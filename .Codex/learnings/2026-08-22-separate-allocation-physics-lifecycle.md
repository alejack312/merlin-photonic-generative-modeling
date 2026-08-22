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

## Addendum — 2026-08-22 Phase 23 planning

### Approach
1. Treat `23-CONTEXT.md` as the locked design contract after the owner chose explicit relational `State.next` traces, strict deferred post-selection, and separate safe/unsafe witnesses.
2. Use three waves: model (`LIFE-01..04`), real Forge evidence and traces (`LIFE-02..05`), then synthesis/documentation/owner review (`LIFE-05..07`).
3. Require raw solver output plus a readable trace table; never accept a scalar Forge verdict where the requirement asks for a trace.

### Decision rules that generalize
- IF a phase has both structural and numerical evidence, THEN make the cross-check a separate artifact and name each method's claim boundary.
- IF a plan requires an owner interpretation, THEN place the blocking checkpoint before requirement status and canonical docs are closed.
- IF automated plan checking times out, THEN report that gate as unavailable and run deterministic local checks; do not label the checker as passed.

### Verification
- `23-RESEARCH.md` was produced from the Phase 22 and CS1710 local precedents; it verified the intended Forge 5.2/Racket 8.15 approach.
- Three plan frontmatters and required sections were checked locally; all LIFE-01..07 claims are present.
- `gsd-tools gap-analysis --phase-dir .planning/phases/23-ancilla-lifecycle-safety-formal-verification` marked all seven LIFE requirements covered (the tool also listed unrelated requirements because it is not phase-filtered).
- `git diff --check` passed. Planning commit: `09c9d17`.

### Next time (for a weaker model)
- Do: load the phase context and prior-phase evidence before choosing waves; preserve the owner’s semantics exactly.
- Do: keep research, plan-checker, and local deterministic fallback outcomes distinct in the handoff.
- Don't: claim a timed-out subagent or checker completed successfully.
