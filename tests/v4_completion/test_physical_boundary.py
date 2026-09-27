"""Owner-independent ideal n=2/3 full-Fock boundary fixtures."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pytest

from merlin_iqp.deploy import direct_fock_cp_reference, ideal_iqp_distribution


FIXTURES = (
    ("no_gate_n2", 2, [0.0, 0.0], []),
    ("bystander_n3", 3, [0.17, -0.29, 0.31], [(0, 2, 0.30)]),
    ("shared_gate_n3", 3, [0.17, -0.24, 0.36], [(0, 1, 0.20), (1, 2, 0.30)]),
    ("asymmetric_wrap_n3", 3, [-0.31, 0.23, 0.17], [(2, 0, 2.0 * np.pi - 0.47)]),
)


@pytest.mark.parametrize("fixture_id,n,singles,pairs", FIXTURES, ids=[row[0] for row in FIXTURES])
def test_ideal_full_fock_fixture_matches_independent_iqp_reference(
    fixture_id: str,
    n: int,
    singles: list[float],
    pairs: list[tuple[int, int, float]],
) -> None:
    result = direct_fock_cp_reference(n, singles, pairs, eta=1.0, projection="final_only")
    if result.status == "INCONCLUSIVE":
        pytest.skip(f"{fixture_id}: {result.diagnostics.get('reason', 'Perceval unavailable')}")

    assert result.status == "PASS"
    assert result.accepted_mass is not None
    assert result.accepted_mass > 0.0
    assert result.diagnostics["source_once"] is True
    assert result.diagnostics["full_fock_total_mass"] == pytest.approx(1.0, abs=1e-12)
    expected = ideal_iqp_distribution(n, singles, pairs)
    assert {key: result.distribution.get(key, 0.0) for key in expected} == pytest.approx(expected, abs=1e-12)
    assert set(result.distribution) <= set(expected)


def test_existing_physical_control_manifest_is_scope_labeled() -> None:
    path = Path(__file__).parents[2] / "results" / "v4_tcdp" / "deploy" / "physical_control_manifest_20260909_final3.json"
    manifest = json.loads(path.read_text(encoding="utf-8"))

    assert manifest["status"] == "PASS"
    assert manifest["source_model"] == "fixed_photon_g2_0"
    assert [control["id"] for control in manifest["controls"]] == [
        "no_gate_n2",
        "single_gate_bystander_n3",
        "shared_gate_n3",
    ]
    assert all(control["source_once"] is True for control in manifest["controls"])
    assert all(control["projection_comparison"]["general_equivalence"] is False for control in manifest["controls"])
