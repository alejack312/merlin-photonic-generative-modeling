---
phase: 21-external-facing-framing-pass
plan: 01
subsystem: docs
tags: [portfolio, case-study, react, tsx, external-framing, v3.0]

# Dependency graph
requires:
  - phase: 20-technical-write-up
    provides: "docs/technical-findings.md and its three source docs — the locked numbers this plan quotes from directly, per 21-RESEARCH.md's file:line sourcing"
provides:
  - "Two new v3.0 Section blocks on the live merlin-quantum case-study page (portfolio repo), covering trainability + hardness-under-loss as co-lead findings and gate validation + Julia cross-checks as supporting evidence"
  - "Extended Role QuoteBlock naming the TRAIN-07 transcribed self-explanation mechanism as concrete AI-disclosure evidence for v3.0"
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns: ["Reused DataTable + hand-rolled 'Key insight' callout markup for new content instead of adding new chart components — content/framing pass only, no new charting code"]

key-files:
  created: []
  modified: ["C:\\Users\\cuqui\\projects\\alejandro-jackson\\src\\pages\\case-studies\\merlin-quantum.tsx"]

key-decisions:
  - "Two new Section blocks (not one, not four): one for TRAIN+HARD as co-lead headline findings, one for ARB-01+Julia as supporting/infrastructure evidence — avoids both the 'four repeated TL;DR blocks' anti-pattern and an overly dense single section."
  - "DataTable over MetricsGrid for the TRAIN headline numbers — the source table already has 5 columns (scope, init, n range, model, R²), which reads more naturally as a table than 4 metric cards."
  - "Reused the existing hand-rolled 'Key insight' callout markup verbatim (not a new component) for both new insight boxes, matching the page's established pattern."
  - "Accent stayed blue (no new accent color) and Section dark-alternation continues correctly (Technical Depth[dark] -> new-1[not dark] -> new-2[dark] -> Role[not dark])."
  - "Role QuoteBlock: reordered (not deleted/reworded) the existing v1.0 sentences so the 'credential-building exercise' framing remains the closing line, with the new v3.0 authorship/AI-disclosure sentences inserted before it — matches the plan's explicit 'moved to remain the closing line' allowance."
  - "Named the TRAIN-07 mechanism explicitly and concretely ('a transcript of my own reasoning through a real disagreement in the data, not Claude's summary of it') rather than a generic AI-verification claim, per phase6-ai-disclosure-framing's mechanism-not-magic convention."

patterns-established: []

# Metrics
duration: 35min
completed: 2026-08-19
---

# Phase 21 Plan 01: Portfolio Case-Study Page v3.0 Extension Summary

**Two new Section blocks (v3.0 headline findings; supporting gate-validation/Julia evidence) inserted into the live `merlin-quantum.tsx` portfolio page between Technical Depth and Role, plus an extended Role QuoteBlock naming the TRAIN-07 transcribed-reasoning mechanism — committed locally in a separate repo (`alejandro-jackson`), not pushed.**

## Performance

- **Duration:** ~35 min
- **Started:** 2026-08-19T00:00:00Z (approx.)
- **Completed:** 2026-08-19T00:35:00Z (approx.)
- **Tasks:** 2 (single combined commit per plan override) + 1 checkpoint
- **Files modified:** 1 (`merlin-quantum.tsx`, in the `alejandro-jackson` repo)

