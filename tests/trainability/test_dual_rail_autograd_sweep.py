"""Tests for trainability/dual_rail_autograd_sweep.py -- the native-autograd,
dual-rail analogue of trainability/sweep.py's parameter-shift-based
gradient-variance sweep.

Ground truth is a finite-difference check on the EXACT SAME forward
computation path (same MerLin layer, same bin-mapping matrix M, same K
matrix) -- not a cross-implementation comparison, which would conflate
float32 noise from two independently-noisy code paths with a real
correctness bug (confirmed live during development: cross-implementation
comparison showed ~1e-3 diff, same-path finite-difference showed ~1e-4,
both consistent with float32 truncation, not a bug)."""

import numpy as np
import pytest
import torch

from merlin_iqp.encoding.dual_rail import make_weight1_quantum_layer, make_weight2_quantum_layer
from merlin_iqp.trainability import mmd_exact, target_grid
from merlin_iqp.trainability.dual_rail_autograd_sweep import (
    _build_bin_mapping,
    pooled_native_gradients_for_cell,
)
from merlin_iqp.trainability.rng import get_rng
from merlin_iqp.trainability.sweep import SIGMA, sample_thetas


def _same_path_finite_diff_weight1(n, thetas, eps=1e-3):
    layer = make_weight1_quantum_layer(n)
    theta_tensor = dict(layer.named_parameters())["theta"]
    centers, p_real_np, bin_index_fn = target_grid.make_target_grid(n)
    M = _build_bin_mapping(layer.output_keys, n, bin_index_fn, 2**n)
    K_mat = torch.tensor(mmd_exact.gaussian_kernel_matrix_np(centers, SIGMA), dtype=torch.float32)
    p_real = torch.tensor(p_real_np, dtype=torch.float32)

    def forward_loss(theta_values):
        with torch.no_grad():
            theta_tensor.copy_(torch.tensor(theta_values, dtype=theta_tensor.dtype))
        out_flat = layer().flatten()
        q_vec = M @ out_flat
        loss = q_vec @ K_mat @ q_vec - 2.0 * (p_real @ K_mat @ q_vec)
        return loss.item()

    grads = []
    for k in range(n):
        plus, minus = list(thetas), list(thetas)
        plus[k] += eps
        minus[k] -= eps
        grads.append((forward_loss(plus) - forward_loss(minus)) / (2 * eps))
    return np.array(grads)


@pytest.mark.parametrize("n", [2, 3])
def test_weight1_autograd_matches_same_path_finite_diff(n):
    draw_rng = get_rng(170917, "weight1", "small_angle", n, 0)
    thetas = sample_thetas(draw_rng, n, "small_angle")

    grads, n_tracked = pooled_native_gradients_for_cell(
        n, "weight1", "small_angle", draw_start=0, draw_count=1
    )
    fd_grads = _same_path_finite_diff_weight1(n, thetas)

    assert n_tracked == n
    assert len(grads) == n
    assert grads == pytest.approx(fd_grads, abs=5e-4)


def test_weight1_pooling_shape():
    """draw_count draws x n params, flat pooled array -- matches
    trainability.sweep.pooled_gradients_for_cell's pooling convention
    (draws AND all n tracked parameters pooled into one flat array)."""
    n, draw_count = 3, 4
    grads, n_tracked = pooled_native_gradients_for_cell(
        n, "weight1", "uniform", draw_start=0, draw_count=draw_count
    )
    assert n_tracked == n
    assert len(grads) == draw_count * n
    assert np.all(np.isfinite(grads))


def test_mixed_requires_n_at_least_2():
    with pytest.raises(ValueError, match="n >= 2"):
        pooled_native_gradients_for_cell(1, "mixed", "small_angle", draw_start=0, draw_count=1)


def test_mixed_pooling_finite_and_correct_shape():
    n, draw_count = 2, 3
    grads, n_tracked = pooled_native_gradients_for_cell(
        n, "mixed", "small_angle", draw_start=0, draw_count=draw_count, weight2_pair=(0, 1)
    )
    assert n_tracked == n
    assert len(grads) == draw_count * n
    assert np.all(np.isfinite(grads))


def test_draw_chunking_matches_single_shot():
    """Draws [0,2) computed in two separate 1-draw calls must be bit-identical
    to draws [0,2) computed in one 2-draw call -- deterministic RNG substreams,
    same guarantee trainability/sweep.py's chunking relies on."""
    n = 2
    chunk_a, _ = pooled_native_gradients_for_cell(n, "weight1", "small_angle", 0, 1)
    chunk_b, _ = pooled_native_gradients_for_cell(n, "weight1", "small_angle", 1, 1)
    single_shot, _ = pooled_native_gradients_for_cell(n, "weight1", "small_angle", 0, 2)
    combined = np.concatenate([chunk_a, chunk_b])
    assert combined == pytest.approx(single_shot, abs=0.0)
