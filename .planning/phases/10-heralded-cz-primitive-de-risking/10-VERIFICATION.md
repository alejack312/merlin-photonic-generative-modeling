---
phase: 10-heralded-cz-primitive-de-risking
verified: 2026-08-06T07:44:23Z
status: passed
score: 4/4 must-haves verified
---

# Phase 10: Heralded-CZ Primitive De-Risking Verification Report

**Phase Goal:** `heralded_cz`'s actual measured behavior (not literature assumptions) is confirmed for this specific Perceval implementation, before any integration work begins.
**Verified:** 2026-08-06T07:44:23Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Herald-success probability measured via `build_experiment()` + `Processor.probs()`, read from `global_perf`/`physical_perf`/`logical_perf` (not shot-sampled) | VERIFIED | `heralded_cz_derisking.py:64-72` (`build_heralded_cz_processor` calls `item.build_experiment()`, never `build_circuit()`, wraps in `Processor("SLOS", exp)`, calls `compute_physical_logical_perf(True)`); ran `venv/Scripts/python.exe heralded_cz_derisking.py` — printed `global_perf=0.0740740741, physical_perf=1.0000000000, logical_perf=0.0740740741` for all 4 inputs, exact 2/27 to 1e-9 |
| 2 | Success probability uniform across all 4 computational-basis dual-rail inputs | VERIFIED | Live run confirms identical `global_perf`=2/27 for `(0,0)`,`(0,1)`,`(1,0)`,`(1,1)`; script prints "Computational-basis uniformity check: PASS"; `pytest tests/test_heralded_cz_derisking.py::test_herald_success_uniform_computational_basis` — 4/4 parametrized cases PASSED. Also exceeds requirement with 2 superposition spot-checks (`|+>|+>`, `|+>|0>`), both PASS |
| 3 | CZ truth table/phase behavior verified against computational-basis inputs | VERIFIED | `measure_cz_phase()` uses `Simulator(SLOSBackend())` on the bare `build_circuit()` output (Processor.probs() is phase-blind), reads herald ancilla counts from `in_heralds` (not hardcoded); live run: amplitudes ≈ `+0.2722` for `(0,0)`,`(0,1)`,`(1,0)` and `-0.2722` for `(1,1)`, matching `diag(1,1,1,-1)`; `|amplitude|^2` = 2/27 in all 4 cases; script prints "Phase sign check: PASS"; also cross-verified via `Analyzer` truth table (zero leakage to invalid/bunched outputs) and `post_select_fn` emptiness (logical_perf is pure herald condition, no hidden filter) |
| 4 | Literature-comparison note documents measured value alongside design doc's previously-flagged literature figures, descriptive only, no equality claimed | VERIFIED | `docs/iqp-photonic-encoding.md` lines 104, 216, 381 all updated: state confirmed 2/27 measurement + phase sign, explicitly frame it as "an observation about this specific gate, not a claim that this implementation is the same construction as the literature's general gate family" — no equality asserted |

**Score:** 4/4 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `heralded_cz_derisking.py` | Herald-success + phase-amplitude functions, main() PASS/FAIL report | VERIFIED | 288 lines (≥80 min); exports `build_heralded_cz_processor`, `measure_herald_success`, `measure_herald_success_superposition`, `build_analyzer`, `check_no_leakage`, `check_post_select_fn_empty`, `measure_cz_phase`, `check_phase_sign`, `main()`; executed standalone, exit 0, all checks print PASS |
| `tests/test_heralded_cz_derisking.py` | Pytest regression coverage | VERIFIED | 91 lines (≥30 min); imports functions directly from `heralded_cz_derisking` (not `import *`); 12 test cases; `pytest tests/test_heralded_cz_derisking.py -v` → 12 passed in 11.88s |
| `docs/iqp-photonic-encoding.md` | Updated Ingredient 2 / Open Questions / Conclusion sections | VERIFIED | All 3 named sections (lines ~104, ~216, ~381) updated with confirmed 2/27 figure, phase sign, and Phase 10 citation; descriptive framing preserved |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `heralded_cz_derisking.py` (probability path) | `HeraldedCzItem` | `build_experiment()` | WIRED | Line 69: `exp = item.build_experiment()  # NOT build_circuit() -- that drops the heralds`; confirmed correct — `build_circuit()` is deliberately used only in the separate phase path (line 176) where the bare circuit is required for `Simulator` |
| `heralded_cz_derisking.py` (phase path) | `HeraldedCzItem` | `build_circuit()` + `Simulator.prob_amplitude` | WIRED | Lines 175-192: `Simulator(SLOSBackend())` set on bare circuit, herald counts read from `build_experiment().in_heralds` (not hardcoded) |
| `tests/test_heralded_cz_derisking.py` | `heralded_cz_derisking.py` | direct function imports | WIRED | Lines 9-21: explicit named imports; import succeeds, all 12 tests collect and pass |

### Requirements Coverage

Not applicable — no REQUIREMENTS.md phase mapping found for this internal de-risking phase; success criteria are the plan's stated must-haves, all verified above.

### Regression Check

`pytest tests/test_iqp_photonic_encoding.py tests/test_perceval_fluency_demo.py -v` — 32 passed in 11.01s. No regressions from Phase 10's changes.

### Anti-Patterns Found

None. No TODO/FIXME/placeholder patterns, no empty returns, no stub handlers in `heralded_cz_derisking.py` or `tests/test_heralded_cz_derisking.py`. All functions have substantive implementations, all assertions are live (not hardcoded to always pass), and live execution reproduces the exact numeric claims made in the code comments and docs.

### Human Verification Required

None. All success criteria are structurally and numerically verifiable via direct script execution and doc inspection, both of which were performed live in this verification (not inferred from SUMMARY.md).

### Gaps Summary

No gaps. All 4 success criteria hold against live execution:
1. Analytic (non-shot-sampled) herald-success probability read from `global_perf`/`physical_perf`/`logical_perf` via `build_experiment()` + `Processor.probs()`.
2. Confirmed uniform (2/27, to 1e-9) across all 4 computational-basis dual-rail inputs (plus 2 superposition spot-checks beyond the stated minimum).
3. CZ truth table/phase confirmed via `Simulator.prob_amplitude` on the bare circuit — correct sign flip on `|1,1>`, matching `diag(1,1,1,-1)`.
4. Literature-comparison note added in 3 places in `docs/iqp-photonic-encoding.md`, framed descriptively with no equality claim.

One historical, dated transcript passage (line 184, "Self-Explanation Checkpoint" record from Phase 9) still contains the older "not independently recomputed... assumed, not verified" phrasing — this is explicitly preserved as an accurate historical record of a past Q&A exchange (the doc states so at line 177: "left as an accurate record of what was actually said"), not a current-state claim, and was not one of the 3 sections the plan scoped for update (Ingredient 2 ~104, Open Questions ~216, Conclusion ~381, all of which are correctly current). Not a gap.

---

*Verified: 2026-08-06T07:44:23Z*
*Verifier: Claude (gsd-verifier)*
