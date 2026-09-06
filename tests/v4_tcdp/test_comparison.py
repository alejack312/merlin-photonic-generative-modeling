import json
import shutil

import numpy as np
import pytest

from merlin_iqp.experiments.comparison import (
    DistributionArm,
    MatchedComparison,
    expected_coverage,
    expected_occupancy,
    floored_log_ratio,
    hamming_mmd2_crosscheck,
    marginal_tvd_panel,
    metric_specific_mutation,
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


def test_infinite_true_kl_is_json_safe_and_explicit() -> None:
    comparison = MatchedComparison(
        "support-mismatch",
        np.array([0.5, 0.5]),
        (DistributionArm("identity", np.array([1.0, 0.0]), "raw"),),
        1.0,
    )
    manifest = comparison.manifest()
    json.dumps(manifest, allow_nan=False)
    row = manifest["metrics"]["raw:identity"]
    assert row["true_forward_kl"] is None
    assert row["true_forward_kl_status"] == "infinite"
    assert row["true_forward_kl_value"] == "inf"


def test_coverage_uses_target_support_and_handles_q_one() -> None:
    result = expected_coverage(np.array([1.0, 0.0]), np.array([1.0, 0.0]), 20_000)
    assert result["support_size"] == 1
    assert result["excluded_target_mass"] == 0.0
    assert result["expected_coverage"] == 1.0
    assert expected_coverage(np.array([1.0, 0.0]), np.array([1.0, 0.0]), 0)["expected_coverage"] == 0.0
    with pytest.raises(ValueError, match="must be an integer"):
        expected_coverage(np.array([1.0, 0.0]), np.array([1.0, 0.0]), 1.5)


def test_occupancy_and_direct_hamming_crosscheck_are_population_metrics() -> None:
    target = np.array([0.4, 0.3, 0.2, 0.1])
    candidate = np.array([0.3, 0.4, 0.2, 0.1])
    occupancy = expected_occupancy(candidate, 100)
    assert 0.0 < occupancy["expected_occupancy"] <= 4.0
    crosscheck = hamming_mmd2_crosscheck(target, candidate, sigma=0.8)
    assert crosscheck["status"] == "PASS"
    assert crosscheck["direct"] == pytest.approx(crosscheck["trainer_objective"])
    assert crosscheck["direct"] == pytest.approx(crosscheck["walsh"])


def test_marginal_panel_is_labeled_msb_first_and_mutations_preserve_mass() -> None:
    target = np.full(8, 1 / 8)
    candidate = target.copy()
    panel = marginal_tvd_panel(target, candidate)
    assert panel["marginal_tvd_order1_mean"] == pytest.approx(0.0)
    assert panel["marginal_tvd_order2_count"] == 3
    assert panel["marginal_bit_order"] == "msb_first"
    mutation = metric_specific_mutation(candidate, "marginal_tvd_order2")
    assert mutation["mass_before"] == pytest.approx(mutation["mass_after"])
    assert mutation["vector"].sum() == pytest.approx(1.0)


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
    assert rows["raw:numpy-iqp"]["stage"] == "raw"
    assert rows["compiled:ideal-compiled-map"]["stage"] == "compiled"
    assert rows["deployed:ideal-deployed-map"]["stage"] == "deployed"
    assert rows["deployed:ideal-deployed-map"]["acceptance_mass"] < 1.0
    assert rows["compiled:ideal-compiled-map"]["tvd_to_target"] != pytest.approx(rows["compiled:ideal-unquantized-control"]["tvd_to_target"], abs=1e-12)
    assert rows["compiled:ideal-compiled-map"]["tvd_to_target"] == pytest.approx(rows["deployed:ideal-deployed-map"]["tvd_to_target"], abs=1e-12)
    assert rows["compiled:ideal-compiled-map"]["acceptance_mass"] == pytest.approx(rows["deployed:ideal-deployed-map"]["acceptance_mass"], abs=1e-18)
    manifest = comparison.manifest()
    assert manifest["controls"]["success_mutation"]["deployed:ideal-deployed-map"]["conditional_vector_hash_equal"] is True
    assert manifest["resource_report"]["elapsed_seconds"] >= 0.0


@pytest.mark.parametrize("array_name", ["generator", "final_theta"])
def test_comparison_rejects_modified_model_arrays(tmp_path, array_name: str) -> None:
    source = __import__("pathlib").Path("results/v4_tcdp/rings/rings_hamming/n4_seed0_smoke")
    fixture = tmp_path / "comparison"
    shutil.copytree(source, fixture)
    with np.load(fixture / "run.npz", allow_pickle=False) as archive:
        arrays = {key: archive[key].copy() for key in archive.files}
    if array_name == "generator":
        arrays[array_name][0, 0] = 1 - arrays[array_name][0, 0]
    else:
        arrays[array_name].flat[0] += 0.02
    np.savez(fixture / "run.npz", **arrays)
    with pytest.raises(ValueError, match=f"{('theta' if array_name == 'final_theta' else 'generator')} hash"):
        build_comparison(fixture)


def test_comparison_rejects_modified_dataset_array(tmp_path) -> None:
    source = __import__("pathlib").Path("results/v4_tcdp/rings/rings_hamming/n4_seed0_smoke")
    fixture = tmp_path / "comparison"
    shutil.copytree(source, fixture)
    with np.load(fixture / "dataset.npz", allow_pickle=False) as archive:
        arrays = {key: archive[key].copy() for key in archive.files}
    arrays["train_histogram"][0] += 0.01
    np.savez(fixture / "dataset.npz", **arrays)
    with pytest.raises(ValueError, match="train dataset hash"):
        build_comparison(fixture)
