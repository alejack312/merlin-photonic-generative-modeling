"""Bounded deployment resource pilot with one isolated process per size.

The pilot measures the complete local-map build and density evaluation path for
one deterministic nearest-neighbour chain at n=4, 6, 8, and 10.  It uses a
state matrix of shape ``(2**n, 2**n)`` and never constructs an embedded
full-circuit superoperator.
"""

from __future__ import annotations

import argparse
import ctypes
import hashlib
import json
import os
from pathlib import Path
import platform
import queue
import subprocess
import sys
import threading
import time
from typing import Any

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from merlin_iqp.deploy.compile import CompiledCircuit, compile_iqp  # noqa: E402
from merlin_iqp.deploy.maps import GateMap, ideal_single_map, reconstruct_cp_map  # noqa: E402


PILOT_SIZES = (4, 6, 8, 10)
N10_RSS_LIMIT_BYTES = 400 * 1024 * 1024
DEFAULT_TIMEOUT_SECONDS = 180.0


class _ProcessMemoryCountersEx(ctypes.Structure):
    """Windows PROCESS_MEMORY_COUNTERS_EX layout, with a portable fallback."""

    _fields_ = [
        ("cb", ctypes.c_ulong),
        ("page_fault_count", ctypes.c_ulong),
        ("peak_working_set_size", ctypes.c_size_t),
        ("working_set_size", ctypes.c_size_t),
        ("quota_peak_paged_pool_usage", ctypes.c_size_t),
        ("quota_paged_pool_usage", ctypes.c_size_t),
        ("quota_peak_non_paged_pool_usage", ctypes.c_size_t),
        ("quota_non_paged_pool_usage", ctypes.c_size_t),
        ("pagefile_usage", ctypes.c_size_t),
        ("peak_pagefile_usage", ctypes.c_size_t),
        ("private_usage", ctypes.c_size_t),
    ]


def _rss_bytes(pid: int) -> int | None:
    """Read a live process working set without adding a runtime dependency."""

    if os.name == "nt":
        kernel32 = ctypes.windll.kernel32
        psapi = ctypes.windll.psapi
        handle = kernel32.OpenProcess(0x0400 | 0x0010, False, int(pid))
        if not handle:
            return None
        try:
            counters = _ProcessMemoryCountersEx()
            counters.cb = ctypes.sizeof(counters)
            ok = psapi.GetProcessMemoryInfo(handle, ctypes.byref(counters), ctypes.sizeof(counters))
            return int(counters.working_set_size) if ok else None
        finally:
            kernel32.CloseHandle(handle)

    status_path = Path(f"/proc/{int(pid)}/status")
    try:
        for line in status_path.read_text(encoding="utf-8").splitlines():
            if line.startswith("VmRSS:"):
                return int(line.split()[1]) * 1024
    except (FileNotFoundError, OSError, ValueError, IndexError):
        return None
    return None


def _source_sha256() -> str:
    return _file_sha256(Path(__file__))


def _file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_value(*args: str) -> str:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"
    return result.stdout.strip()


def _representative_inputs(n: int) -> tuple[list[float], list[tuple[int, int, float]]]:
    singles = [0.031 * (index + 1) for index in range(n)]
    pairs = [(index, index + 1, 0.071 + 0.013 * index) for index in range(n - 1)]
    return singles, pairs


def _compile_representative(n: int) -> CompiledCircuit:
    singles, pairs = _representative_inputs(n)
    return compile_iqp(n, singles, pairs, topology="path", quantize=True)


def _build_maps(compiled: CompiledCircuit) -> list[GateMap]:
    maps: list[GateMap] = []
    for gate in compiled.gates:
        if gate.kind in {"single", "pair_compensation"}:
            maps.append(ideal_single_map(gate.theta))
        else:
            if gate.alpha is None:
                raise ValueError("CP gate is missing alpha")
            maps.append(reconstruct_cp_map(gate.alpha, use_perceval=False))
    return maps


