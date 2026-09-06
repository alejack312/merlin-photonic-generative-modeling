"""Portable unit coverage for the optional sibling retraining boundary."""

from __future__ import annotations

from pathlib import Path

import pytest

from scripts.v4_tcdp.retrain_sibling import _compare_trajectories, _require_outside_sibling


def _rows() -> list[dict[str, object]]:
    return [
        {"step": 0, "theta": [0.1, 0.2], "loss": 0.5},
        {"step": 1, "theta": [0.2, 0.3], "loss": 0.4},
    ]


def test_trajectory_contract_is_self_contained() -> None:
    result = _compare_trajectories(
        _rows(), _rows(), expected_step_ids=(0, 1), expected_theta_shape=(2,)
    )
    assert result["status"] == "PASS"
    assert result["trajectory_rows"] == 2


def test_output_inside_sibling_is_rejected_without_a_checkout() -> None:
    sibling = Path("C:/temporary-sibling")
    with pytest.raises(ValueError, match="outside sibling"):
        _require_outside_sibling(sibling / "results", sibling)
