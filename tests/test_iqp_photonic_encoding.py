import sys
import os
import hashlib

import numpy as np
import pytest
import perceval as pcvl
from perceval.components.core_catalog.heralded_cz import HeraldedCzItem
from perceval.simulators import Simulator
from perceval.backends import SLOSBackend

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from iqp_photonic_encoding import (
    build_state_prep_circuit,
    build_diagonal_layer_circuit,
    build_conjugation_circuit,
    build_readout_circuit,
    build_full_circuit,
    build_cz_insertion,
    build_weight2_processor,
    _build_cz_insertion_core,
    build_cp_insertion,
    _build_cp_insertion_core,
    run_full_circuit,
    run_readout,
    all_h_input,
    expected_single_qubit_probs,
    expected_joint_distribution,
    basic_state_to_bitstring,
    bitstring_to_fock,
    fock_to_bitstring,
    exact_qubit_iqp_distribution,
    photonic_iqp_distribution,
    total_variation_distance,
    photonic_weight2_iqp_distribution,
    photonic_cp_iqp_distribution,
)

TOLERANCE = 1e-9
PHASE_TOLERANCE = 1e-6

# This module's own dual-rail convention, matching what a bare PBS
# deterministically produces for a pure H/V polarization input (Plan 09-02,
# confirmed empirically): H = '0' -> (0,1), V = '1' -> (1,0). This is the
# mirror image of heralded_cz_derisking.py's own DUAL_RAIL (which encodes
# heralded_cz's internal Encoding.DUAL_RAIL standard, '0' -> (1,0)) --
# exactly the convention mismatch build_cz_insertion's internal PERM([1,0])
# adapter corrects for (11-RESEARCH.md Pitfall 1).
MODULE_DUAL_RAIL = {"0": (0, 1), "1": (1, 0)}

EXPECTED_CZ_MAGNITUDE_SQ = 2 / 27  # Phase 10's confirmed heralded_cz herald-success probability


def _cz_core_simulator_and_herald_counts():
    """Simulator over build_cz_insertion's own dual-rail core (PERM ->
    heralded_cz -> PERM, no PBS -- Perceval's SLOSBackend cannot process
    circuits containing PBS, `Circuit.requires_polarization`, confirmed
    empirically), plus the herald ancilla photon counts read from
    HeraldedCzItem().build_experiment().in_heralds (not hardcoded, matching
    heralded_cz_derisking.py's measure_cz_phase pattern)."""
    circuit = _build_cz_insertion_core()
    herald_spec = HeraldedCzItem().build_experiment().in_heralds
    herald_counts = [herald_spec[4], herald_spec[5]]
    sim = Simulator(SLOSBackend())
    sim.set_circuit(circuit)
    return sim, herald_counts


def _dual_rail_state(i_bit, j_bit, herald_counts):
    im, jm = MODULE_DUAL_RAIL[i_bit], MODULE_DUAL_RAIL[j_bit]
    return pcvl.BasicState(list(im) + list(jm) + herald_counts)


def _run_and_collect(circuit, input_state):
    processor = pcvl.Processor("SLOS", circuit)
    analyzer = pcvl.algorithm.Analyzer(processor, [input_state], "*")
    analyzer.compute()
    return {
        str(state): complex(prob).real
        for state, prob in zip(analyzer.output_states_list, analyzer.distribution[0])
    }


def test_state_prep_gives_50_50_split():
    """|+> state prep (HWP(pi/8) on |H>), read out via PBS, must split 50/50
    -- the photonic analogue of qubit-side H|0> = |+>."""
    n = 1
    circuit = pcvl.Circuit(2 * n)
    circuit.add(0, build_state_prep_circuit(n))
    circuit.add(0, build_readout_circuit(n))
    dist = _run_and_collect(circuit, all_h_input(n))
    p_h = dist.get(str(pcvl.BasicState([0, 1])), 0.0)
    p_v = dist.get(str(pcvl.BasicState([1, 0])), 0.0)
    assert np.isclose(p_h, 0.5, atol=TOLERANCE)
    assert np.isclose(p_v, 0.5, atol=TOLERANCE)


def test_diagonal_layer_is_identity_at_theta_zero():
    """WP(0, 0) is the identity -- a zero-angle generator must leave state
    prep's 50/50 split unchanged."""
    n = 1
    circuit = pcvl.Circuit(2 * n)
    circuit.add(0, build_state_prep_circuit(n))
    circuit.add(0, build_diagonal_layer_circuit(n, [0.0]))
    circuit.add(0, build_readout_circuit(n))
    dist = _run_and_collect(circuit, all_h_input(n))
    p_h = dist.get(str(pcvl.BasicState([0, 1])), 0.0)
    p_v = dist.get(str(pcvl.BasicState([1, 0])), 0.0)
    assert np.isclose(p_h, 0.5, atol=TOLERANCE)
    assert np.isclose(p_v, 0.5, atol=TOLERANCE)


@pytest.mark.parametrize("theta", [0.0, 0.3, np.pi / 6, np.pi / 4, np.pi / 2, np.pi])
def test_full_pipeline_single_qubit_matches_closed_form(theta):
    """Full ENC-01 pipeline (prep -> diagonal(theta) -> conjugation -> readout)
    for one qubit matches the empirically-confirmed closed form P(H)=cos^2(theta),
    P(V)=sin^2(theta) -- H=(0,1), V=(1,0), verified against a bare PBS with
    pure H/V input (Plan 09-02)."""
    n = 1
    _, dist = run_full_circuit(n, [theta])
    p_h = dist.get(str(pcvl.BasicState([0, 1])), 0.0)
    p_v = dist.get(str(pcvl.BasicState([1, 0])), 0.0)
    expected = expected_single_qubit_probs(theta)
    assert np.isclose(p_h, expected["H"], atol=TOLERANCE)
    assert np.isclose(p_v, expected["V"], atol=TOLERANCE)
    assert np.isclose(p_h + p_v, 1.0, atol=TOLERANCE)