def _apply_local_map_vectorized(rho: np.ndarray, gate_map: GateMap, qubits: tuple[int, ...], n: int) -> np.ndarray:
    """Apply one local map with tensor reshapes, without a global superoperator."""

    selected = tuple(int(qubit) for qubit in qubits)
    rest = tuple(qubit for qubit in range(n) if qubit not in selected)
    local_dim = 2**len(selected)
    rest_dim = 2**len(rest)
    tensor = rho.reshape((2,) * (2 * n))
    order = list(selected) + list(rest) + [n + qubit for qubit in selected] + [n + qubit for qubit in rest]
    inverse = np.argsort(order)
    blocked = tensor.transpose(order).reshape(local_dim, rest_dim, local_dim, rest_dim)
    if gate_map.kraus:
        mapped = sum(
            np.einsum("oa,akbl,pb->okpl", kraus, blocked, kraus.conj(), optimize=True)
            for kraus in gate_map.kraus
        )
    elif gate_map.superoperator is not None:
        vectorized = blocked.transpose(0, 2, 1, 3).reshape(local_dim * local_dim, rest_dim * rest_dim, order="F")
        mapped_vectorized = gate_map.superoperator @ vectorized
        mapped = mapped_vectorized.reshape(local_dim, local_dim, rest_dim, rest_dim, order="F").transpose(0, 2, 1, 3)
    else:
        raise ValueError("GateMap has neither Kraus operators nor a superoperator")
    return mapped.reshape((2,) * (2 * n)).transpose(inverse).reshape(rho.shape)


def _evaluate(compiled: CompiledCircuit, maps: list[GateMap]) -> tuple[float, float]:
    n = compiled.n
    plus = np.ones(2**n, complex) / np.sqrt(2**n)
    rho = np.outer(plus, plus.conj())
    operations = [(gate.qubits, map_obj) for gate, map_obj in zip(compiled.gates, maps, strict=True)]
    diagonal_state = rho
    for (qubits, map_obj) in operations:
        diagonal_state = _apply_local_map_vectorized(diagonal_state, map_obj, qubits, n)
    success = float(np.trace(diagonal_state).real)
    if success <= 0.0:
        raise ValueError("evaluation produced non-positive model success")
    diagonal_state = diagonal_state / success
    h1 = np.array([[1.0, 1.0], [1.0, -1.0]], complex) / np.sqrt(2.0)
    hadamard = h1
    for _ in range(n - 1):
        hadamard = np.kron(hadamard, h1)
    measured = hadamard @ diagonal_state @ hadamard.conj().T
    probabilities = np.maximum(np.real(np.diag(measured)), 0.0)
    total = float(probabilities.sum())
    if not np.isfinite(total) or total <= 0.0:
        raise ValueError("evaluation produced non-positive probability mass")
    return total, float(success)


def _worker(n: int) -> dict[str, Any]:
    baseline_rss = _rss_bytes(os.getpid())
    print(
        json.dumps(
            {"event": "ready", "n": n, "baseline_rss_bytes": baseline_rss},
            sort_keys=True,
        ),
        flush=True,
    )
    if sys.stdin.readline().strip() != "start":
        raise RuntimeError("isolated worker did not receive the start signal")

    started = time.perf_counter()
    compile_started = time.perf_counter()
    compiled = _compile_representative(n)
    compile_elapsed = time.perf_counter() - compile_started

    map_started = time.perf_counter()
    maps = _build_maps(compiled)
    map_elapsed = time.perf_counter() - map_started

    evaluation_started = time.perf_counter()
    probability_sum, model_success = _evaluate(compiled, maps)
    evaluation_elapsed = time.perf_counter() - evaluation_started
    return {
        "n": n,
        "gate_count": len(compiled.gates),
        "map_count": len(maps),
        "compile_elapsed_seconds": compile_elapsed,
        "map_build_elapsed_seconds": map_elapsed,
        "evaluation_elapsed_seconds": evaluation_elapsed,
        "map_build_and_evaluation_elapsed_seconds": map_elapsed + evaluation_elapsed,
        "elapsed_seconds": time.perf_counter() - started,
        "probability_sum": probability_sum,
        "model_success": model_success,
        "state_matrix_shape": [2**n, 2**n],
        "full_circuit_superoperator_allocated": False,
        "status": "PASS",
    }


def _parse_json_line(line: str) -> dict[str, Any] | None:
    try:
        value = json.loads(line)
    except json.JSONDecodeError:
        return None
    return value if isinstance(value, dict) else None


