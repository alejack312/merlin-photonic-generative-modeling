# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-07-19)

**Core value:** A working, end-to-end, honestly-benchmarked MMD-trained photonic generative model, published in a public repo before Sept 1, 2026 — explainable unaided to Vincent Espitalier.
**Current focus:** Phase 3 — End-to-End Training Run (next up)

## Current Position

Phase: 3 of 6 (End-to-End Training Run) — COMPLETE
Plan: 1 of 1 done (03-01: training loop + real run) — SUMMARY.md written
Status: Full tests/ suite passes 28/28 (Phase 2's 24 + Phase 3's 4). GEN-06 met: real 300-epoch training run completed, decreasing_trend_check passed=True (62% relative drop). Ready for /gsd:plan-phase 4.
Last activity: 2026-07-24 — Completed 03-01-PLAN.md (generator/train.py, train.py, results/phase3_*). Self-explanation checkpoint required one correction (owner initially conflated continuous latent z with a prior project's bitstring MMD kernel; corrected and re-confirmed) before approval — see 03-01-SUMMARY.md "Issues Encountered".

Progress: [█████░░░░░] ~50% (3/6 phases complete)

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

### Pending Todos

None yet.

### Blockers/Concerns

- **Stall-risk checkpoint RESOLVED**: July 25, 2026 was the explicit deadline for Phase 3 (End-to-End Training Run) — a historical stall pattern (prior PennyLane track stalled since May 2026). A real, working end-to-end training run with checked-in evidence (results/phase3_*) was completed 2026-07-24, one day ahead of the deadline. GEN-06 met.
- **Note for Phase 4**: the self-explanation checkpoint for train_step's mechanism required one correction (owner's first attempt conflated this project's continuous latent-noise MMD with a prior project's binary-bitstring MMD kernel) before the owner could explain it correctly. Worth double-checking this distinction stays clear going into Phase 4's evaluation work, which will build directly on the same MMD machinery.

## Session Continuity

Last session: 2026-07-24
Stopped at: Completed 03-01-PLAN.md (Phase 3, End-to-End Training Run) — GEN-06 met
Resume file: None
