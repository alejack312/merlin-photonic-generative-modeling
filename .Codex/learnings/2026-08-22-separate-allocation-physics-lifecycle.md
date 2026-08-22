# Separate static allocation, physics, and lifecycle claims
Date: 2026-08-22 · Scope: project · Recurs when: a formal model evaluates pooled resources across sequential photonic operations

## Context & constraints
- Phase 22 already separated static ancilla-block colouring from Perceval's numerical pooled-vs-dedicated physics probe.
- Deferred post-selection forbids assuming that a completed gate has released its ancilla resource.
- Phase 23 needed both a genuine safe reuse witness and a trace-shaped unsafe counterexample.

## Approach
1. Read the prior phase's invariant, numerical evidence, Forge model, and lifecycle analogues before proposing semantics.
2. Keep the three claim layers separate: physical equivalence, static index allocation, and temporal liveness.
3. Let the owner lock the trace representation and lifecycle semantics before planning implementation.
4. Define safe cross-epoch reuse and unsafe same-trace reuse as distinct witnesses.
5. Compare the direct same-trace result and the cross-epoch sanity result without forcing agreement.

## Decision rules that generalize
- IF a solver model cannot represent amplitudes/interference, THEN do not use it to claim physical gate equivalence.
- IF allocation is static but safety depends on event order, THEN do not answer the lifecycle question with a colouring number alone.
- IF a numerical probe and a structural model disagree, THEN preserve both results and identify the abstraction boundary instead of reconciling by assumption.
- IF a non-vacuity requirement conflicts with a strict invariant, THEN construct separate safe and unsafe witnesses and make the semantic tension explicit.
- IF a counterexample is required to be structural, THEN preserve the solver instance and add a readable state-by-state trace.

## Mistakes avoided / dead ends
- Treating Phase 22's numerical GO as proof that deferred-postselection reuse is structurally safe.
- Reusing the same-pair composition failure as the lifecycle counterexample; vertex-disjoint pairs isolate the intended failure.
- Replacing the explicit relational `State` choice with temporal Forge without owner review.

## Verification
- `gsd-sdk query init.phase-op 23` confirmed the phase and no existing context/plans.
- `git diff --check` passed for the planning artifacts.
- Commits created: `79ca96d` for context/log and `ce130e3` for STATE.md.
- `.planning/STATE.md` records `Phase 23 context gathered`; no discussion checkpoint remains.

## Next time (for a weaker model)
- Do: read the prior phase's physics/static boundary, then identify the lifecycle claim separately.
- Do: ask for owner decisions on trace and release semantics before planning Forge code.
- Don't: infer that a bounded numerical agreement proves an unbounded or temporal safety property.

## Changed files
- `.planning/phases/23-ancilla-lifecycle-safety-formal-verification/23-CONTEXT.md` — captured locked Phase 23 decisions.
- `.planning/phases/23-ancilla-lifecycle-safety-formal-verification/23-DISCUSSION-LOG.md` — preserved alternatives and selections.
- `.planning/STATE.md` — recorded the completed context session.
