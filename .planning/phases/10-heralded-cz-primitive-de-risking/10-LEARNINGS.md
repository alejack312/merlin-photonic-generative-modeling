---
phase: 10
phase_name: "Heralded-CZ Primitive De-Risking"
project: "MerLin Photonic Generative Modeling"
generated: "2026-08-20"
counts:
  decisions: 3
  lessons: 4
  patterns: 3
  surprises: 2
missing_artifacts: []
---

# Phase 10 Learnings: Heralded-CZ Primitive De-Risking

## Decisions

### Measure probability and phase via two separate object graphs, not one
`heralded_cz`'s herald-success probability was measured via `Processor(build_experiment())` + `compute_physical_logical_perf(True)` + `probs()` (reading `global_perf`/`physical_perf`/`logical_perf`), while the CZ phase sign was measured separately via a bare `Simulator(SLOSBackend())` built directly on `build_circuit()`'s 6-mode circuit, using `prob_amplitude()`.

**Rationale:** `Processor.probs()`/`Analyzer` are phase-blind by design (they only ever expose `|amplitude|²`), so no single API path can answer both the probability and phase-sign questions. Following 10-RESEARCH.md's explicit recommendation rather than trying to force one object graph to do both jobs.
**Source:** 10-01-SUMMARY.md (key-decisions), 10-RESEARCH.md (Architecture Patterns)

---

### Treat `logical_perf`'s purity as a checked fact, not an assumption
Asserted `not str(exp.post_select_fn).strip()` (empty post-select expression) plus zero-leakage across all `Analyzer` truth-table columns for the 4 computational-basis inputs, rather than assuming `logical_perf` equals the herald condition.

**Rationale:** `logical_perf` conceptually could bundle a second hidden filter beyond the herald (e.g., a data-validity filter). CONTEXT.md and 10-RESEARCH.md flagged this as an open discretion question. Explicitly checking `post_select_fn` emptiness and Analyzer leakage resolves it as a checked, regression-tested fact rather than a one-time eyeballed observation, and guards against a future `perceval-quandela` version silently adding a post-select expression to this catalog gate.
**Source:** 10-01-SUMMARY.md (key-decisions), 10-01-PLAN.md (Task 1, Task 2), 10-RESEARCH.md (Pitfall 3, Open Question 2)

---

### Keep literature-comparison language strictly descriptive, even though the numbers match exactly
`docs/iqp-photonic-encoding.md` states the measured 2/27 as an observation about this specific gate implementation, not as proof of equivalence to the general literature-cited heralded-CZ construction family, even though the measured figure numerically matches the previously-cited ~2/27 literature figure to the precision quoted.

**Rationale:** Matches the project's established "honesty-ledger" documentation pattern (measured numbers reported plainly, including what they don't prove) — a numeric match to a literature figure is not the same claim as "this implementation is the literature's construction."
**Source:** 10-01-SUMMARY.md (key-decisions), 10-01-PLAN.md (Task 3), 10-CONTEXT.md (Literature-comparison note placement)

---

## Lessons

### `numpy.float64` amplitude coefficients break StateVector construction with a misleading error
`pcvl.StateVector() += amplitude * pcvl.StateVector(state)` raised `ValueError: setting an array element with a sequence... inhomogeneous shape` whenever `amplitude` was a `numpy.float64` (e.g. `1/np.sqrt(2)`) rather than a plain Python `float`.

**Context:** Hit while building the superposition-input herald-success spot-checks (`|+⟩|+⟩`, `|+⟩|0⟩`) in Task 1. Diagnosed as a pybind operator-overload dispatch quirk in the installed `exqalibur` backend, not a physics or logic error — isolated live by reproducing the exact failing multiplication standalone. Fixed by casting amplitude coefficients to plain Python `float` before multiplying/adding `StateVector` terms, and building the accumulator by summing terms directly instead of starting from an empty `StateVector()` and using `+=`.
**Source:** 10-01-SUMMARY.md (Deviations from Plan)

---

### `Simulator.prob_amplitude` silently returns `0j` if herald ancilla photons are omitted from a manual input state
Building a manual 6-mode input for `Simulator.prob_amplitude` with the herald modes left at vacuum (`[0, 0]`) gives `amplitude = 0j` for every input/output pair — a result that looks like "the gate never succeeds" but is actually "the ancilla photons were never supplied."

**Context:** `add_herald(mode, expected)`'s `expected` count applies to input AND output — `heralded_cz` requires 1 real photon injected into each of modes 4 and 5 as part of the physical KLM/Knill-CZ ancilla requirement, not just an output detection condition. `Processor.with_input()` on a 4-length `BasicState` auto-fills this; the bare-circuit `Simulator` path has no such auto-fill and must read `HeraldedCzItem().build_experiment().in_heralds` (`{4: 1, 5: 1}`) to get the correct counts.
**Source:** 10-RESEARCH.md (Pitfall 1)

---

### `StateVector`/superposition inputs to `Processor.with_input` require full circuit_size and manual `min_detected_photons_filter`
A `StateVector` whose `BasicState` terms are only 4 modes long (matching the logical ctrl+data ports, not the full 6-mode circuit) raises `AssertionError: Input distribution contains states with a bad size`. Even after building correct 6-mode terms, `proc.probs()` then raises `ValueError: The value of min_detected_photons is not set` unless `proc.min_detected_photons_filter(...)` is called first.

