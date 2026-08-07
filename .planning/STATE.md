# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-08-06)

**Core value:** A working, end-to-end, honestly-benchmarked MMD-trained photonic generative model, published in a public repo before Sept 1, 2026 — explainable unaided to Vincent Espitalier.
**Current focus:** v1.0 shipped 2026-07-29. v2.0 (IQP → Photonic Encoding) shipped 2026-08-05. v2.1 (Weight-2 Implementation) shipped 2026-08-06. **v3.0 (IQP Circuit Study & Write-Up) roadmap created 2026-08-07** — 8 phases (14-21), 35 v1 requirements mapped, 100% coverage. Four decoupled/lightly-coupled tracks: Julia toolchain spike (14, earliest, stall-risk checkpoint), ARB-01 arbitrary-θ weight-2 gate (15-16), trainability/barren-plateau study (17), hardness-under-loss study (18), Julia cross-checks (19), write-up (20-21). All four Must-have deliverables, no fallback ordering (owner's explicit call) — but STUDY-01/STUDY-02 explicitly do not block on ARB-01's open-research risk, per pitfalls research's highest-leverage finding.

## Current Position

Phase: 15 (ARB-01 Core Gate De-Risking & Validation) — in progress
Plan: 01 of ? — complete
Status: Plan 15-01 shipped: `cp_gate_derisking.py` confirms `PostProcessedControlledRotationsItem` implements `CP(α)=diag(1,1,1,e^{iα})` via bare-circuit `Simulator.prob_amplitude`, at 3 non-trivial α (π/6, π/3, 2π/5) plus the α=π boundary (independently confirming |amplitude|²=1/9 and the sign match to `heralded_cz`'s `diag(1,1,1,-1)`). Plan 15-02 (circuit-wiring integration into the full pipeline — flagged as a real open risk in 15-RESEARCH.md, TVD did not converge in the research spike) is next.

```
Progress: [██------------------] 1/8 phases (v3.0)
```

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

**v3.0 milestone:** In progress — started 2026-08-07, 8 phases planned (14-21), 35 v1 requirements. Deadline: Sept 1, 2026. Mid-milestone checkpoint target: ~2026-08-20 (see `ROADMAP.md`).

## Accumulated Context

### Decisions

Full decision log archived in `.planning/PROJECT.md`'s Key Decisions table, `.planning/milestones/v1.0-ROADMAP.md`'s Milestone Summary, and `.planning/milestones/v2.1-ROADMAP.md`'s Milestone Summary. Reusable technical gotchas carried forward for any future work on this codebase:

- `numpy.float64` amplitude coefficients silently break `perceval`'s `StateVector` arithmetic (misleading "inhomogeneous shape" `ValueError`, not a type error) — cast to plain Python `float` before multiplying/adding `StateVector` terms.
- Perceval's `Simulator`+`SLOSBackend` cannot process any circuit containing `PBS` (`Circuit.requires_polarization` assertion). `Processor`/`Analyzer`/`PolarizationSimulator` can handle `PBS`, but `PolarizationSimulator` combined with unannotated ancilla photons produces spurious results — always explicitly annotate ancilla polarization (`{P:V}` or similar), never rely on the default.
- `Processor.add_herald()` combined with any `PBS`-containing circuit crashes `Processor.probs()` unconditionally (Perceval library limitation, filed upstream as [Quandela/Perceval#783](https://github.com/Quandela/Perceval/issues/783)). Workaround: build a herald-free measurement variant with manual post-selection on the ancilla output modes instead of registering the herald on the measurement processor.
- `torch.func.functional_call` + `jacrev` against MerLin's `QuantumLayer` silently produces an all-zero Jacobian unless `quantum_layer.thetas` is also monkey-patched inside the traced closure (see `generator/neighbor_locality.py`).
- **`MerLin's `QuantumLayer` categorically rejects polarization-annotated `BasicState`s (`ValueError: BasicState with annotations is not supported`) — verified live during v3.0 research.** This project's weight-1/weight-2 IQP circuits (`requires_polarization = True`) can never be wrapped in a `QuantumLayer`; STUDY-01/STUDY-02 must use parameter-shift gradients and `Processor.probs()`+`NoiseModel` instead, never autograd-through-`QuantumLayer` or `Analyzer`+`NoiseModel` (the latter silently ignores loss — also verified live).
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
- v3.0 IQP Circuit Study & Write-Up roadmap created 2026-08-07: 8 phases (14: Julia Toolchain Spike; 15: ARB-01 Core Gate De-Risking & Validation; 16: ARB-01 Extended Validation & Postselection Bookkeeping; 17: Trainability/Barren-Plateau Study; 18: Hardness-Under-Loss Assessment; 19: Independent Julia Cross-Checks; 20: Technical Write-Up; 21: External-Facing Framing Pass), derived from this milestone's 35 v1 requirements (corrected from REQUIREMENTS.md's own "34 total" arithmetic error — 8+7+9+4+7=35). Phases 14/15/17/18 are mutually independent (Wave 1, can plan/execute in parallel); Phase 16 depends on 15; Phase 19 depends on 14+18; Phase 20 depends on 16+17+18; Phase 21 depends on 20. Explicit design goal (per `PITFALLS.md` Pitfall 25): STUDY-01/STUDY-02 (Phases 17-18) never block on ARB-01 (Phases 15-16) resolving. 100% requirement coverage validated (35/35 mapped, no orphans). A mid-milestone checkpoint (~2026-08-20, per Pitfall 26) is recorded as a named roadmap artifact in `ROADMAP.md`.

### Pending Todos

- Owner: send the drafted technical note to Vincent Espitalier (`.planning/phases/06-documentation-publication/06-technical-note.md`) — still open
- Owner: flip the GitHub repo to public (`gh repo edit alejack312/merlin-photonic-generative-modeling --visibility public`) — still open
- Next: continue Phase 15 with Plan 15-02 (circuit-wiring integration — the flagged open risk from 15-RESEARCH.md's Open Question 2, TVD did not converge in the research spike)

### Blockers/Concerns

**Phase 14 verdict: FULL GO** (2026-08-07) — juliaup + Julia 1.10.11 LTS +
Yao.jl (v0.9.1, resolved) + BosonSampling.jl (v1.0.2) all installed and both
hello-world scripts pass their analytical `@assert` checks. No alternate
paths needed; ITensors.jl (the biggest flagged risk) was never pulled into
the resolved dependency tree. See `results/phase14_julia_toolchain_summary.md`
for full detail. Phase 19's VERIFY-02/03/04 can proceed as originally scoped
— no scope conversation with the owner needed.

None open yet for v3.0 execution otherwise. Watch items carried into execution:
- v3.0 was scoped with STUDY-01 (TRAIN), STUDY-02 (HARD), ARB-01, and WRITE-01 all as Must-have with no fallback ordering — owner's explicit call after being shown the risk that ARB-01 is genuinely open research and the Julia toolchain is brand-new. This is the first milestone since the PennyLane stall (May 2026) to combine open research with a hard deadline.
- Mitigation now built into the roadmap: Phase 14 (Julia spike) is sequenced earliest and fully decoupled as an explicit stall-risk checkpoint; Phases 17 (TRAIN) and 18 (HARD) are structurally independent of Phases 15-16 (ARB-01) so ARB-01 slippage cannot block them; a named mid-milestone checkpoint (~2026-08-20) with four per-item progress questions is recorded in `ROADMAP.md`.
- HARD-03 (full read of arXiv:2510.24137) is a near-zero-code but load-bearing, non-deferrable first step inside Phase 18 — flagged explicitly in the roadmap so it isn't left implicit or done last.

## Session Continuity

Last session: 2026-08-07
Stopped at: Plan 15-01 executed and shipped — `cp_gate_derisking.py` + `tests/test_cp_gate_derisking.py` confirm `CP(α)`'s bare-gate phase/structure at 3 non-trivial α plus the α=π boundary. `.planning/phases/15-arb-01-core-gate-de-risking-validation/15-01-SUMMARY.md` documents the run.
Resume by: continue Phase 15 with Plan 15-02 (circuit-wiring integration — the flagged TVD-convergence risk from 15-RESEARCH.md).
