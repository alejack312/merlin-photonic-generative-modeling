"""B2 capacity-ladder contracts and adversarial report checks."""

from __future__ import annotations

from copy import deepcopy
import importlib.util
import json
from pathlib import Path

import pytest

from merlin_iqp.experiments.correlator_audit import (
    B2_RUNG_LABELS,
    b2_capacity_ladder_audit,
    b2_dependency_checkpoint,
    b2_exact_asymmetric_fixtures,
    b2_paired_comparison,
    validate_b2_exact_asymmetric_fixtures,
    validate_b2_report,
)


BENCHMARK_SCRIPT = Path(__file__).parents[2] / "scripts" / "v4_tcdp" / "benchmark_correlators.py"
BENCHMARK_SPEC = importlib.util.spec_from_file_location("benchmark_correlators_b2", BENCHMARK_SCRIPT)
assert BENCHMARK_SPEC is not None and BENCHMARK_SPEC.loader is not None
benchmark_correlators = importlib.util.module_from_spec(BENCHMARK_SPEC)
BENCHMARK_SPEC.loader.exec_module(benchmark_correlators)


TARGET = {
    "000": 0.5,
    "001": 0.0,
    "010": 0.0,
    "011": 0.0,
    "100": 0.0,
    "101": 0.0,
    "110": 0.0,
    "111": 0.5,
}

MODEL = {
    "000": 0.30,
    "001": 0.10,
    "010": 0.15,
    "011": 0.05,
    "100": 0.05,
    "101": 0.15,
    "110": 0.10,
    "111": 0.10,
}


def test_b2_ladder_labels_oracle_and_paired_seed_contract() -> None:
    report = b2_capacity_ladder_audit(
        TARGET,
        MODEL,
        max_order=1,
        subset_seed=17,
        learned_model=TARGET,
    )

    assert tuple(report["rungs"]) == (1, 2, 3, 4, 5)
    assert [report["rungs_by_number"][str(number)]["label"] for number in range(1, 6)] == [
        B2_RUNG_LABELS[number] for number in range(1, 6)
    ]
    assert report["rungs_by_number"]["1"]["reference_only"] is True
    assert report["rungs_by_number"]["1"]["oracle_target_coefficients"] is True
    assert report["rungs_by_number"]["2"]["reference_only"] is False
    assert report["rungs_by_number"]["3"]["reference_only"] is False
    assert report["rungs_by_number"]["2"]["subset_seed"] == 17
    assert report["rungs_by_number"]["3"]["subset_seed"] == 17
    assert report["rungs_by_number"]["2"]["nonidentity_count"] == report["rungs_by_number"]["3"]["nonidentity_count"]
    assert report["rungs_by_number"]["4"]["status"] == "dependency_pending"
    assert report["rungs_by_number"]["5"]["status"] == "dependency_pending"
    assert report["rungs_by_number"]["2"]["learned_theta_exact_sse"] is not None


def test_b2_paired_comparison_rejects_seed_or_count_corruption() -> None:
    report = b2_capacity_ladder_audit(TARGET, MODEL, max_order=1, subset_seed=17)

    wrong_seed = deepcopy(report)
    wrong_seed["rungs_by_number"]["3"]["subset_seed"] = 18
    with pytest.raises(AssertionError, match="same subset seed"):
        b2_paired_comparison(wrong_seed)

    wrong_count = deepcopy(report)
    wrong_count["rungs_by_number"]["3"]["nonidentity_count"] += 1
    with pytest.raises(AssertionError, match="same number"):
        b2_paired_comparison(wrong_count)


def test_b2_report_validation_rejects_corrupted_rung_label() -> None:
    report = b2_capacity_ladder_audit(TARGET, MODEL, max_order=1, subset_seed=17)
    report["rungs_by_number"]["1"]["label"] = "Approximation"

    with pytest.raises(AssertionError, match="rung 1 label"):
        validate_b2_report(report)


def test_b2_paired_comparison_is_explicit_about_direction() -> None:
    report = b2_capacity_ladder_audit(TARGET, MODEL, max_order=1, subset_seed=17)

    comparison = b2_paired_comparison(report)

    assert comparison["paired"] is True
    assert comparison["order_error"] >= 0.0
    assert comparison["random_error"] >= 0.0
    assert comparison["order_beats_random"] == (comparison["order_error"] < comparison["random_error"])


def test_b2_dependency_checkpoint_reports_candidates_without_installing() -> None:
    checkpoint = b2_dependency_checkpoint()

    assert checkpoint["status"] == "selected_optional_dependencies_pending_installation"
    assert {candidate["rung"] for candidate in checkpoint["candidates"]} == {4, 5}
    assert all(candidate["installed"] is False for candidate in checkpoint["candidates"])
    assert all(candidate["optional_only"] is True for candidate in checkpoint["candidates"])
    assert {candidate["version"] for candidate in checkpoint["candidates"]} == {"1.15.0", "0.8.2"}
    assert all(candidate["license"] == "Apache-2.0" for candidate in checkpoint["candidates"])
    assert checkpoint["author_code"]["status"] == "unavailable"
    assert checkpoint["exact_fixture_gate"]["required_before_run"] is True


def test_b2_exact_asymmetric_fixture_gate_passes_exact_outputs() -> None:
    result = validate_b2_exact_asymmetric_fixtures(b2_exact_asymmetric_fixtures())

    assert result["status"] == "PASS"
    assert result["fixture_ids"] == ["n2_asymmetric", "n3_asymmetric"]
    assert result["max_abs_probability_residual"] == 0.0


def test_b2_exact_asymmetric_fixture_gate_rejects_corrupted_output() -> None:
    outputs = b2_exact_asymmetric_fixtures()
    outputs["n3_asymmetric"]["111"] += 1.0e-6
    outputs["n3_asymmetric"]["110"] -= 1.0e-6

    with pytest.raises(AssertionError, match="n3_asymmetric"):
        validate_b2_exact_asymmetric_fixtures(outputs)


def test_b2_cli_builder_emits_all_rungs_and_paired_comparison(tmp_path: Path) -> None:
    target_path = tmp_path / "target.json"
    model_path = tmp_path / "model.json"
    target_path.write_text(json.dumps(TARGET), encoding="utf-8")
    model_path.write_text(json.dumps(MODEL), encoding="utf-8")

    report = benchmark_correlators.build_b2_report(
        target_path,
        model_path,
        max_order=1,
        subset_seed=17,
    )

    assert report["rungs"] == [1, 2, 3, 4, 5]
    assert report["rungs_by_number"]["1"]["reference_only"] is True
    assert report["paired_comparison"]["paired"] is True
