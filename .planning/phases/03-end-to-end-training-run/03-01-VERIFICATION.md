---
phase: 03-end-to-end-training-run
verified: 2026-07-24T17:07:04Z
status: passed
score: 6/6 must-haves verified
---

# Phase 3: End-to-End Training Run Verification Report

**Phase Goal:** The generator trains end-to-end on real data with a loop that measurably decreases MMD — the explicit July 25, 2026 stall-risk checkpoint named in PROJECT.md.
**Verified:** 2026-07-24T17:07:04Z
**Status:** passed
**Re-verification:** No — initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `train.py` runs to completion (exit code 0) using the QuantumLayer generator, precomputed p_real, and the MMD² loss from Phase 2 — no exceptions | ✓ VERIFIED | `results/phase3_loss_history.csv` contains 300 real epoch rows written by `train.py`'s post-loop artifact-write code; `pytest tests/` (28/28, including `test_train_step_smoke_runs_without_error_and_losses_finite`) passes, independently re-run, not taken from SUMMARY.md |
| 2 | QuantumLayer and Adam optimizer constructed exactly once, outside the epoch loop | ✓ VERIFIED | `train.py` lines 31-36 build `centers`, `x_train`, `p_real`, `kernel_matrix`, `quantum_layer`, `optimizer` before the `for epoch in range(EPOCHS)` loop at line 39; nothing in `train_step` (generator/train.py) constructs a QuantumLayer or optimizer |
| 3 | Every training step draws a fresh batch of z via `sample_latent(batch_size)` — never frozen/cached | ✓ VERIFIED | `generator/train.py:26` — `z = sample_latent(batch_size)` called inside `train_step`, which is invoked once per epoch inside the loop; no caching/closure over a fixed `z` |
| 4 | Each step's loss is the mean of per-sample `mmd2(p_real, q_i, K)` across the batch — not batch=1, not average-then-compare q | ✓ VERIFIED | `generator/train.py:28-31` — `torch.stack([mmd2(p_real, q_batch[i], kernel_matrix) for i in range(batch_size)]).mean()`; `q_batch` is never averaged before the `mmd2` call. Matches DESIGN_DECISIONS.md's 2026-07-24 entry ("average per-sample MMD² losses across the batch ... never average q into one vector before calling mmd2") verbatim |
| 5 | The loss curve shows a real, observable decreasing trend across epochs, verified by `decreasing_trend_check()` — not eyeballed | ✓ VERIFIED | Independently recomputed `decreasing_trend_check()` on the actual checked-in CSV (not the SUMMARY's printed log): `slope=-8.59e-05, p_value≈1.05e-128, relative_drop=0.620, passed=True` — exact match to SUMMARY.md's claimed numbers. `results/phase3_loss_curve.png` visually confirms a clean monotonic decline from ~0.042 to ~0.014 over 300 epochs, plateauing near epoch 220 |
| 6 | `results/` contains the loss history CSV, loss curve PNG, and trained checkpoint from a real run — checked-in evidence, not console output | ✓ VERIFIED | All three files exist, non-empty, and committed (`git status` clean): `phase3_loss_history.csv` (7594 bytes, 301 lines incl. header), `phase3_loss_curve.png` (29515 bytes, valid PNG), `phase3_checkpoint.pt` (3125 bytes, loads via `torch.load` into an `OrderedDict` with two non-trivial trained parameter tensors `LI_simple`/`RI_simple`, shape `[110]` each) |

**Score:** 6/6 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `generator/train.py` | `build_generator`, `train_step`, `decreasing_trend_check` | ✓ VERIFIED | 62 lines, all three exported with correct signatures, no stub patterns, imported and used by both `train.py` and `tests/test_train.py` |
| `tests/test_train.py` | smoke run + 3 `decreasing_trend_check` unit tests | ✓ VERIFIED | 49 lines, 4 test functions, all pass under `pytest` |
| `train.py` | root entrypoint, quickstart.py style | ✓ VERIFIED | 71 lines, builds once/loops/writes artifacts/prints verdict, no CLI flags per project scope discipline |
| `results/phase3_loss_history.csv` | per-epoch loss log | ✓ VERIFIED | 300 real rows, values decrease monotonically with noise (0.042→0.014) |
| `results/phase3_loss_curve.png` | loss-vs-epoch plot | ✓ VERIFIED | Valid 640x480 PNG, visually shows clean decreasing trend |
| `results/phase3_checkpoint.pt` | QuantumLayer state_dict | ✓ VERIFIED | Loads cleanly, contains real trained parameter tensors |

### Key Link Verification

| From | To | Via | Status | Details |
|------|----|----|--------|---------|
| `train.py` | `generator/train.py` | `from generator.train import build_generator, train_step, decreasing_trend_check` | ✓ WIRED | Line 12, all three used in `main()` |
| `train_step` | `generator/noise.py sample_latent` | fresh z every call | ✓ WIRED | `z = sample_latent(batch_size)` inside `train_step`, called once per epoch |
| `train_step` | `generator/mmd.py mmd2` | per-sample MMD² loss, averaged | ✓ WIRED | `torch.stack([mmd2(...) for i in range(batch_size)]).mean()` |
| `train.py` | `results/phase3_*` | artifact writes after real run | ✓ WIRED | CSV write, matplotlib savefig, `torch.save` all execute after the 300-epoch loop, all three files present on disk with plausible sizes/content |

### Requirements Coverage

| Requirement | Status | Blocking Issue |
|-------------|--------|-----------------|
| GEN-06 (Training loop runs end-to-end, producing a real MMD-decreasing run) | ✓ SATISFIED | None — verified via independent recomputation of `decreasing_trend_check` against the checked-in CSV, not SUMMARY claims |

Note: `.planning/REQUIREMENTS.md` and `.planning/ROADMAP.md` checkboxes for GEN-06/Phase 3 are still unchecked/"Pending" as of this verification — this is a documentation-sync task for the orchestrator, not a code gap.

### Anti-Patterns Found

None. No TODO/FIXME/placeholder patterns, no empty returns, no stub handlers in `generator/train.py`, `train.py`, or `tests/test_train.py`.

### Human Verification Required

None required for phase-goal achievement — the human-verify checkpoint (Task 3 in 03-01-PLAN.md) was already completed and documented in 03-01-SUMMARY.md: the owner was asked to explain `train_step`'s batch-averaging mechanism unaided, gave an incorrect first answer (conflating this project's continuous-distribution MMD with a prior project's bitstring MMD), was corrected, then gave a confirmed-accurate second explanation before approving. This self-explanation checkpoint is a project-specific (CLAUDE.md) gate, already satisfied and documented — not re-litigated here.

### Gaps Summary

None. All 6 observable truths verified against the actual codebase (not SUMMARY.md claims): the training loop is correctly assembled (QuantumLayer/optimizer built once, fresh z every step, per-sample-average batch reduction matching the owner-confirmed DESIGN_DECISIONS.md entry), a real 300-epoch run completed and its artifacts are checked in, and an independent recomputation of `decreasing_trend_check` on the raw CSV data reproduces the SUMMARY's claimed slope/p_value/relative_drop numbers exactly. `pytest tests/` (28/28) passes with no regressions. The July 25, 2026 stall-risk checkpoint (Phase 3 success criterion 3) is met one day ahead of the deadline (today: 2026-07-24).

---

*Verified: 2026-07-24T17:07:04Z*
*Verifier: Claude (gsd-verifier)*
