# v4.0 additive pipelines and sibling reproduction design

> **Documentation reconciliation, 2026-09-10.** Historical design proposal. Later registered decisions, implementation and evidence supersede proposed defaults below. In particular, the selected initialization is parity-based and deterministic duplicates are labeled. Unrun inventory candidates are not completed reproductions. See [the bounded release](v4-bounded-release.md) and [ledger](../.planning/v4-requirement-evidence.md).

**Revision 1, 2026-09-05.** Owner-requested expansion of the [canonical v4 plan](v4-plan-train-classical-deploy-photonic.md), now revision 4. This document is binding for workstream scope, modular interfaces, experiment selection and phase deliverables. The canonical plan retains the physical, compilation and audit safeguards. This is a plan, not implementation or owner-authored scientific interpretation.

## 1. The owner's three deliverables

1. **Rings:** add a classically trained IQP pipeline for the existing two-ring data. Preserve every existing generator, training script, checkpoint and result.
2. **Sibling reproduction:** add an import/reproduction pipeline for experiments in `C:/Users/cuqui/iqp-mmd-barren-plateau`, then deploy supported frozen IQP models through this photonic construction. Inventory both sibling codebases; do not substitute an unrelated chain/Ising experiment.
3. **Matched comparison:** evaluate non-photonic IQP and photonic realizations of the same model using the same Gaussian-on-Hamming objective, data, parameters and estimators. Separate ideal equivalence from compilation, sampling, noise and resource costs.

The old Ising-chain noise sweep becomes a calibration/extension profile, not the definition of v4.0. NAT remains a planned extension with its existing attempt/stop rule; it does not block classical rings or sibling reproduction.

**Recorded interpretation:** “the ring circuit trained classically” means a new IQP model trained on the same two-ring data, following the surrounding IQP/classical-training request. The v1 `QuantumLayer.simple` model is a different, 462-outcome, latent-input photonic ansatz and already trains via classical simulation. The cosine identity is not a proven efficient trainer for that arbitrary ansatz. The old model remains available for contextual evaluation; no silent claim of an identical circuit is made.

## 2. Correct the premise before implementing

Sonnet correctly identified a missing shared training pipeline, but overstated the kernel obstacle and sampling requirement.

- IQP parity expectations admit classical Monte Carlo estimators when the diagonal phase is efficiently evaluable. Training depends on G, theta, data/target moments, kernel and estimator, not theta alone. Efficient estimation does not guarantee convergence or efficient computation of the full distribution.
- Hardware is not necessary for sampling every current instance: the old product/fixed-pair cases and ideal chain are classically tractable; small-n exact sampling is available. Hardware is one deployment backend.
- Every finite kernel matrix has a Walsh representation. Let N=2^n, W[a,x]=(-1)^(a dot x), mu=W p. Then B=W K W^T/N² and MMD²=(mu_p-mu_q)^T B (mu_p-mu_q). A generic spatial kernel has off-diagonal B. The XOR-invariant Hamming Gaussian has diagonal B with efficiently sampled nonnegative weights. “No Walsh decomposition even in principle” is false; efficient diagonal-mixture estimation is the actual distinction.
- A small-n classical IQP distribution/Jacobian can optimize the existing spatial Gaussian MMD directly. No spectral derivation is needed to make that route possible.
- Sibling targets are not universally bitstring-probability dictionaries: `iqp_bp` consumes binary sample arrays; `iqp_mmd` loaders consume CSV/binary datasets. Exact vectors, weighted support and empirical samples must be separate typed representations.

**Verified numerical check during planning:** N=8 spatial Gaussian MMD and its full Walsh form both equal .1638180415093075; max off-diagonal spatial B is .0376273. Hamming B off-diagonal maximum is 1.73e-17. This demonstrates representation, not scalable generic-kernel training.

