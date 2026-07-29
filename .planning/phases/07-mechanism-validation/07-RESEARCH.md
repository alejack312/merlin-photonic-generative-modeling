# Phase 7: Mechanism Validation - Research

**Researched:** 2026-07-29
**Domain:** PyTorch functional-autograd Jacobian computation over MerLin's `QuantumLayer`; resumable sigma-sweep scripting (reused from Phase 4); lightweight statistical hypothesis testing (reused rigor bar from `generator/train.py`'s `decreasing_trend_check`)
**Confidence:** HIGH — every load-bearing claim below was either read directly from this repo's/MerLin's source, or executed live against this repo's actual `venv` to confirm it works (not inferred from docs or training-data memory).

## Summary

Both of Phase 7's two experiments compose entirely from code that already exists in this repo — no new circuit code, no new MerLin API surface, no new dependency. The neighbor-locality test (`Method B`) needs one new capability the repo hasn't used yet — a Jacobian `∂q/∂θ` — and it was verified live in this environment: **`torch.func.jacrev` + `torch.func.functional_call` works cleanly and fast (1.27s per full 462×220 Jacobian) against `NaturallyOrderedGenerator`**. A naive per-output `torch.autograd.grad` loop (462 sequential backward calls) also works but is ~162x slower (205s/draw vs 1.27s/draw) — confirmed by direct timing in this repo's `venv`, not estimated. The sigma re-sweep needs zero new code beyond copy-adapting `sweep.py`'s existing resumable pattern to `natural_sorted_centers()`/`NaturallyOrderedGenerator` (exactly what `natural_order_train.py` already demonstrates for a single sigma) and looping it over `SIGMA_GRID`.

The two experiments should run in the roadmap's stated order because they're independent findings answering different halves of the same audit caveat (DESIGN_DECISIONS.md, 2026-07-29 correction) — the neighbor-locality test checks whether the *claimed mechanism* is real; the sigma re-sweep checks whether a *confound* (never-re-tuned bandwidth) could produce the same ring_mass bump on its own. Neither result changes the other's validity, so there's no hard technical dependency, only the roadmap's presentation order.

**Primary recommendation:** For the neighbor-locality test, use `torch.func.jacrev(lambda p: torch.func.functional_call(gen, p, (z,))[0])(dict(gen.named_parameters()))` at N=20 fresh random-init draws of `NaturallyOrderedGenerator` (each `build_naturally_ordered_generator()` call already IS an independent random theta draw — no manual reinit needed), concatenate the two per-prefix Jacobian blocks into a (462, 220) matrix, compute signed `cosine_similarity` for all 461 adjacent index pairs vs. an equal-sized random sample of non-adjacent pairs, pool across draws, and test with a two-condition pass/fail (direction + effect-size threshold) mirroring `decreasing_trend_check`'s existing pattern rather than a bare p-value. For the sigma re-sweep, copy `sweep.py` almost verbatim, swapping `make_bin_centers()`/`build_generator()` for `natural_sorted_centers()`/`build_naturally_ordered_generator()`, same `SIGMA_GRID = [0.02, 0.05, 0.1, 0.2, 0.4]`, same resumable checkpoint pattern, output to new `results/phase7_*` paths.

## Standard Stack

