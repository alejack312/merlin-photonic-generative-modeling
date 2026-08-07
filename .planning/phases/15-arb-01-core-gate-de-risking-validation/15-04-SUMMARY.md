---
phase: 15-arb-01-core-gate-de-risking-validation
plan: 04
subsystem: quantum-photonic-encoding
tags: [perceval, linear-optics, iqp, cp-gate, tvd-validation, post-selection]

# Dependency graph
requires:
  - phase: 15-02
    provides: "build_cp_insertion(n, i, j, alpha) / _build_cp_insertion_core(alpha) -- the PERM-adapted CP(alpha) bare-core and PBS-wrapped insertion unit, confirmed to reproduce diag(1,1,1,e^{i*alpha}) exactly"
  - phase: 15-03
    provides: "the general-alpha operator identity (alpha=4*theta) and closed-form success probability p_success(alpha)=1/sigma_max^(2n), documented in docs/iqp-photonic-encoding.md's ARB-01/ARB-02 section"
provides:
  - "photonic_cp_iqp_distribution(n, i, j, thetas, alpha) -- full-pipeline CP(alpha) weight-2 measurement, TVD-validated against the exact reference"
  - "_build_weight2_cp_processor_no_postselect / _weight2_cp_input_state / _decode_single_qubit_pair -- CP-specific pipeline builders mirroring the heralded_cz manual-filtering pattern"
  - "heralded_cz-vs-CP(alpha) descriptive comparison table in docs/iqp-photonic-encoding.md"
affects: [16-arb-01-extended-validation-postselection-bookkeeping]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Manual post-selection filtering (no add_herald/set_postselection) for any gate whose Perceval-registered condition needs to compose with later pipeline components -- Pitfall 3 pattern, now used for both heralded_cz and CP(alpha)."
    - "Per-qubit-pair post-selection failure must be attributed to the gate's OWN postselect_failure_prob, not to a generic residual bucket, whenever the failure condition covers modes the gate itself acts on (verified via the photon-number-preservation argument in this plan's SUMMARY/docs)."

key-files:
  created: []
  modified:
    - iqp_photonic_encoding.py
    - tests/test_iqp_photonic_encoding.py
    - docs/iqp-photonic-encoding.md

key-decisions:
  - "postselect_failure_prob must include BOTH ancilla-nonzero AND qubit-i/j-pair data invalidity, not just ancilla-nonzero -- residual is reserved for genuinely unrelated bystander-qubit leakage only. Found necessary during Task 1's own smoke-test verification (the literal plan recipe gave TVD~0.375, matching 15-RESEARCH.md's flagged unresolved TVD~0.3-0.4 finding); the corrected accounting reproduces the closed-form success probability to ~1e-15 and drives TVD to floating-point noise."
  - "Outer processor sized 2n+4 (not 2n+2) with a 4-entry ancilla mode-mapping dict, per the plan's structural warning -- build_cp_insertion has 4 ancilla modes (build_cp_insertion's own local 4-7), not build_cz_insertion's 2."
  - "Ancilla input state uses plain bare '0' entries (not '{P:V}'-annotated), confirmed empirically before the full TVD sweep -- CP's ancilla_spec expects vacuum (photon count 0) at every ancilla mode, unlike heralded_cz's herald ancilla which needs a real annotated photon."

# Metrics
duration: ~55min
completed: 2026-08-07
---

# Phase 15 Plan 04: Full-Pipeline CP(alpha) Wiring & TVD Validation Summary

**Wired `build_cp_insertion` into the complete weight-2 IQP pipeline as `photonic_cp_iqp_distribution`, found and fixed a postselection-accounting bug that was the root cause of `15-RESEARCH.md`'s previously-unresolved TVD~0.3-0.4 finding, and validated the corrected pipeline to floating-point-noise-level TVD against the exact reference at n=2,3 across 3 non-trivial α values plus the α=π boundary against `heralded_cz`.**

## Performance

