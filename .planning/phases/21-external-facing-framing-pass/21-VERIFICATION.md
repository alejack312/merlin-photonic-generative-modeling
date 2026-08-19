---
phase: 21-external-facing-framing-pass
verified: 2026-08-19T19:12:16Z
status: passed
score: 5/5 must-haves verified
---

# Phase 21: External-Facing Framing Pass Verification Report

**Phase Goal:** Produce an external-facing framing pass (README/case-study level) of the milestone's findings, following this project's established "mechanism-not-magic, ownership-forward" convention -- kept separate from Phase 20's candid internal write-up, which stays unvarnished as-is.
**Verified:** 2026-08-19T19:12:16Z
**Status:** passed
**Re-verification:** No -- initial verification

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | An external-facing case-study treatment exists for v3.0, distinct from Phase 20's internal write-up | VERIFIED | `merlin-quantum.tsx` (alejandro-jackson repo) grew from 524 to 981 lines; new content is prose/DataTable/QuoteBlock, not a restatement of `docs/technical-findings.md`'s technical prose |
| 2 | A short v3.0 pitch section exists in this repo's README, linking out rather than restating | VERIFIED | `README.md` lines 80-97: `## v3.0: IQP Circuit Study`, 4-paragraph pitch plus "Links out" list pointing to the case-study URL and 4 docs/ files |
| 3 | TRAIN-09 (bandwidth non-robustness), TRAIN-10 (negative result), HARD-04 (no-translation scope decision) are stated as honestly on the case-study page as in `docs/technical-findings.md` | VERIFIED | Case-study "Key insight" callouts state the sigma-grid non-robustness plainly (survives/disappears/re-emerges), TRAIN-10 explicitly labeled "a genuine negative result," HARD-04 stated as "a deliberate scope decision, not a failed attempt" -- same substance and directness as `technical-findings.md` lines 40-45, 144-151, 316-317 |
| 4 | Cited numbers trace to real source-doc numbers, not fabricated or misleadingly rounded | VERIFIED | Spot-checked 11 figures across both docs and both files -- all exact matches (see spot-check table below) |
| 5 | The alejandro-jackson repo's git state matches what the SUMMARY claims (5 commits ahead, unpushed) | VERIFIED | `git log origin/main..HEAD` shows exactly 5 commits (`efc3bf1`, `971c0f0`, `2f5ec70`, `28ad9dc` plus pre-existing `40889a1`); `git status` confirms "ahead of origin/main by 5 commits," nothing pushed |

**Score:** 5/5 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| `C:\Users\cuqui\projects\alejandro-jackson\src\pages\case-studies\merlin-quantum.tsx` | v3.0 Section blocks, Bigger Picture, extended Role/hero/badges | VERIFIED | All claimed sections present (see below), substantive prose plus real DataTable data, wired into the page's render tree (not orphaned) |
| `C:\Users\cuqui\projects\alejandro-jackson\src\pages\index.tsx` | MerLin featured-case-study entry | VERIFIED | `featuredCaseStudies[0]` is the MerLin entry, first in the array, with real metrics (`ring_mass=0.691`, `R^2=0.999*`, `4/4 GO`) and `accent: "blue"` wired to a matching `accentClasses.blue` entry |
| `C:\Users\cuqui\merlin-quantum-case-study\README.md` | `## v3.0: IQP Circuit Study` section | VERIFIED | Present, 18 lines, between `## Process & AI Use` and `## License`, links out rather than restating |

**Section inventory confirmed present in `merlin-quantum.tsx`** (via `grep -n 'title='`): Key Metrics, TL;DR (v1.0), Context, Methodology, Key Finding, Held-Out Benchmarking, Technical Depth, **TL;DR: v2.0 -> v3.0** (new), **IQP -> Photonic Encoding & Weight-2 Gate** (new, v2.0-2.1 bridge), **Trainability & Hardness Under Loss** (new), **Gate Validation & Independent Verification** (new, includes dual-rail cross-check subsection), **Bigger Picture** (new, with comparison DataTable plus owner QuoteBlock verdict), Role (extended), What I'd Do Next (extended with v3.0 grouped items), Source Code.

Dark-alternation preserved as claimed: Technical Depth(dark) -> TL;DR v2-v3(not dark) -> v2.0-2.1 bridge(dark) -> TRAIN/HARD(not dark) -> Supporting Evidence(dark) -> Bigger Picture(dark, back-to-back precedented elsewhere on the page) -> Role(not dark).

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| README v3.0 section | case-study page | markdown link to `https://alejandrojackson.dev/case-studies/merlin-quantum` | WIRED | URL present, matches plan's `important_notes` override of the stale-URL flag in 21-RESEARCH.md |
| README v3.0 section | `docs/technical-findings.md` plus 4 source docs | relative markdown links | WIRED | All 5 links present and point to real files in this repo |
| `index.tsx` featured-card | `merlin-quantum.tsx` | `link: "/case-studies/merlin-quantum"` | WIRED | Route matches the actual page file's path |
| Case-study "Key insight" callouts | `docs/trainability-study.md` / `docs/hardness-under-loss-study.md` numbers | hardcoded figures matching source tables | WIRED | See spot-check table below -- all traced |

