# MPAIR-02: The Multi-Pair Ancilla Allocation Invariant (Phase 22 Plan 02)

Owner ruling: GO (`results/phase22_reuse_gate.md`, `## Owner ruling`, 2026-08-21). This
document is prose plus arithmetic — no Forge code, and no `.frg` file is created by this
plan. It states the invariant MPAIR-05's Forge model must check, before any Forge code
exists.

## Compatibility rule

Two pairs `(i,j)` and `(i',j')` may be assigned the same ancilla block if and only if
`{i,j} ∩ {i',j'} = ∅` — i.e. they are vertex-disjoint.

Why vertex-sharing pairs cannot pool: this codebase's IQP circuit applies a diagonal ZZ term
per selected pair as an independent, commuting factor of the overall diagonal layer. Diagonal
ZZ terms on overlapping qubit indices still commute with each other and both legitimately
apply in a multi-ZZ IQP circuit — there is no "only one of these two gates is active at a
time" structure to exploit. Two pairs that share a qubit are therefore always *simultaneously
active* whenever both are selected, so they cannot be treated as mutually exclusive users of
the same physical ancilla block the way a scheduler might reuse a resource between
non-overlapping tasks. Pooling such a pair would mean two coherent CP(α) insertions touching a
common ancilla block while their qubit-index footprints overlap, which is a strictly worse
case than the already-measured same-pair (`{i,j} = {i',j'}`) composability failure in
`results/phase22_reuse_gate.md`'s n=2 probe — that probe is the fully-overlapping special case
of exactly this hazard, and it is the concrete evidence for excluding all overlapping pairs.

This rule is **Claude's Discretion** under `22-CONTEXT.md`'s "Claude's Discretion" section —
the researcher/planner was asked to state it explicitly and precisely as part of MPAIR-02's
invariant, since it is the one mechanism detail within the confirmed pooled/recycled scheme
that has not itself been reviewed by the owner. It is put to the owner for confirmation at
Plan 22-03's checkpoint, per `22-CONTEXT.md`'s deferred item "a second owner review of the
exact pooling-compatibility rule."

## Allocation concretization: round-robin edge-colouring of K_n

The concrete, fixed, subset-independent formula — an allocation that is a pure function of a
pair's own `(i,j)` and does NOT depend on which other pairs are active. This condition is
what the pairwise-reduction argument below depends on, and is stated here as a condition to
satisfy, not assumed:

- **Odd `n`:** `colour(i,j) = (i + j) mod n`, using `K = n` blocks.
- **Even `n`:** let `m = n - 1` (odd). For `i, j < m`: `colour(i,j) = (i + j) mod m`. For the
  last vertex: `colour(i, n-1) = (2i) mod m`. Using `K = m = n - 1` blocks.

Standard construction argument for why the even case is proper: under `(i+j) mod m` on `K_m`
with `m` odd, colour class `c` is a near-perfect matching missing exactly the single vertex
`v` satisfying `2v ≡ c (mod m)`. That `v` is unique because `m` is odd (the map `v -> 2v mod
m` is a bijection on `Z_m` when `m` is odd, since 2 is invertible mod an odd modulus).
Attaching vertex `n-1` to the missed vertex `v` with colour `c` completes each class `c` to a
perfect matching on all `n` vertices, so every colour class is a genuine matching (no vertex,
hence no qubit index, appears twice within one colour) and every edge (pair) receives a
colour.

Per `22-CONTEXT.md` D-05's honesty caveat, stated plainly: the chromatic index of `K_n` is a
KNOWN theorem — `n-1` for even `n`, `n` for odd `n` (König/Vizing). This formula
constructively realizes known combinatorics; it does not settle an open problem. Forge's role
(see "What the Forge model will actually ask" below) is to independently *find* a minimum
colouring via search and confirm it agrees with this hand-constructed witness — not to
discover a new theoretical result.

## Mode-index formula

A pair assigned block `c` occupies ancilla modes `2n + 4c`, `2n + 4c + 1`, `2n + 4c + 2`,
`2n + 4c + 3`.

This generalizes `_build_weight2_cp_processor_no_postselect`'s single-pair tail-ancilla
mapping-dict entries (`{2n:4, 2n+1:5, 2n+2:6, 2n+3:7}` — `iqp_photonic_encoding.py` lines
632-637), which is exactly the `c = 0` case of this formula, rather than replacing it: a
single-pair circuit is the `K = 1` degenerate instance of the same block-indexing scheme.

