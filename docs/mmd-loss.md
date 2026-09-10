# MMD loss: kernels, estimators, and the repository pipelines

Updated 2026-09-10. The [previous explanation](https://github.com/alejack312/merlin-photonic-generative-modeling/blob/41c0d1b/docs/mmd-loss.md) is retained as history. The name MMD does not imply that two experiments use the same objective, representation, or estimator.

## Definition

For normalized probability vectors p and q on the same finite support and a positive-semidefinite kernel matrix K,

`MMD^2(p,q) = p^T K p + q^T K q - 2 p^T K q = (p-q)^T K (p-q)`.

This is exact for the supplied vectors up to numerical error. A target histogram is still estimated from finite data, and a latent-input model average may still be estimated by a minibatch. Exact evaluation of the finite quadratic form does not eliminate those uncertainties. Sample U-statistic and V-statistic estimators have different bias properties; neither should be silently substituted for a population-vector calculation. See [Gretton et al., A Kernel Two-Sample Test](https://www.jmlr.org/papers/v13/gretton12a.html).

## Which pipeline uses which objective?

| Pipeline | Model/output | Kernel and computation |
|---|---|---|
| v1 generator | Latent-input `QuantumLayer.simple`, 462 photonic outcomes mapped to a 2D grid | Gaussian on squared Euclidean distances between centers; classical simulator/autograd |
| v3 trainability study | Small logical IQP scopes, `2^n` indexed bins | Euclidean-grid Gaussian; parameter-shift simulator evaluation; corrected null interpretation |
| v4 spatial rings | NumPy IQP, `2^n` row-major centers | Spatial Gaussian with full finite Walsh representation |
| v4 Hamming rings/sibling comparisons | NumPy or matched sibling IQP on bitstrings | `K(x,y)=exp(-H(x,y)/(2 sigma^2))`; H is the number of differing bits, not its square |

V1 already trained through classical simulation. V4 adds circuit-free IQP mathematics for training; it does not replace v1. The two models share a data recipe, not an ansatz or output space. Kernel values and loss magnitudes across different geometries/bandwidths are not directly comparable scores of model quality.

## Hamming spectral identity

Let `N=2^n`, `W[a,x]=(-1)^(a dot x)`, and `mu_p=W p`. Set `r=exp(-1/(2 sigma^2))`. The normalized Walsh coefficients are

`lambda_a=((1+r)/2)^(n-|a|) ((1-r)/2)^|a|`,

so `K=W^T diag(lambda) W` and

`MMD^2 = sum_a lambda_a (mu_p[a]-mu_q[a])^2`.

The coefficients sum to one. Their expected parity weight is `n(1-r)/2`, which stays bounded when `sigma^2` scales with n. A finite Gaussian kernel still includes higher-order terms; approximate low-body dominance is not the same as explicitly truncating them.

In [kernel.py](../src/merlin_iqp/classical/kernel.py), `gaussian_spectral_weights` returns relative weights `tau^k`, with `tau=tanh(1/(4 sigma^2))`. The normalization factor is required: those relative weights alone are not the complete per-observable coefficients. `gaussian_hamming_spectrum` supplies the normalized coefficients used by the finite implementation. Krawtchouk aggregation groups terms by Hamming weight; it does not remove the need to track normalization.

## A spatial kernel also has a Walsh representation

Every finite `N by N` matrix has the representation `B=W K W^T/N^2`, giving `MMD^2=(mu_p-mu_q)^T B (mu_p-mu_q)`. In general B is dense and is not diagonal. A spatial embedding normally lacks the XOR-translation invariance that diagonalizes the Hamming kernel. Thus “no Walsh decomposition exists, even in principle” is false; what is missing in general is the same efficient diagonal-mixture estimator. The v4 spatial implementation retains the off-diagonal terms and remains bounded exact computation.

## Interpretation and evidence

Bandwidth controls which discrepancies are emphasized. A low MMD under one bandwidth does not establish good support, TVD, or high-order correlation matching. The [release summary](v4-bounded-release.md) reports those separately. There are no collected optical shots behind its nominal 20,000-outcome budget and no sampled confidence intervals to infer from exact model vectors. The data split, mapping, bandwidth, mixture weights, normalization, and estimator must all match before comparing substrates.

Simultaneously permuting p, q, and K leaves MMD unchanged. Reassigning optical outcomes to fixed spatial centers changes the model-to-geometry mapping and can change the objective; this is distinct from merely renaming indices. See [raster order](raster-order.md).
