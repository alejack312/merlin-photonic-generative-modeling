import numpy as np
import pytest

from trainability.sweep import pick_tracked_indices, run_gradient_variance_sweep

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
