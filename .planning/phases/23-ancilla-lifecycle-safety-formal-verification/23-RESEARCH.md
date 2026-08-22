# Phase 23: Ancilla Lifecycle Safety - Formal Verification - Research

**Researched:** 2026-08-22  
**Domain:** Relational Forge bounded trace modeling for CP(alpha) ancilla lifecycle safety  
**Confidence:** HIGH for local Forge syntax and project constraints; MEDIUM for expected Phase 23 solver bounds until the lifecycle model is measured.

<user_constraints>
## User Constraints (from CONTEXT.md)

### Locked Decisions

### Trace representation
- **D-01:** Use explicit relational Forge `State` snapshots, not `#lang forge/temporal`. This follows the owner's `stop_and_copy.frg` precedent and keeps the lifecycle state inspectable.
- **D-02:** Represent one ordered trace with a `next` relation and a configurable finite gate-depth bound rather than duplicating separately named state signatures for every depth.
- **D-03:** Permit traces of up to `N` gate steps so Forge can expose the shortest unsafe trace within the declared bound. The model must still enforce the minimum two-gate scope where a witness requires it.

### Lifecycle resource and event semantics
- **D-04:** Track both individual ancilla modes and their grouped four-mode ancilla block. The block remains the allocation unit inherited from Phase 22; individual mode state is retained for the no-mode-reallocation property.
- **D-05:** Expand each gate protocol into explicit `allocate -> begin/use -> finish` events, with the lifecycle states `free -> allocated -> in-use` visible in the trace.
- **D-06:** Apply strict deferred-postselection liveness: a mode/block remains live after a gate finishes and cannot be collected or reused before final post-selection. The terminal sequence is explicit: `in-use -> releasable -> free`.

### Safe and unsafe witnesses
- **D-07:** Model both interpretations required by the phase: safe reuse across completed circuit epochs and unsafe reuse within one deferred-postselection trace.
- **D-08:** The primary unsafe trace uses two vertex-disjoint pairs assigned the same block, with the second allocation occurring before final post-selection. This isolates lifecycle failure from the already-known same-pair composition failure.
- **D-09:** The safe non-vacuous witness uses block 0 for pair `(0,1)`, reaches final post-selection and `free`, then reuses block 0 in a later epoch for vertex-disjoint pair `(2,3)`.
- **D-10:** Preserve the raw Forge witness and add a human-readable state-by-state trace table showing event, pair, block, individual-mode status, and the exact clobber point.

### Phase 22 cross-check and bounded scope
- **D-11:** Perform both comparisons for LIFE-05: the same-trace strict-liveness case is the primary comparison against Phase 22's vertex-disjoint numerical GO; the cross-epoch case is a separate sanity check.
- **D-12:** Keep static allocation and temporal lifetime as separate questions. Do not search for a joint new minimum `K`; report Phase 22's static minimum and state whether strict liveness creates a temporal-capacity constraint independent of edge colouring.
- **D-13:** If the structural and numerical results disagree, report the disagreement as unresolved and preserve both abstractions. Do not reconcile them by assumption or declare one method a universal winner.
- **D-14:** Start at `n = 4`, the smallest domain containing two vertex-disjoint pairs that can share a block, and prioritize trace depth and counterexample quality over matching Phase 22's full `n <= 8` sweep.

### the agent's Discretion
No areas were delegated to the agent. Any change to the strict liveness interpretation, safe-witness meaning, or static-versus-temporal boundary requires owner review.

### Deferred Ideas (OUT OF SCOPE)

None - discussion stayed within Phase 23's scope.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| LIFE-01 | Model ancilla modes as allocatable cells with explicit lifecycle across a sequence of CP(alpha) gate applications. | Use `sig State { next: lone State }` / `Trace` patterns from local Forge examples and the owner CS1710 memory-management state idiom. [VERIFIED: C:/Users/cuqui/cs1710/forge/forge/examples/basic/gameOfLife.frg; C:/Users/cuqui/cs1710/hw/cs1710-memory-management-alejack312/stop_and_copy.frg] |
| LIFE-02 | Check no ancilla mode is reallocated while live; counterexample must be a trace. | Use an unsafe witness predicate searching for two vertex-disjoint gates assigned block 0 where the second allocation occurs before terminal post-selection and while block/modes are still live. [VERIFIED: .planning/phases/23-ancilla-lifecycle-safety-formal-verification/23-CONTEXT.md] |
| LIFE-03 | Encode deferred post-selection explicitly. | Add terminal `postselect/release/free` events and forbid `releasable`/`free` before terminal post-selection inside one epoch. [VERIFIED: .planning/REQUIREMENTS.md; results/phase22_reuse_gate.md] |
| LIFE-04 | Non-vacuity requires at least two sequential gates and at least one genuine reuse with safety holding. | Provide a safe cross-epoch witness: pair `(0,1)` uses block 0, terminal release frees it, later epoch pair `(2,3)` reuses block 0 safely. [VERIFIED: .planning/phases/23-ancilla-lifecycle-safety-formal-verification/23-CONTEXT.md] |
| LIFE-05 | Cross-check structural verdict against Phase 22 MPAIR-07 numerical verdict. | Report same-trace strict-liveness result against Phase 22's n=4 vertex-disjoint GO (`tvd_pooled_vs_dedicated` about 1e-14) and cross-epoch reuse as a separate sanity check. [VERIFIED: results/phase22_reuse_gate.md] |
| LIFE-06 | State whether safe-reuse constraint changes Phase 22 minimum-block-count result. | Keep static K from Phase 22 (`K=n-1` even, `K=n` odd; Forge converged through n=6, Python baseline through n=8) separate from temporal capacity: same-trace strict liveness forbids reusing a block before terminal post-selection. [VERIFIED: results/phase22_allocation_invariant.md; results/phase22_forge_summary.md] |
| LIFE-07 | Fold findings into `docs/iqp-photonic-encoding.md`. | Add a Phase 23 lifecycle section beside the Phase 22 pooled-allocation section, preserving the distinction between structural lifecycle evidence and numerical Perceval evidence. [VERIFIED: docs/iqp-photonic-encoding.md; .planning/phases/23-ancilla-lifecycle-safety-formal-verification/23-CONTEXT.md] |
</phase_requirements>

