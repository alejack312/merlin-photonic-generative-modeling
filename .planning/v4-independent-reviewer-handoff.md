# v4.0 independent reviewer handoff

## Scope

Review the additive v4.0 implementation against the binding plan, additive design, audit, and the five-state evidence ledger. Treat scientific interpretation as provisional. Do not modify the sibling repository, merge, publish, or launch unapproved sweeps.

## Current correction-pass handoff (2026-09-10)

- Implementation/test corrections are committed at `c76f0ea` on `codex/v4-implementation`; the final documentation/evidence commit is the current branch head recorded by `git rev-parse HEAD`.
- The 2026-09-09 F1–F14 audit is dispositioned in [docs/v4-correction-pass-2026-09-10.md](../docs/v4-correction-pass-2026-09-10.md). No sibling files or legacy pipelines were changed.
- Verification: full suite `719 passed, 1 skipped`; focused correction suite `186 passed, 1 skipped`; explicit sibling integration `35 passed`; artifact validation `499` JSON, `72` JSONL, `17` payload hashes, `0` failures; compileall and diff check pass.
- Fresh post-commit evidence is isolated at [resource_budget_correction_20260910_final2.json](../results/v4_tcdp/deploy/resource_budget_correction_20260910_final2.json), [metrics_v5](../results/v4_tcdp/corrections_20260910/metrics_v5/), and [sibling comparison v5](../results/v4_tcdp/sibling_comparisons/correction_20260910_v5/summary.json). Ring count is 22; sibling comparison count is 8 and overall `PASS`.
- Review boundaries remain explicit: direct full-Fock evidence is bounded to registered small-n controls; the ring/sibling deployed arms are analytic/model-derived; larger-n deployment, NULL-07 adjudication, sampled uncertainty, NAT efficacy interpretation, and unavailable sibling inputs remain incomplete or blocked in the ledger.

## Git and provenance

- Repository: `C:\Users\cuqui\merlin-quantum-case-study`
- Base: `de80e9313beed614528fd6332b2f78aab83c0b50` (`fix/narrow-circuit-claim`)
- Final review target: the current `git rev-parse HEAD` on `codex/v4-implementation`; the prior implementation/evidence commit is `800a53c`.
- Sibling: `C:\Users\cuqui\iqp-mmd-barren-plateau`
- Required sibling checkpoint: `f6d6ebe87e4ee1de10893c6ea2f0ffa367493336`
- Verified sibling state: branch `alejack312`, clean, ahead of its remote by one commit; no sibling edits were made.

## Current repair update (2026-09-09)

The independent audit findings A01–A04 are repaired in implementation commit `7089dbf`; final evidence and documentation are in `800a53c` plus this handoff update. A01 now preserves coherent interference in projection readout; A02 rejects incomplete full-Fock mass instead of normalizing it away; A03 enforces local-versus-unquantized compilation equality per sibling cell; and A04 rejects invalid spatial-kernel mixtures. The repaired physical manifest reports shared-gate final-only/intermediate TVD `1.942890293094024e-16` with unchanged accepted mass. The previous `0.585411845271861` value is superseded and retained only in dated audit/historical artifacts.

Final evidence paths:

- `results/v4_tcdp/deploy/physical_control_manifest_20260909_final.json` (superseded by the acceptance-qualified v2 artifact below)
- `results/v4_tcdp/deploy/physical_control_manifest_20260909_final3.json`
- `results/v4_tcdp/deploy/registered_v3_ring_photonic_spatial_n4_seed0_smoke_20260909_final3.json`
- `results/v4_tcdp/deploy/registered_v3_ring_photonic_hamming_n4_seed0_smoke_20260909_final3.json`
- `results/v4_tcdp/deploy/resource_budget_final_v8.json`
- `results/v4_tcdp/sibling_comparisons/closure_20260909_final/summary.json`

## Post-repair update (2026-09-09)

