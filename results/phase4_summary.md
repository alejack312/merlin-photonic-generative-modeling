# Phase 4 Summary: Generative Quality

## Path taken

Three tuning axes were tried, in order, each because the previous one's owner-reviewed output was not ring-like enough:

1. **Sigma cheap-check (04-01)**: sigma=0.1 (Phase 3's checkpoint). Owner decision: **sweep-needed** — generated scatter/heatmap diffuse across the square, not ring-concentrated.
2. **Full SIGMA_GRID sweep (04-02)**: all 5 values `[0.02, 0.05, 0.1, 0.2, 0.4]`, fixed epochs/lr/batch_size. sigma=0.1 stayed best. Owner decision: still not ring-like at any sigma value.
3. **Ad hoc extensions, sigma=0.1 held fixed** (not formal GSD plans, both owner-directed):
   - **Batch-size sweep**: batch ∈ {16, 32, 64, 128}. batch=32 (already Phase 3's default) stayed best. Owner-confirmed: no batch size looks meaningfully closer to two rings.
   - **"Option 3" — natural-width matching + rank-based spatial correspondence**: diagnosed that `QuantumLayer.simple`'s raw output indices (Fock-state combinatorics) have no designed relationship to the (x,y) bin-center grid, and that MerLin's `ModGrouping` post-processing (folding 462 raw outputs down to 400) compounds the problem. Fixed both: K=462 (no fold) + bin centers sorted by radius, Fock states sorted by center-of-mass, paired by rank. Retrained at identical hyperparameters (sigma=0.1, batch=32, 300 epochs, lr=0.01).

## Artifacts reviewed

- `results/phase4_scatter_comparison.png`, `results/phase4_heatmap_comparison.png` — sigma=0.1 cheap check (04-01)
- `results/phase4_sweep_comparison.png`, `results/phase4_sweep_metrics.csv` — full SIGMA_GRID sweep (04-02)
- `results/phase4_batch_sweep_comparison.png`, `results/phase4_batch_sweep_metrics.csv` — batch-size sweep
- `results/phase4_natural_comparison.png`, `results/phase4_natural_rank_profile.png`, `results/phase4_natural_metrics.csv` — option 3 (natural-order correspondence)

## Ring/gap-band metric values

| variant | K | sigma | batch | ring_mass | gap_mass |
|---|---|---|---|---|---|
| cheap check (04-01) | 400 | 0.1 | 32 | 0.602 (exact) / 0.572 (sampled) | 0.034 / 0.030 |
| SIGMA_GRID sweep best (04-02, sigma=0.1) | 400 | 0.1 | 32 | 0.616 | — |
| batch sweep best (batch=32, reused 04-02 checkpoint) | 400 | 0.1 | 32 | 0.609 | 0.035 |
| batch=64 | 400 | 0.1 | 64 | 0.610 | 0.063 |
| batch=128 | 400 | 0.1 | 128 | 0.618 | 0.077 |
| **option 3 (natural order)** | **462** | **0.1** | **32** | **0.691** | **0.048** |

Option 3's ring_mass is stable across latent draws (20 fresh samples: 0.684 ± 0.008, range 0.670–0.698), non-overlapping with the prior best's range (0.613 ± 0.004, range 0.604–0.621) — the gap is not a single-sample artifact.

## Tuning performed

- Sigma: full 5-value grid swept (04-02). sigma=0.1 best throughout every subsequent axis.
- Batch size: 4 values swept ({16,32,64,128}), sigma held at 0.1. batch=32 best.
- Epoch-increase escape hatch (04-CONTEXT.md): **not used** — 300 epochs throughout, per the original first-pass plan.
- Architecture/encoding: **option 3** — not a hyperparameter but a structural fix to the output correspondence (K=400→462, arbitrary index↔bin pairing → radius/center-of-mass rank pairing). This is architecture-adjacent tuning, documented in full in `DESIGN_DECISIONS.md`'s three 2026-07-25 entries and `.planning/STATE.md`.

## Mechanism behind option 3's improvement (for the record — full derivation in DESIGN_DECISIONS.md)

Radius-sorting the bins turns the two-ring target from 44 disjoint fragments (raster order) into ~2 large contiguous bands plus a few small grid-quantization artifacts (radius order) — verified by direct inspection of `p_real`, and confirmed to be caused by the *ordering*, not the fold removal, since the same collapse (44→7) happens on the old 400-bin grid too. The trained output's total variation in rank order dropped from 1.82 to 1.16, consistent with the circuit's natural output-space smoothness now approximately meaning "smooth in radius." The residual gap is attributed to `fock_state_sort_order`'s center-of-mass heuristic being weak (rank-domain correlation between p_real and q is only 0.38) — the most likely place further gains would come from, not pursued further this phase.

## Final judgment

**Owner's verdict, all three axes considered:** option 3 is "quite an improvement... still not two distinct rings, but an improvement." No axis tried (sigma, batch, or the structural correspondence fix) produced output a human would call two clean, distinct rings. The best available result (option 3, ring_mass=0.691) is a real, mechanistically-understood, and reproducible improvement over the documented baseline — but the honest outcome, per PROJECT.md's "don't gloss over it" rule, is that GEN-07's "recognizably forms two rings" bar is **not fully met**. It is best described as: partial ring structure with a measurably reduced (but non-zero) mismatch, not a clean two-ring generative result.
