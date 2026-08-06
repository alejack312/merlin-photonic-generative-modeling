---
phase: 11-cz-insertion-unit-weight-2-circuit-composition
verified: 2026-08-06T00:00:00Z
status: passed
score: 4/4 must-haves verified
---

# Phase 11: CZ Insertion Unit & Weight-2 Circuit Composition Verification Report

**Phase Goal:** The full weight-2 generator circuit is implemented -- PBS -> heralded_cz -> PBS plus the two WP(pi/4,0) single-qubit corrections -- composed via Processor-level composition, reusing every existing weight-1 builder unmodified.
**Verified:** 2026-08-06
**Status:** passed
**Re-verification:** No -- initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | build_cz_insertion(n, i, j) implements PBS-wrap to heralded_cz to PBS-unwrap and its polarization-basis round-trip is verified against diag(1,1,1,-1) truth table at the (2i,2i+1)/(2j,2j+1) port convention | VERIFIED | iqp_photonic_encoding.py lines 152-207 implements the function exactly as described (local Circuit(6), PBS-wrap, PERM-adapted heralded_cz via _build_cz_insertion_core, PBS-unwrap, herald_spec read from HeraldedCzItem build_experiment in_heralds). Tests test_cz_insertion_returns_circuit_and_herald_spec, test_pbs_conversion_is_phase_neutral_for_computational_basis, test_cz_insertion_phase_sign_computational_basis (4 combos), test_cz_insertion_phase_sign_superposition all PASS -- confirms amplitude-squared equals 2/27 and sign negative only on the 11 basis state for all 4 computational-basis combos, plus superposition spot-checks (++ and +0). |
| 2 | The full weight-2 pipeline is composed via Processor.add(), reusing build_state_prep_circuit, build_conjugation_circuit, build_readout_circuit unmodified, with pi/4 corrections folded additively into build_diagonal_layer_circuit thetas argument | VERIFIED | build_weight2_processor (lines 210-293) calls proc.add(0, build_state_prep_circuit(n)), proc.add(0, build_diagonal_layer_circuit(n, thetas_folded)), proc.add(mapping, cz_circuit), proc.add(0, build_conjugation_circuit(n)), proc.add(0, build_readout_circuit(n)). None of the four weight-1 builder function bodies were touched (confirmed by reading the full file; only build_cz_insertion, _build_cz_insertion_core, build_weight2_processor are new additions). thetas_folded is a copy of thetas with indices i and j each incremented by pi/4 -- additive, non-mutating, passed straight into the unmodified build_diagonal_layer_circuit. test_weight1_builders_unitary_unchanged (sha256 snapshot on build_state_prep_circuit(2) unitary) PASSES, independently confirming zero drift in a shared builder. |
| 3 | The assembled processor heralds property is confirmed non-empty immediately after assembly (calibration check) | VERIFIED | Independently re-executed (not just SUMMARY claim) by this verifier: build_weight2_processor(3,0,1,[0,0,0]).heralds equals {6: 1, 7: 1} (equals {2n:1, 2n+1:1} for n=3), confirmed live. test_weight2_processor_heralds_nonempty asserts the exact dict, not just non-empty, and PASSES. add_herald calls read herald_spec[4]/herald_spec[5] from build_cz_insertion own returned dict, never hardcoded. |
| 4 | The existing 26-test weight-1 suite still passes unmodified (regression check) | VERIFIED | Full module suite pytest tests/test_iqp_photonic_encoding.py -v runs 36/36 passed (26 pre-existing weight-1 tests plus new cz_insertion tests from Plan 11-01 plus new weight2 tests from Plan 11-02). Full repo suite pytest -q runs 107/107 passed, zero failures, zero regressions -- run independently by this verifier, not taken from the SUMMARY. |

