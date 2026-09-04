"""TDD tests for merlin_iqp/hardness/loss_model_weight2.py (Phase 18 Plan 03).

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

from merlin_iqp.encoding.iqp_photonic import (
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
from merlin_iqp.hardness.loss_model_weight2 import (
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
        dist, residual, herald_failure_prob, global_perf, _partial_loss = photonic_weight2_iqp_distribution_lossy(
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
    dist, residual, herald_failure_prob, global_perf, _partial_loss = photonic_weight2_iqp_distribution_lossy(
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
        _, _, herald_failure_prob, _, _ = photonic_weight2_iqp_distribution_lossy(
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
    only, never exported from merlin_iqp/hardness/loss_model_weight2.py: this is a
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
    correct_dist_full, _, correct_hfp_full, _, _ = photonic_weight2_iqp_distribution_lossy(
        n, i, j, thetas, eta=1.0
    )
    correct_dist_lossy, _, correct_hfp_lossy, _, _ = photonic_weight2_iqp_distribution_lossy(
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


# --- Case 5: Pitfall-3 regression, demonstrated not just avoided ----------


def _broken_weight2_with_add_herald(n, i, j, thetas, eta):
    """Deliberately-broken reference reproducing
    photonic_weight2_iqp_distribution_lossy's exact wiring but REGISTERING
    add_herald() on the two ancilla modes and letting Processor.with_input()
    auto-fill them from a reduced (2n-mode) input state -- the Pitfall-3
    regression this test file must prove is real, not just avoided by never
    calling add_herald(). Local to this test file only, never exported from
    merlin_iqp/hardness/loss_model_weight2.py: this is a broken code path, not a
    supported one."""
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
    proc.min_detected_photons_filter(0)

    # The deliberately-broken part: registering add_herald() and then
    # supplying only the reduced (2n-mode) data input, letting the herald
    # ancilla modes auto-fill. Documented (18-RESEARCH.md Pitfall 3,
    # re-confirmed live 2026-08-17) to crash Processor.probs() for
    # PBS-containing circuits like this one -- matching the already-corrected
    # STATE.md decision-log account of Perceval#783's actual trigger
    # condition (herald modes omitted from with_input(), not add_herald()
    # itself).
    proc.add_herald(2 * n, herald_spec[2 * n])
    proc.add_herald(2 * n + 1, herald_spec[2 * n + 1])

    reduced_input = pcvl.BasicState("|" + ",".join(["{P:H},0"] * n) + ">")
    proc.with_input(reduced_input)
    return proc.probs()


def test_pitfall_3_regression_add_herald_with_pbs_crashes():
    """Proves 18-RESEARCH.md Pitfall 3 is real, not just avoided:
    registering add_herald() on heralded_cz's ancilla modes and letting
    Processor auto-fill them from a reduced input crashes Processor.probs()
    for this PBS-containing circuit. photonic_weight2_iqp_distribution_lossy
    avoids this entirely by never calling add_herald() and always supplying
    the full (2n+2)-mode annotated input explicitly (_weight2_input_state)."""
    n, i, j = 2, 0, 1
    thetas = [0.4, 0.9]

    with pytest.raises(Exception):
        _broken_weight2_with_add_herald(n, i, j, thetas, eta=0.8)

    # The real, correct function has no such crash risk -- same n/i/j/thetas.
    dist, residual, herald_failure_prob, global_perf, _partial_loss = photonic_weight2_iqp_distribution_lossy(
        n, i, j, thetas, eta=0.8
    )
    assert dist  # ran successfully, produced a non-empty distribution


# --- Case 6: Pitfall-4 regression, demonstrated not just avoided ----------


def test_pitfall_4_regression_global_perf_is_not_a_herald_failure_proxy():
    """Proves 18-RESEARCH.md Pitfall 4 is real: global_perf stays pinned
    near its lossless value across the entire eta sweep (min_detected_
    photons_filter(0) keeps essentially all probability mass, so nothing
    gets filtered out) while herald_failure_prob genuinely degrades with
    eta -- a caller who mistakenly reads global_perf as a proxy for
    herald-mechanism degradation would see no usable signal at all, not
    just a numerically-different one."""
    n, i, j = 2, 0, 1
    thetas = [0.4, 0.9]
    eta_grid = [1.0, 0.7, 0.4, 0.1]

    hfp_values = []
    global_perf_values = []
    for eta in eta_grid:
        _, _, herald_failure_prob, global_perf, _partial_loss = photonic_weight2_iqp_distribution_lossy(
            n, i, j, thetas, eta=eta
        )
        hfp_values.append(herald_failure_prob)
        global_perf_values.append(global_perf)

    # global_perf stays pinned -- uninformative about herald degradation.
    for gp in global_perf_values:
        assert abs(gp - global_perf_values[0]) <= 1e-6, (
            f"expected global_perf to stay pinned (uninformative) across the "
            f"eta sweep, got {global_perf_values} -- if this fails, Pitfall "
            "4's conflation risk may no longer be reproducible and this "
            "regression test needs to be revisited"
        )

    # herald_failure_prob genuinely moves -- the real signal a caller needs.
    assert hfp_values[-1] > hfp_values[0] + 1e-3, (
        f"expected herald_failure_prob to genuinely degrade across the eta "
        f"sweep, got {hfp_values}"
    )

    # The two quantities materially diverge -- proving they are not
    # interchangeable, per the module docstring's explicit warning.
    for hfp, gp in zip(hfp_values, global_perf_values):
        assert abs(hfp - gp) > 1e-3, (
            f"expected herald_failure_prob ({hfp}) and global_perf ({gp}) to "
            "materially diverge -- if they ever converge, the conflation "
            "risk documented as Pitfall 4 would no longer be real"
        )


# --- Validation: eta out of range -------------------------------------


def test_eta_out_of_range_raises():
    with pytest.raises(ValueError):
        photonic_weight2_iqp_distribution_lossy(2, 0, 1, [0.0, 0.0], eta=1.5)
    with pytest.raises(ValueError):
        photonic_weight2_iqp_distribution_lossy(2, 0, 1, [0.0, 0.0], eta=-0.1)


# --- REFRAME-02: partial_loss mass-reconciliation regression tests --------


@pytest.mark.parametrize("eta", [1.0, 0.7, 0.3, 0.1])
def test_partial_loss_mass_matches_residual(eta):
    """Test A (backward-compatibility invariant, D-03): residual and
    partial_loss are accumulated independently inside
    photonic_weight2_iqp_distribution_lossy (residual is not derived from
    partial_loss), and both receive the SAME herald-success renormalization,
    so their agreement is a genuine cross-check that nothing about the
    pre-existing residual scalar changed. eta=0.0 is excluded here: at total
    loss herald_success_prob is exactly 0 and both quantities are left
    un-renormalized by the existing (pre-REFRAME-02) guard, which Test D
    covers separately."""
    n, i, j = 2, 0, 1
    thetas = [0.4, 0.9]
    dist, residual, herald_failure_prob, global_perf, partial_loss = photonic_weight2_iqp_distribution_lossy(
        n, i, j, thetas, eta=eta
    )
    assert abs(sum(partial_loss.values()) - residual) <= 1e-9


@pytest.mark.parametrize("eta", [1.0, 0.7, 0.3, 0.1])
def test_partial_loss_plus_dist_totals_one_herald_success_conditioned(eta):
    """Test B (total mass), herald-success-conditioned: sum(dist) +
    sum(partial_loss) reconstructs the already-shipped, already-exercised
    julia/generate_reference.py invariant sum(dist) + residual == 1.0 for
    weight-2's renormalized (herald-success-conditioned) outputs. eta=0.0
    is excluded -- see test_partial_loss_mass_matches_residual's docstring."""
    n, i, j = 2, 0, 1
    thetas = [0.4, 0.9]
    dist, residual, herald_failure_prob, global_perf, partial_loss = photonic_weight2_iqp_distribution_lossy(
        n, i, j, thetas, eta=eta
    )
    assert abs(sum(dist.values()) + sum(partial_loss.values()) - 1.0) <= 1e-9


