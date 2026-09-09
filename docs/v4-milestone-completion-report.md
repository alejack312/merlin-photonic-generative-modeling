# v4.0 milestone completion report

Date: 2026-09-08. Branch: `codex/v4-implementation`. Base: `de80e9313beed614528fd6332b2f78aab83c0b50`. The current integration point and remaining-work map are recorded in [.planning/v4-closure-checklist.md](../.planning/v4-closure-checklist.md). This report separates implementation completion from scientific acceptance.

## 2026-09-08 closure-pass addendum

- Owner predictions are now recorded in [docs/v4-owner-predictions-2026-09-08.md](v4-owner-predictions-2026-09-08.md). The registered owner controls for NULL-03 through NULL-06 pass within the declared analytic/fixed-photon scopes; exact scalar residuals are recorded at the project-wide `1.0e-16` scale and probability-vector controls use the binding `1.0e-12` tolerance.
- NULL-03’s analytic k=0 factorization residual is `2.220446049250313e-16`; the direct Perceval no-gate n=2 control has direct-vs-analytic TVD `1.0842021724855044e-16`. NULL-04’s same-parameter compiler/reference control has maximum probability residual `1.1102230246251565e-16` and success residual `1.3877787807814457e-17`. NULL-05 has conditional-shape TVD `0.0` and exact `eta**n` mass scaling. NULL-06’s CP and qualified heralded throughput residuals are `0.0`.
- NULL-08’s binding same-algorithm matched continuation passes for the fresh n=4 seed-0 closure run: both arms share the warm-start and optimizer-state hashes, budgets, final parameter hash and loss endpoint. The owner’s separate continuous-versus-discrete objective prediction remains exploratory because the current registration does not test it.
- A fresh direct full-Fock manifest records final-only and intermediate projections, absolute accepted mass, conditional distributions and the shared-gate discrepancy (`0.585411845271861`). The fixed-photon physical scope passes; it does not certify larger-n full-Fock behavior or multiphoton source models.
- Eight additional n=6/n=8 comparison cells were independently inspected in the isolated closure namespace. Hamming-MMD direct/Walsh cross-checks, hashes, raw/compiled/deployed separation and fixed-loss ratios pass as analytic map-derived evidence. The registered training-smoke, bandwidth, and Ghosh–Kim small-n source trajectories were independently rerun from the pinned sibling trainer; all eight training cells match source theta/loss rows exactly. The registered exact n=6 anti-concentration validation cell also has a PASS source-validation report with byte-identical substantive JSON/CSV outputs. Older checkpoint replay outputs remain separately labeled replay/reference-only.
- The authoritative ledger now marks NULL-03–06, the owner-authored NULL-07 hypothesis, the binding NULL-08 control, registered REPRO-03 small-n retraining, the selected sibling/substrate comparison scope, and WRITE-07 `PASS`; NULL-07’s experimental adjudication remains `INCONCLUSIVE`; and SWEEP-04, RING-04, COMPARE-01 and COMPARE-04 remain qualified because broader physical, uncertainty, and missing-input rows are still incomplete. The owner-authored explanation is recorded in [docs/v4-owner-explanation-2026-09-09.md](v4-owner-explanation-2026-09-09.md). The former COMM-02 communication gate was retired by the owner on 2026-09-08. v4.0 is therefore not fully scientifically accepted.

Closure commands for this addendum:

```powershell
venv/Scripts/python.exe scripts/v4_tcdp/validate_owner_controls.py --output results/v4_tcdp/controls/owner_controls_20260908_head.json
$env:PCVL_PERSISTENT_PATH = Join-Path $env:TEMP 'merlin-v4-null-physical-20260908'
venv/Scripts/python.exe scripts/v4_tcdp/validate_physical_controls.py --pcvl-path $env:PCVL_PERSISTENT_PATH --output results/v4_tcdp/controls/physical_controls_20260908_head.json
venv/Scripts/python.exe scripts/v4_tcdp/validate_deploy.py --output results/v4_tcdp/controls/deploy_controls_20260908_head.json
venv/Scripts/python.exe scripts/v4_tcdp/run_nat.py --n 4 --seed 0 --steps 150 --matched-continuation --equal-budget-control --output results/v4_tcdp/nat/closure_20260908/20260908_n4_seed0_owner_null_head.json
venv/Scripts/python.exe scripts/v4_tcdp/validate_artifacts.py --root results/v4_tcdp
venv/Scripts/python.exe -m pytest -q tests/v4_tcdp/test_deploy.py tests/v4_tcdp/test_nat.py tests/v4_tcdp/test_comparison.py
```

The artifact validator reports `355` JSON files, `72` JSONL rows, and `9`
payload hashes with zero failures. The original non-suffixed physical/NAT
artifacts are preserved historical closure outputs from the prior integration
commit. The owner and physical manifests retain their producer head
`d16f507`; the later closure includes a vectorized analytic-density
implementation and was rechecked by the full suite. The new sibling comparison
manifests record their own producer head and are the authoritative evidence for
that closure. Immutable writers reject silently replacing the former artifacts when the repository identity changes.

## Implementation now exercised

