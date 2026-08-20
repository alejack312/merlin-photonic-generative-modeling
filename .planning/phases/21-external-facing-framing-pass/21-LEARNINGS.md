---
phase: 21
phase_name: "External-Facing Framing Pass"
project: "MerLin Photonic Generative Modeling"
generated: "2026-08-20"
counts:
  decisions: 6
  lessons: 4
  patterns: 4
  surprises: 3
missing_artifacts: []
---

# Phase 21 Learnings: External-Facing Framing Pass

## Decisions

### Two artifacts, two repos, no restatement
The case-study page (`alejandro-jackson/src/pages/case-studies/merlin-quantum.tsx`) is the primary deliverable; this repo's `README.md` gets only a short pitch section linking out to both the case-study page and `docs/technical-findings.md`, not a restatement of either.

**Rationale:** README is a "front door" for GitHub visitors; the full story belongs on the portfolio page. Keeping the README short avoids duplicating maintenance burden across three documents (README, case-study page, technical-findings.md).
**Source:** 21-CONTEXT.md ("Deliverable location" section), 21-02-PLAN.md objective.

### Extend the existing page/URL rather than create a second page
v3.0 content was added to the same `merlin-quantum.tsx` page and URL rather than a new standalone page cross-linked via `CrossLinks`.

**Rationale:** the milestone is framed as "one continuous story" spanning v1.0 to v3.0, not two separate narratives.
**Source:** 21-CONTEXT.md ("Deliverable location" section).

### TRAIN + HARD as co-lead findings; ARB-01 + Julia as supporting evidence
Two new `Section` blocks were used (not one, not four): one for trainability + hardness-under-loss as the milestone's two measured research claims, one for gate validation + Julia cross-checks as supporting/infrastructure material.

**Rationale:** avoids a "four repeated TL;DR blocks" anti-pattern flagged in 21-RESEARCH.md, and avoids overloading a single section with two independent stories (gradients-via-parameter-shift and loss-via-explicit-modeling).
**Source:** 21-01-PLAN.md Task 1 decision note, 21-01-SUMMARY.md key-decisions.

### No new chart components — reuse DataTable and the existing callout markup
Rather than building new chart components (e.g. a bandwidth-sensitivity chart, a TVD-vs-eta chart), the plan reused `DataTable` and the page's existing hand-rolled "Key insight" callout markup verbatim.

**Rationale:** this phase is a content/framing pass, not a features pass — new charting code would add maintenance surface without being required by the phase's scope.
**Source:** 21-01-PLAN.md important_notes ("No new chart components"), 21-01-SUMMARY.md.

### Name the concrete AI-disclosure mechanism, not a generic claim
The Role `QuoteBlock` names TRAIN-07 specifically ("a transcript of my own reasoning through a real disagreement in the data, not Claude's summary of it") rather than a generic "I verified my understanding" statement.

**Rationale:** follows the project's established `[[phase6-ai-disclosure-framing]]` mechanism-not-magic convention — concrete evidence is stronger, ownership-forward framing than an abstract assertion, and this project has an unusually citable concrete example available.
**Source:** 21-01-PLAN.md Task 2 decision note, 21-CONTEXT.md ("AI-disclosure framing").

