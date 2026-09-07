"""Focused v4 deployment/compiler contracts.

These tests are intentionally independent of the existing v2/v3 encoding
tests. They exercise signs, winding, ideal instruments, density composition,
resource controls, and optional-backend capability boundaries.
"""

from __future__ import annotations

import inspect
import json
from pathlib import Path
from dataclasses import replace

import numpy as np
import pytest

from merlin_iqp.deploy import (
    GateMap,
    MapCache,
    FullFockResult,
    apply_compiled_density,
    fixed_photon_accepted_mass,
    compile_iqp,
    compile_generators,
    conditional_erasure_distribution,
    direct_fock_cp_reference,
    fixed_photon_attempts_per_sample,
    full_fock_cp_reference,
    heralded_cz_attempts_per_sample,
    ideal_cp_map,
    ideal_iqp_distribution,
    nearest_alpha_key,
    quantize_theta,
    reconstruct_cp_map,
    success_weighted_haar_fidelity,
    validate_gate_map,
)
import scripts.v4_tcdp.validate_deploy as validate_deploy
from merlin_iqp.deploy.density import compose_instruments
from merlin_iqp.deploy.maps import _choi_from_kraus


def _tvd(left: dict[str, float], right: dict[str, float]) -> float:
    return 0.5 * sum(abs(left.get(key, 0.0) - right.get(key, 0.0)) for key in set(left) | set(right))


def test_negative_phase_sign_and_pair_identity_metadata() -> None:
    compiled = compile_iqp(2, [0.2, -0.1], [(0, 1, 0.3)], quantize=False)
    assert compiled.gates[0].metadata["optical_phase"] == pytest.approx(-0.4)
    pair_compensations = [gate for gate in compiled.gates if gate.kind == "pair_compensation"]
    assert [gate.metadata["optical_phase"] for gate in pair_compensations] == pytest.approx([-0.6, -0.6])
    assert all(gate.metadata["sign"] == "negative_PS" for gate in pair_compensations)


@pytest.mark.parametrize("key", range(63))
def test_all_integer_alpha_keys_are_reachable(key: int) -> None:
    angle = key * 0.1
    nearest, wrapped = nearest_alpha_key(angle)
    assert nearest == key
    assert wrapped == pytest.approx(angle)


def test_circular_nearest_negative_and_tie_boundaries() -> None:
    assert nearest_alpha_key(-0.01)[0] == 0
    assert nearest_alpha_key(-0.08)[0] == 62
    assert nearest_alpha_key(3.15)[0] == 31  # deterministic lower-key tie
    wrapped = quantize_theta(np.pi / 2)
    assert wrapped.key == 0
    assert wrapped.winding == 1
    assert wrapped.lifted_theta == pytest.approx(np.pi / 2)


def test_winding_is_preserved_in_compiled_pair() -> None:
    compiled = compile_iqp(2, [0.3, 0.7], [(0, 1, 0.2 + np.pi / 2)], quantize=True)
    angle = compiled.pair_angles[0][1]
    assert angle.key == 8
    assert angle.winding == 1
    assert angle.lifted_theta == pytest.approx(0.2 + np.pi / 2)
    assert compiled.gates[-1].alpha == pytest.approx(0.8)
    assert compiled.gates[-2].metadata["lifted_theta"] == pytest.approx(0.2 + np.pi / 2)


def test_ideal_map_is_cp_and_trace_nonincreasing() -> None:
    gate = ideal_cp_map(np.pi / 3)
    report = validate_gate_map(gate)
    assert report.passed
    assert report.min_choi_eigenvalue >= -1e-9
    assert report.max_edagger_i_eigenvalue <= 1.0 + 1e-9
    U = np.diag([1, 1, 1, np.exp(1j * np.pi / 3)])
    assert success_weighted_haar_fidelity(gate, U) == pytest.approx(1.0, abs=1e-12)


