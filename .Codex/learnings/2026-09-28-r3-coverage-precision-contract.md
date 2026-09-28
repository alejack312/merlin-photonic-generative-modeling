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

## 2026-09-29 addendum: known-support null and bounded first-run panel

## Decision rules that generalize
- IF a reference samples uniformly over all valid cells, THEN use `V = len(valid_cells)`, precision `1.0`, and coverage `1 - (1 - 1/V)^N`; do not substitute total cells or held-out cells.
- IF a reference is compared with sprayer/oracle anchors, THEN assert `floor <= known_support <= ceiling` and test corrupted denominators before accepting the fixture.
- IF a staged experiment has an approved time cap, THEN measure one representative pilot first and record the projected cost before running the panel.
- IF the owner requests raw benchmark output, THEN write machine-readable rows and labelled MEASURED/AGAINST NULLS/EXPLORATORY tables without interpretation or model comparison.

## Verification
- `venv\Scripts\python.exe -m pytest -q tests\v4_completion\test_generalization.py` → 23 passed, including corrupted `V=2^n` and `V=k` rejection and 5,000-repetition Monte Carlo agreement.
- Pilot: one n=6 B1+B2 checkpoint `0.2640228999662213 s`; all R3 reference rows `0.1089036000194028 s`; projected panel `5.389361599343829 s` against the 7-hour cap.
- First-run artifacts: 20 B1 rows, 180 B2 rung-1–3 rows, 36 R3 reference rows; no model comparison; TN/PPS pending.
- `venv\Scripts\python.exe -m pytest -q` → 794 passed, 1 skipped in 503.27s.
- `venv\Scripts\python.exe scripts\v4_tcdp\validate_artifacts.py --root results\v4_tcdp` → PASS, 579 JSON files, 72 JSONL rows, 19 payload hashes.
