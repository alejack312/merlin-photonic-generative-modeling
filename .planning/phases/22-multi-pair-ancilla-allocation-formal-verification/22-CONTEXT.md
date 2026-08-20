# Phase 22: Multi-Pair Ancilla Allocation — Formal Verification - Context

**Gathered:** 2026-08-20
**Status:** Ready for planning

<domain>
## Phase Boundary

Symbolically verify, in Forge, a k-pair ancilla mode-allocation scheme for the CP(α) weight-2 gate family (ARB-01) — proving no ancilla-mode collision across pairs, and none against any data port, before any Python implements k-pair circuits. Deliberately scoped to verification only: no Python k-pair implementation, no re-run of the hardness-under-loss study with multiple ZZ terms (both explicitly Out of Scope — the latter judged v4.0-sized). Builds directly on Phase 16's ARB-09 Forge model (`forge/ancilla_mapping.frg`), which verified the single-pair case of the same gate family.

</domain>

<decisions>
## Implementation Decisions

### Gate family scope (MPAIR-01/02 precondition)
- **D-01: CP(α) family only** (`build_cp_insertion` / `_build_weight2_cp_processor_no_postselect`, 4 ancilla modes per pair, post-selection-filtered) — not `heralded_cz` (2 ancilla/pair, herald-registered, fixed π/4), and not a generalization over both.
- **Why, stated for downstream agents (not just "user preferred it"):** CP(α)'s 4-ancilla-per-pair footprint is the larger combinatorial object of the two — roughly 4× the pairwise-distinctness constraints per pair-comparison that heralded_cz's 2-ancilla variant would need, so it's the harder instance of the same problem, not merely a formula match to the owner's original framing. It is also the more research-meaningful family: heralded_cz is fixed at θ=π/4, forcing every pair to an identical coupling strength, whereas CP(α)'s arbitrary-θ freedom is what a real future multi-pair circuit would need for heterogeneous per-pair coupling (part of what would make a future hardness study interesting).
- **A "both families generalized" option was explicitly considered and rejected**, not just left unconsidered: herald-registration and post-selection-filtering are not interchangeable bookkeeping styles of the same collision check — a herald failure is a distinguishable click event, post-selection is a silent discard. Abstracting an "ancilla-count" parameter across both without also abstracting that semantic difference would produce a model that claims coverage it doesn't structurally have. Downstream agents should not attempt to generalize the eventual Forge model across both gate families.

### Allocation scheme (MPAIR-01 — attempt-first gate, resolved live in this discussion)
- **D-02: Pooled/recycled ancilla allocation** — ancilla modes are reused across pairs that do not share a qubit index, rather than each pair getting a disjoint, fixed 4-mode block. Rejected alternatives, with reasons, per MPAIR-01's requirement that both be recorded:
  - **Contiguous blocks** (`pair m → 2n+4m..2n+4m+3`, fixed per pair index regardless of which other pairs are active) — this was the scheme in the owner's own original framing (itself inherited from a prior Claude/Opus turn's proposal, not independently re-derived by the owner — flagged explicitly during discussion as the reason a genuine comparison was still owed before treating it as decided). Rejected because it is very likely disjoint *by construction*, the same shape ARB-09's own 2026-08-20 audit already found for the single-pair model (true-by-construction, brute-forceable in <1ms, Forge's exhaustive-search advantage never engages). Cheaper to eventually implement in Python, but would likely make MPAIR-05 re-conclude the same "Forge didn't add anything" finding a second time.
  - **Interleaved (round-robin) allocation** — a third fixed-by-pair-index variant, different arithmetic from contiguous, same likely true-by-construction shape. No advantage over contiguous was identified; rejected for the same reason.
- **Why pooled/recycled won, on both axes actually evaluated (not asserted):**
  - *Forge showcase:* whether a given pair's ancilla block is safe now genuinely depends on which *other* pairs are simultaneously active (two pairs sharing no qubit *can* share ancilla modes; two pairs sharing a qubit cannot) — this is the one scheme where "no collision for every subset of pairs" is a load-bearing property, not a restatement of a per-index arithmetic fact. It is the only candidate where a Forge counterexample would look like an actual structure (a specific bad subset) rather than something a one-line parity argument already rules out.
  - *Research meaningfulness:* attacks the actual bottleneck named in the owner's original framing ("each pair costs 4 extra modes, so simulation cost explodes fast, you might only ever run k=2 or 3") — mode-count growth becomes sub-linear in k instead of a flat 4×k, which is the one lever that would let a real future implementation reach k=4 or 5 rather than stalling at k=2.
  - *Cost accepted knowingly:* MPAIR-02's invariant is harder to state precisely for this scheme (a genuine subset-dependent condition, not four numbers proven pairwise-distinct), and any eventual Python implementation of pooling is more code than contiguous's `2n+4m` formula. This was named explicitly before the owner confirmed the choice.

