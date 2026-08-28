import numpy as np
import pytest

from scripts.v3_arb_gate.cp_gate_derisking import (
    NON_TRIVIAL_ALPHAS,
    BOUNDARY_ALPHA,
    EXPECTED_BOUNDARY_MAGNITUDE_SQ,
    measure_cp_amplitudes,
    check_phase_matches_alpha,
    check_uniform_magnitude,
    check_boundary_magnitude,
    check_boundary_sign,
)


TOLERANCE = 1e-9
PHASE_TOLERANCE = 1e-6


@pytest.mark.parametrize("alpha", NON_TRIVIAL_ALPHAS)
def test_cp_phase_matches_e_i_alpha(alpha):
    """CP(alpha) = diag(1,1,1,e^{i*alpha}): amp(1,1)/amp(0,0) matches
    e^{i*alpha} to floating-point precision, at each of the 3 non-trivial
    alpha values (pi/6, pi/3, 2*pi/5)."""
    amplitudes = measure_cp_amplitudes(alpha)
    assert check_phase_matches_alpha(amplitudes, alpha)


@pytest.mark.parametrize("alpha", NON_TRIVIAL_ALPHAS + [BOUNDARY_ALPHA])
def test_cp_amplitude_uniform_magnitude_per_alpha(alpha):
    """CP(alpha) is a genuine phase-only gate: |amplitude|^2 is identical
    across all 4 computational-basis combos for a given alpha, including
    the alpha=pi boundary."""
    amplitudes = measure_cp_amplitudes(alpha)
    assert check_uniform_magnitude(amplitudes)


def test_cp_boundary_alpha_pi_matches_1_9_and_negative_sign():
    """At alpha=pi (NOT alpha=pi/4 -- per 15-CONTEXT.md's owner-confirmed
    correction, CP's own dial and the Z_iZ_j generator angle theta are
    related by alpha=4*theta): |amplitude|^2 == 1/9 (the post-selected-
    construction literature figure, independently confirmed for this
    exact gate) and the sign pattern matches heralded_cz's
    diag(1,1,1,-1) -- negative only on ctrl='1', data='1'."""
    amplitudes = measure_cp_amplitudes(BOUNDARY_ALPHA)

    for amp in amplitudes.values():
        assert np.isclose(abs(amp) ** 2, EXPECTED_BOUNDARY_MAGNITUDE_SQ, atol=TOLERANCE)

    assert check_boundary_magnitude(amplitudes)
    assert check_boundary_sign(amplitudes)

    for (ctrl, data), amp in amplitudes.items():
        if ctrl == "1" and data == "1":
            assert amp.real < 0
        else:
            assert amp.real > 0
