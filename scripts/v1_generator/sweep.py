import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch

from merlin_iqp.generator.bin_centers import make_bin_centers
from merlin_iqp.generator.data import load_circles_data, compute_p_real
from merlin_iqp.generator.mmd import SIGMA_GRID, gaussian_kernel_matrix
from merlin_iqp.generator.noise import sample_latent
from merlin_iqp.generator.train import build_generator, train_step
from merlin_iqp.generator.visualize import sample_points, ring_band_metrics

EPOCHS = 300  # held fixed at Phase 3's value -- isolates sigma as the one variable
LR = 0.01     # under test (04-CONTEXT.md)
BATCH_SIZE = 32
RESULTS_DIR = "results/v1_generator"


def train_all_sigmas(centers, p_real):
    """Task 1: retrain a fresh generator per SIGMA_GRID value, save each
    checkpoint, and record ring/gap-band metrics for each.

    Resumable: if a sigma's checkpoint already exists on disk (e.g. a prior
    run of this script was interrupted partway through the sweep), that
    sigma is NOT retrained -- its already-completed, already-fresh-QuantumLayer
    checkpoint is loaded instead, only to recompute its metrics row. This
    still satisfies "all 5 retrained from a fresh QuantumLayer each" (each
    surviving checkpoint was produced by exactly one full fresh-model training
    run); it just avoids redundantly re-running sigmas that already finished
    training successfully before an interruption."""
    rows = []
    for sigma in SIGMA_GRID:
        ckpt_path = f"{RESULTS_DIR}/phase4_sigma_{sigma}_checkpoint.pt"
        quantum_layer = build_generator()

        if os.path.exists(ckpt_path):
            print(f"--- sigma={sigma} (checkpoint already exists, skipping retrain) ---")
            quantum_layer.load_state_dict(torch.load(ckpt_path, map_location="cpu"))
        else:
            print(f"--- sigma={sigma} ---")
            kernel_matrix = gaussian_kernel_matrix(centers, sigma)
            optimizer = torch.optim.Adam(quantum_layer.parameters(), lr=LR)  # fresh model per sigma -- never reused

            for epoch in range(EPOCHS):
                loss = train_step(quantum_layer, optimizer, p_real, kernel_matrix, BATCH_SIZE)
                if epoch % 100 == 0 or epoch == EPOCHS - 1:
                    print(f"  epoch {epoch:3d}  loss {loss:.6f}")

            torch.save(quantum_layer.state_dict(), ckpt_path)

        quantum_layer.eval()
        with torch.no_grad():
            z = sample_latent(1)
            q = quantum_layer(z)[0]
        metrics = ring_band_metrics(q, centers)
        print(f"  ring/gap metrics: {metrics}")
        rows.append({"sigma": sigma, "ring_mass": metrics["ring_mass"], "gap_mass": metrics["gap_mass"]})

    with open(f"{RESULTS_DIR}/phase4_sweep_metrics.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["sigma", "ring_mass", "gap_mass"])
        writer.writeheader()
        writer.writerows(rows)


def build_comparison_figure(centers, x_train):
    """Task 2: one combined figure -- real data plus all 5 sigma-trained
    generated distributions -- loading each sigma's saved checkpoint fresh,
    so the owner reviews all 5 together rather than one at a time
    (04-CONTEXT.md locked process)."""
    fig, axes = plt.subplots(1, 6, figsize=(24, 4))

    axes[0].scatter(x_train[:, 0], x_train[:, 1], s=10, alpha=0.6)
    axes[0].set_title("Real (circles)")

    for i, sigma in enumerate(SIGMA_GRID, start=1):
        quantum_layer = build_generator()
        ckpt_path = f"{RESULTS_DIR}/phase4_sigma_{sigma}_checkpoint.pt"
        quantum_layer.load_state_dict(torch.load(ckpt_path, map_location="cpu"))
        quantum_layer.eval()
        with torch.no_grad():
            z = sample_latent(1)
            q = quantum_layer(z)[0]
        points = sample_points(q, centers, n=400)
        axes[i].scatter(points[:, 0], points[:, 1], s=10, alpha=0.6)
        axes[i].set_title(f"sigma={sigma}")

    for ax in axes:
        ax.set_aspect("equal")
        ax.set_xlim(-0.1, 1.1)
        ax.set_ylim(-0.1, 1.1)

    plt.savefig(f"{RESULTS_DIR}/phase4_sweep_comparison.png")
    plt.close()


def main():
    centers = make_bin_centers()
    x_train, _ = load_circles_data()
    p_real = compute_p_real(x_train, centers)

    train_all_sigmas(centers, p_real)
    build_comparison_figure(centers, x_train)


if __name__ == "__main__":
    main()
