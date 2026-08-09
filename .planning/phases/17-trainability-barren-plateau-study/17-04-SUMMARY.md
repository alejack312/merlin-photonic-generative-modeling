---
phase: 17-trainability-barren-plateau-study
plan: 04
subsystem: analysis
tags: [scipy, curve-fit, aic, r-squared, model-comparison, barren-plateau, tdd]

# Dependency graph
requires: []
provides:
  - "trainability/curve_fit.py: exp_model, poly_model, aic, fit_and_compare -- poly-vs-exponential model comparison with R^2 and AIC, proven correct against synthetic ground-truth data"
affects: [17-07 (real gradient-variance-vs-n sweep analysis will call fit_and_compare directly)]

# Tech tracking
tech-stack:
  added: []
  patterns: ["delta-AIC > 2 as the 'meaningfully better' model-selection threshold, explicit inconclusive verdict below that bar", "curve_fit convergence failures caught explicitly and surfaced as converged=False + NaN metrics, never silently swallowed"]

key-files:
  created: [trainability/curve_fit.py, tests/test_curve_fit.py]
  modified: []

key-decisions:
  - "Widened synthetic test ns grid from the plan's suggested [2..6] (5 points) to [2..8] (7 points): with only 5 points and 3 free params per model, exp_model and poly_model fit the same synthetic curve near-identically well over this project's small-n range (delta-AIC < 2 for both ground-truth cases at seed 1710), correctly returning 'inconclusive' per the routine's own honesty bar -- not a routine bug, just insufficient distinguishing power at 5 points. 7 points cleanly separates both cases across multiple tested seeds."
  - "AIC model-selection threshold set to delta > 2.0 (Burnham & Anderson convention), stated explicitly in the module docstring per the plan's requirement."
  - "Broadened _fit_one's caught exceptions to (RuntimeError, ValueError, TypeError) -- TypeError arises when curve_fit is given fewer data points than free parameters (degenerate input), which the plan's own convergence-failure requirement implies should be surfaced, not crash the whole analysis."

# Metrics
duration: 20min
completed: 2026-08-09
---

# Phase 17 Plan 04: Poly-vs-Exponential Curve Fit Summary

**`trainability/curve_fit.py` implements `scipy.optimize.curve_fit`-based exp-vs-poly model comparison with R^2 and AIC, TDD-proven to recover the correct verdict on synthetic ground-truth data before ever touching real sweep data.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-08-09 (session start)
- **Completed:** 2026-08-09T23:26Z
- **Tasks:** 1 TDD feature (RED -> GREEN, no REFACTOR needed)
- **Files modified:** 2 (1 created source, 1 created test)

## Accomplishments
- `trainability/curve_fit.py`: `exp_model`, `poly_model`, `aic`, and `fit_and_compare` — fits both barren-plateau (exponential) and non-barren-plateau (polynomial/power-law) candidate models via `scipy.optimize.curve_fit`, computes R² and AIC for both on every call, and returns an explicit verdict (`"exp"` / `"poly"` / `"inconclusive"`) using a delta-AIC > 2 threshold stated in the docstring.
- TDD test suite (`tests/test_curve_fit.py`, 7 tests) proves the routine recovers the correct verdict on synthetic data with a KNOWN ground-truth model — both for exponential and polynomial decay — with recovered parameters close to the true values, and that R²/AIC are always present and finite for both models, not just the winner.
- Convergence failures are caught explicitly and surfaced as `converged: False` with NaN metrics rather than crashing — proven by a dedicated degenerate-input test (fewer data points than free params).

## Task Commits

TDD cycle (RED -> GREEN, no REFACTOR):

1. **Test: failing tests for poly-vs-exp curve-fit comparison** - `5a60d15` (test)
2. **Feat: implement poly-vs-exp curve-fit model comparison** - `88870fe` (feat)

**Plan metadata:** (this commit, docs: complete plan)

## Files Created/Modified
- `trainability/curve_fit.py` - `exp_model`, `poly_model`, `aic`, `fit_and_compare`; delta-AIC > 2 verdict threshold; explicit convergence-failure surfacing
- `tests/test_curve_fit.py` - 7 TDD tests: exp/poly ground-truth verdict recovery, both-models-report-both-metrics, AIC formula correctness, verdict-key validity, convergence-failure surfacing

