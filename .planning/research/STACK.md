# Stack Research

**Domain:** Photonic quantum computing implementation — weight-2 IQP generator via heralded CZ (Perceval/MerLin)
**Researched:** 2026-08-05
**Confidence:** HIGH (all claims verified by reading installed `perceval-quandela==1.2.4` source directly and by running it against the actual gate instance — not recalled from training data)

## Headline finding (answers the downstream consumer's key question)

The weight-2 construction already derived on paper (PBS → `heralded_cz` → PBS, realizing `exp(iπ/4·Z_i·Z_j)` via `CZ = exp(iπ/4·(I − Z_i − Z_j + Z_i·Z_j))`) needs **no new library** — `perceval.components.core_catalog.heralded_cz.HeraldedCzItem` is a complete, ready-to-instantiate Knill CZ gate already shipped in the installed Perceval version. It is reachable either via `pcvl.catalog['heralded cz']` or the direct import. Verified empirically (source read + live run) that its herald success probability is a uniform **2/27 ≈ 0.074074** across all 4 computational-basis inputs on this exact installed gate instance — this is a measured number for the gate as it ships, not a cited literature figure.

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| perceval-quandela | 1.2.4 (installed, unchanged) | `Circuit`, `Experiment`, `Processor`, catalog gates | Already the project's substrate; `heralded_cz` ships in this exact installed version — verified by reading `venv/Lib/site-packages/perceval/components/core_catalog/heralded_cz.py` directly, not assumed from docs/training data. |
| `perceval.components.core_catalog.HeraldedCzItem` (via `pcvl.catalog['heralded cz']`) | shipped with 1.2.4 | The Knill CZ gate itself: 6-mode circuit, 2 dual-rail qubit ports + 2 herald ancilla modes | This is the literal object the paper design already named (`heralded_cz`, Knill CZ, arXiv:quant-ph/0110144 — confirmed as the `article_ref` in the source file). Reimplementing the beamsplitter angles by hand would forgo Quandela's already-verified construction and its correct convention-adjusted phase placement (see "What NOT to Use"). |
| `pcvl.Processor("SLOS", ...)` + `Processor.probs()` with `compute_physical_logical_perf(True)` | installed | Run the gate, get both the output distribution and the herald/post-selection success rate in one call | `logical_perf` in the returned dict *is* the empirical success probability the milestone wants measured for this specific gate instance — no separate probability-computation code needed. Confirmed by source read of `perceval/runtime/processor.py::probs()` and `perceval/simulators/simulator.py`, and by a live run (see "Verified Behavior" below). |

### Supporting APIs (for integration with `iqp_photonic_encoding.py`)

| API | Purpose | When to Use |
|-----|---------|-------------|
| `Experiment.add_herald(mode, expected, name=None, location=PortLocation.IN_OUT)` | Declares a mode as a herald requiring an exact photon count (0 or 1) on input and/or output | Only needed if hand-building the CZ circuit from `item.build_circuit()` (bare `Circuit`, no ports/heralds). Not needed if using `item.build_experiment()` — heralds are already declared. |
| `Processor.add(mode_mapping, component)` | Composes a sub-`Processor`/`Circuit`/component into a larger `Processor` at a given mode offset | **Verified empirically**: passing a `Processor` built from `item.build_experiment()` as `component` correctly carries its 2 heralds through into the outer processor's herald set (auto-appended past the outer processor's declared mode-of-interest count — e.g. a 6-mode outer processor got heralds re-indexed to modes 6,7). This is the clean composition pattern — see "Integration Pattern" below. |
| `perceval.simulators.Simulator.prob_amplitude(input_state, output_state)` | Returns the complex amplitude (not just `|amplitude|²`) for a specific input→output Fock-state pair | `Processor.probs()` only returns probabilities (phase-blind) — verifying the CZ's signature `-1` phase kickback on `|1,1⟩` (vs. `+1` on `|00⟩,|01⟩,|10⟩`) requires reading the amplitude directly via `Simulator`, built from `expe.unitary_circuit()` (or the merged full circuit), not via `Processor.probs()`. |
| `pcvl.BasicState([...])` | Fock-state input construction | Same object the module already uses; dual-rail qubit state `|0⟩ = [1,0]`, `|1⟩ = [0,1]` per mode pair — matches `HeraldedCzItem`'s port convention (`ctrl` = modes 0,1; `data` = modes 2,3 within its own local numbering). |

## Verified Behavior (`heralded_cz`, read from source + live run against installed 1.2.4)

**Circuit shape** (from `heralded_cz.py`, `HeraldedCzItem.build_experiment`):
- 6 total modes. `build_circuit()` returns a bare `Circuit(6)`; `build_experiment()` wraps it and adds:
  - `Port(Encoding.DUAL_RAIL, 'ctrl')` at mode 0 → occupies modes **0,1**
  - `Port(Encoding.DUAL_RAIL, 'data')` at mode 2 → occupies modes **2,3**
  - `add_herald(4, 1)` and `add_herald(5, 1)` → modes **4,5**, each requiring **exactly 1 photon on both input and output** for the gate to have "worked"
