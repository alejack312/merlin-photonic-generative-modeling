# Literature scope and limits of the photonic IQP construction

Updated 2026-09-10. This is a learning and implementation case study, with bounded numerical checks. It does not establish a new optical universality construction, a quantum advantage, or an exhaustive absence of prior work. The [original Phase 8 search and owner decision](https://github.com/alejack312/merlin-photonic-generative-modeling/blob/41c0d1b832e95161f1d92dba9ef0e2b24dcd16a5/docs/iqp-lit-scoping.md) remain available as historical records; their novelty language is superseded here.

## Established constructions and related models

Universal linear-optical quantum computation predates this project. Encoding qubits in optical modes and using measurement-assisted gates is established work; implementing an IQP gate set within that framework is not, by itself, a new universality result. [Knill, Laflamme and Milburn](https://arxiv.org/abs/quant-ph/0006088).

Douce et al. study a continuous-variable IQP construction with quadrature operations, finite squeezing and homodyne measurement. It is not the photon-counting circuit implemented here. Quadrature and Fock descriptions nevertheless describe the same bosonic systems in different bases: they are not unrelated physical theories. This project does not inherit that paper's hardness proof by using photonics. [Douce et al.](https://arxiv.org/abs/1607.07605).

IQP circuits also have measurement-based realizations; this does not mean every nonadaptive measurement-based computation is the particular IQP ansatz used here. [Hoban et al.](https://arxiv.org/abs/1304.2667).

Classically trained photonic generative models are already a research topic. Kurkin et al. present boson-sampling-based Born machines and classical training constructions; their model and guarantees should not be identified with this repository's finite IQP implementation. Salavrakos et al. study linear-optical Born machines and loss mitigation; their abstract does not justify calling that model this project's IQP ansatz. [Kurkin et al.](https://arxiv.org/abs/2603.11014), [Salavrakos et al.](https://arxiv.org/abs/2405.02277).

## What the literature does and does not license

| Topic | Relevant result | Boundary for this repository |
|---|---|---|
| IQP sampling hardness | Conditional hardness results for specified families and approximation regimes | Not a certificate for every parameter setting, a product circuit, or a noisy trained checkpoint. [Bremner et al.](https://arxiv.org/abs/1504.07999) |
| Classical training | IQP parity expectations admit classical additive-error estimation used in an MMD training construction | Estimating a loss is distinct from efficient optimization and from sampling the full distribution; this release uses bounded exact enumeration. [Recio-Armengol et al.](https://arxiv.org/html/2503.02934v2) |
| Kernel bandwidth | A Hamming-kernel trainability analysis under specified ansatz/ensemble assumptions | Its bandwidth notation and assumptions must be translated before comparison; it is not a theorem about the v3 Euclidean bin grid. [Rudolph et al.](https://arxiv.org/html/2305.02881v2) |
| Photonic gradients | A representation-theoretic analysis and numerical studies of photonic loss landscapes | The Bhattacharyya-loss and circuit-ensemble results do not supply a transferable qubit-count threshold for this IQP MMD study. [Xie et al.](https://arxiv.org/abs/2605.11879) |
| Particle loss | Efficient approximate simulation when the surviving photon count is o(sqrt(n)) in the stated fixed-loss model | This is narrower than merely a vanishing surviving fraction, and does not directly characterize our conditioned logical output. [Oszmaniec and Brod](https://arxiv.org/abs/1801.06166) |
| Noisy shallow optics | Classical simulation results for specified noisy constant-depth optical models | Not a blanket theorem for every postselected optical circuit. [Oh](https://arxiv.org/abs/2406.08086) |
| Generative trainability | A trade-off involving anticoncentration and average trainability | Our small, classically sampleable v3 families and metric artifacts do not test this result or establish a loss threshold. [Herbst et al.](https://arxiv.org/abs/2512.24801) |

## Present contribution

The defensible contribution is an additive implementation with explicit conventions, matched finite comparisons, small-circuit optical controls and an auditable correction history. The [bounded release](v4-bounded-release.md) reports poor target fits alongside conditional agreement and expected postselection cost. Its larger deployment arms are analytic references. No hardware experiment, broad full-Fock equivalence, or scalable sampling advantage is established.

This review checks the cited sources against the claims made here. It is not a systematic review of all photonic IQP literature. For the algebra and kernel conventions, see [IQP baseline](iqp-baseline.md) and [MMD loss](mmd-loss.md).
