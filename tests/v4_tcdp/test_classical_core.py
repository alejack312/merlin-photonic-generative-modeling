"""Focused acceptance tests for the NumPy-only v4 classical boundary."""

from __future__ import annotations

import json
import subprocess
import sys

import numpy as np
import pytest

from merlin_iqp.classical import (
    BinarySamples,
    DatasetBundle,
    ExactProbabilities,
    IQPModel,
    IQPSpec,
    KernelSpec,
    Trainer,
    WeightedSupport,
    all_observables,
    chain_1d,
    expectation_exact,
    gaussian_hamming_kernel,
    generators_from_pairs,
    generators_to_pairs,
    hamming_mmd2,
    hamming_mmd2_walsh,
    initialize_theta,
    spatial_mmd2,
    target_moments,
)
from merlin_iqp.classical.checkpoint import load_checkpoint
from merlin_iqp.classical.gradients import finite_difference_gradient, gradient_exact
from merlin_iqp.classical.expectation import expectation_gradient_exact
from merlin_iqp.classical.kernel import spatial_walsh_matrix
from merlin_iqp.classical.objectives import objective_and_gradient_exact
from merlin_iqp.experiments.datasets import load_rings_dataset


def _target() -> ExactProbabilities:
    values = np.array([0.03, 0.07, 0.12, 0.18, 0.21, 0.16, 0.14, 0.09])
    return ExactProbabilities(values / values.sum())


def test_nonuniform_target_moments_do_not_cast_probabilities() -> None:
    support = WeightedSupport(np.array([[0, 0], [0, 1]]), np.array([0.25, 0.75]))
    moments = target_moments(support, np.array([[0, 0], [0, 1], [1, 0]], dtype=np.uint8))
    np.testing.assert_allclose(moments.values, [1.0, -0.5, 1.0])
    samples = BinarySamples(np.array([[0, 0], [0, 1]]), weights=np.array([1.0, 3.0]))
    np.testing.assert_allclose(target_moments(samples, moments.observables).values, moments.values)


def test_hamming_direct_and_walsh_forms_agree_for_mixture() -> None:
    p = _target().probabilities
    q = IQPModel(chain_1d(3, 2), [0.2, -0.1, 0.3, 0.4, -0.2]).probability_vector_exact()
    direct = hamming_mmd2(p, q, sigmas=[0.4, 1.1], weights=[0.25, 0.75])
    walsh = hamming_mmd2_walsh(p, q, sigmas=[0.4, 1.1], weights=[0.25, 0.75])
    assert direct == pytest.approx(walsh, abs=1e-12)


def test_generic_spatial_walsh_identity_retains_off_diagonal_terms() -> None:
    points = np.array([[-1.0, 0.0], [0.2, 1.0], [0.5, -0.4], [1.0, 0.7]])
    p = np.array([0.1, 0.2, 0.3, 0.4])
    q = np.array([0.3, 0.1, 0.4, 0.2])
    direct = spatial_mmd2(p, q, points, sigma=0.8)
    W = np.array([[1, 1, 1, 1], [1, -1, 1, -1], [1, 1, -1, -1], [1, -1, -1, 1]], dtype=float)
    delta = W @ (p - q)
    B = spatial_walsh_matrix(points, sigma=0.8)
    assert np.max(np.abs(B - np.diag(np.diag(B)))) > 1e-4
    assert direct == pytest.approx(float(delta @ B @ delta), abs=1e-12)


@pytest.mark.parametrize("weights", [[-1.0, 2.0], [0.0, 0.0], [np.nan, 1.0]])
def test_spatial_mmd_rejects_invalid_kernel_mixture_weights(weights: list[float]) -> None:
    with pytest.raises(ValueError, match="weights"):
        spatial_mmd2(
            np.array([1.0, 0.0]),
            np.array([0.0, 1.0]),
            np.array([[0.0], [1.0]]),
            sigmas=[0.1, 10.0],
            weights=weights,
        )


def test_spatial_mmd_rejects_invalid_centers() -> None:
    with pytest.raises(ValueError, match="centers"):
        spatial_mmd2(
            np.array([1.0, 0.0]),
            np.array([0.0, 1.0]),
            np.array([[0.0], [np.nan]]),
        )


