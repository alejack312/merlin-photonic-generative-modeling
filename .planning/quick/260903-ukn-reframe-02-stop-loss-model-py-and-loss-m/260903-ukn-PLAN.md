---
phase: quick-260903-ukn
plan: 01
type: execute
wave: 1
depends_on: []
files_modified:
  - src/merlin_iqp/hardness/loss_model.py
  - src/merlin_iqp/hardness/loss_model_weight2.py
  - src/merlin_iqp/hardness/sweep.py
  - julia/generate_reference.py
  - tests/hardness/test_loss_model.py
  - tests/hardness/test_loss_model_weight2.py
  - tests/scripts/v3_hardness/test_merlin_loss_model.py
  - docs/technical-findings.md
autonomous: true
requirements: [REFRAME-02]

must_haves:
  truths:
    - "photonic_iqp_distribution_lossy returns the partial-loss outcomes as their own keyed dict, not only as a collapsed residual scalar"
    - "photonic_weight2_iqp_distribution_lossy does the same, with the same renormalization treatment residual already receives"
    - "sum(partial_loss.values()) reconstructs the existing residual scalar to floating-point precision, so no existing number changes"
    - "Every existing caller of both functions is updated; the full test suite is green and no test count is lost"
    - "docs/technical-findings.md line 7's trainability-study.md anchor resolves to a real heading"
  artifacts:
    - path: "src/merlin_iqp/hardness/loss_model.py"
      provides: "weight-1 partial_loss dict appended to the return tuple"
      contains: "partial_loss"
    - path: "src/merlin_iqp/hardness/loss_model_weight2.py"
      provides: "weight-2 partial_loss dict appended to the return tuple, renormalized by herald_success_prob"
      contains: "partial_loss"
    - path: "tests/hardness/test_loss_model.py"
      provides: "weight-1 partial-loss mass-reconciliation regression test"
      contains: "partial_loss"
    - path: "tests/hardness/test_loss_model_weight2.py"
      provides: "weight-2 partial-loss mass-reconciliation regression test"
      contains: "partial_loss"
  key_links:
    - from: "src/merlin_iqp/hardness/sweep.py"
      to: "photonic_iqp_distribution_lossy / photonic_weight2_iqp_distribution_lossy"
      via: "positional unpack in _distribution_for_backend"
      pattern: "_partial_loss"
    - from: "tests/scripts/v3_hardness/test_merlin_loss_model.py"
      to: "sweep.photonic_iqp_distribution_lossy"
      via: "monkeypatch stub whose return arity must match the real function"
      pattern: "def polarization"
    - from: "docs/technical-findings.md"
      to: "docs/trainability-study.md line 31 heading"
      via: "markdown anchor link"
      pattern: "trainability-study.md#correction-2026-09-03-revised"
---

<objective>
REFRAME-02 (Should, `.planning/REQUIREMENTS.md:37`): stop `photonic_iqp_distribution_lossy` and
`photonic_weight2_iqp_distribution_lossy` from discarding partial-loss outcomes. Today every
out-of-subspace outcome's probability is summed into one scalar `residual` and the per-pattern
detail is thrown away. Both functions gain a `partial_loss` dict keyed by the raw Fock state, and
every caller is updated.

Second, unrelated bug fix bundled in: `docs/technical-findings.md` line 7 links into
`docs/trainability-study.md` using a slug computed from that heading's OLD text, before it gained
", revised after an independent adversarial review". The link is broken. Fix it.

Purpose: REQUIREMENTS.md's own scope sentence is the whole brief — "No analysis of it in this
milestone — this only stops discarding the data." This is plumbing plus regression tests, nothing
more. The anchor fix is a broken-link repair, not a finding.

Output: two library functions with an extended return tuple, five caller sites updated, two new
regression tests, one corrected markdown anchor.
</objective>

<locked_decisions>
These were decided during planning. The executor implements them; it does not re-litigate them or
improvise a different shape per function.

