# v4 sibling inventory and reproduction boundary

The Phase 26 inventory is a provenance and replay-planning artifact. It is not scientific certification, a claim that any source result has been independently reproduced, or evidence that a photonic backend supports every source circuit.

The read-only inventory covers both `src/iqp_bp` and `src/iqp_mmd`, configuration files, result families, dataset/checkpoint references, direct imports, capability keywords, environment versions, and SHA-256 hashes. The inspected sibling checkout is pinned to `f6d6ebe87e4ee1de10893c6ea2f0ffa367493336`; local result/data/checkpoint artifacts are hashed separately because they are not supplied by that source commit.

Run the inventory from the MerLin repository root with:

```powershell
venv\Scripts\python.exe scripts\v4_tcdp\inventory_sibling.py
```

It writes [sibling_inventory.json](../results/v4_tcdp/sibling_inventory.json), [source_contract.json](../results/v4_tcdp/sibling/source_contract.json), and one reference manifest per inventoried Gaussian-related configuration below `results/v4_tcdp/sibling/`. The command only reads the sibling checkout and writes the MerLin output directory. It does not download, publish, reset, stash, commit, or modify sibling files.

The current local observation recorded 81 sibling source files, 30 parsed configuration files, and 1,314 result/data/checkpoint artifacts. The top-level `data/` directory is absent in this checkout; the inventory records that fact separately and checks configured paths individually. The registered `training_smoke` product-Bernoulli input is regenerable from the source recipe and seed, and is recorded separately from external or unverified inputs.

Each source row has a disposition distinguishing unrun `exact_reproduction_candidate` rows from evidenced `exact_reproduction`, `adapted_reproduction`, `reference_only`, or `blocked`. `execution_state: not_run` is retained when the row has not yet undergone replay. `reference_only` preserves a source study whose scale/backend/capability is not being silently changed; `blocked` preserves the exact missing input or capability. A changed field must be listed for an adaptation.

The safe boundary accepts JSON/YAML/CSV and NumPy `.npy`/`.npz` metadata reads. NumPy loads always use `allow_pickle=False`; Python pickle, joblib, torch, and dill artifacts are rejected. Manifest import reads JSON metadata only and never follows or deserializes a referenced object. A later replay must validate the manifest, input hashes, source defaults, data order/splits, graph/generator rows, theta, estimator mode, and environment before executing.

The inventory supports faithful replay planning. It does not certify the sibling’s scientific claims, validate every historical aggregate, prove dataset rights, or establish physical photonic realizability.

## Bounded checkpoint replay

`scripts/v4_tcdp/replay_sibling.py` safely replays the available `training_smoke` step-4 NPZ checkpoint through the ideal compiler and CP-map density path. It preserves the source `G`, theta, step, source SGD loss, Gaussian bandwidth, source commit and checkpoint hash, and writes separate raw/compiled/deployed vectors under `results/v4_tcdp/sibling_replays/`. The frozen raw/compiled TVD is `3.46e-16` and the deployed acceptance mass is `1.0000000000000002`.

This remains recorded as `adapted_reproduction`: the source checkpoint is replayed, while checkpoint replay is not itself faithful retraining. The registered product-Bernoulli training-smoke input was regenerated from the source recipe/seed, and [retraining_evidence.json](../results/v4_tcdp/sibling_retraining/training_smoke/retraining_evidence.json) records an isolated source-trainer rerun with exact theta/loss agreement for all five trajectory rows. The registered bandwidth cells are covered by [bandwidth retraining evidence](../results/v4_tcdp/sibling_retraining/closure_20260908/bandwidth_source_rerun/retraining_evidence.json), and the registered Ghosh–Kim small-n cells by [Ghosh–Kim retraining evidence](../results/v4_tcdp/sibling_retraining/closure_20260908/ghosh_kim_source_rerun/retraining_evidence.json); all eight training cells matched source theta/loss rows exactly. The exact n=6 anti-concentration validation cell is covered by [validation evidence](../results/v4_tcdp/sibling_retraining/closure_20260908/validation_source_rerun/retraining_evidence.json), with byte-identical substantive JSON/CSV outputs. Large-n sampled, Qiskit-dependent, and missing-input rows remain separately dispositioned.

The retraining adapter is intentionally opt-in because it imports source code. Run it with `--sibling-root`, the exact source `--config`, and an output directory outside the sibling checkout. The normal test suite exercises portable contract checks; the source trajectory comparison is run explicitly when the pinned sibling inputs are present.

## Registered closure reruns

The 2026-09-08 closure used the pinned sibling source at commit `f6d6ebe87e4ee1de10893c6ea2f0ffa367493336` and redirected outputs into `results/v4_tcdp/sibling_retraining/closure_20260908/`. The source runner was invoked through `PYTHONPATH` without modifying the sibling checkout:

