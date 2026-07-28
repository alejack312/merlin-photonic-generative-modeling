---
phase: 05-benchmarking
plan: 01
subsystem: testing
tags: [mmd, benchmarking, pytorch, merlin, quantumlayer, evaluation]

# Dependency graph
requires:
  - phase: 04-generative-quality
    provides: "phase4_natural_checkpoint.pt (K=462, natural-order generator, GEN-07 not met, ring_mass=0.691/gap_mass=0.048), NaturallyOrderedGenerator/natural_sorted_centers, ring_band_metrics"
provides:
  - "benchmark.py: held-out MMD^2 (trained vs untrained vs real-vs-real floor), mean±std over 20 latent draws"
  - "benchmark_timing.py: measured wall-clock training time (425.93s) and parameter count (220) via a fresh timed retrain to a scratch checkpoint"
  - "results/phase5_benchmark_metrics.csv, results/phase5_training_cost.csv: raw numeric results"
  - "results/phase5_summary.md: citation-ready BMK-01/BMK-02 write-up for Phase 6"
affects: [06-documentation-case-study]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Post-hoc benchmark script pattern: load frozen checkpoint, .eval() + torch.no_grad(), no optimizer/backward pass, mean±std over repeat latent draws"
    - "Timed-retrain-to-scratch-checkpoint pattern: never overwrite a documented reference checkpoint when only wall-clock/param-count instrumentation is needed"

key-files:
  created: [benchmark.py, benchmark_timing.py, results/phase5_benchmark_metrics.csv, results/phase5_training_cost.csv, results/phase5_summary.md]
  modified: []

key-decisions:
  - "SIGMA=0.1 kept identical to Phase 4's training bandwidth for direct comparability with all Phase 4 numbers, not re-tuned for the benchmark."
  - "Held-out split reused unchanged from generator/data.py's load_circles_data() (fixed random_state=42 80/20 split) rather than re-splitting with multiple seeds — p_real/p_real_test are deterministic once the split is fixed, so the only source of run-to-run variance is the latent z, which is what N_DRAWS=20 already captures."
  - "benchmark_timing.py writes to a scratch checkpoint (results/phase5_timed_checkpoint.pt), never to results/phase4_natural_checkpoint.pt, to avoid corrupting the Phase 4 reference artifact while still getting a real measured wall-clock number."
  - "BMK-02 fallback path (qualitative comparison, no matched numeric metric) confirmed and used, per 05-RESEARCH.md's pre-execution research finding that MerLin's photonic QGAN reproduction trains on a different data domain (8x8 digit images vs. 2D point-cloud circles) with no defined mapping onto this project's MMD metric space."

patterns-established:
  - "Pattern: benchmark scripts are post-hoc-only (no training), reuse generator/data.py + generator/mmd.py + generator/naturally_ordered_generator.py + generator/visualize.py unchanged, write plain CSVs to results/, and a phase-level *_summary.md aggregates numbers for reuse by later phases."

# Metrics
duration: ~25min
completed: 2026-07-29
---

# Phase 5 Plan 01: Benchmarking Summary

**Held-out MMD² benchmark (trained=0.0125±0.0003 vs untrained=0.0360±0.0048 vs real-vs-real floor=0.0114) plus measured training cost (425.93s wall-clock, 220 params), with a qualitative BMK-02 fallback comparison against MerLin's photonic QGAN reproduction explicitly flagged as non-matched.**

## Performance

- **Duration:** ~25 min (dominated by a ~7 min fresh timed retrain in Task 2)
- **Started:** 2026-07-29
- **Completed:** 2026-07-29
- **Tasks:** 3/3
- **Files modified:** 5 new files (benchmark.py, benchmark_timing.py, 3 results/ files)

