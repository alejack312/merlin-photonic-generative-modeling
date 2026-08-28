"""Phase 22 Plan 01 (MPAIR-07): numeric evidence for whether pooled/recycled
ancilla modes may be safely reused across two SEQUENTIALLY-composed CP(alpha)
insertions under this pipeline's deferred (end-of-circuit-only) post-selection.

D-06 (22-CONTEXT.md) named this an open physics question Forge cannot check:
`Processor.set_postselection()` cannot compose a condition on modes a later
component touches (15-RESEARCH.md Pitfall 3), so ancilla modes are never
deterministically restored to vacuum mid-circuit. A second CP(alpha) insertion
applied to already-used ancilla modes therefore acts on a state that is only
PROBABILISTICALLY vacuum at that point, not a fresh, deterministically-reset
register -- physically different, in principle, from a dedicated ancilla bank.

This script builds `build_two_gate_processor(..., mode="pooled"|"dedicated")`,
a direct generalization of `_build_weight2_cp_processor_no_postselect`
(merlin_iqp/encoding/iqp_photonic.py:589-659) to TWO sequential CP(alpha) insertions, and
compares:
  - `dedicated`: each insertion gets its own disjoint 4-mode ancilla block
    (anchored against `exact_qubit_iqp_distribution` as ground truth)
  - `pooled`: both insertions reuse the SAME 4 physical ancilla modes

DECISION RULE (fixed before any number below was computed -- see
run_probe_n2/run_probe_n4, which print this same rule before printing any
measured number):
  HARNESS ANCHOR (must hold, or the run is invalid -- not a NO-GO):
      TVD(dist_dedicated, exact_reference) <= 1e-9
      AND residual_dedicated <= 1e-9
  GO evidence:
      TVD(dist_pooled, dist_dedicated) <= 1e-9
      AND abs(pfail_pooled - pfail_dedicated) <= 1e-9
  NO-GO evidence:
      either quantity above exceeds 1e-9

This plan does NOT rule on the verdict -- it only produces evidence and a
DRAFTED verdict in results/v3_forge_formal/phase22_reuse_gate.md. The owner rules at Plan
22-02's checkpoint.
"""

import argparse
import time

import perceval as pcvl

from merlin_iqp.encoding.iqp_photonic import (
    build_cp_insertion,
    build_conjugation_circuit,
    build_diagonal_layer_circuit,
    build_readout_circuit,
    build_state_prep_circuit,
    exact_qubit_iqp_distribution,
    total_variation_distance,
)
from merlin_iqp.encoding.iqp_photonic import allstate_iterator, _decode_single_qubit_pair

DECISION_RULE_TEXT = """\
DECISION RULE (pre-committed before any measured number is printed):
  HARNESS ANCHOR (must hold, or the run is invalid -- not a NO-GO):
      TVD(dist_dedicated, exact_reference) <= 1e-9
      AND residual_dedicated <= 1e-9
  GO evidence:
      TVD(dist_pooled, dist_dedicated) <= 1e-9
      AND abs(pfail_pooled - pfail_dedicated) <= 1e-9
  NO-GO evidence:
      either quantity above exceeds 1e-9
"""

THRESHOLD = 1e-9


