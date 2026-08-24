"""Native-autograd gradient-variance sweep via dual_rail_merlin_encoding.py --
v3.0 Phase 17 analogue of trainability/sweep.py's parameter-shift-based
run_gradient_variance_sweep, using MerLin's native torch autograd on the
dual-rail encoding instead of hand-rolled parameter-shift on the
polarization encoding.

An independent cross-check, not a replacement: a different computational
method (native autograd vs. parameter-shift) AND a different physical
circuit (dual rail vs. polarization) answering the same barren-plateau
question. trainability/sweep.py and trainability/param_shift.py are
untouched.

Key structural advantage over parameter-shift: ONE forward+backward pass
gives gradients for ALL n circuit parameters simultaneously (torch
autograd), vs. parameter-shift's 2 Perceval circuit evaluations PER
tracked parameter. This module tracks ALL n parameters by default (no cap),
unlike trainability/sweep.py's max_tracked_params=3 convention -- the cost
no longer scales with tracked-parameter count, so capping would only throw
away free information. This is a stated, deliberate methodological
difference from the parameter-shift study, not a hidden one -- see any
downstream write-up comparing the two.

Differentiability constraint this module exists to satisfy: the ENTIRE
computation from MerLin's raw forward-pass output through to the scalar
MMD^2 loss must stay in torch tensors with requires_grad intact. Routing
through a plain Python dict (as dual_rail_merlin_encoding.py's own
dual_rail_photonic_iqp_distribution does, for interpretability) would break
the autograd graph. The bin-mapping matrix M below (precomputed once, no
grad, from the FIXED output_keys ordering) is what keeps the whole
q = M @ raw_output -> MMD^2(p, q) -> .backward() chain differentiable.
"""

import numpy as np
import perceval as pcvl
import torch

from merlin_iqp.encoding.dual_rail import (
    make_weight1_quantum_layer,
    make_weight2_quantum_layer,
)
from merlin_iqp.encoding.iqp_photonic import fock_to_bitstring
from merlin_iqp.trainability import mmd_exact, target_grid
from merlin_iqp.trainability import rng as rng_mod
from merlin_iqp.trainability.sweep import SIGMA, sample_thetas


def _build_bin_mapping(output_keys, n, bin_index_fn, K):
    """Precompute (once, no grad) a (K, len(output_keys)) 0/1 matrix mapping
    each MerLin output-state index to its target-grid bin index, for states
    that decode to a valid computational-basis bitstring (fock_to_bitstring,
    reused unmodified). Out-of-subspace states get an all-zero column --
    structurally impossible for weight-1 (verified: residual==0 always),
    genuinely possible for weight-2 (handled by the herald mask below, not
    by this matrix)."""
    M = torch.zeros(K, len(output_keys), dtype=torch.float32)
    for idx, key in enumerate(output_keys):
        state = pcvl.BasicState(list(key))
        bits = fock_to_bitstring(state, n)
        if bits is not None:
            M[bin_index_fn(bits), idx] = 1.0
    return M


def _setup_weight1(n):
    layer = make_weight1_quantum_layer(n)
    theta_tensor = dict(layer.named_parameters())["theta"]
    centers, p_real_np, bin_index_fn = target_grid.make_target_grid(n)
    M = _build_bin_mapping(layer.output_keys, n, bin_index_fn, 2**n)
    return layer, theta_tensor, M, None, centers, p_real_np


def _setup_mixed(n, i, j):
    layer, herald_spec = make_weight2_quantum_layer(n, i, j)
    theta_tensor = dict(layer.named_parameters())["theta"]
    centers, p_real_np, bin_index_fn = target_grid.make_target_grid(n)

    ancilla_a, ancilla_b = 2 * n, 2 * n + 1
    expected_a, expected_b = herald_spec[4], herald_spec[5]
    M = torch.zeros(2**n, len(layer.output_keys), dtype=torch.float32)
    herald_ok = torch.zeros(len(layer.output_keys), dtype=torch.float32)
    for idx, key in enumerate(layer.output_keys):
        if key[ancilla_a] != expected_a or key[ancilla_b] != expected_b:
            continue
        herald_ok[idx] = 1.0
        state = pcvl.BasicState(list(key))
        bits = fock_to_bitstring(state, n)
        if bits is not None:
            M[bin_index_fn(bits), idx] = 1.0
    return layer, theta_tensor, M, herald_ok, centers, p_real_np


