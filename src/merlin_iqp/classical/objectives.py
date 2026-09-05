"""Exact finite-vector Gaussian MMD objectives and analytic gradients."""

from __future__ import annotations

import numpy as np

from .contracts import KernelSpec
from .expectation import expectations_and_jacobian_exact
from .kernel import gaussian_hamming_matrix, gaussian_hamming_spectrum, hamming_walsh_matrix, spatial_walsh_matrix
from .targets import all_observables, target_moments, target_probability_vector


def _target_vector(target: object, n: int) -> np.ndarray:
    vector = target_probability_vector(target, n)
    if vector.shape != (2**n,):
        raise ValueError("target vector has the wrong size")
    return vector


def hamming_mmd2(p: np.ndarray, q: np.ndarray, sigma: float = 1.0, *, sigmas: list[float] | None = None, weights: list[float] | None = None) -> float:
    p_vec, q_vec = _probabilities(p, q)
    if len(p_vec) != len(q_vec):
        raise ValueError("p and q must have equal lengths")
    n = int(np.log2(len(p_vec)))
    delta = p_vec - q_vec
    return float(delta @ gaussian_hamming_matrix(n, sigma, sigmas=sigmas, weights=weights) @ delta)


def hamming_mmd2_walsh(p: np.ndarray, q: np.ndarray, sigma: float = 1.0, *, sigmas: list[float] | None = None, weights: list[float] | None = None) -> float:
    p_vec, q_vec = _probabilities(p, q)
    n = int(np.log2(len(p_vec)))
    delta = hamming_walsh_matrix(n) @ (p_vec - q_vec)
    return float(np.sum(gaussian_hamming_spectrum(n, sigma if sigmas is None else sigmas, weights) * delta**2))


def spatial_mmd2(p: np.ndarray, q: np.ndarray, centers: np.ndarray, sigma: float = 1.0, *, sigmas: list[float] | None = None, weights: list[float] | None = None) -> float:
    p_vec, q_vec = _probabilities(p, q)
    points = np.asarray(centers, dtype=np.float64)
    if len(points) != len(p_vec):
        raise ValueError("centers and probability vectors must have equal lengths")
    delta = p_vec - q_vec
    # The direct form intentionally remains available for the generic spatial path.
    distances = np.sum((points[:, None, :] - points[None, :, :]) ** 2, axis=2)
    sig_values = [sigma] if sigmas is None else sigmas
    mix = np.ones(len(sig_values)) if weights is None else np.asarray(weights, dtype=np.float64)
    mix /= mix.sum()
    K = sum(w * np.exp(-distances / (2.0 * s**2)) for s, w in zip(sig_values, mix, strict=True))
    return float(delta @ K @ delta)


def objective_and_gradient_exact(theta: np.ndarray, G: np.ndarray, target: object, kernel: KernelSpec) -> tuple[float, np.ndarray]:
    n = np.asarray(G).shape[1]
    observables = all_observables(n)
    model_moments, jacobian = expectations_and_jacobian_exact(theta, G, observables)
    target_values = target_moments(target, observables).values
    delta = target_values - model_moments
    if kernel.kind == "hamming_gaussian":
        weights = gaussian_hamming_spectrum(n, kernel.sigmas, kernel.mixture_weights)
        loss = float(np.sum(weights * delta**2))
        gradient = -2.0 * jacobian.T @ (weights * delta)
        return loss, gradient
    if kernel.centers is None:
        raise ValueError("spatial kernel needs centers")
    B = spatial_walsh_matrix(kernel.centers, kernel.sigmas[0], sigmas=list(kernel.sigmas), weights=list(kernel.mixture_weights))
    loss = float(delta @ B @ delta)
    return loss, -2.0 * jacobian.T @ (B @ delta)


def mmd2_exact(theta: np.ndarray, G: np.ndarray, target: object, kernel: KernelSpec) -> float:
    return objective_and_gradient_exact(theta, G, target, kernel)[0]


def mmd2_exact_small_n(theta: np.ndarray, G: np.ndarray, target: object, kernel: str | KernelSpec = "gaussian", *, sigma: float = 1.0, **kernel_params: object) -> float:
    """Sibling-named exact objective, adapted to typed weighted targets."""
    if isinstance(kernel, str):
        if kernel not in {"gaussian", "hamming_gaussian", "spatial_gaussian"}:
            raise ValueError(f"unsupported kernel {kernel!r}")
        kind = "hamming_gaussian" if kernel in {"gaussian", "hamming_gaussian"} else "spatial_gaussian"
        spec = KernelSpec(kind=kind, sigma=sigma, centers=kernel_params.get("centers")) if kind == "spatial_gaussian" else KernelSpec(kind=kind, sigma=sigma)
    else:
        spec = kernel
    return mmd2_exact(theta, G, target, spec)


def _probabilities(p: np.ndarray, q: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    p_vec = np.asarray(p, dtype=np.float64)
    q_vec = np.asarray(q, dtype=np.float64)
    for name, value in (("p", p_vec), ("q", q_vec)):
        if value.ndim != 1 or len(value) == 0 or len(value) & (len(value) - 1) or not np.all(np.isfinite(value)) or np.any(value < 0) or not np.isclose(value.sum(), 1.0):
            raise ValueError(f"{name} must be a finite probability vector of length 2^n")
    return p_vec, q_vec
