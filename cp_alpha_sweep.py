import csv

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from iqp_photonic_encoding import photonic_cp_iqp_distribution

# Phase 16 Plan 02 (ARB-08): a denser 16-point sweep of CP(alpha)'s measured
# success probability across [0, 2*pi), extending Phase 15's existing
# 4-point test_cp_pipeline_success_probability_vs_alpha_table
# (tests/test_iqp_photonic_encoding.py:819-847) into a validated, plotted
# dataset. Locked at the SAME configuration as that table: n=2, (i,j)=(0,1),
# thetas=[0.0, 0.0] -- a direct extension, not a new configuration.
#
# Every one of the 16 measured points is asserted against the closed-form
# p_success(alpha) = 1/sigma_max(alpha)**4 (docs/iqp-photonic-encoding.md's
# Closed-Form Success Probability section) to within 1e-6 -- this script
# produces a validated dataset, not a decorative plot.

RESULTS_DIR = "results"

NON_TRIVIAL_ALPHAS_VALIDATED = [np.pi / 6, np.pi / 3, 2 * np.pi / 5, np.pi]  # Phase 15's 4 points

# 12 additional uniformly-spaced points across [0, 2*pi), offset by half a
# step (pi/12) so none collide with the 4 already-validated values above
# (an un-offset 12-point grid would land exactly on pi/6, pi/3, and pi).
_OFFSET = np.pi / 12
_UNIFORM_12 = [_OFFSET + k * (2 * np.pi / 12) for k in range(12)]

ALPHAS = sorted(NON_TRIVIAL_ALPHAS_VALIDATED + _UNIFORM_12)
assert len(ALPHAS) == 16, f"expected 16 alpha points, got {len(ALPHAS)}"
assert len({round(a, 9) for a in ALPHAS}) == 16, "duplicate alpha values in sweep grid"


def sigma_max(alpha):
    a = np.sqrt(complex(np.exp(1j * alpha) - 1))
    return max(abs(1 + a), abs(1 - a))


def run_sweep():
    n, i, j = 2, 0, 1
    thetas = [0.0, 0.0]

    rows = []
    for alpha in ALPHAS:
        _, _, postselect_failure_prob = photonic_cp_iqp_distribution(n, i, j, thetas, float(alpha))
        measured = 1.0 - postselect_failure_prob
        expected = 1.0 / sigma_max(alpha) ** 4
        assert np.isclose(measured, expected, atol=1e-6), (
            f"alpha={alpha}: measured {measured} vs closed-form {expected}"
        )
        rows.append(
            {
                "alpha": alpha,
                "measured_success_prob": measured,
                "closed_form_success_prob": expected,
            }
        )
        print(f"  alpha={alpha:.6f}  measured={measured:.8f}  closed-form={expected:.8f}")

    return rows


def save_csv(rows, path):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["alpha", "measured_success_prob", "closed_form_success_prob"])
        writer.writeheader()
        writer.writerows(rows)


def save_plot(rows, path):
    dense_alphas = np.linspace(0, 2 * np.pi, 200, endpoint=False)
    dense_curve = [1.0 / sigma_max(a) ** 4 for a in dense_alphas]

    measured_alphas = [r["alpha"] for r in rows]
    measured_probs = [r["measured_success_prob"] for r in rows]

    plt.figure(figsize=(8, 5))
    plt.plot(dense_alphas, dense_curve, label="closed-form $1/\\sigma_{max}(\\alpha)^4$", color="C0")
    plt.scatter(measured_alphas, measured_probs, label="measured (16 points)", color="C1", zorder=3)
    plt.xlabel("alpha (radians)")
    plt.ylabel("success probability")
    plt.title("CP(alpha) success probability vs alpha (Phase 16 denser sweep)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(path)
    plt.close()


if __name__ == "__main__":
    rows = run_sweep()
    save_csv(rows, f"{RESULTS_DIR}/phase16_alpha_sweep.csv")
    save_plot(rows, f"{RESULTS_DIR}/phase16_alpha_sweep.png")
    print("All 16 points matched the closed-form prediction to within 1e-6.")
    print(f"Saved {RESULTS_DIR}/phase16_alpha_sweep.csv and {RESULTS_DIR}/phase16_alpha_sweep.png")
