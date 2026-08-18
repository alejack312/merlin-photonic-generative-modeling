---
phase: 20-technical-write-up
plan: 02
subsystem: docs
tags: [iqp, hardness-under-loss, literature-review, anticoncentration, write-up]

# Dependency graph
requires:
  - phase: 18 (Hardness-Under-Loss Assessment)
    provides: "the real measured HARD-01..07 datasets (TVD-vs-eta, anticoncentration alpha(eta), herald compounding) this plan's table and cross-reference note cite, not re-derive"
provides:
  - "docs/hardness-under-loss-study.md gains a literature comparison table (WRITE-02) covering all 11 named baselines, filtered to HARD-specific relevance"
  - "docs/hardness-under-loss-study.md gains a Herbst et al. cross-reference note (success criterion 6, HARD half), correcting docs/iqp-baseline.md's earlier speculative anticoncentration-direction guess"
  - "docs/hardness-under-loss-study.md's stale header note (previously claiming HARD-04/HARD-06 don't exist) is corrected"
affects: [21-external-facing-framing-pass, technical-findings-synthesis-doc]

# Tech tracking
tech-stack:
  added: []
  patterns: ["Literature comparison table + citation-precision prose, mirroring docs/iqp-baseline.md's 'Fresh Primary-Source Verification' section style"]

key-files:
  created: []
  modified: ["docs/hardness-under-loss-study.md"]

key-decisions:
  - "5 substantive rows (Aaronson-Brod, Park & Oh Theorem 1, BMS 2017, BMS 2015, Herbst et al.) get real paragraphs; 6 one-line silent rows for TRAIN/ARB-specific baselines -- avoids a table full of undifferentiated 'silent'."
  - "Aaronson-Brod and Park & Oh Theorem 1 both verdicted 'silent' rather than forced consistent/inconsistent -- neither offers a falsifiable numeric hardness prediction this project's measured TVD/alpha values could agree or disagree with; both are structural/regime observations, already reached elsewhere in the doc, restated here rather than re-derived."
  - "Herbst et al.'s HARD-side verdict is 'inconsistent' -- the measured alpha(eta) direction (decreasing as eta decreases, i.e. MORE anticoncentrated under loss) is the reverse of docs/iqp-baseline.md's original speculative guess, stated as a correction rather than smoothed over."

patterns-established:
  - "Cross-reference notes between sibling source docs (TRAIN/HARD) point at each other's equivalent section rather than restating the other's findings -- keeps each document's substantive content owned by its own phase's data."

# Metrics
duration: ~20min
completed: 2026-08-18
---

# Phase 20 Plan 02: HARD Literature Table and Herbst Cross-Reference Summary

**Added HARD's WRITE-02 literature comparison table (11 baselines, 5 substantive + 6 silent) and a Herbst et al. cross-reference note to `docs/hardness-under-loss-study.md`, correcting an earlier speculative anticoncentration-direction guess in `docs/iqp-baseline.md` and fixing a stale header note left over from before Plan 18-08 completed the document.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-08-18T01:10:00Z
- **Completed:** 2026-08-18T01:30:00Z
- **Tasks:** 2
- **Files modified:** 1

## Accomplishments

