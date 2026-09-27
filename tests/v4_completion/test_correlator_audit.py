"""Red-first R2 null gates and correlator audit contracts."""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest
import numpy as np

from merlin_iqp.experiments.correlator_audit import (
    expected_unseen_coverage,
    frozen_model_correlator_audit,
    negative_reconstruction_mass,
    normalized_hamming_spectral_weights,
    parity_distribution,
    parseval_sse_from_moments,
    reconstruct_from_moments,
    sparse_moment_matching_distribution,
    spatial_walsh_quadratic_form,
    true_forward_kl,
    validate_r2_nulls,
    walsh_moments,
)
from merlin_iqp.classical.kernel import gaussian_hamming_matrix, spatial_walsh_matrix
from merlin_iqp.experiments.comparison import expected_occupancy


BENCHMARK_SCRIPT = Path(__file__).parents[2] / "scripts" / "v4_tcdp" / "benchmark_correlators.py"
BENCHMARK_SPEC = importlib.util.spec_from_file_location("benchmark_correlators", BENCHMARK_SCRIPT)
assert BENCHMARK_SPEC is not None and BENCHMARK_SPEC.loader is not None
benchmark_correlators = importlib.util.module_from_spec(BENCHMARK_SPEC)
BENCHMARK_SPEC.loader.exec_module(benchmark_correlators)


R2_TARGET = {
    "000": 0.5,
    "001": 0.0,
    "010": 0.0,
    "011": 0.0,
    "100": 0.0,
    "101": 0.0,
    "110": 0.0,
    "111": 0.5,
}

ASYMMETRIC_TARGET = {
    "000": 0.4,
    "001": 0.2,
    "010": 0.1,
    "011": 0.0,
    "100": 0.0,
    "101": 0.0,
    "110": 0.0,
    "111": 0.3,
}


def test_r2_owner_fixture_passes_both_nulls() -> None:
    moments = walsh_moments(R2_TARGET)
    rebuilt = reconstruct_from_moments(moments, n=3)

    report = validate_r2_nulls(R2_TARGET, rebuilt)

    assert report["identity_residual_max"] <= 1e-9
    assert report["uniform_reference_sse"] == pytest.approx(0.375, abs=1e-9)


def test_identity_null_rejects_dropped_moment() -> None:
    moments = walsh_moments(R2_TARGET)
    moments.pop((0, 1))
    rebuilt = reconstruct_from_moments(moments, n=3)

    with pytest.raises(AssertionError, match="identity_residual_max"):
        validate_r2_nulls(R2_TARGET, rebuilt)


def test_uniform_null_rejects_missing_two_to_the_minus_n() -> None:
    moments = walsh_moments(R2_TARGET)
    rebuilt = reconstruct_from_moments(moments, n=3)
    wrong_reference = sum(value * value for subset, value in moments.items() if subset)

    with pytest.raises(AssertionError, match="uniform_reference_sse"):
        validate_r2_nulls(
            R2_TARGET,
            rebuilt,
            reported_uniform_reference_sse=wrong_reference,
        )


def test_identity_null_rejects_flipped_bit_order() -> None:
    moments = walsh_moments(ASYMMETRIC_TARGET, bit_order="msb")
    rebuilt = reconstruct_from_moments(moments, n=3, bit_order="lsb")

    with pytest.raises(AssertionError, match="identity_residual_max"):
        validate_r2_nulls(ASYMMETRIC_TARGET, rebuilt)


def test_identity_null_rejects_wrong_sign_convention() -> None:
    moments = walsh_moments(ASYMMETRIC_TARGET)
    rebuilt = reconstruct_from_moments(moments, n=3, character_sign=1)

    with pytest.raises(AssertionError, match="identity_residual_max"):
        validate_r2_nulls(ASYMMETRIC_TARGET, rebuilt)


def test_b0_parseval_and_high_order_parity_fixture() -> None:
    parity = parity_distribution(3, 1.0)
    uniform = parity_distribution(3, 0.0)
    direct, spectral = parseval_sse_from_moments(parity, uniform)

    assert direct == pytest.approx(spectral, abs=1e-12)
    parity_moments = walsh_moments(parity)
    uniform_moments = walsh_moments(uniform)
    assert all(parity_moments[key] == pytest.approx(uniform_moments[key], abs=1e-12) for key in ((0,), (1,), (2,), (0, 1), (0, 2), (1, 2)))
    assert parity_moments[(0, 1, 2)] == pytest.approx(1.0)


