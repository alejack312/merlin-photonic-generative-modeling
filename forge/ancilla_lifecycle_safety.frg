#lang forge
option run_sterling off

-- Phase 23: bounded structural lifecycle model for pooled CP(alpha) ancillas.
--
-- This is an explicit State.next trace model, not #lang forge/temporal (D-01:
-- follows the owner's cs1710 stop_and_copy.frg precedent, keeps every
-- lifecycle state directly inspectable rather than hidden behind temporal
-- operators). It tracks both the four-mode allocation block and each
-- individual mode (D-04) so the allocation unit inherited from Phase 22 and
-- the no-mode-reallocation claim remain visible at the same time -- a block
-- could in principle look "allocated" while one of its own modes drifted
-- out of sync, and blockModeAgreement below is what rules that out.
--
-- The model is bounded: a satisfying or violating trace is evidence within
-- the declared scope, not an unbounded theorem. It does not verify a Python
-- k-pair implementation, photonic amplitudes, physical unitary equivalence,
-- or the hardness-under-loss study.
--
-- BITWIDTH NOTE: `for 7 Int` sets Forge's Int bitwidth (signed range
-- [-64,63]), not a state or Pair count. This model's own arithmetic never
-- exceeds the Pair index range (i,j < 4 at n=4), so the value actually
-- needed here is tiny. `for 7 Int` is carried forward from
-- pooled_ancilla_allocation.frg's Phase 22 precedent (its n=8 mode-index
-- formula reached 43, which needs `for 7 Int` to avoid silent overflow) as
-- a deliberately conservative starting bitwidth, per 23-RESEARCH.md's
-- Pitfall 4 ("Bitwidth Copied Without Recomputing" -- explicitly flagging
-- that a *narrower* bitwidth copied from ancilla_mapping.frg's `for 6 Int`
-- would be the actual mistake to avoid here, not that `for 7 Int` needed
-- fresh justification of its own). Recompute if a future extension adds
-- epoch IDs, event indices, or other integer-valued state that could grow
-- past this range.

-- The six lifecycle events a gate's ancilla block/modes pass through.
-- Allocate/BeginUse/FinishGate follow D-05's explicit allocate -> begin/use
-- -> finish expansion of one gate's protocol; FinalPostselect/Release add
-- D-06's strict deferred-liveness tail (in-use -> releasable -> free) so a
-- block cannot be collected before the circuit's terminal post-selection.
abstract sig Event {}
one sig Start, Allocate, BeginUse, FinishGate, FinalPostselect, Release
    extends Event {}

-- One CP(alpha) qubit pair, mirroring Phase 22's Pair sig
-- (pooled_ancilla_allocation.frg) so the two models stay comparable.
sig Pair {
    i: one Int,
    j: one Int
}

-- Individual ancilla mode. Tracked separately from Block (below) per D-04,
-- purely so the no-mode-reallocation property has something mode-grained
-- to state; Mode carries no other structure of its own.
sig Mode {}

