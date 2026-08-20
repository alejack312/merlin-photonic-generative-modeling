---
phase: 4
phase_name: "Generative Quality"
project: "MerLin Photonic Generative Modeling"
generated: "2026-08-20"
counts:
  decisions: 6
  lessons: 5
  patterns: 5
  surprises: 4
missing_artifacts: []
---

# Phase 4 Learnings: Generative Quality

## Decisions

### Cheap-check-before-sweep sequencing
Visualize Phase 3's already-trained sigma=0.1 checkpoint first (a "cheap check," reusing an existing checkpoint with no new training) before deciding whether the full 5-value SIGMA_GRID sweep was warranted.

**Rationale:** Avoids ~12 minutes of retraining if the cheap check already looked sufficient. Locked into 04-CONTEXT.md's "Sigma sweep / retraining strategy" decision.
**Source:** 04-CONTEXT.md, 04-01-PLAN.md

---

### Visual judgment plus a lightweight supporting metric, never metric-only
Success judgment method combines the owner looking at actual scatter/heatmap plots with a lightweight `ring_band_metrics` (ring_mass/gap_mass) computation — explicitly not an automated metric-threshold pass, and explicitly not a full Phase-5-style benchmark.

**Rationale:** MMD² (and by extension any single scalar metric) can look numerically fine while the learned distribution is structurally wrong — carried forward from Phase 2's deferred item and the prior IQP-MMD project's "AC12 Bandwidth Sweep" lesson. A human must be the one who confirms GEN-07, matching this project's self-explanation-checkpoint pattern from Phase 3's GEN-06.
**Source:** 04-CONTEXT.md, 04-03-PLAN.md

---

### Full 5-value SIGMA_GRID sweep, not a narrow bracket around 0.1
When retraining was needed, all 5 values `[0.02, 0.05, 0.1, 0.2, 0.4]` were swept, holding epochs/lr/batch_size fixed at Phase 3's values (300/0.01/32), isolating sigma as the single variable under test.

**Rationale:** Isolates sigma as the only variable; a narrow bracket risks missing a qualitatively different regime. Increasing epochs was named as an explicit escape hatch (not exercised) rather than a routine additional knob to sweep.
**Source:** 04-CONTEXT.md, 04-02-PLAN.md

---

### Stop scope at hyperparameter tuning; defer architecture-level search
If the sigma sweep (plus the epoch-increase escape hatch) didn't produce visibly ring-like output, the phase would stop there rather than expanding into architecture-level search (different `input_size`/`output_size`/K bin-center count).

**Rationale:** Keeps Phase 4 proportionate to its "not to impress" scope discipline; broader architecture search was explicitly deferred as its own future decision rather than absorbed into this phase.
**Source:** 04-CONTEXT.md ("Tuning budget / iteration approach", "Deferred Ideas")

---

### "Option 3" structural output-correspondence fix (K=400→462, radius/center-of-mass rank pairing)
Beyond hyperparameter sweeps, an ad hoc structural fix was made: removed MerLin's `ModGrouping` fold (K=462 raw outputs, not folded to 400) and paired bin centers (sorted by radius) with Fock states (sorted by center-of-mass) by rank, instead of using the arbitrary raw-index-to-bin-center correspondence.

**Rationale:** Diagnosed that `QuantumLayer.simple`'s raw output indices (Fock-state combinatorics) had no designed relationship to the (x,y) bin-center grid, and that the 462→400 fold compounded this. Radius-sorting collapsed the ring target from ~44 disjoint raster-order fragments into ~2 contiguous radius-sorted bands, matching the circuit's natural output-space smoothness. This produced a real, measurable improvement (ring_mass 0.691 vs. 0.609 baseline) though not full resolution.
**Source:** results/phase4_summary.md, 04-03-SUMMARY.md

---

### GEN-07 marked NOT MET rather than reframed as success
After exhausting three tuning axes (sigma sweep, batch-size sweep, structural correspondence fix), the owner's explicit verdict was "GEN-07 not met, move to Phase 5" — recorded as the phase's honest final status rather than softened.

**Rationale:** Directly required by PROJECT.md's "don't gloss over it" rule and 04-CONTEXT.md's explicit deferral on how to phrase a "no sigma value worked" outcome — the phrasing was worked out with the owner once real results existed, not decided unilaterally in advance.
**Source:** 04-03-SUMMARY.md, results/phase4_summary.md

---

## Lessons

