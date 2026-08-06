# Phase 14: Julia Toolchain Spike - Context

**Gathered:** 2026-08-07
**Status:** Ready for planning

<domain>
## Phase Boundary

Confirm the Julia toolchain (`juliaup`, Yao.jl, BosonSampling.jl) installs and runs a hello-world circuit successfully. This is deliberately this milestone's earliest, most decoupled phase — a stall-risk checkpoint (mirroring v1.0's Jul-25 precedent), not implementation work. The goal is a clean go/no-go signal, produced fast, not a polished Julia integration. Independent VERIFY-02/03/04 cross-check work (reusing this toolchain against real Python-side numbers) is Phase 19's job, not this phase's.

</domain>

<decisions>
## Implementation Decisions

### Time-box & go/no-go trigger
- One calendar day total for the entire spike (juliaup + Yao.jl + BosonSampling.jl combined) — not per-component. Allows overnight troubleshooting but not multi-day drift.
- If a component stalls, try exactly one alternate path, then stop — don't chase a third option or yak-shave.
- If `juliaup` itself fails, trying one alternate install method (e.g. the official Julia installer) *is* that one alternate-path attempt. If that also fails, it's a full no-go — Yao.jl/BosonSampling.jl are never reached.
- If the day is exhausted with a genuine no-go, report it plainly (this project's established honesty norm), then explicitly re-open the risk conversation with the owner about Phase 19/VERIFY-02..04 scope — do not silently redefine scope or quietly drop the requirement.

### Repo structure & integration
- New top-level `julia/` directory, sibling to `generator/`, `tests/`, `docs/` — not scratch, not nested under `.planning/`.
- Commit `Project.toml`; gitignore `Manifest.toml` (standard Julia convention — Manifest is environment-specific lockfile noise).
- Add a minimal `julia/README.md`: how to install juliaup, activate the project, run the hello-world scripts. Written now since Phase 19 and the eventual write-up will reference this directory.
- Hello-world scripts are named, reusable files (e.g. `julia/hello_yao.jl`, `julia/hello_bosonsampling.jl`) — treated as the first real artifacts in `julia/`, not disposable scratch. Phase 19 extends these rather than starting from zero, matching this project's existing pattern of building on prior phases' modules.

### Hello-world scope & proof of success
- Both hello-world scripts must run **and assert a known expected value** — not just execute and print. Yao.jl: an analytically-known circuit (e.g. Bell state measurement statistics). BosonSampling.jl: a 2-mode beamsplitter on a simple Fock input (e.g. `|1,0⟩`) asserted against its known analytical output probabilities.
- Assertions are against **hand-derived/analytical values only** — no cross-check against Python/Perceval output in this phase. Keeps Phase 14 fully decoupled per the roadmap's explicit design; Perceval cross-checking is Phase 19's VERIFY-02/03 job.
- Scripts print Julia version and installed package (Yao.jl/BosonSampling.jl) versions on run — cheap, useful evidence for the write-up and future reproducibility.

### Partial-failure handling
- A split outcome (one package works, the other doesn't) is a **partial go**, not an automatic full no-go. Report precisely which half works and which is blocked (with the actual error). E.g. if Yao.jl works but BosonSampling.jl doesn't, Phase 19's VERIFY-02 (qubit-side) can still proceed even if VERIFY-03/04 (photonic-side) can't yet.
- If BosonSampling.jl specifically fails fast (e.g. package unavailable for the installed Julia version), it's worth trying exactly one alternative photonic-simulation Julia package within the same one-day box before writing off the photonic-side verification. Not a general package search — one candidate, then stop.
- The go/no-go verdict (full, partial, or no-go) is recorded in both `STATE.md` and a phase-level results note (e.g. `results/phase14_*_summary.md`), following this project's existing pattern from Phase 7 — so it's directly checkable at the Aug 20 milestone checkpoint, which explicitly asks whether the toolchain installed and ran a hello-world circuit.

### Claude's Discretion
- Exact Julia version to target/pin.
- Exact circuit chosen for the Yao.jl hello-world (any analytically-tractable small qubit circuit with a measurement is fine).
- Internal script structure/style within `julia/` beyond the two named hello-world files.

</decisions>

<specifics>
## Specific Ideas

No specific product/UX references — this is a CLI/tooling spike. The closest anchor is this project's own precedent: Phase 7's `results/phase7_*_summary.md` pattern for recording a measured verdict, and v1.0's Jul-25 stall-risk-checkpoint template for what "a real go/no-go signal, not silent drift" looks like in practice.

</specifics>

<deferred>
## Deferred Ideas

- Formal cross-check of Julia hello-world output against Python/Perceval numbers — that's Phase 19 (VERIFY-02/03), explicitly deferred here to keep Phase 14 decoupled.
- Evaluating multiple alternative photonic-simulation Julia packages if BosonSampling.jl fails — only one alternate attempt is in scope for this phase; broader package evaluation would be a separate decision if BosonSampling.jl turns out to be a genuine no-go.

</deferred>

---

*Phase: 14-julia-toolchain-spike*
*Context gathered: 2026-08-07*
