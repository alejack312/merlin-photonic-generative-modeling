# v4.0 requirement evidence ledger

Updated 2026-09-07 after the milestone-completion verification pass. Statuses are strict:

- `PASS`: the bounded criterion has direct implementation and verification evidence.
- `FAIL`: an attempted acceptance check produced a contrary result.
- `INCONCLUSIVE`: implementation/evidence exists but does not establish the full criterion.
- `NOT IMPLEMENTED`: the required implementation or run does not exist.
- `BLOCKED`: the next action cannot safely proceed until a named owner decision or external input is supplied.

An incomplete row includes the missing item, next concrete action, and owner dependency. A PASS is limited to the stated bounded evidence and never upgrades a dependent scientific claim.

## 2026-09-06 independent audit disposition

| Finding | Status | Evidence | Remaining action | Owner dependency |
|---|---|---|---|---|
| F01 comparison arm labels | PASS | Quantized compiled and deployed arms share effective parameters; the unquantized compiler is an explicit control; eta=1 equality is tested and the n=6 artifact was regenerated. | None for this repair. | None |
| F02 NAT control | PASS | Matched continuation carries pair keys, windings and Adam state; direct-resume trajectory identity is tested and registered n=4/n=6/n=8 reports contain target-improvement, fixed-reference, acceptance, and ablation fields. | None for the bounded ideal/model-derived report. | None |
| F03 sibling smoke data | PASS | Recorded `(256,6)` product-Bernoulli data was regenerated from seed `1230519654`; source SGD retraining matched all five source theta/loss rows exactly in an isolated tree. | Reproduce remaining registered sibling rows; do not generalize this PASS to them. | External inputs only for genuinely absent rows |
| F04 typed ring adapter | PASS | Real `load_rings_dataset(4).bundle()` construction and focused tests pass. | None for this repair. | None |
| F05 ordered local maps | PASS | Adjacent/nonadjacent asymmetric and entangled-input fixtures pass with caller-declared local MSB order. | None for this repair. | None |
| F06 resume learning rate | PASS | Direct resume rejects missing/invalid/changed learning rates; focused test and probe pass. | None for this repair. | None |
| F07 NAT initialization std | PASS | Public `initialization_std=0` reaches config and produces zero small-angle singles; focused test and probe pass. | None for this repair. | None |
| F08 tomography provenance | PASS | Reconstruction remains `analytic-tomography`; Perceval is a separately scoped accepted-mass probe with explicit metadata. | Obtain absolute physical outcomes only if physical tomography is later claimed. | D1/Perceval evidence |
| F09 deployment success reference | PASS | Success is computed from actual compiled pair keys; analytic and physical statuses are separate; corrected manifest passes analytic validation. | Run optional physical validation only within its approved budget. | D1/Perceval evidence |
| F10 source provenance | PASS | Ring/NAT artifacts and sibling exports record observed commit plus scoped tree identity/dirty state; sibling pin mismatch is explicit. | None for provenance capture; historical artifacts remain qualified. | None |
| F11 Choi consistency | PASS | Validator derives Choi from the operative map and rejects inconsistent stored representations; regression fixture passes. | None for this repair. | None |
| F12 infinite KL export | PASS | Infinite KL is serialized as JSON-safe null plus explicit `infinite`/`inf` metadata; support-mismatch export test passes. | None for this repair. | None |
| F13 replay overwrite | PASS | Replay namespace includes source identity, checkpoint hash, config hash and step; incompatible non-empty reuse is rejected and tested. | None for this repair. | None |
| zero-shot coverage | PASS | `sample_count=0` reports coverage `0.0` and non-integer counts are rejected. | None for this repair. | None |

## 2026-09-06 second repair review disposition

