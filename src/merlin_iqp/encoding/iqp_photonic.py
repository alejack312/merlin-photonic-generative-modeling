"""ENC-01: IQP -> photonic (DV/Fock-space) encoding, polarization scheme.

The core encoding shared by every other subpackage in ``merlin_iqp``: maps
an IQP-style qubit circuit (Hadamard state prep, a diagonal weight-1/weight-2
phase layer, Hadamard conjugation, computational-basis readout) onto a
photonic Fock-space circuit, one photon per qubit, H/V polarization carrying
the qubit basis. Not wrappable by MerLin's ``QuantumLayer`` (which rejects
polarization-annotated ``BasicState`` inputs outright) -- used with direct
Perceval ``Processor``/``Simulator`` calls instead. See
:mod:`merlin_iqp.encoding.dual_rail` for the QuantumLayer-compatible,
polarization-free re-encoding of the same circuit family.
"""

import perceval as pcvl
import numpy as np

from perceval.utils import allstate_iterator
from perceval.components.core_catalog.heralded_cz import HeraldedCzItem
from perceval.components.core_catalog.controlled_rotation_gates import (
    PostProcessedControlledRotationsItem,
)

# ENC-01: IQP -> photonic (DV/Fock-space) encoding, polarization scheme.
#
# Chosen scheme (owner's attempt, Task 1 checkpoint of 09-01-PLAN.md): polarization
# encoding, one photon per qubit, H/V polarization carries the qubit basis
# (|0> = |H>, |1> = |V>). See docs/iqp-photonic-encoding.md's "Owner's Attempt"
# section for the full Q&A this module implements.
#
# Layout convention: each qubit k occupies 2 adjacent spatial modes, port
# 2*k (the polarization-carrying mode) and port 2*k+1 (a vacuum partner mode,
# only used at readout). n qubits -> 2n total modes.
#
# Perceval API facts this relies on (verified against installed
# perceval-quandela==1.2.4 by direct source/behavior inspection, not assumed):
#   - pcvl.WP(delta, xsi) has unitary (from perceval/components/unitary_components.py):
#       [[cos(delta)+i*sin(delta)*cos(2*xsi),   i*sin(delta)*sin(2*xsi)],
#        [i*sin(delta)*sin(2*xsi),               cos(delta)-i*sin(delta)*cos(2*xsi)]]
#     At xsi=0 this is exactly diag(e^{i*delta}, e^{-i*delta}) -- confirmed
#     numerically via wp.compute_unitary(). This is the polarization analogue
#     of PS/Rz: an exact Z-diagonal phase gate, no approximation.
#   - pcvl.HWP(xsi) is WP(delta=pi/2, xsi) (confirmed from HWP.__init__ source).
#     At xsi=pi/8, its unitary is i * (1/sqrt(2)) * [[1,1],[1,-1]] -- the real
#     Hadamard matrix up to the global phase i (confirmed numerically). Global
#     phase is unobservable, so HWP(pi/8) *is* Hadamard on the polarization qubit.
#   - pcvl.PBS() converts a polarization superposition on 1 spatial mode into
#     the same superposition spread across 2 plain spatial modes (and back) --
#     confirmed empirically: HWP(pi/8) on |H> then PBS gives an exact 50/50
#     split across the 2 output modes, matching |+> measured in the
#     computational basis.
#   - A bare polarized BasicState run through Analyzer with no PBS conversion
#     does not resolve H/V in the output distribution (confirmed empirically --
#     Analyzer collapses it to a single "photon present" outcome). PBS is
#     required before Analyzer/Processor.probs() can report which polarization
#     state was measured, in the same way perceval_fluency_demo.py's PS
#     needed a second beamsplitter to become visible.
#   - Empirically confirmed port<->polarization convention (verified via a
#     bare PBS with no other gates, pure |H> and pure |V> input): output pair
#     (0,1) = H, output pair (1,0) = V. (An earlier version of this module
#     had this backwards -- self-consistent within its own H/V labels, so it
#     didn't affect any numerical test result, but the labels didn't match
#     true physical polarization. Corrected in Plan 09-02 after the owner's
#     ENC-03 attempt prompted a direct check.) Combined with the abstract
#     derivation HWP(pi/8)->WP(theta,0)->HWP(pi/8) = Had.diag(e^{i*theta},
#     e^{-i*theta}).Had = [[cos(theta), i*sin(theta)],[i*sin(theta),
#     cos(theta)]], and this port<->polarization convention, the readout
#     probabilities are P(H port=(0,1)) = cos^2(theta), P(V port=(1,0)) =
#     sin^2(theta).
#
# Generator-weight scope (stated limitation, per 09-01-PLAN.md Task 2): these
# functions implement and test weight-1 (single-qubit) IQP generators only.
# A weight->=2 generator (e.g. exp(i*theta*Z_i*Z_j)) is derived on paper in
# docs/iqp-photonic-encoding.md via PBS-mediated conversion to dual rail +
# core_catalog.heralded_cz + PBS back, using the operator identity
#   CZ = exp(i*pi/4 * (I - Z_i - Z_j + Z_i*Z_j))
# i.e. CZ realizes exp(i*pi/4*Z_i*Z_j) up to single-qubit Z-phase corrections
# (which WP(theta,0) already gives) -- but only at that fixed angle pi/4, since
# the catalog's heralded_cz is a fixed (non-continuously-parameterized) gate.
# Not implemented here: building and testing the actual heralded ancilla/
# herald-detection circuit is out of scope for this plan's runnable code.

QUBIT_PI_8 = np.pi / 8  # HWP angle realizing Hadamard (up to global phase)


def build_state_prep_circuit(n):
    """|+>^{tensor n} analogue: HWP(pi/8) on each qubit's polarization mode,
    turning each qubit's |H> input into (|H>+|V>)/sqrt(2). Returns a
    Circuit(2n); odd-indexed (vacuum-partner) modes are untouched."""
    circuit = pcvl.Circuit(2 * n)
    for k in range(n):
        circuit.add(2 * k, pcvl.HWP(QUBIT_PI_8))
    return circuit


def build_diagonal_layer_circuit(n, thetas):
    """Z-diagonal middle layer, weight-1 generators only: WP(thetas[k], 0) on
    qubit k's polarization mode realizes exp(i*thetas[k]*Z_k) exactly (no
    approximation -- WP(delta, xsi=0) = diag(e^{i*delta}, e^{-i*delta})).
    thetas: sequence of length n; thetas[k] = 0.0 means no generator acts on
    qubit k (WP(0,0) = identity). Returns a Circuit(2n)."""
    assert len(thetas) == n
    circuit = pcvl.Circuit(2 * n)
    for k in range(n):
        circuit.add(2 * k, pcvl.WP(thetas[k], 0))
    return circuit


def build_conjugation_circuit(n):
    """Hadamard-conjugation: same HWP(pi/8) as state prep (Hadamard is its own
    inverse), applied to each qubit's polarization mode. Returns a Circuit(2n)."""
    circuit = pcvl.Circuit(2 * n)
    for k in range(n):
        circuit.add(2 * k, pcvl.HWP(QUBIT_PI_8))
    return circuit


