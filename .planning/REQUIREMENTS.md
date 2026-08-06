# Requirements: MerLin Photonic Generative Modeling — v2.1 Weight-2 Implementation

**Defined:** 2026-08-05
**Core Value (this milestone):** Get the weight-2 IQP generator (derived on paper in v2.0 but never built) actually implemented and validated to the same bar weight-1 already cleared — exact reference, herald-conditioned TVD comparison, no silently-discarded failure mass.

## v1 Requirements

Requirements for this milestone (v2.1). Each maps to roadmap phases (continuing numbering from v2.0's Phase 9).

### Weight-2 Circuit Implementation

- [x] **WT2-01**: Weight-2 generator circuit implemented — `PBS`→`heralded_cz`→`PBS` plus the two `WP(π/4,0)` single-qubit corrections, wired into the existing 2n-mode-per-register layout, reusing the existing weight-1 builders (`build_state_prep_circuit`, `build_conjugation_circuit`, `build_readout_circuit`) unmodified via `Processor`-level composition (not a `Circuit`-level modification, per the research finding that `heralded_cz` requires `Processor` composition)
- [ ] **WT2-02**: `exact_qubit_iqp_distribution` (or a sibling function) extended to accept weight-2 pair terms (`Z_iZ_j`), reusing the existing bit-ordering convention

### Validation

- [ ] **WT2-03**: Herald-conditioned photonic distribution computed, with herald-failure probability and out-of-subspace decode residual reported as two separate, explicit numbers — never merged into one figure, never silently renormalized away, per this project's established ENC-03 honesty-ledger policy
- [x] **WT2-04**: Exact (analytic, not sampled) herald-success probability computed for this specific `heralded_cz` implementation, read directly off Perceval's exact backend (`Analyzer.performance` / `logical_perf`) — not estimated via shot-based sampling
- [ ] **WT2-05**: TVD validation test at n=2, θ=π/4, comparing the extended exact qubit-side reference (WT2-02) against the herald-conditioned photonic distribution (WT2-03), in the same style/tolerance conventions as the existing `test_enc04_toy_validation_runs_end_to_end`
- [ ] **WT2-06**: Test coverage added to `tests/test_iqp_photonic_encoding.py` for WT2-01 through WT2-05, matching existing test conventions
- [ ] **WT2-07**: n=3 mixed generator test — 2 weight-1 terms plus 1 weight-2 term in the same circuit, confirming weight-1 and weight-2 layers compose correctly
- [x] **WT2-08**: Literature comparison note documenting the measured herald-success probability alongside the design doc's previously-flagged, unverified literature figures (1/9 post-selected, ~2/27 heralded) — descriptive only, no equality claimed

## v2 Requirements

Deferred to a future milestone, contingent on this milestone's findings.

### Beyond Fixed-Angle Weight-2

- **ARB-01**: Arbitrary-θ weight-2 generator (continuously tunable `exp(iθ·Z_iZ_j)`, θ≠π/4) — needs new paper-derivation work first, not resolvable from the existing `heralded_cz` catalog gate alone

### Trainability & Hardness Study (carried from v2.0)

- **STUDY-01**: Trainability study — gradient variance vs. system size (barren-plateau check) against the qubit-IQP baseline
- **STUDY-02**: Hardness assessment — whether realistic photonic noise/loss breaks the mapped circuit's hardness claim
- **WRITE-01**: Write-up in a format decided by what the study finds

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Arbitrary-θ weight-2 generator | Owner confirmed: accept the fixed θ=π/4 limitation this milestone. `heralded_cz` is a fixed, non-parameterized catalog gate — no known decomposition realizes arbitrary θ from this catalog alone; resolving it would be new research, not implementation of what's already derived |
| Post-selected (non-heralded) CZ construction | Owner already chose the heralded construction over post-selected in v2.0 (`docs/iqp-photonic-encoding.md`); building a second gate variant for comparison is new scope, not this milestone's ask |
| Weight-3+ (three-or-more-qubit) generators | Not derived on paper anywhere in this project; no operator identity or catalog primitive identified; would need its own paper-derivation phase first |
| Shot-based (Monte Carlo) sampling of herald success probability | Perceval's exact backend already computes this quantity analytically and noiselessly; sampling would be strictly worse and would reintroduce exactly the shot-noise ambiguity this project's exact-validation philosophy already avoids |
| Loss/noise/hardware-realism modeling (photon loss, detector inefficiency, dark counts) | Owner confirmed this milestone is implementation + validation only. Existing weight-1 validation is explicitly idealized/lossless; weight-2 validation matches that same standard, not a new realism dimension |
| Trainability/hardness study (STUDY-01/02) and write-up (WRITE-01) | Owner confirmed: implementation + validation only this milestone. These remain deferred, contingent on weight-2 actually working — see v2 Requirements |
| Internal-consistency cross-check (conditioned-distribution sum × herald-success reconstructs raw mass) | Owner declined this differentiator when scoping — cheap but lowest marginal value of the three offered differentiators |

## Traceability

Which phases cover which requirements.

| Requirement | Phase | Status |
|-------------|-------|--------|
| WT2-01 | Phase 11 (CZ Insertion Unit & Weight-2 Circuit Composition) | Complete |
| WT2-02 | Phase 12 (Exact Reference Extension & TVD Validation) | Pending |
| WT2-03 | Phase 12 (Exact Reference Extension & TVD Validation) | Pending |
| WT2-04 | Phase 10 (Heralded-CZ Primitive De-Risking) | Complete |
| WT2-05 | Phase 12 (Exact Reference Extension & TVD Validation) | Pending |
| WT2-06 | Phase 12 (Exact Reference Extension & TVD Validation) | Pending |
| WT2-07 | Phase 13 (Weight-1 + Weight-2 Composability Validation) | Pending |
| WT2-08 | Phase 10 (Heralded-CZ Primitive De-Risking) | Complete |

**Coverage:**
- v1 requirements: 8 total
- Mapped to phases: 8/8 ✓
- Unmapped: 0 — no orphans

---
*Requirements defined: 2026-08-05*
*Last updated: 2026-08-06 after roadmap creation (Phases 10-13)*
