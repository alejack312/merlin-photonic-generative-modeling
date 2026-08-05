---
phase: 09-encoding-design
plan: 03
subsystem: docs+testing
tags: [perceval, photonics, polarization, iqp, encoding, validation, tvd]

# Dependency graph
requires:
  - phase: 09-encoding-design (plan 09-02)
    provides: ENC-03 basis correspondence, fock_to_bitstring/bitstring_to_fock
affects: [09-04-encoding-design]
provides:
  - ENC-04 validation plan and actual n=2,3 toy-scale check (docs/iqp-photonic-encoding.md), TVD ~1e-16 (10 orders of magnitude under the 1e-6 threshold), zero residual
  - iqp_photonic_encoding.py's exact_qubit_iqp_distribution (numpy state-vector reference), photonic_iqp_distribution, total_variation_distance

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Exact-vs-exact distribution comparison should use a parameter-free metric (TVD) rather than MMD -- MMD's kernel/bandwidth machinery exists to handle sampling noise, which doesn't apply when both sides are exact calculations"
    - "Bit-ordering convention (qubit 0 = MSB) stated explicitly in exact_qubit_iqp_distribution's docstring, following the sibling iqp-mmd-barren-plateau project's documented 'critical for correctness' gotcha on the same class of bug"

key-files:
  created: []
  modified:
    - docs/iqp-photonic-encoding.md
    - iqp_photonic_encoding.py
    - tests/test_iqp_photonic_encoding.py

key-decisions:
  - "Reference method: direct numpy state-vector simulation (|+>^n -> diagonal phase -> H^n -> |amplitude|^2), not Van den Nest's cosine-formula trick (would need an extra transform step to get a full distribution from expectation values) or the sibling repo's IqpSimulator (disproportionate cross-repo dependency for n=2-3)"
  - "Metric: total variation distance, not MMD -- MMD's kernel-bandwidth choice exists to handle sampling noise; both distributions being compared here are exact, so there's no noise to smooth over and no principled way to pick a bandwidth"
  - "Threshold: TVD < 1e-6, chosen after distinguishing this exact-vs-exact comparison from the sibling project's own TVD thresholds (0.05/0.4), which apply to a sampled-vs-learned comparison with real statistical noise -- not this project's situation"
  - "Owner's initial claim that the weight-1 result 'will extend to generators of higher weight' was corrected during the Task 3 checkpoint: weight-1 (WP, exact/deterministic/any angle) and weight-2 (heralded_cz, probabilistic/fixed-angle) are structurally different mechanisms, so a clean weight-1 match provides no evidence about weight-2 -- documented as a standing scope limit, not smoothed over"

patterns-established:
  - "Numeric self-explanation checkpoints (owner interprets computed metrics) documented with the same full-transcript pattern as conceptual checkpoints, including a misread of scientific notation and its correction -- consistent with this repo's practice of keeping the actual back-and-forth visible"

# Metrics
duration: ~1.5hr (interactive, across multiple guided-question rounds)
completed: 2026-08-05
---

# Phase 9 Plan 03: ENC-04 Validation Plan and Toy-Scale Check Summary

**Actually-run n=2 and n=3 comparison between the exact qubit-side IQP distribution (plain numpy) and the ENC-01/ENC-03 photonic circuit's decoded output: TVD ~1e-16 in both cases, ten orders of magnitude under the owner's chosen 1e-6 threshold, zero out-of-subspace residual. Confirms the mapping's central claim for weight-1 generators; explicitly does not extend to the untested weight-2 case.**

## Performance

- **Duration:** ~1.5 hours, interactive (Task 1 required two redirects — first from re-describing the photonic circuit as its own "reference," then from proposing MMD before settling on TVD with a threshold grounded in the exact-vs-exact nature of the comparison; Task 3 required correcting a scientific-notation misread and an unsupported extrapolation to weight-2)
- **Completed:** 2026-08-05
- **Tasks:** 3 (Task 1: attempt-first checkpoint; Task 2: implementation and actual run; Task 3: self-explanation checkpoint, numeric interpretation)
- **Files modified:** 3 (`docs/iqp-photonic-encoding.md`, `iqp_photonic_encoding.py`, `tests/test_iqp_photonic_encoding.py`)

## Task 1: Attempt-First Checkpoint

Owner's first sketch re-described the photonic circuit itself as the validation reference — corrected: a circuit can't validate itself, ENC-04 needs an independent calculation. Owner then asked about Van den Nest's cosine formula (technically applicable, but yields expectation values not a full distribution — more machinery than needed) and MMD loss (declined: MMD's bandwidth-selection machinery, the source of this project's own Phase 4/7 sigma-resweep work, exists to handle sampling noise that doesn't apply when both sides are exact). Checked the sibling `iqp-mmd-barren-plateau` project's vault for TVD conventions per the owner's request — found the same standard formula, a documented bit-ordering-convention gotcha (carried into this plan's implementation), and thresholds (`<0.05`/`>0.4`) that apply to a sampled-vs-learned comparison, not this project's exact-vs-exact situation. Final attempt: direct numpy state-vector reference, TVD metric, `TVD < 1e-6` threshold.

## Task 2: Implementation

Added to `iqp_photonic_encoding.py`: `exact_qubit_iqp_distribution(n, thetas)` (plain numpy, explicit MSB bit-ordering convention), `photonic_iqp_distribution(n, thetas)` (runs ENC-01's circuit, decodes via ENC-03's `fock_to_bitstring`, returns `(dist, residual)` per ENC-03's explicit-residual policy), `total_variation_distance(dist_a, dist_b)`. Actually run for `n=2` (`thetas=[0.3,1.1]`) and `n=3` (`thetas=[0.3,1.1,0.75]`): TVD `3.85e-16` and `5.68e-16` respectively, residual `0.0` in both cases. `docs/iqp-photonic-encoding.md`'s new `## ENC-04` section reports both distribution tables and the actual numbers (not a hypothetical).

**Verification:** `pytest tests/test_iqp_photonic_encoding.py -v` — 26/26 passed, including the new end-to-end comparison test asserting `TVD < 1e-6` for both `n` values.

## Task 3: Self-Explanation Checkpoint

Owner's first interpretation misread the scientific notation (`3.85×10⁻¹⁶` read as failing the `1×10⁻⁶` threshold, rather than passing it by ten orders of magnitude) — corrected with a concrete magnitude comparison. Second attempt was directionally correct but under-stated ("going well so far") and, in its second half, extrapolated the weight-1 result to weight-2 without justification. Corrected: weight-1 (`WP`, exact/deterministic/any angle) and weight-2 (`heralded_cz`, probabilistic/fixed-angle-only) are structurally different mechanisms; a clean weight-1 match is silent on weight-2. Final answer: the weight-1 result decisively confirms the mapping's central claim for the tested cases; weight-2 remains genuinely untested ("we'll have to see via heralding"). Also caught and fixed the author's own arithmetic slip while drafting the doc (an earlier draft mis-stated "four orders of magnitude" instead of the correct ten).

Full Q&A, including both misreads and their corrections, recorded in `docs/iqp-photonic-encoding.md`'s "Self-Explanation Checkpoint (Task 3) — Owner's Interpretation" section.

## Deviations

None from the plan's task structure. No mismatch was found in the toy check, so no revision to ENC-01/ENC-03 was needed (the plan's "if mismatch, revise" branch didn't trigger).
