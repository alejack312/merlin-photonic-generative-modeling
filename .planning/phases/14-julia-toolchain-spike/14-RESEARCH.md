# Phase 14: Julia Toolchain Spike - Research

**Researched:** 2026-08-07
**Domain:** Julia toolchain bring-up on Windows (juliaup, Yao.jl, BosonSampling.jl) — de-risking spike, not integration work
**Confidence:** MEDIUM-HIGH overall (juliaup install path and both packages' registered versions verified directly from primary sources; exact hello-world API calls corroborated across 2+ independent sources but not locally executed, since Julia is not installed in this environment)

## Summary

This phase installs a brand-new Julia toolchain on a Windows machine and proves two packages (Yao.jl for qubit circuits, BosonSampling.jl for linear optics) install and run with an analytically-checkable result. This project's own prior milestone research (`.planning/research/STACK.md`, 2026-08-06) already scoped this exact stack — juliaup, Julia 1.10 LTS, Yao.jl, BosonSampling.jl — and rejected Ket.jl for lacking a photonic/Fock-space model. This research phase adds the missing operational detail: exact install commands, exact hello-world code, and the concrete Windows-specific failure modes the CONTEXT's one-alternate-path/time-box logic needs to be able to recognize quickly.

The single biggest concrete risk found is **not** package availability (both packages are live in the Julia General registry, actively maintained, and declare broad `julia = "1"` compatibility) — it is **Windows security software interfering with juliaup's and Julia's own binaries**: juliaup ships unsigned executables that some antivirus/endpoint-protection products kill on install, and Julia's `pkgimages` precompilation cache writes unsigned DLLs that Windows Defender Application Control (where present) blocks with no graceful fallback. A secondary, package-specific risk is that BosonSampling.jl pulls in ITensors.jl (via a 33-package dependency tree including Plots, Luxor, JLD) which has a recurring history of Windows precompilation failures across recent Julia versions — this is exactly the kind of "component stalls, try one alternate path" scenario the CONTEXT already anticipates.

**Primary recommendation:** Install via `winget install --id=Julialang.Juliaup -e` (or the MS Store variant), target Julia 1.10 LTS via `juliaup add lts; juliaup default lts` (not the bleeding-edge release channel — precompilation issues cluster on newer/beta versions), then `Pkg.add(["Yao","BosonSampling"])` in one `julia/Project.toml`-scoped environment. If BosonSampling.jl fails, the fastest diagnostic signal is whether the failure is at `Pkg.add`/resolve (registry/version problem) vs. at first `using BosonSampling` (precompilation problem, most likely ITensors-related) — the CONTEXT's "one alternate path" should target whichever stage actually failed.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|---------------|
| `juliaup` | latest (Rust-based installer/version-manager, actively maintained) | Installs and manages Julia versions, exposes `julia` on PATH | Official JuliaLang tool; this project's own prior research (STACK.md) already chose it over a bare installer specifically so switching Julia versions is a one-line command. |
| Julia | 1.10.11 LTS (confirmed current LTS) or 1.12.6 (current `release` channel) | Language runtime | LTS recommended for this spike over `release` — fewer moving parts this close to deadline, and the ITensors-Windows precompile issues found in this research (see Pitfalls) skew toward newer/beta Julia versions. `juliaup add lts; juliaup default lts` installs and pins it. |
| Yao.jl | 0.9.3 (verified via `Project.toml` on `QuantumBFS/Yao.jl` master, `julia = "1"` compat) | Qubit-circuit statevector simulator | Actively maintained (QuantumBFS org), Apache-2.0, already selected in prior project research over QuantumInformation.jl/QuantumOptics.jl as "the most widely used/maintained circuit-first simulator in the Julia ecosystem." |
| BosonSampling.jl | 1.0.2 (verified via `Project.toml` on `benoitseron/BosonSampling.jl` main, `julia = "1"` compat) | Permanent-based exact linear-optics simulator, registered in Julia General | Confirmed still registered and installable (`Pkg.add("BosonSampling")`); published in *Quantum* (June 2024, arXiv:2212.09537) — the only Julia package in the ecosystem purpose-built for Fock-state/interferometer simulation, already selected over Ket.jl in prior project research for exactly this reason. |

### Supporting
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| (none new) | — | — | Yao.jl and BosonSampling.jl are self-contained for this phase's hello-world scope; no additional Julia packages needed. BosonSampling.jl itself transitively pulls ~33 packages (see Pitfalls) — these are its own declared dependencies, not something the plan should add manually. |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| BosonSampling.jl | Hand-rolled permanent-based simulator | Rejected — reimplementing permanent computation from scratch is exactly the kind of "don't hand-roll" work a registered, published package already solves; only fall back to this if BosonSampling.jl is a genuine no-go (matches CONTEXT's "one alternate photonic package" allowance, not a hand-rolled implementation). |
| Yao.jl | QuantumInformation.jl or QuantumOptics.jl | Both exist and could build a small qubit circuit; not needed unless Yao.jl's API proves awkward — out of scope for this decoupled, time-boxed spike. |
| `juliaup` MS Store / winget install | Manual installer download from julialang.org | This is the documented workaround if winget/juliaup itself is blocked by antivirus (see Pitfalls) — treat as the "one alternate path" for the toolchain-install component specifically, per CONTEXT's own escalation logic. |

**Installation:**
```powershell
# Recommended primary path (Windows, PowerShell):
winget install --id=Julialang.Juliaup -e
# Alternative primary path (equivalent, via MS Store):
winget install --name Julia --id 9NJNWW8PVKMN -e -s msstore

# After install, open a NEW shell (PATH change requires restart), then:
julia --version          # expect: "julia version 1.10.x" or similar

# Pin to LTS explicitly (recommended over the default "release" channel for this spike):
juliaup add lts
juliaup default lts

# Inside julia/ project directory:
julia --project=. -e 'using Pkg; Pkg.add(["Yao", "BosonSampling"])'
```

If `winget install --id=Julialang.Juliaup -e` fails or is blocked (see Pitfalls), the documented one-alternate-path fallback is the manual installer from https://julialang.org/downloads/ (this itself installs juliaup under the hood in current Julia releases) — this *is* the CONTEXT's "one alternate install method" for the toolchain-install component.

## Architecture Patterns

### Recommended Project Structure
```
julia/
├── Project.toml           # committed — declares Yao, BosonSampling as deps
├── Manifest.toml           # gitignored — environment-specific lockfile (per CONTEXT decision)
├── README.md               # install juliaup, activate project, run hello-world scripts
├── hello_yao.jl             # named, reusable — Bell-state circuit + assertion
└── hello_bosonsampling.jl   # named, reusable — 2-mode beamsplitter + assertion
```

### Pattern 1: Project-scoped environment via `Pkg.activate`
**What:** Run everything with `julia --project=julia/` (or `Pkg.activate("julia")` inside a script) rather than adding packages to the global Julia environment.
**When to use:** Always, for any multi-package Julia project — this is standard Julia convention, directly analogous to this project's existing Python `venv`.
**Example:**
```julia
# Source: standard Julia Pkg workflow (docs.julialang.org)
using Pkg
Pkg.activate("julia")          # or run julia with --project=julia
Pkg.add(["Yao", "BosonSampling"])
Pkg.status()                    # confirm resolved versions, no conflicts
```
Running `julia --project=julia/ julia/hello_yao.jl` from repo root is the equivalent of activating a venv and running a script — no global state pollution, and `Project.toml` alone (committed) is enough for anyone to reproduce the environment via `Pkg.instantiate()`.

### Pattern 2: Version/package-version banner as first line of output
**What:** Print `VERSION` (Julia) and the installed package version (via `Pkg.dependencies()` or `pkgversion(Yao)`/`pkgversion(BosonSampling)`) at the top of each hello-world script.
**When to use:** Per CONTEXT's explicit decision — cheap, useful evidence for the write-up and future reproducibility.
**Example:**
```julia
println("Julia: ", VERSION)
println("Yao: ", pkgversion(Yao))   # Julia ≥1.9 built-in; returns a VersionNumber
```

### Anti-Patterns to Avoid
- **Installing packages into the global Julia environment:** Makes the spike non-reproducible and risks version drift affecting Phase 19's later work. Always use the `julia/` project environment.
- **Committing `Manifest.toml`:** Contradicts CONTEXT's explicit decision (gitignore it) and standard Julia convention — Manifest is a lockfile tied to the exact resolved dependency graph, not something meant for review/diffing in this kind of spike.
- **Asserting only that a script "ran without erroring":** CONTEXT explicitly requires assertion against a known analytical value, not just execution — a script that runs and prints output but never checks the number against physics is not proof of correctness.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| 2-mode beamsplitter unitary + permanent-based output probability | A custom Julia function computing permanents/probabilities by hand | BosonSampling.jl's `beam_splitter(t)` (returns the 2×2 unitary) + `Input`/`UserDefinedInterferometer`/`FockDetection`/`Event`/`compute_probability!` pipeline | This is precisely the "existing solution" this phase exists to validate — hand-rolling it defeats the point of the spike (proving the package works), and BosonSampling.jl's permanent evaluation is exactly the independently-implemented method Phase 19's cross-check needs to differ from Perceval's SLOS backend. |
| Bell-state circuit + measurement statistics | A custom Julia statevector simulator | Yao.jl's `chain`/`put`/`control`/`zero_state`/measurement pipeline | Same reasoning — the whole point is confirming Yao.jl itself works, not reimplementing a 2-qubit statevector simulator by hand (which would also be a strictly weaker cross-check for Phase 19, since it wouldn't be "a different simulation engine"). |