## Accomplishments
- BMK-01 met: held-out MMD² statistic computed (mean±std, N=20 draws) for the trained generator, bracketed by an untrained-parameter baseline (shows training helped, ~3x lower MMD²) and a real-train-vs-real-test floor (shows the trained generator is close to "as good as real data" by this metric — only ~0.0011 above the floor).
- Training cost measured for the first time in this repo: 425.93s wall-clock (300 epochs, batch=32), 220 parameters, via a fresh timed retrain to a scratch checkpoint that never touched the Phase 4 reference checkpoint.
- BMK-02 documented via the pre-confirmed qualitative fallback path (05-RESEARCH.md had already established the QGAN reproduction trains on a different data domain), explicitly flagged as "Fallback path used — no matched numeric comparison was computed," with a qualitative comparison table and the reproduction's own reported SSIM=0.570575 cited with its Adam/SPSA caveat.
- Phase 4's GEN-07-not-met framing carried forward honestly: ring_mass=0.6833±0.0073 and gap_mass=0.0514±0.0035 re-measured and reported alongside the MMD² statistic, with an explicit statement that a good MMD² number does not by itself imply clean ring structure.

## Task Commits

Each task was committed atomically:

1. **Task 1: benchmark.py — held-out MMD² with untrained and floor baselines** - `99dd94d` (feat)
2. **Task 2: benchmark_timing.py — timed retrain for wall-clock and parameter count** - `dfcd2c0` (feat)
3. **Task 3: results/phase5_summary.md — citation-ready BMK-01 + BMK-02 write-up** - `07d4f93` (docs)

## Files Created/Modified
- `benchmark.py` - post-hoc, no-training script: held-out MMD² (trained/untrained/floor) + ring/gap metrics, mean±std over 20 latent draws
- `benchmark_timing.py` - fresh 300-epoch timed retrain to a scratch checkpoint; measures wall-clock time and parameter count; sanity-checks final ring/gap against Phase 4's documented values
- `results/phase5_benchmark_metrics.csv` - trained/untrained/floor MMD² and ring/gap numbers
- `results/phase5_training_cost.csv` - wall_clock_seconds, param_count, epochs, batch_size, final ring_mass/gap_mass
- `results/phase5_summary.md` - citation-ready BMK-01 + BMK-02 write-up for Phase 6

## Decisions Made
- SIGMA=0.1 kept identical to training (not re-tuned) for direct comparability with every Phase 4 number.
- Held-out split reused unchanged (`load_circles_data()`'s fixed `random_state=42` split) rather than varying the split across seeds — the only intended source of run-to-run variance is the latent `z`.
- `benchmark_timing.py` writes to a scratch checkpoint path, never overwriting `results/phase4_natural_checkpoint.pt`.
- BMK-02's qualitative fallback path used per 05-RESEARCH.md's pre-execution finding (confirmed again during writing the summary): the QGAN reproduction's image-pixel output space has no defined mapping onto this project's K=462 2D bin-center MMD metric without inventing new BMK-03-scoped work.

## Deviations from Plan

None - plan executed exactly as written. The plan's own anomaly-check ("if trained MMD² mean is not lower than untrained, report it, don't silently fix") did not trigger — trained MMD² (0.0125) was clearly lower than untrained (0.0360) on the first run.

## Issues Encountered
- The repo-root `python` was not the project's venv (`ModuleNotFoundError: No module named 'merlin'` on the first run of `benchmark.py`) — resolved by invoking `./venv/Scripts/python.exe` directly, consistent with this repo's existing venv setup (no CLAUDE.md update needed, this is an environment-invocation detail, not a repo convention change).
- `benchmark_timing.py`'s fresh retrain took ~7 minutes (425.93s), longer than a single 120s foreground command allows in this environment — ran via `run_in_background: true` and polled the output file until epoch-300/param-count lines appeared, consistent with 05-RESEARCH.md's noted precedent (Phase 4's sweep scripts) of long-running scripts needing backgrounding/resumability in this environment.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- `results/phase5_summary.md` is ready to be pulled into Phase 6's README, technical note, and case study with minimal rework — headline numbers up top, BMK-01/BMK-02 both documented, Phase 4's honest "not met" framing carried forward without being implied away.
- All existing tests still pass (48 passed) — no changes made to `generator/` in this plan.
- No blockers for Phase 6.

---
*Phase: 05-benchmarking*
*Completed: 2026-07-29*
