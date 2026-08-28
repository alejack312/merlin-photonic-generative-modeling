import numpy as np
import pytest

from scripts.v2_encoding.heralded_cz_derisking import (
    COMPUTATIONAL_BASIS,
    EXPECTED_HERALD_SUCCESS,
    measure_herald_success,
    measure_herald_success_superposition,
    build_plus_plus_terms,
    build_plus_zero_terms,
    build_analyzer,
    check_no_leakage,
    check_post_select_fn_empty,
    measure_cz_phase,
    check_phase_sign,
)
from perceval.components.core_catalog.heralded_cz import HeraldedCzItem


TOLERANCE = 1e-9


@pytest.mark.parametrize("ctrl,data,state", COMPUTATIONAL_BASIS)
def test_herald_success_uniform_computational_basis(ctrl, data, state):
    """heralded_cz's herald-success probability is exactly 2/27, with
    physical_perf==1.0 (no photon loss in the unitary itself), uniform
    across all 4 computational-basis dual-rail inputs."""
    res = measure_herald_success(state)
    assert np.isclose(res["global_perf"], EXPECTED_HERALD_SUCCESS, atol=TOLERANCE)
    assert np.isclose(res["physical_perf"], 1.0, atol=TOLERANCE)
    assert np.isclose(res["logical_perf"], EXPECTED_HERALD_SUCCESS, atol=TOLERANCE)


def test_herald_success_uniform_superposition_spotchecks():
    """Herald-success probability stays at 2/27 for superposition inputs
    too (|+>|+> and the asymmetric |+>|0>), not just the computational
    basis -- spot-checked, not exhaustively."""
    pp_res = measure_herald_success_superposition(build_plus_plus_terms())
    assert np.isclose(pp_res["global_perf"], EXPECTED_HERALD_SUCCESS, atol=TOLERANCE)

    pz_res = measure_herald_success_superposition(build_plus_zero_terms())
    assert np.isclose(pz_res["global_perf"], EXPECTED_HERALD_SUCCESS, atol=TOLERANCE)


@pytest.mark.parametrize("ctrl,data,state", COMPUTATIONAL_BASIS)
def test_cz_phase_sign(ctrl, data, state):
    """The complex amplitude on |1,1> is negative; |0,0>, |0,1>, |1,0>
    are positive -- matching CZ's diag(1,1,1,-1) truth table -- and
    |amplitude|^2 matches 2/27 in all four cases."""
    amplitudes = measure_cz_phase()
    amp = amplitudes[(ctrl, data)]
    assert np.isclose(abs(amp) ** 2, EXPECTED_HERALD_SUCCESS, atol=TOLERANCE)
    if ctrl == "1" and data == "1":
        assert amp.real < 0
    else:
        assert amp.real > 0


def test_phase_check_passes_for_all_combos():
    """Full phase-sign/magnitude check (all 4 combos at once), matching
    the script's own assertion helper."""
    amplitudes = measure_cz_phase()
    assert check_phase_sign(amplitudes)


def test_no_leakage_to_invalid_outputs():
    """Analyzer's truth-table columns for invalid/bunched outputs are
    all exactly 0 for each of the 4 computational-basis inputs -- the
    'no leakage' claim, checked explicitly rather than eyeballed."""
    an = build_analyzer()
    assert check_no_leakage(an)


def test_post_select_fn_is_empty():
    """heralded_cz's Experiment has no PostSelect expression beyond its
    two add_herald() calls -- logical_perf is pure herald condition, not
    bundled with a second hidden filter. Asserted explicitly so a future
    perceval-quandela version change that adds a post-select expression
    fails loudly instead of silently invalidating this claim."""
    assert check_post_select_fn_empty()

    # Cross-check directly against the source object too, matching
    # Open Question 2's recommendation in 10-RESEARCH.md.
    exp = HeraldedCzItem().build_experiment()
    assert not str(exp.post_select_fn).strip()