## Decisions Made
- Widened the synthetic test's `ns` grid from 5 to 7 points (`[2..8]`) after discovering the plan's suggested 5-point grid gives both candidate models near-identical fit quality on this project's small-n range (delta-AIC ~0.3, correctly "inconclusive"). This is expected behavior of the routine, not a bug — flagged and fixed by widening the grid rather than loosening the AIC threshold, which would have masked genuinely ambiguous cases in real data too.
- AIC delta-threshold of 2.0, explicit convergence-failure exception set (`RuntimeError`, `ValueError`, `TypeError`) — both documented inline for Plan 17-07's consumption.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Test synthetic data grid too small to distinguish models**
- **Found during:** GREEN phase, first test run
- **Issue:** The plan's suggested 5-point `ns = [2,3,4,5,6]` grid produced near-identical AIC for both exp_model and poly_model on the exponential-ground-truth case (both R²≈0.999, delta-AIC≈0.3 < the 2.0 threshold), causing `test_exponential_ground_truth_recovers_exp_verdict` to correctly report `"inconclusive"` per the routine's own logic — but the plan's test spec required a definitive `"exp"` verdict.
- **Fix:** Widened `NS` to 7 points (`[2,3,4,5,6,7,8]`), which cleanly separates both ground-truth cases (delta-AIC > 6 in both directions) across multiple manually-checked seeds, while keeping the fixed seed (1710) the tests actually run with.
- **Files modified:** `tests/test_curve_fit.py`
- **Verification:** All 7 tests pass with seed 1710; spot-checked seeds 42 and 7 also produce correct verdicts at the 7-point grid, confirming this isn't a seed-cherry-picking artifact.
- **Committed in:** `88870fe` (GREEN commit)

**2. [Rule 3 - Blocking] `_fit_one` needed to also catch `TypeError`**
- **Found during:** GREEN phase, ad hoc convergence-failure exploration
- **Issue:** `scipy.optimize.curve_fit` raises `TypeError` (not `RuntimeError`/`ValueError`) when given fewer data points than free parameters — an uncaught crash that violated the plan's "handle convergence failures gracefully, never crash" requirement.
- **Fix:** Added `TypeError` to `_fit_one`'s caught exception tuple, with an inline comment explaining the case.
- **Files modified:** `trainability/curve_fit.py`
- **Verification:** New `test_convergence_failure_is_surfaced_not_swallowed` test (2-point degenerate input) passes, confirming `converged: False` + NaN metrics rather than an exception propagating.
- **Committed in:** `88870fe` (GREEN commit)

---

**Total deviations:** 2 auto-fixed (1 bug in test data sizing, 1 blocking exception-handling gap)
**Impact on plan:** Both fixes strengthen the routine's correctness guarantees for Plan 17-07's real-data use; no scope creep — both stay within this plan's own stated behavior spec (verdict correctness, convergence-failure surfacing).

## Issues Encountered

A concurrent session was executing a sibling Phase 17 plan (17-02/17-03, `trainability/mmd_exact.py` and `trainability/target_grid.py`) in the same working tree while this plan ran — its commits (`f52f969`, `67f2c27`, `fbd148f`) are interleaved with this plan's own commits in `git log`, and its `tests/test_target_grid.py` is present but uncommitted with one failing test (`test_cross_validation_against_compute_p_real`, unrelated to `curve_fit.py` — a torch/numpy `float32`/`float64` precision mismatch in a different module). This is out of scope for 17-04 (no shared code, no shared files) and was left untouched — it belongs to that plan's own executor to resolve. `tests/test_curve_fit.py` and the full suite excluding that one file pass cleanly (175/176 total, the 1 failure being the unrelated concurrent-session file).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

`fit_and_compare(ns, variances)` is ready for Plan 17-07 to call directly against real gradient-variance-vs-n sweep data (from Plan 17-06). Its returned dict shape (`{"exp": {...}, "poly": {...}, "verdict": ...}`) is documented in the module docstring. No blockers for downstream plans. The one open item flagged above (concurrent session's `test_target_grid.py` failure) is unrelated to this plan's deliverable and does not block it.

---
*Phase: 17-trainability-barren-plateau-study*
*Completed: 2026-08-09*
