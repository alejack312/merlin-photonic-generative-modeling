---
phase: 17-trainability-barren-plateau-study
plan: 02
subsystem: testing
tags: [numpy, mmd, gradient, tdd, quantum-ml, trainability]

# Dependency graph
requires: []
provides:
  - "trainability/mmd_exact.py: gaussian_kernel_matrix_np, mmd2_np, mmd2_grad -- pure-numpy MMD^2 loss and exact chain-rule gradient, torch-parity verified against generator/mmd.py"
affects: [17-05 sweep, 17-06/17-07 gradient-variance measurement and write-up]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Torch-free numpy port of an existing torch loss, cross-validated against the torch original only inside the test file (never imported by production code) -- keeps the exact parameter-shift pipeline (Phase 17) free of any autograd dependency"

key-files:
  created:
    - trainability/mmd_exact.py
    - tests/test_mmd_exact.py
  modified: []

key-decisions:
  - "Gradient exactness proven two ways: finite-difference cross-check (atol=1e-4, sanity only) AND an algebraically-expanded closed-form derivative of the known synthetic quadratic (atol=1e-9, the real proof) -- per plan spec, not settling for finite-difference alone."
  - "Deliberately did not implement a Monte-Carlo MMD^2 estimator or exact/MC crossover switch, per 17-RESEARCH.md Pitfall 4 -- this project's kernel matrix stays at K<=2^8, so the sibling project's K~2^16-2^20 MC fallback need never triggers here. Documented as a scope decision in the module docstring."

patterns-established:
  - "Numpy ports of existing torch losses live in trainability/, cross-validated against the torch original in tests/ only -- torch import stays confined to test files and never leaks into trainability/*.py production modules."

# Metrics
duration: ~12min
completed: 2026-08-09
---

# Phase 17 Plan 02: Exact Numpy MMD^2 Loss and Gradient Summary

**Pure-numpy port of `generator/mmd.py`'s Gaussian-kernel MMD^2 quadratic form plus a new exact chain-rule gradient (`mmd2_grad`), torch-parity verified to 1e-6 and gradient-exactness verified to 1e-9 against an algebraically-known synthetic quadratic.**

## Performance

- **Duration:** ~12 min (RED at 01:21:54, GREEN at 01:23:23, per commit timestamps)
- **Started:** 2026-08-09T23:21Z (approx, first commit)
- **Completed:** 2026-08-09T23:23Z
- **Tasks:** 1 TDD feature (RED -> GREEN, no REFACTOR needed)
- **Files modified:** 2 created

## Accomplishments
- `trainability/mmd_exact.py` ships `gaussian_kernel_matrix_np`, `mmd2_np`, `mmd2_grad` -- a torch-free numpy MMD^2 primitive usable directly on parameter-shift outputs (Plan 17-01), with zero torch/autograd dependency anywhere in the module.
- Kernel matrix and MMD^2 value both verified numerically identical (atol=1e-6) to the existing torch implementation (`generator/mmd.py`) across all 5 `SIGMA_GRID` values, on 10-point random 2D centers.
- The MMD^2 gradient chain rule (`d(MMD^2)/d(theta) = 2*(q-p)@K@dq_dtheta`) is proven exact -- not just plausible -- against a synthetic linear model `q(theta) = q0 + theta*dq` whose true derivative was expanded algebraically by hand in the test docstring and matched to atol=1e-9.

## Task Commits

TDD RED -> GREEN cycle (no REFACTOR commit -- implementation had no obvious duplication to clean up):

1. **RED: failing tests for exact numpy MMD^2 primitives** - `f52f969` (test)
2. **GREEN: implement exact numpy MMD^2 loss and gradient** - `67f2c27` (feat)

## Files Created/Modified
- `trainability/mmd_exact.py` - `gaussian_kernel_matrix_np(centers, sigma)`, `mmd2_np(p, q, kernel_matrix)`, `mmd2_grad(q, p, kernel_matrix, dq_dtheta)` -- pure numpy, no torch import.
- `tests/test_mmd_exact.py` - 14 tests: torch-parity on kernel matrix (5x, one per SIGMA_GRID value) and MMD^2 value (5x), self-comparison-is-zero, finiteness/nonnegativity, finite-difference gradient sanity check, and the algebraic-exactness gradient proof.

## Decisions Made
- Proved gradient exactness via an algebraically-expanded closed-form derivative (atol=1e-9), not just a finite-difference check (atol=1e-4) -- the plan explicitly required the stronger proof, since finite-difference alone only demonstrates plausibility, not exactness.
- Followed the plan's explicit scope boundary: no Monte-Carlo MMD^2 estimator, no exact/MC crossover switch. This project's kernel matrix (K<=2^8 bins) never approaches the sibling project's K~2^16-2^20 scale where an MC fallback would matter (17-RESEARCH.md Pitfall 4). Documented as a deliberate decision in the module docstring, not a silent omission.
- Kept `generator.mmd`/`generator.bin_centers` imports confined to the test file only, per the plan's explicit instruction -- `trainability/mmd_exact.py` has zero torch dependency, matching CONTEXT.md's locked "never autograd through a differentiable pipeline for this circuit" rule.

## Deviations from Plan

None - plan executed exactly as written. TDD RED -> GREEN completed on the first implementation attempt; no bugs found, no missing critical functionality, no blockers, no architectural questions.

## Issues Encountered

None specific to this plan. Note: `pytest` (full suite) surfaced one pre-existing failure, `tests/test_target_grid.py::test_cross_validation_against_compute_p_real`, unrelated to this plan's changes -- it belongs to Plan 17-03 (`trainability/target_grid.py`), which was executing concurrently in a parallel agent session at the same time as this plan (confirmed via `git log`: interleaved 17-02/17-03/17-04 commits). `tests/test_mmd_exact.py` itself is 14/14 green, and this plan touched no files that failure depends on. Not fixed here -- out of scope for this plan and would step on the concurrent 17-03 agent's own in-progress work.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- `trainability/mmd_exact.py` is ready for Plan 17-05 (sweep) to combine with Plan 17-01's parameter-shift derivatives, giving the full exact-gradient pipeline TRAIN-01/TRAIN-02 need.
- Known open item (not mine to resolve): Plan 17-03's `test_target_grid.py` had one failing test as of this plan's full-suite run -- flagged here for whoever picks up or reviews Plan 17-03, not actioned in this plan.

---
*Phase: 17-trainability-barren-plateau-study*
*Completed: 2026-08-09*