**Key insight:** This entire phase is a "does the existing solution work" check, not an implementation phase — any hand-rolled physics code here would undermine the phase's own purpose (proving external, independent tooling is usable) as well as Phase 19's later cross-check value.

## Common Pitfalls

### Pitfall 1: Antivirus/endpoint protection kills juliaup's unsigned binaries
**What goes wrong:** juliaup's installer and/or the `julia`/`juliaup` executables it drops are unsigned; consumer and enterprise antivirus products have been observed quarantining or blocking them outright, causing the install to silently fail or `julia` to not appear on PATH. Confirmed as an open, acknowledged issue on the juliaup GitHub repo (`JuliaLang/juliaup#736`).
**Why it happens:** juliaup (Rust-based) does not currently code-sign its Windows binaries.
**How to avoid:** If `winget install --id=Julialang.Juliaup -e` fails or `julia --version` doesn't resolve after a shell restart, check Windows Security / antivirus quarantine logs before assuming a different problem. The documented workaround — and this phase's "one alternate path" for the toolchain-install component per CONTEXT — is the manual installer from julialang.org.
**Warning signs:** Install command reports success but `julia` is not on PATH in a new shell; Windows Security notification around the time of install; `juliaup` command not found despite winget reporting a completed install.

### Pitfall 2: Windows Defender Application Control (WDAC) blocks precompiled package images
**What goes wrong:** Julia's `pkgimages` feature compiles packages to locally-cached native `.dll` files; these are unsigned and generated in user-writable directories, which WDAC policies (common on managed/corporate Windows machines) block from executing, with "no graceful fallback" per the open upstream issue (`JuliaLang/julia#61252`).
**Why it happens:** WDAC treats unsigned DLLs from user-writable paths as untrusted by design — this is a security policy working as intended, not a bug, but Julia's package precompilation model runs directly into it.
**How to avoid:** Less likely to bite on a personal (non-corporate-managed) Windows machine, but worth a fast check if `using Yao` or `using BosonSampling` fails with a cryptic DLL/precompilation error rather than a clean package error — check whether WDAC/Smart App Control is enabled (`Get-CimInstance -ClassName Win32_DeviceGuard` or Windows Security > App & browser control).
**Warning signs:** Package `add` succeeds but `using PackageName` fails with an obscure native-library/precompilation error rather than a Julia-level error.

