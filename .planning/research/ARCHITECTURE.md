# Architecture Research: Weight-2 IQP Generator Integration

**Domain:** Photonic QML (Perceval), extending an existing tested weight-1 module with a `heralded_cz`-based weight-2 generator
**Researched:** 2026-08-05
**Confidence:** HIGH — all claims below verified by direct inspection of the installed `perceval-quandela` source and by running the actual catalog primitive (`perceval.components.catalog['heralded cz']`) in this repo's `venv`, not assumed from docs or training data.

**Note on this file:** supersedes the previous (2026-07-30) version of this file, which was written before v2.0's implementation existed and proposed a `iqp_photonic/` package structure that was never adopted — the actual v2.0 deliverable is a single flat module, `iqp_photonic_encoding.py`, plus `tests/test_iqp_photonic_encoding.py` and `docs/iqp-photonic-encoding.md`. This file is scoped narrowly to the v2.1 weight-2 question and is grounded in that actual codebase, read directly.

## Summary Answer

`heralded_cz` needs 2 extra internal modes beyond the 4 dual-rail modes it acts on, but Perceval's `Processor` abstraction manages those extra modes automatically — they never enter the module's existing 2n-mode logical port numbering. The existing 2n-mode-per-qubit layout is already dual-rail-shaped (`build_readout_circuit`'s `PBS()` on ports `(2k, 2k+1)` is exactly a polarization→dual-rail conversion), so no renumbering of qubit ports is needed. The real architectural fork is different: **weight-1's pipeline is `Circuit`-only (a single unitary matrix), but any circuit containing a heralded gate cannot be represented as a plain `pcvl.Circuit` — it must be composed as a `pcvl.Processor`.** That forces a second, parallel top-level pipeline function (`Processor`-composed) for weight-2, while every existing weight-1 *builder* function (`build_state_prep_circuit`, `build_diagonal_layer_circuit`, `build_conjugation_circuit`, `build_readout_circuit`) is reused unmodified — they're all valid inputs to `Processor.add()`.

## Verified Facts About `heralded_cz`

Confirmed by running `perceval.components.catalog['heralded cz']` directly in this repo's venv:

| Fact | Value | How verified |
|---|---|---|
| Logical (data) modes | 4 — two dual-rail qubits | `catalog['heralded cz'].build_experiment().m == 4` |
| Internal circuit width | 6 | `catalog['heralded cz'].build_circuit().m == 6` |
| Herald modes | 2, at internal circuit indices 4,5 | `Processor(...).heralds == {4: 1, 5: 1}` — success requires exactly 1 photon in each herald mode |
| Gate realized | Knill CZ (arXiv:quant-ph/0110144) | `catalog['heralded cz'].article_ref` |
| Success probability | ≈0.07407 = **2/27** exactly | measured directly via `Processor.probs()['global_perf']` on a `\|1,0,1,0>` dual-rail input — independently confirms the literature figure `docs/iqp-photonic-encoding.md` had flagged as unverified (lines 184, 216, 381) |
| Success-probability retrieval | `Processor.probs()` returns `{'results': {...conditional dist...}, 'global_perf': <success prob>}` | run directly, output captured |
| Herald-mode bookkeeping when composed into a larger `Processor` | Automatic — parent `Processor.m` (logical port count) is unchanged after `p.add(mode_mapping, heralded_cz_experiment)`; `p.circuit_size` grows by 2, `p.heralds` gains the new pair | verified: built a 4-mode weight-1-shaped `Processor`, added the heralded_cz experiment at modes `[0,1,2,3]`, confirmed `p.m` stayed 4 while `circuit_size` went from 4 to 6 |

**Practical consequence:** you never manually allocate ancilla/herald modes in the module's public API — `Processor.add()` does it. This directly answers "does heralded_cz require additional modes beyond the 2n-mode layout": yes, internally (2 per CZ application), but they're invisible to and don't renumber the existing per-qubit port convention, provided composition happens at the `Processor` level rather than by hand-concatenating a 6-mode unitary into a flat `Circuit`.

## Why the Existing 2n-Mode Layout Already Fits

`heralded_cz` acts on 4 dual-rail modes — 2 per qubit. The module's existing layout already reserves exactly 2 modes per qubit: port `2k` (polarization-carrying) and port `2k+1` (vacuum partner, currently unused until `build_readout_circuit`'s final `PBS()`). `PBS()` converts a polarization superposition on mode `2k` into a spread across the pair `(2k, 2k+1)` — that pair **is** the qubit's dual-rail representation. So converting qubit `i` and qubit `j` to dual rail for a CZ application uses their existing mode pairs `(2i, 2i+1)` and `(2j, 2j+1)` — no new modes needed for the conversion itself, only for the herald ancillas inside `heralded_cz`, which `Processor.add()` handles as shown above.

