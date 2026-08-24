"""K=400 (20x20) uniform spatial-bin grid used by the original ``train.py``/
``sweep.py`` baseline. See ``natural_grid.py`` for the K=462 successor grid
that avoids MerLin's ModGrouping fold."""

import numpy as np
import torch


def make_bin_centers(
    side: int = 20,
    lo: float = -0.1,
    hi: float = 1.1,
    dtype: torch.dtype = torch.float32,
) -> torch.Tensor:
    """K = side*side uniform grid centers over [lo, hi]^2. Deterministic, no RNG."""
    xs = np.linspace(lo, hi, side)
    ys = np.linspace(lo, hi, side)
    gx, gy = np.meshgrid(xs, ys, indexing="ij")
    centers = np.stack([gx.ravel(), gy.ravel()], axis=1)  # shape (side*side, 2)
    return torch.tensor(centers, dtype=dtype)
