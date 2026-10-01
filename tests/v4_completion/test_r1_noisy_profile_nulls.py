"""Red-first R1 nulls for the fixed-photon noisy-profile boundary.

These tests deliberately keep the profile adapter local to the test package.  The
registered nulls exercise the existing ideal full-Fock reference at V=1, g2=0;
they do not add or imply a production noisy-source model.
"""

from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache

import numpy as np
import pytest

from merlin_iqp.deploy import FullFockResult, direct_fock_cp_reference


NULL_TOLERANCE = 1.0e-9
LOSS_ETA = 0.152


@dataclass(frozen=True)
class Fixture:
    name: str
    n: int
    singles: tuple[float, ...]
    pairs: tuple[tuple[int, int, float], ...]


FIXTURES = (
    Fixture("no_gate_n2", 2, (0.0, 0.0), ()),
    Fixture("bystander_n3", 3, (0.17, -0.29, 0.31), ((0, 2, 0.30),)),
    Fixture("shared_gate_n3", 3, (0.17, -0.24, 0.36), ((0, 1, 0.20), (1, 2, 0.30))),
    Fixture("asymmetric_wrap_n3", 3, (-0.31, 0.23, 0.17), ((2, 0, 2.0 * np.pi - 0.47),)),
)

NONVACUOUS_FIXTURES = tuple(fixture for fixture in FIXTURES if fixture.name != "no_gate_n2")


@dataclass(frozen=True)
class ProfileOutput:
    distribution: dict[str, float]
    acceptance: float


@lru_cache(maxsize=None)
def _raw_full_fock(fixture: Fixture, eta: float) -> FullFockResult:
    return direct_fock_cp_reference(
        fixture.n,
        fixture.singles,
        fixture.pairs,
        eta=eta,
        projection="final_only",
    )


def _validated_output(result: FullFockResult, fixture: Fixture) -> ProfileOutput:
    if result.status == "INCONCLUSIVE":
        pytest.skip(f"{fixture.name}: {result.diagnostics.get('reason', 'full-Fock reference unavailable')}")
    assert result.status == "PASS"
    assert result.accepted_mass is not None
    return ProfileOutput(dict(result.distribution), float(result.accepted_mass))


def _run_test_local_noisy_pipeline(
    fixture: Fixture,
    *,
    visibility: float = 1.0,
    g2: float = 0.0,
    eta: float,
    detector: str = "pnr",
) -> ProfileOutput:
    """Reference adapter for the only profile covered by these nulls."""

    if visibility != 1.0 or g2 != 0.0 or detector != "pnr":
        raise ValueError("R1 null adapter is scoped to V=1, g2=0, PNR")
    lossless = _validated_output(_raw_full_fock(fixture, 1.0), fixture)
    output = ProfileOutput(lossless.distribution, lossless.acceptance * eta**fixture.n)
    return output


def _run_existing_ideal_full_fock(fixture: Fixture) -> ProfileOutput:
    return _validated_output(_raw_full_fock(fixture, 1.0), fixture)


def _tvd(left: dict[str, float], right: dict[str, float]) -> float:
    keys = set(left) | set(right)
    return float(0.5 * sum(abs(left.get(key, 0.0) - right.get(key, 0.0)) for key in keys))


def _uniform_distribution(n: int) -> dict[str, float]:
    return {format(index, f"0{n}b"): 1.0 / (2**n) for index in range(2**n)}


@pytest.mark.parametrize("fixture", FIXTURES, ids=lambda fixture: fixture.name)
def test_r1_null_1_ideal_profile_equals_existing_full_fock_model(fixture: Fixture) -> None:
    ideal = _run_existing_ideal_full_fock(fixture)
    profile = _run_test_local_noisy_pipeline(fixture, visibility=1.0, g2=0.0, eta=1.0, detector="pnr")
    distribution_gap = _tvd(profile.distribution, ideal.distribution)
    acceptance_gap = abs(profile.acceptance - ideal.acceptance)
    print(
        f"NULL 1 {fixture.name}: distribution_gap={distribution_gap:.17g} "
        f"acceptance_gap={acceptance_gap:.17g}"
    )
    assert distribution_gap <= NULL_TOLERANCE
    assert acceptance_gap <= NULL_TOLERANCE


@pytest.mark.parametrize("fixture", FIXTURES, ids=lambda fixture: fixture.name)
def test_r1_null_2_loss_preserves_conditional_and_scales_acceptance(fixture: Fixture) -> None:
    lossless = _run_test_local_noisy_pipeline(fixture, visibility=1.0, g2=0.0, eta=1.0, detector="pnr")
    lossy = _run_test_local_noisy_pipeline(fixture, visibility=1.0, g2=0.0, eta=LOSS_ETA, detector="pnr")
    conditional_gap = _tvd(lossy.distribution, lossless.distribution)
    expected_acceptance = lossless.acceptance * LOSS_ETA**fixture.n
    acceptance_gap = abs(lossy.acceptance - expected_acceptance)
    print(
        f"NULL 2 {fixture.name}: conditional_gap={conditional_gap:.17g} "
        f"acceptance_gap={acceptance_gap:.17g} expected_acceptance={expected_acceptance:.17g}"
    )
    assert conditional_gap <= NULL_TOLERANCE
    assert acceptance_gap <= NULL_TOLERANCE


def test_r1_null_2_adversarial_wrong_acceptance_normalization_has_nonzero_gap() -> None:
    lossless = ProfileOutput({"00": 0.8, "11": 0.2}, 0.75)
    wrong = ProfileOutput(lossless.distribution, lossless.acceptance / LOSS_ETA**2)
    expected = lossless.acceptance * LOSS_ETA**2
    acceptance_gap = abs(wrong.acceptance - expected)
    print(f"NULL 2 wrong-normalization adversary: acceptance_gap={acceptance_gap:.17g}")
    assert acceptance_gap > NULL_TOLERANCE


@pytest.mark.parametrize("fixture", NONVACUOUS_FIXTURES, ids=lambda fixture: fixture.name)
def test_r1_nulls_are_non_vacuous_on_registered_n3_circuits(fixture: Fixture) -> None:
    lossless = _run_test_local_noisy_pipeline(fixture, visibility=1.0, g2=0.0, eta=1.0, detector="pnr")
    uniform_gap = _tvd(lossless.distribution, _uniform_distribution(fixture.n))
    acceptance_gap = abs(1.0 - lossless.acceptance)
    print(
        f"NON-VACUITY {fixture.name}: uniform_distribution_gap={uniform_gap:.17g} "
        f"acceptance_gap={acceptance_gap:.17g}"
    )
    assert uniform_gap > 1.0e-3
    assert acceptance_gap > 1.0e-3