### Bound and fallback (MPAIR-03)
- **D-03: n ≤ 8, k up to all C(n,2) pairs at that n** — the maximal bound, continuous with ARB-09's own n≤8 convention on the n-axis, pushed to k's ceiling on the new axis. Owner chose this knowing it risks an intractable Forge solve (at n=8, C(8,2)=28 candidate pairs → up to 2^28 ≈ 268M subsets in the worst framing).
- **D-04: Fallback on non-convergence is a hard time ceiling (5–10 minutes), with a timeout treated as a finding, not a failure to be worked around.** This is not a separate contingency bolted onto MPAIR-05 — it *is* MPAIR-05's honest-verdict requirement, applied to the bound choice itself: if the target bound doesn't converge in the ceiling, that non-convergence is the reported result (paired with whatever largest bound did converge, timed, exactly like the ARB-09 summary's Forge-vs-brute-force comparison table). Do not silently shrink the bound and report only the smaller success — report both the attempt and the outcome.
- **Downstream note:** given pooled/recycled's subset-dependent semantics (see D-02), the effective domain size is almost certainly larger than a pairwise-only model at the same (n, k) — plan the empirical bound-finding pass (start small, increase until the ceiling is hit or the target is reached) rather than assuming n=8/k=28 will simply run.

### Post-research decisions (added 2026-08-20, after 22-RESEARCH.md)

Research surfaced two findings that change the phase's shape. Both were put to the owner and answered; these supersede the shape implied by the pre-research CONTEXT/ROADMAP text where they conflict.

- **D-05: The Forge model answers a SEARCH question, not a verify-a-fixed-scheme question.** The model asks *"does an assignment of ≤ K ancilla blocks to all C(n,2) pairs exist such that no two vertex-sharing pairs collide, and what is the minimum such K?"* — i.e. edge-colouring existence/minimality over K_n — rather than "does this fixed formula ever collide."
  - **Why this changed:** research established that collision is an inherently *binary* predicate, so under any allocation that is a fixed function of a pair's own `(i,j)`, "no collision over every subset" is **exactly equivalent** (not weaker) to checking all `C(28,2)+28 = 406` pairwise cases at n=8 — trivially brute-forceable, which would have driven MPAIR-05 to a second "Forge did not earn its place" verdict. Verifying a given colouring is easy; *finding* a minimum one is constraint satisfaction, which is what a SAT-backed model finder is actually for.
  - **Also the more research-useful question:** minimum block count directly answers "how few ancilla modes can a k-pair circuit get away with," which is the simulation-cost ceiling that caps k at 2-3 under naive allocation — the bottleneck D-02 selected pooled/recycled to attack in the first place.
  - **Honest caveat, must be stated in MPAIR-06's write-up:** for complete graphs the chromatic index is a known theorem (`n-1` for even `n`, `n` for odd `n`, König/Vizing). Forge would be constructively confirming known combinatorics and producing the concrete colouring, not settling an open problem. State this plainly rather than implying novelty.
  - **Consequence for MPAIR-03/05 wording:** MPAIR-03's "checking the invariant holds for every subset of pairs" should be read as satisfied by the search formulation (the pairwise-reduction argument, stated explicitly in MPAIR-02's prose, is what licenses not literally enumerating subsets). MPAIR-05's brute-force baseline must now compare against *search*, not against verification — a fair baseline is a hand-rolled colouring search (greedy/backtracking), not the 406-case verification loop.

