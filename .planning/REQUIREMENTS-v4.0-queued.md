# Requirements: v4.0 TCDP — queued, revision 4

**Updated 2026-09-05: owner ring, sibling-reproduction and matched Hamming vision integrated. Not activated; no production implementation authorized.** Source: [binding plan](../docs/v4-plan-train-classical-deploy-photonic.md), [audit](../docs/audits/2026-09-05-v4-plan-audit.md). Original revision-2 requirements are preserved in Git.

[Additive pipelines design](../docs/v4-additive-pipelines-design.md) is binding for the new workstreams. D1 (noisy physical/source scope), D2 (NAT representation/optimizer), D3 (unspecified data-dependent initialization/replication) remain owner decisions for their dependent profiles; explicitly configured classical work does not wait for them. The original 34 requirements preserve existing IDs, correct the previous count of 32, and replace invalid contracts rather than declaring them completed. v3.2 requirements remain separate in REQUIREMENTS.md.

## Classical trainer — Phase 26

- [ ] **TRAIN-01**: Vendor/adapt the required NumPy core with complete imports and license/provenance; add shared target/objective/checkpoint contracts and both sibling-package export boundaries. Preserve source Gaussian mixtures when required; finite spatial loss is supported without copying the full dependency stack. Design §§2–3.
- [ ] **TRAIN-02**: Implement chain_1d(n,k) with n singles then k ordered nearest-neighbour pairs and strict validation.
- [ ] **TRAIN-03**: Round-trip general supported pairs using singles then lexicographic pairs; enforce finite values/shapes; preserve sign, bit order and winding in a separate compilation boundary (§3.2).
- [ ] **TRAIN-04**: Independently validate exact target/gradient, finite spatial and Hamming/Walsh objectives, complete optimizer updates and source initialization parity; time entire runs. Data-dependent settings need D3 only when used.

## Gate maps — Phase 27

- [ ] **CHAN-01**: Validate source and detection assumptions before reconstructing bare-gate CP instruments; include absolute zero/nonzero outcomes, fixed-photon and joint source/loss diagnostics (§§1,4). D1 selects scope.
- [ ] **CHAN-02**: Test Choi positivity and E_dagger(I)<=I, Hermiticity preservation and non-diagonal vectorization/Kraus fixtures; ideal gates and held-out preparations pass fixed tolerances.
- [ ] **CHAN-03**: Use integer circular-nearest keys with lifted theta, complete cache metadata and boundary tests; measure representative maximum map cost before precomputation.
- [ ] **CHAN-04**: Define success-weighted Haar fidelity, verify via Kraus/integration checks and report tomography separately; no unsupported equality between different normalizations.

## Deployment — Phase 28

- [ ] **DEPLOY-01**: Compose unnormalized instruments with recorded model success, negative optical phase signs, preserved winding and explicit topology/order restrictions; no embedded 4^n-square matrix; isolated peak RSS growth <400 MiB at n=10.
- [ ] **DEPLOY-02**: Ideal maps match the ideal COMPILED distribution and correct acceptance, including k=0, nonadjacent/asymmetric fixtures, sign/scale/winding mutations and probability validation.
- [ ] **DEPLOY-03**: Run full-Fock n=2,3 source-once controls, bystanders and joint g2/loss cases; compare conditional output AND absolute acceptance with recorded cutoffs. D1 determines supportable deployment model.
- [ ] **DEPLOY-04**: Prove or delimit final-only versus intermediate projection for supported topology; record shared-gate/hidden-label discrepancies across asymmetric angles. Small-n .01/.05 bands are triage, never large-n error bars.
- [ ] **DEPLOY-05**: Report attempts per accepted sample under the actual source/acceptance model; eta^n factor only for its fixed-photon control. Heralded-CZ is a separately qualified resource illustration.
- [ ] **REFRAME-03**: With D1, specify conditional synthetic output erasure or actual small-n non-post-selected Fock output; preserve gate-failure/multiphoton categories and reconcile all mass. No q-only claim of unconditional output.

## Owner controls — Phase 29

