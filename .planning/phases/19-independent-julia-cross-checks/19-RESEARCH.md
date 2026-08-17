# Phase 19: Independent Julia Cross-Checks - Research

**Researched:** 2026-08-17
**Domain:** Cross-language (Python/Perceval -> Julia/Yao.jl+BosonSampling.jl) numerical verification of an IQP-photonic simulation pipeline
**Confidence:** MEDIUM-HIGH (Python side and Phase 14 environment: HIGH, read directly from this repo. BosonSampling.jl API: MEDIUM — sourced from the package's GitHub `main` branch, not confirmed against the exact installed v1.0.2 tag or Context7. Yao.jl API: MEDIUM — WebSearch + this repo's own working hello-world script.)

## Summary

This phase ports no code — it reproduces three narrow numeric results from this repo's Python/Perceval pipeline in an independently-built Julia program and diffs the two. All three Python-side reference computations are exact, deterministic functions already implemented, tested, and locked in `iqp_photonic_encoding.py` and `hardness/loss_model*.py`; the plan does not need to derive new physics, only decide how to express the *same* physical circuits in Yao.jl's qubit-gate language (VERIFY-02) and BosonSampling.jl's linear-optics language (VERIFY-03/04), then compute a total variation distance (TVD) against Python's numbers using the exact same formula (`total_variation_distance` in `iqp_photonic_encoding.py`: `0.5 * sum(|a(x)-b(x)|)` over the union of keys).

