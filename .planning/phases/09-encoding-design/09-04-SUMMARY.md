---
phase: 09-encoding-design
plan: 04
subsystem: docs
tags: [perceval, photonics, polarization, iqp, encoding, douce-et-al, documentation]

# Dependency graph
requires:
  - phase: 09-encoding-design (plans 09-01, 09-02, 09-03)
    provides: ENC-01 ingredient mapping, ENC-03 basis correspondence, ENC-04 toy validation
provides:
  - ENC-02 positioning against Douce et al. (docs/iqp-photonic-encoding.md)
  - Fully assembled docs/iqp-photonic-encoding.md (intro, ENC-01 through ENC-04, Conclusion and Open Questions)
  - Phase 9 marked complete in REQUIREMENTS.md and ROADMAP.md
  - v2.0 milestone (Phases 8-9) complete
affects: []

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Hedged-tone positioning sections state both the favorable contrast (native single-qubit conjugation) and the honest parallel (probabilistic multi-qubit gate, same character as the CV precedent's gadget) rather than only the flattering half"
    - "A document-level Conclusion section collecting every limitation stated piecemeal across earlier sections gives a reader one place to see the full honesty ledger, rather than requiring them to hunt through the document"

key-files:
  created: []
  modified:
    - docs/iqp-photonic-encoding.md
    - .planning/REQUIREMENTS.md
    - .planning/ROADMAP.md

key-decisions:
  - "ENC-02 states the honest parallel (weight-2's heralded_cz is measurement-conditioned, same character as Douce et al.'s post-selected Fourier gadget) as prominently as the favorable contrast (native single-qubit HWP conjugation vs. Douce's gadget-only realization) -- per 09-CONTEXT.md's tone constraint and 09-RESEARCH.md's Pitfall 3 warning against claiming DV avoids the measurement-based-realization problem entirely"
  - "REQUIREMENTS.md's ENC-01 through ENC-04 checkboxes marked complete as part of Task 2's mechanical update (per the plan's literal instructions), with ENC-05 marked complete but annotated 'pending final self-explanation checkpoint' until Task 3 actually closed"

patterns-established:
  - "Final whole-document self-explanation checkpoints (ENC-05's bar) get the same full-transcript documentation treatment as earlier per-section checkpoints -- multiple correction rounds recorded, not smoothed into a single clean pass"

# Metrics
duration: ~1hr (implementation) + ~45min (final checkpoint, multiple correction rounds)
completed: 2026-08-05
---

# Phase 9 Plan 04: ENC-02 Positioning, Final Assembly, Phase Completion Summary

**ENC-02 positions the mapping against Douce et al. (2017) with an explicit favorable contrast (native, deterministic single-qubit Hadamard-conjugation) and an equally explicit honest parallel (the weight-2 `heralded_cz` construction is measurement-conditioned, the same character as Douce et al.'s post-selected Fourier gadget). `docs/iqp-photonic-encoding.md` is now one coherent document (intro → ENC-01 → ENC-02 → ENC-03 → ENC-04 → Conclusion). Phase 9 and the v2.0 milestone are complete.**

## Performance

- **Duration:** ~1 hour implementation (ENC-02 + assembly + paperwork, not attempt-first gated) + ~45 minutes for the final self-explanation checkpoint, which required five correction rounds
- **Completed:** 2026-08-05
- **Tasks:** 3 (Task 1: write ENC-02; Task 2: final assembly + paperwork; Task 3: final self-explanation checkpoint)
- **Files modified:** 3 (`docs/iqp-photonic-encoding.md`, `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md`)

## Task 1: ENC-02

Positions the mapping against Douce et al. (2017) under `09-CONTEXT.md`'s explicit hedged-tone constraint. States what Douce et al. established (CV/quadrature hardness construction, Fourier-gadget conjugation via post-selected teleportation), how this DV/Fock-space mapping differs (different formalism entirely, native `HWP(π/8)` single-qubit conjugation vs. Douce's gadget-only realization), and — the section's most important honesty check — where the parallel holds rather than breaks: the weight-2 `heralded_cz` construction is itself measurement-conditioned, inheriting a version of the same "not a native unitary, realized via measurement, succeeds only some of the time" character as Douce et al.'s own gadget. Explicitly states this document is a design/mapping exercise, not a complexity-theoretic reduction proof, matching `REQUIREMENTS.md`'s Out-of-Scope exclusion.

## Task 2: Final Assembly and Paperwork

Reassembled `docs/iqp-photonic-encoding.md` into one coherent document: expanded intro (scope statement, prerequisite reading pointers to `docs/iqp-baseline.md` and `docs/iqp-lit-scoping.md`, how-to-read guidance), working table of contents, ENC-01 → ENC-02 → ENC-03 → ENC-04 reading order (ENC-02 moved from its temporary end-of-file position), and a new `## Conclusion and Open Questions` section collecting every limitation stated piecemeal across the four ENC- sections into one honesty ledger (generator-weight scope, unverified `heralded_cz` success probability, toy-check scope, general-`n` scaling not demonstrated).

Updated `.planning/REQUIREMENTS.md` (ENC-01 through ENC-05 marked complete with one-line notes each) and `.planning/ROADMAP.md` (Phase 9: 4/4 plans, complete; v2.0 milestone complete).

**Verification:** `pytest tests/ -v` — 85/85 passed, no regressions from this phase's additions.

## Task 3: Final Self-Explanation Checkpoint

The whole-document checkpoint (ENC-05's bar: explain the entire mapping unaided, as if to Vincent Espitalier) required five correction rounds across all five required points:

1. **Scheme choice** — correct on first attempt.
2. **Commutativity** — initially gave only the disjoint-qubit half (different qubits' 1-mode gates can't touch each other); missing the same-qubit half (two diagonal gates on the same qubit commute because diagonal matrices commute, regardless of order) until prompted. Also conflated Hadamard-conjugation's actual mechanism (phase → visible population difference) with ENC-03's round-trip falsifiability check (forward-map → readout → reverse-map recovers the original bitstring) — a mix-up between two genuinely different, both-real mechanisms in the document; corrected.
3. **Basis correspondence** — repeated the round-trip *property* twice instead of stating the actual forward/reverse *rules* (bit↔polarization, port-pattern↔bit) before finally stating them correctly. Along the way, got the port↔polarization assignment backwards (`(1,0)→H`, `(0,1)→V` — the exact reverse of Wave 2's verified, previously-corrected convention) and had to be walked back to the calibration data before restating it correctly. Also initially named only 2 of the 4 invalid patterns (lost, bunched) before completing the set with `(1,1)` (extra photon, one per mode, distinct from bunching).
4. **n=2-3 result** — correct on the confirmation half from the first attempt, but initially dropped the scope caveat (which generator weight, and silence on weight-2) that had already been established correctly in Plan 09-03's checkpoint; restated with the caveat after a prompt.
5. **Douce et al. positioning** — initial "I'm not sure," rebuilt via direct re-teaching (native single-qubit conjugation as the favorable contrast; weight-2's `heralded_cz` as the honest parallel to Douce's measurement-based gadget), then correctly restated in the owner's own words.

Full record of both the wrong answers and the corrections lives in this conversation; per this repo's established pattern, the notable checkpoint transcripts within the document itself (ENC-01/03/04's Self-Explanation sections) already capture the per-section versions of this same practice.

## Phase 9 and v2.0 Milestone: Complete

All four plans executed, all `must_haves` verified, full test suite green (85/85), `docs/iqp-photonic-encoding.md` assembled as one coherent, defensible document. ENC-01 through ENC-05 marked complete in `REQUIREMENTS.md`. Phase 9 marked complete in `ROADMAP.md`; this closes the v2.0 `IQP → Photonic Encoding` milestone (Phases 8-9).

## Deviations

None from the plan's task structure. The final checkpoint (Task 3) required substantially more correction rounds than a typical per-section checkpoint, consistent with it re-testing the *entire* document's content in one pass rather than one section's worth.
