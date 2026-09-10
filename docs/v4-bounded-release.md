# v4.0 bounded release — 2026-09-10

The selected release contains additive classical IQP training, frozen ring and sibling comparisons, qualified small-circuit optical simulations, NAT continuation controls, and corrected evidence/provenance checks. Closure of this selected scope does **not** mean the original full v4.0 scientific acceptance criteria have passed. The wider requirements retain their statuses in the [ledger](../.planning/v4-requirement-evidence.md).

## What the results show

The main ring fits remain imperfect. Close agreement between implementations establishes numerical consistency within their stated models; it does not establish a good target fit or photonic advantage. TVD is total variation distance from the supplied target histogram: zero is exact agreement and one is maximal disagreement. Support validity is the conditional output probability on states whose supplied target probability exceeds `1e-6`. For these finite empirical targets it is not a certificate of the unknown population support, and it is not a fraction of observed optical samples.

### Rings

The table uses seed 0 for each registered profile. The 20 main artifacts contain deterministic duplicates under the selected initialization; five seed labels do not supply five independent statistical replications. The two n=4 profiles are three-step smoke runs. The n=6/n=8 profiles are the trained main runs.

| Profile | Raw train TVD | Raw held-out TVD | Raw support validity | Analytic deployed TVD | Expected attempts for 20,000 accepted outcomes |
|---|---:|---:|---:|---:|---:|
| Hamming n=4 smoke | 0.8646 | 0.8646 | 0.1354 | 0.8667 | 9.63 million |
| Spatial n=4 smoke | 0.8645 | 0.8645 | 0.1355 | 0.8666 | 9.63 million |
| Hamming n=6 main | 0.5539 | 0.5673 | 0.5438 | 0.5544 | 2.65 billion |
| Spatial n=6 main | 0.5118 | 0.5493 | 0.6269 | 0.5112 | 1.53 billion |
| Hamming n=8 main | 0.6052 | 0.7348 | 0.4399 | 0.6041 | 360.97 billion |
| Spatial n=8 main | 0.5809 | 0.6869 | 0.5133 | 0.5814 | 86.27 billion |

The [22 committed comparison cells](../results/v4_tcdp/corrections_20260910/metrics_v5/) report both kernels, first/second-order marginals, coverage, support, and acceptance separately. Ring deployment estimates here use the quantized analytic CP-map reference at `eta=1`; they are not direct n=6/n=8 optical simulations. The held-out column uses the frozen raw model and test histogram, not the training target used by the comparison panel.

### Sibling/substrate comparison

The eight registered available cells compare the pinned sibling IQP model, equivalent local IQP implementation, unquantized compilation control, quantized compilation, and fixed-photon analytic deployment at `eta=0.9`, with matched parameters and supplied targets. These are population-vector comparisons, not sampled hardware experiments.

| Cell | Analytic deployed TVD | Support validity | Expected attempts for 20,000 accepted outcomes |
|---|---:|---:|---:|
| n=6 training smoke | 0.9351 | 1.0000 | 37,634 |
| n=9 bandwidth sigma=1 | 0.9883 | 0.0118 | 2.59 × 10^16 |
| n=9 bandwidth sigma=3 | 0.9157 | 0.0965 | 1.28 × 10^16 |
| n=9 bandwidth sigma=9 | 0.9908 | 0.0170 | 7.89 × 10^15 |
| n=9 bandwidth sigma=27 | 0.9733 | 0.0315 | 1.44 × 10^15 |
| n=9 Ghosh–Kim sigma=1 | 0.8509 | 0.2933 | 1.02 × 10^16 |
| n=9 Ghosh–Kim sigma=3 | 0.9766 | 0.0234 | 7.02 × 10^16 |
| n=9 Ghosh–Kim sigma=9 | 0.9138 | 0.1626 | 6.17 × 10^16 |

The n=6 target has full support, so its support validity of one coexists with poor fit. The seven n=9 targets have only 7–19 supported states out of 512. Their model acceptance probabilities span approximately `2.85e-13`–`1.39e-11`, or 72 billion–3.51 trillion expected attempts per accepted outcome. These costs follow from `N / acceptance_probability` under independent attempts; 20,000 is a nominal evaluation budget, not a record of collected shots. No attempt rate, wall-clock hardware time, or sampling confidence interval is established. See the [committed eight-cell summary](../results/v4_tcdp/sibling_comparisons/correction_20260910_v5/summary.json).

## Direct optical simulation boundary

- [Perceval controls](../results/v4_tcdp/deploy/physical_control_manifest_20260909_final3.json): the registered n=2/n=3 no-gate, bystander, and shared-gate cases, with absolute accepted mass and final-only projection checks.
- [Spatial](../results/v4_tcdp/deploy/registered_v3_ring_photonic_spatial_n4_seed0_smoke_20260909_final3.json) and [Hamming](../results/v4_tcdp/deploy/registered_v3_ring_photonic_hamming_n4_seed0_smoke_20260909_final3.json) n=4 ring optical smoke evaluations: frozen three-step, small-angle runs.
- All eight sibling deployed arms and the larger ring comparison arms are analytic CP-map references. Their agreement is not independent full-Fock validation at those sizes. No physical hardware run is claimed.

## Final correction review and clean-checkout gate

