# v4.0 Plan: Train Classically, Deploy Photonically (TCDP)

**Status: revision 4, 2026-09-05 — owner vision integrated; planning complete, implementation not started.** Retains revision 3's safeguards and supersedes revision 2 in commit `3f9cb92`. The original review and disposition remain historical records. See [audit](audits/2026-09-05-v4-plan-audit.md), [probes](audits/2026-09-05-v4-plan-probes.py), and [results](audits/2026-09-05-v4-plan-probe-results.json).

The owner now requests three additive deliverables: a classically trained IQP ring pipeline, a sibling-experiment reproduction pipeline, and matched photonic/non-photonic Hamming-kernel comparisons, sharing extensible modules. The binding [additive pipelines design](v4-additive-pipelines-design.md) specifies data contracts, actual sibling experiments, interfaces, phase tasks and acceptance tests. It takes precedence for workstream scope and sequencing; the physical safeguards below remain binding. No old pipeline is replaced. This turn plans the work, not implements it; owner checkpoint answers remain unwritten.

## 0. Question, scope and owner decisions

First deliver the two new pipelines and their ideal matched comparison. Then extend validated checkpoints to noise and NAT. Across both pipelines measure the ideal trained model, its ideal compiled version, and qualified noisy deployment at the same compiled settings. Separate compilation error, noise, target fit and acceptance cost. The former Ising-chain sweep is a calibration/extension profile, not a substitute for the requested ring and sibling experiments.

This is a **simulated deployment study**, not a hardware experiment, sampling-hardness result or demonstration that a photonic device is necessary. The initial ideal chain and calibration Ising target are classically tractable; sibling families can differ and need explicit capabilities. Held-out dataset evaluation is supported where splits exist, but does not alone establish generalization or quantum advantage. The original 462-output ring generator is not the IQP ansatz; the new pipeline shares its data, not an unsupported claim of identical circuitry. The spatial kernel permits classical finite-vector training and a full Walsh representation; Hamming supplies the efficient diagonal spectral structure. See design §2 for the corrected mathematical premise.

The prior literature search is background, not proof of novelty. Record search strings, dates, versions, included papers and exact relevant sections before claiming a contribution. State what the reviewed work does and what this experiment adds; avoid universal absence claims.

| ID | Owner decision | What the evidence rules out | Required record before dependent work |
|---|---|---|---|
| D1 | A validated fixed-photon, g2=0 map study with small-n source diagnostics, or a larger source/number-sector model supporting g2 jointly with loss | Applying an imperfect source once per gate and using eta^n post hoc at g2>0 | Source/detector model, retained axes, revised counts, permissible claims. Neither branch is selected here. |
| D2 | NAT with discrete gate keys and continuous single angles, or a validated continuous-angle noise model | Adam finite differences h=1e-4 through roughly .025-wide theta quantization as a useful pair gradient | Algorithm, gradient/neighbor validation, resolution, objective and budget. |
| D3 | Initialization method/scale and what the five seeds vary | Unspecified sibling defaults, or deterministic duplicates treated as independent restarts | Exact target-moment recipe/configuration, stationary-point pilot and replication unit. |

**Must:** both additive pipelines, shared modular contracts, faithful source inventory/reproduction, matched Hamming comparison, validated deployment, informative metrics/controls, NAT attempt with its existing stop rule, scoped erasure artifact and reproducible reports. **Won't:** implement during this planning turn; replace old pipelines/results; add dependencies here; assert unsupported physical equivalence; invent owner answers; publish or send messages automatically. D1 gates noisy physical scope, D2 gates NAT, D3 gates unspecified data-dependent profiles; they do not block explicitly configured classical ring or source-faithful runs.

## 1. Physical and provenance contract

Record repository commit/dirty hashes, sibling commit, Python/NumPy/Perceval/Exqalibur versions, source defaults, backend, detector model and probability cutoffs. The source baseline after owner-authorized cleanup is `f6d6ebe87e4ee1de10893c6ea2f0ffa367493336`; verify it before vendoring and hash local data/checkpoint inputs separately. Earlier 2.3-second reconstruction claims remain provisional until their complete scripts/configuration/results are committed and rerunnable. SLOS is floating-point numerical simulation, not exact arithmetic; small fitting residual is not a universal physical error bound.

