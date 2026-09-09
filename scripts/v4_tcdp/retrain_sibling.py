"""Run the sibling training-smoke source trainer into an isolated output tree.

The sibling checkout is read-only input. This deliberately smoke-only adapter
admits one exact, exported source configuration, imports the trainer in an
isolated context, redirects generated output outside the sibling checkout, and
compares every recorded theta/loss row with the source trajectory.
"""

from __future__ import annotations

import argparse
import copy
import hashlib
import importlib
import importlib.metadata
import json
import platform
import sys
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Iterator

import numpy as np

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "src"))

from merlin_iqp.experiments.sibling_import import git_source_identity  # noqa: E402

EXPORT_MANIFEST_PATH = (
    REPO_ROOT
    / "results"
    / "v4_tcdp"
    / "sibling"
    / "training_smoke_configs_experiments_training_smoke_yaml"
    / "manifest.json"
)
SUPPORTED_SOURCE_ID = "training_smoke:configs/experiments/training_smoke.yaml"
SUPPORTED_CONFIG_RELATIVE = Path("configs/experiments/training_smoke.yaml")
TRAJECTORY_TOLERANCE = 1e-12


def _parse_json_object(line: str, path: Path) -> dict[str, object]:
    value = json.loads(line)
    if not isinstance(value, dict):
        raise ValueError(f"JSONL row in {path} is not an object")
    return value


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    return [
        _parse_json_object(line, path)
        for line in path.read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _hash_tree(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(
        path
        for path in root.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
    ):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return digest.hexdigest()


def _resolve_source_path(source_root: Path, value: str) -> Path:
    candidate = Path(value)
    return candidate if candidate.is_absolute() else source_root / candidate


def _is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
    except ValueError:
        return False
    return True


def _require_outside_sibling(output_root: Path, sibling_root: Path) -> None:
    if _is_within(output_root, sibling_root):
        raise ValueError(
            f"retraining output must be outside sibling checkout: {output_root}"
        )


def _load_export_manifest() -> dict[str, Any]:
    try:
        value = json.loads(EXPORT_MANIFEST_PATH.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise FileNotFoundError(
            f"exported training_smoke manifest is missing: {EXPORT_MANIFEST_PATH}"
        ) from exc
    if not isinstance(value, dict):
        raise ValueError("exported training_smoke manifest is not an object")
    return value


def _validate_supported_config(
    config_path: Path,
    sibling_root: Path,
    exported: dict[str, Any],
) -> tuple[dict[str, Any], str]:
    """Admit only the exact config represented by the exported smoke manifest."""

    if exported.get("source_id") != SUPPORTED_SOURCE_ID:
        raise ValueError(
            "exported manifest is not the supported training_smoke source: "
            f"{exported.get('source_id')!r}"
        )
    config_record = exported.get("config")
    if not isinstance(config_record, dict):
        raise ValueError("exported training_smoke manifest has no config record")
    expected_hash = config_record.get("sha256")
    expected_path = (sibling_root / SUPPORTED_CONFIG_RELATIVE).resolve()
    if config_path != expected_path:
        raise ValueError(
            "unsupported config for this smoke-only adapter; expected the exact "
            f"source config {expected_path}, got {config_path}"
        )
    if not config_path.is_file():
        raise FileNotFoundError(f"source config is missing: {config_path}")
    observed_hash = _sha256(config_path)
    if not isinstance(expected_hash, str) or observed_hash != expected_hash:
        raise ValueError(
            "source config hash does not match the exported training_smoke "
            f"manifest: expected {expected_hash!r}, observed {observed_hash}"
        )
    content = config_record.get("content")
    if not isinstance(content, dict):
        raise ValueError("exported training_smoke manifest has no resolved config content")
    required = {
        ("experiment", "name"): "training_smoke",
        ("circuit", "family"): "product_state",
        ("circuit", "n_qubits"): [6],
        ("kernel", "type"): "gaussian",
        ("dataset", "type"): "product_bernoulli",
        ("dataset", "n_samples"): 256,
        ("training", "optimizer"): "sgd",
        ("training", "lr"): 0.05,
        ("training", "num_steps"): 4,
    }
    for path, expected in required.items():
        current: Any = content
        for key in path:
            if not isinstance(current, dict) or key not in current:
                raise ValueError(f"exported config is missing required field {'.'.join(path)}")
            current = current[key]
        if current != expected:
            raise ValueError(
                f"unsupported training_smoke config field {'.'.join(path)}: "
                f"expected {expected!r}, got {current!r}"
            )
    return copy.deepcopy(content), observed_hash


def _require_source_identity(identity: dict[str, Any], exported: dict[str, Any]) -> None:
    required_keys = ("observed_commit", "tree_identity", "dirty", "tree_identity_kind")
    missing = [key for key in required_keys if key not in identity]
    if missing or not identity.get("observed_commit") or not identity.get("tree_identity"):
        raise ValueError(
            "sibling source identity could not be verified; missing Git/source "
            f"verification fields: {missing or ['commit_or_tree_identity']}"
        )
    if identity.get("dirty"):
        raise ValueError("sibling source checkout is dirty; refusing retraining")
    if exported.get("source_commit") != identity.get("observed_commit"):
        raise ValueError("sibling source commit does not match the exported manifest")
    if exported.get("source_tree_identity") != identity.get("tree_identity"):
        raise ValueError("sibling source tree identity does not match the exported manifest")
    if exported.get("source_dirty") is not False:
        raise ValueError("exported training_smoke manifest does not certify a clean source")


def _environment() -> dict[str, Any]:
    versions: dict[str, str | None] = {}
    for package in ("numpy", "scipy", "torch", "pyyaml"):
        try:
            versions[package] = importlib.metadata.version(package)
        except importlib.metadata.PackageNotFoundError:
            versions[package] = None
    return {
        "python": sys.version,
        "executable": sys.executable,
        "platform": platform.platform(),
        "numpy_runtime": np.__version__,
        "packages": versions,
    }


def _require_real_yaml() -> object:
    """Require the installed PyYAML module used by the sibling source."""

    try:
        yaml = importlib.import_module("yaml")
    except ModuleNotFoundError as exc:
        raise RuntimeError(
            "source retraining requires the real PyYAML dependency; refusing a yaml stub"
        ) from exc
    origin = getattr(yaml, "__file__", None)
    if not isinstance(origin, str) or not Path(origin).is_file():
        raise RuntimeError(
            "source retraining imported yaml without a file-backed PyYAML module; "
            "refusing a yaml stub"
        )
    if not callable(getattr(yaml, "safe_load", None)):
        raise RuntimeError("source retraining requires yaml.safe_load from PyYAML")
    return yaml


def _training_smoke_dataset_hash(metadata: dict[str, Any]) -> str:
    expected = {"type": "product_bernoulli", "n_samples": 256, "seed": 1230519654}
    if metadata != expected:
        raise ValueError(f"unexpected training_smoke dataset metadata: {metadata!r}")
    data = np.random.default_rng(metadata["seed"]).integers(
        0, 2, size=(metadata["n_samples"], 6), dtype=np.uint8
    )
    return hashlib.sha256(np.ascontiguousarray(data).tobytes()).hexdigest()


def _trajectory_values(
    rows: list[dict[str, object]],
    *,
    label: str,
    expected_step_ids: tuple[int, ...],
    expected_theta_shape: tuple[int, ...],
) -> list[tuple[int, np.ndarray, float]]:
    if not rows:
        raise ValueError(f"{label} trajectory is empty")
    values: list[tuple[int, np.ndarray, float]] = []
    observed_steps: list[int] = []
    for index, row in enumerate(rows):
        if "step" not in row or "theta" not in row or "loss" not in row:
            raise ValueError(f"{label} trajectory row {index} is missing step/theta/loss")
        step = row["step"]
        if isinstance(step, bool) or not isinstance(step, int):
            raise ValueError(f"{label} trajectory row {index} has a non-integer step: {step!r}")
        try:
            theta = np.asarray(row["theta"], dtype=np.float64)
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{label} trajectory row {index} theta is not numeric") from exc
        if theta.shape != expected_theta_shape:
            raise ValueError(
                f"{label} trajectory row {index} theta shape mismatch: "
                f"expected {expected_theta_shape}, got {theta.shape}"
            )
        try:
            loss = float(row["loss"])
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{label} trajectory row {index} loss is not numeric") from exc
        if not np.all(np.isfinite(theta)) or not np.isfinite(loss):
            raise ValueError(f"{label} trajectory row {index} contains NaN or infinity")
        observed_steps.append(step)
        values.append((step, theta, loss))
    if tuple(observed_steps) != expected_step_ids:
        raise ValueError(
            f"{label} trajectory step IDs mismatch: expected {list(expected_step_ids)}, "
            f"got {observed_steps}"
        )
    return values


def _compare_trajectories(
    source_rows: list[dict[str, object]],
    replay_rows: list[dict[str, object]],
    *,
    expected_step_ids: tuple[int, ...],
    expected_theta_shape: tuple[int, ...],
) -> dict[str, object]:
    source = _trajectory_values(
        source_rows,
        label="source",
        expected_step_ids=expected_step_ids,
        expected_theta_shape=expected_theta_shape,
    )
    replay = _trajectory_values(
        replay_rows,
        label="retrained",
        expected_step_ids=expected_step_ids,
        expected_theta_shape=expected_theta_shape,
    )
    if len(source) != len(replay):
        raise ValueError(
            f"trajectory length mismatch: source={len(source)}, retrained={len(replay)}"
        )
    max_theta_error = 0.0
    max_loss_error = 0.0
    for (source_step, source_theta, source_loss), (
        replay_step,
        replay_theta,
        replay_loss,
    ) in zip(source, replay, strict=True):
        if source_step != replay_step:
            raise ValueError(f"trajectory step mismatch: {source_step} != {replay_step}")
        theta_error = float(np.max(np.abs(source_theta - replay_theta)))
        loss_error = abs(source_loss - replay_loss)
        max_theta_error = max(max_theta_error, theta_error)
        max_loss_error = max(max_loss_error, loss_error)
    status = (
        "PASS"
        if max_theta_error <= TRAJECTORY_TOLERANCE
        and max_loss_error <= TRAJECTORY_TOLERANCE
        else "FAIL"
    )
    interpretation = (
        "Source and retrained trajectories matched within fixed 1e-12 tolerance."
        if status == "PASS"
        else "Source and retrained trajectories differed beyond fixed 1e-12 tolerance."
    )
    return {
        "status": status,
        "trajectory_rows": len(source),
        "max_theta_abs_error": max_theta_error,
        "max_loss_abs_error": max_loss_error,
        "interpretation": interpretation,
    }


def _validate_summary_contract(
    summary: dict[str, object], config: dict[str, Any], *, label: str
) -> None:
    expected = {
        "family": config["circuit"]["family"],
        "kernel": config["kernel"]["type"],
        "init": config["init"]["scheme"],
        "n": config["circuit"]["n_qubits"][0],
        "dataset_type": config["dataset"]["type"],
        "bandwidth": config["kernel"]["bandwidth"][0],
        "small_angle_std": config["init"]["small_angle"]["std"][0],
    }
    for key, value in expected.items():
        if summary.get(key) != value:
            raise ValueError(
                f"{label} summary model contract mismatch for {key}: "
                f"expected {value!r}, got {summary.get(key)!r}"
            )
    metadata = summary.get("dataset_metadata")
    if not isinstance(metadata, dict):
        raise ValueError(f"{label} summary is missing dataset metadata")
    _training_smoke_dataset_hash(metadata)


@contextmanager
def _isolated_source_import(sibling_root: Path) -> Iterator[None]:
    """Temporarily expose only the sibling source package to the importer."""

    source_root = (sibling_root / "src").resolve()
    if not source_root.is_dir():
        raise FileNotFoundError(f"sibling source directory is missing: {source_root}")
    for name, module in list(sys.modules.items()):
        if name == "iqp_bp" or name.startswith("iqp_bp."):
            origin = getattr(module, "__file__", None)
            if origin and not _is_within(Path(origin), source_root):
                raise ValueError(
                    f"already imported sibling module has the wrong origin: {name} -> {origin}"
                )

    real_yaml = _require_real_yaml()
    saved_path = list(sys.path)
    saved_modules = {
        name: module
        for name, module in sys.modules.items()
        if name == "iqp_bp" or name.startswith("iqp_bp.") or name == "yaml"
    }
    saved_modules.setdefault("yaml", real_yaml)
    for name in list(saved_modules):
        sys.modules.pop(name, None)
    sys.path.insert(0, str(source_root))
    sys.modules["yaml"] = real_yaml
    try:
        yield
    finally:
        sys.path[:] = saved_path
        for name in list(sys.modules):
            if name == "iqp_bp" or name.startswith("iqp_bp.") or name == "yaml":
                sys.modules.pop(name, None)
        sys.modules.update(saved_modules)


def _execute_source_training(
    sibling_root: Path, config: dict[str, Any]
) -> tuple[list[dict[str, Any]], str, dict[str, Any]]:
    with _isolated_source_import(sibling_root):
        module = importlib.import_module("iqp_bp.experiments.run_training")
        origin = getattr(module, "__file__", None)
        if not origin or not _is_within(Path(origin), sibling_root / "src"):
            raise ValueError(
                "imported sibling trainer has the wrong module origin: "
                f"{origin!r}"
            )
        run = getattr(module, "run", None)
        if not callable(run):
            raise ValueError("imported sibling trainer has no callable run")
        summaries = run(config)
        if not isinstance(summaries, list) or not all(
            isinstance(summary, dict) for summary in summaries
        ):
            raise ValueError("sibling trainer returned an invalid summary collection")
        return summaries, str(Path(origin).resolve()), _environment()


def _load_registered_export(config_path: Path, sibling_root: Path) -> dict[str, Any]:
    """Load the inventory export that admits exactly ``config_path``."""

    relative = config_path.relative_to(sibling_root).as_posix()
    expected_suffix = f":{relative}"
    export_root = REPO_ROOT / "results" / "v4_tcdp" / "sibling"
    matches: list[dict[str, Any]] = []
    for path in sorted(export_root.glob("*/manifest.json")):
        value = json.loads(path.read_text(encoding="utf-8"))
        if (
            isinstance(value, dict)
            and value.get("source_id", "").endswith(expected_suffix)
            and value.get("config", {}).get("path")
        ):
            config_record = value["config"]
            if config_record.get("path") == str(config_path):
                matches.append(value)
    if len(matches) != 1:
        raise ValueError(
            f"expected one exported sibling manifest for {config_path}, got {len(matches)}"
        )
    return matches[0]


def _load_resolved_source_config(exported: dict[str, Any], sibling_root: Path) -> tuple[dict[str, Any], Path]:
    """Load the source runner's own merged config without parsing executable YAML."""

    candidates = [
        sibling_root / Path(value)
        for value in exported.get("result_evidence", [])
        if str(value).replace("\\", "/").endswith("/config.json")
    ]
    if len(candidates) != 1 or not candidates[0].is_file():
        raise FileNotFoundError(
            "registered source row requires exactly one available resolved config.json; "
            f"found {[str(path) for path in candidates]}"
        )
    path = candidates[0].resolve()
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"resolved source config is not an object: {path}")
    output_dir = value.get("experiment", {}).get("output_dir")
    if not isinstance(output_dir, str):
        raise ValueError(f"resolved source config has no experiment.output_dir: {path}")
    resolved_output = _resolve_source_path(sibling_root, output_dir).resolve()
    if not _is_within(resolved_output, sibling_root):
        raise ValueError(f"resolved source output is outside sibling checkout: {resolved_output}")
    return value, path


def _source_results_path(config: dict[str, Any], sibling_root: Path) -> Path:
    output_value = config["experiment"]["output_dir"]
    output_dir = _resolve_source_path(sibling_root, str(output_value)).resolve()
    path = output_dir / "results.jsonl"
    if not _is_within(path, sibling_root) or not path.is_file():
        raise FileNotFoundError(f"source result ledger is missing: {path}")
    return path


def _execute_source_dataset(
    sibling_root: Path, config: dict[str, Any], *, n: int, seed: int
) -> tuple[np.ndarray, dict[str, Any]]:
    """Regenerate one source dataset through the source package's factory."""

    with _isolated_source_import(sibling_root):
        module = importlib.import_module("iqp_bp.experiments.data_factory")
        make_dataset = getattr(module, "make_dataset", None)
        if not callable(make_dataset):
            raise ValueError("source data factory has no callable make_dataset")
        data, metadata = make_dataset(config["dataset"], n=n, seed=seed)
    data = np.asarray(data)
    if data.ndim != 2 or data.shape != (int(config["dataset"]["n_samples"]), n):
        raise ValueError(f"source data has unexpected shape: {data.shape}")
    if data.dtype.kind not in "biu" or not np.all(np.isin(data, (0, 1))):
        raise ValueError("source data factory returned a non-binary dataset")
    if not isinstance(metadata, dict):
        raise ValueError("source data factory returned invalid metadata")
    return data.astype(np.uint8, copy=False), metadata


def _source_cell_key(summary: dict[str, Any]) -> tuple[object, ...]:
    """Return the resolved setting identity used by source and retrained rows."""

    return tuple(
        (key, summary.get(key))
        for key in ("family", "kernel", "init", "n", "dataset_type", "bandwidth", "er_p_edge")
        if key in summary
    )


def _resolve_trajectory(root: Path, value: object, *, label: str, sibling_root: Path) -> Path:
    if not isinstance(value, str):
        raise ValueError(f"{label} summary is missing trajectory_path")
    path = Path(value)
    if not path.is_absolute():
        path = root / path
    path = path.resolve()
    if not _is_within(path, root) or _is_within(path, sibling_root) or not path.is_file():
        raise ValueError(f"{label} trajectory is missing or outside its output: {path}")
    return path


def run_registered_retraining(
    config_path: Path, sibling_root: Path, output_root: Path
) -> dict[str, object]:
    """Faithfully rerun a registered learned-distribution source config.

    The source package, data recipe, estimator mode, optimizer and all resolved
    settings are retained. Only the source runner's output directory changes so
    the sibling checkout remains read-only and historical results are untouched.
    """

    sibling_root = sibling_root.resolve()
    config_path = config_path.resolve()
    output_root = output_root.resolve()
    _require_outside_sibling(output_root, sibling_root)
    exported = _load_registered_export(config_path, sibling_root)
    config_record = exported.get("config")
    if not isinstance(config_record, dict):
        raise ValueError("registered export has no config record")
    config_hash = config_record.get("sha256")
    if not isinstance(config_hash, str) or _sha256(config_path) != config_hash:
        raise ValueError("requested source config hash does not match its inventory export")
    source_identity_before = git_source_identity(
        sibling_root,
        include_paths=("src", "configs", "pyproject.toml", "setup.py", "README.md"),
    )
    if source_identity_before.get("dirty"):
        raise ValueError("sibling source checkout is dirty; refusing source retraining")
    if exported.get("source_commit") != source_identity_before.get("observed_commit"):
        raise ValueError("registered source commit does not match observed sibling HEAD")
    if exported.get("source_tree_identity") != source_identity_before.get("tree_identity"):
        raise ValueError("registered source tree identity does not match observed sibling tree")

    source_config, resolved_config_path = _load_resolved_source_config(exported, sibling_root)
    source_results_path = _source_results_path(source_config, sibling_root)
    source_summaries = _read_jsonl(source_results_path)
    if not source_summaries:
        raise ValueError("source result ledger is empty")
    executed_config = copy.deepcopy(source_config)
    executed_config["experiment"] = copy.deepcopy(source_config["experiment"])
    executed_config["experiment"]["output_dir"] = str(output_root)
    if output_root.exists() and any(output_root.iterdir()):
        raise FileExistsError(f"retraining output already contains an artifact: {output_root}")
    summaries, module_origin, source_environment = _execute_source_training(
        sibling_root, executed_config
    )
    source_identity_after = git_source_identity(
        sibling_root,
        include_paths=("src", "configs", "pyproject.toml", "setup.py", "README.md"),
    )
    if source_identity_before != source_identity_after:
        raise ValueError("sibling source identity changed during retraining")
    retrained_by_key = {_source_cell_key(summary): summary for summary in summaries}
    if len(retrained_by_key) != len(summaries):
        raise ValueError("retrained source runner returned duplicate cell identities")

    source_code_hash = _hash_tree(sibling_root / "src" / "iqp_bp")
    cell_reports: list[dict[str, Any]] = []
    for source_summary in source_summaries:
        key = _source_cell_key(source_summary)
        retrained_summary = retrained_by_key.get(key)
        if retrained_summary is None:
            raise ValueError(f"source cell is missing from retrained output: {key!r}")
        n = int(source_summary["n"])
        source_trajectory = _resolve_trajectory(
            sibling_root, source_summary.get("trajectory_path"), label="source", sibling_root=sibling_root
        )
        retrained_trajectory = _resolve_trajectory(
            output_root, retrained_summary.get("trajectory_path"), label="retrained", sibling_root=sibling_root
        )
        written_steps = source_summary.get("written_steps")
        if not isinstance(written_steps, list) or not written_steps:
            raise ValueError(f"source cell has no complete written_steps: {key!r}")
        source_rows = _read_jsonl(source_trajectory)
        expected_shape = tuple(np.asarray(source_rows[0]["theta"], dtype=np.float64).shape)
        retrained_rows = _read_jsonl(retrained_trajectory)
        comparison = _compare_trajectories(
            source_rows,
            retrained_rows,
            expected_step_ids=tuple(int(step) for step in written_steps),
            expected_theta_shape=expected_shape,
        )
        metadata = source_summary.get("dataset_metadata")
        if not isinstance(metadata, dict) or not isinstance(metadata.get("seed"), int):
            raise ValueError(f"source cell has incomplete dataset metadata: {key!r}")
        data, regenerated_metadata = _execute_source_dataset(
            sibling_root, source_config, n=n, seed=int(metadata["seed"])
        )
        if regenerated_metadata != metadata:
            raise ValueError(f"source dataset metadata changed on regeneration: {key!r}")
        cell_slug = _slug("__".join(f"{name}_{value}" for name, value in key))
        cell_dir = output_root / "cells" / cell_slug
        cell_dir.mkdir(parents=True, exist_ok=True)
        data_path = cell_dir / "source_data.npy"
        np.save(data_path, data)
        cell_report = {
            **comparison,
            "command": [
                "venv/Scripts/python.exe",
                "scripts/v4_tcdp/retrain_sibling.py",
                "--sibling-root",
                str(sibling_root),
                "--config",
                str(config_path),
                "--output-root",
                str(output_root),
            ],
            "source_cell": {name: value for name, value in key},
            "source_summary_sha256": hashlib.sha256(
                json.dumps(source_summary, sort_keys=True, separators=(",", ":")).encode("utf-8")
            ).hexdigest(),
            "source_trajectory": str(source_trajectory),
            "retrained_trajectory": str(retrained_trajectory),
            "source_trajectory_sha256": _sha256(source_trajectory),
            "retrained_trajectory_sha256": _sha256(retrained_trajectory),
            "dataset_metadata": metadata,
            "dataset_sha256": hashlib.sha256(np.ascontiguousarray(data).tobytes()).hexdigest(),
            "dataset_artifact": str(data_path),
            "source_settings": {
                "optimizer": source_config["training"]["optimizer"],
                "learning_rate": source_config["training"]["lr"],
                "steps": source_config["training"]["num_steps"],
                "checkpoint_every": source_config["training"]["checkpoint_every"],
                "loss_mode": source_config["training"]["loss_mode"],
                "diagnostics": source_config["training"].get("diagnostics", {}),
            },
        }
        (cell_dir / "retraining_evidence.json").write_text(
            json.dumps(cell_report, indent=2, sort_keys=True, allow_nan=False) + "\n",
            encoding="utf-8",
        )
        cell_reports.append(cell_report)

    status = "PASS" if all(report["status"] == "PASS" for report in cell_reports) else "FAIL"
    report = {
        "schema_version": "v4_tcdp.sibling_retraining.v3",
        "status": status,
        "reproduction_kind": "faithful_source_retraining",
        "command": [
            "venv/Scripts/python.exe",
            "scripts/v4_tcdp/retrain_sibling.py",
            "--sibling-root",
            str(sibling_root),
            "--config",
            str(config_path),
            "--output-root",
            str(output_root),
        ],
        "source_id": exported.get("source_id"),
        "source_config": str(config_path),
        "source_config_sha256": config_hash,
        "resolved_source_config": str(resolved_config_path),
        "resolved_source_config_sha256": _sha256(resolved_config_path),
        "executed_output": str(output_root),
        "adaptation": {
            "changed_fields": ["experiment.output_dir"],
            "reason": "source runner output redirected outside the read-only sibling checkout",
        },
        "source_identity_before": source_identity_before,
        "source_identity_after": source_identity_after,
        "source_code_sha256": source_code_hash,
        "source_results": str(source_results_path),
        "source_results_sha256": _sha256(source_results_path),
        "imported_module_origin": module_origin,
        "environment": source_environment,
        "adapter_environment": _environment(),
        "unsafe_serialization_loaded": False,
        "cells": cell_reports,
    }
    output_root.mkdir(parents=True, exist_ok=True)
    report_path = output_root / "retraining_evidence.json"
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n", encoding="utf-8"
    )
    report["report_path"] = str(report_path)
    return report


def run_retraining(config_path: Path, sibling_root: Path, output_root: Path) -> dict[str, object]:
    sibling_root = sibling_root.resolve()
    config_path = config_path.resolve()
    output_root = output_root.resolve()
    _require_outside_sibling(output_root, sibling_root)
    exported = _load_export_manifest()
    source_config, source_config_hash = _validate_supported_config(
        config_path, sibling_root, exported
    )

    source_identity_before = git_source_identity(
        sibling_root,
        include_paths=("src/iqp_bp", "configs/experiments/training_smoke.yaml"),
    )
    _require_source_identity(source_identity_before, exported)
    source_results_path = sibling_root / "results" / "training_smoke" / "results.jsonl"
    if not source_results_path.is_file():
        raise FileNotFoundError(f"source training_smoke results are missing: {source_results_path}")
    source_summaries = _read_jsonl(source_results_path)
    matching = [summary for summary in source_summaries if summary.get("n") == 6]
    if len(matching) != 1:
        raise ValueError(
            f"training_smoke expected one n=6 source summary, got {len(matching)}"
        )
    source_summary = matching[0]
    _validate_summary_contract(source_summary, source_config, label="source")
    source_trajectory_value = source_summary.get("trajectory_path")
    if not isinstance(source_trajectory_value, str):
        raise ValueError("source summary is missing trajectory_path")
    source_trajectory = _resolve_source_path(sibling_root, source_trajectory_value).resolve()
    if not _is_within(source_trajectory, sibling_root):
        raise ValueError("source trajectory resolves outside the sibling checkout")
    if not source_trajectory.is_file():
        raise FileNotFoundError(f"source trajectory is missing: {source_trajectory}")
    source_rows = _read_jsonl(source_trajectory)

    written_steps = source_summary.get("written_steps")
    num_steps = source_config["training"]["num_steps"]
    if not isinstance(written_steps, list) or written_steps != list(range(num_steps + 1)):
        raise ValueError(
            "source summary has an unexpected step contract: "
            f"expected {list(range(num_steps + 1))}, got {written_steps!r}"
        )
    expected_step_ids = tuple(written_steps)
    expected_theta_shape = (int(source_config["circuit"]["n_qubits"][0]),)
    _trajectory_values(
        source_rows,
        label="source",
        expected_step_ids=expected_step_ids,
        expected_theta_shape=expected_theta_shape,
    )

    executed_config = copy.deepcopy(source_config)
    executed_config["circuit"]["n_generators"] = "n"
    executed_config["experiment"]["output_dir"] = str(output_root)
    summaries, module_origin, source_environment = _execute_source_training(
        sibling_root, executed_config
    )
    source_identity_after = git_source_identity(
        sibling_root,
        include_paths=("src/iqp_bp", "configs/experiments/training_smoke.yaml"),
    )
    sibling_unchanged = source_identity_before == source_identity_after
    if not sibling_unchanged:
        raise ValueError("sibling source identity changed during retraining")
    if len(summaries) != 1:
        raise ValueError(f"training_smoke expected one resolved run, got {len(summaries)}")
    retrained_summary = summaries[0]
    _validate_summary_contract(retrained_summary, source_config, label="retrained")
    if retrained_summary.get("dataset_metadata") != source_summary.get("dataset_metadata"):
        raise ValueError("source and retrained dataset metadata do not match")
    replay_trajectory_value = retrained_summary.get("trajectory_path")
    if not isinstance(replay_trajectory_value, str):
        raise ValueError("retrained summary is missing trajectory_path")
    replay_trajectory = Path(replay_trajectory_value)
    if not replay_trajectory.is_absolute():
        replay_trajectory = output_root / replay_trajectory
    replay_trajectory = replay_trajectory.resolve()
    if not _is_within(replay_trajectory, output_root):
        raise ValueError("retrained trajectory resolves outside the requested output")
    if _is_within(replay_trajectory, sibling_root):
        raise ValueError("retrained trajectory resolves inside the sibling checkout")
    if not replay_trajectory.is_file():
        raise FileNotFoundError(f"retrained trajectory is missing: {replay_trajectory}")
    replay_rows = _read_jsonl(replay_trajectory)
    comparison = _compare_trajectories(
        source_rows,
        replay_rows,
        expected_step_ids=expected_step_ids,
        expected_theta_shape=expected_theta_shape,
    )

    dataset_metadata = source_summary["dataset_metadata"]
    if not isinstance(dataset_metadata, dict):
        raise ValueError("source summary dataset metadata is not an object")
    dataset_hash = _training_smoke_dataset_hash(dataset_metadata)
    source_code_hash = _hash_tree(sibling_root / "src" / "iqp_bp")
    report = {
        "schema_version": "v4_tcdp.sibling_retraining.v2",
        **comparison,
        "source_id": SUPPORTED_SOURCE_ID,
        "source_config": str(config_path),
        "source_config_sha256": source_config_hash,
        "resolved_config": {
            "path": str(config_path),
            "sha256": source_config_hash,
            "content": source_config,
        },
        "executed_config": executed_config,
        "adaptation": {
            "n_generators": "n",
            "output_dir": str(output_root),
            "reason": "source runner requires the symbolic generator-count formula and output redirection",
        },
        "source_results": str(source_results_path),
        "source_trajectory": str(source_trajectory),
        "retrained_output": str(output_root),
        "retrained_trajectory": str(replay_trajectory),
        "source_dataset_metadata": source_summary.get("dataset_metadata"),
        "retrained_dataset_metadata": retrained_summary.get("dataset_metadata"),
        "expected_step_ids": list(expected_step_ids),
        "expected_theta_shape": list(expected_theta_shape),
        "optimizer": {
            "name": source_config["training"]["optimizer"],
            "lr": source_config["training"]["lr"],
            "steps": source_config["training"]["num_steps"],
        },
        "source_identity_before": source_identity_before,
        "source_identity_after": source_identity_after,
        "sibling_unchanged_by_adapter": sibling_unchanged,
        "imported_module_origin": module_origin,
        "environment": source_environment,
        "numerical_library_provenance": {
            "adapter": _environment(),
            "source_trainer": source_environment,
        },
        "source_hashes": {
            "source_code_sha256": source_code_hash,
            "config_sha256": source_config_hash,
            "dataset_sha256": dataset_hash,
            "results_sha256": _sha256(source_results_path),
            "trajectory_sha256": _sha256(source_trajectory),
        },
        "source_code_sha256": source_code_hash,
        "source_dataset_sha256": dataset_hash,
        "source_trajectory_sha256": _sha256(source_trajectory),
        "retrained_trajectory_sha256": _sha256(replay_trajectory),
    }
    output_root.mkdir(parents=True, exist_ok=True)
    report_path = output_root / "retraining_evidence.json"
    report_path.write_text(
        json.dumps(report, indent=2, sort_keys=True, allow_nan=False) + "\n",
        encoding="utf-8",
    )
    report["report_path"] = str(report_path)
    return report


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--sibling-root", type=Path, default=Path(r"C:\Users\cuqui\iqp-mmd-barren-plateau")
    )
    parser.add_argument(
        "--config",
        type=Path,
        default=Path(r"C:\Users\cuqui\iqp-mmd-barren-plateau\configs\experiments\training_smoke.yaml"),
    )
    parser.add_argument(
        "--output-root",
        type=Path,
        default=REPO_ROOT / "results" / "v4_tcdp" / "sibling_retraining" / "training_smoke",
    )
    args = parser.parse_args()
    if args.config.resolve().name == "training_smoke.yaml":
        report = run_retraining(args.config, args.sibling_root, args.output_root)
    else:
        report = run_registered_retraining(args.config, args.sibling_root, args.output_root)
    print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
