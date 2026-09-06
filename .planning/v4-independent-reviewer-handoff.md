# v4.0 independent reviewer handoff

## Scope

Review the additive v4.0 implementation against the binding plan, additive design, audit, and the five-state evidence ledger. Treat scientific interpretation as provisional. Do not modify the sibling repository, merge, publish, or launch unapproved sweeps.

## Git and provenance

- Repository: `C:\Users\cuqui\merlin-quantum-case-study`
- Base: `de80e9313beed614528fd6332b2f78aab83c0b50` (`fix/narrow-circuit-claim`)
- Review head: `ddce0a8` (`codex/v4-implementation`)
- Sibling: `C:\Users\cuqui\iqp-mmd-barren-plateau`
- Required sibling checkpoint: `f6d6ebe87e4ee1de10893c6ea2f0ffa367493336`
- Verified sibling state: branch `alejack312`, clean, ahead of its remote by one commit; no sibling edits were made.

## Reproduction commands

Run from the photonic repository root:

```powershell
venv/Scripts/python.exe -m pytest -q tests/v4_tcdp
venv/Scripts/python.exe -m py_compile scripts/v4_tcdp/*.py
venv/Scripts/python.exe scripts/v4_tcdp/validate_deploy.py
venv/Scripts/python.exe scripts/v4_tcdp/inventory_sibling.py
venv/Scripts/python.exe scripts/v4_tcdp/replay_sibling.py results/v4_tcdp/sibling/training_smoke_configs_experiments_training_smoke_yaml/manifest.json
venv/Scripts/python.exe scripts/v4_tcdp/compare_backends.py results/v4_tcdp/rings/rings_hamming/n4_seed0_smoke
venv/Scripts/python.exe scripts/v4_tcdp/compare_backends.py results/v4_tcdp/rings/rings_spatial_exact/n4_seed0_smoke
```

The required full suite is:

```powershell
$env:PCVL_PERSISTENT_PATH = Join-Path ([System.IO.Path]::GetTempPath()) 'merlin-v4-perceval'
venv/Scripts/python.exe -m pytest -q
```

Observed result: `609 passed in 304.97s`. Without the override, collection fails because Perceval cannot write its default `AppData\Local\quandela\perceval-quandela\logs\perceval.log`; this is an environment failure, not a relaxed test gate.

## Evidence locations

- [.planning/v4-requirement-evidence.md](v4-requirement-evidence.md) — 52 rows, PASS/FAIL/INCONCLUSIVE/NOT IMPLEMENTED/BLOCKED, with next actions and dependencies.
- [docs/v4-tcdp-study.md](../docs/v4-tcdp-study.md) — synthesis and scope limits.
- [docs/v4-rings-study.md](../docs/v4-rings-study.md) — n=4 ring smoke evidence.
- [docs/v4-sibling-reproduction.md](../docs/v4-sibling-reproduction.md) — inventory and adapted checkpoint replay boundary.
- [docs/v4-deployment-study.md](../docs/v4-deployment-study.md) — compiler/map/full-Fock limits.
- [docs/v4-backend-comparison.md](../docs/v4-backend-comparison.md) — matched raw/compiled/deployed artifacts.
- `results/v4_tcdp/` — canonical JSON/NPZ/NPY artifacts and hashes.

## Review focus and remaining gaps

1. Confirm that all PASS rows are limited to their stated bounded evidence, especially analytic CP-map reconstruction versus actual Perceval absolute-outcome reconstruction.
2. Confirm that raw, compiled, and deployed vectors remain distinct and that acceptance is not conflated with conditional quality.
3. Audit the negative optical signs, alpha-key winding, MSB bit order, Hamming kernel distance (not squared distance), and one-final-normalization composition.
4. Check that the adapted `training_smoke` checkpoint replay is not called faithful retraining.
5. Check D1/D2/D3 gates, owner controls, missing source data, n=6/8 unlaunched profiles, absent photonic ring adapter, absent NAT, and absent independent review are visible in the ledger.
6. Verify no legacy pipeline or sibling file changed, and no large sweep or merge occurred.

## Decisions still requested from owner

- D1: fixed-photon `g2=0` versus joint source/number-sector `g2+loss` model.
- D2: discrete alpha-key optimizer versus validated continuous-angle deployment model.
- D3: data-dependent initialization recipe/scale and replication unit, or explicit exclusion from primary v4 profiles.
