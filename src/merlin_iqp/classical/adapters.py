"""Generator and angle adapters with explicit row-order contracts."""

from __future__ import annotations

from collections.abc import Iterable, Sequence

import numpy as np

from ._validation import binary_matrix, finite_vector


def chain_1d(n: int, k: int) -> np.ndarray:
    if not isinstance(n, (int, np.integer)) or n < 1:
        raise ValueError("n must be a positive integer")
    if not isinstance(k, (int, np.integer)) or not 0 <= k <= n - 1:
        raise ValueError("k must satisfy 0 <= k <= n-1")
    rows = [np.eye(n, dtype=np.uint8)[i] for i in range(n)]
    rows.extend(np.eye(n, dtype=np.uint8)[i] + np.eye(n, dtype=np.uint8)[i + 1] for i in range(k))
    return np.asarray(rows, dtype=np.uint8)


def generators_from_pairs(n: int, pairs: Iterable[Sequence[int]], *, sort_pairs: bool = True) -> np.ndarray:
    if not isinstance(n, (int, np.integer)) or n < 1:
        raise ValueError("n must be a positive integer")
    raw_pairs = list(pairs)
    if any(len(pair) != 2 for pair in raw_pairs):
        raise ValueError("pairs must contain exactly two indices")
    parsed = [(int(pair[0]), int(pair[1])) for pair in raw_pairs]
    if any(i < 0 or j >= n or i >= j for i, j in parsed):
        raise ValueError("pairs must satisfy 0 <= i < j < n")
    if len(set(parsed)) != len(parsed):
        raise ValueError("duplicate pairs are not supported")
    if sort_pairs:
        parsed = sorted(parsed)
    rows = [np.eye(n, dtype=np.uint8)[i] for i in range(n)]
    rows.extend(np.eye(n, dtype=np.uint8)[i] + np.eye(n, dtype=np.uint8)[j] for i, j in parsed)
    return np.asarray(rows, dtype=np.uint8)


def pairs_from_generators(G: np.ndarray) -> list[tuple[int, int]]:
    matrix = binary_matrix(G, name="G")
    n = matrix.shape[1]
    if len(matrix) < n or not np.array_equal(matrix[:n], np.eye(n, dtype=np.uint8)):
        raise ValueError("G must begin with all n single-qubit generators in qubit order")
    pairs: list[tuple[int, int]] = []
    for row in matrix[n:]:
        support = np.flatnonzero(row)
        if len(support) != 2:
            raise ValueError("non-single generators must have weight two")
        pair = (int(support[0]), int(support[1]))
        if pair in pairs:
            raise ValueError("duplicate pair generator")
        pairs.append(pair)
    if pairs != sorted(pairs):
        raise ValueError("general pair generators must be lexicographically sorted")
    return pairs


def generators_to_pairs(G: np.ndarray) -> list[tuple[int, int]]:
    return pairs_from_generators(G)


def round_trip_generators(G: np.ndarray) -> np.ndarray:
    matrix = binary_matrix(G, name="G")
    return generators_from_pairs(matrix.shape[1], pairs_from_generators(matrix), sort_pairs=False)


def adapt_theta(theta: np.ndarray, G: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Validate and return copies; no sign, bit-order, or winding changes occur here."""
    matrix = binary_matrix(G, name="G")
    values = finite_vector(theta, name="theta", length=len(matrix))
    if np.any(matrix.sum(axis=1) == 0):
        raise ValueError("G cannot contain zero-weight rows")
    return matrix, values
