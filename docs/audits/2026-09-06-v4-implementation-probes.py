"""Regression probes for the v4 audit repairs.

Run from repository root with venv/Scripts/python.exe. Each result records
whether the repaired contract now holds; this is not a substitute for the
full acceptance suite.
"""
import json
from pathlib import Path
import sys
import tempfile

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from merlin_iqp.classical import ExactProbabilities, IQPModel, Trainer
from merlin_iqp.deploy.density import compose_instruments
from merlin_iqp.deploy.maps import GateMap, _choi_from_kraus, validate_gate_map
from merlin_iqp.experiments.comparison import DistributionArm, MatchedComparison, expected_coverage
from merlin_iqp.experiments.datasets import load_rings_dataset
from merlin_iqp.experiments.nat import run_nat


def main():
    results = {}
    try:
        bundle = load_rings_dataset(4).bundle()
        results["F04_bundle"] = {"fixed": True, "width": bundle.n}
    except ValueError as error:
        results["F04_bundle"] = {"fixed": False, "error": str(error)}

    x = np.array([[0, 1], [1, 0]], complex)
    operator = np.kron(x, np.eye(2))
    gate = GateMap(4, 1, _choi_from_kraus((operator,)), "XI", kraus=(operator,))
    state = np.zeros((8, 8), complex)
    state[0, 0] = 1
    actual, _ = compose_instruments(3, state, [((0, 2), gate)])
    actual_bitstring = format(int(np.argmax(np.diag(actual).real)), "03b")
    results["F05_order"] = {"fixed": actual_bitstring == "100", "expected": "100", "actual": actual_bitstring}

    generator = np.eye(2, dtype=np.uint8)
    target = ExactProbabilities(np.array([0.1, 0.2, 0.3, 0.4]))
    theta = np.array([0.2, 0.3])
    original = Trainer(IQPModel(generator, theta), target, lr=0.01)
    cache = ROOT / ".pytest_cache"
    cache.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=cache) as directory:
        checkpoint = Path(directory) / "checkpoint.npz"
        original.run(2, checkpoint_path=checkpoint)
        resumed = Trainer(IQPModel(generator, theta), target, lr=0.2)
        try:
            resumed.resume(checkpoint)
        except ValueError as error:
            results["F06_resume"] = {"fixed": True, "error": str(error)}
        else:
            results["F06_resume"] = {"fixed": False, "error": "changed learning rate was accepted"}

    nat = run_nat(target, [(0, 1)], steps=0, initialization="small_angle", initialization_std=0)
    results["F07_std"] = {"fixed": nat.config.initialization_std == 0, "recorded_std": nat.config.initialization_std}

    transpose = np.zeros((4, 4))
    for i in range(2):
        for j in range(2):
            transpose[j + 2 * i, i + 2 * j] = 1
    inconsistent = GateMap(2, 1, np.eye(4), "transpose", superoperator=transpose)
    results["F11_physicality"] = {"fixed": not bool(validate_gate_map(inconsistent).passed)}

    comparison = MatchedComparison("support-mismatch", np.array([0.5, 0.5]), (DistributionArm("identity", np.array([1.0, 0]), "raw"),), 1.0)
    try:
        payload = comparison.manifest()
        json.dumps(payload, allow_nan=False)
        kl_row = payload["metrics"]["raw:identity"]
        results["F12_KL_export"] = {"fixed": kl_row["true_forward_kl_status"] == "infinite", "value": kl_row["true_forward_kl_value"]}
    except ValueError as error:
        results["F12_KL_export"] = {"fixed": False, "error": str(error)}

    coverage = expected_coverage(np.array([1.0, 0]), np.array([1.0, 0]), 0)["expected_coverage"]
    results["zero_shot_coverage"] = {"fixed": coverage == 0, "actual": coverage}
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
