"""TDD tests for hardness/loss_model_weight2.py (Phase 18 Plan 03).

Proves HARD-07's locked decision is actually implemented, not merely
asserted: photon loss is applied via pcvl.LC insertion (never NoiseModel)
UNIFORMLY across all 2n+2 modes -- including heralded_cz's own 2 ancilla
modes, not just the 2n data-carrying modes -- and the herald-failure/
transmission-loss compounding is measured by running the real
heralded_cz pipeline end to end (never an analytical multiplication of the
lossless 2/27 herald rate against a separately-computed loss-survival
probability).

Same two 18-RESEARCH.md gotchas as Plan 18-02's weight-1 tests, re-proven
here rather than assumed carried over:
  - Pitfall 1: NoiseModel(transmittance=eta) silently no-ops for this
    project's polarization-annotated circuits -- avoided by construction
    (photonic_weight2_iqp_distribution_lossy never uses NoiseModel).
  - Pitfall 2: LC-based loss requires an explicit
    proc.min_detected_photons_filter(0) call, or Processor.probs() silently
    discards every lossy branch. Demonstrated live via a deliberately-broken
    local helper (below), not just avoided silently.
"""

import numpy as np
import perceval as pcvl
import pytest

from iqp_photonic_encoding import (
    build_cz_insertion,
    build_state_prep_circuit,
    build_diagonal_layer_circuit,
    build_conjugation_circuit,
    build_readout_circuit,
    _weight2_input_state,
    fock_to_bitstring,
    photonic_weight2_iqp_distribution,
    total_variation_distance,
)
from hardness.loss_model_weight2 import (
    photonic_weight2_iqp_distribution_lossy,
    _build_weight2_processor_lossy,
)

EXPECTED_HERALD_FAILURE_PROB = 1 - 2 / 27  # Phase 10's confirmed heralded_cz success rate


def _all_keys_close(dist_a, dist_b, atol):
    keys = set(dist_a) | set(dist_b)
    return all(abs(dist_a.get(k, 0.0) - dist_b.get(k, 0.0)) <= atol for k in keys)


# --- Case 1: eta=1.0 is a genuine no-op (LC(0) is a true identity) ---------


def test_eta_1_reproduces_lossless_weight2_reference_n2():
    n, i, j = 2, 0, 1
    rng = np.random.default_rng(1803)
    for _ in range(2):
        thetas = rng.uniform(0.0, 2 * np.pi, size=n).tolist()

        expected_dist, expected_residual, expected_hfp = photonic_weight2_iqp_distribution(
            n, i, j, thetas
        )
        dist, residual, herald_failure_prob, global_perf = photonic_weight2_iqp_distribution_lossy(
            n, i, j, thetas, eta=1.0
        )

        assert _all_keys_close(dist, expected_dist, atol=1e-6)
        assert abs(residual - expected_residual) <= 1e-6
        assert abs(herald_failure_prob - expected_hfp) <= 1e-6
        assert abs(herald_failure_prob - EXPECTED_HERALD_FAILURE_PROB) <= 1e-6


def test_eta_1_reproduces_lossless_weight2_reference_n3_bystander():
    n, i, j = 3, 1, 2
    rng = np.random.default_rng(1804)
    thetas = rng.uniform(0.0, 2 * np.pi, size=n).tolist()

    expected_dist, expected_residual, expected_hfp = photonic_weight2_iqp_distribution(
        n, i, j, thetas
    )
    dist, residual, herald_failure_prob, global_perf = photonic_weight2_iqp_distribution_lossy(
        n, i, j, thetas, eta=1.0
    )

    assert _all_keys_close(dist, expected_dist, atol=1e-6)
    assert abs(residual - expected_residual) <= 1e-6
    assert abs(herald_failure_prob - expected_hfp) <= 1e-6
    assert abs(herald_failure_prob - EXPECTED_HERALD_FAILURE_PROB) <= 1e-6
    assert abs(global_perf - 1.0) <= 1e-6


# --- Case 2: ancilla modes are structurally included in the loss model ----