Primary context: [Recio-Armengol et al., §§4.1–4.3](https://arxiv.org/html/2503.02934v2). Distinguish the expectation identity from the MMD estimator and its bias/variance contract. In particular, squaring a noisy estimated expectation adds variance; do not assume an estimator is unbiased just because its inner estimate is. Faithful reproduction records the source estimator; a corrected estimator is a separately labeled experiment.

## 3. Architecture: shared core, separate experiment definitions

The two new pipelines must share data contracts, model definitions, kernels, trainers, checkpoints, metrics and backend adapters. They differ in experiment profiles and reporting, not duplicated scientific implementations.

| Boundary / proposed module | Responsibility | Real callers |
|---|---|---|
| `classical/targets.py` | Binary samples, exact probabilities, weighted support and target-moment access, each with explicit semantics | rings and sibling |
| `classical/expectation.py`, `gradients.py` | Pure IQP moments/derivatives; no Perceval import | both trainers and parity validation |
| `classical/kernel.py`, `objectives.py` | Hamming Gaussian spectral loss and small-n spatial matrix loss; explicit estimator metadata | both pipelines, benchmark metrics |
| `classical/model.py`, `trainer.py` | G/theta, optimizer state, exact/MC modes and portable checkpoints | both training profiles |
| `experiments/datasets.py`, `rings.py` | Frozen ring coordinates/splits, bit encoding and spatial decoding | ring training and both backend evaluations |
| `experiments/sibling_import.py` | Source inventory, resolved configs, dataset/checkpoint export, compatibility decisions | sibling retraining and checkpoint replay |
| `experiments/spec.py`, `runner.py` | Small validated experiment records, task IDs and resumable dispatch | rings, reproduction, comparison |
| `deploy/compile.py`, existing planned deployment modules | Logical-to-physical compilation, acceptance semantics and capability checks | both pipelines |
| `experiments/compare.py` | Paired metrics, runtime/sample accounting and difference decomposition | ring and sibling reports |

Use small Python dataclasses/protocols and explicit factories; no dynamic plugin discovery, general workflow engine, or subclass hierarchy for hypothetical backends. The interfaces have two immediate callers. Preserve src-layout. Dependency direction is experiment -> classical/deploy; classical math must import neither experiment scripts nor Perceval. NumPy remains the core; source-export commands may run in the sibling's own environment to avoid installing its JAX/PennyLane stack here.

### Minimum contracts

- **DatasetBundle:** schema_version, dataset_id, binary width n, representation kind, train/test (validation if source has it), hashes, provenance, preprocessing/feature order, optional probabilities/weights, optional spatial codec. Validate finite/binary values, shape, normalization, no split leakage, and 0/1 versus +/-1 conversion. Never infer bit order from a filename.
- **IQPSpec:** ordered binary generator rows G of arbitrary supported weight for classical training, theta, convention ID, family provenance. Photonic capabilities may be narrower. Source spin symmetry/repeated layers/bit-flip wrappers must be represented or rejected, not silently flattened.
- **KernelSpec:** `hamming_gaussian` (sigma or explicitly weighted sigma mixture) or `spatial_gaussian` (centers hash and sigma). Objective normalization and estimator mode are mandatory fields. Hamming is exp(-d_H/(2 sigma²)); this is not exp(-d_H²/(2 sigma²)).
- **Checkpoint:** spec/dataset/kernel hashes, theta, step, optimizer moments/state, RNG state or stream coordinates, dtype, library versions, source commit, loss history and checkpoint selection rule. Serialization must use stable NPZ/JSON; do not blindly unpickle foreign objects.
- **BackendResult:** exact distribution or samples or moments (distinct capability), accepted_mass, conditioning, attempts/detected/accepted counts, model assumptions and uncertainty. Missing distributions are not filled with moment estimates masquerading as samples.
- **CompatibilityRecord:** exact_reproduction, adapted_reproduction, reference_only, blocked; reason, source row/config, changed fields, required capability and evidence. Every imported experiment gets one.
- **ExperimentSpec:** workstream, dataset/model/kernel/trainer/backend IDs, full resolved configuration, source and output IDs, budget and acceptance gates. No undocumented default merges.

## 4. Pipeline A — rings trained classically

### Data and mapping

Reuse the existing dataset exactly: make_circles(n_samples=400, random_state=42), train_test_split(test_size=.2, random_state=42), train-derived min/max normalization, float32 compatibility with `generator/data.py`. Persist raw/normalized coordinates, 320/80 split IDs and transform. Regeneration must match the existing loader; do not change make_circles defaults silently. Test data never chooses bandwidth, stopping point, encoding or architecture.

Use the existing 2^n-bin geometry from `trainability/target_grid.py`: rows=2^ceil(n/2), cols=2^floor(n/2), coordinates on [-.1,1.1]², row-major centers, bin index=int(bitstring,2). Implement the dataset-only adapter without pulling torch/Perceval into classical training. Persist the mapping, tie-breaking convention, training and test histograms, and quantization error. Test edge/outside points rather than clip silently.

Decode model bitstrings to their exact cell centers for spatial plots/metrics. Do not add unreported jitter. The mapping is a modeling choice: Hamming neighbours do not universally mean Euclidean neighbours. Preserve this fixed mapping for the primary comparison; Gray-code/locality alternatives require a separate profile and cannot be tuned on test data.

### Two objective profiles, one IQP model

- **rings_spatial_exact:** train the new IQP model classically on spatial Gaussian MMD using exact small-n q and its derivative. This preserves the existing kind of ring objective, not the old 462-bin ansatz.
- **rings_hamming:** train the same G and ring bit encodings with Hamming Gaussian MMD, using exact small-n spectral/vector checks and a separately validated MC route for larger instances. This supplies the requested substrate comparison.
- Both profiles evaluate final output with spatial and Hamming metrics. Do not directly rank unlike raw MMD values as if they share a scale.
- Product_state is a control; chain_1d(n,n-1) is the initial interacting profile because its physical composition is more tractable than arbitrary graph circuits. Additional family support comes through Pipeline B.

**Proposed initial run manifest:** n=4 smoke only; n=6 and 8 main exact-classical runs; n=10 resource pilot/extension. Main: product and full chain, 5 explicit seeds, small_angle std=.1 primary, uniform initialization ablation, Adam lr=.05, 300 updates, checkpoints every 50. Spatial sigma=.1 as a labeled legacy starting point; Hamming sigma=.5*sqrt(n) primary and 1.0 control. Values are proposed implementation defaults to review at the phase checkpoint, not manufactured owner decisions. Data-dependent initialization waits for the existing D3 recipe/replication decision.

Use fixed last-step selection for primary final metrics; retain full trajectories and best-training checkpoint as a separately labeled diagnostic. A bad ring fit is a valid measured result, not permission to tune on the 80 test examples. Any tuning uses a predefined training-only validation split and a new profile.

### Ring evidence and acceptance

1. Training completes using only classical IQP math; an import/call guard proves no Perceval/MerLin/device evaluation occurs inside the training step.
2. Finite-difference loss/gradient checks at n=2..4 and exact spatial/spectral equality checks precede training.
3. Record initial/final training loss, held-out ring metrics, geometry quantization floor and seed outcomes. No promised successful learning before measurement.
4. Frozen theta is evaluated by the qubit reference and supported ideal photonic realization with identical compiled settings; full-Fock small cases establish physical compilation.
5. Report original-v1 results in a separate contextual panel. Its 462 bins/latent ansatz are different. A common-grid re-evaluation must explicitly map old center mass onto the new grid and record transport/latent-sampling error; never compare unmatched native MMDs as substrate effects.

Outputs: `results/v4_tcdp/rings/{profile}/{cell}/`, `scripts/v4_tcdp/train_rings.py`, `docs/v4-rings-study.md`. Existing scripts/output paths are never overwritten.

## 5. Pipeline B — sibling experiments, faithfully identified

### Inventory first; both sibling packages count

The sibling has `src/iqp_bp` **and** `src/iqp_mmd`; its README primarily documents the latter. The former contains the Gaussian spectral functions named in the request. Inventory source configuration, effective runtime defaults, dataset files, trained checkpoints and result summaries together. The top-level data directory is absent in this checkout; that is not proof every dataset is missing. Search configured/resolved paths and artifact metadata before marking unavailable. No automatic network download or publication of dataset records is part of this plan.

**Source snapshot gate, updated after owner-authorized cleanup on 2026-09-05:** the inspected working-tree source and configuration changes were preserved in sibling commit `f6d6ebe87e4ee1de10893c6ea2f0ffa367493336` (parent `4e5bfc43e325029d7cc760bc2c355afa2d6461e4`). Use this source baseline for import. This checkpoint is preservation, not certification of all scientific claims. Local results, datasets and checkpoints are not bundled in that commit: inventory and hash the exact data/checkpoint inputs separately, together with environment versions. Do not modify or discard sibling work during v4 execution.

Export actual source arrays/G/theta/configs with hashes whenever possible. Regenerating “the same kind” of Ising or mixture data is not exact dataset reproduction. Preserve source train/test splits, selected features, sample order, seed-stream labels and preprocessing. Dataset rights/provenance accompany exported artifacts; genomic sample rows are not put in public docs.

### Evidence-backed starting inventory

| Source experiment / artifact | Observed contract | v4 reproduction path |
|---|---|---|
| `configs/experiments/training_smoke.yaml` | iqp_bp, product n=6, Gaussian sigma=4, small_angle .15, source seed 11, SGD .05 x4, 256 samples | First exact end-to-end reproduction, retaining source optimizer (not replacing it with ring Adam defaults) |
| `bandwidth_marginal_sweep.yaml`, `results/bandwidth_marginal_sweep` | 2D lattice n=9, sigma 1/3/9/27, uniform, 512 mixture samples, Adam .03 x20 | Faithful classical rerun + frozen-checkpoint photonic capability evaluation; retain marginal-order diagnostics |
| `ghosh_kim_small_n.yaml`, `results/ac_ghosh_kim` | n=9 lattice, sigma 1/3/9, mixture, exact loss | Reproduce exact loss/gradient/checkpoints and anticoncentration/marginal definitions; photonic graph support is a separate gate |
| `ghosh_kim_large_n_sampled.yaml` | n=20 ER graph, Ising samples, sigma 1/3/9, sampled training and exact-vector pseudo-shots | Preserve estimator/sample provenance; classical reproduction first; no n=20 physical validation claim |
| `scaling_v1.yaml`, `scaling_v2.yaml`, `koshik_raw_repro.yaml` | Gaussian gradient-variance cells, families/product/lattice/ER/complete, sizes extending far beyond deployment budget; some source paths use JAX | Preserve source Gaussian cells and variance estimator; matched small-n analytic/photonic gradient checks; larger cells reference-only until supported |
| `results/final_report`, `scaling_ac_*` | Feature/evidence ledgers, AC/marginal/validation aggregates | Trace figures back to runs and definitions; do not reproduce aggregate numbers without source cell provenance |
| `results/grid5000_bandwidth_sweep_final` | Nine reported runs, real-dataset bandwidth/marginal summaries, checkpoints referenced | Include in inventory and checkpoint replay; resolve exact dataset/features/kernel mixture and package path before assigning reproducibility |
| `results/genomic_iqp_mmd_ac_investigation` | n=16 reduced genomic investigation artifacts | Preserve exact feature subset and dataset hashes; smaller replacement is an adaptation, not the same genomic experiment |
| `configs/hyperparameters.yaml` / iqp_mmd models | Includes 16-qubit blobs max_weight=6; Ising max_weight=4; larger real-data models; sigma lists | Separate legacy-package adapter; do not claim weight-1/2 compiler or single-sigma kernel reproduces these unchanged |

This is the initial inventory, not a claim to have audited every source result. Phase 26 produces an exhaustive machine-readable inventory and explicit row dispositions for all Gaussian-related experiment configurations and reported result families, plus an exclusion table for unrelated Forge/other-kernel work.

### Reproduction levels

- **Checkpoint replay:** same frozen G/theta/data/kernel; recompute source objective and metrics. Distinguishes deployment questions from optimizer drift.
- **Retraining replication:** same resolved source config and seed/estimator semantics; compare initialization, one gradient/update, trajectory and final metrics. If floating/library differences preclude identical parameters, use predeclared numerical/statistical tolerances and report them. No post-hoc threshold widening.
- **Photonic realization:** same frozen model mapped through a proven compiler and accepted-output model. Dense/looping circuits require physical projection/composability validation; a qubit statevector with a “photonic” label is not an independent backend.
- **Adapted small instance:** when size/gate support is infeasible, create a named derivative with exact changed fields. It supplements, never substitutes for, the source row.
- **Blocked/reference-only:** preserve source artifacts and the exact missing capability/data/budget; never mark reproduction PASS.

Gaussian mixtures in iqp_mmd are in scope if needed for the actual Gaussian experiments: add explicit component sigmas/weights and normalization with tests. Laplacian/polynomial and classical RBM/EBM retraining are outside this IQP/Hamming milestone unless separately requested; retained external baseline numbers need provenance.

Classical G can support higher-weight commuting Z strings. Physical weight>2, spin-symmetric wrappers, repeated layers and graph cycles need their own compiler capabilities. A proposed parity-compute/CNOT ladder decomposition is not automatically safe with post-selected optical gates; implement only after independent unitary and post-selection proofs. Do not discard high-weight rows, change topology, or substitute a chain while calling the result faithful.

**Compiler extension subplans:** 27A covers arbitrary labeled weight-1/2 generators and explicitly tests chains, a shared-vertex path, a cycle and disconnected components at small n. 27B investigates weight-3 then weight-4/6 parity-phase decomposition for the actual legacy source profiles; first compare its logical unitary up to global phase on every basis input, then compare full photonic accepted amplitudes and success, including rejected-sector return paths. If post-selected gates cannot be safely composed, record the required heralded/instrument alternative and its resource cost before implementation. 27C evaluates the largest feasible independent physical reference and a justified scalable backend. Passing a logical decomposition alone does not grant physical support. Larger/high-weight source rows stay open until those obligations are met, not merely until an adapter can parse them.

Outputs: `sibling_inventory.json`, `sibling_compatibility.csv`, per-source export manifests and `results/v4_tcdp/sibling/{source_id}/{mode}/`; scripts `inventory_sibling.py`, `import_sibling.py`, `reproduce_sibling.py`; `docs/v4-sibling-reproduction.md`.

## 6. Matched Hamming comparison

“Non-photonic” here means the classical evaluation of the **same IQP quantum model**, not a different classical generative model such as an RBM. Compare:

| Arm | Parameters / purpose |
|---|---|
| Classical trainer moment/vector evaluator | Frozen trained theta; validate objective and estimator |
| Independent ideal qubit reference | Same G/theta; catches convention/implementation errors |
| Ideal photonic realization | Same compiled G/theta; conditioned acceptance plus probability comparison |
| Quantized ideal photonic profile | Explicit compiled theta; rounding isolated |
| Noisy physical/surrogate profile | Same compiled theta and qualified source model; optional until D1 validation |
| Legacy v1 ring generator | Contextual separate-ansatz comparison, never a substrate-equivalence arm |

For supported exact ideal realizations the accepted distribution and Hamming objective should match; the expected result is equivalence, not a photonic learning advantage. Physical success probability, runtime and sampling cost can differ. The same classically trained checkpoint should be deployed, rather than retraining one arm under a different optimizer.

Compare Hamming MMD, target/paired TVD when full vectors exist, labeled order-1/2 and source-requested higher marginals, applicable AC diagnostics, held-out empirical scores where source splits exist, and accepted-sample cost. Apply revision-3 metric fixes. Store exact-population and sample estimates separately; at fixed accepted shots report attempts as well. For cost-normalized comparisons hold source attempts fixed and report variable accepted counts.

For sampled estimators, match target batches, observable masks, sample budgets, bandwidths and RNG coupling where meaningful; sample noise from independent hardware/simulator shots cannot be forced identical. Keep paired seeds in bootstrap/interval calculations; zero deterministic duplicates do not constitute independent observations. Validate MC bias/variance against exact small-n controls and report source estimator fidelity separately from any corrected-method run.

No full-vector metric above backend capability, no extrapolated small-n noise error bar, no unsupported hardness inference from AC, and no direct comparison of unnormalized objectives. Source Gaussian scaling results are historical hypotheses to replicate numerically; interpreting their scientific claims requires the earlier audit gates.

Outputs: `results/v4_tcdp/comparisons/{benchmark_id}/` with arm manifests/vector or sample artifacts, `compare_backends.py`, reproducible figures and `docs/v4-backend-comparison.md`.

## 7. Phase plan, dependencies and stopping rules

Keep agreed Phase 26–32 numbers; broaden subplans instead of inserting conflicting numbers. Each implementation prompt includes the applicable canonical safeguards and this workstream specification. No single prompt should attempt the entire milestone.

| Phase | Files / subplans | Checkable finish criteria |
|---|---|---|
| 26 — Shared contracts, classical core and inventory | 26A targets/spec/checkpoints; 26B objective/gradient/trainer adapters; 26C source inventory/export schema | NumPy-only core imports; weighted target and source sample equivalence; Hamming/spatial/Walsh tests; manifest of all relevant source experiments and dependencies |
| 27 — Ideal photonic compilation and physical validation | compile/backend capabilities; exact-angle single/multi-gate tests; source/projection probes; later map cache | Ideal supported cases match independent qubit reference; unsupported graph/weight/size fails before execution; source/loss caveats recorded; no expensive cache before validity |
| 28 — Additive rings pipeline | rings adapter, both objective profiles, train_rings CLI, isolated results and report | Reproduce original data/splits; classical-only training guard; n=4 smoke and n=6/8 runs or explicit budget failure; frozen-checkpoint ideal comparison where supported |
| 29 — Sibling recreation and owner controls | inventory/import/reproduce CLI, source-specific configs, compatibility/reproduction ledger | training_smoke faithful; bandwidth/AC source replay and retraining evidence; every inventoried row dispositioned; owner supplies interpretation/control answers, agents do mechanics |
| 30 — Matched benchmark and qualified noise extension | compare runner, common metrics, design/schema manifests, plots; optional calibrated source-noise profile | Rings and sibling arms at same model/data/kernel; ideal parity controls pass; sampled/exact and resource comparisons labeled; no unsupported source row silently omitted |
| 31 — NAT extension | chosen optimizer and equal-budget control on selected validated ring/sibling or calibration cells | D2/D3/D1 prerequisites for actual selected profile; same-parameter controls; genuine pair-key updates; original attempted/stopped rules preserved |
| 32 — Synthesis, review and owner explanation | three study reports, tcdp synthesis, mirrors, reviews and actual owner transcript | Every claim links artifacts; preservation and tests pass; unresolved reproduction/deployment recorded; owner reviews interpretations before public prose |

Shared core/inventory can proceed before D1/D2. Ideal deployment requires its own compilation/projection evidence but not a noisy-source decision. D3 blocks unspecified data-dependent profiles, not explicitly configured source-faithful or ring small-angle runs. D1 gates physical noisy claims; D2 gates NAT. This prevents optional noise research from holding up the owner's first two pipelines.

Time each complete training update/run, export, exact evaluator and photonic reference at its largest supported pilot. Freeze per-run and total budgets before scale-out; avoid launching sibling's enormous grids from base defaults. An explicit budget failure is BLOCKED/PARTIAL, not permission to silently reduce n/seeds. Design manifests derive counts across workstreams; the old 1,920-file/15,120-row calibration counts are not universal v4 totals.

## 8. Acceptance tests and reproduction tolerances

Before execution, prepare independent small fixtures for:
- dataset splits and signed bit/spin conversion, empty/invalid arrays, normalized exact/weighted targets, source file hashes;
- Gaussian direct matrix = spectral form and mixture normalization; generic spatial Walsh identity with off-diagonal terms retained;
- expectation/Jacobian and loss-gradient finite differences; source initialization/one-update parity; MC estimator bias/variance audit;
- bit order/sign/angle winding and compiled exact/quantized reference; all declared backend capability failures;
- resume equivalence including Adam/RNG state, incompatible cache rejection and no collision between rings/sibling output IDs;
- initial/identity/no-noise controls, target-fit versus deployment-gap distinction and metric-specific mutations;
- preserved old import/CLI behavior and unchanged historical result hashes.

Exact independent small numerical references inherit canonical 1e-12 probability and fixed map tolerances. Gradient tests set scale-aware absolute/relative tolerances before runs and include nonzero components; a zero-only fixture cannot validate a gradient. Sampled reproduction uses registered repeated-seed uncertainty, not 1e-12 equality. Training-trajectory tolerances are defined from controlled source/backend numerical checks before results are reviewed.

Document-level plan completion is distinct from implementation completion. Implementation requires full pytest plus configured checks; additive CLI smoke runs, both ring profiles, source reproduction ledger and matched comparison artifacts. A ledger that honestly lists blocked large/high-weight rows is required reporting, not proof that those experiments were recreated. Final report must distinguish delivered pipelines, fully reproduced experiments, adaptations and outstanding physical realization.

## 9. Decision record and owner learning checkpoints

- Add new IQP ring path; preserve v1 because it is a different model/output space.
- Share finite-target and kernel/objective boundaries because both pipelines immediately need them; avoid importing a complete sibling dependency stack.
- Preserve source Gaussian mixtures where necessary; a single-sigma replacement would change the experiment.
- Establish ideal paired equivalence before noise/NAT because otherwise modeling/training differences are confounded with the substrate.
- Owner confirms the conceptual ansatz/encoding and can explain why changing the ring bit mapping changes a Hamming objective. Agent prepares code facts and experiments, not owner-authored interpretations.
- Before implementation, owner checkpoint answers cover the two kinds of classical training, finite versus efficient Walsh representations, exact reproduction versus adaptation, and post-selection validity. These answers remain unwritten by the agent.