@pytest.mark.parametrize(
    "n,thetas",
    [
        (2, [0.3, 1.1]),
        (2, [0.0, np.pi / 2]),
        (3, [0.3, 1.1, 0.75]),
    ],
)
def test_full_pipeline_multi_qubit_matches_product_distribution(n, thetas):
    """For weight-1-only generators, the joint output distribution must
    exactly factor into the product of each qubit's independent marginal --
    confirming no spurious correlations are introduced (the commutativity/
    independence claim ENC-01 makes, checked empirically at n=2-3)."""
    _, dist = run_full_circuit(n, thetas)
    expected = expected_joint_distribution(n, thetas)

    total_leak = 0.0
    checked_any = False
    for state_str, prob in dist.items():
        state = pcvl.BasicState(state_str)
        bits = basic_state_to_bitstring(state, n)
        if bits is None:
            total_leak += prob
            continue
        checked_any = True
        assert np.isclose(prob, expected[bits], atol=TOLERANCE), (
            f"n={n} thetas={thetas}: outcome {bits} got {prob}, expected {expected[bits]}"
        )

    assert checked_any
    assert np.isclose(total_leak, 0.0, atol=TOLERANCE), (
        "probability leaked outside the computational subspace (bunched/lost photons)"
    )


def test_module_functions_independently_callable():
    """Each building-block function must be independently constructible as a
    standalone Circuit(2n), per 09-01-PLAN.md Task 2's requirement."""
    n = 2
    assert build_state_prep_circuit(n).m == 2 * n
    assert build_diagonal_layer_circuit(n, [0.1, 0.2]).m == 2 * n
    assert build_conjugation_circuit(n).m == 2 * n
    assert build_readout_circuit(n).m == 2 * n
    assert build_full_circuit(n, [0.1, 0.2]).m == 2 * n


@pytest.mark.parametrize("n,bitstring", [(1, "0"), (1, "1"), (2, "00"), (2, "01"), (2, "10"), (2, "11"), (3, "101")])
def test_enc03_round_trip(n, bitstring):
    """ENC-03's falsifiability claim: forward map -> physical PBS readout ->
    reverse map must recover the original bitstring exactly. This is the same
    check that caught Plan 09-02's H/V port-labeling bug -- a real example of
    the correspondence being checkable, not just asserted."""
    fock_state = bitstring_to_fock(bitstring, n)
    readout_state = run_readout(n, fock_state)
    assert readout_state is not None
    decoded = fock_to_bitstring(readout_state, n)
    assert decoded == bitstring


@pytest.mark.parametrize(
    "invalid_pair",
    [(0, 0), (1, 1), (2, 0), (0, 2)],
)
def test_enc03_out_of_subspace_returns_none(invalid_pair):
    """Every non-single-photon pair pattern for a qubit ((0,0)=lost,
    (1,1)=extra photon split across both modes, (2,0)/(0,2)=bunched) must
    decode to None, not a wrong-but-plausible-looking bitstring."""
    state = pcvl.BasicState(list(invalid_pair))
    assert fock_to_bitstring(state, 1) is None


def test_enc03_out_of_subspace_in_larger_register():
    """An invalid pair for one qubit must invalidate the whole reading, even
    when the other qubits in the same register are perfectly valid."""
    # qubit 0 valid ('0'=H=(0,1)), qubit 1 invalid (bunched, (2,0))
    state = pcvl.BasicState([0, 1, 2, 0])
    assert fock_to_bitstring(state, 2) is None


@pytest.mark.parametrize(
    "n,thetas",
    [
        (2, [0.3, 1.1]),
        (3, [0.3, 1.1, 0.75]),
    ],
)
def test_enc04_toy_validation_runs_end_to_end(n, thetas):
    """ENC-04's central claim, actually run: the photonic circuit's output
    distribution (translated to bitstrings via ENC-03) must match the exact
    qubit-side IQP distribution to within TVD < 1e-6 (owner's chosen
    threshold) -- both sides are exact calculations (no sampling noise), so
    near-exact agreement is the right bar, not a loose one."""
    qubit_dist = exact_qubit_iqp_distribution(n, thetas)
    photonic_dist, residual = photonic_iqp_distribution(n, thetas)

    assert np.isclose(residual, 0.0, atol=1e-9)
    assert np.isclose(sum(qubit_dist.values()), 1.0, atol=1e-9)
    assert np.isclose(sum(photonic_dist.values()), 1.0, atol=1e-9)

    tvd = total_variation_distance(qubit_dist, photonic_dist)
    assert 0.0 <= tvd <= 1.0
    assert tvd < 1e-6, f"n={n} thetas={thetas}: TVD={tvd} exceeds the 1e-6 threshold"


# Phase 12 Plan 01: exact_qubit_iqp_distribution's pair_thetas extension (WT2-02).


@pytest.mark.parametrize(
    "n,thetas",
    [
        (2, [0.3, 1.1]),
        (3, [0.3, 1.1, 0.75]),
    ],
)
def test_exact_qubit_distribution_weight2_backward_compatible(n, thetas):
    """pair_thetas=None (or omitted entirely) must reproduce the pre-Phase-12
    weight-1-only output exactly -- no existing call site or test may be
    affected by this extension."""
    baseline = exact_qubit_iqp_distribution(n, thetas)
    explicit_none = exact_qubit_iqp_distribution(n, thetas, pair_thetas=None)
    assert set(baseline.keys()) == set(explicit_none.keys())
    for key in baseline:
        assert explicit_none[key] == pytest.approx(baseline[key], abs=1e-12)


@pytest.mark.parametrize(
    "n,thetas,pair_thetas",
    [
        (2, [0.0, 0.0], {(0, 1): np.pi / 4}),
        (2, [0.3, 1.1], {(0, 1): np.pi / 4}),
        (3, [0.2, 0.0, 0.0], {(1, 2): np.pi / 4}),
    ],
)
def test_exact_qubit_distribution_weight2_extension_sums_to_one(n, thetas, pair_thetas):
    """Any Z_i*Z_j pair-generator addition must still yield a normalized
    probability distribution (the phase layer is unitary, so this must hold
    regardless of pair_thetas' specific values)."""
    dist = exact_qubit_iqp_distribution(n, thetas, pair_thetas=pair_thetas)
    assert np.isclose(sum(dist.values()), 1.0, atol=1e-9)


