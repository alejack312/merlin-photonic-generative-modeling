"""Weight-2 (heralded_cz) LC-based photon-loss distribution function (Phase 18
Plan 03, HARD-07): the ancilla-inclusive herald-failure/transmission-loss
compounding primitive every later loss-sweep number in this phase traces
back to.

Photon loss is applied via pcvl.LC(1-eta) component insertion into a
Processor -- NEVER via the noise=NoiseModel(...) constructor parameter,
which is confirmed to silently no-op for this project's polarization-
annotated circuits (18-RESEARCH.md Pitfall 1, re-confirmed for weight-2 by
this plan's own tests, not assumed carried over from Plan 18-02's weight-1
tests). LC is front-loaded onto every one of the 2n+2 modes -- including the
2 heralded_cz ancilla modes (2n, 2n+1), not just the 2n data-carrying modes
-- BEFORE state prep, the diagonal layer, the CZ insertion, conjugation, and
readout: exactly equivalent to distributing loss throughout the circuit,
since every one of those downstream components is passive/photon-number-
preserving (18-RESEARCH.md's commutation argument, sourced from Park & Oh
arXiv:2510.24137 Sec. II.B). 18-CONTEXT.md's locked HARD-07 decision: this
is the ONLY mechanism by which loss can be seen degrading the herald
mechanism itself, not just the post-herald data readout.

proc.min_detected_photons_filter(0) is called explicitly -- omitting it
(18-RESEARCH.md Pitfall 2) silently discards every lossy branch, pinning
herald_failure_prob at the lossless 2/27 baseline regardless of eta. This
module's own test suite (tests/test_loss_model_weight2.py) demonstrates that
failure mode live via a deliberately-broken local helper, not just avoids it.

Herald failure and transmission loss are measured by running the REAL
heralded_cz pipeline through ONE Processor.probs() call per (n, i, j,
thetas, eta) cell -- never by analytically multiplying the lossless 2/27
herald-success rate by a separately-computed loss-survival probability, per
18-CONTEXT.md's explicit lock. The existing residual/herald-failure
bucketing convention from photonic_weight2_iqp_distribution generalizes to
loss with NO new decode logic: fock_to_bitstring/_decode_single_qubit_pair
already return None (-> residual) for a (0,0) lost-photon mode pair.
"""

import numpy as np
import perceval as pcvl

from iqp_photonic_encoding import (
    build_cz_insertion,
    build_state_prep_circuit,
    build_diagonal_layer_circuit,
    build_conjugation_circuit,
    build_readout_circuit,
    _weight2_input_state,
    fock_to_bitstring,
)


