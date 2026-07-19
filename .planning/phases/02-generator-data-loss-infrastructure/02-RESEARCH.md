# Phase 2: Generator Data & Loss Infrastructure - Research

**Researched:** 2026-07-19
**Domain:** MerLin (`merlinquantum` 0.4.0) photonic QuantumLayer output sizing, latent sampling, MMD² over a fixed 2D bin-center grid, pytest infra
**Confidence:** HIGH (all claims below verified empirically against the installed `venv` — merlin 0.4.0, torch 2.12.1+cpu — not taken from training-data memory or docs alone)

## Summary

The phase-2 building blocks (noise encoding, bin-centers, `p_real`, MMD² loss) are all straightforward to implement directly with `torch`/`numpy`/MerLin's `QuantumLayer.simple()`. The one load-bearing finding that changes the plan from what CONTEXT.md assumed: **`input_size=2` (the locked "start at 2" latent dimensionality) cannot produce a non-degenerate `output_size=400` distribution.** `QuantumLayer.simple(input_size=2)`'s natural (un-grouped) output distribution has only **3** entries (2 photons over 3 modes, unbunched). Requesting `output_size=400` from that circuit doesn't error — MerLin's `ModGrouping` silently **zero-pads** when the requested output width exceeds the natural width, so 397 of the 400 bins would be permanently exactly zero regardless of training. This was verified by direct execution, not inferred from source alone. The natural output width first reaches ≥400 at **`input_size=10`** (natural width 462), which is where `ModGrouping` switches to its real "modulo-index-and-sum" behavior, producing a genuine 400-wide, fully-supported, correctly-normalized, differentiable probability vector. `input_size=10` (and 11) are still cheap: ~0.29s to build the circuit, ~0.03s/sample forward, ~0.28s per full train step at batch=64 — no simulation-cost blocker for Phase 3. This is a **decision the owner needs to confirm** (see Open Questions) — it's a direct conflict between two locked CONTEXT.md decisions, not a discretionary call this research can resolve unilaterally.