# Phase 11 Plan 01: build_cz_insertion -- CZ insertion unit truth table.
#
# build_cz_insertion(n, i, j) returns a Circuit(6) that starts and ends with
# PBS (polarization -> dual rail -> polarization), which Perceval's
# SLOSBackend cannot simulate directly (`assert not
# circuit.requires_polarization` in perceval/backends/_slos.py -- confirmed
# empirically while building these tests). The phase/magnitude truth table
# below therefore targets `_build_cz_insertion_core()` -- the exact same
# PERM->heralded_cz->PERM wiring build_cz_insertion embeds internally, not a
# re-derivation -- using this module's own dual-rail convention
# (MODULE_DUAL_RAIL). Combined with the fact that a bare PBS deterministically
# maps a pure computational-basis polarization input to its dual-rail
# counterpart with amplitude exactly 1 and no extra phase (confirmed
# empirically below in test_pbs_conversion_is_phase_neutral, and already
# implicit in this suite's existing test_enc03_round_trip checks), this
# core's dual-rail truth table IS build_cz_insertion's polarization-basis
# truth table.


def test_cz_insertion_returns_circuit_and_herald_spec():
    """build_cz_insertion's external contract: a local Circuit(6) and a
    herald_spec read from heralded_cz's own in_heralds (not hardcoded)."""
    circuit, herald_spec = build_cz_insertion(2, 0, 1)
    assert circuit.m == 6
    assert herald_spec == {4: 1, 5: 1}


def test_pbs_conversion_is_phase_neutral_for_computational_basis():
    """A bare PBS maps a pure (non-superposed) H/V polarization input to its
    dual-rail counterpart with amplitude exactly 1 (real, positive, no extra
    phase) -- the fact that lets _build_cz_insertion_core's dual-rail truth
    table stand in for build_cz_insertion's full polarization-basis round
    trip. Uses Perceval's PolarizationSimulator (the only simulator that can
    process a PBS-containing circuit) on a standalone 2-mode PBS."""
    from perceval.simulators.polarization_simulator import PolarizationSimulator

    circuit = pcvl.Circuit(2)
    circuit.add(0, pcvl.PBS())
    sim = PolarizationSimulator(Simulator(SLOSBackend()))
    sim.set_circuit(circuit)

    for pol in ["{P:H}", "{P:V}"]:
        in_state = pcvl.BasicState(f"|{pol},0>")
        out = sim.evolve(in_state)
        # The evolved StateVector has exactly one term; its amplitude must be 1+0j.
        amplitudes = [out[state] for state in out.keys()]
        assert len(amplitudes) == 1
        assert np.isclose(amplitudes[0].real, 1.0, atol=PHASE_TOLERANCE)
        assert np.isclose(amplitudes[0].imag, 0.0, atol=PHASE_TOLERANCE)


@pytest.mark.parametrize("i_bit,j_bit", [("0", "0"), ("0", "1"), ("1", "0"), ("1", "1")])
def test_cz_insertion_phase_sign_computational_basis(i_bit, j_bit):
    """build_cz_insertion's internal PERM-adapted heralded_cz core reproduces
    CZ's diag(1,1,1,-1) truth table exactly on this module's own dual-rail
    convention (MODULE_DUAL_RAIL): |amplitude|^2 == 2/27 for all 4 combos,
    sign negative only on |1,1> -- the concrete pass/fail check for the
    ctrl/data swap fix (11-RESEARCH.md Pitfall 1)."""
    sim, herald_counts = _cz_core_simulator_and_herald_counts()
    state = _dual_rail_state(i_bit, j_bit, herald_counts)
    amp = sim.prob_amplitude(state, state)

    assert np.isclose(abs(amp) ** 2, EXPECTED_CZ_MAGNITUDE_SQ, atol=TOLERANCE)
    expected_sign = -1.0 if (i_bit, j_bit) == ("1", "1") else 1.0
    expected_value = expected_sign * np.sqrt(EXPECTED_CZ_MAGNITUDE_SQ)
    assert np.isclose(amp.real, expected_value, atol=PHASE_TOLERANCE)


def test_cz_insertion_phase_sign_superposition():
    """Superposition spot-checks (|+>|+>, |+>|0>) at build_cz_insertion's
    dual-rail core: each term's magnitude matches |amp_in|^2 * 2/27, and the
    relative sign flips only on the |1,1> component -- consistent with
    diag(1,1,1,-1) acting linearly on the computational-basis components,
    not just the pure computational-basis case."""
    sim, herald_counts = _cz_core_simulator_and_herald_counts()

    # |+>|+>: 4 equal-amplitude terms.
    amp_plus_plus = 0.5
    terms = [
        (amp_plus_plus, _dual_rail_state(i_bit, j_bit, herald_counts))
        for i_bit in "01"
        for j_bit in "01"
    ]
    sv = float(terms[0][0]) * pcvl.StateVector(terms[0][1])
    for amplitude, state in terms[1:]:
        sv = sv + float(amplitude) * pcvl.StateVector(state)
    out = sim.evolve(sv)

    for i_bit in "01":
        for j_bit in "01":
            state = _dual_rail_state(i_bit, j_bit, herald_counts)
            out_amp = out[state]
            assert np.isclose(abs(out_amp) ** 2, amp_plus_plus ** 2 * EXPECTED_CZ_MAGNITUDE_SQ, atol=TOLERANCE)
            expected_sign = -1.0 if (i_bit, j_bit) == ("1", "1") else 1.0
            expected_value = expected_sign * amp_plus_plus * np.sqrt(EXPECTED_CZ_MAGNITUDE_SQ)
            assert np.isclose(out_amp.real, expected_value, atol=PHASE_TOLERANCE)

    # |+>|0>: qubit i in superposition, qubit j fixed at '0' -- no |1,1>
    # component exists, so every term must stay positive (no sign flip).
    amp_plus_zero = 1 / np.sqrt(2)
    terms = [(amp_plus_zero, _dual_rail_state(i_bit, "0", herald_counts)) for i_bit in "01"]
    sv = float(terms[0][0]) * pcvl.StateVector(terms[0][1])
    for amplitude, state in terms[1:]:
        sv = sv + float(amplitude) * pcvl.StateVector(state)
    out = sim.evolve(sv)

    for i_bit in "01":
        state = _dual_rail_state(i_bit, "0", herald_counts)
        out_amp = out[state]
        assert np.isclose(abs(out_amp) ** 2, amp_plus_zero ** 2 * EXPECTED_CZ_MAGNITUDE_SQ, atol=TOLERANCE)
        expected_value = amp_plus_zero * np.sqrt(EXPECTED_CZ_MAGNITUDE_SQ)  # always positive -- no |1,1> term
        assert np.isclose(out_amp.real, expected_value, atol=PHASE_TOLERANCE)


