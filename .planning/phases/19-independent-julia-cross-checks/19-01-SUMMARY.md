---
phase: 19-independent-julia-cross-checks
plan: 01
subsystem: testing
tags: [cross-language-verification, perceval, csv, iqp-photonic-encoding, hardness-loss-model]

# Dependency graph
requires:
  - phase: 09-encoding-design
    provides: iqp_photonic_encoding.py exact/lossless distribution functions (exact_qubit_iqp_distribution, photonic_iqp_distribution, photonic_weight2_iqp_distribution)
  - phase: 18-hardness-under-loss-assessment
    provides: hardness/loss_model.py, hardness/loss_model_weight2.py lossy distribution functions and hardness/sweep.py's sample_thetas/ETA_GRID
provides:
  - julia/generate_reference.py, a reusable Python reference-distribution generator
  - 11 CSV reference files under results/julia_reference/ (5 exact-case, 6 loss-case)
affects: [19-02, 19-03, 19-04, 19-05]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Python -> CSV -> Julia diff bridge: plain 2-column bitstring,probability CSVs with `# key=value` header comment lines for any value (residual, herald_failure_prob, global_perf, thetas, eta) a downstream Julia script needs to reproduce the exact same circuit instance"
    - "Fixed single-draw theta generation for cross-implementation numeric diffs: hardness.sweep's existing seed-derivation utility (trainability.rng.get_rng) reused with a phase-specific seed_base, one draw (draw=0) per scope, never the pooled multi-draw sweep path"

key-files:
  created:
    - julia/generate_reference.py
    - results/julia_reference/qubit_n2.csv
    - results/julia_reference/qubit_n3.csv
    - results/julia_reference/weight1_n2.csv
    - results/julia_reference/weight1_n3.csv
    - results/julia_reference/weight2_locked_n2.csv
    - results/julia_reference/weight1_loss_n2_eta099.csv
    - results/julia_reference/weight1_loss_n2_eta080.csv
    - results/julia_reference/weight1_loss_n2_eta005.csv
    - results/julia_reference/mixed_loss_n2_eta099.csv
    - results/julia_reference/mixed_loss_n2_eta080.csv
    - results/julia_reference/mixed_loss_n2_eta005.csv
  modified: []

key-decisions:
  - "Real output filenames use an eta-suffixed per-file family (weight1_loss_n2_eta099.csv/eta080.csv/eta005.csv, mixed_loss_n2_eta099.csv/eta080.csv/eta005.csv) rather than the plan's files_modified shorthand (weight1_loss_n2.csv/mixed_loss_n2.csv), per the plan's own explicit note that the shorthand should be expanded and the real names recorded in the SUMMARY."
  - "photonic_weight2_iqp_distribution(n, i, j, thetas) returns dist already renormalized so sum(dist)+residual==1.0 (not 1.0-herald_failure_prob, as the plan's own draft text speculated before reading the actual function docstring) -- verified against the function's own docstring and test_wt2_tvd_gate_n2_theta_pi_4 before writing the assertion, and the script's assert matches this real contract, not the plan's initial guess."
  - "Cast every written probability/residual/herald_failure_prob/global_perf value through float(...) before repr() -- several upstream functions (exact_qubit_iqp_distribution, photonic_iqp_distribution, photonic_weight2_iqp_distribution) return np.float64, whose bare repr() is \"np.float64(0.123...)\", not a value a Julia CSV parser could read. Caught by inspecting the first generated qubit_n2.csv before committing, fixed before commit (Rule 1 - Bug: silent correctness issue for every downstream Julia consumer, not deferred)."
  - "Added sys.path insertion so `python julia/generate_reference.py` (the plan's own literal verify command) works when invoked directly, since repo root is not automatically on sys.path in that invocation form (only `python -m julia.generate_reference` gets it for free)."

patterns-established:
  - "Every reference CSV records the literal input values (thetas, eta, residual, herald_failure_prob, global_perf) it was generated from as `# key=value` header comments, never just a seed -- Plan 19-05's Julia script needs these as hardcoded literals to reproduce the identical circuit instance, per 19-RESEARCH.md Pitfall 4."

