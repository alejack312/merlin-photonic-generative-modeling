# v4 matched backend comparison

This report records the bounded n=4 ring smoke comparison. It is an artifact-backed control, not evidence of a photonic learning advantage. The raw arm is the exact NumPy IQP evaluator; the compiled arm is the same parameters through unquantized absolute-probability ideal CP maps; the deployed arm uses the catalog alpha-key quantization and the same CP-map composition boundary. The deployed arm is labelled `reference_only` because the full-Fock source/noise model is not validated.

## Matching contract

Both profiles use the same frozen train split, generator, final theta, MSB-first bit order, 20,000 accepted-sample evaluation budget, and Gaussian-on-Hamming kernel `exp(-H/(2 sigma^2))` with `sigma=.5*sqrt(n)`. Spatial MMD is reported for the rings profile only. Raw, compiled, and deployed vectors are stored separately; acceptance is reported separately from conditional distribution quality.

## Smoke artifacts

- [`rings_hamming` comparison](../results/v4_tcdp/rings/rings_hamming/n4_seed0_smoke/backend_comparison.json)
- [`rings_spatial_exact` comparison](../results/v4_tcdp/rings/rings_spatial_exact/n4_seed0_smoke/backend_comparison.json)

The unquantized raw/compiled control agrees to floating-point precision in both profiles. Quantization changes the deployed conditional vector and its MMD/TVD; this is the expected compilation distinction. The ideal-map acceptance mass is model success for the composed trace-decreasing instrument, not a measured hardware yield.

The ring study remains classical-only for training, and no sibling source experiment was silently relabelled as a photonic reproduction. No noisy compiled arm was launched because D1 source/loss decisions and full-Fock projection validation remain open.