# Phase 11 Plan 02: build_weight2_processor -- full pipeline composition.


def test_weight2_processor_heralds_nonempty():
    """Success Criterion 3, the calibration check: build_weight2_processor's
    assembled Processor must have its heralds registered at the exact global
    indices (2n, 2n+1) immediately after assembly -- not just 'non-empty',
    since a wrong-but-nonzero registration would pass a looser check."""
    n, i, j = 3, 0, 1
    proc = build_weight2_processor(n, i, j, [0.0, 0.0, 0.0])
    assert proc.heralds == {2 * n: 1, 2 * n + 1: 1}


def _build_weight2_tail_no_state_prep(n, i, j, thetas_folded):
    """Reproduces build_weight2_processor's diagonal-layer -> CZ-insertion ->
    conjugation -> readout wiring (same mapping dict, same mode layout)
    WITHOUT build_state_prep_circuit's leading Hadamard and WITHOUT
    registering heralds via Processor.add_herald. Exists solely to support
    test_weight2_herald_success_sanity -- see that test's docstring for why
    state_prep and add_herald must both be excluded here (a confirmed
    Perceval PolarizationSimulator limitation, not a design issue in this
    module). Returns (proc, herald_spec) -- proc exposes all 2n+2 modes
    (heralds not registered), so the caller must post-select on herald_spec
    manually."""
    total_modes = 2 * n + 2
    proc = pcvl.Processor("SLOS", total_modes)
    proc.add(0, build_diagonal_layer_circuit(n, thetas_folded))
    cz_circuit, herald_spec = build_cz_insertion(n, i, j)
    mapping = {
        2 * i: 0, 2 * i + 1: 1,
        2 * j: 2, 2 * j + 1: 3,
        2 * n: 4, 2 * n + 1: 5,
    }
    proc.add(mapping, cz_circuit)
    proc.add(0, build_conjugation_circuit(n))
    proc.add(0, build_readout_circuit(n))
    return proc, herald_spec


def test_weight2_herald_success_sanity():
    """11-RESEARCH.md Open Question 2's recommended cheap sanity check:
    confirms the lossless PBS wrap/unwrap doesn't change the bare
    heralded_cz's herald-success probability (2/27), now checked through the
    FULL mode-mapping-dict embedding build_weight2_processor uses (new
    information beyond Plan 11-01's local-Circuit(6)-only truth table).

    Deviation from the plan's literal recipe (Rule 3 -- blocking Perceval
    limitation, discovered during this plan's execution): calling
    build_weight2_processor(...) itself, then Processor.add_herald() +
    Processor.with_input() + Processor.probs() on the result, crashes
    unconditionally (`ValueError: matmul: ... size 12 is different from 16`
    in perceval/simulators/polarization_simulator.py's `_prepare_input`) for
    ANY circuit that combines a registered herald (`add_herald`) with a
    polarization-tracking (`PBS`-containing) circuit -- confirmed by direct
    execution, independent of thetas or state_prep. Separately, even without
    add_herald, feeding this pipeline through build_state_prep_circuit's
    Hadamard (creating a real polarization superposition before the CZ
    insertion) gives silently WRONG (non-crashing) probabilities -- the same
    unannotated-ancilla-photon-distinguishability artifact Plan 11-01's
    summary already flagged as a carry-forward concern for polarization-plus-
    heralded-ancilla simulation, now confirmed to also affect real Hadamard-
    created superpositions, not just directly-constructed dual-rail
    superposition states.

    This test therefore checks the herald-success invariant the way that
    stays inside Perceval's working envelope: no add_herald registration
    (bare Processor, all 2n+2 modes exposed, herald condition applied by
    hand via post-selection on the ancilla output modes), and no state_prep
    (a definite computational-basis input, which WP(theta,0) leaves as a
    definite state up to global phase -- no superposition reaches the CZ
    insertion). Both limitations are carried forward as concerns for Plan
    12's TVD validation strategy (must avoid Processor.probs() on the fully
    composed, herald-registered, PBS+superposition circuit)."""
    n, i, j = 3, 0, 1
    thetas_folded = [0.0, 0.0, 0.0]
    thetas_folded[i] += np.pi / 4
    thetas_folded[j] += np.pi / 4

    proc, herald_spec = _build_weight2_tail_no_state_prep(n, i, j, thetas_folded)
    ancilla_a, ancilla_b = 2 * n, 2 * n + 1
    expected_a, expected_b = herald_spec[4], herald_spec[5]

    # No add_herald registered on this bare processor, so with_input has no
    # auto-fill for the ancilla modes -- they need REAL input photons
    # matching herald_spec's expected counts (Phase 10 Pitfall 1: heralds
    # need a real photon on input, not vacuum), appended by hand to
    # all_h_input(n)'s qubit-port pattern.
    input_state = pcvl.BasicState(
        "|" + ",".join(["{P:H},0"] * n) + f",{expected_a},{expected_b}>"
    )
    proc.with_input(input_state)
    probs = proc.probs()
    herald_matched_total = sum(
        complex(p).real
        for state, p in probs["results"].items()
        if state[ancilla_a] == expected_a and state[ancilla_b] == expected_b
    )
    assert np.isclose(herald_matched_total, EXPECTED_CZ_MAGNITUDE_SQ, atol=TOLERANCE)


# n=2, chosen because build_state_prep_circuit has no parameters besides n,
# so its unitary is a pure function of the module's code. Captured live
# during Plan 11-02's execution -- since build_state_prep_circuit was NOT
# modified by this plan, this must match on first run. If it doesn't,
# something else changed unexpectedly (a real finding, not a test bug).
STATE_PREP_N2_SHA256 = "a61523a81534f6a30fad6b3bdecd777d29484c5009d3944c09aded0aaa228810"


