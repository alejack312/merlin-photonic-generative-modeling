---
phase: 11-cz-insertion-unit-weight-2-circuit-composition
plan: 02
subsystem: quantum-photonic-encoding
tags: [perceval, heralded-cz, processor-composition, mode-mapping, polarization, herald-registration, iqp]

# Dependency graph
requires:
  - phase: 11-cz-insertion-unit-weight-2-circuit-composition (Plan 01)
    provides: "build_cz_insertion(n, i, j) -- PBS-wrap -> heralded_cz -> PBS-unwrap Circuit(6), with herald_spec read from HeraldedCzItem's own in_heralds"
provides:
  - "build_weight2_processor(n, i, j, thetas) in iqp_photonic_encoding.py: full Processor(2n+2) weight-2 IQP generator pipeline (state prep -> theta-folded diagonal layer -> CZ insertion via mode-mapping dict -> conjugation -> readout)"
  - "Confirmed, exact global herald registration ({2n: 1, 2n+1: 1}) immediately after assembly"
  - "Herald-success sanity check proving the full mode-mapping-dict embedding (not just the local Circuit(6)) preserves heralded_cz's 2/27 success probability"
  - "sha256 snapshot regression guard on build_state_prep_circuit's unitary, for future phases that touch this shared module"
  - "Confirmed Perceval limitation: Processor.add_herald() + PBS-containing circuit + Processor.probs() crashes unconditionally; separately, state_prep's real Hadamard superposition + heralded ancilla gives silently wrong (non-crashing) probabilities via PolarizationSimulator -- both block naive use of Processor.probs() on the fully composed, herald-registered pipeline"
affects: [12-exact-reference-extension-tvd-validation, 13-weight-1-weight-2-composability-validation]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Processor.add(mode_mapping_dict, sub_circuit) for non-contiguous mode wiring: ModeConnector auto-inserts a PERM before and its exact inverse after, transparently restoring the outer processor's mode numbering for every subsequent .add() call"
    - "Explicit, immediate herald re-registration (add_herald right after the .add() that wires in a herald-owning sub-circuit) rather than relying on any auto-shift/auto-propagation mechanism -- composing a bare Circuit never carries herald metadata"
    - "Additive theta-folding for the CZ/ZZ operator identity: fold pi/4 corrections into the SAME thetas argument a weight-1 generator on the same qubits would already use, never a separate gate"
    - "When Perceval's PolarizationSimulator+heralds combination is unreliable/crashes, verify the invariant with heralds unregistered (bare Processor, manual post-selection on ancilla output modes) and a definite computational-basis input (skip Hadamard-superposition-inducing stages) -- stays inside the library's working envelope while still proving the real claim"

key-files:
  created: []
  modified:
    - iqp_photonic_encoding.py
    - tests/test_iqp_photonic_encoding.py

key-decisions:
  - "Herald-success sanity check adapted to skip both add_herald() registration and build_state_prep_circuit's Hadamard, verifying via manual post-selection on a bare (herald-unregistered) Processor at a definite computational-basis input instead -- the literal plan recipe (full build_weight2_processor + add_herald + all_h_input + probs()) crashes unconditionally due to a confirmed Perceval PolarizationSimulator limitation (matmul shape mismatch when add_herald is combined with any PBS-containing circuit), independent of thetas or state_prep"
  - "This adapted check still validates strictly more than Plan 11-01's local Circuit(6) truth table: it proves the herald-success invariant survives embedding through the SAME mode-mapping dict (Processor.add with a non-contiguous mapping) build_weight2_processor uses in production, which Plan 11-01 never exercised"

patterns-established:
  - "Herald re-registration is always explicit and immediate at the composition site, never inferred -- matches the CONTEXT.md-locked decision and gives a discoverable, auditable failure mode (Processor.heralds == {} until add_herald is called) instead of a silent unheralded raw unitary"

# Metrics
duration: ~50min
completed: 2026-08-06
---

# Phase 11 Plan 02: Weight-2 Circuit Composition Summary

**`build_weight2_processor(n, i, j, thetas)` assembles the full weight-2 IQP generator pipeline as a `Processor(2n+2)` via `Processor.add()`, reusing every weight-1 builder unmodified, with `pi/4` corrections folded additively and heralds registered at exact global indices `{2n: 1, 2n+1: 1}` immediately after composition.**

## Performance

- **Duration:** ~50 min
- **Started:** 2026-08-06T11:20:00+02:00 (approx.)
- **Completed:** 2026-08-06T12:10:00+02:00 (approx.)
- **Tasks:** 2
- **Files modified:** 2

