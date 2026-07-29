---
phase: 07-mechanism-validation
verified: 2026-07-29T18:00:00Z
status: passed
score: 10/10 must-haves verified
---

# Phase 7: Mechanism Validation Verification Report

**Phase Goal:** Test the two concrete follow-ups flagged by the v1.0 self-audit as unresolved about the natural-order-correspondence result (ring_mass 0.609->0.691) -- whether the claimed mechanism actually holds, and whether an unrelated confound (stale sigma) explains part of the improvement instead. Two experiments in order: (1) Jacobian-based neighbor-locality test on NaturallyOrderedGenerator, (2) sigma re-sweep of Phase 4's SIGMA_GRID against the K=462 natural-order grid.

**Verified:** 2026-07-29
**Status:** passed
**Re-verification:** No -- initial verification

## Goal Achievement

### Observable Truths (07-01, neighbor-locality)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Jacobian-based (Method B) test runs against >=20 fresh, independently random-initialized draws of NaturallyOrderedGenerator | VERIFIED | neighbor_locality_test.py::run_random_draws calls build_naturally_ordered_generator() fresh inside the loop (N_DRAWS=20), no load_state_dict; CSV has 20 distinct per-draw rows with real, differing numbers |
| 2 | Pass/fail verdict is a two-condition check (significance AND effect-size threshold), not bare p-value | VERIFIED | generator/neighbor_locality.py::neighbor_locality_check: passed = bool(mean_diff >= min_effect and p_value < 0.05) -- both conditions required in code |
| 3 | Per-draw directional robustness reported (fraction of 20 draws individually showing adjacent-mean > random-mean) | VERIFIED | results/phase7_neighbor_locality_summary.md states 13/20 draws individually show adjacent-mean greater than random-mean; CSV per-draw rows carry the underlying mean_diff values used to compute it |
| 4 | Trained checkpoint theta measured once, as a labeled supplementary result kept separate from pooled statistic | VERIFIED | run_trained_checkpoint() loads results/phase4_natural_checkpoint.pt, reported as a separate CSV row (draw_idx=trained_checkpoint) and a separate Supplementary section in the summary, explicitly labeled as not pooled |
| 5 | Script reports numbers plus locked-decisions record only, no auto-written interpretive conclusion | VERIFIED | results/phase7_neighbor_locality_summary.md Interpretation section is the exact owner-pending placeholder; grep for conclusion language across both Phase 7 results summaries returns zero matches |

### Observable Truths (07-02, sigma re-sweep)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 6 | Same SIGMA_GRID Phase 4 used is re-swept against K=462 (not old K=400) grid | VERIFIED | sigma_resweep.py imports SIGMA_GRID from generator.mmd (same grid) and build_naturally_ordered_generator/natural_sorted_centers from generator.naturally_ordered_generator (K=462); docstring explicitly forbids make_bin_centers/build_generator and neither appears anywhere except that warning comment |
| 7 | Each sigma trained fresh (new random init) at Phase 4 fixed EPOCHS/LR/BATCH_SIZE | VERIFIED | EPOCHS=300, LR=0.01, BATCH_SIZE=32 constants match Phase 4; generator = build_naturally_ordered_generator() called fresh inside the per-sigma loop before the checkpoint-exists check |
| 8 | Sweep is resumable via skip-if-checkpoint-exists, run in foreground | VERIFIED resumability, minor note on foreground | train_all_sigmas checks os.path.exists(ckpt_path) to skip retrain, else trains and saves -- genuine resumability confirmed in code and all 5 checkpoint files exist on disk. 07-02-SUMMARY.md Issues Encountered section states the run was moved to a background process when a single tool-call timed out, which contradicts the plan explicit do-NOT-background instruction -- see Anti-Patterns below; does not affect correctness of the resulting artifacts |
| 9 | Results reported side-by-side against Phase 4 K=400 sweep numbers | VERIFIED | results/phase7_sigma_resweep_summary.md table values cross-checked directly against results/phase4_sweep_metrics.csv and results/phase7_sigma_resweep_metrics.csv -- all 10 numbers (5 sigmas x ring_mass K=400/K=462) match the source CSVs exactly |
| 10 | Summary reports comparison numbers only, no conclusion on whether stale sigma was a confound | VERIFIED | Descriptive facts only section states the argmax and deltas as measured facts with no causal claim attached; Interpretation section is the exact owner-pending placeholder |

