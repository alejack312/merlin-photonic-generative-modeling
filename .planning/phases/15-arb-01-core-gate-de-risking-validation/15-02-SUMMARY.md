---
phase: 15-arb-01-core-gate-de-risking-validation
plan: 02
subsystem: quantum-encoding
tags: [perceval, photonic, dual-rail, cp-gate, controlled-phase, convention-adapter, PERM]

# Dependency graph
requires:
  - phase: 15-01
    provides: "CP(alpha)'s bare-gate phase/structure confirmed at 3 non-trivial alpha plus the alpha=pi boundary (cp_gate_derisking.py)"
  - phase: 11-01
    provides: "_build_cz_insertion_core's PERM([1,0]) convention-adapter pattern, reused as the direct analog fix for CP"
provides:
  - "_build_cp_insertion_core(alpha): local Circuit(8) PERM-adapted CP(alpha), matches MODULE_DUAL_RAIL truth table diag(1,1,1,e^{i*alpha}) exactly"
  - "build_cp_insertion(n, i, j, alpha): PBS-wrapped Circuit(8) + ancilla_spec, mirroring build_cz_insertion's external contract"
  - "Confirmed boundary agreement: CP(alpha=pi) matches heralded_cz's diag(1,1,1,-1) sign-for-sign at the bare-core level"
affects: [16-arb-01-extended-validation-postselection-bookkeeping]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "CP(alpha) bare-core convention adapter: PERM([1,0]) on ctrl/data dual-rail pairs, direct analog of _build_cz_insertion_core -- confirmed sufficient standalone (no Step 2/3 fallback search needed) once PBS/state-prep/pipeline confounds are removed"

key-files:
  created: []
  modified:
    - iqp_photonic_encoding.py
    - tests/test_iqp_photonic_encoding.py

key-decisions:
  - "Step 1's direct analog fix (PERM([1,0]) on both qubit pairs) worked immediately in the isolated bare-core context -- Step 2 (re-run all 4 PERM combos) and Step 3 (manual unitary inspection) were not needed, confirming 15-RESEARCH.md's hypothesis that the full-pipeline attempt's TVD~0.3 failure was a confound from PBS/state-prep/conjugation/readout, not the ctrl/data convention itself."
  - "ancilla_spec (not herald_spec) is the deliberate name for build_cp_insertion's second return value, since all 4 values are expected-vacuum photon counts (post-selection), not 1-photon herald counts -- keeps the mechanism distinction (post-selection+vacuum vs. heralding) visible in the API, per ARB-05."

patterns-established:
  - "Bare-core isolation before full-pipeline wiring: when a full-pipeline circuit-wiring attempt fails to match a target truth table, isolate the new gate + convention adapter alone (no PBS/state-prep/pipeline) before assuming the convention-adapter search itself failed -- confounds from surrounding components can mask a correct adapter."

# Metrics
duration: 25min
completed: 2026-08-07
---

# Phase 15 Plan 02: CP(alpha) Bare-Gate Convention-Adapter De-Risking Summary

**`_build_cp_insertion_core(alpha)` and `build_cp_insertion(n, i, j, alpha)` added to `iqp_photonic_encoding.py`, using the exact same `PERM([1,0])` ctrl/data convention-adapter fix `_build_cz_insertion_core` already established for `heralded_cz`, confirmed via `Simulator.prob_amplitude` to reproduce `diag(1,1,1,e^{i*alpha})` on this module's `MODULE_DUAL_RAIL` convention -- including exact sign-for-sign agreement with `heralded_cz`'s `diag(1,1,1,-1)` at `alpha=pi`.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-08-07T09:42:00Z
- **Completed:** 2026-08-07T10:07:02Z
- **Tasks:** 2/2 completed
- **Files modified:** 2

## Accomplishments
- `_build_cp_insertion_core(alpha)`: isolated bare-core wiring (PERM -> CP(alpha) bare circuit -> PERM swap-back) confirmed to match `diag(1,1,1,e^{i*alpha})` exactly at 3 non-trivial alpha (pi/6, pi/3, 2pi/5) plus the alpha=pi boundary, on `MODULE_DUAL_RAIL`.
- Bare-core-level boundary-agreement confirmed: at alpha=pi, `_build_cp_insertion_core`'s sign pattern is identical to `_build_cz_insertion_core`'s already-confirmed `diag(1,1,1,-1)` -- negative real amplitude on `|1,1>` only, for both gate families.
- `build_cp_insertion(n, i, j, alpha)`: PBS-wrap -> `_build_cp_insertion_core(alpha)` -> PBS-unwrap, local `Circuit(8)`, returning `(circuit, ancilla_spec)` where `ancilla_spec` is read live from `PostProcessedControlledRotationsItem().build_experiment(...).in_heralds` (`{4:0, 5:0, 6:0, 7:0}`) -- not hardcoded.
- 6 new parametrized/direct tests added; full `tests/test_iqp_photonic_encoding.py` suite (53 tests) and full repo suite (132 tests) both pass with zero regressions.

