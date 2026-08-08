---
phase: 16-arb-01-extended-validation-postselection-bookkeeping
plan: 02
subsystem: quantum-photonic-encoding
tags: [perceval, linear-optics, iqp, cp-gate, success-probability, matplotlib]

# Dependency graph
requires:
  - phase: 15-04
    provides: "photonic_cp_iqp_distribution(n, i, j, thetas, alpha) -- the full-pipeline CP(alpha) weight-2 measurement function, TVD-validated against the exact reference, with postselect_failure_prob correctly accounted"
provides:
  - "cp_alpha_sweep.py -- a 16-point alpha sweep script, computing, asserting (against closed form, atol=1e-6), and plotting CP(alpha)'s success probability across [0, 2*pi)"
  - "results/phase16_alpha_sweep.csv / .png -- validated 16-point success-probability dataset and plot"
  - "docs/iqp-photonic-encoding.md's Denser alpha Sweep (Phase 16) subsection"
affects: [16-03, 20-technical-write-up]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Offset-uniform-grid construction to combine a small set of already-validated discrete points with a larger uniform sweep without collision (12 points offset by half a step, pi/12, to avoid landing on the 4 pre-existing pi/6, pi/3, pi values)."

key-files:
  created:
    - cp_alpha_sweep.py
    - results/phase16_alpha_sweep.csv
    - results/phase16_alpha_sweep.png
  modified:
    - docs/iqp-photonic-encoding.md

key-decisions:
  - "16-point grid = Phase 15's 4 already-validated alpha values (pi/6, pi/3, 2*pi/5, pi) plus 12 uniformly-spaced points offset by pi/12, per the plan's exact recipe -- guarantees the 4 existing points are included with no collision, giving direct visual continuity with Phase 15's prior verification rather than a disjoint new sweep."
  - "Every measured point asserted against the closed form (atol=1e-6) inline in the sweep script itself, not just plotted -- consistent with this project's established convention (Phase 15's success-probability table) of treating plots as validated datasets, never decorative."

# Metrics
duration: ~15min
completed: 2026-08-08
---

# Phase 16 Plan 02: Denser α Sweep Summary

**16-point α sweep of `photonic_cp_iqp_distribution`'s measured success probability across `[0, 2π)`, every point asserted against the closed-form `1/σ_max(α)⁴` to within 1e-6, saved as CSV+PNG and documented as a direct extension of Phase 15's 4-point table.**

## Performance

- **Duration:** ~15 min
- **Completed:** 2026-08-08
- **Tasks:** 2/2 completed
- **Files modified:** 4 (`cp_alpha_sweep.py` created, `results/phase16_alpha_sweep.csv`/`.png` created, `docs/iqp-photonic-encoding.md` modified)

## Accomplishments

- `cp_alpha_sweep.py` (repo root, matching `cp_gate_derisking.py`'s naming convention) sweeps `photonic_cp_iqp_distribution(n=2, i=0, j=1, thetas=[0.0,0.0], alpha)` at 16 α values across `[0, 2π)` — the same locked configuration Phase 15's `test_cp_pipeline_success_probability_vs_alpha_table` uses.
- The 16-point grid includes Phase 15's 4 already-validated points (`π/6`, `π/3`, `2π/5`, `π`) exactly, plus 12 additional uniformly-spaced points offset by `π/12` to avoid collision.
- All 16 measured points matched the closed-form `p_success(α)=1/σ_max(α)⁴` to within `1e-6` — verified live (max observed diff ~1e-9, well inside tolerance).
- `results/phase16_alpha_sweep.csv` (16 rows + header) and `results/phase16_alpha_sweep.png` (closed-form curve at 200 dense points, with the 16 measured points overlaid as scatter markers) saved.
- `docs/iqp-photonic-encoding.md` gained a new "Denser α Sweep (Phase 16)" subsection, positioned directly after "Full-Pipeline Validation (Plan 15-04)" and before "Conclusion and Open Questions", referencing both output files and stating explicitly that every point was asserted, not just plotted.

## Task Commits

Each task was committed atomically:

1. **Task 1: Write and run cp_alpha_sweep.py** - `5957964` (feat)
2. **Task 2: Document the 16-point sweep in docs/iqp-photonic-encoding.md** - `892c588` (docs)

## Files Created/Modified

- `cp_alpha_sweep.py` — 16-point α sweep: builds the offset-uniform grid, calls `photonic_cp_iqp_distribution`, asserts against the closed form, saves CSV+PNG.
- `results/phase16_alpha_sweep.csv` — raw data: `alpha, measured_success_prob, closed_form_success_prob` for all 16 points.
- `results/phase16_alpha_sweep.png` — closed-form curve (200 dense points) with the 16 measured points overlaid.
- `docs/iqp-photonic-encoding.md` — new "Denser α Sweep (Phase 16)" subsection, cross-referencing the sweep's outputs.

## Decisions Made

- Followed the plan's exact grid-construction recipe (4 validated points + 12 offset-uniform points) rather than a plain 16-point uniform grid, to guarantee visual/numeric continuity with Phase 15's already-verified points.
- Used a single full-overwrite CSV write (`csv.DictWriter`), not `batch_sweep.py`'s resumable-merge pattern, since this sweep completes in one pass with no need for checkpoint/resume complexity.

## Deviations from Plan

None — plan executed exactly as written. The venv's `perceval` install required running via `venv/Scripts/python.exe` rather than the system `python` (system Python has no `perceval` installed); this is standard repo setup, not a plan deviation.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

Plan 16-03 (Forge-based postselection verification + final Conclusion/Open-Questions update, per this plan's explicit note that it does NOT touch that section) can proceed independently — no blockers from this plan. Full repo test suite (142/142) still passes with no regressions.

---
*Phase: 16-arb-01-extended-validation-postselection-bookkeeping*
*Completed: 2026-08-08*
