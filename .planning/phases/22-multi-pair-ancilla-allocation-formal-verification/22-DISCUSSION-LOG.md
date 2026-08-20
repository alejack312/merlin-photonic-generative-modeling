# Phase 22: Multi-Pair Ancilla Allocation — Formal Verification - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-20
**Phase:** 22-multi-pair-ancilla-allocation-formal-verification
**Areas discussed:** Gate family scope, Bound choice for the Forge model, Allocation scheme (MPAIR-01), Fallback on non-convergence

---

## Gate family scope

| Option | Description | Selected |
|--------|-------------|----------|
| CP(α) family only | 4 ancilla/pair, post-selection. Direct extension of ARB-09's already-shipped model. Matches the owner's original mode formula. | ✓ |
| heralded_cz family only | 2 ancilla/pair, herald-registered. Cheaper per pair, but fixed at π/4. | |
| Both, one scheme generalized over both | One allocation formula parameterized by ancilla-count-per-pair, covering both families. | |

**User's choice:** CP(α) family only.
**Notes:** Initially selected on the strength of matching the owner's own original mode formula. Owner then explicitly asked which option would showcase Forge strongest and be most meaningful for research — re-examined rather than left as a formula-match rationalization. Finding: CP(α)'s 4-ancilla-per-pair footprint is the larger combinatorial object (~4× the pairwise-distinctness constraints of heralded_cz's 2-ancilla variant) — the harder instance of the same problem. Also more research-meaningful: heralded_cz's fixed π/4 would force identical coupling on every pair, while CP(α)'s arbitrary-θ freedom is what a real future multi-pair circuit needs for heterogeneous coupling. "Both generalized" was explicitly considered and rejected: herald-registration and post-selection-filtering are physically different bookkeeping mechanisms (a herald failure is a distinguishable click; post-selection is a silent discard), so abstracting an ancilla-count parameter across both would produce a model claiming coverage it doesn't structurally have. Choice reaffirmed on both axes, not just the original formula match.

---

## Bound choice for the Forge model

| Option | Description | Selected |
|--------|-------------|----------|
| n≤8, k up to all C(n,2) pairs | Matches ARB-09's n-bound, pushes k to its ceiling — the scenario that stresses subset combinatorics, with real risk of an intractable solve. | ✓ |
| n≤6, k≤4 | Smaller n, capped k — bounded runtime, still exercises genuine subset reasoning. | |
| Claude picks a bound empirically | Start small, increase until a runtime ceiling is crossed, lock that as the justified bound. | |

**User's choice:** n≤8, k up to all C(n,2) pairs — the maximal, most-at-risk option.
**Notes:** Owner picked this knowing it carries real intractability risk (flagged explicitly in the option description before selection).

---

## Allocation scheme (MPAIR-01 — attempt-first gate)

| Option | Description | Selected |
|--------|-------------|----------|
| Contiguous: pair m → 2n+4m..2n+4m+3 | Fixed per pair index, independent of which other pairs are active. Likely disjoint by construction (same shape as ARB-09's own finding). Cheapest to eventually implement. | |
| Pooled/recycled: ancilla modes reused across non-overlapping pairs | Mode count grows sub-linearly with k instead of 4/pair. Safety of a pair's block depends on which other pairs are simultaneously active — genuine subset-dependence. | ✓ |
| Interleaved (round-robin ancilla assignment) | A third fixed-by-index variant, same likely-true-by-construction shape as contiguous, no identified advantage. | |

**User's choice:** Pooled/recycled.
**Notes:** This is the area where the attempt-first gate had to be enforced explicitly. The owner's first response ("let's proceed with what Opus outlined") restated the contiguous scheme from a prior Claude/Opus session's proposal (pasted verbatim into the `/gsd-new-milestone` invocation that scoped this phase) rather than a genuinely independent selection among alternatives. This was named directly: the pasted framing was Claude's own prior proposal, not the owner's derivation, and MPAIR-01 exists specifically to prevent a persuasive AI-authored scheme from being rubber-stamped as "the owner's design decision." The three candidates were then presented plainly with no ranking. Owner asked which would "showcase Forge the strongest" — answered as a factual/technical question (pooled/recycled, because pair-safety is subset-dependent rather than reducible to per-index arithmetic, unlike contiguous/interleaved which likely collapse to ARB-09's own true-by-construction finding) without making the final selection on the owner's behalf. Owner then asked which would be "most meaningful for developing research" — answered: also pooled/recycled, since it's the scheme that attacks the actual simulation-cost bottleneck (4 extra modes/pair under contiguous) that would cap a real future implementation at k=2 or 3. Owner confirmed pooled/recycled as the final choice after seeing both the case for it and the cost being accepted (harder invariant to state, more implementation complexity if ever built).

---

## Fallback on non-convergence (extension of MPAIR-05's honesty requirement)

| Option | Description | Selected |
|--------|-------------|----------|
| Shrink n/k until it solves, report that as the justified bound | Empirical bound-finding, mirrors how the existing model's bitwidth was chosen. | |
| Hard time ceiling (5-10 min); report a timeout as a finding | A timeout at the target bound IS the honest verdict MPAIR-05 already requires, not a failure to work around. | ✓ |

**User's choice:** Hard time ceiling, timeout reported as a finding.
**Notes:** Chosen as a direct extension of MPAIR-05's existing honesty requirement — a non-convergence at the maximal bound (D-03) is itself informative and should be reported plainly rather than quietly worked around by shrinking the bound.

---

## Claude's Discretion

- The precise pooling-compatibility rule (which pairs may share ancilla modes) — default proposed is vertex-disjointness (`{i,j} ∩ {i',j'} = ∅`), reasoned from IQP circuits needing overlapping-qubit ZZ terms to remain independently active. Not put to the owner as a separate gray area; flagged in CONTEXT.md as a mechanism detail the researcher/planner should state precisely and surface back to the owner if it doesn't hold up.
- Exact empirical procedure for finding the largest (n, k) within the time ceiling.
- File location/naming for the new Forge model (kept separate from `forge/ancilla_mapping.frg` rather than extending it in place, to avoid conflating two different verified properties under one file with its own drift-warning scope).

## Deferred Ideas

- Python implementation of the k-pair (pooled/recycled) circuit — out of scope for this phase, already recorded in REQUIREMENTS.md's Out of Scope table.
- Re-running the hardness-under-loss study with multiple ZZ terms — the actual research payoff, judged v4.0-sized during the preceding milestone-scoping discussion, not touched here.
