# Phase 3: End-to-End Training Run - Context

**Gathered:** 2026-07-24
**Status:** Ready for planning

<domain>
## Phase Boundary

Wire Phase 2's already-verified components (noise sampling, bin-centers, `p_real`, MMD² loss) into an actual training loop, run it, and prove — with scripted (not eyeballed) evidence — that the loss shows a real decreasing trend. This is the July 25, 2026 stall-risk checkpoint (GEN-06). Does not include generative-quality tuning or visual ring recovery (Phase 4) or benchmarking (Phase 5).

</domain>

<decisions>
## Implementation Decisions

### Batch-reduction strategy (locked 2026-07-24, owner-confirmed)
- Average per-sample MMD² losses across a batch of fresh `z` draws each step — NOT batch=1, NOT average-then-compare `q` vectors.
- Each step: sample a batch of `z` via `sample_latent(batch_size)`, forward through the single shared `QuantumLayer.simple(input_size=10, output_size=400)` instance, compute `mmd2(p_real, q_i, K)` per row, average the scalars, `.backward()`.
- Full reasoning and rejected alternative: [DESIGN_DECISIONS.md](../../../DESIGN_DECISIONS.md) (2026-07-24 entry).

### Hyperparameter defaults (Claude's Discretion, per 03-RESEARCH.md's Primary Recommendation)
- `batch_size = 32` — within the owner-confirmed ~16-32 range; cheap at the measured ~0.28s/step-at-batch=64 cost.
- `sigma = 0.1` — reuses the exact value already proven to produce finite gradients in Phase 2's test, and matches the verified ring-gap geometry (0.1) from Phase 2 research.
- `epochs = 300`, `lr = 0.01` (Adam) — starting points per 03-RESEARCH.md; not yet empirically validated against this specific circuit. A short smoke run (few epochs) should precede the full run to catch gross issues before committing the ~1-day runway.
- These are tunable if the smoke run shows they're clearly wrong (e.g. loss flat at 300 epochs, or diverging) — not locked the way the batch-reduction strategy is.

### Success-criteria verification method
- "Runs to completion without errors": the training script exits 0.
- "Loss curve shows a real, observable decreasing trend, not flat, not diverging": a scripted check, not eyeballing — e.g. `scipy.stats.linregress` fitted slope over all epochs is negative with reasonable confidence, plus a first-N%-vs-last-N%-mean comparison. This check's actual output (not a printed log alone) is the evidence for GEN-06 being met.

### Artifacts convention (new — none existed before this phase)
- `results/` directory for run outputs: loss history (CSV), loss curve (PNG), and the trained circuit's checkpoint (`torch.save`). Flat naming (e.g. `results/phase3_loss_history.csv`), extensible for Phases 4-6.

</decisions>

<specifics>
## Specific Ideas

- Mirror `quickstart.py`'s flat, no-framework script style for `train.py` — construct the `QuantumLayer` and `Adam` optimizer once outside the loop, log loss every epoch.
- Reuse `P_REAL`/`CENTERS`/kernel-matrix computation pattern already established in `tests/test_mmd.py` (compute once, outside the loop).

</specifics>

<deferred>
## Deferred Ideas

None — visual ring recovery, σ sweep evaluation, and hyperparameter tuning beyond "does it show a real decreasing trend" are explicitly Phase 4's job, not Phase 3's.

</deferred>

---

*Phase: 03-end-to-end-training-run*
*Context gathered: 2026-07-24*
