# Plan additive experiments without changing the comparison
Date: 2026-09-05 · Scope: project · Recurs when: importing a sibling training pipeline into a new physical realization

## Context & constraints
- The ring generator's 462-outcome MerLin ansatz differs from the later IQP family.
- The sibling contains both iqp_bp and iqp_mmd with different dependencies, data contracts and gate support.
- Existing pipelines and historical results must remain available.

## Approach
1. Separate dataset, circuit, objective, estimator and physical backend identity.
2. Inventory actual source configurations and checkpoints before declaring experiment compatibility.
3. Share narrow target/model/kernel/checkpoint contracts across the two new callers.
4. Compare frozen checkpoints before comparing retraining trajectories or noisy outputs.

## Decision rules
- If a finite spatial kernel is not diagonal in Walsh coordinates, it still has a full Walsh representation; do not confuse representation with efficient diagonal-mixture sampling.
- If size, graph, generator weight, kernel mixture or data split changes, label the run an adaptation rather than faithful reproduction.
- If a physical backend lacks support, retain the source row and missing capability; do not substitute a qubit reference labeled photonic.
- If noise/NAT choices remain open, let independent classical reproduction proceed under explicit configurations.

## Verification
- Direct spatial MMD equals full Walsh form at N=8: .1638180415093075; spatial transform is non-diagonal, Hamming transform diagonal to 1.73e-17.
- Plan checks: 52 unique requirement IDs, local links resolve, all three requested workstreams covered, old Phase 25 preserved.
- Planning only; no new training or physical deployment performed.

## Next time
- Do: replay a source checkpoint, then one update, then a full trajectory before assigning substrate differences.
- Don't: silently equate the same dataset with the same circuit or metric.
