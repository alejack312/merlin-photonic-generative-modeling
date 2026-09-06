"""Focused contracts for the bounded discrete-key NAT optimizer."""

from __future__ import annotations

import json

import numpy as np
import pytest

from merlin_iqp.classical import ExactProbabilities, IQPModel, KernelSpec, generators_from_pairs
from merlin_iqp.classical.objectives import objective_and_gradient_exact
from merlin_iqp.deploy.compile import ALPHA_STEP
from merlin_iqp.experiments.nat import run_nat, write_nat_run


def _target_for_pair_key(key: int, *, singles: tuple[float, float] = (0.0, 0.0)) -> ExactProbabilities:
    generator = generators_from_pairs(2, [(0, 1)])
    theta = np.array([*singles, ALPHA_STEP * key / 4.0], dtype=np.float64)
    return ExactProbabilities(IQPModel(generator, theta).probability_vector_exact())


def test_pair_coordinate_search_moves_a_catalog_key() -> None:
    target = _target_for_pair_key(1)
    run = run_nat(target, [(0, 1)], pair_keys=[0], singles=[0.0, 0.0], steps=1, seed=7, sigma=0.8)
    assert run.final_pair_keys == (1,)
    assert run.pair_moves == 1
    assert run.budgets["pair_evaluations"] == 2


def test_pair_keys_and_compiled_winding_stay_on_catalog() -> None:
    run = run_nat(
        _target_for_pair_key(8),
        [(0, 1)],
        pair_thetas=[0.2 + np.pi / 2.0],
        singles=[0.0, 0.0],
        steps=0,
    )
    angle = run.final_compiled.pair_angles[0][1]
    assert 0 <= angle.key < 63
    assert angle.wrapped_alpha == pytest.approx(ALPHA_STEP * angle.key, abs=1e-14)
    assert angle.winding == 1
    assert angle.lifted_theta == pytest.approx(0.2 + np.pi / 2.0, abs=1e-14)
    assert run.final_pair_keys == (8,)
    assert run.to_dict()["final_compiled"]["pair_angles"][0]["winding"] == 1


def test_single_angles_remain_continuous_and_use_exact_gradient() -> None:
    target = _target_for_pair_key(1, singles=(0.31, -0.17))
    run = run_nat(target, [(0, 1)], pair_keys=[1], singles=[0.123456, -0.234567], steps=1, seed=3, sigma=0.8, single_optimizer="sgd", single_lr=0.01)
    assert run.initial_singles.tolist() == [0.123456, -0.234567]
    assert np.any(np.abs(run.final_singles - run.initial_singles) > 1e-12)
    assert not np.allclose(run.final_singles / (ALPHA_STEP / 4.0), np.round(run.final_singles / (ALPHA_STEP / 4.0)), atol=1e-10)
    compiled = run.final_compiled
    theta = np.array([*compiled.singles, compiled.pair_angles[0][1].lifted_theta])
    expected, _ = objective_and_gradient_exact(theta, run.generator, target, KernelSpec("hamming_gaussian", sigma=0.8))
    assert run.final_loss == expected


def test_bounded_run_is_reproducible_and_serializable(tmp_path) -> None:
    kwargs = dict(pair_keys=[0], singles=[0.123456, -0.234567], steps=4, seed=11, sigma=0.8, pair_budget=3)
    first = run_nat(_target_for_pair_key(3), [(0, 1)], **kwargs)
    second = run_nat(_target_for_pair_key(3), [(0, 1)], **kwargs)
    assert first.to_dict() == second.to_dict()
    assert first.budgets["pair_evaluations"] == 3
    path = write_nat_run(first, tmp_path / "nat.json")
    assert json.loads(path.read_text(encoding="utf-8")) == first.to_dict()
    assert first.provenance["replication"]["deterministic_initialization"] is True
    assert first.provenance["replication"]["independent_replica"] is False
    assert first.provenance["replication"]["n_unique_parameterizations_observed"] == 1
