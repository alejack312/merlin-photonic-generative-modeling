# Phase 7 Plan 02: Sigma Re-sweep (K=462) — Summary

## What this compares

Phase 4 tuned `sigma` once, in the `SIGMA_GRID = [0.02, 0.05, 0.1, 0.2, 0.4]` sweep (`sweep.py`, `results/phase4_sweep_metrics.csv`), against the original K=400 bin grid. `sigma=0.1` was the best-performing value in that sweep and was carried forward, unchanged, through every subsequent Phase 4 axis (batch-size sweep) and into "option 3" — the natural-order correspondence fix that changed K from 400 to 462 and reordered Fock-state outputs by radius rank (`natural_order_train.py`, `results/phase4_natural_checkpoint.pt`). Sigma itself was never re-tuned after that grid-width change, even though the Gaussian kernel bandwidth's effective scale relative to bin spacing shifts when K changes. This experiment re-runs the identical `SIGMA_GRID` sweep, fresh-trained from scratch (new random init per sigma), against the K=462 natural-order grid, to check whether `sigma=0.1` — the bandwidth every reported K=462 number in Phase 4/5 actually used — is still the best choice once re-tuned at the correct grid width.

## Side-by-side table

| sigma | ring_mass (K=400) | gap_mass (K=400) | ring_mass (K=462) | gap_mass (K=462) |
|---|---|---|---|---|
| 0.02 | 0.4588 | 0.0100 | 0.4425 | 0.0661 |
| 0.05 | 0.4843 | 0.0341 | 0.6247 | 0.0559 |
| 0.10 | 0.6161 | 0.0346 | 0.7145 | 0.0477 |
| 0.20 | 0.5440 | 0.0478 | 0.6067 | 0.0691 |
| 0.40 | 0.3277 | 0.0224 | 0.5467 | 0.0696 |

(K=400 values read directly from `results/phase4_sweep_metrics.csv`; K=462 values read directly from `results/phase7_sigma_resweep_metrics.csv`, produced by this plan's Task 1.)

## Descriptive facts only

The K=462 argmax (highest `ring_mass`) is **sigma=0.1**, with `ring_mass=0.7145` — the same sigma value already in use for every reported K=462 result (`results/phase4_natural_checkpoint.pt`, `results/phase4_natural_metrics.csv`, and every downstream Phase 5 benchmark). No other `SIGMA_GRID` value's K=462 `ring_mass` exceeds sigma=0.1's: the next-highest is sigma=0.05 at `ring_mass=0.6247` (0.0898 lower), followed by sigma=0.2 at `ring_mass=0.6067` (0.1078 lower), sigma=0.4 at `ring_mass=0.5467` (0.1678 lower), and sigma=0.02 at `ring_mass=0.4425` (0.2720 lower).

Separately: every K=462 `ring_mass` value in this table is higher than its corresponding K=400 `ring_mass` value at the same sigma (e.g. sigma=0.02: 0.4425 vs 0.4588 is the one exception, K=462 slightly lower; all four other sigma rows show K=462 higher than K=400 at that same sigma). This is reported as a measured fact from the two CSVs; no claim is made here about what causes it.

## Interpretation

_Owner interpretation pending — see .planning/phases/07-mechanism-validation/07-RESEARCH.md and DESIGN_DECISIONS.md's 2026-07-29 correction for the confound question this experiment addresses, and results/phase7_neighbor_locality_summary.md (07-01) for the companion mechanism-test result. This file reports the measured sigma-sweep comparison only; per this project's CLAUDE.md, the owner writes the interpretation before it is folded into any published doc._
