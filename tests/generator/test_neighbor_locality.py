import math
import torch

from merlin_iqp.generator.naturally_ordered_generator import build_naturally_ordered_generator
from merlin_iqp.generator.noise import sample_latent
from merlin_iqp.generator.neighbor_locality import (
    compute_jacobian,
    adjacent_and_random_cosines,
    neighbor_locality_check,
)

K = 462
P = 220


def test_compute_jacobian_shape_and_gradient_connectivity():
    gen = build_naturally_ordered_generator()
    gen.eval()
    z = sample_latent(1)
    J = compute_jacobian(gen, z)
    assert J.shape == (K, P)
    assert torch.any(J != 0)


def test_adjacent_and_random_cosines_shapes():
    torch.manual_seed(0)
    J = torch.randn(10, 5)
    adj_cos, rand_cos = adjacent_and_random_cosines(J, seed=1)
    assert adj_cos.shape == (9,)
    assert rand_cos.shape == (9,)


def test_neighbor_locality_check_passes_when_adjacent_rows_correlated():
    # Adjacent rows (small phase shift) are near-identical; far rows (large
    # phase shift) are close to uncorrelated -- constructs a Jacobian with
    # genuine neighbor-locality structure to prove the check discriminates it.
    J = torch.stack(
        [torch.sin(torch.linspace(0, 8 * math.pi, 20) + i * 0.05) for i in range(50)]
    )
    adj_cos, rand_cos = adjacent_and_random_cosines(J, seed=0)
    result = neighbor_locality_check(adj_cos, rand_cos)
    assert result["passed"] is True
    assert result["mean_diff"] > 0.10


def test_neighbor_locality_check_fails_on_iid_random_rows():
    torch.manual_seed(0)
    J = torch.randn(50, 20)
    adj_cos, rand_cos = adjacent_and_random_cosines(J, seed=0)
    result = neighbor_locality_check(adj_cos, rand_cos)
    assert result["passed"] is False
