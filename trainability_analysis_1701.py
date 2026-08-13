"""Phase 17.1 Plan 05: curve-fit analysis for TRAIN-09 (bandwidth sensitivity)
and TRAIN-10 (data-dependent init), against Phase 17's original verdicts.

This is a NEW, separate script from `trainability_analysis.py` (Phase 17's
own, already-shipped output-generator, which `docs/trainability-study.md`
references as-is and which this script does not import from or modify --
per 17.1-RESEARCH.md's explicit instruction). It reuses Plan 17-04's
`trainability.curve_fit.fit_and_compare` UNCHANGED against two new datasets:

TRAIN-09 (bandwidth sensitivity): Plan 17.1-04's 6-sigma-grid CORE sweep
(`results/phase171_train09_{weight1,mixed}_gradient_variance.csv`), fit
per (generator_scope, init_scheme, sigma) -- 24 cells total. Compares
`weight1/uniform` and `mixed/uniform` (the two cells with a definite "exp"
verdict in Phase 17's original CORE data) across the sigma grid against
that original verdict, loaded from `results/phase17_curve_fit_summary.csv`
as the baseline (itself a sigma=0.1 result), producing an explicit
survives/weakens/disappears label per sigma (ROADMAP.md Phase 17.1 success
criterion 2). `small_angle` is fit across the same sigma grid for
completeness (criterion 1 says "both init schemes"), but the
survives/weakens/disappears narrative is scoped to `uniform` only, since
only those cells had an "exp" signature to test for survival
(17.1-RESEARCH.md's explicit scope note).

TRAIN-10 (data-dependent init): Plan 17.1-05 Task 1's new sweep
(`results/phase171_train10_{weight1,mixed}_gradient_variance.csv`,
init_scheme="data_dependent", sigma held at Phase 17's original 0.1), fit
per generator_scope -- 2 cells. Compares each against `small_angle`'s
original "inconclusive" verdict, producing an explicit
clearer-or-still-inconclusive label (ROADMAP.md Phase 17.1 success
criterion 4).

Uses `var` (gradient VARIANCE across draws/tracked-params), not `mean`,
matching `trainability_analysis.py`'s convention and
`docs/iqp-baseline.md`'s formal barren-plateau definition
`Var_theta~D[d_theta L] = O(2^{-alpha*n})`.
"""

import csv
import math
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from trainability.curve_fit import fit_and_compare

RESULTS_DIR = "results"

TRAIN09_CSV_PATHS = {
    "weight1": os.path.join(RESULTS_DIR, "phase171_train09_weight1_gradient_variance.csv"),
    "mixed": os.path.join(RESULTS_DIR, "phase171_train09_mixed_gradient_variance.csv"),
}
TRAIN10_CSV_PATHS = {
    "weight1": os.path.join(RESULTS_DIR, "phase171_train10_weight1_gradient_variance.csv"),
    "mixed": os.path.join(RESULTS_DIR, "phase171_train10_mixed_gradient_variance.csv"),
}
PHASE17_BASELINE_CSV = os.path.join(RESULTS_DIR, "phase17_curve_fit_summary.csv")

TRAIN09_SUMMARY_CSV_PATH = os.path.join(RESULTS_DIR, "phase171_train09_curve_fit_summary.csv")
TRAIN10_SUMMARY_CSV_PATH = os.path.join(RESULTS_DIR, "phase171_train10_curve_fit_summary.csv")
PLOT_PATHS = {
    "weight1": os.path.join(RESULTS_DIR, "phase171_train09_weight1_sigma_sensitivity.png"),
    "mixed": os.path.join(RESULTS_DIR, "phase171_train09_mixed_sigma_sensitivity.png"),
}

GENERATOR_SCOPES = ["weight1", "mixed"]
INIT_SCHEMES = ["small_angle", "uniform"]
SIGMAS = [0.03, 0.1, 0.3, 1.0, 3.0, 9.0]
BASELINE_SIGMA = 0.1  # Phase 17's original, fixed bandwidth -- the baseline CSV's own sigma.

