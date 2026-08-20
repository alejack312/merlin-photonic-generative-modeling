---
phase: 20
phase_name: "Technical Write-Up"
project: "MerLin Photonic Generative Modeling"
generated: "2026-08-20"
counts:
  decisions: 6
  lessons: 3
  patterns: 4
  surprises: 2
missing_artifacts: []
---

# Phase 20 Learnings: Technical Write-Up

## Decisions

### TRAIN-07's interpretation is owner-authored, not Claude-authored
The `> Owner interpretation: [pending]` placeholder at `docs/trainability-study.md:174` was closed via a mandatory blocking human-action checkpoint (Task 1 of Plan 20-01) rather than Claude writing the interpretation itself. The owner's full multi-step reasoning trajectory — including a ruled-out first hypothesis (`complete_graph_like`) and a revised, initially-overreaching framing — was transcribed verbatim.

**Rationale:** Per this project's CLAUDE.md self-explanation-checkpoint convention and `20-CONTEXT.md`'s explicit lock, TRAIN-07 was a genuinely open interpretive gap, not a formality.
**Source:** .planning/phases/20-technical-write-up/20-01-PLAN.md (Task 1), 20-01-SUMMARY.md

### McClean et al. citation confirmed live but flagged at a lower confidence tier
Rather than trusting prior WebSearch-sourced summaries in `.planning/research/`, the McClean et al. citation was confirmed via a direct arXiv API query (arXiv:1803.11173, Nature Communications 9, 4812 (2018)) during plan execution.

**Rationale:** This is an abstract/metadata-level confirmation, not a full-PDF read like the other 10 baselines (all of which have a downloaded PDF in `docs/papers/`) — the plan explicitly required this distinction be stated honestly rather than silently upgraded to full confidence.
**Source:** .planning/phases/20-technical-write-up/20-01-PLAN.md, 20-01-SUMMARY.md

### Literature comparison tables are filtered per-section, not forced to 11 uniform rows everywhere
Each of the three source docs' WRITE-02 tables assigns baselines by actual relevance to that section's subject: TRAIN got 6 substantive + 5 silent rows, HARD got 5 substantive + 6 silent rows, ARB got 1 substantive row (arXiv:2405.01395) plus a single prose paragraph explicitly naming the other 10 as not applicable (never silently omitted).

**Rationale:** Per `20-CONTEXT.md`'s locked decision, each table should list only baselines genuinely relevant to that section to avoid padding with undifferentiated "silent" rows, while still requiring every baseline be explicitly addressed somewhere.
**Source:** .planning/phases/20-technical-write-up/20-01-PLAN.md, 20-02-PLAN.md, 20-03-PLAN.md