## Summary

Phase 23 should model ancilla reuse as a bounded lifecycle trace, not as another static coloring problem. The recommended implementation is a new `forge/ancilla_lifecycle_safety.frg` file using relational Forge, `option run_sterling off`, explicit `State` atoms linked by `next`, and `run/test expect ... for {next is linear}` where useful. This syntax is supported by local Forge examples that model finite traces with `State.next`, `Trace.first`, acyclicity, and linear-order annotations. [VERIFIED: C:/Users/cuqui/cs1710/forge/forge/examples/basic/gameOfLife.frg; C:/Users/cuqui/cs1710/forge/forge/examples/oopsla24/goat_cabbage_wolf.frg]

The planner should treat strict deferred post-selection as the load-bearing semantic rule: inside one circuit epoch, `finish` does not free ancilla; only terminal post-selection may move modes/blocks to `releasable`, then `free`. Under that structural interpretation, a same-trace allocation of block 0 to pair `(2,3)` after pair `(0,1)` has finished but before terminal post-selection is intentionally unsafe, even though Phase 22's numerical Perceval probe found pooled and dedicated n=4 vertex-disjoint distributions indistinguishable within the pre-committed tolerance. [VERIFIED: .planning/phases/23-ancilla-lifecycle-safety-formal-verification/23-CONTEXT.md; results/phase22_reuse_gate.md]

**Primary recommendation:** implement Phase 23 as a small, witness-oriented trace model at `n=4`, with separate test blocks for (1) unsafe same-epoch reuse trace exists, (2) safety forbids live reallocation, (3) safe cross-epoch reuse trace exists after terminal release, and (4) a reporting artifact explicitly compares this structural result to Phase 22's numerical GO without reconciling by assumption. [VERIFIED: .planning/phases/23-ancilla-lifecycle-safety-formal-verification/23-CONTEXT.md]

## Project Constraints (from AGENTS.md)

- Use `venv/Scripts/python.exe` for Python commands in this repo; system Python may lack project dependencies. [VERIFIED: AGENTS.md]
- The canonical full Python test command is `venv/Scripts/python.exe -m pytest -q`; `pytest.ini` sets `testpaths = tests`. [VERIFIED: AGENTS.md; pytest.ini]
- Run Forge files with `racket file.frg`, not `raco forge`; local Phase 16/22 evidence uses this invocation. [VERIFIED: .planning/STATE.md; forge/ancilla_mapping.frg]
- Use `option run_sterling off` in Forge files to avoid Windows Sterling visualizer hangs. [VERIFIED: forge/ancilla_mapping.frg; forge/pooled_ancilla_allocation.frg]
- Preserve the owner's explainability boundary: formal models may specify and check, but interpretation of quantum/physics significance must remain explicit and owner-reviewable. [VERIFIED: AGENTS.md]
- Do not implement Python k-pair circuits or rerun hardness-under-loss in this phase. [VERIFIED: .planning/REQUIREMENTS.md]

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Lifecycle state machine | Formal verification (Forge) | Specification docs | The phase is a bounded relational model of allocation/use/release traces. [VERIFIED: .planning/ROADMAP.md] |
| Static minimum block count | Existing Phase 22 artifacts | Phase 23 report | Phase 23 must cite Phase 22's static K, not search for a new joint K. [VERIFIED: .planning/phases/23-ancilla-lifecycle-safety-formal-verification/23-CONTEXT.md] |
| Numerical pooled-vs-dedicated physics | Existing Perceval script/report | Phase 23 cross-check | Forge cannot evaluate amplitudes/probabilities; Phase 22's `mpair07_reuse_check.py` owns that evidence. [VERIFIED: results/phase22_reuse_gate.md] |
| Witness translation table | Python or manual result tooling | Forge raw instance | LIFE-02/D-10 require a human-readable trace table in addition to raw solver output. [VERIFIED: .planning/phases/23-ancilla-lifecycle-safety-formal-verification/23-CONTEXT.md] |
| Final public/spec write-up | `docs/iqp-photonic-encoding.md` | `results/phase23_lifecycle_summary.md` | LIFE-07 requires documentation beside Phase 22's existing section. [VERIFIED: .planning/REQUIREMENTS.md; docs/iqp-photonic-encoding.md] |