def test_reconstructed_tomography_retains_zero_outcomes_and_is_physical() -> None:
    reconstructed = reconstruct_cp_map(np.pi / 3, use_perceval=False)
    assert reconstructed.metadata["tomography"]["preparations"] == 16
    assert reconstructed.metadata["tomography"]["readout_settings"] == 9
    assert reconstructed.metadata["tomography"]["heldout_input_error"] < 1e-9
    assert reconstructed.metadata["tomography"]["heldout_readout_error"] < 1e-9
    assert reconstructed.metadata["raw_outcomes_included"] is True
    assert reconstructed.metadata["raw_outcomes_source"] == "analytic_projective_projection"
    assert reconstructed.metadata["tomography_source"] == "ideal_cp_map.apply"
    assert reconstructed.metadata["physical_tomography"] is False
    assert reconstructed.metadata["global_perf_used_in_reconstruction"] is False
    assert reconstructed.metadata["perceval_probe"]["status"] == "SKIPPED"
    report = validate_gate_map(reconstructed)
    assert report.passed
    assert report.choi_consistency_error < 1e-9
    assert success_weighted_haar_fidelity(
        reconstructed, np.diag([1, 1, 1, np.exp(1j * np.pi / 3)])
    ) == pytest.approx(1.0, abs=1e-9)


def test_density_composition_matches_direct_ideal_compiled_reference() -> None:
    compiled = compile_iqp(3, [0.2, -0.1, 0.31], [(0, 2, -0.2), (1, 2, 0.311)], quantize=False)
    observed, success = apply_compiled_density(compiled)
    expected = ideal_iqp_distribution(3, compiled.singles, [(i, j, a.lifted_theta) for (i, j), a in compiled.pair_angles])
    assert _tvd(observed, expected) < 1e-12
    expected_success = ideal_cp_map(0.2 * 4).success * ideal_cp_map(0.311 * 4).success
    assert success == pytest.approx(expected_success, abs=1e-12)


def test_fixed_photon_loss_preserves_conditioned_distribution_and_scales_success() -> None:
    compiled = compile_iqp(3, [0.2, -0.1, 0.31], [(0, 2, 0.311)], quantize=False)
    lossless, success_lossless = apply_compiled_density(compiled, eta=1.0)
    lossy, success_lossy = apply_compiled_density(compiled, eta=0.5)
    assert lossy == pytest.approx(lossless, abs=1e-12)
    assert success_lossy == pytest.approx(success_lossless * 0.5**3, abs=1e-12)
    assert success_lossy == pytest.approx(fixed_photon_accepted_mass(0.5, 3, success_lossless), abs=1e-12)


def test_fixed_photon_loss_rejects_invalid_survival() -> None:
    compiled = compile_iqp(2, [0.1, 0.2], [(0, 1, 0.3)], quantize=False)
    with pytest.raises(ValueError, match="eta"):
        apply_compiled_density(compiled, eta=0.0)


def test_k_zero_is_a_valid_identity_instrument_control() -> None:
    compiled = compile_iqp(3, [0.2, -0.1, 0.31], [])
    observed, success = apply_compiled_density(compiled)
    expected = ideal_iqp_distribution(3, compiled.singles)
    assert _tvd(observed, expected) < 1e-12
    assert success == pytest.approx(1.0, abs=1e-12)


def test_quantized_compiled_distribution_is_compared_to_compiled_not_raw() -> None:
    compiled = compile_iqp(2, [0.3, 0.7], [(0, 1, 0.311)], quantize=True)
    observed, success = apply_compiled_density(compiled)
    expected = ideal_iqp_distribution(2, compiled.singles, [(0, 1, compiled.pair_angles[0][1].lifted_theta)])
    raw = ideal_iqp_distribution(2, compiled.singles, [(0, 1, 0.311)])
    assert _tvd(observed, expected) < 1e-12
    assert _tvd(observed, raw) > 1e-5
    assert success == pytest.approx(ideal_cp_map(1.2).success, abs=1e-12)


def test_composition_tracks_unnormalized_model_success() -> None:
    rho = np.diag([1.0, 0.0, 0.0, 0.0]).astype(complex)
    normalized, success = compose_instruments(2, rho, [((0, 1), ideal_cp_map(np.pi))])
    assert success == pytest.approx(1 / 9, abs=1e-12)
    assert np.trace(normalized) == pytest.approx(1.0, abs=1e-12)


def _asymmetric_x_on_local_msb() -> GateMap:
    x = np.array([[0, 1], [1, 0]], complex)
    operator = np.kron(x, np.eye(2))
    return GateMap(4, 1.0, _choi_from_kraus((operator,)), "asymmetric-test", kraus=(operator,))


@pytest.mark.parametrize(
    ("qubits", "expected"),
    [
        ((0, 1), "100"),
        ((1, 2), "010"),
        ((0, 2), "100"),
        ((2, 0), "001"),
    ],
)
def test_density_composition_preserves_declared_local_msb_order(
    qubits: tuple[int, int], expected: str
) -> None:
    state = np.zeros((8, 8), complex)
    state[0, 0] = 1.0
    observed, success = compose_instruments(3, state, [(qubits, _asymmetric_x_on_local_msb())])
    assert success == pytest.approx(1.0)
    assert format(int(np.argmax(np.real(np.diag(observed)))), "03b") == expected


