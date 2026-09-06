"""Six defect reproductions at 8f1298f; not acceptance tests.

Only temporary fixtures under .pytest_cache are written. Existing source,
canonical results, and the real sibling checkout are read-only.
"""
from dataclasses import replace
import json
from pathlib import Path
import subprocess
import sys
import tempfile
from unittest.mock import patch

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path[:0] = [str(ROOT), str(ROOT / "src")]
from merlin_iqp.classical import ExactProbabilities, IQPModel, Trainer
from merlin_iqp.classical.checkpoint import save_checkpoint
from merlin_iqp.deploy import apply_compiled_density
from merlin_iqp.experiments.nat import run_nat
from merlin_iqp.experiments.rings import resolve_config, train_rings, write_run_artifacts
from merlin_iqp.experiments.sibling_import import git_source_identity
from scripts.v4_tcdp.replay_sibling import replay_export


def main():
    (ROOT / ".pytest_cache").mkdir(exist_ok=True)
    root = Path(tempfile.mkdtemp(prefix="third-repair-probes-", dir=ROOT / ".pytest_cache"))
    results = {}

    target3 = ExactProbabilities(np.arange(1, 9) / 36)
    pairs = [(1, 2), (0, 1)]
    options = dict(n=3, steps=0, singles=[.2, .3, .5])
    sequence = run_nat(target3, pairs, pair_keys=[1, 20], **options)
    mapping = run_nat(target3, pairs, pair_keys={(1, 2): 1, (0, 1): 20}, **options)
    def vector(run):
        return np.array([v for _, v in sorted(apply_compiled_density(run.final_compiled)[0].items())])
    tvd = float(.5 * abs(vector(sequence) - vector(mapping)).sum())
    assert tvd > .2
    results["T01"] = {"sequence_mapping_tvd": tvd, "sequence_keys": sequence.initial_pair_keys,
                      "mapping_keys": mapping.initial_pair_keys}

    target2 = ExactProbabilities(np.array([.1, .2, .3, .4]))
    G = np.eye(2, dtype=np.uint8)
    source_trainer = Trainer(IQPModel(G, [.2, .3]), target2)
    source_trainer.run(3)
    checkpoint = source_trainer.checkpoint()
    path = root / "bad.npz"
    save_checkpoint(replace(checkpoint, optimizer_state={"lr": .05}), path, generator=G)
    resumed = Trainer(IQPModel(G, [.7, .8]), target2)
    resumed.run(1)
    before = resumed.model.theta.copy()
    try:
        resumed.resume(path)
    except ValueError:
        pass
    else:
        raise AssertionError("Expected the repaired missing-state rejection")
    assert not np.array_equal(resumed.model.theta, before) and resumed.step == 3
    state = dict(checkpoint.optimizer_state)
    state["v"] = [-1., -1.]
    save_checkpoint(replace(checkpoint, optimizer_state=state), path, generator=G)
    resumed.resume(path)
    assert np.any(resumed._v < 0)
    results["T02"] = {"rejected_resume_mutated_trainer": True, "negative_second_moments_admitted": True}

    source = root / "source"
    (source / "src/iqp_bp").mkdir(parents=True)
    module = source / "src/iqp_bp/model_\u00e9.py"
    module.write_text("x = 1\n", encoding="utf-8")
    def git(*args):
        return subprocess.run(["git", "-C", str(source), *args], check=True,
                              capture_output=True, text=True).stdout
    git("init")
    git("add", ".")
    git("-c", "user.name=Audit", "-c", "user.email=audit@example.invalid", "commit", "-m", "fixture")
    clean = git_source_identity(source, include_paths=("src/iqp_bp",))
    module.write_text("x = 2\n", encoding="utf-8")
    dirty = git_source_identity(source, include_paths=("src/iqp_bp",))
    assert git("status", "--short") and not dirty["dirty"]
    assert dirty["tree_identity"] == clean["tree_identity"]
    real_run = subprocess.run
    def status_failure(args, **kwargs):
        if args[:1] == ["git"] and "status" in args:
            raise subprocess.CalledProcessError(128, args)
        return real_run(args, **kwargs)
    with patch("subprocess.run", side_effect=status_failure):
        failed = git_source_identity(source, include_paths=("src/iqp_bp",))
    assert not failed["dirty"] and failed["tree_identity"] == clean["tree_identity"]
    results["T03"] = {"quoted_edit_reported_clean": True, "status_failure_reported_clean": True}

    run = train_rings(resolve_config("rings_hamming", n=4, seed=0, steps=0))
    paths = write_run_artifacts(run, root / "rings")
    summary = json.loads(paths["summary"].read_text())
    summary["metrics"] = {"tvd_train": -999}
    summary["photonic_evaluation"] = {"status": "PASS"}
    paths["summary"].write_text(json.dumps(summary), encoding="utf-8")
    write_run_artifacts(run, root / "rings")
    assert json.loads(paths["summary"].read_text())["metrics"]["tvd_train"] == -999
    results["T04"] = {"false_summary_metrics_and_physical_pass_preserved": True}

    checkpoint_path = source / "results/step_0001.npz"
    checkpoint_path.parent.mkdir()
    np.savez(checkpoint_path, G=np.array([[1., 0], [0, 1], [1.5, 1]]),
             theta=np.array([.1, .2, .3]), step=np.array(1), loss=np.array(float("nan")))
    identity = git_source_identity(source, include_paths=("src", "configs", "pyproject.toml", "setup.py", "README.md"))
    manifest = {"schema_version": "v4_tcdp.sibling_export_manifest.v1", "copy_performed": False,
                "source_id": "probe:config", "source_commit": identity["observed_commit"],
                "source_tree_identity": identity["tree_identity"], "requested_pinned_commit": identity["observed_commit"],
                "result_evidence": ["results/step_0001.npz"],
                "config": {"content": {"kernel": {"type": "gaussian", "bandwidth": [1.]}}}}
    manifest_path = root / "export.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    replay = replay_export(manifest_path, source, root / "replayed")
    assert replay["status"] == "adapted_reproduction" and np.isnan(replay["checkpoint"]["source_loss"])
    emitted = Path(replay["namespace"]["destination"]) / "manifest.json"
    assert "NaN" in emitted.read_text()
    results["T05"] = {"nonbinary_generator_replayed": True, "nonstandard_nan_json_emitted": True}

    canonical = ROOT / "results/v4_tcdp/nat/n4_seed0_primary-warm-start.json"
    record = json.loads(canonical.read_text())
    assert record["pair_moves"] == 3 and record["budgets"]["pair_moves"] == 163
    results["T06"] = {"top_level_pair_moves": record["pair_moves"],
                      "accepted_move_counter": record["budgets"]["pair_moves"]}
    print(json.dumps(results, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
