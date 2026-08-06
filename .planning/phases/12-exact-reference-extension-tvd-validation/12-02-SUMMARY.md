---
phase: 12-exact-reference-extension-tvd-validation
plan: 02
subsystem: docs
tags: [perceval, tvd, iqp, photonic, bug-report]

# Dependency graph
requires:
  - phase: 12-01
    provides: photonic_weight2_iqp_distribution and exact_qubit_iqp_distribution(pair_thetas=...) with measured TVD, herald-success/failure, and residual numbers
provides:
  - "results/phase12_weight2_tvd_validation_summary.md -- written, numbers-only record of the WT2-05 TVD gate result"
  - "Upstream Perceval bug report (Quandela/Perceval#783) documenting the add_herald + PBS crash"
affects: [phase-13-composability-validation, future-vincent-espitalier-conversation]

# Tech tracking
tech-stack:
  added: []
  patterns: []

key-files:
  created:
    - results/phase12_weight2_tvd_validation_summary.md
  modified: []

key-decisions:
  - "Filed the upstream Perceval bug live via `gh issue create` (Quandela/Perceval#783) rather than drafting to disk -- gh was already authenticated with repo scope, and the target repo slug (Quandela/Perceval) resolved on the first check"
  - "Committed the summary write-up (Task 1) and the bug-report URL pointer (Task 2) as two separate atomic commits touching the same file, matching the plan's two-task structure rather than merging into one commit"

patterns-established: []

# Metrics
duration: 12min
completed: 2026-08-06
---

# Phase 12 Plan 02: Weight-2 TVD Validation Write-up & Upstream Bug Report Summary

**`results/phase12_weight2_tvd_validation_summary.md` records the re-measured WT2-05 TVD gate (TVD=2.58e-15 at n=2, pair (0,1), theta=pi/4) plus an n=3 supplementary check, and Quandela/Perceval#783 files the `add_herald`+`PBS` crash upstream.**

## Performance

- **Duration:** 12 min
- **Started:** 2026-08-06T00:00:00Z (approx)
- **Completed:** 2026-08-06T00:12:00Z (approx)
- **Tasks:** 2
- **Files modified:** 1 (results/phase12_weight2_tvd_validation_summary.md)

## Accomplishments
- Re-ran Plan 12-01's locked TVD gate live against the committed `iqp_photonic_encoding.py` (not transcribed from 12-RESEARCH.md's earlier scratch runs) and wrote up the real numbers in `results/phase12_weight2_tvd_validation_summary.md`, matching `results/phase7_neighbor_locality_summary.md`'s structure.
- Included the n=3 opportunistic bystander-qubit check (from `tests/test_iqp_photonic_encoding.py::test_wt2_tvd_gate_n3_bystander_qubit`) as a separately-labeled supplementary result.
- Filed the confirmed `Processor.add_herald()` + `PBS`-containing circuit crash as an upstream GitHub issue against Quandela/Perceval: https://github.com/Quandela/Perceval/issues/783.

## Task Commits

Each task was committed atomically:

1. **Task 1: Write results/phase12_weight2_tvd_validation_summary.md** - `e5f1dfc` (docs)
2. **Task 2: File the upstream Perceval/Quandela bug report** - `a8c86ca` (docs)

_No separate plan-metadata commit yet -- STATE.md update follows this SUMMARY._

## Files Created/Modified
- `results/phase12_weight2_tvd_validation_summary.md` - Written record of Phase 12's measured TVD/herald/residual numbers (primary + supplementary), with the upstream issue URL noted in the Method section and an unwritten `## Interpretation` placeholder.

## Decisions Made
- Filed the bug report live rather than drafting to disk, since `gh auth status` showed an already-authenticated account with `repo` scope and `Quandela/Perceval` resolved correctly on the first `gh repo view` check -- no blocker encountered, so the plan's fallback draft-to-disk path was not needed.
- Split the single modified file's two tasks into two separate commits (write-up, then bug-report pointer) to preserve per-task atomic commit granularity even though both tasks touch the same file.

## Deviations from Plan

None - plan executed exactly as written. The plan's fallback path (draft-to-disk if filing is blocked) was not triggered since `gh issue create` succeeded on the first attempt.

## Issues Encountered
None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Phase 12 is now fully complete: both plans (12-01 implementation, 12-02 write-up + upstream bug report) executed and committed.
- Upstream Perceval bug report is live at https://github.com/Quandela/Perceval/issues/783 -- no manual follow-up needed unless Quandela maintainers respond and ask for a minimal repro script.
- Ready to close out Phase 12 in STATE.md/REQUIREMENTS.md and move to Phase 13 (Weight-1 + Weight-2 Composability Validation).

---
*Phase: 12-exact-reference-extension-tvd-validation*
*Completed: 2026-08-06*
