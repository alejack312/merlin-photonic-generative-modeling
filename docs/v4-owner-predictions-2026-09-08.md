# Owner-authored v4 null predictions

**Author:** Alejandro Jackson  
**Authored:** 2026-09-08  
**Status:** prospective predictions and falsification criteria; authored before interpreting the next registered result tables

This note records the owner's current understanding and predictions for NULL-03–08. It does not retroactively reinterpret existing canonical results. The literature review remains a learning aid, not a substitute for authorship.

## Tolerance convention

Use `1.0e-16` for exact deterministic algebraic residuals and floating-point self-consistency checks where the implementation and fixture support that precision. The binding v4 plan's `1.0e-12` probability/map fixture tolerance remains in force where prescribed. Sampled quantities, empirical success estimates, and optimization outcomes use their registered statistical or scale-aware tolerances; `1.0e-16` must not be imposed on finite-sample noise or optimizer variability.

## NULL-03 — k=0 factorization

In this repository, `k=0` removes the cross-wire interaction terms. In the generic IQP phase representation, that sets the `b_ij` and other cross-wire coefficients to zero. The diagonal operation then contains only single-wire terms and factorizes. If preparation and final measurement are also product operations, each wire evolves independently and the joint output distribution factorizes:

`p(x) = product_i p_i(x_i)`.

The distribution need not be uniform because retained single-wire phases, preparation, and measurement basis can bias each wire.

**Prediction:** under those assumptions, the k=0 joint distribution will agree with the product of its single-wire marginals. A deterministic factorization residual should be at most `1.0e-16` on the exact fixture where that tolerance is numerically supported.

**Falsification:** a residual above the registered tolerance means that at least one assumption or implementation detail is false: an interaction remains, preparation/measurement is not product, conditioning couples wires, or the reference/model implementation is inconsistent.

## NULL-04 — same-parameter ideal compilation

The compiler requires an independently defined reference semantics. Given the same intended parameters, the compiled implementation should produce the same physical map and output probabilities as the trusted reference under the same rail ordering, signs, angle scale, phase convention, winding/modulo handling, projection, loss, and output codec.

**Prediction:** same-parameter ideal compilation will agree with the independent reference up to physically irrelevant global phase, with exact deterministic residuals at or below `1.0e-16` where supported and the binding plan's `1.0e-12` probability/map fixture tolerance where prescribed.

**Falsification:** a disagreement beyond the registered tolerance establishes an inconsistency in the compiler/reference comparison. It does not by itself prove the compiler algorithm is wrong. Possible causes include rail ordering, sign convention, angle scaling, phase convention, winding handling, or output-codec mismatch. The independent reference must not reuse the compiler's implementation path or constants.

## NULL-05 — fixed-photon uniform loss

For exactly `n` prepared photons, independent uniform survival probability `eta`, and acceptance requiring all `n` photons, loss contributes the common factor `eta**n`:

`m_loss(x) = eta**n * m_ideal(x)`.

After normalization, the conditional distribution is unchanged:

`q_loss(x) = m_loss(x) / s_loss = q_ideal(x)`.

**Prediction:** uniform fixed-photon loss will reduce accepted mass while preserving conditional output shape. The loss survival factor and conditional-distribution residual should satisfy their deterministic registered tolerances, using `1.0e-16` for exact scalar/residual checks where supported and the plan's prescribed probability tolerance otherwise.

**Falsification:** a conditional-distribution change beyond tolerance means the common-scalar assumption is insufficient. Possible causes include non-fixed photon number, mode-dependent loss, detector ambiguity, multiple photon-number sectors, or a different acceptance event. The total success probability may also contain intrinsic gate, detector, source, or logical-postselection factors beyond `eta**n`.

## NULL-06 — throughput

If attempts are independent and each has the same total accepted-branch probability `s > 0`, the expected number of attempts per accepted sample is `1/s`.

**Prediction:** the reported attempts-per-accepted-sample will equal the reciprocal of the declared total success probability under the same model. `s` may combine photon survival, intrinsic gate success, detector acceptance, and logical postselection; it is not necessarily only `eta**n`.