- **D-06: Resolve the physics BEFORE writing any Forge model — this is a go/no-go gate on the whole scheme.** Research identified an unresolved question it could not settle and that is explicitly outside what Forge can check: this pipeline defers CP(α) post-selection to the very end (never per-gate, because `Processor.set_postselection()` rejects conditions on modes a later component touches — Pitfall 3 in `15-RESEARCH.md`). Ancilla modes are therefore *not* deterministically restored to vacuum mid-circuit; "success" is a probabilistic outcome resolved only at final measurement. A second pair's gate applied to already-used ancilla modes acts on a generally non-vacuum, entangled state — physically different from dedicated per-pair ancilla.
  - **Owner's call: resolve this first.** A de-risking step (amplitude calculation, and/or a literature check on ancilla reuse / garbage collection in post-selected linear-optical gates) runs *before* any `.frg` is written.
  - **This gate can invalidate the phase's premise.** If physical reuse turns out invalid under deferred post-selection, then pooling is moot and contiguous allocation was correct after all — in which case the honest outcome is to report that finding and stop, not to model a scheme that cannot be built. The planner MUST structure this as a real branch with a stated stop condition, not a formality that always proceeds.
  - Vertex-disjointness (D-02's compatibility rule) and "safe to physically reuse the same ancilla rail across sequential gates" are two *different, independently necessary* conditions. This project's code and docs currently address only the first.

### Verified corrections to research (checked against official Forge docs, 2026-08-20)

- **Bitwidth must be recomputed — do NOT copy `for 6 Int` forward from `ancilla_mapping.frg`.** Official docs confirm `for N Int` is a *bitwidth, not a count* ("3 Int corresponds to the 8 integers in the range -4 through 3"), so `for 6 Int` gives `[-32, 31]`. Under a pooled scheme at n=8 the largest computed mode index is ~43 (data ports `0..15`, plus `n-1 = 7` ancilla blocks × 4 modes → up to 43), which **overflows `for 6 Int` silently**. `for 7 Int` (`[-64, 63]`) is the minimum safe bitwidth; recompute against the final formula rather than trusting this estimate. Note `22-RESEARCH.md`'s own code snippets still show `for 6 Int` — internally inconsistent with its own finding in the same section; the planner must use the corrected value.
- **`set` multiplicity confirmed available**, and confirmed to require Relational Forge (`#lang forge`, which `ancilla_mapping.frg` already uses) — not Froglet. Official docs give the arity-3 form directly: `sig Student { partnersIn: set Course -> Student }`.
- **Bound-clause syntax is worth verifying on first run:** docs show combined bounds as `run {} for 3 Int for exactly 5 Cat` (repeated `for`), while `22-RESEARCH.md`'s snippets use `for 6 Int, exactly 28 Pair` (comma). Low risk — a syntax error here is loud, not silent — but do not assume the comma form parses.

### Claude's Discretion
- **The precise pooling-compatibility rule** — which pairs are allowed to share ancilla modes. The natural default is vertex-disjointness (two pairs `(i,j)` and `(i',j')` may pool only if `{i,j} ∩ {i',j'} = ∅`), since pairs sharing a qubit are independently "active" in a real IQP circuit (diagonal ZZ terms on overlapping qubits still commute and both apply) and therefore can't safely be treated as mutually exclusive for pooling purposes. **This was not put to the owner as a separate gray area** — it's a mechanism-design detail within the already-confirmed pooled/recycled scheme, not a new design axis — but the researcher/planner should state the rule explicitly and precisely as part of MPAIR-02's invariant statement (owed "in prose before any Forge code" per the requirement), since it is the one piece of the scheme's mechanics not yet reviewed by the owner. Flag it back to the owner if the researcher/planner finds the vertex-disjoint default doesn't hold up (e.g., a subtler physical constraint on shared ancilla banks).
- Exact empirical procedure for finding the largest (n, k) that solves within the time ceiling (linear search, binary search on total domain size, etc.).
- File location and naming for the new Forge model (a separate file from `forge/ancilla_mapping.frg`, since that file's own header still carries a DRIFT WARNING and a "last verified matching source" note scoped to the single-pair case — extending it in place would conflate two different properties under one file).

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Direct Forge precedent (Phase 16, ARB-09)
- `forge/ancilla_mapping.frg` — the single-pair model this phase extends. Copy its two-part `test expect` pattern (`nonVacuous` sat check, then `noCounterexample` unsat check), its bitwidth-justification-in-comments discipline, and its drift-warning convention (the model re-states the Python formula rather than deriving it — do the same here, and carry the same "last verified matching source" obligation).
- `results/phase16_forge_summary.md` — the Forge-vs-brute-force comparison table format MPAIR-05 must produce a sibling of, including its explicit "what Forge alone contributed" framing.
- `.planning/phases/16-arb-01-extended-validation-postselection-bookkeeping/16-CONTEXT.md` — the prior discussion that scoped ARB-09's model (relational vs temporal Forge, pass-criteria structure, why complexity-theoretic claims are out of scope for Forge as a tool category — the same boundary applies here).
- `docs/iqp-photonic-encoding.md` §"Forge Verification of the Ancilla Mode-Mapping (Phase 16)" and §"What Forge alone added — stated honestly" — the exact honesty framing MPAIR-05 must match or extend, including the audit commit `273e9dd` (2026-08-20) that corrected a stale source-line reference and made the "true by construction" finding explicit.

### Gate family source (CP(α), ARB-01/ARB-02)
- `iqp_photonic_encoding.py::build_cp_insertion` (lines ~282–357) — the gate builder; confirms 4 ancilla modes per pair.
- `iqp_photonic_encoding.py::_build_weight2_cp_processor_no_postselect` (lines ~576–648) — the single-pair full-pipeline wiring (mode-mapping dict, theta-folding convention `theta = alpha/4` additive to both qubits' own theta) that any k-pair generalization must extend, not replace.
- `docs/iqp-photonic-encoding.md` §"ARB-01/ARB-02" — the general operator identity and closed-form success probability CP(α) is built on.

### Forge language reference (official, added 2026-08-20)
- https://forge-fm.github.io/forge-documentation/4.2/ — the Forge Documentation (separate from the textbook). Key pages: `building-models/sigs/multiplicity/` (the `set` multiplicity form this phase needs), `running-models/bounds/` (`for N Int` = bitwidth semantics), `testing-chapter/testing/` (`test expect` syntax), `running-models/optimization/`.
- https://forge-fm.github.io/book/2026/ — "Logic for Systems" textbook. Ch. "Modeling Relationships" (Relational Forge) is the relevant chapter for set-valued fields; Ch. "Beyond SAT" for solver-cost intuition.
- `.planning/phases/22-multi-pair-ancilla-allocation-formal-verification/22-RESEARCH.md` — this phase's own research. **Read its Open Questions section**; note the `for 6 Int` inconsistency flagged above.

### Roadmap/requirements (this phase's own locked scope)
- `.planning/ROADMAP.md` Phase 22 entry — success criteria, the "why this phase exists" context note, the attempt-first gate framing (now resolved by this discussion).
- `.planning/REQUIREMENTS.md` MPAIR-01..06 — the six locked requirements this phase must satisfy; do not duplicate their text here, read directly.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `forge/ancilla_mapping.frg`'s `validTriple`/`distinctPorts` predicate shape and `for 6 Int` bitwidth pattern — directly reusable as the starting template for the new model's predicates, extended with a pair-count/subset dimension.
- `_build_weight2_cp_processor_no_postselect`'s mode-mapping dict construction (`{2*i: 0, 2*i+1: 1, 2*j: 2, 2*j+1: 3, 2*n: 4, ...}`) — the exact Python-side pattern the Forge model's formula must stay traceable to, per MPAIR-06's "source of truth for future implementation" requirement (this model has no existing Python to re-state, unlike ARB-09's — it is upstream of implementation, not downstream, which is the opposite direction of drift risk from `ancilla_mapping.frg`).

### Established Patterns
- `results/phaseNN_forge_summary.md` naming and structure (simple pass/fail note + measured comparison table, not a fuller go/no-go toolchain narrative like Phase 14's Julia spike) — Forge tooling itself is already confirmed working, so this phase's summary should follow Phase 16's leaner template, not Phase 14's.
- `docs/iqp-photonic-encoding.md` as the single source-of-truth doc every phase extends in place (never a new parallel doc) — MPAIR-06 continues this pattern explicitly.

### Integration Points
- New Forge model file should NOT extend `forge/ancilla_mapping.frg` in place (see Claude's Discretion above) — sits alongside it in `forge/`, as a related but distinct model.
- `docs/iqp-photonic-encoding.md` gains a new section per MPAIR-06, parallel in structure to the existing "Forge Verification of the Ancilla Mode-Mapping (Phase 16)" section, explicitly stating it verifies a scheme with no Python implementation yet (the source-of-truth direction is reversed from Phase 16's).

</code_context>

<specifics>
## Specific Ideas

- The owner's original framing (carried over from a prior Claude/Opus session's proposal, pasted into the `/gsd-new-milestone` invocation) supplied the "2²⁸ ≈ 268M subsets" framing and the "no collisions across pairs, none with any data port, for every subset of pairs" property statement. That framing was explicitly re-examined during this discussion rather than taken as already-decided — see D-02's rejected-alternatives note. The final scheme (pooled/recycled) is the one where that subset-quantification framing is actually load-bearing; under contiguous or interleaved, it would have overstated what needed checking.
- MPAIR-05's "honest verdict" requirement was explicitly extended, during this discussion, to cover the bound-choice fallback itself (D-04) — a timeout at the target bound is a valid, reportable outcome, not a planning failure.

</specifics>

<deferred>
## Deferred Ideas

- **Python implementation of the k-pair (pooled/recycled) circuit** — explicitly out of scope for Phase 22 (already recorded in `.planning/REQUIREMENTS.md`'s Out of Scope table). This phase produces a specification an eventual implementation would be checked against, not the implementation itself.
- **Re-running the hardness-under-loss study with multiple ZZ terms** — the actual research payoff a k-pair generator would eventually enable, judged v4.0-sized during the milestone-scoping discussion that preceded this one. Not touched in this phase.
- **A second owner review of the exact pooling-compatibility rule** (vertex-disjoint qubits, per Claude's Discretion above) once the researcher/planner states it precisely — not deferred to "later" in the sense of a future phase, but flagged as a checkpoint the planner should surface back to the owner rather than resolve silently, since it's the one mechanism detail within the confirmed scheme that hasn't itself been reviewed.

</deferred>

---

*Phase: 22-multi-pair-ancilla-allocation-formal-verification*
*Context gathered: 2026-08-20*
