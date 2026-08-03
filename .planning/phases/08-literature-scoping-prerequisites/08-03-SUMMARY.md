---
phase: 08-literature-scoping-prerequisites
plan: 03
subsystem: docs
tags: [iqp, barren-plateau, quantum-ml, literature-review, photonic-encoding]

# Dependency graph
requires:
  - phase: 08 (this phase, plan 01)
    provides: docs/iqp-lit-scoping.md (DV IQP structure baseline + Douce et al. CV-IQP summary), cross-referenced from this doc
provides:
  - docs/iqp-baseline.md — qubit-side IQP structure/hardness + barren-plateau trainability reference doc
affects: [09-encoding-design]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Grounding-statement house style: reference docs open by naming exact source files read, not re-deriving from memory (matches docs/mmd-loss.md, docs/iqp-lit-scoping.md convention)"

key-files:
  created: [docs/iqp-baseline.md]
  modified: []

key-decisions:
  - "Covered IQP structure/hardness and barren-plateau trainability with roughly equal section length/depth per 08-CONTEXT.md's explicit weighting instruction, rather than letting one dominate."
  - "Cross-referenced docs/iqp-lit-scoping.md by name (for the DV structural skeleton Douce et al. builds its CV analogue from) instead of duplicating that content, keeping this doc to its 1-2 page scope."

patterns-established:
  - "Short qubit-side reference docs (iqp-lit-scoping.md, iqp-baseline.md) can run ~30-45 lines by wc -l while still being dense, page-length prose — line count alone understates content; word count (~900) is the better proxy for '1-2 pages' in this repo's house style of unwrapped long-line paragraphs."

# Metrics
duration: ~20min
completed: 2026-08-03
---

# Phase 8 Plan 3: Qubit-Side IQP Baseline Doc Summary

**Compiled `docs/iqp-baseline.md` — a 1-2 page reference covering IQP's commuting-diagonal-gate structure (Van den Nest's cosine formula for classical training) and the empirical barren-plateau finding (structure alone doesn't predict plateaus; a 97.9%-accurate init+size+escape-hatch rule does) as Phase 9's qubit-side comparison baseline.**

## Performance

- **Duration:** ~20 min
- **Started:** 2026-08-03T20:20:00Z (approx.)
- **Completed:** 2026-08-03T20:44:11Z
- **Tasks:** 2 (1 read-only, 1 file-producing)
- **Files modified:** 1

## Accomplishments
- Read all three source files from the sibling `iqp-mmd-barren-plateau` project in full (not skimmed): the classical-sampling technical doc, the Barren Plateaus theory note, and the Final Findings report.
- Wrote `docs/iqp-baseline.md`: grounding statement naming all three sources, `## IQP Circuit Structure & Hardness`, `## Barren-Plateau Trainability`, and `## Why This Matters for Phase 9` — both technical sections roughly balanced in depth, per 08-CONTEXT.md's requirement.
- Satisfied PREQ-02: Phase 9 now has a compact, grounded qubit-side reference doc instead of needing to re-read the sibling project's full paper/vault stash.

## Task Commits

Task 1 (reading the three source files) produced no file changes and was not committed separately, per the plan's own `<files>` annotation ("no files modified — reading only").

1. **Task 2: Write docs/iqp-baseline.md** - `99f6443` (docs)

**Plan metadata:** (this commit, made alongside STATE.md update)

## Files Created/Modified
- `docs/iqp-baseline.md` - Qubit-side IQP structure/hardness + barren-plateau trainability reference doc, grounded in three named sibling-project source files, closing with a bridging paragraph for Phase 9.

## Decisions Made
- Weighted the two technical sections roughly equally (both ~5 bullet points, similar prose density) rather than letting the hardness section dominate just because more source material existed for it — matches 08-CONTEXT.md's explicit instruction.
- Cross-referenced `docs/iqp-lit-scoping.md` by name for the Douce et al. CV-analogue connection instead of restating that doc's content, keeping this doc within its 1-2 page reference-glossary scope.
- Confirmed the doc's 42-line length against the min_lines: 40 artifact requirement and against `docs/iqp-lit-scoping.md`'s own precedent (32 lines, 885 words) — both are dense long-line prose docs consistent with this repo's house style, so line count alone was not treated as the sole scope signal; word count (899) was cross-checked as a better "1-2 pages" proxy.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

`docs/iqp-baseline.md` is in place as one of PREQ-02's required prerequisite artifacts for Phase 9 (Encoding Design). Phase 9 remains sequentially contingent on this phase's overall LIT-04 go/no-go verdict (produced by 08-01/08-02, not this plan) — no blockers introduced by this plan specifically.

---
*Phase: 08-literature-scoping-prerequisites*
*Completed: 2026-08-03*
