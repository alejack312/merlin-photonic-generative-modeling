"""Exact Walsh/correlator audits and registered B0 metric fixtures.

The module is deliberately classical and finite: it never imports Perceval and
does not train a surrogate.  Exact target coefficients are accepted only as a
declared ``oracle`` access mode in the frozen-model audit.
"""

from __future__ import annotations

from itertools import combinations
import math
from typing import Any, Literal, Mapping, Sequence

import numpy as np

from merlin_iqp.classical.kernel import (
    gaussian_hamming_spectrum,
    hamming_walsh_matrix,
    spatial_walsh_matrix,
)
from merlin_iqp.experiments.comparison import expected_coverage, expected_occupancy, true_forward_kl


BitOrder = Literal["msb", "lsb"]
R2_NULL_TOLERANCE = 1.0e-9
B2_RUNG_LABELS = {
    1: "Exact reference and oracle diagnostic",
    2: "Approximation",
    3: "Approximation (control for rung 2: does choosing by order matter?)",
    4: "Approximation",
    5: "Approximation",
}


def _validate_bit_order(bit_order: str) -> BitOrder:
    if bit_order not in {"msb", "lsb"}:
        raise ValueError("bit_order must be 'msb' or 'lsb'")
    return bit_order  # type: ignore[return-value]


def _validate_distribution(distribution: Mapping[str, float]) -> tuple[int, dict[str, float]]:
    if not distribution:
        raise ValueError("distribution must not be empty")
    keys = tuple(distribution)
    n = len(keys[0])
    if n < 1 or any(len(key) != n or set(key) - {"0", "1"} for key in keys):
        raise ValueError("distribution keys must be equal-length binary strings")
    expected = {format(index, f"0{n}b") for index in range(2**n)}
    if set(keys) != expected:
        raise ValueError("distribution must contain every binary outcome exactly once")
    values = {key: float(value) for key, value in distribution.items()}
    if any(not math.isfinite(value) or value < 0.0 for value in values.values()):
        raise ValueError("distribution values must be finite and non-negative")
    if not math.isclose(sum(values.values()), 1.0, rel_tol=0.0, abs_tol=1.0e-12):
        raise ValueError("distribution must be normalized")
    return n, values


def _subset_keys(n: int) -> tuple[tuple[int, ...], ...]:
    return tuple(
        subset
        for order in range(n + 1)
        for subset in combinations(range(n), order)
    )


def _bit_at(bitstring: str, qubit: int, bit_order: BitOrder) -> int:
    position = qubit if bit_order == "msb" else len(bitstring) - 1 - qubit
    return int(bitstring[position])


def _character(bitstring: str, subset: tuple[int, ...], bit_order: BitOrder, character_sign: int = -1) -> int:
    result = 1
    for qubit in subset:
        result *= character_sign ** _bit_at(bitstring, qubit, bit_order)
    return result


def walsh_moments(
    distribution: Mapping[str, float],
    *,
    bit_order: BitOrder = "msb",
) -> dict[tuple[int, ...], float]:
    """Return signed Walsh moments, including the identity moment."""

    order = _validate_bit_order(bit_order)
    n, values = _validate_distribution(distribution)
    return {
        subset: float(sum(probability * _character(bitstring, subset, order) for bitstring, probability in values.items()))
        for subset in _subset_keys(n)
    }


def reconstruct_from_moments(
    moments: Mapping[tuple[int, ...], float],
    *,
    n: int,
    bit_order: BitOrder = "msb",
    normalization: float | None = None,
    character_sign: int = -1,
) -> dict[str, float]:
    """Reconstruct a vector from signed moments without hiding truncation."""

    order = _validate_bit_order(bit_order)
    if int(n) != n or n < 1:
        raise ValueError("n must be a positive integer")
    if character_sign not in {-1, 1}:
        raise ValueError("character_sign must be -1 or 1")
    factor = 2.0 ** (-int(n)) if normalization is None else float(normalization)
    if not math.isfinite(factor):
        raise ValueError("normalization must be finite")
    normalized_moments: dict[tuple[int, ...], float] = {}
    for subset, value in moments.items():
        key = tuple(int(index) for index in subset)
        if len(set(key)) != len(key) or any(index < 0 or index >= n for index in key):
            raise ValueError(f"invalid moment subset {subset!r}")
        number = float(value)
        if not math.isfinite(number):
            raise ValueError("moments must be finite")
        normalized_moments[key] = number
    return {
        format(index, f"0{n}b"): float(
            factor
            * sum(
                value * _character(format(index, f"0{n}b"), subset, order, character_sign)
                for subset, value in normalized_moments.items()
            )
        )
        for index in range(2**n)
    }


