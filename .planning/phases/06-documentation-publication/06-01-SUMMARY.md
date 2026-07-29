---
phase: 06-documentation-publication
plan: 01
subsystem: docs
tags: [readme, license, documentation, publication, mmd, photonic]

# Dependency graph
requires:
  - phase: 05-benchmarking
    provides: "results/phase5_summary.md (citation-ready headline numbers), results/phase4_summary.md (GEN-07 verdict)"
provides:
  - "README.md at repo root: problem/approach/results with real numbers and embedded plots, GEN-07 'not met' stated near the top, AI-disclosure sections (top one-liner + bottom Process & AI Use section)"
  - "LICENSE (MIT, Alejandro Jackson, 2026)"
  - "docs/mmd-loss.md and docs/raster-order.md (moved from repo root, now tracked and linked from README)"
  - ".planning/phases/06-documentation-publication/06-technical-note.md — 4-sentence LinkedIn-style draft for Vincent Espitalier"
  - "Verified 48/48 pytest suite passing as the DOC-02 runnable-code check"
  - "All commits pushed to origin/master; repo visibility confirmed unchanged (PRIVATE)"
affects: ["06-02 (portfolio case study — can now link to the same real numbers and README framing)"]

# Tech tracking
tech-stack:
  added: []
  patterns: ["Ownership-forward AI-disclosure framing for public deliverables (memory: phase6-ai-disclosure-framing)"]

key-files:
  created: [README.md, LICENSE, docs/mmd-loss.md, docs/raster-order.md, .planning/phases/06-documentation-publication/06-technical-note.md]
  modified: []

key-decisions:
  - "Used Phase 5's re-measured ring_mass/gap_mass (0.6833±0.0073 / 0.0514±0.0035) as the README's headline benchmark numbers rather than Phase 4's original 0.691/0.048, since Phase 5 is the more recent independent re-measurement of the same checkpoint — both are consistent (within one std), noted as such in results/phase5_summary.md."
  - "README 'How to run' points to natural_order_train.py (the GEN-07 checkpoint variant) as the primary entry point, not quickstart.py (MerLin's own unrelated classifier example) — per explicit plan guidance and 06-RESEARCH.md's Pitfall 1."
  - "Technical note includes the actual (currently private) GitHub URL rather than a placeholder — it will resolve once the owner flips repo visibility, which is an explicit manual step outside this plan's scope."

patterns-established:
  - "Public-facing prose (README, technical note) passes through a humanizer self-review pass (em dashes, rule-of-three, promotional language, negative parallelisms) before commit — internal docs (DESIGN_DECISIONS.md, SUMMARY.md files) are exempt and stay candid/technical as-is."

# Metrics
duration: ~35min
completed: 2026-07-29
---

# Phase 6 Plan 1: Documentation & Publication Summary

**README with embedded results plots and honest GEN-07 headline, MIT LICENSE, two mechanism deep-dives moved into docs/, and a 4-sentence technical-note draft for Vincent Espitalier — all committed and pushed to origin/master, repo left private for the owner's manual visibility toggle.**

## Performance

- **Duration:** ~35 min
- **Tasks:** 3/3
- **Files modified:** 5 created (README.md, LICENSE, docs/mmd-loss.md, docs/raster-order.md, 06-technical-note.md)

## Accomplishments

