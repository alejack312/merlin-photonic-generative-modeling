"""Matched backend comparison and plan-defined metrics for v4.

This module deliberately accepts already-materialized distributions.  It does
not decide whether a vector came from a raw, compiled, or deployed backend;
the caller must label that provenance and provide a separate acceptance mass.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from itertools import combinations
import os
from typing import Any, Mapping

import numpy as np

from merlin_iqp.classical.kernel import gaussian_hamming_matrix
from merlin_iqp.classical.objectives import hamming_mmd2, hamming_mmd2_walsh, spatial_mmd2


def _probability_vector(value: np.ndarray, *, name: str) -> np.ndarray:
    vector = np.asarray(value, dtype=np.float64)
    if vector.ndim != 1 or not len(vector) or len(vector) & (len(vector) - 1):
        raise ValueError(f"{name} must be a non-empty vector of length 2**n")
    if not np.all(np.isfinite(vector)) or np.any(vector < 0) or not np.isclose(vector.sum(), 1.0, atol=1e-10, rtol=1e-10):
        raise ValueError(f"{name} must be finite, non-negative, and normalized")
    total = float(vector.sum())
    if np.isclose(total, 1.0, atol=1e-12, rtol=1e-12):
        return vector.copy()
    return vector / total


def total_variation_distance(left: np.ndarray, right: np.ndarray) -> float:
    return float(0.5 * np.abs(_probability_vector(left, name="left") - _probability_vector(right, name="right")).sum())


def true_forward_kl(target: np.ndarray, candidate: np.ndarray) -> float:
    """Return true KL, including ``inf`` when target mass meets zero candidate."""
    p = _probability_vector(target, name="target")
    q = _probability_vector(candidate, name="candidate")
    positive = p > 0
    if np.any(q[positive] == 0):
        return float("inf")
    return float(np.sum(p[positive] * np.log(p[positive] / q[positive])))


def hamming_mmd2_direct(
    target: np.ndarray,
    candidate: np.ndarray,
    *,
    sigma: float,
    sigmas: list[float] | None = None,
    weights: list[float] | None = None,
) -> float:
    """Evaluate normalized Hamming-Gaussian MMD² from its direct kernel matrix."""

    p = _probability_vector(target, name="target")
    q = _probability_vector(candidate, name="candidate")
    if len(p) != len(q):
        raise ValueError("target and candidate must have equal lengths")
    n = int(np.log2(len(p)))
    delta = p - q
    kernel = gaussian_hamming_matrix(n, sigma, sigmas=sigmas, weights=weights)
    return float(delta @ kernel @ delta)


def hamming_mmd2_crosscheck(target: np.ndarray, candidate: np.ndarray, *, sigma: float) -> dict[str, Any]:
    """Return direct, Walsh and trainer-objective MMD² values and their errors."""

    direct = hamming_mmd2_direct(target, candidate, sigma=sigma)
    walsh = hamming_mmd2_walsh(candidate, target, sigma=sigma)
    trainer = hamming_mmd2(candidate, target, sigma=sigma)
    error = max(abs(direct - walsh), abs(direct - trainer))
    return {
        "direct": direct,
        "walsh": walsh,
        "trainer_objective": trainer,
        "max_abs_error": float(error),
        "status": "PASS" if error <= 1e-12 else "FAIL",
    }


def floored_log_ratio(target: np.ndarray, candidate: np.ndarray, floor: float) -> tuple[float, float]:
    if not np.isfinite(floor) or floor <= 0:
        raise ValueError("floor must be positive and finite")
    p = _probability_vector(target, name="target")
    q = _probability_vector(candidate, name="candidate")
    floored = np.maximum(q, floor)
    added_mass = float(np.sum(floored - q))
    return float(np.sum(p * np.log(np.maximum(p, floor) / floored))), added_mass


def expected_coverage(target: np.ndarray, candidate: np.ndarray, sample_count: int) -> dict[str, float | int]:
    if isinstance(sample_count, (bool, np.bool_)) or not isinstance(sample_count, (int, np.integer)):
        raise ValueError("sample_count must be an integer")
    sample_count = int(sample_count)
    if sample_count < 0:
        raise ValueError("sample_count must be non-negative")
    p = _probability_vector(target, name="target")
    q = _probability_vector(candidate, name="candidate")
    support = p > 1e-6
    support_q = q[support]
    if sample_count == 0:
        coverage = 0.0
    else:
        terms = np.ones_like(support_q)
        below_one = support_q < 1.0
        terms[below_one] = -np.expm1(sample_count * np.log1p(-support_q[below_one]))
        coverage = float(np.mean(terms)) if len(terms) else 0.0
    return {
        "expected_coverage": coverage,
        "support_size": int(np.count_nonzero(support)),
        "excluded_target_mass": float(p[~support].sum()),
        "sample_count": int(sample_count),
    }


def expected_occupancy(candidate: np.ndarray, sample_count: int) -> dict[str, float | int]:
    """Return population expected occupied states for an accepted-shot budget."""

    if isinstance(sample_count, (bool, np.bool_)) or not isinstance(sample_count, (int, np.integer)):
        raise ValueError("sample_count must be an integer")
    sample_count = int(sample_count)
    if sample_count < 0:
        raise ValueError("sample_count must be non-negative")
    q = _probability_vector(candidate, name="candidate")
    if sample_count == 0:
        occupied = 0.0
    else:
        terms = np.ones_like(q)
        below_one = q < 1.0
        terms[below_one] = -np.expm1(sample_count * np.log1p(-q[below_one]))
        occupied = float(terms.sum())
    return {
        "expected_occupancy": occupied,
        "occupancy_fraction": occupied / len(q) if len(q) else 0.0,
        "state_space_size": int(len(q)),
        "sample_count": sample_count,
    }


def _marginal(vector: np.ndarray, subset: tuple[int, ...]) -> np.ndarray:
    q = _probability_vector(vector, name="vector")
    n = int(np.log2(len(q)))
    if any(index < 0 or index >= n for index in subset) or len(set(subset)) != len(subset):
        raise ValueError("marginal subset contains an invalid qubit")
    result = np.zeros(2 ** len(subset), dtype=np.float64)
    for state, probability in enumerate(q):
        local = 0
        for position, qubit in enumerate(subset):
            local |= ((state >> (n - 1 - qubit)) & 1) << (len(subset) - 1 - position)
        result[local] += probability
    return result


def marginal_tvd_panel(target: np.ndarray, candidate: np.ndarray) -> dict[str, Any]:
    """Compare all labeled order-1 and order-2 MSB-first marginals."""

    p = _probability_vector(target, name="target")
    q = _probability_vector(candidate, name="candidate")
    if len(p) != len(q):
        raise ValueError("target and candidate must have equal lengths")
    n = int(np.log2(len(p)))
    result: dict[str, Any] = {}
    for order in (1, 2):
        subsets = list(combinations(range(n), order))
        if not subsets:
            result[f"marginal_tvd_order{order}_mean"] = None
            result[f"marginal_tvd_order{order}_max"] = None
            result[f"marginal_tvd_order{order}_count"] = 0
            continue
        values = [total_variation_distance(_marginal(p, subset), _marginal(q, subset)) for subset in subsets]
        result[f"marginal_tvd_order{order}_mean"] = float(np.mean(values))
        result[f"marginal_tvd_order{order}_max"] = float(np.max(values))
        result[f"marginal_tvd_order{order}_count"] = len(values)
    result["marginal_bit_order"] = "msb_first"
    return result


def mass_preserving_transfer(vector: np.ndarray, source: int, destination: int, amount: float) -> np.ndarray:
    """Transfer probability mass between states without renormalizing or creating mass."""

    q = _probability_vector(vector, name="vector")
    if source == destination or not 0 <= source < len(q) or not 0 <= destination < len(q):
        raise ValueError("source and destination must be distinct valid states")
    if not np.isfinite(amount) or amount <= 0 or amount > q[source]:
        raise ValueError("amount must be positive and no greater than source mass")
    mutated = q.copy()
    mutated[source] -= amount
    mutated[destination] += amount
    return mutated


def metric_specific_mutation(vector: np.ndarray, metric: str, *, amount: float = 0.01) -> dict[str, Any]:
    """Create a declared, mass-preserving mutation targeted at one metric panel."""

    q = _probability_vector(vector, name="vector")
    n = int(np.log2(len(q)))
    source = int(np.argmax(q))
    candidates = list(range(len(q)))
    if metric in {"tvd", "occupancy", "hamming_mmd2"}:
        destination = max(candidates, key=lambda index: (bin(index ^ source).count("1"), -index))
    elif metric == "marginal_tvd_order1":
        destination = next((index for index in candidates if index != source and ((index ^ source) >> (n - 1)) & 1), None)
    elif metric == "marginal_tvd_order2":
        if n < 2:
            raise ValueError("order-2 marginal mutation requires n >= 2")
        destination = next((index for index in candidates if index != source and (index ^ source) & 0b11), None)
    else:
        raise ValueError(f"unsupported mutation metric {metric!r}")
    if destination is None:
        raise ValueError(f"could not construct mutation for {metric}")
    transfer = min(float(amount), float(q[source]) / 2.0)
    if transfer <= 0:
        raise ValueError("source state has no positive mass for mutation")
    return {
        "kind": "mass_preserving_transfer",
        "metric": metric,
        "source": source,
        "destination": int(destination),
        "amount": transfer,
        "mass_before": float(q.sum()),
        "mass_after": float(mass_preserving_transfer(q, source, int(destination), transfer).sum()),
        "vector": mass_preserving_transfer(q, source, int(destination), transfer),
    }


def mutation_control_report(comparison: "MatchedComparison") -> dict[str, Any]:
    """Exercise metric, map, and success mutations as independent controls."""

    baseline_rows = comparison.metrics()
    distribution_controls: dict[str, Any] = {}
    for arm in comparison.arms:
        key = f"{arm.stage}:{arm.backend_id}"
        arm_controls: dict[str, Any] = {}
        for metric, row_key in (
            ("tvd", "tvd_to_target"),
            ("hamming_mmd2", "hamming_mmd2"),
            ("marginal_tvd_order1", "marginal_tvd_order1_mean"),
            ("marginal_tvd_order2", "marginal_tvd_order2_mean"),
            ("occupancy", "expected_occupancy"),
        ):
            try:
                mutation = metric_specific_mutation(arm.vector, metric)
            except ValueError as error:
                arm_controls[metric] = {"status": "not_applicable", "reason": str(error)}
                continue
            mutated_arm = DistributionArm(
                arm.backend_id,
                mutation["vector"],
                arm.stage,
                acceptance_mass=arm.acceptance_mass,
                samples=arm.samples,
                provenance={"mutation": mutation["kind"]},
            )
            mutated_comparison = MatchedComparison(
                "mutation",
                comparison.target,
                (mutated_arm,),
                comparison.hamming_sigma,
                spatial_centers=comparison.spatial_centers,
                spatial_sigma=comparison.spatial_sigma,
            )
            mutated_row = mutated_comparison.metrics()[key]
            before = baseline_rows[key][row_key]
            after = mutated_row[row_key]
            mutated = not np.array_equal(arm.vector, mutated_arm.vector)
            mass_preserved = bool(
                np.isclose(float(mutation["mass_after"]), float(mutation["mass_before"]), rtol=0.0, atol=1e-12)
            )
            if before is None or after is None:
                mutation_status = "not_applicable" if before is None and after is None else "FAIL"
            else:
                # The control certifies that the declared mutation reached
                # the recomputed metric.  A saturated metric (notably finite-
                # sample occupancy) may legitimately remain unchanged; that
                # sensitivity is reported separately rather than converted
                # into a false PASS.
                mutation_status = "PASS" if mutated and mass_preserved else "FAIL"
            arm_controls[metric] = {
                "status": mutation_status,
                "metric_before": before,
                "metric_after": after,
                "metric_changed": (
                    None if before is None or after is None else abs(float(after) - float(before)) > 1e-12
                ),
                "mutation_applied": mutated,
                "mass_preserved": mass_preserved,
                "mass_before": mutation["mass_before"],
                "mass_after": mutation["mass_after"],
                "acceptance_mass_before": arm.acceptance_mass,
                "acceptance_mass_after": mutated_arm.acceptance_mass,
                "source": mutation["source"],
                "destination": mutation["destination"],
            }
        distribution_controls[key] = arm_controls
    def recompute(arm: DistributionArm, *, vector: np.ndarray, acceptance_mass: float, mutation_scope: str) -> dict[str, Any]:
        mutated_arm = DistributionArm(
            arm.backend_id,
            vector,
            arm.stage,
            acceptance_mass=acceptance_mass,
            samples=arm.samples,
            provenance={**arm.provenance, "mutation_scope": mutation_scope},
            source_ac=arm.source_ac,
            uncertainty=arm.uncertainty,
        )
        mutated_comparison = MatchedComparison(
            "mutation",
            comparison.target,
            (mutated_arm,),
            comparison.hamming_sigma,
            spatial_centers=comparison.spatial_centers,
            spatial_sigma=comparison.spatial_sigma,
        )
        key = f"{mutated_arm.stage}:{mutated_arm.backend_id}"
        return {"arm": mutated_arm, "row": mutated_comparison.metrics()[key]}

    def metric_payload(row: Mapping[str, Any]) -> dict[str, Any]:
        excluded = {
            "backend_id",
            "stage",
            "acceptance_mass",
            "attempts_per_accepted_sample",
            "provenance",
            "uncertainty",
        }
        return {key: value for key, value in row.items() if key not in excluded}

    def payload_equal(left: Mapping[str, Any], right: Mapping[str, Any]) -> bool:
        left_payload = metric_payload(left)
        right_payload = metric_payload(right)
        if left_payload.keys() != right_payload.keys():
            return False
        for key in left_payload:
            left_value = left_payload[key]
            right_value = right_payload[key]
            if isinstance(left_value, (int, float)) and isinstance(right_value, (int, float)):
                if not np.isclose(left_value, right_value, rtol=0.0, atol=1e-12):
                    return False
            elif left_value != right_value:
                return False
        return True

    success_controls: dict[str, Any] = {}
    map_controls: dict[str, Any] = {}
    for arm in comparison.arms:
        key = f"{arm.stage}:{arm.backend_id}"
        baseline = baseline_rows[key]

        # Change only the physical success scalar and re-run the metrics.
        success_after = arm.acceptance_mass * 0.99
        success_result = recompute(
            arm,
            vector=arm.vector,
            acceptance_mass=success_after,
            mutation_scope="acceptance_only_success_scalar",
        )
        success_row = success_result["row"]
        conditional_hash_equal = _hash_vector(arm.vector) == _hash_vector(success_result["arm"].vector)
        metrics_unchanged = payload_equal(baseline, success_row)
        success_changed = not np.isclose(arm.acceptance_mass, success_after, rtol=0.0, atol=1e-15)
        success_controls[key] = {
            "kind": "acceptance_only_mutation",
            "physical_map_vs_distribution": "physical acceptance mass changed; conditional distribution was held fixed",
            "acceptance_mass_before": arm.acceptance_mass,
            "acceptance_mass_after": success_row["acceptance_mass"],
            "conditional_vector_hash_before": _hash_vector(arm.vector),
            "conditional_vector_hash_after": _hash_vector(success_result["arm"].vector),
            "conditional_vector_hash_equal": conditional_hash_equal,
            "distribution_metrics_unchanged": metrics_unchanged,
            "status": "PASS" if success_changed and conditional_hash_equal and metrics_unchanged else "FAIL",
        }

        # Mutate the unnormalized accepted map, then derive its trace and
        # conditional vector separately.
        mutation = metric_specific_mutation(arm.vector, "tvd")
        unnormalized = arm.vector * arm.acceptance_mass
        transfer = float(mutation["amount"]) * arm.acceptance_mass
        mutated_unnormalized = unnormalized.copy()
        mutated_unnormalized[int(mutation["source"])] -= transfer
        mutated_unnormalized[int(mutation["destination"])] += transfer
        observed_map_mass = float(mutated_unnormalized.sum())
        if not np.isfinite(observed_map_mass) or observed_map_mass <= 0.0:
            raise ValueError(
                f"map mutation produced non-positive accepted mass for {key}: "
                f"before={arm.acceptance_mass!r}, observed={observed_map_mass!r}"
            )
        if not np.isclose(observed_map_mass, arm.acceptance_mass, rtol=0.0, atol=1e-12):
            raise ValueError(
                f"map mutation changed accepted mass for {key}: "
                f"before={arm.acceptance_mass!r}, observed={observed_map_mass!r}"
            )
        # Use the validated baseline scalar rather than a rounded sum that
        # can become 1.0000000000000002 for a normalized raw arm.
        map_success_after = float(arm.acceptance_mass)
        map_vector_after = mutated_unnormalized / map_success_after
        map_result = recompute(
            arm,
            vector=map_vector_after,
            acceptance_mass=map_success_after,
            mutation_scope="unnormalized_map_mass_transfer",
        )
        map_row = map_result["row"]
        conditional_changed = _hash_vector(arm.vector) != _hash_vector(map_result["arm"].vector)
        success_independent = np.isclose(arm.acceptance_mass, map_row["acceptance_mass"], rtol=0.0, atol=1e-12)
        metrics_changed = not payload_equal(baseline, map_row)
        map_controls[key] = {
            "kind": "unnormalized_map_mass_transfer",
            "physical_map_vs_distribution": "unnormalized accepted-map mass was transferred; conditional distribution was recomputed",
            "map_mass_before": float(unnormalized.sum()),
            "map_mass_after": observed_map_mass,
            "success_before": arm.acceptance_mass,
            "success_after": map_row["acceptance_mass"],
            "conditional_vector_hash_before": _hash_vector(arm.vector),
            "conditional_vector_hash_after": _hash_vector(map_result["arm"].vector),
            "conditional_vector_changed": conditional_changed,
            "distribution_metrics_changed": metrics_changed,
            "success_independent_of_distribution_mutation": bool(success_independent),
            "source": int(mutation["source"]),
            "destination": int(mutation["destination"]),
            "amount": transfer,
            "status": "PASS" if conditional_changed and metrics_changed and success_independent else "FAIL",
        }
    return {
        "distribution_mutations": distribution_controls,
        "map_mutation": map_controls,
        "success_mutation": success_controls,
    }


def process_rss_bytes() -> int | None:
    """Return current-process RSS where the host exposes a safe standard API."""

    try:
        if os.name == "nt":
            import ctypes
            from ctypes import wintypes

            class Counters(ctypes.Structure):
                # PROCESS_MEMORY_COUNTERS_EX is a fixed-width Win32 header
                # followed by SIZE_T fields.  Using the complete layout is
                # required: a truncated structure can make the API reject the
                # query or read the wrong offsets on 64-bit Windows.
                _fields_ = [
                    ("cb", ctypes.c_uint32),
                    ("page_fault_count", ctypes.c_uint32),
                    ("peak_ws", ctypes.c_size_t),
                    ("ws", ctypes.c_size_t),
                    ("quota_peak_paged_pool_usage", ctypes.c_size_t),
                    ("quota_paged_pool_usage", ctypes.c_size_t),
                    ("quota_peak_non_paged_pool_usage", ctypes.c_size_t),
                    ("quota_non_paged_pool_usage", ctypes.c_size_t),
                    ("pagefile_usage", ctypes.c_size_t),
                    ("peak_pagefile_usage", ctypes.c_size_t),
                    ("private_usage", ctypes.c_size_t),
                ]

            counters = Counters()
            counters.cb = ctypes.sizeof(Counters)
            handle = ctypes.windll.kernel32.GetCurrentProcess()
            if ctypes.windll.psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), counters.cb):
                return int(counters.ws)
            return None
        import resource

        value = int(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
        return value * (1024 if sys_platform_is_linux() else 1)
    except (AttributeError, ImportError, OSError):
        return None


def sys_platform_is_linux() -> bool:
    return os.name == "posix" and os.uname().sysname.lower() == "linux"


@dataclass(frozen=True)
class DistributionArm:
    """One normalized output vector with explicit provenance and acceptance."""

    backend_id: str
    vector: np.ndarray
    stage: str
    acceptance_mass: float = 1.0
    samples: int | None = None
    provenance: dict[str, Any] = field(default_factory=dict)
    source_ac: float | None = None
    uncertainty: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        vector = _probability_vector(self.vector, name="vector")
        if self.stage not in {"raw", "compiled", "deployed"}:
            raise ValueError("stage must be raw, compiled, or deployed")
        if not np.isfinite(self.acceptance_mass) or not 0 < self.acceptance_mass <= 1:
            raise ValueError("acceptance_mass must be in (0, 1]")
        reciprocal_limit = 1.0 / np.finfo(np.float64).max
        if self.acceptance_mass <= reciprocal_limit:
            raise ValueError("acceptance_mass is too small for JSON-safe throughput")
        if self.samples is not None and self.samples < 0:
            raise ValueError("samples must be non-negative")
        if self.source_ac is not None and (not np.isfinite(self.source_ac) or self.source_ac < 0):
            raise ValueError("source_ac must be finite and non-negative when supplied")
        object.__setattr__(self, "vector", vector)


@dataclass(frozen=True)
class MatchedComparison:
    cell_id: str
    target: np.ndarray
    arms: tuple[DistributionArm, ...]
    hamming_sigma: float
    spatial_centers: np.ndarray | None = None
    spatial_sigma: float | None = None
    common_manifest: Mapping[str, Any] = field(default_factory=dict)
    controls: Mapping[str, Any] = field(default_factory=dict)
    resource_report: Mapping[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        target = _probability_vector(self.target, name="target")
        hamming_sigma = np.asarray(self.hamming_sigma, dtype=np.float64)
        if hamming_sigma.ndim != 0 or not np.isfinite(hamming_sigma).item() or hamming_sigma.item() <= 0:
            raise ValueError("hamming_sigma must be positive and finite")
        object.__setattr__(self, "hamming_sigma", float(hamming_sigma))
        if len(self.arms) < 1 or any(len(arm.vector) != len(target) for arm in self.arms):
            raise ValueError("comparison arms must be non-empty and match target size")
        if self.spatial_centers is not None:
            centers = np.asarray(self.spatial_centers, dtype=np.float64)
            if centers.shape != (len(target), 2) or not np.all(np.isfinite(centers)):
                raise ValueError("spatial_centers must have shape (2**n, 2)")
            sigma = np.asarray(self.spatial_sigma, dtype=np.float64)
            if sigma.ndim != 0 or not np.isfinite(sigma).item() or sigma.item() <= 0:
                raise ValueError("spatial_sigma is required and positive with spatial_centers")
            object.__setattr__(self, "spatial_centers", centers.copy())
            object.__setattr__(self, "spatial_sigma", float(sigma))
        elif self.spatial_sigma is not None:
            raise ValueError("spatial_sigma requires spatial_centers")
        object.__setattr__(self, "target", target)

    @property
    def n(self) -> int:
        return int(np.log2(len(self.target)))

    def metrics(self) -> dict[str, dict[str, Any]]:
        rows: dict[str, dict[str, Any]] = {}
        for arm in self.arms:
            floor_12, added_12 = floored_log_ratio(self.target, arm.vector, 1e-12)
            floor_9, added_9 = floored_log_ratio(self.target, arm.vector, 1e-9)
            kl = true_forward_kl(self.target, arm.vector)
            kl_infinite = bool(np.isinf(kl))
            target_support = self.target > 1e-6
            row: dict[str, Any] = {
                "backend_id": arm.backend_id,
                "stage": arm.stage,
                "tvd_to_target": total_variation_distance(self.target, arm.vector),
                # JSON has no representation for infinity. Keep the numeric
                # field JSON-safe while carrying the exact extended-real
                # result in an explicit status/value pair.
                "true_forward_kl": None if kl_infinite else kl,
                "true_forward_kl_status": "infinite" if kl_infinite else "finite",
                "true_forward_kl_value": "inf" if kl_infinite else kl,
                "floored_log_ratio_1e-12": floor_12,
                "floored_log_ratio_1e-12_added_mass": added_12,
                "floored_log_ratio_1e-9": floor_9,
                "floored_log_ratio_1e-9_added_mass": added_9,
                "support_validity": float(arm.vector[target_support].sum()),
                "support_threshold": 1e-6,
                "support_definition": "underlying target support where p > 1e-6",
                "support_validity_basis": "underlying conditional probability vector",
                "observed_empirical_support": {
                    "status": "not_available",
                    "reason": "comparison arm supplies a probability vector, not observed outcome samples",
                },
                "target_support_size": int(np.count_nonzero(target_support)),
                "target_support_mass": float(self.target[target_support].sum()),
                "acceptance_mass": arm.acceptance_mass,
                "attempts_per_accepted_sample": 1.0 / arm.acceptance_mass,
                "provenance": dict(arm.provenance),
                "uncertainty": dict(arm.uncertainty) if arm.uncertainty else {"status": "not_applicable", "reason": "exact population vector"},
            }
            row.update(expected_coverage(self.target, arm.vector, arm.samples or 0))
            row.update(expected_occupancy(arm.vector, arm.samples or 0))
            crosscheck = hamming_mmd2_crosscheck(self.target, arm.vector, sigma=self.hamming_sigma)
            row["hamming_mmd2"] = crosscheck["trainer_objective"]
            row["hamming_mmd2_direct"] = crosscheck["direct"]
            row["hamming_mmd2_walsh"] = crosscheck["walsh"]
            row["hamming_mmd2_crosscheck_abs_error"] = crosscheck["max_abs_error"]
            row["hamming_mmd2_crosscheck_status"] = crosscheck["status"]
            row.update(marginal_tvd_panel(self.target, arm.vector))
            if arm.source_ac is not None:
                row["source_anticoncentration"] = arm.source_ac
                row["source_anticoncentration_status"] = "valid_declared_input"
            else:
                row["source_anticoncentration_status"] = "not_computed_missing_declared_input"
            if self.spatial_centers is not None and self.spatial_sigma is not None:
                row["spatial_mmd2"] = spatial_mmd2(arm.vector, self.target, self.spatial_centers, sigma=self.spatial_sigma)
            rows[f"{arm.stage}:{arm.backend_id}"] = row
        return rows

    def manifest(self) -> dict[str, Any]:
        return {
            "schema_version": "v4_tcdp.matched_comparison.v1",
            "cell_id": self.cell_id,
            "n": self.n,
            "target_hash": _hash_vector(self.target),
            "hamming_kernel": {"kind": "gaussian_on_hamming", "sigma": self.hamming_sigma, "distance": "Hamming", "normalization": "MMD2"},
            "spatial_kernel": None if self.spatial_centers is None else {"kind": "Gaussian_on_xy", "sigma": self.spatial_sigma, "centers_hash": _hash_vector(self.spatial_centers)},
            "common_manifest": dict(self.common_manifest),
            "arms": [{"backend_id": arm.backend_id, "stage": arm.stage, "acceptance_mass": arm.acceptance_mass, "samples": arm.samples, "source_ac": arm.source_ac, "provenance": arm.provenance, "uncertainty": arm.uncertainty} for arm in self.arms],
            "controls": dict(self.controls) if self.controls else mutation_control_report(self),
            "resource_report": dict(self.resource_report),
            "metrics": self.metrics(),
        }


def _hash_vector(value: np.ndarray) -> str:
    import hashlib

    array = np.ascontiguousarray(np.asarray(value))
    return hashlib.sha256(array.tobytes()).hexdigest()


__all__ = ["DistributionArm", "MatchedComparison", "expected_coverage", "expected_occupancy", "floored_log_ratio", "hamming_mmd2_crosscheck", "hamming_mmd2_direct", "mass_preserving_transfer", "marginal_tvd_panel", "metric_specific_mutation", "mutation_control_report", "process_rss_bytes", "total_variation_distance", "true_forward_kl"]
