"""Optional small-n full-Fock reference and explicit capability diagnostics."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np


@dataclass(frozen=True)
class FullFockResult:
    status: str
    distribution: dict[str, float] = field(default_factory=dict)
    accepted_mass: float | None = None
    rejected_mass: float | None = None
    diagnostics: dict[str, Any] = field(default_factory=dict)


def full_fock_cp_reference(
    n: int,
    i: int,
    j: int,
    singles: list[float] | tuple[float, ...],
    alpha: float,
    *,
    g2: float = 0.0,
    eta: float = 1.0,
) -> FullFockResult:
    """Run the existing small CP dual-rail reference when its scope applies.

    This deliberately supports only one CP insertion. The fixed-photon
    ``g2=0`` branch accepts uniform loss through explicit ``eta**n`` success
    scaling; multiphoton source requests remain INCONCLUSIVE rather than being
    silently approximated by a gate-local map.
    """

    if n not in (2, 3):
        return FullFockResult("INCONCLUSIVE", diagnostics={"reason": "full-Fock reference is scoped to n=2,3"})
    if not 0 <= i < n or not 0 <= j < n or i == j:
        raise ValueError("invalid CP pair")
    if len(singles) != n:
        raise ValueError("single-angle count does not match n")
    if not np.isfinite(eta) or not 0.0 < eta <= 1.0:
        raise ValueError("eta must be finite and in (0, 1]")
    if not np.isclose(g2, 0.0):
        return FullFockResult(
            "INCONCLUSIVE",
            diagnostics={
                "reason": "multiphoton g2 source model is not implemented; D1 fixed-photon scope excludes it",
                "g2": float(g2),
                "eta": float(eta),
                "source_once": True,
            },
        )
    try:
        from merlin_iqp.encoding.dual_rail import dual_rail_photonic_cp_iqp_distribution
    except Exception as exc:
        return FullFockResult("INCONCLUSIVE", diagnostics={"reason": f"Perceval unavailable: {type(exc).__name__}: {exc}"})
    try:
        distribution, residual, failure = dual_rail_photonic_cp_iqp_distribution(
            n, i, j, list(singles), float(alpha)
        )
    except Exception as exc:
        return FullFockResult("INCONCLUSIVE", diagnostics={"reason": f"Perceval reference failed: {type(exc).__name__}: {exc}"})
    accepted_mass = float((1.0 - failure) * eta**n)
    return FullFockResult(
        "PASS",
        distribution={str(key): float(value) for key, value in distribution.items()},
        accepted_mass=accepted_mass,
        rejected_mass=float(1.0 - accepted_mass),
        diagnostics={
            "source_once": True,
            "source_model": "fixed_photon_g2_0",
            "loss": "uniform_all_photons",
            "projection": "four CP ancilla modes vacuum",
            "residual_out_of_logical_subspace": float(residual),
            "conditional_distribution": True,
            "general_agreement_claim": False,
            "g2": 0.0,
            "eta": float(eta),
            "loss_scaling": "eta**n",
        },
    )
