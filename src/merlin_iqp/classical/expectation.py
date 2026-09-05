"""Exact IQP parity expectations and analytic Jacobians."""

from __future__ import annotations

import numpy as np

from ._validation import binary_matrix, binary_vector, finite_vector


def all_bitstrings(n: int) -> np.ndarray:
    if n < 0 or n > 20:
        raise ValueError("n must be between 0 and 20")
    indices = np.arange(2**n, dtype=np.uint64)
    shifts = np.arange(n - 1, -1, -1, dtype=np.uint64)
    return ((indices[:, None] >> shifts[None, :]) & 1).astype(np.uint8)


def all_observables(n: int) -> np.ndarray:
    return all_bitstrings(n)


def _validate(theta: np.ndarray, G: np.ndarray, a: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    matrix = binary_matrix(G, name="G")
    values = finite_vector(theta, name="theta", length=len(matrix))
    observable = binary_vector(a, name="a", width=matrix.shape[1])
    if np.any(matrix.sum(axis=1) == 0):
        raise ValueError("G cannot contain zero-weight rows")
    return values, matrix, observable


def _phases(theta: np.ndarray, G: np.ndarray, z: np.ndarray, a: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    overlap = ((G @ a) % 2).astype(np.float64)
    signs = 1.0 - 2.0 * ((z @ G.T) % 2).astype(np.float64)
    return 2.0 * (signs @ (theta * overlap)), overlap, signs


def expectation_exact(theta: np.ndarray, G: np.ndarray, a: np.ndarray) -> float:
    values, matrix, observable = _validate(theta, G, a)
    z = all_bitstrings(matrix.shape[1])
    phases, _, _ = _phases(values, matrix, z, observable)
    return float(np.cos(phases).mean())


def iqp_phase(theta: np.ndarray, G: np.ndarray, z: np.ndarray, a: np.ndarray) -> np.ndarray:
    """Sibling-compatible phase helper, retaining the NumPy-only boundary."""
    values, matrix, observable = _validate(theta, G, a)
    samples = binary_matrix(z, name="z", width=matrix.shape[1])
    return _phases(values, matrix, samples, observable)[0]


def iqp_expectation_exact(theta: np.ndarray, G: np.ndarray, a: np.ndarray) -> float:
    return expectation_exact(theta, G, a)


def expectation_gradient_exact(theta: np.ndarray, G: np.ndarray, a: np.ndarray, param_idx: int) -> float:
    values, matrix, observable = _validate(theta, G, a)
    if not 0 <= param_idx < len(values):
        raise IndexError("param_idx is out of range")
    z = all_bitstrings(matrix.shape[1])
    phases, overlap, signs = _phases(values, matrix, z, observable)
    return float(np.mean(-2.0 * np.sin(phases) * overlap[param_idx] * signs[:, param_idx]))


def grad_expectation_exact(theta: np.ndarray, G: np.ndarray, a: np.ndarray, param_idx: int) -> float:
    return expectation_gradient_exact(theta, G, a, param_idx)


def expectations_and_jacobian_exact(theta: np.ndarray, G: np.ndarray, observables: np.ndarray | None = None) -> tuple[np.ndarray, np.ndarray]:
    matrix = binary_matrix(G, name="G")
    values = finite_vector(theta, name="theta", length=len(matrix))
    if observables is None:
        obs = all_observables(matrix.shape[1])
    else:
        obs = binary_matrix(observables, name="observables", width=matrix.shape[1])
    z = all_bitstrings(matrix.shape[1])
    signs = 1.0 - 2.0 * ((z @ matrix.T) % 2).astype(np.float64)
    overlaps = ((obs @ matrix.T) % 2).astype(np.float64)
    phases = 2.0 * ((signs * values[None, :]) @ overlaps.T)
    expectations = np.cos(phases).mean(axis=0)
    jacobian = np.empty((len(obs), len(values)), dtype=np.float64)
    sine = np.sin(phases)
    for index in range(len(values)):
        jacobian[:, index] = np.mean(-2.0 * sine * signs[:, index, None] * overlaps[:, index][None, :], axis=0)
    return expectations, jacobian
