---
phase: 02-generator-data-loss-infrastructure
plan: 01
subsystem: ml-generator
tags: [pytest, numpy, torch, scaffolding]

requires:
  - phase: 01
    provides: verified MerLin environment (Python 3.12 venv, torch<2.13, perceval-quandela>=1.2.1)
provides:
  - "pytest installed and pinned in requirements.txt; pytest.ini at repo root (testpaths = tests)"
  - "generator/ and tests/ as importable packages (generator/__init__.py, tests/__init__.py)"
  - "generator/bin_centers.py: make_bin_centers(side=20, lo=-0.1, hi=1.1) -> deterministic (400, 2) torch.Tensor"
affects: [02-02, 02-03, 02-04]

tech-stack:
  added: [pytest==9.1.1]
  patterns:
    - "Determinism proven via numpy.linspace/meshgrid, never a seeded RNG — no torch.rand anywhere in generator/ data components"

key-files:
  created: [pytest.ini, generator/__init__.py, tests/__init__.py, generator/bin_centers.py, tests/test_bin_centers.py]
  modified: [requirements.txt]

key-decisions:
  - "K=400 (side=20) grid over padded [-0.1, 1.1]^2 — covers the circles dataset's min-max-normalized [0,1]^2 range plus 10% padding, per 02-CONTEXT.md's locked bin-center layout decision."

patterns-established:
  - "tests/__init__.py required even though it looks redundant — without it, pytest's rootdir-based import can silently produce duplicate-module errors once multiple test files exist under tests/."

duration: unrecorded (interactive session, not gsd-executor run)
completed: 2026-07-19
---

# Phase 2, Plan 01: Scaffolding + deterministic bin-centers (GEN-03) Summary

**pytest installed and pinned; `generator/`/`tests/` made importable packages; `generator/bin_centers.py` produces a deterministic 400-point grid over `[-0.1, 1.1]^2`, verified by a passing pytest suite.**

## Performance

- **Duration:** unrecorded — implemented before this session's interactive review process began.
- **Tasks:** 2 (matches plan)
- **Files created:** 5 (`pytest.ini`, `generator/__init__.py`, `tests/__init__.py`, `generator/bin_centers.py`, `tests/test_bin_centers.py`)
- **Files modified:** 1 (`requirements.txt` — added `pytest==9.1.1`)

## Accomplishments
- `./venv/Scripts/python.exe -m pytest --collect-only` runs clean; `generator/` and `tests/` import correctly as packages.
- `make_bin_centers()` returns exactly 400 deterministic points (`side=20` default), confirmed identical across repeated calls, spanning the padded `[-0.1, 1.1]` bounding box on both axes.
- No RNG anywhere in the implementation — determinism comes from `numpy.linspace`/`meshgrid`, matching the plan's requirement that this not depend on a fixed seed.

## Task Commits

Not committed yet — `pytest.ini`, `generator/`, `tests/` are untracked and `requirements.txt` is modified in the working tree (confirmed via `git status`). No commit hashes to report; commit before starting 02-03.

## Files Created/Modified
- `pytest.ini` — `testpaths = tests`.
- `generator/__init__.py`, `tests/__init__.py` — empty, mark both directories as regular packages.
- `generator/bin_centers.py` — `make_bin_centers(side=20, lo=-0.1, hi=1.1, dtype=torch.float32) -> Tensor(400, 2)`.
- `tests/test_bin_centers.py` — asserts shape `(400, 2)`, determinism (`torch.equal` across two calls), bounding-box min/max (`pytest.approx(-0.1)`/`pytest.approx(1.1)`), and `torch.isfinite` on all values.
- `requirements.txt` — added `pytest==9.1.1`.

## Decisions Made
None beyond what 02-CONTEXT.md already locked (K=400, `[-0.1, 1.1]²` padding) — this plan implemented that decision, it didn't make a new one.

## Deviations from Plan
None — plan executed as written. (Note: `tests/test_mmd.py` also exists in the repo as an empty placeholder file; it isn't part of this plan's scope and isn't collected by pytest since it has no test functions. Leaving it for whichever later plan — 02-04 — is meant to fill it in.)

## Issues Encountered
None.

## User Setup Required
None — no external service configuration required.

## Next Phase Readiness
- `make_bin_centers()` is ready for 02-03 (`p_real` histogram) and 02-04 (MMD² loss), both of which need this exact same bin-center grid as their shared source of truth.
- Same outstanding gap noted in 02-02-SUMMARY.md: nothing from this plan is committed yet.

---
*Phase: 02-generator-data-loss-infrastructure*
*Completed: 2026-07-19*
