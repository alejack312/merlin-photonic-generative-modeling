---
phase: 18-hardness-under-loss-assessment
plan: 05
subsystem: hardness-assessment
tags: [numpy, perceval, hardness, tvd, anticoncentration, chunked-sweep, cli]

# Dependency graph
requires:
  - phase: "18-02"
    provides: "hardness/loss_model.py::photonic_iqp_distribution_lossy (weight-1 LC-loss primitive)"
  - phase: "18-03"
    provides: "hardness/loss_model_weight2.py::photonic_weight2_iqp_distribution_lossy (weight-2/mixed LC-loss + herald-compounding primitive)"
  - phase: "18-04"
    provides: "hardness/baselines.py: uniform_baseline, product_of_marginals_baseline, anticoncentration_alpha"
provides:
  - "hardness/sweep.py: pooled_cell_for_neta(n, eta, scope, draw_start, draw_count) -- per-cell TVD/anticoncentration/herald-failure integration, composing 18-02/18-03/18-04"
  - "hardness/sweep.py: combine_pooled_cells(raw_arrays, scope) -- draw-chunk re-summarization"
  - "hardness/sweep.py: ETA_GRID (7-point, shared weight1/mixed grid)"
  - "loss_sweep.py: root-level CLI, chunked/resumable per Phase 17/17.1 convention"
  - "results/phase18_timing_probe.md: real measured per-cell timings at weight1 n=6 and mixed n=4/n=5, with an explicit Final n-range decision for Plan 18-06"
affects: ["18-06 (real sweep execution -- consumes loss_sweep.py + the timing probe's n-range decision directly)", "18-07/18-08 (analysis/write-up stages)"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "hardness.sweep reuses trainability.rng.get_rng verbatim (cross-package reuse of a generic utility, not trainability-specific logic) for deterministic per-draw theta seeding"
    - "Raw-array-now-summarize-later chunking contract (mirrors trainability/sweep.py::pooled_gradients_for_cell): pooled_cell_for_neta returns (summary, raw); raw is a 2D array (draws x quantities) saved to .npy per chunk, concatenated and re-summarized once by combine_pooled_cells"
    - "loss_sweep.py's draw-chunk mode loops over the WHOLE eta grid in one process invocation (not a third chunking dimension) -- weight-2's expense is per-cell-per-eta, so draw-range chunking amortizes across the eta grid instead"

key-files:
  created:
    - hardness/sweep.py
    - loss_sweep.py
    - results/phase18_timing_probe.md
  modified: []

key-decisions:
  - "sample_thetas draws uniform(0, 2*pi) -- this phase's own generic 'uniform' init convention (Phase 17's clean-signal regime), stated explicitly as Claude's Discretion per 18-CONTEXT.md, not silently inherited."
  - "Product-of-marginals baseline computed once per draw from that draw's own lossless (eta=1.0) reference, inside the per-draw loop before the eta computation -- matches 18-CONTEXT.md's explicit lock."
  - "Weight-1 n=7 stretch explicitly skipped (not attempted) -- the plan's own stretch condition ('if [n=6] is fast, also try n=7') does not hold given n=6's measured ~133s/cell."
  - "Mixed n=5 downgraded from a sizing candidate to an optional, likely-to-fail best-effort stretch probe, not a CORE requirement -- confirmed via 2 independent attempts to hit a reproducible single-call MemoryError (not a slow-but-completing case), which draw-chunking cannot fix."

patterns-established:
  - "Pre-commit timing probes for compute-heavy sweeps: measure real single-cell wall time via the CLI's own chunk mode before locking a plan's n-range, and record an explicit, unambiguous decision file the next plan reads and follows without further judgment calls."

# Metrics
duration: ~55min
completed: 2026-08-17
---

# Phase 18 Plan 05: Loss-Sweep Integration Layer & Timing Probe Summary

**`hardness/sweep.py` (per-cell TVD/anticoncentration/herald-failure integration) and `loss_sweep.py` (chunked/resumable CLI) wired together and verified end-to-end; a real machine-measured timing probe found weight-1 n=6 costs ~1900x more than n=4's extrapolated figure and mixed n=5 hits a reproducible, unfixable single-call `MemoryError` -- both facts now locked into `results/phase18_timing_probe.md`'s Final n-range decision for Plan 18-06.**

## Performance

- **Duration:** ~55 min (implementation + verification: ~15 min; timing probe execution/monitoring: ~35 min of real wall-clock compute; write-up: ~5 min)
- **Completed:** 2026-08-17
- **Tasks:** 3/3
- **Files modified:** 3 (all new)

## Accomplishments
- `hardness/sweep.py::pooled_cell_for_neta` composes Plans 18-02/18-03/18-04's primitives into one per-cell integration function, correctly implementing the "product-of-marginals computed once per draw" rule and reusing `trainability.rng.get_rng` verbatim for deterministic draw seeding.
- `loss_sweep.py` matches `gradient_variance_sweep.py`'s established CLI shape (`--draw-start`/`--draw-count`/`--combine-chunks`), verified end-to-end: a direct run and a chunked-then-combined run over the same draw range produced bit-identical summary statistics.
- A real, machine-measured timing probe (not extrapolated) answered `18-RESEARCH.md`'s Open Question 2 for both scopes: weight-1 n=6 (~133s/cell, all 7 eta points) and mixed n=4 (~43.4s/cell, all 7 eta points) are both feasible but far more expensive than the research note's optimistic n<=4 reading suggested; mixed n=5 reproducibly fails with a `MemoryError` on the very first call (confirmed twice, different eta values, ~5.16GB free memory both times).

## Task Commits

Each task was committed atomically:

1. **Task 1: Build hardness/sweep.py -- per-cell integration over draws** - `36d5784` (feat)
2. **Task 2: Build loss_sweep.py CLI with chunked/resumable execution** - `6e701d9` (feat)
3. **Task 3: Timing probe -- measure real per-cell cost before Plan 18-06 commits compute budget** - `9eb3e7b` (docs)

_No TDD tasks in this plan (integration/CLI/measurement, `type="auto"`, no `tdd="true"` attribute)._

## Files Created/Modified
- `hardness/sweep.py` - `sample_thetas`, `pooled_cell_for_neta`, `combine_pooled_cells`, `ETA_GRID` (7-point, shared weight1/mixed grid, denser near eta=1)
- `loss_sweep.py` - Root-level CLI (`run`, `run_chunk`, `combine_chunks`), mirroring `gradient_variance_sweep.py`'s flag shape and flush-after-every-row discipline
- `results/phase18_timing_probe.md` - Real measured timings at weight1 n=6 and mixed n=4/n=5, plus an explicit "Final n-range decision" section

## Decisions Made
- `sample_thetas` uses uniform-over-`[0, 2*pi)` sampling as this phase's own generic init convention -- documented in the module docstring as a deliberate scope choice (Claude's Discretion per `18-CONTEXT.md`), not silently inherited from Phase 17's multi-scheme design (this phase has no init-scheme axis at all).
- Draw-chunk mode in `loss_sweep.py` loops over the *entire* eta grid within one process invocation, rather than adding eta as a third chunking dimension alongside `n` and draw-range -- since weight-2's cost is per-cell-*per-eta*, this amortizes process-startup/import overhead across the whole eta grid for a given draw sub-range.
- Weight-1 n=7 was explicitly *not* attempted as a stretch probe: the plan's own stated condition ("if [n=6] is fast, also try n=7") does not hold given n=6's measured ~133s/cell, so skipping was a reasoned application of the plan's own logic, not an omission.
- Mixed n=5 is recorded as an optional, likely-to-fail best-effort stretch point (not CORE) for Plan 18-06, with an explicit note that Phase 17's own draw-chunking mitigation cannot fix this specific failure mode (a single-call ceiling, not a cross-call leak) -- stated plainly so Plan 18-06 doesn't waste time debugging a repeat `MemoryError` as if it were a new bug.

