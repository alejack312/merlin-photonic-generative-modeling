"""Evaluate one frozen n=4 ring artifact with the direct final-only Fock adapter.

Example (PowerShell):
  $pcvl = Join-Path $env:TEMP 'merlin-v4-physical'
  venv/Scripts/python.exe scripts/v4_tcdp/evaluate_ring_photonic.py `
    results/v4_tcdp/rings/rings_spatial_exact/n4_seed0_smoke `
    --pcvl-path $pcvl --eta 0.9

The Perceval persistence directory must be isolated from unrelated runs. This
bounded evaluator accepts only n=4 smoke artifacts and never launches n=6/n=8
sweeps or a ring training job.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "run_directory",
        type=Path,
        nargs="?",
        default=Path("results/v4_tcdp/rings/rings_spatial_exact/n4_seed0_smoke"),
    )
    parser.add_argument("--eta", type=float, required=True, help="explicit fixed-photon survival probability per data photon")
    parser.add_argument(
        "--validation-manifest",
        type=Path,
        default=Path("results/v4_tcdp/deploy/physical_control_manifest_20260909_final2.json"),
        help="validated direct-control manifest required before deployment",
    )
    parser.add_argument(
        "--pcvl-path",
        type=Path,
        help="isolated writable Perceval persistence directory, e.g. $env:TEMP\\merlin-v4-physical",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/v4_tcdp/deploy/registered_v2_ring_photonic_n4_seed0_smoke.json"),
    )
    args = parser.parse_args()
    if args.pcvl_path is not None:
        args.pcvl_path.mkdir(parents=True, exist_ok=True)
        os.environ["PCVL_PERSISTENT_PATH"] = str(args.pcvl_path.resolve())
    from merlin_iqp.deploy.ring import evaluate_ring_artifact, load_ring_artifact, write_ring_evaluation

    artifact = load_ring_artifact(args.run_directory)
    result = evaluate_ring_artifact(artifact, eta=args.eta, validation_manifest_path=args.validation_manifest)
    output = write_ring_evaluation(result, args.output)
    print(json.dumps({"output": str(output), "status": result["status"], "run_id": result["run_id"], "comparison": result["comparison"], "metrics": result["comparison"]["metrics"]}, indent=2, sort_keys=True, allow_nan=False))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
