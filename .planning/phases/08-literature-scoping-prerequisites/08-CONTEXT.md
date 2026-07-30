# Phase 8: Literature Scoping & Prerequisites - Context

**Gathered:** 2026-07-31
**Status:** Ready for planning

<domain>
## Phase Boundary

Determine whether a discrete-variable (DV, Fock-space) linear-optical construction of IQP is worth designing at all, and confirm the technical/reference prerequisites any subsequent design work depends on. Output is a written go/no-go verdict (LIT-04) plus three artifacts: the Douce et al. summary, a working manual Perceval circuit, and `docs/iqp-baseline.md`. No encoding design work happens in this phase — that's Phase 9, and only if this phase concludes "go."

</domain>

<decisions>
## Implementation Decisions

### Search methodology & sources
- Time-box: moderate pass, ~1 day of effort — not a quick 2-3hr skim, not a multi-day exhaustive citation-chase.
- Sources in scope: arXiv + Google Scholar (primary), plus re-confirming MerLin's reproduced-papers catalog and Perceval docs for IQP-adjacency (LIT-03 groundwork, re-check nothing was missed).
- Sources explicitly out of scope for this pass: quantum CS community sources (Stack Exchange, Discord, X/Twitter), and directly asking Vincent Espitalier — both deferred (see Deferred Ideas).
- Search terms: both direct keyword terms ("IQP linear optics", "IQP photonic", "IQP boson sampling", "discrete variable IQP") AND structural-analogue terms (commuting diagonal gates, Hadamard-basis conjugation, sampling hardness) — casting a wider net than the acronym alone, since a relevant construction might not use the term "IQP" explicitly.

### Go/no-go bar (LIT-04)
- **Go:** no blocking impossibility result found. This is a deliberately low bar — absence of a proven obstruction is sufficient; a fully worked constructive mapping is NOT required to say "go" (that's Phase 9's job).
- **Not-ready:** only triggered by an explicit impossibility/no-go finding — a real argument or result showing DV linear optics cannot realize IQP's structure (e.g., a fundamental obstruction encoding Hadamard-basis conjugation in Fock space). A time-box expiring with nothing found does NOT by itself count as "not-ready."
- **Third outcome — "promising but needs more time":** reserved for a genuine partial/ambiguous lead surfaced during the pass that seems worth a deeper follow-up pass before committing to Phase 9. This is not a catch-all for "found nothing" — if the time-box expires with no blocker AND no partial lead, the default outcome is still "go" per the stated bar above, not this third bucket.
- Whichever outcome is reached, the written verdict must state its reasoning explicitly (what was searched, what was/wasn't found, why that maps to the chosen outcome) rather than silently picking one.

### Perceval fluency demo scope (PREQ-01)
- Trivial fluency demo, not an IQP-flavored preview — simplest circuit that exercises `Circuit`/`PS`/`BS`/`BasicState`/`Analyzer` directly, without `QuantumLayer.simple()`. Previewing IQP structure here would step on Phase 9's actual design work.
- Verification: compare the circuit's output against a known closed-form result (e.g., a simple beamsplitter interference pattern with an analytically predictable outcome) — not just eyeballing the `Analyzer` output.
- Attempt-first: per this repo's CLAUDE.md gating rule, the owner wants to sketch/attempt this circuit themselves first. Claude should explain the low-level Perceval API well enough to attempt, then wait for the owner's sketch/attempt before writing the full implementation.

### Baseline doc scope (PREQ-02)
- Primary source: `C:\Users\cuqui\iqp-mmd-barren-plateau\docs\papers` (verified present — 9 papers: `1504.07999v2`, `1610.01808v4`, `2012.09265v2`, `2305.02881v2` + `2305.02881-implicit-explicit-losses`, `2405.00781-barren-plateau-review`, `2502.07889-warm-start-guarantees`, `2503.02934v2 (3)`, `2512.24801v1`), combined with the owner's own prior project notes/vault — not a from-scratch literature re-derivation.
- Content: both IQP circuit structure/hardness AND barren-plateau trainability, roughly equal weight — both are relevant qubit-side properties this milestone wants to know "survive translation" or not.
- Depth: short reference, 1-2 pages — a tight, scannable comparison point for Phase 9, not a survey paper.

### Claude's Discretion
- Exact search query phrasing/order during the literature pass.
- Exact choice of demo circuit example for PREQ-01, as long as it stays trivial (not IQP-flavored) and has a closed-form-verifiable output.
- Exact section breakdown of `docs/iqp-baseline.md` within the 1-2 page cap.

</decisions>

<specifics>
## Specific Ideas

- The sibling project's paper stash at `C:\Users\cuqui\iqp-mmd-barren-plateau\docs\papers` is the concrete primary source for the baseline doc — verified to exist with 9 relevant PDFs before locking this decision.
- The technical note being sent to Vincent Espitalier (separate, already drafted, owner-only step) is independent of this phase's literature search — not a research channel for Phase 8.

</specifics>

<deferred>
## Deferred Ideas

- Asking Vincent Espitalier directly whether Quandela has internal awareness of a DV IQP construction — deferred, not part of this phase's search sources. Could be worth raising in a future conversation with him, but not blocking or in-scope for Phase 8's time-boxed pass.
- Quantum CS community sources (Stack Exchange, Discord, X/Twitter quantum research circles) — deferred, not part of this phase's search sources.
- An IQP-flavored preview circuit (vs. the trivial fluency demo) — deferred to Phase 9's actual encoding design work; PREQ-01 stays deliberately trivial so it doesn't front-run the novel-contribution deliverable.

</deferred>

---

*Phase: 08-literature-scoping-prerequisites*
*Context gathered: 2026-07-31*
