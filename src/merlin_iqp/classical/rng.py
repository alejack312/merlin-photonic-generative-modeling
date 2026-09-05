"""Deterministic, reorder-safe NumPy seed streams."""

from __future__ import annotations

import hashlib
import json
from typing import Any

import numpy as np


def derive_seed(base_seed: int, *parts: Any) -> int:
    payload = json.dumps(
        {"base_seed": int(base_seed), "parts": parts},
        sort_keys=True,
        separators=(",", ":"),
        default=str,
    ).encode("utf-8")
    return int.from_bytes(hashlib.blake2b(payload, digest_size=8).digest(), "big") % (2**31 - 1)


def make_rng(seed: int, *parts: Any) -> np.random.Generator:
    return np.random.default_rng(derive_seed(int(seed), *parts) if parts else int(seed))


def split_rng(rng: np.random.Generator, count: int) -> list[np.random.Generator]:
    if count < 1:
        raise ValueError("count must be positive")
    parent_seed = int(rng.integers(0, 2**31 - 1))
    return [np.random.default_rng(child) for child in np.random.SeedSequence(parent_seed).spawn(count)]
