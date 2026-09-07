"""Fail-closed n=4 photonic evaluation of a frozen ring artifact."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
import platform
from typing import Any

import numpy as np

from merlin_iqp.classical._validation import binary_matrix, finite_vector, hash_array, hash_json

from .compile import compile_iqp
from .density import ideal_iqp_distribution
from .fock import FullFockResult, direct_fock_compiled_distribution


SUPPORTED_N = 4
SUPPORTED_RUN_KIND = "smoke"


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
    manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
    config = manifest.get("config", {})
    dataset_manifest = manifest.get("dataset", {})
    model_manifest = manifest.get("model", {})
    n = int(config.get("n", -1))
    if n != SUPPORTED_N or config.get("run_kind") != SUPPORTED_RUN_KIND:
        raise ValueError(f"photonic ring adapter supports only n={SUPPORTED_N} {SUPPORTED_RUN_KIND} artifacts")
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


def evaluate_ring_artifact(artifact: LoadedRingArtifact, *, eta: float = 0.9) -> dict[str, Any]:
    """Compile and evaluate one verified ring artifact through final-only Fock output."""

    singles, pairs = _terms(artifact)
    compiled = compile_iqp(SUPPORTED_N, singles.tolist(), pairs, quantize=True)
    direct: FullFockResult = direct_fock_compiled_distribution(compiled, eta=eta, projection="final_only")
    raw_reference = ideal_iqp_distribution(SUPPORTED_N, singles.tolist(), pairs)
    compiled_reference = _compiled_reference(compiled)
    bitstrings = [format(index, f"0{SUPPORTED_N}b") for index in range(2**SUPPORTED_N)]
    decoded_vector = [float(direct.distribution.get(bitstring, 0.0)) for bitstring in bitstrings]
    direct_tvd_raw = _tvd(direct.distribution, raw_reference) if direct.status == "PASS" else None
    direct_tvd_compiled = _tvd(direct.distribution, compiled_reference) if direct.status == "PASS" else None
    comparison_status = "PASS" if direct_tvd_compiled is not None and direct_tvd_compiled <= 1e-12 else (direct.status if direct.status != "PASS" else "FAIL")
    return {
        "schema_version": "v4_tcdp.photonic_ring.v1",
        "status": comparison_status,
        "run_id": artifact.manifest["run_id"],
        "projection": "final_only",
        "ring_scope": {"n": SUPPORTED_N, "run_kind": SUPPORTED_RUN_KIND, "ring_deployment": "smoke_only"},
        "config": artifact.manifest["config"],
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
        "eta": float(eta),
        "direct": {
            "status": direct.status,
            "decoded_conditional_vector": decoded_vector,
            "decoded_bitstrings": bitstrings,
            "conditional_distribution": direct.distribution,
            "absolute_accepted_mass": direct.accepted_mass,
            "rejected_mass": direct.rejected_mass,
            "diagnostics": direct.diagnostics,
        },
        "qubit_reference": {
            "raw_final_theta": raw_reference,
            "compiled_quantized_theta": compiled_reference,
        },
        "comparison": {
            "status": comparison_status,
            "direct_vs_raw_qubit_tvd": direct_tvd_raw,
            "direct_vs_compiled_qubit_tvd": direct_tvd_compiled,
            "final_only_selected_boundary": True,
            "intermediate_shared_gate_comparison": "not selected; prior bounded evidence showed conditional divergence",
        },
        "hashes": {
            **artifact.hashes,
            "compiled_metadata": hash_json(compiled.as_metadata()),
            "decoded_conditional_vector": hash_json(decoded_vector),
            "raw_qubit_reference": hash_json(raw_reference),
            "compiled_qubit_reference": hash_json(compiled_reference),
        },
        "provenance": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "source_commit": artifact.manifest["config"]["source_commit"],
            "backend": direct.diagnostics.get("backend", "unavailable"),
            "perceval_version": direct.diagnostics.get("perceval_version", "unavailable"),
            "physical_source_boundary": "fixed-photon g2=0, source once, explicit eta",
        },
    }