def identity_residual_max(
    target: Mapping[str, float],
    rebuilt: Mapping[str, float],
) -> float:
    """Return the largest absolute entrywise reconstruction residual."""

    _, expected = _validate_distribution(target)
    if set(rebuilt) != set(expected):
        raise ValueError("rebuilt distribution must have the target outcome support")
    values = {key: float(value) for key, value in rebuilt.items()}
    if any(not math.isfinite(value) for value in values.values()):
        raise ValueError("rebuilt distribution must be finite")
    return float(max(abs(expected[key] - values[key]) for key in expected))


def uniform_reference_sse(target: Mapping[str, float]) -> float:
    """Return the exact SSE from a target to the uniform distribution."""

    n, values = _validate_distribution(target)
    uniform = 2.0 ** (-n)
    return float(sum((probability - uniform) ** 2 for probability in values.values()))


def validate_r2_nulls(
    target: Mapping[str, float],
    rebuilt: Mapping[str, float],
    *,
    reported_uniform_reference_sse: float | None = None,
    tolerance: float = R2_NULL_TOLERANCE,
) -> dict[str, float]:
    """Fail closed if either owner-final R2 null is violated."""

    report = {
        "identity_residual_max": identity_residual_max(target, rebuilt),
        "uniform_reference_sse": uniform_reference_sse(target),
    }
    if report["identity_residual_max"] > tolerance:
        raise AssertionError(
            f"identity_residual_max={report['identity_residual_max']:.17g} exceeds {tolerance:.17g}"
        )
    if reported_uniform_reference_sse is not None and not math.isclose(
        float(reported_uniform_reference_sse), report["uniform_reference_sse"], rel_tol=0.0, abs_tol=tolerance
    ):
        raise AssertionError(
            "uniform_reference_sse="
            f"{reported_uniform_reference_sse:.17g} does not match {report['uniform_reference_sse']:.17g}"
        )
    return report


def parseval_sse_from_moments(
    target: Mapping[str, float],
    candidate: Mapping[str, float],
) -> tuple[float, float]:
    """Return direct and Walsh-Parseval squared errors."""

    n_target, _ = _validate_distribution(target)
    n_candidate, _ = _validate_distribution(candidate)
    if n_target != n_candidate:
        raise ValueError("target and candidate must have the same n")
    direct = float(sum((target[key] - candidate[key]) ** 2 for key in target))
    target_moments = walsh_moments(target)
    candidate_moments = walsh_moments(candidate)
    spectral = float(
        2.0 ** (-n_target)
        * sum((target_moments[key] - candidate_moments[key]) ** 2 for key in target_moments)
    )
    return direct, spectral


def parity_distribution(n: int, epsilon: float) -> dict[str, float]:
    """Return the known full-parity fixture ``2^-n(1+epsilon chi_[n])``."""

    if int(n) != n or n < 1 or not math.isfinite(float(epsilon)) or abs(float(epsilon)) > 1.0:
        raise ValueError("n must be positive and epsilon must be finite in [-1, 1]")
    return {
        format(index, f"0{n}b"): float(
            2.0 ** (-n) * (1.0 + float(epsilon) * _character(format(index, f"0{n}b"), tuple(range(n)), "msb"))
        )
        for index in range(2**n)
    }


def normalized_hamming_spectral_weights(n: int, sigma: float) -> dict[tuple[int, ...], float]:
    """Return normalized Gaussian-Hamming Walsh weights by subset."""

    weights = gaussian_hamming_spectrum(n, sigma)
    return {subset: float(weights[index]) for index, subset in enumerate(_subset_keys(n))}


def spatial_walsh_quadratic_form(delta: Sequence[float], kernel: np.ndarray) -> float:
    """Evaluate a finite spatial kernel through its full Walsh matrix."""

    vector = np.asarray(delta, dtype=np.float64)
    matrix = np.asarray(kernel, dtype=np.float64)
    if vector.ndim != 1 or matrix.shape != (len(vector), len(vector)):
        raise ValueError("delta and kernel dimensions do not match")
    if len(vector) == 0 or len(vector) & (len(vector) - 1):
        raise ValueError("delta length must be a positive power of two")
    if not np.all(np.isfinite(vector)) or not np.all(np.isfinite(matrix)):
        raise ValueError("delta and kernel must be finite")
    W = hamming_walsh_matrix(int(math.log2(len(vector))))
    transformed = W @ matrix @ W.T / len(vector) ** 2
    moments = W @ vector
    return float(moments @ transformed @ moments)