This means weight-2 does not require a layout change (e.g., 3n modes, or moving vacuum-partner modes) — it requires an *early* `PBS` conversion on the qubit pair (mid-circuit, not just at final readout), the `heralded_cz` insertion, then a `PBS` conversion back to polarization so the rest of the pipeline (conjugation, readout) is unaffected.

## Why Weight-2 Cannot Reuse `build_full_circuit`'s Circuit-Concatenation Pattern

`build_full_circuit` (`iqp_photonic_encoding.py:111-124`) builds one `pcvl.Circuit(2n)` by calling `circuit.add(port, component)` repeatedly, and `run_full_circuit` wraps that single `Circuit` in a `Processor` only at the very end, purely to run it. This works because every weight-1 component (`HWP`, `WP`, `PBS`) is a plain unitary — a `Circuit` is just a unitary matrix, with no concept of post-selection or heralding.

`heralded_cz`'s catalog item is not exposed as a plain unitary in the way the module needs it: `build_circuit()` gives the raw 6-mode unitary but leaves herald-mode bookkeeping (which modes are heralds, what pattern counts as success, how to compute `global_perf`) entirely on the caller. `build_experiment()`/`build_processor()` give that bookkeeping for free, but return `Experiment`/`Processor` objects, not `Circuit`. `Processor.add()`'s own docstring confirms it accepts "a unitary circuit... a non-unitary component... a processor" — i.e. it is the composition primitive spanning both worlds. A flat `Circuit` cannot hold a non-unitary/heralded component at all.

**Conclusion:** weight-2's top-level pipeline builder must construct a `pcvl.Processor` from the start (composed via `Processor.add()` calls), not a `pcvl.Circuit`. This is a second, parallel pipeline function alongside `build_full_circuit`/`run_full_circuit` — not a modification of them.

## Integration Points With Existing Code (Verified Against Actual `iqp_photonic_encoding.py`)

| Existing function | Reused as-is for weight-2? | How |
|---|---|---|
| `build_state_prep_circuit(n)` | Yes, unmodified | Returns `Circuit(2n)`; add via `processor.add(0, build_state_prep_circuit(n))` — `Processor.add` explicitly accepts a unitary `Circuit` |
| `build_diagonal_layer_circuit(n, thetas)` | Yes, unmodified — and it's also where the CZ single-qubit corrections live | Ingredient 2's operator identity (`exp(iπ/4·Z_iZ_j) = CZ · exp(iπ/4·Z_i) · exp(iπ/4·Z_j)` up to global phase, `docs/iqp-photonic-encoding.md` lines 117-121) needs `WP(π/4, 0)` on each qubit in a CZ pair. Since `WP(θ,0)` gates are diagonal and additive (`exp(iaZ)·exp(ibZ) = exp(i(a+b)Z)`), the correction is just `thetas[i] += π/4`, `thetas[j] += π/4` *before* calling the existing function — no new phase-gate code needed |
| `build_conjugation_circuit(n)` | Yes, unmodified | Same composition pattern as state prep |
| `build_readout_circuit(n)` | Yes, unmodified | Final `PBS` per qubit — unaffected because weight-2's own PBS conversions happen mid-circuit and convert back to polarization before this stage runs |
| `all_h_input(n)` | Yes, unmodified | Input-state convention doesn't change |
| `basic_state_to_bitstring` / `fock_to_bitstring` | Yes, unmodified, conditional on correctness of the mid-circuit PBS round-trip | Decode logic never needs to know a CZ happened, provided weight-2's own PBS-back-conversion restores the same per-qubit `(2k,2k+1)` polarization convention before the final readout stage — worth its own explicit round-trip check (see Build Order step 2), not assumed |
| `exact_qubit_iqp_distribution(n, thetas)` | No — needs a new sibling function for weight-2 validation | Current implementation only sums weight-1 `Z_k` phase terms (lines 235-273); a weight-2 reference needs to also add `Z_i*Z_j` eigenvalue terms for CZ pairs before the Hadamard/probability step |
| `build_full_circuit` / `run_full_circuit` | No — parallel functions, not modifications | Weight-1's `Circuit`-only representation structurally cannot carry a heralded component (see above) |

## New Components Needed

