---
phase: 15
phase_name: "ARB-01 Core Gate De-Risking & Validation"
project: "MerLin Photonic Generative Modeling"
generated: "2026-08-20"
counts:
  decisions: 6
  lessons: 4
  patterns: 4
  surprises: 3
missing_artifacts: []
---

# Phase 15 Learnings: ARB-01 Core Gate De-Risking & Validation

## Decisions

### Use α=π (not α=π/4) as the CP/CZ boundary-check literal value
`15-CONTEXT.md` originally stated the boundary as `α=π/4`; this was corrected to `α=π`, with the relationship `α=4θ` (CP's raw dial vs. this codebase's `Z_iZ_j` generator-angle convention `θ`, used in `pair_thetas`) stated explicitly in code comments and docs so the ambiguity would not resurface in later plans.

**Rationale:** `θ=π/4` (the pre-existing generator-angle convention) maps to `α=π` under the derived relationship `α=4θ`, not to `α=π/4`. Getting this wrong would have made every boundary-agreement check silently target the wrong value.
**Source:** 15-01-PLAN.md, 15-01-SUMMARY.md, 15-03-SUMMARY.md

---

### Use `build_circuit()` directly, not `build_experiment()`, for phase-only Simulator checks
`cp_gate_derisking.py` calls `PostProcessedControlledRotationsItem().build_circuit(n=2, alpha=...)` directly rather than wrapping with `build_experiment()`.

**Rationale:** The phase-only `Simulator.prob_amplitude` path needs only the bare unitary; `build_experiment()` adds herald/postselect metadata that isn't needed at this de-risking level and is deferred to the full-pipeline wiring stage. Matches `heralded_cz_derisking.py`'s established `measure_cz_phase` division of labor.
**Source:** 15-01-PLAN.md, 15-01-SUMMARY.md

---

### Name the CP ancilla-mode return value `ancilla_spec`, not `herald_spec`
`build_cp_insertion`'s second return value is deliberately named differently from `build_cz_insertion`'s `herald_spec`.

**Rationale:** CP's ancilla modes are all expected-vacuum (photon count 0) — post-selection — while `heralded_cz`'s herald ancilla expects a 1-photon click. Using a distinct name keeps the mechanism difference (post-selection+vacuum vs. ancilla-heralding) visible directly in the API, per this project's ARB-05 requirement to state gate-mechanism distinctions plainly rather than conflate them.
**Source:** 15-02-PLAN.md, 15-02-SUMMARY.md

---

### Read `ancilla_spec`/`herald_spec` live from the item's own `build_experiment().in_heralds`, never hardcode it
`build_cp_insertion` sources its 4-entry ancilla spec by calling `PostProcessedControlledRotationsItem().build_experiment().in_heralds`.

**Rationale:** Matches `build_cz_insertion`'s existing pattern of reading the spec from the gate object itself instead of assuming a fixed dict — keeps the code correct if the underlying Perceval gate implementation changes.
**Source:** 15-02-PLAN.md, 15-02-SUMMARY.md

---

### Outer processor sized `2n+4` with a 4-entry ancilla mode-mapping dict for CP, not `2n+2`
The full-pipeline wiring (`photonic_cp_iqp_distribution`) explicitly sizes the outer `Processor` and mode-mapping dict for CP's 4 ancilla modes, structurally different from `heralded_cz`'s 2.

**Rationale:** `build_cp_insertion` has 4 ancilla modes (local 4-7) vs. `heralded_cz`'s 2. This was flagged up front as the single most likely, cheapest-to-check culprit behind `15-RESEARCH.md`'s earlier failed full-pipeline attempt (TVD~0.3-0.4), and was verified explicitly before any deeper debugging.
**Source:** 15-04-PLAN.md, 15-04-SUMMARY.md

---

### `postselect_failure_prob` must include both ancilla-nonzero AND qubit-i/j pair-data invalidity, not just ancilla-nonzero
The full-pipeline measurement function (`photonic_cp_iqp_distribution`) folds per-qubit-pair (i,j) data invalidity into `postselect_failure_prob`, reserving `residual` strictly for genuine bystander-qubit leakage.

**Rationale:** `PostProcessedControlledRotationsItem.build_experiment()` registers ancilla-vacuum AND per-qubit-pair validity as one combined post-selection condition. Since downstream `PBS`/`HWP` components are per-pair photon-number-preserving, checking pair validity at final readout is mathematically identical to checking it right after the bare gate — so it belongs in the gate's own failure accounting, not a generic residual bucket. The literal plan recipe (ancilla-nonzero only → failure) reproduced the exact TVD~0.375 figure `15-RESEARCH.md` had flagged as unresolved; the corrected split matches the theoretical closed form to ~1e-15.
**Source:** 15-04-PLAN.md, 15-04-SUMMARY.md

