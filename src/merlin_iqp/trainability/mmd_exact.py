"""Pure-numpy MMD^2 loss and its exact quadratic-form gradient.

Ported from this repo's existing torch implementation (`generator/mmd.py`),
which is differentiable via torch autograd. This module deliberately has NO
torch import anywhere -- Phase 17's exact parameter-shift gradients operate
directly on plain numpy probability vectors, and MerLin's `QuantumLayer`
categorically rejects this project's polarization-annotated `BasicState`s
(confirmed live during Phase 17 research), so autograd-through-a-
differentiable-pipeline is never an option here. `generator/mmd.py`'s torch
formula is read ONLY as a reference to port from and cross-validate against
in tests (`tests/test_mmd_exact.py`) -- it is never imported by this module
or by the production sweep path (`trainability/sweep.py`, Plan 17-05).

Scope note: this module deliberately does NOT implement a Monte-Carlo MMD^2
estimator or an exact/MC crossover switch, unlike the sibling project
`iqp-mmd-barren-plateau` (which needs one at K~2^16-2^20 qubit-string
outcome spaces). This project's binding compute constraint is the photonic
circuit simulation itself, not the K x K spatial-bin kernel matrix -- the
kernel matrix here stays at K<=2^8, where exact enumeration is trivial and
an MC fallback would essentially never trigger.
"""

import numpy as np


def gaussian_kernel_matrix_np(centers: np.ndarray, sigma: float) -> np.ndarray:
    """Pairwise Gaussian kernel matrix over `centers`.

    K[a, b] = exp(-||center_a - center_b||^2 / (2 * sigma^2))

    Numpy port of `generator.mmd.gaussian_kernel_matrix`'s
    `torch.exp(-torch.cdist(centers, centers)**2 / (2*sigma**2))`.
    """
    diff = centers[:, np.newaxis, :] - centers[np.newaxis, :, :]
    dist_sq = np.sum(diff**2, axis=-1)
    return np.exp(-dist_sq / (2 * sigma**2))


def mmd2_np(p: np.ndarray, q: np.ndarray, kernel_matrix: np.ndarray) -> float:
    """Closed-form MMD^2(p, q) = p@K@p + q@K@q - 2*p@K@q, clamped to >= 0.

    Numpy port of `generator.mmd.mmd2`. The clamp is a defensive guard
    against float rounding noise, matching the torch original's
    `torch.clamp(..., min=0)`.
    """
    value = p @ kernel_matrix @ p + q @ kernel_matrix @ q - 2 * p @ kernel_matrix @ q
    return float(max(0.0, value))


def mmd2_grad(
    q: np.ndarray,
    p: np.ndarray,
    kernel_matrix: np.ndarray,
    dq_dtheta: np.ndarray,
) -> float:
    """Exact gradient of MMD^2(p, q) with respect to a circuit parameter
    theta, given the exact per-bin derivative dq_dtheta = dq/d(theta).

    d(MMD^2)/d(theta) = 2 * (q - p) @ K @ dq_dtheta

    This is the ordinary quadratic-form chain rule applied to
    MMD^2(p, q) = p@K@p + q@K@q - 2*p@K@q (holding p fixed, since p is the
    target distribution and carries no theta-dependence). It is EXACT, not
    an approximation -- provided dq_dtheta is itself the exact per-bin
    derivative of q with respect to theta (e.g. from parameter-shift, per
    Plan 17-01), the multivariate chain rule composed with this quadratic
    form is exact regardless of MMD^2 being quartic in the circuit's
    amplitudes (see 17-RESEARCH.md Pattern 2).

    Note: this is the unclamped derivative of the quadratic form itself.
    The clamp in `mmd2_np` is a measure-zero defensive guard (only ever
    active exactly at MMD^2 == 0, i.e. p == q) and is not differentiated
    through here, matching standard practice for subgradient-at-a-kink
    edge cases that don't arise in practice for distinct p, q.
    """
    return float(2.0 * (q - p) @ kernel_matrix @ dq_dtheta)
