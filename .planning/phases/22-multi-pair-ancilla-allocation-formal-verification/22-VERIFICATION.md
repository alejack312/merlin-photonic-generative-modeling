---
phase: 22-multi-pair-ancilla-allocation-formal-verification
verified: 2026-08-21T00:00:00Z
status: passed
score: 6/6 must-haves verified
overrides_applied: 0
---

# Phase 22: Multi-Pair Ancilla Allocation — Formal Verification Report

**Phase Goal:** Symbolically verify a k-pair ancilla allocation scheme for multi-ZZ weight-2 IQP circuits before any of it is implemented. Deliberately scoped to verification only: no Python k-pair implementation, no multi-ZZ hardness re-run.
**Verified:** 2026-08-21
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Owner selected one allocation scheme from ≥2 candidates, rejection recorded, selection demonstrably the owner's | ✓ VERIFIED | `22-CONTEXT.md` D-02 records pooled/recycled selected over contiguous and interleaved, with reasons for each rejection, resolved live in discussion (not Claude's unilateral pick) |
| 2 | Forge model runs clean: non-collision `unsat`, non-vacuity `sat` | ✓ VERIFIED | `racket forge/pooled_ancilla_allocation.frg` — all 12 live `test expect` blocks (`nonVacuous`, `colouringExists`, `minimality`, `dataPortDisjoint`) pass at n=4,5,6 per `results/phase22_forge_run_log.md`, reproduced with verbatim Forge solver output (`#vars`, `#clauses`, `Solving (ms)`) |
| 3 | `n`/`k` bound and `Int` bitwidth justified in-model against largest computed value | ✓ VERIFIED | Model header states largest mode index `43` at n=8, `for 6 Int` would silently overflow `[-32,31]`, `for 7 Int` (`[-64,63]`) used; confirmed via `grep` — `for 7 Int` used in every live bound clause, `for 6 Int` appears only in explanatory comments |
| 4 | Brute-force baseline run and timed; phase states plainly whether Forge earned its place | ✓ VERIFIED | `pooled_allocation_baseline.py` (backtracking-DFS search) matches Forge's minimum K exactly at n=4/5/6 and additionally solves n=7/n=8 where Forge timed out; `results/phase22_forge_summary.md` states unsoftened: "A few hundred lines of backtracking Python reached the same minimum faster, and reached further, than Forge's SAT-backed exhaustive search" — Forge ~123,000x slower on the shared domain. Reproduced verbatim in `docs/iqp-photonic-encoding.md` |
| 5 | `docs/iqp-photonic-encoding.md` gains a section recording the scheme as a specification, stating no Python implements it, model is source of truth | ✓ VERIFIED | `## MPAIR: Pooled Multi-Pair Ancilla Allocation (Phase 22)` section present with `### No Python implements this — the direction of truth is inverted` subsection stating this explicitly and inverting Phase 16's drift-warning convention |
| 6 | MPAIR-07's physics gate resolved before any `.frg` exists, explicit verdict on deferred-post-selection ancilla reuse | ✓ VERIFIED | `mpair07_reuse_check.py` + `results/phase22_reuse_gate.md` (Plan 22-01, numeric evidence) and owner's `## Owner ruling` (GO, dated 2026-08-21) recorded in Plan 22-02, *before* `forge/pooled_ancilla_allocation.frg` was created (Plan 22-04, wave 3, after Plan 22-02's wave 1 gate) |

**Score:** 6/6 truths verified

### Honesty Checks (explicitly requested)

| Item | Expected | Verified |
|---|---|---|
| (a) Forge model only converged through n=6; n=7 timed out past D-04 ceiling | Recorded as a finding, not silently gapped | ✓ `results/phase22_forge_run_log.md` `## Bound outcome`: "D-03's n<=8 target bound was NOT reached... n=7 was attempted... exceeded D-04's hard 10-minute-per-n ceiling, killed at ~610s with zero blocks resolved; n=8 was not attempted." Reproduced in `docs/iqp-photonic-encoding.md`'s `### What was checked, and how` |
| (b) MPAIR-05 verdict: Forge's exhaustive search did NOT earn its place (Python ~123,000x faster, reached further) | Stated plainly and unsoftened in `results/phase22_forge_summary.md` and reproduced verbatim in docs | ✓ `results/phase22_forge_summary.md` `## What Forge alone contributed`: "Forge is roughly 123,000x slower, not faster... A few hundred lines of backtracking Python reached the same minimum faster, and reached further, than Forge's SAT-backed exhaustive search." Verbatim quote reproduced in `docs/iqp-photonic-encoding.md`'s `### What Forge alone added — stated honestly` |

Both honesty items independently re-run and confirmed live during this verification (`mpair07_reuse_check.py --probe n2` reproduces HARNESS-FAIL numbers exactly; `--probe n4` reproduces GO numbers exactly to the reported precision).

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `mpair07_reuse_check.py` | Pooled-vs-dedicated reuse harness | ✓ VERIFIED | Exists, defines `build_two_gate_processor`, `postselected_distribution`, `run_probe_n2`, `run_probe_n4`; re-run live, reproduces the exact numbers in the SUMMARY and results file |
| `forge/pooled_ancilla_allocation.frg` | Search-formulated Forge model | ✓ VERIFIED | Exists alongside untouched `forge/ancilla_mapping.frg`; six predicates present (`pairsAreKn`, `conflicts`, `blocksInRange`, `properColouring`, `ancillaDisjointFromDataPorts`, `genuinePooling`); 12 live + 2 commented-out (n=7) test blocks; `for 7 Int` used throughout live bounds |
| `pooled_allocation_baseline.py` | Greedy+backtracking colouring search, closed-form checker | ✓ VERIFIED | Defines `edges`, `conflicts`, `greedy_colouring`, `backtracking_min_colouring`, `round_robin_colour`, `check_round_robin`, `naive_subset_scan` per SUMMARY; not wired into `tests/` |
| `results/phase22_reuse_gate.md` | MPAIR-07 evidence + owner ruling | ✓ VERIFIED | All 6 required sections present; `## Owner ruling` heading present, dated, GO, verbatim owner quote |
| `results/phase22_allocation_invariant.md` | MPAIR-02 prose invariant | ✓ VERIFIED | All 8 required headings present plus `## Owner review (Plan 22-03)` (confirm-both) |
| `results/phase22_forge_run_log.md` | Per-n Forge solve timings | ✓ VERIFIED | `## Bound outcome` and `## Empirical bound-finding procedure` present; honest n=6-converged/n=7-timeout finding |
| `results/phase22_forge_summary.md` | Forge-vs-brute-force comparison, honest verdict | ✓ VERIFIED | All 6 required headings; unsoftened verdict; (a)-(d) criteria addressed by name; criterion-correction honesty note present |
| `docs/iqp-photonic-encoding.md` MPAIR section | Specification for future implementation | ✓ VERIFIED | `## MPAIR: Pooled Multi-Pair Ancilla Allocation (Phase 22)` with all 6 subsections plus `### Self-Explanation Checkpoint (Phase 22)`, inserted before `## Conclusion and Open Questions`; insertion-only diff pattern consistent with plan requirement |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| `mpair07_reuse_check.py` | `iqp_photonic_encoding.py` | import of `build_cp_insertion`/`exact_qubit_iqp_distribution` | ✓ WIRED | Confirmed by successful live execution |
| `results/phase22_reuse_gate.md` | `mpair07_reuse_check.py` | numbers traceable to named script run | ✓ WIRED | Re-ran script live; numbers match exactly |
| `results/phase22_allocation_invariant.md` | `results/phase22_reuse_gate.md` | scope-boundary citation | ✓ WIRED | `phase22_reuse_gate` token present |
| `forge/pooled_ancilla_allocation.frg` | `results/phase22_allocation_invariant.md`, `iqp_photonic_encoding.py`, `results/phase22_reuse_gate.md` | header citations | ✓ WIRED | All three tokens present in header |
| `results/phase22_forge_summary.md` | `results/phase22_forge_run_log.md` | timings quoted, not re-measured | ✓ WIRED | Verbatim Forge output block matches run log exactly |
| `pooled_allocation_baseline.py` | `results/phase22_allocation_invariant.md` | round-robin formula reimplemented | ✓ WIRED | `round_robin_colour` present, `check_round_robin` confirms `round_robin_proper=True` at all n |
| `docs/iqp-photonic-encoding.md` | `forge/pooled_ancilla_allocation.frg`, `results/phase22_forge_summary.md` | citations, verbatim verdict | ✓ WIRED | All tokens present; verdict sentence reproduced verbatim (confirmed by direct comparison) |

### Requirements Coverage

| Requirement | Source Plan | Status | Evidence |
|---|---|---|---|
| MPAIR-01 | 22-01/22-CONTEXT | ✓ SATISFIED | Complete in checklist + traceability table |
| MPAIR-02 | 22-02, 22-03 | ✓ SATISFIED | Complete; prose invariant + owner-confirmed mechanism |
| MPAIR-03 | 22-04 | ✓ SATISFIED | Complete; search-formulated model, existence+minimality at n=4/5/6 |
| MPAIR-04 | 22-04 | ✓ SATISFIED | Complete; strengthened `genuinePooling` non-vacuity guard |
| MPAIR-05 | 22-05 | ✓ SATISFIED | Complete; honest verdict, criterion-correction documented |
| MPAIR-06 | 22-06 | ✓ SATISFIED | Complete; specification section + self-explanation checkpoint |
| MPAIR-07 | 22-01, 22-02 | ✓ SATISFIED | Complete; owner GO ruling before any `.frg` written |

All 7 requirement IDs (MPAIR-01 through MPAIR-07) are marked Complete consistently in both the `.planning/REQUIREMENTS.md` checklist (lines 66-73) and the traceability table (lines 164-170). No orphaned requirements found. Summary/footer counts are self-consistent (51 total, 44 Complete, 7 Pending — all LIFE-01..07 for Phase 23).

### Anti-Patterns Found

None. No `TBD`/`FIXME`/`XXX` markers found in any phase-modified file. `pytest -q` reports 296 passed both before and after re-running all live scripts — no regressions introduced by this phase.

### Human Verification Required

None. This phase's checkpoints (owner GO/NO-GO ruling, owner mechanism-confirmation, self-explanation checkpoint) were already run live during execution and are recorded verbatim in the artifacts, which this verification confirmed by direct inspection (not by trusting SUMMARY claims) — the `## Owner ruling`, `## Owner review (Plan 22-03)`, and `### Self-Explanation Checkpoint (Phase 22)` sections all contain the owner's own words, attributed and dated, with Claude's drafted verdicts left visibly unedited alongside them for comparison.

### Gaps Summary

None. All 6 ROADMAP success criteria verified against live re-execution of the Forge model, the Python harness, and the baseline script — not against SUMMARY claims alone. Both deliberately-recorded deviations from the pure success-story shape (n=7 Forge timeout, MPAIR-05's negative verdict) are accurately and unsoftened in the canonical artifacts, matching the phase's own "do not soften a NO-GO"/"do not spin a negative result" discipline.

---

*Verified: 2026-08-21*
*Verifier: Claude (gsd-verifier)*
