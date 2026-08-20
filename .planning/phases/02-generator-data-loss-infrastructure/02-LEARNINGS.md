---
phase: 2
phase_name: "Generator Data & Loss Infrastructure"
project: "MerLin Photonic Generative Modeling"
generated: "2026-08-20"
counts:
  decisions: 6
  lessons: 5
  patterns: 5
  surprises: 4
missing_artifacts:
  - "02-VERIFICATION.md"
  - "02-UAT.md"
---

# Phase 2 Learnings: Generator Data & Loss Infrastructure

## Decisions

### Bin-center grid: K=400 (side=20) over padded [-0.1, 1.1]^2
Locked (from 02-CONTEXT.md) and implemented as `make_bin_centers(side=20, lo=-0.1, hi=1.1)`, producing a deterministic uniform grid via `numpy.linspace`/`meshgrid`.

**Rationale:** Covers the circles dataset's min-max-normalized [0,1]^2 range plus 10% padding on each side — contains the ~0.00025 test-set overshoot from quickstart.py's train-derived normalization, and leaves margin around the outer ring (which touches x,y in {0,1}).
**Source:** 02-01-PLAN.md, 02-01-SUMMARY.md

---

### Latent dimension fixed at 10, not 2
`sample_latent` uses `merlin.NormalLatent(dim=10, mean=0.0, std=2*pi)`.

**Rationale:** `input_size` directly determines `QuantumLayer.simple`'s natural output width. `input_size=2` yields a natural width of only 3, so `output_size=400` would be 397/400 zero-padded and permanently degenerate. `input_size=10` is the smallest value whose natural width (462) exceeds K=400, making `ModGrouping` do real regrouping instead of zero-padding. This was verified during 02-RESEARCH.md and corrected in 02-CONTEXT.md with explicit owner sign-off.
**Source:** 02-02-PLAN.md, 02-02-SUMMARY.md

---

### Latent noise scale std=2π, not [0,1]
`NormalLatent` is used with `std=2*math.pi` rather than a hand-rolled `torch.randn` or a [0,1]-scaled sampler.

**Rationale:** This is MerLin's own `PhotonicGenerator` convention (per 02-RESEARCH.md "Don't Hand-Roll"), not a project-specific choice. quickstart.py's [0,1] min-max normalization was that script's own choice for its classifier input, not a MerLin requirement — `angle_encoding_scale` defaults to 1.0 (no automatic rescaling).
**Source:** 02-02-PLAN.md

---

### p_real computed from X_train only, not the full dataset
`compute_p_real` is called with `X_train` exclusively across this phase's tests and call sites.

**Rationale:** Keeps `X_test` genuinely held out for a later, truly held-out MMD statistic (BMK-01, Phase 5) rather than baking test data into the Phase 3 training target. Per 02-RESEARCH.md's Open Question 3 recommendation.
**Source:** 02-03-PLAN.md

---

### make_circles seeded with random_state=42, deviating from quickstart.py
`load_circles_data()` calls `make_circles(n_samples=400, random_state=42)`, whereas quickstart.py's own call is unseeded.

**Rationale:** quickstart.py only needed the *split* to be reproducible (via `train_test_split(random_state=42)`), not the raw circle points, since it was a one-off classifier demo. `p_real` in this project must be a stable Phase 3 training target and a stable Phase 5 benchmark reference, so the underlying data generation itself needs seeding too — without it, two calls to `load_circles_data()` produced different data despite the split being "seeded."
**Source:** 02-03-SUMMARY.md

---

### MMD² kernel/loss implemented in torch, not numpy
`gaussian_kernel_matrix`/`mmd2` in `generator/mmd.py` use `torch.cdist`, `torch.exp`, and `@` matmul throughout.

**Rationale:** `mmd2`'s `q` argument must stay on PyTorch's autograd graph since it comes from a trainable `QuantumLayer` forward pass. A numpy implementation would look identical in isolated tests (finite, non-negative, symmetric) but would silently sever gradient flow to the circuit, meaning training would never actually update the circuit's parameters. Flagged as the single most important design choice in this plan.
**Source:** 02-04-PLAN.md, 02-04-SUMMARY.md

---

## Lessons

### pytest.approx without `==` silently compares nothing
Occurred three separate times across this phase (02-02, and twice more in 02-03) as `assert pytest.approx(x, tol)` — a no-op assertion that always passes and, on a grad-tracked tensor, actually crashes with `RuntimeError: Can't call numpy() on Tensor that requires grad`.

