"""Tests for dual_rail_merlin_encoding.py -- the additive, polarization-free
dual-rail/MerLin analogue of iqp_photonic_encoding.py's v2.0 (weight-1) and
v2.1 (weight-2) pipelines.

Ground truth throughout is bare Perceval (Analyzer + allstate_iterator) run
directly on this module's own dual-rail circuits -- independent of MerLin
entirely -- not a comparison against the polarization encoding's numbers
(different physical circuit, not expected to match value-for-value)."""

import numpy as np
import perceval as pcvl
import pytest
from perceval.utils import allstate_iterator

import merlin as ML
from dual_rail_merlin_encoding import (
    build_dual_rail_full_circuit,
    build_dual_rail_weight2_processor,
    dual_rail_all_zero_input,
    dual_rail_photonic_iqp_distribution,
    dual_rail_photonic_weight2_iqp_distribution,
    dual_rail_weight2_input_state,
    make_weight2_quantum_layer,
)
from iqp_photonic_encoding import fock_to_bitstring


def _bare_perceval_weight1_dist(n, thetas):
    circuit = build_dual_rail_full_circuit(n, thetas)
    proc = pcvl.Processor("SLOS", circuit)
    in_state = dual_rail_all_zero_input(n)
    proc.with_input(in_state)
    analyzer = pcvl.algorithm.Analyzer(proc, [in_state], list(allstate_iterator(in_state)))
    analyzer.compute()
    dist = {}
    for state, prob in zip(analyzer.output_states_list, analyzer.distribution[0]):
        bits = fock_to_bitstring(state, n)
        if bits is not None:
            dist[bits] = dist.get(bits, 0.0) + complex(prob).real
    return dist


def _bare_perceval_weight2_dist(n, i, j, thetas):
    proc, herald_spec = build_dual_rail_weight2_processor(n, i, j, thetas)
    in_state = dual_rail_weight2_input_state(n)
    proc.with_input(in_state)
    analyzer = pcvl.algorithm.Analyzer(proc, [in_state], list(allstate_iterator(in_state)))
    analyzer.compute()
    ancilla_a, ancilla_b = 2 * n, 2 * n + 1
    expected_a, expected_b = herald_spec[4], herald_spec[5]
    dist, herald_fail = {}, 0.0
    for state, prob in zip(analyzer.output_states_list, analyzer.distribution[0]):
        p = complex(prob).real
        if state[ancilla_a] != expected_a or state[ancilla_b] != expected_b:
            herald_fail += p
            continue
        bits = fock_to_bitstring(state, n)
        if bits is not None:
            dist[bits] = dist.get(bits, 0.0) + p
    success = 1.0 - herald_fail
    dist = {k: v / success for k, v in dist.items()} if success > 0 else dist
    return dist, herald_fail


@pytest.mark.parametrize("n,seed", [(2, 0), (3, 1), (3, 2)])
def test_weight1_matches_bare_perceval(n, seed):
    rng = np.random.default_rng(seed)
    thetas = rng.uniform(0, 2 * np.pi, size=n).tolist()

    merlin_dist, residual = dual_rail_photonic_iqp_distribution(n, thetas)
    gt_dist = _bare_perceval_weight1_dist(n, thetas)

    assert residual == pytest.approx(0.0, abs=1e-6)
    assert sum(merlin_dist.values()) + residual == pytest.approx(1.0, abs=1e-4)
    for key in set(merlin_dist) | set(gt_dist):
        assert merlin_dist.get(key, 0.0) == pytest.approx(gt_dist.get(key, 0.0), abs=1e-4)


def test_weight1_no_bunching_possible():
    """Weight-1's independent per-qubit blocks structurally cannot bunch
    (each pair carries exactly 1 photon, no cross-qubit mode mixing) --
    residual must be exactly (floating-point) zero, not just small."""
    dist, residual = dual_rail_photonic_iqp_distribution(3, [0.4, 1.1, 2.0])
    assert residual < 1e-9
    assert len(dist) == 2**3


