"""R6 null #2: test-local graph-route mixture reference and red controls."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import pytest

from merlin_iqp.mbqc import compile_m1, iqp_distribution_exact


G = np.array([[1, 1], [0, 1]], dtype=np.uint8)
THETA_1 = 0.13
THETA_2A = 0.27
TOLERANCE = 1e-9


def _bits(width: int) -> np.ndarray:
    indices = np.arange(2**width, dtype=np.uint64)
    shifts = np.arange(width - 1, -1, -1, dtype=np.uint64)
    return ((indices[:, None] >> shifts[None, :]) & 1).astype(np.uint8)


def _bits_to_index(bits: np.ndarray) -> int:
    width = len(bits)
    weights = 2 ** np.arange(width - 1, -1, -1, dtype=np.int64)
    return int(np.asarray(bits, dtype=np.int64) @ weights) if width else 0


def _q_theta(theta: Sequence[float]) -> np.ndarray:
    return iqp_distribution_exact(compile_m1(G, np.asarray(theta, dtype=np.float64)))


def _policy_angles(theta_2b: float, s: np.ndarray) -> np.ndarray:
    return np.array([THETA_1, THETA_2A if int(s[0]) == 0 else theta_2b], dtype=np.float64)


def _graph_state_branch_probabilities(theta_2b: float) -> np.ndarray:
    data_bits = _bits(2)
    ancilla_bits = _bits(2)
    result = np.zeros((4, 4), dtype=np.float64)
    graph_norm = 2.0 ** (-2.0)
    data_norm = 2.0 ** (-1.0)
    for s_index, s in enumerate(ancilla_bits):
        theta = _policy_angles(theta_2b, s)
        ancilla_bra = np.empty((2, 2), dtype=np.complex128)
        for j, outcome in enumerate(s):
            angle = theta[j]
            ancilla_bra[j] = (
                (np.cos(angle), -1j * np.sin(angle))
                if outcome == 0
                else (np.sin(angle), 1j * np.cos(angle))
            )
        for y_index, y in enumerate(data_bits):
            amplitude = 0.0j
            for ancilla in ancilla_bits:
                ancilla_factor = 1.0 + 0.0j
                for j, bit in enumerate(ancilla):
                    ancilla_factor *= ancilla_bra[j, bit]
                for data in data_bits:
                    edge_parity = int((ancilla @ ((G @ data) % 2)) % 2)
                    data_sign = -1.0 if int(data @ y) % 2 else 1.0
                    amplitude += graph_norm * data_norm * data_sign * ancilla_factor * ((-1.0) ** edge_parity)
            result[s_index, y_index] = float(abs(amplitude) ** 2)
    return result


def _corrected_output_distribution(joint: np.ndarray, xor_map: np.ndarray) -> np.ndarray:
    result = np.zeros(4, dtype=np.float64)
    y_bits = _bits(2)
    s_bits = _bits(2)
    for s_index, s in enumerate(s_bits):
        mask = (xor_map @ s) % 2
        for y_index, y in enumerate(y_bits):
            result[_bits_to_index((y ^ mask).astype(np.uint8))] += joint[s_index, y_index]
    return result


def _tables_and_mixture(theta_2b: float, weights: Sequence[float] | None = None) -> tuple[list[np.ndarray], np.ndarray]:
    tables = [_q_theta(_policy_angles(theta_2b, s)) for s in _bits(2)]
    branch_weights = np.full(4, 0.25) if weights is None else np.asarray(weights, dtype=np.float64)
    return tables, sum((weight * table for weight, table in zip(branch_weights, tables, strict=True)), start=np.zeros(4))


@pytest.mark.parametrize("theta_2b", [-THETA_2A, THETA_2A + np.pi / 2.0])
def test_r6_correct_policy_matches_same_angle_mixture(theta_2b: float) -> None:
    joint = _graph_state_branch_probabilities(theta_2b)
    corrected = _corrected_output_distribution(joint, G.T)
    _, mixture = _tables_and_mixture(theta_2b)

    np.testing.assert_allclose(corrected, mixture, atol=TOLERANCE, rtol=0.0)


def _validate_policy_dependencies(dependencies: Sequence[Sequence[int]]) -> None:
    for ancilla_index, dependencies_for_ancilla in enumerate(dependencies):
        for dependency in dependencies_for_ancilla:
            if dependency >= ancilla_index:
                raise ValueError(
                    f"ancilla s{ancilla_index + 1} has a future/self dependency on s{dependency + 1}"
                )


def test_r6_equal_angles_collapse_to_plain_iqp_table() -> None:
    joint = _graph_state_branch_probabilities(THETA_2A)
    corrected = _corrected_output_distribution(joint, G.T)
    plain = _q_theta([THETA_1, THETA_2A])

    np.testing.assert_allclose(corrected, plain, atol=TOLERANCE, rtol=0.0)


@pytest.mark.parametrize("theta_2b", [THETA_2A + np.pi / 2.0])
def test_r6_non_vacuity_requires_distinct_tables_and_mixture(theta_2b: float) -> None:
    joint = _graph_state_branch_probabilities(theta_2b)
    corrected = _corrected_output_distribution(joint, G.T)
    tables, _ = _tables_and_mixture(theta_2b)
    table_gap = float(np.max(np.abs(tables[0] - tables[2])))
    mixture_gap_a = float(np.max(np.abs(corrected - tables[0])))
    mixture_gap_b = float(np.max(np.abs(corrected - tables[2])))

    assert table_gap > 1e-3
    assert mixture_gap_a > 1e-3
    assert mixture_gap_b > 1e-3


@pytest.mark.parametrize("theta_2b", [-THETA_2A, THETA_2A + np.pi / 2.0])
def test_r6_branch_weights_and_mass_are_uniform(theta_2b: float) -> None:
    joint = _graph_state_branch_probabilities(theta_2b)

    np.testing.assert_allclose(joint.sum(axis=1), np.full(4, 0.25), atol=TOLERANCE, rtol=0.0)
    assert abs(float(joint.sum()) - 1.0) <= TOLERANCE


def test_r6_drop_xor_is_red_control() -> None:
    joint = _graph_state_branch_probabilities(-THETA_2A)
    _, mixture = _tables_and_mixture(-THETA_2A)
    dropped_xor = _corrected_output_distribution(joint, np.zeros_like(G.T))

    with pytest.raises(AssertionError):
        np.testing.assert_allclose(dropped_xor, mixture, atol=TOLERANCE, rtol=0.0)


def test_r6_wrong_branch_weights_are_red_control() -> None:
    theta_2b = THETA_2A + np.pi / 2.0
    _, correct_mixture = _tables_and_mixture(theta_2b)
    _, wrong_mixture = _tables_and_mixture(theta_2b, weights=[0.3, 0.3, 0.2, 0.2])

    with pytest.raises(AssertionError):
        np.testing.assert_allclose(wrong_mixture, correct_mixture, atol=TOLERANCE, rtol=0.0)


def test_r6_reversed_bit_order_is_red_control() -> None:
    joint = _graph_state_branch_probabilities(-THETA_2A)
    _, mixture = _tables_and_mixture(-THETA_2A)
    reversed_bit_order = _corrected_output_distribution(joint, G.T[::-1, :])

    with pytest.raises(AssertionError):
        np.testing.assert_allclose(reversed_bit_order, mixture, atol=TOLERANCE, rtol=0.0)


@pytest.mark.parametrize(
    ("dependencies", "offending"),
    [([( ), (1,)], "s2"), ([( ), (2,)], "s3")],
)
def test_r6_policy_validator_rejects_self_or_later_dependency(
    dependencies: Sequence[Sequence[int]], offending: str
) -> None:
    with pytest.raises(ValueError, match=offending):
        _validate_policy_dependencies(dependencies)


def test_r6_policy_validator_accepts_earlier_dependency() -> None:
    _validate_policy_dependencies([(), (0,)])
