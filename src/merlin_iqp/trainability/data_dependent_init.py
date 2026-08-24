"""Data-dependent initialization primitives (TRAIN-10).

Implements Recio-Armengol et al.'s (arXiv:2503.02934, Sec. 8.1.2)
data-dependent init recipe, translated onto this project's grid-bin target
representation (`trainability/target_grid.py::make_target_grid`'s `p_real`)
rather than their original raw-training-data-mean formulation.

Pure numpy, fully deterministic, no random component. No dependency on
`trainability.target_grid` or any other project module -- callers pass
`p_real` in directly, matching this package's existing single-concern-per-
module convention (`mmd_exact.py`/`param_shift.py`/`target_grid.py`/`rng.py`/
`stats.py`/`curve_fit.py` are all single-purpose files with no cross-imports
beyond numpy).

Bit-ordering convention (the load-bearing correctness question, per
17.1-RESEARCH.md Pitfall 3): `target_grid.py::make_target_grid`'s
`bin_index_fn(bitstring) = int(bitstring, 2)` treats `bitstring[0]`
(leftmost char) as the bitstring's MOST significant bit, and
`iqp_photonic_encoding.py::fock_to_bitstring` builds that string
left-to-right in qubit order (qubit 0 first). So bit `k` (qubit `k`'s value)
sits at bit-position `n-1-k` (0-indexed from the LSB) of the integer bin
index: `bit_k(bin_index, k, n) = (bin_index >> (n-1-k)) & 1`. This is
proven the exact inverse of `bin_index_fn`'s `int(bitstring, 2)` convention
for every qubit position by `tests/test_data_dependent_init.py`'s dedicated
spot-check, not merely assumed.
"""

import numpy as np


def bit_k(bin_index: int, k: int, n: int) -> int:
    """Qubit k's bit value within a bin index built by bin_index_fn(bitstring) =
    int(bitstring, 2), where bitstring[k] corresponds to qubit k (MSB-first,
    matching trainability/target_grid.py's convention)."""
    return (bin_index >> (n - 1 - k)) & 1


def empirical_mean_bit(p_real: np.ndarray, k: int, n: int) -> float:
    """P(bit k == 1) under p_real -- this project's stand-in for
    Recio-Armengol et al.'s <x_j> = mean of the jth dimension of the training
    data (arXiv:2503.02934, Sec 8.1.2)."""
    idx = np.arange(2**n)
    bits_k = (idx >> (n - 1 - k)) & 1
    return float(np.sum(p_real * bits_k))


def weight1_data_dependent_theta(p_real: np.ndarray, n: int) -> list:
    """arcsin(sqrt(<x_k>)) per qubit k -- the paper's single-qubit-gate init
    rule. Never raises at the arcsin domain boundary: a bit-marginal of
    exactly 0.0 or 1.0 is a valid probability, so arcsin(sqrt(...)) is always
    well-defined here -- no clipping/guard needed."""
    return [float(np.arcsin(np.sqrt(empirical_mean_bit(p_real, k, n)))) for k in range(n)]


def empirical_pm1_covariance(p_real: np.ndarray, j: int, k: int, n: int) -> float:
    """Cov(z_j, z_k) under p_real, z in {-1,+1} convention (the paper converts
    binary training data to +-1 before computing this)."""
    idx = np.arange(2**n)
    zj = 2 * ((idx >> (n - 1 - j)) & 1) - 1
    zk = 2 * ((idx >> (n - 1 - k)) & 1) - 1
    return float(np.sum(p_real * zj * zk) - np.sum(p_real * zj) * np.sum(p_real * zk))


def weight2_data_dependent_theta(
    p_real: np.ndarray, i: int, j: int, n: int, scale_factor: float
) -> float:
    """scale_factor * Cov(z_i, z_j) -- the paper's two-qubit-gate init rule;
    scale_factor is the paper's own free hyperparameter (their Table 2
    searched [0.0001, 1.0])."""
    return scale_factor * empirical_pm1_covariance(p_real, i, j, n)
