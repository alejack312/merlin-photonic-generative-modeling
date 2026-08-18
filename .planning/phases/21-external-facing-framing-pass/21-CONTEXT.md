# Phase 21: External-Facing Framing Pass - Context

**Gathered:** 2026-08-19
**Status:** Ready for planning

<domain>
## Phase Boundary

Produce an external-facing framing of the v3.0 milestone's findings (trainability/barren-plateau study, hardness-under-loss study, ARB-01 gate validation, Julia cross-checks) — README/case-study level, following this project's established "mechanism-not-magic, ownership-forward" convention. Kept separate from Phase 20's candid internal write-up (`docs/technical-findings.md`, `docs/trainability-study.md`, `docs/hardness-under-loss-study.md`, `docs/iqp-photonic-encoding.md`, `docs/julia-cross-check-study.md`), which stays unvarnished as-is.

</domain>

<decisions>
## Implementation Decisions

### Deliverable location — two artifacts, two repos
- **Primary deliverable:** extend the existing case-study page at `C:\Users\cuqui\projects\alejandro-jackson\src\pages\case-studies\merlin-quantum.tsx` (a separate Next.js portfolio repo, NOT this repo) with new content covering the v3.0 IQP circuit study. This is not a markdown file — it's a React/TSX page built from shared components (`CaseStudyLayout`, `CaseStudyHero`, `MetricsGrid`, `Section`, `CalloutBox`, `DataTable`, `ProcessStep`, `QuoteBlock`, `CrossLinks`, imported from `~/components/case-studies/shared`).
- Extend the same page/URL rather than create a new standalone page (e.g. `iqp-circuit-study.tsx`) — one continuous story spanning v1.0 → v3.0, not a second page cross-linked via `CrossLinks`.
- **Secondary deliverable:** this repo's `README.md` gets a short v3.0 pitch section that links out to the portfolio case-study page for the full story — not a full restatement.

### Content selection & emphasis
- Trainability (TRAIN, Phase 17/17.1) and hardness-under-loss (HARD, Phase 18) are co-lead findings — the two measured research claims from this milestone. ARB-01 (gate validation) and the Julia cross-checks are supporting/infrastructure material, not headline findings.
- Negative/inconclusive results (the exponential-decay barren-plateau signature not being robust to bandwidth per Phase 17.1's sigma-grid sweep; `small_angle`/data-dependent init both staying inconclusive; no principled eta-to-depolarizing-rate translation found in Phase 18) are stated with the same honesty as the internal docs — not softened, not buried — but the *process* that surfaced them (the sigma-grid sweep, the literature-grounded HARD-04 checkpoint) is framed as evidence of rigor, similar in spirit to how the existing page frames the MMD²-vs-ring_mass tension as its headline finding rather than hiding it.

### Audience & narrative shape
- Primary reader: a general technical recruiter/engineer, same audience tier as the existing v1.0 page — technical but not necessarily a photonic-QC specialist. Terms get brief inline explanation, matching the existing page's voice (e.g. how it explains QuantumLayer, MMD², ring_mass on first use).
- One shared narrative arc covers all four v3.0 tracks together (TRAIN, HARD, ARB-01, Julia), rather than repeating a full TL;DR → Methodology → Key Finding block four times. The existing page's per-study section pattern (Context, Methodology, Key Finding, Technical Depth) still applies, but scoped to the v3.0 milestone as one unit, not fragmented per track.

### AI-disclosure framing
- Follows [[phase6-ai-disclosure-framing]]'s established convention: state plainly that Claude Code assisted under a self-explanation-required workflow, framed as a discipline the owner imposed on his own process (not "the AI checked my understanding").
- Update the existing "Role" `QuoteBlock` section (currently v1.0-only: "Solo project. I own the full pipeline...") to also cover the v3.0 work, rather than adding a separate disclosure section elsewhere on the page.

### Claude's Discretion
- Whether the Role section's AI-disclosure language calls out the specific transcribed-reasoning mechanism (TRAIN-07's self-explanation checkpoint literally transcribing the owner's own reasoning dialogue verbatim into `docs/trainability-study.md`) by name, or stays general like v1.0's existing phrasing — Claude proposes phrasing during drafting, following the mechanism-not-magic convention either way.
- Exact section headings/order within the shared narrative arc, which of the four tracks' specific numbers/charts to visualize (mirroring the existing page's `RingMassProgressionChart`/`BenchmarkComparisonChart` pattern), and page length.
- Whether to add new interactive chart components (e.g. a bandwidth-sensitivity chart for TRAIN-09, a TVD-vs-eta chart for HARD) or reuse `DataTable`/`MetricsGrid` only.

</decisions>

<specifics>
## Specific Ideas

- The v1.0 page's existing pattern of stating a "key insight" callout box after a chart (e.g. the natural-order-correspondence-fix insight) is the model to follow for v3.0's headline tension too — likely something like "the barren-plateau signature looked real at one bandwidth, but a systematic sweep showed it wasn't robust."
- The existing Role `QuoteBlock` ends with "Built as a credential-building exercise ahead of a Quandela internship conversation" — this framing (explicit purpose, no hype) should carry forward into whatever the v3.0 addition says.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope. (Note: work on the case-study page itself happens in a separate repo, `C:\Users\cuqui\projects\alejandro-jackson`, not this one — downstream planning/execution for that half of this phase will need to operate cross-repo.)

</deferred>

---

*Phase: 21-external-facing-framing-pass*
*Context gathered: 2026-08-19*