```powershell
$env:PYTHONPATH = 'C:\Users\cuqui\iqp-mmd-barren-plateau\src'
venv\Scripts\python.exe -m iqp_bp.cli run-training configs\v4_sibling_bandwidth_retrain.yaml
venv\Scripts\python.exe -m iqp_bp.cli run-training configs\v4_sibling_ghosh_kim_retrain.yaml
venv\Scripts\python.exe scripts\v4_tcdp\validate_registered_bandwidth_rerun.py --source-root C:\Users\cuqui\iqp-mmd-barren-plateau\results\bandwidth_marginal_sweep --rerun-root results\v4_tcdp\sibling_retraining\closure_20260908\bandwidth_source_rerun --source-config C:\Users\cuqui\iqp-mmd-barren-plateau\configs\experiments\bandwidth_marginal_sweep.yaml --output results\v4_tcdp\sibling_retraining\closure_20260908\bandwidth_source_rerun\retraining_evidence.json
venv\Scripts\python.exe scripts\v4_tcdp\validate_registered_bandwidth_rerun.py --source-root C:\Users\cuqui\iqp-mmd-barren-plateau\results\ac_ghosh_kim\small_n_exact --rerun-root results\v4_tcdp\sibling_retraining\closure_20260908\ghosh_kim_source_rerun --source-config C:\Users\cuqui\iqp-mmd-barren-plateau\configs\experiments\ghosh_kim_small_n.yaml --output results\v4_tcdp\sibling_retraining\closure_20260908\ghosh_kim_source_rerun\retraining_evidence.json
$env:PYTHONPATH = 'C:\Users\cuqui\iqp-mmd-barren-plateau\src'
venv\Scripts\python.exe -m iqp_bp.cli run-validation configs\v4_sibling_validation_retrain.yaml
venv\Scripts\python.exe scripts\v4_tcdp\validate_registered_validation_rerun.py --source-config C:\Users\cuqui\iqp-mmd-barren-plateau\configs\experiments\validation.yaml --source-result C:\Users\cuqui\iqp-mmd-barren-plateau\results\validation\complete_graph_n6_seed7.json --source-csv C:\Users\cuqui\iqp-mmd-barren-plateau\results\validation\complete_graph_n6_seed7_thresholds.csv --rerun-config configs\v4_sibling_validation_retrain.yaml --rerun-result results\v4_tcdp\sibling_retraining\closure_20260908\validation_source_rerun\complete_graph_n6_seed7.json --rerun-csv results\v4_tcdp\sibling_retraining\closure_20260908\validation_source_rerun\complete_graph_n6_seed7_thresholds.csv --output results\v4_tcdp\sibling_retraining\closure_20260908\validation_source_rerun\retraining_evidence.json
```

The two training reports are `PASS`; each of their eight cells has five rows (steps 0, 5, 10, 15, 20), maximum theta/loss error `0.0`, and source identity before/after is clean. The separate validation report is also `PASS`: its substantive JSON and threshold CSV are byte-identical to the source outputs, and its source identity is clean before and after. The training validator records every resolved-config difference: output metadata is redirected, and the only other differences are explicitly checked resolver defaults (`allow_legacy_families`, inactive data-dependent-init defaults, and the diagnostics label kind); any unexpected difference fails validation. The validation rerun records its output-metadata and scalar-to-list `n_qubits` adaptations and fails on any other config difference. The training validator uses the registered trajectory tolerance `1.0e-12`; the project-wide `1.0e-16` exact tolerance remains reserved for deterministic algebraic/map identities and is not substituted for training-trajectory tolerance.

## Matched sibling-to-substrate closure

The registered training cells now have an explicit end-to-end comparison artifact:

```text
pinned sibling IQP model -> local equivalent IQP evaluator -> compiled CP map -> deployed fixed-photon map
```

Run the comparator from the MerLin root with the pinned sibling checkout available:

```powershell
venv\Scripts\python.exe scripts\v4_tcdp\compare_sibling_backends.py `
  --sibling-root C:\Users\cuqui\iqp-mmd-barren-plateau `
  --retraining-root results\v4_tcdp\sibling_retraining\training_smoke `
  --retraining-root results\v4_tcdp\sibling_retraining\closure_20260908\bandwidth_source_rerun `
  --retraining-root results\v4_tcdp\sibling_retraining\closure_20260908\ghosh_kim_source_rerun `
  --output-root results\v4_tcdp\sibling_comparisons\correction_20260910_v5 `
  --eta 0.9
```

The resulting [repaired summary](../results/v4_tcdp/sibling_comparisons/correction_20260910_v5/summary.json) contains eight `PASS` cells: one training-smoke cell, four bandwidth cells, and three Ghosh–Kim cells. Each cell stores the source samples, empirical target histogram, sibling/local raw vectors, unquantized control, quantized compiled vector, deployed vector, per-arm metrics, source/checkpoint/config hashes, and acceptance provenance. Profile names are part of each cell identity so equal `(n, sigma)` values from different source experiments cannot overwrite one another. The repaired comparison also enforces local-versus-unquantized compilation equality per cell.

The source and local IQP vectors agree within the existing probability-vector tolerance `1.0e-12` (the largest observed residual is `1.3877787807814457e-16`); deterministic acceptance scaling uses `1.0e-16`, and source trajectory evidence remains `1.0e-12`. The same source bandwidth is used in the Hamming Gaussian kernel for each cell. For `eta=0.9`, deployed acceptance is checked as `eta**n * model_success`, while the normalized deployed vector is checked against the compiled conditional vector separately.

This closes the selected sibling/substrate comparison scope, not every inventoried sibling row. The deployed arm is an analytic absolute-probability CP-map composition under fixed-photon `g2=0`, with final-only projection; it is a model-derived/reference result. It does not certify direct full-Fock behavior for n=9 or hardware performance. Large-n sampled, Qiskit-dependent, missing-input, and high-weight source rows retain their original inventory dispositions.
