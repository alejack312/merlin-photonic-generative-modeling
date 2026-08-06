---
phase: 13-weight-1-weight-2-composability-validation
verified: 2026-08-06T19:24:10Z
status: passed
score: 3/3 must-haves verified
---

# Phase 13: Weight-1 + Weight-2 Composability Validation Verification Report

**Phase Goal:** Weight-1 and weight-2 generator layers are confirmed to compose correctly within the same circuit, not just in isolation.
**Verified:** 2026-08-06T19:24:10Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | An n=3 mixed generator test (2 weight-1 terms + 1 weight-2 term in the same circuit) passes, confirming weight-1 and weight-2 layers compose correctly | VERIFIED | `test_wt2_composability_mixed_generators_n3` (tests/test_iqp_photonic_encoding.py:576-624), parametrized over 3 n=3 configs, each stacking a nonzero weight-1 theta on a weight-2 pair member (i or j) plus one on the bystander qubit. All 3 parametrized cases pass on independent re-run: primary TVD < 1e-6 against the extended exact reference, companion sanity TVD > 0.1 against the weight-1-only reference (confirms ZZ term is non-vacuous). |
| 2 | The test is added to `tests/test_iqp_photonic_encoding.py`, matching existing test conventions | VERIFIED | Appended after `test_wt2_tvd_gate_n3_bystander_qubit` (line 570) under a new `# Phase 13:` comment banner (line 573), matching the file's existing per-phase banner convention (lines 231, 268, 382, 502). Uses `@pytest.mark.parametrize`, `total_variation_distance`, `np.isclose`/`assert tvd <` patterns identical to the immediately preceding Phase 12 tests. Calls `exact_qubit_iqp_distribution` and `photonic_weight2_iqp_distribution`, both already imported at the top of the file (lines 31, 34). |
| 3 | The full test suite (weight-1's original 26 tests + all weight-2 tests added across Phases 10-13) is green after this addition | VERIFIED | Independently re-ran the full repo test suite (`pytest -q` from repo root, all 13 test files under `tests/`, per `pytest.ini`'s `testpaths = tests`): **118 passed, 0 failed**. Confirmed the pre-Phase-13 baseline independently by checking out the pre-commit version of the test file (commit `6874b83`, before `b5cb28a` added the new test) and re-running: **115 passed**. Delta is exactly +3, matching the 3 new parametrized cases added. `test_iqp_photonic_encoding.py` alone: 47 passed (44 pre-existing + 3 new), 0 failed. |

**Score:** 3/3 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `tests/test_iqp_photonic_encoding.py` | Contains `def test_wt2_composability_mixed_generators_n3` | VERIFIED | Exists at line 584, 41-line implementation with docstring, 3-config parametrize decorator, primary + companion assertions. Not a stub — full TVD computation and multiple substantive assertions per case. |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `test_wt2_composability_mixed_generators_n3` | `exact_qubit_iqp_distribution(n, thetas, pair_thetas={(i,j): pi/4})` | direct call | WIRED | Called at line 603 with both `thetas` and `pair_thetas` set (extended exact reference), and again at line 620 with `pair_thetas=None` (weight-1-only reference) for the companion sanity check. Function imported at line 31. |
| `test_wt2_composability_mixed_generators_n3` | `photonic_weight2_iqp_distribution(n, i, j, thetas)` | direct call | WIRED | Called at line 604, return values (`photonic_dist, residual, herald_failure_prob`) all consumed in subsequent assertions (residual near-zero, herald failure prob matches expected 25/27, TVD against both exact references). Function imported at line 34. |

### Requirements Coverage

| Requirement | Status | Blocking Issue |
|-------------|--------|-----------------|
| WT2-07 (n=3 mixed generator test, composability) | SATISFIED by code/tests | `.planning/REQUIREMENTS.md` line 21/64 still lists WT2-07 as `[ ]` Pending — this is a documentation bookkeeping gap, not a code gap. The SUMMARY explicitly notes this is left to the orchestrator/verifier to close out. Flagging for the orchestrator to update REQUIREMENTS.md; does not block phase goal achievement (the test itself passes and demonstrates the requirement). |

### Anti-Patterns Found

None. No TODO/FIXME/placeholder patterns, no stub returns, no console-log-only implementations in the new test code or its dependencies. `iqp_photonic_encoding.py` was not modified, consistent with the plan's explicit "pure test-addition phase" constraint — confirmed via `git status`/`git diff` scope (only `tests/test_iqp_photonic_encoding.py` touched by commit `b5cb28a`).

### Human Verification Required

None. This phase is fully verifiable programmatically — it is a pure numerical TVD-based test addition with no UI, no external services, and no behavior only observable by a human.

### Gaps Summary

No gaps. All three success criteria verified against actual, independently-executed test runs (not trusted from SUMMARY.md). The SUMMARY's claimed "115 to 118" test count was cross-checked against a real `git checkout` of the pre-commit file state and confirmed accurate, resolving what initially looked like a discrepancy against the plan's stated "26-test weight-1 suite" baseline (that figure refers only to the original weight-1-only subset within `test_iqp_photonic_encoding.py`, not the whole-repo count used for the 115→118 tracking in ROADMAP.md/STATE.md).

One minor non-blocking documentation item: `REQUIREMENTS.md` has not yet had WT2-07's checkbox marked complete — recommend the orchestrator update this as part of closing out the phase/milestone.

---

*Verified: 2026-08-06T19:24:10Z*
*Verifier: Claude (gsd-verifier)*
