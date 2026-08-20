---
phase: 5
phase_name: "Benchmarking"
project: "MerLin Photonic Generative Modeling"
generated: "2026-08-20"
counts:
  decisions: 5
  lessons: 3
  patterns: 3
  surprises: 3
missing_artifacts: []
---

# Phase 5 Learnings: Benchmarking

## Decisions

### Keep SIGMA=0.1 unchanged from Phase 4 training
Reused the Phase 4 training kernel bandwidth (SIGMA=0.1) for the benchmark MMD² computation rather than re-tuning it for the benchmark specifically.

**Rationale:** Direct comparability with all Phase 4 numbers takes priority over finding a possibly "more defensible" benchmark-specific bandwidth.
**Source:** 05-01-PLAN.md (Task 1), 05-01-SUMMARY.md key-decisions

---

### Reuse the fixed train/test split unchanged, vary only the latent draw
`load_circles_data()`'s existing fixed `random_state=42` 80/20 split was reused unchanged rather than re-splitting across multiple seeds. `p_real`/`p_real_test` are deterministic once the split is fixed, so the only intended source of run-to-run variance is the latent `z`, which `N_DRAWS=20` already captures.

**Rationale:** Avoids conflating two sources of variance (split randomness vs. latent randomness) in a single mean±std statistic — keeps the statistic's meaning precise.
**Source:** 05-01-SUMMARY.md key-decisions

---

### Timed retrain writes to a scratch checkpoint, never the reference checkpoint
`benchmark_timing.py` writes to `results/phase5_timed_checkpoint.pt`, never to `results/phase4_natural_checkpoint.pt`, even though it reruns the exact same training procedure.

**Rationale:** Getting a real measured wall-clock number requires an actual fresh training run, but that must not risk corrupting the Phase 4 reference artifact that other scripts/analyses depend on.
**Source:** 05-01-PLAN.md (Task 2), 05-01-SUMMARY.md key-decisions

---

### BMK-02 fallback path (qualitative comparison) used instead of a matched numeric benchmark
Compared against MerLin's photonic QGAN reproduction (paper #16) qualitatively (architecture, loss type, dataset domain), explicitly flagged as "Fallback path used — no matched numeric comparison was computed," rather than computing the same held-out MMD² statistic on the QGAN reproduction's output.

**Rationale:** The QGAN reproduction trains on 8x8 grayscale `optdigits` image patches via adversarial loss, not the circles point-cloud dataset — its image-pixel output space has no defined mapping onto this project's K=462 2D bin-center MMD metric without inventing new work, which was explicitly deferred to BMK-03 (out of scope for Phase 5).
**Source:** 05-CONTEXT.md (QGAN comparison scope), 05-01-PLAN.md (Task 3), 05-01-SUMMARY.md key-decisions

---

### Floor baseline row uses empty ring/gap fields, not zeros or N/A placeholders
In `results/phase5_benchmark_metrics.csv`, the `floor` row (real-train-vs-real-test MMD²) leaves `ring_mass_mean`/`ring_mass_std`/`gap_mass_mean`/`gap_mass_std` as empty strings rather than 0 or a placeholder, since ring/gap metrics conceptually don't apply to a p_real-vs-p_real comparison (no generator output involved).

**Rationale:** Avoids a numeric-looking but meaningless value (e.g., 0) being misread as an actual measurement for a metric that doesn't apply to this row.
**Source:** 05-01-PLAN.md (Task 1)

---

## Lessons

### Repo-root `python` is not the project's venv interpreter
Running `python benchmark.py` from the repo root failed with `ModuleNotFoundError: No module named 'merlin'` on the first attempt; the project's venv Python must be invoked directly (`./venv/Scripts/python.exe`).

**Context:** Encountered during Task 1/2 execution. Resolved by using the venv path explicitly — noted as an environment-invocation detail specific to this session, not a repo convention requiring a CLAUDE.md update.
**Source:** 05-01-SUMMARY.md Issues Encountered

---

### Long-running training scripts need backgrounding/resumability in this environment
`benchmark_timing.py`'s fresh 300-epoch retrain took ~7 minutes (425.93s), exceeding the single 120s foreground command budget available in this environment.

**Context:** Ran via `run_in_background: true`, polled the output file until epoch-300/param-count lines appeared. Consistent with a precedent noted in 05-RESEARCH.md from Phase 4's sweep scripts, which had the same constraint.
**Source:** 05-01-SUMMARY.md Issues Encountered

---

