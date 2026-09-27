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

from merlin_iqp.experiments.correlator_audit import frozen_model_correlator_audit


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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, required=True)
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--retained-order", type=int)
    parser.add_argument("--sigma", type=float)
    parser.add_argument("--target-coefficient-access", choices=("oracle", "observed"), default="oracle")
    args = parser.parse_args()
    report = build_report(
        args.target,
        args.model,
        retained_order=args.retained_order,
        sigma=args.sigma,
        target_coefficient_access=args.target_coefficient_access,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({key: report[key] for key in ("identity_residual_max", "uniform_reference_sse")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
