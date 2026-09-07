# v4 matched backend comparison

This report records the bounded n=4 ring smoke comparison. It is an artifact-backed control, not evidence of a photonic learning advantage. The raw arm is the exact NumPy IQP evaluator; the primary compiled arm uses the catalog alpha-key quantization through absolute-probability ideal CP maps; the deployed arm uses the same compiled parameters and the fixed-photon final-only CP-map composition boundary validated by the dedicated n=2/n=3 Perceval controls. An explicit unquantized compiled arm is retained as `ideal-unquantized-control`. The deployed arm remains qualified as a fixed-photon final-only model-derived/reference arm; it is not a hardware result, multiphoton result, or intermediate-projection result.

## Matching contract

Both profiles use the same frozen train split, generator, final theta, MSB-first bit order, 20,000 accepted-sample evaluation budget, and Gaussian-on-Hamming kernel `exp(-H/(2 sigma^2))` with `sigma=.5*sqrt(n)`. Spatial MMD is reported for the rings profile only. Raw, compiled, and deployed vectors are stored separately; acceptance is reported separately from conditional distribution quality.

## Smoke artifacts

- [`rings_hamming` comparison](../results/v4_tcdp/rings/rings_hamming/n4_seed0_smoke/backend_comparison.json)
- [`rings_spatial_exact` comparison](../results/v4_tcdp/rings/rings_spatial_exact/n4_seed0_smoke/backend_comparison.json)

The raw/unquantized control agrees to floating-point precision in both profiles. The primary compiled/deployed arms share effective quantized parameters; at eta=1 their conditional vectors and success masses agree. At eta=.9, loss changes absolute acceptance while conditional quality is reported separately. The ideal-map acceptance mass is model success for the composed trace-decreasing instrument, not a measured hardware yield.

The ring study remains classical-only for training, and no sibling source experiment was silently relabelled as a photonic reproduction. The fixed-photon final-only arm is now included for the registered n=4 smoke cells because the dedicated n=2/n=3 controls pass; it remains a model-derived/reference result, not hardware or multiphoton evidence. Intermediate projection and larger-n photonic deployment remain outside scope.
