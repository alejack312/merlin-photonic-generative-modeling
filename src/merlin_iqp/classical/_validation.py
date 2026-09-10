"""Small validation and hashing helpers shared by the classical modules."""

from __future__ import annotations

import hashlib
import json
from typing import Any

import numpy as np


def finite_vector(value: Any, *, name: str, length: int | None = None) -> np.ndarray:
    array = np.asarray(value, dtype=np.float64)
    if array.ndim != 1:
        raise ValueError(f"{name} must be one-dimensional")
    if length is not None and array.shape != (length,):
        raise ValueError(f"{name} must have shape ({length},), got {array.shape}")
    if not np.all(np.isfinite(array)):
        raise ValueError(f"{name} must contain only finite values")
    return array


def binary_matrix(value: Any, *, name: str, width: int | None = None) -> np.ndarray:
    array = np.asarray(value)
    if array.ndim != 2:
        raise ValueError(f"{name} must have shape (rows, width)")
    if width is not None and array.shape[1] != width:
        raise ValueError(f"{name} must have width {width}, got {array.shape[1]}")
    if array.shape[0] == 0:
        raise ValueError(f"{name} must contain at least one row")
    if not np.all(np.isfinite(array)) or not np.all((array == 0) | (array == 1)):
        raise ValueError(f"{name} must contain only finite binary values")
    return array.astype(np.uint8, copy=True)


def binary_vector(value: Any, *, name: str, width: int | None = None) -> np.ndarray:
    array = np.asarray(value)
    if array.ndim != 1:
        raise ValueError(f"{name} must be one-dimensional")
    if width is not None and array.shape != (width,):
        raise ValueError(f"{name} must have shape ({width},), got {array.shape}")
    if not np.all(np.isfinite(array)) or not np.all((array == 0) | (array == 1)):
        raise ValueError(f"{name} must contain only finite binary values")
    return array.astype(np.uint8, copy=True)


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)


def hash_array(value: np.ndarray) -> str:
    array = np.ascontiguousarray(value)
    digest = hashlib.sha256()
    digest.update(str(array.dtype).encode("ascii"))
    digest.update(repr(array.shape).encode("ascii"))
    digest.update(array.tobytes())
    return digest.hexdigest()


def hash_json(value: Any) -> str:
    return hashlib.sha256(canonical_json(value).encode("utf-8")).hexdigest()
