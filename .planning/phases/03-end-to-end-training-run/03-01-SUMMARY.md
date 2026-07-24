---
phase: 03-end-to-end-training-run
plan: 01
subsystem: ml-training
tags: [pytorch, merlin, quantumlayer, mmd, adam, photonic-qml]

# Dependency graph
requires:
  - phase: 02-generator-data-loss-infrastructure
    provides: make_bin_centers (K=400 grid), sample_latent, compute_p_real, mmd2/gaussian_kernel_matrix (all pure torch, autograd-safe)
provides:
  - "generator/train.py: build_generator, train_step (batch-averaged MMD^2 step), decreasing_trend_check (scripted, non-eyeballed pass/fail)"
  - "root train.py: real 300-epoch end-to-end training run against the circles dataset"
  - "results/phase3_loss_history.csv, results/phase3_loss_curve.png, results/phase3_checkpoint.pt: checked-in evidence artifacts from the real run"
  - "GEN-06 met: first real, working end-to-end training run for this project"
affects: [04-evaluation-and-benchmarking, 05-hyperparameter-tuning-or-scaling]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Build QuantumLayer + optimizer exactly once outside the epoch loop; draw fresh z every step; average per-sample MMD^2 losses across a batch before backward() (single shared theta, batch reduces gradient-estimate variance, not a search over multiple parameter sets)."
    - "decreasing_trend_check(losses): scripted verdict (linregress slope < 0 AND >=10% first-decile-vs-last-decile relative drop) as the standing pattern for 'trend claims must be scripted, not eyeballed' in this repo."

key-files:
  created:
    - generator/train.py
    - tests/test_train.py
    - train.py
    - results/phase3_loss_history.csv
    - results/phase3_loss_curve.png
    - results/phase3_checkpoint.pt
  modified: []

key-decisions:
  - "lr=0.01 (the quickstart.py-informed starting point) produced a passing decreasing_trend_check on the first real run -- the planned lr=0.05/0.1 escalation path (03-RESEARCH.md Open Question 2) was not needed. See train.py's LR comment."
  - "Owner-confirmed batch-averaging strategy (DESIGN_DECISIONS.md 2026-07-24) validated in practice by a real passing run, not just plausible in theory."

patterns-established:
  - "Self-explanation checkpoint required a real correction, not a rubber stamp -- documented in full below per this project's CLAUDE.md."

# Metrics
duration: ~35min
completed: 2026-07-24
---

# Phase 3 Plan 01: End-to-End Training Run Summary

**Real 300-epoch MMD^2-trained QuantumLayer generator run against the circles dataset (batch_size=32, sigma=0.1, lr=0.01) produced a scripted-verified decreasing loss trend (62% relative drop, negative slope, p≈0) -- GEN-06, the July 25 stall-risk checkpoint, is met with two days of runway to spare.**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-07-24 (session start)
- **Completed:** 2026-07-24
- **Tasks:** 3 (2 auto + 1 checkpoint)
- **Files modified:** 6 (generator/train.py, tests/test_train.py, train.py, results/phase3_loss_history.csv, results/phase3_loss_curve.png, results/phase3_checkpoint.pt)

## Accomplishments

- Assembled Phase 2's already-verified pieces (`sample_latent`, `make_bin_centers`, `compute_p_real`, `mmd2`) into a real training loop without any of the named assembly pitfalls (no stale QuantumLayer/optimizer rebuilt per-step, no frozen `z`, no wrong batch reduction that averages `q` before the kernel instead of averaging per-sample losses).
- Ran a real 300-epoch training run end-to-end with no errors, on the first attempt, at the planned starting hyperparameters (no LR escalation needed).
- Produced scripted, non-eyeballed evidence of a genuine decreasing trend via `decreasing_trend_check`.
- Cleared the July 25, 2026 stall-risk checkpoint named in PROJECT.md as the prior PennyLane track's failure point -- with two days of runway remaining, not at the deadline.

## Task Commits

Each task was committed atomically:

1. **Task 1: Build generator/train.py's reusable pieces and smoke-test them** - `c87ac42` (feat)
2. **Task 2: Run the real end-to-end training and produce results/ artifacts** - `c7a62b2` (feat)
3. **Task 3: checkpoint:human-verify** - approved by owner after a self-explanation correction (see below); no code commit (checkpoint only)

**Plan metadata:** (this commit, to follow)

## Files Created/Modified

- `generator/train.py` - `build_generator()`, `train_step()` (batch-averaged MMD^2 step), `decreasing_trend_check()`
- `tests/test_train.py` - smoke test (5-iteration, batch=4 regression guard) + 3 synthetic `decreasing_trend_check` unit tests
- `train.py` - root entrypoint mirroring `quickstart.py`'s flat style; hardcoded constants, builds once, loops 300 epochs, writes `results/` artifacts, prints the scripted verdict
- `results/phase3_loss_history.csv` - per-epoch loss log from the real run
- `results/phase3_loss_curve.png` - loss-vs-epoch plot from the real run
- `results/phase3_checkpoint.pt` - trained `QuantumLayer` state_dict from the real run

