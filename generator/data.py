import numpy as np
import torch
from sklearn.datasets import make_circles
from sklearn.model_selection import train_test_split


def load_circles_data() -> tuple[torch.Tensor, torch.Tensor]:
    """Reproduces quickstart.py's data pipeline (same n_samples=400, same
    train_test_split(test_size=0.2, random_state=42), same train-derived min-max
    normalization — min/max computed from X_train only, then applied to both
    splits, which is why X_test can slightly overshoot [0,1], the reason
    bin_centers.py pads to [-0.1, 1.1]).

    Deviation from quickstart.py: make_circles() here is seeded (random_state=42)
    where quickstart.py's is not. quickstart.py never needed run-to-run
    reproducibility of the raw points; this module does, since p_real must be a
    stable target for Phase 3 training and a stable Phase 5 benchmark reference.
    Without this, two calls produce different circle points even with
    train_test_split's seed fixed, since the split seed only controls how an
    already-random X gets partitioned, not X's contents."""
    X, y = make_circles(n_samples=400, random_state=42)
    X_train, X_test, _, _ = train_test_split(X, y, test_size=0.2, random_state=42)

    min_vals = X_train.min(axis=0, keepdims=True)
    max_vals = X_train.max(axis=0, keepdims=True)
    X_train = (X_train - min_vals) / np.clip(max_vals - min_vals, a_min=1e-6, a_max=None)
    X_test = (X_test - min_vals) / np.clip(max_vals - min_vals, a_min=1e-6, a_max=None)

    return torch.tensor(X_train, dtype=torch.float32), torch.tensor(X_test, dtype=torch.float32)


def compute_p_real(data_xy: torch.Tensor, bin_centers: torch.Tensor) -> torch.Tensor:
    """data_xy: (N,2) points already in the bin-centers' coordinate space.
    bin_centers: (K,2). Returns (K,) probability vector: non-negative, sums to 1.
    Nearest-bin-center assignment (not grid-edge histogram) — same distance
    machinery and source-of-truth grid the MMD kernel will use (02-RESEARCH.md
    Pattern 2)."""
    dists = torch.cdist(data_xy, bin_centers, p=2)
    nearest = dists.argmin(dim=1)
    counts = torch.bincount(nearest, minlength=bin_centers.shape[0]).float()
    return counts / counts.sum()
