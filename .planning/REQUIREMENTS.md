# Requirements: MerLin Photonic Generative Modeling — v3.0 IQP Circuit Study & Write-Up

**Defined:** 2026-08-07
**Core Value:** A working, end-to-end, honestly-benchmarked MMD-trained photonic generative model, published in a public repo before Sept 1, 2026 — explainable unaided to Vincent Espitalier.

## v1 Requirements

All requirements below are Must-have for this milestone — owner's explicit, twice-confirmed call, no fallback/deferral ordering. Pitfalls research flagged this as real timeline risk (this is the first milestone since the PennyLane stall to combine a new toolchain with a hard deadline); the roadmap builds in an early Julia-toolchain checkpoint (mirroring v1.0's Jul-25 pattern) so a stall is visible early rather than silently absorbed.

### Trainability / Barren-Plateau Study (TRAIN)

- [x] **TRAIN-01**: Gradient-variance sweep computed via exact parameter-shift on the existing distribution functions (`photonic_iqp_distribution`/`photonic_weight2_iqp_distribution`) — NOT via MerLin `QuantumLayer` autograd, which architecture research confirmed cannot accept this circuit's polarization-annotated `BasicState`s — across ≥3 system sizes, ≥100 independent random parameter draws each
- [x] **TRAIN-02**: Explicit poly-vs-exponential model comparison (curve fit + goodness-of-fit, e.g. R²/AIC) — not an eyeballed plot
- [x] **TRAIN-03**: Parameter-initialization distribution and per-circuit energy/photon-number normalization stated explicitly and controlled/reported across the sweep
- [x] **TRAIN-04**: Generator scope of the sweep (weight-1-only vs. mixed) stated explicitly, with reasoning
- [x] **TRAIN-05**: Honest statement of the max reachable system size `n`, and whether that range sits inside or outside the historically-misleading small-N regime this project's own pitfalls research documented (arXiv:2605.11879's N=2-10-vs-N=24 fit flip)
- [x] **TRAIN-06**: Mixed weight-1+weight-2 generator sweep, reusing Phase 13's validated composability
- [x] **TRAIN-07**: Cross-reference against `docs/iqp-baseline.md`'s qubit-side empirical plateau rule (97.9% accuracy, 283 rows) — does it transfer to the photonic realization?
- [x] **TRAIN-08**: Sweep extended toward N≈20-24 if compute allows — the range where the cited precedent's poly-vs-exp fit is known to flip; honestly report if this range isn't reached
- [x] **TRAIN-09** *(added 2026-08-12, owner-authorized follow-up to the fresh literature read; corrected same day after verifying Rudolph et al.'s specific bandwidth-scaling formula doesn't transfer to this project's kernel — see below)*: Re-run the gradient-variance sweep with `SIGMA` scaled to hold `sigma/bin-spacing` constant across n, at the same n-range as Phase 17's CORE sweep, to test whether Phase 17's fixed `SIGMA=0.1` (`trainability/sweep.py:29`) is itself sufficient to produce the observed exponential-decay signature via a verified, purely-geometric mechanism — target-grid bin spacing shrinks from 1.20 (n=2) to 0.17 (n=5-6) as `2^n` bins pack into the same fixed `[lo,hi]^2` region (`trainability/target_grid.py`), so a literally-fixed `sigma` becomes progressively less discriminating (kernel value between adjacent bins rises from ≈0 at n=2 to ≈0.23 at n=5-6) independent of circuit structure or init scheme. (Rudolph et al.'s arXiv:2305.02881 `σ∈Θ(n)` prescription was the original literature trigger for this question, but doesn't mechanically apply — their bodyness/Pauli-Z decomposition requires a bitstring-Hamming-distance kernel where each coordinate is one qubit; this project's kernel is a fixed-2D-Euclidean-distance kernel over an arbitrarily-indexed bin grid, verified via direct code read, not the same structure.)
- [x] **TRAIN-10** *(added 2026-08-12, owner-authorized follow-up to the fresh literature read)*: Re-run the gradient-variance sweep at the same n-range under Recio-Armengol et al.'s (arXiv:2503.02934) data-dependent initialization (weight-1 angles from empirical single-bit training-data means, weight-2 angles proportional to empirical pairwise covariances) as a real alternative to the fixed-magnitude `small_angle` scheme, and report whether it changes the small_angle/uniform trainability picture

