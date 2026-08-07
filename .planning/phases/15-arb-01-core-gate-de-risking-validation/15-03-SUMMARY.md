---
phase: 15-arb-01-core-gate-de-risking-validation
plan: 03
subsystem: quantum-encoding
tags: [operator-identity, cp-gate, success-probability, dilation, arXiv-2405.01395, docs]

# Dependency graph
requires:
  - phase: 15-01
    provides: "CP(alpha)'s bare-gate phase/structure confirmed at 3 non-trivial alpha plus the alpha=pi boundary (cp_gate_derisking.py) -- the measured sweep this plan's closed-form derivation is checked against"
provides:
  - "General-alpha operator identity: exp(i*theta*Z_i*Z_j) = e^{-i*theta} * CP(4*theta) * exp(i*theta*Z_i) * exp(i*theta*Z_j), extending Ingredient 2's fixed-pi/4 derivation"
  - "Corrected alpha=4*theta relationship (15-CONTEXT.md originally stated alpha=pi/4 at the CZ boundary; verified value is alpha=pi)"
  - "Closed-form success probability p_success(alpha) = 1/sigma_max^(2n), sourced from arXiv:2405.01395 Section V-B, verified against cp_gate_derisking.py's measured sweep at 7 points to ~1e-7"
  - "Comparison table against heralded_cz (mechanism, tunability, success probability at the shared boundary)"
affects: [15-04-full-cp-insertion-pipeline-tvd-validation, 16-arb-01-extended-validation-postselection-bookkeeping]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "When a hand-derivation of a closed-form physical quantity is checked numerically and found wrong, consult the primary literature the gate implementation itself cites rather than keep re-deriving from a possibly-mismapped structure -- verify the literature formula against already-measured data before accepting it."

key-files:
  created: []
  modified:
    - docs/iqp-photonic-encoding.md

key-decisions:
  - "Checkpoint (autonomous: false) satisfied via Socratic-method attempt-first dialogue for both parts (a) and (b), per this repo's CLAUDE.md attempt-first gating -- owner derived the operator identity by hand (catching a real eigenvalue-vs-exponential error and an arithmetic slip along the way) and correctly identified the general dilation/entanglement-with-environment mechanism for part (b) before any closed form was written down."
  - "Part (b)'s exact closed-form derivation deviated from a pure hand-derivation: a first attempt (assuming block-diagonal-by-qubit-pair structure) was checked numerically against the gate's own measured amplitudes and was wrong (all 4 computational-basis inputs showed identical non-monotonic alpha-dependence, contradicting the wrong assumption's prediction). Resolved by consulting arXiv:2405.01395 Section V-B directly (the paper PostProcessedControlledRotationsItem's own docstring cites) rather than continuing to guess -- same verify-before-asserting discipline established earlier this session for the Perceval GitHub issue correction."

patterns-established:
  - "For a closed-form physical/mathematical claim about a third-party gate implementation: verify any hand-derivation numerically against the gate's own measured data before writing it into docs; if a hand-derivation is wrong, prefer the primary literature the implementation cites over further guessing."

# Metrics
duration: ~45min (Socratic dialogue + literature verification + doc write-up)
completed: 2026-08-07
---

# Phase 15 Plan 03: ARB-02 General-Alpha Operator Identity Summary

