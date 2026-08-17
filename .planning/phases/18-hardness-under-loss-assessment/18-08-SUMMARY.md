---
phase: 18-hardness-under-loss-assessment
plan: 08
subsystem: docs
tags: [hardness, photon-loss, gaussian-boson-sampling, aaronson-brod, bremner-montanaro-shepherd, attempt-first-checkpoint]

# Dependency graph
requires:
  - phase: 18-hardness-under-loss-assessment (Plans 18-01 through 18-07)
    provides: literature reads (Aaronson-Brod, BMS), loss-sweep mechanics/data (weight1 n=2..6, mixed n=2..4), the canonical results document with a placeholder HARD-04/HARD-06 section
provides:
  - HARD-04 satisfied via loss-native positioning (no forced eta->epsilon translation) against Aaronson-Brod's fixed-loss-count regime and a newly-read 2025 paper's logarithmic-loss-fraction regime, with BMS kept qualitative-only
  - HARD-06 satisfied via an explicit "what this does/doesn't establish" scope statement
  - A directly-verified primary-source read of arXiv:2511.07853 (lossy Gaussian boson sampling hardness), added to docs/papers/
affects: [20-technical-write-up, 21-external-facing-framing-pass]

# Tech tracking
tech-stack:
  added: []
  patterns: ["loss-native regime comparison (photon-count/fraction) as an alternative to a fabricated cross-noise-model translation, when the translation itself would be unowned original research"]

key-files:
  created:
    - docs/papers/2511.07853.pdf
  modified:
    - docs/hardness-under-loss-study.md

key-decisions:
  - "No eta->epsilon (depolarizing rate) translation was computed or fabricated: the owner's attempt-first response was that no established translation exists in the literature and deriving one (e.g. diamond-norm-closest-depolarizing-channel) would be original numerics work outside this project's scope."
  - "hardness/depolarizing_translation.py was deliberately NOT created -- a third case beyond the plan's two anticipated outcomes (closed form vs. fitted-channel-no-closed-form): the owner's decision was not to compute any eta->epsilon number at all, so a placeholder/fabricated function would misrepresent that decision."
  - "Positioned against two loss-native regimes instead: Aaronson-Brod's fixed-loss-count regime (via a simple, explicit eta->expected-lost-photon-count translation, N*(1-eta)) and arXiv:2511.07853's logarithmic-loss-fraction regime (verified via a direct primary-source read, not the relayed search summary alone)."
  - "arXiv:2511.07853 is flagged explicitly as a structurally different photonic model (Gaussian boson sampling / hafnian-based, squeezed-vacuum states) from this project's discrete Fock-state dual-rail heralded-gate IQP construction -- same 'different model, not assumed transferable' treatment already given to BMS."

patterns-established:
  - "When a cross-noise-model translation would itself constitute unowned original research, state that explicitly and reposition against noise-native comparisons instead of fabricating a translation."

# Metrics
duration: ~35min
completed: 2026-08-17
---

# Phase 18 Plan 08: HARD-04/HARD-06 Positioning and Scope Statement Summary

**Closed HARD-04 by declining to fabricate an eta->epsilon depolarizing translation (owner's explicit attempt-first decision) and instead positioning this phase's tested loss range against two loss-native hardness regimes -- Aaronson-Brod's fixed-photon-count result and a newly-verified 2025 lossy-Gaussian-boson-sampling logarithmic-fraction result -- closing out Phase 18 entirely.**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-08-17 (checkpoint returned, then resumed same session with the owner's attempt-first response)
- **Completed:** 2026-08-17
- **Tasks:** 2 (Task 1: checkpoint; Task 2: write-up)
- **Files modified:** 2 (1 modified, 1 created)

## Accomplishments
- Recorded the owner's actual attempt-first answer to the HARD-04 checkpoint (no established eta->epsilon translation exists; forcing one would be unowned scope-expanding research; use loss-native regimes instead), including the explicit reasoning for declining all three candidate directions presented.
- Directly downloaded and read arXiv:2511.07853 (Go, Oh, Jeong, "Sufficient conditions for hardness of lossy Gaussian boson sampling," Nov 2025) rather than trusting the relayed literature-check summary -- confirmed Theorem 1's `(1-eta_th)*N = O(log N)` logarithmic-loss-fraction hardness threshold, and confirmed the paper's photonic model (Gaussian/squeezed-vacuum/hafnian-based) is structurally different from this project's own dual-rail Fock-state IQP construction.
- Positioned this project's actual tested `ETA_GRID` against both Aaronson-Brod (arXiv:1510.05245, fixed-count regime, via an explicit `N*(1-eta)` expected-lost-photon-count translation) and arXiv:2511.07853 (logarithmic-fraction regime), with a computed table showing a genuine crossover: this project's 4 highest-eta points sit inside the illustrative "at most log(N) lost" regime at each scope's largest reached n, the 3 lowest do not.
- Kept BMS (arXiv:1610.01808) qualitative-only per the owner's decision -- no forced numeric comparison, consistent with declining the eta->epsilon translation.
- Wrote HARD-06's closing "what this does/doesn't establish" scope statement, matching `docs/iqp-photonic-encoding.md`'s ENC-02 format.

