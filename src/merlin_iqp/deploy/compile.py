"""Logical IQP-to-CP compilation with explicit sign and winding contracts."""

from __future__ import annotations

from dataclasses import dataclass, field
import math
from typing import Iterable, Literal, Sequence

import numpy as np

ALPHA_KEYS = np.arange(63, dtype=int)
ALPHA_STEP = 0.1
TWO_PI = 2.0 * math.pi
Topology = Literal["arbitrary_weight2", "path", "cycle", "disjoint"]


@dataclass(frozen=True)
class QuantizedAngle:
    """Raw and compiled forms of a pair angle.

    ``raw_alpha`` is 4 times the trained ZZ angle.  ``wrapped_alpha`` is the
    catalog key's angle in [0, 2*pi), while ``lifted_theta`` retains the
    winding needed by the two local compensation phase shifters.
    """

    raw_theta: float
    raw_alpha: float
    key: int
    wrapped_alpha: float
    winding: int
    lifted_alpha: float
    lifted_theta: float

    @property
    def effective_theta(self) -> float:
        return self.lifted_theta


@dataclass(frozen=True)
class CompiledGate:
    kind: Literal["single", "pair_compensation", "cp"]
    qubits: tuple[int, ...]
    theta: float
    alpha: float | None = None
    key: int | None = None
    metadata: dict[str, float | int | str] = field(default_factory=dict)


@dataclass(frozen=True)
class CompiledCircuit:
    n: int
    singles: tuple[float, ...]
    pair_angles: tuple[tuple[tuple[int, int], QuantizedAngle], ...]
    gates: tuple[CompiledGate, ...]
    topology: str
    quantized: bool
    metadata: dict[str, object] = field(default_factory=dict)

    @property
    def pairs(self) -> tuple[tuple[int, int], ...]:
        return tuple(pair for pair, _ in self.pair_angles)

    @property
    def lifted_pair_thetas(self) -> dict[tuple[int, int], float]:
        return {pair: angle.lifted_theta for pair, angle in self.pair_angles}

    @property
    def wrapped_pair_alphas(self) -> dict[tuple[int, int], float]:
        return {pair: angle.wrapped_alpha for pair, angle in self.pair_angles}

    def as_metadata(self) -> dict[str, object]:
        return {
            **self.metadata,
            "n": self.n,
            "topology": self.topology,
            "quantized": self.quantized,
            "pair_angles": [
                {
                    "i": pair[0],
                    "j": pair[1],
                    "raw_theta": angle.raw_theta,
                    "raw_alpha": angle.raw_alpha,
                    "key": angle.key,
                    "wrapped_alpha": angle.wrapped_alpha,
                    "winding": angle.winding,
                    "lifted_alpha": angle.lifted_alpha,
                    "lifted_theta": angle.lifted_theta,
                }
                for pair, angle in self.pair_angles
            ],
        }


def _finite(value: float, name: str) -> float:
    value = float(value)
    if not math.isfinite(value):
        raise ValueError(f"{name} must be finite, got {value!r}")
    return value


def wrap_angle(angle: float) -> float:
    """Return an angle in [0, 2*pi), retaining no winding information."""

    return float(_finite(angle, "angle") % TWO_PI)


def circular_distance(a: float, b: float) -> float:
    return abs((a - b + math.pi) % TWO_PI - math.pi)


def nearest_alpha_key(alpha: float) -> tuple[int, float]:
    """Return the circular-nearest integer key and its wrapped angle.

    Keys are intentionally the nonuniform 0.1*j catalog [0, 6.2].  Ties are
    deterministic: the lower integer key wins.
    """

    target = wrap_angle(alpha)
    distances = np.array([circular_distance(target, ALPHA_STEP * int(k)) for k in ALPHA_KEYS])
    key = int(np.flatnonzero(np.isclose(distances, distances.min(), rtol=0.0, atol=1e-14))[0])
    return key, float(ALPHA_STEP * key)


def quantize_theta(theta: float) -> QuantizedAngle:
    """Quantize a ZZ angle while preserving the nearest 2*pi lift."""

    raw_theta = _finite(theta, "theta")
    raw_alpha = 4.0 * raw_theta
    key, wrapped = nearest_alpha_key(raw_alpha)
    # Compare the two adjacent winding choices explicitly, so half-way cases
    # have a stable lower-winding tie break too.
    center = (raw_alpha - wrapped) / TWO_PI
    candidates = [math.floor(center), math.ceil(center)]
    winding = min(candidates, key=lambda value: (abs(wrapped + TWO_PI * value - raw_alpha), value))
    lifted_alpha = wrapped + TWO_PI * winding
    return QuantizedAngle(
        raw_theta=raw_theta,
        raw_alpha=raw_alpha,
        key=key,
        wrapped_alpha=wrapped,
        winding=int(winding),
        lifted_alpha=lifted_alpha,
        lifted_theta=lifted_alpha / 4.0,
    )


def _validate_pairs(n: int, pairs: Iterable[tuple[int, int]]) -> tuple[tuple[int, int], ...]:
    normalized: list[tuple[int, int]] = []
    for pair in pairs:
        if len(pair) != 2:
            raise ValueError(f"pair generator must have weight 2, got {pair!r}")
        i, j = (int(pair[0]), int(pair[1]))
        if i == j or not (0 <= i < n and 0 <= j < n):
            raise ValueError(f"invalid pair {pair!r} for n={n}")
        normalized.append(tuple(sorted((i, j))))
    if len(set(normalized)) != len(normalized):
        raise ValueError("duplicate pair generators are not allowed")
    return tuple(sorted(normalized))