def test_weight1_builders_unitary_unchanged():
    """CONTEXT.md's non-regression requirement: build_state_prep_circuit's
    unitary must be bit-identical to its value captured before this phase's
    changes -- guards against an accidental shared-helper edit, the same
    risk category as Phase 9's silent H/V labeling bug (a module every prior
    phase also depends on)."""
    n = 2
    matrix = np.array(build_state_prep_circuit(n).compute_unitary(), dtype=complex)
    digest = hashlib.sha256(matrix.tobytes()).hexdigest()
    assert digest == STATE_PREP_N2_SHA256


# Phase 12 Plan 01: TVD gate + herald-accounting tests (WT2-05, WT2-06).

EXPECTED_HERALD_FAILURE_PROB = 1 - 2 / 27  # Phase 10's confirmed heralded_cz success rate, 2/27


def test_wt2_tvd_gate_n2_theta_pi_4():
    """ROADMAP Success Criterion 3, the literal locked pass/fail gate: at
    n=2, i=0, j=1, a pure weight-2 pair term (theta=pi/4, no weight-1
    thetas), the photonic weight-2 distribution must match the extended
    exact reference to TVD < 1e-6 -- do not weaken this tolerance.
    Research (12-RESEARCH.md Step 4) measured TVD~2.2e-16 at this exact
    configuration with the {P:V} ancilla annotation fix applied."""
    n, i, j = 2, 0, 1
    thetas = [0.0, 0.0]

    qubit_dist = exact_qubit_iqp_distribution(n, thetas, pair_thetas={(0, 1): np.pi / 4})
    photonic_dist, residual, herald_failure_prob = photonic_weight2_iqp_distribution(n, i, j, thetas)

    assert np.isclose(residual, 0.0, atol=1e-9)
    assert np.isclose(herald_failure_prob, EXPECTED_HERALD_FAILURE_PROB, atol=1e-6)
    assert np.isclose(sum(qubit_dist.values()), 1.0, atol=1e-9)
    assert np.isclose(sum(photonic_dist.values()) + residual, 1.0, atol=1e-9)

    tvd = total_variation_distance(qubit_dist, photonic_dist)
    assert 0.0 <= tvd <= 1.0
    assert tvd < 1e-6, f"n={n} i={i} j={j}: TVD={tvd} exceeds the 1e-6 threshold"


def test_wt2_herald_failure_and_residual_are_separate_numbers():
    """CONTEXT.md-locked accounting check: dist, residual, and
    herald_failure_prob are three separate, never-merged numbers. dist sums
    to 1.0 minus residual exactly (herald_failure_prob was already divided
    out during renormalization, not folded in again), residual is near 0.0
    (lossless circuit) while herald_failure_prob is near 0.9259 -- they must
    be visibly different numbers, not the same value under two names."""
    n, i, j = 2, 0, 1
    thetas = [0.0, 0.0]

    dist, residual, herald_failure_prob = photonic_weight2_iqp_distribution(n, i, j, thetas)

    assert np.isclose(sum(dist.values()) + residual, 1.0, atol=1e-9)
    assert np.isclose(residual, 0.0, atol=1e-9)
    assert np.isclose(herald_failure_prob, EXPECTED_HERALD_FAILURE_PROB, atol=1e-6)
    assert abs(residual - herald_failure_prob) > 0.5, (
        "residual and herald_failure_prob must be visibly distinct numbers, not the same "
        "value silently reported under two names"
    )


def test_wt2_tvd_gate_n3_bystander_qubit():
    """Opportunistic robustness check (12-RESEARCH.md Step 5, CONTEXT.md
    'not a hard requirement'): n=3, pair (1,2), bystander qubit 0 at a
    nonzero weight-1 theta -- same TVD gate assertions as the locked n=2
    test, confirming the fix generalizes beyond the single locked
    configuration."""
    n, i, j = 3, 1, 2
    thetas = [0.6, 0.0, 0.0]

    qubit_dist = exact_qubit_iqp_distribution(n, thetas, pair_thetas={(1, 2): np.pi / 4})
    photonic_dist, residual, herald_failure_prob = photonic_weight2_iqp_distribution(n, i, j, thetas)

    assert np.isclose(residual, 0.0, atol=1e-9)
    assert np.isclose(herald_failure_prob, EXPECTED_HERALD_FAILURE_PROB, atol=1e-6)
    assert np.isclose(sum(qubit_dist.values()), 1.0, atol=1e-9)
    assert np.isclose(sum(photonic_dist.values()) + residual, 1.0, atol=1e-9)

    tvd = total_variation_distance(qubit_dist, photonic_dist)
    assert 0.0 <= tvd <= 1.0
    assert tvd < 1e-6, f"n={n} i={i} j={j} thetas={thetas}: TVD={tvd} exceeds the 1e-6 threshold"


# Phase 13: weight-1 + weight-2 composability (WT2-07).


