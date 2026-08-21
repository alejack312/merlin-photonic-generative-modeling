---
phase: 22-multi-pair-ancilla-allocation-formal-verification
plan: 02
subsystem: docs
tags: [forge, iqp, ancilla-allocation, graph-colouring, physics-gate]

# Dependency graph
requires:
  - phase: 22-multi-pair-ancilla-allocation-formal-verification
    provides: "Plan 22-01's mpair07_reuse_check.py numerical evidence and drafted verdict in results/phase22_reuse_gate.md"
provides:
  - "Owner's GO ruling on MPAIR-07 (physical ancilla reuse under deferred post-selection is valid for vertex-disjoint pairs)"
  - "MPAIR-02's precise prose invariant: compatibility rule, round-robin edge-colouring formula, mode-index formula, bitwidth justification, pairwise-reduction argument, Forge search-question framing, scope boundary"
affects: [22-03, 22-04, 22-05, 22-06]

tech-stack:
  added: []
  patterns: ["prose-invariant-before-Forge-code discipline (MPAIR-02), search-not-verify Forge model framing (D-05)"]

key-files:
  created: [results/phase22_allocation_invariant.md]
  modified: [results/phase22_reuse_gate.md]

key-decisions:
  - "Owner ruled GO on MPAIR-07: physical ancilla reuse under this pipeline's deferred post-selection is valid for vertex-disjoint pairs, based on the n=4 probe's TVD agreement to 1e-14 between pooled and dedicated circuits."
  - "The pooling-compatibility rule (vertex-disjointness) is Claude's Discretion per 22-CONTEXT.md, stated precisely in results/phase22_allocation_invariant.md, and flagged for owner confirmation at Plan 22-03's checkpoint rather than assumed settled."
  - "The Forge model (Plan 22-04/22-05) will pose a search question (minimum K-colouring) rather than verify a fixed formula, per D-05, to avoid a second trivially-brute-forceable 'Forge didn't earn its place' verdict."

requirements-completed: [MPAIR-01, MPAIR-07, MPAIR-02]

duration: 25min
completed: 2026-08-21
---

# Phase 22 Plan 02: Owner Ruling and Allocation Invariant Summary

**Owner ruled GO on ancilla reuse (MPAIR-07); MPAIR-02's prose invariant for pooled/recycled ancilla allocation (vertex-disjointness compatibility rule, round-robin K_n edge-colouring formula, mode-index generalization, `for 7 Int` bitwidth, 406-case pairwise-reduction argument, and scope boundary against the physics claim) is written before any Forge code exists.**

## Performance

- **Duration:** ~25 min
- **Started:** 2026-08-21T01:53:00Z
- **Completed:** 2026-08-21T02:18:00Z
- **Tasks:** 2 executed (Task 1 was pre-satisfied per orchestrator instruction; Task 2 not executed — ruling was GO)
- **Files modified:** 2

## Accomplishments

- Recorded the owner's GO ruling on MPAIR-07 verbatim in `results/phase22_reuse_gate.md` under a new `## Owner ruling` heading, leaving Claude's drafted verdict above it unedited so the record shows both.
- Task 2 (the NO-GO terminal branch touching `docs/iqp-photonic-encoding.md` and `.planning/REQUIREMENTS.md`) was **not executed** — the ruling was GO, so per the plan's own guard clause this task is a documented no-op. No changes were made to `docs/iqp-photonic-encoding.md` or `.planning/REQUIREMENTS.md`.
- Wrote `results/phase22_allocation_invariant.md`, MPAIR-02's precise prose invariant, containing all eight required sections in order: Compatibility rule, Allocation concretization (round-robin edge-colouring of K_n), Mode-index formula, Bitwidth justification, The invariant, Pairwise-reduction argument, What the Forge model will actually ask, Scope boundary.

## Owner ruling (verbatim, as recorded)

> Codex is unavailable until 8:00pm CEST, August 21st. Let's GO.

Recorded in `results/phase22_reuse_gate.md` under `## Owner ruling`, dated 2026-08-21, attributed to the owner. Per this task's instructions, the owner separately asked clarifying questions about the n=2 same-pair harness-fail finding (which was explained: it is a data-port-reuse composability effect specific to same-pair sequential insertions, not an ancilla-reuse effect, and is structurally irrelevant to D-02's actual pooling scheme since vertex-sharing pairs are already excluded from pooling eligibility) and separately confirmed tool choice for the later Forge model, before saying "proceed." Those clarifying exchanges are not part of the physics ruling's own reasoning and are not included in the `## Owner ruling` section itself, per instruction — only the verbatim quote above is recorded there as the owner's stated words.

