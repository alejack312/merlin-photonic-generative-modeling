# Architecture Research

**Domain:** v3.0 milestone — integrating a trainability study (STUDY-01), a loss-hardness study (STUDY-02), an arbitrary-θ two-qubit gate (ARB-01), and an independent Julia verifier into the existing, fully-validated weight-1/weight-2 IQP-photonic codebase
**Researched:** 2026-08-07
**Confidence:** HIGH — every claim below that concerns Perceval/MerLin behavior was verified by direct execution against this repo's own `./venv` (perceval-quandela==1.2.4, merlinquantum==0.4.0), not inferred from documentation or training-data memory. The one claim that could not be verified locally (Julia package behavior) is explicitly marked MEDIUM and sourced from the sibling Stack research thread's `.planning/research/STACK.md`.

**Note on this file:** supersedes the previous (2026-08-05) version of this file, which was scoped narrowly to v2.1's weight-2 `heralded_cz` integration question. That content is preserved in git history; this version covers the four new v3.0 capabilities and is grounded in the actual v2.1-complete codebase (118/118 tests passing, weight-1 and weight-2 both validated).

## Critical Finding First (this changes STUDY-01/02's architecture)

**The existing weight-1/weight-2 IQP-photonic circuits cannot be wrapped in a MerLin `QuantumLayer` at all — not a workaround-able input-format issue, a hard backend incompatibility.**

Verified directly:
```
>>> c = build_full_circuit(n, thetas)
>>> c.requires_polarization
True
>>> ML.QuantumLayer(circuit=c, input_state=all_h_input(n), trainable_parameters=['theta'])
ValueError: BasicState with annotations is not supported
```
`iqp_photonic_encoding.py`'s entire encoding (`WP`, `HWP`, `PBS`, `{P:H}`/`{P:V}`-annotated `BasicState`) is built on Perceval's **polarization** formalism. MerLin's `QuantumLayer` — and by extension Phase 7's `torch.func.jacrev`/`functional_call` pattern in `generator/neighbor_locality.py`, which only works because it differentiates *through* a `QuantumLayer` — is built on plain Fock-space (no polarization degree of freedom) circuits via Perceval's `SLOSBackend`. This is the exact same restriction `_build_cz_insertion_core`'s own docstring already documents for the `Simulator`/`SLOSBackend` path (`assert not circuit.requires_polarization`) — it turns out to apply to `QuantumLayer`'s autodiff pipeline too, for the same underlying reason.