@pytest.mark.parametrize(
    "n, i, j, thetas",
    [
        (3, 0, 1, [0.5, 0.0, 1.3]),
        (3, 1, 2, [0.9, 0.4, 0.0]),
        (3, 0, 2, [0.2, 1.7, 0.65]),
    ],
)
def test_wt2_composability_mixed_generators_n3(n, i, j, thetas):
    """ROADMAP Success Criterion 1 / WT2-07: n=3, 2 weight-1 terms (one
    stacked on a weight-2 pair member i or j, one on the bystander qubit
    outside the pair) plus 1 weight-2 term in the same circuit. Confirms
    weight-1 and weight-2 layers compose correctly, not just in isolation
    (Phases 10-12). Stacking a nonzero weight-1 theta directly on a pair
    qubit is a stronger test than using fully disjoint qubits (CONTEXT.md):
    it proves a qubit's independent Z term and its participation in the ZZ
    pair term compose correctly on the same qubit. Pair theta is locked at
    pi/4 internally by photonic_weight2_iqp_distribution (not
    caller-adjustable, per Phase 12's convention).

    Primary check: TVD < 1e-6 against the extended exact reference (both
    thetas and pair_thetas set) -- same style/tolerance as
    test_wt2_tvd_gate_n3_bystander_qubit. Companion sanity check: TVD
    against the weight-1-only exact reference (pair_thetas=None) must be
    clearly non-negligible, proving the ZZ term isn't vacuously doing
    nothing -- 13-RESEARCH.md measured 0.46-0.50 for these three configs;
    0.1 is used as a safe, non-flaky lower bound with headroom."""
    qubit_dist = exact_qubit_iqp_distribution(n, thetas, pair_thetas={(i, j): np.pi / 4})
    photonic_dist, residual, herald_failure_prob = photonic_weight2_iqp_distribution(n, i, j, thetas)

    assert np.isclose(residual, 0.0, atol=1e-9)
    assert np.isclose(herald_failure_prob, EXPECTED_HERALD_FAILURE_PROB, atol=1e-6)
    assert np.isclose(sum(qubit_dist.values()), 1.0, atol=1e-9)
    assert np.isclose(sum(photonic_dist.values()) + residual, 1.0, atol=1e-9)

    tvd = total_variation_distance(qubit_dist, photonic_dist)
    assert 0.0 <= tvd <= 1.0
    assert tvd < 1e-6, f"n={n} i={i} j={j} thetas={thetas}: TVD={tvd} exceeds the 1e-6 threshold"

    # Companion sanity check: confirm the ZZ term is doing real, non-vacuous
    # work -- TVD against the weight-1-only reference must be clearly
    # non-negligible (observed 0.46-0.50 in 13-RESEARCH.md; 0.1 threshold
    # gives large headroom while still ruling out an accidentally-inert
    # weight-2 term).
    qubit_dist_w1only = exact_qubit_iqp_distribution(n, thetas, pair_thetas=None)
    tvd_sanity = total_variation_distance(qubit_dist_w1only, photonic_dist)
    assert tvd_sanity > 0.1, (
        f"n={n} i={i} j={j} thetas={thetas}: sanity TVD={tvd_sanity} is too small -- "
        "the weight-2 (ZZ) term does not appear to have a non-negligible effect"
    )


# Phase 15 Plan 02: build_cp_insertion / _build_cp_insertion_core -- CP(alpha)
# insertion unit truth table (ARB-01 criterion 1, bare-core level).
#
# Mirrors the Phase 11 Plan 01 CZ-insertion truth-table tests above:
# build_cp_insertion's PBS-wrapped Circuit(8) cannot be simulated directly
# via Simulator/SLOSBackend (Circuit.requires_polarization), so these tests
# target _build_cp_insertion_core(alpha) -- the exact same PERM-adapted
# CP(alpha) wiring build_cp_insertion embeds internally, not a re-derivation
# -- using this module's own dual-rail convention (MODULE_DUAL_RAIL).

NON_TRIVIAL_CP_ALPHAS = [np.pi / 6, np.pi / 3, 2 * np.pi / 5]
BOUNDARY_CP_ALPHA = np.pi  # NOT np.pi / 4 -- 15-CONTEXT.md's owner-confirmed
# correction: alpha=pi (CP's own dial) reproduces heralded_cz's
# diag(1,1,1,-1) exactly, not alpha=pi/4 (see _build_cp_insertion_core's
# docstring for the full alpha-vs-theta disambiguation).


def _cp_core_amplitudes(alpha):
    """Simulator over _build_cp_insertion_core(alpha)'s own dual-rail core
    (PERM -> CP(alpha) -> PERM, no PBS), read via Simulator.prob_amplitude
    at all 4 computational-basis combos on MODULE_DUAL_RAIL, ancilla (local
    4-7) held at vacuum both ends -- the post-selected construction's own
    condition, mirrored directly (not registered via add_herald/
    set_postselection, matching 15-RESEARCH.md Pitfall 3's manual-filtering
    guidance)."""
    circuit = _build_cp_insertion_core(alpha)
    sim = Simulator(SLOSBackend())
    sim.set_circuit(circuit)
    ancilla = [0, 0, 0, 0]
    amplitudes = {}
    for i_bit in "01":
        for j_bit in "01":
            im, jm = MODULE_DUAL_RAIL[i_bit], MODULE_DUAL_RAIL[j_bit]
            state = pcvl.BasicState(list(im) + list(jm) + ancilla)
            amplitudes[(i_bit, j_bit)] = sim.prob_amplitude(state, state)
    return amplitudes


@pytest.mark.parametrize("alpha", NON_TRIVIAL_CP_ALPHAS + [BOUNDARY_CP_ALPHA])
def test_cp_insertion_core_matches_diag_1_1_1_ealpha(alpha):
    """_build_cp_insertion_core(alpha)'s dual-rail truth table (on
    MODULE_DUAL_RAIL) must match diag(1,1,1,e^{i*alpha}) exactly: uniform
    |amplitude|^2 across all 4 computational-basis combos, and
    amp(1,1)/amp(0,0) == e^{i*alpha} to floating-point precision -- the
    concrete pass/fail check for this plan's Step 1 convention-adapter fix."""
    amplitudes = _cp_core_amplitudes(alpha)

    magnitudes_sq = [abs(amp) ** 2 for amp in amplitudes.values()]
    reference = magnitudes_sq[0]
    for m in magnitudes_sq:
        assert np.isclose(m, reference, atol=1e-9), (
            f"alpha={alpha}: |amplitude|^2 not uniform across computational-basis combos"
        )

    amp_00 = amplitudes[("0", "0")]
    amp_11 = amplitudes[("1", "1")]
    ratio = amp_11 / amp_00
    expected = complex(np.cos(alpha), np.sin(alpha))
    assert np.isclose(ratio.real, expected.real, atol=PHASE_TOLERANCE)
    assert np.isclose(ratio.imag, expected.imag, atol=PHASE_TOLERANCE)


