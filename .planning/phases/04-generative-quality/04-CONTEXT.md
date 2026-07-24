# Phase 4: Generative Quality - Context

**Gathered:** 2026-07-24
**Status:** Ready for planning

<domain>
## Phase Boundary

The trained generator's samples (starting from Phase 3's `results/phase3_checkpoint.pt`) are recognizable to a human as approximating the circles dataset's two-ring shape — not just a decreasing loss number. Any hyperparameter tuning needed to reach recognizable output is documented. Does not include quantitative benchmarking against a reference point (Phase 5) or any documentation/publication packaging (Phase 6).

</domain>

<decisions>
## Implementation Decisions

### Sample visualization method
- Both a probability-weighted heatmap/density plot over the 400 bin-centers (exact learned mass, no sampling noise) AND a scatter of points drawn from `q` as a categorical distribution (intuitive, directly comparable to the real circles scatter) — not just one or the other.
- Sampled scatter: draw 400 points, matching the real dataset's `n_samples=400`, so generated and real scatters are density-comparable at a glance.
- Layout: side-by-side subplots (real data | generated data) in the same figure, not overlaid on one set of axes.
- Style: standard matplotlib, functional not polished — same register as Phase 3's loss-curve plot. No specific external reference requested.

### Sigma sweep / retraining strategy
- Start by visualizing Phase 3's existing sigma=0.1 checkpoint first (cheap check) before deciding whether any retraining is needed at all.
- If retraining turns out to be needed: run the **full** `SIGMA_GRID = [0.02, 0.05, 0.1, 0.2, 0.4]` (all 5 values, not just a bracket around 0.1) — carries forward Phase 2's deferred "evaluate the sweep against real ring recovery" item and the prior IQP-MMD project's `AC12 Bandwidth Sweep` lesson (MMD² can look fine numerically while the learned distribution is structurally wrong).
- Keep `epochs`/`lr`/`batch_size` fixed at Phase 3's values (300/0.01/32) while sweeping sigma — isolates sigma as the one variable under test. Increasing epochs is an explicit escape hatch (see Tuning budget below) only if 300 epochs looks undertrained, not a routine knob to also sweep.
- Process: if a sweep is run, execute all planned retrains first, then review all resulting plots together for one combined visual judgment — not an interactive one-at-a-time loop.

### Success judgment method
- Visual judgment (the owner looks at the actual plot) **plus** a lightweight supporting quantitative metric — not eyeball-only, and explicitly not a full Phase-5-style benchmark.
- The metric should be designed with an eye toward reuse in Phase 5 (e.g. something like % of sampled points landing within a ring-band tolerance vs. the empty gap, informed by Phase 2's known geometry — radii 0.4/0.5, ring gap 0.1) rather than disposable Phase-4-only scaffolding. Exact formula/threshold is Claude's discretion at planning/implementation time.
- Final call on whether GEN-07 is genuinely met follows the **same self-explanation-checkpoint pattern as Phase 3**: a human-verify checkpoint where the owner reviews the actual plot(s)/metric and confirms understanding before the phase is marked complete — not an automated metric-threshold pass.

### Tuning budget / iteration approach
- If the full sigma sweep (plus the epoch-increase escape hatch) doesn't produce visibly-ring-like output, stop there for this phase — don't expand into broader architecture-level search (different `input_size`/`output_size`/K bin-center count). That would be a deferred item, not in-scope here.
- Time budget: allowed to spread across a couple of sessions if visual results are ambiguous and warrant careful iteration — not required to fit in one sitting, but should stay proportionate to this project's "not to impress" scope discipline (no hard external deadline analog here like Phase 3's July 25 checkpoint; the only real constraint is the overall Sept 1 milestone).
- If no sigma value produces genuinely ring-like output: how to report that is explicitly left open until real results exist — Claude proposes a plain, honest write-up (per PROJECT.md's "don't gloss over it" rule) once the actual sweep outcome is known, and checks with the owner rather than deciding unilaterally now.

### Claude's Discretion
- Exact quantitative metric formula/threshold for the "lightweight supporting metric."
- Exact epoch-increase value if the escape hatch is triggered.
- Plot styling details beyond the locked side-by-side / heatmap+scatter structure.
- How to phrase/report a "no sigma value worked" outcome — deferred until actual sweep results are in hand.

</decisions>

<specifics>
## Specific Ideas

No specific visual reference requested — standard matplotlib, functional style, consistent with Phase 3's `results/phase3_loss_curve.png`.

</specifics>

<deferred>
## Deferred Ideas

- Broader architecture-level tuning (different `input_size`/`output_size`/K bin-center count) if the sigma sweep alone doesn't produce ring-like output — explicitly out of scope for Phase 4; would need its own future decision if it comes to that.

</deferred>

---

*Phase: 04-generative-quality*
*Context gathered: 2026-07-24*
