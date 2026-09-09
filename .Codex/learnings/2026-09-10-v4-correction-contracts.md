# Evidence-bound correction passes
Date: 2026-09-10 · Scope: project · Recurs when: an independent audit finds that v4 results can pass while inputs, process measurements, controls, or artifact semantics are incomplete.

## Context & constraints
- Preserve historical artifacts, legacy pipelines, and the sibling checkout; use fresh output namespaces for regenerated evidence.
- Keep acceptance mass, conditional distributions, and attempts-per-accepted-sample as separate quantities.
- A passing unit test or analytic self-consistency check is scoped evidence, not a general full-Fock certificate.

## Approach
1. Map every finding to an implementation change, a regression test, and a refreshed artifact or an explicit non-claim.
2. Measure the allocating worker, not the launcher; record PID, peak RSS, source identity, and exact registered sizes.
3. Recompute mutation-control metrics from mutated objects and validate both mutation application and mass preservation; report metric insensitivity separately.
4. Validate semantic artifact invariants after JSON parsing, including finite values, probability mass, acceptance, reciprocal throughput, and complete resource status.
5. Regenerate evidence in a new namespace only after source changes are settled, then run the full suite and the explicit external integration.

## Decision rules that generalize
- IF a result says PASS while an accepted mass is zero, incomplete, or not independently checked, THEN fail qualification even if conditional TVD is good.
- IF a control mutates a vector/map, THEN derive its post-mutation metrics from that object; constants are not evidence.
- IF a source/config/status command fails, THEN record unavailable or fail closed; never infer clean identity from empty output.
- IF a checkpoint omits required optimizer/history state, THEN reject it atomically before mutating the trainer.
- IF a deployment is eta=1 analytic replay, THEN label it as a compiled-model reference, not independent photonic evidence.
- IF a scope is model-derived or small-n, THEN keep larger-n/full-Fock claims INCONCLUSIVE until those exact checks run.

## Mistakes avoided / dead ends
- Reusing old ring outputs hid whether final control logic was present; fresh `metrics_v3` artifacts removed that ambiguity.
- Passing the process-wide artifact validator did not guarantee semantic validity until zero acceptance, bad mass, and incomplete resources were explicit tests.
- A mutation can leave a saturated metric unchanged; this is not the same as a mutation failing to apply.

## Verification
- `venv/Scripts/python.exe -m pytest -q` → 719 passed, 1 skipped.
- Focused correction suite → 186 passed, 1 skipped; explicit sibling integration → 35 passed.
- `venv/Scripts/python.exe scripts/v4_tcdp/validate_artifacts.py --root results/v4_tcdp` → 499 JSON, 72 JSONL rows, 17 payload hashes, 0 failures.

## Next time (for a weaker model)
- Do: inspect the audit and ledger, identify exact producer inputs, then isolate refreshed outputs.
- Don't: promote a bounded smoke run, replay, or self-consistency test into a broader scientific claim.

## Changed files
- `scripts/v4_tcdp/`, `src/merlin_iqp/`, `tests/v4_tcdp/` — hardened measurement, control, checkpoint, deployment, and artifact contracts.
