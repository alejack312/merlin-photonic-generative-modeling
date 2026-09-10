"""Finite Gaussian kernels and their Walsh representations."""

from __future__ import annotations

import numpy as np

from ._validation import finite_vector


def _mixture(sigmas: float | list[float] | tuple[float, ...], weights: list[float] | tuple[float, ...] | None = None) -> tuple[np.ndarray, np.ndarray]:
    values = np.asarray([sigmas] if np.isscalar(sigmas) else sigmas, dtype=np.float64)
    if values.ndim != 1 or not len(values) or not np.all(np.isfinite(values)) or np.any(values <= 0):
        raise ValueError("sigmas must contain positive finite values")
    probs = np.ones(len(values), dtype=np.float64) if weights is None else finite_vector(weights, name="weights", length=len(values))
    if np.any(probs < 0) or not probs.sum() > 0:
        raise ValueError("weights must be non-negative with positive total mass")
    return values, probs / probs.sum()


def gaussian_hamming_kernel(x: np.ndarray, y: np.ndarray, sigma: float = 1.0) -> float:
    if not np.isfinite(sigma) or sigma <= 0:
        raise ValueError("sigma must be positive and finite")
    a, b = np.asarray(x), np.asarray(y)
    if a.ndim != 1 or b.shape != a.shape:
        raise ValueError("x and y must be same-shaped vectors")
    return float(np.exp(-np.count_nonzero(a != b) / (2.0 * sigma**2)))


def gaussian_tau(sigma: float) -> float:
    if not np.isfinite(sigma) or sigma <= 0:
        raise ValueError("sigma must be positive and finite")
    return float(np.tanh(1.0 / (4.0 * sigma**2)))


def gaussian_spectral_weights(n: int, sigma: float) -> np.ndarray:
    if n < 0:
        raise ValueError("n must be non-negative")
    return gaussian_tau(sigma) ** np.arange(n + 1)


def gaussian_hamming_matrix(n: int, sigma: float = 1.0, *, sigmas: list[float] | None = None, weights: list[float] | None = None) -> np.ndarray:
    if n < 0 or n > 12:
        raise ValueError("n must be between 0 and 12 for a full kernel matrix")
    states = _bits(n)
    values, probs = _mixture(sigma if sigmas is None else sigmas, weights)
    distances = np.count_nonzero(states[:, None, :] != states[None, :, :], axis=2)
    return sum(weight * np.exp(-distances / (2.0 * value**2)) for value, weight in zip(values, probs, strict=True))


def gaussian_hamming_spectrum(n: int, sigma: float | list[float] | tuple[float, ...] = 1.0, weights: list[float] | tuple[float, ...] | None = None) -> np.ndarray:
    """Return one Walsh eigenvalue per observable, in MSB lexicographic order."""
    values, probs = _mixture(sigma, weights)
    result = np.zeros(2**n, dtype=np.float64)
    observables = _bits(n)
    for value, weight in zip(values, probs, strict=True):
        r = np.exp(-1.0 / (2.0 * value**2))
        base = (1.0 + r) / 2.0
        ratio = (1.0 - r) / (1.0 + r)
        result += weight * base**n * ratio**observables.sum(axis=1)
    return result


def hamming_walsh_matrix(n: int) -> np.ndarray:
    bits = _bits(n)
    return (1.0 - 2.0 * ((bits @ bits.T) % 2)).astype(np.float64)


def spatial_walsh_matrix(centers: np.ndarray, sigma: float = 1.0, *, sigmas: list[float] | None = None, weights: list[float] | None = None) -> np.ndarray:
    points = np.asarray(centers, dtype=np.float64)
    if points.ndim != 2 or len(points) == 0 or not np.all(np.isfinite(points)):
        raise ValueError("centers must be a non-empty finite matrix")
    values, probs = _mixture(sigma if sigmas is None else sigmas, weights)
    delta = points[:, None, :] - points[None, :, :]
    squared_distance = np.sum(delta * delta, axis=2)
    K = sum(weight * np.exp(-squared_distance / (2.0 * value**2)) for value, weight in zip(values, probs, strict=True))
    if len(points) & (len(points) - 1):
        raise ValueError("spatial Walsh representation requires 2^n centers")
    n = int(np.log2(len(points)))
    W = hamming_walsh_matrix(n)
    return W @ K @ W.T / len(points)**2


def _bits(n: int) -> np.ndarray:
    if n < 0 or n > 20:
        raise ValueError("n must be between 0 and 20")
    indices = np.arange(2**n, dtype=np.uint64)
    shifts = np.arange(n - 1, -1, -1, dtype=np.uint64)
    return ((indices[:, None] >> shifts[None, :]) & 1).astype(np.uint8)