### Pitfall 3: BosonSampling.jl's dependency tree (ITensors.jl) has a real history of Windows precompilation failures
**What goes wrong:** BosonSampling.jl's `Project.toml` declares ~33 dependencies including `ITensors`, `Luxor`, `Plots`, and `JLD` — a genuinely heavy install for a "hello-world" spike. ITensors.jl specifically has multiple open/recent GitHub and Discourse threads reporting Windows-specific precompilation failures (e.g. `TypeParameterAccessors` KeyError, `Base.sort` conflicts) that cluster around newer/beta Julia versions.
**Why it happens:** Large transitive dependency graphs increase the surface area for any one package's precompilation to fail on a given OS/Julia-version combination; ITensors.jl's issue history shows this is a recurring, not one-off, pattern.
**How to avoid:** Pin to Julia 1.10 LTS (not `release`/beta) before attempting `Pkg.add("BosonSampling")` — the reported failures skew toward 1.10-beta/1.11. Budget real wall-clock time for this install specifically within the one-day box (first `using BosonSampling` after `Pkg.add` triggers precompilation of the full dependency tree, which can take several minutes even without errors). If it does fail at precompile time (not at `Pkg.add`/resolve time), that's a strong, fast signal of exactly this pitfall — the CONTEXT's "one alternate photonic package" branch should trigger here rather than extended troubleshooting of ITensors internals.
**Warning signs:** `Pkg.add("BosonSampling")` succeeds (dependency resolution worked) but `using BosonSampling` fails or hangs for a long time; error output mentioning `ITensors`, `NDTensors`, or `TypeParameterAccessors`.

