---
milestone: v1
audited: 2026-07-29
status: tech_debt
scores:
  requirements: 14/15
  phases: 6/6
  integration: 6/6
  flows: 1/1
gaps: {}
tech_debt:
  - source: codex-deep-audit
    severity: moderate
    items:
      - "Natural-order correspondence mechanism claim is asserted, not established — MMD is invariant to consistent relabeling of p/q/K, so 'fewer runs = easier to fit' isn't itself a mechanism unless COM-sorted circuit outputs independently have locality, which is untested"
      - "Sigma=0.1 was never re-swept after K changed 400→462 and correspondence changed — CONFIRMED: at sigma=0.1 the two rings (0.1 apart) have kernel similarity 0.607 to each other and 0.882 to the gap between them, meaning the loss is structurally tolerant of gap-filling"
      - "docs/mmd-loss.md's tau/sigma direction is backwards — CONFIRMED by direct computation: tau=tanh(1/(4*sigma^2)) gives tau->1 as sigma->0 (not 'low tau (small sigma)' as stated)"
      - "Benchmark statistical claim overreach: one trained checkpoint vs one untrained init, 20 latent draws is not evidence of average improvement across training seeds"
      - "'Floor' terminology for MMD²(p_train,p_test)=0.0114 overstates a lower bound — true floor is 0 (self-MMD); phase5_summary.md's actual prose already hedges this reasonably (partition-noise framing), but the word 'floor' itself is imprecise"
      - "Training objective is E_z[MMD²(p,q_z)], not MMD²(p, E_z[q_z]) — a real distinction between per-latent conditional matching and matching the generator's marginal output distribution, not previously flagged in DESIGN_DECISIONS.md"
      - "'Reproducible improvement' (phase4_summary.md) is unsupported — no RNG seeding, single training run per variant"
  - source: codex-deep-audit
    severity: minor
    items:
      - "CONFIRMED: results/phase4_summary.md's batch=64/128 table numbers (0.610/0.063, 0.618/0.077) do not match the committed results/phase4_batch_sweep_metrics.csv (0.5808/0.0658, 0.6051/0.0712) — data drift from an unseeded rerun after the summary was written; does not change the batch=32-stays-best conclusion"
      - "phase5_summary.md's headline ring_mass=0.691 is the single-draw metric, not the 20-draw mean (0.684±0.008) it's presented alongside"
      - "docs/mmd-loss.md's claim that the IQP project's exact path 'avoids enumeration' is contradicted by the sibling repo's own kernel.py, which explicitly builds 2^n arrays and caps at n<=20"
      - "NaturallyOrderedGenerator(input_size=...) accepts arbitrary values but silently breaks if given anything other than the hardcoded default (462-width grid, dim-10 latent)"
      - "Minor cleanliness: unused numpy import in generator/mmd.py, unused labels in generator/data.py, no tests cover benchmark statistics/CSV consistency/bandwidth selection/the COM-smoothness claim"
  - source: integration-checker
    severity: minor
    items:
      - "Repo is still private — case study's 'Source Code' link and the Vincent technical note both link a 404ing URL until the owner's manual visibility toggle (already tracked, not new)"
      - "README's 'How to run' implies generator/train.py is independently runnable; it has no __main__ block and is a no-op when run directly (train.py at repo root is the actual entrypoint)"
---

# v1 Milestone Audit — MerLin Photonic Generative Modeling

