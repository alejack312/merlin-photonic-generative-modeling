---
phase: 19-independent-julia-cross-checks
plan: 02
subsystem: testing
tags: [cross-language-verification, yao.jl, julia, iqp-photonic-encoding, tvd]

# Dependency graph
requires:
  - phase: 19-independent-julia-cross-checks (Plan 01)
    provides: results/julia_reference/qubit_n2.csv, qubit_n3.csv (Python exact_qubit_iqp_distribution reference dumps)
provides:
  - julia/verify_qubit_iqp.jl, an independent Yao.jl build of this repo's qubit-side IQP circuit with a passing TVD cross-check
  - results/phase19_verify02_results.md, VERIFY-02's methodology, measured TVD, and GO verdict
affects: [20-technical-write-up]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Julia CSV-reference diff bridge: read Python-generated results/julia_reference/*.csv via DelimitedFiles with explicit String element type (preserves leading-zero bitstring keys like \"00\"), reimplement the exact Python TVD formula locally rather than importing/shelling out"
    - "Empirical bit-ordering confirmation via two-candidate closed-form test: when a target library's basis-index convention is uncertain, build an asymmetric-parameter circuit with an independently-known per-qubit marginal, test both plausible orderings against it, and assert exactly one matches -- never assume from prior documentation alone"

key-files:
  created:
    - julia/verify_qubit_iqp.jl
    - results/phase19_verify02_results.md
  modified: []

key-decisions:
  - "Phase convention Rz(-2*theta) == WP(theta,0) was derived algebraically in a code comment before being coded, then independently confirmed numerically at n=1 (atol=1e-10) -- not assumed from 19-RESEARCH.md's Pitfall 2 write-up alone."
  - "Yao's bit-ordering (qubit m = LSB of the 0-based probs() index) was re-verified empirically for THIS circuit via an asymmetric-theta n=2 probe with two named candidate orderings (A: qubit=LSB, B: qubit=MSB), asserting exactly one matches known closed-form marginals -- rather than trusting hello_yao.jl's Bell-state-derived comment by citation only."
  - "Task commits were split by temporarily trimming the script to Task 1's scope (phase-convention + bit-ordering checks only), committing, then restoring Task 2's cross-check section -- since both tasks were authored together, this preserves atomic per-task commit granularity without losing any verification step."

patterns-established:
  - "Two-candidate empirical bit-ordering test: whenever a second library's basis-index convention needs confirming, construct a minimal asymmetric circuit with an independently-known closed-form per-qubit result, test both plausible bit-orderings against it, and hard-assert exactly one candidate matches (not \"close enough\") before trusting anything built on that convention."

# Metrics
duration: 25min
completed: 2026-08-17
---

# Phase 19 Plan 02: Yao.jl Qubit-Side IQP Cross-Check Summary

**Independent Yao.jl circuit (H/Rz/put/chain primitives) reproduces `iqp_photonic_encoding.py`'s exact qubit-side IQP distribution at n=2 and n=3 with measured TVD of 2.3e-17 and 1.1e-16 respectively -- roughly 10 orders of magnitude inside the locked 1e-6 tolerance.**

## Performance

- **Duration:** 25 min
- **Started:** 2026-08-17T14:12:00+02:00 (approx)
- **Completed:** 2026-08-17T14:19:08+02:00
- **Tasks:** 2/2
- **Files modified:** 2 (1 script + 1 results doc)

## Accomplishments
- `build_qubit_iqp_circuit(n, thetas)` -- an independently-built Yao.jl circuit (not a mechanical port of Perceval's structure) reproducing this repo's `|+>^n -> diagonal weight-1 phase layer -> H^n conjugation` construction using Yao's own `H`/`Rz`/`put`/`chain` API
- Phase-convention translation (`WP(theta,0)` <-> Yao's `Rz(-2*theta)`) derived algebraically in-file and confirmed numerically at n=1 (`atol=1e-10` against the closed-form `cos(theta)^2`/`sin(theta)^2` marginal)
- Yao's bit-ordering convention confirmed empirically (not assumed) via an asymmetric n=2 probe circuit tested against two named candidate orderings, with a hard assertion that exactly one candidate matches known closed-form marginals
- `probs_to_bitstring_dict(reg, n)` converts Yao's `probs()` vector into this repo's own bitstring convention using the empirically-confirmed ordering
- `read_reference_csv`/`total_variation_distance` reimplement the Python-side CSV read and exact TVD formula independently in Julia (no Python import/shell-out)
- Both cross-checks diff **by bitstring key**, never by raw vector index, per CONTEXT.md's must-have
- VERIFY-02 satisfied with a GO verdict: `julia --project=julia julia/verify_qubit_iqp.jl` exits 0, printing PASS at every checkpoint

## Task Commits

Each task was committed atomically:

1. **Task 1: Derive phase convention and build the Yao.jl circuit** - `fba91a5` (feat)
2. **Task 2: Run n=2/n=3 cross-check against the Python reference and write results** - `86ac792` (feat)

_No TDD flow for this plan (`autonomous: true`, no test file specified -- this is a verification script, not new library logic with its own test suite)._

## Files Created/Modified
- `julia/verify_qubit_iqp.jl` - Independent Yao.jl qubit-side IQP circuit build, phase-convention derivation + numeric check, empirical bit-ordering check, `build_qubit_iqp_circuit`/`probs_to_bitstring_dict`/`read_reference_csv`/`total_variation_distance`, and the n=2/n=3 TVD cross-check against `results/julia_reference/qubit_n2.csv`/`qubit_n3.csv`
- `results/phase19_verify02_results.md` - VERIFY-02 methodology (phase-convention derivation, bit-ordering confirmation, diff protocol), measured TVD table, GO verdict, and an explicit "what this does/doesn't establish" scope statement

## Decisions Made
- **Phase-convention derivation-before-coding**: the algebraic proof that `Rz(-2*theta) == WP(theta,0)` was written as an in-file comment (matching this repo's "no silent unilateral design decisions" convention) before the corresponding code, then independently confirmed numerically -- both steps required by CONTEXT.md's must-haves, neither skipped.
- **Bit-ordering re-verified per-circuit, not re-cited**: rather than reusing `hello_yao.jl`'s Bell-state-derived bit-ordering comment as given, this plan built a fresh asymmetric-theta probe specific to the actual weight-1 IQP circuit and re-derived the same convention independently -- belt-and-suspenders, and the CONTEXT.md must-have explicitly required "verified empirically (not assumed)."
- **Task-commit split via temporary trim/restore**: since both tasks were authored together in one file, Task 1's commit was produced by temporarily trimming the script to just the phase-convention + bit-ordering sections, verifying that trimmed version runs and passes standalone, committing, then restoring the full file (Task 2's CSV cross-check) for the second commit -- preserves atomic per-task history without any verification step being skipped or faked.

## Deviations from Plan

None - plan executed exactly as written. No architectural changes, no bugs found, no missing-critical-functionality gaps, no blocking issues. Both TVDs passed on the first full run of the completed script (no debugging pass was needed).

## Issues Encountered
None.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- VERIFY-02 is fully satisfied and independently reproducible: `julia --project=julia julia/verify_qubit_iqp.jl` exits 0 from a clean checkout, given `results/julia_reference/qubit_n2.csv`/`qubit_n3.csv` (Plan 19-01's output) on disk.
- `results/phase19_verify02_results.md` records the methodology and measured numbers for Phase 20's write-up to cite directly.
- Plans 19-03/19-04/19-05 (VERIFY-03/VERIFY-04, BosonSampling.jl-based) are unaffected by and do not depend on this plan's specific implementation -- CONTEXT.md's "independently gradeable" design holds. An untracked `julia/verify_photonic_iqp_weight1.jl` was observed in the working tree during this plan's execution (`git status`), consistent with a concurrent session already working Phase 19's other wave-2 plans in parallel, per this project's established pattern (see Phase 18's STATE.md notes on concurrent phase-runner sessions) -- not touched by this plan.
- No blockers identified.

---
*Phase: 19-independent-julia-cross-checks*
*Completed: 2026-08-17*
