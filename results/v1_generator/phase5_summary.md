# Phase 5 Summary: Benchmarking

## Headline numbers

| Metric | Value |
|---|---|
| **Held-out MMD² (trained generator)** | **0.0125 ± 0.0003** (mean±std, N=20 latent draws, σ=0.1) |
| Held-out MMD² (untrained baseline) | 0.0360 ± 0.0048 (mean±std, N=20 latent draws, σ=0.1) |
| Held-out MMD² (real-vs-real floor) | 0.0114 (deterministic, no generator) |
| ring_mass (trained, re-measured this phase) | 0.6833 ± 0.0073 |
| gap_mass (trained, re-measured this phase) | 0.0514 ± 0.0035 |
| Wall-clock training time | 425.93 s (≈ 7.1 min, 300 epochs, batch=32) |
| Parameter count | 220 |

Source: `results/phase5_benchmark_metrics.csv` (MMD²/ring/gap), `results/phase5_training_cost.csv` (wall-clock/params).

## What "held-out" means here

`X_test` (80 of the 400 circles-dataset points) was never included in `p_real` at training time — it is a genuine held-out set in that sense. But it is drawn from the **same** underlying `make_circles(random_state=42)` call as `X_train`, just a different 20% partition of one fixed draw (`train_test_split(test_size=0.2, random_state=42)`), not an independently sampled dataset from a different distribution. This is standard train/test-split practice, and it is what BMK-01 measures — generalization to an unseen partition of the same fixed draw, not generalization to a genuinely different data-generating process. The floor baseline below (`MMD²(p_real_train, p_real_test)` = 0.0114) makes the size of this partition-noise floor explicit, rather than leaving "held-out" to imply more than it does.

## BMK-01 interpretation

The trained generator's held-out MMD² (0.0125 ± 0.0003) sits clearly below the untrained baseline (0.0360 ± 0.0048, non-overlapping ranges) — training measurably helped, by roughly a 3x reduction in MMD². It also sits close to the real-train-vs-real-test floor (0.0114) — the trained generator's held-out MMD² is only about 0.0011 above the floor, i.e. it is close to "as good as comparing real data to itself, split two ways" by this metric.

**Two caveats on how strongly to read this (2026-07-29):** First, "floor" here is shorthand for `MMD²(p_real_train, p_real_test)` — an empirical partition-noise reference for this specific fixed split, not a mathematical lower bound. The true floor is 0 (a generator identical to `p_real_test` would score exactly 0 — confirmed by this project's own `test_mmd.py`); 0.0114 only tells you how much MMD² this train/test split carries on its own, before any generator is involved. Second, "training measurably helped" rests on one trained checkpoint compared against one untrained (single random-init) generator — the 20 latent draws quantify genuine sampling variance for *that specific pair*, but they are not 20 independent trainings, so this is not yet evidence that training helps *on average* across seeds/initializations, only that it helped for the one run that was actually done.

This benchmarks Phase 4's GEN-07-not-met generator (`results/phase4_natural_checkpoint.pt`, "option 3" natural-order correspondence, K=462). Phase 4's headline table reports ring_mass=0.691/gap_mass=0.048 — a single-draw metric from that checkpoint's original training-time measurement, not a 20-draw mean. Phase 4's own 20-draw stability check on this checkpoint gave ring_mass=0.684 ± 0.008 (range 0.670–0.698). This phase's independent 20-draw re-measurement of the same checkpoint gives ring_mass=0.6833 ± 0.0073 and gap_mass=0.0514 ± 0.0035 — consistent with (matching, within one std) Phase 4's own 20-draw mean, not a discrepancy, just a different random sample of 20 latent draws. (Correction, 2026-07-29: an earlier version of this sentence attributed 0.691 itself to "its own 20-draw stability check" — it isn't; 0.691 is the single-sample figure, 0.684±0.008 is the actual 20-draw mean.)

A separate fresh 300-epoch retrain done for the wall-clock measurement (`benchmark_timing.py`, a *different* random initialization and training run, saved to a scratch checkpoint, never overwriting `phase4_natural_checkpoint.pt`) produced ring_mass=0.6520/gap_mass=0.0514 on a single post-training sample — close to but below Phase 4's documented 0.691, illustrating run-to-run variance from a fresh stochastic training run at identical hyperparameters. Both numbers are reported here for honesty rather than picking the more favorable one.

**Bottom line, carried forward honestly from Phase 4:** the MMD² statistic looks good in isolation (close to the real-data floor), but ring_mass ≈ 0.68–0.69 and gap_mass ≈ 0.05 confirm what Phase 4 already established visually — this is "an improvement, still not two distinct rings," not a fully successful generative result. A low held-out MMD² does not, by itself, imply the visual ring structure is clean; both numbers must be read together, which is why both are reported here rather than MMD² alone.

## BMK-02: comparison against MerLin's photonic QGAN reproduction (paper #16)

**Fallback path used — no matched numeric comparison was computed.**

Reason: MerLin's paper #16 reproduction (Sedrakyan & Salavrakos, "Photonic quantum generative adversarial networks for classical data," arXiv:2405.06023) is runnable code at `github.com/merlinquantum/reproduced_papers/papers/photonic_QGAN` — confirmed to use MerLin's `ML.QuantumLayer` directly (`lib/generators.py` imports `merlin as ML` and constructs `ML.QuantumLayer(...)` instances), despite a stale README banner claiming "only in Perceval for now." But it trains on 8x8 `optdigits` grayscale digit-image patches via an adversarial minimax loss with a classical discriminator, not the circles dataset used throughout this project. Its image-pixel output space has no defined mapping onto this project's K=462 2D bin-center MMD metric without inventing new work — that scope is explicitly deferred to BMK-03 (out of scope for Phase 5). The reproduction's own reported best SSIM = 0.570575 (from its Adam-based hyperparameter study) is cited here for reference; its own README flags the Adam-vs-SPSA choice as an open, unresolved question versus the original paper's method — a caveat worth carrying forward rather than presenting the SSIM number as settled.

### Qualitative comparison table

| Dimension | This project | QGAN reproduction (paper #16) |
|---|---|---|
| Architecture | Single `ML.QuantumLayer` + closed-form MMD² full-distribution loss, no adversary | `ML.QuantumLayer`-based generator + classical discriminator + adversarial minimax loss |
| Dataset domain | 2D point-cloud, two-ring `circles` dataset | 8x8 grayscale `optdigits` digit-image patches |
| Training cost | Measured this phase: 425.93 s wall-clock, 220 parameters, 300 epochs, batch=32 | Not measured this phase (not run — out of scope, see BMK-02 reason above); only its own reported SSIM=0.570575 is cited, no wall-clock/parameter-count number is fabricated for it |
| Reported quality metric | Held-out MMD²=0.0125±0.0003 (this project's metric, not comparable across domains) | SSIM=0.570575 (reproduction's own reported number, Adam-based, on `optdigits`) |

## Honest framing, restated

This phase benchmarks an imperfect generator (Phase 4, GEN-07 not met, owner-confirmed 2026-07-25). The held-out MMD² and QGAN comparison numbers above describe that generator's actual, measured performance — training clearly helped and the held-out MMD² sits close to the real-data floor, but the ring/gap metrics confirm the generated distribution still does not form two recognizably distinct rings. These numbers describe the generator that was actually built, not a hypothetical fully-successful one.
