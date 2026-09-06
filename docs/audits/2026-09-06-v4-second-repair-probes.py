"""Read-only implementation audit; all generated fixtures stay in .pytest_cache.

These assertions reproduce defects at d16d9cc; after repairs, convert them to
rejection/integrity regressions. They deliberately do not certify acceptance.
"""
from dataclasses import replace
import json
from pathlib import Path
import subprocess
import sys
import tempfile

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from merlin_iqp.classical import ExactProbabilities, IQPModel, Trainer
from merlin_iqp.classical.checkpoint import save_checkpoint
from merlin_iqp.classical.contracts import DatasetBundle
from merlin_iqp.experiments.rings import resolve_config, train_rings, write_run_artifacts
from merlin_iqp.experiments.sibling_import import git_source_identity


def main():
    (ROOT / ".pytest_cache").mkdir(exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix="second-repair-probes-", dir=ROOT / ".pytest_cache"))
    results = {}
    source = root / "source"
    (source / "src/iqp_bp").mkdir(parents=True)
    path = source / "src/iqp_bp/model.py"
    path.write_text("original = 1\n")

    def git(*args):
        return subprocess.run(["git", "-C", str(source), *args], check=True,
                              capture_output=True, text=True).stdout

    git("init")
    git("add", ".")
    git("-c", "user.name=Audit", "-c", "user.email=audit@example.invalid",
        "commit", "-m", "Isolated audit fixture")
    before = git_source_identity(source, include_paths=("src/iqp_bp",))
    path.write_text("modified = 2\n")
    after = git_source_identity(source, include_paths=("src/iqp_bp",))
    assert git("status", "--short").startswith(" M ")
    assert not after["dirty"] and before["tree_identity"] == after["tree_identity"]
    results["S01"] = {"raw_status": git("status", "--short"), "reported_dirty": after["dirty"],
                      "same_tree_identity": True}

    x = np.zeros((256, 6), dtype=np.uint8)
    y = x.copy()
    y[100, 2] = 1
    args = dict(schema_version="v1", dataset_id="fixture", n=6, representation="samples")
    a, b = DatasetBundle(train=x, **args), DatasetBundle(train=y, **args)
    assert not np.array_equal(x, y) and a.dataset_hash == b.dataset_hash
    results["S02"] = {"different_samples_same_dataset_hash": True}

    target = ExactProbabilities(np.array([.1, .2, .3, .4]))
    trainer = Trainer(IQPModel(np.eye(2, dtype=np.uint8), np.array([.2, .3])), target)
    trainer.run(3)
    checkpoint = trainer.checkpoint()
    valid, missing, nonfinite = root / "valid.npz", root / "missing.npz", root / "nonfinite.npz"
    save_checkpoint(checkpoint, valid, generator=trainer.model.G)
    save_checkpoint(replace(checkpoint, optimizer_state={"lr": .05}), missing, generator=trainer.model.G)
    a, b = Trainer.from_checkpoint(valid, target), Trainer.from_checkpoint(missing, target)
    a.run(1)
    b.run(1)
    error = float(np.max(abs(a.model.theta - b.model.theta)))
    assert error > 1e-4
    save_checkpoint(replace(checkpoint, loss_history=(float("nan"),) * 4), nonfinite, generator=trainer.model.G)
    assert np.isnan(Trainer.from_checkpoint(nonfinite, target).run(0)["final_loss"])
    results["S03"] = {"missing_adam_state_accepted": True, "next_theta_max_error": error,
                      "nonfinite_loss_history_accepted": True}

    r0 = train_rings(resolve_config("rings_hamming", n=4, seed=0, steps=0))
    r1 = train_rings(resolve_config("rings_hamming", n=4, seed=1, steps=0))
    output = root / "rings"
    write_run_artifacts(r0, output)
    write_run_artifacts(r1, output)
    try:
        write_run_artifacts(r0, output)
    except FileExistsError:
        results["S04"] = {"identical_run_rejected_after_second_seed": True}
    else:
        raise AssertionError("S04 no longer reproduces")

    paths = write_run_artifacts(r0, root / "missing-ring")
    paths["run"].unlink()
    returned = write_run_artifacts(r0, root / "missing-ring")
    assert not returned["run"].exists()
    results["S05"] = {"writer_returns_success_for_missing_run_npz": True}
    print(json.dumps(results, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
