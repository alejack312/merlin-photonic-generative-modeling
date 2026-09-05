"""Analytic gradient boundary and a finite-difference validation helper."""

from __future__ import annotations

import numpy as np

from .contracts import KernelSpec
from .expectation import expectation_gradient_exact, expectations_and_jacobian_exact
from .objectives import objective_and_gradient_exact


def gradient_exact(theta: np.ndarray, G: np.ndarray, target: object, kernel: KernelSpec) -> np.ndarray:
    return objective_and_gradient_exact(theta, G, target, kernel)[1]


def grad_mmd2_analytic(theta: np.ndarray, G: np.ndarray, target: object, kernel: KernelSpec) -> np.ndarray:
    return gradient_exact(theta, G, target, kernel)


def finite_difference_gradient(function, theta: np.ndarray, step: float = 1e-6) -> np.ndarray:
    if step <= 0 or not np.isfinite(step):
        raise ValueError("step must be positive and finite")
    values = np.asarray(theta, dtype=np.float64)
    if values.ndim != 1 or not np.all(np.isfinite(values)):
        raise ValueError("theta must be a finite vector")
    gradient = np.empty_like(values)
    for index in range(len(values)):
        plus = values.copy()
        minus = values.copy()
        plus[index] += step
        minus[index] -= step
        gradient[index] = (float(function(plus)) - float(function(minus))) / (2.0 * step)
    return gradient


__all__ = ["expectation_gradient_exact", "expectations_and_jacobian_exact", "finite_difference_gradient", "gradient_exact"]