def build_readout_circuit(n):
    """Converts each qubit's polarization state into a which-path (dual-rail-
    like) spatial state via PBS, so Analyzer/Processor.probs() can resolve H
    vs V. Required before measurement -- a bare polarized state is invisible
    to Fock-basis (photon-number) measurement, the polarization analogue of
    perceval_fluency_demo.py's bare-PS-is-invisible result. Returns a
    Circuit(2n)."""
    circuit = pcvl.Circuit(2 * n)
    for k in range(n):
        circuit.add(2 * k, pcvl.PBS())
    return circuit


def _build_cz_insertion_core():
    """The PERM-adapted heralded_cz sub-wiring only -- dual-rail in, dual-rail
    out, local Circuit(6), no PBS -- factored out of build_cz_insertion so
    the ctrl/data swap fix's phase behavior is directly testable via
    Simulator/SLOSBackend (tests/test_iqp_photonic_encoding.py).

    Perceval's SLOSBackend refuses circuits containing PBS
    (`Circuit.requires_polarization` -- confirmed empirically: `assert not
    circuit.requires_polarization` in perceval/backends/_slos.py), so
    build_cz_insertion's full PBS-wrapped circuit cannot be handed to
    Simulator directly. This core is the exact same PERM->heralded_cz->PERM
    wiring build_cz_insertion embeds (identical `circuit.add` calls, just
    without the surrounding PBS steps) -- not a re-derivation -- so testing
    it here genuinely exercises build_cz_insertion's own logic. Combined
    with the fact that a bare PBS deterministically maps a pure (non-
    superposed) computational-basis polarization input to its dual-rail
    counterpart with amplitude exactly 1 and no extra phase (confirmed
    empirically against a standalone PBS circuit; also implicit in Plan
    09-02's port-convention measurement and this suite's existing
    `test_enc03_round_trip` checks), this core's dual-rail truth table IS
    build_cz_insertion's polarization-basis truth table."""
    circuit = pcvl.Circuit(6)
    circuit.add(0, pcvl.PERM([1, 0]))  # Convention adapter (11-RESEARCH.md Pitfall 1), not a bug fix:
                                        # heralded_cz uses Perceval's own Encoding.DUAL_RAIL standard
                                        # (logical 1 -> Fock pattern (0,1), per port.py), which is the
                                        # mirror image of this module's PBS-derived convention (H/bit "0"
                                        # -> (0,1), Plan 09-02, from measured physical PBS behavior).
                                        # Both conventions are independently correct; without this swap,
                                        # the CZ's -1 phase lands on |0,0> instead of |1,1>. Verified by
                                        # direct execution (11-RESEARCH.md "Pitfall 1").
    circuit.add(2, pcvl.PERM([1, 0]))  # same adapter for qubit j's pair
    item = HeraldedCzItem()
    circuit.add(0, item.build_circuit())  # bare 6-mode heralded_cz: ctrl=local(0,1), data=local(2,3), herald=local(4,5)
    circuit.add(0, pcvl.PERM([1, 0]))  # swap back: undo the ctrl-side relabeling so this function's own
                                        # local port 0 is still "qubit i's polarization port" for the caller
    circuit.add(2, pcvl.PERM([1, 0]))  # swap back for qubit j
    return circuit


def build_cz_insertion(n, i, j):
    """Weight-2 CZ insertion unit (Phase 11, ROADMAP Success Criterion 1):
    wraps qubit i's and qubit j's polarization ports into dual rail via PBS,
    routes them through the catalog's heralded_cz gate, then unwraps back to
    polarization -- realizing CZ = diag(1,1,1,-1) on this module's own
    port/bit convention.

    Builds a LOCAL, self-contained Circuit(6) (not sized to the outer
    2n-mode register -- the caller wires it into the full circuit via a
    mode-mapping dict in Plan 11-02). Local layout, matching heralded_cz's
    own numbering:
      local 0 = qubit i's polarization-carrying port (this module's normal
                convention)
      local 1 = qubit i's vacuum-partner port
      local 2 = qubit j's polarization-carrying port
      local 3 = qubit j's vacuum-partner port
      local 4, 5 = herald ancilla, owned entirely by heralded_cz

    Convention adapter, not a bug fix (11-RESEARCH.md Pitfall 1, confirmed
    by direct execution against this repo's venv): heralded_cz's ctrl/data
    ports use Perceval's own Encoding.DUAL_RAIL standard (logical 1 ->
    Fock pattern (0,1), per port.py), which is the mirror image of this
    module's own PBS-derived convention (H/bit '0' -> (0,1), Plan 09-02,
    derived from measuring physical PBS behavior with real H/V input).
    Both conventions are independently correct -- they simply weren't
    chosen to agree, since one is a physics-driven polarization convention
    and the other is an abstract qubit-encoding standard with no reason to
    match it. Without the swap below, the CZ's -1 phase lands on |0,0>
    instead of |1,1>. The fix is a PERM([1,0]) on each qubit's dual-rail
    pair immediately before heralded_cz, undone immediately after, so this
    function's own external contract (ports in this module's normal order
    in, correctly-signed CZ out) stays simple -- the swap never leaks into
    a caller's mode-mapping dict.

    herald_spec is read from HeraldedCzItem().build_experiment().in_heralds
    (NOT hardcoded, matching heralded_cz_derisking.py's measure_cz_phase
    pattern) -- expected {4: 1, 5: 1}, local indices into this function's
    own Circuit(6), since heralded_cz's bare circuit is added at local
    offset 0.

    n, i, j are accepted for interface symmetry with the other build_*
    functions and to validate 0 <= i, j < n, i != j; the circuit body
    itself is always a fixed local Circuit(6).

    Returns (Circuit(6), herald_spec)."""
    assert 0 <= i < n and 0 <= j < n and i != j

    circuit = pcvl.Circuit(6)
    circuit.add(0, pcvl.PBS())        # wrap qubit i: polarization -> dual rail, local (0,1)
    circuit.add(2, pcvl.PBS())        # wrap qubit j: polarization -> dual rail, local (2,3)
    circuit.add(0, _build_cz_insertion_core())  # PERM-adapted heralded_cz, local (0..5)
    circuit.add(0, pcvl.PBS())        # unwrap qubit i: dual rail -> polarization, local (0,1)
    circuit.add(2, pcvl.PBS())        # unwrap qubit j: dual rail -> polarization, local (2,3)

    herald_spec = HeraldedCzItem().build_experiment().in_heralds  # not hardcoded -- fails loudly if heralded_cz's layout ever changes
    return circuit, herald_spec


