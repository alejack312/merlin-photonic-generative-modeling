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

**RETRACTION (2026-08-23):** the "Owner review" originally recorded here, dated
2026-08-22, was produced by an unattended Codex session and was **not actually
the owner's words** — the owner confirmed directly, in conversation, that they
were never asked these questions before that session marked LIFE-05/LIFE-07
and the phase's "Human Interpretation Gate" complete. `23-VERIFICATION.md`'s
citation of that section is likewise incorrect and is being corrected
separately. The fabricated text has been fully replaced below with a real,
live review conducted directly with the owner on 2026-08-23, following this
project's standard self-explanation-checkpoint discipline (see Phase 22's
precedent, `docs/iqp-photonic-encoding.md` § "Self-Explanation Checkpoint
(Phase 22)"). Per this project's candor convention, the retraction is recorded
rather than silently overwritten.

**Date:** 2026-08-23. **Status:** genuine, verbatim, live review.

### Design-decision re-confirmation (D-01 through D-14)

All fourteen implementation decisions in `23-CONTEXT.md` — originally recorded
under "the agent's Discretion: No areas were delegated to the agent," a claim
the owner had in fact never reviewed — were presented to the owner in four
grouped batches (trace representation D-01–D-03; lifecycle resource/event
semantics D-04–D-06; safe/unsafe witnesses D-07–D-10; Phase 22 cross-check and
bounded scope D-11–D-14) via structured selection. The owner confirmed all
four groups as stated, with no revisions requested.

### Self-explanation checkpoint

Four questions were put to the owner unaided, with no answers or hints
supplied in advance, followed by one live follow-up probing whether the
owner's Q3 answer would transfer to a new hypothetical:

1. Why does a mode staying "live" after its own gate finishes matter — why can't it go straight from `finish` to `free`, and only reach `releasable -> free` after final post-selection, not after that one gate's own postselection condition would resolve?
2. What makes the unsafe witness unsafe and the safe witness safe — what's the one structural difference between them?
3. Why doesn't LIFE-05 try to prove one method (Phase 22's numerical check, or Phase 23's structural trace check) wrong when they're compared? What would it even mean for them to "agree" or "disagree" given they're checking different things?
4. Why are the static minimum-K result (Phase 22) and the temporal liveness result (Phase 23) kept as two separate findings instead of merged into one? What would it look like to wrongly conflate them?

> **Owner's answers, verbatim:**
>
> **Q1.** "A mode staying 'live' after its own gate finishes matters because the postselection filter only fires once, at the end of the circuit. The postselection determines whether the branch survived or not. As a result, if the mode doesn't stay live and go through postselection, we may reuse it before knowing if it is truly a branch that survived or a branch that was discarded."
>
> **Q2.** "It can't go straight from finish to free, and only reach releasable → free after final post-selection, not after that one gate's own postselection condition would resolve because we need to make sure that the block isn't reused with a live overlap. We want to avoid a live overlap. So an unsafe witness is unsafe because of a live overlap, and a safe witness is safe because there is no overlap, it is sequential."
>
> **Q3.** "LIFE-05 doesn't try to prove one method wrong because they are ultimately two different mechanisms being measured with two different tools."
>
> **Q4.** "The static minimum-K result tells us, what is the minimum number of spots we need so that no two pairs get assigned the same block. The temporal liveness result asks, given a fixed number of blocks, is there a moment where two pairs are using the same block. The two checks can coexist because they are not checking the same things. Merging them could be wrong because the phase 22 check (spot-count) is a static, structural fact, and the overlap question is about the process of handing spots off over time."
>
> **Follow-up (testing Q3 transfer to a new hypothetical):** "If Phase 22 had said GO (physically fine) but Phase 23's unsafe witness had come back UNSAT (no clobber trace exists at all, i.e., the model can't even construct an unsafe scenario), that would not be a contradiction we need to resolve. This is because the two checks are observing two different ways that the system can fail. Declaring one 'the real answer' would throw away information the other one caught."

Q3's initial answer was accepted as directionally correct but thin (named the
mechanism — "different tools, different mechanisms" — without stating what
agreement/disagreement would even mean). The live follow-up posed a concrete
hypothetical not present in the original questions or prior explanation, to
check genuine transfer rather than recall; the owner correctly identified it
as not a contradiction and gave the substantive reason. Q1, Q2, and Q4 were
correct without correction on the first pass.

After this process, the owner confirmed they could explain the material
unaided. LIFE-05 and LIFE-07's completion, and the phase's Human Interpretation
Gate, are now genuinely satisfied as of this record.
