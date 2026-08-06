# Phase 10: Heralded-CZ Primitive De-Risking - Research

**Researched:** 2026-08-06
**Domain:** Perceval (`perceval-quandela==1.2.4`) heralded-gate API — `Processor`/`Experiment` heralding, `Analyzer`, `Simulator.prob_amplitude`
**Confidence:** HIGH — every claim below was independently re-derived by running code directly against the installed `venv` (not inferred from docs/training data). Source line numbers cited throughout.

## Summary

This phase needs three things from Perceval's API: (1) the exact herald-success probability read off a non-sampled backend, (2) confirmation that success probability is uniform across inputs, and (3) the actual complex amplitude (not just probability) to verify the CZ sign. All three were run live against `venv/Lib/site-packages/perceval-quandela==1.2.4` in this repo during research, not assumed from memory or literature.

**Key results, already measured in this session (reproduce them in the deliverable script/test, don't just copy these numbers):**
- `heralded_cz`'s exact herald-success probability is **2/27 ≈ 0.07407407407407...**, uniform to floating-point precision across all 4 computational-basis dual-rail inputs, confirming (not just repeating) the design doc's previously-flagged literature figure.
- The `-1` phase on `|1,1⟩` is real and was measured directly via `Simulator.prob_amplitude`: amplitude ≈ `+0.27216552697590873` for `|00⟩,|01⟩,|10⟩` and ≈ `-0.2721655269759085` for `|11⟩` — `|amplitude|² = 2/27` in all four cases, sign flips only on `|11⟩`, exactly the CZ truth table.
- Superposition inputs (`|+⟩|+⟩` and `|+⟩|0⟩`) also give exactly `2/27` herald-success probability with correct output populations, confirming uniformity extends beyond the 4 computational-basis inputs (spot-checked, not exhaustively).
- **`logical_perf` is NOT bundling a second filter for this gate.** `Experiment.post_select_fn` on `heralded_cz`'s `build_experiment()` output is empty (`repr()` shows nothing) — the only heralding/post-selection mechanism is the two `add_herald(4,1)` / `add_herald(5,1)` calls. For computational-basis inputs, conditioned on herald success, 100% of the resulting probability mass lands on the single expected valid dual-rail output — no leakage was observed. This resolves the CONTEXT's open discretion question: an explicit assertion that `physical_perf == 1.0` (i.e., no photon-count filtering loss) is enough to demonstrate the herald/post-select split cleanly for this gate; a separate "valid-subspace" filter does not need its own check because none exists on this specific `Experiment`.

**Primary recommendation:** Build the standalone artifact around `Processor.compute_physical_logical_perf(True)` + `Processor.probs()`'s returned `global_perf`/`physical_perf`/`logical_perf` keys for the probability-only checks (criteria 1, 2, 4), and a *separate* `Simulator` built directly on `HeraldedCzItem().build_circuit()` (the bare 6-mode unitary, no `Processor`/heralds wrapper) with `prob_amplitude()` for the phase check (criterion 3) — heralds are not enforced by `Simulator.prob_amplitude`, so the herald condition must be encoded manually by choosing the herald *output* modes at population `(1,1)` and reading the corresponding amplitude, not by relying on any built-in heralding in `Simulator`.

## Standard Stack

### Core (already in this repo's venv — no new installs needed)

| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `perceval-quandela` | 1.2.4 | Photonic circuit simulation, `heralded_cz` catalog gate, `Processor`/`Analyzer`/`Simulator` | Already the project's chosen framework (all prior phases) |
| `pytest` | (already used, see `tests/test_perceval_fluency_demo.py`) | Committed test artifact | Matches Phase 8 precedent |
| `numpy` | (already a dependency) | `np.isclose`/tolerance checks, amplitude comparisons | Matches Phase 8/9 precedent |

No new packages are required for this phase.

## Architecture Patterns

### Two distinct object graphs are needed — do not try to get both probability and phase from one object

1. **Probability/herald-performance path**: `perceval.components.core_catalog.heralded_cz.HeraldedCzItem().build_experiment()` → `pcvl.Processor("SLOS", experiment)` → `proc.with_input(...)` → `proc.probs()`. This is the ONLY path that gives `global_perf`/`physical_perf`/`logical_perf`. `build_circuit()` alone (used directly, without `build_experiment()`) has no herald attached — confirmed in `HeraldedCzItem.build_circuit()`'s own source (`venv/Lib/site-packages/perceval/components/core_catalog/heralded_cz.py:54-72`), which builds a bare 6-mode `Circuit` with no `add_herald` calls. `build_experiment()` (lines 74-79) is what attaches `add_herald(4,1)` / `add_herald(5,1)`.

2. **Phase/amplitude path**: `perceval.simulators.Simulator` built directly on the bare `build_circuit()` output (via `perceval.backends.SLOSBackend()` + `Simulator(backend); sim.set_circuit(circuit)`), then `sim.prob_amplitude(input_state, output_state)`. This bypasses `Processor`/`Experiment` heralding entirely — heralds are not applied automatically. To get the physically meaningful heralded amplitude, the herald condition must be encoded **manually** in both the `input_state` and `output_state` `BasicState`s (see Code Examples below) — get this wrong (e.g. leaving herald modes at vacuum on input) and every amplitude silently comes back `0j`, which looks like a real result but is actually a setup bug (this was hit and diagnosed live during this research — see Common Pitfalls).

### Recommended script/module structure (matching Phase 8's `perceval_fluency_demo.py` precedent)

```
heralded_cz_derisking.py            # or similar name — module-level functions, no CLI framework
tests/test_heralded_cz_derisking.py # imports functions from the root module, asserts on them
```

Pattern from `perceval_fluency_demo.py` (verified by reading it directly): plain functions returning `(analyzer_or_sim, dist_or_amp)` tuples, a `main()` that prints + asserts + reports PASS/FAIL, and `if __name__ == "__main__": main()`. Tests import the functions and re-assert with `pytest.approx`. Follow this exactly — it is the established, already-reviewed pattern in this repo, not a new convention to invent.

### Pattern: reading `global_perf`/`physical_perf`/`logical_perf` off `Processor.probs()`

```python
# Source: verified directly against venv/Lib/site-packages/perceval/simulators/simulator_interface.py:125-138
# format_results() always returns {'results': ..., 'global_perf': physical_perf * logical_perf}.
# physical_perf and logical_perf keys are ONLY added if compute_physical_logical_perf(True) was called.
proc = pcvl.Processor("SLOS", experiment)
proc.compute_physical_logical_perf(True)   # without this, only 'results' and 'global_perf' come back
proc.with_input(pcvl.BasicState([1, 0, 1, 0]))  # 4-length: Processor auto-fills the 2 herald input modes
res = proc.probs()
# res == {'results': {BasicState([1,0,1,0]): 1.0},
#         'global_perf': 0.07407407407407401,
#         'physical_perf': 1.0,
#         'logical_perf': 0.07407407407407401}
```

Critical detail (HIGH confidence, verified by reading `Experiment.with_input`'s `FockState` dispatch, `venv/Lib/site-packages/perceval/components/experiment.py:854-868`): a `BasicState` of length 4 (matching `Processor.m`, the non-heralded port count) is accepted directly — `Processor`/`Experiment` automatically inserts the herald modes' **expected input photon count** (here, 1 photon in each of modes 4 and 5 — `add_herald(mode, expected)`'s docstring: "number of expected photon as input AND output on the given mode", `venv/Lib/site-packages/perceval/components/experiment.py:578`). This is not vacuum-in ancilla — it's a real injected photon per herald mode, both at input and required again at output. Getting this wrong when building a **manual** 6-mode input (e.g. for the `Simulator` phase-check path, which has no such auto-fill) silently zeroes every amplitude — see Common Pitfalls.

### Pattern: `Analyzer` for the truth-table check

```python
# Source: verified against venv/Lib/site-packages/perceval/algorithm/analyzer.py
inputs = [pcvl.BasicState([1,0,1,0]), pcvl.BasicState([1,0,0,1]),
          pcvl.BasicState([0,1,1,0]), pcvl.BasicState([0,1,0,1])]
an = Analyzer(proc, inputs, "*")
out = an.compute()
an.performance  # == min(logical_perf across all 4 inputs) == 2/27 here, since all 4 are uniform
pcvl.pdisplay(an)  # prints the row/col truth table — each input maps deterministically (prob 1) to itself
```

`Analyzer.performance` (`analyzer.py:167`, `self.performance = min(logical_perf)`) reads `logical_perf` if the underlying `probs()` call returned it, else falls back to `global_perf` (`analyzer.py:134-137`) — so calling `proc.compute_physical_logical_perf(True)` before constructing the `Analyzer` is what makes `an.performance` reflect the same number as `physical_perf * logical_perf` (they're equal here since `physical_perf == 1.0` for all tested inputs). This satisfies WT2-04's "read directly off `Analyzer.performance`/`logical_perf`" instruction.

**Analyzer output caveat:** `Analyzer` with `output_states="*"` also allocates columns for invalid/bunched states (e.g. `|0,0,2,0>`, `|2,0,0,0>`) since it enumerates `allstate_iterator` over all possible outputs — these all showed exactly `0` probability in the truth table run during this research (no leakage), but the columns exist and should be inspected/asserted-zero, not just ignored, to make "no leakage" an explicit checked claim rather than an eyeballed one.

### Pattern: phase-sensitive amplitude via `Simulator.prob_amplitude`

```python
# Source: verified against venv/Lib/site-packages/perceval/simulators/simulator.py:146-157
# and venv/Lib/site-packages/perceval/backends/_slos_exqalibur.py
from perceval.simulators import Simulator
from perceval.backends import SLOSBackend
from perceval.components.core_catalog.heralded_cz import HeraldedCzItem

item = HeraldedCzItem()
circuit = item.build_circuit()          # bare 6-mode Circuit, no herald metadata
sim = Simulator(SLOSBackend())
sim.set_circuit(circuit)

dual = {'0': (1, 0), '1': (0, 1)}       # dual-rail convention: bit 0 -> (1,0), bit 1 -> (0,1)
for ctrl in '01':
    for data in '01':
        cm, dm = dual[ctrl], dual[data]
        # Herald modes (indices 4,5) need a REAL input photon each (ancilla), not vacuum --
        # add_herald's "expected" count applies to input AND output.
        in_state  = pcvl.BasicState(list(cm) + list(dm) + [1, 1])
        out_state = pcvl.BasicState(list(cm) + list(dm) + [1, 1])  # herald clicks, data preserved
        amp = sim.prob_amplitude(in_state, out_state)
        # ctrl='1', data='1' -> amp ~= -0.27216552697590857 (the CZ minus sign)
        # all other 3 combos -> amp ~= +0.2721655269759086..0873
        # |amp|**2 == 2/27 in all 4 cases
```

Measured live during this research (values reproduced above in Summary). This is the correct, minimal way to get a phase-sensitive readout for this specific heralded gate — `Processor.probs()`/`Analyzer` are phase-blind (they only ever expose `|amplitude|²`), exactly the concern CONTEXT.md flagged.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Herald-success probability | Manual bookkeeping of which output states satisfy the herald condition, summed by hand | `Processor.compute_physical_logical_perf(True)` + `.probs()`'s `global_perf`/`physical_perf`/`logical_perf` | Perceval's `Simulator.probs_svd` (`simulator.py:581-657`) already computes exactly this via `post_select_distribution` and mode masking — reimplementing it risks silently disagreeing with Perceval's own semantics for what counts as "herald success" |
| Uniform-truth-table check across 4 inputs | 4 separate manual scripts/prints | One `Analyzer` call with all 4 inputs + `output_states="*"` | `Analyzer` already produces the full truth-table matrix in one call, including zero-check columns for invalid/bunched outputs, which is exactly criterion 3's request |
| Herald ancilla-photon bookkeeping for manual `Simulator` input | Guessing the herald input state (e.g. leaving it at vacuum) | `Experiment.in_heralds` (inspect `exp.in_heralds` on the `build_experiment()` output — `{4: 1, 5: 1}`) as the source of truth for what the herald modes' input photon count must be | Confirmed empirically: leaving herald modes at vacuum in a manual `Simulator` input silently returns `amplitude = 0j` for every case — a plausible-looking but wrong "gate always fails" result, not an error |

**Key insight:** every number this phase needs to report already has a first-class Perceval API returning it directly (`global_perf`, `physical_perf`, `logical_perf`, `Analyzer.performance`, `Simulator.prob_amplitude`) — none of it needs custom probability bookkeeping. The only genuinely manual work is correctly constructing the 6-mode `BasicState`s for the `Simulator` phase-check path, since that path has no automatic herald-input-fill (unlike `Processor.with_input` on a 4-length `BasicState`).

## Common Pitfalls

### Pitfall 1: Herald input modes need a real ancilla photon, not vacuum

**What goes wrong:** Building a manual 6-mode input for `Simulator.prob_amplitude` (or any bare-circuit path that bypasses `Processor`/`Experiment`) with the herald modes left at `[0, 0]` (vacuum) gives `amplitude = 0j` for every single input/output pair tested — a result that looks like "the gate never succeeds" but is actually "the ancilla photons were never supplied."

**Why it happens:** `add_herald(mode, expected)`'s docstring states `expected` is "the number of expected photon as input AND output on the given mode" (`experiment.py:578`). `heralded_cz` requires 1 photon injected into each of modes 4 and 5 as part of the physical input (this is the KLM/Knill-CZ ancilla-photon requirement), not just a detection condition on the output. `Processor.with_input()` on a 4-length `BasicState` auto-fills this via `Experiment.with_input`'s `FockState` dispatch (`experiment.py:854-868`, `input_list[k] = self.in_heralds[k]` for herald mode indices) — but any path that builds the 6-mode `BasicState` manually (i.e., the `Simulator`-direct phase-check path) must replicate this by hand.

**How to avoid:** Before writing the phase-check code, inspect `HeraldedCzItem().build_experiment().in_heralds` (returns `{4: 1, 5: 1}` in this version) and use those values, not an assumption, when constructing manual 6-mode `BasicState`s.

**Warning signs:** every `prob_amplitude` call returning exactly `0j` for physically-plausible input/output pairs is a strong signal of this bug, not evidence the gate fails universally — cross-check against the known-nonzero `global_perf` (2/27) from the `Processor.probs()` path before concluding a gate "doesn't work."

### Pitfall 2: `StateVector`/superposition inputs to `Processor.with_input` need the full `circuit_size`, and need `min_detected_photons_filter` set manually

**What goes wrong:** `Processor.with_input(state_vector)` where `state_vector`'s `BasicState` terms are only 4 modes long (matching the "logical" ctrl+data ports) raises `AssertionError: Input distribution contains states with a bad size (4), expected 6`. Even after fixing that (building 6-mode terms including the herald ancilla photons per Pitfall 1), `proc.probs()` then raises `ValueError: The value of min_detected_photons is not set` unless `proc.min_detected_photons_filter(...)` is called explicitly first.

**Why it happens:** `Experiment.with_input`'s `SVDistribution`/`StateVector` dispatch (`experiment.py:887-898`) asserts `svd.m == self.circuit_size` directly, with no auto-fill — unlike the plain `FockState`/`BasicState` dispatch (`experiment.py:854-868`), which is the one that auto-inserts herald modes. `min_detected_photons_filter` is likewise only auto-set by the `LogicalState` dispatch path (`experiment.py:848-852`, `self._min_detected_photons_filter = input_state.n`), not by the raw `StateVector` path.

**How to avoid:** For any superposition input, build 6-mode `BasicState` terms directly (data/ctrl ports + explicit `[1,1]` on the herald modes per Pitfall 1) and call `proc.min_detected_photons_filter(0)` (or any value ≤ the expected data-mode photon count — this research found 0, 1, and 2 all gave identical correct results for the tested cases) before `proc.probs()`.

**Warning signs:** `AssertionError` on `with_input` or `ValueError` on `probs()` — both are configuration gaps, not physics results; don't work around them by catching/suppressing.

### Pitfall 3: `logical_perf` bundling — verified negligible for this gate, but check `post_select_fn`, don't assume

**What goes wrong (the thing CONTEXT.md flagged):** `logical_perf` conceptually combines the herald condition with any additional post-selection filter (e.g., a filter rejecting data-mode outputs that fall outside the valid dual-rail subspace). If such a filter exists and isn't accounted for, citing `logical_perf` as "the herald probability" could be subtly wrong (it would also embed a data-validity filter's rejection rate).

**Resolution (HIGH confidence, verified by direct inspection):** `HeraldedCzItem().build_experiment().post_select_fn` is empty (its `repr()` prints nothing) — this specific `Experiment` has no `PostSelect` expression configured beyond the two `add_herald` calls. Combined with the empirical observation that, for every computational-basis input tested, 100% of the post-herald probability mass lands on exactly the expected single valid output (no bunched/invalid leakage), this confirms `logical_perf` for `heralded_cz` is purely the herald condition for this implementation — no separate hidden filter to disentangle. State this as a checked, not assumed, fact in the deliverable (cite `exp.post_select_fn` being empty + the zero-leakage `Analyzer` truth table as the two pieces of evidence).

**How to avoid regressing this claim:** if this phase's script changes the `Experiment`/`Processor` construction path in a way that adds a `min_detected_photons_filter` or any other post-select, re-verify `physical_perf == 1.0` still holds — that's the signal that no additional filtering silently crept in.

### Pitfall 4: `build_circuit()` alone has no herald — a `Processor` built directly from it will not condition on anything

**What goes wrong:** Calling `HeraldedCzItem().build_circuit()` and wrapping it in a bare `Processor("SLOS", circuit)` (rather than `build_experiment()`) produces a `Processor` with no heralds at all — `proc.heralds` would be empty, `proc.m == 6` (not 4), and `probs()` would report raw 6-mode output probabilities with no herald-conditioning or `global_perf`/`logical_perf` distinction. This is exactly the mistake CONTEXT.md/the phase success criteria explicitly warn against ("never `build_circuit()`, which drops the herald").

**How to avoid:** Always use `build_experiment()` for anything touching herald-success probability or the conditioned truth table. Reserve `build_circuit()` for the phase-amplitude path only, where the herald condition is instead encoded manually via the chosen output `BasicState`'s herald-mode values (Pattern above) rather than via Perceval's built-in heralding machinery.

## Code Examples

### Full herald-success-probability check (criteria 1, 2, 4)

```python
import perceval as pcvl
from perceval.algorithm import Analyzer
from perceval.components.core_catalog.heralded_cz import HeraldedCzItem

def build_heralded_cz_processor():
    item = HeraldedCzItem()
    exp = item.build_experiment()          # NOT build_circuit() -- this attaches the heralds
    proc = pcvl.Processor("SLOS", exp)
    proc.compute_physical_logical_perf(True)  # exposes physical_perf/logical_perf separately
    return proc

def measure_herald_success(basis_input: pcvl.BasicState) -> dict:
    proc = build_heralded_cz_processor()
    proc.with_input(basis_input)            # 4-length; Processor auto-fills herald ancilla photons
    return proc.probs()                     # {'results':..., 'global_perf':..., 'physical_perf':..., 'logical_perf':...}

COMPUTATIONAL_BASIS = [
    pcvl.BasicState([1, 0, 1, 0]),  # |00>
    pcvl.BasicState([1, 0, 0, 1]),  # |01>
    pcvl.BasicState([0, 1, 1, 0]),  # |10>
    pcvl.BasicState([0, 1, 0, 1]),  # |11>
]
```

Measured result set (this session, `perceval-quandela==1.2.4`):

| ctrl,data | global_perf (== physical_perf × logical_perf) | physical_perf | logical_perf |
|---|---|---|---|
| 0,0 | 0.0740740740740741 | 1.0 | 0.0740740740740741 |
| 0,1 | 0.07407407407407404 | 1.0 | 0.07407407407407404 |
| 1,0 | 0.07407407407407401 | 1.0 | 0.07407407407407401 |
| 1,1 | 0.07407407407407399 | 1.0 | 0.07407407407407399 |

All four agree with `2/27 = 0.0740740740740740740...` to floating-point precision (differences at the ~1e-16 level are backend floating-point noise, same order of magnitude as the `n=2/3` TVD results Phase 9 reported).

### Phase check (criterion 3)

Already given in full under "Architecture Patterns" above. Measured result set:

| ctrl,data | amplitude | \|amplitude\|² |
|---|---|---|
| 0,0 | `0.27216552697590873 - 3.3e-17j` | 0.0740740740740741 |
| 0,1 | `0.2721655269759086 - 3.3e-17j` | 0.07407407407407404 |
| 1,0 | `0.27216552697590857 - 6.7e-17j` | 0.07407407407407401 |
| 1,1 | `-0.2721655269759085 + 6.7e-17j` | 0.07407407407407399 |

`sqrt(2/27) = 0.27216552697590867...` — matches all four magnitudes. Sign flips exactly on `|11⟩`, confirming the CZ diagonal `diag(1,1,1,-1)`.

### Superposition spot-checks (CONTEXT.md-mandated coverage beyond the 4 computational-basis inputs)

`|+⟩|+⟩` (both qubits in equal superposition): built as a 4-term `StateVector` (`(1,0)`/`(0,1)` per qubit × `[1,1]` herald ancilla per term), requires `proc.min_detected_photons_filter(0)` (or any value ≤ 2) before `probs()` since the `StateVector` input path has no auto-fill (Pitfall 2). Result: uniform `0.25` population across all 4 valid output states, `global_perf ≈ 0.07407407407407404` — same herald-success rate as the computational-basis case, and population stays uniform (expected: CZ only imparts phase, doesn't redistribute population for this input).

Asymmetric case `|+⟩⊗|0⟩` (ctrl in superposition, data fixed at `|0⟩`): 2-term `StateVector`. Result: `{|1,0,1,0⟩: 0.5, |0,1,1,0⟩: 0.5}`, `global_perf ≈ 0.07407407407407406` — again uniform herald-success rate.

## State of the Art

| Old Approach (docs/iqp-photonic-encoding.md, currently) | Current Approach (this phase's finding) | When Changed | Impact |
|---|---|---|---|
| "The specific success probability was **not** independently recomputed from this circuit — the 1/9... and ~2/27... figures... are secondhand literature citations... not a verified property of this exact implementation" (ENC-01, line 184 as read) | Directly measured: **2/27 exactly**, uniform across all 4 computational-basis inputs + 2 superposition spot-checks, via `Processor.probs()`'s `global_perf` | This phase (10) | The "Open Questions" bullet "Success-probability figure unverified" (`docs/iqp-photonic-encoding.md` Conclusion section) and the ENC-01 line above are now stale and need updating to state the confirmed figure, per WT2-08 / success criterion 4 — described, not claimed equal to the literature figures (2/27 for the heralded variant happens to match the commonly-cited ~2/27 figure to the precision quoted in the doc, but the doc's own framing — "descriptive only, no equality claimed" — should be preserved even though the numbers do match) |

**Not deprecated, just newly load-bearing:** `Processor.compute_physical_logical_perf(True)` was not used anywhere in Phase 8/9's code (their `Analyzer`/`Processor` usage never needed to distinguish `physical_perf` from `logical_perf` since STATE.md notes "weight-1's `run_full_circuit` pattern never needed to read it"). This phase is the first to need it as a first-class reported value.

## Open Questions

1. **Exact file name for the standalone script/test.**
   - What we know: Phase 8's precedent is `perceval_fluency_demo.py` (root) + `tests/test_perceval_fluency_demo.py`. Phase 9's photonic-encoding module is `iqp_photonic_encoding.py` (root) + `tests/test_iqp_photonic_encoding.py`.
   - What's unclear: nothing structurally — CONTEXT.md explicitly leaves the exact name to Claude's discretion, following the established pattern.
   - Recommendation: `heralded_cz_derisking.py` (root) + `tests/test_heralded_cz_derisking.py` — descriptive of the phase's actual deliverable, matches the existing `snake_case_topic.py` naming convention.

2. **Whether to also assert `exp.post_select_fn` emptiness in the committed test, or just narrate it.**
   - What we know: it's empty for this specific catalog gate/version, verified directly.
   - What's unclear: whether a future Perceval version could add a post-select expression to this catalog item, silently changing what `logical_perf` means for this gate.
   - Recommendation: assert it explicitly in the pytest test (e.g. `assert not str(exp.post_select_fn).strip()` or equivalent) so a future `perceval-quandela` upgrade that changes this would fail loudly rather than silently invalidating the "logical_perf is pure herald" claim in the design doc.

## Sources

### Primary (HIGH confidence — direct source inspection + live execution against installed venv)
- `venv/Lib/site-packages/perceval/components/core_catalog/heralded_cz.py` (full file read) — `HeraldedCzItem.build_circuit()`/`build_experiment()`, herald mode indices (4,5), Knill CZ reference (arXiv:quant-ph/0110144)
- `venv/Lib/site-packages/perceval/algorithm/analyzer.py` (full file read) — `Analyzer.__init__`/`compute()`/`.performance` semantics, `logical_perf`/`global_perf` fallback logic
- `venv/Lib/site-packages/perceval/runtime/processor.py` (`probs()` method, lines 193-218) and `venv/Lib/site-packages/perceval/runtime/abstract_processor.py` (`add_herald` docstring, lines 229-239) — herald input/output photon-count semantics
- `venv/Lib/site-packages/perceval/simulators/simulator.py` (`probs_svd`, `evolve_svd`, `prob_amplitude`, lines 146-238, 581-817) — `physical_perf`/`logical_perf` computation internals
- `venv/Lib/site-packages/perceval/simulators/simulator_interface.py` (`format_results`, lines 125-138) — confirms `global_perf = physical_perf * logical_perf`, and that `physical_perf`/`logical_perf` keys are opt-in via `compute_physical_logical_perf(True)`
- `venv/Lib/site-packages/perceval/backends/_slos_exqalibur.py` (full file read) — `SLOSExqaliburBackend.prob_amplitude` implementation
- `venv/Lib/site-packages/perceval/components/experiment.py` (`with_input` dispatches, lines 848-898; `add_herald`, lines 573-591) — herald-mode auto-fill behavior differences between `FockState` and `StateVector` input paths
- Live Python execution against this repo's `venv/Scripts/python.exe` (perceval-quandela 1.2.4) — all numeric results in this document (2/27 uniformity, phase amplitudes, superposition spot-checks) were produced by running code directly, not estimated

### Secondary (MEDIUM confidence)
- `perceval_fluency_demo.py` + `tests/test_perceval_fluency_demo.py` (this repo, Phase 8) — read directly for the artifact-structure/naming precedent this phase should follow
- `docs/iqp-photonic-encoding.md` (this repo, Phase 9) — read directly for the exact current wording of the Ingredient 2 / Open Questions / Conclusion sections that need updating per WT2-08

### Tertiary (LOW confidence)
- None used — every claim in this document traces to direct source inspection or live execution, not WebSearch/training-data recall. No literature-figure verification (1/9, ~2/27) was needed beyond what Phase 9 already cited, since this phase's job is to measure the actual figure independently, which was done directly.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new dependencies, reused exactly what Phase 8/9 already established
- Architecture (Processor+Analyzer vs. Simulator split): HIGH — both paths were built and run live, including debugging the two pitfalls that would otherwise silently produce wrong-looking-right results (vacuum herald input, `StateVector` sizing)
- Pitfalls: HIGH — all four were actually hit and diagnosed during this research session, not hypothesized

**Research date:** 2026-08-06
**Valid until:** Should remain valid as long as `perceval-quandela==1.2.4` is pinned in this repo's venv; re-verify `exp.post_select_fn` emptiness and the herald ancilla-photon requirement if the Perceval version changes.
