# Phase 21: External-Facing Framing Pass - Research

**Researched:** 2026-08-19
**Domain:** Content/structure research for a React/TSX portfolio page extension + README pitch section (no new libraries; this is a writing/placement task, not a stack-selection task)
**Confidence:** HIGH (all findings read directly from source files, not inferred)

## Summary

This phase has two small, mechanical edit targets in two different repos, both already fully scaffolded — there is no new tooling, library, or architecture to research. The real research work was (1) mapping the *exact* current structure of the target case-study page so the planner can specify precisely where v3.0 content is inserted, (2) extracting the shared component prop APIs so tasks can call them correctly on the first try, and (3) pulling the specific numbers/verdicts a writer needs from this repo's Phase 20 synthesis doc and its three source docs, with file:line traceability so the plan doesn't have to re-derive them.

The case-study page (`merlin-quantum.tsx`) currently tells a single, complete v1.0 story with no "Conclusion" section — it runs Hero → Key Metrics → TL;DR → Context → Methodology → Key Finding → Benchmarking → Technical Depth → **Role** → What I'd Do Next → Source Code → CrossLinks. Because "Role" doubles as the page's only authorship/capstone-feeling section and the locked decision requires updating (not duplicating) it, the natural insertion point for the new v3.0 content is **between "Technical Depth" and "Role"** — this keeps Role as the single joint capstone for both v1.0 and v3.0 work, and avoids the "appended after a conclusion" anti-pattern the phase context explicitly warns against (there's no literal Conclusion section to append after, but "What I'd Do Next" / "Source Code" read as the page's tail-end wind-down, so v3.0 content landing after them would read as an afterthought).

**Primary recommendation:** Insert one new v3.0 `Section` block (or a small run of 2-4 sections sharing one narrative arc, per the locked "one shared arc, not four repeated blocks" decision) immediately after the existing "Technical Depth" section and before "Role"; then edit the existing "Role" `QuoteBlock` text in place to add a second sentence/paragraph covering v3.0 authorship and the self-explanation-checkpoint AI-disclosure framing. In this repo's README, add one new top-level section (working title "v3.0" or similar) after the existing content, linking out to the case-study page rather than restating its numbers.

## Current State: `merlin-quantum.tsx`

**Full path:** `C:\Users\cuqui\projects\alejandro-jackson\src\pages\case-studies\merlin-quantum.tsx` (524 lines)

**Exact section order (top to bottom), with the shared component each uses:**

| # | JSX comment marker | `Section` `label`/`title` | Component(s) used | Notes |
|---|---|---|---|---|
| 1 | `{/* ── Hero ── */}` | n/a | `CaseStudyHero` | `accent="blue"`, badges include "MerLin", "PyTorch", "Perceval", "Photonic QML", "MMD Loss", "Quantum Generative Modeling" |
| 2 | `{/* ── Key Metrics ── */}` | label "At a Glance", title "Key Metrics" | `Section` > `MetricsGrid` | 4 metric cards (held-out MMD², ring_mass, params, training time) |
| 3 | `{/* ── TL;DR ── */}` | title "TL;DR", `dark` | `Section` > `CalloutBox title="Summary"` | one paragraph |
| 4 | `{/* ── Context ── */}` | label "Background", title "Context" | `Section` > raw prose (3 `<p>`s in a `max-w-3xl` div) | no shared box component, just styled prose |
| 5 | `{/* ── Methodology ── */}` | label "How", title "Methodology", `dark` | `Section` > 5× `ProcessStep` | numbered 01-05 |
| 6 | `{/* ── Key Finding ── */}` | label "Key Finding", title "Good MMD² ≠ Clean Ring Structure", `dark` | `Section` > prose + custom `RingMassProgressionChart` + `DataTable` + inline insight box | the "insight box" is hand-rolled (`rounded-lg border border-blue-400/20 bg-blue-400/5 px-4 py-3`), not a shared component — same markup pattern is reused inside `RingMassProgressionChart` itself |
| 7 | `{/* ── Benchmarking ── */}` | label "BMK-01", title "Held-Out Benchmarking" | `Section` > prose + custom `BenchmarkComparisonChart` + `DataTable` | |
| 8 | `{/* ── Technical Depth ── */}` | label "Depth", title "Technical Depth", `dark` | `Section` > hand-rolled 2-col grid of `motion.div` cards (NOT a shared component) | 6 cards from `technicalDepth` array |
| 9 | `{/* ── Role ── */}` | label "Authorship", title "Role" | `Section` > `QuoteBlock` | **the section CONTEXT.md says to update in place** — currently v1.0-only text, ends "...ahead of a Quandela internship conversation." |
| 10 | `{/* ── What I'd Do Next ── */}` | label "Future", title "What I'd Do Next", `dark` | `Section` > hand-rolled bullet list (`motion.div` + dot) | 7 items, all v1.0-specific (BMK-03, GAN comparison, sigma re-sweep, etc.) — **not in this phase's locked scope to edit**, but the planner should be aware these read as the page's forward-looking "future work" and a v3.0 addition landing after them (if inserted at the very end) would contradict that framing |
| 11 | `{/* ── GitHub Link ── */}` | title "Source Code" | hand-rolled `<a>` block with inline SVG | links to `https://github.com/alejack312/merlin-photonic-generative-modeling` — **confirmed correct**: this repo's own `git remote -v` origin is exactly that URL (the working-directory folder name `merlin-quantum-case-study` differs from the GitHub repo name, which is expected and not a bug) |
| 12 | `{/* ── Cross Links ── */}` | n/a | `CrossLinks current="merlin-quantum"` | must always be last |

**Exact current "Role" QuoteBlock text** (lines 452-465):
> "Solo project. I own the full pipeline: choosing full-distribution MMD matching over point-averaging or discrete sampling, implementing the closed-form loss, diagnosing why the generated rings kept fragmenting, designing and implementing the radius/center-of-mass correspondence fix, and running the held-out benchmarks. Built as a credential-building exercise ahead of a Quandela internship conversation. The MMD/diagnostic approach carries forward directly from IQP-MMD, my earlier gate-model project: same core question about loss versus learned structure, asked again in a photonic domain."

This is the exact text the plan must extend (not replace) — CONTEXT.md's lock is "update... to also cover v3.0 work," so the v1.0 sentences should stay, with v3.0 authorship/AI-disclosure language added.

**Recommended insertion point:** between marker `{/* ── Technical Depth ── */}` (ends line 449) and `{/* ── Role ── */}` (starts line 451). This is a single clean JSX insertion point — no section needs to be reordered or split.

**Constant to reuse or extend:** `ACCENT: AccentColor = "blue"` (line 18) is used everywhere. The locked decision doesn't request a new accent color for v3.0 content, and reusing `blue` keeps "one continuous story" rather than visually partitioning v1.0 vs v3.0 — recommend the plan state explicitly whether v3.0 content stays `blue` or gets its own accent (this is Claude's-discretion territory not resolved by CONTEXT.md; staying `blue` is the safer default given the "one continuous story" lock).

