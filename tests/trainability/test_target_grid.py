import itertools

import numpy as np
import pytest

from merlin_iqp.generator.data import compute_p_real, load_circles_data
from merlin_iqp.generator.natural_grid import make_natural_bin_centers
from merlin_iqp.trainability.target_grid import (
    _nearest_bin_p_real,
    bitstring_dict_to_vector,
    make_target_grid,
)


@pytest.mark.parametrize("n", [1, 2, 3, 4, 5])
def test_bin_index_bijection(n):
    _, _, bin_index_fn = make_target_grid(n)
    bitstrings = ["".join(b) for b in itertools.product("01", repeat=n)]
    indices = sorted(bin_index_fn(b) for b in bitstrings)
    assert indices == list(range(2**n))


@pytest.mark.parametrize("n", [2, 4, 6])
def test_p_real_validity(n):
    centers, p_real, _ = make_target_grid(n)
    assert centers.shape == (2**n, 2)
    assert p_real.shape == (2**n,)
    assert np.all(p_real >= 0)
    assert np.isclose(p_real.sum(), 1.0, atol=1e-9)


def test_cross_validation_against_compute_p_real():
    """The load-bearing check this plan's must_haves require: proves the
    numpy nearest-bin-assignment port in trainability/target_grid.py is a
    faithful re-implementation of the existing, already-tested torch
    generator/data.py::compute_p_real -- not a plausible-looking but subtly
    different one. Reproduces v1.0's EXACT make_natural_bin_centers() grid
    shape (21x22=462, lo=-0.1, hi=1.1).

    Compares at float32 -- compute_p_real/make_natural_bin_centers' actual
    default precision -- rather than target_grid.py's own float64 default.
    This repo's data (generator/data.py::load_circles_data, seeded) contains
    one training point that lands exactly on the y-midpoint between two
    adjacent grid rows at this 21x22 shape: a genuine (not a bug) floating-
    point tie whose winner depends on distance-formula rounding, so an
    apples-to-apples comparison requires matching precision, not just
    matching algorithm."""
    rows, cols, lo, hi = 21, 22, -0.1, 1.1

    xs = np.linspace(lo, hi, rows)
    ys = np.linspace(lo, hi, cols)
    gx, gy = np.meshgrid(xs, ys, indexing="ij")
    numpy_centers = np.stack([gx.ravel(), gy.ravel()], axis=1).astype(np.float32)

    X_train, _ = load_circles_data()
    numpy_p_real = _nearest_bin_p_real(X_train.numpy().astype(np.float32), numpy_centers)

    torch_bin_centers = make_natural_bin_centers(rows=rows, cols=cols, lo=lo, hi=hi)
    torch_p_real = compute_p_real(X_train, torch_bin_centers).numpy()

    assert numpy_p_real.shape == torch_p_real.shape == (rows * cols,)
    assert np.allclose(numpy_p_real, torch_p_real, atol=1e-9)


def test_bitstring_dict_to_vector_round_trip():
    n = 2
    _, _, bin_index_fn = make_target_grid(n)
    d = {"00": 0.3, "11": -0.1}

    vec = bitstring_dict_to_vector(d, n, bin_index_fn)

    assert vec.shape == (2**n,)
    assert vec[bin_index_fn("00")] == pytest.approx(0.3)
    assert vec[bin_index_fn("11")] == pytest.approx(-0.1)

    remaining_indices = set(range(2**n)) - {bin_index_fn("00"), bin_index_fn("11")}
    for idx in remaining_indices:
        assert vec[idx] == 0.0
