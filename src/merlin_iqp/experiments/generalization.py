"""Registered cell-level holdout contract for the R3 rings benchmark.

The historical rings pipeline keeps its point-level split for continuity.
R3 generalization instead pools all 400 points, assigns them with the
existing :class:`GridCodec`, and holds out whole data-hit cells. This module
contains only that split and its manifest; it does not train a model or use
model outputs to define validity.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Any

import numpy as np

from merlin_iqp.classical._validation import hash_array, hash_json

from .datasets import RingsDataset


SCHEMA_VERSION = "v4_tcdp.ring_cell_holdout.v1"
R3_CELL_HOLDOUT_SEED = 20260928
R3_CELL_HOLDOUT_FRACTION = 0.20
R3_MIN_HELD_OUT_CELLS = 3


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

    def validity_labels(self) -> np.ndarray:
        """Return validity labels from data-hit membership, never model output."""

        labels = np.full(self.cell_count, "invalid", dtype="U12")
        labels[self.data_hit_cells] = "valid"
        labels[self.held_out_cells] = "unseen-valid"
        return labels

    def manifest(self) -> dict[str, Any]:
        """Serialize the registered split, including the per-n held-out list."""

        return {
            "schema_version": SCHEMA_VERSION,
            "dataset_hash": self.dataset_hash,
            "n": self.n,
            "cell_count": self.cell_count,
            "point_count": len(self.point_ids),
            "point_cells_hash": hash_array(self.point_cells),
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
                    "training_point_ids": self.training_point_ids.tolist(),
                    "held_out_point_ids": self.held_out_point_ids.tolist(),
                    "holdout_seed": self.holdout_seed,
                }
            ),
        }


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
    "R3_MIN_HELD_OUT_CELLS",
    "RingCellHoldout",
    "SCHEMA_VERSION",
    "build_ring_cell_holdout",
]
