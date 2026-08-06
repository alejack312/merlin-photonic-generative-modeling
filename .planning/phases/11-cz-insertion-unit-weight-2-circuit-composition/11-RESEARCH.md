# Phase 11: CZ Insertion Unit & Weight-2 Circuit Composition - Research

**Researched:** 2026-08-06
**Domain:** Perceval (perceval-quandela==1.2.4) Processor-level composition of a herald-carrying catalog gate into an existing bare-Circuit polarization pipeline
**Confidence:** HIGH — every API-mechanics claim below was verified by reading the installed `perceval-quandela==1.2.4` source directly and/or executing real code against this repo's own venv (`./venv/Scripts/python.exe`), not inferred from documentation or training-data memory.

## Summary

`heralded_cz`'s bare 6-mode circuit (`HeraldedCzItem().build_circuit()`) can be composed into the existing `Circuit(2n)` weight-1 layout using plain `Processor.add(mode_mapping, bare_circuit)` with a **dict** mode mapping (not an int offset, since qubits `i`/`j` need not be adjacent and two brand-new herald-ancilla modes have no home in the `2n`-mode layout). The herald ancilla modes must be pre-allocated as extra modes at the end of the outer `Processor`'s total mode count (`2n + 2`), wired in via the dict mapping alongside qubit `i`'s and `j`'s ports, and then registered with `Processor.add_herald(global_mode, 1)` **after** the `.add()` call, using the mode's *global* index — this was empirically confirmed to work exactly as expected (see Code Examples).

The single most important and non-obvious finding: **directly wiring the module's own PBS dual-rail output into `heralded_cz`'s ctrl/data ports puts the CZ's `-1` phase on logical `|00⟩`, not `|11⟩`.** This was verified by actually running the composed circuit. **This is not a bug in `heralded_cz`, and it is not an accidental reversal in this module's own code either — confirmed by reading source, not inferred:**
- `heralded_cz.py:74-79`'s `build_experiment()` explicitly declares `Port(Encoding.DUAL_RAIL, 'ctrl')`/`Port(Encoding.DUAL_RAIL, 'data')` — it uses Perceval's own named, standard dual-rail encoding, not an ad-hoc internal choice.
- `port.py:151-152` defines that encoding: `return [0, 1] if qubit_state[0] else [1, 0]` — Perceval's `Encoding.DUAL_RAIL` standard maps logical **1 → Fock pattern (0,1)**, logical **0 → (1,0)**.
- This module's own convention (Plan 09-02, established from measuring the *physical* PBS port behavior with real H/V polarization input) is the mirror image: `H (bit "0") → (0,1)`, `V (bit "1") → (1,0)`.

Both conventions are independently correct and internally consistent — `heralded_cz` correctly puts `-1` on Perceval's own standard logical `|1,1⟩`; this module's PBS convention was correctly derived from real physical port measurement. They just weren't chosen to match each other, because one is a physics-driven polarization convention and the other is an abstract qubit-encoding standard with no reason to agree. **`build_cz_insertion` needs a convention adapter at this boundary, not a bug fix** — the swap is real and still required, but frame it in code comments/docstrings as "translates between this module's physical PBS convention and Perceval's own `Encoding.DUAL_RAIL` standard," not as correcting something `heralded_cz` (or this module) got wrong. (This is a good habit regardless — Plan 09-02's H/V port-labeling correction *was* an actual bug in this module's own code; this is a different, more common situation: two correct components meeting at a boundary with different conventions.) The truth-table check (Success Criterion 1) is still the thing that pins the adapter down empirically, not an assumption.

