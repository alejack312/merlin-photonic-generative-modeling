# Roadmap: MerLin Photonic Generative Modeling

## Milestones

- ✅ **v1.0 Photonic Generator** — Phases 1-6 (shipped 2026-07-29)
- ✅ **v2.0 IQP → Photonic Encoding** — Phases 8-9 (shipped 2026-08-05)
- ✅ **v2.1 Weight-2 Implementation** — Phases 10-13 (shipped 2026-08-06)
- 🚧 **v3.0 IQP Circuit Study & Write-Up** — Phases 14-21 + 17.1 (in progress, started 2026-08-07; 17.1 added 2026-08-12)

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

**Note on the "34 requirements" instruction vs. the actual count:** `REQUIREMENTS.md`'s own summary line states "34 total (TRAIN: 8, HARD: 7, ARB: 9, VERIFY: 4, WRITE: 7)" — but 8+7+9+4+7 = **35**, not 34. This is an arithmetic error in the requirements doc's own header, not a scope change. All 35 actual requirement IDs (TRAIN-01..08, HARD-01..07, ARB-01..09, VERIFY-01..04, WRITE-01..07) are mapped below and the header has been corrected in `REQUIREMENTS.md`'s traceability section. **Updated 2026-08-12: the count is now 37**, following the owner-authorized addition of TRAIN-09/TRAIN-10 (Phase 17.1, below) — a real scope addition this time, not an arithmetic fix.

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
- [x] 16-01-PLAN.md — ARB-07: n=3 mixed weight-1 + arbitrary-θ weight-2 composability test
- [x] 16-02-PLAN.md — ARB-08: 16-point α sweep, plotted success-probability curve
- [x] 16-03-PLAN.md — ARB-09: Forge model of the ancilla mode-mapping dict's injectivity (owner attempt-first checkpoint)

**Result: Complete — verified 3/3 must-haves.** ARB-07's n=3 mixed-generator composability test passes (3/3 parametrized cases, TVD < 1e-6). ARB-08's 16-point α sweep matches the closed-form success probability to ~1e-9 at every point. ARB-09's Forge model (`forge/ancilla_mapping.frg`) confirms the ancilla mode-mapping dict is injective/non-aliasing for all valid `(n,i,j)` up to n=8 — no bug found. 145/145 full suite green throughout. See `16-VERIFICATION.md` for the independently-reproduced evidence.

**Success criteria:**
1. n=3 mixed weight-1 + arbitrary-θ weight-2 composability test passes (TVD under the same threshold), direct parallel to Phase 13's existing test.
2. Denser α sweep (8-16 points across [0, 2π)) run, with success probability plotted as a continuous curve.
3. Forge model of the gate's `set_postselection` local→global ancilla mode-index translation built and run, confirming the mapping is valid and non-aliasing (or surfacing and documenting a real bug if one is found).

---

### Phase 17: Trainability / Barren-Plateau Study