## Task Commits

Each task was committed atomically:

1. **Task 1: Determine and verify CP's dual-rail convention adapter -- `_build_cp_insertion_core(alpha)`** - `345391d` (feat)
2. **Task 2: `build_cp_insertion(n, i, j, alpha)` wrapper + truth-table tests** - `78e7875` (feat)

_Note: No TDD-style test-then-implement split was used here -- both tests and implementation were verified together per the plan's task grouping._

## Files Created/Modified
- `iqp_photonic_encoding.py` - Added `_build_cp_insertion_core(alpha)` (local Circuit(8) convention adapter) and `build_cp_insertion(n, i, j, alpha)` (PBS-wrapped external contract, mirroring `build_cz_insertion`)
- `tests/test_iqp_photonic_encoding.py` - Added `test_cp_insertion_core_matches_diag_1_1_1_ealpha` (parametrized, 4 alpha values), `test_cp_insertion_core_boundary_matches_cz_insertion_core_sign_for_sign`, `test_cp_insertion_returns_circuit_and_ancilla_spec`

## Decisions Made
- **Step 1 sufficed; Steps 2-3 not needed.** The plan budgeted a 3-step bounded debugging search (direct analog fix -> re-run all 4 PERM combos -> manual unitary inspection) because 15-RESEARCH.md's full-pipeline attempt failed with all 4 combos (best TVD ~0.30). In this plan's isolated bare-core context (no PBS, no state-prep, no pipeline), Step 1's direct analog of `_build_cz_insertion_core`'s fix worked immediately and exactly (confirmed via `Simulator.prob_amplitude` at all 4 tested alpha values). This confirms 15-RESEARCH.md's own diagnosis: the full-pipeline TVD failure was caused by confounds elsewhere in the pipeline (PBS-wrap/state-prep/conjugation/readout composition, or the mode-mapping-dict arithmetic explicitly deferred to Plan 15-04), not by the ctrl/data convention-adapter search itself.
- **`ancilla_spec`, not `herald_spec`, as the return-value name.** Per the plan's explicit instruction and ARB-05's requirement to keep the post-selection+vacuum vs. heralding distinction visible: `build_cp_insertion`'s second return value is a dict of expected-vacuum (count 0) photon patterns, a fundamentally different meaning from `build_cz_insertion`'s `herald_spec` (expected 1-photon herald counts).

## Deviations from Plan

None - plan executed exactly as written. The plan explicitly anticipated the possibility that Step 1 might fail and gated Steps 2-3 as contingencies; Step 1 succeeded on the first attempt, so no fallback debugging was needed.

## Issues Encountered

None. To keep task-level commits atomic despite writing both functions' logic together during exploration, the implementation was split back into two sequential edits (core function alone for Task 1's commit, then the wrapper + tests for Task 2's commit) before committing -- a mechanical sequencing choice, not a deviation from what was built.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- Bare-gate-level de-risking for `CP(alpha)` is complete: the convention adapter is found, documented as a convention adapter (not a bug fix, matching `_build_cz_insertion_core`'s framing), and verified at both non-trivial alpha values and the alpha=pi boundary against `heralded_cz`'s already-confirmed ground truth.
- Plan 15-04 (full-pipeline wiring: PBS + CP + PBS composed with state-prep/diagonal/conjugation/readout, plus TVD validation against the exact reference) can now proceed knowing the bare-core convention wiring itself is solid -- any remaining TVD gap in the full pipeline is isolated to the composition/mode-mapping layer (PBS-wrap/state-prep/conjugation/readout integration, or the mode-mapping-dict arithmetic 15-RESEARCH.md explicitly deferred), not to the CP gate's own dual-rail convention.
- No blockers identified for Plan 15-04.

---
*Phase: 15-arb-01-core-gate-de-risking-validation*
*Completed: 2026-08-07*
