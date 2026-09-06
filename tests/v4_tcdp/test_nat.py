"""Focused contracts for the bounded discrete-key NAT optimizer."""

from __future__ import annotations

import json
import sys

import numpy as np
import pytest

from merlin_iqp.classical import ExactProbabilities, IQPModel, KernelSpec, Trainer, generators_from_pairs
from merlin_iqp.classical.objectives import objective_and_gradient_exact
from merlin_iqp.deploy.compile import ALPHA_STEP
from merlin_iqp.experiments.nat import nat_report, run_matched_continuation, run_nat, write_nat_run
import scripts.v4_tcdp.run_nat as run_nat_cli


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


def test_positional_pair_values_follow_caller_pair_order() -> None:
    target = ExactProbabilities(np.arange(1, 9) / 36)
    pairs = [(1, 2), (0, 1)]
    sequence = run_nat(
        target,
        pairs,
        n=3,
        singles=[0.2, 0.3, 0.5],
        pair_keys=[1, 20],
        pair_windings=[0, 1],
        steps=0,
    )
    mapped = run_nat(
        target,
        pairs,
        n=3,
        singles=[0.2, 0.3, 0.5],
        pair_keys={(1, 2): 1, (0, 1): 20},
        pair_windings={(1, 2): 0, (0, 1): 1},
        steps=0,
    )
    assert sequence.config.pairs == ((0, 1), (1, 2))
    assert sequence.initial_pair_keys == mapped.initial_pair_keys == (20, 1)
    assert sequence.initial_pair_windings == mapped.initial_pair_windings == (1, 0)
    np.testing.assert_array_equal(sequence.generator, mapped.generator)
    np.testing.assert_allclose(
        [angle.lifted_theta for _, angle in sequence.final_compiled.pair_angles],
        [angle.lifted_theta for _, angle in mapped.final_compiled.pair_angles],
    )


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


def test_small_angle_initialization_std_is_forwarded() -> None:
    run = run_nat(
        _target_for_pair_key(1),
        [(0, 1)],
        initialization="small_angle",
        initialization_std=0.0,
        steps=0,
        seed=7,
    )
    assert run.config.initialization_std == 0.0
    assert np.all(run.initial_singles == 0.0)


def test_matched_continuation_preserves_optimizer_and_ideal_trajectory() -> None:
    target = _target_for_pair_key(3, singles=(0.23, -0.19))
    warm = run_nat(target, [(0, 1)], steps=3, seed=4, sigma=0.8, single_lr=0.01)
    continued = run_matched_continuation(target, [(0, 1)], warm, steps=2, pair_budget=4)
    resumed = run_nat(
        target,
        [(0, 1)],
        steps=2,
        seed=warm.config.seed,
        sigma=warm.config.sigma,
        single_lr=warm.config.single_lr,
        single_optimizer=warm.config.single_optimizer,
        pair_budget=4,
        topology=warm.config.topology,
        source_commit=warm.config.source_commit,
        initialization=warm.config.initialization,
        initialization_method=warm.config.initialization_method,
        initialization_scale=warm.config.initialization_scale,
        initialization_std=warm.config.initialization_std,
        singles=warm.final_singles,
        pair_keys=warm.final_pair_keys,
        pair_windings=warm.final_pair_windings,
        initial_optimizer_state={
            "kind": warm.config.single_optimizer,
            "m": warm.optimizer_m,
            "v": warm.optimizer_v,
            "step": warm.optimizer_step,
        },
    )
    assert continued.loss_history == resumed.loss_history
    assert np.array_equal(continued.final_singles, resumed.final_singles)
    assert continued.final_pair_keys == resumed.final_pair_keys
    assert continued.final_pair_windings == resumed.final_pair_windings
    assert continued.provenance["warm_start"] == warm.provenance["final_parameter_hash"]
    assert continued.config.allow_pair_moves is True


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


def test_pair_moves_reports_accepted_moves_and_pairs_changed_reports_endpoint_delta() -> None:
    target = _target_for_pair_key(3)
    run = run_nat(target, [(0, 1)], pair_keys=[0], singles=[0.0, 0.0], steps=2, seed=7, sigma=0.8)
    payload = run.to_dict()
    assert payload["pair_moves"] == run.budgets["pair_moves"]
    assert payload["pairs_changed"] == run.pairs_changed


def test_public_spatial_trainer_requires_geometry_and_fits_nontrivial_target() -> None:
    generator = generators_from_pairs(2, [(0, 1)])
    target_model = IQPModel(generator, np.array([0.7, 0.2, 0.1]))
    target = ExactProbabilities(target_model.probability_vector_exact())
    centers = np.array([[0.0, 0.0], [0.0, 1.0], [2.0, 0.0], [2.0, 3.0]])
    with pytest.raises(ValueError, match="requires centers"):
        Trainer(IQPModel(generator, np.zeros(3)), target, kernel="spatial_gaussian")
    trainer = Trainer(IQPModel(generator, np.array([0.2, 0.1, 0.05])), target, kernel="spatial_gaussian", centers=centers, optimizer="sgd", lr=0.1)
    result = trainer.run(5)
    assert result["loss_history"][0] > result["final_loss"]
    assert result["final_loss"] > 0.0


def test_nat_cli_emits_two_arms_from_one_frozen_warm_start(tmp_path, monkeypatch) -> None:
    output = tmp_path / "nat.json"
    monkeypatch.setattr(
        sys,
        "argv",
        ["run_nat.py", "--n", "4", "--seed", "0", "--steps", "1", "--matched-continuation", "--output", str(output)],
    )
    assert run_nat_cli.main() == 0
    warm = json.loads(output.with_name("nat-warm-start.json").read_text(encoding="utf-8"))
    arm_a = json.loads(output.with_name("nat-matched-arm-a.json").read_text(encoding="utf-8"))
    arm_b = json.loads(output.with_name("nat-matched-arm-b.json").read_text(encoding="utf-8"))
    assert warm["artifact"]["role"] == "frozen_warm_start"
    assert arm_a["artifact"]["common_start_hash"] == warm["artifact"]["state_hash"]
    assert arm_b["artifact"]["common_start_hash"] == warm["artifact"]["state_hash"]
    assert arm_a["artifact"]["evaluation_budget"] == arm_b["artifact"]["evaluation_budget"]
    assert arm_a["provenance"]["initial_parameter_hash"] == arm_b["provenance"]["initial_parameter_hash"]


def test_nat_report_separates_target_reference_and_acceptance() -> None:
    target = _target_for_pair_key(2)
    warm = run_nat(target, [(0, 1)], steps=1, seed=12, sigma=0.8)
    arm_a = run_matched_continuation(target, [(0, 1)], warm, steps=1, pair_budget=2, run_kind="matched_arm_a")
    arm_b = run_matched_continuation(target, [(0, 1)], warm, steps=1, pair_budget=2, run_kind="matched_arm_b")
    report = nat_report(target, warm, {"a": arm_a, "b": arm_b})
    assert report["status"] == "PASS"
    assert report["matching"]["common_start_state_hash"]
    assert report["arms"]["a"]["target_improvement"] >= 0.0
    assert report["arms"]["a"]["fixed_reference_tvd"] >= 0.0
    assert report["arms"]["a"]["acceptance"]["attempts_per_accepted_sample"] >= 1.0


def test_nat_time_limit_records_attempted_stop() -> None:
    run = run_nat(_target_for_pair_key(1), [(0, 1)], steps=2, time_limit_seconds=1e-12)
    assert run.budgets["status"] == "attempted/stopped"
    assert run.budgets["completed_steps"] == 0
