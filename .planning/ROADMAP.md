# Roadmap: MerLin Photonic Generative Modeling

## Milestones

- ✅ **v1.0 Photonic Generator** — Phases 1-6 (shipped 2026-07-29)
- ✅ **v2.0 IQP → Photonic Encoding** — Phases 8-9 (shipped 2026-08-05)
- ✅ **v2.1 Weight-2 Implementation** — Phases 10-13 (shipped 2026-08-06)
- ✅ **v3.0 IQP Circuit Study & Write-Up** — Phases 14-21 + 17.1 + 22 + 23 (shipped 2026-08-24)
- 🔧 **v3.1 Correction** — Phase 24 (started 2026-09-03; corrects two v3.0 findings an external audit found to be pipeline artifacts)

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

<details>
<summary>✅ v2.1 Weight-2 Implementation (Phases 10-13) — SHIPPED 2026-08-06</summary>

- [x] Phase 10: Heralded-CZ Primitive De-Risking (1/1 plan) — completed 2026-08-06, 2/27 herald-success confirmed
- [x] Phase 11: CZ Insertion Unit & Weight-2 Circuit Composition (2/2 plans) — completed 2026-08-06, weight-2 pipeline built and truth-table verified
- [x] Phase 12: Exact Reference Extension & TVD Validation (2/2 plans) — completed 2026-08-06, TVD=2.6e-15 at locked gate
- [x] Phase 13: Weight-1 + Weight-2 Composability Validation (1/1 plan) — completed 2026-08-06, 118/118 suite green

Full detail: [`.planning/milestones/v2.1-ROADMAP.md`](milestones/v2.1-ROADMAP.md)
Requirements: [`.planning/milestones/v2.1-REQUIREMENTS.md`](milestones/v2.1-REQUIREMENTS.md)
Audit: [`.planning/milestones/v2.1-MILESTONE-AUDIT.md`](milestones/v2.1-MILESTONE-AUDIT.md)

</details>

<details>
<summary>✅ v3.0 IQP Circuit Study & Write-Up (Phases 14-21, 17.1, 22-23) — SHIPPED 2026-08-24</summary>

- [x] Phase 14: Julia Toolchain Spike (1/1 plan) — completed 2026-08-07, FULL GO (juliaup/Yao.jl/BosonSampling.jl)
- [x] Phase 15: ARB-01 Core Gate De-Risking & Validation (4/4 plans) — completed 2026-08-07, TVD at floating-point-noise level
- [x] Phase 16: ARB-01 Extended Validation & Postselection Bookkeeping (3/3 plans) — completed 2026-08-09, Forge confirms ancilla mode-mapping non-aliasing, no bugs found
- [x] Phase 17: Trainability / Barren-Plateau Study (7/7 plans) — completed 2026-08-11, exponential-decay signature found (uniform init)
- [x] Phase 17.1: Trainability Follow-Up — Bandwidth & Init Sensitivity (6/6 plans) — completed 2026-08-13, exp signature not robust to bandwidth; data-dependent init did not resolve inconclusive verdict
- [x] Phase 18: Hardness-Under-Loss Assessment (8/8 plans) — completed 2026-08-17, no correctness bugs, HARD-04 resolved honestly (no forced eta-to-depolarizing translation)
- [x] Phase 19: Independent Julia Cross-Checks (6/6 plans) — completed 2026-08-17, all 4 legs GO (1 real transpose-convention bug found and fixed)
- [x] Phase 20: Technical Write-Up (4/4 plans) — completed 2026-08-18, docs/technical-findings.md synthesis, Herbst et al. cross-reference corrects an earlier speculative guess
- [x] Phase 21: External-Facing Framing Pass (2/2 plans) — completed 2026-08-19, case-study + README pitch, pushed to origin
- [x] Phase 22: Multi-Pair Ancilla Allocation — Formal Verification (6/6 plans) — completed 2026-08-21, owner GO ruling on ancilla reuse; Forge lost to Python backtracking on its own axis (~123,000x), earned its place as a precise pre-implementation spec instead
- [x] Phase 23: Ancilla Lifecycle Safety — Formal Verification (3/3 plans) — completed 2026-08-22, structural trace/reachability check distinct from Phase 22's static result; self-explanation checkpoint re-run genuinely on 2026-08-23 after an unattended Codex session's original checkpoint was found to be fabricated and retracted

