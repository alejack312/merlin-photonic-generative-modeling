"""Phase 7, plan 02: re-run Phase 4's SIGMA_GRID sweep against the K=462
natural-order grid (NaturallyOrderedGenerator / natural_sorted_centers)
instead of the old K=400 grid it was originally tuned on.

Phase 4's sigma=0.1 choice was tuned once against K=400 (sweep.py) and never
re-swept after the correspondence fix changed K to 462. This experiment
checks whether sigma=0.1 is still the best bandwidth at K=462, or whether a
stale, never-re-tuned bandwidth was masking or inflating the correspondence
fix's apparent ring_mass 0.609->0.691 improvement.

Adapted from sweep.py's exact structure (train_all_sigmas,
build_comparison_figure, main), swapping the K=400 generator/grid for the
K=462 natural-order equivalents. Do NOT import generator.bin_centers.make_bin_centers
or generator.train.build_generator here (07-RESEARCH.md Anti-Pattern).

Resumable: re-running after an interruption reuses each sigma's checkpoint on
disk rather than retraining (backgrounded multi-minute scripts have died
silently in this environment before -- run this in the foreground), matching
sweep.py's and natural_order_train.py's established pattern.
"""

import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch

from generator.data import load_circles_data, compute_p_real
from generator.mmd import SIGMA_GRID, gaussian_kernel_matrix
from generator.naturally_ordered_generator import (
    build_naturally_ordered_generator,
    natural_sorted_centers,
)
from generator.noise import sample_latent
from generator.train import train_step
from generator.visualize import sample_points, ring_band_metrics

EPOCHS = 300  # held fixed at Phase 4's value -- isolates sigma as the one variable
LR = 0.01     # held fixed at Phase 4's value -- sigma is the only variable under test here
BATCH_SIZE = 32
RESULTS_DIR = "results"


def train_all_sigmas(centers, p_real):
    """Task 1: retrain a fresh NaturallyOrderedGenerator per SIGMA_GRID value
    at K=462, save each checkpoint, and record ring/gap-band metrics for each.

    Resumable: if a sigma's checkpoint already exists on disk (e.g. a prior
    run of this script was interrupted partway through the sweep), that
    sigma is NOT retrained -- its already-completed, already-fresh-init
    checkpoint is loaded instead, only to recompute its metrics row.

    Reproducibility note (adversarial-review finding, 2026-07-29): the
    per-sigma init is seeded deterministically by grid index below. Without
    this, a resumed run would draw a DIFFERENT random init for any sigma
    retrained after the resume point than an uninterrupted run would have --
    same checkpoint filename, silently different local optimum, no warning.
    Seeding here makes a resumed run reproduce an uninterrupted run's result
    exactly for every sigma, whether loaded from checkpoint or freshly
    trained."""
    rows = []
    for sigma_idx, sigma in enumerate(SIGMA_GRID):
        ckpt_path = f"{RESULTS_DIR}/phase7_sigma_{sigma}_checkpoint.pt"
        torch.manual_seed(1000 + sigma_idx)  # deterministic per-sigma init -- see reproducibility note above
        generator = build_naturally_ordered_generator()  # K=462, fresh (but seeded) random init every sigma

        if os.path.exists(ckpt_path):
            print(f"--- sigma={sigma} (checkpoint already exists, skipping retrain) ---")
            generator.load_state_dict(torch.load(ckpt_path, map_location="cpu"))
        else:
            print(f"--- sigma={sigma} ---")
            kernel_matrix = gaussian_kernel_matrix(centers, sigma)
            optimizer = torch.optim.Adam(generator.parameters(), lr=LR)
            for epoch in range(EPOCHS):
                loss = train_step(generator, optimizer, p_real, kernel_matrix, BATCH_SIZE)
                if epoch % 100 == 0 or epoch == EPOCHS - 1:
                    print(f"  epoch {epoch:3d}  loss {loss:.6f}")
            torch.save(generator.state_dict(), ckpt_path)

        generator.eval()
        with torch.no_grad():
            q = generator(sample_latent(1))[0]
        metrics = ring_band_metrics(q, centers)
        print(f"  ring/gap metrics: {metrics}")
        rows.append({"sigma": sigma, "ring_mass": metrics["ring_mass"], "gap_mass": metrics["gap_mass"]})

    with open(f"{RESULTS_DIR}/phase7_sigma_resweep_metrics.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["sigma", "ring_mass", "gap_mass"])
        writer.writeheader()
        writer.writerows(rows)


def build_comparison_figure(centers, x_train):
    """Task 1: one combined figure -- real data plus all 5 sigma-trained K=462
    generated distributions -- loading each sigma's saved checkpoint fresh,
    mirroring sweep.py's build_comparison_figure layout."""
    fig, axes = plt.subplots(1, 6, figsize=(24, 4))

    axes[0].scatter(x_train[:, 0], x_train[:, 1], s=10, alpha=0.6)
    axes[0].set_title("Real (circles)")

    for i, sigma in enumerate(SIGMA_GRID, start=1):
        generator = build_naturally_ordered_generator()
        ckpt_path = f"{RESULTS_DIR}/phase7_sigma_{sigma}_checkpoint.pt"
        generator.load_state_dict(torch.load(ckpt_path, map_location="cpu"))
        generator.eval()
        with torch.no_grad():
            q = generator(sample_latent(1))[0]
        points = sample_points(q, centers, n=400)
        axes[i].scatter(points[:, 0], points[:, 1], s=10, alpha=0.6)
        axes[i].set_title(f"sigma={sigma}")

    for ax in axes:
        ax.set_aspect("equal")
        ax.set_xlim(-0.1, 1.1)
        ax.set_ylim(-0.1, 1.1)

    plt.savefig(f"{RESULTS_DIR}/phase7_sigma_resweep_comparison.png")
    plt.close()


def main():
    centers = natural_sorted_centers()
    x_train, _ = load_circles_data()
    p_real = compute_p_real(x_train, centers)

    train_all_sigmas(centers, p_real)
    build_comparison_figure(centers, x_train)


if __name__ == "__main__":
    main()