### Pitfall 4: PowerShell execution policy blocking a script-based install (only if the script-download path is used)
**What goes wrong:** If the manual/alternate install path involves running a downloaded PowerShell install script (rather than the `winget` MSIX path or the `.exe` installer), Windows' default `Restricted` execution policy blocks it outright.
**Why it happens:** Default Windows PowerShell execution policy disallows running unsigned/downloaded `.ps1` scripts.
**How to avoid:** Prefer `winget` or the `.exe`/MSI installer (neither requires changing execution policy) as the primary path; this is why they're recommended as primary over any script-based install method for this spike.
**Warning signs:** `... cannot be loaded because running scripts is disabled on this system` error.

## Code Examples

Verified/corroborated patterns (Yao.jl API cross-checked across `quick-start.md` and the GHZ example page; BosonSampling.jl API cross-checked across the "Basic usage" tutorial page and the published paper's Code Sample 3.1 — both independently produced the same `Input`/`Interferometer`/`FockDetection`/`Event`/`compute_probability!` pipeline):

### Yao.jl hello-world: Bell state via H + CNOT, asserted against analytical probabilities
```julia
# Source: QuantumBFS/Yao.jl quick-start.md + GHZ example (docs.yaoquantum.org),
# corroborated across two independently-fetched pages — MEDIUM-HIGH confidence,
# not yet locally executed.
using Yao

println("Julia: ", VERSION)
println("Yao: ", pkgversion(Yao))

# H on qubit 1, then CNOT with control=1, target=2  ->  (|00> + |11>)/sqrt(2)
bell_circuit = chain(2, put(1=>H), control(1, 2=>X))
reg = zero_state(2) |> bell_circuit

# Exact statevector-derived probabilities (no shot noise) for the assertion:
p = probs(reg)                      # length-4 vector, Yao's bit-order convention
@assert isapprox(p[1], 0.5; atol=1e-10)   # |00>
@assert isapprox(p[4], 0.5; atol=1e-10)   # |11>
@assert isapprox(p[2], 0.0; atol=1e-10)   # |01>
@assert isapprox(p[3], 0.0; atol=1e-10)   # |10>
println("Bell state probabilities: ", p, " -- matches analytical (0.5, 0, 0, 0.5)")
```
**Note on confidence:** `control(1, 2=>X)` syntax (control qubit, `target=>gate` pair) is directly confirmed from the official GHZ example (`control(2, 1=>X)` pattern). `probs(reg)` returning the exact `|amplitude|²` vector from an `ArrayReg` is standard Yao.jl API per training knowledge and partially corroborated by search results describing `probs()` returning `|⟨x|ψ⟩|²`; **this specific call was not independently verified against current docs and should be the first thing confirmed once Julia is actually installed** — if `probs` isn't exported at top level, `Yao.YaoArrayRegister.probs` or `abs2.(statevec(reg))` are the fallback equivalents.

### BosonSampling.jl hello-world: 2-mode beamsplitter on |1,0⟩, asserted against analytical probabilities
```julia
# Source: benoitseron/BosonSampling.jl "Basic usage" tutorial +
# arXiv:2212.09537 Code Sample 3.1 (published paper) — corroborated across
# two independently-fetched sources — MEDIUM-HIGH confidence, not yet
# locally executed. Uses the verified-from-source `beam_splitter()` function
# (src/circuits/circuit_elements.jl) rather than the paper's capitalized
# `BeamSplitter(...)` call, which could not be independently confirmed to
# exist as a separate constructor in current source — safer fallback.
using BosonSampling

println("Julia: ", VERSION)
println("BosonSampling: ", pkgversion(BosonSampling))

t = 1/sqrt(2)                                  # 50/50 beamsplitter, transmission amplitude
U = beam_splitter(t)                           # 2x2 unitary: [[t -r]; [r t]], r = sqrt(1-t^2)
interf = UserDefinedInterferometer(U)

input_state = Input{Bosonic}(ModeOccupation([1, 0]))  # |1,0>

# Assert against analytical single-photon beamsplitter statistics: P(transmitted)=|t|^2=0.5
out_transmitted = FockDetection(ModeOccupation([1, 0]))
ev1 = Event(input_state, out_transmitted, interf)
p_transmitted = compute_probability!(ev1)
@assert isapprox(p_transmitted, 0.5; atol=1e-10)

out_reflected = FockDetection(ModeOccupation([0, 1]))
ev2 = Event(input_state, out_reflected, interf)
p_reflected = compute_probability!(ev2)
@assert isapprox(p_reflected, 0.5; atol=1e-10)

println("Beamsplitter |1,0> output probabilities: transmitted=$p_transmitted, reflected=$p_reflected -- matches analytical (0.5, 0.5)")
```
**Note on confidence:** `Input{Bosonic}(ModeOccupation(...))`, `UserDefinedInterferometer(U)`, `FockDetection(...)`, `Event(...)`, and `compute_probability!(ev)` are all directly confirmed, appearing identically in both the general tutorial fetch and the published-paper code sample fetch — this is the highest-confidence part of the BosonSampling.jl API surface found. `beam_splitter(t)` (lowercase function returning the raw 2×2 matrix) was confirmed by directly fetching `src/circuits/circuit_elements.jl` from the repo. The paper's capitalized `BeamSplitter(1/sqrt(2))` used directly as an `Interferometer` argument could not be located in current source during this research — **the plan should verify at execution time** whether a capitalized `BeamSplitter` type exists (likely a small convenience wrapper), and use it directly if so; the `UserDefinedInterferometer(beam_splitter(t))` composition above is the confirmed-safe fallback either way.

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|-------------------|---------------|--------|
| Manual Julia installer downloads, PATH management by hand | `juliaup` version manager (official, JuliaLang-maintained) | juliaup has been the recommended install path for several years; still current as of this research | Simplifies version pinning (`juliaup add lts`) but introduces the unsigned-binary/antivirus risk documented above — a real tradeoff, not a pure improvement, worth naming in the plan. |
| ket.jl for any Julia-side quantum verification in this project | Yao.jl (qubit) + BosonSampling.jl (photonic) | Decided in this project's own prior milestone research (2026-08-06, `.planning/research/STACK.md`) | Already locked before this phase's research began — this research phase confirms operational feasibility, not the choice itself. |

**Deprecated/outdated:** Bare `.exe`/MSI Julia installers still work but Julia's own docs and juliaup's README both position them as the fallback path ("serious limitations," no auto-update), consistent with the CONTEXT's framing of the manual installer as the "one alternate path," not the primary path.

## Open Questions

1. **Does BosonSampling.jl export a capitalized `BeamSplitter` interferometer constructor, or was the paper's `BeamSplitter(1/sqrt(2))` example referring to something not present in current `main` source?**
   - What we know: A lowercase `beam_splitter(transmission_amplitude)` function exists in `src/circuits/circuit_elements.jl` and returns the expected 2×2 unitary matrix. The published paper (arXiv:2212.09537, Code Sample 3.1) shows `B = BeamSplitter(1/sqrt(2))` used directly as an interferometer argument.
   - What's unclear: Whether this is a real, currently-exported type (possibly renamed/refactored since the paper's 2022 writing, given the docs site itself is dated November 2022 and the package is now at v1.0.2) or a paper-only convenience alias.
   - Recommendation: Plan should treat `UserDefinedInterferometer(beam_splitter(t))` as the confirmed-working path (verified from source) and try the capitalized form only as a quick first check, not a blocking dependency.

