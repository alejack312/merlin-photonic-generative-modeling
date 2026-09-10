# Phase 26 classical-core implementation notes

Status: implementation evidence for TRAIN-01..04 and MOD-01..04 is recorded
by `tests/v4_tcdp/test_classical_core.py` and the package-level provenance
record in `src/merlin_iqp/classical/PROVENANCE.md`.

The classical boundary is NumPy-only. Exact targets are never converted to
integer samples: empirical samples, sparse weighted support, and full exact
probability vectors have separate representations and share a target-moment
function. Hamming Gaussian MMD has both direct and Walsh forms; spatial
Gaussian MMD retains its dense Walsh matrix. IQP moments and their Jacobian are
enumerated only in the explicit small-n exact capability.

The generator adapter emits all singles first and lexicographically sorted
pairs for general graphs. `chain_1d(n, k)` is the declared nearest-neighbour
special case. Adapter values are copied without changing bit order, signs, or
angle winding; photonic sign/compilation work belongs to a later deployment
boundary.

Checkpoint files use compressed NPZ arrays plus JSON metadata and include
generator rows, hashes, optimizer state, RNG state, versions, source commit,
loss history, and selection rule. Resume rejects mismatched spec/dataset/kernel
hashes. The trainer is exact and deterministic for the declared target and
kernel; stochastic estimators and source-specific export remain later work.