Reviewed the correction changes through `d3d6ff6`, then fixed two demonstrated validation defects in `a732d65`: current comparison rows could omit support validity, or disagree with their arm's acceptance probability, and still pass. The new regression checks reject both. A third demonstrated defect appeared in a strict LF checkout: sibling manifests hashed Windows CRLF bytes, while Git stored LF bytes. Repair `a8db410` writes LF JSON, pins comparison line endings in Git, and corrects the eight current manifest hashes while retaining each original hash in `serialization_correction`. No optimizer, circuit, dataset, or numerical result changed.

| Repaired failure case | Release check |
|---|---|
| Replay path escapes sibling root | `test_replay_rejects_checkpoint_path_outside_sibling_root` |
| Erasure accepts invalid mass/index | Negative mass and fractional-index rejection; explicit retained-subset failure-mass conservation tests |
| Throughput becomes nonfinite JSON | `test_distribution_rejects_acceptance_that_overflows_throughput` |
| Parsed artifacts pass with invalid semantics | Full semantic regressions, including the two newly reproduced missing/conflicting metric cases |
| Resource result has incorrect provenance | Worker identity test, live 64 MiB allocation, and four current source-blob hashes checked against the committed pilot |
| Documentation overstates evidence | This summary distinguishes target fit, support, expected cost, analytic references, direct optical controls, and unperformed experiments |

Mutation tests recompute changed distributions and accepted mass and reject an injected no-op. They are software sensitivity controls, not source-model mutation experiments. Support and TVD were independently recomputed from the eight sibling payloads and 22 frozen ring runs. The [read-only release probe](audits/2026-09-10-release-probes.py) verifies 99 committed canonical evidence files, 64 sibling payload hashes, frozen ring support/TVD, and the resource source hashes.

The live memory probe touched a 64 MiB allocation in PID 40180; the allocating, measured, and worker PIDs agreed. RSS rose from 153,608,192 to 220,725,248 bytes, approximately 64 MiB. The [committed resource pilot](../results/v4_tcdp/deploy/resource_budget_correction_20260910_final2.json) records n=4/6/8/10 with an n=10 peak growth of approximately 110 MiB, below its 400 MiB bound. This is resource evidence for the analytic path, not an optical scaling proof.

Clean-checkout verification at implementation commit `a732d65`: full suite **725 passed, 1 skipped in 407.99 s**; explicit sibling integration **36 passed in 66.53 s**. The optional sibling integration is the default-suite skip and was exercised separately. The subsequent portability repair at `a8db410` adds a byte-serialization regression; final clean-checkout verification at that implementation passed **726 tests, 1 skipped in 721.70 s**, and **37 explicit sibling integration tests in 141.51 s**. Artifact validation, the release probe, compilation, and whitespace checks also pass.

Reproduction commands (Python environment must provide the repository dependencies):

```powershell
$env:PYTHONPATH=(Join-Path (Get-Location) 'src')
$env:PCVL_PERSISTENT_PATH=Join-Path $env:TEMP 'merlin-v4-release-perceval'
python -m pytest -q
$env:MERLIN_SIBLING_ROOT='C:/Users/cuqui/iqp-mmd-barren-plateau'
python -m pytest -q tests/v4_tcdp/test_sibling_inventory.py tests/v4_tcdp/test_sibling_replay.py tests/v4_tcdp/test_sibling_retrain_portable.py tests/v4_tcdp/test_sibling_retrain.py tests/v4_tcdp/test_sibling_validation_rerun.py tests/v4_tcdp/test_sibling_backend_comparison.py
python scripts/v4_tcdp/validate_artifacts.py --root results/v4_tcdp
python docs/audits/2026-09-10-release-probes.py
python scripts/v4_tcdp/resource_pilot.py --memory-probe-worker --allocation-bytes 67108864
```

The detached checkout contains only committed inputs. It reuses the installed Python 3.12 environment, with imports explicitly directed to the checkout's `src`; this is not a fresh dependency-install test. Comparison JSON uses explicit LF serialization and a Git attribute to preserve byte-hash identity across checkout settings. Resource source hashes are checked against Git blob bytes. A process-local `safe.directory` exception is limited to this checkout because the checkout creator and test account differ; no global Git trust setting was changed.

Earlier totals of 579 JSON files and 19 payload hashes included untracked working-directory artifacts. Clean verification finds 486 JSON files, 72 JSONL rows, and 18 embedded payload hashes, with zero failures. The separate release probe checks 64 sibling payload hashes. The untracked audit, temporary Perceval/pytest directories, and earlier metrics/resource/sibling versions remain preserved in the original working directory and are excluded from this release. Historical absolute producer paths in sibling summaries are provenance metadata; the probe resolves payloads relative to the committed summary directory.

## Selected scope closure and remaining research

The user selected bounded release closure on 2026-09-10. The clean verification gate passed, and the selected implementation/evidence scope is **closed for PR review**. Creating the PR does not merge, publish a package, or certify the original full scientific milestone.

The following remain outside closure, with their detailed statuses and dependencies preserved in the [requirement ledger](../.planning/v4-requirement-evidence.md): multiphoton/source-imperfection validation; general full-Fock composition and larger-n direct deployment; unavailable sibling experiments; sampled uncertainty; NAT efficacy under a distinct noise model and the unexecuted stop-rule arm; and experimental adjudication of the recorded NULL-07 hypothesis. No row is promoted merely because the software release closes. The recorded owner explanation remains owner-authored; this report does not certify unaided understanding or replace scientific interpretation.