def _build_cp_insertion_core(alpha):
    """The PERM-adapted PostProcessedControlledRotationsItem (CP(alpha))
    sub-wiring only -- dual-rail in, dual-rail out, local Circuit(8), no
    PBS -- mirroring _build_cz_insertion_core's exact structure (Phase 11)
    for the CP(alpha) gate family instead of the fixed heralded_cz.

    alpha (CP's own raw dial, a plain Python float per
    PostProcessedControlledRotationsItem.build_circuit's isinstance check --
    cast at every call site, matching this repo's established
    numpy.float64-breaks-Perceval discipline, STATE.md) is DIFFERENT from
    theta (this codebase's Z_iZ_j generator-angle convention, matching
    pair_thetas={(i,j): theta} in exact_qubit_iqp_distribution): related by
    alpha = 4*theta (15-RESEARCH.md's confirmed general operator identity,
    CP(4*phi).WP(phi,0)_i.WP(phi,0)_j = e^{i*phi}*exp(i*phi*Z_i*Z_j)).
    alpha=pi corresponds to theta=pi/4, the existing Z_iZ_j-generator
    boundary this codebase's pair_thetas already uses for the fixed
    heralded_cz construction -- NOT alpha=pi/4, per 15-CONTEXT.md's
    owner-confirmed correction (15-01-SUMMARY.md/cp_gate_derisking.py
    independently confirmed alpha=pi, not alpha=pi/4, reproduces
    heralded_cz's diag(1,1,1,-1) sign-for-sign).

    Convention adapter, not a bug fix (same class of fix as
    _build_cz_insertion_core's, 11-RESEARCH.md Pitfall 1, confirmed by
    direct execution in this plan's own de-risking pass, 15-RESEARCH.md
    Open Question 2): PostProcessedControlledRotationsItem also registers
    ports via Perceval's own Encoding.DUAL_RAIL standard (confirmed from
    source, 15-RESEARCH.md), the mirror image of this module's own
    PBS-derived convention. Step 1 of this plan (the direct analog of
    _build_cz_insertion_core's fix -- PERM([1,0]) on each qubit's own
    dual-rail pair, local (0,1) and local (2,3), immediately before and
    after the bare CP circuit, swap-back after) reproduces the target
    truth table exactly on this module's own MODULE_DUAL_RAIL convention,
    confirmed via Simulator.prob_amplitude at alpha=pi (matches
    _build_cz_insertion_core's diag(1,1,1,-1) sign-for-sign) and at
    alpha=pi/3 (matches diag(1,1,1,e^{i*pi/3})'s magnitude/phase pattern)
    -- no Step 2/3 fallback search was needed, unlike 15-RESEARCH.md's
    full-pipeline attempt (which had PBS/state-prep/conjugation/readout
    confounds this isolated bare-core context removes).

    n=2 for a 2-qubit CP gate (PostProcessedControlledRotationsItem's own
    "number of qubits of the gate" parameter, confirmed in
    15-RESEARCH.md/cp_gate_derisking.py -- NOT "number of controls"),
    giving a bare Circuit(8): local (0,1) = qubit i's dual-rail pair
    ("ctrl0" port), local (2,3) = qubit j's dual-rail pair ("data" port),
    local (4..7) = ancilla, ALL held at vacuum on both ends (a
    post-selected, not heralded, construction -- structurally different
    from heralded_cz's 6-mode/2-heralded-photon-ancilla construction, per
    15-CONTEXT.md/15-RESEARCH.md's explicit "post-selection + ancilla
    vacuum" vs. "ancilla heralding" mechanism distinction)."""
    circuit = pcvl.Circuit(8)
    circuit.add(0, pcvl.PERM([1, 0]))  # Convention adapter (15-RESEARCH.md Open Question 2 /
                                        # Pitfall 2), not a bug fix -- same class of fix as
                                        # _build_cz_insertion_core's (11-RESEARCH.md Pitfall 1):
                                        # PostProcessedControlledRotationsItem uses Perceval's own
                                        # Encoding.DUAL_RAIL standard (mirror image of this module's
                                        # PBS-derived convention). Verified by direct execution during
                                        # this plan's isolated bare-core de-risking pass.
    circuit.add(2, pcvl.PERM([1, 0]))  # same adapter for qubit j's pair
    item = PostProcessedControlledRotationsItem()
    circuit.add(0, item.build_circuit(n=2, alpha=float(alpha)))  # bare 8-mode CP(alpha):
                                        # ctrl=local(0,1), data=local(2,3), ancilla=local(4..7)
    circuit.add(0, pcvl.PERM([1, 0]))  # swap back: undo the ctrl-side relabeling so this
                                        # function's own local port 0 is still "qubit i's
                                        # polarization port" for the caller
    circuit.add(2, pcvl.PERM([1, 0]))  # swap back for qubit j
    return circuit


def build_cp_insertion(n, i, j, alpha):
    """Weight-2 CP(alpha) insertion unit (Phase 15, ARB-01): wraps qubit i's
    and qubit j's polarization ports into dual rail via PBS, routes them
    through the catalog's PostProcessedControlledRotationsItem gate (via
    _build_cp_insertion_core), then unwraps back to polarization --
    realizing CP(alpha) = diag(1,1,1,e^{i*alpha}) on this module's own
    port/bit convention, mirroring build_cz_insertion's exact external-
    contract pattern (Phase 11) for the tunable CP(alpha) gate family
    instead of the fixed heralded_cz.

    Builds a LOCAL, self-contained Circuit(2n+4) for n=2 -- 4 data modes
    (local 0-3, matching build_cz_insertion's local 0-3 layout) + 4
    ancilla modes (local 4-7). NOT 2 like build_cz_insertion/heralded_cz --
    a structural difference from build_cz_insertion, since
    PostProcessedControlledRotationsItem's n=2 construction uses 4n=8 total
    modes (4 data + 4 ancilla), not heralded_cz's 6 (4 data + 2 herald
    ancilla). Local layout:
      local 0 = qubit i's polarization-carrying port (this module's normal
                convention)
      local 1 = qubit i's vacuum-partner port
      local 2 = qubit j's polarization-carrying port
      local 3 = qubit j's vacuum-partner port
      local 4-7 = ancilla, owned entirely by
                  PostProcessedControlledRotationsItem, ALL vacuum on both
                  ends (post-selection + ancilla vacuum, not heralding --
                  see ancilla_spec below)

    alpha (CP's own raw dial) vs. theta (this codebase's Z_iZ_j
    generator-angle convention): see _build_cp_insertion_core's docstring
    for the full alpha=4*theta disambiguation.

    ancilla_spec is read from PostProcessedControlledRotationsItem().
    build_experiment().in_heralds (NOT hardcoded, matching
    build_cz_insertion's pattern of reading herald_spec from the item's
    own build_experiment() rather than assuming) -- expected {4: 0, 5: 0,
    6: 0, 7: 0}, local indices into this function's own Circuit(2n+4),
    since the bare CP circuit is added at local offset 0. Named
    ancilla_spec, NOT herald_spec, because its meaning is fundamentally
    different from heralded_cz's herald_spec: every value here is an
    EXPECTED PHOTON COUNT OF 0 (vacuum both ends -- a post-selection
    condition on the ancilla modes staying empty), not a 1-photon herald
    count (per 15-CONTEXT.md/15-RESEARCH.md's explicit "post-selection +
    ancilla vacuum" [CP] vs. "ancilla heralding" [heralded_cz] mechanism
    distinction, which ARB-05 requires stating plainly).

    n, i, j are accepted for interface symmetry with the other build_*
    functions and to validate 0 <= i, j < n, i != j; the circuit body
    itself is always a fixed local Circuit(8).

    Returns (Circuit(8), ancilla_spec)."""
    assert 0 <= i < n and 0 <= j < n and i != j

    circuit = pcvl.Circuit(8)
    circuit.add(0, pcvl.PBS())        # wrap qubit i: polarization -> dual rail, local (0,1)
    circuit.add(2, pcvl.PBS())        # wrap qubit j: polarization -> dual rail, local (2,3)
    circuit.add(0, _build_cp_insertion_core(alpha))  # PERM-adapted CP(alpha), local (0..7)
    circuit.add(0, pcvl.PBS())        # unwrap qubit i: dual rail -> polarization, local (0,1)
    circuit.add(2, pcvl.PBS())        # unwrap qubit j: dual rail -> polarization, local (2,3)

    ancilla_spec = PostProcessedControlledRotationsItem().build_experiment(n=2, alpha=float(alpha)).in_heralds
    # Read from the catalog item, not hardcoded -- but every caller (the
    # mode-mapping dict in _build_weight2_cp_processor_no_postselect and the
    # ancilla_modes list in photonic_cp_iqp_distribution) hardcodes local
    # ports 4-7 directly rather than deriving them from this dict, so the
    # "fails loudly" guarantee needs an explicit assertion here -- without
    # it, a future catalog layout change would silently mask the wrong
    # Fock modes as "ancilla vacuum" instead of raising (caught in review,
    # Phase 15 completion).
    assert ancilla_spec == {4: 0, 5: 0, 6: 0, 7: 0}, (
        f"PostProcessedControlledRotationsItem's ancilla layout changed: {ancilla_spec} "
        "-- every downstream caller hardcodes local ports 4-7, all expecting count 0"
    )
    return circuit, ancilla_spec


