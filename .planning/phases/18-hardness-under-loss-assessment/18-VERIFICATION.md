---
phase: 18-hardness-under-loss-assessment
verified: 2026-08-17T03:27:16Z
status: passed
score: 5/5 must-haves verified
---

# Phase 18: Hardness-Under-Loss Assessment Verification Report

**Phase Goal:** Measure whether the sampling-hardness argument survives realistic photon loss, via `Processor.probs()` + a loss mechanism (not `Analyzer`, which silently ignores loss), grounded in a named asymptotic threshold from the literature, reported honestly either direction.
**Verified:** 2026-08-17T03:27:16Z
**Status:** passed
**Re-verification:** No -- initial verification

## Goal Achievement

### Observable Truths (ROADMAP success criteria)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | arXiv:2510.24137 read in full; threshold formula extracted and cited, before methodology finalized | VERIFIED | 18-RESEARCH.md Finding 1-2 (full 14-page + appendix read, dated pre-planning); docs/iqp-baseline.md cites Theorem 1 verbatim (eta = Theta(1/sqrt(N))); hardness/loss_model.py docstring cites the same Sec. II.B commutation fact |
| 2 | Loss sweep run via Processor.probs()+pcvl.LC(loss), uniform across modes, explicit min_detected_photons_filter(0), over a defined eta grid -- not NoiseModel | VERIFIED | hardness/loss_model.py / loss_model_weight2.py implement exactly this (read in full); hardness/sweep.py ETA_GRID = [0.99,0.95,0.90,0.80,0.60,0.35,0.05]; real data in results/phase18_weight1_loss_sweep.csv (35 rows, n=2..6) and results/phase18_mixed_loss_sweep.csv (21 rows, n=2..4); regression test proves omitting the filter is loss-invariant while the real function is not (test_pitfall_2_regression_broken_helper_is_loss_invariant_correct_fn_is_not, passing) |
| 3 | Cross-checked against NoiseModel(transmittance=eta) at >=1 shared eta on a simplified non-polarization circuit, agreement within stated tolerance | VERIFIED | tests/test_loss_model.py::test_hard02_noise_model_and_lc_agree_on_shared_toy_circuit, parametrized eta in {0.5,0.8}, asserts atol=1e-9; test passes (confirmed by direct run); doc cites the same result in the Methodology/HARD-02 section |
| 4 | Positioned against genuine Aaronson-Brod (arXiv:1510.05245) fixed-loss-count regime AND BMS (arXiv:1610.01808) depolarizing regime; states which regime(s) tested loss sits in; states explicitly how (or whether) loss translates to an effective depolarizing rate | VERIFIED | docs/hardness-under-loss-study.md HARD-04 section: AB paper read in full (docs/papers/1510.05245.pdf, 18-01-SUMMARY.md), quoted verbatim on the fixed-k-vs-fractional-eta mismatch, computed crossover table (N=6, ETA_GRID vs log(6)); BMS kept explicitly qualitative-only; owner's attempt-first checkpoint answer recorded verbatim: no established eta-to-epsilon translation exists in the literature, computing one would be unowned original research, so none was fabricated -- an explicit, honestly-stated non-computation, matching this project's honesty-over-narrative convention and the task instructions' guidance that this is a valid, intentional outcome |
| 5 | TVD-vs-eta tracked against lossless reference and an explicit classically-easy baseline, alongside anticoncentration alpha(eta); weight-2 sweep with herald-failure compounding included; explicit "what this does/doesn't establish" scope statement written | VERIFIED | Both CSVs contain tvd_to_lossless, tvd_to_uniform, tvd_to_product_marginals, alpha columns for every (n,eta,scope) cell; mixed CSV additionally has herald_failure_prob/herald_success_rate (rises from 0.926 at eta=0.99 to 0.999 at eta=0.05, confirming real compounding, not an analytic product); docs/hardness-under-loss-study.md HARD-06 section is an explicit, itemized scope statement |