**Consequence:** STUDY-01 (gradients) and, separately, MerLin's `PhotonLossTransform` for STUDY-02 (loss) are both reachable only through a `QuantumLayer`, and a `QuantumLayer` cannot host this project's actual circuit. Both studies must be built on a **different mechanism** than "wrap the circuit in `QuantumLayer` and reuse Phase 7's code verbatim." Details and recommended alternatives are in the STUDY-01/STUDY-02 sections below. The `generator/` MerLin `QuantumLayer` pipeline (a separate, `QuantumLayer.simple()`-generated ansatz, per this milestone's context) is **not the substrate for either study** — it never was the IQP-photonic circuit, and this finding confirms it structurally can't become one.

A second, independently-verified finding, relevant to STUDY-02: **`pcvl.algorithm.Analyzer` — the class every existing distribution function in `iqp_photonic_encoding.py` uses (`run_full_circuit`, `photonic_iqp_distribution`, `photonic_weight2_iqp_distribution`) — silently ignores `Processor`-level `NoiseModel`/loss.** Verified on both the polarization circuit and a trivial 2-mode control circuit: probabilities sum to exactly 1.0 with `transmittance=0.5` set, no loss outcomes appear. `Processor.probs()` (with `min_detected_photons_filter(0)` explicitly set to allow sub-normalized/vacuum outcomes) **does** apply the loss — verified: `transmittance=0.5` on a single photon into a beamsplitter correctly produces `|0,0⟩: 0.5` (photon lost) plus the two split outcomes at 0.25 each. STUDY-02 must call `.probs()`, not `Analyzer`, or loss will be silently absent from the results.

## System Overview

```
┌───────────────────────────────────────────────────────────────────────────┐
│  EXISTING (v2.1, validated, untouched)                                    │
│  iqp_photonic_encoding.py                                                 │
│  ┌──────────────┐ ┌───────────────┐ ┌──────────────┐ ┌─────────────────┐  │
│  │ weight-1     │ │ weight-1      │ │ weight-2 CZ  │ │ weight-2        │  │
│  │ builders     │ │ distribution  │ │ insertion    │ │ processor +     │  │
│  │ (Circuit)    │ │ fns (Analyzer)│ │ (Processor)  │ │ distribution    │  │
│  └──────┬───────┘ └───────┬───────┘ └──────┬───────┘ └────────┬────────┘  │
│         │                 │                │                  │           │
│         └─────────────────┴────────┬───────┴──────────────────┘           │
│                          exact_qubit_iqp_distribution (trusted numpy ref) │
└──────────────────────────────────┬────────────────────────────────────────┘
                                    │  reused UNMODIFIED as forward-pass primitives
        ┌───────────────────┬──────┴───────┬──────────────────────┐
        ▼                   ▼               ▼                      ▼
┌───────────────┐  ┌────────────────┐ ┌─────────────────┐  ┌────────────────┐
│ STUDY-01       │  │ STUDY-02       │ │ ARB-01           │  │ generator/     │
│ trainability   │  │ loss-hardness  │ │ arbitrary-θ gate │  │ (MerLin        │
│                │  │                │ │                  │  │ QuantumLayer,  │
│ NEW:           │  │ NEW:           │ │ NEW:             │  │ separate       │
│ generator/     │  │ iqp_photonic_  │ │ iqp_photonic_    │  │ ansatz —       │
│ trainability.py│  │ encoding.py:   │ │ encoding.py:     │  │ NOT touched by │
│ (parameter-    │  │ *_lossy() fns  │ │ build_arb_gate_  │  │ this milestone)│
│ shift grads,   │  │ via .probs()   │ │ insertion(),     │  │                │
│ no QuantumLayer│  │ + NoiseModel   │ │ build_weight2_   │  │                │
│ trainability_  │  │ loss_hardness_ │ │ arb_processor()  │  │                │
│ study.py       │  │ study.py       │ │ arb01_derisking. │  │                │
│ (driver)       │  │ (driver)       │ │ py (de-risk)     │  │                │
└───────┬────────┘  └────────┬───────┘ └────────┬─────────┘  └────────────────┘
        │                    │                   │
        └────────────────────┴─────────┬─────────┘
                                        ▼
                        results/ (CSV + PNG + *.md, existing convention)
                                        │
                                        ▼
                         ┌──────────────────────────────┐
                         │ julia_verification/ (NEW)     │
                         │ side-channel, subprocess+JSON, │
                         │ never imported by Python at    │
                         │ runtime, never a dependency of  │
                         │ any pytest test unless Julia    │
                         │ is present                      │
                         └──────────────────────────────┘
                                        │
                                        ▼
                            WRITE-01 (docs/, findings write-up)
```

### Component Responsibilities

| Component | Responsibility | Status |
|-----------|----------------|--------|
| `iqp_photonic_encoding.py` | Weight-1/weight-2 circuit builders, distribution functions, exact qubit-side reference | Existing — extended with new distribution/builder functions for STUDY-02 and ARB-01, existing functions untouched |
| `generator/` (`naturally_ordered_generator.py`, `neighbor_locality.py`, etc.) | MerLin `QuantumLayer`-based generative pipeline, separate ansatz | Existing — **not touched**. Confirmed architecturally separate: it never wrapped the IQP-photonic circuit, and per the finding above, it structurally cannot. |
| `generator/trainability.py` (NEW) | Parameter-shift gradient computation directly on `iqp_photonic_encoding.py`'s Analyzer-based distribution functions; gradient-variance-vs-`n` aggregation | New — analogous role to `generator/neighbor_locality.py`, different mechanism (no `QuantumLayer`, no `jacrev`) |
| `trainability_study.py` (NEW, top-level) | STUDY-01 driver script: sweeps `n`, random `θ` draws, calls `generator/trainability.py`, writes `results/` artifacts | New — mirrors `neighbor_locality_test.py`'s role (driver/report script, not a pytest file) |
| `iqp_photonic_encoding.py`: new `*_lossy` functions (NEW) | Loss-aware variants of `photonic_iqp_distribution`/`photonic_weight2_iqp_distribution`, built on `Processor.probs()` + `NoiseModel`, not `Analyzer` | New — additive, same module (matches how weight-2 was added alongside weight-1 in the same file rather than a new module) |
| `loss_hardness_study.py` (NEW, top-level) | STUDY-02 driver script: sweeps transmittance, measures TVD/sampling-hardness proxy vs. loss level | New — mirrors `sigma_resweep.py`/`batch_sweep.py`'s role |
| `iqp_photonic_encoding.py`: `build_arb_gate_insertion`, `build_weight2_arb_processor` (NEW) | `PostProcessedControlledRotationsItem`-based arbitrary-α weight-2 gate, composed the same way `build_cz_insertion`/`build_weight2_processor` are, plus the added `set_postselection` plumbing | New — additive, same module, mirrors the exact precedent set by weight-2's own addition alongside weight-1 |
| `arb01_derisking.py` (NEW, top-level) | Standalone amplitude/phase/success-probability verification of `PostProcessedControlledRotationsItem` before wiring it into the full pipeline | New — mirrors `heralded_cz_derisking.py`'s exact precedent (de-risk the primitive in isolation first) |
| `julia_verification/` (NEW, top-level directory) | Independent Julia-side recomputation of exact distributions (Yao.jl, qubit-side) and lossy photonic distributions (BosonSampling.jl), invoked as a subprocess, compared via JSON — never a runtime dependency of the Python pipeline | New — genuinely new toolchain, isolated per the pattern in "Julia Interop" below |
| `docs/` (WRITE-01) | Findings write-up | Existing directory, new document(s) |

## Recommended Project Structure

```
merlin-quantum-case-study/
├── iqp_photonic_encoding.py       # EXTENDED: existing weight-1/weight-2 fns untouched;
│                                   #   + photonic_iqp_distribution_lossy(n, thetas, noise)
│                                   #   + photonic_weight2_iqp_distribution_lossy(n, i, j, thetas, noise)
│                                   #   + build_arb_gate_insertion(n, i, j, alpha)
│                                   #   + build_weight2_arb_processor(n, i, j, alpha, thetas)
├── generator/
│   ├── trainability.py            # NEW: parameter-shift gradient + variance-vs-n utilities
│   │                               #   (no QuantumLayer dependency — operates on
│   │                               #   iqp_photonic_encoding.py's Analyzer-based fns directly)
│   └── ...                        # (unchanged: neighbor_locality.py, mmd.py, etc.)
├── trainability_study.py          # NEW top-level driver (STUDY-01), mirrors neighbor_locality_test.py
├── loss_hardness_study.py         # NEW top-level driver (STUDY-02), mirrors sigma_resweep.py
├── arb01_derisking.py             # NEW top-level de-risking script (ARB-01), mirrors heralded_cz_derisking.py
├── julia_verification/            # NEW top-level directory — isolated Julia toolchain
│   ├── Project.toml               # Julia's own lockfile (pins Yao.jl, BosonSampling.jl versions)
│   ├── Manifest.toml
│   ├── verify_weight1_qubit_side.jl    # Yao.jl: rebuild the H-diag-H IQP circuit, exact distribution
│   ├── verify_weight2_loss.jl          # BosonSampling.jl: permanent-based lossy linear-optical distribution
│   ├── run_verification.py             # thin Python wrapper: writes JSON input, subprocess.run(["julia", ...]),
│   │                                   #   reads JSON output, compares via existing total_variation_distance()
│   └── fixtures/                       # checked-in JSON snapshots of Python-side reference distributions,
│                                       #   so Julia-side scripts can run standalone without a live Python call
├── tests/
│   ├── test_iqp_photonic_encoding.py   # EXTENDED: new tests for *_lossy fns and ARB-01 builders,
│   │                                   #   appended in the same file — matches existing weight-1/weight-2 precedent
│   ├── test_trainability.py            # NEW: unit tests for generator/trainability.py's parameter-shift math
│   └── test_julia_verification.py      # NEW: `pytest.mark.skipif(shutil.which("julia") is None, ...)` —
│                                       #   never fails CI/local runs when Julia isn't installed
├── results/                         # unchanged convention: *.csv, *.png, *_summary.md per study
└── docs/
    └── iqp-trainability-loss-study.md  # WRITE-01 (name illustrative — final naming is a roadmap/planning call)
```

### Structure Rationale

- **New distribution/builder functions live inside `iqp_photonic_encoding.py`, not new modules.** This matches the file's own established precedent — weight-2 (`build_cz_insertion`, `build_weight2_processor`) was added directly alongside weight-1 in the same file rather than split into a second module, specifically so every builder shares one set of conventions (mode-mapping dicts, herald-spec extraction, bit-ordering) and one 118-test suite that already proves them composable. STUDY-02's loss variants and ARB-01's gate variants are the same kind of extension.
- **STUDY-01's gradient logic lives in `generator/`, not `iqp_photonic_encoding.py`.** It's a numerical/statistical utility (parameter-shift evaluation, variance aggregation) operating *on* the encoding module's outputs, not a circuit builder — matching where `generator/neighbor_locality.py`'s Jacobian/statistics code already lives, even though the underlying differentiation mechanism can't be the same (see Critical Finding).
- **Top-level driver scripts (`*_study.py`, `arb01_derisking.py`) mirror the existing convention exactly** (`batch_sweep.py`, `sigma_resweep.py`, `neighbor_locality_test.py`, `heralded_cz_derisking.py`): a sweep/report script at the repo root that imports from `iqp_photonic_encoding.py`/`generator/`, writes to `results/`, and is not itself part of the pytest suite (the pytest suite tests the underlying functions in `tests/`, not the driver scripts).
- **`julia_verification/` is a dedicated, isolated top-level directory**, not scattered files or a package importable from Python — see "Julia Interop" pattern below for the full rationale.

## Architectural Patterns

### Pattern 1: Parameter-shift gradients directly on the Analyzer-based pipeline (STUDY-01)

**What:** Because the circuit can't enter `QuantumLayer`, compute `∂L/∂θₖ` using the exact parameter-shift rule instead of autograd. Every weight-1 diagonal-layer gate is `WP(θₖ, 0) = diag(e^{iθₖ}, e^{-iθₖ})` — an `exp(iθZ)`-type rotation generator, for which parameter-shift is *exact*, not an approximation: `∂f/∂θₖ = [f(θₖ+π/2) − f(θₖ−π/2)] / 2` for any observable/probability built from this gate family. This is arguably a **stronger** guarantee than autograd-through-SLOS would have given, since it's a closed-form identity rather than a numerically-differentiated computational graph.

**When to use:** STUDY-01's entire gradient-variance-vs-`n` sweep. Also the natural choice for STUDY-02's "does the gradient landscape survive loss" question if that's added to the study, since it reuses the same forward-pass call, just against the lossy distribution function instead of the exact one.

**Trade-offs:** Two forward-pass evaluations per parameter per draw (like any parameter-shift/finite-difference method) — more `Analyzer`/`.probs()` calls than a single autograd backward pass would need, but at this project's system sizes (`n` small enough for exact photonic simulation) this is not a performance concern, and it entirely sidesteps the polarization/`QuantumLayer` incompatibility. The `exact_qubit_iqp_distribution` numpy reference (already trusted to ~1e-16 TVD against the photonic pipeline) can also be parameter-shifted or differentiated in closed form directly (Van den Nest's cosine formula in `docs/iqp-baseline.md` is already an analytic expectation-value formula in `θ`) — a natural cross-check that costs nothing extra.

