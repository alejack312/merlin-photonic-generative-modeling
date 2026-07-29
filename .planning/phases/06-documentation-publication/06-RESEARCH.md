# Phase 6: Documentation & Publication - Research

**Researched:** 2026-07-29
**Domain:** Repo packaging/publication (README + cleanup) in `merlin-quantum-case-study`, plus a cross-repo Next.js case-study page in `alejandro-jackson`
**Confidence:** HIGH (all findings verified directly against the filesystem, git, and gh CLI — no library/API uncertainty in this phase)

## Summary

This phase has almost no technology risk — it's packaging and writing, not new code. The research therefore focused entirely on ground-truth filesystem/git state so the planner can write concrete file paths and commands rather than placeholders. All three README visuals CONTEXT.md calls for already exist as PNG files from Phases 3-5; no new plotting code is needed for those. The one gap is a **benchmark comparison chart** — Phase 5 produced only a CSV (`results/phase5_benchmark_metrics.csv`) and a markdown table (`results/phase5_summary.md`), no PNG bar chart — so the planner should treat "benchmark comparison table/chart" as satisfiable by the existing markdown table alone, or scope a small new plotting task if a chart image is wanted (no existing script produces one).

The GitHub remote already exists (`alejack312/merlin-photonic-generative-modeling`, currently **private**, confirmed via `gh repo view --json visibility`) and the owner is authenticated via `gh` with `repo` scope — so "make public" is a single manual toggle, correctly deferred to the owner per CONTEXT.md. The repo has no README, no LICENSE, no `setup.py`/`pyproject.toml` (only `requirements.txt`); `pytest` (48 tests) passes cleanly in ~105s and is the cheapest "runnable code" smoke test. `.gitignore` already correctly excludes `venv/`, `__pycache__/`, `.pytest_cache/` — no large binaries are tracked (checkpoints are 3-7 KB each, `.git` is 2 MB total), so no gitignore fix is actually needed for DOC-02, just verification.

The portfolio repo (`C:\Users\cuqui\projects\alejandro-jackson`) is a **separate git repository** (`origin` = `alejack312/alejandro-jackson.git`, currently on `main`, clean except one unrelated untracked `image.png`) with its own Next.js 15 / npm toolchain. Adding the new case study means editing **three files** in that repo, not one, and the planner must scope this as its own distinct task/commit from `merlin-quantum-case-study`'s work.

**Primary recommendation:** Split Phase 6 into two clearly separated plan tracks — (1) this-repo packaging (README, LICENSE, docs/ move, cleanup, commit+push to existing `origin`) and (2) portfolio-repo case study (new TSX page + 2 edits to shared files, `npm run lint`/`npm run build` as the verification gate, its own commit in its own repo) — since they're different repos with different toolchains and different git histories.

## Repo State (merlin-quantum-case-study)

### Git / GitHub
| Item | Value |
|---|---|
| Branch | `master`, ahead of `origin/master` by 38 commits (not yet pushed) |
| Remote | `origin` → `https://github.com/alejack312/merlin-photonic-generative-modeling.git` |
| Visibility | **PRIVATE** (confirmed via `gh repo view alejack312/merlin-photonic-generative-modeling --json visibility` → `"PRIVATE"`) |
| `gh` auth | Logged in as `alejack312`, scopes include `repo` — capable of toggling visibility if ever needed, but CONTEXT.md reserves that action for the owner |
| Untracked files | `mmd-loss.md`, `raster-order.md` (both to move into `docs/` per CONTEXT.md) |

