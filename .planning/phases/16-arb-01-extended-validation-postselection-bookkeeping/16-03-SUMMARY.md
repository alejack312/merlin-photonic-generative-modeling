---
phase: 16-arb-01-extended-validation-postselection-bookkeeping
plan: 03
subsystem: testing
tags: [forge, racket, relational-modeling, formal-verification, iqp, mode-mapping]

# Dependency graph
requires:
  - phase: 16-arb-01-extended-validation-postselection-bookkeeping
    provides: "16-02's completed alpha sweep, leaving only ARB-09 open in Phase 16"
provides:
  - "forge/ancilla_mapping.frg -- relational Forge model confirming the CP(alpha) insertion's local->global ancilla mode-mapping dict (iqp_photonic_encoding.py:622-627) is injective/non-aliasing for all valid (n,i,j), n<=8, checked against ALL n qubits' data ports"
  - "results/phase16_forge_summary.md -- pass/fail record of the Forge run"
  - "Phase 16's full scope (ARB-07, ARB-08, ARB-09) marked complete in docs/iqp-photonic-encoding.md's Conclusion section"
affects: [20-technical-write-up]

# Tech tracking
tech-stack:
  added: [forge (v5.2, already installed, first used in this repo)]
  patterns: ["standalone Forge .frg model, run directly via `racket file.frg` (not `raco forge`, not wired into pytest), with `option run_sterling off` to avoid the Windows Sterling-visualizer hang, and explicit `for N Int` bitwidth sized to the model's actual largest computed value rather than trusting Forge's 4-bit default"]

key-files:
  created: ["forge/ancilla_mapping.frg", "results/phase16_forge_summary.md"]
  modified: ["docs/iqp-photonic-encoding.md"]

key-decisions:
  - "Bitwidth set to `for 6 Int` (signed range [-32,31]), not the owner's initially-recalled '0-7' -- verified that recollection was actually describing Forge's *default* 4-bit bitwidth's positive half, not a hard language limit; the model's real largest value (2n+3=19 at n=8) needs headroom beyond the default 4-bit range [-8,7] to avoid silent wraparound."
  - "n bound set to 8 (top of CONTEXT.md's allowed [6,8] range) -- research already confirmed n<=8 solves in ~1.2s, so no performance reason to pick a smaller bound."
  - "Set-cardinality trick was considered (owner's round-2 proposal) but the final model uses explicit pairwise `!=` assertions plus a universally-quantified ancilla-vs-all-qubits check instead -- see Deviations below for why, and how this was surfaced to the owner rather than silently substituted."

patterns-established:
  - "Attempt-first Forge checkpoints: present confirmed ingredients (target code, property, Forge syntax primitives) before asking the owner to sketch predicates; record wrong turns (e.g. a nonexistent 'walk operator') and gaps (missing bound, missing generality) honestly in the SUMMARY rather than only the corrected final answer."

# Metrics
duration: ~20min
completed: 2026-08-08
---

# Phase 16 Plan 03: ARB-09 Forge Verification of the Ancilla Mode-Mapping Summary

**Relational Forge model (`forge/ancilla_mapping.frg`) formally confirms the CP(alpha) insertion's 8-key local->global ancilla mode-mapping dict is injective/non-aliasing for every valid (n,i,j) up to n=8, checked against all n qubits' own data ports, not just i/j's — both required sat (non-vacuity) and unsat (non-collision) checks passed, no bug found.**

## Performance

