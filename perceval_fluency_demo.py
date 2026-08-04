import perceval as pcvl  # Circuit, BS, PS, BasicState, Processor live at top-level.
from perceval.algorithm import Analyzer  # not exported at top level, import explicitly.

import numpy as np

# Build a manual circuit demonstrating low-level Perceval API fluency — no
# QuantumLayer.simple(), deliberately trivial (not IQP-flavored, that's Phase 9's job).
#
# This follows the owner's own attempt/sketch from this plan's Task 1 checkpoint
# (sketched and run live in a terminal session, not through Claude): the owner
# independently built the Circuit(2) + BS.H() + Processor("SLOS", ...) pipeline,
# ran both input states (single-photon and Hong-Ou-Mandel) through one Analyzer
# call, and verified the printed distribution matched both closed-form
# predictions by eye. This version keeps that structure and adds the
# programmatic assertions + explicit PASS/FAIL reporting that PREQ-01 requires
# (checking the result in code, not just eyeballing Analyzer's printout).
#
# API reference (verified against installed perceval-quandela==1.2.4):
#   - pcvl.BS.H() — Hadamard-convention 50/50 beamsplitter (real-valued
#     [[1,1],[1,-1]]/sqrt(2)), easier to hand-verify than the default
#     complex-valued BS().
#   - Analyzer needs a Processor, not a bare Circuit:
#     proc = pcvl.Processor("SLOS", circuit).
#   - Input states: pcvl.BasicState([1, 0]) — one photon in mode 0, vacuum in
#     mode 1.
#   - Run it: analyzer = Analyzer(proc, [input_state], "*") ->
#     analyzer.compute() -> read analyzer.distribution (rows = input states in
#     analyzer.input_states_list order, columns = output states in
#     analyzer.output_states_list order).
#
# Closed-form facts being verified:
#   - One photon through a 50/50 BS -> exact 50/50 split (no interference with
#     a single photon).
#   - Two indistinguishable photons, one per input port, on a 50/50 BS ->
#     Hong-Ou-Mandel dip: P(1,1)=0, P(0,2)=P(2,0)=0.5.
#   - A Mach-Zehnder-style BS.H() -> PS(theta) -> BS.H() construction on a
#     single photon: PS's phase is invisible to a Fock-basis (photon-number)
#     measurement without a second beamsplitter to interfere against, but once
#     that second BS is there, the phase visibly and predictably steers where
#     the photon comes out. Derivation: BS.H() is the real Hadamard matrix
#     1/sqrt(2)*[[1,1],[1,-1]], and PS(theta) applies a bare phase e^{i*theta}
#     to mode 0. Starting from input (1,0), the first BS.H() gives amplitudes
#     (1,1)/sqrt(2); PS(theta) gives (e^{i*theta},1)/sqrt(2); the second
#     BS.H() gives ((e^{i*theta}+1)/2, (e^{i*theta}-1)/2). So:
#       P(|1,0>) = |e^{i*theta}+1|^2/4 = cos^2(theta/2)
#       P(|0,1>) = |e^{i*theta}-1|^2/4 = sin^2(theta/2)
#     theta=0 -> fully constructive on mode 0 (P(1,0)=1); theta=pi/2 -> 50/50;
#     theta=pi -> fully flipped to mode 1 (P(0,1)=1).
#
# Debugging notes from the owner's live attempt (worth keeping — see
# 08-02-SUMMARY.md for the full writeup):
#   - circuit.add(...) takes a starting port index as its first arg (here 0),
#     not a range/tuple of ports — pcvl.BS.H() is a 2-mode component, so
#     circuit.add(0, pcvl.BS.H()) wires it onto modes 0 and 1 of the 2-mode
#     circuit.
#   - pdisplay's box-drawing characters need PYTHONIOENCODING=utf-8 set on
#     Windows terminals, or printing the circuit diagram raises a
#     UnicodeEncodeError.

TOLERANCE = 1e-9


def build_circuit():
    """Two-mode circuit: a single Hadamard-convention 50/50 beamsplitter."""
    circuit = pcvl.Circuit(2)
    circuit.add(0, pcvl.BS.H())
    return circuit


def build_mzi_circuit(theta):
    """Mach-Zehnder-style circuit: BS.H() -> PS(theta) on mode 0 -> BS.H().
    Demonstrates that PS's phase value visibly and predictably changes the
    output distribution once there's a second beamsplitter to interfere
    against (unlike a bare PS, whose phase is invisible to a Fock-basis
    photon-number measurement with no interferometer)."""
    circuit = pcvl.Circuit(2)
    circuit.add(0, pcvl.BS.H())
    circuit.add(0, pcvl.PS(theta))
    circuit.add(0, pcvl.BS.H())
    return circuit