2. **Exact `Yao.probs()` export path and calling convention.**
   - What we know: Yao.jl documentation describes a `probs()` function returning `|⟨x|ψ⟩|²` from a register; it appears in `YaoBase`/`YaoArrayRegister` per search results.
   - What's unclear: Whether `probs` is re-exported at the top-level `Yao` namespace (so `probs(reg)` works directly after `using Yao`) without qualification.
   - Recommendation: First thing to check once Julia is installed — trivial to confirm interactively (`methods(probs)` or just try the call), low risk, but should not block the plan's task breakdown on an unverified assumption.

3. **BosonSampling.jl documentation site is dated November 2022 (Julia 1.8.2) while the package itself is at v1.0.2 — how stale is the tutorial content relative to current API?**
   - What we know: Core types (`Input`, `Interferometer` subtypes, `FockDetection`, `Event`, `compute_probability!`) are corroborated by both the docs site and the more recent published paper's code samples, suggesting this part of the API is stable.
   - What's unclear: Whether any breaking changes have occurred since Nov 2022 that aren't reflected in the still-hosted docs.
   - Recommendation: `Pkg.status()` after install plus a successful `compute_probability!` call is the fastest real-world confirmation — no further research needed before planning, this resolves itself the moment the spike is attempted.

## Sources

