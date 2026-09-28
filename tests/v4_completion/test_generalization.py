"""R3 cell-level holdout and data-defined validity contracts."""

from __future__ import annotations

from dataclasses import replace

import numpy as np
import pytest

from merlin_iqp.experiments.datasets import load_rings_dataset
from merlin_iqp.experiments.generalization import (
    R3_CELL_HOLDOUT_FRACTION,
    R3_CELL_HOLDOUT_SEED,
    R3_MIN_HELD_OUT_CELLS,
    SCHEMA_VERSION,
    build_ring_cell_holdout,
    compute_cell_coverage_precision,
    r3_coverage_anchors,
    r3_memorizer_null,
    r3_sample_budget_grid,
    r3_uniform_sprayer_null,
    validate_r3_null_metrics,
)


@pytest.mark.parametrize("n, expected_hit_cells, expected_holdout_cells", [(4, 12, 3), (6, 24, 5), (8, 80, 16)])
def test_r3_holdout_pools_all_points_and_holds_out_whole_cells(
    n: int, expected_hit_cells: int, expected_holdout_cells: int
) -> None:
    split = build_ring_cell_holdout(load_rings_dataset(n))

    assert len(split.point_ids) == 400
    assert len(split.data_hit_cells) == expected_hit_cells
    assert len(split.held_out_cells) == expected_holdout_cells
    assert len(split.training_point_ids) + len(split.held_out_point_ids) == 400
    assert np.intersect1d(split.training_cells, split.held_out_cells).size == 0
    assert np.all(np.isin(split.point_cells[split.training_point_ids], split.training_cells))
    assert np.array_equal(np.unique(split.point_cells[split.held_out_point_ids]), split.held_out_cells)
    assert np.array_equal(np.sort(np.concatenate([split.training_cells, split.held_out_cells])), split.data_hit_cells)


def test_r3_validity_is_data_defined_and_distinguishes_unseen_valid_from_invalid() -> None:
    split = build_ring_cell_holdout(load_rings_dataset(4))
    labels = split.validity_labels()

    assert np.array_equal(np.flatnonzero(labels == "valid"), split.training_cells)
    assert np.array_equal(np.flatnonzero(labels == "unseen-valid"), split.held_out_cells)
    assert np.array_equal(np.flatnonzero(labels == "invalid"), split.invalid_cells)
    assert np.array_equal(split.valid_cells, split.data_hit_cells)
    assert np.array_equal(split.unseen_valid_cells, split.held_out_cells)


def test_r3_coverage_deduplicates_held_out_hits_and_precision_counts_samples() -> None:
    split = build_ring_cell_holdout(load_rings_dataset(4))
    sampled_cells = [
        int(split.held_out_cells[0]),
        int(split.held_out_cells[0]),
        int(split.training_cells[0]),
        int(split.invalid_cells[0]),
    ]

    metrics = compute_cell_coverage_precision(split, sampled_cells)

    assert metrics["primary_endpoint"] == "coverage"
    assert metrics["safeguard"] == "precision"
    assert metrics["coverage"] == pytest.approx(1.0 / len(split.held_out_cells))
    assert metrics["precision"] == pytest.approx(3.0 / 4.0)
    assert metrics["held_out_cells_hit"] == [int(split.held_out_cells[0])]
    assert metrics["normalized_coverage"] is not None
    assert metrics["anchor_labels"]["ceiling"].startswith("ORACLE:")


def test_r3_per_ring_coverage_uses_majority_assignment_for_mixed_cells() -> None:
    split = build_ring_cell_holdout(load_rings_dataset(4))

    mixed_cells = [
        int(cell)
        for cell in split.data_hit_cells
        if np.unique(split.point_rings[split.point_cells == cell]).size == 2
    ]
    assert mixed_cells
    for cell in mixed_cells:
        point_rings = split.point_rings[split.point_cells == cell]
        expected = "inner" if np.count_nonzero(point_rings == "inner") > np.count_nonzero(point_rings == "outer") else "outer"
        assert split.cell_rings[cell] == expected

    metrics = compute_cell_coverage_precision(split, split.held_out_cells)
    assert metrics["per_ring_coverage"]["outer"] == pytest.approx(1.0)
    assert metrics["per_ring_coverage"]["inner"] is None


def test_r3_all_invalid_samples_have_zero_coverage_and_precision() -> None:
    split = build_ring_cell_holdout(load_rings_dataset(4))

    metrics = compute_cell_coverage_precision(split, [int(split.invalid_cells[0])] * 5)

    assert metrics["coverage"] == 0.0
    assert metrics["precision"] == 0.0
    assert metrics["valid_sample_count"] == 0
    assert metrics["invalid_sample_count"] == 5


def test_r3_zero_samples_leave_precision_undefined_without_a_budget_default() -> None:
    split = build_ring_cell_holdout(load_rings_dataset(4))

    metrics = compute_cell_coverage_precision(split, [])

    assert metrics["sample_count"] == 0
    assert metrics["coverage"] == 0.0
    assert metrics["precision"] is None


