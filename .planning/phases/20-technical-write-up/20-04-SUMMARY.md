---
phase: 20-technical-write-up
plan: 04
subsystem: documentation
tags: [technical-writing, literature-synthesis, iqp, photonic-encoding, trainability, hardness-under-loss]

# Dependency graph
requires:
  - phase: 20-01
    provides: TRAIN-07 owner interpretation, trainability-study.md literature table, Herbst cross-reference note
  - phase: 20-02
    provides: hardness-under-loss-study.md literature table, Herbst cross-reference note, stale-header fix
  - phase: 20-03
    provides: iqp-photonic-encoding.md's "What ARB-01/ARB-02 does/doesn't establish" subsection and literature table
provides:
  - docs/technical-findings.md, the project's synthesis document for STUDY-01 (trainability), STUDY-02 (hardness-under-loss), and ARB-01/ARB-02 (tunable weight-2 gate)
  - All three source docs' literature comparison tables mirrored into one document
  - Milestone-level "what this project does not establish" scope statement, including the explicit ARB-01/ARB-02-vs-HARD-01..07 gate-family distinction
affects: [21-milestone-writeup]

# Tech tracking
tech-stack:
  added: []
  patterns: ["synthesis-doc-points-at-source-docs, never re-derives"]

key-files:
  created: [docs/technical-findings.md]
  modified: []

key-decisions:
  - "TRAIN's randomness is described via its actual hashed-seed mechanism (trainability/rng.py::derive_seed), not forced into a fabricated single literal seed number to match HARD's different convention."
  - "The HARD-04 owner attempt-first response is linked via docs/hardness-under-loss-study.md's clean top-level heading (#hard-04hard-06-positioning-and-scope-statement-plan-18-08) rather than the malformed two-line subsection heading, whose GitHub anchor slug would not resolve as expected."

patterns-established:
  - "Synthesis document mirrors literature tables verbatim from source docs, with a one-line pointer back to the canonical version -- never re-derives verdicts."

# Metrics
duration: 25 min
completed: 2026-08-18
---

# Phase 20 Plan 04: Technical Findings Synthesis Summary

**Wrote `docs/technical-findings.md`, the project's single project-level synthesis document, mirroring all three source docs' literature tables and pointing at (not re-deriving) their scope statements, the Herbst et al. cross-thread, and the julia-cross-check independent verification.**

## Performance

- **Duration:** 25 min
- **Started:** 2026-08-18T11:10:00Z
- **Completed:** 2026-08-18T11:35:00Z
- **Tasks:** 2
- **Files modified:** 1 (new file)

## Accomplishments

- Created `docs/technical-findings.md` (321 lines) with the full locked structure: title/framing paragraph, three study sections (Trainability, Hardness-under-loss, ARB-01/ARB-02) each with methodology-before-results structure and a link to its source doc's own scope section, a Herbst et al. cross-thread section pointing at both source docs' cross-reference notes, an Independent-verification pointer to `docs/julia-cross-check-study.md`, and a milestone-level "what this project does not establish" section.
- Mirrored all three source docs' literature comparison tables (TRAIN's 6 substantive + 5 silent rows, HARD's 5 substantive + 6 silent rows, ARB's 1 substantive row + prose on the other 10), each carrying a one-line pointer back to its canonical source doc for full reasoning/citations — no verdict drift.
- TRAIN-07's owner interpretation (from Plan 20-01) is summarized (not re-authored) in the Trainability section, closely following the owner's actual recorded reasoning sequence.
- Resolved `20-RESEARCH.md`'s Open Question 3 (TRAIN's RNG-seed traceability): stated TRAIN's actual hashed-seed mechanism (`trainability/rng.py::derive_seed`) rather than fabricating a single literal seed number to force stylistic parity with HARD's `seed_base=180814`.
- Added a closing "Traceability and consistency note" confirming every number traces to an already-cited script/CSV/test and that no claim is softer or stronger than its source doc's own framing.

## Task Commits

Each task was committed atomically:

1. **Task 1: Draft docs/technical-findings.md** - `cfeb50c` (feat)
2. **Task 2: Mirror the three literature tables, verify traceability, and resolve the TRAIN seed question** - `ab5bf7a` (docs)

**Plan metadata:** (this commit, following)

## Files Created/Modified

- `docs/technical-findings.md` - Phase 20's project-level synthesis document: three study sections (Trainability/Hardness-under-loss/ARB-01/ARB-02), mirrored literature tables, Herbst cross-thread pointer, independent-verification pointer, milestone-level scope statement, traceability note.

## Decisions Made

- **TRAIN seed mechanism, not a fabricated number.** TRAIN's randomness is a deterministic, reorder-safe hashed-seed scheme (`trainability/rng.py::derive_seed` — a hash of each cell's own `(n, generator_scope, init_scheme, draw_index)` coordinate tuple), architecturally different from HARD's single literal `seed_base=180814`. Per the plan's own explicit instruction, no single literal seed number was invented for TRAIN to force stylistic parity with HARD — doing so would misrepresent TRAIN's actual (and more robust) per-coordinate-hashed design as a single-seed design it isn't. WRITE-06's "fixed seed where randomness is involved" requirement is satisfied via an accurate mechanism citation instead.
- **HARD-04 link target corrected during the traceability pass.** `docs/hardness-under-loss-study.md`'s "Owner's attempt-first response" text is actually written as a two-line markdown heading (`### Owner's attempt-first response (recorded as-given, per this project's` / `### \`CLAUDE.md\` attempt-first gating and the ENC-01/ARB-02 transcript style)`), which does not slugify to a single clean GitHub anchor the way a normal one-line heading would. The synthesis doc links instead to the clean, single-line parent heading (`## HARD-04/HARD-06: Positioning and Scope Statement (Plan 18-08)`, anchor `#hard-04hard-06-positioning-and-scope-statement-plan-18-08`) and notes in prose that the owner's attempt-first response is its first subsection.

## Deviations from Plan

None - plan executed exactly as written. The task split (Task 1: draft the full locked structure including tables; Task 2: verify traceability, resolve the seed question, and fix a link found during that verification pass) matches the plan's own two-task breakdown; Task 2's work was captured as a distinct, real follow-up commit (the anchor-link fix plus the closing traceability note), not a no-op.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

**This closes Phase 20.** All 4 plans (20-01, 20-02, 20-03, 20-04) are now shipped. WRITE-01 (methodology-before-results, now satisfied at both the per-source-doc level and the project/synthesis level), WRITE-02 (literature tables, authored canonically in each source doc and mirrored here), WRITE-03 (honest negative/inconclusive framing preserved throughout, including in this synthesis document), WRITE-05 (TRAIN-07's genuine self-explanation gap closed in Plan 20-01 and reflected, not re-authored, here), and WRITE-06 (every number traceable; TRAIN's seed mechanism accurately described) are all now satisfiable from this phase's shipped artifacts. Phase 21 (external-facing write-up/reframing, per `20-CONTEXT.md`'s explicit "Phase 21's separate job" scoping) can now draw on `docs/technical-findings.md` as its internal/candid source-of-truth synthesis, without needing to re-derive or re-litigate any of Phase 17/17.1/18's findings.

No blockers or concerns carried forward.

---
*Phase: 20-technical-write-up*
*Completed: 2026-08-18*