def pooled_native_gradients_for_cell(
    n,
    generator_scope,
    init_scheme,
    draw_start,
    draw_count,
    weight2_pair=(0, 1),
    seed_base=170917,
):
    """Native-autograd analogue of trainability.sweep.pooled_gradients_for_cell:
    for draw indices [draw_start, draw_start+draw_count), builds the MerLin
    QuantumLayer ONCE (reused across draws -- only theta values change
    between draws, not circuit topology), computes the differentiable MMD^2
    loss via the precomputed bin-mapping matrix M, and gets ALL n
    parameters' gradients from ONE .backward() call per draw.

    generator_scope: "weight1" (make_weight1_quantum_layer) or "mixed"
      (make_weight2_quantum_layer over weight2_pair=(i,j), n >= 2).

    Uses the SAME deterministic RNG substreams (trainability/rng.py) as
    trainability.sweep.pooled_gradients_for_cell -- draw k's theta values
    are bit-identical to what the parameter-shift study drew for the same
    (n, generator_scope, init_scheme, draw) coordinate, so any difference
    in results traces to the computational method / physical encoding, not
    to different random parameter draws.

    Returns (pooled_grads: np.ndarray of length draw_count*n, n_tracked_params)
    -- n_tracked_params == n always (no cap; see module docstring)."""
    if n < 1:
        raise ValueError(f"n must be >= 1, got {n!r}")
    if generator_scope not in ("weight1", "mixed"):
        raise ValueError(f"unknown generator_scope: {generator_scope!r}")
    if generator_scope == "mixed" and n < 2:
        raise ValueError(
            f"generator_scope='mixed' requires n >= 2 (weight2_pair needs "
            f"two distinct qubits), got n={n}"
        )

    if generator_scope == "weight1":
        layer, theta_tensor, M, herald_ok, centers, p_real_np = _setup_weight1(n)
    else:
        i, j = weight2_pair
        layer, theta_tensor, M, herald_ok, centers, p_real_np = _setup_mixed(n, i, j)

    K_mat = torch.tensor(
        mmd_exact.gaussian_kernel_matrix_np(centers, SIGMA), dtype=torch.float32
    )
    p_real = torch.tensor(p_real_np, dtype=torch.float32)

    accumulator = []
    for draw in range(draw_start, draw_start + draw_count):
        draw_rng = rng_mod.get_rng(seed_base, generator_scope, init_scheme, n, draw)
        thetas = sample_thetas(draw_rng, n, init_scheme)
        with torch.no_grad():
            theta_tensor.copy_(torch.tensor(thetas, dtype=theta_tensor.dtype))
        if theta_tensor.grad is not None:
            theta_tensor.grad.zero_()

        out_flat = layer().flatten()
        q_vec = M @ out_flat
        if herald_ok is not None:
            success_prob = (herald_ok * out_flat).sum()
            q_vec = q_vec / success_prob

        # MMD^2(p,q) = p@K@p + q@K@q - 2*p@K@q; the p@K@p term is
        # theta-independent (constant offset), dropped -- does not affect
        # the gradient, matches mmd_exact.mmd2_grad's own quadratic-form
        # chain rule (unclamped, per that module's documented convention).
        loss = q_vec @ K_mat @ q_vec - 2.0 * (p_real @ K_mat @ q_vec)
        loss.backward()

        accumulator.extend(theta_tensor.grad.detach().numpy().tolist())

    return np.array(accumulator), n
