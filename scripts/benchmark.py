"""Phase 5, Task 1: post-hoc benchmark of the trained (option-3, K=462)
generator against a held-out MMD^2 statistic, bracketed by an untrained
baseline and a real-train-vs-real-test floor.

Post-hoc only -- no training, .eval() + torch.no_grad() throughout.
Reuses `natural_order_train.py`'s checkpoint-load pattern and this repo's
existing MMD/data/generator infrastructure unchanged.
"""

import csv

import torch

from merlin_iqp.generator.data import load_circles_data, compute_p_real
from merlin_iqp.generator.mmd import gaussian_kernel_matrix, mmd2
from merlin_iqp.generator.naturally_ordered_generator import (
    build_naturally_ordered_generator,
    natural_sorted_centers,
)
from merlin_iqp.generator.noise import sample_latent
from merlin_iqp.generator.visualize import ring_band_metrics

# SIGMA=0.1 matches the bandwidth `phase4_natural_checkpoint.pt` was trained
# at -- kept identical here (not re-tuned) for direct comparability with all
# Phase 4 numbers (ring_mass=0.691, gap_mass=0.048 were measured at this sigma).
SIGMA = 0.1
CKPT = "results/phase4_natural_checkpoint.pt"
# Mirrors Phase 4's 20-draw ring_mass stability check.
N_DRAWS = 20
RESULTS_DIR = "results"


def measure(generator, p_real_test, centers, kernel_matrix, n_draws=N_DRAWS):
    """Run n_draws fresh latent samples through `generator` (already .eval()'d)
    and collect held-out MMD^2 and ring/gap metrics for each draw."""
    mmds, ring_masses, gap_masses = [], [], []
    with torch.no_grad():
        for _ in range(n_draws):
            z = sample_latent(1)
            q = generator(z)[0]
            mmds.append(mmd2(p_real_test, q, kernel_matrix).item())
            metrics = ring_band_metrics(q, centers)
            ring_masses.append(metrics["ring_mass"])
            gap_masses.append(metrics["gap_mass"])
    return {
        "mmd_mean": torch.tensor(mmds).mean().item(),
        "mmd_std": torch.tensor(mmds).std().item(),
        "ring_mass_mean": torch.tensor(ring_masses).mean().item(),
        "ring_mass_std": torch.tensor(ring_masses).std().item(),
        "gap_mass_mean": torch.tensor(gap_masses).mean().item(),
        "gap_mass_std": torch.tensor(gap_masses).std().item(),
    }


def main():
    centers = natural_sorted_centers()
    X_train, X_test = load_circles_data()  # X_test: held out, never in p_real at training time
    p_real_train = compute_p_real(X_train, centers)
    p_real_test = compute_p_real(X_test, centers)
    kernel_matrix = gaussian_kernel_matrix(centers, SIGMA)

    trained = build_naturally_ordered_generator()
    trained.load_state_dict(torch.load(CKPT, map_location="cpu"))
    trained.eval()

    # Fresh init, no load_state_dict -- random-parameter baseline.
    untrained = build_naturally_ordered_generator()
    untrained.eval()

    trained_results = measure(trained, p_real_test, centers, kernel_matrix)
    untrained_results = measure(untrained, p_real_test, centers, kernel_matrix)

    # "Floor" here is an empirical partition-noise reference for this exact
    # split (p_real_train vs p_real_test), deterministic, no generator, no
    # loop -- NOT a mathematical lower bound. The true floor is 0 (a
    # generator identical to p_real_test scores exactly 0); this number only
    # says how much MMD^2 the train/test split itself carries before any
    # generator is involved.
    mmd_floor = mmd2(p_real_train, p_real_test, kernel_matrix).item()

    print("=== Phase 5 benchmark: held-out MMD^2 (sigma=%.2f, N_DRAWS=%d) ===" % (SIGMA, N_DRAWS))
    for name, r in [("trained", trained_results), ("untrained", untrained_results)]:
        print(
            f"{name:9s}  mmd={r['mmd_mean']:.4f}+/-{r['mmd_std']:.4f}  "
            f"ring_mass={r['ring_mass_mean']:.4f}+/-{r['ring_mass_std']:.4f}  "
            f"gap_mass={r['gap_mass_mean']:.4f}+/-{r['gap_mass_std']:.4f}"
        )
    print(f"floor      mmd={mmd_floor:.4f} (real-train vs real-test, deterministic)")

    if trained_results["mmd_mean"] >= untrained_results["mmd_mean"]:
        print(
            "ANOMALY: trained MMD^2 mean is NOT lower than untrained MMD^2 mean "
            "-- reporting as-is, not silently patched."
        )

    with open(f"{RESULTS_DIR}/phase5_benchmark_metrics.csv", "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "variant", "mmd_mean", "mmd_std", "ring_mass_mean", "ring_mass_std",
            "gap_mass_mean", "gap_mass_std", "n_draws", "sigma",
        ])
        writer.writerow([
            "trained",
            trained_results["mmd_mean"], trained_results["mmd_std"],
            trained_results["ring_mass_mean"], trained_results["ring_mass_std"],
            trained_results["gap_mass_mean"], trained_results["gap_mass_std"],
            N_DRAWS, SIGMA,
        ])
        writer.writerow([
            "untrained",
            untrained_results["mmd_mean"], untrained_results["mmd_std"],
            untrained_results["ring_mass_mean"], untrained_results["ring_mass_std"],
            untrained_results["gap_mass_mean"], untrained_results["gap_mass_std"],
            N_DRAWS, SIGMA,
        ])
        writer.writerow(["floor", mmd_floor, 0, "", "", "", "", 1, SIGMA])


if __name__ == "__main__":
    main()