**Score:** 10/10 truths verified (1 carries a minor documentation-consistency note, not a functional failure)

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| generator/neighbor_locality.py | compute_jacobian, adjacent_and_random_cosines, neighbor_locality_check | VERIFIED | Exists, 108 lines, all 3 functions present, exported, imported and used by both tests/test_neighbor_locality.py and neighbor_locality_test.py |
| tests/test_neighbor_locality.py | 4 tests: real-generator Jacobian shape/gradient test plus 2 synthetic pass/fail tests | VERIFIED | 4 test functions present; running pytest via the project venv gives 4 passed |
| neighbor_locality_test.py | Orchestration: 20 draws plus 1 checkpoint draw, CSV plus summary output | VERIFIED | 160 lines, runs run_random_draws, run_trained_checkpoint, write_csv, write_summary in main() |
| results/phase7_neighbor_locality_metrics.csv | Per-draw plus pooled plus trained_checkpoint rows | VERIFIED | 23 lines (header plus 22 data rows: 20 per-draw plus pooled plus trained_checkpoint), real distinct floating-point values, no placeholders |
| results/phase7_neighbor_locality_summary.md | Locked decisions, pooled result, per-draw robustness, trained-checkpoint result, interpretation-pending placeholder | VERIFIED | All 5 sections present with real numbers pulled from the run; no auto-written conclusion |
| sigma_resweep.py | Resumable per-sigma retrain at K=462 plus comparison figure | VERIFIED | 125 lines, train_all_sigmas, build_comparison_figure, main -- mirrors sweep.py structure |
| results/phase7_sigma_resweep_metrics.csv | sigma, ring_mass, gap_mass per SIGMA_GRID value at K=462 | VERIFIED | 6 lines (header plus 5 rows), real values, e.g. sigma=0.1 gives ring_mass=0.7145 |
| results/phase7_sigma_resweep_comparison.png | 6-panel figure | VERIFIED | Exists, 89KB (non-trivial size consistent with a real matplotlib figure) |
| results/phase7_sigma_resweep_summary.md | K=400 vs K=462 table, descriptive argmax statement, interpretation-pending handoff | VERIFIED | All sections present; table values verified against both source CSVs |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| neighbor_locality_test.py | generator/neighbor_locality.py | import of compute_jacobian, adjacent_and_random_cosines, neighbor_locality_check | WIRED | Import present and all 3 functions called in main() |
| generator/neighbor_locality.py | NaturallyOrderedGenerator | compute_jacobian operates on any passed-in generator instance | WIRED, with a documented and verified deviation | Plan exact functional_call-only recipe was found to silently produce an all-zero Jacobian (root-caused: MerLin QuantumLayer reads params from a plain-list thetas attribute that functional_call never touches). Fix (thetas monkey-patch inside the traced closure) is implemented and verified nonzero via test_compute_jacobian_shape_and_gradient_connectivity, which passes against the real generator |
| neighbor_locality_test.py | results/phase4_natural_checkpoint.pt | load_state_dict | WIRED | run_trained_checkpoint() loads this exact path; produces the labeled supplementary CSV row |
| sigma_resweep.py | generator/naturally_ordered_generator.py | import of build_naturally_ordered_generator, natural_sorted_centers | WIRED | Confirmed K=462 path used exclusively; make_bin_centers/build_generator (K=400) never imported or called |
| sigma_resweep.py | generator/train.py | import of train_step | WIRED | train_step reused unchanged inside train_all_sigmas training loop |
| results/phase7_sigma_resweep_summary.md | results/phase4_sweep_metrics.csv and results/phase7_sigma_resweep_metrics.csv | numeric citation | WIRED | All 10 cited ring_mass/gap_mass values checked line-by-line against both CSVs -- exact matches, no invented numbers |

