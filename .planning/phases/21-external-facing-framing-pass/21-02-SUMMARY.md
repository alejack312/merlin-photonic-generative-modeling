---
phase: 21-external-facing-framing-pass
plan: 02
subsystem: docs
tags: [readme, external-framing, v3.0]

# Dependency graph
requires:
  - phase: 20-technical-write-up
    provides: "docs/technical-findings.md — the locked-numbers source this plan quotes from directly"
provides:
  - "README.md v3.0 pitch section, distinct from and linking out to docs/technical-findings.md and the portfolio case-study page"
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns: ["README top-level sections stay short (4-8 sentences + links list), pointing readers to docs/ for full detail rather than restating it"]

key-files:
  created: []
  modified: ["README.md"]

key-decisions:
  - "Used the production URL https://alejandrojackson.dev/case-studies/merlin-quantum as given in the plan's important_notes (superseding 21-RESEARCH.md's stale-URL flag) — no hedging language needed."
  - "Kept the AI-disclosure extension to one sentence pointing at the case study for a concrete v3.0 example, rather than duplicating the existing Process & AI Use paragraph."

patterns-established: []

# Metrics
duration: 10min
completed: 2026-08-18
---

# Phase 21 Plan 02: README v3.0 Pitch Section Summary

**Added a short "v3.0: IQP Circuit Study" section to README.md — honest co-lead-findings pitch (including the sigma-grid negative result and the no-eta-translation scope call) that links out to the case-study page and `docs/technical-findings.md` instead of restating them.**

## Performance

- **Duration:** ~10 min
- **Started:** 2026-08-18T23:25:00Z
- **Completed:** 2026-08-18T23:36:00Z
- **Tasks:** 1
- **Files modified:** 1

## Accomplishments
- README.md now has a `## v3.0: IQP Circuit Study` section between `## Process & AI Use` and `## License`, giving GitHub-landing readers a v3.0 pitch that previously didn't exist (README stopped at v1.0).
- Both co-lead findings (trainability, hardness-under-loss) stated with their honest negative/inconclusive verdicts intact — the sigma-grid bandwidth non-robustness and the deliberate no-eta-to-depolarizing-rate-translation scope call are both named, not smoothed into pure-positive marketing language.
- Section links out to the live case-study page and `docs/technical-findings.md` rather than restating their content, per this plan's must-have.

## Task Commits

1. **Task 1: Add "v3.0: IQP Circuit Study" section to README.md** - `76456a8` (docs)

**Plan metadata:** (this commit, docs(21-02): complete plan)

## Files Created/Modified
- `README.md` - New `## v3.0: IQP Circuit Study` section (18 lines) inserted between `## Process & AI Use` and `## License`; all content above and below the insertion point verified byte-identical via `git diff` (insertion-only diff, no deletions).

## Decisions Made
- Production case-study URL: used `https://alejandrojackson.dev/case-studies/merlin-quantum` exactly as specified in the plan's `important_notes` (owner-confirmed at execution time, superseding the research doc's stale `vercel.app` flag) — no hedging caveat added to the README text, per the plan's explicit instruction.
- Kept the AI-disclosure extension to one sentence that points at the case study for a concrete v3.0 example (the TRAIN-07 transcribed-reasoning example) rather than re-explaining the whole disclosure paragraph — avoids duplicating the existing `## Process & AI Use` section above it.
- Included all three optional source-doc links (`trainability-study.md`, `hardness-under-loss-study.md`, `iqp-photonic-encoding.md`, `julia-cross-check-study.md`) since they read naturally alongside the required two links — the plan flagged this as optional/discretionary, not required.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered
None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- This closes WRITE-07's README half. Combined with Plan 21-01 (portfolio case-study page, independent/parallel — no `21-01-SUMMARY.md` existed on disk at the time this plan executed, consistent with the two plans running in the same wave with no dependency between them), Phase 21's two artifacts (README pitch + case-study page) are both scoped to complete WRITE-07.
- No blockers for Phase 21 completion from this plan's side. The owner should do a final visual/markdown-render check of the new README section (not required by this plan's verification, which was git-diff-based) before the v3.0 milestone is declared complete.

---
*Phase: 21-external-facing-framing-pass*
*Completed: 2026-08-18*
