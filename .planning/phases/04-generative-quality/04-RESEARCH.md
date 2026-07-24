# Phase 4: Generative Quality - Research

**Researched:** 2026-07-24
**Domain:** Visualizing/evaluating a trained MerLin `QuantumLayer` generator (PyTorch, matplotlib), no new ML theory needed
**Confidence:** HIGH (all findings verified by directly reading and executing repo code, not from training-data assumptions)

## Summary

Phase 4 does not require any new library or unfamiliar API — it's a straight extension of infrastructure that already exists and is already tested (Phase 2/3's `generator/` modules, `train.py`'s matplotlib pattern). The three things Phase 4 actually needs are: (1) load `results/phase3_checkpoint.pt` back into a `QuantumLayer` built the same way `generator/train.py`'s `build_generator()` builds it, (2) turn the loaded model's analytic output vector `q` into 400 (x, y) points via `torch.multinomial` — no MerLin-specific sampling API needed, plain PyTorch is simplest and correct, and (3) a sigma-sweep script that reuses `generator/train.py`'s existing `train_step`/`build_generator` functions with a loop over `generator/mmd.py`'s already-defined `SIGMA_GRID`, since sigma only affects the *kernel matrix* build, not the model or training-step code.

The one real gotcha, verified directly: **`results/phase3_checkpoint.pt` stores only `quantum_layer.state_dict()`** (an `OrderedDict` with keys `quantum_layer.LI_simple`, `quantum_layer.RI_simple`) — it does **not** store which sigma, epoch count, or lr produced it. That information lives only in `train.py`'s hardcoded `SIGMA = 0.1` constant and DESIGN_DECISIONS.md/03-01-SUMMARY.md. Any Phase 4 script that loads this checkpoint must hardcode/comment `sigma=0.1` as "the value train.py used," not assume it's recoverable from the file.

**Primary recommendation:** Build a `generator/visualize.py` module (mirroring `generator/train.py`'s existing style: pure functions, no classes) with `sample_points(quantum_layer, z, centers, n=400)` for categorical sampling and `ring_band_metrics(...)` for the quantitative check, then a root-level `visualize.py` entrypoint (mirroring `train.py`'s flat script style) that loads the checkpoint, builds both plots, and prints the metric. For the sweep, a separate root-level `sweep.py` that loops `SIGMA_GRID`, calling the *same* `generator/train.py` functions per sigma with distinct output filenames — no changes needed to `generator/train.py` itself.

## Current State of the Codebase (verified by reading + running, 2026-07-24)

### `generator/train.py`
```python
def build_generator(input_size: int = LATENT_DIM, output_size: int = 400) -> ML.QuantumLayer:
    return ML.QuantumLayer.simple(input_size=input_size, output_size=output_size)

def train_step(quantum_layer, optimizer, p_real, kernel_matrix, batch_size) -> float: ...
def decreasing_trend_check(losses: list[float], tail_frac: float = 0.1) -> dict: ...
```
`LATENT_DIM = 10` (from `generator/noise.py`). `sigma` is **not** a parameter of `build_generator` or `train_step` — it only enters via the pre-built `kernel_matrix` argument to `train_step`. This means **retraining at a different sigma requires zero changes to `generator/train.py`** — just build a different `kernel_matrix = gaussian_kernel_matrix(centers, new_sigma)` and pass it in.

### Root `train.py`
Hardcodes `SIGMA = 0.1`, `BATCH_SIZE = 32`, `EPOCHS = 300`, `LR = 0.01`. Builds `centers`, `p_real`, `kernel_matrix`, `quantum_layer`, `optimizer` once, loops `EPOCHS`, writes three files to `results/`: `phase3_loss_history.csv`, `phase3_loss_curve.png` (via `matplotlib.use("Agg")` + `plt.figure()`/`plt.plot()`/`plt.savefig()`/`plt.close()`), and `phase3_checkpoint.pt` via **`torch.save(quantum_layer.state_dict(), ...)`** — the bare state dict, not a dict wrapping `{"model": ..., "sigma": ..., "epoch": ...}`.

### `generator/mmd.py`
```python
SIGMA_GRID = [0.02, 0.05, 0.1, 0.2, 0.4]   # already defined, already imported by tests/test_mmd.py
def gaussian_kernel_matrix(centers, sigma) -> torch.Tensor: ...
def mmd2(p, q, kernel_matrix) -> torch.Tensor: ...
```

