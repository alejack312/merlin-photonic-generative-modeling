import os
import importlib
from pathlib import Path

import pytest

import scripts.v4_tcdp.retrain_sibling as retrain_sibling
from scripts.v4_tcdp.retrain_sibling import _compare_trajectories, run_retraining


def test_training_smoke_source_retraining_matches_frozen_trajectory(tmp_path: Path) -> None:
    sibling_root_value = os.environ.get("MERLIN_SIBLING_ROOT")
    if not sibling_root_value:
        pytest.skip("optional sibling integration; set MERLIN_SIBLING_ROOT to run")
    sibling_root = Path(sibling_root_value).resolve()
    config = sibling_root / "configs" / "experiments" / "training_smoke.yaml"
    if not config.is_file():
        pytest.skip(f"optional sibling integration input unavailable: {config}")
    report = run_retraining(
        config,
        sibling_root,
        tmp_path / "training_smoke",
    )
    assert report["status"] == "PASS"
    assert report["trajectory_rows"] == 5
    assert report["max_theta_abs_error"] == 0.0
    assert report["max_loss_abs_error"] == 0.0


def _rows(*, theta: object = [0.1, 0.2], loss: float = 0.5, steps: tuple[int, ...] = (0, 1)) -> list[dict[str, object]]:
    return [{"step": step, "theta": theta, "loss": loss} for step in steps]


@pytest.mark.parametrize(
    "bad_rows",
    [
        [],
        _rows(theta=[float("nan"), 0.2]),
        _rows(loss=float("inf")),
        _rows(steps=(0, 2)),
        _rows(theta=[0.1]),
    ],
)
def test_retraining_rejects_invalid_trajectory_evidence(bad_rows: list[dict[str, object]]) -> None:
    with pytest.raises(ValueError):
        _compare_trajectories(
            _rows(),
            bad_rows,
            expected_step_ids=(0, 1),
            expected_theta_shape=(2,),
        )


def test_retraining_finite_mismatch_is_fail_not_inconclusive() -> None:
    result = _compare_trajectories(
        _rows(),
        _rows(loss=0.6),
        expected_step_ids=(0, 1),
        expected_theta_shape=(2,),
    )
    assert result["status"] == "FAIL"


def test_retraining_contract_rejects_a_non_source_checkout(tmp_path: Path) -> None:
    with pytest.raises((FileNotFoundError, ValueError), match="source|manifest|config"):
        run_retraining(tmp_path / "different.yaml", tmp_path / "fake-sibling", tmp_path / "out")


def test_source_import_fails_explicitly_when_pyyaml_is_missing(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    sibling_root = tmp_path / "sibling"
    (sibling_root / "src").mkdir(parents=True)
    real_import = importlib.import_module

    def missing_yaml(name: str, *args: object, **kwargs: object) -> object:
        if name == "yaml":
            raise ModuleNotFoundError("yaml")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(retrain_sibling.importlib, "import_module", missing_yaml)
    with pytest.raises(RuntimeError, match="real PyYAML|yaml stub"):
        with retrain_sibling._isolated_source_import(sibling_root):
            pass


def test_source_import_uses_real_yaml_and_does_not_silently_accept_malformed_yaml(
    tmp_path: Path,
) -> None:
    sibling_root = tmp_path / "sibling"
    (sibling_root / "src").mkdir(parents=True)
    with retrain_sibling._isolated_source_import(sibling_root):
        yaml = importlib.import_module("yaml")
        with pytest.raises(yaml.YAMLError):
            yaml.safe_load("broken: [")