def run_mzi_analyzer(theta):
    """Build the MZI circuit/processor for a given theta, run a single-photon
    input through one Analyzer call, and return (analyzer, dist) where dist
    is {BasicState: probability}."""
    circuit = build_mzi_circuit(theta)
    processor = pcvl.Processor("SLOS", circuit)

    input_states = [pcvl.BasicState([1, 0])]

    ca = Analyzer(processor, input_states, "*")
    ca.compute()

    output_states = ca.output_states_list
    row = ca.distribution[0]
    dist = {state: complex(prob).real for state, prob in zip(output_states, row)}
    return ca, dist


def check_mzi(dist, theta):
    """Closed-form check: P(|1,0>) = cos^2(theta/2), P(|0,1>) = sin^2(theta/2)."""
    p_10 = dist.get(pcvl.BasicState([1, 0]), 0.0)
    p_01 = dist.get(pcvl.BasicState([0, 1]), 0.0)
    expected_p_10 = np.cos(theta / 2) ** 2
    expected_p_01 = np.sin(theta / 2) ** 2
    return (
        np.isclose(p_10, expected_p_10, atol=TOLERANCE)
        and np.isclose(p_01, expected_p_01, atol=TOLERANCE)
    )


def run_analyzer():
    """Build the circuit/processor, run both input states through one
    Analyzer call, and return (analyzer, single_photon_dist, hom_dist) where
    each dist is a dict {BasicState: probability}."""
    circuit = build_circuit()
    processor = pcvl.Processor("SLOS", circuit)

    input_states = [pcvl.BasicState([1, 0]), pcvl.BasicState([1, 1])]

    ca = Analyzer(processor, input_states, "*")
    ca.compute()

    # distribution rows follow ca.input_states_list order; columns follow
    # ca.output_states_list order.
    output_states = ca.output_states_list
    single_photon_row = ca.distribution[0]
    hom_row = ca.distribution[1]

    single_photon_dist = {
        state: complex(prob).real for state, prob in zip(output_states, single_photon_row)
    }
    hom_dist = {
        state: complex(prob).real for state, prob in zip(output_states, hom_row)
    }
    return ca, single_photon_dist, hom_dist


def check_single_photon(dist):
    """Closed-form: |1,0> input on a 50/50 BS -> 50% |1,0>, 50% |0,1>."""
    p_10 = dist.get(pcvl.BasicState([1, 0]), 0.0)
    p_01 = dist.get(pcvl.BasicState([0, 1]), 0.0)
    return (
        np.isclose(p_10, 0.5, atol=TOLERANCE)
        and np.isclose(p_01, 0.5, atol=TOLERANCE)
    )


def check_hom_dip(dist):
    """Closed-form Hong-Ou-Mandel dip: |1,1> input on a 50/50 BS ->
    P(1,1)=0, P(0,2)=P(2,0)=0.5."""
    p_11 = dist.get(pcvl.BasicState([1, 1]), 0.0)
    p_02 = dist.get(pcvl.BasicState([0, 2]), 0.0)
    p_20 = dist.get(pcvl.BasicState([2, 0]), 0.0)
    return (
        np.isclose(p_11, 0.0, atol=TOLERANCE)
        and np.isclose(p_02, 0.5, atol=TOLERANCE)
        and np.isclose(p_20, 0.5, atol=TOLERANCE)
    )


def main():
    ca, single_photon_dist, hom_dist = run_analyzer()

    # Print the raw distribution table for human inspection.
    pcvl.pdisplay(ca)

    single_photon_pass = check_single_photon(single_photon_dist)
    hom_pass = check_hom_dip(hom_dist)

    print()
    print(f"Single-photon 50/50 split: {single_photon_dist}")
    print(f"closed-form check: {'PASS' if single_photon_pass else 'FAIL'}")
    print()
    print(f"Hong-Ou-Mandel dip: {hom_dist}")
    print(f"closed-form check: {'PASS' if hom_pass else 'FAIL'}")

    assert single_photon_pass, "Single-photon 50/50 split did not match closed-form prediction"
    assert hom_pass, "Hong-Ou-Mandel dip did not match closed-form prediction"

    print()
    mzi_thetas = [0, np.pi / 2, np.pi]
    mzi_passes = []
    for theta in mzi_thetas:
        _, mzi_dist = run_mzi_analyzer(theta)
        mzi_pass = check_mzi(mzi_dist, theta)
        mzi_passes.append(mzi_pass)
        print(f"MZI (BS.H->PS(theta={theta:.4f})->BS.H) distribution: {mzi_dist}")
        print(f"closed-form check: {'PASS' if mzi_pass else 'FAIL'}")
        print()

    assert all(mzi_passes), "MZI interference distribution did not match closed-form prediction for all theta values"

    return


if __name__ == "__main__":
    main()
