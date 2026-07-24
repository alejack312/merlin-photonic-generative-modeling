import pytest
import torch

from generator.bin_centers import make_bin_centers
from generator.data import load_circles_data, compute_p_real
from generator.visualize import sample_points, ring_band_metrics


def test_ring_band_metrics_recovers_real_geometry():
    centers = make_bin_centers()
    x_train, _ = load_circles_data()
    p_real = compute_p_real(x_train, centers)

    metrics = ring_band_metrics(p_real, centers)

    assert metrics["ring_mass"] == pytest.approx(1.0, abs=1e-6)
    assert metrics["gap_mass"] == pytest.approx(0.0, abs=1e-6)


def test_ring_band_metrics_detects_gap_hedging():
    centers = make_bin_centers()
    # (0.1526, 0.2158) lies at radius ~0.4488 from (0.5,0.5) -- strictly inside
    # the empty annular gap between the two ring tolerance bands (0.44, 0.46),
    # not the overall plot center (0.5,0.5) itself (r=0, outside gap_mask).
    gap_point = torch.tensor([0.1526, 0.2158])
    idx = torch.argmin(torch.norm(centers - gap_point, dim=1))

    mass = torch.zeros(centers.shape[0])
    mass[idx] = 1.0

    metrics = ring_band_metrics(mass, centers)

    assert metrics["gap_mass"] == pytest.approx(1.0, abs=1e-6)
    assert metrics["ring_mass"] == pytest.approx(0.0, abs=1e-6)


def test_sample_points_shape_and_membership():
    centers = make_bin_centers()
    q = torch.ones(centers.shape[0])
    q = q / q.sum()

    points = sample_points(q, centers, n=400)

    assert points.shape == (400, 2)
    for p in points:
        assert torch.any(torch.all(centers == p, dim=1))


def test_sample_points_concentrates_on_high_probability_bin():
    centers = make_bin_centers()
    q = torch.zeros(centers.shape[0])
    q[100] = 1.0

    points = sample_points(q, centers, n=400)

    assert torch.all(points == centers[100])
