#lang forge
option run_sterling off

-- Phase 23: bounded structural lifecycle model for pooled CP(alpha) ancillas.
--
-- This is an explicit State.next trace model, not #lang forge/temporal. It
-- tracks both the four-mode allocation block and each individual mode so the
-- allocation unit inherited from Phase 22 and the no-mode-reallocation claim
-- remain visible at the same time.
--
-- The model is bounded: a satisfying or violating trace is evidence within
-- the declared scope, not an unbounded theorem. It does not verify a Python
-- k-pair implementation, photonic amplitudes, physical unitary equivalence,
-- or the hardness-under-loss study.

abstract sig Event {}
one sig Start, Allocate, BeginUse, FinishGate, FinalPostselect, Release
    extends Event {}

sig Pair {
    i: one Int,
    j: one Int
}

sig Mode {}
sig Block {
    modes: set Mode
}

sig Gate {
    pair: one Pair,
    block: one Block
}

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

one sig Trace {
    first: one State
}

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

pred modePartition[s: State] {
    Mode = s.freeModes + s.allocatedModes + s.inUseModes + s.releasableModes
    no s.freeModes & s.allocatedModes
    no s.freeModes & s.inUseModes
    no s.freeModes & s.releasableModes
    no s.allocatedModes & s.inUseModes
    no s.allocatedModes & s.releasableModes
    no s.inUseModes & s.releasableModes
}

pred blockPartition[s: State] {
    Block = s.freeBlocks + s.allocatedBlocks + s.inUseBlocks + s.releasableBlocks
    no s.freeBlocks & s.allocatedBlocks
    no s.freeBlocks & s.inUseBlocks
    no s.freeBlocks & s.releasableBlocks
    no s.allocatedBlocks & s.inUseBlocks
    no s.allocatedBlocks & s.releasableBlocks
    no s.inUseBlocks & s.releasableBlocks
}

pred blockModeAgreement[s: State] {
    all b: Block | {
        (b in s.freeBlocks) iff b.modes in s.freeModes
        (b in s.allocatedBlocks) iff b.modes in s.allocatedModes
        (b in s.inUseBlocks) iff b.modes in s.inUseModes
        (b in s.releasableBlocks) iff b.modes in s.releasableModes
    }
}

pred stateWellFormed[s: State] {
    modePartition[s]
    blockPartition[s]
    blockModeAgreement[s]
}

pred orderedTrace {
    no Trace.first.~next
    one last: State | no last.next
    State = Trace.first.*next
    all s: State | s not in s.^next
    all s: State | stateWellFormed[s]
}

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

pred safeTrace {
    initialState[Trace.first]
    all s: State | some s.next implies validTransition[s, s.next]
}

pred unsafeTrace {
    initialState[Trace.first]
    all s: State | some s.next implies {
        validTransition[s, s.next]
        or (some g: Gate | unsafeAllocateTransition[s, s.next, g])
    }
}

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