### Core (all already in `requirements.txt`, no additions needed)
| Library | Version (pinned) | Purpose | Why standard here |
|---|---|---|---|
| `torch` | 2.12.1 | `torch.func.jacrev`, `torch.func.functional_call`, `torch.nn.functional.cosine_similarity` | `torch.func` (formerly functorch) is the current, non-deprecated PyTorch API for functional/vectorized autograd (vmap-based Jacobians); verified live against this repo's actual `QuantumLayer` forward, not assumed from docs |
| `scipy` | 1.18.0 | `scipy.stats.mannwhitneyu` (or `ttest_ind`) for the adjacent-vs-random comparison | Already a dependency (`generator/train.py`'s `decreasing_trend_check` uses `scipy.stats.linregress`) — reuse, don't add a new stats library |
| `merlin` (`merlinquantum`) | 0.4.0 | `QuantumLayer.simple`, already wrapped by `NaturallyOrderedGenerator` | No new MerLin surface needed |

### Alternatives Considered
| Instead of | Could use | Tradeoff — verified, not guessed |
|---|---|---|
| `torch.func.jacrev` | `torch.autograd.functional.jacobian(func, inputs, vectorize=True)` | Also vmap-based, likely comparable speed — not tested here since `jacrev` already verified working; no reason to switch |
| `torch.func.jacrev` | Naive loop of 462 `torch.autograd.grad(q[k], params)` calls | **Verified 162x slower** (205.3s vs 1.27s for one Jacobian, measured live in this repo's venv). Still correct and safe (uses the exact same autograd path the existing `test_gradient_reaches_quantum_layer_through_permutation` test already proves works) — keep as the documented fallback only if `jacrev` ever misbehaves on a future MerLin version, not as the primary path. |
| `scipy.stats.mannwhitneyu` | `scipy.stats.ttest_ind` | Cosine-similarity distributions aren't guaranteed normal/symmetric; Mann-Whitney is the safer nonparametric default. Either is defensible — Claude's discretion at planning time. |

**Installation:** none — everything needed is already in `requirements.txt` / the committed `venv`.

## Architecture Patterns

### Recommended file layout (mirrors Phase 4/5's `results/`-plus-root-script convention)
```
neighbor_locality_test.py         # new, repo root — mirrors natural_order_train.py's structure
sigma_resweep.py                  # new, repo root — mirrors sweep.py's structure almost exactly
results/
├── phase7_neighbor_locality_metrics.csv   # per-draw adjacent/random cosine-sim summary stats
├── phase7_neighbor_locality_summary.md    # pass/fail verdict + honest interpretation
├── phase7_sigma_resweep_metrics.csv       # same columns as phase4_sweep_metrics.csv, K=462 grid
├── phase7_sigma_resweep_comparison.png    # mirrors phase4_sweep_comparison.png layout
```

### Pattern 1: Jacobian via `functional_call` + `jacrev` (VERIFIED WORKING, live-tested)

**What:** Treat the generator's forward pass as a pure function of its parameter dict at a fixed input `z`, then use reverse-mode functorch-style autodiff to get the full Jacobian in one call.

**When to use:** Any time `∂output/∂parameters` is needed for a `QuantumLayer`-based module without a training loop around it.

**Verified example** (run live against `NaturallyOrderedGenerator` in this repo's `venv`, 2026-07-29):
```python
# Source: verified live, C:\Users\cuqui\merlin-quantum-case-study, python venv/Scripts/python.exe
import torch
from torch.func import functional_call, jacrev
from generator.naturally_ordered_generator import build_naturally_ordered_generator
from generator.noise import sample_latent

gen = build_naturally_ordered_generator()  # fresh instance == fresh random theta draw already
gen.eval()
z = sample_latent(1)                        # (1, 10)
params = {k: v.detach() for k, v in gen.named_parameters()}
# params.keys() == {'base.quantum_layer.LI_simple', 'base.quantum_layer.RI_simple'}
# each value: torch.Size([110])  -- 110 + 110 = 220, matches results/phase5_summary.md's
# documented "Parameter count | 220"

def f(p):
    q = functional_call(gen, p, (z,))
    return q[0]                              # (462,) -- already permuted by gen.perm

J_dict = jacrev(f)(params)
# J_dict['base.quantum_layer.LI_simple'].shape == (462, 110)
# J_dict['base.quantum_layer.RI_simple'].shape == (462, 110)
J = torch.cat([J_dict[k].reshape(462, -1) for k in sorted(params)], dim=1)  # (462, 220)
# Measured wall-clock for the jacrev(f)(params) call alone: 1.27s
```
Critically: `q = functional_call(gen, p, (z,))` calls `NaturallyOrderedGenerator.forward`, which is `self.base(z)[:, self.perm]` — so **row `i` of `J` already corresponds to index `i` of `natural_sorted_centers()`**, i.e. the neighbor structure the plan needs (adjacent rows = adjacent bin-center ranks under radius sort) requires no extra reindexing.

### Pattern 2: Neighbor-locality metric (adjacent vs. random cosine similarity)

**What:** For a fixed `J` (462, 220), compute `cosine_similarity(J[i], J[i+1])` for `i in range(461)` (adjacent, list-neighbor pairs under the natural/radius-correspondence ordering) and `cosine_similarity(J[i], J[j])` for a random sample of `(i, j)` pairs with `|i - j| > 1` (or simply `i != i+1` and `j != i-1`, i.e. exclude both adjacency directions).

```python
import torch.nn.functional as Fnn

def adjacent_and_random_cosines(J, n_random=461, generator_seed=None):
    K = J.shape[0]
    adj_i = torch.arange(K - 1)
    adj_cos = Fnn.cosine_similarity(J[adj_i], J[adj_i + 1], dim=1)   # (461,)

    g = torch.Generator().manual_seed(generator_seed) if generator_seed is not None else None
    rand_pairs = set()
    while len(rand_pairs) < n_random:
        i, j = torch.randint(0, K, (2,), generator=g).tolist()
        if abs(i - j) > 1:
            rand_pairs.add((min(i, j), max(i, j)))
    ri = torch.tensor([p[0] for p in rand_pairs])
    rj = torch.tensor([p[1] for p in rand_pairs])
    rand_cos = Fnn.cosine_similarity(J[ri], J[rj], dim=1)
    return adj_cos, rand_cos
```
**Signed, not absolute, cosine similarity** — "list-neighbors move together" means correlated in the *same direction* (the property that lets a smooth, unimodal-per-band probability profile form), not merely coupled. State this choice explicitly in the plan; it is Claude's-discretion but load-bearing for interpretation (anti-correlated neighbors would score *negative* cosine, which should count as evidence against the mechanism, not for it).

### Pattern 3: Statistical comparison — match the project's existing rigor bar, don't invent a heavier one

`generator/train.py`'s `decreasing_trend_check` is this project's only precedent for "scripted, not eyeballed" statistical evidence, and it deliberately uses a **two-condition pass/fail**, not a bare p-value:
```python
# Source: C:\Users\cuqui\merlin-quantum-case-study\generator\train.py lines 37-61
def decreasing_trend_check(losses, tail_frac=0.1) -> dict:
    ...
    passed = bool(slope < 0 and relative_drop >= 0.10)
    return {"slope": ..., "p_value": ..., ..., "passed": passed}
```
Recommend the same shape for the neighbor-locality test:
```python
from scipy.stats import mannwhitneyu

def neighbor_locality_check(adj_cos: torch.Tensor, rand_cos: torch.Tensor, min_effect: float = 0.05) -> dict:
    stat, p_value = mannwhitneyu(adj_cos.numpy(), rand_cos.numpy(), alternative="greater")
    mean_diff = adj_cos.mean().item() - rand_cos.mean().item()
    passed = bool(mean_diff >= min_effect and p_value < 0.05)
    return {"adj_mean": adj_cos.mean().item(), "rand_mean": rand_cos.mean().item(),
            "mean_diff": mean_diff, "p_value": float(p_value), "passed": passed}
```
`min_effect` (a minimum mean-cosine-similarity gap, not just statistical significance) matters because pooling 20 draws × 461 pairs = 9,220 samples per group gives enormous statistical power — at that N, `p < 0.05` is nearly guaranteed even for a practically negligible effect. **Flag this explicitly in the plan**: report both `p_value` and `mean_diff`, and choose `min_effect` deliberately (e.g. discuss with the owner, or default to something like 0.05–0.10 cosine-similarity units) rather than treating `p < 0.05` alone as "mechanism confirmed." This mirrors the milestone audit's own finding #4 ("benchmark statistical claim overreach... 20 latent draws is not evidence of average improvement") — don't repeat that overreach here in the opposite direction (too much power, not too little).

Also recommend a **per-draw sign check** as a robustness complement, cheap to add: for each of the 20 draws independently, check whether `mean(adjacent) > mean(random)` for that draw alone, and report what fraction of the 20 draws agree in direction. A result that's "significant in pooled aggregate but only holds in 11/20 draws" is a materially weaker finding than "holds in 19/20 draws," and the current codebase's honesty norm (DESIGN_DECISIONS.md's repeated "at first I thought X, but I realized Y" corrections) means this distinction should be visible in the summary, not collapsed into one p-value.

### Anti-Patterns to Avoid
- **Testing locality only at the trained checkpoint's theta.** The roadmap explicitly says "several random parameter draws," and DESIGN_DECISIONS.md's own framing of the open question is about the circuit's "untrained/generic output-neighbor behavior" — a property of the architecture, not of one trained instance. `build_naturally_ordered_generator()` with no `load_state_dict()` call already gives an independent random draw (verified: `nn.Parameter(torch.randn(...) * torch.pi)` in `layer.py`'s `_setup_parameters_from_custom`) — use fresh instances per draw, don't perturb one fixed set of weights.
- **Recomputing the permutation manually.** `natural_sorted_centers()` and `NaturallyOrderedGenerator.forward` already apply/assume the exact same `perm`; `functional_call(gen, params, (z,))` returns the already-permuted 462-vector. Do not reapply `fock_state_sort_order` separately — that would double-permute.
- **Using `make_bin_centers()` (K=400) anywhere in Phase 7.** Both experiments are specifically about the K=462 natural-order grid; the old 400-bin grid is a different, incompatible indexing.
- **Re-seeding/reusing one `z` across all 20 draws without deciding so explicitly.** Either fix one `z` for all draws (isolates parameter-draw variance only) or draw a fresh `z` per draw (matches this repo's "fresh every call" convention in `sample_latent`/`train_step`). Either is defensible; state the choice and reason in the plan — don't leave it implicit.
- **Backgrounding the sigma re-sweep script.** STATE.md and this repo's own history (`natural_order_train.py`'s docstring, DESIGN_DECISIONS.md) document that backgrounded multi-minute scripts have died silently in this environment before. Run `sigma_resweep.py` in the foreground, resumable-by-checkpoint like `sweep.py`, exactly as Phase 4 already established.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Jacobian `∂q/∂θ` | A manual per-parameter finite-difference or hand-written VJP loop | `torch.func.jacrev` + `torch.func.functional_call` | Verified working and 162x faster than even the "safe" autograd-loop fallback; standard, current PyTorch API |
| Resumable multi-value sweep with checkpoint reuse | A new sweep harness | `sweep.py`'s exact pattern (skip-if-checkpoint-exists, per-value CSV row, comparison figure) | Already proven correct and resumable in this exact environment (Phase 4); `natural_order_train.py` already demonstrates the K=462/`NaturallyOrderedGenerator` adaptation for one sigma value — Phase 7 just needs to loop it |
| Held-out/statistical rigor pattern | A bespoke significance framework | `decreasing_trend_check`'s two-condition (direction + effect-size threshold) shape | Matches this project's already-established, owner-familiar rigor bar; avoids both under-claiming (bare eyeballing) and over-claiming (bare p-value at very high N) |
| Bin-center grid, permutation, checkpoint loading | New grid/generator code | `natural_sorted_centers()`, `build_naturally_ordered_generator()`, `NaturallyOrderedGenerator` (all in `generator/naturally_ordered_generator.py`) | This is exactly the object under test; Phase 7 must use the real thing, not a stand-in |

**Key insight:** Phase 7 is, like Phase 5, almost entirely composition of Phase 4/6 building blocks plus one genuinely new but now-verified capability (the Jacobian). Nothing about MerLin's `QuantumLayer` needed a workaround — the risk flagged going into this research (whether `vmap`-based functional autograd would choke on MerLin's complex-valued photonic simulation internals) did **not** materialize; it worked cleanly on the first attempt.

## Common Pitfalls

### Pitfall 1: Mistaking output buffering for a hang when testing this live
**What goes wrong:** Running a Python script that imports `torch`/`merlin` (60–90s just to import, confirmed by direct timing in this session) with stdout redirected to a file appears to produce zero output for minutes, looking like a hang.
**Why it happens:** Python block-buffers stdout (not line-buffered) when stdout is not a TTY — nothing prints until the buffer fills or the process exits.
**How to avoid:** Either accept the wait (import cost is fixed and unavoidable — confirmed ~60–90s in this venv), or run with `python -u` / `PYTHONUNBUFFERED=1` if incremental progress visibility is wanted during plan execution.
**Warning signs:** This bit the research process directly in this session — two background python invocations sat at zero visible output for 3–8 minutes each and both had, in fact, already succeeded; don't kill/retry a script early based on empty output alone.

### Pitfall 2: Interpreting `q[k]` (raw output probability) as needing renormalization before the Jacobian
**What goes wrong:** `q = functional_call(gen, params, (z,))[0]` sums to ~1.0 already (verified: `1.0000001192092896`, float32 rounding, matching the existing `test_forward_shape_and_probability_validity` tolerance of `abs=1e-5`). No renormalization step is needed before differentiating — `jacrev` differentiates through the module's actual forward, softmax-like normalization (if any) included, automatically.
**Why it happens:** Habit from other parts of the codebase (`ring_band_metrics` explicitly renormalizes `mass / mass.sum()` because it accepts un-normalized point counts) might suggest the same is needed here — it isn't; `q` is already a valid probability vector by construction.
**How to avoid:** Don't add a renormalization step to the Jacobian pipeline; it's unnecessary and would subtly change what's being differentiated (the renormalized function has a different, though closely related, Jacobian).

### Pitfall 3: Confounding the two experiments' conclusions
**What goes wrong:** If the sigma re-sweep finds a different optimal sigma at K=462, that changes what bandwidth *should* have been used for Phase 4's ring_mass=0.691 headline number — but it does **not** by itself confirm or refute whether list-neighbors move together (a property of the *circuit and ordering*, independent of sigma). Conversely, a positive neighbor-locality result does not rule out sigma also being a partial confound — both can be true simultaneously (DESIGN_DECISIONS.md's own framing: "Until the ablation... and a post-fix sigma sweep are run, the mechanism above is the best available hypothesis").
**Why it happens:** Both experiments feed into the same "was the 0.609→0.691 improvement real/well-understood" question, tempting a single combined verdict.
**How to avoid:** Report each experiment's result on its own terms in `results/phase7_*_summary.md` (or a combined `07-*-SUMMARY.md` with clearly separated sections), then a short synthesis paragraph — don't merge the two into one pass/fail number.

### Pitfall 4: Statistical power outrunning practical significance (see Pattern 3 above)
**What goes wrong:** Pooling 20 draws × 461 pairs per group makes `p < 0.05` a very low bar. A "PASSED" verdict based on p-value alone could overclaim, mirroring the exact overreach class the v1.0 audit already caught once (benchmark statistical claim overreach).
**How to avoid:** Report `mean_diff` (or a similar effect-size number) alongside `p_value`, and require both to clear stated thresholds, per Pattern 3.

## Code Examples

### Existing gradient-flow proof this test builds on (already passing, 49/49 suite)
```python
# Source: C:\Users\cuqui\merlin-quantum-case-study\tests\test_naturally_ordered_generator.py lines 65-79
def test_gradient_reaches_quantum_layer_through_permutation():
    centers = natural_sorted_centers()
    x_train, _ = load_circles_data()
    p_real = compute_p_real(x_train, centers)
    kernel_matrix = gaussian_kernel_matrix(centers, 0.1)

    gen = build_naturally_ordered_generator()
    q = gen(sample_latent(1))[0]
    mmd2(p_real, q, kernel_matrix).backward()

    params = list(gen.base.parameters())
    assert params
    assert any(p.grad is not None and torch.any(p.grad != 0) for p in params)
```
This already proves standard `.backward()` autograd reaches every trainable parameter through the permutation. Phase 7's Jacobian test is a strict generalization of this (full ∂q/∂θ instead of one scalar loss's gradient) — same underlying graph, same guarantee it's connected.

