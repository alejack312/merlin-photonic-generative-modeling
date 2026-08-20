---
phase: 14
phase_name: "Julia Toolchain Spike"
project: "MerLin Photonic Generative Modeling"
generated: "2026-08-20"
counts:
  decisions: 5
  lessons: 4
  patterns: 4
  surprises: 4
missing_artifacts:
  - "14-UAT.md"
---

# Phase 14 Learnings: Julia Toolchain Spike

## Decisions

### Pin Julia to 1.10 LTS, not the `release` channel
Installed via `juliaup add lts; juliaup default lts` rather than tracking the bleeding-edge `release` channel (1.12.6 at research time).

**Rationale:** Research found Windows precompilation failures (specifically ITensors.jl, a transitive dependency of BosonSampling.jl) cluster on newer/beta Julia versions. Fewer moving parts this close to the project deadline was also weighed explicitly.
**Source:** 14-01-PLAN.md (Task 1), 14-RESEARCH.md (Pitfall 3), 14-01-SUMMARY.md (confirmed correct, no precompile failures encountered)

---

### New top-level `julia/` directory, sibling to `generator/`/`tests/`/`docs/`
Not nested under `.planning/`, not scratch — treated as a first-class project directory from the start.

**Rationale:** `julia/README.md` and the hello-world scripts are meant to be referenced by Phase 19 and the eventual project write-up, so they were written as real, permanent artifacts rather than disposable spike code.
**Source:** 14-CONTEXT.md (Repo structure & integration)

---

### Project-scoped Julia environment (`julia --project=julia`), never global
Mirrors this project's existing Python `venv` isolation convention. `Project.toml` is committed; `Manifest.toml` is gitignored (added to the repo's single root `.gitignore`).

**Rationale:** Keeps the spike reproducible and isolated from Phase 19's later work; Manifest.toml is an environment-specific lockfile, not something meant for review/diffing, per standard Julia convention.
**Source:** 14-RESEARCH.md (Pattern 1, Anti-Patterns), 14-01-PLAN.md (Task 2), 14-01-SUMMARY.md

---

### Hello-world scripts must assert against hand-derived analytical values, not just execute
Both `hello_yao.jl` (Bell-state, H+CNOT) and `hello_bosonsampling.jl` (50/50 beamsplitter on |1,0⟩) use `@assert isapprox(...; atol=1e-10)` against physics-derived expected probabilities, explicitly forbidding "ran without erroring" as sufficient proof.

**Rationale:** CONTEXT explicitly required this — a script that runs and prints output but never checks the number against physics is not proof the toolchain actually works correctly, only that it didn't crash.
**Source:** 14-CONTEXT.md (Hello-world scope & proof of success), 14-RESEARCH.md (Anti-Patterns to Avoid)

---

### Partial-failure handling: split outcome is "partial go," not automatic no-go; one alternate-path cap per component
If one package works and the other doesn't, that's reported precisely as partial go (e.g., Yao.jl works → Phase 19's VERIFY-02 can proceed even if VERIFY-03/04 can't). Each component (toolchain install, BosonSampling.jl) gets exactly one alternate-path attempt before being called a no-go — never a second or third.

**Rationale:** Prevents open-ended troubleshooting/yak-shaving that caused the prior PennyLane track to stall indefinitely at an equivalent stage; makes go/no-go a genuinely time-boxed, honest signal rather than a soft "still working on it."
**Source:** 14-CONTEXT.md (Partial-failure handling, Time-box & go/no-go trigger)

---

## Lessons

