import sys
import os

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from weight2_measurement_crossvalidation import compare, TOLERANCE


@pytest.mark.parametrize(
    "n, i, j, thetas, label",
    [
        (2, 0, 1, [0.0, 0.0], "locked TVD validation point"),
        (3, 1, 2, [0.6, 0.0, 0.0], "robustness / bystander-qubit point"),
    ],
)
def test_direct_add_herald_path_matches_herald_free_path(n, i, j, thetas, label):
    """Phase 12 follow-up (2026-08-07): the direct, add_herald()-registered
    production path (build_weight2_processor + explicit {P:V}-annotated
    herald input) agrees with the existing herald-free measurement path
    (photonic_weight2_iqp_distribution) to floating-point precision, at both
    Phase 12's locked validation point and its robustness/bystander-qubit
    point. Confirms the corrected understanding of the add_herald()+PBS
    crash (only triggers on auto-fill omission, not on explicit herald
    input) without replacing the still-correct herald-free path."""
    max_dist_diff, residual_diff, herald_diff = compare(n, i, j, thetas, label)
    assert max_dist_diff <= TOLERANCE
    assert residual_diff <= TOLERANCE
    assert herald_diff <= TOLERANCE
