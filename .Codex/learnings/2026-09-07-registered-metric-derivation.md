# Bounded derivation from registered experiment artifacts
Date: 2026-09-07 · Scope: project · Recurs when: metric panels must be completed from existing registered runs without starting a new training sweep

## Context & constraints
- Existing ring run directories already contain validated manifests, datasets, and checkpoints.
- Comparison outputs are immutable: rerunning a cell with timing differences must not overwrite its artifact.
- Scope limits require stopping before unapproved registered cells are generated.

## Approach
1. Enumerate only existing registered run directories.
2. Derive raw, unquantized compiled control, quantized compiled, and deployed panels with the existing comparison CLI.
3. Validate direct/Walsh/trainer Hamming-MMD cross-checks and preserve immutable-artifact failures as non-overwrite signals.
4. Record exact completed and intentionally unrun cells in a scoped evidence note.

## Decision rules that generalize
- IF the output path already contains a different valid artifact THEN retain it and do not overwrite it.
- IF a derivation would expand beyond the explicitly bounded registered set THEN stop and report the remaining cells.
- IF source anticoncentration or shot uncertainty inputs are absent THEN record the declared not-computed/not-applicable state.

## Verification
- `venv\\Scripts\\python.exe -m pytest -q tests\\v4_tcdp\\test_comparison.py tests\\v4_tcdp\\test_nat.py tests\\v4_tcdp\\test_resource_pilot.py` → 28 passed.
- Fourteen comparison manifests parse successfully; all report Hamming cross-check status PASS.

## Changed files
- `results/v4_tcdp/metrics/registered-comparison-evidence.md` — bounded completion and remaining-cell record.
