# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-07-19)

**Core value:** A working, end-to-end, honestly-benchmarked MMD-trained photonic generative model, published in a public repo before Sept 1, 2026 — explainable unaided to Vincent Espitalier.
**Current focus:** Phase 4 — Generative Quality (in progress — 3rd tuning axis implemented and run, produced a real but partial improvement; 04-03 write-up/checkpoint not yet run)

## Current Position

Phase: 4 of 6 (Generative Quality) — IN PROGRESS
Plan: 2 of 3 formal plans done (04-02: full SIGMA_GRID sweep) — SUMMARY.md written. Plus two ad hoc (non-plan) tuning axes: a batch-size sweep, and "option 3" (natural-width matching + rank-based spatial correspondence), which is now IMPLEMENTED AND RUN. 04-03 (final write-up + GEN-07 checkpoint) NOT YET STARTED — no longer blocked; option 3 has concluded with a documented result.
Status: Two tuning rounds tried and ruled out. (1) SIGMA_GRID sweep (04-02, formal): sigma=0.1 best, ring_mass=0.616, owner-confirmed still not ring-like. (2) Batch-size sweep (ad hoc, batch_sweep.py, not a GSD plan): fixed sigma=0.1, batch ∈ {16,32,64,128} — batch=32 best (gap_mass=0.035), owner-confirmed still not ring-like (results/phase4_batch_sweep_comparison.png, results/phase4_batch_sweep_metrics.csv). While investigating a 3rd lever (increasing `input_size`), found a likely structural cause going beyond the `ModGrouping` fold: `quantum_layer.output_keys` (raw circuit output ordering, photon-occupation combinatorics) has NO designed relationship to `bin_centers.py`'s (x,y) raster ordering — the correspondence between "which raw circuit output index" and "which spatial bin" is arbitrary, not just folded. Researched two candidate fixes directly against MerLin's docs/source: CircuitBuilder (deeper circuit, real but only marginally reduces the fold, real lever is depth as a capacity bet) vs. a custom output mapping (MerLin's `OutputAdapter`/`output_keys` are exposed for exactly this, `output_size=None` gives the raw unfolded vector). Owner chose the custom-mapping path ("option 3"): match K to the natural width (462, eliminates the fold) + sort bin-centers by radius and raw Fock states by center-of-mass, pair by rank (replaces the arbitrary correspondence with a designed one, motivated by the two-concentric-rings target). (3) Option 3 IMPLEMENTED AND RUN at identical hyperparameters (sigma=0.1, batch=32, 300 epochs, LR=0.01, K=462): **ring_mass 0.609 → 0.691, gap_mass 0.035 → 0.048**, stable across 20 latent draws (0.684±0.008 vs 0.613±0.004, non-overlapping ranges). Owner's visual verdict: "quite an improvement. Still not two distinct rings, but an improvement." Mechanism measured post-hoc: radius sorting collapses p_real from 44 disjoint runs to ~6 (44→7 even on the old 400-grid, isolating ordering from fold removal — the ordering, not the fold, was carrying most of the damage); trained q's total variation dropped 1.82 → 1.16. Known limits: two changes made at once (no single-variable ablation), and rank-domain corr(p_real, q) is only 0.38, so `fock_state_sort_order`'s center-of-mass heuristic remains the weakest link and the likeliest place further gains hide. Full narrative: DESIGN_DECISIONS.md's three 2026-07-25 entries.
Last activity: 2026-07-25 — Implemented the approved option-3 plan (generator/natural_grid.py, generator/spatial_alignment.py, generator/naturally_ordered_generator.py, natural_order_train.py, 3 test files / 16 tests). Full suite 48 passed, zero regressions. Training run completed in the foreground (loss 0.0403 → 0.0026). Owner reviewed both figures and gave the verdict above; DESIGN_DECISIONS.md's third 2026-07-25 entry records the result, the mechanism, and the confounds. All option-3 files + results/phase4_natural_* + batch_sweep.py + results/phase4_batch_sweep_* + DESIGN_DECISIONS.md entries remain uncommitted (per "ask before commit" rule).

Progress: [█████░░░░░] ~58% (3/6 phases complete, Phase 4 — 3 tuning axes tried, best result improved but still not ring-like; 04-03 checkpoint is the next step)

## Performance Metrics

**Velocity:**
- Total plans completed: 0 (Phase 1 predates plan-based tracking)
- Average duration: -
- Total execution time: -

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1. Environment & Architecture Foundation | - | - | - |

**Recent Trend:**
- Last 5 plans: -
- Trend: -

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Phase 1: Extend quickstart classifier into an MMD generator (not reproduce a catalog paper directly) — reuses owner's MMD/generative-modeling background, gives a natural comparison point.
- Phase 1: Generator output = full-distribution/histogram matching via closed-form MMD² — avoids collapsing the circles' two-ring target into its empty middle, avoids non-differentiable discrete sampling.
- Phase 1: Python 3.12 venv used instead of system default 3.13 — required by MerLin's `torch<2.13` + `python<=3.12` constraints.
- Phase 2 (02-02): Tensor-value pytest assertions use `torch.allclose`/`torch.equal`, never `pytest.approx` — `pytest.approx` without `==` doesn't compare anything, and its internal handling breaks on tensors with `requires_grad=True` (which any `QuantumLayer` output has). Full detail: `~/.claude/learnings/2026-07-19-pytest-approx-misuse-grad-tensor.md`.
- Phase 2 (02-04): `generator/mmd.py`'s `mmd2`/`gaussian_kernel_matrix` must be pure `torch` (`cdist`/`exp`/`@`), never `numpy` — `q` comes from a trainable `QuantumLayer` forward pass, and any numpy operation on it severs PyTorch's autograd graph, silently producing a loss that looks fine (finite, non-negative) but never actually trains the circuit.
- Phase 2 (02-04): `torch.cdist(x, x)` is not bit-exact symmetric and its diagonal is not bit-exact 0 (float32 cancellation in its internal distance formula) — both get amplified by a Gaussian kernel's `/(2σ²)` at small σ. Measured: ~1e-6 symmetry / ~5e-4 diagonal noise from cdist itself, ~1e-5 / ~3e-4 after the kernel at σ=0.02. Use `atol=1e-4`/`1e-3` on symmetry/diagonal checks over such a kernel, not `torch.allclose` defaults.
- Phase 3 (03-01): Batch-reduction strategy (average per-sample MMD² losses across a batch of fresh `z`, one shared θ, DESIGN_DECISIONS.md 2026-07-24) is now empirically validated, not just literature-motivated — real run produced a statistically clean decreasing trend (p≈1e-128) at the first-attempt lr=0.01, no LR escalation needed.
- Phase 3 (03-01): lr=0.01 (quickstart.py-informed default) was sufficient on the first real run — the planned lr=0.05/0.1 escalation path for a possible flat first attempt was not exercised.
- Phase 4 (04-01): Checkpoint decision — sigma=0.1's generated distribution is not ring-like enough (diffuse scatter/heatmap, ring_mass=0.602/0.572 exact/sampled, gap_mass=0.034/0.030); owner selected **sweep-needed**, so Plan 04-02's full SIGMA_GRID sweep (~12 min, all 5 sigma values, fixed epochs/lr/batch_size) is required before Plan 04-03's final GEN-07 checkpoint.
- Phase 4 (04-02): Full sweep completed — none of the 5 SIGMA_GRID values produced a visually ring-like generated distribution (all diffuse across the square); sigma=0.1 has the highest ring_mass (0.616) but is still not clean. Plan 04-03's final GEN-07 checkpoint must weigh this combined evidence, not just one sigma.
- Phase 4 (04-02): Backgrounded ~12-14 min training scripts did not reliably survive across tool-call turns in this execution environment (process was silently killed mid-sweep with no captured error). `sweep.py` was made resumable (skip retraining a sigma whose checkpoint already exists) as the general-purpose fix — worth reusing this pattern for any future long-running script in this repo rather than relying on a single uninterrupted backgrounded run.
- Phase 4 (ad hoc, 2026-07-25): Batch-size sweep at sigma=0.1 (batch ∈ {16,32,64,128}) does not fix ring structure either — batch=32 stays best (owner visually confirmed none of the 4 look meaningfully closer to two rings). Batch size ruled out as the lever.
- Phase 4 (ad hoc, 2026-07-25): `QuantumLayer.simple`'s `ModGrouping` post-processing (462 natural width → 400 via index-modulo-400 sum, unrelated to spatial bin adjacency) means increasing `input_size` past 10 makes the fold strictly worse, not better — `input_size=10` (current) is already the least-folded option covering all 400 bins. Naively "increasing circuit size" via `input_size` was flagged to the owner as counterproductive before implementing it. See DESIGN_DECISIONS.md 2026-07-25 entry (first of two).
- Phase 4 (ad hoc, 2026-07-25): Deeper root cause found — `output_keys`' raw ordering (photon-occupation combinatorics) has no designed relationship to bin_centers.py's spatial ordering, so even unfolded bins get an arbitrary spatial label. Researched CircuitBuilder (option 2) vs. custom output mapping via `OutputAdapter`/`output_keys`/`output_size=None` (option 3) directly against MerLin's docs/source. Owner chose option 3: K=462 (no fold) + radius-sorted centers paired by rank with center-of-mass-sorted Fock states. Plan approved (`C:\Users\cuqui\.claude\plans\plan-option-3-dynamic-bunny.md`) and implemented. See DESIGN_DECISIONS.md 2026-07-25 entry (second of three).
- Phase 4 (ad hoc, 2026-07-25): Option 3 result — ring_mass 0.609 → 0.691, owner-confirmed "an improvement, still not two distinct rings." The measurable reason: sorting bins by radius turns the ring target from 44 disjoint fragments into ~6 contiguous bands in the 1-D vector the model actually outputs, so a smooth output has far less high-frequency structure to fight. Verified this collapse is caused by the ordering, not the fold removal (44→7 on the old 400-bin grid too). The residual gap is attributed to `fock_state_sort_order`'s center-of-mass smoothness heuristic being weak — rank-domain corr(p_real, q) = 0.38. See DESIGN_DECISIONS.md 2026-07-25 entry (third of three).

### Pending Todos

None yet.

### Blockers/Concerns

- **Stall-risk checkpoint RESOLVED**: July 25, 2026 was the explicit deadline for Phase 3 (End-to-End Training Run) — a historical stall pattern (prior PennyLane track stalled since May 2026). A real, working end-to-end training run with checked-in evidence (results/phase3_*) was completed 2026-07-24, one day ahead of the deadline. GEN-06 met.
- **Note for Phase 4**: the self-explanation checkpoint for train_step's mechanism required one correction (owner's first attempt conflated this project's continuous latent-noise MMD with a prior project's binary-bitstring MMD kernel) before the owner could explain it correctly. Worth double-checking this distinction stays clear going into Phase 4's evaluation work, which will build directly on the same MMD machinery.
- **Phase 4 in progress, three tuning axes now complete**: 04-01, 04-02, the ad hoc batch-size sweep, and option 3 (natural-width matching + rank-based spatial correspondence, ring_mass 0.609 → 0.691, improved but still not ring-like). Plan 04-03 must review ALL of this combined evidence when it runs, not just the sigma sweep — this is a real, substantive finding the owner needs to weigh (accept diffuse output as the honest documented result, or the option-3 fix works) — not a formality. Per PROJECT.md's "don't gloss over it" rule, if option 3 is tried and still doesn't work, that must also be reported plainly in 04-03.

## Session Continuity

Last session: 2026-07-25
Stopped at: Three tuning axes complete (sigma sweep 04-02, batch-size sweep, option 3). Option 3 improved ring_mass 0.609 → 0.691 and is documented; next step is 04-03 (final write-up + GEN-07 checkpoint), weighing all three axes. Historical context below.
Prior context: Sigma sweep (04-02) and ad hoc batch-size sweep both complete and ruled out. ModGrouping fold + arbitrary output-index/spatial-bin correspondence both diagnosed. CircuitBuilder (option 2) vs. custom output mapping (option 3) researched against MerLin's actual docs/source; owner chose option 3. Full implementation plan written and approved via ExitPlanMode (`C:\Users\cuqui\.claude\plans\plan-option-3-dynamic-bunny.md`). That plan has since been implemented in full and run; its result is recorded above and in DESIGN_DECISIONS.md's third 2026-07-25 entry.
Resume by: running 04-03 (final write-up + GEN-07 checkpoint) against all three tuning axes. Optional cheap follow-up if the option-3 attribution ever needs defending precisely: a single-variable ablation (reorder only, or de-fold only) — not run.
Resume file: .planning/phases/04-generative-quality/ (04-03)