**What Forge actually added, across Phases 16/22/23 (owner-driven synthesis, 2026-08-23):** graded against the CS1710-corrected success criteria (finding an unanticipated scenario; trace/reachability properties; model as precise spec; verifying a design before building it) rather than "beats brute force." Verdict: earned its place on two of four criteria (precise spec, pre-implementation verification — Phases 22/23) plus a genuine trace/reachability check unique to Phase 23, but never surfaced an unanticipated scenario in any of the three Forge phases on this project — a real, stated limitation, not softened. See `docs/iqp-photonic-encoding.md` § "What Forge Actually Added (Phases 16, 22, 23)".

**Provenance note (2026-08-23):** Phase 23 was originally executed and closed via an unattended Codex session (2026-08-22) whose recorded "owner review" was later confirmed fabricated. Independently re-verified all technical content as sound (`23-VERIFICATION-independent.md`), then re-ran all 14 design-decision confirmations and a genuine self-explanation checkpoint live with the owner. The fabricated text was retracted in place, not deleted, per this project's candor convention. See `results/phase23_lifecycle_summary.md` § "Owner review" and `.planning/STATE.md`'s "Phase 23 provenance correction" section for the full record.

**Accepted tech debt at milestone close:** `.planning/milestones/v3.0-MILESTONE-AUDIT.md` found 12/51 requirements carry the newer `requirements-completed` SUMMARY frontmatter field a stricter audit schema checks for; the other 38 (plus one orphaned, `VERIFY-01`) predate that schema. Every phase's own `*-VERIFICATION.md` independently confirms 51/51 requirements satisfied at the behavior/implementation level — this is a metadata/provenance gap in legacy SUMMARY files, not a functional gap. Owner-accepted, not closed retroactively.

Full detail: [`.planning/milestones/v3.0-ROADMAP.md`](milestones/v3.0-ROADMAP.md)
Requirements: [`.planning/milestones/v3.0-REQUIREMENTS.md`](milestones/v3.0-REQUIREMENTS.md)
Audit: [`.planning/milestones/v3.0-MILESTONE-AUDIT.md`](milestones/v3.0-MILESTONE-AUDIT.md)

</details>

### Phase 24: v3.1 Correction — started 2026-09-03 (in progress)

**Goal:** Correct the public record after the 2026-09-03 external audit (Fable 5.1) established that v3.0's trainability "exponential decay" is the MMD loss normalization on a product distribution (the kernel is the identity when sigma is below grid bin spacing, so variance scales as 2^-n with no circuit content) and that hardness-under-loss's `tvd_to_lossless` equals `½(1 − eta^(n+2))` because the pipeline post-selects on full photon survival. Ship the two null results as owner-written tests against the shipped CSVs, dated additive corrections in every affected document, the throughput reframing of the hardness result, a CLAUDE.md null-result gate, an independent Codex review of the corrected text, and a drafted correction note to Vincent. No new experiments.
**Depends on:** Phase 20/21 documents (the things being corrected); audit artifact `claude.ai/code/artifact/2eb88fd5-d090-4933-82b8-396135c2f348`.
**Requirements:** [`.planning/REQUIREMENTS.md`](REQUIREMENTS.md) — NULL-01/02, CORR-01..07, REFRAME-01/02, GATE-01, REVIEW-01, COMM-01.
**Gate:** NULL-01 is owner-only and blocks every plan: `tests/v3_correction/test_null_results.py` must be filled and green before planning proceeds. Derivation by red/green experiment, not on paper (24-CONTEXT.md D-02).
**Plans:** not yet planned — see `24-CONTEXT.md` § Suggested plans (24-00 owner task, then 24-01..24-05).

**Success criteria:**
1. `python -m pytest -q` green including the promoted null-result tests over every shipped HARD row and the sigma ≤ 0.1 TRAIN rows.
2. Every document that stated the two findings (trainability-study, hardness-under-loss-study, technical-findings, README, iqp-baseline Rudolph row, lit-scoping, Post_Sept1 plan, case-study page) carries a dated additive correction that leads its section.
3. Hardness section leads with the throughput closed form `eta^(n+2k)·(2/27)^k`; TVD plots retitled as a pipeline check.
4. `CLAUDE.md` null-result gate present; `.claude/learnings/2026-09-03-null-result-gate-before-sweeps.md` exists.
5. `24-REVIEW.md` records the Codex null-result review and the disposition of each finding.
6. Vincent note drafted by the owner; send/hold decision logged in `24-CONTEXT.md`.

**Explicitly out of scope (v4.0 candidates, undecided):** structured simulator to n≈20+, Hamming-kernel trainability rerun, distinguishability noise, non-post-selected simulability analysis, herald-cost gradient variance, train-classical/deploy-photonic gap, KLM-vs-graph-state comparison.