def validate_topology(n: int, pairs: Sequence[tuple[int, int]], topology: str) -> None:
    """Reject pair graphs outside the explicitly declared capability."""

    if topology not in {"arbitrary_weight2", "path", "cycle", "disjoint"}:
        raise ValueError(f"unsupported topology {topology!r}; weight>2 is not compiled")
    normalized = _validate_pairs(n, pairs)
    if topology == "path" and any(j != i + 1 for i, j in normalized):
        raise ValueError("path topology requires nearest-neighbour pairs")
    if topology == "cycle" and any((j - i not in {1, n - 1}) for i, j in normalized):
        raise ValueError("cycle topology requires circular-nearest pairs")
    if topology == "disjoint":
        vertices = [q for pair in normalized for q in pair]
        if len(set(vertices)) != len(vertices):
            raise ValueError("disjoint topology cannot reuse a qubit")


def compile_iqp(
    n: int,
    singles: Sequence[float],
    pairs: Sequence[tuple[int, int, float]],
    *,
    topology: str = "arbitrary_weight2",
    quantize: bool = True,
) -> CompiledCircuit:
    """Compile weight-1/2 IQP generators into local Z phases and CP gates.

    For a pair term, the identity is
    ``exp(i*t*ZiZj) = exp(-i*t) exp(i*t*Zi) exp(i*t*Zj) CP(4*t)``.
    The optical implementation of each local Z phase uses PS(-2*t); the
    negative sign is retained in gate metadata and is not folded into CP.
    """

    if int(n) != n or n < 1:
        raise ValueError("n must be a positive integer")
    n = int(n)
    if len(singles) != n:
        raise ValueError(f"expected {n} single angles, got {len(singles)}")
    singles_f = tuple(_finite(value, f"single[{idx}]") for idx, value in enumerate(singles))
    pair_rows = [(int(i), int(j), _finite(theta, f"pair[{i},{j}]")) for i, j, theta in pairs]
    pair_indices = _validate_pairs(n, [(i, j) for i, j, _ in pair_rows])
    validate_topology(n, pair_indices, topology)
    theta_by_pair = {(min(i, j), max(i, j)): theta for i, j, theta in pair_rows}

    pair_data: list[tuple[tuple[int, int], QuantizedAngle]] = []
    gates: list[CompiledGate] = []
    for index, theta in enumerate(singles_f):
        gates.append(
            CompiledGate(
                "single",
                (index,),
                theta,
                metadata={"optical_phase": -2.0 * theta, "sign": "negative_PS"},
            )
        )
    for pair in pair_indices:
        raw = theta_by_pair[pair]
        angle = quantize_theta(raw) if quantize else QuantizedAngle(
            raw_theta=raw,
            raw_alpha=4.0 * raw,
            key=-1,
            wrapped_alpha=wrap_angle(4.0 * raw),
            winding=0,
            lifted_alpha=4.0 * raw,
            lifted_theta=raw,
        )
        pair_data.append((pair, angle))
        effective = angle.lifted_theta
        gates.extend(
            [
                CompiledGate(
                    "pair_compensation",
                    (pair[0],),
                    effective,
                    metadata={"optical_phase": -2.0 * effective, "lifted_theta": effective, "sign": "negative_PS", "pair": pair},
                ),
                CompiledGate(
                    "pair_compensation",
                    (pair[1],),
                    effective,
                    metadata={"optical_phase": -2.0 * effective, "lifted_theta": effective, "sign": "negative_PS", "pair": pair},
                ),
                CompiledGate(
                    "cp",
                    pair,
                    effective,
                    alpha=angle.wrapped_alpha,
                    key=angle.key if quantize else None,
                    metadata={
                        "raw_theta": raw,
                        "lifted_theta": effective,
                        "wrapped_alpha": angle.wrapped_alpha,
                        "implementation": "bare_CP",
                    },
                ),
            ]
        )
    return CompiledCircuit(
        n=n,
        singles=singles_f,
        pair_angles=tuple(pair_data),
        gates=tuple(gates),
        topology=topology,
        quantized=quantize,
        metadata={"compiler": "merlin_iqp.deploy.compile", "alpha_step": ALPHA_STEP, "alpha_keys": 63},
    )


def compile_generators(
    generators: np.ndarray,
    theta: Sequence[float],
    *,
    topology: str = "arbitrary_weight2",
    quantize: bool = True,
) -> CompiledCircuit:
    """Adapter for a binary generator matrix with weight 1/2 rows."""

    G = np.asarray(generators)
    values = np.asarray(theta, dtype=float)
    if G.ndim != 2 or values.ndim != 1 or G.shape[0] != values.size:
        raise ValueError("generators must be a 2-D matrix matching theta")
    n = int(G.shape[1])
    if not np.all(np.isfinite(G)) or not np.all(np.isin(G, (0, 1))):
        raise ValueError("generators must be finite binary rows")
    singles = np.zeros(n, dtype=float)
    pairs: list[tuple[int, int, float]] = []
    for row, angle in zip(G.astype(int), values):
        support = tuple(np.flatnonzero(row))
        if len(support) == 1:
            singles[support[0]] += _finite(angle, "theta")
        elif len(support) == 2:
            pairs.append((support[0], support[1], _finite(angle, "theta")))
        else:
            raise ValueError(f"unsupported generator weight {len(support)}; only weights 1 and 2 are compiled")
    return compile_iqp(n, singles, pairs, topology=topology, quantize=quantize)