def test_expectation_and_objective_gradients_match_finite_difference() -> None:
    G = chain_1d(3, 2)
    theta = np.array([0.23, -0.17, 0.31, 0.41, -0.29])
    observable = np.array([1, 0, 1], dtype=np.uint8)
    analytic = np.array([expectation_exact(theta, G, observable)])
    finite = finite_difference_gradient(lambda x: expectation_exact(x, G, observable), theta)
    assert analytic.shape == (1,)
    assert np.any(np.abs(finite) > 1e-5)
    assert finite[0] == pytest.approx(expectation_gradient_exact(theta, G, observable, 0), abs=2e-10)
    kernel = KernelSpec("hamming_gaussian", sigma=0.7)
    _, exact_gradient = objective_and_gradient_exact(theta, G, _target(), kernel)
    objective_fd = finite_difference_gradient(lambda x: objective_and_gradient_exact(x, G, _target(), kernel)[0], theta)
    np.testing.assert_allclose(exact_gradient, objective_fd, rtol=2e-5, atol=2e-7)


def test_chain_and_general_pair_round_trip_preserve_order_contract() -> None:
    assert chain_1d(4, 0).shape == (4, 4)
    np.testing.assert_array_equal(chain_1d(4, 2)[4:], np.array([[1, 1, 0, 0], [0, 1, 1, 0]], dtype=np.uint8))
    G = generators_from_pairs(4, [(2, 3), (0, 2)])
    assert generators_to_pairs(G) == [(0, 2), (2, 3)]
    np.testing.assert_array_equal(generators_from_pairs(4, generators_to_pairs(G)), G)
    with pytest.raises(ValueError):
        chain_1d(3, 3)
    with pytest.raises(ValueError):
        generators_from_pairs(3, [(0, 0)])


def test_invalid_inputs_are_rejected_without_silent_casting() -> None:
    with pytest.raises(ValueError):
        ExactProbabilities(np.array([0.5, 0.6]))
    with pytest.raises(ValueError):
        BinarySamples(np.array([[0, 0.5]]))
    with pytest.raises(ValueError):
        IQPSpec(np.array([[1, 0], [0, 1]]), np.array([0.1]))
    with pytest.raises(ValueError):
        gaussian_hamming_kernel(np.array([0]), np.array([0]), 0.0)
    with pytest.raises(ValueError):
        from merlin_iqp.classical import DatasetBundle

        DatasetBundle("1", "leaky", 2, "samples", np.zeros((2, 2), dtype=np.uint8), np.zeros((2, 2), dtype=np.uint8))


def test_typed_ring_targets_construct_a_dataset_bundle() -> None:
    bundle = load_rings_dataset(4).bundle()
    assert bundle.n == 4
    assert bundle.train.hash
    assert bundle.test is not None and bundle.test.hash
    assert bundle.dataset_hash


def test_raw_dataset_bundle_hash_uses_full_array_content() -> None:
    first = np.zeros((256, 6), dtype=np.uint8)
    second = first.copy()
    second[100, 2] = 1
    kwargs = {"schema_version": "v1", "dataset_id": "fixture", "n": 6, "representation": "samples"}
    assert DatasetBundle(train=first, **kwargs).dataset_hash != DatasetBundle(train=second, **kwargs).dataset_hash


def test_classical_import_has_no_sibling_or_photonic_dependency() -> None:
    script = """
import sys
class Block:
    def find_spec(self, fullname, path=None, target=None):
        if fullname.startswith(('jax', 'perceval', 'merlinquantum', 'iqp_bp', 'iqp_mmd')):
            raise AssertionError(fullname)
        return None
sys.meta_path.insert(0, Block())
import merlin_iqp.classical
print('ok')
"""
    result = subprocess.run([sys.executable, "-c", script], check=True, capture_output=True, text=True)
    assert result.stdout.strip() == "ok"


def test_parity_initialization_is_deterministic_and_uses_weighted_target() -> None:
    G = chain_1d(2, 1)
    target = WeightedSupport(np.array([[0, 0], [0, 1]]), np.array([0.25, 0.75]))
    first, metadata = initialize_theta(G, 4001, scheme="parity", scale=0.1, target=target, return_metadata=True)
    second = initialize_theta(G, 4001, scheme="parity", scale=0.1, target=target)
    np.testing.assert_array_equal(first, second)
    assert metadata["target_representation"] == "weighted_support"


