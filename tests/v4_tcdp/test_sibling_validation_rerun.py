"""Contract tests for the registered sibling validation rerun gate."""

from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).parents[2] / "scripts" / "v4_tcdp" / "validate_registered_validation_rerun.py"
SPEC = importlib.util.spec_from_file_location("validate_registered_validation_rerun", SCRIPT)
assert SPEC and SPEC.loader
validator = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(validator)


def test_config_diff_exposes_only_declared_validation_adaptations() -> None:
    source = {
        "experiment": {"name": "source", "description": "source", "output_dir": "results/source"},
        "circuit": {"n_qubits": 6},
    }
    rerun = {
        "experiment": {"name": "rerun", "description": "rerun", "output_dir": "results/rerun"},
        "circuit": {"n_qubits": [6]},
    }
    differences = validator._diff(source, rerun)
    assert {difference["field"] for difference in differences} == {
        "circuit.n_qubits",
        "experiment.description",
        "experiment.name",
        "experiment.output_dir",
    }


def test_config_diff_distinguishes_missing_fields_from_explicit_null() -> None:
    assert validator._diff({"x": None}, {}) == [
        {"field": "x", "source": None, "rerun": None}
    ]
    assert validator._diff({}, {"x": None}) == [
        {"field": "x", "source": None, "rerun": None}
    ]


def test_canonical_result_removes_only_provenance() -> None:
    payload = {"n": 6, "scaled_second_moment": 2.0, "provenance": {"seed": 7}}
    assert validator._canonical_result(payload) == {"n": 6, "scaled_second_moment": 2.0}
