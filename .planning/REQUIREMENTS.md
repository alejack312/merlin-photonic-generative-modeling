# Requirements: MerLin Photonic Generative Modeling — v3.0 IQP Circuit Study & Write-Up

**Defined:** 2026-08-07
**Core Value:** A working, end-to-end, honestly-benchmarked MMD-trained photonic generative model, published in a public repo before Sept 1, 2026 — explainable unaided to Vincent Espitalier.

## v1 Requirements

All requirements below are Must-have for this milestone — owner's explicit, twice-confirmed call, no fallback/deferral ordering. Pitfalls research flagged this as real timeline risk (this is the first milestone since the PennyLane stall to combine a new toolchain with a hard deadline); the roadmap builds in an early Julia-toolchain checkpoint (mirroring v1.0's Jul-25 pattern) so a stall is visible early rather than silently absorbed.

### Trainability / Barren-Plateau Study (TRAIN)

- [ ] **TRAIN-01**: Gradient-variance sweep computed via exact parameter-shift on the existing distribution functions (`photonic_iqp_distribution`/`photonic_weight2_iqp_distribution`) — NOT via MerLin `QuantumLayer` autograd, which architecture research confirmed cannot accept this circuit's polarization-annotated `BasicState`s — across ≥3 system sizes, ≥100 independent random parameter draws each
- [ ] **TRAIN-02**: Explicit poly-vs-exponential model comparison (curve fit + goodness-of-fit, e.g. R²/AIC) — not an eyeballed plot
- [ ] **TRAIN-03**: Parameter-initialization distribution and per-circuit energy/photon-number normalization stated explicitly and controlled/reported across the sweep
- [ ] **TRAIN-04**: Generator scope of the sweep (weight-1-only vs. mixed) stated explicitly, with reasoning
- [ ] **TRAIN-05**: Honest statement of the max reachable system size `n`, and whether that range sits inside or outside the historically-misleading small-N regime this project's own pitfalls research documented (arXiv:2605.11879's N=2-10-vs-N=24 fit flip)
- [ ] **TRAIN-06**: Mixed weight-1+weight-2 generator sweep, reusing Phase 13's validated composability
- [ ] **TRAIN-07**: Cross-reference against `docs/iqp-baseline.md`'s qubit-side empirical plateau rule (97.9% accuracy, 283 rows) — does it transfer to the photonic realization?
- [ ] **TRAIN-08**: Sweep extended toward N≈20-24 if compute allows — the range where the cited precedent's poly-vs-exp fit is known to flip; honestly report if this range isn't reached

### Hardness-Under-Loss Assessment (HARD)

- [ ] **HARD-01**: Loss sweep via `Processor.probs()` + `NoiseModel(transmittance=η)` over a defined η grid — NOT `Analyzer`, which was confirmed to silently ignore loss entirely
- [ ] **HARD-02**: Cross-check against Perceval's independently-implemented `LossSimulator`/`LC` ancilla-beamsplitter loss model, at ≥1 shared η
- [ ] **HARD-03**: Full read (not abstract-only) of arXiv:2510.24137, with its noisy-IQP-specific threshold formula (if stated) extracted and cited — this is the load-bearing, currently-open gap blocking STUDY-02's central claim
- [ ] **HARD-04**: Explicit positioning of this project's fractional-loss model against Aaronson-Brod's fixed-loss-count regime — state which regime this project's tested loss levels actually sit in
- [ ] **HARD-05**: TVD-vs-η metric tracked against both (a) the lossless reference and (b) an explicitly-defined classically-easy baseline distribution
- [ ] **HARD-06**: Explicit "what this does/doesn't establish" scope statement, matching `docs/iqp-photonic-encoding.md`'s ENC-02 precedent
- [ ] **HARD-07**: Weight-2 loss sweep — physical photon loss compounded with `heralded_cz`'s herald-failure probability

### Arbitrary-θ Weight-2 Gate Validation (ARB)

- [x] **ARB-01**: Gate phase/structure confirmed at ≥3 non-trivial α values via `Simulator.prob_amplitude`, extending the single spot-check already done in research
- [x] **ARB-02**: General-α operator identity written down connecting `CP(α)` to `exp(iθZ_iZ_j)`, extending `docs/iqp-photonic-encoding.md`'s existing fixed-π/4 derivation
- [x] **ARB-03**: TVD validation against the extended exact qubit-side reference at ≥1 representative non-special α (ideally 2-3 values spanning the tested range)
- [x] **ARB-04**: Success probability reported as an explicit function of α (table or curve), never collapsed to a single number
- [x] **ARB-05**: Explicit written comparison to the existing fixed-π/4 `heralded_cz` construction — different gate family (post-selection + ancilla vacuum vs. ancilla heralding), stated plainly, not conflated
- [x] **ARB-06**: Test coverage added to `tests/test_iqp_photonic_encoding.py` matching existing tolerance/parametrization conventions
- [ ] **ARB-07**: n=3 mixed weight-1 + arbitrary-θ weight-2 composability test, direct parallel to Phase 13's existing test
- [ ] **ARB-08**: Denser α sweep (8-16 points across [0, 2π)) with success probability plotted as a continuous curve
- [ ] **ARB-09**: Forge model verifying the gate's `set_postselection` local→global ancilla mode-index translation is a valid, non-aliasing mapping — a narrow, bounded discrete-correctness check, not a numeric verifier

