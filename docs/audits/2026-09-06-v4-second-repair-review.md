# v4 second repair review — d16d9cc

Reviewed 2026-09-06. Implementation HEAD: `d16d9cc83fa8484dde013b16e6ca6fc9c8893e11`.

## Verdict

Five reproducible implementation findings remain: one P1 and four P2 findings. This review does not close scientific acceptance. It does not establish that the existing training results are numerically wrong: the defects concern source verification, dataset identity, checkpoint continuation, and artifact reuse.

Scope: updated reviewer handoff and requirement ledger; latest repair diff from `b7ed7e8`; affected v4 source, scripts and tests; checkpoint/dataset contracts; numerical objective spot checks; saved ring model hashes; explicit sibling retraining. The implementation base remains `de80e9313beed614528fd6332b2f78aab83c0b50`. Legacy code was exercised by the full suite, not re-reviewed line by line in this follow-up.

## Findings

### S01 — P1: scoped Git verification can certify modified source as clean

Locations: `src/merlin_iqp/experiments/sibling_import.py:73`, `:84`, `:116`, `:128`; consumed by `scripts/v4_tcdp/retrain_sibling.py` source admission.

`_git()` strips leading whitespace from the complete porcelain output. A normal first record ` M src/iqp_bp/model.py` becomes `M src/iqp_bp/model.py`. `_status_is_in_scope()` still slices from offset 3, so it tests `rc/iqp_bp/model.py` and discards the modification. `git_source_identity()` then returns `dirty=False` and the committed Git tree instead of the modified content identity. The commit/tree/dirty gate therefore admits this modified source under the pinned identity.

Reproduction: create and commit one source file in a temporary Git repository, modify it without staging, and call the public identity function with `include_paths=("src/iqp_bp",)`. Actual Git reports the edit; the function reports clean and the same tree as before the edit. This is a normal unstaged edit, not malformed input.

Repair: preserve porcelain whitespace, preferably parse `--porcelain=v1 -z` independently of the scalar Git helper. Cover first-record unstaged changes, staged changes, renames, quoted paths, and Git-command failure. Require observed modifications to affect admission and identity. Today's real sibling remains clean; this finding invalidates the guard's completeness, not today's trajectory equality.

### S02 — P2: different raw datasets receive the same DatasetBundle hash

Location: `src/merlin_iqp/classical/contracts.py:110–112`.

The constructor computes full `split_hashes` for validation but then uses `repr(x)` to identify raw NumPy splits. NumPy truncates large array representations. Two valid `(256, 6)` binary arrays differing at `[100, 2]` have identical representations and identical bundle hashes. Display settings can also affect this identity without changing the data.

Repair: derive bundle identity from the already computed, named split hashes and declared metadata. Test a mutation in a region omitted by NumPy's display and stability under print-option changes. Typed `BinarySamples` and the dedicated ring dataset hash use content hashes; this reproduction targets the supported raw-array DatasetBundle boundary.

### S03 — P2: checkpoint resume silently resets missing Adam state

Locations: `src/merlin_iqp/classical/trainer.py:118–127`; `src/merlin_iqp/classical/contracts.py:132–137`.

A step-3 Adam checkpoint retaining its valid learning rate but missing `m`, `v` and `adam_t` is accepted. Resume substitutes zero moments and step zero while preserving the training step/history. After one update, its theta differs from valid continuation by `0.00032466319429763635` in the two-qubit fixture. There is no warning or adaptation label. A checkpoint containing NaN loss history is also admitted, and `run(0)` returns NaN as its final loss.

Repair: validate the complete optimizer-specific state before mutating the trainer: required fields, vector shapes, finite moments, non-negative second moments, integral compatible counters, and finite/complete loss history. Reject incomplete continuation; a deliberately reset optimizer must be a separately named operation. Extend the learning-rate repair tests to missing and malformed state.

### S04 — P2: adding another seed makes an unchanged ring run non-reusable

