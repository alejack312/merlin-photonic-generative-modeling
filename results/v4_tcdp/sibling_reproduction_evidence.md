# v4.0 sibling reproduction bounded evidence

Scope: sibling replay/retraining adapter repair only. This note is isolated evidence; the central v4 ledger and shared synthesis documents are unchanged.

## Source identity

- Sibling checkout: `C:\Users\cuqui\iqp-mmd-barren-plateau`
- Branch: `alejack312`
- HEAD: `f6d6ebe87e4ee1de10893c6ea2f0ffa367493336`
- Source tree identity: `12843f05ea590fae6c3f007c4d681f93075dcbbc`
- Source worktree: clean at verification; no source files were modified.

## Bounded checks

Command:

```text
venv/Scripts/python.exe -m pytest -q tests/v4_tcdp/test_sibling_replay.py
```

Result: `4 passed in 66.96s`.

The regression was caused by requiring a `checkpoints` directory before validating a registered `step_*.npz`. The adapter now accepts any registered safe `step_*.npz`, then performs strict `G`, `theta`, `step`, and finite-loss validation. This preserves rejection of malformed checkpoints while supporting the portable fixture and registered evidence contract.

Required REPRO-03 profile coverage:

- `bandwidth_marginal_sweep`: stopped after raw exact output for the registered `sigma9`, step-20 checkpoint; the stopped manifest records the source checkpoint path/hash, source config/manifest hashes, attempted command, and partial `raw.npy` hash.
- `ghosh_kim_small_n`: completed bounded adapted checkpoint replay for the registered `sigma9`, step-20 checkpoint; the manifest records raw/compiled/deployed outputs, source checkpoint/config/manifest hashes, `raw_compiled_tvd=0.021421552593069916`, and `deployed_acceptance_mass=8.360199399249953e-13`.
- Unavailable checkpoint inputs: blocked manifests exist for `anti_concentration_validation` and `qiskit_validation_report_smoke`. Each names the exact expected sibling checkpoint glob, available non-checkpoint evidence, and attempted command.

The all-registered replay command was stopped before completion because exact replay remained CPU-bound. The required profiles are therefore represented by one completed adapted replay and one stopped partial artifact, not by a completed sweep. No faithful source retraining or matched comparison is claimed by this bounded repair note.

## Changed evidence surface

- `scripts/v4_tcdp/replay_sibling.py`: registered checkpoint selection and manifest provenance/output inventories.
- `scripts/v4_tcdp/retrain_sibling.py`: command provenance in aggregate and per-cell faithful-retraining manifests.
- `results/v4_tcdp/sibling_replays/required_profiles/`: stopped partial manifests for both required REPRO-03 profiles and blocked manifests for unavailable checkpoint inputs.

Open external inputs remain the registered rows without safe NPZ checkpoints. Physical/source validation prerequisites for matched comparisons remain un evidenced, so no comparison extension is recorded here.

## Exact-row audit snapshot

The current inventory registers six exact-reproduction rows. Their isolated evidence/disposition is:

| Source row | Registered input state | Evidence disposition |
| --- | --- | --- |
| `training_smoke` | five safe NPZ checkpoints; source recipe is regenerable | faithful source retraining is recorded under `results/v4_tcdp/sibling_retraining/training_smoke/` |
| `bandwidth_marginal_sweep` | twenty safe NPZ checkpoints across four bandwidth runs | stopped partial raw replay at `sigma9`, step 20; no compiled/deployed claim |
| `ghosh_kim_small_n` | fifteen safe NPZ checkpoints across three bandwidth runs | adapted checkpoint replay complete at `sigma9`, step 20; source target data is not exported |
| `ghosh_kim_large_n_sampled` | nine safe NPZ checkpoints; `n=20` sampled source profile | not rerun: bounded compiled-density adapter rejects this scale before unsafe density allocation; no large exact replay was attempted in this pass |
| `anti_concentration_validation` | no safe NPZ checkpoint; JSON/CSV/plots only | blocked manifest names `results/validation/checkpoints/*.npz` as the missing input |
| `qiskit_validation_report_smoke` | no safe NPZ checkpoint; QASM/raw JSON/results only | blocked manifest names `results/qiskit_validation_report_smoke/checkpoints/*.npz` as the missing input |

This snapshot distinguishes source retraining, adapted frozen-checkpoint replay, stopped partial output, and unavailable/scale-blocked inputs. No exact distribution is inferred from moments or non-checkpoint summaries.
