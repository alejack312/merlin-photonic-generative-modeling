---
phase: 19-independent-julia-cross-checks
plan: 05
subsystem: testing
tags: [cross-language-verification, bosonsampling-jl, photon-loss, native-loss-api, uniform-loss-interferometer, iqp-photonic-encoding]

# Dependency graph
requires:
  - phase: 19-independent-julia-cross-checks
    plan: 01
    provides: results/julia_reference/weight1_loss_n2_eta*.csv, mixed_loss_n2_eta*.csv (Python reference lossy distributions, fixed single theta draw per scope)
  - phase: 19-independent-julia-cross-checks
    plan: 04
    provides: verified Knill-CZ 6x6 unitary construction (arXiv:quant-ph/0110144 Eq. 11, transpose-fixed) and the confirmed n=2/i=0/j=1 mixed-scope circuit shape, reused/generalized here for the loss cross-check
provides:
  - julia/verify_loss_model.jl, an independent BosonSampling.jl native-loss cross-check against Phase 18's LC-based loss model (weight-1 and mixed scope)
  - results/phase19_verify04_results.md, VERIFY-04's methodology + full GO verdict
affects: [20, 21]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "Doubled-mode native-loss marginalization by hand: enumerate every non-negative-integer composition of the conserved total photon count across the 2m virtual-mode space, sum compute_probability! into a physical-mode-keyed bucket -- exact, not sampling, tractable at n=2 (36/1365 patterns)"
    - "Route around a struct's missing method-dispatch registration by wrapping its own computed output field in a sibling type that does have the dispatch (UserDefinedInterferometer(li.U) instead of passing UniformLossInterferometer directly to Event) -- preserves the native computation while avoiding an unrelated API gap"

key-files:
  created:
    - julia/verify_loss_model.jl
    - results/phase19_verify04_results.md
  modified: []

key-decisions:
  - "Used BosonSampling.jl's native UniformLossInterferometer loss API (not a hand-attenuation fallback) -- confirmed usable against the actual installed v1.0.2 depot source, not GitHub main, per the plan's explicit investigation requirement."
  - "Found and worked around a real bug in the installed package: Event() cannot be constructed directly against a UniformLossInterferometer because it never registered a LossParameters method for its own type (confirmed live via a standalone repro, not inferred from source reading alone). Workaround: wrap the interferometer's own native-computed .U field in UserDefinedInterferometer(li.U) before building Events -- compute_probability! only ever reads ev.interferometer.U, so this changes nothing about the loss physics, only the dispatch path."
  - "Resolved a convention mismatch between the two projects' eta parameters: BosonSampling's UniformLossInterferometer(eta, U) treats eta as a transmission AMPLITUDE (transmission probability = eta^2), while this repo's Python-side eta is a transmission PROBABILITY directly. Passed sqrt(eta) to make the two quantities physically identical -- verified (not assumed) via an n=1 closed-form sanity check (p(survive)=eta, p(lost)=1-eta) at all 3 tested eta values before trusting the n=2 comparison."
  - "Did the doubled-mode marginalization by hand via exact enumeration, rather than using sort_by_lost_photons/lossless_part (whose semantics 19-RESEARCH.md flagged as unverified against a MultipleCounts/Partition abstraction this script has no other reason to use). Exploited that total photon number is exactly conserved across the 2m virtual-mode space (a unitary transform), so enumerating every composition of N across 2m modes (36 for weight-1 n=2, 1365 for mixed n=2) and bucketing by the physical-mode sub-pattern gives an exact marginal with no approximation."
  - "For the mixed-scope diagonal Z-phase layer, used the SYMMETRIC diag(e^{i*theta}, e^{-i*theta}) convention directly (matching build_diagonal_layer_circuit and Plan 19-04's embed_correction6 exactly), generalized to two independent per-qubit thetas (theta_i+pi/4, theta_j+pi/4) rather than reusing Plan 19-03's asymmetric phase_shift(pi-2*theta) trick -- the latter is only marginal-preserving (fine for weight-1's product-form, no-entanglement circuit) but not exact-phase-preserving, which matters once the CZ gate creates real interference between the two qubit pairs."