## Shared Component API

**Actual file location:** `C:\Users\cuqui\projects\alejandro-jackson\src\components\case-studies\shared.tsx` — **this is a single file, not a directory** (the import path `~/components/case-studies/shared` resolves to `shared.tsx` via Next.js's extensionless import resolution; CONTEXT.md's phrasing of "the `~/components/case-studies/shared` directory" is imprecise but harmless — there is no `shared/index.ts` or sub-files to worry about).

Exported members relevant to this phase, with exact prop signatures (verified from source, not memory):

```typescript
export type AccentColor = "cyan" | "amber" | "violet" | "emerald" | "sky" | "blue";

export function CaseStudyHero({
  accent: AccentColor;
  label: string;
  title: string;
  subtitle: string;
  badges: string[];
  children?: ReactNode;
}): JSX.Element

export function MetricsGrid({
  accent: AccentColor;
  metrics: { label: string; value: string; detail: string }[];
}): JSX.Element
// renders via MetricCard internally, 2-col mobile / 4-col desktop grid

export function Section({
  accent: AccentColor;
  label?: string;       // optional small uppercase kicker above title
  title: string;        // required
  children: ReactNode;
  dark?: boolean;       // default false; alternates background tint — existing page alternates true/false roughly every other section
}): JSX.Element

export function CalloutBox({
  accent: AccentColor;
  title?: string;
  children: ReactNode;
}): JSX.Element

export function DataTable({
  accent: AccentColor;
  headers: string[];
  rows: string[][];     // NOTE: all cells are strings — numeric values must be pre-formatted (e.g. .toFixed(3)) before passing in, matching existing usage
}): JSX.Element

export function ProcessStep({
  accent: AccentColor;
  number: string;       // e.g. "01" — caller supplies zero-padded numbering, not auto-numbered
  title: string;
  children: ReactNode;
}): JSX.Element

export function QuoteBlock({
  accent: AccentColor;
  children: ReactNode;
  attribution?: string; // NOT used by the existing Role section (no attribution prop passed) — stays unattributed styled italic text
}): JSX.Element

export function CrossLinks({ current: string }): JSX.Element
// current must match one of allStudies[].slug (this page uses "merlin-quantum") — must be the LAST element in CaseStudyLayout's children

export function CaseStudyLayout({ children: ReactNode }): JSX.Element
// no props beyond children; just a <main> wrapper

export function AnimatedBar({
  label: string; value: number; maxValue: number; accent: AccentColor; suffix?: string; index?: number;
}): JSX.Element
// exported but UNUSED by merlin-quantum.tsx currently (it hand-rolls its own bar charts instead — see below)

export function AnimatedCounter({ value: number; suffix?: string; duration?: number }): JSX.Element
// exported but UNUSED by merlin-quantum.tsx currently

export function MetricCard(...) // exported, used internally by MetricsGrid, not called directly by the page
export function SweCrossLinks(...) // for a different page family (`/swe/case-studies/`), not relevant here
```

