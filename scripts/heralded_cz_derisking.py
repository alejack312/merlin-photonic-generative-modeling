import perceval as pcvl  # Circuit, BasicState, Processor, StateVector live at top-level.
from perceval.algorithm import Analyzer  # not exported at top level, import explicitly.
from perceval.components.core_catalog.heralded_cz import HeraldedCzItem
from perceval.simulators import Simulator
from perceval.backends import SLOSBackend

import numpy as np

# Phase 10: heralded_cz de-risking.
#
# This module reproduces 10-RESEARCH.md's live-measured numbers as
# executable, asserted checks -- not just re-printing cached results. It
# measures two independent things about Perceval's `heralded_cz` catalog
# gate (perceval-quandela==1.2.4) directly against this repo's installed
# venv:
#
#   1. Herald-success probability, read off Processor.probs()'s
#      global_perf/physical_perf/logical_perf (never shot-sampled), for
#      all 4 computational-basis dual-rail inputs plus 2 superposition
#      spot-checks.
#   2. The CZ phase sign on |1,1> -- Processor.probs()/Analyzer are
#      phase-blind (they only ever expose |amplitude|^2), so this needs a
#      separate Simulator.prob_amplitude() readout on the bare 6-mode
#      circuit.
#
# Two pitfalls avoided (see 10-RESEARCH.md's "Common Pitfalls" for the
# full writeup):
#   - Pitfall 1: the herald modes (indices 4, 5) need a REAL ancilla
#     photon on input, not vacuum -- add_herald's "expected" count applies
#     to input AND output. Processor.with_input() on a 4-length
#     BasicState auto-fills this; the manual 6-mode Simulator path does
#     not, and must replicate it by hand (read from
#     HeraldedCzItem().build_experiment().in_heralds, not hardcoded).
#   - Pitfall 2: StateVector/superposition inputs to Processor.with_input
#     need full 6-mode terms (not 4-mode) and an explicit
#     min_detected_photons_filter(0) call before probs() -- the
#     StateVector dispatch has no auto-fill, unlike the plain BasicState
#     path.
#
# API reference (verified against installed perceval-quandela==1.2.4):
#   - HeraldedCzItem().build_experiment() -- NOT build_circuit() -- is the
#     only path that attaches the two add_herald() calls; build_circuit()
#     alone returns a bare 6-mode Circuit with no herald metadata
#     (Pitfall 4 in 10-RESEARCH.md).
#   - Processor.compute_physical_logical_perf(True) must be called before
#     probs() for physical_perf/logical_perf to be included in the
#     returned dict (global_perf is always present).

TOLERANCE = 1e-9
PHASE_TOLERANCE = 1e-6

EXPECTED_HERALD_SUCCESS = 2 / 27

DUAL_RAIL = {"0": (1, 0), "1": (0, 1)}

COMPUTATIONAL_BASIS = [
    ("0", "0", pcvl.BasicState([1, 0, 1, 0])),
    ("0", "1", pcvl.BasicState([1, 0, 0, 1])),
    ("1", "0", pcvl.BasicState([0, 1, 1, 0])),
    ("1", "1", pcvl.BasicState([0, 1, 0, 1])),
]


def build_heralded_cz_processor():
    """Build a fresh Processor wrapping heralded_cz's build_experiment()
    output (the herald-attached form), with physical/logical perf
    reporting turned on."""
    item = HeraldedCzItem()
    exp = item.build_experiment()  # NOT build_circuit() -- that drops the heralds
    proc = pcvl.Processor("SLOS", exp)
    proc.compute_physical_logical_perf(True)  # exposes physical_perf/logical_perf separately
    return proc


def measure_herald_success(basis_input: pcvl.BasicState) -> dict:
    """Build a fresh processor and measure herald-success probability for
    a single 4-length dual-rail computational-basis input (Processor
    auto-fills the 2 herald ancilla photons)."""
    proc = build_heralded_cz_processor()
    proc.with_input(basis_input)
    return proc.probs()


