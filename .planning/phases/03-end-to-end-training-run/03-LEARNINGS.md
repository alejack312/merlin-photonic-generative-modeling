---
phase: 3
phase_name: "End-to-End Training Run"
project: "MerLin Photonic Generative Modeling"
generated: "2026-08-20"
counts:
  decisions: 3
  lessons: 3
  patterns: 3
  surprises: 3
missing_artifacts: []
---

# Phase 3 Learnings: End-to-End Training Run

## Decisions

### Batch-averaged per-sample MMD² as the training step objective
`train_step` draws a fresh `z = sample_latent(batch_size)` every call, computes `q_batch = quantum_layer(z)`, then stacks per-row `mmd2(p_real, q_batch[i], kernel_matrix)` and calls `.mean()` on the stack before `backward()`. Averaging `q_batch` into a single vector before calling `mmd2` was explicitly rejected as a different (wrong) training objective.

**Rationale:** This is the owner-confirmed batch-averaging strategy from DESIGN_DECISIONS.md (2026-07-24 entry), grounded in literature (Liu & Wang 2018; Li et al. 2015) predicting a less noisy gradient estimate than batch=1. It is variance reduction on the gradient for one shared circuit parameter set theta — not a search across multiple parameter sets.
**Source:** .planning/phases/03-end-to-end-training-run/03-01-PLAN.md, 03-01-SUMMARY.md

---

### No CLI flags in train.py — hardcoded constants, mirrors quickstart.py style
Root `train.py` uses hardcoded constants (`SIGMA=0.1`, `BATCH_SIZE=32`, `EPOCHS=300`, `LR=0.01`) near the top of the file instead of argparse/CLI flags.

**Rationale:** Matches the project's existing `quickstart.py` flat script style and the project CLAUDE.md's scope-discipline rule against speculative flexibility/config options.
**Source:** .planning/phases/03-end-to-end-training-run/03-01-PLAN.md

---

### lr=0.01 kept without escalation
The plan pre-authorized an LR escalation path (0.01 → 0.05 → 0.1, max 2 additional tries) in case MMD² gradients were too small-magnitude to show a decreasing trend at lr=0.01. The first real run at lr=0.01 already passed `decreasing_trend_check` (62% relative drop), so escalation was never exercised.

**Rationale:** The starting LR came from `quickstart.py`'s already-working precedent; no need to deviate once it worked on the first attempt. Documented inline in `train.py` next to the `LR` constant per decision-log discipline.
**Source:** .planning/phases/03-end-to-end-training-run/03-01-SUMMARY.md

---

## Lessons

### Self-explanation checkpoints catch real gaps, not just formalities
At the human-verify checkpoint, the owner's first attempt to explain `train_step`'s mechanism ("mmd loss being the sum of z strings") conflated this project's continuous-distribution MMD (Gaussian kernel over K=400 real-valued bin-centers) with a *different, prior* project's (`iqp-mmd-barren-plateau`) binary-bitstring MMD over Hamming distance.

**Context:** The correction distinguished: `z` is continuous latent noise (not a bitstring); `mmd2` compares two continuous probability distributions; batch-averaging reduces gradient-estimate variance for one shared theta, not a search over multiple parameter sets. The owner's second attempt was confirmed accurate. This validates the project CLAUDE.md's self-explanation-checkpoint rule as substantive rather than ceremonial.
**Source:** .planning/phases/03-end-to-end-training-run/03-01-SUMMARY.md

---

### A clean assembly of already-verified components can still fail silently in subtle ways
The plan explicitly named three assembly pitfalls that would "run without erroring" while not actually training: rebuilding QuantumLayer/optimizer per-step (silently re-randomizing thetas / resetting optimizer state), using a frozen/cached `z` instead of a fresh draw per step, and averaging `q` before the kernel call instead of averaging per-sample losses.

**Context:** None of these pitfalls were hit in this run, but the plan's explicit call-out of them (and the verifier's independent line-by-line check of `train.py`/`generator/train.py` against each one) shows these are the realistic failure modes for "wiring together already-tested pieces" work — errors of silent incorrectness, not exceptions.
**Source:** .planning/phases/03-end-to-end-training-run/03-01-PLAN.md, 03-01-VERIFICATION.md

