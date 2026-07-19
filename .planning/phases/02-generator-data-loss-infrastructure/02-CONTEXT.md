# Phase 2: Generator Data & Loss Infrastructure - Context

**Gathered:** 2026-07-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Build and independently verify, before wiring together: latent noise sampling/encoding, the fixed K bin-centers, the precomputed real-data histogram (`p_real`), and the closed-form MMD² loss. This phase does not include the training loop (Phase 3) or generative quality tuning (Phase 4).

</domain>

<decisions>
## Implementation Decisions

### Bin-center layout (GEN-03)
- K ≈ 400 bin-centers (e.g. 20×20), balancing resolution against MerLin simulation cost.
- Uniform grid arrangement — not ring-aware/adaptive density. Simpler to implement and verify; ring-aware density was considered and rejected for this phase given the timeline.
- Coverage: circles dataset's (x,y) bounding box plus padding (not the exact/tight data range).
- Must be fully deterministic/reproducible across runs — no randomness in bin-center generation (this is also required by GEN-03's own success criterion).

### Kernel & bandwidth (GEN-05)
- Gaussian kernel over **Euclidean distance** between bin-center coordinates: `k(cᵢ,cⱼ) = exp(-‖cᵢ-cⱼ‖²/(2σ²))`. This is a different formula from the owner's prior IQP-MMD project (`C:\Users\cuqui\iqp-mmd-barren-plateau`), which used Hamming-distance Gaussian kernels over binary bitstrings — that machinery doesn't port directly since bin-centers here are continuous 2D coordinates.
- Bandwidth: sweep across a few σ values rather than committing to one fixed value (e.g. via a single median-heuristic number). This carries forward the reusable lesson from the prior project's `AC12 Bandwidth Sweep` finding: MMD² can hit a near-zero value while the learned distribution still fails to match the target's real structure (there, σ controlled a trainability-vs-fine-structure tradeoff; here the equivalent risk is a σ large enough to blur "on a ring" vs "in the gap between rings"). No specific σ grid locked yet — left for research/planning to propose reasonable values given the ~[0,1]-padded coordinate scale.

### Latent noise encoding (GEN-02)
- Distribution: Normal (Gaussian), matching MerLin's own built-in convention (`merlin.models.photonic_generator.NormalLatent`), not a project-specific choice.
- Scale: MerLin's own default `std=2π` when no latent distribution is explicitly passed to `PhotonicGenerator` — **not** the `[0,1]` min-max normalization the quickstart classifier happened to use. That `[0,1]` convention was quickstart.py's own choice, not a MerLin requirement (`_build_simple_circuit`'s `angle_encoding_scale` defaults to `1.0`, i.e. no automatic rescaling). Use MerLin's own generator-code convention as the more directly relevant precedent.
- Dimensionality: **`input_size=10`** (corrected during `/gsd:plan-phase 2` research — see below), not 2. Latent dim and `QuantumLayer.input_size` are the same number in MerLin (confirmed via `PhotonicGenerator`/`NormalLatent` source) — there's no separate "noise dim" chosen independently of circuit size. `.simple()` caps `input_size` at 19 (`n_modes = input_size+1 ≤ 20`); bigger values mean richer encoding but real simulation-cost growth.
  - **Correction (2026-07-19, during plan-phase research):** the original "start at 2" recommendation above was wrong. `input_size=2` yields a natural output width of only 3 (2 photons over 3 modes) — `QuantumLayer.simple(input_size=2, output_size=400)` runs without error and sums to 1, but 397 of the 400 bins are permanently zero-padded by `ModGrouping`, silently defeating K=400's whole purpose (representing two separate rings). Verified by direct execution against the installed venv. `input_size=10` is the smallest value where the natural output width (462) exceeds K=400, so `ModGrouping` does real regrouping instead of zero-padding. Verified cheap (~0.3s/training-step at batch=64 at input_size=10) — no blocker for the July 25 checkpoint. Confirmed with the owner: keep K=400 (shrinking K to fit input_size=2 would worsen the already-tight resolution margin against the measured 0.1 ring gap), raise input_size to 10 instead.

### Research pointer for implementation
- MerLin ships a **purpose-built `PhotonicGenerator` class** (`merlin/models/photonic_generator.py`) with `NormalLatent`, `VectorAdapter`/`ImageAdapter` output shaping, and multi-head support — built for exactly this generative-model pattern. This wasn't previously known/recorded anywhere in the project. The phase-researcher should investigate whether to build on `PhotonicGenerator` directly (e.g. `VectorAdapter` for shaping raw measurements into the K-dimensional probability vector) rather than reimplementing noise sampling / output shaping from scratch, before GEN-02 is implemented.
- `QuantumLayer.simple(input_size, output_size)` supports an **independent** `output_size` via `ModGrouping`, which regroups the circuit's natural output distribution to any requested width. This means `output_size = K` (~400) is directly achievable without a separate binning/mapping step — worth the researcher confirming this is the right mechanism for producing `q` over the K bin-centers (GEN-05's model output).

### Independent verification method
- Automated pytest tests, not manual scripts — one test per component, asserting the roadmap's stated properties:
  - Noise encoding: sampled/encoded tensor is a valid `QuantumLayer` input on each call (correct shape/dtype, forward pass runs without error).
  - Bin-centers: exactly K points, deterministic/reproducible across repeated calls, span the padded bounding box.
  - `p_real`: non-negative, sums to 1, shape `(K,)`.
  - MMD² loss: finite, non-negative for arbitrary `(p, q)` — **plus** a specific sanity check that `MMD²(p, p) ≈ 0` (a fundamental MMD property; catches a broken kernel/formula before it reaches Phase 3 training).
- These tests run and pass before the four components are wired together into the training loop (Phase 3).

### Claude's Discretion
- Exact σ grid values for the bandwidth sweep (left for research/planning, scaled to the padded coordinate range).
- Test file organization/naming conventions (no existing test suite in this repo to conform to).
- Exact padding percentage for the bin-center bounding box.

</decisions>

<specifics>
## Specific Ideas

- Reuse the *lesson*, not the code, from the prior IQP-MMD project's bandwidth sweep: don't trust a single σ, and don't trust MMD² alone as proof of distribution match — verify visually/structurally once Phase 4 produces samples.
- MerLin's `PhotonicGenerator`/`NormalLatent`/`VectorAdapter` (found during this discussion, not previously documented anywhere in the project) is a strong reuse candidate for GEN-02 and part of GEN-05's output shaping.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within Phase 2 scope. (Simulation-cost tuning, ring-aware bin-center density, and final σ/dimensionality values were explicitly deferred to Phase 3/4 tuning, not to a separate phase — they remain open parameters within this phase's components, not new capabilities.)

</deferred>

---

*Phase: 02-generator-data-loss-infrastructure*
*Context gathered: 2026-07-19*