**Score:** 4/4 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| iqp_photonic_encoding.py::build_cz_insertion(n,i,j) | PBS-wrap to heralded_cz to PBS-unwrap, returns (Circuit(6), herald_spec) | VERIFIED | Exists (line 152), substantive (56-line docstring plus real implementation, no stub patterns), wired (imported/called by build_weight2_processor and by tests) |
| iqp_photonic_encoding.py::_build_cz_insertion_core() | PERM-adapted heralded_cz core, factored for Simulator testability | VERIFIED | Exists (line 113), substantive, wired (called by build_cz_insertion and directly by tests) |
| iqp_photonic_encoding.py::build_weight2_processor(n,i,j,thetas) | Full Processor(2n+2) weight-2 pipeline | VERIFIED | Exists (line 210), substantive, wired (called by tests; ready for Phase 12/13 consumption) |
| tests/test_iqp_photonic_encoding.py | Truth-table, sanity, herald, and regression tests | VERIFIED | 10 new test functions/parametrizations added across both plans, all pass, exercise real production code paths (not duplicated re-derivations) |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| build_cz_insertion PBS-wrap | heralded_cz bare 6-mode circuit | PERM([1,0]) adapter before/after | WIRED | Confirmed in source (lines 135-148) and by passing truth-table tests |
| build_cz_insertion | HeraldedCzItem build_experiment in_heralds | herald_spec read, not hardcoded | WIRED | Line 206; confirmed live: returns {4:1, 5:1} local, {6:1,7:1} global after mapping -- matches |
| build_weight2_processor | build_cz_insertion | Processor.add(mapping_dict, cz_circuit) | WIRED | Lines 276-282, mapping dict matches documented {2i:0, 2i+1:1, 2j:2, 2j+1:3, 2n:4, 2n+1:5} |
| build_weight2_processor | Processor.add_herald | immediate call after CZ add(), using herald_spec | WIRED | Lines 288-289; live-confirmed proc.heralds equals {6:1, 7:1} for n=3 |
| build_weight2_processor thetas | build_diagonal_layer_circuit | pi/4-folded copy | WIRED | Lines 266-268, 274; unmodified build_diagonal_layer_circuit receives thetas_folded |

### Requirements Coverage

| Requirement | Status | Blocking Issue |
|-------------|--------|-----------------|
| WT2-01 | SATISFIED | None -- all 4 supporting truths verified |

Note: REQUIREMENTS.md checkbox for WT2-01 is still unchecked -- this is a documentation-sync item, not a functional gap. Recommend the checkbox be ticked as part of phase close-out.

### Anti-Patterns Found

None. No TODO/FIXME/placeholder patterns, no stub returns, no empty handlers found in the new code (build_cz_insertion, _build_cz_insertion_core, build_weight2_processor). All new functions have real logic, real exports, and are exercised by passing tests against actual Perceval execution (not mocked).

### Human Verification Required

None. All success criteria are structurally and numerically verifiable via source inspection, live re-execution, and the automated test suite, which this verifier ran independently (not merely trusted from SUMMARY.md).

### Gaps Summary

No gaps. All 4 ROADMAP success criteria are met:
1. build_cz_insertion implemented and truth-table verified (computational basis plus superposition) -- confirmed by reading source and independently re-running the test suite.
2. Full weight-2 pipeline composed via Processor.add(), all four weight-1 builders (build_state_prep_circuit, build_diagonal_layer_circuit, build_conjugation_circuit, build_readout_circuit) confirmed byte-identical/unmodified (sha256 snapshot test plus direct source read), pi/4 folding additive and non-mutating.
3. proc.heralds confirmed non-empty and exactly correct ({2n:1, 2n+1:1}) immediately after assembly -- independently re-executed by this verifier, not merely trusted from the SUMMARY.
4. Full 107-test repo suite (including the pre-existing weight-1 suite) passes with zero regressions, independently re-run by this verifier.

The documented deviation (Processor.probs() crashing when add_herald is combined with a PBS-containing circuit -- a confirmed Perceval library limitation, independently reproduced by this verifier via a ValueError matmul shape mismatch inside PolarizationSimulator._prepare_input, size 12 versus 16) does not affect any of the 4 success criteria: it only affected a supplementary test measurement approach (herald-success sanity check), which was correctly adapted to a bare-processor plus manual-post-selection pattern that still validates the same invariant through the real production mode-mapping-dict wiring. The production function build_weight2_processor itself, including its add_herald calls and heralds property, works correctly -- independently confirmed by this verifier to produce the correct {6:1, 7:1} herald dict with no crash when only heralds is inspected. The crash only occurs if a caller subsequently calls probs() on the herald-registered, PBS-containing processor, which is correctly flagged as a concern to carry forward to Phase 12, not a defect in this phase deliverable.

---

*Verified: 2026-08-06*
*Verifier: Claude (gsd-verifier)*
