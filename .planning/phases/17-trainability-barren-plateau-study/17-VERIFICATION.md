---
phase: 17-trainability-barren-plateau-study
verified: 2026-08-11T18:29:56Z
status: passed
score: 8/8 must-haves verified (TRAIN-01..TRAIN-08)
human_verification:
  - test: "Fill in the 'Owner interpretation' placeholder in docs/trainability-study.md's Cross-reference verdict section"
    expected: "Owner explains, in their own words, the one measured disagreement (mixed/uniform: baseline rule predicts no_plateau at n_max=5<6, but measured data shows a clear exponential-decay signature anyway) and what it does/doesn't establish -- this repo's CLAUDE.md self-explanation-checkpoint convention"
    why_human: "Explicitly a placeholder ('> Owner interpretation: [pending]') left for the project owner per this repo's established convention (Phase 7/GEN-07 precedent) -- not something a verifier can or should fill in"
  - test: "Confirm whether the STRETCH background job (n=7 weight-1, n=6 mixed) is still running or has been abandoned"
    expected: "Either results/phase17_weight1_gradient_variance_stretch.csv / results/phase17_mixed_gradient_variance_stretch.csv appear later (re-run trainability_analysis.py to auto-merge), or the job is explicitly declared stopped at/after the 2026-08-20 mid-milestone checkpoint per CONTEXT.md"
    why_human: "A python.exe process (~4.5GB RSS) was observed still running on this machine at verification time, consistent with the STRETCH job from Plan 17-06 still in progress -- its eventual outcome is a scheduling/compute decision, not something to verify structurally"
---

# Phase 17: Trainability / Barren-Plateau Study Verification Report

**Phase Goal:** Measure whether the weight-1(+weight-2) IQP-photonic circuit shows barren-plateau behavior, via exact parameter-shift gradients (not MerLin QuantumLayer autograd) -- a specific measured claim, reported honestly either direction.
**Verified:** 2026-08-11T18:29:56Z
**Status:** passed
**Re-verification:** No -- initial verification

## Goal Achievement

### Observable Truths (derived from ROADMAP.md success criteria / TRAIN-01..08)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Exact parameter-shift gradient (shift=pi/4, no division) implemented for weight-1 and weight-2, proven exact/cross-validated, with the pi/2-shift pitfall documented via a regression test | VERIFIED | `trainability/param_shift.py` (126 lines); `tests/test_param_shift.py::TestWeight1ClosedFormExactness`, `TestWeight2FiniteDifferenceCrossCheck`, `TestPiOverTwoShiftPitfallRegression` all pass |
| 2 | Pure-numpy exact MMD^2 loss + gradient, numerically matching the existing torch `generator/mmd.py` | VERIFIED | `trainability/mmd_exact.py` (77 lines); `tests/test_mmd_exact.py` passes, torch-parity + synthetic-linear-model exactness checks present |
| 3 | Per-n K=2^n target grid generalizing v1.0's fixed 462-bin grid, cross-validated against `generator/data.py::compute_p_real` | VERIFIED | `trainability/target_grid.py` (132 lines); `tests/test_target_grid.py` passes |
| 4 | Poly-vs-exponential model comparison via `scipy.optimize.curve_fit` + R^2/AIC, correctly distinguishing exp vs poly on synthetic ground-truth data | VERIFIED | `trainability/curve_fit.py` (124 lines); `tests/test_curve_fit.py` passes |
| 5 | RNG substream + summary-stats infra, and a sweep runner composing gradient+MMD+grid into pooled gradient-variance-vs-n | VERIFIED | `trainability/rng.py`, `trainability/stats.py`, `trainability/sweep.py`; `tests/test_sweep.py` passes (end-to-end wiring smoke tests) |
| 6 | A real gradient-variance-vs-n dataset exists for weight-1-only, >=3 system sizes, >=100 draws, both init regimes | VERIFIED | `results/phase17_weight1_gradient_variance.csv`: 10 rows, n=2..6 (5 sizes) x {small_angle, uniform}, `n_samples`=200-300 per row, all `var` finite |
| 7 | A real gradient-variance-vs-n dataset exists for mixed weight-1+weight-2 (reusing Phase 13 composability) | VERIFIED | `results/phase17_mixed_gradient_variance.csv`: 8 rows, n=2..5 (4 sizes) x {small_angle, uniform}, all `var` finite; `photonic_weight2_iqp_distribution` called directly in `trainability/sweep.py` |
| 8 | Poly-vs-exp comparison run against the real data, plotted, with a written verdict per (scope, init) cell | VERIFIED | `results/phase17_curve_fit_summary.csv` (4 rows, all fields populated); `results/phase17_weight1_curve_fit.png`, `results/phase17_mixed_curve_fit.png` exist |
| 9 | Init distributions and normalization convention stated explicitly (TRAIN-03) | VERIFIED | `docs/trainability-study.md` "Parameter-initialization and normalization" section: `small_angle ~ U(-0.1,0.1)`, `uniform ~ U(0,2pi)`, passive/unitary photon-number-conserving normalization stated |
| 10 | Generator scope stated with reasoning (TRAIN-04) | VERIFIED | `docs/trainability-study.md` "Generator scope" section: weight1 vs mixed, reasoning tied to Phase 13's validated composability |
| 11 | Honest max-n statement relative to both the n>=6 qubit-baseline threshold and the N=20-24 literature fit-flip threshold (TRAIN-05/08) | VERIFIED | `docs/trainability-study.md` "Honest max-n statement": weight1 n_max=6 (meets n>=6 at boundary), mixed n_max=5 (misses by one), neither reaches N=20-24; compute-cost reasoning given (`C(3n-1,n)~6.75^n`); STRETCH job status reported honestly as not-yet-complete, not silently omitted |
| 12 | Cross-reference against `docs/iqp-baseline.md`'s empirical plateau rule (TRAIN-07) | VERIFIED | `docs/trainability-study.md` "Cross-reference verdict" table: 4 cells, explicit agree/disagree/inconclusive per cell, including one stated disagreement (mixed/uniform) not smoothed over |