### Files at repo root (relevant to this phase)
- No `README.md` — must be created (DOC-01).
- No `LICENSE*` — must be created (CONTEXT.md: MIT suggested).
- No `setup.py` / `pyproject.toml` / `setup.cfg` — the project is not packaged as an installable module; `requirements.txt` (pinned, 45 lines, includes `merlinquantum==0.4.0`, `torch==2.12.1`, `perceval-quandela==1.2.4`) is the only install path. README's "how to run" section should say `pip install -r requirements.txt` (there is no `pip install -e .` to document — don't invent one).
- `quickstart.py` — MerLin's own example script (classifier on `make_circles`, not this project's generator); exists but is not the project's actual deliverable. Don't confuse this with the generator entry point.
- Actual generator entry points: `train.py` (root-level basic training script), `generator/train.py` (module), `natural_order_train.py` (the GEN-07 "best" variant), `benchmark.py`, `benchmark_timing.py`, `sweep.py`, `batch_sweep.py`, `visualize.py` — these are the real runnable artifacts DOC-02 needs to point to, not `quickstart.py`.
- `pytest.ini` → `testpaths = tests`. `python -m pytest -q` **passes 48/48 in ~105s** (verified live this session) — this is the cheap, ready-made "runnable code" smoke test for DOC-02; no new test infrastructure needed.
- `.gitignore` (7 lines): `venv/`, `__pycache__/`, `*.pyc`, `.pytest_cache/`, `*.egg-info/`, `.ipynb_checkpoints/`. Already sufficient — checkpoint files (`results/*.pt`) are small (3-7 KB each, all already tracked in git) and don't need excluding. `.git` directory is only 2 MB total. **No gitignore fix is required**, only a verification line in the plan/README that this was checked.
- `DESIGN_DECISIONS.md` (24.5 KB) and `NOTES.md` (4.9 KB) already exist and are exactly the "explain unaided" evidence CONTEXT.md wants linked from the README, not duplicated into it.

### Results / visuals inventory (`results/`)
All three README visuals CONTEXT.md specifies **already exist** as committed PNGs — no new plotting work is required for the base README:

