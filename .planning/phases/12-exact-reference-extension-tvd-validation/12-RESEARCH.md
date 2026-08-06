# Phase 12: Exact Reference Extension & TVD Validation - Research

**Researched:** 2026-08-06
**Domain:** Perceval `PolarizationSimulator` internals (photon annotation semantics), classical exact-statevector extension
**Confidence:** HIGH (both major questions resolved by direct execution against this repo's own venv/code, cross-checked against a second, independent trusted simulation path)

## Summary

Both of Phase 12's open questions were resolved by direct execution, not by reading docs or guessing:

1. **The "silent wrong numbers" distinguishability bug (Plan 11-02's carried-forward blocker) has a working fix, verified at the exact locked validation point (n=2, i=0, j=1, θ=π/4).** Annotating the two herald-ancilla input photons as `{P:V}` (instead of leaving them unannotated, which Perceval defaults to `{P:H}`) in the manually-constructed input `BasicState`, combined with the already-locked post-selection strategy (never call `add_herald`, run the bare `Processor.probs()`, filter on ancilla output modes by hand), reproduces the trusted, `PolarizationSimulator`-free ground truth to **TVD ≈ 2.2e-16** against the newly-derived extended exact reference (Success Criterion 3's `<1e-6` bar cleared by ten orders of magnitude), with herald-success probability matching Phase 10's established `2/27` to machine precision and **zero** out-of-subspace residual. This was re-confirmed at n=3 with a bystander qubit, at a second `(i,j)` pair, and with nonzero weight-1 thetas mixed in on top of the weight-2 pair term — the fix is not a coincidence specific to one configuration.
2. **The crash (`add_herald` + `PBS` → `Processor.probs()` matmul mismatch) is unaffected by annotation and is a genuinely separate bug** — confirmed still reproducing verbatim (`size 8 is different from 12` variant of the same shape-mismatch family) even with the `{P:V}` fix applied and heralds registered. This confirms the locked strategy is still required: never call `add_herald` on the measurement processor; the `{P:V}` annotation is an *additional*, independent fix layered on top of post-selection, not a replacement for it.
3. **Extending `exact_qubit_iqp_distribution` to `Z_i·Z_j` pair terms is a two-line, low-risk addition** to the existing phase-accumulation loop — confirmed by direct implementation and cross-checked against the trusted photonic ground truth above (both agree to 1e-16).

**Primary recommendation:** Phase 12 does **not** need to invoke its fallback chain (shot-based sampling / computational-basis-only / blocked). A clean fix exists inside the time-box, verified working. Plan around: extend `exact_qubit_iqp_distribution` with an optional `pair_thetas` argument; build a new `_build_weight2_processor_no_herald`-style helper (mirrors `build_weight2_processor` exactly, minus the two `add_herald` calls) for measurement; construct the herald-ancilla input photons with explicit `{P:V}` annotation; report `(dist, residual, herald_failure_prob)` as an explicit 3-tuple.

## What Was Investigated and How

All findings below come from running actual Python against this repo's `venv` (`perceval-quandela==1.2.4`), reusing this module's real functions (`build_state_prep_circuit`, `build_diagonal_layer_circuit`, `build_cz_insertion`, `build_conjugation_circuit`, `build_readout_circuit`, `_build_cz_insertion_core`) — not synthetic circuits. No file in the repo was modified; all reproduction happened in throwaway scratch scripts.

### Step 1 — Reproduced the confirmed bug exactly

Rebuilt Plan 11-02's own scenario (n=3, i=0, j=1, `thetas_folded=[π/4, π/4, 0]`, full `build_state_prep_circuit` Hadamard included, bare processor + manual post-selection on ancilla modes, no `add_herald`) and got **0.16460905349794233** for the herald-matched total — an exact match to Plan 11-02's SUMMARY.md-documented `0.1646` discrepancy. This confirms the bug is reproducible on demand, not environment- or timing-dependent.

### Step 2 — Established ground truth independently, via a completely different simulation path

Before trying any fix, verified what the *correct* answer should be, using a path that never touches `PolarizationSimulator`, `PBS`, or annotations at all: manually constructed the dual-rail superposition `StateVector` that `HWP(π/8) → WP(θ_folded,0)` produces before `build_cz_insertion`'s internal `PBS`-wrap (amplitude `e^{iθ_folded}/√2` on the `'0'` dual-rail branch, `e^{-iθ_folded}/√2` on `'1'`), and ran it through `_build_cz_insertion_core()` (no PBS, no polarization anywhere) via the ordinary `Simulator`+`SLOSBackend` this module's own truth-table tests already trust (`test_cz_insertion_returns_circuit_and_herald_spec` and friends).

Result: herald-success probability = **0.07407407407407401 = 2/27 exactly**, independent of θ (checked at θ ∈ {0, 0.3, π/6, π/4, π/2, 1.9}) — confirming the theoretically-expected KLM-style property that a heralded gate's success probability is state-independent across the logical (single-photon-per-rail) subspace, including genuine superpositions. This also independently confirms `0.1646` (Step 1) is *wrong*, not a surprising-but-correct number.

Pitfall re-hit during this step, already flagged in STATE.md but worth restating since it silently produces a wrong shape error, not a wrong number: `amp * pcvl.StateVector(state)` fails with `numpy.complex128` amplitudes (`ValueError: setting an array element with a sequence...`) — must `complex(amp) * pcvl.StateVector(state)` first.

### Step 3 — Tried the photon-annotation candidate fix

Built the full `build_weight2_processor`-equivalent pipeline (state prep with real Hadamard → diagonal layer → CZ insertion via mode-mapping dict → conjugation → readout, bare processor, no `add_herald`) and varied only how the two herald-ancilla input photons are annotated in the input `BasicState` string:

| Ancilla annotation | herald-success prob | Matches 2/27? |
|---|---|---|
| none (bare integer count, Perceval default) | 0.16460905... | No |
| explicit `{P:H}` | 0.16460905... (identical to no annotation — confirms H is really the silent default) | No |
| explicit `{P:V}` | 0.07407407407407403 | **Yes**, to 1e-9 |

### Step 4 — Verified the fix against the actual TVD acceptance criterion, at the actual locked validation point

Extended `exact_qubit_iqp_distribution` (see below) and ran the exact WT2-05 comparison: n=2, i=0, j=1, θ=π/4, pure weight-2 term (no weight-1 thetas), `{P:V}`-annotated ancilla, post-selection (no `add_herald`).

```
Exact (extended) qubit distribution: {'00': 0.5, '01': ~0, '10': ~0, '11': 0.5}
herald_prob = 0.07407407407407403   (2/27, matches Phase 10 exactly)
residual    = 0.0                    (zero out-of-subspace leakage)
TVD         = 2.220446049250313e-16  (vs Success Criterion 3's <1e-6 bar)
```

`{P:H}` and no-annotation both give `TVD ≈ 0.4639` at this same point — the bug is not a rounding issue, it is a qualitatively wrong distribution.

### Step 5 — Robustness checks (not just one lucky configuration)

- **n=3, pair (1,2), bystander qubit 0 at θ=0.6, weight-1 thetas mixed onto qubits i,j on top of the θ=π/4 pair term:** herald_prob = 0.074074074074074**04**, TVD = 6.4e-16, residual = 0.0.
- **n=3, pair (0,1), same mixed-theta setup:** herald_prob = 0.07407407407407407 (exact), TVD = 5.4e-16, residual = 0.0.
- **Total-probability accounting** (herald_success + herald_failure over the *entire* unconditioned output, no post-selection filter applied) sums to 0.9999999999999992 ≈ 1, with herald_failure ≈ 0.9259 = 1 − 2/27 — matches Phase 10's known heralded_cz success rate exactly, confirming no probability mass is silently lost anywhere in this measurement path.
- **Crash check:** confirmed `add_herald` + `PBS` → `Processor.probs()` still crashes with `{P:V}` annotation applied and heralds registered (`ValueError: matmul: ... size 8 is different from 12`, same shape-mismatch family, different concrete size than Plan 11-02's `12 vs 16` — consistent with "any circuit combining registered herald + PBS" as the trigger, not one specific mode count). This is a distinct bug from the distinguishability issue; the annotation fix does not and should not be expected to touch it.

### What was *not* fully derived: the mechanistic "why"

`PolarizationSimulator._prepare_input` (via `convert_polarized_state`) doubles **every** mode of the circuit into an (H-submode, V-submode) pair, including modes that were never meant to carry polarization at all (the ancilla and post-PBS dual-rail modes internal to `heralded_cz`'s core) — confirmed by reading `venv/Lib/site-packages/perceval/utils/polarization.py`'s `convert_polarized_state` (loops over *every* `state.m`, not just annotated ones) and `polarization_simulator.py`'s `_postprocess_sv_impl` (unconditionally splits/relabels every mode pair as H/V on the way out). A plausible mechanism: components that don't touch polarization (BS, PERM inside `heralded_cz`) act block-diagonally on the H-submode and V-submode copies of the doubled network, so which copy the ancilla photon's default annotation places it in determines whether it can genuinely bosonically interfere (Hong-Ou-Mandel-style) with the data photon's copy — and empirically the data photon's post-PBS branch ends up needing the ancilla in the *V*-copy, not the naively-expected H-copy, to get correct interference. This explanation is a plausible sketch, not a verified mechanism (would require reading the compiled Rust/C++ `exqalibur` `compute_unitary(use_polarization=True)` internals, which are not available as readable Python). **The planner does not need the mechanism to proceed — the fix is empirically verified robustly across 5+ independent configurations — but should not present the "why" as settled fact**, only the "what" and "that it works."

## Recommended Function/Test Signatures

### 1. Extend `exact_qubit_iqp_distribution` in place (not a sibling)

Add an optional third parameter, defaulting to preserve every existing call site and test unchanged:

```python
def exact_qubit_iqp_distribution(n, thetas, pair_thetas=None):
    """... existing weight-1 docstring, plus:
    pair_thetas: optional dict {(i, j): theta_ij} for Z_i*Z_j pair-generator
    terms (i < j), added on top of the existing weight-1 diagonal phase using
    the SAME bit-ordering convention (qubit 0 = MSB) and the SAME Z-eigenvalue
    sign convention ((-1)^bit_k) already established for weight-1. Z_i*Z_j's
    eigenvalue is the product of each qubit's own Z eigenvalue. pair_thetas=None
    behaves identically to the pre-Phase-12 function (backward compatible)."""
    pair_thetas = pair_thetas or {}
    ...
    for i in range(dim):
        ...
        for (a, b), th in pair_thetas.items():
            za = 1 if bit(a) == 0 else -1
            zb = 1 if bit(b) == 0 else -1
            total_phase += th * za * zb
```

Verified correct (Step 2-5 above): this two-line addition to the existing phase-accumulation loop, cross-checked against the independent photonic ground truth, agrees to 1e-16. No change to bit-ordering, no change to the weight-1 path, no new dependency.

### 2. New helper mirroring `build_weight2_processor` minus the crash-triggering calls

```python
def _build_weight2_processor_no_herald(n, i, j, thetas):
    """Identical wiring to build_weight2_processor (state prep -> theta-folded
    diagonal layer -> CZ insertion via the same mode-mapping dict -> conjugation
    -> readout) but WITHOUT calling add_herald (confirmed crash: add_herald +
    PBS -> Processor.probs() raises ValueError: matmul shape mismatch,
    unconditionally, independent of annotation -- see 12-RESEARCH.md).
    Returns (proc, herald_spec); caller must post-select on herald_spec by hand."""
```

This should literally reuse `build_weight2_processor`'s own body (copy-paste minus the two `add_herald` lines, or factor the shared wiring into a private helper both call) — do not re-derive the mode-mapping dict independently; that would risk it silently drifting from the production function it's supposed to validate.

### 3. Input construction: `{P:V}`-annotated ancilla, not `all_h_input`'s bare-integer pattern

```python
def _weight2_input_state(n, herald_spec):
    """all_h_input(n)'s pattern for the n qubit ports, PLUS the two herald
    ancilla ports explicitly annotated {P:V} (NOT bare integers -- Perceval's
    default is {P:H}, confirmed to give a silently wrong herald-conditioned
    distribution; {P:V} confirmed correct, matching a trusted PBS-free
    ground truth to TVD~1e-16 -- see 12-RESEARCH.md Step 3-4). herald_spec's
    values are always 1 in this project (heralded_cz's own in_heralds)."""
    parts = ["{P:H},0"] * n
    parts.append("{P:V}" * herald_spec[4] if herald_spec[4] else "0")
    parts.append("{P:V}" * herald_spec[5] if herald_spec[5] else "0")
    return pcvl.BasicState("|" + ",".join(parts) + ">")
```

### 4. Top-level distribution function — 3-tuple return, per CONTEXT.md's locked reporting rule

```python
def photonic_weight2_iqp_distribution(n, i, j, thetas, pair_theta=np.pi/4):
    """Weight-2 analogue of photonic_iqp_distribution. Returns (dist, residual,
    herald_failure_prob):
      dist: {bitstring: probability} over valid outcomes, HERALD-CONDITIONED
            (renormalized by herald success probability) -- matches
            photonic_iqp_distribution's existing convention of reporting only
            valid, in-subspace outcomes.
      residual: total probability on out-of-subspace outcomes WITHIN the
            herald-success branch (photon bunching/loss on qubit ports) --
            same meaning as photonic_iqp_distribution's existing residual.
      herald_failure_prob: total probability where the ancilla output pattern
            did NOT match herald_spec -- a NEW, separate number (CONTEXT.md-
            locked: never merged into residual, never silently renormalized
            away). Confirmed ~1-2/27 ~ 0.9259 at pair_theta=pi/4 (Phase 10's
            established heralded_cz success rate)."""
```

Note the folding convention: `build_weight2_processor` always folds `+π/4` regardless of the caller's `pair_theta` (the CZ identity is only exact at that fixed angle — this is why CONTEXT.md locks validation to θ=π/4 with no theta sweep). If the new function's signature takes a separate `pair_theta` parameter for clarity/documentation purposes, it should assert `pair_theta == np.pi/4` (or simply not expose it as a variable at all and hardcode the `π/4` fold inline) rather than silently accepting other values that would produce numerically-valid-but-physically-meaningless output. Recommend: don't parameterize it — hardcode the `π/4` fold, matching `build_weight2_processor`'s own hardcoded fold, and let `thetas[i]`/`thetas[j]` carry any additional weight-1 correction the caller wants (exactly as `build_weight2_processor` already does).

### 5. Test coverage (WT2-06)

New tests in `tests/test_iqp_photonic_encoding.py`, matching `test_enc04_toy_validation_runs_end_to_end`'s style:

- `test_exact_qubit_distribution_weight2_extension_sums_to_one` — sanity check on the new `pair_thetas` parameter alone (no photonics), several `(n, thetas, pair_thetas)` combos.
- `test_exact_qubit_distribution_weight2_backward_compatible` — `pair_thetas=None` (or omitted) reproduces the existing weight-1-only function exactly, for a few existing test cases already in the suite — guards against silently breaking WT1 tests.
- `test_wt2_herald_failure_and_residual_are_separate_numbers` — the CONTEXT.md-locked accounting check: `dist` sums to 1 minus nothing extra, `herald_failure_prob ≈ 1 - 2/27`, `residual == 0.0` for this lossless circuit, and none of the three numbers are silently folded into another.
- `test_enc04_toy_validation_weight2_n2_theta_pi_4` (the actual WT2-05 gate) — n=2, i=0, j=1, θ=π/4, TVD < 1e-6 against the extended exact reference. This is the locked pass/fail gate; verified achievable in research (TVD~2e-16).
- Optional/opportunistic (CONTEXT.md: "not a hard requirement"): n=3 variant with a bystander qubit — verified cheap and correct in research (Step 5), so likely worth including if it doesn't blow the plan's time budget.
- Consider one test that explicitly asserts the `{P:H}`/no-annotation path is *wrong* (documents the bug, not just the fix) — optional, but valuable given how easy it would be for a future edit to silently drop the `{P:V}` annotation and regress back into the bug with no test catching it otherwise.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Herald-conditioned distribution accounting | A custom renormalization scheme | The existing `photonic_iqp_distribution`'s `(dist, residual)` pattern, extended | Consistency with the rest of the module; CONTEXT.md explicitly locks this convention |
| Weight-2 exact reference | A wholly new module/function structure | `exact_qubit_iqp_distribution` extended with `pair_thetas` | Reuses the trusted, already-tested bit-ordering/Z-eigenvalue machinery; smaller diff, smaller risk |
| Ancilla input construction | Re-deriving `build_weight2_processor`'s mode-mapping dict independently for the no-herald measurement path | Copy/reuse the exact same mapping dict `build_weight2_processor` uses | Any drift between the measurement helper's wiring and production's wiring would invalidate the whole validation — the point is to test what's actually shipped |

## Common Pitfalls

### Pitfall 1: numpy complex128 breaks StateVector arithmetic (already known, re-confirmed)
**What goes wrong:** `amp * pcvl.StateVector(state)` raises `ValueError: setting an array element with a sequence...` when `amp` is `numpy.complex128`.
**How to avoid:** `complex(amp) * pcvl.StateVector(state)`. Already documented in STATE.md; re-hit during this research, still applies to any new code constructing StateVectors by hand.

### Pitfall 2: Perceval defaults unannotated photons to `{P:H}`, silently
**What goes wrong:** Omitting a `{P:...}` annotation on an input photon does not mean "no polarization" — `convert_polarized_state`'s `annot.get("P", complex(Polarization(0)))` defaults to exactly `H`. For plain (non-polarization-intended) ancilla photons, this silent default is what causes the wrong-numbers bug.
**How to avoid:** For any photon fed into a circuit `PolarizationSimulator` will process, be explicit about its `P` annotation — don't rely on the bare-integer/no-annotation shorthand once polarization-mixing components (PBS) are anywhere in the same circuit, even if the photon in question is logically "just a plain Fock ancilla."
**Warning signs:** Herald-success probability or full distribution numerically close to but visibly different from a trusted independent computation (as opposed to a clean crash) — the "silent wrong numbers" failure mode is specifically dangerous because nothing errors.

### Pitfall 3: `add_herald` + any `PBS`-containing circuit always crashes `Processor.probs()`
**What goes wrong:** `ValueError: matmul: Input operand 1 has a mismatch in its core dimension 0 ...` inside `PolarizationSimulator._prepare_input`, unconditionally, regardless of thetas, state_prep, or (now confirmed) annotation.
**How to avoid:** Never call `add_herald` on the processor instance used for `.probs()` when the circuit contains `PBS`. Build heralds in production code (`build_weight2_processor` itself, correctly, per Success Criterion 3) but measure via a *separate*, herald-unregistered processor instance with manual post-selection.
**Status:** Confirmed still present after the annotation fix — genuinely orthogonal bug, worth filing upstream as CONTEXT.md already directs.

## Sources

### Primary (HIGH confidence — direct execution against this repo's own code/venv)
- `iqp_photonic_encoding.py` (this repo) — `exact_qubit_iqp_distribution`, `photonic_iqp_distribution`, `build_weight2_processor`, `build_cz_insertion`, `_build_cz_insertion_core` read directly, reused unmodified in all reproduction scripts.
- `venv/Lib/site-packages/perceval/simulators/polarization_simulator.py` (perceval-quandela 1.2.4, installed in this repo's venv) — read directly (`_prepare_input`, `_postprocess_sv_impl`, `_postprocess_bsd_impl`).
- `venv/Lib/site-packages/perceval/utils/polarization.py` (perceval-quandela 1.2.4) — read directly (`convert_polarized_state`, `Polarization`, `POLARIZATION_MAPPING`).
- Direct execution: 8 scratch Python scripts run against `venv/Scripts/python.exe`, reproducing the confirmed bug, an independent trusted ground truth, the annotation fix, and robustness checks across n=2/n=3, multiple `(i,j)` pairs, mixed weight-1+weight-2 thetas, and the crash-still-present check. All results quoted above are copy-pasted actual output, not inferred.
- `.planning/phases/11-cz-insertion-unit-weight-2-circuit-composition/11-02-SUMMARY.md` — source of the `0.1646` vs `0.07407` discrepancy this research reproduces and then resolves.

### Secondary/Tertiary
None used — this research question was answerable entirely by direct execution against the installed library and this repo's own code; no WebSearch or external docs were needed or consulted.

## Open Questions

1. **Exact mechanism of why `{P:V}` (not `{P:H}`) is the correct ancilla annotation**
   - What we know: empirically robust across 5+ configurations; `{P:H}`/no-annotation is provably wrong (large TVD), `{P:V}` is provably right (TVD~1e-16) at every configuration tested.
   - What's unclear: the exact internal reason within `PolarizationSimulator`'s doubled-mode representation (would require reading compiled `exqalibur` internals, not available as readable Python).
   - Recommendation: the planner/executor should treat this as an empirically-verified, well-tested fact (cite this research doc + the new tests as evidence) rather than block on deriving the mechanism. Worth one sentence in the upstream Perceval bug report as an observed workaround, clearly labeled as "observed to fix it, mechanism not fully understood."

2. **Whether n=3 is "cheap enough" to include per CONTEXT.md's opportunistic clause**
   - What we know: research's n=3 checks (Step 5) ran with no perceptible slowdown vs n=2, and pass cleanly.
   - What's unclear: whether the *test suite's* n=3 addition (as an actual `@pytest.mark.parametrize` case, inside pytest's overhead, not a one-off script) stays within whatever time budget the plan sets.
   - Recommendation: include it; if it turns out to meaningfully slow the suite, drop it — it's explicitly optional per CONTEXT.md either way.

## Metadata

**Confidence breakdown:**
- Distinguishability-bug fix (annotation): HIGH — verified via direct execution across 5+ independent configurations, cross-checked against 2 independent ground-truth computation methods (a PBS-free trusted simulator path, and the newly-derived extended exact reference), all agreeing to ~1e-15/1e-16.
- Crash (add_herald + PBS) still present: HIGH — directly re-executed with the fix applied; identical failure mode.
- `exact_qubit_iqp_distribution` extension formula/bit-ordering: HIGH — implemented, executed, and independently cross-checked against the photonic ground truth (not just internally self-consistent).
- Mechanistic "why" the annotation fix works: LOW — plausible sketch only, not verified against compiled internals; explicitly flagged as unresolved above.

**Research date:** 2026-08-06
**Valid until:** Tied to `perceval-quandela==1.2.4` (pinned in this repo's venv) — re-verify if the Perceval version changes; the underlying `PolarizationSimulator` bug and its annotation workaround are library-version-specific implementation behavior, not a stable public API contract.
