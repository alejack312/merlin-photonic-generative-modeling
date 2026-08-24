"""TDD tests for trainability/data_dependent_init.py (TRAIN-10).

Proves two things independently: (1) the bit-ordering convention `bit_k`
uses is the exact inverse of trainability/target_grid.py's
`bin_index_fn(bitstring) = int(bitstring, 2)` for every qubit position, not
just position 0 or n-1 (17.1-RESEARCH.md Pitfall 3); (2) every formula
matches a hand-computed worked example, not merely "runs without crashing".

All worked-example expected values below were computed by hand (see the
plan's <behavior> section), not derived by running the implementation.
"""

import numpy as np
import pytest

from merlin_iqp.trainability.data_dependent_init import (
    bit_k,
    empirical_mean_bit,
    empirical_pm1_covariance,
    weight1_data_dependent_theta,
    weight2_data_dependent_theta,
)


# --- Case 1: Pitfall-3 bit-ordering spot-check (mandatory) ---


@pytest.mark.parametrize("n", [2, 3, 4])
def test_bit_k_is_inverse_of_bin_index_fn(n):
    """For every qubit position k in [0, n), a bitstring with a single '1' at
    position k must decode back to bit_k(idx, k, n) == 1 and 0 everywhere
    else -- proving bit_k is int(bitstring, 2)'s exact inverse at every
    position, not just the endpoints."""
    for k in range(n):
        bitstring = "".join("1" if i == k else "0" for i in range(n))
        idx = int(bitstring, 2)
        assert bit_k(idx, k, n) == 1
        for kk in range(n):
            if kk != k:
                assert bit_k(idx, kk, n) == 0


# --- Case 2: empirical_mean_bit worked example ---


def test_empirical_mean_bit_worked_example():
    p_real = np.array([0.1, 0.2, 0.3, 0.4])  # n=2: "00","01","10","11"
    assert empirical_mean_bit(p_real, 0, 2) == pytest.approx(0.7)
    assert empirical_mean_bit(p_real, 1, 2) == pytest.approx(0.6)


# --- Case 3: weight1_data_dependent_theta worked example ---


def test_weight1_data_dependent_theta_worked_example():
    p_real = np.array([0.1, 0.2, 0.3, 0.4])
    result = weight1_data_dependent_theta(p_real, 2)
    assert result == pytest.approx([np.arcsin(np.sqrt(0.7)), np.arcsin(np.sqrt(0.6))])


# --- Case 4: empirical_pm1_covariance worked example ---


def test_empirical_pm1_covariance_worked_example():
    p_real = np.array([0.1, 0.2, 0.3, 0.4])
    assert empirical_pm1_covariance(p_real, 0, 1, 2) == pytest.approx(-0.08)


# --- Case 5: weight2_data_dependent_theta worked example (scale_factor linearity) ---


def test_weight2_data_dependent_theta_worked_example():
    p_real = np.array([0.1, 0.2, 0.3, 0.4])
    assert weight2_data_dependent_theta(p_real, 0, 1, 2, scale_factor=1.0) == pytest.approx(-0.08)
    assert weight2_data_dependent_theta(p_real, 0, 1, 2, scale_factor=2.0) == pytest.approx(-0.16)


# --- Case 6: domain safety at arcsin boundary ---


def test_weight1_data_dependent_theta_domain_safety_at_boundary():
    """A p_real concentrating all mass on one bin gives bit-marginals of
    exactly 0.0 or 1.0 for various k -- both are valid probabilities, so
    arcsin(sqrt(...)) must never raise (no clipping/guard needed)."""
    n = 2
    p_real = np.zeros(4)
    p_real[0] = 1.0  # bin index 0 == "00": both bits are 0 for every draw
    result = weight1_data_dependent_theta(p_real, n)
    assert result == pytest.approx([np.arcsin(np.sqrt(0.0)), np.arcsin(np.sqrt(0.0))])

    p_real2 = np.zeros(4)
    p_real2[3] = 1.0  # bin index 3 == "11": both bits are 1 for every draw
    result2 = weight1_data_dependent_theta(p_real2, n)
    assert result2 == pytest.approx([np.arcsin(np.sqrt(1.0)), np.arcsin(np.sqrt(1.0))])