def test_b0_hamming_spectrum_is_normalized_and_spatial_off_diagonals_are_retained() -> None:
    weights = normalized_hamming_spectral_weights(3, sigma=0.7)
    assert sum(weights.values()) == pytest.approx(1.0, abs=1e-12)

    centers = [[0.0], [1.0], [0.2], [1.2]]
    kernel = gaussian_hamming_matrix(2, sigma=0.8)
    spatial = spatial_walsh_matrix(centers, sigma=0.8)
    delta = [0.2, -0.1, -0.05, -0.05]
    direct = sum(delta[i] * kernel[i, j] * delta[j] for i in range(4) for j in range(4))
    assert spatial_walsh_quadratic_form(delta, kernel) == pytest.approx(direct, abs=1e-12)
    assert np.max(np.abs(spatial - np.diag(np.diag(spatial)))) > 1e-6


def test_b0_signed_vector_uses_quadratic_metrics_and_true_kl_rejects_support_mismatch() -> None:
    assert negative_reconstruction_mass([1.5, -0.5]) == pytest.approx(0.5)
    assert true_forward_kl(np.array([1.0, 0.0]), np.array([0.0, 1.0])) == float("inf")


def test_b0_empty_unseen_set_and_occupancy_are_explicit() -> None:
    candidate = {"00": 0.25, "01": 0.25, "10": 0.25, "11": 0.25}
    assert expected_unseen_coverage(candidate, tuple(candidate), tuple(candidate), 100) == 0.0
    assert expected_occupancy(np.full(4, 0.25), 2)["expected_occupancy"] == pytest.approx(4 * (1 - 0.75**2))


def test_b0_sparse_moment_fixture_is_normalized_nonnegative_and_constraint_exact() -> None:
    result = sparse_moment_matching_distribution(3, 1)
    vector = result["distribution"]
    assert sum(vector.values()) == pytest.approx(1.0, abs=1e-12)
    assert min(vector.values()) >= -1e-12
    assert result["support_size"] <= 4
    assert result["max_constraint_residual"] <= 1e-12


def test_b1_frozen_model_report_has_order_residuals_and_oracle_label() -> None:
    report = frozen_model_correlator_audit(
        R2_TARGET,
        R2_TARGET,
        retained_subsets=((0,), (1,), (2,)),
        sigma=0.7,
        target_coefficient_access="oracle",
        same_theta_loss_before=0.2,
        same_theta_loss_after=0.1,
    )

    assert report["identity_residual_max"] <= 1e-12
    assert report["uniform_reference_sse"] == pytest.approx(0.375)
    assert report["target_coefficient_access"] == "oracle"
    assert report["oracle_target_coefficients"] is True
    assert set(report["residual_by_order"]) == {"1", "2", "3"}
    assert set(report["normalized_residual_by_order"]) == {"1", "2", "3"}
    assert set(report["kernel_weighted_contribution_by_order"]) == {"1", "2", "3"}
    assert report["omitted_energy"] == pytest.approx(0.375)
    assert report["omitted_residual_energy"] == pytest.approx(0.0)
    assert report["negative_reconstruction_mass"] >= 0.0
    assert report["same_theta_loss_change"] == pytest.approx(-0.1)


def test_b1_rejects_unlabeled_exact_target_access() -> None:
    with pytest.raises(ValueError, match="target_coefficient_access"):
        frozen_model_correlator_audit(R2_TARGET, R2_TARGET, target_coefficient_access="efficient")


def test_b1_cli_builder_emits_registered_columns(tmp_path: Path) -> None:
    target_path = tmp_path / "target.json"
    model_path = tmp_path / "model.json"
    target_path.write_text(json.dumps(R2_TARGET), encoding="utf-8")
    model_path.write_text(json.dumps(R2_TARGET), encoding="utf-8")

    report = benchmark_correlators.build_report(
        target_path,
        model_path,
        retained_order=1,
        sigma=0.7,
    )

    assert report["identity_residual_max"] <= 1e-12
    assert report["uniform_reference_sse"] == pytest.approx(0.375)
    assert report["retained_subsets"] == [[0], [1], [2]]