def negative_reconstruction_mass(vector: Sequence[float]) -> float:
    """Return signed pseudo-probability mass below zero."""

    values = np.asarray(vector, dtype=np.float64)
    if values.ndim != 1 or not len(values) or not np.all(np.isfinite(values)):
        raise ValueError("vector must be a non-empty finite vector")
    return float(np.maximum(-values, 0.0).sum())


def expected_unseen_coverage(
    candidate: Mapping[str, float],
    valid_states: Sequence[str],
    training_states: Sequence[str],
    sample_count: int,
) -> float:
    """Return expected unique coverage over ``U = valid - training``."""

    n, values = _validate_distribution(candidate)
    valid = set(valid_states)
    training = set(training_states)
    if any(len(state) != n or set(state) - {"0", "1"} for state in valid | training):
        raise ValueError("valid and training states must be n-bit strings")
    if isinstance(sample_count, bool) or int(sample_count) != sample_count or sample_count < 0:
        raise ValueError("sample_count must be a non-negative integer")
    unseen = valid - training
    if not unseen or sample_count == 0:
        return 0.0
    return float(
        sum(1.0 - (1.0 - values[state]) ** int(sample_count) for state in unseen) / len(unseen)
    )


def sparse_moment_matching_distribution(
    n: int,
    max_order: int,
    *,
    target: Mapping[str, float] | None = None,
) -> dict[str, Any]:
    """Find a non-negative sparse vector matching moments through ``max_order``.

    This is a small B0 existence fixture, not a training method.  The exact
    target coefficient access is therefore reported as an oracle diagnostic.
    """

    if int(n) != n or n < 1 or int(max_order) != max_order or not 0 <= max_order <= n:
        raise ValueError("n must be positive and max_order must lie in [0, n]")
    reference = parity_distribution(n, 0.0) if target is None else dict(target)
    _, reference = _validate_distribution(reference)
    states = tuple(format(index, f"0{n}b") for index in range(2**n))
    subsets = tuple(key for key in _subset_keys(n) if 1 <= len(key) <= max_order)
    rows = [np.ones(2**n, dtype=float)]
    rhs = [1.0]
    reference_moments = walsh_moments(reference)
    for subset in subsets:
        rows.append(np.array([_character(state, subset, "msb") for state in states], dtype=float))
        rhs.append(reference_moments[subset])
    try:
        from scipy.optimize import linprog
    except ImportError as exc:  # pragma: no cover - environment capability branch
        raise RuntimeError("scipy is required for the B0 sparse moment fixture") from exc
    result = linprog(
        c=np.linspace(0.0, 1.0, 2**n, dtype=float),
        A_eq=np.stack(rows),
        b_eq=np.asarray(rhs),
        bounds=(0.0, None),
        method="highs",
    )
    if not result.success or result.x is None:
        raise RuntimeError(f"sparse moment fixture failed: {result.message}")
    vector = np.asarray(result.x, dtype=float)
    return {
        "distribution": {state: float(value) for state, value in zip(states, vector, strict=True)},
        "matched_subsets": [list(subset) for subset in subsets],
        "support_size": int(np.count_nonzero(vector > 1.0e-12)),
        "oracle_target_coefficients": True,
        "max_constraint_residual": float(np.max(np.abs(np.stack(rows) @ vector - np.asarray(rhs)))),
    }


