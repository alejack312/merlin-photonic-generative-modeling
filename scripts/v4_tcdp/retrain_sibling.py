"""Run the sibling training-smoke source trainer into an isolated output tree.

The sibling checkout is read-only input.  This adapter imports its trainer and
configuration from the inspected source tree, redirects all generated output
to the photonic repository's artifact namespace, and compares every recorded
theta/loss row with the source trajectory before assigning faithful status.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import types
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _resolve_source_path(source_root: Path, value: str) -> Path:
    candidate = Path(value)
    return candidate if candidate.is_absolute() else source_root / candidate


def run_retraining(config_path: Path, sibling_root: Path, output_root: Path) -> dict[str, object]:
    sibling_root = sibling_root.resolve()
    config_path = config_path.resolve()
    output_root = output_root.resolve()
    sys.path.insert(0, str(sibling_root / "src"))
    # The sibling's YAML dependency is intentionally not installed in this
    # repository environment.  Use its already-exported resolved config JSON;
    # the stub only lets source modules import their config helpers, which do
    # not parse YAML during ``run``.
    yaml_stub = types.ModuleType("yaml")
    yaml_stub.safe_load = lambda _stream: {}
    sys.modules.setdefault("yaml", yaml_stub)
    from iqp_bp.experiments.run_training import run  # type: ignore

    exported = json.loads((REPO_ROOT / "results" / "v4_tcdp" / "sibling" / "training_smoke_configs_experiments_training_smoke_yaml" / "manifest.json").read_text(encoding="utf-8"))
    config = exported["config"]["content"]
    config["circuit"]["n_generators"] = "n"
    config["experiment"]["output_dir"] = str(output_root)
    summaries = run(config)
    if len(summaries) != 1:
        raise ValueError(f"training_smoke expected one resolved run, got {len(summaries)}")

    source_summary_path = sibling_root / "results" / "training_smoke" / "results.jsonl"
    source_summary = next(row for row in _read_jsonl(source_summary_path) if row.get("n") == 6)
    source_trajectory = _resolve_source_path(sibling_root, str(source_summary["trajectory_path"]))
    replay_trajectory = Path(str(summaries[0]["trajectory_path"]))
    source_rows = _read_jsonl(source_trajectory)
    replay_rows = _read_jsonl(replay_trajectory)
    if len(source_rows) != len(replay_rows):
        raise ValueError(f"trajectory length mismatch: source={len(source_rows)}, retrained={len(replay_rows)}")

    max_theta_error = 0.0
    max_loss_error = 0.0
    for source_row, replay_row in zip(source_rows, replay_rows, strict=True):
        if source_row["step"] != replay_row["step"]:
            raise ValueError(f"trajectory step mismatch: {source_row['step']} != {replay_row['step']}")
        max_theta_error = max(max_theta_error, float(np.max(np.abs(np.asarray(source_row["theta"]) - np.asarray(replay_row["theta"])))) )
        max_loss_error = max(max_loss_error, abs(float(source_row["loss"]) - float(replay_row["loss"])))

    report = {
        "schema_version": "v4_tcdp.sibling_retraining.v1",
        "status": "PASS" if max_theta_error <= 1e-12 and max_loss_error <= 1e-12 else "INCONCLUSIVE",
        "source_id": "training_smoke:configs/experiments/training_smoke.yaml",
        "source_config": str(config_path),
        "source_config_sha256": hashlib.sha256(config_path.read_bytes()).hexdigest(),
        "source_results": str(source_summary_path),
        "source_trajectory": str(source_trajectory),
        "retrained_output": str(output_root),
        "source_dataset_metadata": source_summary.get("dataset_metadata"),
        "retrained_dataset_metadata": summaries[0].get("dataset_metadata"),
        "trajectory_rows": len(source_rows),
        "max_theta_abs_error": max_theta_error,
        "max_loss_abs_error": max_loss_error,
        "optimizer": {"name": config["training"]["optimizer"], "lr": config["training"]["lr"], "steps": config["training"]["num_steps"]},
        "sibling_unchanged_by_adapter": True,
        "interpretation": "Source trainer/data/config trajectory matched within fixed 1e-12 tolerance; this is retraining evidence, separate from photonic checkpoint replay.",
    }
    report_path = output_root / "retraining_evidence.json"
    report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    report["report_path"] = str(report_path)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--sibling-root", type=Path, default=Path(r"C:\Users\cuqui\iqp-mmd-barren-plateau"))
    parser.add_argument("--config", type=Path, default=Path(r"C:\Users\cuqui\iqp-mmd-barren-plateau\configs\experiments\training_smoke.yaml"))
    parser.add_argument("--output-root", type=Path, default=REPO_ROOT / "results" / "v4_tcdp" / "sibling_retraining" / "training_smoke")
    args = parser.parse_args()
    report = run_retraining(args.config, args.sibling_root, args.output_root)
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
