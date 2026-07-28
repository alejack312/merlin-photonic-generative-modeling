# Phase 5: Benchmarking - Research

**Researched:** 2026-07-28
**Domain:** Held-out MMD benchmarking of a trained MerLin `QuantumLayer` generator; comparison against MerLin's photonic QGAN paper reproduction
**Confidence:** HIGH (all four resolution questions answered from direct source/repo evidence, not inference)

## Summary

Everything BMK-01 needs already exists in this repo in reusable form. `generator/data.py`'s `load_circles_data()` already performs a deterministic 80/20 train/test split (320/80, `random_state=42`) of the same 400-point circles dataset used to build `p_real` for training — `X_test` was never touched by training, and a test (`tests/test_p_real.py::test_held_out_separation`) already documents this. Building `p_real_test` is one line: `compute_p_real(X_test, centers)`. The trained generator checkpoint to benchmark is `results/phase4_natural_checkpoint.pt` (the Phase 4 "option 3" natural-order generator, K=462, ring_mass=0.691/gap_mass=0.048, GEN-07 not met but the best available), loaded via `NaturallyOrderedGenerator()` + `load_state_dict()`, exactly as `natural_order_train.py` already does it. All MMD machinery (`gaussian_kernel_matrix`, `mmd2`) is already pure-`torch` and reusable as-is for a post-hoc (non-training) benchmark script.

The critical BMK-02 question — does MerLin ship a runnable local QGAN reproduction of "paper #16" — resolves to: **yes, runnable code exists, but not locally and not on the same data domain.** It lives in a separate public GitHub repo, `github.com/merlinquantum/reproduced_papers`, under `papers/photonic_QGAN/` (confirmed via GitHub API: has `lib/qgan.py`, `lib/generators.py`, `lib/discriminator.py`, a CLI runner `implementation.py`, configs, tests, and a notebook — a real, substantial adversarial-GAN codebase, not a stub). It does use MerLin's `ML.QuantumLayer` (confirmed by reading `lib/generators.py` directly), despite the README's stale-looking "IMPORTANT: only in Perceval for now" banner. It is **not** bundled in the installed `merlinquantum==0.4.0` pip package in this repo's venv — the venv's `merlin/models/photonic_generator.py` only ships the generic `PhotonicGenerator` building block referencing the same paper, not the full GAN/discriminator/training-loop reproduction. Critically, the reproduction trains on 8x8 `optdigits` grayscale digit-image patches (`data/photonic_QGAN/optdigits_csv.csv`), not the circles dataset — a different data domain entirely (pixel-intensity images vs. 2D point coordinates). Computing "the same held-out MMD statistic" (over K=462 radius-sorted 2D bin-centers) on digit-image output is not meaningful without redefining the metric space for images, which is exactly the work BMK-03 explicitly defers to an Aug 8 stretch goal, not required for Phase 5. **The fallback path specified in 05-CONTEXT.md therefore triggers**, and must be flagged explicitly in `results/phase5_summary.md`: cite the reproduction's reported results (best SSIM = 0.570575, from its own hp-study, on the digits dataset) and compare qualitatively — architecture (photonic Fock-space linear-optical circuit + classical discriminator, adversarial minimax loss) vs. this project's architecture (single `QuantumLayer`, closed-form full-distribution MMD² loss, no adversary), and dataset domain (grayscale digit patches vs. 2D point-cloud rings).