**Audited:** 2026-07-29
**Status:** tech_debt (no critical blockers; real, verified accumulated concerns — several confirmed independently, not just Codex's claims)

## Requirements Coverage

| Requirement | Phase | Status |
|---|---|---|
| ENV-01, ENV-02 | 1 | Satisfied |
| GEN-01 through GEN-06 | 1-3 | Satisfied |
| GEN-07 | 4 | **Not met** (honestly concluded 2026-07-25, owner-confirmed — not a gap, a documented result) |
| BMK-01, BMK-02 | 5 | Satisfied |
| DOC-01 through DOC-04 | 6 | Satisfied |

14/15 satisfied, 1 honestly not-met (by design — this project's core value proposition is honest reporting, not a clean win).

## Phase Verification Summary

| Phase | VERIFICATION.md | Status |
|---|---|---|
| 1 | None (predates plan-based tracking) | — |
| 2 | None (SUMMARY.md only, no formal gsd-verifier pass on record) | — |
| 3 | 03-01-VERIFICATION.md | Passed, 6/6 |
| 4 | None (concluded via owner human-verify checkpoint, not gsd-verifier — GEN-07 explicitly not met) | — |
| 5 | 05-VERIFICATION.md | Passed, 6/6 |
| 6 | 06-VERIFICATION.md | Passed, 15/15 |

## Cross-Phase Integration

gsd-integration-checker traced the full train→benchmark→README→case-study numeric chain live (not from SUMMARY claims): checkpoint loads `strict=True`, all six headline numbers (MMD² trained/untrained/floor, ring_mass, gap_mass, wall-clock, param count) match byte-for-byte across `phase5_benchmark_metrics.csv`, `phase5_summary.md`, `README.md`, and the portfolio case study. Zero numeric or file-path drift in that chain. 48/48 tests pass live. Full detail: see integration-checker's findings folded into tech_debt above (private-repo link, train.py doc phrasing).

## Codex Deep Audit (gpt-5.5 via `codex exec`, xhigh reasoning)

Per your request, directed at this project's full implementation, MerLin's local package source (`venv/Lib/site-packages/merlin/`, since docs.merlinquantum.ai wasn't crawled), and the sibling IQP-MMD project's Obsidian vault (`~/iqp-mmd-barren-plateau/iqp-mmd-barren-plateau-vault/`) for cross-referencing kernel/bandwidth conventions and the "low loss ≠ learned structure" lesson this project explicitly claims to replicate.

**Zero CRITICAL findings** — no correctness bug that would silently produce wrong numbers. Core MMD² formula, kernel construction, bin-center/`p_real` construction, train/test separation, the natural-order permutation code itself, and MerLin's `QuantumLayer` characterization were all checked and found clean.

**Seven MODERATE findings** — these are about the strength of causal/statistical claims made in the project's own documentation, not about code correctness. I independently re-verified three of the highest-value ones myself (not just trusting Codex's output):

1. **Confirmed by direct computation:** `docs/mmd-loss.md` states "Low tau (small sigma)" — but `tau=tanh(1/(4σ²))` computes to tau≈1.0 at σ=0.1 and σ=0.02, and only drops toward 0 as σ grows past ~1. The doc has the sigma↔tau relationship backwards. This is in a file linked from the README as a mechanism deep-dive.
2. **Confirmed by re-reading the code and computing kernel similarity directly:** sigma=0.1 was tuned against the old K=400 raster-ordered model and never re-swept after switching to K=462 with radius/center-of-mass correspondence. At σ=0.1, the two rings (0.1 apart) have Gaussian-kernel similarity 0.607 to each other, but a point in the empty gap between them has similarity 0.882 to either ring — the loss is structurally more tolerant of gap-filling than of correctly separating the rings, at the exact bandwidth actually used.
3. **Codex's claim, not independently re-derived by me:** the natural-order-correspondence "mechanism" (radius sorting turns 44 fragments into ~6 contiguous bands, therefore easier to fit) is asserted in DESIGN_DECISIONS.md but never actually tested — MMD is invariant to any *consistent* relabeling of p, q, and the kernel matrix together, so the claimed benefit only holds if the circuit's raw Fock-state outputs independently have locality that center-of-mass sorting captures. That locality is assumed, not measured.

The remaining four moderate findings (benchmark statistical strength, "floor" terminology, the E_z[MMD²] vs MMD²(E_z[q]) objective distinction, and the unseeded "reproducible" claim) are Codex's analysis — plausible and specific enough to take seriously, but I have not independently re-derived each one.

**Six MINOR findings**, two of which I directly confirmed: the batch=64/128 numbers in `phase4_summary.md`'s table don't match the committed CSV (real data drift, doesn't change the batch=32-stays-best conclusion), and `docs/mmd-loss.md`'s claim about the sibling project's exact-MMD path "avoiding enumeration" is contradicted by that project's own `kernel.py` (explicit `2^n`-sized arrays, capped at n≤20).

Full raw Codex output: `.planning/phases/06-documentation-publication/` was not the right home for this (it's a post-hoc project-wide audit, not phase-scoped) — see this file's tech_debt section above for the complete itemized list; ask if you want the verbatim Codex transcript preserved as a separate file.

## What This Means

None of this changes GEN-07's "not met" verdict or invalidates the benchmark's core comparison (trained clearly beats untrained — that ordering is not in question). What it does affect: the specific *mechanistic story* for why the natural-order fix helped (asserted, not demonstrated), one factual error in a public-facing mechanism doc (tau/sigma direction), and several places where prose slightly overclaims what a single unseeded run or one summary number can support.

Per this project's own CLAUDE.md ("Interpreting benchmark/metric results — Claude may compute and plot them, but the owner writes the interpretation first, Claude checks it" / "Anything the owner will need to explain to Vincent or in an interview, unaided"), I'm surfacing these rather than silently patching the docs — several of these (the tau/sigma error, the untested mechanism claim) are exactly the kind of thing you'd want to be able to explain or defend if Vincent asked a follow-up question.

---
*Audited: 2026-07-29*