def frozen_model_correlator_audit(
    target: Mapping[str, float],
    model: Mapping[str, float],
    *,
    retained_subsets: Sequence[tuple[int, ...]] | None = None,
    sigma: float | None = None,
    target_coefficient_access: Literal["oracle", "observed"] = "oracle",
    same_theta_loss_before: float | None = None,
    same_theta_loss_after: float | None = None,
) -> dict[str, Any]:
    """Return B1 order residuals and fixed-theta truncation diagnostics."""

    if target_coefficient_access not in {"oracle", "observed"}:
        raise ValueError("target_coefficient_access must be 'oracle' or 'observed'")
    n_target, _ = _validate_distribution(target)
    n_model, _ = _validate_distribution(model)
    if n_target != n_model:
        raise ValueError("target and model must have the same n")
    target_moments = walsh_moments(target)
    model_moments = walsh_moments(model)
    all_subsets = tuple(key for key in _subset_keys(n_target) if key)
    selected = all_subsets if retained_subsets is None else tuple(tuple(key) for key in retained_subsets)
    if any(key not in target_moments for key in selected):
        raise ValueError("retained_subsets contains an invalid moment")
    residuals = {key: float(target_moments[key] - model_moments[key]) for key in all_subsets}
    by_order: dict[str, float] = {}
    normalized_by_order: dict[str, float] = {}
    for order in range(1, n_target + 1):
        values = [value**2 for key, value in residuals.items() if len(key) == order]
        by_order[str(order)] = float(sum(values))
        normalized_by_order[str(order)] = float(sum(values) / len(values)) if values else 0.0
    weighted_by_order: dict[str, float] | None = None
    if sigma is not None:
        weights = normalized_hamming_spectral_weights(n_target, sigma)
        weighted_by_order = {
            str(order): float(sum(weights[key] * residuals[key] ** 2 for key in all_subsets if len(key) == order))
            for order in range(1, n_target + 1)
        }
    retained = {key: model_moments[key] for key in selected}
    retained[()] = model_moments[()]
    truncated = reconstruct_from_moments(retained, n=n_target)
    selected_set = set(selected)
    omitted_energy = float(
        2.0 ** (-n_target) * sum(model_moments[key] ** 2 for key in all_subsets if key not in selected_set)
    )
    omitted_residual_energy = float(
        2.0 ** (-n_target) * sum(residuals[key] ** 2 for key in all_subsets if key not in selected_set)
    )
    report: dict[str, Any] = {
        "n": n_target,
        "target_coefficient_access": target_coefficient_access,
        "oracle_target_coefficients": target_coefficient_access == "oracle",
        "identity_residual_max": identity_residual_max(model, reconstruct_from_moments(model_moments, n=n_target)),
        "uniform_reference_sse": uniform_reference_sse(target),
        "residual_by_order": by_order,
        "normalized_residual_by_order": normalized_by_order,
        "kernel_weighted_contribution_by_order": weighted_by_order,
        "retained_subsets": [list(key) for key in selected],
        "omitted_energy": omitted_energy,
        "omitted_residual_energy": omitted_residual_energy,
        "negative_reconstruction_mass": negative_reconstruction_mass(tuple(truncated.values())),
        "same_theta_loss_before": same_theta_loss_before,
        "same_theta_loss_after": same_theta_loss_after,
        "same_theta_loss_change": None
        if same_theta_loss_before is None or same_theta_loss_after is None
        else float(same_theta_loss_after - same_theta_loss_before),
    }
    return report


def b0_metric_fixtures() -> dict[str, Any]:
    """Return deterministic B0 reference values for the registered n=3 fixture."""

    target = parity_distribution(3, 1.0)
    uniform = parity_distribution(3, 0.0)
    direct, spectral = parseval_sse_from_moments(target, uniform)
    return {
        "parity_target": target,
        "parity_uniform": uniform,
        "parseval_direct_sse": direct,
        "parseval_walsh_sse": spectral,
        "uniform_reference_sse": uniform_reference_sse(target),
        "identity_residual_max": identity_residual_max(target, reconstruct_from_moments(walsh_moments(target), n=3)),
    }


def _distribution_sse(left: Mapping[str, float], right: Mapping[str, float]) -> float:
    if set(left) != set(right):
        raise ValueError("distributions must have identical support")
    return float(sum((float(left[key]) - float(right[key])) ** 2 for key in left))


def _distribution_tvd(left: Mapping[str, float], right: Mapping[str, float]) -> float:
    if set(left) != set(right):
        raise ValueError("distributions must have identical support")
    return float(0.5 * sum(abs(float(left[key]) - float(right[key])) for key in left))