### Sigma re-sweep — adapt `sweep.py`'s exact resumable pattern
```python
# Source: pattern derived from C:\Users\cuqui\merlin-quantum-case-study\sweep.py (K=400 original)
# and natural_order_train.py (K=462, single sigma=0.1) -- Phase 7 combines both patterns.
import csv, os
import torch
from generator.data import load_circles_data, compute_p_real
from generator.mmd import SIGMA_GRID, gaussian_kernel_matrix
from generator.naturally_ordered_generator import (
    build_naturally_ordered_generator, natural_sorted_centers,
)
from generator.noise import sample_latent
from generator.train import train_step
from generator.visualize import ring_band_metrics

EPOCHS, LR, BATCH_SIZE = 300, 0.01, 32   # held fixed, matching sweep.py's isolation-of-sigma rationale
RESULTS_DIR = "results"

def train_all_sigmas(centers, p_real):
    rows = []
    for sigma in SIGMA_GRID:                 # SAME grid: [0.02, 0.05, 0.1, 0.2, 0.4]
        ckpt_path = f"{RESULTS_DIR}/phase7_sigma_{sigma}_checkpoint.pt"
        generator = build_naturally_ordered_generator()   # K=462, not build_generator() (K=400)
        if os.path.exists(ckpt_path):
            generator.load_state_dict(torch.load(ckpt_path, map_location="cpu"))
        else:
            kernel_matrix = gaussian_kernel_matrix(centers, sigma)
            optimizer = torch.optim.Adam(generator.parameters(), lr=LR)
            for epoch in range(EPOCHS):
                train_step(generator, optimizer, p_real, kernel_matrix, BATCH_SIZE)
            torch.save(generator.state_dict(), ckpt_path)
        generator.eval()
        with torch.no_grad():
            q = generator(sample_latent(1))[0]
        metrics = ring_band_metrics(q, centers)
        rows.append({"sigma": sigma, "ring_mass": metrics["ring_mass"], "gap_mass": metrics["gap_mass"]})
    with open(f"{RESULTS_DIR}/phase7_sigma_resweep_metrics.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["sigma", "ring_mass", "gap_mass"])
        writer.writeheader(); writer.writerows(rows)
```
Note: `train_step` is imported from `generator/train.py` unchanged (it's generator-agnostic — takes any `quantum_layer`-like module, `NaturallyOrderedGenerator` included, confirmed by `natural_order_train.py` already using it this way).

## State of the Art

| Old approach (this repo, pre-Phase-7) | New approach (Phase 7) | When changed | Impact |
|---|---|---|---|
| Sigma tuned once at K=400 (`sweep.py`, Phase 4), never revisited after K changed to 462 | Re-sweep the same `SIGMA_GRID` against K=462 (`sigma_resweep.py`) | Phase 7 | Either confirms sigma=0.1 is still best (strengthens Phase 4's result) or finds a better bandwidth (would mean Phase 4's 0.691 number under-sold what the correspondence fix could achieve, or was partly a bandwidth artifact) |
| Mechanism claim asserted from indirect evidence (fragment-count, total-variation, rank-correlation — all measured on the *target*/*trained-output*, never on the circuit's untrained parameter-sensitivity) | Direct Jacobian-based neighbor-locality test on **untrained**, randomly-initialized circuits | Phase 7 | Tests the actual load-bearing claim (per DESIGN_DECISIONS.md's own 2026-07-29 correction) for the first time, independent of any specific training run |

**Deprecated/outdated:** none — this is new ground for the repo, no prior Phase-7-equivalent work exists to supersede.

## Open Questions

1. **`min_effect` threshold for the neighbor-locality pass/fail.**
   - What we know: pooling 20 draws gives very high statistical power, so a bare `p < 0.05` is a weak bar (Pitfall 4 above).
   - What's unclear: what cosine-similarity gap counts as "practically meaningful" for this specific claim — no prior number in this codebase to anchor to (this is a genuinely new kind of metric for this repo).
   - Recommendation: state a concrete number (e.g. 0.05 or 0.10) explicitly in the plan as a locked decision, or flag it as Claude's-discretion-at-planning with the reasoning shown, rather than leaving `min_effect` as a free parameter decided silently at implementation time. This is exactly the kind of "no silent unilateral design decision" this repo's CLAUDE.md calls out.

2. **Fixed vs. fresh `z` across the 20 parameter draws.**
   - What we know: either choice is technically sound; `sample_latent` is designed to be called fresh every time throughout this codebase.
   - What's unclear: whether varying both `z` and `theta` simultaneously (testing "does locality hold across the joint space the training loop actually samples from") is a stronger or just noisier test than fixing `z` and varying only `theta` (isolating the architecture's parameter-sensitivity structure cleanly).
   - Recommendation: fresh `z` per draw, matching the codebase's dominant convention — but this is a one-line decision the plan should state explicitly rather than default silently.

3. **Whether to also test the trained checkpoint's theta as a secondary, non-required check.**
   - What we know: the roadmap's Method B description says "several random parameter draws" (generic/untrained property), matching DESIGN_DECISIONS.md's framing precisely.
   - What's unclear: whether the owner would also want one measurement at `results/phase4_natural_checkpoint.pt`'s actual trained theta, since that's the specific instance whose ring_mass=0.691 is the number being explained.
   - Recommendation: not required by the roadmap's stated scope, but cheap to add (one more `jacrev` call, ~1.3s) — flag as an easy stretch addition for the plan to include or explicitly defer, not silently omit.

## Sources

### Primary (HIGH confidence — read directly or executed live in this repo/venv)
- `C:\Users\cuqui\merlin-quantum-case-study\generator\naturally_ordered_generator.py` — `NaturallyOrderedGenerator`, `natural_sorted_centers`, `build_naturally_ordered_generator` read directly
- `C:\Users\cuqui\merlin-quantum-case-study\generator\spatial_alignment.py` — `radius_sort_order`, `fock_state_sort_order` read directly
- `C:\Users\cuqui\merlin-quantum-case-study\sweep.py`, `batch_sweep.py`, `natural_order_train.py` — resumable-sweep and K=462-adaptation patterns read directly
- `C:\Users\cuqui\merlin-quantum-case-study\generator\train.py` — `train_step`, `decreasing_trend_check` (statistical-rigor precedent) read directly
- `C:\Users\cuqui\merlin-quantum-case-study\generator\mmd.py` — `SIGMA_GRID = [0.02, 0.05, 0.1, 0.2, 0.4]`, `gaussian_kernel_matrix` read directly
- `C:\Users\cuqui\merlin-quantum-case-study\tests\test_naturally_ordered_generator.py`, `tests\test_spatial_alignment.py`, `tests\test_mmd.py` — existing gradient/permutation guarantees read directly
- `C:\Users\cuqui\merlin-quantum-case-study\venv\Lib\site-packages\merlin\algorithms\layer.py` — `QuantumLayer.simple` (n_modes=11, n_photons=6 for input_size=10 → C(11,6)=462), `self.thetas`/`_setup_parameters_from_custom` (random-init source, `nn.Parameter(torch.randn(...) * torch.pi)`), `forward()`'s autograd path read directly
- `C:\Users\cuqui\merlin-quantum-case-study\venv\Lib\site-packages\merlin\algorithms\layer_utils.py` — `_build_simple_circuit` (confirms two trainable prefixes, `LI_simple`/`RI_simple`) read directly
- **Live execution in this repo's `venv` (2026-07-29):** confirmed `qlayer.thetas` == `[Size([110]), Size([110])]`, total 220 params (matches `results/phase5_summary.md`'s documented parameter count), `output_keys` length 462; confirmed `torch.func.jacrev` + `functional_call` produces a correct (462,220)-equivalent Jacobian in **1.27s**; confirmed a naive 462-call `torch.autograd.grad` loop also works but takes **205.3s** (162x slower) — both executed directly, not assumed
- `C:\Users\cuqui\merlin-quantum-case-study\DESIGN_DECISIONS.md` — full mechanism-claim history and the exact 2026-07-29 self-correction that defines what Phase 7 must test, read directly
- `C:\Users\cuqui\merlin-quantum-case-study\docs\raster-order.md` — mechanism explanation + its own "Correction (2026-07-29)" section, read directly
- `C:\Users\cuqui\merlin-quantum-case-study\.planning\milestones\v1.0-MILESTONE-AUDIT.md` — exact original framing of both Phase 7 follow-ups (frontmatter `tech_debt` items), read directly
- `C:\Users\cuqui\merlin-quantum-case-study\.planning\phases\05-benchmarking\05-RESEARCH.md`, `05-VERIFICATION.md`, `results/phase5_summary.md`, `benchmark.py` — deliverable-format and rigor-bar precedent, read directly
- `C:\Users\cuqui\merlin-quantum-case-study\results\phase4_summary.md` (referenced), `natural_order_train.py`, `benchmark_timing.py` — checkpoint/timing conventions read directly
- `C:\Users\cuqui\merlin-quantum-case-study\.planning\STATE.md`, `.planning\config.json` — current phase status, `commit_docs: true` (not gitignored — confirmed via `git check-ignore`), owner's prior "implement directly" direction, read directly

### Secondary / Tertiary
None retained — every claim above was verified against this repo's own source or executed live; no external WebSearch/Context7 lookups were needed since this phase is 100% internal-repo composition plus one standard, well-documented PyTorch API (`torch.func`) that was verified by direct execution rather than by trusting training-data memory of its behavior.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — nothing new to install; `torch.func.jacrev` usage verified by live execution against the actual target module
- Architecture/Jacobian pattern: HIGH — verified working end-to-end (correct shapes, correct permutation ordering, timed) against `NaturallyOrderedGenerator` in this repo's venv, not inferred
- Sigma re-sweep pattern: HIGH — direct adaptation of two already-working, already-tested scripts (`sweep.py`, `natural_order_train.py`) in the same repo
- Statistical test design: MEDIUM — the two-condition (direction + effect-size) shape is well-grounded in this project's own established precedent (`decreasing_trend_check`), but the exact `min_effect` threshold is a genuinely new judgment call with no prior anchor in this codebase (see Open Question 1) — owner/planner discretion still applies

**Research date:** 2026-07-29
**Valid until:** stable for the remaining life of this project (Sept 1, 2026 deadline) — this is static analysis of this repo's own code plus one directly-verified PyTorch API behavior on a pinned `torch==2.12.1`; re-verify the `jacrev`/`functional_call` behavior only if `requirements.txt`'s torch pin ever changes.
