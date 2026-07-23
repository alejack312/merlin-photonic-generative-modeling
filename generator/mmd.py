import numpy as np
import torch

#  a bandwidth sweep, not one fixed value. Not locked; Phase 4 will evaluate these against actual ring recovery.
SIGMA_GRID = [0.02, 0.05, 0.1, 0.2, 0.4] 

#  exp(-cdist(centers, centers)² / (2σ²)). Precomputed once per σ, never recomputed inside the loss itself.
def gaussian_kernel_matrix(centers, sigma) -> torch.Tensor: 
    return torch.exp(-torch.cdist(centers, centers)**2 / (2*sigma**2))

# mmd2(p, q, kernel_matrix) -> scalar: the closed-form p@K@p + q@K@q - 2·p@K@q, clamped to ≥0 as a defensive guard against float32 rounding noise. p is the fixed p_real (no gradient needed), q is the differentiable circuit output.
def mmd2(p, q, kernel_matrix) -> torch.Tensor:
    mmd2_value = p@kernel_matrix@p + q@kernel_matrix@q - 2*p@kernel_matrix@q
    return torch.clamp(mmd2_value, min=0)