**Context:** Found while reviewing owner drafts of `tests/test_noise.py` and `tests/test_p_real.py`. Fixed by switching to `torch.allclose`/`torch.equal` for tensor comparisons, or `float(x) == pytest.approx(...)` for scalar comparisons. Documented separately at `~/.claude/learnings/2026-07-19-pytest-approx-misuse-grad-tensor.md`.
**Source:** 02-02-SUMMARY.md, 02-03-SUMMARY.md, 02-04-SUMMARY.md

---

### torch.cdist has measurable float32 asymmetry and non-zero self-distance
`torch.cdist(centers, centers)` is not bit-exact symmetric (~1e-6 asymmetry) and its diagonal is not bit-exact 0 (~5e-4 non-zero self-distance), due to float32 cancellation in its internal `||a||^2 + ||b||^2 - 2ab` formula.

**Context:** Discovered running `test_kernel_matrix_sanity` in 02-04 — these artifacts get amplified by the `/(2σ²)` division at small σ (0.02, 0.05), causing default-tolerance `torch.allclose` checks on kernel symmetry and diagonal to fail. Resolved with measured, loosened tolerances (atol=1e-4 symmetry, atol=1e-3 diagonal) rather than papering over with an overly loose default.
**Source:** 02-04-SUMMARY.md

---

### Gaussian kernel underflows to exact zero at small σ over this grid
At σ=0.02 (and likely σ=0.05), the exponent `-dist²/(2σ²)` reaches deeply negative values (≈-3600 at σ=0.02 for far-apart bin-center pairs on the padded [-0.1,1.1]² grid, max pairwise distance ≈1.697) that underflow to exactly 0.0 in float32 (underflow threshold ≈ exponent -87.3).

**Context:** This is expected float32 behavior, not a kernel-formula bug. A strict `(0, 1]` off-diagonal positivity assertion would deterministically fail at small σ for reasons unrelated to correctness — the plan explicitly calls out using non-strict `[0, 1]` bounds instead.
**Source:** 02-04-PLAN.md

---

### Constructing a second nn.Module instance breaks gradient-flow tests
An owner's first draft of `tests/test_mmd.py` constructed `QuantumLayer.simple(...)` twice — once for the forward pass used to compute the loss, and again inside the parameter-check loop — so the parameters being asserted-on were never part of the backward graph at all, and the gradient-flow test was vacuous.

**Context:** Found during full rewrite of `tests/test_mmd.py` in 02-04. Fixed by constructing exactly one `quantum_layer` instance and reusing it for both the forward pass and the parameter check.
**Source:** 02-04-SUMMARY.md

---

### tests/__init__.py is required, not redundant, once multiple test files exist
Without `tests/__init__.py`, pytest's rootdir-based import mechanism can silently produce duplicate-module errors as more test files accumulate under `tests/`.

**Context:** Called out explicitly in 02-01-PLAN.md's Task 1 instructions as something not to skip even though it looks like dead weight with only one test file present at the time.
**Source:** 02-01-PLAN.md

---

## Patterns

### Precomputed Gram-matrix MMD² with kernel passed in, never recomputed inside the loss
`gaussian_kernel_matrix(centers, sigma)` is computed once per σ and passed into `mmd2(p, q, kernel_matrix)` as a parameter, rather than recomputed on every call.

**When to use:** Any repeated-evaluation loss/metric over a fixed set of reference points (e.g. a training loop calling the loss every step) — avoids O(K²) kernel recomputation on the hot path. Called out explicitly as an anti-pattern to avoid in 02-RESEARCH.md.
**Source:** 02-04-PLAN.md

---

### Bin-center grid as single shared source of truth, passed as a parameter rather than re-imported
`generator/data.py` and `generator/mmd.py` both take `bin_centers` as a function parameter and never import `make_bin_centers` internally — only the test files and eventual training loop construct the grid and pass it through.

**When to use:** When multiple independent components (histogram, kernel) must agree on the exact same reference geometry — prevents silent drift between two separately-constructed grids and keeps each module's dependency surface minimal/testable in isolation.
**Source:** 02-03-PLAN.md, 02-04-PLAN.md

---

