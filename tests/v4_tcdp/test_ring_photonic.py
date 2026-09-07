"""Focused tests for the bounded frozen-ring photonic adapter."""

from __future__ import annotations

from pathlib import Path

import pytest

from merlin_iqp.deploy.ring import evaluate_ring_artifact, load_ring_artifact


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