-- The pooled four-mode allocation unit inherited from Phase 22 -- the thing
-- that actually gets allocated/reused, with `modes` as the fixed set of
-- individual Mode atoms it owns (see blockAndModeDomains's `#b.modes = 4`).
sig Block {
    modes: set Mode
}

-- One application of a CP(alpha) gate: which qubit pair it acts on, and
-- which ancilla block it was assigned. `pair` and `block` are fixed per
-- Gate atom -- a Gate does not change which block it uses mid-trace, only
-- the *lifecycle status* of that block changes as the trace advances.
sig Gate {
    pair: one Pair,
    block: one Block
}

-- One explicit snapshot in the trace (D-01/D-02). Each State carries both
-- block-level and mode-level status sets in parallel -- freeBlocks/
-- allocatedBlocks/inUseBlocks/releasableBlocks alongside the equivalent
-- Mode sets -- so blockModeAgreement can check the two granularities never
-- drift apart, and activePair/activeBlock record which Gate the current
-- event (if any) is about.
sig State {
    next: lone State,
    event: one Event,
    activePair: lone Pair,
    activeBlock: lone Block,

    freeBlocks: set Block,
    allocatedBlocks: set Block,
    inUseBlocks: set Block,
    releasableBlocks: set Block,

    freeModes: set Mode,
    allocatedModes: set Mode,
    inUseModes: set Mode,
    releasableModes: set Mode
}

-- The single ordered execution being modeled: one trace with a `next`
-- chain and a configurable finite depth (D-02/D-03), not a family of
-- fixed-depth sigs duplicated per scenario.
one sig Trace {
    first: one State
}

-- Pins the shared n=4 structural domain: each Block owns exactly 4 modes,
-- every Mode belongs to exactly one Block, blocks partition Mode with no
-- overlap, and every Gate's Pair indices are in range for n=4. Combined
-- with n4Pairs below and the `exactly N` bound clauses in each test block,
-- this fixes the atom counts the test suite runs against (D-14: n=4 is the
-- smallest domain containing two vertex-disjoint pairs that can share a
-- block).
pred blockAndModeDomains {
    all b: Block | #b.modes = 4
    Mode = Block.modes
    all disj b1, b2: Block | no b1.modes & b2.modes
    all g: Gate | {
        g.pair.i >= 0
        g.pair.i < g.pair.j
        g.pair.j < 4
    }
}

-- Pins the Pair atom set to exactly K4's six edges (all six i<j pairs with
-- i,j < 4), mirroring pooled_ancilla_allocation.frg's pairsAreKn so the two
-- models' Pair semantics stay directly comparable.
pred n4Pairs {
    all p: Pair | {
        p.i >= 0
        p.i < p.j
        p.j < 4
    }
    all disj p, q: Pair | not (p.i = q.i and p.j = q.j)

    one p: Pair | p.i = 0 and p.j = 1
    one p: Pair | p.i = 0 and p.j = 2
    one p: Pair | p.i = 0 and p.j = 3
    one p: Pair | p.i = 1 and p.j = 2
    one p: Pair | p.i = 1 and p.j = 3
    one p: Pair | p.i = 2 and p.j = 3
}

-- At every well-formed state, the four lifecycle statuses (free/allocated/
-- in-use/releasable) partition Mode with no overlap -- every mode is in
-- exactly one status, matching the free -> allocated -> in-use ->
-- releasable -> free lifecycle D-05/D-06 describe.
pred modePartition[s: State] {
    Mode = s.freeModes + s.allocatedModes + s.inUseModes + s.releasableModes
    no s.freeModes & s.allocatedModes
    no s.freeModes & s.inUseModes
    no s.freeModes & s.releasableModes
    no s.allocatedModes & s.inUseModes
    no s.allocatedModes & s.releasableModes
    no s.inUseModes & s.releasableModes
}

-- Same four-way partition as modePartition, at the Block granularity.
pred blockPartition[s: State] {
    Block = s.freeBlocks + s.allocatedBlocks + s.inUseBlocks + s.releasableBlocks
    no s.freeBlocks & s.allocatedBlocks
    no s.freeBlocks & s.inUseBlocks
    no s.freeBlocks & s.releasableBlocks
    no s.allocatedBlocks & s.inUseBlocks
    no s.allocatedBlocks & s.releasableBlocks
    no s.inUseBlocks & s.releasableBlocks
}

-- Keeps the block-level and mode-level status sets in lockstep: a Block is
-- in a given status iff all four of its own modes are in the matching
-- mode-level status set. This is what makes tracking both granularities
-- (D-04) meaningful rather than two independently-driftable bookkeeping
-- systems -- without this predicate, nothing would stop a well-formed-
-- looking state from marking a block "free" while one of its modes stayed
-- "in-use".
pred blockModeAgreement[s: State] {
    all b: Block | {
        (b in s.freeBlocks) iff b.modes in s.freeModes
        (b in s.allocatedBlocks) iff b.modes in s.allocatedModes
        (b in s.inUseBlocks) iff b.modes in s.inUseModes
        (b in s.releasableBlocks) iff b.modes in s.releasableModes
    }
}

-- The full well-formedness conjunction every State in a trace must satisfy.
pred stateWellFormed[s: State] {
    modePartition[s]
    blockPartition[s]
    blockModeAgreement[s]
}

-- Structural shape of a legal trace: a single first state with no
-- predecessor, exactly one terminal state with no successor, every State
-- atom reachable from Trace.first via next (no orphan states), no cycles,
-- and every state along the way well-formed.
pred orderedTrace {
    no Trace.first.~next
    one last: State | no last.next
    State = Trace.first.*next
    all s: State | s not in s.^next
    all s: State | stateWellFormed[s]
}