### Independent Julia Verifier (VERIFY)

- [x] **VERIFY-01**: Julia toolchain installed (`juliaup`, Yao.jl, BosonSampling.jl) with a hello-world circuit run successfully — the de-risking spike; sequenced early in the roadmap as this milestone's stall-risk checkpoint
- [ ] **VERIFY-02**: Yao.jl independent cross-check of the exact qubit-side IQP reference distribution (weight-1, at least n=2) against the existing Python/NumPy implementation
- [ ] **VERIFY-03**: BosonSampling.jl independent cross-check of the photonic-level exact distribution (weight-1 and/or weight-2) against Perceval's results, at least one shared test case
- [ ] **VERIFY-04**: BosonSampling.jl cross-check of STUDY-02's loss-model numbers at ≥1 shared η against the Python-computed TVD-vs-η result

### Technical Write-Up (WRITE)

- [ ] **WRITE-01**: Methodology-stated-before-results structure for each of the trainability, hardness-under-loss, and ARB-01 sections
- [ ] **WRITE-02**: Explicit comparison table against each named literature baseline (McClean et al., Aaronson-Brod, arXiv:2510.24137, arXiv:2405.01395, `docs/iqp-baseline.md`'s own empirical rule) — consistent with / inconsistent with / silent relative to, stated per baseline
- [ ] **WRITE-03**: Honest negative/inconclusive framing wherever the data warrants it, in the same direct language this project already used for GEN-07/LIT-04/Phase 7's neighbor-locality verdict
- [ ] **WRITE-04**: Explicit "what this does/doesn't establish" scope paragraph for each of the trainability, hardness-under-loss, and ARB-01 sections
- [ ] **WRITE-05**: Self-explanation checkpoint transcripts recorded in the write-up itself (owner's own interpretation transcribed first, per CLAUDE.md's standing rule)
- [ ] **WRITE-06**: Every reported number traceable to a specific script/test/notebook cell, with a fixed seed where randomness is involved
- [ ] **WRITE-07**: External-facing framing pass (README/case-study level), following this project's established "mechanism-not-magic, ownership-forward" convention — separate from the candid internal write-up

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
| ARB-07 | 16 - ARB-01 Extended Validation & Postselection Bookkeeping | Pending |
| ARB-08 | 16 - ARB-01 Extended Validation & Postselection Bookkeeping | Pending |
| ARB-09 | 16 - ARB-01 Extended Validation & Postselection Bookkeeping | Pending |
| TRAIN-01 | 17 - Trainability / Barren-Plateau Study | Pending |
| TRAIN-02 | 17 - Trainability / Barren-Plateau Study | Pending |
| TRAIN-03 | 17 - Trainability / Barren-Plateau Study | Pending |
| TRAIN-04 | 17 - Trainability / Barren-Plateau Study | Pending |
| TRAIN-05 | 17 - Trainability / Barren-Plateau Study | Pending |
| TRAIN-06 | 17 - Trainability / Barren-Plateau Study | Pending |
| TRAIN-07 | 17 - Trainability / Barren-Plateau Study | Pending |
| TRAIN-08 | 17 - Trainability / Barren-Plateau Study | Pending |
| HARD-01 | 18 - Hardness-Under-Loss Assessment | Pending |
| HARD-02 | 18 - Hardness-Under-Loss Assessment | Pending |
| HARD-03 | 18 - Hardness-Under-Loss Assessment | Pending |
| HARD-04 | 18 - Hardness-Under-Loss Assessment | Pending |
| HARD-05 | 18 - Hardness-Under-Loss Assessment | Pending |
| HARD-06 | 18 - Hardness-Under-Loss Assessment | Pending |
| HARD-07 | 18 - Hardness-Under-Loss Assessment | Pending |
| VERIFY-02 | 19 - Independent Julia Cross-Checks | Pending |
| VERIFY-03 | 19 - Independent Julia Cross-Checks | Pending |
| VERIFY-04 | 19 - Independent Julia Cross-Checks | Pending |
| WRITE-01 | 20 - Technical Write-Up | Pending |
| WRITE-02 | 20 - Technical Write-Up | Pending |
| WRITE-03 | 20 - Technical Write-Up | Pending |
| WRITE-04 | 20 - Technical Write-Up | Pending |
| WRITE-05 | 20 - Technical Write-Up | Pending |
| WRITE-06 | 20 - Technical Write-Up | Pending |
| WRITE-07 | 21 - External-Facing Framing Pass | Pending |

**Coverage:**
- v1 requirements: **35 total** (TRAIN: 8, HARD: 7, ARB: 9, VERIFY: 4, WRITE: 7). Note: this file's summary line previously stated "34 total" — 8+7+9+4+7=35, not 34; corrected here during roadmap creation as an arithmetic-error fix, not a scope change. All 35 IDs listed above were already present in the v1 Requirements section unchanged.
- Mapped to phases: 35/35 ✓
- Unmapped: 0 ✓

---
*Requirements defined: 2026-08-07*
*Last updated: 2026-08-07 after roadmap creation — traceability populated, 35/35 v1 requirements mapped to Phases 14-21, 100% coverage, no orphans*
