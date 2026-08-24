"""Closed-form Gaussian-kernel MMD^2 loss used to train the photonic
generator against ``p_real`` with no discriminator and no sampling step:
each forward pass already produces an exact, differentiable probability
vector, so gradients flow straight from MMD^2 back into the circuit's
parameters."""

import torch

#  a bandwidth sweep, not one fixed value. Not locked; Phase 4 will evaluate these against actual ring recovery.
SIGMA_GRID = [0.02, 0.05, 0.1, 0.2, 0.4]


def gaussian_kernel_matrix(centers, sigma) -> torch.Tensor:
    """Pairwise Gaussian kernel matrix exp(-cdist(centers, centers)^2 / (2*sigma^2))
    over the fixed set of K bin centers. Precomputed once per sigma, never
    recomputed inside the loss itself."""
    return torch.exp(-torch.cdist(centers, centers)**2 / (2*sigma**2))


def mmd2(p, q, kernel_matrix) -> torch.Tensor:
    """Closed-form MMD^2(p, q) = p@K@p + q@K@q - 2*p@K@q, clamped to >= 0 as
    a defensive guard against float32 rounding noise. p is the fixed p_real
    (no gradient needed); q is the differentiable circuit output."""
    mmd2_value = p@kernel_matrix@p + q@kernel_matrix@q - 2*p@kernel_matrix@q
    return torch.clamp(mmd2_value, min=0)
