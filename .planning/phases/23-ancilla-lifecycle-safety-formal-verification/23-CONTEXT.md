# Phase 23: Ancilla Lifecycle Safety — Formal Verification - Context

**Gathered:** 2026-08-22
**Status:** Ready for planning

<domain>
## Phase Boundary

Build a bounded Forge model of CP(α) ancilla-mode and four-mode-block lifecycles across ordered gate traces. The model must encode deferred post-selection explicitly, check that no live mode/block is reallocated, expose unsafe reuse as a trace, provide a safe reuse witness across completed circuit epochs, and compare the structural result with Phase 22's numerical pooled-vs-dedicated result. The phase also records whether temporal lifetime safety changes Phase 22's static minimum-block-count conclusion. It does not implement a k-pair Python circuit or rerun the hardness-under-loss study.

</domain>

<decisions>
## Implementation Decisions

### Trace representation
- **D-01:** Use explicit relational Forge `State` snapshots, not `#lang forge/temporal`. This follows the owner's `stop_and_copy.frg` precedent and keeps the lifecycle state inspectable.
- **D-02:** Represent one ordered trace with a `next` relation and a configurable finite gate-depth bound rather than duplicating separately named state signatures for every depth.
- **D-03:** Permit traces of up to `N` gate steps so Forge can expose the shortest unsafe trace within the declared bound. The model must still enforce the minimum two-gate scope where a witness requires it.

### Lifecycle resource and event semantics
- **D-04:** Track both individual ancilla modes and their grouped four-mode ancilla block. The block remains the allocation unit inherited from Phase 22; individual mode state is retained for the no-mode-reallocation property.
- **D-05:** Expand each gate protocol into explicit `allocate → begin/use → finish` events, with the lifecycle states `free → allocated → in-use` visible in the trace.
- **D-06:** Apply strict deferred-postselection liveness: a mode/block remains live after a gate finishes and cannot be collected or reused before final post-selection. The terminal sequence is explicit: `in-use → releasable → free`.

### Safe and unsafe witnesses
- **D-07:** Model both interpretations required by the phase: safe reuse across completed circuit epochs and unsafe reuse within one deferred-postselection trace.
- **D-08:** The primary unsafe trace uses two vertex-disjoint pairs assigned the same block, with the second allocation occurring before final post-selection. This isolates lifecycle failure from the already-known same-pair composition failure.
- **D-09:** The safe non-vacuous witness uses block 0 for pair `(0,1)`, reaches final post-selection and `free`, then reuses block 0 in a later epoch for vertex-disjoint pair `(2,3)`.
- **D-10:** Preserve the raw Forge witness and add a human-readable state-by-state trace table showing event, pair, block, individual-mode status, and the exact clobber point.

### Phase 22 cross-check and bounded scope
- **D-11:** Perform both comparisons for LIFE-05: the same-trace strict-liveness case is the primary comparison against Phase 22's vertex-disjoint numerical GO; the cross-epoch case is a separate sanity check.
- **D-12:** Keep static allocation and temporal lifetime as separate questions. Do not search for a joint new minimum `K`; report Phase 22's static minimum and state whether strict liveness creates a temporal-capacity constraint independent of edge colouring.
- **D-13:** If the structural and numerical results disagree, report the disagreement as unresolved and preserve both abstractions. Do not reconcile them by assumption or declare one method a universal winner.
- **D-14:** Start at `n = 4`, the smallest domain containing two vertex-disjoint pairs that can share a block, and prioritize trace depth and counterexample quality over matching Phase 22's full `n ≤ 8` sweep.

### the agent's Discretion
No areas were delegated to the agent. Any change to the strict liveness interpretation, safe-witness meaning, or static-versus-temporal boundary requires owner review.

</decisions>

<canonical_refs>
## Canonical References

**Downstream agents MUST read these before planning or implementing.**