def measure_herald_success_superposition(terms: list) -> dict:
    """Build a fresh processor and measure herald-success probability for
    a superposition input given as a list of (amplitude, 6-mode
    BasicState) pairs (each term already includes the [1,1] herald
    ancilla photons, per Pitfall 1). Requires min_detected_photons_filter
    per Pitfall 2, since the StateVector path has no auto-fill."""
    proc = build_heralded_cz_processor()
    # NOTE: amplitudes must be plain Python floats, not numpy.float64 --
    # pybind's operator overload resolution on exqalibur.StateVector
    # silently mis-dispatches numpy scalar multiplication (raises a
    # confusing "inhomogeneous shape" ValueError), diagnosed live while
    # building this check.
    sv = float(terms[0][0]) * pcvl.StateVector(terms[0][1])
    for amplitude, state in terms[1:]:
        sv = sv + float(amplitude) * pcvl.StateVector(state)
    proc.with_input(sv)
    proc.min_detected_photons_filter(0)
    return proc.probs()


def build_plus_plus_terms() -> list:
    """|+>|+> as 4 equal-amplitude 6-mode terms (ctrl x data, each in
    {'0','1'}), herald ancilla [1,1] appended to every term."""
    amp = 0.5
    terms = []
    for ctrl in "01":
        for data in "01":
            cm, dm = DUAL_RAIL[ctrl], DUAL_RAIL[data]
            state = pcvl.BasicState(list(cm) + list(dm) + [1, 1])
            terms.append((amp, state))
    return terms


def build_plus_zero_terms() -> list:
    """|+>|0> (ctrl in superposition, data fixed at |0>) as 2 equal-
    amplitude 6-mode terms, herald ancilla [1,1] appended to every term."""
    amp = 1 / np.sqrt(2)
    terms = []
    for ctrl in "01":
        cm, dm = DUAL_RAIL[ctrl], DUAL_RAIL["0"]
        state = pcvl.BasicState(list(cm) + list(dm) + [1, 1])
        terms.append((amp, state))
    return terms


def build_analyzer():
    """Build one Analyzer call over all 4 computational-basis inputs with
    output_states='*', producing the full truth-table matrix including
    zero-check columns for invalid/bunched outputs."""
    proc = build_heralded_cz_processor()
    inputs = [state for _, _, state in COMPUTATIONAL_BASIS]
    an = Analyzer(proc, inputs, "*")
    an.compute()
    return an


def check_no_leakage(an: Analyzer) -> bool:
    """Assert every non-expected output column is exactly 0 for each of
    the 4 computational-basis inputs -- the 'no leakage' claim, checked
    programmatically rather than eyeballed."""
    expected_outputs = [state for _, _, state in COMPUTATIONAL_BASIS]
    output_states = an.output_states_list
    all_clean = True
    for row_idx, expected in enumerate(expected_outputs):
        row = an.distribution[row_idx]
        for state, prob in zip(output_states, row):
            prob_val = complex(prob).real
            if state == expected:
                if not np.isclose(prob_val, 1.0, atol=TOLERANCE):
                    all_clean = False
            else:
                if not np.isclose(prob_val, 0.0, atol=TOLERANCE):
                    all_clean = False
    return all_clean


def check_post_select_fn_empty() -> bool:
    """Assert post_select_fn is empty on the built Experiment --
    logical_perf for this gate is pure herald condition, no hidden
    second filter (Pitfall 3)."""
    item = HeraldedCzItem()
    exp = item.build_experiment()
    return not str(exp.post_select_fn).strip()


def measure_cz_phase() -> dict:
    """Build a Simulator directly on heralded_cz's bare 6-mode circuit
    (no Processor/Experiment wrapper) and read the complex amplitude for
    each of the 4 computational-basis combos via prob_amplitude. Herald
    ancilla photon counts are read from in_heralds, not hardcoded, per
    Pitfall 1's stated mitigation."""
    item = HeraldedCzItem()
    circuit = item.build_circuit()  # bare 6-mode Circuit, no herald metadata
    exp = item.build_experiment()
    in_heralds = exp.in_heralds  # expect {4: 1, 5: 1}
    herald_counts = [in_heralds[4], in_heralds[5]]

    sim = Simulator(SLOSBackend())
    sim.set_circuit(circuit)

    amplitudes = {}
    for ctrl in "01":
        for data in "01":
            cm, dm = DUAL_RAIL[ctrl], DUAL_RAIL[data]
            in_state = pcvl.BasicState(list(cm) + list(dm) + herald_counts)
            out_state = pcvl.BasicState(list(cm) + list(dm) + herald_counts)
            amp = sim.prob_amplitude(in_state, out_state)
            amplitudes[(ctrl, data)] = amp
    return amplitudes


