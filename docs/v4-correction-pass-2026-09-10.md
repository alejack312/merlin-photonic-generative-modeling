# v4.0 bounded correction pass — 2026-09-10

This note records the correction pass following the 2026-09-09 independent audit. It is an implementation and evidence-integrity update; it does not upgrade the unresolved scientific scope to full v4 acceptance. The implementation/test changes are committed in `c76f0ea`.

## Disposition

| Finding | Disposition | Evidence and consequence |
|---|---|---|
| F1 resource pilot measured the launcher and masked worker growth | FIXED | The pilot now identifies the allocating interpreter, records worker OS peak/high-water RSS, validates the Windows structure, and requires all registered sizes. [`resource_budget_correction_20260910.json`](../results/v4_tcdp/deploy/resource_budget_correction_20260910.json) is a fresh n=4/6/8/10 PASS artifact. |
| F2 mutation controls used constants | FIXED | Success and map controls now recompute derived metrics from the mutated objects. A no-op or invalid mutation fails; metric saturation is reported separately from mutation application. |
| F3 support validity was hard-coded | FIXED | Support validity is computed from target support `p > 1e-6` and is labeled as probability-vector support, not empirical sampled support. |
| F4 NAT was described as a noise-adaptation comparison | CLAIM CORRECTED | Under fixed-photon uniform loss, matched NAT arms are a same-procedure reproducibility/continuation control. The deployed arm differs by the scalar `eta**n` acceptance factor; no noise-adaptation claim is made. |
| F5 photonic ring artifacts were over-described | CLAIM CORRECTED | Documentation now calls the existing photonic ring outputs n=4, three-step, small-angle smoke evaluations. The n=6/n=8 trained profiles remain classical artifacts; direct larger-n photonic deployment is not claimed. |
| F6 ring reports omitted fit quality | FIXED IN EVIDENCE | The refreshed 22 ring comparison artifacts contain TVD, Hamming MMD², spatial MMD², order-1/order-2 marginals, occupancy, support validity, and acceptance separately. |
| F7 rail convention was contradictory | QUALIFIED | The owner-authored explanation is preserved. The code/manifest convention is explicitly recorded as MSB-first with logical `0=(0,1)` in the active codec; the earlier `0=(1,0)` wording is retained only as owner-authored historical material and is not used as an implementation assertion. |
| F8 self-consistency controls were presented as physical validation | CLAIM CORRECTED | Reports now distinguish analytic pipeline checks, model-derived fixed-photon references, and direct Perceval controls. |
| F9 erasure/tomography/physicality issues | FIXED / QUALIFIED | Erasure validates finite input and distinguishes represented subdistribution from explicit failure mass; tomography averages independent one-body readouts and keeps provenance analytic; physicality checks both lower and upper `E†I` bounds plus operative-Choi consistency. |
| F10 n=9 acceptance/throughput was omitted | FIXED IN EVIDENCE | The supported sibling comparison artifacts retain acceptance and attempts-per-accepted-sample fields. They remain model-derived/reference-only, not direct n=9 full-Fock evidence. |
| F11 n=9 support was hard-coded to 1 | FIXED | Sibling comparison rows use the declared target-support threshold and expose the definition and basis. |
| F12 unrun inventory rows were called exact reproductions | FIXED | Inventory uses `exact_reproduction_candidate` until execution evidence exists; replay accepts both legacy executed rows and candidate rows. |
| F13 retraining used a YAML stub | FIXED | Source import now requires real PyYAML and fails explicitly when it is unavailable; malformed YAML is not silently accepted. |
| F14 eta=1 replay was presented as deployment | CLAIM CORRECTED | Replay labels eta=1 as a lossless compiled-model reference and records that it is not independent deployment evidence. |

## Implementation evidence

The following changes are in the working tree for this pass:

- worker-identity and peak-RSS measurement in `scripts/v4_tcdp/resource_pilot.py`;
- recomputed mutation controls, target-support metrics, and complete Windows RSS structure in `src/merlin_iqp/experiments/comparison.py`;
- Jacobian-free post-update objective evaluation in `src/merlin_iqp/classical/expectation.py`, `src/merlin_iqp/classical/objectives.py`, and `src/merlin_iqp/classical/trainer.py`;
- finite-input erasure, corrected tomography, and stronger `E†I` physicality bounds in `src/merlin_iqp/deploy/erasure.py` and `src/merlin_iqp/deploy/maps.py`;
- real-source YAML loading and explicit lossless replay labeling in `scripts/v4_tcdp/retrain_sibling.py` and `scripts/v4_tcdp/replay_sibling.py`;
- explicit source-commit resolution in `src/merlin_iqp/experiments/rings.py` and candidate inventory disposition in `src/merlin_iqp/experiments/sibling_import.py`;
- semantic artifact validation in `scripts/v4_tcdp/validate_artifacts.py`.

## Refreshed artifacts

- [Resource pilot](../results/v4_tcdp/deploy/resource_budget_correction_20260910.json): registered n=4/6/8/10 pilot, status `PASS`.
- [Ring comparison refresh](../results/v4_tcdp/corrections_20260910/metrics_v3/): 22 existing ring cells regenerated against the final control logic; historical outputs were not overwritten.
- [Sibling comparison refresh](../results/v4_tcdp/sibling_comparisons/correction_20260910_v3/summary.json): eight registered available cells, status `PASS`, using the pinned sibling checkpoint/retraining evidence and eta=0.9 model-derived deployment arm.

The refreshed metrics compare raw, unquantized compiled control, quantized compiled reference, and deployed fixed-photon reference with the same frozen inputs and budgets. Acceptance and conditional quality are separate. The project-wide deterministic checks remain at `1.0e-16`; probability-vector and source trajectory checks retain their documented `1.0e-12` tolerances.

## Verification run record

- Focused correction suite: `venv/Scripts/python.exe -m pytest -q tests/v4_tcdp/test_artifact_semantics.py tests/v4_tcdp/test_comparison.py tests/v4_tcdp/test_deploy.py tests/v4_tcdp/test_classical_core.py tests/v4_tcdp/test_sibling_inventory.py tests/v4_tcdp/test_sibling_replay.py tests/v4_tcdp/test_sibling_retrain.py tests/v4_tcdp/test_rings_pipeline.py tests/v4_tcdp/test_resource_pilot.py` → `186 passed, 1 skipped`.
- Artifact validator: `venv/Scripts/python.exe scripts/v4_tcdp/validate_artifacts.py --root results/v4_tcdp` → `499` JSON files, `72` JSONL rows, `17` payload hashes, `0` failures (`PASS`).
- Sibling checkout: verified separately as the pinned clean checkpoint; no sibling files were changed.

## Remaining gaps

These are not disguised as interpretation-only limitations:

- direct full-Fock validation remains bounded to the registered small-n controls; the refreshed ring and sibling deployed arms are analytic/model-derived;
- larger-n photonic deployment and direct n=9 full-Fock comparison are not implemented/evidenced;
- NULL-07 remains “hypothesis recorded; experimentally untested”; no source-mutation experiment is claimed by this pass;
- sampled uncertainty panels and unavailable sibling rows remain `INCONCLUSIVE` or `BLOCKED` according to the ledger;
- NAT efficacy under a distinct noisy continuation is not tested by the fixed-photon uniform-loss control;
- owner-authored scientific interpretation remains provisional for review.

No merge, publication, external message, or unapproved sweep was performed.
