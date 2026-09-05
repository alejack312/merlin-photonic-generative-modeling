"""Regression tests for resumable sweep chunk coverage validation."""

import importlib
import json
from pathlib import Path

import pytest


@pytest.mark.parametrize(
    "module_name",
    [
        "scripts.v3_trainability.gradient_variance_sweep",
        "scripts.v3_trainability.dual_rail_gradient_variance_sweep",
        "scripts.v3_hardness.loss_sweep",
    ],
)
def test_chunk_validation_requires_contiguous_expected_coverage(tmp_path, module_name):
    module = importlib.import_module(module_name)
    for name in ("cell_0-2.npy", "cell_2-4.npy"):
        (tmp_path / name).touch()

    paths = module._validated_chunk_files(str(tmp_path / "*.npy"), expected_draws=4)
    assert [Path(p).name for p in paths] == ["cell_0-2.npy", "cell_2-4.npy"]

    (tmp_path / "cell_5-6.npy").touch()
    with pytest.raises(ValueError, match="gap|coverage"):
        module._validated_chunk_files(str(tmp_path / "*.npy"), expected_draws=6)


@pytest.mark.parametrize(
    "module_name",
    [
        "scripts.v3_trainability.gradient_variance_sweep",
        "scripts.v3_trainability.dual_rail_gradient_variance_sweep",
        "scripts.v3_hardness.loss_sweep",
    ],
)
def test_chunk_validation_rejects_overlap(tmp_path, module_name):
    module = importlib.import_module(module_name)
    (tmp_path / "cell_0-3.npy").touch()
    (tmp_path / "cell_2-4.npy").touch()

    with pytest.raises(ValueError, match="overlapping"):
        module._validated_chunk_files(str(tmp_path / "*.npy"), expected_draws=4)


def test_chunk_validation_rejects_manifest_mismatch(tmp_path):
    from scripts.v3_trainability import gradient_variance_sweep as module

    chunk = tmp_path / "cell_0-2.npy"
    chunk.touch()
    (tmp_path / "cell_0-2.npy.json").write_text(
        json.dumps({"scope": "weight1", "n": 2}), encoding="utf-8"
    )
    with pytest.raises(ValueError, match="configuration mismatch"):
        module._validated_chunk_files(
            str(tmp_path / "*.npy"),
            expected_draws=2,
            expected_config={"scope": "mixed", "n": 2},
        )
