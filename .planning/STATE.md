# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-07-30)

**Core value:** A working, end-to-end, honestly-benchmarked MMD-trained photonic generative model, published in a public repo before Sept 1, 2026 — explainable unaided to Vincent Espitalier.
**Current focus:** v1.0 shipped 2026-07-29. Phase 7 (Mechanism Validation) closed 2026-07-30. v2.0 (IQP → Photonic Encoding) roadmap created 2026-07-30 — 2 phases (8: Literature Scoping & Prerequisites, 9: Encoding Design), 11 requirements, 100% coverage.

## Current Position

Milestone: v2.0 IQP → Photonic Encoding — started 2026-07-30 (v1.0 shipped 2026-07-29, tag: v1.0; Phase 7 mechanism-validation add-on closed 2026-07-30)
Phase: 8 (Literature Scoping & Prerequisites) — complete
Plan: 3 of 3 complete (08-01 Douce et al. summary + go/no-go verdict closed 2026-08-04)
Status: All three Phase 8 plans executed and committed: 08-02 (Perceval fluency demo, PREQ-01), 08-03 (qubit-side IQP baseline doc, PREQ-02), 08-01 (Douce et al. summary, independent literature search pass, and LIT-04 go/no-go verdict). LIT-04 verdict: **Go** — no blocking impossibility result against a DV/Fock-space IQP construction found across two independent search passes plus a full owner read of the closest tangential paper (Kurkin et al.'s BSBM, arXiv:2603.11014). Phase 9 (Encoding Design) is now unblocked.

Progress: [██████████] 100% of v1.0 (GEN-07 honestly concluded not-met within that 100% — not a partial-completion asterisk, the requirement was fully addressed, the outcome was negative). Phase 7 mechanism-validation work is fully closed. v2.0 Phase 8: [██████████] 3/3 plans complete. Phase 9 not yet planned — unblocked, ready to plan.

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
- `perceval_fluency_demo.py` (Phase 8 plan 02, PREQ-01) confirms low-level Perceval fluency: manual `Circuit`/`BS.H`/`Processor`/`Analyzer` build, no `QuantumLayer.simple()`, both the single-photon 50/50 split and Hong-Ou-Mandel dip verified programmatically via `numpy.isclose`. Two environment gotchas worth carrying into Phase 9's less-trivial circuits: `circuit.add(port, component)` takes a starting port index (int), not a port range/tuple; and `pcvl.pdisplay()`'s box-drawing output needs `PYTHONIOENCODING=utf-8` set on this Windows machine or it raises `UnicodeEncodeError`.
- `docs/iqp-lit-scoping.md` (Phase 8 plan 01, LIT-01/LIT-02/LIT-04) records the phase's gating decision: **Go** on proceeding to Phase 9. No DV/Fock-space linear-optical IQP construction and no impossibility result exists in the literature, across `08-RESEARCH.md`'s original WebSearch pass and a second, independently-conducted arXiv-API + Semantic-Scholar-citation-graph pass. Douce et al. (2017)'s CV-IQP hardness result is built in the continuous-quadrature formalism (squeezed light + homodyne), a different formalism from Fock-space/photon-number linear optics — it neither proves nor disproves anything about a DV construction. Kurkin et al.'s Boson Sampling Born Machine (arXiv:2603.11014) is the closest tangential paper found but doesn't match: it borrows IQP-QCBM's training recipe but derives hardness from ordinary boson-sampling permanent-hardness (Aaronson-Arkhipov), not IQP's own commuting-diagonal-gate structure in Fock space — worth citing in Phase 9 as context, not as a blocker.

### Roadmap Evolution

- Phase 7 added 2026-07-29: Mechanism Validation — neighbor-locality test (Jacobian-based) + sigma re-sweep against the K=462 grid, scoped from the v1.0 self-audit's tracked backlog. Not yet assigned to a milestone; added via `/gsd:add-phase` continuing numbering from v1.0 rather than restarting.
- v2.0 IQP → Photonic Encoding started 2026-07-30 via `/gsd:new-milestone`, continuing phase numbering from Phase 7 (new phases start at 8).
- v2.0 roadmap created 2026-07-30: exactly 2 phases (8: Literature Scoping & Prerequisites; 9: Encoding Design), derived directly from this milestone's 11 v1 requirements — matching the source plan doc's own Phase 0/Phase 1 split, not the doc's full 5-phase scope. Phase 9 is sequentially dependent on Phase 8's LIT-04 go/no-go verdict. 100% requirement coverage validated (11/11 mapped, no orphans). v2 requirements (IMPL-01/02, STUDY-01/02, WRITE-01) explicitly deferred, not phased.

### Pending Todos

- Owner: send the drafted technical note to Vincent Espitalier (`.planning/phases/06-documentation-publication/06-technical-note.md`, Phase 7 addendum already written in) — owner plans to send 2026-07-31
- Owner: flip the GitHub repo to public (`gh repo edit alejack312/merlin-photonic-generative-modeling --visibility public`)
- Next: `/gsd:plan-phase 9` to plan Encoding Design — Phase 8 is complete and LIT-04's Go verdict has unblocked it
- Backlog (not blocking, candidates for a future milestone): BMK-03 apples-to-apples QGAN comparison; v2.0's deferred Phases 2-4 (implementation, trainability/hardness study, write-up), contingent on this milestone's findings.

### Blockers/Concerns

None open. All prior blockers (the July 25 stall-risk checkpoint, Phase 4's GEN-07 shortfall, the self-audit findings) are resolved or honestly documented as closed — see `.planning/milestones/v1.0-ROADMAP.md` and `.planning/milestones/v1.0-MILESTONE-AUDIT.md`. The Phase 8 LIT-04 contingency is resolved: the owner's Go verdict means Phase 9 (Encoding Design) is unblocked and can proceed.

## Session Continuity

Last session: 2026-08-04
Stopped at: Phase 8, plan 01 (`docs/iqp-lit-scoping.md`) fully closed. Task 3's blocking checkpoint (LIT-04 go/no-go verdict) was resolved by the owner directly — after fetching and reading the full Kurkin et al. BSBM paper (arXiv:2603.11014) rather than just its abstract, the owner stated "No blocking impossibility, let's proceed," a Go verdict, which this session recorded verbatim (lightly edited for flow) as the doc's Go/No-Go Verdict section (commit `b54298f`). Phase 8 is now fully complete (3/3 plans: 08-01, 08-02, 08-03).
Resume by: run `/gsd:plan-phase 9` to plan Encoding Design — Phase 9 is unblocked by LIT-04's Go verdict, with `docs/iqp-lit-scoping.md` and `docs/iqp-baseline.md` as its key reference inputs. The two owner-only v1.0 todos (flip repo public, send technical note to Vincent) remain open and are independent of this milestone.
