"""Read-only checks of the bounded release's committed evidence; run from repo root."""
from pathlib import Path
import hashlib
import json
import subprocess
import sys

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from merlin_iqp.classical._validation import hash_array


def read(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    tracked = set(subprocess.check_output(
        ["git", "ls-files", "-z"], cwd=ROOT).decode().split("\0"))
    base = ROOT / "results/v4_tcdp"
    sibling = base / "sibling_comparisons/correction_20260910_v5"
    rings = base / "corrections_20260910/metrics_v5"
    files = [p for directory in (sibling, rings) for p in directory.rglob("*") if p.is_file()]
    physical = [base / "deploy" / name for name in (
        "physical_control_manifest_20260909_final3.json",
        "registered_v3_ring_photonic_spatial_n4_seed0_smoke_20260909_final3.json",
        "registered_v3_ring_photonic_hamming_n4_seed0_smoke_20260909_final3.json",
        "resource_budget_correction_20260910_final2.json")]
    assert all(p.relative_to(ROOT).as_posix() in tracked for p in files + physical)
    summary = read(sibling / "summary.json")
    assert len(summary["cells"]) == 8
    assert len(list(rings.glob("*.json"))) == 22
    rows = []
    hashes = 0
    ring_rows = []
    for path in sorted(rings.glob("*.json")):
        comparison = read(path)
        directory = base / "rings" / comparison["cell_id"].removesuffix("/matched_backends")
        for name in ("run.npz", "dataset.npz"):
            assert (directory / name).relative_to(ROOT).as_posix() in tracked
        with np.load(directory / "run.npz", allow_pickle=False) as run, np.load(directory / "dataset.npz", allow_pickle=False) as data:
            q, target = run["output_probabilities"], data["train_histogram"]
            metric = comparison["metrics"]["raw:numpy-iqp"]
            assert np.isclose(np.sum(q[target > 1e-6]), metric["support_validity"], atol=1e-12, rtol=0)
            assert np.isclose(np.abs(q-target).sum()/2, metric["tvd_to_target"], atol=1e-12, rtol=0)
            if "seed0" in comparison["cell_id"]:
                deployed = comparison["metrics"]["deployed:ideal-deployed-map"]
                ring_rows.append({"cell": comparison["cell_id"], "train_tvd": metric["tvd_to_target"], "test_tvd": float(np.abs(q-data["test_histogram"]).sum()/2), "support": metric["support_validity"], "deployed_tvd": deployed["tvd_to_target"], "expected_attempts_20000": 20000/deployed["acceptance_mass"]})
    for cell in summary["cells"]:
        # Recorded absolute producer paths are historical metadata, not read locations.
        directory = sibling / cell["directory"].replace("\\", "/").split("/")[-1]
        manifest = read(directory / "manifest.json")
        comparison = read(directory / "comparison.json")
        assert manifest["comparison"] == comparison
        for key, expected in manifest["artifact_hashes"].items():
            path = directory / manifest["artifacts"][key]
            actual = hash_array(np.load(path, allow_pickle=False)) if path.suffix == ".npy" else hashlib.sha256(path.read_bytes()).hexdigest()
            assert actual == expected, str(path)
            hashes += 1
        target = np.load(directory / "target.npy", allow_pickle=False)
        q = np.load(directory / "deployed.npy", allow_pickle=False)
        metric = comparison["metrics"]["deployed:ideal-deployed-map"]
        assert np.isclose(np.sum(q[target > 1e-6]), metric["support_validity"], atol=1e-12, rtol=0)
        assert np.isclose(np.abs(q-target).sum()/2, metric["tvd_to_target"], atol=1e-12, rtol=0)
        rows.append({"cell": comparison["cell_id"], "tvd": metric["tvd_to_target"], "support": metric["support_validity"], "expected_attempts_20000": 20000/metric["acceptance_mass"]})
    resource = read(physical[-1])
    for path, expected in resource["code_source"]["source_files_sha256"].items():
        blob = subprocess.check_output(["git", "show", f"HEAD:{path}"], cwd=ROOT)
        assert hashlib.sha256(blob).hexdigest() == expected, path
    print(json.dumps({"status": "PASS", "committed_evidence_files": len(files + physical), "sibling_payload_hashes": hashes, "ring_metrics": ring_rows, "sibling_metrics": rows}, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
