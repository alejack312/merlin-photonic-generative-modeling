#lang forge
option run_sterling off

-- Structural correctness check of the CP(alpha) insertion's local->global
-- ancilla mode-index mapping dict (iqp_photonic_encoding.py,
-- _build_weight2_cp_processor_no_postselect, lines 622-627):
--   mapping = {2i:0, 2i+1:1, 2j:2, 2j+1:3, 2n:4, 2n+1:5, 2n+2:6, 2n+3:7}
-- ARB-09 (Phase 16): confirms the mapping's 8 KEYS are pairwise distinct
-- (injective) for every valid (n,i,j), checked against ALL n qubits' own
-- data ports (0..2n-1), not just qubit i/j's -- the fully general property
-- (16-CONTEXT.md's explicit instruction), even though it is provably
-- impossible to collide by construction (ancilla ports start at 2n, which
-- is >= the max qubit port 2n-1).
--
-- Bitwidth note: `for 6 Int` sets Forge's Int bitwidth (signed range
-- [-32,31]), NOT the n-bound -- n<=8 is enforced inside validTriple. This
-- is deliberately wider than Forge's *default* bitwidth (4 bits, signed
-- range [-8,7], per the Forge manual and confirmed against this repo's
-- own CS1710 example files, e.g. binarysearch.frg). The largest value this
-- model computes is 2*n+3 at n=8, i.e. 19 -- comfortably inside 6-bit
-- range [-32,31], with headroom, so no silent integer overflow/wraparound
-- is possible at the chosen bound. (An initial recollection that Forge
-- "only supports 0-7" was a garbled memory of the *default* 4-bit
-- bitwidth's positive half, not a hard universal Forge limit -- bitwidth
-- is a per-run `for N Int` setting, not a language ceiling. Verified live
-- during Phase 16 research: `for 6 Int` solves this exact model in ~1.2s
-- total at n<=8.)

pred validTriple[n, i, j: Int] {
    n >= 2
    n <= 8
    i >= 0
    i < n
    j >= 0
    j < n
    i != j
}

pred distinctPorts[n, i, j: Int] {
    let pi0 = multiply[2, i], pi1 = add[multiply[2, i], 1],
        pj0 = multiply[2, j], pj1 = add[multiply[2, j], 1],
        a0 = multiply[2, n], a1 = add[multiply[2, n], 1],
        a2 = add[multiply[2, n], 2], a3 = add[multiply[2, n], 3] | {
        pi0 != pi1  pi0 != pj0  pi0 != pj1  pi0 != a0  pi0 != a1  pi0 != a2  pi0 != a3
        pi1 != pj0  pi1 != pj1  pi1 != a0  pi1 != a1  pi1 != a2  pi1 != a3
        pj0 != pj1  pj0 != a0  pj0 != a1  pj0 != a2  pj0 != a3
        pj1 != a0  pj1 != a1  pj1 != a2  pj1 != a3
        a0 != a1  a0 != a2  a0 != a3  a1 != a2  a1 != a3  a2 != a3
        -- ancilla ports must not collide with ANY qubit's own data port
        -- (0..2n-1), not just qubit i/j's -- the fully general property.
        all k: Int | (k >= 0 and k < multiply[2, n]) implies {
            k != a0
            k != a1
            k != a2
            k != a3
        }
    }
}

test expect {
    -- Part 1: non-vacuity -- guards against a vacuously-true,
    -- over-constrained model (the classic Forge pitfall).
    nonVacuous: {
        some n, i, j: Int | validTriple[n, i, j]
    } for 6 Int is sat

    -- Part 2: no counterexample to injectivity/non-collision within bound.
    noCounterexample: {
        some n, i, j: Int | validTriple[n, i, j] and not distinctPorts[n, i, j]
    } for 6 Int is unsat
}