def build_two_gate_processor(n, pair_a, pair_b, thetas, alpha, mode="pooled"):
    """Generalizes `_build_weight2_cp_processor_no_postselect`
    (merlin_iqp/encoding/iqp_photonic.py:589-659) to TWO sequential CP(alpha) insertions
    on pairs `pair_a = (a0, a1)` and `pair_b = (b0, b1)`.

    mode="dedicated": total_modes = 2*n + 8. Insertion A's ancilla maps to
        global (2n..2n+3); insertion B's to global (2n+4..2n+7). Each
        insertion gets its own physically-disjoint 4-mode ancilla block.
    mode="pooled": total_modes = 2*n + 4. BOTH insertions map their ancilla
        to the SAME global (2n..2n+3) -- physical reuse of the same modes.

    Component order is fixed and IDENTICAL in both modes: state prep ->
    theta-folded diagonal layer -> insertion A -> insertion B -> conjugation
    -> readout. pooled and dedicated differ ONLY in total_modes and in
    insertion B's ancilla mapping entries -- nothing else, so any observed
    distributional difference is attributable to ancilla reuse alone.

    Theta folding: starts from a COPY of `thetas`; alpha/4.0 is added to
    each of the four qubit indices touched (a0, a1 for insertion A; b0, b1
    for insertion B) -- additive, matching the reference's own convention.
    When A and B share a qubit, that qubit receives alpha/4.0 TWICE (no
    special-casing), consistent with two independent CP(alpha) insertions
    each folding their own correction onto whichever qubits they touch.

    Never calls proc.add_herald or proc.set_postselection (15-RESEARCH.md
    Pitfall 3 -- CP's post-selection is filtered by hand downstream).

    Returns (proc, ancilla_modes_a, ancilla_modes_b) where each ancilla_modes
    list is the 4 GLOBAL mode indices that insertion's ancilla landed on."""
    assert mode in ("pooled", "dedicated")
    a0, a1 = pair_a
    b0, b1 = pair_b
    assert 0 <= a0 < n and 0 <= a1 < n and a0 != a1
    assert 0 <= b0 < n and 0 <= b1 < n and b0 != b1
    assert len(thetas) == n

    alpha = float(alpha)
    theta = alpha / 4.0

    thetas_folded = list(thetas)
    thetas_folded[a0] += theta
    thetas_folded[a1] += theta
    thetas_folded[b0] += theta
    thetas_folded[b1] += theta

    if mode == "dedicated":
        total_modes = 2 * n + 8
        ancilla_a = [2 * n, 2 * n + 1, 2 * n + 2, 2 * n + 3]
        ancilla_b = [2 * n + 4, 2 * n + 5, 2 * n + 6, 2 * n + 7]
    else:
        total_modes = 2 * n + 4
        ancilla_a = [2 * n, 2 * n + 1, 2 * n + 2, 2 * n + 3]
        ancilla_b = [2 * n, 2 * n + 1, 2 * n + 2, 2 * n + 3]

    proc = pcvl.Processor("SLOS", total_modes)

    proc.add(0, build_state_prep_circuit(n))
    proc.add(0, build_diagonal_layer_circuit(n, thetas_folded))

    cp_circuit_a, ancilla_spec_a = build_cp_insertion(n, a0, a1, alpha)
    mapping_a = {
        2 * a0: 0, 2 * a0 + 1: 1,
        2 * a1: 2, 2 * a1 + 1: 3,
        ancilla_a[0]: 4, ancilla_a[1]: 5,
        ancilla_a[2]: 6, ancilla_a[3]: 7,
    }
    proc.add(mapping_a, cp_circuit_a)

    cp_circuit_b, ancilla_spec_b = build_cp_insertion(n, b0, b1, alpha)
    mapping_b = {
        2 * b0: 0, 2 * b0 + 1: 1,
        2 * b1: 2, 2 * b1 + 1: 3,
        ancilla_b[0]: 4, ancilla_b[1]: 5,
        ancilla_b[2]: 6, ancilla_b[3]: 7,
    }
    proc.add(mapping_b, cp_circuit_b)

    # NO add_herald, NO set_postselection here -- see module docstring.
    proc.add(0, build_conjugation_circuit(n))
    proc.add(0, build_readout_circuit(n))

    return proc, ancilla_a, ancilla_b


def _two_gate_input_state(n, num_ancilla_modes):
    """All-|+> on the 2n data ports, plain vacuum ('0') on every ancilla
    mode -- CP's own convention (`_weight2_cp_input_state`), extended to
    however many ancilla modes this mode variant exposes (4 pooled, 8
    dedicated)."""
    parts = ["{P:H},0"] * n
    parts.extend(["0"] * num_ancilla_modes)
    return pcvl.BasicState("|" + ",".join(parts) + ">")


