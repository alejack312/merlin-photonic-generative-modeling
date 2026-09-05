"""Conditional/model-derived output erasure artifact."""

from __future__ import annotations

from itertools import combinations
from typing import Mapping, Sequence

import numpy as np


def _as_vector(q: Mapping[str, float] | Sequence[float], n: int | None) -> tuple[list[str], np.ndarray, int]:
    if isinstance(q, Mapping):
        keys = sorted(str(key) for key in q)
        if not keys:
            raise ValueError("q must not be empty")
        width = len(keys[0])
        if any(len(key) != width or set(key) - {"0", "1"} for key in keys):
            raise ValueError("q keys must be equal-width binary strings")
        values = np.array([float(q[key]) for key in keys], dtype=float)
        ordered = [format(index, f"0{width}b") for index in range(2**width)]
        values = np.array([float(q.get(key, 0.0)) for key in ordered])
        return ordered, values, width
    values = np.asarray(q, dtype=float)
    if values.ndim != 1 or values.size == 0 or values.size & (values.size - 1):
        raise ValueError("q must be a non-empty vector of length 2**n")
    width = int(round(np.log2(values.size)))
    if n is not None and int(n) != width:
        raise ValueError("n does not match q length")
    return [format(index, f"0{width}b") for index in range(values.size)], values, width


def conditional_erasure_distribution(
    q: Mapping[str, float] | Sequence[float],
    eta: float,
    *,
    retained: Sequence[int] | None = None,
    gate_success: float = 1.0,
    include_failure: bool = True,
) -> dict[str, float]:
    """Return {0,1,E} outputs conditioned on gate success plus FAILURE mass.

    This is a synthetic conditional output model.  It does not claim to
    recover failed-gate, collision, or multiphoton Fock outcomes.
    """

    keys, values, n = _as_vector(q, None)
    eta = float(eta)
    gate_success = float(gate_success)
    if not np.isfinite(eta) or not 0.0 <= eta <= 1.0:
        raise ValueError("eta must be in [0,1]")
    if not np.isfinite(gate_success) or not 0.0 <= gate_success <= 1.0:
        raise ValueError("gate_success must be in [0,1]")
    if np.any(values < -1e-12) or not np.isclose(values.sum(), 1.0, atol=1e-12):
        raise ValueError("q must be a normalized nonnegative distribution")
    keep = () if retained is None else tuple(sorted(set(int(i) for i in retained)))
    if any(i < 0 or i >= n for i in keep):
        raise ValueError("retained qubit out of range")
    output: dict[str, float] = {}
    for r in range(n + 1):
        for erased in combinations(range(n), r):
            erased_set = set(erased)
            if erased_set.intersection(keep):
                continue
            probability = eta ** (n - r) * (1.0 - eta) ** r
            for bitstring, mass in zip(keys, values):
                rendered = "".join("E" if index in erased_set else bitstring[index] for index in range(n))
                output[rendered] = output.get(rendered, 0.0) + gate_success * probability * float(mass)
    if include_failure:
        output["FAILURE"] = 1.0 - gate_success
    return output