## Standard Stack

### Core

| Tool | Version | Purpose | Why Standard |
|------|---------|---------|--------------|
| Racket | 8.15 [cs] | Host runtime for `#lang forge` files. | Local command `racket --version` returned `Welcome to Racket v8.15 [cs].` [VERIFIED: local command] |
| Forge | 5.2 | Relational bounded model finder. | `racket forge/ancilla_mapping.frg` printed `Forge version: 5.2` and both tests passed. [VERIFIED: local command] |
| Python | 3.12.1 | Optional trace-table parsing/report tooling and existing project tests. | Local command `venv/Scripts/python.exe --version` returned `Python 3.12.1`. [VERIFIED: local command] |
| pytest | 9.1.1 | Existing Python test framework if helper tooling is added. | Local command `venv/Scripts/python.exe -m pytest --version` returned `pytest 9.1.1`. [VERIFIED: local command] |

### Supporting

| Tool/File | Version | Purpose | When to Use |
|-----------|---------|---------|-------------|
| `forge/pooled_ancilla_allocation.frg` | Existing Phase 22 artifact | Static allocation baseline: `Pair`, `Alloc`, `Config`, `conflicts`, bitwidth, `test expect` style. | Reuse concepts and syntax, not the file itself. [VERIFIED: forge/pooled_ancilla_allocation.frg] |
| `forge/ancilla_mapping.frg` | Existing Phase 16 artifact | Small two-part `sat`/`unsat` Forge discipline. | Template for non-vacuity and no-counterexample checks. [VERIFIED: forge/ancilla_mapping.frg] |
| `results/phase22_reuse_gate.md` | Existing Phase 22 artifact | Numerical MPAIR-07 pooled-vs-dedicated comparison. | Required input to LIFE-05 cross-check. [VERIFIED: results/phase22_reuse_gate.md] |

### Alternatives Considered

| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| Explicit relational `State` snapshots | `#lang forge/temporal` | Rejected by locked D-01; do not reopen. [VERIFIED: .planning/phases/23-ancilla-lifecycle-safety-formal-verification/23-CONTEXT.md] |
| One bounded `State.next` trace | Duplicated named states per depth | Rejected by locked D-02; duplication would make configurable depth brittle. [VERIFIED: .planning/phases/23-ancilla-lifecycle-safety-formal-verification/23-CONTEXT.md] |
| Same-trace reuse as safe witness | Cross-epoch reuse after terminal post-selection | Same-trace strict-liveness reuse is intentionally unsafe; LIFE-04 safe reuse must be cross-epoch. [VERIFIED: .planning/phases/23-ancilla-lifecycle-safety-formal-verification/23-CONTEXT.md] |

**Installation:** no new packages. Use the existing tools.

```powershell
racket forge/ancilla_lifecycle_safety.frg
venv/Scripts/python.exe -m pytest tests/test_lifecycle_trace_report.py -q
```

## Package Legitimacy Audit

Not applicable. This phase installs no external packages; it uses already-installed Racket/Forge and the repository Python environment. [VERIFIED: local command; AGENTS.md]

## Architecture Patterns

### System Architecture Diagram

```text
Phase 22 artifacts
  |-- static K / block formula ----------------------.
  |-- MPAIR-07 numerical GO --------------------.    |
                                                v    v
Forge lifecycle model -> raw sat/unsat witnesses -> trace table/report -> docs section
        |
        |-- unsafe same-epoch query: allocate pair A -> finish A -> allocate pair B before final postselection
        |
        `-- safe cross-epoch query: epoch A terminal release -> block free -> epoch B allocate
```

### Recommended Project Structure

```text
forge/
├── ancilla_mapping.frg                 # existing Phase 16 single-pair mapping check
├── pooled_ancilla_allocation.frg       # existing Phase 22 static block-allocation search
└── ancilla_lifecycle_safety.frg        # new Phase 23 lifecycle trace model

results/
├── phase22_reuse_gate.md               # existing numerical cross-check source
├── phase22_forge_summary.md            # existing static-K source
└── phase23_lifecycle_summary.md        # new structural/numerical comparison and trace table

