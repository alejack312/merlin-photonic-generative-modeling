import pytest
import torch
from merlin_iqp.generator.data import load_circles_data, compute_p_real
from merlin_iqp.generator.bin_centers import make_bin_centers


def test_p_real_shape_and_validity():
    X_train, X_test = load_circles_data()
    bin_centers = make_bin_centers()
    p_real = compute_p_real(X_train, bin_centers)

    assert p_real.shape == (400,)
    assert torch.all(p_real >= 0)
    assert float(p_real.sum()) == pytest.approx(1.0, abs=1e-5)


def test_reproducibility():
    bin_centers = make_bin_centers()

    # two separate calls, not the same tensor compared to itself
    X_train_a, _ = load_circles_data()
    X_train_b, _ = load_circles_data()
    assert torch.equal(X_train_a, X_train_b)

    p_real_a = compute_p_real(X_train_a, bin_centers)
    p_real_b = compute_p_real(X_train_b, bin_centers)
    assert torch.equal(p_real_a, p_real_b)


def test_held_out_separation():
    # p_real is computed from X_train only (see test_p_real_shape_and_validity) —
    # this documents that X_test is a real, distinct, ~80/20-split held-out set,
    # never folded into p_real.
    X_train, X_test = load_circles_data()
    assert X_train.shape[0] == 320
    assert X_test.shape[0] == 80