### `generator/bin_centers.py`
```python
def make_bin_centers(side: int = 20, lo: float = -0.1, hi: float = 1.1, dtype=torch.float32) -> torch.Tensor:
    # K = side*side = 400, uniform grid, np.meshgrid(xs, ys, indexing="ij"), flattened via .ravel()
```
Verified empirically: `centers.reshape(20, 20, 2)[i, j] == (x_i, y_j)` — i.e. reshaping preserves x varying along axis 0, y along axis 1. This matters for any `imshow`-based heatmap (see Pitfalls).

### `generator/data.py` / `generator/noise.py`
`load_circles_data()` returns seeded, reproducible `(X_train (320,2), X_test (80,2))` normalized to `~[0,1]²` via train-derived min-max. `compute_p_real(data_xy, bin_centers)` returns a `(400,)` probability vector via nearest-bin-center assignment. `sample_latent(batch_size)` returns fresh `(batch_size, 10)` ~ `Normal(0, 2π)`.

### Checkpoint format — verified by loading it directly
```python
sd = torch.load("results/phase3_checkpoint.pt", map_location="cpu")
# type(sd) == collections.OrderedDict
# keys: 'quantum_layer.LI_simple' torch.Size([110]), 'quantum_layer.RI_simple' torch.Size([110])
```
Loads cleanly (`<All keys matched successfully>`) via:
```python
from generator.train import build_generator
quantum_layer = build_generator()          # input_size=10, output_size=400 — MUST match training-time values
quantum_layer.load_state_dict(torch.load("results/phase3_checkpoint.pt", map_location="cpu"))
quantum_layer.eval()                        # harmless no-op here (no dropout/batchnorm) but correct practice
```
**Confidence: HIGH** — this exact sequence was executed against the real checkpoint file during this research and succeeded.

### Known geometry — verified empirically, not assumed
`load_circles_data()`'s output is centered exactly at `(0.5, 0.5)` with two exact radii:
```
min radius ≈ 0.39999998 (inner ring, target 0.4)
max radius ≈ 0.5        (outer ring, target 0.5)
```
This confirms 04-CONTEXT.md's stated geometry (radii 0.4/0.5, gap 0.1) exactly — noise-free `make_circles` output, points lie essentially exactly on one of the two circles (float32 noise ~1e-7).

### Per-step and per-run timing (measured on this machine, this run)
~0.47s/`train_step` at `batch_size=32` → a full 300-epoch run ≈ 140s. A full 5-value `SIGMA_GRID` sweep at fixed epochs/lr/batch_size ≈ 12 minutes total — cheap enough to run all 5 before reviewing, matching the CONTEXT.md-locked "run all, review together" process.

## Architecture Patterns

### Recommended file layout (matches existing `generator/` + root-script split)
```
generator/
├── visualize.py       # NEW: sample_points(), ring_band_metrics(), plotting helper functions
├── train.py            # unchanged — reused as-is by the sweep
├── mmd.py               # unchanged — SIGMA_GRID already lives here
...
visualize.py             # NEW root entrypoint: load checkpoint, produce results/phase4_*.png, print metric
sweep.py                 # NEW root entrypoint (only if sigma=0.1 checkpoint looks non-ring-like): loops SIGMA_GRID
results/
├── phase3_checkpoint.pt        # existing, sigma=0.1
├── phase4_comparison.png       # NEW: side-by-side real|generated, heatmap+scatter
├── phase4_metrics.csv          # NEW (recommended): ring/gap mass per sigma, for sweep comparison
└── phase4_sigma_<v>_checkpoint.pt  # NEW, only if sweep runs
```

