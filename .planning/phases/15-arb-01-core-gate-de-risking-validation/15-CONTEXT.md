# Phase 15: ARB-01 Core Gate De-Risking & Validation - Context

**Gathered:** 2026-08-07
**Status:** Ready for planning

<domain>
## Phase Boundary

Validate `PostProcessedControlledRotationsItem` (the continuously-tunable two-qubit diagonal phase gate) to the same rigor bar `heralded_cz` cleared in v2.1. This phase de-risks the gate standalone, derives the general-α operator identity, and confirms it via TVD against the extended exact qubit-side reference. Whether a tunable gate exists at all is already closed by research (confirmed) — this phase is validation, not open research. Extended composability testing, denser α sweeps, and Forge postselection verification are Phase 16, not this phase.

</domain>

<decisions>
## Implementation Decisions

### α value selection
- ≥3 non-trivial α values, chosen as round fractions of π spread across (0, π/2) with varied denominators (e.g., π/6, π/3, 2π/5 — not a fixed-denominator series like eighths).
- θ=π/4 (the Z_iZ_j generator angle, this codebase's existing convention — matching `pair_thetas={(0,1): np.pi/4}` in existing tests) is additionally included as an explicit boundary sanity-check, on top of (not counted among) the 3 non-trivial values — confirms the general identity correctly reduces to the already-validated fixed-π/4 `heralded_cz` case. **Correction (post-research, owner-confirmed 2026-08-07):** the literal value passed to `PostProcessedControlledRotationsItem`'s own `alpha` kwarg for this boundary check is `alpha=π` (=4θ), NOT `alpha=π/4` — CP's own dial and the Z_iZ_j generator angle θ are related by `α=4θ`, not equal. Research verified `CP(alpha=π)` reproduces `heralded_cz`'s `CZ=diag(1,1,1,-1)` exactly; `CP(alpha=π/4)` does not. Keep this α (CP dial) vs. θ (generator angle) distinction explicit in the plan and in the eventual `docs/iqp-photonic-encoding.md` writeup.
- Exactly 3 non-trivial values for the gate-structure confirmation (criterion 1) — the roadmap's stated minimum, no extra margin. Total test points for that criterion: 3 non-trivial + 1 boundary (π/4) = 4.

### Derivation ownership
- Attempt-first gating applies: Claude explains the approach/relevant math for the general-α operator identity (`CP(α)` ↔ `exp(iθZᵢZⱼ)`), the owner sketches/attempts the derivation first, Claude then writes up or checks it. Do not skip straight to writing the derivation.
- The general-α derivation is added **alongside** the existing fixed-π/4 derivation in `docs/iqp-photonic-encoding.md`, not replacing it — the π/4 section stays intact, the new section extends it and shows π/4 as the special case.
- Full step-by-step algebra required in the written derivation — matches this project's existing rigor bar (defensible unaided to Vincent), not a high-level sketch.
- The general success-probability-vs-α relationship must be derived analytically (closed form), then confirmed empirically against the measured sweep (criterion 4) — not left purely empirical.

### TVD validation scope
- System sizes: n=2, 3 — same as the existing weight-2 (v2.1) validation, for direct comparability.
- TVD checked at all 3 non-trivial α values (not just the roadmap's stated minimum of 1) — reuses the same α's from the gate-structure sweep.
- The extended exact qubit-side reference reuses Phase 12's exact-reference infrastructure as-is (parameterized by gate angle) — no new extension work assumed. If research finds Phase 12's reference was actually hardcoded to π/4 and doesn't generalize cleanly, flag it rather than silently building new infrastructure.
- Target tolerance: ≤1e-6, same bar weight-2 cleared — no relaxed target for this different gate mechanism.

### heralded_cz comparison depth
- Written comparison is a side-by-side table: success probability, ancilla/resource cost, circuit depth, post-selection (CP(α)) vs. ancilla-heralding (heralded_cz) mechanism — concrete dimensions, reusable directly in Phase 20's write-up.
- Lives in `docs/iqp-photonic-encoding.md`, alongside the new general-α derivation (not a separate standalone doc).
- Purely descriptive — states tradeoffs plainly, does not recommend when to use which gate family. That judgment call is left for later (write-up or actual usage decisions).
- New test coverage includes a direct boundary-agreement test: `CP(α=π/4)` output checked against the existing `heralded_cz` result at that same angle, in addition to standalone `CP(α)` tests — added to `tests/test_iqp_photonic_encoding.py` matching existing conventions.

### Claude's Discretion
- Exact test file structure/naming for the new CP(α) and boundary-agreement tests, as long as they match existing `tests/test_iqp_photonic_encoding.py` conventions.
- Presentation format of the success-probability-vs-α table/curve (criterion 4) beyond "not collapsed to a single number."

</decisions>

<specifics>
## Specific Ideas

No specific external references — decisions above are the concrete requirements for this phase.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope. (Denser α sweeps, mixed-generator composability testing, and Forge postselection verification are already scoped to Phase 16 per the roadmap, not new ideas raised here.)

</deferred>

---

*Phase: 15-arb-01-core-gate-de-risking-validation*
*Context gathered: 2026-08-07*
