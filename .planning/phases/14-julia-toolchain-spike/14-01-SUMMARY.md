---
phase: 14-julia-toolchain-spike
plan: 01
subsystem: infra
tags: [julia, juliaup, yao.jl, bosonsampling.jl, verification-tooling]

# Dependency graph
requires: []
provides:
  - "julia/ project environment (Project.toml) declaring Yao.jl + BosonSampling.jl"
  - "julia/hello_yao.jl -- Bell-state circuit, analytically-asserted, extendable by Phase 19"
  - "julia/hello_bosonsampling.jl -- 50/50 beamsplitter circuit, analytically-asserted, extendable by Phase 19"
  - "Full-go verdict for the Julia toolchain, unblocking Phase 19's VERIFY-02/03/04 scope as originally planned"
affects: [19-independent-julia-cross-checks]

# Tech tracking
tech-stack:
  added: [juliaup, "Julia 1.10.11 LTS", "Yao.jl 0.9.1", "BosonSampling.jl 1.0.2"]
  patterns:
    - "Project-scoped Julia environment (julia --project=julia) instead of global Pkg installs, mirroring this project's Python venv convention"
    - "Version/package-version banner as first line of hello-world script output (Julia + package version)"
    - "Hand-derived analytical @assert as proof of correctness, not just successful execution"

key-files:
  created:
    - julia/Project.toml
    - julia/README.md
    - julia/hello_yao.jl
    - julia/hello_bosonsampling.jl
    - results/phase14_julia_toolchain_summary.md
  modified:
    - .gitignore
    - .planning/STATE.md

key-decisions:
  - "Julia pinned to 1.10 LTS (not release/beta channel) per research's Windows precompilation risk mitigation -- confirmed correct, no precompile failures encountered."
  - "julia/Manifest.toml and julia/.install_log_*.txt gitignored -- standard Julia convention plus this project's context-budget guidance for verbose install logs."
  - "No alternate paths were needed for any component -- both packages and the toolchain itself succeeded on their documented primary paths."

patterns-established:
  - "Pattern 2 from 14-RESEARCH.md (version banner) and Pattern 1 (project-scoped env) both directly reused -- Phase 19 should follow the same conventions when extending these scripts."

# Metrics
duration: ~50min (actual wall-clock across toolchain install, Pkg.add/precompile for both packages, script verification)
completed: 2026-08-07
---

# Phase 14: Julia Toolchain Spike Summary

**Full go: juliaup + Julia 1.10.11 LTS + Yao.jl 0.9.1 + BosonSampling.jl 1.0.2 all installed and verified via hand-derived-analytical-assertion hello-world scripts, with zero alternate-path attempts needed.**

## Performance

- **Duration:** ~50 minutes wall-clock (juliaup install + LTS pin: a few minutes; Yao.jl `Pkg.add`+precompile: ~241s; BosonSampling.jl `Pkg.add` resolve+download+precompile: ~20-25 min, of which precompilation itself was ~687s)
- **Tasks:** 3/3 completed
- **Files modified:** 6 (4 created in julia/, 1 created in results/, .gitignore + STATE.md modified)

## Accomplishments

