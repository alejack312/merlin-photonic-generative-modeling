# Phase 16: ARB-01 Extended Validation & Postselection Bookkeeping - Context

**Gathered:** 2026-08-08
**Status:** Ready for planning

<domain>
## Phase Boundary

Extend the Phase-15-validated `CP(alpha)` / `PostProcessedControlledRotationsItem` gate (ARB-01) three ways: (1) an n=3 mixed weight-1 + arbitrary-θ weight-2 composability test, direct parallel to Phase 13's weight-2 test; (2) a denser (16-point) α sweep with a plotted, closed-form-validated success-probability curve; (3) a Forge-verified structural correctness check of the ancilla mode-mapping used to embed the gate into the full photonic circuit. Depends on Phase 15's shipped gate wiring, `set_postselection`/ancilla-vacuum plumbing, and `ancilla_spec`.

</domain>

<decisions>
## Implementation Decisions

### Composability test design
- Reuse Phase 13's exact 3 `(n, i, j, thetas)` configs at n=3 (`test_wt2_composability_mixed_generators_n3`'s parametrization), each paired with a non-trivial α from the locked `NON_TRIVIAL_ALPHAS` set (`π/6, π/3, 2π/5`) instead of the fixed π/4 — uses `photonic_cp_iqp_distribution`, not `photonic_weight2_iqp_distribution`.
- TVD threshold: < 1e-6 against the extended exact qubit-side reference (`exact_qubit_iqp_distribution` with `pair_thetas`), matching Phase 13 and Phase 15's existing bar.
- Include the same non-vacuity sanity check Phase 13 used: TVD against the weight-1-only reference must be clearly non-negligible (proves the ZZ/CP term isn't vacuously inert). The specific threshold needs re-deriving under non-π/4 α (effective rotation strength differs) — measure first, then set a safe lower bound with headroom, following Phase 13's own reasoning pattern for its 0.1 threshold.
- Stay at n=3 only, per the roadmap's literal success criterion — no n=2 bonus case.

### α sweep specifics
- 16 points, uniform spacing across `[0, 2π)`, with the 4 already-validated values (`π/6, π/3, 2π/5, π`) folded into the sweep so the new curve visibly agrees with Phase 15's existing verified points.
- Run at n=2, `(i,j) = (0,1)` — same configuration as Phase 15's `test_cp_pipeline_success_probability_vs_alpha_table`, making this a direct extension of already-verified points, not a new config.
- Assert the closed-form match (`success_prob = 1/sigma_max(alpha)**4`) at every one of the 16 points, not just plot the measured values — turns the sweep into a validated dataset.
- Save the plot to `results/phase16_alpha_sweep.png` with the raw points in a companion `.csv`, matching this project's existing `results/` convention (e.g. `phase4_batch_sweep_comparison.png` + `.csv`).

### Forge model scope
- **Models the mapping dict**, not a literal `set_postselection` call — see Specifics below for the roadmap-wording correction. Target: the `mapping` dict in `_build_weight2_cp_processor_no_postselect` (`iqp_photonic_encoding.py` ~line 622-627): `{2i:0, 2i+1:1, 2j:2, 2j+1:3, 2n:4, 2n+1:5, 2n+2:6, 2n+3:7}`.
- **Relational Forge** (not temporal) — this is a static structural/injectivity property with no state transitions, ordering, or protocol involved.
- **Property:** for every valid `(n, i, j)` with `0 ≤ i,j < n`, `i ≠ j`, within the checked bound, the 8 values `{2i, 2i+1, 2j, 2j+1, 2n, 2n+1, 2n+2, 2n+3}` are pairwise distinct (injective) — and specifically checks collisions against **all n qubits'** data ports (`0..2n-1`), not just qubit i/j's, even though this is provably structurally impossible by construction (ancilla ports start at `2n ≥` max qubit port `2n-1`). Model the fully general correctness property, not the narrower one.
- **Bound:** n up to 6-8 (Claude's discretion on the exact value within that range) — exceeds the n=2,3 already covered by Python tests, and the arithmetic is simple enough that the Forge run should be effectively instant at this bound.
- **Pass criteria, two-part:** (1) a `sat` check confirming at least one valid instance exists (guards against a vacuously-true, over-constrained model — the classic Forge pitfall), then (2) an `unsat` check confirming no counterexample to injectivity/non-collision exists within the bound.
- **Explicitly not** an attempt to formalize IQP circuit hardness, gate commutativity, or any complexity-theoretic claim — discussed at length and ruled out of scope for Forge as a tool category (see Specifics and Deferred below).
- **Kept standalone**, not wired into the Python pytest suite — runs via Racket/`raco forge` directly, since Forge isn't a Python dependency and CI/local `pytest` runs shouldn't require Racket installed. Same separation Phase 14 used for Julia's hello-worlds vs. the Python suite.
- **Location:** new `forge/` directory for the `.frg` model file(s), parallel to `julia/`'s role for Phase 14's toolchain.

### Output & documentation
- `docs/iqp-photonic-encoding.md`: extend existing sections — add the 16-point sweep curve/reference alongside Phase 15's success-probability table, plus a short Forge verification note (what was modeled, pass/fail). Keeps this doc the single source of truth, matching every prior phase's pattern.
- Composability test + α sweep: added as `pytest` cases in `tests/test_iqp_photonic_encoding.py`, matching every prior phase's convention.
- Forge result: **not** wired into `pytest` — stays a standalone artifact, documented separately.
- `results/phase16_forge_summary.md`: a **simple pass/fail note**, not Phase 14's fuller go/no-go toolchain narrative (installation isn't in question here — Forge is already confirmed working). States what was modeled, the bound checked, the sat+unsat result, and a one-line verdict.
- `results/phase16_alpha_sweep.png` + `.csv`: the sweep plot and raw data.
- `STATE.md` decision log: record "Forge v5.2 (Racket 8.15) confirmed installed, linked from `C:\Users\cuqui\cs1710\forge\forge`" as a reusable technical fact, same style as the other `STATE.md` gotchas — so a future session doesn't have to rediscover this. Unlike Julia in Phase 14, there is no toolchain-spike risk for this phase; Forge was already installed and confirmed at the latest tagged release (v5.2) before planning began.

### Claude's Discretion
- Exact α value assigned to each of the 3 composability test configs (from `NON_TRIVIAL_ALPHAS`) — favor touching more of the validated range across the 3 configs rather than repeating one value.
- Exact sanity-check TVD threshold for the composability test's non-vacuity check.
- Exact n bound for the Forge model within the 6-8 range.

</decisions>

<specifics>
## Specific Ideas

- **Forge toolchain already verified live during this discussion**, not deferred to phase execution: `racket --version` → Racket 8.15 [cs]; `raco pkg show forge` → linked package at `C:\Users\cuqui\cs1710\forge\forge`; `git fetch --tags` against upstream `tnelson/forge` confirmed the checkout is already on `v5.2`, the latest tagged release (ahead-of-tag `dev` branch exists but was deliberately left alone — no reason to run unstable).
- **Roadmap wording correction:** Phase 16's success criterion 3 as written says "formally verify its `set_postselection` local→global ancilla mode-index translation." This literal call does not exist in the shipped CP-insertion pipeline — confirmed during this discussion that `Processor.set_postselection()` raises `AssertionError: Post-selection conditions cannot compose with modes [...]` if attempted on this pipeline (documented as Pitfall 3 in `15-RESEARCH.md`; the pipeline instead filters ancilla-vacuum by hand in `photonic_cp_iqp_distribution`, post-`.compute()`). The actual object being Forge-verified is the `mapping` dict described above, which is the real analog of what `set_postselection`'s local→global translation would otherwise do. Downstream research/planning agents should read the roadmap phrase as referring to this dict, not a literal API call.
- **Owner floated a larger ambition** — formalizing a genuine property about IQP circuits themselves (not just this one gate's wiring) via Forge, e.g. diagonal-gate-layer commutativity or a hardness-adjacent claim. Discussed in depth and the owner agreed to not pursue it in Phase 16: Forge is a bounded relational/SAT model finder suited to discrete structural properties (like the mode-mapping injectivity check), not continuous-phase algebra (this project's `CP(alpha)` gate has a continuous α, ruling out a discrete/Clifford-style encoding without weakening the claim) or complexity-theoretic hardness results (which are asymptotic theorems, not bounded-model-checkable properties — no model-finder tool, Forge included, verifies claims like BJS's IQP-hardness result). See Deferred below.

</specifics>

<deferred>
## Deferred Ideas

- **A "larger property about IQP circuits" via Forge (or another formal tool)** — e.g. diagonal-gate commutativity, or any complexity-theoretic hardness claim about IQP sampling. Not a Phase 16 deliverable; explicitly out of scope for Forge as a tool category given this project's continuous-α gate. If it resurfaces, it belongs either as a much bigger, separately-scoped formal-methods effort, or as a one-line "what this project's formal verification doesn't establish" note in Phase 20's write-up (that section's success criteria already call for this kind of honest scope statement).

</deferred>

---

*Phase: 16-arb-01-extended-validation-postselection-bookkeeping*
*Context gathered: 2026-08-08*
