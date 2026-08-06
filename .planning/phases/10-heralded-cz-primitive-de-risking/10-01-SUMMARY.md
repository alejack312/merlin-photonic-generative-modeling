---
phase: 10-heralded-cz-primitive-de-risking
plan: 01
subsystem: quantum-photonic-simulation
tags: [perceval, heralded-cz, klm-cz, herald-success-probability, phase-amplitude, pytest]

# Dependency graph
requires:
  - phase: 09-encoding-design
    provides: "docs/iqp-photonic-encoding.md's Ingredient 2 weight-2 derivation (heralded_cz + PBS conversion, CZ/ZZ operator identity), which flagged the herald-success probability as an unverified literature citation"
provides:
  - "heralded_cz's herald-success probability independently measured and asserted at exactly 2/27 (~0.074074), uniform across all 4 computational-basis dual-rail inputs plus 2 superposition spot-checks, read from Processor.probs()'s global_perf/physical_perf/logical_perf (never shot-sampled)"
  - "CZ phase sign confirmed via Simulator.prob_amplitude on the bare 6-mode circuit: negative on |1,1>, positive on |0,0>/|0,1>/|1,0>, matching diag(1,1,1,-1)"
  - "logical_perf's purity confirmed (no hidden second filter beyond the herald): empty post_select_fn + zero-leakage Analyzer truth table"
  - "docs/iqp-photonic-encoding.md updated in 3 sections (Ingredient 2, Open Questions, Conclusion) to state the confirmed measurement, replacing prior unverified-literature-citation language"
affects: [11-cz-insertion-unit-and-weight-2-circuit-composition, 12-exact-reference-extension-and-tvd-validation]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Two distinct object graphs for probability vs. phase: Processor(build_experiment()) + compute_physical_logical_perf(True) for global_perf/physical_perf/logical_perf; separate Simulator(SLOSBackend()) on the bare build_circuit() output for phase-sensitive prob_amplitude reads, since Processor.probs()/Analyzer are phase-blind"
    - "Manual 6-mode BasicState construction for the Simulator phase path must read herald ancilla photon counts from Experiment.in_heralds (not hardcode them) -- Processor.with_input() auto-fills this on a 4-length BasicState, but the bare-circuit Simulator path has no such auto-fill"
    - "StateVector amplitude coefficients must be cast to plain Python float before multiplying/adding StateVector terms -- numpy.float64 mis-dispatches exqalibur's pybind operator overloads, raising a misleading 'inhomogeneous shape' ValueError instead of a type error"

key-files:
  created:
    - heralded_cz_derisking.py
    - tests/test_heralded_cz_derisking.py
  modified:
    - docs/iqp-photonic-encoding.md

key-decisions:
  - "Herald-success probability and CZ phase are measured via two separate object graphs, not one -- Processor/Experiment for probability (global_perf/physical_perf/logical_perf), bare Simulator for phase (prob_amplitude) -- following 10-RESEARCH.md's explicit recommendation rather than trying to extract phase information from the phase-blind Processor path."
  - "logical_perf's purity for this gate is treated as a checked fact (empty post_select_fn + zero-leakage Analyzer truth table), not assumed -- resolves the open discretion question CONTEXT.md/10-RESEARCH.md flagged about whether logical_perf bundles a second hidden filter."
  - "docs/iqp-photonic-encoding.md's literature-comparison language stays descriptive: the measured 2/27 numerically matches the previously-cited heralded-variant literature figure to the quoted precision, but this is stated as an observation about this specific gate, not a claim of equivalence to the general literature construction family."

patterns-established:
  - "Standalone de-risking script + pytest test pairing (script builds/prints/asserts once in main(); test file imports functions and re-asserts as pytest cases) -- same division of labor as Phase 8's perceval_fluency_demo.py / test_perceval_fluency_demo.py, now reused for the second such artifact in this repo."

# Metrics
duration: 25min
completed: 2026-08-06
---

# Phase 10 Plan 01: Heralded-CZ Primitive De-Risking Summary

**`heralded_cz`'s herald-success probability (2/27, uniform across 4 computational-basis + 2 superposition inputs) and CZ phase sign (`-1` on `|1,1⟩` only) independently measured and asserted programmatically via `Processor.probs()` and `Simulator.prob_amplitude`, with `logical_perf`'s purity confirmed via empty `post_select_fn` and zero Analyzer-truth-table leakage.**

## Performance

- **Duration:** 25 min
- **Started:** 2026-08-06T00:00:00Z (approx, session start)
- **Completed:** 2026-08-06
- **Tasks:** 3/3 completed
- **Files modified:** 3 (2 created, 1 modified)

## Accomplishments
- Confirmed, not just cited: `heralded_cz`'s herald-success probability is exactly 2/27 (~0.074074), uniform across all 4 computational-basis dual-rail inputs and 2 superposition spot-checks, read from `Processor.probs()`'s `global_perf`/`physical_perf`/`logical_perf` — never shot-sampled.
- Confirmed the CZ phase sign directly via `Simulator.prob_amplitude` on the bare 6-mode circuit: `|1,1⟩` gives a negative amplitude, the other three combinations positive, exactly matching `diag(1,1,1,-1)` — something `Processor.probs()`/`Analyzer` cannot show since they're phase-blind.
- Confirmed `logical_perf` for this gate is pure herald condition with no hidden second filter (empty `post_select_fn`, zero leakage in an `Analyzer` truth table over all 4 computational-basis inputs) — resolves the open discretion question CONTEXT.md/10-RESEARCH.md flagged.
- Updated `docs/iqp-photonic-encoding.md`'s Ingredient 2, Open Questions, and Conclusion sections to state the confirmed 2/27 + phase-sign result, replacing stale "unverified"/"not independently recomputed" language, framed descriptively (no equality claimed with the general literature construction).

