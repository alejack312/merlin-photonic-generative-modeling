"""Latent-noise sampling for the generator's input: a fixed-dimension Normal
distribution consumed directly by ``QuantumLayer.simple``."""

import math
import torch
import merlin as ML

# Module level constants
LATENT_DIM = 10

def sample_latent(
    batch_size: int,
) -> torch.Tensor:
    """
    dim=10, not 2: input_size sets QuantumLayer.simple's natural output width
    directly. input_size=2 only has natural width 3, so output_size=400 would be
    397/400 zero-padded and permanently degenerate; input_size=10 is the smallest
    value whose natural width (462) exceeds 400. std=2*pi (not [0,1]) matches
    MerLin's own PhotonicGenerator/NormalLatent convention, not quickstart.py's
    classifier-specific [0,1] normalization. Full reasoning + verification:
    .planning/phases/02-generator-data-loss-infrastructure/02-CONTEXT.md.

    Returns a fresh (batch_size, LATENT_DIM) tensor on every call — no caching.
    """
    return ML.NormalLatent(dim=LATENT_DIM, mean=0.0, std=2*math.pi).sample(batch_size)
