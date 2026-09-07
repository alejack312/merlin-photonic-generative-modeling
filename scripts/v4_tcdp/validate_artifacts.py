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
