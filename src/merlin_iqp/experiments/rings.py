"""Classical IQP training profiles for the additive two-ring study."""

from __future__ import annotations

import builtins
import json
import os
import platform
import shutil
import tempfile
from contextlib import contextmanager
from dataclasses import asdict, dataclass, replace
from pathlib import Path
from typing import Any, Iterator

import numpy as np

from merlin_iqp.classical import IQPModel, KernelSpec, Trainer, chain_1d, initialize_theta, target_moments
from merlin_iqp.classical._validation import hash_array, hash_json
from merlin_iqp.classical.objectives import hamming_mmd2, spatial_mmd2

from .datasets import RingsDataset, load_rings_dataset
from .sibling_import import git_source_identity


SCHEMA_VERSION = "v4_tcdp.rings_run.v2"
PHOTONIC_EVALUATION = {
    "status": "INCONCLUSIVE",
    "reason": "Phase 28 owned scope has no validated ideal photonic ring deployment adapter; no unsupported simulator label is substituted.",
}
FORBIDDEN_CLASSICAL_IMPORTS = frozenset({"torch", "perceval", "perceval_quandela", "merlinquantum", "merlin"})
SOURCE_COMMIT_RULE = "explicit_commit_preserved; null_or_working_tree_resolves_to_observed"


@dataclass(frozen=True)
class RingProfile:
    profile_id: str
    kernel_kind: str
    sigma_rule: str
    registered_n: tuple[int, ...] = (4, 6, 8)
    main_steps: int = 300
    main_seeds: tuple[int, ...] = (0, 1, 2, 3, 4)


PROFILE_REGISTRY: dict[str, RingProfile] = {
    "rings_spatial_exact": RingProfile("rings_spatial_exact", "spatial_gaussian", "0.1"),
    "rings_hamming": RingProfile("rings_hamming", "hamming_gaussian", "0.5*sqrt(n)"),
}


@dataclass(frozen=True)
class RingConfig:
    profile_id: str
    n: int
    seed: int
    steps: int
    lr: float = 0.05
    optimizer: str = "adam"
    initialization: str = "data_dependent"
    initialization_method: str = "parity"
    initialization_scale: float = 0.1
    initialization_std: float = 0.1
    generator_family: str = "chain_1d"
    source_commit: str | None = None
    run_kind: str = "smoke"

    @property
    def cell_id(self) -> str:
        return f"n{self.n}_seed{self.seed}_{self.run_kind}"

    @property
    def sigma(self) -> float:
        profile = PROFILE_REGISTRY[self.profile_id]
        return 0.1 if profile.kernel_kind == "spatial_gaussian" else 0.5 * np.sqrt(self.n)


@dataclass(frozen=True)
class RingRun:
    config: RingConfig
    dataset: RingsDataset
    generator: np.ndarray
    initial_theta: np.ndarray
    final_theta: np.ndarray
    output_probabilities: np.ndarray
    loss_history: tuple[float, ...]
    metrics: dict[str, float]
    photonic_evaluation: dict[str, str]
    initialization_metadata: dict[str, Any]
    source_provenance: dict[str, Any]


def available_profiles() -> dict[str, dict[str, Any]]:
    return {
        name: {
            "kernel_kind": profile.kernel_kind,
            "sigma_rule": profile.sigma_rule,
            "default_initialization": "data_dependent",
            "default_initialization_method": "parity",
            "default_initialization_scale": 0.1,
            "initialization_ablations": ["small_angle", "uniform"],
            "registered_n": list(profile.registered_n),
            "main_steps": profile.main_steps,
            "main_seeds": list(profile.main_seeds),
            "budget_status": "registered_not_launched",
        }
        for name, profile in PROFILE_REGISTRY.items()
    }


