---
phase: 02-generator-data-loss-infrastructure
plan: 02
subsystem: ml-generator
tags: [pytorch, merlin, pytest, quantum-layer, latent-sampling]

requires:
  - phase: 02-generator-data-loss-infrastructure/02-01
    provides: pytest scaffolding (pytest.ini, generator/ and tests/ packages), generator/bin_centers.py
provides:
  - "generator/noise.py: sample_latent(batch_size) -> fresh (batch_size, 10) Gaussian tensor via merlin.NormalLatent"
  - "tests/test_noise.py: shape/dtype, resample-per-call, forward-pass-through-QuantumLayer, and nonzero-support pitfall-guard coverage"
affects: [02-03, 02-04]

tech-stack:
  added: []
  patterns:
    - "Use torch.allclose/torch.equal for tensor assertions in tests, not pytest.approx (breaks on grad-tracked tensors and silently no-ops without `==`) — see ~/.claude/learnings/2026-07-19-pytest-approx-misuse-grad-tensor.md"

key-files:
  created: [generator/noise.py, tests/test_noise.py]
  modified: []

key-decisions:
  - "sample_latent has no dtype passthrough parameter — NormalLatent's own default (float32) is used directly; an initial draft added an unused dtype param and was removed as untested dead code."
  - "No speculative make_noise/make_noise_grid helpers — an initial draft added these with no caller in this or later plans; removed as scope creep per GEN-02's actual requirement (only sample_latent is needed)."

patterns-established:
  - "Tensor-value pytest assertions use torch.allclose/torch.equal, never pytest.approx, because QuantumLayer output still carries requires_grad and pytest.approx's internal handling breaks on it (and pytest.approx without `==` never compares anything regardless)."

duration: unrecorded (interactive session, not gsd-executor run)
completed: 2026-07-19
---

# Phase 2, Plan 02: Latent noise sampling (GEN-02) Summary

**`generator/noise.py` samples fresh (batch, 10) Gaussian latents via `merlin.NormalLatent(dim=10, std=2π)`, verified non-degenerate through `QuantumLayer.simple(input_size=10, output_size=400)` by a 4-test pytest suite including the explicit zero-padding pitfall guard.**

## Performance

- **Duration:** unrecorded — implemented interactively (owner attempt → review → fix cycle), not via gsd-executor's atomic-commit loop.
- **Tasks:** 2 (matches plan)
- **Files created:** 2 (`generator/noise.py`, `tests/test_noise.py`)

## Accomplishments
- `sample_latent(batch_size)` resamples fresh every call (no caching), confirmed by `test_resample_latent`.
- Forward pass through `QuantumLayer.simple(input_size=10, output_size=400)` verified: correct shape, non-negative, each row sums to 1.
- The specific pitfall this plan exists to catch — `input_size=2`'s silent 397/400 zero-padding degeneracy (RESEARCH.md Pitfall 1) — has an explicit regression guard (`test_pitfall_guard`, `(out > 0).sum(dim=1).float().mean() > 50`) that a shape/sum-only test would not catch.

## Task Commits

Not committed yet — all of `generator/noise.py`, `tests/test_noise.py`, and the phase-01 scaffolding remain uncommitted (`git status`: `generator/`, `tests/`, `pytest.ini` untracked; `requirements.txt` modified). No commit hashes to report; commit before starting 02-03.

## Files Created/Modified
- `generator/noise.py` — `sample_latent(batch_size) -> Tensor(batch_size, 10)` via `merlin.NormalLatent(dim=10, mean=0.0, std=2*math.pi)`.
- `tests/test_noise.py` — 4 tests: shape/dtype, resample-per-call, forward-pass-through-`QuantumLayer`, nonzero-support pitfall guard.

## Decisions Made
- Dropped an unused `dtype` parameter from `sample_latent` (added in an early draft, never wired through to `.sample()` — would have silently done nothing if a caller passed it).
- Dropped `make_noise`/`make_noise_grid` helpers from an early draft — not required by GEN-02, no caller anywhere in this phase, and `make_noise_grid` was a duplicate of `make_noise` under a different name.
- Test correctness fix: `test_forward_pass` originally asserted `pytest.approx(out.sum(dim=1), 1.0)` with no `==` — this compares nothing and crashed with `RuntimeError: Can't call numpy() on Tensor that requires grad` because `out` still carries autograd state from `QuantumLayer`. Replaced with `torch.allclose(out.sum(dim=1), torch.ones(16), atol=1e-5)`, which works directly on grad-tracked tensors. Full writeup: `~/.claude/learnings/2026-07-19-pytest-approx-misuse-grad-tensor.md`.

## Deviations from Plan

### Auto-fixed Issues

**1. Removed untested/unused `dtype` parameter from `sample_latent`**
- **Found during:** review of owner's first draft of Task 1
- **Issue:** parameter accepted but never passed to `.sample()` — silently ignored if used
- **Fix:** removed the parameter; `sample_latent(batch_size)` matches the plan's locked signature
- **Files modified:** `generator/noise.py`
- **Verification:** `sample_latent(5).dtype == torch.float32` (NormalLatent's own default)

**2. Removed speculative `make_noise`/`make_noise_grid` helpers**
- **Found during:** review of owner's first draft of Task 1
- **Issue:** neither function is required by GEN-02 or called anywhere; `make_noise_grid` duplicated `make_noise`'s body
- **Fix:** deleted both functions
- **Files modified:** `generator/noise.py`

**3. Fixed no-op/crashing assertion in `test_forward_pass`**
- **Found during:** review of owner's first draft of Task 2, then reproduced directly
- **Issue:** `assert pytest.approx(out.sum(dim=1), 1.0)` has no `==`, so it never compared anything, and crashed on the grad-tracked tensor besides
- **Fix:** `assert torch.allclose(out.sum(dim=1), torch.ones(16), atol=1e-5)`
- **Files modified:** `tests/test_noise.py`
- **Verification:** `./venv/Scripts/python.exe -m pytest tests/test_noise.py -v` — 4/4 pass

---

**Total deviations:** 3 (2 scope-creep removals, 1 test-correctness fix)
**Impact on plan:** All three tighten the plan's locked scope/must-haves; none expand it. No functional scope creep survived into the final files.

## Issues Encountered
- `pytest.approx` misuse against a `requires_grad=True` tensor (see Decisions Made / learning note above) — resolved.

## User Setup Required
None — no external service configuration required.

## Next Phase Readiness
- `sample_latent()` is ready for Phase 3's training loop and for 02-04 (whatever in this phase consumes generator output).
- Outstanding gap (pre-existing, not from this plan): `.planning/phases/02-generator-data-loss-infrastructure/02-01-SUMMARY.md` was never created even though `generator/bin_centers.py`/`tests/test_bin_centers.py` are implemented and passing — `STATE.md` still says "Plan: Not yet planned." Worth reconciling before `/gsd:plan-phase` or `/gsd:progress` next runs, since they read summaries to assemble context.
- Nothing in this repo is committed yet (`generator/`, `tests/`, `pytest.ini` untracked; `requirements.txt` modified) — recommend committing 02-01 and 02-02's work before starting 02-03.

---
*Phase: 02-generator-data-loss-infrastructure*
*Completed: 2026-07-19*
