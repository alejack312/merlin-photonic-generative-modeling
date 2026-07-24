---
phase: 04-generative-quality
plan: 01
subsystem: ml-evaluation
tags: [pytorch, merlin, mmd, quantum-generative-model, matplotlib, evaluation]

# Dependency graph
requires:
  - phase: 03-end-to-end-training-run
    provides: "results/phase3_checkpoint.pt (trained sigma=0.1 QuantumLayer state_dict), generator/train.py's build_generator/SIGMA convention"
provides:
  - "generator/visualize.py: sample_points(q, centers, n) and ring_band_metrics(mass, centers, center, radii, tol) — reusable, tested sampling/metric primitives"
  - "root visualize.py: entrypoint producing results/phase4_scatter_comparison.png and results/phase4_heatmap_comparison.png, printing ring/gap-band metrics for the sigma=0.1 checkpoint"
  - "Owner's explicit decision: sweep-needed — the full SIGMA_GRID sweep (Plan 04-02) is required before Plan 04-03's final GEN-07 checkpoint"
affects: [04-02-sigma-sweep, 04-03-final-verification]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Ring/gap-band quantitative metric (ring_mass/gap_mass) as a lightweight supporting signal alongside required visual/human judgment — not a replacement for it"
    - "Scatter-based heatmap rendering (not imshow) to avoid the verified x/y-flip pitfall from 04-RESEARCH.md"
    - "torch.multinomial-based sampling from an analytic probability vector q, distinct from the QuantumLayer's shots= forward path"

key-files:
  created:
    - generator/visualize.py
    - tests/test_visualize.py
    - visualize.py
  modified: []

key-decisions:
  - "Checkpoint decision (Task 3, blocking): sweep-needed — sigma=0.1's generated scatter/heatmap were diffuse/uniform, not ring-concentrated, despite ring_mass being well above random baseline. See 'Checkpoint Decision' section below for full reasoning."

patterns-established:
  - "Ring/gap metric computed both on the exact analytic q (primary, deterministic) and on a 400-sample multinomial draw (secondary cross-check) — both printed side by side for comparison."

# Metrics
duration: ~25min
completed: 2026-07-24
---

# Phase 4 Plan 1: Visualize sigma=0.1 checkpoint Summary

**Built reusable ring/gap-band evaluation primitives (`sample_points`, `ring_band_metrics`) and a comparison-plot entrypoint against Phase 3's trained sigma=0.1 checkpoint; owner reviewed the output and decided the full SIGMA_GRID sweep (Plan 04-02) is needed — sigma=0.1 alone does not yet show ring structure.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-07-24
- **Completed:** 2026-07-24
- **Tasks:** 3 (2 auto + 1 blocking checkpoint:decision)
- **Files modified:** 3 created (generator/visualize.py, tests/test_visualize.py, visualize.py) + 2 result artifacts (results/phase4_scatter_comparison.png, results/phase4_heatmap_comparison.png)

## Accomplishments
- `generator/visualize.py`'s `sample_points` (torch.multinomial-based draw from q) and `ring_band_metrics` (ring_mass/gap_mass against the empirically-verified circles geometry) implemented and independently tested — including a test proving the metric actually discriminates gap-hedging, not just returns 1.0 on p_real.
- Root `visualize.py` entrypoint loads `results/phase3_checkpoint.pt`, produces real-vs-generated scatter and heatmap comparison PNGs, and prints both exact-q and sampled-400 ring/gap metrics for the sigma=0.1 checkpoint.
- Full test suite (Phase 2 + Phase 3 + this plan) passes 32/32, no regressions.
- Owner reviewed the actual plots (not just the metric) and made the required explicit sufficient/sweep-needed decision per 04-CONTEXT.md's locked sequencing.

## Task Commits

Each task was committed atomically:

1. **Task 1: Implement generator/visualize.py's sampling and ring/gap metric functions, with tests** - `cacc3b2` (feat)
2. **Task 2: Build root visualize.py entrypoint — load sigma=0.1 checkpoint, produce comparison plots + metric** - `e4dc4ff` (feat)
3. **Task 3: checkpoint:decision** - no code commit (decision recorded below); a prior fix to test geometry / sample_points signature landed in `bd4bad6` before Task 1 was finalized.

