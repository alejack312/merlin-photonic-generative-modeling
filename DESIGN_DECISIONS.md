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

**Correction (2026-07-29) — this objective is not quite what it looks like.** At first I thought "average the per-sample MMD² losses over a batch" was just a variance-reduction trick on top of the same underlying quantity — same thing being optimized, just a smoother estimate of it. But I realized, working through it directly, that `E_z[mmd2(p, q_z)]` and `mmd2(p, E_z[q_z])` are two different quantities, and we train on the first while "the generator's actual output distribution" is the second. `mmd2(p,q) = p^T K p + q^T K q - 2 p^T K q` is a convex quadratic form in `q` (`K` is a Gaussian-kernel Gram matrix, positive semi-definite). By Jensen's inequality, `E_z[q_z^T K q_z] ≥ (E_z[q_z])^T K (E_z[q_z])`, while the cross term `-2 p^T K q_z` is linear in `q_z` and passes through expectation exactly. So `E_z[mmd2(p, q_z)] ≥ mmd2(p, q̄)`, where `q̄ = E_z[q_z]` is the generator's true marginal output distribution (what you'd actually get by sampling `z`, then a measurement outcome) — with equality only when `q_z` has zero variance across `z`, i.e. no latent diversity at all. The objective this project actually minimizes is therefore an upper bound on `mmd2(p, q̄)`, and driving that upper bound down has a side effect the GMMN/QCBM batching-for-noise-reduction citations above never claimed to justify: it implicitly rewards *less* latent diversity, since the bound tightens toward the true value as `q_z` becomes more constant across `z`. Not necessarily wrong for this project's goals — but a different tradeoff than "just a smoother estimate," and worth knowing if asked to defend precisely what the training loss represents.

**Decided by:** Alejandro Jackson, presented with both options and their tradeoff by Claude during `/gsd:plan-phase 3` (per CLAUDE.md's "no silent unilateral design decisions" and "training strategy" rules). Full research: [`.planning/phases/03-end-to-end-training-run/03-RESEARCH.md`](.planning/phases/03-end-to-end-training-run/03-RESEARCH.md).

**Validated empirically (2026-07-24):** the real Phase 3 training run confirmed this choice in practice, not just in theory — see [03-01-SUMMARY.md](.planning/phases/03-end-to-end-training-run/03-01-SUMMARY.md). For a plain-language walkthrough of what `z` is, what gets averaged, and why (including a misconception caught and corrected at the Phase 3 self-explanation checkpoint), see [NOTES.md](NOTES.md).

---

## 2026-07-25 — Phase 4 tuning: sigma sweep + batch-size sweep don't fix ring structure; `ModGrouping` index-fold identified as a likely cause

**Context:** Phase 4's first checkpoint (`results/phase4_scatter_comparison.png`, sigma=0.1, the Phase 3 checkpoint) showed a diffuse, roughly-uniform generated distribution — no visible two-ring structure, `ring_mass=0.60` vs real data's 1.0. Owner reviewed and called it "sweep needed" (04-01-SUMMARY.md). Two rounds of tuning followed.

**Round 1 — `SIGMA_GRID` sweep (Plan 04-02, formal):** retrained fresh generators at sigma ∈ {0.02, 0.05, 0.1, 0.2, 0.4} — this sigma is the MMD² loss's own Gaussian-kernel bandwidth, not just a visualization parameter. All 5 plateaued at diffuse, non-ring output (`results/phase4_sweep_comparison.png`, `results/phase4_sweep_metrics.csv`). Owner's own visual read: sigma=0.1 best (ring_mass=0.616), sigma=0.05 "somewhat" — neither judged as genuinely ring-shaped.

**Round 2 — batch-size sweep (ad hoc, not a formal plan):** fixed sigma=0.1 (owner's pick from Round 1), retrained at batch_size ∈ {16, 32, 64, 128} — 300 epochs each, same `train_step` (`batch_sweep.py`, `results/phase4_batch_sweep_comparison.png`, `results/phase4_batch_sweep_metrics.csv`).

| batch_size | ring_mass | gap_mass |
|---|---|---|
| 16 | 0.485 | 0.074 |
| 32 (baseline) | 0.609 | 0.035 (best) |
| 64 | 0.610 | 0.063 |
| 128 | 0.618 | 0.077 |

Larger batch nudges ring_mass up marginally but makes gap_mass worse; owner's visual read on the comparison figure: none of the four look meaningfully closer to two rings. Batch size is not the lever.

**Likely structural cause found while investigating a 3rd lever (increasing `input_size`):** `QuantumLayer.simple(input_size=10, output_size=400)`'s circuit has a "natural width" of 462 raw measurement outcomes (`comb(n_modes, n_photons)` where `n_modes=input_size+1`). Since 462 ≠ 400, MerLin's `ModGrouping` post-processing maps `output[i] = Σ raw[j] for j % 400 == i` — a raw-index modulo fold with no relationship to the (x, y) spatial adjacency of the 400 bin-centers (`generator/bin_centers.py`). At `input_size=10`, 62/400 output bins are folded sums of 2 unrelated raw outcomes; the rest are clean 1:1. Checked the full `input_size` range MerLin allows (1–19): natural width grows combinatorially (252 at input_size=9, 462 at 10, 924 at 11, 1716 at 12, ...), so **increasing `input_size` past 10 strictly worsens the fold** (every one of the 400 bins becomes a multi-way fold at input_size≥11), and decreasing it below 10 leaves bins permanently zero (natural width < 400). `input_size=10` is already the least-folded option that covers all 400 bins within the `.simple()` API — this was flagged as an open research pointer in the 2026-07-19 follow-up entry above ("`output_size` is independent of `input_size`, regrouped via `ModGrouping`") but its consequence for tuning direction wasn't worked out until now.

**Not yet decided (at the time this entry was first written):** whether to pursue a deeper/more-expressive circuit via MerLin's `CircuitBuilder` directly, or a different fix entirely. **Resolved in the follow-up entry immediately below** ("Phase 4, third tuning axis") — this entry records the sigma/batch findings and the `ModGrouping` mechanism as the basis for that discussion, not the resolution of it.

**Decided by:** Alejandro Jackson — sigma=0.1 selection (04-01) and "sweep needed"/"batch size isn't it" calls (04-02, this session) were the owner's visual judgments; the `ModGrouping` fold mechanism was Claude's investigation, surfaced before acting on the owner's "increase circuit size" request per CLAUDE.md's "no silent unilateral design decisions" and "architecture ... is the owner's job" rules.

---

## 2026-07-25 — Phase 4, third tuning axis: also investigated a deeper structural cause (arbitrary index↔spatial-bin correspondence), researched two candidate fixes against MerLin's actual docs/source, chose one, plan approved

**Context:** While investigating a 3rd tuning lever (increasing `input_size`, see entry above), a second, deeper problem was found beyond the `ModGrouping` fold: `quantum_layer.output_keys` (the raw circuit's 462 output positions) are photon-occupation combinatorics — tuples like `(1,1,1,1,1,1,0,0,0,0,0)` meaning "modes 0–5 hold a photon" — enumerated in a fixed order with **zero designed relationship** to `bin_centers.py`'s (x,y) raster-grid ordering. So even the 338 output bins that pass through `ModGrouping` unfolded (1:1) still have an arbitrary pairing to a spatial location. This plausibly explains why MMD² loss drops substantially in every run (sigma sweep, batch sweep) while the visual output stays scattered/grid-like rather than ring-shaped: the circuit's natural parameter-smoothness has no reason to translate into (x,y) smoothness under this labeling — nearby circuit parameters correlate probability across *physically similar photon patterns*, not *spatially nearby bins*.

**Two candidate fixes were researched directly against MerLin's docs and installed source** (not guessed) — full detail in the conversation, summarized here:

**Option 2 — deeper circuit via MerLin's `CircuitBuilder`:**
- Confirmed real and documented: `CircuitBuilder` composes `add_entangling_layer`, `add_angle_encoding`, `add_rotations`, `add_superpositions(depth=...)` as independent calls — genuine circuit-depth control decoupled from `input_size`, unlike `.simple()`.
- Checked whether `CircuitBuilder` could also reduce the `ModGrouping` fold by choosing a better `(n_modes, n_photons)` pair: swept all combinations up to 19 modes. Best alternative found: `(15 modes, 3 photons)` → natural width 455 (55 folded bins) vs. current `(11, 6)` → 462 (62 folded bins) — a marginal improvement, not a fix.
- No generative/distribution-matching guidance exists anywhere in MerLin's documentation — the official walkthrough is classification-only (Iris dataset). This would be uncharted territory for the library.
- Net assessment: real capability, but its cheap form (mode/photon tuning) barely helps, and its real lever (depth) is a bet that raw capacity can out-muscle an arbitrary labeling — not a fix aimed at the labeling itself.

**Option 3 — custom output mapping (chosen):**
- MerLin ships a purpose-built extension point for exactly this: `merlin.models.photonic_generator.OutputAdapter`, an abstract base class whose docstring reads *"Subclass OutputAdapter when raw quantum measurements need a custom mapping to generated samples."* It receives both the raw probability tensor and `output_keys`.
- Simpler path (used instead of adopting the whole `PhotonicGenerator` wrapper): `QuantumLayer.simple(input_size=10, output_size=None)` already returns the raw, untouched 462-dim probability vector (skips `ModGrouping` entirely), and `output_keys` is directly available on it.
- Checked whether MerLin ships any spatially-aware grouping out of the box: no. `ModGrouping` (mod-fold) and `LexGrouping` (contiguous-chunk sum, found via docs) are both naive index arithmetic with no awareness of what the indices mean. The fix has to be custom-built, but `output_keys`'s exposure is clearly meant to enable exactly that.

**Decision:** pursue option 3. Rationale (owner's call, presented with both options' tradeoffs first): cheaper (no circuit rebuild), faster to test, and mechanistically aimed at the actual identified cause (the arbitrary correspondence) rather than hoping added capacity routes around it. Not mutually exclusive with option 2 — could be layered afterward if still needed.

**Concrete design (full detail + verified implementation specifics in the approved plan file, `C:\Users\cuqui\.claude\plans\plan-option-3-dynamic-bunny.md`):**
1. **Eliminate the fold**: match K exactly to the circuit's natural width (462, via a 21×22 grid) instead of 400 — removes `ModGrouping` entirely, zero information ever summed together.
2. **Replace the arbitrary pairing with a designed one**: sort the 462 bin-centers by ascending **radius** from (0.5,0.5) (real target = two concentric rings, so this turns the target into two contiguous "on" bands in 1D rank-order — a simpler shape for a smooth circuit to represent than an arbitrary 2D pattern) and sort the 462 raw Fock states by center-of-mass of occupied mode indices (a first-pass smoothness heuristic — beamsplitter/phase parameters physically redistribute amplitude between adjacent modes; **explicitly not a proven guarantee**, stated as such in code and here). Pair by matching rank.
3. Implementation is additive-only: new `generator/natural_grid.py`, `generator/spatial_alignment.py`, `generator/naturally_ordered_generator.py`, and a root-level `natural_order_train.py` (following `sweep.py`/`batch_sweep.py`'s established pattern: fixed sigma=0.1/batch=32/300-epoch hyperparameters reused from the prior two tuning rounds, resumable, foreground execution per the documented backgrounded-script lesson below). No existing file is modified; existing checkpoints and scripts are unaffected.

**Status at time of writing:** plan reviewed and approved by the owner; implementation not yet started (owner asked to pause and document the full thread first — this entry is that documentation). Once run, results (actual `ring_mass`/`gap_mass` vs. the `0.609/0.035` baseline above, the rank-profile diagnostic plot, and the owner's own visual judgment) will be recorded in a follow-up entry, per this project's "record the outcome, don't silently swap approaches" rule (see the 2026-07-19 entry above).

**Decided by:** Alejandro Jackson, after Claude presented both options' researched tradeoffs (per CLAUDE.md's "no silent unilateral design decisions" / "architecture is the owner's job" rules) and a detailed implementation plan went through this repo's plan-review workflow (`ExitPlanMode`) before any code was written.

---

## 2026-07-25 — Phase 4, option 3 implemented and run: natural-width matching + rank-based spatial correspondence produces a real, measurable improvement — still not two distinct rings

**What was built** (exactly the approved plan, additive-only — no existing file modified):
`generator/natural_grid.py` (21×22 = 462 grid), `generator/spatial_alignment.py` (`radius_sort_order`, `fock_state_sort_order`), `generator/naturally_ordered_generator.py` (wraps `QuantumLayer.simple(input_size=10, output_size=None)`, permutation registered as a buffer), `natural_order_train.py` (sigma=0.1, batch=32, 300 epochs, LR=0.01 — identical to the prior best run, so the correspondence fix is the only variable). 16 new tests; full suite 48 passed, zero regressions.

**Results** (sigma=0.1, batch=32, 300 epochs in both cases):

| variant | K | ring_mass | gap_mass |
|---|---|---|---|
| prior best (raster order, ModGrouping fold) | 400 | 0.609 | 0.035 |
| natural order (no fold, rank-paired) | 462 | **0.691** | 0.048 |

Metrics are stable across latent draws, so the gap is not a single-sample artifact — over 20 fresh `z` samples each: new = 0.684 ± 0.008 (range 0.670–0.698), old = 0.613 ± 0.004 (range 0.604–0.621). The ranges do not overlap. Training loss fell 0.0403 → 0.0026.

**Owner's visual judgment (the deciding read, per this project's rules):** "quite an improvement. Still not two distinct rings, but an improvement." Recorded as-is — the metric agrees with the visual read in direction, and neither is being used to overrule the other.

**Why the improvement is real and not noise — the mechanism, backed by measurements taken after the run:**

1. **Radius sorting genuinely simplifies the target, and this is the dominant effect.** Counting maximal contiguous runs of non-zero bins in `p_real`: in the original raster ordering the target is **44 disjoint fragments**; radius-sorted it collapses to **~6**. Measured on the *old* 400-bin grid too (44 → 7 runs), which isolates this as an effect of the ordering alone, independent of the fold. The model's output is a 1-D vector; under raster order the ring target is a high-frequency comb in that vector, under radius order it is a couple of broad bands. Less high-frequency structure to represent means a smooth output can get closer.

2. **The trained output is measurably smoother in the ordering that now corresponds to radius.** Total variation (Σ|successive differences|) of the trained `q` in its own index order: **1.82 (old) → 1.16 (new)**. For reference, the old model's output re-indexed into radius-sorted order measures 1.46 — so the new run is smoother than the old one even after correcting for the ordering change. The circuit was always producing something smooth over *its own* output space; the fix is that "smooth over the circuit's output space" now approximately means "smooth in radius" instead of meaning nothing spatially.

3. **Removing the fold is real but is the smaller contribution.** At K=400 only 62 of 400 bins were folded sums of 2 unrelated raw outcomes; the remaining 338 were already clean 1:1 and still mislabeled. The 44 → 7 measurement in (1) shows the mislabeling, not the fold, was carrying most of the damage.

**Honest limits on this claim — what the run does *not* establish:**
- **Two changes were made at once** (fold eliminated *and* correspondence redesigned). The decomposition above argues the correspondence dominates, but no ablation was run that changes only one of the two. That ablation is cheap and is the right next step if the attribution ever needs to be defended precisely.
- **`fock_state_sort_order` remains an unproven heuristic**, exactly as flagged before the run. Rank-domain correlation between `p_real` and `q` is only **0.38** — positive and clearly non-random, but far from the target shape. If the center-of-mass ordering really tracked the circuit's parameter-smoothness well, this number should be much higher. This is the most likely place further gains are hiding, and it is the honest explanation for why the result improves without becoming two rings.
- One seed, one training run per variant. The ±0.008 figure above is variation across latent draws from a *fixed* trained model, not across independent trainings.
- **Correction (2026-07-29) — the mechanism argument above (points 1-2) has a logical gap I missed at the time.** At first I thought "fewer disjoint fragments in the target, measured smoother output" was itself sufficient evidence that reordering *caused* the improvement. But I realized MMD² is invariant to any consistent relabeling of `p`, `q`, and the kernel matrix together — reorder the target, the model's output, and the distance table the same way, and the loss value doesn't change. So "the target looks tidier in list order" cannot by itself be why the score improved; that can only matter if the circuit has a real, independently-existing tendency for neighboring list-positions to move together when its parameters are nudged, and our new ordering happens to line that tendency up with the target's geography. Points 1-2 measure that the *target* got tidier and that trained `q` is *smoother in the new order* — they do not measure whether the circuit's untrained/generic output-neighbor behavior has that locality property in the first place, which is the actual load-bearing claim. No ablation was run to test it (e.g., checking whether small parameter perturbations move list-neighbors together more than random pairs, independent of training). There is also an unexamined confound: sigma=0.1 was chosen for the old 400-bin raster grid and never re-swept after this fix changed K to 462 and the correspondence entirely — at sigma=0.1, points on opposite rings (0.1 apart) have kernel similarity 0.61 to each other, while a point in the empty gap between the rings has similarity 0.88 to either ring. A loss this tolerant of gap-filling could produce a similar ring_mass bump on its own, independent of the reordering story. Until the ablation (fold-only vs. correspondence-only vs. both) and a post-fix sigma sweep are run, the mechanism above is the best available *hypothesis*, not a demonstrated cause.

**Status:** this is an improvement, not a solution. Whether it closes Phase 4 (proceed to 04-03's write-up + GEN-07 checkpoint, documenting the diffuse-but-improved result honestly) or motivates a 4th axis is the owner's call with these numbers in hand — deliberately not pre-decided here.

**Artifacts:** `results/phase4_natural_checkpoint.pt`, `results/phase4_natural_metrics.csv`, `results/phase4_natural_loss_history.csv`, `results/phase4_natural_comparison.png` (3-panel: real | prior best | natural order), `results/phase4_natural_rank_profile.png` (rank-domain `p_real` vs `q`).

**Decided by:** Alejandro Jackson — the "improvement, still not two rings" verdict is the owner's visual judgment. The mechanism explanation above is Claude's, written after the owner's read and grounded in post-hoc measurements (run-count, total-variation, rank correlation, cross-draw stability) rather than in a plausible-sounding story; the confounds and the weak 0.38 correlation are stated because the owner has to be able to defend this unaided.
