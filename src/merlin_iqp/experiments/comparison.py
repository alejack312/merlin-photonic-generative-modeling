"""Matched backend comparison and plan-defined metrics for v4.

This module deliberately accepts already-materialized distributions.  It does
not decide whether a vector came from a raw, compiled, or deployed backend;
the caller must label that provenance and provide a separate acceptance mass.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

import numpy as np

from merlin_iqp.classical.objectives import hamming_mmd2, spatial_mmd2


def _probability_vector(value: np.ndarray, *, name: str) -> np.ndarray:
    vector = np.asarray(value, dtype=np.float64)
    if vector.ndim != 1 or not len(vector) or len(vector) & (len(vector) - 1):
        raise ValueError(f"{name} must be a non-empty vector of length 2**n")
    if not np.all(np.isfinite(vector)) or np.any(vector < 0) or not np.isclose(vector.sum(), 1.0, atol=1e-10, rtol=1e-10):
        raise ValueError(f"{name} must be finite, non-negative, and normalized")
    return vector / vector.sum()


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


def floored_log_ratio(target: np.ndarray, candidate: np.ndarray, floor: float) -> tuple[float, float]:
    if not np.isfinite(floor) or floor <= 0:
        raise ValueError("floor must be positive and finite")
    p = _probability_vector(target, name="target")
    q = _probability_vector(candidate, name="candidate")
    floored = np.maximum(q, floor)
    added_mass = float(np.sum(floored - q))
    return float(np.sum(p * np.log(np.maximum(p, floor) / floored))), added_mass


def expected_coverage(target: np.ndarray, candidate: np.ndarray, sample_count: int) -> dict[str, float | int]:
    if sample_count < 0:
        raise ValueError("sample_count must be non-negative")
    p = _probability_vector(target, name="target")
    q = _probability_vector(candidate, name="candidate")
    support = p > 1e-6
    support_q = q[support]
    terms = np.ones_like(support_q)
    below_one = support_q < 1.0
    terms[below_one] = -np.expm1(sample_count * np.log1p(-support_q[below_one]))
    return {
        "expected_coverage": float(np.mean(terms)) if len(terms) else 0.0,
        "support_size": int(np.count_nonzero(support)),
        "excluded_target_mass": float(p[~support].sum()),
        "sample_count": int(sample_count),
    }


@dataclass(frozen=True)
class DistributionArm:
    """One normalized output vector with explicit provenance and acceptance."""

    backend_id: str
    vector: np.ndarray
    stage: str
    acceptance_mass: float = 1.0
    samples: int | None = None
    provenance: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        vector = _probability_vector(self.vector, name="vector")
        if self.stage not in {"raw", "compiled", "deployed"}:
            raise ValueError("stage must be raw, compiled, or deployed")
        if not np.isfinite(self.acceptance_mass) or not 0 < self.acceptance_mass <= 1:
            raise ValueError("acceptance_mass must be in (0, 1]")
        if self.samples is not None and self.samples < 0:
            raise ValueError("samples must be non-negative")
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

    def __post_init__(self) -> None:
        target = _probability_vector(self.target, name="target")
        if not np.isfinite(self.hamming_sigma) or self.hamming_sigma <= 0:
            raise ValueError("hamming_sigma must be positive and finite")
        if len(self.arms) < 1 or any(len(arm.vector) != len(target) for arm in self.arms):
            raise ValueError("comparison arms must be non-empty and match target size")
        if self.spatial_centers is not None:
            centers = np.asarray(self.spatial_centers, dtype=np.float64)
            if centers.shape != (len(target), 2) or not np.all(np.isfinite(centers)):
                raise ValueError("spatial_centers must have shape (2**n, 2)")
            if self.spatial_sigma is None or not np.isfinite(self.spatial_sigma) or self.spatial_sigma <= 0:
                raise ValueError("spatial_sigma is required and positive with spatial_centers")
            object.__setattr__(self, "spatial_centers", centers.copy())
        object.__setattr__(self, "target", target)

    @property
    def n(self) -> int:
        return int(np.log2(len(self.target)))

    def metrics(self) -> dict[str, dict[str, Any]]:
        rows: dict[str, dict[str, Any]] = {}
        for arm in self.arms:
            floor_12, added_12 = floored_log_ratio(self.target, arm.vector, 1e-12)
            floor_9, added_9 = floored_log_ratio(self.target, arm.vector, 1e-9)
            row: dict[str, Any] = {
                "backend_id": arm.backend_id,
                "stage": arm.stage,
                "tvd_to_target": total_variation_distance(self.target, arm.vector),
                "true_forward_kl": true_forward_kl(self.target, arm.vector),
                "floored_log_ratio_1e-12": floor_12,
                "floored_log_ratio_1e-12_added_mass": added_12,
                "floored_log_ratio_1e-9": floor_9,
                "floored_log_ratio_1e-9_added_mass": added_9,
                "support_validity": 1.0,
                "acceptance_mass": arm.acceptance_mass,
                "attempts_per_accepted_sample": 1.0 / arm.acceptance_mass,
                "provenance": dict(arm.provenance),
            }
            row.update(expected_coverage(self.target, arm.vector, arm.samples or 0))
            row["hamming_mmd2"] = hamming_mmd2(arm.vector, self.target, sigma=self.hamming_sigma)
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
            "arms": [{"backend_id": arm.backend_id, "stage": arm.stage, "acceptance_mass": arm.acceptance_mass, "samples": arm.samples, "provenance": arm.provenance} for arm in self.arms],
            "metrics": self.metrics(),
        }


def _hash_vector(value: np.ndarray) -> str:
    import hashlib

    array = np.ascontiguousarray(np.asarray(value))
    return hashlib.sha256(array.tobytes()).hexdigest()


__all__ = ["DistributionArm", "MatchedComparison", "expected_coverage", "floored_log_ratio", "total_variation_distance", "true_forward_kl"]