Also load-bearing: `PhotonicGenerator`/`VectorAdapter`, the "research pointer" CONTEXT.md flagged as a promising reuse candidate, **is not a clean fit** for this phase's probability-vector-matching use case, and should not be used as the GEN-05 output path. `VectorAdapter` center-crops or zero-pads raw measurement tensors to a target width — it does not renormalize, so cropping silently discards probability mass (breaks "sums to 1") and `PhotonicGenerator` additionally can't even accept the `output_size`-adjusted module `QuantumLayer.simple()` returns, because that wrapper (`SimpleSequential`) is not itself a `QuantumLayer` instance (fails `PhotonicGenerator`'s `isinstance` check). The clean, verified path is: use `QuantumLayer.simple(input_size, output_size=K)` **directly** as the generator's forward model (it already returns a correctly-normalized, fully-differentiable K-wide probability vector via `ModGrouping`, confirmed by direct testing), and optionally reuse MerLin's standalone `NormalLatent` class (exported as `merlin.NormalLatent`) for GEN-02's noise sampling instead of hand-rolling `torch.randn(...).mul(std)` — that part of the research pointer *is* a good, low-risk reuse.

**Primary recommendation:** Build GEN-02–GEN-05 as small standalone modules (no `PhotonicGenerator`): `merlin.NormalLatent(dim, std=2*pi).sample(batch_size)` for noise, a `numpy`/`torch` uniform-grid function for bin-centers, nearest-bin-center histogram binning for `p_real`, and a `torch.cdist`-based closed-form MMD² using precomputed `(K,K)` kernel matrices (one per σ in the sweep). Confirm with the owner whether `input_size` (and therefore latent dim) should move from 2 to 10 to make `output_size=400` real, or whether `K` should shrink to match `input_size=2`'s natural output.

## Standard Stack

### Core
| Library | Version (installed) | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `merlinquantum` (`import merlin`) | 0.4.0 | `QuantumLayer.simple()` for the generator circuit; `NormalLatent` for noise | Already the project's chosen framework (Phase 1) |
| `torch` | 2.12.1+cpu | Tensors, autograd, `torch.cdist` for pairwise distances | Already required by MerLin; gradients must flow through `q` |
| `numpy` | 2.5.1 | Deterministic bin-center grid construction (`np.linspace`/`meshgrid`) | Simpler/clearer than building a grid in torch; convert to `torch.Tensor` once at the end |
| `scikit-learn` | 1.9.0 | `make_circles`, `train_test_split` (already used in quickstart.py) | Already the project's dataset source |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `pytest` | not yet installed (missing from `requirements.txt` and the venv) | Automated test files per CONTEXT.md's locked verification method | Install and pin before writing any Phase 2 test — see Pitfall below |
| `scipy` | 1.18.0 (already installed) | `scipy.spatial.distance.cdist`/`pdist` for exploratory bandwidth analysis (not required in the final loss code — `torch.cdist` covers that) | Optional, exploratory only |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Nearest-bin-center histogram for `p_real` | `numpy.histogram2d` with grid-aligned edges | Both are valid and roughly equivalent for a uniform grid. Nearest-center assignment (1-NN to the K centers via `torch.cdist`/`scipy.cdist` argmin) is recommended because it ties `p_real`'s definition directly to "the K bin-centers" (matching GEN-04's wording) and reuses the exact same distance machinery as the kernel, rather than introducing a second, only-approximately-equivalent binning convention (grid edges vs. grid centers). |
| Custom `PhotonicGenerator` wrapper for GEN-02/05 | Raw `QuantumLayer.simple()` + `merlin.NormalLatent` | See Summary — `PhotonicGenerator`+`VectorAdapter` breaks normalization and can't accept the `output_size`-adjusted `.simple()` module. Not worth fighting for a two-line noise-sampling convenience. |
| Single fixed σ | σ sweep (locked decision) | Already decided in CONTEXT.md; see Bandwidth section for concrete values. |

**Installation:**
```bash
./venv/Scripts/python.exe -m pip install pytest
./venv/Scripts/python.exe -m pip freeze | findstr /I pytest >> requirements.txt   # or manually add pytest==<installed version>
```
(No other new packages are needed — `torch`, `numpy`, `scikit-learn`, `merlinquantum` are already installed.)

## Architecture Patterns

### Recommended Project Structure
```
merlin-quantum-case-study/
├── generator/                  # new package, Phase 2 deliverables
│   ├── __init__.py
│   ├── noise.py                 # GEN-02: sample_latent(batch_size) -> Tensor
│   ├── bin_centers.py            # GEN-03: make_bin_centers() -> Tensor (K,2)
│   ├── data.py                   # GEN-04: compute_p_real(bin_centers) -> Tensor (K,)
│   └── mmd.py                    # GEN-05: gaussian_kernel_matrix(), mmd2()
├── tests/
│   ├── test_noise.py
│   ├── test_bin_centers.py
│   ├── test_p_real.py
│   └── test_mmd.py
├── pytest.ini  (or pyproject.toml [tool.pytest.ini_options])
└── requirements.txt   # add pytest
```
This mirrors quickstart.py's flat, no-framework style — no need for a class hierarchy; each GEN-0x requirement maps to one small, pure-function module with one obvious test file. Given Phase 3 will import all four modules to build the training loop, keep each function's public signature stable and free of side effects (no global state, no hidden RNG seeding) so Phase 3 can call them predictably every step (GEN-02 in particular must be resample-able each training step, per its own requirement wording).