def _worker_payload_valid(payload: dict[str, Any], expected_n: int) -> bool:
    if payload.get("status") != "PASS" or payload.get("n") != expected_n:
        return False
    if payload.get("full_circuit_superoperator_allocated") is not False:
        return False
    for field in (
        "compile_elapsed_seconds",
        "map_build_elapsed_seconds",
        "evaluation_elapsed_seconds",
        "map_build_and_evaluation_elapsed_seconds",
        "elapsed_seconds",
        "probability_sum",
        "model_success",
    ):
        value = payload.get(field)
        if not isinstance(value, (int, float)) or not np.isfinite(value) or value < 0.0:
            return False
    if payload.get("state_matrix_shape") != [2**expected_n, 2**expected_n]:
        return False
    if not np.isclose(float(payload["probability_sum"]), 1.0, atol=1e-10, rtol=1e-10):
        return False
    return all(
        isinstance(payload.get(field), int) and payload[field] >= 0
        for field in ("gate_count", "map_count")
    )


def _run_isolated(n: int, timeout_seconds: float) -> dict[str, Any]:
    command = [sys.executable, str(Path(__file__).resolve()), "--worker", "--n", str(n)]
    started = time.perf_counter()
    process = subprocess.Popen(
        command,
        cwd=REPO_ROOT,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
    )
    stdout_queue: queue.Queue[str] = queue.Queue()
    stdout_lines: list[str] = []

    def _read_stdout() -> None:
        assert process.stdout is not None
        for line in process.stdout:
            stdout_queue.put(line)

    reader = threading.Thread(target=_read_stdout, name=f"resource-pilot-stdout-{n}", daemon=True)
    reader.start()
    baseline_rss: int | None = None
    peak_rss: int | None = None
    ready_payload: dict[str, Any] | None = None
    start_sent = False
    timed_out = False
    while process.poll() is None:
        current = _rss_bytes(process.pid)
        if current is not None:
            peak_rss = current if peak_rss is None else max(peak_rss, current)
        try:
            while True:
                line = stdout_queue.get_nowait()
                stdout_lines.append(line)
                parsed = _parse_json_line(line.strip())
                if parsed is not None and parsed.get("event") == "ready":
                    ready_payload = parsed
        except queue.Empty:
            pass
        if ready_payload is not None and not start_sent:
            baseline_value = ready_payload.get("baseline_rss_bytes")
            if isinstance(baseline_value, int) and baseline_value >= 0:
                baseline_rss = baseline_value
                peak_rss = baseline_value if peak_rss is None else max(peak_rss, baseline_value)
            if process.stdin is not None:
                process.stdin.write("start\n")
                process.stdin.flush()
                process.stdin.close()
            start_sent = True
        if time.perf_counter() - started > timeout_seconds:
            timed_out = True
            process.kill()
            break
        time.sleep(0.01)
    if not start_sent and process.stdin is not None:
        process.stdin.close()
    process.wait()
    reader.join(timeout=5.0)
    while True:
        try:
            stdout_lines.append(stdout_queue.get_nowait())
        except queue.Empty:
            break
    stderr = process.stderr.read() if process.stderr is not None else ""
    payload: dict[str, Any] = {}
    if not timed_out and process.returncode == 0:
        for line in reversed(stdout_lines):
            parsed = _parse_json_line(line.strip())
            if parsed is not None and parsed.get("status") == "PASS":
                payload = parsed
                break
    valid_worker = _worker_payload_valid(payload, n)
    if timed_out or process.returncode != 0 or not valid_worker:
        measurement_status = "FAIL"
    elif baseline_rss is None or peak_rss is None:
        measurement_status = "INCONCLUSIVE"
    else:
        measurement_status = "PASS"
    growth = None if baseline_rss is None or peak_rss is None else max(0, peak_rss - baseline_rss)
    return {
        **payload,
        "n": n,
        "command": subprocess.list2cmdline(command),
        "command_argv": command,
        "return_code": process.returncode,
        "timed_out": timed_out,
        "parent_elapsed_seconds": time.perf_counter() - started,
        "baseline_rss_bytes": baseline_rss,
        "peak_rss_bytes": peak_rss,
        "rss_growth_bytes": growth,
        "measurement_status": measurement_status,
        "worker_payload_valid": valid_worker,
        "stderr": stderr.strip()[-2000:],
    }


