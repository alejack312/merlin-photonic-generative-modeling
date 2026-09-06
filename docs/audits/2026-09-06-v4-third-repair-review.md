# v4 third repair review — 8f1298f

Date: 2026-09-06. Audited HEAD: `8f1298f1c53b951ac11ba405dec7f1ce4d9f282c`; implementation repair commit: `84a71bc`; implementation base: `de80e9313beed614528fd6332b2f78aab83c0b50`.

## Verdict and scope

Six confirmed P2 findings remain. Three expose adjacent gaps in the latest source/checkpoint/artifact repairs; three concern NAT parameter binding, checkpoint replay validation, and NAT reporting. No P0/P1 finding was established in this follow-up. The findings do not establish that the existing ring fits or recorded sibling trajectory are wrong.

Reviewed the updated handoff/ledger, the full latest repair diff from `d16d9cc`, and surrounding v4 trainer/checkpoint, dataset/kernel, NAT, comparison, source import/replay, compiler/map/erasure, and artifact code. Ran the full suite, explicit sibling integration, independent temporary-fixture probes, and bounded numerical/artifact checks. Legacy behavior was exercised by the full suite; this was not a fresh line-by-line review of every historical implementation.

## T01 — P2: NAT sorts pairs without sorting their sequence parameters

Locations: `src/merlin_iqp/experiments/nat.py:45–55`, `:83–85`, `:219–230`, `:287–303`.

`NatConfig` sorts the pair list. `_values_for_pairs` subsequently takes positional keys/thetas/windings unchanged, whereas a mapping is resolved against the sorted pairs. Consequently equivalent caller inputs describe different models. With pairs `[(1,2),(0,1)]`, keys `[1,20]` bind key 1 to `(0,1)` instead of `(1,2)`. A mapping `{(1,2):1,(0,1):20}` produces the intended binding.

At n=3, singles `[0.2,0.3,0.5]`, and zero optimization steps, the two accepted calls produced conditional output TVD **0.21112926434753415**. This is a valid-input circuit change before any optimizer or noise effect. The current CLI supplies sorted chain pairs, so its existing primary runs are not implicated by this counterexample.

Repair: bind positional values to caller pairs before normalization, then reorder the bound records together; alternatively reject unsorted positional input with a clear contract. Cover keys, raw pair angles, and windings. Equivalent mapping and sequence forms must yield the same initial compiled state and trajectory.

## T02 — P2: rejected resume mutates the trainer; invalid Adam state still passes

Locations: `src/merlin_iqp/classical/trainer.py:124–151`; related checkpoint validation in `src/merlin_iqp/classical/contracts.py:132–140`.

The repair rejects missing moments, but only after assigning checkpoint theta, step and history to the live trainer. Attempting to resume a step-3 checkpoint with missing Adam fields into a valid step-1 trainer raises ValueError while changing its theta and step to the rejected checkpoint's values. Its remaining optimizer state belongs to a different trajectory. Catching the error and continuing therefore uses a partially loaded state.

The validator also admits finite negative second moments (`v=[-1,-1]`). These are invalid Adam state and later cause an invalid square root. Counter conversion uses `int(...)` before validating integrality, and history completeness is not enforced. The executed probes establish the mutation-after-rejection and negative-second-moment cases; the latter two observations are additional validation requirements, not separately counted findings.

Repair: parse and validate all state into local variables, including RNG state, before any assignment to the trainer. Require non-negative finite second moments, integral compatible counters, and a history consistent with the checkpoint's step contract. A failed resume must leave a complete before/after trainer snapshot unchanged; a valid resume must retain trajectory equality.

## T03 — P2: quoted Git paths and status failures are still certified as clean

Locations: `src/merlin_iqp/experiments/sibling_import.py:76–101`, `:127–141`.

Preserving the leading status columns fixes the prior ASCII-file counterexample. However, `git status --short` quotes/escapes some paths, and the scope matcher does not decode them. Editing the valid Python module `src/iqp_bp/model_é.py` gives ` M "src/iqp_bp/model_\\303\\251.py"`. The matcher misses the scope, returning `dirty=False` and the same committed tree identity. The companion `ls-files` string parsing also needs unambiguous filename handling.

Separately, `_git_status` returns an empty list on a Git error. Injecting a failing status command while commit/tree reads succeed likewise yields a clean committed identity. An unavailable status observation is not evidence of cleanliness.

Repair: parse NUL-delimited porcelain and file lists, preserving filenames and rename records; propagate status/listing failures as an unverified identity or exception. Test quoted/non-ASCII paths, renames, and command failures through public `git_source_identity` and its admission consumer. The actual sibling checkout remained clean; this is a guard failure, not a claim that it was altered.

## T04 — P2: ring summary metrics and physical status are not integrity-checked