**Primary recommendation:** Build `build_cz_insertion(n, i, j)` as a bare `Circuit(6)` (matching `heralded_cz`'s own local numbering: ctrl dual rail = local 0,1; data dual rail = local 2,3; herald ancilla = local 4,5) containing `PBS` (local 0,1), `PBS` (local 2,3), `heralded_cz`'s bare circuit, `PBS` (local 0,1), `PBS` (local 2,3) again for the unwrap — and have the function additionally return (or document) the herald spec `{4: 1, 5: 1}` (local indices, read from `HeraldedCzItem().build_experiment().in_heralds`, not hardcoded). The **caller** (the outer assembly code) is responsible for computing the mode-mapping dict that both places qubit `i`/`j`'s ports correctly *and* applies the ctrl/data swap fix, wires in the 2 new ancilla modes at `2n`/`2n+1`, and calls `add_herald` at the shifted global indices immediately after composition.

## Standard Stack

No new libraries needed. This phase composes existing installed primitives:

| Component | Source | Purpose |
|---|---|---|
| `perceval.Processor` | top-level `perceval` package | Outer composition target — `.add()`, `.add_herald()`, `.heralds` |
| `perceval.components.core_catalog.heralded_cz.HeraldedCzItem` | `perceval-quandela==1.2.4` | `.build_circuit()` (bare, no herald metadata) and `.build_experiment()` (herald-attached, used only to *read* `in_heralds`/`heralds` dicts, never actually added directly per the locked CONTEXT decision) |
| `perceval.PBS`, `pcvl.Circuit` | same as Phase 9 | Wrap/unwrap polarization ↔ dual rail |
| `perceval.simulators.Simulator` + `perceval.backends.SLOSBackend` | same as Phase 10 | Phase-sign verification (Processor/Analyzer are phase-blind) |

No installation changes — `requirements.txt` already pins `perceval-quandela==1.2.4`.

## Architecture Patterns

### Pattern: bare-Circuit sub-gate + manual herald re-registration (per locked CONTEXT decision)

**What:** `build_cz_insertion(n, i, j)` returns a bare `Circuit(6)`, matching every other weight-1 builder's `Circuit` return-type convention — not an `Experiment`/`Processor`. It also surfaces the herald spec (local indices `{4: 1, 5: 1}`, read off `HeraldedCzItem().build_experiment().in_heralds` — don't hardcode `4`/`5` even though they're currently stable, since `HeraldedCzItem.build_circuit()`'s internal layout is what fixes them, and reading them keeps the code honest if the catalog gate implementation ever changes internally).

**Why this over composing the herald-carrying `Experiment` directly:** `Processor.add()` *can* accept an `Experiment`/`Processor` directly and will auto-propagate heralds via `Experiment._compose_experiment` (HIGH confidence, read from `perceval/components/experiment.py:389-533`) — but that automatic path appends new herald modes "at the bottom" of the *processor's current total mode count at the time of that `.add()` call* (`connector.add_heralded_modes`: `new_mode_index = self._le.circuit_size`), which is fragile/order-dependent and opaque about exactly which global indices end up heralded. The locked CONTEXT decision (bare `Circuit` + explicit manual herald re-add) is the right call for auditability: the plan can state the exact global herald indices in a docstring/assertion rather than relying on an internal composition-order side effect.