@pytest.mark.parametrize("n,i,j,seed", [(2, 0, 1, 0), (3, 0, 2, 1)])
def test_weight2_matches_bare_perceval(n, i, j, seed):
    """Includes the n=3, i=0, j=2 non-contiguous case (qubit 1's pair sits
    between i and j), the actual stress test for the Processor-based
    mode-mapping construction."""
    rng = np.random.default_rng(seed)
    thetas = rng.uniform(0, 2 * np.pi, size=n).tolist()

    merlin_dist, residual, herald_fail = dual_rail_photonic_weight2_iqp_distribution(n, i, j, thetas)
    gt_dist, gt_herald_fail = _bare_perceval_weight2_dist(n, i, j, thetas)

    assert herald_fail == pytest.approx(gt_herald_fail, abs=1e-3)
    assert sum(merlin_dist.values()) + residual == pytest.approx(1.0, abs=1e-3)
    for key in set(merlin_dist) | set(gt_dist):
        assert merlin_dist.get(key, 0.0) == pytest.approx(gt_dist.get(key, 0.0), abs=1e-3)


def test_weight2_herald_failure_rate_matches_phase10():
    """At the pi/4 fold, herald_failure_prob must match Phase 10's
    independently-established heralded_cz success rate (2/27 success, so
    ~1 - 2/27 = 25/27 failure) -- this is this project's own known-answer
    check for the CZ-insertion core, reused unmodified here."""
    _, _, herald_fail = dual_rail_photonic_weight2_iqp_distribution(2, 0, 1, [0.3, 0.9])
    assert herald_fail == pytest.approx(25 / 27, abs=1e-3)


def test_weight2_requires_fock_computation_space_not_unbunched():
    """Regression guard: MerLin's UNBUNCHED default (not FOCK) silently drops
    real probability mass for this circuit, since heralded_cz's internal
    Hong-Ou-Mandel-type interference genuinely produces bunched ancilla
    configurations. Confirmed live during development: UNBUNCHED gave
    herald_failure_prob ~0.194 instead of the correct ~0.9259. This test
    locks that finding in so a future edit can't silently regress back to
    the wrong default."""
    from dual_rail_merlin_encoding import make_weight2_circuit_and_input
    import torch

    circuit, input_state, herald_spec = make_weight2_circuit_and_input(2, 0, 1)
    layer_unbunched = ML.QuantumLayer(
        circuit=circuit,
        input_state=input_state,
        trainable_parameters=["theta"],
        measurement_strategy=ML.MeasurementStrategy.probs(
            computation_space=ML.ComputationSpace.UNBUNCHED
        ),
    )
    with torch.no_grad():
        theta_tensor = dict(layer_unbunched.named_parameters())["theta"]
        theta_tensor.copy_(torch.tensor([0.3, 0.9], dtype=theta_tensor.dtype))
        out_flat = layer_unbunched().flatten()

    ancilla_a, ancilla_b = 4, 5
    expected_a, expected_b = herald_spec[4], herald_spec[5]
    herald_fail_unbunched = sum(
        val for key, val in zip(layer_unbunched.output_keys, out_flat.tolist())
        if key[ancilla_a] != expected_a or key[ancilla_b] != expected_b
    )
    # UNBUNCHED must NOT match the correct 25/27 -- if this assertion ever
    # fails, MerLin's default behavior has changed and FOCK may no longer be
    # necessary (investigate before removing it from the factory functions).
    assert herald_fail_unbunched != pytest.approx(25 / 27, abs=1e-2)


def test_weight2_layer_has_no_registered_herald():
    """This module deliberately never calls Processor.add_herald or uses
    experiment= -- confirms make_weight2_quantum_layer returns a plain
    unitary QuantumLayer (herald/postselection handled manually downstream),
    matching MerLin's documented "no heralding in experiment=" constraint."""
    layer, herald_spec = make_weight2_quantum_layer(2, 0, 1)
    assert herald_spec == {4: 1, 5: 1}
    # A plain forward pass must return probabilities over ALL output states
    # (unfiltered by any herald), i.e. more than just the 2^n subspace.
    out = layer()
    assert out.flatten().numel() > 2**2