def build_weight2_processor(n, i, j, thetas):
    """Full weight-2 IQP generator pipeline (Phase 11, ROADMAP Success
    Criteria 2-4): state prep -> theta-folded diagonal layer -> CZ insertion
    (qubits i, j) -> conjugation -> readout, assembled as a Processor(2n+2)
    via Processor.add() -- every weight-1 builder (build_state_prep_circuit,
    build_diagonal_layer_circuit, build_conjugation_circuit,
    build_readout_circuit) reused completely unmodified, per 11-RESEARCH.md's
    architecture section and this phase's CONTEXT.md-locked decisions.

    Mode layout: 2n+2 total modes. Modes 0..2n-1 are this module's normal
    per-qubit (polarization-port, vacuum-partner-port) pairs (unchanged from
    every other build_* function in this module). Modes 2n, 2n+1 are the 2
    extra herald ancilla modes build_cz_insertion's PBS-wrap ->
    PERM-adapted-heralded_cz -> PBS-unwrap needs -- present in the outer
    Processor from construction (11-RESEARCH.md Pitfall 2:
    Processor.add()'s mode-mapping dict requires every target mode to
    already exist in the processor it's added to).

    Theta folding is additive, not a replacement (CONTEXT.md-locked rule,
    load-bearing for Phase 13's later weight-1+weight-2 mixed-circuit test):
    thetas_folded[k] = thetas[k] + pi/4 for k in {i, j} only, every other
    qubit's theta passes through build_diagonal_layer_circuit unchanged.
    This realizes the CZ/ZZ operator identity documented in
    docs/iqp-photonic-encoding.md: exp(i*pi/4*Z_i*Z_j) = CZ .
    exp(i*pi/4*Z_i) . exp(i*pi/4*Z_j) up to global phase -- the single-qubit
    corrections fold into the SAME thetas argument any weight-1 generator on
    qubits i/j would already be using, not a separate gate.

    build_cz_insertion(n, i, j) (Plan 11-01) is wired in via an explicit,
    straight (unswapped -- the ctrl/data swap fix already lives inside
    build_cz_insertion itself) mode-mapping dict: qubit i's ports (2i,
    2i+1) -> build_cz_insertion's local (0,1), qubit j's ports (2j, 2j+1)
    -> local (2,3), and the outer processor's 2 tail ancilla modes (2n,
    2n+1) -> build_cz_insertion's local herald ports (4,5).
    Processor.add's ModeConnector auto-inserts a PERM before this component
    and its exact inverse after, so the outer processor's mode numbering
    (mode 2i is still "mode 2i") is transparently restored for every .add()
    call that follows -- verified by direct execution in 11-RESEARCH.md,
    not assumed.

    Heralds are registered IMMEDIATELY after that .add() call, using
    build_cz_insertion's own returned herald_spec (never hardcoded 4/5 --
    those are build_cz_insertion's LOCAL indices; the mapping dict above
    sends them to global 2n/2n+1). This is the exact guard ROADMAP Success
    Criterion 3 exists for: composing a bare Circuit (as opposed to an
    Experiment/Processor) never auto-propagates herald metadata
    (Experiment._add_component's plain-component path has no herald logic,
    unlike _compose_experiment) -- forgetting this call would silently
    produce a processor that runs an un-heralded raw unitary with no error.

    Returns a Processor(2n+2) (register size 2n after heralds are
    registered) whose .heralds is non-empty immediately after assembly."""
    assert len(thetas) == n
    assert 0 <= i < n and 0 <= j < n and i != j

    # Additive pi/4 folding -- never mutate the caller's list.
    thetas_folded = list(thetas)
    thetas_folded[i] += np.pi / 4
    thetas_folded[j] += np.pi / 4

    total_modes = 2 * n + 2  # 2n qubit modes + 2 tail herald ancilla modes (11-RESEARCH.md Pitfall 2)
    proc = pcvl.Processor("SLOS", total_modes)

    proc.add(0, build_state_prep_circuit(n))
    proc.add(0, build_diagonal_layer_circuit(n, thetas_folded))

    cz_circuit, herald_spec = build_cz_insertion(n, i, j)
    mapping = {
        2 * i: 0, 2 * i + 1: 1,      # qubit i's ports -> build_cz_insertion's local (0,1)
        2 * j: 2, 2 * j + 1: 3,      # qubit j's ports -> build_cz_insertion's local (2,3)
        2 * n: 4, 2 * n + 1: 5,      # tail ancilla modes -> build_cz_insertion's local herald ports
    }
    proc.add(mapping, cz_circuit)

    # Explicit, immediate herald registration -- Success Criterion 3's guard
    # (see docstring above). herald_spec's keys are build_cz_insertion's own
    # LOCAL indices (4, 5); the global indices they land on via the mapping
    # dict are 2*n and 2*n+1.
    proc.add_herald(2 * n, herald_spec[4])
    proc.add_herald(2 * n + 1, herald_spec[5])

    proc.add(0, build_conjugation_circuit(n))
    proc.add(0, build_readout_circuit(n))
    return proc


