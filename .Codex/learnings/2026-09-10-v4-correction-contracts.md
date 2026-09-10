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
- `venv/Scripts/python.exe -m pytest -q` → 724 passed, 1 skipped.
- Post-review focused boundary → 129 passed; explicit sibling integration → 36 passed.
- `venv/Scripts/python.exe scripts/v4_tcdp/validate_artifacts.py --root results/v4_tcdp` → 579 JSON, 72 JSONL rows, 19 payload hashes, 0 failures.

## Next time (for a weaker model)
- Do: inspect the audit and ledger, identify exact producer inputs, then isolate refreshed outputs.
- Don't: promote a bounded smoke run, replay, or self-consistency test into a broader scientific claim.

## Changed files
- `scripts/v4_tcdp/`, `src/merlin_iqp/`, `tests/v4_tcdp/` — hardened measurement, control, checkpoint, deployment, and artifact contracts.

## Clean-release addendum — 2026-09-10
- IF validation counts include untracked outputs, THEN rerun from a detached committed checkout and report its counts separately; preserve the leftovers.
- IF the editable environment points to the original checkout, THEN explicitly set the clean checkout's `src` import path and verify the imported location.
- IF a required metric is absent or contradicts its arm, THEN reject it; range and reciprocal checks alone miss these cases.
- IF serialized artifacts are byte-hashed, THEN pin writer newlines and Git checkout attributes; compare actual LF and CRLF bytes before blaming provenance. The release probe exposed Windows-only sibling JSON hashes, repaired with LF output and original hashes retained.
- Verification: clean implementation `a732d65` passed 725 tests with 1 optional skip; explicit sibling integration passed 36; committed artifact validation passed 486 JSON, 72 JSONL rows, 18 payload hashes. Live 64 MiB allocation increased measured worker RSS by approximately 64 MiB.

- Final LF-checkout repair verification: `a8db410` passed 726 tests, 1 skipped; explicit sibling integration passed 37. Eight manifests changed only their comparison byte hash and serialization-correction metadata.
