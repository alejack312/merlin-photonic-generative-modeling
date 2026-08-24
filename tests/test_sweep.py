import numpy as np
import pytest

from merlin_iqp.trainability import data_dependent_init, target_grid
from merlin_iqp.trainability.sweep import (
    pick_tracked_indices,
    pooled_gradients_for_cell,
    run_gradient_variance_sweep,
)

EXPECTED_STATS_KEYS = {
    "n",
    "generator_scope",
    "init_scheme",
    "n_tracked_params",
    "n_samples",
    "mean",
    "var",
    "std",
    "median",
    "abs_mean",
    "rms",
}


@pytest.mark.parametrize("generator_scope", ["weight1", "mixed"])
@pytest.mark.parametrize("init_scheme", ["small_angle", "uniform"])
def test_sweep_returns_one_dict_per_n_with_expected_keys(generator_scope, init_scheme):
    results = run_gradient_variance_sweep(
        [2, 3], generator_scope, init_scheme, n_draws=3, max_tracked_params=2
    )
    assert len(results) == 2
    for n, result in zip([2, 3], results):
        assert set(result.keys()) == EXPECTED_STATS_KEYS
        assert result["n"] == n
        assert result["generator_scope"] == generator_scope
        assert result["init_scheme"] == init_scheme
        assert result["n_tracked_params"] <= min(2, n)
        assert result["n_samples"] == result["n_tracked_params"] * 3


def test_sweep_is_deterministic():
    r1 = run_gradient_variance_sweep([2], "weight1", "uniform", n_draws=3, max_tracked_params=2)
    r2 = run_gradient_variance_sweep([2], "weight1", "uniform", n_draws=3, max_tracked_params=2)
    assert r1 == r2


@pytest.mark.parametrize("n,max_tracked_params", [(1, 3), (2, 3), (5, 3), (5, 10), (1, 1)])
def test_pick_tracked_indices_bounds(n, max_tracked_params):
    idx = pick_tracked_indices(n, max_tracked_params)
    assert len(idx) <= min(max_tracked_params, n)
    assert all(0 <= i < n for i in idx)
    assert idx == sorted(set(idx))


def test_sweep_mixed_at_n1_raises_clear_error():
    with pytest.raises(ValueError, match="mixed"):
        run_gradient_variance_sweep([1], "mixed", "uniform", n_draws=1)


def test_sweep_empty_n_values_raises():
    with pytest.raises(ValueError):
        run_gradient_variance_sweep([], "weight1", "uniform", n_draws=1)


def test_sweep_unknown_generator_scope_raises():
    with pytest.raises(ValueError):
        run_gradient_variance_sweep([2], "bogus", "uniform", n_draws=1)


def test_pooled_gradients_sigma_default_matches_explicit_old_value():
    """sigma=SIGMA (0.1) explicitly passed must reproduce the same result as
    omitting sigma entirely -- proves the default really equals the old
    hardcoded behavior, not just "close enough" (Pitfall 1)."""
    grads_default, n_tracked_default = pooled_gradients_for_cell(
        2, "weight1", "uniform", draw_start=0, draw_count=3
    )
    grads_explicit, n_tracked_explicit = pooled_gradients_for_cell(
        2, "weight1", "uniform", draw_start=0, draw_count=3, sigma=0.1
    )
    assert n_tracked_default == n_tracked_explicit
    np.testing.assert_array_equal(grads_default, grads_explicit)


def test_pooled_gradients_different_sigma_changes_output():
    """A materially different sigma must actually change the pooled gradients --
    proves sigma is wired into the kernel matrix, not a no-op parameter."""
    grads_low, _ = pooled_gradients_for_cell(
        2, "weight1", "uniform", draw_start=0, draw_count=3, sigma=0.1
    )
    grads_high, _ = pooled_gradients_for_cell(
        2, "weight1", "uniform", draw_start=0, draw_count=3, sigma=5.0
    )
    assert not np.array_equal(grads_low, grads_high)