**Example (illustrative shape, not final code):**
```python
def parameter_shift_gradient(dist_fn, n, thetas, k, target_bitstring, shift=np.pi/2):
    thetas_plus = list(thetas); thetas_plus[k] += shift
    thetas_minus = list(thetas); thetas_minus[k] -= shift
    dist_plus, _ = dist_fn(n, thetas_plus)
    dist_minus, _ = dist_fn(n, thetas_minus)
    return (dist_plus.get(target_bitstring, 0.0) - dist_minus.get(target_bitstring, 0.0)) / 2
```
`dist_fn` is `photonic_iqp_distribution` (weight-1) or a fixed-`(i,j)` closure over `photonic_weight2_iqp_distribution` (weight-2) — **unmodified**, called as a black box.

### Pattern 2: `Processor.probs()` + `NoiseModel`, never `Analyzer`, for loss (STUDY-02)

**What:** Loss integrates via `pcvl.Processor("SLOS", circuit, noise=pcvl.NoiseModel(transmittance=...))`, exactly as `iqp_photonic_encoding.py`'s existing builders already construct their `Processor`/`Circuit` objects — no change to `build_full_circuit`, `build_weight2_processor`, or any weight-1/weight-2 builder. The only required change is **which Perceval API reads the result**: new `*_lossy` distribution functions must call `proc.min_detected_photons_filter(0); proc.with_input(input_state); proc.probs()` instead of `pcvl.algorithm.Analyzer(proc, [input_state], "*")`. `min_detected_photons_filter(0)` is required so loss-truncated (fewer-photon) outcomes are returned rather than filtered out by Perceval's default photon-count floor.

