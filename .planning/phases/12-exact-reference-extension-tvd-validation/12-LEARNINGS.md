---
phase: 12
phase_name: "Exact Reference Extension & TVD Validation"
project: "MerLin Photonic Generative Modeling"
generated: "2026-08-20"
counts:
  decisions: 5
  lessons: 3
  patterns: 3
  surprises: 3
missing_artifacts: []
---

# Phase 12 Learnings: Exact Reference Extension & TVD Validation

## Decisions

### Herald-failure probability and residual are reported as two separate, never-merged numbers
`photonic_weight2_iqp_distribution` returns a 3-tuple `(dist, residual, herald_failure_prob)` rather than folding herald failure into the residual or silently renormalizing it away. Herald mismatches accumulate into `herald_failure_prob`; separately, out-of-subspace decode failures (within the herald-success branch) accumulate into `residual`. `dist` and `residual` are renormalized by `(1 - herald_failure_prob)` so `sum(dist.values()) + residual ≈ 1.0`, but `herald_failure_prob` itself is always returned raw, never combined back in.

**Rationale:** This extends the project's pre-existing `(dist, residual)` convention (from `photonic_iqp_distribution`) rather than inventing a new shape, and CONTEXT.md explicitly locked the requirement: herald-failure probability "never merged into the residual, never silently renormalized away." The two numbers answer different questions — residual measures how much of the herald-success branch decoded outside the valid qubit subspace (should be ~0, a correctness signal), while herald_failure_prob measures the physical CZ-gate success rate (~2/27 at θ=π/4, an expected, non-zero physical quantity). Conflating them would hide a real correctness bug behind an expected physical inefficiency, or vice versa.
**Source:** 12-01-PLAN.md (Task 2, item 3), 12-CONTEXT.md line 50, 12-VERIFICATION.md criterion 2 (confirms residual=0.0 and herald_failure_prob=0.9259... as visibly distinct values in live execution).

---

### `_build_weight2_processor_no_herald` reuses `build_weight2_processor`'s exact wiring rather than re-deriving it
The herald-unregistered measurement-path processor is built by literally copying `build_weight2_processor`'s body (state prep, theta-folded diagonal layer, `build_cz_insertion` via the same mode-mapping dict, conjugation, readout) and deleting only the two `add_herald` calls, still returning the same `herald_spec`.

**Rationale:** If the measurement path re-derived its own wiring/mode-mapping independently, drift between it and the production function would silently invalidate the TVD validation's claim to be testing what's actually shipped. Reuse guarantees the thing being measured is the thing being deployed.
**Source:** 12-01-PLAN.md (Task 2), 12-01-SUMMARY.md key-decisions, 12-VERIFICATION.md artifact table (confirmed by line-by-line comparison).

---

### Ancilla input photons explicitly annotated `{P:V}`, not `{P:H}` or bare integer
`_weight2_input_state` builds the herald ancilla ports with an explicit `{P:V}` polarization annotation, generated off `herald_spec`'s photon-count values rather than hardcoded.

**Rationale:** Perceval's `PolarizationSimulator` silently defaults ancilla photons to `{P:H}` if not explicitly annotated, and `{P:H}` is confirmed wrong — it produces TVD~0.4639 with no error or crash to flag the problem. `{P:V}` was confirmed by research to match a trusted PBS-free ground truth to TVD~1e-16. This is called out in the plan as "the single most load-bearing line in the whole plan" precisely because a regression here produces no test failure at most configs, only a large TVD at the locked n=2/θ=π/4 gate.
**Source:** 12-01-PLAN.md (Task 2, item 2, and Verification section), 12-01-SUMMARY.md key-decisions.

---

### `photonic_weight2_iqp_distribution` does not expose `pair_theta` as a caller parameter
The π/4 fold is hardcoded inside `_build_weight2_processor_no_herald`, matching `build_weight2_processor`, rather than being a function argument.

**Rationale:** The CZ/ZZ operator identity underlying the weight-2 photonic construction is only exact at θ=π/4; any other value would produce numerically-valid but physically-meaningless output. Exposing it as a parameter would invite misuse.
**Source:** 12-01-PLAN.md (Task 2, item 3), 12-01-SUMMARY.md key-decisions.

---

