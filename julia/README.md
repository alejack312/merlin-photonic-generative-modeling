# julia/

Phase 14 (Julia Toolchain Spike) artifacts: a Julia environment with Yao.jl
(qubit circuits) and BosonSampling.jl (linear-optics/Fock-state circuits),
each proven via a hello-world script asserted against a hand-derived
analytical value. Phase 19 extends these scripts for cross-checks against
this project's Python/Perceval results — it does not start from zero.

## Install

Install `juliaup` (Julia's official version manager):

```
winget install --id=Julialang.Juliaup -e
```

Open a fresh shell (PATH changes require this), then pin to the 1.10 LTS
channel:

```
juliaup add lts
juliaup default lts
julia --version   # expect: julia version 1.10.x
```

## Activate this project

From the repo root:

```
julia --project=julia -e 'using Pkg; Pkg.instantiate()'
```

## Run the hello-world scripts

```
julia --project=julia julia/hello_yao.jl
julia --project=julia julia/hello_bosonsampling.jl
```

Each script prints a Julia/package version banner, runs a small circuit, and
`@assert`s the result against its analytically-known value.

See `results/phase14_julia_toolchain_summary.md` for this spike's recorded
go/no-go verdict.