# "weakens" threshold: if the fitted exp decay rate b, or the AIC margin
# (poly_aic - exp_aic, positive = exp favored) drops below this fraction of
# the baseline's value, the exp signature is judged materially weaker even
# though the verdict itself still says "exp". 0.5 (a 50%+ drop in either
# metric) is this script's own documented threshold -- not a value from any
# external convention, chosen to be a clearly "more than noise" cutoff.
MATERIAL_SHRINK_THRESHOLD = 0.5

TRAIN09_SUMMARY_FIELDNAMES = [
    "generator_scope",
    "init_scheme",
    "sigma",
    "bin_spacing",
    "n_min",
    "n_max",
    "verdict",
    "exp_r2",
    "exp_aic",
    "exp_b",
    "poly_r2",
    "poly_aic",
    "survival_vs_baseline",
]
TRAIN10_SUMMARY_FIELDNAMES = [
    "generator_scope",
    "init_scheme",
    "bin_spacing",
    "n_min",
    "n_max",
    "verdict",
    "exp_r2",
    "exp_aic",
    "exp_b",
    "poly_r2",
    "poly_aic",
    "vs_small_angle_verdict",
]


def _load_rows(path):
    if not os.path.exists(path):
        raise FileNotFoundError(path)
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def _exp_b(fit_result):
    """The fitted exponential decay rate (params[1] of a*exp(-b*n)+c), or
    NaN if the exp fit did not converge -- never silently dropped."""
    if fit_result["exp"]["converged"]:
        return float(fit_result["exp"]["params"][1])
    return float("nan")


def load_train09_series(rows, scope, init_scheme, sigma):
    """Return (ns, variances, bin_spacings) for one (scope, init_scheme,
    sigma) cell, sorted by n ascending."""
    by_n = {}
    for r in rows:
        if r["generator_scope"] != scope or r["init_scheme"] != init_scheme:
            continue
        if not math.isclose(float(r["sigma"]), sigma, rel_tol=1e-9, abs_tol=1e-12):
            continue
        n = int(r["n"])
        by_n[n] = (float(r["var"]), float(r["bin_spacing"]))
    ns = sorted(by_n)
    variances = [by_n[n][0] for n in ns]
    bin_spacings = [by_n[n][1] for n in ns]
    return ns, variances, bin_spacings


def load_train10_series(rows, scope):
    by_n = {}
    for r in rows:
        if r["generator_scope"] != scope or r["init_scheme"] != "data_dependent":
            continue
        n = int(r["n"])
        by_n[n] = (float(r["var"]), float(r["bin_spacing"]))
    ns = sorted(by_n)
    variances = [by_n[n][0] for n in ns]
    bin_spacings = [by_n[n][1] for n in ns]
    return ns, variances, bin_spacings


def load_phase17_baseline():
    """Load results/phase17_curve_fit_summary.csv into
    {(generator_scope, init_scheme): {"exp_b", "exp_aic", "poly_aic", "verdict"}}."""
    rows = _load_rows(PHASE17_BASELINE_CSV)
    baseline = {}
    for r in rows:
        exp_params = [float(p) for p in r["exp_params"].split(";")] if r["exp_params"] else None
        baseline[(r["generator_scope"], r["init_scheme"])] = {
            "exp_b": exp_params[1] if exp_params is not None else float("nan"),
            "exp_aic": float(r["exp_aic"]),
            "poly_aic": float(r["poly_aic"]),
            "verdict": r["verdict"],
        }
    return baseline


def classify_survival(baseline_cell, current_fit_result):
    """"survives" / "weakens" / "disappears" for a cell that had a definite
    "exp" verdict (with b > 0) in Phase 17's original CORE data, per
    ROADMAP.md Phase 17.1 success criterion 2. `baseline_cell` is that
    original phase17_curve_fit_summary.csv row's metrics (computed at
    sigma=0.1); `current_fit_result` is this sigma's fit_and_compare output."""
    verdict = current_fit_result["verdict"]
    if verdict != "exp":
        return "disappears"
    b = _exp_b(current_fit_result)
    if not (b > 0):
        # exp technically wins the AIC comparison but is growing, not
        # shrinking, with n -- not a plateau signature, so treat as disappeared.
        return "disappears"

    baseline_b = baseline_cell["exp_b"]
    baseline_margin = baseline_cell["poly_aic"] - baseline_cell["exp_aic"]
    current_margin = current_fit_result["poly"]["aic"] - current_fit_result["exp"]["aic"]

    b_shrunk = baseline_b > 0 and b < MATERIAL_SHRINK_THRESHOLD * baseline_b
    margin_shrunk = (
        baseline_margin > 0 and current_margin < MATERIAL_SHRINK_THRESHOLD * baseline_margin
    )
    if b_shrunk or margin_shrunk:
        return "weakens"
    return "survives"


