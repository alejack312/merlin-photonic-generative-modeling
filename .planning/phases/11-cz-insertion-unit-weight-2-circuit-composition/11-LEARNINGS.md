---
phase: 11
phase_name: "CZ Insertion Unit & Weight-2 Circuit Composition"
project: "MerLin Photonic Generative Modeling"
generated: "2026-08-20"
counts:
  decisions: 5
  lessons: 4
  patterns: 5
  surprises: 3
missing_artifacts: []
---

# Phase 11 Learnings: CZ Insertion Unit & Weight-2 Circuit Composition

## Decisions

### Convention adapter lives inside build_cz_insertion, not in the caller's mode-mapping dict
`build_cz_insertion(n, i, j)` wires the ctrl/data dual-rail swap fix (two `PERM([1,0])` pairs, immediately before/after `heralded_cz`'s bare circuit) fully internally. The function's external contract is: give it qubit i's/j's ports in the module's normal `(polarization-mode, vacuum-partner)` order, get back a correctly-signed CZ. The caller's mode-mapping dict in `build_weight2_processor` stays plain and unswapped (`{2i:0, 2i+1:1, 2j:2, 2j+1:3, 2n:4, 2n+1:5}`).

**Rationale:** Keeps the module's "everything is a plain Circuit" pattern; a bug in the swap is then visible in one function instead of smeared across every call site that wires in a CZ. Matches the "reusing weight-1 builders unmodified" spirit already established in the module.
**Source:** .planning/phases/11-cz-insertion-unit-weight-2-circuit-composition/11-01-PLAN.md, 11-RESEARCH.md (Open Question 1)

---

### heralded_cz's ctrl/data mismatch is framed as a convention adapter, not a bug fix
`heralded_cz.py` uses Perceval's own `Encoding.DUAL_RAIL` standard (logical 1 -> Fock pattern (0,1)), which is the exact mirror image of this module's own PBS-derived convention (H/bit "0" -> (0,1), established in Plan 09-02 from measuring real physical PBS port behavior). Both conventions are independently correct and internally consistent; they were never chosen to agree because one is a physics-driven convention and the other is an abstract qubit-encoding standard.

**Rationale:** Distinguishes this case from Plan 09-02's H/V port-labeling fix, which *was* an actual bug in this module's own code. Framing the fix as an adapter at a boundary between two correct components (rather than "correcting" either side) is called out explicitly as "a good habit regardless" when combining two encoding schemes.
**Source:** .planning/phases/11-cz-insertion-unit-weight-2-circuit-composition/11-RESEARCH.md (Summary, Pitfall 1), 11-01-PLAN.md (objective)

---

### Herald registration is bare-Circuit + explicit manual add_herald, not auto-propagating Experiment composition
`build_cz_insertion` returns a bare `Circuit(6)` plus a separately-surfaced `herald_spec` (read from `HeraldedCzItem().build_experiment().in_heralds`, never hardcoded). The caller wires it into the outer `Processor` via a mode-mapping dict, then calls `Processor.add_herald()` immediately afterward at the shifted global indices, rather than composing `HeraldedCzItem().build_experiment()` directly (which would auto-propagate heralds via `Experiment._compose_experiment`).

**Rationale:** The automatic Experiment-composition path appends new herald modes "at the bottom" of the processor's total mode count *at the time of that .add() call* — order-dependent and opaque about which global indices end up heralded. Explicit, immediate re-registration is auditable: a reader can state the exact global herald indices in a docstring/assertion instead of relying on an internal composition-order side effect.
**Source:** .planning/phases/11-cz-insertion-unit-weight-2-circuit-composition/11-RESEARCH.md (Architecture Patterns), 11-CONTEXT.md (Herald wiring decision)

---

### Theta folding for the CZ/ZZ identity is additive into the same thetas argument, never a separate gate or replacement
`thetas_folded[k] = thetas_base[k] + pi/4` for `k in {i, j}` only; all other qubits' thetas pass through unchanged. The caller's list is copied, never mutated.

**Rationale:** Realizes `exp(i*pi/4*Z_i*Z_j) = CZ . exp(i*pi/4*Z_i) . exp(i*pi/4*Z_j)` (up to global phase, documented in docs/iqp-photonic-encoding.md). Deciding this now (additive, not exclusive) avoids retrofitting the composition logic in Phase 13, which needs a well-defined mixed weight-1+weight-2 circuit.
**Source:** .planning/phases/11-cz-insertion-unit-weight-2-circuit-composition/11-CONTEXT.md (Theta folding decision), 11-02-PLAN.md

---

### Non-regression snapshot on a shared weight-1 builder's unitary, beyond just re-running the existing suite
Added a sha256 snapshot check on `build_state_prep_circuit(2)`'s unitary as a hardcoded expected value, captured during this plan's own execution, specifically to catch a *future* accidental edit to `build_state_prep_circuit` or its `WP`/`HWP` dependencies.

**Rationale:** Phase 9 already had one silent labeling bug (H/V ports) that no test caught until a direct calibration check was added; this is the same category of risk (a phase whose real focus is elsewhere accidentally editing a module every prior phase depends on).
**Source:** .planning/phases/11-cz-insertion-unit-weight-2-circuit-composition/11-CONTEXT.md (Regression rigor decision), 11-02-PLAN.md (Task 2)

---

## Lessons

### Simulator+SLOSBackend cannot process circuits containing PBS
`SLOSBackend.set_circuit` asserts `not circuit.requires_polarization`, so the plan's original intent (test `build_cz_insertion`'s full returned circuit directly via `Simulator(SLOSBackend())`) is not executable as written — `PBS` components trip the assertion immediately.

