"""Explicit binary target representations and their Walsh moments."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

import numpy as np

from ._validation import binary_matrix, finite_vector, hash_array


def _validate_observables(observables: Any, width: int) -> np.ndarray:
    return binary_matrix(observables, name="observables", width=width)


@dataclass(frozen=True)
class BinarySamples:
    """Empirical binary observations; rows are samples, columns are qubits."""

    samples: np.ndarray
    weights: np.ndarray | None = None
    provenance: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        samples = binary_matrix(self.samples, name="samples")
        weights = None if self.weights is None else finite_vector(self.weights, name="weights", length=len(samples))
        if weights is not None and (np.any(weights < 0) or float(weights.sum()) <= 0):
            raise ValueError("weights must be non-negative with positive total mass")
        object.__setattr__(self, "samples", samples)
        object.__setattr__(self, "weights", weights)

    @property
    def n(self) -> int:
        return int(self.samples.shape[1])

    @property
    def hash(self) -> str:
        return hash_array(self.samples) + ("" if self.weights is None else hash_array(self.weights))


@dataclass(frozen=True)
class ExactProbabilities:
    """A normalized vector in computational-basis index order (qubit 0 is MSB)."""

    probabilities: np.ndarray
    provenance: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        probabilities = finite_vector(self.probabilities, name="probabilities")
        if len(probabilities) == 0 or len(probabilities) & (len(probabilities) - 1):
            raise ValueError("probabilities length must be a nonzero power of two")
        if np.any(probabilities < 0) or not np.isclose(float(probabilities.sum()), 1.0, atol=1e-10, rtol=1e-10):
            raise ValueError("probabilities must be non-negative and sum to one")
        object.__setattr__(self, "probabilities", probabilities / probabilities.sum())

    @property
    def n(self) -> int:
        return int(np.log2(len(self.probabilities)))

    @property
    def hash(self) -> str:
        return hash_array(self.probabilities)


@dataclass(frozen=True)
class WeightedSupport:
    """Sparse weighted support; weights are normalized once at this boundary."""

    bitstrings: np.ndarray
    weights: np.ndarray
    provenance: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        bitstrings = binary_matrix(self.bitstrings, name="bitstrings")
        weights = finite_vector(self.weights, name="weights", length=len(bitstrings))
        if np.any(weights < 0) or float(weights.sum()) <= 0:
            raise ValueError("weights must be non-negative with positive total mass")
        object.__setattr__(self, "bitstrings", bitstrings)
        object.__setattr__(self, "weights", weights / weights.sum())

    @property
    def n(self) -> int:
        return int(self.bitstrings.shape[1])

    @property
    def hash(self) -> str:
        return hash_array(self.bitstrings) + hash_array(self.weights)


@dataclass(frozen=True)
class TargetMoments:
    """Moments ``E[(-1)^(a dot x)]`` for a declared observable panel."""

    observables: np.ndarray
    values: np.ndarray
    representation: str

    def __post_init__(self) -> None:
        observables = binary_matrix(self.observables, name="observables")
        values = finite_vector(self.values, name="values", length=len(observables))
        if np.any(np.abs(values) > 1.0 + 1e-10):
            raise ValueError("target moments must lie in [-1, 1]")
        object.__setattr__(self, "observables", observables)
        object.__setattr__(self, "values", values)

    @property
    def n(self) -> int:
        return int(self.observables.shape[1])


def all_observables(n: int) -> np.ndarray:
    if n < 0 or n > 20:
        raise ValueError("n must be between 0 and 20 for full observable enumeration")
    indices = np.arange(2**n, dtype=np.uint64)
    shifts = np.arange(n - 1, -1, -1, dtype=np.uint64)
    return ((indices[:, None] >> shifts[None, :]) & 1).astype(np.uint8)


def _moments_for_support(bitstrings: np.ndarray, weights: np.ndarray, observables: np.ndarray) -> np.ndarray:
    signs = 1.0 - 2.0 * ((observables @ bitstrings.T) % 2).astype(np.float64)
    return signs @ weights


def target_moments(target: BinarySamples | ExactProbabilities | WeightedSupport | np.ndarray, observables: np.ndarray) -> TargetMoments:
    """Return weighted target moments without casting probabilities to integers."""
    obs = np.asarray(observables)
    if isinstance(target, BinarySamples):
        weights = np.ones(len(target.samples), dtype=np.float64) if target.weights is None else target.weights
        values = _moments_for_support(target.samples, weights / weights.sum(), _validate_observables(obs, target.n))
        return TargetMoments(obs, values, "weighted_samples" if target.weights is not None else "empirical_samples")
    if isinstance(target, WeightedSupport):
        return TargetMoments(obs, _moments_for_support(target.bitstrings, target.weights, _validate_observables(obs, target.n)), "weighted_support")
    if isinstance(target, ExactProbabilities):
        states = all_observables(target.n)
        values = _moments_for_support(states, target.probabilities, _validate_observables(obs, target.n))
        return TargetMoments(obs, values, "exact_probabilities")
    array = np.asarray(target)
    if array.ndim == 1:
        return target_moments(ExactProbabilities(array), obs)
    return target_moments(BinarySamples(array), obs)


def target_probability_vector(target: BinarySamples | ExactProbabilities | WeightedSupport | np.ndarray, n: int | None = None) -> np.ndarray:
    """Materialize a full exact vector where the representation permits it."""
    if isinstance(target, ExactProbabilities):
        return target.probabilities.copy()
    if isinstance(target, np.ndarray) and target.ndim == 1:
        return ExactProbabilities(target).probabilities.copy()
    if isinstance(target, BinarySamples):
        support, weights = target.samples, target.weights
        if weights is None:
            weights = np.ones(len(support), dtype=np.float64)
    elif isinstance(target, WeightedSupport):
        support, weights = target.bitstrings, target.weights
    else:
        raise ValueError("a full probability vector is required for this target")
    width = support.shape[1] if n is None else int(n)
    if width != support.shape[1]:
        raise ValueError("target width does not match n")
    result = np.zeros(2**width, dtype=np.float64)
    indices = np.array([int("".join(map(str, row)), 2) for row in support], dtype=np.intp)
    np.add.at(result, indices, weights / weights.sum())
    return result
