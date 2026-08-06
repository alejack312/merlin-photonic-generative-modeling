---
phase: 12-exact-reference-extension-tvd-validation
plan: 01
subsystem: testing
tags: [perceval, photonic-simulation, iqp, polarization-simulator, tvd, herald-conditioning]

# Dependency graph
requires:
  - phase: 11-cz-insertion-unit-weight-2-circuit-composition
    provides: build_weight2_processor(n, i, j, thetas) and build_cz_insertion(n, i, j) -- the production weight-2 pipeline this plan measures and validates
provides:
  - exact_qubit_iqp_distribution(n, thetas, pair_thetas=None) -- extended exact reference supporting Z_i*Z_j pair terms, backward compatible
  - photonic_weight2_iqp_distribution(n, i, j, thetas) -- herald-conditioned photonic weight-2 measurement, returns (dist, residual, herald_failure_prob) as three never-merged numbers
  - Confirmed, tested {P:V} ancilla annotation fix for PolarizationSimulator's silent distinguishability bug
  - Locked TVD gate (n=2, theta=pi/4) passing at machine precision, clearing ROADMAP Success Criterion 3
affects: [13-weight-1-weight-2-composability-validation]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Measurement-path processors mirror production processors' exact wiring/mode-mapping (never re-derive), differing only in what add_herald calls are omitted to avoid a confirmed Perceval crash"
    - "Herald-conditioned distributions reported as explicit 3-tuples (dist, residual, herald_failure_prob) -- never silently merged or renormalized into fewer numbers"

key-files:
  created: []
  modified:
    - iqp_photonic_encoding.py
    - tests/test_iqp_photonic_encoding.py

key-decisions:
  - "Ancilla input photons explicitly annotated {P:V} (not {P:H}, not bare integer) -- confirmed by 12-RESEARCH.md as the fix for PolarizationSimulator's silent distinguishability bug; without it the same code produces TVD~0.46 instead of ~1e-16 with no crash to flag the error"
  - "photonic_weight2_iqp_distribution does not expose pair_theta as a parameter -- the pi/4 fold is hardcoded inside _build_weight2_processor_no_herald (matching build_weight2_processor), since the CZ/ZZ identity is only exact at pi/4"
  - "_build_weight2_processor_no_herald reuses build_weight2_processor's exact wiring and mode-mapping dict rather than re-deriving it, so the measurement path can never silently drift from what's actually shipped"

patterns-established:
  - "Pattern: for Perceval circuits combining add_herald + PBS, never call add_herald on the measurement processor -- build a herald-unregistered sibling processor and post-select on ancilla output modes by hand"

# Metrics
duration: 25min
completed: 2026-08-06
---

# Phase 12 Plan 01: Exact Reference Extension & TVD Validation Summary

**Weight-2 photonic IQP generators validated against an extended exact qubit-side reference at TVD < 1e-9 (n=2, theta=pi/4), using the confirmed {P:V} ancilla-annotation fix for a Perceval `PolarizationSimulator` distinguishability bug that otherwise silently produces TVD~0.46 with no error.**

## Performance

- **Duration:** ~25 min
- **Tasks:** 3/3 completed
- **Files modified:** 2

## Accomplishments
- `exact_qubit_iqp_distribution` extended with an optional `pair_thetas` dict for `Z_i*Z_j` weight-2 pair terms, fully backward compatible (pair_thetas=None/omitted reproduces pre-Phase-12 behavior exactly)
- `_build_weight2_processor_no_herald`, `_weight2_input_state`, and `photonic_weight2_iqp_distribution` implemented, giving a crash-free measurement path for `build_weight2_processor`'s actual composed pipeline
- The locked WT2-05 TVD gate (n=2, i=0, j=1, theta=pi/4) passes with TVD well under the 1e-6 bar
- Full repository suite: 115/115 passing (107 pre-existing weight-1/infra tests + 8 new Phase 12 tests), zero regressions

## Task Commits

Each task was committed atomically:

1. **Task 1: Extend exact_qubit_iqp_distribution with Z_i*Z_j pair terms (WT2-02)** - `505ea6f` (feat)
2. **Task 2: Herald-conditioned weight-2 measurement path (WT2-03)** - `81f4253` (feat)
3. **Task 3: TVD gate test, herald-accounting test, and full suite verification (WT2-05, WT2-06)** - `d43b716` (test)

## Files Created/Modified
- `iqp_photonic_encoding.py` - `exact_qubit_iqp_distribution` extended with `pair_thetas`; new `_build_weight2_processor_no_herald`, `_weight2_input_state`, `photonic_weight2_iqp_distribution` functions added
- `tests/test_iqp_photonic_encoding.py` - 8 new tests: 2 for the `pair_thetas` extension, the locked n=2/theta=pi/4 TVD gate, the herald-accounting separation test, and an opportunistic n=3 bystander-qubit robustness check

## Decisions Made
- Reused `build_weight2_processor`'s exact mode-mapping dict inside `_build_weight2_processor_no_herald` rather than re-deriving it -- any drift there would have invalidated the validation's claim to be testing what's actually shipped.
- Kept `photonic_weight2_iqp_distribution`'s pi/4 fold hardcoded (not a caller-supplied parameter), consistent with `build_weight2_processor` and 12-RESEARCH.md's explicit recommendation, since the CZ/ZZ operator identity only holds exactly at that angle.
- Included the opportunistic n=3 bystander-qubit test (12-RESEARCH.md Step 5) since it added negligible time to the suite and strengthens the robustness claim beyond the single locked configuration.

## Deviations from Plan

None - plan executed exactly as written. Research (12-RESEARCH.md) had already resolved both open questions (the `{P:V}` annotation fix and the `add_herald`+`PBS` crash workaround) before this plan started, so no new Perceval limitations were discovered mid-execution.

## Issues Encountered

None - the plan's verification commands and the full suite run all passed on first attempt, consistent with 12-RESEARCH.md's pre-verified fix.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

Phase 13 (Weight-1 + Weight-2 Composability Validation) can now build directly on:
- `photonic_weight2_iqp_distribution(n, i, j, thetas)` as a trusted, tested measurement primitive for any weight-2 pair term
- `exact_qubit_iqp_distribution(n, thetas, pair_thetas)` as the trusted exact reference for mixed weight-1/weight-2 configurations
- The `{P:V}` ancilla-annotation pattern and the "never call add_herald on the measurement processor" pattern, both directly reusable for any future circuit combining PBS + heralded ancillas

No blockers or open concerns carried forward. The one remaining unresolved item from 12-RESEARCH.md (the mechanistic "why" `{P:V}` is correct, not just "that it works") is explicitly non-blocking -- documented as an open question in 12-RESEARCH.md, not required for Phase 13.

---
*Phase: 12-exact-reference-extension-tvd-validation*
*Completed: 2026-08-06*