**Context:** Discovered during Plan 11-01 Task 2 while writing the truth-table tests. Not caught during research because 11-RESEARCH.md's executed examples used only the bare (PBS-free) dual-rail core, not the full PBS-wrapped function.
**Source:** .planning/phases/11-cz-insertion-unit-weight-2-circuit-composition/11-01-SUMMARY.md (Deviations)

---

### Processor.add_herald() combined with any PBS-containing circuit crashes Processor.probs() unconditionally
Confirmed by direct execution across multiple theta values and with/without state_prep: always the same `ValueError: matmul: Input operand 1 has a mismatch in its core dimension 0 ... (size 12 is different from 16)` inside `perceval/simulators/polarization_simulator.py`'s `_prepare_input`. The crash is triggered purely by the combination of a registered herald plus any PBS-containing circuit passed through `Processor.probs()` — independent of circuit parameters.

**Context:** Found while writing `test_weight2_herald_success_sanity` in Plan 11-02. This is a genuine Perceval library limitation with no workaround at the `Processor.probs()` level, and is a hard blocker for Phase 12's TVD validation, which cannot call `.probs()` on `build_weight2_processor`'s output as-is.
**Source:** .planning/phases/11-cz-insertion-unit-weight-2-circuit-composition/11-02-SUMMARY.md (Deviations, Issues Encountered)

---

### PolarizationSimulator silently mislabels unannotated heralded-ancilla photons, causing wrong (non-crashing) probabilities under real superposition input
Separately from the crash above: even without `add_herald` registered, routing `build_state_prep_circuit`'s real Hadamard-created superposition into the heralded-ancilla sub-circuit gives silently wrong probabilities via `PolarizationSimulator` (0.1646 measured vs 0.07407 expected in one case) -- traced to `PolarizationSimulator` defaulting unannotated ancilla photons to a specific polarization label, making them spuriously (in)distinguishable from qubit-carrying photons during multi-photon interference.

**Context:** First flagged in Plan 11-01 (attempting a single combined-simulator call for the full PBS round trip produced near-zero/wrong-magnitude probabilities for most computational-basis combos) and confirmed again in Plan 11-02 to also affect real Hadamard-created superpositions, not just directly-constructed dual-rail superposition states. This is a real simulation-fidelity gap in mixing polarization tracking with multi-photon Fock interference, not a flaw in the module's circuit design.
**Source:** .planning/phases/11-cz-insertion-unit-weight-2-circuit-composition/11-01-SUMMARY.md (Decisions Made, Issues Encountered), 11-02-SUMMARY.md (Deviations, Issues Encountered)