**Revision-4 provenance clarification, updated 2026-09-05:** the owner subsequently requested cleanup of both repos. The previously dirty sibling source/configuration snapshot is now committed at the baseline above. Local experiment artifacts remain outside Git; preserve and hash the required inputs under additive design §5 before import. Cleanup does not establish full experiment reproducibility.

Separate source preparation (photon-number mixture, brightness and internal labels attached once per input event), optical gates (acting on those photons), and detection/acceptance (PNR or threshold, ancilla monitoring and output rail occupancy). Default proposed cross-checks use ideal photon-number-resolving detectors and vacuum ancilla acceptance. Threshold-detector hardware papers are context, not validation of that model.

For exactly n input photons, passive optics, uniform loss and acceptance requiring all n photons, loss contributes eta^n and leaves the accepted distribution unchanged. This is a restricted control. At g2>0 extra photons may be lost while still producing accepted n-photon outcomes. The audit's n=2 probe has a conditional TVD shift of .0081128 at g2=.025, eta=.5 and does not obey eta^2 success scaling.

Source noise is not intrinsically gate noise. At eta=1 full detection rejects extra source photons; bystanders also contribute source-acceptance factors. The measured noisy/ideal success ratios are .974519 at n=2 and .962023 at n=3 with one gate. A gate-only map misses the spectator cost. This discrepancy does not imply photon leakage into an unconnected bystander.

## 2. Outputs, imports and caches

Implementation uses `src/merlin_iqp/classical/`, `src/merlin_iqp/deploy/`, new `src/merlin_iqp/experiments/`, `tests/v4_tcdp/`, `scripts/v4_tcdp/`, isolated rings/sibling/comparisons subdirectories of `results/v4_tcdp/`, and the three workstream reports plus `docs/tcdp-study.md`. Modules and command names are specified in additive design §§3–6. Allowed mirrors remain README, technical findings, project instructions and .planning. No new dependency is authorized; source exports can use the sibling's existing environment.

Classical modules: expectation, Gaussian kernel, target moments, loss, gradients, RNG, families, initialization, trainer, adapter, Ising target, and required model/checkpoint support. Deployment modules: gate-map reconstruction, compilation, density matrix, full-Fock reference, throughput, erasure, metrics. Add tests by responsibility; six filenames is not a coverage standard.

`PROVENANCE.md` records original → destination paths, file hashes, license notices, retained symbols and adaptations. Flattened imports need an explicit map: replacing only `iqp_bp.` leaves unresolved subpackages.

Required artifacts: `source_contract.json`, `gate_map_validation.json`, `crosscheck_shared_qubit.json`, `resource_budget.json`, `design_manifest.json`, `schema.json`, trained arrays/trajectories, map caches, exact output vectors, derived CSVs and structured failure records.

Caches are atomic and versioned, keyed by integer angle ID and all source/noise/detector settings, with implementation/source hashes and raw/effective angles. Reject stale caches and duplicate cell IDs. Resume only from matching manifests. Retain all raw acceptance/filter mass; a cache hit is not independent verification.

## 3. Phase 26: classical trainer and compilation

### 3.1 Adapt the trainer explicitly

The sibling Trainer imports IQPModel, save_iqp_checkpoint, RNG constants and derive_seed, absent from revision 2's copy list. Its exact-small-n loss consumes binary samples and Trainer casts data to uint8. It does not accept a probability vector as an exact target.

Add a target-moment boundary used consistently by loss, exact gradients and initialization. Test empirical moments versus weighted vector moments on a nonuniform hand case. Never cast probabilities to integers or substitute samples for a declared exact target. Trace the complete import closure. Test isolated imports without the sibling path and with JAX import forbidden; do not uninstall packages.

Keep Gaussian NumPy paths and required helpers. Exact small-n loss must agree with direct vector-kernel MMD; analytic gradients must agree with finite differences, including nonuniform p and nonzero pairs. Verify a full optimizer update and short trajectory.

