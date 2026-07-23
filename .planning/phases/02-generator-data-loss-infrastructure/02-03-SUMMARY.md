---
phase: 02-generator-data-loss-infrastructure
plan: 03
subsystem: ml-generator
tags: [pytorch, sklearn, pytest, histogram]

requires:
  - phase: 02-01
    provides: generator/bin_centers.py (make_bin_centers, shared K=400 grid)
provides:
  - "generator/data.py: load_circles_data() -> (X_train, X_test) reproducing quickstart.py's normalized split; compute_p_real(data_xy, bin_centers) -> (400,) probability vector"
affects: [02-04, phase-3-training, phase-5-benchmarking]

tech-stack:
  added: []
  patterns:
    - "Tensor-sum pytest assertions use `float(x.sum()) == pytest.approx(...)`, never a bare `pytest.approx(x, tol)` — third recurrence of the same bug class this phase; see ~/.claude/learnings/2026-07-19-pytest-approx-misuse-grad-tensor.md"
    - "Reproducibility tests must call the function twice and compare the two results — comparing a value to itself (torch.equal(x, x)) is a tautology, not a test"

key-files:
  created: [generator/data.py, tests/test_p_real.py]
  modified: []

key-decisions:
  - "make_circles(n_samples=400, random_state=42) — seeded here even though quickstart.py's own call is unseeded. quickstart.py never needed the raw circle points to be reproducible run-to-run; this module does, since p_real must be a stable Phase 3 training target and a stable Phase 5 benchmark reference. Without this, train_test_split's random_state=42 only controls how an already-random X gets split, not X's contents, so two calls to load_circles_data() produced different data despite the split being 'seeded.'"

patterns-established: []

duration: unrecorded (interactive session, not gsd-executor run)
completed: 2026-07-19
---

# Phase 2, Plan 03: Real-data histogram p_real (GEN-04) Summary

**`generator/data.py` reproduces quickstart.py's circles-data pipeline (with `make_circles` additionally seeded for true reproducibility) and bins `X_train` into a nearest-bin-center probability vector over the same 400 bins as `bin_centers.py`, verified by an 8-test suite across the whole `tests/` directory.**

## Performance

- **Duration:** unrecorded — implemented via owner attempt → review → fix cycle, not gsd-executor.
- **Tasks:** 2 (matches plan)
- **Files created:** 2 (`generator/data.py`, `tests/test_p_real.py`)

## Accomplishments
- `load_circles_data()` matches quickstart.py's normalization exactly (train-derived min/max applied to both splits, not independently re-fit per split).
- `compute_p_real()` produces a `(400,)` non-negative, sum-to-1 vector via nearest-bin-center assignment (`torch.cdist` + `argmin` + `torch.bincount`), parametrized on `bin_centers.shape[0]` rather than a hardcoded 400.
- Found and fixed a real non-determinism gap in the data pipeline (see Decisions Made) that the plan's own reproducibility must-have would have silently failed on.
- `./venv/Scripts/python.exe -m pytest tests/ -v` — 8/8 pass across bin-centers, noise, and p_real together.

## Task Commits

Not committed yet — `generator/data.py` and `tests/test_p_real.py` are untracked (confirmed via `git status`). No commit hashes to report.

## Files Created/Modified
- `generator/data.py` — `load_circles_data() -> (X_train, X_test)`, `compute_p_real(data_xy, bin_centers) -> Tensor(K,)`.
- `tests/test_p_real.py` — 3 tests: shape/non-negativity/sum-to-1, reproducibility (two separate `load_circles_data()` calls compared to each other, not to themselves), held-out separation (exact 320/80 train/test counts).

## Decisions Made
- **Seeded `make_circles(random_state=42)`**, deviating from `quickstart.py`'s unseeded call. Rationale and tradeoff: full detail in `key-decisions` above and in `generator/data.py`'s docstring. This is the kind of non-obvious deviation that needs to be explainable unaided — the short version is "quickstart.py only seeded the *split*, not the *data*, so two runs of quickstart.py get different points; that's fine for a one-off classifier demo but not for a `p_real` that Phase 3/5 depend on being stable."

## Deviations from Plan

### Auto-fixed Issues

**1. Fixed three fatal bugs in the owner's first draft of `generator/data.py`**
- **Found during:** initial review — module failed to import (`pytest --collect-only` errored)
- **Issues:** (a) `def load_circles_data() -> (X_train, X_test):` referenced undefined names in a type-annotation position, evaluated eagerly at def time → `NameError`; (b) `make_circles(n_samples=400)`'s `(X, y)` return was unpacked as if it were a train/test split, then fed into `train_test_split` a second time with mismatched unpacking; (c) `MinMaxScaler` was fit twice, independently, on `X_train` and `X_test`, instead of once on `X_train` and reused via `.transform()` on `X_test`
- **Fix:** rewrote `load_circles_data()` to mirror `quickstart.py`'s manual min-max normalization (min/max from `X_train` only, applied to both splits)
- **Files modified:** `generator/data.py`
- **Verification:** smoke-run from the plan's own verify command — shape `(400,)`, sum `1.0`, min `0.0`

**2. Fixed `pytest.approx` misuse (third occurrence this phase) and tautological reproducibility assertions in `tests/test_p_real.py`**
- **Found during:** initial review
- **Issue:** `assert pytest.approx(p_real.sum(), 1.0)` (no `==`, doesn't compare anything); `torch.equal(X_train, X_train)` / `torch.equal(p_real, p_real)` (compares each value to itself, always true)
- **Fix:** `float(p_real.sum()) == pytest.approx(1.0, abs=1e-5)`; call `load_circles_data()` twice and compare the two independent results
- **Files modified:** `tests/test_p_real.py`
- **Verification:** `pytest tests/test_p_real.py -v` — 3/3 pass

**3. Seeded `make_circles` to satisfy the plan's reproducibility must-have**
- **Found during:** running the corrected test suite — `test_reproducibility` failed even after fixes #1/#2
- **Issue:** `make_circles(n_samples=400)` has no `random_state`, so the raw circle points differ every call regardless of `train_test_split`'s seed
- **Fix:** `make_circles(n_samples=400, random_state=42)`
- **Files modified:** `generator/data.py`
- **Verification:** `pytest tests/test_p_real.py::test_reproducibility -v` — passes; full suite 8/8

---

**Total deviations:** 3 (2 bug-fix rounds on the owner's draft, 1 design decision to close a reproducibility gap `quickstart.py` itself has)
**Impact on plan:** All three are corrections required to meet the plan's own stated must-haves. No scope creep — nothing beyond `load_circles_data`/`compute_p_real` was added.

## Issues Encountered
- `make_circles` non-determinism (see Decisions Made) — resolved by seeding.

## User Setup Required
None — no external service configuration required.

## Next Phase Readiness
- `compute_p_real(X_train, make_bin_centers())` is ready for 02-04's MMD² loss and for Phase 3's training loop.
- Same outstanding gap as 02-01/02-02: nothing from this plan is committed yet.

---
*Phase: 02-generator-data-loss-infrastructure*
*Completed: 2026-07-19*