The B01–B03 findings from the post-repair audit are repaired. Ring and physical qualification now independently validate absolute acceptance; positive-step checkpoints require complete histories and round-trip through save/resume; and resource aggregation requires exactly the registered sizes with every measurement passing. The regenerated physical/ring artifacts and resource pilot are versioned separately from the prior final artifacts.

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
venv/Scripts/python.exe scripts/v4_tcdp/compare_sibling_backends.py --sibling-root C:/Users/cuqui/iqp-mmd-barren-plateau --retraining-root results/v4_tcdp/sibling_retraining/training_smoke --retraining-root results/v4_tcdp/sibling_retraining/closure_20260908/bandwidth_source_rerun --retraining-root results/v4_tcdp/sibling_retraining/closure_20260908/ghosh_kim_source_rerun --output-root results/v4_tcdp/sibling_comparisons/closure_20260909_final --eta 0.9
venv/Scripts/python.exe scripts/v4_tcdp/run_nat.py --n 4 --seed 0 --steps 150 --matched-continuation --output results/v4_tcdp/nat/n4_seed0_primary.json
```

The required full suite is:

```powershell
$env:PCVL_PERSISTENT_PATH = Join-Path ([System.IO.Path]::GetTempPath()) 'merlin-v4-perceval'
venv/Scripts/python.exe -m pytest -q
```

Current post-repair verification at `800a53c`:

- Full suite: `693 passed, 1 skipped` in `366.53s`, with writable `PCVL_PERSISTENT_PATH`.
- Explicit sibling integration: `30 passed` in `50.47s`, with `MERLIN_SIBLING_ROOT` set to the pinned clean sibling checkout.
- Artifact validator: `398` JSON files, `72` JSONL rows, `12` payload hashes, `0` failures.
- `compileall` and `git diff --check`: pass.
- Sibling comparison regeneration: eight cells, overall `PASS`, local/unquantized compilation control enforced per cell.
- Repaired physical manifest: overall `PASS`; shared-gate projection TVD `1.942890293094024e-16`; full-Fock mass reconciliation fields present.
- Repaired n=4 spatial/Hamming photonic artifacts: both `PASS`; direct-vs-compiled TVD `1.390014947762197e-16` and `1.767385066422933e-16`.

Post-repair verification after B01–B03:

- Full suite: `697 passed, 1 skipped` in `442.88s`, with writable `PCVL_PERSISTENT_PATH`.
- Explicit sibling integration: `30 passed` in `70.31s`.
- Artifact validator: `402` JSON files, `72` JSONL rows, `14` payload hashes, `0` failures.
- Resource pilot v7: n=4/6/8/10 all `PASS` under the approved timing and RSS gates.
- Acceptance qualification: physical maximum independent acceptance error `4.163336342344337e-17`; regenerated ring errors `2.3852447794681098e-18` and `1.951563910473908e-18`, tolerance `1.0e-16`.

Focused repair closure (2026-09-09, implementation commit `ce637a8` plus provenance-matched artifact closure):

- Targeted regression set: `103 passed in 41.25s`, including ring acceptance qualification, physical-control acceptance mutation rejection, strict checkpoint history/resume round-trip, and exact resource-pilot aggregation.
- Provenance-matched artifacts: physical controls `final3`, spatial/Hamming n=4 ring smoke `final3`, and resource pilot `v8`; the physical maximum independent acceptance error is `4.163336342344337e-17`, and ring errors are `2.3852447794681098e-18` and `1.951563910473908e-18`, all below `1.0e-16`. The resource pilot records source commit `ef67c4a` with `dirty=false` and all four registered sizes passing.
- Artifact validator: `406` JSON files, `72` JSONL rows, `16` payload hashes, `0` failures; `compileall` and `git diff --check` pass.
- Full suite and explicit sibling integration remain the already-recorded `697 passed, 1 skipped` and `30 passed` results for the same implementation code; only active artifact references were advanced from `final2`/`v7` to `final3`/`v8`.

Final verification in the closure pass: the full suite passed `687 passed, 1 skipped in 918.94s (0:15:18)` with `PCVL_PERSISTENT_PATH` redirected to a writable temporary directory; explicit sibling integration plus the new comparison gate passed `28 passed, 1 skipped in 175.16s`; the new validators compiled; and artifact validation passed with `355` JSON files, `72` JSONL rows, `9` payload hashes, and zero failures. These are environment notes, not relaxed acceptance gates.

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

These decisions unlock implementation, but do not certify physical full-Fock composition, NAT efficacy, or owner interpretation. Eight registered training cells (training-smoke, bandwidth, and Ghosh–Kim small-n) are independently retrained from the pinned source trainer, and the registered exact n=6 anti-concentration validation cell has a separate PASS source-validation report; large-n, Qiskit-dependent, and missing-input sibling rows remain separately dispositioned.

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
- Historical resource pilot: `resource_budget_final_v6.json`; superseded by the acceptance-qualified resource pilot v7 listed in the current post-repair verification.
- NAT: registered n=4 seeds 0–4 and n=6/n=8 seed 0 matched reports; final reports include target improvement, fixed-reference TVD, acceptance, optimizer-state equality, and fixed-pair ablation labeling.
- Closure checklist: [.planning/v4-closure-checklist.md](v4-closure-checklist.md) maps each incomplete requirement to the missing evidence, next action, dependency, and budget.
- Post-fix targeted verification: `111 passed`; full suite: `681 passed, 1 skipped in 396.74s (0:06:36)`.
- Independent review disposition: earlier reviews found physical-status, atomic-writer, provenance, and NAT matching defects; those were repaired. The fresh post-fix recheck passed the declared bounded scope; its three cleanup findings are repaired in the cleanup commit following `3e1ae33`.

## Closure-pass handoff update (2026-09-08)

- Review target: record the current checkout's exact `git rev-parse HEAD` at readback; the closure commit adds the supported sibling comparator, its vectorized analytic-density implementation, canonical artifacts, and reconciled evidence. Base remains `de80e9313beed614528fd6332b2f78aab83c0b50`. The owner-control and physical-control manifests retain producer head `d16f50794085d76b2ba829348a3e2d4ad8893017`; that provenance is not rewritten. The vectorized density path and new sibling closure were independently rechecked after implementation.
- Sibling identity remains `f6d6ebe87e4ee1de10893c6ea2f0ffa367493336`, branch `alejack312`, clean, and unmodified.
- Reproducible closure commands include the current-head owner and physical controls, the seven registered NAT matched-continuation reports, and the isolated source retraining/validation commands documented in `docs/v4-sibling-reproduction.md`. The eight training cells and exact validation cell have certifying source reports; older sibling checkpoint replay outputs remain replay/reference-only. The non-suffixed physical/NAT artifacts are preserved historical outputs; immutable writers reject replacing them after a commit-identity change.
- New evidence is at `results/v4_tcdp/controls/owner_controls_20260908_current.json`, `results/v4_tcdp/deploy/physical_control_manifest_20260908_head.json`, `results/v4_tcdp/sibling_retraining/closure_20260908/`, and `results/v4_tcdp/sibling_comparisons/closure_20260908_complete_v4/`. Artifact integrity command: `venv/Scripts/python.exe scripts/v4_tcdp/validate_artifacts.py --root results/v4_tcdp` — current result `355` JSON files, `72` JSONL rows, `9` payload hashes, zero failures.
- Ledger status changes are narrow: NULL-03–06 and the owner-authored NULL-07 hypothesis are PASS within declared scopes; the binding NULL-08 matched continuation is PASS; NULL-07’s experimental adjudication remains INCONCLUSIVE; WRITE-07 remains BLOCKED; the registered sibling/substrate comparison scope is PASS while larger-n direct-physical, missing-input, and broader uncertainty rows remain INCONCLUSIVE. The former COMM-02 communication gate was retired by the owner on 2026-09-08. Do not promote analytic map-derived cells to physical photonic PASS.

## Closure validation recheck (2026-09-08)

- Integrated head: record the exact current `git rev-parse HEAD` in the final readback. The reviewed implementation/evidence head is `50fd652`; subsequent local commits only preserve alternate attempt artifacts and keep this handoff current.
- Full suite: `venv/Scripts/python.exe -m pytest -q` → `687 passed, 1 skipped in 918.94s (0:15:18)` with writable `PCVL_PERSISTENT_PATH`.
- Explicit sibling integration plus comparison gate: `venv/Scripts/python.exe -m pytest -q tests/v4_tcdp/test_sibling_inventory.py tests/v4_tcdp/test_sibling_replay.py tests/v4_tcdp/test_sibling_retrain_portable.py tests/v4_tcdp/test_sibling_retrain.py tests/v4_tcdp/test_sibling_validation_rerun.py tests/v4_tcdp/test_sibling_backend_comparison.py` → `28 passed, 1 skipped in 175.16s`.
- Artifact validator: `355` JSON files, `72` JSONL rows, `9` payload hashes, `0` failures. Independent review repaired the missing-versus-null config-diff defect and the stale `174`-artifact sentence; this closure adds the supported eight-cell sibling/substrate chain without expanding direct physical scope.

## Final documentation-mirror recheck (2026-09-07)

- Independent final review at the current integration head: `PASS` after the documented cleanup findings were repaired and rechecked. The canonical validation manifest is unchanged and the closure metadata matches the current evidence ledger.
- The reviewer confirmed that the README and `docs/technical-findings.md` additions contain only verified, scope-qualified v4 claims; `WRITE-09` is correctly `PASS`; and incomplete rows remain explicit (`INCONCLUSIVE`, `NOT IMPLEMENTED`, and `BLOCKED`) with concrete next actions.
- The documentation changes were then committed with the ledger and handoff updates. No source-code or sibling changes were made in this final documentation pass.
