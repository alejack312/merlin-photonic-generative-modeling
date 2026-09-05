# A. Null results

Let \(q_0=q_{\text{ideal}}\), and let \(L_0,K_0,C_0,F_0,M_{1,0},M_{2,0}\) denote the corresponding exact-vector metrics against the Ising target.

- **BLOCKER** — **Plan:** “Metric definitions ... `tvd_ideal_deployed`, `mmd2_train_*`, `kl_target_*`, `coverage_*`, `fidelity_*`, `marginal_err_k1/k2`.” **Problem:** The ideal-unitary null is `q_dep = q_0`; therefore TVD = `0`, both MMD values = `L0`, both KL values = `K0`, ideal/deployed coverage = `C0`, ideal/deployed fidelity = `F0`, and marginal errors = `M1,0`/`M2,0`, not generally zero. Only TVD has a named null. **Fix:** Add owner tests for equality of every ideal/deployed metric and explicitly state which metrics are differences versus absolute target scores.

- **MAJOR** — **Plan:** “Fig 1: TVD ... one line per V” and “The sweep is a finding only where it differs from the nulls in 5.2.” **Problem:** The nulls cover `k=0` at arbitrary `V,g2` and noiseless `V=1,g2=0`, but not the plotted `V<1,g2=0` lines. A broken deployment can produce a nonzero line and be treated as a distinguishability finding without an all-ideal control line. **Fix:** Require an explicit ideal-channel control series with TVD zero for every `n,k`, and test the plotted aggregation against it.

- **MAJOR** — **Plan:** “Fig 2: TVD vs `(1 - mean_gate_fidelity) * k`.” **Problem:** The null for an ideal channel is `(x,y)=(0,0)`, but the only related test is an `xfail` hypothesis about scaling. A wrong fidelity aggregation or a nonzero gap at zero infidelity can pass. **Fix:** Add a null fixture asserting `mean_gate_fidelity == 1` and TVD `== 0` for an ideal-channel sweep, including `k>0`.

- **MAJOR** — **Plan:** “Fig 3: coverage and forward-KL, ideal vs deployed.” **Problem:** The null is `coverage_deployed = coverage_ideal` and `KL_deployed = KL_ideal`, even when both absolute values are nonzero. No section 5.2 null covers this comparison. **Fix:** Add exact equality nulls for coverage and KL, plus a test that deliberately perturbs `q_dep` so the comparison can fail.

- **MINOR** — **Plan:** “Fig 4: throughput ... with the heralded-CZ curve from v3.1 overlaid.” **Problem:** `owner_null_throughput` appears to cover CP throughput, but the heralded-CZ overlay has no separately specified null formula or test. **Fix:** Require both exact curves: CP `η^n ∏ σ_max(α_eff)^-4`; heralded CZ `η^(n+2k)(2/27)^k`.

- **BLOCKER** — **Plan:** “Metric: the deployed gap before vs after.” **Problem:** NAT has no null. Under an ideal channel, noise-aware training optimizes the same distribution as ideal training, so it should show no device-induced improvement: TVD before/after should remain zero, while coverage and KL should remain at their ideal-trained values. The plan also does not say which gap metrics are measured, despite requirements naming TVD, coverage, and KL. **Fix:** Add `owner_null_nat_ideal` and define the before/after metrics and expected equality before Phase 31.

# B. Silent-failure paths

- **BLOCKER** — **Plan:** “Renormalise the superoperator to trace-preserving (divide by the trace of the Choi state).” **Problem:** Dividing by one scalar does not make a general map trace-preserving. It can make the maximally mixed input have trace one while basis states or coherences have different traces. Post-selected gates can also have input-dependent success probabilities, so replacing a trace-decreasing map with a normalized linear channel changes the physics. **Fix:** Test `Tr(S vec(ρ)) = Tr(ρ)` for every matrix-unit basis element, and specify whether tomography returns a conditional CPTP channel or a trace-decreasing instrument. Do not call scalar Choi normalization “trace preserving.”

- **MAJOR** — **Plan:** “If Perceval's Pauli ordering is undocumented, determine it empirically from the ideal gate.” **Problem:** A diagonal controlled-phase unitary is too symmetric to uniquely validate all Pauli permutations. A wrong ordering can pass the three ideal diagonal tests and corrupt noisy channels. **Fix:** Calibrate with several non-diagonal known channels or directly compare the extracted channel on all computational and Pauli basis operators. The plan has no such test.

