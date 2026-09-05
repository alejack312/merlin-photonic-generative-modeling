# Classical-core provenance

This directory is an adaptation of semantics inspected in sibling commit
`f6d6ebe87e4ee1de10893c6ea2f0ffa367493336` from `iqp_bp` and `iqp_mmd`. The
adapted concepts are the IQP parity phase/expectation, Gaussian Hamming
kernel spectrum, weighted parity moments, deterministic seed derivation,
parity initialization, and SGD/Adam update equations.

The destination intentionally does not copy the sibling import closure. In
particular, it does not import `iqp_bp`, JAX, PennyLane, Perceval, MerLin, or
the sibling model/checkpoint objects. Exact-small-n loss accepts explicit
probability vectors and weighted supports in addition to empirical samples;
this is a deliberate contract adaptation required by the v4 design. Source
Gaussian mixtures remain explicit through `sigmas` and `mixture_weights`.

No source license text or unresolved source imports are vendored here. The
binding design and audit are the authoritative records for the adaptation and
for the separate sign, bit-order, winding, and photonic compilation boundary.
