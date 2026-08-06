# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-08-05)

**Core value:** A working, end-to-end, honestly-benchmarked MMD-trained photonic generative model, published in a public repo before Sept 1, 2026 — explainable unaided to Vincent Espitalier. (v2.1's core value: get weight-2 IQP generators actually working and validated, not just designed on paper.)
**Current focus:** v1.0 shipped 2026-07-29. v2.0 (IQP → Photonic Encoding) shipped 2026-08-05. **v2.1 (Weight-2 Implementation) roadmap created 2026-08-06** — 4 phases (10-13), 8/8 v1 requirements mapped. Phase 10 completed and verified 2026-08-06. Ready to plan Phase 11.

## Current Position

Milestone: **v2.1 Weight-2 Implementation** — in progress, started 2026-08-05 (v2.0 shipped 2026-08-05, tag: v2.0; v1.0 shipped 2026-07-29, tag: v1.0; Phase 7 mechanism-validation add-on closed 2026-07-30, unassigned to a milestone).
Phase: 11 of 13 (CZ Insertion Unit & Weight-2 Circuit Composition) — Plan 01 of 2 (or more) complete.
Plan: 01 complete — `build_cz_insertion(n, i, j)` implemented and truth-table verified.
Status: Phase 11 Plan 01 executed 2026-08-06. `build_cz_insertion(n, i, j)` (PBS-wrap → `heralded_cz` → PBS-unwrap `Circuit(6)`) implemented in `iqp_photonic_encoding.py`, with the ctrl/data convention adapter (`PERM([1,0])`, 11-RESEARCH.md Pitfall 1) fully internal to the function. Truth table proven executable: `|amplitude|^2 == 2/27`, sign negative only on `|1,1⟩`, for all 4 computational-basis combos plus `|+⟩|+⟩`/`|+⟩|0⟩` superposition spot-checks — Success Criterion 1 satisfied. Discovered a real Perceval backend limitation mid-execution (`Simulator`+`SLOSBackend` cannot process circuits containing `PBS`) and resolved it with a minimal, behavior-preserving refactor (`_build_cz_insertion_core()` testability seam) rather than a duplicated test circuit — see `.planning/phases/11-cz-insertion-unit-weight-2-circuit-composition/11-01-SUMMARY.md` for full rationale. Full repo suite: 104/104 tests pass, no regressions. Build order: Phase 10 (done) → Phase 11 (insertion unit + full pipeline composition, in progress) → Phase 12 (exact reference extension + TVD validation) → Phase 13 (weight-1/weight-2 composability).

Progress: v1.0 [██████████] 100% (GEN-07 honestly concluded not-met within that 100% — not a partial-completion asterisk, the requirement was fully addressed, the outcome was negative). Phase 7 mechanism-validation work is fully closed, owner interpretation pending. v2.0 [██████████] 100% — both phases complete (Phase 8: 4/4 plans; Phase 9: 4/4 plans), 11/11 requirements satisfied, shipped 2026-08-05. v2.1 [███░░░░░░░] ~30% — Phase 10 complete and verified (1/4 phases), Phase 11 Plan 01 of ≥2 complete.

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
- Phase 10 confirmed `heralded_cz`'s herald-success probability at exactly 2/27 (~0.074074), uniform across all 4 computational-basis dual-rail inputs and 2 superposition spot-checks, and the CZ phase sign (negative only on `|1,1⟩`, via `Simulator.prob_amplitude` since `Processor.probs()`/`Analyzer` are phase-blind). `logical_perf` confirmed pure herald condition (empty `post_select_fn`, zero Analyzer-truth-table leakage) — no hidden second filter for this gate.
- `numpy.float64` amplitude coefficients silently break `perceval`'s `StateVector` arithmetic (misleading "inhomogeneous shape" `ValueError`, not a type error) — cast to plain Python `float` before multiplying/adding `StateVector` terms. Hit while building Phase 10's superposition spot-checks; worth knowing for any future `StateVector`-construction code in this repo.
- Perceval's `Simulator`+`SLOSBackend` cannot process any circuit containing `PBS` (`Circuit.requires_polarization` assertion) — confirmed by direct execution while building Phase 11 Plan 01's `build_cz_insertion` tests. `Processor`/`Analyzer`/`PolarizationSimulator` can handle `PBS`, but `PolarizationSimulator` combined with `heralded_cz`'s unannotated ancilla photons produces spurious (near-zero or wrong-magnitude) results due to default polarization labeling making ancilla photons wrongly (in)distinguishable from qubit photons during multi-photon interference. Resolved by testing the PBS boundary (phase-neutral, amplitude-1 for computational basis) and the dual-rail core (adapter + `heralded_cz`) separately, never combined in one simulator call. Worth knowing before Plan 12 attempts to phase-check the full composed weight-2 pipeline — use `Processor`/`Analyzer` (magnitude-only) for the full polarized circuit, not `PolarizationSimulator` phase checks.
- `build_cz_insertion(n, i, j)` (Phase 11 Plan 01) realizes CZ = diag(1,1,1,-1) on this module's own polarization convention via PBS-wrap → PERM-adapted `heralded_cz` → PBS-unwrap, `Circuit(6)` local layout, `herald_spec` read from `in_heralds` not hardcoded. The PERM([1,0]) ctrl/data convention adapter (11-RESEARCH.md Pitfall 1) is fully internal to the function — callers use the module's normal port order, never see the adapter. `_build_cz_insertion_core()` exposes the PBS-free inner wiring for direct testability.

### Roadmap Evolution

- Phase 7 added 2026-07-29: Mechanism Validation — neighbor-locality test (Jacobian-based) + sigma re-sweep against the K=462 grid, scoped from the v1.0 self-audit's tracked backlog. Not yet assigned to a milestone; added via `/gsd:add-phase` continuing numbering from v1.0 rather than restarting.
- v2.0 IQP → Photonic Encoding started 2026-07-30 via `/gsd:new-milestone`, continuing phase numbering from Phase 7 (new phases start at 8).
- v2.0 roadmap created 2026-07-30: exactly 2 phases (8: Literature Scoping & Prerequisites; 9: Encoding Design), derived directly from this milestone's 11 v1 requirements. 100% requirement coverage validated (11/11 mapped, no orphans). v2 requirements (IMPL-01/02, STUDY-01/02, WRITE-01) explicitly deferred, not phased.
- v2.0 shipped 2026-08-05 via `/gsd:complete-milestone`, tagged `v2.0`. `.planning/ROADMAP.md` and `REQUIREMENTS.md` archived to `.planning/milestones/v2.0-*`.
- v2.1 Weight-2 Implementation roadmap created 2026-08-06: 4 phases (10: Heralded-CZ Primitive De-Risking; 11: CZ Insertion Unit & Weight-2 Circuit Composition; 12: Exact Reference Extension & TVD Validation; 13: Weight-1 + Weight-2 Composability Validation), derived directly from this milestone's 8 v1 requirements (WT2-01 through WT2-08) and sequenced per research's recommended de-risk-first build order. Phases 10→11→12→13 are sequentially dependent (each builds on the prior's confirmed output). 100% requirement coverage validated (8/8 mapped, no orphans).

### Pending Todos

- Owner: send the drafted technical note to Vincent Espitalier (`.planning/phases/06-documentation-publication/06-technical-note.md`) — still open
- Owner: flip the GitHub repo to public (`gh repo edit alejack312/merlin-photonic-generative-modeling --visibility public`) — still open
- Next: continue Phase 11 — Plan 01 (`build_cz_insertion`) complete; remaining Phase 11 work (full 2n-mode weight-2 circuit composition via mode-mapping dict) still needs planning/execution
- Backlog (not blocking, deferred to a future milestone): ARB-01 (arbitrary-θ weight-2), STUDY-01/02 (trainability/hardness study), WRITE-01 (write-up), BMK-03 (apples-to-apples QGAN comparison) — all contingent on v2.1's weight-2 implementation actually working

### Blockers/Concerns

None open. All prior blockers (the July 25 stall-risk checkpoint, Phase 4's GEN-07 shortfall, the self-audit findings, the Phase 8 LIT-04 contingency, Phase 9's missing formal verification) are resolved or honestly documented as closed. v2.1's research flagged no open unknowns needing further research before planning — all four research files (STACK, FEATURES/SUMMARY, ARCHITECTURE, PITFALLS) are HIGH confidence, grounded in direct source inspection and live execution against the installed package.

## Session Continuity

Last session: 2026-08-06
Stopped at: Phase 11 Plan 01 executed — `build_cz_insertion(n, i, j)` and `_build_cz_insertion_core()` added to `iqp_photonic_encoding.py`; truth-table tests added to `tests/test_iqp_photonic_encoding.py`; `.planning/phases/11-cz-insertion-unit-weight-2-circuit-composition/11-01-SUMMARY.md` created; `.planning/STATE.md` refreshed.
Resume by: continue Phase 11 (full 2n-mode weight-2 circuit composition wiring `build_cz_insertion` in via a mode-mapping dict, per Plan 01's stated caller contract) — plan the next Phase 11 plan or run `/gsd:plan-phase 11` again if further planning is needed.
