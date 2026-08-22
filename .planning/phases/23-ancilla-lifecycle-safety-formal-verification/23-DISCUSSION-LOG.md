# Phase 23: Ancilla Lifecycle Safety — Formal Verification - Discussion Log

> **Audit trail only.** Do not use as input to planning, research, or execution agents.
> Decisions are captured in CONTEXT.md — this log preserves the alternatives considered.

**Date:** 2026-08-22
**Phase:** 23-Ancilla Lifecycle Safety — Formal Verification
**Areas discussed:** Trace representation, Lifecycle semantics, Witness and counterexample shape, Phase 22 cross-check

---

## Trace representation

| Option | Description | Selected |
|--------|-------------|----------|
| 1 | Explicit relational `State` snapshots, following `stop_and_copy.frg`. | ✓ |
| 2 | `#lang forge/temporal` with temporal operators. | |

| Option | Description | Selected |
|--------|-------------|----------|
| 1 | Exactly two gates and a minimal fixed trace. | |
| 2 | Bounded configurable sequence of gates. | ✓ |
| 3 | Two separate fixed safe/unsafe traces. | |

| Option | Description | Selected |
|--------|-------------|----------|
| 1 | One ordered `State` trace with a `next` relation. | ✓ |
| 2 | Separate named state sets per bound. | |

| Option | Description | Selected |
|--------|-------------|----------|
| 1 | Exactly `N` gate steps per run. | |
| 2 | Up to `N` gate steps, allowing the shortest unsafe trace. | ✓ |

**User's choice:** `1, 2, 1, 2`
**Notes:** Explicit relational states, a bounded configurable trace, one ordered `next` relation, and an up-to-`N` bound.

---

## Lifecycle semantics

| Option | Description | Selected |
|--------|-------------|----------|
| 1 | Track four-mode ancilla blocks as the resource unit. | |
| 2 | Track individual ancilla modes only. | |
| 3 | Track both individual modes and grouped blocks. | ✓ |

| Option | Description | Selected |
|--------|-------------|----------|
| 1 | Separate allocation and use events. | |
| 2 | One gate-level transition with allocation/use fields. | |
| 3 | Expanded `allocate → begin/use → finish` gate protocol. | ✓ |

| Option | Description | Selected |
|--------|-------------|----------|
| 1 | Explicit terminal `in-use → releasable → free` sequence. | ✓ |
| 2 | Single terminal `in-use → free` transition. | |
| 3 | End at `releasable`; treat `free` as a later-run initial state. | |

| Option | Description | Selected |
|--------|-------------|----------|
| 1 | Strictly live until terminal post-selection. | ✓ |
| 2 | Gate-local use ends after gate completion. | |
| 3 | Model both interpretations. | |

**User's choice:** `3, 3, 1, 1`
**Notes:** Both resource levels, the expanded protocol, explicit terminal release, and strict deferred-postselection liveness. Same-trace reuse is therefore unsafe; safe reuse is represented across completed epochs.

---

## Witness and counterexample shape

| Option | Description | Selected |
|--------|-------------|----------|
| 1 | Reuse across circuit epochs after terminal release. | |
| 2 | Reuse within one deferred-postselection trace, accepting a LIFE-04 conflict. | |
| 3 | Model both safe cross-epoch reuse and unsafe same-trace reuse. | ✓ |

| Option | Description | Selected |
|--------|-------------|----------|
| 1 | Unsafe trace uses two vertex-disjoint pairs sharing one block. | ✓ |
| 2 | Unsafe trace repeats the same qubit pair. | |
| 3 | Include both vertex-disjoint and same-pair traces. | |

| Option | Description | Selected |
|--------|-------------|----------|
| 1 | Safe witness reuses block 0 across epochs: `(0,1)` then `(2,3)` after release. | ✓ |
| 2 | Safe reuse follows an intermediate post-selection checkpoint. | |
| 3 | Safe reuse occurs only across independent runs. | |

| Option | Description | Selected |
|--------|-------------|----------|
| 1 | Preserve Forge witness and add a human-readable trace table. | ✓ |
| 2 | Preserve only the raw Forge instance. | |
| 3 | Provide only a translated human-readable trace. | |

**User's choice:** `3, 1, 1, 1`
**Notes:** The unsafe trace isolates deferred-lifetime clobbering from same-pair composition. The safe witness is cross-epoch reuse, preserved as solver output plus a readable state trace.

---

## Phase 22 cross-check

| Option | Description | Selected |
|--------|-------------|----------|
| 1 | Make same-trace strict-liveness comparison primary. | |
| 2 | Compare only the safe cross-epoch case. | |
| 3 | Make same-trace comparison primary and cross-epoch reuse a separate sanity check. | ✓ |

| Option | Description | Selected |
|--------|-------------|----------|
| 1 | Test Phase 22's fixed colouring first and increase `K` if needed. | |
| 2 | Search for minimum `K` jointly with lifecycle constraints. | |
| 3 | Keep static minimum `K` and temporal lifetime as separate questions. | ✓ |

| Option | Description | Selected |
|--------|-------------|----------|
| 1 | Let the lifecycle result govern the structural claim. | |
| 2 | Report an unresolved disagreement without choosing a universal winner. | ✓ |
| 3 | Treat disagreement as a model-assumption mismatch and make the broader claim conditional. | |

| Option | Description | Selected |
|--------|-------------|----------|
| 1 | Carry Phase 22's `n ≤ 8` bound. | |
| 2 | Start at `n = 4`, the smallest meaningful witness domain. | ✓ |
| 3 | Sweep increasing `n` and trace depth until a stated Forge ceiling. | |

**User's choice:** `3, 3, 2, 2`
**Notes:** Same-trace comparison is primary; cross-epoch reuse is a sanity check. No joint recolouring search is planned. Any disagreement remains explicit and unresolved. Start at `n = 4`, prioritizing trace depth and witness quality.

---

## the agent's Discretion

None. The owner made all discussed design selections.

## Deferred Ideas

None.
