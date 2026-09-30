# R6: causal commuting M1 policies collapse to a uniform IQP mixture

2026-09-30 — **project derivation, assistant-drafted, owner review pending**.

## Branch derivation

Use the ancilla basis and negative-phase convention in [M1 section 2](v4-mbqc-adaptivity-plan.md#2-m1-is-a-non-adaptive-iqp-construction). Let $P_j=Z_{G_j}$ and $\theta_j(s_{<j})$ be any real-valued causal policy. For a fixed history, projection gives

$$K_{j,0}=2^{-1/2}e^{-i\theta_j P_j},\qquad
K_{j,1}=i2^{-1/2}P_j e^{-i\theta_j P_j}.$$

Each conditional map obeys $K_{j,s_j}^\dagger K_{j,s_j}=I/2$. **Causality** is used here: the same angle is selected for both possible next outcomes, from the already available history. Thus each next bit has conditional probability 1/2, all histories are realizable, and $P(s)=2^{-M}$. Substituting a future-dependent angle would not define this sequential measurement instrument.

For a realized string s, **commutation** of all $P_j$ lets us move every byproduct past every exponential and combine them:

$$K_s=i^{|s|}2^{-M/2}\left(\prod_j P_j^{s_j}\right)
\exp\left[-i\sum_j\theta_j(s_{<j})P_j\right].$$

The product of byproducts is $Z_{G^Ts}$, with binary arithmetic. Measuring data in X maps that product to an XOR of the raw outcome y. Consequently

$$p(s,y)=2^{-M}q_{\theta(s)}(y\mathbin{\mathrm{XOR}}G^Ts),\qquad
q_A(x)=2^{-M}\sum_s q_{\theta(s)}(x).$$

Every branch table is from the ordinary non-adaptive IQP family. Control D with precisely these tables and weights equals A, so equal distribution-based population scores follow. This says nothing about A versus a single open-loop table B, a training optimizer, or the physical cost of realizing the mixture. No A/B/D training was run.

This derivation covers ideal, complete, causal angle policies on the commuting M1 incidence graph with the specified final XOR. It does **not** cover non-commuting gates, state injection (SI), noisy instruments, post-selection, or free physical graph preparation. Owner review and the owner's portfolio/case-study takeaway remain pending.

## Measurement-angle convention — source mapping UNVERIFIED

The stated $|b_0(\theta)\rangle=\cos\theta|0\rangle+i\sin\theta|1\rangle$ has Bloch vector $(0,\sin 2\theta,\cos 2\theta)$: it is in the Y–Z plane, not the standard equatorial X–Y basis $|+_a\rangle=(|0\rangle+e^{ia}|1\rangle)/\sqrt2$. A direct identification of a with theta is therefore invalid.

After a Hadamard change of frame,

$$H|b_0(\theta)\rangle=\frac{e^{i\theta}|0\rangle+e^{-i\theta}|1\rangle}{\sqrt2}
=e^{i\theta}|+_{-2\theta}\rangle.$$

In that explicitly declared frame, $a=-2\theta$ modulo $2\pi$. Thus $a\mapsto-a$ gives $\theta\mapsto-\theta$, while $a\mapsto a+\pi$ gives $\theta\mapsto\theta-\pi/2$ (equivalently $\theta+\pi/2$ modulo the basis-ray period pi), **not** $\theta+\pi$. The masterclass p12 rule $a'=(-1)^s a+t\pi$ would give $\theta'=(-1)^s\theta-t\pi/2$ in this frame. Whether the slides use this frame, sign and outcome-label convention has not been verified; this is a project algebraic translation, not source validation. The Hadamard frame cannot silently be applied to the entire resource graph without transforming its other operations.

A theta shift of pi changes each basis vector only by global sign. In contrast, theta plus pi/2 swaps the two basis rays (up to signs), and can shift the ordinary IQP output table. In the richer fixture sign flip and plus pi are identical-table cases; plus pi/2 is distinct. Sign invariance is **not universal**: the random sample finds counterexamples. The empirical pi invariance observations below are reported as observations; the basis-ray statement above is independently algebraic.

## Reproducible numerical report

Fixture: n=3, M=3, G rows `(100), (110), (111)` (weights 1,2,3); theta `(0.13,0.27,0.41)`. Ancilla 2 depends on s1, ancilla 3 uses `0.41 + 0.19*s1 - 0.23*s2`. Isolated second-angle comparisons hold all other angles fixed, preventing the third-angle policy from masking vacuity.

| Second-angle rule | Joint gap | Corrected mixture gap | Isolated table gap |
|---|---:|---:|---:|
| minus theta | 6.9389e-17 | 3.3307e-16 | 1.1102e-16 (identical, vacuous) |
| theta plus pi | 6.9389e-17 | 3.3307e-16 | 1.1102e-16 (identical, vacuous) |
| theta plus pi/2 | 6.9389e-17 | 2.7756e-16 | 0.709304263544835 (distinct) |

Maximum branch-weight gap: 8.3267e-17; total-mass gap: 4.4409e-16. Negative-control gaps: dropped XOR 0.3151413666763097; reversed output bit order 0.23165188837412776; incorrect weights 0.07718312466352861. Fixed-angle collapse and self/future dependency rejection also pass.

**Empirical, random sample of N=100 cases**: seeded NumPy generator 20260930; rejection-sampled asymmetric 3x3 binary G with no zero rows (duplicates and rank deficiency allowed), independent angles uniform on [-pi,pi), one randomly selected generator per case. Maximum sign-flip table gap: **0.8137486499024578** (invariance fails in this sample). Maximum plus-pi gap: **7.771561172376096e-16** (invariant to numerical precision in this sample). No population-frequency estimate or general theorem is inferred from this sampling check.

Run `venv/Scripts/python.exe -m pytest tests/mbqc/test_r6_chain_mixture_null.py -q -s`. The report-only random test prints values and deliberately makes no invariance assertion.

Mixture-to-individual-branch gaps (minimum/maximum): sign and pi **0.001134762192701061 / 0.14492207662610668**; pi/2 **0.32799863047307065 / 0.44383261616221514**. All exceed the existing non-vacuity threshold 1e-3. Sign/pi chains are nontrivial because of the third-angle policy, while their isolated second-angle rules remain vacuous. Equal-angle collapse gap: **1.1102230246251565e-16**. A deliberate zero-distance probe of this non-vacuity assertion gave **3 failed, 11 deselected**; restoring the actual distances passed.
