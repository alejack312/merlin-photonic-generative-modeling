# Phase 19 Plan 05: VERIFY-04 Results

## Methodology

### Native loss API investigation (Task 1)

BosonSampling.jl's native `UniformLossInterferometer(η, U_physical)` loss
API (confirmed against the ACTUAL installed v1.0.2 source at
`~/.julia/packages/BosonSampling/TEQXU/src/types/loss.jl`, not GitHub main)
IS used -- the strongly-preferred path per `19-RESEARCH.md`'s "Don't Hand-Roll"
table -- with one narrow, verified workaround for a real dispatch gap in the
installed package:

- **Convention mismatch found and resolved:** `η` in `UniformLossInterferometer`
  is a transmission AMPLITUDE (confirmed from `circuit_elements.jl`'s
  `beam_splitter` comment: `|t|^2` is the transmission probability), while this
  repo's Python-side `eta` is a transmission PROBABILITY. This script passes
  `sqrt(eta)` to make the two `eta`'s mean the same physical quantity --
  verified by the n=1 sanity check below.
- **Real bug found in the installed package, worked around:**
  `Event(input, output, uniform_loss_interferometer)` raises
  `MethodError: no method matching LossParameters(::Type{UniformLossInterferometer})`
  -- confirmed live via a standalone repro, not inferred. Worked around by
  wrapping the interferometer's own native-computed `.U` field in
  `UserDefinedInterferometer(li.U)` before constructing `Event`s --
  `compute_probability!` only ever reads `ev.interferometer.U`, so the
  numerical result is identical; only the dispatch path differs. The loss
  PHYSICS still comes entirely from BosonSampling's own native
  `UniformLossInterferometer`/`virtual_interferometer_uniform_loss`
  construction -- this is not a hand-attenuation fallback.
- **Doubled-mode marginalization:** done by hand (not via
  `sort_by_lost_photons`/`lossless_part`, whose semantics were unverified per
  `19-RESEARCH.md` Open Question 2): every non-negative-integer composition of
  the conserved total photon count N across the 2m output modes is enumerated
  exactly (36 patterns for weight-1 n=2, 1365 for mixed n=2), `compute_probability!`
  is called once per full 2m-mode pattern, and probabilities are summed into a
  bucket keyed by the physical-mode (first-m) sub-pattern -- an exact marginal,
  not sampling or approximation.

See `julia/verify_loss_model.jl`'s header comment for the full investigation
detail and source citations.

### n=1 sanity check

Confirmed `eta_python = (transmission_amplitude)^2` and the
`UserDefinedInterferometer(li.U)` workaround against the known closed-form
single-mode loss case (p(survive)=eta, p(lost)=1-eta) at eta in {0.99, 0.80, 0.05},
atol=1e-10, before trusting the n=2 comparison. PASS.

### n=2 cross-checks

Weight-1: an independently-built dual-rail circuit (reusing Plan 19-03's verified
`H*phase_shift(pi-2*theta)*H` per-qubit construction, block-diagonal, no entangling
gate) under native uniform loss, marginalized to a physical-mode distribution, diffed
against `results/julia_reference/weight1_loss_n2_eta{099,080,005}.csv` (Plan 19-01's
fixed single-draw thetas=[1.4696702887560742, 0.5745464671322527]).

Mixed: an independently-built n=2, i=0, j=1 weight-1+weight-2 circuit (reusing Plan
19-04's verified Knill-CZ construction, arXiv:quant-ph/0110144 Eq. 11 transpose-fixed,
generalized to two independent per-qubit diagonal phases theta_A/theta_B = thetas[i]+pi/4,
thetas[j]+pi/4, matching `build_diagonal_layer_circuit`'s symmetric diag(e^{i*theta},
e^{-i*theta}) convention exactly since the CZ gate creates real interference between the
two qubit pairs) under native uniform loss (applied to all 2n+2=6 physical modes,
including both ancilla modes -- matching Python's ancilla-inclusive HARD-07 model),
herald accounting done by hand exactly as Plan 19-04 did (ancilla output pattern must be
[1,1] or the outcome counts as herald failure), diffed against
`results/julia_reference/mixed_loss_n2_eta{099,080,005}.csv` (Plan 19-01's fixed
single-draw thetas=[1.6612470810666293, 1.2467258944387942]).

## Results

### Weight-1

| eta | TVD | Tolerance | Status |
|-----|-----|-----------|--------|
| 0.99 | 2.0708261494473135e-16 | <= 1.0e-6 | PASS |
| 0.8 | 8.131516293641283e-18 | <= 1.0e-6 | PASS |
| 0.05 | 1.6199505116238494e-18 | <= 1.0e-6 | PASS |

### Mixed

| eta | TVD | herald_failure_prob (julia) | herald_failure_prob (python) | \|diff\| | Status |
|-----|-----|------------------------------|-------------------------------|----------|--------|
| 0.99 | 1.7531115448221612e-14 | 0.925933479999999 | 0.9259334800000015 | 2.55351295663786e-15 | PASS |
| 0.8 | 7.806255641895632e-17 | 0.9298370370370368 | 0.9298370370370368 | 0.0 | PASS |
| 0.05 | 1.1689054672109345e-19 | 0.9991287037037037 | 0.9991287037037037 | 0.0 | PASS |

## Verdict

**VERIFY-04: GO**

BosonSampling.jl's independently-built weight-1 and mixed loss circuits, run
through the native `UniformLossInterferometer` loss model (with the documented
`LossParameters` dispatch workaround), reproduce the Python/Perceval `pcvl.LC`
reference distributions within TVD <= 1.0e-6 at all 3 tested eta values
for both scope, satisfying VERIFY-04 in full -- weight-1 and mixed, both scopes,
using BosonSampling.jl's own native, structurally-different loss mechanism (a
beamsplitter-to-environment-mode model) rather than a mechanism mirroring
Perceval's `pcvl.LC` lossy-channel component.
