# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-08-06)

**Core value:** A working, end-to-end, honestly-benchmarked MMD-trained photonic generative model, published in a public repo before Sept 1, 2026 — explainable unaided to Vincent Espitalier.
**Current focus:** v1.0 shipped 2026-07-29. v2.0 (IQP → Photonic Encoding) shipped 2026-08-05. v2.1 (Weight-2 Implementation) shipped 2026-08-06. **v3.0 (IQP Circuit Study & Write-Up) scoping started 2026-08-06** — STUDY-01 (trainability/barren-plateau), STUDY-02 (hardness-under-loss), ARB-01 (arbitrary-θ weight-2), WRITE-01 (write-up), plus a ket.jl/SDP independent verifier. All four Must-have, no fallback ordering (owner's explicit call).

## Current Position

Phase: Not started (defining requirements)
Plan: —
Status: Defining requirements for milestone v3.0.

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

**v2.1 milestone:**
- Phases: 4
- Plans: 6
- Commits: 38
- Files touched: 33 (4,167 insertions, 45 deletions); 1,144 lines of Python
- Timeline: 1 day (2026-08-06, same-day sprint)

## Accumulated Context

### Decisions

Full decision log archived in `.planning/PROJECT.md`'s Key Decisions table, `.planning/milestones/v1.0-ROADMAP.md`'s Milestone Summary, and `.planning/milestones/v2.1-ROADMAP.md`'s Milestone Summary. Reusable technical gotchas carried forward for any future work on this codebase:

- `numpy.float64` amplitude coefficients silently break `perceval`'s `StateVector` arithmetic (misleading "inhomogeneous shape" `ValueError`, not a type error) — cast to plain Python `float` before multiplying/adding `StateVector` terms.
- Perceval's `Simulator`+`SLOSBackend` cannot process any circuit containing `PBS` (`Circuit.requires_polarization` assertion). `Processor`/`Analyzer`/`PolarizationSimulator` can handle `PBS`, but `PolarizationSimulator` combined with unannotated ancilla photons produces spurious results — always explicitly annotate ancilla polarization (`{P:V}` or similar), never rely on the default.
- `Processor.add_herald()` combined with any `PBS`-containing circuit crashes `Processor.probs()` unconditionally (Perceval library limitation, filed upstream as [Quandela/Perceval#783](https://github.com/Quandela/Perceval/issues/783)). Workaround: build a herald-free measurement variant with manual post-selection on the ancilla output modes instead of registering the herald on the measurement processor.
- `torch.func.functional_call` + `jacrev` against MerLin's `QuantumLayer` silently produces an all-zero Jacobian unless `quantum_layer.thetas` is also monkey-patched inside the traced closure (see `generator/neighbor_locality.py`).
- Batch-averaged per-sample MMD² training objective is a provable upper bound on the marginal-distribution MMD² (Jensen's inequality), not identical to it — documented in `DESIGN_DECISIONS.md`.
- Natural-order correspondence's causal mechanism (why radius-sorting helps) is asserted, not demonstrated — a genuine open question if this generator is extended or reused.
- `docs/iqp-photonic-encoding.md` is the canonical design reference for both weight-1 (implemented v2.0) and weight-2 (implemented v2.1) IQP generators — kept in sync with shipped code as of the v2.1 milestone audit.

### Roadmap Evolution

- Phase 7 added 2026-07-29: Mechanism Validation — neighbor-locality test (Jacobian-based) + sigma re-sweep against the K=462 grid, scoped from the v1.0 self-audit's tracked backlog. Not yet assigned to a milestone; added via `/gsd:add-phase` continuing numbering from v1.0 rather than restarting.
- v2.0 IQP → Photonic Encoding started 2026-07-30 via `/gsd:new-milestone`, continuing phase numbering from Phase 7 (new phases start at 8).
- v2.0 roadmap created 2026-07-30: exactly 2 phases (8: Literature Scoping & Prerequisites; 9: Encoding Design), derived directly from this milestone's 11 v1 requirements. 100% requirement coverage validated (11/11 mapped, no orphans). v2 requirements (IMPL-01/02, STUDY-01/02, WRITE-01) explicitly deferred, not phased.
- v2.0 shipped 2026-08-05 via `/gsd:complete-milestone`, tagged `v2.0`. `.planning/ROADMAP.md` and `REQUIREMENTS.md` archived to `.planning/milestones/v2.0-*`.
- v2.1 Weight-2 Implementation roadmap created 2026-08-06: 4 phases (10: Heralded-CZ Primitive De-Risking; 11: CZ Insertion Unit & Weight-2 Circuit Composition; 12: Exact Reference Extension & TVD Validation; 13: Weight-1 + Weight-2 Composability Validation), derived directly from this milestone's 8 v1 requirements (WT2-01 through WT2-08) and sequenced per research's recommended de-risk-first build order. Phases 10→11→12→13 are sequentially dependent (each builds on the prior's confirmed output). 100% requirement coverage validated (8/8 mapped, no orphans).
- v2.1 shipped 2026-08-06 via `/gsd:complete-milestone`, tagged `v2.1`. All 4 phases completed same-day. `.planning/ROADMAP.md`, `REQUIREMENTS.md`, and the milestone audit archived to `.planning/milestones/v2.1-*`.

### Pending Todos

- Owner: send the drafted technical note to Vincent Espitalier (`.planning/phases/06-documentation-publication/06-technical-note.md`) — still open
- Owner: flip the GitHub repo to public (`gh repo edit alejack312/merlin-photonic-generative-modeling --visibility public`) — still open
- Next: continue `/gsd:new-milestone` — requirements not yet defined for v3.0

### Blockers/Concerns

None open yet for v3.0. Watch item: v3.0 was scoped with STUDY-01, STUDY-02, ARB-01, and WRITE-01 all as Must-have with no fallback ordering — owner's explicit call after being shown the risk that ARB-01 is genuinely open research and ket.jl/SDP is a new toolchain. This is the first milestone since the PennyLane stall (May 2026) to combine open research with a hard deadline; worth watching for the same stall pattern.

## Session Continuity

Last session: 2026-08-06
Stopped at: v3.0 (IQP Circuit Study & Write-Up) milestone scoping in progress via `/gsd:new-milestone` — PROJECT.md and STATE.md updated with milestone goals (STUDY-01, STUDY-02, ARB-01, WRITE-01, ket.jl/SDP verifier); requirements not yet defined.
Resume by: continue `/gsd:new-milestone` from the requirements-definition step, or handle the two remaining owner-only manual steps (send technical note to Vincent Espitalier, flip repo public).