`chain_1d(n,k)`: n singles followed by (0,1),...,(k-1,k), 0<=k<=n-1, shape (n+k,n), uint8. Validate binary generators, dimensions, finite theta, no duplicate/zero/high-weight rows and all singles present. General adapters use singles then sorted pairs; chain order is a special case. Round-trip a non-chain (0,2) fixture rather than silently rejecting/discarding it in one direction.

### 3.2 Sign, bit order, winding and quantization

Logical 0 is (1,0), output qubit 0 is the most significant bit. Sibling observable enumeration may be LSB-first: convert explicitly. Symmetric Hamming weights alone cannot detect label reversal.

For the bare CP(alpha)=diag(1,1,1,exp(i alpha)):

`exp(i t Zi Zj) = exp(-i t) exp(i t Zi) exp(i t Zj) CP(4t)`.

On the logical-1 rail **PS(-2t)** implements exp(i t Z) up to global phase. Apply this sign to singles and both pair compensation phases. The audit's revision-2 full-Fock sign circuit has TVD .442651 from the intended model; corrected signs agree to 3.75e-16.

Use integer keys j=0..62 with angles a_j=.1*j and circular-nearest lookup (minimize wrapped angular distance, deterministic ties). This retains 63 keys; the final circular gap is 2*pi-6.2, so bins are not uniform. Reject nonfinite values. Test all keys, negative inputs and both sides of wraps/ties with fixed fixtures.

**Preserve the winding:** choose the lift a_j+2*pi*l closest to 4*t_trained and set t_eff=(a_j+2*pi*l)/4. The CP map uses wrapped a_j; local compensations use lifted t_eff. Setting t_eff=a_j/4 is wrong: exp(i(t+pi/2)ZZ)=i ZZ exp(i t ZZ), which changes local operations, not only global phase. The audit's example changes TVD by .760184.

Persist raw theta/alpha, lifted theta_eff, wrapped angles and integer keys. Test arbitrary-angle exact compilation before quantization, then quantized compilation against the ideal reference at theta_eff. Grid fixtures must lie on the grid; revision 2's pi/12 did not. Uncached arbitrary-alpha map tests are separate.

### 3.3 Calibration target, initialization and timing

The following Ising target belongs to the calibration profile only. Ring data and exact sibling datasets/splits come from additive design §§4–5 and must not be replaced with this target. Preserve source Gaussian mixtures when required; the shared objective boundary also supports finite spatial Gaussian training.

Keep the zero-field open Ising chain: J=default_rng(4001).normal(size=19), prefixes J[:n-1], beta=1, signed s=1-2*x, p proportional to exp(sum J_i s_i s_(i+1)). Cast uint8 bits to signed integers before subtraction. Normalize stably. Independently verify Z=2^n product cosh(J_i), zero one-spin means, adjacent correlations tanh(J_i), prefix and bit-order consistency.

For n=16,20 only, retain 20,000 inverse-CDF samples at seed 4002. Label the empirical-target approximation separately from model/observable Monte Carlo uncertainty. This is fitting a specified target, not held-out generalization.

D3 must specify method and scale. The sibling defaults to parity, scale .1, not its alternative covariance recipe. For this target parity initialization gives zero singles; pair generators preserve bit parity and single-angle loss gradients vanish there. The probe reproduces this stationary subspace. Require a short training diagnostic; do not silently jitter or change initialization.

Exact target + deterministic initialization + exact updates makes all five seeds identical unless another randomness source is declared. Record hashes/n_unique; do not describe duplicates as five independent restarts or bootstrap them as such.

Tests include an asymmetric explicit-amplitude fixture, Walsh/reference n=2..4 comparisons, adapter round trips, sign/scale/winding mutations, exact moments/gradients, RNG and resume. Time an entire update/short run at the largest n, including gradients. A <60-second loss call does not prove the total training budget.

## 4. Phases 27–28: validate physics before scaling

### 4.1 Composition is conditional on an instrument model