### Requirements Coverage

No .planning/REQUIREMENTS.md exists in this repo, and the ROADMAP.md entry for Phase 7 states its requirements are none yet, since this phase predates a formal requirements pass and was scoped directly from the v1.0 milestone audit tracked backlog. No requirements-coverage table applies.

### Anti-Patterns Found

| File | Location | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| .planning/phases/07-mechanism-validation/07-02-SUMMARY.md | Deviations from Plan vs Issues Encountered sections | Self-contradiction: the Deviations section claims none, plan executed exactly as written, while the Issues Encountered section describes moving the run to a background process. The plan explicitly instructs running in the foreground and not backgrounding it, so background execution is a real deviation from an explicit instruction, not none | Info | Does not affect correctness of the shipped artifacts (all 5 checkpoints, CSV, and PNG are real and match expected values), but the SUMMARY self-report is internally inconsistent -- a reminder that SUMMARY claims should be checked rather than trusted |

No stub patterns (TODO, FIXME, placeholder, not implemented), empty returns, or hardcoded/fake statistics were found in generator/neighbor_locality.py, neighbor_locality_test.py, or sigma_resweep.py.

### Human Verification Required

None. This phase must-haves (code correctness, real computed numbers, absence of auto-written interpretation, two-condition check implementation, resumability) are all structurally verifiable and were verified directly: tests were re-run rather than trusted from SUMMARY, CSV and summary numbers were cross-checked against source files, and code was read to confirm the two-condition logic and the resumability check are real, not described-only.

The owner own interpretation of what these measured numbers mean for the ring_mass improvement claim is intentionally out of scope for this phase, explicitly deferred to the owner in both results summaries per this project CLAUDE.md -- that is a human judgment step for the owner to perform next, not a gap in this phase deliverables.

### Gaps Summary

No gaps. All 10 must-haves derived from 07-01-PLAN.md and 07-02-PLAN.md frontmatter are verified against actual code and result files, not SUMMARY.md claims:

- Both generator/neighbor_locality.py and tests/test_neighbor_locality.py exist; all 4 unit tests actually pass when run against the project venv (they fail to even collect under a bare system Python lacking the merlin package -- the venv is required and was used for this verification).
- results/phase7_neighbor_locality_metrics.csv and results/phase7_neighbor_locality_summary.md exist with 22 real, non-placeholder computed rows and sections.
- sigma_resweep.py, results/phase7_sigma_resweep_metrics.csv, results/phase7_sigma_resweep_comparison.png, and results/phase7_sigma_resweep_summary.md all exist with real numbers cross-checked against source CSVs.
- Neither results summary contains an auto-written interpretive conclusion -- both stop at reported numbers plus the exact owner-pending placeholder text.
- The two-condition pass/fail check (mean_diff >= min_effect and p_value < 0.05) is implemented in code inside neighbor_locality_check, not just described in prose.
- The sigma re-sweep is genuinely resumable: an os.path.exists(ckpt_path) skip-if-checkpoint-exists check is real, and all 5 checkpoint files exist on disk confirming the pattern was exercised.

One informational, non-blocking finding: 07-02-SUMMARY.md Deviations from Plan claim of none is contradicted by its own Issues Encountered section, which describes backgrounding the sweep script against the plan explicit foreground-only instruction. This does not affect the correctness of any artifact but is noted as a documentation-trust gap consistent with this verifier mandate not to take SUMMARY claims at face value.

Full regression check: the full existing test suite was run via the project venv and all 53 tests passed, confirming no existing test was broken by either plan.

---

Verified 2026-07-29 by Claude (gsd-verifier)
