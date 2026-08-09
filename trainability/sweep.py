"""Gradient-variance sweep runner: wires Plans 17-01 (parameter-shift),
17-02 (exact MMD^2 gradient), and 17-03 (per-n target grid) together into
the one function TRAIN-01 requires -- `run_gradient_variance_sweep`.

Pooling design (deliberate, per TRAIN-01): for a given (n, generator_scope,
init_scheme), gradients are POOLED across BOTH the tracked parameter
indices AND the draws into a single flat array before summarizing.
TRAIN-01 asks for variance across the parameter LANDSCAPE (the classic
barren-plateau question: "how does Var[d(loss)/d(theta)] scale with n?"),
not a per-parameter-identity breakdown -- so this function reports one
summary-stats cell per (n, generator_scope, init_scheme), not one per
tracked parameter index.

No retry/checkpointing/resumability here -- this is a plain, pure
computation over its inputs. Plan 17-06 (which runs the actual expensive
sweep) decides at execution time whether that's needed.
"""

import numpy as np

from iqp_photonic_encoding import (
    photonic_iqp_distribution,
    photonic_weight2_iqp_distribution,
)
from trainability import mmd_exact, param_shift, target_grid
from trainability import rng as rng_mod
from trainability import stats

SIGMA = 0.1  # v1.0's established bandwidth (CONTEXT.md: reuse v1.0's convention as-is)


def sample_thetas(rng, n, init_scheme):
    """Draw n circuit parameters under one of the two locked init regimes."""
    if init_scheme == "small_angle":
        return rng.uniform(-0.1, 0.1, size=n).tolist()
    if init_scheme == "uniform":
        return rng.uniform(0, 2 * np.pi, size=n).tolist()
    raise ValueError(f"unknown init_scheme: {init_scheme!r}")


def pick_tracked_indices(n, max_tracked_params):
    """Evenly-spaced, deduplicated, sorted parameter indices to track.

    Never returns more than min(max_tracked_params, n) indices, and every
    index is in range(n).
    """
    cap = min(max_tracked_params, n)
    idx = sorted(set(np.linspace(0, n - 1, cap).round().astype(int).tolist()))
    return idx


def run_gradient_variance_sweep(
    n_values,
    generator_scope,
    init_scheme,
    n_draws=100,
    max_tracked_params=3,
    weight2_pair=(0, 1),
    seed_base=170917,
):
    """Pooled exact-gradient-variance sweep across a set of system sizes.

    For each n in n_values: draws n_draws parameter vectors (per
    init_scheme), computes the exact parameter-shift MMD^2 gradient
    (composing Plans 17-01+17-02+17-03) at each of a capped set of tracked
    parameter indices, pools all (tracked index x draw) gradients into one
    array, and summarizes it.

    generator_scope: "weight1" (photonic_iqp_distribution only) or "mixed"
      (photonic_weight2_iqp_distribution over weight2_pair=(i, j), which
      requires n >= 2).

    Returns a list of per-n result dicts:
      {"n": n, "generator_scope": ..., "init_scheme": ...,
       "n_tracked_params": ..., **summarize_gradient_samples(pooled_grads)}
    """
    if not n_values:
        raise ValueError("n_values must be non-empty")
    if any(n < 1 for n in n_values):
        raise ValueError(f"all n_values must be >= 1, got {n_values!r}")
    if generator_scope not in ("weight1", "mixed"):
        raise ValueError(f"unknown generator_scope: {generator_scope!r}")

    results = []
    for n in n_values:
        if generator_scope == "mixed" and n < 2:
            raise ValueError(
                f"generator_scope='mixed' requires n >= 2 (weight2_pair needs "
                f"two distinct qubits), got n={n}"
            )

        centers, p_real, bin_index_fn = target_grid.make_target_grid(n)
        K = mmd_exact.gaussian_kernel_matrix_np(centers, SIGMA)
        tracked = pick_tracked_indices(n, max_tracked_params)

        accumulator = []
        for draw in range(n_draws):
            draw_rng = rng_mod.get_rng(seed_base, generator_scope, init_scheme, n, draw)
            thetas = sample_thetas(draw_rng, n, init_scheme)

            if generator_scope == "weight1":
                q_dist, _q_residual = photonic_iqp_distribution(n, thetas)
            else:
                i, j = weight2_pair
                q_dist, _q_residual, _q_herald_fail = photonic_weight2_iqp_distribution(
                    n, i, j, thetas
                )
            q_vec = target_grid.bitstring_dict_to_vector(q_dist, n, bin_index_fn)

            for k in tracked:
                if generator_scope == "weight1":
                    delta, _resid_diag = param_shift.weight1_param_shift_delta(n, thetas, k)
                else:
                    i, j = weight2_pair
                    delta, _resid_diag, _herald_diag = param_shift.weight2_param_shift_delta(
                        n, i, j, thetas, k
                    )
                dq = target_grid.bitstring_dict_to_vector(delta, n, bin_index_fn)
                grad = mmd_exact.mmd2_grad(q_vec, p_real, K, dq)
                accumulator.append(grad)

        pooled_grads = np.array(accumulator)
        result = {
            "n": n,
            "generator_scope": generator_scope,
            "init_scheme": init_scheme,
            "n_tracked_params": len(tracked),
            **stats.summarize_gradient_samples(pooled_grads),
        }
        results.append(result)

    return results