- **MAJOR** — **Plan:** “`test_trace_preserving`: ... applying `superop` to `vec(I/4)` returns trace 1.” **Problem:** This checks only one input, not trace preservation. A channel can pass while changing the trace of other states. **Fix:** Test all 16 matrix units, or at least all four computational projectors plus an independent coherence basis. The current test does not catch the failure.

- **BLOCKER** — **Plan:** “Alpha is rounded to the grid ... before any channel lookup or deployment” versus “alpha must equal `4*th` or raise.” **Problem:** For almost every trained angle, `alpha_rounded != 4*theta_pair`, so a literal executor either raises on the sweep or silently substitutes the rounded angle into the circuit. The latter changes the experiment. **Fix:** Define `theta_eff = alpha_rounded / 4` as the deployed physical parameter, retain the original theta separately, and compare `q_dep(theta_eff)` against `q_ideal(theta_original)`.

- **MAJOR** — **Plan:** “bit order identical to `exact_qubit_iqp_distribution`” and “q0 is the most-significant bit.” **Problem:** The convention test can still pass if the Walsh reconstruction and adapter use the same mistaken flattening. It also does not independently test deployed density-matrix index placement. **Fix:** Add an asymmetric hand-computed fixture, for example nonzero angles on qubits 0 and 2 with pair `(0,2)`, and assert named bitstring probabilities independently of both array flattenings.

- **MAJOR** — **Plan:** “`p_success` ... mean `global_perf` over the four basis inputs.” **Problem:** The product of mean per-gate success probabilities need not equal the success probability of the actual superposition entering a later gate. A literal executor can report a plausible sample cost unrelated to the composed circuit. **Fix:** Test input-independence of gate success, or label the product as an approximation and cross-check composed `p_success` against full Fock for representative circuits.

- **MAJOR** — **Plan:** “coverage and fidelity: Raj et al. definitions with ‘valid’ = strings in the target's support above `1e-6` ... population version.” **Problem:** Raj’s coverage uses unseen valid strings and a sampling budget; this plan has no training set \(T\), no unseen set, and no population formula. An executor may implement support coverage, finite-sample expected coverage, or sample coverage, all passing a superficial test. **Fix:** Specify one formula, including the valid set, unseen set, threshold, and whether `Q=20,000` is used.

- **MAJOR** — **Plan:** “The two-gate shared-qubit case ... assert only that it is `< 0.05`.” **Problem:** It tests one noise point and only `V`, not g2, eta, alpha, or different parameter states. A shared-qubit failure in the actual sweep can remain invisible. **Fix:** Cross-check both V-only and g2-only noise at representative alphas and define whether the approximation error is a bound, an observed point estimate, or a per-sweep error bar.

- **MAJOR** — **Plan:** “each qubit outside `gate_qubits` is erased independently ... any loss on a qubit inside `gate_qubits` ... dropped.” **Problem:** A set of touched qubits cannot represent repeated/shared gates or gate-specific loss events. Conservation `mass + dropped == 1` can pass for a completely wrong erasure distribution. **Fix:** Test exact per-pattern probabilities for `k=0`, one touched qubit, and a shared-qubit two-gate case.

# C. Underspecified steps

- **BLOCKER** — **Plan:** “both values stored” for trained and rounded alpha, while the CSV columns omit both alpha fields. **Problem:** Two executors can produce incompatible CSVs, and the claimed rounding-error analysis cannot be reproduced. **Fix:** Add `alpha_trained`, `alpha_rounded`, and `theta_effective` as mandatory columns.

- **MAJOR** — **Plan:** “one CSV ... with columns ... `eta`” and “the 4 eta values as post-hoc throughput/erasure columns.” **Problem:** This alternates between four eta rows and four eta-specific columns; erasure columns are not listed. **Fix:** Choose either four rows per conditional deployment or explicit `p_success_eta_*`, `erasure_*` columns and specify the row count.

- **MAJOR** — **Plan:** “Table: per-n, per-noise-point summary, mean +- std over seeds.” **Problem:** There are two kernels and three initializations. It is undefined whether aggregation is over seeds only, or also kernel/init. Figures have the same ambiguity. **Fix:** State the grouping and aggregation for every figure and table, including error bars.