def test_ancilla_modes_included_in_loss_model():
    """Direct, structural proof of HARD-07's requirement (not an indirect
    numeric inference): an LC component must sit on every one of the 2n+2
    modes -- including the 2 tail herald ancilla modes (2n, 2n+1) -- not
    just the 2n data-carrying modes."""
    n, i, j = 2, 0, 1
    thetas = [0.3, 0.5]
    total_modes = 2 * n + 2

    proc, herald_spec = _build_weight2_processor_lossy(n, i, j, thetas, eta=0.6)

    lc_modes = set()
    for mode_range, component in proc.components:
        if isinstance(component, pcvl.LC):
            lc_modes.update(mode_range)

    expected_modes = set(range(total_modes))
    assert expected_modes.issubset(lc_modes), (
        f"LC components must cover all {total_modes} modes (0..{total_modes - 1}), "
        f"but only found LC on modes {sorted(lc_modes)}"
    )
    # The HARD-07-specific requirement: the 2 ancilla modes specifically.
    assert 2 * n in lc_modes, "ancilla mode 2n missing an LC component"
    assert 2 * n + 1 in lc_modes, "ancilla mode 2n+1 missing an LC component"


# --- Case 3: herald-failure compounding is real, not analytically decomposed


def test_herald_failure_compounding_is_real_not_analytically_decomposed():
    n, i, j = 2, 0, 1
    thetas = [0.4, 0.9]
    eta_grid = [1.0, 0.7, 0.4, 0.1]

    hfp_at_eta = {}
    for eta in eta_grid:
        _, _, herald_failure_prob, _ = photonic_weight2_iqp_distribution_lossy(
            n, i, j, thetas, eta=eta
        )
        hfp_at_eta[eta] = herald_failure_prob

    # Herald failure genuinely degrades (increases) as eta decreases from 1.0.
    for earlier_eta, later_eta in zip(eta_grid, eta_grid[1:]):
        assert hfp_at_eta[later_eta] >= hfp_at_eta[earlier_eta] - 1e-9, (
            f"expected herald_failure_prob to increase (or hold) as eta decreases: "
            f"eta={earlier_eta} -> {hfp_at_eta[earlier_eta]}, "
            f"eta={later_eta} -> {hfp_at_eta[later_eta]}"
        )
    assert hfp_at_eta[0.1] > hfp_at_eta[1.0] + 1e-6, (
        "herald_failure_prob should genuinely shift under strong loss, not stay pinned "
        "at the lossless 2/27 value"
    )

    # NOT equal to the naive analytically-decomposed prediction: a simple
    # per-photon-survival product across all 2n+2 modes, decomposed
    # independently of heralded_cz's own physics. CONTEXT.md explicitly
    # forbids this shortcut -- prove the real pipeline differs from it.
    hfp_at_eta_1 = hfp_at_eta[1.0]
    total_modes = 2 * n + 2
    for eta in [0.7, 0.4, 0.1]:
        naive_prediction = 1.0 - (1.0 - hfp_at_eta_1) * (eta ** total_modes)
        actual = hfp_at_eta[eta]
        assert abs(actual - naive_prediction) > 1e-6, (
            f"herald_failure_prob at eta={eta} ({actual}) matched the naive "
            f"analytically-decomposed prediction ({naive_prediction}) -- compounding "
            "must be a genuine full-pipeline effect, not a per-mode-survival product"
        )


# --- Case 4: Pitfall-2 regression, demonstrated not just avoided ----------