---

### A locked design decision (swap-fix placement) can be pinned down by research as MEDIUM confidence and still ship correctly
11-RESEARCH.md flagged Open Question 1 (internal-PERM vs. caller-side swap placement) as MEDIUM confidence -- only the dict-level swap was actually executed end-to-end during research; the internal-PERM version was algebraically argued but not separately run. The plan still locked the internal-PERM placement as the design decision, and Plan 11-01's execution confirmed it worked via the executable truth table.

**Context:** Shows that a locked decision doesn't require every implementation variant to have been separately executed during research, as long as the algebraic equivalence is sound and the plan's own verification step (truth table) will catch a wrong choice.
**Source:** .planning/phases/11-cz-insertion-unit-weight-2-circuit-composition/11-RESEARCH.md (Open Questions), 11-01-SUMMARY.md

---

## Patterns

### Testability seam: factor a PBS-free "core" out of a polarization-containing circuit
When a Perceval backend (Simulator+SLOSBackend) refuses circuits with `Circuit.requires_polarization`, factor the interesting non-polarized sub-wiring (here, the PERM-adapted `heralded_cz` block) into a private helper (`_build_cz_insertion_core()`) that both the production function and the tests call directly -- identical logic, zero behavior change, but now directly testable.

**When to use:** Any time a circuit mixes a Perceval-backend-incompatible component (PBS, polarization optics) with logic you need to unit-test via a backend that rejects that component category. Avoids writing a parallel/duplicated test circuit that risks silently diverging from the real implementation.
**Source:** .planning/phases/11-cz-insertion-unit-weight-2-circuit-composition/11-01-SUMMARY.md (Decisions Made, tech-stack patterns)

---

### Compositional (piecewise) proof instead of one combined simulator call, when the combined path is unreliable
Prove a round-trip claim in independently-verified pieces instead of one end-to-end simulator call: (1) a bare PBS is phase-neutral and amplitude-exactly-1 for pure computational-basis input, and (2) the dual-rail core reproduces the target truth table exactly. Together these establish the same claim the full round trip would, without relying on a Perceval code path (PolarizationSimulator + heralded ancilla) that doesn't correctly model the composition.

**When to use:** When a full end-to-end simulation call through a library combination is confirmed (via direct execution) to produce spurious/wrong results, but each half of the composition is independently verifiable through a reliable path.
**Source:** .planning/phases/11-cz-insertion-unit-weight-2-circuit-composition/11-01-SUMMARY.md (Decisions Made)

---

### Herald re-registration always explicit and immediate at the composition site, never inferred
Call `add_herald` on the outer Processor immediately after the `.add()` call that wires in a herald-owning sub-circuit, reading the herald spec from the sub-circuit builder's own return value (never hardcoded indices). Never rely on auto-shift/auto-propagation mechanisms when composing a bare `Circuit` (which carries no herald metadata at all, unlike composing an `Experiment`/`Processor`).

**When to use:** Any composition of a herald-carrying catalog gate (or any component with implicit ancilla/herald bookkeeping) into a larger `Processor`, especially when using non-contiguous mode-mapping dicts.
**Source:** .planning/phases/11-cz-insertion-unit-weight-2-circuit-composition/11-02-SUMMARY.md (patterns-established, key-decisions)

---

### Processor.add(mode_mapping_dict, sub_circuit) for non-contiguous mode wiring
`ModeConnector` auto-inserts a `PERM` before the sub-component and its exact algebraic inverse after, transparently restoring the outer processor's original mode numbering for every `.add()` call that follows -- confirmed by reading `Experiment._add_component` source directly, not assumed.

