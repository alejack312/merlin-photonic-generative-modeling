# Project Research Summary

**Project:** MerLin Quantum Case Study — v2.1 milestone (weight-2 IQP generator via heralded CZ)
**Domain:** Photonic quantum computing implementation — extending an existing, tested weight-1 IQP-photonic encoding (`iqp_photonic_encoding.py`) with a two-qubit `Z_i·Z_j` generator built on Perceval's `heralded_cz` catalog gate
**Researched:** 2026-08-05
**Confidence:** HIGH

## Executive Summary

This milestone is narrow and well-bounded: implement and validate the weight-2 (`exp(iπ/4·Z_i·Z_j)`) IQP generator already derived on paper in `docs/iqp-photonic-encoding.md`, using Perceval's shipped `core_catalog.heralded_cz` Knill-CZ gate — no new library, no new gate design. All four research files converge on the same picture: the hard part is not physics derivation (already done) but getting the Perceval **API surface** right, because `heralded_cz` breaks the pure-`Circuit` composition pattern the existing weight-1 code relies on. `heralded_cz` is a probabilistic, ancilla-heralded gate that only exists correctly as a `Processor`/`Experiment` object (via `build_experiment()`), never as a bare `Circuit` (`build_circuit()` silently drops the herald). This forces a second, parallel top-level pipeline (`Processor`-composed) alongside the existing weight-1 `Circuit`-only pipeline, while every existing weight-1 builder function is reused unmodified as an input to `Processor.add()`.

The recommended approach: (1) de-risk the primitive standalone first (confirm `heralded_cz`'s measured herald-success probability — verified live in this repo's venv at exactly 2/27 ≈ 0.074074, uniform across all four computational-basis inputs, independently reproducing the literature figure rather than citing it); (2) build a small `PBS → heralded_cz → PBS` insertion unit reusing the existing polarization/dual-rail conversion the readout stage already does; (3) compose it into a new `Processor`-based pipeline via `Processor.add()`, leaving all weight-1 functions untouched; (4) extend the exact qubit-side reference distribution to include `Z_i·Z_j` phase terms; (5) validate via TVD, conditioned on herald success, following the exact ENC-04 pattern already established for weight-1.

The key risk is not "does the gate work" (already confirmed) but **silent API misuse that produces plausible-looking but physically wrong numbers**: using `build_circuit()` instead of `build_experiment()` (drops the herald entirely, runs the raw unlabeled unitary), reading only the conditional output distribution while never capturing the separate herald-success-probability field (`.performance`/`global_perf`), or conflating heralding with post-selection (`logical_perf` actually bundles the herald condition with a data-output-validity filter). Every one of these failure modes produces code that runs without error and returns a normalized distribution — nothing crashes, so nothing self-reports the bug. The project's own established discipline (explicit residual reporting, never silently renormalizing away failure mass — set precedent in the weight-1 ENC-03/ENC-04 work) is exactly what guards against this, and must be extended to a *second* failure channel (herald failure) that weight-1 never had.

## Key Findings

### Recommended Stack

No new dependencies. `perceval-quandela==1.2.4` (already installed) ships `perceval.components.core_catalog.HeraldedCzItem`, reachable via `pcvl.catalog['heralded cz']`, as a complete, verified Knill CZ implementation (arXiv:quant-ph/0110144). All claims below were verified by reading the installed package source directly and running it in this repo's venv — not recalled from training data or cited secondhand.

**Core technologies:**
- `perceval-quandela==1.2.4` (unchanged) — already the project's substrate; `heralded_cz` ships in this exact version, confirmed by direct source read.
- `pcvl.catalog['heralded cz']` (`HeraldedCzItem`) — the Knill CZ gate itself: 6-mode circuit (4 logical dual-rail modes + 2 herald ancilla modes), fixed-angle (no parameterization — `build_circuit(**kwargs)` ignores all kwargs).
- `Processor("SLOS", ...)` + `Processor.probs()` / `pcvl.algorithm.Analyzer` — runs the gate and returns both the herald-conditional output distribution (`results`/`distribution`, already renormalized) and the separate success probability (`global_perf`/`.performance`) in one call. This is the milestone's literal deliverable number.
- `Simulator.prob_amplitude()` — needed only if verifying the CZ's signature phase (`-1` on `|1,1⟩`), since `probs()` is phase-blind.

