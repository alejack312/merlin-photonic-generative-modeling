---
phase: 18-hardness-under-loss-assessment
plan: 02
subsystem: quantum-simulation
tags: [perceval, photon-loss, LC-component, NoiseModel, HARD-01, HARD-02, TDD]

# Dependency graph
requires:
  - phase: 09-encoding-design (v2.0)
    provides: iqp_photonic_encoding.build_full_circuit / all_h_input / fock_to_bitstring (weight-1 ENC-01 pipeline, reused unmodified)
provides:
  - "hardness/loss_model.py::photonic_iqp_distribution_lossy(n, thetas, eta) -- weight-1 LC-based photon-loss primitive"
  - "Proven-not-assumed avoidance of two Perceval loss-simulation pitfalls (NoiseModel silent no-op on polarization circuits; LC requires explicit min_detected_photons_filter(0))"
  - "HARD-02 satisfied: NoiseModel-vs-LC cross-check on a shared non-polarization toy circuit"
affects: [18-05 (sweep integration), 18-06 (real sweep run), 18-07/18-08 (TVD/anticoncentration analysis)]

# Tech tracking
tech-stack:
  added: []
  patterns:
    - "pcvl.LC(loss) component insertion (front-loaded, before the circuit) as the primary loss mechanism for any polarization-annotated Processor in this project -- never noise=NoiseModel(...)"
    - "proc.min_detected_photons_filter(0) is mandatory and must be called explicitly whenever LC-based loss is used"

key-files:
  created: [hardness/loss_model.py]
  modified: []

key-decisions:
  - "Followed 18-RESEARCH.md's verified code skeleton for photonic_iqp_distribution_lossy exactly (LC on all 2n modes, front-loaded before build_full_circuit, explicit min_detected_photons_filter(0)) -- no deviation needed, research's live-verified pattern worked on the first implementation attempt."
  - "hardness/__init__.py was left untouched (not overwritten with a 'minimal one-line' docstring as the plan's implementation notes suggested) because a concurrent session had already created it with a fuller docstring covering later plans' scope (baselines + loss sweep + depolarizing translation) -- overwriting would have been a regression against already-shipped, still-accurate content."

patterns-established:
  - "Pattern: any new Processor built on this project's polarization circuits that needs photon loss must use LC-component insertion + explicit min_detected_photons_filter(0), never the noise= constructor parameter."

# Metrics
duration: ~15min
completed: 2026-08-14
---

# Phase 18 Plan 02: Weight-1 LC-Based Photon-Loss Distribution Summary

**`photonic_iqp_distribution_lossy(n, thetas, eta)` — weight-1 photon loss via `pcvl.LC` component insertion (never `NoiseModel`), with both of 18-RESEARCH.md's load-bearing Perceval pitfalls proven avoided by dedicated regression tests, not just documented.**

## Performance

- **Duration:** ~15 min
- **Completed:** 2026-08-14T03:09:14Z
- **Tasks:** 1 (single TDD feature — RED confirmed, GREEN on first implementation attempt, no REFACTOR needed)
- **Files modified:** 1 created (`hardness/loss_model.py`)

## Accomplishments
- `hardness/loss_model.py::photonic_iqp_distribution_lossy(n, thetas, eta)` — builds a `Processor(2n)`, inserts `pcvl.LC(1-eta)` on every mode before `build_full_circuit`, calls `proc.min_detected_photons_filter(0)` explicitly, returns `(dist, residual, global_perf)`.
- Proved (not assumed) `eta=1.0` is a genuine identity: `dist`/`residual` match `photonic_iqp_distribution`'s lossless reference bit-for-bit (`atol=1e-9`) across n in {1,2,3}, 3 seeded theta draws each; `global_perf~=1.0`.
- Proved the Pitfall-2 regression is real: a deliberately-broken local test helper that omits `min_detected_photons_filter(0)` is shown to be loss-invariant (identical `dist` at `eta=1.0` and `eta=0.3`), while the correct function's `dist` genuinely differs (TVD > 0.05) between those same two eta values.
- HARD-02 satisfied: `NoiseModel(transmittance=eta)` and `pcvl.LC(1-eta)` agree to `atol=1e-9` on a shared bare 2-mode non-polarization toy circuit at `eta=0.5` and `eta=0.8`, matching 18-RESEARCH.md's own verified spot-check (`{|0,0>: 0.5, |1,0>: 0.5}` at `eta=0.5`).

## Task Commits

This plan's single TDD feature spanned two commits (test → feat, no refactor needed):