tests/
└── test_lifecycle_trace_report.py      # only if Python report parsing/formatting is added
```

### Pattern 1: Explicit Bounded Trace With `next`

**What:** Model trace order with `State.next` or `Trace.nextState`, constrain it linear per run, and use transitive closure to reason about reachability through the trace. [VERIFIED: C:/Users/cuqui/cs1710/forge/forge/examples/basic/gameOfLife.frg; C:/Users/cuqui/cs1710/forge/forge/examples/oopsla24/goat_cabbage_wolf.frg]

**When to use:** Phase 23 should use this for "up to N gate steps" and shortest unsafe trace discovery. [VERIFIED: .planning/phases/23-ancilla-lifecycle-safety-formal-verification/23-CONTEXT.md]

```forge
#lang forge
option run_sterling off

sig State {
    next: lone State,
    freeModes: set Mode,
    allocatedModes: set Mode,
    inUseModes: set Mode,
    releasableModes: set Mode,
    event: lone Event,
    gate: lone Gate
}

one sig Trace {
    first: one State
}

pred wellFormedTrace {
    no next.(Trace.first)
    one last: State | no last.next
    all s: State | s not in s.^next
}

run { wellFormedTrace } for 7 Int, 8 State for {next is linear}
```

### Pattern 2: Resource State Partition

**What:** Each mode belongs to exactly one lifecycle set in each state; each block's aggregate status is derived or checked against its four modes. [VERIFIED: stop_and_copy.frg and mark_and_sweep.frg use state-indexed sets; Phase 23 D-04 requires mode plus block tracking]

**When to use:** Use this in every state, not only in event states, to catch unconstrained-state vacuity. [VERIFIED: C:/Users/cuqui/cs1710/hw/cs1710-memory-management-alejack312/stop_and_copy.frg]

```forge
pred modePartition[s: State] {
    Mode = s.freeModes + s.allocatedModes + s.inUseModes + s.releasableModes
    no s.freeModes & s.allocatedModes
    no s.freeModes & s.inUseModes
    no s.freeModes & s.releasableModes
    no s.allocatedModes & s.inUseModes
    no s.allocatedModes & s.releasableModes
    no s.inUseModes & s.releasableModes
}

pred blockLive[s: State, b: Block] {
    some b.modes & (s.allocatedModes + s.inUseModes + s.releasableModes)
}
```

### Pattern 3: Event-Tagged Transitions

**What:** Encode `allocate`, `begin/use`, `finish`, `postselect`, and `release/free` as explicit transition predicates between adjacent states. [VERIFIED: stop_and_copy.frg uses named transition predicates such as `InitialToChanged`, `ChangedToCopy`, and `CopyToFlipped`]

**When to use:** Use this to make the clobber point visible: the unsafe trace should show a second `allocate` event while block 0 is still live from the first gate. [VERIFIED: .planning/phases/23-ancilla-lifecycle-safety-formal-verification/23-CONTEXT.md]

```forge
abstract sig Event {}
one sig Allocate, BeginUse, FinishGate, FinalPostselect, Release extends Event {}

pred allocateTransition[s, s2: State, g: Gate] {
    s2.event = Allocate
    s2.gate = g
    g.block.modes in s.freeModes
    s2.allocatedModes = s.allocatedModes + g.block.modes
    s2.freeModes = s.freeModes - g.block.modes
    s2.inUseModes = s.inUseModes
    s2.releasableModes = s.releasableModes
}

pred finishStrictDeferred[s, s2: State, g: Gate] {
    s2.event = FinishGate
    s2.gate = g
    -- strict deferred post-selection: finishing a gate does not free modes
    s2.inUseModes = s.inUseModes
    s2.releasableModes = s.releasableModes
    s2.freeModes = s.freeModes
}
```

### Pattern 4: Separate Unsafe Trace From Safety Assertion

**What:** Provide a satisfiable query that demonstrates the unsafe same-trace scenario and an unsatisfiable safety query showing no trace satisfies the safe protocol plus live reallocation. [VERIFIED: `forge/ancilla_mapping.frg` and `forge/pooled_ancilla_allocation.frg` use paired `sat` non-vacuity and `unsat` counterexample checks]

**When to use:** Required because LIFE-02 asks for a trace counterexample and LIFE-04 asks for a safe non-vacuous witness. [VERIFIED: .planning/REQUIREMENTS.md]

```forge
pred liveReallocation {
    some disj g1, g2: Gate | {
        g1.block = g2.block
        not conflicts[g1.pair, g2.pair] -- vertex-disjoint, isolates lifecycle failure
        some s: State | {
            s.event = Allocate
            s.gate = g2
            blockLive[s, g1.block]
        }
    }
}

