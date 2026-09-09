"""Acceptance tests for the additive Phase 28 two-ring pipeline."""

from __future__ import annotations

import builtins
import json
from dataclasses import replace

import numpy as np
import pytest

from merlin_iqp.classical import target_moments
from merlin_iqp.classical._validation import hash_array
from merlin_iqp.experiments.datasets import load_rings_dataset, make_grid_codec
from merlin_iqp.experiments.rings import (
    SOURCE_COMMIT_RULE,
    _resolve_source_commit,
    classical_only_import_guard,
    resolve_config,
    train_rings,
    write_run_artifacts,
)


def test_dataset_reproduces_frozen_split_transform_and_hashes() -> None:
    first = load_rings_dataset(4)
    second = load_rings_dataset(4)
    assert first.dataset_hash == second.dataset_hash == "2a021db64ff4ce325765025da21cf8b6754a61648dbfa87050ee3853b4c949ae"
    assert len(first.train_ids) == 320
    assert len(first.test_ids) == 80
    assert set(first.train_ids).isdisjoint(first.test_ids)
    assert first.train_ids.min() >= 0 and first.test_ids.max() < 400
    assert first.normalized_train.dtype == np.float32
    assert np.array_equal(first.min_values, first.raw_train.min(axis=0))
    assert np.array_equal(first.max_values, first.raw_train.max(axis=0))
    assert first.manifest()["train_ids_hash"] == "4849214aeb5c229401eec2978f02df43b39f16eea071c3ccdb9a36237c849d68"
    assert first.manifest()["test_ids_hash"] == "03035d60e5a837eb8ece20a277838a5fc0153ff72079d195e18ef5fb9390acc6"
    assert first.manifest()["normalized_train_hash"] == "585649e3d7e6497a35fa8888d35efb956e68b9de9851ad2c9239416c47baff38"
    assert first.manifest()["normalized_test_hash"] == "52bf7f9fcd0f41331e367ec42e16620fafd709b79c69018daa9050ddfd3371ed"
    assert np.isclose(first.train_histogram.sum(), 1.0)
    assert np.isclose(first.test_histogram.sum(), 1.0)


def test_codec_is_row_major_msb_and_handles_edges_outside_and_ties() -> None:
    codec = make_grid_codec(2)
    assert [codec.bitstring(i) for i in range(4)] == ["00", "01", "10", "11"]
    assert codec.index("10") == 2
    assert np.array_equal(codec.encode(codec.centers), np.arange(4))
    points = np.asarray([[-0.1, -0.1], [1.1, 1.1], [-10.0, 5.0], [-0.1, 0.5]])
    assert np.array_equal(codec.encode(points), np.asarray([0, 3, 1, 0]))
    assert np.array_equal(codec.decode([0, 3]), codec.centers[[0, 3]])
    assert codec.manifest()["tie_breaking"] == "lowest_row_major_index"
    with pytest.raises(ValueError):
        codec.index("2")
    with pytest.raises(ValueError):
        codec.decode([4])


def test_classical_only_guard_blocks_backend_imports_and_restores_importer() -> None:
    original = builtins.__import__
    with classical_only_import_guard():
        with pytest.raises(RuntimeError, match="forbidden import"):
            builtins.__import__("torch")
    assert builtins.__import__ is original


@pytest.mark.parametrize("profile", ["rings_spatial_exact", "rings_hamming"])
def test_both_objective_profiles_train_with_shared_iqp_model(profile: str) -> None:
    config = resolve_config(profile, n=4, seed=0, steps=1)
    run = train_rings(config)
    assert run.generator.shape == (7, 4)
    assert len(run.loss_history) == 2
    assert np.isclose(run.output_probabilities.sum(), 1.0)
    assert all(np.isfinite(value) for value in run.metrics.values())
    assert run.photonic_evaluation["status"] == "INCONCLUSIVE"
    assert config.profile_id == profile
    assert config.initialization == "data_dependent"
    assert config.initialization_method == "parity"
    assert config.initialization_scale == 0.1
    assert run.source_provenance["observed_commit"]
    assert run.config.source_commit == run.source_provenance["observed_commit"]
    assert run.source_provenance["commit_resolution"] == "observed_current_commit"
    assert run.source_provenance["commit_matches_observed"] is True