**Falsification:** disagreement under the same fixed-probability independent-trial model indicates inconsistent success accounting or throughput bookkeeping. Finite empirical retry counts are estimates and must be compared with their registered statistical uncertainty, not a `1.0e-16` equality test.

## NULL-07 — physical/reference gap hypothesis

**Hypothesis:** the remaining gap between a physical-style output and the ideal/reference output is primarily caused by source imperfections rather than the ideal gate map or compiler.

**Prediction:** holding the ideal gate map fixed while replacing the source model with an ideal source will reduce or remove the observed gap if source imperfections are the main cause.

**Support:** changing only the source model reproduces the gap, while the fixed gate map and compilation/reference comparison remain consistent within their registered tolerances.

**Refutation:** the gap remains under an ideal source, or the compiled ideal map already disagrees with the trusted reference. The latter instead points toward compilation, convention, codec, projection, or loss handling.

The diagnostic must report absolute accepted mass and conditional-distribution quality separately, using the registered metric-specific tolerance rather than treating one scalar discrepancy as causal proof.

## NULL-08 — matched NAT continuation

The continuous parameter `theta` is mapped to a discrete key `alpha = Q(theta)`. Because `Q` is discrete, the deployed objective can contain flat regions and jumps, so continuous and discrete continuation need not follow the same trajectory.

The binding plan's registered NULL-08 control is an equal-budget continued-ideal comparison from one frozen warm start. The two registered arms use the same selected NAT algorithm, objective, discretization, optimizer state, seed/RNG, target, and evaluation budget. The owner prediction for that control is that identical ideal continuations will remain identical at the same checkpoints, while extra ideal optimization is allowed to change the parameters relative to the original warm start.

**Binding prediction:** before examining the next registered NAT result, I predict that the two identical continued-ideal arms will have matching trajectories and final state under the same warm start, optimizer state, seed/RNG, target, discretization, and evaluation budget.

**Additional exploratory hypothesis, outside the current binding NULL-08 control:** before examining a separately registered experiment that actually compares continuous and discrete continuation, I predict that continuous continuation will achieve a lower final continuous training objective than discrete-key continuation under the same warm start, optimizer state, seed/RNG, target, and evaluation budget. The current registered arms do not test this hypothesis because they run the same ideal NAT continuation.

The exploratory hypothesis concerns the continuous training objective only. It does not automatically predict better deployed-map TVD, acceptance probability, conditional MMD, or hardware performance.

**Binding support:** the matched arms have equal final state/loss history within the exact deterministic comparison tolerance.

**Binding falsification:** the matched arms diverge beyond the exact deterministic comparison tolerance under otherwise identical provenance. The tolerance must be fixed before the run; `1.0e-16` is reserved for exact state/equality checks.

For the additional exploratory hypothesis, support requires the continuous arm's final objective to be lower by more than a separately pre-registered, scale-aware optimization tolerance; a difference within tolerance or a lower discrete objective would not support it. That extra comparison is not required to close the current binding NULL-08.

## Post-prediction verification record — 2026-09-08

The next available registered continuation reports were checked after the predictions above were recorded: n=4 seeds 0–4, n=6 seed 0, and n=8 seed 0. Across all seven reports, arms A and B had identical warm-start hashes, parameter hashes, budgets, target-loss fields, fixed-reference TVD, acceptance fields, and target-improvement fields. The maximum deterministic numeric difference was `0.0`, below the project-wide exact comparison tolerance `1.0e-16`. This supports the binding same-algorithm continuation prediction only. It does not test the additional continuous-versus-discrete hypothesis.

The current-head owner-control artifact independently records NULL-03–06 as `PASS`, using exact deterministic tolerance `1.0e-16` and probability/map tolerance `1.0e-12`: [owner_controls_20260908_current.json](../results/v4_tcdp/controls/owner_controls_20260908_current.json). The repaired direct physical artifact records the selected fixed-photon `g2=0` n=2/n=3 controls as `PASS`; the corrected registered shared-gate final-only/intermediate conditional TVD is `1.942890293094024e-16` with unchanged accepted mass. This does not establish a general projection theorem: [physical_control_manifest_20260909_final3.json](../results/v4_tcdp/deploy/physical_control_manifest_20260909_final3.json).
