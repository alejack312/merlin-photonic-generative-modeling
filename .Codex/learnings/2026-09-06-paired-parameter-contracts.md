# Keep parameter identity attached to the object it describes
Date: 2026-09-06 · Scope: project · Recurs when: scientific adapters normalize or sort labeled parameter arrays.

## Context and approach
- The v4 NAT API accepts positional pair values and pair-keyed mappings.
- Compare equivalent forms using an intentionally unsorted pair list and asymmetric values, at zero training steps.
- Compare the compiled state and output distribution before investigating optimizer or noise behavior.

## Decision rules
- If objects are reordered, reorder their attached values together; sorting only pair labels changes the requested circuit.
- If a mapping and sequence describe the same input, require equal outputs or explicitly reject ambiguous positional order.
- If reporting optimization moves, distinguish accepted updates from coordinates with different endpoints; test repeated moves on one coordinate.

## Verification
- At 8f1298f, equivalent sequence/mapping inputs produced TVD 0.21112926434753415 before training.
- Canonical n=4 NAT evidence labeled both 3 changed coordinates and 163 accepted updates as pair_moves.
- Evidence: docs/audits/2026-09-06-v4-third-repair-review.md and its probe script.
- These were audit reproductions; no implementation repair or scientific closure was claimed.

## Next time
- Test association invariance before adding more symmetric fixtures or rerunning expensive experiments.

## Follow-up: fourth-repair verification (2026-09-06)
- If a canonical order differs from caller order, bind positional values to the caller labels before sorting; verify sequence and mapping forms at zero optimization steps.
- If a validator can fail after mutating live state, validate into local variables and commit only after all fields pass.
- If a source identity depends on Git, use NUL-delimited status/listing and fail closed on observation errors.
- If an artifact has a summary sidecar, compare the complete immutable summary snapshot, not only its identifier.
- If replay loads external numeric arrays, validate raw values before dtype coercion and reject non-finite evidence before JSON export.
- Verified after repair: 15 targeted regressions passed; 665 full-suite tests passed with 1 optional skip; explicit sibling integration passed 8 tests; canonical NAT JSON now reports accepted `pair_moves` and endpoint `pairs_changed` separately. Scientific interpretation remains provisional.