### Reproducibility tests must compare two independent calls, not a value to itself
`test_reproducibility`-style checks call the function under test twice and compare the two outputs (`torch.equal(a, b)` where `a` and `b` come from separate calls) — never `torch.equal(x, x)`, which is a tautology.

**When to use:** Any test whose purpose is to prove determinism/reproducibility across repeated invocations (seeded RNG, deterministic algorithms). A tautological self-comparison will pass even on a broken/non-deterministic implementation.
**Source:** 02-03-SUMMARY.md

---

### Self-comparison sanity check (MMD²(p,p) ≈ 0) as a cheap correctness gate before integration
Before wiring a loss function into a training loop, verify the fundamental mathematical property (self-distance ≈ 0) against real project data, not just synthetic stand-ins — across the full hyperparameter sweep (all 5 σ values).

**When to use:** Any distance/divergence metric being newly implemented (MMD, KL, Wasserstein, etc.) — catches a broken kernel/formula that would otherwise look "fine" (finite, non-negative) while never actually driving training toward the target distribution.
**Source:** 02-04-PLAN.md, 02-04-SUMMARY.md

---

### Explicit pitfall-guard regression test, verified to actually fail on the bad configuration
For `test_pitfall_guard` in `tests/test_noise.py`, the plan required temporarily reverting to the known-bad configuration (`input_size=2`) locally to confirm the new assertion actually fails on it, then reverting back — rather than trusting the assertion's logic alone.

**When to use:** Whenever adding a regression test for a previously-hit bug/degeneracy — proves the test has real discriminating power (e.g. `(out > 0).sum(dim=1).float().mean() > 50` distinguishes "broad support" from "3 nonzero bins") rather than being coincidentally satisfied by both the correct and incorrect implementations.
**Source:** 02-02-PLAN.md

---

## Surprises

### Owner's first draft of generator/data.py had three fatal, independent bugs
Type annotations referencing undefined names (`-> (X_train, X_test):`) causing an eager-eval `NameError`; `make_circles`'s `(X, y)` return unpacked as if it were already a train/test split and then fed into `train_test_split` a second time with mismatched unpacking; `MinMaxScaler` fit twice independently on `X_train` and `X_test` instead of once on `X_train` and reused via `.transform()`.

**Impact:** Module failed to import entirely (`pytest --collect-only` errored) before any test logic could even run — required a full rewrite of `load_circles_data()` to mirror quickstart.py's manual min-max normalization.
**Source:** 02-03-SUMMARY.md

---

### Owner's first draft of tests/test_mmd.py failed to collect and got most checks wrong
Referenced a nonexistent module (`quantum.layer` instead of `merlin.QuantumLayer`); used `np.random.randn(10)` as a stand-in for `p_real` (wrong library, wrong shape — 10 is the latent dim, not the 400 bin count — and not a valid probability vector); passed a probability vector where bin-center coordinates were expected; used exact float equality instead of `pytest.approx`; referenced an undefined `p_real` in the gradient test and passed a raw NumPy array into `QuantumLayer.forward()`.

**Impact:** Required a full rewrite of the test file rather than incremental fixes — none of the 4 required checks from the plan were correctly implemented in the first draft.
**Source:** 02-04-SUMMARY.md

---

### make_circles non-determinism was not caught until the reproducibility test actually ran
Even after fixing the three fatal bugs and the pytest.approx misuse, `test_reproducibility` still failed because `make_circles(n_samples=400)` has no `random_state`, so raw circle points differ every call regardless of `train_test_split`'s seed.

**Impact:** Surfaced a real, previously-unnoticed non-determinism gap inherited from quickstart.py's own (unseeded) data generation — the plan's own reproducibility must-have would have silently failed on it if the test hadn't specifically compared two independent calls.
**Source:** 02-03-SUMMARY.md

---

### None of Phase 2's four plans were committed to git as they were completed
All four SUMMARY.md files (02-01 through 02-04) independently note that their respective files remained untracked/modified in the working tree, with each summary recommending committing before the next plan starts — the gap persisted across the entire phase rather than being caught after the first occurrence.

**Impact:** By the end of 02-04, all of Phase 2's code (`generator/`, `tests/`, `pytest.ini`, modified `requirements.txt`) was still uncommitted, despite four separate plans completing and each summary flagging the same outstanding gap.
**Source:** 02-01-SUMMARY.md, 02-02-SUMMARY.md, 02-03-SUMMARY.md, 02-04-SUMMARY.md