@pytest.mark.parametrize("eta", [1.0, 0.7, 0.3, 0.1])
def test_global_perf_is_pinned_and_uninformative_about_partial_loss_mass(eta):
    """Test C (global_perf consistency) -- derived empirically (see this
    plan's null-result step, not assumed): global_perf stays pinned at
    ~1.0 across the entire eta grid, regardless of how much probability mass
    partial_loss holds or how herald_failure_prob moves, because
    min_detected_photons_filter(0) never actually filters anything (>=0
    detected photons is every outcome) and the injected LC-based loss lives
    inside the circuit, not in Perceval's own performance-tracking
    machinery. This is a null result: global_perf is NOT a usable proxy for
    partial_loss's total mass, extending the existing Pitfall-4 finding that
    global_perf is also not a usable proxy for herald_failure_prob."""
    n, i, j = 2, 0, 1
    thetas = [0.4, 0.9]
    dist, residual, herald_failure_prob, global_perf, partial_loss = photonic_weight2_iqp_distribution_lossy(
        n, i, j, thetas, eta=eta
    )
    assert abs(global_perf - 1.0) <= 1e-6


def test_partial_loss_is_genuinely_populated_not_an_empty_formality():
    """Test D: at eta strictly between 0 and 1, partial_loss is non-empty
    and disjoint from dist's keys; at eta=1.0 its mass is ~0; at eta=0.0
    herald_success_prob is exactly 0 so the existing (pre-REFRAME-02)
    renormalization guard leaves both dist and partial_loss at their raw
    accumulated value of 0.0 (no herald ever succeeds under total loss, so
    the bits-decoding branch that would populate them is never reached)."""
    n, i, j = 2, 0, 1
    thetas = [0.4, 0.9]

    dist_mid, _, _, _, partial_loss_mid = photonic_weight2_iqp_distribution_lossy(
        n, i, j, thetas, eta=0.5
    )
    assert partial_loss_mid
    assert set(partial_loss_mid.keys()).isdisjoint(set(dist_mid.keys()))

    _, _, _, _, partial_loss_full = photonic_weight2_iqp_distribution_lossy(
        n, i, j, thetas, eta=1.0
    )
    assert sum(partial_loss_full.values()) <= 1e-6

    _, _, herald_failure_prob_zero, _, partial_loss_zero = photonic_weight2_iqp_distribution_lossy(
        n, i, j, thetas, eta=0.0
    )
    assert abs(herald_failure_prob_zero - 1.0) <= 1e-9
    assert abs(sum(partial_loss_zero.values())) <= 1e-9
