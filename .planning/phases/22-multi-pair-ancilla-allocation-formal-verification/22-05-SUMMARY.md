---
phase: 22-multi-pair-ancilla-allocation-formal-verification
plan: 05
subsystem: testing
tags: [forge, edge-colouring, k_n, ancilla-allocation, backtracking-search, mpair-05]

# Dependency graph
requires:
  - phase: 22-multi-pair-ancilla-allocation-formal-verification (Plan 22-04)
    provides: "forge/pooled_ancilla_allocation.frg (search-formulated Forge model) and results/phase22_forge_run_log.md (per-n Forge solve timings, n=4/5/6 converged, n=7/n=8 timed out)"
provides:
  - "pooled_allocation_baseline.py: a genuine colouring SEARCH (greedy upper bound + backtracking-DFS minimum with per-n time ceiling), not a verification loop"
  - "results/phase22_forge_summary.md: the honest Forge-vs-Python-search comparison table and (a)-(d) verdict, quoting Forge's timings from the run log rather than re-measuring them"
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Backtracking-DFS minimum colouring with most-constrained-first (descending-degree) vertex ordering as the fair Python-side analogue of Forge's colouringExists/minimality test-block pair -- both FIND a colouring at K and PROVE infeasibility at K-1, or the comparison would not be fair."
    - "Naive subset-enumeration cost measured as a SECONDARY, explicitly-labelled data point (bitmask iteration over 2^C(n,2), not itertools.combinations, after an initial slow implementation was rewritten for enumeration speed) -- kept separate from the primary pairwise-reduced comparison to avoid inflating Forge's apparent advantage."

key-files:
  created:
    - pooled_allocation_baseline.py
    - results/phase22_forge_summary.md
  modified: []

key-decisions:
  - "The corrected MPAIR-05 grading axis (criteria (a)-(d), not brute-force-timing) is applied throughout, with an explicit statement that the standard was corrected mid-phase rather than graded on the new axis as if it had always applied -- ARB-09's audit used the old axis too."
  - "naive_subset_scan was rewritten from an itertools.combinations(pair_list, r) nested-loop implementation (too slow to reach n=7 within a 60s test budget) to a bitmask-iteration implementation with a precomputed conflict-index-pair list and a 20000-iteration time-poll interval -- the first version's per-subset overhead was itself measuring Python object-construction cost, not enumeration cost, which would have misrepresented the SECONDARY data point."
  - "The full `--n-max 8` default-ceiling run (~11 minutes, dominated by the SECONDARY naive-subset-scan hitting its 600s ceiling at n=8) was executed via a backgrounded Bash process rather than a single foreground call, since it exceeds the 10-minute single-command timeout -- exit code and full stdout were captured and verified before proceeding."

requirements-completed: [MPAIR-05]

# Metrics
duration: ~55min
completed: 2026-08-21
---

# Phase 22 Plan 05: Forge-vs-Brute-Force Baseline and Honest Verdict Summary

**Backtracking-DFS colouring search matches Forge's minimum K exactly at every n Forge reached (4, 5, 6) and additionally solves n=7 (2.28s) and n=8 (0.006s) where Forge's own exhaustive SAT-backed search timed out at n=7 (~610s, zero blocks resolved) — Forge did not earn its place here either, verdict recorded as passing per the corrected MPAIR-05 criterion.**

## Performance

- **Duration:** ~55 min
- **Started:** 2026-08-21
- **Completed:** 2026-08-21
- **Tasks:** 2/2 completed
- **Files modified:** 2 created

## Accomplishments

