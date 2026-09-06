"""Bounded discrete-alpha-key NAT optimization for the v4 deployment boundary.

NAT (natural alpha training) has two different parameter spaces here.  Single
qubit angles are continuous and use the existing exact analytic MMD gradient.
Pair angles are deployment catalog keys, so they use deterministic coordinate
search over the circular ``0.1 * j`` catalog.  A candidate is always compiled
through :mod:`merlin_iqp.deploy.compile`; its winding and lifted angle are part
of the evaluated state.

There is deliberately no finite-difference gradient through quantization,
straight-through estimator, interpolation, or hidden continuous pair proxy.
"""

from __future__ import annotations

from dataclasses import dataclass
import json
import math
import platform
from pathlib import Path
from typing import Any, Mapping, Sequence

import numpy as np

from merlin_iqp.classical import KernelSpec, generators_from_pairs, initialize_theta
from merlin_iqp.classical._validation import hash_array, hash_json
from merlin_iqp.classical.objectives import objective_and_gradient_exact
from merlin_iqp.deploy.compile import (
    ALPHA_KEYS,
    ALPHA_STEP,
    TWO_PI,
    CompiledCircuit,
    compile_iqp,
    quantize_theta,
)


SCHEMA_VERSION = "v4_tcdp.nat_run.v1"
CATALOG_SIZE = len(ALPHA_KEYS)
Pair = tuple[int, int]


def _normalise_pairs(n: int, pairs: Sequence[Sequence[int]]) -> tuple[Pair, ...]:
    pair_rows = list(pairs)
    if any(len(pair) != 2 for pair in pair_rows):
        raise ValueError("pairs must contain exactly two indices")
    result = tuple(sorted((min(int(pair[0]), int(pair[1])), max(int(pair[0]), int(pair[1]))) for pair in pair_rows))
    if not result:
        raise ValueError("NAT requires at least one pair generator")
    if any(i == j or i < 0 or j >= n for i, j in result):
        raise ValueError(f"pairs must satisfy 0 <= i < j < n for n={n}")
    if len(set(result)) != len(result):
        raise ValueError("duplicate pairs are not supported")
    return result


@dataclass(frozen=True)
class NatConfig:
    """All bounded, replay-relevant settings for one NAT run."""

    n: int
    pairs: tuple[Pair, ...]
    steps: int = 150
    seed: int = 0
    sigma: float = 1.0
    single_lr: float = 0.05
    single_optimizer: str = "adam"
    pair_budget: int | None = None
    initialization: str = "data_dependent"
    initialization_method: str = "parity"
    initialization_scale: float = 0.1
    initialization_std: float = 0.1
    topology: str = "arbitrary_weight2"
    source_commit: str | None = None
    allow_pair_moves: bool = True
    run_kind: str = "nat"

    def __post_init__(self) -> None:
        if int(self.n) != self.n or self.n < 2:
            raise ValueError("NAT requires an integer n >= 2")
        normalised = _normalise_pairs(int(self.n), self.pairs)
        object.__setattr__(self, "n", int(self.n))
        object.__setattr__(self, "pairs", normalised)
        if int(self.steps) != self.steps or self.steps < 0:
            raise ValueError("steps must be a non-negative integer")
        object.__setattr__(self, "steps", int(self.steps))
        if self.single_optimizer.lower() not in {"sgd", "adam"}:
            raise ValueError("single_optimizer must be 'sgd' or 'adam'")
        object.__setattr__(self, "single_optimizer", self.single_optimizer.lower())
        for name, value in (("sigma", self.sigma), ("single_lr", self.single_lr), ("initialization_std", self.initialization_std)):
            if not np.isfinite(value) or (name != "initialization_std" and value <= 0) or (name == "initialization_std" and value < 0):
                raise ValueError(f"{name} must be finite and valid")
        if self.initialization not in {"data_dependent", "small_angle"}:
            raise ValueError("initialization must be data_dependent or small_angle")
        if self.initialization_method != "parity":
            raise ValueError("initialization_method must be parity")
        if not np.isfinite(self.initialization_scale) or self.initialization_scale < 0:
            raise ValueError("initialization_scale must be finite and non-negative")
        if self.pair_budget is not None and (int(self.pair_budget) != self.pair_budget or self.pair_budget < 0):
            raise ValueError("pair_budget must be a non-negative integer")
        object.__setattr__(self, "pair_budget", None if self.pair_budget is None else int(self.pair_budget))

    @property
    def resolved_pair_budget(self) -> int:
        """Default to two bounded neighbor trials per pair per step."""

        return self.steps * len(self.pairs) * 2 if self.pair_budget is None else self.pair_budget

    def as_dict(self) -> dict[str, Any]:
        return {
            "n": self.n,
            "pairs": [list(pair) for pair in self.pairs],
            "steps": self.steps,
            "seed": self.seed,
            "sigma": float(self.sigma),
            "single_lr": float(self.single_lr),
            "single_optimizer": self.single_optimizer,
            "pair_budget": self.pair_budget,
            "resolved_pair_budget": self.resolved_pair_budget,
            "initialization_std": float(self.initialization_std),
            "initialization": self.initialization,
            "initialization_method": self.initialization_method,
            "initialization_scale": float(self.initialization_scale),
            "topology": self.topology,
            "source_commit": self.source_commit,
            "allow_pair_moves": self.allow_pair_moves,
            "run_kind": self.run_kind,
        }


