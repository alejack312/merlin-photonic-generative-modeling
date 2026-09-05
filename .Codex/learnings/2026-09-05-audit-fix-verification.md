# Auditing claims and resumable sweep invariants
Date: 2026-09-05 · Scope: project · Recurs when: an agent reports an audit fix but the repository still contains claims or evidence paths that were not independently checked

## Context & constraints
- The repo combines Python/Perceval sweeps, regression gates, and canonical research documents.
- Historical planning/audit records must remain intact; only active claims and current state should be corrected.
- Perceval logging required a workspace-local `PCVL_PERSISTENT_PATH` for reproducible tests.

## Approach
1. Read the independent audit findings and search canonical docs for each flagged phrase.
2. Verify chunk filenames, manifests, and loaded array lengths before concatenation.
3. Make null-result parametrization fail on missing or vacuous evidence and cover absolute values.
4. Narrow scientific language to what the measured controls establish; update active milestone metadata.
5. Run focused tests, compilation, diff checks, and the full suite before committing named files only.

## Decision rules that generalize
- IF a null model uses the same analytic `q(theta)` as the circuit THEN call it a reproducibility/reference check, not proof that the circuit landscape has no effect.
- IF an entangling block stays fixed-size as `n` grows THEN do not label the family an asymptotic hardness candidate.
- IF a variance comparison uses one deterministic vector per size THEN describe it as a diagnostic, not a matched random-draw variance test.
- IF a resumable combiner trusts chunk metadata or array shape THEN bind manifest intervals to filenames and reject row-count mismatches before pooling.
- IF a required evidence file or ratio group is absent THEN fail the gate instead of skipping parametrization.

## Mistakes avoided / dead ends
- Prior “fixed” reports missed stale canonical wording and did not bind manifest intervals to filenames.
- A clean focused test run without the Perceval log-path override failed during collection; the override made the full run reproducible.

## Verification
- `venv\\Scripts\\python.exe -m pytest -q` → 506 passed in 487.04s.
- Focused audit regressions → 17 passed; compileall and `git diff --check` passed.
- Canonical phrase search found no remaining overclaims; only the pre-existing technical-note edit remains unstaged.

## Next time (for a weaker model)
- Do: start from the audit's exact phrases, inspect active docs and contracts, then test the evidence gates.
- Don't: accept an agent's “fixed” summary without a fresh search and an end-to-end suite.

## Changed files
- `scripts/v3_*/*sweep.py` — validate chunk manifests and array lengths.
- `tests/scripts/v3_trainability/test_chunk_validation.py` — add malformed-array regressions.
- `tests/v3_correction/test_null_results.py` — require non-vacuous evidence coverage.
- `docs/*.md`, `README.md`, `.planning/REQUIREMENTS.md` — narrow audited claims.
