# Design Decisions Log

Durable architecture/design calls for the MerLin project, per [MerLin_SMART_Spec_Sept1.md](MerLin_SMART_Spec_Sept1.md). One entry per decision — what was chosen, what was rejected, and why.

---

## 2026-07-19 — Generator output representation: full-distribution matching (not single-point averaging, not discrete sampling)

**Context:** Converting the quickstart classifier (`quantum_layer(x) → class probabilities`) into an MMD-based generative model for the circles dataset required deciding what a "generated sample" actually means, given that `QuantumLayer`'s raw output is always a probability vector over `output_size` measurement outcomes (verified empirically: rows are non-negative and sum to exactly 1 — see [quickstart.py](quickstart.py)).

**Options considered:**
1. **Full-distribution matching (chosen).** Bin both the real 2D circles data and the circuit's output probability vector over the same fixed set of `K` reference points (bin-centers spanning the data region). Compare the two resulting probability vectors directly — no collapsing to a single point, no sampling.
2. **Weighted-average → single continuous point (rejected).** Map the probability vector to one (x, y) point via a probability-weighted average of fixed bin-center coordinates.
3. **Discrete `shots`-based sampling (rejected).** Use MerLin's `shots`/`sampling_method` forward-pass option to draw literal discrete measurement outcomes instead of the exact probability vector.

**Why option 1:**
- Option 2 collapses the full distribution to one blended point. Since the circles dataset is two separate rings with an empty gap between them, any time the circuit hedges probability between "inner ring" and "outer ring" bins, the weighted average lands in that empty gap — a region real data never occupies. This is a structural failure mode for multimodal targets (same reason averaging two population centers gives you a point neither population is near), not a fixable numerical detail.
- Option 3 avoids the averaging problem (each sample commits to one outcome, so it can land on either ring, never the gap), but introduces a real cost: drawing a discrete sample is not a smooth function of the circuit parameters θ, so standard `loss.backward()` doesn't flow through it without an additional (nontrivial) differentiable-sampling estimator. Not worth taking on for this timeline.
- Option 1 avoids both problems. It never collapses the distribution to a point (so no gap-filling), and it never samples (so gradients flow exactly the way they already do in the classifier — through the exact, smooth probability-vector output).

