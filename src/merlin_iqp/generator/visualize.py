"""Turning the generator's raw probability vector into plottable point
samples and ring/gap occupancy metrics."""

import torch


def sample_points(q: torch.Tensor, centers: torch.Tensor, n: int = 400) -> torch.Tensor:
    """Draw n (x,y) points from the categorical distribution q over centers.

    q: (K,) probability vector (need not sum to exactly 1.0 -- torch.multinomial
    renormalizes internally). centers: (K,2). Returns (n,2).

    Uses torch.multinomial, NOT quantum_layer(z, shots=n) -- the shots= forward
    path returns a re-normalized frequency vector over the same K bins (quantized
    to multiples of 1/shots), not a list of individual (x,y) draws, so it is not
    the right shape for a scatter plot (04-RESEARCH.md, verified empirically).
    """
    idx = torch.multinomial(q, num_samples=n, replacement=True)
    return centers[idx]


def ring_band_metrics(
    mass: torch.Tensor,
    centers: torch.Tensor,
    center: tuple[float, float] = (0.5, 0.5),
    radii: tuple[float, float] = (0.4, 0.5),
    tol: float = 0.04,
) -> dict:
    """Fraction of probability mass (or point counts) within `tol` of either ring
    radius ("ring_mass"), vs. fraction in the empty gap strictly between the two
    tolerance bands ("gap_mass"). mass need not sum to 1 -- renormalized here.

    tol=0.04 is empirically the largest tolerance where ring_mass(p_real)==1.0 and
    gap_mass(p_real)==0.0 against this project's real circles data (04-RESEARCH.md
    Pitfall 6) -- tol=0.05 leaves zero gap bins and can never detect gap-hedging.
    A lightweight supporting metric, not a replacement for visual judgment
    (04-CONTEXT.md "Success judgment method").
    """
    c = torch.tensor(center, dtype=centers.dtype)
    r = torch.norm(centers - c, dim=1)
    ring_mask = (torch.abs(r - radii[0]) <= tol) | (torch.abs(r - radii[1]) <= tol)
    lo_gap, hi_gap = radii[0] + tol, radii[1] - tol
    gap_mask = (r > lo_gap) & (r < hi_gap) if hi_gap > lo_gap else torch.zeros_like(r, dtype=torch.bool)
    m = mass / mass.sum()
    return {
        "ring_mass": m[ring_mask].sum().item(),
        "gap_mass": m[gap_mask].sum().item(),
    }
