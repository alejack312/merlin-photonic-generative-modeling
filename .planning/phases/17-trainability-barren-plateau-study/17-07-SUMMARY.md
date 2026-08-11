---
phase: 17-trainability-barren-plateau-study
plan: 07
subsystem: quantum-ml-research
tags: [curve-fit, scipy, matplotlib, barren-plateau, gradient-variance, cross-reference]

# Dependency graph
requires:
  - phase: 17 (Plan 17-04)
    provides: trainability/curve_fit.py's fit_and_compare (poly-vs-exp model comparison, R^2/AIC)
  - phase: 17 (Plan 17-06)
    provides: results/phase17_weight1_gradient_variance.csv (n=2..6) and results/phase17_mixed_gradient_variance.csv (n=2..5), both init schemes, real CORE gradient-variance-vs-n data
provides:
  - trainability_analysis.py -- runs fit_and_compare against real data for all 4 (generator_scope, init_scheme) cells, cross-references docs/iqp-baseline.md's plateau rule, writes summary CSV + 2 plots
  - results/phase17_curve_fit_summary.csv -- per-cell exp/poly params, R^2, AIC, verdict, baseline-rule agreement
  - results/phase17_weight1_curve_fit.png, results/phase17_mixed_curve_fit.png
  - docs/trainability-study.md -- Phase 17's canonical results document (methodology, init/normalization, generator scope, results, honest max-n, cross-reference verdict, scope statement)