### Verifying a stochastic script's output requires distinguishing which parts should be stable vs. variable across reruns
On live re-verification, `benchmark.py` was re-run and reproduced trained MMD²≈0.0125±0.0003 matching the committed CSV, while the untrained baseline is expected to vary run-to-run (random init) by design. `benchmark_timing.py` (the ~7-minute script) was not re-run live; instead its logic was read line-by-line against the CSV, and the presence of the dated scratch checkpoint file on disk was used as independent evidence the script had actually executed (not hand-written output).

**Context:** From the verification pass — this is a budget-aware verification technique: cheap deterministic re-runs get re-executed live, expensive stochastic-but-slow scripts get logic-cross-checked plus artifact-existence evidence instead.
**Source:** 05-VERIFICATION.md Gaps Summary

---

## Patterns

### Post-hoc benchmark script pattern
Benchmark scripts load a frozen checkpoint, call `.eval()` and wrap everything in `torch.no_grad()`, with no optimizer or backward pass. Repeated latent-`z` draws (here N=20) produce a distribution of a scalar metric (MMD²) which is summarized as mean±std, rather than reporting a single deterministic run.

**When to use:** Any phase that needs to honestly quantify a trained model's stochastic-output performance without retraining, especially when the underlying generator is itself parameterized by a random latent input.
**Source:** 05-01-SUMMARY.md tech-stack patterns

---

### Timed-retrain-to-scratch-checkpoint pattern
When a script's sole added purpose is to measure something training-time-only (wall-clock time, parameter count) that no prior script recorded, rerun training but always to a scratch checkpoint path distinct from any documented reference checkpoint that other scripts/docs depend on.

**When to use:** Any time a later phase needs a training-time metric that an earlier phase's training run didn't capture, and re-running training is the only way to get a real (not estimated) number.
**Source:** 05-01-SUMMARY.md tech-stack patterns

---

### Bracket a headline metric with a floor and a ceiling/baseline for honest interpretation
Report the trained result alongside two reference points: an untrained/random-parameter baseline (shows training helped) and a best-possible/floor baseline (shows the remaining gap to ideal). Assert the expected ordering (floor < trained < untrained) as a sanity check, and treat a violation as a reportable anomaly rather than something to silently fix.

**When to use:** Any benchmarking task reporting a single accuracy/quality metric for a trained model — prevents a bare number from being over- or under-interpreted without context.
**Source:** 05-01-PLAN.md (Task 1 done-criteria), 05-CONTEXT.md (Held-out MMD statistic)

---

## Surprises

### Trained generator's held-out MMD² landed very close to the real-vs-real floor
Trained MMD²=0.0125±0.0003 was only ~0.0011 above the floor MMD²=0.0114 (real-train-vs-real-test), and about 3x lower than the untrained baseline (0.0360±0.0048) — i.e., by the MMD² metric specifically, the trained generator is close to "as good as real data," even though Phase 4's ring/gap visual-quality metrics (ring_mass=0.6833, gap_mass=0.0514, re-measured) still show it falling short of two distinct rings (GEN-07 not met).

**Impact:** Confirms and sharpens the honest-framing requirement from 05-CONTEXT.md/05-01-PLAN.md — a good MMD² number alone would misleadingly imply success; it had to be explicitly paired with the ring/gap metrics to avoid overstating the result. This divergence between a favorable MMD² and an unfavorable ring/gap outcome is itself a notable finding about the metric's limitations for this generative task.
**Source:** 05-01-SUMMARY.md Accomplishments, 05-VERIFICATION.md Observable Truths

---

### Anomaly check on MMD ordering did not trigger
The plan's built-in anomaly check (report, don't silently fix, if trained MMD² is not lower than untrained MMD²) did not fire — the correct ordering held on the first run.

**Impact:** No deviation from plan was needed; execution completed in a single pass with no rework, at ~25 minutes total (dominated by the ~7-minute timed retrain in Task 2).
**Source:** 05-01-SUMMARY.md Deviations from Plan, Performance

---

### Live re-verification reproduced the committed metric within stochastic tolerance
Re-running `benchmark.py` during verification (not just trusting SUMMARY.md's claims) reproduced trained MMD²≈0.0125±0.0003 matching the committed CSV, confirming the trained-generator number is stable across reruns (fixed checkpoint) while only the untrained baseline is expected to vary.

**Impact:** Gave high confidence the reported numbers reflect actual script behavior rather than hand-edited or stale CSV values; the verifier explicitly restored the CSV to its git-committed state afterward since the re-run was for verification only, avoiding an unintended diff.
**Source:** 05-VERIFICATION.md Gaps Summary
