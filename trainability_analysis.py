"""Phase 17 Plan 07: curve-fit analysis, baseline cross-reference, and plots.

Closes out Phase 17 by applying Plan 17-04's poly-vs-exponential model
comparison (`trainability.curve_fit.fit_and_compare`) to the real
gradient-variance-vs-n data Plan 17-06 measured, for all four
(generator_scope, init_scheme) combinations, then cross-references the
result against `docs/iqp-baseline.md`'s qubit-side empirical plateau rule
(TRAIN-07). Writes `results/phase17_curve_fit_summary.csv` and two plots.

Data source: `results/phase17_weight1_gradient_variance.csv` and
`results/phase17_mixed_gradient_variance.csv` (Plan 17-06's CORE datasets,
complete and final). If the STRETCH background job launched during Plan
17-06 (n=7 weight-1, n=6 mixed) has produced
`results/phase17_weight1_gradient_variance_stretch.csv` /
`results/phase17_mixed_gradient_variance_stretch.csv` by the time this
script runs, those extra n-values are merged in automatically -- more data
points only strengthen the curve fit. Missing/partial stretch files are not
an error; this is an explicitly authorized outcome (see Plan 17-06's
SUMMARY.md).

Uses `var` (gradient VARIANCE across draws), not `mean`, per
`docs/iqp-baseline.md`'s formal barren-plateau definition
`Var_theta~D[d_theta L] = O(2^{-alpha*n})`.
"""

import csv
import os

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from trainability.curve_fit import exp_model, fit_and_compare, poly_model

RESULTS_DIR = "results"

CSV_PATHS = {
    "weight1": os.path.join(RESULTS_DIR, "phase17_weight1_gradient_variance.csv"),
    "mixed": os.path.join(RESULTS_DIR, "phase17_mixed_gradient_variance.csv"),
}
STRETCH_CSV_PATHS = {
    "weight1": os.path.join(RESULTS_DIR, "phase17_weight1_gradient_variance_stretch.csv"),
    "mixed": os.path.join(RESULTS_DIR, "phase17_mixed_gradient_variance_stretch.csv"),
}
PLOT_PATHS = {
    "weight1": os.path.join(RESULTS_DIR, "phase17_weight1_curve_fit.png"),
    "mixed": os.path.join(RESULTS_DIR, "phase17_mixed_curve_fit.png"),
}
SUMMARY_CSV_PATH = os.path.join(RESULTS_DIR, "phase17_curve_fit_summary.csv")

GENERATOR_SCOPES = ["weight1", "mixed"]
INIT_SCHEMES = ["small_angle", "uniform"]

SUMMARY_FIELDNAMES = [
    "generator_scope",
    "init_scheme",
    "n_min",
    "n_max",
    "n_points",
    "exp_params",
    "exp_r2",
    "exp_aic",
    "poly_params",
    "poly_r2",
    "poly_aic",
    "verdict",
    "baseline_rule_prediction",
    "agrees_with_baseline_rule",
]


def _load_rows(path):
    """Read a gradient-variance CSV into a list of dict rows. Missing/absent
    files (e.g. a not-yet-complete STRETCH CSV) return an empty list rather
    than raising -- per Plan 17-06's explicitly authorized outcome."""
    if not os.path.exists(path):
        return []
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


def load_series(generator_scope, init_scheme):
    """Return (ns, variances) for one (generator_scope, init_scheme) cell,
    sorted by n ascending, merging CORE + STRETCH rows if the STRETCH CSV
    exists. CORE rows take priority on any n collision (CORE is listed
    first, so its rows populate the dict before STRETCH's would)."""
    rows = _load_rows(CSV_PATHS[generator_scope]) + _load_rows(STRETCH_CSV_PATHS[generator_scope])
    by_n = {}
    for r in rows:
        if r["generator_scope"] != generator_scope or r["init_scheme"] != init_scheme:
            continue
        n = int(r["n"])
        if n not in by_n:
            by_n[n] = float(r["var"])
    ns = sorted(by_n)
    variances = [by_n[n] for n in ns]
    return ns, variances


def baseline_rule_prediction(init_scheme, ns):
    """Apply docs/iqp-baseline.md's empirical rule directly to this
    project's own setting:

        plateau if init_scheme == "small_angle"
        or plateau if init_scheme == "uniform" and max(ns) >= 6

    The rule's original `not complete_graph_like` escape-hatch clause is a
    qubit-side structural notion this project's photonic weight-1/mixed
    circuits have no clean mapping onto -- this project's circuits are not
    naturally "complete-graph-like" in that sense, so the clause is treated
    as inapplicable here rather than silently assumed away. This
    mapping-ambiguity is stated explicitly in docs/trainability-study.md,
    not just in this comment.
    """
    if init_scheme == "small_angle":
        return "plateau"
    if init_scheme == "uniform" and max(ns) >= 6:
        return "plateau"
    return "no_plateau"


