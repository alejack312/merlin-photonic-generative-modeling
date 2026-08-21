---
phase: 22-multi-pair-ancilla-allocation-formal-verification
plan: 04
subsystem: forge-verification
tags: [forge, edge-colouring, k_n, ancilla-allocation, mpair-03, mpair-04]

# Dependency graph
requires:
  - phase: 22-multi-pair-ancilla-allocation-formal-verification (Plans 22-01/22-02/22-03)
    provides: "results/phase22_reuse_gate.md (owner GO ruling on ancilla-mode reuse validity) and results/phase22_allocation_invariant.md (owner-confirmed vertex-disjoint compatibility rule, round-robin edge-colouring formula, pairwise-reduction argument, recomputed for-7-Int bitwidth justification)"
provides:
  - "forge/pooled_ancilla_allocation.frg: a NEW search-formulated Forge model (K_n minimum edge-colouring existence/minimality) alongside the untouched forge/ancilla_mapping.frg"
  - "results/phase22_forge_run_log.md: per-n solve timings and the honest D-04 bound-outcome finding (n=6 converged, n=7/n=8 hit the 10-minute ceiling)"
affects: [22-05]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Search-formulated (not verify-a-fixed-formula) Forge model: Alloc.block is a free sig field the solver searches over, with the round-robin formula deliberately absent from the model so agreement between Forge's independent minimum and the hand-constructed witness is a confirming result, not an input constraint."
    - "func Pair -> Int (total-function relation) as the correct Forge idiom for a per-atom scalar field, rather than the initially-attempted 'Pair -> one Int' inline-multiplicity form, which does not parse as a sig field declaration."
    - "Isolated, reduced-workload timeout probe before committing a larger n to the live suite (probed n=7 with 2 of 4 blocks in a scratch file first, rather than extending and re-running the full n=4..6 suite each time) -- cheaper way to discover a ceiling hit without repeatedly re-solving already-converged n values."

key-files:
  created:
    - forge/pooled_ancilla_allocation.frg
    - results/phase22_forge_run_log.md
  modified: []

key-decisions:
  - "Bound-clause syntax: the comma form (`for 7 Int, exactly N Pair`), not the official docs' repeated-`for` form (`for 7 Int for exactly N Pair`), is what actually parses inside a `test expect` block under Forge v5.2 in this environment -- verified live (repeated-`for` produced a parse error), matching every local example file's own comma-form usage."
  - "n=7 and n=8 were not force-fit into the live suite: D-04's ceiling was hit at n=7 (a reduced 2-block probe killed after ~610s with zero blocks resolved), so both are commented out in the model with the measured cutoff time, and n=6 remains the largest live/converging bound -- per D-04, this non-convergence is itself the reported result, not something to work around."
  - "n=8 was not separately attempted once n=7 (a strictly smaller problem on every axis) had already exceeded the ceiling -- climbing further would not produce a different reportable outcome, and D-04's ceiling is stated per-n, not as license to keep retrying at larger n."

patterns-established:
  - "For a Forge search-formulated model where a fixed-formula witness already exists in prose (here, the round-robin colouring), agreement between the independent search's minimum and the witness is the confirming evidence -- never encode the witness formula into the searched-over predicates, or the search collapses back into a verification."

# Metrics
duration: ~35min
completed: 2026-08-21
---

# Phase 22 Plan 04: Search-Formulated Forge Model for Pooled Ancilla Allocation Summary

**Built `forge/pooled_ancilla_allocation.frg`, a Forge model that SEARCHES for a minimum ancilla-block edge-colouring of `K_n` (not verifying a fixed formula), confirming Forge's independent minimum matches the round-robin formula's `K` at n=4/5/6 (both parities) before the search hit D-04's 10-minute ceiling at n=7 -- honestly reported rather than shrunk to fit.**

## Performance

- **Duration:** ~35 minutes (model authoring + one syntax-fix iteration + n=4..6 solve run [~6m9s] + isolated n=7 timeout probe [~10m10s, killed] + run log + summary)
- **Started:** 2026-08-21
- **Completed:** 2026-08-21
- **Tasks:** 3/3 completed (Task 1 skeleton, Task 2 test suite, and Task 3 scale-and-log were implemented together as one build-then-verify pass; commits below map to the two output files)
- **Files modified:** 2 created