-- t=0: nothing allocated yet, no gate active, every block and mode starts
-- free.
pred initialState[s: State] {
    s.event = Start
    no s.activePair
    no s.activeBlock
    s.freeBlocks = Block
    no s.allocatedBlocks
    no s.inUseBlocks
    no s.releasableBlocks
    s.freeModes = Mode
    no s.allocatedModes
    no s.inUseModes
    no s.releasableModes
}

-- Allocate event (D-05): a free block becomes allocated to gate g's pair.
-- Both the block-level and mode-level sets move together, matching
-- blockModeAgreement.
pred allocateTransition[s, s2: State, g: Gate] {
    s2.event = Allocate
    s2.activePair = g.pair
    s2.activeBlock = g.block
    g.block in s.freeBlocks

    s2.freeBlocks = s.freeBlocks - g.block
    s2.allocatedBlocks = s.allocatedBlocks + g.block
    s2.inUseBlocks = s.inUseBlocks
    s2.releasableBlocks = s.releasableBlocks

    s2.freeModes = s.freeModes - g.block.modes
    s2.allocatedModes = s.allocatedModes + g.block.modes
    s2.inUseModes = s.inUseModes
    s2.releasableModes = s.releasableModes
}

-- Begin/use event (D-05): an already-allocated block, for the same gate
-- that just allocated it, moves to in-use.
pred beginUseTransition[s, s2: State, g: Gate] {
    s2.event = BeginUse
    s2.activePair = g.pair
    s2.activeBlock = g.block
    g.block in s.allocatedBlocks
    s.activePair = g.pair
    s.activeBlock = g.block

    s2.freeBlocks = s.freeBlocks
    s2.allocatedBlocks = s.allocatedBlocks - g.block
    s2.inUseBlocks = s.inUseBlocks + g.block
    s2.releasableBlocks = s.releasableBlocks

    s2.freeModes = s.freeModes
    s2.allocatedModes = s.allocatedModes - g.block.modes
    s2.inUseModes = s.inUseModes + g.block.modes
    s2.releasableModes = s.releasableModes
}

-- Finish event (D-05/D-06): the gate itself completes, but nothing is freed
-- or released yet -- post-selection is deferred, so the block/modes stay
-- exactly in-use. This is the state D-06's strict-liveness rule is really
-- about: a naive model might be tempted to free resources the instant the
-- gate "finishes," and this predicate is written so that temptation isn't
-- even representable.
pred finishTransition[s, s2: State, g: Gate] {
    s2.event = FinishGate
    s2.activePair = g.pair
    s2.activeBlock = g.block
    s.activePair = g.pair
    s.activeBlock = g.block
    g.block in s.inUseBlocks

    -- Finishing the gate does not free anything: post-selection is deferred.
    s2.freeBlocks = s.freeBlocks
    s2.allocatedBlocks = s.allocatedBlocks
    s2.inUseBlocks = s.inUseBlocks
    s2.releasableBlocks = s.releasableBlocks
    s2.freeModes = s.freeModes
    s2.allocatedModes = s.allocatedModes
    s2.inUseModes = s.inUseModes
    s2.releasableModes = s.releasableModes
}

-- Final post-selection event (D-06): the terminal read that actually
-- resolves whether the circuit's branch survived. Only after this does the
-- block/modes leave in-use, moving to releasable rather than straight to
-- free -- release (below) is still a separate, explicit step.
pred postselectTransition[s, s2: State, g: Gate] {
    s2.event = FinalPostselect
    s2.activePair = g.pair
    s2.activeBlock = g.block
    s.activePair = g.pair
    s.activeBlock = g.block
    g.block in s.inUseBlocks

    s2.freeBlocks = s.freeBlocks
    s2.allocatedBlocks = s.allocatedBlocks
    s2.inUseBlocks = s.inUseBlocks - g.block
    s2.releasableBlocks = s.releasableBlocks + g.block
    s2.freeModes = s.freeModes
    s2.allocatedModes = s.allocatedModes
    s2.inUseModes = s.inUseModes - g.block.modes
    s2.releasableModes = s.releasableModes + g.block.modes
}

