# v4 matched backend comparison

This report records the bounded n=4 ring smoke comparison. It is an artifact-backed control, not evidence of a photonic learning advantage. The raw arm is the exact NumPy IQP evaluator; the primary compiled arm uses the catalog alpha-key quantization through absolute-probability ideal CP maps; the deployed arm uses the same compiled parameters and the fixed-photon final-only CP-map composition boundary validated by the dedicated n=2/n=3 Perceval controls. An explicit unquantized compiled arm is retained as `ideal-unquantized-control`. The deployed arm remains qualified as a fixed-photon final-only model-derived/reference arm; it is not a hardware result, multiphoton result, or intermediate-projection result.

## Matching contract

Both profiles use the same frozen train split, generator, final theta, MSB-first bit order, 20,000 accepted-sample evaluation budget, and Gaussian-on-Hamming kernel `exp(-H/(2 sigma^2))` with `sigma=.5*sqrt(n)`. Spatial MMD is reported for the rings profile only. Raw, compiled, and deployed vectors are stored separately; acceptance is reported separately from conditional distribution quality.

## Smoke artifacts

- [`rings_hamming` comparison](../results/v4_tcdp/rings/rings_hamming/n4_seed0_smoke/backend_comparison.json)
- [`rings_spatial_exact` comparison](../results/v4_tcdp/rings/rings_spatial_exact/n4_seed0_smoke/backend_comparison.json)

The raw/unquantized control agrees to floating-point precision in both profiles. The primary compiled/deployed arms share effective quantized parameters; at eta=1 their conditional vectors and success masses agree. At eta=.9, loss changes absolute acceptance while conditional quality is reported separately. The ideal-map acceptance mass is model success for the composed trace-decreasing instrument, not a measured hardware yield.

The ring study remains classical-only for training, and no sibling source experiment was silently relabelled as a photonic reproduction. The fixed-photon final-only arm is now included for the registered n=4 smoke cells because the dedicated n=2/n=3 controls pass; it remains a model-derived/reference result, not hardware or multiphoton evidence. Intermediate projection and larger-n photonic deployment remain outside scope.

## Registered sibling substrate comparisons

The sibling chain is recorded separately from the rings report. The comparator in [`compare_sibling_backends.py`](../scripts/v4_tcdp/compare_sibling_backends.py) consumes the independently verified source-trainer artifacts and regenerates the source empirical target from the pinned recipe. It compares the same frozen generator, final parameters, samples, source bandwidth, and MSB-first codec across the sibling IQP implementation, the local equivalent NumPy IQP evaluator, an unquantized compilation control, the quantized compiled CP-map, and the deployed fixed-photon map.

The [repaired eight-cell closure summary](../results/v4_tcdp/sibling_comparisons/closure_20260909_final/summary.json) is `PASS`. The comparison is artifact-backed and profile-qualified; the bandwidth and Ghosh–Kim cells with equal `(n, sigma)` values have distinct source-profile IDs. Each cell reports Hamming MMD2, TVD, marginal panels, acceptance mass and attempts per accepted sample separately. The deployed arm uses `eta=0.9`, and its conditional shape remains equal to the compiled vector while its absolute accepted mass follows `eta**n * model_success` within `1.0e-16`.

The source/local probability comparison uses the project’s existing `1.0e-12` probability-vector tolerance; the largest observed residual is `1.3877787807814457e-16`. This is distinct from the `1.0e-16` deterministic/map checks and the `1.0e-12` source training-trajectory tolerance. No arm is labeled as a direct physical n=9 full-Fock result: the CP-map deployment is model-derived/reference-only, with the direct physical validation boundary still limited to the registered n=2/n=3 final-only controls.

## 2026-09-10 correction refresh

The 22 existing ring comparison cells were regenerated under [`results/v4_tcdp/corrections_20260910/metrics_v2`](../results/v4_tcdp/corrections_20260910/metrics_v2). These artifacts add computed target-support validity, distinguish metric sensitivity from mutation application, and retain separate acceptance and conditional metrics. The eight-cell sibling comparison was regenerated at [`correction_20260910_v2/summary.json`](../results/v4_tcdp/sibling_comparisons/correction_20260910_v2/summary.json). Historical artifacts remain preserved. See the [dated correction report](v4-correction-pass-2026-09-10.md) for the complete finding disposition.
