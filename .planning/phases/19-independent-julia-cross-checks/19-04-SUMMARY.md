---
phase: 19-independent-julia-cross-checks
plan: 04
subsystem: testing
tags: [cross-language-verification, bosonsampling-jl, knill-cz, heralded-gate, literature-sourcing, iqp-photonic-encoding]

# Dependency graph
requires:
  - phase: 19-independent-julia-cross-checks
    plan: 01
    provides: results/julia_reference/weight2_locked_n2.csv (Python reference distribution for the locked weight-2 gate, n=2, i=0, j=1, thetas=[0,0])
  - phase: 09-encoding-design
    provides: docs/iqp-photonic-encoding.md's Ingredient 2 operator identity (exp(i*pi/4*Zi*Zj) = CZ . exp(i*pi/4*Zi) . exp(i*pi/4*Zj)) and heralded_cz_derisking.py's independently-measured 2/27 herald-success/phase-sign facts
provides:
  - julia/verify_photonic_iqp_weight2.jl, an independently-sourced Knill-CZ BosonSampling.jl construction with a hand-herald weight-2 cross-check
  - results/phase19_verify03_weight2_results.md, VERIFY-03's weight-2 leg methodology + GO verdict
affects: [20, 21]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Literature-sourced gate matrix, verified via a standalone Eq-6-style zero-leak diagnostic before trusting it in a larger circuit -- catches convention mismatches (row/col transpose) that unitarity alone cannot detect"
    - "Composite multi-stage linear-optics circuit built as a single explicit Julia matrix product (state_prep * correction * gate * conjugation), then passed to ONE UserDefinedInterferometer call -- avoids depending on any BosonSampling.jl API surface beyond what Phase 14 already validated"

key-files:
  created:
    - julia/verify_photonic_iqp_weight2.jl
    - results/phase19_verify03_weight2_results.md
  modified: []

key-decisions:
  - "Sourced the Knill CZ gate's explicit 4x4 unitary directly from arXiv:quant-ph/0110144 Eq. 11 (Knill, 'A Note on Linear Optics Gates by Post-Selection', 2001) -- fetched both the PDF and the LaTeX e-print source (to eliminate OCR risk in the transcribed matrix) -- never from Perceval's own built heralded_cz circuit, satisfying 19-RESEARCH.md's explicitly-flagged anti-pattern."
  - "Found and fixed a real bug: the paper's own matrix, used exactly as printed, produced nonzero leakage into bunched outputs that Knill's own Eq. 6 guarantees should be exactly zero. Root cause: the paper defines its printed matrix via V_rs = u_sr (a transpose convention), differing from BosonSampling.jl's UserDefinedInterferometer(U) expected output-row/input-column orientation. Diagnosed via a standalone 4-mode zero-leak check (not by trial and error against the full pipeline), fixed by transposing the matrix. Documented as a runnable assertion in the script, not just prose."
  - "Chose to apply the weight-1 pi/4 phase correction AFTER the CZ gate in circuit order (conjugation . correction . cz_embed . state_prep) -- a design choice since both orders are physically equivalent at the logical-qubit level (Zi, Zj, CZ all commute as diagonal 2-qubit operators) but not obviously equivalent at the raw 6-mode matrix level. Worked on the first attempt post-transpose-fix, so the alternate order was never needed or tried."
  - "Built the full 6-mode circuit as ONE explicit Julia matrix product rather than chaining multiple BosonSampling.jl circuit-composition calls, deliberately staying within the single UserDefinedInterferometer(U::Matrix) pattern Phase 14 already validated end-to-end -- avoids introducing new, unverified BosonSampling.jl API surface for this already-highest-risk plan."

patterns-established:
  - "When sourcing a gate matrix from a paper for an independent cross-check, verify it against the paper's OWN stated zero/exact constraints (here: Eq. 6's four leak=0 identities) in a minimal standalone circuit BEFORE embedding it into a larger pipeline -- isolates convention bugs (transpose, sign, mode ordering) from downstream composition bugs immediately, rather than debugging a 6-mode circuit's TVD mismatch as one large search space."

# Metrics
duration: ~70min
completed: 2026-08-17
---

# Phase 19 Plan 04: Independent Knill-CZ BosonSampling.jl Cross-Check (VERIFY-03 weight-2 leg) Summary

**Sourced the Knill CZ gate's unitary directly from the original 2001 paper (arXiv:quant-ph/0110144, Eq. 11), built it independently in BosonSampling.jl, found and fixed a real transpose-convention bug via a standalone zero-leak diagnostic, and reproduced Python's locked weight-2 gate distribution to floating-point precision (TVD=3.5e-15) -- a full GO, not a partial-go.**

## Performance