def test_density_composition_preserves_order_on_entangled_nonadjacent_input() -> None:
    state_vector = np.zeros(8, complex)
    state_vector[0] = 1.0 / np.sqrt(2.0)
    state_vector[7] = 1.0 / np.sqrt(2.0)
    state = np.outer(state_vector, state_vector.conj())
    observed, success = compose_instruments(3, state, [((0, 2), _asymmetric_x_on_local_msb())])
    expected_vector = np.zeros(8, complex)
    expected_vector[3] = 1.0 / np.sqrt(2.0)
    expected_vector[4] = 1.0 / np.sqrt(2.0)
    expected = np.outer(expected_vector, expected_vector.conj())
    assert success == pytest.approx(1.0)
    assert observed == pytest.approx(expected, abs=1e-12)


def test_physicality_rejects_inconsistent_supplied_choi() -> None:
    transpose = np.zeros((4, 4))
    for i in range(2):
        for j in range(2):
            transpose[j + 2 * i, i + 2 * j] = 1
    inconsistent = GateMap(2, 1.0, np.eye(4), "inconsistent-test", superoperator=transpose)
    report = validate_gate_map(inconsistent)
    assert report.passed is False
    assert report.choi_consistency_error > 1e-9


def test_capability_failures_are_explicit() -> None:
    with pytest.raises(ValueError, match="weight 3"):
        compile_generators(np.array([[1, 1, 1]], dtype=np.uint8), [0.1])
    with pytest.raises(ValueError, match="cycle"):
        compile_iqp(4, [0.0] * 4, [(0, 2, 0.1)], topology="cycle")
    result = full_fock_cp_reference(2, 0, 1, [0.0, 0.0], np.pi / 3, g2=0.025)
    assert result.status == "INCONCLUSIVE"
    assert "D1" in result.diagnostics["reason"]


def test_fixed_photon_fock_loss_scales_acceptance_without_changing_conditioned_q() -> None:
    lossless = full_fock_cp_reference(2, 0, 1, [0.2, 0.3], np.pi / 3, eta=1.0)
    lossy = full_fock_cp_reference(2, 0, 1, [0.2, 0.3], np.pi / 3, eta=0.5)
    if lossless.status == "INCONCLUSIVE" or lossy.status == "INCONCLUSIVE":
        pytest.skip("optional Perceval full-Fock result unavailable for one loss setting")
    assert lossless.status == lossy.status == "PASS"
    assert lossy.distribution == pytest.approx(lossless.distribution, abs=1e-12)
    assert lossy.accepted_mass == pytest.approx(lossless.accepted_mass * 0.5**2, abs=1e-12)
    assert lossy.rejected_mass == pytest.approx(1.0 - lossy.accepted_mass, abs=1e-12)


def test_direct_no_gate_zero_angle_identity_and_bit_order() -> None:
    result = direct_fock_cp_reference(2, [0.0, 0.0], [])
    if result.status == "INCONCLUSIVE":
        pytest.skip(result.diagnostics.get("reason", "Perceval unavailable"))
    assert result.distribution == pytest.approx({"00": 1.0}, abs=1e-12)
    assert result.diagnostics["source_once"] is True
    assert result.diagnostics["source_input_photons"] == 2


def test_direct_no_gate_single_angle_matches_independent_reference() -> None:
    result = direct_fock_cp_reference(1, [0.2], [])
    if result.status == "INCONCLUSIVE":
        pytest.skip(result.diagnostics.get("reason", "Perceval unavailable"))
    reference = ideal_iqp_distribution(1, [0.2])
    assert result.distribution == pytest.approx(reference, abs=1e-12)


def test_direct_intermediate_projection_tracks_absolute_acceptance() -> None:
    pairs = [(0, 1, 0.20), (1, 2, 0.30)]
    final = direct_fock_cp_reference(3, [0.17, -0.24, 0.36], pairs, projection="final_only")
    intermediate = direct_fock_cp_reference(3, [0.17, -0.24, 0.36], pairs, projection="intermediate")
    if final.status == "INCONCLUSIVE" or intermediate.status == "INCONCLUSIVE":
        pytest.skip(final.diagnostics.get("reason") or intermediate.diagnostics.get("reason", "Perceval unavailable"))
    assert final.status == intermediate.status == "PASS"
    assert final.diagnostics["projection"] == "final_only"
    assert intermediate.diagnostics["projection"] == "intermediate"
    assert intermediate.diagnostics["raw_source_acceptance"] <= 1.0 + 1e-12
    assert intermediate.accepted_mass == pytest.approx(final.accepted_mass, abs=1e-12)
    assert intermediate.diagnostics["raw_source_acceptance"] == pytest.approx(
        final.diagnostics["raw_source_acceptance"], abs=1e-12
    )


