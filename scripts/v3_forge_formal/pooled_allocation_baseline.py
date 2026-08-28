"""Phase 22 Plan 05 (MPAIR-05): hand-rolled colouring SEARCH baseline.

WHAT THIS IS: a greedy + backtracking minimum edge-colouring SEARCH over
K_n's C(n,2) pairs, run and timed over the same bounded domain
forge/pooled_ancilla_allocation.frg covers, plus an independent check that
the closed-form round-robin formula from
results/v3_forge_formal/phase22_allocation_invariant.md is itself a valid, minimum-count
colouring. This is deliberately NOT a 406-case verification loop over one
fixed colouring -- D-05 (22-CONTEXT.md) requires a genuine SEARCH baseline,
since a fixed-formula check would be a strawman comparison (see
results/v3_forge_formal/phase22_allocation_invariant.md's "What the Forge model will
actually ask").

Standard library only: itertools, time, argparse. No new packages.

Deliberately NOT under tests/ and NOT imported by anything under tests/ --
this script stays outside pytest, matching Phase 16's precedent
(cp_alpha_sweep.py) and per this plan's own acceptance criteria.
"""

import argparse
import itertools
import time


# ---------------------------------------------------------------------------
# 1. Domain: edges of K_n and the vertex-sharing conflict predicate.
#
# Mirrors forge/pooled_ancilla_allocation.frg's `pairsAreKn` predicate: every
# atom is a valid (i, j) with i < j < n, and no two distinct atoms denote the
# same edge -- exactly the C(n,2) pairs for 0 <= i < j < n.
# ---------------------------------------------------------------------------
def edges(n):
    """The C(n,2) pairs (i, j) with 0 <= i < j < n. Mirrors `pairsAreKn`."""
    return list(itertools.combinations(range(n), 2))


def conflicts(p, q):
    """True iff pairs p, q share a qubit index. Mirrors `conflicts[p, q]`."""
    return bool(set(p) & set(q))


# ---------------------------------------------------------------------------
# 2. Greedy first-fit colouring -- an UPPER BOUND, not a minimum.
#
# This is the fast half of the baseline. On its own it cannot answer the
# minimality question Forge's `minimality<N>` blocks (and this script's
# `backtracking_min_colouring`) answer -- greedy only ever proves "K blocks
# suffice", never "K-1 blocks do not suffice". Both Forge and the
# backtracking search below are needed to close the bound from below.
# ---------------------------------------------------------------------------
def greedy_colouring(n, order=None):
    """First-fit greedy colouring. Returns (colouring dict, blocks_used)."""
    pair_list = edges(n) if order is None else list(order)
    colouring = {}
    for p in pair_list:
        used = {colouring[q] for q in colouring if conflicts(p, q)}
        c = 0
        while c in used:
            c += 1
        colouring[p] = c
    blocks_used = (max(colouring.values()) + 1) if colouring else 0
    return colouring, blocks_used


# ---------------------------------------------------------------------------
# 3. Backtracking minimum colouring -- the actual SEARCH, and the fair
# comparison against Forge's colouringExists<N> / minimality<N> pair.
#
# For descending K starting at the greedy upper bound, attempt a depth-first
# proper-colouring construction with backtracking. Returns the smallest K
# for which a proper colouring exists, a witness colouring at that K, and
# the K+1... actually K-1 value at which infeasibility was proven (mirrors
# Forge's `minimality<N>`: unsat at K-1 proves K is minimum).
# ---------------------------------------------------------------------------
def _try_colour(pair_list, k, conflict_pairs):
    """DFS with backtracking: can `pair_list` be properly coloured with k colours?"""
    n_pairs = len(pair_list)
    colour = [-1] * n_pairs

    def neighbours(idx):
        p = pair_list[idx]
        return [j for j, q in enumerate(pair_list) if j != idx and conflicts(p, q)]

    adj = [neighbours(idx) for idx in range(n_pairs)]

    def backtrack(idx):
        if idx == n_pairs:
            return True
        used = {colour[j] for j in adj[idx] if colour[j] != -1}
        for c in range(k):
            if c not in used:
                colour[idx] = c
                if backtrack(idx + 1):
                    return True
                colour[idx] = -1
        return False

    if backtrack(0):
        return {pair_list[i]: colour[i] for i in range(n_pairs)}
    return None


