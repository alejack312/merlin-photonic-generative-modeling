# v4.0 owner explanation: conventions, noise, projection and conditioning

**Date:** 2026-09-09  
**Status:** owner-authored explanation recorded for WRITE-07  
**Scope:** explanatory evidence only; it does not expand the validated physical or experimental scope.

This note records the owner's explanation before scientific interpretation, as required by the v4 binding plan. The wording preserves the owner's reasoning and adds only repository-specific anchors needed to connect it to the implementation and evidence.

## Angle direction, sign and winding

Angles need a direction as well as a magnitude. Therefore the sign and winding conventions connecting the mathematical angle, the compiler representation and the physical transformation must be explicit. When code says `+theta`, we must be able to state which physical operation that means.

For this repository, the pair identity is

\[
e^{it Z_i Z_j}=e^{-it}e^{it Z_i}e^{it Z_j}\operatorname{CP}(4t).
\]

The logical-1 rail uses `PS(-2t)` for the single-qubit compensation. Pair keys are the discrete `0.1*j` catalog, selected by circular-nearest lookup. The compiler preserves winding by retaining the nearest lift of `4t`; the wrapped CP angle and lifted local compensation angle are separate values. Thus a wrapped angle alone is not enough to define the physical circuit.

Logical `0` is `(1,0)`, and output qubit 0 is the most significant bit. These conventions are part of the comparison contract, not presentation details.

## Source error versus gate/compiler error

A source error means that the prepared state is imperfect before the intended circuit acts. A gate or device error means that the physical device performs something closer to `U_tilde` instead of the intended `U`. A compiler error is different again: the compiler may map the intended abstract operation to the wrong physical circuit even when the physical components execute that circuit perfectly.

These causes must be separated. Holding the source fixed while changing the physical gate model tests gate/device effects. Holding the gate map fixed while changing the source model tests source effects. A mismatch in the ideal compiled map can instead indicate a convention or compilation problem, such as rail ordering, sign, scale, phase convention, winding, projection or output-codec mismatch.

The primary v4 deployment model is narrower than this taxonomy: fixed photon number (`g2=0`) with explicit independent uniform per-photon loss. It is not a claim to have modeled arbitrary source imperfections, detector noise or general hardware gate noise.

## Final versus intermediate projection

Suppose a state evolves through `U1` and `U2`. Final projection applies the validity or acceptance test after the complete evolution. Intermediate projection removes invalid components between stages. A component that leaves the selected subspace can sometimes evolve back into it later, so final-only and intermediate projection need not agree.

The selected v4 composition rule applies unnormalized, trace-decreasing CP maps in sequence and normalizes only once at the end. Per-stage normalization would change the instrument. The registered shared-gate control records conditional TVD `0.585411845271861` between final-only and intermediate projection, so final-only is the supported boundary; no general equivalence is claimed.

## Loss, post-selection and conditioning

If an experiment has 1,000 attempts, 100 accepted events, and 90 desired outputs among those accepted events, then

\[
P(\mathrm{accepted})=100/1000=0.10,
\qquad
P(\mathrm{desired}\mid\mathrm{accepted})=90/100=0.90.
\]

Loss is the physical disappearance or non-detection of a resource. Post-selection keeps only events satisfying an acceptance criterion. Conditioning describes the normalized distribution within those retained events. Acceptance probability and conditional quality must be reported separately: a 1% acceptance device with 99% conditional quality may be less useful than a 90% acceptance device with 90% conditional quality.

Under the selected fixed-`n`, uniform-loss assumptions, accepted mass receives the common factor `eta**n`, while the normalized conditional distribution is unchanged. This is not a universal rule for photon-number mixtures, mode-dependent loss or ambiguous detection. Under independent repeated attempts, expected attempts per accepted sample are `1/s`, where `s` is the absolute acceptance probability for the declared model.

## Limits of small-`n` validation

Validation at `n=1,2,3,4` demonstrates agreement on those tested cases. It does not prove correctness for every `n`. A defect can depend on circuit size, topology, shared qubits, numerical accumulation or an edge case absent from the fixtures.

The direct physical evidence is therefore reported separately from analytic-map self-consistency. The fixed-photon direct controls cover the registered small-`n` cases; they do not certify arbitrary-size full-Fock behavior, multiphoton source sectors or hardware behavior.

## NAT scope

With continuous parameters mapped to discrete keys, `theta -> Q(theta)` can create plateaus and jumps. NAT therefore compares a specific continuation procedure, not the correctness of the whole physical model.

The registered v4 control uses matched continued-ideal arms from one frozen warm start with the same target, optimizer state, seed/RNG, parameterization, evaluation budget and checkpoint comparison. If the two registered arms agree, that supports the tested continuation property. It does not establish full-Fock correctness, realistic source or gate noise, arbitrary-`n` compilation correctness, hardware advantage or NAT superiority. Target improvement, fixed-reference distance and acceptance remain separate quantities.

## Evidence boundary

This note closes the owner-authored explanation requirement. It does not convert the separately recorded NULL-07 hypothesis into an experiment, and it does not upgrade the documented broader physical/full-Fock, larger-`n` deployment, unavailable-input or sampled-uncertainty gaps.