# Metrics
duration: 35min
completed: 2026-08-17
---

# Phase 19 Plan 01: Reference-Distribution Generator for Julia Cross-Checks Summary

**`julia/generate_reference.py` calls this repo's already-tested exact and lossy IQP distribution functions directly and writes 11 self-documenting CSV files (5 exact-case, 6 fixed-single-draw loss-case) that Plans 19-02 through 19-05's independently-built Julia scripts diff against.**

## Performance

- **Duration:** 35 min
- **Started:** 2026-08-17T14:00:00Z (approx)
- **Completed:** 2026-08-17T14:35:00Z (approx)
- **Tasks:** 2/2
- **Files modified:** 12 (1 script + 11 CSVs)

## Accomplishments
- `julia/generate_reference.py` produces every reference distribution VERIFY-02/VERIFY-03/VERIFY-04 need, with no new Python physics -- only direct calls into `iqp_photonic_encoding.py` and `hardness/loss_model*.py`
- 5 exact-case CSVs (qubit_n2/n3, weight1_n2/n3, weight2_locked_n2) covering VERIFY-02 and VERIFY-03's targets, the weight-2 case using the exact same configuration as the existing, passing `test_wt2_tvd_gate_n2_theta_pi_4` test
- 6 loss-case CSVs (weight1_loss_n2_eta{099,080,005}, mixed_loss_n2_eta{099,080,005}) for VERIFY-04, each generated from ONE fixed theta draw per scope (not a pooled multi-draw mean), with the literal theta values recorded in every file's header comment
- Every CSV's probability column verified (via a hard assertion, not a soft check) to sum to 1.0 minus any reported residual before being written to disk

## Task Commits

Each task was committed atomically:

1. **Task 1: Exact-distribution reference generator** - `b2261a1` (feat)
2. **Task 2: Loss-model reference generator with fixed single-draw thetas** - `af4cd87` (feat)

_No TDD flow for this plan (`autonomous: true`, no test file specified -- this is a reference-generation script, not new library logic with its own test suite)._

## Files Created/Modified
- `julia/generate_reference.py` - Reference-distribution generator; `generate_exact_references()` (VERIFY-02/03) and `generate_loss_references()` (VERIFY-04), run via `if __name__ == "__main__"`
- `results/julia_reference/qubit_n2.csv`, `qubit_n3.csv` - `exact_qubit_iqp_distribution` output, n=2/n=3, thetas=[0.3,1.1]/[0.3,1.1,0.75]
- `results/julia_reference/weight1_n2.csv`, `weight1_n3.csv` - `photonic_iqp_distribution` output, same theta cases, residual recorded in header
- `results/julia_reference/weight2_locked_n2.csv` - `photonic_weight2_iqp_distribution` output, n=2, i=0, j=1, thetas=[0,0] (pure pi/4 pair term), herald_failure_prob and residual recorded in header
- `results/julia_reference/weight1_loss_n2_eta{099,080,005}.csv` - `photonic_iqp_distribution_lossy` output at 3 eta values, single fixed theta draw (seed_base=190819, scope="weight1", n=2, draw=0), thetas/eta/residual/global_perf recorded in header
- `results/julia_reference/mixed_loss_n2_eta{099,080,005}.csv` - `photonic_weight2_iqp_distribution_lossy` output at the same 3 eta values, single fixed theta draw (seed_base=190819, scope="mixed", n=2, draw=0), thetas/eta/herald_failure_prob/residual/global_perf recorded in header