| Finding | Status | Evidence | Remaining action | Owner dependency |
|---|---|---|---|---|
| R01 retraining trajectory gate | PASS | Empty, non-finite, missing-step, shape-mismatch and finite-mismatch cases are covered; finite mismatch is `FAIL`, and a valid trajectory remains `PASS`. | None for the repaired gate. | None |
| R02 requested retraining config | PASS | The smoke-only adapter validates the requested path and SHA-256 against the exported manifest before execution; mismatched configs are rejected. | Add other source configs only as separately specified adapters. | None for current smoke scope |
| R03 source retraining provenance | PASS | Git/source identity, module origin, source hashes, environment, before/after state and output isolation are enforced; compatibility shims are scoped and restored. | Run the explicit sibling integration command when source inputs are available. | External sibling checkout for integration |
| R04 ring artifact namespace | PASS | Stable config identity includes initialization, optimizer, learning rate, steps and source/data/generator inputs; atomic writes reject incompatible reuse. | Regenerate canonical artifacts only when a registered profile is intentionally rerun. | None |
| R05 comparison stale artifacts | PASS | Loaded generator, theta, dataset arrays, codec centers and binary/finite contracts are validated against manifest hashes before evaluation; evaluated hashes are recorded. | None for the repaired gate. | None |
| R06 spatial Trainer shorthand | PASS | Spatial string shorthand now requires explicit finite centers; a nontrivial centered target-fit regression passes through the public constructor. | None for the repaired API. | None |
| R07 matched NAT arms | PASS | CLI now writes one frozen warm start and two arms with identical common-start state hashes and equal per-arm budgets; the fixed-pair path remains an ablation. | Interpret efficacy only after the NAT metric panel is artifacted. | None for ideal null |
| R08 full-Fock aggregation | PASS | Aggregate status is computed after the requested full-Fock call and propagates injected `FAIL`/`INCONCLUSIVE` results. | Physical/full-Fock evidence remains limited by the existing capability boundary. | D1/Perceval evidence |
| R09 default-suite portability | PASS | Normal tests no longer require a hard-coded sibling checkout; source retraining is an explicit environment-gated integration test with portable contract tests. | Run optional integration explicitly for source-faithful evidence. | External sibling checkout |

## 2026-09-06 third repair review disposition

| Finding | Status | Evidence | Remaining action | Owner dependency |
|---|---|---|---|---|
| S01 scoped Git source identity | PASS | `_git_status` preserves both porcelain status columns; a first-record ` M src/iqp_bp/model.py` fixture is reported dirty by `git_source_identity`. | None for the repaired boundary. | None |
| S02 raw DatasetBundle identity | PASS | DatasetBundle hashes named full-content split hashes; a mutation at `[100, 2]` changes the bundle hash and does not depend on NumPy display settings. | None for the repaired boundary. | None |
| S03 checkpoint continuation | PASS | Adam resume rejects missing, malformed, non-finite, and step-inconsistent state; Checkpoint rejects non-finite loss histories; training rejects non-finite objective trajectories. | None for the repaired boundary. | None |
| S04 multi-seed ring reuse | PASS | Rewriting an unchanged seed-0 run after adding seed 1 succeeds; mutable replica observations are excluded from immutable run identity. | None for the repaired boundary. | None |
| S05 ring artifact integrity | PASS | Existing-output reuse requires all four promised files and validates every serialized dataset/run array plus summary identity against the requested run. Missing and corrupted artifacts are rejected. | None for the repaired boundary. | None |

## 2026-09-06 fourth repair review disposition

| Finding | Status | Evidence | Remaining action | Owner dependency |
|---|---|---|---|---|
| T01 NAT positional pair binding | PASS | Positional keys and windings are bound to caller pair order before canonical sorting; equivalent sequence and mapping inputs produce the same generator, compiled state and zero-step trajectory. | None for the repaired boundary. | None |
| T02 atomic and physical checkpoint resume | PASS | Resume validates history length, learning rate, complete Adam state, non-negative finite second moments, integral step, and RNG state before assignment; rejected resumes leave a trainer snapshot unchanged. | None for the repaired boundary. | None |
| T03 fail-closed source verification | PASS | NUL-delimited Git status/file listing preserves non-ASCII paths; status, commit and tree observation failures raise instead of certifying clean. | None for the repaired boundary. | None |
| T04 ring summary integrity | PASS | Existing summaries must exactly equal the manifest's initialization, replication, metrics and photonic-evaluation snapshot; altered metrics or fabricated physical PASS are rejected. | None for the repaired boundary. | None |
| T05 sibling replay input validation | PASS | Raw generator, theta, step and source loss are validated before coercion/evaluation; nonbinary, nonfinite and non-integral checkpoint fields are rejected and JSON export disallows NaN. | None for the repaired boundary. | None |
| T06 NAT move-count semantics | PASS | Public `pair_moves` now reports accepted discrete updates; `pairs_changed` reports endpoint key/winding changes. Existing NAT JSON artifacts were corrected without retraining. | None for the repaired reporting contract. | None |

