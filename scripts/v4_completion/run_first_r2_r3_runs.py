"""Run the bounded B1/B2(1--3)/R3 reference panel with fit deduplication."""

from __future__ import annotations

import csv
import json
import subprocess
import sys
import time
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from merlin_iqp.experiments.correlator_audit import (  # noqa: E402
    B2_RUNG_LABELS,
    _b2_rung_metrics,
    _subset_keys,
    b2_capacity_ladder_audit,
    frozen_model_correlator_audit,
    walsh_moments,
)
from merlin_iqp.experiments.datasets import load_rings_dataset  # noqa: E402
from merlin_iqp.experiments.generalization import (  # noqa: E402
    build_ring_cell_holdout,
    r3_coverage_anchors,
    r3_known_support_null,
    r3_memorizer_null,
    r3_sample_budget_grid,
    r3_uniform_sprayer_null,
)


OUTPUT_ROOT = REPO_ROOT / "results" / "v4_completion" / "20260929_first_r2_r3_runs"
PROFILE_IDS = ("rings_hamming", "rings_spatial_exact")
N_VALUES = (6, 8)
SOURCE_CHECKPOINT_SEEDS = (0, 1, 2, 3, 4)
REPRESENTATIVE_CHECKPOINT_SEED = 0
SUBSET_SEED = 17
SUBSET_SEEDS = tuple(range(200))
L_VALUES = (1, 2)


def _distribution(values: np.ndarray, n: int) -> dict[str, float]:
    return {format(index, f"0{n}b"): float(value) for index, value in enumerate(values)}


def _git_status() -> dict[str, str]:
    commit = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, check=True, capture_output=True, text=True
    ).stdout.strip()
    status = subprocess.run(
        ["git", "status", "--short"], cwd=REPO_ROOT, check=True, capture_output=True, text=True
    ).stdout
    return {"commit": commit, "status": status}


def _load_representative_checkpoint(profile_id: str, n: int) -> tuple[dict[str, float], dict[str, float]]:
    run_root = (
        REPO_ROOT
        / "results"
        / "v4_tcdp"
        / "rings"
        / profile_id
        / f"n{n}_seed{REPRESENTATIVE_CHECKPOINT_SEED}_main"
    )
    dataset = np.load(run_root / "dataset.npz")
    run = np.load(run_root / "run.npz")
    return _distribution(dataset["train_histogram"], n), _distribution(run["output_probabilities"], n)


def _b1_row(profile_id: str, n: int, target: Mapping[str, float], model: Mapping[str, float]) -> dict[str, Any]:
    sigma = 0.1 if profile_id == "rings_spatial_exact" else 0.5 * np.sqrt(n)
    run_root = (
        REPO_ROOT
        / "results"
        / "v4_tcdp"
        / "rings"
        / profile_id
        / f"n{n}_seed{REPRESENTATIVE_CHECKPOINT_SEED}_main"
    )
    loss_history = np.load(run_root / "run.npz")["loss_history"]
    audit = frozen_model_correlator_audit(
        target,
        model,
        sigma=float(sigma),
        target_coefficient_access="oracle",
        same_theta_loss_before=float(loss_history[0]),
        same_theta_loss_after=float(loss_history[-1]),
    )
    return {
        "profile": profile_id,
        "n": n,
        "source_checkpoint_seeds": ",".join(str(seed) for seed in SOURCE_CHECKPOINT_SEEDS),
        "n_unique_fits": 1,
        "interval": "none",
        "target_role": "train_histogram used by frozen checkpoint",
        "target_coefficient_access": audit["target_coefficient_access"],
        "oracle_target_coefficients": audit["oracle_target_coefficients"],
        "residual_by_order": audit["residual_by_order"],
        "normalized_residual_by_order": audit["normalized_residual_by_order"],
        "kernel_weighted_contribution_by_order": audit["kernel_weighted_contribution_by_order"],
        "negative_reconstruction_mass": audit["negative_reconstruction_mass"],
        "omitted_energy_all_orders": audit["omitted_energy"],
        "omitted_residual_energy_all_orders": audit["omitted_residual_energy"],
        "same_theta_loss_change": audit["same_theta_loss_change"],
    }


