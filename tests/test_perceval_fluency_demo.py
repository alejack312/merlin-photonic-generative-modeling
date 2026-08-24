import numpy as np
import pytest

from scripts.perceval_fluency_demo import (
    run_analyzer,
    check_single_photon,
    check_hom_dip,
    run_mzi_analyzer,
    check_mzi,
)


def test_single_photon_50_50_split():
    """|1,0> input on a 50/50 beamsplitter splits exactly 50/50 between the
    two output ports (no interference possible with a single photon)."""
    _, single_photon_dist, _ = run_analyzer()
    assert check_single_photon(single_photon_dist)


def test_hong_ou_mandel_dip():
    """|1,1> input on a 50/50 beamsplitter always bunches: P(1,1)=0,
    P(0,2)=P(2,0)=0.5."""
    _, _, hom_dist = run_analyzer()
    assert check_hom_dip(hom_dist)


def test_distributions_sum_to_one():
    """Sanity check: both output distributions are proper probability
    distributions."""
    _, single_photon_dist, hom_dist = run_analyzer()
    assert sum(single_photon_dist.values()) == pytest.approx(1.0, abs=1e-9)
    assert sum(hom_dist.values()) == pytest.approx(1.0, abs=1e-9)


@pytest.mark.parametrize("theta", [0, np.pi / 2, np.pi])
def test_mzi_interference(theta):
    """BS.H() -> PS(theta) -> BS.H() on a single photon matches the
    closed-form interference prediction P(1,0)=cos^2(theta/2),
    P(0,1)=sin^2(theta/2) across a sweep of theta values (fully
    constructive, 50/50, fully flipped)."""
    _, mzi_dist = run_mzi_analyzer(theta)
    assert check_mzi(mzi_dist, theta)
