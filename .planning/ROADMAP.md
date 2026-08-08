# Roadmap: MerLin Photonic Generative Modeling

## Milestones

- ✅ **v1.0 Photonic Generator** — Phases 1-6 (shipped 2026-07-29)
- ✅ **v2.0 IQP → Photonic Encoding** — Phases 8-9 (shipped 2026-08-05)
- ✅ **v2.1 Weight-2 Implementation** — Phases 10-13 (shipped 2026-08-06)
- 🚧 **v3.0 IQP Circuit Study & Write-Up** — Phases 14-21 (in progress, started 2026-08-07)

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

## v3.0 IQP Circuit Study & Write-Up (Phases 14-21) — IN PROGRESS

**Goal:** Turn the validated weight-1/weight-2 IQP-photonic encoding into the project's actual research payoff — measure trainability (barren-plateau behavior) and hardness-under-loss, validate a continuously-tunable weight-2 gate, add an independent Julia-based numeric verification path, and write up the findings. All four Must-have deliverables (TRAIN/STUDY-01, HARD/STUDY-02, ARB-01, WRITE-01) are decoupled from each other per this milestone's own research (`.planning/research/PITFALLS.md` Pitfall 25) — no phase blocks on another's open-ended risk (specifically, ARB-01's genuinely-open-research status must never become a single point of failure for the other three).

**Note on the "34 requirements" instruction vs. the actual count:** `REQUIREMENTS.md`'s own summary line states "34 total (TRAIN: 8, HARD: 7, ARB: 9, VERIFY: 4, WRITE: 7)" — but 8+7+9+4+7 = **35**, not 34. This is an arithmetic error in the requirements doc's own header, not a scope change. All 35 actual requirement IDs (TRAIN-01..08, HARD-01..07, ARB-01..09, VERIFY-01..04, WRITE-01..07) are mapped below and the header has been corrected in `REQUIREMENTS.md`'s traceability section.

