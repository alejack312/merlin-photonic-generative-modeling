# Phase 22 Forge-vs-Brute-Force Summary (MPAIR-05)

## What was modeled

The search question, per `22-CONTEXT.md` D-05: **does an assignment of at most `K` ancilla
blocks to all `C(n,2)` pairs of `K_n` exist such that no two vertex-sharing pairs collide, and
what is the minimum such `K`?** This is a SEARCH question — Forge's `Alloc.block` is a free
relation the solver searches over, not a fixed formula being checked. `forge/pooled_ancilla_allocation.frg`
is the model; `results/phase22_allocation_invariant.md` is the prose invariant it encodes.

The alternative — verifying one fixed colouring against the compatibility rule — was deliberately
NOT asked. `results/phase22_allocation_invariant.md`'s "## Pairwise-reduction argument" establishes
that collision is a binary predicate: because the round-robin formula is a pure function of each
pair's own `(i,j)` (no dependence on which other pairs are active), "no collision over every
subset of simultaneously-active pairs" reduces exactly to "no collision over every pair of pairs" —
`C(28,2) + 28 = 406` pairwise checks at `n=8`, trivially brute-forceable in well under a millisecond.
Asking that question would have produced a second "Forge did not earn its place" verdict by
construction, not by measurement — exactly repeating ARB-09's own 2026-08-20 audit finding for
the single-pair model. The search question — find the minimum `K`, not verify one — is what a
SAT-backed model finder is actually for, and is the fair comparison this document reports.

## Bound checked

| `n` | parity | `C(n,2)` (`Pair` bound) | Forge outcome |
|---|---|---|---|
| 4 | even | 6 | converged, `K=3` |
| 5 | odd | 10 | converged, `K=5` |
| 6 | even | 15 | converged, `K=5` |
| 7 | odd | 21 | **timed out** (isolated 2-block probe, ~610s, zero blocks resolved) |
| 8 | even | 28 | not attempted (n=7 already timed out) |