test expect {
    unsafeSameEpochWitness: {
        n4Domain
        wellFormedTrace
        strictDeferredEpoch
        liveReallocation
    } for 7 Int, exactly 8 State, exactly 2 Gate, exactly 4 Mode, exactly 1 Block is sat

    noReallocationUnderSafeProtocol: {
        n4Domain
        wellFormedTrace
        safeProtocol
        liveReallocation
    } for 7 Int, exactly 8 State, exactly 2 Gate, exactly 4 Mode, exactly 1 Block is unsat
}
```

### Anti-Patterns to Avoid

- **Freeing at `finish`:** This contradicts strict deferred post-selection and would erase the whole LIFE-03 question. [VERIFIED: .planning/phases/23-ancilla-lifecycle-safety-formal-verification/23-CONTEXT.md]
- **Only tracking blocks:** This can miss individual-mode clobbering, contrary to D-04. [VERIFIED: .planning/phases/23-ancilla-lifecycle-safety-formal-verification/23-CONTEXT.md]
- **Only tracking modes:** This loses the Phase 22 block allocation unit, contrary to D-04 and LIFE-06. [VERIFIED: .planning/phases/23-ancilla-lifecycle-safety-formal-verification/23-CONTEXT.md]
- **Treating Phase 22 numerical GO as a proof of lifecycle safety:** Perceval and Forge answer different abstractions; D-13 requires unresolved disagreement to remain explicit. [VERIFIED: results/phase22_reuse_gate.md; .planning/phases/23-ancilla-lifecycle-safety-formal-verification/23-CONTEXT.md]
- **Reusing Phase 22's search model in place:** Phase 23 should add a new model file and leave `forge/pooled_ancilla_allocation.frg` unchanged. [VERIFIED: .planning/phases/23-ancilla-lifecycle-safety-formal-verification/23-CONTEXT.md]

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Ordered bounded traces | A custom ad hoc list encoding with separate named states per depth | `State.next`, `Trace.first`, acyclicity, and `for {next is linear}` | Local Forge examples already provide the idiom and it supports configurable state bounds. [VERIFIED: gameOfLife.frg; goat_cabbage_wolf.frg] |
| Static allocation minimum-K search | A new joint lifecycle/coloring optimizer | Phase 22's existing `results/phase22_forge_summary.md` and `pooled_allocation_baseline.py` | D-12 forbids searching for a joint new minimum K in Phase 23. [VERIFIED: .planning/phases/23-ancilla-lifecycle-safety-formal-verification/23-CONTEXT.md] |
| Quantum amplitude equivalence | A Forge predicate pretending to compare physical circuit output | Existing Phase 22 Perceval evidence and explicit scope statement | Forge has no complex amplitudes, probabilities, or Fock-space semantics. [VERIFIED: results/phase22_reuse_gate.md] |
| Lifecycle report parsing | Large custom framework | Small Python stdlib helper only if needed | Phase 22's report/baseline tooling stays standalone and stdlib-only. [VERIFIED: pooled_allocation_baseline.py] |

**Key insight:** Phase 23 is where Forge's trace/reachability value finally engages. Do not dilute it by turning the phase back into another static coloring search or by asking Forge to validate numerical physics. [VERIFIED: results/phase22_forge_summary.md; .planning/REQUIREMENTS.md]

## Common Pitfalls

### Pitfall 1: Acyclic But Not Linear Trace

**What goes wrong:** `next: lone State` permits disconnected states or multiple starts unless constrained. [VERIFIED: gameOfLife.frg uses separate constraints for first/last/no cycles and `for {next is linear}`]

**Why it happens:** A field multiplicity says each state has at most one successor; it does not by itself say all states form one bounded trace. [VERIFIED: gameOfLife.frg]

**How to avoid:** Use a `Trace.first` handle, no predecessor for first, one last, no cycles, transition predicates for every `s.next`, and `for {next is linear}` on run/witness commands. [VERIFIED: gameOfLife.frg; goat_cabbage_wolf.frg]

**Warning signs:** A `sat` witness where only one or two states participate and the rest are unconstrained.

### Pitfall 2: Finish Accidentally Frees Modes

**What goes wrong:** A textbook allocator model would free or collect after use, making same-trace reuse appear safe. [VERIFIED: mark_and_sweep.frg frees during sweep; Phase 23 D-06 says CP modes remain live until terminal post-selection]

**Why it happens:** The memory-management analogy is useful, but CP(alpha) deferred post-selection is stricter than ordinary garbage collection. [VERIFIED: .planning/phases/23-ancilla-lifecycle-safety-formal-verification/23-CONTEXT.md]

**How to avoid:** Encode `finish` as "no longer applying the gate" but still live, then require explicit terminal `FinalPostselect -> Release -> Free`. [VERIFIED: .planning/phases/23-ancilla-lifecycle-safety-formal-verification/23-CONTEXT.md]

**Warning signs:** A safe same-epoch reuse witness appears before final post-selection.

### Pitfall 3: Non-Vacuity Uses Unsafe Reuse

**What goes wrong:** LIFE-04 requires reuse conjoined with safety, but D-07/D-08 also require unsafe reuse as a separate trace. Combining them into one witness makes the requirement impossible or meaningless. [VERIFIED: .planning/REQUIREMENTS.md; .planning/phases/23-ancilla-lifecycle-safety-formal-verification/23-CONTEXT.md]

**How to avoid:** Use two witness predicates: `unsafeSameEpochWitness` is `sat` and deliberately violates the safe protocol; `safeCrossEpochReuseWitness` is `sat` and includes final release before reuse. [VERIFIED: .planning/phases/23-ancilla-lifecycle-safety-formal-verification/23-CONTEXT.md]

**Warning signs:** A single `nonVacuous` predicate tries to prove both unsafe clobbering and safe reuse.

### Pitfall 4: Bitwidth Copied Without Recomputing

**What goes wrong:** Forge integer overflow silently corrupts arithmetic if a model computes mode indices outside the signed range. [VERIFIED: forge/pooled_ancilla_allocation.frg]

**How to avoid:** Start with `for 7 Int`, because Phase 22's n=8/block formula reached mode index 43 and documented `for 6 Int` overflow risk. Recompute if the Phase 23 model introduces epoch IDs, event indices, or more state-count arithmetic. [VERIFIED: results/phase22_allocation_invariant.md; forge/pooled_ancilla_allocation.frg]

**Warning signs:** A planner copies `for 6 Int` from `ancilla_mapping.frg`.

### Pitfall 5: Cross-Check Reconciled By Assumption

**What goes wrong:** The strict lifecycle model will likely say same-epoch reuse is unsafe, while Phase 22's n=4 Perceval comparison says pooled/dedicated are numerically indistinguishable at that bounded instance. [VERIFIED: results/phase22_reuse_gate.md; .planning/phases/23-ancilla-lifecycle-safety-formal-verification/23-CONTEXT.md]

**How to avoid:** Report the mismatch as abstraction divergence: Forge checks declared liveness discipline; Perceval checks a specific physical output distribution. D-13 says not to choose a universal winner. [VERIFIED: .planning/phases/23-ancilla-lifecycle-safety-formal-verification/23-CONTEXT.md]

**Warning signs:** Wording like "Forge disproves Phase 22" or "Perceval proves the lifecycle model wrong."

## Code Examples

### Ordered Trace Skeleton

```forge
-- Source: C:/Users/cuqui/cs1710/forge/forge/examples/basic/gameOfLife.frg
sig State {
    next: lone State,
    freeModes: set Mode,
    allocatedModes: set Mode,
    inUseModes: set Mode,
    releasableModes: set Mode
}

