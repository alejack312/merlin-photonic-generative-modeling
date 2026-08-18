---
phase: 20-technical-write-up
plan: 01
subsystem: docs
tags: [trainability, barren-plateau, literature-review, mmd, iqp, citation-verification]

# Dependency graph
requires:
  - phase: 17-trainability-barren-plateau-study
    provides: TRAIN-01..08's shipped gradient-variance/curve-fit results and docs/trainability-study.md's scaffolded TRAIN-07 cross-reference table
  - phase: 17.1-trainability-follow-up-bandwidth-init-sensitivity
    provides: TRAIN-09/TRAIN-10's bandwidth-sensitivity and data-dependent-init follow-up results, already folded into docs/trainability-study.md
  - phase: 18-hardness-under-loss-assessment
    provides: docs/hardness-under-loss-study.md's own Herbst et al. cross-reference note (HARD-side half), written by a parallel plan in this phase
provides:
  - TRAIN-07 closed with the owner's own unaided (self-explanation-checkpoint) interpretation, transcribed verbatim
  - A literature comparison table (WRITE-02) covering all 11 baselines for TRAIN
  - A Herbst et al. cross-reference note (success criterion 6, TRAIN half) pointing at docs/hardness-under-loss-study.md
affects: [21-external-facing-framing-pass]

# Tech tracking
tech-stack:
  added: []
  patterns: ["arXiv API live citation confirmation (curl export.arxiv.org/api/query) for a baseline this repo has no downloaded PDF for, with confidence tier stated honestly rather than silently upgraded to full-PDF-read confidence"]

key-files:
  created: []
  modified:
    - docs/trainability-study.md

key-decisions:
  - "TRAIN-07's interpretation is owner-authored, transcribed verbatim (including a ruled-out first hypothesis) per this project's CLAUDE.md self-explanation-checkpoint rule -- not written or polished by Claude."
  - "McClean et al.'s citation confirmed live via the arXiv API (arXiv:1803.11173, Nature Communications 9, 4812 (2018)) rather than trusted from prior WebSearch-sourced summaries -- but flagged at a lower confidence tier than the other 10 baselines, which all have a downloaded PDF in docs/papers/, since this was an abstract/metadata fetch, not a full paper read."
  - "TRAIN's Herbst cross-reference note is deliberately hedged: TRAIN never varies eta (all data is at eta=1), so it cannot itself confirm or refute Herbst et al.'s eta-dependent co-occurrence prediction -- the note states what TRAIN's zero-loss data can and cannot establish, then points at HARD's own note for the eta-side measurement, rather than asserting a joint verdict."

patterns-established:
  - "Literature comparison table format (substantive rows with theorem/section citations + reasoning, silent rows as one-liners) matches docs/hardness-under-loss-study.md's own WRITE-02 table -- both phase documents now use the same structure for cross-baseline positioning."

# Metrics
duration: ~35min
completed: 2026-08-18
---

# Phase 20 Plan 01: TRAIN-07 Self-Explanation Checkpoint + Literature Table Summary

**Owner's own multi-step reasoning (including a ruled-out hypothesis) closed TRAIN-07's genuinely open interpretation gap; added an 11-baseline WRITE-02 literature table and a hedged Herbst et al. cross-reference note to docs/trainability-study.md.**

## Performance

- **Duration:** ~35 min (across the human checkpoint pause)
- **Tasks:** 2 (1 blocking human-action checkpoint, 1 auto)
- **Files modified:** 1 (`docs/trainability-study.md`, +231/-1 lines)

## Accomplishments

