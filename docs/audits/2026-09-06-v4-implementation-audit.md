# v4 implementation audit

Reviewed 2026-09-06: `de80e9313beed614528fd6332b2f78aab83c0b50..4e7cbd7ccd5842a41ec195050469fb1ee1d0c3a7`.

Verdict: changes required. Existing passing tests do not establish the advertised contracts. No implementation or sibling files were changed by this audit. Report/probe/learning artifacts are the only additions.

Independent verification: `venv/Scripts/python.exe -m pytest -q tests/v4_tcdp --basetemp .pytest_cache/review-v4-temp`, with `PCVL_PERSISTENT_PATH` set to a workspace cache directory: **114 passed in 120.36 seconds**. The full 621-test result is the implementer's reported result, not a fresh result from this audit. Small counterexamples were run independently; see accompanying probe script. No scientific sweeps were run.

## Findings requiring changes

### F01 — P1: Comparison stages put compilation error into the deployment gap

`scripts/v4_tcdp/compare_backends.py:46-60`; same pattern in `scripts/v4_tcdp/replay_sibling.py:57-60`.

The compiled arm uses `quantize=False`, while the deployed arm uses `quantize=True`. The plan requires the ideal compiled and deployed arms at the same compiled settings, so that raw-to-compiled measures compilation error and compiled-to-deployed isolates the deployment model. The current comparison instead gives raw-to-compiled approximately zero and assigns quantization error to compiled-to-deployed, even at ideal loss. On the committed n=4 Hamming smoke artifact, these distances are approximately `5.89e-16` and `0.0064403804` respectively at eta=1. This is a mislabeled scientific contrast, not evidence of a physical discrepancy.

Use quantized effective parameters for the ideal compiled reference and the identical parameters for deployment. Retain the unquantized compiler identity as a separate control. Regenerate comparison/replay artifacts and add an eta=1 compiled/deployed equality test.

### F02 — P1: The NAT control is a different optimizer, not matched continued-ideal training

`src/merlin_iqp/experiments/nat.py:379-387,482-487`; `scripts/v4_tcdp/run_nat.py:33-36`; plan section 6, especially line 195.

`run_equal_budget_control` disables every pair update but spends its budget evaluating discarded neighbors. NAT can optimize pairs; the control cannot. Both currently evaluate the same exact ideal Hamming objective, so a performance difference measures access to pair updates rather than noise adaptation. Equal counts of discarded evaluations do not satisfy the plan's identical-algorithm ideal null. The CLI also initializes fresh parity parameters and fresh Adam state rather than continuing a selected trained checkpoint with matching optimizer state.

Keep the current fixed-pair procedure only as a clearly separate ablation. Implement the required matched continuation from one frozen warm start, including optimizer state and pair updates, and verify identical trajectories under the ideal objective. The existing 16 artifacts do not close that requirement.

### F03 — P1: A synthetic source dataset is incorrectly classified as externally blocked

`.planning/v4-requirement-evidence.md:60`; `scripts/v4_tcdp/replay_sibling.py:80`.

The ledger says faithful `training_smoke` retraining cannot run because source target data is absent. The pinned sibling's `configs/experiments/training_smoke.yaml` specifies synthetic product-Bernoulli data, and `results/training_smoke/results.jsonl` records `n_samples=256` and data seed `1230519654`. Its `src/iqp_bp/experiments/data_factory.py:17-40` generates this data deterministically. Calling that source factory with the recorded settings successfully regenerated a `(256,6)` binary matrix in memory during this audit.

Regeneration through the original recorded recipe is not fabrication of a substitute dataset. Separate genuinely missing external/genomic inputs from regenerable synthetic inputs. Reproduce the source RNG/config/optimizer path and check against its frozen trajectory before claiming faithful reproduction. This audit establishes that the asserted data-file blocker is false; it does not itself certify the whole retraining trajectory.

### F04 — P2: Typed DatasetBundle construction always evaluates an invalid fallback

`src/merlin_iqp/classical/contracts.py:103`.

The default argument to `getattr(value, 'hash', hash_array(binary_matrix(value,...)))` is eagerly evaluated even when the typed target has a hash. `load_rings_dataset(4).bundle()` raises `ValueError: train must have shape (rows, width)` because `ExactProbabilities` is passed to `binary_matrix`. The public adapter and MOD-01 PASS therefore disagree.

Branch explicitly on whether the target has a hash; test the real ring bundle with typed train/test targets, not only raw arrays.

### F05 — P2: Asymmetric two-qubit maps are applied in reverse local bit order

`src/merlin_iqp/deploy/density.py:20-35,68`.

The index routine assigns the local most-significant bit to the highest-numbered selected qubit. For a map `X tensor I` on `(0,2)` in the global state `|000>`, composition returns `|001>` instead of `|100>`. Sorting the requested qubit tuple additionally loses caller-declared order. Current CP maps are swap-symmetric, so the ideal CP tests conceal this defect; general reconstructed/asymmetric maps are not protected by those tests.

Define and implement ordered local-to-global axes consistent with the MSB contract. Add asymmetric one-sided operations on adjacent and nonadjacent pairs, plus entangled-input tests.

### F06 — P2: Resume silently changes the saved learning rate

`src/merlin_iqp/classical/trainer.py:95-108`.

Checkpoints save `optimizer_state['lr']`, but `resume()` neither restores it nor rejects a mismatch. Saving at lr=0.01 and resuming into lr=0.2 succeeds, then diverges by about `0.19039` in theta after one step in a two-qubit probe. `from_checkpoint()` restores lr, but direct `resume()` is a public supported path.

Restore all trajectory-defining optimizer settings or reject incompatibility explicitly. Test direct resume with a different constructor lr and record any intentionally authorized hyperparameter change as a new run.

