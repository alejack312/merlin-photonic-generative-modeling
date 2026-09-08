# Literature review for NULL-03–08 and WRITE-07

**Status:** bounded study guide; background evidence only.  
**Prepared:** 2026-09-08
**Purpose:** give the owner a source-grounded foundation for writing the prospective NULL-03–08 records and the owner-authored WRITE-07 explanation.

## Boundary and use

This review does not close any v4 acceptance criterion, supply the owner's predictions, or write the owner's explanation.  It must not be converted into retrospective predictions after inspecting new result tables.  The owner should record predictions, falsification rules, and the date of authorship before interpreting the corresponding artifacts.  The repository labels `k=0`, alpha keys, NULL-03–08, and WRITE-07 are project terminology; they are not names used by the cited literature.

The current study scope is also not a literature conclusion: the repository has declared fixed-photon `g2=0` with explicit uniform loss for D1, discrete alpha-key NAT with continuous singles for D2, and a source-style initialization choice for D3.  Those are scope decisions to be explained and tested, not outcomes predicted by these papers.

## A compact map from literature to the owner’s questions

| Question family | What the literature supports | What remains project-specific |
|---|---|---|
| k=0 / product-state control | IQP is a commuting, diagonal-in-a-convenient-basis model; if all cross-wire terms are removed, the circuit factorizes into one-wire components. | Whether the repo’s `k=0` retains singles, and the resulting distribution under its exact preparation and measurement convention. |
| Ideal compiled versus raw reference | Linear-optical unitaries admit multiple decompositions; beam-splitter phases, rail order, and phase conventions must be fixed. | Whether the repo’s compiled matrix and raw trained reference represent the same physical map and output codec. |
| Loss and postselection | A selected branch is described by an unnormalized probability/mass and a conditional distribution after normalization. Fixed-photon uniform loss has a special acceptance factor. | Which source, detector, accepted-photon, and postselection model D1 actually means. |
| Throughput | Probabilistic optical gates and loss-tolerant encodings carry resource/success trade-offs; attempts per accepted sample depend on the full accepted branch. | The numerical throughput for the repo’s network, source, and detector scope. |
| Projection timing | Measurement instruments retain both outcome probabilities and conditional state changes; intermediate measurement can disturb later statistics. | Whether the repo’s final-only and intermediate constructions satisfy the assumptions needed for equivalence. |
| alpha-key versus continuous optimization | Parameter-shift methods concern differentiable continuous gate parameters; SPSA is a gradient-free stochastic method for noisy multivariate objectives. | The effect of the repo’s integer circular keys, rounding, warm start, optimizer state, and equal-budget continuation. |

## 1. IQP, k=0, and product-state controls

