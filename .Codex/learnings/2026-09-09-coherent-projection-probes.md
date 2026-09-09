# Preserve interference when auditing projection diagnostics

Date: 2026-09-09 · Scope: project · Recurs when: optical paths compare final and intermediate postselection.

## Context and constraints
- The shared-gate diagnostic reported TVD 0.5854 and was used as a ring deployment prerequisite.
- Source and implementation stayed unchanged; a process-local probe changed only final-readout accumulation.

## Approach
1. Trace whether each intermediate value is an amplitude or probability.
2. Sum coherent contributions to the same final Fock state before squaring.
3. Compare both conditional TVD and absolute accepted mass with the existing final-only calculation.
4. Trace the numerical result into tests, artifact gates, ledger claims, and owner-facing explanations.

## Decision rules that generalize
- If paths are not distinguished by measurement or environment, retain their interference terms.
- If a gate requires a large discrepancy, independently establish why that discrepancy is physical before encoding it as acceptance.
- If probability mass is normalized, measure the original total first; complementary probabilities are not an independent reconciliation check.

## Mistakes avoided
- Equal acceptance does not establish equal conditional distributions or correct coherent propagation.
- One corrected fixture does not prove a universal projection-equivalence theorem.

## Verification
- Registered n=3 shared-gate fixture: coherent-readout probe reduced TVD from 0.585411845271861 to 1.942890293094024e-16.
- Acceptance stayed approximately 0.0135360315122832 at eta=1.
- See docs/audits/2026-09-09-v4-independent-audit.md for the fixture and required repairs. No production fix was applied during this audit.

## Next time
- Do: use a small coherent superposition and an independently checked readout.
- Do not: preserve a published discrepancy merely because downstream tests require it.
