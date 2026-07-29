---
phase: 07-mechanism-validation
plan: 02
subsystem: testing
tags: [pytorch, sigma-sweep, gaussian-kernel, mmd, photonic-generator, mechanism-validation]

# Dependency graph
requires:
  - phase: 04-generator-natural-ordering
    provides: NaturallyOrderedGenerator, natural_sorted_centers, build_naturally_ordered_generator, results/phase4_sweep_metrics.csv (K=400 sigma sweep to compare against)
  - phase: 07-mechanism-validation (plan 01)
    provides: sequencing precedent (wave 2, depends_on 07-01) and this project's resumable-checkpoint script pattern
provides:
  - Fresh 5-point SIGMA_GRID sweep against the K=462 natural-order grid, directly comparable to Phase 4's K=400 sweep
  - Measured (not interpreted) evidence on whether sigma=0.1 is still the best bandwidth at K=462
affects: [any future retuning of NaturallyOrderedGenerator hyperparameters, owner's confound interpretation pass]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Resumable per-value sweep script pattern (skip-if-checkpoint-exists, run in foreground) reused a third time (sweep.py -> natural_order_train.py -> sigma_resweep.py) for any future hyperparameter re-sweep in this codebase"

key-files:
  created:
    - sigma_resweep.py
    - results/phase7_sigma_resweep_metrics.csv
    - results/phase7_sigma_resweep_comparison.png
    - results/phase7_sigma_resweep_summary.md
    - results/phase7_sigma_0.02_checkpoint.pt
    - results/phase7_sigma_0.05_checkpoint.pt
    - results/phase7_sigma_0.1_checkpoint.pt
    - results/phase7_sigma_0.2_checkpoint.pt
    - results/phase7_sigma_0.4_checkpoint.pt
  modified: []

key-decisions:
  - "EPOCHS=300/LR=0.01/BATCH_SIZE=32 held fixed at Phase 4's values, isolating sigma as the one variable under test (locked in the plan, not decided at implementation time)"
  - "Fresh random init per sigma (no checkpoint reuse across sigma values), matching sweep.py's convention exactly"
  - "Summary reports the K=462 argmax as a plain descriptive fact only -- explicitly does not conclude whether stale sigma was or wasn't a confound in the reported ring_mass 0.609->0.691 improvement (locked in the plan)"

patterns-established: []

# Metrics
duration: ~20min
completed: 2026-07-29
---

# Phase 7 Plan 02: Sigma Re-sweep (K=462) Summary

**Re-ran Phase 4's 5-point SIGMA_GRID sweep fresh against the K=462 natural-order grid; the K=462 argmax is sigma=0.1 (ring_mass=0.7145), matching the bandwidth already in use for every reported K=462 result, with every other tested sigma at least 0.09 lower.**

## Performance

- **Duration:** ~20 min
- **Completed:** 2026-07-29T17:52:00Z
- **Tasks:** 2/2
- **Files modified:** 9 created, 0 modified

## Accomplishments
- Built `sigma_resweep.py`, adapting `sweep.py`'s exact resumable-per-value structure to train 5 fresh `NaturallyOrderedGenerator` models (K=462) from scratch, one per `SIGMA_GRID` value, with `EPOCHS`/`LR`/`BATCH_SIZE` held fixed at Phase 4's values.
- Ran the full sweep to completion (5/5 checkpoints, 300 epochs each) as a backgrounded long-running process, matching this project's established pattern for scripts exceeding a single tool-call's timeout.
- Produced `results/phase7_sigma_resweep_metrics.csv` (real ring_mass/gap_mass per sigma), a 6-panel comparison figure, and `results/phase7_sigma_resweep_summary.md` with a K=400 vs K=462 side-by-side table sourced from both CSVs, plus the K=462 argmax stated as a plain descriptive fact.
- Re-verified the full existing test suite (53/53) still passes, confirming this plan's file-only additions (no `generator/`/`tests/` changes) introduced no regressions.

## Task Commits

1. **Task 1: sigma_resweep.py — resumable per-sigma retrain at K=462, run to completion** - `f269616` (feat)
2. **Task 2: results/phase7_sigma_resweep_summary.md — K=400 vs K=462 comparison, and full regression check** - `2a45895` (docs)

## Files Created/Modified
- `sigma_resweep.py` - `train_all_sigmas` (resumable per-sigma retrain), `build_comparison_figure` (6-panel scatter), `main` orchestration; imports `NaturallyOrderedGenerator`/`natural_sorted_centers` (K=462), never `make_bin_centers`/`build_generator` (K=400)
- `results/phase7_sigma_resweep_metrics.csv` - sigma, ring_mass, gap_mass per SIGMA_GRID value at K=462 (real computed numbers)
- `results/phase7_sigma_resweep_comparison.png` - 6-panel figure: real data + one generated-scatter panel per sigma
- `results/phase7_sigma_0.02_checkpoint.pt` / `_0.05_` / `_0.1_` / `_0.2_` / `_0.4_checkpoint.pt` - 5 fresh trained model checkpoints, K=462
- `results/phase7_sigma_resweep_summary.md` - K=400 vs K=462 side-by-side table, descriptive argmax-sigma statement, owner-interpretation-pending placeholder

## Decisions Made
- `EPOCHS=300`/`LR=0.01`/`BATCH_SIZE=32` fixed, fresh-random-init-per-sigma, and interpretation-deferred-to-owner — all three were pre-locked in `07-02-PLAN.md`'s objective and task 1/2 action sections before execution began, per this codebase's "no silent unilateral design decisions" convention.
- No new implementation decisions were required beyond the plan's exact prescribed structure — `sigma_resweep.py` follows `sweep.py`'s pattern and `natural_order_train.py`'s K=462 imports verbatim, with no deviation from the given code skeleton.

## Deviations from Plan

None — plan executed exactly as written. Unlike 07-01, no blocking bug was encountered: `train_step`, `NaturallyOrderedGenerator`, and `ring_band_metrics` were all reused unchanged from working, already-proven code paths (no new `torch.func`/Jacobian machinery in this plan), so no fix was needed to get real numbers out of the sweep.

## Issues Encountered
The `python sigma_resweep.py` invocation exceeded a single tool-call's timeout partway through training (as anticipated by the plan's own runtime estimate, ~35 min total for all 5 sigmas); it was moved to a background process and polled until `results/phase7_sigma_resweep_metrics.csv` appeared, per the plan's explicit guidance ("if a single tool-call invocation times out partway through, re-invoke... already-completed sigmas are skipped"). The run completed in one continuous background execution without needing a second invocation — all 5 checkpoints and both output artifacts were produced in a single pass.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness

