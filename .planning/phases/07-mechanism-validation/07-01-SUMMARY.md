---
phase: 07-mechanism-validation
plan: 01
subsystem: testing
tags: [pytorch, torch.func, jacrev, functional_call, scipy, mannwhitneyu, merlin, photonic-generator, mechanism-validation]

# Dependency graph
requires:
  - phase: 04-generator-natural-ordering
    provides: NaturallyOrderedGenerator, natural_sorted_centers, build_naturally_ordered_generator, results/phase4_natural_checkpoint.pt
  - phase: 06-documentation-publication
    provides: DESIGN_DECISIONS.md's 2026-07-29 correction defining the mechanism claim under test
provides:
  - Jacobian-based (Method B) neighbor-locality test for NaturallyOrderedGenerator, reusable for any future circuit/ordering variant
  - Working pattern for computing dq/dtheta against MerLin's QuantumLayer via torch.func (with the thetas-list patch required to make it non-zero)
  - Measured (not asserted) evidence on whether list-neighbors move together under this circuit/ordering
affects: [08-sigma-resweep (if planned next), any future extension/reuse of NaturallyOrderedGenerator or MerLin QuantumLayer Jacobians]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "torch.func.jacrev Jacobian against MerLin QuantumLayer requires monkey-patching quantum_layer.thetas (a plain Python list read directly by forward()) inside the traced closure -- functional_call's named-attribute substitution alone silently produces an all-zero Jacobian with no error"
    - "Two-condition statistical pass/fail (direction + effect-size threshold) reused from generator/train.py's decreasing_trend_check as this project's established rigor bar, applied to a new metric (cosine-similarity gap) via mannwhitneyu"

key-files:
  created:
    - generator/neighbor_locality.py
    - tests/test_neighbor_locality.py
    - neighbor_locality_test.py
    - results/phase7_neighbor_locality_metrics.csv
    - results/phase7_neighbor_locality_summary.md
  modified: []

key-decisions:
  - "min_effect=0.10 cosine-similarity units, mirroring decreasing_trend_check's 10%-relative-drop bar (locked in the plan, not decided at implementation time)"
  - "Fresh z per parameter draw, matching sample_latent's codebase-wide fresh-every-call convention (locked in the plan)"
  - "Trained-checkpoint theta included as a labeled supplementary measurement, kept separate from the pooled 20-draw random-init statistic (locked in the plan)"
  - "compute_jacobian additionally monkey-patches quantum_layer.thetas inside the jacrev-traced closure -- required fix, not in the original plan/research sketch, because functional_call alone never reaches MerLin's internal thetas list"

patterns-established:
  - "When differentiating through a MerLin QuantumLayer via torch.func, verify the Jacobian is actually nonzero before trusting functional_call's attribute substitution -- check compute_jacobian's docstring in generator/neighbor_locality.py for the root cause and fix"

# Metrics
duration: ~25min
completed: 2026-07-29
---

# Phase 7 Plan 01: Neighbor-Locality Test (Method B) Summary

