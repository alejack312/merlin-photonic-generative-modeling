# Plan additive experiments without changing the comparison
Date: 2026-09-05 · Scope: project · Recurs when: importing a sibling training pipeline into a new physical realization

## Context & constraints
- The ring generator's 462-outcome MerLin ansatz differs from the later IQP family.
- The sibling contains both iqp_bp and iqp_mmd with different dependencies, data contracts and gate support.
- Existing pipelines and historical results must remain available.

## Approach
1. Separate dataset, circuit, objective, estimator and physical backend identity.
2. Inventory actual source configurations and checkpoints before declaring experiment compatibility.
3. Share narrow target/model/kernel/checkpoint contracts across the two new callers.
4. Compare frozen checkpoints before comparing retraining trajectories or noisy outputs.

## Decision rules
- If a finite spatial kernel is not diagonal in Walsh coordinates, it still has a full Walsh representation; do not confuse representation with efficient diagonal-mixture sampling.
- If size, graph, generator weight, kernel mixture or data split changes, label the run an adaptation rather than faithful reproduction.
- If a physical backend lacks support, retain the source row and missing capability; do not substitute a qubit reference labeled photonic.
- If noise/NAT choices remain open, let independent classical reproduction proceed under explicit configurations.

## Verification
- Direct spatial MMD equals full Walsh form at N=8: .1638180415093075; spatial transform is non-diagonal, Hamming transform diagonal to 1.73e-17.
- Plan checks: 52 unique requirement IDs, local links resolve, all three requested workstreams covered, old Phase 25 preserved.
- Planning only; no new training or physical deployment performed.

## Next time
- Do: replay a source checkpoint, then one update, then a full trajectory before assigning substrate differences.
- Don't: silently equate the same dataset with the same circuit or metric.

## 2026-09-06 implementation addendum

### Reusable ring procedure

1. Reproduce the source data with sklearn, split integer row IDs using the same seed, and derive normalization only from the training rows.
2. Keep normalized data NumPy/float32 and implement the row-major `2**n` grid/`int(bitstring, 2)` codec without importing torch or a photonic backend.
3. Build both spatial-exact and Hamming profiles on the same `IQPModel`/`Trainer`; persist hashes, transform, mapping, histograms, quantization, final probabilities and exact decoded centers.
4. Guard the training step against backend imports, run n=4 smoke profiles, and register larger cells without silently launching an expensive sweep.

### Decision rules

- If the original loader uses train-derived preprocessing, hash split IDs and transform values; a matching sample count is insufficient evidence.
- If a metric changes kernel geometry, report both panels and do not rank raw MMD values across kernels.
- If photonic support is absent, write `INCONCLUSIVE` with the missing capability; never relabel a classical or qubit result as photonic.

### Verification

- `venv/Scripts/python.exe -m pytest -q tests/v4_tcdp/test_classical_core.py tests/v4_tcdp/test_rings_pipeline.py` passed.
- `venv/Scripts/python.exe -m py_compile ...` passed for the three owned Python files.
- Both n=4 seed-0 three-step smoke CLIs passed; exact values are in `docs/v4-rings-study.md` and the isolated manifests.

### Changed files

- `src/merlin_iqp/experiments/datasets.py` — frozen rings data, codec, hashes and diagnostics.
- `src/merlin_iqp/experiments/rings.py` — shared classical profiles, guard, metrics and artifacts.
- `scripts/v4_tcdp/train_rings.py` — bounded smoke CLI.