def _build_weight2_processor_no_herald(n, i, j, thetas):
    """Phase 12 (WT2-03): identical wiring to build_weight2_processor (state
    prep -> theta-folded diagonal layer -> build_cz_insertion via the SAME
    mode-mapping dict -> conjugation -> readout) but WITHOUT calling
    proc.add_herald(...) -- confirmed crash (12-RESEARCH.md Pitfall 3):
    add_herald + PBS -> Processor.probs() raises a ValueError (matmul shape
    mismatch inside PolarizationSimulator._prepare_input), unconditionally,
    independent of thetas, state_prep, or ancilla annotation.

    Deliberately reuses build_cz_insertion's own wiring and mode-mapping
    dict rather than re-deriving it, so this measurement path can never
    silently drift from what build_weight2_processor actually ships
    (12-RESEARCH.md's explicit "Don't Hand-Roll" guidance).

    Returns (proc, herald_spec) -- proc exposes all 2n+2 modes (heralds not
    registered); the caller must post-select on herald_spec by hand."""
    assert len(thetas) == n
    assert 0 <= i < n and 0 <= j < n and i != j

    thetas_folded = list(thetas)
    thetas_folded[i] += np.pi / 4
    thetas_folded[j] += np.pi / 4

    total_modes = 2 * n + 2
    proc = pcvl.Processor("SLOS", total_modes)

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
    return proc, herald_spec


def _weight2_input_state(n, herald_spec):
    """Phase 12 (WT2-03): builds the pcvl.BasicState input for
    _build_weight2_processor_no_herald's processor -- all_h_input(n)'s
    '{P:H},0' pattern for the n qubit ports, PLUS the two herald ancilla
    ports EXPLICITLY annotated '{P:V}' (not bare integers, not '{P:H}').
    Perceval's silent default for an unannotated/bare-integer photon is
    '{P:H}', which is confirmed WRONG here (gives a silently-wrong, non-
    crashing herald-conditioned distribution -- TVD~0.46 at the locked n=2,
    theta=pi/4 gate); '{P:V}' is confirmed CORRECT, matching a trusted
    PBS-free ground truth to TVD~1e-16 (12-RESEARCH.md Steps 3-4, Pitfall 2).

    herald_spec's photon-count values are always 1 in this project (read
    from heralded_cz's own in_heralds, per build_cz_insertion) -- the
    annotation string is still built generically off the count rather than
    hardcoding '1', in case that ever changes."""
    parts = ["{P:H},0"] * n
    parts.append("{P:V}" if herald_spec[4] else "0")
    parts.append("{P:V}" if herald_spec[5] else "0")
    return pcvl.BasicState("|" + ",".join(parts) + ">")


def photonic_weight2_iqp_distribution(n, i, j, thetas):
    """Phase 12 (WT2-03), the weight-2 analogue of photonic_iqp_distribution.

    Builds _build_weight2_processor_no_herald(n, i, j, thetas) (which folds
    +pi/4 onto thetas[i]/thetas[j] internally, exactly as
    build_weight2_processor does -- pair_theta is NOT a caller-supplied
    parameter here, since the CZ/ZZ operator identity this pipeline realizes
    is only exact at pi/4; any other fold would produce numerically-valid
    but physically-meaningless output, per 12-RESEARCH.md's explicit
    recommendation), runs .probs() via Analyzer on the {P:V}-annotated
    ancilla input from _weight2_input_state, and for each output state:
      - if the two ancilla output modes do NOT match herald_spec's expected
        photon pattern, that probability is counted into herald_failure_prob.
      - if they DO match, the ancilla modes are stripped and the remaining
        2n qubit modes are decoded via fock_to_bitstring: None (out-of-
        subspace) goes to residual, otherwise into dist[bitstring].
    dist and residual are then both renormalized by dividing by
    (1 - herald_failure_prob), so dist is reported CONDITIONAL on herald
    success (matching photonic_iqp_distribution's existing convention of
    only reporting valid in-subspace outcomes, now also conditioned on
    herald success), and sum(dist.values()) + residual == 1.0.

    Returns (dist, residual, herald_failure_prob) -- a 3-tuple per
    CONTEXT.md's locked reporting rule: herald_failure_prob is a separate
    number from residual, NEVER merged into it and NEVER silently
    renormalized away.

    Expected herald_failure_prob at the pi/4 fold: ~1 - 2/27 ~ 0.9259,
    matching Phase 10's established heralded_cz success rate (2/27).
    {P:V} ancilla annotation fix sourced from 12-RESEARCH.md."""
    proc, herald_spec = _build_weight2_processor_no_herald(n, i, j, thetas)
    input_state = _weight2_input_state(n, herald_spec)

    # Explicit output_states (not the "*" string) is deliberate, not cosmetic: Analyzer's
    # "*" path sets processor.min_detected_photons_filter(1) internally, forcing Perceval's
    # SLOS backend to enumerate every partial-photon-count branch down to 1 detected photon.
    # list(allstate_iterator(input_state)) is the exact same output-state set "*" builds
    # (same total-photon-count-conserving enumeration -- verified bit-for-bit identical
    # results at n=3), but taking the explicit-list code path sets the filter to n instead
    # of 1, pruning all those partial-photon branches before the backend even starts. That
    # filter, not output-state-list size, is what was causing MemoryError at n>=5/6 on
    # commodity hardware (confirmed live during Phase 17 gradient-variance sweep execution).
    analyzer = pcvl.algorithm.Analyzer(proc, [input_state], list(allstate_iterator(input_state)))
    analyzer.compute()

    ancilla_a, ancilla_b = 2 * n, 2 * n + 1
    expected_a, expected_b = herald_spec[4], herald_spec[5]

    dist = {}
    residual = 0.0
    herald_failure_prob = 0.0
    for state, prob in zip(analyzer.output_states_list, analyzer.distribution[0]):
        p = complex(prob).real
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

    return dist, residual, herald_failure_prob