---

## Lessons

### A full-pipeline TVD failure can hide a correct gate wiring behind an accounting bug elsewhere
`15-RESEARCH.md`'s original end-to-end CP attempt failed at TVD~0.3-0.4 and was flagged as an unresolved open risk potentially involving the PERM convention adapter. Once the bare-core convention adapter was independently confirmed correct (Plan 15-02) and the mode-count arithmetic was fixed (Plan 15-04 Task 1), the pipeline still initially reproduced the same TVD~0.375 figure — the actual root cause was a postselection-accounting classification bug (qubit-pair validity going into `residual` instead of `postselect_failure_prob`), not a wiring or convention bug at all.

**Context:** Diagnosed by isolating `build_cp_insertion` with a plain readout (no state-prep/diagonal/conjugation) and comparing per-basis-input success rates directly against the theoretical `p_success(α)=1/9` figure — this isolation step is what separated "wiring is fine" from "accounting is wrong."
**Source:** 15-04-SUMMARY.md

---

### Step 1 (direct analog of an already-solved convention-adapter fix) can succeed immediately once confounds are removed
Plan 15-02 budgeted a 3-step bounded debugging search (direct analog → re-run all 4 PERM combos → manual unitary inspection) because `15-RESEARCH.md`'s full-pipeline attempt had failed with all 4 combinations. In the isolated bare-core context (no PBS, no state-prep, no pipeline), Step 1 — the exact same `PERM([1,0])` fix already used for `heralded_cz` — worked immediately and exactly.

**Context:** Confirms that the full-pipeline TVD failure `15-RESEARCH.md` observed was caused by confounds elsewhere in the pipeline composition (or the mode-mapping-dict arithmetic later fixed in Plan 15-04), not by the ctrl/data convention-adapter search itself.
**Source:** 15-02-SUMMARY.md

---

### A hand-derived closed-form physical quantity can be wrong even when the algebraic identity around it is right
During Plan 15-03's attempt-first derivation, the operator identity (part a) was derived correctly by the owner via Socratic dialogue. But a first hand-derivation attempt at the closed-form success probability (part b), which assumed the gate's coupling matrix was block-diagonal by qubit pair, was checked numerically against the gate's own measured amplitudes and disproven — all 4 computational-basis inputs showed identical non-monotonic α-dependence, contradicting the wrong assumption's prediction.

