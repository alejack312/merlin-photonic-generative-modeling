"""Registered cell-level holdout contract for the R3 rings benchmark.

The historical rings pipeline keeps its point-level split for continuity.
R3 generalization instead pools all 400 points, assigns them with the
existing :class:`GridCodec`, and holds out whole data-hit cells. This module
contains only that split, its manifest, and the owner-selected coverage /
precision computation; it does not train a model or use model outputs to define
validity.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any, Sequence

import numpy as np

from merlin_iqp.classical._validation import hash_array, hash_json

from .datasets import RingsDataset


SCHEMA_VERSION = "v4_tcdp.ring_cell_holdout.v1"
R3_CELL_HOLDOUT_SEED = 20260928
R3_CELL_HOLDOUT_FRACTION = 0.20
R3_MIN_HELD_OUT_CELLS = 3
R3_GAP_DENOMINATOR_TOLERANCE = 1e-12
R3_NULL_TOLERANCE = 1e-9


def _pooled_raw_points(dataset: RingsDataset) -> np.ndarray:
    point_ids = np.concatenate([dataset.train_ids, dataset.test_ids]).astype(np.int64, copy=False)
    raw_points = np.concatenate([dataset.raw_train, dataset.raw_test], axis=0)
    order = np.argsort(point_ids, kind="stable")
    ordered_ids = point_ids[order]
    expected_ids = np.arange(len(point_ids), dtype=np.int64)
    if not np.array_equal(ordered_ids, expected_ids):
        raise ValueError("rings point IDs must partition the pooled raw dataset")
    return np.asarray(raw_points[order], dtype=np.float64)


def _classify_ring_points(raw_points: np.ndarray) -> np.ndarray:
    radii = np.linalg.norm(raw_points, axis=1)
    if len(radii) != 400:
        raise ValueError("R3 rings holdout requires the registered 400-point dataset")
    sorted_radii = np.sort(radii)
    boundary = float((sorted_radii[199] + sorted_radii[200]) / 2.0)
    labels = np.where(radii <= boundary, "inner", "outer").astype("<U5")
    if np.count_nonzero(labels == "inner") != 200 or np.count_nonzero(labels == "outer") != 200:
        raise ValueError("registered rings fixture must contain 200 points in each ring")
    return labels


def _majority_ring_by_cell(point_cells: np.ndarray, point_rings: np.ndarray, cell_count: int) -> np.ndarray:
    labels = np.full(cell_count, "invalid", dtype="<U7")
    for cell in np.unique(point_cells):
        rings = point_rings[point_cells == cell]
        inner_count = int(np.count_nonzero(rings == "inner"))
        outer_count = int(np.count_nonzero(rings == "outer"))
        if inner_count == outer_count:
            raise ValueError(f"cell {int(cell)} has no unique majority ring")
        labels[cell] = "inner" if inner_count > outer_count else "outer"
    return labels


def _pooled_cell_assignments(dataset: RingsDataset) -> tuple[np.ndarray, np.ndarray]:
    point_ids = np.concatenate([dataset.train_ids, dataset.test_ids]).astype(np.int64, copy=False)
    cell_indices = np.concatenate([dataset.train_indices, dataset.test_indices]).astype(np.int64, copy=False)
    order = np.argsort(point_ids, kind="stable")
    ordered_ids = point_ids[order]
    expected_ids = np.arange(len(point_ids), dtype=np.int64)
    if not np.array_equal(ordered_ids, expected_ids):
        raise ValueError("rings point IDs must partition the pooled 400-point dataset")
    return ordered_ids, cell_indices[order]


def _validate_holdout_options(holdout_fraction: float, min_held_out_cells: int) -> None:
    if not np.isfinite(holdout_fraction) or not 0.0 < holdout_fraction < 1.0:
        raise ValueError("holdout_fraction must be finite and strictly between 0 and 1")
    if not isinstance(min_held_out_cells, (int, np.integer)) or min_held_out_cells < 1:
        raise ValueError("min_held_out_cells must be a positive integer")


@dataclass(frozen=True)
class RingCellHoldout:
    """A deterministic whole-cell interpolation split for one ring size."""

    dataset_hash: str
    n: int
    cell_count: int
    point_ids: np.ndarray
    point_cells: np.ndarray
    point_rings: np.ndarray
    cell_rings: np.ndarray
    data_hit_cells: np.ndarray
    training_cells: np.ndarray
    held_out_cells: np.ndarray
    invalid_cells: np.ndarray
    training_point_ids: np.ndarray
    held_out_point_ids: np.ndarray
    holdout_seed: int
    holdout_fraction: float
    min_held_out_cells: int

    @property
    def valid_cells(self) -> np.ndarray:
        """All cells hit by data, including cells reserved for unseen-valid evaluation."""

        return self.data_hit_cells.copy()

    @property
    def unseen_valid_cells(self) -> np.ndarray:
        """Data-hit cells held out from training."""

        return self.held_out_cells.copy()

    @property
    def held_out_cells_by_ring(self) -> dict[str, np.ndarray]:
        """Held-out data-hit cells assigned by the majority of their points."""

        return {
            ring: self.held_out_cells[self.cell_rings[self.held_out_cells] == ring].copy()
            for ring in ("inner", "outer")
        }

    def validity_labels(self) -> np.ndarray:
        """Return validity labels from data-hit membership, never model output."""

        labels = np.full(self.cell_count, "invalid", dtype="U12")
        labels[self.data_hit_cells] = "valid"
        labels[self.held_out_cells] = "unseen-valid"
        return labels

    def compute_cell_coverage_precision(self, sampled_cells: Sequence[int] | np.ndarray) -> dict[str, Any]:
        """Compute R3 coverage and precision from observed cell IDs.

        Coverage is the fraction of held-out cells hit at least once. Precision
        is the fraction of samples landing in any data-hit cell. An empty
        held-out set makes coverage undefined, and zero samples make precision
        undefined; both cases return ``None`` rather than inventing a value.
        A non-empty sample with no held-out hits has coverage ``0.0``.
        """

        try:
            numeric = np.asarray(sampled_cells, dtype=np.float64)
        except (TypeError, ValueError) as error:
            raise ValueError("sampled_cells must be a one-dimensional integer sequence") from error
        if numeric.ndim != 1 or not np.all(np.isfinite(numeric)):
            raise ValueError("sampled_cells must be a one-dimensional finite integer sequence")
        integer = numeric.astype(np.int64)
        if not np.all(integer == numeric) or np.any(integer < 0) or np.any(integer >= self.cell_count):
            raise ValueError("sampled_cells must contain integer cell IDs in range")

        sample_count = int(len(integer))
        valid_mask = np.isin(integer, self.valid_cells)
        held_out_hits = np.unique(integer[np.isin(integer, self.held_out_cells)])
        coverage = (
            None
            if len(self.held_out_cells) == 0
            else float(len(held_out_hits) / len(self.held_out_cells))
        )
        precision = None if sample_count == 0 else float(np.count_nonzero(valid_mask) / sample_count)
        anchors = r3_coverage_anchors(
            n=self.n,
            held_out_cell_count=len(self.held_out_cells),
            sample_count=sample_count,
            coverage=coverage,
        )
        per_ring_coverage: dict[str, float | None] = {}
        per_ring_hit_cells: dict[str, list[int]] = {}
        per_ring_cell_counts: dict[str, int] = {}
        for ring, ring_cells in self.held_out_cells_by_ring.items():
            ring_hits = np.unique(held_out_hits[np.isin(held_out_hits, ring_cells)])
            per_ring_hit_cells[ring] = ring_hits.tolist()
            per_ring_cell_counts[ring] = int(len(ring_cells))
            per_ring_coverage[ring] = None if len(ring_cells) == 0 else float(len(ring_hits) / len(ring_cells))
        return {
            "primary_endpoint": "coverage",
            "safeguard": "precision",
            "coverage": coverage,
            "precision": precision,
            "sample_count": sample_count,
            "valid_sample_count": int(np.count_nonzero(valid_mask)),
            "invalid_sample_count": int(sample_count - np.count_nonzero(valid_mask)),
            "held_out_cells_hit": held_out_hits.tolist(),
            "held_out_cell_count": int(len(self.held_out_cells)),
            "per_ring_coverage": per_ring_coverage,
            "per_ring_held_out_cells_hit": per_ring_hit_cells,
            "per_ring_held_out_cell_count": per_ring_cell_counts,
            "normalized_coverage": anchors["normalized_coverage"],
            "floor": anchors["floor"],
            "ceiling": anchors["ceiling"],
            "gap_closed": anchors["gap_closed"],
            "anchor_labels": anchors["labels"],
        }

    def manifest(self) -> dict[str, Any]:
        """Serialize the registered split, including the per-n held-out list."""

        return {
            "schema_version": SCHEMA_VERSION,
            "dataset_hash": self.dataset_hash,
            "n": self.n,
            "cell_count": self.cell_count,
            "point_count": len(self.point_ids),
            "point_cells_hash": hash_array(self.point_cells),
            "point_rings_hash": hash_array(self.point_rings),
            "cell_ring_assignment": self.cell_rings.tolist(),
            "ring_assignment_rule": "raw-point radius separates the two registered rings; mixed cells use the point-count majority",
            "data_hit_cells": self.data_hit_cells.tolist(),
            "training_cells": self.training_cells.tolist(),
            "held_out_cells": self.held_out_cells.tolist(),
            "invalid_cells": self.invalid_cells.tolist(),
            "training_point_ids": self.training_point_ids.tolist(),
            "held_out_point_ids": self.held_out_point_ids.tolist(),
            "validity_rule": {
                "valid": "any data-hit cell",
                "unseen_valid": "data-hit cell held out from training",
                "invalid": "cell hit by no data point",
                "source": "GridCodec assignments for pooled points; never model outputs",
            },
            "holdout": {
                "fraction": self.holdout_fraction,
                "minimum_cells": self.min_held_out_cells,
                "selected_cell_count": len(self.held_out_cells),
                "rng_seed": self.holdout_seed,
                "rng_role": "registered cell-holdout selection only; separate from fit and sampling RNGs",
            },
            "manifest_hash": hash_json(
                {
                    "dataset_hash": self.dataset_hash,
                    "n": self.n,
                    "data_hit_cells": self.data_hit_cells.tolist(),
                    "held_out_cells": self.held_out_cells.tolist(),
                    "point_rings_hash": hash_array(self.point_rings),
                    "cell_ring_assignment": self.cell_rings.tolist(),
                    "training_point_ids": self.training_point_ids.tolist(),
                    "held_out_point_ids": self.held_out_point_ids.tolist(),
                    "holdout_seed": self.holdout_seed,
                }
            ),
        }


def compute_cell_coverage_precision(
    holdout: RingCellHoldout, sampled_cells: Sequence[int] | np.ndarray
) -> dict[str, Any]:
    """Compute the registered R3 endpoints for an observed sample sequence."""

    return holdout.compute_cell_coverage_precision(sampled_cells)


def r3_coverage_anchors(
    *, n: int, held_out_cell_count: int, sample_count: int, coverage: float | None
) -> dict[str, Any]:
    """Return descriptive sprayer/oracle anchors without a gap threshold."""

    if not isinstance(n, (int, np.integer)) or n < 1:
        raise ValueError("n must be a positive integer")
    if not isinstance(held_out_cell_count, (int, np.integer)) or held_out_cell_count < 0:
        raise ValueError("held_out_cell_count must be a non-negative integer")
    if not isinstance(sample_count, (int, np.integer)) or sample_count < 0:
        raise ValueError("sample_count must be a non-negative integer")

    floor = float(1.0 - (1.0 - 1.0 / (2**int(n))) ** int(sample_count))
    ceiling = (
        None
        if held_out_cell_count == 0
        else float(1.0 - (1.0 - 1.0 / int(held_out_cell_count)) ** int(sample_count))
    )
    denominator = None if ceiling is None else ceiling - floor
    gap_closed: float | str
    if coverage is None or denominator is None or np.isclose(
        denominator, 0.0, atol=R3_GAP_DENOMINATOR_TOLERANCE, rtol=0.0
    ):
        gap_closed = "undefined"
    else:
        gap_closed = float((coverage - floor) / denominator)
    normalized_coverage = (
        None
        if coverage is None or ceiling is None or np.isclose(ceiling, 0.0, atol=R3_GAP_DENOMINATOR_TOLERANCE, rtol=0.0)
        else float(coverage / ceiling)
    )
    return {
        "floor": floor,
        "ceiling": ceiling,
        "gap_closed": gap_closed,
        "normalized_coverage": normalized_coverage,
        "labels": {
            "floor": "uniform sprayer",
            "ceiling": "ORACLE: ideal uniform sampler over held-out cells",
        },
    }


def r3_sample_budget_grid(n: int) -> list[dict[str, Any]]:
    """Return the registered approximately 10/50/90 percent coverage budgets."""

    if not isinstance(n, (int, np.integer)) or n < 1:
        raise ValueError("n must be a positive integer")
    cell_count = 2**int(n)
    records: list[dict[str, Any]] = []
    for target in (0.10, 0.50, 0.90):
        exact_budget = math.log1p(-target) / math.log1p(-1.0 / cell_count)
        budget = int(round(exact_budget))
        records.append(
            {
                "target_coverage": target,
                "N": budget,
                "exact_N": exact_budget,
                "degenerate": budget < 5,
                "uniform_expected_coverage": float(
                    1.0 - (1.0 - 1.0 / cell_count) ** budget
                ),
            }
        )
    return records


def r3_memorizer_null(holdout: RingCellHoldout, sample_count: int) -> dict[str, Any]:
    """Return the registered empirical memorizer null, without sampling."""

    if not isinstance(sample_count, (int, np.integer)) or sample_count < 0:
        raise ValueError("sample_count must be a non-negative integer")
    per_ring = {
        ring: None if len(cells) == 0 else 0.0
        for ring, cells in holdout.held_out_cells_by_ring.items()
    }
    return {
        "coverage": None if len(holdout.held_out_cells) == 0 else 0.0,
        "precision": 1.0,
        "per_ring_coverage": per_ring,
        "sample_count": int(sample_count),
    }


def r3_uniform_sprayer_null(holdout: RingCellHoldout, sample_count: int) -> dict[str, Any]:
    """Return the closed-form uniform-sprayer null for the registered split."""

    if not isinstance(sample_count, (int, np.integer)) or sample_count < 0:
        raise ValueError("sample_count must be a non-negative integer")
    n = holdout.n
    expected_coverage = float(1.0 - (1.0 - 1.0 / (2**n)) ** int(sample_count))
    per_ring = {
        ring: None if len(cells) == 0 else expected_coverage
        for ring, cells in holdout.held_out_cells_by_ring.items()
    }
    return {
        "coverage": None if len(holdout.held_out_cells) == 0 else expected_coverage,
        "precision": float(len(holdout.valid_cells) / holdout.cell_count),
        "per_ring_coverage": per_ring,
        "sample_count": int(sample_count),
    }


def validate_r3_null_metrics(
    observed: dict[str, Any], expected: dict[str, Any], *, tolerance: float = R3_NULL_TOLERANCE
) -> None:
    """Validate null metrics for red-first tests and fail on corrupted output."""

    for key in ("coverage", "precision"):
        observed_value = observed.get(key)
        expected_value = expected.get(key)
        if observed_value is None or expected_value is None:
            if observed_value is not expected_value:
                raise AssertionError(f"{key}: expected {expected_value!r}, got {observed_value!r}")
        elif not np.isclose(observed_value, expected_value, atol=tolerance, rtol=0.0):
            raise AssertionError(f"{key}: expected {expected_value!r}, got {observed_value!r}")
    for ring in ("inner", "outer"):
        observed_value = observed.get("per_ring_coverage", {}).get(ring)
        expected_value = expected.get("per_ring_coverage", {}).get(ring)
        if observed_value is None or expected_value is None:
            if observed_value is not expected_value:
                raise AssertionError(f"per_ring_coverage[{ring}]: expected {expected_value!r}, got {observed_value!r}")
        elif not np.isclose(observed_value, expected_value, atol=tolerance, rtol=0.0):
            raise AssertionError(f"per_ring_coverage[{ring}]: expected {expected_value!r}, got {observed_value!r}")


def build_ring_cell_holdout(
    dataset: RingsDataset,
    *,
    holdout_seed: int = R3_CELL_HOLDOUT_SEED,
    holdout_fraction: float = R3_CELL_HOLDOUT_FRACTION,
    min_held_out_cells: int = R3_MIN_HELD_OUT_CELLS,
) -> RingCellHoldout:
    """Build the registered R3 holdout without consuming fit/sampling RNGs."""

    _validate_holdout_options(holdout_fraction, min_held_out_cells)
    if not isinstance(holdout_seed, (int, np.integer)):
        raise ValueError("holdout_seed must be an integer")
    point_ids, point_cells = _pooled_cell_assignments(dataset)
    point_rings = _classify_ring_points(_pooled_raw_points(dataset))
    cell_rings = _majority_ring_by_cell(point_cells, point_rings, dataset.codec.size)
    data_hit_cells = np.unique(point_cells)
    selected_count = max(min_held_out_cells, math.ceil(holdout_fraction * len(data_hit_cells)))
    if selected_count >= len(data_hit_cells):
        raise ValueError("holdout must leave at least one data-hit training cell")

    rng = np.random.default_rng(int(holdout_seed))
    held_out_cells = np.sort(rng.choice(data_hit_cells, size=selected_count, replace=False)).astype(np.int64)
    training_cells = np.setdiff1d(data_hit_cells, held_out_cells, assume_unique=True)
    held_out_mask = np.isin(point_cells, held_out_cells)
    training_point_ids = point_ids[~held_out_mask]
    held_out_point_ids = point_ids[held_out_mask]
    invalid_cells = np.setdiff1d(
        np.arange(dataset.codec.size, dtype=np.int64), data_hit_cells, assume_unique=True
    )
    return RingCellHoldout(
        dataset_hash=dataset.dataset_hash,
        n=dataset.codec.n,
        cell_count=dataset.codec.size,
        point_ids=point_ids.copy(),
        point_cells=point_cells.copy(),
        point_rings=point_rings.copy(),
        cell_rings=cell_rings.copy(),
        data_hit_cells=data_hit_cells.copy(),
        training_cells=training_cells,
        held_out_cells=held_out_cells,
        invalid_cells=invalid_cells,
        training_point_ids=training_point_ids,
        held_out_point_ids=held_out_point_ids,
        holdout_seed=int(holdout_seed),
        holdout_fraction=float(holdout_fraction),
        min_held_out_cells=int(min_held_out_cells),
    )


__all__ = [
    "R3_CELL_HOLDOUT_FRACTION",
    "R3_CELL_HOLDOUT_SEED",
    "R3_GAP_DENOMINATOR_TOLERANCE",
    "R3_MIN_HELD_OUT_CELLS",
    "R3_NULL_TOLERANCE",
    "RingCellHoldout",
    "SCHEMA_VERSION",
    "build_ring_cell_holdout",
    "compute_cell_coverage_precision",
    "r3_coverage_anchors",
    "r3_memorizer_null",
    "r3_sample_budget_grid",
    "r3_uniform_sprayer_null",
    "validate_r3_null_metrics",
]