## Accomplishments
- `build_weight2_processor(n, i, j, thetas)` implemented: `Processor(2n+2)` assembled from `build_state_prep_circuit`, a `pi/4`-folded `build_diagonal_layer_circuit`, `build_cz_insertion` (Plan 11-01) wired via an explicit mode-mapping dict, `build_conjugation_circuit`, and `build_readout_circuit` -- every weight-1 builder reused with zero modification.
- Theta folding is additive and non-mutating: `thetas_folded[i] += pi/4`, `thetas_folded[j] += pi/4`, copied from the caller's list, realizing the CZ/ZZ operator identity documented in `docs/iqp-photonic-encoding.md`.
- Heralds registered immediately after the CZ insertion's `.add()` call, reading `build_cz_insertion`'s own `herald_spec` (never hardcoded) -- confirmed `proc.heralds == {2n: 1, 2n+1: 1}` exactly, satisfying Success Criterion 3.
- All 4 of Phase 11's ROADMAP Success Criteria now satisfied (Criterion 1 by Plan 11-01, Criteria 2-4 by this plan).
- Discovered and worked around a genuine, previously only partially-flagged Perceval limitation: `Processor.add_herald()` combined with any `PBS`-containing circuit crashes `Processor.probs()` unconditionally (a `matmul` shape mismatch inside `PolarizationSimulator._prepare_input`), and separately, a real Hadamard-created superposition (`build_state_prep_circuit`) feeding a heralded-ancilla sub-circuit gives silently wrong (non-crashing) numbers -- both confirmed by direct execution, both carried forward as concerns for Plan 12's TVD validation strategy.

## Task Commits

Each task was committed atomically:

1. **Task 1: Implement build_weight2_processor(n, i, j, thetas)** - `d961366` (feat)
2. **Task 2: Herald/sanity checks, non-regression snapshot, and full-suite verification** - `96246a4` (test)

**Plan metadata:** (this commit, docs)

## Files Created/Modified
- `iqp_photonic_encoding.py` - Added `build_weight2_processor(n, i, j, thetas)`
- `tests/test_iqp_photonic_encoding.py` - Added `test_weight2_processor_heralds_nonempty`, `test_weight2_herald_success_sanity` (plus its `_build_weight2_tail_no_state_prep` helper), `test_weight1_builders_unitary_unchanged` (sha256 snapshot regression guard)

