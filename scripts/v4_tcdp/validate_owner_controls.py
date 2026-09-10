"""Run the registered owner-control fixtures for NULL-03 through NULL-06.

The controls are deliberately limited to the settled D1 model: one fixed
``n``-photon source, explicit uniform per-photon loss, and ideal compiled
maps.  They record exact deterministic residuals separately from probability
vector comparisons.  The project-wide ``1.0e-16`` tolerance is used for
scalar identities and factorization residuals; the binding plan's
``1.0e-12`` probability/map tolerance is used for dense floating-point
probability vectors.

This command does not adjudicate the NULL-07 source-gap hypothesis or the
non-binding continuous-versus-discrete NAT hypothesis.  Those require a
different registered source model or experiment.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import platform
import subprocess
from typing import Any

import numpy as np

from merlin_iqp.deploy import (
    apply_compiled_density,
    compile_iqp,
    fixed_photon_accepted_mass,
    fixed_photon_attempts_per_sample,
    general_attempts_per_sample,
    heralded_cz_attempts_per_sample,
    ideal_cp_map,
    ideal_iqp_distribution,
)


EXACT_TOLERANCE = 1.0e-16
PROBABILITY_TOLERANCE = 1.0e-12
ETA = 0.9
N = 4
SINGLES = (0.17, -0.23, 0.31, 0.41)
PAIRS = ((0, 1, 0.23), (2, 3, -0.18))


def _repo_commit() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"


def _tvd(left: dict[str, float], right: dict[str, float]) -> float:
    keys = set(left) | set(right)
    return float(0.5 * sum(abs(left.get(key, 0.0) - right.get(key, 0.0)) for key in keys))


def _max_abs(left: dict[str, float], right: dict[str, float]) -> float:
    keys = set(left) | set(right)
    return float(max(abs(left.get(key, 0.0) - right.get(key, 0.0)) for key in keys))


def _factorized_distribution(distribution: dict[str, float], n: int) -> dict[str, float]:
    marginals = [
        sum(probability for bits, probability in distribution.items() if bits[qubit] == "1")
        for qubit in range(n)
    ]
    return {
        bits: float(
            np.prod(
                [
                    marginals[qubit] if bits[qubit] == "1" else 1.0 - marginals[qubit]
                    for qubit in range(n)
                ]
            )
        )
        for bits in distribution
    }


def _status(*checks: bool) -> str:
    return "PASS" if all(checks) else "FAIL"


def run() -> dict[str, Any]:
    # NULL-03: removing all pair terms must factorize for product preparation
    # and measurement.  This is an exact analytic control, not full-Fock data.
    k0 = compile_iqp(N, SINGLES, (), quantize=False)
    k0_distribution, k0_success = apply_compiled_density(k0, eta=1.0)
    k0_factorized = _factorized_distribution(k0_distribution, N)
    k0_max_residual = _max_abs(k0_distribution, k0_factorized)
    k0_record = {
        "prediction": "k=0 output factorizes under product preparation and measurement",
        "source_model": "analytic product IQP reference",
        "n": N,
        "pair_count": 0,
        "model_success": float(k0_success),
        "max_factorization_residual": k0_max_residual,
        "tolerance": PROBABILITY_TOLERANCE,
        "status": "PASS" if k0_max_residual <= PROBABILITY_TOLERANCE else "FAIL",
    }

    # NULL-04: same raw parameters through the unquantized compiler must match
    # the independent ideal IQP distribution and compiled pair success.
    compiled = compile_iqp(N, SINGLES, PAIRS, quantize=False)
    compiled_distribution, compiled_success = apply_compiled_density(compiled, eta=1.0)
    reference_distribution = ideal_iqp_distribution(N, SINGLES, PAIRS)
    pair_success = float(
        np.prod(
            [ideal_cp_map(angle.wrapped_alpha).success for _, angle in compiled.pair_angles]
        )
    )
    map_max_residual = _max_abs(compiled_distribution, reference_distribution)
    map_tvd = _tvd(compiled_distribution, reference_distribution)
    success_residual = abs(float(compiled_success) - pair_success)
    null04_status = _status(
        map_max_residual <= PROBABILITY_TOLERANCE,
        success_residual <= EXACT_TOLERANCE,
    )
    null04 = {
        "prediction": "same-parameter ideal compilation equals the independent reference under the declared codec",
        "source_model": "analytic compiled map; quantize=false",
        "n": N,
        "singles": list(SINGLES),
        "pairs": [list(row) for row in PAIRS],
        "max_probability_residual": map_max_residual,
        "tvd": map_tvd,
        "success_residual": success_residual,
        "probability_tolerance": PROBABILITY_TOLERANCE,
        "exact_tolerance": EXACT_TOLERANCE,
        "status": null04_status,
    }

    # NULL-05: fixed-photon uniform loss changes accepted mass by eta**n but
    # leaves the normalized conditional distribution unchanged.
    lossy_compiled = compile_iqp(N, SINGLES, PAIRS, quantize=True)
    ideal_distribution, ideal_success = apply_compiled_density(lossy_compiled, eta=1.0)
    lossy_distribution, lossy_success = apply_compiled_density(lossy_compiled, eta=ETA)
    expected_loss_success = float(ideal_success * ETA**N)
    loss_shape_tvd = _tvd(ideal_distribution, lossy_distribution)
    loss_success_residual = abs(float(lossy_success) - expected_loss_success)
    null05 = {
        "prediction": "uniform fixed-photon loss scales accepted mass by eta**n and preserves conditional shape",
        "source_model": "fixed_photon_g2_0",
        "n": N,
        "eta": ETA,
        "ideal_success": float(ideal_success),
        "lossy_success": float(lossy_success),
        "expected_lossy_success": expected_loss_success,
        "conditional_shape_tvd": loss_shape_tvd,
        "success_residual": loss_success_residual,
        "probability_tolerance": PROBABILITY_TOLERANCE,
        "exact_tolerance": EXACT_TOLERANCE,
        "status": _status(
            loss_shape_tvd <= PROBABILITY_TOLERANCE,
            loss_success_residual <= EXACT_TOLERANCE,
        ),
    }

    # NULL-06: compare both registered throughput formulas.  No empirical
    # source-rate claim is made; these are model-derived attempts/sample.
    model_success = float(ideal_success)
    total_acceptance = fixed_photon_accepted_mass(ETA, N, model_success)
    cp_attempts = fixed_photon_attempts_per_sample(ETA, N, model_success)
    general_attempts = general_attempts_per_sample(total_acceptance)
    cp_residual = abs(cp_attempts - 1.0 / total_acceptance)
    heralded_n = 3
    heralded_k = 2
    heralded_attempts = heralded_cz_attempts_per_sample(ETA, heralded_n, heralded_k)
    heralded_expected = 1.0 / (
        ETA ** (heralded_n + 2 * heralded_k) * (2.0 / 27.0) ** heralded_k
    )
    heralded_residual = abs(heralded_attempts - heralded_expected)
    null06 = {
        "prediction": "attempts per accepted sample equals 1/s under each declared acceptance model",
        "cp_model": {
            "eta": ETA,
            "n": N,
            "model_success": model_success,
            "total_acceptance": total_acceptance,
            "fixed_photon_attempts_per_sample": cp_attempts,
            "general_attempts_per_sample": general_attempts,
            "residual": cp_residual,
            "status": "PASS" if cp_residual <= EXACT_TOLERANCE else "FAIL",
        },
        "heralded_model": {
            "eta": ETA,
            "n": heralded_n,
            "k": heralded_k,
            "attempts_per_sample": heralded_attempts,
            "expected": heralded_expected,
            "residual": heralded_residual,
            "status": "PASS" if heralded_residual <= EXACT_TOLERANCE else "FAIL",
        },
        "tolerance": EXACT_TOLERANCE,
        "status": _status(
            cp_residual <= EXACT_TOLERANCE,
            heralded_residual <= EXACT_TOLERANCE,
        ),
    }

    controls = {
        "NULL-03": k0_record,
        "NULL-04": null04,
        "NULL-05": null05,
        "NULL-06": null06,
    }
    result: dict[str, Any] = {
        "schema_version": "v4_tcdp.owner_controls.v1",
        "status": _status(*(record["status"] == "PASS" for record in controls.values())),
        "scope": {
            "d1": "fixed_photon_g2_0 with explicit uniform loss",
            "physical_backend": False,
            "conditional_distributions_and_absolute_success_separate": True,
            "owner_prediction_note": "docs/v4-owner-predictions-2026-09-08.md",
        },
        "tolerances": {
            "exact_deterministic": EXACT_TOLERANCE,
            "probability_map": PROBABILITY_TOLERANCE,
        },
        "controls": controls,
        "provenance": {
            "repo_commit": _repo_commit(),
            "python": platform.python_version(),
        },
    }
    payload = json.dumps(result, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    result["payload_sha256"] = hashlib.sha256(payload).hexdigest()
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/v4_tcdp/controls/owner_controls_20260908.json"),
    )
    args = parser.parse_args()
    result = run()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
