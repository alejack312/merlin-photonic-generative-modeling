# Project State

## Project Reference

See: .planning/PROJECT.md (updated 2026-07-19)

**Core value:** A working, end-to-end, honestly-benchmarked MMD-trained photonic generative model, published in a public repo before Sept 1, 2026 — explainable unaided to Vincent Espitalier.
**Current focus:** Phase 6 — Documentation & Publication COMPLETE (2/2 plans). This was the final phase in the roadmap. Phase 5 (Benchmarking) VERIFIED COMPLETE 2026-07-29 (6/6 must-haves, gsd-verifier).

## Current Position

Phase: 6 of 6 (Documentation & Publication) — COMPLETE (2 of 2 plans)
Phase 4 (Generative Quality) is CLOSED. All 3 formal plans done (04-01, 04-02, 04-03) plus 2 ad hoc tuning axes (batch-size sweep, "option 3" natural-order correspondence). Final checkpoint (04-03) taken 2026-07-25: owner's verbatim response — **"GEN-07 not met, move to Phase 5."** `results/phase4_summary.md` and `.planning/phases/04-generative-quality/04-03-SUMMARY.md` record the full evidence and verdict.
Phase 5 (Benchmarking) CLOSED 2026-07-29 (6/6 must-haves, gsd-verifier). `results/phase5_summary.md` citation-ready. Full detail: `.planning/phases/05-benchmarking/05-01-SUMMARY.md`.
Phase 6 Plan 06-01 (this-repo packaging) executed end-to-end and complete. `README.md` states GEN-07's "not met" result plainly near the top with the real Phase 5 numbers (held-out MMD²=0.0125±0.0003 trained vs 0.0360±0.0048 untrained vs 0.0114 floor; ring_mass=0.6833±0.0073; gap_mass=0.0514±0.0035; improvement path 0.609→0.691), embeds `results/phase3_loss_curve.png` and `results/phase4_natural_comparison.png`, and links to `DESIGN_DECISIONS.md`, `docs/mmd-loss.md`, `docs/raster-order.md`, and both phase summary files. Two AI-disclosure sections (top one-liner + bottom "Process & AI Use") use the ownership-forward framing from memory `phase6-ai-disclosure-framing`. `mmd-loss.md`/`raster-order.md` moved from untracked repo-root scratch files into `docs/`, now tracked. MIT `LICENSE` added. Full pytest suite (48/48) re-verified passing as DOC-02's runnable-code check. Technical note for Vincent Espitalier drafted (4 sentences, LinkedIn-style, one honest GEN-07 clause, no CTA) at `.planning/phases/06-documentation-publication/06-technical-note.md`. All work committed atomically and pushed to `origin/master`; repo visibility confirmed still PRIVATE via `gh repo view` (owner's manual toggle, not touched by this plan).
Phase 6 Plan 06-02 (portfolio case study, DOC-04, cross-repo work in the separate `alejandro-jackson` repo) executed end-to-end and complete. Built `src/pages/case-studies/merlin-quantum.tsx` (497 lines) following `iqp-mmd.tsx`'s full structural depth (hero through cross-links), with two bespoke animated components (`RingMassProgressionChart`, `BenchmarkComparisonChart`) and a "Key Finding" section stating the GEN-07 shortfall plainly ("Good MMD² ≠ Clean Ring Structure"). `ACCENT="blue"` used since violet/emerald (CONTEXT.md's original suggestions) were both already claimed in `allStudies`. Registered in `shared.tsx`'s `allStudies` and `index.tsx`'s `caseStudies` (header copy "Five"→"Six"). `npm run lint`/`npm run build` both verified clean on an isolated run (build flakiness during verification traced to host disk-space exhaustion + concurrent-build contention, not code — resolved, not a code defect). Owner reviewed the live page at the blocking checkpoint and approved. After approval, the orchestrator handled a small scoped follow-up directly (not part of this plan's own tasks): reordered `/case-studies` to show most-recent-first, committed as `3c51c60`. All work pushed to `alejandro-jackson`'s own `origin/main` (`b08298a..3c51c60`), a separate git history from this repo.
Last activity: 2026-07-29 — Plan 06-02 executed and Phase 6 (final phase) closed. Task commits in `alejandro-jackson`: `7fea4f1` (TSX page), `983f108` (registration), `3c51c60` (orchestrator reorder follow-up).

Progress: [██████████] 100% (all 6 phases concluded; Phase 4's conclusion was "not successful" — GEN-07 not met, honestly documented and carried forward through Phases 5-6; Phase 6 complete, 2/2 plans done)

## Performance Metrics

**Velocity:**
- Total plans completed: 0 (Phase 1 predates plan-based tracking)
- Average duration: -
- Total execution time: -

**By Phase:**

| Phase | Plans | Total | Avg/Plan |
|-------|-------|-------|----------|
| 1. Environment & Architecture Foundation | - | - | - |

**Recent Trend:**
- Last 5 plans: -
- Trend: -

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Phase 1: Extend quickstart classifier into an MMD generator (not reproduce a catalog paper directly) — reuses owner's MMD/generative-modeling background, gives a natural comparison point.
- Phase 1: Generator output = full-distribution/histogram matching via closed-form MMD² — avoids collapsing the circles' two-ring target into its empty middle, avoids non-differentiable discrete sampling.
- Phase 1: Python 3.12 venv used instead of system default 3.13 — required by MerLin's `torch<2.13` + `python<=3.12` constraints.
- Phase 2 (02-02): Tensor-value pytest assertions use `torch.allclose`/`torch.equal`, never `pytest.approx` — `pytest.approx` without `==` doesn't compare anything, and its internal handling breaks on tensors with `requires_grad=True` (which any `QuantumLayer` output has). Full detail: `~/.claude/learnings/2026-07-19-pytest-approx-misuse-grad-tensor.md`.
- Phase 2 (02-04): `generator/mmd.py`'s `mmd2`/`gaussian_kernel_matrix` must be pure `torch` (`cdist`/`exp`/`@`), never `numpy` — `q` comes from a trainable `QuantumLayer` forward pass, and any numpy operation on it severs PyTorch's autograd graph, silently producing a loss that looks fine (finite, non-negative) but never actually trains the circuit.
- Phase 2 (02-04): `torch.cdist(x, x)` is not bit-exact symmetric and its diagonal is not bit-exact 0 (float32 cancellation in its internal distance formula) — both get amplified by a Gaussian kernel's `/(2σ²)` at small σ. Measured: ~1e-6 symmetry / ~5e-4 diagonal noise from cdist itself, ~1e-5 / ~3e-4 after the kernel at σ=0.02. Use `atol=1e-4`/`1e-3` on symmetry/diagonal checks over such a kernel, not `torch.allclose` defaults.
- Phase 3 (03-01): Batch-reduction strategy (average per-sample MMD² losses across a batch of fresh `z`, one shared θ, DESIGN_DECISIONS.md 2026-07-24) is now empirically validated, not just literature-motivated — real run produced a statistically clean decreasing trend (p≈1e-128) at the first-attempt lr=0.01, no LR escalation needed.
- Phase 3 (03-01): lr=0.01 (quickstart.py-informed default) was sufficient on the first real run — the planned lr=0.05/0.1 escalation path for a possible flat first attempt was not exercised.
- Phase 4 (04-01): Checkpoint decision — sigma=0.1's generated distribution is not ring-like enough (diffuse scatter/heatmap, ring_mass=0.602/0.572 exact/sampled, gap_mass=0.034/0.030); owner selected **sweep-needed**, so Plan 04-02's full SIGMA_GRID sweep (~12 min, all 5 sigma values, fixed epochs/lr/batch_size) is required before Plan 04-03's final GEN-07 checkpoint.
- Phase 4 (04-02): Full sweep completed — none of the 5 SIGMA_GRID values produced a visually ring-like generated distribution (all diffuse across the square); sigma=0.1 has the highest ring_mass (0.616) but is still not clean. Plan 04-03's final GEN-07 checkpoint must weigh this combined evidence, not just one sigma.
- Phase 4 (04-02): Backgrounded ~12-14 min training scripts did not reliably survive across tool-call turns in this execution environment (process was silently killed mid-sweep with no captured error). `sweep.py` was made resumable (skip retraining a sigma whose checkpoint already exists) as the general-purpose fix — worth reusing this pattern for any future long-running script in this repo rather than relying on a single uninterrupted backgrounded run.
- Phase 4 (ad hoc, 2026-07-25): Batch-size sweep at sigma=0.1 (batch ∈ {16,32,64,128}) does not fix ring structure either — batch=32 stays best (owner visually confirmed none of the 4 look meaningfully closer to two rings). Batch size ruled out as the lever.
- Phase 4 (ad hoc, 2026-07-25): `QuantumLayer.simple`'s `ModGrouping` post-processing (462 natural width → 400 via index-modulo-400 sum, unrelated to spatial bin adjacency) means increasing `input_size` past 10 makes the fold strictly worse, not better — `input_size=10` (current) is already the least-folded option covering all 400 bins. Naively "increasing circuit size" via `input_size` was flagged to the owner as counterproductive before implementing it. See DESIGN_DECISIONS.md 2026-07-25 entry (first of two).
- Phase 4 (ad hoc, 2026-07-25): Deeper root cause found — `output_keys`' raw ordering (photon-occupation combinatorics) has no designed relationship to bin_centers.py's spatial ordering, so even unfolded bins get an arbitrary spatial label. Researched CircuitBuilder (option 2) vs. custom output mapping via `OutputAdapter`/`output_keys`/`output_size=None` (option 3) directly against MerLin's docs/source. Owner chose option 3: K=462 (no fold) + radius-sorted centers paired by rank with center-of-mass-sorted Fock states. Plan approved (`C:\Users\cuqui\.claude\plans\plan-option-3-dynamic-bunny.md`) and implemented. See DESIGN_DECISIONS.md 2026-07-25 entry (second of three).
- Phase 4 (ad hoc, 2026-07-25): Option 3 result — ring_mass 0.609 → 0.691, owner-confirmed "an improvement, still not two distinct rings." The measurable reason: sorting bins by radius turns the ring target from 44 disjoint fragments into ~6 contiguous bands in the 1-D vector the model actually outputs, so a smooth output has far less high-frequency structure to fight. Verified this collapse is caused by the ordering, not the fold removal (44→7 on the old 400-bin grid too). The residual gap is attributed to `fock_state_sort_order`'s center-of-mass smoothness heuristic being weak — rank-domain corr(p_real, q) = 0.38. See DESIGN_DECISIONS.md 2026-07-25 entry (third of three).
- Phase 4 (04-03, final checkpoint, 2026-07-25): **GEN-07 not met.** Owner's verbatim response: "GEN-07 not met, move to Phase 5." Reached after the owner independently re-derived the radius-sorting mechanism via a Feynman-technique explanation, and after checking whether MMD loss itself was the culprit by running MerLin's quickstart classifier directly — found it to be a weak baseline itself (46-64% test accuracy across repeated runs on an easily-separable dataset), so the shortfall is attributed mainly to task structure (unsupervised full-distribution generation from coordinate-free noise vs. supervised low-information discrimination fed real coordinates), not primarily to the loss function. Phase 4 closed; Phase 5 (Benchmarking) begins carrying this not-met result forward honestly.
- Phase 5 (05-01, 2026-07-29): BMK-01 held-out MMD² benchmarking uses `load_circles_data()`'s existing fixed `random_state=42` split unchanged (X_test never in p_real at training time) rather than varying splits across seeds — the only intended source of run-to-run variance is the latent `z`, matched by N_DRAWS=20 mirroring Phase 4's stability check convention. SIGMA=0.1 kept identical to training bandwidth for direct comparability with Phase 4 numbers, not re-tuned for benchmarking.
- Phase 5 (05-01, 2026-07-29): BMK-02 used the pre-confirmed qualitative fallback path (05-RESEARCH.md established before execution that MerLin's photonic QGAN reproduction trains on a different data domain, 8x8 digit images vs. this project's 2D circles, with no defined mapping onto the K=462 MMD metric without new BMK-03-scoped work) — explicitly flagged in `results/phase5_summary.md`, not silently substituted for a matched number.
- Phase 5 (05-01, 2026-07-29): `benchmark_timing.py` writes its fresh timed retrain to a scratch checkpoint path (`results/phase5_timed_checkpoint.pt`), never overwriting `results/phase4_natural_checkpoint.pt`, to get a real measured wall-clock number (425.93s, 220 params) without corrupting the Phase 4 reference artifact.
- Phase 6 (06-01, 2026-07-29): README's headline benchmark table uses Phase 5's re-measured ring_mass/gap_mass (0.6833±0.0073 / 0.0514±0.0035) rather than Phase 4's original run (0.691/0.048) as the primary cited figures, since Phase 5 is the more recent independent re-measurement of the same checkpoint — both numbers (and the 0.609→0.691 improvement path) appear in the README so neither reading is hidden.
- Phase 6 (06-01, 2026-07-29): Public-facing prose (README, technical note) passed through a humanizer self-review pass (em dashes, inflated framing, negative parallelisms) per this execution's explicit `/humanizer` flag before commit; internal docs (DESIGN_DECISIONS.md, SUMMARY.md files, NOTES.md) were left untouched/candid, consistent with memory `phase6-ai-disclosure-framing`'s "don't scrub internal artifacts" guidance.
- Phase 6 (06-02, 2026-07-29): Portfolio case-study page (`alejandro-jackson` repo) uses `ACCENT="blue"` instead of CONTEXT.md's original violet/emerald suggestions, both already claimed by `dalas`/`quantum-algorithms` in `shared.tsx`'s `allStudies` array — locked in the plan itself (06-RESEARCH.md Pitfall 3), not re-litigated during execution.
- Phase 6 (06-02, 2026-07-29): The case-study's hero metrics and ring_mass tuning-axis chart cite Phase 4's original per-axis numbers (0.616 → 0.609-0.618 → 0.691), while the Key Finding narrative separately cites Phase 5's independent re-measurement (ring_mass ≈ 0.68-0.69) — mirrors 06-01's README precedent of citing both consistent measurements rather than picking the more favorable one.
- Phase 6 (06-02, 2026-07-29): Build/lint verification during execution hit false-alarm failures from concurrent background `npm run build` processes racing on `alejandro-jackson`'s shared `.next/` output directory, ultimately traced to the host C: drive being at 100% capacity. Not a code defect — resolved by freeing disk space and running one isolated build. Worth remembering for any future cross-repo Next.js verification in this environment: don't stack multiple background builds against the same `.next/` directory.

### Pending Todos

None yet.

### Blockers/Concerns

- **Stall-risk checkpoint RESOLVED**: July 25, 2026 was the explicit deadline for Phase 3 (End-to-End Training Run) — a historical stall pattern (prior PennyLane track stalled since May 2026). A real, working end-to-end training run with checked-in evidence (results/phase3_*) was completed 2026-07-24, one day ahead of the deadline. GEN-06 met.
- **Note for Phase 4**: the self-explanation checkpoint for train_step's mechanism required one correction (owner's first attempt conflated this project's continuous latent-noise MMD with a prior project's binary-bitstring MMD kernel) before the owner could explain it correctly. Worth double-checking this distinction stays clear going into Phase 4's evaluation work, which will build directly on the same MMD machinery.
- **Phase 4 CLOSED, GEN-07 not met (owner-confirmed 2026-07-25)**: three tuning axes tried (sigma sweep, batch sweep, option 3 natural-order correspondence). Best result: ring_mass 0.609 → 0.691 — a real, mechanistically-verified improvement, but not two recognizable rings. Full evidence in `results/phase4_summary.md`. Phase 5's benchmarking work is therefore against an imperfect generator, and that context must carry forward honestly into Phase 5's write-up, not be implied away.
- **Phase 5 VERIFIED COMPLETE (2026-07-29)**: BMK-01 and BMK-02 both delivered and independently verified (6/6 must-haves, gsd-verifier re-ran scripts live), `results/phase5_summary.md` citation-ready for Phase 6.
- **Phase 6 Plan 06-01 COMPLETE (2026-07-29)**: DOC-01 (README), the packaging half of DOC-02 (runnable code verified, repo pushed, visibility left to owner), and DOC-03 (technical note drafted) all satisfied for `merlin-quantum-case-study`. Repo confirmed still PRIVATE. Owner's remaining manual step (outside any plan's scope): flip visibility with `gh repo edit alejack312/merlin-photonic-generative-modeling --visibility public` or the GitHub UI, whenever ready.
- **Phase 6 Plan 06-02 COMPLETE (2026-07-29)**: DOC-04 (portfolio case study) satisfied — `merlin-quantum.tsx` built in the `alejandro-jackson` repo, registered, cross-linked, owner-approved live at the blocking checkpoint. **Phase 6 is now fully complete (2/2 plans) — this was the last phase in the roadmap.** No further phases remain. Two open manual items outside any plan's scope: (1) flip `merlin-quantum-case-study`'s GitHub visibility to public (from 06-01, still pending — the new case-study page's source-code link 404s until this happens), (2) nothing further planned for `alejandro-jackson` beyond the orchestrator's post-checkpoint reorder commit (`3c51c60`).

## Session Continuity

Last session: 2026-07-29
Stopped at: Phase 6 Plan 06-02 (Documentation & Publication, portfolio case study) fully executed, checkpoint-approved, and committed/pushed in the separate `alejandro-jackson` repo. `.planning/phases/06-documentation-publication/06-02-SUMMARY.md` created, this STATE.md and `.planning/ROADMAP.md` updated to reflect Phase 6 (final phase) completion.
Prior context (Phase 4, for reference): Sigma sweep (04-02), ad hoc batch-size sweep, and "option 3" (natural-order spatial correspondence — K=462, radius/center-of-mass rank pairing) all tried. Option 3 was the best result (ring_mass 0.609 → 0.691) but still owner-judged not ring-like. Full narrative: DESIGN_DECISIONS.md's three 2026-07-25 entries.
Resume by: no further plans remain in the roadmap. Project is at 100% (all 6 phases concluded, Phase 4's conclusion honestly recorded as "not successful"). Remaining open item is the owner's manual GitHub visibility toggle for `merlin-quantum-case-study` (flagged since 06-01, not blocking, no plan scoped to it since it's explicitly the owner's own manual step).
Resume file: None — no pending PLAN.md in this repo's `.planning/phases/`.
