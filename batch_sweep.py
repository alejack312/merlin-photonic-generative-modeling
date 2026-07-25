import argparse
import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch

from generator.bin_centers import make_bin_centers
from generator.data import load_circles_data, compute_p_real
from generator.mmd import gaussian_kernel_matrix
from generator.noise import sample_latent
from generator.train import build_generator, train_step
from generator.visualize import sample_points, ring_band_metrics

# sigma=0.1 held fixed: owner-confirmed best result from the SIGMA_GRID sweep
# (04-02). This experiment isolates batch_size as the one variable under test,
# to see whether a less noisy per-step MMD^2 gradient estimate (larger batch)
# helps the generator settle into a ring-shaped distribution instead of the
# plateaued-but-diffuse minimum every sigma converged to.
SIGMA = 0.1
EPOCHS = 300  # held fixed at Phase 3's value, same reasoning as sweep.py
LR = 0.01
BATCH_GRID = [16, 32, 64, 128]
RESULTS_DIR = "results"

# batch=32, sigma=0.1 is exactly Plan 04-02's sweep result already on disk --
# reused instead of retrained.
BASELINE_CKPT = f"{RESULTS_DIR}/phase4_sigma_{SIGMA}_checkpoint.pt"


def train_one_batch(batch_size, centers, p_real):
    ckpt_path = f"{RESULTS_DIR}/phase4_batch_{batch_size}_checkpoint.pt"
    quantum_layer = build_generator()

    if os.path.exists(ckpt_path):
        print(f"--- batch_size={batch_size} (checkpoint already exists, skipping retrain) ---")
        quantum_layer.load_state_dict(torch.load(ckpt_path, map_location="cpu"))
    elif batch_size == 32 and os.path.exists(BASELINE_CKPT):
        print(f"--- batch_size=32 (reusing existing sigma=0.1 baseline checkpoint from 04-02) ---")
        quantum_layer.load_state_dict(torch.load(BASELINE_CKPT, map_location="cpu"))
        torch.save(quantum_layer.state_dict(), ckpt_path)
    else:
        print(f"--- batch_size={batch_size} ---")
        kernel_matrix = gaussian_kernel_matrix(centers, SIGMA)
        optimizer = torch.optim.Adam(quantum_layer.parameters(), lr=LR)  # fresh model per batch_size -- never reused
        for epoch in range(EPOCHS):
            loss = train_step(quantum_layer, optimizer, p_real, kernel_matrix, batch_size)
            if epoch % 100 == 0 or epoch == EPOCHS - 1:
                print(f"  epoch {epoch:3d}  loss {loss:.6f}")
        torch.save(quantum_layer.state_dict(), ckpt_path)

    quantum_layer.eval()
    with torch.no_grad():
        z = sample_latent(1)
        q = quantum_layer(z)[0]
    metrics = ring_band_metrics(q, centers)
    print(f"  ring/gap metrics: {metrics}")
    return metrics


def update_metrics_csv(batch_size, metrics):
    """Resumable, like sweep.py: merge this batch_size's row into whatever's
    already on disk rather than overwriting, so running batch sizes one at a
    time (foreground, per the 04-02 lesson about backgrounded multi-minute
    scripts dying silently) never loses a previous run's result."""
    csv_path = f"{RESULTS_DIR}/phase4_batch_sweep_metrics.csv"
    rows = {}
    if os.path.exists(csv_path):
        with open(csv_path) as f:
            for row in csv.DictReader(f):
                rows[int(row["batch_size"])] = row
    rows[batch_size] = {
        "batch_size": batch_size,
        "ring_mass": metrics["ring_mass"],
        "gap_mass": metrics["gap_mass"],
    }
    with open(csv_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["batch_size", "ring_mass", "gap_mass"])
        writer.writeheader()
        for b in sorted(rows):
            writer.writerow(rows[b])


def build_comparison_figure(centers, x_train):
    fig, axes = plt.subplots(1, len(BATCH_GRID) + 1, figsize=(4 * (len(BATCH_GRID) + 1), 4))

    axes[0].scatter(x_train[:, 0], x_train[:, 1], s=10, alpha=0.6)
    axes[0].set_title("Real (circles)")

    for i, b in enumerate(BATCH_GRID, start=1):
        quantum_layer = build_generator()
        ckpt_path = f"{RESULTS_DIR}/phase4_batch_{b}_checkpoint.pt"
        quantum_layer.load_state_dict(torch.load(ckpt_path, map_location="cpu"))
        quantum_layer.eval()
        with torch.no_grad():
            z = sample_latent(1)
            q = quantum_layer(z)[0]
        points = sample_points(q, centers, n=400)
        axes[i].scatter(points[:, 0], points[:, 1], s=10, alpha=0.6)
        axes[i].set_title(f"batch={b}")

    for ax in axes:
        ax.set_aspect("equal")
        ax.set_xlim(-0.1, 1.1)
        ax.set_ylim(-0.1, 1.1)

    plt.savefig(f"{RESULTS_DIR}/phase4_batch_sweep_comparison.png")
    plt.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Train only this batch size (foreground-safe, one at a time). "
             "Omit to run the full grid sequentially and build the comparison figure.",
    )
    args = parser.parse_args()

    centers = make_bin_centers()
    x_train, _ = load_circles_data()
    p_real = compute_p_real(x_train, centers)

    if args.batch_size is not None:
        metrics = train_one_batch(args.batch_size, centers, p_real)
        update_metrics_csv(args.batch_size, metrics)
    else:
        for b in BATCH_GRID:
            metrics = train_one_batch(b, centers, p_real)
            update_metrics_csv(b, metrics)
        build_comparison_figure(centers, x_train)


if __name__ == "__main__":
    main()