- Moved `mmd-loss.md` and `raster-order.md` from untracked repo-root scratch files into `docs/`, now tracked and linked from the README as deep-dive reading.
- Added an MIT `LICENSE` (Alejandro Jackson, 2026).
- Verified the full pytest suite (48/48) passes as DOC-02's "working, runnable code" check.
- Wrote `README.md`: states GEN-07's "not met" result plainly in a dedicated "Headline result" section near the top (not buried), with the real Phase 5 numbers (held-out MMD²=0.0125±0.0003 trained vs 0.0360±0.0048 untrained vs 0.0114 floor; ring_mass=0.6833±0.0073; gap_mass=0.0514±0.0035) and the measured improvement path (ring_mass 0.609→0.691). Embeds `results/phase3_loss_curve.png` and `results/phase4_natural_comparison.png`, copies Phase 5's headline table verbatim, and links out to `DESIGN_DECISIONS.md`, both `docs/` deep-dives, and both phase summary files.
- Two AI-disclosure mentions in the README (a one-line "How this was built" near the top and a fuller "Process & AI Use" section near the bottom), both using the ownership-forward framing from memory `phase6-ai-disclosure-framing` ("I verify every AI-assisted component against my own unaided explanation before it ships") rather than "the AI caught my mistake" framing. Internal artifacts (`NOTES.md`, `DESIGN_DECISIONS.md`) are referenced as the evidence trail, not scrubbed.
- Drafted `.planning/phases/06-documentation-publication/06-technical-note.md`: a 4-sentence, LinkedIn-message-style note that opens with the IQP-MMD methodology connection, states the photonic result, gives the GEN-07 shortfall exactly one honest clause ("though it's not fully clean yet"), and has no explicit CTA.
- Both README's prose sections and the technical note were passed through a humanizer self-review (per the phase's `/humanizer` flag) before commit — em dashes, inflated framing ("throughline of this whole project"), and other AI-writing tells were rewritten; the numeric table and code blocks were left untouched/verbatim.
- All three tasks committed atomically and pushed to `origin/master`. Repo visibility confirmed still `PRIVATE` via `gh repo view` — not touched, per plan.

## Task Commits

Each task was committed atomically:

1. **Task 1: Move deep-dive docs, add LICENSE, verify repo cleanliness** - `b9b772a` (docs)
2. **Task 2: Write README.md** - `3961200` (docs)
3. **Task 3: Draft technical note, final push** - `0d69ef8` (docs)

## Files Created/Modified

- `README.md` - Problem/approach/results writeup with real numbers, embedded plots, links to deep-dive docs, two AI-disclosure sections
- `LICENSE` - MIT license text, copyright Alejandro Jackson 2026
- `docs/mmd-loss.md` - Moved from repo root (mechanism deep-dive: MMD implementation comparison vs. prior IQP project)
- `docs/raster-order.md` - Moved from repo root (mechanism deep-dive: radius-sorted bin ordering fix)
- `.planning/phases/06-documentation-publication/06-technical-note.md` - Draft technical note text for Vincent Espitalier, ready to copy-paste

## Decisions Made

- README's benchmark table uses Phase 5's re-measured ring_mass/gap_mass (0.6833±0.0073 / 0.0514±0.0035) as the headline figures rather than Phase 4's original run (0.691/0.048), since Phase 5 is the more recent, independently re-measured number against the same checkpoint. Both figures (and the 0.609→0.691 improvement path) appear in the README so neither reading is hidden.
- Technical note includes the real (currently private) GitHub repo URL rather than a placeholder, since it becomes valid the moment the owner flips visibility — deferring URL-writing to a later manual step would just create more busywork for no benefit.
- Applied a humanizer self-review pass to README prose and the technical note per this execution's explicit `/humanizer` instruction, leaving the numeric table, code blocks, and commands untouched. This is scoped to this execution's flag, not established as a standing repo convention beyond Phase 6's public deliverables.

## Deviations from Plan

None — plan executed exactly as written. `git mv` failed on both `mmd-loss.md`/`raster-order.md` (as the plan itself anticipated: "these are currently untracked — then `git add`"), so a plain `mv` was used instead, matching the plan's own fallback instruction.

## Issues Encountered

None. `python -m pytest -q` ran longer than the default 3-minute foreground timeout and was moved to background by the tool automatically; it completed cleanly (48 passed in 159.41s) and the commit proceeded once confirmed.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- DOC-01 (README with real numbers/plots), the packaging half of DOC-02 (working runnable code, prepared+pushed public-ready repo, visibility left to owner), and DOC-03 (technical note ready to send) are all satisfied for `merlin-quantum-case-study`.
- Repo remains PRIVATE. Owner's next manual step, whenever ready: `gh repo edit alejack312/merlin-photonic-generative-modeling --visibility public` or the GitHub UI.
- Plan 06-02 (portfolio case study in the separate `alejandro-jackson` repo, DOC-04) was not touched by this plan and remains open — per 06-CONTEXT.md/06-RESEARCH.md, it's cross-repo work with its own toolchain (Next.js/npm) and its own commit boundary.
- No blockers identified for 06-02.

---
*Phase: 06-documentation-publication*
*Completed: 2026-07-29*