Total mode count becomes `2n + 4K` instead of `4 * C(n,2)` under contiguous per-pair
allocation — the sub-linear-in-k growth D-02 selected pooling to obtain (contiguous costs 4
modes per pair regardless of overlap structure; pooled costs 4 modes per *colour*, and
`K = O(n)` while `C(n,2) = O(n^2)`).

Concrete comparison at `n = 8`: pooled `2*8 + 4*7 = 44` modes versus contiguous
`2*8 + 4*28 = 128` modes (`K = n - 1 = 7` at even `n = 8`; `C(8,2) = 28` pairs under
contiguous).

## Bitwidth justification

Compute the largest value the model computes, explicitly, and justify the Forge bitwidth
against it — matching `forge/ancilla_mapping.frg`'s existing header-note discipline.

At `n = 8` (even), `K = n - 1 = 7`, so the largest colour index is `c_max = K - 1 = 6`, and
the largest ancilla mode index is `2*8 + 4*6 + 3 = 16 + 24 + 3 = 43`.

`for N Int` sets Forge's Int **bitwidth**, not a count: `for N Int` gives the signed range
`[-2^(N-1), 2^(N-1) - 1]`. `for 6 Int` gives `[-32, 31]` and would **silently overflow** at
43 — Forge does not error on this; a value that exceeds the bitwidth wraps around modulo the
representable range without any diagnostic, which would corrupt every downstream comparison
involving mode index 32 or above without producing a visible failure. The minimum safe
bitwidth is **`for 7 Int`**, giving range **`[-64, 63]`**, comfortably containing 43 with
headroom.

`22-RESEARCH.md`'s own code snippets still show `for 6 Int` and are internally inconsistent
with the finding stated in that same research section (which already flags the `for 6 Int`
overflow risk in prose). `for 6 Int` must NOT be copied forward from `forge/ancilla_mapping.frg`
into the new model — that file's own `for 6 Int` choice was correctly justified there because
its largest computed value was only 19 (single-pair case, `2n+3` at `n=8`), a bound that does
not hold once pooling introduces the `4c` term.

## The invariant