### Accuracy corrections are made and disclosed, not shipped silently
When fact-checking during drafting surfaced findings that contradicted the drafted copy (the dual-rail reimplementation's existence in round 2; the small_angle sigma=0.3 "exp" flip in round 3), the copy was corrected and the correction was documented inline in the SUMMARY rather than shipped as originally drafted or silently fixed without a trace.

**Rationale:** matches this project's CLAUDE.md instruction to "push back... name it explicitly rather than complying quietly," and preserves an audit trail of what was caught and why.
**Source:** 21-01-SUMMARY.md "Checkpoint-Feedback Continuation, Round 2" and "Round 3" sections.

---

## Lessons

### A drafted claim can be wrong even when it "sounds like" the source data
While fact-checking the "Bigger Picture" comparison-table row against `docs/trainability-study.md`'s TRAIN-09 bandwidth-grid raw table, the drafted claim ("small_angle came out inconclusive in every tested scope and every follow-up... never resolved either way") turned out to be false: at sigma=0.3, both `weight1/small_angle` and `mixed/small_angle` flip to a clear "exp" verdict. The error existed because `docs/technical-findings.md`'s canonical synthesis prose never surfaces this bandwidth-grid detail for `small_angle` (it only narrates the `uniform`-cell story), so a claim that sounded consistent with the higher-level summary was inconsistent with the underlying raw table.

**Context:** synthesis documents can omit details that are true in a lower-level source doc; drafting external-facing prose from a synthesis doc alone (without checking the raw table it summarizes) risks reproducing that omission as an inaccurate claim.
**Source:** 21-01-SUMMARY.md "Checkpoint-Feedback Continuation, Round 3" (real accuracy gap found and fixed during fact-checking).

### Reviewing a rendered page surfaces gaps that reviewing drafted text does not
The first checkpoint round found six real content gaps (missing homepage feature, stale hero description, missing tools/badges, stale "What I'd Do Next," no TL;DR, an unexplained R²=0.000 figure) — none of which were caught during plan-writing or execution, only when the owner reviewed the actual rendered page in context with the rest of the site.

**Context:** a plan scoped narrowly to "the new v3.0 sections" can still ship an internally-inconsistent page if sibling surfaces (homepage feature list, hero copy, badges, an existing "next steps" list) aren't updated in the same pass — these inconsistencies are only visible when the whole page/site is reviewed together, not when reviewing the diff in isolation.
**Source:** 21-01-SUMMARY.md "Checkpoint-Feedback Continuation (2026-08-19)" (owner feedback, six items).

### An omission can be a real accuracy gap even when the stated fact is technically true
Round 2's checkpoint flagged that the page's claim ("gradients computed via exact parameter-shift, not MerLin's `QuantumLayer` autograd, which can't accept polarization-annotated states") was true for the primary pipeline but incomplete — it omitted that a supplementary dual-rail reimplementation exists that DOES use `QuantumLayer`'s native autograd, because MerLin's rejection is specifically of polarization annotations, not dual-rail encoding generally.

**Context:** a true-but-incomplete statement can still read as misleading to a careful reader familiar with the underlying mechanism; catching this required domain knowledge the AI-drafted copy didn't have (the reviewer, not the drafting process, caught it).
**Source:** 21-01-SUMMARY.md "Checkpoint-Feedback Continuation, Round 2 (2026-08-19, same day)".

### Pre-existing unrelated working-tree changes must be actively excluded, not just ignored
The target file (`merlin-quantum.tsx`) had a pre-existing, unrelated uncommitted hero-subtitle change already sitting in the working tree before rounds 2 and 3 started, plus an unrelated modified PDF and an untracked image. Blanket `git add` would have swept these into this phase's commits.

**Context:** in a shared/live repo where the owner may have other in-progress edits, staging must be deliberate (`git add -p`, hunk-by-hunk) rather than file-level, even when the whole file is "the" target of the current change.
**Source:** 21-01-SUMMARY.md "Working-tree hygiene note" (Round 2) and "Working-tree hygiene" (Round 3).

---

## Patterns

### Iterative checkpoint rounds for external-facing content
When a checkpoint task gates a content addition to a live, user-facing page, expect multiple review rounds rather than one approve/reject cycle — each round in this phase found either a real content gap, a real accuracy gap, or a new content request, and each was resolved as an append/continuation to the same plan's SUMMARY rather than a new plan.

**When to use:** any phase whose deliverable is externally-visible copy/framing (case-study pages, README pitches, marketing copy) reviewed by the project owner before it can be pushed — budget for iteration, and document each round as a distinct dated section within the same SUMMARY file rather than starting over.
**Source:** 21-01-SUMMARY.md (four "Checkpoint-Feedback Continuation" rounds plus a final "Checkpoint Approved" section).

### Cite every number to a file:line source before drafting
21-RESEARCH.md pre-extracted every quotable number with file:line sourcing before either PLAN.md was written, and both plans instructed the executor to quote from that pre-extracted set rather than re-deriving or paraphrasing numbers from the source docs directly.

**When to use:** any external-facing writing pass built from an existing internal technical write-up — pre-extracting sourced numbers up front makes later fact-checking against the drafted copy fast (spot-check against a known list) rather than requiring a full re-derivation.
**Source:** 21-01-PLAN.md context references ("Ground-truth numbers... pre-extracted with file:line sourcing... do not re-derive, do not paraphrase loosely"), 21-VERIFICATION.md's 11-figure spot-check table.

### Separate candid internal docs from framed external docs, explicitly
This phase exists specifically to produce an external-facing, "mechanism-not-magic, ownership-forward" framing of findings that are stated more bluntly in `docs/technical-findings.md`, while explicitly leaving the internal doc unvarnished — the phase boundary states this as a design goal, not an incidental split.

**When to use:** any project that maintains both an internal technical write-up (candid, exhaustive) and a recruiter/interview-facing artifact (curated, framed) — keep both, and treat the framing pass as translation rather than replacement: the external copy must still surface every negative/inconclusive result the internal doc reports, just in accessible language.
**Source:** 21-CONTEXT.md (Phase Boundary), 21-VERIFICATION.md phase goal statement.

### Correct a drafting error in place and document the correction, not just the fix
When the round-3 fact-check found the drafted small_angle claim was inaccurate, the fix preserved the row's correct aggregate verdict ("never resolved either way") while removing the specific false sub-claim ("inconclusive in every... bandwidth grid") — and the SUMMARY documented both what was wrong and why the correct version is still accurate.

**When to use:** whenever a fact-check catches an error in already-drafted external-facing copy — fix the specific false claim without discarding the surrounding correct framing, and record the before/after and the reasoning in the deliverable's own audit trail (SUMMARY/commit message), not just in chat.
**Source:** 21-01-SUMMARY.md "Checkpoint-Feedback Continuation, Round 3" (real accuracy gap found and fixed).

---

## Surprises

### A synthesis document's silence produced a factual error in downstream copy
The technical-findings.md synthesis doc's decision not to narrate the small_angle bandwidth-grid detail (because it only tracked the uniform-cell story) meant a claim drafted from that synthesis, while consistent with the synthesis's own narrative, was factually wrong against the underlying raw table in trainability-study.md.

**Impact:** this was caught only because round 3 explicitly re-checked the specific row against the raw source table rather than trusting the synthesis doc's framing — a project convention (fact-check against raw data, not just against the nearest write-up) prevented an inaccurate claim from shipping.
**Source:** 21-01-SUMMARY.md "Checkpoint-Feedback Continuation, Round 3".

### An asterisk on a headline metric was judged safe specifically because of where it points
The homepage's featured-card metric `R²=0.999*` was kept (not dropped or reworded) on the judgment that the asterisk is a "legitimate forward-pointer" because the case-study page it links to explains the bandwidth-fragility caveat in its own "Key insight" callout.

**Impact:** this is documented as a deliberate decision in 21-01-SUMMARY.md, but this repo's artifacts contain no record of anyone later verifying that the asterisk actually resolves to a visible footnote/explanation on the card itself, nor any record of a post-approval review flagging it as a dangling reference. (Note: this contradicts a detail supplied in this task's own briefing about a post-approval "dangling reference" finding — that finding is not present in any artifact in this phase directory, so it is not included here as a verified fact.)
**Source:** 21-01-SUMMARY.md line 114 (decision rationale only — no corroborating fix or later-round follow-up found in this phase's artifacts).

### Verification re-checked a correction rather than trusting the SUMMARY's claim
21-VERIFICATION.md independently re-verified the round-3 small_angle bandwidth-grid correction against the source doc rather than accepting the SUMMARY's account of the fix at face value, and explicitly notes this in its gaps summary ("independently re-verified here and found accurate").

**Impact:** demonstrates the verification step in this project's workflow treats even self-reported corrections as claims requiring evidence, not as settled once documented — relevant given this phase's unusually high rate of self-caught drafting errors (two distinct accuracy corrections across four checkpoint rounds).
**Source:** 21-VERIFICATION.md "Gaps Summary" and "Number Spot-Check" table (row: "sigma=0.3 flips both scopes' small_angle to 'exp'").

---
*Phase: 21-external-facing-framing-pass*
*Generated: 2026-08-20*
