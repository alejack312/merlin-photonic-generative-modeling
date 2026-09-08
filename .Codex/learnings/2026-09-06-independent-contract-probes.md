# Independent numerical contract probes
Date: 2026-09-06 · Scope: project · Recurs when: a scientific implementation passes its own tests but evidence remains incomplete.

## Context & constraints
- Audit implementation separately from physical qualification and owner interpretation.
- Keep existing scientific artifacts and sibling source unchanged.

## Approach
1. Read the actual caller and the acceptance contract together.
2. Construct asymmetric, boundary, and resume counterexamples independently of existing fixtures.
3. Inspect canonical output metadata for mismatched code provenance and scientific contrasts.
4. Trace alleged missing inputs back to the source factory and recorded seeds.

## Decision rules that generalize
- If two-qubit fixtures use only swap-symmetric gates, add X tensor I on nonadjacent qubits before trusting axis order.
- If resume claims deterministic replay, vary constructor settings to test restoration or explicit rejection.
- If a getattr fallback performs validation, check eager evaluation with the real typed object.
- If an ideal comparison changes quantization between arms, separate compilation error before interpreting a deployment gap.
- If a control discards updates that the treatment uses, equal evaluation counts do not establish matched optimization.
- If source data is synthetic, check the original generator and recorded RNG seed before declaring an external blocker.

## Verification
- v4 suite: 114 passed; independent probes still reproduced bundle, order, resume, NAT std, physicality and KL serialization defects.
- Probe script: docs/audits/2026-09-06-v4-implementation-probes.py.
- These are defect reproductions; no implementation fixes were made or certified.

## Next time
- Do test public adapters and real artifact writers, not just isolated numerical helpers.
- Don't treat missing scientific evidence and a reproducibly incorrect result as the same status.

## Follow-up: repair-integration checks (2026-09-06)
- If errors accumulate with Python max, inject NaNs and empty trajectories before accepting a numerical equality gate.
- If a CLI reports a config hash, vary that file and confirm execution uses it or rejects the mismatch.
- If run identity omits ablation settings, write two configurations into a temporary output root and check for overwrite.
- If a comparison copies manifest hashes, mutate a valid-shaped numerical artifact and require rejection before evaluation.
- If a continuation helper passes, inspect caller artifacts: treatment and control must branch from the same start, not form a sequential chain.
- Verified on b7ed7e8: 129 focused and 636 full tests passed; new independent failure probes still exposed these integration defects. No fixes were made in the review.

## Follow-up: identity and artifact reuse (2026-09-06, d16d9cc)
- If parsing Git porcelain, preserve leading whitespace; test the first unstaged modification in a real temporary repository.
- If hashing raw arrays, mutate an element hidden by NumPy's abbreviated display; identity must cover bytes, not repr.
- If resuming Adam, remove moments/counters and require rejection before state changes; matching learning rates alone are insufficient.
- If reusing artifacts, test both a missing array and a repeat after adding another seed. Keep run identity separate from changing group statistics.
- Verified: five counterexamples; full suite 652 passed/1 skipped; explicit sibling integration 8 passed. Saved ring model hashes matched in 22 manifests. No fixes or scientific closure were claimed.

## Follow-up: third-repair contract closure (2026-09-06)
- Preserve the two Git porcelain columns when scoping dirty paths; trimming the first status line can certify an edited source tree as clean.
- Derive composite dataset identities from named full-content hashes, never abbreviated array representations.
- Require complete Adam moments and step counters at resume, reject non-finite histories, and fail non-finite training trajectories before writing checkpoints.
- Compare immutable run identity separately from replica-group observations, then validate every promised serialized array before idempotent reuse.
- Verified: focused boundary regressions 35 passed; full suite 658 passed/1 skipped; sibling HEAD remained `f6d6ebe87e4ee1de10893c6ea2f0ffa367493336` and clean. Canonical v4 result files were not regenerated.

## Follow-up: registered source-validation closure (2026-09-08)
- If a recursive config diff uses `dict.get`, a missing field and an explicit `null` field can compare equal; use a per-level sentinel and add both deletion and insertion tests.
- When a newly available sibling row is rerun, compare substantive outputs byte-for-byte where deterministic, validate only explicitly declared schema/output adaptations, and record source identity before and after execution.
- Keep source-validation replay, faithful training, checkpoint replay, and physical deployment as separate evidence kinds even when their numerical outputs agree.
- Verified: exact n=6 anti-concentration validation rerun passed with byte-identical substantive JSON/CSV outputs; the missing/null validator regression passed; full suite 684 passed/1 skipped; artifact validation 294 JSON/72 JSONL/9 payload hashes/0 failures; sibling remained clean at `f6d6ebe87e4ee1de10893c6ea2f0ffa367493336`.