def fit_verdict_to_plateau_label(fit_result):
    """Map fit_and_compare's exp/poly/inconclusive verdict onto a
    plateau/no_plateau label for comparison against the baseline rule.

    "exp" only counts as a plateau signature if the fitted exponential is
    actually decaying with n (b > 0 in a*exp(-b*n)+c) -- an exp-model win
    with b < 0 (growing, not shrinking, with n) is NOT a shrinking-with-n
    signature consistent with a plateau, even though the exp model
    statistically outfit poly; that distinction is preserved rather than
    silently treating "exp wins" as always meaning "plateau".
    """
    verdict = fit_result["verdict"]
    if verdict == "exp":
        b = fit_result["exp"]["params"][1]
        return "plateau" if b > 0 else "no_plateau (exp fit growing, not shrinking)"
    if verdict == "poly":
        return "no_plateau"
    return "inconclusive"


def _fmt_params(params):
    if params is None:
        return ""
    return ";".join(f"{p:.6g}" for p in params)


def run_analysis():
    """Run fit_and_compare for all 4 (generator_scope, init_scheme) cells.

    Returns (summary_rows, fit_cache) where fit_cache maps
    (scope, init_scheme) -> (ns, variances, fit_result) for plotting.
    """
    summary_rows = []
    fit_cache = {}
    for scope in GENERATOR_SCOPES:
        for init_scheme in INIT_SCHEMES:
            ns, variances = load_series(scope, init_scheme)
            if not ns:
                raise RuntimeError(f"no gradient-variance data found for {scope}/{init_scheme}")
            fit_result = fit_and_compare(ns, variances)
            fit_cache[(scope, init_scheme)] = (ns, variances, fit_result)

            rule_pred = baseline_rule_prediction(init_scheme, ns)
            fit_label = fit_verdict_to_plateau_label(fit_result)
            if fit_label == "inconclusive":
                agreement = "inconclusive"
            else:
                agreement = "agree" if fit_label == rule_pred else "disagree"

            summary_rows.append(
                {
                    "generator_scope": scope,
                    "init_scheme": init_scheme,
                    "n_min": min(ns),
                    "n_max": max(ns),
                    "n_points": len(ns),
                    "exp_params": _fmt_params(fit_result["exp"]["params"]),
                    "exp_r2": fit_result["exp"]["r2"],
                    "exp_aic": fit_result["exp"]["aic"],
                    "poly_params": _fmt_params(fit_result["poly"]["params"]),
                    "poly_r2": fit_result["poly"]["r2"],
                    "poly_aic": fit_result["poly"]["aic"],
                    "verdict": fit_result["verdict"],
                    "baseline_rule_prediction": rule_pred,
                    "agrees_with_baseline_rule": agreement,
                }
            )
            print(
                f"{scope}/{init_scheme}: n={ns} verdict={fit_result['verdict']} "
                f"(exp r2={fit_result['exp']['r2']:.4f} aic={fit_result['exp']['aic']:.2f}; "
                f"poly r2={fit_result['poly']['r2']:.4f} aic={fit_result['poly']['aic']:.2f}) "
                f"fit_label={fit_label} baseline_rule={rule_pred} -> {agreement}"
            )
    return summary_rows, fit_cache


def save_summary_csv(rows, path):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=SUMMARY_FIELDNAMES)
        writer.writeheader()
        writer.writerows(rows)


def save_plot(scope, fit_cache, path):
    """Two subplots (one per init_scheme): log-scale variance vs n, real
    scatter points plus both fitted curves overlaid, per cp_alpha_sweep.py's
    established plotting convention."""
    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    for ax, init_scheme in zip(axes, INIT_SCHEMES):
        ns, variances, fit_result = fit_cache[(scope, init_scheme)]
        ns_arr = np.array(ns, dtype=float)
        ys_arr = np.array(variances, dtype=float)

        ax.scatter(ns_arr, ys_arr, color="C0", zorder=3, label="measured")

        dense_ns = np.linspace(min(ns), max(ns), 200)
        if fit_result["exp"]["converged"]:
            ax.plot(
                dense_ns,
                exp_model(dense_ns, *fit_result["exp"]["params"]),
                color="C1",
                label=f"exp fit (R2={fit_result['exp']['r2']:.3f})",
            )
        if fit_result["poly"]["converged"]:
            ax.plot(
                dense_ns,
                poly_model(dense_ns, *fit_result["poly"]["params"]),
                color="C2",
                label=f"poly fit (R2={fit_result['poly']['r2']:.3f})",
            )

        ax.set_yscale("log")
        ax.set_xlabel("n")
        ax.set_ylabel("gradient variance")
        ax.set_title(f"{init_scheme} (verdict: {fit_result['verdict']})")
        ax.legend()

    fig.suptitle(f"{scope}: gradient variance vs n -- poly-vs-exponential curve fit")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


if __name__ == "__main__":
    summary_rows, fit_cache = run_analysis()
    save_summary_csv(summary_rows, SUMMARY_CSV_PATH)
    for scope in GENERATOR_SCOPES:
        save_plot(scope, fit_cache, PLOT_PATHS[scope])
    print(f"Wrote {SUMMARY_CSV_PATH} and {len(PLOT_PATHS)} plots ({', '.join(PLOT_PATHS.values())}).")
