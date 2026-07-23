import pytest
import torch
import merlin as ML

from generator.mmd import gaussian_kernel_matrix, mmd2, SIGMA_GRID
from generator.bin_centers import make_bin_centers
from generator.data import load_circles_data, compute_p_real
from generator.noise import sample_latent

CENTERS = make_bin_centers()
_X_TRAIN, _ = load_circles_data()
P_REAL = compute_p_real(_X_TRAIN, CENTERS)


@pytest.mark.parametrize("sigma", SIGMA_GRID)
def test_kernel_matrix_sanity(sigma):
    K = gaussian_kernel_matrix(CENTERS, sigma)
    assert K.shape == (400, 400)
    # atol=1e-4, not the default: torch.cdist(centers, centers) has a tiny
    # inherent float32 asymmetry (~1e-6) that gets amplified by /(2*sigma^2)
    # and exp() at small sigma — a known cdist numerical quirk, not a bug here.
    assert torch.allclose(K, K.T, atol=1e-4)
    # non-strict [0,1]: at small sigma, far-apart pairs underflow to exact 0.0
    # in float32 — expected, not a bug (see 02-04-PLAN.md).
    assert (K >= 0).all() and (K <= 1).all()
    # atol=1e-3: cdist's self-distance isn't exactly 0 (float32 cancellation in
    # its internal ||a||^2+||b||^2-2ab formula), amplified the same way at small
    # sigma (measured diagonal deviation ~3e-4 at sigma=0.02).
    assert torch.allclose(torch.diagonal(K), torch.ones(400), atol=1e-3)


@pytest.mark.parametrize("sigma", SIGMA_GRID)
def test_mmd2_finite_and_nonnegative(sigma):
    K = gaussian_kernel_matrix(CENTERS, sigma)
    for _ in range(50):
        p = torch.rand(400)
        p = p / p.sum()
        q = torch.rand(400)
        q = q / q.sum()
        value = mmd2(p, q, K)
        assert torch.isfinite(value)
        assert value >= 0


@pytest.mark.parametrize("sigma", SIGMA_GRID)
def test_mmd2_self_comparison_is_zero(sigma):
    # fundamental MMD property: a distribution compared against itself is 0 —
    # catches a broken kernel/formula before it reaches Phase 3.
    K = gaussian_kernel_matrix(CENTERS, sigma)
    assert mmd2(P_REAL, P_REAL, K).item() == pytest.approx(0.0, abs=1e-5)


def test_mmd2_gradient_reaches_quantum_layer():
    K = gaussian_kernel_matrix(CENTERS, sigma=0.1)

    # one quantum_layer instance, reused for both the forward pass and the
    # parameter check below — a second, freshly-constructed layer would never
    # have gradients, since it was never part of this computation graph.
    quantum_layer = ML.QuantumLayer.simple(input_size=10, output_size=400)
    q = quantum_layer(sample_latent(1))[0]

    loss = mmd2(P_REAL, q, K)
    loss.backward()

    found_grad = False
    for param in quantum_layer.parameters():
        if param.grad is not None:
            assert torch.isfinite(param.grad).all()
            found_grad = True
    assert found_grad