-- Release event (D-06): a releasable block/its modes return to free and
-- become available for a later gate to allocate. This is the only
-- transition that clears activePair/activeBlock, since after release no
-- gate owns the block anymore.
pred releaseTransition[s, s2: State, g: Gate] {
    s2.event = Release
    s.activePair = g.pair
    s.activeBlock = g.block
    g.block in s.releasableBlocks
    no s2.activePair
    no s2.activeBlock

    s2.freeBlocks = s.freeBlocks + g.block
    s2.allocatedBlocks = s.allocatedBlocks
    s2.inUseBlocks = s.inUseBlocks
    s2.releasableBlocks = s.releasableBlocks - g.block
    s2.freeModes = s.freeModes + g.block.modes
    s2.allocatedModes = s.allocatedModes
    s2.inUseModes = s.inUseModes
    s2.releasableModes = s.releasableModes - g.block.modes
}

-- The safe protocol's only legal moves: one state may advance to the next
-- only via one of the five named lifecycle events above, for some gate g.
pred validTransition[s, s2: State] {
    some g: Gate | {
        allocateTransition[s, s2, g]
        or beginUseTransition[s, s2, g]
        or finishTransition[s, s2, g]
        or postselectTransition[s, s2, g]
        or releaseTransition[s, s2, g]
    }
}

-- This transition intentionally models the unsafe counterexample: it allows
-- allocation of a block that is still allocated/in-use/releasable and clobbers
-- its old lifecycle status. The trace retains the exact source state and
-- second gate so the violation is inspectable rather than a scalar assertion.
pred unsafeAllocateTransition[s, s2: State, g: Gate] {
    s2.event = Allocate
    s2.activePair = g.pair
    s2.activeBlock = g.block
    g.block in s.allocatedBlocks + s.inUseBlocks + s.releasableBlocks

    s2.freeBlocks = s.freeBlocks - g.block
    s2.allocatedBlocks = s.allocatedBlocks + g.block
    s2.inUseBlocks = s.inUseBlocks - g.block
    s2.releasableBlocks = s.releasableBlocks - g.block
    s2.freeModes = s.freeModes - g.block.modes
    s2.allocatedModes = s.allocatedModes + g.block.modes
    s2.inUseModes = s.inUseModes - g.block.modes
    s2.releasableModes = s.releasableModes - g.block.modes
}

-- A trace that only ever takes the protocol's legal (validTransition) moves
-- -- what an actual, correctly-implemented pipeline would produce.
pred safeTrace {
    initialState[Trace.first]
    all s: State | some s.next implies validTransition[s, s.next]
}

-- A trace where every step is either a legal move OR the unsafe
-- reallocation -- used to search for whether an unsafe move is reachable
-- at all (D-08), separately from asking whether it's reachable *under the
-- safe protocol* (noLiveReallocationUnderSafeProtocol, in the test block
-- below uses safeTrace, not this predicate).
pred unsafeTrace {
    initialState[Trace.first]
    all s: State | some s.next implies {
        validTransition[s, s.next]
        or (some g: Gate | unsafeAllocateTransition[s, s.next, g])
    }
}

-- D-08's primary unsafe shape: two vertex-disjoint pairs (0,1) and (2,3)
-- assigned the same block, where the second allocation happens right after
-- the first gate's FinishGate -- i.e. before that gate's own terminal
-- post-selection has run. This isolates a lifecycle-liveness failure from
-- the already-known, unrelated failure mode of two pairs sharing a qubit
-- index (Phase 22's conflicts predicate; not modeled here since these two
-- pairs are already vertex-disjoint).
pred unsafeSameEpochReuse {
    some disj g1, g2: Gate | {
        g1.pair.i = 0
        g1.pair.j = 1
        g2.pair.i = 2
        g2.pair.j = 3
        g1.block = g2.block
        some s, s2: State | {
            s.next = s2
            s.event = FinishGate
            s2.event = Allocate
            s.activeBlock = g1.block
            s2.activeBlock = g2.block
            g1.block in s.inUseBlocks
            unsafeAllocateTransition[s, s2, g2]
        }
    }
}