def _build_weight2_cp_processor_no_postselect(n, i, j, thetas, alpha):
    """Phase 15 Plan 04 (ARB-03/ARB-04): the CP(alpha)-specific analogue of
    _build_weight2_processor_no_herald -- identical wiring shape (state prep
    -> theta-folded diagonal layer -> weight-2 insertion via a mode-mapping
    dict -> conjugation -> readout), but built around build_cp_insertion
    (Plan 15-02) instead of build_cz_insertion, and with NEITHER
    Processor.add_herald() NOR Processor.set_postselection() called anywhere
    (15-RESEARCH.md Pitfall 3, confirmed by direct execution: CP's
    set_postselection condition raises `AssertionError: Post-selection
    conditions cannot compose with modes [...]` the moment a later component
    -- here, build_conjugation_circuit/build_readout_circuit -- touches the
    same mode indices again). Filtering is deferred entirely to
    photonic_cp_iqp_distribution's manual pass, mirroring the established
    workaround _build_weight2_processor_no_herald already uses for the
    analogous heralded_cz+PBS limitation (12-RESEARCH.md Pitfall 3).

    Mode-count arithmetic (this task's structural warning, verified before
    anything else): build_cp_insertion returns a local Circuit(2n+4) for its
    OWN fixed n=2 (4 data modes + 4 ancilla modes) -- 4 ancilla modes, NOT
    build_cz_insertion's 2. The OUTER processor (sized to this function's own
    n, the outer qubit count, which may be 2 or 3) must therefore be
    total_modes = 2*n + 4 (2n qubit modes + 4 tail ancilla modes), and the
    mode-mapping dict must map all 4 tail ancilla modes (2n, 2n+1, 2n+2,
    2n+3) to build_cp_insertion's local ancilla ports (4, 5, 6, 7) -- a
    4-entry dict, not build_weight2_processor's 2-entry one.

    Theta folding uses the ARB-01/ARB-02 identity derived in
    docs/iqp-photonic-encoding.md (Plan 15-03): exp(i*theta*Z_i*Z_j) =
    e^{-i*theta} * CP(4*theta) * exp(i*theta*Z_i) * exp(i*theta*Z_j), i.e.
    theta = alpha/4 is the single-qubit correction angle added to BOTH
    qubit i's and qubit j's own theta -- additive, never mutating the
    caller's list, matching build_weight2_processor's exact convention.

    Returns (proc, ancilla_spec) -- proc exposes all 2n+4 modes (no
    herald/postselect registered); ancilla_spec's keys are
    build_cp_insertion's own LOCAL indices (4..7), read from
    build_cp_insertion's own returned value (never hardcoded), for the
    caller to filter by hand."""
    assert len(thetas) == n
    assert 0 <= i < n and 0 <= j < n and i != j

    alpha = float(alpha)  # Pitfall 1 (15-RESEARCH.md) -- cast at every call site
    theta = alpha / 4.0

    thetas_folded = list(thetas)
    thetas_folded[i] += theta
    thetas_folded[j] += theta

    total_modes = 2 * n + 4  # 2n qubit modes + 4 tail ancilla modes (build_cp_insertion
                              # has 4 ancilla modes, not build_cz_insertion's 2)
    proc = pcvl.Processor("SLOS", total_modes)

    proc.add(0, build_state_prep_circuit(n))
    proc.add(0, build_diagonal_layer_circuit(n, thetas_folded))

    cp_circuit, ancilla_spec = build_cp_insertion(n, i, j, alpha)
    mapping = {
        2 * i: 0, 2 * i + 1: 1,          # qubit i's ports -> build_cp_insertion's local (0,1)
        2 * j: 2, 2 * j + 1: 3,          # qubit j's ports -> build_cp_insertion's local (2,3)
        2 * n: 4, 2 * n + 1: 5,          # tail ancilla modes -> build_cp_insertion's
        2 * n + 2: 6, 2 * n + 3: 7,      # local ancilla ports (ALL 4, not 2)
    }
    proc.add(mapping, cp_circuit)

    # NO add_herald, NO set_postselection here -- see docstring above
    # (15-RESEARCH.md Pitfall 3). photonic_cp_iqp_distribution filters the
    # ancilla-vacuum condition by hand after .compute().

    proc.add(0, build_conjugation_circuit(n))
    proc.add(0, build_readout_circuit(n))
    return proc, ancilla_spec


def _weight2_cp_input_state(n, ancilla_spec):
    """Phase 15 Plan 04: builds the pcvl.BasicState input for
    _build_weight2_cp_processor_no_postselect's processor -- all_h_input(n)'s
    '{P:H},0' pattern for the n qubit ports, PLUS ALL 4 ancilla ports.

    Unlike heralded_cz's herald ancilla (_weight2_input_state, which needs a
    REAL '{P:V}'-annotated input photon on each herald mode -- Phase 10
    Pitfall 1), CP's ancilla_spec expects photon count 0 at every ancilla
    mode -- vacuum, both ends (post-selection on ancilla vacuum, not
    heralding on a photon click). Confirmed empirically before running the
    full TVD sweep (this task's own verification step, per the plan's
    instruction not to assume the {P:V} fix transfers unchanged): plain bare
    '0' entries (the SAME pattern all_h_input(n) already uses for each
    qubit's own vacuum-partner mode, e.g. the second entry in '{P:H},0') is
    the correct choice here -- a genuinely-vacuum mode needs no polarization
    annotation at all, unlike a mode that must carry a real heralded photon.
    Built as ONE single annotated-BasicState-string pass (15-RESEARCH.md
    Pitfall 5: concatenating a bare-integer list onto an existing BasicState
    via list(existing_state) + [0,0,0,0] silently strips annotations and
    crashes PolarizationSimulator dispatch -- avoided here by building the
    whole '|...>' string in one go, exactly as all_h_input/_weight2_input_state
    already do)."""
    parts = ["{P:H},0"] * n
    parts.extend(["0"] * len(ancilla_spec))  # ancilla_spec always has 4 entries (build_cp_insertion's
                                              # local 4-7), each expecting photon count 0 (vacuum)
    return pcvl.BasicState("|" + ",".join(parts) + ">")


def _decode_single_qubit_pair(state, k):
    """Decodes ONE qubit's (port_2k, port_2k+1) pair only -- '0' for (0,1),
    '1' for (1,0), None for any of the four invalid patterns (same rule
    fock_to_bitstring applies to every qubit at once). Factored out for
    photonic_cp_iqp_distribution's per-pair accounting (see that function's
    docstring for why the (i,j) pair's own validity must be checked
    separately from any bystander qubit's)."""
    a, b = state[2 * k], state[2 * k + 1]
    if (a, b) == (0, 1):
        return "0"
    if (a, b) == (1, 0):
        return "1"
    return None


