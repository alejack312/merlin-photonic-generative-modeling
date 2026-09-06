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

The all-registered replay command was started but stopped before completion because the large-`n` exact raw replay remained CPU-bound. Its partial output is not used as completed row evidence. No faithful source retraining or matched comparison is claimed by this bounded repair note.

## Changed evidence surface

- `scripts/v4_tcdp/replay_sibling.py`: registered checkpoint selection and manifest provenance/output inventories.
- `scripts/v4_tcdp/retrain_sibling.py`: command provenance in aggregate and per-cell faithful-retraining manifests.
- `results/v4_tcdp/sibling_replays/registered/`: partial blocked-row output from the interrupted sweep; not a complete batch result.

Open external inputs remain the registered rows without safe NPZ checkpoints. Physical/source validation prerequisites for matched comparisons remain un evidenced, so no comparison extension is recorded here.
