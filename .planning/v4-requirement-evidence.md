# v4.0 requirement evidence ledger

Statuses are strict: `PASS` means the bounded implementation criterion has direct evidence; `INCONCLUSIVE` means a required physical, source, owner or review input is absent; `FAIL` means a required acceptance condition was not met. A PASS here never upgrades a dependent scientific claim.

| ID | Status | Evidence / remaining gate |
|---|---|---|
| TRAIN-01 | PASS | `src/merlin_iqp/classical/PROVENANCE.md`, focused core tests |
| TRAIN-02 | PASS | `test_classical_core.py`, chain generator validation |
| TRAIN-03 | PASS | classical round-trip and separate deploy compiler tests |
| TRAIN-04 | PASS | `test_classical_core.py` exact gradients/objectives/update |
| CHAN-01 | INCONCLUSIVE | D1 source/detection model not selected |
| CHAN-02 | PASS | `test_deploy.py` Choi, E†I, Hermiticity, tomography fixtures |
| CHAN-03 | INCONCLUSIVE | key/cache boundaries pass; representative map-cost gate not run |
| CHAN-04 | INCONCLUSIVE | formula fixture passes; independent physical/tomography validation remains |
| DEPLOY-01 | INCONCLUSIVE | composition/sign/winding tests pass; n=10 RSS gate not measured |
| DEPLOY-02 | PASS | direct compiled equality, k=0/nonadjacent/winding fixtures |
| DEPLOY-03 | INCONCLUSIVE | one-gate ideal reference only; g2/loss is explicitly D1-gated |
| DEPLOY-04 | INCONCLUSIVE | projection/full-Fock discrepancy study not completed |
| DEPLOY-05 | INCONCLUSIVE | formulas tested; actual source acceptance model is open |
| REFRAME-03 | INCONCLUSIVE | conditional erasure helper passes; no unconditional Fock output |
| NULL-03 | INCONCLUSIVE | owner prediction required |
| NULL-04 | INCONCLUSIVE | owner explanation/prediction required |
| NULL-05 | INCONCLUSIVE | owner loss prediction and D1 required |
| NULL-06 | INCONCLUSIVE | owner throughput prediction required |
| NULL-07 | INCONCLUSIVE | owner gap hypothesis required |
| NULL-08 | INCONCLUSIVE | owner NAT interpretation required |
| NULL-09 | INCONCLUSIVE | ideal equality fixture exists; full control/mutation panel not complete |
| SWEEP-01 | PASS | isolated ring/sibling/comparison manifests; no calibration count substitution |
| SWEEP-02 | PASS | NPZ/JSON namespaces, hashes, dispositions and cache rejection tests |
| SWEEP-03 | INCONCLUSIVE | core metrics pass; marginal/source-AC panel is not complete |
| SWEEP-04 | INCONCLUSIVE | matched n=4 ring smoke only; no sibling/noisy arm |
| SWEEP-05 | PASS | reports distinguish delivered, reference-only and blocked work |
| NAT-01 | INCONCLUSIVE | D2 optimizer decision not selected |
| NAT-02 | INCONCLUSIVE | no approved noise model/budgeted continuation run |
| NAT-03 | INCONCLUSIVE | stop-rule run not attempted |
| WRITE-07 | INCONCLUSIVE | owner-authored explanation is required |
| WRITE-08 | PASS | rings, sibling, backend and synthesis reports exist with artifact links |
| WRITE-09 | INCONCLUSIVE | final README/technical-findings mirror awaits review |
| REVIEW-02 | INCONCLUSIVE | required Fable/Opus and Codex review not run |
| COMM-02 | INCONCLUSIVE | Gibbs offer recorded; owner journal/Vincent note not authored |
| ADD-01 | PASS | additive paths and legacy tree preserved; existing paths untouched |
| MOD-01 | PASS | typed contracts and focused validation tests |
| MOD-02 | PASS | rings use shared target/objective/trainer/checkpoint boundaries |
| MOD-03 | PASS | spatial/Hamming objectives and Walsh/direct tests |
| MOD-04 | PASS | checkpoint/resume/hash/cache tests and NPZ/JSON artifacts |
| RING-01 | PASS | exact loader equivalence and frozen dataset/codec manifests |
| RING-02 | PASS | both ring profiles use NumPy IQP model with backend import guard |
| RING-03 | PASS | both n=4 smoke profiles and registered n=6/8 budgets |
| RING-04 | INCONCLUSIVE | validated photonic ring adapter is not available |
| REPRO-01 | PASS | sibling inventory: both packages, configs, artifacts and dispositions |
| REPRO-02 | PASS | pinned clean state plus separately hashed local artifacts; sibling unchanged |
| REPRO-03 | INCONCLUSIVE | frozen `training_smoke` checkpoint replay passes as adapted; source SGD/data trajectory and bandwidth/Ghosh–Kim retraining remain unavailable |
| REPRO-04 | PASS | inventory preserves unsupported topology/weights and source fields |
| REPRO-05 | PASS | every inventoried row has explicit disposition; no reproduction claim |
| COMPARE-01 | INCONCLUSIVE | raw/qubit-like and ideal map control exists; supported physical arm absent |
| COMPARE-02 | PASS | raw/compiled/deployed plus target/acceptance metrics are separate |
| COMPARE-03 | PASS | common 20,000 accepted-sample budget is recorded; exact controls used |
| COMPARE-04 | PASS | artifact-backed ring comparison and visible reference-only arm |

The ledger is intentionally not a checkbox rewrite of the queued requirements. Missing inputs remain visible.
