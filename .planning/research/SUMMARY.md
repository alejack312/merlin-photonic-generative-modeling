# Project Research Summary

**Project:** MerLin Photonic Generative Modeling — v3.0 milestone (IQP Circuit Study & Write-Up)
**Domain:** Quantum-computing research study (empirical trainability + hardness-under-loss measurement on an existing photonic IQP encoding), plus one open primitive-design question and a cross-language verification toolchain
**Researched:** 2026-08-06 to 2026-08-07
**Confidence:** HIGH overall — every load-bearing claim about Perceval/MerLin behavior was verified by direct source read and/or live execution against this repo's own `./venv`, not inferred from docs or memory. The Julia toolchain and several literature-threshold specifics are MEDIUM (not locally verifiable, or abstract-only reads).

## Executive Summary

This milestone is not a "pick a stack" research problem — the stack is already fully installed and, for three of the four deliverables, requires zero new packages. The real research payoff of this phase was discovering a **hard architectural constraint that changes how two of the four deliverables must be built**: this project's existing weight-1/weight-2 circuits use Perceval's polarization formalism (`requires_polarization = True`), and MerLin's `QuantumLayer` — the class every autograd/gradient mechanism in the codebase assumes — categorically rejects polarization-annotated states (`ValueError: BasicState with annotations is not supported`, verified live). STUDY-01 (trainability) and STUDY-02 (loss) therefore cannot reuse Phase 7's `QuantumLayer`/`jacrev` pattern; they must be built on parameter-shift gradients (exact, since every weight-1 gate is an `exp(iθZ)`-type rotation) and on `Processor.probs()` + `NoiseModel` respectively (not `Analyzer`, which was independently verified to silently ignore loss). Both substitute mechanisms are already fully specified and lower-risk than the naive plan, not blockers — but skipping this finding and copy-pasting Phase 7's code would silently fail or silently produce wrong physics.

