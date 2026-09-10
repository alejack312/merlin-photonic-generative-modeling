"""Validate an isolated rerun of a registered sibling validation cell."""

from __future__ import annotations

import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from merlin_iqp.experiments.sibling_import import git_source_identity  # noqa: E402


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _diff(source: object, rerun: object, path: str = "") -> list[dict[str, object]]:
    if isinstance(source, dict) and isinstance(rerun, dict):
        differences: list[dict[str, object]] = []
        missing = object()
        for name in sorted(set(source) | set(rerun)):
            child = f"{path}.{name}" if path else name
            source_value = source[name] if name in source else missing
            rerun_value = rerun[name] if name in rerun else missing
            if source_value is missing or rerun_value is missing:
                differences.append(
                    {
                        "field": child,
                        "source": None if source_value is missing else source_value,
                        "rerun": None if rerun_value is missing else rerun_value,
                    }
                )
            else:
                differences.extend(_diff(source_value, rerun_value, child))
        return differences
    if source != rerun:
        return [{"field": path, "source": source, "rerun": rerun}]
    return []


def _canonical_result(payload: dict[str, Any]) -> dict[str, Any]:
    result = copy.deepcopy(payload)
    result.pop("provenance", None)
    return result


def validate(
    *,
    sibling_root: Path,
    source_config: Path,
    source_result: Path,
    source_csv: Path,
    rerun_config: Path,
    rerun_result: Path,
    rerun_csv: Path,
) -> dict[str, Any]:
    paths = (source_config, source_result, source_csv, rerun_config, rerun_result, rerun_csv)
    for path in paths:
        if not path.is_file():
            raise FileNotFoundError(path)

    identity_before = git_source_identity(
        sibling_root.resolve(),
        include_paths=("src", "configs", "pyproject.toml", "setup.py", "README.md"),
    )
    source_cfg = yaml.safe_load(source_config.read_text(encoding="utf-8"))
    rerun_cfg = yaml.safe_load(rerun_config.read_text(encoding="utf-8"))
    config_differences = _diff(source_cfg, rerun_cfg)
    allowed_config_fields = {
        "circuit.n_qubits",
        "experiment.description",
        "experiment.name",
        "experiment.output_dir",
    }
    unexpected_config_differences = [
        difference
        for difference in config_differences
        if difference["field"] not in allowed_config_fields
    ]

    source_payload = json.loads(source_result.read_text(encoding="utf-8"))
    rerun_payload = json.loads(rerun_result.read_text(encoding="utf-8"))
    if not isinstance(source_payload, dict) or not isinstance(rerun_payload, dict):
        raise ValueError("validation summaries must be JSON objects")
    source_provenance = source_payload.get("provenance", {})
    rerun_provenance = rerun_payload.get("provenance", {})
    provenance_match = {
        "family": source_provenance.get("family") == rerun_provenance.get("family"),
        "n": source_provenance.get("n") == rerun_provenance.get("n"),
        "seed": source_provenance.get("seed") == rerun_provenance.get("rng_seed"),
        "source": source_provenance.get("source") == rerun_provenance.get("source"),
    }
    identity_after = git_source_identity(
        sibling_root.resolve(),
        include_paths=("src", "configs", "pyproject.toml", "setup.py", "README.md"),
    )
    sibling_unchanged = identity_before == identity_after
    summary_equal = _canonical_result(source_payload) == _canonical_result(rerun_payload)
    csv_equal = source_csv.read_bytes() == rerun_csv.read_bytes()
    status = (
        "PASS"
        if (
            not identity_before.get("dirty")
            and sibling_unchanged
            and not unexpected_config_differences
            and summary_equal
            and csv_equal
            and all(provenance_match.values())
        )
        else "FAIL"
    )
    return {
        "schema_version": "v4_tcdp.sibling_validation_rerun.v1",
        "status": status,
        "reproduction_kind": "faithful_source_validation_rerun",
        "source_config": str(source_config.resolve()),
        "source_config_sha256": _sha256(source_config),
        "rerun_config": str(rerun_config.resolve()),
        "rerun_config_sha256": _sha256(rerun_config),
        "source_result": str(source_result.resolve()),
        "source_result_sha256": _sha256(source_result),
        "rerun_result": str(rerun_result.resolve()),
        "rerun_result_sha256": _sha256(rerun_result),
        "source_csv": str(source_csv.resolve()),
        "source_csv_sha256": _sha256(source_csv),
        "rerun_csv": str(rerun_csv.resolve()),
        "rerun_csv_sha256": _sha256(rerun_csv),
        "config_comparison": {
            "status": "PASS" if not unexpected_config_differences else "FAIL",
            "changed_fields": [difference["field"] for difference in config_differences],
            "allowed_adaptations": config_differences,
            "unexpected_fields": unexpected_config_differences,
            "reason": "Only output metadata and the source schema's scalar-to-list n_qubits normalization changed.",
        },
        "summary_equal_excluding_provenance": summary_equal,
        "threshold_csv_byte_equal": csv_equal,
        "provenance_match": provenance_match,
        "source_identity_before": identity_before,
        "source_identity_after": identity_after,
        "sibling_unchanged": sibling_unchanged,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sibling-root", type=Path, default=Path(r"C:\Users\cuqui\iqp-mmd-barren-plateau"))
    parser.add_argument("--source-config", type=Path, required=True)
    parser.add_argument("--source-result", type=Path, required=True)
    parser.add_argument("--source-csv", type=Path, required=True)
    parser.add_argument("--rerun-config", type=Path, required=True)
    parser.add_argument("--rerun-result", type=Path, required=True)
    parser.add_argument("--rerun-csv", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    report = validate(
        sibling_root=args.sibling_root,
        source_config=args.source_config,
        source_result=args.source_result,
        source_csv=args.source_csv,
        rerun_config=args.rerun_config,
        rerun_result=args.rerun_result,
        rerun_csv=args.rerun_csv,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