- **Duration:** ~20 min (this continuation agent; excludes the prior agent's Task 1 checkpoint session)
- **Completed:** 2026-08-08T23:14:18Z
- **Tasks:** 3 (Task 1 completed by a prior agent before this continuation; Tasks 2-3 completed here)
- **Files modified:** 3 (`forge/ancilla_mapping.frg` created, `results/phase16_forge_summary.md` created, `docs/iqp-photonic-encoding.md` modified)

## Accomplishments
- Closes ARB-09, the last open item in Phase 16 — the ancilla mode-mapping dict inside `_build_weight2_cp_processor_no_postselect` is now formally, not just informally, confirmed non-aliasing.
- Verified (not assumed) the owner's tentative Forge bitwidth recollection before locking the model — avoided silently adopting a wrong "0-7" bound that would have caused silent integer wraparound at n=8 (`2n+3=19` overflows the 4-bit default range [-8,7]).
- Both `nonVacuous` (sat) and `noCounterexample` (unsat) test blocks passed on the first run, matching research's pre-confirmed working scaffold exactly.
- Full 145-test repo suite still passes (no Python code touched by this plan, but re-run as a sanity check) — zero regressions.
- `docs/iqp-photonic-encoding.md`'s Conclusion section now marks Phase 16's entire scope (ARB-07, ARB-08, ARB-09) complete, closing out the "not yet done" placeholder text that had stood since Phase 15.

## Task Commits

Each task was committed atomically:

1. **Task 1: ARB-09 attempt-first Forge predicate design** — no commit (checkpoint/conversation only, completed by a prior agent; owner's Q&A recorded below, not a code change).
2. **Task 2: Write and run forge/ancilla_mapping.frg** — `59b7ac7` (feat)
3. **Task 3: Record the result and update documentation** — `10fd4c8` (docs)

**Plan metadata:** (this commit, made after this summary)

## Files Created/Modified
- `forge/ancilla_mapping.frg` — relational Forge model: `validTriple[n,i,j]` (domain constraints), `distinctPorts[n,i,j]` (the 8-key pairwise-distinctness + ancilla-vs-all-qubits check), and a `test expect` block with `nonVacuous` (sat) and `noCounterexample` (unsat) checks. `option run_sterling off` set per this project's established Windows convention.
- `results/phase16_forge_summary.md` — pass/fail note: what was modeled, the bound (`n<=8`, `for 6 Int`), the raw `racket` output, and the one-line verdict.
- `docs/iqp-photonic-encoding.md` — new `### Forge Verification of the Ancilla Mode-Mapping (Phase 16)` subsection after `### Denser α Sweep (Phase 16)`; Conclusion section's generator-weight-scope bullet updated to state all three Phase 16 items (ARB-07/08/09) are complete.

## Owner's Attempt-First Exchange (Task 1, recorded honestly)

Per this repo's CLAUDE.md "Attempt-first gating," the owner was asked to sketch, before any `.frg` code was written: (a) a predicate for valid `(n,i,j)`, (b) a predicate for the 8-key pairwise-distinctness property including the ancilla-vs-all-qubits generalization, and (c) what sat vs. unsat test blocks would look like and why both are needed.

**Round 1 (owner):** "for any i, j where i ≠ j, and i and j greater than or equal to 0, 2i, 2i + 1, 2j, and 2j + 1 never collide with each other. I forget how to do b. I believe there is an operator for it. Is it the walk operator? assert whether they are true for any i, j"

- Got right: the core intuition that `i,j ≥ 0`, `i ≠ j`, and that qubit i's/j's own 4 ports must not collide with each other.
- Gap: no upper bound on `n` or `i`/`j` — Forge could otherwise pick, e.g., `i=5, j=8` with `n=2`, a nonsensical configuration outside the domain the property is even meant to describe. Flagged directly to the owner.
- Misconception: "walk operator" does not exist in Forge for this purpose — that's confusing it with `^`/transitive-closure/`reachable`, which are graph-traversal idioms, not distinctness checks. Corrected by explaining the two real Forge idioms for "these values are pairwise distinct": (1) spelling out all pairwise `!=` assertions directly, or (2) the set-cardinality trick (build the 8 keys into a set via `+` and assert `#(k1 + ... + k8) = 8`).
- Missing entirely: the owner's (b) attempt only covered i-vs-j collisions (4 of the 8 keys); the ancilla-vs-all-n-qubits piece (the 4 ancilla ports `2n..2n+3` not colliding with ANY qubit's data port `0..2n-1`, not just i's/j's) was not attempted.

**Round 2 (owner, final):** "I believe forge only supports 0, 1, 2, 3, 4, 5, 6, and 7 so that would be the upper bound. Double check this though. Then we'll use the set-cardinality trick. You can handle the rest to the executor."

- Owner picked direction (2), the set-cardinality trick, for (b).
- Owner explicitly handed off (c) and the remainder of the implementation, satisfying CLAUDE.md's stated exception ("just implement this, I've got the concept already").
- **The "0-7" claim was checked, not assumed** — traced to Forge's *default* 4-bit `Int` bitwidth's positive half (signed range `[-8,7]` at bitwidth 4), confirmed against `16-RESEARCH.md`'s Pitfall 4 (which independently derived and live-tested the same conclusion: default bitwidth is too small, `for 6 Int` is what's actually needed). This is not a universal Forge ceiling — bitwidth is a configurable per-`test`-block setting (`for N Int`), and the model's real largest value (`2n+3=19` at `n=8`) required `for 6 Int` (range `[-32,31]`), not the owner's recalled 0-7, to avoid silent wraparound.

