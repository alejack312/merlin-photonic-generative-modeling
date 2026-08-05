import perceval as pcvl
import numpy as np

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
#   - Empirically confirmed input/output basis-index convention (verified, not
#     assumed): starting from |H> and running through
#     HWP(pi/8) -> WP(theta,0) -> HWP(pi/8) -> PBS, the two readout ports give
#     P(|H> port) = sin^2(theta), P(|V> port) = cos^2(theta). This is the
#     abstract derivation's H*D(theta)*H = [[cos(theta), i*sin(theta)],
#     [i*sin(theta), cos(theta)]] result, with Perceval's internal {P:H}/{P:V}
#     amplitude-index assignment fixing which physical port carries which label
#     -- the operator structure (Hadamard-sandwiched diagonal phase) is exactly
#     as derived; only the H<->port-index correspondence is an implementation
#     convention, confirmed empirically here rather than assumed.
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
    sin^2(theta), P(V) = cos^2(theta), from HWP(pi/8) -> WP(theta,0) ->
    HWP(pi/8) -> PBS starting from |H>."""
    return {"H": np.sin(theta) ** 2, "V": np.cos(theta) ** 2}


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
    """Converts a 2n-mode readout BasicState (each qubit pair is [1,0]='H' or
    [0,1]='V') to an n-character 'H'/'V' bitstring. Returns None if the state
    has any qubit pair outside the single-photon computational subspace
    (bunched/lost photons) -- ENC-03's out-of-subspace case."""
    modes = [state[i] for i in range(2 * n)]
    bits = []
    for k in range(n):
        pair = (modes[2 * k], modes[2 * k + 1])
        if pair == (1, 0):
            bits.append("H")
        elif pair == (0, 1):
            bits.append("V")
        else:
            return None
    return "".join(bits)