**Score:** 12/12 truths verified (mapping onto all 8 TRAIN-01..08 requirements)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `trainability/param_shift.py` | Exact parameter-shift deltas, weight-1 + weight-2 | VERIFIED | 126 lines, `weight1_param_shift_delta`/`weight2_param_shift_delta`, SHIFT hardcoded to pi/4 (no caller override), imported by `trainability/sweep.py` |
| `trainability/mmd_exact.py` | Numpy MMD^2 + exact gradient | VERIFIED | 77 lines, `gaussian_kernel_matrix_np`/`mmd2_np`/`mmd2_grad`, no torch import, imported by `trainability/sweep.py` |
| `trainability/target_grid.py` | Per-n K=2^n grid + dict<->vector utilities | VERIFIED | 132 lines, `make_target_grid`/`bitstring_dict_to_vector`, imported by `trainability/sweep.py` |
| `trainability/curve_fit.py` | Poly-vs-exp model comparison, R^2+AIC | VERIFIED | 124 lines, `exp_model`/`poly_model`/`aic`/`fit_and_compare`, imported by `trainability_analysis.py` |
| `trainability/sweep.py` | Sweep runner composing all 3 gradient primitives | VERIFIED | 178 lines, `run_gradient_variance_sweep`/`pooled_gradients_for_cell`, imported by `gradient_variance_sweep.py` |
| `trainability/rng.py` | Deterministic reorder-safe RNG substreams | VERIFIED | 38 lines, `derive_seed`/`get_rng` (blake2b hash of labeled coordinate tuple, not a running counter) |
| `trainability/stats.py` | Gradient-sample summary statistics | VERIFIED | 33 lines, `summarize_gradient_samples` returns mean/var/std/median/abs_mean/rms |
| `gradient_variance_sweep.py` | Root-level CLI wrapping the sweep runner | VERIFIED | 286 lines, argparse CLI, CSV writer with flush+fsync, draw-chunking mode (`--draw-start`/`--draw-count`/`--combine-chunks`) |
| `trainability_analysis.py` | Curve-fit + cross-reference analysis script | VERIFIED | 253 lines, loads both CSVs, runs `fit_and_compare`, applies baseline rule, writes summary CSV + plots |
| `results/phase17_weight1_gradient_variance.csv` | n=2..6, both init schemes, >=100 draws/cell | VERIFIED | 10 data rows, all columns populated, `var` finite in every row |
| `results/phase17_mixed_gradient_variance.csv` | n=2..5, both init schemes, >=100 draws/cell | VERIFIED | 8 data rows, all columns populated, `var` finite in every row |
| `results/phase17_curve_fit_summary.csv` | Per-cell exp/poly params/r2/aic/verdict | VERIFIED | 4 data rows, all columns populated including `baseline_rule_prediction`/`agrees_with_baseline_rule` |
| `docs/trainability-study.md` | Phase 17's canonical results document | VERIFIED | 186 lines, all required sections present (methodology, TRAIN-03/04/05/07/08 statements, results table+plots, scope limitations) |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `trainability/param_shift.py` | `iqp_photonic_encoding.photonic_iqp_distribution`/`photonic_weight2_iqp_distribution` | direct import + call, thetas[k] +/- pi/4 | WIRED | Confirmed in source; tests exercise this path |
| `trainability/mmd_exact.py` | `generator/mmd.py` | independent numpy reimplementation, cross-validated in tests only (never imported at runtime, by design) | WIRED (as designed) | `tests/test_mmd_exact.py` imports both and compares numerically |
| `trainability/target_grid.py` | `generator/data.py::load_circles_data`/`compute_p_real` | `load_circles_data()` reused; `compute_p_real` cross-validated in tests | WIRED | Confirmed in source and `tests/test_target_grid.py` |
| `trainability/sweep.py` | `param_shift`, `mmd_exact`, `target_grid` | direct function calls per draw x tracked-param | WIRED | Confirmed in `pooled_gradients_for_cell`; `tests/test_sweep.py` exercises full composition |
| `gradient_variance_sweep.py` | `trainability.sweep.run_gradient_variance_sweep`/`pooled_gradients_for_cell` | direct call, CSV row per (n, init_scheme) | WIRED | Confirmed in source; produced the real CSVs in `results/` |
| `trainability_analysis.py` | `trainability.curve_fit.fit_and_compare` | direct call per (scope, init_scheme) cell on real CSV data | WIRED | Confirmed in source; produced `results/phase17_curve_fit_summary.csv` with real numbers, not placeholders |
| `trainability_analysis.py` | `docs/iqp-baseline.md`'s empirical rule | `baseline_rule_prediction()` implements the rule directly, applied to real `ns` | WIRED | Confirmed in source and reflected in `docs/trainability-study.md`'s cross-reference table |

