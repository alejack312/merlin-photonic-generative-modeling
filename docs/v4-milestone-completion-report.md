# v4.0 milestone completion report

Date: 2026-09-08. Branch: `codex/v4-implementation`. Base: `de80e9313beed614528fd6332b2f78aab83c0b50`. The current integration point and remaining-work map are recorded in [.planning/v4-closure-checklist.md](../.planning/v4-closure-checklist.md). This report separates implementation completion from scientific acceptance.

## 2026-09-08 closure-pass addendum

- Owner predictions are now recorded in [docs/v4-owner-predictions-2026-09-08.md](v4-owner-predictions-2026-09-08.md). The registered owner controls for NULL-03 through NULL-06 pass within the declared analytic/fixed-photon scopes; exact scalar residuals are recorded at the project-wide `1.0e-16` scale and probability-vector controls use the binding `1.0e-12` tolerance.
- NULL-03’s analytic k=0 factorization residual is `2.220446049250313e-16`; the direct Perceval no-gate n=2 control has direct-vs-analytic TVD `1.0842021724855044e-16`. NULL-04’s same-parameter compiler/reference control has maximum probability residual `1.1102230246251565e-16` and success residual `1.3877787807814457e-17`. NULL-05 has conditional-shape TVD `0.0` and exact `eta**n` mass scaling. NULL-06’s CP and qualified heralded throughput residuals are `0.0`.
- NULL-08’s binding same-algorithm matched continuation passes for the fresh n=4 seed-0 closure run: both arms share the warm-start and optimizer-state hashes, budgets, final parameter hash and loss endpoint. The owner’s separate continuous-versus-discrete objective prediction remains exploratory because the current registration does not test it.
- A fresh direct full-Fock manifest records final-only and intermediate projections, absolute accepted mass, conditional distributions and the shared-gate discrepancy (`0.585411845271861`). The fixed-photon physical scope passes; it does not certify larger-n full-Fock behavior or multiphoton source models.
- Eight additional n=6/n=8 comparison cells were independently inspected in the isolated closure namespace. Hamming-MMD direct/Walsh cross-checks, hashes, raw/compiled/deployed separation and fixed-loss ratios pass as analytic map-derived evidence. The worker’s sibling output is retained as a stopped partial replay/reference artifact; no faithful retraining claim is made because it lacks certifying source-trajectory provenance.
- The authoritative ledger now marks NULL-03–06 and the binding NULL-08 control `PASS`, NULL-07 `INCONCLUSIVE`, and WRITE-07/COMM-02 `BLOCKED`. SWEEP-04, RING-04, REPRO-03, COMPARE-01 and COMPARE-04 remain `INCONCLUSIVE` because their required sibling, larger-n physical, or complete matched arms are still absent. v4.0 is therefore not fully scientifically accepted.

Closure commands for this addendum:

```powershell
venv/Scripts/python.exe scripts/v4_tcdp/validate_owner_controls.py --output results/v4_tcdp/controls/owner_controls_20260908_head.json
$env:PCVL_PERSISTENT_PATH = Join-Path $env:TEMP 'merlin-v4-null-physical-20260908'
venv/Scripts/python.exe scripts/v4_tcdp/validate_physical_controls.py --pcvl-path $env:PCVL_PERSISTENT_PATH --output results/v4_tcdp/controls/physical_controls_20260908_head.json
venv/Scripts/python.exe scripts/v4_tcdp/validate_deploy.py --output results/v4_tcdp/controls/deploy_controls_20260908_head.json
venv/Scripts/python.exe scripts/v4_tcdp/run_nat.py --n 4 --seed 0 --steps 150 --matched-continuation --equal-budget-control --output results/v4_tcdp/nat/closure_20260908/20260908_n4_seed0_owner_null_head.json
venv/Scripts/python.exe -m pytest -q tests/v4_tcdp/test_deploy.py tests/v4_tcdp/test_nat.py tests/v4_tcdp/test_comparison.py
```

The original non-suffixed physical/NAT artifacts are preserved historical
closure outputs from the prior integration commit. The suffixed `head`
artifacts are the reproducible current-head reruns; immutable writers reject
silently replacing the former artifacts when the repository identity changes.

## Implementation now exercised

