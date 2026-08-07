---
phase: 15-arb-01-core-gate-de-risking-validation
verified: 2026-08-07T16:16:05Z
status: passed
score: 5/5 must-haves verified
---

# Phase 15: ARB-01 Core Gate De-Risking & Validation Verification Report

**Phase Goal:** Validate PostProcessedControlledRotationsItem (the continuously-tunable two-qubit diagonal phase gate) to the same rigor bar heralded_cz cleared in v2.1 -- de-risk it standalone, derive the general-alpha operator identity, and confirm it via TVD against the extended exact qubit-side reference.
**Verified:** 2026-08-07T16:16:05Z
**Status:** passed
**Re-verification:** No -- initial verification

## Goal Achievement

### Observable Truths / Success Criteria

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | Gate phase/structure confirmed at >=3 non-trivial alpha values via Simulator.prob_amplitude, matching the operator identity prediction | VERIFIED | cp_gate_derisking.py independently re-run live: prints phase/magnitude table at alpha=pi/6, pi/3, 2pi/5, pi; every row PASS for phase(amp)==e^(i*alpha) and uniformity. Bare-core level (_build_cp_insertion_core, iqp_photonic_encoding.py:213) independently confirmed via live pytest re-run: test_cp_insertion_core_matches_diag_1_1_1_ealpha at all 4 alpha, test_cp_insertion_core_boundary_matches_cz_insertion_core_sign_for_sign -- all pass, matching diag(1,1,1,e^(i*alpha)) on MODULE_DUAL_RAIL. |
| 2 | General-alpha operator identity (CP(alpha) mapped to exp(i*theta*Z_i*Z_j)) derived and written down, extending the existing fixed-pi/4 derivation | VERIFIED | docs/iqp-photonic-encoding.md lines 375-434 (new ARB-01/ARB-02 section, added alongside -- not replacing -- the existing Ingredient 2 fixed-pi/4 derivation, confirmed intact by reading the file). Full step-by-step algebra present (lines 391-402); independently re-derived by hand during this verification (multiplying exp(i*theta*Z_i)*exp(i*theta*Z_j) by CP(4*theta) and the global phase e^(-i*theta) reproduces diag(e^(i*theta),e^(-i*theta),e^(-i*theta),e^(i*theta)) exactly) -- the doc's claimed identity is algebraically correct, not just asserted. alpha=4*theta relationship stated unambiguously (line 397, 402), correcting 15-CONTEXT.md's originally-stated alpha=pi/4 to the verified alpha=pi. Owner's attempt-first Q&A transcript present (lines 379-389), matching this document's ENC-01/ENC-05 convention of recording wrong turns. |
| 3 | TVD validation against the extended exact qubit-side reference passes at >=1 representative non-special alpha, <=1e-6 | VERIFIED | Independently re-executed outside pytest (not just trusting the test suite): photonic_cp_iqp_distribution vs. exact_qubit_iqp_distribution at n=2, pair (0,1), thetas=[0.3,1.1], for all 3 non-trivial alpha: TVD = 4.1e-16, 5.1e-16, 1.9e-15 -- all roughly 10 orders of magnitude below the 1e-6 bar. Boundary (alpha=pi) TVD against heralded_cz's already-validated output = 2.7e-15. n=3 bystander-qubit configuration also independently re-run via pytest (test_cp_pipeline_tvd_gate_n3_bystander_qubit, 3/3 alpha PASSED). |
| 4 | Success probability reported as an explicit table/curve as a function of alpha, never collapsed to a single number | VERIFIED | Bare-gate level: cp_gate_derisking.py's printed table (4 rows, distinct alpha/amplitude-squared/phase columns). Pipeline level: docs/iqp-photonic-encoding.md lines 420-432 (7-point closed-form-vs-measured table) and lines 459-463 (measured TVD/residual table by configuration); test_cp_pipeline_success_probability_vs_alpha_table explicitly asserts at least 2 distinct success-probability values across the tested alpha set, not a constant. Independently confirmed non-monotonicity live: success probs 0.174539 / 0.111111 / 0.100142 / 0.111111 at pi/6, pi/3, 2pi/5, pi (dips then rises -- genuine alpha-dependence, not a coincidental duplicate-row bug; confirmed via closed-form cross-check p_success=1/sigma_max^4). |
| 5 | Written comparison against heralded_cz (mechanism stated plainly) plus new test coverage added to tests/test_iqp_photonic_encoding.py, passing | VERIFIED | docs/iqp-photonic-encoding.md lines 436-449: side-by-side table (mechanism, tunability, ancilla/resource cost, circuit depth, success probability at boundary and in general) -- purely descriptive, no "which to use" recommendation language (grep confirms no recommend/should-use/prefer language in the section). Circuit-depth figures independently re-verified live: build_cz_insertion = 21 components/depth 12, build_cp_insertion = 9 components/depth 5 -- exact match to the doc's stated numbers. 22 CP-related tests across tests/test_cp_gate_derisking.py and tests/test_iqp_photonic_encoding.py independently re-run: all pass. Full repo suite (142 tests) independently re-run: 142/142 pass, zero regressions. |

