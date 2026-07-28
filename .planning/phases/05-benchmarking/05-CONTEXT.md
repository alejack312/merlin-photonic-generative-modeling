# Phase 5: Benchmarking - Context

**Gathered:** 2026-07-28
**Status:** Ready for planning

<domain>
## Phase Boundary

The trained generator's performance is honestly quantified with a held-out MMD benchmark statistic (BMK-01) and situated against a comparison to MerLin's photonic QGAN reproduction (paper #16, adversarial loss) (BMK-02). This phase carries forward Phase 4's GEN-07-not-met result honestly — it is benchmarking an imperfect generator, not implying the shortfall away. Improving generative quality further is out of scope (that was Phase 4, now closed); tuning the generator's ring structure is not reopened here.

</domain>

<decisions>
## Implementation Decisions

### Held-out MMD statistic (BMK-01)
- "Held-out" = a real train/test split of the 400 circles-dataset points. Build a held-out `p_real_test` (separate from whatever built the `p_real` the generator was trained against) and score the trained generator's `q` against it.
- Report as mean±std across multiple seeds (multiple fresh latent-`z` draws and/or multiple random train/test splits), following the same rigor pattern as Phase 4's 20-draw stability check (0.684±0.008 style) — not a single deterministic number.
- Report against **two baselines**, bracketing the trained generator's number:
  - **Ceiling/ceiling-reference**: MMD²(p_real_test, q_untrained) using the same architecture with random/untrained parameters — shows training helped.
  - **Floor**: MMD²(p_real_train, p_real_test) — shows how close the generator gets to "as good as two real splits of real data."

### QGAN comparison scope (BMK-02)
- Preferred approach: actually run MerLin's paper #16 QGAN reproduction and compute the **same held-out MMD statistic** on its output, for a matched apples-to-apples number (not just citing paper #16's own reported metrics).
- **Fallback** (research-phase gated): if MerLin does not actually ship a runnable paper #16 QGAN reproduction locally (only a paper reference, no code), fall back to citing paper #16's reported results and comparing qualitatively (architecture, loss type) instead of a matched number. This fallback must be flagged explicitly in the summary doc if it triggers — not silently substituted.
- `/gsd:plan-phase`'s research step must confirm what MerLin actually provides for paper #16 before the plan locks in which path (matched run vs. qualitative fallback).

### What else gets reported
- Phase 4's `ring_mass`/`gap_mass` visual-quality metrics carry forward and are reported alongside the held-out MMD statistic for both the generator and (if run) the QGAN comparison — continues Phase 4's honest "not met" framing into Phase 5's numbers rather than letting MMD alone imply a cleaner story.
- Training cost/efficiency (wall-clock training time, parameter count) is reported alongside the accuracy/quality metrics, comparing the MMD generator against the QGAN comparison — relevant because adversarial (GAN) training is typically less stable/more expensive than the closed-form MMD approach, and this context makes the accuracy comparison more honest rather than a bare "which number is better."

### Claude's Discretion
- Exact train/test split ratio for the 400 circles points.
- Number of seeds/repeats and which sigma/kernel bandwidth to use for the benchmark MMD statistic (may differ from Phase 4's tuning-sweep sigma if a different choice is more defensible for a benchmark number specifically — state the choice and why if it differs).
- Exact file layout within `results/` and the phase directory, following Phase 4's existing pattern.
- Whether the QGAN comparison, if run, uses the same K=462/radius-sorted bin-center scheme as the trained generator, or its own natural output representation — decide during planning based on what's actually comparable, and document the choice.

</decisions>

<specifics>
## Specific Ideas

- Output artifact pattern should match Phase 4 exactly: scripts + numeric results (CSV/checkpoints) in `results/`, a `results/phase5_summary.md` aggregating everything, consistent with `results/phase4_summary.md`, `DESIGN_DECISIONS.md` entries, and `.planning/phases/05-benchmarking/SUMMARY.md`.
- `results/phase5_summary.md` should be written **citation-ready** for Phase 6 — clear headline numbers, captioned plots, honest framing consistent with Phase 4's "not met" context — so Phase 6's README, technical note, and case study can pull from it with minimal rework rather than needing a rewrite pass.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 05-benchmarking*
*Context gathered: 2026-07-28*
