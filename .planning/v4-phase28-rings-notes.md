# Phase 28 ring implementation notes

Status: historical implementation notes, superseded by the registered n=6/n=8 classical runs and the n=4 fixed-photon photonic outputs under `results/v4_tcdp/deploy/registered_v2_ring_photonic_*.json`. The older `registered_not_launched` and photonic `INCONCLUSIVE` wording below is retained as provenance, not current status.

Date: 2026-09-06

## Delivered

- Added the NumPy-only ring dataset/codec adapter in `src/merlin_iqp/experiments/datasets.py`.
- Added `rings_spatial_exact` and `rings_hamming` profile definitions, shared-model training, the classical-only import guard, metrics, exact center decoding, and JSON/NPZ artifact writing in `src/merlin_iqp/experiments/rings.py`.
- Added `scripts/v4_tcdp/train_rings.py` with small defaults: n=4, seed 0, three steps. n=4,6,8 are registered; n=6/8 main status is `registered_not_launched`.
- Added focused acceptance tests in `tests/v4_tcdp/test_rings_pipeline.py`.
- Added the study report in `docs/v4-rings-study.md`.

## Evidence

- `venv/Scripts/python.exe -m pytest -q tests/v4_tcdp/test_rings_pipeline.py` -> **7 passed**.
- `venv/Scripts/python.exe -m py_compile src/merlin_iqp/experiments/datasets.py src/merlin_iqp/experiments/rings.py scripts/v4_tcdp/train_rings.py` -> **PASS**.
- Smoke CLI -> **PASS** for both profiles at n=4, seed 0, three steps. Artifacts are under `results/v4_tcdp/rings/{profile}/n4_seed0_smoke/`.
- Dataset reproduction check against `merlin_iqp.generator.data.load_circles_data` -> normalized train and test arrays **exactly equal**; split sizes are 320/80.

Exact smoke metrics are recorded in `docs/v4-rings-study.md` and each manifest. The n=4 quantization-floor RMS is `0.1856589447436645`. Photonic evaluation is **INCONCLUSIVE** because a validated ring deployment adapter is outside this owned slice.

## Scope decisions

The row-major MSB-first codec is retained because it is the existing `2**n` target-grid convention. The legacy 462-bin ansatz is preserved as context only; unmatched native MMDs are not compared. No existing source module, test, generator, checkpoint, result, CLI, `experiments/__init__.py`, deploy path, or sibling-inventory artifact was edited.