**D-01 — Append at the very END of both tuples. Never insert in the middle.**

- `photonic_iqp_distribution_lossy` → `(dist, residual, global_perf, partial_loss)`
- `photonic_weight2_iqp_distribution_lossy` → `(dist, residual, herald_failure_prob, global_perf, partial_loss)`

Rationale, in order of weight:
1. Growing the arity means any caller doing fixed-arity positional unpacking that was NOT updated
   fails LOUDLY (`too many values to unpack`) at call time, rather than silently mis-assigning a
   variable. That is the safety property that makes this change auditable by grep + a full test
   run. It is the point of the change's shape, not a stylistic preference.
2. Appending specifically (rather than inserting after `residual`, the other candidate considered)
   additionally preserves the meaning of every existing positional index, so the caller update is
   the same mechanical edit at all five sites — add one trailing name — with no reordering to get
   wrong.
3. Both existing docstrings' `Returns (...)` sentences stay literally true as a prefix, so the
   docstring edit is additive, matching this repo's additive-correction convention.

Considered and rejected: `(dist, residual, partial_loss, global_perf)` — semantically tidier
(`partial_loss` is `residual`'s own decomposition, so they belong adjacent) but it makes each
caller edit a reorder rather than an append, which is a strictly larger class of mistake for zero
functional gain. Consistency across both functions was the constraint; append wins it.

**D-02 — `partial_loss` is `{str(state): probability}`.** Keyed by the stable string
representation of the raw Perceval Fock `state` (`str(state)`, e.g. `"|0,0>"`), NOT by a decoded
bitstring — these are exactly the states `fock_to_bitstring` returns `None` for, so no decoded
bitstring exists. This is the same branch that currently increments `residual`; it is simply also
recorded per-key instead of only summed.

**D-03 — weight-2 `partial_loss` gets the SAME renormalization `residual` already gets**: each
value divided by `herald_success_prob = 1.0 - herald_failure_prob`, inside the existing
`if herald_success_prob > 0:` guard, alongside the existing `dist` and `residual` renormalization.
`herald_failure_prob` itself stays raw, unchanged. Consequence — and this is the backward-
compatibility invariant the new tests assert, not merely a claim:
`sum(partial_loss.values()) == residual` to floating-point precision, in both functions.

**D-04 — No behavior change anywhere downstream.** `sweep.py`'s `_distribution_for_backend` already
discards `global_perf` (its own docstring says "The sweep does not use `global_perf`"); it discards
`partial_loss` the same way, as `_partial_loss`. Its own 3-element return contract is unchanged, so
no CSV column, no file under `results/`, and no sweep-script output shape is affected. Do not
re-run any sweep script. Do not touch any file under `results/`. Do not add any interpretation of
what the partial-loss data means — REQUIREMENTS.md:37 explicitly forecloses that in this milestone.
</locked_decisions>

<execution_context>
@$HOME/.claude/get-shit-done/workflows/execute-plan.md
</execution_context>

<context>
@CLAUDE.md
@.planning/REQUIREMENTS.md
@src/merlin_iqp/hardness/loss_model.py
@src/merlin_iqp/hardness/loss_model_weight2.py
@src/merlin_iqp/hardness/sweep.py

<caller_inventory>
Every positional-unpack call site of either function in the repo, from
`grep -rn "photonic_iqp_distribution_lossy\|photonic_weight2_iqp_distribution_lossy" --include=*.py .`
run during planning. Task 1 must update all of them. Two of these were NOT in the task brief's
grounding notes and were found during planning — they are flagged.

Weight-1 (`photonic_iqp_distribution_lossy`), 3-tuple → 4-tuple:
- `src/merlin_iqp/hardness/sweep.py:76` — `dist, residual, _global_perf = ...`
- `julia/generate_reference.py:178` — `dist, residual, global_perf = ...`  **[NOT in the brief's
  caller list. Real caller. A reference-CSV generator script; it is NOT re-run by this task, but it
  must not be left broken at unpack time.]**
- `tests/hardness/test_loss_model.py:45, 64, 71` — 3-way unpacks
- `tests/hardness/test_loss_model.py:125, 126` — `correct_dist_full, _, _ = ...` / `correct_dist_lossy, _, _ = ...`

Weight-2 (`photonic_weight2_iqp_distribution_lossy`), 4-tuple → 5-tuple:
- `src/merlin_iqp/hardness/sweep.py:87-90`
- `julia/generate_reference.py:197`  **[NOT in the brief's caller list. Same note as above.]**
- `tests/hardness/test_loss_model_weight2.py:63, 81, 131, 252, 255, 336, 360`
- `tests/hardness/test_loss_model_weight2.py:396, 398` — inside `pytest.raises(...)`, NO unpacking.
  These need NO change. Leave them alone.

Arity-coupled stub (not a call site, but breaks identically):
- `tests/scripts/v3_hardness/test_merlin_loss_model.py:114-116` — the local `polarization(n, thetas, eta)`
  monkeypatch stub, installed via `monkeypatch.setattr(sweep, "photonic_iqp_distribution_lossy", polarization)`
  at line 122, currently `return {"00": 1.0}, 0.0, 1.0`. Once `sweep.py:76` unpacks four values this
  stub MUST return four. **[NOT in the brief's caller list. This is the one that fails as a
  confusing unrelated-test failure rather than an obvious unpack error at the changed line, so
  handle it deliberately.]** The `merlin` stub beside it patches
  `dual_rail_photonic_iqp_distribution`, which this task does not touch — leave it unchanged.

Do not treat this inventory as final: Task 1's verify step re-runs the grep repo-wide.
</caller_inventory>

<verified_invariant>
Verified during planning by reading shipped, exercised code — `julia/generate_reference.py:179-183`
and `:200-204` both already assert `sum(dist.values()) + residual == 1.0` (within 1e-9) for
weight-1 and for weight-2's renormalized outputs. `Processor.probs()` returns a normalized
`results` mapping with `global_perf` reported as a SEPARATE survival scalar, not folded into the
probabilities.

What follows from that, and is therefore safe to assert directly: `sum(dist) + sum(partial_loss) ≈ 1.0`.

What does NOT follow and has NOT been checked: the exact relationship between those masses and
`global_perf`. Task 2 derives it empirically before asserting it. See that task's null-result step.
</verified_invariant>
</context>

<tasks>

<task type="auto">
  <name>Task 1: Return partial_loss from both functions and update every caller</name>
  <files>src/merlin_iqp/hardness/loss_model.py, src/merlin_iqp/hardness/loss_model_weight2.py, src/merlin_iqp/hardness/sweep.py, julia/generate_reference.py, tests/hardness/test_loss_model.py, tests/hardness/test_loss_model_weight2.py, tests/scripts/v3_hardness/test_merlin_loss_model.py</files>
  <action>
Implement D-01 through D-04.

In `loss_model.py`'s `photonic_iqp_distribution_lossy`: initialize an empty `partial_loss` dict
beside `residual`. In the existing `if bits is None:` branch, in addition to `residual += p`, record
`partial_loss[str(state)] = partial_loss.get(str(state), 0.0) + p`. Keep `residual` exactly as it
is — it is not derived from `partial_loss`, it is still accumulated independently, so the test in
Task 2 is a genuine cross-check of two independent accumulations rather than a tautology. Append
`partial_loss` as the fourth return value. Extend the docstring's existing
`Returns (dist, residual, global_perf):` block additively: rename the sentence to the new 4-tuple
and add a `partial_loss` bullet stating it is the per-pattern decomposition of `residual`, keyed by
`str(state)`, added for REFRAME-02, and that it is returned but not analyzed in this milestone.
Do not delete or rewrite any existing docstring prose.

In `loss_model_weight2.py`'s `photonic_weight2_iqp_distribution_lossy`: same pattern. The
`partial_loss` accumulation goes in the SAME `if bits is None:` branch that increments `residual`
— i.e. AFTER the herald-mismatch `continue`, so herald failures are never recorded in
`partial_loss`. Inside the existing `if herald_success_prob > 0:` block, add
`partial_loss = {k: v / herald_success_prob for k, v in partial_loss.items()}` alongside the
existing `dist` and `residual` renormalization (D-03). Append `partial_loss` as the fifth return
value. Extend the docstring's `Returns (dist, residual, herald_failure_prob, global_perf)` sentence
the same additive way, explicitly noting that `partial_loss` is herald-success-conditioned and
renormalized exactly like `residual`, and excludes herald failures.

Update the callers. In `sweep.py` both sites, discard the new value using the file's own existing
underscore convention — `_partial_loss` — matching how it already discards `_global_perf`. Do not
change `_distribution_for_backend`'s own return statement, its docstring's contract description, or
anything downstream of it (D-04).

In `julia/generate_reference.py:178` and `:197`, add a trailing `_partial_loss` to each unpack.
Change nothing else in that file — not the existing `total = sum(dist.values()) + residual`
assertions, not the CSV header comments, not the written CSVs. Do not run this script.

In `tests/hardness/test_loss_model.py` and `tests/hardness/test_loss_model_weight2.py`, add a
trailing `_` (or a named variable if the test will use it) to each unpack listed in the caller
inventory. Leave lines 396/398 of the weight-2 file untouched. Do not add new tests here — that is
Task 2.

In `tests/scripts/v3_hardness/test_merlin_loss_model.py`, change the local `polarization` stub's
return from `{"00": 1.0}, 0.0, 1.0` to `{"00": 1.0}, 0.0, 1.0, {}` so its arity tracks the real
function. Leave the `merlin` stub alone.
  </action>
  <verify>
    <automated>cd "C:/Users/cuqui/merlin-quantum-case-study/.claude/worktrees/serene-sanderson-728202" && grep -rn "photonic_iqp_distribution_lossy\|photonic_weight2_iqp_distribution_lossy" --include=*.py . | grep -v "^\./src/merlin_iqp/hardness/loss_model" | grep -v "#" </automated>
    <automated>cd "C:/Users/cuqui/merlin-quantum-case-study/.claude/worktrees/serene-sanderson-728202" && PYTHONPATH=src C:/Users/cuqui/merlin-quantum-case-study/venv/Scripts/python.exe -m pytest -q</automated>
  </verify>
  <done>
The repo-wide grep's output is inspected line by line and every unpacking site it prints is
accounted for — either updated to the new arity, or explicitly one of the two `pytest.raises`
non-unpacking lines. If the grep surfaces a call site not in the caller inventory above, update it
too and note it in the summary.

The full suite is green with a test count no lower than the pre-change baseline. Record the
baseline count by running the suite BEFORE making any edit, and compare — do not rely on the
"425 tests" figure in the task brief or the stale "296" figure in CLAUDE.md.
  </done>
</task>

<task type="auto" tdd="true">
  <name>Task 2: Mass-reconciliation regression tests for partial_loss</name>
  <files>tests/hardness/test_loss_model.py, tests/hardness/test_loss_model_weight2.py</files>
  <behavior>
REQUIREMENTS.md:37 asks for "a test that its total mass plus the in-subspace mass equals
`global_perf`-consistent totals". Written as concrete expectations, in each of the two test files,
matching that file's existing style (module-level test functions, `_all_keys_close` helper,
`np.random.default_rng(seed)` theta draws, `abs(...) <= tol` assertions — no new fixtures, no new
test files):

- Test A (the backward-compatibility invariant, D-03): across an eta grid including at least one
  strictly-partial value, `abs(sum(partial_loss.values()) - residual) <= 1e-9`. This is the
  assertion that proves nothing about the existing numbers changed — `residual` and `partial_loss`
  are accumulated independently in the implementation, so agreement is a real cross-check.
- Test B (total mass): `abs(sum(dist.values()) + sum(partial_loss.values()) - 1.0) <= 1e-9`.
  Grounded in the already-shipped, already-exercised `julia/generate_reference.py` assertion that
  `sum(dist) + residual == 1.0`. For weight-2 this is the herald-success-conditioned total; state
  that in the test's own docstring.
- Test C (`global_perf` consistency): the reconciliation between the above masses and `global_perf`.
  **The exact form of this assertion is derived by experiment, not assumed — see the null-result
  step in the action below.**
- Test D (the data is genuinely there, not an empty formality): at eta strictly between 0 and 1,
  `partial_loss` is non-empty and every key is a string absent from `dist`'s keys; at eta=1.0 its
  total mass is <= 1e-9; at eta=0.0 (weight-1) its total mass is ~1.0, mirroring the existing
  `test_survival_mass_is_monotonically_non_increasing_as_eta_decreases` assertion that
  `residual_zero == 1.0`.
  </behavior>
  <action>
**Null-result step, run FIRST, before writing Test C's assertion** (CLAUDE.md's null-result gate:
write the predicted closed form, then run it against the data, then revise — derivation by
experiment is fine, symbolic derivation is not required):