### Phase scope and requirements
- `.planning/ROADMAP.md` §Phase 23 — phase goal, dependency, and success criteria.
- `.planning/REQUIREMENTS.md` §Ancilla Lifecycle Safety — LIFE-01 through LIFE-07 and the explicit out-of-scope boundary.
- `.planning/STATE.md` — Phase 22 close-out findings, Forge conventions, bitwidth cautions, and open review notes.
- `.planning/PROJECT.md` — project values, explainability boundary, and Phase 22 status.
- `MerLin_SMART_Spec_Sept1.md` — project-level deadline and explainability context.

### Phase 22 allocation and physics boundary
- `.planning/phases/22-multi-pair-ancilla-allocation-formal-verification/22-CONTEXT.md` — prior allocation decisions and scope separation.
- `results/phase22_allocation_invariant.md` — vertex-disjoint compatibility rule, fixed round-robin allocation, pairwise reduction, and static-index scope.
- `results/phase22_reuse_gate.md` — MPAIR-07 numerical pooled-vs-dedicated evidence, owner GO ruling, and bounded-claim caveats.
- `results/phase22_forge_summary.md` — Forge/Python comparison and honest contribution assessment.
- `results/phase22_forge_run_log.md` — bounded Forge execution results and time-ceiling record.
- `docs/iqp-photonic-encoding.md` §MPAIR: Pooled Multi-Pair Ancilla Allocation (Phase 22) — public specification and explicit statement of what Phase 22 does and does not establish.

### Forge and lifecycle precedents
- `forge/pooled_ancilla_allocation.frg` — relational static allocation model, `test expect` structure, non-vacuity guard, and bitwidth discipline.
- `forge/ancilla_mapping.frg` — existing injectivity model and `sat`/`unsat` non-vacuity/counterexample pattern.
- `../cs1710/hw/cs1710-memory-management-alejack312/stop_and_copy.frg` — explicit `State` snapshots, reachability/liveness, allocation, copying, and state-transition precedent.
- `../cs1710/hw/cs1710-memory-management-alejack312/mark_and_sweep.frg` — explicit allocation/mark/sweep state structure and safety/cleanliness checks.

</canonical_refs>

<code_context>
## Existing Code Insights

### Reusable Assets
- `forge/pooled_ancilla_allocation.frg`: reuse its `Pair`, `Alloc`, `Config`, compatibility, non-vacuity, and bitwidth patterns as the static baseline; do not treat it as a temporal model.
- `forge/ancilla_mapping.frg`: reuse the two-part `test expect` discipline, with a satisfiable non-vacuity witness and an unsatisfiable counterexample query.
- `../cs1710/hw/cs1710-memory-management-alejack312/stop_and_copy.frg`: use its explicit state-transition and reachability/liveness idiom as the conceptual model for lifecycle states.

### Established Patterns
- Forge files use `#lang forge`, `option run_sterling off`, explicit `for N Int` bitwidth justification, and `test expect` blocks rather than unbounded claims.
- Phase 22 separates static mode-index bookkeeping from physical Perceval evidence; Phase 23 must add a third, temporal lifecycle layer without conflating those claims.
- Non-vacuity must exercise the behavior under study. A single allocated pair is insufficient; the safe witness must contain two gates and genuine block reuse across epochs.

### Integration Points
- Add the lifecycle Forge model under `forge/` as a new artifact; leave `forge/pooled_ancilla_allocation.frg` unchanged.
- Record run outputs, witness traces, and the structural/numerical comparison under `results/`.
- Fold the final lifecycle findings into `docs/iqp-photonic-encoding.md` beside the existing Phase 22 section, preserving the distinction between bounded structural evidence and numerical physical evidence.

</code_context>

<specifics>
## Specific Ideas

- The owner selected explicit relational `State` modeling after reviewing `stop_and_copy.frg`.
- The trace should be an ordered `next` sequence with a configurable upper bound, not a collection of duplicated fixed-depth models.
- Strict deferred post-selection is intentional: a block cannot become `releasable` or `free` until terminal post-selection. The apparent conflict with Phase 22's numerical GO is itself an expected result to investigate, not a premise to smooth over.
- The initial structural probe should use `n = 4`, pairs `(0,1)` and `(2,3)`, and block 0.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within Phase 23's scope.

</deferred>

---

*Phase: 23-Ancilla Lifecycle Safety — Formal Verification*
*Context gathered: 2026-08-22*
