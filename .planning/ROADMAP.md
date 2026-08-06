# Roadmap: MerLin Photonic Generative Modeling

## Milestones

- ✅ **v1.0 Photonic Generator** — Phases 1-6 (shipped 2026-07-29)
- ✅ **v2.0 IQP → Photonic Encoding** — Phases 8-9 (shipped 2026-08-05)
- 🚧 **v2.1 Weight-2 Implementation** — Phases 10-13 (in progress)

## Phases

<details>
<summary>✅ v1.0 Photonic Generator (Phases 1-6) — SHIPPED 2026-07-29</summary>

- [x] Phase 1: Environment & Architecture Foundation — completed 2026-07-19
- [x] Phase 2: Generator Data & Loss Infrastructure (4/4 plans) — completed 2026-07-19
- [x] Phase 3: End-to-End Training Run (1/1 plan) — completed 2026-07-24
- [x] Phase 4: Generative Quality (3/3 plans) — concluded 2026-07-25 (GEN-07 not met, honestly documented)
- [x] Phase 5: Benchmarking (1/1 plan) — completed 2026-07-29
- [x] Phase 6: Documentation & Publication (2/2 plans) — completed 2026-07-29

Full detail: [`.planning/milestones/v1.0-ROADMAP.md`](milestones/v1.0-ROADMAP.md)

</details>

### Phase 7: Mechanism Validation — completed 2026-07-30 (not yet assigned to a milestone)