### A metric well above random baseline is not the same as "looks ring-like"
At the 04-01 cheap check, ring_mass=0.602 (exact q) was well above a random/uniform baseline, yet both the executing agent and orchestrator independently judged the actual scatter/heatmap plots as diffuse, not ring-concentrated — genuinely ambiguous by eye.

**Context:** This is the concrete case the "MMD² can look numerically fine while the structure is wrong" caution (04-CONTEXT.md) anticipated, observed directly rather than just theorized about.
**Source:** 04-01-SUMMARY.md

---

### Backgrounded multi-minute training scripts did not reliably survive in this environment
The first `sweep.py` run was launched via a backgrounded Bash call. It completed 4 of 5 sigmas (checkpoints written over ~7 minutes) then went silent with no captured stdout/stderr; ~28 minutes later no python process was alive. Root cause was the execution environment killing the backgrounded process across tool-call turns, not a bug in the training code.

**Context:** Discovered during Plan 04-02's sweep execution; recovered by making `sweep.py` resumable (skip retrain if a sigma's checkpoint already exists) and rerunning the remainder in the foreground.
**Source:** 04-02-SUMMARY.md

---

### An unseeded metrics script silently overwrote its own committed CSV with different numbers on rerun
`batch_sweep.py` drew fresh, unseeded latent samples on every invocation. A later rerun (for an unrelated check) silently overwrote `results/phase4_batch_sweep_metrics.csv` with new numbers, while the already-written summary prose still quoted the old numbers — the mismatch was only caught on a reconciliation pass days later (2026-07-29 correction).

**Context:** Found while writing/correcting `results/phase4_summary.md`; the fix was to treat the checked-in CSV as source of truth over the prose table, and to note the discrepancy explicitly rather than silently correct it without comment. Underlying issue (no RNG seeding, one training run per variant) is called out as an explicit honest-limits caveat, not resolved.
**Source:** results/phase4_summary.md ("Correction (2026-07-29)" note)

---

### `ModGrouping`'s raw-output-to-bin-center correspondence has no designed spatial meaning
MerLin's `QuantumLayer.simple` raw output indices are Fock-state combinatorics with no designed relationship to the (x,y) bin-center grid used for the circles task; the `ModGrouping` post-processing that folds 462 raw outputs to 400 compounds this arbitrary correspondence.

**Context:** Diagnosed only after two full tuning axes (sigma, batch size) failed to move the needle — this was a deeper, architecture-adjacent issue rather than a hyperparameter issue, and was not anticipated by the original phase plan (04-01/04-02 anticipated only sigma tuning).
**Source:** results/phase4_summary.md

---

### The MerLin quickstart classifier is itself a weak baseline, not a strong reference point
When the owner asked for a comparison against MerLin's own quickstart classifier to calibrate expectations, it turned out to have 46-64% test accuracy across repeated runs on an easily-separable dataset — undermining its use as a reference point for "what good MerLin performance looks like."

**Context:** Surfaced during the extended GEN-07 checkpoint discussion in Plan 04-03, before the final "not met" verdict was given.
**Source:** 04-03-SUMMARY.md

---

## Patterns

### Reusable sampling/metric primitives built once, consumed by every later plan unmodified
`generator/visualize.py`'s `sample_points` (torch.multinomial draw from an analytic q) and `ring_band_metrics` (ring_mass/gap_mass against known circles geometry) were built and tested in Plan 04-01, then reused unmodified by Plan 04-02's sweep and Plan 04-03's final checkpoint.

**When to use:** When a phase's evaluation logic will plausibly be needed again by a later plan or later phase (04-CONTEXT.md explicitly asked for the metric to be "designed with an eye toward reuse in Phase 5") — build and test it as a standalone module once rather than re-deriving it inline per plan.
**Source:** 04-01-SUMMARY.md, 04-02-PLAN.md

---

### Scatter-based heatmap rendering instead of imshow
Real-vs-generated probability heatmaps were rendered via `ax.scatter(centers[:,0], centers[:,1], c=mass, cmap=...)` rather than `imshow`, to avoid a verified x/y-orientation flip pitfall.

**When to use:** Any time a probability/mass vector is defined over irregular or non-grid-aligned bin centers (as here) rather than a clean 2D array — scatter-based coloring sidesteps imshow's implicit row/column-to-axis orientation assumptions.
**Source:** 04-01-PLAN.md (04-RESEARCH.md Pitfall 3)

---

### Ring/gap-band metric computed on both exact analytic distribution and a finite sample, printed side by side
`ring_band_metrics` was applied both to the exact analytic `q` (deterministic, primary) and to counts from a 400-point `torch.multinomial` draw (secondary cross-check), both printed together.