- `pooled_allocation_baseline.py` implements `edges`, `conflicts`, `greedy_colouring`, `backtracking_min_colouring`, `round_robin_colour`, `check_round_robin`, and `naive_subset_scan` as specified, and runs cleanly at `--n-max 8` (exit 0).
- **Backtracking search agrees with Forge's minimum K exactly at n=4 (K=3), n=5 (K=5), n=6 (K=5)** — no disagreement to report.
- **Backtracking search additionally solves n=7 (K=7, 2.284s) and n=8 (K=7, 0.006s)**, both beyond Forge's converging bound — the comparison that answers the interesting question this plan exists to ask. Combined n=4..8 backtracking wall time: ~2.29 seconds.
- **`round_robin_proper` is True for every n from 2 to 8**, and `round_robin_K` equals `n-1` for even n and `n` for odd n throughout — the closed-form formula independently checked correct.
- **SECONDARY naive subset scan**: completed n=2..7 fully (n=7 in 46.13s, 2,097,152 of 2,097,152 subsets), timed out at n=8 after checking 18,080,000 of 268,435,456 subsets (~6.7%) in the 600s ceiling — confirms the original `2^28`-subset framing genuinely would have been intractable, which is what licenses the pairwise reduction both Forge and the Python search actually use.
- **Verdict** (`results/phase22_forge_summary.md`, `## What Forge alone contributed`): *"A few hundred lines of backtracking Python reached the same minimum faster, and reached further, than Forge's SAT-backed exhaustive search."* At the domain both converge on (n=4..6), Forge is ~123,000x slower than the Python search (~369s vs ~0.003s); at n=7/n=8, Forge did not converge at all where Python solved both in under 2.3 seconds combined.
- Criteria (a)-(d) addressed by name: (a) no — the scenario space was already fully enumerated in prose before any Forge code existed; (b) no — this is a static combinatorial property, not a trace/reachability question (that's Phase 23's LIFE-01..07); (c) yes, partially — modest precision gain, since the prose invariant was already careful; (d) yes — no Python implements pooled allocation yet, so both Forge and this baseline verify a design before it's built.
- Explicit statement that the brute-force-timing standard was the wrong axis and was corrected mid-phase (2026-08-21), not graded on the new axis as if it had always applied — ARB-09's audit used the old axis too.
- Known-theorem caveat restated: chromatic index of K_n is `n-1` (even) / `n` (odd), König/Vizing — both tools confirm known combinatorics, neither settles an open problem.
- `venv/Scripts/python.exe -m pytest -q` reports **296 passed**, unchanged from before this plan. `grep -rn "pooled_allocation_baseline" tests/` returns nothing — the script stays outside `pytest.ini`'s `testpaths = tests`.

## Task Commits

1. **Task 1: Build and time the colouring-search baseline** - `c1d2c71` (feat)
2. **Task 2: Write the Forge-vs-brute-force comparison and the honest verdict** - `fde0178` (docs)

**Plan metadata:** (this commit, pending)

## Files Created/Modified

- `pooled_allocation_baseline.py` - greedy + backtracking-DFS minimum colouring search, closed-form round-robin formula reimplementation and checker, and a SECONDARY naive subset-enumeration cost measurement, all over K_n's edge set mirroring `forge/pooled_ancilla_allocation.frg`'s predicates.
- `results/phase22_forge_summary.md` - what was modeled, bound checked, verbatim Forge n=6 output, Forge-vs-Python comparison table (timings quoted from `results/phase22_forge_run_log.md`, not re-measured), SECONDARY subset-scan row, the corrected (a)-(d) verdict, and the scope boundary against MPAIR-07's physics ruling.

## Decisions Made

