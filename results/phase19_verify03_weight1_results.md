# Phase 19 Plan 03: VERIFY-03 Weight-1 Leg Results

## Methodology

An independent BosonSampling.jl dual-rail (2-modes-per-qubit) circuit for the
weight-1 photonic IQP generator family was built from BosonSampling.jl's own
primitives (`beam_splitter`, `phase_shift`, `UserDefinedInterferometer`) --
not a port of Perceval's HWP/WP/PBS polarization circuit (`iqp_photonic_encoding.py`).

Encoding: qubit k (1-indexed) occupies modes `(2k-1, 2k)`; bit=0 <=> upper mode
occupied, bit=1 <=> lower mode occupied. Per-qubit gate stack: Hadamard-equivalent
(`beam_splitter(1/sqrt(2))`) -> Z-phase (`phase_shift(pi - 2*theta)` on the lower
rail) -> Hadamard-equivalent conjugation. The phase parameter `phi = pi - 2*theta`
was algebraically derived (not assumed) from `H*D*H` acting on the bit=0 input,
requiring `P(bit=0) = cos(theta)^2` to match Python's closed-form marginal -- see
the header comment in `julia/verify_photonic_iqp_weight1.jl` for the full derivation.

The n=1 convention check (Task 1) verifies this construction directly against the
known closed-form single-qubit marginal `P(bit=0)=cos(theta)^2, P(bit=1)=sin(theta)^2`
at theta=0.3, before trusting the full n=2/n=3 comparison.

The n=2/n=3 distributions are computed by enumerating all `2^n` valid
computational-basis outcomes (each qubit pair carries exactly 1 photon) via
`compute_probability!` per outcome, and diffed by total variation distance against
Python's `photonic_iqp_distribution` reference (`results/julia_reference/weight1_n2.csv`,
`weight1_n3.csv`, generated in Plan 19-01), using the identical theta values
(`n=2: thetas=[0.3, 1.1]`, `n=3: thetas=[0.3, 1.1, 0.75]`).

## Results

| n | thetas | TVD | Tolerance | Status |
|---|--------|-----|-----------|--------|
| 2 | [0.3, 1.1] | 2.3592239273284576e-16 | <= 1.0e-6 | PASS |
| 3 | [0.3, 1.1, 0.75] | 3.0357660829594124e-16 | <= 1.0e-6 | PASS |

n=1 convention check: p(bit=0)=0.9126678074548391 (expected 0.9126678074548391), 
p(bit=1)=0.0873321925451609 (expected 0.08733219254516084), both within atol=1e-10. PASS.

## Verdict

**VERIFY-03 weight-1 leg: GO**

BosonSampling.jl's independently-built dual-rail weight-1 circuit reproduces
the Python/Perceval reference distribution within TVD <= 1.0e-6 at both
n=2 and n=3, confirming cross-implementation agreement on the weight-1 photonic
IQP distribution. This satisfies VERIFY-03's weight-1 leg independent of Plan
19-04's weight-2 (Knill-CZ) leg.