def test_explicit_historical_source_commit_is_preserved_and_not_silently_rewritten() -> None:
    resolved, rule = _resolve_source_commit("72e8079", "current-commit")
    assert resolved == "72e8079"
    assert rule == "explicit_configured_commit"

    config = replace(
        resolve_config("rings_hamming", n=4, seed=0, steps=0),
        source_commit="72e8079",
    )
    run = train_rings(config)
    assert run.config.source_commit == "72e8079"
    assert run.source_provenance["configured_commit"] == "72e8079"
    assert run.source_provenance["resolved_commit"] == "72e8079"
    assert run.source_provenance["commit_matches_observed"] is False
    assert run.source_provenance["commit_rule"] == SOURCE_COMMIT_RULE


def test_default_data_dependent_initialization_uses_exact_train_moments_and_scale() -> None:
    dataset = load_rings_dataset(4)
    first = train_rings(resolve_config("rings_spatial_exact", n=4, seed=0, steps=0))
    second = train_rings(resolve_config("rings_spatial_exact", n=4, seed=99, steps=0))
    assert first.initialization_metadata["scheme"] == "data_dependent"
    assert first.initialization_metadata["method"] == "parity"
    assert first.initialization_metadata["scale"] == 0.1
    assert first.initialization_metadata["target_split"] == "train"
    assert first.initialization_metadata["target_dataset_hash"] == dataset.dataset_hash
    assert first.initialization_metadata["target_representation"] == "exact_probabilities"
    moments = target_moments(dataset.train_target, first.generator)
    assert first.initialization_metadata["target_moments_hash"] == hash_array(moments.values)
    assert np.allclose(first.initial_theta, 0.1 * moments.values)
    assert np.array_equal(first.initial_theta, second.initial_theta)
    assert first.initialization_metadata["parameter_hash"] == second.initialization_metadata["parameter_hash"]


@pytest.mark.parametrize("scheme", ["small_angle", "uniform"])
def test_initialization_ablations_are_explicitly_selectable(scheme: str) -> None:
    config = resolve_config("rings_hamming", n=4, seed=3, steps=0, initialization=scheme)
    run = train_rings(config)
    assert run.config.initialization == scheme
    assert run.initialization_metadata["scheme"] == scheme
    assert run.initialization_metadata["seed"] == 3
    assert run.initialization_metadata["scale"] == 0.1
    assert run.initialization_metadata["randomness_source"] == "numpy.default_rng(seed)"


def test_artifact_schema_contains_dataset_codec_diagnostics_and_context(tmp_path) -> None:
    run = train_rings(resolve_config("rings_hamming", n=4, seed=1, steps=1))
    paths = write_run_artifacts(run, tmp_path)
    assert set(paths) == {"dataset", "run", "manifest", "summary"}
    manifest = json.loads(paths["manifest"].read_text(encoding="utf-8"))
    assert manifest["schema_version"] == "v4_tcdp.rings_run.v2"
    assert manifest["dataset"]["codec"]["index_order"] == "row_major"
    assert manifest["dataset"]["codec"]["mapping"][0]["bitstring"] == "0000"
    assert "train_counts" in manifest["dataset"]["histograms"]
    assert "quantization" in manifest["dataset"]
    assert manifest["legacy_v1_context"]["output_bins"] == 462
    assert manifest["photonic_evaluation"]["status"] == "INCONCLUSIVE"
    assert manifest["initialization"]["method"] == "parity"
    assert manifest["initialization"]["scale"] == 0.1
    assert manifest["initialization"]["seed"] == 1
    assert manifest["initialization"]["parameter_hash"] == manifest["model"]["initial_theta_hash"]
    assert manifest["replication_identity"]["replica_id"] == "rings_hamming/n4_seed1_smoke"
    assert manifest["replication_identity"]["n_unique_parameterizations_observed"] == 1
    with np.load(paths["run"], allow_pickle=False) as archive:
        assert archive["decoded_centers"].shape == (16, 2)
        assert archive["output_probabilities"].shape == (16,)


