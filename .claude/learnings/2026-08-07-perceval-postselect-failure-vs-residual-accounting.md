# Manual post-selection: which bucket does a failure belong in?
Date: 2026-08-07 · Scope: project · Recurs when: building a manually-filtered (herald-free/postselect-free) Perceval measurement pipeline for any linear-optical gate whose registered post-selection condition covers multiple physical checks and can't compose with later pipeline components (Pitfall 3 pattern).

## Context & constraints
- `PostProcessedControlledRotationsItem` (CP(α)) registers ONE combined condition via `build_experiment()`: ancilla vacuum (`add_herald(i,0)`) AND per-qubit-pair data validity (`set_postselection('[0,1]==1 & [2,3]==1')`) — two physical checks, registered together as the gate's own success condition.
- This repo's established 3-tuple reporting convention (`dist`, `residual`, `*_failure_prob`) requires every failure mode to land in exactly one bucket, and `residual` is meant only for genuinely unrelated leakage (e.g. a bystander qubit the gate never touched).
- `PBS`/`HWP` (this project's polarization<->dual-rail wrap/unwrap and conjugation gates) are per-qubit-pair photon-number-preserving — no cross-qubit-pair mode coupling.

## Approach
1. Implement the manual filter using the literal plan/spec wording first, but treat the plan's own smoke-test step as a real correctness gate, not a formality — run it before writing the full test suite.
2. If the smoke test's TVD doesn't match the target bar, don't assume it's a wiring/convention bug. First isolate the bare gate + a plain readout (no state-prep/diagonal/conjugation) and check whether the "clean" per-basis-input success amplitude matches the theoretical value exactly. If it does, the wiring is fine — the bug is in the accounting/classification layer, not the circuit.
3. Trace which physical checks the catalog gate's OWN registered condition actually covers (read `build_experiment()`'s `add_herald`/`set_postselection` calls from source, don't assume it's ancilla-only). Any check that's part of the gate's own condition and touches the SAME qubit pair the gate acts on belongs in that gate's failure_prob.
4. Reserve `residual` only for checks on modes the gate never touched (bystander qubits).

## Decision rules that generalize
- IF a passive component (PBS, HWP, or equivalent) sits between the gate and the final readout, AND it doesn't couple different qubit pairs' modes together, THEN a qubit pair's validity at final readout is mathematically identical to its validity immediately after the gate — safe to check either place.
- IF the catalog gate's `build_experiment()` registers more than one condition (ancilla heralds AND `set_postselection`), THEN both conditions' failures belong in the same `*_failure_prob` bucket — splitting them across `failure_prob`/`residual` silently divides `dist` by the wrong denominator.
- IF TVD is large (~0.1-0.5) but a bare-gate-plus-readout isolation test shows the correct amplitude landing exactly on the expected computational-basis outcome, THEN the bug is very likely a postselection-accounting/classification error, not a mode-wiring/convention bug — check the failure/residual split before re-deriving PERM adapters or mode-mapping dicts.

## Mistakes avoided / dead ends
- Assumed (per prior research's own framing) that a large TVD mismatch (~0.3-0.4) after fixing the ancilla-mode-count arithmetic meant a deeper wiring/convention bug remained unfound. It didn't — the wiring was already correct; only the accounting was wrong. The tell: per-basis-input isolated testing showed the "clean" success amplitude exactly matching theory (1/9 at α=π) for every input, which a genuine wiring bug would not produce.

## Verification
- `photonic_cp_iqp_distribution` TVD against `exact_qubit_iqp_distribution` at n=2,3, 3 non-trivial α values: `~1e-16`-`1e-15` (target `<1e-6`).
- Measured success probability (`1 - postselect_failure_prob`) matches closed-form `p_success(α)=1/σ_max^4` to `~1e-15`.
- `α=π` boundary vs. `heralded_cz`'s already-validated output: TVD `~3e-15`.

## Next time (for a weaker model)
- Do: read the catalog gate's `build_experiment()` source to see exactly which conditions it registers before writing the manual filter; run the plan's own smoke test before the full suite; isolate bare-gate-plus-readout per-basis-input tests when TVD is off by a large margin.
- Don't: assume a large TVD gap means the mode-mapping/PERM-adapter convention is wrong just because a prior research pass already flagged it as unresolved — verify the wiring in isolation first, since accounting bugs produce the same symptom (large TVD) as wiring bugs.

## Changed files
- iqp_photonic_encoding.py — `photonic_cp_iqp_distribution`'s failure/residual split corrected; `_decode_single_qubit_pair` added.
