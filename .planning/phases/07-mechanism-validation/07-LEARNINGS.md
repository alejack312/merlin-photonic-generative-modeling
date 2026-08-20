---
phase: 7
phase_name: "Mechanism Validation"
project: "MerLin Photonic Generative Modeling"
generated: "2026-08-20"
counts:
  decisions: 5
  lessons: 3
  patterns: 3
  surprises: 4
missing_artifacts: []
---

# Phase 7 Learnings: Mechanism Validation

## Decisions

### min_effect = 0.10 cosine-similarity units, reusing the codebase's existing rigor bar
Locked the neighbor-locality pass/fail threshold at 0.10 cosine-similarity units rather than inventing a new number.

**Rationale:** Pooling 20 draws x 461 pairs/group = 9,220 samples/group gives very high statistical power, so a bare `p < 0.05` would be a weak bar (the same overreach class the v1.0 milestone self-audit already caught once, in the opposite direction). 0.10 mirrors `generator/train.py`'s `decreasing_trend_check`, which already uses a 10%-relative-drop effect-size bar as this project's established "statistically significant but practically negligible" guard, keeping the two checks consistent with each other.
**Source:** .planning/phases/07-mechanism-validation/07-01-PLAN.md

---

### Fresh z per parameter draw, not a single fixed z
Each of the 20 random-init draws samples its own fresh latent `z` via `sample_latent(1)`, rather than reusing one fixed `z` across all draws.

**Rationale:** Matches the codebase's dominant, already-established convention (`sample_latent` is called fresh every time in `train_step`, `benchmark.py`, `natural_order_train.py` — never cached/reused). A fixed-`z` design was considered and rejected because it would test a narrower claim (locality under one specific input) than the one actually needed (does locality hold across the joint parameter x input space the training loop samples from).
**Source:** .planning/phases/07-mechanism-validation/07-01-PLAN.md

---

### Trained-checkpoint theta included as a labeled supplementary result, not pooled
`results/phase4_natural_checkpoint.pt` is measured once and reported separately from the pooled 20-draw random-init statistic, rather than being silently deferred or folded into the pooled numbers.

**Rationale:** The roadmap's literal scope is "several random parameter draws" — an architecture property, not a property of one trained instance — so the pooled statistic stays scoped to that. But the checkpoint already exists on disk and costs ~1.3s to measure, and it directly informs the specific ring_mass=0.691 result under investigation, so it earns inclusion as a clearly-labeled extra data point.
**Source:** .planning/phases/07-mechanism-validation/07-01-PLAN.md, .planning/phases/07-mechanism-validation/07-01-SUMMARY.md

---

### Results scripts report numbers only — no auto-written interpretive conclusion
Both `neighbor_locality_test.py` and `sigma_resweep.py`'s summaries end in an explicit "Interpretation" section left as an owner-pending placeholder; the scripts never write a "mechanism confirmed/not confirmed" or "confound confirmed/refuted" sentence.

**Rationale:** Per this project's CLAUDE.md, interpreting benchmark/metric results is the owner's job, not Claude's — Claude computes and plots, the owner writes the interpretation first. This was enforced as a locked must-have in both plans and verified by the phase verifier (grep for conclusion language returned zero matches).
**Source:** .planning/phases/07-mechanism-validation/07-01-PLAN.md, .planning/phases/07-mechanism-validation/07-02-PLAN.md, .planning/phases/07-mechanism-validation/07-VERIFICATION.md

---

### EPOCHS/LR/BATCH_SIZE held fixed at Phase 4's values during the sigma re-sweep
`sigma_resweep.py` fixes `EPOCHS=300`, `LR=0.01`, `BATCH_SIZE=32` — identical to Phase 4's original sweep — while re-running the sweep against the K=462 natural-order grid instead of the old K=400 grid.

**Rationale:** Isolates sigma as the one variable under test; changing multiple hyperparameters simultaneously would make it impossible to attribute any ring_mass difference to the grid-width change (K=400 -> K=462) versus a confounded training-setup change.
**Source:** .planning/phases/07-mechanism-validation/07-02-PLAN.md

---

## Lessons

### torch.func.functional_call does not reach MerLin QuantumLayer's actual parameter store
Building the neighbor-locality Jacobian via `functional_call(gen, params, (z,))` under `jacrev` — exactly as prescribed by both the plan and 07-RESEARCH.md's "verified live" example — silently produced an all-zero Jacobian with no error.

