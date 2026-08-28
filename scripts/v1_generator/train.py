import csv
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch

from merlin_iqp.generator.bin_centers import make_bin_centers
from merlin_iqp.generator.data import load_circles_data, compute_p_real
from merlin_iqp.generator.mmd import gaussian_kernel_matrix
from merlin_iqp.generator.train import build_generator, train_step, decreasing_trend_check

SIGMA = 0.1
BATCH_SIZE = 32
EPOCHS = 300
# lr=0.01 (the quickstart.py/theta-init-scale-informed starting point, 03-RESEARCH.md
# Open Question 2) produced a decreasing_trend_check passed=True result on the first
# attempt (see 03-01-SUMMARY.md for the actual slope/relative_drop numbers) -- kept
# as-is, the escalation to lr=0.05/0.1 named in 03-RESEARCH.md was not needed.
LR = 0.01

RESULTS_DIR = "results/v1_generator"


def main():
    # Build once, before the loop -- QuantumLayer and Adam optimizer are never
    # rebuilt inside the loop (Pattern 1, 03-RESEARCH.md): rebuilding either
    # would silently re-randomize thetas / reset optimizer state every step
    # while still "running without errors".
    centers = make_bin_centers()
    x_train, _ = load_circles_data()
    p_real = compute_p_real(x_train, centers)
    kernel_matrix = gaussian_kernel_matrix(centers, SIGMA)
    quantum_layer = build_generator()
    optimizer = torch.optim.Adam(quantum_layer.parameters(), lr=LR)

    losses = []
    for epoch in range(EPOCHS):
        loss = train_step(quantum_layer, optimizer, p_real, kernel_matrix, BATCH_SIZE)
        losses.append(loss)
        if epoch % 20 == 0 or epoch == EPOCHS - 1:
            print(f"epoch {epoch:3d}  loss {loss:.6f}")

    os.makedirs(RESULTS_DIR, exist_ok=True)

    with open(os.path.join(RESULTS_DIR, "phase3_loss_history.csv"), "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["epoch", "loss"])
        for epoch, loss in enumerate(losses):
            writer.writerow([epoch, loss])

    plt.figure()
    plt.plot(range(EPOCHS), losses)
    plt.xlabel("epoch")
    plt.ylabel("loss (mean per-sample MMD^2)")
    plt.title("Phase 3 training loss")
    plt.savefig(os.path.join(RESULTS_DIR, "phase3_loss_curve.png"))
    plt.close()

    torch.save(quantum_layer.state_dict(), os.path.join(RESULTS_DIR, "phase3_checkpoint.pt"))

    result = decreasing_trend_check(losses)
    print("decreasing_trend_check:", result)
    verdict = "PASS" if result["passed"] else "FAIL"
    print(f"GEN-06 decreasing-trend check: {verdict}")


if __name__ == "__main__":
    main()
