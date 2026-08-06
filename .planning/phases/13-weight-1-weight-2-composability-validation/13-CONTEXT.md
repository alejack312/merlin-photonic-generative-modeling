# Phase 13: Weight-1 + Weight-2 Composability Validation - Context

**Gathered:** 2026-08-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Confirm that weight-1 (single-qubit Z) and weight-2 (two-qubit ZZ, via `heralded_cz`) generator layers compose correctly within the *same* circuit — not just validated in isolation as in Phases 10-12. Scope is exactly the roadmap's single success criterion: one n=3 mixed generator test (2 weight-1 terms + 1 weight-2 term) passes, added to `tests/test_iqp_photonic_encoding.py`, with the full suite still green. This is the final phase of the v2.1 milestone.

</domain>

<decisions>
## Implementation Decisions

### Circuit configuration
- n=3. Weight-2 pair on qubits (0,1) at the mandatory θ=π/4 (per `photonic_weight2_iqp_distribution`'s internal fold — not caller-adjustable).
- Weight-1 terms: one on qubit 2 (fully outside the pair) and one *stacked* on qubit 0 or 1 (already inside the pair) — this is the only way to reach "2 weight-1 + 1 weight-2" at n=3, since only 1 qubit sits outside any pair. Deliberately chosen over bumping to n=4 with fully-disjoint qubits: stacking is a *stronger* test because it proves a qubit's independent Z term and its participation in the ZZ pair term compose correctly on the same qubit, not just across disjoint qubits.
- Do not avoid overlap — overlap is the point of this configuration.

### Theta values
- Use arbitrary, distinct, non-degenerate nonzero values for the weight-1 thetas (e.g. not all equal, not multiples of π/4, not zero) — avoids a symmetric/degenerate case that could mask a real composition bug. Claude picks the exact numbers during planning/implementation as long as they satisfy this.
- The pair theta stays locked at π/4 (not user-adjustable — `photonic_weight2_iqp_distribution` folds it internally, consistent with Phase 12's locked gate convention).

### Validation rigor
- Primary check: TVD < 1e-6 between the extended exact reference (`exact_qubit_iqp_distribution` with both `thetas` and `pair_thetas` set) and the herald-conditioned photonic distribution (`photonic_weight2_iqp_distribution`) — same style/tolerance as Phase 12's `test_enc04_toy_validation_runs_end_to_end`-style gate.
- Companion sanity check: also compare against the weight-1-only exact reference (same `thetas`, `pair_thetas=None`) and confirm TVD is clearly non-negligible (far above the 1e-6 bar) — proves the test isn't vacuously passing by accident (e.g. if the ZZ term happened to have near-zero effect on the chosen thetas).

### Test scope
- Parametrize over 2-3 configurations (varying qubit-pair choice and/or theta sets) rather than a single fixed config — more robustness than the roadmap's literal single-test wording, still well within phase scope since it's the same success criterion exercised multiple ways, not a new capability.

### Claude's Discretion
- Exact numeric theta values (any nonzero, non-degenerate set).
- Exact parametrize configurations (which 2-3 qubit-pair/theta combos), following Phase 12's existing pytest test-naming and structure conventions.
- Test function naming and placement within `tests/test_iqp_photonic_encoding.py`.

</decisions>

<specifics>
## Specific Ideas

No specific product/behavioral references — this is a technical validation test, not a user-facing feature. Match the rigor and TVD-reporting style already established in Phase 12's tests and `results/phase12_weight2_tvd_validation_summary.md`.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope. (Reminder: ARB-01 arbitrary-θ weight-2, STUDY-01/02 trainability/hardness study, WRITE-01 write-up, and BMK-03 QGAN comparison are already tracked in STATE.md's backlog, contingent on this milestone shipping — not re-raised here since they didn't come up in this discussion.)

</deferred>

---

*Phase: 13-weight-1-weight-2-composability-validation*
*Context gathered: 2026-08-06*