## Deviations from Plan

None — plan executed exactly as written. The timing probe's results (weight-1 n=6 being far more expensive than expected, mixed n=5 being outright infeasible) are measurement *findings*, not deviations from what the plan asked for — Task 3 explicitly anticipated an unfavorable outcome was possible ("if mixed n=5's measured single-cell time makes a full sweep... infeasible... record the honest tradeoff") and this plan followed that instruction.

## Issues Encountered

**Weight-1's real n=6 cost was a genuine surprise relative to `18-RESEARCH.md`'s sizing note**, which measured weight-1 as "trivial" (0.07s/cell) at n=4 and predicted tractability "likely beyond" n=6 on that basis (`3^n` output-state growth argument). The real n=6 number (~133s/cell mean) is ~1900x the n=4 figure over 2 n-steps (~43x per n-step) -- i.e. wall-time growth is NOT flat relative to the `3^n` state-count growth the research note's n<=4 data suggested. This was resolved by simply reporting the real number and its implications honestly in `results/phase18_timing_probe.md`, per this project's established honesty-over-narrative convention (Phase 7/17/17.1 precedent) -- not smoothed over or treated as an error to fix.

**Mixed n=5 hit a reproducible `MemoryError` on the very first `Processor.probs()` call**, in a fresh process with ~5.16GB free memory (confirmed on 2 independent attempts, different eta values). This is mechanically distinct from Phase 17's own mixed-n=5 `MemoryError` (a cross-call leak across ~600 repeated calls within one process, fixed by draw-chunking) -- here the failure occurs inside a single draw's single call, before any result is produced, so `loss_sweep.py`'s own chunking mechanism cannot rescue it. Documented explicitly in `results/phase18_timing_probe.md` so Plan 18-06 doesn't attempt to "fix" this with more chunking.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- `hardness/sweep.py` and `loss_sweep.py` are the complete, tested integration layer + CLI Plan 18-06 needs to run the real sweep -- no further infrastructure work required before that plan starts.
- `results/phase18_timing_probe.md`'s Final n-range decision is unambiguous and ready for Plan 18-06 to follow directly: weight-1 CORE `n=2..6` (chunked/resumable, one n at a time, ~1.5-2.5h estimated total), mixed CORE `n=2..4` (~25min estimated), mixed n=5 as an optional best-effort stretch attempt only (not CORE, not expected to succeed).
- 266/266 full repo test suite passes, zero regressions (no new tests added in this plan -- integration/CLI/measurement work, not new primitive logic requiring its own unit tests; Plans 18-02/18-03/18-04's existing test suites already cover the primitives this plan composes).

---
*Phase: 18-hardness-under-loss-assessment*
*Completed: 2026-08-17*