### Pattern 1: Deterministic bin-center grid (GEN-03)
**What:** A `K = side * side` uniform grid over the padded bounding box of the (min-max-normalized) circles data, built once with `numpy.linspace`/`meshgrid` — no `torch.rand`, no seeded RNG, so it is bit-identical across runs/processes.
**When to use:** Any time bin-centers are needed (GEN-03, and as an input to GEN-04/GEN-05).
**Example (verified, adapt directly):**
```python
# Verified via direct execution against the installed merlin/torch stack.
import numpy as np
import torch

def make_bin_centers(
    side: int = 20,
    lo: float = -0.1,
    hi: float = 1.1,
    dtype: torch.dtype = torch.float32,
) -> torch.Tensor:
    """K = side*side uniform grid centers over [lo, hi]^2. Deterministic, no RNG."""
    xs = np.linspace(lo, hi, side)
    ys = np.linspace(lo, hi, side)
    gx, gy = np.meshgrid(xs, ys, indexing="ij")
    centers = np.stack([gx.ravel(), gy.ravel()], axis=1)  # shape (side*side, 2)
    return torch.tensor(centers, dtype=dtype)
```
Verified: `make_bin_centers(20, -0.1, 1.1)` produces exactly 400 rows, grid spacing 1.2/19 ≈ 0.0632, and is identical on repeated calls (no source of nondeterminism in `np.linspace`/`meshgrid`).

### Pattern 2: `p_real` via nearest-bin-center histogram (GEN-04)
**What:** Assign each real (normalized) training point to its nearest bin-center (Euclidean, argmin), count, normalize by total count.
**Example:**
```python
import torch

def compute_p_real(data_xy: torch.Tensor, bin_centers: torch.Tensor) -> torch.Tensor:
    """data_xy: (N,2) real points already in the bin-centers' coordinate space.
    bin_centers: (K,2). Returns (K,) probability vector, non-negative, sums to 1."""
    dists = torch.cdist(data_xy, bin_centers, p=2)          # (N, K)
    nearest = dists.argmin(dim=1)                            # (N,)
    counts = torch.bincount(nearest, minlength=bin_centers.shape[0]).float()
    return counts / counts.sum()
```
Note: with only ~320 training points spread over two thin rings and 400 bins, most bins will have `p_real == 0` (verified: the two rings sit at exact radius 0.4 and 0.5 from the box center, with `noise=None` in `make_circles` — points lie exactly on two 1-D curves, not filling the 2-D grid). This is expected/correct, not a bug — GEN-04's own success criterion only requires non-negative + sums to 1 + shape `(K,)`, not full support.

### Pattern 3: Closed-form MMD² via precomputed kernel matrix (GEN-05)
**What:** `MMD²(p,q) = pᵀKp + qᵀKq − 2pᵀKq` where `K` is the `(K,K)` Gram matrix `k(cᵢ,cⱼ) = exp(−‖cᵢ−cⱼ‖²/(2σ²))` over the **fixed** bin-centers (computed once per σ, not per training step).
**Example (verified numerically — MMD²(p,p)=0.0 exactly, no negative values across 2000 random trials in float32):**
```python
import torch

def gaussian_kernel_matrix(centers: torch.Tensor, sigma: float) -> torch.Tensor:
    """centers: (K,2). Returns (K,K) Gram matrix. Compute once per sigma; reuse every step."""
    sq_dists = torch.cdist(centers, centers, p=2) ** 2
    return torch.exp(-sq_dists / (2 * sigma ** 2))

def mmd2(p: torch.Tensor, q: torch.Tensor, kernel_matrix: torch.Tensor) -> torch.Tensor:
    """p, q: (K,) probability vectors. kernel_matrix: (K,K), precomputed. Returns scalar tensor."""
    pp = p @ kernel_matrix @ p
    qq = q @ kernel_matrix @ q
    pq = p @ kernel_matrix @ q
    return pp + qq - 2 * pq
```
`p_real` (fixed, `requires_grad=False`) and `q` (the circuit's differentiable output) can both be passed here — gradients only need to flow through `q`, which they do (verified: `q = quantum_layer(z)` retains `grad_fn`, and `p @ K @ q` differentiates through `q` normally since it's ordinary matmul).
**Defensive practice (optional but recommended):** clamp the result with `torch.clamp(value, min=0.0)` before use as a loss — mathematically MMD² is provably ≥0 for a PSD kernel (Gaussian is PSD), and empirical testing found no negative values, but clamping is a one-line guard against float32 rounding at K=400 scale that costs nothing.

