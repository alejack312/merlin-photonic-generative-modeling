# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-08-05)

**Core value:** A working, end-to-end, honestly-benchmarked MMD-trained photonic generative model, published in a public repo before Sept 1, 2026 — explainable unaided to Vincent Espitalier. (v2.1's core value: get weight-2 IQP generators actually working and validated, not just designed on paper.)
**Current focus:** v1.0 shipped 2026-07-29. v2.0 (IQP → Photonic Encoding) shipped 2026-08-05. **v2.1 (Weight-2 Implementation) roadmap created 2026-08-06** — 4 phases (10-13), 8/8 v1 requirements mapped. Ready to plan Phase 10.

## Current Position

Milestone: **v2.1 Weight-2 Implementation** — in progress, started 2026-08-05 (v2.0 shipped 2026-08-05, tag: v2.0; v1.0 shipped 2026-07-29, tag: v1.0; Phase 7 mechanism-validation add-on closed 2026-07-30, unassigned to a milestone).
Phase: 10 of 13 (Heralded-CZ Primitive De-Risking) — ready to plan.
Plan: — (not yet planned)
Status: Roadmap created 2026-08-06 (research + roadmap complete). Build order: Phase 10 (de-risk `heralded_cz` standalone) → Phase 11 (insertion unit + full pipeline composition) → Phase 12 (exact reference extension + TVD validation) → Phase 13 (weight-1/weight-2 composability). Existing 26-test weight-1 suite must stay green throughout.

Progress: v1.0 [██████████] 100% (GEN-07 honestly concluded not-met within that 100% — not a partial-completion asterisk, the requirement was fully addressed, the outcome was negative). Phase 7 mechanism-validation work is fully closed, owner interpretation pending. v2.0 [██████████] 100% — both phases complete (Phase 8: 4/4 plans; Phase 9: 4/4 plans), 11/11 requirements satisfied, shipped 2026-08-05. v2.1 [░░░░░░░░░░] 0% — roadmap created, 0/4 phases started.

## Performance Metrics

**v1.0 milestone:**
- Phases: 6
- Plans: 11
- Commits: 51
- Files touched: 103 (7,624 insertions, 56 deletions)
- LOC: 1,648 Python
- Timeline: 10 days (2026-07-19 → 2026-07-29)

**v2.0 milestone:**
- Phases: 2
- Plans: 8
- Commits: 33
- Lines added: 1,282 (code + tests)
- Timeline: 6 days (2026-07-30 → 2026-08-05)

## Accumulated Context

### Decisions

Full decision log archived in `.planning/PROJECT.md`'s Key Decisions table and `.planning/milestones/v1.0-ROADMAP.md`'s Milestone Summary. Highlights carried forward for any future work on this codebase:

- Weight-2 requires `Processor`-level composition, not `Circuit`-level — `heralded_cz`'s `build_circuit()` alone has no herald attached; only `build_experiment()`/`build_processor()` do. Every existing weight-1 builder (`build_state_prep_circuit`, `build_diagonal_layer_circuit`, `build_conjugation_circuit`, `build_readout_circuit`) is a valid `Processor.add()` input and stays unmodified.
- `heralded_cz` success probability independently re-measured in this repo's venv at exactly 2/27 ≈ 0.074074, uniform across all 4 computational-basis inputs — confirms rather than merely cites the literature figure. `physical_perf == 1.0` in all cases (no photon loss in the unitary itself; the entire cost is the herald/logical filter).
- `global_perf`/`.performance` (herald success) must be captured as a first-class, separately-reported number from day one — weight-1's `run_full_circuit` pattern never needed to read it (its `performance` was always 1.0), so copy-pasting that helper verbatim would silently drop the milestone's actual deliverable number.
- `logical_perf` bundles the true herald condition with a second, distinct filter (data-mode output falling outside the valid dual-rail subspace) — must be checked negligible for the inputs actually used before citing it as "the herald probability," not assumed.
- The CZ/ZZ operator identity (`exp(iπ/4·Z_iZ_j) = CZ · exp(iπ/4·Z_i) · exp(iπ/4·Z_j)` up to global phase) means the single-qubit π/4 corrections fold additively into `build_diagonal_layer_circuit`'s existing `thetas` argument — no new phase-gate code needed.
- Batch-averaged per-sample MMD² training objective is a provable upper bound on the marginal-distribution MMD² (Jensen's inequality on the convex kernel term), not identical to it — documented in `DESIGN_DECISIONS.md`, worth knowing before extending the training loop.
- Natural-order correspondence's causal mechanism (why radius-sorting helps) is asserted, not demonstrated — a genuine open question, not a settled fact, if this generator is extended or reused.
- `torch.func.functional_call` + `jacrev` against MerLin's `QuantumLayer` silently produces an all-zero Jacobian unless `quantum_layer.thetas` is also monkey-patched inside the traced closure (see `generator/neighbor_locality.py`).
- `docs/iqp-photonic-encoding.md` (Phase 9) is the milestone's core prior deliverable: polarization encoding, `WP(θ,0) = diag(e^{iθ},e^{-iθ})` for weight-1, `HWP(π/8)` for state prep/conjugation. Port convention `H=(0,1)`, `V=(1,0)` — a backwards version of this was caught and fixed silently mid-Phase-9 (no test failed, only the label was wrong) via a direct calibration check, the same pattern weight-2's mode-index round-trip check (Phase 11) must repeat.

### Roadmap Evolution

- Phase 7 added 2026-07-29: Mechanism Validation — neighbor-locality test (Jacobian-based) + sigma re-sweep against the K=462 grid, scoped from the v1.0 self-audit's tracked backlog. Not yet assigned to a milestone; added via `/gsd:add-phase` continuing numbering from v1.0 rather than restarting.
- v2.0 IQP → Photonic Encoding started 2026-07-30 via `/gsd:new-milestone`, continuing phase numbering from Phase 7 (new phases start at 8).
- v2.0 roadmap created 2026-07-30: exactly 2 phases (8: Literature Scoping & Prerequisites; 9: Encoding Design), derived directly from this milestone's 11 v1 requirements. 100% requirement coverage validated (11/11 mapped, no orphans). v2 requirements (IMPL-01/02, STUDY-01/02, WRITE-01) explicitly deferred, not phased.
- v2.0 shipped 2026-08-05 via `/gsd:complete-milestone`, tagged `v2.0`. `.planning/ROADMAP.md` and `REQUIREMENTS.md` archived to `.planning/milestones/v2.0-*`.
- v2.1 Weight-2 Implementation roadmap created 2026-08-06: 4 phases (10: Heralded-CZ Primitive De-Risking; 11: CZ Insertion Unit & Weight-2 Circuit Composition; 12: Exact Reference Extension & TVD Validation; 13: Weight-1 + Weight-2 Composability Validation), derived directly from this milestone's 8 v1 requirements (WT2-01 through WT2-08) and sequenced per research's recommended de-risk-first build order. Phases 10→11→12→13 are sequentially dependent (each builds on the prior's confirmed output). 100% requirement coverage validated (8/8 mapped, no orphans).

### Pending Todos

- Owner: send the drafted technical note to Vincent Espitalier (`.planning/phases/06-documentation-publication/06-technical-note.md`) — still open
- Owner: flip the GitHub repo to public (`gh repo edit alejack312/merlin-photonic-generative-modeling --visibility public`) — still open
- Next: `/gsd:plan-phase 10` to begin planning the first v2.1 phase
- Backlog (not blocking, deferred to a future milestone): ARB-01 (arbitrary-θ weight-2), STUDY-01/02 (trainability/hardness study), WRITE-01 (write-up), BMK-03 (apples-to-apples QGAN comparison) — all contingent on v2.1's weight-2 implementation actually working

### Blockers/Concerns

None open. All prior blockers (the July 25 stall-risk checkpoint, Phase 4's GEN-07 shortfall, the self-audit findings, the Phase 8 LIT-04 contingency, Phase 9's missing formal verification) are resolved or honestly documented as closed. v2.1's research flagged no open unknowns needing further research before planning — all four research files (STACK, FEATURES/SUMMARY, ARCHITECTURE, PITFALLS) are HIGH confidence, grounded in direct source inspection and live execution against the installed package.

## Session Continuity

Last session: 2026-08-06
Stopped at: v2.1 roadmap created — `.planning/ROADMAP.md` updated with Phases 10-13, `.planning/REQUIREMENTS.md` traceability updated (8/8 mapped), `.planning/STATE.md` refreshed.
Resume by: run `/gsd:plan-phase 10` to plan the first phase (Heralded-CZ Primitive De-Risking).
