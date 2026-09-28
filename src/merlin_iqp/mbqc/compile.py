"""Frozen IQP-to-M1 compilation boundary."""

from __future__ import annotations

from typing import Any

from .pattern import M1Pattern


def compile_m1(generator: Any, theta: Any, *, provenance: dict[str, Any] | None = None) -> M1Pattern:
    """Compile raw/effective IQP parameters into the fixed-basis M1 pattern."""

    return M1Pattern(
        G=generator,
        raw_theta=theta,
        effective_theta=theta,
        provenance={
            "compiler": "logical M1 incidence graph",
            "basis_policy": "fixed; no ideal feed-forward",
            **dict(provenance or {}),
        },
    )
