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

## 2026-09-08 addendum: sibling-to-substrate closure

### Context & constraints
- The selected closure compares the same regenerated source samples, generator, final parameters, Hamming bandwidth, MSB-first codec, and evaluation budget across sibling IQP, local IQP, compiled CP-map, and fixed-photon deployed-map arms.
- The deployed n=9 arm is analytic absolute-probability CP-map evidence; direct Perceval full-Fock validation remains limited to the declared n=2/n=3 boundary.

### Decision rules that generalize
- IF source retraining evidence is PASS, THEN independently regenerate the dataset and compare source/local vectors before compiling; checkpoint replay alone is not enough.
- IF multiple source profiles share `(n, sigma)`, THEN include the source config/profile in the artifact identity or outputs can overwrite each other.
- IF uniform fixed-photon loss is applied, THEN store conditional vectors and absolute success separately and verify `success_loss = eta**n * success_ideal` at the exact tolerance.
- IF a numerical implementation changes after an older manifest was produced, THEN retain the producer commit in that manifest and explicitly revalidate or qualify it; do not claim the old artifact is current-head evidence.

### Verification
- Canonical closure: `results/v4_tcdp/sibling_comparisons/closure_20260908_complete_v4/summary.json` contains 8 PASS cells; all JSON/NPY hashes recompute.
- Full suite: `687 passed, 1 skipped`; explicit sibling integration/comparison: `28 passed, 1 skipped`; artifact validator: `355` JSON, `72` JSONL, `9` payload hashes, `0` failures.

### Next time
- Do: make the comparison chain and physical capability boundary explicit in the artifact schema before running all registered cells.
- Don't: call an analytic deployed map hardware evidence, or let a successful source rerun stand in for a matched substrate comparison.
