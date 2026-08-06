# Stack Research

**Domain:** v3.0 milestone — IQP-photonic trainability study, loss-hardness study, arbitrary-θ two-qubit gate, independent Julia verifier
**Researched:** 2026-08-06
**Confidence:** HIGH for items 1–3 (verified by reading installed package source + live execution against the installed venv). MEDIUM for item 4 (verified via WebFetch/WebSearch of official repos/docs — no local execution possible, Julia is not installed in this environment).

## Headline findings

1. **STUDY-01 (trainability) needs zero new packages.** MerLin's `QuantumLayer` is a `torch.nn.Module`; gradient-variance-vs-system-size is a plain PyTorch autograd sweep over the existing stack (`torch==2.12.1`, `numpy`, `scipy`, `matplotlib`, all already installed).
2. **STUDY-02 (loss) needs zero new packages either — MerLin already ships a differentiable loss model.** `merlin/measurement/photon_loss.py` implements `PhotonLossTransform`, a fully differentiable per-mode photon-survival map, wired into `QuantumLayer(noise=pcvl.NoiseModel(transmittance=..., brightness=...))`. This was **not previously used** in this project but is already installed (`merlinquantum==0.4.0`). Raw Perceval also ships a separate, independently-implemented loss model (`LossSimulator` / `LC` component, ancilla-beamsplitter construction) usable as a second, structurally-different cross-check of the same physics.
3. **ARB-01 has a real answer already sitting in the installed Perceval catalog** — `perceval.components.core_catalog.controlled_rotation_gates.PostProcessedControlledRotationsItem` (catalog key `"postprocessed controlled gate"`) implements a genuinely tunable `n`-qubit controlled-phase gate `C...CZ(α)`, `α ∈ ℝ` free. For `n=2` this is exactly `diag(1,1,1,e^{iα})` — verified empirically below by direct amplitude/phase readout. This is a **different gate family** (post-selection on ancilla vacuum + data-rail validity, arXiv:2405.01395) from the fixed-π/4 `heralded_cz` already in use (ancilla-heralded Knill construction, arXiv:quant-ph/0110144) — no new install required, but it is a new circuit family to integrate, with its own (lower, α-dependent) success probability.
4. **Ket.jl is real and well-maintained but is the wrong tool for this job.** It is a Bell-inequality/entanglement/nonlocality toolbox over discrete qubit density matrices — it has no notion of Fock states, photon number, permanents, or linear-optical unitaries. For the two stated Julia use cases, two *other* Julia packages fit far better: **Yao.jl** (qubit-circuit statevector simulator, for cross-checking the existing numpy-based `exact_qubit_iqp_distribution` qubit-side reference) and **BosonSampling.jl** (permanent-based linear-optics simulator with built-in loss and partial-distinguishability models, for cross-checking the Perceval/MerLin photonic-side loss physics directly). The SDP angle does not have a clean literature match to "bound classical simulability under loss" — see the dedicated section below before committing to it.

---

## Recommended Stack

### STUDY-01: trainability / barren-plateau measurement

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| `torch` | 2.12.1 (installed, unchanged) | Autograd for `∂L/∂θᵢ` per parameter, per random draw | MerLin's `QuantumLayer` is a standard `nn.Module`; gradients over its parameters are already differentiable end-to-end through the SLOS-based exact simulator (same exactness the weight-1/weight-2 TVD work already relies on) — no shot noise contaminating the gradient-variance measurement, which is essential for a clean McClean-et-al.-style barren-plateau protocol. |
| `numpy` / `scipy` | 2.5.1 / 1.18.0 (installed) | Aggregate gradient variance across seeds; fit variance-vs-`n` decay (e.g. `scipy.optimize.curve_fit` for `Var ~ c·b^n`) | Already the project's numerics stack — no reason to add `statsmodels` or similar for a single exponential-decay fit. |
| `matplotlib` | 3.11.1 (installed) | Log-variance-vs-`n` plots (the standard barren-plateau diagnostic figure) | Already installed; project's existing `visualize.py`/`generator/visualize.py` establish the plotting convention to follow. |

**Optional, no-install efficiency tool:** `torch.func` (`vmap` + `grad`, stable in `torch` since 2.0, present in the installed 2.12.1) can vectorize "compute ∂L/∂θᵢ for many random parameter draws" instead of a Python-level loop over seeds. Worth using only if the naive loop is too slow at the largest `n` tested — not a prerequisite to start.

