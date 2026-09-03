"""TDD tests for merlin_iqp/hardness/loss_model.py (Phase 18 Plan 02).

Proves both load-bearing gotchas from 18-RESEARCH.md are actually avoided,
not merely assumed avoided:
  - Pitfall 1: NoiseModel(transmittance=eta) silently no-ops for this
    project's polarization-annotated circuits -- photonic_iqp_distribution_lossy
    must use pcvl.LC insertion instead, never NoiseModel, inside its own body.
  - Pitfall 2: LC-based loss requires an explicit
    proc.min_detected_photons_filter(0) call, or Processor.probs() silently
    discards every lossy branch and returns a loss-invariant "normalized"
    result. Demonstrated live via a deliberately-broken local helper (below),
    not just avoided silently -- mirrors 17-01's pi/2-shift regression style.

Also covers HARD-02: since NoiseModel cannot be run end-to-end on this
project's real polarization circuits (Pitfall 1), the honest cross-check is
confirming NoiseModel and LC -- two independently-implemented Perceval loss
mechanisms -- agree with each other on a shared, simplified, non-polarization
toy circuit where both are actually applicable (18-RESEARCH.md's Code
Examples section).
"""

import numpy as np
import perceval as pcvl
import pytest

from merlin_iqp.encoding.iqp_photonic import photonic_iqp_distribution, total_variation_distance
from merlin_iqp.hardness.loss_model import photonic_iqp_distribution_lossy


def _all_keys_close(dist_a, dist_b, atol):
    keys = set(dist_a) | set(dist_b)
    return all(abs(dist_a.get(k, 0.0) - dist_b.get(k, 0.0)) <= atol for k in keys)


# --- Case 1: eta=1.0 is a genuine identity (LC(0) is a true no-op) ---------


@pytest.mark.parametrize("n", [1, 2, 3])
def test_eta_1_reproduces_lossless_reference_bit_for_bit(n):
    rng = np.random.default_rng(1802)
    for _ in range(3):
        thetas = rng.uniform(0.0, 2 * np.pi, size=n).tolist()

        expected_dist, expected_residual = photonic_iqp_distribution(n, thetas)
        dist, residual, global_perf, _partial_loss = photonic_iqp_distribution_lossy(n, thetas, eta=1.0)

        assert _all_keys_close(dist, expected_dist, atol=1e-9)
        assert abs(residual - expected_residual) <= 1e-9
        assert abs(global_perf - 1.0) <= 1e-6


# --- Case 2: eta-dependence, and the Pitfall-2 regression demonstrated live -


ETA_GRID = [1.0, 0.7, 0.3, 0.0]


def test_survival_mass_is_monotonically_non_increasing_as_eta_decreases():
    n = 2
    thetas = [0.4, 1.1]

    survival = []
    for eta in ETA_GRID:
        dist, residual, global_perf, _partial_loss = photonic_iqp_distribution_lossy(n, thetas, eta=eta)
        survival.append(sum(dist.values()))

    for earlier, later in zip(survival, survival[1:]):
        assert later <= earlier + 1e-9  # non-increasing as eta decreases

    # eta=0.0: total loss -- no in-subspace mass survives.
    dist_zero, residual_zero, global_perf_zero, _partial_loss_zero = photonic_iqp_distribution_lossy(
        n, thetas, eta=0.0
    )
    assert sum(dist_zero.values()) <= 1e-9
    assert abs(residual_zero - 1.0) <= 1e-9


def _broken_lossy_distribution_no_filter(n, thetas, eta):
    """Deliberately-broken reference reproducing photonic_iqp_distribution_lossy's
    exact wiring but OMITTING proc.min_detected_photons_filter(0) -- the
    Pitfall-2 regression this test file must prove is real, not just avoided.
    Local to this test file only, never exported from merlin_iqp/hardness/loss_model.py:
    this is a broken code path, not a supported one."""
    from merlin_iqp.encoding.iqp_photonic import build_full_circuit, all_h_input, fock_to_bitstring

    loss = 1.0 - eta
    total_modes = 2 * n
    proc = pcvl.Processor("SLOS", total_modes)
    for m in range(total_modes):
        proc.add(m, pcvl.LC(loss))
    proc.add(0, build_full_circuit(n, thetas))
    # NOTE: proc.min_detected_photons_filter(0) deliberately NOT called here.
    proc.with_input(all_h_input(n))
    res = proc.probs()

    dist = {}
    residual = 0.0
    for state, prob in res["results"].items():
        p = float(prob)
        bits = fock_to_bitstring(state, n)
        if bits is None:
            residual += p
        else:
            dist[bits] = dist.get(bits, 0.0) + p
    return dist, residual, res["global_perf"]