**Measured result (reported here as fact, not interpreted — per this project's CLAUDE.md, interpretation is the owner's job):**
- K=462 sigma sweep: sigma=0.02 → ring_mass=0.4425; sigma=0.05 → ring_mass=0.6247; sigma=0.1 → ring_mass=0.7145 (argmax); sigma=0.2 → ring_mass=0.6067; sigma=0.4 → ring_mass=0.5467.
- The K=462 argmax is sigma=0.1 — the same bandwidth already used for every reported K=462 result (`results/phase4_natural_checkpoint.pt` and all downstream Phase 5 benchmarks). No re-tuning is indicated by this sweep: sigma=0.1 was not merely "carried forward, never re-checked" — re-checking confirms it is still the best of the five tested values at the new grid width.
- Separately, K=462 ring_mass is higher than K=400 ring_mass at four of the five sigma values (all but sigma=0.02, where K=462 is slightly lower: 0.4425 vs 0.4588) — reported as a measured fact from the two CSVs, with no causal claim attached.
- `results/phase7_sigma_resweep_summary.md`'s "Interpretation" section is intentionally left as an owner-pending placeholder, matching 07-01's precedent and this plan's explicit non-goal.

**Ready for:** the owner's own interpretation pass on both Phase 7 results together (07-01's neighbor-locality mechanism test and this plan's sigma-confound check) — the roadmap's two Phase 7 experiments are now both complete.

**No blockers.** Full existing test suite (53/53) still passes; no existing file under `generator/` or `tests/` was modified by this plan.

---
*Phase: 07-mechanism-validation*
*Completed: 2026-07-29*