def test_r3_empty_held_out_set_leaves_coverage_undefined() -> None:
    split = build_ring_cell_holdout(load_rings_dataset(4))
    empty_holdout = replace(
        split,
        held_out_cells=np.array([], dtype=np.int64),
        training_cells=split.data_hit_cells.copy(),
    )

    metrics = compute_cell_coverage_precision(empty_holdout, [int(split.training_cells[0])])

    assert metrics["coverage"] is None
    assert metrics["precision"] == 1.0
    assert metrics["ceiling"] is None
    assert metrics["gap_closed"] == "undefined"


def test_r3_memorizer_null_is_red_first_then_green() -> None:
    split = build_ring_cell_holdout(load_rings_dataset(4))
    sample_count = 10
    observed = compute_cell_coverage_precision(split, [int(split.training_cells[0])] * sample_count)
    expected = r3_memorizer_null(split, sample_count)

    corrupted = dict(observed)
    corrupted["coverage"] = 1.0
    with pytest.raises(AssertionError):
        validate_r3_null_metrics(corrupted, expected)
    validate_r3_null_metrics(observed, expected)
    assert expected["coverage"] == 0.0
    assert expected["precision"] == 1.0


def test_r3_uniform_sprayer_null_is_red_first_then_green_on_n4_fixture() -> None:
    split = build_ring_cell_holdout(load_rings_dataset(4))
    assert split.cell_count == 16
    assert len(split.data_hit_cells) == 12
    assert len(split.held_out_cells) == 3
    assert len(split.training_cells) == 9

    expected = r3_uniform_sprayer_null(split, 10)
    exact_formula = 1.0 - (15.0 / 16.0) ** 10
    assert expected["coverage"] == pytest.approx(exact_formula, abs=1e-9)
    assert expected["precision"] == pytest.approx(12.0 / 16.0, abs=1e-9)

    corrupted = dict(expected)
    corrupted["precision"] = 1.0
    with pytest.raises(AssertionError):
        validate_r3_null_metrics(corrupted, expected)
    validate_r3_null_metrics(expected, expected)


def test_r3_uniform_sprayer_monte_carlo_agrees_with_closed_form_within_sampling_error() -> None:
    split = build_ring_cell_holdout(load_rings_dataset(4))
    expected = r3_uniform_sprayer_null(split, 10)
    rng = np.random.default_rng(20260929)
    repetitions = 5000
    draws = rng.integers(0, split.cell_count, size=(repetitions, 10))
    coverage = np.mean(
        np.array([len(np.intersect1d(np.unique(row), split.held_out_cells)) / len(split.held_out_cells) for row in draws])
    )
    precision = np.mean(np.isin(draws, split.valid_cells))
    coverage_se = np.std(
        np.array([len(np.intersect1d(np.unique(row), split.held_out_cells)) / len(split.held_out_cells) for row in draws]),
        ddof=1,
    ) / np.sqrt(repetitions)
    precision_se = np.sqrt(expected["precision"] * (1.0 - expected["precision"]) / (repetitions * 10))
    assert abs(coverage - expected["coverage"]) <= 4.0 * coverage_se
    assert abs(precision - expected["precision"]) <= 4.0 * precision_se


def test_r3_anchors_guard_degenerate_gap_and_k_one() -> None:
    anchors = r3_coverage_anchors(n=4, held_out_cell_count=1, sample_count=0, coverage=0.0)

    assert anchors["floor"] == 0.0
    assert anchors["ceiling"] == 0.0
    assert anchors["gap_closed"] == "undefined"
    assert anchors["normalized_coverage"] is None


@pytest.mark.parametrize("n, expected", [(4, [2, 11, 36]), (6, [7, 44, 146]), (8, [27, 177, 588])])
def test_r3_sample_budget_grid_matches_registered_levels(n: int, expected: list[int]) -> None:
    grid = r3_sample_budget_grid(n)

    assert [record["N"] for record in grid] == expected
    assert [record["degenerate"] for record in grid] == [budget < 5 for budget in expected]


def test_r3_holdout_is_deterministic_and_manifest_records_registered_list() -> None:
    first = build_ring_cell_holdout(load_rings_dataset(6))
    second = build_ring_cell_holdout(load_rings_dataset(6))
    manifest = first.manifest()

    assert np.array_equal(first.held_out_cells, second.held_out_cells)
    assert first.holdout_seed == R3_CELL_HOLDOUT_SEED
    assert first.holdout_fraction == R3_CELL_HOLDOUT_FRACTION
    assert first.min_held_out_cells == R3_MIN_HELD_OUT_CELLS
    assert manifest["schema_version"] == SCHEMA_VERSION
    assert manifest["n"] == 6
    assert manifest["held_out_cells"] == first.held_out_cells.tolist()
    assert manifest["holdout"]["rng_role"].startswith("registered cell-holdout selection only")
    assert manifest["validity_rule"]["source"].endswith("never model outputs")


@pytest.mark.parametrize(
    "kwargs, message",
    [
        ({"holdout_fraction": 0.0}, "holdout_fraction"),
        ({"holdout_fraction": 1.0}, "holdout_fraction"),
        ({"min_held_out_cells": 0}, "min_held_out_cells"),
        ({"holdout_seed": "fit-seed"}, "holdout_seed"),
    ],
)
def test_r3_rejects_invalid_holdout_registration(kwargs: dict[str, object], message: str) -> None:
    with pytest.raises(ValueError, match=message):
        build_ring_cell_holdout(load_rings_dataset(4), **kwargs)
