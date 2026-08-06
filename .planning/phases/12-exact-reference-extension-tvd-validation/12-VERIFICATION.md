---
phase: 12-exact-reference-extension-tvd-validation
verified: 2026-08-06T17:05:54Z
status: passed
score: 4/4 must-haves verified
---

# Phase 12: Exact Reference Extension & TVD Validation Verification Report

Phase Goal: Weight-2 is validated to the same rigor bar weight-1 already cleared -- exact reference, herald-conditioned TVD comparison, explicit honest failure/residual reporting, no silently-discarded probability mass.
Verified: 2026-08-06T17:05:54Z
Status: passed
Re-verification: No -- initial verification

## Goal Achievement

### Observable Truths / Success Criteria

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | exact_qubit_iqp_distribution extended with Z_i.Z_j pair terms, reusing weight-1 bit-ordering/Z-eigenvalue convention | VERIFIED | iqp_photonic_encoding.py:544-599. Signature is exact_qubit_iqp_distribution(n, thetas, pair_thetas=None); pair term loop (lines 580-585) reuses the exact same bit_k convention already used for weight-1 (lines 577-579), just applied to both indices and multiplied. pair_thetas=None default preserves old behavior -- confirmed by live test run (test_exact_qubit_distribution_weight2_backward_compatible, both param sets PASSED). |
| 2 | Herald-conditioned photonic distribution reports herald-failure probability and out-of-subspace residual as two separate, never-merged, never-silently-renormalized numbers | VERIFIED | photonic_weight2_iqp_distribution (iqp_photonic_encoding.py:359-417) returns a 3-tuple (dist, residual, herald_failure_prob). Herald mismatches accumulate into herald_failure_prob (line 404); out-of-subspace decode failures accumulate into residual (line 408) -- separate accumulators, never combined. Renormalization (lines 412-415) divides dist and residual by herald_success_prob only -- herald_failure_prob itself is returned raw, not folded back in. Live re-execution: residual=0.0, herald_failure_prob=0.9259259259259256 -- visibly distinct values, confirmed by dedicated test test_wt2_herald_failure_and_residual_are_separate_numbers. |
| 3 | TVD test at n=2, theta=pi/4 passes, exact reference vs herald-conditioned photonic distribution, TVD < 1e-6 (same style as test_enc04_toy_validation_runs_end_to_end) | VERIFIED | tests/test_iqp_photonic_encoding.py:507-527, test_wt2_tvd_gate_n2_theta_pi_4. Live re-run (independent of pytest, direct script execution against committed code) gives TVD = 2.581268532253489e-15, well under 1e-6. Matches results/phase12_weight2_tvd_validation_summary.md recorded numbers exactly, and matches test_enc04 style (explicit docstring stating the claim, total_variation_distance helper, explicit < 1e-6 assertion with failure message). |
| 4 | New test coverage added for WT2-01 through WT2-05, matching existing conventions; full suite (26 + new) passes | VERIFIED (see labeling note below) | 8 new WT2-tagged tests added to tests/test_iqp_photonic_encoding.py: test_exact_qubit_distribution_weight2_backward_compatible (x2 params), test_exact_qubit_distribution_weight2_extension_sums_to_one (x3 params), test_wt2_tvd_gate_n2_theta_pi_4, test_wt2_herald_failure_and_residual_are_separate_numbers, test_wt2_tvd_gate_n3_bystander_qubit (opportunistic n=3). Full suite independently re-run with venv/Scripts/python.exe -m pytest tests/ -v: 115 passed, 0 failed (pre-existing weight-1/infra suite grew from 26 to 107 across Phases 9-11; Phase 12 adds 8 more, total 115). Zero regressions. |

Note on criterion 4 wording: the ROADMAP text says WT2-01 through WT2-05 but Phase 12 own REQUIREMENTS mapping (confirmed in both PLAN files frontmatter) is WT2-02, WT2-03, WT2-05, WT2-06 -- WT2-01 and WT2-04 belong to earlier phases (state prep / heralded-CZ de-risking, Phase 10-11). The actual test coverage added matches the phase real requirement set (WT2-02/03/05/06), which is what the plan frontmatter and CONTEXT.md lock, not the ROADMAP possibly-imprecise range shorthand. This is a labeling discrepancy in the ROADMAP text, not a gap in delivered coverage.

