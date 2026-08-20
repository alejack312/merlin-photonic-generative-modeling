---
phase: 13
phase_name: "Weight-1 + Weight-2 Composability Validation"
project: "MerLin Photonic Generative Modeling"
generated: "2026-08-20"
counts:
  decisions: 3
  lessons: 2
  patterns: 2
  surprises: 2
missing_artifacts: []
---

# Phase 13 Learnings: Weight-1 + Weight-2 Composability Validation

## Decisions

### Stack the weight-1 theta on a weight-2 pair member, not a disjoint qubit
At n=3, chose to place one weight-1 (Z) term directly on qubit 0 or 1 (already inside the weight-2 pair) plus one on qubit 2 (the bystander), rather than expanding to n=4 to keep all weight-1 and weight-2 qubits disjoint.

**Rationale:** Stacking is a strictly stronger test — it proves a qubit's independent Z term and its participation in the ZZ pair term compose correctly *on the same qubit*, not merely across disjoint qubits. At n=3 it's also the only way to reach "2 weight-1 + 1 weight-2" in the same circuit, since exactly one qubit sits outside any pair.
**Source:** 13-CONTEXT.md ("Circuit configuration" section); restated in 13-01-PLAN.md docstring and 13-01-SUMMARY.md key-decisions.

---

### Companion sanity-check threshold set to TVD > 0.1
Added a second assertion (beyond the primary TVD < 1e-6 correctness check) requiring TVD between the photonic distribution and the *weight-1-only* exact reference (`pair_thetas=None`) to exceed 0.1.

**Rationale:** Guards against a vacuously-passing test where the chosen thetas happen to make the ZZ term have near-zero effect. 13-RESEARCH.md measured actual sanity TVD of 0.46-0.50 for the three chosen configs, so 0.1 gives large headroom against flakiness while still ruling out an accidentally-inert weight-2 term.
**Source:** 13-CONTEXT.md ("Validation rigor" section); 13-01-PLAN.md task action; 13-01-SUMMARY.md key-decisions.

---

### Non-degenerate theta values required, not arbitrary ones
Weight-1 theta values were required to be nonzero, mutually distinct, and not multiples of π/4 (the three chosen configs: `[0.5, 0.0, 1.3]`-style tuples with the pair-adjacent qubit set to a non-trivial value).

**Rationale:** A symmetric or degenerate theta choice (all equal, zero, or π/4-aligned) could mask a real composition bug by accident — the test needs thetas that would expose a bug if one existed.
**Source:** 13-CONTEXT.md ("Theta values" section); 13-01-PLAN.md task action ("Do not use theta values that are zero, equal to each other, or multiples of pi/4").

---

## Lessons

### Whole-repo test count and single-file test count are different baselines — don't conflate them
The plan's verification step referenced "26 weight-1 tests" as a baseline inside one file, while STATE.md/ROADMAP.md tracked a whole-repo count (115 → 118 tests). The verifier initially flagged this as a discrepancy before resolving it by checking out the pre-commit file state and re-running both counts independently.

**Context:** `test_iqp_photonic_encoding.py` alone went 44 → 47 tests (including the 26 original weight-1-only tests as a subset), while the full `pytest -q` repo run went 115 → 118. Both are correct; they're just counting different scopes.
**Source:** 13-VERIFICATION.md ("Gaps Summary").

---

### Backslash paths for the venv Python failed in the bash execution environment
Running `venv\Scripts\python.exe` with backslashes did not resolve in the bash shell used during execution; forward slashes (`venv/Scripts/python.exe`) were required instead.

**Context:** A pure shell-syntax quirk of the Windows + bash-tool environment, not a code or test issue — noted so it isn't re-discovered as if it were a new bug.
**Source:** 13-01-SUMMARY.md ("Issues Encountered").

---

## Patterns

### Dual-reference TVD test: primary correctness check + companion "effect is non-vacuous" check
Structure a composability/correctness test as two TVD comparisons against two different exact references: (1) full exact reference (with the feature under test enabled) for tight correctness (TVD < 1e-6), and (2) a reference with the feature under test disabled/absent, asserting the TVD is clearly non-negligible (e.g. > 0.1) to prove the feature actually does something.

**When to use:** Any test validating that a new circuit term/generator/feature composes correctly with existing ones — guards against both "wrong implementation" (caught by check 1) and "implementation has no real effect, test passes by accident" (caught by check 2).
**Source:** 13-01-PLAN.md task action; 13-CONTEXT.md ("Validation rigor").

---

### Verify pre-computed research numbers via independent git checkout before trusting a SUMMARY's claimed test-count delta
Rather than trusting the SUMMARY.md's stated "115 → 118" test count claim at face value, the verifier checked out the pre-commit version of the test file (`git checkout` to commit before the phase's commit) and independently re-ran the suite to confirm the delta.

**When to use:** Any verification step that needs to confirm a claimed before/after count (test counts, coverage numbers, etc.) — re-derive from git history rather than trusting the summary's arithmetic.
**Source:** 13-VERIFICATION.md (Requirement 3 evidence and "Gaps Summary").

---

## Surprises

### REQUIREMENTS.md bookkeeping lagged the actual code/test completion
The phase's tests fully satisfied WT2-07 (verified passing, wired correctly), but `.planning/REQUIREMENTS.md` still listed WT2-07 as `[ ]` Pending at verification time — a documentation gap explicitly left for the orchestrator to close, not a code gap.

**Impact:** Non-blocking, but flagged as a recurring pattern to watch for at phase/milestone boundaries: code-complete and docs-complete can diverge by one step even when the plan explicitly delegates the doc update.
**Source:** 13-VERIFICATION.md ("Requirements Coverage" table and "Gaps Summary").

---

### The task ran first-try with zero deviations on a phase with historically fragile stall risk
This is described in the project's CLAUDE.md as a project where a prior track stalled; this phase (the smallest in the project, ~17 KB of artifacts) executed exactly as planned in ~10 minutes with no deviations, no plan/code mismatches, and all three parametrized cases passing on the first attempt.

**Impact:** Confirms that when a phase is scoped tightly (single success criterion, pre-verified numeric configs from RESEARCH.md, no source-code changes required), execution risk drops sharply — useful calibration for scoping future small validation-only phases.
**Source:** 13-01-SUMMARY.md ("Deviations from Plan": "None - plan executed exactly as written"; "Issues Encountered": "None. The plan's given test code ran and passed on the first attempt").
</content>
