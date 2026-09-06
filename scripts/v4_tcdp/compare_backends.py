"""Build a bounded, matched raw/compiled/deployed comparison for a ring cell."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "src"))

from merlin_iqp.classical import IQPModel  # noqa: E402
from merlin_iqp.deploy import apply_compiled_density, compile_generators  # noqa: E402
from merlin_iqp.experiments.comparison import DistributionArm, MatchedComparison  # noqa: E402


def _vector_from_mapping(mapping: dict[str, float]) -> np.ndarray:
    return np.array([mapping[key] for key in sorted(mapping)], dtype=np.float64)


def build_comparison(run_directory: Path, *, eta: float = 1.0) -> MatchedComparison:
    run = np.load(run_directory / "run.npz")
    dataset = np.load(run_directory / "dataset.npz")
    manifest = json.loads((run_directory / "manifest.json").read_text(encoding="utf-8"))
    generator = np.asarray(run["generator"], dtype=np.uint8)
    theta = np.asarray(run["final_theta"], dtype=np.float64)
    n = int(manifest["config"]["n"])
    target = np.asarray(dataset["train_histogram"], dtype=np.float64)

    model = IQPModel(generator, theta, provenance={"source": "rings_smoke_manifest", "run_id": manifest["run_id"]})
    raw = model.probability_vector_exact()
    singles = np.zeros(n, dtype=np.float64)
    pairs: list[tuple[int, int, float]] = []
    for row, value in zip(generator, theta, strict=True):
        support = np.flatnonzero(row)
        if len(support) == 1:
            singles[int(support[0])] += float(value)
        elif len(support) == 2:
            pairs.append((int(support[0]), int(support[1]), float(value)))
        else:
            raise ValueError("comparison supports only the ring weight-1/2 generator")

    # The primary compiled and deployed arms must share the exact effective
    # compiled parameters.  Otherwise quantization is incorrectly included in
    # the compiled-to-deployed gap.  Keep the unquantized result as an explicit
    # compilation control rather than silently folding it into that gap.
    unquantized = compile_generators(generator, theta, quantize=False)
    unquantized_mapping, unquantized_success = apply_compiled_density(unquantized)
    compiled = compile_generators(generator, theta, quantize=True)
    compiled_mapping, compiled_success = apply_compiled_density(compiled)
    deployed_mapping, deployed_success = apply_compiled_density(compiled, eta=eta)
    if eta == 1.0 and (
        not np.allclose(list(compiled_mapping.values()), list(deployed_mapping.values()), atol=1e-12, rtol=1e-12)
        or not np.isclose(compiled_success, deployed_success, atol=1e-12, rtol=1e-12)
    ):
        raise AssertionError("ideal eta=1 compiled and deployed arms must be identical")
    unquantized_vector = _vector_from_mapping(unquantized_mapping)
    compiled_vector = _vector_from_mapping(compiled_mapping)
    deployed_vector = _vector_from_mapping(deployed_mapping)
    if not np.allclose(raw.sum(), compiled_vector.sum()):
        raise ValueError("raw/compiled vectors are not normalized")

    return MatchedComparison(
        cell_id=f"{manifest['run_id']}/matched_backends",
        target=target,
        arms=(
            DistributionArm("numpy-iqp", raw, "raw", samples=20_000, provenance={"model_hash": manifest["model"]["final_theta_hash"]}),
            DistributionArm("ideal-unquantized-control", unquantized_vector, "compiled", acceptance_mass=unquantized_success, samples=20_000, provenance={"quantized": False, "role": "compilation_control", "construction": "absolute-probability-CP-map"}),
            DistributionArm("ideal-compiled-map", compiled_vector, "compiled", acceptance_mass=compiled_success, samples=20_000, provenance={"quantized": True, "role": "primary_compiled_reference", "construction": "absolute-probability-CP-map"}),
            DistributionArm("ideal-deployed-map", deployed_vector, "deployed", acceptance_mass=deployed_success, samples=20_000, provenance={"quantized": True, "role": "same_effective_parameters_as_compiled", "construction": "absolute-probability-CP-map", "physical_status": "reference_only", "source_model": "fixed_photon_g2_0", "eta": eta, "loss": "uniform_all_photons"}),
        ),
        hamming_sigma=0.5 * np.sqrt(n),
        spatial_centers=np.asarray(dataset["centers"], dtype=np.float64),
        spatial_sigma=0.1,
        common_manifest={
            "dataset_hash": manifest["dataset"]["dataset_hash"],
            "generator_hash": manifest["model"]["generator_hash"],
            "theta_hash": manifest["model"]["final_theta_hash"],
            "split": "train",
            "seed": manifest["config"]["seed"],
            "budget": {"training_steps": manifest["config"]["steps"], "accepted_samples": 20_000},
            "raw_compiled_deployed_distinct": True,
            "compiled_deployed_same_effective_parameters": True,
            "unquantized_compilation_control": True,
            "source_model": "fixed_photon_g2_0",
            "loss": {"eta": eta, "acceptance_rule": "eta**n * model_success"},
        },
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_directory", type=Path)
    parser.add_argument("--eta", type=float, default=1.0, help="fixed-photon survival probability per photon")
    parser.add_argument("--output", type=Path, default=None)
    args = parser.parse_args()
    comparison = build_comparison(args.run_directory, eta=args.eta)
    output = args.output or (args.run_directory / "backend_comparison.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(comparison.manifest(), indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8")
    print(json.dumps({"output": str(output), "cell_id": comparison.cell_id, "metrics": comparison.metrics()}, indent=2, sort_keys=True, allow_nan=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