| ID | Status | Evidence / missing implementation or evidence | Next concrete action | Owner dependency |
|---|---|---|---|---|
| TRAIN-01 | PASS | NumPy core, contracts, provenance, and sibling export boundary exist; focused tests pass. | None for bounded scope. | None |
| TRAIN-02 | PASS | `chain_1d` and strict generator validation are tested. | None. | None |
| TRAIN-03 | PASS | Classical round-trip and separate signed/winding deployment compiler tests pass. | None for supported weight 1/2 scope. | None |
| TRAIN-04 | PASS | Exact gradients, spatial/Hamming objectives, optimizer update, initialization forwarding, typed ring targets and strict checkpoint-resume tests pass; the independent repair probes also pass. | None for the explicit ring profiles. | None |
| CHAN-01 | PASS | D1 fixed-photon `g2=0` source-once controls are exercised in [physical_control_manifest.json](../results/v4_tcdp/deploy/physical_control_manifest.json), with zero/nonzero outcomes and explicit absolute acceptance; `g2>0` is outside the selected scope. | None for the selected fixed-photon implementation; do not generalize to multiphoton source claims. | None for selected scope |
| CHAN-02 | PASS | Choi positivity, `E†I <= I`, Hermiticity, non-diagonal reconstruction, held-out fixtures and operative-map/supplied-Choi consistency validation pass. | None for ideal analytic maps. | None |
| CHAN-03 | PASS | Integer circular-nearest keys, lifted winding, cache metadata, boundary tests, and the clean n=4/6/8/10 resource pilot in [resource_budget_final_v6.json](../results/v4_tcdp/deploy/resource_budget_final_v6.json) are verified. | None for the bounded map/resource scope. | None |
| CHAN-04 | PASS | Success-weighted Haar fidelity, Kraus/reference fixtures, and separate tomography provenance are implemented and tested; no physical-tomography claim is made. | None for the declared analytic fidelity scope. | None |
| DEPLOY-01 | PASS | Negative signs, winding, topology restrictions, unnormalized composition, no embedded `4^n` square, n=10 RSS `<400 MiB`, and the approved three-hour timing gate are evidenced by the deployment tests and [resource_budget_final_v6.json](../results/v4_tcdp/deploy/resource_budget_final_v6.json). | None for the bounded compiler/resource scope. | None |
| DEPLOY-02 | PASS | Ideal compiled-map equality, k=0, nonadjacent/asymmetric ordered-local fixtures, sign/scale/winding and probability fixtures pass. | None for implemented ideal weight 1/2 maps. | None |
| DEPLOY-03 | PASS | The dedicated Perceval manifest exercises fixed-photon n=2/3 no-gate, single-gate-with-bystander, and shared-gate controls, with conditional TVD and absolute accepted mass; `g2>0` is outside D1. | None for the selected fixed-photon scope; joint multiphoton/loss remains unsupported. | None for selected scope |
| DEPLOY-04 | PASS | Final-only and intermediate projection are both executed for the shared-gate fixture; the conditional TVD is `0.585411845271861`, so the unsupported intermediate boundary is explicitly delimited and final-only is selected. | Do not extrapolate final-only composition to intermediate projection or hidden-label/full-Fock cases. | None |
| DEPLOY-05 | PASS | [physical_control_manifest.json](../results/v4_tcdp/deploy/physical_control_manifest.json) records model success, source acceptance, `eta**n` absolute mass, and attempts per accepted sample; heralded-CZ remains a separate qualified formula. | None for the selected fixed-photon resource scope. | None |
| REFRAME-03 | PASS | `conditional_erasure_distribution` provides the selected conditional synthetic `{0,1,E}` output plus a `FAILURE` category and mass-conservation test. It is explicitly not an unconditional multiphoton/Fock output. | None for the selected conditional synthetic scope; do not upgrade it to full non-post-selected Fock evidence. | None |
| NULL-03 | BLOCKED | Owner k=0 prediction is absent. | Owner records prediction before the k=0 control is interpreted. | Owner decision |
| NULL-04 | BLOCKED | Owner same-parameter ideal-map prediction is absent. | Owner records raw-versus-compiled prediction before comparison claims. | Owner decision |
| NULL-05 | BLOCKED | Owner loss prediction and photon-number assumptions are absent. | Owner records the prediction after D1 selection. | D1 + owner |
| NULL-06 | BLOCKED | Owner throughput predictions are absent. | Owner records separate CP and heralded-model predictions. | D1 + owner |
| NULL-07 | BLOCKED | Owner falsifiable gap hypothesis is absent. | Owner records the hypothesis and success/failure interpretation rule. | Owner decision |
| NULL-08 | BLOCKED | Owner NAT equality and equal-budget continuation explanation is absent. | Owner records the prediction after D2/D3 selection. | D2 + D3 + owner |
| NULL-09 | PASS | The matched comparison smoke artifacts contain ideal equality, metric-specific mass-preserving distribution mutations, independent map mutations, and acceptance-only mutations, with direct/Walsh/trainer Hamming checks. | None for the bounded control panel. | None |
| SWEEP-01 | PASS | Separate ring, sibling and comparison manifests preserve source settings and distinct seed/budget fields. | None for bounded artifacts. | None |
| SWEEP-02 | PASS | Isolated namespaces, NPZ/JSON artifacts, hashes, compatibility dispositions and stale-cache tests pass. | None for bounded artifacts. | None |
| SWEEP-03 | PASS | The two n=4 matched comparison artifacts include true KL/infinity status, labeled floor scores, coverage, occupancy, support validity, MSB-first marginal panels, TVD/MMD, and mass-preserving controls; direct/Walsh/trainer Hamming agreement is recorded. Source anticoncentration is correctly omitted when no source-AC input exists. | None for the exact-vector bounded panel. | None |
| SWEEP-04 | NOT IMPLEMENTED | Only n=4 ring smoke comparisons exist; no sibling matched arm, sampled uncertainty or noisy comparison exists. | Complete sibling data closure and selected physical model, then run paired profiles within budget. | D1; D3 for replication |
| SWEEP-05 | PASS | Reports distinguish delivered, adapted, reference-only, blocked and unperformed work. | None. | None |
| NAT-01 | PASS | D2 selects bounded discrete alpha-key neighbor search with continuous single-angle updates; focused tests prove pair-key movement, catalog membership, winding preservation and reproducibility. | Validate on the registered ring/cell profile before interpreting efficacy. | None |
| NAT-02 | PASS | Registered n=4 seeds 0–4 and n=6/n=8 seed-0 runs contain two matched 150-step continuations from one frozen warm start with identical optimizer state/budget, target improvement, fixed-reference TVD, acceptance, and explicit fixed-pair ablation fields. | Interpret efficacy only as ideal/model-derived continuation evidence; no noisy superiority claim. | None |
| NAT-03 | INCONCLUSIVE | The registered n=8 run completed under the 20-minute bound, but the two-day n=4 arm was not executed; the retained stop rule is therefore only partially exercised. | Run the n=4 two-day stop-rule attempt only if that approved budget is explicitly retained; otherwise record this scope limitation. | None for implementation; owner/budget authorization if the two-day run is desired |
| WRITE-07 | BLOCKED | Owner explanation of signs, source/gate noise, projection, loss, NAT and conditioning is absent. | Owner writes the explanation before interpretive synthesis. | Owner decision |
| WRITE-08 | PASS | Rings, sibling, deployment, backend-comparison and v4 synthesis reports link canonical artifacts and limits. | None for current evidence. | None |
| WRITE-09 | PASS | README and `docs/technical-findings.md` now mirror only the verified, scope-qualified v4 implementation and evidence, link the canonical report/ledger, and state the remaining scientific and owner-gated boundaries. | None for the documentation mirror. | None |
| REVIEW-02 | PASS | Independent post-integration recheck at `3e1ae33`, cleanup recheck at `dd348e9`, final disposition reconciliation at `53b541f`, and a content-only final-docs recheck verified the physical manifest, ring payloads/writers, NAT optimizer-state rejection, clean resource pilot, immutable physical writer, focused publication checks, bounded documentation mirrors, and full-suite handoff. The reviewer’s stale-note/default-path findings were repaired and rechecked. | None for the completed review gate. | None |
| COMM-02 | BLOCKED | Gibbs offer is made; owner journal/Vincent note is not authored and nothing was sent. | Owner authors or records hold; sending remains separately authorized. | Owner decision |
| ADD-01 | PASS | Legacy suite passes; v4 paths are isolated and existing source/result paths were not modified. | None. | None |
| MOD-01 | PASS | Dataset/spec/kernel/checkpoint/backend/compatibility contracts and validation tests exist. | None for bounded scope. | None |
| MOD-02 | PASS | Rings share target moments, objectives, training and checkpoint boundaries; no plugin framework added. | None for bounded scope. | None |
| MOD-03 | PASS | Spatial/direct and Hamming/Walsh routes, mixtures and identities are tested. | None for bounded scope. | None |
| MOD-04 | PASS | Portable NPZ/JSON state, resume/hash rejection and safe source metadata export are tested. | None for bounded scope. | None |
| RING-01 | PASS | 400-point/320–80 loader equivalence, train-only normalization and row-major MSB codec are artifact-backed. | None for bounded n=4 smoke. | None |
| RING-02 | PASS | Both ring profiles run through the NumPy IQP model and backend import guard; v1 462-bin path remains separate. | None. | None |
| RING-03 | PASS | D3 data-dependent parity initialization at scale `0.1` is implemented; both kernels × n=6,8 × five registered seed IDs completed 300-step main runs, with 20 manifests recording deterministic duplicates and `n_unique=1` per profile/n group. | None for execution/provenance coverage; do not interpret duplicate seeds as stochastic variability. | None |
| RING-04 | INCONCLUSIVE | Both n=4 ring profiles have registered fixed-photon final-only photonic evaluations and matched qubit references in `results/v4_tcdp/deploy/registered_v2_ring_photonic_*.json`; n=6/n=8 photonic deployment is deliberately unsupported by the validated adapter scope. | Extend only after a declared larger-n physical validation boundary is established; do not extrapolate n=4. | None for n=4; physical validation for larger n |
| REPRO-01 | PASS | Both sibling packages, configs, artifact families and row dispositions are inventoried and hashed. | None. | None |
| REPRO-02 | PASS | Pinned sibling state and local artifact hashes are recorded; sibling remained unchanged; unsafe serialization was not loaded. | None for inventory scope. | None |
| REPRO-03 | INCONCLUSIVE | The recorded synthetic `training_smoke` data was regenerated from the sibling recipe/seed and the source SGD trajectory was independently rerun into an isolated output tree with exact theta/loss agreement. Bandwidth is a stopped partial replay; Ghosh–Kim is adapted checkpoint replay; faithful retraining for those rows remains unavailable. | Supply exact source arrays/checkpoints and run the registered retraining cells, or retain the explicit stopped/adapted dispositions. | External source inputs for missing rows |
| REPRO-04 | PASS | Inventory preserves high-weight/topology/estimator fields and records unsupported cases rather than coercing them. | None for inventory scope. | None |
| REPRO-05 | PASS | Every inventoried source row has exact/adapted/reference-only/blocked disposition; no unperformed reproduction is claimed. | None. | None |
| COMPARE-01 | INCONCLUSIVE | The n=4 spatial and Hamming registered artifacts compare the same frozen ring checkpoint, codec, target and parameters across raw, compiled qubit, and fixed-photon final-only photonic arms. A sibling matched arm and larger-n photonic arm are not available. | Add those arms only when the exact sibling inputs and larger-n physical boundary exist. | External sibling inputs; larger-n physical validation |
| COMPARE-02 | PASS | Raw, quantized compiled, unquantized compilation-control and deployed vectors are separate; the primary compiled/deployed arms share effective parameters, while acceptance and metrics remain separate in canonical JSON. | None for the bounded ideal comparison. | None |
| COMPARE-03 | PASS | Common 20,000 accepted-sample evaluation budget, exact controls and acceptance accounting are recorded. | Add sampled uncertainty only when a sampled arm is authorized. | None for current exact scope |
| COMPARE-04 | INCONCLUSIVE | Ring comparison artifacts and the registered photonic outputs are present with visible unsupported/missing-arm labels; sibling/substrate comparison and figures remain absent. | Supply the missing sibling/substrate arms, then regenerate the report/figures without relabeling adapted replay as faithful. | External sibling data; larger-n physical validation |

The default full-suite command initially failed because Perceval could not open its default log path. With `PCVL_PERSISTENT_PATH` redirected to a writable temporary directory, the post-fourth-repair full suite passed `665` tests with one optional source-integration skip in `654.64s`. The explicit sibling integration passed `8` tests in `9.50s`. This is an environment note, not a requirement PASS for physical validation.