Write the prediction down in the scratchpad first, e.g. "un-normalized physical mass on all
outcomes = `global_perf`, so `(sum(dist) + sum(partial_loss)) * global_perf == global_perf` and the
normalized total is exactly 1.0 independent of eta" — or whatever the executor actually predicts.
Then write a throwaway script in the scratchpad directory that calls both functions across an eta
grid (weight-1 n=2, weight-2 n=2 i=0 j=1, a couple of theta draws) and prints `sum(dist)`,
`sum(partial_loss)`, `residual`, `herald_failure_prob`, `global_perf`, and the predicted quantity.
Run it. Compare.

If the data matches the prediction, encode it as Test C and state the relationship in one plain
sentence in the test's docstring. If the data does NOT match, revise the prediction, re-run, and
document in the summary which prediction survived and which was wrong.

**Hard rule:** do not loosen a tolerance, drop an assertion, or reshape Test C to fit numbers you
do not understand. If after two revision attempts the `global_perf` relationship still is not
explicable in one sentence, STOP and report that in the summary with the printed numbers, rather
than shipping an assertion that merely happens to pass. A test that was fitted to the output
instead of predicting it is exactly the failure mode this milestone exists to correct.

Then add Tests A/B/D and the settled Test C to the two test files. Keep them at small n (weight-1
n in {1,2}; weight-2 n=2, i=0, j=1) — these run a real `Processor.probs()` per call and the suite
is already slow. Do not add any prose, comment, or docstring interpreting what the partial-loss
patterns MEAN physically; REQUIREMENTS.md:37 defers that. Describe only the mass bookkeeping.

