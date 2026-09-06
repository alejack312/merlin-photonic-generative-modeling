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
