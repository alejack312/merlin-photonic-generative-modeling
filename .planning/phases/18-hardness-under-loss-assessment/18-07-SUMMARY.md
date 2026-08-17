---
phase: 18-hardness-under-loss-assessment
plan: 07
subsystem: hardness
tags: [write-up, tvd, anticoncentration, herald-compounding, matplotlib, docs]

# Dependency graph
requires:
  - phase: 18-hardness-under-loss-assessment (Plan 18-06)
    provides: "results/phase18_weight1_loss_sweep.csv, results/phase18_mixed_loss_sweep.csv -- the real measured loss-sweep datasets this plan writes up"
  - phase: 18-hardness-under-loss-assessment (Plan 18-01)
    provides: "docs/iqp-baseline.md's BMS (arXiv:1610.01808) and Park & Oh (arXiv:2510.24137) citation bullets, referenced from this plan's methodology/anticoncentration sections"
provides:
  - "docs/hardness-under-loss-study.md: Phase 18's canonical results document (HARD-01/HARD-02/HARD-05/HARD-07 fully satisfied with real measured numbers and plots), structured so Plan 18-08 can append HARD-04/HARD-06 without restructuring"
  - "hardness_analysis.py: root-level analysis script producing the phase's 3 TVD/anticoncentration plots from the real Plan 18-06 CSVs"
  - "results/phase18_weight1_tvd_plot.png, results/phase18_mixed_tvd_plot.png, results/phase18_anticoncentration_plot.png"
affects: [18-08, 20-technical-write-up]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "hardness_analysis.py mirrors trainability_analysis.py's established shape (matplotlib.use('Agg') before pyplot import, CSV paths as module constants, one function per plot) -- second instance of this project's own analysis-script convention, now established as repeatable across phases."

key-files:
  created:
    - hardness_analysis.py
    - docs/hardness-under-loss-study.md
    - results/phase18_weight1_tvd_plot.png
    - results/phase18_mixed_tvd_plot.png
    - results/phase18_anticoncentration_plot.png
  modified: []

key-decisions:
  - "Eta grid has no literal eta=1.0 row (max is eta=0.99) -- stated explicitly throughout the doc as a near-lossless anchor, never implied to be a true lossless measurement, since the plan's own instruction text assumed an eta=1.0 row that doesn't exist in the real data."
  - "Corrected an initial drafting error before commit: the weight1 TVD-baseline-coincidence note originally claimed tvd_to_uniform (not just tvd_to_product_marginals) matched tvd_to_lossless at eta=0.99 -- the actual CSV data only supports the product-marginals claim (weight1 has no entangling gate, so its lossless output already factors as a product distribution); tvd_to_uniform is materially different (0.5726 vs 0.0100 at n=2). Fixed before commit by re-deriving the claim directly from the CSV numbers rather than trusting the first draft's phrasing."
  - "Corrected a second arithmetic slip before commit: 2/27 (heralded_cz's lossless success rate, Phase 10's established value) was mistyped as 0.09259 in an early draft of the HARD-07 section; the correct value is 0.07407 (2/27), distinct from the herald FAILURE rate 25/27~=0.9259 -- fixed by recomputing 2/27 directly rather than trusting the first-drafted digit string."

patterns-established:
  - "For any future Phase-18-style write-up plan: verify every cross-baseline numeric coincidence claim (e.g. 'X equals Y at this point') directly against the source CSV before writing it into the doc -- two such claims in this plan's first draft were wrong until re-checked against the actual row values."

# Metrics
duration: ~15min
completed: 2026-08-17
---

# Phase 18 Plan 07: Hardness-Under-Loss Write-Up Summary

**Turned Plan 18-06's real measured weight-1/mixed loss-sweep CSVs into `docs/hardness-under-loss-study.md` -- Phase 18's canonical results document, with `hardness_analysis.py` producing the 3 plots it embeds.**

## Performance

- **Duration:** ~15 min
- **Completed:** 2026-08-17
- **Tasks:** 2/2 completed
- **Files modified:** 5 created (1 script, 1 doc, 3 plots)