def resolve_config(
    profile_id: str,
    *,
    n: int = 4,
    seed: int = 0,
    steps: int | None = None,
    main: bool = False,
    initialization: str | None = None,
    initialization_method: str | None = None,
    initialization_scale: float | None = None,
    initialization_std: float | None = None,
) -> RingConfig:
    if profile_id not in PROFILE_REGISTRY:
        raise ValueError(f"unknown ring profile {profile_id!r}")
    if n not in PROFILE_REGISTRY[profile_id].registered_n:
        raise ValueError(f"n={n} is not registered for {profile_id}; use one of {PROFILE_REGISTRY[profile_id].registered_n}")
    resolved_steps = PROFILE_REGISTRY[profile_id].main_steps if steps is None and main else (3 if steps is None else steps)
    if resolved_steps < 0:
        raise ValueError("steps must be non-negative")
    scheme = "data_dependent" if initialization is None else initialization
    method = "parity" if initialization_method is None else initialization_method
    scale = 0.1 if initialization_scale is None else float(initialization_scale)
    std = 0.1 if initialization_std is None else float(initialization_std)
    _validate_initialization(scheme, method, scale, std)
    return RingConfig(
        profile_id=profile_id,
        n=n,
        seed=seed,
        steps=resolved_steps,
        initialization=scheme,
        initialization_method=method,
        initialization_scale=scale,
        initialization_std=std,
        run_kind="main" if main else "smoke",
    )


def _validate_initialization(scheme: str, method: str, scale: float, std: float) -> None:
    if scheme not in {"data_dependent", "small_angle", "uniform"}:
        raise ValueError(f"unknown ring initialization {scheme!r}")
    if method != "parity":
        raise ValueError(f"unknown data-dependent initialization method {method!r}")
    if not np.isfinite(scale) or scale < 0:
        raise ValueError("initialization_scale must be finite and non-negative")
    if not np.isfinite(std) or std < 0:
        raise ValueError("initialization_std must be finite and non-negative")


@contextmanager
def classical_only_import_guard() -> Iterator[None]:
    """Fail loudly if a classical training step tries to import a backend."""
    original_import = builtins.__import__

    def guarded_import(name: str, *args: Any, **kwargs: Any) -> Any:
        root = name.split(".", 1)[0]
        if root in FORBIDDEN_CLASSICAL_IMPORTS:
            raise RuntimeError(f"classical ring training attempted forbidden import: {name}")
        return original_import(name, *args, **kwargs)

    builtins.__import__ = guarded_import
    try:
        yield
    finally:
        builtins.__import__ = original_import


def _tvd(left: np.ndarray, right: np.ndarray) -> float:
    return float(0.5 * np.abs(np.asarray(left) - np.asarray(right)).sum())


def _metric_panel(dataset: RingsDataset, probabilities: np.ndarray) -> dict[str, float]:
    return {
        "train_spatial_mmd2": spatial_mmd2(probabilities, dataset.train_histogram, dataset.codec.centers, sigma=0.1),
        "test_spatial_mmd2": spatial_mmd2(probabilities, dataset.test_histogram, dataset.codec.centers, sigma=0.1),
        "train_hamming_mmd2_sigma_primary": hamming_mmd2(probabilities, dataset.train_histogram, sigma=0.5 * np.sqrt(dataset.codec.n)),
        "test_hamming_mmd2_sigma_primary": hamming_mmd2(probabilities, dataset.test_histogram, sigma=0.5 * np.sqrt(dataset.codec.n)),
        "train_tvd": _tvd(probabilities, dataset.train_histogram),
        "test_tvd": _tvd(probabilities, dataset.test_histogram),
        "quantization_floor_rms": float(dataset.train_quantization["rms_euclidean_error"]),
    }


