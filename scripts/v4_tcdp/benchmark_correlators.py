"""Run the exact-feasible B1 frozen-model correlator audit.

Inputs are JSON mappings from MSB-first bitstrings to probabilities.  Exact
target coefficient access is an explicit oracle diagnostic and is never
silently labeled as an efficient preprocessing step.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from merlin_iqp.experiments.correlator_audit import (
    b2_capacity_ladder_audit,
    b2_paired_comparison,
    frozen_model_correlator_audit,
)


def _load_distribution(path: Path) -> dict[str, float]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(value, dict) and "distribution" in value:
        value = value["distribution"]
    if not isinstance(value, dict):
        raise ValueError(f"{path} must contain a bitstring-to-probability mapping")
    return {str(key): float(probability) for key, probability in value.items()}


def build_report(
    target_path: Path,
    model_path: Path,
    *,
    retained_order: int | None = None,
    sigma: float | None = None,
    target_coefficient_access: str = "oracle",
) -> dict[str, Any]:
    target = _load_distribution(target_path)
    model = _load_distribution(model_path)
    retained_subsets = None
    if retained_order is not None:
        n = len(next(iter(target)))
        if int(retained_order) != retained_order or not 0 <= retained_order <= n:
            raise ValueError("retained-order must be an integer in [0, n]")
        from itertools import combinations

        retained_subsets = tuple(
            subset
            for order in range(1, int(retained_order) + 1)
            for subset in combinations(range(n), order)
        )
    return frozen_model_correlator_audit(
        target,
        model,
        retained_subsets=retained_subsets,
        sigma=sigma,
        target_coefficient_access=target_coefficient_access,  # type: ignore[arg-type]
    )


def build_b2_report(
    target_path: Path,
    model_path: Path,
    *,
    max_order: int,
    subset_seed: int,
    learned_model_path: Path | None = None,
) -> dict[str, Any]:
    """Build the B2 ladder report without selecting TN/PPS dependencies."""

    target = _load_distribution(target_path)
    model = _load_distribution(model_path)
    learned_model = None if learned_model_path is None else _load_distribution(learned_model_path)
    report = b2_capacity_ladder_audit(
        target,
        model,
        max_order=max_order,
        subset_seed=subset_seed,
        learned_model=learned_model,
    )
    report["paired_comparison"] = b2_paired_comparison(report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--retained-order", type=int)
    parser.add_argument("--sigma", type=float)
    parser.add_argument("--target-coefficient-access", choices=("oracle", "observed"), default="oracle")
    parser.add_argument("--b2-max-order", type=int)
    parser.add_argument("--subset-seed", type=int, default=0)
    parser.add_argument("--learned-model", type=Path)
    args = parser.parse_args()
    if args.b2_max_order is not None:
        report = build_b2_report(
            args.target,
            args.model,
            max_order=args.b2_max_order,
            subset_seed=args.subset_seed,
            learned_model_path=args.learned_model,
        )
    else:
        report = build_report(
            args.target,
            args.model,
            retained_order=args.retained_order,
            sigma=args.sigma,
            target_coefficient_access=args.target_coefficient_access,
        )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if args.b2_max_order is not None:
        print(json.dumps(report["paired_comparison"], sort_keys=True))
    else:
        print(json.dumps({key: report[key] for key in ("identity_residual_max", "uniform_reference_sse")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
