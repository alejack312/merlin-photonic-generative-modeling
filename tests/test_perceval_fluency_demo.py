import sys
import os

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from perceval_fluency_demo import run_analyzer, check_single_photon, check_hom_dip


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
