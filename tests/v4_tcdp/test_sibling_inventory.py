from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import numpy as np
import pytest

from merlin_iqp.experiments.sibling_import import (
    COMPATIBILITY_STATUSES,
    build_sibling_inventory,
    compatibility_record,
    regenerate_training_smoke_data,
    safe_import_artifact,
    write_inventory_outputs,
)

REPO_ROOT = Path(__file__).resolve().parents[2]
SIBLING_ROOT = Path(r"C:\Users\cuqui\iqp-mmd-barren-plateau")
INVENTORY_PATH = REPO_ROOT / "results" / "v4_tcdp" / "sibling_inventory.json"


def test_inventory_schema_and_two_packages() -> None:
    assert INVENTORY_PATH.exists()
    inventory = json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))
    assert inventory["schema_version"] == "v4_tcdp.sibling_inventory.v1"
    assert set(inventory["packages"]) == {"iqp_bp", "iqp_mmd"}
    assert inventory["source"]["pinned_commit"] == "f6d6ebe87e4ee1de10893c6ea2f0ffa367493336"
    assert inventory["summary"]["source_file_count"] > 0
    assert inventory["summary"]["artifact_count"] > 0
    assert all(row["disposition"] in COMPATIBILITY_STATUSES for row in inventory["source_rows"])
    assert all(record["sha256"] for record in inventory["artifacts"])


def test_classical_import_has_no_sibling_dependency() -> None:
    classical_root = REPO_ROOT / "src" / "merlin_iqp" / "classical"
    source_text = "\n".join(path.read_text(encoding="utf-8") for path in classical_root.glob("*.py"))
    assert "iqp_bp" not in source_text
    assert "iqp_mmd" not in source_text
    probe = subprocess.run(
        [sys.executable, "-c", "import sys; import merlin_iqp.classical; print('\\n'.join(sys.path))"],
        cwd=REPO_ROOT,
        check=True,
        capture_output=True,
        text=True,
        env={"PYTHONPATH": str(REPO_ROOT / "src")},
    )
    assert str(SIBLING_ROOT) not in probe.stdout


def test_missing_artifact_is_blocked_without_substitution(tmp_path: Path) -> None:
    missing = tmp_path / "missing" / "train.npy"
    row = compatibility_record(
        "fixture:missing-data",
        required_paths=[missing],
        status="exact_reproduction",
        reason="fixture requested exact replay",
    )
    assert row["status"] == "blocked"
    assert "missing:" in row["evidence"][0]
    assert "substitute" not in row["reason"] or "no substitute" in row["reason"]


def test_safe_artifact_boundary_rejects_pickle_and_reads_npz(tmp_path: Path) -> None:
    pickle_path = tmp_path / "foreign.pkl"
    pickle_path.write_bytes(b"not loaded")
    with pytest.raises(ValueError, match="unsafe serialized"):
        safe_import_artifact(pickle_path)
    npz_path = tmp_path / "checkpoint.npz"
    np.savez(npz_path, G=np.eye(2, dtype=np.uint8), theta=np.zeros(2))
    metadata = safe_import_artifact(npz_path)
    assert metadata["keys"] == ["G", "theta"]
    assert metadata["arrays"]["G"]["dtype"] == "uint8"


@pytest.mark.skipif(not SIBLING_ROOT.exists(), reason="local sibling checkout is unavailable")
def test_inventory_does_not_mutate_sibling(tmp_path: Path) -> None:
    before_status = subprocess.run(
        ["git", "-C", str(SIBLING_ROOT), "status", "--short"], check=True, capture_output=True, text=True
    ).stdout
    before_head = subprocess.run(
        ["git", "-C", str(SIBLING_ROOT), "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()
    inventory = build_sibling_inventory(SIBLING_ROOT)
    after_status = subprocess.run(
        ["git", "-C", str(SIBLING_ROOT), "status", "--short"], check=True, capture_output=True, text=True
    ).stdout
    after_head = subprocess.run(
        ["git", "-C", str(SIBLING_ROOT), "rev-parse", "HEAD"], check=True, capture_output=True, text=True
    ).stdout.strip()
    assert inventory["source"]["observed_head"] == before_head
    assert inventory["source"]["observed_commit"] == before_head
    assert inventory["source"]["observed_branch"]
    assert inventory["source"]["observed_tree_identity"]
    assert inventory["source"]["pin_status"] == "MATCH"
    outputs = write_inventory_outputs(inventory, tmp_path / "exports")
    exported = json.loads(outputs["training_smoke_configs_experiments_training_smoke_yaml"].read_text(encoding="utf-8"))
    assert exported["source_commit"] == before_head
    assert exported["source_branch"]
    assert exported["source_tree_identity"] == inventory["source"]["observed_tree_identity"]
    assert exported["source_pin_status"] == "MATCH"
    assert (before_status, before_head) == (after_status, after_head)


@pytest.mark.skipif(not SIBLING_ROOT.exists(), reason="local sibling checkout is unavailable")
def test_training_smoke_data_is_regenerated_from_recorded_recipe() -> None:
    data, provenance = regenerate_training_smoke_data(SIBLING_ROOT)
    assert data.shape == (256, 6)
    assert data.dtype == np.uint8
    assert provenance["seed"] == 1230519654
    assert provenance["faithful_retraining"] == "not_run"
    assert provenance["sha256"] == "dd03528a153d041bcd670204a91a2e3cfebcbbce32bad2b5fe9ab93b33bb2c53"