### Pattern: reuse `generator/train.py` unmodified for the sweep
Because sigma only affects `kernel_matrix` (never `build_generator`/`train_step`'s signatures), the sweep script is a thin loop, not a rewrite:
```python
from generator.mmd import SIGMA_GRID, gaussian_kernel_matrix
from generator.train import build_generator, train_step
from generator.bin_centers import make_bin_centers
from generator.data import load_circles_data, compute_p_real

centers = make_bin_centers()
x_train, _ = load_circles_data()
p_real = compute_p_real(x_train, centers)

for sigma in SIGMA_GRID:
    kernel_matrix = gaussian_kernel_matrix(centers, sigma)
    quantum_layer = build_generator()                       # fresh model per sigma — do not reuse across sigmas
    optimizer = torch.optim.Adam(quantum_layer.parameters(), lr=0.01)
    for epoch in range(300):
        train_step(quantum_layer, optimizer, p_real, kernel_matrix, batch_size=32)
    torch.save(quantum_layer.state_dict(), f"results/phase4_sigma_{sigma}_checkpoint.pt")
```
This is a **strict reuse** of Phase 3's already-tested `train_step`, so it carries the same correctness guarantees Phase 3 already validated (no new training-loop risk, per CLAUDE.md's "boilerplate offload" guidance — the *sigma choice/interpretation* is the owner's judgment call, not the loop mechanics).

### Pattern: categorical sampling — plain `torch.multinomial`, not a MerLin API
Verified: `ML.QuantumLayer`'s `shots=`/`sampling_method=` forward-pass options (used by `quantum_layer(z, shots=400)`) return a **re-normalized frequency vector over the same 400 bins** (quantized to multiples of `1/shots`), not a list of individual (x, y) draws — not the right shape for a scatter plot of 400 points. The correct, verified approach:
```python
import torch
q = quantum_layer(z)[0]                       # (400,) analytic probability vector, requires_grad not needed here
idx = torch.multinomial(q, num_samples=400, replacement=True)  # (400,) int64 bin indices
points = centers[idx]                          # (400, 2) — direct (x, y) scatter data
```
Verified empirically: works correctly including on bins with near-zero probability (e.g. `8.8e-7`) — `torch.multinomial` does not require the input to sum to exactly 1 (it renormalizes internally) and tolerates very small nonzero entries without numerical issues. **Don't hand-roll a cumulative-sum/searchsorted sampler** — `torch.multinomial` is the standard, correct, differentiation-agnostic (no grad needed here since this is inference-only visualization) tool for exactly this.

### Pattern: matplotlib side-by-side subplots, reusing `train.py`'s established style
`train.py`'s existing loss-curve script already establishes the conventions to match: `matplotlib.use("Agg")` set at import time (headless-safe, already done once per process — no need to repeat if `visualize.py` imports happen after `train.py`'s import, but **do set it again explicitly at the top of any new standalone script**, since each Python process needs its own backend set before any `pyplot` import). For side-by-side:
```python
fig, axes = plt.subplots(1, 2, figsize=(10, 5))
axes[0].scatter(x_train[:, 0], x_train[:, 1], s=10)
axes[0].set_title("Real (circles)")
axes[1].scatter(points[:, 0], points[:, 1], s=10)
axes[1].set_title("Generated (sampled)")
for ax in axes:
    ax.set_aspect("equal")
plt.savefig("results/phase4_scatter_comparison.png")
plt.close()
```
For the heatmap, **recommend a scatter-based heatmap over `imshow`** — `plt.scatter(centers[:,0], centers[:,1], c=q, cmap="viridis", s=40)` avoids the reshape/orientation pitfall entirely (see below) and reuses the exact same plotting primitive as the point-scatter, keeping the script simpler and more consistent with this repo's established "functional, not polished" style.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Draw 400 (x,y) points from a 400-way categorical distribution | Manual cumulative-probability + `searchsorted` sampler | `torch.multinomial(q, num_samples=400, replacement=True)` then `centers[idx]` | Standard, verified-correct, handles near-zero probabilities and non-exact-sum-to-1 inputs without special-casing |
| Reconstructing training-loop mechanics for the sigma sweep | A new/modified training loop | `generator/train.py`'s existing `build_generator`/`train_step`, looped over `SIGMA_GRID` | Already tested (28/28 passing suite), and sigma is already isolated to the `kernel_matrix` argument — no code path changes needed |
| Recovering which sigma/epoch/lr produced `phase3_checkpoint.pt` | Any inference-from-weights trick | Hardcode `sigma=0.1` with a comment citing `train.py`'s `SIGMA` constant / DESIGN_DECISIONS.md | The checkpoint file itself carries zero metadata — this is a fact about the file, not a solvable problem |

**Key insight:** everything Phase 4 needs is either already built (Phase 2/3 modules) or a single well-known PyTorch primitive (`torch.multinomial`). There is no new external dependency to research.

## Common Pitfalls

