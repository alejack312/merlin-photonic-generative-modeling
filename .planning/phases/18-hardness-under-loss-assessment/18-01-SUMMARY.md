---
phase: 18-hardness-under-loss-assessment
plan: 01
subsystem: docs
tags: [boson-sampling, hardness, literature, arxiv, aaronson-brod, park-oh]

# Dependency graph
requires:
  - phase: 18-hardness-under-loss-assessment (research)
    provides: 18-RESEARCH.md's Finding 1-2 (Park & Oh authorship correction, Theorem 1 vs Section V distinction) and Open Question 1 (genuine Aaronson-Brod paper unread)
provides:
  - "docs/papers/1510.05245.pdf — locally-saved, full-text-read copy of the genuine Aaronson-Brod paper"
  - "docs/iqp-baseline.md — two new citation bullets (Park & Oh Theorem 1; Aaronson-Brod fixed-loss-count Theorem 1) with verbatim-quoted formulas/thresholds, explicitly distinguished from each other and from Park & Oh's Section V"
affects: [18-04 (baselines/anticoncentration), 18-08 (HARD-04 positioning derivation), 20 (technical write-up)]

# Tech tracking
tech-stack:
  added: []
  patterns: []

key-files:
  created:
    - docs/papers/1510.05245.pdf
  modified:
    - docs/iqp-baseline.md

key-decisions:
  - "Cited Park & Oh's Theorem 1 (lossy-boson-sampling/passive-linear-optics, eta=Theta(1/sqrt(N))) as the physically-matching result, explicitly excluding the same paper's Section V ('Noisy IQP Sampling', qubit-level Pauli-noise) despite its more tempting label."
  - "Stated plainly that Aaronson-Brod's noise model is a fixed constant count k of lost photons, structurally different from this project's fractional-rate eta model, and flagged (from the paper's own text, not inference) that this project's fixed-eta-as-n-grows regime falls into the paper's weak 'constant fraction lost' case, which the authors themselves say gives no strong complexity claim."

patterns-established: []

# Metrics
duration: ~25min
completed: 2026-08-14
---

# Phase 18 Plan 01: Aaronson-Brod Literature Read & Citation Correction Summary

**Downloaded and fully read the genuine Aaronson-Brod paper (arXiv:1510.05245) for the first time in this project, and added two verbatim-quoted, explicitly-distinguished citation bullets to `docs/iqp-baseline.md` — correcting `18-CONTEXT.md`'s original misattribution of arXiv:2510.24137 as "Aaronson-Brod" before it could propagate further.**

## Performance

- **Duration:** ~25 min
- **Tasks:** 2/2 completed
- **Files modified:** 2 (1 created, 1 modified)

## Accomplishments
- Downloaded `docs/papers/1510.05245.pdf` (13 pages, valid PDF) and read it in full (not abstract-only), extracting Theorem 1's exact statement, its fixed-count-k noise model, and the paper's own discussion of how that model degrades as k scales with n.
- Added two new, clearly-separated citation bullets to `docs/iqp-baseline.md`'s existing "Fresh Primary-Source Verification (2026-08-12)" section: Park & Oh (arXiv:2510.24137) Theorem 1, and the genuine Aaronson-Brod paper (arXiv:1510.05245) — each with verbatim-quoted formulas/thresholds and an explicit relevance statement, closed by one shared sentence stating the two papers are distinct and must never be merged.
- HARD-03 is now satisfied in full for both papers this phase's hardness-vs-loss claim depends on; HARD-04's literature groundwork is in place for Plan 18-08.

## Task Commits

Each task was committed atomically:

1. **Task 1: Download and fully read arXiv:1510.05245** - `0d2c992` (docs)
2. **Task 2: Document both papers into docs/iqp-baseline.md's Fresh Primary-Source Verification section** - `8816a21` (docs)

_Note: no plan-metadata commit issued separately — Task 2's commit message already documents the plan's full intent; this SUMMARY.md/STATE.md update is the final commit for this plan._

## Files Created/Modified
- `docs/papers/1510.05245.pdf` - Locally-saved copy of Aaronson & Brod, "BosonSampling with Lost Photons" (Phys. Rev. A 93, 012335 (2016))
- `docs/iqp-baseline.md` - Two new bullets in the Fresh Primary-Source Verification section (Park & Oh Theorem 1; Aaronson-Brod fixed-loss-count Theorem 1), plus a closing sentence explicitly separating the two papers by arXiv ID

## Decisions Made
- **Cited Theorem 1, not Section V, from Park & Oh.** Park & Oh's paper contains two structurally different results under two different noise channels. Theorem 1 (photon transmittance through passive linear optics) is the one that physically matches this project's loss mechanism; Section V ("Noisy IQP Sampling," qubit-level Pauli noise) does not, despite carrying the more tempting "IQP" label. Stated this explicitly in the doc so a future reader (or Plan 18-08/Phase 20) cannot accidentally cite the wrong half of the paper.
- **Stated the fixed-k-vs-fractional-η structural mismatch plainly, using the paper's own words.** Rather than asserting a translation or leaving the mismatch implicit, the doc quotes Aaronson-Brod's own discussion (pp.4, 9) of how their guarantee weakens once k scales with n (`k = εn` gives only `1/n^Θ(εn)` precision, explicitly called insufficient for "any strong complexity claims" by the authors) and becomes trivially simulable for large enough k. Since this project's η is typically held fixed as n grows, this places the project's tested regime in the weak case by the paper's own admission — a fact worth having on record for Plan 18-08's positioning work, not an interpretation Claude introduced.

## Deviations from Plan

None - plan executed exactly as written.

## Issues Encountered

None. `curl -L -o docs/papers/1510.05245.pdf https://arxiv.org/pdf/1510.05245` succeeded on the first attempt (13-page PDF, ~176KB).

**Observation (not a blocker for this plan):** during this session's git history check, two pre-existing commits for Plan 18-04 (`067e695` test, `415dbbb` feat — `hardness/baselines.py`, `tests/test_baselines.py`, `tests/test_loss_model.py`) were found already on `master`, timestamped just before this plan's own commits, with no `18-04-SUMMARY.md` yet on disk. These touch entirely disjoint files from this plan's changes (`hardness/*` vs `docs/papers/*`, `docs/iqp-baseline.md`) — no conflict, no action taken. Flagged here for STATE.md/session continuity so it isn't mistaken for this plan's own work or silently lost.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness
- HARD-03 fully satisfied: both arXiv:2510.24137 (Theorem 1) and arXiv:1510.05245 read in full and cited with extracted formulas, explicitly distinguished from each other and from Park & Oh's own Section V.
- Plan 18-08 (HARD-04 positioning) now has the literature groundwork it needs without having to re-do this reading itself.
- **Blocker/concern for the coordinator:** Plan 18-04's commits already exist on `master` without a corresponding SUMMARY.md — worth confirming with the owner whether that plan was executed by a separate/parallel session and, if so, whether it should be formally closed out (SUMMARY + STATE.md entry) before Phase 18 is considered complete.

---
*Phase: 18-hardness-under-loss-assessment*
*Completed: 2026-08-14*