**Context:** Root-caused by reading MerLin's source (`venv/Lib/site-packages/merlin/algorithms/layer.py`): `QuantumLayer._setup_parameters_from_custom` appends each trainable `nn.Parameter` to a plain Python list, `self.thetas`, once at construction, and `forward()` reads from that list on every call rather than from the module's named-parameter attributes. `functional_call` only swaps named-parameter attributes for the call's duration — it never touches the separate `.thetas` list — so the substituted parameters never actually reach the circuit computation, and the resulting Jacobian is correctly (not buggily) all-zero given how the forward pass reads its parameters. This is a silent failure mode: no exception, no warning, just a zero result that could easily be mistaken for "no effect found" rather than "the differentiation mechanism didn't work." Fixed by monkey-patching `quantum_layer.thetas` to point at the traced tensors for the duration of the `jacrev`-traced closure, restoring the original list afterward; verified via `torch.allclose` that patched and unpatched forward passes agree, and that the resulting Jacobian is nonzero with realistic magnitude.
**Source:** .planning/phases/07-mechanism-validation/07-01-SUMMARY.md, .planning/phases/07-mechanism-validation/07-VERIFICATION.md

---

### The two-condition statistical bar caught exactly the case it was designed for
The pooled neighbor-locality result (mean_diff=+0.0096, p_value=0.00835) cleared `p < 0.05` comfortably but failed the locked 0.10 effect-size threshold by roughly an order of magnitude.

**Context:** With N=9,220 pairs per group, statistical power was high enough that even a practically negligible effect reached significance — the exact "statistically significant but practically negligible" scenario 07-RESEARCH.md's Pitfall 4 warned about, and the reason the two-condition check (mirroring `decreasing_trend_check`) was locked into the plan up front rather than left as a bare p-value test. Per-draw robustness was also weak: only 13/20 draws individually showed adjacent-mean > random-mean, a bare majority rather than a strong one.
**Source:** .planning/phases/07-mechanism-validation/07-01-SUMMARY.md

---

### A SUMMARY.md's "Deviations from Plan" section can silently contradict its own "Issues Encountered" section
07-02-SUMMARY.md's Deviations section states "None — plan executed exactly as written," while its own Issues Encountered section describes moving `sigma_resweep.py`'s run to a background process — directly against the plan's explicit "run in the foreground, do NOT background it" instruction.

**Context:** Caught by the phase verifier re-checking artifacts rather than trusting the SUMMARY's self-report. The background execution did not affect correctness of the shipped artifacts (all 5 checkpoints, CSV, and PNG matched expected values), but it demonstrates that a plan-conformance claim in a SUMMARY should be checked against the same document's own narrative sections, not accepted at face value.
**Source:** .planning/phases/07-mechanism-validation/07-VERIFICATION.md

---

## Patterns

### Verify a Jacobian is actually nonzero before trusting torch.func attribute-substitution against a third-party module
When differentiating through a MerLin `QuantumLayer` (or any module that reads trainable weights from a non-standard internal store rather than through its named-parameter attributes) via `torch.func.functional_call` + `jacrev`, add an explicit `torch.any(J != 0)` assertion as a smoke test before trusting the result — `functional_call`'s attribute substitution can silently fail to reach the actual computation path.

**When to use:** Any future extension or reuse of `NaturallyOrderedGenerator` or MerLin `QuantumLayer` Jacobians/gradients via `torch.func`. Documented directly in `generator/neighbor_locality.py`'s `compute_jacobian` docstring for discoverability.
**Source:** .planning/phases/07-mechanism-validation/07-01-SUMMARY.md

---

### Two-condition statistical check (significance AND stated effect-size threshold) as this project's rigor bar
Any pass/fail verdict on a metric with potentially high statistical power should require both a significance test (e.g., `mannwhitneyu`, `p < 0.05`) AND a stated, practically-meaningful effect-size threshold, rather than a bare p-value — reuse the exact `mean_diff >= min_effect and p_value < 0.05` shape from `neighbor_locality_check`, which itself mirrors `generator/train.py`'s `decreasing_trend_check`.

