import torch
import merlin as ML

from merlin_iqp.generator.natural_grid import make_natural_bin_centers
from merlin_iqp.generator.spatial_alignment import fock_state_sort_order, radius_sort_order

CENTERS = make_natural_bin_centers()
OUTPUT_KEYS = ML.QuantumLayer.simple(input_size=10, output_size=None).quantum_layer.output_keys


def _is_permutation(perm: torch.Tensor, n: int) -> bool:
    return torch.equal(torch.sort(perm).values, torch.arange(n))


def test_radius_sort_order_is_valid_permutation():
    perm = radius_sort_order(CENTERS)
    assert perm.dtype == torch.long
    assert _is_permutation(perm, CENTERS.shape[0])


def test_radius_sort_order_is_ascending_in_radius():
    perm = radius_sort_order(CENTERS)
    r = torch.norm(CENTERS - torch.tensor([0.5, 0.5]), dim=1)[perm]
    assert torch.all(r[1:] >= r[:-1])


def test_radius_sort_order_is_deterministic():
    assert torch.equal(radius_sort_order(CENTERS), radius_sort_order(CENTERS))


def test_fock_state_sort_order_is_valid_permutation():
    perm = fock_state_sort_order(OUTPUT_KEYS)
    assert perm.dtype == torch.long
    assert _is_permutation(perm, len(OUTPUT_KEYS))


def test_fock_state_sort_order_is_ascending_in_center_of_mass():
    perm = fock_state_sort_order(OUTPUT_KEYS)
    coms = []
    for i in perm.tolist():
        positions = [m for m, n in enumerate(OUTPUT_KEYS[i]) for _ in range(n)]
        coms.append(sum(positions) / len(positions))
    assert all(b >= a - 1e-12 for a, b in zip(coms, coms[1:]))


def test_fock_state_sort_order_is_deterministic():
    assert torch.equal(fock_state_sort_order(OUTPUT_KEYS), fock_state_sort_order(OUTPUT_KEYS))


def test_fock_state_sort_order_tertiary_tiebreak_is_exercised():
    # Pitfall guard: the (com, var) key alone is NOT unique across these 462
    # states -- photon number is fixed, so many states share both statistics.
    # Without the original-index tiebreak the order within such a group would
    # depend on sort implementation details rather than being pinned. This test
    # proves at least one real tie group exists AND that ties come out in
    # ascending original-index order.
    def stats(i):
        positions = [m for m, n in enumerate(OUTPUT_KEYS[i]) for _ in range(n)]
        com = sum(positions) / len(positions)
        var = sum((p - com) ** 2 for p in positions) / len(positions)
        # exact float values, not rounded: the sort key compares these floats
        # bit-for-bit, so rounding here would group pairs the sort does not
        # actually consider tied.
        return (com, var)

    groups = {}
    for i in range(len(OUTPUT_KEYS)):
        groups.setdefault(stats(i), []).append(i)
    tied = [g for g in groups.values() if len(g) > 1]
    assert tied, "expected at least one (com, var) tie group among the 462 states"

    order = fock_state_sort_order(OUTPUT_KEYS).tolist()
    rank = {idx: r for r, idx in enumerate(order)}
    for group in tied:
        ranks = [rank[i] for i in sorted(group)]
        assert ranks == sorted(ranks)