**What NOT to use:** `CatalogItem.build_processor()` (deprecated since 1.2.0 — use `build_experiment()` instead); hand-deriving the Knill CZ beamsplitter network from the paper (already correctly implemented, with a deliberate convention adjustment noted in source comments — reimplementing risks reintroducing a resolved sign bug); `PostProcessedCzItem` (a different gate family — post-selection, not the ancilla-heralded construction already committed to in the design doc); any attempt at a parameterized/arbitrary-θ variant (no such parameter exists in this catalog item).

### Expected Features

**Must have (table stakes) to call weight-2 "implemented and validated," mirroring the exact bar already set for weight-1 (ENC-04):**
- `build_weight2_generator_circuit` (name illustrative): PBS→dual-rail, `heralded_cz`, PBS-back, plus two `WP(π/4,0)` single-qubit phase corrections (the CZ/ZZ operator identity already derived on paper), wired via `Processor.add()` into the existing per-qubit mode layout.
- Extended exact qubit-side reference (`exact_qubit_iqp_distribution` + pair terms) that can express `Z_i·Z_j`.
- Herald-conditioned photonic distribution with herald-failure probability and out-of-subspace decode residual reported as two separate, explicit numbers — never merged, never silently discarded.
- TVD test at n=2, θ=π/4, comparing the extended exact reference against the herald-conditioned photonic output, same style/tolerance conventions as `test_enc04_toy_validation_runs_end_to_end`.
- Exact (analytic, not shot-sampled) herald-success probability, read directly off `Analyzer.performance`/`probs()['global_perf']` — Perceval computes this exactly and noiselessly, so Monte Carlo sampling is explicitly an anti-feature (redundant, slower, reintroduces ambiguity the project's exact-validation philosophy deliberately avoids).
- Matching test coverage added to `tests/test_iqp_photonic_encoding.py`.

**Should have (differentiators):** n=3 mixed weight-1+weight-2 generator test (validates composability in the same register); explicit side-by-side reporting of the two failure channels (herald failure vs. out-of-subspace residual); internal-consistency cross-check (conditioned distribution sum × success probability reconstructs raw non-out-of-subspace mass); informational comparison of the measured success probability against the literature figures already flagged as unverified in the design doc.

**Defer (explicitly out of scope this milestone):** arbitrary-θ weight-2 generator (no known decomposition — open research question); post-selected (non-heralded) CZ variant (owner already chose heralded over post-selected); weight-3+ generators (no paper derivation exists yet); loss/noise/hardware-realism modeling (weight-1's validation is explicitly idealized/lossless — parity, not a new realism dimension, is the goal).

### Architecture Approach

`heralded_cz` needs 2 extra internal ancilla modes beyond the 4 dual-rail modes it acts on, but `Processor` manages them automatically — they never enter or renumber the module's existing 2n-mode-per-qubit port convention (already dual-rail-shaped, since `build_readout_circuit`'s final `PBS()` is exactly a polarization→dual-rail conversion). The real fork: weight-1's pipeline is `Circuit`-only (a single unitary matrix, no heralding concept); any circuit containing a heralded gate cannot be represented as a plain `Circuit` at all — it must be a `Processor`, composed via `Processor.add()`. This forces a second, parallel top-level pipeline function for weight-2 (`build_full_circuit_weight2`/`run_full_circuit_weight2`) while every existing weight-1 builder (`build_state_prep_circuit`, `build_diagonal_layer_circuit`, `build_conjugation_circuit`, `build_readout_circuit`) is reused unmodified — all are valid `Processor.add()` inputs, and the CZ's single-qubit π/4 corrections fold cleanly into `build_diagonal_layer_circuit`'s existing `thetas` argument (additive phase, no new gate code needed).

**Major components (new):**
1. **`build_cz_insertion(n, i, j)`** — `Processor`-composable unit: PBS on qubit `i`, PBS on qubit `j` (convert to dual rail), `heralded_cz` experiment across those 4 modes, PBS back on both (return to polarization) — so the rest of the pipeline is unaffected.
2. **`build_full_circuit_weight2(n, thetas, cz_pairs)`** — new top-level `Processor`-composed pipeline: state prep → adjusted diagonal layer (thetas + π/4 corrections per CZ pair) → CZ insertions → conjugation → readout. Returns a `Processor`, not a `Circuit`.
3. **`run_full_circuit_weight2`** — runs via `Processor.probs()`, returning three things (not two, unlike weight-1): the conditional distribution, the herald success probability (`global_perf` — new, no weight-1 analogue), and the existing out-of-subspace residual (re-verified empirically for weight-2, not assumed zero).
4. **`exact_qubit_iqp_distribution_weight2`** (or additive parameter) — qubit-side reference including `Z_i·Z_j` terms, matching the fixed π/4 realization only.

Suggested build order (from ARCHITECTURE.md): de-risk the bare primitive standalone → build and test `build_cz_insertion` in isolation → compose the full weight-2 pipeline from unmodified weight-1 builders + the insertion unit → extend the qubit-side reference → run TVD validation → full regression of the existing 26-test suite after each step (should stay green throughout, since every new function is additive).

### Critical Pitfalls

Top pitfalls from the v2.1-dated PITFALLS.md addendum (heralded_cz-specific; supersedes the older v2.0 literature-scoping section for this milestone's purposes):

1. **Conflating success probability with the conditional output distribution (Pitfall 9)** — `Analyzer.distribution`/`Processor.probs()['results']` is already renormalized and sums to 1 regardless of herald success; the actual success number lives in a separate field (`.performance`/`global_perf`) that weight-1 code never needed to read (its `performance` was always 1.0). Any weight-2 helper copy-pasted from `run_full_circuit` will silently drop the milestone's actual deliverable number. **Avoid by:** treating success probability as a first-class, separately-captured return value from day one.
2. **Using `build_circuit()` instead of `build_experiment()`/`build_processor()` (Pitfall 13)** — the bare `Circuit` has no heralds attached at all; splicing it into a bigger `Circuit` the way `HWP`/`WP`/`PBS` are added today runs the raw, unheralded 6-mode unitary and produces a plausible-looking but physically wrong distribution (no crash, "success probability" reads as 1.0). **Avoid by:** using `build_experiment()`/`Processor.add()`, and verifying `processor.heralds` is non-empty immediately after assembly, before running anything downstream.
3. **Heralding vs. post-selection semantic drift (Pitfall 11)** — `logical_perf`/`global_perf` actually bundles the true herald condition (ancilla modes clicking) with a second, distinct filter (data-mode output falling outside the valid dual-rail subspace). For this project's ideal/lossless regime the second component is typically negligible, but that must be checked, not assumed. **Avoid by:** explicitly checking that malformed/bunched-data-output probability mass is ~0 for the inputs actually used before citing `logical_perf` as "the herald probability."
4. **Mode-index renumbering breaking the existing `2*k`/`2*k+1` layout convention (Pitfall 14)** — `Experiment.m` excludes herald modes from external numbering once heralds are added; weight-1's flat convention has no established, tested pattern for coexisting with herald-mode gaps. **Avoid by:** a small calibration script (mirroring the weight-1 H/V port-labeling check that already caught a real bug) that round-trips a known input through the embedded weight-2 block before trusting any output-parsing helper.
5. **Assuming input-independence of the measured success probability without checking the actual generator's input regime (Pitfall 12)** — literature/spot-checked values (2/27, uniform across computational-basis inputs) may not automatically generalize to the `|+⟩`-derived, potentially-entangling inputs this circuit's diagonal layer actually produces. **Avoid by:** measuring (not assuming) across the actual input regime, and stating explicitly which inputs were tested.

## Implications for Roadmap

Based on combined research, this milestone decomposes cleanly into a single implementation phase with clear internal sequencing (already largely specified by ARCHITECTURE.md's build order) rather than multiple roadmap-level phases — the scope is one well-bounded feature addition to an existing, tested module.

### Phase 1: De-risk the primitive standalone
**Rationale:** Isolates the highest-uncertainty piece (does `heralded_cz` really behave as the paper derivation assumed) before touching any existing code; directly resolves the "success probability unverified" flag already open in `docs/iqp-photonic-encoding.md`.
**Delivers:** A throwaway/small test confirming `heralded_cz`'s measured success probability (2/27, expected uniform across the 4 computational-basis inputs) and its CZ truth table, run via `build_experiment()` + `Processor.probs()`/`Analyzer`.
**Addresses:** FEATURES.md's "exact analytic herald-success probability" table-stakes item.
**Avoids:** Pitfall 13 (build_circuit vs build_experiment), Pitfall 9 (capturing `.performance` from the start).

### Phase 2: Build and test the CZ insertion unit in isolation
**Rationale:** Confirms the mid-circuit PBS round-trip claim (polarization → dual-rail → CZ → dual-rail → polarization) independent of the full pipeline, before composing anything larger.
**Delivers:** `build_cz_insertion(n, i, j)`, tested against a known computational-basis truth table at the module's existing `(2i,2i+1)`/`(2j,2j+1)` port convention.
**Uses:** `Processor.add()` composition pattern from STACK.md/ARCHITECTURE.md.
**Implements:** The `build_cz_insertion` architecture component.
**Avoids:** Pitfall 14 (mode-index renumbering) via an explicit calibration round-trip.

### Phase 3: Compose the full weight-2 pipeline
**Rationale:** All weight-1 builders are reusable unmodified once the insertion unit is proven — this is pure composition, not new circuit design.
**Delivers:** `build_full_circuit_weight2`/`run_full_circuit_weight2`, folding the π/4 single-qubit corrections into the existing `build_diagonal_layer_circuit` call via additive `thetas`.
**Uses:** Existing `build_state_prep_circuit`, `build_conjugation_circuit`, `build_readout_circuit` (all unmodified).
**Implements:** ARCHITECTURE.md's parallel Processor-based top-level pipeline.

### Phase 4: Extend the exact reference and validate
**Rationale:** This is the direct weight-2 analogue of ENC-04 — the project's own established validation bar, not a lower one.
**Delivers:** Extended `exact_qubit_iqp_distribution` (or sibling) with `Z_i·Z_j` pair terms; n=2 TVD test between the exact reference and the herald-conditioned photonic output; herald success probability and out-of-subspace residual reported as two explicit, separate numbers.
**Addresses:** FEATURES.md's full table-stakes list (TVD comparison, herald-conditioned distribution, explicit dual-residual reporting, matching test coverage).
**Avoids:** Pitfall 11 (heralding vs. post-selection drift), Pitfall 12 (input-independence assumption) — via explicit checks documented in the test/writeup, not silent assumptions.

### Phase Ordering Rationale

- Standalone primitive verification must come first (Phase 1) because it is both the cheapest de-risking step and directly answers the milestone's own core question (measure the success probability) — no reason to build downstream code before confirming the primitive behaves as the paper assumed.
- The insertion unit (Phase 2) must be proven before full-pipeline composition (Phase 3) because it is the one genuinely new API-shape departure (Circuit → Processor); isolating it avoids conflating a composition bug with a pipeline bug.
- Validation (Phase 4) must come last because it depends on both the extended exact reference and the working photonic pipeline existing simultaneously — per FEATURES.md's dependency graph, neither half alone is sufficient.
- This ordering directly avoids the older v2.0 pitfalls section's Pitfall 8 historical failure mode: design-then-implement, not implement-by-trial-and-error — each phase has an explicit correctness check before the next phase builds on it.

### Research Flags

Phases likely needing deeper research during planning: none identified as needing fresh research — all four research files (STACK, FEATURES, ARCHITECTURE, PITFALLS) were produced via direct source inspection and live execution against the actual installed package in this repo's venv, so the API surface, herald semantics, and measured numbers are already ground-truth-verified rather than assumed. If planning surfaces an unexpected need (e.g., a mode-count mismatch not covered by the calibration-script pattern), it will be narrowly scoped (specific API call), not a broad unknown.

Phases with standard patterns (skip research-phase): all four phases above — the composition pattern (`Processor.add()`), the herald-reading pattern (`.performance`/`global_perf`), and the validation pattern (ENC-04-style TVD) are all fully specified by this research with source-verified code-level detail, not just conceptual guidance.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | HIGH | All claims verified by reading installed `perceval-quandela==1.2.4` source directly and by live execution against the actual gate instance in this repo's venv — not recalled from docs or training data. |
| Features | HIGH | Grounded in direct inspection of this repo's existing `iqp_photonic_encoding.py`, its test suite, `docs/iqp-photonic-encoding.md`'s Ingredient 2 derivation, and the same verified Perceval source reads as STACK.md. |
| Architecture | HIGH | All claims verified by direct inspection of the installed package source and by running the actual catalog primitive in this repo's venv (mode counts, herald bookkeeping, `Processor.add()` behavior all confirmed empirically, not assumed). |
| Pitfalls | HIGH (v2.1 addendum) | Load-bearing claims verified by direct source inspection (`heralded_cz.py`, `experiment.py`) and small scripts run against the installed package in this venv; literature figures (1/9, 2/27) cited only where independently reproduced numerically, not taken secondhand. Note: PITFALLS.md's older v2.0 section (literature-scoping/encoding-design pitfalls) is MEDIUM confidence for general research-process judgment and is superseded for this milestone's purposes by the v2.1 addendum. |

**Overall confidence:** HIGH

### Gaps to Address

- **Phase-behavior of the CZ gate (`-1` sign on `|1,1⟩`) has not yet been run** — STACK.md flags this as the next concrete implementation step, not a research gap per se, but it should be checked (via `Simulator.prob_amplitude()` on the un-heralded full circuit) before or alongside Phase 4's validation, since the qubit-side reference's correctness depends on the physical gate actually implementing the intended phase.
- **Success-probability input-independence beyond computational-basis states and one spot-checked superposition case is not exhaustively verified** (Pitfall 12) — the full pipeline's actual `|+⟩`-derived, potentially-entangling inputs should be explicitly measured during Phase 4 validation, not generalized from the spot-check already done in research.
- **`logical_perf`'s negligible-data-leakage assumption (Pitfall 11)** has not yet been formally checked for this project's specific input regime — recommended as an explicit one-time check during Phase 4, recorded in the writeup rather than assumed.

## Sources

### Primary (HIGH confidence)
- `venv/Lib/site-packages/perceval/components/core_catalog/heralded_cz.py` — direct source read, circuit construction, herald modes, fixed angles, `article_ref` (arXiv:quant-ph/0110144).
- `venv/Lib/site-packages/perceval/components/core_catalog/__init__.py`, `component_catalog.py`, `port.py`, `experiment.py` — direct source reads confirming catalog structure, deprecations, port/herald semantics.
- `venv/Lib/site-packages/perceval/runtime/processor.py`, `runtime/abstract_processor.py` — `Processor.add()`, `Processor.probs()`, `compute_physical_logical_perf()`.
- `venv/Lib/site-packages/perceval/simulators/simulator.py`, `simulator_interface.py`, `algorithm/analyzer.py` — `logical_perf`/`physical_perf`/`.performance` semantics, `prob_amplitude()`.
- Live execution against installed `perceval-quandela==1.2.4` in this repo's `./venv` (multiple sessions, 2026-08-05) — ground truth: measured 2/27 ≈ 0.074074 herald-success probability across all 4 computational-basis inputs plus one spot-checked superposition input; confirmed `Processor.add()` correctly propagates sub-processor heralds; reproduced both `StateVector`-input failure modes (Pitfall 10).
- `C:\Users\cuqui\merlin-quantum-case-study\iqp_photonic_encoding.py`, `tests\test_iqp_photonic_encoding.py`, `docs\iqp-photonic-encoding.md` — existing project code/tests/design doc, read directly to determine integration surface and prior conventions.

### Secondary (MEDIUM confidence)
- PITFALLS.md's older v2.0 section (literature-scoping/encoding-design pitfalls, researched 2026-07-30) — general research-process judgment (confirmation bias, scope creep patterns) applied to this project's documented history; not photonics-specific facts, superseded for this milestone's implementation focus by the v2.1 addendum.

### Tertiary (LOW confidence)
- None — no unverified or single-source claims were carried into the table-stakes recommendations.

---
*Research completed: 2026-08-05*
*Ready for roadmap: yes*
