# Roadmap: MerLin Photonic Generative Modeling

## Milestones

- ✅ **v1.0 Photonic Generator** — Phases 1-6 (shipped 2026-07-29)
- 🚧 **v2.0 IQP → Photonic Encoding** — Phases 8-9 (in progress, started 2026-07-30)

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

**Details:**
Two experiments, in this order:
1. **Neighbor-locality test** — does `NaturallyOrderedGenerator`'s output have the property the correspondence-fix mechanism assumes: that list-neighbors (under the radius/center-of-mass ordering) move together more than random pairs when the circuit's parameters are nudged? Method B (Jacobian-based): compute `J = ∂q/∂θ` via autograd at several random parameter draws, compare `cosine_similarity(J[i,:], J[j,:])` for adjacent vs. random index pairs.
2. **Sigma re-sweep** — rerun Phase 4's `sweep.py` pattern (same `SIGMA_GRID`, same resumable-checkpoint structure) against the K=462 natural-order grid instead of the old K=400 grid, to check whether sigma=0.1 is still the best choice or whether the never-re-swept bandwidth was masking/inflating the correspondence fix's apparent benefit.

Not yet assigned to a v1.1 or later milestone — added directly to the roadmap per owner's explicit `/gsd:add-phase` request, continuing phase numbering from v1.0 rather than restarting at 1.

**Results (measured, not interpreted — owner's job per this repo's CLAUDE.md):**
- Neighbor-locality: pooled test **fails** the locked two-condition bar (`mean_diff=0.0096` vs. `min_effect=0.10`; p=0.00835 clears significance alone but the effect size doesn't). 13/20 draws individually show the expected direction. Trained checkpoint also fails (`mean_diff=0.0402`).
- Sigma re-sweep: K=462 argmax is still sigma=0.1 (`ring_mass=0.7145`) — no other tested sigma beats it. Same bandwidth already used for every reported K=462 result.
- Owner interpretation pending in both `results/phase7_*_summary.md` files.

### Phase 8: Literature Scoping & Prerequisites

**Goal:** Determine whether a discrete-variable (DV, Fock-space) linear-optical construction of IQP is worth designing at all — and confirm the technical/reference prerequisites that any subsequent design work depends on.
**Depends on:** None (new milestone; builds on v1.0's already-installed MerLin/Perceval environment, no code dependency on Phase 7)
**Requirements:** LIT-01, LIT-02, LIT-03, LIT-04, PREQ-01, PREQ-02
**Plans:** Not yet planned — run `/gsd:plan-phase 8`

**Success Criteria:**
1. A go/no-go verdict on Phase 9 (encoding design) is written down explicitly, citing both constructive and disconfirming search passes, with the stated time-box honored — "not ready" counted as a valid, reportable outcome if nothing viable is found (LIT-01, LIT-04)
2. Douce et al. (PRL 118, 070503, 2017, arXiv:1607.07605) has been read in full text (not abstract-level), with its CV-analogue construction (commuting diagonal gates, Hadamard-basis conjugation) summarized well enough to correctly position a DV design against it (LIT-02)
3. MerLin's reproduced-papers catalog is confirmed checked for IQP-adjacency — already complete, carried forward for coverage (LIT-03)
4. A working manual Perceval circuit (`Circuit`, `PS`, `BS`, `BasicState`, `Analyzer`) is built and run without the `QuantumLayer.simple()` wrapper, demonstrating low-level API fluency (PREQ-01)
5. Prior IQP + barren-plateau notes/results are compiled into a single reference doc (`docs/iqp-baseline.md`) as the qubit-side baseline for later comparison (PREQ-02)

### Phase 9: Encoding Design

**Goal:** Produce a defensible, on-paper mapping from IQP's structure onto Perceval's DV/Fock-space primitives — the milestone's actual novel-contribution deliverable.
**Depends on:** Phase 8 — contingent entirely on LIT-04's verdict being "go"; does not start if Phase 8 concludes "not ready"
**Requirements:** ENC-01, ENC-02, ENC-03, ENC-04, ENC-05
**Plans:** Not yet planned — run `/gsd:plan-phase 9` after Phase 8 completes with a "go" verdict

**Success Criteria:**
1. An on-paper mapping from IQP's commuting diagonal gates + Hadamard-basis conjugation to phase shifters, beamsplitters, and photon-number measurement is written in raw Perceval vocabulary, not MerLin's high-level builder DSL (ENC-01)
2. The mapping explicitly states how it differs from and extends the Douce et al. CV precedent, positioned as a distinct DV contribution rather than a restatement (ENC-02)
3. A concrete, falsifiable basis correspondence is stated between qubit computational-basis bitstrings and photonic Fock-state/photon-count outcomes — not a hand-wavy analogy (ENC-03)
4. A stated, checkable-in-principle validation plan (e.g., a small-scale classical comparison) exists, even though it won't run until a future implementation phase (ENC-04)
5. The mapping is documented in `docs/iqp-photonic-encoding.md`, and the owner can explain it unaided — same bar as the v1.0 self-explanation checkpoints (ENC-05)

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
| 8. Literature Scoping & Prerequisites | v2.0 | 0/? | Not started | — |
| 9. Encoding Design | v2.0 | 0/? | Not started (contingent on Phase 8 "go" verdict) | — |

v2.0 roadmap created 2026-07-30, continuing phase numbering from Phase 7 (starts at 8) per owner's explicit scoping decision. Next: `/gsd:plan-phase 8`.
