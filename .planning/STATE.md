# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-07-29)

**Core value:** A working, end-to-end, honestly-benchmarked MMD-trained photonic generative model, published in a public repo before Sept 1, 2026 — explainable unaided to Vincent Espitalier.
**Current focus:** v1.0 shipped 2026-07-29. Phase 7 (Mechanism Validation) added 2026-07-29, not yet assigned to a milestone.

## Current Position

Milestone: v1.0 Photonic Generator — SHIPPED 2026-07-29 (tag: v1.0)
Phase: 7 (Mechanism Validation) — Plan 01 (neighbor-locality test, Method B) complete. Plan 02 (sigma re-sweep) not yet started.
Status: Neighbor-locality test executed and committed. Measured result: pooled mean_diff=+0.0096 and trained-checkpoint mean_diff=+0.0402 both fail the locked 0.10 effect-size bar despite the pooled result clearing p<0.05 alone (see 07-01-SUMMARY.md and results/phase7_neighbor_locality_summary.md). Interpretation is intentionally left for the owner — not yet done. Sigma re-sweep (Phase 7's second experiment) is next if the owner proceeds.

Progress: [██████████] 100% of v1.0 (GEN-07 honestly concluded not-met within that 100% — not a partial-completion asterisk, the requirement was fully addressed, the outcome was negative). Phase 7 is post-v1.0 mechanism-validation work, tracked separately above.

## Performance Metrics

**v1.0 milestone:**
- Phases: 6
- Plans: 11
- Commits: 51
- Files touched: 103 (7,624 insertions, 56 deletions)
- LOC: 1,648 Python
- Timeline: 10 days (2026-07-19 → 2026-07-29)

## Accumulated Context

### Decisions

Full decision log archived in `.planning/PROJECT.md`'s Key Decisions table and `.planning/milestones/v1.0-ROADMAP.md`'s Milestone Summary. Highlights carried forward for any future work on this codebase:

- Batch-averaged per-sample MMD² training objective is a provable upper bound on the marginal-distribution MMD² (Jensen's inequality on the convex kernel term), not identical to it — documented in `DESIGN_DECISIONS.md`, worth knowing before extending the training loop.
- Natural-order correspondence's causal mechanism (why radius-sorting helps) is asserted, not demonstrated — a genuine open question, not a settled fact, if this generator is extended or reused.
- MerLin ships its own `PhotonicGenerator`/`OutputAdapter` extension point (`merlin.models.photonic_generator`) — worth using directly (via a custom `OutputAdapter` subclass) rather than hand-rolling a training loop, if this codebase is extended.
- `torch.cdist` symmetry/diagonal float32 noise (~1e-6/~5e-4) needs `atol=1e-4`/`1e-3` in tests over a Gaussian kernel at small σ, not `torch.allclose` defaults.
- Backgrounded long-running training/build scripts did not reliably survive across tool-call turns in this execution environment — resumable scripts (skip-if-checkpoint-exists) are the general-purpose fix, reusable for any future long-running work here.
- Windows Next.js builds that fail mid-trace-collection with ENOENT/MODULE_NOT_FOUND on files just written are often disk-space exhaustion, not a code bug — check `df -h` before debugging the diff (full pattern: `~/.claude/learnings/2026-07-29-windows-nextjs-build-disk-space.md`).
- `torch.func.functional_call` + `jacrev` against MerLin's `QuantumLayer` silently produces an all-zero Jacobian: `QuantumLayer` reads trainable parameters from a plain Python list (`quantum_layer.thetas`) populated once at construction, not from named-parameter attributes on each call, so `functional_call`'s attribute substitution never reaches it. Fix: also monkey-patch `quantum_layer.thetas` inside the `jacrev`-traced closure (see `generator/neighbor_locality.py`'s `compute_jacobian` docstring). Worth knowing before any future `torch.func` differentiation against a MerLin `QuantumLayer`.

### Roadmap Evolution

- Phase 7 added 2026-07-29: Mechanism Validation — neighbor-locality test (Jacobian-based) + sigma re-sweep against the K=462 grid, scoped from the v1.0 self-audit's tracked backlog. Not yet assigned to a milestone; added via `/gsd:add-phase` continuing numbering from v1.0 rather than restarting.

### Pending Todos

- Owner: flip GitHub repo to public (`gh repo edit alejack312/merlin-photonic-generative-modeling --visibility public`)
- Owner: send the drafted technical note to Vincent Espitalier (`.planning/phases/06-documentation-publication/06-technical-note.md`)
- Owner: interpret the neighbor-locality test result (`results/phase7_neighbor_locality_summary.md`'s "Interpretation" section is intentionally left blank — pooled mean_diff=+0.0096 and trained-checkpoint mean_diff=+0.0402 both fail the locked 0.10 effect-size bar)
- Phase 7 (Mechanism Validation): sigma re-sweep (Plan 02, not yet started) — the second of the two experiments, per owner's ad hoc direction
- Backlog (not blocking, candidates for a future milestone): BMK-03 apples-to-apples QGAN comparison; the deferred IQP→photonic circuit mapping project.

### Blockers/Concerns

None open. All prior blockers (the July 25 stall-risk checkpoint, Phase 4's GEN-07 shortfall, the self-audit findings) are resolved or honestly documented as closed — see `.planning/milestones/v1.0-ROADMAP.md` and `.planning/milestones/v1.0-MILESTONE-AUDIT.md`.

## Session Continuity

Last session: 2026-07-29
Stopped at: Completed 07-01-PLAN.md (neighbor-locality test). Owner interpretation of the result is pending.
Resume by: sigma re-sweep (Phase 7's second experiment) if the owner proceeds, or `/gsd:new-milestone` for a next goal.