**Primary recommendation:** Write a single `benchmark.py` script that (1) reuses `load_circles_data()`/`compute_p_real()`/`natural_sorted_centers()`/`gaussian_kernel_matrix()`/`mmd2()` unchanged, loads `phase4_natural_checkpoint.pt`, computes mean±std held-out MMD² over N=20 fresh latent-z draws (mirroring Phase 4's existing 20-draw ring_mass stability check) at sigma=0.1 (same bandwidth as training, for direct comparability with all Phase 4 numbers), reports it against the untrained-generator and real-train-vs-real-test baselines, and (2) writes `results/phase5_summary.md` citing paper #16's reported SSIM and reproduction location, explicitly flagged as a qualitative-only comparison with the reason stated.

## Standard Stack

No new libraries needed. This phase is 100% built from existing repo infrastructure.

### Core (reused, unchanged)
| Module/Function | Location | Purpose |
|---|---|---|
| `load_circles_data()` | `generator/data.py` | Returns `(X_train, X_test)`, deterministic 80/20 split, already the held-out set BMK-01 needs |
| `compute_p_real(data_xy, bin_centers)` | `generator/data.py` | Nearest-bin-center histogram; call once on `X_train` (training reference, already used) and once on `X_test` (new: the held-out benchmark reference) |
| `natural_sorted_centers()` | `generator/naturally_ordered_generator.py` | K=462 radius-sorted bin centers matching the Phase 4 "option 3" checkpoint's output ordering |
| `gaussian_kernel_matrix(centers, sigma)` / `mmd2(p, q, kernel_matrix)` | `generator/mmd.py` | Closed-form MMD², pure torch, no autograd needed here (no `.backward()` call) but safe to reuse as-is |
| `build_naturally_ordered_generator()` / `NaturallyOrderedGenerator` | `generator/naturally_ordered_generator.py` | Construct the K=462 generator; fresh instance = untrained baseline, `load_state_dict(torch.load(...))` = trained model |
| `sample_latent(batch_size)` | `generator/noise.py` | Fresh z draws for repeat-seed MMD estimates |
| `ring_band_metrics(mass, centers)` | `generator/visualize.py` | Reuse unchanged for the carried-forward ring_mass/gap_mass numbers (CONTEXT.md requirement) |

### Supporting
| Library | Version | Purpose |
|---|---|---|
| `torch` | 2.12.1 (pinned in `requirements.txt`) | already installed |
| `time` (stdlib) | — | wrap training/inference for wall-clock reporting (CONTEXT.md requirement) — no script in this repo currently records this, must be added |

### Alternatives Considered
| Instead of | Could use | Tradeoff |
|---|---|---|
| Reusing `load_circles_data()`'s fixed 320/80 split | Re-splitting with multiple `random_state` values for a multi-split mean±std | `p_real`/`p_real_test` are deterministic (no randomness once the split is fixed) — the only source of run-to-run variance in `q` is the latent `z`, not the split. Varying the split adds a second uncontrolled variable and breaks reuse of every other script/test in the repo that assumes this exact split (`tests/test_p_real.py`, `train.py`, `natural_order_train.py`). **Recommendation: keep the split fixed, vary only `z` across repeats.** |
| Running `merlinquantum/reproduced_papers`' `photonic_QGAN` reproduction locally for a matched number | Cite its reported SSIM + qualitative comparison | Running it requires cloning a second repo, installing `torchvision`/`scikit-image`/`loguru` (not in this project's `requirements.txt`), fetching/regenerating the `optdigits` CSV, and — most importantly — its output domain (image patches) has no defined mapping onto this project's K=462 2D bin-center MMD metric without inventing new work equivalent to BMK-03 (explicitly deferred). Not worth doing for Phase 5's core deliverable given the Sep 1 deadline. |

**Installation:** none — no new packages required for BMK-01. If a future stretch (BMK-03) actually runs the QGAN reproduction, its `requirements.txt` is `merlinquantum, matplotlib, scikit-image, loguru, pytest, torchvision`.

## Architecture Patterns

### Recommended file layout (mirrors Phase 4's `results/` convention exactly)
```
benchmark.py                              # new, repo root, mirrors natural_order_train.py's structure
results/
├── phase5_benchmark_metrics.csv          # MMD mean/std + baselines + ring_mass/gap_mass + wall-clock + param count
├── phase5_summary.md                     # citation-ready aggregation (BMK-01 + BMK-02 + honest framing)
```