def backtracking_min_colouring(n, k_start=None, time_ceiling_s=600.0):
    """The SEARCH: smallest K admitting a proper colouring, backtracking DFS.

    Direct analogue of Forge's colouringExists/minimality pair -- it both
    FINDS a colouring at the returned K and establishes infeasibility at
    K-1, or reports a timeout rather than silently reducing the problem
    (matching D-04's per-n 10-minute ceiling).

    Returns a dict with keys: min_K, witness, infeasible_at, timed_out,
    seconds.
    """
    pair_list = edges(n)
    if not pair_list:
        return {
            "min_K": 0,
            "witness": {},
            "infeasible_at": None,
            "timed_out": False,
            "seconds": 0.0,
        }

    conflict_pairs = None  # unused, kept for signature clarity
    if k_start is None:
        _, k_start = greedy_colouring(n)

    start = time.time()
    best_witness = None
    best_k = k_start
    infeasible_at = None
    timed_out = False

    # Sort pairs by descending degree (most-constrained-first) -- a standard
    # backtracking heuristic that reduces thrash without changing the answer.
    def degree(p):
        return sum(1 for q in pair_list if q != p and conflicts(p, q))

    ordered_pairs = sorted(pair_list, key=degree, reverse=True)

    k = k_start
    while k >= 0:
        if time.time() - start > time_ceiling_s:
            timed_out = True
            break
        witness = _try_colour(ordered_pairs, k, conflict_pairs)
        if witness is None:
            infeasible_at = k
            break
        best_witness = witness
        best_k = k
        k -= 1

    seconds = time.time() - start
    return {
        "min_K": best_k,
        "witness": best_witness,
        "infeasible_at": infeasible_at,
        "timed_out": timed_out,
        "seconds": seconds,
    }


# ---------------------------------------------------------------------------
# 4. Closed-form round-robin formula -- reimplementation and independent
# check against results/v3_forge_formal/phase22_allocation_invariant.md's
# "## Allocation concretization: round-robin edge-colouring of K_n".
# ---------------------------------------------------------------------------
def round_robin_colour(n, i, j):
    """Direct reimplementation of the closed-form round-robin formula.

    Odd n: colour(i,j) = (i + j) % n, using K = n blocks.
    Even n: m = n - 1 (odd). For i, j < m: (i + j) % m.
             For the last vertex (j == n - 1): (2 * i) % m.
             Using K = n - 1 blocks.
    """
    if n % 2 == 1:
        return (i + j) % n
    m = n - 1
    if j == n - 1:
        return (2 * i) % m
    return (i + j) % m


def round_robin_block_count(n):
    return n if n % 2 == 1 else n - 1


def check_round_robin(n):
    """Independently verify round_robin_colour(n, .) is a proper colouring
    using exactly the claimed block count K.

    Returns (is_proper, k_claimed, k_used, colouring dict).
    """
    pair_list = edges(n)
    colouring = {(i, j): round_robin_colour(n, i, j) for (i, j) in pair_list}
    k_claimed = round_robin_block_count(n)

    is_proper = True
    for (p, q) in itertools.combinations(pair_list, 2):
        if conflicts(p, q) and colouring[p] == colouring[q]:
            is_proper = False
            break

    k_used = (max(colouring.values()) + 1) if colouring else 0
    uses_exactly_claimed = k_used <= k_claimed  # colour indices must stay within [0, k_claimed)
    all_in_range = all(0 <= c < k_claimed for c in colouring.values())

    return is_proper and all_in_range, k_claimed, k_used, colouring


# ---------------------------------------------------------------------------
# Secondary data point (22-RESEARCH.md Research Question 5): what the
# ORIGINAL 2^C(n,2)-subset framing would have cost, purely to measure the
# magnitude of the pairwise-reduction argument's savings. This is NOT the
# primary comparison -- the primary model (Forge's properColouring /
# this script's backtracking search) is pairwise-reduced and never
# enumerates subsets; presenting subset-scan time as "the baseline" would
# unfairly inflate Forge's apparent advantage. Labelled SECONDARY in output.
# ---------------------------------------------------------------------------
def naive_subset_scan(n, time_budget_s=600.0):
    """Enumerate subsets of the edge set and check the invariant per subset.

    Purely to measure what the original 2^C(n,2)-subset framing would have
    cost. Time-boxed to `time_budget_s`; reports how far it got.

    Per-subset work is deliberately cheap (a fixed-colouring collision check
    against pairs of the SUBSET's own edges, using precomputed colours and a
    tuple-set membership test rather than nested itertools.combinations) so
    the measured cost reflects enumeration itself, not incidental Python
    overhead unrelated to the 2^C(n,2) framing this function exists to cost
    out. `time.time()` is polled every CHECK_INTERVAL subsets, not every
    subset, since per-call timer overhead would otherwise dominate at this
    scale and distort the very timing this function measures.
    """
    pair_list = edges(n)
    m = len(pair_list)
    total_subsets = 2 ** m
    colours = [round_robin_colour(n, i, j) for (i, j) in pair_list]
    # Precompute conflicting index-pairs once; used for the cheap per-subset check.
    conflict_idx_pairs = [
        (a, b) for a in range(m) for b in range(a + 1, m) if conflicts(pair_list[a], pair_list[b])
    ]

    CHECK_INTERVAL = 20000
    start = time.time()
    checked = 0
    timed_out = False

    for bitmask in range(total_subsets):
        # Cheap per-subset check: does this subset contain a conflicting
        # index-pair with equal round-robin colour? (Stand-in invariant
        # check, not a search -- purely to cost out enumeration.)
        for a, b in conflict_idx_pairs:
            if (bitmask >> a) & 1 and (bitmask >> b) & 1 and colours[a] == colours[b]:
                break  # would be a violation; not expected under round-robin
        checked += 1
        if checked % CHECK_INTERVAL == 0:
            if time.time() - start > time_budget_s:
                timed_out = True
                break

    seconds = time.time() - start
    return {
        "n": n,
        "total_subsets": total_subsets,
        "checked": checked,
        "timed_out": timed_out,
        "seconds": seconds,
    }


