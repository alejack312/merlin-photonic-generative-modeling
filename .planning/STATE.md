# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-07-19)

**Core value:** A working, end-to-end, honestly-benchmarked MMD-trained photonic generative model, published in a public repo before Sept 1, 2026 — explainable unaided to Vincent Espitalier.
**Current focus:** Phase 4 — Generative Quality (in progress)

## Current Position

Phase: 4 of 6 (Generative Quality) — IN PROGRESS
Plan: 2 of 3 done (04-02: full SIGMA_GRID sweep) — SUMMARY.md written
Status: Full tests/ suite passes 32/32 (unchanged by this plan). All 5 SIGMA_GRID values ([0.02, 0.05, 0.1, 0.2, 0.4]) retrained fresh, epochs/lr/batch_size fixed at Phase 3's values; results/phase4_sweep_metrics.csv and results/phase4_sweep_comparison.png produced. Combined figure shows all 5 sigmas as diffuse scatter, none clearly ring-like (sigma=0.1 has the highest ring_mass=0.616 of the 5, still visually diffuse) — this evidence carries into Plan 04-03's final GEN-07 checkpoint, which is next.
Last activity: 2026-07-25 — Completed 04-02-PLAN.md (sweep.py, results/phase4_sigma_*_checkpoint.pt x5, results/phase4_sweep_metrics.csv, results/phase4_sweep_comparison.png). No blocking checkpoint in this plan (autonomous).

Progress: [█████░░░░░] ~55% (3/6 phases complete, Phase 4 plan 2/3 done)

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

### Pending Todos

None yet.

### Blockers/Concerns

- **Stall-risk checkpoint RESOLVED**: July 25, 2026 was the explicit deadline for Phase 3 (End-to-End Training Run) — a historical stall pattern (prior PennyLane track stalled since May 2026). A real, working end-to-end training run with checked-in evidence (results/phase3_*) was completed 2026-07-24, one day ahead of the deadline. GEN-06 met.
- **Note for Phase 4**: the self-explanation checkpoint for train_step's mechanism required one correction (owner's first attempt conflated this project's continuous latent-noise MMD with a prior project's binary-bitstring MMD kernel) before the owner could explain it correctly. Worth double-checking this distinction stays clear going into Phase 4's evaluation work, which will build directly on the same MMD machinery.
- **Phase 4 in progress**: 04-01 and 04-02 done. Plan 04-03 (final GEN-07 human-verification checkpoint) is next and last for Phase 4 — it must review the combined sweep evidence (results/phase4_sweep_comparison.png, results/phase4_sweep_metrics.csv), which shows no sigma value producing a clean ring structure. This is a real, substantive finding the owner needs to weigh at that checkpoint (accept diffuse output as the honest result, or consider further changes) — not a formality.

## Session Continuity

Last session: 2026-07-25
Stopped at: Completed 04-02-PLAN.md (full SIGMA_GRID sweep). Ready for execute of 04-03 (final GEN-07 human-verification checkpoint).
Resume file: None
