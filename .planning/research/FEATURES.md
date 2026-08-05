# Feature Research

**Domain:** Photonic (Perceval/MerLin) implementation and validation of a weight-2 (two-qubit, entangling) IQP generator, built on an existing working weight-1 photonic IQP encoding
**Researched:** 2026-08-05
**Confidence:** HIGH (grounded in direct inspection of this repo's `iqp_photonic_encoding.py`/`tests/test_iqp_photonic_encoding.py`, `docs/iqp-photonic-encoding.md`'s Ingredient 2 derivation, and the installed `perceval-quandela` source for `core_catalog/heralded_cz.py` and `simulators/simulator.py`'s `logical_perf`/`physical_perf` machinery)

**Note on scope of this file:** an earlier FEATURES.md existed in this directory from the v2.0/Phase 8-9 literature-scoping research (IQP→photonic encoding feasibility). That content is now superseded by v2.0's shipped requirements/roadmap (archived under `.planning/milestones/v2.0-*`). This file is regenerated for the v2.1 milestone's specific question: weight-2 generator implementation and testing.

## Feature Landscape

### Table Stakes (Must Have to Call Weight-2 "Implemented and Validated")

Mirrors what v2.0 already established for weight-1 (build + exact reference + TVD check) — weight-2 isn't "done" until it clears the same bar, not a lower one.

| Feature | Why Expected | Complexity | Notes |
|---------|--------------|------------|-------|
| `build_weight2_generator_circuit` (or equivalent): PBS→dual-rail conversion, `heralded_cz`, PBS back, plus the two `WP(pi/4,0)` single-qubit corrections | This is the actual circuit `docs/iqp-photonic-encoding.md` Ingredient 2 derives on paper; without it there is no "implementation," only the existing derivation | MEDIUM-HIGH | `heralded_cz` is delivered via `CatalogItem.build_experiment()`, not a bare `Circuit` — it returns a `Circuit(6)` plus 2 dual-rail ports and 2 heralds (`add_herald(4,1)`, `add_herald(5,1)`), a different composition pattern than every existing weight-1 builder (`build_diagonal_layer_circuit` etc.), which are all bare `Circuit(2n)` objects with no herald/port state. Wiring this into the existing 2n-mode-per-register layout is the main new engineering surface. |
| Extend `exact_qubit_iqp_distribution` to accept a weight-2 (pairwise) term, not just per-qubit `thetas` | The validation pattern this project already committed to (ENC-04) is TVD against an exact qubit-side reference; that reference currently has no way to express `Z_iZ_j`, so it cannot validate weight-2 at all until extended | LOW | Same structure as the existing weight-1 phase loop (lines 254-261 of `iqp_photonic_encoding.py`): add a second phase contribution `phi_ij * (Z_i-eigenvalue * Z_j-eigenvalue)` = `phi_ij * (-1)^(bit_i XOR bit_j)`, using the same `(i >> (n-1-k)) & 1` bit-ordering convention already documented and tested. Recommended signature: accept an explicit list of pair terms, e.g. `pairs=[(i, j, phi)]`, rather than a fixed 2-qubit-only special case — keeps it usable at n=3 for the differentiator case below. |
| Herald-conditioned photonic distribution over qubit bitstrings, reported separately from herald-failure mass | `heralded_cz` is probabilistic — some outcomes fail the herald detector-click condition. The existing `photonic_iqp_distribution` residual concept (out-of-subspace Fock patterns) is a *different* failure mode (bunching/loss after the fact) and must not be conflated with herald failure (ancilla modes not clicking as required) | MEDIUM | Two independent "leakage" channels now exist: (1) herald failure — ancilla detector pattern wrong — and (2) post-readout out-of-subspace decode failure (ENC-03's existing 4 invalid patterns). Report both explicitly, never silently merged into one number or silently renormalized away. |
| TVD comparison between exact qubit-side weight-2 reference and photonic weight-2 output, **conditioned on herald success** | This is the direct weight-2 analogue of ENC-04, the validation pattern already locked in for weight-1; anything less is "built but not validated" | LOW (given the above two exist) | Must condition (i.e., renormalize the photonic distribution over the herald-successful branch) before computing TVD — comparing against the *unconditioned* joint distribution would make TVD dominated by herald-failure mass that has nothing to do with whether the gate's Z_iZ_j phase is correct. This mirrors real hardware use of a heralded gate: only herald-successful shots count as "the gate ran." |
| n=2 test case at the fixed angle θ=π/4 | n=2 is the minimum system size where a weight-2 generator applies at all (stated in milestone context) — without it, weight-2 is untested at any size | LOW | Directly reuses `exact_qubit_iqp_distribution`'s extension above with `pairs=[(0,1,pi/4)]`, `thetas=[0,0]` (or nonzero, see mixed case below), and the new photonic builder. |
| Exact (analytic) herald-success probability, computed from Perceval's own exact backend — not an empirical per-shot postselection frequency | Perceval's `Simulator`/`Analyzer` pipeline computes `logical_perf` (heralds) and `physical_perf` (detected-photon filter) as exact quantities derived from the state-vector simulation itself (`simulators/simulator.py`, `_logical_perf`/`physical_perf` fields; `Analyzer.compute()` already surfaces this as `self.performance`, confirmed at `analyzer.py:167` `self.performance = min(logical_perf)`) — no sampling noise is involved anywhere in this project's exact-validation path (SLOS backend, `Analyzer`), so treating this number as an empirically-sampled shot-based rate would be both wrong and unnecessary work | LOW | This directly answers the milestone's "empirically measure heralded_cz's actual herald-success probability" ask: "empirically measure" should mean *read the exact analytic value off the already-built circuit's `Analyzer`/`Processor` run* (e.g. `analyzer.performance` or the equivalent sum over herald-satisfying vs herald-failing branches of the raw output distribution), not run repeated finite-shot sampling. This is a **measurement of this specific implementation's number**, correctly distinguishing it from the unverified literature figures (1/9, ~2/27) `docs/iqp-photonic-encoding.md` already flags as belonging to a different, unconfirmed construction. |
| Test coverage in `tests/test_iqp_photonic_encoding.py` for all of the above, in the same style/tolerance conventions as the existing weight-1 tests | Existing test suite conventions (parametrized, `TOLERANCE = 1e-9` for exact algebra, explicit `< 1e-6` TVD threshold for the toy validation) are the project's own established bar; weight-2 tests that don't match it would be an inconsistent addition | LOW | Follows `test_enc04_toy_validation_runs_end_to_end`'s exact shape: build both distributions, assert both sum to 1 (each *within its own normalization* — see anti-features below on what NOT to force to sum to 1), assert TVD < chosen threshold. |

### Differentiators (Nice-to-Have — Strengthens the Validation Beyond the Minimum Bar)

| Feature | Value Proposition | Complexity | Notes |
|---------|-------------------|------------|-------|
| n=3 mixed generator set: 2 weight-1 terms + 1 weight-2 term (e.g. `thetas=[a,b,c]`, `pairs=[(0,1,pi/4)]`) | Tests that weight-1 and weight-2 layers compose correctly in the same circuit — the realistic case for an actual IQP circuit (mixed generator weights), not just an isolated 2-qubit toy | LOW-MEDIUM (mostly reuses table-stakes machinery once the pair-term extension to `exact_qubit_iqp_distribution` already supports arbitrary `pairs`) | Directly requested in the milestone context as an example differentiator; validates that `build_diagonal_layer_circuit`'s existing weight-1 gates and the new weight-2 builder can sit in the same 2n-mode register without interference (they act on disjoint/overlapping qubit polarization modes but different spatial submodes during the PBS→dual-rail excursion, so this is a genuine new integration check, not free). |
| Explicit two-number failure report per run: (herald-failure probability, out-of-subspace decode residual) shown side by side, rather than only a single combined TVD | Makes the honesty-ledger pattern this project already follows (see `docs/iqp-photonic-encoding.md`'s "Open questions and limitations" and "honesty ledger" sections) concrete for weight-2, instead of leaving readers to infer which failure channel dominates | LOW | Natural to log/print/assert both quantities separately in the test, e.g. `assert herald_success_prob > 0` and `assert residual == 0` (or whatever the true value turns out to be) as two independent assertions rather than one blended number. |
| Cross-check the analytic herald-success probability against a literature sanity bound (informational only, not a pass/fail gate) | `docs/iqp-photonic-encoding.md` already flags 1/9 and ~2/27 as unverified for this exact gate; reporting the actual computed number next to those figures (without asserting equality) closes that open question honestly | LOW | This is documentation/interpretation work (owner's job per this repo's CLAUDE.md), not new code — Claude should compute the number, the owner should interpret whether/how it relates to the cited figures. |
| Sanity-check the herald-conditioned distribution's normalization directly against `1 - herald_failure_probability` (i.e., confirm the two independently-computed quantities agree to floating-point precision) | A cheap internal-consistency check: the sum of the herald-conditioned photonic distribution's probabilities, times the herald success probability, should reconstruct the total non-out-of-subspace mass of the raw (unconditioned) run — catches bugs in the conditioning/renormalization logic itself | LOW | Pure arithmetic check on quantities already computed for the table-stakes items; no new circuit code needed. |

### Anti-Features (Explicitly Out of Scope This Milestone)

| Feature | Why It Seems Appealing | Why Problematic (This Milestone) | Alternative |
|---------|------------------------|-----------------------------------|-------------|
| Arbitrary-θ weight-2 generator (continuously tunable `exp(iθ·Z_iZ_j)` for θ ≠ π/4) | Would make the weight-2 generator as flexible as the weight-1 `WP(theta,0)` gates, and "feels" like the natural generalization of the existing API (`build_diagonal_layer_circuit(n, thetas)` takes arbitrary angles) | `docs/iqp-photonic-encoding.md` (Ingredient 2) already states plainly that Perceval's `core_catalog.heralded_cz` is a fixed, non-parameterized gate — there is no known decomposition from this catalog alone that realizes an arbitrary θ; attempting it this milestone would be solving an open research problem the project has explicitly deferred, not implementing what was derived on paper | Ship the fixed θ=π/4 case only, exactly as derived; if arbitrary-θ is ever wanted, that's a distinct, larger research question for a future milestone |
| Post-selected (non-heralded) CZ construction, e.g. for comparing success-probability figures against a different gate | `docs/iqp-photonic-encoding.md` cites the ~1/9 figure specifically for a *post-selected* construction, and it might be tempting to implement both to "verify" the literature numbers | Owner already explicitly chose the heralded construction over post-selected (stated design decision, `docs/iqp-photonic-encoding.md` line 52); building a second gate variant is new scope this milestone didn't ask for and doubles the surface needing validation | Stick to `heralded_cz` only; if the post-selected variant is ever wanted for comparison, treat it as its own milestone with its own validation pass |
| Weight-3+ (three- or more-qubit) generators | Natural-seeming next step once weight-2 works, and the qubit-side exact reference generalizes easily to arbitrary-weight Z-strings | Not derived on paper anywhere in this project yet (no operator identity for a 3-qubit catalog gate exists in `docs/iqp-photonic-encoding.md`), no existing catalog primitive was identified, and it's outside this milestone's stated scope (n=2 minimum, mixed n=3 weight-1+weight-2 only) | Defer; would need its own paper-derivation phase (like Ingredient 2 was) before any implementation attempt |
| Estimating herald-success probability via Monte Carlo / finite-shot sampling (e.g. `pcvl.algorithm.Sampler`) as the primary reported number | "Empirically measure" in the milestone context could be misread as "run simulated shots and count," which sounds more rigorous/realistic | Perceval's `Analyzer`/exact backend already computes this quantity exactly and noiselessly from the state-vector simulation (`logical_perf`/`performance`) — the same exact-computation philosophy this project already committed to for weight-1 TVD ("both sides are exact calculations, no sampling noise, near-exact agreement is the right bar" — `tests/test_iqp_photonic_encoding.py` docstring). Introducing sampling noise here would be a strictly worse, slower way to get a number Perceval already gives exactly, and would reintroduce exactly the ambiguity ("is TVD failing because of the mapping or because of shot noise?") the project deliberately avoided in v2.0 | Read the exact value off `Analyzer.performance` (or the equivalent manual sum over the raw distribution's herald-satisfying vs. herald-failing branches); reserve shot-based sampling for a future milestone explicitly about realistic/hardware-like behavior, if ever pursued |
| Forcing the herald-conditioned photonic distribution to be silently renormalized to sum to 1 without ever reporting the herald-failure mass it discarded | Simpler assertions (`sum(dist.values()) == 1`) mirror the existing weight-1 test pattern exactly | Silently discarding/renormalizing away the herald-failure probability without reporting it violates this project's own explicit ENC-03 policy ("explicit residual, never silently discarded/renormalized," `photonic_iqp_distribution`'s own docstring) — the same discipline must extend to the new herald-failure channel, or the resulting validation would overstate how "clean" the weight-2 gate is | Report herald success probability as its own explicit return value/assertion, exactly parallel to how `residual` already works for out-of-subspace decoding |
| Loss/noise modeling (photon loss, detector inefficiency, dark counts) layered on top of the ideal `heralded_cz` | Would make the weight-2 validation "more realistic" | Out of scope — the existing weight-1 validation is explicitly idealized/lossless (`docs/iqp-photonic-encoding.md`: "under an idealized, lossless SLOS simulation"), and this milestone's stated goal is parity with that same validation pattern for weight-2, not a new realism dimension | Defer to a future milestone explicitly about noise/hardware realism |

## Feature Dependencies

```
Extend exact_qubit_iqp_distribution to accept pairs=[(i,j,phi)]
    └──requires──> existing bit-ordering convention (already established, weight-1)

build_weight2_generator_circuit (PBS -> heralded_cz -> PBS + WP(pi/4,0) corrections)
    └──requires──> existing build_state_prep_circuit / build_conjugation_circuit / build_readout_circuit
                       (weight-2 sits in the *middle* diagonal layer only, same position as
                       build_diagonal_layer_circuit; state prep/conjugation/readout are unchanged)
    └──requires──> Perceval's core_catalog.heralded_cz (external, already installed/verified)

Herald-conditioned photonic distribution (table stakes)
    └──requires──> build_weight2_generator_circuit
    └──requires──> exact separation of herald-failure mass from out-of-subspace decode residual

TVD(exact weight-2 reference, herald-conditioned photonic distribution)  [the actual weight-2 ENC-04 analogue]
    └──requires──> Extend exact_qubit_iqp_distribution (above)
    └──requires──> Herald-conditioned photonic distribution (above)

n=3 mixed weight-1+weight-2 test (differentiator)
    └──requires──> everything above, at n>=2
    └──enhances──> confidence in weight-1/weight-2 composability, not required for weight-2 "done"

Exact analytic herald-success probability report (table stakes)
    └──requires──> build_weight2_generator_circuit
    └──conflicts with──> Monte Carlo/shot-based herald-probability estimation (anti-feature; redundant given exact backend)
```

### Dependency Notes

- **TVD comparison requires both the extended exact reference AND the herald-conditioned photonic distribution first:** neither half alone is sufficient — this project's own established pattern (ENC-04) is a two-sided comparison, and skipping either side would leave weight-2 exactly where it is today (paper-derived, unvalidated).
- **Herald-conditioning requires exact separation of the two failure channels:** conflating herald failure (ancilla side) with out-of-subspace decode residual (data-qubit side) would produce a TVD number that can't be interpreted — a regression could hide in either channel and get attributed to the wrong cause.
- **Exact herald-success probability conflicts with shot-based estimation:** these are alternative ways to get the same number; given Perceval computes it exactly for free as part of the same `Analyzer` run already needed for the TVD check, there is no reason to also implement sampling, and doing so would only introduce ambiguity about which of the two the reported figure is.

## MVP Definition

### Launch With (v2.1 Table Stakes)

Minimum to honestly claim "weight-2 IQP generator implemented and validated":

- [ ] Extended `exact_qubit_iqp_distribution` (or a new sibling function) accepting weight-2 pair terms
- [ ] `build_weight2_generator_circuit` (or equivalent name) implementing PBS→`heralded_cz`→PBS + the two `WP(pi/4,0)` single-qubit corrections, wired into the existing n-qubit register layout
- [ ] Herald-conditioned photonic distribution, with herald-failure probability and out-of-subspace residual reported as two separate, explicit numbers (never merged, never silently renormalized away)
- [ ] TVD test at n=2, θ=π/4, comparing the extended exact reference against the herald-conditioned photonic distribution, in the same style as the existing `test_enc04_toy_validation_runs_end_to_end`
- [ ] Exact (analytic, not sampled) herald-success probability computed and reported for this specific implementation
- [ ] Test coverage added to `tests/test_iqp_photonic_encoding.py` matching existing conventions

### Add After Validation (v2.1.x, if time allows this milestone)

- [ ] n=3 mixed weight-1 + weight-2 generator set test
- [ ] Internal-consistency check: herald-conditioned distribution sum × herald-success probability reconstructs raw non-out-of-subspace mass
- [ ] Side-by-side comparison note of the computed herald-success probability against the literature figures already flagged as unverified in `docs/iqp-photonic-encoding.md`

### Future Consideration (v3+, explicitly deferred)

- [ ] Arbitrary-θ weight-2 generator (needs new paper-derivation work first)
- [ ] Post-selected CZ variant for success-probability comparison
- [ ] Weight-3+ generators
- [ ] Loss/noise/hardware-realism modeling
- [ ] Shot-based (Monte Carlo) sampling of herald success, if ever needed for a realism-focused milestone

## Feature Prioritization Matrix

| Feature | User Value | Implementation Cost | Priority |
|---------|------------|---------------------|----------|
| Extend exact reference for `Z_iZ_j` | HIGH | LOW | P1 |
| `build_weight2_generator_circuit` | HIGH | MEDIUM-HIGH | P1 |
| Herald-conditioned distribution + explicit dual residual reporting | HIGH | MEDIUM | P1 |
| n=2 TVD validation | HIGH | LOW (given above) | P1 |
| Exact analytic herald-success probability | HIGH | LOW | P1 |
| n=3 mixed generator test | MEDIUM | LOW-MEDIUM | P2 |
| Herald-probability vs. literature figures note | LOW-MEDIUM | LOW | P2 |
| Internal consistency cross-check | LOW | LOW | P3 |
| Arbitrary-θ weight-2 | — | HIGH / open research question | Out of scope |
| Shot-based herald sampling | — | LOW but redundant | Out of scope |

**Priority key:**
- P1: Must have to call weight-2 implemented and validated this milestone
- P2: Should have if time allows, strengthens the result
- P3: Nice to have, cheap but low marginal value

## Sources

- `C:\Users\cuqui\merlin-quantum-case-study\iqp_photonic_encoding.py` — existing weight-1 implementation, `exact_qubit_iqp_distribution`, `photonic_iqp_distribution`, `total_variation_distance` (direct code read)
- `C:\Users\cuqui\merlin-quantum-case-study\tests\test_iqp_photonic_encoding.py` — existing test conventions and tolerance thresholds (direct code read)
- `C:\Users\cuqui\merlin-quantum-case-study\docs\iqp-photonic-encoding.md` — Ingredient 2 (weight-2 paper derivation), open-questions/honesty-ledger sections, owner's stated choice of heralded over post-selected CZ (direct doc read)
- `C:\Users\cuqui\merlin-quantum-case-study\venv\Lib\site-packages\perceval\components\core_catalog\heralded_cz.py` — confirms `heralded_cz` is delivered as a `CatalogItem` with `build_experiment()` returning a `Circuit(6)` + 2 dual-rail ports + 2 heralds (`add_herald(4,1)`, `add_herald(5,1)`), not a bare parameterized `Circuit` (direct source read, installed `perceval-quandela` package)
- `C:\Users\cuqui\merlin-quantum-case-study\venv\Lib\site-packages\perceval\simulators\simulator.py` — confirms `logical_perf`/`physical_perf` are computed exactly and analytically from the state-vector simulation, not sampled (direct source read, e.g. lines ~69, ~110-111, ~592-596)
- `C:\Users\cuqui\merlin-quantum-case-study\venv\Lib\site-packages\perceval\algorithm\analyzer.py` — confirms `Analyzer.compute()` surfaces this as `self.performance = min(logical_perf)` (line ~167), directly usable with the same `Analyzer` call pattern the existing codebase already uses for exact TVD validation (direct source read)

---
*Feature research for: photonic IQP weight-2 generator implementation and validation (Merlin/Perceval quantum case study, v2.1)*
*Researched: 2026-08-05*
