"""Phase 4, option 3: retrain at the owner-confirmed-best hyperparameters, but
under a corrected index<->spatial-bin correspondence.

Two things change versus every prior Phase 4 run, and nothing else:
  1. K = 462 (a 21x22 grid) instead of 400, matching the circuit's natural
     output width exactly -- so MerLin's ModGrouping modulo fold never runs.
  2. Output columns are reordered by Fock-state "smoothness" rank and paired
     with bin centers sorted by ascending radius, replacing the arbitrary
     combinatorics-vs-raster labeling.

sigma=0.1, batch=32 are held fixed (owner-confirmed best from 04-02 and the
batch sweep), so the ordering fix is the single variable under test.

Resumable: re-running after an interruption reuses the checkpoint on disk rather
than retraining (backgrounded multi-minute scripts have died silently in this
environment before -- run this in the foreground).
"""

import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch

from generator.bin_centers import make_bin_centers
from generator.data import load_circles_data, compute_p_real
from generator.mmd import gaussian_kernel_matrix
from generator.naturally_ordered_generator import (
    build_naturally_ordered_generator,
    natural_sorted_centers,
)
from generator.noise import sample_latent
from generator.train import build_generator, train_step
from generator.visualize import sample_points, ring_band_metrics

SIGMA = 0.1
BATCH_SIZE = 32
EPOCHS = 300
LR = 0.01
RESULTS_DIR = "results"

CKPT = f"{RESULTS_DIR}/phase4_natural_checkpoint.pt"
# The documented best 400-wide result, used as the comparison panel.
BASELINE_CKPT = f"{RESULTS_DIR}/phase4_batch_32_checkpoint.pt"


def train():
    centers = natural_sorted_centers()
    x_train, _ = load_circles_data()
    p_real = compute_p_real(x_train, centers)

    generator = build_naturally_ordered_generator()
    loss_history = []

    if os.path.exists(CKPT):
        print("checkpoint already exists, skipping retrain")
        generator.load_state_dict(torch.load(CKPT, map_location="cpu"))
    else:
        kernel_matrix = gaussian_kernel_matrix(centers, SIGMA)
        optimizer = torch.optim.Adam(generator.parameters(), lr=LR)
        for epoch in range(EPOCHS):
            loss = train_step(generator, optimizer, p_real, kernel_matrix, BATCH_SIZE)
            loss_history.append(loss)
            if epoch % 50 == 0 or epoch == EPOCHS - 1:
                print(f"  epoch {epoch:3d}  loss {loss:.6f}")
        torch.save(generator.state_dict(), CKPT)
        with open(f"{RESULTS_DIR}/phase4_natural_loss_history.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["epoch", "loss"])
            for e, l in enumerate(loss_history):
                writer.writerow([e, l])

    generator.eval()
    with torch.no_grad():
        q = generator(sample_latent(1))[0]
    return centers, p_real, q, x_train


def write_metrics(metrics):
    with open(f"{RESULTS_DIR}/phase4_natural_metrics.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["variant", "sigma", "batch_size", "K", "ring_mass", "gap_mass"])
        writer.writeheader()
        writer.writerow({
            "variant": "natural_order",
            "sigma": SIGMA,
            "batch_size": BATCH_SIZE,
            "K": 462,
            "ring_mass": metrics["ring_mass"],
            "gap_mass": metrics["gap_mass"],
        })


def build_comparison_figure(centers, q, x_train):
    fig, axes = plt.subplots(1, 3, figsize=(12, 4))

    axes[0].scatter(x_train[:, 0], x_train[:, 1], s=10, alpha=0.6)
    axes[0].set_title("Real (circles)")

    if os.path.exists(BASELINE_CKPT):
        old_centers = make_bin_centers()
        old = build_generator()
        old.load_state_dict(torch.load(BASELINE_CKPT, map_location="cpu"))
        old.eval()
        with torch.no_grad():
            old_q = old(sample_latent(1))[0]
        old_points = sample_points(old_q, old_centers, n=400)
        axes[1].scatter(old_points[:, 0], old_points[:, 1], s=10, alpha=0.6)
    axes[1].set_title("Prior best (K=400, sigma=0.1, batch=32)")

    points = sample_points(q, centers, n=400)
    axes[2].scatter(points[:, 0], points[:, 1], s=10, alpha=0.6)
    axes[2].set_title("Natural order (K=462)")

    for ax in axes:
        ax.set_aspect("equal")
        ax.set_xlim(-0.1, 1.1)
        ax.set_ylim(-0.1, 1.1)

    plt.tight_layout()
    plt.savefig(f"{RESULTS_DIR}/phase4_natural_comparison.png")
    plt.close()


def build_rank_profile_figure(p_real, q):
    """Tests the design premise directly, in the rank domain the model actually
    sees: does p_real become two contiguous bands once bins are radius-sorted,
    and does q approximate that shape?"""
    plt.figure(figsize=(10, 4))
    plt.plot(p_real.numpy(), label="p_real", linewidth=1.2)
    plt.plot(q.numpy(), label="q (trained)", linewidth=1.2)
    plt.xlabel("rank index (0 = smallest radius from (0.5, 0.5))")
    plt.ylabel("probability mass")
    plt.title("Rank-domain profile, radius-sorted bins")
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"{RESULTS_DIR}/phase4_natural_rank_profile.png")
    plt.close()


def main():
    centers, p_real, q, x_train = train()
    metrics = ring_band_metrics(q, centers)
    print(f"ring/gap metrics: {metrics}")
    print("baseline for comparison (K=400, sigma=0.1, batch=32): ring_mass=0.609, gap_mass=0.035")
    write_metrics(metrics)
    build_comparison_figure(centers, q, x_train)
    build_rank_profile_figure(p_real, q)


if __name__ == "__main__":
    main()
