"""Weight-1 photon-loss distribution function (Phase 18, HARD-01/HARD-02).

Applies uniform per-mode transmittance loss via pcvl.LC component insertion
-- NEVER via the noise=NoiseModel(transmittance=eta) Processor constructor
parameter, which is confirmed (18-RESEARCH.md Pitfall 1) to silently no-op
for this project's polarization-annotated circuits (ENC-01, locked since
Phase 9) -- on top of the existing weight-1 ENC-01 pipeline in
iqp_photonic_encoding.py.
"""

import perceval as pcvl

from merlin_iqp.encoding.iqp_photonic import build_full_circuit, all_h_input, fock_to_bitstring


def photonic_iqp_distribution_lossy(n, thetas, eta=1.0):
    """Weight-1 IQP photonic distribution under uniform per-mode photon loss.

    eta in [0.0, 1.0]: transmittance (eta=1.0 lossless, eta=0.0 total loss).
    Builds a Processor(2n), inserts pcvl.LC(1.0 - eta) on every one of the 2n
    modes BEFORE build_full_circuit(n, thetas). Front-loading LC (rather than
    distributing it through the circuit) is exact, not a simplification with
    hidden risk: uniform per-mode loss commutes with any passive
    linear-optical unitary, and every component in build_full_circuit (state
    prep, diagonal layer, conjugation, PBS readout) is passive/photon-number
    -preserving -- 18-RESEARCH.md Architecture Patterns, matching Park & Oh's
    own stated commutation fact (arXiv:2510.24137 Sec. II.B).

    Calls proc.min_detected_photons_filter(0) EXPLICITLY (18-RESEARCH.md
    Pitfall 2 -- MUST NOT be omitted or left to the default: Processor's
    automatic filter only inspects NoiseModel, has no knowledge of LC
    components, and silently defaults to a filter that excludes every lossy
    branch, producing a plausible-looking but loss-invariant "normalized"
    result -- tests/test_loss_model.py's dedicated regression test
    demonstrates this failure mode is real, not just avoided).

    Returns (dist, residual, global_perf, partial_loss):
      - dist: {bitstring: probability} over in-subspace outcomes, same shape
        as photonic_iqp_distribution's dist.
      - residual: total probability on out-of-subspace outcomes -- now
        genuinely includes lost-photon branches (a (0,0) mode pair), not
        just the near-zero-residual case the lossless function documents.
        fock_to_bitstring already returns None for these -- no new decode
        logic needed.
      - global_perf: Processor.probs()'s own true survival-probability
        report. Do not infer survival from sum(dist.values()) alone -- a
        buggy pipeline that omits min_detected_photons_filter(0) can look
        loss-invariant in dist/residual while global_perf still correctly
        reflects the true loss (18-RESEARCH.md Pitfall 2's warning sign).
      - partial_loss: {str(state): probability}, the per-pattern decomposition
        of residual, keyed by the raw Fock state's string representation.
        Added for REFRAME-02 -- returned but not analyzed in this milestone.
    """
    if not (0.0 <= eta <= 1.0):
        raise ValueError(f"eta must be in [0.0, 1.0], got {eta!r}")

    loss = 1.0 - eta
    total_modes = 2 * n
    proc = pcvl.Processor("SLOS", total_modes)
    for m in range(total_modes):
        proc.add(m, pcvl.LC(loss))
    proc.add(0, build_full_circuit(n, thetas))
    proc.min_detected_photons_filter(0)
    proc.with_input(all_h_input(n))
    res = proc.probs()

    dist = {}
    residual = 0.0
    partial_loss = {}
    for state, prob in res["results"].items():
        p = float(prob)
        bits = fock_to_bitstring(state, n)
        if bits is None:
            residual += p
            partial_loss[str(state)] = partial_loss.get(str(state), 0.0) + p
        else:
            dist[bits] = dist.get(bits, 0.0) + p

    return dist, residual, float(res["global_perf"]), partial_loss
