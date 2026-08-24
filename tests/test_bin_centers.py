import torch
import pytest
import numpy as np
from merlin_iqp.generator.bin_centers import make_bin_centers

def test_make_bin_centers():
    centers = make_bin_centers()
    # shape is (400, 2) for defaults
    assert centers.shape == (400, 2)
    # two separate calls return tensors that are torch.equal (proves determinism)
    assert torch.all(torch.isfinite(centers))
    # min/max on both axes are pytest.approx(-0.1) / pytest.approx(1.1) (proves bounding-box coverage)
    assert torch.all(centers >= -0.1)
    assert torch.all(centers <= 1.1)
    
    assert centers.min() == pytest.approx(-0.1) 
    assert centers.max() == pytest.approx(1.1) # proves bounding-box coverage
    
    a = make_bin_centers()
    b = make_bin_centers()
    assert torch.equal(a, b) # proves determinism
  