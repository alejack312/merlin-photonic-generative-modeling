"""Focused contracts for the registered sibling/substrate comparator."""

from __future__ import annotations

import numpy as np
import pytest

from scripts.v4_tcdp.compare_sibling_backends import (
    PROBABILITY_TOLERANCE,
    _acceptance_for_arm,
    _target_histogram,
    _vector_from_mapping,
)


def test_source_sample_histogram_uses_explicit_msb_first_codec() -> None:
    samples = np.array([[0, 0], [0, 1], [1, 0], [1, 0]], dtype=np.uint8)
    np.testing.assert_array_equal(_target_histogram(samples, 2), [0.25, 0.25, 0.5, 0.0])


def test_compiled_mapping_requires_complete_msb_first_state_space() -> None:
    with pytest.raises(ValueError, match="complete explicit MSB-first"):
        _vector_from_mapping({"00": 1.0}, 2)


def test_acceptance_roundoff_is_recorded_as_valid_probability() -> None:
    assert _acceptance_for_arm(1.0 + 0.5 * PROBABILITY_TOLERANCE) == 1.0
    with pytest.raises(ValueError, match="exceeds one"):
        _acceptance_for_arm(1.0 + 2.0 * PROBABILITY_TOLERANCE)
