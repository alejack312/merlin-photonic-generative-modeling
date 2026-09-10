"""Run a bounded Hamming-MMD NAT smoke and optionally its equal-budget control."""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from merlin_iqp.experiments.datasets import load_rings_dataset  # noqa: E402
from merlin_iqp.experiments.nat import nat_report, nat_state_hash, run_equal_budget_control, run_matched_continuation, run_nat, write_nat_report, write_nat_run  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--n", type=int, default=4)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--steps", type=int, default=3)
    parser.add_argument("--sigma", type=float, default=None)
    parser.add_argument("--pair-budget", type=int, default=None)
    parser.add_argument("--output", type=Path, default=REPO_ROOT / "results" / "v4_tcdp" / "nat" / "nat.json")
    parser.add_argument("--equal-budget-control", action="store_true")
    parser.add_argument("--matched-continuation", action="store_true", help="emit one frozen warm start and two matched continuation arms")
    parser.add_argument("--eta", type=float, default=1.0, help="fixed-photon survival probability used only in acceptance reporting")
    parser.add_argument("--time-limit-seconds", type=float, default=None, help="stop only between complete outer steps")
    args = parser.parse_args()
    if args.n < 2:
        parser.error("--n must be at least 2")
    started = time.perf_counter()
    dataset = load_rings_dataset(args.n)
    pairs = [(index, index + 1) for index in range(args.n - 1)]
    sigma = 0.5 * math.sqrt(args.n) if args.sigma is None else args.sigma
    outputs: dict[str, str] = {}
    if args.matched_continuation:
        warm_path = args.output.with_name(args.output.stem + "-warm-start" + args.output.suffix)
        arm_a_path = args.output.with_name(args.output.stem + "-matched-arm-a" + args.output.suffix)
        arm_b_path = args.output.with_name(args.output.stem + "-matched-arm-b" + args.output.suffix)
        warm_start = run_nat(
            dataset.train_target,
            pairs,
            n=args.n,
            seed=args.seed,
            steps=args.steps,
            sigma=sigma,
            pair_budget=args.pair_budget,
            source_commit="working-tree",
            run_kind="matched_warm_start",
            time_limit_seconds=args.time_limit_seconds,
        )
        common_start_hash = nat_state_hash(warm_start)
        warm_metadata = {
            "role": "frozen_warm_start",
            "frozen": True,
            "state_hash": common_start_hash,
            "training_budget": dict(warm_start.budgets),
        }
        outputs["warm_start"] = str(write_nat_run(warm_start, warm_path, artifact_metadata=warm_metadata))
        arms = {}
        for arm_id, arm_path in (("a", arm_a_path), ("b", arm_b_path)):
            arm = run_matched_continuation(
                dataset.train_target,
                pairs,
                warm_start,
                steps=args.steps,
                pair_budget=args.pair_budget,
                run_kind=f"matched_arm_{arm_id}",
            )
            arms[arm_id] = arm
            arm_metadata = {
                "role": "matched_continuation_arm",
                "arm_id": arm_id,
                "branch_from": warm_path.name,
                "common_start_hash": common_start_hash,
                "evaluation_budget": dict(arm.budgets),
            }
            outputs[f"matched_arm_{arm_id}"] = str(write_nat_run(arm, arm_path, artifact_metadata=arm_metadata))
        run = warm_start
    else:
        run = run_nat(dataset.train_target, pairs, n=args.n, seed=args.seed, steps=args.steps, sigma=sigma, pair_budget=args.pair_budget, source_commit="working-tree")
        outputs["nat"] = str(write_nat_run(run, args.output))
    if args.equal_budget_control:
        control = run_equal_budget_control(dataset.train_target, pairs, n=args.n, seed=args.seed, steps=args.steps, sigma=sigma, pair_budget=args.pair_budget, source_commit="working-tree")
        control_path = args.output.with_name(args.output.stem + "-control" + args.output.suffix)
        outputs["control"] = str(write_nat_run(control, control_path))
    if args.matched_continuation:
        report_path = args.output.with_name(args.output.stem + "-report" + args.output.suffix)
        report = nat_report(dataset.train_target, warm_start, arms, fixed_pair_ablation=control if args.equal_budget_control else None, eta=args.eta)
        report["execution_timing"] = {
            "elapsed_seconds": time.perf_counter() - started,
            "time_limit_seconds": args.time_limit_seconds,
            "basis": "wall_clock_cli_execution_including_warm_start_arms_and_report",
        }
        outputs["report"] = str(write_nat_report(report, report_path))
    print(json.dumps({"artifacts": outputs, "nat": run.to_dict()}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
