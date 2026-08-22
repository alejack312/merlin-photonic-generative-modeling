---
phase: 23-ancilla-lifecycle-safety-formal-verification
plan: 01
subsystem: formal-verification
tags: [forge, lifecycle, deferred-postselection, ancilla-allocation]
requires:
  - phase: 22-multi-pair-ancilla-allocation-formal-verification
    provides: static pooled block abstraction and vertex-disjoint pair boundary
provides:
  - explicit State.next lifecycle model
  - safe cross-epoch and unsafe same-trace witness predicates
affects: [phase-23-evidence, phase-23-documentation]
tech-stack:
  added: []
  patterns: [explicit relational State snapshots, bounded Forge test expect]
key-files:
  created: [forge/ancilla_lifecycle_safety.frg]
  modified: []
key-decisions:
  - "Use explicit State.next snapshots rather than Temporal Forge, per D-01."
  - "Keep block-level and individual-mode lifecycle state in the same bounded model."
requirements-completed: [LIFE-01, LIFE-02, LIFE-03, LIFE-04]
duration: interactive execution session
completed: 2026-08-22
---

# Phase 23 Plan 01: Explicit Lifecycle Model Summary

**Bounded Forge model of CP(alpha) ancilla allocation, deferred liveness, and trace-shaped reuse witnesses**

## Accomplishments

- Added explicit `State.next` snapshots with block and individual-mode status partitions.
- Encoded `allocate`, `begin/use`, `finish`, terminal post-selection, and release/free transitions.
- Added SAT unsafe same-trace, UNSAT valid-protocol safety, and SAT safe cross-epoch witness checks.

## Task Commits

1. **Tasks 1–3: lifecycle vocabulary, transitions, and bounded tests** — `172ef29` (`feat(23-01)`)

## Files Created/Modified

- `forge/ancilla_lifecycle_safety.frg` — bounded n=4 relational lifecycle model.

## Decisions Made

Strict deferred post-selection keeps a finished gate's block live until the
terminal post-selection/release sequence. The unsafe transition is retained as
a deliberately explicit counterexample shape rather than being hidden inside
the valid safety predicate.

## Deviations from Plan

Two Forge syntax/debug corrections were required during the first execution
attempt: parenthesizing a quantified disjunction and replacing sequential
`let` references with direct `next` chains. A safe-witness predicate was also
corrected to identify the post-release state by `freeBlocks`, because release
clears `activeBlock` by design. All corrections were verified by the final
passing suite.

## Issues Encountered

None remaining. Final Forge run passed all three named expectations.

## Next Phase Readiness

Plan 23-02 can use the committed model and its declared nine-state n=4 bound.

---
*Phase: 23-ancilla-lifecycle-safety-formal-verification*
*Completed: 2026-08-22*
