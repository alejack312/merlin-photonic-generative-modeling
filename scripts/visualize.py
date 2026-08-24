import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch

from merlin_iqp.generator.bin_centers import make_bin_centers
from merlin_iqp.generator.data import load_circles_data, compute_p_real
from merlin_iqp.generator.noise import sample_latent
from merlin_iqp.generator.train import build_generator
from merlin_iqp.generator.visualize import sample_points, ring_band_metrics

CHECKPOINT_PATH = "results/phase3_checkpoint.pt"
SIGMA = 0.1  # the value train.py used to produce this checkpoint -- the checkpoint
             # file itself carries no sigma/epoch metadata (04-RESEARCH.md Pitfall 1),
             # this is an out-of-band fact from train.py's SIGMA constant.
RESULTS_DIR = "results"


def main():
    centers = make_bin_centers()
    x_train, _ = load_circles_data()
    p_real = compute_p_real(x_train, centers)

    quantum_layer = build_generator()  # input_size=10, output_size=400 -- MUST match
                                        # training-time defaults (04-RESEARCH.md Pitfall 2)
    quantum_layer.load_state_dict(torch.load(CHECKPOINT_PATH, map_location="cpu"))
    quantum_layer.eval()

    with torch.no_grad():
        z = sample_latent(1)
        q = quantum_layer(z)[0]  # (400,) analytic probability vector

    points = sample_points(q, centers, n=400)

    # Scatter comparison: real | generated
    fig, axes = plt.subplots(1, 2, figsize=(10, 5))
    axes[0].scatter(x_train[:, 0], x_train[:, 1], s=10, alpha=0.6)
    axes[0].set_title("Real (circles)")
    axes[1].scatter(points[:, 0], points[:, 1], s=10, alpha=0.6)
    axes[1].set_title(f"Generated (sampled, sigma={SIGMA})")
    for ax in axes:
        ax.set_aspect("equal")
        ax.set_xlim(-0.1, 1.1)
        ax.set_ylim(-0.1, 1.1)
    plt.savefig(f"{RESULTS_DIR}/phase4_scatter_comparison.png")
    plt.close()

    # Heatmap comparison: real p_real | generated q -- scatter-based (not imshow),
    # avoids the verified x/y orientation pitfall (04-RESEARCH.md Pitfall 3)
    fig, axes = plt.subplots(1, 2, figsize=(11, 5))
    sc0 = axes[0].scatter(centers[:, 0], centers[:, 1], c=p_real, cmap="viridis", s=40)
    axes[0].set_title("Real (p_real heatmap)")
    sc1 = axes[1].scatter(centers[:, 0], centers[:, 1], c=q.detach(), cmap="viridis", s=40)
    axes[1].set_title(f"Generated (q heatmap, sigma={SIGMA})")
    for ax, sc in zip(axes, [sc0, sc1]):
        ax.set_aspect("equal")
        plt.colorbar(sc, ax=ax)
    plt.savefig(f"{RESULTS_DIR}/phase4_heatmap_comparison.png")
    plt.close()

    # Ring/gap-band metric: exact q (deterministic, primary) and sampled counts
    # (secondary cross-check matching CONTEXT.md's "% of sampled points" framing)
    exact_metrics = ring_band_metrics(q.detach(), centers)
    idx = torch.multinomial(q.detach(), num_samples=400, replacement=True)
    counts = torch.bincount(idx, minlength=centers.shape[0]).float()
    sampled_metrics = ring_band_metrics(counts, centers)

    print(f"sigma={SIGMA} ring/gap metrics (exact q):    {exact_metrics}")
    print(f"sigma={SIGMA} ring/gap metrics (sampled 400): {sampled_metrics}")


if __name__ == "__main__":
    main()