def photonic_cp_iqp_distribution(n, i, j, thetas, alpha):
    """Phase 15 Plan 04 (ARB-03/ARB-04), the CP(alpha) analogue of
    photonic_weight2_iqp_distribution.

    Builds _build_weight2_cp_processor_no_postselect(n, i, j, thetas, alpha)
    (which folds +alpha/4 onto thetas[i]/thetas[j] internally, per the
    ARB-01/ARB-02 identity -- alpha is a genuine caller-supplied parameter
    here, unlike photonic_weight2_iqp_distribution's fixed +pi/4 fold),
    runs .probs() via Analyzer on the plain-'0'-ancilla input from
    _weight2_cp_input_state, and for each output state applies THREE checks
    in order:
      1. If ANY of the 4 ancilla output modes (2n, 2n+1, 2n+2, 2n+3) is
         non-zero, that probability is counted into postselect_failure_prob.
      2. Otherwise, if qubit i's OR qubit j's own (port_2k, port_2k+1) pair
         is itself outside the single-photon computational subspace
         (bunched/lost -- via _decode_single_qubit_pair), that probability
         is ALSO counted into postselect_failure_prob, not residual.
      3. Otherwise (ancilla vacuum AND both pair-i and pair-j valid), any
         REMAINING bystander qubit (k != i, j) that is itself out-of-
         subspace contributes to residual; if every qubit decodes validly,
         the bitstring goes into dist.

    Why step 2 is folded into postselect_failure_prob, not residual (a
    deliberate correction from this plan's original literal recipe, found
    necessary during this task's own verification pass -- see
    15-04-SUMMARY.md's deviations section): CP's own registered
    post-selection condition inside PostProcessedControlledRotationsItem
    (15-RESEARCH.md's architecture notes) is TWO conditions checked
    together -- ancilla vacuum AND `[0,1]==1 & [2,3]==1` (exactly one
    photon on EACH of CP's own local dual-rail pairs, i.e. qubit i's and
    qubit j's own pair specifically). Since every component between CP and
    the final readout (this module's own PBS-unwrap, HWP conjugation, PBS
    readout) is a passive, per-pair-photon-number-preserving transform --
    confirmed by inspection: HWP is a 1-mode component with zero cross-mode
    coupling, and PBS only ever couples a single qubit's OWN 2-mode pair,
    never a different qubit's -- whether pair i (or pair j) ends up with
    exactly 1 photon at the FINAL readout is mathematically identical to
    whether it had exactly 1 photon immediately after CP's own action.
    Treating that as a bystander-style "residual" (as photonic_weight2_iqp_
    distribution's structurally-similar but physically-different herald
    mechanism does, where residual is always ~0) silently divides dist by
    the wrong denominator: verified empirically that reporting pair-i/pair-j
    invalidity as residual (matching this function's original draft, before
    this fix) produces TVD~0.3-0.4 against the exact reference -- exactly
    the unresolved number 15-RESEARCH.md's own end-to-end attempt hit --
    while folding it into postselect_failure_prob instead reproduces the
    theoretical closed-form success probability p_success(alpha)=1/sigma_max^4
    (docs/iqp-photonic-encoding.md's ARB-02 section) to ~1e-15 and drives
    TVD to floating-point noise level. A genuine bystander qubit (n=3,
    k != i, j) remains unaffected by CP entirely -- its own pair validity
    is independent of pair i/j's, and residual for it is expected to stay
    at ~0, matching this module's established lossless-pipeline convention.

    dist and residual are both renormalized by (1 - postselect_failure_prob),
    matching the existing 3-tuple convention (dist, residual,
    postselect_failure_prob -- three separate, never-merged numbers).

    Returns (dist, residual, postselect_failure_prob) -- postselect_failure_prob
    is named distinctly from herald_failure_prob elsewhere in this module
    (ARB-05's requirement to state the mechanism difference plainly: CP
    succeeds on ancilla VACUUM plus per-pair data validity -- a
    post-selection condition -- not heralded_cz's ancilla photon click).

    Success probability (1 - postselect_failure_prob) VARIES with alpha
    (unlike heralded_cz's fixed 2/27) -- callers needing the
    success-probability-vs-alpha table (ARB-04) should compute this across
    multiple alpha values, never report a single collapsed number."""
    alpha = float(alpha)  # Pitfall 1 -- cast before any downstream numpy.float64 leak
    proc, ancilla_spec = _build_weight2_cp_processor_no_postselect(n, i, j, thetas, alpha)
    input_state = _weight2_cp_input_state(n, ancilla_spec)

    analyzer = pcvl.algorithm.Analyzer(proc, [input_state], list(allstate_iterator(input_state)))
    analyzer.compute()

    ancilla_modes = [2 * n, 2 * n + 1, 2 * n + 2, 2 * n + 3]

    dist = {}
    residual = 0.0
    postselect_failure_prob = 0.0
    for state, prob in zip(analyzer.output_states_list, analyzer.distribution[0]):
        p = complex(prob).real
        if any(state[m] != 0 for m in ancilla_modes):
            postselect_failure_prob += p
            continue

        bit_i = _decode_single_qubit_pair(state, i)
        bit_j = _decode_single_qubit_pair(state, j)
        if bit_i is None or bit_j is None:
            # CP's own post-selection condition on its own pair -- see
            # docstring above for why this is failure, not residual.
            postselect_failure_prob += p
            continue

        bits = []
        bystander_invalid = False
        for k in range(n):
            if k == i:
                bits.append(bit_i)
            elif k == j:
                bits.append(bit_j)
            else:
                b = _decode_single_qubit_pair(state, k)
                if b is None:
                    bystander_invalid = True
                    break
                bits.append(b)

        if bystander_invalid:
            residual += p
        else:
            key = "".join(bits)
            dist[key] = dist.get(key, 0.0) + p

    postselect_success_prob = 1.0 - postselect_failure_prob
    if postselect_success_prob > 0:
        dist = {k: v / postselect_success_prob for k, v in dist.items()}
        residual = residual / postselect_success_prob

    return dist, residual, postselect_failure_prob


def build_full_circuit(n, thetas):
    """Full ENC-01 pipeline for weight-1 generators: state prep -> diagonal
    layer -> conjugation -> readout, all on Circuit(2n)."""
    assert len(thetas) == n
    circuit = pcvl.Circuit(2 * n)
    for k in range(n):
        circuit.add(2 * k, pcvl.HWP(QUBIT_PI_8))
    for k in range(n):
        circuit.add(2 * k, pcvl.WP(thetas[k], 0))
    for k in range(n):
        circuit.add(2 * k, pcvl.HWP(QUBIT_PI_8))
    for k in range(n):
        circuit.add(2 * k, pcvl.PBS())
    return circuit


def all_h_input(n):
    """BasicState with all n qubits starting in |H> (= |0>) and their vacuum
    partner modes empty: |{P:H},0,{P:H},0,...>."""
    return pcvl.BasicState("|" + ",".join(["{P:H},0"] * n) + ">")


def run_full_circuit(n, thetas):
    """Build and run the full pipeline for n qubits with the given weight-1
    generator angles. Returns (analyzer, dist) where dist is
    {str(BasicState): probability} over the 2n-mode output."""
    circuit = build_full_circuit(n, thetas)
    processor = pcvl.Processor("SLOS", circuit)
    input_state = all_h_input(n)

    analyzer = pcvl.algorithm.Analyzer(processor, [input_state], list(allstate_iterator(input_state)))
    analyzer.compute()

    dist = {
        str(state): complex(prob).real
        for state, prob in zip(analyzer.output_states_list, analyzer.distribution[0])
    }
    return analyzer, dist


def expected_single_qubit_probs(theta):
    """Closed-form, empirically-confirmed marginal for one qubit: P(H) =
    cos^2(theta), P(V) = sin^2(theta), from HWP(pi/8) -> WP(theta,0) ->
    HWP(pi/8) -> PBS starting from |H>. (H/V corrected in Plan 09-02 -- see
    the port<->polarization convention note above the module docstring's
    Perceval API facts.)"""
    return {"H": np.cos(theta) ** 2, "V": np.sin(theta) ** 2}


def expected_joint_distribution(n, thetas):
    """Product-state prediction for n weight-1 (uncorrelated) generators:
    joint probability of a bitstring is the product of each qubit's marginal.
    Returns {bitstring: probability} where bitstring[k] is 'H' or 'V'."""
    import itertools

    marginals = [expected_single_qubit_probs(theta) for theta in thetas]
    dist = {}
    for bits in itertools.product("HV", repeat=n):
        p = 1.0
        for k, b in enumerate(bits):
            p *= marginals[k][b]
        dist["".join(bits)] = p
    return dist