def _b2_rung_metrics(
    *,
    rung: int,
    label: str,
    target: Mapping[str, float],
    target_moments: Mapping[tuple[int, ...], float],
    frozen_model: Mapping[str, float],
    frozen_model_moments: Mapping[tuple[int, ...], float],
    selected_subsets: Sequence[tuple[int, ...]],
    subset_seed: int,
    reference_only: bool,
    learned_model: Mapping[str, float] | None,
) -> dict[str, Any]:
    selected = tuple(selected_subsets)
    reconstruction_moments = {(): frozen_model_moments[()]}
    reconstruction_moments.update({subset: frozen_model_moments[subset] for subset in selected if subset})
    reconstruction = reconstruct_from_moments(reconstruction_moments, n=len(next(iter(target))))
    nonidentity = tuple(subset for subset in selected if subset)
    omitted = tuple(subset for subset in frozen_model_moments if subset and subset not in nonidentity)
    coefficient_errors = [target_moments[subset] - frozen_model_moments[subset] for subset in nonidentity]
    learned_sse = None
    learned_tvd = None
    if learned_model is not None:
        learned_sse = _distribution_sse(learned_model, frozen_model)
        learned_tvd = _distribution_tvd(learned_model, frozen_model)
    return {
        "rung": rung,
        "label": label,
        "status": "PASS",
        "reference_only": reference_only,
        "oracle_target_coefficients": True,
        "target_coefficient_access": "oracle",
        "subset_seed": subset_seed,
        "selected_subsets": [list(subset) for subset in selected],
        "nonidentity_count": len(nonidentity),
        "frozen_theta_coefficient_sse": float(sum(error**2 for error in coefficient_errors)),
        "frozen_theta_coefficient_max_abs": float(max((abs(error) for error in coefficient_errors), default=0.0)),
        "frozen_theta_omitted_coefficient_energy": float(
            2.0 ** (-len(next(iter(target)))) * sum(frozen_model_moments[subset] ** 2 for subset in omitted)
        ),
        "frozen_theta_reconstruction_sse": _distribution_sse(frozen_model, reconstruction),
        "frozen_theta_negative_reconstruction_mass": negative_reconstruction_mass(tuple(reconstruction.values())),
        "learned_theta_exact_sse": learned_sse,
        "learned_theta_exact_tvd": learned_tvd,
    }


def b2_dependency_checkpoint() -> dict[str, Any]:
    """Report unselected TN/PPS candidates without importing or installing them."""

    return {
        "status": "selection_pending",
        "candidates": [
            {
                "rung": 4,
                "kind": "tensor_network",
                "candidate": "registered tensor-network contraction backend",
                "installed": False,
                "license_review_required": True,
                "required_registration": ["bond_dimension", "truncation_tolerance", "contraction_order", "discarded_weight"],
            },
            {
                "rung": 5,
                "kind": "pauli_propagation",
                "candidate": "registered Pauli-propagation evaluator",
                "installed": False,
                "license_review_required": True,
                "required_registration": ["truncation_or_cutoff", "error_diagnostics", "parameter_convention"],
            },
        ],
    }


def b2_capacity_ladder_audit(
    target: Mapping[str, float],
    frozen_model: Mapping[str, float],
    *,
    max_order: int,
    subset_seed: int,
    learned_model: Mapping[str, float] | None = None,
) -> dict[str, Any]:
    """Audit B2 rungs 1--3 and register dependency-pending rungs 4--5.

    Rung 1 is a small-n exact reference only. Rungs 2 and 3 use the same
    frozen model and paired subset seed, so their difference isolates ordered
    feature selection from choosing the same number of features at random.
    """

    n_target, _ = _validate_distribution(target)
    n_model, _ = _validate_distribution(frozen_model)
    if n_target != n_model:
        raise ValueError("target and frozen_model must have the same n")
    if isinstance(max_order, bool) or int(max_order) != max_order or not 0 <= max_order <= n_target:
        raise ValueError("max_order must be an integer in [0, n]")
    if isinstance(subset_seed, bool) or int(subset_seed) != subset_seed or subset_seed < 0:
        raise ValueError("subset_seed must be a non-negative integer")
    if learned_model is not None:
        n_learned, _ = _validate_distribution(learned_model)
        if n_learned != n_target:
            raise ValueError("learned_model must have the same n")

    target_moments = walsh_moments(target)
    frozen_model_moments = walsh_moments(frozen_model)
    all_nonidentity = tuple(subset for subset in _subset_keys(n_target) if subset)
    order_selected = tuple(subset for subset in all_nonidentity if len(subset) <= max_order)
    rng = np.random.default_rng(int(subset_seed))
    random_indices = rng.choice(len(all_nonidentity), size=len(order_selected), replace=False)
    random_selected = tuple(all_nonidentity[int(index)] for index in sorted(random_indices.tolist()))
    rung_one = _b2_rung_metrics(
        rung=1,
        label=B2_RUNG_LABELS[1],
        target=target,
        target_moments=target_moments,
        frozen_model=frozen_model,
        frozen_model_moments=frozen_model_moments,
        selected_subsets=all_nonidentity,
        subset_seed=int(subset_seed),
        reference_only=True,
        learned_model=learned_model,
    )
    rung_two = _b2_rung_metrics(
        rung=2,
        label=B2_RUNG_LABELS[2],
        target=target,
        target_moments=target_moments,
        frozen_model=frozen_model,
        frozen_model_moments=frozen_model_moments,
        selected_subsets=order_selected,
        subset_seed=int(subset_seed),
        reference_only=False,
        learned_model=learned_model,
    )
    rung_three = _b2_rung_metrics(
        rung=3,
        label=B2_RUNG_LABELS[3],
        target=target,
        target_moments=target_moments,
        frozen_model=frozen_model,
        frozen_model_moments=frozen_model_moments,
        selected_subsets=random_selected,
        subset_seed=int(subset_seed),
        reference_only=False,
        learned_model=learned_model,
    )
    dependency = b2_dependency_checkpoint()
    rung_four = {"rung": 4, "label": B2_RUNG_LABELS[4], "status": "dependency_pending", **dependency["candidates"][0]}
    rung_five = {"rung": 5, "label": B2_RUNG_LABELS[5], "status": "dependency_pending", **dependency["candidates"][1]}
    report = {
        "n": n_target,
        "max_order": int(max_order),
        "subset_seed": int(subset_seed),
        "target_coefficient_access": "oracle",
        "oracle_target_coefficients": True,
        "rungs": [1, 2, 3, 4, 5],
        "rungs_by_number": {"1": rung_one, "2": rung_two, "3": rung_three, "4": rung_four, "5": rung_five},
        "dependency_checkpoint": dependency,
    }
    validate_b2_report(report)
    return report


