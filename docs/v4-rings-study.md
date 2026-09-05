# Phase 28: classically trained IQP rings

Status: the additive classical ring pipeline is implemented. The n=4 smoke profiles ran on 2026-09-06 with three Adam updates, seed 0, `chain_1d(4, 3)`, learning rate 0.05, and small-angle initialization with standard deviation 0.1. The n=6 and n=8 profiles are registered in the manifest with five seeds and 300 updates, but those main runs were not launched in this bounded implementation pass.

## Reproduced data and codec

`load_rings_dataset` reproduces `make_circles(n_samples=400, random_state=42)`, the 320/80 `train_test_split(test_size=0.2, random_state=42)`, and the legacy loader's train-derived min/max transform. Normalized coordinates are stored as float32 for compatibility with the original loader. The n=4 dataset hash is `2a021db64ff4ce325765025da21cf8b6754a61648dbfa87050ee3853b4c949ae`; the focused tests pin the split and normalized-array hashes.

For each n, the codec has `2**ceil(n/2)` rows and `2**floor(n/2)` columns over `[-0.1, 1.1]²`. Cells are row-major, bitstrings are MSB-first, and `index = int(bitstring, 2)`. Nearest-center assignment uses the lowest row-major index on a tie. Raw and normalized splits, IDs, transform, centers/mapping, train/test histograms, and quantization diagnostics are persisted in each dataset artifact. Decoded model output is the exact weighted set of grid centers; no jitter is added.

## Smoke evidence

The two profiles use the same NumPy-only `IQPModel` and `Trainer` and differ only in their objective kernel. Values below are exact JSON artifact values from the n=4 smoke runs.

| profile | initial loss | final loss | train spatial MMD² | test spatial MMD² | train Hamming MMD² | test Hamming MMD² | test TVD |
|---|---:|---:|---:|---:|---:|---:|---:|
| `rings_spatial_exact` | 1.0579791825976854 | 0.6773627388036133 | 0.6773627388036133 | 0.6829325804260553 | 0.4246001561119608 | 0.43375763051375377 | 0.8644530125264482 |
| `rings_hamming` | 0.6289767125264263 | 0.4248202431456149 | 0.6777522079966285 | 0.6833195340147248 | 0.4248202431456149 | 0.43398036183254896 | 0.8645913300529666 |

The geometry quantization-floor RMS error is `0.1856589447436645` for this n=4 grid. The runs are poor-fit smoke measurements, not evidence of successful learning or generalization. Spatial and Hamming MMD² values are reported side by side and are not treated as directly rankable scales.

Artifacts:

- [`rings_spatial_exact` smoke manifest](../results/v4_tcdp/rings/rings_spatial_exact/n4_seed0_smoke/manifest.json)
- [`rings_hamming` smoke manifest](../results/v4_tcdp/rings/rings_hamming/n4_seed0_smoke/manifest.json)

## Backend boundary and legacy context

The training step is protected by a classical-only import guard that rejects torch, Perceval, and MerLin backend imports. No photonic ring deployment adapter was available in this owned Phase 28 slice, so photonic evaluation is recorded as `INCONCLUSIVE`; no simulator output is relabeled as an independent photonic result.

The historical 462-bin `QuantumLayer.simple` ansatz remains contextual only. It has a different latent-input ansatz and output space from this `2**n` IQP model. Native MMD values from those unmatched spaces are not compared.
