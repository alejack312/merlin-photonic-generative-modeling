"""Deterministic, reorder-safe RNG substream utility.

This repo has no existing convention of its own for this (17-RESEARCH.md's
Don't-Hand-Roll table recommends mirroring the sibling project's
`derive_seed`/`split_rng` SHAPE, not its code verbatim). Each seed is a pure
hash of its own full labeled coordinate tuple -- e.g.
(n, generator_scope, init_scheme, draw_index) -- never a running counter, so
adding or reordering a system size, init scheme, or draw index elsewhere can
never silently reshuffle any OTHER setting's random draws.
"""

import hashlib

import numpy as np


def derive_seed(*parts) -> int:
    """Stable integer seed from arbitrary labeled parts.

    Adding/reordering a setting elsewhere never shifts another setting's
    seed, since each seed is a pure hash of its own full coordinate tuple,
    not a running counter. `repr(tuple(parts))` disambiguates types (e.g.
    int 3 vs str "3") and part order, so distinct coordinates essentially
    never collide.
    """
    payload = repr(tuple(parts)).encode("utf-8")
    digest = hashlib.blake2b(payload, digest_size=8).digest()
    return int.from_bytes(digest, "big") % (2**31 - 1)


def get_rng(*parts) -> np.random.Generator:
    """Deterministic numpy Generator for the given labeled coordinate.

    Same `parts` always yields the same seed (and thus the same draw
    sequence); different `parts` yield independent streams.
    """
    return np.random.default_rng(derive_seed(*parts))
