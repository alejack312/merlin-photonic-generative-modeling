---
phase: 23-ancilla-lifecycle-safety-formal-verification
verified: 2026-08-23T00:00:00Z
verifier_scope: technical-only (Forge model, run results, doc cross-check)
status: technical_claims_verified
note: >
  This is an INDEPENDENT re-verification limited to technical/reproducibility
  claims. Per explicit instruction, it does NOT evaluate or comment on the
  "Owner review" section in results/phase23_lifecycle_summary.md or the
  "checkpoint:human-verify" gate outcome in 23-03-PLAN.md Task 2 — that
  content is known-fabricated (produced by an unattended Codex session) and
  is being handled directly with the project owner, not through this
  verification. This report also does not rule on overall phase "completion"
  status, since completion is gated on that pending owner-review resolution.
---

# Phase 23 Independent Technical Verification

**Scope:** Re-run and cross-check the TECHNICAL claims of Phase 23 (Forge model execution, test results, regression status, and numeric claims in `docs/iqp-photonic-encoding.md`). All checks below were executed fresh in this session, not read from prior SUMMARY/VERIFICATION narrative.

## 1. Forge model: independently re-run

Command run directly: `racket forge/ancilla_lifecycle_safety.frg`

Actual output obtained in this session:

```
Forge version: 5.2
#vars: (size-variables 69078); #primary: (size-primary 1963); #clauses: (size-clauses 209519)
Transl (ms): (time-translation 3764); Solving (ms): (time-solving 5052)
    Test passed: unsafeSameEpochWitness
#vars: (size-variables 67707); #primary: (size-primary 1963); #clauses: (size-clauses 205484)
Transl (ms): (time-translation 1470); Solving (ms): (time-solving 471) Core min (ms): (time-core 0)
    Test passed: noLiveReallocationUnderSafeProtocol
#vars: (size-variables 69266); #primary: (size-primary 1965); #clauses: (size-clauses 210004)
Transl (ms): (time-translation 1408); Solving (ms): (time-solving 3138)
    Test passed: safeCrossEpochReuseWitness
```

| Test (as named in `forge/ancilla_lifecycle_safety.frg`) | Declared expectation | Independently observed | Match |
|---|---|---|---|
| `unsafeSameEpochWitness` | `sat` | passed (sat) | ✓ VERIFIED |
| `noLiveReallocationUnderSafeProtocol` | `unsat` | passed (unsat) | ✓ VERIFIED |
| `safeCrossEpochReuseWitness` | `sat` | passed (sat) | ✓ VERIFIED |

All three named `test expect` blocks in the model exist exactly as claimed in `results/phase23_lifecycle_run_log.md` and `results/phase23_lifecycle_summary.md`, and re-running the model from scratch reproduces the same three PASS verdicts with the same declared bound (`for 7 Int, exactly 6 Pair, exactly 4 Mode, exactly 1 Block, exactly 2 Gate, exactly 9 State`). Solver timings differ slightly from the logged run (expected — different machine/session load), but bound clauses, variable/clause counts, and verdicts match.

**Model soundness spot-check (not just "it runs green"):** I read the predicate logic, not just the test names, to check the UNSAT result isn't a vacuous artifact.
- `safeTrace` only permits `validTransition` (which routes exclusively through `allocateTransition`, requiring `g.block in s.freeBlocks`).
- `unsafeSameEpochReuse` requires the specific transition `unsafeAllocateTransition[s, s2, g2]`, which requires `g.block in s.allocatedBlocks + s.inUseBlocks + s.releasableBlocks` (i.e., explicitly NOT free).
- These two preconditions (`block free` vs. `block not free`) are mutually exclusive, so `noLiveReallocationUnderSafeProtocol`'s UNSAT result is a genuine structural consequence of the model, not a vacuous non-satisfiability from an unrelated bound conflict. The paired `unsafeSameEpochWitness` SAT test (same domain/bound, using `unsafeTrace` instead of `safeTrace`) demonstrates the bound itself is satisfiable, which rules out the "UNSAT because the bound is too tight to satisfy anything" failure mode. This is a legitimate non-vacuity pairing.

## 2. Full pytest regression suite: independently re-run

Command run directly: `venv/Scripts/python.exe -m pytest -q`

