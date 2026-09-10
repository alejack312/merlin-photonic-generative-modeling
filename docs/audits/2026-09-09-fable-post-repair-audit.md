# Post-repair codebase audit (2026-09-09, Claude Fable 5.1)

Scope: `codex/v4-implementation` at `279623b`, after the gpt-5.6-luna repair pass. Read the v4 classical, deploy, experiments and script code end to end, re-derived the load-bearing math, re-ran probes against the published artifacts, and re-ran the test suite. Findings are ordered by how much they undermine a claim the ledger currently marks `PASS`.

## What holds up

- Compilation identity `exp(i t ZiZj) = exp(-i t) exp(i t Zi) exp(i t Zj) CP(4t)`, the `PS(-2t)` sign, the nearest-lift winding rule, and the wrapped-CP / lifted-compensation split are correct (`deploy/compile.py`, `deploy/density.py`).
- Hamming-Gaussian Walsh spectrum `((1+r)/2)^n ((1-r)/(1+r))^|a|`, `tau = tanh(1/(4 sigma^2))`, the spatial `W K W^T / N^2` transform, the IQP moment formula and its Jacobian, and the FWHT probability vector are all correct (`classical/kernel.py`, `objectives.py`, `expectation.py`, `model.py`).
- Choi construction, `E^dagger(I)` check, and the success-weighted Haar fidelity `(Tr J + <u|J|u>)/((d+1) Tr J)` reduce to the standard `(d F_e + 1)/(d+1)` and give 1 for the ideal map (`deploy/maps.py`).
- `_cp_success(alpha)` reproduces the SLOS accepted mass in the physical manifest to ~1e-16 for alpha = 0.8, 1.2 and their product.
- The direct SLOS path's `[1,0]*n` input plus BS/PS/BS sandwich is the correct IQP distribution in the declared `(0,1)->0` readout convention (BS = S H S, so BS D BS on the declared logical-1 input equals H D H on logical-0 up to phases).
- Fixed-photon `eta**n` is applied exactly once on every path I traced (`density.apply_compiled_density`, `fock.*`, `ring.evaluate_ring_artifact`, `compare_*`).

## Findings

### F1. The n=10 "RSS growth < 400 MiB" PASS is a measurement artifact (DEPLOY-01, CHAN-03, B03)

`resource_budget_final_v8.json` reports `rss_growth_bytes: 0` and `peak_rss_bytes == baseline_rss_bytes` for every n, including n=10 where the density path holds several 1024x1024 complex matrices. That is not physically plausible and is explained by the sampler:

- `scripts/v4_tcdp/resource_pilot.py::_run_isolated` samples `_rss_bytes(process.pid)`. On Windows the venv `python.exe` is a launcher that spawns the real interpreter as a separate process (verified: `Popen.pid` 26480 vs interpreter `os.getpid()` 37616). The parent therefore samples a ~4.4 MB stub; a child holding 256 MiB still reads 4399104 bytes.
- The worker's self-reported baseline (~153 MB, correct, measured from inside the interpreter) is always larger than every parent sample, so `peak_rss = max(baseline, samples) = baseline` and growth is exactly 0 by construction.

The RSS criterion has therefore never been exercised. Fix: have the worker report its own `peak_working_set_size` at exit (it already has the correct `PROCESS_MEMORY_COUNTERS_EX` struct), or resolve the grandchild PID. Until then the ledger rows citing "n=10 RSS < 400 MiB" should be `INCONCLUSIVE`.

Related: `experiments/comparison.py::process_rss_bytes` declares a 4-field struct, so `GetProcessMemoryInfo` fails with `ERROR_INSUFFICIENT_BUFFER` (122) and returns `None` on Windows. Every comparison artifact's `resource_report` is `rss_unavailable`; the artifacts say so honestly, but the helper is dead on the platform it was run on.

### F2. Two of the three "mutation controls" in every comparison artifact are hard-coded constants (NULL-09, SWEEP-03)

`experiments/comparison.py::mutation_control_report` computes the distribution mutations genuinely, but `success_controls` and `map_controls` are literal dictionaries:

```python
"acceptance_mass_after": arm.acceptance_mass * 0.99,
"conditional_vector_hash_equal": True,
"distribution_metrics_unchanged": True,
...
"success_after": arm.acceptance_mass,
"conditional_vector_changed": True,
"success_independent_of_distribution_mutation": True,
```

Nothing is mutated or re-evaluated. The values appear verbatim in `results/v4_tcdp/comparisons/**` and `sibling_comparisons/**`, and `tests/v4_tcdp/test_comparison.py:115` asserts the constant `True`. The ledger's NULL-09 evidence ("independent map mutations, and acceptance-only mutations") and SWEEP-03 ("mass-preserving controls") should not count these two panels. Either implement them (perturb `success` on an unnormalized map and re-run the metric panel; scale acceptance and re-hash the conditional vector) or delete them from the artifact schema.

