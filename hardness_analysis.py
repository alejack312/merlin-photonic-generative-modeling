"""Phase 18 Plan 07: hardness-under-loss plotting/summary script.

Loads Plan 18-06's real measured loss-sweep datasets
(`results/phase18_weight1_loss_sweep.csv`, `results/phase18_mixed_loss_sweep.csv`)
and produces the 3 plots `docs/hardness-under-loss-study.md` embeds: TVD-vs-eta
(weight1, mixed -- against both the lossless reference and both
classically-easy baselines) and anticoncentration alpha(eta) (both scopes on
one figure). Also prints the headline numbers (lowest/highest measured eta,
per scope) that doc transcribes into its results tables.

Mirrors `trainability_analysis.py`'s established shape: module docstring
stating data provenance, `matplotlib.use("Agg")` before importing pyplot, CSV
paths as module constants, one function per plot.

Data provenance: Plan 18-06's real, non-simulated sweep -- weight1 n=2..6,
mixed n=2..4, full 7-point ETA_GRID = [0.99, 0.95, 0.90, 0.80, 0.60, 0.35,
0.05] (`hardness/sweep.py::ETA_GRID`), n_draws=5, seed_base=180814. There is
no literal eta=1.0 row in either CSV -- eta=0.99 is the closest available
near-lossless anchor, not a lossless row itself.
"""

import csv
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

RESULTS_DIR = "results"

CSV_PATHS = {
    "weight1": os.path.join(RESULTS_DIR, "phase18_weight1_loss_sweep.csv"),
    "mixed": os.path.join(RESULTS_DIR, "phase18_mixed_loss_sweep.csv"),
}
PLOT_PATHS = {
    "weight1_tvd": os.path.join(RESULTS_DIR, "phase18_weight1_tvd_plot.png"),
    "mixed_tvd": os.path.join(RESULTS_DIR, "phase18_mixed_tvd_plot.png"),
    "anticoncentration": os.path.join(RESULTS_DIR, "phase18_anticoncentration_plot.png"),
}

TVD_METRICS = [
    ("tvd_to_lossless", "TVD to lossless reference"),
    ("tvd_to_uniform", "TVD to uniform baseline"),
    ("tvd_to_product_marginals", "TVD to product-of-marginals baseline"),
]

NON_NUMERIC_FIELDS = ("generator_scope",)
INT_FIELDS = ("n", "n_draws")


def load_rows(scope):
    """Read one scope's loss-sweep CSV into a list of dict rows, with
    numeric fields cast to float/int. Herald fields are '' in the weight1
    CSV (no herald mechanism there) -- cast to None rather than left as an
    empty string, so downstream formatting never has to special-case '' """
    path = CSV_PATHS[scope]
    with open(path, newline="") as f:
        rows = list(csv.DictReader(f))
    for r in rows:
        for key in list(r.keys()):
            if key in NON_NUMERIC_FIELDS:
                continue
            if r[key] in ("", None):
                r[key] = None
            elif key in INT_FIELDS:
                r[key] = int(r[key])
            else:
                r[key] = float(r[key])
    return rows


def _ns(rows):
    return sorted({r["n"] for r in rows})


def _etas_desc(rows):
    """eta values sorted descending (0.99 -> 0.05) -- eta near 1 (low loss)
    reads first/left, matching the low-loss-to-high-loss left-to-right
    convention every plot in this module uses."""
    return sorted({r["eta"] for r in rows}, reverse=True)


def _series_for_n(rows, n, mean_key, std_key=None):
    n_rows = sorted((r for r in rows if r["n"] == n), key=lambda r: -r["eta"])
    etas = [r["eta"] for r in n_rows]
    means = [r[mean_key] for r in n_rows]
    stds = [r[std_key] for r in n_rows] if std_key else None
    return etas, means, stds


