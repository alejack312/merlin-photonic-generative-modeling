---
phase: 6
phase_name: "Documentation & Publication"
project: "MerLin Photonic Generative Modeling"
generated: "2026-08-20"
counts:
  decisions: 6
  lessons: 3
  patterns: 4
  surprises: 3
missing_artifacts:
  - "06-UAT.md"
---

# Phase 6 Learnings: Documentation & Publication

## Decisions

### Cite the more recent independent re-measurement as the headline number, but show both
README's benchmark table uses Phase 5's re-measured ring_mass/gap_mass (0.6833±0.0073 / 0.0514±0.0035) as the headline figures rather than Phase 4's original run (0.691/0.048), because Phase 5 is a more recent, independent re-measurement of the same checkpoint. Both numbers (and the 0.609→0.691 improvement path) are shown in the README so neither reading is hidden.

**Rationale:** Prefer the more recently verified number as "headline," but don't suppress the earlier number — avoids the appearance of cherry-picking a favorable figure.
**Source:** 06-01-SUMMARY.md (Decisions Made section)

---

### Point "How to run" at the actual best-checkpoint entry point, not the library's own example
README's "How to run" section points to `natural_order_train.py` (the GEN-07 checkpoint variant), not `quickstart.py`, which is MerLin's own unrelated classifier example bundled with the dependency.

**Rationale:** Referencing the wrong entry point would make a technical reader run the wrong code and misjudge the project; this was explicitly flagged as Pitfall 1 in 06-RESEARCH.md.
**Source:** 06-01-PLAN.md (Task 2, step 6); 06-01-SUMMARY.md (key-decisions)

---

### Include the real (private) GitHub URL in the technical note rather than a placeholder
The technical note to Vincent Espitalier includes the actual `github.com/alejack312/merlin-photonic-generative-modeling` URL even while the repo is still private, since the URL becomes valid the moment the owner flips visibility.

**Rationale:** Deferring URL-writing to a later manual step would create unnecessary busywork with no benefit — the URL is stable and correct in advance.
**Source:** 06-01-SUMMARY.md (Decisions Made)

---

### Repo stays private; visibility flip is an explicit manual, owner-only step
The plan explicitly forbids running `gh repo edit --visibility public` or any visibility-changing command. All packaging (LICENSE, README, pytest verification, push) is completed with the repo left PRIVATE.

**Rationale:** Publishing/visibility changes are an owner decision, locked in 06-CONTEXT.md as out of scope for automated execution.
**Source:** 06-01-PLAN.md (Task 3, step 6); 06-VERIFICATION.md (Requirements Coverage, DOC-02 row)

---

### Accent color substitution (blue instead of violet/emerald) locked in-plan, not re-litigated at execution
CONTEXT.md originally suggested `"violet"` or `"emerald"` for the new case study's accent, but both were already claimed by `dalas` and `quantum-algorithms` in the `allStudies` group. The plan locked `"blue"` as the substitute before execution began.

**Rationale:** Pre-resolving a known collision in the plan (rather than leaving it for the executor to discover and improvise) avoids inconsistent ad-hoc choices and keeps the decision auditable.
**Source:** 06-02-PLAN.md (Task 1, ACCENT paragraph); 06-02-SUMMARY.md (key-decisions)

---

### Cite Phase 4's per-axis tuning numbers in the chart, Phase 5's re-measurement in the narrative
The case-study page's hero metrics and `RingMassProgressionChart` use Phase 4's original per-axis figures (0.616 / 0.609–0.618 / 0.691), while the "Key Finding" narrative separately cites Phase 5's independent re-measurement (ring_mass ≈ 0.68–0.69).

**Rationale:** Matches 06-01's README precedent of citing both real, sourced (and consistent) measurements rather than picking only the more favorable one.
**Source:** 06-02-SUMMARY.md (Decisions Made)

---

## Lessons

### `git mv` fails on untracked files; fall back to plain `mv` + `git add`
`git mv mmd-loss.md docs/mmd-loss.md` failed because the files were never tracked in the first place (they were root-level scratch files). The plan had already anticipated this and specified a fallback.

**Context:** Encountered during Task 1 of 06-01 (moving deep-dive docs into `docs/`). Not a surprise to the plan itself (documented as an anticipated fallback) but worth remembering as a general git-mv gotcha for future doc-reorganization tasks.
**Source:** 06-01-SUMMARY.md (Deviations from Plan)

---

### Background-launched `npm run build` invocations can race on `.next/`, masking a disk-space root cause as a code bug
Running multiple `npm run build` commands in the background (to avoid blocking on a slow build) caused them to run concurrently and race on the shared `.next/` output directory, producing `ENOENT`/`MODULE_NOT_FOUND` errors that looked like build failures. The actual root cause was the C: drive at 100% capacity (3.5GB free), which broke Next.js's build-trace-collection step even on unrelated, pre-existing pages.

**Context:** Found during 06-02 Task 2's build verification. Resolved by freeing disk space (to 47GB free) and running a single isolated `npm run build` with nothing else contending for `.next/`. No code changes were needed — this was purely an environment/process issue, not a defect in the new page.
**Source:** 06-02-SUMMARY.md (Deviations from Plan, item 2)

---