**When to use:** Wiring a sub-circuit into non-adjacent global mode indices (e.g. two qubits' ports plus newly-appended ancilla modes) without hand-rolling PERM/index bookkeeping.
**Source:** .planning/phases/11-cz-insertion-unit-weight-2-circuit-composition/11-RESEARCH.md (Don't Hand-Roll, Pitfall 5), 11-02-SUMMARY.md (tech-stack patterns)

---

### Route around a confirmed library limitation by staying inside the library's known-working envelope, while still proving the real claim
When `PolarizationSimulator`+heralds is unreliable/crashes, verify the invariant with heralds unregistered (bare Processor, manual post-selection on ancilla output modes matching the expected herald photon counts) and a definite computational-basis input (skip the Hadamard-superposition-inducing stage). This still validates strictly more than a smaller isolated test, since it proves the invariant survives the same mode-mapping-dict embedding the production code actually uses.

**When to use:** When a target library API is confirmed (by direct execution, not guesswork) to be broken/unreliable for a specific combination of features, and a narrower-but-still-representative test path exists that avoids the broken combination without weakening what's actually being proven.
**Source:** .planning/phases/11-cz-insertion-unit-weight-2-circuit-composition/11-02-SUMMARY.md (Deviations, key-decisions, patterns-established)

---

## Surprises

### A confirmed Perceval library limitation blocks the very approach the next phase (12) was expected to use
`Processor.add_herald()` + PBS-containing circuit + `Processor.probs()` crashes unconditionally with a matmul shape mismatch. This wasn't anticipated by 11-RESEARCH.md's Open Question 2 (which only asked "does herald-success probability change when composed with the rest of the pipeline," expecting a cheap `probs()` sanity check to answer it) -- the sanity check itself couldn't run as originally planned.

**Impact:** Directly changes Phase 12's design constraints: TVD validation cannot use `Processor.probs()` on the fully composed, herald-registered `build_weight2_processor` output at all. Phase 12 must pick an alternative measurement path (different API, workaround analogous to this phase's bare-processor+manual-post-selection, or file/investigate the issue upstream in Perceval) from the start rather than discovering it mid-execution. Flagged explicitly in both SUMMARY.md files and carried into STATE.md's Blockers/Concerns.
**Source:** .planning/phases/11-cz-insertion-unit-weight-2-circuit-composition/11-02-SUMMARY.md (Issues Encountered, Next Phase Readiness), 11-VERIFICATION.md (Gaps Summary)

---

### The verifier independently reproduced the exact same crash, not just trusted the SUMMARY's claim
11-VERIFICATION.md explicitly states the Perceval limitation (matmul shape mismatch, size 12 vs 16) was "independently reproduced by this verifier," not merely read from 11-02-SUMMARY.md -- and the verifier also independently re-ran the full 107-test suite and the `proc.heralds` check rather than trusting reported numbers.

**Impact:** Raises confidence that the library limitation is real and reproducible (not an environment fluke of the executing session), and that Phase 11's reported pass/fail status is grounded in independent re-execution rather than second-hand trust.
**Source:** .planning/phases/11-cz-insertion-unit-weight-2-circuit-composition/11-VERIFICATION.md (Gaps Summary, Observable Truths row 3-4)

---

### Two genuinely independent Perceval simulation gaps stack up around the same feature combination (polarization + heralds)
Not one bug but two distinct, separately-confirmed issues both centered on mixing polarization-tracking (PBS) with heralded multi-photon ancilla: (1) a hard crash when `add_herald` + PBS + `Processor.probs()` are combined, and (2) silently wrong (non-crashing) probabilities when `PolarizationSimulator` handles real Hadamard-created superposition feeding a heralded-ancilla sub-circuit, due to unannotated ancilla photons getting a default polarization label that spuriously affects distinguishability.

**Impact:** A single feature combination (polarization + heralded ancilla + Processor-level simulation) has more than one failure mode in this Perceval version, meaning future phases touching this combination should assume neither crash-avoidance nor absence-of-error is sufficient evidence of correctness -- both failure modes had to be separately identified and worked around.
**Source:** .planning/phases/11-cz-insertion-unit-weight-2-circuit-composition/11-01-SUMMARY.md (Issues Encountered), 11-02-SUMMARY.md (Deviations, Issues Encountered)