def postselected_distribution(proc, n, ancilla_modes, gate_qubits):
    """Reproduces `photonic_cp_iqp_distribution`'s exact three-check filter
    (merlin_iqp/encoding/iqp_photonic.py:705-823), generalized to an arbitrary set of
    ancilla modes and an arbitrary set of qubits touched by any insertion:
      1. any ancilla output mode non-zero -> postselect_failure_prob
      2. else, any gate-touched qubit's own dual-rail pair decodes to None
         -> postselect_failure_prob (CP's own two-part post-selection
         condition -- NOT residual; getting this wrong produced TVD~0.3-0.4
         in Phase 15)
      3. else, any remaining bystander qubit decodes to None -> residual
    dist and residual are both divided by (1 - postselect_failure_prob).

    Returns (dist, residual, postselect_failure_prob)."""
    total_modes = 2 * n + len(ancilla_modes)
    input_state = _two_gate_input_state(n, len(ancilla_modes))

    analyzer = pcvl.algorithm.Analyzer(proc, [input_state], list(allstate_iterator(input_state)))
    analyzer.compute()

    dist = {}
    residual = 0.0
    postselect_failure_prob = 0.0

    for state, prob in zip(analyzer.output_states_list, analyzer.distribution[0]):
        p = complex(prob).real

        if any(state[m] != 0 for m in ancilla_modes):
            postselect_failure_prob += p
            continue

        gate_bits = {}
        gate_invalid = False
        for k in gate_qubits:
            b = _decode_single_qubit_pair(state, k)
            if b is None:
                gate_invalid = True
                break
            gate_bits[k] = b
        if gate_invalid:
            postselect_failure_prob += p
            continue

        bits = []
        bystander_invalid = False
        for k in range(n):
            if k in gate_bits:
                bits.append(gate_bits[k])
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


def _run_one_draw(n, pair_a, pair_b, thetas, alpha, reference_pair_thetas, draw_label):
    """Runs dedicated + pooled variants for one (n, pair_a, pair_b, thetas,
    alpha) draw, plus the exact reference, and returns a result dict."""
    gate_qubits = set(pair_a) | set(pair_b)

    proc_ded, anc_a_ded, anc_b_ded = build_two_gate_processor(
        n, pair_a, pair_b, thetas, alpha, mode="dedicated"
    )
    ancilla_modes_ded = anc_a_ded + anc_b_ded
    dist_ded, residual_ded, pfail_ded = postselected_distribution(
        proc_ded, n, ancilla_modes_ded, gate_qubits
    )

    proc_pool, anc_a_pool, anc_b_pool = build_two_gate_processor(
        n, pair_a, pair_b, thetas, alpha, mode="pooled"
    )
    ancilla_modes_pool = anc_a_pool  # same 4 modes for both insertions
    dist_pool, residual_pool, pfail_pool = postselected_distribution(
        proc_pool, n, ancilla_modes_pool, gate_qubits
    )

    reference = exact_qubit_iqp_distribution(n, thetas, pair_thetas=reference_pair_thetas)

    tvd_ded_vs_ref = total_variation_distance(dist_ded, reference)
    tvd_pool_vs_ded = total_variation_distance(dist_pool, dist_ded)
    pfail_delta = abs(pfail_pool - pfail_ded)

    harness_ok = tvd_ded_vs_ref <= THRESHOLD and residual_ded <= THRESHOLD
    if not harness_ok:
        verdict = "HARNESS-FAIL"
    elif tvd_pool_vs_ded <= THRESHOLD and pfail_delta <= THRESHOLD:
        verdict = "GO"
    else:
        verdict = "NO-GO"

    return {
        "draw": draw_label,
        "tvd_dedicated_vs_reference": tvd_ded_vs_ref,
        "residual_dedicated": residual_ded,
        "tvd_pooled_vs_dedicated": tvd_pool_vs_ded,
        "pfail_dedicated": pfail_ded,
        "pfail_pooled": pfail_pool,
        "pfail_delta": pfail_delta,
        "verdict": verdict,
    }


def _print_table(rows, probe_label):
    header = (
        f"{'draw':<10}{'tvd_dedicated_vs_reference':<28}{'tvd_pooled_vs_dedicated':<26}"
        f"{'pfail_dedicated':<18}{'pfail_pooled':<16}{'verdict':<14}"
    )
    print(f"\n--- {probe_label} results ---")
    print(header)
    for r in rows:
        print(
            f"{r['draw']:<10}{r['tvd_dedicated_vs_reference']:<28.3e}"
            f"{r['tvd_pooled_vs_dedicated']:<26.3e}{r['pfail_dedicated']:<18.6f}"
            f"{r['pfail_pooled']:<16.6f}{r['verdict']:<14}"
        )
    return header


