# Phase 28: classically trained IQP rings

## D3 initialization and replication note

The settled D3 choice makes sibling-style data-dependent parity initialization at scale `0.1` the primary initialization for both two-ring profiles. `small_angle` and `uniform` remain explicit CLI/configuration ablations. The data-dependent path derives moments only from the exact train target after grid projection; it does not use test data or raw continuous coordinates. Every run artifact records the initialization method and scale, seed, initial/final parameter hashes, target provenance, and replication identity. Seeds that reproduce the same deterministic parameterization are labeled `duplicate_deterministic` and are not treated as independent replicas.

The smoke numbers below predate this D3 choice and were generated under the historical `small_angle` initialization. They remain historical context, not primary data-dependent-init evidence; no milestone completion is claimed from them.

Status: the additive classical ring pipeline is implemented. The historical n=4 smoke profiles ran on 2026-09-06 with three Adam updates and small-angle initialization; they are not primary D3 evidence. The selected primary profiles now have 20 completed main artifacts: both kernels × n=6,8 × five seed IDs, 300 Adam updates, with data-dependent parity initialization at scale 0.1. Because that initialization is deterministic for a fixed target, each n/profile group records `n_unique=1` and labels seeds 1–4 as `duplicate_deterministic`, not independent replicas.

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

## Primary main-run evidence

The 20 main artifacts are reproducible from `scripts/v4_tcdp/train_rings.py --main`. For each fixed profile and n, all five seed IDs produce the same initial and final parameter hashes because parity initialization and the exact NumPy update are deterministic; this is recorded as a replication fact rather than seed variability. The main runs establish execution and provenance coverage, not a claim of generalization or a successful photonic realization.

Artifacts:

- [`rings_spatial_exact` smoke manifest](../results/v4_tcdp/rings/rings_spatial_exact/n4_seed0_smoke/manifest.json)
- [`rings_hamming` smoke manifest](../results/v4_tcdp/rings/rings_hamming/n4_seed0_smoke/manifest.json)

## Backend boundary and legacy context

The training step is protected by a classical-only import guard that rejects torch, Perceval, and MerLin backend imports. The registered n=4 spatial and Hamming smoke checkpoints were subsequently evaluated through the fixed-photon final-only photonic adapter with matching qubit references; those two artifacts are bounded `PASS` controls, not evidence for n=6/n=8 photonic deployment or a photonic advantage. The shared-gate physical controls show a material final-only/intermediate discrepancy, so the intermediate boundary remains unsupported.

The historical 462-bin `QuantumLayer.simple` ansatz remains contextual only. It has a different latent-input ansatz and output space from this `2**n` IQP model. Native MMD values from those unmatched spaces are not compared.
