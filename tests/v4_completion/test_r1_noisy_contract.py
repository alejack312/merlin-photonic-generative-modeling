"""Bucket-1 contract and test-local multiphoton reference checks."""

from __future__ import annotations

from collections import defaultdict

import pytest

from merlin_iqp.deploy import (
    EXTRA_PHOTON_MODEL,
    G2_P2_EQUATION,
    G2_P2_SOURCE_NOTE,
    IGNORED_MASS_FLAG_THRESHOLD,
    NoisyProfile,
    make_noisy_run_report,
    p2_from_g2,
)


def _one_pulse_detected_counts(p2: float, eta: float) -> dict[int, float]:
    """Owner-provided one-pulse oracle; retained in tests, not production code."""

    return {
        0: p2 * (1.0 - eta) ** 2 + (1.0 - p2) * (1.0 - eta),
        1: p2 * (2.0 * eta * (1.0 - eta)) + (1.0 - p2) * eta,
        2: p2 * eta**2,
    }


def _convolve_counts(one_pulse: dict[int, float], pulses: int) -> dict[int, float]:
    counts = {0: 1.0}
    for _ in range(pulses):
        next_counts: defaultdict[int, float] = defaultdict(float)
        for left, left_mass in counts.items():
            for right, right_mass in one_pulse.items():
                next_counts[left + right] += left_mass * right_mass
        counts = dict(next_counts)
    return counts


def _tvd(left: dict[int, float], right: dict[int, float]) -> float:
    keys = set(left) | set(right)
    return 0.5 * sum(abs(left.get(key, 0.0) - right.get(key, 0.0)) for key in keys)


def test_pont_g2_mapping_is_explicit_and_inverts_owner_example() -> None:
    assert G2_P2_EQUATION == "g2 = 2*p2 / (p1 + 2*p2)**2"
    assert "Appendix H" in G2_P2_SOURCE_NOTE
    assert "owner review pending" in G2_P2_SOURCE_NOTE
    g2_for_point_one = 2.0 * 0.1 / (1.0 + 0.1) ** 2
    assert p2_from_g2(g2_for_point_one, assume_p1_plus_p2_normalized=True) == pytest.approx(0.1, abs=1e-12)
    with pytest.raises(ValueError, match="explicit assumption"):
        p2_from_g2(g2_for_point_one, assume_p1_plus_p2_normalized=False)


def test_owner_one_pulse_and_two_pulse_examples() -> None:
    one = _one_pulse_detected_counts(0.1, 0.5)
    assert one == pytest.approx({0: 0.475, 1: 0.5, 2: 0.025}, abs=1e-12)
    two = _convolve_counts(one, 2)
    assert two == pytest.approx({0: 0.225625, 1: 0.475, 2: 0.27375, 3: 0.025, 4: 0.000625}, abs=1e-12)
    assert {key: round(value, 5) for key, value in two.items()} == pytest.approx(
        {0: 0.22563, 1: 0.475, 2: 0.27375, 3: 0.025, 4: 0.00063}, abs=1e-12
    )
    assert _one_pulse_detected_counts(0.1, 1.0)[0] == pytest.approx(0.0, abs=1e-12)


def test_positive_g2_changes_conditional_counts_when_eta_changes() -> None:
    p2 = p2_from_g2(2.0 * 0.1 / (1.0 + 0.1) ** 2, assume_p1_plus_p2_normalized=True)
    lossless = _one_pulse_detected_counts(p2, 1.0)
    lossy = _one_pulse_detected_counts(p2, 0.5)
    assert _tvd(lossless, lossy) > 1.0e-3
    assert sum(lossless.values()) == pytest.approx(1.0, abs=1e-12)
    assert sum(lossy.values()) == pytest.approx(1.0, abs=1e-12)


def test_noisy_profile_contract_records_cutoff_detectors_and_acceptance_columns() -> None:
    profile = NoisyProfile("ideal-pnr", 1.0, 0.0, 0.5, "PNR", cutoff_extra_photons=2)
    assert profile.extra_photon_model == EXTRA_PHOTON_MODEL == "distinguishable"
    assert profile.cutoff(2) == 4
    assert profile.acceptance_after_source(2) == pytest.approx(0.25)
    assert profile.acceptance_with_brightness(2) is None

    bright = NoisyProfile("published-brightness", 0.9438, 0.00732, 0.5, "threshold", 1, 0.55)
    assert bright.cutoff(3) == 4
    assert bright.acceptance_after_source(3) == pytest.approx(0.125)
    assert bright.acceptance_with_brightness(3) == pytest.approx(0.06875)


def test_noisy_run_report_always_exposes_ignored_mass_and_flag() -> None:
    profile = NoisyProfile("ideal-pnr", 1.0, 0.0, 0.5, "PNR", 0)
    flagged = make_noisy_run_report(profile, 2, {"00": 0.9}, total_mass=1.0, retained_mass=0.9989)
    assert flagged.ignored_mass == pytest.approx(0.0011)
    assert flagged.ignored_mass_flagged is True
    assert flagged.as_row()["acceptance_with_brightness"] is None
    assert flagged.as_row()["ignored_mass"] == pytest.approx(0.0011)

    clear = make_noisy_run_report(profile, 2, {"00": 0.9}, total_mass=1.0, retained_mass=0.9991)
    assert clear.ignored_mass_flagged is False
    assert IGNORED_MASS_FLAG_THRESHOLD == 1.0e-3

    boundary = make_noisy_run_report(profile, 2, {"00": 0.9}, total_mass=1.0, retained_mass=0.999)
    assert boundary.ignored_mass_flagged is True


def test_profile_contract_rejects_unregistered_detector_and_extra_model() -> None:
    with pytest.raises(ValueError, match="detector"):
        NoisyProfile("bad-detector", 1.0, 0.0, 1.0, "PNR-like", 0)  # type: ignore[arg-type]
    with pytest.raises(ValueError, match="extra_photon_model"):
        NoisyProfile("bad-model", 1.0, 0.0, 1.0, "PNR", 0, extra_photon_model="indistinguishable")
