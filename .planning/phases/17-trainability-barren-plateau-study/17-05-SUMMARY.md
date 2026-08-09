---
phase: 17-trainability-barren-plateau-study
plan: 05
subsystem: testing
tags: [numpy, gradient-variance, barren-plateau, parameter-shift, mmd, rng]

# Dependency graph
requires:
  - phase: 17-01 (trainability/param_shift.py)
    provides: weight1_param_shift_delta, weight2_param_shift_delta (exact pi/4 parameter-shift gradient)
  - phase: 17-02 (trainability/mmd_exact.py)
    provides: gaussian_kernel_matrix_np, mmd2_grad (exact MMD^2 quadratic-form gradient)
  - phase: 17-03 (trainability/target_grid.py)
    provides: make_target_grid, bitstring_dict_to_vector (per-n K=2^n target distribution)
provides:
  - "trainability/rng.py::derive_seed/get_rng -- deterministic, reorder-safe RNG substream utility"
  - "trainability/stats.py::summarize_gradient_samples -- mean/var/std/median/abs_mean/rms over pooled gradient samples"
  - "trainability/sweep.py::run_gradient_variance_sweep -- pooled exact-gradient-variance sweep across n, for weight1/mixed generator scope and small_angle/uniform init"
affects: [17-06 (runs the actual expensive full sweep using this function), 17-07 (curve-fit analysis over the produced data)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Seed derivation via blake2b hash of repr(tuple(labeled_coordinate)) -- reorder-safe substreams, no running counter, no dependency on iteration order elsewhere"
    - "Gradient pooling across BOTH tracked parameter indices AND draws into one flat array per (n, generator_scope, init_scheme) cell -- deliberate design choice documented in trainability/sweep.py's module docstring, since TRAIN-01 measures landscape-wide variance, not per-parameter-identity breakdown"

key-files:
  created: [trainability/rng.py, trainability/stats.py, trainability/sweep.py, tests/test_sweep.py]
  modified: []

key-decisions:
  - "RNG seeds are a pure hash of each call's full labeled coordinate tuple (n, generator_scope, init_scheme, draw_index), never a running counter -- adding/reordering a system size, init scheme, or draw index elsewhere can never silently reshuffle another setting's random draws (17-RESEARCH.md's Don't-Hand-Roll guidance)"
  - "Gradients pooled across tracked parameter indices AND draws into one array per (n, generator_scope, init_scheme), not broken out per-parameter-identity -- TRAIN-01 asks how Var[gradient] scales with n across the parameter landscape, matching the classic barren-plateau question"

patterns-established:
  - "Any future sweep/experiment module in this repo needing reproducible-but-independent randomness across a multi-dimensional parameter space should use trainability/rng.py's derive_seed/get_rng shape rather than a global seed or running counter"

# Metrics
duration: 20min
completed: 2026-08-10
---

# Phase 17 Plan 05: Gradient-Variance Sweep Runner Summary

**`run_gradient_variance_sweep` wires the exact parameter-shift gradient, exact MMD^2 gradient, and per-n target grid into one pooled gradient-variance measurement per (n, generator_scope, init_scheme), backed by a reorder-safe hashed-seed RNG utility.**

## Performance

- **Duration:** 20 min
- **Started:** 2026-08-10T02:05:00+02:00 (approx.)
- **Completed:** 2026-08-10T02:25:00+02:00 (approx.)
- **Tasks:** 2 completed
- **Files modified:** 4 (all new)

## Accomplishments
- `trainability/rng.py::derive_seed(*parts)`/`get_rng(*parts)` -- deterministic per-labeled-coordinate seeding via blake2b hash, immune to reordering elsewhere in the sweep space
- `trainability/stats.py::summarize_gradient_samples(grads)` -- returns `n_samples`, `mean`, `var`, `std`, `median`, `abs_mean`, `rms` as plain Python floats
- `trainability/sweep.py::run_gradient_variance_sweep(n_values, generator_scope, init_scheme, n_draws, max_tracked_params, weight2_pair, seed_base)` -- composes Plans 17-01/17-02/17-03 end to end: draws thetas per init_scheme, runs `photonic_iqp_distribution`/`photonic_weight2_iqp_distribution`, computes exact parameter-shift deltas at capped tracked indices, converts to grid vectors, and computes the exact MMD^2 gradient via `mmd2_grad`; pools across tracked indices and draws; returns one summary-stats dict per requested n
- Manually verified all 4 (generator_scope, init_scheme) combinations at n=2,3 with 5 draws each, all completing in well under a minute per combination, plus the mixed-scope n=1 error path
- `tests/test_sweep.py` -- 13 fast smoke tests covering expected-keys shape (both scopes x both init schemes), determinism, `pick_tracked_indices` bounds, and both required error paths (empty `n_values`, `mixed` at `n=1`, unknown `generator_scope`)

## Task Commits

Each task was committed atomically:

1. **Task 1: RNG substream utility and gradient summary statistics** - `65576bb` (feat)
2. **Task 2: The gradient-variance sweep runner** - `cbe6963` (feat, includes tests/test_sweep.py)

## Files Created/Modified
- `trainability/rng.py` - `derive_seed(*parts)`, `get_rng(*parts)`
- `trainability/stats.py` - `summarize_gradient_samples(grads)`
- `trainability/sweep.py` - `sample_thetas`, `pick_tracked_indices`, `run_gradient_variance_sweep`
- `tests/test_sweep.py` - 13 smoke tests proving correct end-to-end wiring

## Decisions Made
- Seed derivation hashes each call's full labeled coordinate tuple rather than using a running counter or a single global seed -- this is what makes the substream utility reorder-safe (adding a new `n` value or reordering `generator_scope`/`init_scheme` combinations elsewhere can never shift another cell's draws), per 17-RESEARCH.md's explicit guidance to mirror the sibling project's `derive_seed`/`split_rng` shape.
- Gradients are pooled across BOTH tracked parameter indices and draws into a single flat array per `(n, generator_scope, init_scheme)` cell, not reported per-parameter-identity. This matches TRAIN-01's actual question (how does gradient variance scale with system size across the parameter landscape) and keeps Plan 17-07's curve-fit analysis operating on one clean array per sweep point.
- `max_tracked_params` caps the number of parameter indices whose gradient is measured per draw (evenly spaced via `np.linspace`, deduplicated) rather than measuring every parameter -- keeps the expensive photonic-circuit-simulation cost from scaling with both `n` and the number of tracked parameters simultaneously, while still sampling the parameter landscape broadly as `n` grows.

## Deviations from Plan
None - plan executed exactly as written. All API shapes (`derive_seed`/`get_rng`, `summarize_gradient_samples`, `run_gradient_variance_sweep`, `sample_thetas`, `pick_tracked_indices`) match the plan's specified signatures and behavior exactly, including the two locked init regimes and both generator scopes.

## Issues Encountered
None. `photonic_iqp_distribution` and `photonic_weight2_iqp_distribution`'s actual signatures (confirmed by reading `iqp_photonic_encoding.py` before implementing) matched the plan's assumptions exactly, so no adjustment was needed when wiring them into `trainability/sweep.py`.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- `trainability/sweep.py::run_gradient_variance_sweep` is ready for Plan 17-06 to call at the real, expensive scale (larger `n_values`, `n_draws>=100`) to produce the phase's actual gradient-variance-vs-n dataset.
- Manual smoke timing at n=2,3 with 5 draws (~27-28s per 2-n combination including per-draw x per-tracked-index photonic circuit simulation) gives Plan 17-06 a rough per-point cost estimate to plan the full sweep's runtime budget against.
- No blockers. Full 197-test repo suite passes with zero regressions as of this plan's completion.

---
*Phase: 17-trainability-barren-plateau-study*
*Completed: 2026-08-10*