An unnormalized CP trace-nonincreasing map represents a specified success instrument on a specified input space. Composing such maps and tracking trace is exact for that instrument model, not automatically for a circuit with final-only post-selection.

In general P U2 P U1 P != P U2 U1 P: rejected sectors can return. The probe gives a repeated-rail counterexample with fresh vacuum ancillas. This does not itself refute a one-pass chain. Prove for the supported ideal fixed-photon chain that retired rails cannot be repopulated, ancillas never re-enter and rejected sectors cannot reach final acceptance. Restrict/reject other topologies/orders unless validated.

Partial distinguishability retains hidden labels across shared gates; a local reset of the environment is an additional approximation. g2 changes number sectors and source preparation, requiring D1. Single-gate reconstruction cannot establish multi-gate source-model validity.

Per-step normalization is possible if each input-dependent success is multiplied and nonlinear conditioning is explicit. The forbidden operation is treating the normalized map as a linear TP channel or losing those factors. Default to unnormalized composition; validated rescaling plus log-success can prevent underflow. Call trace **model success** until physical-reference agreement is established.

### 4.2 Reconstruction, physicality and fidelity

Use the bare catalog gate, correctly prepared 0,1,+,i inputs, X/Y/Z readouts, vacuum ancillas and declared acceptance. Derive matrices from optical unitaries and independently check them against known qubit matrices. Absolute outcomes include global_perf. Retain zero outcomes as well as observed outcomes; record probability thresholds and discarded mass.

Fit row-major superoperator using 16 product preparations x 9 readouts. Record rank 256, conditioning, residual and time. Add held-out complex/asymmetric preparations and readouts. A fit to its own preparation set is not proof that a noisy-source preparation is a linear qubit encoding.

Use unnormalized Choi J=sum_ij |i><j| tensor E(|i><j|), Tr J=Tr E(I). Test Hermiticity and eigenvalues >=-1e-9. Test 0<=E_dagger(I)<=I by eigenvalues, not success on 16 chosen states. Hermiticity preservation is E(Eij)^dagger=E(Eji); off-diagonal units are not themselves Hermitian states. Check vectorization against explicit Kraus action and a non-diagonal known operation. No silent PSD/trace repair.

Ideal exact-alpha maps equal s(alpha) U rho Udagger, s=1/sigma_max(alpha)^4, to 1e-9. Reference probability tolerance remains 1e-12; repeatability 1e-13. Record failures without relaxing tolerances; repeatability is not a physical error bound.

Replace the undefined conditional fidelity with **success-weighted Haar fidelity**:
`F_success=(Tr J + <u|J|u>)/((d+1)*Tr J)`, d=4, u=sum_i |i> tensor U|i>.
This averages fidelity weighted by success, then divides by mean success. It differs from an unweighted average of normalized fidelities for input-dependent success. Test with explicit Kraus overlaps and Haar integration. Perceval tomography is secondary diagnostics with normalization recorded; different averages need not agree within .005. Define empty-gate mean fidelity as 1, not NaN.

### 4.3 Full-Fock/source trust gate

Qubit q uses (2q,2q+1); gate g has fresh ancillas starting 2n+4g. Validate local/global mapping with a nonadjacent pair. Use H prep/readout and negative signs from §3.2. Noise is applied once at source input. For source/loss diagnostics retain photon sectors before conditioning, and reconcile acceptance plus rejection to 1 with named cutoff losses.

Test n=2,3: no gate, single gate with bystander, shared gates; separate V-only, g2-only, loss-only and joint g2/loss. Check both normalized TVD and absolute success. Use asymmetric singles, different pair angles, near-zero and wrap cases. Enumerate fixtures in a manifest. A physically present zero-angle gate and no gate need distinct resource labels.

The .01/.05 TVD bands from revision 2 are **small-n pilot triage only**: <.01 permits discussing a surrogate study; .01–.05 requires model reconsideration; >.05 stops this surrogate proposal. Record absolute/relative success errors separately. Do not extrapolate an n=3 discrepancy to n=10, KL, coverage or fidelity as an error bar without a bound for that size/metric. Show a separate validation panel. Larger-n hardware claims require compositional error analysis or direct validation.

