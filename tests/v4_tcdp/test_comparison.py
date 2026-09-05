import numpy as np
import pytest

from merlin_iqp.experiments.comparison import (
    DistributionArm,
    MatchedComparison,
    expected_coverage,
    floored_log_ratio,
    true_forward_kl,
)
from scripts.v4_tcdp.compare_backends import build_comparison


def test_hamming_comparison_reports_all_stages_and_acceptance() -> None:
    target = np.array([0.5, 0.25, 0.2, 0.05])
    comparison = MatchedComparison(
        "fixture",
        target,
        (
            DistributionArm("qubit", target, "compiled"),
            DistributionArm("photonic", [0.49, 0.26, 0.2, 0.05], "deployed", acceptance_mass=0.25, samples=200),
        ),
        hamming_sigma=1.0,
    )
    rows = comparison.metrics()
    assert rows["compiled:qubit"]["hamming_mmd2"] == pytest.approx(0.0)
    assert rows["compiled:qubit"]["acceptance_mass"] == 1.0
    assert rows["deployed:photonic"]["attempts_per_accepted_sample"] == pytest.approx(4.0)
    assert comparison.manifest()["hamming_kernel"]["distance"] == "Hamming"


def test_true_kl_and_floor_are_distinct() -> None:
    target = np.array([1.0, 0.0])
    candidate = np.array([0.0, 1.0])
    assert np.isinf(true_forward_kl(target, candidate))
    value, added_mass = floored_log_ratio(target, candidate, 1e-12)
    assert value > 0 and added_mass > 0


def test_coverage_uses_target_support_and_handles_q_one() -> None:
    result = expected_coverage(np.array([1.0, 0.0]), np.array([1.0, 0.0]), 20_000)
    assert result["support_size"] == 1
    assert result["excluded_target_mass"] == 0.0
    assert result["expected_coverage"] == 1.0


def test_distribution_rejects_unnormalized_or_invalid_stage() -> None:
    with pytest.raises(ValueError):
        DistributionArm("x", [0.2, 0.2, 0.2, 0.2], "raw", acceptance_mass=0)
    with pytest.raises(ValueError):
        DistributionArm("x", [0.5, 0.5], "simulated")


def test_ring_smoke_comparison_keeps_raw_compiled_and_deployed_distinct() -> None:
    comparison = build_comparison(
        __import__("pathlib").Path("results/v4_tcdp/rings/rings_hamming/n4_seed0_smoke")
    )
    rows = comparison.metrics()
    assert rows["raw:numpy-iqp"]["tvd_to_target"] == pytest.approx(rows["compiled:ideal-compiled-map"]["tvd_to_target"], abs=1e-12)
    assert rows["deployed:ideal-deployed-map"]["stage"] == "deployed"
    assert rows["deployed:ideal-deployed-map"]["acceptance_mass"] < 1.0
