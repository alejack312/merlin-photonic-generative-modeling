# Phase 19 Plan 02 (VERIFY-02): Yao.jl Qubit-Side IQP Cross-Check Results

## Verdict: **GO**

An independently-built Yao.jl circuit reproduces the Python/`iqp_photonic_encoding.py`
reference qubit-side IQP distribution at both n=2 and n=3, with measured TVD many
orders of magnitude below the locked `1e-6` tolerance:

| n | thetas | TVD (Julia vs. Python) | Tolerance | Result |
|---|--------|------------------------:|-----------|--------|
| 2 | `[0.3, 1.1]` | `2.26e-17` | `1e-6` | PASS |
| 3 | `[0.3, 1.1, 0.75]` | `1.12e-16` | `1e-6` | PASS |

Both measured TVDs sit at the level of floating-point noise -- consistent with
both sides being exact, non-sampling computations of the same physics, not an
approximate/statistical agreement.

## Methodology

### Circuit construction (independent, not a mechanical port)

Built entirely from Yao.jl's own qubit-gate API (`H`, `Rz`, `put`, `chain`,
`zero_state`, `probs`) -- the same shape as this repo's own
`exact_qubit_iqp_distribution` (state prep -> diagonal weight-1 phase layer ->
Hadamard conjugation -> `|amplitude|^2`), but expressed in Yao's own idioms
rather than replaying Perceval's circuit structure:

```julia
function build_qubit_iqp_circuit(n, thetas)
    had_layer = chain(n, [put(k => H) for k in 1:n]...)
    phase_layer = chain(n, [put(k => Rz(-2 * thetas[k])) for k in 1:n]...)
    circuit = chain(n, had_layer, phase_layer, had_layer)
    return zero_state(n) |> circuit
end
```

### Phase-convention derivation (verified algebraically and numerically)

This repo's weight-1 generator gate is `WP(theta,0) = diag(e^{i*theta}, e^{-i*theta})`.
Yao's built-in `Rz(phi) = diag(e^{-i*phi/2}, e^{i*phi/2})`. Setting `phi = -2*theta`:

```
Rz(-2*theta) = diag(e^{-i*(-2*theta)/2}, e^{i*(-2*theta)/2})
             = diag(e^{i*theta}, e^{-i*theta})
             = WP(theta, 0)          -- entry-for-entry, not "up to global phase"
```

Confirmed numerically at n=1 (`theta=0.3`): the circuit's `probs()` output
`[0.91266780745..., 0.08733219254...]` matches the closed-form single-qubit
marginal `[cos(theta)^2, sin(theta)^2]` to `atol=1e-10`.

### Bit-ordering confirmation (verified empirically, not assumed)

Yao's `probs()` vector ordering was confirmed empirically for this specific
circuit, not assumed from `hello_yao.jl`'s Bell-state comment. An asymmetric
n=2 circuit (`thetas=[0.3, 1.1]`, no entangling gate so each qubit's marginal
factors independently) was built, and two candidate bit-orderings were tested
against the known closed-form per-qubit marginals `P(qubit_m=0)=cos(thetas[m])^2`:

- **Candidate A** (qubit `m` = LSB of the 0-based index): predicted
  `P(q1=0)=0.91266..., P(q2=0)=0.20574...` -- **matched** the measured
  marginals.
- **Candidate B** (qubit `m` = MSB): predicted the two values swapped --
  did not match.

Only Candidate A matched (confirmed by an explicit `@assert` that exactly one
candidate matches). This confirms Yao's qubit-1-is-least-significant-bit
convention for this circuit, consistent with (but independently re-verified
against, not just re-cited from) `hello_yao.jl`'s Phase 14 finding.

`probs_to_bitstring_dict(reg, n)` converts Yao's `probs()` vector into a
`Dict{String,Float64}` keyed by this repo's own bitstring convention (qubit 0
= leftmost character, matching `exact_qubit_iqp_distribution`'s docstring),
using the empirically-confirmed bit-ordering fact above.

### Diff protocol

Both n=2 and n=3 distributions are diffed **by bitstring key**, never by raw
vector index -- the Python reference CSVs
(`results/julia_reference/qubit_n2.csv`, `qubit_n3.csv`) are read into
`Dict{String,Float64}` via `DelimitedFiles` (forcing `String` element type so
leading-zero bitstrings like `"00"` are preserved, not parsed as numbers).
TVD is computed via a direct Julia reimplementation of
`iqp_photonic_encoding.py::total_variation_distance`
(`0.5 * sum(|a(x)-b(x)|)` over the union of both dicts' keys) -- no Python
import or shell-out.

### Shared test inputs (matching Plan 19-01's Python-side generation exactly)

- n=2: `thetas=[0.3, 1.1]`
- n=3: `thetas=[0.3, 1.1, 0.75]`

## Result

`julia --project=julia julia/verify_qubit_iqp.jl` runs to completion, prints
`PASS` at every checkpoint (n=1 phase convention, n=2 bit-ordering, n=2 TVD,
n=3 TVD), and exits 0. No debugging pass was needed -- both TVDs passed on
the first run of the completed script.

## What this establishes / does not establish

- **Establishes:** the qubit-side IQP math (weight-1 diagonal phase layer +
  Hadamard conjugation) is correctly implemented in `iqp_photonic_encoding.py`,
  confirmed by an independent second implementation built from a different
  library's own API, at n=2 and n=3.
- **Does not establish:** anything about the photonic-level encoding (PBS,
  polarization gates, `heralded_cz`) -- that is VERIFY-03's scope (Plans
  19-03/19-04), not this plan's.

VERIFY-02 is satisfied.
