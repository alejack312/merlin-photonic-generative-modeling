# Benchmark specification: correlators, generalization, and delivered cost

Date: 2026-09-24. **Proposed registration; no runs executed.** Sources and applicability qualifications are in the [crosswalk](v4-literature-crosswalk.md). Execution dependencies and owner decisions are in the [roadmap](../.planning/v4-full-completion-roadmap.md).

## 1. Questions and claim levels

The independent case study measures the relationship between **unlearned correlations, deployment errors, unseen-valid sample generation, and physical cost**. It extends the existing ring/sibling study without presenting a collection of borrowed experiments as a demonstrated new scientific result. Originality of the combination is a project proposal, not an established literature-priority claim.

| Question | Evidence that answers it | Evidence that does not answer it |
|---|---|---|
| Does compilation preserve the model? | Independent same-parameter distribution and absolute acceptance checks | A better loss after retraining |
| Can a classical surrogate match the model? | Accuracy/resources versus surrogate capacity, including actual sampling cost | Exponential exact evaluation alone |
| Does the model generalize? | Frozen unseen-valid sampling, population metrics where known, memorizer controls | Training MMD alone |
| Does adaptivity help? | Matched adaptive/open-loop/branch-ablation experiments with full costs | MBQC universality or ideal equivalence |
| Is there practical quantum advantage? | Matched useful output quality, end-to-end physical resources, strong classical baselines and uncertainty | Optical simulation time or a conditional-quality improvement with negligible acceptance |

Report separate outcomes: `IMPLEMENTATION_VALIDATED`, `EMPIRICAL_CLASSICAL_MATCH`, `EMPIRICAL_SEPARATION_WITHIN_TESTED_BUDGET`, `PHYSICAL_RESOURCE_ESTIMATE`, and `ADVANTAGE_NOT_ESTABLISHED`. A classical baseline timeout is a censored observation, not a classical lower bound. No numerical combination of these fields is an “advantage certificate.”

### Scope of this registration

This is a **classical comparison and generalization benchmark** at small n, with simulated physical-resource estimates. Exact classical evaluation is feasible in the registered regime; these runs cannot establish computational quantum advantage. Sample-efficiency or held-out quality differences apply only to the named learners, access rules and budgets. A future computational-advantage claim needs a separate scaling protocol, competitive classical algorithms, and measured quantum end-to-end cost; it is not an acceptance criterion here. The filename is retained for existing links.

### GATE-02: classify controls before interpreting them

| Arm | What it checks | Mechanism removed? |
|---|---|---|
| Exact classical evaluation of q(theta), equivalent MBQC | Reproducibility/implementation identity | No |
| Fourier, RFC or TN approximation to the same q(theta) | Approximation accuracy and classical cost | No; approximation is not a physical ablation |
| Fixed uniform/product generator independent of learned theta | No learned-circuit reference | Yes, learned circuit dependence; task difficulty may also change |
| Pair angles zero, other settings controlled | Contribution of the chosen entangling terms | Partial intervention, with changed model capacity |
| M2 outcome-independent policy, correct M1 XOR retained | Contribution of chosen outcome-dependent policy | Yes, that policy; not all quantum mechanisms |

Do not describe same-q agreement as a no-mechanism null. Each causal comparison must state the changed object and remaining confounders. The owner supplies the closed-form null and red-first test before R2/R3/R5/R6 runs, per [CLAUDE.md](../CLAUDE.md).

## 2. Dataset layers and leakage controls

| Dataset | Role | Split and validity contract |
|---|---|---|
| Existing rings | Preserve continuity with v4 | Keep original 400-point, 320/80 split and train-only transform; retain old empirical support metric under its existing name |
| New synthetic rings | Population generalization adaptation | Freeze generator, ring thickness/noise and quantization before training; independent train/validation/test draws; define geometric validity independently of observed bins |
| Cardinality \(S=\{x:|x|=n/2\}\) | Known-support critique challenge | Even n; split unique strings into disjoint training/validation/final evaluation sets; define U as S minus training strings for source-comparable coverage |
| Controlled parity distribution | High-order blind-spot fixture | \(p_\epsilon(x)=2^{-n}[1+\epsilon\chi_{[n]}(x)]\), \(|\epsilon|\leq1\); lower-order moments match uniform; known full target |
| Existing pinned sibling datasets | Faithful reproduction | Preserve source arrays, codec, splits, objectives, estimator bias and configuration; new diagnostics do not rewrite source training |
| Genomics / unavailable source rows | Conditional replication | Exact permitted source input and protocol required; keep BLOCKED if absent; synthetic substitutes are separate adaptations |

A uniform-cardinality oracle is efficiently sampleable by selecting a subset of n/2 positions. The parity fixture is also efficiently sampleable. Both are **validation/generalization challenges, not hardness candidates**. An optional complexity-motivated family requires its own source-backed structural argument and scaling profile; it is not created by renaming either fixture.

