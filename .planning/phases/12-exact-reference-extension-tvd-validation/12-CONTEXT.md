# Phase 12: Exact Reference Extension & TVD Validation - Context

**Gathered:** 2026-08-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Extend the exact qubit-side reference (`exact_qubit_iqp_distribution`) to include `Z_i·Z_j` pair terms, then validate the herald-conditioned weight-2 photonic distribution against it via TVD, at the same rigor bar weight-1 already cleared (explicit residual reporting, no silently-discarded probability mass). This phase must design its measurement strategy around a confirmed Perceval library limitation carried forward from Phase 11 (see Blocker Investigation below) — not discover it mid-execution.

</domain>

<decisions>
## Implementation Decisions

### Blocker Investigation — the actual technical problem

`build_weight2_processor`'s output cannot currently be measured via `Processor.probs()` because it combines three things that individually work but break Perceval's simulator together:
1. Polarization encoding (`PBS` components) — required since Phase 9.
2. A heralded ancilla photon (`add_herald`) — required because `heralded_cz` succeeds probabilistically.
3. Superposition input (the Hadamard in `build_state_prep_circuit`) — required because IQP generators are meaningless without it.

Two distinct, separately-confirmed failure modes (both from Phase 11 Plan 02, both independent of theta):
- **Crash:** `add_herald` + `PBS` together → `Processor.probs()` raises a `matmul` shape-mismatch inside `PolarizationSimulator._prepare_input`, unconditionally.
- **Silent wrong numbers:** even *without* `add_herald` registered, a real Hadamard-superposition input feeding the heralded-ancilla sub-circuit gives incorrect (non-crashing) probabilities via `PolarizationSimulator` (measured `0.1646` vs expected `0.07407` in Plan 11-02's test) — believed to be an ancilla/data-photon polarization-distinguishability bug in `PolarizationSimulator`, not a herald-registration issue.

### Measurement workaround strategy

- **Starting point: post-selection instead of registered heralding.** Never call `add_herald` on the processor used for measurement; run the bare `Processor.probs()` (avoids the crash entirely, since the crash is specifically triggered by `add_herald` + `PBS`), then manually filter/post-select the ancilla output modes in Python against the expected herald pattern, treating discarded mass as the explicit herald-failure probability. This extends Plan 11-02's existing bare-processor + manual-post-selection pattern.
- Post-selection alone does **not** solve the silent-wrong-numbers bug under superposition — that requires a separate fix attempt (leading candidate: photon annotation/labeling to disambiguate the ancilla photon from data photons during `PolarizationSimulator`'s interference calculation).
- **Time-box: tight, one focused attempt.** Try post-selection + one candidate fix for the distinguishability bug. If it doesn't land cleanly, stop investigating and fall back rather than digging further (see Fallback below).
- **File the crash as an upstream Perceval/Quandela bug report.** The repro is already fully characterized (matmul shape mismatch, independent of thetas/state_prep) — write it up as a GitHub issue. Low cost given the existing characterization, and relevant context given the Vincent Espitalier / Quandela conversation this project is building toward.

### Fallback if the blocker resists a clean fix

If neither post-selection nor the one candidate distinguishability fix lands within the tight time-box, in this order:
1. **Shot-based sampling workaround** — fall back to Perceval's sampling backend (SLOS sampler) for an approximate distribution via enough samples, reporting TVD with an explicit statistical caveat instead of the roadmap's exact `<1e-6` bar. **Note:** this is a deviation from Phase 12's locked Success Criterion 3 (`TVD < 1e-6`) and must be flagged explicitly if it happens — not silently substituted.
2. **Restrict to computational-basis-only validation** — validate the herald/CZ mechanism on definite computational-basis inputs only (as Plan 11-02's sanity check already does), and honestly document that full-superposition TVD validation is blocked, rather than faking a workaround.
3. **Stop and report the blocker plainly** — if neither above lands, report Phase 12 as genuinely blocked with the evidence, rather than dressing up partial progress as done.

### Validation scope (n, theta values)

- **Locked pass/fail gate:** n=2, θ=π/4 (per ROADMAP Success Criterion 3) — always run this.
- **Add n=3 if the workaround generalizes cheaply** (matching weight-1's own n=2,3 precedent from Phase 9) — not required, opportunistic only.
- No extra theta sweeps — production only ever uses θ=π/4 (the CZ/ZZ operator identity is fixed at this value), so sweeping other thetas is out of scope for this phase.

### Residual/failure reporting format

Both of the following, matching this project's existing patterns:
- **Function-level:** extend the existing `(dist, residual)` return-value convention (see `photonic_iqp_distribution`) to also surface herald-failure probability as an explicit third value/field — never merged into the residual, never silently renormalized away.
- **Written summary artifact:** a `results/phase12_*.md`-style write-up (matching the Phase 7 `results/phase7_*_summary.md` precedent) documenting both numbers with space for the owner's interpretation, per this repo's CLAUDE.md convention that Claude computes/plots, the owner interprets.

### Claude's Discretion

- Exact photon-annotation/labeling mechanics for the candidate distinguishability fix, if attempted.
- Whether to extend to n=3 depends on implementation cost discovered during planning/execution — not a hard requirement either way.
- Exact wording/format of the upstream Perceval bug report.

</decisions>

<specifics>
## Specific Ideas

- The workaround pattern to extend is explicitly Plan 11-02's `_build_weight2_tail_no_state_prep`-style bare-processor + manual-post-selection test — see `.planning/phases/11-cz-insertion-unit-weight-2-circuit-composition/11-02-SUMMARY.md`'s "Next Phase Readiness" section for the recommended starting point.
- Reporting style should match `results/phase7_*_summary.md` (measured numbers only, owner interpretation left open) — not a Claude-authored conclusion.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope. (The shot-based-sampling fallback and computational-basis-only fallback are documented as contingency paths within this phase, not deferred to a future phase — if either triggers, it changes how Phase 12 concludes, not what phase it belongs to.)

</deferred>

---

*Phase: 12-exact-reference-extension-tvd-validation*
*Context gathered: 2026-08-06*
