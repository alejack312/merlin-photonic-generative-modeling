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

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from merlin_iqp.classical import IQPModel  # noqa: E402
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


def replay_export(manifest_path: Path, sibling_root: Path, output_root: Path) -> dict[str, object]:
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
    candidates = [sibling_root / Path(item) for item in manifest.get("result_evidence", []) if str(item).endswith(".npz")]
    checkpoints = [path for path in candidates if path.exists() and path.name.startswith("step_")]
    if not checkpoints:
        raise FileNotFoundError("export manifest contains no available safe NPZ checkpoint")
    checkpoint = sorted(checkpoints)[-1]
    with np.load(checkpoint, allow_pickle=False) as payload:
        required = {"G", "theta", "step", "loss"}
        if not required.issubset(payload.files):
            raise ValueError(f"checkpoint is missing required fields: {sorted(required - set(payload.files))}")
        generator = np.asarray(payload["G"], dtype=np.uint8)
        theta = np.asarray(payload["theta"], dtype=np.float64)
        step = int(payload["step"])
        source_loss = float(payload["loss"])
    source_config = manifest["config"].get("content", manifest["config"])
    checkpoint_hash = _sha256(checkpoint)
    config_hash = _config_hash(source_config)
    source_key = f"{_slug(manifest['source_id'])}__{_slug(source_identity.get('observed_commit'))[:16]}__{_slug(source_identity.get('tree_identity'))[:16]}"
    destination = output_root / source_key / f"checkpoint_{checkpoint_hash[:16]}" / f"config_{config_hash[:16]}" / f"step_{step:04d}"
    if destination.exists() and any(destination.iterdir()):
        raise FileExistsError(f"replay destination already contains an artifact: {destination}")
    model = IQPModel(generator, theta, provenance={"source_commit": source_identity.get("observed_commit"), "source_id": manifest["source_id"]})
    raw = model.probability_vector_exact()
    compiled = compile_generators(generator, theta, quantize=True)
    compiled_vector = _vector(apply_compiled_density(compiled)[0])
    deployed = compiled
    deployed_mapping, acceptance = apply_compiled_density(deployed)
    deployed_vector = _vector(deployed_mapping)
    destination.mkdir(parents=True, exist_ok=True)
    np.save(destination / "raw.npy", raw)
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
        },
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
    }
    (destination / "manifest.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--sibling-root", type=Path, default=Path(r"C:\Users\cuqui\iqp-mmd-barren-plateau"))
    parser.add_argument("--output-root", type=Path, default=REPO_ROOT / "results" / "v4_tcdp" / "sibling_replays")
    args = parser.parse_args()
    result = replay_export(args.manifest, args.sibling_root, args.output_root)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
