# Sibling dataset-loader audit — 2026-09-28

## Scope and provenance

This is a read-only check requested by the owner. The supplied path
`C:\\Users\\cuqui\\iqp-mmd-barren-plateau\\src\\iqp\\_mmd\\datasets` does not exist; the actual package path is
`C:\\Users\\cuqui\\iqp-mmd-barren-plateau\\src\\iqp_mmd\\datasets`.

The sibling checkout was clean on branch `alejack312` at commit
`f6d6ebe87e4ee1de10893c6ea2f0ffa367493336`, matching the pinned inventory
commit. No sibling files were modified, downloaded, regenerated, or substituted.

The available loader modules are `blobs.py`, `dwave.py`, `genomic.py`,
`ising.py`, `mnist.py`, and the generic CSV loader in `loaders.py`.

Source-version observations:

- D-Wave's loader pins Zenodo record `7250436` in its URL.
- Genomic's loader pins INRIA GitLab commit `29c1ef7cf242e842df4360abae2eebeec995f40e`.
- MNIST uses `torchvision.datasets.MNIST(..., download=True)` without a dataset revision pin.
- Blobs and Ising are generated through optional runtime dependencies; they do not read a committed source data file.
- The local CSVs are ignored/generated artifacts and have no sidecar linking their bytes to a source revision. Their presence alone is therefore not treated as faithful source-version proof.

## Blocked or missing-input rows

| Inventory row | Result | Read-only finding |
|---|---|---|
| `forge_gradient_plateau_smoke` | **unrelated** | The row uses `product_bernoulli` from `src/iqp_bp/experiments/data_factory.py`, not an `iqp_mmd.datasets` loader. Its exact missing inputs are `results/gradient_labels/gradient_labels.jsonl` and the run output directory `results/forge_gradient_plateau_smoke/`; a dataset loader cannot resolve the missing gradient-label artifact. |
| `forge_sprint` | **unrelated** | The row also generates `product_bernoulli` through `iqp_bp`. The missing item is the run output directory `results/forge_sprint/`, not a file-backed dataset. |
| `koshik_raw_repro` | **unrelated** | The row's runtime data contract is `product_bernoulli` plus data-dependent Ising initialization in `iqp_bp`; the missing items are `results/koshik_raw_repro/` and the declared root `checkpoints/` directory. The sibling dataset loaders do not provide the required checkpoint/run artifact. |
| `qiskit_validation` | **unrelated** | The data is generated `product_bernoulli`; the missing row input is `results/qiskit_validation/`. The required `qiskit`/`qiskit-aer` simulator capability is separate from the dataset loaders and was not changed by this audit. |
| `scaling_ac_diverse` | **unrelated** | The row uses generated `product_bernoulli`; its declared `checkpoints/` capability is absent at the sibling root. The existing `results/scaling_ac_diverse/` directory does not turn the row into a faithful loader resolution. |
| `scaling_ac_holdout_families` | **unrelated** | Same boundary: generated `product_bernoulli`, declared root `checkpoints/` absent, and the dataset loaders are not the blocker. `results/scaling_ac_holdout_families/` exists but does not supply the missing declared capability/provenance. |
| `scaling_ac_holdout_n` | **unrelated** | Same boundary: generated `product_bernoulli`, declared root `checkpoints/` absent, and the dataset loaders are not the blocker. `results/scaling_ac_holdout_n/` exists but does not supply the missing declared capability/provenance. |
| `scaling_ac_smoke` | **unrelated** | The expected checkpoint is present at `results/scaling_ac_smoke/checkpoints/complete_graph_n4_gaussian_uniform_seed0.npz`, but the inventory row's declared root `checkpoints/` is absent. This is a checkpoint/inventory-state issue, not a dataset-loader issue; no row status was silently rewritten. |
| `scaling_v1` | **unrelated** | The row uses generated `product_bernoulli`; the missing exact item is `results/scaling_v1/`. No `iqp_mmd.datasets` file is required to resolve that output artifact. |
| `scaling_v2` | **unrelated** | The row uses generated `product_bernoulli`; the missing exact item is `results/scaling_v2/`. No `iqp_mmd.datasets` file is required to resolve that output artifact. |
| `anti_concentration_validation_from_checkpoint` | **unrelated** | The configured checkpoint is present at `results/scaling_ac_smoke/checkpoints/complete_graph_n4_gaussian_uniform_seed0.npz`, and `results/validation_from_checkpoint/` is present. The row's dependency is checkpoint validation/provenance, not a sibling dataset loader; the checkpoint metadata contains `source: run_scaling`, not a source commit/tree identity. |
| `hyperparameters` | **still missing** | The exact configured graph input `datasets/ising/scale_free_dataset/graph.adjlist` is absent. `ising.py` can generate a new scale-free graph, but that is not the named source file and cannot be substituted. |
| `pauli_estimator_datasets` | **still missing** | The loader code exists, but the complete big-n input set is not source-version-resolved. Present: `datasets/dwave/dwave_X_train.csv` (SHA-256 `caaef2ce302f7c320e35015d38809da091bfdd4b7e431760726eac92615d7416`) and `datasets/dwave/dwave_X_test.csv` (SHA-256 `32460106cc78ae5a19be3dd7595fe11a78de9e118cd4b92584785a1035687a9f`), plus `datasets/genomic/805_SNP_1000G_real_train.csv` (SHA-256 `5fb070225749a3b7430adad1200d2ba5ab532a71cb17bdb8baf166314d1d80c3`) and `datasets/MNIST/x_train.csv` (SHA-256 `0b556818d11891168c87013dbac3a385d992b89f1510cc1089ac8551e43ead0b`). Still missing: `datasets/genomic/805_SNP_1000G_real_test.csv`; `datasets/MNIST/x_test.csv`; `datasets/MNIST/y_train.csv`; `datasets/MNIST/y_test.csv`; the `spin_glass` and `scale_free` dataset artifacts/load contracts; and a sidecar tying the ignored local files to the pinned D-Wave/genomic/MNIST source versions. |
| `validate_n16_checkpoints` | **unrelated** | Both configured checkpoints are present: `results/iqp_mmd_ac_investigation/checkpoints/ising_n16_iters1000_seed666.npz` and `results/iqp_mmd_ac_investigation/checkpoints/spin_blobs_n16_iters1000_seed666.npz`. Their metadata identifies `source: investigate_iqp_mmd.py` but contains no source commit/tree identity. The remaining issue is exact checkpoint provenance/validation execution, not the availability of the dataset loader. |

## Conclusion

The loader path is available under the corrected `iqp_mmd` package name, but it resolves none of the output-directory, checkpoint, Qiskit, or gradient-label blockers. It partially explains the available ignored D-Wave/genomic/MNIST artifacts, but the complete `pauli_estimator_datasets` row remains unresolved because required files and source-version bindings are missing. The exact Ising graph input remains missing. No sibling-repo change was made.
