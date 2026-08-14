---
phase: 18-hardness-under-loss-assessment
plan: 04
subsystem: hardness-assessment
tags: [numpy, tdd, hardness, anticoncentration, bremner-montanaro-shepherd, baselines]

# Dependency graph
requires: []
provides:
  - "hardness/baselines.py: uniform_baseline(n), product_of_marginals_baseline(reference_dist, n), anticoncentration_alpha(dist, n) -- pure, Perceval-free functions"
  - "hardness/ package (new, hardness/__init__.py)"
affects: ["18-05 (eta-sweep integration will consume both baselines and anticoncentration_alpha)", "18-06/18-07/18-08 (analysis/write-up stages)"]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Pure-numpy, no-cross-import, single-concern module (matches trainability/*.py convention) -- baselines.py has zero Perceval dependency, callers pass distribution dicts in directly"
    - "product_of_marginals_baseline does not renormalize or assume a normalized reference -- documented contract, caller's responsibility (needed for lossy/residual-bearing distributions in later Phase 18 plans)"

key-files:
  created:
    - hardness/__init__.py
    - hardness/baselines.py
    - tests/test_baselines.py

key-decisions:
  - "Implemented exactly per the plan's <implementation>/<behavior> blocks -- no deviation from the specified formulas, alphabet convention ('0'/'1', not 'H'/'V'), or worked examples."

patterns-established:
  - "Baseline/comparison distributions for Phase 18 live in a new top-level hardness/ package, mirroring trainability/'s Phase 17 package structure."

# Metrics
duration: ~15min
completed: 2026-08-14
---

# Phase 18 Plan 04: Classically-Easy Baselines & Anticoncentration Parameter Summary

**`hardness/baselines.py` implementing HARD-05's two classically-easy comparison distributions (uniform, product-of-marginals) plus BMS Theorem 4's anticoncentration parameter `alpha(dist, n)`, all pure/Perceval-free and verified against known closed-form values.**

## Performance

- **Duration:** ~15 min (RED confirm -> GREEN implement -> verify -> commit)
- **Completed:** 2026-08-14
- **Tasks:** 1 (TDD: RED, GREEN; no REFACTOR needed -- implementation matched the plan's reference spec with no cleanup required)
- **Files modified:** 3 (all new)

## Accomplishments
- `uniform_baseline(n)`: exact `2**-n` for every one of `2**n` `'0'/'1'` bitstrings, verified at n in {1,2,3,4}.
- `product_of_marginals_baseline(reference_dist, n)`: per-qubit marginals summed only over `reference_dist`'s present keys (no internal renormalization assumed), matched to a hand-computed 4-value worked example (n=2) plus an explicit unnormalized-reference test (mass sums to 0.5, not 1.0) confirming the documented "caller's responsibility" contract holds in practice, not just in the docstring.
- `anticoncentration_alpha(dist, n)`: BMS Theorem 4's `2**n * sum(p_x**2)` normalization, verified exactly at both closed-form extremes -- `alpha=1.0` on the uniform distribution, `alpha=2**n` on a delta/point-mass distribution -- at n in {1,2,3,4} and {1,2,3} respectively.
- TVD wiring sanity-checked by reusing (not re-deriving) `iqp_photonic_encoding.total_variation_distance`: zero self-distance, and a hand-computable `0.75` uniform-vs-delta case.

## Task Commits

TDD task, two commits (RED -> GREEN; no REFACTOR needed):

1. **RED: failing tests for classically-easy baselines and anticoncentration alpha** - `067e695` (test)
2. **GREEN: implement classically-easy baselines and anticoncentration alpha** - `415dbbb` (feat)

## Files Created/Modified
- `hardness/__init__.py` - new package docstring (Phase 18)
- `hardness/baselines.py` - `uniform_baseline`, `product_of_marginals_baseline`, `anticoncentration_alpha` (94 lines, pure numpy/itertools/math, no Perceval import)
- `tests/test_baselines.py` - 19 tests: uniform-baseline key/value/normalization checks, anticoncentration alpha at both closed-form extremes, product-of-marginals hand-computed example, unnormalized-reference handling, TVD wiring sanity checks (88 lines)

## Decisions Made
None beyond the plan's own spec -- implemented the formulas, alphabet convention, and test cases exactly as written in `<implementation>`/`<behavior>`. No architectural or interpretive choices were needed.

## Deviations from Plan

None — plan executed exactly as written.

## Issues Encountered

**Concurrent-session git-index race (process note, not a content bug).** Per this project's Fleet Operations convention (parallel sessions expected), another in-flight session was simultaneously executing Plan 18-02's RED phase (`tests/test_loss_model.py`, importing a not-yet-existent `hardness/loss_model.py`). That file was apparently staged into the shared git index by the other session between this execution's `git status` check and its `git commit` call for the GREEN task; because `git commit` (without a pathspec) commits everything currently staged, not just the paths most recently `git add`-ed, `tests/test_loss_model.py` was swept into this plan's `415dbbb` commit alongside the intended `hardness/__init__.py`/`hardness/baselines.py`. Confirmed via `git show --stat 415dbbb`. No content was lost or altered — the file is exactly Plan 18-02's own RED-phase test, unrelated to and not evaluated by this plan. This plan's own full-suite verification therefore ran with `--ignore=tests/test_loss_model.py` (253/253 passed, zero regressions from this plan's own changes); the unscoped full suite currently shows one collection error (`ModuleNotFoundError: No module named 'hardness.loss_model'`), which is Plan 18-02's own expected, honest RED-phase state, not a regression introduced here. **Lesson for future executions in this repo: always re-run `git status --short` immediately before `git commit`, or commit with an explicit pathspec (`git commit <paths> -m ...`), never a bare `git commit -m` that trusts the index's current contents** — `git add <specific files>` alone does not guarantee only those files end up in the resulting commit if another process staged something else in between.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- `hardness/baselines.py` is a trusted, independently-tested, Perceval-free primitive ready for Plan 18-05's eta-sweep integration to consume: `uniform_baseline` and `product_of_marginals_baseline` for HARD-05's dual-baseline TVD tracking, `anticoncentration_alpha` for HARD-04/HARD-05's alpha(eta) tracking across both weight-1 and mixed scopes.
- `product_of_marginals_baseline`'s "compute once from the reference, never renormalize internally" contract is implemented and tested — Plan 18-05 must call it exactly once against the lossless (eta=1) target distribution per (n, generator_scope) cell and reuse the result across the whole eta grid, per `18-CONTEXT.md`'s lock; this plan does not enforce that call pattern (it's a pure function), so Plan 18-05 is responsible for the correct call site.
- This plan's own scope (253 tests, ignoring the concurrently-in-flight `test_loss_model.py`) passes with zero regressions. The full unscoped suite will only be fully green once Plan 18-02's own work lands its GREEN phase — not this plan's responsibility.

---
*Phase: 18-hardness-under-loss-assessment*
*Completed: 2026-08-14*
