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

## Checkpoint-Feedback Continuation (2026-08-19)

The original checkpoint review above was not an approval — the owner reviewed the rendered page and identified six real content gaps, not tone/accuracy nits. This section documents the continuation that closed them. This is an append to the existing SUMMARY above, not a new plan or a rewrite of it; the original Tasks 1+2 content (the two v3.0 Section blocks, the extended Role QuoteBlock) is untouched except for the one Fact-set-E sentence noted below.

**Owner feedback (verbatim, 6 items):**
1. The merlin case study is not featured on the home page.
2. The hero description wasn't updated for v2.0/2.1/3.0.
3. The tools/badges list didn't include Julia, Forge, etc.
4. "What I'd Do Next" didn't include anything about v2.0/2.1/3.0.
5. No TL;DR for v2.0/2.1/3.0.
6. Why is exp R²=0.000 for mixed/small_angle? (answered directly in chat, required no code change — but the existing "Key insight" callout was extended with one clarifying sentence so the page itself doesn't leave the number unexplained.)

**Fixes applied, in `alejandro-jackson` (two files):**

- **`src/pages/index.tsx`:** Added a `blue` entry to `accentClasses` (matching `merlin-quantum.tsx`'s own `AccentColor = "blue"`) and a new first entry in `featuredCaseStudies` for MerLin Photonic Generative Modeling — title, 3 keywords (MerLin, Perceval, Julia), one-sentence outcome naming both the v1.0 generator and the v3.0 "construction that didn't exist in the literature before" claim, link, `accent: "blue"`, and 3 metrics (`ring_mass=0.691`, `Trainability=R²=0.999*`, `Julia checks=4/4 GO`). Placed first in the array as the most recent/significant project. Kept the `R²=0.999*` asterisk (rather than dropping it) since the case-study page itself explains the bandwidth-fragility caveat in its own "Key insight" callout — the asterisk is a legitimate forward-pointer, not an unexplained hedge at card scale. Also fixed a now-stale line ("Five engineering projects...") to "Six engineering projects..." since the section subtitle would otherwise contradict the 6 cards now rendered (Rule 1 — bug, not in original scope but directly caused by this change).
- **`src/pages/case-studies/merlin-quantum.tsx` hero (Fact sets B/C):** Extended the `CaseStudyHero` `subtitle` to keep the existing v1.0 MMD²/no-discriminator sentence and add a second sentence naming the v3.0 trainability + hardness-under-loss study and its "didn't exist in the literature before" claim. Added `"Julia"` and `"Forge"` to the `badges` array (8 badges total now), grouped near their thematically closest existing badges (Julia next to Perceval; Forge at the end).
- **Two new `Section` blocks (Fact set D)**, inserted between the existing "Technical Depth" section and the (already-shipped) "v3.0: Trainability & Hardness Under Loss" section — preserving `dark` alternation exactly as specified (Technical Depth `dark` → new TL;DR *not* `dark` → new bridge `dark` → existing TRAIN/HARD *not* `dark`, unchanged → existing Supporting Evidence `dark`, unchanged → Role, unchanged):
  - **"TL;DR: v2.0 → v3.0"** — a single `CalloutBox`, matching the existing v1.0 TL;DR section's exact pattern, framing v2.0 (IQP→photonic mapping), v2.1 (weight-2 gate), and v3.0 (trainability + hardness questions) as one continuous story, and stating the literature-search finding that this discrete Fock-space IQP construction did not previously exist (the one existing "IQP + photonics" paper builds hardness in a different, continuous-quadrature formalism).
  - **"v2.0-2.1: IQP → Photonic Encoding & Weight-2 Gate"** — prose covering what IQP circuits are, the v2.0 encoding (TVD ~1e-16 vs. exact reference), the v2.1 weight-2 heralded-CZ gate (2/27 herald rate, TVD=2.6e-15, 118/118 tests green), and the "genuinely new, not previously published" claim — plus a new 3-row `DataTable` (`v2BridgeData` const) summarizing the milestone/what-it-built/result table specified in Fact set D. Confirmed the later Supporting Evidence section's "extending the fixed-angle heralded-CZ gate already used elsewhere on this page" sentence now correctly resolves to this new section (that sentence was left unedited, per instructions).
- **"Key insight" callout extension (Fact set E):** added one sentence after the existing TRAIN-09 sigma-grid text, explaining that the mixed/small_angle R²≈0.000 cell isn't a data error — with only 4 points and a near-zero-magnitude init, the exponential fit explained essentially none of the variance, which is itself the evidence behind that cell's "inconclusive" label. No other part of that callout, or the section around it, was touched.
- **"What I'd Do Next" (Fact set F):** restructured the single flat bulleted list into two labeled groups ("v1.0 Follow-Ups" / "v3.0 Follow-Ups", styled with the same font-mono uppercase-tracking label pattern used elsewhere on the page) since the list was growing to 12 items and a flat list would have buried the new v3.0-relevant items among unrelated v1.0 ones. The original 7 v1.0 items are unchanged, unreordered, and un-reworded. Appended the 5 specified v3.0 items verbatim (trainability sweep past n=6/7; cross-testing the tunable gate under loss; pushing the mixed-generator sweep past n=4; distinguishability/g² noise as a second axis; the deliberately-not-attempted eta-to-depolarizing-rate translation).

**Verification:**
- `npm run lint` in `alejandro-jackson`: clean — zero warnings or errors in either modified file (`merlin-quantum.tsx`, `index.tsx`); the only warnings reported repo-wide are pre-existing, in unrelated files (`InfiniteCarousel.tsx`, `about.tsx`, `iqp-mmd.tsx`, `contact.tsx`), untouched by this change.
- `npm run build` in `alejandro-jackson`: clean — `next build` exited 0, "Compiled successfully in 34.1s," all 42/42 static pages generated with zero build-time errors. `/case-studies/merlin-quantum` grew from 9.91 kB/187 kB First Load JS (original checkpoint) to 11.5 kB/189 kB; the home page `/` (now rendering 6 featured cards instead of 5) is 5.97 kB/196 kB. No regression to any other route.

**Commit:** one combined commit for all of the above (home page + case-study page), continuing this plan's original override of GSD's default one-commit-per-task convention — both files are one continuous "close the checkpoint feedback gaps" content addition. `alejandro-jackson`'s `main` is now 3 commits ahead of `origin/main`: pre-existing `40889a1`, this plan's original `efc3bf1`, plus this continuation's new commit. Still not pushed — push remains a separate, explicit owner action outside this plan's scope.

**Status:** returning to checkpoint again for final owner approval. Not yet marked "approved" — this continuation addresses the identified gaps but has not itself been re-reviewed by the owner.

---

## Checkpoint-Feedback Continuation, Round 2 (2026-08-19, same day)

The second checkpoint review was also not an approval — the owner flagged one real accuracy gap in the v3.0 TRAIN/HARD section: the page stated gradients are computed by exact parameter-shift because MerLin's `QuantumLayer` autograd can't accept this project's polarization-annotated states, which is true for the primary pipeline but incomplete. A supplementary, polarization-free dual-rail reimplementation of the same abstract weight-1/weight-2 IQP circuit family was also built (after the trainability and hardness-under-loss studies had already shipped) specifically because MerLin's `QuantumLayer` rejection is of polarization annotations, not dual-rail encoding — so it runs natively through `QuantumLayer`'s own autograd and was used to independently rerun both sweeps end to end. The page omitted this entirely; this round adds it.

**Facts sourced directly from `docs/trainability-study.md`'s "Independent cross-check: dual-rail encoding + MerLin native autograd" section and `docs/hardness-under-loss-study.md`'s "MerLin dual-rail parallel" section, not re-derived.**

**Fixes applied, in `alejandro-jackson`, one file (`src/pages/case-studies/merlin-quantum.tsx`):**

- **v3.0 TRAIN/HARD section intro paragraph:** extended the existing "not MerLin's `QuantumLayer` autograd, which can't accept this project's polarization-annotated states" sentence with a clause naming the supplementary dual-rail reimplementation and pointing to Supporting Evidence for the full comparison — kept to one sentence since the full story lives in the new subsection below.
- **New subsection inside the existing "Supporting Evidence: Gate Validation & Independent Verification" section**, inserted between the existing Julia cross-check `DataTable` and the section's existing closing paragraph (that paragraph, and everything above the insertion point, is unmodified): an intro paragraph naming what the dual-rail reimplementation is, what it covers (weight-1, weight-2, ARB-01's tunable gate), that it is supplementary/non-phase-tracked work built after the trainability and hardness-under-loss studies had already shipped, and that its trainability rerun reached n=8 (weight1) and n=7 (mixed) — two sizes past the original studies' own compute ceiling; a new 2-row `DataTable` (`dualRailCrossCheckData` const, headers `["Comparison", "What agrees", "What doesn't"]`) with one row for TRAIN and one for HARD, using the exact numbers below; a closing sentence stating this doesn't change either study's own shipped verdicts — additional evidence, with one open question of its own.
- **TRAIN row (exact numbers from `docs/trainability-study.md` lines ~450-541):** weight1/uniform and mixed/small_angle verdicts replicate (exp R²=0.983 vs 0.999; inconclusive vs inconclusive) under "What agrees," alongside the n=8/n=7 reach. Under "What doesn't": the mixed/uniform cell genuinely disagrees (CORE exp R²=0.910 vs dual-rail inconclusive R²=0.840), stated as genuinely unresolved — three candidate explanations (no real effect, a real weak effect, an under-specified comparison across different n ranges/methods/precision), none asserted as the answer, matching the source doc's own explicit "further experimentation is required... None of the three is asserted" framing. This disagreement was deliberately NOT softened or resolved in the copy.
- **HARD row (exact numbers from `docs/hardness-under-loss-study.md` lines ~306-370):** loss-driven quantities agree tightly across the full 7-point eta grid, 56 matched cells (max TVD-to-lossless diff 3.84e-6, max herald-failure/success diff 6.17e-7) under "What agrees." Under "What doesn't": absolute output-shape metrics don't agree pointwise (max mean diffs: TVD-to-uniform 0.1434, TVD-to-product-marginals 0.05382, anticoncentration alpha 5.7774), stated exactly as the source doc frames it — "a different physical encoding, not a bug," not a discrepancy to be alarmed about.
- **Framing constraints honored:** the new content never implies this work is part of the formally-verified TRAIN-01..10/HARD-01..07 requirement set (it's explicitly called "supplementary, non-phase-tracked work" in the copy itself), and is not given the same finality as the Julia cross-checks in the same section (those are stated as closed GO verdicts; this one closes with "one open question of its own").

**Working-tree hygiene note:** the target file had a pre-existing, unrelated uncommitted one-line change already sitting in the working tree before this round started (a softened hero-subtitle wording, `"v3.0 study"` / `"didn't exist in the literature before"` → `"broader study"` / `"is not widely explored in the literature"`), plus an unrelated modified `public/resume/quantum.pdf` and an untracked `image.png` at the repo root. None of these are part of this plan's scope. All three were left exactly as found — not committed, not discarded, not touched — using `git add -p` to stage only this round's four new hunks (the new `dualRailCrossCheckData` const, the intro-sentence extension, the new subsection, and confirming the pre-existing subtitle hunk was excluded) rather than a blanket `git add`.

**Verification:**
- `npm run lint` in `alejandro-jackson`: clean — zero warnings in `merlin-quantum.tsx`; the only warnings reported repo-wide are the same pre-existing ones in unrelated files already documented in the prior round (`InfiniteCarousel.tsx`, `about.tsx`, `iqp-mmd.tsx`, `contact.tsx`, `index.tsx`).
- `npm run build` in `alejandro-jackson`: clean — `next build` exited 0, "Compiled successfully in 39.6s," all 42/42 static pages generated with zero build-time errors. `/case-studies/merlin-quantum` grew from 11.5 kB/189 kB First Load JS (prior round) to 12.3 kB/190 kB. No regression to any other route.

**Commit:** one combined commit, continuing this plan's original override of GSD's default one-commit-per-task convention — `feat(case-studies): add MerLin dual-rail cross-check evidence` (`2f5ec70` in `alejandro-jackson`). `alejandro-jackson`'s `main` is now 4 commits ahead of `origin/main`: pre-existing `40889a1`, this plan's original `efc3bf1`, round-1-feedback `971c0f0`, plus this round's `2f5ec70`. Still not pushed — push remains a separate, explicit owner action outside this plan's scope.

**Status:** returning to checkpoint again for final owner approval. Not yet marked "approved."

---

## Checkpoint-Feedback Continuation, Round 3 (2026-08-19, same day)

This round was not triggered by a rejected checkpoint review — it's a new content request layered onto the still-open checkpoint: add a "Bigger Picture" section comparing this project's v3.0 findings against the sibling `iqp-mmd-barren-plateau` project's own findings, closing with the owner's own transcribed verdict on whether the approach is worth pursuing further.

**Fix applied, in `alejandro-jackson`, one file (`src/pages/case-studies/merlin-quantum.tsx`):**

- **New `Section` block** (`accent={ACCENT}`, `label="Synthesis"`, `title="Bigger Picture"`, `dark`), inserted between the existing "Supporting Evidence: Gate Validation & Independent Verification" section's closing `</Section>` and the "Role" section marker — preserving the established dark→no-dark transition into Role unchanged (two `dark` sections in a row is already precedented elsewhere on the page, e.g. Methodology→Key Finding).
- **Content, in order:** (1) one intro paragraph framing the section as a comparison against IQP-MMD, the qubit-side gate-model project already named in the page's own Context section, and naming that this project's MMD² methodology and literature baseline (the fitted empirical plateau rule the trainability findings cross-reference) both descend from it; (2) a new `DataTable` (`bigPictureData` const, headers `["Finding", "Sibling project (qubit, gate-model)", "This project (photonic, Fock-space)"]`) with 4 rows — shape-vs-loss-metric (anti-concentration insufficiency parallel), small-angle init, the uniform-init n≥6 plateau threshold, and photon loss as a qubit-side-inapplicable axis; (3) a closing `QuoteBlock` transcribing the owner's own verdict verbatim in substance ("Not promising, on my own read of it...") — trainability transfers only partially and the exponential-decay signature is bandwidth-fragile (survives at only two of six tested bandwidths), photon loss is a new complication with no qubit-side analog, the working hypothesis that photonic IQP circuits get harder to run as they scale (loss compounding with heralding failure, no established eta-to-depolarizing-rate translation per HARD-04), but still judged worth exploring further since the scaling hypothesis itself is unverified and photonic hardware may have benefits not yet visible at this project's reachable n. No hedge, softening, or counterpoint was added beyond what the owner stated.
- **Real accuracy gap found and fixed during fact-checking, not silently shipped:** the row 2 text requested by this round's instructions read "small_angle came out inconclusive in every tested scope and every follow-up (bandwidth grid, data-dependent init) — never resolved either way." Checking this directly against `docs/trainability-study.md`'s own TRAIN-09 bandwidth-grid raw table (lines 285-307) found this claim is not accurate: at sigma=0.3, both `weight1/small_angle` (R²=0.904) and `mixed/small_angle` (R²=0.920) flip to a clear "exp" winning-model verdict — not inconclusive. `docs/technical-findings.md`'s own canonical synthesis prose never surfaces this bandwidth-grid detail for `small_angle` (it only narrates the `uniform`-cell bandwidth story), which is why the discrepancy wasn't caught upstream. Per this project's CLAUDE.md ("push back... name it explicitly rather than complying quietly") and this plan's own precedent (Round 2's dual-rail accuracy fix), the row was corrected rather than shipped as specified: "small_angle was inconclusive in the original sweep and stayed unresolved after TRAIN-10's data-dependent-init follow-up; the bandwidth grid (TRAIN-09) was mostly inconclusive too, but flipped to a clear 'exp' verdict at one tested bandwidth (sigma=0.3, both scopes) — never cleanly resolved either way." This preserves the row's overall "never resolved either way" verdict (which does hold in aggregate — no consistent resolution emerged) while removing the false "inconclusive in every... bandwidth grid" claim. The other 3 rows were independently checked against `docs/iqp-baseline.md` (283 rows/97.9% accuracy, the empirical plateau rule text, the anti-concentration-insufficiency finding) and `README.md`/the page's own existing content (ring_mass 0.6833/0.691) and found accurate as specified — no other row was altered.
- **DataTable cell styling:** matched the page's existing convention (plain-text strings, no markdown backticks — confirmed against `dualRailCrossCheckData`'s own existing rows, which use plain apostrophes/text inside JS string literals since `DataTable` renders cells as-is, non-first columns already styled `font-mono`).

**Working-tree hygiene:** the target file still has the same pre-existing, unrelated uncommitted hero-subtitle change from Round 2 (`"v3.0 study"`/`"didn't exist in the literature before"` → `"broader study"`/`"is not widely explored in the literature"`), plus the same unrelated modified `public/resume/quantum.pdf` and untracked `image.png`. All three were left exactly as found — not committed, not discarded — using `git add -p` to stage only this round's two new hunks (the new `bigPictureData` const; the new Section block), explicitly declining the pre-existing subtitle hunk when prompted.

**Verification:**
- `npm run lint` in `alejandro-jackson`: clean — zero warnings in `merlin-quantum.tsx`; only the same pre-existing warnings in unrelated files already documented in prior rounds (`InfiniteCarousel.tsx`, `about.tsx`, `iqp-mmd.tsx`, `contact.tsx`, `index.tsx`).
- `npm run build` in `alejandro-jackson`: clean — `next build` exited 0, "Compiled successfully in 3.0min," all 42/42 static pages generated with zero build-time errors. `/case-studies/merlin-quantum` grew from 12.3 kB/190 kB First Load JS (prior round) to 13.4 kB/191 kB. No regression to any other route.

**Commit:** one combined commit, continuing this plan's original override of GSD's default one-commit-per-task convention — `feat(case-studies): add Bigger Picture synthesis section to merlin-quantum page` (`28ad9dc` in `alejandro-jackson`; commit message documents the row-2 correction inline). `alejandro-jackson`'s `main` is now 5 commits ahead of `origin/main`: pre-existing `40889a1`, this plan's original `efc3bf1`, round-1-feedback `971c0f0`, round-2 `2f5ec70`, plus this round's `28ad9dc`. Still not pushed — push remains a separate, explicit owner action outside this plan's scope.

**Status:** returning to checkpoint again for final owner approval. Not yet marked "approved."

---
*Phase: 21-external-facing-framing-pass*
*Completed: 2026-08-19*