Model selection uses validation only. Any final-target/oracle access used for analysis must be labeled and excluded from training and hyperparameter choice. If reproducing GEN exactly, preserve its §V/Appendix C access protocol separately; the new three-way split is an adaptation, not an exact reproduction.

## 3. Ordered experiment matrix

### B0 — Algebra and adversarial metric fixtures

Before training, validate Fourier inversion, Parseval, identity moment, signed parity versus 0/1 moments, normalized Hamming spectral weights, spatial off-diagonal terms, negative truncated vectors, true infinite KL, empty unseen-set handling, and occupancy formulas.

Use the parity fixture to show that matching all orders below n can miss a known high-order difference. Add a small linear-program moment-matching construction for the GEN sparse-minimizer existence result. The n=12, L=2 paper example can be a separate replication; do not require the same support count from a different LP tie-breaker. Success means nonnegative normalized weights and matched constraints with sparse support, not a particular optimizer-selected basis.

### B1 — Frozen-model correlator audit

For existing raw, compiled, and deployed checkpoints, compute complete moment vectors only at exact-feasible n. With identity excluded from summaries, record:

\[
E_\ell=\sum_{|S|=\ell}[m_S(p^*)-m_S(q)]^2,\qquad
e_\ell=E_\ell/\binom n\ell.
\]

Report both total and per-correlator residual: the combinatorial number of moments changes with order. Report kernel-weighted contributions separately. For \(\Omega\) retained moments, quantify omitted energy, negative reconstruction mass, and loss changes at the **same theta**. This distinguishes truncation error from optimization error.

The existing exact implementation does not have a surrogate approximation gap at a fixed theta. Its gap to a compiled/noisy model must not be labeled BU's classical-surrogate error. Adding an actual approximation creates a new arm.

### B2 — Surrogate capacity ladder

Use one frozen IQP generator matrix and the same training data for:

1. Exact full-vector/correlator oracle (small-n reference only).
2. Exact correlators restricted to order L; retain identity. This isolates feature selection, not efficient correlator evaluation.
3. Uniform random subsets of the same number of nonidentity correlators, paired by subset seed. Any nonuniform/reweighted estimator must specify its inclusion probabilities; unbiased sums use the corresponding inverse-inclusion weighting.
4. A tensor-network correlator evaluator with registered bond dimension, truncation tolerance, contraction ordering, and discarded weight.
5. A Pauli-propagation evaluator with registered truncation/cutoff, error diagnostics and parameter convention; BU Eq. (51) is a candidate specialization only after it agrees with exact asymmetric fixtures.

An oracle-aligned selection from exact target/model coefficients is a labeled diagnostic upper bound, not a free efficient preprocessing step. TN/PPS dependencies and licenses are selected at their implementation checkpoint, not assumed installed.

Measure coefficient error at frozen theta before training each approximation. Then compare each learned theta on the exact model and, where supported, independent physical/MBQC references. Record the exact-trained **best found** model without calling it a global optimum.

A low-bond-dimension TN is particularly important for the current single-layer nearest-neighbor chain. Analyze its contraction width and sequential conditional sampler before entertaining hardness. Restricted topology can be much easier than generic IQP; generic hardness arguments cannot be imported solely from the IQP label.

### B3 — Generalization tournament

Minimum classical panel: uniform bits, empirical memorizer, fitted independent Bernoulli, a likelihood-trained autoregressive model, and a tensor-network Born model. Include the known-target oracle only as a marked ceiling. RBM can be a secondary comparator, not the only serious classical baseline. Separate three contests:

- Same frozen model: backend correctness and surrogate approximation.
- Different generators: matched data, tuning budget, delivered sample budget and useful metrics.
- Oracle: exact target/coefficients unavailable to normal learners.

Retain both source-faithful hyperparameter reproductions and a separately labeled equal-budget comparison if source methods used different budgets. Equal parameter counts alone do not equalize compute or inductive bias. Record baseline convergence diagnostics and allow the same validation budget for all trainable families.

For each model publish: training/validation loss; free-sample validity F; unseen valid mass \(q(U)\); unique unseen coverage; duplicate and training-set-hit fractions; order-resolved residuals; exact TVD/KL where feasible; end-to-end time/memory and attempts. For sample-only larger models, do not report an exact full-distribution TVD from a sparse plug-in histogram as though it were a certified distance.

### B4 — Match accepted outputs and source attempts

Let s be total physical acceptance and q the normalized accepted-output distribution. Two panels answer different questions:

- **Fixed Q accepted outputs:** compare conditional quality at Q, recording all attempts and failures needed to obtain them.
- **Fixed B source attempts:** keep failures as outcomes, compare delivered valid unseen outputs without topping up a model that accepts rarely.

Under IID attempts, the project-derived expectations are

\[
\mathbb E[N_{\rm valid,new}]=B\,s\,q(U),\qquad
\mathbb E[\widehat C_B^{\rm attempts}]=|U|^{-1}\sum_{x\in U}[1-(1-sq(x))^B].
\]