**When to use:** Any STUDY-02 measurement (TVD-vs-transmittance sweeps, hardness-under-loss proxies).

**Trade-offs:** `.probs()`'s output shape/dict keys differ slightly from `Analyzer`'s (`output_states_list`/`distribution` pair) — the new `*_lossy` functions need their own small adapter to convert `.probs()`'s result into the same `{bitstring: probability}` + `residual` shape the existing (lossless) functions already return, so downstream code (TVD comparisons, plotting) doesn't need to know which path produced a distribution. Raw Perceval's `LossSimulator`/`LC` component (the "second, independently-implemented" loss model per `STACK.md`) is available as an **in-Python cross-check that both loss models agree**, cheaper to run than reaching for the Julia verifier for this specific question.

### Pattern 3: `PostProcessedControlledRotationsItem` composes like `build_cz_insertion`, but needs new postselection plumbing (ARB-01)

**What:** Verified directly against the installed catalog item's `build_experiment()`:
```python
e.set_postselection(PostSelect("[0,1]==1 & [2,3]==1"))   # data/ctrl dual-rail validity (LOCAL indices, n=2)
for i in range(4, 8):  # 2n..4n-1
    e.add_herald(i, 0)                                    # ALL 2n ancilla modes heralded to vacuum
```
Two composition-relevant differences from `build_cz_insertion`'s `heralded_cz`-based pattern:
1. **Twice the ancilla modes.** `heralded_cz` uses 2 herald ancilla modes (6-mode local circuit total); `PostProcessedControlledRotationsItem` uses `2n` ancilla modes for an `n`-qubit gate — **4 ancilla modes** for the `n=2` case this project uses (8-mode local circuit total: 4 data + 4 ancilla). `build_weight2_arb_processor`'s outer mode-count constant must become `2*n_qubits + 4` (mirroring how `build_weight2_processor` uses `2*n_qubits + 2` for `heralded_cz`'s 2 ancilla modes), and the mode-mapping dict passed to `Processor.add()` needs 4 ancilla-mode entries instead of 2.
2. **A `set_postselection` call is required in addition to heralds — new plumbing `build_cz_insertion`/`build_weight2_processor` never needed.** `heralded_cz`'s data-rail validity is currently handled *after* simulation, in plain Python (`fock_to_bitstring` returning `None` for out-of-subspace states, bucketed into `residual`). `PostProcessedControlledRotationsItem` instead expects validity enforced *at the Perceval level* via `Experiment.set_postselection`/`Processor.set_postselection`, using **global** mode indices once composed into the full `2n_qubits+4`-mode outer processor — exactly the same local→global translation problem `build_cz_insertion` already solved for `herald_spec` (Plan 11-02's mode-mapping dict), but for a `PostSelect` condition string instead of a herald dict. This is genuinely new code (a small helper to rewrite `PostSelect`'s local mode indices into the outer processor's global ones), not a reuse of existing plumbing — flag this explicitly as new work, not "the same pattern, just call it."

