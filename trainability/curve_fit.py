"""Poly-vs-exponential model comparison for gradient-variance-vs-n data.

TRAIN-02 requires an "explicit poly-vs-exponential model comparison (curve
fit + goodness-of-fit, e.g. R^2/AIC) -- not an eyeballed plot." This module
fits two candidate models to a (system size `n`, gradient variance) curve
via `scipy.optimize.curve_fit` and reports which is better-supported.

Candidate models:
    exp_model(n, a, b, c)  = a * exp(-b * n) + c   -- the barren-plateau
        signature: variance decays exponentially in n.
    poly_model(n, a, b, c) = a * n**(-b) + c        -- the non-barren-plateau
        alternative: variance decays polynomially (power-law) in n.

`fit_and_compare(ns, variances)` fits both models, computes R^2 and AIC for
each, and returns a verdict based on which model has the lower (better) AIC.
Model-comparison convention: a model is declared the winner only if its AIC
is lower by more than `AIC_DELTA_THRESHOLD` (2.0, the conventional
"meaningfully better" bar for delta-AIC -- see Burnham & Anderson, Model
Selection and Multimodel Inference). If the AIC difference is smaller than
that, or if one/both fits fail to converge, the verdict is "inconclusive".

Return shape (this module's own choice -- consumed directly by Plan 17-07):
    {
        "exp":  {"params": np.ndarray | None, "r2": float, "aic": float, "converged": bool},
        "poly": {"params": np.ndarray | None, "r2": float, "aic": float, "converged": bool},
        "verdict": "exp" | "poly" | "inconclusive",
    }
Both "exp" and "poly" entries are always present with "r2"/"aic" keys, even
when a fit does not converge -- consumers must be able to see BOTH models'
metrics side by side, never just the winner. A failed fit reports
`converged: False` and `r2`/`aic` as `float("nan")` rather than being
silently dropped or crashing the whole analysis.
"""

import numpy as np
from scipy.optimize import curve_fit

AIC_DELTA_THRESHOLD = 2.0


def exp_model(n, a, b, c):
    """Exponential decay: the barren-plateau signature."""
    return a * np.exp(-b * n) + c


def poly_model(n, a, b, c):
    """Polynomial/power-law decay: the non-barren-plateau alternative."""
    return a * np.power(n, -b) + c


def aic(residuals, k_params):
    """Akaike Information Criterion from residuals, assuming Gaussian errors.

    AIC = n_obs * log(RSS / n_obs) + 2 * k_params. Lower is better.
    """
    residuals = np.asarray(residuals, dtype=float)
    n_obs = len(residuals)
    rss = np.sum(residuals ** 2)
    rss = max(rss, 1e-300)  # guard against log(0) if a fit is ~perfect
    return n_obs * np.log(rss / n_obs) + 2 * k_params


def _r_squared(ys, resid):
    ss_res = np.sum(resid ** 2)
    ss_tot = np.sum((ys - ys.mean()) ** 2)
    if ss_tot <= 0:
        return float("nan")
    return 1.0 - ss_res / ss_tot


def _fit_one(model_fn, ns, ys):
    """Fit a single model, returning a metrics dict; never raises."""
    p0 = [ys[0] - ys[-1], 0.5, ys[-1]]
    try:
        params, _ = curve_fit(model_fn, ns, ys, p0=p0, maxfev=10000)
        resid = ys - model_fn(ns, *params)
        return {
            "params": params,
            "r2": _r_squared(ys, resid),
            "aic": aic(resid, k_params=len(params)),
            "converged": True,
        }
    except (RuntimeError, ValueError, TypeError):
        # RuntimeError: curve_fit failed to converge within maxfev.
        # ValueError: invalid input (e.g. NaN produced during fitting).
        # TypeError: degenerate input, e.g. fewer data points than params.
        return {
            "params": None,
            "r2": float("nan"),
            "aic": float("nan"),
            "converged": False,
        }


def fit_and_compare(ns, variances):
    """Fit exp_model and poly_model to (ns, variances) and compare.

    Returns a dict with "exp"/"poly" metrics (params, r2, aic, converged)
    and a "verdict" of "exp", "poly", or "inconclusive" (see module
    docstring for the delta-AIC threshold convention).
    """
    ns = np.asarray(ns, dtype=float)
    ys = np.asarray(variances, dtype=float)

    exp_result = _fit_one(exp_model, ns, ys)
    poly_result = _fit_one(poly_model, ns, ys)

    if exp_result["converged"] and poly_result["converged"]:
        delta = poly_result["aic"] - exp_result["aic"]
        if delta > AIC_DELTA_THRESHOLD:
            verdict = "exp"
        elif -delta > AIC_DELTA_THRESHOLD:
            verdict = "poly"
        else:
            verdict = "inconclusive"
    elif exp_result["converged"] and not poly_result["converged"]:
        verdict = "exp"
    elif poly_result["converged"] and not exp_result["converged"]:
        verdict = "poly"
    else:
        verdict = "inconclusive"

    return {"exp": exp_result, "poly": poly_result, "verdict": verdict}