### Pattern 1: Post-hoc benchmark script (no training loop)
**What:** Load a frozen checkpoint, run `.eval()` + `torch.no_grad()`, compute a metric over repeat draws — structurally different from `train.py`/`natural_order_train.py` (no optimizer, no backward pass).
**When to use:** Any Phase 5 script.
**Example, following existing repo conventions:**
```python
# Source: pattern derived from natural_order_train.py's load path (generator/naturally_ordered_generator.py, generator/data.py)
import torch
from generator.data import load_circles_data, compute_p_real
from generator.mmd import gaussian_kernel_matrix, mmd2
from generator.naturally_ordered_generator import (
    build_naturally_ordered_generator, natural_sorted_centers,
)
from generator.noise import sample_latent

SIGMA = 0.1
CKPT = "results/phase4_natural_checkpoint.pt"

centers = natural_sorted_centers()
X_train, X_test = load_circles_data()          # X_test: 80 points, never seen by training
p_real_train = compute_p_real(X_train, centers) # == what training optimized against
p_real_test = compute_p_real(X_test, centers)   # NEW: held-out reference for BMK-01
kernel_matrix = gaussian_kernel_matrix(centers, SIGMA)

generator = build_naturally_ordered_generator()
generator.load_state_dict(torch.load(CKPT, map_location="cpu"))
generator.eval()

with torch.no_grad():
    mmds = []
    for _ in range(20):  # mirrors Phase 4's existing 20-draw ring_mass stability check
        q = generator(sample_latent(1))[0]
        mmds.append(mmd2(p_real_test, q, kernel_matrix).item())
mmd_tensor = torch.tensor(mmds)
print(f"held-out MMD^2: {mmd_tensor.mean():.4f} +/- {mmd_tensor.std():.4f}")
```

### Pattern 2: Untrained-baseline comparison
**What:** Construct the same architecture with fresh (random) `torch.randn`-initialized parameters — `build_naturally_ordered_generator()` without `load_state_dict()` — and compute the identical held-out MMD.
**Why:** CONTEXT.md-required baseline 1 ("MMD²(p_real_test, q_untrained)"), shows training helped at all.
```python
untrained = build_naturally_ordered_generator()  # fresh init, no checkpoint loaded
untrained.eval()
with torch.no_grad():
    q0 = untrained(sample_latent(1))[0]
mmd_untrained = mmd2(p_real_test, q0, kernel_matrix)
```

### Pattern 3: Real-vs-real floor baseline
**What:** CONTEXT.md-required baseline 2 — `MMD²(p_real_train, p_real_test)`, no generator involved at all, both computed from `compute_p_real`.
```python
mmd_floor = mmd2(p_real_train, p_real_test, kernel_matrix)
```

### Anti-Patterns to Avoid
- **Recomputing bin centers with `make_bin_centers()` (K=400) instead of `natural_sorted_centers()` (K=462):** the checkpoint's output columns are permuted/ordered for the 462-wide radius-sorted scheme; pairing it with the old 400-bin grid silently produces nonsense (shape mismatch or, worse, a shape-compatible but spatially wrong pairing if code is adapted carelessly).
- **Re-deriving a new train/test split:** `load_circles_data()`'s split is already what every other script/test in the repo assumes as "the" held-out set. A second, different split would be inconsistent with `tests/test_p_real.py` and would need its own justification.
- **Sampling-based MMD estimate:** this project's `mmd2` is closed-form over full probability vectors (see `mmd-loss.md` for the explicit rationale vs. a sibling project's sampling-based approach) — do not introduce `torch.multinomial`-based sampling into the metric itself; `sample_points`/`torch.multinomial` exist only for visualization (scatter plots), not for computing MMD.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Held-out train/test split of the circles data | A new `train_test_split` call with a fresh seed | `load_circles_data()`'s existing `X_test` (80 points, `random_state=42`) | Already deterministic, already tested (`test_held_out_separation`), already the split every other artifact in the repo implicitly assumes |
| Gaussian-kernel MMD² | A new sampling-based or numpy MMD implementation | `generator/mmd.py`'s `gaussian_kernel_matrix`/`mmd2` | Exact closed form already validated (Phase 2/3), numerically-checked tolerances already documented (`STATE.md`'s cdist float32-noise note) |
| Checkpoint loading for the K=462 model | A bespoke loader | `build_naturally_ordered_generator()` + `.load_state_dict(torch.load(CKPT, map_location="cpu"))`, exactly as in `natural_order_train.py` | State-dict keys (`perm`, `base.quantum_layer.*`) are specific to `NaturallyOrderedGenerator`; the plain `build_generator()` (K=400) uses different keys and is NOT compatible with `phase4_natural_checkpoint.pt` |

