# Sibling row disposition audit
Date: 2026-09-07 · Scope: project · Recurs when: registered source rows mix checkpoints, summaries, and backend-scale limits

## Context & constraints
- The sibling checkout is read-only and must match the pinned commit/tree identity.
- Registered rows can support faithful retraining, frozen-checkpoint replay, partial output, or a blocked disposition.
- Exact distributions must not be reconstructed from moments, QASM, plots, or summary metrics.

## Approach
1. Read the inventory manifest and enumerate every exact-reproduction row.
2. Verify sibling HEAD, branch, cleanliness, config hashes, checkpoint families, and safe artifact types.
3. Run only bounded feasible profiles; preserve raw partial output when stopped and write a manifest beside it.
4. For missing checkpoints, write a blocked manifest with the exact expected path, available evidence, and attempted command.
5. Keep large-scale density limits and absent target data as explicit boundaries; do not relabel adapted replay as retraining.

## Decision rules that generalize
- IF a registered safe NPZ exists and the adapter completes, THEN call it adapted checkpoint replay, not faithful retraining.
- IF raw output exists but compiled/deployed output or the adapter manifest is absent, THEN call the row stopped-partial.
- IF no safe NPZ exists, THEN name the exact expected checkpoint path/glob and preserve the row as blocked.
- IF `n` exceeds the bounded compiled-density limit, THEN do not allocate a full density matrix or extrapolate a physical result.

## Verification
- Pinned sibling HEAD: `f6d6ebe87e4ee1de10893c6ea2f0ffa367493336`; branch `alejack312`; clean.
- Four required-profile manifests validated by JSON checks; sibling replay tests passed 4/4.
- Ghosh–Kim small-n replay produced raw/compiled/deployed artifacts; bandwidth replay retained a hashed raw partial artifact.

## Next time (for a weaker model)
- Do: classify every exact row before running anything and namespace each output by source/config/checkpoint identity.
- Don’t: call checkpoint replay retraining, infer a distribution from a marginal/plot, or silently run the large-n density path.

## Changed files
- `scripts/v4_tcdp/replay_sibling.py` — exact missing-input path in blocked manifests.
- `results/v4_tcdp/sibling_reproduction_evidence.md` — row-level disposition snapshot.
