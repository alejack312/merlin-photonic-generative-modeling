"""TDD tests for trainability/curve_fit.py (Phase 17 Plan 04, TRAIN-02).

Proves fit_and_compare correctly distinguishes exponential decay (the
barren-plateau signature) from polynomial/power-law decay on SYNTHETIC
data with a KNOWN ground-truth model, before it is ever run against the
real gradient-variance-vs-n data Plan 17-06/17-07 produce.
"""

import numpy as np
import pytest

from merlin_iqp.trainability.curve_fit import exp_model, poly_model, aic, fit_and_compare

# Fixed seed for all synthetic-noise generation -- deterministic tests.
SEED = 1710

# Ground-truth parameters shared by both synthetic cases.
A_TRUE, B_TRUE, C_TRUE = 2.0, 0.8, 0.001

NS = np.array([2, 3, 4, 5, 6, 7, 8], dtype=float)


def _make_exp_data():
    rng = np.random.default_rng(SEED)
    clean = exp_model(NS, A_TRUE, B_TRUE, C_TRUE)
    noise_std = 0.01 * (clean.max() - clean.min())
    noisy = clean + rng.normal(0.0, noise_std, size=clean.shape)
    return NS, noisy


def _make_poly_data():
    rng = np.random.default_rng(SEED)
    clean = poly_model(NS, A_TRUE, B_TRUE, C_TRUE)
    noise_std = 0.01 * (clean.max() - clean.min())
    noisy = clean + rng.normal(0.0, noise_std, size=clean.shape)
    return NS, noisy


def test_exponential_ground_truth_recovers_exp_verdict():
    ns, ys = _make_exp_data()
    result = fit_and_compare(ns, ys)

    assert result["verdict"] == "exp"

    a_fit, b_fit, c_fit = result["exp"]["params"]
    assert np.isclose(a_fit, A_TRUE, atol=0.5)
    assert np.isclose(b_fit, B_TRUE, atol=0.5)
    assert np.isclose(c_fit, C_TRUE, atol=0.5)


def test_polynomial_ground_truth_recovers_poly_verdict():
    ns, ys = _make_poly_data()
    result = fit_and_compare(ns, ys)

    assert result["verdict"] == "poly"

    a_fit, b_fit, c_fit = result["poly"]["params"]
    assert np.isclose(a_fit, A_TRUE, atol=0.5)
    assert np.isclose(b_fit, B_TRUE, atol=0.5)
    assert np.isclose(c_fit, C_TRUE, atol=0.5)


@pytest.mark.parametrize("data_fn", [_make_exp_data, _make_poly_data])
def test_both_models_report_both_metrics(data_fn):
    ns, ys = data_fn()
    result = fit_and_compare(ns, ys)

    for model_name in ("exp", "poly"):
        assert "r2" in result[model_name]
        assert "aic" in result[model_name]
        assert np.isfinite(result[model_name]["r2"])
        assert np.isfinite(result[model_name]["aic"])


def test_aic_formula_matches_definition():
    residuals = np.array([0.1, -0.2, 0.05, 0.0, -0.1])
    k_params = 3
    n_obs = len(residuals)
    rss = np.sum(residuals ** 2)
    expected = n_obs * np.log(rss / n_obs) + 2 * k_params
    assert np.isclose(aic(residuals, k_params), expected)


def test_verdict_key_is_one_of_expected_values():
    ns, ys = _make_exp_data()
    result = fit_and_compare(ns, ys)
    assert result["verdict"] in ("exp", "poly", "inconclusive")


def test_convergence_failure_is_surfaced_not_swallowed():
    """Degenerate input (fewer points than free params) must not crash the
    whole analysis -- fit_and_compare should surface converged=False and
    NaN metrics for the failing model(s), per this plan's success criteria.
    """
    ns = np.array([2.0, 3.0])
    ys = np.array([1e10, -1e10])

    result = fit_and_compare(ns, ys)

    assert result["exp"]["converged"] is False
    assert result["poly"]["converged"] is False
    assert result["exp"]["params"] is None
    assert result["poly"]["params"] is None
    assert np.isnan(result["exp"]["r2"])
    assert np.isnan(result["exp"]["aic"])
    assert result["verdict"] == "inconclusive"
