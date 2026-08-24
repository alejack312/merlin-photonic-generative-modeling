import math

import torch

from merlin_iqp.generator.bin_centers import make_bin_centers
from merlin_iqp.generator.data import load_circles_data, compute_p_real
from merlin_iqp.generator.mmd import gaussian_kernel_matrix
from merlin_iqp.generator.train import build_generator, train_step, decreasing_trend_check


def test_train_step_smoke_runs_without_error_and_losses_finite():
    # Build once, matching Pattern 1 (build once, loop many) -- never rebuilt
    # inside the loop below.
    centers = make_bin_centers()
    x_train, _ = load_circles_data()
    p_real = compute_p_real(x_train, centers)
    kernel_matrix = gaussian_kernel_matrix(centers, sigma=0.1)
    quantum_layer = build_generator()
    optimizer = torch.optim.Adam(quantum_layer.parameters(), lr=0.01)

    losses = []
    for _ in range(5):
        loss = train_step(quantum_layer, optimizer, p_real, kernel_matrix, batch_size=4)
        losses.append(loss)

    assert len(losses) == 5
    for loss in losses:
        assert math.isfinite(loss)


def test_decreasing_trend_check_passes_on_monotonically_decreasing_losses():
    losses = [10 - 0.1 * i for i in range(100)]
    result = decreasing_trend_check(losses)
    assert result["passed"] is True
    assert result["slope"] < 0


def test_decreasing_trend_check_fails_on_flat_losses():
    losses = [5.0 for _ in range(100)]
    result = decreasing_trend_check(losses)
    assert result["passed"] is False


def test_decreasing_trend_check_fails_on_increasing_losses():
    losses = [1 + 0.1 * i for i in range(100)]
    result = decreasing_trend_check(losses)
    assert result["passed"] is False
    assert result["slope"] > 0