def run_train09_analysis():
    """Fit every (generator_scope, init_scheme, sigma) cell -- 24 total.

    Returns (summary_rows, fit_cache) where fit_cache maps
    (scope, init_scheme, sigma) -> (ns, variances, fit_result) for plotting.
    """
    baseline = load_phase17_baseline()
    summary_rows = []
    fit_cache = {}
    for scope in GENERATOR_SCOPES:
        rows = _load_rows(TRAIN09_CSV_PATHS[scope])
        for init_scheme in INIT_SCHEMES:
            for sigma in SIGMAS:
                ns, variances, bin_spacings = load_train09_series(rows, scope, init_scheme, sigma)
                if not ns:
                    raise RuntimeError(
                        f"no TRAIN-09 gradient-variance data for {scope}/{init_scheme}/sigma={sigma}"
                    )
                fit_result = fit_and_compare(ns, variances)
                fit_cache[(scope, init_scheme, sigma)] = (ns, variances, fit_result)

                # Only weight1/uniform and mixed/uniform had a definite "exp"
                # verdict in Phase 17's original CORE data -- the two cells
                # ROADMAP.md success criterion 2 asks about. small_angle
                # cells are fit for completeness but get "n/a" here.
                if init_scheme == "uniform":
                    survival = classify_survival(baseline[(scope, init_scheme)], fit_result)
                else:
                    survival = "n/a (no exp verdict in original small_angle baseline)"

                summary_rows.append(
                    {
                        "generator_scope": scope,
                        "init_scheme": init_scheme,
                        "sigma": sigma,
                        "bin_spacing": ";".join(f"{bs:.6g}" for bs in bin_spacings),
                        "n_min": min(ns),
                        "n_max": max(ns),
                        "verdict": fit_result["verdict"],
                        "exp_r2": fit_result["exp"]["r2"],
                        "exp_aic": fit_result["exp"]["aic"],
                        "exp_b": _exp_b(fit_result),
                        "poly_r2": fit_result["poly"]["r2"],
                        "poly_aic": fit_result["poly"]["aic"],
                        "survival_vs_baseline": survival,
                    }
                )
                print(
                    f"[TRAIN-09] {scope}/{init_scheme} sigma={sigma}: verdict={fit_result['verdict']} "
                    f"exp_b={_exp_b(fit_result):.4g} (exp r2={fit_result['exp']['r2']:.4f} "
                    f"aic={fit_result['exp']['aic']:.2f}; poly r2={fit_result['poly']['r2']:.4f} "
                    f"aic={fit_result['poly']['aic']:.2f}) survival={survival}"
                )
    return summary_rows, fit_cache


