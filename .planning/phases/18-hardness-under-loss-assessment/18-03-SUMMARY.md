---
phase: 18-hardness-under-loss-assessment
plan: 03
subsystem: quantum-simulation
tags: [perceval, photon-loss, LC-component, heralded-cz, herald-failure, HARD-07, TDD]

# Dependency graph
requires:
  - phase: 11-cz-insertion-unit-weight-2-circuit-composition (v2.1)
    provides: iqp_photonic_encoding.build_cz_insertion / build_state_prep_circuit / build_diagonal_layer_circuit / build_conjugation_circuit / build_readout_circuit (weight-2 heralded_cz pipeline, reused unmodified)
  - phase: 12-exact-reference-extension-tvd-validation (v2.1)
    provides: iqp_photonic_encoding._weight2_input_state / fock_to_bitstring / photonic_weight2_iqp_distribution (lossless reference + residual/herald-failure bucketing convention, reused unmodified)
provides:
  - "hardness/loss_model_weight2.py::photonic_weight2_iqp_distribution_lossy(n, i, j, thetas, eta) -- weight-2 (heralded_cz) LC-based photon-loss primitive, HARD-07's central primitive"
  - "Proven (not assumed): loss applied uniformly across all 2n+2 modes, including both heralded_cz ancilla modes -- structural test on the constructed Processor's component list"
  - "Proven (not assumed): herald-failure and transmission-loss compound physically via one real Processor.probs() call, and genuinely differ from a naive analytical per-mode-survival-product decomposition"