**`docs/iqp-photonic-encoding.md` extended with a new ARB-01/ARB-02 section: the general-alpha operator identity connecting `CP(alpha)` to `exp(i*theta*Z_i*Z_j)` for arbitrary theta (`alpha=4*theta`, correcting `15-CONTEXT.md`'s originally-stated `alpha=pi/4` boundary to the verified `alpha=pi`), and a closed-form success-probability formula (`p_success(alpha) = 1/sigma_max^(2n)`, sourced from arXiv:2405.01395) verified against `cp_gate_derisking.py`'s measured sweep at 7 points to ~1e-7 -- both derived via attempt-first Socratic dialogue with the owner, not handed over directly.**

## Performance

- **Duration:** ~45 min
- **Started:** 2026-08-07 (checkpoint task)
- **Completed:** 2026-08-07
- **Tasks:** 2/2 completed (Task 1: attempt-first checkpoint; Task 2: doc write-up)
- **Files modified:** 1

## Accomplishments
- General-alpha operator identity derived: `exp(i*theta*Z_i*Z_j) = e^{-i*theta} * CP(4*theta) * exp(i*theta*Z_i) * exp(i*theta*Z_j)` (up to global phase), extending Ingredient 2's existing fixed-pi/4 derivation without replacing it.
- `alpha=4*theta` relationship stated explicitly and checked against the confirmed boundary (`theta=pi/4 -> alpha=pi`, matching Plans 15-01/15-02's independently-confirmed result) -- corrects `15-CONTEXT.md`'s original `alpha=pi/4` note.
- Closed-form success probability `p_success(alpha) = (1/sigma_max)^(2n)` derived from arXiv:2405.01395 Section V-B, specialized to n=2 (`sigma_max = max(|1+a|, |1-a|)`, `a=(e^{i*alpha}-1)^{1/2}`), verified against `cp_gate_derisking.py`'s measured `|amplitude|^2` table at 7 points (the original 4-point sweep plus 3 additional exploratory points), all agreeing to ~1e-7.
- Physical interpretation tied explicitly to the owner's own dilation/entanglement-with-environment answer: `sigma_max` deviating from 1 is the target operation's "excess gain" that leaks into non-vacuum-ancilla branches; success probability is `(1/sigma_max^2)^n` since each of the n photons independently pays this per-particle cost.
- Comparison table against `heralded_cz` added (mechanism: heralding vs. post-selection; tunability: fixed vs. continuous; success probability at the shared boundary: 2/27 vs. 1/9 -- genuinely different numbers for genuinely different gate families, never conflated).
- Stale "ARB-01, deferred" line in the document's Conclusion section corrected to reflect the now-resolved arbitrary-theta case (full-pipeline TVD validation at arbitrary alpha remains Plan 15-04's job, stated explicitly as still open).

## Task Commits

1. **Task 1: Attempt-first checkpoint (Socratic-method derivation of parts a and b)** — conversational, no code commit (checkpoint gate, not an implementation task).
2. **Task 2: Write general-alpha operator identity + success probability into docs/iqp-photonic-encoding.md** — `82b3619` (docs)

## Files Created/Modified
- `docs/iqp-photonic-encoding.md` — New `## ARB-01/ARB-02: General-α Operator Identity and Success Probability` section (Owner's Attempt, General-α Operator Identity, Closed-Form Success Probability with verification table, Comparison Against `heralded_cz`); Contents list updated; one stale line in the Conclusion section corrected.

## Decisions Made
- **Part (a) closed form derived entirely by the owner**, via incremental Socratic questions (eigenvalues → exponential → single-qubit correction structure → global-phase degree of freedom → solving for φ and α), with two real errors caught along the way (eigenvalue-vs-exponential confusion; an `α=1` arithmetic slip) rather than accepted uncorrected.
- **Part (b) closed form required primary-literature verification, not pure derivation.** A first hand-derivation attempt (assuming the gate's coupling matrix was block-diagonal by qubit pair) was checked numerically against the gate's own measured amplitudes and disproven (all 4 computational-basis inputs showed identical behavior, contradicting the wrong assumption). Rather than continue re-deriving from a mismapped structure, `arXiv:2405.01395` (the paper `PostProcessedControlledRotationsItem`'s own docstring cites) was consulted directly via `WebFetch`, and the resulting formula verified against `cp_gate_derisking.py`'s measured sweep before being written into the doc — same verify-before-asserting discipline this session already established for the Perceval GitHub issue correction (see `~/.claude/learnings/2026-08-07-verify-before-filing-external-bug-reports.md`).
- **Doc structure:** new content added as a standalone `## ARB-01/ARB-02` section (matching the existing `## ENC-XX` numbering pattern) placed after `ENC-05` and before `Conclusion and Open Questions`, rather than folding into Ingredient 2 — keeps the fixed-pi/4 derivation intact and unreplaced, per the plan's explicit "ALONGSIDE, not replacing" requirement.

## Deviations from Plan

- Part (b)'s derivation path deviated from a pure hand-derivation to include a primary-literature check (`WebFetch` against arXiv:2405.01395) after a first hand-derivation attempt was numerically disproven. This is a stronger verification standard than the plan anticipated, not a shortcut — the alternative (continuing to guess at the internal matrix structure) was explicitly rejected given this session's established precedent for a wrong-but-confident technical claim.

## Issues Encountered

None blocking. The first attempt at part (b)'s closed form was wrong (see Decisions Made above) — caught by numerical verification before it reached the document, not after.

## User Setup Required

None — no external service configuration required.

## Next Phase Readiness

- ARB-02's general-alpha operator identity and closed-form success probability are both derived, documented, and verified against measured data — Plan 15-04 (full CP-insertion pipeline + TVD validation at arbitrary alpha) can proceed with a settled theoretical reference to validate the implementation against.
- No blockers identified for Plan 15-04.

---
*Phase: 15-arb-01-core-gate-de-risking-validation*
*Completed: 2026-08-07*
