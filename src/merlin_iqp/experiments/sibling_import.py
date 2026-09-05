"""Read-only inventory and safe artifact boundary for the v4 sibling study.

The sibling repository is a provenance source, not an import dependency.  This
module deliberately performs no sibling imports, does not mutate the sibling,
and never deserializes Python objects.  It records references and hashes so a
later replay can make an explicit compatibility decision without fabricating a
missing dataset.
"""

from __future__ import annotations

import ast
import csv
import hashlib
import importlib.metadata
import json
import os
import platform
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Literal

import numpy as np

COMPATIBILITY_STATUSES = (
    "exact_reproduction",
    "adapted_reproduction",
    "reference_only",
    "blocked",
)
CompatibilityStatus = Literal[
    "exact_reproduction",
    "adapted_reproduction",
    "reference_only",
    "blocked",
]
SCHEMA_VERSION = "v4_tcdp.sibling_inventory.v1"
PINNED_SIBLING_COMMIT = "f6d6ebe87e4ee1de10893c6ea2f0ffa367493336"
_TEXT_SUFFIXES = {".py", ".yaml", ".yml", ".json", ".jsonl", ".md", ".toml", ".txt", ".csv"}
_SAFE_IMPORT_SUFFIXES = {".json", ".jsonl", ".yaml", ".yml", ".csv", ".npy", ".npz"}
_UNSAFE_SUFFIXES = {".pkl", ".pickle", ".joblib", ".pt", ".pth", ".dill"}
_KEYWORDS = (
    "gaussian", "bandwidth", "sigma", "marginal", "anticoncentration", "genomic",
    "mixture", "checkpoint", "dataset", "ising", "iqp", "hamming", "walsh",
)
_EXCLUDED_PARTS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", ".ruff_cache"}