**Verified working example** (executed against this repo's venv):

```python
# Source: verified live against ./venv (perceval-quandela==1.2.4)
import perceval as pcvl
from perceval.components.core_catalog.heralded_cz import HeraldedCzItem

item = HeraldedCzItem()
bare = item.build_circuit()                       # Circuit(6), no herald metadata
in_heralds = item.build_experiment().in_heralds    # {4: 1, 5: 1} -- read, not hardcoded

n = 3
total_modes = 2 * n + 2          # 2n register modes + 2 ancilla modes appended at the end
proc = pcvl.Processor("SLOS", total_modes)

i, j = 0, 2  # qubit indices (need not be adjacent)
mapping = {
    2 * i: 1, 2 * i + 1: 0,      # SWAPPED -- see "Common Pitfalls" below
    2 * j: 3, 2 * j + 1: 2,      # SWAPPED
    2 * n: 4, 2 * n + 1: 5,      # new ancilla modes, straight (no swap needed for these)
}
proc.add(mapping, bare)

# proc.m == total_modes here (8) -- heralds not yet registered
proc.add_herald(2 * n, 1)
proc.add_herald(2 * n + 1, 1)
# proc.m == 6 now (== 2n, the original register size) -- with_input() only needs
# a 2n-length input state; the 2 ancilla photons auto-fill, exactly like Phase 10's
# 4-mode -> 6-mode auto-fill on the standalone heralded_cz Processor.
# proc.heralds == {6: 1, 7: 1}  (global indices, i.e. 2n, 2n+1)
```

This was actually executed (not just read) and produced exactly: `proc.m` before `add_herald` = 8, after = 6, `proc.heralds` = `{6: 1, 7: 1}`, `proc.in_heralds` = `{6: 1, 7: 1}`.

### Pattern: outer assembly at `Processor(2n+2)`, weight-1 builders added at offset 0 unchanged

Because `Circuit`-typed weight-1 builders (`build_state_prep_circuit(n)` etc.) return exactly `Circuit(2n)`, and `Processor.add(0, some_2n_circuit)` with an **int** mode_mapping only ever touches modes `0..2n-1` (confirmed from `ModeConnector.resolve`'s int-branch, which walks `map_begin + i` sequentially and only skips modes that are *already-registered heralds on the outer processor* — irrelevant here since the outer processor's herald registration for the ancilla pair happens at `2n`/`2n+1`, outside that range), the existing weight-1 builders can be added at `.add(0, builder(...))` exactly as before, unmodified, with the 2 extra ancilla modes at the tail simply untouched (left at vacuum/unused) by every non-CZ builder call.

Recommended assembly order:
```
proc = Processor("SLOS", 2*n + 2)
proc.add(0, build_state_prep_circuit(n))
proc.add(0, build_diagonal_layer_circuit(n, thetas))   # thetas already folded w/ +pi/4 additively
proc.add(cz_mode_mapping, build_cz_insertion(n, i, j))  # PBS-wrap -> heralded_cz -> PBS-unwrap, swapped mapping
proc.add_herald(2*n, 1); proc.add_herald(2*n+1, 1)      # immediately after composition, per Success Criterion 3
proc.add(0, build_conjugation_circuit(n))
proc.add(0, build_readout_circuit(n))
```
The exact position of the CZ insertion relative to the (folded) diagonal layer doesn't matter physically since all these operators are diagonal and commute (already established in `docs/iqp-photonic-encoding.md`'s commutativity argument) — placing it adjacent to the diagonal layer, before conjugation, mirrors the on-paper derivation in that doc most directly.