def validate_b2_report(report: Mapping[str, Any]) -> None:
    """Reject altered rung labels, oracle status, or paired-control metadata."""

    if tuple(report.get("rungs", ())) != (1, 2, 3, 4, 5):
        raise AssertionError("B2 report must contain rungs 1 through 5")
    rungs = report.get("rungs_by_number")
    if not isinstance(rungs, Mapping):
        raise AssertionError("B2 report is missing rungs_by_number")
    for rung in range(1, 6):
        entry = rungs.get(str(rung))
        if not isinstance(entry, Mapping) or entry.get("label") != B2_RUNG_LABELS[rung]:
            raise AssertionError(f"rung {rung} label is invalid")
    if rungs["1"].get("reference_only") is not True or rungs["1"].get("oracle_target_coefficients") is not True:
        raise AssertionError("rung 1 must be an oracle-only reference")
    if rungs["2"].get("subset_seed") != rungs["3"].get("subset_seed"):
        raise AssertionError("rungs 2 and 3 must use the same subset seed")
    if rungs["2"].get("nonidentity_count") != rungs["3"].get("nonidentity_count"):
        raise AssertionError("rungs 2 and 3 must use the same number of nonidentity correlators")
    if rungs["4"].get("status") != "dependency_pending" or rungs["5"].get("status") != "dependency_pending":
        raise AssertionError("TN/PPS rungs must remain dependency-pending until selected")


def b2_paired_comparison(report: Mapping[str, Any]) -> dict[str, Any]:
    """Compare order-selected and paired random-subset reconstruction error."""

    validate_b2_report(report)
    rungs = report["rungs_by_number"]
    order = rungs["2"]
    random = rungs["3"]
    return {
        "paired": True,
        "subset_seed": order["subset_seed"],
        "nonidentity_count": order["nonidentity_count"],
        "order_error": float(order["frozen_theta_reconstruction_sse"]),
        "random_error": float(random["frozen_theta_reconstruction_sse"]),
        "order_beats_random": float(order["frozen_theta_reconstruction_sse"])
        < float(random["frozen_theta_reconstruction_sse"]),
    }


__all__ = [
    "R2_NULL_TOLERANCE",
    "B2_RUNG_LABELS",
    "b2_capacity_ladder_audit",
    "b2_dependency_checkpoint",
    "b2_paired_comparison",
    "b0_metric_fixtures",
    "expected_coverage",
    "expected_occupancy",
    "expected_unseen_coverage",
    "frozen_model_correlator_audit",
    "identity_residual_max",
    "negative_reconstruction_mass",
    "normalized_hamming_spectral_weights",
    "parity_distribution",
    "parseval_sse_from_moments",
    "reconstruct_from_moments",
    "spatial_walsh_quadratic_form",
    "sparse_moment_matching_distribution",
    "true_forward_kl",
    "validate_b2_report",
    "uniform_reference_sse",
    "validate_r2_nulls",
    "walsh_moments",
]