### Primary (HIGH confidence)
- `raw.githubusercontent.com/QuantumBFS/Yao.jl/master/Project.toml` — direct fetch, confirmed Yao.jl v0.9.3, `julia = "1"` compat.
- `raw.githubusercontent.com/benoitseron/BosonSampling.jl/main/Project.toml` — direct fetch, confirmed BosonSampling.jl v1.0.2, `julia = "1"` compat, full 33-package dependency list.
- `raw.githubusercontent.com/benoitseron/BosonSampling.jl/main/src/circuits/circuit_elements.jl` — direct fetch, confirmed `beam_splitter(transmission_amplitude=sqrt(0.5))` signature and matrix convention.
- `github.com/JuliaLang/juliaup` (README, via WebFetch) — Windows install methods (winget/MS Store primary, MSI limited/discouraged), `Windows.Web.Http` API requirement.
- `github.com/JuliaLang/juliaup/issues/736` — unsigned-binary/antivirus issue, documented manual-installer workaround.
- `github.com/JuliaLang/julia/issues/61252` — WDAC/pkgimages unsigned-DLL blocking issue.
- `.planning/research/STACK.md` (this project's own prior milestone research, 2026-08-06) — HIGH confidence, already-locked stack decision (juliaup, Julia 1.10 LTS, Yao.jl, BosonSampling.jl over Ket.jl) that this research phase builds on rather than re-derives.

### Secondary (MEDIUM confidence)
- `github.com/QuantumBFS/Yao.jl/blob/master/docs/src/quick-start.md` and `docs.yaoquantum.org/v0.4/examples/GHZ/` — corroborating fetches, confirmed `chain`/`put`/`control`/`zero_state`/`measure` API shape.
- `benoitseron.github.io/BosonSampling.jl/stable/tutorial/basic_usage.html` and `arxiv.org/html/2212.09537` (paper HTML) — corroborating fetches, confirmed `Input`/`ModeOccupation`/`Interferometer` subtypes/`FockDetection`/`Event`/`compute_probability!` pipeline identically across both independent sources.
- WebSearch, "juliaup install Windows 2026" and "Julia LTS version 2026" — confirmed current Julia 1.10.11 LTS / 1.12.6 release, consistent with prior project research from the previous day.
- WebSearch, "BosonSampling.jl ITensors Windows precompile issue" — ITensors.jl Windows precompilation failure pattern (GitHub issues, ITensor Discourse), real but not BosonSampling-specific; inferred risk by transitive dependency, not directly observed on BosonSampling.jl itself.

### Tertiary (LOW confidence)
- WebFetch AI-summarized page content (used throughout, since raw HTML often couldn't be returned verbatim) — flagged wherever a claim rests on a single summarized fetch rather than a direct source read or cross-corroboration; see Open Questions for the two specific API details that fall into this bucket.

## Metadata

**Confidence breakdown:**
- Standard stack (juliaup, Julia LTS, package versions): HIGH — both package versions and compat bounds confirmed by direct `Project.toml` reads, not just search summaries.
- Architecture (project structure, `Pkg.activate` pattern): HIGH — standard, well-documented Julia convention, already partially specified by the CONTEXT itself.
- Hello-world code examples: MEDIUM-HIGH — core API surface corroborated across 2+ independent sources for both packages, but not locally executed (Julia isn't installed in this research environment); two small open questions flagged explicitly rather than glossed over.
- Windows-specific pitfalls: MEDIUM — juliaup/WDAC issues are confirmed real, filed, open GitHub issues (not speculation), but their actual likelihood on this specific personal (non-corporate-managed) Windows machine is unverified and could be lower than the issue reports suggest.

**Research date:** 2026-08-07
**Valid until:** ~30 days (package versions/registry status could shift, but this is a one-day spike executed imminently, so staleness risk is low in practice)