affects: [20 (Technical Write-Up, draws on docs/trainability-study.md directly)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "STRETCH-CSV auto-merge pattern: analysis scripts check os.path.exists on a *_stretch.csv sibling file and merge in any extra rows found, never failing on absence -- lets a background job's eventual output get picked up by a later re-run without code changes"

key-files:
  created:
    - trainability_analysis.py
    - results/phase17_curve_fit_summary.csv
    - results/phase17_weight1_curve_fit.png
    - results/phase17_mixed_curve_fit.png
    - docs/trainability-study.md
  modified: []

key-decisions:
  - "fit_verdict_to_plateau_label maps fit_and_compare's 'exp' verdict to 'plateau' only when the fitted decay rate b>0 (actually shrinking with n), not merely when the exp model statistically outfits poly -- an exp model winning with b<0 would be a growing, not shrinking, curve and is not a plateau signature despite the AIC comparison favoring it."
  - "docs/iqp-baseline.md's 'not complete_graph_like' rule clause is treated as inapplicable (not silently assumed true or false) when cross-referencing against this project's photonic circuits, since this project's circuits have no established mapping onto that qubit-side structural notion -- stated explicitly in the doc rather than glossed over."
  - "Ran with CORE data only (STRETCH CSVs do not exist as of this plan's execution) -- trainability_analysis.py checks for and would auto-merge stretch CSVs if present, so no code change is needed if/when the background STRETCH job completes later; this plan's written verdict is explicitly scoped to the CORE n<=6 range."
  - "agrees_with_baseline_rule is stored as a 3-way string (agree/disagree/inconclusive) rather than forced into a boolean -- 2 of 4 cells produced a statistically inconclusive fit_and_compare verdict (weight1/small_angle, mixed/small_angle), and collapsing that into False would misrepresent 'no clear signal' as 'disagrees with the rule'."

patterns-established:
  - "docs/trainability-study.md's Cross-reference verdict section ends with a labeled '> Owner interpretation: [pending]' placeholder rather than an asserted final conclusion -- matches this repo's established self-explanation-checkpoint convention (CLAUDE.md, Phase 7/GEN-07 precedent) for any interpretive claim about measured results."

# Metrics
duration: ~20 min
completed: 2026-08-11
---

# Phase 17 Plan 07: Curve-Fit Analysis & Cross-Reference Summary

**Ran Plan 17-04's poly-vs-exponential model comparison against Plan 17-06's real gradient-variance data for all 4 (generator_scope, init_scheme) cells, finding 2 statistically clear "exp" verdicts (weight1/uniform, mixed/uniform), 2 inconclusive fits, and one direct disagreement with `docs/iqp-baseline.md`'s qubit-side plateau rule (mixed/uniform: rule predicts no_plateau at n_max=5, measured data shows exponential decay) — written up honestly in `docs/trainability-study.md` with an owner-interpretation placeholder rather than an asserted conclusion.**

## Performance

- **Duration:** ~20 min
- **Completed:** 2026-08-11
- **Tasks:** 2/2
- **Files modified:** 5 created (trainability_analysis.py, 1 CSV, 2 PNGs, 1 doc)

## Accomplishments

- `trainability_analysis.py`: loads both CORE gradient-variance CSVs (auto-merging STRETCH CSVs if present -- none were, as of this run), runs `fit_and_compare` per (generator_scope, init_scheme), applies `docs/iqp-baseline.md`'s empirical rule to this project's own n range, writes `results/phase17_curve_fit_summary.csv` and two 2-subplot log-scale PNGs.
- All 4 cells produced a definite fit_and_compare verdict category: `weight1/small_angle` inconclusive (R²≈0.4-0.5 both models), `weight1/uniform` exp (R²=0.999, clearly decaying), `mixed/small_angle` inconclusive (R²≈0 both models, no discernible trend across n=2..5), `mixed/uniform` exp (R²=0.910, decaying).
- Cross-reference against `docs/iqp-baseline.md`'s rule: `weight1/uniform` agrees (rule predicts plateau at n_max=6≥6, measured shows decay); `mixed/uniform` disagrees (rule predicts no_plateau since mixed only reached n_max=5<6, but measured data shows a clear exponential decay signature anyway); the two `small_angle` cells are inconclusive on the measured side so agreement can't be assessed either way.
- `docs/trainability-study.md`: all 7 required sections (methodology, TRAIN-03 init/normalization, TRAIN-04 generator scope, results table+plots, TRAIN-05/08 honest max-n statement, TRAIN-07 cross-reference verdict with owner-interpretation placeholder, scope-limitation paragraph), matching `docs/iqp-baseline.md`/`docs/iqp-photonic-encoding.md`'s existing terse documentation style.
- Full 197/197 repo test suite passes, zero regressions (this plan added no new test-covered logic — `trainability_analysis.py` is a root-level analysis script composing already-tested Plan 17-04/17-06 code, matching `cp_alpha_sweep.py`'s established pattern of not itself carrying a test file).

## Task Commits

1. **Task 1: Curve-fit analysis, cross-reference, and plots** - `2b2f10b` (feat)
2. **Task 2: Write docs/trainability-study.md** - `358cc5a` (docs)

## Files Created/Modified

- `trainability_analysis.py` - Loads both gradient-variance CSVs (+ stretch CSVs if present), runs `fit_and_compare` per (generator_scope, init_scheme), applies `docs/iqp-baseline.md`'s plateau rule, writes summary CSV + 2 PNGs.
- `results/phase17_curve_fit_summary.csv` - 4 rows: per-(generator_scope, init_scheme) n range, exp/poly params/R²/AIC, verdict, baseline-rule prediction, agreement.
- `results/phase17_weight1_curve_fit.png`, `results/phase17_mixed_curve_fit.png` - Log-scale variance-vs-n plots, 2 subplots (one per init_scheme), scatter + both fitted curves.
- `docs/trainability-study.md` - Phase 17's canonical results document.

## Decisions Made

- **`fit_verdict_to_plateau_label` requires the exp fit's decay rate `b > 0`, not just an "exp" AIC win, to count as a plateau signature.** An exp model that statistically outfits poly but with a *negative* `b` (growing, not shrinking, variance) would not be a shrinking-with-n signature — the plan's own wording ("does the variance data show exponential decay ... or not") asked for this distinction, so it's encoded rather than left implicit. In this run all "exp"-winning cells had `b > 0`, so this branch didn't change any cell's outcome, but it's load-bearing for correctness if re-run against different/extended data.
- **`docs/iqp-baseline.md`'s `not complete_graph_like` clause treated as inapplicable, not silently true/false, for this project's circuits** — stated explicitly in both the script's docstring and the write-up, per the plan's explicit instruction not to silently assume the mapping doesn't matter.
- **`agrees_with_baseline_rule` stored as `agree`/`disagree`/`inconclusive`, not a boolean** — 2 of 4 cells (`weight1/small_angle`, `mixed/small_angle`) produced a statistically inconclusive `fit_and_compare` verdict; forcing that into `False` would have misrepresented "no clear signal either way" as "actively disagrees with the rule."
- **Ran against CORE data only.** `results/phase17_weight1_gradient_variance_stretch.csv` / `results/phase17_mixed_gradient_variance_stretch.csv` do not exist as of this plan's execution (checked directly, not assumed) — `trainability_analysis.py`'s data-loading step already checks for and would merge them automatically if/when the background STRETCH job (launched during Plan 17-06, no time-box) completes, so no future code change is needed; this plan's written verdict is explicitly scoped to the n<=6 CORE range and states that scoping honestly in `docs/trainability-study.md`.

## Deviations from Plan

None - plan executed exactly as written. No bugs found, no missing critical functionality, no blocking issues, no architectural changes needed.

## Issues Encountered

- `scipy.optimize.curve_fit` emitted `OptimizeWarning: Covariance of the parameters could not be estimated` for at least one cell during the run (a symptom of a poorly-identified, large-magnitude-cancelling `a`/`c` parameterization at only 4-5 data points, seen in `mixed/uniform`'s and `weight1/uniform`'s fitted params). This does not invalidate the AIC-based verdict (both thresholds were cleared with margin), but is reported honestly in `docs/trainability-study.md`'s Results section as a fit-quality caveat rather than hidden — the fitted decay *rate* in these near-degenerate cases should be read as "exponential shape fits better than power-law," not as a precisely determined constant.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- **Phase 17 is now fully complete.** All 7 plans (17-01 through 17-07) shipped; TRAIN-01 through TRAIN-08 are all satisfiable from this phase's artifacts (`trainability/` module, `results/phase17_*_gradient_variance.csv`, `results/phase17_curve_fit_summary.csv`, `docs/trainability-study.md`).
- **`docs/trainability-study.md` is ready for Phase 20 (Technical Write-Up) to draw on directly** — it is self-contained (methodology, init/normalization, generator scope, results, honest max-n, cross-reference) and does not require re-deriving anything from raw CSVs.
- **Open item, not a blocker:** `docs/trainability-study.md`'s Cross-reference verdict section has a labeled `> Owner interpretation: [pending]` placeholder — the owner has not yet filled in their own interpretation of the one measured disagreement (`mixed/uniform`). This is intentional (self-explanation-checkpoint convention, not an oversight) and does not block Phase 18 or further Phase 17 work, since Phase 17 has no further plans.
- **STRETCH job (n=7 weight-1, n=6 mixed) status is unchanged from Plan 17-06's summary** — still not complete as of this plan's execution. If it completes later, re-running `trainability_analysis.py` will automatically pick up the extra data points and can produce an updated summary/plots/doc revision; this is not required for Phase 17 to be considered complete, per Plan 17-06's and this plan's explicit authorization.
- **Out-of-scope discovery (not fixed, reported only):** `results/Figure_1.png`, `results/Figure_2.png`, `results/Figure_3.png` are untracked, unrelated files present in the working tree at the start of this plan's execution (not created by this plan, not referenced by any code touched in this plan). Left untouched — outside this plan's scope to investigate or clean up.

---
*Phase: 17-trainability-barren-plateau-study*
*Completed: 2026-08-11*
