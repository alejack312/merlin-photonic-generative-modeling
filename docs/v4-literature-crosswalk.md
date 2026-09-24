# v4 literature: equations, assumptions, and transfer limits

Date: 2026-09-24. Companion to the [completion audit](v4-full-completion-audit.md) and [benchmark specification](v4-advantage-benchmark-spec.md). Equations marked **project derivation** are independently specified checks, not claims of new theorems. Proposed experiments are not executed results.

## 1. Source register and reading depth

The three supplied v1 PDFs are the version-pinned primary sources. Local study notes and lecture slides orient the reading; their summaries do not override the papers. Public arXiv metadata was checked, but no later version is silently substituted.

| Key | Source | Relevant inspected material | Use |
|---|---|---|---|
| BU | Herrero-González et al., [The Born Ultimatum, 2511.01845v1](https://arxiv.org/abs/2511.01845v1), 45 PDF pages | §§I A–C, II, V–VII; Appendix E discrepancy derivation; selected theorem page 10 visually checked | Fourier formalism and surrogate/deployment benchmark design |
| BS | Mhiri et al., [Boson sampling beyond the dilute regime, 2604.14323v1](https://arxiv.org/abs/2604.14323v1), 56 PDF pages | §II definitions, §III B Theorems 1–2/Corollary 2, conclusions; page 10 visually checked | Ensemble second moments and theorem applicability boundary |
| GEN | Raj et al., [Train classical, deploy quantum requires rethinking generalization, 2608.31117v1](https://arxiv.org/abs/2608.31117v1), 22 PDF pages | §§III–V definitions, Theorem 1/Corollary 1, sampling protocol; page 6 visually checked | Generalization challenge and metric controls |
| MC | Danos, Kashefi, Panangaden, [The Measurement Calculus](https://arxiv.org/abs/0704.1263) | Primary PDF §4 Proposition 8 and §5 pattern composition; local masterclass pp. 14–23 | J/CZ compilation and causal measurement dependencies |
| FLOW | Danos/Kashefi, [Determinism in the one-way model](https://arxiv.org/abs/quant-ph/0506062); Browne et al., [Generalized flow](https://arxiv.org/abs/quant-ph/0702212) | Primary abstracts and local flow notes; full proof audit remains a compiler prerequisite | Flow certificate; no claim that failure of ordinary flow proves nondeterminism |
| SI | Monbroussou et al., [Towards quantum advantage with photonic state injection](https://arxiv.org/html/2410.01572v1) | §2.1 definition and §3 controllability discussion; not a complete complexity-proof review | Alternative adaptive instrument; no inherited sampling advantage |
| PQCNN | Monbroussou et al., [Photonic QCNNs with adaptive state injection](https://arxiv.org/html/2504.20989v1) | §II architecture and experiment/task description | Hardware-motivated extension; classification is not our generative benchmark |

Local PDF SHA-256 identities:

```text
2511.01845v1.pdf   2e60d1917949e0ec433b05aa71841c7d9fa12622be3c543e9a0d3035b28201cf
2604.14323-v1.pdf  750c2a8684ede285fc997039378a2e93e911e9c0dc58288ae5875d6823f1601d
2608.31117-v1.pdf  1773ebec755ef491e693d97cd846346363987baebdb5a776d9b2ab6625fb7986
```

Local locations are those supplied with the task: BU under `quantum-information-material/measurement-based-quantum-computing/papers/`; BS and GEN under their arXiv-numbered `papers/` directories. Both 60-page lecture PDFs were text-extracted; measurement-calculus sections and FQC25 state-injection references were consulted. This is a targeted methods review, **not a full proof verification of all 123 primary-paper pages or the slides**.

BU points to [QCBM_correlator_surrogates](https://github.com/quantumsoftwarelab/QCBM_correlator_surrogates). At inspection, its public main-branch listing exposed a README/template, not an executable benchmark implementation. Treat it as an unavailable replication dependency until a usable revision and license are pinned. Our benchmark is an independent implementation of documented equations, not an imported authors' framework.

## 2. Vocabulary and the current model

A **Born machine** defines probabilities through measurement of a parameterized state: \(q_\theta(x)=|\langle x|U(\theta)|0^n\rangle|^2\). A **correlator** here is the mean product of Pauli-Z outcomes, each encoded as +1 or −1. A **classical surrogate** approximates selected quantities without performing the full quantum calculation. An exact statevector running on a classical computer is an oracle/reference; it is not evidence of efficient surrogation at scale.

**Generalization** concerns a target population beyond the training samples. **Sampling hardness** concerns the resources needed to reproduce a distribution. **QML advantage** needs a useful learning task and an explicit resource/accuracy comparison. Neither good training loss nor a hardness conjecture settles all three.

The repository's exact reference implements

\[
U_\theta=H^{\otimes n}\exp\!\left(-i\sum_j\theta_j Z_{G_j}\right)H^{\otimes n},
\qquad Z_{G_j}=\bigotimes_i Z_i^{G_{ji}}.
\]

Source: `classical/model.py` uses `exp(-1j * signs @ theta)` and a normalized Walsh transform. Older planning identities use a positive exponent; any new compiler must reconcile the **live signed convention** explicitly and test amplitudes, not copy angle signs from prose. Output bit order is MSB-first.

## 3. BU: the useful formalism and its limits

### 3.1 Exact correlator representation

BU Lemmas I.1/I.2, Eqs. (4) and (6), give the Fourier pair. With \(S\subseteq[n]\), define \(\chi_S(x)=(-1)^{\sum_{i\in S}x_i}\). Then

\[
m_S(q)=\sum_x q(x)\chi_S(x),\qquad
q(x)=2^{-n}\sum_{S\subseteq[n]}m_S(q)\chi_S(x),\quad m_\varnothing=1.
\]

Do not confuse these signed moments with the mean product of 0/1 bits in BU's preliminary data-moment notation. For IID signed parity samples, **project derivation** gives \(\operatorname{Var}(\widehat m_S)=(1-m_S^2)/N\). The Bernoulli variance formula applies to a 0/1 indicator, not directly to signed parity.

BU Definitions I.1/I.2, Eqs. (10)–(11), retain low-order or selected correlators. The empty set preserves total mass, but omitted terms can make individual reconstructed entries negative. Report negative mass \(\nu=\sum_x\max(0,-\widetilde q(x))\). Never sample from this signed vector or evaluate ordinary forward KL on it. A clipped/renormalized or projected version is a **different model**, with its correction cost and bias reported.

**Project derivation**, using Walsh orthogonality, gives a useful exact small-n test:

\[
\sum_x[p(x)-q(x)]^2=2^{-n}\sum_S[m_S(p)-m_S(q)]^2.
\]

This permits order-resolved residuals without claiming every high-order moment is useful. If evaluation is weighted by the target rather than uniform counting measure, the diagonal Parseval identity alone is not the corresponding risk formula.

### 3.2 What the theorems authorize

BU Definition II.1 and Theorem II.1 concern RFC excess risk, using efficient frequency sampling, a polynomial concentration condition written \((c_{C\ell})_{\max}^{-1}\in O(\mathrm{poly}(n))\), and alignment with absolute coefficients of an optimally trained quantum model. Here the frequency-sampling distribution is not the signed correlator vector. Missing one sufficient condition does **not** prove classical impossibility. Computing aligned frequencies from all \(2^n\) exact coefficients is an oracle diagnostic whose exponential cost must be charged.

BU Theorem II.2, Eq. (32), bounds a risk difference using two coefficient distances through an optimal quantum reference. It distinguishes restricted/surrogate representation from parameter-transfer effects. A local optimizer's best checkpoint is not a certified global \(\theta_Q^*\). In this project, measure same-parameter surrogate errors and empirical optimization gaps directly; label best-found exact training as an oracle baseline, not a theorem instantiation.

For a fully explicit finite-vector substitute, let \(R_\mu(f)=\sum_x\mu(x)[p^*(x)-f(x)]^2\), with normalized declared weights \(\mu\). The **project-derived**, directly checkable bound is

\[
|R_\mu(f)-R_\mu(g)|\leq
\|f-g\|_\mu\bigl(\|f-p^*\|_\mu+\|g-p^*\|_\mu\bigr).
\]

Use \(\mu=2^{-n}\) for the initial benchmark, and retain the distinction from the unnormalized squared Euclidean loss. This bound needs no inaccessible optimum and is not a hardness test.

### 3.3 Source issues to preserve, not silently copy

- The sentence after BU Eq. (27) gives a delta-kernel normalization inconsistent with directly summing its displayed full-support kernel: \(2^{-n}\sum_S\chi_S(x)\chi_S(y)=\delta_{xy}\). Use the displayed sum and independent fixtures; record any divergence from a future reference implementation.
- BU §I B explicitly permits negative pseudo-probabilities; the wording at the start of §V A about positive domains is inconsistent with this restriction. Use quadratic algebraic losses for signed vectors; ordinary KL and generative sampling require valid probabilities.
- Theorem II.1's frequency conditions and optimal-reference availability need mathematical review before being promoted to a project “dequantization certificate.” Do not replace the stated maximum condition with an unproved bound on every coefficient or infer a converse.

These are normalization/interpretation cautions, not a claim that the paper's overall framework is invalid.

## 4. GEN: challenge generalization, not just optimization

GEN Eqs. (6)–(7) express Gaussian-Hamming MMD as

\[
k_\sigma(x,y)=e^{-d_H(x,y)/(2\sigma^2)},\quad
\mathrm{MMD}^2=\sum_S w_\sigma(S)[m_S(p)-m_S(q)]^2,
\]
\[
w_\sigma(S)=a^{|S|}(1-a)^{n-|S|},\qquad
a=\frac{1-e^{-1/(2\sigma^2)}}2.
\]

The code's `gaussian_hamming_spectrum` equals these weights; `gaussian_spectral_weights` returns only relative order weights and must not silently replace the normalized spectrum. Mixtures combine normalized spectra with their registered mixture weights. Spatial kernels generally require the full Walsh-transformed matrix, including off-diagonal terms.

GEN Theorem 1: for a moment loss of capacity \(d\), if \(d+1<|S|\) and the target has full support on finite valid set \(S\), an exact sparse minimizing distribution exists on at most \(d+1\) points. Corollary 1 improves the count when the constant function is included. This is an existence result over distributions: it does not prove that our IQP ansatz realizes that distribution or its optimizer finds it.

The paper explicitly excludes **full characteristic population MMD** from this exact sparse-minimizer conclusion. Full population MMD has the target as its unique zero-loss distribution. However, empirical MMD is minimized by the empirical training distribution, and finite stochastic estimates add another uncertainty. Distinguish \(p^*\), the empirical training measure, and minibatch estimates throughout.

GEN Definitions 2–3 and Eqs. (8)–(10) supply the audit metrics. Let \(T\) be unique training strings, \(S\) the externally specified valid set, and \(U=S\setminus T\neq\varnothing\). For independent model outputs \(Y_1,\ldots,Y_Q\):

\[
F=q(S),\quad \widehat C_Q=\frac{|\{Y_1,\ldots,Y_Q\}\cap U|}{|U|},\quad
\mathbb E\widehat C_Q=\frac1{|U|}\sum_{x\in U}[1-(1-q(x))^Q].
\]

Also report forward \(D_{KL}(p^*\|q)\), with infinity for support mismatch when exact probabilities are available. \(F\) is validity, **not quantum state fidelity**. High coverage alone is not weighted population accuracy. Zero observed samples do not prove a model probability is zero.

GEN §V uses free sampling, retaining invalid outcomes. Its normalization \(C^*=1-(1-1/|U|)^Q\) describes an oracle uniform sampler restricted to unseen valid strings. A uniform sampler over all \(S\) instead has expected unseen coverage \(1-(1-1/|S|)^Q\). Label both denominators if reported; do not confuse this oracle with an attainable fair training baseline.

For rings, the old `p > 1e-6` support metric is empirical histogram support, not the unknown continuous population's validity rule. Keep it for historical comparison; define a new generator-based or geometrically specified validity rule before making unseen-valid claims.

## 5. BS: anti-concentration under the correct ensemble

Photon-counted boson sampling has discrete Fock occupation outcomes \(s=(s_1,\ldots,s_m)\), \(\sum_i s_i=r\). The interferometer parameters are continuous. This is different from homodyne/heterodyne continuous-variable readout. Our rail-encoded qubits and boson sampling both use photons, but their ensembles and accepted outcome spaces differ.

Write \(r\) for photon count here, reserving \(n\) for logical qubits. BS uses \(n\) for photons. The full fixed-photon dimension is \(D=\binom{m+r-1}{r}\). For Haar-random \(U\in U(m)\), collision-free input, indistinguishable photons, and the full Fock output space, BS Eqs. (26)–(28) define

\[
P_2(m,r)=D\,\mathbb E_U\sum_s p_U(s)^2,
\qquad
\Pr_{U,s\mathrm{\ uniform}}[p_U(s)\geq\alpha/D]\geq\frac{(1-\alpha)^2}{P_2(m,r)},\quad0<\alpha<1.
\]

BS Theorem 2: dilute \(m=c r^\beta\), \(\beta\geq2\), has linear-in-\(r\) scaling; intermediate \(1\leq\beta<2\) has \(P_2=m/r+1+o(1)\). Constant \(m/r=c\) gives a constant anti-concentration bound; intermediate growing ratios give only a polynomially declining bound. These are asymptotic statements, not finite-n acceptance thresholds.

The paragraph after Corollary 2 prints a positive exponent for the declining probability. Eq. (46) instead gives \(\Omega(r^{1-\beta})\), which is the scaling used here. Verify theorem transcription against the rendered page rather than copying OCR text.

The finite-n reference can use BS Eq. (45):

\[
P_2(m,r)=(r+m-1)\int_0^{\pi/2}\cos^{r+m-2}(t)\sin((r+1)t)\,dt.
\]

Compare numerical quadrature with direct small-system Haar simulations and, if needed, the hypergeometric expression in Eq. (40). Large oscillatory integrals need precision/convergence checks; Eq. (41)'s parameter labels must be reconciled before implementing that alternate route.

**Two different collisions:** \(\sum_s p(s)^2\) is the probability that two independent runs produce the same entire output. Photon bunching is an occupation event within one run, such as \(\max_i s_i\geq2\). Measure them separately.

**Transfer boundary:** trained structured IQP interferometers are not Haar samples. Logical post-selection changes the measure. Loss makes a mixture of surviving photon sectors; distinguishability and injection change the model. Even if rail/ancilla mode count grows linearly, these differences prevent directly importing the theorem. Fixed-photon uniform loss conditioned on all photons surviving leaves the conditional distribution unchanged, while reducing throughput; that does not move that accepted ensemble to another photon-density regime.

For actual project circuits, report empirical \(D_A\sum_{x\in A}q(x\mid A)^2\), the declared accepted space \(A\), its mass, and training/parameter ensemble. Call this a **concentration diagnostic**, not proof of hardness. Uniform independent bits give the minimum collision diagnostic while remaining trivial to sample: anti-concentration alone cannot certify quantum advantage.

## 6. MBQC, state injection, and Kashefi's work

MC supplies the graph-state measurement and correction language; FLOW supplies causal determinism conditions. SI supplies an alternative instrument: detect photons and condition the reinjected Fock state on that outcome, with fixed optical unitaries. PQCNN gives an experimental classification setting. These support investigating adaptivity, but **classification performance, probability-estimation complexity, generative sampling, and blind verification are different tasks**.

No speedup from SI or PQCNN is transferred to the present QCBM. Any such claim requires the exact input access, approximation error, success probability, resource scaling, and classical comparison of the relevant theorem. The [MBQC plan](v4-mbqc-adaptivity-plan.md) makes those prerequisites explicit and does not add UBQC/VUBQC claims merely because graph states and feed-forward are used.

## 7. Audit reconciliation with the study vault (2026-09-24)

- **IQP/MBQC:** Fujii–Morimae, [Definition 4, Remark 3 and Eq. (1)](https://arxiv.org/pdf/1311.2128), explicitly construct non-adaptive MBIQP and output relabeling. This replaces the earlier generic J/CZ-first proposal. The scoped vault search did not locate this construction; that is not a claim that the owner has not studied it. The MBQC plan provides the negative-phase convention derivation and implementation tests.
- **Born Ultimatum:** `measurement-based-quantum-computing/quantum-circuits/09 - Dequantization and Dequantization Conditions.md` correctly lists efficient frequency sampling and inverse maximum Fourier weight polynomial in n, and later warns against a converse. Its “exactly when” wording should instead be read as sufficient conditions. Its prose about avoiding a sharply peaked spectrum reverses the maximum-weight condition: a point mass has c_max=1 and satisfies that condition; a uniform distribution on 2^n frequencies has inverse c_max=2^n and does not. Neither example alone settles the other hypotheses. Theorem II.2 compares classical-surrogate and quantum-deployment risks at the classically learned parameter; an ideal optimum in the bound must not replace that left-hand-side comparison. Resolve these wording differences before R2; no vault files were edited.
- **Boson sampling:** `papers/2604.14323-boson-sampling-beyond-dilute-regime/02 - Technical Details.md` agrees with this crosswalk: Haar interferometers, collision-free Fock input, full fixed-photon output space, and qualified asymptotic regimes. No ensemble disagreement was found in that note. Trained, lossy, post-selected IQP remains outside direct theorem transfer.

These paths are relative to the supplied `C:/Users/cuqui/quantum-information-material` vault. This is a targeted second-reading comparison, not a request to repeat existing study notes. The withdrawn audit finding about delegating understanding is not reinstated.
