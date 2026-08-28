import pytest
import torch

from merlin_iqp.generator.natural_grid import make_natural_bin_centers


def test_natural_grid_shape_and_bounds():
    centers = make_natural_bin_centers()
    assert centers.shape == (462, 2)  # 21*22 == the circuit's natural output width
    assert torch.all(torch.isfinite(centers))
    assert centers.min() == pytest.approx(-0.1)
    assert centers.max() == pytest.approx(1.1)


def test_natural_grid_is_deterministic():
    assert torch.equal(make_natural_bin_centers(), make_natural_bin_centers())


def test_natural_grid_row_major_ordering():
    # Pitfall guard: a transposed grid (cols x rows) would still pass the shape
    # and bounds checks above, since the total count and bounding box are
    # identical -- only the ordering differs, and ordering is the whole point of
    # this module. centers[0] is the (lo,lo) corner and the first `cols` entries
    # sweep the second coordinate while the first stays at lo.
    rows, cols = 21, 22
    centers = make_natural_bin_centers(rows=rows, cols=cols)
    assert centers[0].tolist() == pytest.approx([-0.1, -0.1])
    assert centers[cols - 1].tolist() == pytest.approx([-0.1, 1.1])
    assert centers[cols][0].item() > centers[0][0].item()
