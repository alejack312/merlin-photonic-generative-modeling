---
phase: 17-trainability-barren-plateau-study
plan: 01
subsystem: quantum-ml
tags: [parameter-shift, gradients, perceval, iqp, photonic, tdd]

# Dependency graph
requires:
  - phase: 09-encoding-design (v2.0)
    provides: photonic_iqp_distribution (weight-1 IQP-photonic circuit)
  - phase: 11-cz-insertion-weight2-composition (v2.1)
    provides: photonic_weight2_iqp_distribution (weight-2 IQP-photonic circuit)
provides:
  - "weight1_param_shift_delta(n, thetas, k) -- exact per-bitstring parameter-shift gradient delta for the weight-1 circuit"
  - "weight2_param_shift_delta(n, i, j, thetas, k) -- exact per-bitstring parameter-shift gradient delta for the weight-2 circuit"
  - "trainability/ package scaffold (importable, minimal __init__.py)"
affects: [17-02-mmd-gradient, 17-05-gradient-variance-sweep, 17-06-run-sweep, 17-07-curve-fit-writeup]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Parameter-shift with shift=pi/4 (no division) for any WP(theta,0)=exp(i*theta*Z)-generated gate in this repo, hardcoded so callers cannot supply the wrong (pi/2) shift value"

key-files:
  created:
    - trainability/param_shift.py
    - tests/test_param_shift.py
  modified:
    - trainability/__init__.py

key-decisions:
  - "SHIFT=pi/4 is a module constant, not a function parameter -- makes the pi/2-shift footgun structurally impossible via this module's public API (the pitfall-regression test bypasses the module entirely to demonstrate what would go wrong)."
  - "trainability/__init__.py already existed (empty, committed by a concurrent wave-1 plan) -- filled in with the one-line docstring this plan's spec calls for rather than leaving it empty, since content and concurrent commit don't conflict."

patterns-established:
  - "Both param-shift functions return a diagnostic tuple (delta dict, residual[, herald_failure_prob]) rather than asserting internally -- callers decide what residual/herald-failure levels are acceptable, matching iqp_photonic_encoding.py's own reporting convention (residual/herald_failure_prob surfaced, never silently folded away)."

# Metrics
duration: ~10min
completed: 2026-08-10
---

# Phase 17 Plan 01: Exact Parameter-Shift Gradient Summary

**Exact, undivided pi/4 parameter-shift gradient (`trainability/param_shift.py`) for both weight-1 and weight-2 IQP-photonic circuits, replacing the textbook pi/2-shift rule that silently zeroes out for this repo's exp(i*theta*Z) gate convention.**

## Performance

- **Duration:** ~10 min
- **Started:** ~2026-08-10T01:20:00+02:00
- **Completed:** 2026-08-10T01:27:37+02:00
- **Tasks:** 1 (TDD: RED -> GREEN, no refactor needed)
- **Files modified:** 3 (2 created, 1 modified)

## Accomplishments
- `weight1_param_shift_delta(n, thetas, k)` proven exact against the closed-form analytic derivative of `expected_joint_distribution` (translated into `photonic_iqp_distribution`'s own '0'/'1' alphabet), to `atol=1e-9`, across n in {1,2,3} and 5 seeded random theta draws each, for every tracked k and every bitstring.
- `weight2_param_shift_delta(n, i, j, thetas, k)` cross-validated against an independent central finite-difference of `photonic_weight2_iqp_distribution` (eps=1e-4), to `atol=1e-4`, across n in {2,3}, (i,j)=(0,1), 3 seeded draws, every k.
- The textbook pi/2-shift pitfall demonstrated live (not just asserted in a docstring): `photonic_iqp_distribution(n,[theta+pi/2]) - photonic_iqp_distribution(n,[theta-pi/2])` is exactly 0.0 for every tested theta, confirming the failure mode this module's hardcoded `SHIFT=pi/4` closes off.
- Full repo test suite (184 tests) passes with zero regressions.

## Task Commits

TDD task, following RED -> GREEN (no refactor needed -- no duplication worth extracting between the three test cases):

1. **Task 1 RED: add failing tests for exact parameter-shift gradient** - `40452e0` (test)
2. **Task 1 GREEN: implement exact parameter-shift gradient of WP(theta,0)** - `82e0ee3` (feat)

**Plan metadata:** (this commit, following SUMMARY/STATE update)

## Files Created/Modified
- `trainability/param_shift.py` - `weight1_param_shift_delta`/`weight2_param_shift_delta`, `SHIFT = pi/4` module constant, no caller-supplied shift parameter
- `tests/test_param_shift.py` - 8 tests: weight-1 closed-form exactness (3 n-values x 5 draws x k), weight-2 finite-difference cross-check (2 n-values x 3 draws x k), pi/2-shift pitfall regression (3 theta values)
- `trainability/__init__.py` - filled in module docstring (file already existed empty, from a concurrent wave-1 plan)

## Decisions Made
- `SHIFT` hardcoded as a module constant rather than accepted as a parameter, per the plan's explicit requirement -- this is the single design choice that makes the wrong-shift bug this plan exists to prevent structurally unreachable through this module's API.
- Analytic reference for the weight-1 test built directly in `photonic_iqp_distribution`'s own '0'/'1' bitstring alphabet (0='H', 1='V'), rather than round-tripping through `expected_joint_distribution`'s 'H'/'V' alphabet, per the plan's explicit warning about this exact translation pitfall.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

**Concurrent wave-1 execution:** Plans 17-02 (`trainability/mmd_exact.py`), 17-03 (`trainability/target_grid.py`), and 17-04 (`trainability/curve_fit.py`) were being executed by sibling agents in parallel with this plan (all four are `wave: 1`, `depends_on: []`), committing to the same repo concurrently. `trainability/__init__.py` was found already created (empty) and committed by one of them before this plan's own commit. Handled by: (1) unstaging a sibling plan's in-flight staged file (`trainability/target_grid.py`) before committing, to avoid this plan's commit accidentally sweeping in unrelated uncommitted work from another agent's git index state; (2) filling in `__init__.py`'s docstring content on top of the already-committed empty file rather than treating it as a conflict. No functional conflicts -- each plan's files are disjoint (`param_shift.py` vs `mmd_exact.py`/`target_grid.py`/`curve_fit.py`), and the full 184-test suite passes cleanly after this plan's commits.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- `trainability/param_shift.py` is ready for Plan 17-02 (MMD² gradient) to compose with: `weight1_param_shift_delta`/`weight2_param_shift_delta`'s delta dicts are exactly the `dq_dtheta_k` input `trainability/mmd_exact.py`'s `mmd2_grad` (already implemented by the concurrent 17-02 plan) expects, once converted to a vector via a bin-index mapping (17-03's `trainability/target_grid.py::bitstring_dict_to_vector`).
- No blockers. Confirmed live (not just asserted) that this repo's parameter-shift math is exact for weight-1 and correct-to-finite-difference-precision for weight-2, closing out TRAIN-01's foundational requirement.

---
*Phase: 17-trainability-barren-plateau-study*
*Completed: 2026-08-10*
