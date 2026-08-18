---
phase: 20-technical-write-up
plan: 03
subsystem: docs
tags: [iqp, photonic-encoding, arb-01, literature-review, write-up]

# Dependency graph
requires:
  - phase: 15-16 (ARB-01 Core Gate De-Risking & Extended Validation)
    provides: PostProcessedControlledRotationsItem/CP(alpha) gate construction, closed-form success probability, full-pipeline validation, Forge mode-mapping verification -- all cited, not re-derived, in this plan's new subsection
provides:
  - "docs/iqp-photonic-encoding.md gains a section-scoped 'What ARB-01/ARB-02 does/doesn't establish' subsection, closing the one structural gap vs. TRAIN's/HARD's existing per-section scope subsections"
  - "WRITE-02's literature comparison table for the ARB section: arXiv:2405.01395 given a substantive consistent verdict, other 10 named baselines explicitly marked not applicable via prose"
affects: [21-external-facing-framing-pass, technical-findings-synthesis-doc]

# Tech tracking
tech-stack:
  added: []
  patterns: ["Section-scoped 'what this does/doesn't establish' subsection pattern, matching docs/trainability-study.md and docs/hardness-under-loss-study.md's existing convention"]

key-files:
  created: []
  modified: ["docs/iqp-photonic-encoding.md"]

key-decisions:
  - "Used a short (1-row) literature table plus prose for the other 10 baselines, rather than 11 rows of mostly 'silent' -- per 20-CONTEXT.md's locked decision that each section's table lists only baselines actually relevant to that section."
  - "Did not add a Herbst et al. cross-thread note to this document -- per 20-CONTEXT.md's locked decision, that cross-thread belongs only in trainability-study.md and hardness-under-loss-study.md (trainability/hardness predictions), not in this gate-mechanics document."

patterns-established:
  - "Section-scoped scope statements restate (not re-derive) the whole-document Conclusion's relevant bullets, narrowed to the specific section, and cite existing subsections by name rather than re-deriving their content."

# Metrics
duration: ~10min
completed: 2026-08-18
---

# Phase 20 Plan 03: ARB-01/ARB-02 Scope Statement and Literature Table Summary

**Added a section-scoped "what this does/doesn't establish" subsection plus a 1-row-plus-prose literature comparison table to `docs/iqp-photonic-encoding.md`'s ARB-01/ARB-02 section, closing the one structural gap Phase 20's research identified relative to TRAIN's and HARD's existing per-section scope subsections.**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-08-18T01:15:00Z
- **Completed:** 2026-08-18T01:25:36Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments

- New `### What ARB-01/ARB-02 does/doesn't establish` subsection inserted between the existing "Forge Verification of the Ancilla Mode-Mapping (Phase 16)" subsection and the document-level "Conclusion and Open Questions" section.
- States what ARB-01/ARB-02 establishes (continuously-tunable two-qubit diagonal-phase gate, validated to the same rigor bar `heralded_cz` cleared: general operator identity, closed-form success probability, 16-point sweep match, full-pipeline TVD validation + boundary agreement, n=3 composability, Forge injectivity check), citing existing subsections by name rather than re-deriving them.
- States what it does not establish, scoped specifically to ARB-01/ARB-02 (not a hardness/trainability claim; toy-check scope n=2-3 lossless only, never cross-tested under loss; general-n scaling stated not demonstrated; success probability genuinely alpha-dependent, not fixed) — restated and narrowed from the document-level Conclusion's relevant bullets, not copied verbatim.
- Added the WRITE-02 literature comparison table for this section: arXiv:2405.01395 given a substantive **consistent** verdict (the primary construction source, independently verified to ~1e-7 against measurement — a stronger form of engagement than a citation check); the other 10 named WRITE-02 baselines addressed via one prose paragraph as not applicable to this section's gate-construction claim (all named explicitly, none silently omitted), with a pointer to `docs/trainability-study.md`'s and `docs/hardness-under-loss-study.md`'s own tables for where those 10 baselines do apply.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add the ARB-01/ARB-02-scoped "what this does/doesn't establish" subsection** - `0ae0a0c` (docs)

## Files Created/Modified

- `docs/iqp-photonic-encoding.md` - Added `### What ARB-01/ARB-02 does/doesn't establish` subsection (19 lines: establishes/does-not-establish prose + WRITE-02 literature table) between the Phase-16 Forge Verification subsection and the document-level Conclusion. No existing content altered.

## Decisions Made

- **Short table + prose, not 11 padded rows.** Per `20-CONTEXT.md`'s locked decision that each section's WRITE-02 table lists only baselines genuinely relevant to that section, this table has one substantive row (arXiv:2405.01395) and addresses the remaining 10 via a single prose paragraph explicitly naming each one as not applicable — avoids a table full of "silent" while still satisfying WRITE-02's "all 11 addressed" requirement.
- **No Herbst et al. cross-thread here.** Per `20-CONTEXT.md`'s explicit lock, Herbst et al.'s prediction (anticoncentration driving both trainability and hardness) is a trainability/hardness claim, not a gate-mechanics claim — the cross-thread belongs only in `docs/trainability-study.md` and `docs/hardness-under-loss-study.md`, not here.

## Deviations from Plan

None - plan executed exactly as written. The single task's content matched the plan's detailed specification (establishes/does-not-establish bullets, table structure, prose paragraph for the other 10 baselines) directly.

## Issues Encountered

**Concurrent-session commit-attribution mixing (operational note, not a code defect).** This phase's plans run with `wave: 1`/no cross-dependency between 20-01/20-02/20-03, and a concurrent session executing Plan 20-02 (`docs/hardness-under-loss-study.md`'s literature table + Herbst cross-reference note) was working in this same shared working directory at the same time. That session's own metadata commit (`610230d`, labeled `docs(20-02)`) swept up this plan's already-staged `.planning/ROADMAP.md`, `.planning/STATE.md`, and this `20-03-SUMMARY.md` file alongside its own `docs/hardness-under-loss-study.md` changes — the same pattern already documented multiple times in `STATE.md` for Phase 18's concurrent-plan execution. Content verified intact and unaltered (this file's content matches what this plan wrote; `docs/iqp-photonic-encoding.md`'s own changes are cleanly isolated in this plan's own commit `0ae0a0c`). No history was rewritten to fix the attribution; flagged here for the record, consistent with this project's established handling of the same situation in Phase 18.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- WRITE-04 (ARB) and WRITE-02 (ARB's table) are now satisfied for this document. `docs/iqp-photonic-encoding.md`'s ARB-01/ARB-02 section now matches TRAIN's and HARD's existing per-section scope-statement pattern.
- This plan is independent of Plan 20-01 (TRAIN) and Plan 20-02 (HARD) — no blockers or dependencies exist between them. Plans 20-01, 20-02, and 20-04 (the `docs/technical-findings.md` synthesis doc, per `20-CONTEXT.md`) remain to be executed to complete Phase 20.
- No blockers for Phase 20's remaining plans.

---
*Phase: 20-technical-write-up*
*Completed: 2026-08-18*
