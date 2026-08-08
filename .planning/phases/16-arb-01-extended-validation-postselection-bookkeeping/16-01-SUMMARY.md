---
phase: 16-arb-01-extended-validation-postselection-bookkeeping
plan: 01
subsystem: testing
tags: [perceval, photonic-circuits, iqp, pytest, tvd-validation]

# Dependency graph
requires:
  - phase: 15-arb-01-core-gate-de-risking-validation
    provides: "photonic_cp_iqp_distribution(n, i, j, thetas, alpha) -- validated full-pipeline arbitrary-theta weight-2 CP(alpha) gate"
provides:
  - "test_cp_composability_mixed_generators_n3 -- ARB-07's n=3 mixed weight-1 + arbitrary-theta weight-2 composability test, confirming photonic_cp_iqp_distribution composes correctly with weight-1 terms in a shared circuit"
affects: [16-02, 16-03, 20-technical-write-up]

# Tech tracking
tech-stack:
  added: []
  patterns: ["parametrized pytest test mirroring an existing test's structure but swapping the gate mechanism under test (photonic_weight2_iqp_distribution -> photonic_cp_iqp_distribution) and the fixed angle for per-config values from a locked NON_TRIVIAL_ALPHAS set"]

key-files:
  created: []
  modified: ["tests/test_iqp_photonic_encoding.py"]

key-decisions:
  - "Sanity-check TVD threshold set to 0.005 (not Phase 13's 0.1) after measuring the actual non-vacuity TVD range (0.017-0.088) at these alpha values -- alpha/4 folds in a smaller effective rotation than Phase 13's fixed pi/4, so reusing 0.1 literally would have been wrong, not just conservative."
  - "Alpha values spread across NON_TRIVIAL_ALPHAS (pi/6, pi/3, 2*pi/5) rather than repeating one, per CONTEXT.md's stated preference for touching more of the validated range."

patterns-established: []

# Metrics
duration: 5min
completed: 2026-08-08
---

# Phase 16 Plan 01: ARB-07 Mixed-Generator Composability Test Summary

**Added a parametrized pytest test confirming CP(alpha)'s arbitrary-theta weight-2 gate composes correctly with weight-1 terms at n=3, across 3 distinct non-trivial alpha values, closing ARB-07.**

## Performance

- **Duration:** 5 min
- **Started:** 2026-08-08T21:51:00Z
- **Completed:** 2026-08-08T21:56:03Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments
- `test_cp_composability_mixed_generators_n3` added: n=3, 2 weight-1 terms plus 1 arbitrary-alpha weight-2 (CP) term in the same circuit, direct CP(alpha) analogue of Phase 13's `test_wt2_composability_mixed_generators_n3`.
- Confirms the arbitrary-theta weight-2 gate validated standalone in Phase 15 also composes correctly with weight-1 terms in a shared circuit, not just in isolation.
- Full repo suite verified green at 145/145 (142 baseline + 3 new parametrized cases), zero regressions.

## Task Commits

Each task was committed atomically:

1. **Task 1: Write and tune the ARB-07 composability test** - `3629b8d` (test)
2. **Task 2: Full-suite regression check** - no commit (verification-only, no file changes)

**Plan metadata:** (this commit, made after this summary)

## Files Created/Modified
- `tests/test_iqp_photonic_encoding.py` - Added `test_cp_composability_mixed_generators_n3`, a parametrized test over 3 n=3 configs, each with a distinct alpha from `NON_TRIVIAL_ALPHAS`.

## Decisions Made
- **Non-vacuity threshold recalculated, not reused**: Phase 13's `0.1` sanity-check threshold was measured at the fixed pi/4 angle. Here, `theta = alpha/4` produces effective rotations of ~0.13-0.31 rad (vs pi/4's ~0.785 rad), so the actual non-vacuity TVD is genuinely smaller (0.017-0.088 measured). Set the threshold to `0.005` — over 3x headroom below the smallest observed value — rather than either reusing `0.1` (would have failed) or guessing.
- **Alpha assignment**: each of the 3 `(i,j,thetas)` configs from Phase 13 paired with a different value from `NON_TRIVIAL_ALPHAS` (pi/6, pi/3, 2*pi/5) to spread coverage, per Claude's discretion as scoped in `16-CONTEXT.md`.

## Deviations from Plan

None - plan executed exactly as written. All measured values (TVD, sanity TVD range) matched the plan's stated expectations exactly.

## Issues Encountered
None. The repo's `venv/` virtual environment (not system Python) was required to run the test suite (`perceval`/`merlin` are only installed there) — noted for future execution sessions in this repo, not a plan deviation.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- ARB-07 fully satisfied; ready for Plan 02 (denser 16-point alpha sweep with closed-form validation and plot) and Plan 03 (Forge-based mode-mapping structural verification), both independent of this plan's changes.
- No blockers or concerns carried forward.

---
*Phase: 16-arb-01-extended-validation-postselection-bookkeeping*
*Completed: 2026-08-08*
