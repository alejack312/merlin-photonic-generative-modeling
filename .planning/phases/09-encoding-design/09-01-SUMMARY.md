---
phase: 09-encoding-design
plan: 01
subsystem: docs+testing
tags: [perceval, photonics, polarization, iqp, encoding, fock-space]

# Dependency graph
requires:
  - phase: 08-literature-scoping-prerequisites
    provides: perceval_fluency_demo.py's MZI/PS interference pattern, docs/iqp-baseline.md's IQP structure, LIT-04 go verdict
provides:
  - ENC-01 ingredient-level mapping (docs/iqp-photonic-encoding.md), owner-chosen polarization encoding
  - iqp_photonic_encoding.py's state-prep/diagonal-layer/conjugation/readout circuit builders, weight-1 generators
  - Correction to 09-RESEARCH.md's claim that Perceval lacks a polarization gate catalog (it ships HWP/QWP/PR/WP/PBS)
affects: [09-02-encoding-design, 09-03-encoding-design, 09-04-encoding-design]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "WP(theta, xsi=0) = diag(e^{i*theta}, e^{-i*theta}) exactly -- the polarization analogue of PS for a Z-diagonal phase gate, verified against Perceval's installed unitary matrix, not assumed"
    - "HWP(xsi) = WP(pi/2, xsi); HWP(pi/8) realizes Hadamard up to an unobservable global phase i -- confirmed both symbolically and numerically"
    - "A bare polarized BasicState needs PBS conversion to spatial modes before Analyzer/Processor.probs() can resolve H vs V -- polarization analogue of perceval_fluency_demo.py's bare-PS-invisible-without-a-second-BS finding"
    - "2n-mode layout: qubit k occupies ports 2k (polarization) and 2k+1 (vacuum partner, used only at readout)"

key-files:
  created:
    - docs/iqp-photonic-encoding.md
    - iqp_photonic_encoding.py
    - tests/test_iqp_photonic_encoding.py
  modified: []

key-decisions:
  - "Owner chose polarization encoding (H/V) from personal Sorbonne coursework, not dual rail or QUDIT -- corrects 09-RESEARCH.md's characterization of polarization as lacking a native gate catalog (HWP/QWP/PR/WP/PBS all ship in perceval-quandela==1.2.4, confirmed by direct source inspection)"
  - "Runnable code and tests scoped to weight-1 IQP generators only; weight-2 (exp(i*theta*Z_i*Z_j)) derived on paper via PBS-mediated conversion to dual rail's core_catalog.heralded_cz, using the operator identity CZ = exp(i*pi/4*(I-Z_i-Z_j+Z_iZ_j)) -- CZ is a fixed-angle (pi/4) instance of the ZZ-interaction family, not a continuously-tunable gate, a real limitation of the catalog gate rather than a design flaw"
  - "heralded_cz's source was read directly (Knill CZ, arXiv:quant-ph/0110144, 2 herald modes each requiring exactly 1 photon) to confirm the mechanism is real; its exact success probability was explicitly NOT claimed as verified -- the 1/9 (post-selected KLM)/2/27 (heralded variant) figures are secondhand literature citations for the same gate family, flagged as assumed not verified"

patterns-established:
  - "Self-explanation checkpoint Q&A (both rounds, including the initial incorrect/incomplete answers and corrections) documented directly in the mapping doc, not just the polished final result -- matches this repo's established pattern (v1.0 GEN-07, Phase 7 neighbor-locality) of keeping negative/partial results visible rather than smoothing them over"

# Metrics
duration: ~2.5hr (interactive, across multiple checkpoint rounds)
completed: 2026-08-05
---

# Phase 9 Plan 01: ENC-01 Ingredient-Level Mapping Summary

**Polarization-encoded IQP-to-photonic mapping: |+⟩ prep and Hadamard-conjugation via `HWP(π/8)`, weight-1 Z-diagonal generators via the exact `WP(θ,0) = diag(e^{iθ},e^{-iθ})` identity, weight-2 generators derived on paper via a `PBS`→`heralded_cz`→`PBS` round trip. n=2-3 worked examples verified against the predicted product distribution to floating-point precision.**

## Performance