### TRAIN's RNG seed is described via its actual mechanism, not a fabricated literal number
TRAIN uses a deterministic, reorder-safe hashed-seed scheme (`trainability/rng.py::derive_seed`, hashing each cell's `(n, generator_scope, init_scheme, draw_index)` coordinate), architecturally different from HARD's single literal `seed_base=180814`. The synthesis doc states this mechanism honestly rather than inventing a single seed number to force stylistic parity with HARD.

**Rationale:** Doing so would misrepresent TRAIN's actual (and more robust) per-coordinate-hashed design as a single-seed design it isn't; WRITE-06's "fixed seed" requirement is satisfied via an accurate mechanism citation instead.
**Source:** .planning/phases/20-technical-write-up/20-04-PLAN.md (Task 2, Part C), 20-04-SUMMARY.md

### No Herbst et al. cross-thread note added to iqp-photonic-encoding.md
Per `20-CONTEXT.md`'s explicit lock, the Herbst et al. anticoncentration-tradeoff prediction is a trainability/hardness claim, not a gate-mechanics claim, so it was deliberately excluded from the ARB-01/ARB-02 document even though TRAIN and HARD both got one.

**Rationale:** Keeps each cross-reference scoped to documents that actually measure a relevant quantity; avoids forcing an irrelevant cross-thread into a document about gate construction validation.
**Source:** .planning/phases/20-technical-write-up/20-03-PLAN.md, 20-03-SUMMARY.md

### docs/iqp-baseline.md's earlier speculative anticoncentration-direction guess was corrected, not smoothed over
HARD's real measured `alpha(eta)` decreases as `eta` decreases (loss increases anticoncentration). `docs/iqp-baseline.md`'s earlier 2026-08-12 speculative note had guessed the opposite direction (loss erodes anticoncentration, improving trainability at higher loss). Plan 20-02 explicitly stated the real measured direction is the reverse of that speculation and corrected the record.

**Rationale:** Matches this project's established pattern of catching and correcting its own earlier speculative statements once real data exists, rather than letting a since-falsified guess stand uncorrected.
**Source:** .planning/phases/20-technical-write-up/20-02-PLAN.md (Task 2, Part A), 20-02-SUMMARY.md

> **Forward note (2026-08-20, added after this phase closed):** the measured direction recorded above was itself later found to be an artifact and is **no longer the project's position**. `alpha` had been computed on the raw, un-renormalized lossy distribution, so it decayed as exactly `eta^(2n)` — the square of the surviving mass — with no residual signal; 33 of 56 shipped rows reported `alpha < 1.0`, below BMS's hard theoretical floor of 1.0. Conditioned on detection, anticoncentration is **exactly invariant** under photon loss. Consequently the Herbst et al. verdict moved from "inconsistent" to "silent" (the sweep does not vary the quantity that prediction is keyed on), and the 2026-08-19 correction note in `docs/iqp-baseline.md` was itself withdrawn. See `docs/hardness-under-loss-study.md`'s HARD-05 section and `hardness/baselines.py::anticoncentration_alpha`.
>
> This entry is left as written, not rewritten: it accurately records what Phase 20's artifacts established at the time it closed. The correction is appended rather than substituted, per the same additive-correction convention used in `docs/iqp-baseline.md` and `docs/trainability-study.md`.

---

## Lessons

### Concurrent-session commit-attribution mixing recurs when plans run in the same wave with no dependency
Plans 20-01/20-02/20-03 all ran in wave 1 with no cross-dependency, working in the same shared git working directory concurrently. Plan 20-02's Task 2 commit (`610230d`) swept in files (`.planning/ROADMAP.md`, `.planning/STATE.md`, `20-03-SUMMARY.md`) that a concurrent session executing Plan 20-03 had already staged, even though each plan staged files explicitly (never `git add -A`/`git add .`).

**Context:** This is the same pattern already documented for Phase 18's concurrent plan execution. The content was verified intact and correctly attributed to its actual authoring plan (via `git show HEAD -- <file>`) before proceeding; no history was rewritten to fix attribution.
**Source:** .planning/phases/20-technical-write-up/20-02-SUMMARY.md ("Issues Encountered"), 20-03-SUMMARY.md ("Issues Encountered")

### A malformed two-line markdown heading breaks its expected GitHub anchor slug
`docs/hardness-under-loss-study.md`'s "Owner's attempt-first response" text was written as a two-line heading split across two `###` lines, which does not slugify into a single clean anchor the way a normal one-line heading does.

**Context:** Discovered during Plan 20-04's Task 2 traceability/link-verification pass. Rather than fixing the malformed heading itself, the synthesis doc's link was pointed at the nearest clean, single-line parent heading instead, with prose noting the owner's response is its first subsection.
**Source:** .planning/phases/20-technical-write-up/20-04-SUMMARY.md ("Decisions Made")

### A section-scoped "what this does/doesn't establish" subsection was a structural gap unique to one of three sibling documents
`docs/iqp-photonic-encoding.md`'s ARB-01/ARB-02 section had no section-scoped scope statement of its own — only a document-wide `## Conclusion and Open Questions` — unlike `docs/trainability-study.md` and `docs/hardness-under-loss-study.md`, which each already had per-section scope subsections.

**Context:** Identified during Phase 20's research pass (`20-RESEARCH.md`) as the one real structural inconsistency across the three source docs, and closed by Plan 20-03 rather than left as an accepted asymmetry.
**Source:** .planning/phases/20-technical-write-up/20-03-PLAN.md (objective)

---

## Patterns

### Section-scoped "what this does/doesn't establish" subsection
A per-section scope statement (not a whole-document Conclusion) that restates — never re-derives — the document-level Conclusion's relevant bullets, narrowed to the specific section, citing existing subsections by name.

**When to use:** Any technical document with multiple distinct claims/sections (methodology, results, etc.) where each section's actual epistemic scope needs to be stated explicitly and separately, rather than folded into one document-wide caveat list.
**Source:** .planning/phases/20-technical-write-up/20-03-PLAN.md, 20-03-SUMMARY.md ("patterns-established")

### Literature comparison table: citation-precision prose over terse table-only format
Follow `docs/iqp-baseline.md`'s "Fresh Primary-Source Verification" style: cite theorem/section/page inline, then state relevance and a consistent/inconsistent/silent verdict, rather than a bare table with one-word verdicts.

**When to use:** Any cross-referencing of project results against a fixed list of literature baselines, especially when multiple sibling documents need the same list addressed with different relevance per document.
**Source:** .planning/phases/20-technical-write-up/20-01-PLAN.md, 20-02-PLAN.md, 20-03-PLAN.md (all cite this same style requirement)

### Synthesis document mirrors, never re-derives
`docs/technical-findings.md` mirrors each source doc's literature table verbatim (or lightly reformatted) with a one-line pointer back to the canonical version, and links to (rather than restates) each source doc's own scope/cross-reference sections.

**When to use:** Any project-level synthesis document sitting above multiple detailed source documents — keeps a single source of truth per claim and prevents verdict drift between the synthesis doc and its sources.
**Source:** .planning/phases/20-technical-write-up/20-04-PLAN.md (objective, Task 2 Part A), 20-04-SUMMARY.md ("patterns-established")

### Cross-reference notes point at the sibling document, never restate its findings
`docs/trainability-study.md`'s and `docs/hardness-under-loss-study.md`'s Herbst et al. cross-reference notes each state their own document's measured facts and hedges, then point at the other document's equivalent note for the other half — neither restates the other's numbers.

**When to use:** Any interpretive connection spanning two independently-measured datasets from different phases/documents where a single combined verdict is not directly testable from either dataset alone.
**Source:** .planning/phases/20-technical-write-up/20-02-SUMMARY.md ("patterns-established")

---

## Surprises

### The literal placeholder `[pending]` had survived from Phase 17 into Phase 20 untouched
`docs/trainability-study.md:174` still contained the literal string `> Owner interpretation: [pending]` at the start of Phase 20, confirming TRAIN-07 was a genuinely open, not merely formal, gap that prior phases had explicitly deferred rather than quietly resolved or dropped.

**Impact:** Validated the phase's mandatory blocking-checkpoint design — the plan treated this as a real gate rather than a rubber-stamp step, and the resulting transcript captured genuine reasoning (including a ruled-out hypothesis) rather than a token acknowledgment.
**Source:** .planning/phases/20-technical-write-up/20-01-PLAN.md (must_haves.truths, line 13)

### HARD's measured anticoncentration direction was the opposite of the project's own earlier speculative guess
`docs/iqp-baseline.md`'s 2026-08-12 speculative note had guessed photon loss would erode anticoncentration and thereby improve trainability at higher loss. The real measured data (HARD's `alpha(eta)`) showed the reverse: loss increases anticoncentration, which under Herbst et al.'s framework would predict trainability getting worse, not better, at higher loss.

**Impact:** Phase 20 treated this as a correction to be stated explicitly (marking Herbst as "inconsistent" with the project's own earlier guess in HARD's literature table) rather than quietly dropping or softening the earlier note.
**Source:** .planning/phases/20-technical-write-up/20-02-PLAN.md (Task 2, Part A), 20-02-SUMMARY.md ("Decisions Made")

> **Forward note (2026-08-20):** superseded — the measured direction above was an artifact of computing `alpha` on un-renormalized distributions. Anticoncentration is exactly invariant under loss, and the Herbst verdict is now "silent," not "inconsistent." Full detail in this file's Decisions section ("docs/iqp-baseline.md's earlier speculative anticoncentration-direction guess was corrected, not smoothed over") and in `docs/hardness-under-loss-study.md`'s HARD-05 section. Left as written, per the additive-correction convention.
