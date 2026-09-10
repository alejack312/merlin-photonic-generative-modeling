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

## Repair addendum (2026-09-09)
- The production readout now sums complex amplitudes per logical output before squaring; full-Fock outputs reject incomplete mass instead of silently renormalizing it.
- The sibling comparator now enforces local-versus-unquantized compilation equality, and the public spatial MMD path shares positive finite mixture validation with typed kernels.
- Verification: focused repair tests `113 passed, 1 skipped`; full suite `693 passed, 1 skipped`; explicit sibling integration `30 passed`; artifact validation `398` JSON, `72` JSONL, `12` payload hashes, zero failures.

## Post-repair audit addendum (2026-09-09)
- Total backend mass conservation and conditional-shape equality do not independently validate accepted probability. Mutate acceptance while preserving shape and eta bookkeeping; the qualification gate must detect the change.
- At `6d3af6f`, ring qualification accepted zero success with the saved conditional vector, and physical-control qualification accepted halved success in both projections. The saved nominal controls independently matched ideal acceptance within 4.17e-17.
- See `docs/audits/2026-09-09-v4-post-repair-audit.md`. This is an unresolved gate defect, not a new nominal projection disagreement; no implementation fix was made in the audit.

## Focused repair closure (2026-09-09)
- For registered physical instruments, compare measured acceptance to an independent composed-map success, and separately check positivity, eta/raw scaling, and accepted-plus-rejected mass.
- For resumable state, reject positive-step checkpoints without a complete history before assigning any trainer fields; verify resume → run → save → resume.
- For aggregate measurements, require the exact registered size set and all individual measurement/RSS statuses to be `PASS` before aggregate `PASS`.
- Verification: acceptance mutation tests, checkpoint round-trip tests, and resource completeness tests pass; full suite and regenerated artifacts are recorded in the reviewer handoff.
