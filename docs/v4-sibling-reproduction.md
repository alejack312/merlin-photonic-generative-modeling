# v4 sibling inventory and reproduction boundary

The Phase 26 inventory is a provenance and replay-planning artifact. It is not scientific certification, a claim that any source result has been independently reproduced, or evidence that a photonic backend supports every source circuit.

The read-only inventory covers both `src/iqp_bp` and `src/iqp_mmd`, configuration files, result families, dataset/checkpoint references, direct imports, capability keywords, environment versions, and SHA-256 hashes. The inspected sibling checkout is pinned to `f6d6ebe87e4ee1de10893c6ea2f0ffa367493336`; local result/data/checkpoint artifacts are hashed separately because they are not supplied by that source commit.

Run the inventory from the MerLin repository root with:

```powershell
venv\Scripts\python.exe scripts\v4_tcdp\inventory_sibling.py
```

It writes [sibling_inventory.json](../results/v4_tcdp/sibling_inventory.json), [source_contract.json](../results/v4_tcdp/sibling/source_contract.json), and one reference manifest per inventoried Gaussian-related configuration below `results/v4_tcdp/sibling/`. The command only reads the sibling checkout and writes the MerLin output directory. It does not download, publish, reset, stash, commit, or modify sibling files.

The current local observation recorded 81 sibling source files, 30 parsed configuration files, and 1,314 result/data/checkpoint artifacts. The top-level `data/` directory is absent in this checkout; the inventory records that fact separately and checks configured paths individually. The registered `training_smoke` product-Bernoulli input is regenerable from the source recipe and seed, and is recorded separately from external or unverified inputs.

Each source row has one of four dispositions: `exact_reproduction`, `adapted_reproduction`, `reference_only`, or `blocked`. `execution_state: not_run` is retained when the row has not yet undergone replay. `reference_only` preserves a source study whose scale/backend/capability is not being silently changed; `blocked` preserves the exact missing input or capability. A changed field must be listed for an adaptation.

The safe boundary accepts JSON/YAML/CSV and NumPy `.npy`/`.npz` metadata reads. NumPy loads always use `allow_pickle=False`; Python pickle, joblib, torch, and dill artifacts are rejected. Manifest import reads JSON metadata only and never follows or deserializes a referenced object. A later replay must validate the manifest, input hashes, source defaults, data order/splits, graph/generator rows, theta, estimator mode, and environment before executing.

The inventory supports faithful replay planning. It does not certify the sibling’s scientific claims, validate every historical aggregate, prove dataset rights, or establish physical photonic realizability.

## Bounded checkpoint replay

`scripts/v4_tcdp/replay_sibling.py` safely replays the available `training_smoke` step-4 NPZ checkpoint through the ideal compiler and CP-map density path. It preserves the source `G`, theta, step, source SGD loss, Gaussian bandwidth, source commit and checkpoint hash, and writes separate raw/compiled/deployed vectors under `results/v4_tcdp/sibling_replays/`. The frozen raw/compiled TVD is `3.46e-16` and the deployed acceptance mass is `1.0000000000000002`.

This remains recorded as `adapted_reproduction`: the source checkpoint is replayed, while checkpoint replay is not itself faithful retraining. The registered product-Bernoulli training-smoke input was regenerated from the source recipe/seed, and [retraining_evidence.json](../results/v4_tcdp/sibling_retraining/training_smoke/retraining_evidence.json) records an isolated source-trainer rerun with exact theta/loss agreement for all five trajectory rows. Bandwidth/marginal and Ghosh–Kim checkpoint retraining remain unexecuted and are not called reproduced.

The retraining adapter is intentionally opt-in because it imports source code. Run it with `--sibling-root`, the exact source `--config`, and an output directory outside the sibling checkout. The normal test suite exercises portable contract checks; the source trajectory comparison is run explicitly when the pinned sibling inputs are present.
