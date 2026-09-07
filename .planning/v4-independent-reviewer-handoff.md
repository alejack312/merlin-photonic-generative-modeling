# v4.0 independent reviewer handoff

## Scope

Review the additive v4.0 implementation against the binding plan, additive design, audit, and the five-state evidence ledger. Treat scientific interpretation as provisional. Do not modify the sibling repository, merge, publish, or launch unapproved sweeps.

## Git and provenance

- Repository: `C:\Users\cuqui\merlin-quantum-case-study`
- Base: `de80e9313beed614528fd6332b2f78aab83c0b50` (`fix/narrow-circuit-claim`)
- Final review target: the current `git rev-parse HEAD` on `codex/v4-implementation`. This handoff intentionally does not pin a stale pre-review documentation hash.
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

Final verification in this pass: focused integration `124 passed`, explicit sibling integration `21 passed`, script compilation passed, and full suite `681 passed, 1 skipped in 396.74s (0:06:36)`. A persistent Perceval path override was used so collection could write its log; without that override, collection can fail when the default `AppData\Local\quandela\perceval-quandela\logs\perceval.log` is unavailable. These are environment notes, not relaxed acceptance gates.

## Evidence locations

- [.planning/v4-requirement-evidence.md](v4-requirement-evidence.md) — 52 rows, PASS/FAIL/INCONCLUSIVE/NOT IMPLEMENTED/BLOCKED, with next actions and dependencies; the exact integrated head is the output of `git rev-parse HEAD` in the final verification readback.
- [docs/v4-tcdp-study.md](../docs/v4-tcdp-study.md) — synthesis and scope limits.
- [docs/v4-rings-study.md](../docs/v4-rings-study.md) — n=4 ring smoke evidence.
- [docs/v4-sibling-reproduction.md](../docs/v4-sibling-reproduction.md) — inventory and adapted checkpoint replay boundary.
- [docs/v4-deployment-study.md](../docs/v4-deployment-study.md) — compiler/map/full-Fock limits.
- [docs/v4-backend-comparison.md](../docs/v4-backend-comparison.md) — matched raw/compiled/deployed artifacts.
- [docs/audits/2026-09-06-v4-repair-review.md](../docs/audits/2026-09-06-v4-repair-review.md) — nine-finding independent repair review.
- [docs/audits/2026-09-06-v4-second-repair-review.md](../docs/audits/2026-09-06-v4-second-repair-review.md) — five-finding second repair review.
- [docs/audits/2026-09-06-v4-third-repair-review.md](../docs/audits/2026-09-06-v4-third-repair-review.md) — six-finding third repair review.
- `results/v4_tcdp/` — canonical JSON/NPZ/NPY artifacts and hashes.

## Review focus and remaining gaps

1. Confirm that all PASS rows are limited to their stated bounded evidence, especially analytic CP-map reconstruction versus actual Perceval absolute-outcome reconstruction.
2. Confirm that raw, compiled, and deployed vectors remain distinct and that acceptance is not conflated with conditional quality.
3. Audit the negative optical signs, alpha-key winding, MSB bit order, Hamming kernel distance (not squared distance), and one-final-normalization composition.
4. Check that the adapted `training_smoke` checkpoint replay is not called faithful retraining.
5. Check the repaired R01–R09, S01–S05 and T01–T06 contracts: finite/complete retraining trajectories, exact requested config, fail-closed source identity, raw-content dataset hashes, complete/atomic Adam continuation, ring namespaces, multi-seed idempotence, full artifact and summary integrity, stale-array rejection, explicit spatial geometry, paired NAT binding/reporting, two matched NAT arms, full-Fock aggregation, and optional sibling integration.
6. Check the recorded D1/D2/D3 choices, fixed-photon loss boundary, owner controls, n=6/8 ring training profiles, n=4-only photonic ring boundary, registered NAT reports, and the post-integration review disposition against the ledger.
7. Check that README and `docs/technical-findings.md` mirror the same bounded v4 conclusions and do not collapse the ledger's incomplete rows into a milestone-complete claim.
8. Verify no legacy pipeline or sibling file changed, and no unapproved sweep or merge occurred. The 20 ring main artifacts are within the registered n=6/n=8 five-seed/300-step budget.
9. Verify the owner-learning statement and literature review are treated as prerequisites for NULL-03–08/WRITE-07, not as agent-authored predictions or retrospective interpretation.

## Decisions recorded from owner (2026-09-06)

- D1: fixed-photon `g2=0` with explicit uniform per-photon loss; multiphoton `g2>0` claims remain outside scope.
- D2: discrete `0.1*j` alpha-key neighbor search with continuous single-qubit angles and exact analytic gradients.
- D3: sibling-style data-dependent parity initialization at scale `0.1` for primary profiles; small-angle and uniform remain ablations; deterministic duplicates are not independent replicas.

These decisions unlock implementation, but do not certify physical full-Fock composition, NAT efficacy, or owner interpretation. The training-smoke source trajectory is independently retrained with the regenerated source-recipe data; other sibling rows remain separately dispositioned.

## Third-repair evidence (2026-09-06)

- Focused regression evidence: `venv/Scripts/python.exe -m pytest -q tests/v4_tcdp/test_classical_core.py tests/v4_tcdp/test_rings_pipeline.py tests/v4_tcdp/test_sibling_inventory.py` — 35 passed across the three touched boundaries (the ring/inventory subset was 22 passed and classical core was 13 passed in the focused reruns; the remaining v4 tests are covered by the full gate).
- The historical second-repair probe remains a counterexample record and is not a post-repair pass command. The new regression tests are the executable post-repair evidence for S01–S05.
- Third-repair baseline: `658 passed, 1 skipped in 455.60s (0:07:35)`.

