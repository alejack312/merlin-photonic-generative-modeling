# v4 metrics and NAT scoped evidence

Date: 2026-09-07. This note records only the bounded metrics/NAT work owned by this checkout. It does not alter the v4 ledger or synthesis reports.

## Metrics

`compare_backends.py` now writes comparison artifacts under `results/v4_tcdp/metrics/`. Each comparison keeps the exact raw IQP vector, unquantized compilation control, quantized compiled vector, and deployed fixed-photon vector as separate arms. Per-arm panels include TVD, true forward KL with explicit infinite status, labeled floor scores, expected coverage, expected occupancy, support validity, order-1/order-2 MSB-first marginal TVDs, spatial MMD where centers are available, and normalized Hamming-Gaussian MMD².

Hamming MMD² is checked three ways: direct normalized kernel matrix, Walsh form, and the shared trainer objective. The smoke manifests report maximum absolute agreement at or below `1.67e-16`. Source anticoncentration is explicitly omitted when no declared source-AC input exists; exact population vectors report uncertainty as not applicable rather than inventing shot intervals.

The control panel uses probability-mass transfers for metric-specific distribution mutations, a separate unnormalized-map mutation, and a separate acceptance-only mutation. These controls preserve the distinction between conditional distribution quality and independently measured/model-derived acceptance.

Smoke artifacts:

- `rings_hamming__n4_seed0_smoke__matched_backends/backend_comparison.json`
- `rings_spatial_exact__n4_seed0_smoke__matched_backends/backend_comparison.json`

## NAT

`run_nat.py --matched-continuation` writes one frozen warm start and two continuation arms. The report checks common starting-state hash, initial parameterization, optimizer, budget, deterministic checkpoint selection, target improvement from the warm-start target loss, distance to the frozen warm-start reference distribution, and fixed-photon model acceptance/attempts separately. `--equal-budget-control` is labeled `fixed_pair_equal_budget_control` and is an ablation only.

The smoke report uses one n=4 seed and one update to keep this evidence bounded. It is a contract/control artifact, not NAT efficacy evidence for the registered n={4,6,8}, five-seed, 150-step attempts. No claim of NAT superiority or conditional noise effect is made under the fixed-photon uniform-loss model.

## Verification

- `venv/Scripts/python.exe -m pytest -q tests/v4_tcdp/test_comparison.py tests/v4_tcdp/test_nat.py` — 23 passed.
- `venv/Scripts/python.exe scripts/v4_tcdp/compare_backends.py results/v4_tcdp/rings/rings_hamming/n4_seed0_smoke` — completed; metrics manifest emitted.
- `venv/Scripts/python.exe scripts/v4_tcdp/compare_backends.py results/v4_tcdp/rings/rings_spatial_exact/n4_seed0_smoke` — completed; metrics manifest emitted.
- `venv/Scripts/python.exe scripts/v4_tcdp/run_nat.py --n 4 --seed 0 --steps 1 --matched-continuation --equal-budget-control --output results/v4_tcdp/nat/metrics/n4_seed0_metrics_smoke.json` — completed; five NAT artifacts emitted.

The workspace had unrelated concurrent edits in deployment and sibling-reproduction surfaces. They were left untouched and are excluded from this scoped commit.
