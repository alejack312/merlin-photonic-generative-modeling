# Technical findings: corrected v3 record and bounded v4 release

Updated 2026-09-10. This synthesis reports the conclusions supported by the repository's committed evidence. The [pre-reconciliation version](https://github.com/alejack312/merlin-photonic-generative-modeling/blob/41c0d1b/docs/technical-findings.md) preserves earlier tables and owner discussion. Historical “consistent with” verdicts there are not current confirmations of literature predictions.

## Correction of the v3 headline claims

The v3 trainability and hardness-under-loss headlines did not establish the claimed circuit effects. The [trainability study](trainability-study.md) and [loss study](hardness-under-loss-study.md) preserve their dated corrections, methods, measured tables, and regression evidence.

- **Trainability:** a classical null reproduces the tested gradient-variance curves. The Euclidean kernel is numerically close to the identity at the smaller tested sizes, but its off-diagonal entries are non-negligible at larger tested sizes. The null result is scoped to the tested circuits; it is not an ansatz-independent theorem or an asymptotic barren-plateau demonstration. A deterministic initialization with one vector per size is not a matched ensemble-variance experiment.
- **Loss:** if the accepted subdistribution is `m=s q` with normalized q, the historical half-l1 diagnostic against q equals `(1-s)/2`. That is not TVD between two normalized distributions. Adding failure outcomes to make a common normalized sample space gives TVD `1-s` against an ideal always-successful reference; comparing the conditional q vectors instead gives zero under the stated uniform-loss assumptions. These are different questions.
- **Hardness:** the v3 weight-1 circuits are products, and the mixed scope contains only one fixed correlated pair. Both admit classical sampling. Equality of a lossy conditional distribution with its lossless counterpart cannot establish hardness that the tested family never had.

For fixed n-photon input, passive optics, uniform per-photon survival eta, and acceptance requiring all n photons, the no-loss contribution scales by `eta^n`. This does not extend automatically to multiphoton sources, nonuniform loss, or accepted events that permit missing photons. For the separately modeled heralded-CZ architecture with two real ancilla photons per gate, `eta^(n+2k)(2/27)^k` is a resource formula under its stated ideal composability/success assumptions. It is not the success formula for the vacuum-ancilla CP catalog.

## Classical training and quantum deployment

The [IQP baseline](iqp-baseline.md) distinguishes classical expectation estimation, bounded exact enumeration, optimization success, and conditional sampling-hardness statements. The v1 model already trained through classical simulation. V4 adds a separate NumPy IQP training pipeline, including a dense spatial Walsh representation and a Hamming spectral objective. It does not demonstrate scalable exact training or require a quantum device to sample every implemented instance. See [MMD loss](mmd-loss.md).

## Optical construction and independent checks

The [encoding study](iqp-photonic-encoding.md) records gate-level identities and numerical checks. The [Julia study](julia-cross-check-study.md) supplies separate-toolchain checks for its explicitly listed small v3 circuits. Agreement supports those calculations, not the withdrawn trainability/hardness interpretations, a universal composition theorem, or every v4 compiler configuration.

V4 retains unnormalized completely positive maps, composes within the qualified model, and normalizes once at the end. Direct Perceval evidence covers the registered n=2/n=3 controls and n=4 ring smoke evaluations. Analytic CP-map results at larger sizes are identified separately. The repaired shared-gate fixture agrees with its final-only reference to numerical precision, but one fixture is not a general proof that intermediate postselection is harmless.

## Bounded v4 results

The [bounded release summary](v4-bounded-release.md) is the current numerical entry point and links the committed artifacts. It reports:

- Twenty main ring artifacts, representing four distinct deterministic profile/size runs rather than twenty independent replicas. Raw training TVD is approximately 0.51–0.61; held-out TVD is approximately 0.55–0.73. The two n=4 cases are three-step smoke runs.
- Eight available sibling training cells with matched substrate-reference comparisons. Faithful short-trajectory reproduction does not establish successful fitting or reproduction of every source experiment.
- Seven n=9 analytic deployed comparisons with TVD approximately 0.85–0.99 and support validity approximately 0.012–0.293. Their model cost is approximately `1.4e15`–`7.0e16` expected source attempts for 20,000 accepted outcomes. These are not collected optical samples or measured hardware runtimes.
- Matched NAT continuations that establish bounded mechanics/reproducibility. Uniform fixed-photon loss changes acceptance by a scalar, so these controls do not establish noise-adaptation efficacy or superiority.

Support validity refers to mass on the supplied finite target's support, not knowledge of the unknown data-generating distribution. Good implementation agreement and poor target fit can coexist. This release makes no photonic advantage claim.

## Acceptance status

The selected bounded release is closed for PR review. Original full-scope scientific acceptance is incomplete. The [ledger](../.planning/v4-requirement-evidence.md) remains authoritative: the owner explanation is recorded; NULL-07's hypothesis is recorded but its source-mutation experiment is unperformed. Larger-n direct optical deployment, richer source validation, unavailable sibling experiments, sampled uncertainty, and broader NAT efficacy remain qualified.

No cited paper resolves those missing experiments. Family-level complexity results, numerical agreement, fitted finite-size curves, and hardware feasibility are separate evidentiary claims.
