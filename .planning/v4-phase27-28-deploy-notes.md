# Phase 27–28 deployment notes

## Delivered additive slice

- src/merlin_iqp/deploy/compile.py: finite weight-1/2 compiler, negative PS signs, circular alpha keys, preserved winding, topology/weight rejection.
- src/merlin_iqp/deploy/maps.py: ideal CP/single instruments, 16x9 tomography reconstruction, physicality checks, success-weighted Haar fidelity, stale-key cache guard.
- src/merlin_iqp/deploy/density.py: local density-block composition with one final normalization; no embedded 4^n x 4^n superoperator.
- src/merlin_iqp/deploy/fock.py: optional n=2/3 single-CP full-Fock adapter with source-once/projection diagnostics and explicit D1 inconclusive status for g2/loss.
- src/merlin_iqp/deploy/throughput.py and erasure.py: fixed-photon and heralded-CZ controls plus conditional synthetic erasure with FAILURE mass.
- scripts/v4_tcdp/validate_deploy.py: bounded validation smoke and manifest writer.

## Evidence

Focused deployment tests: 75 passed. The default smoke reports the actual optional Perceval probe status in results/v4_tcdp/deploy/validation_manifest.json.

## Boundaries

The code does not claim D1: no joint g2/loss source model, general multi-gate full-Fock agreement, or unconditional non-post-selected output. The optional full-Fock adapter refuses those settings as INCONCLUSIVE. The classical/rings/sibling files in the shared checkout are outside this slice and were preserved.
