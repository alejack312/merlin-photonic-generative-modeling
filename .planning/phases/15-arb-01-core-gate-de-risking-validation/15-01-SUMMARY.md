---
phase: 15-arb-01-core-gate-de-risking-validation
plan: 01
subsystem: quantum-circuit-validation
tags: [perceval, photonic-gates, post-selection, phase-gate, simulator, pytest]

# Dependency graph
requires:
  - phase: 10-heralded-cz-primitive-de-risking
    provides: "heralded_cz_derisking.py's standalone-gate-first de-risking pattern (bare-circuit Simulator.prob_amplitude, module structure) reused directly for CP(alpha)"
  - phase: 12-exact-reference-extension-tvd-validation
    provides: "exact_qubit_iqp_distribution's pair_thetas parameterization, confirmed already generalized to arbitrary theta (referenced but not modified here)"
provides:
  - "cp_gate_derisking.py: standalone confirmation that PostProcessedControlledRotationsItem implements CP(alpha)=diag(1,1,1,e^{i*alpha}) via bare-circuit Simulator.prob_amplitude"
  - "Independent confirmation of the alpha=pi boundary: |amplitude|^2==1/9, sign pattern matches heralded_cz's diag(1,1,1,-1) exactly"
  - "Explicit alpha-vs-theta disambiguation (alpha=4*theta) encoded directly in code comments, resolving 15-CONTEXT.md's flagged ambiguity"
  - "tests/test_cp_gate_derisking.py: pytest regression coverage for all ARB-01 criterion-1 claims"
affects: [16-arb-01-extended-validation-postselection-bookkeeping, 20-technical-write-up]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Standalone bare-gate de-risking before circuit-wiring integration (heralded_cz_derisking.py's established pattern, now reused for a second gate family)"

key-files:
  created:
    - cp_gate_derisking.py
    - tests/test_cp_gate_derisking.py
  modified: []

key-decisions:
  - "alpha=pi (not alpha=pi/4) used as the boundary-check literal value, per 15-CONTEXT.md's owner-confirmed correction: CP's own dial (alpha) and this codebase's Z_iZ_j generator angle (theta) are related by alpha=4*theta, not equal"
  - "build_circuit() used directly (not build_experiment()) since the phase-only Simulator.prob_amplitude path needs no herald/postselect metadata -- matches heralded_cz_derisking.py's measure_cz_phase pattern exactly"

patterns-established:
  - "alpha (CP's raw dial) vs theta (Z_iZ_j generator angle) distinction stated explicitly in both module docstring and inline comments, to prevent the same ambiguity 15-CONTEXT.md flagged from resurfacing in Plans 15-02+"

# Metrics
duration: ~15min
completed: 2026-08-07
---

# Phase 15 Plan 01: CP(alpha) Core Gate De-Risking Summary

**Confirmed `PostProcessedControlledRotationsItem` implements `CP(α) = diag(1,1,1,e^{iα})` via `Simulator.prob_amplitude` on the bare 8-mode circuit at 3 non-trivial α (π/6, π/3, 2π/5) plus the α=π boundary, independently reproducing the 1/9 literature figure and `heralded_cz`'s exact sign pattern.**

## Performance

- **Duration:** ~15 min
- **Completed:** 2026-08-07
- **Tasks:** 2 completed
- **Files modified:** 2 (both new)

## Accomplishments
- `cp_gate_derisking.py` measures `CP(α)`'s bare-circuit phase/magnitude behavior directly against this repo's installed `perceval-quandela==1.2.4`, reproducing 15-RESEARCH.md's live-measured numbers as executable, asserted checks rather than cached results.
- Phase identity confirmed programmatically at all 4 tested α: `amp(1,1)/amp(0,0) == e^{iα}` to `1e-6` tolerance, with success probability printed as an explicit table (never collapsed to one number), satisfying ARB-04's bare-gate-level requirement.
- α=π boundary check independently confirms `|amplitude|² == 1/9` (previously only cited, unverified-for-this-exact-gate, in `docs/iqp-photonic-encoding.md`'s ENC-01 section) and the sign pattern matches `heralded_cz`'s `diag(1,1,1,-1)` exactly — resolving 15-CONTEXT.md's flagged α-vs-θ ambiguity in code, not just in prose.
- `tests/test_cp_gate_derisking.py` adds 8 pytest regression cases; full existing suite (65 tests total) stays green.

## Task Commits

1. **Task 1: Build cp_gate_derisking.py — CP(α) phase/structure confirmation** - `99a09f9` (feat)
2. **Task 2: Write tests/test_cp_gate_derisking.py — pytest regression coverage** - `28fc8a6` (test)

## Files Created/Modified
- `cp_gate_derisking.py` - Standalone module: `measure_cp_amplitudes(alpha, n=2)` builds `PostProcessedControlledRotationsItem().build_circuit(n=2, alpha=...)` and reads amplitudes via `Simulator(SLOSBackend()).prob_amplitude`; `main()` prints the success-probability-vs-α table and PASS/FAIL per check, asserting all of them.
- `tests/test_cp_gate_derisking.py` - Pytest coverage: phase-matches-e^{iα} (parametrized over 3 non-trivial α), uniform-magnitude (parametrized over all 4 tested α), and the α=π boundary check (1/9 magnitude + sign pattern).

## Decisions Made
- Used `alpha=π` (not `α=π/4`) as the literal boundary-check value, per 15-CONTEXT.md's owner-confirmed correction — the code encodes the `α=4θ` relationship explicitly in comments so this doesn't resurface as ambiguous in later plans (15-02+) or the eventual write-up.
- Used `build_circuit()` directly rather than `build_experiment()`, matching `heralded_cz_derisking.py`'s `measure_cz_phase` division of labor: the phase-only `Simulator` path needs only the bare unitary, not herald/postselect metadata (which is `build_experiment()`'s job, deferred to Plan 15-02's full-pipeline wiring).

## Deviations from Plan

None — plan executed exactly as written. All measured values (phase ratios, α=π magnitude=1/9, sign pattern) matched 15-RESEARCH.md's cached live-measurement table exactly on first run, no debugging needed.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- ARB-01's bare-gate-level phase/structure confirmation (criterion 1) and part of ARB-04's success-probability-vs-α table are now closed with executable, committed evidence — not just eyeballed research numbers.
- Plan 15-02 (circuit-wiring integration, per 15-RESEARCH.md's flagged Open Question 2) still needs a dedicated de-risking task: the PBS-wrap/CP-insertion/PBS-unwrap wiring into the existing pipeline did not reproduce the exact reference in research's spike (TVD ~0.3-0.4), and this plan's bare-gate confirmation does not resolve that — it only confirms the starting point (the bare gate itself) is correct, isolating the wiring as the sole remaining unknown.
- No blockers for Plan 15-02.

---
*Phase: 15-arb-01-core-gate-de-risking-validation*
*Completed: 2026-08-07*