def _path_string(path: Path) -> str:
    return str(path.resolve())


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git(root: Path, *args: str) -> str | None:
    try:
        completed = subprocess.run(
            ["git", "-C", str(root), *args],
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    return completed.stdout.strip()


def _git_status(root: Path) -> list[str]:
    value = _git(root, "status", "--short")
    return [] if value is None or not value else value.splitlines()


def _iter_files(root: Path) -> list[Path]:
    if not root.exists():
        return []
    return sorted(
        (
            path for path in root.rglob("*")
            if path.is_file() and not any(part in _EXCLUDED_PARTS for part in path.parts)
        ),
        key=lambda path: path.as_posix().lower(),
    )


def _relative(path: Path, root: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def _text(path: Path, limit: int = 2_000_000) -> str:
    if path.suffix.lower() not in _TEXT_SUFFIXES:
        return ""
    try:
        return path.read_text(encoding="utf-8", errors="replace")[:limit]
    except OSError:
        return ""


def _is_gaussian_related(path: Path, root: Path) -> tuple[bool, list[str]]:
    relative = _relative(path, root).lower()
    haystack = relative + "\n" + _text(path).lower()
    hits = sorted({keyword for keyword in _KEYWORDS if keyword in haystack})
    return bool(hits), hits


def _imports(path: Path) -> dict[str, Any]:
    source = _text(path)
    if not source:
        return {"parse_status": "not_applicable", "modules": [], "dynamic_imports": False}
    try:
        tree = ast.parse(source, filename=str(path))
    except SyntaxError as exc:
        return {"parse_status": "syntax_error", "error": str(exc), "modules": [], "dynamic_imports": False}
    modules: set[str] = set()
    dynamic = False
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            modules.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            modules.add(node.module)
        elif isinstance(node, (ast.Call, ast.Assign)) and "import_module" in ast.dump(node):
            dynamic = True
    return {
        "parse_status": "parsed",
        "modules": sorted(modules),
        "dependency_roots": sorted({module.split(".")[0] for module in modules}),
        "dynamic_imports": dynamic,
    }


def _capabilities(path: Path, root: Path) -> list[str]:
    haystack = (_relative(path, root) + "\n" + _text(path)).lower()
    capabilities: list[str] = []
    tests = (
        ("gaussian_kernel", "gaussian" in haystack or "bandwidth" in haystack or "sigma" in haystack),
        ("gaussian_mixture", "mixture" in haystack),
        ("marginal_diagnostics", "marginal" in haystack),
        ("anticoncentration", "anti_concentration" in haystack or "anticoncentration" in haystack),
        ("checkpoint_export", "checkpoint" in haystack or ".npz" in haystack),
        ("dataset_generation_or_loading", "dataset" in haystack or "data_factory" in haystack),
        ("ising_or_spin_target", "ising" in haystack or "spin" in haystack),
        ("jax_dependency", "jax" in haystack),
        ("pennylane_dependency", "pennylane" in haystack),
        ("higher_weight_or_graph", "weight" in haystack or "hypergraph" in haystack or "graph" in haystack),
    )
    for name, present in tests:
        if present:
            capabilities.append(name)
    return capabilities


def _safe_yaml(path: Path) -> tuple[str, Any | None, str | None]:
    try:
        import yaml  # type: ignore[import-not-found]
    except ImportError:
        try:
            return "parsed_without_pyyaml", _minimal_yaml(path), None
        except Exception as exc:
            return "parse_error", None, f"minimal YAML parser: {type(exc).__name__}: {exc}"
    try:
        with path.open("r", encoding="utf-8") as handle:
            return "parsed", yaml.safe_load(handle), None
    except Exception as exc:  # malformed source is inventory evidence, not a reason to execute it
        return "parse_error", None, f"{type(exc).__name__}: {exc}"


def _parse_scalar(value: str) -> Any:
    value = value.strip()
    if not value:
        return None
    if value in {"null", "Null", "NULL", "~"}:
        return None
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    if value.startswith("[") or value.startswith("{"):
        try:
            return json.loads(value.replace("'", '"').replace("True", "true").replace("False", "false").replace("None", "null"))
        except json.JSONDecodeError:
            try:
                return ast.literal_eval(value)
            except (SyntaxError, ValueError):
                return value
    if (value.startswith('"') and value.endswith('"')) or (value.startswith("'") and value.endswith("'")):
        return value[1:-1]
    try:
        return int(value)
    except ValueError:
        try:
            return float(value)
        except ValueError:
            return value


def _minimal_yaml(path: Path) -> dict[str, Any]:
    """Parse the simple mapping/list YAML used by the sibling configs.

    This fallback intentionally handles configuration inspection only.  It does
    not implement YAML tags, anchors, object constructors, or arbitrary code.
    """
    root: dict[str, Any] = {}
    stack: list[tuple[int, Any]] = [(-1, root)]
    lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    for raw_line in lines:
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        line = re.sub(r"\s+#.*$", "", raw_line.rstrip())
        indent = len(line) - len(line.lstrip(" "))
        content = line.strip()
        while len(stack) > 1 and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if content.startswith("- "):
            if not isinstance(parent, list):
                raise ValueError("unsupported YAML list placement")
            parent.append(_parse_scalar(content[2:]))
            continue
        separator = None
        quote: str | None = None
        depth = 0
        for index, character in enumerate(content):
            if character in {"'", '"'}:
                quote = None if quote == character else character if quote is None else quote
            elif quote is None and character in "[{":
                depth += 1
            elif quote is None and character in "]}":
                depth -= 1
            elif quote is None and character == ":" and depth == 0:
                separator = index
                break
        if separator is None or not isinstance(parent, dict):
            raise ValueError(f"unsupported YAML line: {raw_line}")
        key = content[:separator].strip().strip('"\'')
        value = content[separator + 1:].strip()
        if value:
            parent[key] = _parse_scalar(value)
        else:
            next_indent = None
            for candidate in lines[lines.index(raw_line) + 1:]:
                if candidate.strip() and not candidate.lstrip().startswith("#"):
                    next_indent = len(candidate) - len(candidate.lstrip(" "))
                    break
            child: Any = [] if next_indent is not None and next_indent > indent and candidate.strip().startswith("- ") else {}
            parent[key] = child
            stack.append((indent, child))
    return root


def _safe_json(path: Path) -> tuple[str, Any | None, str | None]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            return "parsed", json.load(handle), None
    except Exception as exc:
        return "parse_error", None, f"{type(exc).__name__}: {exc}"


def _json_safe(value: Any) -> Any:
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [_json_safe(item) for item in value]
    return repr(value)


def _declared_paths(value: Any, base: Path, repo_root: Path | None = None) -> list[dict[str, Any]]:
    found: list[dict[str, Any]] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if isinstance(child, str) and ("path" in str(key).lower() or any(token in child.lower() for token in ("data/", "datasets/", "checkpoint", "results/"))):
                candidate = Path(child)
                if not candidate.is_absolute():
                    key_name = str(key).lower()
                    rooted = repo_root is not None and (key_name in {"output_dir", "checkpoint_dir", "artifact_dir"} or child.lower().startswith(("data/", "datasets/", "results/", "checkpoints/")))
                    candidate = ((repo_root if rooted else base) / candidate).resolve()
                found.append({"field": str(key), "declared": child, "resolved": _path_string(candidate), "exists": candidate.exists()})
            found.extend(_declared_paths(child, base, repo_root))
    elif isinstance(value, list):
        for child in value:
            found.extend(_declared_paths(child, base, repo_root))
    return found


def _environment() -> dict[str, Any]:
    package_versions: dict[str, str | None] = {}
    for name in ("numpy", "scipy", "perceval-quandela", "exqalibur", "merlinquantum", "jax", "jaxlib", "pennylane", "torch", "pyyaml"):
        try:
            package_versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            package_versions[name] = None
    return {
        "python": sys.version,
        "executable": sys.executable,
        "platform": platform.platform(),
        "packages": package_versions,
    }


def _file_record(path: Path, root: Path, *, kind: str, parse: bool = False) -> dict[str, Any]:
    related, hits = _is_gaussian_related(path, root)
    record: dict[str, Any] = {
        "path": _path_string(path),
        "relative_path": _relative(path, root),
        "kind": kind,
        "suffix": path.suffix.lower(),
        "size_bytes": path.stat().st_size,
        "sha256": _sha256(path),
        "gaussian_related": related,
        "keyword_hits": hits,
        "capabilities": _capabilities(path, root),
    }
    if path.suffix.lower() == ".py":
        record["imports"] = _imports(path)
    if parse and path.suffix.lower() in {".yaml", ".yml", ".json"}:
        status, parsed, error = _safe_yaml(path) if path.suffix.lower() in {".yaml", ".yml"} else _safe_json(path)
        record["parse_status"] = status
        record["parse_error"] = error
        if status in {"parsed", "parsed_without_pyyaml"}:
            record["content"] = _json_safe(parsed)
            record["declared_paths"] = _declared_paths(parsed, path.parent, root)
    return record


def _artifact_files(root: Path) -> list[Path]:
    candidates: list[Path] = []
    for directory_name in ("results", "data", "datasets", "checkpoints", "artifacts"):
        directory = root / directory_name
        candidates.extend(_iter_files(directory))
    return sorted(set(candidates), key=lambda path: path.as_posix().lower())


def _artifact_kind(path: Path, root: Path) -> str:
    relative = _relative(path, root).lower()
    if path.suffix.lower() in _UNSAFE_SUFFIXES:
        return "unsafe_serialization_reference"
    if "checkpoint" in relative or path.name.startswith("step_"):
        return "checkpoint"
    if "data" in relative or "dataset" in relative:
        return "dataset_or_input"
    if "results" in relative:
        return "result_or_derived_artifact"
    return "artifact"


def _source_rows(configs: list[dict[str, Any]], artifacts: list[dict[str, Any]], root: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    artifact_paths = {record["relative_path"] for record in artifacts}
    artifact_text = "\n".join(artifact_paths).lower()
    for config in configs:
        if not config["gaussian_related"]:
            continue
        relative = config["relative_path"]
        content = config.get("content") if isinstance(config.get("content"), dict) else {}
        experiment = content.get("experiment", {}) if isinstance(content, dict) else {}
        name = str(experiment.get("name", Path(relative).stem))
        output_dir = str(experiment.get("output_dir", ""))
        output_exists = bool(output_dir and (root / output_dir).exists())
        declared_missing = [item for item in config.get("declared_paths", []) if not item["exists"]]
        lower = f"{relative} {name} {output_dir}".lower()
        if declared_missing:
            status: CompatibilityStatus = "blocked"
            reason = "A configured input path is missing; the source dataset is not fabricated."
        elif "grid5000" in lower or "genomic" in lower:
            status = "blocked" if "genomic" in lower and "genomic" not in artifact_text else "reference_only"
            reason = "Exact real-data provenance/features are not resolved from the local artifact set."
        elif "scaling" in lower or "koshik" in lower or "jax" in _text(root / relative):
            status = "reference_only"
            reason = "The source row is a large/JAX variance study; it is inventoried for provenance, not silently reduced to a different run."
        elif not output_exists:
            status = "blocked"
            reason = "The resolved source output directory is absent."
        else:
            status = "exact_reproduction"
            reason = "Config, source package and local result family are present; replay has not been executed by inventory."
        changed: list[str] = []
        if status == "reference_only":
            changed = ["execution_backend_or_size_not_changed_in_inventory"]
        if status == "blocked":
            changed = ["none; missing source input is preserved as blocked"]
        rows.append({
            "source_id": f"{name}:{relative}",
            "package_scope": "iqp_bp" if "iqp_bp" in lower or "training_smoke" in lower or "scaling" in lower else "iqp_mmd_or_shared",
            "config": config,
            "result_evidence": sorted(path for path in artifact_paths if Path(path).parts and (name.lower() in path.lower() or Path(output_dir).as_posix().lower() in path.lower()))[:500],
            "disposition": status,
            "reason": reason,
            "changed_fields": changed,
            "execution_state": "not_run",
        })
    return rows


def compatibility_record(
    source_row: str,
    *,
    required_paths: list[str | Path] = None,
    status: CompatibilityStatus | None = None,
    reason: str | None = None,
    changed_fields: tuple[str, ...] = (),
    required_capability: str = "",
    evidence: tuple[str, ...] = (),
) -> dict[str, Any]:
    """Create a validated ledger row, forcing missing inputs to ``blocked``."""
    paths = [Path(path) for path in (required_paths or [])]
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        status = "blocked"
        reason = reason or "Required source artifact is missing; no substitute was generated."
        evidence = tuple(evidence) + tuple(f"missing:{path}" for path in missing)
    if status is None or status not in COMPATIBILITY_STATUSES:
        raise ValueError(f"status must be one of {COMPATIBILITY_STATUSES}")
    if not reason:
        raise ValueError("compatibility records require a reason")
    return {
        "source_row": source_row,
        "status": status,
        "reason": reason,
        "changed_fields": list(changed_fields),
        "required_capability": required_capability,
        "evidence": list(evidence),
    }


def build_sibling_inventory(sibling_root: str | Path, *, pinned_commit: str = PINNED_SIBLING_COMMIT) -> dict[str, Any]:
    """Build a read-only, hash-backed inventory of both sibling packages."""
    root = Path(sibling_root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        raise FileNotFoundError(root)
    source_files: list[dict[str, Any]] = []
    for package in ("iqp_bp", "iqp_mmd"):
        package_root = root / "src" / package
        for path in _iter_files(package_root):
            source_files.append(_file_record(path, root, kind=f"source:{package}"))
    configs = [_file_record(path, root, kind="config", parse=True) for path in _iter_files(root / "configs") if path.suffix.lower() in {".yaml", ".yml", ".json"}]
    artifact_records: list[dict[str, Any]] = []
    for path in _artifact_files(root):
        record = _file_record(path, root, kind=_artifact_kind(path, root))
        record["safe_import"] = path.suffix.lower() in _SAFE_IMPORT_SUFFIXES
        if path.suffix.lower() in _UNSAFE_SUFFIXES:
            record["safe_import_reason"] = "Python object deserialization is intentionally unsupported."
        artifact_records.append(record)
    observed_head = _git(root, "rev-parse", "HEAD")
    pinned_parent = _git(root, "show", "-s", "--format=%P", pinned_commit)
    result: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "inventory_scope": {
            "purpose": "provenance inventory and replay planning, not scientific certification",
            "packages": ["iqp_bp", "iqp_mmd"],
            "included": ["source modules", "configs", "results", "data/dataset/checkpoint references", "direct import dependencies", "capabilities", "hashes"],
            "excluded_from_execution": ["automatic downloads", "automatic publication", "sibling mutation", "blind pickle/joblib/torch deserialization"],
        },
        "source": {
            "root": _path_string(root),
            "pinned_commit": pinned_commit,
            "observed_head": observed_head,
            "head_matches_pinned": observed_head == pinned_commit,
            "pinned_parent": pinned_parent,
            "git_status": _git_status(root),
            "status_observation": "clean" if not _git_status(root) else "dirty",
        },
        "environment": _environment(),
        "packages": {
            package: {
                "root": _path_string(root / "src" / package),
                "files": [record for record in source_files if record["kind"] == f"source:{package}"],
                "dependency_roots": sorted({dependency for record in source_files if record["kind"] == f"source:{package}" for dependency in record.get("imports", {}).get("dependency_roots", [])}),
                "capabilities": sorted({capability for record in source_files if record["kind"] == f"source:{package}" for capability in record.get("capabilities", [])}),
            }
            for package in ("iqp_bp", "iqp_mmd")
        },
        "configs": configs,
        "artifacts": artifact_records,
        "source_rows": [],
        "missing_artifact_observations": {
            "top_level_data_directory": (root / "data").exists(),
            "top_level_datasets_directory": (root / "datasets").exists(),
            "note": "An absent top-level directory does not prove every configured dataset is missing; each declared/resolved path is checked separately.",
        },
        "safe_boundary": {
            "allowed_import_suffixes": sorted(_SAFE_IMPORT_SUFFIXES),
            "rejected_suffixes": sorted(_UNSAFE_SUFFIXES),
            "np_load_allow_pickle": False,
            "missing_data_policy": "record blocked and preserve reference; never synthesize a replacement",
        },
    }
    result["source_rows"] = _source_rows(configs, artifact_records, root)
    result["summary"] = {
        "source_file_count": len(source_files),
        "config_count": len(configs),
        "artifact_count": len(artifact_records),
        "gaussian_config_count": sum(1 for config in configs if config["gaussian_related"]),
        "dispositions": {status: sum(1 for row in result["source_rows"] if row["disposition"] == status) for status in COMPATIBILITY_STATUSES},
    }
    return result


def _validate_inventory(value: Any) -> dict[str, Any]:
    if not isinstance(value, dict) or value.get("schema_version") != SCHEMA_VERSION:
        raise ValueError(f"expected schema_version {SCHEMA_VERSION}")
    for key in ("source", "environment", "packages", "configs", "artifacts", "source_rows", "safe_boundary"):
        if key not in value:
            raise ValueError(f"inventory missing {key}")
    for row in value["source_rows"]:
        if row.get("disposition") not in COMPATIBILITY_STATUSES:
            raise ValueError(f"invalid source disposition: {row.get('disposition')}")
    return value


def _write_json(path: Path, value: Any) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(_json_safe(value), handle, indent=2, sort_keys=True)
        handle.write("\n")
    temporary.replace(path)
    return path


def write_inventory_outputs(inventory: dict[str, Any], destination: str | Path) -> dict[str, Path]:
    """Write inventory, source contract, and per-row reference manifests atomically."""
    validated = _validate_inventory(inventory)
    output_root = Path(destination)
    output_root.mkdir(parents=True, exist_ok=True)
    inventory_path = _write_json(output_root / "sibling_inventory.json", validated)
    contract = {
        "schema_version": "v4_tcdp.sibling_source_contract.v1",
        "source": validated["source"],
        "environment": validated["environment"],
        "packages": {name: {"root": value["root"], "dependency_roots": value["dependency_roots"], "capabilities": value["capabilities"]} for name, value in validated["packages"].items()},
        "configs": [{"source_id": row["source_id"], "relative_path": row["config"]["relative_path"], "content": row["config"].get("content"), "declared_paths": row["config"].get("declared_paths", []), "disposition": row["disposition"], "reason": row["reason"], "changed_fields": row["changed_fields"]} for row in validated["source_rows"]],
        "capability_policy": {
            "physical_weight_gt_2": "blocked_or_reference_only_until_compiler_and_projection_proof",
            "jax_or_pennylane": "source dependency recorded; no dependency added to merlin_iqp.classical",
            "real_or_genomic_data": "requires exact local input hashes and feature/split provenance",
        },
        "scientific_status": "inventory only; not scientific certification",
    }
    contract_path = _write_json(output_root / "sibling" / "source_contract.json", contract)
    manifest_paths: dict[str, Path] = {}
    for row in validated["source_rows"]:
        safe_id = "".join(character if character.isalnum() or character in "-_" else "_" for character in row["source_id"])
        manifest = {
            "schema_version": "v4_tcdp.sibling_export_manifest.v1",
            "source_id": row["source_id"],
            "source_commit": validated["source"]["pinned_commit"],
            "disposition": row["disposition"],
            "reason": row["reason"],
            "changed_fields": row["changed_fields"],
            "execution_state": row["execution_state"],
            "config": row["config"],
            "result_evidence": row["result_evidence"],
            "copy_performed": False,
            "missing_data_policy": "No missing dataset is generated by this manifest.",
        }
        manifest_paths[safe_id] = _write_json(output_root / "sibling" / safe_id / "manifest.json", manifest)
    return {"inventory": inventory_path, "source_contract": contract_path, **manifest_paths}


def load_export_manifest(path: str | Path) -> dict[str, Any]:
    """Load a JSON manifest only; this never loads a referenced artifact."""
    manifest_path = Path(path).resolve()
    with manifest_path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict) or not str(value.get("schema_version", "")).startswith("v4_tcdp.sibling_export_manifest."):
        raise ValueError("unsupported sibling export manifest")
    if value.get("copy_performed") is not False:
        raise ValueError("manifest must explicitly record whether copying occurred")
    return value


def safe_import_artifact(path: str | Path) -> dict[str, Any]:
    """Read supported numeric/text formats without Python object deserialization."""
    source = Path(path).resolve()
    if not source.exists():
        raise FileNotFoundError(source)
    suffix = source.suffix.lower()
    if suffix in _UNSAFE_SUFFIXES:
        raise ValueError(f"unsafe serialized artifact rejected: {suffix}")
    if suffix not in _SAFE_IMPORT_SUFFIXES:
        raise ValueError(f"unsupported artifact format: {suffix}")
    record: dict[str, Any] = {"path": _path_string(source), "sha256": _sha256(source), "format": suffix}
    if suffix == ".npz":
        with np.load(source, allow_pickle=False) as archive:
            record["keys"] = list(archive.files)
            record["arrays"] = {key: {"shape": list(archive[key].shape), "dtype": str(archive[key].dtype)} for key in archive.files}
    elif suffix == ".npy":
        array = np.load(source, allow_pickle=False)
        record["array"] = {"shape": list(array.shape), "dtype": str(array.dtype)}
    elif suffix in {".json", ".jsonl", ".yaml", ".yml"}:
        if suffix == ".json":
            status, parsed, error = _safe_json(source)
        elif suffix in {".yaml", ".yml"}:
            status, parsed, error = _safe_yaml(source)
        else:
            status, parsed, error = "metadata_only", None, None
        record["parse_status"] = status
        if error:
            record["parse_error"] = error
        elif parsed is not None:
            record["top_level_type"] = type(parsed).__name__
    elif suffix == ".csv":
        with source.open("r", encoding="utf-8", newline="") as handle:
            reader = csv.reader(handle)
            record["header"] = next(reader, [])
    return record
