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
    all_h_input,
    expected_single_qubit_probs,
    expected_joint_distribution,
    basic_state_to_bitstring,
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
    p_h = dist.get(str(pcvl.BasicState([1, 0])), 0.0)
    p_v = dist.get(str(pcvl.BasicState([0, 1])), 0.0)
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
    p_h = dist.get(str(pcvl.BasicState([1, 0])), 0.0)
    p_v = dist.get(str(pcvl.BasicState([0, 1])), 0.0)
    assert np.isclose(p_h, 0.5, atol=TOLERANCE)
    assert np.isclose(p_v, 0.5, atol=TOLERANCE)


@pytest.mark.parametrize("theta", [0.0, 0.3, np.pi / 6, np.pi / 4, np.pi / 2, np.pi])
def test_full_pipeline_single_qubit_matches_closed_form(theta):
    """Full ENC-01 pipeline (prep -> diagonal(theta) -> conjugation -> readout)
    for one qubit matches the empirically-confirmed closed form P(H)=sin^2(theta),
    P(V)=cos^2(theta)."""
    n = 1
    _, dist = run_full_circuit(n, [theta])
    p_h = dist.get(str(pcvl.BasicState([1, 0])), 0.0)
    p_v = dist.get(str(pcvl.BasicState([0, 1])), 0.0)
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