- **Duration:** ~55 min
- **Completed:** 2026-08-07
- **Tasks:** 3/3 completed
- **Files modified:** 3 (`iqp_photonic_encoding.py`, `tests/test_iqp_photonic_encoding.py`, `docs/iqp-photonic-encoding.md`)

## Accomplishments

- `photonic_cp_iqp_distribution(n, i, j, thetas, alpha)` and its supporting builders (`_build_weight2_cp_processor_no_postselect`, `_weight2_cp_input_state`, `_decode_single_qubit_pair`) implemented, mirroring `photonic_weight2_iqp_distribution`'s manual-filtering pattern for a gate whose Perceval-registered postselection cannot compose with the later conjugation/readout components (Pitfall 3).
- Diagnosed and fixed a genuine accounting bug (not a wiring/convention bug): the literal plan recipe's `postselect_failure_prob`/`residual` split reproduced `15-RESEARCH.md`'s own unresolved TVD~0.3-0.4 finding exactly. Root cause: qubit i's/j's own pair-validity failure is part of CP's *own* internal post-selection condition (ancilla vacuum AND `[0,1]==1 & [2,3]==1`), and must be reported as failure, not residual, since every downstream component (`PBS`, `HWP`) is per-pair photon-number-preserving.
- TVD validated at floating-point-noise level (`~1e-16`-`1e-15`) against the extended exact reference at n=2 (pair `(0,1)`) and n=3 (pair `(1,2)`, bystander qubit at nonzero θ), across all 3 non-trivial α values (`π/6`, `π/3`, `2π/5`) — well under the locked `<1e-6` bar.
- Direct full-pipeline boundary-agreement confirmed at α=π: `photonic_cp_iqp_distribution`'s output matches `photonic_weight2_iqp_distribution`'s already-validated `heralded_cz`-based output to TVD~3e-15 — the missing third confirmation level (bare-gate and bare-core were already confirmed in Plans 15-01/15-02).
- Success-probability-vs-α reported as an explicit table (never a single number), matching the closed-form `p_success(α)=1/σ_max^4` (n=2) to ~1e-6.
- `docs/iqp-photonic-encoding.md`'s comparison table extended with ancilla/resource cost and measured circuit-depth rows (CP: 4 ancilla/vacuum, 9 components, max depth 5; `heralded_cz`: 2 ancilla/heralded photon, 21 components, max depth 12) — purely descriptive, no recommendation, per locked scope. Open Questions/Conclusion sections updated to reflect weight-2 is no longer fixed-π/4-only.

## Task Commits

Each task was committed atomically:

1. **Task 1: Full pipeline wiring + manual-filtering measurement function** - `de6bdb6` (feat)
2. **Task 2: TVD validation, boundary-agreement test, success-probability-vs-α table** - `869c364` (test)
3. **Task 3: heralded_cz-vs-CP comparison table + doc finalization** - `771665b` (docs)

## Files Created/Modified

- `iqp_photonic_encoding.py` — `_build_weight2_cp_processor_no_postselect`, `_weight2_cp_input_state`, `_decode_single_qubit_pair`, `photonic_cp_iqp_distribution` added (237 insertions).
- `tests/test_iqp_photonic_encoding.py` — `test_cp_pipeline_tvd_gate_n2`, `test_cp_pipeline_tvd_gate_n3_bystander_qubit`, `test_cp_pipeline_boundary_agreement_matches_heralded_cz`, `test_cp_pipeline_success_probability_vs_alpha_table` added (122 insertions).
- `docs/iqp-photonic-encoding.md` — comparison table extended (ancilla/resource cost, circuit depth rows), new "Full-Pipeline Validation (Plan 15-04)" subsection, Open Questions/Conclusion sections updated.

## Decisions Made