def _initialize_ring_parameters(
    config: RingConfig, dataset: RingsDataset, generator: np.ndarray
) -> tuple[np.ndarray, dict[str, Any]]:
    _validate_initialization(
        config.initialization,
        config.initialization_method,
        config.initialization_scale,
        config.initialization_std,
    )
    if config.initialization == "data_dependent":
        target = dataset.train_target
        moments = target_moments(target, generator)
        theta, metadata = initialize_theta(
            generator,
            config.seed,
            scheme=config.initialization_method,
            scale=config.initialization_scale,
            target=target,
            return_metadata=True,
        )
        metadata.update(
            {
                "scheme": "data_dependent",
                "method": config.initialization_method,
                "scale": float(config.initialization_scale),
                "seed": int(config.seed),
                "randomness_source": "none; exact train target moments",
                "target_dataset_hash": dataset.dataset_hash,
                "target_split": "train",
                "target_representation": moments.representation,
                "target_moments_hash": hash_array(moments.values),
            }
        )
    elif config.initialization == "small_angle":
        theta, metadata = initialize_theta(
            generator,
            config.seed,
            scheme="small_angle",
            std=config.initialization_std,
            return_metadata=True,
        )
        metadata.update(
            {
                "scheme": "small_angle",
                "method": "normal",
                "scale": float(config.initialization_std),
                "seed": int(config.seed),
                "randomness_source": "numpy.default_rng(seed)",
            }
        )
    else:
        theta, metadata = initialize_theta(
            generator,
            config.seed,
            scheme="uniform",
            scale=config.initialization_scale,
            return_metadata=True,
        )
        metadata.update(
            {
                "scheme": "uniform",
                "method": "uniform_symmetric",
                "scale": float(config.initialization_scale),
                "seed": int(config.seed),
                "randomness_source": "numpy.default_rng(seed)",
            }
        )
    metadata["parameter_hash"] = hash_array(theta)
    return np.asarray(theta, dtype=np.float64), metadata


def _resolve_source_commit(configured: str | None, observed: object) -> tuple[str, str]:
    """Resolve provenance without rewriting an explicit historical commit."""

    if not isinstance(observed, str) or not observed:
        raise ValueError("ring source provenance has no observed commit")
    if configured is None or configured == "working-tree":
        return observed, "observed_current_commit"
    if not isinstance(configured, str) or not configured:
        raise ValueError("ring source_commit must be a non-empty string or None")
    return configured, "explicit_configured_commit"


def train_rings(config: RingConfig) -> RingRun:
    source_provenance = git_source_identity(
        Path(__file__).resolve().parents[3],
        include_paths=("src/merlin_iqp", "scripts/v4_tcdp/train_rings.py", "pyproject.toml", "pytest.ini"),
    )
    configured_source_commit = config.source_commit
    resolved_source_commit, commit_resolution = _resolve_source_commit(
        configured_source_commit, source_provenance.get("observed_commit")
    )
    source_provenance = {
        **source_provenance,
        "configured_commit": configured_source_commit,
        "resolved_commit": resolved_source_commit,
        "commit_resolution": commit_resolution,
        "commit_rule": SOURCE_COMMIT_RULE,
        "commit_matches_observed": resolved_source_commit == source_provenance.get("observed_commit"),
    }
    if config.source_commit != resolved_source_commit:
        config = replace(config, source_commit=resolved_source_commit)
    dataset = load_rings_dataset(config.n)
    generator = chain_1d(config.n, config.n - 1)
    initial_theta, initialization_metadata = _initialize_ring_parameters(config, dataset, generator)
    model = IQPModel(generator, initial_theta, provenance={"family": config.generator_family, "profile": config.profile_id})
    profile = PROFILE_REGISTRY[config.profile_id]
    if profile.kernel_kind == "spatial_gaussian":
        kernel = KernelSpec(kind="spatial_gaussian", sigma=config.sigma, centers=dataset.codec.centers, provenance={"profile": config.profile_id})
    else:
        kernel = KernelSpec(kind="hamming_gaussian", sigma=config.sigma, provenance={"profile": config.profile_id})
    trainer = Trainer(model, dataset.train_target, kernel, optimizer=config.optimizer, lr=config.lr, seed=config.seed, source_commit=config.source_commit)
    with classical_only_import_guard():
        result = trainer.run(config.steps)
    probabilities = model.probability_vector_exact()
    return RingRun(
        config=config,
        dataset=dataset,
        generator=generator.copy(),
        initial_theta=initial_theta.copy(),
        final_theta=np.asarray(result["theta"], dtype=np.float64),
        output_probabilities=probabilities,
        loss_history=tuple(float(x) for x in result["loss_history"]),
        metrics=_metric_panel(dataset, probabilities),
        photonic_evaluation=dict(PHOTONIC_EVALUATION),
        initialization_metadata=initialization_metadata,
        source_provenance=source_provenance,
    )


