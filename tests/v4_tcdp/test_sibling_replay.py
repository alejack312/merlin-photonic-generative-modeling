import json
from pathlib import Path
import subprocess

import numpy as np
import pytest

from scripts.v4_tcdp.replay_sibling import replay_export


def _make_source_fixture(root: Path) -> tuple[Path, Path]:
    (root / "src" / "iqp_bp").mkdir(parents=True)
    (root / "src" / "iqp_bp" / "model.py").write_text("x = 1\n", encoding="utf-8")
    subprocess.run(["git", "-C", str(root), "init"], check=True, capture_output=True, text=True)
    subprocess.run(["git", "-C", str(root), "add", "."], check=True, capture_output=True, text=True)
    subprocess.run(
        ["git", "-C", str(root), "-c", "user.name=Audit", "-c", "user.email=audit@example.invalid", "commit", "-m", "fixture"],
        check=True,
        capture_output=True,
        text=True,
    )
    checkpoint = root / "results" / "step_0001.npz"
    checkpoint.parent.mkdir()
    identity = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()
    manifest = root / "export.json"
    manifest.write_text(
        json.dumps(
            {
                "schema_version": "v4_tcdp.sibling_export_manifest.v1",
                "copy_performed": False,
                "source_id": "probe:config",
                "source_commit": identity,
                "source_tree_identity": subprocess.run(
                    ["git", "-C", str(root), "rev-parse", "HEAD^{tree}"], check=True, capture_output=True, text=True
                ).stdout.strip(),
                "requested_pinned_commit": identity,
                "result_evidence": ["results/step_0001.npz"],
                "config": {"content": {"kernel": {"type": "gaussian", "bandwidth": [1.0]}}},
            }
        ),
        encoding="utf-8",
    )
    return checkpoint, manifest


def test_replay_rejects_malformed_generator_and_nonfinite_loss(tmp_path: Path) -> None:
    source = tmp_path / "source"
    checkpoint, manifest = _make_source_fixture(source)
    np.savez(checkpoint, G=np.array([[1.0, 0.0], [0.0, 1.0], [1.5, 1.0]]), theta=np.array([0.1, 0.2, 0.3]), step=np.array(1), loss=np.array(0.5))
    with pytest.raises(ValueError, match="source generator"):
        replay_export(manifest, source, tmp_path / "replayed")
    np.savez(checkpoint, G=np.array([[1, 0], [0, 1]], dtype=np.uint8), theta=np.array([0.1, 0.2]), step=np.array(1), loss=np.array(float("nan")))
    with pytest.raises(ValueError, match="checkpoint loss must be finite"):
        replay_export(manifest, source, tmp_path / "replayed")


def test_training_smoke_checkpoint_replay_is_safe_and_explicit(tmp_path: Path) -> None:
    result = replay_export(
        Path("results/v4_tcdp/sibling/training_smoke_configs_experiments_training_smoke_yaml/manifest.json"),
        Path(r"C:\Users\cuqui\iqp-mmd-barren-plateau"),
        tmp_path,
    )
    assert result["status"] == "adapted_reproduction"
    assert result["unsafe_serialization_loaded"] is False
    assert result["raw_compiled_tvd"] < 1e-12
    assert result["deployed_acceptance_mass"] == pytest.approx(1.0)
    raw = np.load(Path(result["namespace"]["destination"]) / "raw.npy", allow_pickle=False)
    assert raw.shape == (64,)
    assert np.isclose(raw.sum(), 1.0)
    assert result["dataset_regeneration"]["status"] == "regenerated"
    assert result["faithful_retraining"]["status"] == "not_run"
    assert Path(result["namespace"]["destination"]) != tmp_path / "training_smoke" / "step_0004"


def test_replay_namespaces_same_step_by_source_identity(tmp_path: Path) -> None:
    source_manifest = Path("results/v4_tcdp/sibling/training_smoke_configs_experiments_training_smoke_yaml/manifest.json")
    first_manifest = tmp_path / "first.json"
    second_manifest = tmp_path / "second.json"
    value = json.loads(source_manifest.read_text(encoding="utf-8"))
    first_manifest.write_text(json.dumps(value), encoding="utf-8")
    altered = dict(value)
    altered["source_id"] = "training_smoke:alternate-source-config.yaml"
    second_manifest.write_text(json.dumps(altered), encoding="utf-8")

    first = replay_export(first_manifest, Path(r"C:\Users\cuqui\iqp-mmd-barren-plateau"), tmp_path / "replays")
    second = replay_export(second_manifest, Path(r"C:\Users\cuqui\iqp-mmd-barren-plateau"), tmp_path / "replays")
    first_destination = Path(first["namespace"]["destination"])
    second_destination = Path(second["namespace"]["destination"])
    assert first_destination != second_destination
    assert (first_destination / "raw.npy").exists()
    assert (second_destination / "raw.npy").exists()


def test_replay_rejects_accidental_same_identity_overwrite(tmp_path: Path) -> None:
    manifest = Path("results/v4_tcdp/sibling/training_smoke_configs_experiments_training_smoke_yaml/manifest.json")
    sibling = Path(r"C:\Users\cuqui\iqp-mmd-barren-plateau")
    output = tmp_path / "replays"
    replay_export(manifest, sibling, output)
    with pytest.raises(FileExistsError, match="already contains"):
        replay_export(manifest, sibling, output)