- The NumPy IQP trainer, typed two-ring adapter, spatial and Hamming objectives, D3 initialization, discrete-alpha/continuous-single NAT, portable checkpoints, source inventory/replay boundary, compiler, CP-map validation, full-Fock controls, throughput/erasure helpers, metric panels, comparison writer, and provenance gates are implemented without migrating legacy pipelines.
- Fixed-photon `g2=0` Perceval controls pass for n=2/n=3 no-gate, single-gate-with-bystander, and shared-gate cases. Absolute accepted mass and conditional output are separate. The shared-gate final-only/intermediate conditional TVD is `0.585411845271861`; final-only is therefore the supported boundary.
- Registered n=4 spatial and Hamming ring checkpoints have fixed-photon final-only photonic evaluations with matched compiled qubit references. The n=6/n=8 ring training budget is complete; larger-n photonic deployment is not claimed.
- Registered NAT reports contain two matched continuation arms from one frozen warm start with matched optimizer state and budgets for n=4 seeds 0–4 and n=6/n=8 seed 0. They are ideal/model-derived evidence, not a noisy-efficacy claim.
- The retained NAT stop rule is now artifact-backed: a bounded n=8 matched run completed in `264.498991300003` seconds under the `1200`-second limit, while registered n=4 runs were already green, so the two-day n=4 condition was not triggered.
- Sibling `training_smoke` is faithfully retrained from regenerated source-recipe data. Bandwidth is stopped partial replay; Ghosh–Kim is adapted checkpoint replay. These dispositions remain distinct.
- Bounded derived comparison artifacts now cover the registered Hamming n=6/n=8 seed cells and two spatial n=6 cells, with raw/compiled/deployed-map panels and Hamming-MMD cross-checks. They do not close the sibling-matched or larger-n physical comparison requirements.

## Evidence and commands

- Physical controls: `venv/Scripts/python.exe scripts/v4_tcdp/validate_physical_controls.py --pcvl-path <writable-perceval-path> --output results/v4_tcdp/deploy/physical_control_manifest.json` — manifest status `PASS` for the declared fixed-photon final-only controls.
- Photonic ring smoke: `venv/Scripts/python.exe scripts/v4_tcdp/evaluate_ring_photonic.py results/v4_tcdp/rings/rings_spatial_exact/n4_seed0_smoke --eta 0.9 --validation-manifest results/v4_tcdp/deploy/physical_control_manifest.json --output results/v4_tcdp/deploy/registered_v2_ring_photonic_n4_seed0_smoke.json`, and the corresponding Hamming path/output. Both report `PASS`; direct-vs-compiled TVD is below `2e-16`.
- Focused integration: `venv/Scripts/python.exe -m pytest -q tests/v4_tcdp/test_deploy.py tests/v4_tcdp/test_ring_photonic.py tests/v4_tcdp/test_resource_pilot.py tests/v4_tcdp/test_comparison.py tests/v4_tcdp/test_nat.py tests/v4_tcdp/test_sibling_replay.py` — 124 passed.
- Explicit sibling integration: `venv/Scripts/python.exe -m pytest -q tests/v4_tcdp/test_sibling_retrain.py tests/v4_tcdp/test_sibling_replay.py tests/v4_tcdp/test_sibling_inventory.py` — 21 passed.
- Script compilation: `venv/Scripts/python.exe -m compileall -q scripts/v4_tcdp` — passed.
- Resource pilot: `venv/Scripts/python.exe scripts/v4_tcdp/resource_pilot.py --output results/v4_tcdp/deploy/resource_budget_final_v6.json` — n=4/6/8/10 completed within the approved three-hour timing gate, no full-circuit superoperator was allocated, and the n=10 RSS criterion passed with clean source provenance.
- Artifact validation: 174 committed JSON artifacts parsed; finite-value, declared-output, physical payload-hash, registered-ring payload-hash, and final-resource payload-hash checks all passed.
- Documentation mirror: README and `docs/technical-findings.md` state the same bounded v4 evidence and explicitly preserve the remaining ledger statuses; no new scientific claim is introduced there.
- Full-suite command: `venv/Scripts/python.exe -m pytest -q` with `PCVL_PERSISTENT_PATH` set to a writable directory. Final result is recorded in the evidence ledger and reviewer handoff after completion.

## Acceptance status

The authoritative requirement-by-requirement status is [.planning/v4-requirement-evidence.md](../.planning/v4-requirement-evidence.md). PASS rows are bounded to their stated evidence. INCONCLUSIVE rows include the missing arm or scope. NOT IMPLEMENTED is reserved for absent required work; BLOCKED is reserved for owner/external inputs.

Remaining scientific gaps are: multiphoton `g2>0` validation, a general chain-level final-only/intermediate composition proof, larger-n photonic deployment, faithful sibling retraining for rows whose exact inputs are absent, and a complete sibling/substrate matched comparison and figures. These are not relabeled as interpretation-only gaps; a two-day n=4 wait was not launched because registered n=4 was already green.

Owner-gated rows are now split accurately: NULL-03–06 and the binding NULL-08 control have owner-authored notes plus registered bounded evidence; NULL-07 remains unadjudicated because its source-mutation capability is outside D1; WRITE-07 still requires the owner-authored sign/winding, source-versus-gate, projection/loss, conditioning and NAT explanation; COMM-02 still requires an owner-authored draft or hold. No external message, merge, publication, or unapproved sweep is part of this milestone.