**Important gap:** `RingMassProgressionChart` and `BenchmarkComparisonChart` (the two custom bar-chart-style visualizations CONTEXT.md references as "the pattern to mirror") are **NOT shared components** — they are page-local functions defined directly inside `merlin-quantum.tsx` (lines 96-200), using `motion.div` + `useInView` + manually computed percentage widths, not `AnimatedBar`. If the plan wants a new v3.0 chart (e.g. for the eta-sweep TVD curve or the sigma-grid signature-survival result), the correct move is to write a new page-local function in the same file following this same hand-rolled pattern (or, alternatively, use the exported-but-unused `AnimatedBar`/`MetricsGrid`/`DataTable` — genuinely simpler, no new code to write). This is exactly the "which specific numbers/charts to visualize... vs. reuse DataTable/MetricsGrid only" decision CONTEXT.md leaves to Claude's discretion — worth flagging in the plan explicitly rather than defaulting silently to writing more custom chart code.

**Don't hand-roll:** given `DataTable` and `MetricsGrid` already exist and are proven components, and given the phase's own CONTEXT.md explicitly leaves "how much custom charting" open, the lower-risk default is to reuse `DataTable`/`CalloutBox`/`MetricsGrid` for the v3.0 numbers and add at most one new custom chart component only if a specific number benefits strongly from visual framing (the sigma-grid "signature disappears at intermediate sigma" story is the one number in this phase's material that most resembles the existing "ring_mass across axes" chart shape — see Sourceable Numbers below).

## Sourceable Numbers (this repo)

All numbers below are read directly from `docs/technical-findings.md` (Phase 20 synthesis) and cross-checked against the three underlying source docs. File:line references point at `C:\Users\cuqui\merlin-quantum-case-study\docs\...`.

### TRAIN (Phase 17/17.1) — locked as co-lead headline finding

- **Headline finding, original fixed bandwidth (sigma=0.1):** both `weight1/uniform` and `mixed/uniform` show a statistically clear exponential-decay gradient-variance-vs-n signature (exp beats poly on AIC) — `weight1/uniform` exp R²=0.999 (n=2-6), `mixed/uniform` exp R²=0.910 (n=2-5). Both `small_angle`-init cells are inconclusive (`weight1/small_angle` R²=0.543, `mixed/small_angle` R²=0.000). — `docs/technical-findings.md:33-38`, `docs/trainability-study.md:79-83`
- **The headline tension (TRAIN-09, the one CONTEXT.md explicitly calls out as the model for a "key insight" callout, analogous to the existing ring_mass-vs-MMD² tension):** re-running the barren-plateau signature across a six-point sigma grid `{0.03, 0.1, 0.3, 1.0, 3.0, 9.0}` shows it is **NOT robust to bandwidth**. Both `uniform` cells survive only near the original bandwidth (sigma in {0.03, 0.1}), flip to "inconclusive" at intermediate sigma (0.3, 1.0), and `weight1/uniform` then non-monotonically re-emerges as "exp" at high sigma (3.0, 9.0) while `mixed/uniform` stays inconclusive through sigma=9.0. — `docs/technical-findings.md:40-48`, exact per-sigma numbers table at `docs/trainability-study.md:283-313` (e.g. sigma=0.3, weight1/uniform: exp R²=0.988 but flagged "disappears"; sigma=1.0, mixed/uniform: exp R²=0.000)
- **TRAIN-10 negative result:** Recio-Armengol et al.'s literature-sourced data-dependent initialization did **NOT** resolve `small_angle`'s inconclusive verdict in either generator scope (weight1/data_dependent exp R²=0.000; mixed/data_dependent exp R²=0.253, still inconclusive). — `docs/technical-findings.md:49-52`, `docs/trainability-study.md:385-410`
- **TRAIN-07 (the owner's own transcribed self-explanation reasoning, not Claude-authored):** the sibling qubit-side project's empirical plateau rule agrees with measured data for `weight1/uniform` but disagrees for `mixed/uniform`; the owner's conclusion is that the sibling project's specific `n>=6` numeric threshold doesn't hold here, but this is not in tension with the general literature's asymptotic prediction (Recio-Armengol et al., arXiv:2503.02934, Sec. 9.3) that uniform init drives exponential concentration as n grows — only with that sibling project's own qubit-specific fitted cutoff. — `docs/technical-findings.md:54-76`, full transcript at `docs/trainability-study.md:153-` ("Cross-reference verdict (TRAIN-07)" section, line ~153-180)
- **Methodology one-liner for case-study framing:** gradients computed via exact parameter-shift (not MerLin `QuantumLayer` autograd, which doesn't work for this project's polarization-annotated circuits); two generator scopes (`weight1` n=2-6, `mixed` n=2-5) x two init schemes (`small_angle`, `uniform`); loss is exact MMD² via closed form. — `docs/technical-findings.md:20-29`

### HARD (Phase 18) — locked as co-lead headline finding

- **Headline finding:** for every n and both scopes, `tvd_to_lossless` rises monotonically as eta decreases (~0.01-0.03 at eta=0.99 to ~0.50 at eta=0.05), while `tvd_to_uniform`/`tvd_to_product_marginals` fall over the same range, all converging near ~0.50 by eta=0.05. — `docs/technical-findings.md:128-131`
- **The counter-intuitive result (strong case-study candidate — genuinely surprising, verified number):** anticoncentration `alpha(eta) = 2^n * sum(p_x^2)` **decreases** monotonically as eta decreases for both scopes — i.e. **photon loss makes these circuits MORE anticoncentrated, not less** — the reverse of an earlier internal speculative guess (`docs/iqp-baseline.md`'s 2026-08-12 note) about which direction this would go. — `docs/technical-findings.md:132-136,243-250`
  - Concrete alpha values (verified exact against CSVs per Phase 20's own code review, per STATE.md): weight1 n=6 at eta=0.99 alpha=16.2048, dropping to alpha=4.46e-15 at eta=0.05; mixed n=4 at eta=0.99 alpha=3.1992, dropping to alpha=6.37e-12 at eta=0.05. Full table: `docs/hardness-under-loss-study.md:163-201`
- **Weight-2 herald compounding:** `herald_failure_prob` rises monotonically from the near-lossless anchor (~0.926, matching the lossless 2/27 baseline) to 0.999 at eta=0.05 — loss compounds with the gate's own intrinsic herald-failure rate. — `docs/technical-findings.md:139-142`
- **HARD-04 scope/honesty point (an intentional, stated negative — must not be softened):** no eta-to-depolarizing-rate translation was attempted, by deliberate owner scope decision (not a failed attempt) — deriving one would be original numerics work outside project scope. — `docs/technical-findings.md:144-150`
- **Methodology one-liner:** photon loss via `pcvl.LC(1-eta)` with explicit `min_detected_photons_filter(0)`; 7-point eta grid `[0.99, 0.95, 0.90, 0.80, 0.60, 0.35, 0.05]`; two scopes (weight1 n=2-6, mixed n=2-4). — `docs/technical-findings.md:114-124`

### ARB-01/ARB-02 (Phase 15/16) — supporting/infrastructure material

- 16-point alpha sweep spanning `[0, 2*pi)` matches closed-form success probability within 1e-6 at every point. Full-pipeline TVD validation at floating-point-noise level (~1e-16 to 1e-15) for n=2,3. n=3 mixed weight-1+arbitrary-theta weight-2 composability TVD < 1e-6. Forge-based formal check confirmed gate mode-mapping is injective/non-aliasing for n<=8, no bug found. — `docs/technical-findings.md:202-211`

### Julia cross-checks (Phase 19) — supporting/infrastructure material

- All four legs (VERIFY-02 qubit-side/Yao.jl, VERIFY-03 weight-1, VERIFY-03 weight-2/Knill-CZ, VERIFY-04 loss model) reached a genuine GO verdict, independently built (not ported) against a 1e-6 TVD tolerance bar. Representative TVDs: VERIFY-02 n=3: 1.12e-16; VERIFY-03 weight-1 n=3: 3.04e-16; VERIFY-03 weight-2 locked: 3.497e-15; VERIFY-04 mixed loss model: GO across eta in {0.99, 0.80, 0.05}. — `docs/julia-cross-check-study.md:68-249`, `docs/technical-findings.md:262-276`

### Trainability/hardness connection (cross-thread finding, potentially strong case-study material)

- Herbst et al. (arXiv:2512.24801) predict anticoncentration should co-occur with BOTH increased classical-simulability-under-noise AND increased trainability-loss concentration. This project's own data: TRAIN shows a genuine (if bandwidth-fragile) untrainability signature; HARD shows anticoncentration **increasing** as loss increases (the reverse of the original internal speculative guess). Under Herbst et al.'s framework this implies training should, if anything, get worse (not better) as loss increases — opposite the original speculative conclusion. TRAIN and HARD do not share a common independent variable (TRAIN sweeps n at eta=1; HARD sweeps eta at small fixed n), so this project cannot directly test the co-occurrence prediction with one combined experiment — stated as an explicit hedge, not resolved. — `docs/technical-findings.md:239-260`

### Milestone-level honesty statements (must carry into external framing per CONTEXT.md's "no softening" lock)

- No complexity-theoretic proof; no asymptotic-scale demonstration (all three studies run at small, compute-bound n); ARB-01/ARB-02's `CP(alpha)` gate and HARD-01..07's `heralded_cz` gate are two different weight-2 gate families, never cross-tested under loss together. — `docs/technical-findings.md:278-302`

## This Repo's README

**Full path:** `C:\Users\cuqui\merlin-quantum-case-study\README.md` (83 lines)

**Current structure (exact heading order):** Title → 1-line description → "How this was built" AI-disclosure line (links to `#process--ai-use`) → `## Headline result` → `## Problem & approach` → `## Results` (with 2 images + a v1.0 benchmark table) → `## How to run` → `## Links out` → `## Process & AI Use` → `## License`.

**Confirmed: this README is v1.0-only.** It was last substantively touched in commit `3961200` ("add README with results, visuals, AI disclosure") and copyedited in `b69507e`; it has never been updated for v2.0 (IQP → Photonic Encoding), v2.1 (Weight-2), or v3.0 (this milestone) — `git log --oneline -- README.md` shows no commits from Phase 14 onward touching this file. There is no existing "v2.0"/"v3.0" section to extend or collide with.

**What a v3.0 pitch section should NOT restate:**
- The v1.0 headline numbers already in `## Headline result` / `## Results` (held-out MMD² 0.0125±0.0003, ring_mass 0.68-0.69, etc.) — these are a different milestone's story.
- The existing `## Process & AI Use` framing/rule statement — the phrasing ("I verify every AI-assisted component against my own unaided explanation before it ships") is already established house style; a v3.0 section should either point back to this section or add one sentence extending it to v3.0, not re-derive the whole disclosure paragraph.
- Full methodology detail for TRAIN/HARD/ARB/Julia — CONTEXT.md's lock is explicit that README gets "a short v3.0 pitch section linking out... not a full restatement" of the case-study page.

**Where it fits:** the natural insertion point is a new top-level `## v3.0: ...` (or similarly named) section placed after `## Process & AI Use` and before `## License` — this keeps the existing v1.0 narrative (Headline result → Results → How to run → Links out → Process & AI Use) intact as a complete unit and adds the v3.0 pitch as a clearly separate, later addition, mirroring how the case-study page's own insertion point sits after the v1.0 body and before the (updated) Role/authorship section. Exact heading text and how much of TRAIN/HARD's headline tension to name in the README (vs. just "see the case study") is left to the plan/writer — CONTEXT.md doesn't lock README section wording.

## Build/Lint/Tooling Gotchas (alejandro-jackson repo)

- **No dedicated `typecheck` npm script.** `package.json` scripts are: `build` (`next build` — performs a full TypeScript typecheck as part of the Next.js build pipeline), `dev`, `lint` (`next lint`), `start`, `test:e2e`/`test:e2e:update` (Playwright). Recommended finish criteria for the executor: `npm run lint` clean, and `npm run build` clean (this is the closest thing to `tsc --noEmit` this repo has — it doubles as the typecheck gate). Running the full Playwright e2e suite is optional/likely unnecessary for a content-only page edit unless an existing e2e test snapshots this specific case-study page (not checked here — out of scope for research; flag for planner to grep `tests/` for `merlin-quantum` references if e2e coverage matters).
- `tsconfig.json` has `"strict": true` and `"noUncheckedIndexedAccess": true` — consistent with this project's own CLAUDE.md "TypeScript strict mode always" rule, no extra action needed, just don't disable it.
- Component imports use the `~/` path alias (`~/components/case-studies/shared`) — confirmed working in the existing file, no alias-resolution gotcha found.
- `DataTable`'s `rows: string[][]` prop means any new numeric data (e.g. TVD, alpha, R² values from the Sourceable Numbers section above) must be pre-formatted to strings before being passed in, matching the existing `tuningAxisData.map((d) => [d.axis, d.value.toFixed(3), d.detail])` pattern (line 382).

## Repo State (alejandro-jackson)

- **Git repo confirmed**, branch `main`, clean working tree apart from one pre-existing untracked file (`image.png` at repo root) unrelated to this phase — not something this phase's edit should touch or need to account for.
- Local `main` is 1 commit ahead of `origin/main` (an already-committed, unpushed change from a prior unrelated session — `40889a1`, "docs: add hiring-agent resume evaluation results"). This is pre-existing and not something Phase 21 caused; the planner/executor should be aware a `git push` here will also push that unrelated prior commit, and should mention that rather than being surprised by it.
- No stashes, no in-progress merge/rebase state detected.
- Most recent commits touching this exact file (`merlin-quantum.tsx`) are copyedit/correction passes (`6a87bc7`, `2d30208`, `fe2e9d6`, `3c51c60`) — confirms the file is actively maintained and copyedited carefully, consistent with the high bar for precision CONTEXT.md sets for this phase.

## Architecture Patterns (page-construction conventions to follow)

### Pattern: `Section` alternation for visual rhythm
The existing page alternates `dark`/non-`dark` roughly every other `Section` (Key Metrics: not dark, TL;DR: dark, Context: not dark, Methodology: dark, Key Finding: dark, Benchmarking: not dark, Technical Depth: dark, Role: not dark, What I'd Do Next: dark, Source Code: not dark). New v3.0 sections inserted between Technical Depth (dark) and Role (not dark) should pick `dark`/non-`dark` values that continue this alternation smoothly rather than breaking the visual rhythm (e.g., if inserting 2 sections, dark→not-dark keeps the sequence: Technical Depth[dark] → new-1[not dark] → new-2[dark] → Role[not dark] still alternates correctly? — actually Role is currently `not dark` following Technical Depth's `dark`; inserting an even number of sections preserves that adjacency, an odd number flips it. The plan should explicitly choose to keep this alternation correct, not leave it to accident).

### Pattern: "Key insight" callout after a chart
`RingMassProgressionChart` (lines 135-146) and the standalone insight box after the `DataTable` in the "Key Finding" section (lines 385-397) both use the same hand-rolled markup: `<div className="rounded-lg border border-blue-400/20 bg-blue-400/5 px-4 py-3">` wrapping a `<p>` that starts with `<span className="font-semibold text-blue-400">Key insight:</span>`. This exact pattern is what CONTEXT.md calls out as the model for framing the TRAIN-09 sigma-grid tension ("the barren-plateau signature looked real at one bandwidth, but a systematic sweep showed it wasn't robust") — reuse this literal markup pattern, not a new one.

### Anti-pattern to avoid
Do not create a 4th "TL;DR → Methodology → Key Finding → Technical Depth" repeated block per v3.0 sub-study — CONTEXT.md's lock is explicit that all four v3.0 tracks (TRAIN, HARD, ARB-01, Julia) share ONE narrative arc, with TRAIN/HARD as co-leads and ARB-01/Julia as supporting material woven in, not four independent mini-case-studies stacked back to back.

## Open Questions

1. **Exact number/count of new `Section` blocks for v3.0.**
   - What we know: CONTEXT.md locks "one shared narrative arc," leaves exact section headings/order and page length to Claude's discretion.
   - What's unclear: whether "one arc" means literally one `Section`, or a short run of 2-4 sections (e.g. Context → Key Finding[TRAIN+HARD headline tension] → Supporting Evidence[ARB-01+Julia]) that together read as one arc without being four repeated TL;DR blocks.
   - Recommendation: the planner should decide and state this explicitly as a task-level decision (per this project's "no silent unilateral design decisions" CLAUDE.md rule) rather than leaving it implicit in task actions.

2. **Whether to add a new custom chart component (mirroring `RingMassProgressionChart`) for the TRAIN-09 sigma-grid finding, or use `DataTable`/`CalloutBox` only.**
   - What we know: `RingMassProgressionChart`/`BenchmarkComparisonChart` are page-local, not shared, so a new one requires writing similar hand-rolled code in this file; `DataTable` and `MetricsGrid` are proven, already-imported, zero-new-code options.
   - What's unclear: whether the sigma-grid "signature disappears at intermediate bandwidth" story is visually compelling enough to warrant new chart code, given this phase's scope should stay tight (WRITE-07 only, no scope creep).
   - Recommendation: default to `DataTable` + a "Key insight" `CalloutBox` (matching the existing pattern) unless the plan has a specific reason a bar/line visualization adds real clarity beyond a table.

3. **Whether "What I'd Do Next" (currently v1.0-only) should be left untouched or given a v3.0-relevant addition.**
   - What we know: CONTEXT.md's locked scope doesn't mention this section; the phase's success criteria only require the new v3.0 content and the updated Role QuoteBlock.
   - What's unclear: whether leaving "What I'd Do Next" v1.0-only reads oddly once v3.0 content exists above it (its 7 bullets are generator-specific, e.g. BMK-03/GAN comparison — they don't map onto TRAIN/HARD/ARB future work at all).
   - Recommendation: treat as explicitly out of scope for this phase unless the plan states a deliberate reason to touch it — safer to leave as-is and let a future phase handle it than to silently expand scope here.

## Sources

### Primary (HIGH confidence — direct file reads)
- `C:\Users\cuqui\projects\alejandro-jackson\src\pages\case-studies\merlin-quantum.tsx` — full file read (524 lines)
- `C:\Users\cuqui\projects\alejandro-jackson\src\components\case-studies\shared.tsx` — full file read (628 lines)
- `C:\Users\cuqui\merlin-quantum-case-study\docs\technical-findings.md` — full file read (322 lines)
- `C:\Users\cuqui\merlin-quantum-case-study\README.md` — full file read (83 lines)
- `C:\Users\cuqui\merlin-quantum-case-study\docs\trainability-study.md`, `docs\hardness-under-loss-study.md`, `docs\julia-cross-check-study.md` — targeted grep + section reads for headline numbers/tables
- `C:\Users\cuqui\projects\alejandro-jackson\package.json`, `tsconfig.json` — full read
- `git status`, `git remote -v`, `git log` in both repos — direct command output

### Secondary / Tertiary
- None used — this phase's research surface was entirely local files and git state, no web research needed.

## Metadata

**Confidence breakdown:**
- Page structure / component API: HIGH — read directly from source, not inferred
- Sourceable numbers: HIGH — read directly from the Phase 20 synthesis doc plus underlying source docs; STATE.md confirms Phase 20's own numbers were independently code-reviewed and CSV-verified before this research ran
- README current-state / gap: HIGH — confirmed via full read plus git log showing no post-v1.0 touches
- Tooling/finish-criteria: HIGH — read directly from package.json/tsconfig.json
- Open questions (exact section count, chart-vs-table choice, What-I'd-Do-Next scope): explicitly flagged as planner decisions, not research gaps — CONTEXT.md itself defers these to Claude's discretion

**Research date:** 2026-08-19
**Valid until:** effectively indefinite for the structural/component-API findings (static files, no external dependency drift risk) — but re-verify if either repo receives unrelated commits before this phase executes, since both repos are actively being worked (alejandro-jackson has an unpushed local commit; this repo is mid-milestone).
