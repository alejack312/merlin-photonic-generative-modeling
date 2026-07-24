---
phase: 04-generative-quality
plan: 02
subsystem: ml-evaluation
tags: [pytorch, merlin, mmd, quantum-generative-model, matplotlib, hyperparameter-sweep]

# Dependency graph
requires:
  - phase: 04-generative-quality
    plan: 01
    provides: "generator/visualize.py's sample_points/ring_band_metrics primitives; owner's sweep-needed checkpoint decision that made this plan required"
provides:
  - "sweep.py: resumable entrypoint retraining a fresh generator per SIGMA_GRID value ([0.02, 0.05, 0.1, 0.2, 0.4]), reusing generator/train.py unmodified"
  - "results/phase4_sigma_<v>_checkpoint.pt for all 5 sigma values"
  - "results/phase4_sweep_metrics.csv -- per-sigma ring_mass/gap_mass"
  - "results/phase4_sweep_comparison.png -- one combined figure, real data + all 5 generated distributions, for Plan 04-03's single combined visual review"
affects: [04-03-final-verification]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Resumable sweep script: skip retraining a sigma whose checkpoint already exists on disk, recompute only its metrics -- makes a multi-minute sweep robust to an interrupted background process without redoing already-finished, already-fresh-QuantumLayer work"

key-files:
  created:
    - sweep.py
  modified: []

key-decisions:
  - "Made sweep.py resumable (checkpoint-exists => skip retrain, recompute metrics only) after the initial background run died silently partway through (after sigma=0.2, before sigma=0.4) -- Rule 3 (blocking issue) auto-fix, not a plan deviation in outcome: all 5 checkpoints are still each the product of one full fresh-QuantumLayer training run, just not all produced by a single uninterrupted script execution."

patterns-established:
  - "Long-running (~12+ min) training scripts should not be launched via a single backgrounded shell call in this environment -- background bash jobs did not reliably survive across tool-call turns and the process died with no error output. Prefer: keep training loops short enough to run in the foreground within a tool timeout, or make any backgrounded script resumable/checkpoint-per-unit-of-work so a silent kill is recoverable rather than requiring a full redo."

# Metrics
duration: ~46min (includes an unplanned ~28min gap while a killed background process went undetected before being caught and restarted)
completed: 2026-07-25
---

# Phase 4 Plan 2: SIGMA_GRID Sweep Summary