**Key insight:** Phase 5 is almost entirely composition of Phase 2–4 building blocks, not new infrastructure. The only genuinely new code is: (1) the untrained-baseline construction, (2) the repeat-seed loop + mean/std aggregation for the held-out statistic, (3) wall-clock/param-count instrumentation, (4) the `results/phase5_summary.md` write-up.

## Common Pitfalls

### Pitfall 1: Conflating "held-out" with "unseen distribution shape"
**What goes wrong:** `X_test` is drawn from the exact same `make_circles(random_state=42)` call as `X_train` (just a different 20% partition) — it is not an independently sampled dataset, it shares the same generating process/seed. This is standard train/test-split practice, but the summary write-up must not overstate it as testing generalization to a *different* distribution.
**Why it happens:** "Held-out" sounds stronger than "different 20% slice of one fixed draw."
**How to avoid:** State precisely in `phase5_summary.md`: "held-out" = never included in `p_real` at training time, drawn from the same underlying `make_circles` call.
**Warning signs:** none needed here — the CONTEXT.md's own definition already matches what the code does; just don't inflate the framing in the summary.

### Pitfall 2: K/bin-center mismatch if a QGAN comparison number is ever computed later
**What goes wrong:** If a future stretch (BMK-03) does attempt a matched number against the QGAN reproduction, its native output space (8x8 image, 64 pixel intensities) has no natural mapping onto this project's K=462 2D bin-center scheme. Forcing a comparison (e.g., reshaping/rescaling pixel intensities into a fake "distribution over 462 bins") would produce a number that looks comparable but measures a different thing.
**Why it happens:** Wanting one "matched" number is tempting once BMK-02's stretch fallback is documented.
**How to avoid:** Phase 5 stays fallback-only (qualitative), per 05-CONTEXT.md; do not attempt a forced numeric mapping without a real BMK-03-scoped plan.

