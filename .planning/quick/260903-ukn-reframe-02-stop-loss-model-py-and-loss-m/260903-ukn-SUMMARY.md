---
quick_id: 260903-ukn
status: complete
---

# Quick Task 260903-ukn: REFRAME-02 + stale anchor fix

## What was done

**REFRAME-02** (`.planning/REQUIREMENTS.md:37`): `photonic_iqp_distribution_lossy` and
`photonic_weight2_iqp_distribution_lossy` no longer discard partial-loss outcomes into an opaque
`residual` scalar — both now additionally return a `partial_loss` dict (`{str(state): probability}`),
the per-pattern decomposition of `residual`, appended as the last element of each return tuple
(D-01: append-only, so any caller not updated fails loudly rather than silently mis-assigning).
Weight-2's `partial_loss` receives the same herald-success renormalization `residual` already gets
(D-03), so `sum(partial_loss.values()) == residual` to floating-point precision in both functions —
proving no existing number changed.

**Task 3**: fixed `docs/technical-findings.md` line 7's stale anchor into `docs/trainability-study.md`
— recomputed from the heading's live text (it had gained ", revised after an independent adversarial
review" since the anchor was last computed) rather than trusted from any pre-computed value.

## Commits (on `claude/serene-sanderson-728202`, merged from the executor's worktree)

- `d6c62b1` — feat: return `partial_loss` from both loss-model functions, update all callers
- `9bf5c11` — test: partial_loss mass-reconciliation regression tests
- `c47eda9` — fix(docs): repair stale trainability-study.md anchor
- merge commit — worktree branch merged back after independent verification

## Callers updated (all found and fixed; repo-wide grep re-run confirmed exhaustive)

- `src/merlin_iqp/hardness/sweep.py` (both call sites) — discards `_partial_loss`, matching its
  existing `_global_perf` discard convention; `_distribution_for_backend`'s own 3-element return
  contract is unchanged, so no CSV/`results/` impact.
- `julia/generate_reference.py` (both call sites) — **not in the original task brief**, found during
  planning via repo-wide grep. Updated to discard `_partial_loss`; script itself was not re-run.
- `tests/hardness/test_loss_model.py` and `tests/hardness/test_loss_model_weight2.py` — all existing
  unpacks extended to the new arity.
- `tests/scripts/v3_hardness/test_merlin_loss_model.py`'s `polarization` monkeypatch stub — **also
  not in the original brief**, found during planning. Its hardcoded return tuple updated from
  `{"00": 1.0}, 0.0, 1.0` to `{"00": 1.0}, 0.0, 1.0, {}` to track the real function's new arity.

## Null-result outcome (Task 2, per CLAUDE.md's null-result gate)

Predicted first, in a throwaway scratchpad script (deleted before commit, not a deliverable): that
`global_perf` stays pinned at ~1.0 regardless of `eta`, because `min_detected_photons_filter(0)`
never actually filters anything (≥0 detected photons is every outcome) and loss is injected via
in-circuit `LC` components, not Perceval's own performance-tracking machinery. Ran this prediction
across both functions (weight-1 n=2; weight-2 n=2, i=0, j=1) over `eta ∈ {1.0, 0.7, 0.3, 0.0}`:
**held on the first attempt** — `global_perf` measured within 1e-15 of exactly 1.0 in every cell,
independent of `eta` and of how much mass `partial_loss` held. No revision needed. Encoded directly
as Test C — a genuine null result extending the existing Pitfall-4 finding (`global_perf` already
known to be uninformative about `herald_failure_prob`) to also being uninformative about
`partial_loss`'s mass.

## Test counts

- Baseline (before any edit): **425 passed**
- After Task 1 (arity fixes only, no new tests): **425 passed** — no regression
- After Task 2 (new tests added): **451 passed** (26 new parametrized mass-reconciliation cases)
- Independently re-verified by the orchestrating session after merge: **451 passed**, confirmed via
  a fresh `pytest -q` run in the executor's worktree before merging.

## Verified independently before merge (not just trusted from the executor's own report)

- Read the full diff of all three commits directly (`git show`/`git diff`) — confirmed D-01/D-02/D-03
  were implemented exactly as locked in the plan.
- Re-ran the repo-wide grep for both function names myself — confirmed every call site has the
  correct new arity, and the monkeypatch stub was fixed.
- Re-ran the full test suite myself in the executor's worktree before merging — 451/451 passed.
- Confirmed `docs/technical-findings.md`'s new anchor fragment
  (`correction-2026-09-03-revised-after-an-independent-adversarial-review--the-exponential-decay-verdict-is-a-pipeline-artifact-not-a-trainability-finding`)
  matches the live heading in `docs/trainability-study.md:31` character-for-character.
- Confirmed `git diff --stat -- results/` between the pre-dispatch commit and the final commit is
  empty — nothing under `results/` was touched.

## Out-of-scope discovery (not fixed, flagged by the executor)

Task 3's own verify script checks *all* cross-doc anchors in `docs/technical-findings.md` and
surfaces a pre-existing, unrelated anchor break: three links into a line-wrap-split heading in
`docs/hardness-under-loss-study.md`, predating this quick task entirely (confirmed via `git show`
against the pre-dispatch commit). Left untouched per scope discipline — worth a separate fix later.

## Process note: this session's `git worktree remove --force` lost the executor's own uncommitted
SUMMARY.md

The executor left `260903-ukn-SUMMARY.md` uncommitted in its worktree per the quick-workflow
convention (the orchestrator commits docs artifacts separately). When cleaning up the worktree after
merging its branch, this session ran `git worktree unlock` + `git worktree remove --force` +
`git branch -D` directly, skipping the official workflow's "rescue uncommitted SUMMARY.md before
worktree removal" step (`find "$WT/.planning" -name "*SUMMARY.md"` + copy) — deleting the
uncommitted file along with the worktree. No data was actually lost: the executor's own completion
report (captured in this session's transcript) contained the same content reconstructed above, and
every substantive claim in it was independently re-verified against the merged commits before being
restated here. Process lesson for next time: always run the rescue-copy step before
`git worktree remove`, even when planning to reconstruct from the agent's report as a fallback.
