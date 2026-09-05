from pathlib import Path

import numpy as np
import pytest

from scripts.v4_tcdp.replay_sibling import replay_export


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
    raw = np.load(tmp_path / "training_smoke" / "step_0004" / "raw.npy", allow_pickle=False)
    assert raw.shape == (64,)
    assert np.isclose(raw.sum(), 1.0)
