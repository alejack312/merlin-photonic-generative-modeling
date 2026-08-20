# Phase 22: Multi-Pair Ancilla Allocation — Formal Verification - Research

**Researched:** 2026-08-20
**Domain:** Forge (Alloy-family, Racket-hosted) formal verification of a combinatorial mode-allocation scheme, upstream of any Python implementation
**Confidence:** MEDIUM — the Forge encoding techniques are HIGH confidence (grounded in this repo's own prior Forge model plus four local, already-installed Forge example files read directly). The tractability question and the pooling-compatibility mechanism question are genuinely open and are reported as open, not guessed.

## Summary

This phase extends `forge/ancilla_mapping.frg`'s single-pair injectivity check to a **pooled/recycled** k-pair ancilla allocation scheme. The single biggest finding of this research is a modeling tension the planner and owner must resolve explicitly before Forge code is written: **the way "pooled/recycled" is concretized determines whether the property is Forge-tractable at all.**

If the ancilla-block assigned to a pair is a function of *that pair alone* (its own `(i,j)` identity, not of which other pairs happen to be simultaneously active), then "no collision for every subset of active pairs" is logically **equivalent** to "no collision for every *pair* of pairs" — a `C(k,2)` pairwise check, not a `2^k`-subset search. This collapses the stated "2^28 ≈ 268M subsets" risk to a few hundred pairwise comparisons at n=8, and is directly Forge-tractable using the same `noCounterexample`/`nonVacuous` two-part pattern `ancilla_mapping.frg` already uses.

But a *subset-independent, per-pair-only* allocation function is uncomfortably close to what D-02 already rejected as "true by construction" for contiguous/interleaved schemes. A genuinely dynamic scheme (block assignment recomputed per active subset, e.g. greedy first-fit coloring) resists the pairwise reduction and pushes toward exactly the alternating-quantifier (∀-subset, ∃-allocation) Forge pattern that this repo's own local `prim.frg` example documents as impractically slow even at trivial bounds ("*This takes longer to run than I am willing to wait*").

There is a middle path this research recommends surfacing to the owner: model the pooled scheme as a **static edge-coloring (1-factorization) of the complete graph K_n** — i.e., precompute, once per `n`, a fixed `color(i,j)` assignment (a pair's ancilla-block identity) such that any two pairs sharing that color are guaranteed vertex-disjoint. This is a real, well-known combinatorial structure (not arithmetic-parity-trivial like `2n+4m`), it needs only `n-1` or `n` ancilla-block identities (a genuine, non-trivial reduction from `C(n,2)` blocks — the actual research payoff named in D-02), it is expressible as a closed-form-ish per-pair formula (so the pairwise-check reduction applies and Forge stays tractable), and its correctness is a real claim worth checking (that same-colored pairs are always vertex-disjoint) rather than an obvious parity fact.

**Primary recommendation:** adopt a fixed, deterministic, subset-independent allocation formula for the pooled scheme (round-robin edge-coloring of K_n is the concrete candidate), verify it via the pairwise-reduction argument (proven sound below), and time both a brute-force pairwise check and a brute-force naive-subset check as MPAIR-05's honest baseline comparison. Flag the allocation-formula choice itself back to the owner — it is new content beyond what CONTEXT.md locked, per its own instruction to flag mechanism-design gaps.

## Architectural Responsibility Map

| Capability | Primary Tier | Secondary Tier | Rationale |
|------------|-------------|----------------|-----------|
| Ancilla mode-allocation invariant statement (prose) | Specification (docs) | — | MPAIR-02 requires this exist before any Forge code; it is not itself executable |
| Discrete structural verification (no collision) | Formal verification (Forge/Racket) | — | Bounded, discrete, silent-if-wrong property — the class Forge fits, per `16-CONTEXT.md`'s established boundary |
| Honesty/tractability audit (brute-force baseline, timing) | Tooling script (Python, standalone) | — | MPAIR-05's comparison; not part of the pytest suite, mirrors `ancilla_mapping.frg`'s own standalone brute-force audit |
| Future k-pair circuit implementation | Python/Perceval (`iqp_photonic_encoding.py`) | — | Explicitly out of scope for this phase — the Forge model becomes its source-of-truth spec |
| Physical/quantum correctness of ancilla reuse across sequential gates | **Not covered by this phase's tooling** | — | See Pitfall 1 below — this is a unitarity/physics claim Forge cannot check, and it is currently unresolved even informally |

## User Constraints (from CONTEXT.md)

<user_constraints>
### Locked Decisions

- **D-01: Gate family — CP(α) only** (`build_cp_insertion`/`_build_weight2_cp_processor_no_postselect`, 4 ancilla modes/pair, post-selection-filtered). Not `heralded_cz`. Not a generalization over both — herald-registration and post-selection-filtering are structurally different bookkeeping styles (a herald failure is a distinguishable click event; post-selection is a silent discard), and abstracting across both would claim coverage the model doesn't structurally have.
- **D-02: Allocation scheme — Pooled/recycled.** Ancilla modes reused across pairs that do not share a qubit index. Rejected alternatives, both with reasons that must be recorded per MPAIR-01: **Contiguous** (`2n+4m..2n+4m+3`, fixed per pair index) — rejected as likely true-by-construction, the same weakness ARB-09's audit found for the single-pair model. **Interleaved (round-robin)** — a different arithmetic, same true-by-construction shape, no advantage identified.
  - Forge-showcase rationale: pooled/recycled is the only candidate where "no collision for every subset of pairs" is load-bearing rather than a restatement of per-index arithmetic — a Forge counterexample would be an actual structure (a bad subset), not something a one-line parity argument rules out.
  - Research-meaningfulness rationale: attacks the actual bottleneck (4 extra modes per pair, flat cost) — mode-count growth sub-linear in k is the lever that could let a real future implementation reach k=4-5 instead of stalling at k=2-3.
  - Cost accepted knowingly: MPAIR-02's invariant is harder to state precisely (genuine subset-dependent condition, not four pairwise-distinct numbers); any eventual Python implementation is more code than contiguous's one-line formula.
- **D-03: Bound — n ≤ 8, k up to all C(n,2) pairs at that n** (max n=8 → C(8,2)=28 candidate pairs). Owner chose this knowing it risks an intractable Forge solve.
- **D-04: Fallback — hard time ceiling (5-10 minutes).** A timeout at the target bound is a REPORTABLE FINDING (paired with whatever largest bound did converge, timed), not a failure to engineer around. Do not silently shrink the bound and report only the smaller success.
- **Downstream note (from CONTEXT.md):** given pooled/recycled's subset-dependent semantics, the effective domain size is almost certainly larger than a pairwise-only model at the same (n,k) — plan an empirical bound-finding pass rather than assuming n=8/k=28 will simply run. *(This research's finding above complicates that framing further: whether the domain is genuinely subset-dependent, or reducible to pairwise, depends on which concretization of "pooled/recycled" is chosen — see Summary.)*

### Claude's Discretion

- **The precise pooling-compatibility rule.** CONTEXT.md's stated default is vertex-disjointness: two pairs `(i,j)` and `(i',j')` may pool only if `{i,j} ∩ {i',j'} = ∅`. CONTEXT.md explicitly asks the researcher/planner to state this precisely and **flag it back to the owner if it doesn't hold up**. This research finds a related but distinct concern that also needs flagging — see Pitfall 1 (Research Question 3) below: vertex-disjointness may be necessary but is not obviously sufficient, because it says nothing about whether *sequential* reuse of the same physical ancilla modes across two circuit components is unitarily valid given this pipeline's deferred (end-of-circuit-only) post-selection.
- Exact empirical procedure for finding the largest (n,k) that solves within the time ceiling.
- File location/naming for the new Forge model (separate file from `forge/ancilla_mapping.frg`, per CONTEXT.md's explicit instruction not to conflate the two properties in one file — e.g. `forge/pooled_ancilla_allocation.frg`).

### Deferred Ideas (OUT OF SCOPE)

- Python implementation of the k-pair (pooled/recycled) circuit.
- Re-running the hardness-under-loss study with multiple ZZ terms (v4.0-sized).
- A second owner review of the pooling-compatibility rule, once stated precisely — explicitly flagged as a checkpoint for the planner to surface back to the owner, not resolve silently.
</user_constraints>

<phase_requirements>
## Phase Requirements

| ID | Description | Research Support |
|----|-------------|------------------|
| MPAIR-01 | ≥2-3 candidate allocation schemes presented, no implied ranking, owner selects, rejection reasons recorded | Already resolved live in `22-CONTEXT.md` (D-02) — this research does not reopen it, but flags that the *concretization* of the chosen scheme (fixed-formula vs. dynamic) is a residual, unresolved design choice within D-02, not a re-litigation of D-02 itself |
| MPAIR-02 | Non-collision invariant written in prose before Forge code — what it quantifies over, what a counterexample looks like as a structure | Research Questions 1, 3, 4 below give the concrete vocabulary (`active: set Pair`, per-pair `block` assignment, pairwise-vs-subset formulation) the prose statement needs |
| MPAIR-03 | Forge model checking the invariant for every subset of pairs at every k up to a bound, over n up to a bound, with bound/bitwidth justified | Research Questions 1, 2 — concrete Forge syntax (verified against local examples) and the pairwise-reduction tractability argument |
| MPAIR-04 | Two-part `test expect` (sat non-vacuity, then unsat no-counterexample), matching `ancilla_mapping.frg`'s convention | Research Question 4 — states precisely what "non-vacuous" must mean once the model has a free `active` set (a vacuous instance could otherwise be the empty active set) |
| MPAIR-05 | Honest verdict on whether Forge's exhaustive search actually engages, via a timed brute-force baseline over the same domain | Research Question 5 — baseline design recommendation, and the honest expectation given the pairwise-reduction finding |
| MPAIR-06 | Verified scheme recorded in `docs/iqp-photonic-encoding.md` as a specification for future implementation (no Python implements it yet) | Follows `docs/iqp-photonic-encoding.md`'s "Forge Verification..." section structure (read directly, cited below) as the template, inverted for source-of-truth direction |
</phase_requirements>

## Standard Stack

No new packages. This phase uses:

| Tool | Version (confirmed live) | Purpose |
|------|---------------------------|---------|
| Racket | 8.15 [cs] | Forge's host language runtime |
| Forge | v5.2, linked from `C:\Users\cuqui\cs1710\forge\forge` | The verification DSL/solver interface (Kodkod/SAT-backed) |
| Python (stdlib only) | 3.12 (`venv/Scripts/python.exe`) | MPAIR-05's brute-force baseline script — no new packages needed, plain loops/`itertools` suffice |

**Version verification:** `racket --version` and `raco pkg show forge` both re-confirmed live during this research session (2026-08-20) — `[VERIFIED: raco pkg show forge]`, matching `16-CONTEXT.md`'s prior confirmation.

## Package Legitimacy Audit

Not applicable — this phase installs no new packages (Forge/Racket already installed and confirmed working per `16-CONTEXT.md`; MPAIR-05's baseline uses Python stdlib only).

## Architecture Patterns

### Recommended Project Structure

```
forge/
├── ancilla_mapping.frg              # existing, single-pair (Phase 16) — NOT extended in place
└── pooled_ancilla_allocation.frg    # new (this phase) — Claude's Discretion on exact name

results/
└── phase22_forge_summary.md         # pass/fail note + brute-force comparison table, sibling of phase16_forge_summary.md

docs/
└── iqp-photonic-encoding.md         # gains a new section, parallel to "Forge Verification of the Ancilla Mode-Mapping (Phase 16)"
```

### Research Question 1 — Forge set/subset modeling (concrete syntax)

`forge/ancilla_mapping.frg` models a single `(n,i,j)` triple using plain `Int` arguments to a `pred`, quantified with `some`/`all n,i,j: Int`. This does not extend to "a set of simultaneously-active pairs" — that needs a **sig with a set-typed field**, which is a different, well-established Forge idiom. Verified directly against four local example files already installed in this environment (`C:\Users\cuqui\cs1710\forge\forge\examples\...`), not from training-data recollection:

**`[VERIFIED: forge/examples/network/network.frg, forge/examples/prim/prim.frg]`** — the idiomatic pattern for "a relation that Forge is free to choose, bounded by a sig":

```forge
#lang forge

sig Pair {
    i: one Int,
    j: one Int
}

one sig Instance {
    active: set Pair,           -- the free "which pairs are simultaneously active" variable
    block: Pair -> one Int      -- the ancilla-block-index assignment (function, one per pair)
}
```

This is `network.frg`'s exact pattern (`sig Host { wires: set Host, forwarding: set Address -> Host }`) and `prim.frg`'s exact pattern (`sig Node { edges: set Node -> Int }`) applied to this domain. Crucially, `active: set Pair` and `block: Pair -> one Int` are **first-order relations over a bounded sig** — Kodkod (Forge's backend) solves for them natively via SAT, this is *not* the higher-order quantification `prim.frg`'s own comment warns is rejected. The rejected pattern is specifically **universally quantifying over a free relation inside a predicate body** (`all t2: set Node -> Node | ...` — `prim.frg` line ~284, explicitly commented "Forge will reject this Alloy-style syntax"). `active`/`block` above are sig *fields*, not `all`-quantified relation variables, so this restriction does not apply to declaring them.

**How to express "for every subset of pairs, no collision" as a checkable `test expect`:** follow `ancilla_mapping.frg`'s and `prim.frg`'s own established idiom — a universal claim over a free relation becomes a search for a counterexample (`is unsat`), not a literal `all S: set Pair` inside a predicate:

```forge
pred conflicts[p, q: Pair] {
    -- vertex-disjointness compatibility rule (Claude's Discretion default, see below)
    p.i = q.i or p.i = q.j or p.j = q.i or p.j = q.j
}

pred collision {
    some disj p, q: Instance.active | {
        conflicts[p, q]
        Instance.block[p] = Instance.block[q]
    }
    -- plus: block values must not collide with any qubit's own data ports (0..2n-1),
    -- same structural check ancilla_mapping.frg already performs
}

test expect {
    nonVacuous: { some Instance.active } for 6 Int, exactly 28 Pair is sat
    noCounterexample: { collision } for 6 Int, exactly 28 Pair is unsat
}
```

This is the direct set-based generalization of `ancilla_mapping.frg`'s own two-part pattern (`nonVacuous`/`noCounterexample`), with `active`/`block` playing the role the scalar `n,i,j` triple played before. `[VERIFIED: pattern directly modeled on ancilla_mapping.frg lines 79-90 plus network.frg/prim.frg sig-field idiom]`.

**Bitwidth vs. sig-bound interaction — confirmed distinct, per `ancilla_mapping.frg`'s own header note.** `for 6 Int` sets Forge's signed integer range (`[-32,31]`), independent of `Pair` sig cardinality (`exactly 28 Pair` or similar bounds n separately). The two bounds are orthogonal knobs and must both be justified: the `Int` bitwidth against the largest value the model computes (block indices and mode indices — for a scheme needing at most `n-1` block identities and mode arithmetic up to `2n+4·(n-1)+3`, at n=8 that is `2·8+4·7+3=47`, still comfortably inside `for 6 Int`'s `[-32,31]`... **note this actually exceeds 31** — `for 6 Int` would NOT be wide enough if physical mode indices are computed this way; **this is a concrete, checkable arithmetic risk the planner must verify against whatever final mode-index formula is chosen, likely requiring `for 7 Int` (range `[-64,63]`) instead of `for 6 Int`.** Do not silently reuse `for 6 Int` from `ancilla_mapping.frg` without recomputing the largest value this new model actually produces — the whole point of the bitwidth-note discipline `ancilla_mapping.frg` established is to make this check explicit each time, not copy the prior value forward.

### Research Question 2 — Tractability at the target bound

**The literal "2^28 subsets" framing in `22-CONTEXT.md`/`ROADMAP.md` describes what a *naive brute-force enumeration* would cost — it does not describe what Forge itself does, and it does not describe what a smarter combinatorial argument requires.**

**Key finding (reasoned from the structure of the collision predicate, not measured — flagged as such):** the collision condition `Instance.block[p] = Instance.block[q]` (for `conflicts[p,q]`-related pairs) is inherently **binary** — it only ever involves two pairs at a time. There is no three-or-more-way interaction in an index-collision property (unlike, say, a scheduling problem with resource-capacity constraints, where three simultaneously-active items can jointly violate a constraint that no two of them violate alone). Therefore:

> **If** the `block` assignment is a pure function of each pair's own identity `(i,j)` (i.e. `block[p]` does not depend on which *other* pairs happen to be in `active`), **then** "no collision for every subset of active pairs" is logically equivalent to "no collision for every *pair* of pairs that could be simultaneously active" — collapsing the check from `2^28` subsets to `C(28,2) + 28 = 406` pairwise cases at n=8.

This equivalence is exact (not an approximation or weakening) under that one condition, because: if some subset S has a collision, that collision is witnessed by *some* two elements of S (since the predicate is binary) — so a subset-level counterexample implies a pairwise-level counterexample, and the converse holds trivially (a colliding pair is itself a 2-element "subset"). **This is the single most important tractability lever this research identifies**, and it directly answers Research Question 2's ask for "a formulation that checks pairwise-compatibility-plus-transitivity instead of enumerating subsets" — it is **not weaker**, it is equivalent, given the stated (and checkable) condition. State this condition explicitly in MPAIR-02's invariant prose, and have the Forge model itself assert the pairwise formulation directly (as shown in the `collision` pred above, which is already pairwise, not subset-quantified) — Forge/Kodkod does not need to be told to "enumerate subsets" at all under this framing; `active` need not even appear as a quantified subset in the pairwise check, only in the non-vacuity sat check.

**The condition does NOT hold for a dynamic/adaptive allocation** (e.g. greedy first-fit coloring recomputed per active set, where `block[p]` depends on `active`) — there, the pairwise reduction is unsound, because two pairs individually compatible might still get reassigned differently depending on a third pair's presence. A dynamic scheme genuinely requires reasoning "for every subset S, [something about the allocation induced by S]" — and expressing "the allocation induced by S" inside a Forge predicate, when the allocation is itself a free relation Forge would need to solve for *per subset*, reintroduces the alternating-quantifier shape `prim.frg`'s own comment flags as rejected/impractical (`all t2: set Node -> Node | ...`, and separately, the `otherTree`-helper minimality check that the file's own author annotates: *"This takes longer to run than I am willing to wait"* even at 5-node/5-Int bound, `[VERIFIED: prim.frg lines 317-322]`).

**Recommendation:** choose a **fixed, subset-independent allocation formula** (the pairwise-reduction condition), not a dynamic/adaptive one. This is the modeling choice this research recommends flagging to the owner (see Summary) — a static edge-coloring of `K_n` (1-factorization) is a concrete candidate that satisfies this condition while remaining genuinely non-arithmetic-trivial.

**What this research could NOT determine — honestly flagged:** actual Kodkod solve time for the pairwise-reduced model at `n=8`/28 `Pair` atoms. `C(28,2)+28=406` clauses is almost certainly small for a SAT solver (network.frg-scale models solve in under a second; `ancilla_mapping.frg`'s own considerably more constrained 168-triple model took ~1.2s at `for 6 Int`), but sig-cardinality bounds (`exactly 28 Pair`) interact with symmetry-breaking overhead in ways this research did not measure. **Recommended empirical procedure:** grow `n` from 2 upward (matching `ancilla_mapping.frg`'s own convention of testing at the full stated bound directly, since the model is expected to be cheap under the pairwise reduction) — first confirm the pairwise-reduced model solves quickly at n=8 (expected: seconds, given the small clause count), and *only* explore a naive subset-quantified formulation (if the owner wants a direct comparison of "what naive would have cost") as a deliberately-time-boxed secondary experiment against the 5-10 minute ceiling, since that formulation is the one genuinely at intractability risk.

### Research Question 3 — The pooling-compatibility rule (mechanism check against the circuit's own structure)

Read `_build_weight2_cp_processor_no_postselect` (`iqp_photonic_encoding.py:576-646`) and `build_cp_insertion` (`iqp_photonic_encoding.py:282-354`) directly. Two facts matter:

1. **The CP(α) insertion is a genuine unitary, not a measurement.** `build_cp_insertion` wraps qubit i/j into dual rail via `PBS`, routes through the catalog gate, and unwraps — this is a fixed local `Circuit(8)`, composed into the outer `Processor` via `proc.add(mapping, cp_circuit)`. No measurement or projection happens at this point.
2. **Post-selection is deferred to the very end, by hand, after `.compute()`** — explicitly because `Processor.set_postselection()` raises `AssertionError: Post-selection conditions cannot compose with modes [...]` if a later component touches those same mode indices again (documented as Pitfall 3 in this repo's own `15-RESEARCH.md`, restated in this function's docstring at lines 582-586).

**Consequence for pooling (flagged as an open question, not resolved here — this is exactly the kind of gap `22-CONTEXT.md` asks the researcher to surface back to the owner):** vertex-disjointness governs whether two pairs' data-port usage can safely overlap in *identity* (both diagonal ZZ terms commute and are simultaneously "real" in a genuine multi-ZZ circuit only if they don't share a qubit's own port range at the same circuit position — actually, per the diagonal-layer structure, ZZ terms on overlapping qubits still commute and both legitimately apply, so vertex-sharing is about which pairs can co-occur as valid problem instances, not directly about physical mode-reuse safety). It says **nothing** about whether *reusing the same physical ancilla mode indices across two sequentially-composed `build_cp_insertion` unitaries* is valid. Specifically:

- CP(α)'s ancilla modes are not deterministically restored to vacuum mid-circuit — "success" (ancilla-vacuum) is a probabilistic outcome only resolved by the final measurement/post-selection.
- If a second pair's gate is applied later in the circuit sequence to the *same* physical ancilla modes a first pair's gate already used, that second unitary acts on whatever (generally non-vacuum, entangled) state resides there at that point — not a fresh vacuum. This is physically different from giving each pair its own dedicated ancilla modes for the full circuit duration.
- Inserting an *intermediate* post-selection/heralding step between pair uses (which would resolve this cleanly) is exactly the operation `set_postselection()` was already confirmed to reject when composed with later-touched modes (Pitfall 3, above) — so the existing pipeline architecture does not obviously support a safe intermediate reset even if the owner wanted one.

**This research's assessment:** vertex-disjointness (the qubit-index-sharing rule) and "safe to physically reuse the same ancilla rail across two sequential gates" are two **different, independently-necessary** conditions, and this project's own code/docs currently only address the first. Whether pooled/recycled ancilla reuse is physically valid *at all*, under this pipeline's deferred-post-selection architecture, is an open physics question this research cannot resolve with the available reading (it would require either a literature check on ancilla-reuse/garbage-collection techniques in linear-optical post-selected gates, or a from-scratch amplitude calculation) — **and it is explicitly out of the class of things Forge can check** (a unitarity/physical-validity claim, not a discrete structural one), matching the boundary `16-CONTEXT.md` already drew around Forge as a tool category.

**Recommendation for the planner:** state this precisely in MPAIR-02's invariant prose as an explicit scope boundary — "this Forge model verifies that no two simultaneously-*allocatable* pairs are assigned overlapping ancilla-block *index* ranges under the stated compatibility rule; it does **not** verify that reusing those physical modes across sequential CP(α) unitaries reproduces the same physics as giving each pair dedicated ancilla for the full circuit — that is a separate, unresolved question, flagged to the owner, out of scope for Forge." This satisfies MPAIR-06's honesty requirement (the doc must state what the spec does/doesn't establish) and directly follows the precedent `docs/iqp-photonic-encoding.md`'s own "What Forge alone added — stated honestly" section already set for Phase 16.

### Research Question 4 — Non-vacuity under a set-based model (MPAIR-04)

`ancilla_mapping.frg`'s `nonVacuous` check is `some n,i,j: Int | validTriple[n,i,j] is sat` — trivially non-vacuous once any valid triple exists. In a set-based model, `some Instance.active` (a non-empty active set exists) is a strictly weaker, potentially misleading check: it would pass even if `Instance.active` always has exactly one element in every satisfying instance (i.e. the model never actually explores the *combinatorial* case this phase exists to test).

**Recommendation:** the non-vacuity check for this model must specifically require **at least two simultaneously-active, mutually-compatible pairs** — the smallest instance that actually exercises the pooling behavior rather than the trivial single-pair case Phase 16 already covers:

```forge
nonVacuous: {
    some disj p, q: Instance.active | not conflicts[p, q]  -- 2 pairs, pooling-eligible
    Instance.block[p] = Instance.block[q]                  -- they DO share a block (pooling actually happened)
} for 6 Int, exactly 28 Pair is sat
```

This directly parallels this project's established pattern of measuring the *actually-exercised* scope rather than asserting a weaker existence claim (e.g. Phase 13's non-vacuity sanity check requiring the ZZ term be "clearly non-negligible," not merely present). State this explicitly in the model's header, matching `ancilla_mapping.frg`'s comment discipline.

### Research Question 5 — Brute-force baseline design (MPAIR-05)

ARB-09's baseline was a trivial 168-case Python loop, `< 1ms`. For this phase, MPAIR-05 requires a **fair** comparison, and the honest design depends directly on the Research Question 2 finding:

- **If the pairwise-reduction condition holds** (recommended, fixed allocation formula): the fair brute-force baseline is the **equivalent** pairwise Python loop — iterate all `C(28,2)+28 = 406` pair-of-pairs cases at n=8, check the same compatibility+collision logic. This is directly comparable to what the Forge model is *actually* checking (per Research Question 2's equivalence argument), and it will almost certainly also run in well under a second — the same "Forge's advantage never engaged" verdict ARB-09 reached is the honest expectation here too, and should be stated as a real possibility going in, not discovered as a surprise.
- **As a secondary, explicitly-labeled data point** (not the primary comparison, since it isn't what the recommended model actually checks): a naive subset-enumeration brute force, time-boxed against the same 5-10 minute ceiling D-04 already established, to give the owner a concrete "what the naive framing would have cost" number — this is the number that motivates presenting the pairwise-reduction as a genuine contribution rather than an assumption.
- Both should be timed and reported side-by-side with the Forge run, in a table directly modeled on `results/phase16_forge_summary.md`'s existing format (Forge time vs. brute-force time vs. coverage/bound).

**Honest expectation to state up front (not discovered as a surprise mid-phase):** given the pairwise-reduction finding, this phase may well reach the same "Forge's exhaustive-search advantage did not meaningfully engage" verdict Phase 16's audit reached — the domain, once reduced correctly, is small. MPAIR-05 explicitly accepts either verdict; the honest framing is that the interesting technical content of this phase is likely to be the **modeling exercise** (correctly reducing a subset-quantified claim to a pairwise one, and getting the allocation formula and compatibility rule right) rather than Forge's raw search power — consistent with, not a departure from, this project's pattern across `ancilla_mapping.frg`.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| "Smallest available block index" / greedy allocation, if a dynamic scheme is attempted anyway | A custom recursive Forge predicate | Forge's native `min[...]`/set-difference aggregation, following `prim.frg`'s own `candidatesWithWeights`/`minCandidateWeight` idiom (`fun minCandidateWeight: set Int { min[candidatesWithWeights[Node]]}`) | This is a directly-precedented, working Forge idiom in this environment's own example set — reinventing it risks re-discovering the same alternating-quantifier trap `prim.frg` already documents |
| Edge-coloring / 1-factorization of K_n, if adopted as the allocation formula | A from-scratch combinatorial derivation inside the Forge model | A standard round-robin tournament-scheduling formula (well-established construction, `n-1` or `n` colors) computed in Python/plain prose first, then encoded as a fixed Forge relation instance or arithmetic formula | This is settled combinatorics (1-factorization of complete graphs) — no need to re-derive it inside Forge; state the formula, then let Forge verify its collision-freedom property |

## Runtime State Inventory

Not applicable — this phase is not a rename/refactor/migration. Skipped per this section's own trigger condition.

## Common Pitfalls

### Pitfall 1: Vertex-disjointness is not obviously sufficient for physical ancilla reuse
**What goes wrong:** treating the vertex-disjoint compatibility rule as settling both "which pairs may share an ancilla-block *identity*" and "is it physically valid to reuse the *same modes* across sequential gates" — these are different questions (see Research Question 3).
**Why it happens:** the rule was proposed as a natural-sounding default in `22-CONTEXT.md` without a pass against `_build_weight2_cp_processor_no_postselect`'s actual deferred-post-selection architecture.
**How to avoid:** state the Forge model's scope boundary explicitly (verifies index-non-collision under the stated rule, not physical/unitary correctness of reuse) and flag the open physics question back to the owner, per CONTEXT.md's own instruction.
**Warning signs:** any write-up language that implies the Forge check "proves pooling is safe" rather than "proves the chosen index-allocation scheme doesn't collide."

### Pitfall 2: Confusing "Forge doesn't enumerate subsets" with "the property doesn't need bounding"
**What goes wrong:** assuming that because Kodkod solves via SAT rather than literal enumeration, the `2^28`-subset framing is irrelevant and any formulation will be fast.
**Why it happens:** SAT solving is not immune to combinatorial blowup — a *dynamic* allocation formula genuinely re-introduces exponential-shaped alternating quantifiers, which Kodkod handles by Skolemization/expansion, not magic.
**How to avoid:** commit to the pairwise-reduction condition (fixed, subset-independent allocation) up front, and treat any deviation from it as a deliberate, time-boxed experiment against the 5-10 minute ceiling, not the default plan.
**Warning signs:** a model that includes `all` quantification directly over a free relation inside a predicate body (the exact pattern `prim.frg`'s own comments flag as rejected/slow).

### Pitfall 3: Reusing `ancilla_mapping.frg`'s `for 6 Int` bitwidth without recomputing
**What goes wrong:** copying `for 6 Int` forward because it worked for Phase 16, without checking the new model's largest computed value.
**Why it happens:** the two models look similar (same repo, same author, same file family) but compute different arithmetic — pooled allocation likely needs block-index-dependent mode arithmetic that can exceed `2n+3`'s Phase-16 maximum of 19.
**How to avoid:** as shown in Research Question 1 above, a naive `2n+4·blockIndex+3` style formula reaches ~47 at n=8 with 7 block identities — already over `for 6 Int`'s `[-32,31]` range. Recompute the actual maximum for whatever final formula is chosen and select the bitwidth accordingly (likely `for 7 Int`), stating the arithmetic in a comment exactly as `ancilla_mapping.frg` already does.
**Warning signs:** any silent overflow/wraparound — Forge will not error on this, it will just quietly produce wrong integers within the declared bit range.

### Pitfall 4: This model is upstream of implementation — the drift-warning direction inverts
**What goes wrong:** copying `ancilla_mapping.frg`'s "DRIFT WARNING: this model re-states the Python formula" header verbatim — it doesn't apply the same way here.
**Why it happens:** superficial copy-paste of a working header pattern from the direct prior-art file.
**How to avoid:** per `22-CONTEXT.md`'s own note and MPAIR-06, there is no existing Python to drift *from* — this model is the **source of truth** a future implementation must be checked *against*. The header/doc language should say so explicitly (e.g. "no Python implements this scheme yet; a future implementation should be checked against this model's formula, not the other way around"), inverting Phase 16's drift-risk framing rather than restating it.
**Warning signs:** doc language that says "verified against source" when there is no source to verify against yet.

### Pitfall 5: Treating "Forge didn't earn its place" as a phase failure
**What goes wrong:** feeling pressure to make the domain artificially larger/slower to "justify" using Forge, given the pairwise-reduction finding likely makes this fast too.
**Why it happens:** natural but misplaced instinct after committing significant design effort to a formal-methods phase.
**How to avoid:** MPAIR-05 explicitly accepts either verdict (`"Either verdict satisfies the criterion; only an unchecked assertion fails it"` — `ROADMAP.md` Phase 22 success criterion 4). The honest finding is itself the deliverable, matching this project's established pattern (`ancilla_mapping.frg`'s own audit reached the same conclusion and it was reported plainly, not spun).

## Code Examples

### Two-part `test expect` pattern (verified against this repo's own precedent)

```forge
-- Source: forge/ancilla_mapping.frg lines 79-90, generalized per Research Question 1/4 above
test expect {
    nonVacuous: {
        some disj p, q: Instance.active | not conflicts[p, q]
        Instance.block[p] = Instance.block[q]
    } for 7 Int is sat

    noCounterexample: {
        some disj p, q: Instance.active | {
            conflicts[p, q]
            Instance.block[p] = Instance.block[q]
        }
        or
        -- ancilla blocks colliding with any qubit's own data ports
        some p: Instance.active, k: Int | {
            k >= 0 and k < multiply[2, n]
            -- k equals one of p's assigned ancilla mode indices
        }
    } for 7 Int is unsat
}
```

### Sig-field relation idiom (the core new technique this phase needs)

```forge
-- Source: forge/examples/network/network.frg (sig Host { wires: set Host, forwarding: set Address -> Host })
--         forge/examples/prim/prim.frg (sig Node { edges: set Node -> Int })
sig Pair { i: one Int, j: one Int }
one sig Instance {
    active: set Pair,
    block: Pair -> one Int
}
```

## State of the Art

Not applicable in the usual sense (no library-version churn here — Forge/Racket versions are already pinned and confirmed). The relevant "state of the art" is this project's own established Forge-usage convention, which this phase must extend rather than deviate from:

| Established pattern (Phase 16) | This phase's extension | Why extended, not replaced |
|---|---|---|
| Scalar `Int`-typed pred arguments (`n,i,j: Int`) | Sig-typed free relations (`Pair` sig with `active`/`block` fields) | Scalars cannot express "a set of simultaneously-present things whose count varies" — this is the actual new capability the phase needs |
| Bitwidth justified once, in a header comment | Bitwidth re-justified against the new model's own largest value (see Pitfall 3) | The discipline transfers; the specific number does not |
| Two-part `test expect` (`sat` then `unsat`) | Same shape, with non-vacuity strengthened to require genuine pooling (2+ compatible active pairs sharing a block), not mere existence | Prevents a new vacuous-truth failure mode specific to set-valued models (see Research Question 4) |

## Assumptions Log

| # | Claim | Section | Risk if Wrong |
|---|-------|---------|---------------|
| A1 | The collision predicate is purely binary (no 3+-way interaction), making the subset→pairwise reduction exact | Research Question 2 | If some other invariant is later added that isn't purely pairwise (e.g. a global ancilla-budget cap), the reduction breaks and the model must revert to genuine subset quantification |
| A2 | A round-robin edge-coloring (1-factorization) of K_n is a workable, concrete pooled-allocation formula that needs only n-1 or n block identities | Summary, Research Question 2 | Untested against the actual physics (Pitfall 1) and not yet owner-reviewed — presented as a candidate, not a locked design |
| A3 | Vertex-disjointness alone does not resolve whether physical ancilla-mode reuse across sequential gates is unitarily valid | Research Question 3 | If it turns out this pipeline's post-selection semantics DO make reuse safe (e.g. because the failure branches are harmlessly projected out at the very end regardless of intermediate reuse — a nontrivial claim this research did not verify either way), then this flagged concern is overcautious; but asserting safety without checking would be the worse error |
| A4 | Naive subset-enumeration brute force at n=8/k=28 (2^28 ≈ 268M) would plausibly exceed a reasonable Python runtime, though this was not measured | Research Question 5 | If it turns out fast in practice (Python subset iteration is sometimes faster than intuition suggests with early termination), the "secondary, time-boxed" framing is more conservative than necessary — low risk either way, since it's explicitly framed as a bounded experiment |

## Open Questions

1. **Is the round-robin edge-coloring allocation formula (A2) the scheme the owner actually wants, or is a different concretization of "pooled/recycled" intended?**
   - What we know: D-02 locked the *category* (pooled/recycled, vertex-disjoint compatibility) but not a specific formula.
   - What's unclear: whether the owner's original mental model was closer to a dynamic/greedy scheme (which resists the tractability reduction) or would be satisfied by a fixed, provably-correct coloring scheme.
   - Recommendation: the planner should present this as a concrete, scoped sub-decision at the top of MPAIR-02's prose-writing step — not a full re-run of MPAIR-01's attempt-first gate, but a specific "here is one concrete way to realize pooled/recycled; confirm or propose an alternative" checkpoint.

2. **Does the deferred-post-selection architecture actually permit safe ancilla reuse across sequential gates at all (Pitfall 1 / A3)?**
   - What we know: post-selection is applied once, at the very end, after all pairs' gates have been composed; `set_postselection()` cannot be called mid-circuit on modes touched again later (Pitfall 3, prior phases).
   - What's unclear: whether this deferred, single end-of-circuit filter is nonetheless mathematically equivalent to independent per-pair post-selection when ancilla modes are reused — this may be provably fine, provably broken, or genuinely open without a direct calculation.
   - Recommendation: state this explicitly as an unresolved scope boundary in the Forge model's header and in `docs/iqp-photonic-encoding.md`'s new section (MPAIR-06) — the Forge model verifies index bookkeeping, not this physics question. If the owner wants it resolved, that is separate scope (likely v4.0-sized, adjacent to the deferred multi-ZZ implementation work).

## Validation Architecture

### Test Framework

| Property | Value |
|----------|-------|
| Framework | None (Forge model runs standalone via `racket`, not wired into `pytest` — established convention, `16-CONTEXT.md`) |
| Config file | none |
| Quick run command | `racket forge/pooled_ancilla_allocation.frg` (exact filename per Claude's Discretion) |
| Full suite command | same — this is the only executable artifact this phase produces beyond the brute-force baseline script |

### Phase Requirements → Test Map

| Req ID | Behavior | Test Type | Automated Command | File Exists? |
|--------|----------|-----------|-------------------|-------------|
| MPAIR-03 | No index collision for any valid (active-pair-set, allocation) instance within bound | Forge `test expect ... is unsat` | `racket forge/pooled_ancilla_allocation.frg` | ❌ Wave (this phase) |
| MPAIR-04 | Non-vacuity (genuine pooling instance exists) | Forge `test expect ... is sat` | same command | ❌ Wave (this phase) |
| MPAIR-05 | Brute-force baseline timed and compared | Python standalone script | `venv/Scripts/python.exe pooled_allocation_baseline.py` (name TBD) | ❌ Wave (this phase) |

### Sampling Rate

- **Per task commit:** re-run `racket forge/pooled_ancilla_allocation.frg` after any predicate/bound change — this repo's own convention (`ancilla_mapping.frg`'s audit re-ran it directly rather than trusting a prior SUMMARY claim).
- **Per wave merge:** re-run both the Forge model and the brute-force baseline together, matching `results/phase16_forge_summary.md`'s side-by-side comparison table format.
- **Phase gate:** both `test expect` blocks passing (`sat`/`unsat` as specified), plus a timed brute-force comparison recorded, before `/gsd:verify-work`.

### Wave 0 Gaps

- [ ] `forge/pooled_ancilla_allocation.frg` — does not exist yet; this phase creates it (analogous to Phase 16 creating `forge/ancilla_mapping.frg` from nothing).
- [ ] Brute-force baseline script (Python, standalone, not in `tests/`) — new for this phase, per MPAIR-05.
- [ ] No pytest infrastructure gap — this phase deliberately stays outside `pytest`, matching Phase 16's precedent; `pytest.ini`'s `testpaths = tests` is unaffected.

## Security Domain

Not meaningfully applicable. This phase produces a standalone formal-verification artifact (Forge model + brute-force comparison script) with no network access, no user input, no authentication, no stored user data, and no runtime service — it is closer to a mathematical proof artifact than a software component. The ASVS categories (V2 Auth, V3 Session, V4 Access Control, V5 Input Validation, V6 Cryptography) do not apply to a bounded-domain SAT-model-checking script run locally by its own author. Documented here explicitly per the phase-researcher's requirement to state the boundary rather than silently omit the section.

## Sources

### Primary (HIGH confidence)
- `forge/ancilla_mapping.frg` — read directly, this repo's own established Forge convention and the direct prior-art model this phase extends.
- `C:\Users\cuqui\cs1710\forge\forge\examples\network\network.frg` — read directly, `[VERIFIED: local Forge example]` — sig-with-set-typed-field idiom (`wires: set Host`, `forwarding: set Address -> Host`).
- `C:\Users\cuqui\cs1710\forge\forge\examples\prim\prim.frg` — read directly, `[VERIFIED: local Forge example]` — `set Node -> Int` field idiom, `min[...]`/aggregation idiom, and the explicit documented limitation on `all t2: set Node -> Node` (higher-order quantification over a free relation) plus a measured real-world instance of that pattern being "too slow to wait for" even at trivial (5 Node, 5 Int) bound.
- `C:\Users\cuqui\cs1710\forge\forge\examples\basic\schoolPuzzle.frg` — read directly, `[VERIFIED: local Forge example]` — basic sig/pred/quantifier syntax confirmation.
- `results/phase16_forge_summary.md` — read directly, the comparison-table format and honesty framing MPAIR-05 must match.
- `.planning/phases/16-arb-01-extended-validation-postselection-bookkeeping/16-CONTEXT.md` — read directly, the Forge-as-tool-category scope boundary this phase must not cross (no complexity-theoretic/continuous-phase claims).
- `docs/iqp-photonic-encoding.md` §"Forge Verification of the Ancilla Mode-Mapping (Phase 16)" and §"What Forge alone added — stated honestly" — read directly, the exact honesty-framing template MPAIR-06 must extend.
- `iqp_photonic_encoding.py::build_cp_insertion` (lines 282-354) and `::_build_weight2_cp_processor_no_postselect` (lines 576-646) — read directly, the source of the Research Question 3 physics-boundary finding.
- Live-confirmed 2026-08-20: `racket --version` (8.15 [cs]), `raco pkg show forge` (v5.2, linked from `C:\Users\cuqui\cs1710\forge\forge`).

### Secondary (MEDIUM confidence)
- The round-robin/1-factorization edge-coloring recommendation (A2) — standard, well-known graph theory (not verified against a specific citation in this session; presented as a design candidate, not a locked fact).

### Tertiary (LOW confidence)
- None — where this research could not verify a claim (Research Question 3's physics question, actual Kodkod solve time at n=8), it is reported as an open question rather than a low-confidence guess.

## Metadata

**Confidence breakdown:**
- Forge encoding technique (Research Question 1): HIGH — grounded in this repo's own prior model plus four local, directly-read example files.
- Tractability argument (Research Question 2): MEDIUM — the pairwise-reduction equivalence is a sound logical argument (HIGH confidence in the argument itself), but actual measured solve time is unverified (explicitly flagged as needing empirical confirmation during planning/execution).
- Pooling-compatibility mechanism (Research Question 3): MEDIUM-LOW — a real, well-reasoned gap is identified and precisely stated, but not resolved; correctly flagged as an open question rather than answered.
- Non-vacuity design (Research Question 4): HIGH — direct extension of an already-verified local pattern.
- Brute-force baseline design (Research Question 5): HIGH — design is sound, but expected outcome (Forge not engaging) is a prediction, stated as such.

**Research date:** 2026-08-20
**Valid until:** No expiry pressure — Forge/Racket versions are pinned and stable; the open technical questions (Research Questions 2 and 3) do not go stale, they need resolution during planning/execution, not re-research.