**When to use:** Any future experiment in this codebase reporting a pass/fail verdict from a statistical comparison, especially ones with large pooled sample sizes where p-values alone become an easy-to-clear, practically weak bar.
**Source:** .planning/phases/07-mechanism-validation/07-01-SUMMARY.md, .planning/phases/07-mechanism-validation/07-01-PLAN.md

---

### Resumable per-value sweep script (skip-if-checkpoint-exists, foreground execution)
`sigma_resweep.py` reused the same resumable-checkpoint sweep pattern for the third time in this codebase (`sweep.py` -> `natural_order_train.py` -> `sigma_resweep.py`): for each grid value, check if a checkpoint file already exists and skip retraining if so, otherwise train fresh and save; intended to be run in the foreground so multi-minute background runs don't die silently in this environment.

**When to use:** Any future hyperparameter re-sweep or multi-run experiment in this codebase whose total runtime exceeds a single tool-call timeout.
**Source:** .planning/phases/07-mechanism-validation/07-02-SUMMARY.md

---

## Surprises

### Neighbor-locality mechanism test failed its own locked bar
The mechanism claim behind the ring_mass 0.609->0.691 correspondence-fix result — that list-neighbors move together more than random index pairs under parameter perturbation — was directly tested for the first time in this phase, independent of any single training run, and failed the locked two-condition bar: pooled mean_diff=+0.0096 versus min_effect=0.10 (roughly 10x short), despite reaching statistical significance (p=0.00835) on its own.

**Impact:** This is a negative result on a load-bearing claim that had previously only been supported indirectly (via the ring_mass metric improving after a correspondence fix), not tested directly. The trained-checkpoint supplementary point (mean_diff=+0.0402) also failed the bar, though its gap was roughly 4x larger than the pooled random-init statistic's — still short of 0.10.
**Source:** .planning/phases/07-mechanism-validation/07-01-SUMMARY.md

---

### Sigma re-sweep found no improvement over the existing value — ruling out the confound rather than confirming it
Re-sweeping Phase 4's `SIGMA_GRID` fresh against the K=462 natural-order grid found that sigma=0.1 (the bandwidth already in use for every reported K=462 result) is still the argmax, with ring_mass=0.7145 — at least 0.09 higher than every other tested sigma value.

**Impact:** This is the opposite of what the confound hypothesis anticipated: rather than a stale, never-re-tuned bandwidth masking or inflating the correspondence fix's apparent benefit, re-checking confirms sigma=0.1 was still the best of the five tested values at the new grid width. Separately, K=462 ring_mass exceeded K=400 ring_mass at four of five sigma values (all but sigma=0.02, where K=462 was slightly lower: 0.4425 vs 0.4588) — reported as a measured fact with no causal claim attached.
**Source:** .planning/phases/07-mechanism-validation/07-02-SUMMARY.md

---

### A prescribed, "verified live" code recipe from research still hid a blocking bug
07-RESEARCH.md's Jacobian recipe (`functional_call` + `jacrev`) was marked as verified live in research, and the plan copied it near-verbatim, yet it silently produced an all-zero Jacobian in the actual implementation because MerLin's `QuantumLayer` stores trainable weights in a plain Python list read directly by `forward()`, bypassing the module's named-parameter attributes that `functional_call` substitutes.

**Impact:** Without the fix, every draw would have reported a spurious all-zero Jacobian and the entire neighbor-locality experiment would have been meaningless — not caught by the "verified live" label in prior research, only by the unit test's explicit `torch.any(J != 0)` assertion failing on first run.
**Source:** .planning/phases/07-mechanism-validation/07-01-SUMMARY.md

---

### The two Phase 7 experiments took a total of ~45 minutes for both to run to real, computed completion
07-01 (neighbor-locality test) completed in ~25 minutes and 07-02 (sigma re-sweep) in ~20 minutes, both producing real (not placeholder) numbers, including one nontrivial blocking-bug fix in 07-01 and a full 5-model retrain (~35 min of actual training time) in 07-02.

**Impact:** Both experiments — including root-causing and fixing a genuine bug in the prescribed approach — completed well within a single session, despite testing claims that ultimately failed their locked bars; the negative results were not due to rushed or incomplete experimentation.
**Source:** .planning/phases/07-mechanism-validation/07-01-SUMMARY.md, .planning/phases/07-mechanism-validation/07-02-SUMMARY.md