def test_adam_checkpoint_resume_is_equivalent(tmp_path) -> None:
    G = chain_1d(3, 2)
    target = _target()
    kernel = KernelSpec("hamming_gaussian", sigma=0.6)
    full = Trainer(IQPModel(G, [0.17, -0.09, 0.21, 0.31, -0.11]), target, kernel, optimizer="adam", lr=0.03, seed=9)
    full_result = full.run(4)
    first = Trainer(IQPModel(G, [0.17, -0.09, 0.21, 0.31, -0.11]), target, kernel, optimizer="adam", lr=0.03, seed=9)
    checkpoint_path = tmp_path / "step2.npz"
    first.run(2, checkpoint_path=checkpoint_path)
    resumed = Trainer(IQPModel(G, np.zeros(G.shape[0])), target, kernel, optimizer="adam", lr=0.03, seed=9)
    resumed.resume(checkpoint_path)
    resumed_result = resumed.run(2)
    np.testing.assert_allclose(full_result["theta"], resumed_result["theta"], atol=1e-13)
    assert full_result["loss_history"] == pytest.approx(resumed_result["loss_history"], abs=1e-13)
    loaded = load_checkpoint(checkpoint_path)
    assert loaded.step == 2
    with pytest.raises(ValueError):
        load_checkpoint(checkpoint_path, expected_kernel_hash="stale")


def test_checkpoint_resume_rejects_changed_learning_rate(tmp_path) -> None:
    G = chain_1d(3, 1)
    target = _target()
    kernel = KernelSpec("hamming_gaussian", sigma=0.6)
    checkpoint_path = tmp_path / "lr-mismatch.npz"
    Trainer(IQPModel(G, [0.17, -0.09, 0.13, 0.05]), target, kernel, optimizer="adam", lr=0.03, seed=9).run(1, checkpoint_path=checkpoint_path)
    resumed = Trainer(IQPModel(G, np.zeros(G.shape[0])), target, kernel, optimizer="adam", lr=0.2, seed=9)
    with pytest.raises(ValueError, match="checkpoint learning rate mismatch"):
        resumed.resume(checkpoint_path)


def test_adam_resume_rejects_incomplete_state_and_nonfinite_history(tmp_path) -> None:
    G = chain_1d(3, 1)
    target = _target()
    kernel = KernelSpec("hamming_gaussian", sigma=0.6)
    source = Trainer(IQPModel(G, [0.17, -0.09, 0.13, 0.05]), target, kernel, optimizer="adam", lr=0.03, seed=9)
    source.run(2)
    checkpoint = source.checkpoint()
    missing_path = tmp_path / "missing-state.npz"
    from dataclasses import replace
    from merlin_iqp.classical.checkpoint import save_checkpoint

    save_checkpoint(replace(checkpoint, optimizer_state={"lr": 0.03}), missing_path, generator=G)
    resumed = Trainer(IQPModel(G, np.zeros(G.shape[0])), target, kernel, optimizer="adam", lr=0.03, seed=9)
    with pytest.raises(ValueError, match="missing Adam optimizer state"):
        resumed.resume(missing_path)
    with pytest.raises(ValueError, match="loss_history must contain only finite"):
        replace(checkpoint, loss_history=(float("nan"),) * 3)


def test_rejected_adam_resume_is_atomic_and_rejects_negative_second_moments(tmp_path) -> None:
    from dataclasses import replace
    from merlin_iqp.classical.checkpoint import save_checkpoint

    G = chain_1d(2, 1)
    target = ExactProbabilities(np.array([0.1, 0.2, 0.3, 0.4]))
    kernel = KernelSpec("hamming_gaussian", sigma=0.6)
    source = Trainer(IQPModel(G, [0.17, -0.09, 0.13]), target, kernel, optimizer="adam", lr=0.03, seed=9)
    source.run(3)
    checkpoint = source.checkpoint()
    path = tmp_path / "invalid.npz"
    save_checkpoint(replace(checkpoint, optimizer_state={"lr": 0.03}), path, generator=G)
    resumed = Trainer(IQPModel(G, [0.7, 0.8, 0.9]), target, kernel, optimizer="adam", lr=0.03, seed=9)
    resumed.run(1)
    before = (resumed.model.theta.copy(), resumed.step, tuple(resumed.loss_history), resumed._m.copy(), resumed._v.copy(), resumed._adam_t)
    with pytest.raises(ValueError, match="missing Adam optimizer state"):
        resumed.resume(path)
    after = (resumed.model.theta, resumed.step, tuple(resumed.loss_history), resumed._m, resumed._v, resumed._adam_t)
    np.testing.assert_array_equal(after[0], before[0])
    assert after[1] == before[1]
    assert after[2] == before[2]
    np.testing.assert_array_equal(after[3], before[3])
    np.testing.assert_array_equal(after[4], before[4])
    assert after[5] == before[5]

    invalid_state = dict(checkpoint.optimizer_state)
    invalid_state["v"] = [-1.0, -1.0, -1.0]
    save_checkpoint(replace(checkpoint, optimizer_state=invalid_state), path, generator=G)
    with pytest.raises(ValueError, match="second moments"):
        resumed.resume(path)
