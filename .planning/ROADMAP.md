# Roadmap: MerLin Photonic Generative Modeling

## Milestones

- ✅ **v1.0 Photonic Generator** — Phases 1-6 (shipped 2026-07-29)
- ✅ **v2.0 IQP → Photonic Encoding** — Phases 8-9 (shipped 2026-08-05)
- ✅ **v2.1 Weight-2 Implementation** — Phases 10-13 (shipped 2026-08-06)
- ✅ **v3.0 IQP Circuit Study & Write-Up** — Phases 14-21 + 17.1 + 22 + 23 (shipped 2026-08-24)
- ✅ **v3.1 Correction** — Phase 24 (shipped 2026-09-04; corrected two v3.0 findings an external audit found to be pipeline artifacts)
- ⏳ **v4.0 Train Classically, Deploy Photonically (TCDP)** — Phases 25-31 (queued 2026-09-03, unblocked 2026-09-04 now that v3.1 has shipped; plan: `docs/v4-plan-train-classical-deploy-photonic.md`)

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

## v4.0 Train Classically, Deploy Photonically (Phases 25-31) — QUEUED 2026-09-03

**Milestone goal:** Measure how far a classically trained IQP Born machine's photonic post-selected output drifts from the distribution the trainer deployed, under partial distinguishability, multi-photon emission, and loss, as a function of gate count and n; then test whether classical training against the tomographed gate channels closes that gap. Requirements: [`.planning/REQUIREMENTS.md`](REQUIREMENTS.md) § v4.0. Binding design: [`docs/v4-plan-train-classical-deploy-photonic.md`](../docs/v4-plan-train-classical-deploy-photonic.md) table 5.1 and forbidden moves § 9. Starts when v3.1 is closed via `/gsd-complete-milestone`.

**Ordering:** 25 → 26 → 27 → 28 (owner) → 29 → 30 → 31. Phase 29 cannot start until Phase 27's `crosscheck_shared_qubit.json` is on disk and Phase 28's k=0 and noiseless nulls are filled.

### Phase 25: Classical Trainer Vendoring & Convention Lock
**Goal:** Bring the spring-semester classical IQP trainer into `merlin_iqp.classical` as a numpy-only package and prove its theta is this repo's theta.
**Depends on:** v3.1 (test conventions); sibling repo `C:\Users\cuqui\iqp-mmd-barren-plateau` at a recorded commit.
**Requirements:** TRAIN-01, TRAIN-02, TRAIN-03, TRAIN-04.
**Executor:** Codex (mechanical). Plan section 3 verbatim in the prompt.
**Success criteria:**
1. `import merlin_iqp.classical` succeeds in the venv with jax uninstalled; `PROVENANCE.md` names the sibling commit and every stripped path.
2. `tests/v4_tcdp/test_convention.py` green: Walsh-inverse vs `exact_qubit_iqp_distribution` < 1e-12; scaled-theta variants fail; exact MMD² at n=10 under 60 s.
3. Full suite still green.

### Phase 26: Noisy Gate Map Reconstruction
**Goal:** Reconstruct one noisy `CP(alpha)` gate as a trace-decreasing completely positive 2-qubit map by linear inversion from absolute post-selected Perceval probabilities (method verified 2026-09-03: exact to 5e-16 ideal, CP at V=0.9, 2.3 s per map); Perceval tomography is a fidelity cross-check only.
**Depends on:** none beyond Perceval 1.2.4 (probe facts in plan § 0).
**Requirements:** CHAN-01, CHAN-02, CHAN-03, CHAN-04.
**Executor:** Codex. Plan sections 4.2-4.3 verbatim.
**Success criteria:**
1. Ideal maps equal `(1/sigma_max^4) U ρ U†` to 1e-9 at four alphas with the phase on |11⟩; every cached map is CP and trace-non-increasing on all 16 matrix units; no per-gate renormalisation anywhere.
2. Input-dependence of success at V=0.9 recorded; repeatability 1e-13; Perceval tomography fidelity agrees with the map's exact conditional fidelity within 5e-3 at three noise points.
3. `alpha_key` yields exactly 63 keys; `map_timing.json` exists, measured at the slowest condition, and the 1134-map budget is under 3 single-core hours (measured ~45 min on 2026-09-03).

