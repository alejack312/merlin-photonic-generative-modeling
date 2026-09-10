"""Run one registered classical IQP two-ring profile and write isolated artifacts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from merlin_iqp.experiments.rings import (  # noqa: E402
    available_profiles,
    resolve_config,
    train_rings,
    write_run_artifacts,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=tuple(available_profiles()), default="rings_spatial_exact")
    parser.add_argument("--n", type=int, default=4)
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--steps", type=int, default=None, help="override the smoke (3) or main (300) step count")
    parser.add_argument("--main", action="store_true", help="use the registered 300-step main profile")
    parser.add_argument("--initialization", choices=("data_dependent", "small_angle", "uniform"), default=None)
    parser.add_argument("--initialization-method", choices=("parity",), default=None)
    parser.add_argument("--initialization-scale", type=float, default=None)
    parser.add_argument("--initialization-std", type=float, default=None)
    parser.add_argument("--output-root", type=Path, default=REPO_ROOT / "results" / "v4_tcdp" / "rings")
    parser.add_argument("--list-profiles", action="store_true")
    args = parser.parse_args()
    if args.list_profiles:
        print(json.dumps(available_profiles(), indent=2, sort_keys=True))
        return 0
    config = resolve_config(
        args.profile,
        n=args.n,
        seed=args.seed,
        steps=args.steps,
        main=args.main,
        initialization=args.initialization,
        initialization_method=args.initialization_method,
        initialization_scale=args.initialization_scale,
        initialization_std=args.initialization_std,
    )
    run = train_rings(config)
    paths = write_run_artifacts(run, args.output_root)
    print(json.dumps({"run_id": f"{config.profile_id}/{config.cell_id}", "metrics": run.metrics, "artifacts": {key: str(value) for key, value in paths.items()}, "photonic_evaluation": run.photonic_evaluation}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
