---
phase: 17-trainability-barren-plateau-study
plan: 03
subsystem: testing
tags: [numpy, mmd, target-distribution, barren-plateau, iqp-photonic]

# Dependency graph
requires:
  - phase: 09-encoding-design (v2.0)
    provides: generator/data.py::compute_p_real, generator/natural_grid.py::make_natural_bin_centers (v1.0/v2.0 grid machinery this generalizes)
provides:
  - "trainability/target_grid.py::make_target_grid(n, lo, hi) -> (centers, p_real, bin_index_fn) for any n, K=2**n"
  - "trainability/target_grid.py::bitstring_dict_to_vector(d, n, bin_index_fn) -> np.ndarray, for both probability distributions and signed parameter-shift deltas"
affects: [17-05, 17-06 (Trainability/Barren-Plateau Study sweep plans needing a per-n MMD target distribution)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "numpy-only production path (no torch) for Phase 17's trainability subsystem, consistent with Plans 17-01/17-02"
    - "squared-expansion distance formula (||a||^2 - 2a.b + ||b||^2) to bit-faithfully match torch.cdist's internal rounding at genuine floating-point ties, rather than a direct elementwise-difference formula"

key-files:
  created: [trainability/target_grid.py, tests/test_target_grid.py]
  modified: []

key-decisions:
  - "bin_index_fn(bitstring) = int(bitstring, 2) chosen as the bitstring<->grid-index convention -- deliberately arbitrary and stated as such, since gradient-variance magnitude (this phase's actual measurement) is not expected to be sensitive to this choice per 17-RESEARCH.md Open Question 1"
  - "make_target_grid defaults to float64 precision (not float32) for the production per-n grid, since Phase 17 measures small gradient-variance magnitudes where precision matters; the v1.0 cross-validation test explicitly downcasts to float32 to match compute_p_real's actual default precision for an honest apples-to-apples comparison"

patterns-established:
  - "Any future numpy port of an existing torch distance/argmin computation in this repo should match torch.cdist's squared-expansion formula, not just be mathematically equivalent -- direct elementwise-difference formulas round differently at genuine ties and will silently diverge from the torch original on real (not synthetic) data"

# Metrics
duration: 9min
completed: 2026-08-10
---

# Phase 17 Plan 03: Per-n Target Grid Summary

**Numpy `make_target_grid(n)` generalizes v1.0's fixed K=462 MMD target grid to any K=2^n, cross-validated bit-faithfully against the existing `compute_p_real` by matching torch.cdist's internal distance formula, not just its output.**

## Performance

- **Duration:** 9 min
- **Started:** 2026-08-10T01:22:38+02:00
- **Completed:** 2026-08-10T01:31:31+02:00
- **Tasks:** 2 completed
- **Files modified:** 2 (both new)

## Accomplishments
- `trainability/target_grid.py::make_target_grid(n, lo=-0.1, hi=1.1)` builds a valid `K=2**n` grid + target distribution `p_real` for any n, with `rows*cols == 2**n` exactly (no rounding) at every n
- `bitstring_dict_to_vector` generically converts `{bitstring: value}` dicts to length-`2**n` numpy arrays, correctly handling both non-negative probability distributions and signed (possibly negative) parameter-shift deltas without normalizing
- Cross-validated the numpy nearest-bin-assignment port against the existing, already-tested `generator/data.py::compute_p_real` at v1.0's exact 21x22=462 grid shape, and in the process found and fixed a genuine floating-point tie-break discrepancy between numpy and torch (documented below)

## Task Commits

Each task was committed atomically:

1. **Task 1: Build the per-n target grid and bin-index mapping** - `fbd148f` (feat)
2. **Task 2: Cross-validate the numpy port and add test coverage** - `9ac06d5` (test, includes the Rule 1 bug fix discovered during cross-validation)

## Files Created/Modified
- `trainability/target_grid.py` - `make_target_grid(n, lo, hi)` and `bitstring_dict_to_vector(d, n, bin_index_fn)`, plus the private `_nearest_bin_p_real` helper
- `tests/test_target_grid.py` - bin-index bijection (n=1..5), p_real validity (n=2,4,6), cross-validation against `compute_p_real` at the 21x22 shape, `bitstring_dict_to_vector` round-trip including a negative-value case

## Decisions Made
- `bin_index_fn = int(bitstring, 2)`: chosen and documented as a deliberate, low-risk-to-leave-arbitrary convention (per 17-RESEARCH.md Open Question 1 and 17-CONTEXT.md) -- gradient-variance magnitude, not spatial layout, is what this phase measures.
- Production `make_target_grid` stays at numpy's natural (float64) precision rather than forcing float32 to match torch's default -- deliberately kept more precise than v1.0's original torch path, since Phase 17's actual purpose (measuring tiny gradient-variance magnitudes for barren-plateau scaling) benefits from the extra precision. The v1.0 cross-validation test casts inputs to float32 specifically to compare like-with-like against `compute_p_real`'s real default behavior, without weakening production precision.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Distance-formula tie-break mismatch in the numpy port**
- **Found during:** Task 2 (writing/running the `compute_p_real` cross-validation test)
- **Issue:** The initial numpy port computed nearest-bin distances via direct elementwise-difference (`sqrt(sum((a-b)**2))`). At v1.0's real 21x22 grid and the real (seeded) circles dataset, one training point `(0.1, 0.5)` lands EXACTLY on the y-midpoint between two adjacent grid rows -- a genuine floating-point tie, not a bug in the assignment logic itself. `torch.cdist` internally uses a different but mathematically equivalent formula (`||a||^2 - 2*a.b + ||b||^2`), which rounds this specific tie in the opposite direction, causing exactly 1 of 320 points (and thus 2 of 462 bins, by 1/320 ≈ 0.003125 each) to disagree between the numpy port and the torch original -- large enough to fail `np.allclose(..., atol=1e-9)`.
- **Fix:** Rewrote `_nearest_bin_p_real` to use the same squared-expansion distance formula `torch.cdist` uses internally, without forcing any dtype (natural numpy type promotion applies, so production stays float64). Verified this reproduces `compute_p_real`'s bin assignment exactly, including at the tied point, when compared at matching (float32) precision.
- **Files modified:** `trainability/target_grid.py`, `tests/test_target_grid.py` (test explicitly casts both sides to float32 for an honest apples-to-apples comparison, documented inline)
- **Verification:** `./venv/Scripts/python.exe -m pytest tests/test_target_grid.py -v` -- all 10 tests pass, including `test_cross_validation_against_compute_p_real`; full 184-test repo suite passes with zero regressions
- **Committed in:** `9ac06d5` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** The fix strengthens the plan's own core requirement (a faithful, not just plausible-looking, numpy port) rather than deviating from it. No scope creep -- the fix stayed inside `_nearest_bin_p_real`, the exact function the plan asked to be cross-validated.

## Issues Encountered
None beyond the Rule 1 fix above.

Note: this plan's tasks executed while sibling Phase 17 plans (17-01, 17-02, 17-04) were running concurrently in parallel sessions against the same working tree, also writing into `trainability/` (`param_shift.py`, `curve_fit.py`, `mmd_exact.py`, and additions to `trainability/__init__.py`'s docstring). Per protocol, only this plan's own files (`trainability/target_grid.py`, `tests/test_target_grid.py`) were staged and committed at each step -- no files from concurrent sessions were touched, reverted, or included in these commits.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- `trainability/target_grid.py` is ready for Plans 17-05/17-06 to consume: `make_target_grid(n)` gives a target distribution and `bitstring_dict_to_vector` maps both actual distributions and parameter-shift deltas into the same length-`2**n` vector space needed for MMD² and its gradient at every sweep point n.
- No blockers. Full 184-test repo suite passes with zero regressions as of this plan's completion.

---
*Phase: 17-trainability-barren-plateau-study*
*Completed: 2026-08-10*
