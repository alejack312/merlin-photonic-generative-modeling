#lang forge
option run_sterling off

-- WHAT THIS MODELS: a search for a minimum-cardinality assignment of ancilla
-- blocks to the C(n,2) qubit pairs of K_n such that no two vertex-sharing
-- pairs receive the same block -- i.e. edge-colouring existence/minimality
-- over K_n. This is the SEARCH formulation MPAIR-03/MPAIR-04 require, not a
-- verification of one fixed formula. The prose source this model encodes is
-- results/phase22_allocation_invariant.md -- read it first; in particular
-- "## The invariant", "## Mode-index formula", "## Bitwidth justification",
-- and "## What the Forge model will actually ask" motivate every predicate
-- below. The round-robin colouring formula itself is deliberately NOT
-- encoded here (see note above properColouring): this model searches
-- freely, and the formula is Plan 22-05's independently-constructed witness
-- to compare against, not an input constraint on the search.
--
-- INVERTED DRIFT DIRECTION (this is NOT ancilla_mapping.frg's drift
-- warning -- do not copy that text): no Python implements this scheme.
-- There is nothing to drift FROM. This model is the SOURCE OF TRUTH that
-- any future k-pair implementation in iqp_photonic_encoding.py must be
-- checked against, which is the opposite direction from Phase 16's model
-- (which re-stated an already-shipped Python formula and could drift out of
-- sync with it).
--
-- BITWIDTH NOTE: `for N Int` sets Forge's Int BITWIDTH (a signed range),
-- not a count of anything. The largest value THIS model computes: at
-- n = 8, K = n - 1 = 7, so the largest colour index is c_max = K - 1 = 6,
-- and the largest ancilla mode index is 2*8 + 4*6 + 3 = 43. `for 6 Int`
-- gives range [-32, 31] and would SILENTLY overflow at 43 -- Forge does not
-- error on this, it wraps the value modulo the representable range with no
-- diagnostic, corrupting every downstream comparison involving mode index
-- 32 or above. `for 7 Int` gives range [-64, 63], comfortably containing 43
-- with headroom, and is therefore the minimum safe bitwidth used
-- throughout this file. This value was RECOMPUTED for this model and is
-- NOT copied forward from ancilla_mapping.frg, whose own largest computed
-- value was only 19 (single-pair case, 2n+3 at n=8) -- a bound that does
-- not hold once pooling introduces the 4c term. 22-RESEARCH.md's own code
-- snippets still show `for 6 Int` and are internally inconsistent with the
-- overflow-risk finding stated in that same research section; do not carry
-- that value forward here.
--
-- BOUND ACTUALLY REACHED vs D-03's TARGET: D-03 targeted n<=8. The live
-- suite below actually only reaches n=6 (largest ancilla mode index
-- computed at n=6: 2*6 + 4*4 + 3 = 31) -- n=7 and n=8 both hit D-04's
-- 10-minute ceiling; see the comment above the commented-out N7/N8 blocks
-- and results/phase22_forge_run_log.md's "## Bound outcome" section.
-- `for 7 Int` is kept (not narrowed to fit the smaller n=6 maximum of 31,
-- which would in fact still fit `for 6 Int`'s [-32,31]) because it remains
-- the correct, headroom-bearing justification against D-03's original
-- n=8/43 target that the commented-out blocks are written against, and
-- narrowing it would only save nothing (both bitwidths solve the same
-- SAT problem size) while creating a second bitwidth inconsistency to
-- track if the ceiling is ever lifted.
--
-- SCOPE NOTE: this model checks ancilla mode INDEX bookkeeping only. It
-- does NOT establish that reusing those physical modes across sequential
-- CP(alpha) unitaries reproduces dedicated-ancilla physics -- that is a
-- unitarity claim outside what a bounded model finder can check, settled
-- separately by MPAIR-07. See results/phase22_reuse_gate.md and its
-- "## Owner ruling" section (owner ruled GO, 2026-08-21, based on the n=4
-- vertex-disjoint probe's numerical evidence).
--
-- BOUND-CLAUSE SYNTAX: the repeated-`for` form the official docs show for
-- `run` blocks (`for 3 Int for exactly 5 Cat`) does NOT parse inside a
-- `test expect` block's trailing bound clause under Forge v5.2 in this
-- environment -- it produced a parse error at the second `for`. The COMMA
-- form (`for 7 Int, exactly 6 Pair`), matching every local example file
-- (`network.frg`'s `for exactly 2 Endpoint, 4 Host`, `prim.frg`'s
-- `for 5 Node, 5 Int`), is the form actually used below -- verified live,
-- not assumed on faith from 22-RESEARCH.md's snippets.

sig Pair {
    i: one Int,
    j: one Int
}

-- The free assignment Forge searches over. This is a sig FIELD, not an
-- `all`-quantified relation variable, so it does not hit the higher-order
-- restriction prim.frg's own author documents and rejects (`all t2: set
-- Node -> Node | ...` over a free relation inside a predicate body).
one sig Alloc {
    block: func Pair -> Int
}

-- Carries the two run constants explicitly rather than scattering magic
-- numbers through predicates.
one sig Config {
    n: one Int,
    kmax: one Int
}

-- Pins the Pair atom set to exactly the edge set of K_n: every atom is a
-- valid (i,j) with i<j<n, and no two distinct atoms denote the same edge.
-- Combined with an `exactly C(n,2) Pair` bound clause in each run/test
-- block, this forces the atom set to be exactly K_n's edges (no more, no
-- fewer).
pred pairsAreKn {
    all p: Pair | {
        p.i >= 0
        p.i < p.j
        p.j < Config.n
    }
    all disj p, q: Pair | not (p.i = q.i and p.j = q.j)
}

-- The vertex-disjoint compatibility rule from
-- results/phase22_allocation_invariant.md's "## Compatibility rule",
-- negated: pairs that CONFLICT share a qubit index and may not pool.
pred conflicts[p, q: Pair] {
    p.i = q.i or p.i = q.j or p.j = q.i or p.j = q.j
}

pred blocksInRange {
    all p: Pair | {
        Alloc.block[p] >= 0
        Alloc.block[p] < Config.kmax
    }
}

-- PAIRWISE formulation. results/phase22_allocation_invariant.md's
-- "## Pairwise-reduction argument" licenses this standing in for
-- subset-quantification: collision is a binary predicate (it is either
-- witnessed by two specific pairs or it does not exist at all), so "no
-- collision over every subset of simultaneously-active pairs" is exactly
-- equivalent to "no collision over every pair of pairs" -- provided (as is
-- the case here) the block assignment is a free relation with no
-- dependence on which OTHER pairs are active. Per D-05 the round-robin
-- colouring formula is deliberately NOT encoded anywhere in this file --
-- Forge searches freely over Alloc.block subject only to this predicate
-- and blocksInRange; the formula is Plan 22-05's independently-built
-- witness to compare the resulting minimum K against, not an input
-- constraint on the search.
pred properColouring {
    all disj p, q: Pair | conflicts[p, q] implies Alloc.block[p] != Alloc.block[q]
}

-- Every pair's ancilla mode index (2n + 4*block + t, for t in 0..3) must
-- avoid the data-port range 0..2n-1. Expected to hold BY CONSTRUCTION
-- (ancilla indices start at 2n, the largest data port is 2n-1) and checked
-- anyway, matching Phase 16/ARB-09's precedent of checking the fully
-- general property rather than asserting it.
pred ancillaDisjointFromDataPorts {
    all p: Pair | all t: Int | (t >= 0 and t < 4) implies {
        let modeIdx = add[multiply[2, Config.n], add[multiply[4, Alloc.block[p]], t]] | {
            all k: Int | (k >= 0 and k < multiply[2, Config.n]) implies k != modeIdx
        }
    }
}

-- MPAIR-04's strengthened non-vacuity condition: requires at least two
-- simultaneously-active, MUTUALLY-COMPATIBLE pairs that actually share a
-- block -- an instance where pooling genuinely happened. The weaker
-- `some Instance.active`-style form used elsewhere in this codebase is
-- insufficient here: it would pass on a single-pair instance, which is
-- vacuous in a way the scalar Phase 16 model never faced, because it never
-- exercises the pooling behaviour this phase exists to test.
pred genuinePooling {
    some disj p, q: Pair | not conflicts[p, q] and Alloc.block[p] = Alloc.block[q]
}

-- ---------------------------------------------------------------------
-- Counterexample shape (MPAIR-02): a counterexample to properColouring is
-- a specific n, a specific pair of vertex-sharing Pair atoms, and the
-- specific block index both were assigned -- an exhibited colliding
-- configuration (two pairs and a shared block index), not a failing
-- arithmetic comparison. E.g. n=6, pair (1,3) and pair (3,5), both sharing
-- vertex 3, with colour(1,3) = colour(3,5) = 2.
-- ---------------------------------------------------------------------

-- Four blocks per n: existence at K, minimality at K-1 (no proper
-- colouring with fewer blocks), data-port disjointness, and genuine
-- non-vacuous pooling. K = n-1 for even n, K = n for odd n
-- (results/phase22_allocation_invariant.md's round-robin formula's block
-- count; Vizing/Koenig's chromatic-index theorem for K_n).

test expect {

    -- n = 4 (even, K = 3)
    nonVacuousN4: {
        Config.n = 4
        Config.kmax = 3
        pairsAreKn
        blocksInRange
        properColouring
        genuinePooling
    } for 7 Int, exactly 6 Pair is sat

    colouringExistsN4: {
        Config.n = 4
        Config.kmax = 3
        pairsAreKn
        blocksInRange
        properColouring
    } for 7 Int, exactly 6 Pair is sat

    minimalityN4: {
        Config.n = 4
        Config.kmax = 2
        pairsAreKn
        blocksInRange
        properColouring
    } for 7 Int, exactly 6 Pair is unsat

    dataPortDisjointN4: {
        Config.n = 4
        Config.kmax = 3
        pairsAreKn
        blocksInRange
        properColouring
        not ancillaDisjointFromDataPorts
    } for 7 Int, exactly 6 Pair is unsat

    -- n = 5 (odd, K = 5) -- exercises the odd-n branch of the parity claim.
    nonVacuousN5: {
        Config.n = 5
        Config.kmax = 5
        pairsAreKn
        blocksInRange
        properColouring
        genuinePooling
    } for 7 Int, exactly 10 Pair is sat

    colouringExistsN5: {
        Config.n = 5
        Config.kmax = 5
        pairsAreKn
        blocksInRange
        properColouring
    } for 7 Int, exactly 10 Pair is sat

    minimalityN5: {
        Config.n = 5
        Config.kmax = 4
        pairsAreKn
        blocksInRange
        properColouring
    } for 7 Int, exactly 10 Pair is unsat

    dataPortDisjointN5: {
        Config.n = 5
        Config.kmax = 5
        pairsAreKn
        blocksInRange
        properColouring
        not ancillaDisjointFromDataPorts
    } for 7 Int, exactly 10 Pair is unsat

    -- n = 6 (even, K = 5)
    nonVacuousN6: {
        Config.n = 6
        Config.kmax = 5
        pairsAreKn
        blocksInRange
        properColouring
        genuinePooling
    } for 7 Int, exactly 15 Pair is sat

    colouringExistsN6: {
        Config.n = 6
        Config.kmax = 5
        pairsAreKn
        blocksInRange
        properColouring
    } for 7 Int, exactly 15 Pair is sat

    minimalityN6: {
        Config.n = 6
        Config.kmax = 4
        pairsAreKn
        blocksInRange
        properColouring
    } for 7 Int, exactly 15 Pair is unsat

    dataPortDisjointN6: {
        Config.n = 6
        Config.kmax = 5
        pairsAreKn
        blocksInRange
        properColouring
        not ancillaDisjointFromDataPorts
    } for 7 Int, exactly 15 Pair is unsat

    -- n = 7 and n = 8 (D-03's target bound) were ATTEMPTED and hit D-04's
    -- hard 10-minute-per-n ceiling -- this is a REPORTABLE FINDING, not a
    -- failure to engineer around (D-04). n = 6 is the largest bound that
    -- converged; see results/phase22_forge_run_log.md for the full
    -- per-n timing table and the "## Bound outcome" section.
    --
    -- Measured: an isolated 2-block probe at n=7 (colouringExistsN7,
    -- minimalityN7 only -- not even the full 4-block suite used at n<=6)
    -- was killed after exceeding the 600s/10-minute ceiling (measured wall
    -- time at cutoff: ~610s) with NEITHER block having returned translation
    -- or solving output. Racket/kodkod's memory footprint at kill time was
    -- ~420MB and still growing. Given n=6's own solving times already
    -- ranged 35-62s PER BLOCK (4 blocks, exact-count Pair bound growing
    -- from 15 at n=6 to 21 at n=7 to 28 at n=8, with search-space growth
    -- driven by Alloc.block's free assignment over an increasing Pair
    -- count and Config.kmax range), n=7 exceeding the ceiling before even
    -- ONE block resolved is consistent with continued steep growth, not
    -- an anomaly. n=8 was not separately attempted, since n=7 (the
    -- intermediate step below it) already exceeded the ceiling -- climbing
    -- further would not produce a different, reportable outcome.
    --
    -- The test blocks below are commented out rather than deleted, kept in
    -- the exact shape they would run in if the ceiling were lifted, so the
    -- model's live, non-commented bound remains n=6 (D-04's instruction:
    -- do not weaken a property or drop a block to force green -- comment
    -- out with the measured cutoff time, which is done here).
    --
    -- colouringExistsN7: {
    --     Config.n = 7
    --     Config.kmax = 7
    --     pairsAreKn
    --     blocksInRange
    --     properColouring
    -- } for 7 Int, exactly 21 Pair is sat
    --
    -- minimalityN7: {
    --     Config.n = 7
    --     Config.kmax = 6
    --     pairsAreKn
    --     blocksInRange
    --     properColouring
    -- } for 7 Int, exactly 21 Pair is unsat
    --
    -- colouringExistsN8: {
    --     Config.n = 8
    --     Config.kmax = 7
    --     pairsAreKn
    --     blocksInRange
    --     properColouring
    -- } for 7 Int, exactly 28 Pair is sat
    --
    -- minimalityN8: {
    --     Config.n = 8
    --     Config.kmax = 6
    --     pairsAreKn
    --     blocksInRange
    --     properColouring
    -- } for 7 Int, exactly 28 Pair is unsat
}
