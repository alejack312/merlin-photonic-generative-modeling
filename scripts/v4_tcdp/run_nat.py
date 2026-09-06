"""Run a bounded Hamming-MMD NAT smoke and optionally its equal-budget control."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from merlin_iqp.experiments.datasets import load_rings_dataset  # noqa: E402
from merlin_iqp.experiments.nat import run_equal_budget_control, run_nat, write_nat_run  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=4)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--steps", type=int, default=3)
    parser.add_argument("--sigma", type=float, default=None)
    parser.add_argument("--pair-budget", type=int, default=None)
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "results" / "v4_tcdp" / "nat" / "nat.json")
    parser.add_argument("--equal-budget-control", action="store_true")
    args = parser.parse_args()
    if args.n < 2:
        parser.error("--n must be at least 2")
    dataset = load_rings_dataset(args.n)
    pairs = [(index, index + 1) for index in range(args.n - 1)]
    sigma = 0.5 * math.sqrt(args.n) if args.sigma is None else args.sigma
    run = run_nat(dataset.train_target, pairs, n=args.n, seed=args.seed, steps=args.steps, sigma=sigma, pair_budget=args.pair_budget, source_commit="working-tree")
    outputs = {"nat": str(write_nat_run(run, args.output))}
    if args.equal_budget_control:
        control = run_equal_budget_control(dataset.train_target, pairs, n=args.n, seed=args.seed, steps=args.steps, sigma=sigma, pair_budget=args.pair_budget, source_commit="working-tree")
        control_path = args.output.with_name(args.output.stem + "-control" + args.output.suffix)
        outputs["control"] = str(write_nat_run(control, control_path))
    print(json.dumps({"artifacts": outputs, "nat": run.to_dict()}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