- Confirmed via `HeraldedCzItem().build_experiment()`: `.heralds == {4: 1, 5: 1}`, `.in_heralds == {4: 1, 5: 1}`, `.m == 4` (modes of interest, heralds excluded), `.circuit_size == 6`.

**Success signal (concretely, how to read it):**
- On the *raw* 6-mode circuit (no `Processor`/heralds abstraction), "success" = exactly 1 photon detected on mode 4 AND exactly 1 photon detected on mode 5 in the output Fock state. Any other photon count on those two modes (0, 2, bunched, etc.) is a **failure** branch — the gate did not implement CZ on that shot/term.
- Using `Processor` (recommended — do this, not manual post-selection): declaring the heralds via `add_herald`/`build_experiment()` and calling `.probs()` **automatically discards the failure branches** from the returned `results` distribution (`keep_heralds(False)` is set internally) and reports the aggregate success weight in `global_perf`/`logical_perf`. You never have to manually filter mode-4/mode-5 photon counts yourself.
- `physical_perf` vs `logical_perf`: for a noiseless (perfect-source) simulation as used here, `physical_perf = 1.0` always; `logical_perf` is the actual herald/post-selection acceptance probability — this is the number to report as "the empirically measured success probability for this gate instance."

**Measured success probability** (live run, `Processor.probs()` with `compute_physical_logical_perf(True)`, all 4 computational-basis dual-rail inputs):

| ctrl,data input | output (prob 1 conditioned on success) | `logical_perf` |
|---|---|---|
| \|0⟩\|0⟩ → `[1,0,1,0]` | `[1,0,1,0]` | 0.07407407... |
| \|0⟩\|1⟩ → `[1,0,0,1]` | `[1,0,0,1]` | 0.07407407... |
| \|1⟩\|0⟩ → `[0,1,1,0]` | `[0,1,1,0]` | 0.07407407... |
| \|1⟩\|1⟩ → `[0,1,0,1]` | `[0,1,0,1]` | 0.07407407... |

**= 2/27 ≈ 0.074074, uniform across all 4 inputs.** This is the milestone's own measured number, not a cited figure — worth stating explicitly in the eventual write-up as "measured for this installed gate instance," since the general Knill-CZ family has multiple published variants (1/9, 2/27, etc. depending on ancilla count and specific beamsplitter angles) and citing a literature number without running it would violate this milestone's stated scope ("not just cite literature figures").

**Phase behavior**: `Processor.probs()` cannot show the `-1` phase on `|1,1⟩` because probabilities are phase-blind (each output state above has probability 1, both for the identity-passing inputs and for `|1,1⟩`). To confirm the CZ sign, use `Simulator.prob_amplitude()` on the *un-heralded* full circuit and manually restrict to the terms where modes 4,5 both carry exactly 1 photon — e.g. compare `prob_amplitude(BasicState([0,1,0,1,1,1]), BasicState([0,1,0,1,1,1]))` (the `|1,1⟩` + herald-photon input/output term) against `prob_amplitude` for `|0,1,1,0,1,1⟩` etc., and check the relative sign flips between the `|1,1⟩` term and the three others. This has not yet been run — flagged as the next concrete implementation step, not a research gap.

## Integration Pattern (for `iqp_photonic_encoding.py`)

The existing module encodes each qubit as one polarization mode + one vacuum-partner mode (2 modes/qubit), converting polarization ↔ dual-rail only at final readout via `build_readout_circuit`'s per-qubit `PBS()`. The weight-2 construction requires the **same PBS conversion done mid-circuit**, only on the two qubits participating in the `Z_i·Z_j` term, sandwiching the `heralded_cz` sub-circuit:

1. `PBS()` on qubit `i`'s polarization mode and qubit `j`'s polarization mode — same primitive `build_readout_circuit` already uses, just applied to 2 qubits instead of all `n`, and mid-pipeline instead of at the end. This converts each qubit's single polarization mode into a genuine 2-mode dual-rail pair, matching `heralded_cz`'s `ctrl`/`data` port convention.
2. Compose `pcvl.Processor("SLOS", pcvl.catalog['heralded cz'].build_experiment())` into the larger multi-qubit processor via `.add(mode_mapping, sub_proc)` at the mode offset where qubit `i`'s and `j`'s (now-dual-rail) 4 modes live. **Verified empirically**: this correctly propagates the 2 new herald modes into the outer processor's herald set (they get appended after the outer processor's existing modes-of-interest, not overwritten) — no manual `add_herald` bookkeeping required on the outer processor.
3. `PBS()` again (PBS is its own inverse for this purpose — same component, applied a second time) to convert the two qubits back from dual-rail to single polarization mode, so any subsequent weight-1 diagonal-layer gates or the final conjugation/readout stage can continue operating in the module's existing 2-modes/qubit polarization convention.
4. The 2 herald ancilla modes are new modes at the *end* of the full circuit's mode numbering (not interleaved) — plan the full-circuit mode budget as `2n` (existing per-qubit polarization+vacuum layout) `+ 2` per weight-2 term applied (each `heralded_cz` insertion adds exactly 2 new herald modes).