### Anti-Patterns to Avoid
- **Using `PhotonicGenerator` + `VectorAdapter` as GEN-05's output path:** `VectorAdapter` center-crops/zero-pads raw tensor outputs to a target width without renormalizing. Verified directly: wrapping a raw `QuantumLayer` (natural width 462) in `VectorAdapter(400)` produced row sums of ~0.80–0.86, not 1.0 — silently violates GEN-04/GEN-05's normalization requirement. Use `QuantumLayer.simple(input_size, output_size=K)` directly instead (it applies `ModGrouping`, which sums rather than crops, and is verified to preserve `sum == 1`).
- **Recomputing the kernel matrix inside the MMD² function on every call:** the `(K,K)` Gram matrix depends only on fixed bin-centers and σ — compute it once (per σ) outside the training loop / test loop, pass it in.
- **Trusting `output_size=K` "runs without error" as proof it's correct:** `QuantumLayer.simple(input_size=2, output_size=400)` runs and returns a `(batch, 400)` tensor that sums to 1 — but only 3 of the 400 entries are ever nonzero (zero-padded), for any input `z` and any training. A shape/sum-only test would pass on this broken configuration; the pytest suite for GEN-02/GEN-05 should include a nonzero-support check (see Common Pitfalls) specifically to catch this class of failure.
- **Re-deriving `p_real` bin-edges differently from the bin-centers used in the kernel:** keep one grid definition (`make_bin_centers`) as the single source of truth consumed by both GEN-04 (via nearest-center assignment) and GEN-05 (via the kernel matrix), so indices line up 1:1.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Gaussian-distributed latent sampling with a given std | A hand-written `torch.randn(...) * std + mean` scattered across modules | `merlin.NormalLatent(dim, mean=0.0, std=2*math.pi).sample(batch_size)` | It's the exact class MerLin's own `PhotonicGenerator` defaults to; identical math, but importing it documents *why* `std=2π` (MerLin's own convention) rather than a magic number, and is one less thing to independently unit-test (already tested by MerLin's own test suite: batch-size/dtype validation, positional args, etc.) |
| Pairwise squared Euclidean distance for the kernel | Manual `((c[:,None,:]-c[None,:,:])**2).sum(-1)` broadcasting | `torch.cdist(centers, centers, p=2) ** 2` | Fewer opportunities for a broadcasting-shape bug; verified numerically stable and fast (400×400 Gram matrix build: ~4ms per σ) |
| Circuit sizing math ("how many modes/photons for N inputs") | Manually computing `n_modes = input_size+1`, photon placement, etc. | `QuantumLayer.simple(input_size, output_size)` | Already does this (verified: `n_modes = input_size+1`, alternating-mode photon placement, `MeasurementStrategy.probs(...)` default) — reimplementing it would just recreate `.simple()` with more bug surface |

**Key insight:** The only genuinely novel code in this phase is the MMD² closed-form and the bin-center/`p_real` machinery — everything latent- and circuit-related has an existing, tested MerLin building block. The risk in this phase isn't "what do I hand-roll," it's "which `input_size`/`output_size` combination is actually non-degenerate" (see Common Pitfalls).

## Common Pitfalls

### Pitfall 1: `output_size` silently degenerates when it exceeds the circuit's natural output width
**What goes wrong:** `QuantumLayer.simple(input_size=2, output_size=400)` builds and runs without any error or warning. The returned tensor has shape `(batch, 400)`, is non-negative, and each row sums to exactly 1.0 — every test in CONTEXT.md's locked verification list (shape, sum-to-1, no-error-forward-pass) would pass. But only 3 of the 400 entries are ever nonzero, for every input, forever (`ModGrouping` zero-pads rather than expanding when `output_size > natural_output_size`).
**Why it happens:** `.simple(input_size)` sets `n_modes = input_size + 1` and `n_photons = ceil(n_modes/2)`, computed in `ComputationSpace.UNBUNCHED` (default). The natural probability distribution width is `C(n_modes, n_photons)`. Verified table (installed merlin 0.4.0):