- **Duration:** ~70 min
- **Tasks:** 2/2 (both completed -- literature sourcing succeeded within the time-box, so Task 2's full pipeline was attempted and completed)
- **Files modified:** 2 (1 Julia script, 1 results doc)

## Accomplishments
- Fetched and read arXiv:quant-ph/0110144 (both PDF and LaTeX e-print source, to eliminate OCR risk) and identified Eq. 11's explicit closed-form 4x4 real-orthogonal matrix `V_180` as the independent source for Knill's `CS_180°` (a heralded CZ gate, success probability 2/27) -- never extracted from Perceval's own `heralded_cz` circuit.
- Built the full n=2 locked weight-2 IQP circuit independently in BosonSampling.jl: a 6-mode dual-rail construction (state prep via a bare Hadamard, a pi/4 weight-1 correction realizing the CZ-to-ZZ operator identity already derived in `docs/iqp-photonic-encoding.md`, the Knill gate embedded on the logical-|1> rails + 2 ancillas, and conjugation), with herald post-selection done entirely by hand (enumerating all 10 herald-success data-mode patterns via `compute_probability!`).
- Found and fixed a real bug during Task 2: the paper's printed matrix, used as-is, leaked probability into bunched outputs that Knill's own Eq. 6 proves should be exactly zero. Diagnosed via a standalone 4-mode check against Eq. 6's four zero-constraints (not by guessing against the full pipeline) -- root cause was a row/column (input/output) transpose convention mismatch between the paper's `V_rs = u_sr` definition and `UserDefinedInterferometer`'s expected orientation. Fixing it (using `V^T`) dropped all four leak terms to numerical zero (~1e-32).
- Measured result: TVD = `3.497e-15` against `results/julia_reference/weight2_locked_n2.csv`, `herald_failure_prob` matching Python's `25/27` to `5.55e-16` -- both roughly ten orders of magnitude inside the locked `1e-6` tolerance. **GO verdict**, not a partial-go: the literature-sourcing time-box was not exhausted, and the full cross-check succeeded.

## Task Commits

Each task was committed atomically:

1. **Task 1+2 (combined): independent Knill-CZ BosonSampling.jl construction + cross-check** - `4879010` (feat)
2. **Results documentation** - `b762d3d` (docs)

_Tasks 1 and 2 were authored and debugged together as one script (literature sourcing succeeded within the time-box, so Task 2 was reached and completed in the same working session) and committed as a single feat commit, followed by a separate docs commit for the results file -- matching this plan's own two-artifact structure (script, results doc) rather than an artificial task-by-task split._

## Files Created/Modified
- `julia/verify_photonic_iqp_weight2.jl` - Independently-sourced Knill CZ construction (arXiv:quant-ph/0110144 Eq. 11), 6-mode dual-rail weight-2 IQP circuit, hand-herald post-selection, TVD/herald_failure_prob comparison against the Python reference CSV. Includes a runnable Task-1 diagnostic (unitarity + Eq. 6 zero-leak checks) documenting the transpose-convention fix.
- `results/phase19_verify03_weight2_results.md` - Full methodology (literature source, construction, the transpose bug found and fixed), measured GO verdict, and honesty/scope notes.

## Decisions Made
- **Literature source:** arXiv:quant-ph/0110144 Eq. 11 (Knill, 2001), fetched as both PDF and LaTeX source to eliminate transcription risk -- confirmed byte-for-byte against the LaTeX source before debugging began, which is what pointed the debugging effort at a convention issue rather than a transcription error.
- **Transpose fix:** documented as a runnable assertion in the script (not just prose) -- the standalone Eq.-6 zero-leak diagnostic re-verifies both the bug's absence and the fix's correctness on every run.
- **Correction-before-vs-after-CZ ordering:** applied after CZ; not re-tested with the alternate order since the first attempt (post-transpose-fix) succeeded. Documented as an untested-alternative design choice in the results doc, not asserted as proven-irrelevant.
- **No fallback to Perceval's matrix at any point** -- the anti-pattern flagged in 19-RESEARCH.md was avoided throughout, including during debugging (the fix was re-deriving the correct matrix orientation from the paper's own stated convention, not comparing against or borrowing from Perceval's circuit).

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] Knill matrix transpose convention mismatch**
- **Found during:** Task 2 (first full pipeline run, before comparing against the Python reference)
- **Issue:** Eq. 11's matrix, used exactly as printed, produced ~0.033 probability leakage into bunched data-mode outputs for a `|1,1>` input -- directly contradicting Knill's own Eq. 6, which the matrix is proven to satisfy exactly in the paper.
- **Fix:** Identified the paper's `V_rs = u_sr` transpose definition (stated in Sec. III) as differing from `UserDefinedInterferometer`'s expected orientation; used `V^T` instead.
- **Verification:** A standalone diagnostic (4 of Eq. 6's zero-leak constraints, tested directly against the 4-mode gate before any 6-mode embedding) confirmed the fix: leak terms dropped from ~0.033 to ~1e-32. Full pipeline TVD then measured at 3.5e-15.
- **Committed in:** `4879010` (the fix was made before the commit, so the commit reflects only the corrected, working script)

---

**Total deviations:** 1 auto-fixed (1 bug, found and fixed within the same session, well inside the plan's time-box)
**Impact on plan:** None on scope -- this is exactly the kind of "obvious culprit" (matrix/mode orientation convention) 19-CONTEXT.md's disagreement-handling protocol names as the first thing to check when Julia/Python disagree, and it resolved in a single focused pass.

## Issues Encountered
None beyond the auto-fixed transpose bug above, which is itself a genuine, positive finding (an independent confirmation that the literature-sourced construction is correct once oriented properly) rather than an unresolved issue.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- VERIFY-03's weight-2 leg is fully satisfied with a real, independently-sourced, measured GO result -- not a partial-go. This is the phase's highest-stall-risk piece (per this plan's own framing and CONTEXT.md's isolation design), and it did not stall.
- Plans 19-02, 19-03, and 19-05 (VERIFY-02, VERIFY-03's weight-1 leg, and VERIFY-04) are independently gradeable and were not blocked by this plan's execution or its debugging pass, per 19-CONTEXT.md's decoupling philosophy.
- `julia/verify_photonic_iqp_weight2.jl` runs cleanly end-to-end via `julia --project=julia julia/verify_photonic_iqp_weight2.jl` and can be re-run to re-verify the result at any time.
- No blockers identified for Plan 19-06 or Phase 20/21's write-up work, which can now cite a real (not partial) VERIFY-03 weight-2 result.

---
*Phase: 19-independent-julia-cross-checks*
*Completed: 2026-08-17*