1. **RED: failing test for `photonic_iqp_distribution_lossy`** — committed as part of `415dbbb` by a concurrent phase-runner session executing another plan in the same shared working directory (see Deviations below); content verified byte-identical to what this plan's spec required, confirmed as genuinely RED (`ModuleNotFoundError: No module named 'hardness.loss_model'`) before implementation began.
2. **GREEN: implement `photonic_iqp_distribution_lossy`** — `4170061` (feat)

**Plan metadata:** (this commit, following)

## Files Created/Modified
- `hardness/loss_model.py` — `photonic_iqp_distribution_lossy(n, thetas, eta)`, the weight-1 LC-based photon-loss primitive
- `tests/test_loss_model.py` — already present in the working tree/git history when this plan began execution (see Deviations); not re-created or modified, its 7 tests all pass against this plan's implementation unchanged

## Decisions Made
- Implemented `photonic_iqp_distribution_lossy` following 18-RESEARCH.md's live-verified code skeleton exactly (front-loaded `LC` on all `2n` modes, explicit `min_detected_photons_filter(0)`, `float()`-cast probability values matching this repo's established numpy-float-breaks-Perceval discipline) — no deviation from the research's recommended pattern was needed.
- Left `hardness/__init__.py` untouched rather than overwriting it with the plan's suggested "minimal one-line docstring" — see Deviations below for why.

## Deviations from Plan

### Concurrent execution collision (observed, not a deviation this plan caused)

During execution, `git status`/`git log` revealed that another phase-runner session was concurrently executing other Phase 18 plans (18-01, 18-04, and in-progress 18-03) in the same shared working directory. Two concrete effects on this plan's execution:

1. **`tests/test_loss_model.py` (this plan's own RED test file, per its `files_modified` list) was already present, both on disk and already committed under commit `415dbbb`** ("feat(18-04): implement classically-easy baselines and anticoncentration alpha") by the time this plan's executor began work — content is byte-identical to what this plan's spec required, strongly suggesting the concurrent session's broad-staging commit (`git add` across the shared working tree) swept up this plan's already-written-but-uncommitted test file. RED was still independently confirmed genuine (`ModuleNotFoundError`) before any implementation code existed, so the TDD discipline itself was not compromised — only the commit attribution/labeling is anomalous. This plan did not amend or re-commit that file under a corrected message, per the standing rule against rewriting shared history that concurrent sessions may have already built on.
2. **`hardness/__init__.py` already existed** (created by the concurrent session, presumably as part of Plan 18-01 or 18-04's own scope) with a multi-line docstring already covering this plan's and later plans' scope ("...and (in later plans) the photon-loss sampling sweep and depolarizing-rate translation..."). This plan's own spec called for a "minimal one-line module docstring" version — overwriting the existing, more complete, still-accurate docstring would have been a pure regression, so it was left as-is. `hardness/__init__.py` is therefore correctly NOT listed as a file this plan modified.
3. **A third file, `tests/test_loss_model_weight2.py`, appeared mid-execution** (from what is presumably a concurrent Plan 18-03 session) — observed but deliberately not touched, staged, or committed by this plan's execution, since it is out of this plan's scope (weight-1 only).

No code-correctness deviation occurred — Rules 1-3 auto-fixes were not needed, the implementation matched the plan's spec exactly. This is flagged here as an operational/process observation per this project's standing safety concern (STATE.md's documented concurrent-session collision history from Plan 17-06), not a code deviation, and is worth surfacing to the owner: **multiple phase-runner sessions appear to be operating on the same working directory concurrently for Phase 18's independent (wave=1, depends_on=[]) plans, which risks commit-attribution mixing (as observed here) even though no data was lost or corrupted in this instance.**

## Issues Encountered
None beyond the concurrency observation above — implementation matched research's verified pattern exactly, all tests passed on the first run.

## User Setup Required
None — no external service configuration required.

## Next Phase Readiness
- `photonic_iqp_distribution_lossy` is ready for Plan 18-05's sweep integration and Plan 18-06's real sweep run — the foundational weight-1 loss primitive every later TVD/anticoncentration number in this phase traces back to.
- **Owner-visible flag:** confirm with the owner/orchestrator whether Phase 18's plans are intentionally being executed by multiple concurrent phase-runner sessions sharing one working directory (observed live during this plan's execution — see Deviations). If unintentional, commit-attribution mixing across concurrent plans (as happened with `tests/test_loss_model.py` here) could recur and should be watched for in later Phase 18 plans' SUMMARYs.

---
*Phase: 18-hardness-under-loss-assessment*
*Completed: 2026-08-14*
