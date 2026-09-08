# v4.0 closure validation note

Date: 2026-09-08 · Scope: registered sibling validation closure

## Purpose

This note records the next available registered source experiment exercised during the v4.0 completion pass. It extends the existing owner-prediction note; it does not upgrade missing physical, large-n, Qiskit, or owner-authored evidence.

## Exact source-validation rerun

- Source: sibling `iqp-mmd-barren-plateau`, commit `f6d6ebe87e4ee1de10893c6ea2f0ffa367493336`, branch `alejack312`, clean before and after.
- Registered cell: `anti_concentration_validation`, complete graph, `n=6`, seed `7`.
- Rerun config: [`configs/v4_sibling_validation_retrain.yaml`](../configs/v4_sibling_validation_retrain.yaml), isolated under `results/v4_tcdp/sibling_retraining/closure_20260908/validation_source_rerun/`.
- Allowed config adaptations are limited to output metadata and the source runner's scalar-to-list normalization of `circuit.n_qubits`; any other difference fails closed.
- Result summary, excluding runner provenance: byte-identical to the source JSON.
- Threshold CSV: byte-identical to the source CSV.
- Source and rerun provenance agree on family, `n`, seed, and source model.
- Evidence: [`retraining_evidence.json`](../results/v4_tcdp/sibling_retraining/closure_20260908/validation_source_rerun/retraining_evidence.json), status `PASS`.

## Tolerances and checks

- Deterministic identity/map checks use the project-wide `1.0e-16` tolerance.
- Probability/vector and compilation checks use the registered `1.0e-12` probability tolerance.
- Training trajectory checks use the registered `1.0e-12` trajectory tolerance; this validation row is byte-identical rather than tolerance-matched.
- Focused regression: `venv/Scripts/python.exe -m pytest -q tests/v4_tcdp/test_sibling_validation_rerun.py` → `3 passed`.
- Artifact validation: `venv/Scripts/python.exe scripts/v4_tcdp/validate_artifacts.py --root results/v4_tcdp` → `294` JSON files, `72` JSONL rows, `9` payload hashes, `0` failures.

## Interpretation boundary

This is faithful replay of an available classical source-validation cell through the pinned sibling trainer. It is not a full-Fock validation, a photonic deployment result, a large-n sampled reproduction, a Qiskit reproduction, or evidence for the unadjudicated NULL-07 source-gap hypothesis. The remaining registered source rows retain their documented reference-only, blocked, or unavailable-input dispositions.
