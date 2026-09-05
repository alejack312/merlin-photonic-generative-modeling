"""Bounded Phase-27 deployment/compiler validation smoke.

The default run is ideal/NumPy-only and does not claim a D1 physical model.
Use --with-perceval only for the optional n=2 full-Fock diagnostic.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import time

import numpy as np

from merlin_iqp.deploy import (
    apply_compiled_density,
    compile_iqp,
    fixed_photon_attempts_per_sample,
    full_fock_cp_reference,
    ideal_cp_map,
    reconstruct_cp_map,
    success_weighted_haar_fidelity,
    validate_gate_map,
)


def run(with_perceval: bool = False) -> dict[str, object]:
    started = time.perf_counter()
    compiled = compile_iqp(3, [0.2, -0.1, 0.31], [(0, 2, 0.311), (1, 2, -0.2)])
    probabilities, model_success = apply_compiled_density(compiled)
    gate = reconstruct_cp_map(np.pi / 3, use_perceval=with_perceval)
    physicality = validate_gate_map(gate)
    ideal = ideal_cp_map(np.pi / 3)
    U = np.diag([1, 1, 1, np.exp(1j * np.pi / 3)])
    result: dict[str, object] = {
        "status": "PASS" if physicality.passed and np.isclose(sum(probabilities.values()), 1.0) else "FAIL",
        "compiler": compiled.as_metadata(),
        "probability_sum": float(sum(probabilities.values())),
        "model_success": float(model_success),
        "ideal_success_product": float(ideal.success**2),
        "map_physicality": physicality.__dict__,
        "haar_fidelity": float(success_weighted_haar_fidelity(gate, U)),
        "throughput_fixed_n": float(fixed_photon_attempts_per_sample(0.9, 3, model_success)),
        "perceval": gate.metadata["perceval"],
        "elapsed_seconds": float(time.perf_counter() - started),
    }
    if with_perceval:
        fock = full_fock_cp_reference(2, 0, 1, [0.2, 0.3], np.pi / 3)
        result["full_fock"] = {
            "status": fock.status,
            "accepted_mass": fock.accepted_mass,
            "rejected_mass": fock.rejected_mass,
            "diagnostics": fock.diagnostics,
        }
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--with-perceval", action="store_true")
    parser.add_argument("--output", type=Path, default=Path("results/v4_tcdp/deploy/validation_manifest.json"))
    args = parser.parse_args()
    result = run(args.with_perceval)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True), encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