**Context:** Resolved by consulting the primary literature (`arXiv:2405.01395` Section V-B, the paper `PostProcessedControlledRotationsItem`'s own docstring cites) directly via WebFetch, rather than continuing to guess at the internal matrix structure, and verifying the literature formula against `cp_gate_derisking.py`'s measured sweep before writing it into the doc.
**Source:** 15-03-SUMMARY.md

---

### `.planning/REQUIREMENTS.md`'s checkbox/status tracking can lag behind actually-completed phase work
Verification found that `REQUIREMENTS.md`'s ARB-01 through ARB-06 checkboxes and requirements-to-phase table still showed "Pending"/unchecked even though all 6 requirements were fully satisfied and independently re-verified against live code.

**Context:** Flagged explicitly as a bookkeeping/status-tracking gap outside the phase's own deliverables, not a phase-goal failure — but worth catching before it misleads future planning about what's actually done.
**Source:** 15-VERIFICATION.md

---

## Patterns

### Bare-gate → bare-core → full-pipeline de-risking sequence, each level independently verified before the next
Phase 15 validated `CP(α)` in three escalating, separately-committed stages: (1) bare-gate phase/structure via `Simulator.prob_amplitude` on the raw circuit (Plan 15-01), (2) bare-core convention-adapter wiring on this module's own dual-rail convention, isolated from PBS/state-prep/pipeline (Plan 15-02), (3) full-pipeline TVD validation against the exact reference (Plan 15-04). Each stage's own boundary-agreement check (α=π vs. `heralded_cz`) was re-verified independently at that stage's level rather than assumed to carry over from the previous stage.

**When to use:** Any time a new physical/gate primitive needs to be wired into an existing validated pipeline — isolate correctness at the smallest possible scope first (bare gate), then the next scope (convention adapter alone), then the full composition, so a failure at the outer level can be attributed to a specific layer instead of triggering a full re-debug of everything at once.
**Source:** 15-01-SUMMARY.md, 15-02-SUMMARY.md, 15-04-SUMMARY.md, 15-VERIFICATION.md

---

### Isolate a new component from surrounding pipeline confounds when a full-pipeline attempt fails to match a target
When `15-RESEARCH.md`'s full end-to-end CP wiring attempt failed to hit the target TVD, Plan 15-02 didn't re-attempt the same full-pipeline search — it stripped away PBS-wrap, state-prep, conjugation, and readout, and tested the bare gate + convention adapter alone. This isolation immediately surfaced that Step 1 (the direct analog fix) was actually correct, and the real problem lived elsewhere.

**When to use:** Whenever a multi-component pipeline fails to match a target output and the search for "which combination fixes it" has already been exhausted at the full-pipeline level without success — isolate the newest/most-suspect component alone before assuming the search itself is wrong.
**Source:** 15-02-PLAN.md, 15-02-SUMMARY.md

---

### Verify a numeric hand-derivation against already-measured data before trusting it, and consult primary literature the implementation itself cites if a derivation attempt fails
Established as a general practice during Plan 15-03: any closed-form physical/mathematical claim about a third-party gate implementation should be checked numerically against the gate's own measured amplitudes before being written into documentation. If a hand-derivation attempt is falsified this way, look first at whatever literature the third-party implementation's own docstring/source cites, rather than continuing to guess at internal structure.

**When to use:** Deriving any closed-form formula (success probability, phase relationship, etc.) for a gate/operator implemented by an external library — especially before it goes into a defensible write-up.
**Source:** 15-03-SUMMARY.md

---

### Attempt-first Socratic checkpoint for conceptual derivations, with wrong turns recorded verbatim in the doc
Plan 15-03's Task 1 was a blocking human checkpoint: Claude presented only the confirmed prerequisite ingredients (not the answer), the owner attempted the general-α operator identity and success-probability derivation themselves first (catching a real eigenvalue-vs-exponential error and an arithmetic slip along the way), and the actual Q&A — including the wrong turns — was recorded in `docs/iqp-photonic-encoding.md`, matching the document's existing ENC-01/ENC-05 style rather than being smoothed into only the polished final answer.

**When to use:** Any conceptual/theoretical derivation this project's CLAUDE.md flags as "the owner's job, not Claude's" — present ingredients, gate on the owner's own attempt via a blocking checkpoint task, then write up (with corrections shown, not hidden) rather than deriving and handing over the final answer.
**Source:** 15-03-PLAN.md, 15-03-SUMMARY.md

---

## Surprises

### Success probability vs. α is genuinely non-monotonic, not just gate-dependent
Independent live re-computation during verification found `|amplitude|²` at α = π/6, π/3, 2π/5, π to be 0.1745, 0.1111, 0.1001, 0.1111 — dipping then rising, confirmed against the closed-form `p_success(α)=1/σ_max^4` rather than being a table-printing artifact or coincidental duplicate row.

**Impact:** Confirms the phase's explicit requirement (ARB-04) that success probability be reported as a real function of α, never collapsed to a single number — the shape of that function turned out to be non-trivial (non-monotonic), which a single boundary-only measurement would have completely missed.
**Source:** 15-VERIFICATION.md

---

### The bare-core convention adapter needed zero extra debugging once isolated, despite the full-pipeline attempt having already exhausted a 4-combination PERM search
Plan 15-02 budgeted three escalating debugging steps specifically because `15-RESEARCH.md`'s prior full-pipeline attempt had already tried all 4 PERM combinations and failed (TVD~0.30 best case). In the isolated bare-core context, Step 1 alone succeeded immediately and exactly — Steps 2 and 3 were never needed.

**Impact:** Took less debugging time than planned/budgeted for; more importantly, it proved (rather than merely suggested) that the earlier full-pipeline TVD failure had nothing to do with the convention adapter itself, redirecting all further debugging effort in Plan 15-04 toward the composition/accounting layer instead.
**Source:** 15-02-SUMMARY.md

---

### The plan's literal postselection-accounting recipe reproduced the exact same TVD figure the earlier unresolved research finding had flagged
When Plan 15-04's Task 1 smoke test was run using the plan's literal recipe (ancilla-nonzero → failure, otherwise decode via `fock_to_bitstring`), it produced TVD~0.375 — matching `15-RESEARCH.md`'s previously flagged, unresolved TVD~0.3-0.4 finding almost exactly, even though the mode-count arithmetic fix (2n+4, 4-entry ancilla mapping) had already been applied.

**Impact:** This coincidence was the actual diagnostic signal that let the team distinguish "wiring bug" from "accounting bug" — the bare-core wiring (already independently confirmed correct in Plan 15-02) was not the problem; a specific, previously-unidentified postselection-classification error was. Fixing it dropped TVD from ~0.375 to floating-point noise (~1e-16).
**Source:** 15-04-SUMMARY.md