Delete the scratchpad script when done; it is not a deliverable.
  </action>
  <verify>
    <automated>cd "C:/Users/cuqui/merlin-quantum-case-study/.claude/worktrees/serene-sanderson-728202" && PYTHONPATH=src C:/Users/cuqui/merlin-quantum-case-study/venv/Scripts/python.exe -m pytest -q tests/hardness/test_loss_model.py tests/hardness/test_loss_model_weight2.py</automated>
    <automated>cd "C:/Users/cuqui/merlin-quantum-case-study/.claude/worktrees/serene-sanderson-728202" && PYTHONPATH=src C:/Users/cuqui/merlin-quantum-case-study/venv/Scripts/python.exe -m pytest -q</automated>
  </verify>
  <done>
New tests exist in both files and pass. Full suite green, count strictly greater than Task 1's
baseline. Test C's docstring states the derived `global_perf` relationship in one sentence, and the
summary records whether the initial prediction held or was revised. No file under `results/` was
touched; no sweep script was run.
  </done>
</task>

<task type="auto">
  <name>Task 3: Fix the stale trainability-study.md anchor in technical-findings.md</name>
  <files>docs/technical-findings.md</files>
  <action>
`docs/technical-findings.md` line 7 contains
`[docs/trainability-study.md](trainability-study.md#correction-2026-09-03--the-exponential-decay-verdict-is-a-pipeline-artifact-not-a-trainability-finding)`.
That slug was computed from the heading's text BEFORE it gained ", revised after an independent
adversarial review". The heading has since changed; the link is broken.

