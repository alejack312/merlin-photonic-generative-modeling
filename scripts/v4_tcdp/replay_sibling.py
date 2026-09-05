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
from merlin_iqp.experiments.sibling_import import PINNED_SIBLING_COMMIT, load_export_manifest  # noqa: E402


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _vector(mapping: dict[str, float]) -> np.ndarray:
    return np.array([mapping[key] for key in sorted(mapping)], dtype=np.float64)


def replay_export(manifest_path: Path, sibling_root: Path, output_root: Path) -> dict[str, object]:
    manifest = load_export_manifest(manifest_path)
    if manifest["source_commit"] != PINNED_SIBLING_COMMIT:
        raise ValueError("export manifest is not pinned to the required sibling commit")
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
    model = IQPModel(generator, theta, provenance={"source_commit": PINNED_SIBLING_COMMIT, "source_id": manifest["source_id"]})
    raw = model.probability_vector_exact()
    compiled = compile_generators(generator, theta, quantize=False)
    compiled_vector = _vector(apply_compiled_density(compiled)[0])
    deployed = compile_generators(generator, theta, quantize=True)
    deployed_mapping, acceptance = apply_compiled_density(deployed)
    deployed_vector = _vector(deployed_mapping)
    destination = output_root / "training_smoke" / f"step_{step:04d}"
    destination.mkdir(parents=True, exist_ok=True)
    np.save(destination / "raw.npy", raw)
    np.save(destination / "compiled.npy", compiled_vector)
    np.save(destination / "deployed.npy", deployed_vector)
    source_config = manifest["config"].get("content", manifest["config"])
    result = {
        "schema_version": "v4_tcdp.sibling_replay.v1",
        "status": "adapted_reproduction",
        "reason": "frozen source checkpoint replayed through the ideal photonic construction; source SGD/data trajectory was not rerun",
        "source_id": manifest["source_id"],
        "source_commit": manifest["source_commit"],
        "checkpoint": {"path": str(checkpoint), "sha256": _sha256(checkpoint), "step": step, "source_loss": source_loss},
        "generator_hash": hashlib.sha256(np.ascontiguousarray(generator).tobytes()).hexdigest(),
        "theta_hash": hashlib.sha256(np.ascontiguousarray(theta).tobytes()).hexdigest(),
        "n": model.n,
        "kernel": {"source_type": source_config.get("kernel", {}).get("type"), "source_bandwidth": source_config.get("kernel", {}).get("bandwidth"), "comparison_kernel": "not computed; source target data is not exported"},
        "raw_compiled_tvd": float(0.5 * np.abs(raw - compiled_vector).sum()),
        "compiled_deployed_tvd": float(0.5 * np.abs(compiled_vector - deployed_vector).sum()),
        "deployed_acceptance_mass": float(acceptance),
        "artifacts": {"raw": "raw.npy", "compiled": "compiled.npy", "deployed": "deployed.npy"},
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