**When to use:** ARB-01's entire gate — ancilla-wrap/unwrap via `PBS` (same convention-adapter `PERM` pattern `build_cz_insertion` already established, since `PostProcessedControlledRotationsItem`'s ports are also `Encoding.DUAL_RAIL`) still applies unchanged; only the herald/postselection registration step differs.

**Trade-offs:** Success probability is `α`-dependent and non-monotonic (0.42 near `α→0` down to ~0.09 near `α=π/2`, per `STACK.md`'s empirical table) — any sweep over `α` must budget for this, unlike the fixed 2/27 rate `heralded_cz` always has.

### Pattern 4: Julia as an out-of-process, JSON-mediated side channel, never an in-process interop bridge

**What:** `julia_verification/run_verification.py` is the *only* Python file that knows Julia exists. It shells out via `subprocess.run(["julia", "verify_weight1_qubit_side.jl", "--input", "fixtures/case1.json", "--out", "/tmp/out.json"])`, then loads the JSON and diffs it against Python's own `exact_qubit_iqp_distribution`/`photonic_iqp_distribution` output using the **already-existing** `total_variation_distance()` function — the same cross-check shape this project has used since Phase 12 (exact-qubit-vs-photonic TVD validation), just with a third, independently-implemented source added to the comparison.

**When to use:** Standalone verification runs, not wired into any code path the rest of the project depends on at runtime.

**Trade-offs (why not PyJulia/juliacall):**
- **Availability blast radius.** Julia is confirmed **not installed** in this environment (per `STACK.md`, `julia --version` → not found). An in-process bridge (PyJulia/`juliacall`) would make importing `run_verification.py` — and transitively, any test module that imports it — fail on any machine without a correctly version-matched Julia install. A subprocess CLI call fails only when that one script is actually invoked, and can be `pytest.mark.skipif`-guarded cleanly (`shutil.which("julia") is None`).
- **Version-pinning independence.** Julia's `Project.toml`/`Manifest.toml` lock Yao.jl/BosonSampling.jl versions entirely on the Julia side; nothing about the Python `venv`, `requirements.txt`, or CI needs to know Julia exists at all.
- **Matches the milestone's own stated intent.** `PROJECT.md` explicitly frames this as "not a central architectural component — a verification tool alongside the existing pipeline." A subprocess+JSON side channel is the only shape that can't accidentally become load-bearing; an in-process bridge, once adopted, has a strong pull toward becoming one (any convenience win from calling Julia functions inline from Python creates exactly the coupling this milestone's own scoping note says to avoid).
- **Windows-specific risk reduction.** PyJulia's Python↔Julia shared-library bridge has known extra friction on Windows (locating `libjulia`, matching Python's own ABI); a plain subprocess call sidesteps all of it — `julia script.jl` behaves identically to any other CLI tool from PowerShell/Bash.

## Data Flow

### STUDY-01 (trainability)

```
random θ draws (numpy, seeded) × system sizes n=2..N
        ↓
photonic_iqp_distribution(n, θ) / photonic_weight2_iqp_distribution(n, i, j, θ)   [UNCHANGED]
        ↓ (called twice per θₖ, at θₖ±π/2 — Pattern 1)
generator/trainability.py: parameter_shift_gradient(...)  → ∂L/∂θₖ per draw
        ↓
aggregate Var[∂L/∂θₖ] across draws, per n  → fit exponential decay vs n
        ↓ (same statistical spine as generator/train.py's decreasing_trend_check
        ↓  and generator/neighbor_locality.py's neighbor_locality_check —
        ↓  direction + effect-size threshold, not a bare p-value)
results/phaseNN_trainability_metrics.csv, .png, _summary.md
        ↓
docs/ WRITE-01, cross-checked (optionally) by julia_verification/verify_weight1_qubit_side.jl
```

### STUDY-02 (loss-hardness)

```
weight-1/weight-2 Circuit/Processor  [UNCHANGED builders]
        ↓ wrapped with pcvl.Processor(..., noise=pcvl.NoiseModel(transmittance=t))
        ↓ (Pattern 2: .probs() with min_detected_photons_filter(0), NOT Analyzer)
new photonic_iqp_distribution_lossy() / photonic_weight2_iqp_distribution_lossy()
        ↓
TVD(lossless dist, lossy dist) vs t sweep   [reuses existing total_variation_distance()]
        ↓
results/phaseNN_loss_hardness_metrics.csv, .png, _summary.md
        ↓
docs/ WRITE-01, cross-checked (optionally) by julia_verification/verify_weight2_loss.jl (BosonSampling.jl)
```

### ARB-01 (arbitrary-θ gate)

```
arb01_derisking.py (standalone, mirrors heralded_cz_derisking.py):
  PostProcessedControlledRotationsItem amplitude/phase/success-probability checks
        ↓ (if it de-risks cleanly)
iqp_photonic_encoding.py: build_arb_gate_insertion(n, i, j, alpha)   [mirrors build_cz_insertion]
        ↓
build_weight2_arb_processor(n, i, j, alpha, thetas)   [mirrors build_weight2_processor,
        ↓                                              +4 ancilla modes, + set_postselection]
TVD validation against exact_qubit_iqp_distribution(..., pair_thetas={(i,j): alpha/2})
        ↓ (same CZ/ZZ operator-identity pattern already used for the fixed-π/4 case,
        ↓  generalized to arbitrary alpha — CP(α) = exp(iα/4·(I−Zᵢ−Zⱼ+ZᵢZⱼ)))
tests/test_iqp_photonic_encoding.py (appended)
```

## Anti-Patterns

### Anti-Pattern 1: Wrapping the polarization circuit in `QuantumLayer` "because Phase 7 already has the pattern"

**What people would do:** Try to reuse `generator/neighbor_locality.py`'s `compute_jacobian` verbatim by passing `build_full_circuit`/`build_weight2_processor`'s output into `QuantumLayer(circuit=...)`.
**Why it's wrong:** Confirmed by direct execution — this raises `ValueError: BasicState with annotations is not supported`, because the circuit's `requires_polarization` is `True`. This isn't a bug to work around with a kwarg; it's a genuine backend mismatch between Perceval's polarization formalism and MerLin's Fock-space-only autodiff pipeline.
**Do this instead:** Parameter-shift gradients directly on the existing `Analyzer`-based distribution functions (Pattern 1). If literal `QuantumLayer`/`jacrev` reuse is later judged worth the cost, it would require designing and re-validating a **second, non-polarization (plain dual-rail) IQP-photonic encoding** from scratch — a substantial new-encoding effort, not a wrapper, and should be treated as clearly out of scope for this milestone's timeline unless explicitly chosen.

### Anti-Pattern 2: Configuring `NoiseModel` on a `Processor` and reading results via `Analyzer`

**What people would do:** Add `noise=pcvl.NoiseModel(transmittance=t)` to `Processor("SLOS", circuit, noise=...)` and assume the existing `Analyzer`-based distribution functions now report lossy results.
**Why it's wrong:** Confirmed by direct execution on both the project's own circuit and a trivial control circuit — `Analyzer` output sums to exactly 1.0 regardless of `transmittance`; the noise model is silently not applied.
**Do this instead:** Use `Processor.probs()` with `min_detected_photons_filter(0)` explicitly set (Pattern 2). Write new `*_lossy` functions rather than adding a `noise=` parameter to the existing `photonic_iqp_distribution`/`photonic_weight2_iqp_distribution` — those functions' current `Analyzer`-based contract (exact, lossless, already TVD-validated) should stay untouched.

### Anti-Pattern 3: Treating `PostProcessedControlledRotationsItem` as a drop-in replacement for `heralded_cz`

**What people would do:** Assume `build_arb_gate_insertion` can reuse `build_cz_insertion`'s exact mode-mapping dict and herald-registration code with only the catalog item swapped.
**Why it's wrong:** The ancilla mode count doubles (2 → 4 for `n=2`) and the composition requires an additional `set_postselection` call with mode indices translated from local to global — a mechanism `build_cz_insertion` never needed. Copying `build_cz_insertion`'s structure without accounting for both differences will silently under- or over-constrain the circuit.
**Do this instead:** Treat it as a new builder following the same *shape* of precedent (local circuit + explicit spec returned to the caller, global-index translation at the outer-processor call site) rather than a literal code reuse — see Pattern 3.

### Anti-Pattern 4: PyJulia/`juliacall` in-process interop for "convenience"

**What people would do:** Use `juliacall` to call Julia functions directly from a Python script for a tighter feedback loop.
**Why it's wrong:** Makes every Python module that imports the interop layer implicitly depend on a correctly-versioned Julia install being present — a severe availability regression for a project whose test suite currently has zero non-Python dependencies and 118/118 passing tests, especially risky this close to the Sept 1 deadline on a toolchain confirmed not-yet-installed.
**Do this instead:** Subprocess + JSON (Pattern 4). The convenience cost (one extra serialization boundary) is worth the isolation guarantee.

## Integration Points

### Existing files/functions — extended (new functions added, existing ones untouched)

| File | New additions | Existing code touched? |
|------|---------------|------------------------|
| `iqp_photonic_encoding.py` | `photonic_iqp_distribution_lossy`, `photonic_weight2_iqp_distribution_lossy` (STUDY-02); `build_arb_gate_insertion`, `build_weight2_arb_processor` (ARB-01) | No — all 118 existing tests should pass unmodified; additive only |
| `tests/test_iqp_photonic_encoding.py` | New test functions for the above | No — appended, matching existing precedent |

### Existing files/functions — left alone

| File | Why untouched |
|------|----------------|
| `generator/naturally_ordered_generator.py`, `generator/data.py`, `generator/mmd.py`, `generator/train.py` | The `generator/` MerLin `QuantumLayer` pipeline is a separate ansatz from the IQP-photonic encoding; confirmed structurally incapable of hosting the polarization circuit, so there is no integration point here to modify — STUDY-01/02 do not run through this pipeline at all |
| `generator/neighbor_locality.py` | Phase 7's `jacrev`/`functional_call` pattern is `QuantumLayer`-specific; not reusable as code for STUDY-01 (see Critical Finding), only reusable as a *conceptual* precedent (statistical rigor pattern — see `generator/train.py`'s `decreasing_trend_check` two-condition shape, reused by `neighbor_locality_check`, and now by STUDY-01's gradient-variance check) |
| `docs/iqp-photonic-encoding.md` | Canonical design doc for weight-1/weight-2 — extend only if ARB-01 changes the encoding's on-paper design (likely: a new section documenting `CP(α)`'s operator identity, alongside the existing `π/4` `heralded_cz` one), not a rewrite |

