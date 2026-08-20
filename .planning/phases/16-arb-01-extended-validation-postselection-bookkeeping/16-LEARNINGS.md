---
phase: 16
phase_name: "ARB-01 Extended Validation & Postselection Bookkeeping"
project: "MerLin Photonic Generative Modeling"
generated: "2026-08-20"
counts:
  decisions: 6
  lessons: 3
  patterns: 3
  surprises: 3
missing_artifacts: []
---

# Phase 16 Learnings: ARB-01 Extended Validation & Postselection Bookkeeping

## Decisions

### Forge models the mapping dict, not a literal `set_postselection` call
The roadmap's original wording ("formally verify its `set_postselection` local→global ancilla mode-index translation") was corrected during context-gathering: no such literal call exists in the shipped CP-insertion pipeline. `Processor.set_postselection()` raises `AssertionError` when composed with this pipeline's later components (documented as Pitfall 3 in 15-RESEARCH.md); ancilla-vacuum filtering is instead done by hand in `photonic_cp_iqp_distribution`. The actual object formally verified is the `mapping` dict in `_build_weight2_cp_processor_no_postselect` (`iqp_photonic_encoding.py:622-627`), which is the real analog of what `set_postselection`'s translation would otherwise do.

**Rationale:** Verifying a nonexistent API call would be meaningless; the mapping dict is the true load-bearing bookkeeping structure this property applies to.
**Source:** 16-CONTEXT.md (Specifics section, "Roadmap wording correction")

---

### Check the fully general injectivity property, not just the narrow i/j case
The Forge model checks that the 4 ancilla ports (`2n..2n+3`) don't collide with ANY of the n qubits' data ports (`0..2n-1`), not just qubit i's/j's ports — even though this is provably impossible by construction (ancilla ports start at `2n`, which is ≥ the max qubit port `2n-1`).

**Rationale:** Modeling the fully general correctness property (rather than the narrower, already-obviously-true one) is more rigorous and catches the case where a future code change might violate the invariant for some qubit other than i/j.
**Source:** 16-CONTEXT.md (Forge model scope); forge/ancilla_mapping.frg header comment

---

