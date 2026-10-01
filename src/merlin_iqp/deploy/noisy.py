"""Contract objects for the expanded D1 noisy-source boundary.

This module records profile parameters and run-level accounting only.  It does
not simulate a noisy source, detector, or physical device.
"""

from __future__ import annotations

from dataclasses import dataclass
import math
from typing import Literal, Mapping


Detector = Literal["PNR", "threshold"]
EXTRA_PHOTON_MODEL = "distinguishable"
IGNORED_MASS_FLAG_THRESHOLD = 1.0e-3
G2_P2_EQUATION = "g2 = 2*p2 / (p1 + 2*p2)**2"
G2_P2_SOURCE_NOTE = (
    "Assistant reading of Pont et al., PRX 12, 031033 (2022), Appendix H, PDF p. 18; "
    "owner review pending. Inverting the published relation assumes p1 + p2 = 1."
)


def _finite_probability(value: float, name: str, *, allow_zero: bool = True) -> float:
    value = float(value)
    lower_ok = value >= 0.0 if allow_zero else value > 0.0
    if not math.isfinite(value) or not lower_ok or value > 1.0:
        interval = "[0,1]" if allow_zero else "(0,1]"
        raise ValueError(f"{name} must be finite and in {interval}, got {value!r}")
    return value


def p2_from_g2(g2: float, *, assume_p1_plus_p2_normalized: bool) -> float:
    """Invert the Appendix-H relation under an explicit normalization assumption.

    Pont et al. give ``g2 = 2*p2/(p1 + 2*p2)^2``.  This helper selects the
    physical small root after explicitly requiring the assistant's reading
    ``p1 + p2 = 1``; it does not silently infer that normalization.
    """

    if not assume_p1_plus_p2_normalized:
        raise ValueError("p2 inversion requires the explicit assumption p1 + p2 = 1")
    g2 = _finite_probability(g2, "g2")
    if g2 > 0.5:
        raise ValueError("g2 must be at most 0.5 for the p1 + p2 = 1 inversion")
    if g2 == 0.0:
        return 0.0
    p2 = (1.0 - g2 - math.sqrt(1.0 - 2.0 * g2)) / g2
    return _finite_probability(p2, "p2")


@dataclass(frozen=True)
class NoisyProfile:
    """Registered source/detector contract for one noisy profile cell."""

    profile_id: str
    visibility: float
    g2: float
    eta: float
    detector: Detector
    cutoff_extra_photons: int
    source_emission_probability: float | None = None
    extra_photon_model: str = EXTRA_PHOTON_MODEL

    def __post_init__(self) -> None:
        if not self.profile_id:
            raise ValueError("profile_id must not be empty")
        _finite_probability(self.visibility, "visibility")
        _finite_probability(self.g2, "g2")
        _finite_probability(self.eta, "eta", allow_zero=False)
        if self.detector not in {"PNR", "threshold"}:
            raise ValueError("detector must be PNR or threshold")
        if int(self.cutoff_extra_photons) != self.cutoff_extra_photons or self.cutoff_extra_photons < 0:
            raise ValueError("cutoff_extra_photons must be a nonnegative integer")
        if self.source_emission_probability is not None:
            _finite_probability(self.source_emission_probability, "source_emission_probability")
        if self.extra_photon_model != EXTRA_PHOTON_MODEL:
            raise ValueError(f"extra_photon_model is fixed to {EXTRA_PHOTON_MODEL!r}")

    def cutoff(self, n: int) -> int:
        if int(n) != n or n < 0:
            raise ValueError("n must be a nonnegative integer")
        return int(n) + int(self.cutoff_extra_photons)

    def acceptance_after_source(self, n: int) -> float:
        """Acceptance after source loss, excluding unpublished brightness."""

        return float(self.eta ** self._validated_n(n))

    def acceptance_with_brightness(self, n: int) -> float | None:
        """Acceptance including source emission probability, or N/A when absent."""

        if self.source_emission_probability is None:
            return None
        return float(self.source_emission_probability * self.eta ** self._validated_n(n))

    @staticmethod
    def _validated_n(n: int) -> int:
        if int(n) != n or n < 0:
            raise ValueError("n must be a nonnegative integer")
        return int(n)


@dataclass(frozen=True)
class NoisyRunReport:
    """A result plus acceptance and ignored-mass accounting for one run."""

    profile: NoisyProfile
    n: int
    result: dict[str, float]
    total_mass: float
    retained_mass: float

    def __post_init__(self) -> None:
        if int(self.n) != self.n or self.n < 0:
            raise ValueError("n must be a nonnegative integer")
        total_mass = float(self.total_mass)
        retained_mass = float(self.retained_mass)
        if not math.isfinite(total_mass) or total_mass <= 0.0:
            raise ValueError("total_mass must be finite and positive")
        if not math.isfinite(retained_mass) or retained_mass < 0.0 or retained_mass > total_mass:
            raise ValueError("retained_mass must be finite and within total_mass")
        object.__setattr__(self, "result", dict(self.result))

    @property
    def ignored_mass(self) -> float:
        return float(self.total_mass - self.retained_mass)

    @property
    def ignored_mass_flagged(self) -> bool:
        return self.ignored_mass >= IGNORED_MASS_FLAG_THRESHOLD

    def as_row(self) -> dict[str, object]:
        """Return stable report columns, keeping N/A brightness as ``None``."""

        return {
            "profile_id": self.profile.profile_id,
            "n": int(self.n),
            "result": dict(self.result),
            "acceptance_after_source_eta_n": self.profile.acceptance_after_source(self.n),
            "acceptance_with_brightness": self.profile.acceptance_with_brightness(self.n),
            "ignored_mass": self.ignored_mass,
            "ignored_mass_flagged": self.ignored_mass_flagged,
        }


def make_noisy_run_report(
    profile: NoisyProfile,
    n: int,
    result: Mapping[str, float],
    *,
    total_mass: float,
    retained_mass: float,
) -> NoisyRunReport:
    """Build a run report without normalizing away ignored mass."""

    return NoisyRunReport(profile, int(n), dict(result), total_mass, retained_mass)