This composition (`Processor.add()` with a sub-`Processor`) is the correct level to work at — do not try to manually merge `heralded_cz`'s bare `Circuit(6)` into a hand-built bigger `Circuit` and then bolt heralds on separately; `build_experiment()` + `Processor.add()` keeps port/herald metadata attached and was the path actually verified to work.

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|--------------|
| `CatalogItem.build_processor()` | **Deprecated** as of Perceval 1.2.0 (confirmed: `@deprecated(reason="Use build_experiment instead", version="1.2.0")` decorator directly on the method in `component_catalog.py`) — will emit a deprecation warning and may be removed in a future release. | `item.build_experiment()` wrapped in `pcvl.Processor(backend, experiment)` — functionally identical, not deprecated. |
| Hand-deriving/re-decomposing the Knill CZ's beamsplitter network from the arXiv:quant-ph/0110144 paper | `HeraldedCzItem` already implements this exact reference (confirmed `article_ref` field) with correctly convention-adjusted phase placement — the source file's own comment notes a deliberate deviation from the paper's phase-shifter placement (mode 3 vs mode 1) "due to a different convention for the beamsplitters." Reimplementing risks silently reintroducing a sign/convention bug that Quandela already resolved. | `pcvl.catalog['heralded cz']` as-is. |
| `perceval.components.core_catalog.PostProcessedCzItem` (also present in the catalog, confirmed in `core_catalog/__init__.py`) | This is a *different* gate family — post-selection on the computational-subspace output pattern itself (no ancilla herald modes, no independent success/failure signal to measure), not the ancilla-heralded Knill construction the paper design already committed to. Swapping to it mid-implementation would silently change what's being measured and contradict the already-derived operator identity in the docs. | Stay with `HeraldedCzItem` — it's the gate the paper design already named. |
| Feeding a *parameterized* angle into `heralded_cz` expecting a continuously-tunable `Z_i·Z_j` phase | `HeraldedCzItem.build_circuit(**kwargs)` **ignores all kwargs** — `theta1`/`theta2` are hardcoded class constants (`math.acos(...)`), confirmed by reading the source; there is no angle parameter exposed. | This matches the paper design's own stated limitation (fixed π/4 angle only, via the operator identity, with any other Z-phase correction applied separately through the already-implemented `WP(theta,0)` weight-1 gate). Don't spend implementation time looking for a parameterized variant — none exists in this catalog item. |

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|------------------|-------|
| perceval-quandela==1.2.4 | Python 3.10–3.14 (repo venv 3.12) | No change from v2.0 milestone research — same installed version covers this milestone's needs; `heralded_cz` is not a new-in-1.2.4 addition requiring a bump, just previously unused. |
| `pcvl.catalog['heralded cz']` | Same package, no separate install | Confirmed live: `pcvl.catalog` is a `Catalog` instance populated at import time from `core_catalog.catalog_items`; `'heralded cz' in pcvl.catalog` returns `True` with no extra setup. |

## Sources

- `venv/Lib/site-packages/perceval/components/core_catalog/heralded_cz.py` — HIGH confidence, read directly (ground truth for circuit construction, herald modes, fixed angles).
- `venv/Lib/site-packages/perceval/components/core_catalog/__init__.py` — HIGH confidence, confirms `HeraldedCzItem` and `PostProcessedCzItem` are separate catalog entries.
- `venv/Lib/site-packages/perceval/components/component_catalog.py` — HIGH confidence, confirms `build_processor()` deprecation and `CatalogItem` interface.
- `venv/Lib/site-packages/perceval/components/port.py` — HIGH confidence, confirms `Port`/`Herald`/`Encoding.DUAL_RAIL` semantics.
- `venv/Lib/site-packages/perceval/components/experiment.py` — HIGH confidence, confirms `add_herald()` signature and `m`/`m_in`/`circuit_size` semantics.
- `venv/Lib/site-packages/perceval/runtime/processor.py` and `runtime/abstract_processor.py` — HIGH confidence, confirms `Processor.add()`, `Processor.probs()`, `compute_physical_logical_perf()`.
- `venv/Lib/site-packages/perceval/simulators/simulator.py` and `simulator_interface.py` — HIGH confidence, confirms `logical_perf`/`physical_perf` semantics (post-selection performance vs. photon-detection-filter performance) and `prob_amplitude()`.
- Live execution against installed `perceval-quandela==1.2.4` in `./venv` — HIGH confidence, ground truth: measured 2/27 ≈ 0.074074 success probability, confirmed `Processor.add()` correctly propagates sub-processor heralds into a composed outer processor.
- Existing project module `iqp_photonic_encoding.py` — HIGH confidence, read directly to determine integration surface (polarization/dual-rail conventions, existing PBS usage pattern).

---
*Stack research for: weight-2 IQP generator implementation via Perceval's `heralded_cz`*
*Researched: 2026-08-05*
