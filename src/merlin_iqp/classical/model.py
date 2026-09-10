"""Pure NumPy exact IQP model."""

from __future__ import annotations

import numpy as np

from ._validation import binary_matrix, finite_vector


class IQPModel:
    def __init__(self, G: np.ndarray, theta: np.ndarray | None = None, provenance: dict[str, object] | None = None) -> None:
        matrix = binary_matrix(G, name="G")
        if np.any(matrix.sum(axis=1) == 0):
            raise ValueError("G cannot contain zero-weight rows")
        values = np.zeros(len(matrix), dtype=np.float64) if theta is None else finite_vector(theta, name="theta", length=len(matrix))
        self.G = matrix
        self.theta = values.copy()
        self.provenance = dict(provenance or {})

    @property
    def n(self) -> int:
        return int(self.G.shape[1])

    @property
    def m(self) -> int:
        return int(self.G.shape[0])

    def copy(self) -> "IQPModel":
        return IQPModel(self.G.copy(), self.theta.copy(), self.provenance.copy())

    def probability_vector_exact(self, max_qubits: int = 20) -> np.ndarray:
        if self.n > max_qubits:
            raise ValueError(f"exact probability vector infeasible for n={self.n} > max_qubits={max_qubits}")
        bits = _bits(self.n)
        signs = 1.0 - 2.0 * ((bits @ self.G.T) % 2).astype(np.float64)
        diagonal = np.exp(-1j * (signs @ self.theta))
        amplitudes = _fwht(diagonal) / 2**self.n
        probabilities = np.abs(amplitudes) ** 2
        return probabilities / probabilities.sum()

    output_probabilities_exact = probability_vector_exact


def _bits(n: int) -> np.ndarray:
    indices = np.arange(2**n, dtype=np.uint64)
    shifts = np.arange(n - 1, -1, -1, dtype=np.uint64)
    return ((indices[:, None] >> shifts[None, :]) & 1).astype(np.uint8)


def _fwht(values: np.ndarray) -> np.ndarray:
    result = values.copy()
    width = 1
    while width < len(result):
        for start in range(0, len(result), width * 2):
            top = result[start : start + width].copy()
            bottom = result[start + width : start + 2 * width].copy()
            result[start : start + width] = top + bottom
            result[start + width : start + 2 * width] = top - bottom
        width *= 2
    return result
