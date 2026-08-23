---
phase: 17-trainability-barren-plateau-study
slug: trainability-barren-plateau-study
status: partial
nyquist_compliant: false
wave_0_complete: true
created: 2026-08-23
---

# Phase 17 — Validation Strategy

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (project virtualenv) |
| **Config file** | `pytest.ini` |
| **Quick run command** | `./venv/Scripts/python.exe -m pytest tests/test_mmd_exact.py tests/test_target_grid.py tests/test_curve_fit.py -q` |
| **Full suite command** | `./venv/Scripts/python.exe -m pytest -q` |
| **Observed quick run** | 31 passed in 28.97s (2026-08-23) |
| **Observed Perceval limitation** | Parameter-shift/sweep collection fails before test execution because Perceval cannot open its user log file (`PermissionError`); existing phase evidence records these tests green. |

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 17-01 | 01 | 1 | TRAIN-01 exact parameter-shift gradients and pi/2 regression | unit | `./venv/Scripts/python.exe -m pytest tests/test_param_shift.py -q` | ✅ | ⚠️ blocked by Perceval log-file permission in current environment; prior verification: green |
| 17-02 | 02 | 1 | TRAIN-01/02 exact NumPy MMD² gradient parity | unit | `./venv/Scripts/python.exe -m pytest tests/test_mmd_exact.py -q` | ✅ | ✅ green (included in observed 31 passed) |
| 17-03 | 03 | 1 | TRAIN-01/06 per-n target grid and compute_p_real parity | unit | `./venv/Scripts/python.exe -m pytest tests/test_target_grid.py -q` | ✅ | ✅ green (included in observed 31 passed) |
| 17-04 | 04 | 1 | TRAIN-02 polynomial-vs-exponential fit with R²/AIC | unit | `./venv/Scripts/python.exe -m pytest tests/test_curve_fit.py -q` | ✅ | ✅ green (included in observed 31 passed) |
| 17-05 | 05 | 2 | TRAIN-01/06 wired sweep, deterministic RNG, summary statistics | integration | `./venv/Scripts/python.exe -m pytest tests/test_sweep.py -q` | ✅ | ⚠️ blocked at collection by same Perceval log-file permission; prior verification: green |
| 17-06 | 06 | 2 | TRAIN-01/03/04/06 real gradient-variance datasets and honest stretch outcome | integration/data | `./venv/Scripts/python.exe gradient_variance_sweep.py ...` (full commands in `17-06-PLAN.md`) | ✅ | ✅ evidence-backed: core CSVs have 10 and 8 rows, finite variance; stretch stopped after n=7 MemoryError |
| 17-07 | 07 | 3 | TRAIN-02/03/04/05/07/08 analysis, plots, and written verdict | integration/document | `./venv/Scripts/python.exe trainability_analysis.py` | ✅ | ✅ evidence-backed: summary CSV has 4 cells and both plots exist |

## Wave 0 Requirements

Existing test infrastructure covers all phase requirements. No new fixtures or implementation tests were required during this reconstruction.

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Owner interpretation of the measured mixed/uniform disagreement | TRAIN-07 | Deliberate owner self-explanation checkpoint | Read the pending placeholder in `docs/trainability-study.md` and record the owner’s interpretation in their own words. |
| Final disposition of the stretch job | TRAIN-08 | Scheduling/compute outcome, not deterministic application behavior | Confirm the documented result in `17-06-SUMMARY.md`: n=7 weight-1 failed with repeatable `MemoryError`, no stretch CSV was produced, and the owner stopped the attempt. |
| Perceval-dependent unit/integration rerun in a writable runtime | TRAIN-01/06 | Current environment permission failure occurs during third-party logger initialization | Run the parameter-shift and sweep commands in an environment where Perceval can create its log file, then retain the exact pytest output. |

## Validation Sign-Off

- [x] All tasks have documented automated verification or an explicit manual-only boundary
- [x] Existing infrastructure covers the phase’s test types
- [x] No implementation files modified
- [x] No tests weakened or skipped silently
- [ ] All current-environment commands green (Perceval logger permission remains)
- [ ] `nyquist_compliant: true` (not claimed because of the environment-dependent rerun and owner gates)

**Approval:** pending

## Validation Audit 2026-08-23

| Metric | Count |
|--------|-------|
| Requirements mapped | 8 |
| Automated green in this run | 5 (MMD, target grid, curve fit; 31 tests total) |
| Evidence-backed from prior phase verification | 8 |
| Current-environment blocked command groups | 2 (parameter-shift, sweep) |
| Manual-only items | 3 |

