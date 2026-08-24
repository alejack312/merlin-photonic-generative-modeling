"""Sort keys used to build a *designed* correspondence between the circuit's raw
output indices and the (x,y) bin centers.

Background: ML.QuantumLayer.simple's output index i is a photon-occupation Fock
state (a tuple like (1,1,1,1,1,1,0,0,0,0,0)) enumerated by combinatorics. It has
no designed relationship whatsoever to the raster order of a 2D grid of bin
centers. Pairing them index-for-index therefore imposes an arbitrary labeling:
whatever smoothness the circuit has over its own output space gets scattered
across the plane. These two functions replace that arbitrary pairing with one
that at least *tries* to line the two orderings up.
"""

import torch


def radius_sort_order(
    centers: torch.Tensor,
    center: tuple[float, float] = (0.5, 0.5),
) -> torch.Tensor:
    """Permutation sorting (K,2) centers by (radius, angle, original index).

    For a two-concentric-rings target, sorting bins by radius turns the target
    into two contiguous "on" bands in 1D rank order separated by contiguous
    "off" gaps — a much simpler shape than an arbitrary 2D pattern.

    The key is a tuple purely for determinism: radius alone leaves ties (grid
    reflection symmetry), angle resolves essentially all of them, and the
    original index makes the result fully deterministic regardless.
    """
    c = torch.tensor(center, dtype=centers.dtype)
    delta = centers - c
    radius = torch.norm(delta, dim=1)
    angle = torch.atan2(delta[:, 1], delta[:, 0])
    idx = torch.arange(centers.shape[0])
    keys = sorted(
        range(centers.shape[0]),
        key=lambda i: (radius[i].item(), angle[i].item(), int(idx[i])),
    )
    return torch.tensor(keys, dtype=torch.long)


def fock_state_sort_order(output_keys) -> torch.Tensor:
    """Permutation sorting Fock-state tuples by (center of mass of occupied mode
    indices, variance of those positions, original index).

    HEURISTIC, not a proven smoothness guarantee. The rationale is physical:
    beamsplitter and phase parameters redistribute amplitude between *adjacent*
    modes, so states whose photons sit in nearby modes plausibly vary together
    under a small parameter change. Whether that actually yields spatial
    smoothness once paired with radius rank is exactly what the experiment
    tests — treat it as a first-pass empirical choice.

    Center of mass alone ties heavily (photon number is fixed across all states,
    so only ~31 distinct values across 462 states); the positional variance
    breaks most of those groups, and the original index makes it deterministic.
    """
    def key(i):
        """Sort key for output index ``i``: (center of mass, positional
        variance, original index) of its Fock state's occupied modes."""
        state = output_keys[i]
        positions = [m for m, n in enumerate(state) for _ in range(n)]
        n = len(positions)
        if n == 0:
            return (0.0, 0.0, i)
        com = sum(positions) / n
        var = sum((p - com) ** 2 for p in positions) / n
        return (com, var, i)

    order = sorted(range(len(output_keys)), key=key)
    return torch.tensor(order, dtype=torch.long)