def _replication_key(run: RingRun) -> str:
    config = asdict(run.config)
    config.pop("seed", None)
    return hash_json(
        {
            "config": config,
            "dataset_hash": run.dataset.dataset_hash,
            "generator_hash": hash_array(run.generator),
            "initial_parameter_hash": hash_array(run.initial_theta),
            "final_parameter_hash": hash_array(run.final_theta),
        }
    )


def _artifact_config_payload(run: RingRun) -> dict[str, Any]:
    config = asdict(run.config)
    # The seed is already part of the cell id.  Excluding it keeps all seeds
    # for one experimental configuration in the same replication namespace.
    config.pop("seed", None)
    return {
        "config": config,
        "sigma": run.config.sigma,
        "profile_kernel_kind": PROFILE_REGISTRY[run.config.profile_id].kernel_kind,
        "dataset_hash": run.dataset.dataset_hash,
        "generator_hash": hash_array(run.generator),
    }


def _artifact_config_id(run: RingRun) -> str:
    return hash_json(_artifact_config_payload(run))[:16]


def _replication_identity(run: RingRun, destination: Path) -> dict[str, Any]:
    key = _replication_key(run)
    manifest_path = destination / "manifest.json"
    candidates: list[dict[str, Any]] = []
    group_root = destination.parent
    pattern = f"n{run.config.n}_seed*_{run.config.run_kind}/manifest.json"
    for candidate_path in sorted(group_root.glob(pattern)):
        if candidate_path.resolve() == manifest_path.resolve():
            continue
        try:
            candidate = json.loads(candidate_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        candidates.append(candidate)
    matching = [candidate for candidate in candidates if candidate.get("replication_identity", {}).get("equivalence_key") == key]
    duplicate_of = matching[0].get("run_id") if matching else None
    observed_keys = {
        candidate.get("replication_identity", {}).get("equivalence_key")
        for candidate in candidates
        if candidate.get("replication_identity", {}).get("equivalence_key")
    }
    observed_keys.add(key)
    deterministic = run.config.initialization == "data_dependent" and run.config.initialization_method == "parity"
    return {
        "replica_id": f"{run.config.profile_id}/{run.config.cell_id}",
        "replication_group": f"{run.config.profile_id}/n{run.config.n}/{run.config.run_kind}",
        "seed": int(run.config.seed),
        "equivalence_key": key,
        "initial_parameter_hash": hash_array(run.initial_theta),
        "final_parameter_hash": hash_array(run.final_theta),
        "randomness_source": run.initialization_metadata["randomness_source"],
        "deterministic_initialization": deterministic,
        "status": "duplicate_deterministic" if duplicate_of else ("deterministic_primary" if deterministic else "unique_seeded_ablation"),
        "independent_replica": False if duplicate_of or deterministic else True,
        "duplicate_of": duplicate_of,
        "observed_replica_count": len(candidates) + 1,
        "n_unique_parameterizations_observed": len(observed_keys),
    }


def _manifest(run: RingRun, replication_identity: dict[str, Any]) -> dict[str, Any]:
    config = asdict(run.config)
    config["sigma"] = run.config.sigma
    config["profile_kernel_kind"] = PROFILE_REGISTRY[run.config.profile_id].kernel_kind
    artifact_config_id = _artifact_config_id(run)
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": f"{run.config.profile_id}/{run.config.cell_id}",
        "config": config,
        "artifact_identity": {
            "config_id": artifact_config_id,
            "config_payload": _artifact_config_payload(run),
            "namespace": f"{run.config.profile_id}/config-{artifact_config_id}/{run.config.cell_id}",
        },
        "profile_registry": available_profiles(),
        "dataset": run.dataset.manifest(),
        "initialization": run.initialization_metadata,
        "replication_identity": replication_identity,
        "model": {
            "generator_family": run.config.generator_family,
            "generator_hash": hash_array(run.generator),
            "generator_shape": list(run.generator.shape),
            "initial_theta_hash": hash_array(run.initial_theta),
            "final_theta_hash": hash_array(run.final_theta),
            "output_probability_hash": hash_array(run.output_probabilities),
            "bit_order": "msb_first",
        },
        "metrics": run.metrics,
        "selection_rule": "fixed_last_step",
        "photonic_evaluation": run.photonic_evaluation,
        "source_provenance": run.source_provenance,
        "legacy_v1_context": {
            "status": "context_only",
            "ansatz": "QuantumLayer.simple",
            "output_bins": 462,
            "native_mmd_comparison": "forbidden_unmatched_ansatz_and_output_space",
        },
        "environment": {"python": platform.python_version(), "numpy": np.__version__},
        "manifest_hash": hash_json(
            {
                "run_id": f"{run.config.profile_id}/{run.config.cell_id}",
                "dataset": run.dataset.dataset_hash,
                "config": config,
                "initialization": run.initialization_metadata,
                "replication_key": replication_identity["equivalence_key"],
                "artifact_config_id": artifact_config_id,
                "theta": hash_array(run.final_theta),
            }
        ),
    }