- The NumPy IQP trainer, typed two-ring adapter, spatial and Hamming objectives, D3 initialization, discrete-alpha/continuous-single NAT, portable checkpoints, source inventory/replay boundary, compiler, CP-map validation, full-Fock controls, throughput/erasure helpers, metric panels, comparison writer, and provenance gates are implemented without migrating legacy pipelines.
- Fixed-photon `g2=0` Perceval controls pass for n=2/n=3 no-gate, single-gate-with-bystander, and shared-gate cases. Absolute accepted mass and conditional output are separate. The shared-gate final-only/intermediate conditional TVD is `0.585411845271861`; final-only is therefore the supported boundary.
- Registered n=4 spatial and Hamming ring checkpoints have fixed-photon final-only photonic evaluations with matched compiled qubit references. The n=6/n=8 ring training budget is complete; larger-n photonic deployment is not claimed.
- Registered NAT reports contain two matched continuation arms from one frozen warm start with matched optimizer state and budgets for n=4 seeds 0–4 and n=6/n=8 seed 0. They are ideal/model-derived evidence, not a noisy-efficacy claim.
- The retained NAT stop rule is now artifact-backed: a bounded n=8 matched run completed in `264.498991300003` seconds under the `1200`-second limit, while registered n=4 runs were already green, so the two-day n=4 condition was not triggered.
- Sibling `training_smoke`, all four registered bandwidth cells, and all three registered Ghosh–Kim small-n cells are faithfully retrained from the pinned source trainer. The registered exact n=6 anti-concentration validation cell has a separate PASS source-validation report. Existing checkpoint replays, large-n sampled, Qiskit-dependent, and missing-input rows retain their separate adapted/reference-only/blocked dispositions.
- Bounded derived comparison artifacts cover the registered Hamming n=6/n=8 seed cells and two spatial n=6 cells, and the eight-cell sibling/substrate closure covers training-smoke, bandwidth, and Ghosh–Kim cells with raw/compiled/deployed-map panels and Hamming-MMD cross-checks. The sibling closure is model-derived at n=9; it does not close larger-n direct physical/full-Fock comparison requirements.

## Evidence and commands

- Physical controls: `venv/Scripts/python.exe scripts/v4_tcdp/validate_physical_controls.py --pcvl-path <writable-perceval-path> --output results/v4_tcdp/deploy/physical_control_manifest.json` — manifest status `PASS` for the declared fixed-photon final-only controls.
- Photonic ring smoke: `venv/Scripts/python.exe scripts/v4_tcdp/evaluate_ring_photonic.py results/v4_tcdp/rings/rings_spatial_exact/n4_seed0_smoke --eta 0.9 --validation-manifest results/v4_tcdp/deploy/physical_control_manifest.json --output results/v4_tcdp/deploy/registered_v2_ring_photonic_n4_seed0_smoke.json`, and the corresponding Hamming path/output. Both report `PASS`; direct-vs-compiled TVD is below `2e-16`.
- Focused integration: `venv/Scripts/python.exe -m pytest -q tests/v4_tcdp/test_deploy.py tests/v4_tcdp/test_ring_photonic.py tests/v4_tcdp/test_resource_pilot.py tests/v4_tcdp/test_comparison.py tests/v4_tcdp/test_nat.py tests/v4_tcdp/test_sibling_replay.py` — 124 passed.
- Explicit sibling integration: `venv/Scripts/python.exe -m pytest -q tests/v4_tcdp/test_sibling_retrain.py tests/v4_tcdp/test_sibling_replay.py tests/v4_tcdp/test_sibling_inventory.py` — 21 passed.
- Script compilation: `venv/Scripts/python.exe -m compileall -q scripts/v4_tcdp` — passed.
- Resource pilot: `venv/Scripts/python.exe scripts/v4_tcdp/resource_pilot.py --output results/v4_tcdp/deploy/resource_budget_final_v6.json` — n=4/6/8/10 completed within the approved three-hour timing gate, no full-circuit superoperator was allocated, and the n=10 RSS criterion passed with clean source provenance.
- Artifact validation: 355 current JSON artifacts parsed; finite-value, declared-output, physical payload-hash, registered-ring payload-hash, sibling-comparison, and final-resource payload-hash checks all passed.
- Documentation mirror: README and `docs/technical-findings.md` state the same bounded v4 evidence and explicitly preserve the remaining ledger statuses; no new scientific claim is introduced there.
- Full-suite command: `venv/Scripts/python.exe -m pytest -q` with `PCVL_PERSISTENT_PATH` set to a writable directory → `687 passed, 1 skipped in 918.94s (0:15:18)`.

## Acceptance status

The authoritative requirement-by-requirement status is [.planning/v4-requirement-evidence.md](../.planning/v4-requirement-evidence.md). PASS rows are bounded to their stated evidence. INCONCLUSIVE rows include the missing arm or scope. NOT IMPLEMENTED is reserved for absent required work; BLOCKED is reserved for owner/external inputs.

Remaining scientific gaps are: multiphoton `g2>0` validation, a general chain-level final-only/intermediate composition proof, larger-n direct photonic deployment, faithful sibling retraining for rows whose exact inputs are absent, and sampled-uncertainty/figure extensions where not registered. The selected eight-cell sibling/substrate matched comparison is complete as an analytic fixed-photon reference and is not relabeled as direct n=9 full-Fock or hardware evidence. These are not relabeled as interpretation-only gaps; a two-day n=4 wait was not launched because registered n=4 was already green.

Owner-gated rows are now split accurately: NULL-03–06, the NULL-07 hypothesis, the binding NULL-08 control, and WRITE-07 have owner-authored notes plus registered bounded evidence; NULL-07 remains experimentally unadjudicated because its source-mutation capability is outside D1. The former COMM-02 communication gate was retired after two unanswered owner-sent messages; no further outreach, merge, publication, or unapproved sweep is part of this milestone.