Location: `src/merlin_iqp/experiments/rings.py:470–472`.

The existing-artifact branch now checks every saved array, but checks only `run_id` in `summary.json`. Changing summary metrics to `{"tvd_train": -999}` and photonic evaluation to `{"status":"PASS"}`, while retaining its run ID, is accepted by `write_run_artifacts`. The corrupted summary is preserved and returned as a successful artifact. Removing substantive summary fields is likewise not prevented by the run-ID-only check.

Repair: compare all immutable summary fields against the verified manifest/run. Validate replication metadata against the preserved snapshot or a separately validated aggregation contract. Test missing fields, altered metrics, initialization, and physical capability status. The 22 current saved ring summaries matched their manifest fields in the bounded check; the defect is the reuse guard.

## T05 — P2: sibling replay coerces nonbinary generators and exports NaN evidence

Locations: `scripts/v4_tcdp/replay_sibling.py:70–77`, `:89`, `:138`.

The safe NPZ reader casts `G` to uint8 before `IQPModel` validates it. A source row `[1.5,1]` becomes `[1,1]` and is replayed as an ordinary binary IQP generator. Thus malformed source data can be silently changed rather than rejected. The same boundary accepts a NaN source loss, and the result writer emits the nonstandard JSON token `NaN` while reporting `adapted_reproduction`.

An independent temporary source checkout and safe NPZ reproduced both behaviors; no real sibling files were changed. No claim is made that the pinned historical checkpoint contains those malformed values.

Repair: validate the loaded raw generator, theta, scalar step and source loss before coercion, evaluation, or writes. Require finite numeric evidence and valid integral non-negative steps, and serialize with `allow_nan=False`. Test malformed NPZ fields through the complete adapter. Safe deserialization alone does not establish scientific data validity.

## T06 — P2: NAT exports two incompatible quantities named pair_moves

Locations: `src/merlin_iqp/experiments/nat.py:157–159`, `:181`, `:442–446`, `:529`.

The top-level `pair_moves` counts pair coordinates whose final key differs from their initial key. The budget field with the same name counts accepted search moves. These differ whenever a coordinate moves more than once or returns to its initial key. The top-level calculation also omits winding-only final changes.

This discrepancy is present in canonical evidence: `results/v4_tcdp/nat/n4_seed0_primary-warm-start.json` reports **3** top-level pair moves and **163** accepted moves in budgets. The n=6 primary artifacts report **5** versus **278**. A consumer using the public property or top-level field therefore receives changed-coordinate count under a move-count label.

Repair: expose the accumulated accepted-move count as `pair_moves`; name the endpoint statistic `pairs_changed` (including a declared winding policy). Add a multi-step fixture where one coordinate moves more than once. Existing fitted parameters need not be retrained to correct this reporting field, but any artifact correction should be explicit and provenance-preserving.

## Latest five-repair disposition

| Prior finding | Current review |
|---|---|
| S01 first-record Git trimming | Original ASCII case corrected; quoted paths and failed observations remain open under T03. |
| S02 abbreviated dataset hashes | Corrected: bundle identity uses named full-content split hashes. |
| S03 incomplete Adam resume | Missing fields and non-finite history now rejected, but rejection is not atomic and state-domain validation remains incomplete under T02. |
| S04 multi-seed idempotence | Original counterexample corrected by separating replication observations from immutable identity. |
| S05 existing artifact integrity | Required files and arrays are checked; summary integrity remains incomplete under T04. |

The corresponding ledger PASS claims should be narrowed or reopened for the reproduced boundaries. New T01/T05/T06 findings need their own dispositions; they should not be conflated with the already acknowledged absence of physical or efficacy evidence.

## Verification and limits

- Full suite with writable Perceval path: **658 passed, 1 skipped in 496.11 seconds**. The skip is the optional sibling integration in the default run.
- Explicit sibling retraining integration: **8 passed in 7.98 seconds**.
- Twelve random n=2/3/4 quantized compiler checks, including signed/winding angles, matched the effective-angle IQP reference with maximum TVD **1.0894063429134349e-15**.
- All **22** canonical ring summaries agreed with the checked manifest fields (`run_id`, metrics and photonic-evaluation fields where present).
- [Executable probes](2026-09-06-v4-third-repair-probes.py) reproduce all six findings. These are historical counterexamples, not tests that should continue passing after repair.

No implementation code, canonical outputs, sibling source, milestone statuses, commits, merges or publications were changed by this audit. Only the review/probe files and a focused learning note were added. Temporary fixtures stayed under `.pytest_cache`.

Physical/full-Fock composition, final-only projection, photonic ring deployment, broader sibling reproduction, NAT efficacy and owner-authored controls remain separately open. This review does not establish scientific milestone closure or supply owner interpretation.