1. **`build_cz_insertion(n, i, j)`** (naming illustrative) — a `Processor`-composable unit implementing Ingredient 2's mechanism: `PBS` on qubit `i`'s pair, `PBS` on qubit `j`'s pair (convert both to dual rail), the catalog's `heralded_cz` experiment across those 4 modes, then `PBS` back on both pairs (return to polarization). Likely itself assembled as a small `Processor`/`Experiment`, since it mixes plain `PBS` circuits with the non-unitary `heralded_cz` catalog item.

2. **`build_full_circuit_weight2(n, thetas, cz_pairs)`** — the new top-level `Processor`-composed pipeline: state prep → adjusted diagonal layer (weight-1 `thetas` plus `π/4` corrections folded in per CZ pair) → for each pair in `cz_pairs`, insert `build_cz_insertion` at that pair's ports → conjugation → readout. Returns a `Processor`, not a `Circuit`.

3. **`run_full_circuit_weight2(n, thetas, cz_pairs)`** — runs the above via `Processor.probs()` (not `Analyzer`, which was built around the module's existing single-`Circuit`+`Processor`-wrap pattern; `Processor.probs()` already returns both the herald-conditional distribution and `global_perf` directly, as verified above). Should return three things, not two: the conditional distribution (analogous to `run_full_circuit`'s `dist`), the herald `global_perf` (success probability — new, no weight-1 analogue), and the module's existing out-of-subspace `residual` concept (still worth checking empirically for weight-2 rather than assuming zero, since weight-2 mixes photons across qubit pairs in a way weight-1 never does).

4. **`exact_qubit_iqp_distribution_weight2(n, thetas, cz_pairs)`** (or an additive optional parameter on the existing function) — qubit-side reference distribution including `Z_i*Z_j` phase terms, needed as the ENC-04-style ground truth for weight-2 validation. Decide up front: model only CZ (θ fixed at π/4, matching what `heralded_cz` actually realizes) rather than an arbitrary-angle two-qubit term — per `docs/iqp-photonic-encoding.md` line 121, the catalog gate is fixed, so the reference should match exactly, or the validation comparison is apples-to-oranges.

## Data Flow Changes

- **Mode count:** the logical port count stays `2n` for the pipeline's public interface (matches weight-1) — heralds are internal-only, hidden by `Processor`. No change to any function's `n`-based mode arithmetic.
- **Readout/decode logic:** unchanged in principle, but the weight-2 pipeline's PBS-back-conversion after each CZ pair must be verified (not assumed) to restore the exact same 2-mode-per-qubit polarization convention weight-1 relies on — analogous to ENC-03's existing round-trip test.
- **New data surfaced:** `global_perf` (herald success probability) is genuinely new, with no weight-1 equivalent. It is not the same thing as the existing out-of-subspace `residual` (a post-hoc property of decoded Fock outcomes) — per the module's established convention (explicit residual reporting, never silently renormalized — `docs/iqp-photonic-encoding.md` lines 254, 299), `global_perf` must be surfaced explicitly alongside the conditional distribution, not folded into or confused with `residual`. Keep them as two clearly separate return fields.
- **Validation metric implication:** TVD between the weight-2 photonic distribution and the qubit-side reference should be computed on the herald-conditional distribution (`Processor.probs()['results']`, already renormalized by Perceval) against the exact-CZ qubit-side reference, with `global_perf` reported alongside as a separate honest datum — not folded into the TVD comparison itself. Mirrors the existing pattern of reporting `residual` alongside, not folded into, TVD in `photonic_iqp_distribution`/ENC-04.

## Suggested Build Order

1. **De-risk the primitive standalone, no integration.** Reproduce this research's own verification (n=2 bare dual-rail `Processor` around `catalog['heralded cz']`, confirm `global_perf ≈ 2/27`, confirm the CZ truth table on `|1,0,1,0>`-style dual-rail inputs) as an actual test, independent of the rest of the module. Cheap, isolates the highest-uncertainty piece (does the catalog gate really behave as ENC-01 assumed) before touching any existing code, and directly resolves the "success-probability unverified" flag currently open in `docs/iqp-photonic-encoding.md`.
2. **Build `build_cz_insertion`** (PBS-wrap + `heralded_cz` + PBS-unwrap) as an isolated `Processor`-composable unit at the module's existing `(2i,2i+1)`/`(2j,2j+1)` port convention. Test its polarization-basis truth table directly (not yet embedded in a full IQP pipeline) — confirms the mid-circuit PBS round-trip claim above.
3. **Compose `build_full_circuit_weight2`/`run_full_circuit_weight2`** from existing weight-1 builders + step 2's insertion, via `Processor.add()`. No changes to any existing weight-1 function.
4. **Extend the qubit-side reference** (`exact_qubit_iqp_distribution_weight2` or an additive parameter) to include CZ terms, matching the fixed-π/4 realization only.
5. **Weight-2 TVD validation**, ENC-04-style, at small `n` (2-3 qubits, one CZ pair) — report TVD on the conditional distribution plus `global_perf` and `residual` as separate honest fields, following the existing module's reporting convention exactly.
6. **Full regression run** of the existing 26-test suite (`pytest tests/test_iqp_photonic_encoding.py -v`) after each of steps 2-4, to catch any accidental signature change to a reused weight-1 function early. Since every new function is additive, this should stay green throughout — if it doesn't, that's a signal a "reuse" step accidentally mutated a shared function instead of composing around it.

