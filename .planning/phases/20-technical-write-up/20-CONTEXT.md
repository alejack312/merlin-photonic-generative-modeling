# Phase 20: Technical Write-Up - Context

**Gathered:** 2026-08-18
**Status:** Ready for planning

<domain>
## Phase Boundary

Write up STUDY-01 (Phase 17 + 17.1 trainability), STUDY-02 (Phase 18 hardness-under-loss), and ARB-01's (Phases 15-16 tunable gate) findings as the project's technical findings document — methodology-stated-before-results, honest negative/inconclusive framing wherever the data warrants it, matching this project's existing GEN-07/LIT-04/Phase-7 rigor bar. Internal/candid document — external-facing reframing is Phase 21's separate job and must not be pulled forward here.

</domain>

<decisions>
## Implementation Decisions

### Deliverable shape
- **New synthesis doc + edits to the three source docs** (not one or the other alone).
- New doc: `docs/technical-findings.md` (matches this project's existing `docs/` naming convention — `iqp-baseline.md`, `trainability-study.md`, etc.).
- The three source docs stay as the detailed record and get direct edits wherever WRITE-01..06 finds a real gap in them (e.g. filling TRAIN-07's pending owner interpretation — see below).
- Source docs in scope: `docs/trainability-study.md` (TRAIN, includes the 17.1 follow-up sections already), `docs/hardness-under-loss-study.md` (HARD), the ARB-01/ARB-02 section of `docs/iqp-photonic-encoding.md` (ARB). `docs/julia-cross-check-study.md` is supplementary evidence only — include if it strengthens a point, do not block on it, do not force WRITE-01..06 structure onto it (per ROADMAP.md's explicit Phase 20 "Depends on" note).

### Self-explanation checkpoint (WRITE-05)
- **Reuse what's already recorded, close the one open gap.**
- ARB-01/ARB-02 already has extensive Socratic-method attempt-first records in `docs/iqp-photonic-encoding.md` (lines 379-389) — cite/reuse, do not re-run.
- HARD-04 already has an owner attempt-first response recorded in `docs/hardness-under-loss-study.md` (~line 364) — cite/reuse, do not re-run.
- TRAIN-07's cross-reference-verdict owner interpretation is genuinely `[pending]` (`docs/trainability-study.md:174`) — this is a real, currently-open gap, not a formality.
- **Timing: run this checkpoint later, during Phase 20 execution** (not during this discussion). It should land in the Phase 20 plan as an explicit task, following the same self-explanation-checkpoint ritual already used for ENC-05 and HARD-04 — the owner explains, unaided, what the TRAIN-07 agree/disagree pattern means (`weight1/uniform` agrees with `iqp-baseline.md`'s empirical rule, `mixed/uniform` disagrees) before that section of the write-up is marked done.

### Literature comparison table (WRITE-02)
- **Three separate per-section tables**, not one unified table — TRAIN, HARD, and ARB-01 each get their own table listing only the baselines actually relevant to that section (avoids rows full of "silent").
- **Location: both** — each table is authored canonically inside its own source doc, next to that doc's existing "what this does/doesn't establish" section, then the same table is mirrored/repeated in `docs/technical-findings.md` so a reader gets the full picture without jumping around.
- 11 named baselines to cover across the three tables (per `REQUIREMENTS.md` WRITE-02 / ROADMAP.md Phase 20 success criterion 2): McClean et al., Aaronson-Brod (arXiv:1510.05245, already read in Phase 18), arXiv:2510.24137 (Park & Oh), arXiv:2405.01395, `docs/iqp-baseline.md`'s own empirical rule, Bremner-Montanaro-Shepherd 2015 (arXiv:1504.07999), Bremner-Montanaro-Shepherd 2017 (arXiv:1610.01808, already read in Phase 18), Rudolph et al. (arXiv:2305.02881, already engaged in Phase 17.1's TRAIN-09), Mhiri et al. (arXiv:2502.07889), Recio-Armengol et al. (arXiv:2503.02934, already implemented in Phase 17.1's TRAIN-10), Herbst et al. (arXiv:2512.24801, see cross-thread below). Each cell: consistent / inconsistent / silent, stated per baseline.

### Herbst et al. cross-thread (success criterion 6)
- **Woven into both source docs' existing scope sections** — not a new standalone section anywhere (not in either source doc, not in the synthesis doc as its own section).
- Add a short cross-reference note into `trainability-study.md`'s and `hardness-under-loss-study.md`'s existing "what this does/doesn't establish" sections, each pointing at the other, stating plainly whether this project's measured TRAIN result (Phase 17/17.1) and HARD result (Phase 18) came out consistent or inconsistent with Herbst et al.'s prediction that anticoncentration drives both.
- The synthesis doc (`docs/technical-findings.md`) should still surface this connection where it ties the two sections together, but the substantive analysis lives in the two source docs per the above — the synthesis doc's job is pointing the reader at it, not re-deriving it.

### Claude's Discretion
- Exact prose/structure of `docs/technical-findings.md` beyond the "synthesis + tables mirrored + links to source docs" shape locked above — table of contents, ordering of the three sections, how much executive-summary framing to add up front.
- Exact wording of the three comparison tables' column headers and per-baseline justification text, as long as the consistent/inconsistent/silent verdict and the table-per-section structure are honored.
- Precise placement (which existing subsection, what exact heading) of the Herbst et al. cross-reference notes within each source doc's scope section.

</decisions>

<specifics>
## Specific Ideas

- The comparison tables and self-explanation checkpoints should match this project's established conventions exactly, not invent new formats: the "> Owner interpretation:" blockquote style already used in `trainability-study.md`, and the "### Self-Explanation Checkpoint" / "Owner's Attempt" heading style already used in `iqp-photonic-encoding.md` and `hardness-under-loss-study.md`.
- Nothing here should soften or pre-narrate any of Phase 17/17.1/18's honest negative/inconclusive findings (the exp-decay signature not surviving the sigma grid, TRAIN-10's data-dependent init not resolving the inconclusive verdict, HARD-04's "no forced translation" conclusion) — Phase 20 organizes and cross-references existing honest findings, it does not re-litigate or re-interpret them beyond the one genuinely open TRAIN-07 gap.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope. (WRITE-07's external-facing framing pass was explicitly named as Phase 21's separate job, not pulled forward here.)

</deferred>

---

*Phase: 20-technical-write-up*
*Context gathered: 2026-08-18*
