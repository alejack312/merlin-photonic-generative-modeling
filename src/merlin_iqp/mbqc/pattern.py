"""Validated incidence-graph objects for the logical M1 construction."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np


def _validate_matrix(value: Any) -> np.ndarray:
    matrix = np.asarray(value)
    if matrix.ndim != 2 or matrix.shape[1] < 1:
        raise ValueError("G must have shape (M, n) with n >= 1")
    if not np.all(np.isfinite(matrix)) or not np.all((matrix == 0) | (matrix == 1)):
        raise ValueError("G must contain only finite binary values")
    return matrix.astype(np.uint8, copy=True)


def _validate_theta(value: Any, m: int) -> np.ndarray:
    theta = np.asarray(value, dtype=np.float64)
    if theta.ndim != 1 or theta.shape != (m,):
        raise ValueError(f"theta must have shape ({m},)")
    if not np.all(np.isfinite(theta)):
        raise ValueError("theta must contain only finite values")
    return theta.copy()


@dataclass(frozen=True)
class M1Pattern:
    """An ordered, fixed-basis M1 incidence graph.

    The matrix rows are generator masks.  Its transpose maps the ordered
    ancilla outcome vector to the data-output XOR map.  Empty ``G`` is allowed
    for the M=0 adversarial fixture, while the data width remains positive.
    """

    G: np.ndarray
    raw_theta: np.ndarray
    effective_theta: np.ndarray
    provenance: dict[str, Any] | None = None

    def __post_init__(self) -> None:
        matrix = _validate_matrix(self.G)
        raw_theta = _validate_theta(self.raw_theta, len(matrix))
        effective_theta = _validate_theta(self.effective_theta, len(matrix))
        object.__setattr__(self, "G", matrix)
        object.__setattr__(self, "raw_theta", raw_theta)
        object.__setattr__(self, "effective_theta", effective_theta)
        object.__setattr__(self, "provenance", dict(self.provenance or {}))

    @property
    def n(self) -> int:
        return int(self.G.shape[1])

    @property
    def m(self) -> int:
        return int(self.G.shape[0])

    @property
    def theta(self) -> np.ndarray:
        """The effective negative-phase angles used by the reference evaluator."""

        return self.effective_theta.copy()

    @property
    def output_xor_map(self) -> np.ndarray:
        """Return the n-by-M map whose action is ``G.T @ s mod 2``."""

        return self.G.T.copy()

    @property
    def edge_count(self) -> int:
        return int(self.G.sum())

    def manifest(self) -> dict[str, Any]:
        return {
            "n": self.n,
            "m": self.m,
            "generator_masks": self.G.tolist(),
            "raw_theta": self.raw_theta.tolist(),
            "effective_theta": self.effective_theta.tolist(),
            "output_xor_map": self.output_xor_map.tolist(),
            "edge_count": self.edge_count,
            "fixed_bases": {
                "data": "X",
                "ancilla": "b(theta_j) from the registered M1 construction",
            },
            "ideal_feed_forward_rounds": 0,
            "logical_only": True,
            "provenance": dict(self.provenance),
        }
