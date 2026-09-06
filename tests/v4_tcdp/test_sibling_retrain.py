from pathlib import Path

from scripts.v4_tcdp.retrain_sibling import run_retraining


def test_training_smoke_source_retraining_matches_frozen_trajectory(tmp_path: Path) -> None:
    report = run_retraining(
        Path(r"C:\Users\cuqui\iqp-mmd-barren-plateau\configs\experiments\training_smoke.yaml"),
        Path(r"C:\Users\cuqui\iqp-mmd-barren-plateau"),
        tmp_path / "training_smoke",
    )
    assert report["status"] == "PASS"
    assert report["trajectory_rows"] == 5
    assert report["max_theta_abs_error"] == 0.0
    assert report["max_loss_abs_error"] == 0.0
