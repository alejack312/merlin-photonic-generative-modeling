# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-07-30)

**Core value:** A working, end-to-end, honestly-benchmarked MMD-trained photonic generative model, published in a public repo before Sept 1, 2026 — explainable unaided to Vincent Espitalier.
**Current focus:** v1.0 shipped 2026-07-29. Phase 7 (Mechanism Validation) closed 2026-07-30. v2.0 (IQP → Photonic Encoding) roadmap created 2026-07-30 — 2 phases (8: Literature Scoping & Prerequisites, 9: Encoding Design), 11 requirements, 100% coverage. **v2.0 milestone complete as of 2026-08-05** (Phases 8-9 both done).

## Current Position

Milestone: v2.0 IQP → Photonic Encoding — **complete** 2026-08-05 (started 2026-07-30; v1.0 shipped 2026-07-29, tag: v1.0; Phase 7 mechanism-validation add-on closed 2026-07-30)
Phase: 9 (Encoding Design) — complete, all 4 plans executed, final self-explanation checkpoint passed
Plan: 4 of 4 complete (09-01 ENC-01, 09-02 ENC-03, 09-03 ENC-04, 09-04 ENC-02 + final assembly)
Status: Phase 9 delivered `docs/iqp-photonic-encoding.md` — a complete, owner-attempted, equation-derived mapping from IQP's structure onto Perceval's polarization-encoding primitives. Owner chose polarization encoding (personal Sorbonne coursework). Weight-1 IQP generators: fully derived (`WP(θ,0) = exp(iθZ)` exactly), implemented (`iqp_photonic_encoding.py`), and empirically validated (TVD ~1e-16 against the exact qubit-side distribution at n=2,3 — ten orders of magnitude under the owner's chosen 1e-6 threshold). Weight-2 generators: derived on paper only (fixed angle π/4 via `heralded_cz`), explicitly flagged throughout as untested — the owner correctly resisted extrapolating the weight-1 result to weight-2 during the Wave 3 checkpoint. A real H/V port-labeling bug from Wave 1 (self-consistent but backwards relative to true physical polarization) was caught and fixed during Wave 2's attempt-first checkpoint. ENC-02 positions the mapping against Douce et al. (2017) with both a favorable contrast (native single-qubit conjugation) and an honest parallel (weight-2's probabilistic gate inherits the same measurement-based character as Douce's gadget). Full test suite: 85/85 passing, no regressions.

Progress: [██████████] 100% of v1.0 (GEN-07 honestly concluded not-met within that 100% — not a partial-completion asterisk, the requirement was fully addressed, the outcome was negative). Phase 7 mechanism-validation work is fully closed. v2.0: [██████████] both phases complete (Phase 8: 4/4 plans; Phase 9: 4/4 plans), 11/11 requirements satisfied.

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
- `perceval_fluency_demo.py` (Phase 8 plan 04, gap closure) added a `pcvl.PS`-exercising third example: a `BS.H()->PS(theta)->BS.H()` Mach-Zehnder construction, closed-form checked against `cos^2(theta/2)`/`sin^2(theta/2)` across theta in `{0, pi/2, pi}`. Confirms a bare phase shifter's angle is invisible to Fock-basis photon-number measurement without a second beamsplitter to interfere against — the MZI form is what actually demonstrates PS's role. This closed `08-VERIFICATION.md`'s only gap (score 9/10 -> fully verified) and is directly reusable groundwork for Phase 9's phase-driven interference reasoning.
- `docs/iqp-lit-scoping.md` (Phase 8 plan 01, LIT-01/LIT-02/LIT-04) records the phase's gating decision: **Go** on proceeding to Phase 9. No DV/Fock-space linear-optical IQP construction and no impossibility result exists in the literature, across `08-RESEARCH.md`'s original WebSearch pass and a second, independently-conducted arXiv-API + Semantic-Scholar-citation-graph pass. Douce et al. (2017)'s CV-IQP hardness result is built in the continuous-quadrature formalism (squeezed light + homodyne), a different formalism from Fock-space/photon-number linear optics — it neither proves nor disproves anything about a DV construction. Kurkin et al.'s Boson Sampling Born Machine (arXiv:2603.11014) is the closest tangential paper found but doesn't match: it borrows IQP-QCBM's training recipe but derives hardness from ordinary boson-sampling permanent-hardness (Aaronson-Arkhipov), not IQP's own commuting-diagonal-gate structure in Fock space — worth citing in Phase 9 as context, not as a blocker.
- `docs/iqp-photonic-encoding.md` (Phase 9, all 4 plans) is the milestone's core deliverable: polarization encoding (owner's choice), `WP(θ,0) = diag(e^{iθ},e^{-iθ})` for weight-1 generators (exact, verified against Perceval's installed matrix), `HWP(π/8)` for both state prep and Hadamard-conjugation (realizes Hadamard up to an unobservable global phase `i`). Empirically confirmed port↔polarization convention: `H=(0,1)`, `V=(1,0)` (an earlier, self-consistent-but-backwards version of this convention was caught and fixed during Phase 9 — worth remembering if this module is ever extended, since the bug was silent: no test ever failed, only the human-readable label was wrong). Weight-2 generators (`exp(iθZ_iZ_j)`) are derived on paper via `PBS`→`heralded_cz`→`PBS`, realizing only the fixed angle `θ=π/4`, and were never implemented or run — this is a real, stated gap for any future implementation phase, not a solved problem. ENC-04's toy validation (TVD ~1e-16 at n=2,3) confirms the mapping only for the weight-1 case tested; it provides zero evidence about weight-2, which behaves via a structurally different (probabilistic, fixed-angle) mechanism.
- `iqp_photonic_encoding.py`'s `bitstring_to_fock`/`fock_to_bitstring` (ENC-03) give the falsifiable basis correspondence, with `None` returned (not a discarded/renormalized guess) for any of four out-of-subspace photon-count patterns per qubit pair: `(0,0)` lost, `(1,1)` extra photon split across both modes, `(2,0)`/`(0,2)` bunched — worth reusing this same round-trip-test pattern (forward map → physical circuit → reverse map → compare to original) for any future basis-correspondence work, since it's what caught the H/V labeling bug above.

### Roadmap Evolution

- Phase 7 added 2026-07-29: Mechanism Validation — neighbor-locality test (Jacobian-based) + sigma re-sweep against the K=462 grid, scoped from the v1.0 self-audit's tracked backlog. Not yet assigned to a milestone; added via `/gsd:add-phase` continuing numbering from v1.0 rather than restarting.
- v2.0 IQP → Photonic Encoding started 2026-07-30 via `/gsd:new-milestone`, continuing phase numbering from Phase 7 (new phases start at 8).
- v2.0 roadmap created 2026-07-30: exactly 2 phases (8: Literature Scoping & Prerequisites; 9: Encoding Design), derived directly from this milestone's 11 v1 requirements — matching the source plan doc's own Phase 0/Phase 1 split, not the doc's full 5-phase scope. Phase 9 is sequentially dependent on Phase 8's LIT-04 go/no-go verdict. 100% requirement coverage validated (11/11 mapped, no orphans). v2 requirements (IMPL-01/02, STUDY-01/02, WRITE-01) explicitly deferred, not phased.

### Pending Todos

- Owner: send the drafted technical note to Vincent Espitalier (`.planning/phases/06-documentation-publication/06-technical-note.md`, Phase 7 addendum already written in) — owner plans to send 2026-07-31 (still open)
- Owner: flip the GitHub repo to public (`gh repo edit alejack312/merlin-photonic-generative-modeling --visibility public`) — still open
- Next: `/gsd:audit-milestone` or `/gsd:complete-milestone` to close out v2.0, or start planning a future milestone covering the deferred v2 requirements (IMPL-01/02, STUDY-01/02, WRITE-01) if the owner wants to continue implementing the weight-2 case and running a larger-scale study
- Backlog (not blocking, candidates for a future milestone): BMK-03 apples-to-apples QGAN comparison; v2.0's deferred Phases 2-4 (implementation, trainability/hardness study, write-up) — now well-scoped by Phase 9's stated limitations (weight-2 `heralded_cz` needs actual implementation and testing; general-n scaling untested)

### Blockers/Concerns

None open. All prior blockers (the July 25 stall-risk checkpoint, Phase 4's GEN-07 shortfall, the self-audit findings, the Phase 8 LIT-04 contingency) are resolved or honestly documented as closed — see `.planning/milestones/v1.0-ROADMAP.md` and `.planning/milestones/v1.0-MILESTONE-AUDIT.md`. v2.0 milestone (Phases 8-9) is now fully complete with no open blockers.

## Session Continuity

Last session: 2026-08-05
Stopped at: Phase 9 (Encoding Design) fully complete — all 4 plans executed, verified, and committed (`27925f7`, `396dd5a`, `b87b2a2`, `773756f`, `15a64ed`, `c341af0`, `541145d`, `0315ba8`). `docs/iqp-photonic-encoding.md` assembled as one coherent document (intro, ENC-01 through ENC-04, Conclusion and Open Questions). Owner chose polarization encoding; weight-1 generators fully derived/implemented/validated (TVD ~1e-16 at n=2,3); weight-2 derived on paper only, explicitly untested. A real H/V port-labeling bug from Wave 1 was caught during Wave 2 and fixed across the module, tests, and docs. Full test suite: 85/85 passing. Final whole-document self-explanation checkpoint passed after several correction rounds (documented in `09-04-SUMMARY.md` and within the doc's own checkpoint sections). `.planning/REQUIREMENTS.md` (ENC-01 through ENC-05) and `.planning/ROADMAP.md` (Phase 9, Progress table) updated to reflect completion. v2.0 milestone is complete.
Resume by: run `/gsd:audit-milestone` to formally audit v2.0 before archiving, or `/gsd:complete-milestone` to archive directly, or start a new milestone/phase for the deferred v2 requirements (weight-2 implementation, trainability study, write-up) if the owner wants to continue. The two owner-only v1.0 todos (flip repo public, send technical note to Vincent) remain open and are independent of this milestone.