**Score:** 5/5 criteria verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| cp_gate_derisking.py | Bare-gate CP(alpha) phase/structure confirmation script | VERIFIED | Exists (214 lines), substantive, no stub patterns, live-re-executed with exit 0 and all PASS printed. |
| tests/test_cp_gate_derisking.py | Pytest regression coverage | VERIFIED | Exists (62 lines), 8 tests, all live-re-run PASSED. |
| iqp_photonic_encoding.py::_build_cp_insertion_core | Bare-core PERM-adapted CP(alpha), matches MODULE_DUAL_RAIL | VERIFIED | Exists (line 213), substantive docstring plus implementation, wired into build_cp_insertion and 6 tests, live-confirmed to match diag(1,1,1,e^(i*alpha)). |
| iqp_photonic_encoding.py::build_cp_insertion | PBS-wrapped Circuit(8) plus ancilla_spec, build_cz_insertion's external-contract pattern | VERIFIED | Exists (line 281), wired into the full pipeline builder, ancilla_spec read live from PostProcessedControlledRotationsItem().build_experiment().in_heralds (not hardcoded, confirmed by source read). |
| iqp_photonic_encoding.py::photonic_cp_iqp_distribution | Full-pipeline CP(alpha) measurement, TVD-validated | VERIFIED | Exists (line 671), substantive (returns 3-tuple dist, residual, postselect_failure_prob), live-confirmed to reproduce TVD under 1e-6 (actually ~1e-15/1e-16) at all tested configurations. |
| docs/iqp-photonic-encoding.md | General-alpha derivation plus comparison table | VERIFIED | New ARB-01/ARB-02 section (105 lines, 375-479), existing fixed-pi/4 section confirmed unmodified/intact by direct read. |
| tests/test_iqp_photonic_encoding.py | CP truth-table, TVD, boundary-agreement, success-probability-table tests | VERIFIED | 14 new CP-specific test functions/parametrizations added across Plans 15-02/15-04, all live-re-run PASSED. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| cp_gate_derisking.py | PostProcessedControlledRotationsItem.build_circuit | direct call, bare circuit | WIRED | Confirmed by source read plus live execution producing correct amplitudes. |
| _build_cp_insertion_core | PostProcessedControlledRotationsItem.build_circuit | PERM([1,0])-wrapped | WIRED | Confirmed by source read (lines 262-278) plus live Simulator.prob_amplitude re-execution matching target truth table. |
| build_cp_insertion | _build_cp_insertion_core | PBS-wrap then core then PBS-unwrap | WIRED | Confirmed by source read (lines 333-338). |
| photonic_cp_iqp_distribution | build_cp_insertion | Processor.add(mapping, cp_circuit), 4-entry ancilla mapping | WIRED | Confirmed by source read (lines 610-617) -- mapping dict has exactly 4 ancilla entries (2n..2n+3 to local 4-7), matching the plan's structural-warning fix; live-confirmed correct via TVD results. |
| photonic_cp_iqp_distribution | exact_qubit_iqp_distribution | pair_thetas={(i,j): alpha/4} | WIRED | Confirmed live: TVD at floating-point noise across all tested alpha and both n=2,3. |
| docs/iqp-photonic-encoding.md's derivation | actual code behavior | algebraic identity plus numeric cross-check table | WIRED | Independently re-derived by hand (see criterion 2) and cross-checked against cp_gate_derisking.py's live output -- not merely asserted in prose. |

