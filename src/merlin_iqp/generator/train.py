"""Generator construction and the closed-form-MMD^2 training step for the
K=400 baseline (see ``naturally_ordered_generator.py`` for the K=462
successor), plus a scripted decreasing-trend check used in place of
eyeballing loss curves."""

import numpy as np
import torch
import merlin as ML
from scipy.stats import linregress

from merlin_iqp.generator.noise import LATENT_DIM, sample_latent
from merlin_iqp.generator.mmd import mmd2


def build_generator(input_size: int = LATENT_DIM, output_size: int = 400) -> ML.QuantumLayer:
    """Thin wrapper around ML.QuantumLayer.simple(...) so train.py and tests
    construct the generator identically. input_size defaults to LATENT_DIM
    (10, not 2) — see generator/noise.py's own docstring for why."""
    return ML.QuantumLayer.simple(input_size=input_size, output_size=output_size)


def train_step(quantum_layer, optimizer, p_real, kernel_matrix, batch_size) -> float:
    """One training step: fresh z-batch -> forward -> per-sample MMD^2 -> mean -> backward.

    Owner-confirmed batch-reduction strategy (DESIGN_DECISIONS.md, 2026-07-24):
    average per-sample mmd2(p_real, q_i, K) losses across the batch — never
    average q_batch into one vector before calling mmd2 (that is a different,
    rejected training objective, see 03-RESEARCH.md Open Question 1).
    """
    optimizer.zero_grad()
    z = sample_latent(batch_size)  # fresh every step, never cached
    q_batch = quantum_layer(z)  # (batch_size, 400), default analytic output (no shots=)
    losses = torch.stack([
        mmd2(p_real, q_batch[i], kernel_matrix) for i in range(batch_size)
    ])
    loss = losses.mean()
    loss.backward()
    optimizer.step()
    return loss.item()


def decreasing_trend_check(losses: list[float], tail_frac: float = 0.1) -> dict:
    """Scripted (not eyeballed) evidence that a loss curve shows a real
    decreasing trend. Two independent conditions, both required:
      1. Fitted slope over all epochs is negative (real trend, not noise).
      2. Mean loss over the last `tail_frac` of epochs is at least 10% lower
         than the mean over the first `tail_frac` — guards against a
         technically-negative-but-visually-flat slope.
    """
    n = len(losses)
    x = np.arange(n)
    y = np.array(losses)
    slope, intercept, r_value, p_value, std_err = linregress(x, y)
    k = max(1, int(n * tail_frac))
    first_mean = y[:k].mean()
    last_mean = y[-k:].mean()
    relative_drop = (first_mean - last_mean) / first_mean if first_mean > 0 else 0.0
    passed = bool(slope < 0 and relative_drop >= 0.10)
    return {
        "slope": float(slope),
        "p_value": float(p_value),
        "first_mean": float(first_mean),
        "last_mean": float(last_mean),
        "relative_drop": float(relative_drop),
        "passed": passed,
    }