## Decisions Made
- **Real loss-case filenames** use an eta-suffixed family (`weight1_loss_n2_eta099.csv` etc.) rather than the plan's `files_modified` shorthand (`weight1_loss_n2.csv`) -- the plan explicitly anticipated and authorized this expansion, asking only that the real names be recorded here.
- **Weight-2 renormalization contract**: verified against `photonic_weight2_iqp_distribution`'s own docstring and the existing `test_wt2_tvd_gate_n2_theta_pi_4` test that `dist`/`residual` are already renormalized by `(1 - herald_failure_prob)`, so `sum(dist) + residual == 1.0` (not `1.0 - herald_failure_prob`, as the plan's draft text speculated before this verification step). The script's assertion matches the real, verified contract.
- **numpy float64 leakage fixed before commit**: `exact_qubit_iqp_distribution`/`photonic_iqp_distribution`/`photonic_weight2_iqp_distribution` return `np.float64` values; a bare `repr()` on those produces `"np.float64(0.123...)"`, which would break any Julia CSV parser expecting a bare number. Every written value is now explicitly cast through `float(...)` first. Caught by inspecting the first generated `qubit_n2.csv` output, not assumed correct.
- **`sys.path` insertion** added so the plan's own literal verify command (`python julia/generate_reference.py`, run directly rather than as `python -m julia.generate_reference`) can import repo-root modules (`iqp_photonic_encoding`, `hardness`, `trainability`) without requiring the caller to set `PYTHONPATH` or use module-invocation syntax.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] numpy float64 repr() leaking into CSV output**
- **Found during:** Task 1 (spot-checking the first generated `qubit_n2.csv`)
- **Issue:** Several upstream distribution functions return `np.float64` values; writing `repr(dist[bitstring])` directly produced values like `np.float64(0.1877808915423396)` in the probability column instead of a bare float -- would have silently corrupted every downstream Julia CSV parse.
- **Fix:** Cast every value through `float(...)` before `repr()` in `_write_csv` and in every header-comment f-string that records residual/herald_failure_prob/global_perf.
- **Files modified:** `julia/generate_reference.py`
- **Verification:** Re-ran the script and re-inspected `qubit_n2.csv`, `weight2_locked_n2.csv`, and one loss-case CSV -- all values are now bare Python floats.
- **Committed in:** `b2261a1` (Task 1 commit; the fix was made before either commit, so both commits reflect the corrected behavior)

**2. [Rule 3 - Blocking] `python julia/generate_reference.py` could not import repo-root modules**
- **Found during:** Task 1 (first verification run per the plan's literal verify command)
- **Issue:** Running the script via `python julia/generate_reference.py` (as opposed to `python -m julia.generate_reference`) does not put repo root on `sys.path`, so `from iqp_photonic_encoding import ...` raised `ModuleNotFoundError`.
- **Fix:** Added an explicit `sys.path.insert(0, ...)` pointing at the repo root, computed relative to the script's own file location.
- **Files modified:** `julia/generate_reference.py`
- **Verification:** `python julia/generate_reference.py` now runs cleanly from the repo root.
- **Committed in:** `b2261a1`

---

**Total deviations:** 2 auto-fixed (1 bug, 1 blocking)
**Impact on plan:** Both fixes necessary for the script to work at all / for its output to be usable by Julia. No scope creep -- no new physics or logic beyond wiring and file I/O, matching the plan's explicit constraint.

## Issues Encountered
None beyond the two auto-fixed deviations above.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- All 11 reference CSVs exist under `results/julia_reference/`, each internally consistent (probabilities sum to 1.0 minus any reported residual, verified by hard assertion at generation time, not just eyeballed).
- Full repo test suite (268/268) still passes -- this plan added no new Python logic beyond a script, so no new tests were required or written; existing suite confirms zero regressions.
- Plans 19-02 through 19-05 can start immediately: each has its file-based reference ready (qubit_n2/n3.csv for 19-02's VERIFY-02, weight1_n2/n3.csv + weight2_locked_n2.csv for 19-03/19-04's VERIFY-03, the 6 eta-suffixed loss CSVs for 19-05's VERIFY-04), with every literal theta/eta value needed to reproduce each circuit instance recorded in-file.
- No blockers identified.

---
*Phase: 19-independent-julia-cross-checks*
*Completed: 2026-08-17*