- **`postselect_failure_prob` scope correction** (the load-bearing decision of this plan): CP's own post-selection condition covers ancilla vacuum AND per-qubit-pair (i, j) data validity together, since `PostProcessedControlledRotationsItem.build_experiment()` registers both as one combined condition. Because `PBS`/`HWP` downstream of the gate are per-pair photon-number-preserving, checking pair i/j validity at final readout is mathematically identical to checking it right after the bare gate — so it belongs in `postselect_failure_prob`, not `residual`. Verified empirically both ways: the wrong split reproduced the exact unresolved TVD figure `15-RESEARCH.md` flagged; the corrected split matches the theoretical closed form to ~1e-15.
- **Mode-count arithmetic**: outer processor sized `2n+4` with a 4-entry ancilla mapping dict, per the plan's own structural warning — this alone was necessary but *not* sufficient (see above) to reach the TVD bar.
- **Ancilla input annotation**: plain `'0'` (no `{P:V}` tag), confirmed empirically rather than assumed to transfer from `heralded_cz`'s herald-ancilla convention — CP's ancilla is vacuum, not a real photon, so no polarization annotation is needed.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Corrected `postselect_failure_prob`/`residual` accounting to fold qubit-pair (i,j) data invalidity into failure, not residual**
- **Found during:** Task 1's own smoke-test verification step (required by the plan before writing the full test suite)
- **Issue:** The plan's literal recipe ("if ancilla nonzero → failure; otherwise decode via `fock_to_bitstring`, `None` → residual") produced TVD~0.375 at the smoke-test configuration (n=2, α=π, θ=0), matching `15-RESEARCH.md`'s own flagged-unresolved TVD~0.3-0.4 finding from its prior end-to-end attempt. Root cause: CP's own internal post-selection condition (ancilla vacuum AND `[0,1]==1 & [2,3]==1` on the gate's own dual-rail pair) was being split across two different reported buckets, effectively under-normalizing `dist`.
- **Fix:** Added `_decode_single_qubit_pair` to check qubit i's and j's own pair validity separately from any bystander qubit; folded i/j-pair invalidity into `postselect_failure_prob`, reserving `residual` for genuine bystander-only leakage (which measures 0.0 in every tested configuration, matching this module's established lossless-pipeline convention).
- **Files modified:** `iqp_photonic_encoding.py`
- **Verification:** TVD dropped from ~0.375 to floating-point noise (`~1e-16`) at the same smoke-test configuration; measured success probability matches the closed-form `p_success(α)=1/σ_max^4` to ~1e-15 across all tested α; full test suite (61/61 module, 142/142 repo) passes.
- **Committed in:** `de6bdb6` (Task 1 commit — the corrected version was written directly, not as a follow-up fix, since the smoke test caught it before any commit was made)

---

**Total deviations:** 1 auto-fixed (Rule 1 - bug)
**Impact on plan:** Necessary to meet the plan's own locked TVD<1e-6 pass/fail gate. No scope creep — the fix is entirely within `photonic_cp_iqp_distribution`'s own accounting logic, not a new architectural component.

## Issues Encountered

`15-RESEARCH.md` had flagged the exact wiring/TVD risk this plan's structural warning anticipated (mode-count arithmetic, 2 vs 4 ancilla modes) but its own end-to-end attempt still failed at TVD~0.3-0.4 even after that fix, calling it an unresolved open risk. This plan's own smoke-test step reproduced that exact number, which made the root cause traceable: not a further mode-wiring/convention bug (the isolated bare-`build_cp_insertion`-plus-readout test, run to debug this, showed the "clean" success amplitude was *already* exactly 1/9 for every computational-basis input, confirming the wiring itself was correct), but a postselection-accounting classification error in how "failure" vs "residual" was split. Diagnosed by isolating `build_cp_insertion` with a plain readout (no state-prep/diagonal/conjugation) and comparing per-basis-input success rates directly against the theoretical `p_success(α)=1/9` figure.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

Phase 16 (Extended Validation & Postselection Bookkeeping) can proceed: the core arbitrary-α weight-2 pipeline is now validated end-to-end (TVD<1e-6, boundary-agreement confirmed, success probability reported as an explicit table), unblocking denser α sweeps, mixed weight-1+arbitrary-θ weight-2 composability testing, and Forge-based postselection verification, per this plan's docs update. No blockers identified.

---
*Phase: 15-arb-01-core-gate-de-risking-validation*
*Completed: 2026-08-07*