- Applied the corrected MPAIR-05 grading axis (criteria (a)-(d) rather than brute-force-timing as the pass/fail axis) throughout, per `REQUIREMENTS.md`'s 2026-08-21 correction note, with runtime kept as one reported data point rather than the verdict itself.
- Rewrote `naive_subset_scan` mid-task from an `itertools.combinations`-based nested-loop implementation to bitmask iteration with a precomputed conflict-index-pair list, after the first version failed to reach `n=7` within a 60-second test budget (1.47M of 2.1M subsets checked) — the original implementation's per-subset Python-object-construction overhead was measuring itself, not the enumeration cost this SECONDARY data point is meant to report. [Rule 1 - Bug, self-caught during Task 1 verification, before any commit.]
- Ran the full `--n-max 8` default-ceiling verification command (~11 minutes total, dominated by the naive subset scan's 600s ceiling hit at n=8) as a backgrounded process rather than a single foreground call, since it exceeds a single Bash command's 10-minute timeout ceiling; captured and verified full stdout (exit 0) before proceeding to write the comparison document.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `naive_subset_scan` too slow to complete its stated purpose within the time budget**
- **Found during:** Task 1, initial implementation test at n=7 with a 60s time budget
- **Issue:** The first `naive_subset_scan` implementation used `itertools.combinations(pair_list, r)` plus a nested `itertools.combinations(subset, 2)` collision check per subset, and polled `time.time()` every single subset. At n=7 (2,097,152 total subsets) this only reached 1,472,926 (70%) in 60 seconds — the per-subset Python overhead dominated, meaning the measured cost reflected object-construction overhead rather than the enumeration cost the function is documented to report.
- **Fix:** Rewrote using direct bitmask iteration over `range(2**m)` with a precomputed list of conflicting index-pairs and an early-break inner check, polling `time.time()` only every 20,000 iterations instead of every iteration.
- **Files modified:** `pooled_allocation_baseline.py`
- **Verification:** Re-ran at n=7 with a 60s budget: completed all 2,097,152 subsets in 46.13s (previously timed out at 70% coverage). Full `--n-max 8` run subsequently reached n=8 and reported 18,080,000 of 268,435,456 subsets checked before the 600s ceiling — a measured, not artificially-slow, SECONDARY data point.
- **Committed in:** `c1d2c71` (Task 1 commit; the rewrite happened before any commit was made, so no separate fix commit exists)

---

**Total deviations:** 1 auto-fixed (bug, self-caught during pre-commit verification — no scope or property change; the function's documented purpose and signature were unchanged, only the internal implementation).
**Impact on plan:** Necessary for the SECONDARY data point to actually measure what it claims to measure. No scope creep.

## Issues Encountered

- The default `--time-ceiling 600` full run (`pooled_allocation_baseline.py --n-max 8`) takes ~11 minutes wall time in total, almost entirely spent in the SECONDARY naive subset scan hitting its ceiling at n=8 (the primary backtracking search itself completes n=2..8 in ~2.3 seconds combined). This exceeds a single Bash tool call's 10-minute timeout, so it was run as a backgrounded process and polled to completion rather than as one foreground call. No change to the script or its documented CLI was needed — this is an execution-environment note, not a plan deviation.

## User Setup Required

None — no external service configuration required. Python standard library only, no new packages.

## Next Phase Readiness

- MPAIR-05 is satisfied: a genuine colouring SEARCH was run and timed over the same bounded domain Forge covers, agreement is exact at every n both reached, and the phase states plainly — with the measured ratio — that Forge's exhaustive search did not earn its place here, per the corrected (a)-(d) criterion.
- **Verdict sentence for Plan 22-06 to reproduce verbatim, without softening:** *"A few hundred lines of backtracking Python reached the same minimum faster, and reached further, than Forge's SAT-backed exhaustive search."*
- Plan 22-06 (MPAIR-06, recording the verified scheme as a specification in `docs/iqp-photonic-encoding.md`) can proceed — this plan's honest timing/verdict content is ready to be folded in without modification.
- Phase 23 (LIFE-01..07, ancilla lifecycle safety) remains the trace/reachability counterpart flagged in criterion (b) above as the case this phase's static colouring model does not cover.

---
*Phase: 22-multi-pair-ancilla-allocation-formal-verification*
*Completed: 2026-08-21*

## Self-Check: PASSED

- FOUND: pooled_allocation_baseline.py
- FOUND: results/phase22_forge_summary.md
- FOUND: commit c1d2c71
- FOUND: commit fde0178