**When to use:** When evaluating a generative model whose exact output distribution is available (not just samples) — reporting both the exact and sampled version cross-checks that the metric on real deployed sampling matches the analytic ideal, catching sampling-noise-driven misreads.
**Source:** 04-01-PLAN.md, 04-01-SUMMARY.md

---

### Resumable, checkpoint-per-unit-of-work sweep scripts for multi-minute training loops
`sweep.py` was made resumable — if a given sigma's checkpoint already exists on disk, skip retraining it and only recompute its metrics — so an externally-killed background process doesn't require redoing already-finished, valid work.

**When to use:** Any script whose total runtime exceeds what a single foreground tool call/timeout can reliably guarantee, especially when it must be launched via a backgrounded call in this environment. Prefer this over hoping a single long-running background job survives, or over accepting a full redo on interruption.
**Source:** 04-02-SUMMARY.md ("patterns-established")

---

### Run all sweep variants first, review the combined figure once — not one variant at a time
All 5 SIGMA_GRID retrains were completed before any visual review; results were then combined into a single 6-panel figure (real + all 5 sigmas) for one combined judgment pass, per 04-CONTEXT.md's locked process.

**When to use:** Multi-variant sweeps intended for human visual comparison — batching the review avoids anchoring bias from judging the first variant in isolation and reduces total review overhead versus an interactive one-at-a-time loop.
**Source:** 04-CONTEXT.md, 04-02-PLAN.md, 04-02-SUMMARY.md

---

## Surprises

### GEN-07, the phase's headline requirement, was formally not met despite three separate tuning axes
Sigma sweep (5 values), batch-size sweep (4 values), and a structural output-correspondence fix (option 3) were all tried across the phase, and none produced output a human would call two clean, distinct rings — the best result (option 3, ring_mass=0.691) was a real, mechanistically-understood improvement but a partial one, not resolution.

**Impact:** The phase's scope grew organically beyond its original two-plan structure (04-01 cheap check, 04-02 sweep) to include two additional ad hoc, owner-directed axes before the final checkpoint was taken — and even then the headline claim was closed as NOT MET rather than reframed as success. This is the single most consequential learning of the phase: the project's "don't gloss over it" documentation discipline was exercised for real, not just as a stated principle.
**Source:** 04-03-SUMMARY.md, results/phase4_summary.md

---

### The root cause of poor ring recovery was an encoding/correspondence bug, not an undertrained model or wrong bandwidth
Two full tuning axes (sigma, batch size) — the ones the original plan anticipated — made only marginal difference (ring_mass 0.602→0.616→0.609 across variants). The actual biggest lever (0.609→0.691) came from fixing an arbitrary raw-output-index-to-bin-center correspondence that had no designed spatial meaning, discovered only after both anticipated axes were exhausted.

**Impact:** Confirms this project's own house lesson (AC12 Bandwidth Sweep, cited in 04-CONTEXT.md) in a new form: the failure mode that looked like a hyperparameter problem (bandwidth/batch size) was actually a structural/architectural issue one layer deeper, and the phase's original plan structure (built before this was known) had to be extended ad hoc to reach it.
**Source:** results/phase4_summary.md

---

### A background training process died silently with zero error output, costing ~28 minutes of undetected wall-clock time
The first sweep attempt appeared to run to completion in the background but was killed by the environment partway through (after sigma=0.2, before sigma=0.4), with the background task's captured output file containing no training print output at all — not even for the sigmas that had genuinely completed, suggesting stdout buffering under redirection rather than a crash.

**Impact:** Plan 04-02's duration (~46 min) was nearly double what the training math alone predicted (~12 min), almost entirely due to this undetected gap. Directly produced the "resumable sweep script" pattern now on record for future long-running scripts in this environment.
**Source:** 04-02-SUMMARY.md

---

### A metrics CSV silently drifted from the prose that cited it, and was only caught 4 days later
`results/phase4_batch_sweep_metrics.csv` was regenerated by an unseeded rerun of `batch_sweep.py` after `results/phase4_summary.md`'s prose table had already been written from the original run's numbers — the two disagreed until a 2026-07-29 reconciliation pass caught and explicitly corrected it in place.

**Impact:** Did not change the phase's conclusion (batch=32 was still best either way), but is a concrete instance of a documentation-integrity risk (unseeded scripts + committed derived artifacts + prose that quotes them) worth guarding against in any future phase that mixes randomized sweeps with written summaries.
**Source:** results/phase4_summary.md ("Correction (2026-07-29)" note)
