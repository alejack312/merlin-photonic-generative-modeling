import numpy as np
import torch


def make_natural_bin_centers(
    rows: int = 21,
    cols: int = 22,
    lo: float = -0.1,
    hi: float = 1.1,
    dtype: torch.dtype = torch.float32,
) -> torch.Tensor:
    """K = rows*cols uniform grid centers over [lo, hi]^2. Deterministic, no RNG.

    Same meshgrid(indexing="ij") + ravel() convention as bin_centers.py's
    make_bin_centers, but deliberately non-square: 21*22 = 462 matches exactly
    the natural output width of QuantumLayer.simple(input_size=10), so nothing
    has to be folded down by MerLin's ModGrouping post-processing. Kept as a
    separate function so make_bin_centers (and every checkpoint/script built on
    its 400-bin grid) is untouched.
    """
    xs = np.linspace(lo, hi, rows)
    ys = np.linspace(lo, hi, cols)
    gx, gy = np.meshgrid(xs, ys, indexing="ij")
    centers = np.stack([gx.ravel(), gy.ravel()], axis=1)  # shape (rows*cols, 2)
    return torch.tensor(centers, dtype=dtype)