## Accomplishments
- `merlin-quantum.tsx` grew from 524 to 728 lines. Two new `Section` blocks landed between the existing "Technical Depth" and "Role" sections:
  - **"v3.0: Trainability & Hardness Under Loss"** (not dark): methodology framing, a `DataTable` of the four TRAIN headline rows (weight1/uniform exp R²=0.999, mixed/uniform exp R²=0.910, both small_angle rows inconclusive), a "Key insight" callout stating the TRAIN-09 sigma-grid non-robustness finding plainly (survives near-original bandwidth, flips to inconclusive at intermediate sigma, non-monotonically re-emerges at high sigma for weight1/uniform only), the TRAIN-10 negative data-dependent-init result, a `DataTable` of HARD's tvd_to_lossless rise (weight1 n=6 and mixed n=4, eta=0.99 vs eta=0.05), a second "Key insight" callout stating the counter-intuitive alpha(eta) DECREASE finding with concrete numbers (16.2048 -> ~4.46e-15) and explicitly correcting the project's earlier internal guess, and a closing honest-scope sentence (HARD-04's deliberate no-translation decision; no complexity-theoretic/asymptotic claim).
  - **"Supporting Evidence: Gate Validation & Independent Verification"** (dark): prose on the tunable weight-2 gate's 16-point alpha-sweep match (~1e-6) and full-pipeline TVD (~1e-16 to 1e-15), prose on the four independently-built Julia cross-checks (not ports), a 6-row `DataTable` summarizing each check and its result, and a closing sentence naming the milestone-level limit that ARB's `CP(alpha)` gate and HARD's `heralded_cz` gate were never cross-tested under loss together.
- The Role `QuoteBlock` now covers v3.0 authorship: two new sentences state the v3.0 work was built and interpreted under the same self-explanation rule as v1.0, and name TRAIN-07 concretely as evidence ("a transcript of my own reasoning through a real disagreement in the data, not Claude's summary of it"). No existing v1.0 sentence was deleted or reworded — the paragraph was reordered so the pre-existing "credential-building exercise" closing sentence remains the paragraph's final line.
- `npm run lint` and `npm run build` both ran clean in `alejandro-jackson` after the edit (build output below) — no regression to the existing v1.0 page or any other page (all 42 static pages, including `/case-studies/merlin-quantum` at 9.91 kB / 187 kB First Load JS, generated successfully).

## Task Commits

Per this plan's explicit override of GSD's default one-commit-per-task convention (`important_notes`: "Single combined commit for Tasks 1 and 2"), Tasks 1 and 2 were held uncommitted and committed together as one commit, in the `alejandro-jackson` repo:

1. **Task 1 (new Section blocks) + Task 2 (Role QuoteBlock extension)** - `efc3bf1` (feat) — `feat(case-studies): add v3.0 IQP circuit study to merlin-quantum page`

**Plan metadata:** this commit (in `merlin-quantum-case-study`, the repo this SUMMARY lives in — the edited file itself is in a separate repo per this plan's cross-repo design).

No commit was made in `merlin-quantum-case-study` for the code change itself, since the edited file (`merlin-quantum.tsx`) lives entirely in `alejandro-jackson`, a separate git repository. `alejandro-jackson`'s `main` branch is now exactly 2 commits ahead of `origin/main`: the pre-existing, unrelated `40889a1` ("docs: add hiring-agent resume evaluation results") plus this plan's own `efc3bf1`. No push was performed in that repo at any point in this plan.

## Files Created/Modified
- `C:\Users\cuqui\projects\alejandro-jackson\src\pages\case-studies\merlin-quantum.tsx` — added 3 new data consts (`trainHeadlineData`, `hardHeadlineData`, `juliaCrossCheckData`), 2 new `Section` blocks (209 insertions total), and extended the Role `QuoteBlock`'s text (5 lines removed/replaced as part of the reordering, 14 lines added). No new imports — `Section`/`DataTable`/`QuoteBlock` were already imported at the top of the file.

## Decisions Made
- **Two new Section blocks, not one and not four** — stated explicitly in the plan's own instructions and followed as specified: TRAIN+HARD as co-lead headline findings in one section, ARB-01+Julia as supporting/infrastructure evidence in a second section.
- **DataTable chosen over MetricsGrid** for the TRAIN headline numbers, since the source data has 5 columns (generator scope, init scheme, n range, winning model, exp R²) that read naturally as a table row per cell, matching the existing "Key Finding" section's own `DataTable` usage pattern.
- **No new chart components** — reused `DataTable` and the existing hand-rolled "Key insight" callout markup (`rounded-lg border border-blue-400/20 bg-blue-400/5 px-4 py-3` wrapping a `<p>` starting with a bold blue "Key insight:" span), copied verbatim from lines 385-397 of the pre-edit file, per the plan's explicit instruction and 21-RESEARCH.md's recommendation to keep this a content/framing pass, not a features pass.
- **Accent color unchanged** — `ACCENT: AccentColor = "blue"` reused for all new content, per the plan's lock that a new accent would visually partition v1.0 from v3.0 content, contradicting the "one continuous story" goal.
- **Section dark-alternation preserved**: Technical Depth (`dark`) -> new Section 1 (not `dark`) -> new Section 2 (`dark`) -> Role (not `dark`, unchanged) — inserting an even number of sections keeps every downstream section's adjacency-to-Role parity intact, exactly as the plan specified.
- **Role QuoteBlock reordering, not deletion**: the plan explicitly allowed either "unchanged in place" or "moved to remain the closing line" for the existing "Built as a credential-building exercise..." sentence. Since that sentence was not already the paragraph's last sentence in the pre-edit file (the IQP-MMD carryover sentence was), it was moved to the end (its exact text unchanged) so the paragraph still closes on that framing after the new v3.0 sentences, per the plan's `<verify>` criteria for Task 2.
- **TRAIN-07 named explicitly, not left generic** — the QuoteBlock addition states "the trainability write-up's literature cross-reference (TRAIN-07) is a transcript of my own reasoning through a real disagreement in the data, not Claude's summary of it," matching [[phase6-ai-disclosure-framing]]'s mechanism-not-magic convention and satisfying this plan's must-have truth that the Role section names the concrete mechanism, not just asserts the rule abstractly.

## Deviations from Plan

None - plan executed exactly as written. All content, numbers, and structural decisions (section count, dark-alternation, accent, no new chart components, single combined commit, no push) followed the plan's `<action>` blocks and `important_notes` precisely.

## Issues Encountered
None. Both `npm run lint` and `npm run build` passed clean on the first run — no debugging pass was needed for JSX syntax, type errors, or unescaped-entity lint violations (the file consistently uses `&apos;`/`&mdash;` HTML entities throughout, and the new content followed that same convention).

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- This closes WRITE-07's case-study-page half. Combined with Plan 21-02 (README v3.0 pitch section, already shipped, commit `76456a8`), both of Phase 21's artifacts are now complete: the README's short pitch section and this plan's full case-study-page treatment.
- **A checkpoint is open, awaiting the owner's review** (see below) — this is not yet a "phase complete" state. The commit is local and unpushed by design; pushing `alejandro-jackson`'s `main` (which will also push the unrelated pre-existing `40889a1` commit) requires the owner's explicit separate go-ahead, out of this plan's scope.
- No blockers. Once the owner approves the rendered page, Phase 21 and the v3.0 milestone (WRITE-07, the project's last v1 requirement) are ready to be declared complete.

---
*Phase: 21-external-facing-framing-pass*
*Completed: 2026-08-19*