### Hardness-Under-Loss Assessment (HARD)

- [x] **HARD-01**: Loss sweep via `Processor.probs()` over a defined η grid — NOT `Analyzer`, which was confirmed to silently ignore loss entirely. **Corrected 2026-08-14 (Phase 18 planning research):** the actual loss mechanism is `pcvl.LC(loss)` component insertion, applied uniformly across all modes inside the `Processor`, followed by an explicit `proc.min_detected_photons_filter(0)` call — `Processor(..., noise=NoiseModel(transmittance=η))` was confirmed (source trace + live execution) to silently no-op for this project's polarization-annotated circuits, so it cannot be the sweep's primary mechanism as originally written here.
- [x] **HARD-02**: Cross-check against Perceval's independently-implemented `NoiseModel(transmittance=η)` source-level loss model, at ≥1 shared η, on a simplified non-polarization circuit. **Corrected 2026-08-14:** roles reversed from this requirement's original wording — `LC` is now HARD-01's primary mechanism (see above), so `NoiseModel` serves as the independent cross-check reference instead (it works correctly for non-polarization inputs; confirmed to agree with `LC` on a shared toy case).
- [x] **HARD-03**: Full read (not abstract-only) of arXiv:2510.24137, with its noisy-IQP-specific threshold formula (if stated) extracted and cited — this is the load-bearing, currently-open gap blocking STUDY-02's central claim
- [x] **HARD-04**: Explicit positioning of this project's fractional-loss model against Aaronson-Brod's fixed-loss-count regime **and** Bremner-Montanaro-Shepherd's depolarizing-noise-threshold regime (arXiv:1610.01808, added 2026-08-12 via fresh literature read) — state which regime(s) this project's tested loss levels actually sit in, and state explicitly how (or whether) photon loss translates to an effective depolarizing rate for the second comparison to be meaningful (the two are physically different noise channels — Fock-space erasure vs. qubit depolarizing — not equivalent by assumption). **Corrected 2026-08-14:** arXiv:2510.24137 is Park & Oh, not Aaronson-Brod — cite Park & Oh's Theorem 1 for the passive-linear-optics/photon-transmittance comparison, and the genuine Aaronson-Brod paper (arXiv:1510.05245, read separately per Phase 18 planning) for the fixed-loss-count regime; both cited explicitly, not conflated.
- [x] **HARD-05**: TVD-vs-η metric tracked against both (a) the lossless reference and (b) an explicitly-defined classically-easy baseline distribution
- [x] **HARD-06**: Explicit "what this does/doesn't establish" scope statement, matching `docs/iqp-photonic-encoding.md`'s ENC-02 precedent
- [x] **HARD-07**: Weight-2 loss sweep — physical photon loss compounded with `heralded_cz`'s herald-failure probability

### Arbitrary-θ Weight-2 Gate Validation (ARB)

- [x] **ARB-01**: Gate phase/structure confirmed at ≥3 non-trivial α values via `Simulator.prob_amplitude`, extending the single spot-check already done in research
- [x] **ARB-02**: General-α operator identity written down connecting `CP(α)` to `exp(iθZ_iZ_j)`, extending `docs/iqp-photonic-encoding.md`'s existing fixed-π/4 derivation
- [x] **ARB-03**: TVD validation against the extended exact qubit-side reference at ≥1 representative non-special α (ideally 2-3 values spanning the tested range)
- [x] **ARB-04**: Success probability reported as an explicit function of α (table or curve), never collapsed to a single number
- [x] **ARB-05**: Explicit written comparison to the existing fixed-π/4 `heralded_cz` construction — different gate family (post-selection + ancilla vacuum vs. ancilla heralding), stated plainly, not conflated
- [x] **ARB-06**: Test coverage added to `tests/test_iqp_photonic_encoding.py` matching existing tolerance/parametrization conventions
- [x] **ARB-07**: n=3 mixed weight-1 + arbitrary-θ weight-2 composability test, direct parallel to Phase 13's existing test
- [x] **ARB-08**: Denser α sweep (8-16 points across [0, 2π)) with success probability plotted as a continuous curve
- [x] **ARB-09**: Forge model verifying the gate's `set_postselection` local→global ancilla mode-index translation is a valid, non-aliasing mapping — a narrow, bounded discrete-correctness check, not a numeric verifier