## Decisions Made

- **lr=0.01 kept, no escalation needed.** The plan anticipated MMD^2 gradients might be small-magnitude enough that a first attempt at lr=0.01 could show a flat curve, requiring escalation to lr=0.05 then lr=0.1 (03-RESEARCH.md Open Question 2). The first real run at lr=0.01 already passed `decreasing_trend_check` (62% relative drop, `passed=True`), so no escalation was exercised. Documented inline in `train.py` next to the `LR` constant per decision-log discipline.
- **Batch-averaging strategy validated in practice.** DESIGN_DECISIONS.md's 2026-07-24 entry chose batch~16-32 per-sample-MMD^2-averaging over batch=1 based on literature (Liu & Wang 2018; Li et al. 2015) predicting a less noisy curve. This run's clean, statistically significant negative slope (p≈1e-128) is the first empirical confirmation that choice paid off for this project specifically, not just in theory.

## Deviations from Plan

None - plan executed exactly as written. No LR escalation, no bug fixes, no missing-critical additions were required during Tasks 1-2.

## Issues Encountered

**Self-explanation checkpoint required a real correction (this is the load-bearing detail for this checkpoint, per this project's CLAUDE.md self-explanation-checkpoint and "push back" rules -- documented plainly, not glossed over):**

Per Task 3's `<how-to-verify>` step 3, the owner was asked to explain `train_step`'s batch-averaging mechanism unaided.

- **First attempt (incorrect):** "mmd loss being the sum of z strings" -- this conflated the current project's continuous latent-noise `z` (a real-valued input vector to the QuantumLayer) with a prior project's (`iqp-mmd-barren-plateau`) binary-bitstring MMD kernel over Hamming distance. The two are architecturally different: this project's `mmd2` compares two continuous probability distributions over K=400 real-valued bin-centers via a Gaussian kernel (Euclidean distance), not bitstrings.
- **Correction (in conversation):** Clarified that `z` is latent noise input (not a bitstring), `mmd2` operates on probability-vector outputs over fixed bin-centers, and the batch-averaging step is variance reduction on the gradient estimate for a single shared circuit parameter set theta -- not a search or comparison across multiple different parameter sets.
- **Second attempt (confirmed accurate, after refinement):** "we are trying to minimize the distance between the two distributions... by averaging the sample distances, we tweak the parameters to get closer to [minimizing MMD^2 against] p_real" -- refined in dialogue to state explicitly that there is one shared theta across the batch, and averaging the 32 per-sample `mmd2` losses gives a less noisy gradient estimate for the single step that updates theta (gradient of a mean = mean of gradients).
- **Owner's explicit confirmation** that both GEN-06 success criteria are genuinely met by this specific run (not just "the script ran"): (1) the training loop ran to completion without errors; (2) the loss curve shows a real, observable decreasing trend, confirmed via the scripted `decreasing_trend_check` (not eyeballed) -- `passed=True`, 62% relative drop, negative slope at ~0 p-value.
- **Owner's final response:** "Yes, that makes sense" -- checkpoint approved after the corrected explanation, not on the first attempt.

This is exactly the kind of first-attempt gap the project's CLAUDE.md self-explanation-checkpoint rule exists to catch: the owner did not understand the batch-averaging mechanism unaided on the first pass, required one correction distinguishing this project's continuous-distribution MMD from a prior project's bitstring MMD, and then explained it correctly. Recorded here plainly rather than reported as a clean first-pass approval.

## Real training run evidence (verbatim `decreasing_trend_check` output)

```
{'slope': -8.590513079191068e-05, 'p_value': 1.0547316055240812e-128,
 'first_mean': 0.0383556650330623, 'last_mean': 0.014556273818016052,
 'relative_drop': 0.62049220615863, 'passed': True}
GEN-06 decreasing-trend check: PASS
```

- Full `pytest tests/` suite: 28/28 passed (Phase 2's 24 tests + Phase 3's 4 new tests), no regressions.
- `train.py` exited 0 on the real 300-epoch run.
- `results/phase3_loss_history.csv` (7594 bytes), `results/phase3_loss_curve.png` (29515 bytes), `results/phase3_checkpoint.pt` (3125 bytes) all present and non-empty.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- GEN-06 is met: a real, working, end-to-end training run exists with checked-in evidence, achieved 2026-07-24 (before the July 25, 2026 stall-risk deadline named in PROJECT.md). The historical PennyLane-track stall pattern was not repeated.
- `results/phase3_checkpoint.pt` (trained QuantumLayer weights) and `results/phase3_loss_history.csv` are available as inputs for Phase 4 (evaluation/benchmarking against the real circles data, e.g. visualizing generated samples vs. real rings).
- No blockers. Open item for future phases: the loss trend is real but the plan did not require (nor did this run assess) whether the *generated distribution itself* visually/qualitatively matches the two-ring structure -- that is Phase 4's job, not a gap in this plan's scope.

---
*Phase: 03-end-to-end-training-run*
*Completed: 2026-07-24*
