# Optional surrogate dependency gates
Date: 2026-09-28 · Scope: project · Recurs when: an experimental benchmark needs a third-party approximation backend without making it a default-suite dependency

## Context & constraints
- B2 selected quimb 1.15.0 and PauliPropagation.jl 0.8.2, both Apache-2.0, with the author implementation unavailable.
- The default Python suite must remain runnable without either backend, and no surrogate run is valid before exact asymmetric fixture agreement.
- TN/PPS resource settings are preregistration fields, not values to infer after a run.

## Approach
1. Put the Python backend in an exact optional extra and pin the Julia package in the existing project environment's compat section.
2. Keep the dependency checkpoint metadata-only: version, license, source, optional install boundary, author-code status, and required registration fields.
3. Add a complete-vector gate over asymmetric n=2 and n=3 exact fixtures with a stated absolute tolerance.
4. Test both exact pass and mass-preserving corruption failure before running the full suite.

## Decision rules that generalize
- IF a backend is not required by the default suite, THEN keep its import/install behind an explicit optional boundary.
- IF an approximation backend has a selected version, THEN record the exact version and license in code/config and documentation.
- IF a surrogate has not matched exact asymmetric fixtures, THEN do not measure capacity, runtime, memory, or scientific advantage.
- IF source author code is unavailable, THEN record that status and do not silently substitute it with an independent implementation.

## Mistakes avoided / dead ends
- Treating a dependency choice as permission to install it immediately would make the default environment and reproducibility gate ambiguous.
- Validating only symmetric fixtures could hide bit-order, sign, or normalization errors.
- Calling rung 1 a classical method would mislabel the exact/oracle reference.

## Verification
- `venv\\Scripts\\python.exe -m pytest -q tests\\v4_completion` → 35 passed.
- `venv\\Scripts\\python.exe -m pytest -q` → 764 passed, 1 skipped.
- Artifact validator → `failure_count=0`, 579 JSON files, 72 JSONL rows, 19 payload hashes.
- `quimb` was absent from the venv; the Julia executable was unavailable, so neither optional backend was installed or run.

## Next time (for a weaker model)
- Do: register exact versions, licenses, resource knobs, fixture IDs, and tolerance before any optional install.
- Don’t: let a package import happen at module import time or use a failed fixture run as a capacity result.

## Changed files
- `pyproject.toml` and `julia/Project.toml` — exact optional dependency pins.
- `src/merlin_iqp/experiments/correlator_audit.py` — dependency metadata and asymmetric pre-run gate.
- `docs/v4-b2-dependency-registration.md` — license, provenance, and installation boundary record.
