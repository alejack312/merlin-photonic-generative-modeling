# Phase 17: Trainability / Barren-Plateau Study - Context

**Gathered:** 2026-08-09
**Status:** Ready for planning

<domain>
## Phase Boundary

Measure whether the weight-1(+weight-2) IQP-photonic circuit shows barren-plateau behavior, via exact parameter-shift gradients (never MerLin `QuantumLayer` autograd — architecture research confirmed it rejects this circuit's polarization-annotated `BasicState`s). A specific measured claim, reported honestly either direction. Independent of ARB-01 (Phases 15-16), HARD (Phase 18), and VERIFY (Phase 19) — this phase does not wait on any of them.

</domain>

<decisions>
## Implementation Decisions

### Cost function / observable
- Gradient-variance is measured on **MMD² between the generated distribution and a target distribution** — not a generic Pauli-Z/literature-standard observable. This matches both this project's own actual generator training objective and the precedent behind the qubit-side empirical plateau rule TRAIN-07 requires comparing against (computed by the sibling project `iqp-mmd-barren-plateau` using its own MMD-based gradient estimator, confirmed live in `iqp_bp/mmd/gradients.py`).
- Target distribution: start with **v1.0's existing target** (K=462 natural-order grid, sigma=0.1) — direct continuity with this project's established training setup. May switch to the sibling project's own datasets later if that comparison turns out to matter more (owner's explicit hedge — not locked to v1.0's target permanently).
- MMD² is computed **exactly (full enumeration over the output distribution) while n stays small enough to enumerate, then falls back to Monte Carlo estimation once it doesn't** — directly mirrors the sibling project's confirmed pattern (`mmd2_exact_small_n`, used up to their n≤20 ceiling, with an estimator-based fallback for larger n). The actual crossover n for this project's photonic Fock-space output (likely different from the sibling's qubit n≤20, since Fock-space output grows differently than 2^n) is a research/planning determination, not locked here.
- Gradients computed via **parameter-shift directly on `photonic_iqp_distribution`/`photonic_weight2_iqp_distribution`** (per TRAIN-01) — the exact distribution functions already shipped in Phases 9/11-13, not MerLin `QuantumLayer` autograd.

### Code reuse
- `generator/neighbor_locality.py`'s gradient machinery (`jacrev` autodiff through MerLin's `QuantumLayer`) is **not reusable** — it's exactly the forbidden mechanism (QuantumLayer rejects this circuit's polarization-annotated states). Phase 17 needs a fresh implementation built directly on the exact-distribution + parameter-shift approach above. This is settled, not open for research to reconsider.

### System-size range & compute budget
- Push the sweep toward TRAIN-08's N≈20-24 target **until compute/memory genuinely can't go further — no time-box.** Owner's explicit call, made after being told this is the same "open-ended struggle with no early go/no-go signal" pattern that caused the prior PennyLane stall (documented in this repo's `CLAUDE.md`). The existing mid-milestone checkpoint (~2026-08-20, recorded in `ROADMAP.md`) is the accepted safety net for this risk — no additional time-box needed.
- Specific starting n values (beyond the ≥3-sizes/≥100-draws floor from TRAIN-01): **research/planning's call**, based on what's actually tractable once real per-n cost is measured.

### Generator scope split
- Weight-1-only sweep: pushed to the full compute-bound range above.
- Mixed weight-1+weight-2 sweep (TRAIN-04/06, reusing Phase 13's validated composability): **same n range as weight-1-only, best effort** — not deliberately capped smaller, even though weight-2's heralded_cz/CP(α) postselection overhead may make matching the full range harder in practice. If it turns out infeasible to match, that's an honest reporting outcome (per TRAIN-05's honesty requirement), not a reason to have scoped it smaller up front.
- Specific mix ratio (how many weight-2 gates vs. weight-1 in the mixed circuit): **open — research/planning picks a reasonable mix**, no locked ratio.

### Parameter init & normalization
- Test **both** initialization regimes the qubit-side empirical rule is split by: **small-angle (θ near 0) and uniform ([0, 2π))**. Testing only uniform would weaken TRAIN-07's cross-reference, since the qubit-side rule's most robust finding (`uniform and n≥6 and not complete_graph_like`) is only half the story without the small-angle regime alongside it.
- Per-circuit energy/photon-number normalization: **use whatever convention the existing weight-1/weight-2 circuit code already establishes** (per `docs/iqp-photonic-encoding.md` and prior phases) — state it explicitly in the write-up rather than introducing a new one.

### Claude's Discretion
- Exact crossover n where exact-MMD²-enumeration switches to Monte Carlo estimation.
- Specific starting/tested n values within the ≥3-sizes/≥100-draws floor.
- Specific weight-1:weight-2 mix ratio for the mixed-generator sweep.
- Implementation details of the fresh parameter-shift gradient code (batching, RNG seeding conventions, etc.) — following this repo's existing conventions (e.g. `tests/test_iqp_photonic_encoding.py` patterns).

</decisions>

<specifics>
## Specific Ideas

- The sibling project `iqp-mmd-barren-plateau` (`C:\Users\cuqui\iqp-mmd-barren-plateau\`) is treated as a live precedent to check against, not just background reading — its gradient estimator code (`src/iqp_bp/mmd/gradients.py`), exact/Monte-Carlo split (`src/iqp_bp/mmd/loss.py`'s `mmd2_exact_small_n`), and empirical plateau rule (`docs/iqp-baseline.md`) all directly informed decisions above. Research should treat this sibling repo as a first-class reference alongside the external literature already scoped for Phase 17.
- Owner may want to reuse the sibling project's actual training datasets (not just its methodology) instead of v1.0's target distribution — left open, not decided.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within phase scope.

</deferred>

---

*Phase: 17-trainability-barren-plateau-study*
*Context gathered: 2026-08-09*