- **Duration:** ~2.5 hours, interactive (Task 1 checkpoint required multiple correction rounds; Task 3 self-explanation checkpoint required one correction round)
- **Completed:** 2026-08-05
- **Tasks:** 3 (Task 1: attempt-first checkpoint; Task 2: implementation; Task 3: self-explanation checkpoint)
- **Files created:** 3 (`docs/iqp-photonic-encoding.md`, `iqp_photonic_encoding.py`, `tests/test_iqp_photonic_encoding.py`)

## Task 1: Attempt-First Checkpoint

Owner picked polarization encoding (H/V) from their own Sorbonne coursework. Initial sketch needed two corrections, both recorded in the doc's "Owner's Attempt" section:
- State prep: owner proposed a 45° beamsplitter; corrected to `HWP(ξ=π/8)` (a wave plate, not a beamsplitter — a half-wave plate rotates polarization by *twice* its physical axis angle, so 22.5° is the correct setting, not 45°).
- Multi-qubit gates: owner initially proposed CNOT/CZ/SWAP generically; corrected that IQP's middle layer is Z-diagonal by definition, which rules out CNOT and SWAP (not Z-diagonal) and leaves CZ as the legitimate example. Owner chose the heralded (not post-selected) construction.

This surfaced a real inaccuracy in `09-RESEARCH.md`'s survey (claimed Perceval has no polarization gate catalog) — corrected by direct inspection of the installed `perceval-quandela==1.2.4` source, which ships `HWP`, `QWP`, `PR`, `WP`, and `PBS`.

## Task 2: Implementation

`iqp_photonic_encoding.py` implements, on a `2n`-mode layout (qubit `k` = ports `2k` polarization + `2k+1` vacuum partner):
- `build_state_prep_circuit(n)` — `HWP(π/8)` per qubit
- `build_diagonal_layer_circuit(n, thetas)` — `WP(thetas[k], 0)` per qubit, exact `exp(iθZ)`
- `build_conjugation_circuit(n)` — same `HWP(π/8)` (Hadamard is self-inverse)
- `build_readout_circuit(n)` — `PBS` per qubit, required before Analyzer can resolve H/V
- `build_full_circuit`/`run_full_circuit` — full pipeline, plus closed-form comparison helpers

`docs/iqp-photonic-encoding.md`'s ENC-01 section derives commutativity and conjugation-symmetry at equation level, states the weight-2 scope limitation explicitly (fixed-angle `π/4` via `heralded_cz`, not continuously tunable), and instantiates n=2 and n=3 worked examples that match their predicted product distributions to floating-point precision with zero probability leaking outside the computational subspace.

**Verification:** `pytest tests/test_iqp_photonic_encoding.py -v` — 12/12 passed. `python -c "import iqp_photonic_encoding"` — clean.

## Task 3: Self-Explanation Checkpoint

Owner's first-round answers restated the qubit-side abstraction (commutativity) and contained a physical misconception (described Hadamard-conjugation as collapsing `|+⟩` into a single polarization, rather than converting an invisible phase into an observable population imbalance). Both corrected via a Feynman-style walkthrough, after which the owner's second-round answers were correct: the CZ-as-frozen-ZZ-dial-setting identity, the two distinct reasons operators commute (disjoint tensor factors vs. same-basis diagonal-matrix multiplication), and the phase-to-population mechanism (with one remaining overclaim — "converts into `|0⟩` or `|1⟩`" — corrected to "population imbalance, still a superposition for general θ"). While verifying the CZ/heralded-gate discussion, `core_catalog.heralded_cz`'s actual source was read directly (Knill CZ, arXiv:quant-ph/0110144) rather than relying on the secondhand 1/9 literature figure repeated earlier in the conversation — that figure was explicitly flagged as unverified for this specific gate.

Full Q&A (both rounds, including the corrections) recorded in `docs/iqp-photonic-encoding.md`'s "Self-Explanation Checkpoint (Task 3)" section.

## Deviations

None from the plan's task structure. The attempt-first checkpoint (Task 1) required more correction rounds than a single exchange (owner's initial framing needed the beamsplitter-vs-waveplate and CNOT/SWAP-not-Z-diagonal corrections before a workable sketch emerged) — handled inline per the plan's own "a rough attempt... is enough" allowance, not treated as a blocker.