Locations: `src/merlin_iqp/experiments/rings.py:329–365`, `:430–440`.

The writer recomputes replication metadata from sibling directories and compares that entire new manifest with the existing immutable manifest. Write seed 0, write seed 1, then write the exact same seed-0 RingRun again: `FileExistsError` is raised. Replica count and duplicate classification changed because another artifact exists; the run itself did not change. Consequently a completed multi-seed sweep cannot be safely rerun using the intended idempotent writer behavior.

Repair: separate immutable run identity from group observations. Validate the existing run against its immutable identity and store aggregate replication information separately, or explicitly preserve the existing snapshot. Add a repeat-after-second-seed test for deterministic and seeded profiles.

### S05 — P2: ring writer reports success for missing or corrupted existing arrays

Location: `src/merlin_iqp/experiments/rings.py:432–443`.

The existing-destination branch checks only manifest equality. Write a run, remove `run.npz`, and call the writer again with the same RingRun: it returns the missing path as a successful artifact result without repairing or rejecting it. The same branch never verifies the bytes of existing arrays, so a matching manifest alone can also preserve corrupted data. The comparison reader now rejects many such corruptions, but the producer still reports successful completion.

Repair: require all promised artifacts and validate their content before an idempotent return. Reject incomplete/corrupt destinations clearly, or implement an explicit safe reconstruction path. Keep the no-overwrite guarantee for valid dependent comparisons.

## Prior nine-repair disposition

| Previous finding | Current review |
|---|---|
| R01 empty/NaN trajectory false passes | Corrected for the sibling comparator; explicit step/shape/finiteness checks and finite mismatch FAIL are present. S03 is a separate checkpoint boundary. |
| R02 ignored config | Exact source config path/hash is now required; unsupported configs are rejected, and generator-count adaptation is disclosed. |
| R03 source verification | Import scoping, pin admission and outside-sibling output checks added, but S01 defeats dirty-source admission for a common edit. |
| R04 ring overwrite namespaces | Config namespaces and staged initial writes added. S04/S05 remain in existing-output handling. |
| R05 stale comparison hashes | Loaded model and dataset content hashes are checked before comparison. |
| R06 spatial geometry shorthand | Explicit centers are now required; unsupported kernel strings are rejected. |
| R07 matched NAT arms | CLI now creates two arms from the same frozen warm state; efficacy remains a separate open criterion. |
| R08 full-Fock aggregation | Executed full-Fock FAIL/INCONCLUSIVE now contributes to the aggregate status. |
| R09 default sibling dependency | Source integration is opt-in; portable tests cover local contracts. Explicit integration passed. |

## Verification

- Full suite with a writable Perceval path: **652 passed, 1 skipped in 512.89 seconds**. The skip is the optional sibling integration in the default suite.
- Explicit `MERLIN_SIBLING_ROOT` integration: **8 passed in 7.21 seconds**, including source retraining against the recorded trajectory.
- All **22** ring model manifests matched their saved generator and final-theta arrays.
- Independent finite-difference checks of Hamming and spatial objective gradients at n=2,3,4: maximum absolute error **2.34e-10** (rounded upward).
- Five executable counterexamples: [second-repair probes](2026-09-06-v4-second-repair-probes.py). They assert current defects; after fixes they should stop reproducing and become rejection/integrity regression tests.

No production code, canonical results, sibling source, branch history or milestone statuses were changed by this review. The new audit files and learning-note addendum are intentionally uncommitted.

## Acceptance consequences

The ledger's broad PASS statements about strict checkpoint contracts, portable resume, source identity, and artifact integrity need to be narrowed or reopened against these counterexamples (especially MOD-01/MOD-04 and SWEEP-02). A passing default suite does not settle these behavioral contracts.

The already disclosed physical full-Fock/projection, photonic-ring, NAT metric, broader sibling, and owner-control gaps remain open. They are not counted as new findings here. This review supplies independent evidence; it cannot supply owner interpretation or substitute for the separately requested external review.
