"""Classically-easy baseline distributions and the BMS anticoncentration
parameter (Phase 18, HARD-05).

Two comparison points against which this project's true (loss-affected)
output distributions are measured, per 18-CONTEXT.md's locked decision to
track both separately rather than collapse them into a single crossover
threshold:

- `uniform_baseline`: the maximally-anticoncentrated reference -- every
  n-bit output state equally likely.
- `product_of_marginals_baseline`: the mean-field / independence baseline --
  the product distribution obtained from a reference distribution's own
  per-qubit marginals. Per 18-CONTEXT.md, callers must compute this ONCE
  from the lossless (eta=1) target distribution and reuse it across the
  whole eta grid -- this module does not enforce that call pattern, it only
  implements the pure computation.

`anticoncentration_alpha` implements Bremner-Montanaro-Shepherd's Theorem 4
normalization (arXiv:1610.01808): Sigma p_x^2 <= alpha * 2^-n, computed
directly/exactly from a fully-materialized distribution (never
sampled/estimated).

Pure, standalone, deterministic functions -- no Perceval dependency, no
circuit-building. Operates only on already-materialized distribution dicts
keyed by '0'/'1' bitstrings (this project's `fock_to_bitstring` convention,
not `expected_joint_distribution`'s 'H'/'V' alphabet).
"""

import itertools
import math


def _all_bitstrings(n):
    """All 2**n n-bit '0'/'1' bitstrings, matching
    iqp_photonic_encoding.expected_joint_distribution's enumeration pattern
    adapted to the '0'/'1' alphabet."""
    return ["".join(bits) for bits in itertools.product("01", repeat=n)]


def uniform_baseline(n):
    """Uniform-over-output-states baseline: {bitstring: 2**-n for every
    n-bit '0'/'1' bitstring}. HARD-05's maximally-anticoncentrated
    comparison point."""
    p = 2.0**-n
    return {bits: p for bits in _all_bitstrings(n)}


def product_of_marginals_baseline(reference_dist, n):
    """Product-of-marginals (mean-field) baseline distribution.

    Each qubit k's marginal P(bit_k='1') is computed by summing
    reference_dist's probability mass over every key present in
    reference_dist with bits[k]=='1'. reference_dist's keys may not cover
    all 2**n bitstrings (e.g. output of a lossy/residual-bearing sweep) --
    marginals are summed only over present keys.

    Contract: reference_dist is NOT assumed to be normalized to 1.0
    internally -- a caller may pass in a loss-affected distribution whose
    mass sums to less than 1 after residual/herald-failure bucketing. The
    caller is responsible for passing an appropriately-normalized
    reference; this function does not renormalize.

    Returns the full product distribution over all 2**n bitstrings:
    {bits: prod(marginal[k] if bits[k]=='1' else (1-marginal[k])
               for k in range(n))
     for bits in all bitstrings}.
    """
    marginals = [0.0] * n
    for bits, p in reference_dist.items():
        for k in range(n):
            if bits[k] == "1":
                marginals[k] += p

    product_dist = {}
    for bits in _all_bitstrings(n):
        prob = 1.0
        for k in range(n):
            prob *= marginals[k] if bits[k] == "1" else (1.0 - marginals[k])
        product_dist[bits] = prob
    return product_dist


def anticoncentration_alpha(dist, n):
    """Bremner-Montanaro-Shepherd's Theorem 4 anticoncentration parameter
    (arXiv:1610.01808): alpha(dist, n) = 2**n * sum(p_x**2 for p_x in
    dist.values()), matching their normalization Sigma p_x^2 <= alpha *
    2**-n. Computed directly/exactly from the full materialized
    distribution, never sampled/estimated.

    Known closed-form extremes: alpha=1.0 for the uniform distribution
    (maximally anticoncentrated); alpha=2**n for a delta/point-mass
    distribution (maximally concentrated).

    `dist` is RENORMALIZED to sum to 1.0 before the computation. This is
    load-bearing, not defensive tidying: alpha is a shape statistic, and
    the extremes above (the alpha>=1 floor in particular) hold only for a
    normalized distribution. Passing a sub-normalized distribution -- e.g.
    a lossy distribution whose mass has leaked to undetected/out-of-subspace
    outcomes -- makes alpha scale with the SQUARE of the surviving mass and
    produces values below 1.0, which are not interpretable as BMS's
    parameter at all (their alpha has a hard floor of 1.0).

    Correction (2026-08-20): Phase 18's loss sweep originally called this
    on the raw, un-renormalized lossy distribution, so the reported
    alpha(eta) decayed as exactly eta**(2n) -- a pure survival-probability
    artifact that was misread as "photon loss makes these circuits more
    anticoncentrated." 33 of 56 shipped rows reported alpha < 1.0, below
    the theoretical floor. Conditioned on detection (i.e. renormalized, as
    here), this circuit family's anticoncentration is EXACTLY INVARIANT
    under uniform photon loss, because uniform per-mode loss preserves the
    surviving distribution's shape exactly. See
    docs/hardness-under-loss-study.md's HARD-05 section.
    """
    total = math.fsum(dist.values())
    if total <= 0.0:
        raise ValueError(
            f"anticoncentration_alpha requires a distribution with positive "
            f"total mass; got sum(dist.values())={total!r}"
        )
    return (2.0**n) * math.fsum((p / total) ** 2 for p in dist.values())