### Filed the confirmed `add_herald()` + `PBS` crash as a live upstream GitHub issue rather than drafting to disk
Plan 12-02 attempted `gh issue create --repo Quandela/Perceval` first, per the plan's stated preference, and it succeeded (issue #783) since `gh auth status` was already authenticated with repo scope and the slug resolved on the first check. The disk-draft fallback path was available but not needed.

**Rationale:** CONTEXT.md required filing the bug report (repro already fully characterized) or a fully-drafted fallback if filing was blocked — filing live is lower-friction than a draft when nothing blocks it, and is directly relevant context for the Vincent Espitalier / Quandela conversation this project is building toward.
**Source:** 12-02-PLAN.md (Task 2), 12-02-SUMMARY.md key-decisions and Accomplishments.

---

## Lessons

### `Processor.add_herald()` combined with a `PBS`-containing circuit crashes `Processor.probs()` unconditionally
Calling `add_herald()` on a processor whose circuit contains a `PBS` (polarizing beam splitter) and then calling `.probs()` raises a `ValueError: matmul: Input operand 1 has a mismatch in its core dimension 0` (exact shape varies by mode count, e.g. "size 8 is different from 12"). This is independent of theta values or state preparation — a pure library-level structural bug, not a modeling error.

**Context:** Discovered as a carried-forward blocker from Phase 11 and confirmed by dedicated research before Phase 12 execution began (12-RESEARCH.md Pitfall 3). Worked around by building a herald-unregistered sibling processor and post-selecting on ancilla output modes by hand, rather than by any change to thetas/state prep (those don't affect the crash).
**Source:** 12-01-PLAN.md (Task 2 action, Verification section), 12-02-PLAN.md (Task 2 action), 12-VERIFICATION.md.

---

### Perceval's `PolarizationSimulator` silently defaults unannotated ancilla photons to `{P:H}`, producing wrong-but-plausible numbers with no crash
Without the explicit `{P:V}` annotation, the same measurement code runs to completion and returns a distribution, but the TVD against the exact reference is ~0.4639 at the locked n=2/θ=π/4 configuration instead of ~1e-16 — a silent correctness bug, not a crash.

**Context:** This is more dangerous than the `add_herald`+`PBS` crash precisely because it fails silently. The mechanistic "why" `{P:V}` (rather than `{P:H}` or any other explicit annotation) is correct was left as an explicitly non-blocking open question in 12-RESEARCH.md — the fix was empirically confirmed against a trusted PBS-free ground truth, but the underlying `PolarizationSimulator` distinguishability mechanism was not fully explained.
**Source:** 12-01-PLAN.md (Task 2, item 2), 12-01-SUMMARY.md "Next Phase Readiness" (flags the open mechanistic question as non-blocking).

---

### The ROADMAP's requirement-range shorthand (WT2-01 through WT2-05) did not exactly match the phase's actual locked requirement set (WT2-02/03/05/06)
Verification found a labeling discrepancy: ROADMAP text names a range that includes WT2-01 and WT2-04, but those belong to earlier phases (state prep / heralded-CZ de-risking, Phase 10-11), not Phase 12. The plan frontmatter and CONTEXT.md's actual requirement set was WT2-02/03/05/06, which is what was delivered and is correct.

**Context:** Verifier treated this as a documentation imprecision in the ROADMAP text, not a coverage gap, and did not block on it — but it's worth checking ROADMAP requirement-ID ranges against a phase's own PLAN frontmatter rather than trusting the range literally when scoping future phases.
**Source:** 12-VERIFICATION.md criterion 4 note, "Gaps Summary."

---

## Patterns

### Build a herald-unregistered sibling processor and post-select on ancilla output modes by hand, when combining `add_herald` with `PBS`
For any Perceval circuit combining `add_herald()` with a `PBS`, don't call `add_herald` on the processor used for measurement/validation — construct a second processor with identical wiring but without the herald registration, run `.probs()` on it, then manually check whether the ancilla output modes match the expected herald pattern and bucket probability mass into herald-failure vs. herald-success accordingly.

**When to use:** Any future Perceval circuit that needs both PBS-based polarization encoding and heralded ancilla photons (heralded gates), where `Processor.probs()` would otherwise crash. Established as a named, reusable pattern in the summary's patterns-established list, generalizing Plan 11-02's `_build_weight2_tail_no_state_prep` precedent.
**Source:** 12-01-SUMMARY.md patterns-established, tech-stack.patterns.

---

### Mirror production wiring exactly in a measurement-path processor; never re-derive it independently
When building a parallel/diagnostic version of a production processor (e.g. to work around a library bug during validation), copy the production function's construction code and only remove the minimal piece causing the problem, rather than reconstructing the wiring/mode-mapping from scratch.

**When to use:** Any time a test or validation harness needs a processor variant that differs from production only in a narrow, library-limitation-driven way. Prevents silent drift between what's validated and what's shipped.
**Source:** 12-01-SUMMARY.md tech-stack.patterns, key-decisions.

---

### Report conditional/post-selected distributions as an explicit N-tuple of never-merged accounting terms, not a single renormalized number
When a measurement pipeline has multiple distinct sources of "missing" probability mass (e.g. herald failure vs. out-of-subspace decode failure), keep each as its own explicitly named, explicitly reported value, and state exactly which subset of them sum to 1.0 in the docstring, rather than collapsing them into one number for convenience.

**When to use:** Any physical simulation or measurement pipeline with more than one failure/rejection mechanism, especially where one mechanism (physical device inefficiency) is expected and benign while another (out-of-subspace mass) is a correctness signal that should stay near zero.
**Source:** 12-CONTEXT.md line 50 (the locked rule), 12-01-PLAN.md Task 2 item 3, 12-01-SUMMARY.md tech-stack.patterns.

---

## Surprises

### The confirmed fix and both Perceval bugs were fully pre-resolved by research before execution began, so Plan 12-01 hit zero new issues
Both the plan and its summary state explicitly that research (12-RESEARCH.md) had already resolved both open questions (the `{P:V}` annotation fix and the `add_herald`+`PBS` crash workaround) before Plan 12-01 started, and that the plan's verification commands and full-suite run all passed on first attempt with no deviations.

**Impact:** Task 3's full-suite run (115/115 tests) and the TVD gate both passed on the first try; execution took only ~25 minutes for Plan 01. This is notable against the project's general pattern (per project CLAUDE.md) that Jul 25-equivalent stages are historical stall points — this phase avoided that because the risky unknowns were front-loaded into the RESEARCH phase rather than discovered mid-execution.
**Source:** 12-01-SUMMARY.md "Deviations from Plan" and "Issues Encountered" (both "None").

---

### TVD landed at machine-precision levels (2.58e-15), far below the locked 1e-6 gate
The locked pass/fail gate required TVD < 1e-6; the actual measured value at n=2, θ=π/4 was 2.581268532253489e-15 — roughly 9 orders of magnitude tighter than the required bar, and reproduced identically across three independent measurements (Plan 12-01's test, Plan 12-02's write-up re-run, and the phase verifier's independent re-execution).

**Impact:** Confirms the `{P:V}` fix + herald-unregistered-processor workaround is not merely "good enough" but recovers exact agreement with the analytical reference, strengthening confidence that the weight-2 photonic construction is mathematically correct rather than approximately close. All three independent re-executions matched exactly, which also validates that no floating-point-order-dependent nondeterminism is present in the pipeline.
**Source:** 12-01-SUMMARY.md headline result, 12-02-SUMMARY.md headline result, 12-VERIFICATION.md criterion 3.

---

### `gh issue create` succeeded on the first attempt with no auth/access blocker, despite the plan explicitly time-boxing a disk-draft fallback
The plan (12-02-PLAN.md Task 2) anticipated filing could be "genuinely blocked (no repo access/auth)" and built in a full fallback procedure (draft to `results/phase12_perceval_bug_report_draft.md`, flag the gap in SUMMARY). None of that was needed — `gh auth status` was already authenticated with repo scope and `Quandela/Perceval` resolved on the first `gh repo view` check.

**Impact:** The upstream bug report is live and public (Quandela/Perceval#783) rather than sitting as an unfiled local draft, giving the project a concrete, verifiable artifact relevant to the Vincent Espitalier / Quandela conversation without requiring later manual follow-up.
**Source:** 12-02-SUMMARY.md "Decisions Made" and "Deviations from Plan" ("plan's fallback draft-to-disk path was not needed").
