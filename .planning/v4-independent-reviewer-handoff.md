# v4.0 independent reviewer handoff

## Scope

Review the additive v4.0 implementation against the binding plan, additive design, audit, and the five-state evidence ledger. Treat scientific interpretation as provisional. Do not modify the sibling repository, merge, publish, or launch unapproved sweeps.

## Git and provenance

- Repository: `C:\Users\cuqui\merlin-quantum-case-study`
- Base: `de80e9313beed614528fd6332b2f78aab83c0b50` (`fix/narrow-circuit-claim`)
- Review target: current `HEAD` on `codex/v4-implementation` (record the exact commit with `git rev-parse HEAD`; this handoff is part of that final commit).
- Sibling: `C:\Users\cuqui\iqp-mmd-barren-plateau`
- Required sibling checkpoint: `f6d6ebe87e4ee1de10893c6ea2f0ffa367493336`
- Verified sibling state: branch `alejack312`, clean, ahead of its remote by one commit; no sibling edits were made.

## Reproduction commands

Run from the photonic repository root:

```powershell
venv/Scripts/python.exe -m pytest -q tests/v4_tcdp
venv/Scripts/python.exe -m compileall -q scripts/v4_tcdp
venv/Scripts/python.exe docs/audits/2026-09-06-v4-implementation-probes.py
venv/Scripts/python.exe docs/audits/2026-09-06-v4-repair-review-probes.py  # pre-fix counterexamples; expected to raise after the repairs
venv/Scripts/python.exe scripts/v4_tcdp/validate_deploy.py
venv/Scripts/python.exe scripts/v4_tcdp/inventory_sibling.py
venv/Scripts/python.exe scripts/v4_tcdp/replay_sibling.py results/v4_tcdp/sibling/training_smoke_configs_experiments_training_smoke_yaml/manifest.json --sibling-root C:/Users/cuqui/iqp-mmd-barren-plateau --output-root results/v4_tcdp/sibling_replays
$env:MERLIN_SIBLING_ROOT='C:/Users/cuqui/iqp-mmd-barren-plateau'; venv/Scripts/python.exe -m pytest -q tests/v4_tcdp/test_sibling_retrain.py
venv/Scripts/python.exe scripts/v4_tcdp/retrain_sibling.py --sibling-root C:/Users/cuqui/iqp-mmd-barren-plateau --config C:/Users/cuqui/iqp-mmd-barren-plateau/configs/experiments/training_smoke.yaml --output-root results/v4_tcdp/sibling_retraining/training_smoke
venv/Scripts/python.exe scripts/v4_tcdp/compare_backends.py results/v4_tcdp/rings/rings_hamming/n6_seed0_main --eta 0.9 --output results/v4_tcdp/comparisons/rings_hamming_n6_seed0_eta09.json
venv/Scripts/python.exe scripts/v4_tcdp/run_nat.py --n 4 --seed 0 --steps 150 --matched-continuation --output results/v4_tcdp/nat/n4_seed0_primary.json
```

The required full suite is:

```powershell
$env:PCVL_PERSISTENT_PATH = Join-Path ([System.IO.Path]::GetTempPath()) 'merlin-v4-perceval'
venv/Scripts/python.exe -m pytest -q
```

Observed result after the second repair pass: focused v4 suite `144 passed, 2 skipped`; full suite `652 passed, 1 skipped in 362.20s (0:06:02)`. A persistent Perceval path override was used so collection could write its log; without that override, collection can fail when the default `AppData\Local\quandela\perceval-quandela\logs\perceval.log` is unavailable. The default suite no longer requires the sibling checkout; the source integration is explicit via `MERLIN_SIBLING_ROOT`. These are environment notes, not relaxed acceptance gates.

## Evidence locations

- [.planning/v4-requirement-evidence.md](v4-requirement-evidence.md) — 52 rows, PASS/FAIL/INCONCLUSIVE/NOT IMPLEMENTED/BLOCKED, with next actions and dependencies.
- [docs/v4-tcdp-study.md](../docs/v4-tcdp-study.md) — synthesis and scope limits.
- [docs/v4-rings-study.md](../docs/v4-rings-study.md) — n=4 ring smoke evidence.
- [docs/v4-sibling-reproduction.md](../docs/v4-sibling-reproduction.md) — inventory and adapted checkpoint replay boundary.
- [docs/v4-deployment-study.md](../docs/v4-deployment-study.md) — compiler/map/full-Fock limits.
- [docs/v4-backend-comparison.md](../docs/v4-backend-comparison.md) — matched raw/compiled/deployed artifacts.
- [docs/audits/2026-09-06-v4-repair-review.md](../docs/audits/2026-09-06-v4-repair-review.md) — nine-finding independent repair review.
- `results/v4_tcdp/` — canonical JSON/NPZ/NPY artifacts and hashes.

## Review focus and remaining gaps

1. Confirm that all PASS rows are limited to their stated bounded evidence, especially analytic CP-map reconstruction versus actual Perceval absolute-outcome reconstruction.
2. Confirm that raw, compiled, and deployed vectors remain distinct and that acceptance is not conflated with conditional quality.
3. Audit the negative optical signs, alpha-key winding, MSB bit order, Hamming kernel distance (not squared distance), and one-final-normalization composition.
4. Check that the adapted `training_smoke` checkpoint replay is not called faithful retraining.
5. Check the repaired R01–R09 contracts: finite/complete retraining trajectories, exact requested config, scoped source identity, ring namespaces, stale-array rejection, explicit spatial geometry, two matched NAT arms, full-Fock aggregation, and optional sibling integration.
6. Check the recorded D1/D2/D3 choices, fixed-photon loss boundary, owner controls, completed n=6/8 ring main profiles, absent photonic ring adapter, incomplete NAT production metric panel, and absent independent review against the ledger.
7. Verify no legacy pipeline or sibling file changed, and no unapproved sweep or merge occurred. The 20 ring main artifacts are within the registered n=6/n=8 five-seed/300-step budget.

## Decisions recorded from owner (2026-09-06)

- D1: fixed-photon `g2=0` with explicit uniform per-photon loss; multiphoton `g2>0` claims remain outside scope.
- D2: discrete `0.1*j` alpha-key neighbor search with continuous single-qubit angles and exact analytic gradients.
- D3: sibling-style data-dependent parity initialization at scale `0.1` for primary profiles; small-angle and uniform remain ablations; deterministic duplicates are not independent replicas.

These decisions unlock implementation, but do not certify physical full-Fock composition, NAT efficacy, or owner interpretation. The training-smoke source trajectory is independently retrained with the regenerated source-recipe data; other sibling rows remain separately dispositioned.
