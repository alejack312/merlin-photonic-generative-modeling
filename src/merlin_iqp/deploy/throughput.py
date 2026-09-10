"""Qualified accepted-sample resource controls."""

from __future__ import annotations

import math


def _probability(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value) or not 0.0 < value <= 1.0:
        raise ValueError(f"{name} must be finite and in (0,1], got {value!r}")
    return value


def general_attempts_per_sample(total_acceptance: float) -> float:
    """Independent source attempts per accepted sample for a full model."""

    return 1.0 / _probability(total_acceptance, "total_acceptance")


def fixed_photon_attempts_per_sample(eta: float, n: int, model_success: float) -> float:
    """Fixed-n, g2=0 control: 1/(eta**n * p_model_success)."""

    eta = _probability(eta, "eta")
    if int(n) != n or n < 0:
        raise ValueError("n must be a nonnegative integer")
    return general_attempts_per_sample(eta**int(n) * _probability(model_success, "model_success"))


def fixed_photon_accepted_mass(eta: float, n: int, model_success: float) -> float:
    """Absolute accepted mass for the fixed-n, ``g2=0`` loss model.

    Uniform independent survival contributes exactly ``eta**n`` when the
    acceptance event requires all n photons.  This helper is deliberately
    separate from conditional-distribution code so callers cannot normalize
    the loss away before recording acceptance.
    """

    eta = _probability(eta, "eta")
    if int(n) != n or n < 0:
        raise ValueError("n must be a nonnegative integer")
    return float(eta**int(n) * _probability(model_success, "model_success"))


def heralded_cz_attempts_per_sample(eta: float, n: int, k: int) -> float:
    """Separate ideal-source heralded-CZ resource illustration."""

    eta = _probability(eta, "eta")
    if int(n) != n or int(k) != k or n < 0 or k < 0:
        raise ValueError("n and k must be nonnegative integers")
    return 1.0 / (eta ** (int(n) + 2 * int(k)) * (2.0 / 27.0) ** int(k))