### Anti-Patterns to Avoid
- **Composing `HeraldedCzItem().build_experiment()` directly via `Processor.add()`** — contradicts the locked CONTEXT decision (WT2-01 explicitly requires the manual-herald-surfacing approach), and its automatic "append heralds at the bottom" behavior is order-dependent and less auditable for a plan a reader must be able to explain unaided.
- **Feeding the module's raw PBS dual-rail output straight into `heralded_cz`'s ctrl/data ports without the swap** — produces a *physically wrong* gate (`diag(-1,1,1,1)`, not globally-phase-equivalent to `diag(1,1,1,-1)`), verified by direct execution. See Common Pitfalls.
- **Hardcoding herald mode indices `4`/`5`** — read them from `HeraldedCzItem().build_experiment().in_heralds` (Phase 10's own established pattern), so a future `perceval-quandela` version bump that changes the catalog gate's internal layout fails loudly via an assertion instead of silently miswiring heralds.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Mapping non-adjacent qubit ports + new ancilla modes into a sub-component | Manual index bookkeeping / custom PERM construction | `Processor.add(mode_mapping_dict, component)` | `ModeConnector` already handles arbitrary non-contiguous dict mappings, auto-inserts the needed `PERM` before the component and its inverse after (confirmed: `Experiment._add_component` appends `perm_component` then `perm_inv` — the outer mode numbering is fully restored after the `.add()` call, so mode `2i` is still "mode `2i`" for every subsequent `.add()` call) |
| Verifying the CZ's `-1` phase sign after composition | Trusting Processor.probs()/Analyzer output | `Simulator(SLOSBackend()).prob_amplitude(in_state, out_state)` on the bare (pre-composition or isolated) 6-mode dual-rail state | `Processor.probs()`/`Analyzer` are phase-blind (`|amplitude|²` only) — this was already the exact reason Phase 10 built `measure_cz_phase` |

**Key insight:** Perceval's own `mode_mapping` dict mechanism already solves "arbitrary sub-component placement + extra ancilla modes" — the only genuinely new code this phase needs is (a) the swap fix in the mapping dict and (b) reading/re-registering herald indices, both of which are thin, auditable, a few lines each.

## Common Pitfalls

### Pitfall 1: `heralded_cz`'s ctrl/data bit convention (Perceval's own `Encoding.DUAL_RAIL` standard) is the mirror image of this module's PBS convention — not a bug on either side (HIGH confidence — empirically verified by direct execution AND confirmed from source: `heralded_cz.py`'s `Port(Encoding.DUAL_RAIL, ...)` declarations + `port.py`'s `Encoding.DUAL_RAIL` definition)

**What goes wrong:** Wiring the module's PBS dual-rail output straight into `heralded_cz`'s local ports (`0,1`=ctrl, `2,3`=data) with no adjustment produces the `-1` phase on module-logical `|00⟩` instead of `|11⟩`.

**Why it happens:** This module's `build_readout_circuit`'s `PBS()` (same component used for the PBS-wrap step here) empirically gives `H (bit "0") → local pair (0,1)`, `V (bit "1") → local pair (1,0)` (established in Plan 09-02, re-confirmed here). `heralded_cz`'s internal circuit (its own `PERM`/beamsplitter structure, unrelated to this module) triggers its `-1` phase on local ctrl-pair pattern `(0,1)` AND data-pair pattern `(0,1)` simultaneously — which, per this module's own convention, is the physical pattern for bit **"0"**, not "1". Directly executed proof (against `./venv`, `perceval-quandela==1.2.4`):

```
Module PBS-derived dual-rail pattern per bit, fed straight into heralded_cz:
bits=00 readout_dual_rail=[0, 1, 0, 1] amplitude=-0.2722  <- WRONG: -1 lands on |00>
bits=01 readout_dual_rail=[0, 1, 1, 0] amplitude=+0.2722
bits=10 readout_dual_rail=[1, 0, 0, 1] amplitude=+0.2722
bits=11 readout_dual_rail=[1, 0, 1, 0] amplitude=+0.2722  <- WRONG: should be negative here
```

**How to avoid:** Swap each qubit's local dual-rail pair order in the mode-mapping dict before wiring into `heralded_cz` — i.e. map polarization-carrying port `2k → heralded_cz local slot 1`, vacuum-partner port `2k+1 → heralded_cz local slot 0` (for both `i` as ctrl and `j` as data). Directly verified this produces the correct `diag(1,1,1,-1)`:

```
With each qubit's dual-rail pair swapped:
bits=00 swapped=[1, 0, 1, 0] amplitude=+0.2722
bits=01 swapped=[1, 0, 0, 1] amplitude=+0.2722
bits=10 swapped=[0, 1, 1, 0] amplitude=+0.2722
bits=11 swapped=[0, 1, 0, 1] amplitude=-0.2722  <- CORRECT: -1 exactly on |11>
```

**Warning signs:** If Success Criterion 1's truth-table check (which the plan MUST implement using `Simulator.prob_amplitude`, per Phase 10's own established pattern, not `Processor.probs()`/`Analyzer` alone) shows the `-1` sign on any bit pattern other than `|11⟩`, this swap is the fix — don't reach for a different mode-mapping topology or assume the catalog gate is broken.

