# Phase 23 Lifecycle Traces

## How to read these traces

The Forge run uses `option run_sterling off`, so its CLI stdout contains the
named test verdicts and solver timing but no Sterling-rendered atom instance.
The verbatim stdout is preserved in
[`phase23_lifecycle_run_log.md`](phase23_lifecycle_run_log.md). The tables
below are the explicit witness projections required by the model's ordered
event predicates: `B0` is the sole four-mode block and `M0..M3` are its four
individual modes. They preserve the state/event, pair, block, mode status,
and post-selection status needed to reconstruct the witness without claiming
that Forge printed symbolic atom labels.

## Unsafe same-trace reuse witness

Pairs are vertex-disjoint: `g1=(0,1)` and `g2=(2,3)`. Both target `B0`.
The second allocation occurs after `g1` finishes but before terminal
post-selection. That row is the exact clobber point: `B0` and `M0..M3` are
still live in the source state, while the intentionally unsafe transition
reclassifies them as newly allocated for `g2`.

| State | Event | Pair | Block | Individual modes | Block status | Terminal post-selection? |
|---|---|---|---|---|---|---|
| S0 | start | — | — | `M0..M3` free | `B0` free | no |
| S1 | allocate | `(0,1)` | `B0` | `M0..M3` allocated | allocated | no |
| S2 | begin/use | `(0,1)` | `B0` | `M0..M3` in-use | in-use | no |
| S3 | finish | `(0,1)` | `B0` | `M0..M3` still in-use | still live/in-use | no |
| **S4** | **allocate (unsafe clobber)** | **`(2,3)`** | **`B0`** | **reclassified allocated while prior use is live** | **reallocated before release** | **no** |
| S5 | begin/use | `(2,3)` | `B0` | `M0..M3` in-use | in-use | no |
| S6 | finish | `(2,3)` | `B0` | `M0..M3` still in-use | still live/in-use | no |
| S7 | terminal post-selection | `(2,3)` | `B0` | `M0..M3` releasable | releasable | yes |
| S8 | release/free | `(2,3)` | `B0` | `M0..M3` free | free | yes |

This is a counterexample to the claim that the locked strict-liveness
protocol permits same-trace reallocation. It is not a physical-amplitude
claim and does not say that the Phase 22 numerical probe was implemented
incorrectly.

## Safe cross-epoch reuse witness

The same block is reused only after the first epoch reaches terminal
post-selection and an explicit release/free state. The second epoch begins
with the block free. The bounded witness ends after the second gate's finish;
its second post-selection/release is outside this witness's minimum scope.

| State | Event | Pair | Block | Individual modes | Block status | Terminal post-selection? |
|---|---|---|---|---|---|---|
| S0 | start | — | — | `M0..M3` free | `B0` free | no |
| S1 | allocate | `(0,1)` | `B0` | `M0..M3` allocated | allocated | no |
| S2 | begin/use | `(0,1)` | `B0` | `M0..M3` in-use | in-use | no |
| S3 | finish | `(0,1)` | `B0` | `M0..M3` still in-use | still live/in-use | no |
| S4 | terminal post-selection | `(0,1)` | `B0` | `M0..M3` releasable | releasable | yes |
| **S5** | **release/free** | **`(0,1)`** | **`B0`** | **`M0..M3` free** | **free; release point** | **yes** |
| S6 | allocate | `(2,3)` | `B0` | `M0..M3` allocated again | allocated after release | no |
| S7 | begin/use | `(2,3)` | `B0` | `M0..M3` in-use | in-use | no |
| S8 | finish | `(2,3)` | `B0` | `M0..M3` still in-use | still live/in-use | no |

The safe witness satisfies the strengthened non-vacuity requirement: it has
two gates, two vertex-disjoint pairs, genuine reuse of the same block, and a
terminal release between the two allocations.

## Evidence boundary

These tables are projections of the explicit event sequence and lifecycle
predicates in [`forge/ancilla_lifecycle_safety.frg`](../forge/ancilla_lifecycle_safety.frg).
The run log preserves the actual SAT/UNSAT output. The model establishes
bounded structural trace behavior only; it does not establish output-state
equivalence, physical unitary equivalence, an unbounded theorem, a Python
k-pair implementation, or a new hardness-under-loss result.