**Score:** 5/5 truths verified

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| hardness/loss_model.py | Weight-1 LC-based loss primitive | VERIFIED | 74 lines, LC front-loaded on all 2n modes, explicit min_detected_photons_filter(0), real Perceval Processor.probs() call, no stub patterns |
| hardness/loss_model_weight2.py | Weight-2 LC-based loss + herald compounding | VERIFIED | 183 lines, LC on all 2n+2 modes including both ancilla modes, single real Processor.probs() call per cell (no analytic herald x loss product), herald_failure_prob tracked separately from residual |
| hardness/baselines.py | Classically-easy baselines + anticoncentration alpha | VERIFIED | 94 lines, pure/Perceval-free, uniform_baseline, product_of_marginals_baseline, anticoncentration_alpha (BMS Theorem 4 normalization) |
| hardness/sweep.py | Per-cell integration + chunking | VERIFIED | 205 lines, composes the three modules above, ETA_GRID, deterministic RNG substreams reused from trainability.rng |
| loss_sweep.py | Chunked/resumable CLI | VERIFIED | present at repo root, exercised in Plan 18-06 (external-kill recovery via --eta-grid resumption, verified in git history) |
| results/phase18_weight1_loss_sweep.csv | Real weight-1 TVD/alpha dataset | VERIFIED | 35 data rows (n=2..6 x 7 eta), all finite, non-degenerate (alpha_mean varies 16.2 to 4.5e-15) |
| results/phase18_mixed_loss_sweep.csv | Real mixed TVD/alpha/herald dataset | VERIFIED | 21 data rows (n=2..4 x 7 eta), all finite, herald_failure_prob monotonically rises with loss |
| results/phase18_*_plot.png (3 files) | TVD/anticoncentration plots | VERIFIED | all 3 present, non-trivial file sizes (80-101KB), built from the real CSVs by hardness_analysis.py |
| docs/hardness-under-loss-study.md | Canonical results doc | VERIFIED | 504 lines, methodology-before-results structure, all HARD-01..07 sections present and complete (no placeholder headings remain) |
| docs/iqp-baseline.md (HARD-03 citations) | Park and Oh + Aaronson-Brod citations | VERIFIED | both papers cited by arXiv ID, formulas extracted verbatim, explicitly kept distinct |
| docs/papers/1510.05245.pdf, docs/papers/2511.07853.pdf | Locally-saved primary sources | VERIFIED | present, both directly read (not abstract-only) per SUMMARY evidence |
| tests/test_loss_model.py, test_loss_model_weight2.py, test_baselines.py | Regression coverage | VERIFIED | 32 tests, all passing (confirmed via direct pytest run) |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| hardness/sweep.py | hardness/loss_model.py / loss_model_weight2.py | direct import + call in _raw_values_for_cell | WIRED | both lossless (eta=1.0) and lossy (eta=requested) calls use the same loss-model function, never a separate "lossless" code path |
| hardness/sweep.py | hardness/baselines.py | direct import, product-of-marginals computed once per draw from the eta=1.0 reference | WIRED | matches 18-CONTEXT.md's explicit lock, verified in code |
| loss_sweep.py | results/phase18_*.csv | CLI writes real Processor.probs() output | WIRED | CSVs contain 35+21 real, non-degenerate rows with correct row counts matching the stated n-range x eta-grid |
| results/phase18_*.csv | hardness_analysis.py -> results/phase18_*.png | plot generation reads the real CSVs | WIRED | plots exist, correct timestamps (2026-08-17 04:23), post-date the sweep CSVs |
| results/phase18_*.csv | docs/hardness-under-loss-study.md | tabulated numbers match CSV values | WIRED | spot-checked: doc's n=6,eta=0.99 alpha=16.2048 matches CSV alpha_mean exactly; herald-success-rate table matches CSV herald_success_rate_mean column |

### Requirements Coverage

| Requirement | Status | Evidence |
|-------------|--------|----------|
| HARD-01 | SATISFIED | Real Processor.probs()+LC sweep, both CSVs populated, never Analyzer/NoiseModel as primary mechanism |
| HARD-02 | SATISFIED | test_hard02_noise_model_and_lc_agree_on_shared_toy_circuit passes at atol=1e-9, eta in {0.5,0.8} |
| HARD-03 | SATISFIED | Full read of arXiv:2510.24137 (pre-methodology), Theorem 1 extracted and cited |
| HARD-04 | SATISFIED (owner-resolved) | AB + BMS positioning stated plainly; no fabricated eta-to-epsilon translation, explicit owner decision on record |
| HARD-05 | SATISFIED | Dual baselines + alpha(eta) tracked at every cell, both scopes |
| HARD-06 | SATISFIED | Explicit scope statement in docs/hardness-under-loss-study.md |
| HARD-07 | SATISFIED | Ancilla-inclusive loss, single real pipeline call, herald_failure_prob tracked and shown to compound with eta |

Note: .planning/REQUIREMENTS.md and .planning/ROADMAP.md still show these as "Pending"/"0/8 Planned" -- this reflects that phase-completion bookkeeping (roadmap/requirements-doc updates) is normally done by the orchestrator after verification passes, per this project's established sequencing (compare Phase 17.1's roadmap entry, updated only after its own verification). STATE.md already correctly reflects "Phase 18 is fully complete -- 8/8 plans shipped." Not a goal-achievement gap.

### Anti-Patterns Found

None. Grep for TODO/FIXME/placeholder/"not implemented"/"coming soon" across hardness/*.py, hardness_analysis.py, loss_sweep.py returned zero matches. hardness/depolarizing_translation.py was deliberately never created -- a documented, intentional non-artifact (see HARD-04 discussion above), not a missing stub.

### Human Verification Required

None. All must-haves are structurally/numerically checkable from committed artifacts (code, tests, CSVs, doc), and were checked directly:
- Full test suite run: 266/266 passing (python -m pytest -q), including the 32 Phase-18-specific tests.
- CSV row counts and value ranges independently spot-checked against the doc's tabulated numbers.
- Both cited papers (docs/papers/1510.05245.pdf, docs/papers/2511.07853.pdf) confirmed present on disk.

### Gaps Summary

No gaps. All 5 ROADMAP success criteria and all 7 requirements (HARD-01..07) are verified against real code, real data, and a complete write-up -- not merely claimed in SUMMARYs. HARD-04's "no eta-to-epsilon translation" outcome is a deliberate, well-documented scope boundary (owner's explicit attempt-first decision), consistent with this project's honesty-over-narrative convention, and matches the task's own guidance that this is a valid intentional resolution rather than an unmet requirement.

One minor bookkeeping note (not a gap): ROADMAP.md/REQUIREMENTS.md have not yet been updated to reflect Phase 18's completion -- expected to be done as part of the orchestrator's post-verification ship step.

---

*Verified: 2026-08-17T03:27:16Z*
*Verifier: Claude (gsd-verifier)*
