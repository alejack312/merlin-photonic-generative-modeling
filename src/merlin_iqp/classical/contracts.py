"""Narrow, serializable contracts shared by the v4 classical pipelines."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal

import numpy as np

from ._validation import binary_matrix, finite_vector, hash_array, hash_json


@dataclass(frozen=True)
class IQPSpec:
    G: np.ndarray
    theta: np.ndarray
    convention_id: str = "iqp_z_msb_v1"
    family: str = "explicit"
    provenance: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        G = binary_matrix(self.G, name="G")
        theta = finite_vector(self.theta, name="theta", length=len(G))
        if np.any(G.sum(axis=1) == 0):
            raise ValueError("G cannot contain zero-weight generators")
        object.__setattr__(self, "G", G)
        object.__setattr__(self, "theta", theta)

    @property
    def n(self) -> int:
        return int(self.G.shape[1])

    @property
    def m(self) -> int:
        return int(self.G.shape[0])

    @property
    def hash(self) -> str:
        return hash_json({"G": hash_array(self.G), "theta": hash_array(self.theta), "convention_id": self.convention_id, "family": self.family, "provenance": self.provenance})


@dataclass(frozen=True)
class KernelSpec:
    kind: Literal["hamming_gaussian", "spatial_gaussian"]
    sigma: float | None = None
    sigmas: tuple[float, ...] = ()
    mixture_weights: tuple[float, ...] = ()
    centers: np.ndarray | None = None
    normalization: str = "mmd2"
    estimator_mode: str = "exact"
    provenance: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.kind not in {"hamming_gaussian", "spatial_gaussian"}:
            raise ValueError("kind must be hamming_gaussian or spatial_gaussian")
        sigmas = tuple(float(x) for x in (self.sigmas or (() if self.sigma is None else (self.sigma,))))
        if not sigmas or not all(np.isfinite(sigmas)) or any(x <= 0 for x in sigmas):
            raise ValueError("kernel must declare positive finite sigma values")
        weights = self.mixture_weights or tuple(1.0 / len(sigmas) for _ in sigmas)
        if len(weights) != len(sigmas) or not all(np.isfinite(weights)) or any(x < 0 for x in weights) or sum(weights) <= 0:
            raise ValueError("mixture_weights must be finite, non-negative, and nonzero")
        if self.kind == "spatial_gaussian":
            if self.centers is None:
                raise ValueError("spatial_gaussian requires centers")
            centers = np.asarray(self.centers, dtype=np.float64)
            if centers.ndim != 2 or not np.all(np.isfinite(centers)):
                raise ValueError("centers must be a finite matrix")
            object.__setattr__(self, "centers", centers.copy())
        object.__setattr__(self, "sigmas", sigmas)
        object.__setattr__(self, "sigma", sigmas[0])
        norm = float(sum(weights))
        object.__setattr__(self, "mixture_weights", tuple(float(x / norm) for x in weights))

    @property
    def hash(self) -> str:
        return hash_json({"kind": self.kind, "sigmas": self.sigmas, "weights": self.mixture_weights, "centers": None if self.centers is None else hash_array(self.centers), "normalization": self.normalization, "estimator_mode": self.estimator_mode, "provenance": self.provenance})


@dataclass(frozen=True)
class DatasetBundle:
    schema_version: str
    dataset_id: str
    n: int
    representation: str
    train: Any
    test: Any | None = None
    validation: Any | None = None
    provenance: dict[str, Any] = field(default_factory=dict)
    preprocessing: dict[str, Any] = field(default_factory=dict)
    feature_order: tuple[str, ...] = ()
    dataset_hash: str = ""

    def __post_init__(self) -> None:
        if self.n < 1 or not self.dataset_id or not self.schema_version:
            raise ValueError("dataset_id, schema_version, and positive n are required")
        split_hashes: dict[str, str] = {}
        for name, value in (("train", self.train), ("test", self.test), ("validation", self.validation)):
            if value is None:
                continue
            width = int(value.n) if hasattr(value, "n") else int(binary_matrix(value, name=name, width=self.n).shape[1])
            if width != self.n:
                raise ValueError(f"{name} width does not match n")
            value_hash = getattr(value, "hash", None)
            if value_hash is None:
                value_hash = hash_array(binary_matrix(value, name=name, width=self.n))
            split_hash = str(value_hash)
            split_hashes[name] = split_hash
        if len(split_hashes) > 1 and len(set(split_hashes.values())) != len(split_hashes):
            raise ValueError("dataset splits must not be identical; possible split leakage")
        if not self.dataset_hash:
            hashes = [getattr(x, "hash", repr(x)) for x in (self.train, self.test, self.validation) if x is not None]
            object.__setattr__(self, "dataset_hash", hash_json({"id": self.dataset_id, "n": self.n, "representation": self.representation, "splits": hashes, "preprocessing": self.preprocessing, "feature_order": self.feature_order}))


@dataclass(frozen=True)
class Checkpoint:
    spec_hash: str
    dataset_hash: str
    kernel_hash: str
    theta: np.ndarray
    step: int
    optimizer: str
    optimizer_state: dict[str, Any] = field(default_factory=dict)
    rng_state: dict[str, Any] = field(default_factory=dict)
    dtype: str = "float64"
    library_versions: dict[str, str] = field(default_factory=dict)
    source_commit: str | None = None
    loss_history: tuple[float, ...] = ()
    checkpoint_selection_rule: str = "fixed_last_step"
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        theta = finite_vector(self.theta, name="theta")
        if self.step < 0 or not self.spec_hash or not self.dataset_hash or not self.kernel_hash:
            raise ValueError("checkpoint hashes and non-negative step are required")
        object.__setattr__(self, "theta", theta)
        object.__setattr__(self, "loss_history", tuple(float(x) for x in self.loss_history))


@dataclass(frozen=True)
class BackendResult:
    backend_id: str
    distribution: np.ndarray | None = None
    samples: np.ndarray | None = None
    moments: np.ndarray | None = None
    accepted_mass: float | None = None
    conditioning: str = "unspecified"
    attempts: int | None = None
    detected: int | None = None
    accepted: int | None = None
    assumptions: dict[str, Any] = field(default_factory=dict)
    uncertainty: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CompatibilityRecord:
    status: Literal["exact_reproduction", "adapted_reproduction", "reference_only", "blocked"]
    reason: str
    source_row: str
    changed_fields: tuple[str, ...] = ()
    required_capability: str = ""
    evidence: tuple[str, ...] = ()