-- D-09's safe non-vacuous witness shape: the same block, same two
-- vertex-disjoint pairs as unsafeSameEpochReuse, but this time the first
-- gate reaches Release (freeing the block) strictly before the second
-- gate's Allocate -- reuse across two fully-separated epochs, which the
-- safe protocol permits.
pred safeCrossEpochReuse {
    some disj g1, g2: Gate | {
        g1.pair.i = 0
        g1.pair.j = 1
        g2.pair.i = 2
        g2.pair.j = 3
        g1.block = g2.block
        some sRelease, sAllocate: State | {
            sRelease.next = sAllocate
            sRelease.event = Release
            no sRelease.activeBlock
            sAllocate.event = Allocate
            sAllocate.activeBlock = g2.block
            g2.block in sAllocate.allocatedBlocks
            g2.block in sRelease.freeBlocks
            validTransition[sRelease, sAllocate]
        }
    }
}

-- Pins the unsafe witness to one exact 9-state event skeleton (via `let`
-- over the next-chain) so the counterexample Forge returns is the specific
-- shape D-08 describes -- first gate runs allocate/begin/finish, second
-- gate's allocate clobbers it -- rather than some other, less legible
-- unsafe trace the solver could otherwise return.
pred unsafeEventSequence {
    let s0 = Trace.first,
        s1 = Trace.first.next,
        s2 = Trace.first.next.next,
        s3 = Trace.first.next.next.next,
        s4 = Trace.first.next.next.next.next,
        s5 = Trace.first.next.next.next.next.next,
        s6 = Trace.first.next.next.next.next.next.next,
        s7 = Trace.first.next.next.next.next.next.next.next,
        s8 = Trace.first.next.next.next.next.next.next.next.next | {
        s0.event = Start
        s1.event = Allocate
        s2.event = BeginUse
        s3.event = FinishGate
        s4.event = Allocate
        s5.event = BeginUse
        s6.event = FinishGate
        s7.event = FinalPostselect
        s8.event = Release
        no s8.next
    }
}

-- Pins the safe witness to one exact 9-state event skeleton, matching
-- D-09's shape: the first gate runs its full lifecycle through
-- release/free, then the second gate allocates the same block in the
-- following epoch.
pred safeEventSequence {
    let s0 = Trace.first,
        s1 = Trace.first.next,
        s2 = Trace.first.next.next,
        s3 = Trace.first.next.next.next,
        s4 = Trace.first.next.next.next.next,
        s5 = Trace.first.next.next.next.next.next,
        s6 = Trace.first.next.next.next.next.next.next,
        s7 = Trace.first.next.next.next.next.next.next.next,
        s8 = Trace.first.next.next.next.next.next.next.next.next | {
        s0.event = Start
        s1.event = Allocate
        s2.event = BeginUse
        s3.event = FinishGate
        s4.event = FinalPostselect
        s5.event = Release
        s6.event = Allocate
        s7.event = BeginUse
        s8.event = FinishGate
        no s8.next
    }
}

-- Bundles the two domain-shaping predicates (blockAndModeDomains, n4Pairs)
-- so every test block below shares the exact same n=4 scope (D-14) instead
-- of restating both calls three times.
pred n4LifecycleDomain {
    blockAndModeDomains
    n4Pairs
}

test expect {
    -- The unsafe witness contains two vertex-disjoint pairs, the same block,
    -- and the second allocation before terminal post-selection. It is SAT as
    -- an exhibited trace-shaped counterexample, not a safety approval.
    unsafeSameEpochWitness: {
        n4LifecycleDomain
        orderedTrace
        unsafeTrace
        unsafeEventSequence
        unsafeSameEpochReuse
    } for 7 Int, exactly 6 Pair, exactly 4 Mode, exactly 1 Block,
        exactly 2 Gate, exactly 9 State is sat

    -- The valid protocol cannot contain a live reallocation. This is UNSAT;
    -- the preceding SAT query is the separate counterexample existence claim.
    noLiveReallocationUnderSafeProtocol: {
        n4LifecycleDomain
        orderedTrace
        safeTrace
        unsafeSameEpochReuse
    } for 7 Int, exactly 6 Pair, exactly 4 Mode, exactly 1 Block,
        exactly 2 Gate, exactly 9 State is unsat

    -- The safe non-vacuous witness uses two gates and reuses block 0 only after
    -- final post-selection and explicit release/free in a later epoch.
    safeCrossEpochReuseWitness: {
        n4LifecycleDomain
        orderedTrace
        safeTrace
        safeEventSequence
        safeCrossEpochReuse
    } for 7 Int, exactly 6 Pair, exactly 4 Mode, exactly 1 Block,
        exactly 2 Gate, exactly 9 State is sat
}
