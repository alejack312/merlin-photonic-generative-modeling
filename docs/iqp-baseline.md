# Qubit-side IQP baseline

Updated 2026-09-10 against the implemented v4 contracts and the primary sources below. This replaces earlier statements that conflated efficient estimation, successful optimization, and hard sampling. The previous text remains in [Git history](https://github.com/alejack312/merlin-photonic-generative-modeling/blob/41c0d1b/docs/iqp-baseline.md).

## Circuit and conventions

For binary generator rows `g_j`, write `Z(g_j)` for the product of Z operators on the selected qubits. The v4 logical convention is

`U(theta) = H^n exp(i sum_j theta_j Z(g_j)) H^n`, acting on `|0^n>`.

All logical middle-layer gates commute. An optical decomposition may contain noncommuting elementary components; the logical IQP description does not require each physical component to commute. A library gate `MultiRZ(2 theta)` conventionally represents `exp(-i theta Z(g))`; its sign must be translated explicitly when comparing parameterizations.

## Classical expectation estimation and training

For a binary observable label `a`, the output parity expectation is

`mu_a = E_z cos(2 sum_j theta_j (a dot g_j mod 2) (-1)^(z dot g_j))`,

where `z` is uniform on binary strings. Evaluating this average by enumeration is exponential in n. Sampling bounded cosine terms instead gives an additive-error estimator of a selected expectation. That distinction is essential: a compact formula is not automatically an efficient exact algorithm.

[Recio-Armengol, Ahmed and Bowles, Proposition 1 and Section 4](https://arxiv.org/html/2503.02934v2) derive a classical estimator and an MMD training construction. Their cited den Nest reference is unambiguously [Simulating quantum computers with probabilistic methods, arXiv:0911.1624](https://arxiv.org/abs/0911.1624), rather than the Gottesman–Knill paper. Efficient estimation does not guarantee convergence to a good fit or efficient relative-error resolution of arbitrarily small gradients.

Here, [expectation.py](../src/merlin_iqp/classical/expectation.py) implements bounded exact enumeration of parity expectations/Jacobians. The released trainer is classical and NumPy-only, but it is not the thousand-qubit sampled implementation of the paper. See [MMD loss](mmd-loss.md) for the kernel-dependent representation and [the release results](v4-bounded-release.md) for actual fit quality.

## Sampling hardness is a separate, conditional claim

[Bremner, Montanaro and Shepherd](https://arxiv.org/abs/1504.07999) establish conditional approximate-sampling hardness for specified IQP families using average-case complexity conjectures. Their additive l1 threshold must not be silently treated as the same numerical TVD threshold: TVD is half l1 for normalized distributions. Such family-level results do not prove hardness of a particular trained instance, noisy optical construction, or small circuit.

The v3 `weight1` circuits factor into independent qubits. Its `mixed` circuits add only one fixed pair, leaving a constant-size correlated factor and independent qubits. Both are classically sampleable. A growing entangling structure is not sufficient by itself to establish hardness either. Classical sampling methods include direct product sampling and structure-dependent algorithms, not only a full state-vector simulator. This repository demonstrates no quantum sampling advantage.

## Trainability claims and bandwidth

A barren-plateau statement specifies the circuit/initialization ensemble, cost, derivative, and asymptotic scaling. Small-n curve fits and optimizer termination do not establish such a theorem. The historical sibling classifier is an empirical rule for its own labeled dataset, not a universal IQP law or a transferable n=6 threshold.

[Rudolph et al., Theorem 2](https://arxiv.org/html/2305.02881v2) explicitly treats a product ansatz with single-qubit Haar-random unitaries. Its loss-variance result is not an initialization-independent theorem for every ansatz. Its bandwidth symbol occurs without the square used in this repository's `exp(-H/(2 sigma^2))`; compare formulas before translating scaling. In our convention the low-body scaling is `sigma^2 = Theta(n)`, equivalently `sigma = Theta(sqrt(n))`. None of this directly proves a result for the legacy Euclidean-grid kernel.

The corrected v3 conclusion is that classical nulls reproduce the measured curves for the tested scopes; those runs did not isolate an additional photonic trainability effect. V4's poor-fit main results and deterministic duplicate seeds must be read as reported, without inferring either general trainability or general untrainability.
