import pytest
import torch
import merlin as ML

from generator.mmd import gaussian_kernel_matrix, mmd2
from generator.data import load_circles_data, compute_p_real
from generator.noise import sample_latent
from generator.naturally_ordered_generator import (
    NaturallyOrderedGenerator,
    build_naturally_ordered_generator,
    natural_sorted_centers,
)

K = 462


def test_forward_shape_and_probability_validity():
    gen = build_naturally_ordered_generator()
    q = gen(sample_latent(4))
    assert q.shape == (4, K)
    assert torch.all(q >= 0)
    # abs=1e-5: float32 accumulation over 462 terms, same tolerance the existing
    # MMD self-comparison test uses for this-size sums.
    assert q.sum(dim=1).tolist() == pytest.approx([1.0] * 4, abs=1e-5)


def test_perm_buffer_is_valid_permutation_and_not_a_parameter():
    gen = build_naturally_ordered_generator()
    assert torch.equal(torch.sort(gen.perm).values, torch.arange(K))
    assert "perm" not in dict(gen.named_parameters())
    assert "perm" in dict(gen.named_buffers())


def test_forward_matches_manual_raw_permutation():
    # Pitfall guard: shape + sum-to-one would pass even if perm were the identity
    # or applied to the wrong axis. This cross-checks the actual values against an
    # independently constructed raw layer carrying the same weights.
    gen = build_naturally_ordered_generator()
    raw = ML.QuantumLayer.simple(input_size=10, output_size=None)
    raw.load_state_dict(gen.base.state_dict())

    z = sample_latent(3)
    gen.eval()
    raw.eval()
    with torch.no_grad():
        assert torch.allclose(gen(z), raw(z)[:, gen.perm])


def test_state_dict_roundtrip():
    gen = build_naturally_ordered_generator()
    z = sample_latent(2)
    gen.eval()
    with torch.no_grad():
        before = gen(z)

    restored = NaturallyOrderedGenerator()
    restored.load_state_dict(gen.state_dict())
    restored.eval()
    with torch.no_grad():
        after = restored(z)
    assert torch.allclose(before, after)
    assert torch.equal(gen.perm, restored.perm)


def test_gradient_reaches_quantum_layer_through_permutation():
    # Mirrors test_mmd.py's gradient test: the permutation must not sever the
    # graph between the loss and the circuit's trainable parameters.
    centers = natural_sorted_centers()
    x_train, _ = load_circles_data()
    p_real = compute_p_real(x_train, centers)
    kernel_matrix = gaussian_kernel_matrix(centers, 0.1)

    gen = build_naturally_ordered_generator()
    q = gen(sample_latent(1))[0]
    mmd2(p_real, q, kernel_matrix).backward()

    params = list(gen.base.parameters())
    assert params
    assert any(p.grad is not None and torch.any(p.grad != 0) for p in params)


def test_input_size_mismatch_raises_clear_error():
    # Guards against the silent-mismatch footgun: natural_sorted_centers()'s
    # 462-cell grid and sample_latent()'s dim are both hardcoded to LATENT_DIM
    # independently of this constructor's input_size arg, so a mismatch must
    # fail loudly here rather than producing a wrong-width tensor downstream.
    with pytest.raises(ValueError, match="input_size"):
        NaturallyOrderedGenerator(input_size=5)


def test_batch_rows_are_independent():
    # Guards against a broadcasting/indexing bug in raw[:, self.perm] silently
    # mixing rows: each row must equal the wrapper run on that row alone.
    gen = build_naturally_ordered_generator()
    gen.eval()
    z = sample_latent(3)
    with torch.no_grad():
        batched = gen(z)
        for i in range(3):
            assert torch.allclose(batched[i], gen(z[i : i + 1])[0])