### Sanity-check TVD threshold recalculated per-phase rather than reused
Phase 13's non-vacuity sanity-check threshold (0.1) was measured at a fixed π/4 angle. Phase 16's composability test uses `theta = alpha/4` with smaller non-trivial alphas, producing genuinely smaller effective rotations (~0.13–0.31 rad vs π/4's ~0.785 rad). Reusing 0.1 literally would have caused false failures. The threshold was set to 0.005 (>3x headroom below the smallest observed value of 0.017) after measuring first.

**Rationale:** A threshold tied to specific numeric conditions from a prior phase does not transfer to a different parameter regime; measure-then-threshold-with-headroom is safer than reuse-by-analogy.
**Source:** 16-01-SUMMARY.md (Decisions Made)

---

### Bitwidth set via verification, not the owner's initial recollection
The owner initially recalled Forge's integer range as "0-7." This was checked against research rather than trusted, and found to be Forge's *default* 4-bit bitwidth's positive half (signed range [-8,7] at bitwidth 4) — not a hard language ceiling. The model's real largest value (`2n+3=19` at n=8) required `for 6 Int` (signed range [-32,31]) to avoid silent integer wraparound.

**Rationale:** Silent wraparound in a SAT model would produce a false "no counterexample" result without any error — verifying the owner's tentative recollection against independent research (16-RESEARCH.md Pitfall 4) before locking the model prevented a hidden correctness bug in the verifier itself.
**Source:** 16-03-SUMMARY.md (Owner's Attempt-First Exchange; Decisions Made)

---

### n bound set to 8 (top of the allowed [6,8] range)
Research had already confirmed n≤8 solves in ~1.2s, so there was no performance reason to pick a smaller bound within the range CONTEXT.md allowed.

**Rationale:** Wider verified envelope at no additional cost.
**Source:** 16-03-SUMMARY.md (Decisions Made); 16-CONTEXT.md (Forge model scope)

---

### Explicit pairwise `!=` assertions used instead of the owner's chosen set-cardinality trick
The owner's round-2 attempt explicitly named the set-cardinality trick (`#(k1+...+k8) = 8`) as their intended direction for expressing "8 keys are pairwise distinct." The plan instead used the research-verified pairwise-`!=` scaffold (already built and executed live during phase research) rather than re-deriving and re-verifying a new set-cardinality version.

**Rationale:** Both approaches check the identical mathematical property; the pairwise version was already proven working end-to-end and gives a more diagnostic failure message (which specific pair collided) than a bare cardinality mismatch. Flagged as a deviation from the owner's stated preference rather than silently substituted.
**Source:** 16-03-SUMMARY.md (Decisions Made; Deviations from Plan)

---

## Lessons

### `venv/Scripts/python.exe` is required, not system Python
The repo's virtual environment (not system Python) is required to run the test suite, since `perceval`/`merlin` are only installed there. This was noted as a recurring setup fact for future execution sessions.

**Context:** Discovered while running Task 2's full-suite regression check in Plan 16-01.
**Source:** 16-01-SUMMARY.md (Issues Encountered)

---

### `raco forge` does not exist in Forge v5.2 — use `racket file.frg` directly
Confirmed during phase research and carried into execution: the correct invocation is `racket forge/ancilla_mapping.frg`, not `raco forge`.

**Context:** Documented as Pitfall 2 in 16-RESEARCH.md; enforced explicitly in the plan's Task 2 instructions to prevent a session from trying the nonexistent subcommand.
**Source:** 16-03-PLAN.md (Task 2 action, citing 16-RESEARCH.md Pitfall 2)

---

### `option run_sterling off` is required on Windows to avoid a hang
Forge's default behavior tries to launch its Sterling visualizer, which hangs on Windows. Setting `option run_sterling off` as the file's second line avoids this.

**Context:** A toolchain-specific gotcha discovered/confirmed during phase research and required for the model to run non-interactively.
**Source:** 16-03-PLAN.md (Task 1, "Forge basics needed"); forge/ancilla_mapping.frg

---

## Patterns

### Bounded discrete-correctness verification via Forge for narrow bookkeeping questions
Using a formal relational model-finder (Forge/SAT) to verify a bounded, discrete structural property (here: injectivity of an 8-key index-mapping dict) rather than a continuous physics claim. The model is deliberately scoped away from anything requiring continuous algebra or asymptotic/complexity-theoretic reasoning, which Forge as a bounded model-finder cannot address.

**When to use:** When a piece of code contains discrete bookkeeping logic (index mappings, non-aliasing/uniqueness invariants, finite combinatorial structure) whose correctness matters but is hard to fully cover with example-based unit tests. Not appropriate for continuous-parameter physics or for asymptotic hardness/complexity claims — those require different tools entirely (numeric validation, closed-form checks, or literature-level proofs).
**Source:** 16-CONTEXT.md (Forge model scope; Specifics — "Owner floated a larger ambition"); 16-03-PLAN.md objective

---

### Attempt-first checkpoint for formal-method predicate design
Before writing any `.frg` code, present confirmed ingredients (target code, the property to check, and the minimal Forge syntax primitives needed) to the owner, then have them sketch the predicate(s) and the sat/unsat test structure themselves. Record the actual attempt — including wrong turns (e.g., confusing a "walk operator" with distinctness idioms) and gaps (missing bound, missing generality) — honestly in the summary rather than only the polished final answer. Executor then checks the owner's attempt against a research-verified scaffold, correcting and surfacing any divergence rather than silently replacing it.

**When to use:** Any phase introducing a new conceptual/formal-methods component (matches this repo's CLAUDE.md "attempt-first gating" for non-boilerplate work), especially when there's already a pattern from a prior phase (here: Phase 15-03's ARB-02 operator-identity derivation) to mirror.
**Source:** 16-03-PLAN.md (Task 1); 16-03-SUMMARY.md (Owner's Attempt-First Exchange, patterns-established)

---

### Offset-uniform-grid construction to merge pre-validated points with a denser uniform sweep
To extend a small set of already-validated discrete points (Phase 15's 4 alpha values) into a denser sweep (16 points) without collision, add uniformly-spaced points offset by half a step (`π/12`) so the new grid never lands exactly on the pre-existing values. This gives direct visual/numeric continuity with prior verification while still covering the full range densely.

**When to use:** Extending any existing sparse, already-verified parameter sweep into a denser one where visual/numeric continuity with the prior verified points matters (e.g., plotting a curve that must visibly pass through previously-confirmed markers).
**Source:** 16-02-PLAN.md (Task 1, "16-point construction"); 16-02-SUMMARY.md (patterns)

---

## Surprises

### Forge run was effectively instant (~1.2s) even at the widest allowed bound
Research had already confirmed n≤8 solves in ~1.2s total, meaning there was no performance tradeoff in choosing the top of the allowed [6,8] range — the widest verified envelope came at zero extra cost.

**Impact:** Removed what would otherwise have been a real design tradeoff (bound size vs. solve time), simplifying the "Claude's discretion" decision to "just pick the top of the range."
**Source:** 16-CONTEXT.md (Forge model scope: "the arithmetic is simple enough that the Forge run should be effectively instant"); 16-03-SUMMARY.md (Decisions Made)

---

### Non-vacuity TVD range was much smaller than Phase 13's, but the fixed threshold Phase 13 used would have been silently wrong, not just conservative
At the non-trivial alpha values used (paired via `theta = alpha/4`), the measured sanity-check TVDs (0.017–0.088) were far below Phase 13's fixed π/4-angle range (0.46–0.50). Naively reusing Phase 13's 0.1 threshold would have caused real, non-buggy test cases to fail.

**Impact:** Confirms that thresholds derived under one parameter regime cannot be assumed transferable to another, even within the same test family — required measuring the new regime directly rather than inheriting the old constant.
**Source:** 16-01-PLAN.md (Task 1 docstring); 16-01-SUMMARY.md (Decisions Made)

---

### Both required Forge checks (sat non-vacuity, unsat non-collision) passed on the very first run
The model matched the research-verified scaffold from 16-RESEARCH.md exactly and produced identical solve times/output on first execution — no debugging cycle was needed for the formal model itself.

**Impact:** Suggests the phase-research investment (building and live-testing the scaffold before planning) paid off directly, eliminating what is often the highest-risk step (getting a new-to-this-repo formal tool's model to actually run correctly) from the execution phase.
**Source:** 16-03-SUMMARY.md (Issues Encountered: "None — Forge ran cleanly on the first attempt, matching 16-RESEARCH.md's pre-verified scaffold exactly")

---

*Phase: 16-arb-01-extended-validation-postselection-bookkeeping*
*Learnings generated: 2026-08-20*
