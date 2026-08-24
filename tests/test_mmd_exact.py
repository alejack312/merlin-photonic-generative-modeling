"""TDD tests for trainability/mmd_exact.py.

Proves two things:
1. The pure-numpy kernel/MMD^2 port matches the existing torch implementation
   (generator/mmd.py) to floating-point precision on identical inputs.
2. The exact MMD^2 gradient chain-rule formula (mmd2_grad) is algebraically
   exact, not just plausible -- checked against a synthetic linear model
   q(theta) = q0 + theta*dq, where the true derivative is known in closed
   form by expanding the quadratic.
"""

import numpy as np
import pytest
import torch

from merlin_iqp.generator.mmd import gaussian_kernel_matrix, mmd2, SIGMA_GRID
from merlin_iqp.trainability.mmd_exact import gaussian_kernel_matrix_np, mmd2_np, mmd2_grad


def _make_centers(n=10, seed=0):
    rng = np.random.default_rng(seed)
    return rng.uniform(-0.1, 1.1, size=(n, 2))


def _make_prob_vector(n, seed):
    rng = np.random.default_rng(seed)
    v = rng.random(n)
    return v / v.sum()


@pytest.mark.parametrize("sigma", SIGMA_GRID)
def test_kernel_matrix_matches_torch(sigma):
    centers_np = _make_centers()
    K_np = gaussian_kernel_matrix_np(centers_np, sigma)
    K_torch = gaussian_kernel_matrix(
        torch.tensor(centers_np, dtype=torch.float64), sigma
    ).numpy()
    assert K_np.shape == (10, 10)
    np.testing.assert_allclose(K_np, K_torch, atol=1e-6)


@pytest.mark.parametrize("sigma", SIGMA_GRID)
def test_mmd2_matches_torch(sigma):
    centers_np = _make_centers()
    K_np = gaussian_kernel_matrix_np(centers_np, sigma)
    K_torch = torch.tensor(K_np, dtype=torch.float64)

    for seed in range(5):
        p_np = _make_prob_vector(10, seed=100 + seed)
        q_np = _make_prob_vector(10, seed=200 + seed)

        value_np = mmd2_np(p_np, q_np, K_np)
        value_torch = mmd2(
            torch.tensor(p_np, dtype=torch.float64),
            torch.tensor(q_np, dtype=torch.float64),
            K_torch,
        ).item()

        assert value_np == pytest.approx(value_torch, abs=1e-6)


def test_mmd2_self_comparison_is_zero():
    centers_np = _make_centers()
    K_np = gaussian_kernel_matrix_np(centers_np, sigma=0.1)
    p_np = _make_prob_vector(10, seed=42)
    assert mmd2_np(p_np, p_np, K_np) == pytest.approx(0.0, abs=1e-5)


def test_mmd2_np_is_nonnegative_and_finite():
    centers_np = _make_centers()
    K_np = gaussian_kernel_matrix_np(centers_np, sigma=0.1)
    for seed in range(10):
        p_np = _make_prob_vector(10, seed=seed)
        q_np = _make_prob_vector(10, seed=seed + 1000)
        value = mmd2_np(p_np, q_np, K_np)
        assert np.isfinite(value)
        assert value >= 0


def test_mmd2_grad_matches_finite_difference():
    centers_np = _make_centers()
    K_np = gaussian_kernel_matrix_np(centers_np, sigma=0.1)

    rng = np.random.default_rng(7)
    p = _make_prob_vector(10, seed=1)
    q0 = rng.standard_normal(10)  # need not be a valid probability vector
    dq = rng.standard_normal(10)

    grad = mmd2_grad(q0, p, K_np, dq)

    h = 1e-5
    f_plus = mmd2_np(p, q0 + h * dq, K_np)
    f_minus = mmd2_np(p, q0 - h * dq, K_np)
    finite_diff = (f_plus - f_minus) / (2 * h)

    assert grad == pytest.approx(finite_diff, abs=1e-4)


def test_mmd2_grad_matches_exact_algebraic_derivative():
    """The real exactness proof: mmd2_np(p, q0 + theta*dq, K) is an exactly
    known quadratic function of theta (before the clamp, which is inactive
    here since q0, dq are chosen so the value stays positive near theta=0).
    Expand it algebraically and differentiate at theta=0 by hand, then
    compare against mmd2_grad's closed-form chain-rule output.

    MMD2(theta) = p@K@p + (q0+theta*dq)@K@(q0+theta*dq) - 2*p@K@(q0+theta*dq)
                = p@K@p + q0@K@q0 + 2*theta*(q0@K@dq) + theta^2*(dq@K@dq)
                  - 2*p@K@q0 - 2*theta*(p@K@dq)

    d/dtheta at theta=0 = 2*q0@K@dq - 2*p@K@dq = 2*(q0-p)@K@dq
    """
    centers_np = _make_centers()
    K_np = gaussian_kernel_matrix_np(centers_np, sigma=0.1)

    rng = np.random.default_rng(11)
    p = _make_prob_vector(10, seed=2)
    q0 = rng.standard_normal(10)
    dq = rng.standard_normal(10)

    grad = mmd2_grad(q0, p, K_np, dq)

    exact_derivative_at_zero = 2.0 * (q0 - p) @ K_np @ dq

    assert grad == pytest.approx(exact_derivative_at_zero, abs=1e-9)