### F3. `support_validity` is hard-coded to 1.0 and is wrong for every ring target (SWEEP-03, COMPARE-04)

`MatchedComparison.metrics()` writes `"support_validity": 1.0`. The plan (sec 5.3) said validity is trivially 1 only for the Ising calibration grid and explicitly required "recompute support for every dataset". The ring train histograms have zero-mass cells: 4/16 at n=4, 40/64 at n=6, 177/256 at n=8. An IQP output vector has generic full support, so `sum_{p>1e-6} q < 1` for every ring cell, yet the published n=6 comparison artifacts report 1.0. Replace with `float(q[p > 1e-6].sum())`.

### F4. NAT has no noise term, so the "matched arms" and the NULL-08 control are a determinism check (NAT-01, NAT-02, NULL-08)

`experiments/nat.py::_compiled_objective` evaluates `objective_and_gradient_exact` at the lifted compiled angles. `eta` never enters the optimization; it appears only in the post-hoc `nat_report` acceptance field. Under the selected D1 model the deployed conditional distribution is identical to the compiled one, so there is nothing for "noise-aware" training to adapt to. `run_nat.py` then calls `run_matched_continuation` twice with byte-identical arguments to produce arms A and B; their agreement at `0.0` is guaranteed by determinism and does not test the plan's control ("NAT versus equal-budget continued ideal optimization"), because both arms are the same procedure. The docs hedge ("not a noisy-efficacy claim"), but the ledger presents two arms where there is one, and the owner-explanation and prediction notes describe the control as if it could fail. The honest label is "quantization-aware ideal continuation, run twice".

Same structural point for the comparison "deployed" arm: `apply_compiled_density(compiled, eta=eta)` differs from the compiled arm only by the scalar `eta**n`, so the compiled-to-deployed "noise TVD" is 0 by construction, not by measurement.

### F5. The photonically deployed ring models are 3-step small-angle smoke runs, not the D3 profile (RING-04)

`registered_v3_ring_photonic_*_final3.json` carry `initialization: small_angle, steps: 3, run_kind: smoke`. The rings study says the smoke runs are "historical context, not primary D3 evidence", but RING-04 and the README describe them as "registered n=4 spatial and Hamming ring smoke evaluations" without saying the deployed model is essentially its random initialization. The only ring models that were trained (n=6/8, 300 steps, parity init) were never deployed.

### F6. Main-run fit quality is not reported anywhere

The 20 n=6/n=8 main artifacts show the MMD^2 loss falling by two orders of magnitude while total variation to the training target stays at 0.51 to 0.61 (test 0.55 to 0.74). The rings study table reports only the n=4 smoke numbers. The low MMD^2 is a bandwidth effect (sigma = 0.5 sqrt(n) keeps only low-order Walsh moments; the sigma = 0.1 spatial kernel is nearly diagonal), so the loss alone misleads. The TVD/marginal panel for the main runs should be surfaced alongside the loss.

### F7. Rail convention is documented inconsistently

`docs/v4-plan-train-classical-deploy-photonic.md` sec 3.2 and the owner explanation (WRITE-07) state "Logical 0 is (1,0)". The implemented readout in `deploy/fock.py::_valid_bitstring`, `encoding/dual_rail.py`, and the physical manifests use `(0,1) -> 0`, `(1,0) -> 1`. The direct controls pass under the code's convention, so the code is self-consistent; the owner-authored note and the binding plan state the opposite of what was validated.

### F8. Several `PASS` controls are self-consistency of one code path

- NULL-06: `heralded_cz_attempts_per_sample` is compared with the same formula retyped in the script; `cp_residual` compares two helpers that call each other. Residual 0.0 is guaranteed.
- NULL-03: `apply_compiled_density` with no pair gates applies only single-qubit maps to a product state; factorisation is by construction.
- `hamming_mmd2_crosscheck`: "direct" and "trainer_objective" are the same expression (`delta @ gaussian_hamming_matrix @ delta`); only the Walsh route is independent.
- `test_density_path_does_not_construct_embedded_4n_square_superoperator` greps the source text for the string `4**n`.

These are pipeline checks under the repo's own null-result gate and should be labelled that way rather than as passed controls.

### F9. Smaller defects

