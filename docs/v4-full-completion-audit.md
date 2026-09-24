# Completing v4.0 and extending the case study

Date: 2026-09-24. Documentation review at checkout `65039a1`. **Full scientific v4.0 remains incomplete.** This is a research plan, not new experimental evidence or an owner-authored interpretation.

## Read this first

The proposed independent case study asks: **When does a classically trained photonic generative model retain useful, unseen correlations after compilation, conditioning, and adaptive execution, and what classical and physical resources are needed to match it?** A negative result is a valid outcome. This small-n registration tests classical comparisons and generalization; computational quantum advantage requires a separate future scaling protocol.

Read in this order:

1. This audit: original commitments, completed work, remaining evidence.
2. [Literature and formalism crosswalk](v4-literature-crosswalk.md): equations, assumptions, and limits of transfer.
3. [Benchmark specification](v4-advantage-benchmark-spec.md): surrogate, generalization, and resource comparisons.
4. [MBQC and adaptivity proposal](v4-mbqc-adaptivity-plan.md): an equivalent implementation followed by a separately identified model extension.
5. [Execution roadmap](../.planning/v4-full-completion-roadmap.md): files, dependencies, experiments, and stop gates.

## 1. What v4.0 originally meant

The [binding TCDP plan](v4-plan-train-classical-deploy-photonic.md), [additive design](v4-additive-pipelines-design.md), and [queued requirements](../.planning/REQUIREMENTS-v4.0-queued.md) define Phases 26–32. They combine a classical IQP trainer, qualified photonic compilation, ring learning, faithful sibling reproduction, matched backend comparisons, noise-aware training (NAT), and scientific synthesis. TCDQ means train classical/deploy quantum; TCDP is this project's photonic realization of that broader strategy.

The additive design gives rings and sibling reproduction their own manifests. The older **1,920-training-file Ising grid is a calibration extension**, not the total v4 workload or an automatic obligation to launch it. Its 15,120/60,480 deployment counts depend on different noise assumptions. Do not revive those counts without a physical model and resource registration.

The requirements file says “52 unique requirements,” but currently enumerates **51 active IDs**. `COMM-02` was explicitly retired on 2026-09-08, giving 52 historical IDs including that retired communication item. This plan tracks all 51 active IDs and preserves the retirement. It does not reinstate outreach.

## 2. How far we got

The [2026-09-10 bounded release](v4-bounded-release.md) and [evidence ledger](../.planning/v4-requirement-evidence.md) establish the following recorded scope. These are artifact-backed historical results inspected during planning; the experiments were not rerun for this document.

| Workstream | Recorded evidence | Remaining limit |
|---|---|---|
| Classical core | Exact NumPy IQP model, gradients, spatial/Hamming objectives, portable state, provenance and replay rejection | Exact enumeration is an exponential reference, not an efficient classical surrogate |
| Rings | n=4 smoke; n=6/8, 300-step main profiles; 22 refreshed comparison cells | Five seed labels yield `n_unique=1` per deterministic main group; main fit remains imperfect |
| Sibling | Eight available training cells faithfully retrained; n=6 exact validation rerun; matched source/local/compiled comparisons | Missing datasets/environments and unsupported source profiles remain blocked/reference-only |
| Optical controls | Direct Perceval fixed-photon n=2/3 controls and n=4 ring smoke, absolute mass retained | Larger ring/sibling arms are analytic CP-map references; no n=6/8 direct optical validation or hardware result |
| Physical model | Fixed photon number, `g2=0`, uniform loss, declared final projection; analytic tomography and physicality checks | Multiphoton inputs, distinguishability memory, and general projection equivalence are unestablished |
| NAT | Matched 150-step continuation controls, discrete pair-angle moves, recorded n=8 run below 20 minutes | Uniform loss leaves conditional shape unchanged; these controls do not establish useful noise adaptation |
| Owner checkpoints | Predictions and WRITE-07 explanation recorded | NULL-07 source-gap hypothesis has not been experimentally adjudicated |
| Software release | Historical clean-checkout gate: 726 passed, 1 skipped; 37 explicit sibling tests | A software gate does not certify physical correctness or generalization |

Illustrative recorded findings: n=8 ring held-out TVD is 0.7348 (Hamming) and 0.6869 (spatial); the n=9 sibling analytic deployment estimates range from roughly 72 billion to 3.51 trillion attempts per accepted output. These values motivate quality and resource evaluation together; they do not predict MBQC performance. See the bounded release for exact profiles and assumptions.

