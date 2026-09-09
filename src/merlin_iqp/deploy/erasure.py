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
    """Return a model-derived erasure instrument with explicit normalization.

    This is a synthetic conditional output model.  It does not claim to
    recover failed-gate, collision, or multiphoton Fock outcomes.  With
    ``retained=None``, every exact surviving-qubit subset is enumerated.  With
    a retained subset, only the exact event in which that subset survives is
    represented, with the plan-defined mass
    ``eta**len(retained) * (1-eta)**(n-len(retained))``.  When
    ``include_failure`` is true, all unrepresented mass (gate failure and any
    unselected erasure event) is placed in ``FAILURE`` and the result sums to
    one.  When false, the result is the represented subdistribution and its
    sum is the represented mass.
    """

    keys, values, n = _as_vector(q, None)
    eta = float(eta)
    gate_success = float(gate_success)
    if not np.isfinite(eta) or not 0.0 <= eta <= 1.0:
        raise ValueError("eta must be in [0,1]")
    if not np.isfinite(gate_success) or not 0.0 <= gate_success <= 1.0:
        raise ValueError("gate_success must be in [0,1]")
    if not np.all(np.isfinite(values)) or np.any(values < 0.0) or not np.isclose(values.sum(), 1.0, atol=1e-12):
        raise ValueError("q must be a normalized nonnegative distribution")
    if retained is None:
        keep = ()
    else:
        raw_indices = tuple(retained)
        if any(isinstance(i, (bool, np.bool_)) or not isinstance(i, (int, np.integer)) for i in raw_indices):
            raise ValueError("retained qubits must be integer indices")
        keep = tuple(sorted(set(int(i) for i in raw_indices)))
    if any(i < 0 or i >= n for i in keep):
        raise ValueError("retained qubit out of range")
    output: dict[str, float] = {}
    surviving_sets = (
        [set(keep)]
        if retained is not None
        else [set(indices) for r in range(n + 1) for indices in combinations(range(n), r)]
    )
    represented_mass = 0.0
    for surviving in surviving_sets:
        erased_set = set(range(n)) - surviving
        probability = eta ** len(surviving) * (1.0 - eta) ** len(erased_set)
        represented_mass += gate_success * probability
        for bitstring, mass in zip(keys, values):
            rendered = "".join(bitstring[index] if index in surviving else "E" for index in range(n))
            output[rendered] = output.get(rendered, 0.0) + gate_success * probability * float(mass)
    if include_failure:
        output["FAILURE"] = 1.0 - represented_mass
    return output