**This must be an explicit, asserted check in the plan's implementation** (mirroring `heralded_cz_derisking.py`'s `check_phase_sign`), not an assumption carried over silently — this is exactly the class of "self-consistent but backwards" bug the project has hit once already (Plan 09-02's H/V port-labeling fix), and the CONTEXT.md's own truth-table verification-scope requirement (item 2) is designed to catch it.

### Pitfall 2: Herald ancilla modes need to be pre-sized into the outer `Processor`'s total mode count from construction

**What goes wrong:** `Processor.add()` with a dict mapping requires every mapping key (global mode) to already exist and be connectible (`ModeConnector._check_consistency` calls `self._le.is_mode_connectible(m_out)`) — you cannot map onto a mode index that doesn't exist yet.

**Why it happens:** `Experiment.add()`'s auto-sizing (`if self.m == 0: self.m = ...`) only fires when the processor starts completely empty; once any modes exist, `m` doesn't grow implicitly.

**How to avoid:** Construct the outer `Processor("SLOS", 2*n + 2)` up front with room for the herald ancilla pair, before adding any weight-1 builder circuits. Directly verified: `Processor("SLOS", 8)` (n=3) → `.add(mapping_including_modes_6_7, bare_cz)` → `proc.m` correctly reads 8 before `add_herald`, 6 after.

### Pitfall 3: `add_herald` must use the outer Processor's *global* mode index, computed from the same mapping dict used in `.add()`

**What goes wrong:** Calling `add_herald(4, 1)` / `add_herald(5, 1)` (the *local* indices from `HeraldedCzItem`) on the outer `Processor` either errors (if those global modes are already occupied by qubit ports) or silently heralds the wrong modes.

**How to avoid:** The caller must track, from the exact mode-mapping dict passed to `Processor.add()`, which global mode each local herald index (`4`, `5`) landed on — in the recommended layout that's always `2n` and `2n+1` (the two modes appended past the register), regardless of which `i`/`j` pair is targeted. `Processor.add_herald(2*n, 1)`, `Processor.add_herald(2*n+1, 1)`.

### Pitfall 4: `Processor.heralds` is empty until `add_herald` is called explicitly on the outer Processor — composing a bare `Circuit` never populates it automatically

**Why it happens:** `_add_component` (the plain-`AComponent` composition path, used because `build_cz_insertion` returns a bare `Circuit`, not an `Experiment`) has no herald-propagation logic at all (unlike `_compose_experiment`, which is only reached when the composed object is an `Experiment`/`Processor`). This is exactly why Success Criterion 3 ("assembled processor's `heralds` property is confirmed non-empty immediately after assembly") exists as a guard — the actual failure mode it's protecting against is the executor forgetting to call `add_herald` at all after using the bare-`Circuit` path, silently producing a Processor that runs an un-heralded raw unitary. Verified empirically: `proc.heralds` reads `{}` immediately after `.add(mapping, bare_cz)` and only becomes `{6: 1, 7: 1}` after the two explicit `add_herald` calls.

### Pitfall 5: Mode ordering is restored after a plain-`Circuit` `.add()` call — verified, not assumed

**What could go wrong (if untrue):** If `Processor.add()`'s internal permutation-and-inverse-permutation mechanics did *not* restore original mode ordering, every subsequent `.add(0, build_conjugation_circuit(n))` call downstream of the CZ insertion could be silently wired to the wrong physical modes.

**How this was checked:** Read `Experiment._add_component` (`perceval/components/experiment.py:535-561`) directly — for a plain `AComponent`, it always appends a `PERM` before the component and `perm_inv` (its exact algebraic inverse, `perm_component.copy().inverse(h=True)`) after, when the mapping requires reordering. This means the outer processor's mode numbering is transparently preserved: mode `2i` is still "mode `2i`" for every `.add()` call that follows the CZ insertion. HIGH confidence — read directly from source, and consistent with the executed `proc.heralds == {6: 1, 7: 1}` result matching the exact global indices requested.

## Code Examples

### Reading herald spec without hardcoding
```python
# Source: verified against perceval-quandela==1.2.4 installed source
# (perceval/components/core_catalog/heralded_cz.py)
from perceval.components.core_catalog.heralded_cz import HeraldedCzItem

item = HeraldedCzItem()
bare_circuit = item.build_circuit()                    # Circuit(6): ctrl(0,1) data(2,3) herald(4,5)
herald_spec = item.build_experiment().in_heralds        # {4: 1, 5: 1} -- read every time, don't hardcode
```

### Regression: bit-identical unitary comparison for weight-1 builders (Success Criterion 4 / CONTEXT item 4)
```python
# Source: perceval/components/linear_circuit.py's compute_unitary (verified present, signature confirmed)
import numpy as np
before = build_state_prep_circuit(n).compute_unitary()   # returns a Matrix (numpy-array-like)
after = build_state_prep_circuit(n).compute_unitary()    # after Phase 11's changes, same call
assert np.array_equal(np.array(before, dtype=complex), np.array(after, dtype=complex))
```
Note: `WP`/`HWP`/`PBS` all set `_supports_polarization = True`, so `compute_unitary()` on these builders returns a polarization-doubled matrix automatically (`use_polarization` defaults to `True` whenever `_supports_polarization` is set) — no extra flag needed, confirmed from `LinearCircuit.compute_unitary`'s source (`linear_circuit.py:72-94`).

## State of the Art

Not applicable in the usual sense (no library-version churn here) — the one relevant fact is that `perceval-quandela==1.2.4` is the version this whole project has pinned and tested against since Phase 9/10; no need to re-verify version currency for this phase.

## Open Questions

1. **Whether the swap fix should live inside `build_cz_insertion`'s own bare `Circuit(6)` (via an internal `PERM`) or in the caller's mode-mapping dict.**
   - What we know: both are mechanically equivalent and both were exercised during this research (the dict-level swap is what was actually tested end-to-end above; an internal-`PERM` version was not separately executed but is algebraically identical — swapping which local port maps to which global port is exactly what a `PERM([1,0])` component placed at the start/end of the sub-circuit would do).
   - What's unclear: which placement better matches the phase's stated shape ("`build_cz_insertion(n, i, j)` (PBS-wrap → `heralded_cz` → PBS-unwrap)" — CONTEXT item 1 describes it as three visible steps, which reads more naturally as a self-contained `Circuit(6)` doing its own internal wiring than as a caller-side mapping trick).
   - Recommendation: put the swap inside `build_cz_insertion` itself, as an internal `PERM([1,0])` (or equivalent local-port relabeling) immediately before and after the `heralded_cz` sub-block, so the function's contract is "give me qubit `i`'s two ports and qubit `j`'s two ports in the module's normal `(polarization-mode, vacuum-partner)` order, get back the correctly-signed CZ" — keeping the caller's mode-mapping dict a plain, unswapped `{2i:0, 2i+1:1, 2j:2, 2j+1:3, 2n:4, 2n+1:5}`. This is very slightly extra work but keeps the convention-fix contained in one place instead of leaking into every call site, and matches the "reusing weight-1 builders unmodified" spirit — `build_cz_insertion` becomes the one function that has to know about this quirk.

2. **Whether success probability changes at all when composed with the rest of the pipeline (vs. Phase 10's standalone 2/27).**
   - What we know: Phase 10 confirmed 2/27 for the bare `heralded_cz` alone. This phase's PBS-wrap/unwrap steps are exact, deterministic, lossless unitaries (already established for `PBS` in Phase 9), so composing them shouldn't change the herald-success probability.
   - What's unclear: not independently re-verified end-to-end in this research pass (time-boxed to the composition-mechanics questions the phase actually asked). Cheap to check: run `proc.compute_physical_logical_perf(True)` + `proc.probs()` on the fully-assembled weight-2 processor at a fixed computational-basis input and confirm `global_perf` still reads `2/27`.
   - Recommendation: add this as a cheap sanity assertion in the plan's implementation, not a separate research question — one extra `probs()` call.

## Sources

### Primary (HIGH confidence — read directly from installed source and/or executed)
- `venv/Lib/site-packages/perceval/components/core_catalog/heralded_cz.py` — `HeraldedCzItem.build_circuit()`/`build_experiment()`, confirms 6-mode layout (ctrl 0-1, data 2-3, herald 4-5) and `add_herald(4,1)`/`add_herald(5,1)`.
- `venv/Lib/site-packages/perceval/runtime/abstract_processor.py` (lines ~194-329) — `AProcessor.add`, `add_herald`, `heralds`/`in_heralds` properties, all delegate to `self.experiment`.
- `venv/Lib/site-packages/perceval/components/experiment.py` (lines 262-591) — `Experiment.add` dispatch, `_compose_experiment` (auto herald-shifting for Experiment/Processor components), `_add_component` (plain-`AComponent` path: PERM + inverse-PERM, no herald propagation), `add_herald`.
- `venv/Lib/site-packages/perceval/components/_mode_connector.py` (full file) — `ModeConnector.resolve` (int/list/dict mapping resolution), `add_heralded_modes`, `generate_permutation`.
- `venv/Lib/site-packages/perceval/components/unitary_components.py` — `PBS` unitary/docstring ("converts a superposition of polarisation modes in a single spatial mode to... two spatial modes, and vice versa").
- `venv/Lib/site-packages/perceval/components/linear_circuit.py` (lines 60-105) — `compute_unitary`/`U` for the regression bit-identical check.
- Live execution against `./venv/Scripts/python.exe` (this repo's actual installed `perceval-quandela==1.2.4`):
  - Confirmed `Processor.add(dict_mapping, bare_circuit)` + `add_herald(global_idx, 1)` post-composition workflow (`proc.m`: 8→6, `proc.heralds`: `{}`→`{6:1,7:1}`).
  - Confirmed the ctrl/data dual-rail convention mismatch and its swap fix by directly running `iqp_photonic_encoding.py`'s `build_readout_circuit`/`bitstring_to_fock`/`run_readout` piped into `heralded_cz`'s bare circuit via `Simulator(SLOSBackend()).prob_amplitude`, both unswapped (wrong, `-1` on `|00⟩`) and swapped (correct, `-1` on `|11⟩`).
- `heralded_cz_derisking.py` and `tests/test_heralded_cz_derisking.py` (this repo, Phase 10) — established phase-sign verification pattern (`Simulator`/`SLOSBackend`/`prob_amplitude`, reading `in_heralds` not hardcoding, `float()`-casting `StateVector` amplitudes).
- `iqp_photonic_encoding.py` and `tests/test_iqp_photonic_encoding.py` (this repo, Phase 9) — existing weight-1 builder conventions, port convention (`H=(0,1)`, `V=(1,0)`), test style (`Processor("SLOS", circuit)` + `Analyzer`, `np.isclose` assertions, `pytest.mark.parametrize`).
- `docs/iqp-photonic-encoding.md` — on-paper weight-2 derivation (CZ/ZZ operator identity, PBS-mediated conversion mechanism) this phase implements.

### Secondary / Tertiary
None used — every claim in this document was either read directly from the installed package source or confirmed by executing code against it.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new libraries, all already pinned and in use.
- Architecture (Processor.add/add_herald mechanics, mode-mapping dict, PERM restoration): HIGH — read from source, confirmed by execution.
- Pitfalls (especially the dual-rail bit-convention mismatch): HIGH — confirmed by direct execution against this repo's actual venv, not inference.
- Open question 1 (internal-PERM vs. caller-side swap placement): MEDIUM — mechanically equivalent, only one variant actually executed; the other is a straightforward algebraic equivalent but wasn't separately run.

**Research date:** 2026-08-06
**Valid until:** No expiry expected while `requirements.txt` stays pinned to `perceval-quandela==1.2.4` — re-verify the dual-rail convention finding (Pitfall 1) if that pin is ever bumped, since it depends on `HeraldedCzItem`'s internal circuit structure, which is implementation detail, not a documented contract.
