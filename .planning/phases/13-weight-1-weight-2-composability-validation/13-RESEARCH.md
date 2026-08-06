# Phase 13: Weight-1 + Weight-2 Composability Validation - Research

**Researched:** 2026-08-06
**Domain:** This repo's own `iqp_photonic_encoding.py` module + pytest conventions (no external library research needed)
**Confidence:** HIGH — verified by direct source reading and direct execution against the installed venv, not by inspection alone

## Summary

This phase requires **no changes to `iqp_photonic_encoding.py`**. `photonic_weight2_iqp_distribution(n, i, j, thetas)` already accepts an arbitrary `thetas` array of length `n`, including nonzero values at indices `i` and `j` themselves (the pair members) — it additively folds `+pi/4` onto `thetas[i]`/`thetas[j]` internally (`thetas_folded[i] += np.pi/4`), it does not require or check that `thetas[i]`/`thetas[j]` start at 0. `exact_qubit_iqp_distribution(n, thetas, pair_thetas=None)` likewise already accepts both weight-1 `thetas` and a `pair_thetas` dict simultaneously, with independent, additive phase accumulation for each. Both functions already implement exactly the "2 weight-1 + 1 weight-2, with one weight-1 term stacked on a pair qubit" scenario CONTEXT.md locks in — this was implicitly exercised (though not literally as this phase's required n=3-mixed-with-stacking config) by Phase 12's own `test_wt2_tvd_gate_n3_bystander_qubit`, which already puts a nonzero weight-1 theta on a bystander qubit alongside a weight-2 pair, just not stacked on a pair member.

I verified this directly by running the exact target scenario (n=3, pair (0,1) at the mandatory folded pi/4, weight-1 thetas `[0.5, 0.0, 1.3]` — nonzero and stacked on qubit 0, one of the pair members, plus qubit 2 outside the pair) against the installed venv. Result: **TVD = 1.8e-15** (against extended exact reference with `pair_thetas` set), and **TVD = 0.4999...** against the weight-1-only exact reference (`pair_thetas=None`) — confirming the ZZ term is doing real, non-vacuous work. I also ran two more configurations varying the pair choice and stacking on the other pair member (`j` instead of `i`); all three configs pass the TVD < 1e-6 gate with TVD in the 1e-16 to 1e-15 range, and all three show sanity-check TVD in the 0.46-0.50 range (clearly non-negligible).

**Primary recommendation:** This is purely a test-writing phase. Add one new `@pytest.mark.parametrize`-driven test function to `tests/test_iqp_photonic_encoding.py`, following the exact pattern of `test_wt2_tvd_gate_n3_bystander_qubit` (Phase 12's closest existing analogue) but parametrized over 2-3 configs that vary the pair choice and which pair member gets the stacked weight-1 theta, per CONTEXT.md's locked requirements. No source-module changes, no new helper functions needed — everything the test needs already exists in `iqp_photonic_encoding.py`.

## Standard Stack

N/A — this is an internal, self-contained numerics module with no external library gap. Only dependency is the existing `pytest`, `numpy`, `perceval` (already imported at the top of the test file). No new imports are needed beyond what's already imported (`exact_qubit_iqp_distribution`, `photonic_weight2_iqp_distribution`, `total_variation_distance`, `np`, `pytest` — all already present in the test file's import block).

## Architecture Patterns

### Pattern: TVD-gate test matching Phase 12's convention
**What:** A parametrized pytest test that (1) builds an extended exact reference via `exact_qubit_iqp_distribution(n, thetas, pair_thetas={(i,j): pi/4})`, (2) builds the photonic distribution via `photonic_weight2_iqp_distribution(n, i, j, thetas)`, (3) asserts `residual ≈ 0`, `herald_failure_prob ≈ EXPECTED_HERALD_FAILURE_PROB`, both distributions sum to 1, then (4) asserts `total_variation_distance(...) < 1e-6`.

**When to use:** This is the exact test being added in Phase 13.

**Example (verified against this repo's existing test, `tests/test_iqp_photonic_encoding.py:551-570`):**
```python
def test_wt2_tvd_gate_n3_bystander_qubit():
    n, i, j = 3, 1, 2
    thetas = [0.6, 0.0, 0.0]

    qubit_dist = exact_qubit_iqp_distribution(n, thetas, pair_thetas={(1, 2): np.pi / 4})
    photonic_dist, residual, herald_failure_prob = photonic_weight2_iqp_distribution(n, i, j, thetas)

    assert np.isclose(residual, 0.0, atol=1e-9)
    assert np.isclose(herald_failure_prob, EXPECTED_HERALD_FAILURE_PROB, atol=1e-6)
    assert np.isclose(sum(qubit_dist.values()), 1.0, atol=1e-9)
    assert np.isclose(sum(photonic_dist.values()) + residual, 1.0, atol=1e-9)

    tvd = total_variation_distance(qubit_dist, photonic_dist)
    assert 0.0 <= tvd <= 1.0
    assert tvd < 1e-6, f"n={n} i={i} j={j} thetas={thetas}: TVD={tvd} exceeds the 1e-6 threshold"
```
Phase 13's version differs only in: `thetas` must have a nonzero value at one of `{i, j}` (the "stacked" requirement) in addition to the bystander qubit's nonzero theta, and it should be parametrized across 2-3 configs per CONTEXT.md rather than a single fixed case. `EXPECTED_HERALD_FAILURE_PROB` (`= 1 - 2/27`, defined once at module level, line 504) is reused unchanged — the CZ/heralded_cz success probability is architecture-fixed and does not depend on the weight-1 thetas at all, confirmed by all three of my verification runs (all showed `herald_fail=0.925926` regardless of theta values or pair choice).

### Pattern: companion "sanity check" (non-vacuity) assertion
**What:** A second TVD computed between the same `photonic_dist` and the **weight-1-only** exact reference (`exact_qubit_iqp_distribution(n, thetas, pair_thetas=None)` — omit the pair term entirely, same thetas). CONTEXT.md requires this be "clearly non-negligible" to prove the ZZ term is doing something.
**When to use:** Companion assertion within the same test function (or a second parametrized test), immediately after the primary TVD-gate assertion.
**Verified magnitude:** In my 3 verification runs this sanity TVD ranged 0.46-0.50 — i.e., roughly half the total probability mass moves when the ZZ term is included versus excluded. A threshold like `assert tvd_sanity > 0.1` (or even `> 0.2`) would be a safe, non-flaky bound; no existing test in this file has needed a "non-negligible" lower-bound assertion before, so there's no established constant to reuse — CONTEXT.md leaves the exact threshold to your discretion, use a round number well below the observed 0.46-0.50 range for headroom.

### Recommended test placement
Directly after `test_wt2_tvd_gate_n3_bystander_qubit` (line 570, end of file) and its preceding "Phase 12 Plan 01: TVD gate + herald-accounting tests (WT2-05, WT2-06)" comment block — add a new comment header (e.g. `# Phase 13: weight-1 + weight-2 composability (WT2-07).`) followed by the new parametrized test function(s), matching the file's existing pattern of one comment banner per phase/plan segment (see lines 231, 268, 382, 502 for precedent).

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Extended exact reference with both weight-1 and weight-2 terms | A new reference-distribution function | `exact_qubit_iqp_distribution(n, thetas, pair_thetas={...})` | Already supports both simultaneously (Phase 12); verified numerically to ~1e-15 agreement |
| Photonic distribution for a circuit with weight-1 thetas overlapping the pair | A new processor-builder variant | `photonic_weight2_iqp_distribution(n, i, j, thetas)` | Already folds `+pi/4` additively onto `thetas[i]`/`thetas[j]`, so a nonzero `thetas[i]` and the pair term coexist correctly by construction — no special-casing needed for the "stacked" scenario |
| Herald-failure-probability expected value | A new constant | Reuse module-level `EXPECTED_HERALD_FAILURE_PROB = 1 - 2/27` (line 504 of the test file) | Confirmed architecture-invariant across all tested theta/pair configs — heralded_cz's success rate doesn't depend on the weight-1 phases at all |

**Key insight:** Every piece this phase needs was already built and tested (at simpler configs) in Phases 10-12. This phase is exclusively about composing existing, already-verified building blocks into one new test with the specific "2 weight-1 (one stacked) + 1 weight-2" shape CONTEXT.md specifies — there is no new numerics to write.

## Common Pitfalls

### Pitfall 1: Forgetting the pair theta is not independently settable
**What goes wrong:** Someone might try to pass a `pair_thetas` value other than `pi/4` to `exact_qubit_iqp_distribution`, expecting `photonic_weight2_iqp_distribution` to match at that angle.
**Why it happens:** `exact_qubit_iqp_distribution`'s `pair_thetas` parameter is fully general (any angle), but `photonic_weight2_iqp_distribution` always internally folds exactly `+pi/4` — this asymmetry is easy to miss.
**How to avoid:** Always use `pair_thetas={(i, j): np.pi / 4}` in the exact reference when comparing against `photonic_weight2_iqp_distribution`'s output for that same `(i, j)` pair — this matches CONTEXT.md's explicit lock ("Pair theta stays locked at pi/4 internally").
**Warning signs:** A TVD around 0.3-0.5 instead of ~1e-15 is the signature of a pair-theta mismatch (same magnitude as the sanity-check TVD) — if the primary TVD assertion unexpectedly lands near the sanity-check's expected range, check the pair-theta value first.

### Pitfall 2: Choosing thetas that are degenerate or synchronize with pi/4
**What goes wrong:** CONTEXT.md explicitly locks weight-1 thetas to be "arbitrary, distinct, non-degenerate nonzero values (not all equal, not multiples of pi/4, not zero)" — picking round numbers like `pi/4`, `pi/2`, or `0.0` for the weight-1 thetas would weaken the test (degenerate cases can accidentally hide composition bugs via symmetry).
**How to avoid:** Use non-round decimal values (e.g. `0.5`, `1.3`, `0.9`, `0.4`, `0.2`, `1.7`, `0.65` — all confirmed to work in my verification runs) rather than fractions of pi.
**Warning signs:** N/A — this is a design-quality pitfall, not something that would cause a test failure; it just weakens the test's statistical power to catch bugs.

### Pitfall 3: Mixing up "stacked on i/j" with "outside the pair"
**What goes wrong:** CONTEXT.md requires the mixed-generator shape to include a weight-1 term genuinely stacked on a pair-member qubit (index `i` or `j`), not just two weight-1 terms both outside the pair (which would only be testing weight-1 composability, already covered by Phase 9-10's original 26 tests, not the new composability claim WT2-07 makes).
**How to avoid:** For each parametrize config, explicitly set a nonzero `thetas[k]` for `k` equal to `i` or `j` (the pair), plus a nonzero `thetas[m]` for the one remaining qubit `m` outside `{i, j}` at n=3.
**Warning signs:** If all three of a config's thetas happen to be at indices outside `{i, j}`, re-check — at n=3 with one weight-2 pair, there are only 3 qubits total, so exactly one is "outside" and two are "inside" the pair; correctly hitting CONTEXT.md's "2 weight-1 + 1 weight-2" shape means putting weight-1 thetas at the outside qubit AND at least one pair qubit (not both pair qubits necessarily — CONTEXT.md's example uses one pair qubit + the outside qubit, i.e. 2 nonzero weight-1 thetas total, not 3).

## Code Examples

### Verified target scenario (ran directly against this repo's venv, not just read from source)
```python
# Source: direct execution against C:\Users\cuqui\merlin-quantum-case-study\venv
import numpy as np
from iqp_photonic_encoding import (
    exact_qubit_iqp_distribution,
    photonic_weight2_iqp_distribution,
    total_variation_distance,
)

n, i, j = 3, 0, 1
thetas = [0.5, 0.0, 1.3]  # nonzero at qubit 0 (stacked, pair member i) and qubit 2 (outside)
pair_thetas = {(i, j): np.pi / 4}

qubit_dist = exact_qubit_iqp_distribution(n, thetas, pair_thetas=pair_thetas)
photonic_dist, residual, herald_failure_prob = photonic_weight2_iqp_distribution(n, i, j, thetas)

tvd = total_variation_distance(qubit_dist, photonic_dist)
# Result observed: tvd = 1.811e-15  (well under 1e-6 gate)
# residual = 0.0, herald_failure_prob = 0.9259259259259262

qubit_dist_w1only = exact_qubit_iqp_distribution(n, thetas, pair_thetas=None)
tvd_sanity = total_variation_distance(qubit_dist_w1only, photonic_dist)
# Result observed: tvd_sanity = 0.4999999999999995  (clearly non-negligible)
```

Two additional configs verified, both passing with the same magnitudes (TVD ~1e-15 to 1e-16 primary, ~0.46-0.50 sanity):
```python
# Stacked on j instead of i, different pair
n, i, j = 3, 1, 2
thetas = [0.9, 0.4, 0.0]   # -> TVD=2.555e-15, sanity_TVD=0.5000

# Different pair again, stacked on j
n, i, j = 3, 0, 2
thetas = [0.2, 1.7, 0.65]  # -> TVD=6.609e-16, sanity_TVD=0.4605
```
These three configs are ready to drop directly into a `@pytest.mark.parametrize` list, satisfying CONTEXT.md's "2-3 configurations, varying the qubit-pair choice and/or theta sets" requirement.

## State of the Art

N/A — this is a closed, internal validation module; there is no "current best practice" drift to track. The relevant prior state is fully captured in Phases 9-12's STATE.md/RESEARCH.md history, which the CONTEXT.md for this phase already summarizes accurately (I independently confirmed every claim it made against actual source and execution).

## Open Questions

None. The one open question posed in this phase's brief ("does `photonic_weight2_iqp_distribution` already fully support this test with no code changes") is definitively answered: **yes**, confirmed both by source inspection (no restriction anywhere on `thetas[i]`/`thetas[j]` being zero — the fold is unconditional and additive) and by direct execution of the exact target scenario plus two variants, all passing the TVD < 1e-6 gate with large margin (~1e-15 vs 1e-6, six orders of magnitude of headroom).

## Sources

### Primary (HIGH confidence)
- `C:\Users\cuqui\merlin-quantum-case-study\iqp_photonic_encoding.py` — full source read, specifically `exact_qubit_iqp_distribution` (lines 544-599), `photonic_weight2_iqp_distribution` (lines 359-417), `_build_weight2_processor_no_herald` (lines 296-335), `_weight2_input_state` (lines 338-356), and `build_weight2_processor`'s theta-folding docstring (lines 228-236, explicitly states the folding rule is "load-bearing for Phase 13's later weight-1+weight-2 mixed-circuit test").
- `C:\Users\cuqui\merlin-quantum-case-study\tests\test_iqp_photonic_encoding.py` — full source read for existing conventions, specifically `test_wt2_tvd_gate_n3_bystander_qubit` (lines 551-570, closest existing analogue), `test_wt2_tvd_gate_n2_theta_pi_4` (lines 507-527), `EXPECTED_HERALD_FAILURE_PROB` constant (line 504), import block (lines 14-35).
- Direct execution against the repo's own venv (`C:\Users\cuqui\merlin-quantum-case-study\venv\Scripts\python.exe`) of the exact target scenario plus 2 variants — not simulated or assumed, actually run, output captured above.

### Secondary (MEDIUM confidence)
None used — no external research was needed for this phase.

### Tertiary (LOW confidence)
None.

## Metadata

**Confidence breakdown:**
- Standard stack: N/A — no external stack decisions in this phase
- Architecture: HIGH — verified against actual source and by direct execution, not inference
- Pitfalls: HIGH — Pitfall 1 and 2 are directly derivable from source/CONTEXT.md; Pitfall 3 is a design-intent clarification confirmed against CONTEXT.md's literal wording

**Research date:** 2026-08-06
**Valid until:** N/A (internal, static module — not subject to external ecosystem drift; re-verify only if `iqp_photonic_encoding.py` itself changes)