### New components needed

| Component | Depends on |
|-----------|------------|
| `generator/trainability.py` | `iqp_photonic_encoding.py`'s existing distribution functions (unmodified) |
| `trainability_study.py` | `generator/trainability.py` |
| `iqp_photonic_encoding.py`'s new `*_lossy` functions | `perceval.utils.noise_model.NoiseModel`, existing `Processor`/`Circuit` builders (unmodified) |
| `loss_hardness_study.py` | The new `*_lossy` functions |
| `iqp_photonic_encoding.py`'s `build_arb_gate_insertion`/`build_weight2_arb_processor` | `perceval.components.core_catalog.controlled_rotation_gates.PostProcessedControlledRotationsItem`, the existing PBS-wrap/`PERM`-adapter pattern from `build_cz_insertion` |
| `arb01_derisking.py` | `PostProcessedControlledRotationsItem` directly (no dependency on the new builders — de-risks the primitive first, same order `heralded_cz_derisking.py` established) |
| `julia_verification/` | Julia 1.10 LTS + Yao.jl + BosonSampling.jl (new toolchain, `juliaup`-installed); Python side depends only on `subprocess`/`json`, stdlib |

## Suggested Build Order

1. **ARB-01 de-risking (`arb01_derisking.py`) first, standalone.** Genuinely open research (per `PROJECT.md`'s own framing) with no known blocker but also no prior validation in this project — same "de-risk the primitive before wiring it in" order weight-2 already used successfully (`heralded_cz_derisking.py` → `build_cz_insertion`). Front-loading it leaves the most runway if it needs a pivot, and it has zero dependency on STUDY-01/02.
2. **STUDY-02 (loss) and STUDY-01 (trainability) in parallel — both depend only on the existing, already-validated weight-1/weight-2 builders**, not on each other or on ARB-01. STUDY-02 is the lower-risk of the two (Pattern 2 is now fully verified end-to-end; "just" a sweep + plotting task). STUDY-01 carries more open methodological risk (choosing the observable/loss `L` for the barren-plateau protocol, deciding weight-1-only vs. weight-1+weight-2 scope) and benefits from starting in parallel rather than after STUDY-02.
3. **ARB-01 full integration (`build_arb_gate_insertion`/`build_weight2_arb_processor` + TVD validation)** once de-risked — can run concurrently with STUDY-01/02 since it touches only new functions in `iqp_photonic_encoding.py`.
4. **Julia toolchain spike, early and small, decoupled from when the real cross-check scripts get written.** Given the "new toolchain this close to a deadline" risk `PROJECT.md` itself already flags, do a minimal `juliaup add lts; Pkg.add(["Yao","BosonSampling"])` + one hello-world circuit in each package as its own tiny early step — not gated behind STUDY-01/02 numeric results existing yet — specifically to surface install/version friction (the CLAUDE.md-documented Jul-25 stall pattern) before it can block anything load-bearing. The full `julia_verification/` cross-check scripts (which need real Python-side numbers to diff against) come after STUDY-01/02/ARB-01 produce results.
5. **WRITE-01 last**, synthesizing STUDY-01/02's measured results (reported honestly either direction, per `PROJECT.md`), ARB-01's outcome (resolved or plainly documented as unresolved), and the Julia cross-check's outcome (or an honest note if descoped/incomplete) — matching this project's established norm (`docs/iqp-photonic-encoding.md`, `iqp-baseline.md`) of citing what was actually verified, not what was hoped for.

## Sources

- Direct execution against this repo's `./venv` (perceval-quandela==1.2.4, merlinquantum==0.4.0) — HIGH confidence:
  - `c.requires_polarization` on `build_full_circuit`'s output → `True`.
  - `ML.QuantumLayer(circuit=..., input_state=all_h_input(n), ...)` on the polarization circuit → `ValueError: BasicState with annotations is not supported`, traced to `venv/Lib/site-packages/merlin/algorithms/layer_utils.py:549`.
  - `pcvl.Parameter` objects pass through `build_full_circuit`/`build_diagonal_layer_circuit` unmodified and register correctly as circuit parameters (`c.get_parameters()`), confirming the builders are parameter-duck-typed even though they can't currently reach `QuantumLayer`.
  - `pcvl.algorithm.Analyzer` on a `Processor` constructed with `noise=pcvl.NoiseModel(transmittance=0.5)` (both the project's own circuit and a trivial 2-mode control circuit) → output sums to 1.0, no loss applied.
  - `Processor.probs()` with `min_detected_photons_filter(0)` on the same trivial circuit → correctly loss-truncated distribution (`|0,0⟩: 0.5` for `transmittance=0.5` on a single input photon).
  - `Processor.experiment` → confirmed a `perceval.components.experiment.Experiment` instance, the exact type `QuantumLayer(experiment=...)` expects — relevant if a future non-polarization dual-rail re-encoding is ever pursued.
  - `Processor.set_postselection`/`.post_select_fn` confirmed present as an outer-`Processor`-level API.
- `venv/Lib/site-packages/perceval/components/core_catalog/controlled_rotation_gates.py` — HIGH confidence, read directly (`PostProcessedControlledRotationsItem.build_circuit`/`build_experiment`: `4*n`-mode local circuit, `set_postselection` on data/ctrl dual-rail pairs, `add_herald(i, 0)` on all `2n` ancilla modes).
- `venv/Lib/site-packages/merlin/algorithms/layer.py`, `layer_utils.py` — HIGH confidence, read directly (`QuantumLayer.__init__`'s `circuit`/`experiment`/`builder` mutual exclusivity, `prepare_input_state`'s annotation rejection).
- `iqp_photonic_encoding.py`, `generator/neighbor_locality.py`, `generator/naturally_ordered_generator.py`, `generator/data.py`, `generator/train.py`, `generator/noise.py`, `benchmark.py`, `batch_sweep.py` (this repo) — HIGH confidence, read directly, established existing conventions (mode-mapping dicts, herald-spec local→global translation, top-level driver script pattern, `results/` output convention, two-condition statistical-check pattern).
- `docs/iqp-baseline.md` (this repo) — HIGH confidence, read directly (Van den Nest cosine-formula analytic gradient precedent, barren-plateau formal definition, average-case framing).
- `.planning/research/STACK.md` (sibling research thread, this milestone) — MEDIUM confidence for the Julia-specific claims (Julia not installed locally, so those claims could not be independently re-verified here); HIGH confidence for the parts also independently re-verified above (`PostProcessedControlledRotationsItem`'s success-probability table, `PhotonLossTransform`'s `QuantumLayer`-only reachability — now additionally explained by this research's `requires_polarization` finding, which `STACK.md` did not test).
- `.planning/PROJECT.md` (this repo) — HIGH confidence, read directly (v3.0 milestone scope, Must-have status of all four items, historical Jul-25 stall-risk framing).

---
*Architecture research for: MerLin v3.0 milestone — IQP circuit study & write-up*
*Researched: 2026-08-07*