| `input_size` | `n_modes` | `n_photons` | natural output width |
|---|---|---|---|
| 2 | 3 | 2 | **3** |
| 5 | 6 | 3 | 20 |
| 8 | 9 | 5 | 126 |
| 9 | 10 | 5 | 252 |
| **10** | **11** | **6** | **462** ← first ≥400 |
| 11 | 12 | 6 | 924 |
| 12 | 13 | 7 | 1716 |

`ModGrouping` (`merlin/utils/grouping.py`) only does real "modulo-index-and-sum" regrouping when `output_size <= input_size` (its own `input_size` = the natural width). When `output_size > natural width`, it takes the `if self.output_size > self.input_size:` branch and just zero-pads. Verified directly: at `input_size=2, output_size=400`, `torch.nonzero(out[0])` = `[0,1,2]` only; at `input_size=10, output_size=400`, all 400 entries are nonzero and gradients flow to both trainable parameter tensors.
**How to avoid:** Use `input_size >= 10` if `K=400` is to be honored as written, OR reduce `K` to ≤ the natural width for whatever `input_size` is chosen. This is a locked-decision conflict (see Open Questions) — don't resolve it silently either direction; confirm with the owner per this project's "no silent unilateral design decisions" rule.
**Warning signs:** A "shape + sum-to-1" test passing is not sufficient evidence the encoding is correct. Add an explicit nonzero-support assertion (e.g., `assert (q > 0).sum() > K * 0.5` or similar, tuned to what's actually expected) to the GEN-02/GEN-05 pytest suite.

### Pitfall 2: `pytest` is not installed
**What goes wrong:** CONTEXT.md locks "automated pytest tests" as the verification method, but `pytest` is not in `requirements.txt` and not present in the venv (`ModuleNotFoundError: No module named 'pytest'`, verified directly).
**Why it happens:** Phase 1 only installed `merlinquantum`/`torch`/`scikit-learn` dependencies for the quickstart classifier; no test framework was ever added.
**How to avoid:** Install `pytest` into the venv and pin it in `requirements.txt` as an explicit Phase 2 setup task, before writing any test file.
**Warning signs:** `pytest` command not found / import error when a test file is first run.

### Pitfall 3: Bin resolution vs. ring gap — σ that's "too smooth" hides the two-ring structure
**What goes wrong:** A σ chosen purely by a naive "median pairwise distance" heuristic will be far larger than what distinguishes the two rings from the empty gap between them, producing an MMD² that looks small/well-behaved while `q` is actually blurred across both rings and the gap — the exact failure mode DESIGN_DECISIONS.md's `AC12 Bandwidth Sweep` finding warns about.
**Why it happens:** Verified geometry of the actual dataset (via direct computation, `make_circles(n_samples=400)` + the exact min-max normalization in `quickstart.py`, `random_state=42`):
- The two rings sit at **exact** radius 0.4 and 0.5 from the box center `(0.5, 0.5)` (no noise in `make_circles`, so each ring is a thin 1-D curve, not a band).
- Radial gap between the rings: **0.1** (in the normalized `[0,1]²` coordinate space).
- Median pairwise distance among bin-centers (20×20 grid, pad=0.1): **≈0.64** — over 6× the ring gap. A blind median-heuristic σ would completely blur the two rings together.
- Grid spacing at 20×20 over `[-0.1, 1.1]²`: **≈0.063** — close to (63% of) the ring gap, meaning even the finest σ in a sensible sweep is operating near the resolution limit of the (already-locked) K=400/20×20 grid.
**How to avoid:** Don't use a single median-heuristic σ. Sweep values that bracket the ring gap (0.1) from below and above — see the concrete grid below.
**Warning signs:** MMD² decreasing smoothly during training while generated/plotted samples (Phase 4) don't show two separated rings — the exact "looks good numerically, fails structurally" pattern already documented from the prior IQP-MMD project.

## Code Examples

### Verified: circuit build/forward timing at candidate `input_size` values
```
input_size=10, output_size=400: build 0.29s, forward batch=5 in 0.11s, train step batch=64 ≈ 0.28s/step
input_size=11, output_size=400: build 0.53s, forward batch=32 in 0.15s, train step batch=64 ≈ 0.32s/step
```
Neither is a Phase-2 blocker (Phase 2 doesn't run a training loop), and both stay well within Phase 3's July 25 checkpoint budget (a few hundred steps at ~0.3s/step is minutes, not hours).

### Verified: real data range after quickstart.py's exact normalization
```
raw make_circles(n_samples=400) range (factor=0.8 default, noise=None): x,y ∈ [-1, 1]
X_train_n (min-max on train only): exactly [0,1]² by construction
X_test_n (same train-derived min/max applied to test): approx [0.0089, 0.9990] × [0.0022, 1.0002]
  → test slightly overshoots [0,1] on the high end (~0.00025) due to train/test split variance
```
This confirms CONTEXT.md's "[0,1]-ish" assumption and justifies non-zero padding on the bin-center bounding box (both for real resolution near the rings and to safely contain the small test-set overshoot).

### Proposed padding and bandwidth values (Claude's Discretion items from CONTEXT.md)
- **Padding:** 10% of the `[0,1]` unit range on each side → bounding box `[-0.1, 1.1]²`. Rationale: comfortably contains the ~0.00025 test-set overshoot measured above, and leaves a visible margin around both rings (outer ring reaches radius 0.5 from center `(0.5,0.5)`, i.e. touches `x,y ∈ {0,1}` — some margin is needed so the outermost ring isn't sitted exactly on the grid boundary).
- **σ sweep (proposed, tied to the verified ring gap of 0.1 and grid spacing of ≈0.063):**

| σ | Rationale |
|---|---|
| 0.02 | Well below grid spacing — near-delta kernel; mostly diagnostic (expect noisy/harsh gradient signal), included as a lower bound |
| 0.05 | ≈ grid spacing (0.063) — resolves individual bins, should distinguish the two rings clearly |
| 0.1 | ≈ ring gap exactly — the boundary case; kernel starts bridging the two rings at this scale |
| 0.2 | 2× ring gap — visibly blurs ring separation; useful to demonstrate the "looks fine, structurally wrong" failure mode from the sweep, per the carried-forward lesson |
| 0.4 | ≈ 1/3 of the full padded domain (1.2) — heavily oversmoothed; a clear "too smooth" reference point |

This is a **proposed starting grid, not a locked value** (CONTEXT.md explicitly leaves exact σ values to research/planning) — Phase 4 is where the sweep gets evaluated against actual visual/structural ring recovery, per CONTEXT.md's deferred items.

## State of the Art

Not applicable in the usual "library version churn" sense — this is a fixed-version research codebase (`merlinquantum==0.4.0` pinned). The one relevant "state of the art" fact: `merlinquantum` 0.4.0 already ships a purpose-built generative-model scaffold (`PhotonicGenerator`, added recently enough that it wasn't previously known to this project per DESIGN_DECISIONS.md) — but as established above, its `VectorAdapter` output-shaping path doesn't fit a probability-vector target, so this phase should use `QuantumLayer.simple()` directly rather than the newer scaffold.

## Open Questions

1. **`input_size`/latent-dimensionality vs. `K≈400`: these two locked CONTEXT.md decisions are mutually incompatible as stated, and this research cannot silently resolve it.**
   - What we know: `input_size=2` (the locked starting dimensionality) yields a natural output width of only 3, so `output_size=400` zero-pads 397 entries permanently. `input_size=10` is the smallest value that makes `output_size=400` non-degenerate (natural width 462), verified cheap to build/run (~0.3s/train-step at batch=64).
   - What's unclear: whether the owner intended "latent dim starts at 2" as a hard constraint on `QuantumLayer.input_size` specifically (as CONTEXT.md's phrasing states: "there's no separate noise dim chosen independently of circuit size"), or as a general "keep it small" instruction that should yield to the more specific, already-quantified `K≈400` decision.
   - Recommendation: bring this to the owner explicitly before planning locks in a value. If forced to pick a default for planning purposes, recommend **`input_size=10`** (satisfies `K=400` cleanly, still cheap, still well under the `.simple()` cap of 19, still a Phase 3/4-tunable knob) — but flag this in the plan as a deviation from CONTEXT.md's literal "start at 2" wording that needs the owner's explicit sign-off, consistent with this project's "no silent unilateral design decisions" rule.

2. **Padding percentage and σ grid** — proposed concrete values given above (10% padding; σ ∈ {0.02, 0.05, 0.1, 0.2, 0.4}), grounded in the verified ring-gap (0.1) and grid-spacing (≈0.063) geometry, but these were explicitly left to research/planning discretion in CONTEXT.md and haven't been validated against actual training behavior (that's Phase 3/4's job).

3. **`p_real` data source** — CONTEXT.md doesn't specify whether `p_real` should be computed from `X_train` only or from the full (train+test) circles sample. Recommendation: `X_train` only, so the held-out `X_test` set remains available for a genuinely held-out MMD statistic in Phase 5 (BMK-01) rather than having already been baked into the training target.

## Sources

### Primary (HIGH confidence — verified by direct execution against the installed venv)
- `C:\Users\cuqui\merlin-quantum-case-study\venv\Lib\site-packages\merlin\algorithms\layer.py` — `QuantumLayer.simple()` implementation (n_modes/n_photons sizing, `ModGrouping` wiring, `output_size` handling)
- `C:\Users\cuqui\merlin-quantum-case-study\venv\Lib\site-packages\merlin\utils\grouping.py` — `ModGrouping`/`LexGrouping` (confirmed the zero-pad-when-`output_size>natural_width` behavior directly in source, then reproduced it empirically)
- `C:\Users\cuqui\merlin-quantum-case-study\venv\Lib\site-packages\merlin\models\photonic_generator.py` — `PhotonicGenerator`, `NormalLatent`, `VectorAdapter`, `ImageAdapter` source
- Direct script execution via `./venv/Scripts/python.exe` (natural-output-width table across `input_size` 2–14; zero-padding vs. real-grouping behavior at `input_size=2` vs `10`/`11`; gradient-flow check via `loss.backward()`; timing at batch=5/32/64; `make_circles`+quickstart-normalization data-range check; ring-radius/gap geometry check; MMD² non-negativity check over 2000 random trials; kernel-matrix build/eval timing at K=400)
- `C:\Users\cuqui\merlin-quantum-case-study\quickstart.py` — verified-working `QuantumLayer` usage pattern this phase extends
- `C:\Users\cuqui\merlin-quantum-case-study\DESIGN_DECISIONS.md`, `.planning/phases/02-generator-data-loss-infrastructure/02-CONTEXT.md`, `.planning/REQUIREMENTS.md`, `.planning/STATE.md` — locked project decisions and requirements

### Secondary (MEDIUM confidence)
None used — all claims in this document trace to source code read directly or to scripts executed directly against the installed environment.

### Tertiary (LOW confidence)
None.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — small, already-installed dependency set; only addition (`pytest`) is a standard, uncontroversial choice
- Architecture: HIGH — every code pattern shown was executed and its output captured above, not just read from source
- Pitfalls: HIGH — the `input_size`/`output_size` degeneracy and the `pytest`-missing gap were both discovered and confirmed by direct execution, not speculation

**Research date:** 2026-07-19
**Valid until:** Tied to `merlinquantum==0.4.0` staying pinned (per requirements.txt) — re-verify the `output_size`/`ModGrouping` table if the MerLin version changes.