patterns-established:
  - "When an installed package's own MethodError reveals a missing type-specific method (here: LossParameters), verify the failure live with a minimal standalone repro before writing any workaround -- confirms it's a genuine package gap (not caller error) and that the reasoning documented in the script matches what actually happens at runtime."

# Metrics
duration: ~50min
completed: 2026-08-17
---

# Phase 19 Plan 05: Independent BosonSampling.jl Native-Loss Cross-Check (VERIFY-04) Summary

**BosonSampling.jl's native `UniformLossInterferometer` loss model (not a hand-attenuation fallback), with one narrow documented workaround for a real dispatch bug in the installed v1.0.2 package, reproduces Phase 18's LC-based photon-loss distributions for both weight-1 and mixed (weight-1+weight-2) scope at n=2, all 3 tested eta values, with TVD between 1e-14 and 1e-18 -- a full GO, not a partial-go.**

## Performance

- **Duration:** ~50 min
- **Tasks:** 2/2 (both completed; the native API investigation succeeded within budget, so the full weight-1 + mixed cross-check was attempted and completed)
- **Files modified:** 2 (1 Julia script, 1 results doc)

## Accomplishments
- Confirmed BosonSampling.jl v1.0.2's native `UniformLossInterferometer(η, U_physical)` API directly against the local Julia depot source (`~/.julia/packages/BosonSampling/TEQXU/src/types/loss.jl`), not GitHub `main` -- resolving 19-RESEARCH.md's explicitly-flagged unverified-version risk.
- Found and worked around a real bug in the installed package: constructing `Event(input, output, uniform_loss_interferometer)` raises `MethodError: no method matching LossParameters(::Type{UniformLossInterferometer})` -- confirmed live via a standalone repro before writing the workaround. Fixed by wrapping the interferometer's own native-computed `.U` field in `UserDefinedInterferometer(li.U)`, which does have the needed dispatch and is numerically identical (`compute_probability!` only ever reads `.U`).
- Resolved a convention mismatch: BosonSampling's `η` parameter is a transmission amplitude (`|t|^2` = transmission probability), while this repo's Python-side `eta` is a transmission probability directly. Confirmed `sqrt(eta_python)` is the correct translation via an n=1 closed-form sanity check (`p(survive)=eta`, `p(lost)=1-eta`) at eta in {0.99, 0.80, 0.05}, atol=1e-10.
- Did the doubled-mode marginalization (19-RESEARCH.md's single most nontrivial open API question) by hand via exact enumeration: since the virtual 2m-mode interferometer is unitary, total photon count is exactly conserved, so every composition of N photons across 2m modes was enumerated (36 for weight-1 n=2, 1365 for mixed n=2) and summed into physical-mode buckets -- an exact marginal, not sampling.
- Weight-1 leg (n=2, reusing Plan 19-03's verified dual-rail construction) and mixed leg (n=2, i=0, j=1, reusing Plan 19-04's verified Knill-CZ construction generalized to two independent per-qubit diagonal phases) both independently reproduce the Python reference distributions: TVD from `1.6e-18` to `1.8e-14` across all 3 eta values and both scopes, `herald_failure_prob` matching to within `2.6e-15`.

## Task Commits

Each task was committed atomically:

1. **Task 1+2 (combined): independent BosonSampling.jl native-loss cross-check** - `b3a6caa` (feat)
2. **Results documentation** - `b504981` (docs)

_Tasks 1 and 2 were authored and verified together as one script (the native-loss investigation succeeded within budget, so Task 2 was reached and completed in the same working session), matching Plans 19-03/19-04's precedent of one combined feat commit followed by a separate docs commit for the results file._

## Files Created/Modified
- `julia/verify_loss_model.jl` - Native `UniformLossInterferometer`-based loss cross-check: n=1 sanity check (Task 1), weight-1 and mixed n=2 loss cross-checks at 3 eta values (Task 2), extensive header documentation of the API investigation, the transmission-amplitude-vs-probability convention resolution, and the `LossParameters` dispatch workaround.
- `results/phase19_verify04_results.md` - Full methodology (native-loss investigation outcome, convention/bug findings), measured TVD/herald-failure-prob per eta per scope, and the GO verdict.

## Decisions Made
- **Native loss API used, not hand-attenuation:** confirmed usable within the plan's investigation budget; per CONTEXT.md's "Claude's Discretion" allowance, hand-attenuation was never needed as a fallback.
- **`LossParameters` dispatch workaround documented as a runnable, explained pattern** (not silently absorbed) -- the script's header comment states the exact `MethodError`, the confirmed root cause (no `LossParameters` method registered for `UniformLossInterferometer` in the installed v1.0.2), and why the workaround preserves the native loss physics unchanged.
- **eta convention translation (`sqrt(eta)`)** verified via closed-form n=1 check before being trusted in the n=2 comparison, following this project's established "verify against a hand-derivable case before trusting the full pipeline" pattern (same as Plans 19-02/19-03/19-04).
- **Mixed-scope diagonal phase uses the exact symmetric `diag(e^{i*theta}, e^{-i*theta})` convention** (matching `build_diagonal_layer_circuit` and Plan 19-04's locked-case construction), not Plan 19-03's asymmetric weight-1-only phase-shift trick -- flagged explicitly in the script as necessary specifically because the CZ gate makes exact relative phase (not just per-qubit marginals) physically load-bearing.

## Deviations from Plan

### Auto-fixed Issues

**1. [Rule 3 - Blocking] `UniformLossInterferometer` missing `LossParameters` dispatch in installed v1.0.2**
- **Found during:** Task 1 (first attempt to construct an `Event` directly against a `UniformLossInterferometer`)
- **Issue:** `Event(...)` raised `MethodError: no method matching LossParameters(::Type{UniformLossInterferometer})` -- the installed package never registered this method for its own native loss-interferometer type, even though `RandomPhaseShifter`, `LosslessLoop`, `LossyBeamSplitter`, etc. all have one.
- **Fix:** Wrap the interferometer's own native-computed `.U` field in `UserDefinedInterferometer(li.U)` before constructing `Event`s. Verified numerically identical (n=1 sanity check passes exactly) since `compute_probability!` only ever reads `ev.interferometer.U`.
- **Verification:** n=1 sanity check reproduces the exact closed-form loss probabilities (atol=1e-10); full n=2 cross-checks subsequently pass at TVD ~1e-14 to 1e-18.
- **Committed in:** `b3a6caa` (the workaround was in place before the commit, so the commit reflects only the working script)

---

**Total deviations:** 1 auto-fixed (1 blocking issue, a real installed-package API gap, found and worked around within the same session)
**Impact on plan:** None on scope -- the workaround preserves the native loss API's physics unchanged and is documented as a runnable, explained pattern in the script itself, not silently absorbed. This is exactly the kind of installed-version-specific API gap 19-RESEARCH.md's own investigation requirement anticipated (Task 1 exists precisely because GitHub-main-sourced API assumptions were flagged as unverified against the exact installed tag).

## Issues Encountered
None beyond the auto-fixed `LossParameters` dispatch gap above, which is itself a genuine, positive finding (confirms the native loss API's underlying computation is correct and usable, once routed around one narrow struct-registration gap) rather than an unresolved issue.

## User Setup Required
None - no external service configuration required.

## Next Phase Readiness
- VERIFY-04 is fully satisfied with a real, measured GO verdict across both weight-1 and mixed scope -- not a partial-go, and not a fallback to hand-attenuation.
- This closes out Phase 19's third and final requirement (VERIFY-02, VERIFY-03, and now VERIFY-04 are all satisfied with real GO results, per this plan's own framing and 19-CONTEXT.md's "independently gradeable, a stall on one doesn't block the others" isolation design -- no plan in this phase stalled).
- `julia/verify_loss_model.jl` runs cleanly end-to-end via `julia --project=julia julia/verify_loss_model.jl` (~1m24s) and can be re-run to re-verify the result at any time.
- No blockers identified for Plan 19-06 or Phase 20/21's write-up work, which can now cite real, independently-confirmed GO results for all three of VERIFY-02/03/04.

---
*Phase: 19-independent-julia-cross-checks*
*Completed: 2026-08-17*