- [ ] **NULL-03**: Owner predicts k=0 behavior under the declared source/detector model; answers are not agent-filled.
- [ ] **NULL-04**: Owner predicts same-parameter ideal-map behavior, distinguishing compiled from raw trained reference.
- [ ] **NULL-05**: Owner predicts loss behavior under explicit photon-number assumptions; no universal g2>0 invariance.
- [ ] **NULL-06**: Owner supplies throughput predictions for the separately scoped CP and heralded models.
- [ ] **NULL-07**: Owner records a falsifiable gap hypothesis; scientific agreement/disagreement is data, not permissive xfail masking code errors.
- [ ] **NULL-08**: Owner explains NAT same-parameter equality and equal-budget continuation control; no requirement that extra ideal optimization leaves theta unchanged.
- [ ] **NULL-09**: Pipeline asserts q_dep=q_comp at ideal fixed-photon maps and the corresponding metric/acceptance equalities in every control cell; metric-specific mass-preserving mutations plus separate map/success mutations.

## Sweep — Phase 30

- [ ] **SWEEP-01**: Freeze separate rings, sibling and optional calibration manifests. Source profiles retain their resolved settings. Derive counts across workstreams; calibration 1,920 is not total v4. Record distinct seed runs and data/encoding hashes.
- [ ] **SWEEP-02**: Use isolated rings/sibling/comparison output namespaces, portable checkpoints and complete schemas. Build only validated maps; derive per-profile counts, list incompatible/missing source rows and keep exact/sampled/model-derived artifacts distinct.
- [ ] **SWEEP-03**: Implement plan §5.3 metrics on raw/compiled/deployed vectors; true KL and labeled floor scores, stable occupancy, constant support-validity and informative target TVD/MMD/marginals; independent hand fixtures.
- [ ] **SWEEP-04**: Regenerate matched Hamming and ring spatial comparisons with common model/data/parameters, ideal control, compilation/noise separation and real replication counts. No unmatched loss ranking or extrapolated error bars.
- [ ] **SWEEP-05**: Report delivered pipelines, faithful reproductions, adaptations, unsupported deployments and noise/NAT outcomes separately. The old Ising calibration study cannot substitute for the ring or sibling deliverables.

## Noise-aware training — Phase 31

- [ ] **NAT-01**: D2 selects and validates a discrete/continuous optimizer able to move pair angles; no h=1e-4 gradient through the rounded objective or unapproved interpolation.
- [ ] **NAT-02**: Retain candidate n=4,6,8, k=n-1 and 150 steps with D1/D3 settings; match continued-ideal optimization budget/state/RNG. Report target improvement, fixed-reference distance and acceptance separately. Correct old all-parameter FD arithmetic is 51,750 evaluations before controls; budget chosen algorithm anew.
- [ ] **NAT-03**: Retain 20-minute n=8 / two-day n=4 stop rule; stopped means attempted/stopped with partial data, not verified efficacy.

## Write-up — Phase 32

- [ ] **WRITE-07**: Record actual owner explanation of sign/winding, source versus gate noise, projection and loss assumptions, validation limits, NAT controls and acceptance conditioning before interpretation.
- [ ] **WRITE-08**: Write rings, sibling-reproduction and backend-comparison reports plus tcdp synthesis; artifact-linked values, source fidelity/read depth and physical limits are explicit.
- [ ] **WRITE-09**: Mirror only verified workstream conclusions to README, technical findings and project instructions; preserve legacy pipelines and never conflate distinct ansatz or simulated and hardware results.
- [ ] **REVIEW-02**: Fable/Opus then Codex review assumptions, controls, raw numbers, extrapolations and all audit findings; dispositions require evidence, not status prose.
- [ ] **COMM-02**: Offer Gibbs reflection; owner authors journal/Vincent note. Record draft/hold; sending requires explicit authorization.


## Additive preservation

- [ ] **ADD-01**: Existing generator/trainability/hardness imports, CLIs, checkpoints and historical results remain intact; new pipelines/results have separate IDs and paths. No implicit migration or replacement.

## Shared modular architecture — Phase 26

