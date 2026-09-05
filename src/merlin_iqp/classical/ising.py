"""The explicitly scoped zero-field open Ising calibration target."""

from __future__ import annotations

import numpy as np

from .targets import ExactProbabilities


def ising_probabilities(n: int, couplings: np.ndarray | None = None, *, beta: float = 1.0, seed: int = 4001) -> np.ndarray:
    if n < 1 or not np.isfinite(beta):
        raise ValueError("n must be positive and beta must be finite")
    if couplings is None:
        couplings = np.random.default_rng(seed).normal(size=n - 1)
    J = np.asarray(couplings, dtype=np.float64)
    if J.shape != (n - 1,) or not np.all(np.isfinite(J)):
        raise ValueError("couplings must have shape (n-1,) and be finite")
    bits = _bits(n)
    spins = 1.0 - 2.0 * bits
    energies = beta * np.sum(J[None, :] * spins[:, :-1] * spins[:, 1:], axis=1)
    shifted = energies - energies.max()
    probabilities = np.exp(shifted)
    return probabilities / probabilities.sum()


def ising_target(n: int, couplings: np.ndarray | None = None, *, beta: float = 1.0, seed: int = 4001) -> ExactProbabilities:
    return ExactProbabilities(ising_probabilities(n, couplings, beta=beta, seed=seed))


def _bits(n: int) -> np.ndarray:
    indices = np.arange(2**n, dtype=np.uint64)
    shifts = np.arange(n - 1, -1, -1, dtype=np.uint64)
    return ((indices[:, None] >> shifts[None, :]) & 1).astype(np.uint8)
