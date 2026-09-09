import json
from pathlib import Path

from scripts.v4_tcdp.validate_artifacts import validate


def _write(path: Path, value: object) -> Path:
    path.write_text(json.dumps(value), encoding="utf-8")
    return path


def test_validator_rejects_zero_acceptance_pass_and_bad_attempts(tmp_path: Path) -> None:
    value = {
        "schema_version": "v4_tcdp.matched_comparison.v1",
        "arms": [{"stage": "deployed", "backend_id": "p", "acceptance_mass": 0.0}],
        "metrics": {"deployed:p": {"acceptance_mass": 0.5, "attempts_per_accepted_sample": 0.0}},
    }
    result = validate(tmp_path)
    assert result["status"] == "PASS"
    _write(tmp_path / "bad.json", value)
    result = validate(tmp_path)
    assert result["status"] == "FAIL"
    assert result["failure_count"] >= 2


def test_validator_rejects_corrupt_photonic_mass_and_conditional_vector(tmp_path: Path) -> None:
    _write(
        tmp_path / "bad.json",
        {
            "schema_version": "v4_tcdp.photonic_ring.v2",
            "status": "PASS",
            "direct": {
                "absolute_accepted_mass": 0.0,
                "rejected_mass": 0.1,
                "decoded_conditional_vector": [0.6, 0.6],
            },
        },
    )
    result = validate(tmp_path)
    assert result["status"] == "FAIL"
    assert result["failure_count"] >= 3


def test_validator_rejects_incomplete_resource_sizes(tmp_path: Path) -> None:
    _write(tmp_path / "bad.json", {"schema": "v4.resource-budget.v1", "sizes": [10], "cases": []})
    result = validate(tmp_path)
    assert result["status"] == "FAIL"


def test_validator_rejects_resource_pass_with_inconclusive_case(tmp_path: Path) -> None:
    _write(
        tmp_path / "bad.json",
        {
            "schema": "v4.resource-budget.v1",
            "status": "PASS",
            "sizes": [4, 6, 8, 10],
            "cases": [
                {"n": n, "measurement_status": "PASS" if n != 8 else "INCONCLUSIVE"}
                for n in [4, 6, 8, 10]
            ],
        },
    )
    result = validate(tmp_path)
    assert result["status"] == "FAIL"


def test_validator_requires_labeled_support_evidence(tmp_path: Path) -> None:
    _write(
        tmp_path / "bad.json",
        {
            "schema_version": "v4_tcdp.matched_comparison.v1",
            "target_hash": "0" * 64,
            "arms": [{"stage": "raw", "backend_id": "x", "acceptance_mass": 1.0}],
            "metrics": {
                "raw:x": {
                    "acceptance_mass": 1.0,
                    "attempts_per_accepted_sample": 1.0,
                    "support_validity": 1.0,
                }
            },
        },
    )
    result = validate(tmp_path)
    assert result["status"] == "FAIL"
