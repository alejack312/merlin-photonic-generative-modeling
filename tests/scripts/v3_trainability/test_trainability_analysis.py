"""CORR-08 (2026-09-05): adversarial regression tests for the plateau
classifiers in scripts/v3_trainability/trainability_analysis.py and
trainability_analysis_1701.py.

An independent audit found both classifiers checked only the fitted
exponential's decay rate `b` (in a*exp(-b*n)+c), when whether the curve
actually decreases with n depends on sign(-a*b) -- both a and b. Feeding
either classifier a strictly INCREASING sequence (1-exp(-0.8n)) previously
returned "plateau" / "survives". These tests reproduce that adversarial
case directly against the real `fit_and_compare` output, plus the
already-correct decaying case, so a future regression trips immediately.
"""

import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[3]))

from merlin_iqp.trainability.curve_fit import fit_and_compare
from scripts.v3_trainability.trainability_analysis import fit_verdict_to_plateau_label
from scripts.v3_trainability.trainability_analysis_1701 import classify_survival

NS = np.arange(2, 9, dtype=float)


def _fit(ys):
    return fit_and_compare(NS, ys)


def test_increasing_curve_is_not_labeled_plateau():
    """1 - exp(-0.8n): strictly increasing, exp wins the AIC comparison
    with a<0, b>0. Must NOT be labeled "plateau"."""
    ys = 1 - np.exp(-0.8 * NS)
    fit = _fit(ys)

    assert fit["verdict"] == "exp"
    a, b = fit["exp"]["params"][0], fit["exp"]["params"][1]
    assert a < 0 and b > 0, "test setup must reproduce the adversarial a<0,b>0 case"

    label = fit_verdict_to_plateau_label(fit)
    assert label != "plateau"


def test_zero_floor_decaying_curve_is_labeled_plateau():
    """Sanity check the fix doesn't over-correct: a real decaying curve
    (a>0, b>0) must still be labeled "plateau"."""
    ys = 2.0 * np.exp(-0.8 * NS)
    fit = _fit(ys)

    assert fit["verdict"] == "exp"
    a, b = fit["exp"]["params"][0], fit["exp"]["params"][1]
    assert a > 0 and b > 0, "test setup must reproduce the genuine-decay case"

    assert fit_verdict_to_plateau_label(fit) == "plateau"


def test_positive_floor_is_inconclusive_not_plateau():
    ys = 2.0 * np.exp(-0.8 * NS) + 0.001
    fit = _fit(ys)

    assert fit["verdict"] == "exp"
    assert fit_verdict_to_plateau_label(fit) == "inconclusive (exp fit has nonzero floor)"


def test_classify_survival_does_not_survive_an_increasing_curve():
    """Same adversarial case against trainability_analysis_1701's
    classify_survival: an increasing curve must not report "survives" or
    "weakens" (both imply an ongoing plateau signature)."""
    ys = 1 - np.exp(-0.8 * NS)
    fit = _fit(ys)
    baseline_cell = {"exp_b": 0.8, "exp_aic": -50.0, "poly_aic": -10.0, "verdict": "exp"}

    result = classify_survival(baseline_cell, fit)

    assert result == "disappears"


def test_classify_survival_survives_a_genuinely_decaying_curve():
    ys = 2.0 * np.exp(-0.8 * NS)
    fit = _fit(ys)
    baseline_cell = {"exp_b": 0.8, "exp_aic": -50.0, "poly_aic": -10.0, "verdict": "exp"}

    result = classify_survival(baseline_cell, fit)

    assert result in ("survives", "weakens")


def test_classify_survival_rejects_positive_floor():
    ys = 2.0 * np.exp(-0.8 * NS) + 0.001
    fit = _fit(ys)
    baseline_cell = {"exp_b": 0.8, "exp_aic": -50.0, "poly_aic": -10.0, "verdict": "exp"}

    assert classify_survival(baseline_cell, fit) == "disappears"