The present code contains a gate-based IQP/dual-rail optical workflow, not a graph-state measurement-pattern executor. Inspection of `src/merlin_iqp/classical/model.py`, `deploy/fock.py`, and a scoped MBQC/feed-forward search found no MBQC backend. A final optical measurement alone does not implement the proposed graph-state pattern. IQP nevertheless has a non-adaptive MBQC realization; causal basis dependencies are not required for that realization.

## 3. Full-scope gaps and success evidence

| Gap | Required next evidence | Why it matters | Runnable boundary |
|---|---|---|---|
| Physical/source contract | Explicit input mixture, distinguishability, loss placement, detector POVM, accepted outcomes, cutoffs and residual mass | A local gate map can omit source/bystander costs or correlated hidden labels | Design now; broader source profile needs owner choice |
| Source-once full-Fock checks | n=2/3 no-gate, bystander, shared-gate, asymmetric/wrap fixtures; ideal, loss-only, source-only, distinguishability-only and joint source/loss cells | Conditional agreement can conceal wrong absolute probability | New model implementation and pilot required |
| Projection/composition | Independent final-only and intermediate calculations, supported-topology proof or an explicit restricted capability | A tested fixture is not a theorem that rejected sectors never return | Mathematical work and small fixtures before scale |
| Larger ring deployment | Frozen trained n=6 and n=8 checkpoints evaluated directly, or a justified compositional bound with an accurately scoped claim | n=4 smoke and analytic maps cannot certify these circuits | Resource pilot first; inability remains INCONCLUSIVE |
| NULL-07 | Hold gate/compiler fixed; vary only source; report conditional and mass effects separately | Tests the owner's existing causal hypothesis | No new prediction needed; source capability is missing |
| Sibling gaps | Exact missing source data/config/checkpoint/environment or explicit capability extension, each identified by inventory row | Substituting a dataset cannot count as faithful reproduction | External-input rows stay BLOCKED |
| Sampling uncertainty | Actual draws, unique RNG streams, interval method, accepted-shot and attempt-budget panels | Nominal “20,000 shots” on a population vector provides no sampling interval | Can be designed independently of hardware |
| NAT beyond the null | A validated noise model that changes the objective, paired with equal-budget ideal continuation and fixed-pair ablation | Extra optimization and noise adaptation are different effects | Owner selects conceptual noise objective; retain existing stop rule |
| Final interpretation | Owner writes conclusions after viewing results; independent scientific/code review at final head | Neither tests nor agent prose demonstrate unaided understanding | After experimental evidence |

Full original acceptance must retain each requirement's actual wording. A justified impossibility or missing-input disposition is useful science, but it is **not a PASS for an unperformed required experiment**. If a requirement becomes infeasible, record a scope amendment separately and name the result “revised scope complete”; do not rename it full original v4.0.

## 4. Requirement coverage

The groups below partition every active ID exactly once. Bounded PASS statuses remain in the original ledger; this table identifies what must be revisited for full scope, without overwriting history.

| Active IDs | Completion treatment | Roadmap |
|---|---|---|
| TRAIN-01, TRAIN-02, TRAIN-03, TRAIN-04 | Preserve core and source tests; reconcile signed convention before new compilation; run baseline gate | R0, R2 |
| MOD-01, MOD-02, MOD-03, MOD-04, ADD-01 | Preserve shared contracts, existing result identities and all legacy paths; add narrow modules | R0–R7 |
| CHAN-01, CHAN-02, CHAN-03, CHAN-04 | Retain analytic checks; add source-valid physical reconstruction only for registered supported maps; pilot cost | R1 |
| DEPLOY-01, DEPLOY-02, DEPLOY-03, DEPLOY-04, DEPLOY-05, REFRAME-03 | Add full-Fock/source and projection evidence, direct larger-n boundary, complete failure accounting and source-attempt cost | R1, R4 |
| NULL-03, NULL-04, NULL-05, NULL-06, NULL-08, NULL-09 | Preserve recorded predictions and passing scoped controls; extend controls only when model assumptions change | R1, R4 |
| NULL-07 | Execute source-isolation test; record support/refutation/inconclusive result | R1 |
| RING-01, RING-02, RING-03, RING-04 | Preserve datasets/training results; add genuine replication as new profiles, and full trained-checkpoint deployment evidence | R1, R3 |
| REPRO-01, REPRO-02, REPRO-03, REPRO-04, REPRO-05 | Read inventory row-by-row; recover exact inputs/capabilities; label faithful/adapted/reference/blocked separately | R0, R4 |
| SWEEP-01, SWEEP-02, SWEEP-03, SWEEP-04, SWEEP-05 | Register new manifests and sampled panels; retain raw/compiled/noisy distinctions; derive counts rather than inherit calibration grid | R2–R4 |
| COMPARE-01, COMPARE-02, COMPARE-03, COMPARE-04 | Preserve matched frozen artifacts; add independent optical and sampled uncertainty evidence; distinguish same-model from different-model contests | R1–R4 |
| NAT-01, NAT-02, NAT-03 | Preserve discrete optimizer/control; register distinct-noise efficacy or honest attempted/stopped outcome | R4 |
| WRITE-07, WRITE-08, WRITE-09, REVIEW-02 | Retain owner explanation; new owner interpretation, artifact-linked reports and final independent review | R7 |