**The reusable payoff:** MMD's standard definition is
```
MMD²(P, Q) = E[k(x,x')] + E[k(y,y')] − 2·E[k(x,y)]     for x,x'~P, y,y'~Q
```
When P and Q are both categorical distributions over the same K fixed bin-centers {c₁...c_K} with probability vectors **p** (real data histogram) and **q** (circuit output), this expectation collapses to a finite double sum over bin-center pairs, weighted by **p**/**q** instead of empirical sample counts:
```
MMD²(p, q) = Σᵢⱼ pᵢpⱼ k(cᵢ,cⱼ) + Σᵢⱼ qᵢqⱼ k(cᵢ,cⱼ) − 2·Σᵢⱼ pᵢqⱼ k(cᵢ,cⱼ)
```
This is the same kernel/bandwidth machinery from the prior IQP-MMD work, just weighted by probability mass instead of sample counts. **p** is fixed (computed once from the real dataset, no gradient needed). **q** is the circuit's differentiable output. Critically, this form is naturally penalized for hedging into the gap between rings — mass placed where **p** is ~0 costs loss — which is exactly what option 2 couldn't express.

**Still open (implementation-level, not architectural):**
- `K` / bin-center layout: how many bins, how they're arranged spatially, and what region of (x, y) space they cover. Needs enough resolution near both rings; this is a resolution-vs-simulation-cost tradeoff, not a re-litigation of this decision.
- Kernel choice and bandwidth for `k(cᵢ,cⱼ)` — Gaussian is the default assumption; reuse whatever heuristic (e.g. median heuristic) came out of the IQP-MMD work if one exists.
- Latent noise distribution and dimensionality (`input_size` for `z`).

**Decided by:** Alejandro Jackson, informed by this conversation. Superseding note: if this doesn't work in practice (e.g. bin resolution turns out too coarse to represent the rings, or training the circuit against this loss doesn't converge), that's a reason to revisit — record the outcome here, don't silently swap approaches.

---

## 2026-07-19 — Follow-up: the three "still open" items above, resolved during Phase 2 discussion

Full detail in [`.planning/phases/02-generator-data-loss-infrastructure/02-CONTEXT.md`](.planning/phases/02-generator-data-loss-infrastructure/02-CONTEXT.md). Summary:

- **Bin-center layout:** K≈400 (20×20), uniform grid, data bounding box + padding, fully deterministic. Ring-aware density considered and rejected as unnecessary complexity for this timeline.
- **Kernel/bandwidth:** Gaussian kernel over **Euclidean** distance between bin-centers (`exp(-‖cᵢ-cⱼ‖²/(2σ²))`) — not the Hamming-distance kernel from the prior IQP-MMD project (`iqp-mmd-barren-plateau/src/iqp_bp/mmd/kernel.py`), which operates on binary bitstrings and doesn't port to continuous coordinates. Bandwidth: swept across a few σ values rather than one fixed number, carrying forward that project's `AC12 Bandwidth Sweep` finding that MMD² can look good while the learned distribution still fails to match target structure.
- **Latent noise:** Normal distribution at MerLin's own default scale (`std=2π`), **not** the `[0,1]` normalization the quickstart classifier used — that was quickstart.py's own choice, not a MerLin requirement (verified: `_build_simple_circuit`'s `angle_encoding_scale` defaults to `1.0`, no auto-rescaling). Dimensionality starts at 2 (matching the classifier's verified `input_size`), explicitly a Phase 3/4 tuning knob, not a Phase 2 correctness requirement.
- **New finding, not previously known:** MerLin ships a purpose-built `merlin.models.photonic_generator.PhotonicGenerator` class (`NormalLatent`, `VectorAdapter`, multi-head support) for exactly this generative-model pattern, and `QuantumLayer.simple()`'s `output_size` parameter is independent of `input_size` (regrouped via `ModGrouping`) — meaning `output_size = K` is directly achievable. Both are research pointers for Phase 2 implementation, not yet confirmed as the chosen implementation path.

---

## 2026-07-24 — Phase 3 training-step batch-reduction: average per-sample MMD² losses over a batch of z, not batch=1

**Context:** Each individual latent draw `z` already produces a complete, valid `(400,)` probability distribution (per the 2026-07-19 decision above), so unlike a classic GAN/GMMN, batching isn't structurally required — `mmd2(p_real, quantum_layer(z)[0], K)` for one fresh `z` is already a complete, differentiable training step, and it's the exact pattern Phase 2's `test_mmd2_gradient_reaches_quantum_layer` already verified. The open question was whether to also average across several `z`'s per step, and if so how.

**Options considered:**
1. **Batch=1 per step (the exact tested pattern).** Zero new risk beyond what Phase 2 already verified.
2. **Batch of ~16–32, average per-sample MMD² losses across the batch (chosen).** Loop the same tested `mmd2()` call across multiple fresh `z`'s each step, average the resulting scalars into one loss before `.backward()`.

**Why option 2:** MMD/QCBM literature (Liu & Wang 2018; Li et al. 2015 GMMN) reports MMD-based generative training is noise-sensitive at small batch sizes — batch=1 tends to produce a visibly noisier, less monotonic loss curve. Phase 3's success criterion is specifically "observable decreasing trend across epochs, not flat, not diverging," evaluated with roughly one day of runway before the July 25, 2026 stall-risk checkpoint — a noisy batch=1 curve directly threatens that criterion being defensibly true rather than eyeballed. Averaging per-sample losses over a batch is a strict generalization of the already-tested single-`z` pattern (same `mmd2()` call, just looped and averaged), not a new, untested formulation — so it adds negligible implementation risk while meaningfully reducing curve noise. Cost is acceptable: ~0.28s/step was measured at batch=64 in Phase 2 research, so batch=16–32 stays cheap.

**Decided by:** Alejandro Jackson, presented with both options and their tradeoff by Claude during `/gsd:plan-phase 3` (per CLAUDE.md's "no silent unilateral design decisions" and "training strategy" rules). Full research: [`.planning/phases/03-end-to-end-training-run/03-RESEARCH.md`](.planning/phases/03-end-to-end-training-run/03-RESEARCH.md).