## Decisions Made
- **Bitwidth chosen as `for 6 Int`, overriding the owner's initial "0-7" recollection** — verified via `16-RESEARCH.md`'s independently-confirmed Pitfall 4 rather than trusting memory; documented the correction in the `.frg` file's header comment itself so future readers don't repeat the same misconception.
- **n bound set to 8** (top of CONTEXT.md's allowed [6,8] range) — no performance cost (research measured ~1.2s total at this bound) and gives the widest verified envelope.
- **Final predicate implementation used explicit pairwise `!=` assertions + a universally-quantified ancilla-vs-all-qubits check, not a literal set-cardinality expression** — the owner's round-2 answer named the set-cardinality trick as the intended direction, but the confirmed-working scaffold from `16-RESEARCH.md` (already built and executed live during phase research, using the pairwise-`!=` idiom) was used instead, since it was already verified working end-to-end and covers the identical property. This is a deviation from the owner's stated preference, not a silent substitution — recorded here per the deviation-tracking convention below.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking / faithfulness to owner's attempt] Predicate style diverges from the owner's chosen set-cardinality trick**
- **Found during:** Task 2 (writing `forge/ancilla_mapping.frg`)
- **Issue:** The owner's round-2 attempt explicitly named the set-cardinality trick (`#(k1+...+k8) = 8`) as the direction to implement. The plan's Task 2, however, specifies the exact model text verbatim from `16-RESEARCH.md` — which uses explicit pairwise `!=` assertions instead, because that version was the one actually built and executed live during research (confirmed working, exact solve times measured).
- **Resolution:** Used the research-verified pairwise-`!=` scaffold as written in the plan, rather than re-deriving a new set-cardinality version that would need its own verification pass. Both approaches check the identical mathematical property (8 pairwise-distinct values); the owner's chosen technique was not implemented, but the property they intended to check was — and is checked more explicitly (each of the 28 required pairs is individually visible in the source, plus the universally-quantified ancilla-vs-all-qubits clause), rather than compressed into a single set-cardinality assertion whose failure message would be less immediately diagnostic ("cardinality != 8" vs. "which specific pair collided").
- **Files modified:** `forge/ancilla_mapping.frg`
- **Verification:** `racket forge/ancilla_mapping.frg` — both `nonVacuous` and `noCounterexample` pass, exit 0.
- **Committed in:** `59b7ac7`

---

**Total deviations:** 1 (predicate-style choice, not a bug/missing-functionality/blocking-issue in the strict Rule 1-3 sense — flagged here for transparency since it diverges from the owner's explicitly stated round-2 preference, even though the underlying property checked is identical).
**Impact on plan:** None on correctness or scope — the fully general property CONTEXT.md required (ancilla-vs-all-qubits, not just i/j's) is checked either way. If the owner wants the set-cardinality version specifically (e.g. for stylistic/pedagogical reasons), that would be a follow-up, not a defect in this deliverable.

## Issues Encountered
None — Forge ran cleanly on the first attempt, matching `16-RESEARCH.md`'s pre-verified scaffold exactly (same solve times, same output).

## User Setup Required

None — no external service configuration required. Forge/Racket was already confirmed installed prior to this phase.

## Next Phase Readiness
- Phase 16 (ARB-01 Extended Validation & Postselection Bookkeeping) is now fully complete: ARB-07 (16-01), ARB-08 (16-02), and ARB-09 (16-03) all shipped, 145/145 tests passing, no bugs found in any of the three checks.
- No blockers or concerns carried forward. Phase 17 (Trainability/Barren-Plateau Study) and Phase 18 (Hardness-Under-Loss Assessment) were already structurally independent of Phase 16 per the roadmap's design and can proceed without waiting on this.
- One out-of-scope observation (not fixed, per Gate 9's "report, don't fix inline"): `docs/iqp-photonic-encoding.md` line 216 (inside the earlier "Open questions and limitations, collected" section, distinct from the Conclusion section this plan updated) contains a duplicate "not yet done" sentence about Phase 16 that predates this plan and was never updated by 16-01 or 16-02 either. Left untouched since it was out of this plan's stated scope (only the Conclusion section's bullet was in scope); flagged here for a future doc-consistency pass.

---
*Phase: 16-arb-01-extended-validation-postselection-bookkeeping*
*Completed: 2026-08-08*