## Task Commits

Each task was committed atomically:

1. **Task 1: Build heralded_cz_derisking.py — herald-success probability + CZ phase-sign checks** - `7e32e04` (feat)
2. **Task 2: Write tests/test_heralded_cz_derisking.py — pytest regression coverage** - `ab62fd0` (test)
3. **Task 3: Update docs/iqp-photonic-encoding.md with the confirmed measurement** - `869388c` (docs)

## Files Created/Modified
- `heralded_cz_derisking.py` - Standalone module measuring herald-success probability (Processor/Experiment path) and CZ phase amplitude (bare-circuit Simulator path) for `heralded_cz`, with a `main()` printing PASS/FAIL for uniformity, no-leakage, `post_select_fn` emptiness, and phase-sign checks
- `tests/test_heralded_cz_derisking.py` - 12 pytest cases importing directly from `heralded_cz_derisking.py`, covering herald-success uniformity (parametrized + superposition spot-checks), phase sign (parametrized), no-leakage, and `post_select_fn` emptiness
- `docs/iqp-photonic-encoding.md` - Ingredient 2, "Open questions and limitations, collected", and "Conclusion and Open Questions" sections updated to state the confirmed 2/27 figure and phase sign, replacing prior unverified-citation language

## Decisions Made
- Herald-success probability and CZ phase measured via two separate object graphs (`Processor`/`Experiment` for probability, bare `Simulator` for phase) rather than trying to force one API to answer both questions — matches 10-RESEARCH.md's explicit recommendation and Perceval's actual API split (Processor.probs()/Analyzer are phase-blind by design).
- `logical_perf`'s purity treated as a checked, asserted fact (empty `post_select_fn` string + zero-leakage `Analyzer` truth table), not an assumption — closes the open question CONTEXT.md raised about whether `logical_perf` silently bundles a second filter beyond the herald condition.
- Literature-comparison framing in the doc stays strictly descriptive: the measured 2/27 numerically matches the ~2/27 heralded-variant figure previously cited from the literature, but the doc states this as an observation about this specific gate's implementation, not a claim that this construction is identical to the general literature gate family.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 1 - Bug] `numpy.float64` amplitude coefficients silently broke `StateVector` construction**
- **Found during:** Task 1 (building the superposition-input herald-success spot-checks)
- **Issue:** `pcvl.StateVector() += amplitude * pcvl.StateVector(state)` raised `ValueError: setting an array element with a sequence... inhomogeneous shape` whenever `amplitude` was a `numpy.float64` (e.g. `1/np.sqrt(2)` or a fresh `pcvl.StateVector()` accumulator), rather than a plain Python `float`. This is a pybind operator-overload dispatch quirk in the installed `exqalibur` backend, not a physics or logic error — diagnosed live by isolating the exact failing multiplication in a standalone repro.
- **Fix:** Cast amplitude coefficients to plain Python `float` before multiplying/adding `StateVector` terms, and build the accumulator by summing terms directly (`float(amp) * StateVector(...) + ...`) instead of starting from an empty `pcvl.StateVector()` and using `+=`.
- **Files modified:** `heralded_cz_derisking.py` (`measure_herald_success_superposition`)
- **Verification:** `python heralded_cz_derisking.py` now runs to completion with both superposition spot-checks (`|+⟩|+⟩`, `|+⟩|0⟩`) correctly reporting `global_perf ≈ 2/27`, matching 10-RESEARCH.md's cited values.
- **Committed in:** `7e32e04` (Task 1 commit)

---

**Total deviations:** 1 auto-fixed (1 bug)
**Impact on plan:** Necessary for the superposition spot-check criterion (an explicit plan requirement) to run at all. No scope creep — the fix is scoped entirely to constructing `StateVector` inputs correctly, using exactly the construction 10-RESEARCH.md's Pattern section specified, just with a numeric-type fix the research session's example code hadn't hit.

## Issues Encountered
None beyond the deviation above — all measured values (herald-success probability, phase amplitudes, no-leakage, `post_select_fn` emptiness) matched 10-RESEARCH.md's live-measured figures exactly on first successful run.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- `heralded_cz` is de-risked standalone: herald-success probability, CZ phase sign, and `logical_perf` purity are all confirmed programmatically and committed as regression tests, satisfying WT2-04 and WT2-08.
- `docs/iqp-photonic-encoding.md` no longer carries stale "unverified" language about the success-probability figure — Phase 11 can build the full weight-2 circuit (`PBS` conversion + `heralded_cz` + `π/4` phase corrections + `PBS` back-conversion) on top of a primitive whose behavior is now independently confirmed, not just cited from literature.
- Existing 32-test suite (26 weight-1 + 6 fluency-demo) plus the new 12 heralded_cz-de-risking tests all green — no regressions carried into Phase 11.
- No blockers. The one open item this phase deliberately left open (per plan scope): the full weight-2 circuit's end-to-end behavior once `heralded_cz` is composed with `PBS` conversion and phase corrections — that's explicitly Phase 11/12's job, not re-attempted here.

---
*Phase: 10-heralded-cz-primitive-de-risking*
*Completed: 2026-08-06*
