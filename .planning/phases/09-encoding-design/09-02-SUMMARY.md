---
phase: 09-encoding-design
plan: 02
subsystem: docs+testing
tags: [perceval, photonics, polarization, iqp, encoding, fock-space, basis-correspondence]

# Dependency graph
requires:
  - phase: 09-encoding-design (plan 09-01)
    provides: ENC-01 ingredient-level mapping, iqp_photonic_encoding.py's state-prep/diagonal-layer/conjugation/readout circuit builders
provides:
  - ENC-03 basis correspondence (docs/iqp-photonic-encoding.md), bidirectional and falsifiable
  - iqp_photonic_encoding.py's bitstring_to_fock (forward), fock_to_bitstring (reverse), run_readout helper
  - Fix to Wave 1's H/V port-labeling bug (basic_state_to_bitstring, expected_single_qubit_probs, and ENC-01's derivation text were self-consistent but physically backwards)
affects: [09-03-encoding-design, 09-04-encoding-design]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Verified port<->polarization convention via a bare PBS with no other gates and pure H/V input, rather than inferring it from a sandwiched multi-gate circuit -- isolates the one fact being checked from everything else in the pipeline"
    - "Round-trip test (forward map -> physical circuit -> reverse map -> compare to original) is both the falsifiability statement and the mechanism that actually caught the H/V labeling bug -- a concrete example of 'checkable claim' vs. 'plausible-sounding analogy'"
    - "Out-of-subspace outcomes reported as an explicit residual percentage, never silently discarded/renormalized -- preserves a fair comparison basis for ENC-04's distribution comparison against the qubit-side reference (which has no invalid outcomes to begin with)"

key-files:
  created: []
  modified:
    - docs/iqp-photonic-encoding.md
    - iqp_photonic_encoding.py
    - tests/test_iqp_photonic_encoding.py

key-decisions:
  - "Corrected H/V port convention (verified: H=(0,1), V=(1,0) via bare PBS calibration) applied retroactively to Wave 1's basic_state_to_bitstring and expected_single_qubit_probs, not just ENC-03's new functions -- owner explicitly requested this for consistency even though it didn't change any Wave 1 test's pass/fail result"
  - "Out-of-subspace policy: report residual probability explicitly rather than discard-and-renormalize (owner's choice, confirmed at the Task 3 checkpoint by reasoning through what silent renormalization would hide from ENC-04's distribution comparison)"
  - "fock_to_bitstring implemented as a thin wrapper over the (now-corrected) basic_state_to_bitstring, translating H/V labels to 0/1 bits, rather than duplicating the pair-validation logic"

patterns-established:
  - "Historical checkpoint transcripts (ENC-01's Self-Explanation Checkpoint section) were left unedited when a later plan corrected an underlying convention they referenced -- an editorial note was added pointing to the correction instead of rewriting the quotes, preserving an accurate record of what was actually said at the time"

# Metrics
duration: ~1.5hr (interactive, across multiple guided-question rounds)
completed: 2026-08-05
---

# Phase 9 Plan 02: ENC-03 Basis Correspondence Summary

**Bidirectional, falsifiable bitstring<->Fock-state correspondence for polarization encoding: `bitstring_to_fock` (forward), `fock_to_bitstring` (reverse, `None` for any of four out-of-subspace patterns). A direct calibration check (bare `PBS`, pure H/V input) caught and fixed a real port-labeling bug carried over from Wave 1.**

## Performance

- **Duration:** ~1.5 hours, interactive (Task 1's attempt-first checkpoint required breaking all three questions into smaller guided sub-questions after the owner said they weren't sure how to answer; Task 3's checkpoint required one round of pushing past a plan-quote back to the owner's own reasoning)
- **Completed:** 2026-08-05
- **Tasks:** 3 (Task 1: attempt-first checkpoint; Task 2: implementation; Task 3: self-explanation checkpoint)
- **Files modified:** 3 (`docs/iqp-photonic-encoding.md`, `iqp_photonic_encoding.py`, `tests/test_iqp_photonic_encoding.py`)

## Task 1: Attempt-First Checkpoint

Owner initially could not answer any of the three sub-questions (reverse map, out-of-subspace case, falsifiability) unprompted. Each was broken into a smaller, more concrete guided question:
- **Reverse map:** owner correctly identified `(0,1)=H`, `(1,0)=V` — checked directly (not assumed) via a bare `PBS()` with pure H/V input, which **caught a real bug**: Wave 1's `basic_state_to_bitstring`/`expected_single_qubit_probs` had this backwards (self-consistent, so no Wave 1 test result was ever wrong, but the human-readable labels didn't match true physical polarization). Fixed across the module, tests, and ENC-01's derivation text at the owner's explicit request, for consistency.
- **Out-of-subspace case:** owner correctly named the disqualifying criterion (total photon count ≠ 1) and the reporting policy (residual percentage, not silent discard), but initially missed two of the four invalid patterns (the bunched `(2,0)`/`(0,2)` cases). Explained via a Feynman-style "one coin, two boxes" analogy after the owner explicitly requested it.
- **Falsifiability:** owner correctly identified the round-trip property and connected it to unitarity/reversibility.

## Task 2: Implementation

Added to `iqp_photonic_encoding.py`: `bitstring_to_fock(bitstring, n)` (forward: `'0'→H`, `'1'→V`), `run_readout(n, input_state)` (runs a state through the `PBS`-only readout circuit), `fock_to_bitstring(basic_state, n)` (reverse, wraps the corrected `basic_state_to_bitstring`, returns `None` for any of the four out-of-subspace patterns). `docs/iqp-photonic-encoding.md`'s new `## ENC-03` section documents the full attempt-first Q&A, states the forward/reverse maps, the reporting policy, and the falsifiability claim, with a worked code example.

**Verification:** `pytest tests/test_iqp_photonic_encoding.py -v` — 24/24 passed (12 from Wave 1 plus 12 new: 7 round-trip cases across `n=1-3`, 4 individual out-of-subspace patterns, 1 out-of-subspace-embedded-in-a-larger-register case). `python -c "import iqp_photonic_encoding"` — clean.

## Task 3: Self-Explanation Checkpoint

First-round answer to "why is the out-of-subspace policy right for ENC-04" quoted the plan's own wording rather than reasoning through it; pushed back, and the owner's second answer ("discarding and rescaling would hide how often the mapping fails") was correct and their own. "Why falsifiable, not an analogy" initially drew "I'm not sure what you are asking" — clarified with a non-photonics example (key/lock vs. password/login) before the owner correctly named the round-trip property as the concrete, already-tested claim.

## Deviations

None from the plan's task structure. Task 1 required more scaffolding than Plan 09-01's equivalent checkpoint (all three sub-questions needed to be broken down further before the owner could attempt them), and Task 2 grew slightly beyond the plan's stated scope to include fixing Wave 1's pre-existing labeling bug (owner-requested, in scope per this repo's deviation rules — a correctness fix, not a new feature).
