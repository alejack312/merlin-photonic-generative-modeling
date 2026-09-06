"""Replay a safe sibling checkpoint through the supported ideal construction.

This is a frozen-checkpoint adapter, not a claim that the sibling optimizer or
dataset has been independently rerun. Python pickle/joblib/torch artifacts are
never loaded.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

MAX_COMPILED_N = 10

from merlin_iqp.classical import IQPModel  # noqa: E402
from merlin_iqp.classical._validation import binary_matrix, finite_vector  # noqa: E402
from merlin_iqp.deploy import apply_compiled_density, compile_generators  # noqa: E402
from merlin_iqp.experiments.sibling_import import (  # noqa: E402
    PINNED_SIBLING_COMMIT,
    git_source_identity,
    load_export_manifest,
    regenerate_training_smoke_data,
)


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _vector(mapping: dict[str, float]) -> np.ndarray:
    return np.array([mapping[key] for key in sorted(mapping)], dtype=np.float64)


def _slug(value: object) -> str:
    text = str(value)
    return "".join(character if character.isalnum() or character in "-_" else "_" for character in text).strip("_") or "unknown"


def _config_hash(config: object) -> str:
    encoded = json.dumps(config, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def _numeric_scalar(value: object, *, name: str, integer: bool = False) -> float | int:
    array = np.asarray(value)
    if array.ndim != 0 or not np.issubdtype(array.dtype, np.number):
        raise ValueError(f"checkpoint {name} must be a numeric scalar")
    scalar = float(array.item())
    if not np.isfinite(scalar):
        raise ValueError(f"checkpoint {name} must be finite")
    if integer:
        if int(scalar) != scalar or scalar < 0:
            raise ValueError(f"checkpoint {name} must be a non-negative integer")
        return int(scalar)
    return scalar


def _checkpoint_candidates(manifest: dict[str, Any], sibling_root: Path) -> list[Path]:
    candidates = [
        (sibling_root / Path(item)).resolve()
        for item in manifest.get("result_evidence", [])
        if str(item).replace("\\", "/").endswith(".npz")
    ]
    return [
        path
        for path in candidates
        if path.is_file() and path.name.startswith("step_")
    ]


def _latest_checkpoint_per_run(candidates: list[Path]) -> list[Path]:
    by_run: dict[Path, list[Path]] = {}
    for path in candidates:
        by_run.setdefault(path.parent.parent, []).append(path)
    return [
        max(paths, key=lambda path: int(path.stem.removeprefix("step_")))
        for _, paths in sorted(by_run.items(), key=lambda item: item[0].as_posix().lower())
    ]


def _write_blocked_manifest(
    *, manifest_path: Path, manifest: dict[str, Any], sibling_root: Path, output_root: Path
) -> dict[str, object]:
    source_id = str(manifest.get("source_id", manifest_path.stem))
    source_key = _slug(source_id)
    destination = (output_root / source_key / "blocked").resolve()
    if destination.exists() and any(destination.iterdir()):
        raise FileExistsError(f"replay disposition already exists: {destination}")
    destination.mkdir(parents=True, exist_ok=True)
    source_identity = git_source_identity(
        sibling_root, include_paths=("src", "configs", "pyproject.toml", "setup.py", "README.md")
    )
    result = {
        "schema_version": "v4_tcdp.sibling_replay.v2",
        "status": "blocked",
        "reproduction_kind": "checkpoint_replay",
        "reason": "No safe NPZ checkpoint with G/theta/step/loss is present in the registered result evidence.",
        "source_id": source_id,
        "source_manifest": str(manifest_path.resolve()),
        "source_manifest_sha256": _sha256(manifest_path),
        "source_config_sha256": manifest.get("config", {}).get("sha256")
        if isinstance(manifest.get("config"), dict)
        else None,
        "source_commit": source_identity.get("observed_commit"),
        "source_tree_identity": source_identity.get("tree_identity"),
        "source_dirty": source_identity.get("dirty"),
        "missing_inputs": ["safe NPZ checkpoint containing G, theta, step and loss"],
        "missing_input_paths": [
            str(
                Path(
                    next(
                        (
                            item.get("resolved")
                            for item in manifest.get("config", {}).get("declared_paths", [])
                            if isinstance(item, dict) and item.get("field") == "output_dir"
                        ),
                        sibling_root / "results",
                    )
                )
                / "checkpoints"
                / "*.npz"
            )
        ],
        "available_result_evidence": manifest.get("result_evidence", []),
        "input_hashes": {"checkpoint": None},
        "output_files": ["manifest.json"],
        "unsafe_serialization_loaded": False,
        "command": [
            "venv/Scripts/python.exe",
            "scripts/v4_tcdp/replay_sibling.py",
            str(manifest_path),
        ],
        "namespace": {"destination": str(destination)},
    }
    (destination / "manifest.json").write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8"
    )
    result["manifest_path"] = str(destination / "manifest.json")
    return result


def replay_export(
    manifest_path: Path,
    sibling_root: Path,
    output_root: Path,
    *,
    checkpoint_path: Path | None = None,
    run_key: str | None = None,
) -> dict[str, object]:
    manifest = load_export_manifest(manifest_path)
    source_identity = git_source_identity(sibling_root, include_paths=("src", "configs", "pyproject.toml", "setup.py", "README.md"))
    requested_pin = manifest.get("requested_pinned_commit", PINNED_SIBLING_COMMIT)
    if manifest.get("source_commit") != source_identity.get("observed_commit"):
        raise ValueError("export manifest source commit does not match the observed sibling checkout")
    if manifest.get("source_tree_identity") and manifest["source_tree_identity"] != source_identity.get("tree_identity"):
        raise ValueError("export manifest source tree identity does not match the observed sibling checkout")
    if manifest.get("source_pin_status") == "MISMATCH" or source_identity.get("observed_commit") != requested_pin or source_identity.get("dirty"):
        pin_status = "MISMATCH"
    else:
        pin_status = "MATCH"
    checkpoints = _checkpoint_candidates(manifest, sibling_root)
    if not checkpoints:
        raise FileNotFoundError("export manifest contains no available safe NPZ checkpoint")
    checkpoint = (checkpoint_path or sorted(checkpoints)[-1]).resolve()
    if checkpoint not in checkpoints:
        raise ValueError(f"requested checkpoint is not registered in the export manifest: {checkpoint}")
    with np.load(checkpoint, allow_pickle=False) as payload:
        required = {"G", "theta", "step", "loss"}
        if not required.issubset(payload.files):
            raise ValueError(f"checkpoint is missing required fields: {sorted(required - set(payload.files))}")
        try:
            generator = binary_matrix(payload["G"], name="source generator")
            theta = finite_vector(payload["theta"], name="source theta", length=len(generator))
            step = int(_numeric_scalar(payload["step"], name="step", integer=True))
            source_loss = float(_numeric_scalar(payload["loss"], name="loss"))
        except (TypeError, ValueError) as error:
            raise ValueError(f"invalid sibling checkpoint fields: {error}") from error
    source_config = manifest["config"].get("content", manifest["config"])
    checkpoint_hash = _sha256(checkpoint)
    config_hash = _config_hash(source_config)
    source_manifest_hash = _sha256(manifest_path)
    source_key = f"{_slug(manifest['source_id'])}__{_slug(source_identity.get('observed_commit'))[:16]}__{_slug(source_identity.get('tree_identity'))[:16]}"
    run_component = f"run_{_slug(run_key)}" if run_key else None
    destination = output_root / source_key
    if run_component:
        destination /= run_component
    destination = destination / f"checkpoint_{checkpoint_hash[:16]}" / f"config_{config_hash[:16]}" / f"step_{step:04d}"
    if destination.exists() and any(destination.iterdir()):
        raise FileExistsError(f"replay destination already contains an artifact: {destination}")
    model = IQPModel(generator, theta, provenance={"source_commit": source_identity.get("observed_commit"), "source_id": manifest["source_id"]})
    raw = model.probability_vector_exact()
    destination.mkdir(parents=True, exist_ok=True)
    np.save(destination / "raw.npy", raw)
    if model.n > MAX_COMPILED_N:
        result = {
            "schema_version": "v4_tcdp.sibling_replay.v2",
            "status": "reference_only",
            "reproduction_kind": "checkpoint_replay_raw_only",
            "reason": (
                f"Raw exact replay completed at n={model.n}; the bounded compiled-density "
                f"adapter rejects n>{MAX_COMPILED_N} before allocating a 2^n by 2^n density matrix."
            ),
            "source_id": manifest["source_id"],
            "source_commit": source_identity.get("observed_commit"),
            "source_branch": source_identity.get("observed_branch"),
            "source_dirty": source_identity.get("dirty"),
            "source_tree_identity": source_identity.get("tree_identity"),
            "source_pin_status": pin_status,
            "requested_pinned_commit": requested_pin,
            "checkpoint": {"path": str(checkpoint), "sha256": checkpoint_hash, "step": step, "source_loss": source_loss},
            "source_manifest_sha256": source_manifest_hash,
            "source_config_sha256": manifest.get("config", {}).get("sha256")
            if isinstance(manifest.get("config"), dict)
            else None,
            "input_hashes": {
                "checkpoint": checkpoint_hash,
                "generator": hashlib.sha256(np.ascontiguousarray(generator).tobytes()).hexdigest(),
                "theta": hashlib.sha256(np.ascontiguousarray(theta).tobytes()).hexdigest(),
            },
            "generator_hash": hashlib.sha256(np.ascontiguousarray(generator).tobytes()).hexdigest(),
            "theta_hash": hashlib.sha256(np.ascontiguousarray(theta).tobytes()).hexdigest(),
            "n": model.n,
            "kernel": {"source_type": source_config.get("kernel", {}).get("type"), "source_bandwidth": source_config.get("kernel", {}).get("bandwidth"), "comparison_kernel": "not computed; target data is not part of checkpoint replay"},
            "raw_compiled_tvd": None,
            "compiled_deployed_tvd": None,
            "deployed_acceptance_mass": None,
            "artifacts": {"raw": "raw.npy", "manifest": "manifest.json"},
            "output_files": ["raw.npy", "manifest.json"],
            "dataset_regeneration": None,
            "faithful_retraining": {"status": "not_run", "reason": "checkpoint replay does not rerun the source optimizer"},
            "namespace": {"source_key": source_key, "run_key": run_key, "checkpoint_hash": checkpoint_hash, "config_hash": config_hash, "destination": str(destination)},
            "capability": {"compiled_density_max_n": MAX_COMPILED_N, "compiled_status": "not_attempted"},
            "unsafe_serialization_loaded": False,
            "command": ["venv/Scripts/python.exe", "scripts/v4_tcdp/replay_sibling.py", str(manifest_path)],
        }
        (destination / "manifest.json").write_text(
            json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8"
        )
        return result
    compiled = compile_generators(generator, theta, quantize=True)
    compiled_vector = _vector(apply_compiled_density(compiled)[0])
    deployed = compiled
    deployed_mapping, acceptance = apply_compiled_density(deployed)
    deployed_vector = _vector(deployed_mapping)
    np.save(destination / "compiled.npy", compiled_vector)
    np.save(destination / "deployed.npy", deployed_vector)
    data_regeneration: dict[str, object] | None = None
    if str(manifest["source_id"]).startswith("training_smoke:"):
        data, data_regeneration = regenerate_training_smoke_data(sibling_root)
        np.save(destination / "source_data.npy", data)
    result = {
        "schema_version": "v4_tcdp.sibling_replay.v1",
        "status": "adapted_reproduction",
        "reason": "frozen source checkpoint replayed through the ideal photonic construction; source SGD/data trajectory was not rerun",
        "source_id": manifest["source_id"],
        "source_commit": source_identity.get("observed_commit"),
        "source_branch": source_identity.get("observed_branch"),
        "source_dirty": source_identity.get("dirty"),
        "source_tree_identity": source_identity.get("tree_identity"),
        "source_pin_status": pin_status,
        "requested_pinned_commit": requested_pin,
        "checkpoint": {"path": str(checkpoint), "sha256": checkpoint_hash, "step": step, "source_loss": source_loss},
        "source_manifest_sha256": source_manifest_hash,
        "source_config_sha256": manifest.get("config", {}).get("sha256")
        if isinstance(manifest.get("config"), dict)
        else None,
        "input_hashes": {
            "checkpoint": checkpoint_hash,
            "generator": hashlib.sha256(np.ascontiguousarray(generator).tobytes()).hexdigest(),
            "theta": hashlib.sha256(np.ascontiguousarray(theta).tobytes()).hexdigest(),
        },
        "generator_hash": hashlib.sha256(np.ascontiguousarray(generator).tobytes()).hexdigest(),
        "theta_hash": hashlib.sha256(np.ascontiguousarray(theta).tobytes()).hexdigest(),
        "n": model.n,
        "kernel": {"source_type": source_config.get("kernel", {}).get("type"), "source_bandwidth": source_config.get("kernel", {}).get("bandwidth"), "comparison_kernel": "not computed; source target data is not exported"},
        "raw_compiled_tvd": float(0.5 * np.abs(raw - compiled_vector).sum()),
        "compiled_deployed_tvd": float(0.5 * np.abs(compiled_vector - deployed_vector).sum()),
        "deployed_acceptance_mass": float(acceptance),
        "artifacts": {
            "raw": "raw.npy",
            "compiled": "compiled.npy",
            "deployed": "deployed.npy",
            **({"source_data": "source_data.npy"} if data_regeneration is not None else {}),
            "manifest": "manifest.json",
        },
        "output_files": [
            "raw.npy",
            "compiled.npy",
            "deployed.npy",
            *( ["source_data.npy"] if data_regeneration is not None else [] ),
            "manifest.json",
        ],
        "dataset_regeneration": data_regeneration,
        "faithful_retraining": {
            "status": "not_run",
            "reason": "A frozen checkpoint was replayed; source data and optimizer trajectory were not independently retrained.",
        },
        "namespace": {
            "source_key": source_key,
            "checkpoint_hash": checkpoint_hash,
            "config_hash": config_hash,
            "destination": str(destination),
        },
        "unsafe_serialization_loaded": False,
        "command": ["venv/Scripts/python.exe", "scripts/v4_tcdp/replay_sibling.py", str(manifest_path)],
    }
    (destination / "manifest.json").write_text(
        json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8"
    )
    return result


def replay_registered_manifest(
    manifest_path: Path, sibling_root: Path, output_root: Path
) -> dict[str, object]:
    """Replay the latest checkpoint for every registered source run cell."""

    manifest = load_export_manifest(manifest_path)
    checkpoints = _latest_checkpoint_per_run(_checkpoint_candidates(manifest, sibling_root.resolve()))
    if not checkpoints:
        return _write_blocked_manifest(
            manifest_path=manifest_path,
            manifest=manifest,
            sibling_root=sibling_root.resolve(),
            output_root=output_root.resolve(),
        )
    cells: list[dict[str, object]] = []
    for checkpoint in checkpoints:
        run_key = checkpoint.parent.parent.relative_to(sibling_root.resolve()).as_posix()
        cells.append(
            replay_export(
                manifest_path,
                sibling_root,
                output_root,
                checkpoint_path=checkpoint,
                run_key=run_key,
            )
        )
    return {
        "schema_version": "v4_tcdp.sibling_replay_batch.v1",
        "status": "PASS" if all(cell["status"] in {"adapted_reproduction", "reference_only"} for cell in cells) else "FAIL",
        "source_id": manifest.get("source_id"),
        "cells": cells,
        "checkpoint_cell_count": len(cells),
        "command": ["venv/Scripts/python.exe", "scripts/v4_tcdp/replay_sibling.py", str(manifest_path)],
    }


def replay_all_registered(
    sibling_root: Path, output_root: Path
) -> dict[str, object]:
    """Execute checkpoint replay or a blocked disposition for every exact row."""

    export_root = REPO_ROOT / "results" / "v4_tcdp" / "sibling"
    manifests = []
    for path in sorted(export_root.glob("*/manifest.json")):
        value = load_export_manifest(path)
        if value.get("disposition") == "exact_reproduction":
            manifests.append(path)
    reports = [replay_registered_manifest(path, sibling_root, output_root) for path in manifests]
    output_root.mkdir(parents=True, exist_ok=True)
    summary = {
        "schema_version": "v4_tcdp.sibling_replay_execution.v1",
        "status": "complete_with_blocked_rows" if any(report["status"] == "blocked" for report in reports) else "complete",
        "registered_exact_row_count": len(reports),
        "reports": reports,
        "command": ["venv/Scripts/python.exe", "scripts/v4_tcdp/replay_sibling.py", "--all-registered"],
    }
    (output_root / "sibling_replay_execution.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8"
    )
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path, nargs="?")
    parser.add_argument("--all-registered", action="store_true")
    parser.add_argument("--sibling-root", type=Path, default=Path(r"C:\Users\cuqui\iqp-mmd-barren-plateau"))
    parser.add_argument("--output-root", type=Path, default=REPO_ROOT / "results" / "v4_tcdp" / "sibling_replays")
    args = parser.parse_args()
    if args.all_registered:
        result = replay_all_registered(args.sibling_root, args.output_root)
    elif args.manifest is not None:
        result = replay_export(args.manifest, args.sibling_root, args.output_root)
    else:
        parser.error("provide a manifest or --all-registered")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
