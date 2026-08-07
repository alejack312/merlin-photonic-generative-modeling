# Phase 14: Julia Toolchain Spike Summary

## Verdict: **FULL GO**

Both Yao.jl and BosonSampling.jl install cleanly on this Windows machine under
Julia 1.10 LTS and their hello-world circuits pass `@assert` checks against
hand-derived analytical values. No alternate-path attempts were needed for
either component -- the primary path worked for the toolchain install and
both packages on the first try.

## Locked planning decisions (from 14-CONTEXT.md)

1. **One calendar day, whole-spike time-box** (not per-component) -- actual
   wall-clock spent was well under this: roughly 50 minutes total across
   toolchain install, Yao.jl add+precompile, and BosonSampling.jl
   add+precompile.
2. **Exactly one alternate path per stalled component, then stop.** Not
   triggered -- no component stalled.
3. **Hand-derived analytical assertions only**, no Python/Perceval
   cross-check in this phase (deferred to Phase 19's VERIFY-02/03).
4. **Yao.jl: Bell-state circuit (H + CNOT).** BosonSampling.jl: 2-mode 50/50
   beamsplitter on `|1,0>`. Both per CONTEXT's "Claude's Discretion" section.

## Per-component detail

### Toolchain: juliaup + Julia 1.10 LTS

- Installed via primary path: `winget install --id=Julialang.Juliaup -e`.
  Succeeded on first attempt, no antivirus/quarantine issue observed
  (Pitfall 1 from 14-RESEARCH.md did not manifest on this machine).
- `juliaup add lts; juliaup default lts` pinned Julia to **1.10.11 LTS**,
  confirmed via `julia --version` in a fresh shell and `juliaup status`
  showing `lts` marked as default.
- **Result: PASS.** No alternate path needed.

### Yao.jl

- Added via `Pkg.add("Yao")` in the project-scoped `julia/` environment.
  Resolved to v0.9.3 initially; after BosonSampling.jl was added later, the
  resolver downgraded it to **v0.9.1** to satisfy the combined environment's
  compatibility constraints (both are `julia/hello_yao.jl`-compatible --
  the API surface used, `chain`/`put`/`control`/`zero_state`/`probs`, is
  unaffected).
- 142 dependencies precompiled cleanly in ~241 seconds, 0 errors.
- `probs(reg)` is directly exported at the top-level `Yao` namespace --
  resolves 14-RESEARCH.md's Open Question 2. No `YaoArrayRegister`
  qualification or `abs2.(statevec(reg))` fallback was needed.
- `julia/hello_yao.jl` (Bell state via H on qubit 1 + CNOT(1,2)) ran and
  passed all 4 `@assert`s against the analytical values (0.5, 0.0, 0.0, 0.5).
  Observed vector: `[0.4999999999999999, 0.0, 0.0, 0.4999999999999999]`.
- **Result: PASS.** No alternate path needed.

### BosonSampling.jl

- Added via `Pkg.add("BosonSampling")` in the same project environment.
  Resolved to v1.0.2. Notably, **the resolver did not pull in ITensors.jl**
  at all for this environment -- 14-RESEARCH.md's biggest flagged risk
  (Pitfall 3: ITensors.jl's Windows precompilation failure history) never
  materialized, because the dependency wasn't part of the resolved graph in
  this configuration.
- 231 dependencies precompiled in ~687 seconds (~11.5 min) with 0 errors --
  only benign deprecation/method-shadowing warnings from `Formatting`,
  `DataFrames`, and `Interpolations` (unrelated to BosonSampling itself).
- The lowercase `beam_splitter(t)` function (confirmed-from-source fallback
  in 14-RESEARCH.md) was used directly; the capitalized `BeamSplitter(...)`
  convenience constructor from the paper's example was not tried since the
  documented-safe path worked immediately -- resolves 14-RESEARCH.md's Open
  Question 1 in practice (not required either way).
- `julia/hello_bosonsampling.jl` (50/50 beamsplitter on `|1,0>` via
  `UserDefinedInterferometer(beam_splitter(1/sqrt(2)))` +
  `Input{Bosonic}`/`FockDetection`/`Event`/`compute_probability!`) ran and
  passed both `@assert`s against the analytical values (0.5, 0.5). Observed:
  `transmitted=0.4999999999999999, reflected=0.5000000000000001`.
- **Result: PASS.** No alternate path needed.

## Alternate-path attempts

None. Both the toolchain install and both packages succeeded on their
primary, documented paths on the first attempt.

## Wall-clock time (relative to the one-day time-box)

Roughly 50 minutes of actual elapsed time:
- juliaup install + LTS pin: a few minutes.
- Yao.jl `Pkg.add` + precompile: ~241 seconds (~4 min).
- BosonSampling.jl `Pkg.add` (resolve + download + precompile): ~20-25
  minutes total, of which precompilation itself was ~687 seconds (~11.5
  min) -- the remainder was package resolution/download for the ~250-package
  combined dependency tree.

Well within the one-calendar-day time-box; no overnight troubleshooting was
needed.

## What this means for Phase 19

Full go on both components means **Phase 19's VERIFY-02 (qubit-side,
Yao.jl) and VERIFY-03/04 (photonic-side, BosonSampling.jl) can all proceed
as originally scoped** -- no re-opened scope conversation with the owner is
needed. `julia/hello_yao.jl` and `julia/hello_bosonsampling.jl` are the
starting points Phase 19 extends, per this project's established pattern of
building on prior phases' modules rather than starting from zero.

One forward-looking note for Phase 19: the combined `julia/` environment now
resolves Yao.jl to v0.9.1 (not the latest v0.9.3) due to BosonSampling.jl's
compatibility constraints. This is expected Julia `Pkg` resolver behavior
for a shared environment and does not affect correctness of the API surface
used here, but Phase 19 should be aware the pinned version may lag Yao.jl's
latest release for as long as both packages share this one environment.