**Plan metadata:** (this commit) `docs(04-01): complete visualize sigma=0.1 checkpoint plan`

## Files Created/Modified
- `generator/visualize.py` - `sample_points(q, centers, n)` (torch.multinomial draw), `ring_band_metrics(mass, centers, center, radii, tol)` (ring_mass/gap_mass against real-circles geometry, tol=0.04)
- `tests/test_visualize.py` - 4 tests: metric recovers p_real's known geometry exactly, metric discriminates gap-hedging on a synthetic gap-concentrated distribution, sampling shape/membership, sampling concentrates on high-probability bins
- `visualize.py` - root entrypoint: loads `results/phase3_checkpoint.pt`, builds `p_real`/`q`, renders scatter and heatmap comparisons, prints exact and sampled ring/gap metrics
- `results/phase4_scatter_comparison.png` - real (left) vs. generated-sampled (right) scatter, sigma=0.1
- `results/phase4_heatmap_comparison.png` - real p_real (left) vs. generated q (right) scatter-based heatmap, sigma=0.1

## Checkpoint Decision

**Decision: `sweep-needed`**

Reviewed, per the plan's checklist, in order:
1. `results/phase4_scatter_comparison.png` — the generated (right) panel's points are spread fairly uniformly across the whole square rather than concentrated on the two ring bands the real (left) panel shows.
2. `results/phase4_heatmap_comparison.png` — the generated heatmap is similarly diffuse rather than showing a clear annular high-probability band matching the real heatmap.
3. Printed ring/gap-band metric: `ring_mass=0.602` (exact q) / `0.572` (sampled 400), `gap_mass=0.034` (exact) / `0.030` (sampled) — well above a random/uniform baseline, but not concentrated enough to read as "ring-like" against the plots.

Both the executing agent and the orchestrator independently reviewed the two PNGs and reached the same read: not a blob, not entirely in the gap, but not yet a clean two-ring structure either — genuinely ambiguous by eye, which is exactly the case 04-CONTEXT.md's "MMD² can look numerically fine while the structure is wrong" caution anticipates. The owner reviewed both plots and the printed metric and confirmed: **sweep needed**.

**Consequence:** Plan 04-02 (full `SIGMA_GRID` sweep, ~12 minutes of additional training, all 5 sigma values at fixed epochs/lr/batch_size per 04-CONTEXT.md's locked strategy) must run before Plan 04-03's final GEN-07 human-verification checkpoint.

## Decisions Made
- Checkpoint decision: `sweep-needed` (see "Checkpoint Decision" above for full reasoning) — this is the plan's primary deliverable decision, not an implementation-detail decision.
- No other deviations from the plan's specified implementation of `sample_points`/`ring_band_metrics`/`visualize.py`.

## Deviations from Plan

None beyond the pre-existing `bd4bad6` fix (already committed prior to this plan's Task 1/2 execution, correcting gap-hedging test geometry and the `sample_points` signature in the plan's own frontmatter) — no new deviations during Task 1 or Task 2 execution.

## Issues Encountered

None. Both auto tasks executed and verified cleanly on the first pass; the checkpoint required genuine visual judgment (plots read as ambiguous/diffuse rather than clearly ring-like or clearly a blob), which is the expected, intended outcome of a non-automatable decision gate — not a problem to resolve, but the reason this checkpoint exists.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- `generator/visualize.py`'s `sample_points`/`ring_band_metrics` are ready to be reused unmodified by Plan 04-02 (sweep) and Plan 04-03 (final verification), per this plan's stated purpose.
- Plan 04-02 must run the full `SIGMA_GRID` sweep before Plan 04-03's final GEN-07 checkpoint — this plan's `sweep-needed` decision is the explicit gate that makes 04-02 required rather than optional.
- No blockers identified for starting Plan 04-02.

---
*Phase: 04-generative-quality*
*Completed: 2026-07-24*
