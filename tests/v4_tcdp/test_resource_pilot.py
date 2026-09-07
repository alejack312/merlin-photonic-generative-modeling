"""Focused checks for the bounded deployment resource pilot."""

from __future__ import annotations

import importlib.util
from pathlib import Path


SCRIPT = Path(__file__).parents[2] / "scripts" / "v4_tcdp" / "resource_pilot.py"
SPEC = importlib.util.spec_from_file_location("resource_pilot", SCRIPT)
assert SPEC is not None and SPEC.loader is not None
resource_pilot = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(resource_pilot)


def test_pilot_sizes_and_allocation_contract_are_bounded() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    assert resource_pilot.PILOT_SIZES == (4, 6, 8, 10)
    assert "np.eye(4**n" not in source
    assert "np.zeros((4**n" not in source
    assert '"full_circuit_superoperator_allocated": False' in source


def test_n10_rss_gate_is_strictly_below_400_mib() -> None:
    passed = {"n": 10, "rss_growth_bytes": resource_pilot.N10_RSS_LIMIT_BYTES - 1}
    failed = {"n": 10, "rss_growth_bytes": resource_pilot.N10_RSS_LIMIT_BYTES}
    missing = {"n": 10, "rss_growth_bytes": None}
    assert resource_pilot.rss_status(passed) == "PASS"
    assert resource_pilot.rss_status(failed) == "FAIL"
    assert resource_pilot.rss_status(missing) == "INCONCLUSIVE"


def test_aggregate_status_preserves_failure_and_missing_memory_evidence() -> None:
    assert resource_pilot.aggregate_status([{"n": 4, "measurement_status": "FAIL"}]) == "FAIL"
    assert resource_pilot.aggregate_status([{"n": 10, "measurement_status": "PASS", "rss_growth_bytes": None}]) == "INCONCLUSIVE"
    assert resource_pilot.aggregate_status([{"n": 10, "measurement_status": "PASS", "rss_growth_bytes": 1}]) == "PASS"


def test_worker_payload_validation_rejects_wrong_shape_or_superoperator_claim() -> None:
    valid = {
        "status": "PASS",
        "n": 4,
        "full_circuit_superoperator_allocated": False,
        "compile_elapsed_seconds": 0.1,
        "map_build_elapsed_seconds": 0.2,
        "evaluation_elapsed_seconds": 0.3,
        "map_build_and_evaluation_elapsed_seconds": 0.5,
        "elapsed_seconds": 0.6,
        "probability_sum": 1.0,
        "model_success": 0.9,
        "state_matrix_shape": [16, 16],
        "gate_count": 13,
        "map_count": 13,
    }
    assert resource_pilot._worker_payload_valid(valid, 4)
    assert not resource_pilot._worker_payload_valid({**valid, "state_matrix_shape": [256, 256]}, 4)
    assert not resource_pilot._worker_payload_valid({**valid, "full_circuit_superoperator_allocated": True}, 4)