**What NOT to add:** No PennyLane, no Qiskit, no `qml.numpy` — the project's `CLAUDE.md` already parks PennyLane for this cycle, and MerLin/PyTorch already provides everything a gradient-variance sweep needs. Adding a second QML framework here would be scope creep with no capability gain.

### STUDY-02: photon loss / hardness-under-loss

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| `merlin.measurement.photon_loss.PhotonLossTransform` (via `QuantumLayer(noise=pcvl.NoiseModel(...))`) | shipped in `merlinquantum==0.4.0` (installed) | Differentiable per-mode uniform-transmittance loss applied directly to the Fock probability vector inside the training/inference graph | Confirmed by reading `merlin/measurement/photon_loss.py` directly: `resolve_photon_loss_kernel()` reads `pcvl.NoiseModel.brightness`/`.transmittance` off the `Experiment`, and `PhotonLossTransform.forward()` is a plain differentiable matrix multiply (`distribution @ matrix`) built from binomial per-mode survival statistics. This means loss-under-training (does the *trained* circuit's output distribution and its gradient behavior survive loss) is answerable **inside the same MerLin pipeline** already used for weight-1/weight-2 — not a separate side-channel. |
| `perceval.utils.noise_model.NoiseModel` | perceval-quandela==1.2.4 (installed) | Declares `transmittance`, `brightness`, `indistinguishability`, `g2`, `phase_imprecision`, `phase_error` — the noise vocabulary both Perceval and MerLin consume | Read directly from `venv/Lib/site-packages/perceval/utils/noise_model.py`. All parameters default to "no noise" (transmittance=1, etc.), so an existing weight-1/weight-2 circuit gets loss added purely by passing a populated `NoiseModel` — no circuit-construction changes needed. |
| `perceval.simulators.loss_simulator.LossSimulator` + `perceval.components.non_unitary_components.LC` (loss channel) | perceval-quandela==1.2.4 (installed) | A **second, independently-implemented** loss model: each lossy mode is expanded into a beamsplitter coupling to a traced-out ancilla mode (the standard "fictitious beamsplitter" loss model), not a differentiable linear map | Read directly from `venv/Lib/site-packages/perceval/simulators/loss_simulator.py`. Structurally different code path from MerLin's `PhotonLossTransform` (ancilla-mode expansion + `BSDistribution` post-processing vs. a precomputed binomial transform matrix) — useful as an **in-Python cross-check that the two loss models agree**, before ever reaching for Julia. Not differentiable, so not a substitute for `PhotonLossTransform` inside training — a validation tool, not the training-loop tool. |

**Confirmed via source read** (not run live, since this is describing existing shipped capability, not new code): MerLin's noise support is not limited to loss — `merlin/pcvl_pytorch/noisy_slos.py` also implements a fully differentiable **source-indistinguishability and g² (multi-photon emission)** noise model (`NoisyG2SLOSComputeGraph`, `NoisySLOSComputeGraph`, "Orthogonal Bad Bits" formalism). This is a stretch capability beyond the stated STUDY-02 scope (pure transmission loss) but costs nothing extra to know about if the write-up wants to discuss "loss" more broadly as "realistic photonic noise."

**What's missing (genuinely, not just unused):**
- Perceval/MerLin do not ship any **classical-simulability-under-loss decision procedure** (e.g., an implementation of the Renema/Oszmaniec–Brod/García-Patrón-style transmission-threshold argument, or a matrix-product-state simulator that could demonstrate polynomial-time classical simulation once loss crosses a threshold). This is a methodology/write-up gap, not a code gap: the milestone's STUDY-02 deliverable is presumably to *apply* one of these known threshold arguments (or a from-scratch loss-scaling numerical study) to this specific weight-1+weight-2 circuit, not to implement a new lossy-simulation algorithm. A 2025 preprint, **"Matrix product state approach to lossy boson sampling and noisy IQP sampling"** (arXiv:2510.24137), is the closest direct precedent — same problem class (noisy/lossy IQP sampling), current, and MPS-based rather than SDP-based. Flagging this now because it changes what STUDY-02's "hardness survives loss?" answer should be checked against: an analytic/numerical threshold comparison to this literature, not a from-scratch complexity-theory derivation.
- No package here computes **permanents** (needed for exact classical brute-force cross-checks of small lossy-photonic distributions) — Perceval's own SLOS backend already does this internally in Python/C++ (`exqalibur`), so nothing needs adding for the Python side; this gap only matters for the Julia cross-check (see below).

### ARB-01: continuously-tunable two-qubit diagonal phase gate

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| `perceval.components.core_catalog.controlled_rotation_gates.PostProcessedControlledRotationsItem` (via `pcvl.catalog['postprocessed controlled gate']`) | shipped in perceval-quandela==1.2.4 (installed) | `C...CZ(α)` gate, `n≥2` qubits, `α: float` free parameter (default `π`) | This is the answer to "is there a path to arbitrary-θ beyond fixed-π/4 `heralded_cz`?" — **yes, in the already-installed package.** Verified live against the installed venv (see below): calling `item.build_circuit(n=2, alpha=α)` for arbitrary real `α` produces a circuit whose action on the 4 computational-basis dual-rail inputs is exactly `diag(1,1,1,e^{iα})` up to the same operator identity already used for the fixed-π/4 case (`CP(α) = exp(iα/4·(I − Z_i − Z_j + Z_i·Z_j))`) — so the existing weight-1 `WP` local-phase-correction machinery composes with this gate exactly the way it already composes with `heralded_cz`. |

**Verified empirically (live run against installed `perceval-quandela==1.2.4`):**

Amplitude/phase readout via `Simulator.prob_amplitude()` on the bare (un-postselected) 8-mode circuit for `n=2, α=π/3` (60°):

| ctrl,data input | amplitude | phase | `\|amp\|²` |
|---|---|---|---|
| `\|0,0⟩` | 0.3333 + 0j | 0.0° | 0.1111 |
| `\|0,1⟩` | 0.3333 + 0j | ~0° | 0.1111 |
| `\|1,0⟩` | 0.3333 + 0j | ~0° | 0.1111 |
| `\|1,1⟩` | 0.1667 + 0.2887j | **60.0°** | 0.1111 |

The `|1,1⟩` term picks up exactly `α` (60.0° for `α=π/3`, to floating-point precision) relative to the other three terms — this is the textbook controlled-phase signature, confirmed for a non-special angle (not just `α=π`), which is the strongest possible empirical evidence this gate is genuinely continuously tunable rather than only correct at a few special points.

`logical_perf` (post-selection success probability, uniform across the 4 computational-basis inputs, measured via `Processor.probs()` with `compute_physical_logical_perf(True)`):

| `α/π` | success probability |
|---|---|
| 0.032 (≈0.1 rad) | 0.4240 |
| 0.25 (π/4) | 0.1334 |
| 0.5 (π/2) | 0.0905 |
| 0.667 (2π/3) | 0.0858 |
| 1.0 (π, standard CZ) | **0.1111 = 1/9** — matches the known literature figure for the classic postselected-CZ gate (this catalog item's `article_ref`, arXiv:2405.01395, generalizes the `1/9`-success postselected CZ of Ralph–Langford–Bell–White, PhysRevA.65.062324, which the project's `PostProcessedCzItem` — noted but not used — already implements as the fixed-`α=π` special case). |

**Practical implications for integration:**
- Success probability is **not monotonic and not always better than `heralded_cz`'s fixed 2/27 ≈ 0.074** — at small `α` it is much higher (~0.42 near `α→0`), near `α=π/2` it dips to ~0.09, comparable to `heralded_cz`. Any weight-2 sweep over `α` needs to budget for this α-dependent success rate, not assume a constant one.
- This gate uses **post-selection on ancilla vacuum + data-rail validity** (`Processor.probs()` handles this the same way it already handles `heralded_cz`'s heralds — no new API surface to learn), not measurement-heralding in the same sense as `heralded_cz`. Practically identical to integrate (same `Processor.add()` composition pattern already verified for `heralded_cz` in the prior weight-2 research), but worth naming explicitly as a different gate *family* if the write-up compares the two.
- `PostProcessedCzItem` (`catalog['postprocessed cz']`), already present but previously dismissed as "a different gate family" in the fixed-angle weight-2 work, is now understood to be the `α=π` special case of this same tunable family — worth citing together in the write-up rather than treating as unrelated.

**What NOT to do:** Do not attempt to parameterize `heralded_cz`'s `theta1`/`theta2` — as already documented in this project's prior weight-2 research, those are hardcoded class constants with no exposed angle parameter, confirmed by source read. `PostProcessedControlledRotationsItem` is a **separate, already-tunable gate**, not a patch to `heralded_cz`.

### Independent Julia verifier

| Technology | Version | Purpose | When to Use |
|------------|---------|---------|-------------|
| Julia | 1.10 LTS (recommend) or 1.12.6 (current stable, released Apr 2026) | Language runtime | **Not installed in this environment** (`julia --version` → not found). Genuinely new toolchain addition, not a resume of existing infra. Prefer the LTS (1.10.x) unless a chosen package explicitly requires newer — fewer surprises this close to a Sept 1 deadline. Install via `juliaup` (the official Julia version manager) rather than a bare installer, so switching to whatever version a package needs is a one-line command. |
| **Yao.jl** | current (QuantumBFS/Yao.jl, actively maintained, Apache-2.0) | Independent qubit-circuit statevector simulator — build the same H → diagonal-phase-layer → H IQP circuit and get an exact distribution | **This, not Ket.jl, is the right tool for use case (a)** — cross-checking the exact qubit-side reference. The project's existing qubit-side reference (`exact_qubit_iqp_distribution` in `iqp_photonic_encoding.py`) is a **hand-rolled numpy statevector construction**, not built on any circuit-simulation library — so the strongest possible independent cross-check is a from-scratch reimplementation in a different language on a different circuit-simulation engine, i.e., building the actual gate sequence (Hadamards, `Rz`/controlled-phase gates matching the weight-1/weight-2 operator identities) in Yao.jl and comparing its output distribution against both the numpy reference and the Perceval/MerLin photonic output. |
| **BosonSampling.jl** (+ its companion **Permanents.jl**) | current (Seron & Restivo, ULB; published in *Quantum*, June 2024; registered in Julia General, `] add BosonSampling`) | Independent permanent-based exact simulator for linear-optical circuits, with **built-in loss and partial-distinguishability models** | The right tool for use cases (a) at the photonic level and (b) for STUDY-02: build the same weight-1/weight-2 photonic circuit (as a Perceval-equivalent unitary matrix / optical-element sequence) independently in Julia and get an exact permanent-based output distribution, including loss — a genuinely different computational method (permanent evaluation) from both Perceval's SLOS backend and MerLin's `PhotonLossTransform`, which is what makes it a real cross-check rather than the same code in a different language. |
| **Ket.jl** | current (dev-ket/Ket.jl, actively maintained — 661 commits, Zenodo-DOI'd, MIT license) | Bell-inequality / entanglement / nonlocality toolbox over discrete quantum states, with `JuMP`-integrated helper functions (`partial_trace`, `partial_transpose`) for building SDP-based Bell/entanglement witnesses | **Verdict: real and well-maintained, but wrong domain for both stated use cases.** No Fock states, no photon number, no permanents, no linear-optical circuit model of any kind — its "quantum information" is exclusively discrete-dimension qubit/qudit density-matrix nonlocality theory (MUBs, SIC-POVMs, Bell/Tsirelson bounds, entanglement robustness). It cannot build or simulate the photonic circuit at all, so it cannot serve use case (a) as an exact-distribution cross-check. For use case (b), see the SDP section below — the mismatch is not "Ket.jl is broken," it's that its SDP machinery targets a different question (nonlocality/entanglement certification) than "bound classical simulability of a lossy sampling process." |
| `JuMP.jl` + `SCS.jl` | current, both in Julia General registry, actively maintained (JuMP-dev 2026 held May 2026; SCS.jl MIT-licensed) | Generic conic/SDP modeling + a free open-source SDP solver | Only pull this in if a concrete SDP formulation is actually decided on (see below) — don't install "just in case." If needed, `SCS.jl` is the standard free choice (no license/Mosek-key friction); Ket.jl's own SDP-based functions (e.g. `local_bound`) already assume a JuMP-compatible solver is present, so this pairing is required infrastructure *if* Ket.jl's Bell-style tooling ends up used for anything (see recommendation below), independent of the loss-bounding question. |

## SDP formulation for bounding classical simulability under loss — honest assessment

The literature searches run for this milestone (classical simulability of lossy boson sampling/GBS, IQP-under-noise hardness, boson-sampling verification) turned up **no standard SDP relaxation whose stated purpose is "bound classical simulability of a lossy linear-optical sampler."** The dominant tool families in that specific literature are:
- **Analytic transmission-threshold arguments** (Renema et al., Oszmaniec–Brod, García-Patrón et al.) — closed-form or semi-closed-form bounds on the loss rate below which a classical algorithm (often based on the permanent's approximability or a "thinning" argument) becomes efficient. No SDP.
- **Tensor-network / matrix-product-state simulability arguments** — the closest, most current precedent is arXiv:2510.24137 ("Matrix product state approach to lossy boson sampling and noisy IQP sampling," Oct 2025), which studies exactly this problem class (lossy/noisy IQP-style sampling) via MPS bond-dimension scaling, not SDP.
- **SDP does appear** in the *adjacent* boson-sampling verification literature (e.g., Bell-inequality-style or likelihood-based genuine-multiphoton-interference certification), but that answers a different question — "is this sampler doing real quantum interference at all?" — not "does the sampling task remain classically hard once loss is added?" This is exactly the kind of question Ket.jl's Bell/nonlocality machinery *would* be a legitimate fit for, if the milestone's actual interest turns out to be interference-certification rather than complexity-threshold-under-loss.

**Recommendation:** Treat "SDP via Ket.jl" as an open, unresolved question rather than a locked plan — the owner flagged this as a genuine open question, and this research confirms it is. Two honest paths forward, and the roadmap should pick one explicitly rather than defaulting into Ket.jl because it was already the ambient self-study track:
1. **If STUDY-02's actual claim is "sampling hardness survives loss up to threshold X"** — follow the MPS/threshold-argument literature (arXiv:2510.24137 and its citations) directly; the natural Julia tool is `BosonSampling.jl`'s loss model plus a from-scratch MPS bond-dimension scaling study (would need a Julia tensor-network package, e.g. `ITensors.jl`, if pursued — **not yet verified as a fit, flag as a future research item if this path is chosen**). This path does not need Ket.jl or SDP at all.
2. **If the actual interest is closer to "can we certify genuine multiphoton interference under the loss levels observed"** — that's a Bell/nonlocality-style question, and Ket.jl + JuMP + SCS.jl is a legitimate, well-matched toolchain for it. But this is a different research question from "does the IQP sampling-hardness argument survive loss," and the milestone brief as given is closer to (1).

Given the Sept 1 deadline, defaulting to path (1) (no Ket.jl, no SDP) for the STUDY-02 deliverable itself, while optionally using Ket.jl separately/later as the originally-scoped "informal ambient self-study" (per `MerLin_SMART_Spec_Sept1.md`'s own framing) is the lower-risk reading — but this is a judgment call for the roadmap, not a settled fact from this research.

## Installation

```bash
# Python side: NOTHING to install. All STUDY-01/STUDY-02/ARB-01 work uses
# packages already in ./venv (perceval-quandela==1.2.4, merlinquantum==0.4.0,
# torch==2.12.1, numpy==2.5.1, scipy==1.18.0, matplotlib==3.11.1).

# Julia side: new toolchain.
# 1. Install juliaup (version manager), then:
juliaup add lts        # Julia 1.10.x LTS
juliaup default lts

# 2. In the Julia REPL package manager:
julia -e 'using Pkg; Pkg.add(["Yao", "BosonSampling"])'

# 3. Only if the SDP/Ket.jl path (option 2 above) is explicitly chosen:
julia -e 'using Pkg; Pkg.add(["Ket", "JuMP", "SCS"])'
```

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|--------------------------|
| MerLin's built-in `PhotonLossTransform` (via `QuantumLayer(noise=...)`) for STUDY-02's training-loop loss model | Hand-rolling a custom differentiable loss layer on top of raw Perceval `Processor.probs()` | Never for this milestone — MerLin already ships exactly this, verified by source read; hand-rolling would duplicate tested code for no capability gain. |
| `PostProcessedControlledRotationsItem` for ARB-01 | Deriving a fresh linear-optical decomposition of `CP(α)` from scratch (e.g. via `Generic2ModeItem`'s free 2-mode `BS.H` + phases, hand-solved for an arbitrary-α controlled-phase unitary) | Only if the catalog gate's fixed 4-ancilla-mode topology turns out to be a poor fit for composing with the rest of the circuit (e.g. mode-budget pressure at larger `n`) — not expected to be needed, but the `Generic2ModeItem` catalog entry (already installed, a free universal 2-mode `BS.H`+3-phases primitive) is the fallback building block if a bespoke decomposition is ever needed. |
| Yao.jl for qubit-side cross-check | QuantumInformation.jl or QuantumOptics.jl (both real, found in the same search) | Only if Yao.jl's autodiff/circuit-builder API proves awkward for this specific commuting-diagonal-gate circuit shape — both alternatives can also build and exactly simulate small qubit circuits, but Yao.jl is the most widely used/maintained circuit-first simulator in the Julia ecosystem and is the natural first choice. |
| BosonSampling.jl for photonic-side cross-check | Reimplementing a bespoke permanent-based simulator by hand in Julia | Only if BosonSampling.jl's circuit-construction API can't express the specific weight-1 polarization-encoding / weight-2 heralded-gate composition used here — plausible friction point, not yet verified, flag as first thing to check when this package is actually picked up. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|--------------|
| Ket.jl as the primary/only Julia tool for either stated use case | No photonic/linear-optical circuit model at all (confirmed: no Fock states, no permanents, no boson-sampling support in its docs/README) — cannot execute either cross-check task as literally stated | Yao.jl (qubit cross-check) and BosonSampling.jl (photonic cross-check); reserve Ket.jl for a genuinely Bell/nonlocality-flavored question if one emerges |
| A generic/unverified SDP relaxation "for classical simulability under loss" invented ad hoc to give Ket.jl something to do | No such standard relaxation was found in the current (2024–2025) literature for this exact question; inventing one without a literature anchor risks a result that doesn't mean what the write-up claims it means | The MPS/threshold-argument literature (arXiv:2510.24137 and its citation trail) for the "does hardness survive loss" question; Ket.jl's actual SDP strength (Bell/nonlocality bounds) only if the research question is reframed toward interference certification |
| PennyLane, Qiskit, or any second Python QML/quantum-circuit framework for STUDY-01/STUDY-02 | Explicitly parked per this project's `CLAUDE.md`/SMART spec for this cycle; MerLin+PyTorch+Perceval already covers every capability needed | Existing installed stack only |
| Hand-deriving `heralded_cz`'s beamsplitter angles to try to make it tunable | Already established as a dead end in this project's prior weight-2 research — `theta1`/`theta2` are hardcoded, no angle kwarg exists | `PostProcessedControlledRotationsItem` — a different, already-tunable gate |

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|------------------|-------|
| perceval-quandela==1.2.4 | merlinquantum==0.4.0, torch==2.12.1, Python 3.10–3.12 (repo venv 3.12) | No changes from existing installed versions — `NoiseModel`, `LossSimulator`, `LC`, `PostProcessedControlledRotationsItem` are all already present in this exact installed version (confirmed by direct source read), not new-version features requiring a bump. |
| merlinquantum==0.4.0 | perceval-quandela==1.2.4, torch<2.13 (per project `CLAUDE.md`) | `QuantumLayer(noise=pcvl.NoiseModel(...))` and the differentiable `PhotonLossTransform`/`NoisySLOSComputeGraph` pipeline are already present in this installed version — confirmed by direct source read of `merlin/algorithms/layer.py`, `merlin/measurement/photon_loss.py`, `merlin/pcvl_pytorch/noisy_slos.py`. |
| Julia 1.10 LTS / 1.12.6 | Yao.jl, BosonSampling.jl, Ket.jl (if used), JuMP.jl+SCS.jl (if used) | Not verified against a specific Julia minor version for each package — first Julia-side task should be `Pkg.add` + `Pkg.status` to confirm no version conflicts before writing any cross-check code; this is a genuinely new toolchain with no prior track record in this project. |

## Sources

- `venv/Lib/site-packages/perceval/utils/noise_model.py` — HIGH confidence, read directly (NoiseModel parameter set and defaults).
- `venv/Lib/site-packages/perceval/simulators/loss_simulator.py` — HIGH confidence, read directly (ancilla-beamsplitter loss model, independent of MerLin's).
- `venv/Lib/site-packages/merlin/measurement/photon_loss.py` — HIGH confidence, read directly (`PhotonLossTransform`, `resolve_photon_loss`/`resolve_photon_loss_kernel`).
- `venv/Lib/site-packages/merlin/pcvl_pytorch/noisy_slos.py` — HIGH confidence, read directly (source-indistinguishability/g² noise, differentiable, Orthogonal Bad Bits model).
- `venv/Lib/site-packages/merlin/algorithms/layer.py` — HIGH confidence, read directly (`QuantumLayer(noise: pcvl.NoiseModel | None)` constructor signature, line 130).
- `venv/Lib/site-packages/perceval/components/core_catalog/controlled_rotation_gates.py` — HIGH confidence, read directly (`PostProcessedControlledRotationsItem`, `build_control_gate_unitary`, arXiv:2405.01395 reference).
- `venv/Lib/site-packages/perceval/components/core_catalog/postprocessed_cz.py` — HIGH confidence, read directly (confirms `α=π` special case relationship to the pre-existing `postprocessed cz` catalog item).
- Live execution against installed `perceval-quandela==1.2.4` in `./venv` (`Processor.probs()` with `compute_physical_logical_perf(True)`, `Simulator.prob_amplitude()`) — HIGH confidence, ground truth: measured success-probability table and exact 60.0° phase readout for `α=π/3` on `PostProcessedControlledRotationsItem(n=2)`.
- `docs/iqp-baseline.md` and `iqp_photonic_encoding.py` (existing project files) — HIGH confidence, read directly, established that the existing qubit-side reference is hand-rolled numpy, informing the Yao.jl recommendation.
- [Ket.jl (dev-ket/Ket.jl) GitHub](https://github.com/dev-ket/Ket.jl) — MEDIUM confidence, WebFetch of official repo (feature set, license, activity; exact version/release date not machine-readable from the page).
- [Ket.jl on Julia Packages](https://juliapackages.com/p/ket) and [Zenodo record](https://doi.org/10.5281/zenodo.15166547) — MEDIUM confidence, corroborates active maintenance and registry status.
- [Yao.jl (QuantumBFS/Yao.jl) GitHub](https://github.com/QuantumBFS/Yao.jl) and [yaoquantum.org](https://yaoquantum.org/) — MEDIUM confidence, WebSearch-sourced, confirms maintainers, license (Apache-2.0), and 2026 activity.
- [BosonSampling.jl paper, Quantum journal, June 2024](https://quantum-journal.org/papers/q-2024-06-18-1378/) and [arXiv:2212.09537](https://arxiv.org/abs/2212.09537) — MEDIUM confidence; WebFetch of the GitHub repo confirmed loss + partial-distinguishability support and Julia General registry status, but exact current version/Julia-version requirement was not machine-readable from the fetched page — verify directly (`Pkg.add("BosonSampling"); Pkg.status()`) before relying on it.
- [arXiv:2510.24137, "Matrix product state approach to lossy boson sampling and noisy IQP sampling" (Oct 2025)](https://arxiv.org/pdf/2510.24137) — MEDIUM confidence (WebSearch result, abstract-level only, not fully read) — the most directly relevant current precedent for STUDY-02's methodology; read in full before finalizing STUDY-02's approach.
- [JuMP.jl](https://jump.dev/) and [SCS.jl (jump-dev/SCS.jl)](https://github.com/jump-dev/SCS.jl) — MEDIUM confidence, WebSearch-sourced, confirms active maintenance (JuMP-dev 2026 conference) and MIT licensing, only relevant if the SDP path is chosen.
- [endoflife.date/julia](https://endoflife.date/julia) and general WebSearch on Julia release status — MEDIUM confidence, current Julia 1.12.6 stable / 1.10.11 LTS as of research date; local `julia --version` confirmed **not installed** in this environment (HIGH confidence, verified directly).
- General WebSearch, "semidefinite programming boson sampling verification classical simulability loss 2024 2025" — MEDIUM confidence, used to ground the "no clean SDP match" finding; not exhaustive, flagged honestly as a negative/absence claim that should be re-checked if the SDP path is ever seriously pursued.

---
*Stack research for: MerLin v3.0 milestone — trainability study, loss-hardness study, arbitrary-θ weight-2 gate, Julia verifier*
*Researched: 2026-08-06*