**Context:** `Experiment.with_input`'s `SVDistribution`/`StateVector` dispatch asserts `svd.m == self.circuit_size` with no auto-fill, unlike the `FockState`/`BasicState` dispatch which auto-inserts herald modes. `min_detected_photons_filter` is likewise only auto-set by the `LogicalState` dispatch path, not the raw `StateVector` path. Resolved by building 6-mode `BasicState` terms directly (data/ctrl ports + explicit `[1,1]` herald modes) and calling `proc.min_detected_photons_filter(0)` before `probs()`.
**Source:** 10-RESEARCH.md (Pitfall 2)

---

### `build_circuit()` alone drops the herald entirely — must use `build_experiment()` for anything probability-related
Calling `HeraldedCzItem().build_circuit()` and wrapping it directly in a bare `Processor("SLOS", circuit)` produces a `Processor` with no heralds at all (`proc.heralds` empty, `proc.m == 6` not 4) — `probs()` reports raw unconditioned 6-mode output probabilities, no `global_perf`/`logical_perf` distinction.

**Context:** `build_circuit()` (source lines 54-72) builds a bare 6-mode `Circuit` with no `add_herald` calls; `build_experiment()` (lines 74-79) is what attaches `add_herald(4,1)`/`add_herald(5,1)`. This is exactly the mistake the phase's own success criteria explicitly warned against, and the plan enforced it via a `key_links` regex check (`HeraldedCzItem\(\)\.build_(experiment|circuit)`) to keep the two paths from being confused across the probability vs. phase code.
**Source:** 10-RESEARCH.md (Pitfall 4), 10-01-PLAN.md (key_links)

---

## Patterns

### Standalone de-risking script + paired pytest test, reusing an established repo convention
Built `heralded_cz_derisking.py` (plain module-level functions returning data, a `main()` that prints results and asserts, `if __name__ == "__main__": main()`) paired with `tests/test_heralded_cz_derisking.py` (imports named functions directly, one test per distinct claim, re-asserts with `pytest.approx`/`np.isclose`). Script owns build+print+assert-once in `main()`; test file owns import+re-assert-as-pytest-cases — no duplicated logic between the two.

**When to use:** Any phase whose job is to independently verify a specific library/API behavior (not shot-sampled, not assumed from literature) before building integration code on top of it. This is the second instance of the pattern in this repo (first: Phase 8's `perceval_fluency_demo.py` / `tests/test_perceval_fluency_demo.py`), making it a confirmed reusable convention, not a one-off.
**Source:** 10-01-SUMMARY.md (patterns-established), 10-RESEARCH.md (Recommended script/module structure)

---

### De-risk a primitive standalone, empirically, before integrating it into a larger circuit
Rather than trusting the literature-cited ~2/27 figure and building the full weight-2 circuit (heralded_cz + PBS conversion + phase corrections) directly, this phase isolated `heralded_cz` alone and empirically measured its herald-success probability, phase sign, and `logical_perf` purity — all independently confirmed programmatically before any integration work (Phase 11) touched it.

**When to use:** Whenever a plan depends on an external library primitive's behavior (probability, sign convention, filtering semantics) that is currently only known via literature citation or informal testing — verify it standalone with asserted, regression-tested checks before composing it into a larger system, so a later integration failure (e.g. an opaque TVD mismatch) can be attributed correctly instead of requiring re-derivation of the primitive's behavior under integration-test noise.
**Source:** 10-CONTEXT.md (Phase verification depth), 10-01-PLAN.md (objective/Purpose)

---

### Read structural facts from the library's own API instead of hardcoding them
Herald ancilla photon counts for manually-constructed `BasicState`s were read from `HeraldedCzItem().build_experiment().in_heralds` (returns `{4: 1, 5: 1}`) rather than hardcoded as literal `[1, 1]` values in the phase-check code.

**When to use:** Any time a manual/bare-circuit code path needs to replicate metadata that a wrapped/managed API path (`Processor`/`Experiment`) would otherwise auto-fill — reading it from the library's own introspection API keeps the manual path correct if the underlying catalog gate implementation changes, rather than silently drifting from a hardcoded assumption.
**Source:** 10-01-PLAN.md (Task 1, Phase path), 10-RESEARCH.md (Pitfall 1 "How to avoid")

---

## Surprises

### The measured figure matched the literature citation to floating-point precision, with zero discrepancy
The independently-measured herald-success probability (2/27 ≈ 0.07407407407407401, uniform across all 4 computational-basis inputs and both superposition spot-checks, differences only at the ~1e-16 floating-point-noise level) matched the previously-flagged, unverified literature figure exactly, rather than surfacing a discrepancy that would have required reconciling the doc's claims with reality.

**Impact:** Confirmed rather than contradicted the design doc's prior citation, but the phase's outcome was not assumed in advance — the verification work (building the assertions, hitting and fixing the StateVector float-casting bug) was still necessary and non-trivial, and the doc's language was deliberately kept descriptive ("observation," not "proof of equivalence") even given the exact numeric match, since matching one implementation's number to a literature figure doesn't prove the constructions are identical.
**Source:** 10-RESEARCH.md (Summary, "State of the Art"), 10-VERIFICATION.md (Observable Truths #1)

---

### All measured values matched research-session figures exactly on the first successful execution run
Beyond the one auto-fixed `numpy.float64` StateVector bug, every other measured value (herald-success probability, phase amplitudes, no-leakage check, `post_select_fn` emptiness) matched 10-RESEARCH.md's live-measured figures exactly on first successful run of the deliverable script — no additional debugging or numeric surprises during Task 1-3 execution.

**Impact:** The phase completed in 25 minutes with only a single deviation (the StateVector float bug), reflecting that the upfront research session (which had already run the code live against the venv) transferred cleanly into the deliverable artifact with minimal friction.
**Source:** 10-01-SUMMARY.md (Issues Encountered, Performance)