### Requirements Coverage

| Requirement | Status | Evidence |
|-------------|--------|----------|
| TRAIN-01 | SATISFIED | Exact parameter-shift sweep, weight1 n=2..6 (5 sizes >=3), 100 draws/cell x up to 3 tracked params, both init schemes |
| TRAIN-02 | SATISFIED | `curve_fit.py::fit_and_compare` (R^2+AIC, delta-AIC>2.0 threshold), applied via `trainability_analysis.py`, plotted in 2 PNGs |
| TRAIN-03 | SATISFIED | `docs/trainability-study.md` explicit init distributions + normalization statement |
| TRAIN-04 | SATISFIED | `docs/trainability-study.md` explicit weight1/mixed scope statement with Phase-13-reuse reasoning |
| TRAIN-05 | SATISFIED | `docs/trainability-study.md` honest max-n statement (n<=6, both thresholds addressed) |
| TRAIN-06 | SATISFIED | `results/phase17_mixed_gradient_variance.csv` real data via `photonic_weight2_iqp_distribution` |
| TRAIN-07 | SATISFIED | Cross-reference table in `docs/trainability-study.md`, one disagreement stated plainly (mixed/uniform) |
| TRAIN-08 | SATISFIED | N=20-24 not reached; honestly reported with quantified compute-cost reasoning and stretch-job status, not silently omitted; matches phase goal's "reported honestly either direction" |

Note: `.planning/REQUIREMENTS.md`'s checkbox table (lines 12-19, 105-112) still shows all 8 TRAIN items as unchecked/"Pending" -- a stale bookkeeping artifact, not a functional gap. Evidence in the codebase and `docs/trainability-study.md` satisfies all 8 items; recommend updating REQUIREMENTS.md's checkboxes/status column to reflect this.

### Anti-Patterns Found

None blocking. One benign false-positive from the stub-pattern grep: `docs/trainability-study.md:32` contains the phrase "deliberately not implemented", which is a documented design decision (no Monte-Carlo MMD^2 fallback needed, since exact enumeration is tractable at this project's K<=2^8 scale) rather than an incomplete-implementation marker.

Untracked stray files `results/Figure_1.png`, `results/Figure_2.png`, `results/Figure_3.png` are present in the working tree but are not produced by, or referenced by, any Phase 17 code -- already flagged as an out-of-scope discovery in Plan 17-07's own SUMMARY.md and left untouched. Not a Phase 17 gap.

### Test Suite

Full repo suite: 197/197 passed (`python -m pytest -q`, ~58s). Phase-17-specific subset (`test_param_shift.py`, `test_mmd_exact.py`, `test_target_grid.py`, `test_curve_fit.py`, `test_sweep.py`): 52/52 passed.

### Human Verification Required

1. **Owner interpretation placeholder** -- `docs/trainability-study.md`'s Cross-reference verdict section ends with `> Owner interpretation: [pending]`. This is an intentional placeholder per this repo's CLAUDE.md self-explanation-checkpoint convention (the owner, not Claude, is meant to interpret the measured disagreement), not a code gap. Does not block Phase 17 completion per Plan 17-07's own SUMMARY.md, but the owner should fill it in before Phase 20 (Technical Write-Up) draws on this document.
2. **STRETCH job status** -- a `python.exe` process (~4.5GB RSS) was observed still running on this machine at verification time, consistent with Plan 17-06's background STRETCH job (n=7 weight-1, n=6 mixed) still in progress. Its outcome (complete, still running, or stopped at the 2026-08-20 checkpoint) is a scheduling decision for the owner, not something to verify structurally -- `trainability_analysis.py` will auto-merge the stretch CSVs if/when they appear, no code change required.

### Gaps Summary

No gaps found. All 8 TRAIN-01..08 requirements are satisfied by real, tested, wired code and a real measured dataset (not stubs or placeholders). The phase's central measured claim is produced and reported honestly in both directions: `weight1/uniform` and `mixed/uniform` show a statistically clear exponential-decay (barren-plateau) signature; `weight1/small_angle` and `mixed/small_angle` are inconclusive; one cross-reference disagreement against `docs/iqp-baseline.md`'s qubit-side rule (`mixed/uniform`) is stated plainly rather than smoothed over. The two open items above are explicitly-authorized non-blocking outcomes (owner-interpretation placeholder, in-progress stretch job), not implementation gaps.

---

*Verified: 2026-08-11T18:29:56Z*
*Verifier: Claude (gsd-verifier)*
