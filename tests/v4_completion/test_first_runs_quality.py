"""Data-quality guards for the deduplicated first-run tables."""

from __future__ import annotations

import pytest

from scripts.v4_completion.run_first_r2_r3_runs import validate_multiseed_table


def test_multiseed_table_rejects_identical_rows() -> None:
    rows = [
        {"subset_seed": 0, "rung3_reconstruction_sse": 0.25},
        {"subset_seed": 1, "rung3_reconstruction_sse": 0.25},
    ]

    with pytest.raises(AssertionError, match="only identical"):
        validate_multiseed_table(rows)


def test_multiseed_table_accepts_seed_variation() -> None:
    rows = [
        {"subset_seed": 0, "rung3_reconstruction_sse": 0.25},
        {"subset_seed": 1, "rung3_reconstruction_sse": 0.5},
    ]

    validate_multiseed_table(rows)
