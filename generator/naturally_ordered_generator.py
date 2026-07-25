import torch
import torch.nn as nn
import merlin as ML

from generator.natural_grid import make_natural_bin_centers
from generator.noise import LATENT_DIM
from generator.spatial_alignment import fock_state_sort_order, radius_sort_order


class NaturallyOrderedGenerator(nn.Module):
    """QuantumLayer.simple with output_size=None (raw 462-wide probability
    vector, no ModGrouping fold), reordered so column r holds the r-th "smoothest"
    Fock state — meant to be paired index-for-index with bin centers sorted by
    ascending radius (see natural_sorted_centers).

    Two independent fixes at once: no arbitrary modulo fold (462 == the circuit's
    natural width), and no arbitrary index<->bin labeling.

    Note: state_dict keys here ("perm", "base.quantum_layer.*") differ from
    build_generator()'s bare keys, so existing Phase 4 checkpoints are not
    loadable into this wrapper. Intentional — every Phase 4 variant trains fresh.
    """

    def __init__(self, input_size: int = LATENT_DIM):
        super().__init__()
        self.base = ML.QuantumLayer.simple(input_size=input_size, output_size=None)
        perm = fock_state_sort_order(self.base.quantum_layer.output_keys)
        # buffer, not parameter: moves with .to(), persists in state_dict, no grad
        self.register_buffer("perm", perm)

    def forward(self, z: torch.Tensor) -> torch.Tensor:
        return self.base(z)[:, self.perm]


def build_naturally_ordered_generator(input_size: int = LATENT_DIM) -> NaturallyOrderedGenerator:
    """Factory mirroring generator/train.py's build_generator() convention."""
    return NaturallyOrderedGenerator(input_size=input_size)


def natural_sorted_centers(
    rows: int = 21,
    cols: int = 22,
    lo: float = -0.1,
    hi: float = 1.1,
) -> torch.Tensor:
    """(rows*cols, 2) bin centers sorted by ascending radius from (0.5, 0.5),
    index-for-index paired with NaturallyOrderedGenerator's output columns."""
    centers = make_natural_bin_centers(rows=rows, cols=cols, lo=lo, hi=hi)
    return centers[radius_sort_order(centers)]
