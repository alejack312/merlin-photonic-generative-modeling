---
phase: 06-documentation-publication
plan: 02
subsystem: docs
tags: [portfolio, nextjs, tsx, case-study, mmd, photonic, cross-repo]

# Dependency graph
requires:
  - phase: 05-benchmarking
    provides: "results/phase4_summary.md (ring_mass tuning-axis numbers), results/phase5_summary.md (held-out MMD² benchmark numbers)"
  - phase: 06-documentation-publication
    provides: "06-01: README framing and headline numbers reused in the case-study page"
provides:
  - "src/pages/case-studies/merlin-quantum.tsx (alejandro-jackson repo): full interactive case-study page, hero through cross-links, no section skipped"
  - "Two bespoke animated components (RingMassProgressionChart, BenchmarkComparisonChart) following iqp-mmd.tsx's ACGapChart/BandwidthSweepViz pattern"
  - "merlin-quantum registered in shared.tsx's allStudies (blue accent) and index.tsx's caseStudies, discoverable from /case-studies and cross-linked from all other case studies"
  - "Case studies on /case-studies sorted most-recent-first (orchestrator follow-up after checkpoint approval)"
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns: ["ACCENT=blue substituted for CONTEXT.md's violet/emerald suggestions, both already claimed in allStudies — documented in-plan, not silently resolved"]

key-files:
  created: [C:\Users\cuqui\projects\alejandro-jackson\src\pages\case-studies\merlin-quantum.tsx]
  modified: [C:\Users\cuqui\projects\alejandro-jackson\src\components\case-studies\shared.tsx, C:\Users\cuqui\projects\alejandro-jackson\src\pages\case-studies\index.tsx]

key-decisions:
  - "ACCENT=blue, not CONTEXT.md's suggested violet/emerald (both already claimed by dalas/quantum-algorithms in the allStudies group) — locked by the plan itself, not re-litigated during execution."
  - "Hero metrics and the ring_mass tuning-axis chart use Phase 4's original numbers (sigma sweep 0.616, batch sweep 0.609-0.618, natural-order fix 0.691) per the plan's explicit instruction, while the Key Finding narrative cites Phase 5's independently re-measured ring_mass (0.68-0.69) — matching README's own dual-citation approach from 06-01, neither number hidden."
  - "Case studies on /case-studies re-sorted most-recent-first after checkpoint approval, per a user request handled directly by the orchestrator (not this execution) as a quick scoped follow-up."

patterns-established:
  - "Public-facing case-study prose passed through a humanizer self-review pass (em dashes replaced, no rule-of-three/negative-parallelism/inflated-significance constructions) before commit, consistent with 06-01's precedent — code, data arrays, and exact numeric content were left untouched."

# Metrics
duration: ~50min
completed: 2026-07-29
---

# Phase 6 Plan 2: Portfolio Case Study Summary

**New interactive Next.js/TSX case-study page (`/case-studies/merlin-quantum`) in the separate `alejandro-jackson` portfolio repo, with two bespoke animated charts, registered and cross-linked across all case studies, owner-approved live.**

## Performance

- **Duration:** ~50 min (including a resource-contention detour on the build verification step)
- **Tasks:** 2 auto tasks + 1 blocking human-verify checkpoint, all complete
- **Files modified:** 3 in `alejandro-jackson` (1 created, 2 modified), plus a 4th commit by the orchestrator after checkpoint approval

## Accomplishments

