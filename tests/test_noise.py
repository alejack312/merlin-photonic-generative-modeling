import pytest
import torch
import merlin as ML

from generator.noise import sample_latent

def test_sample_latent():
    # Shape/dtype test: sample_latent(32).shape == (32, 10), dtype is floating.
    assert sample_latent(32).shape == (32, 10)
    assert sample_latent(32).dtype == torch.float32
    
# Resample test: two calls to sample_latent(32) are NOT torch.equal — proves it isn't cached.
def test_resample_latent():
    assert not torch.equal(sample_latent(32), sample_latent(32))
    
# out is a probability vector over the same 400 bins as generator/bin_centers.py's
# make_bin_centers() grid — each bin is a possible location a generated sample lands
# in, so "which of the 400 bins" is a probability distribution over 400 mutually
# exclusive outcomes, and by definition those probabilities must sum to 1. GEN-04's
# p_real will express the real training data the same way (a histogram over the same
# 400 bins), so GEN-05's MMD² loss can compare the two directly — that comparison
# only makes sense if both sides are valid probability vectors over the same bins.
# Full reasoning: DESIGN_DECISIONS.md ("Generator output representation").
def test_forward_pass():
    layer = ML.QuantumLayer.simple(input_size=10, output_size=400)
    out = layer(sample_latent(16))
    assert out.shape == (16, 400)
    assert out.dtype == torch.float32
    # torch.allclose, not pytest.approx: out still has requires_grad=True (straight
    # out of QuantumLayer), and pytest.approx's internal handling breaks on that —
    # see ~/.claude/learnings/2026-07-19-pytest-approx-misuse-grad-tensor.md
    assert torch.allclose(out.sum(dim=1), torch.ones(16), atol=1e-5)

# The pitfall-guard test (the one that actually matters): assert broad nonzero 
# support on that same output, e.g. (out > 0).sum(dim=1).float().mean() > 50. 
# A shape+sums-to-1 test alone would still pass on the broken input_size=2 
# config, so this specific assertion is what proves you avoided the degeneracy.
def test_pitfall_guard():
    layer = ML.QuantumLayer.simple(input_size=10, output_size=400)
    out = layer(sample_latent(16))
    assert (out > 0).sum(dim=1).float().mean() > 50