def _broken_weight2_lossy_no_filter(n, i, j, thetas, eta):
    """Deliberately-broken reference reproducing
    photonic_weight2_iqp_distribution_lossy's exact wiring but OMITTING
    proc.min_detected_photons_filter(0) -- the Pitfall-2 regression this
    test file must prove is real, not just avoided. Local to this test file
    only, never exported from hardness/loss_model_weight2.py: this is a
    broken code path, not a supported one."""
    thetas_folded = list(thetas)
    thetas_folded[i] += np.pi / 4
    thetas_folded[j] += np.pi / 4

    total_modes = 2 * n + 2
    loss = 1.0 - eta
    proc = pcvl.Processor("SLOS", total_modes)
    for m in range(total_modes):
        proc.add(m, pcvl.LC(loss))

    proc.add(0, build_state_prep_circuit(n))
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
    # NOTE: proc.min_detected_photons_filter(0) deliberately NOT called here.

    input_state = _weight2_input_state(n, herald_spec)
    proc.with_input(input_state)
    res = proc.probs()

    ancilla_a, ancilla_b = 2 * n, 2 * n + 1
    expected_a, expected_b = herald_spec[4], herald_spec[5]

    dist = {}
    residual = 0.0
    herald_failure_prob = 0.0
    for state, p in res["results"].items():
        p = float(p)
        if state[ancilla_a] != expected_a or state[ancilla_b] != expected_b:
            herald_failure_prob += p
            continue
        bits = fock_to_bitstring(state, n)
        if bits is None:
            residual += p
        else:
            dist[bits] = dist.get(bits, 0.0) + p

    herald_success_prob = 1.0 - herald_failure_prob
    if herald_success_prob > 0:
        dist = {k: v / herald_success_prob for k, v in dist.items()}
        residual = residual / herald_success_prob
    return dist, residual, herald_failure_prob, res["global_perf"]


def test_pitfall_2_regression_broken_helper_is_loss_invariant_correct_fn_is_not():
    n, i, j = 2, 0, 1
    thetas = [0.4, 0.9]

    # The broken helper (no min_detected_photons_filter(0) call): its
    # herald_failure_prob and dist stay pinned at the lossless value across
    # eta -- exactly the silent, plausible-looking bug 18-RESEARCH.md
    # Pitfall 2 warns about ("herald-success-rate never moves off 2/27").
    broken_dist_full, _, broken_hfp_full, _ = _broken_weight2_lossy_no_filter(
        n, i, j, thetas, eta=1.0
    )
    broken_dist_lossy, _, broken_hfp_lossy, _ = _broken_weight2_lossy_no_filter(
        n, i, j, thetas, eta=0.3
    )
    assert abs(broken_hfp_full - broken_hfp_lossy) <= 1e-6, (
        "the broken (no-filter) helper was expected to be loss-invariant in "
        "herald_failure_prob -- if this fails, Pitfall 2's failure mode is no longer "
        "reproducible and this regression test needs to be revisited"
    )
    assert _all_keys_close(broken_dist_full, broken_dist_lossy, atol=1e-6), (
        "the broken (no-filter) helper was expected to be loss-invariant in dist too"
    )

    # The real, correct function genuinely differs with eta -- proves the
    # explicit min_detected_photons_filter(0) call actually matters.
    correct_dist_full, _, correct_hfp_full, _ = photonic_weight2_iqp_distribution_lossy(
        n, i, j, thetas, eta=1.0
    )
    correct_dist_lossy, _, correct_hfp_lossy, _ = photonic_weight2_iqp_distribution_lossy(
        n, i, j, thetas, eta=0.3
    )
    assert abs(correct_hfp_full - correct_hfp_lossy) > 1e-6, (
        "expected photonic_weight2_iqp_distribution_lossy's herald_failure_prob to "
        "genuinely vary with eta"
    )
    tvd = total_variation_distance(correct_dist_full, correct_dist_lossy)
    assert tvd > 0.02, (
        f"expected photonic_weight2_iqp_distribution_lossy's dist to meaningfully vary "
        f"with eta (TVD > 0.02), got TVD={tvd}"
    )


# --- Validation: eta out of range -------------------------------------


def test_eta_out_of_range_raises():
    with pytest.raises(ValueError):
        photonic_weight2_iqp_distribution_lossy(2, 0, 1, [0.0, 0.0], eta=1.5)
    with pytest.raises(ValueError):
        photonic_weight2_iqp_distribution_lossy(2, 0, 1, [0.0, 0.0], eta=-0.1)
