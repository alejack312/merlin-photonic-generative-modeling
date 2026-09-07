"""Run bounded direct fixed-photon physical controls and write a manifest.

The CLI uses Perceval's deterministic SLOS backend for the authorized small-n
``g2=0``/source-once controls. Set ``--pcvl-path`` to an isolated writable
Perceval persistence directory, for example ``$env:TEMP\\merlin-v4-physical``
in PowerShell. No ring deployment is attempted: the command exits non-zero
while any physical control is FAIL.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import platform
import subprocess
import tempfile
from typing import Any

from merlin_iqp.deploy import direct_fock_cp_reference, ideal_iqp_distribution


ETA = 0.9


def _tvd(left: dict[str, float], right: dict[str, float]) -> float:
    keys = set(left) | set(right)
    return float(0.5 * sum(abs(left.get(key, 0.0) - right.get(key, 0.0)) for key in keys))


def _status(*statuses: str) -> str:
    normalized = {value.upper() for value in statuses}
    if "FAIL" in normalized:
        return "FAIL"
    if "INCONCLUSIVE" in normalized:
        return "INCONCLUSIVE"
    return "PASS"


def _repo_commit() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], check=True, capture_output=True, text=True
        ).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        return "unavailable"


def _result_record(result: Any) -> dict[str, Any]:
    return {
        "status": result.status,
        "distribution": result.distribution,
        "accepted_mass": result.accepted_mass,
        "rejected_mass": result.rejected_mass,
        "diagnostics": result.diagnostics,
    }


def _control(control_id: str, n: int, singles: list[float], pairs: list[tuple[int, int, float]]) -> dict[str, Any]:
    final = direct_fock_cp_reference(n, singles, pairs, eta=ETA, projection="final_only")
    intermediate = direct_fock_cp_reference(n, singles, pairs, eta=ETA, projection="intermediate")
    # The independent reference takes the raw single and pair terms.  Folded
    # singles are only the compiled physical implementation detail and would
    # silently omit the pair interaction from this comparison.
    analytic = ideal_iqp_distribution(n, singles, pairs)
    eta_consistent = all(
        result.accepted_mass is not None
        and result.diagnostics.get("eta") == ETA
        and result.accepted_mass == result.diagnostics.get("raw_source_acceptance", 0.0) * ETA**n
        for result in (final, intermediate)
    )
    projection_valid = (
        final.status == "PASS"
        and intermediate.status == "PASS"
        and final.accepted_mass is not None
        and intermediate.accepted_mass is not None
        and set(final.distribution) == set(intermediate.distribution)
        and eta_consistent
    )
    projection_comparison: dict[str, Any] = {
        "valid": projection_valid,
        "reason": "both direct projections completed with matching logical support and eta-scaled mass"
        if projection_valid
        else "comparison unavailable because one projection did not complete, supports differ, or eta scaling is inconsistent",
        "eta": ETA,
        "conditional_distribution_valid": projection_valid,
        "absolute_mass_valid": projection_valid,
    }
    if projection_valid:
        projection_comparison["conditional_tvd_final_vs_intermediate"] = _tvd(
            final.distribution, intermediate.distribution
        )
        projection_comparison["accepted_mass_delta"] = float(
            abs(float(final.accepted_mass) - float(intermediate.accepted_mass))
        )
        projection_comparison["raw_source_acceptance_delta"] = float(
            abs(
                float(final.diagnostics["raw_source_acceptance"])
                - float(intermediate.diagnostics["raw_source_acceptance"])
            )
        )
    direct_status = _status(final.status, intermediate.status)
    if not projection_valid:
        # A completed direct call is not sufficient evidence when the two
        # projection paths did not produce a comparable absolute instrument.
        # Keep this aggregate fail-closed instead of allowing two weak PASS
        # records to certify a broken projection contract.
        pair_status = "INCONCLUSIVE" if direct_status == "INCONCLUSIVE" else "FAIL"
    elif direct_status != "PASS":
        pair_status = direct_status
    else:
        pair_status = "PASS" if _tvd(final.distribution, analytic) <= 1e-12 else "FAIL"
    return {
        "id": control_id,
        "n": n,
        "singles": singles,
        "pairs": [{"i": i, "j": j, "theta": theta} for i, j, theta in pairs],
        "eta": ETA,
        "source_model": "fixed_photon_g2_0",
        "source_once": True,
        "analytic": analytic,
        "final_only": _result_record(final),
        "intermediate": _result_record(intermediate),
        "projection_comparison": projection_comparison,
        "conditional_tvd_direct_final_vs_analytic": _tvd(final.distribution, analytic)
        if final.status == "PASS"
        else None,
        "status": pair_status,
    }


def build_manifest() -> dict[str, Any]:
    controls = [
        _control("no_gate_n2", 2, [0.17, -0.29], []),
        _control("single_gate_bystander_n3", 3, [0.17, -0.29, 0.31], [(0, 2, 0.30)]),
        _control("shared_gate_n3", 3, [0.17, -0.24, 0.36], [(0, 1, 0.20), (1, 2, 0.30)]),
    ]
    manifest: dict[str, Any] = {
        "schema_version": "v4_tcdp.physical_controls.v2",
        "status": _status(*(control["status"] for control in controls)),
        "backend": "Perceval SLOS direct full-Fock",
        "source_model": "fixed_photon_g2_0",
        "controls": controls,
        "provenance": {
            "repo_commit": _repo_commit(),
            "python": platform.python_version(),
            "platform": platform.platform(),
            "pcvl_persistent_path": os.environ.get("PCVL_PERSISTENT_PATH", "unset"),
        },
    }
    payload = json.dumps(manifest, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    manifest["payload_sha256"] = hashlib.sha256(payload).hexdigest()
    return manifest


def _write_immutable_manifest(path: Path, manifest: dict[str, Any]) -> None:
    """Publish a physical manifest once and reject incompatible reuse."""

    encoded = json.dumps(manifest, indent=2, sort_keys=True, allow_nan=False) + "\n"
    if path.exists():
        try:
            existing = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            raise FileExistsError(f"existing physical manifest is unreadable: {path}") from error
        if existing != manifest:
            raise FileExistsError(f"incompatible physical manifest already exists: {path}")
        return
    temporary: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", dir=path.parent, prefix=f".{path.name}.", suffix=".tmp", delete=False
        ) as handle:
            handle.write(encoded)
            temporary = Path(handle.name)
        os.rename(temporary, path)
    except FileExistsError:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        if path.is_file() and json.loads(path.read_text(encoding="utf-8")) == manifest:
            return
        raise
    except Exception:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
        raise


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/v4_tcdp/deploy/physical_control_manifest.json"),
        help="manifest path; defaults to the committed v4_tcdp namespace",
    )
    parser.add_argument(
        "--pcvl-path",
        type=Path,
        help="isolated writable Perceval persistence directory, e.g. $env:TEMP\\merlin-v4-physical",
    )
    args = parser.parse_args()
    if args.pcvl_path is not None:
        args.pcvl_path.mkdir(parents=True, exist_ok=True)
        os.environ["PCVL_PERSISTENT_PATH"] = str(args.pcvl_path.resolve())
    manifest = build_manifest()
    args.output.parent.mkdir(parents=True, exist_ok=True)
    _write_immutable_manifest(args.output, manifest)
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0 if manifest["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