### Pitfall 3: Wall-clock/parameter-count instrumentation doesn't exist yet
**What goes wrong:** No existing script in this repo records training wall-clock time or `sum(p.numel() for p in generator.parameters())`. `natural_order_train.py` prints per-epoch loss but never timed the run.
**Why it happens:** Not needed until Phase 5's CONTEXT.md requirement ("training cost/efficiency... reported alongside accuracy").
**How to avoid:** The benchmark script (or a small addendum) should wrap `time.time()` around a fresh from-scratch retrain (or, cheaper and equally honest: note that the existing checkpoint's training wall-clock was not captured historically, retrain-and-time from scratch as part of Phase 5 if an exact number is wanted) and separately report `sum(p.numel() for p in generator.parameters())` — trivial one-liner, no training needed for the param count.

### Pitfall 4: Stale README claim ("only in Perceval for now")
**What goes wrong:** Taking the QGAN reproduction's README banner at face value would incorrectly conclude it doesn't use MerLin's `QuantumLayer` at all.
**Why it happens:** The banner is at the top of the README and reads as authoritative.
**How to avoid:** Verified directly by reading `papers/photonic_QGAN/lib/generators.py` — it imports `merlin as ML` and builds `ML.QuantumLayer(...)` instances. The banner is likely stale/refers to a missing hardware-backend integration, not the absence of MerLin usage. State the comparison's architecture description from the actual code, not the banner.

## Code Examples

### Loading the trained Phase 4 checkpoint (verified pattern, `natural_order_train.py` lines 49-59)
```python
# Source: C:\Users\cuqui\merlin-quantum-case-study\natural_order_train.py
centers = natural_sorted_centers()
x_train, _ = load_circles_data()
p_real = compute_p_real(x_train, centers)

generator = build_naturally_ordered_generator()
generator.load_state_dict(torch.load(CKPT, map_location="cpu"))
generator.eval()
with torch.no_grad():
    q = generator(sample_latent(1))[0]
```

### Existing held-out split, already tested (`tests/test_p_real.py`)
```python
# Source: C:\Users\cuqui\merlin-quantum-case-study\tests\test_p_real.py
def test_held_out_separation():
    X_train, X_test = load_circles_data()
    assert X_train.shape[0] == 320
    assert X_test.shape[0] == 80
```

### QGAN reproduction's generator construction (evidence it uses MerLin's QuantumLayer, not raw Perceval)
```python
# Source: https://github.com/merlinquantum/reproduced_papers/blob/main/papers/photonic_QGAN/lib/generators.py
layer = ML.QuantumLayer(
    input_size=num_enc_params,
    circuit=pcvl_circuit.circuit,
    input_parameters=circuit_enc_params,
    trainable_parameters=circuit_var_params,
    input_state=self.input_state,
    measurement_strategy=ML.MeasurementStrategy.PROBABILITIES,
    computation_space=ML.ComputationSpace.FOCK,
)
```

### QGAN reproduction's run command (for citation only — not executed this phase)
```bash
# Source: https://github.com/merlinquantum/reproduced_papers/blob/main/papers/photonic_QGAN/README.md
python implementation.py --paper photonic_QGAN --config configs/defaults.json --mode digits
```

## State of the Art

| Old approach | Current approach | When changed | Impact |
|---|---|---|---|
| N/A — this is a first-time benchmark, no prior benchmarking code exists in this repo | — | — | — |

**Deprecated/outdated:** none relevant; Phase 5 is new ground for this repo.

## Open Questions

1. **Is a from-scratch timed retrain needed for the wall-clock number, or is an estimate acceptable?**
   - What we know: no historical wall-clock was captured for `phase4_natural_checkpoint.pt`'s original training run (300 epochs, batch=32).
   - What's unclear: whether Phase 5's plan should re-run training once more (few minutes, per Phase 4's precedent of ~12-14 min for a 5-value sweep, so a single 300-epoch run is materially faster) purely to capture `time.time()`, or whether an order-of-magnitude estimate suffices.
   - Recommendation: re-run once, timed — cheap or the case study to be honest per its constraint. Reuse `natural_order_train.py`'s exact resumable pattern (skip if checkpoint exists) is NOT desirable here since the goal is to time the run; the plan should either use a fresh output path or delete/backup the existing checkpoint intentionally before a timed retrain, or simply accept a slight fudge by timing a fresh training call to a scratch checkpoint path (not overwriting `phase4_natural_checkpoint.pt`) and confirming the same final ring_mass/gap_mass as documented (0.691/0.048) as a correctness check.

2. **Exact SSIM comparability caveat for BMK-02's qualitative citation.**
   - What we know: the reproduction's README reports best SSIM = 0.570575 from its own Adam-based hyperparameter study (not the original paper's SPSA-based result) — the README itself flags Adam-vs-SPSA as an open, unresolved question in their own reproduction.
   - What's unclear: whether Phase 5's summary should cite this Adam-based number, the original paper's SPSA number (not directly present in the fetched README — would require reading the arXiv paper, https://arxiv.org/abs/2405.06023, for the original figure), or both.
   - Recommendation: cite both if the arXiv paper's number is easy to pull during planning/execution; otherwise cite the reproduction's number with the Adam/SPSA caveat stated, which is itself an honest, citation-ready detail matching this project's "don't gloss over it" norm.

## Sources

### Primary (HIGH confidence)
- `C:\Users\cuqui\merlin-quantum-case-study\generator\data.py` — `load_circles_data()`, `compute_p_real()` read directly
- `C:\Users\cuqui\merlin-quantum-case-study\generator\mmd.py` — `gaussian_kernel_matrix`, `mmd2` read directly
- `C:\Users\cuqui\merlin-quantum-case-study\generator\naturally_ordered_generator.py` — checkpoint-compatible generator class read directly
- `C:\Users\cuqui\merlin-quantum-case-study\natural_order_train.py` — existing checkpoint-load pattern read directly
- `C:\Users\cuqui\merlin-quantum-case-study\tests\test_p_real.py` — proof the held-out split already exists and is tested
- `C:\Users\cuqui\merlin-quantum-case-study\venv\Lib\site-packages\merlin\models\photonic_generator.py` — confirms installed pip package (`merlinquantum==0.4.0`) ships only the generic `PhotonicGenerator` building block, not a full QGAN reproduction
- `C:\Users\cuqui\merlin-quantum-case-study\results\phase4_summary.md`, `.planning\STATE.md` — confirms `phase4_natural_checkpoint.pt` is the correct checkpoint to benchmark and its documented metrics (ring_mass=0.691, gap_mass=0.048)
- GitHub API (`api.github.com/repos/merlinquantum/reproduced_papers/contents/papers/photonic_QGAN`) — direct, authoritative listing confirming the reproduction's file structure (`lib/qgan.py`, `lib/discriminator.py`, `lib/generators.py`, `configs/`, `tests/`, notebook)
- `https://raw.githubusercontent.com/merlinquantum/reproduced_papers/main/papers/photonic_QGAN/README.md` — fetched directly (343 lines), confirms dataset (optdigits digit images), modes, hp-study results (SSIM=0.570575), run commands
- `https://raw.githubusercontent.com/merlinquantum/reproduced_papers/main/papers/photonic_QGAN/lib/generators.py` — fetched directly, confirms `import merlin as ML` and `ML.QuantumLayer(...)` usage, contradicting the README's stale "only in Perceval" banner
- `https://raw.githubusercontent.com/merlinquantum/reproduced_papers/main/papers/shared/photonic_QGAN/digits.py` — fetched directly, confirms 8x8 optdigits image dataset format
- `https://raw.githubusercontent.com/merlinquantum/reproduced_papers/main/papers/photonic_QGAN/requirements.txt` — fetched directly, confirms extra deps (`torchvision`, `scikit-image`, `loguru`) not in this project's `requirements.txt`

### Secondary (MEDIUM confidence)
- WebSearch confirming `merlinquantum/reproduced_papers` is the correct catalog repo and that paper #16 corresponds to Sedrakyan & Salavrakos, "Photonic quantum generative adversarial networks for classical data," Optica Quantum 2024/2025 (arXiv:2405.06023) — cross-checked against this repo's own `.planning/PROJECT.md` catalog note ("photonic QGAN (#16, adversarial loss, Sedrakyan & Salavrakos 2024)")

### Tertiary (LOW confidence)
- None retained — all load-bearing claims were verified against a primary source above.

## Metadata

**Confidence breakdown:**
- BMK-01 implementation path (held-out split, checkpoint loading, MMD reuse): HIGH — every piece verified by reading this repo's actual code, not inferred
- BMK-02 critical question (runnable local QGAN reproduction): HIGH — verified via GitHub API + direct file fetches of the actual reproduction source, not just its docs page
- Sigma/split defaults: MEDIUM — a reasoned recommendation (consistency with Phase 4's sigma=0.1), not itself independently re-derived from a fresh bandwidth study; owner/planner discretion still applies per 05-CONTEXT.md
- Wall-clock/param-count instrumentation: MEDIUM — straightforward but genuinely new code with no existing repo precedent to copy exactly

**Research date:** 2026-07-28
**Valid until:** stable — this is a static analysis of this repo's own code plus a fixed external repo's current `main` branch; re-verify the external repo's `main` branch state if execution is delayed more than ~30 days (it could add/change the reproduction).
