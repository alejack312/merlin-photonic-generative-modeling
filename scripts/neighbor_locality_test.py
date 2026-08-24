import csv

import torch

from merlin_iqp.generator.naturally_ordered_generator import build_naturally_ordered_generator
from merlin_iqp.generator.noise import sample_latent
from merlin_iqp.generator.neighbor_locality import (
    compute_jacobian,
    adjacent_and_random_cosines,
    neighbor_locality_check,
)

N_DRAWS = 20
MIN_EFFECT = 0.10
CKPT = "results/phase4_natural_checkpoint.pt"
RESULTS_DIR = "results"

LOCKED_DECISIONS = """## Locked planning decisions

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
"""


def run_random_draws():
    per_draw_rows = []
    all_adj, all_rand = [], []
    for draw_idx in range(N_DRAWS):
        gen = build_naturally_ordered_generator()  # fresh instance == fresh random theta draw, no load_state_dict
        gen.eval()
        z = sample_latent(1)  # fresh z per draw -- locked decision (see 07-01-PLAN.md objective)
        J = compute_jacobian(gen, z)
        adj_cos, rand_cos = adjacent_and_random_cosines(J, seed=draw_idx)
        draw_mean_diff = adj_cos.mean().item() - rand_cos.mean().item()
        per_draw_rows.append({
            "draw_idx": draw_idx,
            "adj_mean": adj_cos.mean().item(),
            "rand_mean": rand_cos.mean().item(),
            "mean_diff": draw_mean_diff,
            "sign_agrees": draw_mean_diff > 0,
        })
        all_adj.append(adj_cos)
        all_rand.append(rand_cos)
        print(f"draw {draw_idx:2d}  adj_mean={adj_cos.mean().item():.4f}  rand_mean={rand_cos.mean().item():.4f}  diff={draw_mean_diff:+.4f}")
    return per_draw_rows, torch.cat(all_adj), torch.cat(all_rand)


def run_trained_checkpoint():
    trained_gen = build_naturally_ordered_generator()
    trained_gen.load_state_dict(torch.load(CKPT, map_location="cpu"))
    trained_gen.eval()
    z = sample_latent(1)
    J = compute_jacobian(trained_gen, z)
    adj_cos, rand_cos = adjacent_and_random_cosines(J, seed=9999)
    return neighbor_locality_check(adj_cos, rand_cos, min_effect=MIN_EFFECT)


def write_csv(per_draw_rows, pooled_result, trained_result):
    fieldnames = ["draw_idx", "adj_mean", "rand_mean", "mean_diff", "sign_agrees", "p_value", "min_effect", "passed"]
    with open(f"{RESULTS_DIR}/phase7_neighbor_locality_metrics.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in per_draw_rows:
            writer.writerow({
                "draw_idx": row["draw_idx"],
                "adj_mean": row["adj_mean"],
                "rand_mean": row["rand_mean"],
                "mean_diff": row["mean_diff"],
                "sign_agrees": row["sign_agrees"],
                "p_value": "",
                "min_effect": "",
                "passed": "",
            })
        writer.writerow({"draw_idx": "pooled", "sign_agrees": "", **pooled_result})
        writer.writerow({"draw_idx": "trained_checkpoint", "sign_agrees": "", **trained_result})


def write_summary(pooled_result, n_agree, trained_result):
    lines = []
    lines.append("# Phase 7: Neighbor-Locality Test Summary\n")
    lines.append(LOCKED_DECISIONS)
    lines.append("\n## Pooled result (N=20 draws x 461 pairs/group = 9,220 pairs/group)\n")
    lines.append("| adj_mean | rand_mean | mean_diff | p_value | min_effect | passed |")
    lines.append("|---|---|---|---|---|---|")
    lines.append(
        f"| {pooled_result['adj_mean']:.6f} | {pooled_result['rand_mean']:.6f} | "
        f"{pooled_result['mean_diff']:.6f} | {pooled_result['p_value']:.6e} | "
        f"{pooled_result['min_effect']} | {pooled_result['passed']} |"
    )
    lines.append(
        "\n**Methodology caveat (adversarial-review finding, 2026-07-29):** the pooled "
        "p-value above treats all 9,220 pooled pairs as independent, but within one draw "
        "adjacent-pair cosines share rows (pair i,i+1 and i+1,i+2 both use row i+1), so "
        "they are autocorrelated, not i.i.d. -- pooling likely overstates the effective "
        "sample size and understates the true p-value. This does not change the verdict: "
        "`passed` is decided by the `min_effect=0.10` bar, which the pooled result misses "
        "by a wide margin (`mean_diff=0.0096`) independent of the p-value's validity. Read "
        "the p-value as supporting evidence, not a standalone significance claim.\n"
    )
    lines.append("\n## Per-draw robustness\n")
    lines.append(f"{n_agree}/20 draws individually show adjacent-mean > random-mean.\n")
    lines.append("\n## Supplementary: trained checkpoint (results/phase4_natural_checkpoint.pt)\n")
    lines.append(
        "Single-instance measurement at the actual trained theta whose ring_mass=0.691 is "
        "the number under investigation. Kept separate from the pooled random-init statistic "
        "above -- this is a supplementary data point, not part of the primary architecture-level claim.\n"
    )
    lines.append("| adj_mean | rand_mean | mean_diff | p_value | min_effect | passed |")
    lines.append("|---|---|---|---|---|---|")
    lines.append(
        f"| {trained_result['adj_mean']:.6f} | {trained_result['rand_mean']:.6f} | "
        f"{trained_result['mean_diff']:.6f} | {trained_result['p_value']:.6e} | "
        f"{trained_result['min_effect']} | {trained_result['passed']} |"
    )
    lines.append("\n## Interpretation\n")
    lines.append(
        "_Owner interpretation pending -- see .planning/phases/07-mechanism-validation/07-RESEARCH.md "
        "for the mechanism claim under test and DESIGN_DECISIONS.md's 2026-07-29 correction for full "
        "context. This file reports the measured numbers only; per this project's CLAUDE.md, the owner "
        "writes the interpretation before it is folded into any published doc._\n"
    )
    with open(f"{RESULTS_DIR}/phase7_neighbor_locality_summary.md", "w") as f:
        f.write("\n".join(lines))


def main():
    per_draw_rows, pooled_adj, pooled_rand = run_random_draws()
    pooled_result = neighbor_locality_check(pooled_adj, pooled_rand, min_effect=MIN_EFFECT)
    n_agree = sum(r["sign_agrees"] for r in per_draw_rows)
    print(f"\npooled  adj_mean={pooled_result['adj_mean']:.4f}  rand_mean={pooled_result['rand_mean']:.4f}  "
          f"mean_diff={pooled_result['mean_diff']:+.4f}  p_value={pooled_result['p_value']:.4e}  "
          f"passed={pooled_result['passed']}")
    print(f"per-draw robustness: {n_agree}/20 draws show adjacent-mean > random-mean")

    trained_result = run_trained_checkpoint()
    print(f"trained_checkpoint  adj_mean={trained_result['adj_mean']:.4f}  rand_mean={trained_result['rand_mean']:.4f}  "
          f"mean_diff={trained_result['mean_diff']:+.4f}  p_value={trained_result['p_value']:.4e}  "
          f"passed={trained_result['passed']}")

    write_csv(per_draw_rows, pooled_result, trained_result)
    write_summary(pooled_result, n_agree, trained_result)


if __name__ == "__main__":
    main()