@dataclass(frozen=True)
class NatRun:
    """Serializable result and evidence ledger for a bounded NAT run."""

    config: NatConfig
    generator: np.ndarray
    initial_singles: np.ndarray
    initial_pair_keys: tuple[int, ...]
    initial_pair_windings: tuple[int, ...]
    final_singles: np.ndarray
    final_pair_keys: tuple[int, ...]
    final_pair_windings: tuple[int, ...]
    final_compiled: CompiledCircuit
    loss_history: tuple[float, ...]
    budgets: dict[str, int]
    provenance: dict[str, Any]

    @property
    def final_loss(self) -> float:
        return float(self.loss_history[-1])

    @property
    def pair_moves(self) -> int:
        return sum(int(a != b) for a, b in zip(self.initial_pair_keys, self.final_pair_keys, strict=True))

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "schema_version": SCHEMA_VERSION,
            "config": self.config.as_dict(),
            "generator": self.generator.astype(np.uint8).tolist(),
            "initial_singles": self.initial_singles.tolist(),
            "initial_pair_keys": list(self.initial_pair_keys),
            "initial_pair_windings": list(self.initial_pair_windings),
            "final_singles": self.final_singles.tolist(),
            "final_pair_keys": list(self.final_pair_keys),
            "final_pair_windings": list(self.final_pair_windings),
            "final_compiled": self.final_compiled.as_metadata(),
            "loss_history": list(self.loss_history),
            "final_loss": self.final_loss,
            "pair_moves": self.pair_moves,
            "budgets": dict(self.budgets),
            "provenance": dict(self.provenance),
        }
        payload["run_hash"] = hash_json({"config": payload["config"], "loss_history": payload["loss_history"], "final_singles": payload["final_singles"], "final_pair_keys": payload["final_pair_keys"], "final_pair_windings": payload["final_pair_windings"]})
        return payload


def _infer_n(target: object, n: int | None) -> int:
    if n is not None:
        return int(n)
    target_n = getattr(target, "n", None)
    if target_n is not None:
        return int(target_n)
    values = np.asarray(target)
    if values.ndim == 1 and len(values) > 0 and len(values) & (len(values) - 1) == 0:
        return int(math.log2(len(values)))
    raise ValueError("n must be supplied when target has no n attribute")


def _values_for_pairs(value: Sequence[Any] | Mapping[Sequence[int], Any] | None, pairs: tuple[Pair, ...], *, name: str) -> list[Any] | None:
    if value is None:
        return None
    if isinstance(value, Mapping):
        normalised = {(min(int(pair[0]), int(pair[1])), max(int(pair[0]), int(pair[1]))): item for pair, item in value.items()}
        if set(normalised) != set(pairs):
            raise ValueError(f"{name} mapping must contain exactly the configured pairs")
        return [normalised[pair] for pair in pairs]
    values = list(value)
    if len(values) != len(pairs):
        raise ValueError(f"{name} must contain one value per pair")
    return values


def _validate_key(value: Any, *, name: str) -> int:
    if int(value) != value or not 0 <= int(value) < CATALOG_SIZE:
        raise ValueError(f"{name} must be an integer catalog key in [0, {CATALOG_SIZE - 1}]")
    return int(value)