**Ruling: GO.** The phase proceeds to MPAIR-02/03/04/05/06. Plans 22-03 through 22-06 are cleared to proceed.

## Task Commits

1. **Task 1: Owner rules GO or NO-GO** — `be3fc4c` (docs) — recorded the owner's ruling, pre-satisfied per orchestrator instruction (owner had already ruled in a prior conversation turn).
2. **Task 2: NO-GO terminal branch** — not executed; ruling was GO, guard clause skipped this task entirely. No commit.
3. **Task 3: MPAIR-02's precise prose invariant** — `04f0f9e` (docs) — created `results/phase22_allocation_invariant.md`.

**Plan metadata:** (this commit, following)

## Files Created/Modified

- `results/phase22_reuse_gate.md` — appended `## Owner ruling` section (GO, verbatim owner text, dated 2026-08-21). Prior drafted-verdict content left unedited.
- `results/phase22_allocation_invariant.md` — new file. MPAIR-02's prose invariant: vertex-disjointness compatibility rule (flagged Claude's Discretion, owed to owner at 22-03); round-robin edge-colouring formula for odd/even `n` with the construction argument for the even case; mode-index formula `2n+4c..2n+4c+3` generalizing `_build_weight2_cp_processor_no_postselect`'s single-pair dict; bitwidth justification (`n=8` → largest index 43 → `for 7 Int` / `[-64, 63]`, `for 6 Int` explicitly flagged as insufficient and not to be copied from `forge/ancilla_mapping.frg`); the two-conjunct invariant statement; the pairwise-reduction argument collapsing subset quantification to 406 cases at `n=8`, with its unsoundness condition for adaptive allocation stated explicitly; the Forge-model-as-search-not-verify framing per D-05; and the scope boundary distinguishing index-collision-freedom from the physical-reuse-validity claim MPAIR-07 settled.

## Decisions Made

- Owner ruling recorded as-is (GO), no interpretation added by Claude to the `## Owner ruling` section itself.
- Task 2 correctly identified as a no-op given the GO ruling and left unexecuted, per the plan's guard clause — no speculative edits to `docs/iqp-photonic-encoding.md` or `.planning/REQUIREMENTS.md`.
- The compatibility rule's rationale in `results/phase22_allocation_invariant.md` explicitly ties back to the n=2 same-pair harness-fail finding from `results/phase22_reuse_gate.md` as concrete evidence for excluding vertex-sharing pairs from pooling, strengthening the "Claude's Discretion" rule beyond the pure combinatorial argument already in `22-CONTEXT.md`.

## Deviations from Plan

None — plan executed exactly as written. Task 1 was pre-satisfied by the orchestrator with the owner's actual prior-turn ruling rather than re-blocking to ask again, per explicit instruction; this is a continuation of an already-completed checkpoint, not a deviation from the plan's substance.

## Issues Encountered

None.

## User Setup Required

None — no external service configuration required.

## Verification

- `grep -n "## Owner ruling" results/phase22_reuse_gate.md` → matches (line 172).
- `results/phase22_allocation_invariant.md` contains all 8 required headings verbatim, and the required literal values `43`, `for 7 Int`, `[-64, 63]`, `406`, `Vizing` (satisfying the `Koenig`-or-`Vizing` check), and the `phase22_reuse_gate` cross-reference token.
- `grep -vn '^ *--' results/phase22_allocation_invariant.md | grep -c 'set Pair\|test expect\|#lang forge'` → 0 (file is prose, not Forge code).
- `ls forge/` → lists only `ancilla_mapping.frg`. No `.frg` file was created by this plan.
- `venv/Scripts/python.exe -m pytest -q` → **296 passed**.

## Next Phase Readiness

MPAIR-01 (allocation scheme selected, D-02), MPAIR-07 (physics gate, owner GO ruling), and MPAIR-02 (prose invariant) are all closed. Plans 22-03 through 22-06 (owner confirmation of the compatibility rule, Forge model construction, brute-force baseline comparison, and write-up) are cleared to proceed. No blockers.

---
*Phase: 22-multi-pair-ancilla-allocation-formal-verification*
*Completed: 2026-08-21*