Recompute the slug from the heading's LIVE text. Do not trust any pre-computed slug — including the
one in the note below. This is precisely the class of bug (a slug silently drifting from its
heading) that produced the stale anchor in the first place, so re-deriving it is the whole point.

1. Run `grep -n "^## Correction" docs/trainability-study.md` and read the actual heading text.
2. Apply GitHub slug rules, confirmed against this repo's own working precedent (the sibling anchor
   `...#correction-2026-09-03--the-gradient-computation-method-itself-was-chosen-without-asking-what-an-iqp-model-actually-needs`
   on line 11, which resolves correctly today): lowercase everything; DELETE parentheses, commas,
   and the em-dash entirely — delete the character, do not replace it with a hyphen; every space
   that remains after those deletions becomes its own hyphen; hyphens are never collapsed, so a
   deleted em-dash surrounded by two spaces yields a double hyphen.
3. Replace only the fragment after `trainability-study.md#` on line 7. Change nothing else on that
   line and no other line in the file.

Planner's independently-computed expectation, for reconciliation only, NOT to be pasted in blind:
`correction-2026-09-03-revised-after-an-independent-adversarial-review--the-exponential-decay-verdict-is-a-pipeline-artifact-not-a-trainability-finding`.
If the executor's own recomputation from the live heading disagrees with this, do not silently pick
either one — recheck the heading text character by character and report the discrepancy.

