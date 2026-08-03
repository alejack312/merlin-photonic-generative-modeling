# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-07-30)

**Core value:** A working, end-to-end, honestly-benchmarked MMD-trained photonic generative model, published in a public repo before Sept 1, 2026 — explainable unaided to Vincent Espitalier.
**Current focus:** v1.0 shipped 2026-07-29. Phase 7 (Mechanism Validation) closed 2026-07-30. v2.0 (IQP → Photonic Encoding) roadmap created 2026-07-30 — 2 phases (8: Literature Scoping & Prerequisites, 9: Encoding Design), 11 requirements, 100% coverage.

## Current Position

Milestone: v2.0 IQP → Photonic Encoding — started 2026-07-30 (v1.0 shipped 2026-07-29, tag: v1.0; Phase 7 mechanism-validation add-on closed 2026-07-30)
Phase: 8 (Literature Scoping & Prerequisites) — in progress
Plan: 03 of 3 complete (08-01 Douce et al. summary + go/no-go verdict, and 08-02 Perceval fluency demo, still outstanding — both `autonomous: false`, likely awaiting a checkpoint/owner attempt-first step separately)
Status: Plan 08-03 (qubit-side IQP baseline doc, PREQ-02) executed and committed. Roadmap scoped to exactly 2 phases matching the source plan doc's own Phase 0 (Literature Scoping) and Phase 1 (Encoding Design); implementation/trainability-study/write-up (v2 requirements: IMPL-01/02, STUDY-01/02, WRITE-01) deliberately deferred pending Phase 8's go/no-go verdict (LIT-04). Phase 9 (Encoding Design) is sequentially contingent on Phase 8 concluding "go" — will not be planned/executed if Phase 8 concludes "not ready."

Progress: [██████████] 100% of v1.0 (GEN-07 honestly concluded not-met within that 100% — not a partial-completion asterisk, the requirement was fully addressed, the outcome was negative). Phase 7 mechanism-validation work is fully closed. v2.0 Phase 8: [███░░░░░░░] 1/3 plans complete (08-03 done; 08-01, 08-02 outstanding). Phase 9 not yet planned.

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
- v2.0 encoding target is discrete-variable (DV, Fock-space: phase shifters/beamsplitters/photon-counting), not continuous-variable (CV, squeezed states/homodyne) — no published DV construction exists (genuinely novel), whereas Douce et al. (2017) already proved the CV-IQP hardness result (reproduction, not invention); DV also preserves IQP's native discrete bitstring-sampling character.
- `docs/iqp-baseline.md` (Phase 8 plan 03) compiles the qubit-side IQP structure/hardness (Van den Nest cosine-formula classical-training trick) and barren-plateau trainability (empirical rule: `plateau if small_angle OR (uniform AND n>=6 AND NOT complete_graph_like)`, 97.9% accuracy) baseline Phase 9 will compare its photonic encoding against — worth reading before starting Phase 9's design work rather than re-deriving from the sibling `iqp-mmd-barren-plateau` project's full paper stash.

### Roadmap Evolution

- Phase 7 added 2026-07-29: Mechanism Validation — neighbor-locality test (Jacobian-based) + sigma re-sweep against the K=462 grid, scoped from the v1.0 self-audit's tracked backlog. Not yet assigned to a milestone; added via `/gsd:add-phase` continuing numbering from v1.0 rather than restarting.
- v2.0 IQP → Photonic Encoding started 2026-07-30 via `/gsd:new-milestone`, continuing phase numbering from Phase 7 (new phases start at 8).
- v2.0 roadmap created 2026-07-30: exactly 2 phases (8: Literature Scoping & Prerequisites; 9: Encoding Design), derived directly from this milestone's 11 v1 requirements — matching the source plan doc's own Phase 0/Phase 1 split, not the doc's full 5-phase scope. Phase 9 is sequentially dependent on Phase 8's LIT-04 go/no-go verdict. 100% requirement coverage validated (11/11 mapped, no orphans). v2 requirements (IMPL-01/02, STUDY-01/02, WRITE-01) explicitly deferred, not phased.

### Pending Todos

- Owner: send the drafted technical note to Vincent Espitalier (`.planning/phases/06-documentation-publication/06-technical-note.md`, Phase 7 addendum already written in) — owner plans to send 2026-07-31
- Owner: flip the GitHub repo to public (`gh repo edit alejack312/merlin-photonic-generative-modeling --visibility public`)
- Next: `/gsd:plan-phase 8` to plan Literature Scoping & Prerequisites
- Backlog (not blocking, candidates for a future milestone): BMK-03 apples-to-apples QGAN comparison; v2.0's deferred Phases 2-4 (implementation, trainability/hardness study, write-up), contingent on this milestone's findings.

### Blockers/Concerns

None open. All prior blockers (the July 25 stall-risk checkpoint, Phase 4's GEN-07 shortfall, the self-audit findings) are resolved or honestly documented as closed — see `.planning/milestones/v1.0-ROADMAP.md` and `.planning/milestones/v1.0-MILESTONE-AUDIT.md`. One live contingency to track going forward: Phase 9 (Encoding Design) does not proceed if Phase 8 concludes "not ready" on LIT-04 — that would be a valid, honestly-reportable milestone outcome, not a blocker to work around.

## Session Continuity

Last session: 2026-08-03
Stopped at: Phase 8, plan 03 (`docs/iqp-baseline.md`) executed, committed (`99f6443`), and summarized. Plans 08-01 and 08-02 in this same wave are not yet complete (no SUMMARY.md, no committed deliverables beyond 08-01's Douce et al. doc) — resume there before considering Phase 8 closed and moving to the LIT-04 go/no-go gate for Phase 9.
Resume by: complete 08-01 (go/no-go verdict + Douce summary write-up, `autonomous: false`) and 08-02 (Perceval fluency demo, `autonomous: false`) — both likely need an owner attempt-first/checkpoint step per their plans. The two owner-only v1.0 todos (flip repo public, send technical note to Vincent) remain open and are independent of this milestone.