### Nested shell quoting (Bash → powershell.exe → julia -e) silently corrupts inline Julia code
Passing `Pkg.add("...")` and check calls through `julia -e '...'` nested three levels deep (Bash tool → `powershell.exe -Command` → Julia's own `-e` flag) caused string content to be lost, producing misleading errors (`UndefVarError: Yao not defined`, then a `ParseError` on a later `println`) that looked like a Julia/package problem but were actually a shell-quoting problem.

**Context:** Encountered while running `Pkg.add` for Yao and BosonSampling from this Windows environment during Task 2/3 execution.
**Source:** 14-01-SUMMARY.md (Issues Encountered)

---

### `Pkg`'s resolver can silently downgrade an already-installed package when a second package is added to the same environment
Adding BosonSampling.jl to the shared `julia/` environment caused the resolver to downgrade the already-installed Yao.jl from v0.9.3 to v0.9.1 to satisfy combined compatibility constraints — standard `Pkg` behavior, not a bug, but easy to mistake for something broken if the version isn't re-checked.

**Context:** Discovered when re-verifying `hello_yao.jl` after adding BosonSampling.jl; re-run confirmed it still passed against v0.9.1. Worth knowing for Phase 19 if it needs a Yao.jl feature only present in later 0.9.x releases.
**Source:** 14-01-SUMMARY.md (Deviations from Plan, Next Phase Readiness)

---

### The two Open Questions flagged in research resolved themselves cleanly on first execution
Research flagged two unverified API details as risks going into planning: (1) whether BosonSampling.jl exports a capitalized `BeamSplitter` constructor or only the lowercase `beam_splitter()` function, and (2) whether `probs(reg)` is callable at Yao's top-level namespace without qualification. Both were confirmed in practice on the first attempt — the documented-safe fallback path (`UserDefinedInterferometer(beam_splitter(t))`) worked immediately, and `probs(reg)` needed no qualification.

**Context:** These were explicitly called out in 14-RESEARCH.md as "should be the first thing confirmed once Julia is actually installed," not blocking assumptions — treating them as fallback-covered rather than hard blockers meant the plan didn't stall waiting for pre-execution certainty.
**Source:** 14-01-SUMMARY.md (Decisions Made), 14-RESEARCH.md (Open Questions 1 and 2)

---

### The single biggest flagged research risk (ITensors.jl Windows precompilation failure) never materialized
Research's top concern was that BosonSampling.jl's ~33-package dependency tree includes ITensors.jl, which has a real, filed history of Windows-specific precompilation failures. In practice, the resolved dependency tree for this environment (BosonSampling.jl 1.0.2 under Julia 1.10.11 LTS) did not include ITensors.jl at all.

**Context:** Suggests the risk was version/dependency-graph-specific rather than inherent to the package, and that pinning to LTS (as decided) may have sidestepped it entirely rather than merely mitigating it.
**Source:** 14-01-SUMMARY.md (Accomplishments)

---

## Patterns

### Time-boxed, decoupled toolchain spike as an explicit stall-risk checkpoint
Sequence an unfamiliar toolchain's install-and-hello-world validation as its own fully decoupled phase, placed early in the milestone, with a hard one-calendar-day time-box covering the whole spike (not per-component) and a mandatory recorded go/no-go/partial-go verdict — before any real implementation work depends on that toolchain.

**When to use:** Any time a project is about to commit to an unfamiliar framework/language/toolchain for a load-bearing piece of work, especially if the project has a documented history of stalling on a previous unfamiliar-toolchain adoption (here: the PennyLane track). Deliberately mirrors this project's own v1.0 Jul-25 precedent.
**Source:** 14-CONTEXT.md (Phase Boundary), 14-01-PLAN.md (objective)

---

### One-alternate-path cap, enforced per component, as the concrete anti-yak-shaving mechanism
For each independently-failable component (toolchain install, each package), explicitly allow exactly one fallback approach before calling that component a no-go and moving on — never a second or third attempt, and never open-ended troubleshooting of library internals (e.g., explicitly ruled out "extended troubleshooting of ITensors internals").

**When to use:** Any time-boxed spike/checkpoint phase where the risk is indefinite stalling rather than technical difficulty per se. Pairs with recording the actual error text that triggered the alternate attempt, so the record stays honest and diagnosable later.
**Source:** 14-CONTEXT.md (Time-box & go/no-go trigger), 14-01-PLAN.md (Task 1, Task 3 guard clauses)

---

### Dual-recorded go/no-go verdict (results file + STATE.md), word-for-word matching
Record the same verdict term ("FULL GO" / "PARTIAL GO" / "NO GO") in both a phase-level results summary (`results/phaseN_*_summary.md`) and the project's `.planning/STATE.md`, explicitly checked to match word-for-word rather than just "compatible in spirit."

**When to use:** Any phase whose outcome gates a later phase's scope — makes the verdict directly checkable at a later milestone checkpoint without re-deriving it from scattered notes. Reused verbatim from this project's own Phase 7 precedent.
**Source:** 14-CONTEXT.md (Partial-failure handling), 14-01-PLAN.md (key_links), 14-VERIFICATION.md (Key Link Verification)

---

### Redirect verbose install/precompile logs to a gitignored throwaway file, inspect only the tail
`Pkg.add`/precompile output for large dependency trees (BosonSampling.jl's ~33 packages) piped to `julia/.install_log_<pkg>.txt | tail -30` instead of dumped inline, keeping agent context usage low during long installs while still preserving full logs on disk for diagnosis if something fails.

**When to use:** Any long-running install/build/precompile step during agent-driven execution where the full output would be hundreds of lines and mostly noise.
**Source:** 14-01-PLAN.md (time_box), 14-01-PLAN.md (Task 2, Task 3 command examples)

---

## Surprises

### Zero alternate-path attempts needed across the entire spike
Every documented risk (antivirus/unsigned-binary quarantine blocking juliaup, WDAC blocking precompiled package images, ITensors.jl Windows precompilation failures, the two open API questions) was flagged as plausible in research, yet none materialized — toolchain install, Yao.jl, and BosonSampling.jl all succeeded on their primary, documented paths on the first attempt.

**Impact:** The entire spike completed in ~50 minutes wall-clock against a one-calendar-day time-box, with no contingency logic exercised — the phase's stall-risk-checkpoint design was never actually tested against a real failure in this run, though the plan/verification confirmed the contingency paths were fully specified and ready.
**Source:** 14-01-SUMMARY.md (Deviations from Plan, Performance), 14-VERIFICATION.md (Observable Truth #4, "VERIFIED (not triggered)")

---

### BosonSampling.jl install/precompile took ~20-25 minutes, the dominant share of total time
Of the ~50-minute total, BosonSampling.jl's `Pkg.add` resolve+download+precompile alone accounted for roughly 20-25 minutes (precompilation itself ~687s / ~11.5 min), versus Yao.jl's ~241s (~4 min) and a few minutes for the toolchain install itself.

**Impact:** Confirms research's warning to "budget real wall-clock time" for BosonSampling.jl specifically was well-founded even though it didn't fail — a naive assumption that failure was the only thing to budget time for would have underestimated total spike duration.
**Source:** 14-01-SUMMARY.md (Performance)

---

### Shell-quoting broke Julia inline-eval calls, not the Julia toolchain itself
The one real execution snag (`UndefVarError: Yao not defined`, then a `ParseError`) was misleading on its face — it looked like a Yao.jl/package problem but was actually three levels of shell quoting (Bash → `powershell.exe -Command` → `julia -e`) corrupting the string. Resolved by writing throwaway `.jl` script files and invoking them directly instead of using `-e`.

**Impact:** None of the phase's anticipated risks (antivirus, WDAC, ITensors) were the actual friction point encountered — the real issue was environment/tooling plumbing specific to this agent's Windows/PowerShell/Bash execution chain, not the Julia ecosystem itself. Worth remembering for any future agent-driven Julia work on this machine: prefer script files over `-e` for anything beyond trivial one-liners.
**Source:** 14-01-SUMMARY.md (Issues Encountered)

---

### `Pkg`'s cross-package resolver downgrade was silent and easy to miss
Adding a second package (BosonSampling.jl) to an environment that already had a working, verified package (Yao.jl) silently changed that package's resolved version (0.9.3 → 0.9.1) as a side effect of dependency resolution — not flagged as an error or warning requiring action, just standard resolver behavior.

**Impact:** Required an extra, unplanned-for re-verification step (re-running `hello_yao.jl` after BosonSampling.jl was added) to confirm the downgrade didn't silently break the already-passing Yao.jl hello-world. Left as an explicit forward-looking note for Phase 19 in case it needs a Yao.jl 0.9.3-only feature.
**Source:** 14-01-SUMMARY.md (Deviations from Plan, Next Phase Readiness)