def _stable_manifest_payload(payload: dict[str, Any]) -> dict[str, Any]:
    """Exclude replica-group observations from immutable run identity."""

    stable = dict(payload)
    stable.pop("replication_identity", None)
    return stable


def _validate_existing_artifacts(
    paths: dict[str, Path], manifest: dict[str, Any], run: RingRun, decoded_centers: np.ndarray
) -> None:
    missing = [str(path) for path in paths.values() if not path.is_file()]
    if missing:
        raise FileExistsError(f"ring artifact destination is incomplete; missing: {', '.join(missing)}")
    try:
        with np.load(paths["dataset"], allow_pickle=False) as dataset_archive:
            expected_dataset = {
                "raw_train": run.dataset.raw_train,
                "raw_test": run.dataset.raw_test,
                "normalized_train": run.dataset.normalized_train,
                "normalized_test": run.dataset.normalized_test,
                "train_ids": run.dataset.train_ids,
                "test_ids": run.dataset.test_ids,
                "min_values": run.dataset.min_values,
                "max_values": run.dataset.max_values,
                "scale": run.dataset.scale,
                "centers": run.dataset.codec.centers,
                "train_indices": run.dataset.train_indices,
                "test_indices": run.dataset.test_indices,
                "train_counts": run.dataset.train_counts,
                "test_counts": run.dataset.test_counts,
                "train_histogram": run.dataset.train_histogram,
                "test_histogram": run.dataset.test_histogram,
            }
            for name, expected in expected_dataset.items():
                if name not in dataset_archive or hash_array(dataset_archive[name]) != hash_array(expected):
                    raise ValueError(f"ring dataset artifact hash mismatch for {name}")
        with np.load(paths["run"], allow_pickle=False) as run_archive:
            expected_run = {
                "generator": run.generator,
                "initial_theta": run.initial_theta,
                "final_theta": run.final_theta,
                "output_probabilities": run.output_probabilities,
                "loss_history": np.asarray(run.loss_history),
                "decoded_centers": decoded_centers,
            }
            for name, expected in expected_run.items():
                if name not in run_archive or hash_array(run_archive[name]) != hash_array(expected):
                    raise ValueError(f"ring run artifact hash mismatch for {name}")
        summary = json.loads(paths["summary"].read_text(encoding="utf-8"))
        expected_summary = {
            "run_id": manifest["run_id"],
            "initialization": manifest["initialization"],
            "replication_identity": manifest["replication_identity"],
            "metrics": manifest["metrics"],
            "photonic_evaluation": manifest["photonic_evaluation"],
        }
        if summary != expected_summary:
            raise ValueError("ring summary does not match the immutable manifest fields")
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as error:
        raise FileExistsError(f"ring artifact destination failed integrity validation: {paths['manifest'].parent}") from error