## Fourth-repair evidence (2026-09-06)

- Targeted T01–T06 regressions: `venv/Scripts/python.exe -m pytest -q tests/v4_tcdp/test_nat.py tests/v4_tcdp/test_classical_core.py::test_rejected_adam_resume_is_atomic_and_rejects_negative_second_moments tests/v4_tcdp/test_sibling_inventory.py::test_scoped_source_identity_handles_non_ascii_paths tests/v4_tcdp/test_sibling_inventory.py::test_source_identity_fails_closed_when_status_is_unavailable tests/v4_tcdp/test_sibling_replay.py::test_replay_rejects_malformed_generator_and_nonfinite_loss tests/v4_tcdp/test_rings_pipeline.py::test_idempotent_ring_rewrite_rejects_corrupt_summary` — 15 passed.
- Fourth-repair full-suite verification: `665 passed, 1 skipped in 654.64s (0:10:54)`.
- Explicit sibling integration after source/replay changes: `8 passed in 9.50s`.

## Milestone-completion evidence (2026-09-07)

- Physical controls: fixed-photon n=2/n=3 no-gate, bystander, and shared-gate controls `PASS`; final-only/intermediate shared conditional TVD `0.585411845271861`, so final-only is the supported boundary. The historical pre-fix `FAIL` candidate is preserved separately.
- Registered ring outputs: `registered_v2_ring_photonic_n4_seed0_smoke.json` and its Hamming counterpart; both `PASS`, direct-vs-compiled TVD below `2e-16`, with recomputable payload hashes and matched parameters.
- Resource pilot: `resource_budget_final_v6.json`; n=4/6/8/10 all `PASS`, clean source commit `980cfe7`, n=10 RSS growth `0` bytes, timing criterion `PASS`, and a payload hash.
- NAT: registered n=4 seeds 0–4 and n=6/n=8 seed 0 matched reports; final reports include target improvement, fixed-reference TVD, acceptance, optimizer-state equality, and fixed-pair ablation labeling.
- Closure checklist: [.planning/v4-closure-checklist.md](v4-closure-checklist.md) maps each incomplete requirement to the missing evidence, next action, dependency, and budget.
- Post-fix targeted verification: `111 passed`; full suite: `681 passed, 1 skipped in 396.74s (0:06:36)`.
- Independent review disposition: earlier reviews found physical-status, atomic-writer, provenance, and NAT matching defects; those were repaired. The fresh post-fix recheck passed the declared bounded scope; its three cleanup findings are repaired in the cleanup commit following `3e1ae33`.

## Closure-pass handoff update (2026-09-08)

- Artifact-producing implementation head is `c1617601df5f7f5da6ccba324e8c0b32aab46054`; final integrated HEAD is `bb42fa4d68cbd1030716d82e1b6f60650be9a821`. The commits after c161 are documentation/validator-only, so the suffixed artifacts are qualified as generated-at-c161 rather than mislabeled as exact-final-head runs. Base remains `de80e9313beed614528fd6332b2f78aab83c0b50`.
- Sibling identity remains `f6d6ebe87e4ee1de10893c6ea2f0ffa367493336`, branch `alejack312`, clean, and unmodified.
- Reproducible closure commands use the suffixed outputs in the milestone report: `validate_owner_controls.py --output results/v4_tcdp/controls/owner_controls_20260908_head.json`, isolated-Perceval `validate_physical_controls.py --output results/v4_tcdp/controls/physical_controls_20260908_head.json`, `validate_deploy.py --output results/v4_tcdp/controls/deploy_controls_20260908_head.json`, and `run_nat.py ... --output results/v4_tcdp/nat/closure_20260908/20260908_n4_seed0_owner_null_head.json`. Those committed outputs record source commit c161 by design; reruns against a later checkout should use a new isolated output name.
- New evidence is at `results/v4_tcdp/controls/`, `results/v4_tcdp/nat/closure_20260908/`, `results/v4_tcdp/comparisons/closure_20260908/`, and `results/v4_tcdp/sibling_replays/closure_20260908/`. Treat the sibling closure output as a stopped partial replay/reference artifact, not faithful retraining; it has no worker report or certifying source-trajectory provenance. The non-suffixed physical/NAT artifacts are preserved historical outputs; immutable writers reject replacing them after a commit-identity change.
- Artifact integrity command: `venv/Scripts/python.exe scripts/v4_tcdp/validate_artifacts.py --root results/v4_tcdp` — current result `242` JSON files, `30` JSONL rows, `7` payload hashes, zero failures.
- Ledger status changes are narrow: NULL-03–06 are PASS within declared scopes; the binding NULL-08 matched continuation is PASS; NULL-07 remains INCONCLUSIVE; WRITE-07 and COMM-02 remain BLOCKED; the sibling/larger-n/complete-comparison rows remain INCONCLUSIVE. Do not promote analytic map-derived cells to physical photonic PASS.

## Final documentation-mirror recheck (2026-09-07)

- Independent final review at the current integration head: `PASS` after the documented cleanup findings were repaired and rechecked. The canonical validation manifest is unchanged and the closure metadata matches the current evidence ledger.
- The reviewer confirmed that the README and `docs/technical-findings.md` additions contain only verified, scope-qualified v4 claims; `WRITE-09` is correctly `PASS`; and incomplete rows remain explicit (`INCONCLUSIVE`, `NOT IMPLEMENTED`, and `BLOCKED`) with concrete next actions.
- The documentation changes were then committed with the ledger and handoff updates. No source-code or sibling changes were made in this final documentation pass.
