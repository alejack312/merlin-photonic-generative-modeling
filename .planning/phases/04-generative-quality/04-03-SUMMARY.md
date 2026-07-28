---
phase: 04-generative-quality
plan: 03
subsystem: ml-evaluation
tags: [mmd, quantum-generative-model, evaluation, checkpoint]

# Dependency graph
requires:
  - phase: 04-01-visualize-sigma-checkpoint
    provides: "sample_points/ring_band_metrics, sigma=0.1 cheap-check evidence"
  - phase: 04-02-sigma-sweep
    provides: "full SIGMA_GRID sweep evidence"
provides:
  - "results/phase4_summary.md: aggregated evidence across all three Phase 4 tuning axes (sigma sweep, batch sweep, natural-order correspondence)"
  - "GEN-07 final status: NOT MET, owner-confirmed"
affects: [05-benchmarking]

key-files:
  created:
    - results/phase4_summary.md
  modified: []

key-decisions:
  - "GEN-07 checkpoint: NOT MET. Owner's verbatim response: 'GEN-07 not met, move to Phase 5.' Best available result (natural-order correspondence, ring_mass=0.691) is a real, mechanistically-verified improvement over the documented baseline (ring_mass=0.609) but does not recognizably form two distinct rings."

# Metrics
duration: ~10min (checkpoint response only — evidence aggregation and all three tuning axes were completed across prior sessions/turns)
completed: 2026-07-25
---

# Phase 4 Plan 3: Document tuning path, human-verify checkpoint confirming GEN-07 Summary

**Aggregated all three Phase 4 tuning axes (SIGMA_GRID sweep, ad hoc batch-size sweep, ad hoc natural-order spatial correspondence fix) into `results/phase4_summary.md`; owner reviewed the combined evidence and confirmed GEN-07 is not met.**

## Performance

- **Completed:** 2026-07-25
- **Tasks:** 2 (1 auto — write summary; 1 blocking checkpoint:human-verify)
- **Files modified:** 1 created (`results/phase4_summary.md`)

## Accomplishments

- `results/phase4_summary.md` documents the actual path taken across three tuning axes (not just the two the original plan anticipated — an ad hoc "option 3" natural-width/spatial-correspondence axis was added after 04-01/04-02 both failed to produce ring-like output), the real ring_mass/gap_mass values for every variant tried, and the mechanism behind option 3's improvement.
- Owner reviewed the full evidence set (all comparison PNGs, the rank-domain profile, and the metric table) across this thread and gave the required human-verification response.

## Checkpoint Decision

**GEN-07: NOT MET.**

Owner's verbatim response: **"GEN-07 not met, move to Phase 5."**

This follows an extended review across this session: the owner first characterized the natural-order result as "quite an improvement. Still not two distinct rings, but an improvement," then walked through the mechanism behind that improvement (radius-sorting collapsing the ring target from ~44 disjoint raster fragments into ~2 contiguous radius-sorted bands) via a Feynman-technique explanation to confirm real understanding, then asked a clarifying comparison against MerLin's own quickstart classifier (which turned out to be a weak baseline itself — 46-64% test accuracy across repeated runs on an easily-separable dataset, not a strong reference point) before giving the final checkpoint verdict.

Per PROJECT.md's "don't gloss over it" rule and 04-CONTEXT.md's explicit deferral on how to phrase a "not met" outcome: the honest final status is that **no axis tried across all of Phase 4 (sigma, batch size, or the structural output-correspondence fix) produced a generated distribution a human would call two clean, distinct rings.** The best available result (natural-order correspondence: ring_mass=0.691, gap_mass=0.048, K=462) is real, reproducible, and mechanistically understood — but it is a partial improvement, not resolution.

## Decisions Made

- GEN-07 marked **not met**, per explicit owner confirmation — this is the plan's required outcome, valid per 04-CONTEXT.md/PROJECT.md as an honest non-met result, not a failure of process.
- Proceeding to Phase 5 (Benchmarking) with this honestly-documented partial result as Phase 4's final state, per the owner's explicit instruction.

## Deviations from Plan

- The original 04-03-PLAN.md anticipated aggregating evidence from only two axes (04-01's cheap check, 04-02's sigma sweep). Two additional ad hoc axes (batch-size sweep, natural-order correspondence) were run between 04-02 and this checkpoint, at the owner's direction, before the GEN-07 checkpoint was actually taken. `results/phase4_summary.md` was written to cover all three axes, not just the two originally scoped — this is a superset of the plan's requirement, not a shortfall.

## Issues Encountered

None. The checkpoint required genuine visual/conceptual judgment from the owner across an extended discussion (mechanism explanation, Feynman-technique re-explanation, comparison against the quickstart classifier) — this is the intended, non-automatable purpose of this gate, not a problem.

## Next Phase Readiness

- Phase 4 is closed with GEN-07 **not met**, honestly documented in `results/phase4_summary.md`, `DESIGN_DECISIONS.md`, and `.planning/STATE.md`.
- Phase 5 (Benchmarking, requirements BMK-01/BMK-02) begins against the natural-order generator as the best available (though imperfect) trained model. Phase 5's honest benchmarking write-up should carry forward the GEN-07-not-met context — the benchmark is being run against a generator that does not yet recognizably reproduce the target shape, and that should be stated plainly rather than implied otherwise.
- No blockers identified for starting Phase 5.

---
*Phase: 04-generative-quality*
*Completed: 2026-07-25*