### Independent Julia Verifier (VERIFY)

- [x] **VERIFY-01**: Julia toolchain installed (`juliaup`, Yao.jl, BosonSampling.jl) with a hello-world circuit run successfully — the de-risking spike; sequenced early in the roadmap as this milestone's stall-risk checkpoint
- [x] **VERIFY-02**: Yao.jl independent cross-check of the exact qubit-side IQP reference distribution (weight-1, at least n=2) against the existing Python/NumPy implementation
- [x] **VERIFY-03**: BosonSampling.jl independent cross-check of the photonic-level exact distribution (weight-1 and/or weight-2) against Perceval's results, at least one shared test case
- [x] **VERIFY-04**: BosonSampling.jl cross-check of STUDY-02's loss-model numbers at ≥1 shared η against the Python-computed TVD-vs-η result

### Technical Write-Up (WRITE)

- [x] **WRITE-01**: Methodology-stated-before-results structure for each of the trainability, hardness-under-loss, and ARB-01 sections
- [x] **WRITE-02**: Explicit comparison table against each named literature baseline (McClean et al., Aaronson-Brod, arXiv:2510.24137, arXiv:2405.01395, `docs/iqp-baseline.md`'s own empirical rule, **plus 6 papers added 2026-08-12 via fresh literature read: arXiv:1504.07999, arXiv:1610.01808, arXiv:2305.02881, arXiv:2502.07889, arXiv:2503.02934, arXiv:2512.24801** — listed individually in `ROADMAP.md`'s Phase 20 success criterion 2) — consistent with / inconsistent with / silent relative to, stated per baseline
- [x] **WRITE-03**: Honest negative/inconclusive framing wherever the data warrants it, in the same direct language this project already used for GEN-07/LIT-04/Phase 7's neighbor-locality verdict
- [x] **WRITE-04**: Explicit "what this does/doesn't establish" scope paragraph for each of the trainability, hardness-under-loss, and ARB-01 sections
- [x] **WRITE-05**: Self-explanation checkpoint transcripts recorded in the write-up itself (owner's own interpretation transcribed first, per CLAUDE.md's standing rule)
- [x] **WRITE-06**: Every reported number traceable to a specific script/test/notebook cell, with a fixed seed where randomness is involved
- [x] **WRITE-07**: External-facing framing pass (README/case-study level), following this project's established "mechanism-not-magic, ownership-forward" convention — separate from the candid internal write-up

### Multi-Pair Ancilla Allocation — Formal Verification (MPAIR)

*Added 2026-08-20, owner-authorized as additive v3.0 scope (Phase 22). Not a new milestone — same insertion pattern as Phase 17.1. Scope is the symbolic verification only: no Python k-pair implementation, no multi-ZZ hardness re-run (both explicitly Out of Scope below).*

