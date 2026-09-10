# Photonic source and bit-order validation
Date: 2026-09-07 · Scope: project · Recurs when: a direct full-Fock photonic adapter disagrees with an independent logical reference.

## Context & constraints
- The existing dual-rail convention is `(0,1) = 0`; output relabeling is not an allowed repair.
- The control is fixed-photon `g2=0`, source-once, with final logical projection.
- The direct backend and analytic CP map are different mechanisms and must be compared independently.

## Approach
1. Test the smallest no-gate, zero-angle case before inspecting gate behavior.
2. Trace the source preparation and readout maps separately through the backend's beam-splitter convention.
3. Add an independent identity and bit-order fixture; repair only a concrete local state-preparation error.
4. Rerun no-gate, single-gate+bystander, and shared-gate controls and compare conditional distributions with TVD.
5. Keep the aggregate result failed when any gate control remains mismatched; do not relabel outputs.

## Decision rules that generalize
- IF zero-angle no-gate output violates the documented encoding, THEN inspect source preparation before changing the decoder.
- IF a backend transformation maps the documented `(0,1)` source to physical `(1,0)`, THEN start the direct source in `(1,0)` while retaining the documented decoder.
- IF no-gate identity passes but gate controls retain material TVD, THEN classify the construction as FAIL and investigate CP wiring/phase conventions.
- IF the mismatch is a source/readout convention choice rather than a local bug, THEN preserve the result and record the exact evidence needed for the owner decision.

## Mistakes avoided / dead ends
- Treating direct `11` as equivalent to logical `00` would have silently relabeled the existing encoding.
- Passing the no-gate identity does not validate the CP-gate construction.

## Verification
- The independent no-gate fixture passes with TVD `6.418476861114186e-17`.
- The single-gate+bystander and shared-gate controls remain FAIL with TVDs `0.60070872508387` and `0.5541109141490421`.
- The three-control manifest records fixed-photon `g2=0`, source-once, raw acceptance, absolute accepted mass, and provenance.

## Next time (for a weaker model)
- Do: establish identity, source state, decoder, and backend ordering in a one-qubit fixture first.
- Don't: change D1/D2/D3 or claim ring deployment to make a physical mismatch disappear.

## Addendum: intermediate projection accounting
- IF a diagnostic filters amplitudes after each successful instrument, THEN retain the squared norm relative to the original source norm; do not normalize the surviving branch before reporting absolute acceptance.
- IF final-only and intermediate runs use the same eta, THEN compare conditional distributions separately from eta-scaled accepted mass.

## Changed files
- `src/merlin_iqp/deploy/fock.py` — corrected the direct source state and added full-Fock controls.
- `tests/v4_tcdp/test_deploy.py` — added independent no-gate identity and bit-order fixtures.
- `scripts/v4_tcdp/validate_physical_controls.py` — records final/intermediate projection and eta-consistency evidence.

## Addendum: frozen ring loading
- IF a loader builds a logical path map for `manifest`, `run`, and `dataset`, THEN use those logical keys consistently rather than mixing them with filename keys such as `run.npz`.
- IF a frozen ring is evaluated physically, THEN verify array hashes, codec/config/source metadata, and n=4 smoke scope before compiling or simulating.
