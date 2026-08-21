# Phase 22 Plan 04: Forge Run Log (MPAIR-03/MPAIR-04)

Model: `forge/pooled_ancilla_allocation.frg`. Toolchain: Racket 8.15 [cs], Forge v5.2.
Command: `racket forge/pooled_ancilla_allocation.frg`.

This log records the per-`n` solve timings for the ascending search over minimum ancilla-block
counts for `K_n`, against D-04's hard 10-minute-per-`n` ceiling.

## Per-n table

Each `n` has four test blocks: `nonVacuous<N>` (sat, MPAIR-04 non-vacuity), `colouringExists<N>`
(sat, existence at `K`), `minimality<N>` (unsat, no proper colouring at `K-1`), and
`dataPortDisjoint<N>` (unsat, no valid allocation collides with a data port). `Solving (ms)`
figures are Forge's own printed `Solving (ms)` values, not estimated.

| `n` | parity | `C(n,2)` (`Pair` bound) | `K` | Block | Verdict | Solving (ms) | Transl (ms) |
|---|---|---|---|---|---|---|---|
| 4 | even | 6 | 3 | `nonVacuousN4` | passed | 7904 | 969 |
| 4 | even | 6 | 3 | `colouringExistsN4` | passed | 5972 | 473 |
| 4 | even | 6 | 3 | `minimalityN4` | passed | 4003 | 325 |
| 4 | even | 6 | 3 | `dataPortDisjointN4` | passed | 5296 | 428 |
| 5 | odd | 10 | 5 | `nonVacuousN5` | passed | 19883 | 734 |
| 5 | odd | 10 | 5 | `colouringExistsN5` | passed | 13454 | 533 |
| 5 | odd | 10 | 5 | `minimalityN5` | passed | 30083 | 519 |
| 5 | odd | 10 | 5 | `dataPortDisjointN5` | passed | 22872 | 543 |
| 6 | even | 15 | 5 | `nonVacuousN6` | passed | 52982 | 1038 |
| 6 | even | 15 | 5 | `colouringExistsN6` | passed | 36486 | 875 |
| 6 | even | 15 | 5 | `minimalityN6` | passed | 60802 | 992 |
| 6 | even | 15 | 5 | `dataPortDisjointN6` | passed | 57163 | 975 |
| 7 | odd | 21 | 7 | `colouringExistsN7` | **timed out** | n/a — ceiling hit | n/a |
| 7 | odd | 21 | 6 | `minimalityN7` | **timed out** | n/a — ceiling hit | n/a |
| 8 | even | 28 | 7 | `colouringExistsN8` | not attempted | — | — |
| 8 | even | 28 | 6 | `minimalityN8` | not attempted | — | — |

Total wall time for the live `n=4..6` suite (all 12 blocks, one process): **~6m9s** (measured via
`time racket forge/pooled_ancilla_allocation.frg`).

## Verbatim Forge output, n=6 (largest converging n)

```
#vars: (size-variables 269928); #primary: (size-primary 6046); #clauses: (size-clauses 701585)
Transl (ms): (time-translation 1038); Solving (ms): (time-solving 52982)
    Test passed: nonVacuousN6
#vars: (size-variables 256122); #primary: (size-primary 6016); #clauses: (size-clauses 651784)
Transl (ms): (time-translation 875); Solving (ms): (time-solving 36486)
    Test passed: colouringExistsN6
#vars: (size-variables 256122); #primary: (size-primary 6016); #clauses: (size-clauses 651784)
Transl (ms): (time-translation 992); Solving (ms): (time-solving 60802) Core min (ms): (time-core 0)
    Test passed: minimalityN6
#vars: (size-variables 265319); #primary: (size-primary 6287); #clauses: (size-clauses 681958)
Transl (ms): (time-translation 975); Solving (ms): (time-solving 57163) Core min (ms): (time-core 0)
    Test passed: dataPortDisjointN6
```

## n=7 timeout probe