What the property quantifies over: `n` ranging from 2 to 8 inclusive; all `C(n,2)` pairs
`(i,j)` with `0 <= i < j < n`; the block assignment `colour: Pair -> [0, K)` (where `K` is
`n` for odd `n` and `n-1` for even `n`, per the Allocation concretization above); and the
data-port range `0 .. 2n-1` (each qubit's two dual-rail ports).

Two conjuncts:

(a) **No index collision between pairs:** no two vertex-sharing pairs — i.e. pairs `(i,j)`
and `(i',j')` with `{i,j} ∩ {i',j'} ≠ ∅` — are assigned the same block `colour(i,j) =
colour(i',j')`.

(b) **No index collision against data ports:** no ancilla mode index `2n + 4c + t`, for `t`
in `0..3` and `c` in `0..K-1`, equals any data port in `0 .. 2n-1`. (This conjunct holds true
by construction, the same shape ARB-09's audit already found for the single-pair model:
ancilla indices start at `2n`, strictly above the largest data port `2n-1`. It is restated as
part of the invariant, not omitted, because the Forge model should still check it explicitly
rather than assume it.)

What a counterexample looks like AS A STRUCTURE, not as a number: a specific `n`, a specific
pair of pairs sharing a qubit index — e.g. `n=6`, pair `(1,3)` and pair `(3,5)`, both sharing
vertex `3` — and the specific block index both were assigned, e.g. `colour(1,3) = colour(3,5)
= 2`. A counterexample is an exhibited colliding configuration (two pairs and a shared block
index), not a failing arithmetic comparison.

## Pairwise-reduction argument

This is the load-bearing step and is written out in full, because it is what licenses not
literally enumerating the `2^28` subsets the original framing worried about (`22-CONTEXT.md`,
"Specific Ideas": the owner's original framing supplied the `2^28 ≈ 268M subsets` estimate).

Collision is a **binary predicate**: whether the allocation collides is entirely determined
by looking at pairs of pairs, two at a time, and there is no three-or-more-way interaction —
unlike a *capacity* constraint (e.g. "at most 4 pairs may pool the same block simultaneously"),
where three simultaneously-active items could jointly violate a bound that no two of them
violate alone. A collision between colour assignments either exists between some two pairs, or
it does not exist at all.

Therefore, **provided** the block assignment is a pure function of each pair's own identity
`(i,j)` and does not depend on which other pairs are active (the condition flagged in
"Allocation concretization" above — the round-robin formula satisfies it, since `colour(i,j)`
never references any other pair), the statement "no collision over every subset of
simultaneously-active pairs" is **exactly equivalent — not weaker —** to the statement "no
collision over every pair of pairs."

- **Forward direction:** if some subset `S` of simultaneously-active pairs collides (some two
  members of `S` share a block despite sharing a qubit), the collision is witnessed by two
  specific elements of `S` — so a pairwise counterexample exists.
- **Converse:** a colliding pair of pairs is itself already a two-element subset, so it is
  trivially also a subset-level counterexample.

At `n = 8`, this collapses "check all subsets of the 28 pairs" down to checking all
`C(28,2) + 28 = 378 + 28 = 406` pairwise cases (every unordered pair of distinct pairs, plus
each pair checked against itself for the degenerate self-collision `colour(i,j) =
colour(i,j)`, trivially true and included for completeness of the pairwise enumeration).

The reduction is **unsound for a dynamic/adaptive allocation** (e.g. a greedy first-fit
colouring recomputed per active subset, where a pair's assigned block could change depending
on which other pairs happen to be selected) — this is precisely why the fixed, pure-function
round-robin formula was chosen over any adaptive scheme. Adding any non-pairwise invariant
later (for example, a global ancilla-budget cap limiting the total number of blocks in use
across the whole circuit at once, rather than just checking overlap between block-sharing
pairs) would break the reduction and force genuine subset-level quantification.

## What the Forge model will actually ask

Per D-05 (`22-CONTEXT.md`), the model poses a **search** question, not a verification one:
*"does an assignment of at most `K` ancilla blocks to all `C(n,2)` pairs exist such that no
two vertex-sharing pairs collide, and what is the minimum such `K`?"*

Why: verifying a given fixed colouring reduces to the 406 pairwise checks derived above, and
that check is trivially brute-forceable (a Python loop over 406 comparisons runs in well
under a millisecond) — which would drive MPAIR-05 to a second "Forge did not earn its place"
verdict by construction, repeating exactly the finding ARB-09's own 2026-08-20 audit already
made for the single-pair model. **Finding** a minimum colouring, by contrast, is constraint
satisfaction over an unconstrained search space of block assignments — which is what a
SAT-backed model finder like Forge is actually for, and is not trivially brute-forceable at
scale the same way a fixed-formula check is.

The Forge model must therefore **NOT** encode the round-robin formula as the thing being
checked. Instead it searches freely over all possible block assignments subject only to the
compatibility rule and the block-count bound, and the round-robin formula above is the
independently-constructed witness whose colour count (`K = n` odd, `K = n-1` even) must agree
with whatever minimum Forge's search finds — agreement is the confirming result, not an input
constraint on the search.

## Scope boundary — what this does NOT establish

This invariant is about ancilla mode **INDEX bookkeeping only**. Index-level non-collision
does **NOT** establish that reusing those physical modes across sequentially-composed CP(α)
unitaries reproduces the same physics as dedicated per-pair ancilla.

That is a separate, independently necessary condition. It is a unitarity/physics claim
categorically outside what a bounded model finder can check — the same tool-category boundary
`16-CONTEXT.md` already drew around Forge for the single-pair case (Forge verifies discrete,
structural, combinatorial properties; it cannot evaluate whether a photonic circuit's measured
quantum state matches an intended unitary action). It was settled separately by MPAIR-07 —
see `results/phase22_reuse_gate.md` and its `## Owner ruling` section (owner ruled GO,
2026-08-21, based on the n=4 vertex-disjoint probe's numerical evidence).

Any write-up language implying the Forge check "proves pooling is safe" rather than "proves
the chosen index-allocation scheme does not collide" is wrong. The two questions — does the
index scheme collide, and does the physical reuse reproduce the intended physics — are
independent, and this document addresses only the first.

## Owner review (Plan 22-03)

Date: 2026-08-21. Attributed to: the owner.

> Option: confirm-both
> Selected: "Confirm both (Recommended)" — confirms the vertex-disjoint compatibility rule (a) and the fixed round-robin allocation formula (b) as presented, via structured selection. No additional reasoning text was provided beyond the option selection.

Since the ruling is `confirm-both`, no revision to `## Compatibility rule`,
`## Allocation concretization: round-robin edge-colouring of K_n`, `## Mode-index formula`,
`## Bitwidth justification`, or `## Pairwise-reduction argument` is needed — they already
state (a) and (b) exactly as confirmed (written in Plan 22-02). This discharges
`22-CONTEXT.md`'s flag-back obligation on the compatibility rule and `22-RESEARCH.md` Open
Question 1 on the fixed-vs-dynamic concretization.
