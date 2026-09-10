"""Focused tests for the bounded frozen-ring photonic adapter."""

from __future__ import annotations

from pathlib import Path
from dataclasses import replace

import pytest

from merlin_iqp.deploy.ring import evaluate_ring_artifact, load_ring_artifact
import merlin_iqp.deploy.ring as ring_module
from merlin_iqp.classical._validation import hash_json


RING_ROOT = Path("results/v4_tcdp/rings/rings_spatial_exact/n4_seed0_smoke")


def test_load_ring_artifact_verifies_n4_config_source_and_hashes() -> None:
    artifact = load_ring_artifact(RING_ROOT)
    assert artifact.manifest["config"]["n"] == 4
    assert artifact.manifest["config"]["run_kind"] == "smoke"
    assert artifact.manifest["config"]["source_commit"]
    assert artifact.manifest["dataset"]["codec"]["bit_order"] == "msb_first"
    assert artifact.hashes["generator"] == artifact.manifest["model"]["generator_hash"]
    assert artifact.hashes["final_theta"] == artifact.manifest["model"]["final_theta_hash"]


def test_evaluate_ring_artifact_uses_final_only_and_fixed_photon_eta() -> None:
    artifact = load_ring_artifact(RING_ROOT)
    result = evaluate_ring_artifact(artifact, eta=0.9)
    assert result["status"] == "PASS"
    assert result["projection"] == "final_only"
    assert result["source_model"] == "fixed_photon_g2_0"
    assert result["source_once"] is True
    assert result["direct"]["status"] == "PASS"
    assert len(result["direct"]["decoded_conditional_vector"]) == 16
    assert result["direct"]["absolute_accepted_mass"] == pytest.approx(
        result["direct"]["diagnostics"]["raw_source_acceptance"] * 0.9**4,
        abs=1e-12,
    )
    assert result["comparison"]["direct_vs_compiled_qubit_tvd"] <= 1e-12
    assert result["comparison"]["final_only_selected_boundary"] is True
    assert result["hashes"]["generator"] == artifact.hashes["generator"]
    assert result["hashes"]["final_theta"] == artifact.hashes["final_theta"]


def test_ring_evaluation_rejects_zero_acceptance_even_when_shape_matches(monkeypatch) -> None:
    artifact = load_ring_artifact(RING_ROOT)
    original = ring_module.direct_fock_compiled_distribution

    def zero_acceptance(compiled, *, eta: float, projection: str):
        result = original(compiled, eta=eta, projection=projection)
        return replace(result, accepted_mass=0.0, rejected_mass=1.0)

    monkeypatch.setattr(ring_module, "direct_fock_compiled_distribution", zero_acceptance)
    result = evaluate_ring_artifact(artifact, eta=0.9)
    assert result["status"] == "FAIL"
    assert result["comparison"]["acceptance"]["status"] == "FAIL"
    assert result["comparison"]["acceptance"]["field_consistency"] is False


def test_ring_payload_hash_is_recomputable_without_self_reference() -> None:
    result = evaluate_ring_artifact(load_ring_artifact(RING_ROOT), eta=0.9)
    payload = dict(result)
    hashes = dict(result["hashes"])
    declared = hashes.pop("output_payload")
    payload["hashes"] = hashes | {"output_payload": None}
    assert declared == hash_json(payload)