## Accomplishments

- `forge/pooled_ancilla_allocation.frg` exists as a genuinely new file (`git diff --stat forge/ancilla_mapping.frg` is empty across the whole plan) with all six required predicates (`pairsAreKn`, `conflicts`, `blocksInRange`, `properColouring`, `ancillaDisjointFromDataPorts`, `genuinePooling`) and a 12-block `test expect` suite, all passing (`racket forge/pooled_ancilla_allocation.frg` exits 0).
- **Minimum K found by search, per n (all matching the round-robin formula exactly):**
  - `n=4` (even): `K=3`
  - `n=5` (odd): `K=5`
  - `n=6` (even): `K=5`
  - `n=7`/`n=8`: not established -- search hit the D-04 ceiling before converging (see Bound outcome below).
- MPAIR-04's strengthened non-vacuity guard (`genuinePooling`, requiring two mutually-compatible pairs to actually share a block, conjoined with `properColouring`) passes at all three converged `n`.
- Data-port disjointness confirmed unsat-of-violation at all three converged `n` (the fully general property, checked rather than assumed, matching Phase 16's precedent).
- Bitwidth recomputed and justified in-header against this model's own largest computed value (43 at the D-03 target n=8), landing on `for 7 Int` ([-64,63]) rather than copying `ancilla_mapping.frg`'s `for 6 Int` (whose own max was only 19) -- `for 6 Int` appears in the file only inside explanatory comments, never in a live bound clause.
- `results/phase22_forge_run_log.md` records the honest D-04 finding: `n=6` is the largest converging bound (~6m9s total wall time for the 12-block suite); `n=7` was probed in isolation (a reduced 2-block workload) and killed after ~610s with zero blocks resolved, exceeding the 600s/10-minute ceiling; `n=8` was not separately attempted since the smaller `n=7` problem had already timed out.

## Task Commits

1. **Task 1 (model skeleton, predicates, bitwidth) + Task 2 (test suite, n=4/5/6)** - `65b8f32` (feat) - both tasks landed in a single commit since the model was authored, debugged (one syntax fix: `func Pair -> Int` in place of an invalid `Pair -> one Int` field form), and verified against n=4/5/6 as one build-then-verify pass before any commit was made.
2. **Task 3 (n=7/n=8 scale attempt and run log)** - `8de060e` (docs)

**Plan metadata:** (this commit, pending)

## Files Created/Modified

- `forge/pooled_ancilla_allocation.frg` - search-formulated Forge model: six predicates, one `test expect` suite (12 live blocks at n=4/5/6; n=7/n=8 blocks present but commented out with the measured D-04 cutoff), header citing `results/phase22_allocation_invariant.md`, `iqp_photonic_encoding.py`, and `results/phase22_reuse_gate.md`.
- `results/phase22_forge_run_log.md` - per-n solve-timing table (Forge's own `Solving (ms)`/`Transl (ms)` output, quoted verbatim for `n=6`), `## Bound outcome`, and `## Empirical bound-finding procedure` sections.

## Decisions Made

- **Bound-clause syntax resolved by direct test, not assumption:** the official docs' repeated-`for` run-block form (`for 7 Int for exactly 6 Pair`) does not parse inside a `test expect` block's trailing bound clause under Forge v5.2 here (produced a loud parse error at the second `for`, exactly as `22-CONTEXT.md` anticipated it might be loud-not-silent if wrong). The comma form (`for 7 Int, exactly 6 Pair`), matching every local example file's own usage, is what the file actually uses.
- **`func Pair -> Int`, not `Pair -> one Int`, for the sig field:** the initial attempt to declare `Alloc.block` as `Pair -> one Int` failed to parse. Cross-checked against installed local Forge example files (`buckets.frg`, `binarysearch.frg`, `bst.frg` use `pfunc`/plain `one Int` field forms; `restricting_space.frg` uses `pfunc Int -> Int`) and corrected to `func Pair -> Int` (total function, since every `Pair` atom must have exactly one block under `blocksInRange`'s constraints) -- `[Rule 3 - Blocking]` auto-fix, since this was a syntax error preventing any further verification, not an architectural change.
- **n=7 probed in isolation before committing to the full 4-block addition:** rather than extending the live model's `test expect` suite to `n=7` (which would re-solve the already-converged `n=4..6` blocks on every subsequent `racket` invocation while iterating), a scratch file with a reduced 2-block subset (`colouringExistsN7`, `minimalityN7` only) was run first. It alone exceeded the 10-minute ceiling, which settled the question without repeatedly paying the ~6-minute `n=4..6` re-solve cost.
- **n=8 not separately attempted:** once `n=7` (strictly smaller than `n=8` on every axis: fewer `Pair` atoms, a smaller `Config.kmax` range) had already exceeded the ceiling with a smaller workload than `n=8` would present, running `n=8` would not produce a different or additional reportable outcome, so it was not attempted -- consistent with D-04's framing of a timeout as the finding itself.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `Alloc.block: Pair -> one Int` field declaration does not parse**
- **Found during:** Task 1, first `racket forge/pooled_ancilla_allocation.frg` run
- **Issue:** Forge v5.2 rejected the field declaration `block: Pair -> one Int` with a parse error at the `Pair` token. The plan's own action text suggested this exact form (`one sig Alloc { block: Pair -> one Int }`), but it does not match Forge's actual sig-field-with-multiplicity grammar.
- **Fix:** Checked local installed Forge example files (`examples/basic/restricting_space.frg`'s `f: pfunc Int -> Int`, `examples/oopsla24/f2_ttt.frg`'s `board: pfunc Int -> Int -> Player`) and corrected to `block: func Pair -> Int` -- `func` is Forge's total-function relation multiplicity keyword, matching the "every pair has exactly one block" semantics `blocksInRange` already assumes.
- **Files modified:** `forge/pooled_ancilla_allocation.frg`
- **Verification:** `racket forge/pooled_ancilla_allocation.frg` subsequently parsed and all 12 test blocks passed.
- **Committed in:** `65b8f32`

---

**Total deviations:** 1 auto-fixed (blocking, syntax-only -- no scope or property change).

## Issues Encountered

- **Solve-time growth is steep, not gentle.** Per-block solving time roughly quadrupled from `n=4` (avg ~5.8s/block) to `n=5` (avg ~21.6s/block) to `n=6` (avg ~51.9s/block). Extrapolating this rate made `n=7` a plausible ceiling-hit candidate before it was even attempted, and the isolated 2-block probe confirmed it: exceeded 600s with zero blocks resolved (not even one `Transl (ms)`/`Solving (ms)` line printed before the process was killed at ~610s, memory footprint ~420MB and still climbing). This is reported in `results/phase22_forge_run_log.md`'s `## Bound outcome` as the finding itself, per D-04 -- not engineered around, not silently replaced by a smaller success.

## User Setup Required

None -- no external service configuration required. Racket/Forge toolchain was already confirmed working from Phase 16.

## Known Stubs

None. No hardcoded empty values or placeholder text introduced; the commented-out n=7/n=8 test blocks are not stubs in the sense the summary template flags them for -- they are the plan-mandated record of an attempted-and-ceiling-hit search, kept in the exact runnable shape they would need if the ceiling were ever lifted, with the measured cutoff documented per D-04's honest-verdict requirement rather than silently dropped.

## Next Phase Readiness

**Ready for Plan 22-05 (baseline comparison / write-up):**
- Minimum `K` per converged `n` (4, 5, 6) is established and matches the round-robin formula exactly, giving Plan 22-05 the comparison-table numbers it needs against a hand-rolled search baseline.
- Total Forge wall time for the converged suite (~6m9s for n=4..6) plus the n=7 timeout data (~610s to hit the ceiling with zero blocks resolved) are both recorded in `results/phase22_forge_run_log.md` for Plan 22-05's own comparison table.
- The largest `n` reached is `6`, not the D-03 target of `8` -- Plan 22-05 should treat `n<=6` as the model's live/verified range and report the `n=7`/`n=8` non-convergence as part of the honest verdict, not as a gap to quietly omit.

---
*Phase: 22-multi-pair-ancilla-allocation-formal-verification*
*Completed: 2026-08-21*

## Self-Check: PASSED

- FOUND: forge/pooled_ancilla_allocation.frg
- FOUND: results/phase22_forge_run_log.md
- FOUND: commit 65b8f32
- FOUND: commit 8de060e
