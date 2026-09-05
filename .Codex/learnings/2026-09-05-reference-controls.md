# Distinguish an exact reference from a mechanism-removing control
Date: 2026-09-05 · Scope: project · Recurs when: a classical IQP calculation reproduces a photonic measurement.

## Context & constraints
- The v3.1 regression retains exactly the original parameterized q(theta), kernel, and target.
- The single mixed pair factorizes from the remaining qubits.
- Correct arithmetic and passing tests do not establish the intended scientific interpretation.

## Approach
1. Identify which mathematical object the alleged null changes.
2. Trace its q(theta), derivatives, conditioning, and ensemble back to the original calculation.
3. Probe the smallest circuit and an adversarial synthetic curve independently.
4. Check existing dated corrections before describing a discrepancy as newly discovered.

## Decision rules
- If the reference retains the same q(theta), label it an exact reference, not a model-free control.
- If only one fixed-size component entangles, factor the output before invoking generic IQP hardness.
- If initialization is deterministic, distinguish spread across coordinates from variance across draws.
- If a fit has an offset or negative amplitude, inspect its derivative and limit before assigning a plateau label.
- If two encodings use different angle conventions, match physical states and apply the gradient chain rule before comparison.

## Mistakes avoided / dead ends
- The zero-angle encoding discrepancy was already documented in the hardness study; the remaining API mathematics and comparison contract were inconsistent.
- A green suite did not cover rising-curve classification or overlapping resumed chunks.

## Verification
- See docs/audits/2026-09-05-codebase-audit.md and its two runnable probes.
- 451 existing tests pass; an increasing sequence is nevertheless labeled plateau.
- Mixed reference factorization agrees through n=8 within 1.11e-16.
- Audit diagnoses are recorded; implementation fixes have not been made.

## Next time
- Do: compare contracts, smallest cases, and active claims before larger sweeps.
- Do not: treat classical evaluability as proof that loss-induced concentration is absent.