- Built `src/pages/case-studies/merlin-quantum.tsx` (497 lines): hero, key metrics, TL;DR, context, 5-step methodology, Key Finding (dark section, states the GEN-07 shortfall plainly: "Good MMD² ≠ Clean Ring Structure"), a BMK-01 benchmarking section, technical depth (6 cards), role/authorship, "what I'd do next" (5 items), source-code link, and `<CrossLinks current="merlin-quantum" />` as the final element — matching `iqp-mmd.tsx`'s full structural depth, no section skipped.
- Two bespoke animated components written locally in the page, following `ACGapChart`/`BandwidthSweepViz`'s `useRef` + `useInView({ once: true, margin: "-40px" })` + staggered `motion.div` width-animation pattern:
  - `RingMassProgressionChart` — ring_mass across three tuning axes (σ sweep 0.616 → batch sweep 0.609–0.618 → natural-order fix 0.691), paired with a `DataTable`.
  - `BenchmarkComparisonChart` — held-out MMD² trained (0.0125) vs. untrained (0.0360) vs. floor (0.0114), paired with a `DataTable`.
- Registered the case study in `shared.tsx`'s `allStudies` array (`slug: "merlin-quantum"`, `accent: "blue"`) so it appears in every other case study's `CrossLinks`, and in `index.tsx`'s `caseStudies` array (card entry with description and 3 condensed metrics). Fixed the hardcoded "Five engineering case studies" header copy to "Six."
- `npm run lint` (exit 0, only pre-existing unrelated warnings) and `npm run build` (exit 0, `Compiled successfully in 53s`, all 42 pages generated including `/case-studies/merlin-quantum` at 6.95 kB / 185 kB First Load JS) both verified clean on an isolated run.
- All prose (hero subtitle, TL;DR, context paragraphs, methodology step bodies, Key Finding narrative, technical-depth card descriptions, role quote, "what I'd do next" items) was drafted and then edited against the humanizer skill's pattern list before commit — em dashes replaced with periods/colons, no rule-of-three padding, no inflated-significance or promotional language, no negative-parallelism ("not just X, it's Y") constructions. Code, data arrays, and cited numbers were left untouched and verbatim from `results/phase4_summary.md` / `results/phase5_summary.md`.
- Owner reviewed the live page and cross-links at the blocking checkpoint and approved.
- **Orchestrator follow-up (after checkpoint approval, not part of this execution's tasks):** owner asked for case studies to display most-recent-first on `/case-studies`. The orchestrator reordered both `index.tsx`'s `caseStudies` array and `shared.tsx`'s `allStudies` array chronologically by original git-history addition date (merlin-quantum → iqp-mmd → quantum-algorithms → quantum-simulator/parallel-programming-mitm/dalas), verified lint/build clean, and committed/pushed directly as `3c51c60` "fix(case-studies): sort case studies most-recent-first."

## Task Commits

Each task was committed atomically, in the `alejandro-jackson` repo (separate git history from `merlin-quantum-case-study`):

1. **Task 1: Build the merlin-quantum case-study TSX page** - `7fea4f1` (feat)
2. **Task 2: Register the case study, verify build, commit and push** - `983f108` (feat)
3. **Checkpoint: human-verify** - approved by owner, no changes requested
4. **Orchestrator follow-up (post-approval, out of this plan's task list): reorder case studies most-recent-first** - `3c51c60` (fix)

All four commits pushed to `alejandro-jackson`'s own `origin/main` (`b08298a..3c51c60`).

## Files Created/Modified

- `C:\Users\cuqui\projects\alejandro-jackson\src\pages\case-studies\merlin-quantum.tsx` - New case-study page (497 lines)
- `C:\Users\cuqui\projects\alejandro-jackson\src\components\case-studies\shared.tsx` - `allStudies` entry added (Task 2), reordered (orchestrator follow-up)
- `C:\Users\cuqui\projects\alejandro-jackson\src\pages\case-studies\index.tsx` - `caseStudies` entry added, header copy "Five"→"Six" (Task 2), reordered (orchestrator follow-up)

## Decisions Made

- `ACCENT = "blue"` used instead of CONTEXT.md's original violet/emerald suggestions, both already claimed by `dalas`/`quantum-algorithms` in the `allStudies` group — this substitution was locked in the plan itself (06-RESEARCH.md's Pitfall 3), not a decision made during execution, but restated here for the record since it's a real deviation from CONTEXT.md's literal wording.
- Hero metrics grid and the ring_mass tuning-axis chart cite Phase 4's original figures (0.616 / 0.609–0.618 / 0.691) since those are the plan-specified per-axis progression numbers; the Key Finding narrative separately cites Phase 5's independent re-measurement (ring_mass ≈ 0.68–0.69) for the "current honest state" framing. Both are real, sourced numbers from different (consistent) measurements of the same checkpoint — matching 06-01's README precedent of citing both rather than picking the more favorable one.
- Case-study reordering (most-recent-first) was a user-directed scope addition surfaced and handled by the orchestrator directly after the checkpoint, not re-delegated back through this plan's task list — noted here for an accurate task/commit trail, not attributed to this execution's own work.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Fixed react/no-unescaped-entities lint warning in the new page**
- **Found during:** Task 2 (`npm run lint` verification step)
- **Issue:** `merlin-quantum.tsx` line 139 used a raw apostrophe (`circuit's`) inside JSX text, triggering `react/no-unescaped-entities`.
- **Fix:** Escaped to `circuit&apos;s`, matching the convention already used everywhere else in the new file.
- **Files modified:** `src/pages/case-studies/merlin-quantum.tsx`
- **Verification:** Re-ran `npm run lint`, warning gone; only pre-existing unrelated warnings in other files remain.
- **Committed in:** `983f108` (Task 2 commit)

**2. [Rule 3 - Blocking] Diagnosed and resolved false-alarm build failures caused by disk-space exhaustion and concurrent-build contention, not code errors**
- **Found during:** Task 2 (`npm run build` verification step)
- **Issue:** Multiple `npm run build` invocations launched in the background (to avoid blocking on a slow build) ended up running concurrently, racing on the shared `.next/` output directory (`ENOENT`/`MODULE_NOT_FOUND` errors reading files another process had just written/removed). Underlying root cause, found by the orchestrator: the C: drive was at 100% capacity (3.5GB free), which made Next.js's build-trace-collection step fail even on unrelated, pre-existing pages — confirming this was never a bug in the new/edited TSX.
- **Fix:** Owner freed disk space (47GB free after). `.next/` was cleared and a single isolated `npm run build` was run with nothing else contending for it.
- **Files modified:** None (no code changes; environment/process issue only).
- **Verification:** Final isolated build: `Compiled successfully in 53s`, all 42 pages generated including `/case-studies/merlin-quantum`, exit 0.
- **Committed in:** N/A (no code change required).

---

**Total deviations:** 2 auto-fixed (1 bug, 1 blocking/environmental)
**Impact on plan:** Both were necessary to get a trustworthy build/lint result before the checkpoint; neither represents scope creep or a code defect in the delivered page.

## Issues Encountered

- Build verification took multiple attempts due to background-process contention and, ultimately, host disk-space exhaustion unrelated to this plan's code changes. Resolved as documented above; the final, isolated build/lint run is the one that counts as the plan's verification evidence.

## User Setup Required

None - no external service configuration required.

## Next Phase Readiness

- DOC-04 (portfolio case study, IQP-MMD case-study format) is satisfied: a full interactive TSX page exists at `/case-studies/merlin-quantum`, is discoverable from the case-studies index, is cross-linked bidirectionally with all other case studies, uses a non-colliding accent color (`blue`), and states the GEN-07 honest result as its "Key Finding" — owner-verified live at the blocking checkpoint.
- Phase 6 (Documentation & Publication) is now complete: both 06-01 (README, LICENSE, docs/ moves, technical note, this-repo packaging) and 06-02 (portfolio case study, cross-repo) are done.
- Source-code link on the new case-study page (`https://github.com/alejack312/merlin-photonic-generative-modeling`) will 404 until the owner flips the `merlin-quantum-case-study` repo's visibility to public — an existing, previously-flagged manual step from 06-01, not new to this plan.
- No blockers identified. This was the last plan in Phase 6 and in the project's roadmap.

---
*Phase: 06-documentation-publication*
*Completed: 2026-07-29*