### 4.4 Throughput and erasures

Throughput = independent source attempts per accepted sample. Fixed-n/g2=0 uniform-loss model: 1/(eta^n*p_model_success). General source model: use total acceptance including loss; eta belongs in model/cache/result keys. Do not double-count brightness/routing/gate losses when interpreting end-to-end hardware efficiency.

Heralded-CZ 1/(eta^(n+2k)*(2/27)^k) is a separate ideal-source resource illustration under the validated heralded construction. It does not implement arbitrary trained CP angles and is not a noise-matched alternative.

Revision 2's erasure helper lacks gate-failure mass and cannot represent full non-post-selected output. A synthetic output-erasure channel **conditioned on gate success** may erase every output qubit, including gate participants: for retained set R the mass is eta^|R|*(1-eta)^(n-|R|)*marginal_q(bits_R). Label this conditional/model-derived. Multiplying by gate success and adding a FAILURE category gives a complete coarse instrument only for that stated measurement model; it does not recover failed-gate output patterns.

If M5 requires actual non-post-selected photonic output, obtain small-n full-Fock outcomes including ancilla failures, collisions and multiphoton categories, and reconcile mass before conditioning. {0,1,E} alone is insufficient at g2>0. Resolve scope with D1; a q-only artifact cannot silently complete REFRAME-03.

## 5. Phases 29–30: design, controls and metrics

### 5.1 Candidate grid and counts

**Calibration extension only.** This grid does not define total v4 work or the ring/sibling profiles. Their resolved manifests and source configurations determine independent counts, optimizers and budgets; see additive design §§4–7. No source experiment silently inherits this profile's defaults.

Retain proposed n={4,6,8,10} deployment, {16,20} training-only, k=0..n-1, Gaussian K=exp(-Hamming/(2*sigma^2)), sigma=.5*sqrt(n) primary and 1 control, three initialization labels, five seed IDs, Adam .05, 300 steps, checkpoints every 50. D3 completes initialization. This kernel uses Hamming distance, not its square; test direct K against normalized Walsh weights.

V={1,.99,.95,.93,.84,.70}, g2={0,.007,.025} is provisional pending D1/calibration. Raw HOM visibility .93 is not automatically the source-overlap parameter: official Perceval tomography uses .9438 with g2=.00732. Record raw/corrected meanings and avoid counting multiphoton corrections twice. Use hardware-inspired labels, not “Ascella-grade deployment.” Verify roadmap numbers from a dated primary source before use.

All-k arithmetic: 840 deployable training files plus (16+20)*2*3*5=1080 training-only = **1920**, not 900. A 900-file design needs an explicit single training-only k choice per n, not yet authorized. There are 15,120 deployment rows only for 18 noise points with legitimate post-hoc eta; four jointly modeled eta values give **60,480**. Generate unique IDs from configuration and decisions rather than hard-code an inconsistent count.

63*18=1134 maps is arithmetic, not permission to build an invalid source model. Measure maximum cost across representative alpha/noise conditions. Budget whole training, deployment, NAT, controls, storage and memory. Retain 400 MiB peak RSS growth at n=10 and 3-hour map-build gate; measure in isolated processes. Never allocate an embedded 4^n x 4^n superoperator.

### 5.2 Three distributions and controls

q_raw=q_ideal(theta_trained); q_comp=q_ideal(theta_eff); q_dep=q_model(theta_eff,noise).
Define rounding=TVD(raw,comp), noise=TVD(comp,dep), total=TVD(raw,dep); test triangle bounds, not additive equality.

At the fixed-photon ideal-map control assert **q_dep=q_comp**, noise TVD=0, all comp/dep target metrics equal, gate fidelity=1 and model success equals the appropriate ideal product. Total TVD equals rounding TVD and generally is not zero.

Owner tests remain unfilled: k=0 for a declared source model, same-parameter ideal maps, fixed-number loss, both throughput models, NAT interpretation and gap hypothesis. A hypothesis is a recorded scientific outcome, not xfail(strict=False) swallowing exceptions. Missing data/owner answers must fail the run.