def test_physical_control_manifest_records_projection_evidence() -> None:
    manifest_path = Path(__file__).parents[2] / "results" / "v4_tcdp" / "deploy" / "physical_control_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["schema_version"] == "v4_tcdp.physical_controls.v2"
    assert manifest["status"] == "PASS"
    assert [control["id"] for control in manifest["controls"]] == [
        "no_gate_n2",
        "single_gate_bystander_n3",
        "shared_gate_n3",
    ]
    assert [control["status"] for control in manifest["controls"]] == ["PASS", "PASS", "PASS"]
    assert manifest["controls"][1]["conditional_tvd_direct_final_vs_analytic"] <= 1e-12
    assert manifest["controls"][2]["conditional_tvd_direct_final_vs_analytic"] <= 1e-12
    for control in manifest["controls"]:
        assert control["final_only"]["diagnostics"]["projection"] == "final_only"
        assert control["intermediate"]["diagnostics"]["projection"] == "intermediate"
        comparison = control["projection_comparison"]
        assert comparison["valid"] is True
        assert comparison["conditional_distribution_valid"] is True
        assert comparison["absolute_mass_valid"] is True
        assert comparison["eta"] == pytest.approx(control["eta"])
        assert comparison["accepted_mass_delta"] <= 1e-12
    assert manifest["controls"][2]["projection_comparison"]["conditional_tvd_final_vs_intermediate"] > 1e-3


def test_throughput_and_conditional_erasure_conserve_mass() -> None:
    assert fixed_photon_attempts_per_sample(0.5, 2, 0.25) == pytest.approx(16.0)
    assert heralded_cz_attempts_per_sample(1.0, 2, 1) == pytest.approx(27 / 2)
    distribution = conditional_erasure_distribution(
        {"00": 0.25, "01": 0.25, "10": 0.25, "11": 0.25}, 0.5, gate_success=0.8
    )
    assert distribution["FAILURE"] == pytest.approx(0.2)
    assert sum(distribution.values()) == pytest.approx(1.0)


def test_cache_rejects_stale_source_metadata(tmp_path) -> None:
    cache = MapCache(tmp_path)
    key = cache.key(alpha_key=3, raw_alpha=0.31, lifted_alpha=0.31, source={"g2": 0}, noise={"eta": 1}, detector={"kind": "pnr"})
    cache.save_metadata(key, {"source_hash": "fresh"})
    assert cache.load_metadata(key, {"source_hash": "fresh"})["source_hash"] == "fresh"
    with pytest.raises(ValueError, match="stale cache"):
        cache.load_metadata(key, {"source_hash": "stale"})


def test_density_path_does_not_construct_embedded_4n_square_superoperator() -> None:
    source = inspect.getsource(compose_instruments)
    assert "4**n" not in source.replace(" ", "")
    assert "np.eye(4**n" not in source.replace(" ", "")


@pytest.mark.parametrize(("fock_status", "expected"), [("FAIL", "FAIL"), ("INCONCLUSIVE", "INCONCLUSIVE")])
def test_deploy_aggregate_includes_full_fock_status(monkeypatch, fock_status: str, expected: str) -> None:
    def fake_reconstruct(_alpha: float, *, use_perceval: bool) -> GateMap:
        gate = ideal_cp_map(np.pi / 3)
        gate.metadata["perceval"] = {"status": "PASS"}
        gate.metadata["perceval_probe"] = {"status": "PASS"}
        return gate

    monkeypatch.setattr(validate_deploy, "reconstruct_cp_map", fake_reconstruct)
    monkeypatch.setattr(
        validate_deploy,
        "full_fock_cp_reference",
        lambda *_args, **_kwargs: FullFockResult(fock_status, diagnostics={"injected": True}),
    )
    result = validate_deploy.run(with_perceval=True)
    assert result["physical_status"] == "INCONCLUSIVE"
    assert result["perceval_probe_status"] == "PASS"
    assert result["full_fock"]["status"] == fock_status
    assert result["status"] == expected
