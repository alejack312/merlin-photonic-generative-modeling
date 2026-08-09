"""Per-n MMD target grid, generalizing v1.0's fixed K=462 grid.

v1.0's `generator/natural_grid.py::make_natural_bin_centers` (K=21*22=462) was
sized to match `ML.QuantumLayer.simple(input_size=10)`'s own Fock-state output
width -- an unrelated circuit's shape, not this project's `2^n`-outcome IQP
bitstring space, which changes at every n in Phase 17's trainability sweep
(17-RESEARCH.md Pitfall 3). This module builds a fresh `K=2^n` grid (and a
matching `{bitstring: probability|delta}` <-> length-`2^n` vector mapping) at
any n, so Plans 17-01/17-02's parameter-shift gradients and MMD^2 computation
have a target distribution to work against at every sweep point.

This GENERALIZES (does not replace) `generator/natural_grid.py`'s v1.0
machinery -- kept fully separate so no existing v1.0 script or checkpoint is
affected. `make_target_grid`'s nearest-bin-center assignment is a faithful
numpy re-implementation of `generator/data.py::compute_p_real` (same
algorithm: pairwise distance to bin centers, argmin, bincount, normalize) --
proven equivalent by cross-validating against the torch original at v1.0's own
462-bin grid shape in `tests/test_target_grid.py`, not just trusted by
construction.

Bin-index convention: `bin_index_fn(bitstring) = int(bitstring, 2)` -- the
bitstring's raw binary integer value. This is a deliberate but arbitrary
choice among several possible bitstring<->grid-index conventions
(17-RESEARCH.md Open Question 1). It is left undecided by anything else in
this project because it is low-risk here: Phase 17 only needs gradient-
variance MAGNITUDE (barren-plateau scaling), which is not expected to be
sensitive to which bitstring maps to which grid cell, unlike an actual
generative-training run where spatial smoothness of the bitstring<->2D-point
mapping would matter.
"""

import numpy as np
import torch

from generator.data import load_circles_data


def _nearest_bin_p_real(data_xy: np.ndarray, centers: np.ndarray) -> np.ndarray:
    """Numpy nearest-bin-center histogram, faithfully re-implementing
    generator/data.py::compute_p_real's algorithm (pairwise distance -> argmin
    -> bincount -> normalize), but without torch.

    Distances are computed via the squared-expansion form
    (||a||^2 - 2*a.b + ||b||^2, the same decomposition torch.cdist uses
    internally) rather than a direct elementwise-difference sum-of-squares.
    Both forms are mathematically equivalent, but for data points that are
    genuinely equidistant (to floating-point precision) from two bin centers
    -- confirmed to occur at v1.0's own 21x22 grid, where one training point
    lands exactly on the y-midpoint between two adjacent rows -- the two
    formulas round differently and can break the tie in opposite directions.
    Matching torch.cdist's formula (not just its output) makes this a
    bit-faithful port rather than a merely-equivalent one; verified in
    tests/test_target_grid.py to reproduce compute_p_real's bin assignment
    exactly, including at that tied point.

    data_xy: (N,2) numpy array, already in the bin-centers' coordinate space.
    centers: (K,2) numpy array.
    Returns (K,) numpy array: non-negative, sums to 1.

    Deliberately does NOT force a specific dtype -- ordinary numpy type
    promotion applies (e.g. float32 data_xy against float64 centers upcasts
    to float64, matching this module's own float64-centers default and
    preserving precision for the gradient-variance work downstream). Callers
    that need to reproduce compute_p_real's float32 default exactly (e.g. the
    v1.0 cross-validation test) must cast BOTH inputs to float32 themselves
    before calling.
    """
    a_sq = np.sum(data_xy**2, axis=1, keepdims=True)  # (N,1)
    b_sq = np.sum(centers**2, axis=1, keepdims=True).T  # (1,K)
    cross = data_xy @ centers.T  # (N,K)
    sq_dists = np.clip(a_sq - 2 * cross + b_sq, a_min=0, a_max=None)
    dists = np.sqrt(sq_dists)  # (N, K)
    nearest = np.argmin(dists, axis=1)  # (N,)
    counts = np.bincount(nearest, minlength=centers.shape[0]).astype(np.float64)
    return counts / counts.sum()


def make_target_grid(n: int, lo: float = -0.1, hi: float = 1.1):
    """Builds a 2^n-bin target grid over [lo,hi]^2 and its target distribution.

    rows = 2**((n+1)//2), cols = 2**(n//2), so rows*cols == 2**n EXACTLY for
    every n (no rounding -- e.g. n=3: rows=4, cols=2; n=6: rows=8, cols=8).
    Same meshgrid(indexing="ij") + ravel() convention as
    generator/natural_grid.py::make_natural_bin_centers, in plain numpy (no
    torch -- this whole subsystem is numpy-only, per Plans 17-01/17-02's
    established no-torch-in-production-path rule).

    Bin index idx (0-indexed, row-major, idx = row*cols + col) corresponds to
    centers[idx].

    Returns (centers, p_real, bin_index_fn):
      centers: np.ndarray (2**n, 2)
      p_real: np.ndarray (2**n,), non-negative, sums to 1.0
      bin_index_fn: str -> int, bin_index_fn(bitstring) = int(bitstring, 2)
    """
    rows = 2 ** ((n + 1) // 2)
    cols = 2 ** (n // 2)
    assert rows * cols == 2**n

    xs = np.linspace(lo, hi, rows)
    ys = np.linspace(lo, hi, cols)
    gx, gy = np.meshgrid(xs, ys, indexing="ij")
    centers = np.stack([gx.ravel(), gy.ravel()], axis=1)  # (2**n, 2)

    X_train, _ = load_circles_data()
    data_xy = X_train.numpy()

    p_real = _nearest_bin_p_real(data_xy, centers)

    def bin_index_fn(bitstring: str) -> int:
        return int(bitstring, 2)

    return centers, p_real, bin_index_fn


def bitstring_dict_to_vector(d: dict, n: int, bin_index_fn) -> np.ndarray:
    """Generic {bitstring: value} -> length-2^n numpy array utility.

    Used for BOTH actual probability distributions (from
    photonic_iqp_distribution/photonic_weight2_iqp_distribution) AND signed
    parameter-shift deltas (from Plan 17-01's weight1_param_shift_delta /
    weight2_param_shift_delta) -- does NOT assume non-negativity or sum-to-1,
    and does not normalize, since deltas can be negative and do not sum to a
    fixed value.

    result[bin_index_fn(x)] = v for each (x, v) in d.items(); 0.0 elsewhere.
    """
    result = np.zeros(2**n, dtype=np.float64)
    for bitstring, value in d.items():
        result[bin_index_fn(bitstring)] = value
    return result
