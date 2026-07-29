# Phase 7: Neighbor-Locality Test Summary

## Locked planning decisions

1. **`min_effect` threshold = 0.10 cosine-similarity units.** Pooling 20
   draws x 461 pairs/group = 9,220 samples/group gives very high statistical
   power, so a bare `p < 0.05` would be a weak bar (07-RESEARCH.md Pitfall 4
   -- the same overreach class the v1.0 milestone audit already caught once,
   in the opposite direction). 0.10 is chosen to mirror `generator/train.py`'s
   `decreasing_trend_check`, which already uses a 10%-relative-drop
   effect-size bar as this codebase's established rigor convention -- reusing
   that number keeps the two "is this a real effect, not just a significant
   one" checks in this project consistent with each other, rather than
   inventing an unrelated new threshold.
2. **Fresh `z` per parameter draw, not a single fixed `z`.** Matches this
   codebase's dominant, already-established convention (`sample_latent` is
   called fresh every time in `train_step`, `benchmark.py`,
   `natural_order_train.py` -- never cached/reused across iterations).
   Isolating parameter-draw variance alone (fixed `z`) was considered but
   rejected: it would test a narrower claim (locality under one specific
   input) than the one actually needed (does locality hold across the joint
   parameter x input space the training loop actually samples from).
3. **Trained-checkpoint theta: IN SCOPE, as a cheap supplementary check.**
   The roadmap's literal scope is "several random parameter draws" (an
   architecture property, not a property of one trained instance) -- the
   pooled 20-draw statistic is the primary result and stays scoped to that.
   But `results/phase4_natural_checkpoint.pt` already exists on disk and one
   extra `compute_jacobian` call costs ~1.3s, so it is included as a
   clearly-labeled, separately-reported extra data point (not pooled into
   the random-init statistic) rather than silently deferred, since it
   directly informs the specific ring_mass=0.691 result under investigation.


## Pooled result (N=20 draws x 461 pairs/group = 9,220 pairs/group)

| adj_mean | rand_mean | mean_diff | p_value | min_effect | passed |
|---|---|---|---|---|---|
| 0.016075 | 0.006523 | 0.009551 | 8.351025e-03 | 0.1 | False |

**Methodology caveat (adversarial-review finding, 2026-07-29):** the pooled p-value above treats all 9,220 pooled pairs as independent, but within one draw adjacent-pair cosines share rows (pair i,i+1 and i+1,i+2 both use row i+1), so they are autocorrelated, not i.i.d. -- pooling likely overstates the effective sample size and understates the true p-value. This does not change the verdict: `passed` is decided by the `min_effect=0.10` bar, which the pooled result misses by a wide margin (`mean_diff=0.0096`) independent of the p-value's validity. Read the p-value as supporting evidence, not a standalone significance claim.

## Per-draw robustness

13/20 draws individually show adjacent-mean > random-mean.


## Supplementary: trained checkpoint (results/phase4_natural_checkpoint.pt)

Single-instance measurement at the actual trained theta whose ring_mass=0.691 is the number under investigation. Kept separate from the pooled random-init statistic above -- this is a supplementary data point, not part of the primary architecture-level claim.

| adj_mean | rand_mean | mean_diff | p_value | min_effect | passed |
|---|---|---|---|---|---|
| 0.066777 | 0.026618 | 0.040159 | 1.866751e-02 | 0.1 | False |

## Interpretation

_Owner interpretation pending -- see .planning/phases/07-mechanism-validation/07-RESEARCH.md for the mechanism claim under test and DESIGN_DECISIONS.md's 2026-07-29 correction for full context. This file reports the measured numbers only; per this project's CLAUDE.md, the owner writes the interpretation before it is folded into any published doc._
