---
phase: 13-weight-1-weight-2-composability-validation
plan: 01
subsystem: testing
tags: [pytest, perceval, tvd, iqp, photonic-encoding, weight-2]

# Dependency graph
requires:
  - phase: 12-exact-reference-extension-tvd-validation
    provides: "exact_qubit_iqp_distribution(pair_thetas=...) and photonic_weight2_iqp_distribution(n, i, j, thetas), both TVD-validated to ~1e-15 at the locked n=2 gate"
provides:
  - "test_wt2_composability_mixed_generators_n3: parametrized (3 configs) proof that weight-1 (single-qubit Z) and weight-2 (ZZ pair) generator layers compose correctly in the same n=3 circuit, including a weight-1 theta stacked directly on a weight-2 pair member"
  - "WT2-07 satisfied -- closes out the v2.1 Weight-2 Implementation milestone's 8/8 requirements"
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns: []

key-files:
  created: []
  modified:
    - tests/test_iqp_photonic_encoding.py

key-decisions:
  - "Stacked the weight-1 theta directly on a weight-2 pair member (i or j) rather than using fully disjoint qubits, per CONTEXT.md's stronger-test requirement -- proves per-qubit Z and pairwise ZZ terms compose correctly on the same qubit, not just across disjoint qubits"
  - "Companion sanity-check threshold set to TVD > 0.1 against the weight-1-only reference (research measured 0.46-0.50 for these configs) -- large headroom against flakiness while still ruling out an accidentally-inert weight-2 term"

patterns-established: []

# Metrics
duration: 10min
completed: 2026-08-06
---

# Phase 13 Plan 01: Weight-1 + Weight-2 Composability Validation Summary

**Added a 3-config parametrized pytest proving weight-1 (Z) and weight-2 (ZZ) generator layers compose correctly in the same n=3 circuit, including on a shared qubit -- closing WT2-07 and all 8/8 v2.1 requirements.**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-08-06T19:05:00Z (approx)
- **Completed:** 2026-08-06T19:17:00Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments
- New `test_wt2_composability_mixed_generators_n3`, parametrized over 3 verified n=3 configs, each with a nonzero, non-degenerate weight-1 theta on a weight-2 pair member plus one on the bystander qubit
- Primary TVD assertion (< 1e-6) against the extended exact reference (`pair_thetas` set) confirms exact correctness; companion sanity assertion (TVD > 0.1 against the weight-1-only reference) confirms the ZZ term is doing real, non-vacuous work rather than being silently inert
- No changes to `iqp_photonic_encoding.py` -- both `exact_qubit_iqp_distribution` and `photonic_weight2_iqp_distribution` already fully supported this scenario from Phase 12
- Full test suite grew from 115 to 118 passing tests (+3, exactly as predicted), zero regressions

## Task Commits

Each task was committed atomically:

1. **Task 1: Add n=3 mixed weight-1 + weight-2 composability test (WT2-07)** - `b5cb28a` (test)

_No TDD flag on this task; a single test-addition commit is correct per the plan._

## Files Created/Modified
- `tests/test_iqp_photonic_encoding.py` - Added `test_wt2_composability_mixed_generators_n3`, a 3-config parametrized test covering weight-1/weight-2 composability at n=3, appended after `test_wt2_tvd_gate_n3_bystander_qubit`

## Decisions Made
- Kept the plan's exact three (n, i, j, thetas) configs and 0.1 sanity threshold as specified -- no changes needed, both were independently pre-verified in 13-RESEARCH.md before this plan was locked

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None. The plan's given test code ran and passed on the first attempt; `venv/Scripts/python.exe` required forward slashes in this bash environment (backslash path failed to resolve), a shell-syntax quirk with no code impact.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

This was the final requirement (WT2-07) of the v2.1 Weight-2 Implementation milestone -- all 8/8 v1 requirements (WT2-01 through WT2-08) now have passing test evidence. No blockers. Remaining milestone-closing steps (marking WT2-07 Complete in `REQUIREMENTS.md`, phase verification, milestone completion) are the orchestrator's/verifier's responsibility, not this plan's.

---
*Phase: 13-weight-1-weight-2-composability-validation*
*Completed: 2026-08-06*
