"""Portable NPZ/JSON checkpoint storage; foreign pickle objects are unsupported."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import numpy as np

from .contracts import Checkpoint


def _jsonable(value: Any) -> Any:
    if isinstance(value, np.ndarray):
        return value.tolist()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_jsonable(item) for item in value]
    return value


def save_checkpoint(checkpoint: Checkpoint, path: str | Path, *, generator: np.ndarray | None = None) -> Path:
    if not isinstance(checkpoint, Checkpoint):
        raise TypeError("save_checkpoint expects a Checkpoint")
    destination = Path(path)
    if destination.suffix != ".npz":
        destination = destination.with_suffix(".npz")
    destination.parent.mkdir(parents=True, exist_ok=True)
    metadata = {
        "spec_hash": checkpoint.spec_hash,
        "dataset_hash": checkpoint.dataset_hash,
        "kernel_hash": checkpoint.kernel_hash,
        "step": checkpoint.step,
        "optimizer": checkpoint.optimizer,
        "optimizer_state": _jsonable(checkpoint.optimizer_state),
        "rng_state": _jsonable(checkpoint.rng_state),
        "dtype": checkpoint.dtype,
        "library_versions": _jsonable(checkpoint.library_versions),
        "source_commit": checkpoint.source_commit,
        "loss_history": list(checkpoint.loss_history),
        "checkpoint_selection_rule": checkpoint.checkpoint_selection_rule,
        "metadata": _jsonable(checkpoint.metadata),
    }
    arrays: dict[str, Any] = {"theta": checkpoint.theta, "metadata": np.asarray(json.dumps(metadata, sort_keys=True))}
    if generator is not None:
        arrays["G"] = np.asarray(generator, dtype=np.uint8)
    temporary = destination.with_suffix(destination.suffix + ".tmp")
    with temporary.open("wb") as handle:
        np.savez_compressed(handle, **arrays)
    temporary.replace(destination)
    return destination


def load_checkpoint(path: str | Path, *, expected_spec_hash: str | None = None, expected_dataset_hash: str | None = None, expected_kernel_hash: str | None = None) -> Checkpoint:
    source = Path(path)
    if not source.exists():
        raise FileNotFoundError(source)
    with np.load(source, allow_pickle=False) as archive:
        if "theta" not in archive or "metadata" not in archive:
            raise ValueError("checkpoint is missing theta or JSON metadata")
        metadata = json.loads(str(archive["metadata"].item()))
        checkpoint = Checkpoint(
            spec_hash=str(metadata["spec_hash"]),
            dataset_hash=str(metadata["dataset_hash"]),
            kernel_hash=str(metadata["kernel_hash"]),
            theta=np.asarray(archive["theta"], dtype=np.float64),
            step=int(metadata["step"]),
            optimizer=str(metadata["optimizer"]),
            optimizer_state=dict(metadata.get("optimizer_state", {})),
            rng_state=dict(metadata.get("rng_state", {})),
            dtype=str(metadata.get("dtype", "float64")),
            library_versions=dict(metadata.get("library_versions", {})),
            source_commit=metadata.get("source_commit"),
            loss_history=tuple(metadata.get("loss_history", [])),
            checkpoint_selection_rule=str(metadata.get("checkpoint_selection_rule", "fixed_last_step")),
            metadata=dict(metadata.get("metadata", {})),
        )
    if expected_spec_hash is not None and checkpoint.spec_hash != expected_spec_hash:
        raise ValueError("checkpoint spec hash does not match the requested run")
    if expected_dataset_hash is not None and checkpoint.dataset_hash != expected_dataset_hash:
        raise ValueError("checkpoint dataset hash does not match the requested run")
    if expected_kernel_hash is not None and checkpoint.kernel_hash != expected_kernel_hash:
        raise ValueError("checkpoint kernel hash does not match the requested run")
    return checkpoint


def checkpoint_generator(path: str | Path) -> np.ndarray:
    with np.load(path, allow_pickle=False) as archive:
        if "G" not in archive:
            raise ValueError("checkpoint does not contain generator rows")
        return np.asarray(archive["G"], dtype=np.uint8)
