---
phase: 18-hardness-under-loss-assessment
plan: 06
subsystem: hardness
tags: [perceval, photon-loss, tvd, anticoncentration, herald-failure, boson-sampling]

# Dependency graph
requires:
  - phase: 18-hardness-under-loss-assessment (Plans 18-02/18-03/18-04/18-05)
    provides: photonic_iqp_distribution_lossy, photonic_weight2_iqp_distribution_lossy, hardness/baselines.py, hardness/sweep.py::pooled_cell_for_neta, loss_sweep.py CLI, and the pre-commit timing probe's Final n-range decision
provides:
  - "results/phase18_weight1_loss_sweep.csv: real TVD-vs-eta and anticoncentration-alpha-vs-eta dataset, weight-1 scope, n=2..6, full 7-point ETA_GRID, n_draws=5"
  - "results/phase18_mixed_loss_sweep.csv: real TVD-vs-eta, alpha-vs-eta, and herald_failure_prob-vs-eta dataset, mixed weight-1+weight-2 scope, n=2..4 (CORE), full 7-point ETA_GRID, n_draws=5"
  - "Mixed n=5 stretch attempt: confirmed (third time, independently) as a reproducible, unfixable single-call MemoryError -- not attempted further"
affects: [18-07, 18-08, 19-verify-04]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Chunked-by-n synchronous CLI invocations (not one long-running process) for compute-heavy sweeps on this machine's memory-constrained hardware -- extends the draw-chunking pattern with a coarser per-n granularity."
    - "--eta-grid override used to resume a partially-completed n-cell after an external kill, targeting only the missing eta values rather than re-running or duplicating already-saved rows."

key-files:
  created:
    - results/phase18_weight1_loss_sweep.csv
    - results/phase18_mixed_loss_sweep.csv
  modified: []

key-decisions:
  - "Weight-1 CORE sweep run one n at a time via separate --append invocations (not a single synchronous call for all of n=2..6), per the timing probe's own recommendation, to bound per-process memory growth on this machine."
  - "When the n=6 background job was killed externally mid-sweep (5/7 eta cells already saved, no traceback/error in captured output), resumed with --eta-grid targeting only the 2 missing eta values rather than re-running the full n=6 cell -- avoids both wasted recompute and duplicate rows."
  - "Mixed n=5 stretch attempted once (single eta=0.99, not the full 7-point grid) since the timing probe already established this is a first-call MemoryError, not something more draws or more eta points would clarify. Reproduced the identical error at the identical call site (Simulator.probs_svd inside Processor.probs()) -- third independent confirmation of the same ceiling (2 from the timing probe, 1 here)."
  - "Deleted the header-only phase18_mixed_loss_sweep_stretch.csv (zero data rows, crashed before writing any) rather than leaving it on disk -- an empty CSV could be mistaken by a future glob/analysis script for a real (if empty) dataset. The outcome is documented here in prose instead, matching Phase 17's own precedent (\"no stretch CSV was ever produced\")."

patterns-established:
  - "For a confirmed single-call (not cross-call) memory ceiling: do not attempt draw-chunking as a workaround (it does not address per-call memory needs), and do not leave a zero-row output file as a stand-in for 'no result' -- report the outcome in the plan's own documentation instead."

# Metrics
duration: ~2h40min (weight-1 sweep ~1h50min incl. one external-kill recovery; mixed CORE sweep ~40min; stretch attempt ~1min)
completed: 2026-08-17
---

# Phase 18 Plan 06: Real Weight-1/Mixed Photon-Loss Sweep Summary

**Ran the phase's central compute-heavy measurement: real TVD-vs-eta and anticoncentration-alpha-vs-eta data for weight-1 (n=2..6, 35 rows) and mixed weight-1+weight-2 (n=2..4, 21 rows) generators across the full 7-point eta grid, with herald-failure-vs-eta tracked explicitly for mixed scope; confirmed mixed n=5 is a genuine, three-times-reproduced single-call memory ceiling that draw-chunking cannot fix.**

## Performance

- **Duration:** ~2h40min total wall time across both sweeps plus the stretch attempt
- **Started:** 2026-08-17 (session continuation from Plan 18-05)
- **Completed:** 2026-08-17
- **Tasks:** 2/2 completed
- **Files modified:** 2 created (both CSV artifacts)

## Accomplishments
- Weight-1 CORE loss sweep complete: `results/phase18_weight1_loss_sweep.csv`, 35 rows (n=2..6 x 7 eta), all quantities finite, `alpha_mean` visibly collapsing with loss at every n (e.g. n=6: 16.2 at eta=0.99 down to 4.5e-15 at eta=0.05) -- the Pitfall-2 sanity check the plan's must_haves require, confirmed passing.
- Mixed CORE loss sweep complete: `results/phase18_mixed_loss_sweep.csv`, 21 rows (n=2..4 x 7 eta), all quantities finite, `herald_failure_prob_mean` visibly rising with loss (n=4: 0.9259 at eta=0.99 -> 0.9991 at eta=0.05, never stuck at the lossless 2/27~=0.926 baseline) -- the compounding sanity check confirmed passing.
- Mixed n=5 stretch genuinely attempted (not skipped, not silently dropped) and its failure independently reconfirmed a third time, at the exact call site the timing probe identified.
- One real infrastructure event handled cleanly: the weight-1 n=6 background job was killed externally mid-run (not by this session); recovered by resuming only the missing eta cells via `--eta-grid`, with no data loss or duplication.

## Task Commits

Each task was committed atomically:

1. **Task 1: Run the weight-1 CORE loss sweep across the full eta grid** - `5369de9` (feat)
2. **Task 2: Run the mixed CORE loss sweep, then attempt the largest size best-effort with no time-box** - `351043f` (feat)