**Retrained the generator from scratch at all 5 `SIGMA_GRID` values (epochs/lr/batch_size fixed at Phase 3's 300/0.01/32), producing 5 checkpoints, a per-sigma ring/gap metrics CSV, and one combined 6-panel comparison figure -- none of the 5 sigma values show a visually ring-like generated distribution, all read as diffuse across the whole square, same character as Plan 04-01's sigma=0.1-alone finding.**

## Performance

- **Duration:** ~46 min wall-clock (2026-07-25T00:00Z start ~2026-07-24T21:32Z, completed ~2026-07-24T22:18Z UTC-equivalent local 23:32-00:18) -- includes a ~28 min unplanned gap while a killed background training process went undetected (see Issues Encountered)
- **Tasks:** 2 (both auto)
- **Files modified:** 1 created (sweep.py) + 7 result artifacts (5 checkpoints, 1 CSV, 1 PNG)

## Accomplishments
- `sweep.py` retrains a fresh `QuantumLayer` (via `generator/train.py`'s unmodified `build_generator`/`train_step`) at each of the 5 `SIGMA_GRID` values, isolating sigma as the only variable under test.
- All 5 checkpoints (`results/phase4_sigma_{0.02,0.05,0.1,0.2,0.4}_checkpoint.pt`) exist and are non-empty; `results/phase3_checkpoint.pt` was never touched (verified: unchanged mtime/size before and after).
- `results/phase4_sweep_metrics.csv` records one ring_mass/gap_mass row per sigma.
- `results/phase4_sweep_comparison.png` shows the real circles data plus all 5 generated scatters in one figure, for Plan 04-03's single combined review (per 04-CONTEXT.md's locked process -- not reviewed one sigma at a time).
- Full test suite still passes 32/32 -- no regressions from this plan's changes.

## Task Commits

Each task was committed atomically:

1. **Task 1: Sweep all 5 SIGMA_GRID values, save per-sigma checkpoints and metrics** - `f82c8ec` (feat)
2. **Task 2: Build the combined sweep comparison figure for a single visual review** - `5625cac` (feat)

**Plan metadata:** (this commit) `docs(04-02): complete SIGMA_GRID sweep plan`

## Files Created/Modified
- `sweep.py` - resumable entrypoint: loops `SIGMA_GRID`, retrains a fresh generator per sigma (skipping retrain if that sigma's checkpoint already exists on disk), saves per-sigma checkpoints + metrics CSV + combined comparison figure
- `results/phase4_sigma_0.02_checkpoint.pt`, `..._0.05_...`, `..._0.1_...`, `..._0.2_...`, `..._0.4_...` - trained `QuantumLayer` state dicts, one per sigma
- `results/phase4_sweep_metrics.csv` - per-sigma ring_mass/gap_mass:

  | sigma | ring_mass | gap_mass |
  |-------|-----------|----------|
  | 0.02  | 0.4588    | 0.0100   |
  | 0.05  | 0.4843    | 0.0341   |
  | 0.1   | 0.6161    | 0.0346   |
  | 0.2   | 0.5440    | 0.0478   |
  | 0.4   | 0.3277    | 0.0224   |

- `results/phase4_sweep_comparison.png` - 6-panel figure: real data + all 5 sigma-trained generated scatters

## Decisions Made
- Made `sweep.py` resumable (Rule 3 - Blocking auto-fix, see Deviations below) so an interrupted sweep does not require redoing already-finished sigmas.
- No decisions requiring owner input in this plan -- the combined visual review and any resulting decision belongs to Plan 04-03, not this plan.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Made sweep.py resumable after the backgrounded training process died silently**
- **Found during:** Task 1 (sweep execution) -- the coordinator flagged that no new files had appeared in ~28 minutes and no `venv` python process was running, after the first background run had completed sigma=0.02/0.05/0.1/0.2 (checkpoints written 23:36-23:43) but not sigma=0.4, and had not reached the CSV/figure step.
- **Issue:** A ~12-14 min training script launched via a single backgrounded `Bash` call did not survive across tool-call turns in this environment -- it was killed with no error output captured, well before finishing. This is an execution-environment issue, not a bug in the training code itself (the 4 completed checkpoints were valid, fully-trained results).
- **Fix:** Added a resumability check to `sweep.py`'s `train_all_sigmas`: if a sigma's checkpoint file already exists on disk, skip retraining it and just reload the checkpoint to recompute its metrics row (rather than blindly retraining all 5 from zero, which would have discarded 4 already-valid results and cost ~10 extra minutes). Reran the script in the foreground this time (not backgrounded), so only sigma=0.4's ~140s training plus the fast aggregation step needed to complete, which finished cleanly within the tool's timeout.
- **Files modified:** sweep.py
- **Verification:** All 5 checkpoints present and non-empty; `results/phase4_sweep_metrics.csv` has exactly 5 rows with finite, sensible ring_mass/gap_mass values; `results/phase4_sweep_comparison.png` shows all 6 panels; full test suite still 32/32; `results/phase3_checkpoint.pt` mtime/size unchanged.
- **Committed in:** `f82c8ec` (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** The fix is purely about *how* the sweep was executed (resumable vs. one-shot), not what it produced -- all 5 checkpoints are each the output of one full, fresh-`QuantumLayer`, unmodified `train_step` run, satisfying the plan's must-have truths exactly as written. No scope creep; no change to `generator/train.py`, `generator/mmd.py`, or `generator/visualize.py`.

## Issues Encountered

- The first `sweep.py` run was launched via a backgrounded `Bash` call (`run_in_background: true`). It progressed through 4 of 5 sigmas (checkpoints for 0.02/0.05/0.1/0.2 written 23:36-23:43) and then went silent -- no further file writes, no captured stdout/stderr in the background task's output file (which contained no training print output at all, even for the sigmas that did complete, suggesting stdout buffering when redirected rather than a crash mid-write). By the time the coordinator's status check ran (~28 min later), no `venv` python process was alive. Root cause: this environment's backgrounded bash jobs do not reliably survive across tool-call turns for multi-minute processes -- the process was killed externally, not by an error in the training code. Resolved by making the script resumable and rerunning the remaining work (sigma=0.4 + aggregation, well under a single foreground timeout) directly in the foreground so the agent could supervise it to completion. See "patterns-established" in frontmatter for the operational lesson.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- All 5 `SIGMA_GRID` checkpoints, the per-sigma metrics CSV, and the combined comparison figure are ready for Plan 04-03's final GEN-07 human-verification checkpoint.
- **Observation for Plan 04-03 (not a decision made here):** visually, `results/phase4_sweep_comparison.png` shows all 5 generated panels as diffuse scatter across the full `[-0.1, 1.1]^2` square -- none present as a clean two-ring structure, sigma=0.1 has the highest ring_mass (0.6161) of the 5 but is still visually diffuse, consistent with Plan 04-01's sigma=0.1-alone finding. This combined evidence is what Plan 04-03's checkpoint will need to weigh.
- No blockers identified for starting Plan 04-03.

---
*Phase: 04-generative-quality*
*Completed: 2026-07-25*
