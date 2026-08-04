---
phase: 08-literature-scoping-prerequisites
plan: 04
subsystem: testing
tags: [perceval, photonics, quantum-optics, phase-shifter, interferometry, pytest]

# Dependency graph
requires:
  - phase: 08-literature-scoping-prerequisites (plan 02)
    provides: perceval_fluency_demo.py's existing BS.H() single-photon-split and Hong-Ou-Mandel examples, Processor+Analyzer pattern
provides:
  - A third worked example in perceval_fluency_demo.py exercising pcvl.PS (phase shifter) inside a BS-PS-BS Mach-Zehnder construction
  - Closed-form, programmatically-verified proof that PS's phase angle predictably drives interference-based output changes
  - Full closure of PREQ-01 and ROADMAP.md Phase 8 success criterion 4 (all five named Perceval primitives now genuinely exercised)
affects: [09-encoding-design]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Mach-Zehnder interferometer pattern: BS.H() -> PS(theta) -> BS.H() on a 2-mode Circuit, single-photon input, closed-form check via cos^2(theta/2)/sin^2(theta/2)"

key-files:
  created: []
  modified:
    - perceval_fluency_demo.py
    - tests/test_perceval_fluency_demo.py

key-decisions:
  - "Followed 08-VERIFICATION.md's recommended remediation exactly: added a third PS-driven example rather than an owner waiver, since PS is explicitly named in both 08-CONTEXT.md's locked scope and ROADMAP.md's Phase 8 success criterion 4."
  - "Chose a BS-PS-BS Mach-Zehnder construction (not a bare PS) because a bare phase shifter's angle is invisible to Fock-basis photon-number measurement without an interferometer to convert phase into amplitude — the MZI form is the version that actually demonstrates why PS matters."

patterns-established:
  - "Closed-form interference check pattern for future Perceval demos: derive amplitudes algebraically from real Hadamard-BS matrices and a bare e^{i*theta} phase term, then assert np.isclose per output state across a small theta sweep (0, pi/2, pi) covering fully-constructive/50-50/fully-flipped cases."

# Metrics
duration: ~15min
completed: 2026-08-04
---

# Phase 8 Plan 04: PS Fluency Gap Closure Summary

**Added a BS.H()->PS(theta)->BS.H() Mach-Zehnder example to perceval_fluency_demo.py, closing PREQ-01's only outstanding gap by giving `pcvl.PS` a genuine, closed-form-verified role in the demo.**

## Performance

- **Duration:** ~15 min
- **Completed:** 2026-08-04T16:42:00Z
- **Tasks:** 1
- **Files modified:** 2

## Accomplishments
- `perceval_fluency_demo.py` now instantiates and wires `pcvl.PS(theta)` into an actual circuit (`build_mzi_circuit`), not just naming it in a comment.
- The MZI construction's output distribution is checked against the closed-form prediction `P(|1,0>) = cos^2(theta/2)`, `P(|0,1>) = sin^2(theta/2)` across `theta in {0, pi/2, pi}` — fully constructive, 50/50, and fully-flipped cases — all asserted programmatically via `np.isclose`, not eyeballed.
- `tests/test_perceval_fluency_demo.py` gained a parametrized `test_mzi_interference` test covering the same three theta values.
- Module docstring updated with the full amplitude derivation (two `BS.H()` Hadamard matrices sandwiching a bare phase `e^{i*theta}` on mode 0) so the closed-form facts are documented alongside the existing single-photon-split and HOM-dip derivations.
- `perceval_fluency_demo.py` runs to completion printing PASS for all 5 closed-form checks (single-photon split, HOM dip, and 3 MZI theta values); `pytest tests/test_perceval_fluency_demo.py` passes 6/6 tests.

## Task Commits

Each task was committed atomically:

1. **Task 1: Add a BS-PS-BS Mach-Zehnder example exercising PS, with a closed-form interference check** - `3dfde7b` (feat)

_Note: single-task plan, no TDD phases used (boilerplate/API-lookup work per this repo's CLAUDE.md offload rules, not a new conceptual decision)._

## Files Created/Modified
- `perceval_fluency_demo.py` - Added `build_mzi_circuit(theta)`, `run_mzi_analyzer(theta)`, `check_mzi(dist, theta)`; wired a theta sweep `[0, pi/2, pi]` into `main()` with PASS/FAIL reporting; extended the module docstring with the MZI amplitude derivation
- `tests/test_perceval_fluency_demo.py` - Added parametrized `test_mzi_interference` covering the three theta values; imported the new functions and `numpy`

## Decisions Made
- Followed 08-VERIFICATION.md's suggested remediation path (add the missing PS example) rather than seeking an owner waiver, since PS is explicitly named as a required primitive in both 08-CONTEXT.md's locked scope and ROADMAP.md's Phase 8 success criterion 4 — this is boilerplate/API-lookup work per this repo's CLAUDE.md, not a design decision requiring the owner's judgment.
- Used a Mach-Zehnder (BS-PS-BS) construction rather than a bare-PS example, because a bare phase shifter's angle has no effect on Fock-basis photon-number measurement without a second beamsplitter to convert the phase difference into an observable amplitude/probability change — the MZI form is what actually demonstrates PS's role, and is directly relevant groundwork for Phase 9's phase-driven interference reasoning.

## Deviations from Plan

**1. [N/A — pre-resolved by orchestrator] Dead `phase_shift()` helper removal step was a no-op**
- The plan's Task 1 action instructed removing a "dead `phase_shift(circuit, angle)` helper (lines ~56-59)." This function did not exist in the current file — confirmed by both the orchestrator and the plan-checker before execution began, per explicit instruction in this execution's context. It was a stale reference to a local edit already discarded before the plan was checked in. No removal action was needed or taken; not counted as a deviation requiring a rule-based fix, since it was pre-flagged rather than discovered during execution.

No other deviations — plan executed exactly as written.

## Issues Encountered
None. The demo ran and passed on the first attempt (using the project's `venv/Scripts/python.exe` with `PYTHONIOENCODING=utf-8`, consistent with the Windows gotcha already documented from plan 08-02).

## User Setup Required
None — no external service configuration required.

## Next Phase Readiness

PREQ-01 and ROADMAP.md's Phase 8 success criterion 4 are now fully satisfied: `perceval_fluency_demo.py` exercises all five named primitives (`Circuit`, `PS`, `BS`, `BasicState`, `Analyzer`) directly, without `QuantumLayer.simple()`, with every example — including the new PS-driven interference example — verified against a closed-form prediction programmatically. This closes the single gap `08-VERIFICATION.md` identified (score 9/10 -> 10/10 on this criterion). Phase 8 is now fully verified with no outstanding gaps. Phase 9 (Encoding Design) remains unblocked by the earlier LIT-04 Go verdict and can proceed; the MZI phase-driven interference pattern established here (`build_mzi_circuit`, closed-form derivation in the docstring) is directly reusable groundwork for Phase 9's encoding design work, which will need to reason about phase-driven interference in a less trivial circuit.

`.planning/REQUIREMENTS.md`'s stale unchecked checkboxes and `.planning/ROADMAP.md`'s stale "0/3, Planned" progress row for Phase 8 (both flagged as documentation-currency-only gaps in `08-VERIFICATION.md`, not functional gaps) remain open bookkeeping items outside this plan's scope — noted for whoever next touches those two files.

---
*Phase: 08-literature-scoping-prerequisites*
*Completed: 2026-08-04*