affects: [18-06 (real weight-2 sweep run), 18-07/18-08 (TVD/anticoncentration analysis, herald-rate-vs-eta writeup)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "For weight-2/ancilla-bearing Processors: LC(1-eta) must be front-loaded on ALL modes including ancilla modes, not just data modes, to expose the herald mechanism itself to loss (HARD-07)."
    - "Herald-failure-vs-loss compounding must be measured via one real Processor.probs() call per (n, eta) cell -- never an analytical multiplication of a separately-computed lossless herald rate against a separately-computed loss-survival probability."

key-files:
  created: [hardness/loss_model_weight2.py]
  modified: []

key-decisions:
  - "Introduced a private helper, _build_weight2_processor_lossy(n, i, j, thetas, eta), returning (proc, herald_spec) rather than inlining processor construction directly in photonic_weight2_iqp_distribution_lossy -- gives the structural ancilla-loss test (Case 2) a clean introspection point on the raw Processor's component list, mirroring iqp_photonic_encoding.py's own build_*/no_herald split pattern."
  - "Followed 18-RESEARCH.md's stated commutation argument and Plan 18-02's front-loaded weight-1 pattern exactly: LC on all 2n+2 modes before any other component, inlining _build_weight2_processor_no_herald's own .add() sequence (state prep -> diagonal layer -> CZ insertion via its own mode-mapping dict -> conjugation -> readout) rather than trying to prepend LC onto that function's own internally-built fresh Processor."

patterns-established:
  - "Pattern: any weight-2/ancilla-bearing loss primitive in this project must front-load LC on every mode the outer Processor exposes (data + ancilla), and structurally prove ancilla coverage via proc.components introspection, not just a numeric side-effect."

# Metrics
duration: ~20min
completed: 2026-08-14
---

# Phase 18 Plan 03: Weight-2 Ancilla-Inclusive Photon-Loss Distribution Summary

**`photonic_weight2_iqp_distribution_lossy(n, i, j, thetas, eta)` — heralded_cz photon loss via `pcvl.LC` on all `2n+2` modes (including both herald ancilla modes), with herald-failure/transmission-loss compounding measured through one real `Processor.probs()` call and proven to differ from a naive analytical decomposition.**

## Performance

- **Duration:** ~20 min
- **Completed:** 2026-08-14T03:22:00Z
- **Tasks:** 1 (single TDD feature — RED confirmed, GREEN on first implementation attempt, no REFACTOR needed)
- **Files modified:** 2 created (`hardness/loss_model_weight2.py`, `tests/test_loss_model_weight2.py`)

## Accomplishments
- `hardness/loss_model_weight2.py::photonic_weight2_iqp_distribution_lossy(n, i, j, thetas, eta)` — builds a `Processor(2n+2)` via a new `_build_weight2_processor_lossy` helper, inserts `pcvl.LC(1-eta)` on every one of the `2n+2` modes (data **and** both `heralded_cz` ancilla modes) before state prep, calls `proc.min_detected_photons_filter(0)` explicitly, and returns `(dist, residual, herald_failure_prob, global_perf)` — the lossless function's existing 3-tuple convention plus `global_perf`.
- Proved (not assumed) `eta=1.0` is a genuine identity: `dist`/`residual`/`herald_failure_prob` match `photonic_weight2_iqp_distribution`'s lossless reference to `atol=1e-6` at n=2 (2 seeded theta draws) and n=3 with a bystander qubit; `herald_failure_prob ~= 1 - 2/27` in both cases.
- Proved (structurally, not by numeric inference) HARD-07's ancilla-inclusive requirement: a dedicated test inspects the constructed `Processor`'s `.components` list and asserts an `LC` instance sits on every mode `0..2n+1`, explicitly including modes `2n` and `2n+1`.
- Proved herald-failure compounding is a genuine full-pipeline effect: swept `eta` over `{1.0, 0.7, 0.4, 0.1}` at fixed `n=2, i=0, j=1, thetas=[0.4, 0.9]` — `herald_failure_prob` rises monotonically from `0.9259` (eta=1.0) to `0.9967` (eta=0.1), and at every non-1.0 eta value the actual number differs from the naive prediction `1.0 - (1-hfp@eta=1)*eta**(2n+2)` by well over `1e-6` (measured gaps: `-0.0559` at eta=0.7, `-0.0343` at eta=0.4, `-0.0033` at eta=0.1) — the shortcut CONTEXT.md forbids is demonstrably wrong, not just theoretically suspect.
- Proved the Pitfall-2 regression is real for weight-2 too (not just inherited from Plan 18-02's weight-1 case): a deliberately-broken local test helper that omits `min_detected_photons_filter(0)` stays pinned at the lossless `herald_failure_prob`/`dist` across `eta`, exactly matching 18-RESEARCH.md's stated warning sign ("herald-success-rate never moves off 2/27"), while the correct function's output genuinely shifts.

## Task Commits

This plan's single TDD feature spanned two commits (test → feat, no refactor needed):

1. **RED: failing tests for `photonic_weight2_iqp_distribution_lossy`** — `6157492` (test). Confirmed genuine RED (`ModuleNotFoundError: No module named 'hardness.loss_model_weight2'`) before implementation began.
2. **GREEN: implement `photonic_weight2_iqp_distribution_lossy`** — `7ea0733` (feat). All 6 new tests passed on the first implementation attempt; full 266-test repo suite passes, zero regressions.

**Plan metadata:** (this commit, following)

## Files Created/Modified
- `hardness/loss_model_weight2.py` — `photonic_weight2_iqp_distribution_lossy(n, i, j, thetas, eta)` (public) and `_build_weight2_processor_lossy(n, i, j, thetas, eta)` (private, introspection point for the structural ancilla-loss test)
- `tests/test_loss_model_weight2.py` — 6 tests: eta=1.0 reproduction (n=2, n=3 bystander), structural ancilla-LC-coverage check, herald-failure-compounding-vs-naive-decomposition, Pitfall-2 regression, eta-range validation

## Decisions Made
- Added a private `_build_weight2_processor_lossy` helper (returning the raw `Processor` + `herald_spec`) rather than inlining processor construction directly inside the public function — needed a clean introspection point for the structural "LC present on all `2n+2` modes" test (Case 2 of the plan's spec explicitly calls for inspecting "the constructed `Processor`'s component list (or an equivalent introspection point)"), and this also mirrors `iqp_photonic_encoding.py`'s own established `build_weight2_processor` / `_build_weight2_processor_no_herald` split pattern.
- Inlined `_build_weight2_processor_no_herald`'s exact `.add()` sequence (state prep → diagonal layer → CZ insertion via its own mode-mapping dict → conjugation → readout) onto a `Processor` that already has `LC` front-loaded on every mode, rather than trying to call that existing function and prepend `LC` afterward — matches the plan's explicit instruction, since `_build_weight2_processor_no_herald` builds its own fresh `Processor` internally and offers no hook to inject components before its first `.add()` call.
- Confirmed live (not assumed from 18-RESEARCH.md's extrapolated argument) that the naive analytical decomposition genuinely diverges from the real compounded value at every tested non-lossless eta — this was the single highest-risk assumption in the plan (the compounding effect might have been too small to reliably clear a `1e-6` bound), verified with an ad hoc script before finalizing the test's assertions (see gaps quoted in Accomplishments above, all several orders of magnitude past the `1e-6` threshold).

## Deviations from Plan

None from the plan's own spec — the implementation matched 18-RESEARCH.md's documented weight-2 pattern and 18-CONTEXT.md's HARD-07 lock on the first attempt; all 6 tests passed GREEN without needing any correction.

### Concurrent execution collision (observed, not a deviation this plan caused)

Confirmed live (consistent with Plan 18-02's and 18-04's own SUMMARYs, which independently observed the same thing): multiple phase-runner sessions are executing Phase 18's other independent (`wave: 1`, `depends_on: []`) plans concurrently in this same shared working directory. Two concrete effects on this plan's own git history:

1. **Commit `6157492`** ("test(18-03): ..."), though staged with only this plan's own `tests/test_loss_model_weight2.py`, ended up also containing a concurrent session's already-staged `.planning/STATE.md` update and its `18-02-SUMMARY.md` file — `git diff --cached --name-only` immediately before committing showed only this plan's own file, meaning another session's `git add` ran in the narrow window between that check and `git commit`. Content of the swept-in files was verified intact and unrelated (Plan 18-02's own summary, an accurate STATE.md progress update) — no data loss or corruption, only commit-message/attribution mismatch.
2. **Commit `7ea0733`** ("feat(18-03): ...") similarly swept in a concurrent session's `18-04-SUMMARY.md`, for the same reason (index-sharing race between concurrent `git add`/`git commit` calls from different sessions). Verified intact and correctly attributed to Plan 18-04's own actual work.

No history was rewritten (per this project's standing rule against amending commits other sessions may already be building on, and per Plan 18-02's/18-04's precedent of the same call). No code-correctness impact — Rules 1-3 auto-fixes were not needed anywhere in this plan's own scope.

## Issues Encountered
None beyond the concurrency observation above — implementation matched research's verified pattern exactly, all tests passed on the first run, full suite green.

## User Setup Required
None — no external service configuration required.

## Next Phase Readiness
- `photonic_weight2_iqp_distribution_lossy` is ready for Plan 18-06's real weight-2/mixed sweep run — HARD-07's foundational primitive, with both the ancilla-inclusive loss requirement and the non-decomposed herald-compounding requirement independently proven, not just implemented per spec.
- **Owner-visible flag (repeat of Plan 18-02's/18-04's observation, now independently reconfirmed a third time):** multiple phase-runner sessions continue to operate on the same working directory concurrently for Phase 18's wave-1 plans. No data has been lost across three separate plans' executions so far, but commit-attribution mixing (files from one plan's commit landing under another plan's commit message) has now been observed in essentially every commit made during this concurrent window. Recommend the owner/orchestrator confirm this is intentional (per `/gsd:execute-milestone`'s documented parallel-phase-runner design) and, if so, treat commit-message/file mismatches within Phase 18's wave-1 window as expected noise rather than a signal of a real problem — each affected plan's SUMMARY.md has independently cross-checked and confirmed content integrity.

---
*Phase: 18-hardness-under-loss-assessment*
*Completed: 2026-08-14*