- [x] **MPAIR-01**: 2–3 candidate k-pair ancilla allocation schemes presented with tradeoffs stated and **no implied ranking**; the owner selects one, and both the selection and the reason the other candidates were rejected are recorded in the phase's own artifacts. Claude does not pick — per CLAUDE.md's "no silent unilateral design decisions" and attempt-first gating on conceptual components.
- [x] **MPAIR-02**: The non-collision invariant written down precisely in prose **before** any Forge code — stating what the property quantifies over (which `n`, which `k`, which subsets of pairs, which port ranges) and what a counterexample would look like *as a structure*, not as a number.
- [ ] **MPAIR-03** *(reframed 2026-08-20 after research — see `22-CONTEXT.md` D-05)*: Forge model of the selected scheme establishing the MPAIR-02 invariant over all `n` up to a stated bound. **The model poses a search question, not a verification one**: "does an assignment of ≤ K ancilla blocks to all C(n,2) pairs exist such that no two vertex-sharing pairs collide, and what is the minimum such K?" The original "holds for every subset of pairs at every `k`" wording is satisfied via the pairwise-reduction argument (collision is a binary predicate, so subset-quantification is exactly equivalent to pairwise checking under a fixed per-pair allocation) — that argument must be stated explicitly in MPAIR-02's prose, since it is what licenses not literally enumerating subsets — with the bound and Forge's `Int` bitwidth each justified against the largest value the model computes, so no silent overflow/wraparound is possible. Follows `forge/ancilla_mapping.frg`'s existing bitwidth-note discipline.
- [ ] **MPAIR-04**: Non-vacuity guard in the same two-part `test expect` form as `forge/ancilla_mapping.frg` — a `sat` check that the constraint set admits some valid instance, guarding against a vacuously-true, over-constrained model (the classic Forge pitfall).
- [ ] **MPAIR-05** *(criterion corrected 2026-08-21 — see note below)*: Honest verdict on what the Forge model contributed, measured not assumed — a brute-force baseline over the same bounded domain run and timed alongside the Forge model, with the conclusion stated either way. *(Refined 2026-08-20: under D-05's search framing the baseline must be a hand-rolled colouring **search** — greedy/backtracking — not a 406-case verification loop, which would be an unfair strawman comparison.)* Direct successor to ARB-09's own audit finding (2026-08-20) that Forge's advantage did *not* engage at the single-pair scale; this requirement exists so the claim is checked a second time rather than assumed. A "Forge did not earn its place here either" verdict satisfies this requirement.
  - **Criterion correction (2026-08-21).** ARB-09's audit, and this requirement as originally written, both graded Forge on *"does it beat brute force on an intractable domain."* A review of the owner's own CS1710 (Logic for Systems) coursework — the course this Forge toolchain comes from — establishes that this is **the wrong standard**: none of its models are brute-force-intractable either (hotel locking runs at 3 rooms / 3 guests / 8 time steps; goats-and-wolves is a river-crossing puzzle a BFS solves in milliseconds). What those models actually buy is (a) **finding the scenario you would not think to enumerate** — brute force requires already knowing what to enumerate over and what counts as bad, (b) **properties over traces and reachability**, where the "brute force" *is* a model checker, (c) **the model as a precise specification**, and (d) **verifying a design before building it**. MPAIR-05's verdict must therefore be graded on (a)-(d), with brute-force timing kept as *one* reported data point rather than the pass/fail axis. A negative verdict remains passing; an unchecked assertion still fails.
- [x] **MPAIR-07** *(added 2026-08-20, owner-authorized after research — see `22-CONTEXT.md` D-06)*: **Go/no-go physics gate, resolved BEFORE any `.frg` is written.** Determine whether this pipeline physically permits ancilla-mode reuse at all: CP(α) post-selection is deferred to the very end (never per-gate, since `Processor.set_postselection()` rejects conditions on modes a later component touches), so ancilla modes are not deterministically restored to vacuum mid-circuit and a second pair's gate would act on a generally non-vacuum, entangled state. Resolve via amplitude calculation and/or a literature check on ancilla reuse in post-selected linear-optical gates. **This gate can invalidate the phase's premise** — if reuse is invalid, pooling is moot, contiguous allocation was correct after all, and the honest outcome is to report that and stop rather than model an unbuildable scheme. Must be a real branch with a stated stop condition, not a formality.
- [ ] **MPAIR-06**: The verified scheme recorded as a **specification for future implementation** in `docs/iqp-photonic-encoding.md`, explicitly stating that no Python implements it yet — so unlike `forge/ancilla_mapping.frg` (which re-states an already-shipped formula with nothing linking the two, and carries a standing drift warning because of it), this model is the source of truth any eventual implementation must be checked against.

### Ancilla Lifecycle Safety — Formal Verification (LIFE)

*Added 2026-08-21, owner-authorized as additive v3.0 scope (Phase 23). Owner chose "both" when offered colouring-only, lifecycle-only, or both — accepting explicitly-stated multi-phase scope. Phase 22 answers **how few** ancilla blocks are needed (the mode-budget question); Phase 23 answers **whether reuse is structurally safe at all** (the trace question). These are genuinely different questions.*

*Idiom source: the owner's own CS1710 memory-management work (`cs1710/hw/cs1710-memory-management-alejack312/stop_and_copy.frg` and `mark_and_sweep.frg`) — ancilla pooling is a memory-allocation-and-reuse problem, and "is this mode free yet?" is a liveness/collection question.*

- [ ] **LIFE-01**: Ancilla modes modeled as allocatable cells with an explicit lifecycle (free -> allocated -> in-use -> releasable) across a *sequence* of CP(alpha) gate applications, following the `stop_and_copy.frg` / `mark_and_sweep.frg` idiom (explicit `State` sig in relational Forge, or `#lang forge/temporal` — the choice is a discuss-phase decision, not pre-locked here).
- [ ] **LIFE-02**: Safety property — no ancilla mode is reallocated to a later gate while still live from an earlier one. **A counterexample must be a trace** (a sequence of gate applications that silently clobbers an in-use ancilla), not a number — this is the "scenario you wouldn't think to enumerate" case that MPAIR-05's corrected criterion identifies as Forge's actual contribution.
- [ ] **LIFE-03**: The deferred-post-selection constraint encoded explicitly — collection cannot occur mid-circuit (`Processor.set_postselection()` rejects conditions on modes a later component touches), so a mode becomes releasable only at the final post-selection. This is the constraint that distinguishes this from a textbook allocator, and is the structural counterpart of Phase 22's MPAIR-07 numerical probe.
- [ ] **LIFE-04**: Non-vacuity — an instance exists with at least 2 sequential gates and at least one genuine mode reuse, conjoined with the safety property holding (a witness that reuses but is unsafe proves nothing).
- [ ] **LIFE-05**: Cross-check the model's structural verdict against Phase 22's MPAIR-07 *numerical* verdict. These are independent methods answering the same question (one measures amplitudes, one reasons about lifecycle structure) — agreement strengthens both; disagreement is a finding to report and investigate, never to reconcile by assumption. Follows this project's established independent-cross-check precedent (VERIFY-01..04, Julia vs Python).
- [ ] **LIFE-06**: State whether the safe-reuse constraint *changes* Phase 22's minimum-block-count result — if lifetime constraints make the conflict structure something other than K_n's line graph, the minimum colouring may differ from the Koenig/Vizing value and the combinatorics genuinely harden (minimum edge colouring is NP-hard for general graphs, Holyer 1981). Report either way.
- [ ] **LIFE-07**: Findings folded into `docs/iqp-photonic-encoding.md` alongside Phase 22's section, stating plainly what the lifecycle model does and does not establish.

## v2 Requirements

Deferred to a future release, per FEATURES.md's explicit "Future Consideration" list.

### Trainability / Hardness

- **STUDY-03**: Distinguishability/g² noise as a second noise axis beyond pure photon loss
- **STUDY-04**: Any complexity-theoretic proof work (barren-plateau theorem, loss-threshold reduction) for this specific ansatz — explicitly out of scope for this or any near-term milestone absent a scope change

## Out of Scope

Explicitly excluded this milestone. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Peer-review-grade barren-plateau theorem for this ansatz | This milestone is an empirical study, matching this project's established "design/mapping exercise, not a proof" precedent (ENC-02) |
| Reaching hardware-relevant N (≥50) to settle the asymptotic question definitively | Infeasible given Fock-space simulation cost and the Sept 1 deadline; chasing it risks repeating the historical stall pattern |
| Exhaustive hyperparameter/loss-function/observable grid search | This project's established scope discipline calls for one well-justified choice, stated and defended |
| Independent from-scratch CV/Gaussian barren-plateau derivation | This circuit is discrete-Fock, non-Gaussian passive linear optics — the Gaussian-case result doesn't directly transplant, and re-deriving it is its own open research problem |
| Full complexity-theoretic reduction proof of a loss threshold for this circuit | Explicitly excluded by this project's own ENC-02 precedent; positioned as a literature comparison instead |
| SDP-based Bell-inequality/nonlocality certification via ket.jl | Research found this answers a different question than "does sampling hardness survive loss"; ket.jl/SDP stays parked as the owner's personal summer study, unrelated to this milestone |
| Hardware-realism noise modeling beyond photon loss (dark counts, detector inefficiency, phase drift) as a required component | Loss is the one new realism dimension this milestone adds; weight-1/weight-2 validation was explicitly idealized/lossless |
| Empirically observing the classical-simulability transition itself at this project's small, fixed n | Asymptotic transitions are scaling properties this project's small n cannot exhibit on its own — would be an overclaim; comparison to literature thresholds is the honest framing |
| Bespoke from-scratch linear-optical decomposition of `CP(α)` | Unnecessary — the already-published, already-verified `PostProcessedControlledRotationsItem` catalog gate is lower-risk and sufficient |
| Deterministic (success-probability = 1) two-qubit gate | Known-infeasible for linear-optical two-qubit entangling gates without additional resources — standard, settled KLM-era knowledge |
| Patching/re-deriving `heralded_cz`'s internals to expose an angle parameter | Already confirmed a dead end (hardcoded class constants, no exposed kwarg) — `PostProcessedControlledRotationsItem` is a separate, parallel gate family instead |
| Peer-review-submission-ready manuscript for WRITE-01 | This is a defensible personal technical write-up for a specific reader (Vincent Espitalier) and deadline, not a paper submission |
| Generic QML/photonics textbook background padding in WRITE-01 | Contradicts this project's established terse, load-bearing-only documentation style |
| Python implementation of the k-pair (multi-ZZ) weight-2 circuit | Phase 22 is verification-before-implementation by design — the whole argument for using Forge here is that the scheme can be proven for all `k` up to a large bound even though simulation cost (4 extra modes per pair) means only `k=2` or `3` would ever actually run. Implementation is a separate, later decision. |
| Re-running the hardness-under-loss study with multiple ZZ terms | The genuine research-gap close, and the reason multi-pair support is interesting at all — but it is v4.0-sized (new sweeps, new exact references, new Julia cross-checks), not one additive phase. Owner-confirmed 2026-08-20. |
| Deciding the allocation scheme on the owner's behalf | MPAIR-01 exists specifically to prevent this. Claude presents candidates without ranking; the design call is the owner's. |

## Traceability

Which phases cover which requirements. Populated during roadmap creation (2026-08-07).

| Requirement | Phase | Status |
|-------------|-------|--------|
| VERIFY-01 | 14 - Julia Toolchain Spike | Complete |
| ARB-01 | 15 - ARB-01 Core Gate De-Risking & Validation | Complete |
| ARB-02 | 15 - ARB-01 Core Gate De-Risking & Validation | Complete |
| ARB-03 | 15 - ARB-01 Core Gate De-Risking & Validation | Complete |
| ARB-04 | 15 - ARB-01 Core Gate De-Risking & Validation | Complete |
| ARB-05 | 15 - ARB-01 Core Gate De-Risking & Validation | Complete |
| ARB-06 | 15 - ARB-01 Core Gate De-Risking & Validation | Complete |
| ARB-07 | 16 - ARB-01 Extended Validation & Postselection Bookkeeping | Complete |
| ARB-08 | 16 - ARB-01 Extended Validation & Postselection Bookkeeping | Complete |
| ARB-09 | 16 - ARB-01 Extended Validation & Postselection Bookkeeping | Complete |
| TRAIN-01 | 17 - Trainability / Barren-Plateau Study | Complete |
| TRAIN-02 | 17 - Trainability / Barren-Plateau Study | Complete |
| TRAIN-03 | 17 - Trainability / Barren-Plateau Study | Complete |
| TRAIN-04 | 17 - Trainability / Barren-Plateau Study | Complete |
| TRAIN-05 | 17 - Trainability / Barren-Plateau Study | Complete |
| TRAIN-06 | 17 - Trainability / Barren-Plateau Study | Complete |
| TRAIN-07 | 17 - Trainability / Barren-Plateau Study | Complete |
| TRAIN-08 | 17 - Trainability / Barren-Plateau Study | Complete |
| TRAIN-09 | 17.1 - Trainability Follow-Up: Bandwidth & Init Sensitivity | Complete |
| TRAIN-10 | 17.1 - Trainability Follow-Up: Bandwidth & Init Sensitivity | Complete |
| HARD-01 | 18 - Hardness-Under-Loss Assessment | Complete |
| HARD-02 | 18 - Hardness-Under-Loss Assessment | Complete |
| HARD-03 | 18 - Hardness-Under-Loss Assessment | Complete |
| HARD-04 | 18 - Hardness-Under-Loss Assessment | Complete |
| HARD-05 | 18 - Hardness-Under-Loss Assessment | Complete |
| HARD-06 | 18 - Hardness-Under-Loss Assessment | Complete |
| HARD-07 | 18 - Hardness-Under-Loss Assessment | Complete |
| VERIFY-02 | 19 - Independent Julia Cross-Checks | Complete |
| VERIFY-03 | 19 - Independent Julia Cross-Checks | Complete |
| VERIFY-04 | 19 - Independent Julia Cross-Checks | Complete |
| WRITE-01 | 20 - Technical Write-Up | Complete |
| WRITE-02 | 20 - Technical Write-Up | Complete |
| WRITE-03 | 20 - Technical Write-Up | Complete |
| WRITE-04 | 20 - Technical Write-Up | Complete |
| WRITE-05 | 20 - Technical Write-Up | Complete |
| WRITE-06 | 20 - Technical Write-Up | Complete |
| WRITE-07 | 21 - External-Facing Framing Pass | Complete |
| MPAIR-01 | 22 - Multi-Pair Ancilla Allocation (Forge) | Complete |
| MPAIR-02 | 22 - Multi-Pair Ancilla Allocation (Forge) | Complete |
| MPAIR-03 | 22 - Multi-Pair Ancilla Allocation (Forge) | Pending |
| MPAIR-04 | 22 - Multi-Pair Ancilla Allocation (Forge) | Pending |
| MPAIR-05 | 22 - Multi-Pair Ancilla Allocation (Forge) | Pending |
| MPAIR-06 | 22 - Multi-Pair Ancilla Allocation (Forge) | Pending |
| MPAIR-07 | 22 - Multi-Pair Ancilla Allocation (Forge) | Complete |
| LIFE-01 | 23 - Ancilla Lifecycle Safety (Forge) | Pending |
| LIFE-02 | 23 - Ancilla Lifecycle Safety (Forge) | Pending |
| LIFE-03 | 23 - Ancilla Lifecycle Safety (Forge) | Pending |
| LIFE-04 | 23 - Ancilla Lifecycle Safety (Forge) | Pending |
| LIFE-05 | 23 - Ancilla Lifecycle Safety (Forge) | Pending |
| LIFE-06 | 23 - Ancilla Lifecycle Safety (Forge) | Pending |
| LIFE-07 | 23 - Ancilla Lifecycle Safety (Forge) | Pending |

**Coverage:**
- v1 requirements: **51 total** (TRAIN: 10, HARD: 7, ARB: 9, VERIFY: 4, WRITE: 7, MPAIR: 7, LIFE: 7). Note: this file's summary line previously stated "34 total" then corrected to "35 total" (8+7+9+4+7=35, arithmetic-error fix during roadmap creation); now 37 following the 2026-08-12 addition of TRAIN-09/TRAIN-10 (see below) — a real scope addition, not an arithmetic correction.
- Mapped to phases: 51/51 ✓
- Unmapped: 0 ✓

---
*Requirements defined: 2026-08-07*
*Last updated: 2026-08-20 — added MPAIR-01..06 (Phase 22, Multi-Pair Ancilla Allocation — Formal Verification), owner-authorized as additive v3.0 scope rather than a new milestone. 43 v1 requirements total, up from 37; 37 Complete, 6 Pending. Phases 14-21 remain shipped and unreopened.*
*Prior update: 2026-08-19 — WRITE-07 (Phase 21, External-Facing Framing Pass) marked Complete. All 37 v1 requirements defined at that point were Complete — 37/37, 0 Pending.*
*Prior update: 2026-08-12 (later same day) — added TRAIN-09 and TRAIN-10, owner-authorized follow-up experiments to Phase 17's trainability study, discovered via a fresh direct read of 8 literature papers (owner's explicit instruction not to rely on the sibling project's secondhand vault notes). TRAIN-09 tests whether Phase 17's fixed MMD bandwidth (not just circuit/init) is itself sufficient to produce the measured exponential-decay signature (Rudolph et al., arXiv:2305.02881). TRAIN-10 tests a literature-sourced data-dependent initialization (Recio-Armengol et al., arXiv:2503.02934) as a real alternative to the inconclusive `small_angle` scheme. Both mapped to a new inserted phase, 17.1 (see ROADMAP.md), rather than reopening the already-shipped, already-verified Phase 17 itself. Earlier same-day update: traceability table's TRAIN-01..08 rows corrected from "Pending" to "Complete" (Phase 17 finished and verified 2026-08-11; flagged by gsd-verifier during Phase 17's own verification pass, fixed same day). Dual-rail/MerLin exploration work done after Phase 17 closed (see docs/trainability-study.md's "Independent cross-check" section, .planning/STATE.md) remains explicitly supplementary and separate from TRAIN-09/10.*
