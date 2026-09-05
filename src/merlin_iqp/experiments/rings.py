"""Classical IQP training profiles for the additive two-ring study."""

from __future__ import annotations

import builtins
import json
import platform
from contextlib import contextmanager
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any, Iterator

import numpy as np

from merlin_iqp.classical import IQPModel, KernelSpec, Trainer, chain_1d, initialize_theta
from merlin_iqp.classical._validation import hash_array, hash_json
from merlin_iqp.classical.objectives import hamming_mmd2, spatial_mmd2

from .datasets import RingsDataset, load_rings_dataset


SCHEMA_VERSION = "v4_tcdp.rings_run.v1"
PHOTONIC_EVALUATION = {
    "status": "INCONCLUSIVE",
    "reason": "Phase 28 owned scope has no validated ideal photonic ring deployment adapter; no unsupported simulator label is substituted.",
}
FORBIDDEN_CLASSICAL_IMPORTS = frozenset({"torch", "perceval", "perceval_quandela", "merlinquantum", "merlin"})


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
    initialization: str = "small_angle"
    initialization_std: float = 0.1
    generator_family: str = "chain_1d"
    source_commit: str = "72e8079"
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


def available_profiles() -> dict[str, dict[str, Any]]:
    return {
        name: {
            "kernel_kind": profile.kernel_kind,
            "sigma_rule": profile.sigma_rule,
            "registered_n": list(profile.registered_n),
            "main_steps": profile.main_steps,
            "main_seeds": list(profile.main_seeds),
            "budget_status": "registered_not_launched",
        }
        for name, profile in PROFILE_REGISTRY.items()
    }


def resolve_config(profile_id: str, *, n: int = 4, seed: int = 0, steps: int | None = None, main: bool = False) -> RingConfig:
    if profile_id not in PROFILE_REGISTRY:
        raise ValueError(f"unknown ring profile {profile_id!r}")
    if n not in PROFILE_REGISTRY[profile_id].registered_n:
        raise ValueError(f"n={n} is not registered for {profile_id}; use one of {PROFILE_REGISTRY[profile_id].registered_n}")
    resolved_steps = PROFILE_REGISTRY[profile_id].main_steps if steps is None and main else (3 if steps is None else steps)
    if resolved_steps < 0:
        raise ValueError("steps must be non-negative")
    return RingConfig(profile_id=profile_id, n=n, seed=seed, steps=resolved_steps, run_kind="main" if main else "smoke")


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


def train_rings(config: RingConfig) -> RingRun:
    dataset = load_rings_dataset(config.n)
    generator = chain_1d(config.n, config.n - 1)
    initial_theta = initialize_theta(generator, config.seed, scheme=config.initialization, std=config.initialization_std)
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
    )


def _manifest(run: RingRun) -> dict[str, Any]:
    config = asdict(run.config)
    config["sigma"] = run.config.sigma
    config["profile_kernel_kind"] = PROFILE_REGISTRY[run.config.profile_id].kernel_kind
    return {
        "schema_version": SCHEMA_VERSION,
        "run_id": f"{run.config.profile_id}/{run.config.cell_id}",
        "config": config,
        "profile_registry": available_profiles(),
        "dataset": run.dataset.manifest(),
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
        "legacy_v1_context": {
            "status": "context_only",
            "ansatz": "QuantumLayer.simple",
            "output_bins": 462,
            "native_mmd_comparison": "forbidden_unmatched_ansatz_and_output_space",
        },
        "environment": {"python": platform.python_version(), "numpy": np.__version__},
        "manifest_hash": hash_json({"run_id": f"{run.config.profile_id}/{run.config.cell_id}", "dataset": run.dataset.dataset_hash, "theta": hash_array(run.final_theta)}),
    }


def write_run_artifacts(run: RingRun, output_root: str | Path) -> dict[str, Path]:
    destination = Path(output_root) / run.config.profile_id / run.config.cell_id
    destination.mkdir(parents=True, exist_ok=True)
    dataset_path = destination / "dataset.npz"
    run_path = destination / "run.npz"
    manifest_path = destination / "manifest.json"
    summary_path = destination / "summary.json"
    np.savez_compressed(
        dataset_path,
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
    decoded_centers = run.dataset.codec.decode(np.arange(2**run.config.n))
    np.savez_compressed(run_path, generator=run.generator, initial_theta=run.initial_theta, final_theta=run.final_theta, output_probabilities=run.output_probabilities, loss_history=np.asarray(run.loss_history), decoded_centers=decoded_centers)
    payload = _manifest(run)
    manifest_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    summary_path.write_text(json.dumps({"run_id": payload["run_id"], "metrics": run.metrics, "photonic_evaluation": run.photonic_evaluation}, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return {"dataset": dataset_path, "run": run_path, "manifest": manifest_path, "summary": summary_path}


__all__ = ["PROFILE_REGISTRY", "RingConfig", "RingProfile", "RingRun", "available_profiles", "classical_only_import_guard", "resolve_config", "train_rings", "write_run_artifacts"]
