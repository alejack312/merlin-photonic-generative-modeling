---
phase: 02-generator-data-loss-infrastructure
plan: 04
subsystem: ml-generator
tags: [pytorch, merlin, pytest, mmd, kernel]

requires:
  - phase: 02-01
    provides: generator/bin_centers.py (make_bin_centers, shared K=400 grid)
  - phase: 02-02
    provides: generator/noise.py (sample_latent, valid QuantumLayer input)
  - phase: 02-03
    provides: generator/data.py (load_circles_data, compute_p_real)
provides:
  - "generator/mmd.py: gaussian_kernel_matrix(centers, sigma) -> (400,400) Gram matrix; mmd2(p, q, kernel_matrix) -> scalar; SIGMA_GRID = [0.02, 0.05, 0.1, 0.2, 0.4]"
  - "tests/test_mmd.py: kernel sanity, finite/non-negative over random trials, self-comparison ~0 against real p_real, gradient flow through a real QuantumLayer forward pass"
affects: [phase-3-training]

tech-stack:
  added: []
  patterns:
    - "torch.cdist(x,x) is not bit-exact symmetric and its diagonal is not bit-exact 0 (float32 cancellation in its internal ||a||^2+||b||^2-2ab formula) — both artifacts get amplified by small-sigma Gaussian-kernel division; use atol=1e-3/1e-4 on symmetry/diagonal checks over such a kernel, not the torch.allclose default"
    - "When testing gradient flow through an nn.Module, construct exactly one instance and reuse it for both the forward pass and the parameter check — a second, freshly-constructed instance was never part of the backward graph and can never show gradients"

key-files:
  created: [generator/mmd.py, tests/test_mmd.py]
  modified: []

key-decisions:
  - "gaussian_kernel_matrix/mmd2 implemented in torch (cdist/exp/matmul), not numpy — mmd2's q argument must stay on PyTorch's autograd graph since it comes from a trainable QuantumLayer forward pass; a numpy implementation would silently sever gradient flow to the circuit."

patterns-established:
  - "Kernel symmetry/diagonal pytest assertions over a Gaussian kernel built on torch.cdist use loosened, measured tolerances (atol=1e-4 symmetry, atol=1e-3 diagonal) rather than torch.allclose defaults, because cdist's self-distance float32 noise gets amplified by small sigma."

duration: unrecorded (interactive session, not gsd-executor run)
completed: 2026-07-19
---

# Phase 2, Plan 04: Closed-form MMD² loss (GEN-05) Summary

**`generator/mmd.py` implements the closed-form MMD² over the K=400 bin-centers via a precomputed Gaussian kernel Gram matrix, fully differentiable through a real `QuantumLayer` forward pass, verified by a 7-test suite (24/24 across the whole phase) including the two properties that matter most for Phase 3: `mmd2(p_real, p_real) ≈ 0` and gradients reaching the circuit's trainable parameters.**

## Performance

- **Duration:** unrecorded — implemented via owner attempt → review → fix cycle, not gsd-executor.
- **Tasks:** 2 (matches plan)
- **Files created:** 2 (`generator/mmd.py`, `tests/test_mmd.py` — the latter existed as an empty placeholder from 02-01, filled in here)

## Accomplishments
- `gaussian_kernel_matrix()`/`mmd2()` built entirely on `torch` operations (`cdist`, `exp`, `@`), keeping `q` on the autograd graph — the one property this whole plan exists to prove.
- `mmd2(p_real, p_real, K) ≈ 0` holds across all 5 σ values, verified against this project's *actual* `p_real` (via `generator.data` + `generator.bin_centers`), not synthetic data.
- Gradient flow verified end-to-end: `sample_latent()` → `QuantumLayer.simple(input_size=10, output_size=400)` → `mmd2()` → `.backward()` reaches the circuit's real parameters with finite gradients.
- Two real float32 numerical artifacts in `torch.cdist` (asymmetry, non-zero self-distance) found, measured, and correctly tolerance-adjusted rather than papered over — see `tech-stack.patterns`.
- Full `tests/` suite: 24/24 passing across all four Phase 2 plans together.

## Task Commits

Not committed yet — `generator/mmd.py` and `tests/test_mmd.py` are untracked/modified (confirmed via `git status`). No commit hashes to report.

## Files Created/Modified
- `generator/mmd.py` — `SIGMA_GRID`, `gaussian_kernel_matrix(centers, sigma) -> Tensor(K,K)`, `mmd2(p, q, kernel_matrix) -> Tensor` (scalar, clamped to `>=0`).
- `tests/test_mmd.py` — 4 test functions (kernel sanity parametrized over σ, finite/non-negative over 50 random trials × σ, self-comparison ≈0 parametrized over σ, single gradient-flow integration test) — 20 collected test cases total (parametrization included).

