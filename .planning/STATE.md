# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-07-19)

**Core value:** A working, end-to-end, honestly-benchmarked MMD-trained photonic generative model, published in a public repo before Sept 1, 2026 — explainable unaided to Vincent Espitalier.
**Current focus:** Phase 3 — End-to-End Training Run (next up)

## Current Position

Phase: 2 of 6 (Generator Data & Loss Infrastructure) — COMPLETE
Plan: 4 of 4 done (bin-centers, noise, p_real, MMD²) — all with SUMMARY.md written
Status: Full tests/ suite passes 24/24 across all four plans together. Still uncommitted — commit before starting Phase 3 (/gsd:plan-phase 3)
Last activity: 2026-07-19 — Implemented and reviewed GEN-05 (generator/mmd.py, tests/test_mmd.py); fixed a numpy-vs-torch differentiability bug (would have silently severed gradient flow to the QuantumLayer), a broken test file (wrong import, undefined name, duplicate QuantumLayer instances defeating the gradient-flow check), and two measured torch.cdist float32 tolerance issues (see 02-04-SUMMARY.md)

Progress: [███░░░░░░░] ~33% (2/6 phases complete)

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

### Pending Todos

None yet.

### Blockers/Concerns

- **Stall-risk checkpoint**: July 25, 2026 is the explicit deadline for Phase 3 (End-to-End Training Run). PROJECT.md names this as a historical stall pattern (prior PennyLane track stalled since May 2026) — if no end-to-end run exists by then, name it plainly rather than glossing over it.

## Session Continuity

Last session: 2026-07-19
Stopped at: Roadmap and traceability created; ready to begin `/gsd:plan-phase 2`
Resume file: None
