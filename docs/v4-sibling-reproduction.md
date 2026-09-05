# v4 sibling inventory and reproduction boundary

The Phase 26 inventory is a provenance and replay-planning artifact. It is not scientific certification, a claim that any source result has been independently reproduced, or evidence that a photonic backend supports every source circuit.

The read-only inventory covers both `src/iqp_bp` and `src/iqp_mmd`, configuration files, result families, dataset/checkpoint references, direct imports, capability keywords, environment versions, and SHA-256 hashes. The inspected sibling checkout is pinned to `f6d6ebe87e4ee1de10893c6ea2f0ffa367493336`; local result/data/checkpoint artifacts are hashed separately because they are not supplied by that source commit.

Run the inventory from the MerLin repository root with:

```powershell
venv\Scripts\python.exe scripts\v4_tcdp\inventory_sibling.py
```

It writes [sibling_inventory.json](../results/v4_tcdp/sibling_inventory.json), [source_contract.json](../results/v4_tcdp/sibling/source_contract.json), and one reference manifest per inventoried Gaussian-related configuration below `results/v4_tcdp/sibling/`. The command only reads the sibling checkout and writes the MerLin output directory. It does not download, publish, reset, stash, commit, or modify sibling files.

The current local observation recorded 81 sibling source files, 30 parsed configuration files, and 1,314 result/data/checkpoint artifacts. The top-level `data/` directory is absent in this checkout; the inventory records that fact separately and checks configured paths individually. It does not fabricate a dataset when a path or feature/split provenance is missing.

Each source row has one of four dispositions: `exact_reproduction`, `adapted_reproduction`, `reference_only`, or `blocked`. `execution_state: not_run` is retained when the row has not yet undergone replay. `reference_only` preserves a source study whose scale/backend/capability is not being silently changed; `blocked` preserves the exact missing input or capability. A changed field must be listed for an adaptation.

The safe boundary accepts JSON/YAML/CSV and NumPy `.npy`/`.npz` metadata reads. NumPy loads always use `allow_pickle=False`; Python pickle, joblib, torch, and dill artifacts are rejected. Manifest import reads JSON metadata only and never follows or deserializes a referenced object. A later replay must validate the manifest, input hashes, source defaults, data order/splits, graph/generator rows, theta, estimator mode, and environment before executing.

The inventory supports faithful replay planning. It does not certify the sibling’s scientific claims, validate every historical aggregate, prove dataset rights, or establish physical photonic realizability.