def test_cp_insertion_core_boundary_matches_cz_insertion_core_sign_for_sign():
    """ARB-06's direct boundary-agreement test, bare-core-level instance
    (the full-pipeline-level instance is Plan 15-04's job): at alpha=pi,
    _build_cp_insertion_core's sign pattern must be IDENTICAL to
    _build_cz_insertion_core's ALREADY-CONFIRMED diag(1,1,1,-1) truth
    table, sign-for-sign -- negative real amplitude on (1,1), positive on
    the other three, for BOTH gate families."""
    cp_amplitudes = _cp_core_amplitudes(BOUNDARY_CP_ALPHA)
    cz_sim, cz_herald_counts = _cz_core_simulator_and_herald_counts()

    for i_bit in "01":
        for j_bit in "01":
            cp_amp = cp_amplitudes[(i_bit, j_bit)]
            cz_state = _dual_rail_state(i_bit, j_bit, cz_herald_counts)
            cz_amp = cz_sim.prob_amplitude(cz_state, cz_state)

            expected_sign_negative = (i_bit, j_bit) == ("1", "1")
            assert (cp_amp.real < 0) == expected_sign_negative, (
                f"CP core sign mismatch at ({i_bit},{j_bit})"
            )
            assert (cz_amp.real < 0) == expected_sign_negative, (
                f"CZ core sign mismatch at ({i_bit},{j_bit})"
            )


def test_cp_insertion_returns_circuit_and_ancilla_spec():
    """build_cp_insertion's external contract: a local Circuit(8) and an
    ancilla_spec read from PostProcessedControlledRotationsItem's own
    in_heralds (not hardcoded) -- all 4 ancilla modes expected at vacuum
    (photon count 0), distinct in meaning from build_cz_insertion's
    herald_spec (1-photon herald counts)."""
    circuit, ancilla_spec = build_cp_insertion(2, 0, 1, np.pi / 3)
    assert circuit.m == 8
    assert ancilla_spec == {4: 0, 5: 0, 6: 0, 7: 0}


# Phase 15 Plan 04: photonic_cp_iqp_distribution -- full-pipeline TVD
# validation, alpha=pi boundary-agreement vs heralded_cz, and the
# success-probability-vs-alpha table (ARB-03/ARB-04/ARB-05/ARB-06).

NON_TRIVIAL_ALPHAS = [np.pi / 6, np.pi / 3, 2 * np.pi / 5]  # same 3 values as
# NON_TRIVIAL_CP_ALPHAS above (15-CONTEXT.md's locked non-trivial set),
# repeated here as its own name since this section validates the FULL
# pipeline, not the bare core.


@pytest.mark.parametrize("alpha", NON_TRIVIAL_ALPHAS)
def test_cp_pipeline_tvd_gate_n2(alpha):
    """ARB-03, the full-pipeline-level TVD gate for n=2, pair (0,1), across
    all 3 non-trivial alpha values -- same TVD<1e-6 bar WT2-05 already
    cleared for heralded_cz at its own fixed angle (15-CONTEXT.md's locked
    decision: do not relax the tolerance for this different gate mechanism).
    theta=alpha/4 per the ARB-01/ARB-02 identity (docs/iqp-photonic-encoding.md),
    reused directly as exact_qubit_iqp_distribution's pair_thetas argument."""
    n, i, j = 2, 0, 1
    thetas = [0.3, 1.1]
    theta = alpha / 4

    qubit_dist = exact_qubit_iqp_distribution(n, thetas, pair_thetas={(i, j): theta})
    photonic_dist, residual, postselect_failure_prob = photonic_cp_iqp_distribution(n, i, j, thetas, alpha)

    assert np.isclose(residual, 0.0, atol=1e-9)
    assert np.isclose(sum(qubit_dist.values()), 1.0, atol=1e-9)
    assert np.isclose(sum(photonic_dist.values()) + residual, 1.0, atol=1e-9)
    assert 0.0 < postselect_failure_prob < 1.0

    tvd = total_variation_distance(qubit_dist, photonic_dist)
    assert 0.0 <= tvd <= 1.0
    assert tvd < 1e-6, f"alpha={alpha}: TVD={tvd} exceeds the 1e-6 threshold"


@pytest.mark.parametrize("alpha", NON_TRIVIAL_ALPHAS)
def test_cp_pipeline_tvd_gate_n3_bystander_qubit(alpha):
    """ARB-03's n=3 instance, mirroring test_wt2_tvd_gate_n3_bystander_qubit's
    style: pair (1,2), bystander qubit 0 at a nonzero weight-1 theta. Confirms
    the fix generalizes beyond n=2 and beyond the single locked pair, across
    all 3 non-trivial alpha values (not just one, since ARB-03 requires
    coverage at n=2 AND n=3 for the tested angles)."""
    n, i, j = 3, 1, 2
    thetas = [0.6, 0.0, 0.0]
    theta = alpha / 4

    qubit_dist = exact_qubit_iqp_distribution(n, thetas, pair_thetas={(i, j): theta})
    photonic_dist, residual, postselect_failure_prob = photonic_cp_iqp_distribution(n, i, j, thetas, alpha)

    assert np.isclose(residual, 0.0, atol=1e-9)
    assert np.isclose(sum(qubit_dist.values()), 1.0, atol=1e-9)
    assert np.isclose(sum(photonic_dist.values()) + residual, 1.0, atol=1e-9)
    assert 0.0 < postselect_failure_prob < 1.0

    tvd = total_variation_distance(qubit_dist, photonic_dist)
    assert 0.0 <= tvd <= 1.0
    assert tvd < 1e-6, f"n=3 alpha={alpha}: TVD={tvd} exceeds the 1e-6 threshold"


def test_cp_pipeline_boundary_agreement_matches_heralded_cz():
    """ARB-05/ARB-06's direct full-pipeline boundary-agreement test (the
    missing third level -- Plans 15-01/15-02 already confirmed the bare-gate
    and bare-core levels): at alpha=pi (the corrected literal value per
    15-CONTEXT.md, NOT pi/4), photonic_cp_iqp_distribution's output must
    match the ALREADY-VALIDATED photonic_weight2_iqp_distribution
    (heralded_cz-based) output at the same (n, i, j, thetas) configuration --
    confirming CP(alpha=pi) genuinely reproduces heralded_cz's construction
    end-to-end, not just at the bare-gate/bare-core level."""
    n, i, j = 2, 0, 1
    thetas = [0.3, 1.1]

    cp_dist, cp_residual, cp_failure_prob = photonic_cp_iqp_distribution(n, i, j, thetas, np.pi)
    cz_dist, cz_residual, cz_herald_failure_prob = photonic_weight2_iqp_distribution(n, i, j, thetas)

    assert np.isclose(cp_residual, 0.0, atol=1e-9)
    assert np.isclose(cz_residual, 0.0, atol=1e-9)

    tvd = total_variation_distance(cp_dist, cz_dist)
    assert 0.0 <= tvd <= 1.0
    assert tvd < 1e-6, f"CP(alpha=pi) vs heralded_cz boundary-agreement TVD={tvd} exceeds the 1e-6 threshold"

    # The two gate families' success-probability MECHANISMS are genuinely
    # different (ARB-05: post-selection + ancilla vacuum vs. ancilla
    # heralding) -- their failure-probability NUMBERS need not, and do not,
    # match, even though their conditional output DISTRIBUTIONS do. Stated
    # explicitly here so the boundary agreement isn't misread as "the two
    # gates are identical in every respect."
    assert not np.isclose(cp_failure_prob, cz_herald_failure_prob, atol=1e-3)


