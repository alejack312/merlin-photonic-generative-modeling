import sys
import os

import numpy as np
import pytest
import perceval as pcvl

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from iqp_photonic_encoding import (
    build_state_prep_circuit,
    build_diagonal_layer_circuit,
    build_conjugation_circuit,
    build_readout_circuit,
    build_full_circuit,
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
)

TOLERANCE = 1e-9


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
