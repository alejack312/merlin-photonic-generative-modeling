# Cell-level generalization holdouts
Date: 2026-09-28 · Scope: project · Recurs when: a benchmark must measure ring generalization from quantized cells rather than near-duplicate points

## Context & constraints
- The legacy rings loader retains a point-level 80/20 split and must remain historically reproducible.
- R3 requires pooling all 400 points through the existing `GridCodec`, then holding out whole data-hit cells.
- Validity is data-defined; R3 objectives, endpoint, and effect size remain owner-gated.

## Approach
1. Restore pooled point order from the loader's train/test IDs and concatenate their existing GridCodec indices.
2. Select a deterministic random subset of unique data-hit cells using a registered holdout seed, 20% rounded up, minimum three.
3. Expose training point IDs only from non-held-out cells; classify held-out cells as unseen-valid and never inspect model outputs.
4. Serialize the per-`n` cell lists, seed, RNG role, and validity rule in a dedicated split manifest.

## Decision rules that generalize
- IF a point-level test cell also appears in training, THEN do not call it an unseen-valid generalization test.
- IF a cell has at least one pooled data point, THEN it is valid; IF it is held out, label it unseen-valid; otherwise label it invalid.
- IF a new split is added, THEN keep its RNG separate from fit and sampling RNGs and record the held-out cell list.
- IF owner-defined objectives or endpoints are absent, THEN implement only the split contract and its tests.

## Mistakes avoided / dead ends
- Reusing the legacy point split would measure point separation, not cell generalization.
- Generating a new grid or using model probability support would violate the owner’s validity contract.
- Adding the new holdout to the legacy training path would silently change historical artifacts.

## Verification
- `venv\\Scripts\\python.exe -m pytest -q tests\\v4_completion\\test_generalization.py` → 9 passed.
- `venv\\Scripts\\python.exe -m pytest -q` → 762 passed, 1 skipped.
- Artifact validator → `failure_count=0`, 579 JSON files, 72 JSONL rows, 19 payload hashes.

## Next time (for a weaker model)
- Do: inspect the existing point IDs and codec contract before designing a new split.
- Don’t: change the historical dataset loader or begin R3 comparisons before owner decisions are recorded.

## Changed files
- `src/merlin_iqp/experiments/generalization.py` — registered cell-holdout contract and manifest.
- `tests/v4_completion/test_generalization.py` — whole-cell, validity, determinism, and input-validation tests.