### Requirements Coverage

| Requirement | Status | Blocking Issue |
|-------------|--------|-----------------|
| WRITE-07 | SATISFIED | Both artifacts (README section + case-study page) shipped, distinct from Phase 20's internal doc, honest verdicts preserved, numbers verified accurate |

### Number Spot-Check (11 figures traced to source)

| Cited figure | Location in case-study/README | Source doc | Source location | Match |
|---|---|---|---|---|
| weight1/uniform exp R^2=0.999 | TRAIN DataTable | `docs/trainability-study.md` | line 82 | exact |
| mixed/uniform exp R^2=0.910 | TRAIN DataTable | `docs/trainability-study.md` | line 84 | exact |
| alpha=16.2048 (n=6, eta=0.99) to ~4.46e-15 (eta=0.05) | HARD "Key insight" | `docs/hardness-under-loss-study.md` | lines 173-174 | exact |
| weight-2 herald rate 2/27 | v2.0-2.1 bridge section | `docs/iqp-photonic-encoding.md` | line 105 | exact ("exactly 2/27 (~0.074074)") |
| TVD=2.6e-15 at locked gate | v2.0-2.1 bridge section | `docs/iqp-photonic-encoding.md` | line 102 ("TVD=2.58e-15") | matches (rounded consistently) |
| 118/118 composability test suite | v2.0-2.1 bridge section | `.planning/ROADMAP.md` | line 337 ("118/118 suite green") | exact |
| TVD ~1e-16 at n=2,3 | v2.0-2.1 bridge section | `docs/iqp-photonic-encoding.md` | line 334 | exact |
| dual-rail weight1/uniform exp R^2=0.983 (n=2-8) | Supporting Evidence dual-rail table | `docs/trainability-study.md` | lines 488, 500 | exact |
| dual-rail mixed/uniform R^2=0.840, disagree | Supporting Evidence dual-rail table | `docs/trainability-study.md` | lines 490, 502 | exact |
| sigma=0.3 flips both scopes' small_angle to "exp" (R^2=0.904/0.920) | Bigger Picture row-2 correction (round 3) | `docs/trainability-study.md` | lines 287, 304 | exact -- correction is accurate, not a fabricated fix |
| dual-rail HARD max diffs (3.84e-6, 6.17e-7, 0.1434, 0.05382, 5.7774) | Supporting Evidence dual-rail table | `docs/hardness-under-loss-study.md` | lines 355-363 | exact |

No fabricated or misleadingly-rounded numbers found across the spot-check.

### Anti-Patterns Found

None. No TODO/FIXME/placeholder/stub patterns in either modified file. No empty handlers, no dead links, no softened verdicts relative to `docs/technical-findings.md`.

### Git State Verification (alejandro-jackson repo)

Confirmed via `git log`, `git status`, `git log origin/main..HEAD`:
- `main` is 5 commits ahead of `origin/main`: `40889a1` (pre-existing, unrelated) -> `efc3bf1` -> `971c0f0` -> `2f5ec70` -> `28ad9dc`.
- Nothing pushed.
- Working tree has 3 pre-existing, unrelated uncommitted items (confirmed via `git diff`): a softened hero-subtitle wording change, a modified `public/resume/quantum.pdf`, and an untracked `image.png` -- all documented in the SUMMARY as intentionally untouched, and confirmed by direct `git diff` inspection to be exactly the claimed one-sentence subtitle softening (not scope creep from this phase's work).

### Human Verification Required

None required for structural/content verification -- all claims were checkable against source files and git state directly. The SUMMARY notes a final visual/render check is optional but not blocking; since the owner already reviewed and approved the rendered page across 4 checkpoint rounds (documented in 21-01-SUMMARY.md's "Checkpoint Approved" section), this is not treated as an open gap.

### Gaps Summary

None. All 5 derived must-haves verified against actual file content and git state, not SUMMARY claims alone. Both artifacts (README section, case-study page) exist, are substantive, are wired correctly, preserve Phase 20's honest verdicts without softening, and all spot-checked numbers trace to real source-doc figures. The round-3 fact-check correction documented in 21-01-SUMMARY.md (small_angle bandwidth-grid claim) was independently re-verified here and found accurate.

---
*Verified: 2026-08-19T19:12:16Z*
*Verifier: Claude (gsd-verifier)*