## Decisions Made
- `torch`, not `numpy`, throughout `mmd.py` — see `key-decisions` above. This was the one design choice in this plan that mattered most and was worth catching before Phase 3: a numpy-based kernel would have looked identical in isolated tests (finite, non-negative, symmetric) but silently produced a `q` disconnected from the circuit's autograd graph, so training would never actually update the circuit's parameters.

## Deviations from Plan

### Auto-fixed Issues

**1. Fixed `generator/mmd.py`'s numpy/annotation bugs (owner's first draft)**
- **Found during:** initial review — module failed to import (`NameError` from `-> (K,K)`/`-> scalar` annotations); separately, the implementation used `numpy`/`scipy.spatial.distance.cdist` instead of `torch`
- **Fix:** owner corrected both independently before the test-fixing pass — verified via smoke-run matching the plan's own verify command exactly (shape `(400,400)`, max `1.0`, min `0.0`)
- **Files modified:** `generator/mmd.py` (by the owner, verified by review)

**2. Rewrote `tests/test_mmd.py` from scratch**
- **Found during:** initial review — file failed to even collect (`ModuleNotFoundError: quantum.layer`, which doesn't exist in this project; should be `merlin.QuantumLayer`), and only 2 of the plan's 4 required checks were attempted, both broken: `p_real` was `np.random.randn(10)` (wrong library, wrong shape — 10 is the latent dim, not the 400 bin count — and not a valid probability vector); `gaussian_kernel_matrix(p_real, sigma)` passed a probability vector where bin-center coordinates were expected; `assert mmd2(...) == 0` used exact float equality instead of `pytest.approx`; the gradient test referenced an undefined `p_real`, passed a raw NumPy array into `QuantumLayer.forward()`, and — most importantly — constructed `QuantumLayer.simple(...)` **twice** (once for the forward pass, again in the parameter-check loop), so the parameters being checked were never part of the backward graph at all
- **Fix:** full rewrite per the plan's 4 required checks, using the project's real `p_real`/`bin_centers`/`sample_latent`, a single reused `quantum_layer` instance, and `torch.isfinite(grad).all()` rather than `!= 0`
- **Files modified:** `tests/test_mmd.py`
- **Verification:** `pytest tests/test_mmd.py -v` — all pass after fix

**3. Loosened kernel symmetry/diagonal test tolerances after measuring real cdist float32 noise**
- **Found during:** running the rewritten suite — `test_kernel_matrix_sanity` failed at σ=0.02/0.05 on both the `K == K.T` check (default `torch.allclose` tolerance) and the diagonal-≈1.0 check
- **Issue:** `torch.cdist(centers, centers)` has ~1e-6 inherent asymmetry and ~5e-4 non-zero self-distance (float32 cancellation in its internal distance formula), both amplified by `/(2σ²)` at small σ
- **Fix:** measured the actual deviations directly, then set `atol=1e-4` (symmetry) and `atol=1e-3` (diagonal) — loose enough to tolerate the measured artifact, tight enough to still catch a real bug (e.g. transposed indices, wrong exponent sign)
- **Files modified:** `tests/test_mmd.py`
- **Verification:** `pytest tests/ -v` — 24/24 pass across the full phase

---

**Total deviations:** 3 (owner fixed #1 independently; #2 full test rewrite; #3 tolerance correction backed by direct measurement)
**Impact on plan:** All required to meet the plan's stated must-haves. No scope creep — no functionality beyond `gaussian_kernel_matrix`/`mmd2` and their 4 required test properties was added.

## Issues Encountered
- `torch.cdist` float32 symmetry/diagonal artifacts (see Deviations #3) — resolved via measured tolerance adjustment, not by weakening what the tests actually verify.

## User Setup Required
None — no external service configuration required.

## Next Phase Readiness
- **Phase 2 is complete.** All four components (noise, bin-centers, p_real, MMD²) exist, are independently verified, and pass together (24/24) — the phase's own goal-backward success criterion.
- Phase 3 (End-to-End Training Run, the July 25 stall-risk checkpoint) can now wire these four pieces into an actual training loop: `sample_latent()` → `QuantumLayer` → `mmd2(p_real, q, kernel)` → `.backward()` → optimizer step.
- Same outstanding gap as 02-01/02-02/02-03: nothing from this plan is committed yet.

---
*Phase: 02-generator-data-loss-infrastructure*
*Completed: 2026-07-19*