### Tracking docs (REQUIREMENTS.md, ROADMAP.md) can silently drift out of sync with actual completion state
`.planning/REQUIREMENTS.md` and `.planning/ROADMAP.md` still showed DOC-01 through DOC-04 as unchecked/Pending even though all four were verified SATISFIED against the actual codebase.

**Context:** Flagged by the verifier as a stale tracking-doc sync issue, not a real gap in deliverables — but worth a checkbox update to avoid confusing future readers of those docs.
**Source:** 06-VERIFICATION.md (Requirements Coverage, closing note)

---

## Patterns

### Ownership-forward AI-disclosure framing for public deliverables
Public-facing documents (README, technical note) state that Claude Code assisted with implementation/verification under a self-imposed discipline, phrased as "I verify every AI-assisted component against my own unaided explanation before it ships" rather than "the AI caught my mistake" or "the AI checked whether I understood the code." Internal artifacts (DESIGN_DECISIONS.md, SUMMARY.md files, git history) stay candid/technical as-is and are referenced as the evidence trail, not scrubbed.

**When to use:** Any externally-visible document (README, portfolio page, note to a technical contact) that discloses AI assistance on a credential-building project. Internal planning/analysis docs are exempt from this framing.
**Source:** 06-01-PLAN.md (Task 2, step 8); 06-01-SUMMARY.md (Accomplishments, tech-stack patterns)

---

### Humanizer self-review pass before committing public-facing prose
Both README prose and the technical note (in 06-01), and all case-study page prose (in 06-02), were run through a humanizer-style self-review before commit: removing em dashes, rule-of-three padding, inflated-significance language, negative-parallelism constructions ("not just X, it's Y"), and other AI-writing tells. Numeric tables, code blocks, and data arrays were left untouched/verbatim from source data.

**When to use:** Any public-facing prose deliverable drafted as part of a credential-building or portfolio project, where AI-writing tells would undercut the "genuine understanding" credibility goal. Not applied to internal candid docs.
**Source:** 06-01-SUMMARY.md (Accomplishments; patterns-established); 06-02-SUMMARY.md (Accomplishments; patterns-established)

---

### Cross-repo case-study registration checklist: page + allStudies + caseStudies + cross-link verification
Adding a new portfolio case study requires touching three coordinated locations in a separate repo: the standalone TSX page, `shared.tsx`'s `allStudies` array (drives cross-links on every other page), and `index.tsx`'s `caseStudies` array (drives the index card). A slug mismatch between the page's `CrossLinks current="..."` prop and the `allStudies`/`caseStudies` slug breaks discoverability silently (TypeScript won't catch a string mismatch across independent literals).

**When to use:** Whenever adding a new portfolio case study to the `alejandro-jackson` repo's case-studies system — verify slug consistency across all three locations before considering the task done.
**Source:** 06-02-PLAN.md (must_haves.key_links; Task 1 and Task 2 actions); 06-VERIFICATION.md (Key Link Verification table)

---

### Verify runnable-code claims by actually running the test suite, not by inspection
Before claiming DOC-02's "working, runnable code," the plan required actually running `python -m pytest -q` and reading the pass count from output, not inferring it from code inspection or prior test runs.

**When to use:** Any documentation/publication task that asserts code "works" or is "runnable" — run the actual verification command and cite the live result (e.g., "48 passed in 159.41s") rather than asserting from memory.
**Source:** 06-01-PLAN.md (Task 1, step 5 and verify clause); 06-01-SUMMARY.md (Issues Encountered)

---

## Surprises

### pytest suite runtime exceeded the tool's default foreground timeout
`python -m pytest -q` ran longer than the default 3-minute foreground timeout and was automatically moved to background by the tool; it completed cleanly at 48 passed in 159.41s, and the commit proceeded once confirmed.

**Impact:** No functional impact (the run completed successfully), but it's a reusable fact for time-budgeting future full-suite runs in this repo — don't assume the suite finishes within a short synchronous window.
**Source:** 06-01-SUMMARY.md (Issues Encountered)

---

### A disk-space issue masqueraded as a build/code failure across unrelated pages
Multiple concurrent `npm run build` attempts produced `ENOENT`/`MODULE_NOT_FOUND` errors that looked like bugs in the newly added page, but the actual cause was the host's C: drive being nearly full (3.5GB free), breaking Next.js's build-trace step even on pre-existing, unrelated pages.

**Impact:** Cost significant debugging time during 06-02's build verification step before the true root cause (disk space, not code) was identified. Worth checking disk space early when a Next.js build fails in a way that touches unrelated files.
**Source:** 06-02-SUMMARY.md (Deviations from Plan, item 2)

---

### Case-study reordering request arrived after the checkpoint and was handled outside the plan's task list
After the owner approved the checkpoint, they asked for case studies to display most-recent-first on `/case-studies`. This was handled directly by the orchestrator (not re-delegated through the plan) as a scoped follow-up, requiring reordering both `allStudies` and `caseStudies` arrays and a separate commit (`3c51c60`).

**Impact:** Shows that owner feedback surfacing right after a checkpoint approval can still be folded in cleanly as a small scoped addition without reopening the full plan — a low-risk way to handle late-arriving small requests.
**Source:** 06-02-SUMMARY.md (Accomplishments, "Orchestrator follow-up"; Decisions Made)
