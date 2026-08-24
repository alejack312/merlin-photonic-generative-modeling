"""Phase 5, Task 2: timed retrain to capture wall-clock training time and
parameter count -- no prior script in this repo recorded these
(05-RESEARCH.md Pitfall 3).

Reuses natural_order_train.py's exact hyperparameters and construction.
Writes to a SCRATCH checkpoint path -- never touches
results/phase4_natural_checkpoint.pt.

Resumable, like natural_order_train.py: if the scratch checkpoint already
exists, skip retraining and load it instead; the wall-clock number reported
is then read back from results/phase5_training_cost.csv (the CSV written on
the original run), never fabricated.
"""

import csv
import os
import time

import torch

from merlin_iqp.generator.data import load_circles_data, compute_p_real
from merlin_iqp.generator.mmd import gaussian_kernel_matrix
from merlin_iqp.generator.naturally_ordered_generator import (
    build_naturally_ordered_generator,
    natural_sorted_centers,
)
from merlin_iqp.generator.noise import sample_latent
from merlin_iqp.generator.train import train_step
from merlin_iqp.generator.visualize import ring_band_metrics

SIGMA = 0.1
BATCH_SIZE = 32
EPOCHS = 300
LR = 0.01
RESULTS_DIR = "results"
TIMED_CKPT = f"{RESULTS_DIR}/phase5_timed_checkpoint.pt"
COST_CSV = f"{RESULTS_DIR}/phase5_training_cost.csv"

# Phase 4's documented values for the sanity check (results/phase4_summary.md).
PHASE4_RING_MASS = 0.691
PHASE4_GAP_MASS = 0.048
SANITY_TOL = 0.05


def main():
    centers = natural_sorted_centers()
    X_train, _ = load_circles_data()
    p_real = compute_p_real(X_train, centers)
    kernel_matrix = gaussian_kernel_matrix(centers, SIGMA)

    generator = build_naturally_ordered_generator()

    if os.path.exists(TIMED_CKPT):
        print("scratch checkpoint already exists, skipping retrain")
        generator.load_state_dict(torch.load(TIMED_CKPT, map_location="cpu"))
        wall_clock_seconds = None
        if os.path.exists(COST_CSV):
            with open(COST_CSV, newline="") as f:
                row = next(csv.DictReader(f))
                wall_clock_seconds = row["wall_clock_seconds"]
                print(
                    f"reporting wall_clock_seconds from prior run's CSV: "
                    f"{wall_clock_seconds} (not freshly measured this run)"
                )
        if wall_clock_seconds is None:
            print("no prior wall_clock_seconds available -- reporting NA, not fabricating")
            wall_clock_seconds = ""
    else:
        optimizer = torch.optim.Adam(generator.parameters(), lr=LR)
        start = time.time()
        for epoch in range(EPOCHS):
            loss = train_step(generator, optimizer, p_real, kernel_matrix, BATCH_SIZE)
            if epoch % 50 == 0 or epoch == EPOCHS - 1:
                print(f"  epoch {epoch:3d}  loss {loss:.6f}")
        end = time.time()
        wall_clock_seconds = end - start
        torch.save(generator.state_dict(), TIMED_CKPT)
        print(f"wall_clock_seconds (fresh, measured): {wall_clock_seconds:.2f}")

    param_count = sum(p.numel() for p in generator.parameters())

    generator.eval()
    with torch.no_grad():
        q = generator(sample_latent(1))[0]
    metrics = ring_band_metrics(q, centers)
    final_ring_mass = metrics["ring_mass"]
    final_gap_mass = metrics["gap_mass"]

    print(f"param_count: {param_count}")
    print(f"final ring_mass={final_ring_mass:.4f}  gap_mass={final_gap_mass:.4f}")
    if (
        abs(final_ring_mass - PHASE4_RING_MASS) > SANITY_TOL
        or abs(final_gap_mass - PHASE4_GAP_MASS) > SANITY_TOL
    ):
        print(
            f"NOTE: final ring_mass/gap_mass differ from Phase 4's documented "
            f"({PHASE4_RING_MASS}/{PHASE4_GAP_MASS}) by more than {SANITY_TOL} -- "
            f"this is a fresh stochastic run, not necessarily a structural problem, "
            f"but worth a look."
        )
    else:
        print("sanity check OK: within stochastic run-to-run variance of Phase 4's documented values")

    with open(COST_CSV, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            "wall_clock_seconds", "param_count", "epochs", "batch_size",
            "final_ring_mass", "final_gap_mass",
        ])
        writer.writerow([
            wall_clock_seconds, param_count, EPOCHS, BATCH_SIZE,
            final_ring_mass, final_gap_mass,
        ])


if __name__ == "__main__":
    main()
