"""Tests for hardness/baselines.py (Phase 18, Plan 18-04): the two
classically-easy comparison distributions (uniform, product-of-marginals)
and the BMS anticoncentration parameter alpha(dist, n), verified against
known closed-form values and a hand-computed worked example."""

import itertools

import pytest

from hardness.baselines import (
    anticoncentration_alpha,
    product_of_marginals_baseline,
    uniform_baseline,
)
from iqp_photonic_encoding import total_variation_distance


@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_uniform_baseline_keys_and_values(n):
    dist = uniform_baseline(n)
    expected_keys = {"".join(b) for b in itertools.product("01", repeat=n)}
    assert set(dist.keys()) == expected_keys
    assert len(dist) == 2**n
    for v in dist.values():
        assert v == 2**-n


@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_uniform_baseline_normalizes(n):
    dist = uniform_baseline(n)
    assert sum(dist.values()) == pytest.approx(1.0, abs=1e-12)


@pytest.mark.parametrize("n", [1, 2, 3, 4])
def test_anticoncentration_alpha_uniform(n):
    dist = uniform_baseline(n)
    alpha = anticoncentration_alpha(dist, n)
    assert alpha == pytest.approx(1.0, abs=1e-9)


@pytest.mark.parametrize("n", [1, 2, 3])
def test_anticoncentration_alpha_delta(n):
    dist = {"0" * n: 1.0}
    alpha = anticoncentration_alpha(dist, n)
    assert alpha == pytest.approx(2**n, abs=1e-9)


@pytest.mark.parametrize("n", [2, 3, 4])
@pytest.mark.parametrize("surviving_mass", [0.5, 0.1, 1e-3, 1e-8])
def test_anticoncentration_alpha_is_scale_invariant(n, surviving_mass):
    """alpha is a SHAPE statistic: uniformly scaling a distribution's mass
    down (as uniform photon loss does) must not change it.

    Regression test for the Phase 18 defect corrected 2026-08-20: the loss
    sweep called this on the raw sub-normalized lossy distribution, so the
    reported alpha decayed as exactly eta**(2n) -- a survival-probability
    artifact misreported as an anticoncentration finding. Against the
    pre-fix implementation this test fails by a factor of surviving_mass**2.
    """
    dist = uniform_baseline(n)
    # Perturb off-uniform so we are not sitting exactly on the alpha=1 floor.
    keys = sorted(dist)
    dist[keys[0]] *= 3.0
    total = sum(dist.values())
    normalized = {k: v / total for k, v in dist.items()}
    scaled = {k: v * surviving_mass for k, v in normalized.items()}

    assert anticoncentration_alpha(scaled, n) == pytest.approx(
        anticoncentration_alpha(normalized, n), rel=1e-12
    )


@pytest.mark.parametrize("n", [2, 3, 4])
@pytest.mark.parametrize("surviving_mass", [1.0, 0.5, 1e-6])
def test_anticoncentration_alpha_respects_bms_floor(n, surviving_mass):
    """BMS's alpha has a hard floor of 1.0 (equality iff uniform), for any
    input mass. 33 of 56 shipped Phase 18 rows violated this before the fix."""
    dist = {k: v * surviving_mass for k, v in uniform_baseline(n).items()}
    assert anticoncentration_alpha(dist, n) >= 1.0 - 1e-12


def test_anticoncentration_alpha_rejects_zero_mass():
    with pytest.raises(ValueError, match="positive total mass"):
        anticoncentration_alpha({"00": 0.0, "01": 0.0}, 2)


def test_product_of_marginals_hand_computed_example():
    reference_dist = {"00": 0.5, "01": 0.3, "10": 0.1, "11": 0.1}
    # P(bit_0='1') = mass where bits[0]=='1' -> "10","11" = 0.1+0.1 = 0.20
    # P(bit_1='1') = mass where bits[1]=='1' -> "01","11" = 0.3+0.1 = 0.40
    expected = {
        "00": 0.8 * 0.6,  # (1-0.2)*(1-0.4) = 0.48
        "01": 0.8 * 0.4,  # (1-0.2)*0.4 = 0.32
        "10": 0.2 * 0.6,  # 0.2*(1-0.4) = 0.12
        "11": 0.2 * 0.4,  # 0.2*0.4 = 0.08
    }
    result = product_of_marginals_baseline(reference_dist, 2)
    assert set(result.keys()) == set(expected.keys())
    for k, v in expected.items():
        assert result[k] == pytest.approx(v, abs=1e-9)
    assert sum(result.values()) == pytest.approx(1.0, abs=1e-9)


def test_product_of_marginals_handles_unnormalized_reference():
    # reference_dist may not sum to 1.0 (lossy/residual-bearing sweep output)
    # -- caller's responsibility, but the function must not crash or silently
    # renormalize; marginals are computed only over present keys' mass.
    reference_dist = {"00": 0.4, "11": 0.1}  # sums to 0.5, not 1.0
    result = product_of_marginals_baseline(reference_dist, 2)
    assert set(result.keys()) == {"00", "01", "10", "11"}
    # P(bit_0='1') = 0.1 (from "11"), P(bit_1='1') = 0.1 (from "11")
    assert result["00"] == pytest.approx(0.9 * 0.9, abs=1e-9)
    assert result["11"] == pytest.approx(0.1 * 0.1, abs=1e-9)


def test_tvd_wiring_uniform_vs_itself_is_zero():
    n = 3
    dist = uniform_baseline(n)
    assert total_variation_distance(dist, dist) == pytest.approx(0.0, abs=1e-12)


def test_tvd_wiring_uniform_vs_delta():
    dist_a = uniform_baseline(2)
    dist_b = {"00": 1.0}
    # 0.5 * (|0.25-1.0| + 3*|0.25-0.0|) = 0.5 * (0.75 + 0.75) = 0.75
    tvd = total_variation_distance(dist_a, dist_b)
    assert tvd == pytest.approx(0.75, abs=1e-9)