## Accomplishments
- `hardness_analysis.py` loads both of Plan 18-06's CSVs and produces `results/phase18_weight1_tvd_plot.png`, `results/phase18_mixed_tvd_plot.png` (3-subplot figures: TVD-to-lossless/TVD-to-uniform/TVD-to-product-marginals vs eta, one line per n, error bars from the CSV's own `_std` columns) and `results/phase18_anticoncentration_plot.png` (alpha(eta) for both scopes on one figure, with an alpha=1 uniform reference line).
- `docs/hardness-under-loss-study.md` created with a methodology-before-results structure: loss mechanism (`LC` + explicit `min_detected_photons_filter(0)`, Pitfall 1/2 stated plainly), the real 7-point `ETA_GRID`, the honest n-range per scope (weight1 n=2..6; mixed n=2..4 with n=5 stated as a confirmed hard ceiling, not pending), `n_draws=5`/`seed_base=180814`, and the deliberate "uniform" theta-init scope decision.
- HARD-01/HARD-02 satisfied: loss sweep mechanism described, and Plan 18-02's `NoiseModel`-vs-`LC` cross-check result (`atol=1e-9`, eta in {0.5, 0.8}) cited.
- HARD-05 satisfied: TVD-vs-eta reported for both scopes against both baselines (uniform, product-of-marginals) and the lossless reference, as measured tables/plots -- `18-CONTEXT.md`'s no-crossover-threshold lock respected (both curves reported, "classically easy" interpretation explicitly deferred).
- Anticoncentration alpha(eta) reported for both scopes as an explicit function of eta, with a forward pointer (not a positioning claim) to `docs/iqp-baseline.md`'s BMS Theorem 4 bullet.
- HARD-07 satisfied: herald-success-rate-vs-eta reported as an explicit 7-row table (n-independent within precision, verified against the CSV), and the weight-2 TVD numbers restated as conditioned/postselected on herald success, with `herald_failure_prob` tracked separately from `residual` per this project's standing convention.
- Placeholder `## HARD-04/HARD-06: Positioning and Scope Statement (Plan 18-08)` heading left at the end, explicitly marked incomplete-not-abandoned.

## Task Commits

Each task was committed atomically:

1. **Task 1: Build hardness_analysis.py -- load CSVs, produce plots** - `f347986` (feat)
2. **Task 2: Write docs/hardness-under-loss-study.md** - `b241717` (docs)

## Files Created/Modified
- `hardness_analysis.py` - root-level analysis script (mirrors `trainability_analysis.py`), loads both loss-sweep CSVs, produces 3 plots, prints headline lowest/highest-eta numbers
- `docs/hardness-under-loss-study.md` - Phase 18's canonical results document
- `results/phase18_weight1_tvd_plot.png`, `results/phase18_mixed_tvd_plot.png`, `results/phase18_anticoncentration_plot.png` - the 3 plots the doc embeds

## Decisions Made
- Used `eta=0.99` (the grid's actual maximum) as the "near-lossless anchor" representative point everywhere the plan's task text referred to "eta=1.0" -- the real `ETA_GRID` has no `eta=1.0` row, and the doc states this explicitly rather than silently substituting 0.99 without comment.
- x-axis on all 3 plots is inverted (eta descending left-to-right is reversed to ascending-eta/low-loss-first reading, i.e. `eta=0.99` at the left) so "loss increasing" reads naturally left-to-right, per the plan's own instruction.
- Two numeric claims in the doc were corrected during drafting after re-checking against the actual CSV values rather than being committed as first-drafted (see key-decisions above: the weight1 baseline-coincidence claim, and the 2/27 vs 0.09259 arithmetic slip in the HARD-07 section) -- both fixed before the Task 2 commit, so no incorrect numbers reached git history.

## Deviations from Plan

None beyond the two in-flight self-corrections during drafting (caught and fixed before commit, not left as errors) -- no Rule 1-4 deviations. Plan executed as written.

## Issues Encountered
None. Both tasks ran cleanly on the first attempt (`hardness_analysis.py` produced all 3 plots with no errors; the doc's numbers were transcribed from the script's printed headline summary and the raw CSVs).

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness

**Ready for Plan 18-08:**
- `docs/hardness-under-loss-study.md` has its methodology, HARD-01/HARD-02/HARD-05/HARD-07 results sections fully written and committed, with a placeholder `## HARD-04/HARD-06: Positioning and Scope Statement (Plan 18-08)` heading ready for Plan 18-08 to append its own sections -- no restructuring needed.
- Plan 18-08's HARD-04 eta-to-depolarizing-rate translation work now has real measured numbers to ground itself against, in particular the weight-2 herald-success-rate-vs-eta table (this document's HARD-07 section) that `18-RESEARCH.md`'s "compounded gate-failure rate" candidate direction needs.
- No blockers.

---
*Phase: 18-hardness-under-loss-assessment*
*Completed: 2026-08-17*