### Pitfall 1: Checkpoint carries no sigma/epoch metadata
**What goes wrong:** Assuming `torch.load(...)` on the checkpoint will reveal what sigma trained it, or building a "load and inspect" script that expects a `{"sigma": ..., "state_dict": ...}` wrapper.
**Why it happens:** `train.py`'s line 61 saves the bare `quantum_layer.state_dict()`, not a wrapping dict.
**How to avoid:** Treat `sigma=0.1` as an out-of-band fact (from `train.py`'s `SIGMA` constant), and document it explicitly in whatever script loads `phase3_checkpoint.pt`. **Recommended for the sweep:** if Phase 4 saves new checkpoints, consider switching to `torch.save({"state_dict": ..., "sigma": sigma, "epochs": epochs}, path)` for the *new* files going forward — cheap improvement, avoids repeating this footgun for Phase 5. Not required for reading the existing Phase 3 file, which must be read as a bare state dict regardless.

### Pitfall 2: `build_generator()` params must match the checkpoint's training-time params exactly
**What goes wrong:** Constructing `QuantumLayer.simple(input_size=2, output_size=400)` (the classifier's `input_size`, not the generator's) or any other mismatched shape before `load_state_dict` — this raises a hard shape-mismatch error, not a silent corruption, but it's an easy typo since `quickstart.py` uses `input_size=2` for a different model.
**How to avoid:** Always construct via `generator.train.build_generator()` with no overrides (defaults are `input_size=LATENT_DIM=10, output_size=400`, matching what actually trained). Verified: this exact call loads the real checkpoint with `<All keys matched successfully>`.

### Pitfall 3: `imshow`-based heatmap orientation
**What goes wrong:** Naively `plt.imshow(q.reshape(20, 20))` silently transposes x/y and flips the vertical axis relative to a normal scatter plot (imshow's default `origin='upper'` and row/col = y/x convention), producing a heatmap that looks mirrored/rotated relative to the adjacent scatter subplot.
**How to avoid:** Either avoid `imshow` entirely (recommended — use `plt.scatter(centers[:,0], centers[:,1], c=q, ...)`, verified orientation-safe since it uses raw (x,y) coordinates directly), or if `imshow` is used, verified-correct call is `plt.imshow(q.reshape(20,20,-1)... .T, origin='lower', extent=[-0.1, 1.1, -0.1, 1.1])` — the `.T` and `origin='lower'` are both required together; verified via direct inspection that `centers.reshape(20,20,2)[i,j]` has x varying along axis 0 and y along axis 1, which is the opposite of `imshow`'s row=vertical/col=horizontal default.

### Pitfall 4: Overwriting `results/` files during a 5-value sweep
**What goes wrong:** Reusing `train.py`'s literal filenames (`phase3_checkpoint.pt`, etc.) for sweep runs, silently clobbering Phase 3's checked-in evidence artifact.
**How to avoid:** Sigma-parameterize all sweep output filenames (e.g. `results/phase4_sigma_0.02_checkpoint.pt`), never touch `phase3_*` files. `results/` is not gitignored (verified: `.gitignore` only excludes `venv/`, `__pycache__/`, `*.pyc`, `.pytest_cache/`, `*.egg-info/`, `.ipynb_checkpoints/`) — anything written there is a checked-in artifact by this repo's established convention (Phase 3 precedent).

### Pitfall 5: `matplotlib.use("Agg")` must be set per-process before any `pyplot` import
**What goes wrong:** A new script imports `matplotlib.pyplot` before calling `matplotlib.use("Agg")`, which can silently fail to switch the backend on some platforms/interactive setups, or (on a headless/CI machine without a GUI backend) crash instead of just skipping display.
**How to avoid:** Copy `train.py`'s exact pattern verbatim at the top of any new script: `import matplotlib; matplotlib.use("Agg")` **before** `import matplotlib.pyplot as plt`.

### Pitfall 6: The ring/gap band width must leave room for a "gap" to exist
**What goes wrong:** Choosing a tolerance band so wide it swallows the entire 0.1-wide gap between radius 0.4 and 0.5 (e.g. `tol=0.05` exactly meets in the middle, leaving *zero* bins classified as "gap" — the metric can never detect gap-hedging, even for a badly-hedging generator).
**How to avoid:** Verified empirically against `p_real` itself (see Code Examples below) that `tol=0.04` is the largest value that (a) captures 100% of real data's probability mass in the "ring" bands and (b) still leaves gap bins (8 of 400) available to register mis-placed generated mass. Don't go above `tol=0.04` without re-checking against `p_real`.

## Code Examples

### Loading the Phase 3 checkpoint and sampling 400 points (verified working, this session)
```python
import torch
from generator.train import build_generator
from generator.noise import sample_latent
from generator.bin_centers import make_bin_centers

quantum_layer = build_generator()   # input_size=10, output_size=400 (defaults match training)
quantum_layer.load_state_dict(torch.load("results/phase3_checkpoint.pt", map_location="cpu"))
quantum_layer.eval()

centers = make_bin_centers()        # (400, 2), same grid used in training
with torch.no_grad():
    z = sample_latent(1)            # (1, 10) fresh latent draw
    q = quantum_layer(z)[0]         # (400,) probability vector, sums to 1
    idx = torch.multinomial(q, num_samples=400, replacement=True)
    points = centers[idx]           # (400, 2) — ready for plt.scatter
```

### Ring-band quantitative metric (concrete proposal — geometry verified empirically against real data)
```python
def ring_band_mass(q_or_counts, centers, center=(0.5, 0.5), radii=(0.4, 0.5), tol=0.04):
    """Fraction of probability mass (or point counts) within `tol` of either ring
    radius, vs. fraction in the empty gap between them.

    Verified against p_real (real circles data, K=400 bin-centers): tol=0.04 is
    the largest tolerance where ring_mass(p_real) == 1.0 and gap_mass(p_real) == 0.0
    -- i.e. it perfectly recovers the real geometry while still leaving 8/400 bins
    available to register a generated distribution's gap-hedging (tol=0.05 leaves
    zero gap bins and can never detect hedging).

    q_or_counts: (K,) tensor -- either the exact probability vector q (deterministic,
    recommended primary metric, reusable in Phase 5 with zero sampling variance) or
    a per-bin count vector from the 400 sampled scatter points (matches the CONTEXT.md
    framing of "% of sampled points", reported as a secondary/cross-check number).
    """
    r = torch.norm(centers - torch.tensor(center), dim=1)
    ring_mask = (torch.abs(r - radii[0]) <= tol) | (torch.abs(r - radii[1]) <= tol)
    lo_gap, hi_gap = radii[0] + tol, radii[1] - tol
    gap_mask = (r > lo_gap) & (r < hi_gap) if hi_gap > lo_gap else torch.zeros_like(r, dtype=torch.bool)
    mass = q_or_counts / q_or_counts.sum()
    return {
        "ring_mass": mass[ring_mask].sum().item(),
        "gap_mass": mass[gap_mask].sum().item(),
    }

# Sanity check against real data (run during this research):
#   tol=0.04 -> ring_mass(p_real) = 1.0000, gap_mass(p_real) = 0.0000  (n_gap_bins=8, available)
#   tol=0.05 -> ring_mass(p_real) = 1.0000, gap_mass(p_real) = 0.0000  (n_gap_bins=0 -- unusable, no gap left to detect)
```
To get the sample-based (scatter) version, convert the 400 sampled `idx` into a per-bin count vector first: `counts = torch.bincount(idx, minlength=400).float()`, then call `ring_band_mass(counts, centers, ...)`.

### Side-by-side heatmap+scatter figure (4 subplots: real-scatter, gen-scatter, real-heatmap via p_real, gen-heatmap via q)
```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 2, figsize=(10, 5))
axes[0].scatter(x_train[:, 0], x_train[:, 1], s=10, alpha=0.6)
axes[0].set_title("Real (circles, n=400 total incl. held-out)")
axes[1].scatter(points[:, 0], points[:, 1], s=10, alpha=0.6)
axes[1].set_title(f"Generated (sampled, sigma={SIGMA})")
for ax in axes:
    ax.set_aspect("equal")
    ax.set_xlim(-0.1, 1.1)
    ax.set_ylim(-0.1, 1.1)
plt.savefig("results/phase4_scatter_comparison.png")
plt.close()

fig, axes = plt.subplots(1, 2, figsize=(10, 5))
sc0 = axes[0].scatter(centers[:, 0], centers[:, 1], c=p_real, cmap="viridis", s=40)
axes[0].set_title("Real (p_real heatmap)")
sc1 = axes[1].scatter(centers[:, 0], centers[:, 1], c=q, cmap="viridis", s=40)
axes[1].set_title("Generated (q heatmap)")
for ax, sc in zip(axes, [sc0, sc1]):
    ax.set_aspect("equal")
    plt.colorbar(sc, ax=ax)
plt.savefig("results/phase4_heatmap_comparison.png")
plt.close()
```

## State of the Art

Not applicable in the usual sense (no external ecosystem/version churn relevant here) — this phase uses only already-pinned repo dependencies (`torch==2.12.1`, `matplotlib==3.11.1`, `merlinquantum==0.4.0`, per `requirements.txt`) and functions already implemented and tested in this repo. No deprecated APIs encountered; `ML.QuantumLayer.simple(...)`, `.state_dict()`/`.load_state_dict()`, and `torch.multinomial` are all current, stable PyTorch/MerLin APIs as installed.

## Open Questions

1. **Whether sigma=0.1's existing checkpoint already looks ring-like enough, or whether the sweep is needed at all**
   - What we know: this is explicitly the first step CONTEXT.md locks in ("visualize the existing checkpoint first, cheap check") — it's a result to observe, not something researchable in advance.
   - What's unclear: nothing implementation-wise; this is a judgment call for the owner once the first plot exists.
   - Recommendation: no action needed from planning — the plan should sequence "visualize sigma=0.1" as its own early task/checkpoint before committing to the sweep task.

2. **How to report a "no sigma value worked" outcome**
   - Explicitly deferred in 04-CONTEXT.md until real sweep results exist. Not researchable now — flagged here only so the planner doesn't try to pre-decide it.

3. **Whether Phase 4's new checkpoints (if the sweep runs) should switch to a metadata-wrapped save format**
   - What we know: Phase 3's bare-state-dict format works but loses sigma/epoch provenance (Pitfall 1).
   - What's unclear: whether this is worth the small format inconsistency with `phase3_checkpoint.pt` for a one-phase timeline.
   - Recommendation: low-cost improvement, suggested but not required — planner's discretion; if adopted, only applies to newly-saved Phase 4 files, not a rewrite of the existing Phase 3 artifact.

## Sources

### Primary (HIGH confidence — direct repo inspection + execution, 2026-07-24)
- `generator/train.py`, `train.py`, `generator/mmd.py`, `generator/bin_centers.py`, `generator/data.py`, `generator/noise.py`, `quickstart.py` — read directly
- `tests/test_train.py`, `tests/test_mmd.py`, `tests/test_p_real.py` — read directly
- `results/phase3_checkpoint.pt` — loaded directly via `torch.load` + `build_generator().load_state_dict(...)`, both the raw key structure and successful load verified by execution, not assumed
- `venv/Lib/site-packages/merlin/algorithms/layer.py` (`QuantumLayer.forward` signature) — inspected via `inspect.signature`
- Empirical execution in this session: checkpoint loading, `torch.multinomial` sampling, `centers.reshape(20,20,2)` orientation check, real-data radius/geometry verification (`min≈0.4`, `max≈0.5`, centered at `(0.5,0.5)`), ring/gap tolerance sweep against `p_real` (tol=0.02 through 0.05), per-step/per-run timing measurement
- `requirements.txt` — exact pinned versions (`torch==2.12.1`, `matplotlib==3.11.1`, `merlinquantum==0.4.0`)
- `.gitignore` — confirms `results/` is tracked, not excluded
- `.planning/phases/04-generative-quality/04-CONTEXT.md`, `DESIGN_DECISIONS.md`, `.planning/phases/03-end-to-end-training-run/03-01-SUMMARY.md`, `NOTES.md` — read directly for locked decisions and prior-phase context

### Secondary / Tertiary
None used — this phase required no external/web research; everything needed was resolvable from the repo itself and standard, already-pinned PyTorch/matplotlib APIs already in use elsewhere in this codebase.

## Metadata

**Confidence breakdown:**
- Codebase current-state findings (checkpoint format, function signatures, geometry): HIGH — all verified by direct execution against the real files, not inference
- Sampling approach (`torch.multinomial`): HIGH — standard, stable PyTorch API, tested directly against the real loaded model in this session
- Ring-band metric formula/threshold: MEDIUM — the tol=0.04 value is empirically justified against real data in this repo, but is a design proposal (per 04-CONTEXT.md's explicit "Claude's discretion"), not an externally-standardized metric; planner/owner should treat the exact threshold as adjustable
- Plotting orientation pitfalls (imshow vs scatter): HIGH — verified by direct tensor inspection of `centers.reshape(20,20,2)`

**Research date:** 2026-07-24
**Valid until:** effectively indefinite for this phase (no external dependency drift risk — all findings are about this specific, already-pinned, already-written codebase, not a fast-moving ecosystem)
