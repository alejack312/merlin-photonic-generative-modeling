"""Compare registered sibling checkpoints through the local photonic construction.

This is deliberately narrower than the ring comparator.  It consumes the
already-validated source-trainer artifacts, regenerates the source dataset
from the sibling recipe, verifies the source and local checkpoints, and then
evaluates the same frozen G/theta/data through:

    sibling IQP -> local equivalent IQP -> compiled CP-map -> deployed map

The deployed arm is an analytic, model-derived fixed-photon ``g2=0`` result.
It is not a direct full-Fock or hardware result.  Source retraining is not
performed here; its independent evidence is required as an input.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib
import json
import os
import sys
import tempfile
import time
from pathlib import Path
from typing import Any

import numpy as np
import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from merlin_iqp.classical import IQPModel  # noqa: E402
from merlin_iqp.classical.objectives import hamming_mmd2  # noqa: E402
from merlin_iqp.classical._validation import (  # noqa: E402
    binary_matrix,
    finite_vector,
    hash_array,
    hash_json,
)
from merlin_iqp.deploy import apply_compiled_density, compile_generators  # noqa: E402
from merlin_iqp.experiments.comparison import (  # noqa: E402
    DistributionArm,
    MatchedComparison,
    process_rss_bytes,
    total_variation_distance,
)
from merlin_iqp.experiments.sibling_import import (  # noqa: E402
    PINNED_SIBLING_COMMIT,
    git_source_identity,
)

EXACT_TOLERANCE = 1.0e-16
PROBABILITY_TOLERANCE = 1.0e-12
TRAJECTORY_TOLERANCE = 1.0e-12
ACCEPTED_SAMPLE_BUDGET = 20_000
COMPILED_DENSITY_MAX_N = 10
DEFAULT_ETA = 0.9


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _read_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            value = json.loads(line)
            if not isinstance(value, dict):
                raise ValueError(f"expected JSON object in {path}")
            rows.append(value)
    return rows


def _resolve_path(value: str | Path, *, root: Path | None = None) -> Path:
    path = Path(value)
    if not path.is_absolute() and root is not None:
        path = root / path
    return path.expanduser().resolve()


def _resolve_local_artifact(value: str | Path, *, run_dir: Path) -> Path:
    """Resolve either an absolute path or a repo-relative source-run path."""

    path = Path(value)
    if path.is_absolute():
        return path.resolve()
    local_candidate = (run_dir / path).resolve()
    if local_candidate.exists():
        return local_candidate
    return (REPO_ROOT / path).resolve()


def _require_file(path: Path, label: str) -> Path:
    if not path.is_file():
        raise FileNotFoundError(f"{label} is missing: {path}")
    return path


def _safe_source_path(value: str | Path, *, sibling_root: Path, label: str) -> Path:
    path = _resolve_path(value, root=sibling_root)
    try:
        path.relative_to(sibling_root.resolve())
    except ValueError as error:
        raise ValueError(f"{label} escapes the sibling checkout: {path}") from error
    return _require_file(path, label)


def _slug(value: object) -> str:
    text = str(value)
    return "".join(c if c.isalnum() or c in "-_" else "_" for c in text).strip("_") or "unknown"


def _write_immutable_json(path: Path, payload: dict[str, Any]) -> None:
    encoded = json.dumps(payload, indent=2, sort_keys=True, allow_nan=False) + "\n"
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        existing = _read_json(path)
        if existing != payload:
            raise FileExistsError(f"incompatible comparison artifact already exists: {path}")
        return
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent,
            prefix=f".{path.name}.", suffix=".tmp", delete=False,
        ) as handle:
            handle.write(encoded)
            temporary = Path(handle.name)
        os.replace(temporary, path)
    finally:
        if temporary is not None and temporary.exists():
            temporary.unlink()


def _write_immutable_array(path: Path, array: np.ndarray) -> None:
    expected = hash_array(array)
    path.parent.mkdir(parents=True, exist_ok=True)
    if path.exists():
        with path.open("rb") as handle:
            existing = np.load(handle, allow_pickle=False)
        if hash_array(existing) != expected:
            raise FileExistsError(f"incompatible array artifact already exists: {path}")
        return
    try:
        with path.open("xb") as handle:
            np.save(handle, array, allow_pickle=False)
    except FileExistsError:
        with path.open("rb") as handle:
            existing = np.load(handle, allow_pickle=False)
        if hash_array(existing) != expected:
            raise FileExistsError(f"incompatible array artifact already exists: {path}")


def _load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"source config is not an object: {path}")
    return value


def _source_identity(sibling_root: Path) -> dict[str, Any]:
    identity = git_source_identity(
        sibling_root,
        include_paths=("src", "configs", "pyproject.toml", "setup.py", "README.md"),
    )
    if identity.get("observed_commit") != PINNED_SIBLING_COMMIT:
        raise ValueError(
            "sibling commit does not match the registered pin: "
            f"{identity.get('observed_commit')} != {PINNED_SIBLING_COMMIT}"
        )
    if identity.get("dirty"):
        raise ValueError("sibling checkout is dirty; refusing matched comparison")
    return identity


def _source_model_class(sibling_root: Path) -> type[Any]:
    source_src = str((sibling_root / "src").resolve())
    if source_src not in sys.path:
        sys.path.insert(0, source_src)
    module = importlib.import_module("iqp_bp.iqp.model")
    return module.IQPModel


def _source_dataset_factory(sibling_root: Path):
    source_src = str((sibling_root / "src").resolve())
    if source_src not in sys.path:
        sys.path.insert(0, source_src)
    module = importlib.import_module("iqp_bp.experiments.data_factory")
    return module.make_dataset


def _target_histogram(data: np.ndarray, n: int) -> np.ndarray:
    samples = np.asarray(data, dtype=np.uint8)
    if samples.ndim != 2 or samples.shape[1] != n or not np.all((samples == 0) | (samples == 1)):
        raise ValueError("source data must be a finite binary array with shape (samples, n)")
    powers = 1 << np.arange(n - 1, -1, -1, dtype=np.int64)
    indices = samples.astype(np.int64) @ powers
    target = np.bincount(indices, minlength=2**n).astype(np.float64)
    target /= float(len(samples))
    return target


def _vector_from_mapping(mapping: dict[str, float], n: int) -> np.ndarray:
    expected_keys = [format(index, f"0{n}b") for index in range(2**n)]
    if set(mapping) != set(expected_keys):
        raise ValueError("compiled mapping does not contain the complete explicit MSB-first codec")
    vector = np.array([mapping[key] for key in expected_keys], dtype=np.float64)
    if not np.all(np.isfinite(vector)) or np.any(vector < -PROBABILITY_TOLERANCE):
        raise ValueError("compiled mapping contains invalid probability values")
    total = float(vector.sum())
    if not np.isclose(total, 1.0, atol=PROBABILITY_TOLERANCE, rtol=0.0):
        raise ValueError(f"compiled conditional vector is not normalized: {total}")
    return np.maximum(vector, 0.0) / np.maximum(vector.sum(), 1.0)


def _validate_unquantized_compilation(
    local_vector: np.ndarray,
    unquantized_vector: np.ndarray,
) -> dict[str, float]:
    """Require unquantized compilation to match the local qubit reference."""

    local = np.asarray(local_vector, dtype=np.float64)
    compiled = np.asarray(unquantized_vector, dtype=np.float64)
    if local.shape != compiled.shape:
        raise ValueError("local and unquantized compilation vectors have different shapes")
    max_abs_error = float(np.max(np.abs(local - compiled)))
    tvd = float(total_variation_distance(local, compiled))
    if max_abs_error > PROBABILITY_TOLERANCE or tvd > PROBABILITY_TOLERANCE:
        raise ValueError(
            "unquantized compilation does not match the local IQP reference "
            f"(max_abs_error={max_abs_error}, tvd={tvd}, tolerance={PROBABILITY_TOLERANCE})"
        )
    return {"max_abs_error": max_abs_error, "tvd": tvd, "tolerance": PROBABILITY_TOLERANCE}


def _acceptance_for_arm(value: float) -> float:
    """Convert harmless trace roundoff to a valid probability without hiding it."""

    if not np.isfinite(value) or value <= 0:
        raise ValueError(f"model success must be positive and finite: {value}")
    if value > 1.0:
        if value - 1.0 > PROBABILITY_TOLERANCE:
            raise ValueError(f"model success exceeds one beyond tolerance: {value}")
        return 1.0
    return float(value)


def _checkpoint_path(run_dir: Path, trajectory: list[dict[str, Any]]) -> Path:
    if not trajectory:
        raise ValueError(f"empty local trajectory: {run_dir}")
    row = trajectory[-1]
    value = row.get("checkpoint_path")
    if not isinstance(value, str):
        raise ValueError("final local trajectory row has no checkpoint_path")
    path = _resolve_local_artifact(value, run_dir=run_dir)
    return _require_file(path, "local final checkpoint")


def _source_checkpoint_path(sibling_root: Path, trajectory: list[dict[str, Any]]) -> Path:
    if not trajectory:
        raise ValueError("empty source trajectory")
    value = trajectory[-1].get("checkpoint_path")
    if not isinstance(value, str):
        raise ValueError("final source trajectory row has no checkpoint_path")
    return _safe_source_path(value, sibling_root=sibling_root, label="source final checkpoint")


def _cell_key(cell: dict[str, Any]) -> tuple[Any, ...]:
    return (
        cell.get("family"),
        int(cell.get("n", -1)),
        cell.get("kernel"),
        cell.get("init"),
        cell.get("dataset_type"),
        None if cell.get("bandwidth") is None else float(cell["bandwidth"]),
    )


def _evidence_records(evidence: dict[str, Any]) -> list[dict[str, Any]]:
    cells = evidence.get("cells")
    if isinstance(cells, list):
        return [dict(cell) for cell in cells if isinstance(cell, dict)]
    return [evidence]


def _load_registered_cells(retraining_root: Path) -> list[dict[str, Any]]:
    evidence = _read_json(retraining_root / "retraining_evidence.json")
    if evidence.get("status") != "PASS":
        raise ValueError(f"retraining evidence is not PASS: {retraining_root}")
    source_config = _require_file(_resolve_path(evidence["source_config"]), "source config")
    if _sha256(source_config) != evidence.get("source_config_sha256"):
        raise ValueError("source config hash does not match retraining evidence")
    summaries = _read_jsonl(retraining_root / "results.jsonl")
    records = _evidence_records(evidence)
    by_key = {_cell_key(record.get("source_cell", record)): record for record in records}
    result: list[dict[str, Any]] = []
    for summary in summaries:
        cell = {
            "family": summary.get("family"),
            "n": summary.get("n"),
            "kernel": summary.get("kernel"),
            "init": summary.get("init"),
            "dataset_type": summary.get("dataset_type"),
            "bandwidth": summary.get("bandwidth"),
        }
        record = by_key.get(_cell_key(cell))
        if record is None and len(records) == 1:
            record = records[0]
        if record is None:
            raise ValueError(f"no retraining evidence cell matches {cell!r}")
        run_dir = _resolve_path(summary["run_dir"], root=REPO_ROOT)
        trajectory = _read_jsonl(_require_file(run_dir / "trajectory.jsonl", "local trajectory"))
        source_trajectory_path = _resolve_path(record["source_trajectory"])
        source_trajectory = _read_jsonl(_require_file(source_trajectory_path, "source trajectory"))
        if tuple(row.get("step") for row in trajectory) != tuple(row.get("step") for row in source_trajectory):
            raise ValueError(f"source/local trajectory steps differ for {cell!r}")
        if float(record.get("max_theta_abs_error", 0.0)) > TRAJECTORY_TOLERANCE:
            raise ValueError(f"source/local theta trajectory exceeds tolerance for {cell!r}")
        if float(record.get("max_loss_abs_error", 0.0)) > TRAJECTORY_TOLERANCE:
            raise ValueError(f"source/local loss trajectory exceeds tolerance for {cell!r}")
        result.append(
            {
                "summary": summary,
                "evidence": evidence,
                "cell_evidence": record,
                "source_config": source_config,
                "run_dir": run_dir,
                "trajectory": trajectory,
                "source_trajectory": source_trajectory,
            }
        )
    return result


def _build_cell(record: dict[str, Any], *, sibling_root: Path, eta: float) -> tuple[dict[str, Any], dict[str, np.ndarray]]:
    summary = record["summary"]
    evidence = record["evidence"]
    cell_evidence = record["cell_evidence"]
    run_dir = record["run_dir"]
    source_config = _load_yaml(record["source_config"])
    n = int(summary["n"])
    bandwidth = float(summary["bandwidth"])
    dataset_metadata = cell_evidence.get("source_dataset_metadata") or summary.get("dataset_metadata")
    if not isinstance(dataset_metadata, dict) or not isinstance(dataset_metadata.get("seed"), int):
        raise ValueError("registered cell is missing an integer dataset seed")
    make_dataset = _source_dataset_factory(sibling_root)
    data, regenerated_metadata = make_dataset(source_config["dataset"], n=n, seed=int(dataset_metadata["seed"]))
    data = np.asarray(data, dtype=np.uint8)
    if regenerated_metadata != dataset_metadata:
        raise ValueError(f"source dataset metadata changed during regeneration: {dataset_metadata!r}")
    target = _target_histogram(data, n)

    local_checkpoint = _checkpoint_path(run_dir, record["trajectory"])
    source_checkpoint = _source_checkpoint_path(sibling_root, record["source_trajectory"])
    with np.load(local_checkpoint, allow_pickle=False) as local_payload:
        local_g = binary_matrix(local_payload["G"], name="local generator", width=n)
        local_theta = finite_vector(local_payload["theta"], name="local theta", length=len(local_g))
        local_step = int(np.asarray(local_payload["step"]).item())
        local_loss = float(np.asarray(local_payload["loss"]).item())
    with np.load(source_checkpoint, allow_pickle=False) as source_payload:
        source_g = binary_matrix(source_payload["G"], name="source generator", width=n)
        source_theta = finite_vector(source_payload["theta"], name="source theta", length=len(source_g))
        source_step = int(np.asarray(source_payload["step"]).item())
        source_loss = float(np.asarray(source_payload["loss"]).item())
    if not np.array_equal(local_g, source_g):
        raise ValueError("source and local checkpoint generators differ")
    theta_error = float(np.max(np.abs(local_theta - source_theta)))
    if theta_error > TRAJECTORY_TOLERANCE:
        raise ValueError(f"source and local final theta differ by {theta_error}")
    if local_step != source_step:
        raise ValueError("source and local final checkpoint steps differ")
    if not np.isfinite(source_loss) or not np.isfinite(local_loss):
        raise ValueError("source/local final losses must be finite")

    source_model_class = _source_model_class(sibling_root)
    source_model = source_model_class(source_g, source_theta)
    source_vector = np.asarray(source_model.probability_vector_exact(), dtype=np.float64)
    local_model = IQPModel(local_g, local_theta, provenance={"source": "registered_sibling_checkpoint"})
    local_vector = local_model.probability_vector_exact()
    source_local_max_abs = float(np.max(np.abs(source_vector - local_vector)))
    if source_local_max_abs > PROBABILITY_TOLERANCE:
        raise ValueError(f"source/local IQP probability mismatch {source_local_max_abs} > {PROBABILITY_TOLERANCE}")

    started = time.perf_counter()
    rss_before = process_rss_bytes()
    unquantized = compile_generators(local_g, local_theta, quantize=False)
    unquantized_mapping, unquantized_success = apply_compiled_density(unquantized)
    compiled = compile_generators(local_g, local_theta, quantize=True)
    compiled_mapping, compiled_success = apply_compiled_density(compiled)
    deployed_mapping, deployed_success = apply_compiled_density(compiled, eta=eta)
    rss_after = process_rss_bytes()
    unquantized_vector = _vector_from_mapping(unquantized_mapping, n)
    compiled_vector = _vector_from_mapping(compiled_mapping, n)
    deployed_vector = _vector_from_mapping(deployed_mapping, n)
    unquantized_equality = _validate_unquantized_compilation(local_vector, unquantized_vector)
    expected_deployed_success = compiled_success * eta**n
    if abs(deployed_success - expected_deployed_success) > EXACT_TOLERANCE:
        raise AssertionError("fixed-photon acceptance is not eta**n times compiled success")
    conditional_loss_tvd = total_variation_distance(compiled_vector, deployed_vector)
    if conditional_loss_tvd > PROBABILITY_TOLERANCE:
        raise AssertionError("uniform fixed-photon loss changed the conditional output vector")

    source_loss_error = float(abs(float(hamming_mmd2(local_vector, target, sigma=bandwidth)) - source_loss))
    # Keep the source objective check local and explicit so source kernel semantics
    # cannot be hidden behind a report-only comparison.
    if source_loss_error > TRAJECTORY_TOLERANCE:
        raise ValueError(f"source/local target-loss mismatch {source_loss_error}")

    comparison = MatchedComparison(
        cell_id=f"sibling/{_slug(Path(record['source_config']).stem)}/{_slug(summary.get('family'))}/n{n}/sigma{_slug(bandwidth)}/matched_backends",
        target=target,
        arms=(
            DistributionArm("sibling-iqp", source_vector, "raw", samples=ACCEPTED_SAMPLE_BUDGET, provenance={"source": "pinned_sibling_iqp_bp"}),
            DistributionArm("local-equivalent-iqp", local_vector, "raw", samples=ACCEPTED_SAMPLE_BUDGET, provenance={"source": "merlin_iqp", "role": "equivalent_qubit_reference"}),
            DistributionArm("ideal-unquantized-control", unquantized_vector, "compiled", acceptance_mass=_acceptance_for_arm(unquantized_success), samples=ACCEPTED_SAMPLE_BUDGET, provenance={"quantized": False, "role": "compilation_control", "construction": "absolute-probability-CP-map", "raw_model_success": float(unquantized_success)}),
            DistributionArm("ideal-compiled-map", compiled_vector, "compiled", acceptance_mass=_acceptance_for_arm(compiled_success), samples=ACCEPTED_SAMPLE_BUDGET, provenance={"quantized": True, "role": "primary_compiled_reference", "construction": "absolute-probability-CP-map", "raw_model_success": float(compiled_success)}),
            DistributionArm("ideal-deployed-map", deployed_vector, "deployed", acceptance_mass=_acceptance_for_arm(deployed_success), samples=ACCEPTED_SAMPLE_BUDGET, provenance={"quantized": True, "role": "same-effective-parameters-as-compiled", "construction": "absolute-probability-CP-map", "physical_status": "model_derived_reference_only", "source_model": "fixed_photon_g2_0", "eta": eta, "loss": "uniform_all_photons", "projection": "final_only", "raw_model_success": float(deployed_success)}),
        ),
        hamming_sigma=bandwidth,
        controls={
            "status": "PASS",
            "scope": "cell-level source/substrate controls",
            "source_local_probability_equality": {"max_abs_error": source_local_max_abs, "tolerance": PROBABILITY_TOLERANCE},
            "local_unquantized_probability_equality": unquantized_equality,
            "fixed_photon_loss_shape": {"conditional_tvd": float(conditional_loss_tvd), "tolerance": PROBABILITY_TOLERANCE},
            "acceptance_scaling": {"formula": "eta**n * compiled_model_success", "absolute_error": float(abs(deployed_success - expected_deployed_success)), "tolerance": EXACT_TOLERANCE},
            "metric_mutation_panel": "covered by the registered comparison control suite; not recomputed per sibling cell",
        },
        common_manifest={
            "comparison_kind": "sibling_to_equivalent_to_compiled_photonic",
            "dataset_hash": hash_array(data),
            "target_hash": hash_array(target),
            "generator_hash": hash_array(local_g),
            "theta_hash": hash_array(local_theta),
            "split": "source empirical samples; no train/test reinterpretation",
            "bit_order": "msb_first",
            "hamming_kernel": {"kind": "gaussian_on_hamming", "sigma": bandwidth, "formula": "exp(-H/(2*sigma**2))"},
            "evaluation_budget": {"accepted_samples": ACCEPTED_SAMPLE_BUDGET, "population_vectors": True},
            "source_retraining": "verified separately by retraining_evidence.json",
            "source_model": "fixed_photon_g2_0",
            "loss": {"eta": eta, "acceptance_rule": "eta**n * model_success", "conditional_shape_expected_invariant": True},
            "photonic_capability": {"compiled_density_max_n": COMPILED_DENSITY_MAX_N, "physical_full_fock_n": [2, 3], "status": "analytic_CP_map_model_derived_for_this_cell"},
        },
        resource_report={
            "status": "measured" if rss_before is not None and rss_after is not None else "rss_unavailable",
            "rss_before_bytes": rss_before,
            "rss_after_bytes": rss_after,
            "rss_delta_bytes": None if rss_before is None or rss_after is None else rss_after - rss_before,
            "elapsed_seconds": float(time.perf_counter() - started),
            "memory_policy": "current-process RSS; no embedded 4^n-square superoperator",
        },
    )
    comparison_payload = comparison.manifest()
    comparison_payload["source_checks"] = {
        "source_local_generator_equal": True,
        "source_local_theta_max_abs_error": theta_error,
        "source_local_probability_max_abs_error": source_local_max_abs,
        "local_unquantized_probability_max_abs_error": unquantized_equality["max_abs_error"],
        "local_unquantized_tvd": unquantized_equality["tvd"],
        "source_final_loss": source_loss,
        "local_final_loss": local_loss,
        "local_loss_recomputed_from_target": float(hamming_mmd2(local_vector, target, sigma=bandwidth)),
        "loss_recomputed_abs_error": source_loss_error,
        "status": "PASS",
        "tolerances": {"exact": EXACT_TOLERANCE, "probability": PROBABILITY_TOLERANCE, "trajectory": TRAJECTORY_TOLERANCE},
    }
    comparison_payload["acceptance_checks"] = {
        "unquantized_model_success": float(unquantized_success),
        "compiled_model_success": float(compiled_success),
        "deployed_absolute_success": float(deployed_success),
        "expected_deployed_absolute_success": float(expected_deployed_success),
        "deployed_success_abs_error": float(abs(deployed_success - expected_deployed_success)),
        "compiled_deployed_conditional_tvd": float(conditional_loss_tvd),
        "attempts_per_accepted_sample": float(1.0 / deployed_success),
        "status": "PASS",
    }
    artifact_payload = {
        "comparison": comparison_payload,
        "provenance": {
            "source_commit": evidence.get("source_identity_after", {}).get("observed_commit"),
            "source_tree_identity": evidence.get("source_identity_after", {}).get("tree_identity"),
            "source_config": str(record["source_config"]),
            "source_config_sha256": _sha256(record["source_config"]),
            "source_retraining_evidence_sha256": _sha256(run_dir.parent.parent / "retraining_evidence.json") if (run_dir.parent.parent / "retraining_evidence.json").is_file() else None,
            "source_trajectory": str(_resolve_path(record["cell_evidence"]["source_trajectory"])),
            "source_trajectory_sha256": _sha256(_resolve_path(record["cell_evidence"]["source_trajectory"])),
            "source_checkpoint_sha256": _sha256(source_checkpoint),
            "local_checkpoint_sha256": _sha256(local_checkpoint),
            "input_hashes": {"data": hash_array(data), "target": hash_array(target), "generator": hash_array(local_g), "theta": hash_array(local_theta)},
            "local_head": _git_head(REPO_ROOT),
        },
        "outputs": {
            "status": "PASS",
            "raw_compiled_tvd": float(total_variation_distance(local_vector, compiled_vector)),
            "compiled_deployed_tvd": float(total_variation_distance(compiled_vector, deployed_vector)),
            "source_local_tvd": float(total_variation_distance(source_vector, local_vector)),
        },
    }
    arrays = {"data": data, "target": target, "sibling_iqp": source_vector, "local_iqp": local_vector, "unquantized": unquantized_vector, "compiled": compiled_vector, "deployed": deployed_vector}
    return artifact_payload, arrays


def _git_head(root: Path) -> str | None:
    import subprocess

    try:
        result = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], check=True, capture_output=True, text=True)
    except (OSError, subprocess.CalledProcessError):
        return None
    return result.stdout.strip()


def run_comparisons(retraining_roots: list[Path], *, sibling_root: Path, output_root: Path, eta: float) -> dict[str, Any]:
    if not np.isfinite(eta) or not 0 < eta <= 1:
        raise ValueError("eta must be finite and in (0, 1]")
    identity = _source_identity(sibling_root)
    all_records: list[dict[str, Any]] = []
    for root in retraining_roots:
        all_records.extend(_load_registered_cells(root))
    if not all_records:
        raise ValueError("no registered retraining cells were supplied")
    summary: dict[str, Any] = {"schema_version": "v4_tcdp.sibling_matched_comparisons.v1", "status": "PASS", "eta": eta, "source_identity": identity, "cells": []}
    for record in all_records:
        payload, arrays = _build_cell(record, sibling_root=sibling_root, eta=eta)
        cell_id = payload["comparison"]["cell_id"]
        destination = output_root / f"{_slug(cell_id)}__eta{str(eta).replace('.', 'p')}"
        destination.mkdir(parents=True, exist_ok=True)
        for name, array in arrays.items():
            _write_immutable_array(destination / f"{name}.npy", np.asarray(array))
        comparison_path = destination / "comparison.json"
        manifest_path = destination / "manifest.json"
        _write_immutable_json(comparison_path, payload["comparison"])
        artifact = {**payload, "artifacts": {name: f"{name}.npy" for name in arrays} | {"comparison": "comparison.json", "manifest": "manifest.json"}}
        artifact["artifact_hashes"] = {name: hash_array(array) for name, array in arrays.items()}
        artifact["artifact_hashes"].update({"comparison": _sha256(comparison_path)})
        _write_immutable_json(manifest_path, artifact)
        summary["cells"].append({"cell_id": cell_id, "directory": str(destination), "manifest": str(manifest_path), "status": "PASS"})
    summary_path = output_root / "summary.json"
    _write_immutable_json(summary_path, summary)
    return summary


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sibling-root", type=Path, default=Path(r"C:\Users\cuqui\iqp-mmd-barren-plateau"))
    parser.add_argument("--output-root", type=Path, default=Path("results/v4_tcdp/sibling_comparisons/closure_20260908"))
    parser.add_argument("--eta", type=float, default=DEFAULT_ETA)
    parser.add_argument("--retraining-root", type=Path, action="append", required=True, help="registered local retraining output root; repeat for each profile")
    args = parser.parse_args()
    roots = [_resolve_path(value, root=REPO_ROOT) for value in args.retraining_root]
    result = run_comparisons(roots, sibling_root=_resolve_path(args.sibling_root), output_root=_resolve_path(args.output_root, root=REPO_ROOT), eta=args.eta)
    print(json.dumps({"status": result["status"], "cells": len(result["cells"]), "summary": str(_resolve_path(args.output_root, root=REPO_ROOT) / "summary.json")}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
