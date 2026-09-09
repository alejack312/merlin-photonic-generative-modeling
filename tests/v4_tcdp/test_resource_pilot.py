"""Focused checks for the bounded deployment resource pilot."""

from __future__ import annotations

import ctypes
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys


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
    passed = {"n": 10, "measurement_status": "PASS", "peak_rss_bytes": 500, "rss_growth_bytes": resource_pilot.N10_RSS_LIMIT_BYTES - 1}
    failed = {"n": 10, "measurement_status": "PASS", "peak_rss_bytes": 500, "rss_growth_bytes": resource_pilot.N10_RSS_LIMIT_BYTES}
    missing = {"n": 10, "measurement_status": "PASS", "peak_rss_bytes": None, "rss_growth_bytes": None}
    assert resource_pilot.rss_status(passed) == "PASS"
    assert resource_pilot.rss_status(failed) == "FAIL"
    assert resource_pilot.rss_status(missing) == "INCONCLUSIVE"


def test_aggregate_status_preserves_failure_and_missing_memory_evidence() -> None:
    assert resource_pilot.aggregate_status([{"n": 4, "measurement_status": "FAIL"}]) == "INCONCLUSIVE"
    complete = [
        {"n": n, "measurement_status": "PASS", "peak_rss_bytes": 100, "rss_growth_bytes": 1}
        for n in resource_pilot.PILOT_SIZES
    ]
    assert resource_pilot.aggregate_status(complete) == "PASS"
    assert resource_pilot.aggregate_status([case for case in complete if case["n"] != 6]) == "INCONCLUSIVE"
    assert resource_pilot.aggregate_status([{**case, "measurement_status": "INCONCLUSIVE"} if case["n"] == 4 else case for case in complete]) == "INCONCLUSIVE"
    assert resource_pilot.aggregate_status([*complete, {"n": 4, "measurement_status": "PASS", "peak_rss_bytes": 100, "rss_growth_bytes": 1}]) == "INCONCLUSIVE"
    assert resource_pilot.aggregate_status([{**case, "measurement_status": "UNKNOWN"} if case["n"] == 10 else case for case in complete]) == "UNKNOWN"
    assert resource_pilot.aggregate_status([{**case, "measurement_status": "FAIL"} if case["n"] == 8 else case for case in complete]) == "FAIL"


def test_windows_memory_counter_layout_is_the_full_ex_structure() -> None:
    fields = [name for name, _ in resource_pilot._ProcessMemoryCountersEx._fields_]
    assert fields == [
        "cb",
        "page_fault_count",
        "peak_working_set_size",
        "working_set_size",
        "quota_peak_paged_pool_usage",
        "quota_paged_pool_usage",
        "quota_peak_non_paged_pool_usage",
        "quota_non_paged_pool_usage",
        "pagefile_usage",
        "peak_pagefile_usage",
        "private_usage",
    ]
    assert resource_pilot._ProcessMemoryCountersEx._fields_[0][1] is ctypes.c_uint32
    assert resource_pilot._ProcessMemoryCountersEx._fields_[1][1] is ctypes.c_uint32
    assert ctypes.sizeof(resource_pilot._ProcessMemoryCountersEx) == 8 + 9 * ctypes.sizeof(ctypes.c_size_t)


def test_worker_payload_validation_rejects_wrong_shape_or_superoperator_claim() -> None:
    valid = {
        "status": "PASS",
        "n": 4,
        "worker_pid": 1234,
        "baseline_rss_bytes": 100,
        "worker_final_rss_bytes": 200,
        "worker_peak_rss_bytes": 250,
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
    assert not resource_pilot._worker_payload_valid({**valid, "worker_pid": 0}, 4)
    assert not resource_pilot._worker_payload_valid({**valid, "worker_peak_rss_bytes": 99}, 4)


def test_memory_probe_measures_the_allocating_interpreter() -> None:
    allocation_bytes = 8 * 1024 * 1024
    process = subprocess.Popen(
        [
            sys.executable,
            str(SCRIPT),
            "--memory-probe-worker",
            "--allocation-bytes",
            str(allocation_bytes),
        ],
        cwd=SCRIPT.parents[2],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    stdout, stderr = process.communicate(timeout=30)
    assert process.returncode == 0, stderr
    payload = json.loads(stdout.strip().splitlines()[-1])
    assert payload["status"] == "PASS"
    assert payload["worker_pid"] == payload["allocating_pid"] == payload["measured_pid"]
    assert payload["allocation_bytes"] == allocation_bytes
    assert payload["touched_bytes"] > 0
    assert payload["checksum"] > 0
    assert payload["peak_rss_bytes"] >= payload["baseline_rss_bytes"]
    if os.name == "nt":
        assert payload["worker_pid"] != process.pid


def test_run_requests_each_registered_size_once_without_launching_pilot(monkeypatch) -> None:
    seen: list[int] = []

    def fake_run_isolated(n: int, timeout_seconds: float) -> dict[str, object]:
        del timeout_seconds
        seen.append(n)
        return {
            "n": n,
            "measurement_status": "PASS",
            "peak_rss_bytes": 100,
            "rss_growth_bytes": 1,
            "map_build_and_evaluation_elapsed_seconds": 0.1,
        }

    monkeypatch.setattr(resource_pilot, "_run_isolated", fake_run_isolated)
    report = resource_pilot.run(timeout_seconds=1.0)
    assert seen == list(resource_pilot.PILOT_SIZES)
    assert report["sizes"] == list(resource_pilot.PILOT_SIZES)
    assert report["status"] == "PASS"
