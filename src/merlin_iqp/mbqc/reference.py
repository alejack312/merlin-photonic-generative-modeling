"""Independent exact references for M1 branch and corrected-output identities."""

from __future__ import annotations

from typing import Any

import numpy as np

from .pattern import M1Pattern


def _bits(width: int) -> np.ndarray:
    indices = np.arange(2**width, dtype=np.uint64)
    shifts = np.arange(width - 1, -1, -1, dtype=np.uint64)
    return ((indices[:, None] >> shifts[None, :]) & 1).astype(np.uint8)


def _bits_to_index(bits: np.ndarray) -> int:
    width = len(bits)
    if width == 0:
        return 0
    weights = 2 ** np.arange(width - 1, -1, -1, dtype=np.int64)
    return int(np.asarray(bits, dtype=np.int64) @ weights)


def _validate_distribution(distribution: Any, n: int) -> np.ndarray:
    values = np.asarray(distribution, dtype=np.float64)
    if values.shape != (2**n,) or not np.all(np.isfinite(values)) or np.any(values < -1e-14):
        raise ValueError("distribution must be a finite non-negative vector of length 2**n")
    values = np.maximum(values, 0.0)
    total = float(values.sum())
    if not np.isclose(total, 1.0, atol=1e-12, rtol=0.0):
        raise ValueError("distribution must sum to one")
    return values / total


def iqp_distribution_exact(pattern: M1Pattern) -> np.ndarray:
    """Evaluate q(theta) directly from the computational-basis phase sum."""

    z_bits = _bits(pattern.n)
    y_bits = z_bits
    parity = (z_bits @ pattern.G.T) % 2
    eigenvalues = 1.0 - 2.0 * parity.astype(np.float64)
    phases = np.exp(-1j * (eigenvalues @ pattern.effective_theta))
    walsh = 1.0 - 2.0 * ((y_bits @ z_bits.T) % 2).astype(np.float64)
    amplitudes = walsh @ phases / (2**pattern.n)
    probabilities = np.abs(amplitudes) ** 2
    return probabilities / probabilities.sum()


def joint_probabilities_from_distribution(
    distribution: Any, generator: Any
) -> np.ndarray:
    """Construct p(s,y)=2^-M q(y xor G.T s) with MSB-first bit ordering."""

    matrix = np.asarray(generator)
    if matrix.ndim != 2 or matrix.shape[1] < 1 or not np.all((matrix == 0) | (matrix == 1)):
        raise ValueError("generator must be a finite binary matrix with positive width")
    matrix = matrix.astype(np.uint8, copy=False)
    n, m = int(matrix.shape[1]), int(matrix.shape[0])
    q = _validate_distribution(distribution, n)
    result = np.empty((2**m, 2**n), dtype=np.float64)
    s_bits = _bits(m)
    y_bits = _bits(n)
    for s_index, s in enumerate(s_bits):
        mask = (s @ matrix) % 2
        for y_index, y in enumerate(y_bits):
            result[s_index, y_index] = q[_bits_to_index((y ^ mask).astype(np.uint8))] / (2**m)
    return result


def graph_state_branch_probabilities(pattern: M1Pattern) -> np.ndarray:
    """Project the graph state directly onto fixed ancilla and data bases."""

    n, m = pattern.n, pattern.m
    data_bits = _bits(n)
    ancilla_bits = _bits(m)
    result = np.zeros((2**m, 2**n), dtype=np.float64)
    graph_norm = 2.0 ** (-(n + m) / 2.0)
    data_norm = 2.0 ** (-n / 2.0)
    for s_index, s in enumerate(ancilla_bits):
        ancilla_bra = np.empty((m, 2), dtype=np.complex128)
        for j, outcome in enumerate(s):
            theta = pattern.effective_theta[j]
            ancilla_bra[j] = (
                (np.cos(theta), -1j * np.sin(theta))
                if outcome == 0
                else (np.sin(theta), 1j * np.cos(theta))
            )
        for y_index, y in enumerate(data_bits):
            amplitude = 0.0j
            for ancilla in ancilla_bits:
                ancilla_factor = 1.0 + 0.0j
                for j, bit in enumerate(ancilla):
                    ancilla_factor *= ancilla_bra[j, bit]
                for data in data_bits:
                    edge_parity = int((ancilla @ ((pattern.G @ data) % 2)) % 2)
                    data_sign = -1.0 if int(data @ y) % 2 else 1.0
                    amplitude += graph_norm * data_norm * data_sign * ancilla_factor * ((-1.0) ** edge_parity)
            result[s_index, y_index] = float(abs(amplitude) ** 2)
    return result


def corrected_output_distribution(joint: Any, output_xor_map: Any) -> np.ndarray:
    """Apply the classical XOR correction to every retained ancilla branch."""

    values = np.asarray(joint, dtype=np.float64)
    xor_map = np.asarray(output_xor_map)
    if values.ndim != 2 or xor_map.ndim != 2:
        raise ValueError("joint and output_xor_map have incompatible shapes")
    n = int(round(np.log2(values.shape[1])))
    m = int(round(np.log2(values.shape[0])))
    if (
        2**n != values.shape[1]
        or 2**m != values.shape[0]
        or xor_map.shape != (n, m)
        or not np.all((xor_map == 0) | (xor_map == 1))
    ):
        raise ValueError("output_xor_map must be a binary n-by-M map")
    result = np.zeros(2**n, dtype=np.float64)
    y_bits = _bits(n)
    s_bits = _bits(values.shape[0].bit_length() - 1)
    for s_index, s in enumerate(s_bits):
        mask = (xor_map @ s) % 2
        for y_index, y in enumerate(y_bits):
            result[_bits_to_index((y ^ mask).astype(np.uint8))] += values[s_index, y_index]
    return result


def total_variation_distance(left: Any, right: Any) -> float:
    """Return TVD for two normalized finite distributions."""

    first = np.asarray(left, dtype=np.float64)
    second = np.asarray(right, dtype=np.float64)
    if first.shape != second.shape:
        raise ValueError("distributions must have the same shape")
    return float(0.5 * np.abs(first - second).sum())
