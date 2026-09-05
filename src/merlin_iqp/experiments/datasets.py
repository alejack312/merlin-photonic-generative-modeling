"""NumPy-only frozen data and geometry adapter for the v4 ring study.

The legacy generator owns the source data recipe.  This module reproduces the
recipe without importing torch so that the new classical IQP trainer has a
small, inspectable boundary: raw points and split IDs, train-derived
normalization, and the per-``n`` row-major ``2**n`` grid.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
from sklearn.datasets import make_circles
from sklearn.model_selection import train_test_split

from merlin_iqp.classical._validation import hash_array, hash_json
from merlin_iqp.classical.contracts import DatasetBundle
from merlin_iqp.classical.targets import ExactProbabilities


SCHEMA_VERSION = "v4_tcdp.rings_dataset.v1"
DATASET_ID = "rings.make_circles.400.seed42.split42.train_minmax"


def _row_major_centers(n: int, lo: float, hi: float) -> tuple[np.ndarray, int, int]:
    if not isinstance(n, (int, np.integer)) or n < 1 or n > 20:
        raise ValueError("n must be an integer between 1 and 20")
    if not np.isfinite(lo) or not np.isfinite(hi) or not lo < hi:
        raise ValueError("lo and hi must be finite and satisfy lo < hi")
    rows = 2 ** ((n + 1) // 2)
    cols = 2 ** (n // 2)
    xs = np.linspace(lo, hi, rows)
    ys = np.linspace(lo, hi, cols)
    gx, gy = np.meshgrid(xs, ys, indexing="ij")
    return np.stack([gx.ravel(), gy.ravel()], axis=1), rows, cols


@dataclass(frozen=True)
class GridCodec:
    """The fixed bitstring-to-cell convention used by the ring profiles."""

    n: int
    centers: np.ndarray
    rows: int
    cols: int
    lo: float = -0.1
    hi: float = 1.1
    bit_order: str = "msb_first"
    index_order: str = "row_major"
    tie_breaking: str = "lowest_row_major_index"

    def __post_init__(self) -> None:
        centers = np.asarray(self.centers, dtype=np.float64)
        if centers.shape != (2**self.n, 2) or not np.all(np.isfinite(centers)):
            raise ValueError("centers must have shape (2**n, 2) and be finite")
        if self.rows * self.cols != 2**self.n:
            raise ValueError("rows and cols must cover the complete grid")
        object.__setattr__(self, "centers", centers.copy())

    @property
    def size(self) -> int:
        return 2**self.n

    def bitstring(self, index: int) -> str:
        if not isinstance(index, (int, np.integer)) or not 0 <= int(index) < self.size:
            raise ValueError(f"index must be in [0, {self.size})")
        return format(int(index), f"0{self.n}b")

    def index(self, bitstring: str) -> int:
        if not isinstance(bitstring, str) or len(bitstring) != self.n or set(bitstring) - {"0", "1"}:
            raise ValueError(f"bitstring must be a {self.n}-bit binary string")
        return int(bitstring, 2)

    def encode(self, points: np.ndarray) -> np.ndarray:
        """Assign points to nearest centers; ties choose the lowest index."""
        values = np.asarray(points)
        if values.ndim != 2 or values.shape[1] != 2 or not np.all(np.isfinite(values)):
            raise ValueError("points must be a finite matrix with shape (samples, 2)")
        # This squared-expansion form matches the existing NumPy target-grid
        # port and preserves argmin's first/lowest-index tie behavior.
        data = values.astype(np.float32, copy=False)
        data_sq = np.sum(data**2, axis=1, keepdims=True)
        center_sq = np.sum(self.centers**2, axis=1, keepdims=True).T
        cross = data @ self.centers.T
        squared = np.clip(data_sq - 2.0 * cross + center_sq, a_min=0.0, a_max=None)
        return np.argmin(squared, axis=1).astype(np.int64)

    def decode(self, indices: np.ndarray | list[int]) -> np.ndarray:
        values = np.asarray(indices)
        if values.ndim != 1 or not np.all(np.isfinite(values)):
            raise ValueError("indices must be a finite vector")
        integer = values.astype(np.int64)
        if not np.all(integer == values) or np.any(integer < 0) or np.any(integer >= self.size):
            raise ValueError("indices must be integer cell indices in range")
        return self.centers[integer].copy()

    def mapping(self) -> list[dict[str, Any]]:
        return [
            {
                "index": index,
                "bitstring": self.bitstring(index),
                "row": index // self.cols,
                "column": index % self.cols,
                "center": [float(x) for x in self.centers[index]],
            }
            for index in range(self.size)
        ]

    def manifest(self) -> dict[str, Any]:
        return {
            "n": self.n,
            "rows": self.rows,
            "cols": self.cols,
            "lo": self.lo,
            "hi": self.hi,
            "bit_order": self.bit_order,
            "index_order": self.index_order,
            "tie_breaking": self.tie_breaking,
            "centers_hash": hash_array(self.centers),
            "mapping": self.mapping(),
        }


def make_grid_codec(n: int, *, lo: float = -0.1, hi: float = 1.1) -> GridCodec:
    centers, rows, cols = _row_major_centers(n, lo, hi)
    return GridCodec(n=n, centers=centers, rows=rows, cols=cols, lo=lo, hi=hi)


def _nearest_diagnostics(points: np.ndarray, codec: GridCodec, indices: np.ndarray) -> dict[str, Any]:
    decoded = codec.decode(indices)
    error = np.asarray(points, dtype=np.float64) - decoded
    distances = np.sqrt(np.sum(error * error, axis=1))
    data = np.asarray(points, dtype=np.float32)
    data_sq = np.sum(data**2, axis=1, keepdims=True)
    center_sq = np.sum(codec.centers**2, axis=1, keepdims=True).T
    squared = np.clip(data_sq - 2.0 * (data @ codec.centers.T) + center_sq, a_min=0.0, a_max=None)
    minima = np.min(squared, axis=1, keepdims=True)
    exact_ties = np.sum(squared == minima, axis=1)
    return {
        "samples": int(len(points)),
        "mean_euclidean_error": float(np.mean(distances)),
        "rms_euclidean_error": float(np.sqrt(np.mean(distances**2))),
        "max_euclidean_error": float(np.max(distances, initial=0.0)),
        "mean_squared_error": float(np.mean(distances**2)),
        "exact_tie_count": int(np.count_nonzero(exact_ties > 1)),
        "max_tie_multiplicity": int(np.max(exact_ties, initial=0)),
        "tie_breaking": codec.tie_breaking,
    }


def _histogram(indices: np.ndarray, size: int) -> tuple[np.ndarray, np.ndarray]:
    counts = np.bincount(indices, minlength=size).astype(np.int64)
    probabilities = counts.astype(np.float64) / float(counts.sum())
    return counts, probabilities


@dataclass(frozen=True)
class RingsDataset:
    """Frozen raw/normalized ring splits and their exact grid projections."""

    codec: GridCodec
    raw_train: np.ndarray
    raw_test: np.ndarray
    normalized_train: np.ndarray
    normalized_test: np.ndarray
    train_ids: np.ndarray
    test_ids: np.ndarray
    min_values: np.ndarray
    max_values: np.ndarray
    scale: np.ndarray
    train_indices: np.ndarray
    test_indices: np.ndarray
    train_counts: np.ndarray
    test_counts: np.ndarray
    train_histogram: np.ndarray
    test_histogram: np.ndarray
    train_quantization: dict[str, Any]
    test_quantization: dict[str, Any]
    dataset_hash: str

    @property
    def train_target(self) -> ExactProbabilities:
        return ExactProbabilities(self.train_histogram, provenance={"dataset_id": DATASET_ID, "split": "train"})

    @property
    def test_target(self) -> ExactProbabilities:
        return ExactProbabilities(self.test_histogram, provenance={"dataset_id": DATASET_ID, "split": "test"})

    def bundle(self) -> DatasetBundle:
        return DatasetBundle(
            schema_version=SCHEMA_VERSION,
            dataset_id=DATASET_ID,
            n=self.codec.n,
            representation="normalized_xy_with_row_major_grid_codec",
            train=self.train_target,
            test=self.test_target,
            provenance={"source_loader": "merlin_iqp.generator.data.load_circles_data", "random_state": 42},
            preprocessing={
                "normalization": "(x - train_min) / clip(train_max - train_min, 1e-6, inf)",
                "train_min": self.min_values.tolist(),
                "train_max": self.max_values.tolist(),
                "scale": self.scale.tolist(),
            },
            feature_order=("x", "y"),
            dataset_hash=self.dataset_hash,
        )

    def manifest(self) -> dict[str, Any]:
        return {
            "schema_version": SCHEMA_VERSION,
            "dataset_id": DATASET_ID,
            "dataset_hash": self.dataset_hash,
            "n": self.codec.n,
            "raw_split_sizes": {"train": len(self.raw_train), "test": len(self.raw_test)},
            "train_ids_hash": hash_array(self.train_ids),
            "test_ids_hash": hash_array(self.test_ids),
            "raw_train_hash": hash_array(self.raw_train),
            "raw_test_hash": hash_array(self.raw_test),
            "normalized_train_hash": hash_array(self.normalized_train),
            "normalized_test_hash": hash_array(self.normalized_test),
            "transform": {
                "kind": "train_derived_minmax",
                "min_values": self.min_values.tolist(),
                "max_values": self.max_values.tolist(),
                "scale": self.scale.tolist(),
                "clip_floor": 1e-6,
                "normalized_dtype": str(self.normalized_train.dtype),
            },
            "codec": self.codec.manifest(),
            "histograms": {
                "train_counts": self.train_counts.tolist(),
                "test_counts": self.test_counts.tolist(),
                "train_hash": hash_array(self.train_histogram),
                "test_hash": hash_array(self.test_histogram),
            },
            "quantization": {"train": self.train_quantization, "test": self.test_quantization},
        }


def load_rings_dataset(n: int = 4) -> RingsDataset:
    """Reproduce the legacy loader and add deterministic split/codec evidence."""
    raw, _labels = make_circles(n_samples=400, random_state=42)
    identifiers = np.arange(len(raw), dtype=np.int64)
    train_ids, test_ids = train_test_split(identifiers, test_size=0.2, random_state=42)
    raw_train = raw[train_ids]
    raw_test = raw[test_ids]
    min_values = raw_train.min(axis=0, keepdims=True)
    max_values = raw_train.max(axis=0, keepdims=True)
    scale = np.clip(max_values - min_values, a_min=1e-6, a_max=None)
    normalized_train = ((raw_train - min_values) / scale).astype(np.float32)
    normalized_test = ((raw_test - min_values) / scale).astype(np.float32)

    codec = make_grid_codec(n)
    train_indices = codec.encode(normalized_train)
    test_indices = codec.encode(normalized_test)
    train_counts, train_histogram = _histogram(train_indices, codec.size)
    test_counts, test_histogram = _histogram(test_indices, codec.size)
    hash_payload = {
        "dataset_id": DATASET_ID,
        "n": n,
        "raw_train": hash_array(raw_train),
        "raw_test": hash_array(raw_test),
        "normalized_train": hash_array(normalized_train),
        "normalized_test": hash_array(normalized_test),
        "train_ids": hash_array(train_ids),
        "test_ids": hash_array(test_ids),
        "transform": {"min": min_values.tolist(), "max": max_values.tolist(), "scale": scale.tolist()},
        "codec": {"centers": hash_array(codec.centers), "n": n, "lo": codec.lo, "hi": codec.hi},
        "train_histogram": hash_array(train_histogram),
        "test_histogram": hash_array(test_histogram),
    }
    return RingsDataset(
        codec=codec,
        raw_train=raw_train.copy(),
        raw_test=raw_test.copy(),
        normalized_train=normalized_train,
        normalized_test=normalized_test,
        train_ids=np.asarray(train_ids, dtype=np.int64),
        test_ids=np.asarray(test_ids, dtype=np.int64),
        min_values=min_values.ravel().copy(),
        max_values=max_values.ravel().copy(),
        scale=scale.ravel().copy(),
        train_indices=train_indices,
        test_indices=test_indices,
        train_counts=train_counts,
        test_counts=test_counts,
        train_histogram=train_histogram,
        test_histogram=test_histogram,
        train_quantization=_nearest_diagnostics(normalized_train, codec, train_indices),
        test_quantization=_nearest_diagnostics(normalized_test, codec, test_indices),
        dataset_hash=hash_json(hash_payload),
    )


__all__ = ["DATASET_ID", "SCHEMA_VERSION", "GridCodec", "RingsDataset", "load_rings_dataset", "make_grid_codec"]
