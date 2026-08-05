# Roadmap: MerLin Photonic Generative Modeling

## Milestones

- ✅ **v1.0 Photonic Generator** — Phases 1-6 (shipped 2026-07-29)
- ✅ **v2.0 IQP → Photonic Encoding** — Phases 8-9 (shipped 2026-08-05)

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

## Progress

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

v2.0 milestone (Phases 8-9) shipped 2026-08-05. Full phase and requirement detail archived to `.planning/milestones/v2.0-ROADMAP.md` and `.planning/milestones/v2.0-REQUIREMENTS.md`. Next milestone not yet started — run `/gsd:new-milestone` to begin.
