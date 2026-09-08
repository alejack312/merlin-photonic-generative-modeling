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


def validate(
    *, sibling_root: Path, source_root: Path, rerun_root: Path, source_config: Path
) -> dict[str, Any]:
    sibling_root = sibling_root.resolve()
    source_root = source_root.resolve()
    rerun_root = rerun_root.resolve()
    source_config = source_config.resolve()
    source_results = source_root / "results.jsonl"
    source_resolved_config = source_root / "config.json"
    rerun_results = rerun_root / "results.jsonl"
    for path in (source_config, source_results, source_resolved_config, rerun_results):
        if not path.is_file():
            raise FileNotFoundError(path)

    source_identity_before = git_source_identity(
        sibling_root,
        include_paths=("src", "configs", "pyproject.toml", "setup.py", "README.md"),
    )
    if source_identity_before.get("dirty"):
        raise ValueError("sibling checkout is dirty; refusing faithful validation")

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
    status = "PASS" if unchanged and cells and all(cell["status"] == "PASS" for cell in cells) else "FAIL"
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
        "source_results": str(source_results),
        "source_results_sha256": _sha256(source_results),
        "rerun_results": str(rerun_results),
        "rerun_results_sha256": _sha256(rerun_results),
        "rerun_output": str(rerun_root),
        "adaptation": {
            "changed_fields": ["experiment.output_dir", "experiment.name", "experiment.description"],
            "reason": "source runner output was redirected outside the read-only sibling checkout; selected circuit, dataset, kernel and training settings were retained",
        },
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
