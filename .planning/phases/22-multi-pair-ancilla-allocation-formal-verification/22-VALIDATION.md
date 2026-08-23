---
phase: 22
slug: multi-pair-ancilla-allocation-formal-verification
status: validated-partial
nyquist_compliant: false
wave_0_complete: true
created: 2026-08-20
validated: 2026-08-23
---

# Phase 22 — Validation Strategy

Phase 22 is a verification-only Forge/Python phase. It deliberately stays outside `pytest`: the Forge model is executed by Racket and the baseline is a standalone colouring-search script.

## Test Infrastructure

| Property | Value |
|----------|-------|
| Framework | Forge 5.2 via Racket; standalone Python baseline |
| Quick run | `racket forge/pooled_ancilla_allocation.frg` |
| Baseline | `venv/Scripts/python.exe pooled_allocation_baseline.py --skip-naive --time-ceiling 600` |
| Regression evidence | Phase 23 verification records `venv/Scripts/python.exe -m pytest -q` → 296 passed; not rerun in this validation pass |
| Scope boundary | The optional naive `2^C(n,2)` subset scan is secondary and skipped; MPAIR-05's required comparison is the pairwise-reduced colouring search |

## Requirement-to-validation map

| Requirement | Evidence | Status |
|-------------|----------|--------|
| MPAIR-01 | `22-CONTEXT.md` D-02 and `22-DISCUSSION-LOG.md` record the owner's selection of pooled/recycled and rejection of alternatives | Manual-only, satisfied |
| MPAIR-02 | `results/phase22_allocation_invariant.md`; owner review and pairwise-reduction scope recorded | Manual-only, satisfied |
| MPAIR-03 | Forge `colouringExists`/`minimality` checks at n=4,5,6; `for 7 Int` bitwidth documented | Automated green + manual bitwidth review |
| MPAIR-04 | Forge `nonVacuousN4/N5/N6` checks passed | Automated green |
| MPAIR-05 | Python backtracking search exited 0; min K matched Forge at n=4,5,6 and reached n=7,8; timing/verdict interpretation remains human judgment | Automated green + manual interpretation |
| MPAIR-06 | `docs/iqp-photonic-encoding.md` specification section states no Python implementation exists and links the evidence | Automated link/content check, satisfied |
| MPAIR-07 | `results/phase22_reuse_gate.md` and owner ruling establish the physics gate before Forge modeling | Manual-only, satisfied |

## Live validation evidence — 2026-08-23

### Forge model

Command: `racket forge/pooled_ancilla_allocation.frg`
Result: exit 0. All 12 checks passed: `nonVacuous`, `colouringExists`, `minimality`, and `dataPortDisjoint` for n=4,5,6. The run completed within the phase's 600-second ceiling. The model's recorded bounded outcome remains n≤6; n=7 was previously documented as timing out at the phase ceiling.

### Python primary baseline

Command: `venv\Scripts\python.exe pooled_allocation_baseline.py --skip-naive --time-ceiling 600`
Result: exit 0. Backtracking found min K values 3, 5, 5, 7, 7 for n=4,5,6,7,8; it matched Forge at every shared n and reported no disagreements. The secondary subset enumeration was intentionally skipped because it is not the required MPAIR-05 comparison.

## Manual-only gates

| Gate | Requirement | Resolution |
|------|-------------|------------|
| Owner selected the allocation scheme | MPAIR-01 | Recorded in `22-CONTEXT.md` and discussion log |
| Prose invariant and pairwise reduction mean what the model claims | MPAIR-02 | Owner review recorded in phase artifacts |
| Deferred post-selection permits or forbids physical reuse | MPAIR-07 | Numeric reuse gate and owner GO ruling recorded before Forge model creation |
| Forge's contribution versus Python | MPAIR-05 | Human interpretation is recorded honestly: Python was faster and reached further; Forge contributed declarative modeling and bounded solver evidence |
| Bitwidth and bounded-model scope | MPAIR-03 | `for 7 Int` and n≤8 formula limits are documented; model convergence is n≤6 |

## Sign-off

- [x] MPAIR-07 physics gate resolved before the `.frg` model was written
- [x] Forge non-vacuity and colouring/minimality/data-port checks pass at n=4,5,6
- [x] Non-vacuity requires genuine pooled compatible pairs
- [x] Bitwidth is justified against the final formula
- [x] Baseline is a real greedy/backtracking search, not a fixed-colouring verification loop
- [ ] Full repository pytest regression rerun in this pass — prior verification evidence records 296 passed
- [x] Feedback latency stayed within the 600-second ceiling; bounded Forge outcome is recorded honestly
- [ ] `nyquist_compliant: true` — not claimed because MPAIR-01, MPAIR-02, MPAIR-07, and interpretation checkpoints are inherently manual

## Validation Audit 2026-08-23

| Metric | Count |
|--------|-------|
| Requirements mapped | 7 |
| Automated green | 4 |
| Manual-only/supplemented | 3 |
| New implementation tests | 0 |
| Blockers | 0 |

**Result:** Phase 22 is validated partially. The executable Forge and baseline evidence is green; remaining manual-only gates are explicit scope boundaries, not missing implementation tests.