- New `### Literature comparison table (WRITE-02)` subsection inserted immediately before `### HARD-06: What this phase does and does not establish`, covering all 11 WRITE-02 baselines with a stated verdict each.
- New `### Cross-reference: Herbst et al.'s anticoncentration-tradeoff prediction` section appended at the end of the document, stating HARD's real measured `alpha(eta)` direction, explicitly correcting `docs/iqp-baseline.md`'s earlier speculative guess of the opposite direction, and pointing at `docs/trainability-study.md`'s equivalent note for the TRAIN half.
- Stale header note (previously claiming HARD-04/HARD-06 sections don't yet exist) corrected to list all sections the document actually contains, including this phase's two additions.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add HARD's literature comparison table** - `9195d06` (docs)
2. **Task 2: Add the Herbst cross-reference note and fix the stale header note** - `610230d` (docs)

## Files Created/Modified

- `docs/hardness-under-loss-study.md` — added the Literature comparison table (WRITE-02) subsection before `### HARD-06`; added the Herbst et al. cross-reference note at the end of the document; corrected the stale header paragraph (lines 9-12 originally).

## Decisions Made

- **Aaronson-Brod and Park & Oh Theorem 1 verdicted "silent," not forced into consistent/inconsistent.** Both baselines' own text/scope precludes a falsifiable numeric hardness prediction comparable to HARD's measured TVD/alpha values (AB's guarantee is regime-mismatched for this project's fractional-rate loss model; Park & Oh Theorem 1 bounds one classical algorithm's efficiency, not a hardness lower bound). This restates verdicts the document's own pre-existing "Dual/triple positioning" section already reached — not a new interpretive call.
- **BMS 2017 verdicted "silent by owner decision," distinct in kind from AB/Park&Oh's "silent by regime mismatch."** No `eta`-to-`epsilon` translation exists (the owner's on-record HARD-04 decision), so no honest numeric comparison against Theorem 4 is possible — this is a decision-driven silence, not a scope-driven one, and the table/prose keep that distinction explicit rather than collapsing all three "silent" rows into one undifferentiated bucket.
- **Herbst et al. verdicted "inconsistent."** HARD's own measured `alpha(eta)` decreases as `eta` decreases (loss increases anticoncentration, not erodes it) — the reverse of `docs/iqp-baseline.md`'s 2026-08-12 speculative guess that photon loss would erode anticoncentration and thereby improve trainability at higher loss. This is stated as a correction, following this project's established pattern of catching and fixing its own earlier speculative statements once real data exists.
- **The TRAIN/HARD cross-reference is explicitly hedged, not asserted as a joint result.** TRAIN sweeps `n` at `eta=1` (no loss); HARD sweeps `eta` at small fixed `n` — the two phases share no common independent variable, so Herbst et al.'s co-occurrence prediction cannot be directly tested on one combined dataset. The note states this qualification explicitly and flags the cross-reference as requiring the owner's own review before being treated as settled, per this project's `CLAUDE.md` convention that Claude organizes/computes but does not assert interpretive conclusions on the owner's behalf.

## Deviations from Plan

None — plan executed exactly as written. Both tasks' content matched the plan's detailed per-baseline assignment and Herbst-note specification directly.

## Issues Encountered

**Concurrent-session commit-attribution mixing (same documented pattern as Phase 18's Plans 18-02/18-03/18-04, and this phase's own Plan 20-03).** Task 2's `git commit` (`git add docs/hardness-under-loss-study.md`, explicit single-file staging — never `git add -A`/`git add .`) swept in three additional files that a concurrent session executing Plan 20-03 had already staged in the shared git index before this commit ran: `.planning/ROADMAP.md`, `.planning/STATE.md`, and the new `.planning/phases/20-technical-write-up/20-03-SUMMARY.md`. Commit `610230d` therefore contains both this plan's real Task 2 diff and Plan 20-03's already-completed, already-committed-to-disk-but-not-yet-git-committed metadata. Verified before proceeding: `git show HEAD -- <each file>` confirmed the swept-in content is Plan 20-03's own genuine, complete work (matches `20-03-SUMMARY.md`'s own account, commit `0ae0a0c` for the actual code/docs change already exists independently on the branch) — not corrupted, not misattributed to this plan's task, and not touched or reset. No history was rewritten, consistent with this project's established handling of this exact failure mode in Phase 18.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- WRITE-02 (HARD's table, all 11 baselines) and success criterion 6 (HARD half of the Herbst cross-thread) are now satisfied for `docs/hardness-under-loss-study.md`.
- This plan is independent of Plan 20-01 (TRAIN) and Plan 20-03 (ARB, already shipped) — no blockers exist between them. Plan 20-01 (TRAIN-07 checkpoint + TRAIN literature table + Herbst note) and Plan 20-04 (`docs/technical-findings.md` synthesis doc) remain to complete Phase 20.
- `docs/trainability-study.md`'s own equivalent Herbst cross-reference note (Plan 20-01's job) does not yet exist as of this plan's completion — this plan's note points at it by section name/pointer only, consistent with the plan's own instruction not to assume or restate TRAIN-side content; no blocker for Plan 20-01, which can add its own note independently at any time.
- No blockers for Phase 20's remaining plans.

---
*Phase: 20-technical-write-up*
*Completed: 2026-08-18*
