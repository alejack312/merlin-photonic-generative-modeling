"""Owner-requested Ascella brightness correction; all other CSV cells stay fixed."""
from __future__ import annotations

import csv
import math
import os
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
ORIGINAL = ROOT / "results/v4_completion/20261002_first_r1_runs/profiles_measured.csv"
UPDATED = ROOT / "results/v4_completion/20261002_first_r1_runs_brightness/profiles_measured.csv"


def _read(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as stream:
        return list(csv.DictReader(stream))


@pytest.mark.parametrize("index", range(32))
def test_brightness_product_and_other_columns_unchanged(index: int) -> None:
    original = _read(ORIGINAL)[index]
    table = Path(os.environ.get("R1_BRIGHTNESS_TABLE", str(UPDATED)))
    revised = _read(table)[index]
    assert original.keys() == revised.keys()
    for column in original:
        if column != "with_brightness_acceptance":
            assert revised[column] == original[column], column
    if original["profile"].startswith("Ascella"):
        expected = float(original["after_source_acceptance"]) * 0.55 ** int(original["n"])
        observed = float(revised["with_brightness_acceptance"])
        gap = abs(observed - expected)
        print(f"Ascella {original['circuit']} n={original['n']} {original['detector']}: gap={gap:.17g}")
        assert math.isfinite(observed)
        assert gap <= 1e-9
    else:
        assert revised["with_brightness_acceptance"] == "N/A"


def test_exactly_eight_cells_changed() -> None:
    original = _read(ORIGINAL)
    revised = _read(Path(os.environ.get("R1_BRIGHTNESS_TABLE", str(UPDATED))))
    assert len(original) == len(revised) == 32
    changes = [(i, key) for i, (a, b) in enumerate(zip(original, revised))
               for key in a if a[key] != b[key]]
    assert len(changes) == 8
    assert all(key == "with_brightness_acceptance" for _, key in changes)
