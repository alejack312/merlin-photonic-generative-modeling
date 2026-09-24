# MBQC and adaptivity: proposed extension of the case study

Date: 2026-09-24. **Conceptual design proposal; no MBQC code or adaptive experiment exists yet.** This accompanies the [benchmark specification](v4-advantage-benchmark-spec.md). Mathematical source locations and reading limits are in the [crosswalk](v4-literature-crosswalk.md).

## 1. What changes, and what stays comparable

Measurement-based quantum computation (MBQC) prepares an entangled resource state and computes through single-qubit measurements, whose bases can depend on earlier outcomes. A graph state is

\[
|G\rangle=\prod_{(i,j)\in E}CZ_{ij}|+\rangle^{\otimes |V|}.
\]

Current photonic IQP deployment uses optical circuits and final post-selection. It does not yet provide graph-state preparation, an executable measurement dependency graph, or branch corrections. Both approaches can produce discrete bitstrings; the physical resources and failure channels differ.

Two stages answer different questions:

| Stage | Proposed object | Expected ideal result | Scientific role |
|---|---|---|---|
| M1: equivalent MBQC | Compile the frozen IQP model to a measurement pattern | Corrected branch mixture equals the same ideal IQP distribution | Independent implementation and resource comparison |
| M2: adaptive extension | Introduce a separately specified outcome-conditioned model or injection instrument | Distribution may change | Test whether changed expressivity improves generalization at its full cost |

M1 cannot by itself improve the ideal target fit: equal distributions have equal population metrics. It can expose resource or noise tradeoffs. M2 is a new model and needs fresh training/controls; it must not inherit a claim of same-model substrate superiority.

## 2. M1 is a non-adaptive IQP construction