### Requirements Coverage

| Requirement | Status | Blocking Issue |
|-------------|--------|-----------------|
| ARB-01 (gate phase/structure confirmed >=3 non-trivial alpha) | SATISFIED | None |
| ARB-02 (general-alpha operator identity derived and written) | SATISFIED | None |
| ARB-03 (TVD validation, >=1 representative non-special alpha, <=1e-6) | SATISFIED | None (exceeded: all 3 non-trivial alpha, n=2 and n=3, TVD ~1e-15/1e-16) |
| ARB-04 (success probability as explicit function of alpha) | SATISFIED | None |
| ARB-05 (written comparison to heralded_cz, mechanism stated plainly) | SATISFIED | None |
| ARB-06 (new test coverage matching existing conventions) | SATISFIED | None |

Note: .planning/REQUIREMENTS.md's checkboxes for ARB-01 through ARB-06 are still shown unchecked and the requirements-to-phase table still says "Pending" as of this verification -- this is a bookkeeping/status-tracking artifact outside this phase's own deliverables (not part of any must_haves artifact list for Plans 15-01 through 15-04), not a gap in the phase's actual deliverables. Flagged for the orchestrator to update REQUIREMENTS.md's status tracking, not a phase-goal failure.

### Anti-Patterns Found

None blocking. A pre-existing module-header comment ("Not implemented here: building and testing the actual heralded ancilla/herald-detection circuit is out of scope for this plan's runnable code", iqp_photonic_encoding.py:65) predates Phase 15 (part of the original weight-1-only scope note from Phase 9) and does not describe any Phase-15 CP code -- not a stub in this phase's deliverables. No TODO/FIXME/placeholder patterns found in any of the 4 Phase 15 plans' actual code artifacts (cp_gate_derisking.py, _build_cp_insertion_core, build_cp_insertion, _build_weight2_cp_processor_no_postselect, _weight2_cp_input_state, _decode_single_qubit_pair, photonic_cp_iqp_distribution).

### Human Verification Required

None. All 5 ROADMAP success criteria are mechanically checkable (Simulator.prob_amplitude phase/magnitude checks, algebraic identity, TVD numeric threshold, table-based success-probability reporting, descriptive-comparison-table presence) and were independently re-executed against the actual committed codebase during this verification pass -- not merely read from SUMMARY.md claims. Independent re-derivation of the general-alpha operator identity by hand (criterion 2) and independent re-computation of circuit-depth figures (criterion 5) both matched the document's claims exactly.

### Gaps Summary

No gaps. All 5 ROADMAP success criteria for Phase 15 are verified against live re-execution of the actual code, not SUMMARY.md claims:
- cp_gate_derisking.py re-run live: all PASS, matches the phase/structure claim at 3 non-trivial alpha plus the alpha=pi boundary.
- The general-alpha operator identity was independently re-derived by hand during this verification and found algebraically correct (not just trusted from the doc's prose).
- TVD independently re-computed outside pytest at all 3 non-trivial alpha (n=2) plus n=3 bystander configuration plus the alpha=pi boundary: all ~1e-15/1e-16, far below the 1e-6 bar.
- Success-probability non-monotonicity (pi/6 to pi/3 to 2pi/5 to pi: 0.1745 to 0.1111 to 0.1001 to 0.1111) independently reproduced live, confirmed against the closed-form p_success(alpha)=1/sigma_max^4 formula, not a table-printing artifact.
- The heralded_cz-vs-CP(alpha) comparison table's circuit-depth figures (21/12 vs. 9/5) independently re-computed live via Circuit.ncomponents()/.depths() and matched exactly.
- Full test suite (142 tests, including 22 CP-specific tests) independently re-run: 142/142 pass, zero regressions.
- One informational note: .planning/REQUIREMENTS.md's ARB-01 through ARB-06 checkboxes/status table are stale (still "Pending"/unchecked) relative to this phase's actual completed work -- a status-tracking bookkeeping item, not a phase deliverable gap.

---

Verified: 2026-08-07T16:16:05Z
Verifier: Claude (gsd-verifier)