### Phase 27: Density-Matrix Deployment Simulator & Full-Fock Cross-Check
**Goal:** Compose gate channels on an n-qubit density matrix, prove it exact against the qubit reference and against full-Fock Perceval, and measure the one approximation it makes.
**Depends on:** Phase 25 (adapter), Phase 26 (channels).
**Requirements:** DEPLOY-01, DEPLOY-02, DEPLOY-03, DEPLOY-04, DEPLOY-05, REFRAME-03.
**Executor:** Codex. Plan sections 4.4-4.7 verbatim.
**Success criteria:**
1. Ideal maps reproduce `exact_qubit_iqp_distribution` to 1e-12 and the closed-form success product to 1e-9; k=0 ignores noisy maps; the hand-computed asymmetric n=3 fixture matches by named bitstring; no `4^n × 4^n` matrix is formed.
2. Composed vs full-Fock: TVD < 1e-9 **and** success probability agreement to 1e-9 for one gate at n=2 and n=3 (bystander, V-only and g2-only separately).
3. `results/v4_tcdp/crosscheck_shared_qubit.json` holds the shared-qubit discrepancies at three noise points × two alphas, with the pre-registered band applied.
4. Erasure helper passes hand-enumerated per-pattern tests including the shared-qubit case; heralded-CZ throughput overlay function exists.

### Phase 28: Owner Null Results (owner-only gate)
**Goal:** The owner writes, red first, what the deployment sweep outputs if the gates contribute nothing, before any sweep row exists.
**Depends on:** Phase 27 (the functions the nulls are tested against).
**Requirements:** NULL-03, NULL-04, NULL-05, NULL-06, NULL-07, NULL-08, NULL-09.
**Executor:** Owner for NULL-03..08 (Claude asks questions and points at rows; does not supply formulas, 24-CONTEXT.md D-02); Codex for NULL-09's pipeline control tests.
**Success criteria:**
1. `tests/v4_tcdp/test_nulls_tcdp.py` exists with all owner functions filled; k=0, noiseless, eta, both throughput, and NAT-ideal nulls green; scaling hypothesis marked xfail.
2. Each owner function's docstring carries the owner's one-sentence "why it has this shape".
3. `test_control_point_every_cell` and `test_control_point_can_fail` present and green on three cells.

### Phase 29: Classical Training Runs & Deployment Gap Sweep
**Goal:** Train every design-table cell classically, deploy each through the channel simulator across the hardware-anchored noise grid, and report the six metrics against the nulls.
**Depends on:** Phases 25-28.
**Requirements:** SWEEP-01, SWEEP-02, SWEEP-03, SWEEP-04, SWEEP-05.
**Executor:** Codex for scripts and figures; owner interprets first, Claude checks (CLAUDE.md rule).
**Success criteria:**
1. `results/v4_tcdp/trained/` complete and byte-reproducible; `deploy_sweep.csv` has every cell or `missing_cells.md` explains each gap.
2. Figures 1-4 regenerate from `tcdp_analysis.py` with no manual edits.
3. For each null, the write-up states matched / did not match; the headline outcome from plan § 5.6 is named.
4. Tomography wall-clock reported; any alpha rounding stated.

### Phase 30: Noise-Aware Classical Training
**Goal:** Train theta against the channel-composed deployed distribution and measure whether the gap closes at Ascella-grade noise. The milestone's method claim, either way it comes out.
**Depends on:** Phase 29 (baseline gaps).
**Requirements:** NAT-01, NAT-02, NAT-03.
**Executor:** Codex; owner reads timing before each n step.
**Success criteria:**
1. Finite-difference training loop on the exact deployed vector runs green end-to-end at n=4.
2. Before/after gap table at n ∈ {4,6,8}, k=n-1, Ascella noise, 5 seeds, next to the ideal-trained baseline.
3. Stop rule outcome recorded in `PROJECT.md` (completed, or stopped with numbers).

### Phase 31: Write-Up, Review Gate, Communication
**Goal:** Owner checkpoint, study document, mirrors, two-stage review, Gibbs pass, Vincent note.
**Depends on:** Phases 29-30.
**Requirements:** WRITE-07, WRITE-08, WRITE-09, REVIEW-02, COMM-02.
**Executor:** Owner (checkpoint, journal, note); Sonnet (prose, read aloud before commit); Fable/Opus then Codex (review).
**Success criteria:**
1. Owner checkpoint transcript recorded before prose; no hedging on the four questions.
2. `docs/tcdp-study.md`, technical-findings section, README paragraph, CLAUDE.md Repo state all present; every number traces to CSV or test.
3. REVIEW.md dispositions every finding from both reviews.
4. Vincent note drafted; send/hold recorded; journal entry in the owner's words.