Use the bipartite incidence-graph construction in Fujii and Morimae, [Definition 4, Remark 3 and Eq. (1), pp. 9–10](https://arxiv.org/pdf/1311.2128). It explicitly needs no measurement-angle feed-forward. The following project derivation fixes the signs for our negative-phase convention; it is not a verbatim transcription.

Let the rows of the binary matrix G be generator masks, with M rows and n columns, and write P_j=Z_{G_j}. Prepare n data qubits and M ancillas in |+>, with CZ edges from ancilla j to every data qubit selected by row j. Measure data in X and ancilla j in the fixed orthonormal basis

\[
|b_0(\theta_j)\rangle=\cos\theta_j|0\rangle+i\sin\theta_j|1\rangle,\qquad
|b_1(\theta_j)\rangle=\sin\theta_j|0\rangle-i\cos\theta_j|1\rangle.
\]

The ancilla branch maps acting on data are

\[
K_{j,0}=2^{-1/2}e^{-i\theta_j P_j},\qquad
K_{j,1}=i2^{-1/2}P_j e^{-i\theta_j P_j}.
\]

All generators commute. If s is the M-bit ancilla outcome and y the raw n-bit data outcome, then

\[
p(s,y)=2^{-M}q_\theta(y\oplus G^T s),\qquad x=y\oplus G^T s,
\]

with binary arithmetic and the existing MSB bit convention. Retain every ancilla branch. The XOR is classical output processing; it requires no changes to measurement bases and no post-selection on s=0. Measurements may occur simultaneously in the ideal model.

Thus corrected M1 and IQP distributions are equal by construction. A numerical equality check validates signs, ordering, branch accounting and implementation; it is not new physics, improved fit, or an adaptivity benefit. This sampling construction needs no generic J/CZ compiler or ordinary-flow validator. Generic teleportation and adaptive J chains remain optional teaching/implementation material for a separately chosen M2 architecture.

## 3. Minimal implementation and acceptance

Proposed additive modules, after the owner's conceptual checkpoint:

- `src/merlin_iqp/mbqc/pattern.py`: bipartite graph, fixed bases, ordered generator masks, output XOR map.
- `src/merlin_iqp/mbqc/compile.py`: frozen IQP parameters to the incidence graph, preserving raw/effective theta labels.
- `src/merlin_iqp/mbqc/reference.py`: independent exact graph-state projection and all-branch probabilities.
- `src/merlin_iqp/mbqc/resources.py`: preparation costs, graph size, measurements and physical assumptions.
- `tests/mbqc/`: branch identities, normalization, asymmetric angles, bit ordering and corrupted output-map controls.

Acceptance:

1. n=1–3 fixtures with zero, Clifford, non-Clifford and asymmetric angles; enumerate within a registered graph-size cap.
2. All-branch probabilities sum to one and satisfy the displayed joint-probability identity within 1e-12; corrected output TVD versus independent IQP evaluation is at most 1e-12.
3. Deliberately corrupt a nontrivial output XOR on a fixture where this changes the distribution. The assertion must fail before restoring the correct implementation. Include zero/symmetric cases where a corruption may be invisible.
4. Compare a frozen trained checkpoint if its total graph size is feasible. A toy graph does not close a ring comparison.
5. Report n+M graph qubits, sum_j |G_j| edges, fixed measurement bases, and zero ideal basis-feedback rounds. Physical scheduling/preparation can still require time and heralding.

Exact enumeration scales with total graph size, not just logical n. Stopped runs remain stopped. A sampled branch approximation is labeled with uncertainty. No free graph preparation or discarded branch mass is allowed. For lossy realization, represent accepted and failure outcomes separately; only the complete instrument can be trace preserving.

Before any M1 benchmark, the owner records the expected equality/null and its test under the roadmap's null-result gate. This derivation is supporting material, not an owner-authored sign-off.

## 4. Physical qualification: a graph is not free

M1 first establishes logical simulation. Physical deployment additionally needs a resource-state preparation proposal (including heralding/fusion), encoding, number-resolving or other specified measurements, optical switching, storage/delay, detector errors and calibrated loss. Do not implement “prepare graph state” as a free hardware operation or reuse post-selected CP gate success as if it guaranteed an offline usable cluster state.

Report photons consumed per trial and successful preparation, temporal/spatial modes, measurement count, non-Pauli measurement count, adaptive round depth, source/detector rates, delays and losses. With preparation time t_prep and R sequential feed-forward rounds, a basic **model-derived** time budget includes

\[
t_{\rm trial}=t_{\rm prep}+\sum_{j=1}^{R}(t_{{\rm measure},j}+t_{{\rm control},j}+t_{{\rm switch},j})+t_{\rm readout}.
\]

Parallel schedules and pipelining require an explicit model. A storage survival factor such as \(e^{-\gamma t}\) is an assumption to calibrate, not an experimental value. Treat physical preparation and logical execution success separately and avoid double-counting losses. Use the benchmark's fixed-attempt panel to expose low throughput.

## 5. M2: adaptivity experiments and alternatives

The owner chooses the first conceptual extension after M1. The question is what outcome dependence adds beyond the fixed non-adaptive IQP reference. A dependent basis defines a changed architecture, but does not by itself prove a distribution outside all IQP models or a harder sampling task. These alternatives are not interchangeable:

| Route | Change | Useful hypothesis | Main cost/limitation |
|---|---|---|---|
| Graph-state adaptive generator | Beyond fixed output relabeling, let a constrained parameterized later basis depend on prior outcomes | Outcome conditioning may alter useful high-order structure | New model; branch complexity, training estimator and causal policy must be specified |
| Photonic state injection | Detect occupations then reinject an outcome-dependent Fock state between fixed optical layers | Measurement/repreparation may extend reachable states beyond passive optics | Photon preparation/detection costs; not automatically a graph-state MBQC compilation |

For the graph route, start with **one measured ancilla and one outcome-conditioned angle** in a small otherwise frozen circuit. Compare (a) learned outcome dependence, (b) angle independent of outcome, (c) outcome labels shuffled independently of the quantum state, and (d) a classical mixture matched to branch weights. Match tunable parameter counts where possible and report discrepancies. Preserve required M1 correction logic in all valid arms; disabling correctness corrections is an engineering negative control, not a fair competing learner.

For SI, the primary paper defines a number-preserving choice of injection functions with \(\sum_i f_i(\mathbf r)=\sum_i r_i\). Start with the paper's same-mode count-and-reinject instrument as a separately labeled physical model. Describe each branch by its measurement/repreparation map; sum over outcomes. Any later choice with a changed photon number gets new sector/resource accounting.

Both routes admit the general form

\[
q_{\theta,\phi}(x)=\sum_s\operatorname{Tr}\!\left[\Pi_x\mathcal E_{s,\theta,\phi}(\rho)\right],
\]

with normalized total mass for the complete ideal instrument. The controller may use only earlier measured outcomes. An adaptive instrument remains linear in the input density operator when outcomes are averaged; “measurement-driven nonlinearity” does not mean a nonlinear quantum channel. Normalized conditional branches can be nonlinear functions of the input, which is a different statement.

Train small models by exact branch summation first, then compare to a declared sampled estimator. Optimize on training/validation only, keep the same tuning budget, and evaluate the GEN metrics plus correlator residuals and physical cost. No outcome-dependent oracle target access is allowed.

### M2 acceptance and falsification

- Valid adaptive branch semantics and complete mass; no future-outcome dependencies.
- Registered advantage hypothesis and effect size before seeing final-test results.
- Improvement survives equal-budget open-loop/classical controls and uncertainty analysis, or is reported as absent.
- Any correlator gain is checked for relevance to target/generalization, not just larger Jacobian rank or expressivity.
- If resource cost erases the gain, record that as the case-study result. Universality, adaptivity and a non-Clifford angle do not prove an advantage.

## 6. Owner learning and interpretation checkpoints

Before M1 implementation, use the existing vault understanding: the owner explains the incidence graph and why ancilla outcomes require only a final XOR, then sketches one branch. No repeat paper summary is required. Before M2, the owner states which operation changes the model, the matched non-adaptive control, and a result that would refute its usefulness. Existing explanations remain valid for their original scope. The assistant checks the owner's attempt; it does not author the owner's interpretation. Explicit confirmation that the concept is understood can waive the attempt requirement as the project instructions allow.

Optional Gibbs reflection after that choice: What happened? How did it feel? What worked or failed? Why? What did you learn? What will you change next time? These remain questions for the owner, not agent-written answers.

UBQC blindness, trap-based verification, fault tolerance and hardware acquisition are outside this extension's current acceptance scope. They can become later work only with their own trust and resource contracts.
