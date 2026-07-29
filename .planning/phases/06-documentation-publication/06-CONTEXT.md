# Phase 6: Documentation & Publication - Context

**Gathered:** 2026-07-29
**Status:** Ready for planning

<domain>
## Phase Boundary

Package the project into artifacts the owner can explain unaided: README (DOC-01), a public GitHub repo (DOC-02), a 3-5 sentence technical note to Vincent Espitalier (DOC-03), and a portfolio case study (DOC-04). No new generator/benchmark code — this phase documents and publishes what Phases 1-5 already produced (including Phase 4's honest GEN-07 "not met" result).

</domain>

<decisions>
## Implementation Decisions

### README structure & framing
- Primary audience: technical reader (ML/quantum background) — go straight into MMD², ring_mass, photonic circuit specifics without over-explaining basics.
- GEN-07 "not met" result: **headline honesty** — state plainly near the top what worked and what didn't, including the measured improvement path (ring_mass 0.609 → 0.691). Do not bury it in a caveats section.
- Depth: README summarizes problem/approach/results with numbers and plots; links out to `DESIGN_DECISIONS.md`, phase SUMMARY.md files, and the two mechanism deep-dives (see Repo scope below) for full detail — not a monolithic single document.
- Visuals to include: generated-vs-real scatter/heatmap comparison (Phase 4), training loss curve (Phase 3), benchmark comparison table/chart (Phase 5: trained/untrained/floor MMD²).

### AI disclosure in the README
- Must be honest, not hype, not silent — and not read as "vibecoded." Apply the existing decision in `[[phase6-ai-disclosure-framing]]` memory: mechanism-not-magic, ownership-forward.
- Placement: a short one-line mention near the top (e.g. under a "How this was built" line), plus a fuller "Process & AI Use" section near the bottom of the README.
- Framing: state that Claude Code assisted under a self-imposed discipline — "I verify every AI-assisted component against my own unaided explanation before it ships" — never "the AI checked whether I understood the code" or "the AI caught my mistake." Same underlying facts, ownership-forward phrasing.
- Internal artifacts (DESIGN_DECISIONS.md, phase SUMMARY.md files, git history) stay candid as-is — they're the paper trail proving genuine understanding, not to be scrubbed or softened.

### Technical note to Vincent Espitalier
- Channel: LinkedIn/message style — short, casual, no subject line (not a formal email).
- Opens with the result (what was built, honest outcome), but includes brief pretext connecting it to the prior IQP-MMD project as the methodology source before the photonic-specific result.
- GEN-07 shortfall gets exactly one honest clause (e.g. "...ring structure improved substantially but isn't fully resolved yet") — present but brief, doesn't dominate the 3-5 sentences.
- No explicit ask/CTA. Share the work and let it stand; no "let's schedule a call" push.

### Portfolio case study format (DOC-04)
- **Not** a markdown file in this repo, and **not** the alejandro-jackson-freelance MDX template. The actual reference is `C:\Users\cuqui\projects\alejandro-jackson\src\pages\case-studies\iqp-mmd.tsx` — a full interactive Next.js/TSX page built from shared components in `src/components/case-studies/shared.tsx` (`CaseStudyLayout`, `CaseStudyHero`, `MetricsGrid`, `Section`, `CalloutBox`, `DataTable`, `ProcessStep`, `QuoteBlock`, `CrossLinks`).
- Scope: build the full TSX page in that portfolio repo (e.g. `src/pages/case-studies/merlin-quantum.tsx` or similar name — final slug TBD), matching the `iqp-mmd.tsx` structure: hero, key-metrics grid, TL;DR callout, context section, architecture/methodology, a "key finding" section, technical-depth cards, role/authorship, "what I'd do next," source-code link, and `CrossLinks` registration so it's discoverable from the case-studies index.
- Cross-repo work: this phase's plan must account for editing a second repository (`C:\Users\cuqui\projects\alejandro-jackson`), not just `merlin-quantum-case-study`.
- Accent color: pick a new one distinct from `iqp-mmd.tsx`'s "sky" (e.g. violet or emerald) so the two projects read as visually separate on the case-studies index.
- Key finding, mirroring `iqp-mmd.tsx`'s "MMD ≠ Shape": something like "good MMD² ≠ clean ring structure" — a good scalar loss/benchmark number does not by itself mean the generator learned the target's spatial shape. Pair with the natural-order-correspondence fix (K=462, radius-sorted bins) as the technical highlight, the same honest framing as the README (state the shortfall plainly, don't bury it).
- Custom visualizations: 2-3 bespoke animated components in the `iqp-mmd.tsx` style, e.g. an animated chart of ring_mass improving across the three tuning axes (sigma sweep → batch sweep → natural-order fix), and a benchmark bar comparison (trained vs untrained vs floor MMD²) — not just static images dropped into `DataTable`/`MetricsGrid`.

### Public repo scope & cleanup
- `mmd-loss.md` and `raster-order.md` (currently untracked at repo root) move into a `docs/` folder and get committed — they're exactly the "explainable unaided" mechanism evidence Vincent would want, and should be linked from the README as deep-dive reading, not left as unlinked scratch notes.
- Cleanup in scope before going public: add a LICENSE file (e.g. MIT, none exists yet); prune any leftover scratch scripts/dead files/stale artifacts not referenced by the README or results; verify `.gitignore` correctly excludes the venv and any large binary checkpoints that shouldn't be tracked.
- Claude prepares everything (README, LICENSE, docs/ moves, cleanup commits, pushes to the existing remote) but does **not** flip the GitHub repo's visibility from private to public — the owner does that toggle themselves as the final step.

### Claude's Discretion
- Exact wording/copy throughout (README prose, technical note phrasing, case-study section copy) — draft it, owner reviews.
- Final slug/filename for the new case-study TSX page and its exact route.
- Which specific scratch/dead files (if any) get pruned during cleanup — identify and report before deleting anything non-obvious.
- Exact chart types/layout for the 2-3 custom case-study visualizations, as long as they follow the `iqp-mmd.tsx` interactivity level (framer-motion animated bars/reveals).

</decisions>

<specifics>
## Specific Ideas

- Case-study "Key Finding" framing should deliberately echo `iqp-mmd.tsx`'s "MMD ≠ Shape" pattern — same lesson (a scalar loss number can look good while the target's actual structure isn't learned), now demonstrated a second time in a different domain (photonic/spatial vs. gate-model/combinatorial). Worth stating that continuity explicitly in the "Role"/context section, the same way the technical note leads with the IQP-MMD connection.
- AI-disclosure exact phrasing already drafted in memory `[[phase6-ai-disclosure-framing]]`: prefer "I verify every AI-assisted component against my own unaided explanation before it ships" over "the AI caught my misunderstanding and corrected it."

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope. (Exact replication of MerLin's photonic QGAN paper's full MNIST-patch dataset, mentioned as a stretch goal in PROJECT.md, is explicitly out of scope for this phase and wasn't revisited here.)

</deferred>

---

*Phase: 06-documentation-publication*
*Context gathered: 2026-07-29*
