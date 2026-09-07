"""Fail-closed n=4 photonic evaluation of a frozen ring artifact."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import tempfile
from typing import Any

import numpy as np

from merlin_iqp.classical._validation import binary_matrix, finite_vector, hash_array, hash_json
from merlin_iqp.classical.objectives import hamming_mmd2, spatial_mmd2

from .compile import compile_iqp
from .density import ideal_iqp_distribution
from .fock import FullFockResult, direct_fock_compiled_distribution
from merlin_iqp.experiments.rings import PROFILE_REGISTRY
from merlin_iqp.experiments.sibling_import import git_source_identity


SUPPORTED_N = 4
SUPPORTED_RUN_KIND = "smoke"
SUPPORTED_VALIDATION_SCHEMA = "v4_tcdp.physical_controls.v2"
SUPPORTED_PROJECTION = "final_only"
MATERIAL_PROJECTION_TVD = 1e-3
DEFAULT_VALIDATION_MANIFEST = Path("results/v4_tcdp/deploy/physical_control_manifest.json")


def _file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _tvd(left: dict[str, float], right: dict[str, float]) -> float:
    keys = set(left) | set(right)
    return float(0.5 * sum(abs(left.get(key, 0.0) - right.get(key, 0.0)) for key in keys))


def _require_hash(actual: str, expected: str, name: str) -> None:
    if not expected or actual != expected:
        raise ValueError(f"{name} hash does not match manifest")


def _load_json(path: Path) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"unable to load JSON artifact {path}") from error
    if not isinstance(payload, dict):
        raise ValueError(f"JSON artifact must contain an object: {path}")
    return payload


def _validate_physical_manifest(path: Path) -> tuple[dict[str, Any], float]:
    if not path.is_file():
        raise FileNotFoundError(f"required physical validation manifest is missing: {path}")
    manifest = _load_json(path)
    if manifest.get("schema_version") != SUPPORTED_VALIDATION_SCHEMA:
        raise ValueError("physical validation manifest has an unsupported schema")
    declared_hash = manifest.get("payload_sha256")
    payload = dict(manifest)
    payload.pop("payload_sha256", None)
    if not isinstance(declared_hash, str) or hash_json(payload) != declared_hash:
        raise ValueError("physical validation manifest payload hash does not match")
    if manifest.get("status") != "PASS":
        raise ValueError("physical validation is not PASS; ring deployment is blocked")
    if manifest.get("source_model") != "fixed_photon_g2_0":
        raise ValueError("physical validation uses an unsupported source model")
    controls = manifest.get("controls")
    if not isinstance(controls, list):
        raise ValueError("physical validation manifest is missing controls")
    by_id = {control.get("id"): control for control in controls if isinstance(control, dict)}
    required = ("no_gate_n2", "single_gate_bystander_n3", "shared_gate_n3")
    if set(by_id) != set(required):
        raise ValueError("physical validation manifest does not cover the required direct controls")
    for control_id in required:
        control = by_id[control_id]
        final = control.get(SUPPORTED_PROJECTION)
        direct_tvd = control.get("conditional_tvd_direct_final_vs_analytic")
        diagnostics = final.get("diagnostics") if isinstance(final, dict) else None
        if control.get("status") != "PASS" or not isinstance(final, dict) or final.get("status") != "PASS":
            raise ValueError(f"physical control {control_id} is not a passing final-only control")
        if not isinstance(diagnostics, dict) or diagnostics.get("projection") != SUPPORTED_PROJECTION:
            raise ValueError(f"physical control {control_id} does not validate final_only")
        if not isinstance(direct_tvd, (int, float)) or not math.isfinite(float(direct_tvd)) or float(direct_tvd) > 1e-12:
            raise ValueError(f"physical control {control_id} does not match its analytic reference")
    comparison = by_id["shared_gate_n3"].get("projection_comparison")
    discrepancy = comparison.get("conditional_tvd_final_vs_intermediate") if isinstance(comparison, dict) else None
    if not isinstance(comparison, dict) or comparison.get("valid") is not True:
        raise ValueError("shared-gate projection comparison is missing or invalid")
    if not isinstance(discrepancy, (int, float)) or not math.isfinite(float(discrepancy)) or float(discrepancy) <= MATERIAL_PROJECTION_TVD:
        raise ValueError("shared-gate final-only/intermediate discrepancy is missing or not material")
    return manifest, float(discrepancy)


def _dataset_hash(dataset: dict[str, np.ndarray], manifest: dict[str, Any], n: int) -> str:
    codec = manifest["codec"]
    return hash_json(
        {
            "dataset_id": manifest["dataset_id"],
            "n": n,
            "raw_train": hash_array(dataset["raw_train"]),
            "raw_test": hash_array(dataset["raw_test"]),
            "normalized_train": hash_array(dataset["normalized_train"]),
            "normalized_test": hash_array(dataset["normalized_test"]),
            "train_ids": hash_array(dataset["train_ids"]),
            "test_ids": hash_array(dataset["test_ids"]),
            "transform": {
                "min": np.asarray(dataset["min_values"]).reshape(1, -1).tolist(),
                "max": np.asarray(dataset["max_values"]).reshape(1, -1).tolist(),
                "scale": np.asarray(dataset["scale"]).reshape(1, -1).tolist(),
            },
            "codec": {
                "centers": hash_array(dataset["centers"]),
                "n": n,
                "lo": codec["lo"],
                "hi": codec["hi"],
            },
            "train_histogram": hash_array(dataset["train_histogram"]),
            "test_histogram": hash_array(dataset["test_histogram"]),
        }
    )


@dataclass(frozen=True)
class LoadedRingArtifact:
    root: Path
    manifest: dict[str, Any]
    run: dict[str, np.ndarray]
    dataset: dict[str, np.ndarray]
    hashes: dict[str, str]


def load_ring_artifact(root: str | Path) -> LoadedRingArtifact:
    """Load and verify one frozen n=4 smoke ring artifact."""

    root = Path(root).resolve()
    paths = {
        "manifest": root / "manifest.json",
        "run": root / "run.npz",
        "dataset": root / "dataset.npz",
    }
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise FileNotFoundError(f"ring artifact is incomplete: {', '.join(missing)}")
    manifest = _load_json(paths["manifest"])
    config = manifest.get("config", {})
    dataset_manifest = manifest.get("dataset", {})
    model_manifest = manifest.get("model", {})
    n = int(config.get("n", -1))
    if n != SUPPORTED_N or config.get("run_kind") != SUPPORTED_RUN_KIND:
        raise ValueError(f"photonic ring adapter supports only n={SUPPORTED_N} {SUPPORTED_RUN_KIND} artifacts")
    if config.get("profile_id") not in PROFILE_REGISTRY:
        raise ValueError("ring manifest has an unknown profile")
    if config.get("generator_family") != "chain_1d":
        raise ValueError("photonic ring adapter requires the chain_1d generator family")
    run_id = str(manifest.get("run_id", ""))
    expected_run_id = f"{config.get('profile_id')}/n{n}_seed{config.get('seed')}_{config.get('run_kind')}"
    if run_id != expected_run_id:
        raise ValueError("ring manifest run_id does not match its config")
    source_commit = config.get("source_commit")
    if not isinstance(source_commit, str) or not source_commit:
        raise ValueError("ring manifest is missing its source commit")
    source_provenance = manifest.get("source_provenance")
    if isinstance(source_provenance, dict) and source_provenance.get("observed_commit") not in {None, source_commit}:
        raise ValueError("ring source provenance commit does not match config source_commit")
    if int(dataset_manifest.get("n", -1)) != n or int(dataset_manifest.get("codec", {}).get("n", -1)) != n:
        raise ValueError("ring manifest dimensions do not match")
    codec = dataset_manifest.get("codec", {})
    if codec.get("bit_order") != "msb_first" or codec.get("index_order") != "row_major":
        raise ValueError("unsupported ring codec convention")
    with np.load(paths["run"], allow_pickle=False) as archive:
        run = {key: np.asarray(archive[key]) for key in archive.files}
    with np.load(paths["dataset"], allow_pickle=False) as archive:
        dataset = {key: np.asarray(archive[key]) for key in archive.files}
    required_run = {"generator", "initial_theta", "final_theta", "output_probabilities", "decoded_centers"}
    required_dataset = {
        "raw_train", "raw_test", "normalized_train", "normalized_test", "train_ids", "test_ids",
        "min_values", "max_values", "scale", "centers", "train_histogram", "test_histogram",
    }
    if not required_run.issubset(run) or not required_dataset.issubset(dataset):
        raise ValueError("ring artifact is missing required arrays")
    _require_hash(hash_array(run["generator"]), model_manifest.get("generator_hash", ""), "generator")
    _require_hash(hash_array(run["initial_theta"]), model_manifest.get("initial_theta_hash", ""), "initial theta")
    _require_hash(hash_array(run["final_theta"]), model_manifest.get("final_theta_hash", ""), "final theta")
    _require_hash(hash_array(run["output_probabilities"]), model_manifest.get("output_probability_hash", ""), "output probabilities")
    _require_hash(hash_array(dataset["centers"]), codec.get("centers_hash", ""), "centers")
    for name in ("raw_train", "raw_test", "normalized_train", "normalized_test", "train_ids", "test_ids"):
        _require_hash(hash_array(dataset[name]), dataset_manifest.get(f"{name}_hash", ""), name)
    _require_hash(hash_array(dataset["train_histogram"]), dataset_manifest.get("histograms", {}).get("train_hash", ""), "train histogram")
    _require_hash(hash_array(dataset["test_histogram"]), dataset_manifest.get("histograms", {}).get("test_hash", ""), "test histogram")
    _require_hash(_dataset_hash(dataset, dataset_manifest, n), dataset_manifest.get("dataset_hash", ""), "dataset")
    if not np.array_equal(run["decoded_centers"], dataset["centers"]):
        raise ValueError("decoded centers do not match the ring codec centers")
    generator = binary_matrix(run["generator"], name="generator", width=n)
    theta = finite_vector(run["final_theta"], name="final_theta", length=len(generator))
    if any(int(row.sum()) not in (1, 2) for row in generator):
        raise ValueError("photonic ring adapter supports only weight-1/2 generators")
    if manifest.get("selection_rule") != "fixed_last_step":
        raise ValueError("ring artifact does not select final theta with fixed_last_step")
    hashes = {name: _file_hash(path) for name, path in paths.items()}
    hashes.update({"generator": hash_array(generator), "final_theta": hash_array(theta), "dataset": dataset_manifest["dataset_hash"]})
    return LoadedRingArtifact(root, manifest, run, dataset, hashes)


def _terms(artifact: LoadedRingArtifact) -> tuple[np.ndarray, list[tuple[int, int, float]]]:
    generator = binary_matrix(artifact.run["generator"], name="generator", width=SUPPORTED_N)
    theta = finite_vector(artifact.run["final_theta"], name="final_theta", length=len(generator))
    singles = np.zeros(SUPPORTED_N, dtype=float)
    pairs: list[tuple[int, int, float]] = []
    for row, value in zip(generator, theta, strict=True):
        support = tuple(int(index) for index in np.flatnonzero(row))
        if len(support) == 1:
            singles[support[0]] += float(value)
        else:
            pairs.append((support[0], support[1], float(value)))
    return singles, pairs


def _compiled_reference(compiled: Any) -> dict[str, float]:
    pairs = [(pair[0], pair[1], angle.lifted_theta) for pair, angle in compiled.pair_angles]
    return ideal_iqp_distribution(compiled.n, compiled.singles, pairs)


def evaluate_ring_artifact(
    artifact: LoadedRingArtifact | str | Path,
    *,
    eta: float = 0.9,
    validation_manifest_path: str | Path = DEFAULT_VALIDATION_MANIFEST,
) -> dict[str, Any]:
    """Evaluate one verified ring artifact through the supported final-only boundary."""

    eta_value = float(eta)
    if not math.isfinite(eta_value) or not 0.0 < eta_value <= 1.0:
        raise ValueError("eta must be finite and in (0,1]")
    if not isinstance(artifact, LoadedRingArtifact):
        artifact = load_ring_artifact(artifact)
    validation_path = Path(validation_manifest_path).resolve()
    validation_manifest, projection_discrepancy = _validate_physical_manifest(validation_path)

    singles, pairs = _terms(artifact)
    compiled = compile_iqp(SUPPORTED_N, singles.tolist(), pairs, topology="path", quantize=True)
    direct: FullFockResult = direct_fock_compiled_distribution(compiled, eta=eta_value, projection=SUPPORTED_PROJECTION)
    if direct.status != "PASS":
        raise RuntimeError(f"direct final-only ring evaluation did not PASS: {direct.diagnostics.get('reason', direct.status)}")
    if direct.diagnostics.get("projection") != SUPPORTED_PROJECTION:
        raise ValueError("direct ring evaluator returned an unexpected projection")
    if direct.accepted_mass is None or not math.isfinite(float(direct.accepted_mass)) or not 0.0 <= float(direct.accepted_mass) <= 1.0:
        raise ValueError("direct ring evaluator returned an invalid absolute acceptance")

    raw_reference = _compiled_reference(compile_iqp(SUPPORTED_N, singles.tolist(), pairs, topology="path", quantize=False))
    compiled_reference = _compiled_reference(compiled)
    bitstrings = [format(index, f"0{SUPPORTED_N}b") for index in range(2**SUPPORTED_N)]
    unknown_keys = set(direct.distribution) - set(bitstrings)
    if unknown_keys:
        raise ValueError(f"direct ring evaluator returned undecodable bitstrings: {sorted(unknown_keys)}")
    decoded_vector = np.asarray([float(direct.distribution.get(bitstring, 0.0)) for bitstring in bitstrings], dtype=np.float64)
    if not np.all(np.isfinite(decoded_vector)) or np.any(decoded_vector < 0.0) or not np.isclose(decoded_vector.sum(), 1.0, atol=1e-10, rtol=1e-10):
        raise ValueError("direct ring evaluator returned an invalid conditional distribution")
    decoded_vector /= decoded_vector.sum()
    raw_vector = np.asarray([raw_reference.get(bitstring, 0.0) for bitstring in bitstrings], dtype=np.float64)
    compiled_vector = np.asarray([compiled_reference.get(bitstring, 0.0) for bitstring in bitstrings], dtype=np.float64)
    direct_tvd_raw = _tvd(dict(zip(bitstrings, decoded_vector, strict=True)), raw_reference)
    direct_tvd_compiled = _tvd(dict(zip(bitstrings, decoded_vector, strict=True)), compiled_reference)
    hamming_metric = hamming_mmd2(decoded_vector, compiled_vector, sigma=0.5 * math.sqrt(SUPPORTED_N))
    spatial_metric = spatial_mmd2(decoded_vector, compiled_vector, artifact.dataset["centers"], sigma=0.1)
    profile_kind = artifact.manifest["config"]["profile_kernel_kind"]
    metrics = {
        "tvd": float(direct_tvd_compiled),
        "hamming_mmd2": float(hamming_metric),
        "spatial_mmd2": float(spatial_metric),
        "profile_mmd2": float(spatial_metric if profile_kind == "spatial_gaussian" else hamming_metric),
    }
    config_hash = hash_json(artifact.manifest["config"])
    validation_hash = _file_hash(validation_path)
    result: dict[str, Any] = {
        "schema_version": "v4_tcdp.photonic_ring.v2",
        "status": "PASS" if direct_tvd_compiled <= 1e-12 else "FAIL",
        "run_id": artifact.manifest["run_id"],
        "projection": SUPPORTED_PROJECTION,
        "ring_scope": {"n": SUPPORTED_N, "run_kind": SUPPORTED_RUN_KIND, "ring_deployment": "smoke_only"},
        "config": artifact.manifest["config"],
        "config_sha256": config_hash,
        "codec": artifact.manifest["dataset"]["codec"],
        "target_and_budget": {
            "dataset_id": artifact.manifest["dataset"]["dataset_id"],
            "dataset_hash": artifact.manifest["dataset"]["dataset_hash"],
            "train_histogram_hash": artifact.manifest["dataset"]["histograms"]["train_hash"],
            "steps": artifact.manifest["config"]["steps"],
            "seed": artifact.manifest["config"]["seed"],
            "optimizer": artifact.manifest["config"]["optimizer"],
            "learning_rate": artifact.manifest["config"]["lr"],
        },
        "source_model": "fixed_photon_g2_0",
        "source_once": True,
        "eta": eta_value,
        "direct": {
            "status": direct.status,
            "decoded_conditional_vector": decoded_vector.tolist(),
            "decoded_bitstrings": bitstrings,
            "conditional_distribution": {key: float(value) for key, value in zip(bitstrings, decoded_vector, strict=True)},
            "absolute_accepted_mass": float(direct.accepted_mass),
            "rejected_mass": direct.rejected_mass,
            "diagnostics": direct.diagnostics,
        },
        "qubit_reference": {
            "bit_order": "msb_first",
            "raw_final_theta": raw_reference,
            "compiled_quantized_theta": compiled_reference,
            "raw_vector_sha256": hash_array(raw_vector),
            "compiled_vector_sha256": hash_array(compiled_vector),
        },
        "comparison": {
            "status": "PASS" if direct_tvd_compiled <= 1e-12 else "FAIL",
            "direct_vs_raw_qubit_tvd": float(direct_tvd_raw),
            "direct_vs_compiled_qubit_tvd": float(direct_tvd_compiled),
            "metrics": metrics,
            "final_only_selected_boundary": True,
            "intermediate_shared_gate_comparison": {
                "supported": False,
                "conditional_tvd_final_only_vs_intermediate": projection_discrepancy,
                "materiality_threshold": MATERIAL_PROJECTION_TVD,
                "reason": "shared-gate conditional projection differs materially; final_only is the supported boundary",
            },
        },
        "hashes": {
            **artifact.hashes,
            "compiled_metadata": hash_json(compiled.as_metadata()),
            "decoded_conditional_vector": hash_array(decoded_vector),
            "raw_qubit_reference": hash_json(raw_reference),
            "compiled_qubit_reference": hash_json(compiled_reference),
            "configuration": config_hash,
            "validation_manifest": validation_hash,
            "output_payload": None,
        },
        "provenance": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "source_commit": artifact.manifest["config"]["source_commit"],
            "backend": direct.diagnostics.get("backend", "unavailable"),
            "perceval_version": direct.diagnostics.get("perceval_version", "unavailable"),
            "physical_source_boundary": "fixed-photon g2=0, source once, explicit eta",
            "validation_manifest_status": validation_manifest["status"],
            "validation_manifest_payload_sha256": validation_manifest["payload_sha256"],
            "repo": git_source_identity(Path(__file__).resolve().parents[3], include_paths=("src/merlin_iqp/deploy", "scripts/v4_tcdp/evaluate_ring_photonic.py")),
        },
    }
    # Hash the complete payload with this field set to its sentinel value.  A
    # consumer can recompute this value without creating a self-referential
    # hash that can never validate against the serialized result.
    payload_for_hash = dict(result)
    payload_hashes = dict(result["hashes"])
    payload_hashes["output_payload"] = None
    payload_for_hash["hashes"] = payload_hashes
    result["hashes"]["output_payload"] = hash_json(payload_for_hash)
    return result


def write_ring_evaluation(result: dict[str, Any], output_path: str | Path) -> Path:
    """Write an isolated JSON result and reject incompatible reuse."""

    destination = Path(output_path).resolve()
    destination.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(result, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if destination.exists():
        existing = _load_json(destination)
        if existing != result:
            raise FileExistsError(f"incompatible ring evaluation already exists: {destination}")
        return destination
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{destination.name}.", dir=destination.parent)
    os.close(descriptor)
    temporary = Path(temporary_name)
    try:
        temporary.write_text(serialized, encoding="utf-8")
        os.rename(temporary, destination)
    except FileExistsError:
        if destination.is_file() and _load_json(destination) == result:
            return destination
        raise FileExistsError(f"incompatible ring evaluation already exists: {destination}")
    finally:
        if temporary.exists():
            temporary.unlink()
    return destination


__all__ = ["DEFAULT_VALIDATION_MANIFEST", "LoadedRingArtifact", "evaluate_ring_artifact", "load_ring_artifact", "write_ring_evaluation"]