one sig Trace {
    first: one State
}

pred findTrace {
    one last: State | no last.next
    no next.(Trace.first)
    all s: State | s not in s.^next
}

run { findTrace } for 7 Int, 8 State for {next is linear}
```

### Phase 22 Compatibility Reuse

```forge
-- Source: forge/pooled_ancilla_allocation.frg
sig Pair {
    i: one Int,
    j: one Int
}

pred conflicts[p, q: Pair] {
    p.i = q.i or p.i = q.j or p.j = q.i or p.j = q.j
}
```

### Safe Cross-Epoch Witness Shape

```forge
-- Source: derived from Phase 23 D-09, not yet implemented
pred safeCrossEpochReuseWitness {
    some disj g1, g2: Gate | {
        g1.pair.i = 0
        g1.pair.j = 1
        g2.pair.i = 2
        g2.pair.j = 3
        g1.block = Block0
        g2.block = Block0
        terminalReleaseBeforeSecondAllocate[g1, g2]
        no liveReallocation
    }
}
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Judge Forge mainly by brute-force speedup | Judge this phase by trace/reachability specification value, witness quality, and precise abstraction boundaries | Phase 22 close-out / Phase 23 context, 2026-08-21 to 2026-08-22 | Planner should not manufacture a larger search to justify Forge. [VERIFIED: results/phase22_forge_summary.md; .planning/phases/23-ancilla-lifecycle-safety-formal-verification/23-CONTEXT.md] |
| Static allocation answers "pooling safety" | Split into static indexing, numerical physics, and lifecycle liveness | Phase 23 context | LIFE-05/06 must compare, not conflate, these layers. [VERIFIED: .planning/phases/23-ancilla-lifecycle-safety-formal-verification/23-CONTEXT.md] |
| Named state snapshots only (`Initial`, `Changed`, etc.) | Configurable bounded `State.next` trace | Phase 23 D-02 | Keeps owner CS1710 inspectability while supporting shortest unsafe trace search. [VERIFIED: stop_and_copy.frg; gameOfLife.frg] |

**Deprecated/outdated:**
- `raco forge`: not the invocation used in this repo; use `racket path/to/file.frg`. [VERIFIED: .planning/STATE.md; local command]
- `for 6 Int` copied from Phase 16: unsafe for Phase 22's pooled mode arithmetic and should not be copied into Phase 23 without recomputation. [VERIFIED: forge/pooled_ancilla_allocation.frg]
- Any claim that Phase 22's Forge file proves physical reuse safety: Phase 22 explicitly scopes that out. [VERIFIED: results/phase22_forge_summary.md]

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The Phase 23 lifecycle model will remain tractable at `n=4` with roughly 8-10 states and two gates. [ASSUMED] | Validation Architecture | If wrong, planner must add a time-boxed bound-reduction step and report the largest converged trace. |
| A2 | A small Python helper may be useful to turn raw Forge witnesses into the D-10 human-readable table. [ASSUMED] | Architecture Patterns | If unnecessary, planner can make the trace table manually from raw Forge output; no source code helper is required. |
| A3 | `for {next is linear}` can be used on Phase 23 witness `run` commands and likely on any `test expect`/assert forms that need linear ordering. [ASSUMED] | Architecture Patterns | If Forge rejects it inside `test expect`, use explicit linearity constraints (`one first`, `one last`, no cycles, connectedness) in the predicates. |

