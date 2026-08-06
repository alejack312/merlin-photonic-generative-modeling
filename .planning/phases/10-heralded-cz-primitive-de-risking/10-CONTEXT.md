# Phase 10: Heralded-CZ Primitive De-Risking - Context

**Gathered:** 2026-08-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Standalone verification of `heralded_cz`'s actual measured behavior — success probability and phase behavior — for this specific Perceval implementation, before any integration work touches the existing weight-1 code. Building the full weight-2 circuit, wiring it into the existing register layout, and running TVD validation are all later phases (11-13), not this one.

</domain>

<decisions>
## Implementation Decisions

### Phase verification depth
- Verify the actual `-1` phase on `|1,1⟩`, not just output probabilities. Use `Simulator.prob_amplitude` (or equivalent), since `Processor.probs()` is phase-blind and a probability-only check could pass even with a wrong sign (`|1|² == |-1|²`).
- This is the concrete claim the CZ/ZZ operator identity depends on — confirming it now, standalone, is cheaper than discovering a phase bug later via an opaque TVD failure in Phase 12.

### Success-probability input coverage
- Measure the 4 computational-basis dual-rail inputs (already done during research: uniform 2/27) plus a few superposition spot-checks — e.g. `|+⟩|+⟩` and one asymmetric superposition case.
- Not exhaustive over the continuous input space — a few spot-checks are enough to catch gross input-dependence without turning this into its own research project.

### Artifact form
- Both a standalone script (readable/runnable on its own, for exploration and as a reference the owner can re-run and explain unaided) and a committed pytest test (regression guard).
- Matches this project's established pattern: `perceval_fluency_demo.py` + `tests/test_perceval_fluency_demo.py` from Phase 8.

### Literature-comparison note placement
- Update `docs/iqp-photonic-encoding.md` directly — specifically the Ingredient 2 / Open Questions sections that already flag the 1/9 and ~2/27 figures as unverified for this exact gate.
- Closes the loop where the question was originally raised, rather than fragmenting the milestone's findings into a separate file. Matches this project's pattern of maintaining one coherent living design document (v1.0's DESIGN_DECISIONS.md, v2.0's iqp-photonic-encoding.md).

### Claude's Discretion
- Exact script/test file naming (should follow the `perceval_fluency_demo.py`-style precedent)
- Which specific superposition inputs to spot-check beyond `|+⟩|+⟩`
- Whether `logical_perf`'s bundled herald-vs-data-validity filter (flagged in Pitfalls research) needs its own explicit assertion in this phase, or can be verified as negligible inline while measuring success probability

</decisions>

<specifics>
## Specific Ideas

No specific product/visual references — this is a verification-only phase. The relevant "specific idea" is methodological: match the rigor and documentation style already established in Phase 8 (perceval_fluency_demo.py) and Phase 9 (docs/iqp-photonic-encoding.md's honesty-ledger pattern — measured numbers reported plainly, including what they don't prove).

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope. (Weight-2 circuit implementation, exact reference extension, TVD validation, and mixed-generator composability are already correctly scoped to Phases 11-13 per the roadmap, not raised as scope-creep candidates during this discussion.)

</deferred>

---

*Phase: 10-heralded-cz-primitive-de-risking*
*Context gathered: 2026-08-06*