Mutations conserve probability by transferring mass and use an appropriate fixture per metric. Perturbing q cannot change gate fidelity or separately computed success; mutate those separately. Some metrics are invariant to some perturbations; never require every scalar to detect every change. Constant metrics are tested as constants.

### 5.3 Metrics

Use the target representation and splits declared by each ring/sibling profile. The numerical Ising support statement below applies only to the calibration grid; recompute support for every dataset. If only samples/moments are available, use the profile's validated estimator and do not fabricate an exact probability vector or exact TVD.

Validate finite, nonnegative, unit-mass vectors before metrics; any numerical repair needs a fixed policy and recorded raw mass/minimum. p is the exact target; Q=20000 is accepted samples, not source attempts.

- TVD: .5*sum(abs(a-b)); report three contrasts and target TVD as a fit diagnostic.
- MMD²: sum_a w_a(moment_p-moment_q)^2, normalized Gaussian weights. Cross-check direct (p-q)^T K (p-q) and trainer objective.
- Forward KL: true KL is infinite where p>0 and q=0. Floors 1e-12 and 1e-9 may remain as labeled **floored log-ratio scores**, with added floor mass/count reported. Unnormalized flooring is not true KL and can make it negative.
- Expected coverage: over S={x:p(x)>1e-6}, mean(-expm1(Q*log1p(-q(x)))), handle q=1 exactly. Persist |S|/excluded p mass. Occupancy is not held-out generalization.
- Support-validity (old fidelity_pop): sum_S q. **S is the whole space for this grid**; minimum p at n=10 is 1.74358e-6. Hence validity is always 1. Keep it as an annotated control, not an informative fidelity/noise result; do not manufacture variation by changing the target.
- Marginal TVD: mean over all labeled size-1/2 subsets, with bit-order fixtures. Matching low orders does not establish full-distribution agreement.

### 5.4 Artifacts, figures and claims

NPZ vectors/JSON manifests are canonical; CSVs are derived. Freeze schema before production. Include cell/design/model hashes, all axes and units, raw/lifted angles/keys, three TVDs, metrics on raw/comp/dep, support diagnostics, fidelity definition, total acceptance/conditioning, attempts/sample, rounding/source/map diagnostics and status. Validate uniqueness/completeness; missing is never zero.

Keep primary kernel/init figures and other combinations in the appendix. Show seed-level outcomes and n_unique. Re-training across k changes ansatz, learned angles and expressivity; its curve is descriptive, not the causal effect of adding an otherwise identical gate. Noise ablations compare the same trained/compiled cell.

Figures: noise TVD vs k with zero ideal control and separate compilation curve; noise TVD versus sum gate infidelities as a heuristic, not bound; target-fit metrics raw/comp/dep; attempts/sample with qualified heralded illustration. Small-n model checks get a separate panel, not extrapolated error bars.

Retain .02/.1 only as descriptive TVD bands at the prespecified n=10,k=9 cell with all seed values. Remove slogans assigning hardware survival or a distinguishability ceiling; source/compilation/model errors prevent that attribution. A control deviation alone establishes neither novelty nor utility nor causation.

## 6. Phase 31: NAT with an equal-budget control

NAT extends selected validated ring/sibling checkpoints, or the calibration profile if explicitly selected. Freeze the selected dataset/model/kernel/noise settings in its manifest; the n grid below is the retained calibration proposal, not permission to replace a source experiment. Classical pipeline delivery and ideal comparisons do not wait for NAT research.

Retain n={4,6,8}, k=n-1, primary kernel/init, five seed IDs, warm starts, 150 steps and the existing stop rule. D1 supplies validated noise; D2 supplies an algorithm able to move pair angles. h=1e-4 through the quantizer gave zero pair differences for 99.19% of audit draws. “Parameter-shift is invalid for every channel” is also false; applicability depends on parameter dependence and conditioning.