## Decisions Made
- **Additive theta folding, never mutating the caller's list** -- `thetas_folded = list(thetas)` before incrementing indices `i` and `j`, matching the CONTEXT.md-locked rule Phase 13's mixed-circuit test depends on.
- **Straight (unswapped) mode-mapping dict** -- the ctrl/data convention adapter already lives entirely inside `build_cz_insertion` (Plan 11-01), so the mapping dict in `build_weight2_processor` is the plain, unswapped port order: `{2i: 0, 2i+1: 1, 2j: 2, 2j+1: 3, 2n: 4, 2n+1: 5}`.
- **Herald registration adapted for the sanity test, not for the production function** -- `build_weight2_processor` itself still calls `add_herald` exactly as the plan specifies (this is correct and required -- see Success Criterion 3's own verification, which passed cleanly with no crash: it's `Processor.probs()` specifically that's incompatible with the `add_herald` + `PBS` combination, not `add_herald` or `.heralds` alone). Only the *test* verifying herald-success probability was adapted to avoid calling `.probs()` on that combination.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] Adapted the herald-success sanity check to avoid a Perceval PolarizationSimulator crash**
- **Found during:** Task 2 (writing `test_weight2_herald_success_sanity`)
- **Issue:** The plan's Task 2 action specified calling `proc.compute_physical_logical_perf(True)`, `proc.with_input(all_h_input(n))`, `proc.probs()` directly on `build_weight2_processor`'s output (which has `add_herald` already registered and contains `PBS` components). This crashes unconditionally with `ValueError: matmul: Input operand 1 has a mismatch in its core dimension 0 ... (size 12 is different from 16)` inside `perceval/simulators/polarization_simulator.py`'s `_prepare_input` -- confirmed by direct execution to be independent of `thetas` or whether `state_prep` is included; the crash is triggered purely by combining a registered herald with any `PBS`-containing circuit through `Processor.probs()`. Separately (a distinct, non-crashing issue), even without `add_herald`, routing `build_state_prep_circuit`'s real Hadamard-created superposition into the heralded-ancilla sub-circuit gives silently wrong probabilities (`0.1646` measured vs `0.07407` expected) via `PolarizationSimulator` -- the same unannotated-ancilla-photon-distinguishability artifact Plan 11-01's summary already flagged as a carry-forward concern, now confirmed to also affect real Hadamard-created superpositions (not just directly-constructed dual-rail superposition states).
- **Fix:** Rewrote the sanity check to stay inside Perceval's confirmed-working envelope: a bare `Processor` (no `add_herald` registered, so `Processor.probs()` works) built with `build_weight2_processor`'s exact diagonal-layer -> CZ-insertion (mode-mapping dict) -> conjugation -> readout wiring, MINUS `build_state_prep_circuit`'s leading Hadamard (so the CZ insertion receives a definite computational-basis input, since `WP(theta,0)` leaves a definite input state up to global phase). Herald-success is computed by hand via post-selection on the ancilla output modes matching `herald_spec`'s expected photon counts, with explicit real photons on the ancilla input modes (Phase 10 Pitfall 1: heralds need a real input photon, not vacuum). This still validates strictly more than Plan 11-01's local-`Circuit(6)`-only truth table, since it proves the invariant survives the full mode-mapping-dict embedding `build_weight2_processor` actually uses in production.
- **Files modified:** `tests/test_iqp_photonic_encoding.py`
- **Verification:** `test_weight2_herald_success_sanity` passes, matching `2/27` to `1e-9`; full plan suite (36 tests) and full repo suite (107 tests) pass.
- **Committed in:** `96246a4` (Task 2 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** `build_weight2_processor` itself is unaffected -- it calls `add_herald` exactly as the plan specifies, and Success Criterion 3's own verification (`proc.heralds == {2n: 1, 2n+1: 1}`, no `.probs()` call involved) passed with zero issues. Only the supplementary sanity-check *test* needed adaptation to route around a confirmed Perceval library limitation that has no workaround at the `Processor.probs()` level. No scope creep -- the adapted test validates the same invariant, just measured through a path that actually executes.

## Issues Encountered
- Perceval's `Processor.add_herald()`, when combined with any `PBS`-containing circuit, makes `Processor.probs()` crash unconditionally (confirmed via direct execution across multiple theta values and with/without `state_prep` -- always the same `matmul` shape-mismatch error inside `PolarizationSimulator._prepare_input`). This is a hard blocker for any future code that wants to call `.probs()` on `build_weight2_processor`'s output directly -- **critical for Plan 12 to know before design**: Plan 12's TVD validation cannot use `Processor.probs()` on the fully composed, herald-registered `build_weight2_processor` output. It will need either (a) a different measurement API that doesn't route through `PolarizationSimulator` with heralds attached, (b) a workaround analogous to this plan's (bare processor + manual post-selection, no `add_herald`), or (c) to file/investigate this as a genuine Perceval bug upstream. This is now flagged in STATE.md's Blockers/Concerns.
- Separately, even without `add_herald`, real Hadamard-created superposition (from `build_state_prep_circuit`) combined with the heralded-ancilla sub-circuit gives silently wrong (not crashing) probabilities via `PolarizationSimulator` -- consistent with, and now extending, Plan 11-01's already-documented ancilla-distinguishability finding. Plan 12 needs a validation strategy that avoids this combination entirely, not just a crash-avoidance workaround.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- `build_weight2_processor(n, i, j, thetas)` is complete and satisfies all 4 of Phase 11's ROADMAP Success Criteria. `iqp_photonic_encoding.py` now provides the full weight-2 pipeline entry point Plan 12 needs.
- **Blocking concern for Plan 12 (TVD validation):** `Processor.probs()` cannot be called on `build_weight2_processor`'s output as-is when `add_herald` has been registered -- this will crash. Plan 12 must design its TVD-measurement approach around this constraint from the start (see "Issues Encountered" above), not discover it mid-execution. Recommended starting point: reproduce this plan's `_build_weight2_tail_no_state_prep`-style bare-processor + manual-post-selection pattern, extended to cover `state_prep`'s superposition case as well (which will need its own investigation, since the manual-post-selection workaround alone does not fix the separate wrong-numbers-under-superposition issue).
- The existing 32-test weight-1 suite (Phase 9 + Phase 10) plus Plan 11-01's 4 tests plus this plan's 3 tests all pass -- 107/107 total, zero regressions. The `test_weight1_builders_unitary_unchanged` snapshot check is now in place to catch any future accidental edit to the shared weight-1 builders.

---
*Phase: 11-cz-insertion-unit-weight-2-circuit-composition*
*Completed: 2026-08-06*
