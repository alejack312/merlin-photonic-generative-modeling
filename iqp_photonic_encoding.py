import perceval as pcvl
import numpy as np

from perceval.components.core_catalog.heralded_cz import HeraldedCzItem

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
    circuit.add(0, pcvl.PBS())        # unwrap qubit i: dual rail -> polarization, local (0,1)
    circuit.add(2, pcvl.PBS())        # unwrap qubit j: dual rail -> polarization, local (2,3)

    herald_spec = HeraldedCzItem().build_experiment().in_heralds  # not hardcoded -- fails loudly if heralded_cz's layout ever changes
    return circuit, herald_spec


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

    analyzer = pcvl.algorithm.Analyzer(processor, [input_state], "*")
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
    analyzer = pcvl.algorithm.Analyzer(processor, [input_state], "*")
    analyzer.compute()
    for state, prob in zip(analyzer.output_states_list, analyzer.distribution[0]):
        if np.isclose(complex(prob).real, 1.0, atol=1e-9):
            return state
    return None


# ENC-04: validation -- exact qubit-side reference, photonic-side readout,
# and a distance metric between them.


def exact_qubit_iqp_distribution(n, thetas):
    """Exact qubit-side IQP distribution via direct state-vector simulation
    (plain numpy, no external dependency): |+>^{tensor n} -> diagonal
    weight-1 phase layer (thetas[k] on qubit k, matching
    build_diagonal_layer_circuit's generator set) -> H^{tensor n} -> |amplitude|^2.

    Bit-ordering convention (stated explicitly, per the sibling
    iqp-mmd-barren-plateau project's documented gotcha that this is easy to
    get backwards): qubit 0 is the most-significant bit. Basis-state index i
    (0 <= i < 2^n) has qubit k's bit = (i >> (n-1-k)) & 1. This matches
    np.kron's natural tensor-product ordering when qubit 0's factor is
    kron'd first, and matches this module's own bitstring convention
    elsewhere (bitstring[k] = qubit k, left to right)."""
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
