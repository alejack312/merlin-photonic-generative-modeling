"""Regression tests for the MerLin dual-rail Phase 18 loss backend."""

import csv

import torch
import perceval as pcvl
import pytest

from merlin_iqp.encoding.dual_rail import (
    build_dual_rail_full_circuit,
    build_dual_rail_weight2_processor,
    dual_rail_all_zero_input,
    dual_rail_photonic_iqp_distribution,
    dual_rail_photonic_weight2_iqp_distribution,
    dual_rail_weight2_input_state,
    make_weight1_quantum_layer,
    make_weight2_quantum_layer,
)
from merlin_iqp.hardness import sweep
from scripts.v3_hardness.hardness_analysis import write_backend_comparison
from scripts.v3_hardness.loss_sweep import _chunk_path, _row_from_summary


def _lc_raw_probs(circuit, input_state, eta):
    proc = pcvl.Processor("SLOS", circuit.m)
    for mode in range(circuit.m):
        proc.add(mode, pcvl.LC(1.0 - eta))
    proc.add(0, circuit)
    proc.min_detected_photons_filter(0)
    proc.with_input(input_state)
    return {
        tuple(state): float(prob)
        for state, prob in proc.probs()["results"].items()
        if abs(float(prob)) > 1e-10
    }


def _merlin_raw_probs(layer, thetas):
    with torch.no_grad():
        theta = dict(layer.named_parameters())["theta"]
        theta.copy_(torch.tensor(thetas, dtype=theta.dtype))
        output = layer().flatten().tolist()
    return {
        tuple(key): float(prob)
        for key, prob in zip(layer.output_keys, output)
        if abs(float(prob)) > 1e-10
    }


def _tvd(a, b):
    return 0.5 * sum(abs(a.get(key, 0.0) - b.get(key, 0.0)) for key in set(a) | set(b))


def test_merlin_weight1_loss_matches_explicit_lc_raw_distribution():
    n, eta, thetas = 2, 0.6, [0.3, 0.9]
    actual = _merlin_raw_probs(make_weight1_quantum_layer(n, eta=eta), thetas)
    expected = _lc_raw_probs(
        build_dual_rail_full_circuit(n, thetas), dual_rail_all_zero_input(n), eta
    )
    assert sum(actual.values()) == pytest.approx(1.0, abs=1e-6)
    assert _tvd(actual, expected) <= 1e-6


def test_merlin_weight2_loss_matches_explicit_lc_and_herald_failure():
    n, i, j, eta, thetas = 2, 0, 1, 0.6, [0.3, 0.9]
    layer, herald_spec = make_weight2_quantum_layer(n, i, j, eta=eta)
    actual = _merlin_raw_probs(layer, thetas)
    reference_proc, _ = build_dual_rail_weight2_processor(n, i, j, thetas)
    expected = _lc_raw_probs(
        reference_proc.linear_circuit(), dual_rail_weight2_input_state(n), eta
    )
    assert _tvd(actual, expected) <= 1e-6

    expected_a, expected_b = herald_spec[4], herald_spec[5]
    actual_failure = sum(
        prob
        for state, prob in actual.items()
        if state[2 * n] != expected_a or state[2 * n + 1] != expected_b
    )
    expected_failure = sum(
        prob
        for state, prob in expected.items()
        if state[2 * n] != expected_a or state[2 * n + 1] != expected_b
    )
    assert actual_failure == pytest.approx(expected_failure, abs=1e-6)


def test_merlin_loss_endpoints_and_validation():
    lossless_default = dual_rail_photonic_iqp_distribution(2, [0.3, 0.9])
    lossless_explicit = dual_rail_photonic_iqp_distribution(2, [0.3, 0.9], eta=1.0)
    assert lossless_explicit == pytest.approx(lossless_default, abs=1e-7)

    dist, residual = dual_rail_photonic_iqp_distribution(2, [0.3, 0.9], eta=0.0)
    assert dist == {}
    assert residual == pytest.approx(1.0, abs=1e-6)

    dist, residual, herald_failure = dual_rail_photonic_weight2_iqp_distribution(
        2, 0, 1, [0.3, 0.9], eta=0.0
    )
    assert dist == {}
    assert residual == pytest.approx(0.0, abs=1e-6)
    assert herald_failure == pytest.approx(1.0, abs=1e-6)

    for invalid_eta in (-0.1, 1.1):
        with pytest.raises(ValueError):
            make_weight1_quantum_layer(2, eta=invalid_eta)
        with pytest.raises(ValueError):
            make_weight2_quantum_layer(2, 0, 1, eta=invalid_eta)


def test_hardness_sweep_backend_preserves_theta_substreams(monkeypatch):
    calls = []

    def polarization(n, thetas, eta):
        calls.append(("polarization", eta, tuple(thetas)))
        return {"00": 1.0}, 0.0, 1.0, {}

    def merlin(n, thetas, eta):
        calls.append(("merlin-dual-rail", eta, tuple(thetas)))
        return {"00": 1.0}, 0.0

    monkeypatch.setattr(sweep, "photonic_iqp_distribution_lossy", polarization)
    monkeypatch.setattr(sweep, "dual_rail_photonic_iqp_distribution", merlin)
    kwargs = dict(n=2, eta=0.8, scope="weight1", draw_start=3, draw_count=1)
    sweep._raw_values_for_cell(**kwargs, backend="polarization")
    sweep._raw_values_for_cell(**kwargs, backend="merlin-dual-rail")

    polarization_thetas = [entry[2] for entry in calls if entry[0] == "polarization"]
    merlin_thetas = [entry[2] for entry in calls if entry[0] == "merlin-dual-rail"]
    assert polarization_thetas == merlin_thetas
    with pytest.raises(ValueError, match="unknown backend"):
        sweep._raw_values_for_cell(**kwargs, backend="unknown")


def test_loss_sweep_rows_and_chunks_are_backend_specific():
    summary = {
        "n_draws": 1,
        "tvd_to_lossless_mean": 0.0,
        "tvd_to_lossless_std": 0.0,
        "tvd_to_uniform_mean": 0.1,
        "tvd_to_uniform_std": 0.0,
        "tvd_to_product_marginals_mean": 0.2,
        "tvd_to_product_marginals_std": 0.0,
        "alpha_mean": 1.0,
        "alpha_std": 0.0,
    }
    row = _row_from_summary(2, "weight1", "merlin-dual-rail", 0.8, summary)
    assert row["simulation_backend"] == "merlin-dual-rail"
    path = _chunk_path(
        ".pytest_cache/merlin_loss_out.csv",
        "merlin-dual-rail",
        "weight1",
        2,
        0.8,
        0,
        1,
    )
    assert "merlin-dual-rail_weight1" in path


def test_backend_comparison_csv_has_unique_columns():
    common = {
        "generator_scope": "weight1",
        "n": 2,
        "eta": 0.8,
        "n_draws": 1,
        "tvd_to_lossless_mean": 0.2,
        "herald_failure_prob_mean": None,
    }
    polarization = dict(common, simulation_backend="polarization")
    merlin = dict(
        common,
        simulation_backend="merlin-dual-rail",
        tvd_to_lossless_mean=0.200001,
    )
    path = ".pytest_cache/backend_comparison.csv"
    rows = write_backend_comparison([polarization], [merlin], path)
    assert rows[0]["tvd_to_lossless_mean_abs_delta"] == pytest.approx(1e-6)
    with open(path, newline="") as f:
        header = next(csv.reader(f))
    assert len(header) == len(set(header))
