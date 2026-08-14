# Phase 18: Hardness-Under-Loss Assessment - Research

**Researched:** 2026-08-14
**Domain:** Perceval photon-loss simulation API + noisy-sampling-hardness literature (arXiv:2510.24137, arXiv:1610.01808)
**Confidence:** HIGH (API mechanics — verified by direct source read + empirical execution against this repo's own venv and circuit-building code); HIGH (paper content — full read, not abstract-only); MEDIUM (HARD-04 depolarizing-translation guidance — genuinely open, deferred to owner per CLAUDE.md)

## Summary

The single most important finding of this research is that **HARD-01's literal instruction — `Processor.probs()` + `NoiseModel(transmittance=η)` — silently does not apply loss to this project's circuits**, because they are polarization-annotated (this project's entire ENC-01 encoding, locked since Phase 9). This was confirmed two ways: (1) a direct source-code trace through `perceval/runtime/processor.py`, `abstract_processor.py`, and `components/experiment.py` showing that `Processor.with_input()` short-circuits the noise-model pathway for any `AnnotatedFockState`/polarization input; (2) live execution against `iqp_photonic_encoding.build_full_circuit` showing `NoiseModel(transmittance=0.5)` produces *bit-identical* output to the no-noise baseline. This is a third instance of the "silent loss-ignoring" failure mode HARD-01 already warns about for `Analyzer` — except this time it's `Processor` itself, for this project's specific encoding.

The fix, also verified empirically, is to stop routing loss through the `noise=NoiseModel(...)` constructor parameter and instead insert Perceval's `LC` (loss channel) component directly into the circuit via `Processor.add(mode, LC(loss))` — i.e., use the exact mechanism HARD-02 names as the "independent cross-check" (`LossSimulator`/`LC`) as the *primary* loss mechanism for this project, not merely a spot-check. `Processor.probs()`'s own `SimulatorFactory` auto-detects `LC` components and correctly composes `LossSimulator` on top of `PolarizationSimulator` — confirmed both by source (`simulator_factory.py`) and by a live run reproducing the exact expected 50/50 survival split at `loss=0.5`. A second, equally load-bearing pitfall was also confirmed live: with LC-based loss, `Processor`'s automatic `min_detected_photons_filter` heuristic still thinks the source is "perfect" (it only inspects `NoiseModel`, not circuit components) and silently defaults to a filter that excludes every lossy (fewer-photon) output branch — you must call `proc.min_detected_photons_filter(0)` explicitly.

On the literature side, arXiv:2510.24137 is **not** an Aaronson-Brod paper — it is Park & Oh (KAIST, 2026), "Matrix product state approach to lossy boson sampling and noisy IQP sampling." This is a factual correction to this project's own `18-CONTEXT.md`. The real Aaronson-Brod paper ("BosonSampling with Lost Photons," 2016) is a different arXiv ID (1510.05245) that has not yet been read. Park & Oh's paper has *two* structurally different threshold results, and the one that actually matches this project's noise channel (photon transmittance through passive linear optics) is not the one badged "IQP" in the paper — see Finding 3 below. Bremner-Montanaro-Shepherd's Theorem 4 was verified against the primary source directly (page 4 of arXiv:1610.01808v4) and matches `docs/iqp-baseline.md`'s existing paraphrase.

**Primary recommendation:** Implement HARD-01/HARD-07 via `LC`-component insertion (not `NoiseModel`), always pair it with an explicit `proc.min_detected_photons_filter(0)`, and reframe HARD-02's cross-check as "does `NoiseModel`'s source-level Bernoulli-loss formula agree with `LC`'s beamsplitter-expansion formula on a simplified (non-polarization) circuit" rather than "run the same polarization pipeline two ways" (only one way actually works end-to-end for this project's circuits).

## Standard Stack

No new libraries needed — everything is already-installed `perceval-quandela==1.2.4` (this repo's venv). No MerLin/`QuantumLayer` path is usable here (already established in STATE.md: polarization-annotated circuits are categorically rejected by `QuantumLayer`).

### Core (already installed)
| Component | Module | Purpose | Why |
|---|---|---|---|
| `pcvl.LC(loss)` | `perceval.components.non_unitary_components` | Explicit per-mode loss channel, insertable at any point via `Processor.add()` | The *only* mechanism confirmed to actually apply loss to this project's polarization circuits |
| `pcvl.Processor.probs()` | `perceval.runtime.processor` | Strong (exact) simulation returning `{"results": BSDistribution, "global_perf": float}` | HARD-01's mandated non-`Analyzer` API; auto-detects `LC` and wraps `LossSimulator` around `PolarizationSimulator` correctly |
| `pcvl.NoiseModel(transmittance=η)` | `perceval.utils.noise_model` | Source-side per-photon loss model | Works correctly for **non**-polarization-annotated inputs (verified); use it as the independent HARD-02 cross-check reference on a stripped-down circuit, not as the sweep's actual loss mechanism |
| `perceval.simulators.LossSimulator` | `perceval.simulators.loss_simulator` | Wraps a base simulator, expands each `LC` into a real ancilla-beamsplitter (`BS.H(BS.r_to_theta(1-loss))`), traces out the loss mode | This is what `Processor.probs()` auto-invokes when it sees `LC` components — confirmed via `SimulatorFactory.build` source |

### Alternatives considered
| Instead of | Could use | Verdict |
|---|---|---|
| `LC`-component insertion | `Processor(..., noise=NoiseModel(transmittance=η))` | **Confirmed broken** for this project's polarization inputs (silent no-op) — do not use as the sweep mechanism |
| Manual `Source.generate_distribution` + `with_input(svd)` workaround | building a noisy `SVDistribution` by hand and feeding it via the "bypass the source" `with_input(SVDistribution)` overload | `Source.generate_distribution` requires a plain `FockState`, not `AnnotatedFockState` — raises `TypeError` for polarization input; not viable without hand-rolling the polarization mixture yourself (more work than `LC`, no upside) |

No install step needed — nothing new to add to `requirements.txt`/venv.

## Architecture Patterns

### Recommended wiring into the existing weight-1/weight-2 functions

**Weight-1** (`build_full_circuit`, `all_h_input`): insert `LC(loss)` on every one of the `2n` modes *before* `build_state_prep_circuit`, inside a `Processor`, mirroring how the existing functions already build `Circuit`s and hand them to a `Processor`:

```python
# Verified live against this repo's iqp_photonic_encoding.py, perceval-quandela==1.2.4
total_modes = 2 * n
proc = pcvl.Processor("SLOS", total_modes)
for m in range(total_modes):
    proc.add(m, pcvl.LC(loss))                 # loss = 1 - eta, applied uniformly
proc.add(0, enc.build_full_circuit(n, thetas))
proc.min_detected_photons_filter(0)             # MUST be explicit -- see Pitfall 2 below
proc.with_input(enc.all_h_input(n))
res = proc.probs()                              # {"results": BSDistribution, "global_perf": float}
```

Empirically confirmed at `n=1, theta=0`: `loss=0.0` → `|0,1⟩: 1.0` (matches the no-loss baseline exactly); `loss=1.0` → `|0,0⟩: 1.0` (total loss). Placing `LC` at the very front (before any gate) rather than distributed throughout the circuit is *not* a simplification with hidden risk — it is exactly equivalent, because uniform per-mode loss commutes with any passive linear-optical unitary (state prep, diagonal layer, conjugation, and PBS-based readout are all passive/photon-number-preserving), a fact this project doesn't need to take on faith: it is stated explicitly in Park & Oh's paper (arXiv:2510.24137, Sec. II.B: *"loss channels commute with passive linear-optical elements and can be moved to the input of the ideal interferometer"*).

**Weight-2** (`build_weight2_processor`/`_build_weight2_processor_no_herald`, `heralded_cz`-based): the *same* front-loaded `LC` insertion, but on all `2n + 2` modes (data qubits **and** the 2 herald ancilla modes), before `build_state_prep_circuit`. This directly satisfies HARD-07's locked decision ("loss applied uniformly across all modes including ancilla... run the full pipeline so herald failure and transmission loss interact physically, not an analytical multiplication"), for the same commutation reason: the herald ancilla photons sit untouched (identity evolution) through state prep and the diagonal layer (those sub-circuits are built on the first `2n` modes only) until reaching `build_cz_insertion`'s own local sub-circuit — so applying loss to them "at the front" is physically identical to applying it "right before they enter the CZ gate," since nothing happens in between either way.

Verified live end-to-end (`n=2, i=0, j=1`) using `_build_weight2_processor_no_herald`'s exact wiring (no `add_herald`, matching the confirmed-crash workaround already in this codebase — see Pitfall 3 below) with `LC` prepended on all 6 modes: `loss=0.0` reproduces `global_perf=1.0` as expected; `loss=0.3` runs cleanly and returns a `BSDistribution` you then classify by hand into `herald_failure_prob`/`residual`/`dist`, using the *exact same loop structure* `photonic_weight2_iqp_distribution` already uses (ancilla-mode check → `fock_to_bitstring`/`_decode_single_qubit_pair` → bucket). **No new decode logic is needed for HARD-07 — the existing residual-bucketing convention already generalizes correctly to loss**, because `fock_to_bitstring`/`_decode_single_qubit_pair` already return `None` (→ residual) for a `(0,0)` pair, which is exactly what a lost photon produces. The only required change is: (a) swap `Analyzer` for `Processor.probs()` + prepended `LC`, and (b) read `res["results"].items()` instead of `zip(analyzer.output_states_list, analyzer.distribution[0])`.

For CP(α)-based weight-2 (`_build_weight2_cp_processor_no_postselect`), the same pattern applies, with `LC` on all `2n + 4` modes (4 ancilla modes, per that function's own established layout).

### Anti-patterns to avoid
- **Using `noise=NoiseModel(transmittance=η)` on any `Processor` whose input will be `with_input()`-ed with a polarization-annotated `BasicState`.** Confirmed silently produces the lossless result. Do not "fix" this by trying harder to feed noise through the `Source`/`NoiseModel` constructor path — `Source.generate_distribution` fundamentally does not accept `AnnotatedFockState`.
- **Relying on `Processor`'s automatic `min_detected_photons_filter` when using `LC`.** `check_min_detected_photons_filter()` only inspects `self._source.is_perfect()`, which is derived purely from the `NoiseModel` — it has no knowledge of `LC` components in the circuit, so it will auto-set the filter as if the run were lossless (see Pitfall 2).
- **Computing weight-2's TVD/herald-rate from `global_perf` alone.** `global_perf = physical_perf * logical_perf` conflates photon-loss-caused failure with herald/postselection failure into one scalar (confirmed from `simulator_interface.py`'s `format_results`). HARD-07 needs these tracked *separately* (herald-success-rate vs. η, and TVD conditioned on herald success) — use the existing manual per-state classification loop, not `global_perf`.

## Don't Hand-Roll

| Problem | Don't build | Use instead | Why |
|---|---|---|---|
| Applying photon transmittance loss to a linear-optical circuit | A custom per-mode amplitude-damping matrix multiplication | `pcvl.LC(loss)` + `Processor.probs()`'s auto-`LossSimulator` wrapping | Already correctly composes with `PolarizationSimulator` (confirmed from `SimulatorFactory.build` source); reinventing this risks subtly wrong normalization/vacuum-mode bookkeeping |
| Computing Σp_x² (BMS's anticoncentration parameter α) | A sampling-based Monte Carlo estimate | Direct summation over the already-materialized `res["results"]` dict (or the existing lossless `dist` dict) | This project's n range (≤6-8) makes the *exact* distribution cheap to enumerate (confirmed: weight-1 n=4 with full loss enumeration returns in 0.07s); CONTEXT.md already locks "computed directly/exactly, not sampled" |

**Key insight:** this project's own residual/herald-failure-bucketing convention (established in Phases 9-15) is *already* the right shape for handling loss — the risk in this phase is not "need new accounting logic," it's "silently using an API path that discards or ignores the very probability mass HARD-05/07 need to measure."

## Common Pitfalls

### Pitfall 1: `NoiseModel(transmittance=η)` silently no-ops for polarization-annotated input (CONFIRMED, HIGH severity)
**What goes wrong:** `Processor("SLOS", circuit, noise=NoiseModel(transmittance=η)).with_input(polarization_annotated_state).probs()` returns the exact lossless result, for any η.
**Why it happens:** Traced through source: `Experiment.with_input`'s `AnnotatedFockState` dispatch (`experiment.py:870-876`) sets `self._input_state = input_state` directly and fires `_input_changed()`, which invokes `Processor._input_changed_observer` (`abstract_processor.py:65-73`, wired via `add_observers`). For any `AnnotatedFockState`, that observer sets `self._inputs_map = SVDistribution(StateVector(self.input_state))` — a noise-free delta distribution — *unconditionally*. `Processor.probs()` then checks `_has_custom_input` (True for polarization, since `has_polarization` is checked explicitly) and uses `self.source_distribution`, whose property getter only calls `_generate_noisy_input()` (the function that actually applies `Source.generate_distribution`, i.e. the noise) `if self._inputs_map is None` — but it's never `None` after `with_input()` ran. The noise model is constructed (`self._source = Source.from_noise_model(noise)`) but never consulted for this input type.
**How to avoid:** Use `LC`-component insertion (see Architecture Patterns above) instead of the `noise=` constructor parameter, for any circuit this project's weight-1/weight-2 functions build.
**Warning signs:** A loss sweep whose TVD-vs-η curve is flat/zero everywhere, or whose weight-2 herald-success-rate never moves off `2/27` regardless of η — both would be the direct symptom of this bug.
**Verification performed:** Live execution against `iqp_photonic_encoding.build_full_circuit(n=1, thetas=[0.0])` — `NoiseModel(transmittance=0.5)` and no-noise both produced `{|0,1⟩: 1.0}` bit-for-bit. Confidence: HIGH (source trace + empirical reproduction, both independently pointing to the same mechanism).

### Pitfall 2: `LC`-based loss requires an explicit `min_detected_photons_filter` (CONFIRMED, HIGH severity)
**What goes wrong:** Without calling `proc.min_detected_photons_filter(...)` yourself, `Processor.probs()` on an `LC`-loss circuit returns a `results` dict that looks like a valid, normalized-to-1 probability distribution — but it's silently conditioned on "no loss occurred," discarding all the lossy branches you're trying to measure.
**Why it happens:** `check_min_detected_photons_filter()` (`abstract_processor.py:334-342`) only checks `self._source.is_perfect()`. `self._source` is built purely from the `NoiseModel` (`Source.from_noise_model`), which knows nothing about `LC` components sitting in the circuit. Since no `NoiseModel` is set in the `LC`-based approach, `is_perfect()` is `True`, so the filter auto-sets to `input_state.n - sum(heralds)` — the *full lossless photon count* — which then filters out every branch with fewer detected photons.
**How to avoid:** Always call `proc.min_detected_photons_filter(0)` explicitly immediately after constructing any `LC`-loss `Processor`, before `.probs()`.
**Warning signs:** `results` dict sums to ~1.0 and contains only full-photon-count states even at high loss; the *true* survival probability is still recoverable from `res["global_perf"]` (confirmed in testing: `global_perf=0.5` was correctly reported even though `results` silently showed only the lossless branch) — so a sweep that only checks `sum(results.values()) ≈ 1` as a sanity check would NOT catch this bug. Check `global_perf` / the presence of reduced-photon-count states in `results` instead.
**Verification performed:** Live execution, `n=1, loss=0.5`, no manual filter call: `is_perfect()` reported `True`, `results = {|0,1⟩: 1.0}`, `global_perf = 0.5`. Confidence: HIGH.

### Pitfall 3 (inherited from STATE.md/12-RESEARCH.md, re-confirm applies here): `add_herald` + PBS crashes `Processor.probs()`
Already documented in this project's STATE.md: `Processor.add_herald()` on a PBS-containing circuit crashes `.probs()` unless every herald mode is also explicitly supplied in `with_input()`. This project's existing workaround (`_build_weight2_processor_no_herald`: skip `add_herald`, manually classify ancilla-mode outcomes) is exactly the pattern to keep using for the loss sweep — do not attempt to register real heralds on the `LC`-loss weight-2 processor.

### Pitfall 4: `global_perf`'s single-scalar shape conflates loss and herald/postselection failure
Already covered under Anti-Patterns above — restated here because it's easy to reach for `global_perf` as "the one number I need" for HARD-07's herald-success-rate-vs-η tracking, when it's actually the *product* of loss-driven and herald-driven attrition. Confirmed from `perceval/simulators/simulator_interface.py:134`: `result = {'results': results, 'global_perf': physical_perf * logical_perf}`. (Note: this project's installed `perceval-quandela==1.2.4` returns `global_perf` as a single combined key — not the separate `physical_perf`/`logical_perf` keys some `Simulator.probs_svd` docstrings describe; that docstring describes the base `Simulator` class's return before `ASimulatorDecorator.format_results` recombines them. Don't assume separate keys exist without checking this version's actual returned dict.)

### Pitfall 5 (paper-level, not code-level): the two literature papers' noise channels are NOT the same, and Park & Oh's own paper contains two DIFFERENT threshold results, only one of which matches this project's noise channel
See Finding 3 below — flagging here because it's the kind of thing easy to grab the wrong number from if only skimming for "a formula with η in it."

## Code Examples

### Weight-1 loss sweep skeleton (verified pattern)
```python
# Source: this repo's iqp_photonic_encoding.py + perceval-quandela==1.2.4,
# verified live during this research pass.
import perceval as pcvl
import iqp_photonic_encoding as enc

def photonic_iqp_distribution_lossy(n, thetas, eta):
    loss = 1.0 - eta
    total_modes = 2 * n
    proc = pcvl.Processor("SLOS", total_modes)
    for m in range(total_modes):
        proc.add(m, pcvl.LC(loss))
    proc.add(0, enc.build_full_circuit(n, thetas))
    proc.min_detected_photons_filter(0)
    proc.with_input(enc.all_h_input(n))
    res = proc.probs()

    dist, residual = {}, 0.0
    for state, p in res["results"].items():
        bits = enc.fock_to_bitstring(state, n)
        if bits is None:
            residual += p
        else:
            dist[bits] = dist.get(bits, 0.0) + p
    return dist, residual, res["global_perf"]
```

### HARD-02 cross-check design (NoiseModel vs. LC, on a shared simplified case)
```python
# Both mechanisms verified independently to give matching survival statistics
# at eta=0.5 on a bare non-polarization 2-mode identity circuit.
noise_via_model = pcvl.Processor("SLOS", pcvl.Circuit(2), noise=pcvl.NoiseModel(transmittance=0.5))
noise_via_model.min_detected_photons_filter(0)
noise_via_model.with_input(pcvl.BasicState("|1,0>"))
res_a = noise_via_model.probs()   # {|0,0>: 0.5, |1,0>: 0.5}

noise_via_lc = pcvl.Processor("SLOS", 2)
noise_via_lc.add(0, pcvl.LC(0.5))
noise_via_lc.min_detected_photons_filter(0)
noise_via_lc.with_input(pcvl.BasicState("|1,0>"))
res_b = noise_via_lc.probs()      # matches res_a's survival split
```
This is the recommended shape for HARD-02: it cannot be run on the *real* polarization pipeline (only `LC` works there, per Pitfall 1), so the honest cross-check is "these two independently-implemented Perceval loss mechanisms agree on a case where both are applicable" — not "the same full pipeline computed two ways."

## Literature Findings

### Finding 1: arXiv:2510.24137 authorship correction (HIGH confidence — full read performed)

**This is Sojeong Park and Changhun Oh, "Matrix product state approach to lossy boson sampling and noisy IQP sampling" (KAIST, submitted 2026), not an Aaronson-Brod paper.** `18-CONTEXT.md` states *"Aaronson-Brod (arXiv:2510.24137, read in full first, per HARD-03)"* — this attribution is wrong and should be corrected before it propagates further into `docs/iqp-baseline.md` or a write-up. The actual Aaronson-Brod paper is **"BosonSampling with Lost Photons," Phys. Rev. A 93, 012335 (2016), arXiv:1510.05245** — a different paper, not yet read in this project, that proves hardness is preserved when a *constant number* `k` of photons are lost (not a fractional/rate-based loss model). HARD-04's text ("Aaronson-Brod's fixed-loss-count regime") is describing *that* paper's actual content correctly — it's specifically the CONTEXT.md line conflating the two that's wrong. **Open item for the owner/planner: HARD-04 as literally written requires comparing against the genuine Aaronson-Brod paper (1510.05245), which has not yet been read — flag this explicitly rather than silently substituting Park & Oh's paper for it.**

### Finding 2: Park & Oh's paper has two distinct threshold results — pick the right one (HIGH confidence)

The paper does two separate things, using different noise models:

1. **Lossy boson sampling / single-photon Fock inputs (Sec. IV, Theorem 1 — this is the one that physically matches this project's noise channel).** Setup: `N` single photons through an `M`-mode passive linear-optical interferometer, with uniform photon transmittance `η` (loss channel `LC` semantics, commuted to the input — exactly this project's own architecture, see Architecture Patterns above). Result (Theorem 1, their Eq. 25-26): the sampled output branch's Rényi entanglement entropy is `S_α(ρ_A) = O(N η^{2α})`, giving an efficiently-MPS-approximable (→ classically simulable to fixed accuracy) regime whenever `η = O((log N / N)^{1/(2α)})` — up to log factors, this is the well-known **η = Θ(1/√N)** transmission-rate threshold. This is an *upper bound on where classical simulation via this specific MPS method is efficient* — it is **not** a complexity-theoretic hardness lower bound above that threshold (the paper is explicit about this asymmetry — MPS-inapproximability doesn't imply hardness, only that this particular algorithm doesn't give an efficient answer). N here is photon count; for this project's weight-1 encoding, N = n (one photon per qubit).

2. **IQP sampling with qubit-level Pauli noise (Sec. V — this is the one badged "IQP" in the paper, but it does NOT match this project's photon-loss channel).** Setup: an `n`-qubit IQP circuit (standard `H^⊗n D H^⊗n`), with independent **dephasing** or **depolarizing** noise applied per-gate-layer to each qubit (a completely different, qubit-level noise channel — the same general family as Bremner-Montanaro-Shepherd's Theorem 4, not photon transmittance). Result (Eq. 59/63): efficient MPS simulability whenever circuit depth `d = Ω(log(n) / |log(1-2p)|)` for per-layer noise rate `p` — a **depth-vs-noise-rate** threshold, explicitly stated as "consistent with" a prior independent result (Rajakumar, Watson & Liu, SODA 2025, arXiv:2411.02585, and a percolation-based threshold in Nelson, Rajakumar, Hangleiter & Gullans, arXiv:2405.13767 — both cited in the paper as refs [40]/[43]).

**Recommendation for HARD-03/HARD-04:** cite **Theorem 1** (Finding 2.1 above) as the primary comparison point, since it is the one whose physical setup (photon transmittance through passive linear optics) actually matches this project's circuit — not Section V's threshold, despite Section V literally being titled "Noisy IQP Sampling." State this distinction explicitly in the write-up; citing Section V's formula as "the paper's IQP threshold" without this caveat would be citing the wrong noise channel for this project's own claim.

### Finding 3: BMS Theorem 4 — verified exact statement (HIGH confidence, page 4 of arXiv:1610.01808v4)

> **Theorem 4.** Consider a unitary circuit `C = H^⊗n D H^⊗n` whose diagonal part `D` is defined by `⟨x|D|x⟩ = f(x)` for some `f: {0,1}^n → ℂ` such that `f(x)` can be computed in time `poly(n)` for any `x`. Let the probability of receiving output `x` after applying `C` to input `|0⟩^⊗n` be `p_x`, and assume that `Σ_x p_x² ≤ α2^{-n}` for some `α`. Further assume `C` experiences independent depolarising noise on each qubit with rate `ε`. Then `T` samples can be generated from a distribution which approximates the noisy output probability distribution up to `δ` in ℓ1 norm, in time `n^{O(log(α/δ)/ε)} + T·poly(n)`.

Matches `docs/iqp-baseline.md`'s existing paraphrase — no correction needed there. Two nuances worth stating precisely for HARD-04, since they affect how "positioning against this regime" should be phrased:
- **There is no single numeric threshold ε\*.** The runtime is `n^{O(log(α/δ)/ε)}` — for *any fixed constant* `ε > 0` (however small) with `α = O(1)`, the exponent is a constant independent of `n`, giving polynomial-time simulation. The paper's own framing (abstract, Sec. 1.1) is "*an arbitrarily small constant amount of noise* destroys hardness for anticoncentrated circuits" — not "noise above rate X destroys hardness." Don't manufacture a crossover number that isn't in the theorem.
- **This project's achievable n (≤6-8) makes the asymptotic character of this statement fundamentally undemonstrable at this project's scale** — the same honesty caveat already applied elsewhere in this project's trainability write-ups (`docs/trainability-study.md`) to n-scaling claims. State this plainly in HARD-06's scope statement rather than implying the sweep "confirms" or "refutes" Theorem 4's asymptotic regime.
- **The depolarizing channel's operational definition is directly useful for HARD-04's translation.** `D_ε(ρ) = (1-ε)ρ + ε·I/2` — "with probability `1-ε`, keep the state; with probability `ε`, discard it and replace with the maximally mixed state" (verified, page 3 of the PDF). Note the structural resemblance to an *erasure*: a lost photon (this project's actual failure mode) is also "discard the qubit's information" — the difference is that depolarizing *replaces* with a random guess (measurable, contributes a real but randomized bit), while this project's photon loss currently gets bucketed into `residual`/`herald_failure_prob` and *excluded* from `dist` entirely. This gap (erasure vs. depolarizing-as-relabeled-erasure) is exactly the kind of thing the owner's attempt-first sketch should reckon with — see next section.

### Finding 4: Anticoncentration parameter α(η) — computation is straightforward, not novel
`Σ_x p_x²` (BMS's α, un-normalized by `2^{-n}`) is directly computable from the same `dist` dict this project's existing functions already produce — `sum(p**2 for p in dist.values())`, then divide by `2**-n` to report α per BMS's own normalization. No new machinery needed; CONTEXT.md already confirms this project's n range makes exact (non-sampled) computation feasible, and the compute-cost section below confirms the underlying `.probs()` calls stay cheap through at least n=4-5.

## Guidance for the HARD-04 Attempt-First Checkpoint (not a worked derivation — per this project's CLAUDE.md, that's the owner's job)

Three genuinely different, physically-motivated candidate directions exist for mapping this project's photon-loss/herald-failure mechanics onto BMS's single-qubit depolarizing rate `ε`. Presenting the *shape* of each option (not picking one) so the owner has real material to sketch against:

1. **Erasure-as-depolarizing.** Since `D_ε` operationally means "replace with maximally mixed state with probability ε" and this project's lost photon *already* is "no information" for that qubit — the simplest candidate is `ε ≈` (per-qubit probability the qubit's readout is invalid/lost), i.e. directly related to `1-η` for weight-1. The open question the owner needs to resolve: BMS's depolarizing channel still *produces a bit* (a uniformly random guess) that gets fed into the rest of the (otherwise noiseless) sampling process, whereas this project's convention currently *discards* that outcome into `residual`. Is `ε = 1-η` a fair translation, or does the discard-vs-guess distinction need to be reconciled first (e.g., by asking "what if a lost photon were reported as a uniformly random bit instead of discarded")?
2. **Compounded gate-failure rate.** For weight-2, `heralded_cz`'s own lossless success probability is `2/27`; `CP(α)`'s success probability varies with `α` (`docs/iqp-photonic-encoding.md`'s ARB-02 closed form). A candidate direction: derive `ε` not from raw transmittance alone but from how much the *herald-conditioned* output distribution deviates from the lossless herald-conditioned distribution as η varies — i.e., an effective ε that's a function of both η and the gate's own success-probability sensitivity to η (which Task work in this phase will measure directly per HARD-07).
3. **Fitted effective channel.** The most rigorous (and heaviest) option: compute the actual single-qubit reduced channel induced by tracing out everything except one qubit's own mode-pair, for the real lossy circuit, and find the depolarizing rate ε whose `D_ε` is closest (in diamond-norm or simpler trace-distance terms) to that real induced channel. This is the only option of the three that would produce a defensible "this ε is what the real physics does to a single qubit," rather than an analogy — but is materially more work and may be out of scope for this phase's time budget.

Direction 1 is the cheapest to sketch and the most directly grounded in machinery this project already has (`residual`, `herald_failure_prob`); it's the most natural starting point for the owner's own attempt, with the discard-vs-guess question flagged as the one thing that needs an explicit, stated assumption either way.

## Compute Cost: Empirically-Grounded Sizing

All timings below are from live runs against this repo's venv (`perceval-quandela==1.2.4`) on this machine, during this research pass — not estimates.

### Weight-1, `LC`-loss + `min_detected_photons_filter(0)`
| n | output states (loss=0.3) | wall time |
|---|---|---|
| 2 | 9 | 0.03s |
| 3 | 27 | 0.02s |
| 4 | 81 | 0.07s |

Output-state count grows as `3^n` (each qubit independently: survives as H, survives as V, or lost) — **much cheaper than the naive worst-case combinatorial estimate** of enumerating every Fock state across all photon counts (which would be `Σ_{k=0}^{n} C(2n+k-1,k)`, far larger). Perceval's SLOS backend appears to prune physically-unreachable branches even at `min_detected_photons_filter=0`, for this circuit topology (single photon per qubit-pair, no bunching source). This is good news: weight-1 loss sweeps at n up to Phase 17's established n=6 CORE ceiling (and likely beyond) should stay tractable on this basis alone — but this has only been verified through n=4; recommend a quick timing check at n=5/6 before committing to a max-n target in the plan.

### Weight-2 (`heralded_cz`), `LC`-loss on all `2n+2` modes + `min_detected_photons_filter(0)`
| n | output states (loss=0.3) | wall time |
|---|---|---|
| 2 | 204 | 0.04s |
| 3 | 612 | 0.62s |
| 4 | 1836 | **16.8s** |

State count grows ~3× per additional bystander qubit (consistent with weight-1's per-qubit branching, layered on the CZ-insertion's own ~204-state base), but **wall time grows much faster than state count** (~15× then ~27× per step) — the per-call cost of strong-simulating the larger mode count (2n+2 modes, more photons in flight through the CZ insertion's internal beamsplitters) dominates, not enumeration size. Extrapolating (not measured): n=5 plausibly several minutes, n=6 plausibly tens of minutes to hours or a `MemoryError`, in the same ballpark as Phase 17's own established mixed-scope n=5 CORE ceiling (which used a cheaper, fixed-photon-count-only `Analyzer` enumeration, no loss) — **loss sweeps on top of an already-expensive weight-2 circuit should be expected to be at or somewhat below Phase 17's n=5 mixed ceiling, not above it.**

### Sizing implication for the plan
This is a **single (n, η, scope) cell's cost** — the full phase multiplies this by ~6-8 η-grid points × 2 scopes (weight-1, mixed) × 2 baselines (but the baselines — uniform, product-of-marginals — are cheap classical computations, not additional Perceval calls, since product-of-marginals' per-qubit marginals are computed once from the η=1 reference per CONTEXT.md's locked decision). Rough total-cost shape: weight-1's full η-grid at a given n costs roughly `8 × (single-cell time)`; at n=4 that's ~0.5s, trivial. Mixed's full η-grid at n=4 costs roughly `8 × 16.8s ≈ 2-3 min`; at n=5 (unverified, extrapolated) plausibly 30-70 min for the whole grid at that one n. **Recommend the plan size mixed-scope max-n conservatively (n=4 CORE, n=5 as a best-effort/chunked stretch, mirroring Phase 17.1's "no fixed time-box, chunked/resumable" pattern) rather than assuming Phase 17's exact n=5/n=6 ceilings transfer unchanged** — loss changes both the enumeration shape and the per-call cost profile enough that the old ceiling is a starting guess, not a guarantee. A quick empirical timing check at n=5 (both scopes) before locking the plan's max-n target is cheap insurance (a handful of single-cell calls, not a full sweep).

## Open Questions

1. **Does HARD-04 need the genuine Aaronson-Brod paper (arXiv:1510.05245) read, given arXiv:2510.24137 turned out to be a different paper (Park & Oh)?**
   - What we know: HARD-04's text describes "Aaronson-Brod's fixed-loss-count regime" accurately as a description of the real 2016 paper's actual result (constant-count loss, not fractional rate) — that paper itself has not been read in this project.
   - What's unclear: whether HARD-04 as originally scoped intended a *third* paper read (the real Aaronson-Brod), or whether the CONTEXT.md misattribution means the phase's actual intent was always "compare against Park & Oh's Theorem 1" and the "Aaronson-Brod" name was simply attached to the wrong paper throughout.
   - Recommendation: surface this explicitly to the owner before planning fixes a scope; a full read of arXiv:1510.05245 is comparatively cheap (a focused, shorter, older paper) if the owner wants HARD-04 to genuinely cover both regimes as separate literature reads.

2. **Weight-1 n=5/6 and weight-2 n=5 loss-sweep timing is extrapolated past n=4, not measured.**
   - What we know: n≤4 for both scopes is fast (sub-20s per cell).
   - What's unclear: whether the ~27×-per-step wall-time growth trend (weight-2) continues, worsens, or plateaus at n=5/6.
   - Recommendation: run a handful of single-cell timing probes at the plan's proposed max-n before committing compute budget to the full sweep, per this project's Phase 17-established practice of checking before committing.

3. **The "erasure vs. randomized-guess" gap in Direction 1 of the HARD-04 sketch (Finding 3) is unresolved by design** — flagged for the owner's attempt-first checkpoint, not resolved here per this project's CLAUDE.md.

## Sources

### Primary (HIGH confidence)
- Direct source read: `venv/Lib/site-packages/perceval/{runtime/processor.py, runtime/abstract_processor.py, components/experiment.py, components/source.py, components/non_unitary_components.py, simulators/{loss_simulator.py, simulator_factory.py, simulator.py, simulator_interface.py}, utils/noise_model.py}` (perceval-quandela==1.2.4, this repo's venv)
- Live empirical execution against `iqp_photonic_encoding.py` and toy circuits, this repo's venv, this research session (all scripts run via `./venv/Scripts/python.exe`)
- `docs/papers/1610.01808v4.pdf` (Bremner, Montanaro & Shepherd, "Achieving quantum supremacy with sparse and noisy commuting quantum computations," Quantum 1, 8 (2017)) — pages 1-6 read directly, Theorem 4 quoted verbatim
- arXiv:2510.24137 PDF (Park & Oh, "Matrix product state approach to lossy boson sampling and noisy IQP sampling") — full paper read (14 pages + appendix start), fetched directly from arxiv.org/pdf/2510.24137 during this session

### Secondary (MEDIUM confidence)
- WebSearch confirming arXiv:1510.05245 is the genuine Aaronson-Brod paper ("BosonSampling with Lost Photons," Phys. Rev. A 93, 012335 (2016)) — corroborated by Semantic Scholar and arXiv abstract-page metadata, but the paper's own text was not read in this session (Open Question 1)

### Tertiary (LOW confidence)
- None — every load-bearing claim above was either source-traced, empirically verified, or read from the primary paper text directly.

## Metadata

**Confidence breakdown:**
- Perceval API mechanics (Findings under Architecture Patterns/Pitfalls 1-4): HIGH — verified by both source trace and live execution, not assumption
- Literature findings (Findings 1-4): HIGH for what the papers say; MEDIUM for how cleanly it maps onto this project's own encoding (that mapping work is HARD-04's job, not fully resolved here)
- HARD-04 depolarizing-translation guidance: MEDIUM — genuinely open by design, three candidate directions sketched, none picked
- Compute-cost sizing: MEDIUM-HIGH — real measurements through n=4, extrapolated (not measured) beyond that

**Research date:** 2026-08-14
**Valid until:** ~30 days (Perceval API facts are version-pinned to `perceval-quandela==1.2.4` and won't drift on their own; literature findings are permanent; compute-cost numbers are machine-specific and should be re-checked if the sweep runs on different hardware)