**Goal:** Measure whether the weight-1(+weight-2) IQP-photonic circuit shows barren-plateau behavior, via exact parameter-shift gradients (not MerLin `QuantumLayer` autograd, which architecture research confirmed cannot accept this circuit's polarization-annotated states) — a specific measured claim, reported honestly either direction.
**Depends on:** None beyond already-shipped weight-1/weight-2 modules. Independent of ARB, HARD, and VERIFY — this phase does not wait on ARB-01's outcome.
**Requirements:** TRAIN-01, TRAIN-02, TRAIN-03, TRAIN-04, TRAIN-05, TRAIN-06, TRAIN-07, TRAIN-08
**Plans:** 7 plans (4 waves — 17-01/02/03/04 parallel in wave 1, all independent; 17-05 depends on 17-01/02/03; 17-06 depends on 17-05; 17-07 depends on 17-06 and 17-04)

Plans:
- [x] 17-01-PLAN.md — Exact parameter-shift gradient (weight-1 + weight-2) of the WP(theta,0) gate, TDD against closed-form/finite-difference
- [x] 17-02-PLAN.md — Exact numpy MMD² loss + quadratic-form gradient, TDD against the existing torch reference
- [x] 17-03-PLAN.md — Per-n (K=2^n) target distribution & bin-index mapping, generalizing v1.0's fixed K=462 grid
- [x] 17-04-PLAN.md — Poly-vs-exponential curve fit with R²/AIC model comparison, TDD against synthetic ground-truth data
- [x] 17-05-PLAN.md — RNG substreams, summary statistics, and the gradient-variance sweep runner (integrates 17-01/02/03)
- [x] 17-06-PLAN.md — Run the real weight-1-only (n=2..6) and mixed (n=2..5) gradient-variance sweeps, plus best-effort n=7/n=6 stretch attempts
- [x] 17-07-PLAN.md — Curve-fit analysis, cross-reference against docs/iqp-baseline.md, and docs/trainability-study.md write-up

**Result: Complete — verified 8/8 must-haves (TRAIN-01..08).** Real gradient-variance data collected for weight-1 (n=2..6, both init schemes, 10 rows) and mixed (n=2..5, both init schemes, 8 rows). `weight1/uniform` and `mixed/uniform` show statistically clear exponential-decay (barren-plateau) signatures (R²=0.999, 0.910); `weight1/small_angle` and `mixed/small_angle` are inconclusive. Cross-reference against `docs/iqp-baseline.md`'s qubit-side empirical rule: `weight1/uniform` agrees, `mixed/uniform` disagrees — reported honestly, not smoothed over. Max n reached (weight1=6, mixed=5) falls short of the N=20-24 literature threshold; a STRETCH attempt toward n=7 weight-1/n=6 mixed was launched in the background per the phase's no-time-box decision and may still be running. Mid-execution, a genuine MemoryError bug was found and fixed in `iqp_photonic_encoding.py`'s `Analyzer(...)` calls (all 4 sites: `"*"` wildcard → explicit `list(allstate_iterator(input_state))`, root cause was an internal `min_detected_photons_filter(1)` forcing wasteful partial-photon-count enumeration; verified bit-identical output, 197/197 tests pass) plus a companion draw-chunking mechanism added to `trainability/sweep.py`/`gradient_variance_sweep.py` to work around a separate per-process memory leak in weight-2's larger circuit. See `17-VERIFICATION.md` and `docs/trainability-study.md` for full detail. Owner interpretation of the cross-reference verdict is an intentional `[pending]` placeholder per this project's self-explanation-checkpoint convention.

**Success criteria:**
1. Gradient-variance sweep computed via exact parameter-shift across ≥3 system sizes, ≥100 independent random parameter draws each, with an explicit poly-vs-exponential model comparison (curve fit + goodness-of-fit, not eyeballed).
2. Parameter-initialization distribution and per-circuit energy/photon-number normalization stated explicitly and controlled/reported across the sweep.
3. Generator scope of the sweep (weight-1-only vs. mixed) stated explicitly with reasoning; mixed weight-1+weight-2 sweep run (reusing Phase 13's validated composability) if in scope.
4. Max reachable system size `n` honestly reported, stated explicitly relative to both `docs/iqp-baseline.md`'s n≥6 qubit-baseline threshold and the N=10→24 photonic-postselection literature fit-flip threshold (arXiv:2605.11879) — extended toward N≈20-24 if compute allows, honestly reported if not reached.
5. Result cross-referenced against `docs/iqp-baseline.md`'s qubit-side empirical plateau rule (97.9% accuracy, 283 rows) — does it transfer to the photonic realization?

---

### Phase 17.1: Trainability Follow-Up — Bandwidth & Init Sensitivity

**Added 2026-08-12** via `/gsd:insert-phase`-style decimal insertion, not a Phase-17 reopen — Phase 17 stays shipped and verified as-is; this is new, owner-authorized follow-up work discovered by a fresh direct read of 8 literature papers (see `docs/iqp-baseline.md`'s "Fresh Primary-Source Verification" section), sequenced immediately after Phase 17 rather than renumbering Phases 18-21.

**Goal:** Resolve two concrete, literature-motivated open questions about Phase 17's already-shipped trainability result, using the exact sweep infrastructure Phase 17 already built (`trainability/sweep.py`, `gradient_variance_sweep.py`, `curve_fit.py`) rather than new machinery: (1) is the measured exponential gradient-decay signature partly or wholly a fixed-bandwidth artifact rather than a circuit/init property? (2) does a literature-sourced, data-dependent initialization (Recio-Armengol et al., arXiv:2503.02934) resolve Phase 17's inconclusive `small_angle` result where a fixed-magnitude heuristic didn't? Both measured and reported honestly either direction — this phase can conclude "the original finding holds" just as validly as "it doesn't."

**TRAIN-09 correction (2026-08-12, same day as this phase's addition):** the original literature trigger for TRAIN-09 was Rudolph et al.'s (arXiv:2305.02881) proof that a fixed, n-independent MMD bandwidth causes exponential loss-variance concentration via a Pauli-Z "bodyness" decomposition, with their fix being a bandwidth scaled as `σ∈Θ(n)`. Verified via direct code read (`trainability/target_grid.py`, `trainability/mmd_exact.py`) that this doesn't mechanically transfer: their kernel is bitstring-Hamming-distance where each bit-vector coordinate is one qubit; this project's kernel is Euclidean distance over a **fixed-2D** bin-center grid (`centers` shape `(2^n, 2)` for every n) with an arbitrary, non-spatial bitstring→index mapping — there is no Pauli-Z decomposition of that kernel to control the bandwidth of. The real, *verified* (not assumed) analog: because `2^n` bins pack into the same fixed `[lo,hi]^2` region, bin spacing shrinks from 1.20 (n=2) to 0.17 (n=5-6) as n grows, so the literally-fixed `SIGMA=0.1` becomes progressively less discriminating relative to the grid (kernel value between adjacent bins: ≈0 at n=2 → ≈0.23 at n=5-6, computed directly). TRAIN-09 is redefined around this verified mechanism instead.

**Depends on:** Phase 17 (reuses its sweep infrastructure and CORE dataset as the baseline to compare against). Independent of Phase 18/19 — does not block or wait on either.
**Requirements:** TRAIN-09, TRAIN-10

**TRAIN-09 design finalized (2026-08-12, post-research, owner-reviewed — supersedes success criterion 1's original "scale sigma per n" wording below):** rather than deriving a single per-n-varying sigma schedule (which requires picking one arbitrary anchor point, a real weakness), the owner chose a fixed sigma **grid** — `{0.03, 0.1, 0.3, 1.0, 3.0, 9.0}`, directly modeled on the sibling project's own `AC12` bandwidth sweep — with Phase 17's full CORE sweep re-run once per grid value (6 independent runs, sigma held constant across the whole n-range within each run), rather than one sigma-schedule sweep. `sigma=0.1` reproduces Phase 17's original CORE CSVs bit-for-bit, used as a built-in consistency check. See `17.1-RESEARCH.md`'s "Owner Decisions" section for full detail.

**Plans:** 6 plans (5 waves — 17.1-01/17.1-02 parallel in wave 1 (independent files); 17.1-03 depends on both (wave 2); 17.1-04 depends on 17.1-03 (wave 3, TRAIN-09's 6-sigma-grid execution); 17.1-05 depends on 17.1-04 (wave 4, TRAIN-10 execution + comparison analysis, sequenced after TRAIN-09 to avoid concurrent heavy compute per this project's documented memory constraint); 17.1-06 depends on 17.1-05 (wave 5, docs write-up))

Plans:
- [x] 17.1-01-PLAN.md — TDD: data-dependent init math primitives (`trainability/data_dependent_init.py`), bit-ordering-verified (Pitfall 3)
- [x] 17.1-02-PLAN.md — Thread `sigma` through the sweep pipeline (backward-compatible), CLI `--sigma`/CSV columns, chunk/combine sigma-consistency fix (Pitfall 2)
- [x] 17.1-03-PLAN.md — Wire `data_dependent` init scheme into the sweep pipeline and CLI (`--scale-factor`)
- [x] 17.1-04-PLAN.md — Run TRAIN-09's 6-sigma-grid CORE sweep (weight1 + mixed), sigma=0.1 consistency check
- [x] 17.1-05-PLAN.md — Run TRAIN-10's sweep; new `trainability_analysis_1701.py` comparison analysis (does not modify Phase 17's `trainability_analysis.py`)
- [x] 17.1-06-PLAN.md — Fold both follow-ups into `docs/trainability-study.md` as new subsections

**Result: Complete — verified 5/5 must-haves.** TRAIN-09's real 6-sigma-grid CORE sweep (`{0.03, 0.1, 0.3, 1.0, 3.0, 9.0}`) shows the original Phase 17 exponential-decay ("exp") verdict for `weight1/uniform` and `mixed/uniform` is **not robust** to bandwidth changes — survives only near sigma in {0.03, 0.1} (Phase 17's original value), flips to "inconclusive" at {0.3, 1.0}, and `weight1/uniform` non-monotonically re-emerges as "exp" at {3.0, 9.0} while `mixed/uniform` stays inconclusive through sigma=9.0. TRAIN-10's data-dependent init (Recio-Armengol et al.) did **not** resolve `small_angle`'s original "inconclusive" verdict in either generator scope — a genuine negative result. Both findings folded into `docs/trainability-study.md` as new subsections, strictly additive (175 insertions, 0 deletions), Phase 17's original numbers untouched. 234/234 full repo suite passes throughout. See `17.1-VERIFICATION.md` for the independently-reproduced evidence. A staff-engineer-style review pass found no production bugs — informational findings only (minor code duplication/reuse opportunities, and a documentation-convention note that the new doc sections state interpretive conclusions more assertively than this project's usual `> Owner interpretation: [pending]` pattern — flagged for the owner, not auto-fixed).

**Success criteria:**
1. TRAIN-09: gradient-variance sweep re-run at Phase 17's CORE n-range (weight1 n=2-6, mixed n=2-5), both init schemes, at each of a fixed sigma grid `{0.03, 0.1, 0.3, 1.0, 3.0, 9.0}` (owner-finalized design, see above — supersedes this criterion's original "scale sigma per n" phrasing) — the sigma and bin-spacing values stated explicitly in the sweep's own output/report for every row, not just implied by a formula.
2. TRAIN-09: same poly-vs-exponential curve-fit analysis (reusing `trainability.curve_fit.fit_and_compare` unchanged) applied to the new sweep at every sigma grid value; explicit statement of whether the exponential-decay verdict for `weight1/uniform` and `mixed/uniform` survives across the sigma grid, weakens, or disappears.
3. TRAIN-10: Recio-Armengol et al.'s data-dependent init recipe implemented (weight-1 angles from empirical single-bit target-distribution means; weight-2 angles proportional to empirical pairwise covariances, scaled by a stated hyperparameter — `scale_factor=1.0`, owner-decided) as a new init scheme alongside the existing `small_angle`/`uniform` options.
4. TRAIN-10: gradient-variance sweep re-run under this new init scheme at the same n-range (`n_draws=1`, owner-decided — the init is fully deterministic, so more draws are redundant); explicit statement of whether it produces a clearer (non-inconclusive) trainability verdict than `small_angle` did, and if so which direction.
5. Both results folded into `docs/trainability-study.md` as new subsections (not silently replacing Phase 17's original reported numbers) — the original CORE dataset and verdict stay on record either way, with these results presented as a follow-up check, honoring this project's honesty-over-narrative convention.

---

### Phase 18: Hardness-Under-Loss Assessment

**Goal:** Measure whether the sampling-hardness argument survives realistic photon loss, via `Processor.probs()` + a loss mechanism (not `Analyzer`, which silently ignores loss), grounded in a named asymptotic threshold from the literature, reported honestly either direction. **HARD-03 (full read of arXiv:2510.24137) is the first, near-zero-code step within this phase, not the last** — it gates this phase's central claim (where this project's tested loss levels sit relative to the known threshold) and must not be left implicit.

**Mechanism correction (2026-08-14, discovered during Phase 18 planning research):** `Processor(..., noise=NoiseModel(transmittance=η))` was confirmed (source trace + live execution) to silently no-op for this project's polarization-annotated weight-1/weight-2 circuits — a third instance of the "silent loss-ignoring" failure mode this phase's own HARD-01 already warns about for `Analyzer`. The actual mechanism, verified working end-to-end: `pcvl.LC(loss)` component insertion uniformly across all modes inside a `Processor`, plus an explicit `proc.min_detected_photons_filter(0)` call (otherwise the automatic filter silently discards every lossy branch). `NoiseModel` still has a role — as the HARD-02 cross-check reference on a simplified non-polarization circuit, the reverse of HARD-01/HARD-02's original wording. `REQUIREMENTS.md`'s HARD-01/HARD-02 and this phase's success criteria 2/3 below are corrected accordingly; the plans (18-02/18-03) implement the corrected mechanism. See `.planning/phases/18-hardness-under-loss-assessment/18-RESEARCH.md` Pitfalls 1-2 for full detail.

**Literature grounding added 2026-08-12** (fresh primary-source read of 8 papers, per owner's explicit instruction — see `docs/iqp-baseline.md`'s "Fresh Primary-Source Verification" section): Bremner-Montanaro-Shepherd's noise+anticoncentration theorem (arXiv:1610.01808, *Quantum* 1, 8 (2017), Theorem 4) is a second named asymptotic threshold alongside arXiv:2510.24137/Aaronson-Brod, folded into success criterion 4 below — but its noise model (single-qubit depolarizing) is a physically different channel than photon transmission loss (a Fock-space erasure/leakage channel, typically surfacing as herald failure rather than a random bit-flip), so the positioning must state an explicit translation model, not assume equivalence. Its anticoncentration parameter `α` (`Σp_x² ≤ α·2⁻ⁿ`) is the quantity that paper's own hardness-vs-simulability threshold is keyed on, and should be tracked alongside `η` (folded into success criterion 5).

**Depends on:** None beyond already-shipped weight-1/weight-2 modules. Independent of ARB, TRAIN, and VERIFY — this phase does not wait on ARB-01's outcome.
**Requirements:** HARD-01, HARD-02, HARD-03, HARD-04, HARD-05, HARD-06, HARD-07

**Plans:** 8 plans (5 waves — 18-01/18-02/18-03/18-04 parallel in wave 1, all independent files (literature grounding; weight-1 loss model + HARD-02 cross-check; weight-2 loss model + herald compounding; classically-easy baselines + anticoncentration); 18-05 depends on 18-02/18-03/18-04 (wave 2, sweep integration + CLI + timing probe); 18-06 depends on 18-05 (wave 3, the real compute-heavy sweep run); 18-07 depends on 18-06+18-01 (wave 4, results write-up); 18-08 depends on 18-07 (wave 5, HARD-04 attempt-first checkpoint + HARD-06 scope statement, mirroring Phase 15's ARB-02/Plan-15-03 checkpoint precedent))

Plans:
- [x] 18-01-PLAN.md — Read arXiv:1510.05245 (genuine Aaronson-Brod) in full; cite it and Park & Oh's Theorem 1 (arXiv:2510.24137) into docs/iqp-baseline.md (HARD-03)
- [x] 18-02-PLAN.md — TDD: weight-1 LC-based loss distribution function (hardness/loss_model.py) + HARD-02 NoiseModel-vs-LC cross-check
- [x] 18-03-PLAN.md — TDD: weight-2 (heralded_cz) LC-based loss distribution with ancilla-inclusive herald-failure compounding (hardness/loss_model_weight2.py), HARD-07
- [x] 18-04-PLAN.md — TDD: classically-easy baselines (uniform, product-of-marginals) + BMS anticoncentration parameter alpha (hardness/baselines.py), HARD-05
- [x] 18-05-PLAN.md — Sweep integration (hardness/sweep.py), chunked/resumable CLI (loss_sweep.py), and a real timing probe before committing compute budget
- [x] 18-06-PLAN.md — Run the real weight-1 and mixed loss sweeps across the full eta grid (HARD-01, HARD-05, HARD-07 real data)
- [x] 18-07-PLAN.md — Results write-up: docs/hardness-under-loss-study.md methodology + TVD-vs-eta + anticoncentration + herald-compounding results
- [x] 18-08-PLAN.md — HARD-04 attempt-first checkpoint (owner sketches eta-to-depolarizing-rate translation) + dual literature positioning + HARD-06 scope statement

**Result: Complete — verified 5/5 must-haves.** Real weight-1 loss sweep (n=2..6, full 7-point eta grid, `results/phase18_weight1_loss_sweep.csv`) and mixed-scope sweep (n=2..4 CORE, `results/phase18_mixed_loss_sweep.csv`; n=5 confirmed a hard memory ceiling on this hardware, reproduced 3x, not a CORE requirement) both complete with real, finite TVD-vs-eta and anticoncentration-alpha data, plus herald-failure compounding shown to genuinely diverge from a naive analytical decomposition. Loss mechanism corrected mid-planning (`pcvl.LC(loss)` + explicit `min_detected_photons_filter(0)`, never `NoiseModel`, which was confirmed to silently no-op) and cross-checked against Perceval's own `NoiseModel` on a simplified circuit within stated tolerance. HARD-04's attempt-first checkpoint (owner-driven, per this project's CLAUDE.md convention): after a literature check confirmed no principled η-to-depolarizing-rate translation exists (photon loss's established formalism is the pure-loss/bosonic-amplitude-damping channel, structurally distinct from depolarizing noise), the owner chose to state this plainly rather than fabricate a number — positioned against loss-native thresholds instead (Aaronson-Brod's fixed-count regime; a newly-verified 2025 lossy-Gaussian-boson-sampling logarithmic-fraction result, read in full and explicitly flagged as a different photonic encoding than this project's), with BMS's depolarizing threshold kept qualitative-only. A staff-engineer-style code review (6 angles) found zero correctness bugs; two real, pre-existing gaps it surfaced (an unverified "Van den Nest" citation; two documented pitfalls in the weight-2 loss model with no regression tests) were fixed before closing the phase — the citation independently confirmed correct via a paper already in this project's corpus, and both missing regression tests added and live-verified against the actual documented crash/conflation behavior. 268/268 full suite passes. See `18-VERIFICATION.md` for the independently-reproduced evidence.

**Success criteria:**
1. arXiv:2510.24137 read in full (not abstract-only); its noisy-IQP-specific threshold formula (if stated) extracted and cited — done *before* the loss-sweep methodology below is finalized.
2. Loss sweep run via `Processor.probs()` + `pcvl.LC(loss)` component insertion (uniform across all modes, with an explicit `min_detected_photons_filter(0)`) over a defined η grid — corrected 2026-08-14 from this criterion's original `NoiseModel(transmittance=η)` wording, which was confirmed to silently no-op for this project's polarization-annotated circuits.
3. Cross-checked against Perceval's independently-implemented `NoiseModel(transmittance=η)` source-level loss model at ≥1 shared η on a simplified non-polarization circuit, agreement confirmed within a stated tolerance — roles reversed from this criterion's original wording (see mechanism correction above).
4. This project's fractional-loss model explicitly positioned against the genuine Aaronson-Brod paper's (arXiv:1510.05245, read per Phase 18 Plan 18-01) fixed-loss-count regime AND Bremner-Montanaro-Shepherd's depolarizing-noise-threshold regime (arXiv:1610.01808) — states plainly which regime(s) this project's tested loss levels actually sit in, and states explicitly how (or whether) photon loss translates to an effective depolarizing rate for that second comparison to be meaningful, rather than assuming the two noise channels are equivalent. Corrected 2026-08-14: arXiv:2510.24137 is Park & Oh, not Aaronson-Brod (see criterion 1) — its Theorem 1, not the genuine Aaronson-Brod paper, is the source for the passive-linear-optics comparison; the genuine Aaronson-Brod paper is a separate, additional read.
5. TVD-vs-η tracked against both the lossless reference and an explicitly-defined classically-easy baseline distribution, alongside the output distribution's anticoncentration parameter `α` as a function of `η` (per arXiv:1610.01808's Theorem 4); weight-2 loss sweep (photon loss compounded with `heralded_cz`'s herald-failure probability) included; explicit "what this does/doesn't establish" scope statement written.

---

### Phase 19: Independent Julia Cross-Checks

**Goal:** Independently cross-check the Python/Perceval pipeline's exact and lossy distributions using the Julia toolchain confirmed working in Phase 14 — the full cross-check scripts, sequenced after real Python-side numbers exist to diff against.
**Depends on:** Phase 14 (Julia toolchain must be confirmed working first); Phase 18 (VERIFY-04 specifically needs HARD's TVD-vs-η dataset to cross-check against). VERIFY-02/03 reuse the already-shipped weight-1/weight-2 exact distributions (Phases 9, 11-13) and are bundled into this same phase rather than run separately, to keep the Julia toolchain's engagement narrow and time-boxed (per `PITFALLS.md` Pitfall 23) instead of returning to it multiple times.
**Requirements:** VERIFY-02, VERIFY-03, VERIFY-04
**Plans:** 6 plans (4 waves — 19-01 alone in wave 1, generates every Python reference distribution the Julia scripts diff against; 19-02/19-03/19-04 parallel in wave 2, all depend only on 19-01 (Yao.jl qubit-side; BosonSampling.jl weight-1; BosonSampling.jl weight-2/Knill-CZ, isolated as the phase's highest stall risk per 19-CONTEXT.md); 19-05 depends on 19-01 + 19-04 (wave 3, BosonSampling.jl native loss-model cross-check — sequenced after 19-04 so it deterministically reads 19-04's finished weight-2 outcome before deciding whether the mixed-scope loss leg is attemptable); 19-06 depends on 19-02/19-03/19-04/19-05 (wave 4, results write-up + REQUIREMENTS.md correction, sequenced after 19-05 completes))

Plans:
- [x] 19-01-PLAN.md — Python reference-distribution generator (exact qubit/weight-1/weight-2 cases + fixed-single-draw loss cases at 3 eta values)
- [x] 19-02-PLAN.md — VERIFY-02: Yao.jl independent qubit-side IQP cross-check (n=2, n=3)
- [x] 19-03-PLAN.md — VERIFY-03 (weight-1 leg): BosonSampling.jl independent dual-rail weight-1 cross-check (n=2, n=3)
- [x] 19-04-PLAN.md — VERIFY-03 (weight-2 leg): Knill-CZ literature sourcing + BosonSampling.jl cross-check (isolated, time-boxed stall risk)
- [x] 19-05-PLAN.md — VERIFY-04: BosonSampling.jl native-loss-API cross-check against Phase 18's TVD-vs-η numbers (n=2, 3 eta values)
- [x] 19-06-PLAN.md — docs/julia-cross-check-study.md write-up + REQUIREMENTS.md status correction

**Result: Complete — verified 5/5 must-haves.** All four independent cross-checks reached a genuine GO: VERIFY-02 (Yao.jl qubit-side, TVD 2.26e-17/1.12e-16 at n=2/3), VERIFY-03 weight-1 (BosonSampling.jl, TVD 2.36e-16/3.04e-16 at n=2/3), VERIFY-03 weight-2 (Knill-CZ, TVD 3.50e-15 — a real matrix-transpose convention bug found via Knill's own Eq. 6 zero-leak constraint, fixed, and independently confirmed via Codex/gpt-5.5 review to be a legitimate correction, not a coincidental double-bug), and VERIFY-04 (BosonSampling.jl native loss API, TVD ≤1.75e-14 across 3 η values for both weight-1 and mixed scope — two real findings: η-as-transmission-amplitude-not-probability, and a package dispatch gap, both fixed and documented). `docs/julia-cross-check-study.md` written as the canonical results document; `REQUIREMENTS.md`'s VERIFY-02/03/04 rows corrected to Complete. gsd-verifier independently re-ran all four Julia scripts live rather than trusting SUMMARY claims. A follow-up Codex review (requested by the owner) confirmed the transpose fix's reasoning holds up, but flagged a real, separate methodological gap worth the owner's attention: the weight-2 locked-gate test case (thetas=[0,0]) produces a distribution symmetric under bit-relabeling (00/11 at 50% each, 01/10 both exactly 0), which cannot fully rule out a hidden Julia/Python bitstring-convention mismatch — the passing TVD is real evidence of correctness but not a complete proof against this specific failure mode. Not fixed in this phase; flagged as an open item.

**Success criteria:**
1. Yao.jl reproduces the exact qubit-side IQP reference distribution (weight-1, at least n=2) within a stated tolerance of the existing Python/NumPy implementation.
2. BosonSampling.jl reproduces the photonic-level exact distribution (weight-1 and/or weight-2) within a stated tolerance of Perceval's results, for at least one shared test case.
3. BosonSampling.jl cross-checks Phase 18's loss-model numbers at ≥1 shared η; agreement (or a documented, honestly-reported disagreement) stated against the Python-computed TVD-vs-η result.

---

### Phase 20: Technical Write-Up

**Goal:** Write up STUDY-01 (Phase 17), STUDY-02 (Phase 18), and ARB-01's (Phases 15-16) findings as the project's technical findings document — methodology-stated-before-results, honest negative/inconclusive framing wherever the data warrants it, matching this project's existing GEN-07/LIT-04/Phase-7 rigor bar. Per research (`FEATURES.md`): this phase's *structure* (methodology-first, literature-comparison tables, explicit scope statements) is reasonable to draft early, in parallel with Phases 15-18, as a template to fill in — but the phase cannot be substantively completed until those phases have at least first-pass results.

**Literature grounding added 2026-08-12** (fresh primary-source read of 8 papers — see `docs/iqp-baseline.md`'s "Fresh Primary-Source Verification" section): six additional named baselines are now available beyond the four already on record, folded into success criterion 2. Separately, Herbst et al. (arXiv:2512.24801) gives an explicit theoretical link between the TRAIN and HARD sections — anticoncentration is predicted to drive *both* IQP's sampling hardness and its MMD-loss concentration, so the two sections' findings should be explicitly checked against (not silently left as two unrelated results) — folded into a new success criterion 6.

**Depends on:** Phase 16 (ARB-01's full outcome), Phase 17 (TRAIN's dataset), Phase 17.1 (bandwidth/init follow-up results — added 2026-08-12), Phase 18 (HARD's dataset). Does not require Phase 19 (Julia cross-check results are supplementary evidence, not a stated WRITE-01..06 requirement — include if ready, do not block on it).
**Requirements:** WRITE-01, WRITE-02, WRITE-03, WRITE-04, WRITE-05, WRITE-06

**Success criteria:**
1. Methodology-stated-before-results structure exists for each of the trainability, hardness-under-loss, and ARB-01 sections.
2. Explicit comparison table against each named literature baseline — McClean et al., Aaronson-Brod, arXiv:2510.24137, arXiv:2405.01395, `docs/iqp-baseline.md`'s own empirical rule, plus the six papers added by the 2026-08-12 fresh literature read: Bremner-Montanaro-Shepherd 2015 (arXiv:1504.07999, hardness threshold) and 2017 (arXiv:1610.01808, noise+hardness), Rudolph et al. (arXiv:2305.02881, MMD bodyness/bandwidth trainability), Mhiri et al. (arXiv:2502.07889, warm-start/small-angle guarantees), Recio-Armengol et al. (arXiv:2503.02934, n=1000 IQP-generative-ML), and Herbst et al. (arXiv:2512.24801, anticoncentration-trainability tradeoff) — stated per baseline as consistent with / inconsistent with / silent relative to.
3. Honest negative/inconclusive framing applied wherever the data warrants it, in the same direct language already used for GEN-07/LIT-04/Phase 7's neighbor-locality verdict.
4. Explicit "what this does/doesn't establish" scope paragraph present for each of the three sections.
5. Self-explanation checkpoint transcripts recorded (owner's own interpretation transcribed first); every reported number traceable to a specific script/test/notebook cell, with a fixed seed where randomness is involved.
6. The TRAIN and HARD sections explicitly engage with Herbst et al.'s anticoncentration-tradeoff prediction — stated plainly whether this project's own measured TRAIN result (Phase 17) and HARD result (Phase 18) came out consistent or inconsistent with that framework, as the connecting thread between the two otherwise-separate sections rather than two unrelated findings.

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
- Wave 2: Phase 16 (depends on 15), Phase 17.1 (depends on 17 — added 2026-08-12), Phase 19 (depends on 14 + 18)
- Wave 3: Phase 20 (depends on 16, 17, 17.1, 18)
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
| 16. ARB-01 Extended Validation & Postselection Bookkeeping | v3.0 | 3/3 | Complete — verified 3/3, no bugs found | 2026-08-09 |
| 17. Trainability / Barren-Plateau Study | v3.0 | 7/7 | Complete — verified 8/8, honest exp-decay signature found (uniform init) | 2026-08-11 |
| 17.1. Trainability Follow-Up: Bandwidth & Init Sensitivity | v3.0 | 6/6 | Complete — verified 5/5, exp signature not robust to bandwidth; data-dependent init did not resolve inconclusive verdict | 2026-08-13 |
| 18. Hardness-Under-Loss Assessment | v3.0 | 8/8 | Complete — verified 5/5, no correctness bugs, HARD-04 resolved honestly (no forced translation) | 2026-08-17 |
| 19. Independent Julia Cross-Checks | v3.0 | 6/6 | Complete — verified 5/5, all 4 legs GO (1 real transpose bug found+fixed) | 2026-08-17 |
| 20. Technical Write-Up | v3.0 | 0/? | Not started | — |
| 21. External-Facing Framing Pass | v3.0 | 0/? | Not started | — |

v2.0 milestone (Phases 8-9) shipped 2026-08-05. v2.1 milestone (Phases 10-13, Weight-2 Implementation) shipped 2026-08-06. v3.0 milestone (Phases 14-21, IQP Circuit Study & Write-Up) roadmap created 2026-08-07 — 35 v1 requirements mapped across 8 phases (see `REQUIREMENTS.md` note on the corrected 34→35 count), 100% coverage validated, no orphans. Phase 16 (ARB-01 Extended Validation & Postselection Bookkeeping) completed 2026-08-09 — verified 3/3 must-haves, ARB-07/08/09 all satisfied, no bugs found. Phase 17 (Trainability/Barren-Plateau Study) completed 2026-08-11 — verified 8/8, honest exponential-decay signature found under uniform init. **Phase 17.1 added 2026-08-12**, inserted after a fresh, owner-instructed direct read of 8 literature papers (not the sibling project's secondhand vault notes) surfaced two concrete, testable follow-up questions about Phase 17's already-shipped result — a possible fixed-bandwidth confound (TRAIN-09, verified via direct code read to be a real geometric effect, not Rudolph et al.'s literal σ∈Θ(n) mechanism which doesn't apply to this project's kernel) and a literature-sourced alternative to the inconclusive `small_angle` init scheme (TRAIN-10, Recio-Armengol et al.). Both owner-authorized as new milestone scope (37 v1 requirements total now, up from 35); Phase 17 itself was not reopened or reversed. **Phase 17.1 completed 2026-08-13** — verified 5/5 must-haves. All 6 plans shipped across 5 waves (17.1-01/02 wave 1; 17.1-03 wave 2; 17.1-04 wave 3, TRAIN-09's 6-sigma-grid execution; 17.1-05 wave 4, TRAIN-10 execution + comparison analysis; 17.1-06 wave 5, docs write-up). TRAIN-09: the original Phase 17 exponential-decay signature is not robust across the sigma grid `{0.03, 0.1, 0.3, 1.0, 3.0, 9.0}` — survives only near Phase 17's original bandwidth, disappears mid-grid, and (for weight1 only) non-monotonically re-emerges at higher sigma. TRAIN-10: Recio-Armengol et al.'s data-dependent init did not resolve the inconclusive `small_angle` verdict in either scope — a genuine negative result. Both findings folded into `docs/trainability-study.md`, strictly additive. Full phase and requirement detail for shipped milestones archived to `.planning/milestones/v2.0-ROADMAP.md`/`v2.0-REQUIREMENTS.md` and `.planning/milestones/v2.1-ROADMAP.md`/`v2.1-REQUIREMENTS.md`/`v2.1-MILESTONE-AUDIT.md`.
