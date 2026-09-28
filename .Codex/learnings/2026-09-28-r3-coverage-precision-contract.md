# Cell coverage and precision endpoints
Date: 2026-09-28 · Scope: project · Recurs when: a held-out-cell benchmark needs a primary coverage endpoint and a validity safeguard without a registered sample budget

## Context & constraints
- R3 uses whole data-hit cells; training-distribution MMD/TVD diagnostics cannot measure held-out-cell generalization.
- The owner selected coverage as primary and precision as safeguard, but deferred N, the precision floor, and effect size.
- No model comparison or default budget may be introduced by the metric helper.

## Approach
1. Accept observed sampled cell IDs rather than a budget parameter.
2. Count unique held-out cells hit at least once for coverage.
3. Count every sample landing in any data-hit cell for precision, so duplicates affect precision but not coverage.
4. Return observed counts and endpoint labels for an auditable result.
5. Return `None` for mathematically undefined ratios: empty held-out coverage or zero-sample precision.

## Decision rules that generalize
- IF the endpoint is cell coverage, THEN deduplicate held-out hits before dividing by held-out-cell count.
- IF the safeguard is valid-cell precision, THEN count samples, not unique cells.
- IF the denominator is zero, THEN report undefined explicitly rather than selecting a default.
- IF a metric can be computed from a split and samples alone, THEN keep it independent of model outputs and training objectives.

## Mistakes avoided / dead ends
- Reporting train MMD/TVD as the R3 endpoint would hide that the training distribution has zero mass on held-out cells.
- Counting duplicate hits as separate coverage would overstate generalization.
- Picking N or a precision threshold in code would override the deferred owner decision.

## Verification
- `venv\\Scripts\\python.exe -m pytest -q tests\\v4_completion\\test_generalization.py` → 13 passed.
- `venv\\Scripts\\python.exe -m pytest -q` → 768 passed, 1 skipped.
- Artifact validator → `failure_count=0`, 579 JSON files, 72 JSONL rows, 19 payload hashes.

## Next time (for a weaker model)
- Do: specify denominator behavior before writing endpoint code and test duplicates, invalid samples, empty sets, and zero samples.
- Don’t: launch a model comparison while N, precision floor, or effect size remain deferred.

## Changed files
- `src/merlin_iqp/experiments/generalization.py` — coverage/precision computation.
- `tests/v4_completion/test_generalization.py` — adversarial endpoint tests.