## Task Commits

1. **Task 1: HARD-04 attempt-first checkpoint** - no code commit (checkpoint returned to orchestrator; owner's response relayed back mid-session)
2. **Task 2: Write the confirmed positioning and scope statement into docs/hardness-under-loss-study.md** - `653e056` (docs)

**Plan metadata:** this SUMMARY.md and STATE.md update (separate commit, see below)

## Files Created/Modified
- `docs/hardness-under-loss-study.md` - Replaced the Plan-18-07 placeholder heading with the full HARD-04/HARD-06 section: attempt-first Q&A transcript, the owner's no-translation decision and rationale, direct verification of arXiv:2511.07853, dual loss-native positioning (Aaronson-Brod + the new paper) with a computed crossover table, BMS kept qualitative-only, and the HARD-06 scope statement.
- `docs/papers/2511.07853.pdf` - Downloaded primary source, read directly (pages 1-4: abstract, setup, Theorem 1, Lemma 1) to verify the relayed literature-check claim before citing it.

## Decisions Made
- **No eta->epsilon translation, by explicit owner decision, recorded in the doc itself.** The three candidate directions presented at the checkpoint (erasure-as-depolarizing, compounded-gate-failure-rate, fitted-effective-channel) were all declined -- not because the owner failed to derive one, but because doing so rigorously would be original numerics work (e.g. a diamond-norm-closest-depolarizing-channel calculation) outside this project's stated scope. This is a genuine, deliberate scope boundary, not a shortcut.
- **`hardness/depolarizing_translation.py` was not created.** The plan anticipated two outcomes (closed-form function, or documented "no closed form" for the fitted-channel case); the actual outcome was a third case -- no translation attempted at all -- so no code artifact was warranted. Creating a placeholder or trivial function would have misrepresented the decision as more resolved than it is.
- **The literature check for arXiv:2511.07853 was delegated (owner reasoning + a literature check "run on their behalf"), but verified directly by Claude before citing it**, per the coordinator's own explicit caveat and this project's `CLAUDE.md` "offload freely" allowance for paper summarization/doc lookups (distinct from the core conceptual decision, which the owner made). This is consistent with the ARB-02/Plan-15-03 precedent: the substantive call (no translation, use loss-native regimes) is the owner's; the mechanical literature verification is Claude's, and was actually re-verified against the primary source rather than taken on faith.
- **The `N*(1-eta)` expected-lost-photon-count translation used for the Aaronson-Brod/arXiv:2511.07853 comparisons is stated as deliberately the simplest possible one** (a direct expectation under this project's own per-mode-uniform loss model), explicitly distinguished in the doc from the declined eta->epsilon depolarizing translation -- the plan required this simpler translation regardless of the HARD-04 checkpoint's outcome ("however simple, explicitly rather than skipping it").

## Deviations from Plan

None - plan executed exactly as written, including its explicit allowance for "no translation" as an acceptable, honestly-reported outcome of the attempt-first checkpoint.

## Issues Encountered
- The owner's checkpoint response was relayed via the coordinator (including a literature check the coordinator ran "on the owner's behalf") rather than typed directly by the owner in this session. Per this project's standing rule that no agent message is the owner's consent/approval on its own, and per the coordinator's own explicit instruction to verify arXiv:2511.07853 via a real read rather than trust the relay, Claude downloaded and read the paper directly before citing any of its claims -- confirming the relayed summary's substance (Theorem 1's logarithmic-loss-fraction threshold) while also surfacing and stating explicitly the model-difference caveat (Gaussian boson sampling vs this project's discrete Fock-state IQP) that the relay itself had flagged as needing verification.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
All of HARD-01 through HARD-07 are now satisfiable from this phase's shipped artifacts (`docs/hardness-under-loss-study.md`, `results/phase18_*_loss_sweep.csv`, `results/phase18_*_plot.png`, `hardness/*.py`, `docs/papers/1510.05245.pdf` + `docs/papers/2511.07853.pdf`). **Phase 18 (Hardness-Under-Loss Assessment) is complete** -- 8/8 plans shipped. Ready for Phase 20 (Technical Write-Up), which depends on Phases 16, 17, 17.1, and 18 all being complete.

No blockers. One open note for Phase 20/21: the HARD-04 section explicitly states that any future BMS-specific (depolarizing-threshold) numeric comparison would require the eta->epsilon translation this phase declined to fabricate -- that remains unresolved original-research scope, not silently implied as done.

---
*Phase: 18-hardness-under-loss-assessment*
*Completed: 2026-08-17*