- [ ] **MOD-01**: Implement DatasetBundle, IQPSpec, KernelSpec, Checkpoint, BackendResult and compatibility records with narrow explicit contracts, finite/binary validation, provenance and no circular classical-to-deploy dependency.
- [ ] **MOD-02**: Both pipelines use the same target moments, objective/gradient, training, checkpoint and metric implementations; dataset adapters/configuration provide variation. No generic plugin framework.
- [ ] **MOD-03**: Exact-vector spatial and exact/MC Hamming Gaussian routes are distinct capabilities; preserve Gaussian mixtures required by source experiments. Test generic full Walsh and diagonal Hamming identities.
- [ ] **MOD-04**: Portable NPZ/JSON checkpoints include optimizer/RNG state and hashes; resume and cache rejection tests; source-environment exports avoid installing its entire stack here.

## Rings — Phase 28

- [ ] **RING-01**: Reproduce the existing 400-point/320–80 two-ring dataset, training-only transform and explicit 2^n grid/bit codec; freeze artifacts and verify against the original loader.
- [ ] **RING-02**: Add rings_spatial_exact and rings_hamming training profiles for a new IQP model; training runs without Perceval/MerLin calls. Preserve source v1 as a different ansatz.
- [ ] **RING-03**: Run proposed smoke/main profiles under registered budgets; report initial/final train and held-out spatial/Hamming metrics, quantization floor, seeds and poor-fit outcomes without test-set tuning.
- [ ] **RING-04**: Deploy frozen ring checkpoints to supported ideal photonic evaluation and matched qubit reference; plot decoded center samples. Old 462-bin comparisons are explicitly contextual or common-grid adapted.

## Sibling reproduction — Phases 26 and 29

- [ ] **REPRO-01**: Inventory both iqp_bp and iqp_mmd configs/results/data/checkpoints, including Gaussian scaling, bandwidth/marginals, AC, grid5000 and genomic artifacts. Every relevant source experiment receives a compatibility disposition.
- [ ] **REPRO-02**: Freeze the inspected dirty sibling worktree, including relevant tracked/untracked source/config files, alongside actual arrays, splits, ordered G/theta, effective configs, environment and hashes. A base commit alone is insufficient. Label substitutes/feature changes as adaptations; no sibling reset/stash/commit, unsafe blind pickle load or automatic public data export.
- [ ] **REPRO-03**: First faithfully reproduce training_smoke (source SGD and sigma retained); add checkpoint replay and retraining comparison for bandwidth_marginal_sweep and ghosh_kim small-n profiles with registered tolerances.
- [ ] **REPRO-04**: Preserve high-weight terms, graph topology, spin symmetry, Gaussian mixtures and source estimator definitions. Unsupported physical size/order/weights are rejected before execution and recorded, never changed silently.
- [ ] **REPRO-05**: For every source row distinguish exact reproduction, adapted reproduction, reference-only and blocked; retain large-n classical evidence and plan capability extensions without claiming unperformed photonic reproduction.

## Matched comparison — Phase 30

- [ ] **COMPARE-01**: Compare classical evaluator, independent ideal qubit reference and supported photonic realization at the same frozen G/theta/data/Hamming kernel. Ideal accepted-output equality is the expected control.
- [ ] **COMPARE-02**: Separate raw-trained, ideal-compiled and noisy-compiled results and targets; report objective, TVD where available, marginals/source AC diagnostics and accepted-sample cost under correct conditioning.
- [ ] **COMPARE-03**: Match estimators and accepted-shot or source-attempt budgets explicitly; preserve source MC bias semantics for faithful replay and label corrected estimator experiments separately; validate uncertainty against exact controls.
- [ ] **COMPARE-04**: Produce artifact-backed ring, sibling and substrate comparison reports; backend capability and failed/missing arms are visible. No simulator-as-independent-photonics label or different-ansatz substrate claim.

## Completion and traceability

52 unique requirements. ADD/MOD/REPRO inventory begin in Phase 26; RING is Phase 28, source replay Phase 29, COMPARE Phase 30. Existing scientific IDs retain their safeguards. The additive design takes precedence for phase/workstream scope; D1 gates noisy claims, D2 NAT, and D3 only unspecified data-dependent profiles. No production implementation is authorized by this plan update. Existing v3.2 requirements remain separate.
