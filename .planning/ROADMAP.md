# Roadmap: MerLin Photonic Generative Modeling

## Milestones

- ✅ **v1.0 Photonic Generator** — Phases 1-6 (shipped 2026-07-29)
- ✅ **v2.0 IQP → Photonic Encoding** — Phases 8-9 (shipped 2026-08-05)
- ✅ **v2.1 Weight-2 Implementation** — Phases 10-13 (shipped 2026-08-06)
- ✅ **v3.0 IQP Circuit Study & Write-Up** — Phases 14-21 + 17.1 + 22 + 23 (shipped 2026-08-24)
- ✅ **v3.1 Correction** — Phase 24 (shipped 2026-09-04; corrected two v3.0 findings an external audit found to be pipeline artifacts)
- 🔧 **v3.2 Correction (Audit Response)** — Phase 25 (opened 2026-09-05; corrects overreach in the v3.1 correction itself plus code-level defects a second independent audit found)

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

<details>
<summary>✅ v3.1 Correction (Phase 24) — SHIPPED 2026-09-04</summary>

- [x] Phase 24: v3.1 Correction (executed interactively, no PLAN.md; +2 `/gsd-quick` tasks) — completed 2026-09-04, 12/13 requirements shipped, NULL-01 tracked as a known gap (owner-gated, not blocking)

Full detail: [`.planning/milestones/v3.1-ROADMAP.md`](milestones/v3.1-ROADMAP.md)
Requirements: [`.planning/milestones/v3.1-REQUIREMENTS.md`](milestones/v3.1-REQUIREMENTS.md)
Audit: [`.planning/milestones/v3.1-MILESTONE-AUDIT.md`](milestones/v3.1-MILESTONE-AUDIT.md)

</details>

### Phase 25: v3.2 Correction (Audit Response) — opened 2026-09-05 (in progress)

**Goal:** Correct two places where the v3.1 correction itself overreached (CONCEPT-01: an exact classical reference mistaken for a mechanism-removing control; CONCEPT-02: the `mixed` scope's "hardness candidate" framing never checked whether its one-fixed-pair entangling structure scales with `n` — it doesn't), retract or narrow TRAIN-10's mismatched-statistics negative result (CONCEPT-03), and fix the code-level defects a second independent audit (GPT-6 Astra) found: a plateau classifier that labels increasing curves "plateau," `fit_and_compare` contradicting its own single-convergence contract, chunked-sweep double-counting, Julia scripts exiting 0 on disagreement, and a null-result gate that silently skips missing CSVs.
**Depends on:** `docs/trainability-study.md`/`docs/hardness-under-loss-study.md` (the documents being corrected); `docs/audits/2026-09-05-codebase-audit.md` and its two probe scripts.
**Requirements:** [`.planning/REQUIREMENTS.md`](REQUIREMENTS.md) — CONCEPT-01..03, CORR-08..17, GATE-02/03.
**Note:** phases 25-31 are also claimed by the still-unmerged v4.0 plan (PR #3, `claude/merlin-photonic-iqp-audit-e8144c`) — one of the two will need renumbering when the other merges.

**Success criteria:**
1. CONCEPT-01..03 each have an owner-authored resolution recorded in the affected document(s), dated and additive.
2. CORR-08, CORR-09, CORR-10, CORR-11, CORR-12 implemented with regression tests; `python -m pytest -q` green.
3. CORR-13..17 addressed or explicitly declined with a stated reason.
4. GATE-02/GATE-03 added to `CLAUDE.md`.