**Mid-milestone checkpoint (per `PITFALLS.md` Pitfall 26 — a named roadmap artifact, not left implicit):**
Target date: **~2026-08-20** (roughly the milestone's midpoint, mirroring v1.0's Jul-25 stall-risk-checkpoint template). At that date, answer four questions with concrete evidence (a running script, a measured number, a committed file — not "in progress"):
1. VERIFY-01 (Julia toolchain): did `juliaup`/Yao.jl/BosonSampling.jl actually install and run a hello-world circuit? (Phase 14)
2. ARB-01: has the tunable gate cleared its dedicated TVD/composability validation, or is it still open? (Phases 15-16)
3. TRAIN-01..05: does a real gradient-variance-vs-n dataset exist yet, with a stated max-n ceiling? (Phase 17)
4. HARD-01..05: has arXiv:2510.24137 been read, and does a real TVD-vs-η dataset exist yet? (Phase 18)
If any item is stalled at this checkpoint, say so plainly (per this project's established honesty norm) rather than letting the date pass unremarked — this does not require abandoning the "no fallback" scope decision, only an explicit, recorded acknowledgment.

### Phase 14: Julia Toolchain Spike

**Goal:** Confirm the Julia toolchain (`juliaup`, Yao.jl, BosonSampling.jl) installs and runs a hello-world circuit successfully. **This is deliberately this milestone's earliest, most decoupled phase — a stall-risk checkpoint, not an implementation detail.** The owner committed to a brand-new Julia toolchain as Must-have despite research explicitly flagging it as this milestone's single biggest risk of repeating the historical stall pattern: a prior self-directed track (PennyLane) stalled indefinitely from May 2026 after committing to an unfamiliar framework with no early go/no-go signal (documented in `CLAUDE.md` and `PROJECT.md`). Mirroring this project's own v1.0 Jul-25 stall-risk-checkpoint precedent: if the toolchain can't produce a hello-world result early, that's a visible, actionable signal — not something discovered only when VERIFY-02/03/04 are due.
**Depends on:** None. Deliberately decoupled from every other phase's results.
**Requirements:** VERIFY-01
**Plans:** 1 plan (1 wave, single autonomous plan — install + both hello-worlds + go/no-go verdict, sequential by nature of a from-scratch toolchain install)

Plans:
- [x] 14-01-PLAN.md — Install juliaup/Julia 1.10 LTS, scaffold `julia/` project, run Yao.jl + BosonSampling.jl hello-world circuits asserted against hand-derived analytical values, record go/no-go/partial-go verdict in `results/phase14_julia_toolchain_summary.md` + `STATE.md`

**Result: FULL GO.** Julia 1.10.11 LTS + Yao.jl 0.9.1 + BosonSampling.jl 1.0.2 all installed and hello-world-verified against hand-derived analytical values (Bell state 0.5/0/0/0.5; 50/50 beamsplitter 0.5/0.5). No alternate paths needed for either component. Verified 4/4 must-haves — see `.planning/phases/14-julia-toolchain-spike/14-VERIFICATION.md`.

**Success criteria:**
1. `juliaup` installed; `julia --version` runs successfully from the project's shell.
2. Yao.jl added to the project's Julia environment and a hello-world circuit (e.g., a small qubit circuit with a measurement) runs and produces output.
3. BosonSampling.jl added and a hello-world linear-optical circuit (e.g., a 2-mode beamsplitter on a Fock input) runs and produces output.
4. If either package fails to install or run within a stated, small time-box, that failure is reported plainly — a concrete go/no-go signal exists before any further Julia work (Phase 19) is attempted, rather than an open-ended struggle.

---

### Phase 15: ARB-01 Core Gate De-Risking & Validation

**Goal:** Validate `PostProcessedControlledRotationsItem` (the continuously-tunable two-qubit diagonal phase gate) to the same rigor bar `heralded_cz` cleared in v2.1 — de-risk it standalone, derive the general-α operator identity, and confirm it via TVD against the extended exact qubit-side reference. ARB-01's "does a tunable gate exist" question is already closed by research (confirmed to exist and work); this phase is validation work, not open research.
**Depends on:** None beyond already-shipped weight-1/weight-2 modules (Phases 9, 11-13). Independent of TRAIN, HARD, and VERIFY — no phase in this milestone blocks on ARB-01, and ARB-01 blocks on nothing else.
**Requirements:** ARB-01, ARB-02, ARB-03, ARB-04, ARB-05, ARB-06
**Plans:** 4 plans (3 waves — 15-02/15-03 parallel in wave 2, both depend only on 15-01; 15-04 depends on both)

Plans:
- [x] 15-01-PLAN.md — CP(alpha) standalone gate de-risking: phase/structure confirmed at 3 non-trivial alpha + the alpha=pi boundary (ARB-01)
- [x] 15-02-PLAN.md — CP circuit wiring de-risking: mode-convention adapter for the bare dual-rail core, isolated from the full pipeline (real, budgeted debugging risk per research)
- [x] 15-03-PLAN.md — ARB-02 general-alpha operator identity: attempt-first owner checkpoint + written derivation in docs/iqp-photonic-encoding.md
- [x] 15-04-PLAN.md — Full CP-insertion pipeline, TVD validation (n=2,3), boundary-agreement test, and heralded_cz comparison table (ARB-03, ARB-04, ARB-05, ARB-06)

**Result: Complete — verified 5/5 must-haves.** All success criteria below cleared; TVD at floating-point-noise level (well under the 1e-6 bar), general-α operator identity and closed-form success probability both derived (owner-attempted, Socratic method) and documented, `heralded_cz` comparison table written. See `15-VERIFICATION.md` for the independently-reproduced evidence.

**Success criteria:**
1. Gate phase/structure confirmed at ≥3 non-trivial α values via `Simulator.prob_amplitude`, matching the operator identity's prediction (extends the single spot-check already done in research).
2. General-α operator identity (`CP(α)` ↔ `exp(iθZ_iZ_j)`) derived and written down, extending `docs/iqp-photonic-encoding.md`'s existing fixed-π/4 derivation.
3. TVD validation against the extended exact qubit-side reference passes at ≥1 representative non-special α, at the same rigor bar weight-2 cleared (target ≤1e-6, ideally far below).
4. Success probability reported as an explicit table/curve as a function of α — never collapsed to a single number.
5. Written comparison against the existing fixed-π/4 `heralded_cz` construction (different gate family: post-selection + ancilla vacuum vs. ancilla heralding, stated plainly) documented; new test coverage added to `tests/test_iqp_photonic_encoding.py` matching existing conventions, passing.

---

### Phase 16: ARB-01 Extended Validation & Postselection Bookkeeping

**Goal:** Extend the core ARB-01 gate to a mixed-generator composability test and a denser α characterization, and formally verify its `set_postselection` local→global ancilla mode-index translation via Forge — a narrow, bounded discrete-correctness check, not a numeric verifier.
**Depends on:** Phase 15 (needs the actual gate wiring and `set_postselection` plumbing to exist before it can be modeled or extended).
**Requirements:** ARB-07, ARB-08, ARB-09
**Plans:** 3 plans (2 waves — 16-01/16-02 parallel in wave 1, both independent; 16-03 depends on 16-02 for a shared docs/iqp-photonic-encoding.md edit, not a logical dependency)

Plans:
- [ ] 16-01-PLAN.md — ARB-07: n=3 mixed weight-1 + arbitrary-θ weight-2 composability test
- [ ] 16-02-PLAN.md — ARB-08: 16-point α sweep, plotted success-probability curve
- [ ] 16-03-PLAN.md — ARB-09: Forge model of the ancilla mode-mapping dict's injectivity (owner attempt-first checkpoint)

**Success criteria:**
1. n=3 mixed weight-1 + arbitrary-θ weight-2 composability test passes (TVD under the same threshold), direct parallel to Phase 13's existing test.
2. Denser α sweep (8-16 points across [0, 2π)) run, with success probability plotted as a continuous curve.
3. Forge model of the gate's `set_postselection` local→global ancilla mode-index translation built and run, confirming the mapping is valid and non-aliasing (or surfacing and documenting a real bug if one is found).

---

### Phase 17: Trainability / Barren-Plateau Study

**Goal:** Measure whether the weight-1(+weight-2) IQP-photonic circuit shows barren-plateau behavior, via exact parameter-shift gradients (not MerLin `QuantumLayer` autograd, which architecture research confirmed cannot accept this circuit's polarization-annotated states) — a specific measured claim, reported honestly either direction.
**Depends on:** None beyond already-shipped weight-1/weight-2 modules. Independent of ARB, HARD, and VERIFY — this phase does not wait on ARB-01's outcome.
**Requirements:** TRAIN-01, TRAIN-02, TRAIN-03, TRAIN-04, TRAIN-05, TRAIN-06, TRAIN-07, TRAIN-08

**Success criteria:**
1. Gradient-variance sweep computed via exact parameter-shift across ≥3 system sizes, ≥100 independent random parameter draws each, with an explicit poly-vs-exponential model comparison (curve fit + goodness-of-fit, not eyeballed).
2. Parameter-initialization distribution and per-circuit energy/photon-number normalization stated explicitly and controlled/reported across the sweep.
3. Generator scope of the sweep (weight-1-only vs. mixed) stated explicitly with reasoning; mixed weight-1+weight-2 sweep run (reusing Phase 13's validated composability) if in scope.
4. Max reachable system size `n` honestly reported, stated explicitly relative to both `docs/iqp-baseline.md`'s n≥6 qubit-baseline threshold and the N=10→24 photonic-postselection literature fit-flip threshold (arXiv:2605.11879) — extended toward N≈20-24 if compute allows, honestly reported if not reached.
5. Result cross-referenced against `docs/iqp-baseline.md`'s qubit-side empirical plateau rule (97.9% accuracy, 283 rows) — does it transfer to the photonic realization?

---

### Phase 18: Hardness-Under-Loss Assessment

**Goal:** Measure whether the sampling-hardness argument survives realistic photon loss, via `Processor.probs()` + `NoiseModel` (not `Analyzer`, which silently ignores loss), grounded in a named asymptotic threshold from the literature, reported honestly either direction. **HARD-03 (full read of arXiv:2510.24137) is the first, near-zero-code step within this phase, not the last** — it gates this phase's central claim (where this project's tested loss levels sit relative to the known threshold) and must not be left implicit.
**Depends on:** None beyond already-shipped weight-1/weight-2 modules. Independent of ARB, TRAIN, and VERIFY — this phase does not wait on ARB-01's outcome.
**Requirements:** HARD-01, HARD-02, HARD-03, HARD-04, HARD-05, HARD-06, HARD-07

**Success criteria:**
1. arXiv:2510.24137 read in full (not abstract-only); its noisy-IQP-specific threshold formula (if stated) extracted and cited — done *before* the loss-sweep methodology below is finalized.
2. Loss sweep run via `Processor.probs()` + `NoiseModel(transmittance=η)` over a defined η grid.
3. Cross-checked against Perceval's independently-implemented `LossSimulator`/`LC` ancilla-beamsplitter loss model at ≥1 shared η, agreement confirmed within a stated tolerance.
4. This project's fractional-loss model explicitly positioned against Aaronson-Brod's fixed-loss-count regime — states plainly which regime this project's tested loss levels actually sit in.
5. TVD-vs-η tracked against both the lossless reference and an explicitly-defined classically-easy baseline distribution; weight-2 loss sweep (photon loss compounded with `heralded_cz`'s herald-failure probability) included; explicit "what this does/doesn't establish" scope statement written.

---

### Phase 19: Independent Julia Cross-Checks

**Goal:** Independently cross-check the Python/Perceval pipeline's exact and lossy distributions using the Julia toolchain confirmed working in Phase 14 — the full cross-check scripts, sequenced after real Python-side numbers exist to diff against.
**Depends on:** Phase 14 (Julia toolchain must be confirmed working first); Phase 18 (VERIFY-04 specifically needs HARD's TVD-vs-η dataset to cross-check against). VERIFY-02/03 reuse the already-shipped weight-1/weight-2 exact distributions (Phases 9, 11-13) and are bundled into this same phase rather than run separately, to keep the Julia toolchain's engagement narrow and time-boxed (per `PITFALLS.md` Pitfall 23) instead of returning to it multiple times.
**Requirements:** VERIFY-02, VERIFY-03, VERIFY-04

**Success criteria:**
1. Yao.jl reproduces the exact qubit-side IQP reference distribution (weight-1, at least n=2) within a stated tolerance of the existing Python/NumPy implementation.
2. BosonSampling.jl reproduces the photonic-level exact distribution (weight-1 and/or weight-2) within a stated tolerance of Perceval's results, for at least one shared test case.
3. BosonSampling.jl cross-checks Phase 18's loss-model numbers at ≥1 shared η; agreement (or a documented, honestly-reported disagreement) stated against the Python-computed TVD-vs-η result.

---

### Phase 20: Technical Write-Up

**Goal:** Write up STUDY-01 (Phase 17), STUDY-02 (Phase 18), and ARB-01's (Phases 15-16) findings as the project's technical findings document — methodology-stated-before-results, honest negative/inconclusive framing wherever the data warrants it, matching this project's existing GEN-07/LIT-04/Phase-7 rigor bar. Per research (`FEATURES.md`): this phase's *structure* (methodology-first, literature-comparison tables, explicit scope statements) is reasonable to draft early, in parallel with Phases 15-18, as a template to fill in — but the phase cannot be substantively completed until those phases have at least first-pass results.
**Depends on:** Phase 16 (ARB-01's full outcome), Phase 17 (TRAIN's dataset), Phase 18 (HARD's dataset). Does not require Phase 19 (Julia cross-check results are supplementary evidence, not a stated WRITE-01..06 requirement — include if ready, do not block on it).
**Requirements:** WRITE-01, WRITE-02, WRITE-03, WRITE-04, WRITE-05, WRITE-06

**Success criteria:**
1. Methodology-stated-before-results structure exists for each of the trainability, hardness-under-loss, and ARB-01 sections.
2. Explicit comparison table against each named literature baseline (McClean et al., Aaronson-Brod, arXiv:2510.24137, arXiv:2405.01395, `docs/iqp-baseline.md`'s own empirical rule) — stated per baseline as consistent with / inconsistent with / silent relative to.
3. Honest negative/inconclusive framing applied wherever the data warrants it, in the same direct language already used for GEN-07/LIT-04/Phase 7's neighbor-locality verdict.
4. Explicit "what this does/doesn't establish" scope paragraph present for each of the three sections.
5. Self-explanation checkpoint transcripts recorded (owner's own interpretation transcribed first); every reported number traceable to a specific script/test/notebook cell, with a fixed seed where randomness is involved.

---

### Phase 21: External-Facing Framing Pass

**Goal:** Produce an external-facing framing pass (README/case-study level) of the milestone's findings, following this project's established "mechanism-not-magic, ownership-forward" convention — kept separate from Phase 20's candid internal write-up, which stays unvarnished as-is.
**Depends on:** Phase 20 (the internal write-up must exist before it can be externally reframed).
**Requirements:** WRITE-07

**Success criteria:**
1. External-facing summary (README section and/or case-study material) written, distinct from Phase 20's internal technical document.
2. Framing follows the project's established "mechanism-not-magic, ownership-forward" convention without softening any of Phase 20's honest verdicts (positive or negative).

## Progress

**Execution Order (v1.0-v2.1, shipped):**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6 → 7 → 8 → 9 → 10 → 11 → 12 → 13

**Execution Order (v3.0, in progress) — waves, per dependency structure above:**
- Wave 1 (parallel, no interdependencies): Phase 14, Phase 15, Phase 17, Phase 18
- Wave 2: Phase 16 (depends on 15), Phase 19 (depends on 14 + 18)
- Wave 3: Phase 20 (depends on 16, 17, 18)
- Wave 4: Phase 21 (depends on 20)

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
| 12. Exact Reference Extension & TVD Validation | v2.1 | 2/2 | Complete — verified 4/4, TVD=2.6e-15 at locked gate | 2026-08-06 |
| 13. Weight-1 + Weight-2 Composability Validation | v2.1 | 1/1 | Complete — verified 3/3, 118/118 suite green | 2026-08-06 |
| 14. Julia Toolchain Spike | v3.0 | 1/1 | Complete — verified 4/4, FULL GO | 2026-08-07 |
| 15. ARB-01 Core Gate De-Risking & Validation | v3.0 | 4/4 | Complete — verified 5/5, TVD at floating-point-noise level | 2026-08-07 |
| 16. ARB-01 Extended Validation & Postselection Bookkeeping | v3.0 | 0/? | Not started | — |
| 17. Trainability / Barren-Plateau Study | v3.0 | 0/? | Not started | — |
| 18. Hardness-Under-Loss Assessment | v3.0 | 0/? | Not started | — |
| 19. Independent Julia Cross-Checks | v3.0 | 0/? | Not started | — |
| 20. Technical Write-Up | v3.0 | 0/? | Not started | — |
| 21. External-Facing Framing Pass | v3.0 | 0/? | Not started | — |

v2.0 milestone (Phases 8-9) shipped 2026-08-05. v2.1 milestone (Phases 10-13, Weight-2 Implementation) shipped 2026-08-06. v3.0 milestone (Phases 14-21, IQP Circuit Study & Write-Up) roadmap created 2026-08-07 — 35 v1 requirements mapped across 8 phases (see `REQUIREMENTS.md` note on the corrected 34→35 count), 100% coverage validated, no orphans. Full phase and requirement detail for shipped milestones archived to `.planning/milestones/v2.0-ROADMAP.md`/`v2.0-REQUIREMENTS.md` and `.planning/milestones/v2.1-ROADMAP.md`/`v2.1-REQUIREMENTS.md`/`v2.1-MILESTONE-AUDIT.md`.
