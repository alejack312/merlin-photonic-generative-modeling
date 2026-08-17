# Phase 19: Independent Julia Cross-Checks - Context

**Gathered:** 2026-08-17
**Status:** Ready for planning

<domain>
## Phase Boundary

Independently cross-check the Python/Perceval pipeline's exact and lossy distributions using the Julia toolchain confirmed working in Phase 14 (Yao.jl for qubit-side IQP, BosonSampling.jl for photonic-level). VERIFY-02, VERIFY-03, VERIFY-04. This is reproduction/verification work against already-shipped Python results, not new science, and is deliberately kept narrow per `PITFALLS.md` Pitfall 23 (avoid returning to the Julia toolchain multiple times).

</domain>

<decisions>
## Implementation Decisions

### VERIFY-02 — Yao.jl qubit-side IQP reference reproduction
- Reproduce at n=2 **and** n=3 (matches the depth Phase 9's exact-reference validation used — TVD ~1e-16 at n=2,3 — rather than stopping at the success criterion's literal minimum of n=2).
- Tolerance: same bar as Phase 12's locked gate — TVD ≤ 1e-6, ideally far below (both sides are exact, non-sampling computations, so a tight bar is achievable).

### VERIFY-03 — BosonSampling.jl photonic-level reproduction
- Cover **both** weight-1 and weight-2 (full parity with what Phases 11-13 validated in Python), not just the success criterion's "and/or" minimum.
- Build the Julia-side circuits **independently** from BosonSampling.jl's own API/docs (Julia-native idioms), not a mechanical port of Perceval's circuit structure — this is what makes it a real independence check rather than replaying the same bug in two languages.
- Use the **same test inputs** as the Python side (same input Fock state, same params) so results are directly comparable number-for-number.
- Tolerance: same TVD ≤ 1e-6 bar as VERIFY-02.

### VERIFY-04 — Loss-model cross-check against Phase 18's TVD-vs-η dataset
- Use BosonSampling.jl's **own native loss/noise API** if it has one (strongest independence guarantee — an independently-implemented loss mechanism, not Perceval's math replayed in Julia). Research this first; if no native API exists, this falls to Claude's discretion (see below).
- Cross-check **2-3 η values** spread across Phase 18's 7-point grid (not just the success criterion's literal minimum of 1).
- Cover **both** weight-1 and mixed/weight-2 generator scope (full parity with what Phase 18 reported, including herald-compounding behavior).
- Use **n=2 only** — smallest tractable size; the point is cross-implementation agreement, not re-establishing a full n-sweep.
- Tolerance: same tight TVD ≤ 1e-6 bar as the exact case (owner explicitly chose not to loosen this for the loss comparison).

### Disagreement handling (applies to all of VERIFY-02/03/04)
- If Julia and Python disagree beyond tolerance: time-box a debugging attempt first — **a few focused hours / one session** to check obvious culprits (mode ordering, normalization, loss-parameter convention mismatch) — then report as a documented disagreement if unresolved, following this project's established honesty norm (HARD-04, GEN-07, Phase 7's neighbor-locality precedent). Do not grind indefinitely.

### Stop conditions & phase structure
- If any piece's Julia porting proves harder than expected, follow Phase 14's go/no-go template: report plainly if a time-box is blown rather than struggling open-endedly.
- VERIFY-02, VERIFY-03, and VERIFY-04 are **independently gradeable** — a stall on one (e.g. the weight-2 BosonSampling.jl port) does not block the others from shipping and being reported complete. A stalled piece is reported honestly as partial-go, consistent with this milestone's overall decoupling philosophy (Pitfall 25).
- No fixed overall time budget for the phase — the narrow scope decided above (n=2/3, 2-3 η values, n=2 for loss) is the control mechanism, not a separate clock.

### Claude's Discretion
- If BosonSampling.jl has no native loss/noise API, how to construct the lossy distribution in Julia (e.g. hand-attenuating the exact distribution) is Claude's call — research the actual library capability first, don't presuppose.
- Exact severity threshold for "how much a disagreement is worth investigating further" within the few-hours debug budget (near-miss suggesting a units/convention bug vs. wildly-off result).

</decisions>

<specifics>
## Specific Ideas

- Reuse Phase 14's confirmed environment/versions as-is: Julia 1.10.11 LTS, Yao.jl 0.9.1, BosonSampling.jl 1.0.2 — no need to re-verify toolchain installation from scratch before starting.
- The "independent build from API, not mechanical port" principle for VERIFY-03 is the single most load-bearing decision in this phase — it's what makes the cross-check meaningful rather than cosmetic.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 19-independent-julia-cross-checks*
*Context gathered: 2026-08-17*
