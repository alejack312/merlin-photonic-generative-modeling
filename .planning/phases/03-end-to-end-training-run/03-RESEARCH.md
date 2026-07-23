# Phase 3: End-to-End Training Run - Research

**Researched:** 2026-07-24
**Domain:** Training-loop design for a MerLin `QuantumLayer` photonic generator against a fixed target distribution via closed-form MMD², on CPU, under a 1-day timeline
**Confidence:** MEDIUM-HIGH — stack/pitfalls are HIGH (verified directly against installed venv + Phase 2's already-tested code); the batch-reduction architecture question is a genuine, unresolved design decision that this research narrows to two named options with a recommendation, not something safe to silently lock

## Summary

Phase 2 already leaves every piece Phase 3 needs, verified and tested: `sample_latent(batch_size)`, `make_bin_centers()`, `compute_p_real()`, `gaussian_kernel_matrix()`/`mmd2()`, and — critically — `tests/test_mmd.py::test_mmd2_gradient_reaches_quantum_layer` already proves the exact gradient path end-to-end (`QuantumLayer.simple(input_size=10, output_size=400)` → `mmd2(P_REAL, q, K)` → `.backward()` → finite gradients on the circuit's `thetas`). Phase 3's job is almost entirely assembly: wrap that proven single-step pattern in a loop with an optimizer, run it enough times to show a real trend, and prove the trend is real rather than eyeballed.

The one substantive open design question is how a *batch* of latent draws becomes the single `q` that `mmd2()` compares against `p_real`. This project's Phase 1 architecture decision (`DESIGN_DECISIONS.md`) already establishes that **each individual `z` already produces a full, valid, correctly-normalized `(400,)` probability distribution** — not a single point, not a discrete sample. That means, unlike a classic MMD-GAN/GMMN (which computes MMD between two *sets of discrete samples*), there is no forced requirement to batch at all: `mmd2(p_real, quantum_layer(z)[0], K)` for one fresh `z` per step is already a complete, differentiable, correct training step, and it's the exact pattern the Phase 2 test already verified. The question is whether to also average across several `z`'s per step, and if so, at which point (before or after the `mmd2` call) — this changes what the trained circuit is actually being pushed toward, so it is flagged as an explicit decision for the owner/plan rather than resolved silently, per this project's CLAUDE.md ("training strategy" is listed as a non-shortcuttable decision).

External QCBM/MMD literature (Liu & Wang 2018 "Differentiable Learning of a Quantum Circuit Born Machine"; Li et al. 2015 "Generative Moment Matching Networks") consistently reports that **MMD-based generative training is noise-sensitive at small batch sizes** — batch=1 tends to produce visibly noisier, less monotonic loss curves. Given Phase 3's success criterion is specifically "observable decreasing trend, not flat, not diverging," this is directly load-bearing: training on a single fresh `z` per step (batch=1) is the *safest, already-tested* pattern for correctness, but the *riskiest* for producing a clean, defensible trend within one day of runway. The recommended default (see Open Questions) is a per-sample-loss-averaged batch of ~16–32, which is a strict generalization of the tested batch=1 pattern (loop/vectorize the same `mmd2` call across a batch and average the scalars) rather than a new, untested "average-then-compare" formulation.

**Primary recommendation:** Build one script (`train.py`, mirroring `quickstart.py`'s flat style) that: constructs `QuantumLayer.simple(input_size=10, output_size=400)` and its `Adam` optimizer once outside the loop; each epoch draws a fresh batch of `z` via `sample_latent(batch_size)`, forward-passes it through the (already-built) quantum layer to get `q_batch` of shape `(batch, 400)`, computes `mmd2(p_real, q_i, K)` per row and averages the scalars into one loss, then does the standard `zero_grad()/backward()/step()`; log the loss every epoch; at the end, run a scripted (not eyeballed) decreasing-trend check and save `results/` artifacts (loss history CSV, loss curve PNG, model checkpoint). Use `sigma=0.1` from the existing `SIGMA_GRID` (already used and proven to produce finite gradients in the Phase 2 test) as Phase 3's training bandwidth. Confirm the batch-reduction choice with the owner before locking the plan.

## Standard Stack

### Core
| Library | Version (installed) | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `merlinquantum` (`import merlin as ML`) | 0.4.0 | `QuantumLayer.simple()` generator, reused unchanged from Phase 2 | Already the project's framework |
| `torch` | 2.12.1+cpu | `torch.optim.Adam`, autograd, tensors | Already required; `zero_grad/backward/step` is the exact quickstart.py pattern |
| `scipy` | 1.18.0 (installed) | `scipy.stats.linregress` for a scripted decreasing-trend check | Already installed; avoids hand-rolling a slope test |
| `matplotlib` | 3.11.1 (installed) | Loss-curve plot | Already installed — confirmed via `pip list`, no new dependency needed |
| `pandas` | 3.0.3 (installed) | Convenience for writing `loss_history.csv`, optional | Already installed; `csv`/`torch.save` alone is equally sufficient if preferred |

**No new packages need to be installed for Phase 3** — confirmed directly (`pip list` shows matplotlib, scipy, pandas, pytest, merlinquantum, torch all already present in `./venv`).

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| `scipy.stats.linregress` for the trend check | Hand-rolled `(loss[-1] - loss[0])` comparison only | A single endpoint comparison is fooled by noise on either end; a fitted slope over all epochs plus a first-N%-vs-last-N%-mean check is more defensible as "the owner needs to defend this as genuinely met" |
| `torch.save(model.state_dict())` checkpoint | No checkpoint, only the loss curve | Phase 4 needs generated samples from a trained generator — saving Phase 3's trained weights is a cheap continuity point even if Phase 4 chooses to retrain with tuned hyperparameters |

## Architecture Patterns

### Recommended Project Structure
```
merlin-quantum-case-study/
├── generator/
│   ├── noise.py, bin_centers.py, data.py, mmd.py     # unchanged, Phase 2
│   └── train.py                # NEW: build_generator(), train_step(), run(), decreasing_trend_check()
├── train.py                    # NEW: thin entrypoint script, mirrors quickstart.py's flat style
├── results/                    # NEW: run artifacts (see "Artifact convention" below)
│   ├── phase3_loss_history.csv
│   ├── phase3_loss_curve.png
│   └── phase3_checkpoint.pt
├── tests/
│   └── test_train.py           # NEW: short smoke test (few epochs, tiny batch) — no-error + finite-loss checks only
```
Two-file split (`generator/train.py` for reusable pieces + root `train.py` as the runnable script) mirrors the existing convention: `generator/` holds pure, importable, testable functions; `quickstart.py` at root is the runnable script. Keep `train.py`'s reusable pieces (the step function, the trend-check function) in `generator/train.py` so `tests/test_train.py` can import and smoke-test them without running the full multi-hundred-epoch script.

### Pattern 1: Build once, loop many — QuantumLayer and optimizer persist across the whole run
**What:** Construct `QuantumLayer.simple(...)` and `torch.optim.Adam(quantum_layer.parameters(), lr=...)` exactly once, before the epoch loop. Never rebuild either inside the loop.
**Why it matters here specifically:**
- Rebuilding `QuantumLayer` inside the loop would re-randomize `thetas` every step (`torch.randn(...) * torch.pi` is the layer's own init, confirmed in `merlin/algorithms/layer.py`) — this silently defeats training entirely (every step starts from a fresh random circuit) while still "running without errors," making it a dangerous, easy-to-miss mistake for exactly the kind of "looks fine, isn't" failure this checkpoint needs to avoid.
- Rebuilding the `Adam` optimizer inside the loop resets its internal per-parameter moment estimates every step, degrading convergence even though nothing errors.
- This is the exact pattern `quickstart.py` and `tests/test_mmd.py::test_mmd2_gradient_reaches_quantum_layer` already use — no new risk here, just don't regress it.

### Pattern 2: One training step = fresh z-batch → forward → per-sample MMD² → average → backward
**What (recommended default, see Open Question 1 for the alternative):**
```python
# generator/train.py — extends the already-verified single-z pattern from
# tests/test_mmd.py::test_mmd2_gradient_reaches_quantum_layer to a batch,
# reducing via mean-of-per-sample-losses (not mean-of-q-vectors — see Open Questions).
import torch

def train_step(quantum_layer, optimizer, p_real, kernel_matrix, batch_size):
    optimizer.zero_grad()
    z = sample_latent(batch_size)               # fresh every step — GEN-02's own requirement
    q_batch = quantum_layer(z)                    # (batch_size, 400), each row already a valid prob. vector
    losses = torch.stack([
        mmd2(p_real, q_batch[i], kernel_matrix) for i in range(batch_size)
    ])
    loss = losses.mean()
    loss.backward()
    optimizer.step()
    return loss.item()
```
A vectorized (non-Python-loop) form is possible since `mmd2` is a bilinear form (`p@K@p + q@K@q - 2*p@K@q`), e.g. `qKq = torch.einsum('bi,ij,bj->b', q_batch, kernel_matrix, q_batch)` and `pKq = q_batch @ kernel_matrix @ p_real`, but at `batch_size` ≤ 64 and `K=400` the plain Python loop over `mmd2()` calls costs microseconds relative to the ~0.28s/step circuit forward pass measured in Phase 2 — vectorizing the reduction is a nice-to-have, not a Phase 3 blocker.

### Pattern 3: Precompute the kernel matrix once per chosen σ, outside the loop
**What:** `K = gaussian_kernel_matrix(bin_centers, sigma=0.1)` computed once, before the loop — already an established anti-pattern warning from Phase 2's own research ("Recomputing the kernel matrix inside the MMD² function on every call"). `p_real` is likewise computed once (Phase 2, no gradient needed).

### Anti-Patterns to Avoid
- **Passing `shots=` to `quantum_layer(z)`:** `QuantumLayer.forward()` accepts an optional `shots: int | None = None` / `sampling_method` pair (confirmed in `merlin/algorithms/layer.py`, `~line 1002`). Default (`shots=None`) means `apply_sampling=False` — the forward pass returns the exact analytic probability vector, which is what makes `mmd2(P_REAL, P_REAL, K) == 0.0` exactly (verified in Phase 2). Passing a `shots` value would layer additional shot-noise stochasticity onto the already-stochastic z-resampling, making the loss curve noisier for no reason Phase 3 needs — don't pass it unless intentionally exploring shot-noise robustness (out of scope here).
- **Averaging `q` vectors across the batch before calling `mmd2`, without deciding this explicitly:** see Open Question 1 — this changes the training objective's meaning, not just its variance.
- **Reusing one frozen `z` for the whole run:** GEN-02's own requirement ("resample-able every training step") exists precisely so the trained circuit doesn't overfit to one latent draw; always call `sample_latent(batch_size)` fresh inside the loop.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Adam optimizer, gradient step boilerplate | Manual SGD update | `torch.optim.Adam(quantum_layer.parameters(), lr=...)` | Already the proven pattern from `quickstart.py`; no reason to deviate |
| "Is this trend really decreasing" | Eyeballing a printed log | `scipy.stats.linregress(epoch_idx, losses)` slope/p-value + first-N%-vs-last-N%-mean comparison | Needed because this is an explicit stall-risk checkpoint the owner must defend as genuinely met, not just "looked fine" |
| Batched pairwise-kernel bilinear form | Custom einsum from scratch (optional optimization) | Plain Python loop over `mmd2()` per batch row (already-tested function) first; vectorize only if profiling shows it matters | At these problem sizes the circuit forward dominates cost by 3+ orders of magnitude; premature vectorization risks introducing a new untested numerical path under time pressure |

**Key insight:** Nearly everything Phase 3 needs is already built and tested in Phase 2. The engineering risk here isn't API unfamiliarity — it's (a) silently picking a batch-reduction semantics that changes what "trained" means without owner sign-off, and (b) claiming "the loss decreases" without a script-checkable definition of what that means.

## Common Pitfalls

### Pitfall 1: Batch size vs. loss-curve cleanliness (load-bearing for this phase's success criterion)
**What goes wrong:** Training with `batch_size=1` (i.e., the exact pattern already verified in `test_mmd2_gradient_reaches_quantum_layer`) is provably correct (gradients reach the circuit, are finite) but is documented in the QCBM/MMD literature to produce meaningfully noisier, less monotonic loss curves than larger batches — directly risking a curve that reads as "flat" or "not clearly decreasing" even if the underlying optimization is working.
**Why it happens:** Each step's `q` depends on one random `z`; MMD² of a single sampled configuration against `p_real` has high step-to-step variance independent of whether `theta` is actually improving.
**How to avoid:** Don't ship the literal batch=1 pattern as the *training* loop, even though it's the tested minimal case — use batch_size in the ~16–32 range (cheap: Phase 2 measured ~0.28s/step at batch=64, so 16–32 will cost less per step) and average the per-sample losses (Pattern 2 above).
**Warning signs:** A loss curve that visibly oscillates step-to-step without any clear envelope trend; the scripted trend check (linregress slope, or first/last-decile mean comparison) failing despite "the numbers look like they're going down" on manual inspection.

### Pitfall 2: `output_size` degeneracy silently returning — reconfirm, don't re-derive
**What goes wrong:** Phase 2 already discovered and fixed this (`input_size=10` required for `output_size=400` to be non-degenerate under `ModGrouping`). Phase 3 code must reuse `generator/noise.py`'s `LATENT_DIM = 10` and `QuantumLayer.simple(input_size=10, output_size=400)` exactly — don't re-derive `input_size` independently in the new training script.
**How to avoid:** Import `LATENT_DIM` from `generator/noise.py` rather than hardcoding `10` again in `train.py`, so there's a single source of truth if it's ever revisited.

### Pitfall 3: No hidden `log()` anywhere in the loss — confirmed, not a risk here
**What was checked:** Read `generator/mmd.py` directly. `mmd2()` and `gaussian_kernel_matrix()` use only `torch.exp`, `torch.cdist`, matrix multiplication (`@`), and `torch.clamp(..., min=0)` — no `torch.log` anywhere. The KL-divergence-style "probability underflows to exact 0 under log" failure mode does not apply to this MMD² formulation. **Confirmed, not merely assumed** — no new numerical-stability code is needed for Phase 3 unless a future phase adds a log-based term.

### Pitfall 4: Rebuilding the circuit or optimizer inside the loop (see Pattern 1)
Already covered above — restated here because it is the single most likely "looks fine but doesn't train" mistake for this phase, since neither error nor a shape mismatch would surface it; only a flat/random loss curve would.

## Code Examples

### Verified: default `QuantumLayer` parameter initialization scale
```python
# merlin/algorithms/layer.py, confirmed by direct source read:
parameter = nn.Parameter(
    torch.randn((len(theta_list),), dtype=self.dtype, device=self.device) * torch.pi
)
```
Thetas start at std ≈ π ≈ 3.14, mean 0 — matches `PhotonicGenerator`'s own reset convention (`merlin/models/photonic_generator.py::_reset_quantum_layer_trainable_parameters`, `torch.randn_like(parameter).mul(math.pi)`). This grounds the Adam `lr=0.01` starting point from `quickstart.py`: at `lr=0.01`, an early step moves parameters by roughly 0.3% of their initial scale — a conservative, standard-order-of-magnitude starting point for variational quantum circuit training, not a value to accept blindly (see Open Questions on lr tuning).

### Verified: `QuantumLayer.forward()` default keeps analytic (non-sampled) output
```python
# merlin/algorithms/layer.py, ~line 1002:
def forward(self, ..., shots: int | None = None, sampling_method: str | None = None):
    ...
    requested_shots = int(shots or 0)
    apply_sampling = requested_shots > 0   # False when shots is not passed
```
Confirms: calling `quantum_layer(z)` with no extra kwargs (as Phase 2's tests and `quickstart.py` already do) returns the exact analytic probability vector, deterministic given `(theta, z)` — the same property Phase 2 relied on to verify `mmd2(P_REAL, P_REAL, K) == 0.0` exactly.

### Proposed: scripted decreasing-trend check
```python
# generator/train.py
import numpy as np
from scipy.stats import linregress

def decreasing_trend_check(losses: list[float], tail_frac: float = 0.1) -> dict:
    """Returns a dict with slope, p_value, first_mean, last_mean, and a
    combined `passed` bool. Two independent conditions, both required:
      1. Fitted slope over all epochs is negative (real trend, not noise).
      2. Mean loss over the last `tail_frac` of epochs is at least 10% lower
         than the mean over the first `tail_frac` — guards against a
         technically-negative-but-visually-flat slope."""
    n = len(losses)
    x = np.arange(n)
    y = np.array(losses)
    slope, intercept, r_value, p_value, std_err = linregress(x, y)
    k = max(1, int(n * tail_frac))
    first_mean = y[:k].mean()
    last_mean = y[-k:].mean()
    relative_drop = (first_mean - last_mean) / first_mean if first_mean > 0 else 0.0
    passed = bool(slope < 0 and relative_drop >= 0.10)
    return {
        "slope": float(slope), "p_value": float(p_value),
        "first_mean": float(first_mean), "last_mean": float(last_mean),
        "relative_drop": float(relative_drop), "passed": passed,
    }
```
This is a proposed pattern (not yet implemented/tested against real training data — that's Phase 3 execution's job), offered so the plan can turn "loss curve shows a real, observable decreasing trend" into a script-checkable assertion rather than a manual read of a printed log.

## State of the Art

Not applicable in the version-churn sense (pinned `merlinquantum==0.4.0`, per `requirements.txt`). One relevant fact: the installed MerLin package ships no bundled examples/notebooks/tutorials directory (`pip show -f merlinquantum` and a filesystem search of the installed package both confirm no `examples/`, `notebooks/`, or `tutorial` files), and no MMD- or Born-machine-specific training loop exists anywhere in the installed source (`grep -i "mmd\|born.machine\|qcbm"` across the package returns nothing) — so there is no MerLin-native reference training loop for this exact architecture to crib from; `quickstart.py`'s classifier loop plus the already-tested Phase 2 gradient path are the closest available precedent, which is why Pattern 2 above builds directly on them.

## Open Questions

1. **Batch-reduction semantics: average per-sample losses (recommended) vs. average `q` vectors before computing one `mmd2` — an architecture/training-strategy decision this research cannot resolve unilaterally.**
   - What we know: a single `z` already yields a complete, valid `(400,)` distribution (Phase 1's `DESIGN_DECISIONS.md`, GEN-01). `mmd2` is a convex (PSD-quadratic) function of `q`, so by Jensen's inequality, **averaging losses** (`mean_i mmd2(p, q_i, K)`) pushes every individual `q_i` toward `p_real` (drives the circuit toward being largely z-invariant — every latent draw individually resembles the target), while **averaging q first** (`mmd2(p, mean_i(q_i), K)`) only requires the *mixture* over z to match `p_real`, permitting different z's to specialize on different parts of the distribution (e.g., different rings) as long as their aggregate matches. Both are used in different generative-modeling traditions; neither is "the" standard for this project's specific full-distribution-matching design, because that design itself (GEN-01) deliberately departs from the classic discrete-sample MMD-GAN formulation these traditions were built around.
   - What's unclear: which behavior the owner actually wants the trained generator to exhibit, and whether Phase 4's "generated samples visibly form two rings" (GEN-07) is easier to satisfy under one option vs. the other — that can't be determined without running Phase 3 itself.
   - Recommendation: default to **averaging per-sample losses** for planning purposes — it's a direct, minimal-risk generalization of the exact pattern already verified in `tests/test_mmd.py`, requires no new untested reduction logic, and is the more literature-precedented interpretation for MMD-based generative training under time pressure. Flag this explicitly in the plan for the owner to confirm or override before/while executing, consistent with CLAUDE.md's "no silent unilateral design decisions" and "training strategy is the owner's job" rules.

2. **Batch size, epoch count, learning rate — proposed starting defaults, not empirically tuned yet (that's what running Phase 3 itself determines).**
   - Proposed: `batch_size=32`, `epochs=300`, `Adam(lr=0.01)` (the `quickstart.py`/theta-init-scale-informed starting point above). At batch=32, expect somewhat less than the measured ~0.28s/step (batch=64) — a 300-epoch run should take on the order of 1–2 minutes wall-clock on CPU, leaving large margin against the July 25 checkpoint.
   - Recommendation: run a short smoke pass first (e.g., 20–30 epochs) before committing to the full run, to sanity-check the loss is moving at all; if it's nearly flat at `lr=0.01`, raise to `lr=0.05`–`0.1` before increasing epoch count — MMD² gradients can be small-magnitude even far from convergence, and this hasn't been empirically observed yet for this specific circuit/kernel combination.

3. **σ choice for Phase 3's actual training run.**
   - Recommendation: **σ=0.1** — already the exact value used in `tests/test_mmd2_gradient_reaches_quantum_layer` (proven to produce finite, non-degenerate gradients), and matches Phase 2 research's own reasoning (σ=0.1 ≈ the measured ring gap of 0.1, a middle-ground value expected to avoid both the near-delta-kernel vanishing-gradient risk at σ=0.02 and the over-smoothed weak-gradient risk at σ=0.4). Trying σ=0.2 as a second, cheap comparison run is reasonable given cost is negligible, but σ=0.1 should be the primary/default. Structural (visual ring-recovery) evaluation of the full `SIGMA_GRID` remains explicitly Phase 4's job per the existing locked decision.

4. **Artifact/results convention — proposed since none exists yet in this repo.**
   - Confirmed: no `results/`, `runs/`, or `scripts/` directory exists anywhere in the repo currently (`find . -maxdepth 2` checked directly).
   - Recommendation: create `results/` at repo root (not gitignored — `commit_docs: true` in `.planning/config.json`, and Phase 6 needs checked-in evidence of the actual run for the public repo/case study), with phase-prefixed filenames: `results/phase3_loss_history.csv`, `results/phase3_loss_curve.png`, `results/phase3_checkpoint.pt`. This keeps a flat structure consistent with the repo's current small scale (no nested per-phase subdirectories needed yet) while remaining unambiguous about provenance. Phases 4–6 can extend the same convention (`phase4_*`, `phase5_*`) rather than needing to invent a new one.

5. **pytest vs. script for the two success criteria.**
   - Recommendation: a small `tests/test_train.py` pytest smoke test (few epochs, small batch, asserts no exceptions + all losses finite — cheap, fast, CI-style regression guard) is appropriate and consistent with CONTEXT.md's locked Phase 2 verification method, but the *actual* evidence for "loss curve shows a real, observable decreasing trend" should come from running the real (300-epoch) `train.py` script and applying `decreasing_trend_check()` (Code Examples above) to its real output — a short pytest smoke run is not a substitute for the real run's evidence, since a few-epoch smoke test can't demonstrate a meaningful trend either way.

## Sources

### Primary (HIGH confidence — verified by direct execution/source read against the installed venv)
- `C:\Users\cuqui\merlin-quantum-case-study\venv\Lib\site-packages\merlin\algorithms\layer.py` — `QuantumLayer.forward()` `shots`/`sampling_method` default behavior (~line 999-1239); theta initialization (`torch.randn(...) * torch.pi`, ~line 595-600)
- `C:\Users\cuqui\merlin-quantum-case-study\venv\Lib\site-packages\merlin\models\photonic_generator.py` — `PhotonicGenerator`, `NormalLatent`, theta-reset convention (`_reset_quantum_layer_trainable_parameters`)
- `C:\Users\cuqui\merlin-quantum-case-study\generator\noise.py`, `bin_centers.py`, `data.py`, `mmd.py` — read directly, confirmed no `numpy`/`log` in the differentiable path
- `C:\Users\cuqui\merlin-quantum-case-study\tests\test_mmd.py` — the already-verified single-z gradient-flow test this phase's step function directly extends
- `C:\Users\cuqui\merlin-quantum-case-study\quickstart.py` — training-loop boilerplate precedent (Adam, `zero_grad/backward/step`, epoch-print cadence)
- `./venv/Scripts/python.exe -m pip list` — confirmed `matplotlib`, `scipy`, `pandas`, `pytest` all already installed; no new dependencies needed
- Filesystem search of `./venv/Lib/site-packages/merlin` — confirmed no examples/notebooks/tutorial files, no MMD/Born-machine-specific code anywhere in the installed package
- `.planning/phases/02-generator-data-loss-infrastructure/02-RESEARCH.md`, `02-CONTEXT.md`, `DESIGN_DECISIONS.md`, `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`, `.planning/STATE.md` — locked project decisions, requirements, and prior verified timing/geometry measurements (~0.28s/step at batch=64; σ=0.1 ≈ ring gap)

### Secondary (MEDIUM confidence)
- WebSearch: QCBM + MMD training batch-size sensitivity ("learning quality decreases drastically with smaller batches, more noise") — consistent across search results, not independently re-derived on this project's own circuit; treated as directional evidence, not a proven number for this specific setup.
- WebSearch: Generative Moment Matching Networks (Li, Swersky, Zemel 2015) — "requirement for a rather large batch size during training" — same caveat; this project's architecture (full-distribution matching per `z`, not discrete-sample MMD) is not identical to GMMN's classic formulation, so this is suggestive precedent, not a direct transfer.

### Tertiary (LOW confidence)
None used as load-bearing claims — where literature couldn't be directly verified against this project's specific (non-standard, full-distribution) architecture, that gap is called out explicitly in Open Question 1 rather than papered over.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — every package needed is already installed and verified present; no new dependency risk
- Architecture (loop structure, build-once/reuse pattern, numerical-safety pitfalls): HIGH — grounded in direct source reads of the installed `merlin` package and the project's own already-passing tests, not external inference
- Architecture (batch-reduction semantics specifically): MEDIUM — genuinely unresolved design question, given an explicit recommendation and rationale but correctly flagged as needing owner sign-off, not silently decided
- Pitfalls: HIGH — `shots` default, theta init scale, and the no-log-in-mmd2 confirmation were all read directly from source, not assumed

**Research date:** 2026-07-24
**Valid until:** Tied to `merlinquantum==0.4.0` staying pinned; re-verify the `shots`/theta-init findings if the MerLin version changes. The batch-reduction Open Question is not time-sensitive — it's a design decision, not a fact that goes stale.
