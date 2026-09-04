# Adversarial null-result review
Date: 2026-09-03 · Scope: project · Recurs when: a corrected research claim replaces a failed metric interpretation

## Context & constraints
- v3.1 corrections reinterpret trainability and photon-loss metrics rather than rerun the original studies.
- The repository uses small, exact-enumeration Python models and keeps historical claims in the docs.
- A passing regression suite is not sufficient when its tested domain or tolerance is weaker than the prose claim.

## Approach
1. Extract every corrected or newly positive claim from the dated sections and README mirror.
2. Derive the circuit-free metric output, including normalization, conditioning, and units.
3. Check the formula against implementation, CSVs, and the exact test parameter ranges.
4. Separate a valid pipeline null from any claim about physical trainability, computational hardness, or novelty.

## Decision rules that generalize
- IF a Gaussian bandwidth is merely smaller than bin spacing, THEN compute the actual nearest off-diagonal kernel value; “smaller” does not imply identity.
- IF a null test uses Monte Carlo or a wide tolerance, THEN report approximate/directional agreement, not exact reproduction.
- IF a conditional distribution equals the lossless distribution, THEN claim conditional identity; do not infer that either distribution is computationally hard.
- IF a table reports `1/p`, THEN label it expected trials/samples per success; label `p` as a per-shot probability.
- IF a correction claims originality or external-paper transfer, THEN require literature verification; circuit tests establish correctness, not novelty.

## Mistakes avoided / dead ends
- The trainability test covered n<=4, while the claimed n=5-6 sigma=0.1 kernel has nearest off-diagonal K≈0.230.
- The hardness null matched the primary CSVs tightly, but that did not validate the replacement phrase “exactly as hard.”
- The throughput table’s arithmetic was right while the surrounding probability/expected-count wording was dimensionally wrong.

## Verification
- `venv/Scripts/python.exe -m pytest tests\\v3_correction -q` -> 129 passed.
- Direct hardness-null comparison: primary max absolute error 7.216e-15; dual-rail mixed max 3.843e-6.
- `mmd_exact.py` gives `K=exp(-d²/(2 sigma²))`; d=0.171428... and sigma=.1 gives K=.230066...

## Next time (for a weaker model)
- Do: inventory claims, derive the no-signal output, then inspect the test’s coverage and tolerance.
- Don’t: accept “independently verified” when the test omits the headline boundary cases.

## Changed files
- `REVIEW_CODEX_OUTPUT.md` — recorded the adversarial claim-by-claim review.