- `deploy/erasure.py`: with a non-empty `retained` set the output no longer sums to 1 (0.6 for one retained qubit at eta 0.5, gate_success 0.8); the probability that a retained qubit was erased is silently dropped rather than conditioned on or added to `FAILURE`. Only the `retained=None` case is tested.
- `deploy/maps.py::_tomography_output` line 144 is dead code (`... if False else None`), and the docstring claims one-body coefficients are "averaged over compatible settings" while the loop overwrites them.
- `classical/trainer.py::run` evaluates the objective and full Jacobian twice per step (once for the update, once for the history), doubling training cost.
- `experiments/rings.py::train_rings` special-cases the magic commit string `"72e8079"`.
- `scripts/v4_tcdp/validate_artifacts.py` checks only JSON parse, finiteness and `payload_sha256`; "406 JSON, 0 failures" says nothing about the content of the artifacts.

## Second pass: sibling inventory, retraining, replay and eight-cell comparison

### F10. The n=9 "deployed" arms have acceptance masses of 1e-13 to 1e-11, and no document reports it (COMPARE-01, COMPARE-03, COMPARE-04)

In `results/v4_tcdp/sibling_comparisons/closure_20260909_final/`, the seven n=9 cells report `acceptance_mass` between `2.85e-13` and `1.39e-11`, i.e. `7e10` to `3.5e12` source attempts per accepted sample. The "common 20,000 accepted-sample evaluation budget" (COMPARE-03) therefore corresponds to 1e15 to 1e16 attempts. This is the single most important number a "deploy photonically" study produces for these cells and it appears in no report; `docs/v4-backend-comparison.md` says only that acceptance is "reported separately". The eight postselected CP gates on a 9-qubit lattice make the model-derived deployment physically vacuous, and the write-up should say so in numbers.

### F11. `support_validity` failure is far worse on the sibling cells

The n=9 targets have 493 to 505 zero-mass states out of 512 (512 samples, 7 to 19 distinct outcomes). True `sum_{p>1e-6} q` for the deployed arms is 0.012 to 0.293; every artifact reports `1.0`. TVD to target is 0.85 to 0.99 for all seven cells, so the registered sibling models are essentially disjoint from their targets after 20 source steps. Fine for a smoke rerun, but the comparison reports do not say it.

### F12. Inventory labels never-run rows `exact_reproduction` (REPRO-05)

`sibling_inventory.json` assigns `exact_reproduction` by keyword heuristic to six rows, all with `execution_state: not_run`, including `ghosh_kim_large_n_sampled` (n=20, never rerun) and `qiskit_validation_report_smoke` (no safe checkpoint; the evidence note itself calls it blocked). REPRO-05 says "no unperformed reproduction is claimed"; the disposition name claims exactly that. Rename the pre-run state (e.g. `exact_reproduction_candidate`) or set it only after a run.

### F13. Retraining adapter installs a `yaml` stub that returns `{}`

`scripts/v4_tcdp/retrain_sibling.py::_isolated_source_import` puts a fake `yaml` module with `safe_load = lambda _: {}` into `sys.modules` when PyYAML has not been imported yet. The sibling's `iqp_bp.config` uses `yaml.safe_load` for `base.yaml` and `schema.yaml`. The exercised `run_training.run(config)` path does not go through those loaders, so the recorded training_smoke evidence is unaffected, but any future source path that validates against the schema would silently validate against an empty one. A "faithful source retraining" adapter should fail loudly rather than stub a dependency.

### F14. Replay "deployed" arm is the compiled arm at eta=1

`scripts/v4_tcdp/replay_sibling.py` sets `deployed = compiled` and evaluates with the default `eta=1.0`, then reports `compiled_deployed_tvd` (identically 0) and a "deployed acceptance mass". The docs quote the training_smoke replay's deployed acceptance as `1.0000000000000002`; that is the lossless model success of a near-zero-angle circuit, not a deployment number.

Also confirmed in this pass: `compare_sibling_backends.py` hard-codes `"status": "PASS"` in its `controls` and `source_checks` blocks (defensible, since every check above them raises on failure) and records `metric_mutation_panel: "not recomputed per sibling cell"`, so the sibling cells carry no mutation controls at all. The `_build_cp_insertion_core` PERM adapters and the literature review's citations (S1 to S16) checked out.

## Test suite

`venv/Scripts/python.exe -m pytest -q --basetemp=<writable dir>` with `PCVL_PERSISTENT_PATH` redirected: `697 passed, 1 skipped in 355.80s`. The reported tally is confirmed. (A run without `--basetemp` in this sandbox produced 43 `tmp_path` `PermissionError`s under `%TEMP%\pytest-of-cuqui`; environmental, not a code defect.) Note that the suite passing does not contradict F1 to F4: the tests assert the hard-coded values (`test_comparison.py:115`) and never exercise the parent-side RSS sampler against a growing child.