def run_train10_analysis():
    """Fit every generator_scope's data_dependent cell -- 2 total."""
    summary_rows = []
    for scope in GENERATOR_SCOPES:
        rows = _load_rows(TRAIN10_CSV_PATHS[scope])
        ns, variances, bin_spacings = load_train10_series(rows, scope)
        if not ns:
            raise RuntimeError(f"no TRAIN-10 gradient-variance data for {scope}")
        fit_result = fit_and_compare(ns, variances)

        verdict = fit_result["verdict"]
        if verdict == "exp":
            vs_small_angle = "clearer (exp)"
        elif verdict == "poly":
            vs_small_angle = "clearer (poly)"
        else:
            vs_small_angle = "still inconclusive"

        summary_rows.append(
            {
                "generator_scope": scope,
                "init_scheme": "data_dependent",
                "bin_spacing": ";".join(f"{bs:.6g}" for bs in bin_spacings),
                "n_min": min(ns),
                "n_max": max(ns),
                "verdict": verdict,
                "exp_r2": fit_result["exp"]["r2"],
                "exp_aic": fit_result["exp"]["aic"],
                "exp_b": _exp_b(fit_result),
                "poly_r2": fit_result["poly"]["r2"],
                "poly_aic": fit_result["poly"]["aic"],
                "vs_small_angle_verdict": vs_small_angle,
            }
        )
        print(
            f"[TRAIN-10] {scope}/data_dependent: verdict={verdict} exp_b={_exp_b(fit_result):.4g} "
            f"(exp r2={fit_result['exp']['r2']:.4f} aic={fit_result['exp']['aic']:.2f}; "
            f"poly r2={fit_result['poly']['r2']:.4f} aic={fit_result['poly']['aic']:.2f}) "
            f"vs_small_angle={vs_small_angle}"
        )
    return summary_rows


def save_summary_csv(rows, path, fieldnames):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def save_sigma_sensitivity_plot(scope, fit_cache, path):
    """One figure per scope: x-axis = sigma (log scale), y-axis = fitted
    exp-model decay rate `b` (params[1] of a*exp(-b*n)+c), one line per
    init_scheme. `b` is chosen over the AIC-delta because it directly shows
    whether the exp signature's actual decay strength is shrinking with
    sigma, not just whether the verdict flips at the AIC_DELTA_THRESHOLD=2.0
    boundary -- a verdict can flip from "exp" to "inconclusive" while b is
    still positive and only slightly smaller, or b can nearly vanish while
    the verdict nominally still reads "exp"; plotting b surfaces both cases,
    while an AIC-delta plot would only clearly surface the former. Points
    where the exp fit did not converge (b = NaN) are omitted from the line
    (matplotlib skips NaN by default) rather than plotted as zero.
    """
    fig, ax = plt.subplots(figsize=(7, 5))
    for init_scheme, color in zip(INIT_SCHEMES, ["C0", "C1"]):
        bs = [_exp_b(fit_cache[(scope, init_scheme, sigma)][2]) for sigma in SIGMAS]
        ax.plot(SIGMAS, bs, marker="o", color=color, label=init_scheme)
    ax.set_xscale("log")
    ax.set_xlabel("sigma (MMD kernel bandwidth)")
    ax.set_ylabel("fitted exp decay rate b (a*exp(-b*n)+c)")
    ax.axhline(0, color="gray", linewidth=0.8, linestyle="--")
    ax.set_title(f"{scope}: exp-decay-rate sigma sensitivity (TRAIN-09)")
    ax.legend()
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


if __name__ == "__main__":
    train09_rows, train09_fit_cache = run_train09_analysis()
    save_summary_csv(train09_rows, TRAIN09_SUMMARY_CSV_PATH, TRAIN09_SUMMARY_FIELDNAMES)
    for scope in GENERATOR_SCOPES:
        save_sigma_sensitivity_plot(scope, train09_fit_cache, PLOT_PATHS[scope])

    train10_rows = run_train10_analysis()
    save_summary_csv(train10_rows, TRAIN10_SUMMARY_CSV_PATH, TRAIN10_SUMMARY_FIELDNAMES)

    print()
    print("=== Summary ===")
    print(f"Wrote {TRAIN09_SUMMARY_CSV_PATH} ({len(train09_rows)} rows)")
    print(f"Wrote {TRAIN10_SUMMARY_CSV_PATH} ({len(train10_rows)} rows)")
    print(f"Wrote plots: {', '.join(PLOT_PATHS.values())}")
    print()
    print("TRAIN-09 (weight1/uniform, mixed/uniform survival across the sigma grid):")
    for row in train09_rows:
        if row["init_scheme"] == "uniform":
            print(
                f"  {row['generator_scope']}/uniform sigma={row['sigma']}: "
                f"{row['survival_vs_baseline']}"
            )
    print("TRAIN-10 (clearer-or-still-inconclusive vs. small_angle's original verdict):")
    for row in train10_rows:
        print(f"  {row['generator_scope']}/data_dependent: {row['vs_small_angle_verdict']}")