- **MAJOR** — **Plan:** “Target ... `J_i ~ N(0,1)` drawn once from `default_rng(4001)`.” **Problem:** It is unclear whether each n uses an independently generated chain or prefixes one common chain, and whether the 20,000 samples affect training or only reporting. **Fix:** State “generate one length-19 vector and use prefixes” or “generate one vector per n,” and state exactly where samples are consumed.

- **MAJOR** — **Plan:** “coverage and fidelity ... Raj et al. definitions.” **Problem:** The population adaptation is not specified, and the plan’s `1e-6` target-support threshold is not the paper’s complete protocol. **Fix:** Write the formulas directly into the plan and name the denominator and sampling budget.

- **MAJOR** — **Plan:** “two-pair variant assembled through `Processor.add(mapping, ...)` following ... mapping pattern.” **Problem:** The global mode map, pair order, ancilla modes, folded corrections, post-selection, and comparison normalization are left to the executor. **Fix:** Include the exact mapping and expected input/output mode layout in the plan.

- **MAJOR** — **Plan:** “Train theta against `q_dep(theta)` ... Adam ...” in Phase 6. **Problem:** No NAT optimizer steps, kernel, initialization, seed policy, stopping criterion per run, or channel-cache behavior for newly encountered rounded alphas is specified. **Fix:** Copy the exact NAT design table into section 6, including steps, five seeds, loss, and tomography/cache policy.

# D. Tolerances and stop rules

- **MAJOR** — **Plan:** “to `1e-12`,” “to `1e-9`,” and “TVD `< 1e-6`.” **Problem:** These are plausible for exact NumPy identities but not justified for tomography, linear inversion, or independent Perceval runs. They are thresholds an executor could reasonably call too tight and widen. **Fix:** Attach each to a measured numerical baseline and specify max-absolute versus norm error. Never use `1e-9` to validate a noisy reconstructed channel without a reproducibility envelope.

- **MAJOR** — **Plan:** “Assert only that [shared-qubit TVD] is `< 0.05` ... if it exceeds `0.01`...” **Problem:** The two thresholds have no scientific or numerical justification and create a large zone where the approximation is accepted but materially affects conclusions. **Fix:** Predefine the interpretation of `<0.01`, `0.01–0.05`, and `>0.05`, or replace them with an owner-approved uncertainty budget.

- **MAJOR** — **Plan:** “q floored at `1e-12`” and target support “above `1e-6`.” **Problem:** Both values can materially change KL and coverage, especially for exact distributions with tiny probabilities. No sensitivity check is required. **Fix:** Add a fixed sensitivity table at nearby thresholds and state which threshold is scientifically intended.

- **MAJOR** — **Plan:** “If the gap ... stays below `0.02` ... if it grows past `0.1`...” **Problem:** These headline cutoffs have no statistical, practical, or aggregation justification and invite cherry-picking across n, seeds, kernels, eta, and noise points. **Fix:** Define the aggregation first and justify the thresholds before seeing results.

- **MINOR** — **Plan:** “round ... to the `0.1` rad grid ... rounding error ... measured once and reported.” **Problem:** There is no pass/fail threshold for acceptable rounding error. A large rounding artifact can therefore remain in the headline result. **Fix:** Set an owner-approved maximum rounding-induced TVD or treat rounding as a separately reported experimental axis.

# E. Literature claims