def _b2_rows_for_fit(
    profile_id: str,
    n: int,
    target: Mapping[str, float],
    model: Mapping[str, float],
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for L in (*L_VALUES, n):
        report = b2_capacity_ladder_audit(target, model, max_order=L, subset_seed=SUBSET_SEED)
        for rung in (1, 2, 3):
            entry = report["rungs_by_number"][str(rung)]
            rows.append(
                {
                    "profile": profile_id,
                    "n": n,
                    "L": L,
                    "source_checkpoint_seeds": ",".join(str(seed) for seed in SOURCE_CHECKPOINT_SEEDS),
                    "n_unique_fits": 1,
                    "interval": "none",
                    "subset_seed": SUBSET_SEED,
                    "rung": rung,
                    "label": B2_RUNG_LABELS[rung],
                    "reference_only": entry["reference_only"],
                    "oracle_target_coefficients": entry["oracle_target_coefficients"],
                    "nonidentity_count": entry["nonidentity_count"],
                    "frozen_theta_coefficient_sse": entry["frozen_theta_coefficient_sse"],
                    "frozen_theta_reconstruction_sse": entry["frozen_theta_reconstruction_sse"],
                    "frozen_theta_negative_reconstruction_mass": entry[
                        "frozen_theta_negative_reconstruction_mass"
                    ],
                }
            )
    return rows


def _run_b1_and_b2() -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    b1_rows: list[dict[str, Any]] = []
    b2_rows: list[dict[str, Any]] = []
    for profile_id in PROFILE_IDS:
        for n in N_VALUES:
            target, model = _load_representative_checkpoint(profile_id, n)
            b1_rows.append(_b1_row(profile_id, n, target, model))
            b2_rows.extend(_b2_rows_for_fit(profile_id, n, target, model))
    return b1_rows, b2_rows


def validate_multiseed_table(
    rows: Sequence[Mapping[str, Any]],
    *,
    seed_field: str = "subset_seed",
    metric_fields: Sequence[str] = ("rung3_reconstruction_sse",),
) -> None:
    """Reject a purported variable-seed table whose measured values never vary."""

    if len(rows) < 2:
        raise AssertionError("multi-seed table must contain at least two rows")
    if len({row.get(seed_field) for row in rows}) < 2:
        raise AssertionError("multi-seed table must contain at least two distinct seeds")
    signatures = {tuple(row.get(field) for field in metric_fields) for row in rows}
    if len(signatures) == 1:
        raise AssertionError("multi-seed table contains only identical measured rows")


def _run_rung3_subset_sweep() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for profile_id in PROFILE_IDS:
        for n in N_VALUES:
            target, model = _load_representative_checkpoint(profile_id, n)
            target_moments = walsh_moments(target)
            frozen_model_moments = walsh_moments(model)
            all_nonidentity = tuple(subset for subset in _subset_keys(n) if subset)
            for L in (*L_VALUES, n):
                order_selected = tuple(subset for subset in all_nonidentity if len(subset) <= L)
                rung_two = _b2_rung_metrics(
                    rung=2,
                    label=B2_RUNG_LABELS[2],
                    target=target,
                    target_moments=target_moments,
                    frozen_model=model,
                    frozen_model_moments=frozen_model_moments,
                    selected_subsets=order_selected,
                    subset_seed=SUBSET_SEED,
                    reference_only=False,
                    learned_model=None,
                )
                for subset_seed in SUBSET_SEEDS:
                    rng = np.random.default_rng(subset_seed)
                    random_indices = rng.choice(len(all_nonidentity), size=len(order_selected), replace=False)
                    random_selected = tuple(all_nonidentity[int(index)] for index in sorted(random_indices.tolist()))
                    rung_three = _b2_rung_metrics(
                        rung=3,
                        label=B2_RUNG_LABELS[3],
                        target=target,
                        target_moments=target_moments,
                        frozen_model=model,
                        frozen_model_moments=frozen_model_moments,
                        selected_subsets=random_selected,
                        subset_seed=subset_seed,
                        reference_only=False,
                        learned_model=None,
                    )
                    rows.append(
                        {
                            "profile": profile_id,
                            "n": n,
                            "L": L,
                            "subset_seed": subset_seed,
                            "paired": True,
                            "rung2_reconstruction_sse": rung_two["frozen_theta_reconstruction_sse"],
                            "rung3_reconstruction_sse": rung_three["frozen_theta_reconstruction_sse"],
                            "rung3_minus_rung2_reconstruction_sse": float(
                                rung_three["frozen_theta_reconstruction_sse"]
                                - rung_two["frozen_theta_reconstruction_sse"]
                            ),
                            "rung2_coefficient_sse": rung_two["frozen_theta_coefficient_sse"],
                            "rung3_coefficient_sse": rung_three["frozen_theta_coefficient_sse"],
                        }
                    )
    return rows


def _summary(values: Sequence[float]) -> dict[str, float]:
    array = np.asarray(values, dtype=float)
    q25 = float(np.quantile(array, 0.25))
    q75 = float(np.quantile(array, 0.75))
    return {
        "median": float(np.median(array)),
        "q25": q25,
        "q75": q75,
        "iqr": q75 - q25,
        "min": float(np.min(array)),
        "max": float(np.max(array)),
    }


def _run_rung3_subset_summaries(rows: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    groups = {(row["profile"], row["n"], row["L"]) for row in rows}
    for profile_id, n, L in sorted(groups):
        group = [row for row in rows if (row["profile"], row["n"], row["L"]) == (profile_id, n, L)]
        variation_expected = L < n
        if variation_expected:
            validate_multiseed_table(group)
        reconstruction = _summary([float(row["rung3_reconstruction_sse"]) for row in group])
        coefficient = _summary([float(row["rung3_coefficient_sse"]) for row in group])
        delta = _summary([float(row["rung3_minus_rung2_reconstruction_sse"]) for row in group])
        summaries.append(
            {
                "profile": profile_id,
                "n": n,
                "L": L,
                "subset_seed_count": len(group),
                "seed_variation_expected": variation_expected,
                "paired_with_rung2": all(bool(row["paired"]) for row in group),
                "rung2_reconstruction_sse": float(group[0]["rung2_reconstruction_sse"]),
                "rung3_reconstruction_sse_median": reconstruction["median"],
                "rung3_reconstruction_sse_q25": reconstruction["q25"],
                "rung3_reconstruction_sse_q75": reconstruction["q75"],
                "rung3_reconstruction_sse_iqr": reconstruction["iqr"],
                "rung3_reconstruction_sse_min": reconstruction["min"],
                "rung3_reconstruction_sse_max": reconstruction["max"],
                "rung3_minus_rung2_reconstruction_sse_median": delta["median"],
                "rung3_minus_rung2_reconstruction_sse_iqr": delta["iqr"],
                "rung3_coefficient_sse_median": coefficient["median"],
                "rung3_coefficient_sse_iqr": coefficient["iqr"],
            }
        )
    return summaries


def _run_r3_references() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for n in (4, 6, 8):
        holdout = build_ring_cell_holdout(load_rings_dataset(n))
        for budget in r3_sample_budget_grid(n):
            sample_count = int(budget["N"])
            anchors = r3_coverage_anchors(
                n=n,
                held_out_cell_count=len(holdout.held_out_cells),
                sample_count=sample_count,
                coverage=0.0,
            )
            references = {
                "memorizer": r3_memorizer_null(holdout, sample_count),
                "sprayer": r3_uniform_sprayer_null(holdout, sample_count),
                "known_support": r3_known_support_null(holdout, sample_count),
                "ceiling": {"coverage": anchors["ceiling"], "precision": 1.0},
            }
            for reference_name, reference in references.items():
                observed_coverage = reference["coverage"]
                observed_anchors = r3_coverage_anchors(
                    n=n,
                    held_out_cell_count=len(holdout.held_out_cells),
                    sample_count=sample_count,
                    coverage=observed_coverage,
                )
                rows.append(
                    {
                        "n": n,
                        "N": sample_count,
                        "target_uniform_coverage": budget["target_coverage"],
                        "degenerate": budget["degenerate"],
                        "valid_cell_count_V": len(holdout.valid_cells),
                        "held_out_cell_count_k": len(holdout.held_out_cells),
                        "reference": reference_name,
                        "coverage": observed_coverage,
                        "precision": reference["precision"],
                        "floor": observed_anchors["floor"],
                        "ceiling": observed_anchors["ceiling"],
                        "gap_closed": observed_anchors["gap_closed"],
                        "normalized_coverage": observed_anchors["normalized_coverage"],
                        "floor_le_coverage_le_ceiling": (
                            observed_coverage is None
                            or observed_anchors["ceiling"] is None
                            or observed_anchors["floor"] - 1e-12 <= observed_coverage <= observed_anchors["ceiling"] + 1e-12
                        ),
                    }
                )
    return rows


def _write_csv(path: Path, rows: Sequence[Mapping[str, Any]]) -> None:
    flattened = []
    for row in rows:
        flattened.append(
            {
                key: json.dumps(value, sort_keys=True, separators=(",", ":"))
                if isinstance(value, (dict, list))
                else value
                for key, value in row.items()
            }
        )
    fieldnames = sorted({key for row in flattened for key in row})
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(flattened)


def _markdown_table(title: str, rows: Sequence[Mapping[str, Any]]) -> str:
    if not rows:
        return f"## {title}\n\nNo rows.\n"
    fields = list(rows[0])
    lines = [f"## {title}", "", "| " + " | ".join(fields) + " |", "|" + "|".join("---" for _ in fields) + "|"]
    for row in rows:
        cells = []
        for field in fields:
            value = row.get(field)
            if isinstance(value, (dict, list)):
                value = json.dumps(value, sort_keys=True, separators=(",", ":"))
            cells.append(str(value).replace("|", "\\|"))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines) + "\n"


def main() -> int:
    start = time.perf_counter()
    b1_rows, b2_rows = _run_b1_and_b2()
    rung3_subset_rows = _run_rung3_subset_sweep()
    rung3_summary_rows = _run_rung3_subset_summaries(rung3_subset_rows)
    r3_rows = _run_r3_references()
    elapsed = time.perf_counter() - start
    git_state = _git_status()
    OUTPUT_ROOT.mkdir(parents=True, exist_ok=True)
    _write_csv(OUTPUT_ROOT / "b1_measured.csv", b1_rows)
    _write_csv(OUTPUT_ROOT / "b2_rungs_1_3_measured.csv", b2_rows)
    _write_csv(OUTPUT_ROOT / "b2_rung3_subset_distribution.csv", rung3_subset_rows)
    _write_csv(OUTPUT_ROOT / "b2_rung3_distribution_summary.csv", rung3_summary_rows)
    _write_csv(OUTPUT_ROOT / "r3_references_measured.csv", r3_rows)
    report = {
        "schema_version": "v4_completion.first_r2_r3_runs.v2",
        "source_git": git_state,
        "stage_cap_hours": 7,
        "measured_elapsed_seconds": elapsed,
        "pilot": {
            "one_n6_b1_b2_seconds": 0.2640228999662213,
            "all_n4_n6_n8_r3_reference_seconds": 0.1089036000194028,
            "previous_projected_seconds": 5.389361599343829,
            "projection_basis": "previous 20 n=6/n=8 profile-seed checkpoints plus n=4/6/8 R3 references",
        },
        "scope": {
            "b1": "one row per profile,n; source checkpoint seeds 0-4 were identical; n_unique_fits=1; no interval",
            "b2": "one row per profile,n,L,rung; source checkpoint seeds 0-4 were identical; n_unique_fits=1; no interval",
            "b2_rung3_subset_sweep": "200 subset seeds per profile,n,L, paired with rung 2; L=n is full-set deterministic",
            "r3": "memorizer, uniform sprayer, known-support, and ceiling references at registered N grid; no model comparison",
            "target_role": "train histogram used by each frozen checkpoint",
            "oracle_label": "exact target coefficient access is oracle",
        },
        "rows": {
            "b1": len(b1_rows),
            "b2": len(b2_rows),
            "b2_rung3_subset_distribution": len(rung3_subset_rows),
            "b2_rung3_distribution_summary": len(rung3_summary_rows),
            "r3": len(r3_rows),
        },
    }
    (OUTPUT_ROOT / "manifest.json").write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    markdown = "# First R2/R3 runs (deduplicated raw tables)\n\n"
    markdown += "## MEASURED\n\n"
    markdown += "B1/B2 report one fit per deterministic (profile,n) checkpoint family: n_unique fits = 1, no interval. Exact-target coefficient access is labelled oracle.\n\n"
    markdown += _markdown_table("B1 frozen-model audit (one row per profile,n)", b1_rows)
    markdown += _markdown_table("B2 rungs 1-3 (one row per profile,n,L,rung)", b2_rows)
    markdown += _markdown_table("B2 rung-3 paired subset-seed distribution summary", rung3_summary_rows)
    markdown += "Raw paired subset-seed rows are in `b2_rung3_subset_distribution.csv`.\n\n"
    markdown += _markdown_table("R3 reference rows", r3_rows)
    markdown += "## AGAINST NULLS\n\n"
    markdown += "R3 rows are closed-form reference outputs; `floor_le_coverage_le_ceiling` is the recorded anchor check. No model interval test was run.\n\n"
    markdown += _markdown_table(
        "R3 null/reference checks",
        [
            {key: row[key] for key in ("n", "N", "reference", "coverage", "precision", "floor", "ceiling", "floor_le_coverage_le_ceiling")}
            for row in r3_rows
        ],
    )
    markdown += "## EXPLORATORY\n\nNo model-vs-model comparison was run. TN/PPS rungs remain pending dependency review.\n"
    (OUTPUT_ROOT / "raw_tables.md").write_text(markdown, encoding="utf-8")
    print(
        json.dumps(
            {"output_root": str(OUTPUT_ROOT), "elapsed_seconds": elapsed, "rows": report["rows"]},
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