**Goal:** Test the two concrete follow-ups flagged by the v1.0 self-audit as unresolved about the natural-order-correspondence result (ring_mass 0.609→0.691) — whether the claimed mechanism actually holds, and whether an unrelated confound (stale sigma) explains part of the improvement instead.
**Depends on:** Phase 6 (uses `NaturallyOrderedGenerator`, `natural_sorted_centers`, the Phase 4 sigma-sweep pattern)
**Requirements:** None yet — this phase predates a formal requirements pass; scoped directly from `.planning/milestones/v1.0-MILESTONE-AUDIT.md`'s tracked backlog.
**Plans:** 2 plans (2 waves, sequential — 07-02 depends on 07-01 per the roadmap's stated experiment order)

Plans:
- [x] 07-01-PLAN.md — Neighbor-locality test (Method B, Jacobian-based): `generator/neighbor_locality.py` + `neighbor_locality_test.py`, 20 fresh random parameter draws + 1 trained-checkpoint supplementary draw
- [x] 07-02-PLAN.md — Sigma re-sweep: `sigma_resweep.py`, same SIGMA_GRID as Phase 4 re-trained against the K=462 natural-order grid, compared side-by-side against Phase 4's K=400 numbers

**Results (measured, not interpreted — owner's job per this repo's CLAUDE.md):**
- Neighbor-locality: pooled test **fails** the locked two-condition bar (`mean_diff=0.0096` vs. `min_effect=0.10`; p=0.00835 clears significance alone but the effect size doesn't). 13/20 draws individually show the expected direction. Trained checkpoint also fails (`mean_diff=0.0402`).
- Sigma re-sweep: K=462 argmax is still sigma=0.1 (`ring_mass=0.7145`) — no other tested sigma beats it. Same bandwidth already used for every reported K=462 result.
- Owner interpretation pending in both `results/phase7_*_summary.md` files.

<details>
<summary>✅ v2.0 IQP → Photonic Encoding (Phases 8-9) — SHIPPED 2026-08-05</summary>

- [x] Phase 8: Literature Scoping & Prerequisites (4/4 plans) — completed 2026-08-04, LIT-04 verdict: **Go**
- [x] Phase 9: Encoding Design (4/4 plans) — completed 2026-08-05, polarization encoding, TVD ~1e-16 at n=2,3

Full detail: [`.planning/milestones/v2.0-ROADMAP.md`](milestones/v2.0-ROADMAP.md)
Requirements: [`.planning/milestones/v2.0-REQUIREMENTS.md`](milestones/v2.0-REQUIREMENTS.md)
Audit: [`.planning/milestones/v2.0-MILESTONE-AUDIT.md`](milestones/v2.0-MILESTONE-AUDIT.md)

</details>

### 🚧 v2.1 Weight-2 Implementation (Phases 10-13, in progress)

**Milestone Goal:** Implement and validate the weight-2 IQP generator (`heralded_cz`-based two-qubit diagonal phase gate, fixed at θ=π/4) that v2.0 designed on paper but never built or ran. Extend the classical-comparison validation pattern from weight-1 (TVD-based) to cover weight-2. Empirically measure `heralded_cz`'s actual success probability against Perceval's specific implementation, rather than relying on secondhand literature figures.

**Build order rationale (from research):** de-risk the `heralded_cz` primitive standalone first (Phase 10) → build/verify the PBS-wrap/heralded_cz/PBS-unwrap insertion unit and compose the full weight-2 pipeline reusing existing weight-1 builders unmodified (Phase 11) → extend the exact reference and run TVD validation (Phase 12) → confirm weight-1/weight-2 composability in a mixed circuit (Phase 13). The existing 26-test weight-1 suite must stay green throughout — each phase includes an explicit regression check before the next phase builds on it.

#### Phase 10: Heralded-CZ Primitive De-Risking
**Goal**: `heralded_cz`'s actual measured behavior (not literature assumptions) is confirmed for this specific Perceval implementation, before any integration work begins.
**Depends on**: Phase 9 (reuses the polarization/dual-rail conventions `docs/iqp-photonic-encoding.md` established)
**Requirements**: WT2-04, WT2-08
**Success Criteria** (what must be TRUE):
  1. A standalone test/script, built via `build_experiment()` + `Processor.probs()`/`Analyzer` (never `build_circuit()`, which drops the herald), reports `heralded_cz`'s exact analytic herald-success probability read directly off `global_perf`/`.performance` — not shot-sampled.
  2. The measured success probability is confirmed uniform (to floating-point precision) across all 4 computational-basis dual-rail inputs.
  3. `heralded_cz`'s CZ truth table/phase behavior is verified against computational-basis inputs.
  4. A literature-comparison note documents the measured value alongside the design doc's previously-flagged, unverified literature figures (1/9 post-selected, ~2/27 heralded) — descriptive only, no equality claimed.
**Plans:** 1 plan

Plans:
- [x] 10-01-PLAN.md — Herald-success probability + CZ phase-sign de-risking (heralded_cz_derisking.py + tests + docs update)

**Results (measured 2026-08-06):** `heralded_cz` herald-success probability confirmed at exactly 2/27 (~0.074074), uniform across 4 computational-basis inputs + 2 superposition spot-checks, read from `global_perf`/`physical_perf`/`logical_perf` (never shot-sampled). CZ phase sign confirmed via `Simulator.prob_amplitude`: negative only on `|1,1⟩`, matching `diag(1,1,1,-1)`. `logical_perf` confirmed pure herald condition (empty `post_select_fn`, zero-leakage `Analyzer` truth table). Literature-comparison note added to `docs/iqp-photonic-encoding.md` (descriptive, no equality claimed). Full 32-test suite (26 existing + 6 new pytest functions covering 12 parametrized cases) green, no regression. Verified 4/4 must-haves.

#### Phase 11: CZ Insertion Unit & Weight-2 Circuit Composition
**Goal**: The full weight-2 generator circuit is implemented — `PBS`→`heralded_cz`→`PBS` plus the two `WP(π/4,0)` single-qubit corrections — composed via `Processor`-level composition, reusing every existing weight-1 builder unmodified.
**Depends on**: Phase 10 (confirms the primitive behaves as assumed before building on it)
**Requirements**: WT2-01
**Success Criteria** (what must be TRUE):
  1. `build_cz_insertion(n, i, j)` (PBS-wrap → `heralded_cz` → PBS-unwrap) is implemented and its polarization-basis round-trip is verified against a known truth table at the module's existing `(2i,2i+1)`/`(2j,2j+1)` port convention.
  2. The full weight-2 pipeline is composed via `Processor.add()`, reusing `build_state_prep_circuit`, `build_conjugation_circuit`, and `build_readout_circuit` unmodified, with the `π/4` single-qubit corrections folded additively into `build_diagonal_layer_circuit`'s existing `thetas` argument.
  3. The assembled processor's `heralds` property is confirmed non-empty immediately after assembly (calibration check, guards against silently running an unheralded raw unitary).
  4. The existing 26-test weight-1 suite still passes unmodified (regression check) after this phase's changes.
**Plans**: 2 plans (2 waves, sequential)

Plans:
- [x] 11-01-PLAN.md — build_cz_insertion(n, i, j): PBS-wrap -> heralded_cz -> PBS-unwrap, internal ctrl/data convention adapter, truth-table + superposition verification
- [x] 11-02-PLAN.md — build_weight2_processor(n, i, j, thetas): full Processor-level pipeline composition, additive pi/4 theta folding, herald re-registration, non-regression snapshot check

**Results (measured 2026-08-06):** `build_cz_insertion(n, i, j)` implemented as a local `Circuit(6)` (PBS-wrap -> PERM-adapted `heralded_cz` -> PBS-unwrap), truth-table verified to reproduce `diag(1,1,1,-1)` exactly (`|amplitude|^2 == 2/27`, sign negative only on `|1,1⟩`) across all 4 computational-basis combos plus `|+⟩|+⟩`/`|+⟩|0⟩` superposition spot-checks. The ctrl/data convention mismatch found in research (`heralded_cz` uses Perceval's own `Encoding.DUAL_RAIL` standard, the mirror image of this module's PBS-derived convention) is fully internal to the function via a `PERM([1,0])` adapter — confirmed from source (`heralded_cz.py`'s `Port(Encoding.DUAL_RAIL, ...)` declarations, `port.py`'s encoding definition) to be a convention mismatch between two independently-correct components, not a bug on either side. `build_weight2_processor(n, i, j, thetas)` composes the full `Processor(2n+2)` pipeline via `Processor.add()`, reusing all four weight-1 builders unmodified (confirmed via sha256 snapshot regression test); `pi/4` corrections fold additively into `build_diagonal_layer_circuit`'s `thetas`; heralds confirmed registered at exact global indices `{2n:1, 2n+1:1}` immediately after assembly. All 4 Success Criteria verified (gsd-verifier: 4/4, independently re-executed, not just trusted from SUMMARYs). Discovered and documented a genuine Perceval library limitation carried forward to Phase 12: `Processor.probs()` crashes unconditionally when a registered herald is combined with any `PBS`-containing circuit (independently reproduced by both the orchestrator and the verifier) — Phase 12's TVD-validation design must route around this from the start. Full 107-test suite green, zero regressions to the pre-existing 32-test weight-1 suite.

#### Phase 12: Exact Reference Extension & TVD Validation
**Goal**: Weight-2 is validated to the same rigor bar weight-1 already cleared — exact reference, herald-conditioned TVD comparison, explicit honest failure/residual reporting, no silently-discarded probability mass.
**Depends on**: Phase 11 (needs a working weight-2 pipeline to validate against)
**Requirements**: WT2-02, WT2-03, WT2-05, WT2-06
**Success Criteria** (what must be TRUE):
  1. `exact_qubit_iqp_distribution` (or a sibling function) is extended to include `Z_i·Z_j` pair terms, reusing the existing bit-ordering/Z-eigenvalue convention already established for weight-1.
  2. The herald-conditioned photonic distribution is computed with herald-failure probability and out-of-subspace decode residual reported as two separate, explicit numbers — never merged into one figure, never silently renormalized away.
  3. A TVD test at n=2, θ=π/4 passes, comparing the extended exact reference against the herald-conditioned photonic distribution, in the same style/tolerance convention as `test_enc04_toy_validation_runs_end_to_end` (TVD < 1e-6).
  4. New test coverage is added to `tests/test_iqp_photonic_encoding.py` for WT2-01 through WT2-05, matching existing test conventions, and the full suite (existing 26 + new tests) passes.
**Plans**: TBD

#### Phase 13: Weight-1 + Weight-2 Composability Validation
**Goal**: Weight-1 and weight-2 generator layers are confirmed to compose correctly within the same circuit, not just in isolation.
**Depends on**: Phase 12 (needs the validated weight-2 pipeline and exact reference to build the mixed-circuit test against)
**Requirements**: WT2-07
**Success Criteria** (what must be TRUE):
  1. An n=3 mixed generator test (2 weight-1 terms + 1 weight-2 term in the same circuit) passes, confirming weight-1 and weight-2 layers compose correctly.
  2. The test is added to `tests/test_iqp_photonic_encoding.py`, matching existing test conventions.
  3. The full test suite (weight-1's original 26 tests + all weight-2 tests added across Phases 10-13) is green after this addition.
**Plans**: TBD

## Progress

**Execution Order:**
Phases execute in numeric order: 10 → 11 → 12 → 13

| Phase | Milestone | Plans Complete | Status | Completed |
|-------|-----------|-----------------|--------|-----------|
| 1. Environment & Architecture Foundation | v1.0 | - | Complete | 2026-07-19 |
| 2. Generator Data & Loss Infrastructure | v1.0 | 4/4 | Complete | 2026-07-19 |
| 3. End-to-End Training Run | v1.0 | 1/1 | Complete | 2026-07-24 |
| 4. Generative Quality | v1.0 | 3/3 | Concluded (GEN-07 not met) | 2026-07-25 |
| 5. Benchmarking | v1.0 | 1/1 | Complete | 2026-07-29 |
| 6. Documentation & Publication | v1.0 | 2/2 | Complete | 2026-07-29 |
| 7. Mechanism Validation | (unassigned) | 2/2 | Complete — verified 10/10, owner interpretation pending | 2026-07-30 |
| 8. Literature Scoping & Prerequisites | v2.0 | 4/4 | Complete — verified 10/10, LIT-04: **Go** | 2026-08-04 |
| 9. Encoding Design | v2.0 | 4/4 | Complete — polarization encoding, TVD ~1e-16 at n=2,3, UAT 8/8 | 2026-08-05 |
| 10. Heralded-CZ Primitive De-Risking | v2.1 | 1/1 | Complete — verified 4/4, 2/27 herald-success confirmed | 2026-08-06 |
| 11. CZ Insertion Unit & Weight-2 Circuit Composition | v2.1 | 2/2 | Complete — verified 4/4, weight-2 pipeline built and truth-table verified | 2026-08-06 |
| 12. Exact Reference Extension & TVD Validation | v2.1 | 0/TBD | Not started | - |
| 13. Weight-1 + Weight-2 Composability Validation | v2.1 | 0/TBD | Not started | - |

v2.0 milestone (Phases 8-9) shipped 2026-08-05. Full phase and requirement detail archived to `.planning/milestones/v2.0-ROADMAP.md` and `.planning/milestones/v2.0-REQUIREMENTS.md`. v2.1 (Weight-2 Implementation, Phases 10-13) roadmap created 2026-08-06 — 8/8 v1 requirements mapped, no orphans. Phase 10 (Heralded-CZ Primitive De-Risking) completed 2026-08-06 — WT2-04, WT2-08 satisfied. Phase 11 (CZ Insertion Unit & Weight-2 Circuit Composition) completed and verified 2026-08-06 — WT2-01 satisfied, full weight-2 circuit built and truth-table verified, 107-test suite green. Next: `/gsd:discuss-phase 12`.