### F07 — P2: NAT ignores the requested initialization standard deviation

`src/merlin_iqp/experiments/nat.py:314-330`.

`run_nat(initialization_std=...)` never forwards that argument into `NatConfig`. Calling it with `initialization='small_angle', initialization_std=0, steps=0` still yields config std=0.1 and nonzero singles `[0.01257302,-0.01321049]`. This invalidates configured small-angle ablations and any reasoning based on a zero-angle control. The default parity artifacts are not affected by this specific bug.

Forward the argument and test zero and nondefault values through the public function.

### F08 — P2: Analytic tomography can be labeled Perceval tomography

`src/merlin_iqp/deploy/maps.py:226-245`.

Reconstruction always uses `_tomography_from_callable(ideal.apply)`. A successful unrelated one-input Perceval probe changes `implementation` to `perceval-tomography`; the metadata also asserts retained `global_perf` although it was not consumed by reconstruction. The physical probe's accepted probability is not checked against the analytic model. A successful backend call must not relabel synthetic analytic observations as physical tomography.

Always label this path analytic tomography with an independent probe status, until actual absolute Perceval outcomes supply the inversion. Validate the probe separately and include its actual scope.

### F09 — P2: Deployment validation records the wrong success reference and does not check it

`scripts/v4_tcdp/validate_deploy.py:30-41`.

The compiled circuit uses two different quantized pair angles, but `ideal_success_product` squares the success of an unrelated pi/3 gate. Committed manifests contain model success `0.013726388348954028` versus alleged reference `0.012345679012345684`, yet status PASS. The status checks only physicality and normalization; the requested Perceval diagnostic may also be INCONCLUSIVE while the overall result stays PASS.

Compute the success product from the actual compiled gate alphas and assert agreement. Separate analytic and physical validation statuses; when physical validation is requested, unavailable evidence must remain visible in the aggregate result rather than being summarized as complete PASS.

### F10 — P2: Source provenance does not identify the code that generated the artifacts

`src/merlin_iqp/experiments/rings.py:59`; `scripts/v4_tcdp/run_nat.py:33-36`; `src/merlin_iqp/experiments/sibling_import.py:554`.

Ring main manifests hard-code source commit `72e8079`, which predates the later ring/D3 code. NAT records the literal `working-tree` without a tree hash. The sibling exporter records a requested pinned commit even when its own inventory reports a different observed HEAD or dirty tree. These values cannot reproduce the generating implementation and may attribute changed source to an old pin.

Capture actual commit plus dirty source digest (or require a clean source snapshot) at generation time. Make export fail or explicitly carry observed provenance on pin mismatch. Preserve historical artifacts with accurate qualification; do not retroactively invent their generating hashes.

### F11 — P2: Physicality validates a supplied Choi matrix independently of the applied map

`src/merlin_iqp/deploy/maps.py:262-274`.

`GateMap` permits both Choi metadata and a Kraus/superoperator implementation, but the validator never checks they describe the same map. A transpose superoperator with an identity matrix supplied as `choi` passes every check even though it is not completely positive. A swapped/stale cache component could therefore pass the intended protection.

Derive the Choi matrix from the operative map and compare against stored data, or store one canonical representation. Check dimensions, finiteness and Hermiticity before eigenvalue checks. Add an inconsistent-representation rejection fixture.

### F12 — P2: Correct infinite KL values cannot be exported

`src/merlin_iqp/experiments/comparison.py:35-39,129-135`; `scripts/v4_tcdp/compare_backends.py:89-90`.

The metric intentionally returns positive infinity when a target-positive outcome has zero model probability. The CLI serializes it with `allow_nan=False`, causing `ValueError: Out of range float values are not JSON compliant: inf`. For example, target `[0.5,0.5]` and candidate `[1,0]` produce a valid comparison that cannot be written. Exact zeros are legitimate IQP outputs, especially identity/symmetry controls.

Use a JSON-safe explicit infinity/status representation without replacing true KL by a floored value. Test serialization on support mismatch.

### F13 — P2: Replay outputs from different source experiments overwrite one another

`scripts/v4_tcdp/replay_sibling.py:62`.

All accepted manifests write to `output_root/training_smoke/step_NNNN`, regardless of source ID, model, checkpoint hash or config. Two different supported source checkpoints at the same step overwrite the same vectors and manifest. This violates isolated reproducible artifact namespaces as soon as replay is extended beyond its one current example.

Namespace by validated source identity and checkpoint hash, and reject incompatible existing destinations or write an explicit new run. Add a two-manifest same-step test.

## Smaller confirmed issue

`experiments/comparison.py:58-60`: expected coverage initializes q=1 outcomes to one even for zero requested samples. The point-mass probe reports coverage=1 at N=0; the correct coverage is zero. Validate integer counts and handle N=0 first. This does not affect the committed 20,000-sample expectation calculations.

## Status and follow-up

Do not close already acknowledged full-Fock multi-gate, photonic rings, marginal/uncertainty, owner-control or external-review gaps on the strength of these tests. Conversely, do not classify regenerable source data as externally blocked. MOD-01/MOD-04 and related PASS claims need disposition against the concrete failures above.

The present D1 implementation multiplies ideal accepted mass by eta**n and deliberately leaves conditional quality unchanged. It does not independently establish source-once/full-Fock behavior. The current NAT objective is exact ideal Hamming MMD over quantized angles; its name must not imply demonstrated noise robustness. Neither point is a new claim that fixed-photon loss algebra itself is wrong.

Recommended repair order: F01/F02/F03 (scientific contrasts and deliverables), F04–F07 (runtime and numerical contracts), F08–F13 (validation/provenance/artifacts), then regenerate affected artifacts and rerun independent controls. No fixes, commits, merges or publication were performed by this review.