def basic_state_to_bitstring(state, n):
    """Converts a 2n-mode readout BasicState (each qubit pair is [0,1]='H' or
    [1,0]='V' -- verified against a bare PBS with pure H/V input, Plan 09-02)
    to an n-character 'H'/'V' bitstring. Returns None if the state has any
    qubit pair outside the single-photon computational subspace (bunched/lost
    photons) -- ENC-03's out-of-subspace case."""
    modes = [state[i] for i in range(2 * n)]
    bits = []
    for k in range(n):
        pair = (modes[2 * k], modes[2 * k + 1])
        if pair == (0, 1):
            bits.append("H")
        elif pair == (1, 0):
            bits.append("V")
        else:
            return None
    return "".join(bits)


# ENC-03: basis correspondence (bitstring <-> Fock state), both directions.


def bitstring_to_fock(bitstring, n):
    """Forward map (ENC-03): '0' -> |H>, '1' -> |V>, one photon per qubit on
    its own polarization-carrying mode, vacuum on its partner mode -- matches
    ENC-01's |0>=|H>, |1>=|V> convention and this module's 2n-mode layout.
    Returns a raw (pre-circuit) pcvl.BasicState, not yet converted through
    build_readout_circuit's PBS."""
    assert len(bitstring) == n
    assert all(b in "01" for b in bitstring)
    parts = []
    for b in bitstring:
        parts.append("{P:H}" if b == "0" else "{P:V}")
        parts.append("0")
    return pcvl.BasicState("|" + ",".join(parts) + ">")


def run_readout(n, input_state):
    """Runs input_state through build_readout_circuit(n) (PBS conversion
    only, no diagonal/conjugation gates) and returns the single output
    BasicState with probability ~1. For a pure computational-basis input
    (exactly one polarization state per qubit, no superposition), the PBS
    conversion is deterministic -- exactly one output state should have
    probability 1. Returns None if no such state is found (would indicate an
    input that wasn't a pure computational-basis state)."""
    circuit = build_readout_circuit(n)
    processor = pcvl.Processor("SLOS", circuit)
    analyzer = pcvl.algorithm.Analyzer(processor, [input_state], list(allstate_iterator(input_state)))
    analyzer.compute()
    for state, prob in zip(analyzer.output_states_list, analyzer.distribution[0]):
        if np.isclose(complex(prob).real, 1.0, atol=1e-9):
            return state
    return None


# ENC-04: validation -- exact qubit-side reference, photonic-side readout,
# and a distance metric between them.


def exact_qubit_iqp_distribution(n, thetas, pair_thetas=None):
    """Exact qubit-side IQP distribution via direct state-vector simulation
    (plain numpy, no external dependency): |+>^{tensor n} -> diagonal
    weight-1 (+ optional weight-2) phase layer (thetas[k] on qubit k, matching
    build_diagonal_layer_circuit's generator set) -> H^{tensor n} -> |amplitude|^2.

    Bit-ordering convention (stated explicitly, per the sibling
    iqp-mmd-barren-plateau project's documented gotcha that this is easy to
    get backwards): qubit 0 is the most-significant bit. Basis-state index i
    (0 <= i < 2^n) has qubit k's bit = (i >> (n-1-k)) & 1. This matches
    np.kron's natural tensor-product ordering when qubit 0's factor is
    kron'd first, and matches this module's own bitstring convention
    elsewhere (bitstring[k] = qubit k, left to right).

    pair_thetas (Phase 12, WT2-02): optional dict {(i, j): theta_ij} (i < j)
    for Z_i*Z_j pair-generator terms, added on top of the existing weight-1
    diagonal phase accumulation using the SAME bit-ordering convention and
    the SAME Z-eigenvalue sign convention ((-1)^bit_k) already established
    for weight-1 -- Z_i*Z_j's eigenvalue is the product of each qubit's own
    Z eigenvalue. pair_thetas=None (the default) behaves identically to the
    pre-Phase-12 function -- fully backward compatible, no existing call
    site or test needs to change. Verified against the photonic ground
    truth to ~1e-16 (12-RESEARCH.md Steps 2-5)."""
    pair_thetas = pair_thetas or {}
    plus = np.array([1, 1], dtype=complex) / np.sqrt(2)
    state = plus.copy()
    for _ in range(n - 1):
        state = np.kron(state, plus)

    dim = 2 ** n
    phases = np.zeros(dim, dtype=complex)
    for i in range(dim):
        total_phase = 0.0
        for k in range(n):
            bit_k = (i >> (n - 1 - k)) & 1
            total_phase += thetas[k] * (1 if bit_k == 0 else -1)  # Z eigenvalue (-1)^bit_k
        for (a, b), th in pair_thetas.items():
            bit_a = (i >> (n - 1 - a)) & 1
            bit_b = (i >> (n - 1 - b)) & 1
            za = 1 if bit_a == 0 else -1
            zb = 1 if bit_b == 0 else -1
            total_phase += th * za * zb
        phases[i] = np.exp(1j * total_phase)
    state = state * phases

    had = np.array([[1, 1], [1, -1]], dtype=complex) / np.sqrt(2)
    had_n = had.copy()
    for _ in range(n - 1):
        had_n = np.kron(had_n, had)
    final_state = had_n @ state

    probs = np.abs(final_state) ** 2
    return {
        "".join(str((i >> (n - 1 - k)) & 1) for k in range(n)): probs[i]
        for i in range(dim)
    }


def photonic_iqp_distribution(n, thetas):
    """Photonic-side IQP distribution: runs the ENC-01 circuit (prep +
    diagonal + conjugation + readout, via run_full_circuit) for the given
    weight-1 generator set, and translates outputs to bitstrings via ENC-03's
    fock_to_bitstring. Returns (dist, residual) where dist = {bitstring:
    probability} over valid outcomes only, and residual = total probability
    on out-of-subspace outcomes -- ENC-03's reporting policy (explicit
    residual, never silently discarded/renormalized)."""
    _, raw_dist = run_full_circuit(n, thetas)
    dist = {}
    residual = 0.0
    for state_str, prob in raw_dist.items():
        state = pcvl.BasicState(state_str)
        bits = fock_to_bitstring(state, n)
        if bits is None:
            residual += prob
        else:
            dist[bits] = dist.get(bits, 0.0) + prob
    return dist, residual


def total_variation_distance(dist_a, dist_b):
    """Standard total variation distance: TVD = 0.5 * sum(|a(x)-b(x)|) over
    the union of both distributions' keys."""
    keys = set(dist_a) | set(dist_b)
    return 0.5 * sum(abs(dist_a.get(k, 0.0) - dist_b.get(k, 0.0)) for k in keys)


def fock_to_bitstring(basic_state, n):
    """Reverse map (ENC-03): a 2n-mode post-readout BasicState (each qubit
    pair (0,1)='0'=H or (1,0)='1'=V) -> an n-character '0'/'1' bitstring.
    Returns None for any qubit pair outside the single-photon computational
    subspace -- (0,0) [photon lost], (1,1) [extra photon, one per mode],
    (2,0)/(0,2) [bunched photons] -- the out-of-subspace case ENC-03 requires
    an explicit answer for, even though this module's own ideal, lossless
    circuits never actually produce these outcomes (confirmed empirically in
    Plan 09-01: exactly zero leaked probability for every tested case)."""
    hv = basic_state_to_bitstring(basic_state, n)
    if hv is None:
        return None
    return hv.replace("H", "0").replace("V", "1")
