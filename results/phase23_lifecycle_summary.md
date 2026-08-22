# Phase 23: Ancilla Lifecycle Safety — Results Summary

## Scope and bounded evidence

Phase 23 adds a relational Forge model for ancilla-mode and four-mode-block
lifecycle across ordered CP(alpha) gate events. The model uses explicit
`State.next` snapshots, tracks both block and individual-mode status, and
encodes `allocate -> begin/use -> finish -> terminal post-selection ->
release/free` transitions.

The live run used the smallest meaningful domain: n=4, the six K4 pairs, two
gates, one four-mode block, and nine ordered states, with `for 7 Int`. The
exact command, bound, solver versions, stdout, and timing lines are preserved
in [`results/phase23_lifecycle_run_log.md`](phase23_lifecycle_run_log.md).
The model passed all three named checks:

- `unsafeSameEpochWitness`: SAT — an unsafe trace exists when the deliberately
  permissive counterexample transition reallocates a live block.
- `noLiveReallocationUnderSafeProtocol`: UNSAT — valid lifecycle transitions
  cannot contain that live-reallocation shape.
- `safeCrossEpochReuseWitness`: SAT — the same block can be reused after
  terminal post-selection and explicit release/free in a later epoch.

The readable state-by-state projections are in
[`results/phase23_lifecycle_traces.md`](phase23_lifecycle_traces.md). They are
derived from the model's explicit event predicates; Sterling was disabled, so
the CLI output does not contain symbolic atom-instance labels.

## Primary LIFE-05 cross-check

Phase 22's MPAIR-07 probe measured pooled-versus-dedicated Perceval output
distributions for the n=4 vertex-disjoint configuration. It recorded
`tvd_pooled_vs_dedicated` values of approximately `1.305e-14` and `2.899e-14`,
inside the pre-committed `1e-9` tolerance (`results/phase22_reuse_gate.md`).
That is a bounded numerical result for the tested circuit instances.

Phase 23 measures the structural question of whether a block may be allocated
again while strict deferred post-selection still marks it live. Its same-trace
answer is no: the unsafe trace reaches a second allocation before terminal
post-selection. The cross-epoch answer is yes after explicit release. The
numerical GO and structural unsafe result are therefore an unresolved
abstraction-level disagreement. Neither method is treated as proving the
other wrong, and the cross-epoch witness is retained as a separate sanity
check rather than substituted for the primary comparison.

## Static minimum-K versus temporal capacity

Phase 22's static allocation result remains the static graph-coloring result:
`K=n-1` for even n and `K=n` for odd n, with Forge converging through n=6 and
the Python baseline checking the formula through n=8. Phase 23 does not search
for a new joint minimum K and therefore does not replace or recompute that
static result.

Strict lifetime safety does add a separate temporal-capacity constraint. In a
single deferred-postselection epoch, a block used by one gate remains live
through `finish`; even a vertex-disjoint later pair cannot reuse it until the
terminal post-selection/release sequence. Thus the static K is not, by itself,
a proof that K blocks suffice for an arbitrary same-epoch gate schedule. The
new temporal minimum, if a schedule permits multiple same-epoch gates, cannot
be decided by this bounded n=4 witness alone; it would require an explicitly
scoped scheduling/capacity search, which is outside Phase 23's locked scope.

This preserves both claims without conflating them: Phase 22 answers a static
allocation question, while Phase 23 demonstrates a bounded lifecycle
constraint that can make the temporal problem stricter. The result does not
establish an unbounded theorem, Perceval amplitude equivalence, physical
unitary equivalence, a Python k-pair implementation, or a new
hardness-under-loss result.

## LIFE-01..07 evidence map

| Requirement | Evidence | Current evidence status |
|---|---|---|
| LIFE-01 | [`forge/ancilla_lifecycle_safety.frg`](../forge/ancilla_lifecycle_safety.frg); run log | evidence present in bounded n=4 model |
| LIFE-02 | Forge unsafe SAT witness and safe-protocol UNSAT check; trace table | evidence present; unsafe trace is explicit |
| LIFE-03 | `FinishGate` preserves liveness; `FinalPostselect` then `Release` transitions | evidence present in bounded model |
| LIFE-04 | SAT safe cross-epoch witness with two gates and genuine block reuse | evidence present; reuse occurs after release |
| LIFE-05 | [`phase23_lifecycle_run_log.md`](phase23_lifecycle_run_log.md); [`phase23_lifecycle_traces.md`](phase23_lifecycle_traces.md); Phase 22 numerical source | complete after owner interpretation review |
| LIFE-06 | This static-vs-temporal section; Phase 22 invariant and summary | complete; no joint temporal-K search performed |
| LIFE-07 | This summary and the canonical encoding section | complete after owner review |

## Owner review

**Date:** 2026-08-22
**Status:** approved with wording preserved verbatim.

> Same-trace reuse is unsafe under deferred post-selection because the unsafe trace reaches a second allocation before terminal post-selection.
>
> Cross-epoch reuse is safe because of  terminal post-selection and explicit release/free in a later epoch.
>
> LIFE-05 compares the same-trace and cross-epoch methods under strict deferred post-selection. It does not try to prove one method wrong.
>
> Temporal safety does not changes Phase 22's static minimum-K conclusion

Interpretation applied: the static minimum-K result remains unchanged as a
static graph-colouring result; the lifecycle model adds a separate temporal
capacity constraint and does not compute a replacement joint minimum-K search.
The extra space in “because of  terminal” and the grammatical phrasing in the
last sentence are preserved because this section records the owner's words,
not an edited paraphrase.

The owner reviewed, in their own words:

1. why same-trace reuse is unsafe under strict deferred post-selection;
2. why cross-epoch reuse is a separate safe witness;
3. what LIFE-05 does and does not compare; and
4. whether the temporal finding changes Phase 22's static minimum-K conclusion.

The review is now recorded. Requirement metadata may be closed because the
actual model, run log, trace evidence, and owner interpretation are present.