---

### Trend claims must be scripted, not eyeballed — reusable repo convention
`decreasing_trend_check(losses)` combines `scipy.stats.linregress` slope/p-value with a first-decile-vs-last-decile relative-drop threshold (>=10%) into a single `passed` boolean, replacing a visual read of the loss curve as evidence.

**Context:** The verifier independently recomputed this check directly from the checked-in CSV (not from SUMMARY.md's printed numbers) and got an exact match, confirming the check is reproducible evidence rather than a claim to trust.
**Source:** .planning/phases/03-end-to-end-training-run/03-01-SUMMARY.md, 03-01-VERIFICATION.md

---

## Patterns

### Build-once-loop-many for stateful training components
`QuantumLayer` and the Adam optimizer are constructed exactly once outside the epoch loop; only `train_step` runs inside the loop, drawing a fresh `z` each call.

**When to use:** Any training loop involving a stateful model + optimizer pair — rebuilding either inside the loop silently discards learned state or optimizer momentum while still appearing to "run."
**Source:** .planning/phases/03-end-to-end-training-run/03-01-PLAN.md, 03-01-VERIFICATION.md

---

### Scripted pass/fail check for trend claims (decreasing_trend_check)
A reusable pattern: combine a statistical trend test (linregress slope + p-value) with a magnitude test (relative drop between first and last deciles) into one function returning a dict with a boolean `passed` field, and print the full dict plainly regardless of outcome.

**When to use:** Any time a plot's "it looks like it's decreasing/converging" claim needs to become checkable evidence rather than a visual judgment call — established here as the standing convention for trend claims in this repo.
**Source:** .planning/phases/03-end-to-end-training-run/03-01-PLAN.md, 03-01-SUMMARY.md

---

### Never silently hide a failing verdict
The plan required `train.py` to print the full `decreasing_trend_check` dict and an explicit PASS/FAIL line even if `passed=False`, rather than raising an exception or omitting output on failure.

**When to use:** Any script whose job is to produce evidence for a go/no-go criterion — the failure path must be as visible as the success path.
**Source:** .planning/phases/03-end-to-end-training-run/03-01-PLAN.md

---

## Surprises

### First real run passed on the first attempt, no LR escalation needed
The plan anticipated a real risk (informed by 03-RESEARCH.md's Open Question 2) that MMD² gradients could be small-magnitude enough to produce a flat curve at lr=0.01, requiring up to two escalation attempts (lr=0.05, then 0.1). The very first 300-epoch run at lr=0.01 passed cleanly.

**Impact:** No rework was needed; the plan's contingency path was documented but never exercised. Reduced total task duration to ~35 minutes end-to-end.
**Source:** .planning/phases/03-end-to-end-training-run/03-01-SUMMARY.md

---

### The July 25 historical stall point was cleared a day early with a strongly significant result
This phase targeted GEN-06, the exact point where a prior self-directed project (PennyLane track) previously stalled. The run completed 2026-07-24 (one day ahead of the named deadline) with a statistically strong result: `slope=-8.59e-05, p_value≈1.05e-128, relative_drop=0.620, passed=True`.

**Impact:** The p-value (~1e-128) is far beyond what's needed to establish significance, indicating an unusually clean, low-noise decreasing trend for this run rather than a marginal pass — removing ambiguity about whether the checkpoint was genuinely met.
**Source:** .planning/phases/03-end-to-end-training-run/03-01-SUMMARY.md, 03-01-VERIFICATION.md

---

### Self-explanation checkpoint required a real correction, not a rubber stamp
Given the emphasis in the plan and project CLAUDE.md on this being a stall-risk checkpoint, the owner's first explanation attempt genuinely conflated concepts from a different prior project (binary-bitstring MMD vs. this project's continuous-distribution MMD) — this was not anticipated as a specific risk in the plan text itself but occurred in practice.

**Impact:** Confirms the self-explanation-checkpoint mechanism catches real gaps rather than passing automatically once code artifacts exist; the SUMMARY.md documents both the incorrect first attempt and the corrected second attempt in full rather than glossing over it.
**Source:** .planning/phases/03-end-to-end-training-run/03-01-SUMMARY.md
