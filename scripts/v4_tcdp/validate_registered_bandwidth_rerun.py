"""Validate an already executed bounded sibling bandwidth rerun.

This validator compares the isolated output of the pinned sibling runner with
the sibling's registered trajectories. It never imports serialized model
objects and never writes to the sibling checkout. The runner's four cells and
20-step budget are intentionally fixed by the supplied source artifacts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys
from typing import Any

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))
sys.path.insert(0, str(REPO_ROOT / "scripts" / "v4_tcdp"))

from merlin_iqp.experiments.sibling_import import git_source_identity  # noqa: E402
import retrain_sibling as retrain  # noqa: E402


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _resolve_rerun_path(value: object) -> Path:
    path = Path(str(value))
    return path.resolve() if path.is_absolute() else (REPO_ROOT / path).resolve()


def _cell_key(summary: dict[str, Any]) -> tuple[tuple[str, object], ...]:
    return retrain._source_cell_key(summary)


_MISSING = object()
_OUTPUT_REDIRECT_FIELDS = {
    "experiment.description",
    "experiment.name",
    "experiment.output_dir",
}
_RESOLVED_DEFAULTS: dict[str, object] = {
    "circuit.allow_legacy_families": False,
    "forge.plateau_agreement.label_kind": "concentration",
    "init.data_dependent.fallback_std": 0.1,
    "init.data_dependent.method": "parity",
    "init.data_dependent.scale": 0.1,
}


def _config_differences(
    source: object, rerun: object, path: str = ""
) -> list[dict[str, object]]:
    if isinstance(source, dict) and isinstance(rerun, dict):
        differences: list[dict[str, object]] = []
        for name in sorted(set(source) | set(rerun)):
            child_path = f"{path}.{name}" if path else name
            differences.extend(
                _config_differences(
                    source.get(name, _MISSING), rerun.get(name, _MISSING), child_path
                )
            )
        return differences
    if source is _MISSING or rerun is _MISSING or source != rerun:
        return [
            {
                "field": path,
                "source": "<missing>" if source is _MISSING else source,
                "rerun": "<missing>" if rerun is _MISSING else rerun,
            }
        ]
    return []


def _compare_resolved_configs(
    source: dict[str, Any], rerun: dict[str, Any]
) -> dict[str, object]:
    differences = _config_differences(source, rerun)
    output_redirects = [
        difference
        for difference in differences
        if difference["field"] in _OUTPUT_REDIRECT_FIELDS
    ]
    resolved_defaults = []
    unexpected = []
    for difference in differences:
        field = str(difference["field"])
        if field in _OUTPUT_REDIRECT_FIELDS:
            continue
        expected = _RESOLVED_DEFAULTS.get(field, _MISSING)
        if (
            expected is not _MISSING
            and difference["source"] == "<missing>"
            and difference["rerun"] == expected
        ):
            resolved_defaults.append(difference)
        else:
            unexpected.append(difference)
    return {
        "status": "PASS" if not unexpected else "FAIL",
        "changed_fields": [str(difference["field"]) for difference in differences],
        "output_redirected_fields": output_redirects,
        "resolved_default_fields": resolved_defaults,
        "unexpected_fields": unexpected,
        "note": (
            "The source runner's active circuit, dataset, kernel and training settings "
            "must be identical; output metadata is redirected, and only the explicitly "
            "listed resolver defaults may be materialized in the isolated rerun."
        ),
    }


def validate(
    *, sibling_root: Path, source_root: Path, rerun_root: Path, source_config: Path
) -> dict[str, Any]:
    sibling_root = sibling_root.resolve()
    source_root = source_root.resolve()
    rerun_root = rerun_root.resolve()
    source_config = source_config.resolve()
    source_results = source_root / "results.jsonl"
    source_resolved_config = source_root / "config.json"
    rerun_config = rerun_root / "config.json"
    rerun_results = rerun_root / "results.jsonl"
    for path in (
        source_config,
        source_results,
        source_resolved_config,
        rerun_config,
        rerun_results,
    ):
        if not path.is_file():
            raise FileNotFoundError(path)

    source_identity_before = git_source_identity(
        sibling_root,
        include_paths=("src", "configs", "pyproject.toml", "setup.py", "README.md"),
    )
    if source_identity_before.get("dirty"):
        raise ValueError("sibling checkout is dirty; refusing faithful validation")

    config_comparison = _compare_resolved_configs(
        json.loads(source_resolved_config.read_text(encoding="utf-8")),
        json.loads(rerun_config.read_text(encoding="utf-8")),
    )
    source_rows = retrain._read_jsonl(source_results)
    rerun_rows = retrain._read_jsonl(rerun_results)
    rerun_by_key = {_cell_key(row): row for row in rerun_rows}
    if len(rerun_by_key) != len(rerun_rows):
        raise ValueError("rerun contains duplicate cell identities")

    cells: list[dict[str, Any]] = []
    for source_row in source_rows:
        key = _cell_key(source_row)
        rerun_row = rerun_by_key.get(key)
        if rerun_row is None:
            raise ValueError(f"rerun is missing source cell {key!r}")
        source_trajectory = retrain._resolve_source_path(
            sibling_root, source_row["trajectory_path"]
        ).resolve()
        rerun_trajectory = _resolve_rerun_path(rerun_row["trajectory_path"])
        source_values = retrain._read_jsonl(source_trajectory)
        rerun_values = retrain._read_jsonl(rerun_trajectory)
        expected_steps = tuple(int(step) for step in source_row["written_steps"])
        expected_shape = tuple(np.asarray(source_values[0]["theta"], dtype=np.float64).shape)
        comparison = retrain._compare_trajectories(
            source_values,
            rerun_values,
            expected_step_ids=expected_steps,
            expected_theta_shape=expected_shape,
        )
        cells.append(
            {
                **comparison,
                "source_cell": {name: value for name, value in key},
                "source_trajectory": str(source_trajectory),
                "rerun_trajectory": str(rerun_trajectory),
                "source_trajectory_sha256": _sha256(source_trajectory),
                "rerun_trajectory_sha256": _sha256(rerun_trajectory),
                "source_final_loss": source_row.get("final_loss"),
                "rerun_final_loss": rerun_row.get("final_loss"),
                "source_dataset_metadata": source_row.get("dataset_metadata"),
                "rerun_dataset_metadata": rerun_row.get("dataset_metadata"),
            }
        )

    source_identity_after = git_source_identity(
        sibling_root,
        include_paths=("src", "configs", "pyproject.toml", "setup.py", "README.md"),
    )
    unchanged = source_identity_before == source_identity_after
    status = (
        "PASS"
        if (
            unchanged
            and config_comparison["status"] == "PASS"
            and cells
            and all(cell["status"] == "PASS" for cell in cells)
        )
        else "FAIL"
    )
    return {
        "schema_version": "v4_tcdp.sibling_bandwidth_validation.v1",
        "status": status,
        "reproduction_kind": "faithful_source_retraining",
        "registered_budget": {
            "cells": len(source_rows),
            "steps": sorted({int(step) for row in source_rows for step in row["written_steps"]}),
            "n": sorted({int(row["n"]) for row in source_rows}),
            "bandwidths": sorted(float(row["bandwidth"]) for row in source_rows),
        },
        "source_identity_before": source_identity_before,
        "source_identity_after": source_identity_after,
        "sibling_unchanged": unchanged,
        "source_config": str(source_config),
        "source_config_sha256": _sha256(source_config),
        "resolved_source_config": str(source_resolved_config),
        "resolved_source_config_sha256": _sha256(source_resolved_config),
        "resolved_rerun_config": str(rerun_config),
        "resolved_rerun_config_sha256": _sha256(rerun_config),
        "source_results": str(source_results),
        "source_results_sha256": _sha256(source_results),
        "rerun_results": str(rerun_results),
        "rerun_results_sha256": _sha256(rerun_results),
        "rerun_output": str(rerun_root),
        "config_comparison": config_comparison,
        "trajectory_tolerance": 1.0e-12,
        "cells": cells,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sibling-root", type=Path, default=Path(r"C:\Users\cuqui\iqp-mmd-barren-plateau"))
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--rerun-root", type=Path, required=True)
    parser.add_argument("--source-config", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = validate(
        sibling_root=args.sibling_root,
        source_root=args.source_root,
        rerun_root=args.rerun_root,
        source_config=args.source_config,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
