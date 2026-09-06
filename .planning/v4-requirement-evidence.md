# v4.0 requirement evidence ledger

Updated 2026-09-06. Statuses are strict:

- `PASS`: the bounded criterion has direct implementation and verification evidence.
- `FAIL`: an attempted acceptance check produced a contrary result.
- `INCONCLUSIVE`: implementation/evidence exists but does not establish the full criterion.
- `NOT IMPLEMENTED`: the required implementation or run does not exist.
- `BLOCKED`: the next action cannot safely proceed until a named owner decision or external input is supplied.

An incomplete row includes the missing item, next concrete action, and owner dependency. A PASS is limited to the stated bounded evidence and never upgrades a dependent scientific claim.

| ID | Status | Evidence / missing implementation or evidence | Next concrete action | Owner dependency |
|---|---|---|---|---|
| TRAIN-01 | PASS | NumPy core, contracts, provenance, and sibling export boundary exist; focused tests pass. | None for bounded scope. | None |
| TRAIN-02 | PASS | `chain_1d` and strict generator validation are tested. | None. | None |
| TRAIN-03 | PASS | Classical round-trip and separate signed/winding deployment compiler tests pass. | None for supported weight 1/2 scope. | None |
| TRAIN-04 | PASS | Exact gradients, spatial/Hamming objectives, optimizer update, initialization and checkpoint tests pass. | None for explicit ring profiles. | None |
| CHAN-01 | INCONCLUSIVE | D1 is selected as fixed-photon `g2=0` with explicit loss; the code records the restricted model, but a physical noisy source/map validation is not complete. | Run the prescribed fixed-photon source-once controls and independent absolute-outcome reconstruction; keep `g2>0` outside scope. | None for fixed-photon implementation; Perceval/source evidence for physical claim |
| CHAN-02 | PASS | Choi positivity, `E†I <= I`, Hermiticity, non-diagonal reconstruction and held-out fixtures pass. | None for ideal analytic map. | None |
| CHAN-03 | INCONCLUSIVE | Key/winding/cache tests pass, but representative maximum map-cost and RSS measurements were not run. | Run isolated representative timing/RSS pilots before any cache sweep. | D1 only if noisy maps are included |
| CHAN-04 | INCONCLUSIVE | Success-weighted Haar formula and ideal fidelity fixture pass; no independent physical tomography integration is established. | Run the prescribed Perceval absolute-outcome reconstruction and independent Kraus/Haar check. | D1 for noisy scope |
| DEPLOY-01 | INCONCLUSIVE | Signs, winding, topology rejection, unnormalized composition and no-`4^n` allocation pass; n=10 RSS gate is missing. | Run the isolated n=10 memory pilot and record peak RSS. | None for ideal map; D1 for noise |
| DEPLOY-02 | PASS | Ideal compiled-map equality, k=0, nonadjacent/asymmetric, sign/scale/winding and probability fixtures pass. | None for implemented ideal weight 1/2 maps. | None |
| DEPLOY-03 | INCONCLUSIVE | Fixed-photon `g2=0` and explicit `eta**n` acceptance scaling are implemented; prescribed multi-gate/bystander/shared-gate full-Fock controls are still absent, and `g2>0` remains out of scope. | Run the fixed-photon n=2/3 source-once controls and record conditional TVD plus absolute success; do not substitute them for multiphoton validation. | None for fixed-photon scope; optional Perceval evidence |
| DEPLOY-04 | NOT IMPLEMENTED | No chain-specific final-only versus intermediate-projection proof or hidden-label discrepancy study exists. | Prove restricted no-return conditions, or reject the topology and record the unsupported boundary. | D1 if hidden-label/noise cases are included |
| DEPLOY-05 | INCONCLUSIVE | Fixed-photon and heralded formula helpers pass; actual source acceptance under the selected model is not measured. | Compute attempts per accepted sample from the selected source/acceptance instrument. | D1 |
| REFRAME-03 | INCONCLUSIVE | D1 fixes the primary scope to fixed-photon accepted output; the existing erasure artifact remains explicitly conditional/synthetic and does not provide unconditional non-post-selected Fock categories. | Either complete the separately scoped fixed-photon full-Fock failure artifact, or retain this requirement as unsupported and document the boundary. | None for the selected scope; owner must accept the unsupported boundary for closure |
| NULL-03 | BLOCKED | Owner k=0 prediction is absent. | Owner records prediction before the k=0 control is interpreted. | Owner decision |
| NULL-04 | BLOCKED | Owner same-parameter ideal-map prediction is absent. | Owner records raw-versus-compiled prediction before comparison claims. | Owner decision |
| NULL-05 | BLOCKED | Owner loss prediction and photon-number assumptions are absent. | Owner records the prediction after D1 selection. | D1 + owner |
| NULL-06 | BLOCKED | Owner throughput predictions are absent. | Owner records separate CP and heralded-model predictions. | D1 + owner |
| NULL-07 | BLOCKED | Owner falsifiable gap hypothesis is absent. | Owner records the hypothesis and success/failure interpretation rule. | Owner decision |
| NULL-08 | BLOCKED | Owner NAT equality and equal-budget continuation explanation is absent. | Owner records the prediction after D2/D3 selection. | D2 + D3 + owner |
| NULL-09 | NOT IMPLEMENTED | Equality fixtures exist, but every-cell mass-preserving mutation/control panel is not implemented. | Add explicit ideal equality, metric-specific mass mutation, and independent map/success mutation controls. | D1 for selected physical arm |
| SWEEP-01 | PASS | Separate ring, sibling and comparison manifests preserve source settings and distinct seed/budget fields. | None for bounded artifacts. | None |
| SWEEP-02 | PASS | Isolated namespaces, NPZ/JSON artifacts, hashes, compatibility dispositions and stale-cache tests pass. | None for bounded artifacts. | None |
| SWEEP-03 | NOT IMPLEMENTED | Marginal/source-AC panel, occupancy artifact and independent hand fixtures are not complete. | Implement the remaining metrics without fabricating exact vectors from moments. | D1 only for noisy arm |
| SWEEP-04 | NOT IMPLEMENTED | Only n=4 ring smoke comparisons exist; no sibling matched arm, sampled uncertainty or noisy comparison exists. | Complete sibling data closure and selected physical model, then run paired profiles within budget. | D1; D3 for replication |
| SWEEP-05 | PASS | Reports distinguish delivered, adapted, reference-only, blocked and unperformed work. | None. | None |
| NAT-01 | PASS | D2 selects bounded discrete alpha-key neighbor search with continuous single-angle updates; focused tests prove pair-key movement, catalog membership, winding preservation and reproducibility. | Validate on the registered ring/cell profile before interpreting efficacy. | None |
| NAT-02 | INCONCLUSIVE | D1–D3 are selected and the optimizer/control implementations exist; no registered 150-step matched NAT/continued-ideal production run has been completed. | Freeze a validated profile and run matched 150-step NAT and equal-budget continuation control within the plan budget. | None for implementation; physical validation if a noisy arm is selected |
| NAT-03 | NOT IMPLEMENTED | The 20-minute n=8/two-day n=4 stop-rule run was not attempted. | Run only after NAT prerequisites are satisfied; record attempted/stopped if the rule fires. | D1 + D2 + D3 |
| WRITE-07 | BLOCKED | Owner explanation of signs, source/gate noise, projection, loss, NAT and conditioning is absent. | Owner writes the explanation before interpretive synthesis. | Owner decision |
| WRITE-08 | PASS | Rings, sibling, deployment, backend-comparison and v4 synthesis reports link canonical artifacts and limits. | None for current evidence. | None |
| WRITE-09 | INCONCLUSIVE | AGENTS was updated, but README and legacy technical findings have not been mirrored after review. | Mirror only verified v4 conclusions after the owner/reviewer pass. | Owner/reviewer approval |
| REVIEW-02 | NOT IMPLEMENTED | Independent Fable/Opus and Codex review of implementation evidence has not been run. | Give the reviewer handoff to an independent reviewer and record finding dispositions. | None, but required review gate |
| COMM-02 | BLOCKED | Gibbs offer is made; owner journal/Vincent note is not authored and nothing was sent. | Owner authors or records hold; sending remains separately authorized. | Owner decision |
| ADD-01 | PASS | Legacy suite passes; v4 paths are isolated and existing source/result paths were not modified. | None. | None |
| MOD-01 | PASS | Dataset/spec/kernel/checkpoint/backend/compatibility contracts and validation tests exist. | None for bounded scope. | None |
| MOD-02 | PASS | Rings share target moments, objectives, training and checkpoint boundaries; no plugin framework added. | None for bounded scope. | None |
| MOD-03 | PASS | Spatial/direct and Hamming/Walsh routes, mixtures and identities are tested. | None for bounded scope. | None |
| MOD-04 | PASS | Portable NPZ/JSON state, resume/hash rejection and safe source metadata export are tested. | None for bounded scope. | None |
| RING-01 | PASS | 400-point/320–80 loader equivalence, train-only normalization and row-major MSB codec are artifact-backed. | None for bounded n=4 smoke. | None |
| RING-02 | PASS | Both ring profiles run through the NumPy IQP model and backend import guard; v1 462-bin path remains separate. | None. | None |
| RING-03 | PASS | D3 data-dependent parity initialization at scale `0.1` is implemented; both kernels × n=6,8 × five registered seed IDs completed 300-step main runs, with 20 manifests recording deterministic duplicates and `n_unique=1` per profile/n group. | None for execution/provenance coverage; do not interpret duplicate seeds as stochastic variability. | None |
| RING-04 | NOT IMPLEMENTED | No validated ideal photonic ring adapter or decoded photonic ring samples exist. | Complete physical support and deploy frozen ring checkpoints with matched qubit reference. | D1 for physical source; topology/projection evidence |
| REPRO-01 | PASS | Both sibling packages, configs, artifact families and row dispositions are inventoried and hashed. | None. | None |
| REPRO-02 | PASS | Pinned sibling state and local artifact hashes are recorded; sibling remained unchanged; unsafe serialization was not loaded. | None for inventory scope. | None |
| REPRO-03 | BLOCKED | `training_smoke` frozen checkpoint replay is adapted; source target data is absent, so faithful SGD/data retraining and bandwidth/Ghosh–Kim replay cannot run. | Obtain/validate the missing source target/checkpoint closure, then rerun source SGD and registered replays. | External source inputs |
| REPRO-04 | PASS | Inventory preserves high-weight/topology/estimator fields and records unsupported cases rather than coercing them. | None for inventory scope. | None |
| REPRO-05 | PASS | Every inventoried source row has exact/adapted/reference-only/blocked disposition; no unperformed reproduction is claimed. | None. | None |
| COMPARE-01 | INCONCLUSIVE | Ring raw/qubit-like/ideal-map control exists; fixed-photon loss scope is selected, but a validated photonic ring realization and sibling matched arm are absent. | Complete ring topology/projection validation, then add the selected fixed-photon deployed arm and sibling target/model. | External sibling data and topology/projection evidence |
| COMPARE-02 | PASS | Raw, compiled and deployed vectors, targets, metrics and acceptance are separate in canonical JSON artifacts. | None for bounded comparison. | None |
| COMPARE-03 | PASS | Common 20,000 accepted-sample evaluation budget, exact controls and acceptance accounting are recorded. | Add sampled uncertainty only when a sampled arm is authorized. | None for current exact scope |
| COMPARE-04 | INCONCLUSIVE | Ring comparison artifact exists and reference-only capability is visible; sibling/substrate comparison and figures are missing. | Complete sibling/physical arms, then regenerate comparison figures and manifests. | D1; external sibling data |

The default full-suite command initially failed because Perceval could not open its default log path. With `PCVL_PERSISTENT_PATH` redirected to a writable temporary directory, the same suite passed `609` tests. This is an environment note, not a requirement PASS for physical validation.