def write_run_artifacts(run: RingRun, output_root: str | Path) -> dict[str, Path]:
    output_root = Path(output_root)
    artifact_config_id = _artifact_config_id(run)
    destination = output_root / run.config.profile_id / f"config-{artifact_config_id}" / run.config.cell_id
    dataset_path = destination / "dataset.npz"
    run_path = destination / "run.npz"
    manifest_path = destination / "manifest.json"
    summary_path = destination / "summary.json"
    paths = {"dataset": dataset_path, "run": run_path, "manifest": manifest_path, "summary": summary_path}
    decoded_centers = run.dataset.codec.decode(np.arange(2**run.config.n))
    replication_identity = _replication_identity(run, destination)
    payload = _manifest(run, replication_identity)
    if destination.exists():
        if not destination.is_dir() or not manifest_path.is_file():
            raise FileExistsError(f"ring artifact destination is non-empty or incomplete: {destination}")
        try:
            existing_payload = json.loads(manifest_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise FileExistsError(f"ring artifact destination has an unreadable manifest: {destination}") from error
        if _stable_manifest_payload(existing_payload) != _stable_manifest_payload(payload):
            raise FileExistsError(f"incompatible ring artifact already exists at {destination}")
        _validate_existing_artifacts(paths, existing_payload, run, decoded_centers)
        # A matching run is deterministic and already owns any dependent
        # comparison artifact in this namespace; leave it intact.
        return paths

    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary_directory = Path(tempfile.mkdtemp(prefix=f".{destination.name}.", dir=destination.parent))
    try:
        np.savez_compressed(
            temporary_directory / "dataset.npz",
            raw_train=run.dataset.raw_train,
            raw_test=run.dataset.raw_test,
            normalized_train=run.dataset.normalized_train,
            normalized_test=run.dataset.normalized_test,
            train_ids=run.dataset.train_ids,
            test_ids=run.dataset.test_ids,
            min_values=run.dataset.min_values,
            max_values=run.dataset.max_values,
            scale=run.dataset.scale,
            centers=run.dataset.codec.centers,
            train_indices=run.dataset.train_indices,
            test_indices=run.dataset.test_indices,
            train_counts=run.dataset.train_counts,
            test_counts=run.dataset.test_counts,
            train_histogram=run.dataset.train_histogram,
            test_histogram=run.dataset.test_histogram,
        )
        np.savez_compressed(
            temporary_directory / "run.npz",
            generator=run.generator,
            initial_theta=run.initial_theta,
            final_theta=run.final_theta,
            output_probabilities=run.output_probabilities,
            loss_history=np.asarray(run.loss_history),
            decoded_centers=decoded_centers,
        )
        (temporary_directory / "manifest.json").write_text(
            json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8"
        )
        (temporary_directory / "summary.json").write_text(
            json.dumps(
                {
                    "run_id": payload["run_id"],
                    "initialization": run.initialization_metadata,
                    "replication_identity": replication_identity,
                    "metrics": run.metrics,
                    "photonic_evaluation": run.photonic_evaluation,
                },
                indent=2,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
        os.rename(temporary_directory, destination)
    except Exception:
        if temporary_directory.exists():
            shutil.rmtree(temporary_directory)
        raise
    return {"dataset": dataset_path, "run": run_path, "manifest": manifest_path, "summary": summary_path}


__all__ = ["PROFILE_REGISTRY", "RingConfig", "RingProfile", "RingRun", "available_profiles", "classical_only_import_guard", "resolve_config", "train_rings", "write_run_artifacts"]