**Plan metadata:** (this commit)

## Files Created/Modified
- `results/phase18_weight1_loss_sweep.csv` - Weight-1 TVD-to-lossless/uniform/product-marginals and anticoncentration-alpha, n=2..6 x 7-point ETA_GRID, n_draws=5, 35 rows
- `results/phase18_mixed_loss_sweep.csv` - Mixed-scope TVD-to-lossless/uniform/product-marginals, anticoncentration-alpha, and herald_failure_prob/herald_success_rate, n=2..4 x 7-point ETA_GRID, n_draws=5, 21 rows

## Decisions Made
- Ran weight-1's n=2..6 as five separate `loss_sweep.py` invocations (one per n, appending), matching the timing probe's explicit recommendation to bound per-process memory growth rather than issue one ~1.5-2.5h synchronous call.
- On the n=6 external kill (5/7 eta cells already saved), resumed with `--eta-grid 0.35 0.05` rather than re-running the full n=6 cell from scratch -- correct because `loss_sweep.py`'s `run()` mode computes and appends independently per (n, eta) pair; targeting only the missing pair avoided ~11 minutes of redundant recompute and any risk of duplicate rows.
- Attempted the mixed n=5 stretch with a single eta value (0.99) rather than the full 7-point grid, since the timing probe already established the failure occurs on the very first `Processor.probs()` call of a fresh process -- additional eta points would not add diagnostic value, only additional wasted compute time on an already-confirmed ceiling.
- Deleted the resulting header-only stretch CSV (0 data rows) rather than leaving it on disk, to avoid a future script mistaking "file exists" for "data exists" -- the outcome is recorded here in prose instead, per this project's established honest-reporting convention (Phase 17 precedent: "no stretch CSV was ever produced" when a stretch attempt fails before any row is written).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Weight-1 n=6 background job killed externally mid-sweep, recovered via targeted eta resumption**
- **Found during:** Task 1 (weight-1 CORE sweep, n=6 cell)
- **Issue:** The n=6 sweep (estimated ~77 min for all 7 eta points) was launched via `run_in_background`. A task-notification reported the job's status as `"killed"` after only 5 of 7 eta cells completed (eta=0.99, 0.95, 0.9, 0.8, 0.6 all saved, finite, and eta-varying). The captured stdout showed clean per-cell progress output with no Python traceback, exception, or `MemoryError` before the job stopped -- ruling out a Perceval crash as the cause. Per this project's standing safety rule, no attempt was made to identify or inspect whatever terminated the process (it was not a process this session started and then investigated by pattern-matching); the termination is reported as observed, not diagnosed further.
- **Fix:** Resumed with a second invocation targeting only the two missing eta values (`--eta-grid 0.35 0.05`, `--append`), which completed cleanly (exit code 0) and produced the final 2 rows without re-running or duplicating the 5 already-saved n=6 rows.
- **Files modified:** `results/phase18_weight1_loss_sweep.csv` (no code changes -- this was an operational/infrastructure event, not a bug)
- **Verification:** Post-resumption, the full CSV was checked programmatically: 35 total rows, 0 non-finite values, all 5 n-values each have exactly 7 distinct eta rows.
- **Committed in:** `5369de9` (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking, operational -- no code changed)
**Impact on plan:** No scope creep, no code changes. The recovery mechanism used (`--eta-grid` targeting missing values) was already built into `loss_sweep.py` by Plan 18-05; this plan only exercised it under a real interruption rather than needing new code.

## Issues Encountered
- Mixed n=4's actual per-cell wall time (~194s) ran roughly 4.5x slower than the timing probe's measured 43.4s/cell, consistent with this machine's documented memory-pressure variability (free memory was ~2.5-4GB during this plan's execution vs. an unstated but presumably better condition during Plan 18-05's own timing probe run). The sweep still completed correctly (exit code 0, all values finite) -- this affected wall time only, not correctness.
- Mixed n=5's `MemoryError: bad allocation` reproduced identically to the timing probe's own finding (same call site: `perceval.simulators.simulator.Simulator.probs_svd`, called via `Processor.probs()`), now confirmed across three independent attempts (2 in the timing probe, 1 here) at different eta values and different free-memory conditions (~5.16GB in the probe, ~2.5GB here). This is conclusively a hard, non-transient ceiling for mixed-scope n=5 under the current `LC`-loss pipeline, not noise -- consistent with the timing probe's own conclusion and not a new finding, but independently reconfirmed rather than assumed to still hold.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness

**Ready for Plans 18-07/18-08:**
- `results/phase18_weight1_loss_sweep.csv` (35 rows) satisfies HARD-01/HARD-05's data-floor requirement in full -- weight-1 n=2..6, matching Phase 17's own established ceiling, across the complete eta grid, with both classically-easy baselines (uniform, product-of-marginals) and the BMS anticoncentration parameter tracked per cell.
- `results/phase18_mixed_loss_sweep.csv` (21 rows) satisfies HARD-07's data-floor requirement for CORE scope -- mixed n=2..4 across the complete eta grid, with `herald_failure_prob`/`herald_success_rate` tracked explicitly as a function of eta.
- Mixed n=5 remains genuinely unreachable on this hardware under the current pipeline (confirmed a third time, not merely repeated from the timing probe). Plans 18-07/18-08 should treat mixed scope's usable range as n=2..4 only and not expect n=5 data to arrive later in this milestone -- this is a hard ceiling, not a pending/in-progress item.
- No blockers for Plans 18-07/18-08 or Phase 19's VERIFY-04 cross-check -- both required datasets are complete, finite, and their respective sanity checks (alpha varying with eta; herald_failure_prob varying with eta) pass.

---
*Phase: 18-hardness-under-loss-assessment*
*Completed: 2026-08-17*
