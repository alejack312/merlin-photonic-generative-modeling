"""Summary statistics over a pool of gradient samples.

Domain-agnostic (mean, variance, RMS, etc.) -- there is no meaningful "port"
to do here beyond matching the sibling project's general shape of "report
several angles on the same sample," not its implementation. Kept
self-contained (pure numpy, no dependency on the sibling project's code).
"""

import numpy as np


def summarize_gradient_samples(grads: np.ndarray) -> dict:
    """Summary statistics for a 1-D array of pooled gradient samples.

    Returns plain Python floats (not numpy scalars) for clean CSV/JSON
    serialization downstream.

    `rms` (root-mean-square, sqrt(mean(grads**2))) is included because raw
    gradient means can be near-zero by symmetry while the variance/RMS is
    the barren-plateau-relevant quantity (its scaling with n is what
    TRAIN-01/TRAIN-02 actually test).
    """
    grads = np.asarray(grads, dtype=np.float64)
    return {
        "n_samples": int(grads.size),
        "mean": float(np.mean(grads)),
        "var": float(np.var(grads)),
        "std": float(np.std(grads)),
        "median": float(np.median(grads)),
        "abs_mean": float(np.mean(np.abs(grads))),
        "rms": float(np.sqrt(np.mean(grads**2))),
    }
