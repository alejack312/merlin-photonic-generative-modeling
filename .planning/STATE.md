# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-07-29)

**Core value:** A working, end-to-end, honestly-benchmarked MMD-trained photonic generative model, published in a public repo before Sept 1, 2026 — explainable unaided to Vincent Espitalier.
**Current focus:** v1.0 shipped 2026-07-29. Phase 7 (Mechanism Validation) added 2026-07-29, completed and verified 2026-07-30, not yet assigned to a milestone.

## Current Position

Milestone: v1.0 Photonic Generator — SHIPPED 2026-07-29 (tag: v1.0)
Phase: 7 (Mechanism Validation) — COMPLETE. Both plans executed, gsd-verifier passed 10/10 must-haves, gstack `/review` adversarial pass ran (Codex timed out, Claude subagent fallback per skill policy) and found 4 issues, all resolved: K<4 hang guard, misleading LR comment, and sign_agrees CSV column auto-fixed; deterministic per-sigma resweep seeding and a pooled-p-value independence caveat applied after owner approval via AskUserQuestion.
Status: Neighbor-locality test executed and committed. Measured result: pooled mean_diff=+0.0096 and trained-checkpoint mean_diff=+0.0402 both fail the locked 0.10 effect-size bar despite the pooled result clearing p<0.05 alone (see 07-01-SUMMARY.md and results/phase7_neighbor_locality_summary.md). Sigma re-sweep executed and committed: K=462 argmax is sigma=0.1 (ring_mass=0.7145), matching the bandwidth already in use for every reported K=462 result — no other tested sigma value beats it (see 07-02-SUMMARY.md and results/phase7_sigma_resweep_summary.md). Owner interpretation of both results is now written into both summary docs (commits 1d7b113, ca6d295) — Phase 7 is fully closed. Neighbor-locality conclusion: the effect is real (p=0.0084 pooled) but ~10x too small to be practically meaningful (mean_diff=0.0096 vs. min_effect=0.10) — the correspondence-fix mechanism is not confirmed by this test. Sigma re-sweep conclusion: no stale-sigma confound (sigma=0.1 remains the K=462 argmax by a wide margin), but K=400→K=462 is a tradeoff, not a clean win — gap_mass worsened at every single sigma even as ring_mass improved at 4/5.

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
- Resumable per-run scripts that draw random inits from the global unseeded RNG (e.g. `torch.randn` without a preceding `torch.manual_seed`) are not actually reproducible across a resume: completed steps skip the RNG draw on reload, so any step retrained after a resume point diverges silently from what an uninterrupted run would have produced. Seed deterministically per resumable unit (e.g. `torch.manual_seed(base + index)`) if resume-reproducibility matters — caught by adversarial code review in Phase 7, fixed in `sigma_resweep.py`.
- Pooling non-independent samples (e.g. adjacent-pair cosine similarities that share a row with their neighbor) into a single significance test overstates effective sample size and can make a p-value look stronger than it is — worth a stated caveat rather than a silent pooled claim; doesn't necessarily change a verdict decided by a separate effect-size threshold, but should be flagged.

### Roadmap Evolution

- Phase 7 added 2026-07-29: Mechanism Validation — neighbor-locality test (Jacobian-based) + sigma re-sweep against the K=462 grid, scoped from the v1.0 self-audit's tracked backlog. Not yet assigned to a milestone; added via `/gsd:add-phase` continuing numbering from v1.0 rather than restarting.

### Pending Todos

- Owner: send the drafted technical note to Vincent Espitalier (`.planning/phases/06-documentation-publication/06-technical-note.md`, Phase 7 addendum already written in) — owner plans to send 2026-07-31
- Backlog (not blocking, candidates for a future milestone): BMK-03 apples-to-apples QGAN comparison; the deferred IQP→photonic circuit mapping project.

### Blockers/Concerns

None open. All prior blockers (the July 25 stall-risk checkpoint, Phase 4's GEN-07 shortfall, the self-audit findings) are resolved or honestly documented as closed — see `.planning/milestones/v1.0-ROADMAP.md` and `.planning/milestones/v1.0-MILESTONE-AUDIT.md`.

## Session Continuity

Last session: 2026-07-30
Stopped at: Phase 7 fully complete — executed, verified (10/10 must-haves, gsd-verifier), code-reviewed (gstack `/review`, adversarial fixes applied and re-tested, 53/53 tests pass), and interpreted (owner wrote both interpretations through two rounds of Claude checking the framing against the actual numbers per this project's CLAUDE.md rule; final versions committed 1d7b113, ca6d295). Nothing left queued in Phase 7.
Resume by: `/gsd:new-milestone` for a next goal, or the two remaining owner-only todos above (flip repo public, send technical note to Vincent — consider a Phase 7 addendum first).
