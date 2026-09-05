"""Explicit parameter initialization, including the sibling parity recipe."""

from __future__ import annotations

from typing import Any

import numpy as np

from .rng import make_rng
from .targets import target_moments
from ._validation import binary_matrix


def initialize_theta(G: np.ndarray, seed: int, *, scheme: str = "small_angle", scale: float = 0.1, target: object | None = None, std: float | None = None, return_metadata: bool = False) -> np.ndarray | tuple[np.ndarray, dict[str, Any]]:
    matrix = binary_matrix(G, name="G")
    if not np.isfinite(scale) or scale < 0:
        raise ValueError("scale must be finite and non-negative")
    rng = make_rng(seed)
    if scheme in {"small_angle", "normal"}:
        deviation = float(scale if std is None else std)
        if deviation < 0 or not np.isfinite(deviation):
            raise ValueError("std must be finite and non-negative")
        theta = rng.normal(0.0, deviation, size=len(matrix)).astype(np.float64)
        metadata = {"scheme": "small_angle", "std": deviation, "seed": int(seed)}
    elif scheme == "uniform":
        theta = rng.uniform(-scale, scale, size=len(matrix)).astype(np.float64)
        metadata = {"scheme": scheme, "low": -scale, "high": scale, "seed": int(seed)}
    elif scheme == "parity":
        if target is None:
            raise ValueError("parity initialization requires target")
        moments = target_moments(target, matrix)
        theta = scale * moments.values
        metadata = {"scheme": scheme, "scale": float(scale), "seed": int(seed), "target_representation": moments.representation}
    else:
        raise ValueError(f"unknown initialization scheme {scheme!r}")
    return (theta, metadata) if return_metadata else theta
