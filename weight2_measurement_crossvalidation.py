import perceval as pcvl

import sys
sys.path.insert(0, ".")
from iqp_photonic_encoding import (
    build_weight2_processor,
    fock_to_bitstring,
    photonic_weight2_iqp_distribution,
)

# Phase 12 follow-up (2026-08-07): cross-validates the herald-free
# measurement path (`photonic_weight2_iqp_distribution`, built in Phase 12
# to route around a Perceval `add_herald()`+`PBS` crash in `Processor.probs()`)
# against the DIRECT, herald-registered production path
# (`build_weight2_processor`, which has always called `proc.add_herald()`
# internally) -- now that 2026-08-07's corrected understanding shows the
# crash only triggers when the herald mode(s) are OMITTED from
# `Processor.with_input()` and left to auto-fill, not whenever
# `add_herald()`+`PBS` are combined (see
# `~/.claude/learnings/2026-08-06-perceval-polarizationsimulator-heralds-crash.md`
# addendum). Supplying the herald ancilla modes explicitly, `{P:V}`-annotated,
# avoids the crash entirely and lets `.probs()` run directly on the real
# production processor.
#
# This does NOT replace the herald-free path (still correct, still the
# 100+-test-covered production measurement helper) -- it's an additional,
# independent confirmation that both measurement strategies agree, run at
# the exact points Phase 12's own research already validated:
#   1. The locked TVD validation point: n=2, i=0, j=1, pure weight-2 (theta=0
#      before internal +pi/4 folding).
#   2. The robustness/bystander-qubit point: n=3, pair (1,2), qubit 0 at
#      theta=0.6 mixed in on top of the weight-2 pair term.

TOLERANCE = 1e-9


def direct_herald_distribution(n, i, j, thetas):
    """The direct, add_herald()-registered analogue of
    photonic_weight2_iqp_distribution: builds build_weight2_processor(n, i,
    j, thetas) (the actual production processor, herald already registered),
    supplies an explicit {P:V}-annotated ancilla input (avoiding the
    auto-fill crash), and reads the herald-conditioned distribution directly
    off Processor.probs() -- no manual post-selection needed, since a
    registered herald already restricts .probs()'s output to the
    herald-surviving subspace and reports the herald-success probability as
    global_perf.

    Returns (dist, residual, herald_success_prob) -- same shape as
    photonic_weight2_iqp_distribution's (dist, residual, herald_failure_prob)
    modulo the success/failure convention, for direct comparison."""
    proc = build_weight2_processor(n, i, j, thetas)
    input_state = pcvl.BasicState(
        "|" + ",".join(["{P:H},0"] * n) + ",{P:V},{P:V}>"
    )
    proc.with_input(input_state)
    probs = proc.probs()

    dist = {}
    residual = 0.0
    for state, p in probs["results"].items():
        p_real = complex(p).real
        bits = fock_to_bitstring(state, n)
        if bits is None:
            residual += p_real
        else:
            dist[bits] = dist.get(bits, 0.0) + p_real

    return dist, residual, probs["global_perf"]


def compare(n, i, j, thetas, label):
    dist_ref, residual_ref, herald_failure_ref = photonic_weight2_iqp_distribution(
        n, i, j, thetas
    )
    dist_direct, residual_direct, herald_success_direct = direct_herald_distribution(
        n, i, j, thetas
    )
    herald_success_ref = 1.0 - herald_failure_ref

    keys = set(dist_ref) | set(dist_direct)
    max_dist_diff = max(
        abs(dist_ref.get(k, 0.0) - dist_direct.get(k, 0.0)) for k in keys
    )
    residual_diff = abs(residual_ref - residual_direct)
    herald_diff = abs(herald_success_ref - herald_success_direct)

    print(f"--- {label} (n={n}, i={i}, j={j}, thetas={thetas}) ---")
    print(f"  herald-free (ref):    dist={dist_ref}")
    print(f"  direct add_herald():  dist={dist_direct}")
    print(f"  herald success -- ref: {herald_success_ref!r}  direct: {herald_success_direct!r}")
    print(f"  max dist diff: {max_dist_diff:.3e}  residual diff: {residual_diff:.3e}  herald diff: {herald_diff:.3e}")

    return max_dist_diff, residual_diff, herald_diff


def main():
    diffs = []
    diffs.append(compare(2, 0, 1, [0.0, 0.0], "locked TVD validation point"))
    diffs.append(
        compare(3, 1, 2, [0.6, 0.0, 0.0], "robustness / bystander-qubit point")
    )

    all_pass = all(d <= TOLERANCE for diff_set in diffs for d in diff_set)
    print()
    print(f"All checks agree within {TOLERANCE:.0e}: {'PASS' if all_pass else 'FAIL'}")

    for max_dist_diff, residual_diff, herald_diff in diffs:
        assert max_dist_diff <= TOLERANCE, f"dist mismatch: {max_dist_diff}"
        assert residual_diff <= TOLERANCE, f"residual mismatch: {residual_diff}"
        assert herald_diff <= TOLERANCE, f"herald-success mismatch: {herald_diff}"

    print()
    print("Both measurement paths agree. The herald-free path remains the")
    print("production measurement helper (unchanged); this confirms the")
    print("direct add_herald() path is also valid, now that the crash's")
    print("actual trigger (auto-fill omission) is understood.")


if __name__ == "__main__":
    main()