The foundational IQP papers define a restricted computation built from commuting gates, commonly represented by preparing a product state with Hadamards, applying a diagonal commuting operation, and measuring after another Hadamard layer. Shepherd and Bremner introduced the temporally unstructured model; Bremner, Jozsa, and Shepherd formalized IQP and its postselected complexity consequences ([S1](#sources), [S2](#sources)). Their hardness statements concern families with suitable interacting gates and assumptions about classical simulation; they do not imply that every IQP instance is hard.

For the repo’s control, the useful algebra is simpler than the hardness results. Write the diagonal phase as

\[
D = \exp\!\left(i\sum_i a_i Z_i + i\sum_{i<j} b_{ij} Z_iZ_j + \cdots\right).
\]

If every cross-wire coefficient `b_ij` and every higher-order cross-wire term is zero, then `D = ⊗ᵢ Dᵢ`. With a product input and product final measurement, the output probability factorizes, `p(x) = ∏ᵢ pᵢ(xᵢ)`. This is a derivation from tensor-product algebra, not a claim that the literature uses the repo’s `k` notation. It also does not imply a uniform distribution: retained one-wire phases, the input state, the measurement basis, and angle conventions determine each `pᵢ`.

The control question for NULL-03 is therefore narrower than “does IQP work?”: state exactly what `k=0` removes, what it retains, and which source/detector model is being held fixed. The literature supports factorization under the stated product assumptions; it does not supply the owner’s distributional prediction for this implementation.

The later IQP literature reinforces the need for controls. Bremner, Montanaro, and Shepherd’s average-case result concerns particular interacting commuting families and conjectures ([S3](#sources)). A no-interaction control should not be used as a generic proxy for the interacting study, nor should a product-state control be described as evidence for or against the complexity conjectures.

## 2. Ideal compilation and source-versus-gate conventions

Reck et al. showed that arbitrary finite-dimensional unitaries can be decomposed into optical elements ([S4](#sources)); Clements et al. gave a different, lower-depth universal interferometer design and analyzed propagation-loss implications ([S5](#sources)). The practical lesson is that a target matrix is not a unique list of beam splitters and phase shifters. A comparison must freeze:

- mode/rail ordering and input-output bit conventions;
- the beam-splitter matrix convention, including reflection/transmission phases;
- the sign and scale used to map an abstract angle to an optical phase;
- whether the implementation preserves a lifted phase/winding or reduces modulo `2π`;
- where source preparation, optical loss, detector loss, heralding, and logical postselection occur.

Global phase is physically irrelevant for a complete probability measurement, but relative phases are not. A compiler that differs by a rail permutation, a local phase, a sign, or an angle scale can therefore produce a different encoded map while still looking numerically close at the parameter-label level. The appropriate ideal control is equality of the compiled physical map and the output probability distribution under the same codec, not equality of a raw parameter vector.

Perceval’s peer-reviewed platform paper describes separate circuit building blocks for sources, beam splitters, phase shifters, and detectors, along with strong and sampling backends ([S6](#sources)). Its current public documentation is a useful implementation-level supplement: source parameters include emission probability, multiphoton component, indistinguishability, and source loss, while processors report results together with a selected-state performance. The documentation is not a substitute for a physical validation paper, so these API semantics should be treated as software evidence and checked against the version used by the repo.

## 3. Fixed-photon loss, postselection, success probability, and conditioning

There are three quantities that should remain separate:

1. the unnormalized accepted mass `m(x,E) = Pr(output=x and accepted event E)`;
2. the success probability `s(E) = Σₓ m(x,E)`;
3. the conditional distribution `q(x|E) = m(x,E)/s(E)`, defined only when `s(E)>0`.

This is the operational content of a trace-decreasing branch: the trace is the branch probability, and normalization gives the conditional state or distribution. Knill’s analysis of postselected linear-optical gates makes the success probability explicit and bounds it for nonlinear-sign-shift constructions ([S8](#sources)). Dressel and Jordan formulate the same distinction in terms of quantum instruments, where outcome probabilities and conditional state changes are both part of the laboratory description ([S12](#sources)).

The fixed-photon loss control is a special case. Suppose exactly `n` photons are prepared, each independently survives a uniform transmissivity `η`, and the accepted event requires all `n` photons to be present. Then the all-survive acceptance factor is `ηⁿ`. If uniform loss commutes with the lossless interferometer and the conditional event retains the same `n`-photon sector, the conditional output distribution is unchanged by this scalar factor. That is a derivation under explicit assumptions, not a universal statement about noisy photonic circuits.

Those assumptions fail or change when the source can emit vacuum or multiphoton components, when loss is mode-dependent, when threshold detection merges photon numbers, or when acceptance allows several photon-number sectors. Rohde and Ralph identify loss and mode mismatch as dominant practical error sources in boson sampling and analyze robustness under their model ([S9](#sources)). Aaronson and Brod study a different lossy model in which an unknown subset of photons is lost at the sources; their complexity result is not evidence that a fixed-photon post-hoc `ηⁿ` correction is valid for a source-plus-detector experiment ([S10](#sources)).

For this reason, NULL-05 should be written only after the owner states the photon-number and acceptance assumptions. A result can preserve conditional shape while losing acceptance mass, or it can alter both shape and mass. Comparing only normalized vectors cannot distinguish these cases.

## 4. Throughput and resource scaling

For independent trials with accepted-branch probability `s`, the expected number of attempts per accepted sample is `1/s`. In a full experiment, `s` may factor into or be bounded by source emission, transmission, gate heralding, detector acceptance, and logical postselection. The exact factorization depends on the physical model; multiplying an `ηⁿ` term by unrelated success factors without defining the events can double-count or omit failures.

KLM established that single photons, passive linear optics, photodetection, and feed-forward can support scalable linear-optical quantum computation, while also making clear that nondeterministic operations and resource overhead are central parts of the scheme ([S7](#sources)). Varnava, Browne, and Rudolph showed that one-way linear-optical schemes can tolerate loss with polynomially increasing resources and logarithmically increasing photon lifetimes under their encoding assumptions ([S11](#sources)). These are architecture-level resource results, not throughput predictions for the repo’s small fixed-photon circuits.

NULL-06 should keep two models separate if both are discussed: a trace-decreasing CP-map deployment cost and a heralded physical resource cost. The first can report accepted mass for a declared map; the second must count attempts and the source/detector/gate events required to obtain a usable sample. Neither model is resolved by the literature review, and neither is interchangeable with a normalized TVD or fidelity.

## 5. Final-only versus intermediate projection

The deferred-measurement principle is conditional, not a blanket license to move every projection to the end. Deferral is safe when the measurement record can be retained coherently or classically and later operations are adjusted so that the final joint statistics are preserved. A physical projection that removes amplitudes, reveals a hidden label, or changes which later optical modes interact is a different operation.

The instrument viewpoint is the cleanest bookkeeping: an intermediate selected branch is represented by an unnormalized map `E₁` followed by a projector/acceptance map `P` and later evolution `E₂`. Its accepted mass is `Tr[E₂(P(E₁(ρ)))]`. A final-only construction instead applies the later evolution before selecting the final event, schematically `Tr[P_f(E₂(E₁(ρ)))]`. These expressions coincide only under topology and commutation/record assumptions that must be proved for the particular circuit. Normalizing after each local projection introduces another nonlinear conditioning step and is not generally the same as composing unnormalized branches and normalizing once.

Postselection research makes the dependence on the measurement sequence explicit: conditional states are defined relative to the selected measurement outcome and its placement in the sequence ([S12](#sources)); postselected metrology likewise defines a projective postselection between the unknown evolution and the final measurement, with a separate postselection probability ([S16](#sources)). The repo’s final-only/intermediate comparison is therefore a legitimate null experiment, but the cited literature does not prove equivalence or non-equivalence for its hidden-label topology. That remains a repo-specific hypothesis to test with absolute mass and conditional-distribution diagnostics.

## 6. Matched discrete alpha-key and continuous-angle optimization

Two different parameter spaces must be named explicitly:

- a continuous angle `θ ∈ ℝ` used by an optical gate or a differentiable ideal objective;
- a discrete circular key `α ∈ ℤ` that selects a compiled angle, possibly with a lifted integer winding.

Parameter-shift methods derive gradients for continuous parametrized quantum circuits and their measurement objectives ([S13](#sources)). They do not, by themselves, provide a gradient through a nearest-key lookup. If the compiled objective is `f(Q(θ))`, where `Q` rounds to a key, the function can be piecewise constant or discontinuous in `θ`; a small finite difference of the raw angle may measure the same key twice or straddle a boundary. That conclusion follows from the quantizer’s definition and should be checked against the repo’s exact key map, not inferred from continuous-angle literature.

SPSA is a primary source for gradient-free stochastic approximation with simultaneous perturbations in multivariate objectives ([S14](#sources)). It is relevant as an optimization family, not as evidence that it is the correct D2 choice. McClean et al. show why random parameterized circuits can have exponentially small gradients in certain settings ([S15](#sources)); this motivates reporting optimizer behavior and scale carefully, but it does not predict the repo’s NAT outcome.

A matched control should hold fixed every factor that is not the treatment: warm-start parameters, optimizer state, RNG stream, data/target, discretization, stopping rule, and evaluation budget. “Same number of steps” is insufficient when one arm evaluates several neighbors per step or when one arm has a different compilation cost. The comparison should preserve at least raw continuous parameters, compiled keys, deployed vectors, target metrics, accepted mass, and evaluation counts.

## 7. Null-experiment matrix for study design

The following are control designs, not predictions or acceptance decisions.

| Control | Isolates | Record before looking at new result tables |
|---|---|---|
| `k=0` / no pair terms | Product-state factorization versus interaction-dependent behavior | Exact retained singles, preparation, measurement, and expected factorization criterion. |
| Same parameter, ideal compiled map | Compiler/sign/scale/winding and codec agreement | Whether raw and compiled objects are asserted equivalent, and which metric is expected to be exactly equal by construction. |
| Fixed-photon, uniform loss | Acceptance-only scaling under a declared `n`-photon sector | Photon-number, loss placement, all-survive event, and whether conditional distribution is the estimand. |
| Source multiphoton or detector-loss arm | Source/detector noise versus gate-map noise | Which sectors are included and whether counts are PNR or thresholded. |
| Final-only versus intermediate projection | Projection placement and hidden-label disturbance | Topology assumptions under which equality would hold, plus the absolute and conditional failure criteria. |
| Discrete-key continuation versus continuous continuation | Optimization treatment effect under matched budget | Warm start, optimizer/RNG state, key lookup, number of evaluations, and comparison metric. |
| Zero-step, bystander, and no-gate controls | Harness and bookkeeping errors | Which exact identities must hold from construction and which mutations must fail. |

The control table is intentionally silent about the sign, direction, magnitude, or scientific interpretation of any future result. It is a checklist for prospective authorship, not a substitute for NULL-03–08.

## 8. Owner study prompts

After reading the sources, the owner should be able to answer unaided, in their own words:

1. What does `k=0` remove and retain in this repo, and why does that imply (or fail to imply) a product distribution?
2. Which object is being compared: a raw IQP parameterization, a compiled interferometer, a deployed CP instrument, or a normalized conditional distribution?
3. What event defines success, what is its probability, and which output distribution is conditional on it?
4. Under which exact photon-number assumptions is `ηⁿ` valid, and what changes when source multiphoton sectors or detector loss are admitted?
5. What would make final-only and intermediate projection equivalent, and what observable would falsify that assumption?
6. Why is a discrete alpha-key objective not automatically differentiable in the continuous angle, and what makes the NAT control budget-matched?

The answers to these prompts are the owner’s NULL-03–08 and WRITE-07 work. This document supplies definitions, derivations, and source trails only; it does not supply those answers.

## Evidence limitations

- The IQP papers establish restricted-model definitions and complexity-theoretic consequences, not the repo’s exact photonic compiler or its finite-size controls.
- The loss papers study different physical and complexity models. They support separating photon-number sectors, loss placement, acceptance, and conditional distributions; they do not establish a universal invariance claim for `g2>0`.
- Reck and Clements establish decomposition methods, not the repo’s sign, rail, codec, or winding convention. Those require direct implementation evidence.
- Perceval’s paper and documentation describe software capabilities and models; software semantics do not certify a physical source or detector model without calibration and experiment-specific evidence.
- The optimizer papers concern continuous gradients or stochastic approximation in their stated settings. They do not predict the repo’s discrete-key NAT behavior.
- No cited source resolves the repository ledger, the owner’s acceptance criteria, the unperformed larger-n physical experiments, or the owner’s prospective predictions. The review must not be used to claim that it does.

## Sources

**[S1]** Dan Shepherd and Michael J. Bremner, “Temporally unstructured quantum computation,” *Proceedings of the Royal Society A* **465**(2105), 1413–1439 (2009). DOI: [10.1098/rspa.2008.0443](https://doi.org/10.1098/rspa.2008.0443). Primary IQP model paper.

**[S2]** Michael J. Bremner, Richard Jozsa, and Dan J. Shepherd, “Classical simulation of commuting quantum computations implies collapse of the polynomial hierarchy,” *Proceedings of the Royal Society A* **467**(2126), 459–472 (2011). DOI: [10.1098/rspa.2010.0301](https://doi.org/10.1098/rspa.2010.0301). Primary IQP/postselection complexity result.

**[S3]** Michael J. Bremner, Ashley Montanaro, and Dan J. Shepherd, “Average-case complexity versus approximate simulation of commuting quantum computations,” *Physical Review Letters* **117**, 080501 (2016). DOI: [10.1103/PhysRevLett.117.080501](https://doi.org/10.1103/PhysRevLett.117.080501). Primary average-case IQP result.

**[S4]** Michael Reck, Anton Zeilinger, Herbert J. Bernstein, and Philip Bertani, “Experimental realization of any discrete unitary operator,” *Physical Review Letters* **73**(1), 58–61 (1994). DOI: [10.1103/PhysRevLett.73.58](https://doi.org/10.1103/PhysRevLett.73.58). Primary universal interferometer decomposition.

**[S5]** William R. Clements, Peter C. Humphreys, Benjamin J. Metcalf, W. Steven Kolthammer, and Ian A. Walmsley, “Optimal design for universal multiport interferometers,” *Optica* **3**(12), 1460–1465 (2016). DOI: [10.1364/OPTICA.3.001460](https://doi.org/10.1364/OPTICA.3.001460). Primary alternative compilation and loss analysis.

**[S6]** Nicolas Heurtel et al., “Perceval: A Software Platform for Discrete Variable Photonic Quantum Computing,” *Quantum* **7**, 931 (2023). DOI: [10.22331/q-2023-02-21-931](https://doi.org/10.22331/q-2023-02-21-931). Peer-reviewed platform paper; source/circuit/detector documentation is additionally available at [Perceval Source](https://perceval.quandela.net/docs/v1.1/reference/components/source.html) and [Perceval Processor](https://perceval.quandela.net/docs/v1.2/reference/runtime/processor.html).

**[S7]** Emanuel Knill, Raymond Laflamme, and Gerald J. Milburn, “A scheme for efficient quantum computation with linear optics,” *Nature* **409**, 46–52 (2001). DOI: [10.1038/35051009](https://doi.org/10.1038/35051009). Primary LOQC resource and nondeterministic-gate proposal.

**[S8]** Emanuel Knill, “Bounds on the probability of success of postselected nonlinear sign shifts implemented with linear optics,” *Physical Review A* **68**, 064303 (2003). DOI: [10.1103/PhysRevA.68.064303](https://doi.org/10.1103/PhysRevA.68.064303). Primary success-probability bounds for postselected optical gates.

**[S9]** Peter P. Rohde and Timothy C. Ralph, “Error tolerance of the boson-sampling model for linear optics quantum computing,” *Physical Review A* **85**, 022332 (2012). DOI: [10.1103/PhysRevA.85.022332](https://doi.org/10.1103/PhysRevA.85.022332). Primary analysis of loss and mode mismatch.

**[S10]** Scott Aaronson and Daniel J. Brod, “BosonSampling with lost photons,” *Physical Review A* **93**, 012335 (2016). DOI: [10.1103/PhysRevA.93.012335](https://doi.org/10.1103/PhysRevA.93.012335). Primary fixed-number/source-loss complexity model.

**[S11]** Michael Varnava, Daniel E. Browne, and Terry Rudolph, “Loss tolerant linear optical quantum memory by measurement-based quantum computing,” *New Journal of Physics* **9**, 203 (2007). DOI: [10.1088/1367-2630/9/6/203](https://doi.org/10.1088/1367-2630/9/6/203). Primary loss-tolerant resource-scaling proposal.

**[S12]** Justin Dressel and Andrew N. Jordan, “Quantum instruments as a foundation for both states and observables,” *Physical Review A* **88**, 022107 (2013). DOI: [10.1103/PhysRevA.88.022107](https://doi.org/10.1103/PhysRevA.88.022107). Primary instrument/conditioning framework.

**[S13]** Maria Schuld, Ville Bergholm, Christian Gogolin, Josh Izaac, and Nathan Killoran, “Evaluating analytic gradients on quantum hardware,” *Physical Review A* **99**, 032331 (2019). DOI: [10.1103/PhysRevA.99.032331](https://doi.org/10.1103/PhysRevA.99.032331). Primary parameter-shift/continuous-gradient reference.

**[S14]** James C. Spall, “Multivariate stochastic approximation using a simultaneous perturbation gradient approximation,” *IEEE Transactions on Automatic Control* **37**(3), 332–341 (1992). DOI: [10.1109/9.119632](https://doi.org/10.1109/9.119632). Primary SPSA reference.

**[S15]** Jarrod R. McClean et al., “Barren plateaus in quantum neural network training landscapes,” *Nature Communications* **9**, 4812 (2018). DOI: [10.1038/s41467-018-07090-4](https://doi.org/10.1038/s41467-018-07090-4). Primary training-landscape result; motivation for, not a prediction of, optimizer controls.

**[S16]** David R. M. Arvidsson-Shukur et al., “Quantum advantage in postselected metrology,” *Nature Communications* **11**, 3775 (2020). DOI: [10.1038/s41467-020-17559-w](https://doi.org/10.1038/s41467-020-17559-w). Primary postselected prepare-measure treatment with an explicit renormalized state and postselection probability.