The most consequential finding: BosonSampling.jl has a **native uniform-loss API** (`UniformLossInterferometer(η, U_physical)` in `src/types/loss.jl`), which is exactly what VERIFY-04's CONTEXT.md asked to check for first. It works by doubling the mode count (m -> 2m) and inserting a beamsplitter of transmissivity η in front of every physical mode, with the extra m modes representing the lost-photon "environment" — mechanistically the *same physical model* Park & Oh's commutation argument (already cited in this repo's `loss_model.py`) justifies, but a *structurally different implementation* from Perceval's `pcvl.LC` component, which is exactly the kind of independence VERIFY-04 wants. Using it requires converting both the interferometer (`to_lossy(interf)` or `UniformLossInterferometer(η, U)`) and the input state (`to_lossy(input)`) to the doubled-mode representation, and the output distribution reported by `compute_probability!`/`noisy_distribution` is over the full 2m-mode space — the planner must account for marginalizing/summing over the environment (loss) modes to get a distribution over just the physical m modes, this is not automatic.

For VERIFY-03's weight-2 case, the "independent, not a mechanical port" requirement is real friction: Perceval's `heralded_cz` is a specific pre-built catalog gate (the Knill CZ construction, arXiv:quant-ph/0110144, 6 dual-rail modes: 4 data + 2 heralded ancilla, herald success 2/27, confirmed empirically in this repo's `heralded_cz_derisking.py`). BosonSampling.jl has no equivalent catalog of named multi-qubit gates — it only exposes primitive beamsplitters/phase-shifters/`UserDefinedInterferometer(U::Matrix)`. An independent Julia build therefore means deriving/sourcing the Knill CZ's own 6x6 (or equivalent) unitary from the *literature* (not by numerically extracting Perceval's already-built matrix, which would just be comparing Python to itself) and constructing it in Julia via `UserDefinedInterferometer`, then heralding by hand (post-select on the two ancilla output modes each having exactly 1 photon, exactly mirroring Python's own herald-accounting logic in `photonic_weight2_iqp_distribution`). This is flagged as an **open question requiring literature lookup during planning/execution**, not resolved here.

**Primary recommendation:** Build all three cross-checks directly against the *dual-rail-equivalent* representation of this repo's polarization encoding, not the polarization/PBS machinery itself — BosonSampling.jl has no polarization/PBS component, and the CONTEXT.md's "independent build" requirement makes replicating Perceval's PBS-wrapping pointless anyway. Since a bare PBS is a deterministic, phase-neutral basis change (already confirmed in this repo, `iqp_photonic_encoding.py`'s port-convention comments and `test_pbs_conversion_is_phase_neutral_for_computational_basis`), the polarization encoding and a plain 2-mode-per-qubit dual-rail encoding are physically equivalent for every quantity this phase measures (probabilities over the computational-basis bitstring). Use n modes-per-qubit=2, bit=0 -> photon in "upper" mode, bit=1 -> photon in "lower" mode, Hadamard-conjugation = 50/50 beamsplitter (already proven correct in `hello_bosonsampling.jl`), and weight-1 Z-phase = `phase_shift`.

## Standard Stack

### Core (already installed, Phase 14 go/no-go, do not re-verify)
| Package | Version | Purpose | Source |
|---------|---------|---------|--------|
| Julia | 1.10.11 LTS | runtime | `julia/README.md` |
| Yao.jl | 0.9.1 | qubit circuit simulation (VERIFY-02) | `julia/Project.toml`, `julia/Manifest.toml` |
| BosonSampling.jl | 1.0.2 | linear-optics/Fock-state simulation (VERIFY-03, VERIFY-04) | `julia/Project.toml`, `julia/Manifest.toml` |

No new packages needed. `julia --project=julia` activates this environment from repo root; `Pkg.instantiate()` was already run in Phase 14.

### Alternatives Considered
None — CONTEXT.md and Phase 14 already locked this toolchain. No alternative research needed.

## Architecture Patterns

### File layout (extends Phase 14's `julia/` dir, same conventions as `hello_*.jl`)
```
julia/
├── Project.toml, Manifest.toml   # unchanged from Phase 14
├── hello_yao.jl                  # Phase 14 (existing, don't modify)
├── hello_bosonsampling.jl        # Phase 14 (existing, don't modify)
├── verify_qubit_iqp.jl           # VERIFY-02 — new
├── verify_photonic_iqp.jl        # VERIFY-03 (weight-1 + weight-2) — new
└── verify_loss_model.jl          # VERIFY-04 — new
```
Each Phase 14 script follows a fixed shape worth reusing exactly: print Julia/package version banner -> build circuit -> compute -> `@assert isapprox(...)` against a hand-known or externally-supplied value -> `println("PASS: ...")`. New scripts should keep this shape but source the "known value" from a **Python-generated reference file** (see below) rather than a hand-derived analytical constant, since here the reference is itself a computed distribution, not a closed form.

### Pattern: Python -> file -> Julia diff bridge
There is no existing IPC/data-bridge convention between the Python and Julia sides in this repo (Phase 14 only ran standalone hello-worlds). Recommended pattern for the planner: a small Python script (e.g. `julia/generate_reference.py` or reuse an existing results-writing convention) that calls the already-implemented, already-tested Python functions (`exact_qubit_iqp_distribution`, `photonic_iqp_distribution`, `photonic_weight2_iqp_distribution`, `photonic_iqp_distribution_lossy`, `photonic_weight2_iqp_distribution_lossy`) for the agreed shared test cases and dumps `{bitstring: probability}` dicts to JSON (Julia's `JSON.jl` is NOT in `Project.toml` — either add it, or use a dependency-free format: CSV via Julia's stdlib `DelimitedFiles`, which BosonSampling.jl already pulls in transitively per Manifest.toml, is a lower-friction choice that avoids a new Project.toml dependency). Julia then reads this file, computes its own independently-built distribution, and computes TVD against it directly in Julia (reimplementing the one-line TVD formula in Julia — trivial, and avoids any need to round-trip Julia's numbers back to Python).

### Anti-Patterns to Avoid
- **Extracting Perceval's already-built unitary matrix (e.g. `heralded_cz` circuit's `.compute_unitary()`) and hardcoding those literal numbers into Julia's `UserDefinedInterferometer`.** This produces agreement by construction (both sides run the same matrix), which is exactly the "cosmetic, not meaningful" cross-check CONTEXT.md's locked decision warns against for VERIFY-03. The Knill CZ unitary must come from an independent source (the original paper, or an independent re-derivation) for the check to mean anything.
- **Mechanically re-implementing Perceval's PBS/WP/HWP polarization machinery in Julia.** BosonSampling.jl has no polarization component at all — the natural, idiomatic Julia equivalent is a plain dual-rail (2-mode-per-qubit) construction, not a polarization simulation. Trying to force polarization semantics onto BosonSampling.jl's plain-Fock-state model would itself be a kind of indirect port and adds needless complexity.
- **Reporting TVD against Phase 18's *pooled 5-draw mean* CSV numbers directly.** See Pitfall 4 below — those numbers are averages over 5 independently random `thetas` draws per (n, η) cell, not a single reproducible circuit instance. A cross-check needs a single, fixed θ draw.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|--------------|-----|
| Uniform per-mode loss model in Julia | A hand-attenuation of the exact distribution (mixing amplitudes/probabilities manually) | `BosonSampling.UniformLossInterferometer(η, U_physical)` / `to_lossy(...)` (native, `src/types/loss.jl`) | It's the strongest independence guarantee available (a genuinely different mechanism from Perceval's `LC` component — beamsplitter-to-environment-mode model vs. Perceval's lossy-channel component) and it already exists in the installed package; hand-attenuation was explicitly named in CONTEXT.md as the *fallback only if no native API exists* — one does. |
| TVD computation | A new Julia TVD helper with different edge-case handling | Reimplement the exact one-line formula from `iqp_photonic_encoding.py::total_variation_distance` (`0.5 * sum(|a(x)-b(x)|)` over the union of keys) | Keeps the comparison metric identical on both sides; any deviation in TVD definition would itself become a false source of disagreement. |
| Bell-state / 50-50-beamsplitter sanity checks | New from-scratch spot checks | Phase 14's `hello_yao.jl` / `hello_bosonsampling.jl` (already passing) | Confirms the toolchain baseline is still working before building on top of it; no need to re-derive. |

**Key insight:** every quantity Julia needs to reproduce is already a known, tested, exact Python function output — the Julia work is entirely about faithfully building an *independent* implementation of the same physics, not about deriving anything new.

## Common Pitfalls

### Pitfall 1: Yao.jl's bit-ordering differs from this repo's Python convention
**What goes wrong:** `hello_yao.jl`'s own comment states Yao's `probs()` is little-endian (qubit 1 = least-significant bit), i.e. index order `|00>, |10>, |01>, |11>`. Python's `exact_qubit_iqp_distribution` explicitly documents qubit 0 as the **most-significant bit** (`bit_k = (i >> (n-1-k)) & 1`). These are opposite conventions.
**Why it happens:** Two independently-designed simulators picked opposite default orderings — extremely common, and exactly why CONTEXT.md's "mode ordering" pitfall category was called out in advance.
**How to avoid:** Do not compare index-for-index. Convert Yao's `probs()` output to a `{bitstring: probability}` dict using Yao's own known bit convention (verify empirically, the same way `hello_yao.jl` did, don't assume), and diff the two *dicts* (keyed by bitstring, e.g. `"01"`) via TVD, which is order-independent by construction as long as both sides use the same key semantics (qubit k's actual value, not its position in a positional index).
**Warning sign:** A TVD that's suspiciously close to 1.0 rather than ~0 for a case where the two implementations should trivially agree (e.g. symmetric thetas) is the classic ordering-bug signature — check this before doing anything else if VERIFY-02 fails.

### Pitfall 2: Yao's exact diagonal-phase convention must be derived, not assumed to be `Rz` with no adjustment
**What goes wrong:** Python's weight-1 generator gate is `diag(e^{iθ}, e^{-iθ})` (an exact match, not "up to global phase," per the module's own docstring). Yao's standard `Rz(φ)` gate is `diag(e^{-iφ/2}, e^{iφ/2})`.
**How to avoid:** These are the *same* matrix at `φ = -2θ` (both diagonal, entry-for-entry — verify this algebraically before coding, not just assume). So `put(k => Rz(-2*theta))` should reproduce Python's `WP(theta, 0)` exactly if applied at the same point in the same circuit (after a Hadamard-equivalent state prep, before a Hadamard-equivalent conjugation). Confirm numerically against `expected_single_qubit_probs` (`P(H)=cos²θ, P(V)=sin²θ`) as a first sanity check before trusting the n=2/n=3 IQP comparison.
**Warning sign:** A constant-factor-2 discrepancy in the effective phase angle is the tell (e.g. results matching what you'd get at `2θ` or `θ/2` instead of `θ`).

### Pitfall 3: BosonSampling.jl's `UniformLossInterferometer`/`to_lossy` outputs live in a doubled mode space
**What goes wrong:** Calling `compute_probability!`/`noisy_distribution` on a lossy (`to_lossy`-converted) circuit returns amplitudes/probabilities over `2m` modes (m physical + m "environment"/loss modes), not `m`. A caller that forgets this and tries to directly compare against an m-mode Python distribution will get a shape mismatch or, worse, silently wrong numbers if they truncate incorrectly.
**Why it happens:** This is the package's chosen internal representation for loss (a beamsplitter-to-environment-mode virtual interferometer) — not a bug, but an unavoidable API shape that must be explicitly handled: the planner needs a step that marginalizes over environment-mode occupation patterns (sum probabilities across all environment-mode outcomes for each fixed physical-mode outcome) to get a distribution comparable to Python's `dist`/`residual` split. `sort_by_lost_photons`/`lossless_part`/`keep_lossless_part!` (also in `loss.jl`) look like relevant existing helpers for this but their exact semantics need to be verified against BosonSampling.jl's own docs/tests before relying on them, not assumed from the source snippets alone.
**How to avoid:** Budget explicit investigation time for this during planning/execution — this is the single most nontrivial new API surface in the whole phase, more so than VERIFY-02/03's exact-case work.

### Pitfall 4: Phase 18's CSV numbers are pooled means over 5 random draws, not a single reproducible circuit
**What goes wrong:** `results/phase18_weight1_loss_sweep.csv` / `phase18_mixed_loss_sweep.csv` report `tvd_to_lossless_mean`/`_std` averaged over `n_draws=5` independently-random `thetas` per (n, η, scope) cell (`hardness/sweep.py::_raw_values_for_cell`, seeded via `trainability.rng.get_rng(seed_base, scope, n, draw)` — a `blake2b`-hash-based seed, not something to reimplement in Julia). VERIFY-04 cannot target "the CSV number" directly — there is no single Python circuit instance that produces `0.00995` (n=2, weight1, η=0.99); it's an average over 5 different theta draws.
**Why it happens:** Phase 18's own design deliberately pools over random draws to characterize typical-case behavior, not a specific instance — reasonable for that phase's own purpose, but the wrong shape for a cross-implementation numeric diff.
**How to avoid:** For VERIFY-04, generate a **specific, fixed θ draw** in Python (e.g. call `hardness.sweep._raw_values_for_cell(n=2, eta=<value>, scope=..., draw_start=0, draw_count=1)`, or more directly call `sample_thetas` with a literal fixed seed / hardcode literal theta values), record that single draw's raw `tvd_to_lossless` value (not the mean) plus the literal `thetas` used, and have Julia reproduce that *exact* single-instance number, not the pooled mean. This also sidesteps needing to replicate `trainability.rng.derive_seed`'s hashing scheme in Julia — Julia only needs the concrete theta values, generated once in Python and treated as a fixed input.
**Warning sign:** Trying to match Julia's output to a CSV column labeled `_mean` is itself the warning sign — stop and generate a single-draw reference instead.

### Pitfall 5: `heralded_cz`'s success probability (2/27) and Knill CZ literature figures aren't automatically the same construction
**What goes wrong:** This repo's own `docs/iqp-photonic-encoding.md` explicitly flags that commonly-cited literature figures for "the general Knill CZ gate family" (1/9 post-selected, ~2/27 heralded) were *not* independently re-derived from Perceval's exact circuit before Phase 10 measured 2/27 directly — the match was observed, not proven equivalent-by-construction. If VERIFY-03's independent Julia build of the Knill CZ produces a different success probability (even a plausible-looking one like 1/9), that is not automatically a bug — it may indicate the independently-sourced literature construction differs in some detail (e.g. heralding vs. post-selection variant) from Perceval's specific implementation.
**How to avoid:** Before concluding "Julia disagrees with Python, therefore something is broken," check whether the Julia-side construction is verifiably the *same* variant (heralded, not post-selected; same herald condition: exactly 1 photon in each of 2 ancilla modes) as Perceval's, per this repo's own confirmed facts in `heralded_cz_derisking.py` (herald-success 2/27 uniform across all computational-basis inputs, CZ phase sign negative only on `|1,1>`, confirmed via `Simulator.prob_amplitude`). A different-but-internally-consistent success probability from a different-but-valid construction is a documented, honestly-reported finding, not necessarily a debugging failure — consistent with this phase's own disagreement-handling norm.

### Pitfall 6: BosonSampling.jl's `beam_splitter`/`beam_splitter_modes` sign/transpose convention is unverified against Perceval's
**What goes wrong:** `circuit_elements.jl`'s `beam_splitter(t) = [[t -r]; [r t]]` — a specific, particular sign convention for the reflection coefficient. Perceval's own components (`WP`, `HWP`, etc., per `iqp_photonic_encoding.py`'s header comments) use a different, independently-derived unitary form. There is no a priori reason these two packages' sign/phase conventions for "a beamsplitter" agree.
**How to avoid:** This is a real but *expected* source of possible disagreement, not necessarily a bug when it appears — Phase 14's `hello_bosonsampling.jl` already empirically validated BosonSampling.jl's `beam_splitter` reproduces the correct |amplitude|² for the trivial 50/50 case (which is convention-insensitive, since |amplitude|² is unaffected by an overall sign flip on `r`). For gates with an observable *relative phase* between two amplitudes (e.g. the weight-2 CZ sign, or any Hadamard-conjugation step with more than one interfering path), do not assume sign conventions cancel — verify against a known closed-form (e.g. the weight-1 `cos²θ/sin²θ` marginal, already exact and convention-robust) before trusting a phase-sensitive multi-step circuit.

## Code Examples

### Verified patterns from this repo (already working, Phase 14)

**Yao.jl: circuit construction, register prep, probability extraction**
```julia
# Source: julia/hello_yao.jl (this repo, Phase 14, passing)
using Yao
bell_circuit = chain(2, put(1 => H), control(1, 2 => X))
reg = zero_state(2) |> bell_circuit
p = probs(reg)  # length-2^n vector
```

**BosonSampling.jl: interferometer + event + probability**
```julia
# Source: julia/hello_bosonsampling.jl (this repo, Phase 14, passing)
using BosonSampling
t = 1 / sqrt(2)
U = beam_splitter(t)
interf = UserDefinedInterferometer(U)
input_state = Input{Bosonic}(ModeOccupation([1, 0]))
out = FockDetection(ModeOccupation([1, 0]))
ev = Event(input_state, out, interf)
p = compute_probability!(ev)
```

**BosonSampling.jl: native loss (from `src/types/loss.jl`, NOT yet used anywhere in this repo — verify against installed v1.0.2 before relying on it)**
```julia
# Source: BosonSampling.jl GitHub (main branch; confirm against installed v1.0.2 source
# in the local Julia depot before use, since this was fetched from GitHub, not Context7
# or the exact installed version)
U_physical = beam_splitter(t)                       # or any Interferometer's .U
lossy_interf = UniformLossInterferometer(eta, U_physical)  # doubles m -> 2m internally
# OR, equivalently:
lossy_interf2 = to_lossy(UserDefinedInterferometer(U_physical))  # loss=0 encoded as eta=1 case needs checking

input_lossy = to_lossy(Input{Bosonic}(ModeOccupation([1, 0])))  # pads with m zero-modes
# output_measurement must also target the doubled (2m) mode space --
# marginalizing over environment-mode occupation is a required extra step
# not shown by any example found during this research pass (Pitfall 3).
```

**Python: the exact reference functions VERIFY-02/03/04 must reproduce**
```python
# Source: iqp_photonic_encoding.py (this repo)
exact_qubit_iqp_distribution(n, thetas, pair_thetas=None)     # VERIFY-02's target
photonic_iqp_distribution(n, thetas)                           # VERIFY-03 weight-1 target
photonic_weight2_iqp_distribution(n, i, j, thetas)              # VERIFY-03 weight-2 target
total_variation_distance(dist_a, dist_b)                        # the exact metric to reimplement in Julia

# Source: hardness/loss_model.py, hardness/loss_model_weight2.py (this repo)
photonic_iqp_distribution_lossy(n, thetas, eta=1.0)              # VERIFY-04 weight-1 target
photonic_weight2_iqp_distribution_lossy(n, i, j, thetas, eta=1.0) # VERIFY-04 mixed target
```

**Shared test cases already established/tested on the Python side (reuse these exact inputs in Julia, per CONTEXT.md's "same test inputs" lock):**
```python
# Weight-1, n=2 (tests/test_iqp_photonic_encoding.py::test_full_pipeline_multi_qubit_matches_product_distribution)
n, thetas = 2, [0.3, 1.1]
# Weight-1, n=3
n, thetas = 3, [0.3, 1.1, 0.75]

# Weight-2, n=2, i=0, j=1 (the LOCKED gate, tests/test_iqp_photonic_encoding.py::test_wt2_tvd_gate_n2_theta_pi_4)
n, i, j, thetas, pair_thetas = 2, 0, 1, [0.0, 0.0], {(0, 1): np.pi / 4}
# measured TVD ~2.2e-16 in Python; expected herald_failure_prob = 1 - 2/27
```

## State of the Art
Not applicable in the usual sense (this is a fixed, already-implemented internal pipeline, not a fast-moving external library). One relevant fact: `docs/iqp-photonic-encoding.md` documents that Perceval's `heralded_cz` implements the **Knill CZ gate**, arXiv:quant-ph/0110144 (Knill, 2002) — this is the literature source the planner should point to when researching an independent construction for VERIFY-03's weight-2 case.

## Open Questions

1. **What is the Knill CZ gate's independently-sourced unitary matrix, in a form usable for a `UserDefinedInterferometer`?**
   - What we know: it's a 6-mode (4 data + 2 ancilla) linear-optical circuit; Perceval's implementation has a confirmed 2/27 herald-success rate, negative phase sign only on `|1,1>`, uniform across all computational-basis and 2 superposition test inputs (`heralded_cz_derisking.py`).
   - What's unclear: the exact matrix (or, more practically, the exact sequence of beamsplitters/phase-shifters) from an independent source (the original paper or a textbook derivation), which is what "not a mechanical port" requires.
   - Recommendation: fetch/read arXiv:quant-ph/0110144 directly during planning or early execution (a literature lookup, not something resolvable from this repo's own files); if the exact matrix can't be found/derived cheaply, treat VERIFY-03's weight-2 leg as the piece most likely to hit the phase's disagreement-handling/time-box path, consistent with CONTEXT.md's "independently gradeable, a stall on one doesn't block the others" design.

2. **Does `UniformLossInterferometer`/`to_lossy`'s doubled-mode output require a specific BosonSampling.jl helper (e.g. `sort_by_lost_photons`, `keep_lossless_part!`) to marginalize back to a physical-mode distribution, or does the planner need to write that reduction by hand?**
   - What we know: the doubled-mode representation and several loss-analysis helper functions exist in `src/types/loss.jl`.
   - What's unclear: their exact call signatures/semantics were not confirmed against runnable examples (WebFetch/WebSearch summarized the paper, not a full worked tutorial); the source shown here was fetched from BosonSampling.jl's GitHub `main` branch, not verified against the exact installed v1.0.2 tag, and not cross-checked via Context7 (BosonSampling.jl does not appear to be Context7-indexed based on this research pass).
   - Recommendation: before writing the loss cross-check script, read the actual installed source in the local Julia depot (`julia --project=julia -e 'using BosonSampling; pathof(BosonSampling)'` locates it) to confirm the v1.0.2 API matches what's documented here, and/or run a minimal experiment mirroring `hello_bosonsampling.jl`'s style (assert against a hand-derivable case, e.g. n=1 mode with a known η) before attempting n=2 weight-1/mixed.

3. **Does BosonSampling.jl's herald/post-selection accounting need to be done entirely by hand (summing over the 2 ancilla modes' output occupation), or does the package have any built-in heralding/post-selection primitive (analogous to Perceval's `add_herald`)?**
   - What we know: the package exposes `Event`/`compute_probability!` for single output patterns and doesn't appear (from this research pass) to have a `Processor`-like object with built-in herald registration akin to Perceval's.
   - What's unclear: whether enumerating all valid data-mode output patterns for a fixed ancilla-herald pattern needs to be done via repeated single-`Event` `compute_probability!` calls (feasible at n=2's small state space) or whether a batched/analyzer-style helper exists.
   - Recommendation: plan for per-outcome `compute_probability!` calls in a loop (mirroring Python's own `Analyzer`-based enumeration, conceptually, though via a different mechanism) as the safe default; this is tractable at the CONTEXT.md-locked n=2/n=3 scale.

## Sources

### Primary (HIGH confidence)
- `iqp_photonic_encoding.py`, `hardness/loss_model.py`, `hardness/loss_model_weight2.py`, `hardness/sweep.py`, `trainability/rng.py` (this repo) — exact Python reference functions, signatures, and TVD/loss-grid conventions.
- `tests/test_iqp_photonic_encoding.py` (this repo) — concrete shared test-case inputs (thetas, n, i, j) already validated on the Python side.
- `julia/hello_yao.jl`, `julia/hello_bosonsampling.jl`, `julia/Project.toml`, `julia/Manifest.toml`, `julia/README.md` (this repo, Phase 14) — confirmed-working Julia API usage patterns and exact installed versions (Julia 1.10.11, Yao.jl 0.9.1, BosonSampling.jl 1.0.2).
- `results/phase18_weight1_loss_sweep.csv`, `results/phase18_mixed_loss_sweep.csv` (this repo) — the exact η grid (`[0.99, 0.95, 0.90, 0.80, 0.60, 0.35, 0.05]`, confirmed also in `hardness/sweep.py::ETA_GRID`) and column semantics (pooled means over 5 draws, not single-instance values — see Pitfall 4).
- `docs/iqp-photonic-encoding.md`, `heralded_cz_derisking.py` (this repo) — Knill CZ construction identity, confirmed 2/27 herald-success rate and phase-sign facts for `heralded_cz`.

### Secondary (MEDIUM confidence)
- BosonSampling.jl source files fetched directly from GitHub `main` branch (`src/types/loss.jl`, `src/types/interferometers.jl`, `src/types/input.jl`, `src/circuits/circuit_elements.jl`) — real source code, but not confirmed against the exact installed v1.0.2 tag, and not cross-checked via Context7 (package doesn't appear Context7-indexed).
- arXiv:2212.09537 ("BosonSampling.jl: A Julia package for quantum multi-photon interferometry") via WebFetch — confirms `Event`/`compute_probability!`/`Input{T}`/`ModeOccupation` API shape and the existence of a `noisy_distribution(input=, loss=, interf=)` helper function (not independently verified from source in this pass).

### Tertiary (LOW confidence)
- WebSearch summaries of Yao.jl's `probs`, `measure!`, `most_probable`, `Rz`, block/kron/chain composition — general API shape confirmed by multiple hits and consistent with this repo's own working `hello_yao.jl`, but exact signatures for a custom diagonal ZZ-interaction gate were not independently verified against Yao.jl source or Context7 in this pass.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — locked by Phase 14/CONTEXT.md, verified directly from `julia/Manifest.toml`.
- Python-side reference functions: HIGH — read directly from this repo's source and test suite.
- Yao.jl API for VERIFY-02: MEDIUM — general shape confirmed, exact custom-diagonal-gate construction needs verification during planning/execution.
- BosonSampling.jl API for VERIFY-03/04: MEDIUM — native loss API confirmed to exist (a real, load-bearing finding), but exact usage semantics (doubled-mode marginalization, heralding-by-hand) are open questions flagged above, sourced from GitHub `main` rather than the exact installed version or Context7.
- Pitfalls: HIGH for Python-side pitfalls (bit-ordering, phase-convention, pooled-mean CSV trap — all directly verified from this repo's code/docs); MEDIUM for BosonSampling.jl-side pitfalls (loss-mode marginalization, beamsplitter sign convention — inferred from source, not empirically run).

**Research date:** 2026-08-17
**Valid until:** ~30 days (stable, already-pinned toolchain; the only fast-moving risk is if BosonSampling.jl's GitHub `main` has diverged meaningfully from the installed v1.0.2 — verify against the local depot early in planning/execution).