def plot_tvd_figure(scope, rows, path):
    """One subplot per TVD_METRICS entry, one line per n value, x-axis eta
    (descending -- eta near 1/low-loss on the left), y-axis TVD, error bars
    from each metric's own _std column."""
    ns = _ns(rows)
    fig, axes = plt.subplots(1, 3, figsize=(16, 5), sharey=True)
    for ax, (mean_base, title) in zip(axes, TVD_METRICS):
        mean_key, std_key = f"{mean_base}_mean", f"{mean_base}_std"
        for n in ns:
            etas, means, stds = _series_for_n(rows, n, mean_key, std_key)
            ax.errorbar(etas, means, yerr=stds, marker="o", capsize=3, label=f"n={n}")
        ax.set_xlabel("eta (transmittance)")
        ax.set_title(title)
        ax.invert_xaxis()
        ax.grid(alpha=0.3)
    axes[0].set_ylabel("TVD")
    axes[-1].legend(loc="upper left", bbox_to_anchor=(1.02, 1.0))
    fig.suptitle(f"{scope}: TVD vs eta (lossless reference + both classically-easy baselines)")
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def plot_anticoncentration_figure(weight1_rows, mixed_rows, path):
    """alpha_mean vs eta, both scopes on one figure -- solid lines for
    weight1, dashed for mixed -- one line per n per scope, plus a horizontal
    alpha=1 reference line (uniform / maximally-anticoncentrated)."""
    fig, ax = plt.subplots(figsize=(9, 6))
    for n in _ns(weight1_rows):
        etas, means, stds = _series_for_n(weight1_rows, n, "alpha_mean", "alpha_std")
        ax.errorbar(etas, means, yerr=stds, marker="o", linestyle="-", capsize=3, label=f"weight1 n={n}")
    for n in _ns(mixed_rows):
        etas, means, stds = _series_for_n(mixed_rows, n, "alpha_mean", "alpha_std")
        ax.errorbar(etas, means, yerr=stds, marker="s", linestyle="--", capsize=3, label=f"mixed n={n}")
    ax.axhline(1.0, color="gray", linestyle=":", label="alpha=1 (uniform)")
    ax.set_yscale("log")
    ax.set_xlabel("eta (transmittance)")
    ax.set_ylabel("alpha (anticoncentration parameter)")
    ax.invert_xaxis()
    ax.set_title("Anticoncentration alpha(eta), both generator scopes")
    ax.grid(alpha=0.3)
    ax.legend(loc="upper left", bbox_to_anchor=(1.02, 1.0), fontsize=8)
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)


def print_headline_summary(scope, rows):
    """Print the headline numbers docs/hardness-under-loss-study.md
    transcribes: lowest measured eta and highest measured eta (this phase's
    grid has no literal eta=1.0 row -- eta=0.99 is the closest available
    near-lossless anchor, stated as such, not implied to be lossless), per
    n, for TVD-to-lossless / TVD-to-each-baseline / alpha and (mixed only)
    herald_success_rate."""
    etas = _etas_desc(rows)
    lo, hi = etas[-1], etas[0]
    print(f"\n=== {scope}: headline numbers (lowest eta={lo}, highest eta={hi}) ===")
    for n in _ns(rows):
        for eta in (hi, lo):
            row = next(r for r in rows if r["n"] == n and r["eta"] == eta)
            line = (
                f"n={n} eta={eta}: tvd_lossless={row['tvd_to_lossless_mean']:.4f} "
                f"tvd_uniform={row['tvd_to_uniform_mean']:.4f} "
                f"tvd_product_marginals={row['tvd_to_product_marginals_mean']:.4f} "
                f"alpha={row['alpha_mean']:.4f}"
            )
            if scope == "mixed":
                line += f" herald_success_rate={row['herald_success_rate_mean']:.4f}"
            print(line)


if __name__ == "__main__":
    weight1_rows = load_rows("weight1")
    mixed_rows = load_rows("mixed")

    plot_tvd_figure("weight1", weight1_rows, PLOT_PATHS["weight1_tvd"])
    plot_tvd_figure("mixed", mixed_rows, PLOT_PATHS["mixed_tvd"])
    plot_anticoncentration_figure(weight1_rows, mixed_rows, PLOT_PATHS["anticoncentration"])

    print_headline_summary("weight1", weight1_rows)
    print_headline_summary("mixed", mixed_rows)

    print(f"\nWrote {len(PLOT_PATHS)} plots: {', '.join(PLOT_PATHS.values())}")