def rss_status(case: dict[str, Any]) -> str:
    growth = case.get("rss_growth_bytes")
    if case.get("n") != 10:
        return "PASS" if case.get("peak_rss_bytes") is not None else "INCONCLUSIVE"
    if growth is None:
        return "INCONCLUSIVE"
    return "PASS" if int(growth) < N10_RSS_LIMIT_BYTES else "FAIL"


def aggregate_status(cases: list[dict[str, Any]]) -> str:
    if any(case.get("measurement_status") == "FAIL" for case in cases):
        return "FAIL"
    n10 = next((case for case in cases if case.get("n") == 10), None)
    if n10 is None or rss_status(n10) == "INCONCLUSIVE":
        return "INCONCLUSIVE"
    if rss_status(n10) == "FAIL":
        return "FAIL"
    return "PASS"


def _environment() -> dict[str, Any]:
    return {
        "python": sys.version,
        "python_executable": sys.executable,
        "numpy": np.__version__,
        "platform": platform.platform(),
        "machine": platform.machine(),
        "cpu_count": os.cpu_count(),
        "cwd": str(REPO_ROOT),
        "rss_sampler": "Windows GetProcessMemoryInfo working set, /proc/VmRSS fallback",
    }


def _deployment_source_hashes() -> dict[str, str]:
    paths = {
        "scripts/v4_tcdp/resource_pilot.py": Path(__file__),
        "src/merlin_iqp/deploy/compile.py": REPO_ROOT / "src" / "merlin_iqp" / "deploy" / "compile.py",
        "src/merlin_iqp/deploy/density.py": REPO_ROOT / "src" / "merlin_iqp" / "deploy" / "density.py",
        "src/merlin_iqp/deploy/maps.py": REPO_ROOT / "src" / "merlin_iqp" / "deploy" / "maps.py",
    }
    return {name: _file_sha256(path) for name, path in paths.items()}


def run(timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS) -> dict[str, Any]:
    cases = [_run_isolated(n, timeout_seconds) for n in PILOT_SIZES]
    n10 = next(case for case in cases if case["n"] == 10)
    growth = n10.get("rss_growth_bytes")
    criterion_status = rss_status(n10)
    return {
        "schema": "v4.resource-budget.v1",
        "generated_at_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "status": aggregate_status(cases),
        "scope": "bounded exact compiled-map build/evaluation resource pilot",
        "sizes": list(PILOT_SIZES),
        "commands": [case["command_argv"] for case in cases],
        "code_source": {
            "commit": _git_value("rev-parse", "HEAD"),
            "branch": _git_value("branch", "--show-current"),
            "dirty": bool(_git_value("status", "--porcelain")),
            "resource_pilot_sha256": _source_sha256(),
            "source_files_sha256": _deployment_source_hashes(),
        },
        "environment": _environment(),
        "allocation_contract": {
            "state_matrix": "(2**n, 2**n)",
            "full_circuit_superoperator": "forbidden and not allocated",
        },
        "n10_memory_growth_criterion": {
            "expression": "peak_rss - first_baseline_rss < 400 MiB",
            "limit_bytes": N10_RSS_LIMIT_BYTES,
            "observed_growth_bytes": growth,
            "observed_growth_mib": None if growth is None else growth / (1024 * 1024),
            "status": criterion_status,
        },
        "cases": cases,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--worker", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--n", type=int, choices=PILOT_SIZES)
    parser.add_argument("--timeout-seconds", type=float, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "results" / "v4_tcdp" / "deploy" / "resource_budget.json")
    args = parser.parse_args()
    if args.worker:
        if args.n is None:
            parser.error("--worker requires --n")
        print(json.dumps(_worker(args.n), sort_keys=True), flush=True)
        return
    report = run(timeout_seconds=args.timeout_seconds)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({"status": report["status"], "output": str(args.output)}, sort_keys=True))
    if report["status"] == "FAIL":
        raise SystemExit(1)


if __name__ == "__main__":
    main()