def _nearest_winding(wrapped_alpha: float, reference_alpha: float) -> int:
    center = (reference_alpha - wrapped_alpha) / TWO_PI
    candidates = (math.floor(center), math.ceil(center))
    return int(min(candidates, key=lambda winding: (abs(wrapped_alpha + TWO_PI * winding - reference_alpha), winding)))


def _lifted_alpha(key: int, winding: int) -> float:
    return float(ALPHA_STEP * key + TWO_PI * winding)


def _compile_state(config: NatConfig, singles: np.ndarray, keys: tuple[int, ...], windings: tuple[int, ...]) -> CompiledCircuit:
    pair_rows = [(i, j, _lifted_alpha(key, winding) / 4.0) for (i, j), key, winding in zip(config.pairs, keys, windings, strict=True)]
    compiled = compile_iqp(config.n, singles, pair_rows, topology=config.topology, quantize=True)
    for (pair, angle), key in zip(compiled.pair_angles, keys, strict=True):
        if angle.key != key:
            raise AssertionError(f"compiler changed requested NAT key for {pair}: {key} -> {angle.key}")
    return compiled


def _compiled_objective(compiled: CompiledCircuit, generator: np.ndarray, target: object, kernel: KernelSpec) -> tuple[float, np.ndarray]:
    pair_thetas = np.asarray([angle.lifted_theta for _, angle in compiled.pair_angles], dtype=np.float64)
    theta = np.concatenate((np.asarray(compiled.singles, dtype=np.float64), pair_thetas))
    return objective_and_gradient_exact(theta, generator, target, kernel)


def _initial_state(
    config: NatConfig,
    *,
    singles: Sequence[float] | None,
    pair_keys: Sequence[int] | Mapping[Sequence[int], int] | None,
    pair_thetas: Sequence[float] | Mapping[Sequence[int], float] | None,
    pair_windings: Sequence[int] | Mapping[Sequence[int], int] | None,
    target: object,
) -> tuple[np.ndarray, tuple[int, ...], tuple[int, ...]]:
    if pair_keys is not None and pair_thetas is not None:
        raise ValueError("provide pair_keys or pair_thetas, not both")
    generator = generators_from_pairs(config.n, config.pairs)
    if config.initialization == "data_dependent":
        seeded_theta = initialize_theta(
            generator,
            config.seed,
            scheme="parity",
            scale=config.initialization_scale,
            target=target,
        )
    else:
        seeded_theta = initialize_theta(generator, config.seed, scheme="small_angle", std=config.initialization_std)
    initial_singles = np.asarray(seeded_theta[: config.n] if singles is None else singles, dtype=np.float64).copy()
    if initial_singles.shape != (config.n,) or not np.all(np.isfinite(initial_singles)):
        raise ValueError(f"singles must be a finite vector of length {config.n}")

    raw_thetas = _values_for_pairs(pair_thetas, config.pairs, name="pair_thetas")
    if raw_thetas is None and pair_keys is None and singles is None:
        raw_thetas = list(seeded_theta[config.n :])
    if raw_thetas is not None:
        if pair_windings is not None:
            raise ValueError("pair_windings cannot accompany pair_thetas")
        quantized = [quantize_theta(float(theta)) for theta in raw_thetas]
        return initial_singles, tuple(angle.key for angle in quantized), tuple(angle.winding for angle in quantized)

    raw_keys = _values_for_pairs(pair_keys, config.pairs, name="pair_keys")
    if raw_keys is None:
        raw_keys = [0] * len(config.pairs)
    keys = tuple(_validate_key(key, name="pair key") for key in raw_keys)
    raw_windings = _values_for_pairs(pair_windings, config.pairs, name="pair_windings")
    windings = tuple(0 if winding is None else int(winding) for winding in (raw_windings or [0] * len(config.pairs)))
    return initial_singles, keys, windings


