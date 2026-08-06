# Phase 11: CZ Insertion Unit & Weight-2 Circuit Composition - Context

**Gathered:** 2026-08-06
**Status:** Ready for planning

<domain>
## Phase Boundary

Implement the full weight-2 generator circuit: `PBS`→`heralded_cz`→`PBS` (the CZ insertion unit) plus the two `WP(π/4,0)` single-qubit corrections, composed at `Processor` level, reusing every existing weight-1 builder (`build_state_prep_circuit`, `build_conjugation_circuit`, `build_readout_circuit`) unmodified. Requirement: WT2-01. Exact-reference extension and TVD validation are out of scope — that's Phase 12.

</domain>

<decisions>
## Implementation Decisions

### Herald wiring / build_cz_insertion return shape
- `build_cz_insertion(n, i, j)` returns a **bare `Circuit`**, matching every other weight-1 builder's convention (`build_state_prep_circuit`, `build_diagonal_layer_circuit`, etc.) — not an `Experiment`/`Processor` fragment.
- Herald bookkeeping is explicit and separate: the function also surfaces the herald mode offsets/spec (e.g. as a second return value or a documented attribute) so the caller can re-add `heralds` to the outer `Processor` at the correctly shifted mode indices after composition via `Processor.add()`.
- Rationale (owner-selected): preserves the "everything is a plain `Circuit`" pattern the rest of the module already relies on, at the cost of pushing herald index math to the composition step — explicit over implicit, so a bug in herald-index shifting is visible in one place rather than hidden inside a return type nobody else in the module uses.
- Success criterion 3 (assembled processor's `heralds` property confirmed non-empty right after assembly) is the concrete check this decision must satisfy.

### PBS-wrap round-trip verification scope
- The truth-table check (success criterion 1) covers **all 4 computational-basis inputs AND superposition spot-checks** (e.g. `|+>` on one or both qubits), not just computational basis.
- Rationale: Phase 9's H/V port-labeling bug was self-consistent and passed every computational-basis test while being wrong — it only would have been caught by a coherent-superposition check. Phase 10 already established the superposition-spot-check pattern (`build_plus_plus_terms`, `build_plus_zero_terms` in `heralded_cz_derisking.py`); Phase 11 reuses that pattern for the wrap/unwrap round trip specifically.

### Theta folding (π/4 correction composition)
- Additive: `thetas[k]` for a qubit participating in a weight-2 CZ term = **(any existing weight-1 generator angle already active on qubit k) + π/4**, not a replacement.
- Rationale: this is what makes Phase 13 (weight-1 + weight-2 composability) well-defined later — deciding the folding rule now (additive, not exclusive) avoids retrofitting the composition logic in Phase 13. In Phase 11 itself, the tests may still exercise the isolated case (weight-2 term only, other thetas = 0) since Phase 13 owns the actual mixed-circuit test.

### Regression rigor beyond the existing suite
- Beyond re-running the existing 32-test weight-1 suite unmodified (success criterion 4 as stated), Phase 11 adds a **lightweight non-regression assertion**: confirm weight-1 builder outputs (e.g. `build_state_prep_circuit(n)`'s unitary, or equivalent) are bit-identical before/after this phase's changes.
- Rationale: cheap insurance against an accidental shared-helper edit — Phase 9 already had one silent labeling bug (H/V ports) that no test caught until a direct calibration check was added. This is the same category of risk (unmodified module edited by a phase whose real focus is elsewhere) recurring for Phase 11.

### Claude's Discretion
- Exact function/variable names for the herald-spec return value from `build_cz_insertion` (e.g. tuple vs named attribute), as long as it's documented in the same docstring style as the rest of `iqp_photonic_encoding.py`.
- Which specific weight-1 unitary/output to snapshot for the non-regression assertion, and how (inline pytest fixture vs standalone check).
- Internal test organization/file placement, following existing `tests/test_iqp_photonic_encoding.py` conventions.

</decisions>

<specifics>
## Specific Ideas

No specific product/behavior references beyond what's captured in Implementation Decisions — this is a technical/library phase, not a user-facing one. The owner's CLAUDE.md requires this circuit-composition logic be explainable unaided at the next self-explanation checkpoint, so plans should keep the herald-wiring and theta-folding rationale visible in code comments/docstrings, matching the existing module's documentation density (see `iqp_photonic_encoding.py`'s and `heralded_cz_derisking.py`'s inline API-fact comments).

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope. (Exact-reference extension/TVD validation explicitly belongs to Phase 12; mixed weight-1+weight-2 circuit test explicitly belongs to Phase 13 — both already scoped in ROADMAP.md, not new ideas surfaced here.)

</deferred>

---

*Phase: 11-cz-insertion-unit-weight-2-circuit-composition*
*Context gathered: 2026-08-06*