Objective remains noisy target MMD². Improving it need not reduce distance to the original ideal-trained model. Report target changes, distance to that fixed reference, same-parameter noise gap and acceptance cost separately.

Ideal control is same-parameter equality for every tested theta, not unchanged theta after another 150 steps. Compare NAT with equal-budget continued ideal optimization from the same warm start, matching optimizer state, discretization, budget and RNG. At ideal noise, identical algorithms/objectives should follow identical trajectories; both may improve over the original fit. Weight-1-only optimization must be explicitly chosen/labeled.

For all m=n+k=2n-1 parameters, the old finite-difference evaluation counts are 15,23,31 per step at n=4,6,8: **51,750** total over 150 steps/five seeds, excluding control/validation. This corrects arithmetic, not the unsuitable algorithm. Recompute actual cost after D2, including maps/control/metrics.

Stop rule retained: an n=8 run over 20 minutes or two calendar days without green n=4 end-to-end produces **attempted/stopped** with timings and partial data, not PASS efficacy. Fix best/last-iterate selection before running and compare like checkpoints.

## 7. Phase 32: interpretation and review

Owner explains angle/sign/winding, source versus gate noise, composition/loss assumptions, small-n validation limits, NAT control and throughput conditioning before interpretive prose. Record actual answers. Offer Gibbs reflection; owner writes it.

Write tcdp-study from artifacts with PASS/FAIL/INCONCLUSIVE boundaries. Mirror verified conclusions only. Fable/Opus then Codex review physical assumptions, nulls, numbers and extrapolations as well as every prior finding. A disposition row is not validation. Owner writes the Vincent note; sending needs explicit authorization.

## 8. Execution and finish gates

Phase numbers stay **26–32** with revised workstream tasks in additive design §7: shared core/inventory; ideal compilation; rings; sibling recreation/owner controls; matched comparison/noise extension; NAT; synthesis. Data/core and source reproduction can progress before noise decisions. Only noisy comparison waits for D1; NAT waits for D2 and its selected initialization. Phase 27 requires physical validity before expensive maps. Source-faithful settings and explicit ring defaults do not inherit unspecified D3 settings. Phase 31 never executes the broken quantized finite differences.

Before production: import/target/gradient/angle tests, physical/source checks, schema/manifest tests and resource gates pass for the explicitly approved scope. Pilot failure stops dependent claims. No small-n failure becomes a universal error bar.

Run venv/Scripts/python.exe -m pytest -q plus applicable configured Python checks. Validate artifacts/hashes, missing/duplicate IDs, finite values, units and rejection mass. Regenerate figures from canonical data. Missing runs are partial completion. NAT may be attempted/stopped under its rule; physical validation and owner explanations cannot be skipped to close scientific claims.

## 9. Primary sources and read depth

- [Recio-Armengol et al. 2503.02934v2](https://arxiv.org/html/2503.02934v2): training context; inspect exact initialization/model assumptions before comparison.
- [Raj et al. 2608.31117](https://arxiv.org/abs/2608.31117): metric/generalization context; prior full-read claim is historical, not a new full read here. Our known-vector protocol differs.
- [Salavrakos et al. 2405.02277v3](https://arxiv.org/html/2405.02277v3): architecture/experimental sections inspected here; universal-interferometer QCBM and threshold detectors differ from this rail-encoded PNR proposal.
- [Maring et al. 2306.00874](https://arxiv.org/abs/2306.00874): verify raw/corrected visibility and efficiency definitions before calibration; old table alone is insufficient.
- [Xie et al. 2605.11879](https://arxiv.org/abs/2605.11879): abstract checked; no new implementation-level claim here.
- [Perceval source](https://perceval.quandela.net/docs/v1.1/reference/exqalibur/source.html), [v1.2 tomography](https://perceval.quandela.net/docs/v1.2/notebooks/Tomography_walkthrough.html): source-mixture/normalization context. Installed source governs execution; documentation is not proof that input-dependent normalization is TP.
- [Catalog gate reference 2405.01395](https://arxiv.org/abs/2405.01395): full construction comparison remains an implementation prerequisite; the installed unitary is used directly in the independent audit probes.