D-04's ceiling is per-`n`, not per-block, so before running the full `n=7` addition inside the
main model (which would also re-run `n=4..6` every invocation), `n=7` was probed in isolation
first, with only 2 of the 4 blocks (`colouringExistsN7`, `minimalityN7`) — a strictly *smaller*
workload than the full 4-block suite used at `n<=6`.

- Launched: `racket <isolated n=7 probe file>` (same predicates, `for 7 Int, exactly 21 Pair`
  bound, `Config.kmax = 7` / `6`).
- Killed after: **~610s (10m10s)**, exceeding the 600s/10-minute D-04 ceiling.
- Racket/kodkod process memory at kill time: ~420MB and still growing.
- Neither block had printed ANY translation or solving output (`Transl (ms)` / `Solving (ms)`
  lines) before the kill — the process was still in Kodkod's variable/clause construction or SAT
  solving phase for the first block, `colouringExistsN7`, with `minimalityN7` not yet reached.

This is a genuine ceiling hit, not a fluke: `n=6`'s own solving times already ranged 35–62s
*per block* (4 blocks), and the growth from `n=4` (avg ~5.8s/block) to `n=5` (avg ~21.6s/block)
to `n=6` (avg ~51.9s/block) is roughly 3.5–4x per step in `n`. Extrapolating that growth rate to
`n=7`'s larger `Pair` bound (21, up from 15) and `Config.kmax` range (7, up from 5) is consistent
with `n=7` exceeding 10 minutes before even one block converges.

`n=8` (D-03's original target) was **not** separately attempted: `n=7`, the intermediate step
below it, already exceeded the ceiling, and per D-04 the non-convergence at `n=7` is itself the
reported finding — attempting the strictly larger `n=8` problem would not change that outcome or
add a different reportable result.

## Bound outcome

**D-03's `n<=8` target bound was NOT reached.** The largest `n` for which a proper colouring was
found to exist at `K` and proven minimal at `K-1` (all four test blocks passing) is **`n=6`**,
converging in ~6m9s of total wall time for the full `n=4..6` suite (12 blocks). `n=7` was
attempted (a strictly smaller 2-block probe, not even the full suite) and exceeded D-04's hard
10-minute-per-`n` ceiling, killed at ~610s with zero blocks resolved; `n=8` was not attempted
given `n=7`'s timeout. This non-convergence at `n=7`/`n=8` is reported here as the finding
itself, per D-04 — paired with, not substituting for, the converging bound at `n=6`.

At every converged `n` (4, 5, and 6), the minimum `K` Forge's search found matches
`results/phase22_allocation_invariant.md`'s round-robin formula exactly: `K = n-1` for even `n`
(`n=4` -> `K=3`; `n=6` -> `K=5`) and `K = n` for odd `n` (`n=5` -> `K=5`), confirming — as
`22-CONTEXT.md`'s D-05 anticipated — that Forge's independent search agrees with the
hand-constructed witness rather than settling new combinatorics.

## Empirical bound-finding procedure

**Ascending linear search from `n=4`, with a per-`n` 10-minute (600s) hard ceiling.** `n=4`, `5`,
and `6` were each run as part of the live model's single `test expect` suite (all 12 blocks in
one `racket` invocation, ~6m9s total). Before extending the suite to `n=7` — which would have
re-run `n=4..6` on every subsequent invocation — `n=7` was probed in isolation with a reduced
2-block model to get a faster read on whether the ceiling would be hit at all before committing
to the full 4-block addition. It was: the isolated probe itself exceeded the ceiling. `n=8` was
not attempted, since `n=7` (a smaller problem on every axis: fewer `Pair` atoms, a smaller
`Config.kmax` range, and only half the test blocks) already timed out. Linear search was chosen
over a binary search on total domain size because `22-CONTEXT.md`'s Claude's Discretion note
left the exact procedure open, and the point of interest here is the *first* `n` that fails, for
which an ascending sweep is both simpler and directly produces the growth-curve data point
(`n=4` -> `n=5` -> `n=6` timings) needed to explain *why* `n=7` was expected to fail before
attempting it.