## Anti-Patterns to Avoid

### Anti-Pattern: Manually managing herald ancilla modes by hand-extending a flat `Circuit`
**What people might do:** keep `build_full_circuit`'s single-`Circuit`-concatenation style by manually widening the circuit to `2n+2` modes per CZ pair and adding `catalog['heralded cz'].build_circuit()`'s raw 6-mode unitary directly.
**Why it's wrong:** `build_circuit()` gives the *unconditional* unitary including the herald modes as ordinary output modes — heralding (post-select on the herald outcome, compute success probability, renormalize) would have to be reimplemented entirely by hand, duplicating what `Processor`/`Experiment` already do correctly, and entangling herald-mode indices into the module's clean `2n`-port qubit convention.
**Do this instead:** compose at the `Processor` level using `build_experiment()`/`build_processor()` and `Processor.add()`, exactly as verified above — let Perceval track heralds and `global_perf`.

### Anti-Pattern: Silently renormalizing away herald failure
**What people might do:** report only the herald-conditional distribution (`Processor.probs()['results']`) and drop `global_perf`, since it's "just" a success probability.
**Why it's wrong:** contradicts this module's own established, explicitly-stated policy (`docs/iqp-photonic-encoding.md` line 254) of never silently discarding/renormalizing probability mass without reporting it — `global_perf` is exactly the kind of number that policy exists to surface, and is also the number needed to finally resolve the "success probability unverified for this exact gate" flag currently open in that document.

### Anti-Pattern: Extrapolating weight-1's exactness threshold blindly, in either direction
**What people might do:** either assume weight-2 can't be validated to the same `TVD < 1e-6` bar as weight-1 (since it's "probabilistic"), or ignore `global_perf`'s own precision when claiming validation success.
**Why it's wrong:** `docs/iqp-photonic-encoding.md`'s own ENC-04 self-explanation checkpoint (lines 341-343) already flags the naive "weight-1 matched exactly, so weight-2 will too" extrapolation as unsupported reasoning, precisely because it treats a deterministic and a probabilistic mechanism as interchangeable. But conditioning on herald success is just Bayes' rule over Perceval's exact `SLOS` simulation — so the *conditional* distribution should still match the exact-CZ qubit-side reference to floating-point precision, and `TVD < 1e-6` remains the right bar for that comparison. What must not be silently assumed is that `global_perf` itself reproduces 2/27 to the same precision once composed inside the full n-qubit pipeline (as opposed to the standalone-primitive check in Build Order step 1) — that should be asserted explicitly in the weight-2 validation, not taken on faith from the isolated test.

## Sources

- `perceval-quandela` installed package (version pinned in `requirements.txt`), inspected directly via this repo's `venv` — `Processor`, `Circuit`, `catalog['heralded cz']` behavior all confirmed by running code, not read from docs.
- `C:\Users\cuqui\merlin-quantum-case-study\iqp_photonic_encoding.py` — full existing module, read directly.
- `C:\Users\cuqui\merlin-quantum-case-study\docs\iqp-photonic-encoding.md` — design document, Ingredient 2 (weight-2 derivation) and its ENC-02/Conclusion open-questions sections.
- `C:\Users\cuqui\merlin-quantum-case-study\tests\test_iqp_photonic_encoding.py` — existing 26-test suite structure (test names enumerated directly, not re-derived).
- Catalog gate provenance: arXiv:quant-ph/0110144 (Knill, 2002), per `catalog['heralded cz'].article_ref`.

---
*Architecture research for: weight-2 IQP generator implementation (v2.1 milestone)*
*Researched: 2026-08-05*
