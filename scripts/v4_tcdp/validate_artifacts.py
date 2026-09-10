"""Fail-closed validation for v4 JSON and JSONL evidence artifacts."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path
from typing import Any


def _reject_constant(value: str) -> None:
    raise ValueError(f"non-finite JSON constant {value!r}")


def _walk_finite(value: Any, path: str, failures: list[str]) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        failures.append(f"{path}: non-finite numeric value")
    elif isinstance(value, dict):
        for key, child in value.items():
            _walk_finite(child, f"{path}/{key}", failures)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            _walk_finite(child, f"{path}/{index}", failures)


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"), parse_constant=_reject_constant)


def _validate_payload_hash(value: Any, path: Path, failures: list[str]) -> bool:
    if not isinstance(value, dict) or "payload_sha256" not in value:
        return False
    expected = value["payload_sha256"]
    without_hash = dict(value)
    without_hash.pop("payload_sha256")
    actual = hashlib.sha256(
        json.dumps(without_hash, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    ).hexdigest()
    if actual != expected:
        failures.append(f"{path}: payload_sha256 mismatch")
    return True


def _finite_number(value: Any) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(float(value))


def _is_current_comparison_artifact(path: Path) -> bool:
    """Apply the v2 semantic contract to current namespaces only.

    Older committed comparison outputs are retained historical evidence and
    predate the support-provenance fields. They remain parseable, while every
    correction namespace and every ad-hoc artifact is checked strictly.
    """

    if "results" not in path.parts:
        return True
    return any(part.startswith("correction") for part in path.parts)


def _validate_semantics(value: Any, path: Path, failures: list[str]) -> None:
    """Check invariants that JSON syntax and hashes cannot establish."""

    if not isinstance(value, dict):
        return
    schema = value.get("schema_version", value.get("schema"))
    if schema == "v4_tcdp.matched_comparison.v1":
        arms = value.get("arms")
        metrics = value.get("metrics")
        if not isinstance(arms, list) or not isinstance(metrics, dict) or not arms:
            failures.append(f"{path}: matched comparison must contain non-empty arms and metrics")
            return
        if _is_current_comparison_artifact(path):
            target_hash = value.get("target_hash")
            if not isinstance(target_hash, str) or len(target_hash) != 64 or any(
                character not in "0123456789abcdef" for character in target_hash.lower()
            ):
                failures.append(f"{path}: current matched comparison lacks a valid target_hash")
        arm_keys = set()
        for arm in arms:
            if not isinstance(arm, dict):
                failures.append(f"{path}: matched comparison arm is not an object")
                continue
            key = f"{arm.get('stage')}:{arm.get('backend_id')}"
            arm_keys.add(key)
            acceptance = arm.get("acceptance_mass")
            if not _finite_number(acceptance) or not 0.0 < float(acceptance) <= 1.0:
                failures.append(f"{path}: invalid arm acceptance_mass for {key}")
        if arm_keys != set(metrics):
            failures.append(f"{path}: metrics keys do not match arm keys")
        for key, row in metrics.items():
            if not isinstance(row, dict):
                failures.append(f"{path}: metric row {key} is not an object")
                continue
            acceptance = row.get("acceptance_mass")
            attempts = row.get("attempts_per_accepted_sample")
            if not _finite_number(acceptance) or not 0.0 < float(acceptance) <= 1.0:
                failures.append(f"{path}: invalid metric acceptance_mass for {key}")
            elif not _finite_number(attempts) or not math.isclose(float(attempts), 1.0 / float(acceptance), rel_tol=0.0, abs_tol=1e-12):
                failures.append(f"{path}: attempts_per_accepted_sample is inconsistent for {key}")
            support = row.get("support_validity")
            if support is not None and (not _finite_number(support) or not 0.0 <= float(support) <= 1.0):
                failures.append(f"{path}: invalid support_validity for {key}")
            if support is not None and _is_current_comparison_artifact(path):
                if row.get("support_definition") != "underlying target support where p > 1e-6":
                    failures.append(f"{path}: support_definition is missing or inconsistent for {key}")
                if row.get("support_validity_basis") != "underlying conditional probability vector":
                    failures.append(f"{path}: support_validity_basis is missing or inconsistent for {key}")
                if row.get("support_threshold") != 1e-6:
                    failures.append(f"{path}: support_threshold is missing or inconsistent for {key}")
                if not isinstance(row.get("target_support_size"), int) or isinstance(row.get("target_support_size"), bool) or row["target_support_size"] < 1:
                    failures.append(f"{path}: target_support_size evidence is missing or invalid for {key}")
                target_mass = row.get("target_support_mass")
                if not _finite_number(target_mass) or not 0.0 <= float(target_mass) <= 1.0:
                    failures.append(f"{path}: target_support_mass evidence is missing or invalid for {key}")
    elif schema in {"v4_tcdp.photonic_ring.v1", "v4_tcdp.photonic_ring.v2"}:
        direct = value.get("direct")
        if isinstance(direct, dict):
            accepted = direct.get("absolute_accepted_mass")
            rejected = direct.get("rejected_mass")
            if not _finite_number(accepted) or not 0.0 < float(accepted) <= 1.0:
                if value.get("status") == "PASS":
                    failures.append(f"{path}: PASS photonic artifact has non-positive acceptance")
            if _finite_number(accepted) and _finite_number(rejected) and not math.isclose(float(accepted) + float(rejected), 1.0, rel_tol=0.0, abs_tol=1e-12):
                failures.append(f"{path}: accepted and rejected masses do not sum to one")
            vector = direct.get("decoded_conditional_vector")
            if isinstance(vector, list) and (not vector or any(not _finite_number(item) or float(item) < 0.0 for item in vector) or not math.isclose(sum(float(item) for item in vector), 1.0, rel_tol=0.0, abs_tol=1e-10)):
                failures.append(f"{path}: decoded conditional vector is not a probability vector")
    elif schema == "v4.resource-budget.v1":
        sizes = value.get("sizes")
        cases = value.get("cases")
        if sizes != [4, 6, 8, 10] or not isinstance(cases, list) or [case.get("n") for case in cases if isinstance(case, dict)] != [4, 6, 8, 10]:
            failures.append(f"{path}: resource pilot must contain exactly the registered sizes [4, 6, 8, 10]")
        for case in cases if isinstance(cases, list) else []:
            if not isinstance(case, dict):
                failures.append(f"{path}: resource case is not an object")
                continue
            status = str(case.get("measurement_status", "")).upper()
            if status not in {"PASS", "FAIL", "UNKNOWN", "INCONCLUSIVE"}:
                failures.append(f"{path}: invalid resource measurement_status")
        if str(value.get("status", "")).upper() == "PASS" and any(
            not isinstance(case, dict) or str(case.get("measurement_status", "")).upper() != "PASS"
            for case in cases if isinstance(cases, list)
        ):
            failures.append(f"{path}: resource PASS requires every registered measurement to PASS")


def validate(root: Path) -> dict[str, int | str]:
    failures: list[str] = []
    json_files = 0
    jsonl_rows = 0
    payload_hashes = 0
    for path in sorted(root.rglob("*.json")):
        json_files += 1
        try:
            value = _load_json(path)
            _walk_finite(value, str(path), failures)
            _validate_semantics(value, path, failures)
            payload_hashes += int(_validate_payload_hash(value, path, failures))
        except Exception as error:
            failures.append(f"{path}: {type(error).__name__}: {error}")
    for path in sorted(root.rglob("*.jsonl")):
        for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            jsonl_rows += 1
            try:
                value = json.loads(line, parse_constant=_reject_constant)
                _walk_finite(value, f"{path}:{line_number}", failures)
            except Exception as error:
                failures.append(f"{path}:{line_number}: {type(error).__name__}: {error}")
    result: dict[str, int | str] = {
        "root": str(root),
        "json_files": json_files,
        "jsonl_rows": jsonl_rows,
        "payload_hashes": payload_hashes,
        "failure_count": len(failures),
        "status": "PASS" if not failures else "FAIL",
    }
    if failures:
        result["failures"] = "\n".join(failures[:20])
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("results/v4_tcdp"))
    args = parser.parse_args()
    result = validate(args.root)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