## Open Questions

1. **Exact state bound for the first implementation run**
   - What we know: minimum meaningful unsafe witness needs two gate protocols; safe witness needs two epochs. [VERIFIED: .planning/phases/23-ancilla-lifecycle-safety-formal-verification/23-CONTEXT.md]
   - What's unclear: whether 8, 10, or 12 `State` atoms gives the cleanest minimal trace after explicit `allocate -> begin/use -> finish -> postselect -> release/free` events.
   - Recommendation: start with 8 states for unsafe same-epoch witness and 10-12 for safe cross-epoch witness; record the exact bound that produces readable traces. [ASSUMED]

2. **Raw witness extraction workflow**
   - What we know: D-10 requires raw Forge witness plus human-readable table. [VERIFIED: .planning/phases/23-ancilla-lifecycle-safety-formal-verification/23-CONTEXT.md]
   - What's unclear: whether CLI output alone is enough or whether Sterling/offline instance export is needed.
   - Recommendation: first keep `option run_sterling off` and copy the raw satisfying instance output if Forge prints enough detail; if not, add a tiny hand-authored table from the known witness predicates. [ASSUMED]

## Environment Availability

| Dependency | Required By | Available | Version | Fallback |
|------------|-------------|-----------|---------|----------|
| Racket | Running `.frg` files | yes | 8.15 [cs] | None needed. [VERIFIED: local command] |
| Forge | Lifecycle model | yes | 5.2 | None needed. [VERIFIED: `racket forge/ancilla_mapping.frg`] |
| Python venv | Optional report helper and tests | yes | 3.12.1 | Avoid helper; write report manually if needed. [VERIFIED: local command] |
| pytest | Optional helper tests | yes | 9.1.1 | Forge-only validation if no helper code is added. [VERIFIED: local command] |
| Graphify | Graph context | no | disabled | Continue from explicit local artifacts. [VERIFIED: `gsd-tools graphify status`] |

**Missing dependencies with no fallback:** none.

**Missing dependencies with fallback:** graphify is disabled; research used direct artifact reads instead. [VERIFIED: `gsd-tools graphify status`]

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | Forge v5.2 for model checks; pytest 9.1.1 only if Python helper code is added. [VERIFIED: local command] |
| Config file | `pytest.ini` with `testpaths = tests` for Python tests; no Forge test config. [VERIFIED: pytest.ini] |
| Quick run command | `racket forge/ancilla_lifecycle_safety.frg` |
| Full suite command | `racket forge/ancilla_lifecycle_safety.frg`; plus `venv/Scripts/python.exe -m pytest tests/test_lifecycle_trace_report.py -q` if helper code exists. |

### Phase Requirements -> Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|--------------|
| LIFE-01 | Lifecycle states exist and transitions cover allocate/begin/finish/postselect/release. | Forge `sat` witness plus predicate review | `racket forge/ancilla_lifecycle_safety.frg` | no - Wave 0 |
| LIFE-02 | Live mode/block cannot be reallocated under safe protocol; unsafe trace can be exhibited separately. | Forge `unsat` safety check and `sat` unsafe witness | `racket forge/ancilla_lifecycle_safety.frg` | no - Wave 0 |
| LIFE-03 | No mid-circuit collection; only final post-selection creates releasable/free state. | Forge `unsat` check for early free/release | `racket forge/ancilla_lifecycle_safety.frg` | no - Wave 0 |
| LIFE-04 | Safe witness with at least two gates and genuine reuse exists. | Forge `sat` cross-epoch witness | `racket forge/ancilla_lifecycle_safety.frg` | no - Wave 0 |
| LIFE-05 | Structural verdict compared to Phase 22 numerical GO. | Report check | `rg -n "Phase 22|tvd_pooled_vs_dedicated|structural" results/phase23_lifecycle_summary.md` | no - Wave 0 |
| LIFE-06 | Temporal constraint effect on Phase 22 static K stated. | Report check | `rg -n "minimum|K|temporal|static" results/phase23_lifecycle_summary.md docs/iqp-photonic-encoding.md` | no - Wave 0 |
| LIFE-07 | Docs section added with what model does/does not establish. | Documentation check | `rg -n "Lifecycle|Phase 23|does not establish" docs/iqp-photonic-encoding.md` | no - Wave 0 |

### Sampling Rate