def _build_weight2_processor_lossy(n, i, j, thetas, eta):
    """Builds the LC-loss weight-2 Processor -- state prep -> theta-folded
    diagonal layer -> build_cz_insertion(n, i, j) via the SAME mode-mapping
    dict _build_weight2_processor_no_herald uses -> conjugation -> readout
    -- with pcvl.LC(1-eta) front-loaded on all 2n+2 modes (the 2n data modes
    AND the 2 tail herald ancilla modes) before any other component, and
    proc.min_detected_photons_filter(0) called explicitly. NO add_herald()
    call (Pitfall 3, inherited from _build_weight2_processor_no_herald: PBS
    + add_herald crashes Processor.probs() unless every herald mode is also
    supplied to with_input(), which this function's caller does via
    _weight2_input_state's {P:V} annotation) -- the caller classifies
    ancilla-mode outcomes by hand, exactly as the lossless function already
    does.

    Reuses build_cz_insertion's own wiring and mode-mapping dict verbatim
    (never re-derived) so this loss-sweep path can never silently drift from
    what build_weight2_processor/_build_weight2_processor_no_herald actually
    ship. Since _build_weight2_processor_no_herald builds its OWN fresh
    Processor, this function cannot simply call it and prepend LC -- its
    internal .add() sequence is replicated here onto a Processor that
    already has LC on every mode from construction (mirroring Plan 18-02's
    front-loaded weight-1 pattern).

    Returns (proc, herald_spec) -- proc exposes all 2n+2 modes (heralds not
    registered); herald_spec's keys are build_cz_insertion's own LOCAL
    indices (4, 5), read from build_cz_insertion's own returned value (never
    hardcoded)."""
    assert len(thetas) == n
    assert 0 <= i < n and 0 <= j < n and i != j

    loss = 1.0 - eta

    # Additive pi/4 folding, exactly matching
    # _build_weight2_processor_no_herald's own convention -- never mutate
    # the caller's list.
    thetas_folded = list(thetas)
    thetas_folded[i] += np.pi / 4
    thetas_folded[j] += np.pi / 4

    total_modes = 2 * n + 2  # 2n data modes + 2 tail herald ancilla modes
    proc = pcvl.Processor("SLOS", total_modes)

    # Front-load LC on EVERY mode -- data modes AND both ancilla modes --
    # before any other component. This is HARD-07's ancilla-inclusive
    # requirement (module docstring above).
    for m in range(total_modes):
        proc.add(m, pcvl.LC(loss))

    proc.add(0, build_state_prep_circuit(n))
    proc.add(0, build_diagonal_layer_circuit(n, thetas_folded))

    cz_circuit, herald_spec = build_cz_insertion(n, i, j)
    mapping = {
        2 * i: 0, 2 * i + 1: 1,      # qubit i's ports -> build_cz_insertion's local (0,1)
        2 * j: 2, 2 * j + 1: 3,      # qubit j's ports -> build_cz_insertion's local (2,3)
        2 * n: 4, 2 * n + 1: 5,      # tail ancilla modes -> build_cz_insertion's local herald ports
    }
    proc.add(mapping, cz_circuit)

    proc.add(0, build_conjugation_circuit(n))
    proc.add(0, build_readout_circuit(n))

    proc.min_detected_photons_filter(0)  # Pitfall 2 -- MUST be explicit, never omitted

    return proc, herald_spec


def photonic_weight2_iqp_distribution_lossy(n, i, j, thetas, eta=1.0):
    """The weight-2 loss-sweep core function (HARD-07's central primitive):
    physical photon loss compounded with heralded_cz's own herald-failure
    probability, run through the real pipeline in ONE Processor.probs()
    call so the two failure modes interact as they physically would --
    never an analytical multiplication of a separately-computed lossless
    2/27 herald rate against a separately-computed loss-survival
    probability (18-CONTEXT.md's explicit, locked decision).

    Builds _build_weight2_processor_lossy(n, i, j, thetas, eta) (which folds
    +pi/4 onto thetas[i]/thetas[j] internally, exactly as the lossless
    photonic_weight2_iqp_distribution does), runs proc.probs() on the
    {P:V}-annotated ancilla input from _weight2_input_state, and classifies
    every returned (state, prob) pair using the EXACT SAME loop shape
    photonic_weight2_iqp_distribution already uses:
      - ancilla mode mismatch (vs herald_spec) -> herald_failure_prob
      - ancilla match but fock_to_bitstring(state, n) is None -> residual
      - otherwise -> dist[bitstring]
    dist/residual are renormalized by dividing by herald_success_prob = 1.0
    - herald_failure_prob (conditioned-on-herald-success reporting, matching
    the existing lossless function's convention and 18-CONTEXT.md's explicit
    HARD-07 lock); herald_failure_prob itself is reported as a separate,
    un-renormalized number, never merged into residual.

    Returns (dist, residual, herald_failure_prob, global_perf) -- a 4-tuple:
    the lossless function's existing 3-tuple convention, plus global_perf
    (Processor.probs()'s own reported physical_perf * logical_perf) appended
    as a genuinely new quantity this lossy variant needs to report. NOTE
    (18-RESEARCH.md Pitfall 4): global_perf alone conflates loss-driven and
    herald-driven attrition into one scalar -- callers needing herald-rate-
    vs-eta specifically must use herald_failure_prob, not global_perf.

    eta=1.0 (the default) reproduces photonic_weight2_iqp_distribution's
    output bit-for-bit (LC(0) is a genuine identity, proven by this module's
    own test suite, not assumed)."""
    if not (0.0 <= eta <= 1.0):
        raise ValueError(f"eta must be in [0.0, 1.0], got {eta}")

    proc, herald_spec = _build_weight2_processor_lossy(n, i, j, thetas, eta)
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