def test_duplicate_deterministic_data_dependent_replicas_are_labeled(tmp_path) -> None:
    first = train_rings(resolve_config("rings_spatial_exact", n=4, seed=0, steps=0))
    second = train_rings(resolve_config("rings_spatial_exact", n=4, seed=1, steps=0))
    write_run_artifacts(first, tmp_path)
    second_paths = write_run_artifacts(second, tmp_path)
    manifest = json.loads(second_paths["manifest"].read_text(encoding="utf-8"))
    identity = manifest["replication_identity"]
    assert identity["status"] == "duplicate_deterministic"
    assert identity["independent_replica"] is False
    assert identity["duplicate_of"] == "rings_spatial_exact/n4_seed0_smoke"
    assert identity["n_unique_parameterizations_observed"] == 1


def test_idempotent_ring_rewrite_survives_another_seed(tmp_path) -> None:
    first = train_rings(resolve_config("rings_hamming", n=4, seed=0, steps=0))
    second = train_rings(resolve_config("rings_hamming", n=4, seed=1, steps=0))
    first_paths = write_run_artifacts(first, tmp_path)
    write_run_artifacts(second, tmp_path)
    assert write_run_artifacts(first, tmp_path) == first_paths


def test_idempotent_ring_rewrite_rejects_missing_promised_artifact(tmp_path) -> None:
    run = train_rings(resolve_config("rings_hamming", n=4, seed=0, steps=0))
    paths = write_run_artifacts(run, tmp_path)
    paths["run"].unlink()
    with pytest.raises(FileExistsError, match="missing"):
        write_run_artifacts(run, tmp_path)


def test_idempotent_ring_rewrite_rejects_corrupt_promised_artifact(tmp_path) -> None:
    run = train_rings(resolve_config("rings_hamming", n=4, seed=0, steps=0))
    paths = write_run_artifacts(run, tmp_path)
    with np.load(paths["run"], allow_pickle=False) as archive:
        arrays = {name: archive[name] for name in archive.files}
    arrays["final_theta"][0] += 1.0
    np.savez_compressed(paths["run"], **arrays)
    with pytest.raises(FileExistsError, match="integrity validation"):
        write_run_artifacts(run, tmp_path)


def test_idempotent_ring_rewrite_rejects_corrupt_summary(tmp_path) -> None:
    run = train_rings(resolve_config("rings_hamming", n=4, seed=0, steps=0))
    paths = write_run_artifacts(run, tmp_path)
    summary = json.loads(paths["summary"].read_text(encoding="utf-8"))
    summary["metrics"] = {"tvd_train": -999.0}
    summary["photonic_evaluation"] = {"status": "PASS"}
    paths["summary"].write_text(json.dumps(summary), encoding="utf-8")
    with pytest.raises(FileExistsError, match="integrity validation"):
        write_run_artifacts(run, tmp_path)


def test_ring_artifacts_namespace_initialization_and_step_ablations(tmp_path) -> None:
    primary = train_rings(resolve_config("rings_hamming", n=4, seed=0, steps=0, main=True))
    uniform = train_rings(resolve_config("rings_hamming", n=4, seed=0, steps=0, main=True, initialization="uniform"))
    longer = train_rings(resolve_config("rings_hamming", n=4, seed=0, steps=1, main=True))
    primary_path = write_run_artifacts(primary, tmp_path)["run"]
    uniform_path = write_run_artifacts(uniform, tmp_path)["run"]
    longer_path = write_run_artifacts(longer, tmp_path)["run"]
    assert primary_path != uniform_path
    assert primary_path != longer_path
    assert primary_path.parent != uniform_path.parent
    assert primary_path.parent != longer_path.parent


def test_legacy_grid_shapes_remain_contextually_unchanged() -> None:
    from merlin_iqp.generator.bin_centers import make_bin_centers
    from merlin_iqp.generator.natural_grid import make_natural_bin_centers

    assert tuple(make_bin_centers().shape) == (400, 2)
    assert tuple(make_natural_bin_centers().shape) == (462, 2)