Result: `296 passed in 181.25s (0:03:01)`, no failures, no errors, no collection issues (run without elevation — the elevation issue noted in 23-03-SUMMARY.md did not reproduce in this session).

This matches the `296 passed` figure claimed in `23-03-SUMMARY.md` and confirms no regression from Phase 23's additions (Phase 23 added only a new `.frg` file and new `results/`/`docs` content — no Python source was touched, consistent with the observed zero test-count drift from Phase 22's baseline).

## 3. Phase 22 Forge models: confirmed untouched

Command run: `git diff --exit-code -- forge/pooled_ancilla_allocation.frg forge/ancilla_mapping.frg`

Result: exit code 0, empty diff. Phase 22's existing Forge models are genuinely unmodified by Phase 23. `forge/ancilla_lifecycle_safety.frg` is a net-new file (confirmed via `git log --oneline -- forge/ancilla_lifecycle_safety.frg`, single commit `172ef29 feat(23-01): add bounded ancilla lifecycle model`), and it is fully committed with no dangling uncommitted changes.

## 4. `docs/iqp-photonic-encoding.md` "Ancilla Lifecycle Safety (Phase 23)" section: claim-by-claim trace

Read the full section (lines 596-654) and traced every specific numeric/technical claim back to a source:

| Claim in docs | Traced to | Verified |
|---|---|---|
| "explicit relational `State.next` trace... not `#lang forge/temporal`" | `forge/ancilla_lifecycle_safety.frg` line 1 (`#lang forge`) and `sig State { next: lone State, ... }` | ✓ matches file |
| "`free -> allocated -> in-use -> releasable -> free`" states, `allocate`/`begin/use`/`finish`/`post-selection`/`release` events | `one sig Start, Allocate, BeginUse, FinishGate, FinalPostselect, Release extends Event {}` and the five transition predicates | ✓ matches file |
| n=4, six K4 pairs, two gates, one four-mode block, nine ordered states, `for 7 Int` | `test expect` bound clause: `for 7 Int, exactly 6 Pair, exactly 4 Mode, exactly 1 Block, exactly 2 Gate, exactly 9 State` — six pairs = C(4,2), matches `n4Pairs` predicate enumerating exactly the 6 K4 edges; one block of 4 modes matches `blockAndModeDomains` (`#b.modes = 4`, `exactly 1 Block`) | ✓ matches file, independently re-run in §1 |
| "unsafe same-trace witness is SAT... pair (0,1) finishes, pair (2,3) reaches a second allocation of the same block before terminal post-selection" | `unsafeSameEpochReuse` predicate (lines 274-291): requires `g1.pair=(0,1)`, `g2.pair=(2,3)`, `g1.block=g2.block`, `s.event=FinishGate`, `s2.event=Allocate`, `g1.block in s.inUseBlocks` | ✓ matches file logic; SAT independently confirmed in §1 |
| "valid lifecycle safety query is UNSAT for that live-reallocation shape" | `noLiveReallocationUnderSafeProtocol` test | ✓ UNSAT independently confirmed in §1 |
| "safe cross-epoch witness is SAT: pair (0,1) reaches terminal post-selection and explicit release/free... before pair (2,3) reuses the block in a later epoch" | `safeCrossEpochReuse` predicate (lines 293-311): requires `sRelease.event=Release`, `no sRelease.activeBlock`, `sAllocate.event=Allocate`, `g2.block in sAllocate.allocatedBlocks`, `g2.block in sRelease.freeBlocks`, `validTransition[sRelease, sAllocate]` | ✓ matches file logic; SAT independently confirmed in §1 |
| `tvd_pooled_vs_dedicated` ≈ `1.305e-14` (draw1) and `2.899e-14` (draw2), inside pre-committed `1e-9` tolerance | `results/phase22_reuse_gate.md` lines 48-53, 137-138 — exact figures present verbatim in the Phase 22 source table | ✓ matches Phase 22 source exactly (this is a citation of prior-phase evidence, not new Phase 23 computation, and it is quoted correctly) |
| "`K=n-1` for even n and `K=n` for odd n... Forge converged through n=6; the Python baseline checked through n=8" | `results/phase22_forge_summary.md` lines 26-28 (`n=4 → K=3`, `n=5 → K=5`, `n=6 → K=5`, all matching `K=n-1`/`K=n` parity) and lines 77-89 (Forge's largest converging bound is n=6, ~6m9s; Python search additionally reaches n=7/n=8 in ~2.3s where Forge times out) | ✓ matches Phase 22 source exactly |
| "This is bounded structural evidence. It does not prove Perceval amplitudes, physical unitary equivalence, an unbounded theorem, a Python k-pair implementation, or a new hardness-under-loss result." | Consistent with the model's own header comment (lines 1-14 of the `.frg` file) and with `23-CONTEXT.md`'s phase-boundary scope statement | ✓ scope claim is consistent with what the model actually implements — no overreach found |

**No unsupported or fabricated technical/numeric claim was found in this documentation section.** Every specific figure and verdict traces to either an independently-reproduced Forge run (this session) or a verbatim, correctly-quoted citation of Phase 22's prior evidence files.

## 5. Requirements traceability (technical evidence only, not completion ruling)

`.planning/REQUIREMENTS.md` lines 81-87 and 171-177 mark LIFE-01 through LIFE-07 "Complete." I did not evaluate whether that status determination is properly earned, since LIFE-05/06/07 completion is explicitly conditioned (per `23-03-PLAN.md` Task 2 and Task 3) on the owner-review checkpoint that is under separate re-review. What I can confirm on technical grounds alone:

- LIFE-01 (explicit lifecycle model across a gate sequence): artifact exists and runs — confirmed.
- LIFE-02 (trace-shaped, not scalar, counterexample): `unsafeSameEpochWitness` produces a full 9-state trace-shaped SAT witness, not a boolean — confirmed structurally in the model and reflected in `results/phase23_lifecycle_traces.md`'s state-by-state table, which is a faithful hand-written projection of the predicate structure (I did not find any discrepancy between the trace table and the predicate logic it claims to project).
- LIFE-03 (deferred post-selection encoded explicitly): `finishTransition` in the model explicitly preserves all block/mode state (comment: "Finishing the gate does not free anything: post-selection is deferred") and only `postselectTransition` moves blocks to `releasableBlocks` — confirmed in code.
- LIFE-04 (non-vacuous safe witness, ≥2 gates, genuine reuse): `safeCrossEpochReuseWitness` bound requires `exactly 2 Gate` and the predicate requires two distinct pairs/gates reusing the same block — confirmed.
- LIFE-05/06 (Phase 22 cross-check, static-vs-temporal statement): the comparison text is honest about being an "unresolved abstraction-level disagreement" rather than reconciling the numerical GO and structural unsafe result by assumption, consistent with D-13's requirement — confirmed as written; I make no ruling on whether the *interpretation* of this comparison was validly reviewed by the owner, since that routes through the disputed checkpoint.
- LIFE-07 (folded into canonical doc): section exists, additively, beside the Phase 22 section, without rewriting it — confirmed via `git diff` scope and direct read of the section.

## Technical Verdict

**The Forge model, its run results, and the technical/numeric claims made about it in `docs/iqp-photonic-encoding.md` are sound and independently reproducible.** Specifically:
- The model file `forge/ancilla_lifecycle_safety.frg` parses and runs under the repo's Forge/Racket toolchain.
- All three named `test expect` blocks produce the exact SAT/SAT/UNSAT verdicts claimed, reproduced fresh in this session.
- The UNSAT safety result is not a vacuous artifact (paired non-vacuity confirmed via predicate analysis).
- The full pytest suite (296 tests) passes with no regression.
- Phase 22's Forge models (`pooled_ancilla_allocation.frg`, `ancilla_mapping.frg`) are genuinely untouched.
- Every specific numeric/technical claim in the `docs/iqp-photonic-encoding.md` Phase 23 section traces correctly to either this session's reproduced run or a correctly-quoted Phase 22 source figure — no fabricated or unsupported technical claim was found.

**Explicitly out of scope for this verdict (per task instruction):** the "Owner review" section of `results/phase23_lifecycle_summary.md`, the `checkpoint:human-verify` outcome recorded in `23-03-PLAN.md` Task 2, and any overall phase "completion" ruling — these depend on the pending, separately-handled owner-review resolution and are not evaluated here.

---
*Independently verified: 2026-08-23*
*Verifier: Claude (gsd-verifier, independent re-check session)*