def test_cp_pipeline_success_probability_vs_alpha_table():
    """ARB-04, closing the loop at the full-pipeline level (Plan 15-01
    already satisfied it at the bare-gate level): reports
    1 - postselect_failure_prob across all 3 non-trivial alpha values plus
    alpha=pi, as an explicit table -- never a single collapsed number.
    Matches the closed-form p_success(alpha)=1/sigma_max^4 derived in
    docs/iqp-photonic-encoding.md's ARB-02 section (n=2) to within 1e-6."""
    n, i, j = 2, 0, 1
    thetas = [0.0, 0.0]

    def sigma_max(alpha):
        a = np.sqrt(complex(np.exp(1j * alpha) - 1))
        return max(abs(1 + a), abs(1 - a))

    table = {}
    for alpha in NON_TRIVIAL_ALPHAS + [np.pi]:
        _, _, postselect_failure_prob = photonic_cp_iqp_distribution(n, i, j, thetas, alpha)
        success_prob = 1.0 - postselect_failure_prob
        table[alpha] = success_prob

        expected_success = 1.0 / sigma_max(alpha) ** 4
        assert np.isclose(success_prob, expected_success, atol=1e-6), (
            f"alpha={alpha}: measured success {success_prob} vs closed-form {expected_success}"
        )

    # Explicit table check (ARB-04's literal requirement): success
    # probability must be a genuine function of alpha, not a constant --
    # at least 2 distinct values across the 4 tested alpha points.
    assert len(set(round(v, 6) for v in table.values())) >= 2


# Phase 16 Plan 01: mixed weight-1 + arbitrary-theta weight-2 (CP)
# composability at n=3 (ARB-07).


@pytest.mark.parametrize(
    "n, i, j, thetas, alpha",
    [
        (3, 0, 1, [0.5, 0.0, 1.3], np.pi / 6),
        (3, 1, 2, [0.9, 0.4, 0.0], np.pi / 3),
        (3, 0, 2, [0.2, 1.7, 0.65], 2 * np.pi / 5),
    ],
)
def test_cp_composability_mixed_generators_n3(n, i, j, thetas, alpha):
    """ARB-07: n=3, 2 weight-1 terms plus 1 arbitrary-alpha weight-2 (CP)
    term in the same circuit -- the CP(alpha) analogue of
    test_wt2_composability_mixed_generators_n3 (Phase 13), using
    photonic_cp_iqp_distribution instead of photonic_weight2_iqp_distribution
    and a per-config alpha from NON_TRIVIAL_ALPHAS instead of the fixed
    pi/4 heralded_cz gate. Same 3 (n,i,j,thetas) tuples as Phase 13's test,
    each paired with a different non-trivial alpha to spread coverage
    across the validated range.

    Primary check: TVD < 1e-6 against the extended exact reference
    (pair_thetas={(i,j): alpha/4}), matching Phase 13/15's tolerance bar.
    Companion sanity check: TVD against the weight-1-only exact reference
    must be clearly non-negligible, proving the CP/ZZ term isn't vacuously
    inert. Unlike Phase 13 (which measured 0.46-0.50 at the FIXED pi/4
    angle), this test's alpha values fold in a much smaller effective
    theta=alpha/4 (~0.13-0.31 rad vs pi/4's ~0.785 rad), so the sanity TVD
    is genuinely smaller too -- measured directly for these 3 configs:
    0.017037 (alpha=pi/6), 0.066987 (alpha=pi/3), 0.087953 (alpha=2*pi/5).
    0.005 is used as a safe, non-flaky lower bound (>3x headroom below the
    smallest observed value), following Phase 13's own reasoning pattern
    of measuring first, then setting a threshold with headroom -- NOT
    reusing Phase 13's 0.1 literal value, since these alpha values produce
    a genuinely smaller (but still clearly non-zero) effect."""
    theta = alpha / 4
    qubit_dist = exact_qubit_iqp_distribution(n, thetas, pair_thetas={(i, j): theta})
    photonic_dist, residual, postselect_failure_prob = photonic_cp_iqp_distribution(n, i, j, thetas, alpha)

    assert np.isclose(residual, 0.0, atol=1e-9)
    assert np.isclose(sum(qubit_dist.values()), 1.0, atol=1e-9)
    assert np.isclose(sum(photonic_dist.values()) + residual, 1.0, atol=1e-9)
    assert 0.0 < postselect_failure_prob < 1.0

    tvd = total_variation_distance(qubit_dist, photonic_dist)
    assert 0.0 <= tvd <= 1.0
    assert tvd < 1e-6, f"n={n} i={i} j={j} alpha={alpha} thetas={thetas}: TVD={tvd} exceeds the 1e-6 threshold"

    # Companion sanity check: confirm the CP/ZZ term is doing real,
    # non-vacuous work -- see docstring above for the measured range and
    # threshold reasoning.
    qubit_dist_w1only = exact_qubit_iqp_distribution(n, thetas, pair_thetas=None)
    tvd_sanity = total_variation_distance(qubit_dist_w1only, photonic_dist)
    assert tvd_sanity > 0.005, (
        f"n={n} i={i} j={j} alpha={alpha} thetas={thetas}: sanity TVD={tvd_sanity} is too small -- "
        "the CP (weight-2) term does not appear to have a non-negligible effect"
    )
