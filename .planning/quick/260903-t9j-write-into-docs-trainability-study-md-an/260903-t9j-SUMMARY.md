---
quick_id: 260903-t9j
status: complete
---

# Quick Task 260903-t9j: Write the TCDQ/method-choice framing gap into the docs

## What was done

Wrote the framing gap an independent Fable 5.1 review of the v3.1 correction flagged — that IQP
Born machines are trained classically by construction (Van den Nest's cosine formula), that the
owner's spring-semester sibling project (`iqp-mmd-barren-plateau`) already had a correct
Hamming-kernel classical trainer implementing exactly that, and that v3.0 chose parameter-shift
through Perceval simulation instead because MerLin autograd was structurally unavailable — without
ever asking what gradient an IQP model actually needs. This had been explained verbally in chat
but never written into the docs.

**Task 1** — `docs/trainability-study.md`: inserted a new `###`-level subsection, headed
`### Correction (2026-09-03) — the gradient-computation method itself was chosen without asking
what an IQP model actually needs`, inside the existing `## Correction (2026-09-03, revised after
an independent adversarial review)` section (after its "What survives this correction" paragraph,
before `## Results`). Four parts: the Van den Nest mechanism, the sibling project's prior art,
what v3.0 did instead and why the stated MerLin-autograd reason was true but insufficient, and an
explicit scope statement that no number/curve/verdict changes.

**Task 2** — `docs/technical-findings.md`: added a third bullet to the existing
`## Correction (2026-09-03)` list, condensed to four sentences, with a resolving link to Task 1's
new heading.

## Exact heading text written (Task 1)

```
### Correction (2026-09-03) — the gradient-computation method itself was chosen without asking what an IQP model actually needs
```

## Computed anchor slug used in Task 2

```
trainability-study.md#correction-2026-09-03--the-gradient-computation-method-itself-was-chosen-without-asking-what-an-iqp-model-actually-needs
```

Verified by listing `docs/trainability-study.md`'s actual `###` headings and confirming a
character-by-character match (GitHub slug rules: lowercase; drop parens/em-dash/commas; each
remaining space becomes its own hyphen, not collapsed — confirmed against this repo's own existing
`correction-2026-09-03--the-exponential-decay-verdict-is-a-pipeline-artifact-not-a-trainability-finding`
anchor as a working precedent for the algorithm).

## `git diff --numstat`

```
12  0  docs/trainability-study.md
1   0  docs/technical-findings.md
```

Zero deletions in both files — additive-only convention satisfied.

## Regression sanity check

`venv/Scripts/python.exe -m pytest -q` (via `PYTHONPATH=src`, venv in the main checkout, not this
worktree): **425 passed** (296 base + 129 `v3_correction`). Documentation-only change; this
confirms nothing broke, not evidence for the change itself.

## Out-of-scope discovery (not fixed, flagged per the plan)

`docs/technical-findings.md` line 7 links to
`trainability-study.md#correction-2026-09-03--the-exponential-decay-verdict-is-a-pipeline-artifact-not-a-trainability-finding`,
but the actual heading in `docs/trainability-study.md` has since gained
`, revised after an independent adversarial review`, so the recorded slug no longer matches and
that anchor is dead. Left untouched per the plan's explicit scope discipline — worth a separate
one-line fix later.

## Process note: worktree-isolated executor hit #2015

The first executor dispatch for this quick task was spawned with `isolation="worktree"` and hit
the known Claude Code bug where `EnterWorktree` branches from `master` instead of the target
branch's actual HEAD (#2015) — its worktree landed on stale `master` (missing the entire v3.0/v3.1
correction history), and rather than completing the plan's two tasks it started reconstructing
already-existing correction content that was simply absent from its stale checkout. The
orchestrating session sent a mid-flight correction with the real expected base commit hash, but
the agent's task ended (`status: stopped`, no completion record) before finishing. The broken
worktree and its branch (`worktree-agent-aa526dcccd10671ae`) were inspected — confirmed nothing in
its staged/unstaged diff was new task content, all of it was a replay of pre-existing corrections
— then removed (`git worktree unlock` + `git worktree remove --force`, `git branch -D`) rather than
merged. Both tasks were then executed directly on the current branch (no worktree isolation) using
the exact grounding facts and constraints already locked in `260903-t9j-PLAN.md`, with the same
verify commands run manually and passing.
