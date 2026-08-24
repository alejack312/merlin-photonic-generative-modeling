import itertools

import numpy as np
import pytest

from merlin_iqp.encoding.iqp_photonic import (
    photonic_iqp_distribution,
    photonic_weight2_iqp_distribution,
    expected_single_qubit_probs,
)
from merlin_iqp.trainability.param_shift import (
    weight1_param_shift_delta,
    weight2_param_shift_delta,
)

TOLERANCE = 1e-9
FD_TOLERANCE = 1e-4
FD_EPS = 1e-4


def _analytic_weight1_derivative(n, thetas, k):
    """Exact closed-form d(dist[bits])/d(thetas[k]) for every bitstring, in
    photonic_iqp_distribution's own '0'/'1' alphabet (0='H', 1='V', per
    fock_to_bitstring). Since expected_single_qubit_probs gives
    P(H)=cos^2(theta), P(V)=sin^2(theta): d/d(theta) cos^2(theta) =
    -sin(2*theta), d/d(theta) sin^2(theta) = +sin(2*theta). The joint
    probability is a product of independent per-qubit marginals (weight-1,
    uncorrelated), so by the product rule only qubit k's own factor is
    differentiated; every other qubit's marginal factor is carried through
    unchanged."""
    marginals = [expected_single_qubit_probs(t) for t in thetas]
    deriv = {}
    for bits in itertools.product("01", repeat=n):
        other_product = 1.0
        for idx, b in enumerate(bits):
            if idx == k:
                continue
            label = "H" if b == "0" else "V"
            other_product *= marginals[idx][label]
        sign = -1.0 if bits[k] == "0" else 1.0
        deriv["".join(bits)] = other_product * sign * np.sin(2.0 * thetas[k])
    return deriv


def _weight2_central_finite_difference(n, i, j, thetas, k, eps=FD_EPS):
    """Independent numerical cross-check: central finite-difference of
    photonic_weight2_iqp_distribution with respect to thetas[k], using the
    same union-of-keys-with-0-default convention weight2_param_shift_delta
    uses. O(eps^2) truncation error at this eps -- callers must not compare
    against this with a tighter atol than the method supports."""
    thetas_plus = list(thetas)
    thetas_plus[k] += eps
    thetas_minus = list(thetas)
    thetas_minus[k] -= eps

    dist_plus, _, _ = photonic_weight2_iqp_distribution(n, i, j, thetas_plus)
    dist_minus, _, _ = photonic_weight2_iqp_distribution(n, i, j, thetas_minus)

    keys = set(dist_plus) | set(dist_minus)
    return {
        x: (dist_plus.get(x, 0.0) - dist_minus.get(x, 0.0)) / (2.0 * eps)
        for x in keys
    }


class TestWeight1ClosedFormExactness:
    """Case 1 (17-01-PLAN.md): weight1_param_shift_delta must equal the
    exact analytic derivative of the weight-1 product-state distribution,
    to atol=1e-9, across multiple n and random theta draws."""

    @pytest.mark.parametrize("n", [1, 2, 3])
    def test_matches_analytic_derivative(self, n):
        rng = np.random.default_rng(1701 + n)
        n_draws = 5
        for _ in range(n_draws):
            thetas = rng.uniform(0.0, 2.0 * np.pi, size=n).tolist()
            for k in range(n):
                delta, residual = weight1_param_shift_delta(n, thetas, k)
                expected = _analytic_weight1_derivative(n, thetas, k)
                assert residual < TOLERANCE
                for bits, expected_val in expected.items():
                    assert delta.get(bits, 0.0) == pytest.approx(
                        expected_val, abs=TOLERANCE
                    ), f"n={n} k={k} bits={bits} thetas={thetas}"


class TestWeight2FiniteDifferenceCrossCheck:
    """Case 2 (17-01-PLAN.md): weight2_param_shift_delta must agree with an
    independent central finite-difference of photonic_weight2_iqp_distribution
    to within the finite-difference method's own error bound (atol=1e-4)."""

    @pytest.mark.parametrize("n", [2, 3])
    def test_matches_finite_difference(self, n):
        i, j = 0, 1
        rng = np.random.default_rng(2718 + n)
        n_draws = 3
        for _ in range(n_draws):
            thetas = rng.uniform(0.0, 2.0 * np.pi, size=n).tolist()
            for k in range(n):
                delta, residual, herald_fail = weight2_param_shift_delta(
                    n, i, j, thetas, k
                )
                fd = _weight2_central_finite_difference(n, i, j, thetas, k)

                assert residual < 1.0  # diagnostic surfaced, sanity-bounded
                assert 0.0 <= herald_fail <= 1.0

                keys = set(delta) | set(fd)
                for bits in keys:
                    assert delta.get(bits, 0.0) == pytest.approx(
                        fd.get(bits, 0.0), abs=FD_TOLERANCE
                    ), f"n={n} k={k} bits={bits} thetas={thetas}"


class TestPiOverTwoShiftPitfallRegression:
    """Case 3 (17-01-PLAN.md): demonstrates -- not just describes -- the
    documented pi/2-shift-divide-by-2 pitfall. This repo's WP(theta,0) =
    exp(i*theta*Z) convention has eigenvalue gap 2, so the textbook
    shift=pi/2 rule lands on sin(2*pi/2)=sin(pi)=0: the raw (unnormalized)
    two-point difference f(theta+pi/2) - f(theta-pi/2) is exactly zero for
    every theta, which would look like a legitimate barren-plateau signal
    but is actually a shift-rule bug. This test deliberately bypasses
    weight1_param_shift_delta (which must never accept pi/2 as a shift) and
    calls photonic_iqp_distribution directly."""

    @pytest.mark.parametrize("theta", [0.3, np.pi / 6, np.pi / 3])
    def test_pi_over_2_shift_produces_zero_delta(self, theta):
        n = 1
        dist_plus, _ = photonic_iqp_distribution(n, [theta + np.pi / 2])
        dist_minus, _ = photonic_iqp_distribution(n, [theta - np.pi / 2])

        keys = set(dist_plus) | set(dist_minus)
        assert keys, "expected at least one output bitstring"
        for bits in keys:
            delta = dist_plus.get(bits, 0.0) - dist_minus.get(bits, 0.0)
            assert delta == pytest.approx(0.0, abs=TOLERANCE), (
                f"theta={theta} bits={bits}: pi/2 shift did not land on the "
                f"expected zero -- pitfall may not reproduce as documented"
            )