**Jacobian-based neighbor-locality test (torch.func.jacrev against MerLin's QuantumLayer, with a required manual patch to reach its internal `thetas` list) ran against 20 fresh random-init draws + 1 trained checkpoint; both the pooled statistic (mean_diff=+0.0096) and the trained-checkpoint supplementary point (mean_diff=+0.0402) fail the locked 0.10 effect-size bar despite the pooled result clearing p<0.05 alone.**

## Performance

- **Duration:** ~25 min
- **Completed:** 2026-07-29T15:27:40Z
- **Tasks:** 2/2
- **Files modified:** 5 created, 0 modified

## Accomplishments
- Built a reusable Jacobian-based neighbor-locality test module (`generator/neighbor_locality.py`) with 4 passing unit tests, including a real-generator gradient-connectivity smoke test and two synthetic-data tests proving the two-condition statistical check correctly discriminates correlated from uncorrelated structure.
- Discovered and fixed a genuine blocking bug in the plan's own prescribed approach: MerLin's `QuantumLayer` reads trainable parameters from a plain Python list (`quantum_layer.thetas`) populated once at construction, which `torch.func.functional_call`'s attribute-substitution mechanism never reaches — the plan's exact recipe silently produces an all-zero Jacobian with no error.
- Ran the full experiment (20 fresh random-init draws + 1 trained-checkpoint draw) and produced real, reported (not interpreted) numbers in `results/phase7_neighbor_locality_metrics.csv` and `results/phase7_neighbor_locality_summary.md`.

## Task Commits

1. **Task 1: generator/neighbor_locality.py — Jacobian + two-condition statistical check, with unit tests** - `5a991b2` (feat)
2. **Task 2: neighbor_locality_test.py — run the experiment, produce CSV + summary** - `6ef85c3` (feat)

## Files Created/Modified
- `generator/neighbor_locality.py` - `compute_jacobian` (jacrev + `quantum_layer.thetas` patch), `adjacent_and_random_cosines` (signed cosine similarity), `neighbor_locality_check` (two-condition pass/fail)
- `tests/test_neighbor_locality.py` - 4 tests: real-generator Jacobian shape/gradient-connectivity, synthetic shapes, synthetic pass case, synthetic fail case
- `neighbor_locality_test.py` - orchestration script: 20 fresh draws + 1 trained-checkpoint draw, pooled statistic, per-draw sign check, CSV + summary md output
- `results/phase7_neighbor_locality_metrics.csv` - 20 per-draw rows + pooled + trained_checkpoint summary rows, real computed numbers
- `results/phase7_neighbor_locality_summary.md` - locked decisions, pooled result, per-draw robustness, trained-checkpoint supplementary result, owner-interpretation-pending placeholder

## Decisions Made
- `min_effect=0.10` cosine-similarity units, fresh-`z`-per-draw, and trained-checkpoint-included-as-supplementary — all three were pre-locked in `07-01-PLAN.md`'s objective section before execution began, per this codebase's "no silent unilateral design decisions" convention. Rationale for each is restated verbatim in `results/phase7_neighbor_locality_summary.md`.
- Concat order in `compute_jacobian`'s final `torch.cat` changed from the plan's `sorted(J_dict)` to `param_names` (insertion order from `qlayer.named_parameters()`) — functionally equivalent for this generator (both orders happen to be `['LI_simple', 'RI_simple']`), but derived directly from the same list needed for the `.thetas` patch rather than a separate alphabetical sort, avoiding two different orderings of the same two keys in one function.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `functional_call`+`jacrev` alone produces an all-zero Jacobian against MerLin's QuantumLayer**
- **Found during:** Task 1, first test run (`test_compute_jacobian_shape_and_gradient_connectivity` failed: shape correct, but `torch.any(J != 0)` was `False`)
- **Issue:** The plan's exact prescribed code (matching 07-RESEARCH.md's "verified live" example) uses `functional_call(gen, params, (z,))` under `jacrev`. Traced the root cause directly in MerLin's source (`venv/Lib/site-packages/merlin/algorithms/layer.py`): `_setup_parameters_from_custom` appends each trainable `nn.Parameter` to a plain Python list, `self.thetas`, once at construction; `forward()` reads parameters from `self.thetas` on every call (`params = [theta.expand(batch_size, -1) for theta in self.thetas]`), not from the module's named-parameter attributes. `functional_call` swaps only the named-parameter attributes for the duration of a call — it never touches the separate `.thetas` list — so the substituted parameters the Jacobian is supposedly taken with respect to never actually reach the circuit computation. The output has zero true dependency on them, so the Jacobian is correctly (not buggily) all-zero given how the forward pass actually reads its parameters — a silent failure mode, not an exception.
- **Fix:** `compute_jacobian` now also monkey-patches `quantum_layer.thetas` to point at the traced parameter tensors for the duration of the closure passed to `jacrev`, restoring the original list afterward. Verified live: with the patch, `gen(z)` under the patch produces output identical to the plain unpatched forward (`torch.allclose` true), and the resulting Jacobian is correctly nonzero (`max abs ~0.02-0.03` per prefix, matching the magnitude MerLin's own random-init parameters would produce).
- **Files modified:** `generator/neighbor_locality.py` (`compute_jacobian`)
- **Verification:** `tests/test_neighbor_locality.py::test_compute_jacobian_shape_and_gradient_connectivity` passes (shape `(462, 220)`, `torch.any(J != 0)` is `True`); full experiment run in Task 2 produced real nonzero cosine-similarity statistics for all 20 draws plus the trained checkpoint, consistent with a working, gradient-connected Jacobian.
- **Committed in:** `5a991b2` (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 blocking)
**Impact on plan:** Necessary for the experiment to produce any real evidence at all — without the fix, every draw would have silently reported a spurious all-zero Jacobian and the entire test would have been meaningless. No scope creep: the fix stays inside `compute_jacobian`'s existing signature and contract; nothing else in the plan changed.

## Issues Encountered
None beyond the deviation documented above (which was root-caused and fixed within Task 1, before any experiment numbers were generated).

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness

**Measured result (reported here as fact, not interpreted — per this project's CLAUDE.md, interpretation is the owner's job):**
- Pooled (N=20 draws x 461 pairs/group = 9,220 pairs/group): `adj_mean=0.0161`, `rand_mean=0.0065`, `mean_diff=+0.0096`, `p_value=0.00835`, `min_effect=0.10`, `passed=False`. The pooled result clears `p < 0.05` on its own but falls well short of the locked 0.10 effect-size bar — the exact "statistically significant but practically negligible" case the two-condition check was designed to catch (07-RESEARCH.md Pitfall 4).
- Per-draw robustness: 13/20 draws individually show adjacent-mean > random-mean (a bare majority, not a strong majority).
- Trained-checkpoint supplementary point (`results/phase4_natural_checkpoint.pt`): `adj_mean=0.0668`, `rand_mean=0.0266`, `mean_diff=+0.0402`, `p_value=0.0187`, `passed=False` — also fails the effect-size bar, though the gap is roughly 4x larger than the pooled random-init statistic's.
- `results/phase7_neighbor_locality_summary.md`'s "Interpretation" section is intentionally left as an owner-pending placeholder, per the plan's explicit non-goal ("the script reports computed numbers ... it does not auto-write an interpretive conclusion").

**Ready for:** the owner's own interpretation pass on this result (self-explanation checkpoint per this project's CLAUDE.md), and/or the sigma re-sweep (the roadmap's other Phase 7 experiment) if the owner wants to proceed with that next.

**No blockers.** Full existing test suite (53/53) still passes; no existing file was modified by this plan.

---
*Phase: 07-mechanism-validation*
*Completed: 2026-07-29*