def test_bin_spacing_matches_hand_verified_table():
    assert target_grid.bin_spacing(2) == pytest.approx(1.2)
    assert target_grid.bin_spacing(6) == pytest.approx(0.1714, abs=1e-3)


def test_pooled_gradients_data_dependent_is_identical_across_draws():
    """init_scheme='data_dependent' has no random component (Plan 17.1-01) --
    every draw of the same (n, generator_scope) cell must produce IDENTICAL
    pooled gradients, proven directly rather than assumed."""
    grads, n_tracked = pooled_gradients_for_cell(
        3, "weight1", "data_dependent", draw_start=0, draw_count=5, max_tracked_params=2
    )
    assert n_tracked >= 1
    per_draw = grads.reshape(5, n_tracked)
    for row in per_draw[1:]:
        np.testing.assert_array_equal(row, per_draw[0])


def test_pooled_gradients_mixed_data_dependent_overrides_pair_indices():
    """For generator_scope='mixed', weight2_pair's two qubits (i, j) must
    receive weight2_data_dependent_theta's covariance-based value in place of
    weight1_data_dependent_theta's per-qubit arcsin(sqrt(mean)) value --
    proves the documented mixed-scope override actually happens, not just
    that SOME data-dependent scheme runs."""
    from merlin_iqp.encoding.iqp_photonic import photonic_weight2_iqp_distribution
    from merlin_iqp.trainability import mmd_exact, param_shift

    n = 3
    weight2_pair = (0, 1)
    i, j = weight2_pair
    _centers, p_real, bin_index_fn = target_grid.make_target_grid(n)

    plain_thetas = data_dependent_init.weight1_data_dependent_theta(p_real, n)
    pair_theta = data_dependent_init.weight2_data_dependent_theta(p_real, i, j, n, 1.0)
    overridden_thetas = list(plain_thetas)
    overridden_thetas[i] = pair_theta
    overridden_thetas[j] = pair_theta

    # The override must actually change something, or this test proves nothing.
    assert overridden_thetas != plain_thetas

    actual_grads, _n_tracked = pooled_gradients_for_cell(
        n,
        "mixed",
        "data_dependent",
        draw_start=0,
        draw_count=1,
        max_tracked_params=2,
        weight2_pair=weight2_pair,
        scale_factor=1.0,
    )

    K = mmd_exact.gaussian_kernel_matrix_np(_centers, 0.1)
    tracked = pick_tracked_indices(n, 2)

    def grads_for_thetas(thetas):
        q_dist, _r, _h = photonic_weight2_iqp_distribution(n, i, j, thetas)
        q_vec = target_grid.bitstring_dict_to_vector(q_dist, n, bin_index_fn)
        out = []
        for k in tracked:
            delta, _rd, _hd = param_shift.weight2_param_shift_delta(n, i, j, thetas, k)
            dq = target_grid.bitstring_dict_to_vector(delta, n, bin_index_fn)
            out.append(mmd_exact.mmd2_grad(q_vec, p_real, K, dq))
        return np.array(out)

    expected_with_override = grads_for_thetas(overridden_thetas)
    expected_without_override = grads_for_thetas(plain_thetas)

    np.testing.assert_array_equal(actual_grads, expected_with_override)
    assert not np.array_equal(actual_grads, expected_without_override)


def test_sweep_data_dependent_weight1_returns_expected_shape():
    """run_gradient_variance_sweep with init_scheme='data_dependent' still
    returns the standard per-n stats-dict shape."""
    results = run_gradient_variance_sweep(
        [2, 3], "weight1", "data_dependent", n_draws=1, max_tracked_params=2
    )
    assert len(results) == 2
    for n, result in zip([2, 3], results):
        assert set(result.keys()) == EXPECTED_STATS_KEYS
        assert result["n"] == n
        assert result["generator_scope"] == "weight1"
        assert result["init_scheme"] == "data_dependent"
