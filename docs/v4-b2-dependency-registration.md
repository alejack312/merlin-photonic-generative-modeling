# B2 optional dependency registration

This records the owner-final B2 dependency selection for rungs 4 and 5. The
dependencies are optional: the default Python suite does not import them, and
no B2 TN/PPS run is authorized until its exact-fixture gate passes.

| Rung | Dependency | Exact version | License | Installation boundary |
|---|---|---:|---|---|
| 4 | [quimb](https://github.com/jcmgray/quimb) | `1.15.0` | Apache-2.0 (`LICENSE.txt`; GitHub metadata is `NOASSERTION`) | Python extra `b2-tn`; declared as `quimb==1.15.0` |
| 5 | [PauliPropagation.jl](https://github.com/SparqleSim/PauliPropagation.jl), formerly `MSRudolph/` | `0.8.2` | Apache-2.0 | Optional package addition through the existing `julia/` environment |

The Pauli-propagation reference is [arXiv:2505.21606](https://arxiv.org/abs/2505.21606).
The authors' [QCBM correlator-surrogates repository](https://github.com/quantumsoftwarelab/QCBM_correlator_surrogates)
is recorded as unavailable because its public contents contain only a README;
it is not installed or substituted.

## Pre-run registration

Before a rung 4 or rung 5 run, the report must register:

- TN: bond dimension, truncation tolerance, contraction order, and discarded weight.
- PPS: cutoff, error diagnostics, and parameter convention.
- Both: exact asymmetric fixture IDs and the absolute probability tolerance.

The current exact gate is `validate_b2_exact_asymmetric_fixtures` over the
registered `n2_asymmetric` and `n3_asymmetric` fixtures at tolerance `1e-12`.
It must pass before capacity, runtime, memory, or approximation comparisons are
recorded. Rung 1 remains an exact reference/oracle diagnostic, never a classical
method.

## Optional installation commands

These commands are registration-only instructions and were not executed as
part of the default suite:

```text
venv\Scripts\python.exe -m pip install -e .[b2-tn]
julia --project=julia -e 'using Pkg; Pkg.add(Pkg.PackageSpec(name="PauliPropagation", version="0.8.2"))'
```

The Julia command uses the existing project-scoped environment and an exact
version request. The current host's Julia executable was unavailable during
the registration check, so PPS availability remains unverified and no Julia
environment was modified.