def run_probe_n2(alpha=None):
    """Primary decisive probe. n=2, pair_a = pair_b = (0, 1): TWO sequential
    CP(alpha) insertions on the SAME qubit pair. This isolates the exact
    mechanism in question -- does insertion B act on vacuum ancilla, or on
    whatever insertion A left behind? -- at the smallest possible mode count
    (8 modes pooled, 12 dedicated).

    Two draws (asymmetric thetas, per the Phase 19 addendum's finding that
    symmetric/degenerate cases hide convention errors), so a single
    accidental coincidence cannot drive the verdict:
      draw1: alpha=1.0,  theta0=0.3,   theta1=1.1
      draw2: alpha=2.4,  theta0=0.7,   theta1=-0.45

    Reference uses pair_thetas={(0,1): alpha/2.0} -- two sequential
    insertions at alpha compose to exp(i*(alpha/2)*Z_0*Z_1), per the
    ARB-01/ARB-02 operator identity (each insertion folds alpha/4 onto the
    reference's pair_theta)."""
    print(DECISION_RULE_TEXT)

    draws = [
        ("draw1", 1.0, 0.3, 1.1),
        ("draw2", 2.4, 0.7, -0.45),
    ]

    n = 2
    pair = (0, 1)
    rows = []
    for label, a, t0, t1 in draws:
        thetas = [t0, t1]
        reference_pair_thetas = {(0, 1): a / 2.0}
        result = _run_one_draw(n, pair, pair, thetas, a, reference_pair_thetas, label)
        result["alpha"] = a
        rows.append(result)

    _print_table(rows, "n=2 same-pair double-gate probe")
    return rows


def run_probe_n4(alpha=None, time_ceiling_s=15 * 60):
    """Confirmation probe at n=4, pair_a=(0,1), pair_b=(2,3) -- the smallest
    genuinely VERTEX-DISJOINT two-pair instance, the configuration D-02's
    pooling rule actually permits. Mode counts: 12 pooled, 16 dedicated.

    Reference uses pair_thetas={(0,1): alpha/4.0, (2,3): alpha/4.0} -- alpha/4
    per pair, since each pair carries exactly one insertion here (unlike
    run_probe_n2's same-pair double insertion).

    Hard 15-minute wall ceiling (D-04's fallback convention, and Phase 18's
    MemoryError precedent at comparable mode counts -- 18-06-SUMMARY.md). A
    MemoryError or ceiling breach is a REPORTED OUTCOME, not a task failure:
    the exception type and call site are recorded honestly, and the n=2
    same-pair probe is reported as the sole evidence base in that case."""
    print(DECISION_RULE_TEXT)

    draws = [
        ("draw1", 1.0, [0.3, 1.1, -0.6, 0.85]),
        ("draw2", 2.4, [0.7, -0.45, 1.3, 0.05]),
    ]

    n = 4
    pair_a = (0, 1)
    pair_b = (2, 3)
    rows = []
    start = time.monotonic()
    for label, a, thetas in draws:
        elapsed = time.monotonic() - start
        if elapsed > time_ceiling_s:
            raise TimeoutError(
                f"run_probe_n4: exceeded {time_ceiling_s}s wall ceiling after {elapsed:.1f}s "
                f"(D-04 fallback) before completing draw {label}"
            )
        reference_pair_thetas = {(0, 1): a / 4.0, (2, 3): a / 4.0}
        result = _run_one_draw(n, pair_a, pair_b, thetas, a, reference_pair_thetas, label)
        result["alpha"] = a
        rows.append(result)

    _print_table(rows, "n=4 vertex-disjoint two-pair probe")
    return rows


def main():
    parser = argparse.ArgumentParser(
        description="MPAIR-07: pooled-vs-dedicated ancilla reuse evidence for sequential CP(alpha) insertions."
    )
    parser.add_argument("--probe", choices=["n2", "n4"], default="n2")
    parser.add_argument("--alpha", type=float, default=None, help="unused override placeholder; draws are fixed per-plan")
    args = parser.parse_args()

    if args.probe == "n2":
        run_probe_n2(args.alpha)
    else:
        run_probe_n4(args.alpha)


if __name__ == "__main__":
    main()