- **Per task commit:** run `racket forge/ancilla_lifecycle_safety.frg` after every model edit.
- **Per wave merge:** run the Forge file plus any focused helper pytest file.
- **Phase gate:** Forge checks pass, `results/phase23_lifecycle_summary.md` contains raw/verbal witness material, and docs state the abstraction boundary.

### Wave 0 Gaps

- [ ] `forge/ancilla_lifecycle_safety.frg` - new model for LIFE-01..04.
- [ ] `results/phase23_lifecycle_summary.md` - raw witness, trace table, Phase 22 cross-check, and LIFE-06 statement.
- [ ] `docs/iqp-photonic-encoding.md` Phase 23 section - LIFE-07.
- [ ] `tests/test_lifecycle_trace_report.py` - only if a Python trace/report helper is implemented.

## Security Domain

This phase is local formal-methods work with no network service, no authentication, no user data, and no runtime input surface. [VERIFIED: .planning/phases/23-ancilla-lifecycle-safety-formal-verification/23-CONTEXT.md]

### Applicable ASVS Categories

| ASVS Category | Applies | Standard Control |
|---------------|---------|------------------|
| V2 Authentication | no | Not applicable. [VERIFIED: phase scope] |
| V3 Session Management | no | Not applicable. [VERIFIED: phase scope] |
| V4 Access Control | no | Not applicable. [VERIFIED: phase scope] |
| V5 Input Validation | no | No external input surface; if Python helper reads files, use fixed local paths. [ASSUMED] |
| V6 Cryptography | no | Not applicable. [VERIFIED: phase scope] |

### Known Threat Patterns for Local Research Artifacts

| Pattern | STRIDE | Standard Mitigation |
|---------|--------|---------------------|
| Misleading generated evidence | Tampering | Preserve raw Forge output and record exact commands. [VERIFIED: .planning/phases/23-ancilla-lifecycle-safety-formal-verification/23-CONTEXT.md] |
| Scope overclaim | Repudiation | Separate Forge structural claims from Perceval numerical claims in results/docs. [VERIFIED: results/phase22_reuse_gate.md] |

## Sources

### Primary (HIGH confidence)

- `.planning/phases/23-ancilla-lifecycle-safety-formal-verification/23-CONTEXT.md` - locked decisions D-01..D-14, phase scope, required artifacts.
- `.planning/ROADMAP.md` - Phase 23 goal, dependency, success criteria.
- `.planning/REQUIREMENTS.md` - LIFE-01..07 and out-of-scope boundary.
- `.planning/STATE.md` - Phase 22 close-out, Forge invocation and bitwidth cautions.
- `forge/pooled_ancilla_allocation.frg` - Phase 22 static allocation model syntax, `func Pair -> Int`, comma bounds, `for 7 Int`, non-vacuity.
- `forge/ancilla_mapping.frg` - Phase 16 `sat`/`unsat` test pattern; ran live and passed.
- `C:/Users/cuqui/cs1710/hw/cs1710-memory-management-alejack312/stop_and_copy.frg` - owner precedent for explicit `State` snapshots and liveness/reachability.
- `C:/Users/cuqui/cs1710/hw/cs1710-memory-management-alejack312/mark_and_sweep.frg` - owner precedent for mark/sweep lifecycle states and safety/cleanliness predicates.
- `C:/Users/cuqui/cs1710/forge/forge/examples/basic/gameOfLife.frg` - local Forge finite trace with `State.next`, `Trace.first`, acyclicity, and `for {next is linear}`.
- `C:/Users/cuqui/cs1710/forge/forge/examples/oopsla24/goat_cabbage_wolf.frg` - local Forge trace wrapper with `nextState: pfunc State -> State` and linear bound.
- `results/phase22_reuse_gate.md` - MPAIR-07 numerical pooled-vs-dedicated evidence and owner GO ruling.
- `results/phase22_forge_summary.md` - Phase 22 Forge-vs-baseline summary and static/lifecycle boundary.
- `results/phase22_allocation_invariant.md` - Phase 22 compatibility rule, mode formula, static K and bitwidth arithmetic.
- Local commands run 2026-08-22: `racket --version`, `racket forge/ancilla_mapping.frg`, `raco pkg show forge`, `venv/Scripts/python.exe --version`, `venv/Scripts/python.exe -m pytest --version`, `gsd-tools graphify status`.

### Secondary (MEDIUM confidence)

- None. This research intentionally stayed on local authoritative artifacts and local Forge examples.

### Tertiary (LOW confidence)

- None. Open issues are logged as assumptions/questions rather than low-confidence claims.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - all tools verified locally, and existing Forge model ran successfully.
- Architecture: HIGH - locked by Phase 23 context and local Forge trace examples.
- Pitfalls: HIGH for scope/bitwidth/invocation pitfalls already observed in Phase 16/22; MEDIUM for expected Phase 23 runtime until measured.

**Research date:** 2026-08-22  
**Valid until:** 2026-09-21 for local syntax/tooling; re-check immediately if Forge/Racket versions or Phase 23 locked decisions change.