def test_pitfall_2_regression_broken_helper_is_loss_invariant_correct_fn_is_not():
    n = 1
    thetas = [0.6]

    # The broken helper (no min_detected_photons_filter(0) call): its
    # "normalized" dist looks identical at eta=1.0 and eta=0.3 -- exactly
    # the silent, plausible-looking bug 18-RESEARCH.md Pitfall 2 warns about.
    broken_dist_full, _, _ = _broken_lossy_distribution_no_filter(n, thetas, eta=1.0)
    broken_dist_lossy, _, _ = _broken_lossy_distribution_no_filter(n, thetas, eta=0.3)
    assert _all_keys_close(broken_dist_full, broken_dist_lossy, atol=1e-9), (
        "the broken (no-filter) helper was expected to be loss-invariant -- "
        "if this fails, Pitfall 2's failure mode is no longer reproducible "
        "and this regression test needs to be revisited"
    )

    # The real, correct function genuinely differs with eta -- proves the
    # explicit min_detected_photons_filter(0) call actually matters.
    correct_dist_full, _, _, _ = photonic_iqp_distribution_lossy(n, thetas, eta=1.0)
    correct_dist_lossy, _, _, _ = photonic_iqp_distribution_lossy(n, thetas, eta=0.3)
    tvd = total_variation_distance(correct_dist_full, correct_dist_lossy)
    assert tvd > 0.05, (
        f"expected photonic_iqp_distribution_lossy's dist to meaningfully "
        f"vary with eta (TVD > 0.05), got TVD={tvd}"
    )


# --- Case 3: HARD-02 cross-check -- NoiseModel vs LC on a shared toy circuit


def _noise_model_toy_probs(eta):
    proc = pcvl.Processor(
        "SLOS", pcvl.Circuit(2), noise=pcvl.NoiseModel(transmittance=eta)
    )
    proc.min_detected_photons_filter(0)
    proc.with_input(pcvl.BasicState("|1,0>"))
    res = proc.probs()
    return {str(state): float(p) for state, p in res["results"].items()}


def _lc_toy_probs(eta):
    proc = pcvl.Processor("SLOS", 2)
    proc.add(0, pcvl.LC(1.0 - eta))
    proc.min_detected_photons_filter(0)
    proc.with_input(pcvl.BasicState("|1,0>"))
    res = proc.probs()
    return {str(state): float(p) for state, p in res["results"].items()}


@pytest.mark.parametrize("eta", [0.5, 0.8])
def test_hard02_noise_model_and_lc_agree_on_shared_toy_circuit(eta):
    """Two independently-implemented Perceval loss mechanisms (NoiseModel's
    source-side Bernoulli-loss formula and LC's beamsplitter-expansion
    formula) agreeing on a case where both are applicable -- NOT a
    same-pipeline-computed-two-ways check, since only LC works end-to-end on
    this project's real polarization circuits (18-RESEARCH.md Pitfall 1)."""
    probs_noise_model = _noise_model_toy_probs(eta)
    probs_lc = _lc_toy_probs(eta)

    keys = set(probs_noise_model) | set(probs_lc)
    for k in keys:
        assert abs(probs_noise_model.get(k, 0.0) - probs_lc.get(k, 0.0)) <= 1e-9

    if eta == 0.5:
        # 18-RESEARCH.md's own verified spot-check value.
        assert abs(probs_noise_model.get("|0,0>", 0.0) - 0.5) <= 1e-9
        assert abs(probs_noise_model.get("|1,0>", 0.0) - 0.5) <= 1e-9