Forge bitwidth: `for 7 Int` (signed range `[-64, 63]`), justified against the largest ancilla mode
index this model computes — `2*8 + 4*6 + 3 = 43` at the D-03 target `n=8` (`K = n-1 = 7`, so
`c_max = K-1 = 6`). `for 6 Int` (`[-32, 31]`) would silently overflow at 43 with no diagnostic;
`for 7 Int` comfortably contains it with headroom. (Restated from
`results/phase22_allocation_invariant.md`'s "## Bitwidth justification"; not recomputed here.)

## Result

Verbatim Forge output, `n=6` (the largest converging `n`), quoted from
`results/phase22_forge_run_log.md`:

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

All 12 live test blocks passed across `n=4/5/6`: `nonVacuous<N>` (sat, MPAIR-04 non-vacuity),
`colouringExists<N>` (sat, existence at `K`), `minimality<N>` (unsat, no proper colouring at
`K-1`), `dataPortDisjoint<N>` (unsat, no valid allocation collides with a data port).

## Forge vs. brute force

`pooled_allocation_baseline.py --n-max 8` (default 600s per-n ceiling), full output below.
Backtracking search table (the primary comparison — the direct analogue of Forge's
`colouringExists<N>`/`minimality<N>` pair):

| `n` | Forge min `K` | Forge outcome | Python `min_K` (backtracking) | Python `backtracking_seconds` |
|---|---|---|---|---|
| 4 | 3 | converged | 3 | 0.001 |
| 5 | 5 | converged | 5 | 0.001 |
| 6 | 5 | converged | 5 | 0.001 |
| 7 | — | timed out (~610s, 0 blocks resolved) | 7 | 2.284 |
| 8 | — | not attempted | 7 | 0.006 |

Agreement is exact at every `n` Forge reached (4, 5, 6) — no disagreement to report. The Python
search additionally reaches `n=7` and `n=8`, both beyond Forge's converging bound, in a combined
~2.29 seconds — where Forge's isolated `n=7` probe was still killed at ~610s with zero blocks
resolved (`results/phase22_forge_run_log.md`, "## n=7 timeout probe").

| Metric | Forge | Python backtracking search |
|---|---|---|
| Verdict (minimum `K` found + infeasibility at `K-1` established) | `K=3,5,5` at `n=4,5,6`; not established at `n=7,8` | `K=3,5,5,7,7` at `n=4,5,6,7,8` — identical at every `n` both reached, plus 2 more |
| Coverage | `n=4..6` (12 test blocks, all passed) | `n=2..8` (all 7 values) |
| Runtime | ~6m9s total wall time for the `n=4..6` suite (`results/phase22_forge_run_log.md`, "Total wall time for the live `n=4..6` suite"); `n=7` probe killed at ~610s | `n=4..8` backtracking total: 0.001+0.001+0.001+2.284+0.006 ≈ **2.29s** |
| Ratio (n=4..6, both converged) | Forge ~6m9s = 369s | Python ~0.003s → **Forge is ~123,000x slower** on the domain both reached |
| Ratio (n=7, Forge timeout vs. Python solve) | Forge: killed at 610s, 0 blocks resolved | Python: 2.284s, fully solved (K found + K-1 proven infeasible) — Forge did not converge at all where Python did in under 3 seconds |

**SECONDARY — naive subset-enumeration cost** (NOT the primary comparison; the primary model is
pairwise-reduced per `results/phase22_allocation_invariant.md`'s "## Pairwise-reduction argument"
and never enumerates subsets — this row exists purely to cost out the original `2^28`-subset
framing `22-CONTEXT.md`'s "Specific Ideas" section worried about):

| `n` | total subsets (`2^C(n,2)`) | subsets checked | timed out | seconds |
|---|---|---|---|---|
| 7 | 2,097,152 | 2,097,152 | No | 46.13 |
| 8 | 268,435,456 | 18,080,000 | **Yes** | 600.52 (ceiling) |

`SECONDARY: reached n=8, checked 18,080,000 of 268,435,456 subsets before the 600.0s ceiling` —
the naive framing genuinely would have been intractable at `n=8` under a straightforward Python
enumeration (covering only ~6.7% of the subset space in 10 minutes), confirming
`results/phase22_allocation_invariant.md`'s pairwise-reduction argument is not a hypothetical
convenience but the thing that makes this domain checkable at all — by *either* tool. Neither
Forge's search nor the Python backtracking search enumerates subsets; both operate on the
reduced, pairwise-formulated problem, which is exactly why both finish n=7/n=8 in seconds while
naive subset enumeration cannot finish n=8 in ten minutes.

## What Forge alone contributed

**CRITERION CORRECTION (2026-08-21).** This plan was originally written to grade Forge on *"does
it beat brute force on an intractable domain."* That standard was corrected in `REQUIREMENTS.md`
(MPAIR-05's own correction note, added 2026-08-21) after reviewing the owner's CS1710 (Logic for
Systems) coursework — the course this Forge toolchain comes from. None of that course's own
models are brute-force-intractable either (hotel locking: 3 rooms / 3 guests / 8 time steps;
goats-and-wolves: a river-crossing puzzle a BFS solves in milliseconds). The brute-force-timing
standard was the wrong axis, and it was corrected **mid-phase**, not discovered as the standard
all along — ARB-09's audit (`results/phase16_forge_summary.md`) was graded on that old axis too,
and its "Forge's exhaustive-search advantage never engaged" framing should be read with that in
mind rather than as evidence the corrected criterion was already in use.

The corrected grading axis is four questions, addressed explicitly:

**(a) Did the model find a scenario you would not have thought to enumerate?** No. The scenario
space here — `K_n`'s edges, the vertex-disjointness conflict rule — was already fully enumerated
by hand in `results/phase22_allocation_invariant.md` before any Forge code existed (the round-robin
formula, the pairwise-reduction argument, the counterexample shape). Forge searched over a space
whose boundaries were already known; it did not surface an unanticipated case.

**(b) Is the property one over traces/reachability, where the "brute force" would itself be a
model checker?** No. This is a static combinatorial property (graph edge-colouring existence and
minimality) with no state, no sequence of actions, no reachability question. Phase 23's
LIFE-01..07 (ancilla lifecycle safety, added 2026-08-21) is explicitly the trace/reachability
counterpart to this phase's static colouring question — this document is honest that Phase 22
itself is not that case.

**(c) Did writing the model force the specification to be precise in a way prose did not?** Yes,
partially. Encoding `properColouring`, `conflicts`, and `genuinePooling` as Forge predicates forced
explicit answers to questions the prose invariant (`results/phase22_allocation_invariant.md`)
already answered carefully (MPAIR-04's strengthened non-vacuity condition — requiring two
mutually-compatible pairs that actually share a block, not the weaker `some active` form that
passes vacuously on a single-pair instance — was written into the prose specifically because a
set-valued model needs it). The precision gain here is real but modest: the prose document was
already precise before the `.frg` file existed, unlike a case where Forge is the first place the
specification gets nailed down.

**(d) Did it verify a design before it was built — the thing this phase exists to do?** Yes. No
Python implements pooled multi-pair ancilla allocation yet (MPAIR-06's own framing: unlike
`forge/ancilla_mapping.frg`, which re-states an already-shipped formula, `pooled_ancilla_allocation.frg`
is the source of truth an eventual implementation must be checked against). This is the one
criterion this phase clearly satisfies — Forge (and independently, this Python search) confirmed
the allocation scheme before any implementation exists to drift from it.

**Whether Forge's exhaustive search engaged at this scale, stated with the measured ratio:** it
did not engage in the sense of finding anything the Python search couldn't. At the converged
domain (`n=4..6`), Forge took ~369s total wall time where the Python backtracking search took
~0.003s — Forge is roughly **123,000x slower**, not faster, on the domain both tools solved. At
`n=7`, Forge's own exhaustive SAT-backed search hit D-04's 10-minute ceiling with zero blocks
resolved, while the Python backtracking search — a few hundred lines of depth-first search with a
most-constrained-first heuristic — solved `n=7` in 2.28 seconds and `n=8` in 0.006 seconds. **A
few hundred lines of backtracking Python reached the same minimum faster, and reached further,
than Forge's SAT-backed exhaustive search.** This is not a marginal result — Forge's search did
not converge at all on the two `n` values (7, 8) the Python search solved in under 2.3 seconds
combined.

**A negative verdict on (a)-(d) is a PASSING outcome.** Per `REQUIREMENTS.md`'s MPAIR-05 wording:
*"A 'Forge did not earn its place here either' verdict satisfies this requirement"* and per
ROADMAP success criterion 4, only an unchecked assertion fails it — a measured negative is not a
failure. This document does not manufacture a larger domain or a different framing to justify the
tool; the measured comparison stands as reported.

**Known-theorem caveat, stated plainly (per D-05).** The chromatic index of `K_n` is a **known
theorem** — `n-1` for even `n`, `n` for odd `n` (König/Vizing). Both Forge's search and the Python
backtracking search constructively confirm known combinatorics and produce a concrete colouring
(the round-robin formula, independently checked proper by `check_round_robin` at every `n=2..8`,
`round_robin_proper=True` throughout); neither tool settles an open problem. This is restated here,
not implied as novel.

**Non-convergence at n=7/n=8, restated per D-04 (paired, not substituted, with the converging
bound).** `n=6` remains Forge's largest converging bound (~6m9s); `n=7` was probed and killed at
~610s with zero blocks resolved (`results/phase22_forge_run_log.md`); `n=8` was not separately
attempted. This non-convergence is reported here again alongside the converging `n=6` bound, per
D-04, and is itself part of the comparison: the same `n=7`/`n=8` domain Forge could not finish is
exactly where the Python search's advantage shows up most starkly (2.29 seconds total).

**What is durable regardless of the timing verdict:**
- **The declarative statement of the invariant.** `results/phase22_allocation_invariant.md`'s
  compatibility rule, allocation formula, and pairwise-reduction argument exist as a precise,
  reviewable prose specification independent of which tool checks it — this document's honest
  timing verdict does not diminish that the invariant itself had to be gotten right first.
- **The non-vacuity discipline strengthened for a set-valued model.** `genuinePooling` requires two
  mutually-compatible pairs that actually share a block, conjoined with `properColouring` holding —
  the weaker `some active`-style form used elsewhere in this codebase would pass vacuously on a
  single-pair instance, never exercising the pooling behaviour this phase exists to test. This
  guard transfers to future set-valued models regardless of Forge's raw search performance here.
- **The minimality half, which a greedy heuristic alone cannot establish.** `greedy_colouring` in
  `pooled_allocation_baseline.py` gives an upper bound only (`greedy_K=7` at both `n=7` and `n=8`,
  which happens to equal the true minimum here but is not proven minimal by greedy alone) — both
  Forge's `minimality<N>` blocks and this script's `backtracking_min_colouring` are needed to
  close the bound from below by proving `K-1` infeasible, not merely that `K` suffices.

## Scope boundary

This comparison is about ancilla mode **INDEX bookkeeping**, nothing more. It says nothing about
whether physically reusing those modes across sequentially-composed `CP(α)` unitaries reproduces
the same physics as dedicated per-pair ancilla — that is a separate, independently necessary
condition, categorically outside what a bounded model finder (or a Python colouring search) can
check. It was settled separately by MPAIR-07: see `results/phase22_reuse_gate.md` and its
`## Owner ruling` section (owner ruled **GO**, 2026-08-21, based on the `n=4` vertex-disjoint
probe's numerical evidence — `tvd_pooled_vs_dedicated` of `1.305e-14`/`2.899e-14`, both far inside
the `1e-9` GO threshold). Any language implying this document, or `forge/pooled_ancilla_allocation.frg`,
"proves pooling is safe" rather than "proves the chosen index-allocation scheme does not collide"
is wrong — the two questions are independent, and this document addresses only the index question.