Historical `COMM-02`: retired; no execution task. New literature/benchmark/MBQC work uses separate `LIT`, `BENCH`, `MBQC`, and `ADAPT` IDs in the roadmap. It does not retroactively expand the old acceptance contract.

## 5. Decisions recorded for this planning pass

- Maintain two explicit tracks: original v4 completion and literature-led extensions. Combining their acceptance checklists would obscure whether original obligations were met.
- Extend the existing Python scientific package rather than introduce TypeScript into numerical code. The live repository is a Python package with NumPy/Perceval tests; TypeScript is not a current runtime dependency.
- Propose equivalent MBQC compilation before a new adaptive generative model. Equivalence is a falsifiable control; adding a new ansatz at the same time would confound representation and learning changes. Both stages are planned; neither conceptual implementation is started here.
- Keep graph-state MBQC and photonic state injection as distinct architectures. They share measurement-conditioned operations but need different resource and correctness arguments.
- Apply Brown's **Explainable algorithms, human judgment retained** principle: artifact status, model assumptions, and owner decisions remain visible; no scalar “advantage score” substitutes for scientific judgment.

This turn does not change numerical code, historical results, sibling worktrees, owner answers, or publish anything. Concrete owner decision prompts and conceptual checkpoints are in the roadmap; planning is complete without inventing their answers.

## 6. Verification of this documentation pass

The local paper files were extracted and fingerprinted; relevant theorem pages were visually checked. Reading depth and source issues are recorded in the crosswalk. Requirement coverage and local links are checked mechanically in the final validation record. No new paper replication or experimental result is claimed.

Final readback: 51/51 active requirements mapped once; all 19 local links in the five new documents resolve. The artifact validator passes 579 JSON files, 72 JSONL rows and 19 embedded hashes with zero failures (working-directory scope). The independent committed-evidence probe passes 99 evidence files and 64 sibling payload hashes and recomputes ring/sibling summary quantities. Small independent Fourier/kernel/J-gadget equation checks pass at maximum absolute residual 5.56e-17. See the roadmap's validation record for commands and boundaries.

The attempted command `venv/Scripts/python.exe -m pytest -q --basetemp=tmp/pytest-v4-planning-20260924` stopped during collection: Perceval could not write its default log under `AppData/Local/quandela/perceval-quandela/logs`. This is an environment-blocked check, not a failing scientific experiment. The prior 726-test result remains historical. A future permitted test run can use the documented process-local writable Perceval log directory. No environment variables were changed in this pass.

There is no `package.json`/TypeScript configuration or configured Python lint/type-check command in `pyproject.toml`; npm lint/test and `tsc --noEmit` are not applicable to this documentation-only Python repository change.

## Audit revision: expected identities and execution boundary

M1 now uses the non-adaptive IQP incidence graph with final classical XOR. Ideal equality is an expected implementation identity, not a physics finding or adaptivity gain. M2 separately asks whether a specified outcome-dependent policy helps against the matched non-adaptive model. The small-n benchmark supports classical-comparison/generalization conclusions only. The roadmap now requires owner-authored nulls and red-first tests, distinguishes same-q surrogates from mechanism interventions, and caps the first tranche without retiring any original requirement. A fresh green baseline remains a prerequisite to new experiment execution.