Expected attempts for Q accepted outputs are Q/s, but this is not a measured runtime. Cost includes training, tuning, classical preprocessing, circuit/graph preparation, rejected trials, photon supply, switching/feed-forward latency, detector efficiency and any error mitigation. Keep simulator CPU seconds, assumed device latency, and observed hardware time in distinct fields. Classical samplers also pay rejection/conditioning costs if used.

### B5 — Loss, bunching, and second-moment companion panel

Keep an independent **Haar boson-sampling reference** separate from trained IQP. Start with r=2,3 and m=2r, then pilot m=r²; Haar unitaries via complex Gaussian QR with phase correction. Enumerate full Fock outputs including bunching, use collision-free indistinguishable input, and compare averaged P2 against BS Eq. (45). Validate probability normalization and dimension \(\binom{m+r-1}r\). An m=r³ arm is optional and resource-gated.

The IQP panel uses the actual structured ensemble before/after training. Report full optical bunching probability, output-collision second moment, logical accepted mass and conditional concentration as distinct quantities. For noisy experiments retain survivor photon sector weights, detector model and cutoff residuals; do not combine different-dimensional sectors into a single P2 without a defined measure.

Uniform loss/all-photons-retained is the null: accepted shape and conditional second moment are unchanged while acceptance falls. Mode-dependent loss, distinguishability or source mixtures are separate registered perturbations after physical validation. The Haar theorem is a reference test, not a theorem about these perturbations or the adaptive model.

## 4. Proposed pilot sizes, budgets, and uncertainty

These are planning defaults to freeze in a manifest before implementation/runs, not retroactive changes to source protocols:

| Stage | Candidate budget | Escalation rule |
|---|---|---|
| Algebra fixtures | n=2–6; complete vectors | Must pass independent references at absolute probability tolerance 1e-12 |
| Correlator/training pilot | n=4,6,8; L=1,2,n; five distinct initialization seeds | Verify actual distinct initial states; deterministic duplicates count once |
| Sampling panel | Q=1,000 and 20,000; 30 independent sampling streams per frozen model | Interval-calibration gate precedes inference |
| Attempt panel | B=20,000 per model initially | Report zeros honestly; do not secretly increase B for low acceptance |
| Haar reference | 100 independent unitaries per feasible (m,r) cell | Increase ensemble size only under preregistered precision rule |
| MBQC pilot | n=1,2 then 3; branch limit set from compiled measurement count | Never select only favorable measurement branches to fit memory |

Five model seeds are a pilot, not guaranteed statistical power. Paired split/initialization IDs and separate sampling RNGs are required. Bootstrap paired differences **across independent model fits**, retaining within-fit samples together; do not bootstrap duplicate trajectories as independent training. For sample validity/acceptance use binomial intervals under the IID model; for coverage use repeated independent occupancy experiments and calibrate interval coverage against exact known vectors. For MCMC baselines, diagnose autocorrelation/mixing or use genuinely independent draws; nominal Q is not effective sample size.

Freeze primary endpoint, confidence level (proposed 95%), useful effect size, model-selection rule and multiple-comparison handling before the main tournament. Primary practical endpoint proposed for owner review: valid unseen deliveries per resource budget, with coverage and target distance as joint safeguards. No winner if quality/resource tradeoffs remain unresolved. Simultaneous comparisons need multiplicity control or explicitly exploratory labeling.

Existing v4 limits remain: n=10 analytic RSS growth <400 MiB, map build <3 hours, NAT n=8 <20 minutes, and the historical two-day n=4 failure stop rule. The already-green n=4 does not require waiting two days. New large-n jobs require a measured pilot, total cell count, disk estimate and owner-agreed compute cap; no inherited promise to finish an exponential sweep.

## 5. Artifact and rejection contract

Use a new `results/v4_completion/<registration-id>/` namespace and reuse existing checkpoint/provenance conventions. Each manifest records:

- source commit and scoped dirty-tree identity; paper version/hash and source-vs-adapted designation;
- dataset hash, unique split membership, codec, generator matrix/order, raw/effective theta hashes;
- true/empirical/stochastic objective type, kernel convention, surrogate truncation and reconstruction validity;
- backend capability and physical assumptions, conditioning event and represented/discarded mass;
- training seed, subset seed and sample seed separately; initialization hash and unique-fit count;
- timings by stage, process memory, requested/actual shots and attempts, interval method;
- all missing, stopped, failed and unsupported cells, including primary endpoint status.

Reject comparisons with mismatched target/codec, accidental test reuse, unrecorded smoothing, duplicate “replicates,” unknown acceptance, invalid signed sampling vectors or oracle access mislabeled as efficient. Figures must regenerate from these artifacts. A schematic/simulated photonic result must never appear under a hardware-results heading.

## 6. Completion evidence

The benchmark is implemented only when B0 controls pass, B1/B2 discrepancy curves are reproducible, B3 includes valid classical samplers and unseen-data evaluation, B4 charges rejection costs, and B5 clearly separates theorem-compatible and diagnostic ensembles. A report saying “no advantage found in this tested regime” can satisfy every benchmark requirement. An unperformed baseline or unvalidated physical model cannot.