- Installed a brand-new Julia toolchain (juliaup, Julia 1.10.11 LTS) on this Windows machine from scratch, with zero antivirus/quarantine issues (14-RESEARCH.md's Pitfall 1 did not manifest).
- Built a project-scoped `julia/` environment with Yao.jl and BosonSampling.jl as committed dependencies (`julia/Project.toml`), matching this project's existing Python-venv-style isolation convention.
- Both hello-world scripts run and pass `@assert` checks against hand-derived analytical values, not just execute:
  - `julia/hello_yao.jl`: Bell-state circuit (H + CNOT), probabilities match (0.5, 0.0, 0.0, 0.5).
  - `julia/hello_bosonsampling.jl`: 50/50 beamsplitter on `|1,0>`, probabilities match (0.5, 0.5).
- Confirmed the single biggest flagged risk (ITensors.jl's Windows precompilation failure history, 14-RESEARCH.md Pitfall 3) never materialized -- the resolved BosonSampling.jl 1.0.2 dependency tree for this environment does not include ITensors.jl at all.
- Recorded a matching **full go** verdict in both `results/phase14_julia_toolchain_summary.md` and `.planning/STATE.md`.

## Task Commits

Each task was committed atomically:

1. **Task 1: Install Julia toolchain (juliaup + Julia 1.10 LTS)** - no commit (system-level install only, no repo files modified per plan)
2. **Task 2: Julia project scaffold + Yao.jl hello-world** - `3c6342b` (feat)
3. **Task 3: BosonSampling.jl hello-world + go/no-go verdict** - `cb16335` (feat)

## Files Created/Modified

- `julia/Project.toml` - Committed environment manifest declaring Yao.jl + BosonSampling.jl deps
- `julia/README.md` - Install/activate/run instructions for the julia/ project
- `julia/hello_yao.jl` - Bell-state circuit (H + CNOT) with version banner and 4 analytical `@assert`s
- `julia/hello_bosonsampling.jl` - 50/50 beamsplitter on `|1,0>` with version banner and 2 analytical `@assert`s
- `results/phase14_julia_toolchain_summary.md` - Full go verdict, per-component detail, wall-clock time, Phase 19 implications
- `.gitignore` - Added `julia/Manifest.toml` and `julia/.install_log_*.txt`
- `.planning/STATE.md` - Verdict recorded in Blockers/Concerns and Session Continuity, position/progress updated

## Decisions Made

- Julia pinned to 1.10 LTS rather than the `release` channel, per 14-RESEARCH.md's recommendation to avoid Windows precompilation issues clustering on newer/beta versions -- confirmed to work cleanly.
- Used the confirmed-from-source `beam_splitter(t)` + `UserDefinedInterferometer(...)` composition rather than trying the paper's capitalized `BeamSplitter(...)` constructor first, since 14-RESEARCH.md flagged the latter as unconfirmed in current source -- the documented-safe path worked immediately, so the capitalized alternative was never needed (resolves 14-RESEARCH.md's Open Question 1 in practice).
- `probs(reg)` confirmed directly callable at Yao's top-level namespace with no qualification needed -- resolves 14-RESEARCH.md's Open Question 2.

## Deviations from Plan

None - plan executed exactly as written. Both the toolchain install and both packages succeeded on their primary, documented paths on the first attempt; no alternate-path branch of the plan was triggered.

One incidental observation not a deviation: adding BosonSampling.jl caused the Julia `Pkg` resolver to downgrade the already-installed Yao.jl from v0.9.3 to v0.9.1 to satisfy the combined environment's compatibility constraints. This is standard `Pkg` resolver behavior for a shared environment, not a bug or a plan deviation -- `julia/hello_yao.jl` was re-run and re-verified to still pass against v0.9.1.

## Issues Encountered

- Passing `Pkg.add("...")` calls through nested `Bash -> powershell.exe -Command -> julia -e '...'` quoting caused a misparse (`UndefVarError: Yao not defined`, then a `ParseError` on a later `println` check) because the double-quoted string content was lost across three levels of shell quoting. Resolved by writing small throwaway `.jl` script files (`julia/_add_yao.jl`, `julia/_add_bs.jl`, `julia/_check_load.jl`) and invoking `julia --project=julia <script>.jl` directly instead of `-e`, then deleting them once no longer needed. Not a plan deviation -- purely a shell-quoting workaround, and none of these throwaway files are part of the committed repo.

## User Setup Required

None - no external service configuration required. Julia toolchain is installed locally on this machine; `julia/README.md` documents the reproduction steps for anyone else.

## Next Phase Readiness

- Phase 19 (Independent Julia Cross-Checks) can proceed with its originally planned scope (VERIFY-02 qubit-side via Yao.jl, VERIFY-03/04 photonic-side via BosonSampling.jl) -- no re-opened scope conversation with the owner is needed, since this is a full go, not a partial go or no-go.
- `julia/hello_yao.jl` and `julia/hello_bosonsampling.jl` are ready to be extended by Phase 19 rather than started from zero, per this project's established pattern of building on prior phases' modules.
- One forward-looking note for Phase 19: the shared `julia/` environment currently pins Yao.jl to v0.9.1 (resolver-downgraded from v0.9.3 by BosonSampling.jl's compatibility constraints) -- expected behavior, not a blocker, but worth knowing if Phase 19 needs a specific Yao.jl feature only present in later 0.9.x releases.

---
*Phase: 14-julia-toolchain-spike*
*Completed: 2026-08-07*