| CONTEXT.md visual | File | Status |
|---|---|---|
| Generated-vs-real scatter/heatmap (Phase 4) | `results/phase4_scatter_comparison.png`, `results/phase4_heatmap_comparison.png`, `results/phase4_natural_comparison.png` | Exists (3 candidate variants — planner/owner picks which is most representative; `phase4_natural_comparison.png` is likely the best "final" one since it's the GEN-07 checkpoint result) |
| Training loss curve (Phase 3) | `results/phase3_loss_curve.png` | Exists |
| Benchmark comparison (Phase 5: trained/untrained/floor MMD²) | **No PNG exists.** Only `results/phase5_benchmark_metrics.csv` (raw numbers) and the markdown table already in `results/phase5_summary.md` | **Gap** — see below |

Other existing Phase 4 visuals not explicitly required but available if useful: `phase4_sweep_comparison.png`, `phase4_batch_sweep_comparison.png`, `phase4_natural_rank_profile.png`.

**Benchmark comparison gap:** CONTEXT.md says "table/chart" (either satisfies it). The markdown table already exists verbatim in `results/phase5_summary.md` ("Headline numbers" table) and can be copied into the README directly — zero new work. If the owner wants an actual bar chart image instead of/in addition to the table, that requires a small new script (no `benchmark.py`/`benchmark_timing.py` code currently calls `plt.savefig` — confirmed via grep, no matches) reading `results/phase5_benchmark_metrics.csv`. **Recommend the planner default to the table (already exists, zero-risk) and treat a PNG chart as optional/discretionary**, not a blocking requirement — CONTEXT.md's own case-study track separately wants an *interactive* animated bar comparison in the TSX page, which is a better home for a bar-chart-style visual anyway.

### Phase evidence files (for README's "links out" targets)
- `results/phase4_summary.md`, `results/phase5_summary.md` — both citation-ready per STATE.md.
- `.planning/phases/04-generative-quality/04-03-SUMMARY.md` — contains the exact verbatim GEN-07 "not met" owner quote and mechanism explanation.
- `.planning/phases/05-benchmarking/05-01-SUMMARY.md`.
- `DESIGN_DECISIONS.md` — three 2026-07-25 entries cover the natural-order-correspondence mechanism (referenced by `raster-order.md`).
- `mmd-loss.md` (root, untracked) — compares this project's MMD implementation against the sibling `iqp-mmd-barren-plateau` project's approach. Move to `docs/mmd-loss.md`.
- `raster-order.md` (root, untracked) — explains why radius-sorted bin ordering fixes ring fragmentation. Move to `docs/raster-order.md`.

## Portfolio Repo (alejandro-jackson) — Component API & Conventions

### Repo facts
- Location: `C:\Users\cuqui\projects\alejandro-jackson` — **separate git repo**, `origin` = `https://github.com/alejack312/alejandro-jackson.git`, branch `main`, currently clean except one unrelated untracked `image.png` (not part of this phase's scope — leave it alone, don't clean up files outside phase scope).
- Stack: Next.js 15.5 (Pages Router — file-based routing under `src/pages/case-studies/`), React 19, TypeScript, Tailwind 3.3, `motion` (the renamed `framer-motion` package, imported as `"motion/react"` — **note:** `iqp-mmd.tsx` imports from `"framer-motion"` directly, which still works since `motion` is a compatible re-export/successor package already in `package.json` dependencies; new pages should match `shared.tsx`'s own import (`"motion/react"`) for consistency, though either import path is currently functional in this repo).
- Package manager: npm (`"packageManager": "npm@9.7.2"`).
- `package.json` scripts: `dev`, `build` (`next build`), `lint` (`next lint`), `start`, `test:e2e` (Playwright), `test:e2e:update`. **No unit test script.** `npm run build` and `npm run lint` are the correct cheap verification gate for a new page — confirms the TSX compiles/type-checks and passes ESLint without needing to stand up the dev server. Playwright e2e tests exist but are not required for a static content page addition (out of scope unless the owner wants visual regression coverage — not requested in CONTEXT.md).

### Files that must be touched for the new case study (3 files, not 1)
1. **New file**: `src/pages/case-studies/<slug>.tsx` (slug TBD — CONTEXT.md leaves this to discretion, e.g. `merlin-quantum.tsx`). This is the main page, following `iqp-mmd.tsx`'s exact structure.
2. **`src/components/case-studies/shared.tsx`**: the `allStudies` array (used by `CrossLinks`, lines ~448-479) must get a new entry `{ slug, title, accent, keywords }` or the new page won't appear in *other* pages' cross-links, and existing pages won't link to it either. This is easy to miss since it's a shared file, not the new page.
3. **`src/pages/case-studies/index.tsx`**: the `caseStudies` array (lines ~11-79) must get a new entry (`title`, `slug`, `accent`, `keywords`, `description`, `metrics`) or the new case study won't appear on the case-studies landing page at all — this is the actual discovery surface for a portfolio visitor, and CONTEXT.md's "CrossLinks registration so it's discoverable" implies both this and #2.

Note: `index.tsx`'s header text currently says "Five engineering case studies" (hardcoded count) — adding a sixth study means this copy also needs a one-word edit (`Five` → `Six`) or it becomes a small but real inconsistency. Flag for the planner as a one-line discretionary fix, not a separate task.

### Component API reference (from `shared.tsx`, verified by reading full file)

- **`AccentColor`** = `"cyan" | "amber" | "violet" | "emerald" | "sky" | "blue"`. CONTEXT.md wants a new accent distinct from `iqp-mmd.tsx`'s `"sky"` — `"violet"` is used by `dalas.tsx` already (per `allStudies`), `"amber"` by `parallel-programming-mitm.tsx`, `"cyan"` by `quantum-simulator.tsx`, `"emerald"` by `quantum-algorithms.tsx`. Every accent in the 5-color case-study palette is already claimed by an existing case study except `"blue"` (currently reserved for the separate `allSweStudies`/SWE case-studies group, not used in the quantum-project `allStudies` group at all). **Emerald and violet are both already taken; CONTEXT.md's own suggestion list ("violet or emerald") conflicts with actual current usage** — planner/owner should pick `"blue"` instead (unused in the `allStudies` group) or accept a duplicate-with-`dalas`/`quantum-algorithms` accent color. This is a real discretionary decision to surface, not silently resolve.
- **`CaseStudyHero`** props: `accent: AccentColor`, `label: string`, `title: string`, `subtitle: string`, `badges: string[]`, optional `children`.
- **`Section`** props: `accent`, optional `label`, `title: string` (required), `children` (required), optional `dark?: boolean` (alternates background tint — `iqp-mmd.tsx` alternates dark/non-dark roughly every other section).
- **`MetricsGrid`** props: `accent`, `metrics: { label: string; value: string; detail: string }[]` — renders via `MetricCard`, typically 4 entries for the hero "at a glance" grid.
- **`CalloutBox`** props: `accent`, optional `title`, `children` — used for the TL;DR summary block.
- **`DataTable`** props: `accent`, `headers: string[]`, `rows: string[][]` (all cells are strings — pre-format numbers before passing).
- **`ProcessStep`** props: `accent`, `number: string` (e.g. `"01"`), `title: string`, `children` — used in numbered sequence for the methodology section; renders a connecting vertical line between steps automatically.
- **`QuoteBlock`** props: `accent`, `children`, optional `attribution` — used for the "Role" section.
- **`CrossLinks`** props: `{ current: string }` — `current` must exactly match the new entry's `slug` string added to `allStudies` in `shared.tsx`, or the self-exclusion filter (`s.slug !== current`) won't work and the new page will link to itself.
- **`AnimatedBar`** exists in `shared.tsx` (props: `label`, `value`, `maxValue`, `accent`, optional `suffix`, `index`) but is unused in `iqp-mmd.tsx` — `iqp-mmd.tsx` instead builds fully custom bespoke chart components (`ACGapChart`, `BandwidthSweepViz`) using raw `motion.div` width animations keyed off `useInView`. CONTEXT.md's "2-3 bespoke animated components in the iqp-mmd.tsx style" means: **write custom local components in the new page file** (not just reuse `AnimatedBar`), following the `useRef` + `useInView({ once: true, margin: "-40px" })` + staggered `transition={{ delay: i * 0.1 }}` pattern demonstrated in `ACGapChart`/`BandwidthSweepViz`. `AnimatedBar` alone is a reasonable building block for a simpler "trained vs untrained vs floor MMD²" 3-bar comparison but the ring_mass-improvement-across-three-axes visual likely needs a custom component similar to `ACGapChart`.
- **`CaseStudyLayout`**: no props besides `children`, just wraps in `<main className="relative min-h-screen overflow-hidden bg-black">`.

### Source-code link convention
`iqp-mmd.tsx`'s final "Source Code" section links to `https://github.com/alejack312/iqp-mmd-barren-plateau` — the new page's equivalent link should point to `https://github.com/alejack312/merlin-photonic-generative-modeling` (this project's actual GitHub remote, confirmed above), which only works once the owner has flipped it to public — the planner should note this creates a soft cross-dependency (case-study page references a URL that returns 404/private until the owner completes the manual visibility toggle) but should not block writing/shipping the TSX page itself.

## Cross-Repo Plan Mechanics

- The two repos (`merlin-quantum-case-study` and `alejandro-jackson`) have **independent git histories, remotes, and toolchains** (Python/pytest vs. npm/Next.js). A single gsd-executor task should never span both repos' commits — treat them as two separate tasks/plans with their own commit boundaries, matching Gate 7's "no scope smuggling" and Gate 8's per-repo deploy discipline.
- Any PLAN.md task that touches `alejandro-jackson` must give the **absolute path** (`C:\Users\cuqui\projects\alejandro-jackson\...`), not a path relative to `merlin-quantum-case-study`'s cwd — the executor's default working directory is the GSD project repo, and Bash commands need explicit `cd "C:\Users\cuqui\projects\alejandro-jackson"` (or equivalent absolute-path invocation) to run `npm run build`/`npm run lint`/git commands there.
- Verification gate for the portfolio-repo task should be `npm run lint` and `npm run build` (both exist as scripts, both are fast, both catch TS/ESLint errors in the new TSX before commit) — there is no `tsc --noEmit` script defined separately, but `next build` performs type-checking as part of its build step, satisfying the "type-check clean" quality gate from CLAUDE.md's global rules.
- Because this is a second git repo, it needs **its own commit** (and, if the owner wants it live immediately, its own push — confirm with owner whether pushing/deploying the portfolio site is in scope for this phase or a separate manual step; CONTEXT.md doesn't explicitly address portfolio-repo push/deploy, only that the case study gets built).
- Risk to flag explicitly in the plan: editing `shared.tsx`'s `allStudies` array is a shared file used by every existing case study's `CrossLinks` — a mistake there (e.g. bad accent key, duplicate slug) could visually break cross-links on all 5 existing pages, not just the new one. This is exactly the "blast radius" check from Gate 2 (architecture) — call it out as a specific verification step (visually or via `npm run build` catching a TS error if the `AccentColor` type is misused).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Benchmark comparison visual for README | New matplotlib script for a PNG bar chart | The existing markdown table in `results/phase5_summary.md` (copy-paste) | Already exists, zero risk, satisfies CONTEXT.md's "table/chart" wording without new code in a phase explicitly scoped to "no new generator/benchmark code" |
| Case-study bar/comparison visuals | Static `<img>` drop-ins | `shared.tsx`'s `AnimatedBar` / a custom component following `ACGapChart`'s pattern | CONTEXT.md explicitly requires interactive animated components in the `iqp-mmd.tsx` style, not static images — matches the existing repo convention exactly |
| Portfolio page routing/registration | A custom nav or manual link | Editing `allStudies` in `shared.tsx` + `caseStudies` in `index.tsx` | This is the actual, only mechanism this codebase uses for making a case study discoverable — confirmed by reading both files in full |

## Common Pitfalls

### Pitfall 1: Treating `quickstart.py` as the project's deliverable
**What goes wrong:** README's "how to run this" section points readers to `quickstart.py`, which is MerLin's own generic classifier example (unrelated to this project's generator), not this project's actual code.
**Why it happens:** It's the most prominent/simplest script at repo root and superficially looks like an entry point.
**How to avoid:** README's runnable-code pointer should reference `train.py` / `generator/train.py` / `natural_order_train.py` (the actual generator) and `pytest` (the actual verifiable smoke test), not `quickstart.py`.
**Warning signs:** README describes running `quickstart.py` and calling that "the project."

### Pitfall 2: Missing the `allStudies`/`index.tsx` registration when adding the case study
**What goes wrong:** New TSX page is written and even accessible by direct URL, but never appears on the case-studies index page or in any other page's `CrossLinks`, quietly failing the "discoverable" part of CONTEXT.md's DOC-04 success criterion.
**Why it happens:** `shared.tsx` and `index.tsx` are separate files from the new page, easy to forget since the new page itself looks complete on its own.
**How to avoid:** Treat "add case study" as a 3-file change from the start (new page + `shared.tsx` `allStudies` entry + `index.tsx` `caseStudies` entry), per the file list above.
**Warning signs:** `npm run build` succeeds but manually checking `/case-studies` (index) doesn't show the new card.

### Pitfall 3: Accent color collision
**What goes wrong:** CONTEXT.md suggests "violet or emerald," but both are already used by other case studies in the same `allStudies` group (`dalas` = violet, `quantum-algorithms` = emerald) — picking either creates two case studies with identical accent colors, undermining CONTEXT.md's own stated goal ("read as visually separate").
**How to avoid:** Use `"blue"` (confirmed unused in the `allStudies` group — only used in the separate `allSweStudies` group) or explicitly flag the collision to the owner as a discretion call before implementing.
**Warning signs:** Two cards on `/case-studies` render with the same colored accent line/badges.

### Pitfall 4: Committing across two repos as one logical change
**What goes wrong:** A plan/task tries to "commit the phase" as a single atomic unit, but the work spans two independent git repositories with separate histories — this either fails mechanically (can't commit files outside the repo root) or silently only commits one repo's half of the work.
**How to avoid:** Two separate commits, two separate tasks, explicit repo-path context in each.
**Warning signs:** A PLAN.md task lists file paths from both `merlin-quantum-case-study` and `alejandro-jackson` under one `git add`/`git commit` step.

## Code Examples

### Confirming GitHub repo visibility (read-only, already run this session)
```bash
gh repo view alejack312/merlin-photonic-generative-modeling --json visibility,url,description
# → {"description":"","url":"https://github.com/alejack312/merlin-photonic-generative-modeling","visibility":"PRIVATE"}
```

### Smoke-testing "runnable code" for DOC-02
```bash
python -m pytest -q
# → 48 passed in 105.03s (confirmed this session)
```

### `CrossLinks` self-exclusion pattern (from `shared.tsx`, verbatim)
```typescript
// Source: C:\Users\cuqui\projects\alejandro-jackson\src\components\case-studies\shared.tsx
export function CrossLinks({ current }: { current: string }) {
  const others = allStudies.filter((s) => s.slug !== current);
  // ...
}
```
The new page's own `<CrossLinks current="..." />` call must pass the exact same slug string used in the new `allStudies` entry.

## Open Questions

1. **Final case-study slug/filename**
   - What we know: CONTEXT.md leaves this to discretion; existing slugs are short kebab-case project names (`iqp-mmd`, `quantum-algorithms`, `dalas`).
   - What's unclear: exact final string.
   - Recommendation: something like `merlin-quantum` or `merlin-photonic` — planner/owner picks at plan time, must match consistently across the new file name, `allStudies` entry, `index.tsx` entry, and `<CrossLinks current="...">`.

2. **Accent color final pick**
   - What we know: `"violet"` and `"emerald"` (CONTEXT.md's suggestions) are both already in use elsewhere in `allStudies`.
   - What's unclear: whether the owner is fine with a duplicate accent, or wants `"blue"` instead.
   - Recommendation: default to `"blue"` (only unused option in the group) and flag the substitution explicitly in the plan.

3. **Whether `alejandro-jackson` gets pushed/deployed as part of this phase**
   - What we know: CONTEXT.md scopes "build the full TSX page" but doesn't explicitly mention pushing/deploying the portfolio site.
   - What's unclear: whether Phase 6's finish criteria require the case study to be live at a public URL, or just committed locally/pushed to `origin` on `main`.
   - Recommendation: plan for at minimum a commit + push to `alejandro-jackson`'s existing `origin/main` (mirrors this project's own repo's expected end-state), treat actual production deploy (if the site auto-deploys via Vercel on push, likely, but unconfirmed) as a side effect, not a separate task to build — but flag it as a checkpoint for the owner to confirm the live page looks right, since visual/interactive TSX output can't be fully verified by `npm run build` alone (Gate 4 — UI shipping requires an actual look, not just a passing build).

4. **Which of the three existing Phase 4 comparison PNGs is "the" README scatter/heatmap visual**
   - What we know: three candidates exist (`phase4_scatter_comparison.png`, `phase4_heatmap_comparison.png`, `phase4_natural_comparison.png`).
   - What's unclear: which best represents the final GEN-07 state referenced by CONTEXT.md's "headline honesty" framing.
   - Recommendation: `phase4_natural_comparison.png` is most likely correct since it corresponds to the natural-order-correspondence checkpoint (ring_mass=0.691) that Phase 4/5 both treat as the final/best result — but the owner should confirm at plan or execute time since this is a visual/judgment call, not a mechanical one.

## Sources

### Primary (HIGH confidence — direct filesystem/git/gh inspection this session)
- `git status`, `git remote -v`, `git log --oneline` in `merlin-quantum-case-study`
- `gh repo view alejack312/merlin-photonic-generative-modeling --json visibility,url,description`
- `gh auth status`
- Full read of `C:\Users\cuqui\projects\alejandro-jackson\src\pages\case-studies\iqp-mmd.tsx`
- Full read of `C:\Users\cuqui\projects\alejandro-jackson\src\components\case-studies\shared.tsx`
- Full read of `C:\Users\cuqui\projects\alejandro-jackson\src\pages\case-studies\index.tsx`
- `C:\Users\cuqui\projects\alejandro-jackson\package.json`
- Live `python -m pytest -q` run (48 passed)
- `find`/`ls` inventory of `results/`, `tests/`, `generator/`, repo root
- `.planning/phases/04-generative-quality/04-03-SUMMARY.md`, `results/phase5_summary.md` (read in full)
- `.gitignore`, `requirements.txt`, `pytest.ini`, `NOTES.md`, `quickstart.py` (read in full)

No WebSearch/Context7 sources were needed — this phase's research question was entirely "what already exists in these two specific repos," not a library/API/ecosystem question.

## Metadata

**Confidence breakdown:**
- Repo state (files, git, GitHub visibility): HIGH — verified directly, not inferred
- Portfolio repo component API: HIGH — read both relevant files in full, not summarized from memory
- Cross-repo mechanics / gsd-executor behavior: MEDIUM — reasoned from CLAUDE.md's global GSD conventions and the two repos' actual independence, not verified against gsd-executor's source code (out of scope for this research)
- Accent color collision finding: HIGH — directly cross-referenced `shared.tsx`'s `allStudies` array

**Research date:** 2026-07-29
**Valid until:** Effectively indefinite for the filesystem/git facts (this is a snapshot of static project state, not a fast-moving library ecosystem) — but re-verify git/GitHub state (branch ahead-count, visibility) immediately before executing, since local commits accumulate between research and execution.
