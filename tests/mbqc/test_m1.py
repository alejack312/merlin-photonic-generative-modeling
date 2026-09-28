"""R5 M1 null, branch identity, corruption, and logical resource tests."""

from __future__ import annotations

import numpy as np
import pytest

from merlin_iqp.mbqc import (
    compile_m1,
    corrected_output_distribution,
    graph_state_branch_probabilities,
    iqp_distribution_exact,
    joint_probabilities_from_distribution,
    resource_report,
    total_variation_distance,
)


def _fixture(n: int) -> np.ndarray:
    return {
        1: np.array([[1]], dtype=np.uint8),
        2: np.array([[1, 1], [1, 0]], dtype=np.uint8),
        3: np.array([[1, 1, 0], [0, 1, 1]], dtype=np.uint8),
    }[n]


def _theta_profile(profile: str, m: int) -> np.ndarray:
    if profile == "zero":
        return np.zeros(m)
    if profile == "clifford":
        return np.full(m, np.pi / 4.0)
    if profile == "non_clifford":
        return np.full(m, np.pi / 8.0)
    if profile == "asymmetric":
        return np.asarray([0.13 + 0.071 * index for index in range(m)], dtype=np.float64)
    raise AssertionError(f"unknown fixture profile: {profile}")


@pytest.mark.parametrize("n", [1, 2, 3])
@pytest.mark.parametrize("profile", ["zero", "clifford", "non_clifford", "asymmetric"])
def test_m1_all_branches_match_independent_iqp_identity(n: int, profile: str) -> None:
    generator = _fixture(n)
    theta = _theta_profile(profile, len(generator))
    pattern = compile_m1(generator, theta)

    graph_branches = graph_state_branch_probabilities(pattern)
    independent_q = iqp_distribution_exact(pattern)
    expected_joint = joint_probabilities_from_distribution(independent_q, generator)
    corrected = corrected_output_distribution(graph_branches, pattern.output_xor_map)

    assert graph_branches.sum() == pytest.approx(1.0, abs=1e-12)
    assert np.max(np.abs(graph_branches - expected_joint)) <= 1e-12
    assert total_variation_distance(corrected, independent_q) <= 1e-12


def test_m1_corrupted_xor_is_red_first_on_non_invariant_point_mass() -> None:
    generator = np.array([[1, 1, 0], [0, 1, 1]], dtype=np.uint8)
    target = np.zeros(8, dtype=np.float64)
    target[0] = 1.0
    joint = joint_probabilities_from_distribution(target, generator)
    correct_map = generator.T
    wrong_map = correct_map.copy()
    wrong_map[0, 0] ^= 1

    corrupted = corrected_output_distribution(joint, wrong_map)
    with pytest.raises(AssertionError):
        np.testing.assert_allclose(corrupted, target, atol=1e-12, rtol=0.0)

    restored = corrected_output_distribution(joint, correct_map)
    np.testing.assert_allclose(restored, target, atol=1e-12, rtol=0.0)
    assert total_variation_distance(corrupted, target) > 1e-6


def test_m1_uniform_target_documents_corruption_invisible_control() -> None:
    generator = np.array([[1, 1, 0], [0, 1, 1]], dtype=np.uint8)
    target = np.full(8, 1.0 / 8.0)
    joint = joint_probabilities_from_distribution(target, generator)
    wrong_map = generator.T.copy()
    wrong_map[0, 0] ^= 1

    corrupted = corrected_output_distribution(joint, wrong_map)

    assert total_variation_distance(corrupted, target) <= 1e-12


def test_m1_adversarial_zero_angles_m_zero_repeated_rows_and_all_ones_branch() -> None:
    zero = compile_m1(np.array([[1, 1], [1, 0]], dtype=np.uint8), np.zeros(2))
    zero_joint = graph_state_branch_probabilities(zero)
    assert zero_joint.sum() == pytest.approx(1.0, abs=1e-12)

    m_zero = compile_m1(np.zeros((0, 3), dtype=np.uint8), np.zeros(0))
    m_zero_branches = graph_state_branch_probabilities(m_zero)
    assert m_zero_branches.shape == (1, 8)
    assert m_zero_branches.sum() == pytest.approx(1.0, abs=1e-12)
    assert m_zero_branches[0, 0] == pytest.approx(1.0, abs=1e-12)

    repeated = compile_m1(
        np.array([[1, 1, 0], [1, 1, 0]], dtype=np.uint8),
        np.array([0.17, -0.2]),
    )
    repeated_branches = graph_state_branch_probabilities(repeated)
    assert repeated_branches.sum() == pytest.approx(1.0, abs=1e-12)

    all_ones = np.ones(repeated.m, dtype=np.uint8)
    expected_mask = (repeated.G.T @ all_ones) % 2
    assert np.array_equal(expected_mask, np.array([0, 0, 0], dtype=np.uint8))


def test_m1_resource_report_is_logical_only_and_counts_edges_and_bases() -> None:
    pattern = compile_m1(
        np.array([[1, 1, 0], [0, 1, 1]], dtype=np.uint8),
        np.array([0.13, 0.27]),
    )
    report = resource_report(pattern)

    assert report["graph_qubits"] == 5
    assert report["edges"] == 4
    assert report["fixed_bases"]["data"] == "X"
    assert report["fixed_bases"]["ancilla"] == ["b(theta_0)", "b(theta_1)"]
    assert report["ideal_feed_forward_rounds"] == 0
    assert report["status"] == "logical-only"
    assert report["physical_graph_preparation_validated"] is False