Score: 4/4 criteria verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| iqp_photonic_encoding.py::exact_qubit_iqp_distribution | (n, thetas, pair_thetas=None), backward compatible | VERIFIED | Exists, substantive (56 lines incl. docstring), wired into tests and into photonic_weight2_iqp_distribution validation test. |
| iqp_photonic_encoding.py::_build_weight2_processor_no_herald | Herald-unregistered sibling of build_weight2_processor, reusing its wiring | VERIFIED | Exists (lines 296-335); wiring is a literal copy of build_weight2_processor minus the two add_herald calls (confirmed by direct line-by-line comparison -- same mapping dict, same builder calls). Used by photonic_weight2_iqp_distribution. |
| iqp_photonic_encoding.py::_weight2_input_state | P:V-annotated ancilla input | VERIFIED | Exists (lines 338-356); explicitly builds P:V annotation strings for the ancilla ports (lines 354-355), not bare integers or P:H -- matches the plan load-bearing fix. |
| iqp_photonic_encoding.py::photonic_weight2_iqp_distribution | Returns 3-tuple (dist, residual, herald_failure_prob) | VERIFIED | Exists (lines 359-417), wired (imported/used by 3 tests), confirmed live to return correct 3-tuple with expected values. |
| tests/test_iqp_photonic_encoding.py | WT2-02/03/05/06 coverage | VERIFIED | 8 new tests present and passing, wired into the module under test. |
| results/phase12_weight2_tvd_validation_summary.md (Plan 12-02) | Numbers-only write-up, phase7 format | VERIFIED | Exists; recorded TVD/residual/herald numbers match this verification independent live re-run exactly (TVD=2.581268532253489e-15, herald_failure_prob=0.9259259259259256, residual=0.0); ends with unwritten Interpretation placeholder as locked by CONTEXT.md. |
| Upstream Perceval bug report | Filed or drafted | VERIFIED | Live, open GitHub issue confirmed via gh api repos/Quandela/Perceval/issues/783 -- title, body, and repro description match 12-RESEARCH.md Pitfall 3 characterization; filed by the project owner account on 2026-08-06. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| photonic_weight2_iqp_distribution | _build_weight2_processor_no_herald | direct call | WIRED | Line 389: proc, herald_spec = _build_weight2_processor_no_herald(n, i, j, thetas). |
| _weight2_input_state | herald ancilla photons | P:V annotation | WIRED | Lines 354-355, confirmed non-P:H/non-bare-integer as required. |
| test_wt2_tvd_gate_n2_theta_pi_4 | exact_qubit_iqp_distribution vs photonic_weight2_iqp_distribution | total_variation_distance | WIRED | Lines 517-527; live re-execution reproduces TVD=2.58e-15, matching both the test assertion and the results write-up. |

### Requirements Coverage

| Requirement | Status | Blocking Issue |
|-------------|--------|-----------------|
| WT2-02 (exact reference extension) | SATISFIED | None |
| WT2-03 (herald-conditioned photonic measurement path) | SATISFIED | None |
| WT2-05 (locked TVD gate) | SATISFIED | None |
| WT2-06 (herald-accounting separation) | SATISFIED | None |

### Anti-Patterns Found

None. No TODO/FIXME/placeholder/stub patterns found in the new code (_build_weight2_processor_no_herald, _weight2_input_state, photonic_weight2_iqp_distribution, extended exact_qubit_iqp_distribution). No empty returns, no hardcoded fake outputs.

### Human Verification Required

None. All success criteria are mechanically checkable (test suite pass/fail, TVD numeric threshold, tuple-arity/value inspection) and were independently re-executed against the actual committed codebase, not just read from SUMMARY.md claims.

### Gaps Summary

No gaps. All 4 ROADMAP success criteria for Phase 12 are verified against live re-execution of the actual code (not SUMMARY.md claims):
- exact_qubit_iqp_distribution extension confirmed via source read + live test run.
- Herald-failure/residual separation confirmed via source read + live direct execution (residual=0.0, herald_failure_prob=0.9259..., distinct values).
- TVD gate at n=2, theta=pi/4 independently re-run outside pytest: TVD=2.58e-15, well under the 1e-6 bar.
- Full test suite independently re-run: 115/115 passing, zero regressions from the pre-existing 107 tests.
- Bonus: the results write-up numbers were cross-checked against this verification independent live re-run and match exactly; the upstream Perceval GitHub issue (#783) was confirmed to actually exist via the GitHub API, not just trusted from the SUMMARY.
- One minor labeling discrepancy noted (ROADMAP says WT2-01 through WT2-05, actual phase requirement set per PLAN frontmatter is WT2-02/03/05/06) -- not a coverage gap, just an imprecise range reference in the ROADMAP text.

---

Verified: 2026-08-06T17:05:54Z
Verifier: Claude (gsd-verifier)
