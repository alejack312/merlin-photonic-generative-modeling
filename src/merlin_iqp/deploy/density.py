"""Density-matrix instrument composition without a 4^n square superoperator."""

from __future__ import annotations

from typing import Mapping, Sequence

import numpy as np

from .compile import CompiledCircuit
from .maps import GateMap, ideal_cp_map, ideal_single_map


def _validate_eta(eta: float) -> float:
    value = float(eta)
    if not np.isfinite(value) or not 0.0 < value <= 1.0:
        raise ValueError("eta must be finite and in (0, 1]")
    return value


def _index(local_bits: int, rest_bits: int, qubits: tuple[int, ...], n: int) -> int:
    selected = set(qubits)
    local_cursor = len(qubits) - 1
    rest_cursor = n - len(qubits) - 1
    value = 0
    for qubit in range(n - 1, -1, -1):
        if qubit in selected:
            bit = (local_bits >> local_cursor) & 1
            local_cursor -= 1
        else:
            bit = (rest_bits >> rest_cursor) & 1
            rest_cursor -= 1
        value |= bit << (n - 1 - qubit)
    return value


def _apply_local_map(rho: np.ndarray, gate_map: GateMap, qubits: tuple[int, ...], n: int) -> np.ndarray:
    local_dim = 2 ** len(qubits)
    rest_dim = 2 ** (n - len(qubits))
    out = np.zeros_like(rho, dtype=complex)
    for rest_ket in range(rest_dim):
        rows = [_index(local, rest_ket, qubits, n) for local in range(local_dim)]
        for rest_bra in range(rest_dim):
            cols = [_index(local, rest_bra, qubits, n) for local in range(local_dim)]
            block = rho[np.ix_(rows, cols)]
            mapped = gate_map.apply(block)
            out[np.ix_(rows, cols)] = mapped
    return out


def compose_instruments(
    n: int,
    rho: np.ndarray,
    operations: Sequence[tuple[tuple[int, ...], GateMap]],
) -> tuple[np.ndarray, float]:
    """Apply unnormalized local instruments in the declared sequence.

    The returned matrix is normalized only once at the end.  ``success`` is
    the trace of the unnormalized composed instrument, called model success
    until a full physical reference validates the instrument model.
    """

    d = 2**n
    state = np.asarray(rho, dtype=complex)
    if state.shape != (d, d):
        raise ValueError(f"rho must have shape {(d, d)}")
    current = state.copy()
    for qubits, gate_map in operations:
        qubits = tuple(sorted(int(q) for q in qubits))
        if len(qubits) not in (1, 2) or any(q < 0 or q >= n for q in qubits):
            raise ValueError(f"unsupported local operation on {qubits}")
        expected_dim = 2 ** len(qubits)
        if gate_map.dimension != expected_dim:
            raise ValueError("gate map dimension does not match local qubits")
        current = _apply_local_map(current, gate_map, qubits, n)
    success = float(np.trace(current).real)
    if success <= 0.0:
        raise ValueError("composed instrument has non-positive model success")
    return current / success, success


def _hadamard_density(n: int) -> np.ndarray:
    H = np.array([[1.0, 1.0], [1.0, -1.0]], complex) / np.sqrt(2.0)
    result = H
    for _ in range(n - 1):
        result = np.kron(result, H)
    return result


def apply_compiled_density(
    compiled: CompiledCircuit,
    *,
    return_state: bool = False,
    eta: float = 1.0,
) -> tuple[dict[str, float], float] | tuple[np.ndarray, float]:
    """Evaluate the compiled IQP model under fixed-photon uniform loss.

    The logical state is conditioned on acceptance and therefore has the same
    normalized probabilities as the lossless instrument. The returned
    success is absolute accepted mass and includes ``eta**n`` exactly once.
    This is the restricted ``g2=0`` model.
    """

    n = compiled.n
    eta = _validate_eta(eta)
    plus = np.ones(2**n, complex) / np.sqrt(2**n)
    rho = np.outer(plus, plus.conj())
    operations: list[tuple[tuple[int, ...], GateMap]] = []
    for gate in compiled.gates:
        if gate.kind in {"single", "pair_compensation"}:
            operations.append((gate.qubits, ideal_single_map(gate.theta)))
        else:
            if gate.alpha is None:
                raise ValueError("CP gate is missing alpha")
            operations.append((gate.qubits, ideal_cp_map(gate.alpha)))
    diagonal_state, success = compose_instruments(n, rho, operations)
    H = _hadamard_density(n)
    measured = H @ diagonal_state @ H.conj().T
    probs = np.real(np.diag(measured))
    probs = np.where(np.abs(probs) < 1e-14, 0.0, probs)
    if np.any(probs < -1e-9):
        raise ValueError("ideal compiled probability vector contains negative mass")
    probs = np.maximum(probs, 0.0)
    probs /= probs.sum()
    success = float(success * eta**n)
    if return_state:
        return measured, success
    return {format(index, f"0{n}b"): float(value) for index, value in enumerate(probs)}, success


def ideal_iqp_distribution(
    n: int,
    singles: Sequence[float],
    pairs: Sequence[tuple[int, int, float]] = (),
) -> dict[str, float]:
    """Independent direct state-vector reference for raw logical IQP angles."""

    if len(singles) != n:
        raise ValueError("single-angle count does not match n")
    amplitudes = np.ones(2**n, complex) / np.sqrt(2**n)
    for index in range(2**n):
        phase = 0.0
        z = [1.0 if ((index >> (n - 1 - q)) & 1) == 0 else -1.0 for q in range(n)]
        phase += float(np.dot(np.asarray(singles, dtype=float), np.asarray(z)))
        for i, j, theta in pairs:
            phase += float(theta) * z[int(i)] * z[int(j)]
        amplitudes[index] *= np.exp(1j * phase)
    H = _hadamard_density(n)
    measured = H @ np.outer(amplitudes, amplitudes.conj()) @ H.conj().T
    probabilities = np.maximum(np.real(np.diag(measured)), 0.0)
    probabilities /= probabilities.sum()
    return {format(index, f"0{n}b"): float(value) for index, value in enumerate(probabilities)}