def run_nat(
    target: object,
    pairs: Sequence[Sequence[int]],
    *,
    n: int | None = None,
    singles: Sequence[float] | None = None,
    pair_keys: Sequence[int] | Mapping[Sequence[int], int] | None = None,
    pair_thetas: Sequence[float] | Mapping[Sequence[int], float] | None = None,
    pair_windings: Sequence[int] | Mapping[Sequence[int], int] | None = None,
    steps: int = 150,
    seed: int = 0,
    sigma: float = 1.0,
    single_lr: float = 0.05,
    single_optimizer: str = "adam",
    pair_budget: int | None = None,
    topology: str = "arbitrary_weight2",
    source_commit: str | None = None,
    allow_pair_moves: bool = True,
    run_kind: str = "nat",
    initialization: str = "data_dependent",
    initialization_method: str = "parity",
    initialization_scale: float = 0.1,
    initialization_std: float = 0.1,
) -> NatRun:
    """Run bounded NAT on an exact target using the Hamming Gaussian MMD.

    Each outer step performs at most two objective evaluations per pair (the
    circular ``key - 1`` and ``key + 1`` neighbors), subject to ``pair_budget``.
    It then performs one exact analytic gradient update on the continuous
    singles.  ``allow_pair_moves=False`` provides a labeled fixed-pair,
    equal-budget continuation control; it still evaluates the same neighbors
    but deliberately does not commit their keys.
    """

    resolved_n = _infer_n(target, n)
    config = NatConfig(
        n=resolved_n,
        pairs=tuple((int(pair[0]), int(pair[1])) for pair in pairs),
        steps=steps,
        seed=seed,
        sigma=sigma,
        single_lr=single_lr,
        single_optimizer=single_optimizer,
        pair_budget=pair_budget,
        topology=topology,
        source_commit=source_commit,
        allow_pair_moves=allow_pair_moves,
        run_kind=run_kind,
        initialization=initialization,
        initialization_method=initialization_method,
        initialization_scale=initialization_scale,
    )
    generator = generators_from_pairs(config.n, config.pairs)
    current_singles, current_keys, current_windings = _initial_state(
        config,
        singles=singles,
        pair_keys=pair_keys,
        pair_thetas=pair_thetas,
        pair_windings=pair_windings,
        target=target,
    )
    initial_singles = current_singles.copy()
    initial_keys = current_keys
    initial_windings = current_windings
    kernel = KernelSpec(kind="hamming_gaussian", sigma=config.sigma, provenance={"nat": True, "schema_version": SCHEMA_VERSION})
    objective_evaluations = 0
    pair_evaluations = 0
    single_gradient_evaluations = 0
    pair_moves = 0
    compiled = _compile_state(config, current_singles, current_keys, current_windings)
    loss, _ = _compiled_objective(compiled, generator, target, kernel)
    objective_evaluations += 1
    loss_history = [float(loss)]
    adam_m = np.zeros(config.n, dtype=np.float64)
    adam_v = np.zeros(config.n, dtype=np.float64)
    adam_t = 0

    for _step in range(config.steps):
        for pair_index in range(len(config.pairs)):
            if pair_evaluations >= config.resolved_pair_budget:
                break
            current_pair_alpha = _lifted_alpha(current_keys[pair_index], current_windings[pair_index])
            candidate_records: list[tuple[float, int, int, CompiledCircuit]] = []
            for delta in (-1, 1):
                if pair_evaluations >= config.resolved_pair_budget:
                    break
                candidate_key = (current_keys[pair_index] + delta) % CATALOG_SIZE
                candidate_winding = _nearest_winding(ALPHA_STEP * candidate_key, current_pair_alpha)
                candidate_keys = list(current_keys)
                candidate_windings = list(current_windings)
                candidate_keys[pair_index] = candidate_key
                candidate_windings[pair_index] = candidate_winding
                candidate_compiled = _compile_state(config, current_singles, tuple(candidate_keys), tuple(candidate_windings))
                candidate_loss, _ = _compiled_objective(candidate_compiled, generator, target, kernel)
                objective_evaluations += 1
                pair_evaluations += 1
                candidate_records.append((float(candidate_loss), candidate_key, candidate_winding, candidate_compiled))
            if not candidate_records:
                break
            best = min(candidate_records, key=lambda record: (record[0], record[1], record[2]))
            if allow_pair_moves and best[0] < loss:
                loss, best_key, best_winding, compiled = best
                current_keys = tuple(best_key if index == pair_index else key for index, key in enumerate(current_keys))
                current_windings = tuple(best_winding if index == pair_index else winding for index, winding in enumerate(current_windings))
                pair_moves += 1
            if not allow_pair_moves:
                # This evaluates the same discrete neighborhood as NAT while
                # retaining the starting compiled pair state for the control.
                compiled = _compile_state(config, current_singles, current_keys, current_windings)

        compiled = _compile_state(config, current_singles, current_keys, current_windings)
        loss, gradient = _compiled_objective(compiled, generator, target, kernel)
        objective_evaluations += 1
        single_gradient_evaluations += 1
        single_gradient = np.asarray(gradient[: config.n], dtype=np.float64)
        if config.single_optimizer == "sgd":
            current_singles = current_singles - config.single_lr * single_gradient
        else:
            adam_t += 1
            adam_m = 0.9 * adam_m + 0.1 * single_gradient
            adam_v = 0.999 * adam_v + 0.001 * single_gradient**2
            m_hat = adam_m / (1.0 - 0.9**adam_t)
            v_hat = adam_v / (1.0 - 0.999**adam_t)
            current_singles = current_singles - config.single_lr * m_hat / (np.sqrt(v_hat) + 1e-8)
        if not np.all(np.isfinite(current_singles)):
            raise FloatingPointError("NAT single-angle update produced a non-finite value")
        compiled = _compile_state(config, current_singles, current_keys, current_windings)
        loss, _ = _compiled_objective(compiled, generator, target, kernel)
        objective_evaluations += 1
        loss_history.append(float(loss))

    target_provenance = getattr(target, "provenance", {})
    provenance = {
        "algorithm": "bounded_discrete_alpha_key_neighbor_coordinate_search",
        "single_update": "objective_and_gradient_exact plus deterministic SGD/Adam update on first n coordinates",
        "pair_update": "circular key neighbors (key-1, key+1) with strict-improvement acceptance",
        "objective": {"kind": "hamming_gaussian", "sigma": float(config.sigma), "normalization": "mmd2", "exact": True},
        "compiler": {"module": "merlin_iqp.deploy.compile", "catalog_step": ALPHA_STEP, "catalog_keys": CATALOG_SIZE, "quantize": True, "winding_and_lift_preserved": True},
        "forbidden_methods": ["finite_difference_through_quantization", "straight_through_gradient", "interpolation"],
        "control": "fixed_pair_equal_budget" if not allow_pair_moves else None,
        "seed": int(config.seed),
        "initialization": {
            "scheme": config.initialization,
            "method": config.initialization_method,
            "scale": float(config.initialization_scale),
            "std": float(config.initialization_std),
            "target_hash": str(getattr(target, "hash", "unavailable")),
            "target_split": target_provenance.get("split", "unspecified") if isinstance(target_provenance, Mapping) else "unspecified",
        },
        "python": platform.python_version(),
        "numpy": np.__version__,
        "generator_hash": hash_array(generator),
        "source_commit": source_commit,
    }
    budgets = {
        "requested_steps": config.steps,
        "completed_steps": config.steps,
        "pair_budget": config.resolved_pair_budget,
        "pair_evaluations": pair_evaluations,
        "single_gradient_evaluations": single_gradient_evaluations,
        "objective_evaluations": objective_evaluations,
        "pair_moves": pair_moves,
    }
    return NatRun(
        config=config,
        generator=generator,
        initial_singles=initial_singles,
        initial_pair_keys=initial_keys,
        initial_pair_windings=initial_windings,
        final_singles=current_singles.copy(),
        final_pair_keys=current_keys,
        final_pair_windings=current_windings,
        final_compiled=compiled,
        loss_history=tuple(loss_history),
        budgets=budgets,
        provenance=provenance,
    )


def run_equal_budget_control(target: object, pairs: Sequence[Sequence[int]], **kwargs: Any) -> NatRun:
    """Run the fixed-pair continuation control with NAT's same budget rules."""

    kwargs["allow_pair_moves"] = False
    kwargs["run_kind"] = "fixed_pair_equal_budget_control"
    return run_nat(target, pairs, **kwargs)


def write_nat_run(run: NatRun, path: str | Path) -> Path:
    """Write deterministic JSON suitable for replay and provenance review."""

    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(run.to_dict(), indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return destination


__all__ = ["CATALOG_SIZE", "NatConfig", "NatRun", "SCHEMA_VERSION", "run_equal_budget_control", "run_nat", "write_nat_run"]