def check_phase_sign(amplitudes: dict) -> bool:
    """Assert |amplitude|^2 matches 2/27 for all four combos, and the
    sign matches CZ's diag(1,1,1,-1): negative only on ctrl='1',
    data='1'."""
    expected_magnitude = np.sqrt(EXPECTED_HERALD_SUCCESS)
    all_pass = True
    for (ctrl, data), amp in amplitudes.items():
        magnitude_sq = abs(amp) ** 2
        if not np.isclose(magnitude_sq, EXPECTED_HERALD_SUCCESS, atol=TOLERANCE):
            all_pass = False
        expected_sign = -1.0 if (ctrl == "1" and data == "1") else 1.0
        expected_value = expected_sign * expected_magnitude
        if not np.isclose(amp.real, expected_value, atol=PHASE_TOLERANCE):
            all_pass = False
    return all_pass


def main():
    print("=" * 70)
    print("heralded_cz de-risking: herald-success probability")
    print("=" * 70)

    computational_results = {}
    for ctrl, data, state in COMPUTATIONAL_BASIS:
        res = measure_herald_success(state)
        computational_results[(ctrl, data)] = res
        print(
            f"ctrl={ctrl}, data={data}: global_perf={res['global_perf']:.10f}, "
            f"physical_perf={res['physical_perf']:.10f}, "
            f"logical_perf={res['logical_perf']:.10f}"
        )

    uniform_pass = all(
        np.isclose(res["global_perf"], EXPECTED_HERALD_SUCCESS, atol=TOLERANCE)
        and np.isclose(res["physical_perf"], 1.0, atol=TOLERANCE)
        and np.isclose(res["logical_perf"], EXPECTED_HERALD_SUCCESS, atol=TOLERANCE)
        for res in computational_results.values()
    )
    print(f"\nComputational-basis uniformity check: {'PASS' if uniform_pass else 'FAIL'}")

    print()
    print("Superposition spot-checks:")
    pp_res = measure_herald_success_superposition(build_plus_plus_terms())
    print(f"|+>|+>: global_perf={pp_res['global_perf']:.10f}")
    pz_res = measure_herald_success_superposition(build_plus_zero_terms())
    print(f"|+>|0>: global_perf={pz_res['global_perf']:.10f}")

    superposition_pass = np.isclose(
        pp_res["global_perf"], EXPECTED_HERALD_SUCCESS, atol=TOLERANCE
    ) and np.isclose(pz_res["global_perf"], EXPECTED_HERALD_SUCCESS, atol=TOLERANCE)
    print(f"Superposition uniformity check: {'PASS' if superposition_pass else 'FAIL'}")

    print()
    print("=" * 70)
    print("Analyzer truth table (no-leakage check)")
    print("=" * 70)
    an = build_analyzer()
    pcvl.pdisplay(an)
    no_leakage_pass = check_no_leakage(an)
    print(f"No-leakage check: {'PASS' if no_leakage_pass else 'FAIL'}")

    print()
    post_select_empty = check_post_select_fn_empty()
    print(
        f"post_select_fn emptiness check "
        f"(logical_perf is pure herald condition): "
        f"{'PASS' if post_select_empty else 'FAIL'}"
    )

    print()
    print("=" * 70)
    print("heralded_cz de-risking: CZ phase sign")
    print("=" * 70)
    amplitudes = measure_cz_phase()
    for (ctrl, data), amp in amplitudes.items():
        print(
            f"ctrl={ctrl}, data={data}: amplitude={amp}, "
            f"|amplitude|^2={abs(amp) ** 2:.10f}"
        )
    phase_pass = check_phase_sign(amplitudes)
    print(f"Phase sign check: {'PASS' if phase_pass else 'FAIL'}")

    assert uniform_pass, "Herald-success probability not uniform across computational-basis inputs"
    assert superposition_pass, "Herald-success probability not uniform for superposition spot-checks"
    assert no_leakage_pass, "Analyzer truth table shows leakage to unexpected output states"
    assert post_select_empty, "post_select_fn is non-empty -- logical_perf bundles a hidden second filter"
    assert phase_pass, "CZ phase sign/magnitude check failed"

    print()
    print("All checks PASS.")


if __name__ == "__main__":
    main()