- TRAIN-07's `> Owner interpretation: [pending]` placeholder (`docs/trainability-study.md:174`) replaced with the owner's actual, unaided, multi-step reasoning trajectory — not a Claude-authored interpretation, and not the exception waiver (the owner engaged directly, including a hypothesis that was tried and ruled out).
- New `### Literature comparison table (WRITE-02)` subsection covering all 11 baselines: 6 substantive rows with theorem/section-level citations and TRAIN-specific reasoning (McClean et al., `docs/iqp-baseline.md`'s own rule, Rudolph et al., Mhiri et al., Recio-Armengol et al., Herbst et al.), 5 one-line silent rows (Aaronson-Brod, Park & Oh, arXiv:2405.01395, BMS 2015, BMS 2017).
- New `### Cross-reference: Herbst et al.'s anticoncentration-tradeoff prediction` subsection, stating TRAIN's measured facts, TRAIN's structural inability to test the eta-axis directly, a pointer to HARD's own equivalent note, and a hedged combined statement.

## Task Commits

Each task was committed atomically:

1. **Task 1: TRAIN-07 self-explanation checkpoint** — no commit (checkpoint task, no file changes; owner's interpretation gathered via the orchestrator relay)
2. **Task 2: Transcribe interpretation + add literature table + Herbst note** — `4f58319` (docs)

**Plan metadata:** this commit (docs: complete plan) — see below

## Files Created/Modified

- `docs/trainability-study.md` — TRAIN-07's placeholder replaced with the owner's transcribed interpretation; new Literature comparison table (WRITE-02) subsection; new Herbst et al. cross-reference subsection. 778 lines total (was 548-ish before this plan), all changes additive except the single-line placeholder replacement.

## Decisions Made

- **TRAIN-07 checkpoint honored literally, not shortcut:** the owner engaged with the actual question (why does `weight1/uniform` agree with the sibling project's empirical rule while `mixed/uniform` disagrees?), tried a first hypothesis (`complete_graph_like`) that didn't hold up under the rule's own structure, reviewed raw fitted parameters and per-n gradient-variance values, asked a mechanical curve-fitting question, checked what the literature actually claims, and revised an initial (slightly overreaching) framing after pushback — the full trajectory is transcribed, not just the final conclusion.
- **McClean et al.'s citation was verified live** via a direct arXiv API query (`curl https://export.arxiv.org/api/query?...`) rather than trusted from this repo's own prior WebSearch-sourced summaries (`20-RESEARCH.md`'s flagged gap) — confirmed arXiv:1803.11173, *Nature Communications* 9, 4812 (2018), and its abstract confirms the gradient-variance-vs-system-size protocol shape Phase 17's methodology uses. This is stated as a lower-confidence-tier confirmation (abstract/metadata fetch, not a full PDF read) than the other 10 baselines, all of which have a downloaded PDF in `docs/papers/` — never silently presented at the same confidence.
- **TRAIN's Herbst cross-reference is deliberately hedged, not asserted as a joint verdict:** TRAIN's entire dataset is measured at `eta=1` (no loss) — it can establish that a genuine (if bandwidth-fragile, per TRAIN-09) untrainability signature exists for `uniform` init at zero loss, but cannot itself test Herbst et al.'s eta-dependent co-occurrence prediction. The note points at `docs/hardness-under-loss-study.md`'s own equivalent note (written by a parallel plan in this phase) for the eta-side measurement, and states explicitly what remains untested (TRAIN's own gradient variance was never measured as a function of eta in this project).

## Deviations from Plan

None — plan executed exactly as written. The checkpoint (Task 1) was honored per the plan's mandatory-blocking gate; the owner's real answer (including the ruled-out first hypothesis) was relayed by the orchestrator and transcribed verbatim, not authored by Claude, and the "just write something reasonable" waiver was never invoked.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- WRITE-02 (TRAIN's table), WRITE-05 (TRAIN-07's recorded checkpoint), and success criterion 6 (TRAIN half) are all satisfied for this plan's scope.
- `docs/trainability-study.md`'s HARD-side counterpart cross-reference note already exists in `docs/hardness-under-loss-study.md` (written by a parallel plan, `20-02`, in this same phase) — both halves of the TRAIN/HARD cross-reference are now on record, each correctly hedged and pointing at the other rather than restating it.
- No blockers for the rest of Phase 20 or for Phase 21 (External-Facing Framing Pass). Ready for whichever plan is next in this phase's wave structure.

---
*Phase: 20-technical-write-up*
*Completed: 2026-08-18*