Two other anchors on nearby lines were checked during planning and are CORRECT — leave them alone:
line 7's `hardness-under-loss-study.md#correction-2026-09-03--tvd-vs-eta-is-a-closed-form-with-no-circuit-content-here-is-the-actual-result`
(resolves to that file's line 22 heading) and line 11's gradient-computation-method anchor
(resolves to trainability-study.md line 45). Re-verify both with the same grep-and-compare method
while you are in the file; if either is also stale, fix it and say so in the summary.

This is a plain broken-link fix. It gets NO dated correction section, no "Correction (2026-09-XX)"
prose, no changelog entry — the repo's additive-correction convention is for changed claims, and no
claim changes here.
  </action>
  <verify>
    <automated>cd "C:/Users/cuqui/merlin-quantum-case-study/.claude/worktrees/serene-sanderson-728202" && C:/Users/cuqui/merlin-quantum-case-study/venv/Scripts/python.exe -c "
import re, pathlib
def slug(h):
    return re.sub(r'[^\w\s-]', '', h.lower(), flags=re.UNICODE).replace(' ', '-')
docs = pathlib.Path('docs')
headings = {}
for p in docs.glob('*.md'):
    for line in p.read_text(encoding='utf-8').splitlines():
        m = re.match(r'^#+\s+(.*)$', line)
        if m:
            headings.setdefault(p.name, set()).add(slug(m.group(1).strip()))
bad = []
text = (docs / 'technical-findings.md').read_text(encoding='utf-8')
for target, frag in re.findall(r'\]\(([a-z0-9\-]+\.md)#([^)]+)\)', text):
    if frag not in headings.get(target, set()):
        bad.append((target, frag))
print('BROKEN:', bad)
assert not bad, bad
print('all technical-findings.md cross-doc anchors resolve')
"</automated>
  </verify>
  <done>
The verify script prints `all technical-findings.md cross-doc anchors resolve` and exits 0. The diff
touches exactly one fragment on line 7 (plus any additional stale anchor the script caught, if any),
and adds no prose.
  </done>
</task>

</tasks>

<threat_model>
## Trust Boundaries

| Boundary | Description |
|----------|-------------|
| (none introduced) | Pure in-process library change plus a markdown link fix. No network, no user input, no serialization boundary, no new file read/write. |

## STRIDE Threat Register

| Threat ID | Category | Component | Disposition | Mitigation Plan |
|-----------|----------|-----------|-------------|-----------------|
| T-ukn-01 | Tampering | shipped numbers under `results/` | mitigate | D-04 forbids touching `results/` or re-running any sweep; `sweep.py`'s own return contract is unchanged, so no CSV can shift. Task 2's Test A asserts `sum(partial_loss) == residual`, proving the existing scalar is untouched. |
| T-ukn-02 | Tampering | silent caller breakage from arity change | mitigate | D-01's append-only shape makes every missed caller fail loudly at unpack time; Task 1's verify re-greps the whole repo and runs the full suite. |
| T-ukn-SC | Tampering | npm/pip/cargo installs | n/a | No package installs in this plan. |
</threat_model>

<source_audit>
| Source | Item | Status | Covered by |
|--------|------|--------|------------|
| REQ | REFRAME-02 — both functions return non-post-selected outcomes as their own keys | COVERED | Task 1 (implementation), Task 2 (the required mass test) |
| REQ | REFRAME-02 — "No analysis of it in this milestone" | COVERED | D-04 and Task 2's explicit prohibition on interpretive prose |
| GOAL | Fix `technical-findings.md` line 7's stale anchor | COVERED | Task 3 |
| CONTEXT | D-01 append-only, one consistent position across both functions | COVERED | locked_decisions D-01, applied in Task 1 |
| CONTEXT | D-02 `str(state)`-keyed dict | COVERED | locked_decisions D-02 |
| CONTEXT | D-03 weight-2 renormalization parity with `residual` | COVERED | locked_decisions D-03, asserted by Task 2 Test A |
| CONTEXT | D-04 no `results/` change, no sweep re-run, no new analysis | COVERED | locked_decisions D-04, Task 1/2 done criteria |
| CONTEXT | Repo-wide re-grep for both function names in the verify step | COVERED | Task 1 verify (first automated command) |
| CONTEXT | New tests go in the existing test files | COVERED | Task 2 `files` and behavior block |

No unplanned items. Two callers absent from the task brief's grounding notes
(`julia/generate_reference.py`, `tests/scripts/v3_hardness/test_merlin_loss_model.py`'s monkeypatch
stub) were found during planning and folded into Task 1 rather than deferred.
</source_audit>

<verification>
Run from the worktree root, with the venv from the MAIN checkout:

```
cd "C:/Users/cuqui/merlin-quantum-case-study/.claude/worktrees/serene-sanderson-728202"
PYTHONPATH=src C:/Users/cuqui/merlin-quantum-case-study/venv/Scripts/python.exe -m pytest -q
```

Test count must be strictly greater than the baseline captured before Task 1's first edit, and no
previously-passing test may fail.

`git status` must show no modification to anything under `results/`.
</verification>

<success_criteria>
- Both functions return `partial_loss` appended last; both docstrings extended additively.
- All five positional-unpack call sites plus the one monkeypatch stub updated; repo-wide grep clean.
- `sum(partial_loss.values()) == residual` asserted and passing in both test files.
- The `global_perf` reconciliation was predicted first, then checked against real output, and the
  summary says whether the prediction held.
- `docs/technical-findings.md`'s cross-doc anchors all resolve.
- Full suite green, count up, `results/` untouched, no sweep re-run, no interpretive prose added.
</success_criteria>

<output>
Create `.planning/quick/260903-ukn-reframe-02-stop-loss-model-py-and-loss-m/260903-ukn-SUMMARY.md` when done.

The summary must record: the pre-change test-count baseline and the post-change count; any caller
found by the repo-wide grep that was not in this plan's caller inventory; and the outcome of Task
2's null-result step (prediction made, whether it survived contact with the data, and the one-
sentence `global_perf` relationship that was settled on).
</output>
