# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-07-19)

**Core value:** A working, end-to-end, honestly-benchmarked MMD-trained photonic generative model, published in a public repo before Sept 1, 2026 — explainable unaided to Vincent Espitalier.
**Current focus:** Phase 5 — Benchmarking (starting). Phase 4 CONCLUDED 2026-07-25 — GEN-07 not met (owner-confirmed).

## Current Position

Phase: 5 of 6 (Benchmarking) — STARTING
Phase 4 (Generative Quality) is CLOSED. All 3 formal plans done (04-01, 04-02, 04-03) plus 2 ad hoc tuning axes (batch-size sweep, "option 3" natural-order correspondence). Final checkpoint (04-03) taken 2026-07-25: owner's verbatim response — **"GEN-07 not met, move to Phase 5."** `results/phase4_summary.md` and `.planning/phases/04-generative-quality/04-03-SUMMARY.md` record the full evidence and verdict.
Status: Two tuning rounds tried and ruled out. (1) SIGMA_GRID sweep (04-02, formal): sigma=0.1 best, ring_mass=0.616, owner-confirmed still not ring-like. (2) Batch-size sweep (ad hoc, batch_sweep.py, not a GSD plan): fixed sigma=0.1, batch ∈ {16,32,64,128} — batch=32 best (gap_mass=0.035), owner-confirmed still not ring-like (results/phase4_batch_sweep_comparison.png, results/phase4_batch_sweep_metrics.csv). While investigating a 3rd lever (increasing `input_size`), found a likely structural cause going beyond the `ModGrouping` fold: `quantum_layer.output_keys` (raw circuit output ordering, photon-occupation combinatorics) has NO designed relationship to `bin_centers.py`'s (x,y) raster ordering — the correspondence between "which raw circuit output index" and "which spatial bin" is arbitrary, not just folded. Researched two candidate fixes directly against MerLin's docs/source: CircuitBuilder (deeper circuit, real but only marginally reduces the fold, real lever is depth as a capacity bet) vs. a custom output mapping (MerLin's `OutputAdapter`/`output_keys` are exposed for exactly this, `output_size=None` gives the raw unfolded vector). Owner chose the custom-mapping path ("option 3"): match K to the natural width (462, eliminates the fold) + sort bin-centers by radius and raw Fock states by center-of-mass, pair by rank (replaces the arbitrary correspondence with a designed one, motivated by the two-concentric-rings target). (3) Option 3 IMPLEMENTED AND RUN at identical hyperparameters (sigma=0.1, batch=32, 300 epochs, LR=0.01, K=462): **ring_mass 0.609 → 0.691, gap_mass 0.035 → 0.048**, stable across 20 latent draws (0.684±0.008 vs 0.613±0.004, non-overlapping ranges). Owner's visual verdict: "quite an improvement. Still not two distinct rings, but an improvement." Mechanism measured post-hoc: radius sorting collapses p_real from 44 disjoint runs to ~6 (44→7 even on the old 400-grid, isolating ordering from fold removal — the ordering, not the fold, was carrying most of the damage); trained q's total variation dropped 1.82 → 1.16. Known limits: two changes made at once (no single-variable ablation), and rank-domain corr(p_real, q) is only 0.38, so `fock_state_sort_order`'s center-of-mass heuristic remains the weakest link and the likeliest place further gains hide. Full narrative: DESIGN_DECISIONS.md's three 2026-07-25 entries.
Last activity: 2026-07-25 — Committed all option-3 + batch-sweep code, tests, and results (`83c4d7c`). Wrote `results/phase4_summary.md` aggregating all three tuning axes. Owner reviewed the mechanism (asked for and received a Feynman-technique re-explanation of why radius-sorting helps) and a comparison against MerLin's quickstart classifier (found to be a weak baseline itself — 46-64% test accuracy across repeated runs, not a strong reference point) before giving the final checkpoint verdict: GEN-07 not met, proceed to Phase 5. `.planning/phases/04-generative-quality/04-03-SUMMARY.md` and this STATE.md update, plus ROADMAP.md's Phase 4 closure, are pending commit.

Progress: [██████░░░░] ~60% (3/6 phases fully complete; Phase 4 concluded but NOT successful — GEN-07 not met, honestly documented; Phase 5 starting)

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
- Phase 4 (04-03, final checkpoint, 2026-07-25): **GEN-07 not met.** Owner's verbatim response: "GEN-07 not met, move to Phase 5." Reached after the owner independently re-derived the radius-sorting mechanism via a Feynman-technique explanation, and after checking whether MMD loss itself was the culprit by running MerLin's quickstart classifier directly — found it to be a weak baseline itself (46-64% test accuracy across repeated runs on an easily-separable dataset), so the shortfall is attributed mainly to task structure (unsupervised full-distribution generation from coordinate-free noise vs. supervised low-information discrimination fed real coordinates), not primarily to the loss function. Phase 4 closed; Phase 5 (Benchmarking) begins carrying this not-met result forward honestly.

### Pending Todos

None yet.

### Blockers/Concerns

- **Stall-risk checkpoint RESOLVED**: July 25, 2026 was the explicit deadline for Phase 3 (End-to-End Training Run) — a historical stall pattern (prior PennyLane track stalled since May 2026). A real, working end-to-end training run with checked-in evidence (results/phase3_*) was completed 2026-07-24, one day ahead of the deadline. GEN-06 met.
- **Note for Phase 4**: the self-explanation checkpoint for train_step's mechanism required one correction (owner's first attempt conflated this project's continuous latent-noise MMD with a prior project's binary-bitstring MMD kernel) before the owner could explain it correctly. Worth double-checking this distinction stays clear going into Phase 4's evaluation work, which will build directly on the same MMD machinery.
- **Phase 4 CLOSED, GEN-07 not met (owner-confirmed 2026-07-25)**: three tuning axes tried (sigma sweep, batch sweep, option 3 natural-order correspondence). Best result: ring_mass 0.609 → 0.691 — a real, mechanistically-verified improvement, but not two recognizable rings. Full evidence in `results/phase4_summary.md`. Phase 5's benchmarking work is therefore against an imperfect generator, and that context must carry forward honestly into Phase 5's write-up, not be implied away.
- **Phase 5 not yet started**: no research/context/plan files exist yet for Phase 5 (Benchmarking, requirements BMK-01/BMK-02). Needs `/gsd:plan-phase` or equivalent to produce 05-CONTEXT.md/05-RESEARCH.md/05-01-PLAN.md before execution.

## Session Continuity

Last session: 2026-07-25
Stopped at: Phase 4 formally closed. `results/phase4_summary.md` and `.planning/phases/04-generative-quality/04-03-SUMMARY.md` written; ROADMAP.md and this file updated to reflect GEN-07 not met and move focus to Phase 5. Pending: commit these doc updates (04-03-SUMMARY.md, STATE.md, ROADMAP.md).
Prior context (Phase 4, for reference): Sigma sweep (04-02), ad hoc batch-size sweep, and "option 3" (natural-order spatial correspondence — K=462, radius/center-of-mass rank pairing) all tried. Option 3 was the best result (ring_mass 0.609 → 0.691) but still owner-judged not ring-like. Full narrative: DESIGN_DECISIONS.md's three 2026-07-25 entries.
Resume by: starting Phase 5 (Benchmarking) — likely `/gsd:plan-phase` to produce 05-CONTEXT.md/05-RESEARCH.md/05-01-PLAN.md against requirements BMK-01 (held-out MMD benchmark statistic) and BMK-02 (comparison against MerLin's photonic QGAN reproduction, paper #16).
Resume file: .planning/phases/05-benchmarking/ (does not exist yet — first Phase 5 artifact to create)