- **MAJOR** — **Plan:** “Recio-Armengol et al. ... deploy on ideal qubits.” **Problem:** The abstract supports classically trained parameterized IQP models and quantum-hardware deployment, but it does not establish that the reported deployment is an ideal-qubit simulation. That requires the methods and experiment sections. [Recio-Armengol et al. abstract](https://arxiv.org/abs/2503.02934)  
  **Fix:** Cite the exact full-text section or weaken this to “the paper studies qubit IQP deployment and does not study this photonic noise model.”

- **MAJOR** — **Plan:** “Raj ... study the objective on a state-vector simulator.” **Problem:** The abstract supports MMD-based benchmarking, but not the simulator claim. The full text does state that the cardinality task reaches 30 qubits by full state-vector simulation and defines coverage/fidelity/KL. [Raj et al. full text](https://arxiv.org/html/2608.31117)  
  **Fix:** Use the full-text citation and accurately distinguish exact state-vector evaluation from sampled metrics.

- **MAJOR** — **Plan:** “Salavrakos ... train a photonic Born machine on-device with loss mitigation but do not use the classical-training route or IQP structure.” **Problem:** The abstract supports a photonic QCBM, recycling mitigation, simulation, and an integrated-photonic experiment. It does not prove the negative claims about classical training or IQP structure. [Salavrakos et al. abstract](https://arxiv.org/abs/2405.02277)  
  **Fix:** Full-read the circuit and training sections, then cite exact evidence or weaken the sentence.

- **BLOCKER** — **Plan:** “Nobody has put a classically trained IQP model through a photonic noise model.” **Problem:** This is a universal literature claim. None of the cited abstracts can support it, and checking four papers is not evidence that nobody has done it. **Fix:** Say “we did not find such a study in the four works reviewed,” with search scope and date, unless a broader literature review supports the stronger claim.

- **MAJOR** — **Plan:** “Xie ... dual-rail post-selection and trainability.” **Problem:** The abstract does support exact state-vector comparisons involving dual-rail post-selection and trainability. It does not by itself support every implementation-level comparison the write-up may draw. [Xie, Notton, and Senellart abstract](https://arxiv.org/abs/2605.11879)  
  **Fix:** Full-read before claiming matching circuit details, noise assumptions, or conclusions beyond the abstract.

# F. Feasibility

- **BLOCKER** — **Plan:** “63 alphas x 18 ... = 1134 tomographies.” **Problem:** Nearest-neighbor rounding over `[0, 2π)` produces `0.0` through `6.3`, which is 64 grid values unless the plan explicitly wraps or clamps the top bin. If alpha is not first reduced modulo `2π`, trained angles can create still more keys. **Fix:** Specify modulo-`2π`, boundary behavior, and the resulting exact key count.

- **MAJOR** — **Plan:** “4 n-values x k = 0..n-1 x 2 kernels x 3 inits x 5 seeds x 18 channel points, with the 4 eta values...” **Problem:** Deployable circuit cells are `(4+6+8+10)=28` k-values, so `28×2×3×5 = 840` trained cells and `840×18 = 15,120` conditional noise rows. If eta is a CSV row, the total is `60,480`; if eta is post-hoc columns, the listed `eta` column is wrong. **Fix:** State the exact row count and schema.

- **MINOR** — **Plan:** “about 7 single-core hours at the measured 20 s each.” **Problem:** Using the supplied measurements gives `1134×22 s = 6.93 h`, or `1152×22 s = 7.04 h` with 64 bins. The estimate is fine, but timing must use the slowest noise condition, not an ideal-only measurement. **Fix:** Gate on the maximum measured seconds per tomography across all `(V,g2)` conditions.

- **MAJOR** — **Plan:** “`4^10 * 16 B = 16 MB per copy` ... n = 12 ... use ... einsum.” **Problem:** The arithmetic for n=10 is correct: 16 MiB per complex128 density matrix. At n=12 it is 256 MiB per copy, before einsum temporaries, output arrays, and channel intermediates. The plan does not bound those allocations. **Fix:** Specify peak-memory measurement for n=10 and forbid any full `4^n × 4^n` embedded superoperator.

- **MAJOR** — **Plan:** “Gradient by central finite differences ... `h = 1e-4`.” **Problem:** With n parameters, each optimizer step costs `2n+1` deployed-vector evaluations: 9, 13, and 17 at n=4, 6, and 8. At 300 steps and five seeds, that is 58,500 evaluations across the three n values, before any newly needed channel tomography. The plan gives no step count and does not budget tomography for alphas reached during training. **Fix:** Specify the step budget and precompute or budget all new rounded-alpha channel keys.

## Verdict

Phase 26 can start only after the plan’s own contract is repaired. The immediate blockers are the rounded-alpha versus `alpha == 4*theta` contradiction, the invalid scalar “trace-preserving” renormalization, the missing nulls for non-TVD metrics and NAT, and the undefined population coverage/fidelity metrics. Fix those before vendoring begins; otherwise a literal executor can produce a green, reproducible pipeline whose reported deployment gap and sample cost do not mean what the plan claims.