The recommended approach: treat ARB-01 (arbitrary-θ two-qubit gate) as an independent, decoupled track — its core resolvability question is already answered (Perceval's catalog ships `PostProcessedControlledRotationsItem`, empirically confirmed continuously tunable at a non-special angle) — while STUDY-01/STUDY-02 run immediately against the already-validated, already-shipped fixed-π/4 `heralded_cz` circuit rather than waiting on ARB-01 to resolve. This is the single highest-leverage structural decision surfaced by the pitfalls research: ARB-01 is "genuinely open research" with no reliable time estimate and is explicitly the item most likely to reproduce this project's historical stall pattern (the same one that killed a prior PennyLane track at the equivalent milestone stage). Making STUDY-01/02/WRITE-01 hard-dependent on ARB-01 landing first would convert one open-ended item into a single point of failure for the entire milestone.

The key risks, in priority order: (1) false ARB-01 dependency chain blocking the other three deliverables (Pitfall 25 — mitigated by explicit phase decoupling); (2) finite-size deception compounded by this project's actual compute budget — the achievable system size for a gradient-variance sweep is likely inside the exact range (N<10, or n<6) the project's own prior research already flags as historically misleading (Pitfall 15); (3) treating a small-n loss sweep as a standalone hardness result rather than positioning it against a literature threshold (arXiv:2510.24137, not yet fully read — Pitfall 18); (4) declaring ARB-01 "resolved" on the strength of one spot-checked angle rather than the same multi-α TVD/composability rigor bar `heralded_cz` cleared in v2.1 (Pitfall 20). None of these are blockers — all have a stated, concrete mitigation already worked out in this research.

## Key Findings

### Recommended Stack

Python side needs **zero new installs** — `torch==2.12.1`, `numpy==2.5.1`, `scipy==1.18.0`, `matplotlib==3.11.1`, `perceval-quandela==1.2.4`, and `merlinquantum==0.4.0` (all already in `./venv`) cover STUDY-01, STUDY-02, and ARB-01 entirely. Julia is a genuinely new toolchain (not installed in this environment) needed only for the optional independent-verifier track.

**Core technologies:**
- `torch` autograd / parameter-shift (manual, on the Analyzer pipeline) — exact gradients for STUDY-01, no shot noise, no new dependency
- `merlin.measurement.photon_loss.PhotonLossTransform` via `QuantumLayer(noise=pcvl.NoiseModel(...))` — MerLin's already-shipped differentiable loss model for STUDY-02, though the training-loop-friendly path is unreachable for this project's polarization circuit (see Architecture below); loss measurement instead goes through `Processor.probs()`
- `perceval.simulators.loss_simulator.LossSimulator`/`LC` — a second, structurally independent (ancilla-beamsplitter) loss model, used as an in-Python cross-check before trusting any loss number
- `perceval.components.core_catalog.controlled_rotation_gates.PostProcessedControlledRotationsItem` — already-shipped, continuously-tunable `C...CZ(α)` gate for ARB-01; empirically verified to produce exactly the expected phase at a non-special angle (α=π/3 → 60.0°)
- Julia (`juliaup`, 1.10 LTS) + **Yao.jl** (qubit-side statevector cross-check) + **BosonSampling.jl** (permanent-based photonic/loss cross-check) — the correct pair for the independent verifier; **Ket.jl was investigated and found to be the wrong tool** (no Fock-state/linear-optics support at all) for both originally-scoped use cases

**What NOT to add:** No PennyLane, no Qiskit, no second Python QML framework (explicitly parked per this project's CLAUDE.md); no ad hoc SDP formulation for "classical simulability under loss" — the literature search found no such standard relaxation exists for this exact question, and forcing one would produce a result that doesn't mean what it claims (see Pitfalls below).

### Expected Features

Four Must-have deliverables, all held to this project's existing rigor bar (exact-over-sampled computation, honest negative-result reporting, explicit scope/falsifiability statements — the same bar GEN-07/LIT-04/ENC-04 already set).

**Must have (table stakes):**
- STUDY-01: gradient-variance sweep across ≥3 system sizes, ≥100 draws each, explicit poly-vs-exponential model comparison (not eyeballed), stated init distribution and generator scope, honest statement of whether the achievable n sits inside the historically-misleading small-N range
- STUDY-02: loss sweep via `PhotonLossTransform`/`NoiseModel`, cross-checked against Perceval's independent `LossSimulator`, full read of arXiv:2510.24137 before finalizing methodology, explicit positioning against Aaronson-Brod's fixed-count-vs-fractional-loss distinction, explicit "what this does/doesn't establish" scope statement
- ARB-01: gate phase confirmed at ≥3 non-trivial α values, general-α operator identity written down, TVD validation at ≥1 non-special α, success probability reported as a function of α (not a single number, since it's measured non-monotonic), explicit comparison to the existing `heralded_cz`
- WRITE-01: methodology-before-results structure, literature-comparison tables, honest negative/inconclusive framing, self-explanation checkpoint transcripts, every number traceable to a specific script/seed

**Should have (differentiators):** extending STUDY-01 toward N≈20-24 (the range where the closest literature precedent's poly-vs-exp fit is documented to flip); mixed weight-1+weight-2 generator sweeps; weight-2 loss sweep combining herald failure with photon loss; a denser ARB-01 α sweep; the Julia cross-check.

**Explicitly out of scope this milestone:** any complexity-theoretic proof work (barren-plateau theorem, loss-threshold reduction), reaching hardware-relevant N, a deterministic (success-probability-1) two-qubit gate (known-infeasible), Ket.jl/SDP forced into STUDY-02's core claim, a peer-review-manuscript-grade write-up.

### Architecture Approach

The existing weight-1/weight-2 `iqp_photonic_encoding.py` module stays untouched and is reused as a forward-pass primitive by all three new capabilities; new work is additive (new functions in the same file, following the exact precedent weight-2 already set alongside weight-1) plus new top-level driver scripts mirroring the existing `batch_sweep.py`/`heralded_cz_derisking.py` convention. The `generator/` MerLin `QuantumLayer` pipeline is a structurally separate ansatz and is confirmed incapable of ever hosting the polarization circuit — it is not touched by this milestone.

**Major components:**
1. `generator/trainability.py` + `trainability_study.py` — parameter-shift gradient computation directly on the existing Analyzer-based distribution functions (no `QuantumLayer`), gradient-variance-vs-n aggregation and poly/exp model comparison
2. `iqp_photonic_encoding.py`'s new `*_lossy` functions + `loss_hardness_study.py` — loss-aware distribution functions built on `Processor.probs()` + `NoiseModel` (never `Analyzer`, which silently ignores loss), TVD-vs-transmittance sweep
3. `iqp_photonic_encoding.py`'s `build_arb_gate_insertion`/`build_weight2_arb_processor` + `arb01_derisking.py` — `PostProcessedControlledRotationsItem`-based gate, needing new `set_postselection` plumbing (4 ancilla modes vs. `heralded_cz`'s 2) not previously built in this codebase
4. `julia_verification/` — an isolated, subprocess+JSON side channel (never an in-process interop bridge like PyJulia/juliacall), so a Julia toolchain confirmed not-yet-installed can never become a runtime dependency of the Python pipeline or its 118-test suite

### Critical Pitfalls

1. **False ARB-01 → STUDY-01/02/WRITE-01 dependency chain (Pitfall 25).** ARB-01 is open-ended research with no time estimate; STUDY-01/02 need no ARB-01 output and should run against the already-validated `heralded_cz` circuit immediately. Sequencing them as one dependent chain converts a bounded risk into a single point of failure for the whole milestone — the single highest-leverage prevention in this research.
2. **Finite-size deception compounded by this project's actual compute budget (Pitfall 15).** The achievable gradient-variance sweep size is likely below both this project's own qubit-baseline threshold (n≥6) and the closest photonic-postselection literature's documented poly→exp fit-flip point (N=10→24). Any plateau/no-plateau verdict must state explicitly where the achieved range sits relative to both thresholds, not imply a settled conclusion from a small range.
3. **Analyzer silently ignores loss; QuantumLayer cannot host this project's circuit at all (Architecture finding, generalizes Pitfall 2).** `pcvl.algorithm.Analyzer` on a `Processor` with `NoiseModel` set returns a distribution that still sums to 1.0 — verified empirically. STUDY-02 must use `Processor.probs()` with `min_detected_photons_filter(0)` explicitly, never `Analyzer`.
4. **Premature "ARB-01 resolved" declaration (Pitfall 20).** STACK.md's single-α spot-check is promising but is exactly the kind of single-instance evidence this project's own Verification Traps table already warns is weak. ARB-01 needs the same multi-α TVD/composability rigor `heralded_cz` cleared across v2.1's Phase 10→13, not a shortcut on its highest-stakes open item.
5. **Vacuous small-n hardness-under-loss claim (Pitfall 18).** At n=2-3, any output distribution is trivially classically simulable regardless of loss — the complexity argument is asymptotic. STUDY-02's claim must be positioned against a named literature threshold (arXiv:2510.24137, full read required — not yet done), not reported as a standalone empirical finding.

## Implications for Roadmap

Based on combined research, suggested phase structure (four decoupled or lightly-coupled tracks, not one dependency chain):

### Phase A: ARB-01 de-risking + validation (standalone, can start immediately)
**Rationale:** Genuinely open research, per its own explicit framing — front-load it so a pivot (if needed) has maximum runway. Zero dependency on STUDY-01/02. Its "does a tunable gate exist" question is already answered YES by stack research; remaining work is validation at the existing rigor bar.
**Delivers:** De-risked, multi-α-validated `PostProcessedControlledRotationsItem` integration (or an honestly-documented non-resolution), operator identity, success-probability-vs-α curve.
**Addresses:** ARB-01's full table-stakes list (FEATURES.md).
**Avoids:** Pitfall 20 (premature "resolved" claim), Pitfall 22 (new gate's postselection mechanism reintroducing the herald/PBS failure class via a different API surface — needs its own de-risking check, the prior heralded_cz fix doesn't generalize).

### Phase B: STUDY-02 (loss-hardness) — runs immediately, parallel to Phase A
**Rationale:** Lower methodological risk than STUDY-01 (Pattern 2 — `.probs()` + `NoiseModel` — is fully verified end-to-end); mostly a sweep + literature-positioning task on top of already-available tooling. No dependency on ARB-01.
**Delivers:** TVD-vs-transmittance dataset, cross-checked against a second independent loss model, positioned against arXiv:2510.24137's threshold.
**Uses:** `PhotonLossTransform`/`NoiseModel`, `Processor.probs()`, `LossSimulator`/`LC` (STACK.md).
**Implements:** the `*_lossy` distribution functions + `loss_hardness_study.py` (ARCHITECTURE.md Pattern 2).

### Phase C: STUDY-01 (trainability) — runs immediately, parallel to Phase A/B
**Rationale:** Carries more open methodological risk than STUDY-02 (choosing the observable/loss for the barren-plateau protocol, weight-1-only vs. mixed scope) and benefits from starting in parallel rather than waiting. No dependency on ARB-01.
**Delivers:** Gradient-variance-vs-n dataset via parameter-shift (not autograd-through-QuantumLayer, per the architectural finding), explicit poly/exp model comparison, honest statement of the achieved-n ceiling relative to known deception thresholds.
**Uses:** parameter-shift on the existing Analyzer-based pipeline (ARCHITECTURE.md Pattern 1).
**Implements:** `generator/trainability.py` + `trainability_study.py`.

### Phase D: Julia verifier spike (small, early, time-boxed) — decoupled from Phase A/B/C's numeric results
**Rationale:** New-toolchain risk (per this project's CLAUDE.md-documented Jul-25 stall pattern) should surface early via a minimal install+hello-world spike, not be gated behind real numbers to diff against.
**Delivers:** Confirmed working `juliaup`/Yao.jl/BosonSampling.jl install with one trivial circuit each; the full cross-check scripts come later, after B/C produce real numbers to compare against.
**Avoids:** Pitfall 23 (Julia scope creep — fix the two closed comparison targets before writing any Julia code) and Pitfall 24 (forcing Ket.jl/SDP into STUDY-02 despite no clean formulation existing).

### Phase E: WRITE-01 (write-up) — last, but skeleton drafted early
**Rationale:** Cannot be substantively completed before A/B/C produce at least preliminary results, but its structure (methodology-first, literature-comparison tables, explicit scope statements) can and should be drafted in parallel as a template, per this project's own ENC-01→ENC-05 precedent.
**Delivers:** Final technical write-up synthesizing STUDY-01/02's honest verdicts, ARB-01's outcome (resolved or plainly-documented-open), and the Julia cross-check's result or honest non-completion note.

### Phase Ordering Rationale

- Phases A, B, C are independent by design (Pitfall 25 is the single highest-leverage finding from this research) — do not let roadmap sequencing imply a dependency that doesn't exist.
- Phase D is time-boxed and decoupled specifically because it's a new toolchain this close to the deadline; the closest analog to this project's own historical stall pattern.
- A **mid-milestone checkpoint** (Pitfall 26) should be a named roadmap artifact — a specific date (~Aug 18-20, given the Aug 6 start and Sept 1 deadline) with four explicit per-item progress questions (concrete evidence, not "in progress"). This is the project's own proven Jul-25-checkpoint template, reapplied.
- Every STUDY-01/STUDY-02 result must be labeled with which weight-2 gate family (fixed-π/4 `heralded_cz` vs. ARB-01's tunable gate) produced it (Pitfall 21) — if ARB-01 lands in time and results get re-run against it, that must be a clearly-labeled secondary/comparison result, not a silent substitution.

### Research Flags

Phases likely needing deeper research during planning:
- **Phase A (ARB-01):** the `set_postselection` global-mode-index translation plumbing is genuinely new code (not a reuse of `heralded_cz`'s herald-registration pattern) — worth a `research-phase` pass focused specifically on the local→global `PostSelect` translation helper.
- **Phase D (Julia verifier):** BosonSampling.jl's circuit-construction API fit for this project's specific weight-1 polarization-encoding/weight-2 heralded-gate composition is explicitly flagged as "not yet verified" — first thing to check when picked up.
- **Phase B (STUDY-02):** the arXiv:2510.24137 noisy-IQP-specific threshold formula was not retrievable from the abstract alone — needs a full-PDF literature read before methodology can be finalized (near-zero-code but load-bearing and non-deferrable).

Phases with standard patterns (skip research-phase):
- **Phase C (STUDY-01):** parameter-shift gradients on `exp(iθZ)`-type gates is closed-form, well-established math; no new API surface beyond what's already verified.
- **Phase B's loss-sweep mechanism itself** (as opposed to the literature-threshold question above): `Processor.probs()` + `NoiseModel` is already fully verified end-to-end in this research.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH (Python) / MEDIUM (Julia) | Python-side claims verified by direct source read + live execution against installed venv; Julia claims sourced from WebFetch/WebSearch of official repos only, no local Julia install to verify against |
| Features | HIGH (ARB-01, general shape) / MEDIUM (exact loss-threshold numerics) | Grounded in this project's own prior research and validated literature (McClean 2018, Aaronson-Brod 2016); the arXiv:2510.24137 noisy-IQP-specific threshold number is a stated open gap, not yet read in full |
| Architecture | HIGH | Every Perceval/MerLin behavioral claim (QuantumLayer polarization rejection, Analyzer silently ignoring loss, PostProcessedControlledRotationsItem's mode/postselection structure) verified by direct execution against this repo's own venv |
| Pitfalls | HIGH (project-specific/API claims) / MEDIUM (literature-applicability judgment calls) | API footguns and this-repo history verified directly; broader claims about how CV/photonic barren-plateau theory or loss-threshold literature applies to this project's specific circuit are informed judgment over cited sources, not fresh derivation |

**Overall confidence:** HIGH

### Gaps to Address

- **arXiv:2510.24137's noisy-IQP-specific threshold formula** — abstract-level only, not fully read. This is a table-stakes blocker for STUDY-02's central claim ("do our tested loss levels sit above/below the known threshold") and must be resolved with a full-PDF read before STUDY-02's methodology is finalized, not deferred to the write-up stage.
- **Julia package fit for this project's specific circuit shape** (BosonSampling.jl's ability to express the weight-1 polarization encoding / weight-2 heralded-gate composition) — explicitly flagged as unverified in STACK.md; first thing to check in Phase D, not assumed.
- **SDP formulation for "classical simulability under loss"** — actively searched for and not found in the current literature. Treat this as resolved-negative (don't force Ket.jl/SDP into STUDY-02); if the roadmap wants to preserve Ket.jl work at all, scope it explicitly as separate, informal, ambient self-study per the original SMART-spec framing, never as part of STUDY-02's validated claim.
- **Achievable system size for STUDY-01's sweep** — genuinely unknown until the parameter-shift harness is built and run; the roadmap should not commit to a specific n target, only to reporting honestly wherever the compute ceiling lands relative to the n≥6/N=24 thresholds.

## Sources

### Primary (HIGH confidence)
- Direct source reads of installed packages in this repo's `./venv`: `perceval/utils/noise_model.py`, `perceval/simulators/loss_simulator.py`, `merlin/measurement/photon_loss.py`, `merlin/pcvl_pytorch/noisy_slos.py`, `merlin/algorithms/layer.py`, `merlin/algorithms/layer_utils.py`, `perceval/components/core_catalog/controlled_rotation_gates.py`, `perceval/components/core_catalog/postprocessed_cz.py`, `perceval/components/experiment.py`, `perceval/components/core_catalog/heralded_cz.py`
- Live execution against installed `perceval-quandela==1.2.4`/`merlinquantum==0.4.0` in this repo's venv — amplitude/phase readout, success-probability tables, `QuantumLayer` polarization-rejection error, `Analyzer` loss-blindness confirmation
- This repo's own prior docs: `docs/iqp-baseline.md`, `docs/iqp-photonic-encoding.md`, `iqp_photonic_encoding.py`, `generator/neighbor_locality.py`, `.planning/PROJECT.md`, `CLAUDE.md`, `.planning/milestones/v2.1-MILESTONE-AUDIT.md`

### Secondary (MEDIUM confidence)
- McClean et al. 2018 (barren plateaus, gradient-variance-vs-system-size protocol) — WebSearch-sourced summary, well-known result
- Aaronson & Brod 2016, arXiv:1510.05245 (fixed-count vs. fractional photon loss) — WebSearch-sourced, corroborated across multiple sources
- arXiv:2510.24137 (MPS approach to lossy boson sampling and noisy IQP sampling) — abstract-level WebFetch only; boson-sampling threshold confirmed, noisy-IQP-specific number not yet retrieved
- arXiv:2405.01395 (literature grounding for `PostProcessedControlledRotationsItem`) — WebSearch-confirmed title/abstract
- Yao.jl, BosonSampling.jl, Ket.jl (GitHub/Julia Packages/Zenodo) — WebFetch/WebSearch of official repos, no local verification possible (Julia not installed)

### Tertiary (LOW confidence)
- None flagged as standalone LOW-confidence claims; all Julia-specific and literature-threshold gaps are explicitly carried forward as "Gaps to Address" above rather than treated as settled.

---
*Research completed: 2026-08-07*
*Ready for roadmap: yes*