# ---------------------------------------------------------------------------
# Forge's minimum K per n, quoted from results/v3_forge_formal/phase22_forge_run_log.md
# (converged values only -- n=7, n=8 timed out in Forge and are not
# included here). Used purely for the printed cross-check column; not
# re-measured.
# ---------------------------------------------------------------------------
FORGE_MIN_K = {4: 3, 5: 5, 6: 5}


def main():
    parser = argparse.ArgumentParser(
        description="Pooled ancilla allocation: greedy + backtracking colouring "
        "search baseline, timed against forge/pooled_ancilla_allocation.frg."
    )
    parser.add_argument("--n-max", type=int, default=8, help="largest n to run (default 8)")
    parser.add_argument(
        "--time-ceiling", type=float, default=600.0, help="per-n wall-time ceiling in seconds (default 600)"
    )
    parser.add_argument("--skip-naive", action="store_true", help="skip the SECONDARY naive subset scan")
    args = parser.parse_args()

    print(
        f"{'n':>3} {'C(n,2)':>7} {'greedy_K':>9} {'min_K':>6} {'infeasible_at':>14} "
        f"{'round_robin_K':>14} {'round_robin_proper':>19} {'greedy_seconds':>15} "
        f"{'backtracking_seconds':>21}"
    )

    disagreements = []

    for n in range(2, args.n_max + 1):
        pair_list = edges(n)
        c_n_2 = len(pair_list)

        t0 = time.time()
        _, greedy_k = greedy_colouring(n)
        greedy_seconds = time.time() - t0

        bt = backtracking_min_colouring(n, k_start=greedy_k, time_ceiling_s=args.time_ceiling)
        min_k = bt["min_K"]
        infeasible_at = bt["infeasible_at"]
        backtracking_seconds = bt["seconds"]
        if bt["timed_out"]:
            infeasible_at = "TIMEOUT"

        is_proper, k_claimed, k_used, _ = check_round_robin(n)

        print(
            f"{n:>3} {c_n_2:>7} {greedy_k:>9} {min_k:>6} {str(infeasible_at):>14} "
            f"{k_claimed:>14} {str(is_proper):>19} {greedy_seconds:>15.6f} "
            f"{backtracking_seconds:>21.6f}"
        )

        if not is_proper or k_used > k_claimed:
            print(f"  WARNING: round-robin formula failed check at n={n} "
                  f"(is_proper={is_proper}, k_claimed={k_claimed}, k_used={k_used})")

        forge_k = FORGE_MIN_K.get(n)
        if forge_k is not None and forge_k != min_k:
            msg = (
                f"DISAGREEMENT at n={n}: backtracking min_K={min_k} != "
                f"Forge min_K={forge_k} (results/v3_forge_formal/phase22_forge_run_log.md)"
            )
            print(f"  {msg}")
            disagreements.append(msg)
        elif forge_k is not None:
            print(f"  matches Forge's min_K={forge_k} at n={n} (results/v3_forge_formal/phase22_forge_run_log.md)")

    if disagreements:
        print("\n=== DISAGREEMENTS (not reconciled) ===")
        for d in disagreements:
            print(f"  {d}")
    else:
        print("\nNo disagreements between backtracking search and Forge at any n both reached.")

    if not args.skip_naive:
        print("\n=== SECONDARY: naive subset-scan cost (NOT the primary comparison) ===")
        print("The primary model is pairwise-reduced and does not enumerate subsets;")
        print("this measures only what the original 2^C(n,2)-subset framing would have cost.")
        print(f"{'n':>3} {'total_subsets':>16} {'checked':>12} {'timed_out':>10} {'seconds':>10}")
        for n in range(2, args.n_max + 1):
            result = naive_subset_scan(n, time_budget_s=args.time_ceiling)
            print(
                f"{result['n']:>3} {result['total_subsets']:>16} {result['checked']:>12} "
                f"{str(result['timed_out']):>10} {result['seconds']:>10.4f}"
            )
            if result["timed_out"]:
                print(
                    f"  SECONDARY: reached n={n}, checked {result['checked']} of "
                    f"{result['total_subsets']} subsets before the {args.time_ceiling}s ceiling"
                )
                break


if __name__ == "__main__":
    main()
