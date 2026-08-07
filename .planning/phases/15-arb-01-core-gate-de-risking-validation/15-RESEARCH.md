# Phase 15: ARB-01 Core Gate De-Risking & Validation - Research

**Researched:** 2026-08-07
**Domain:** Perceval linear-optical gate catalog (`PostProcessedControlledRotationsItem`), operator-identity derivation, TVD validation against this repo's existing exact qubit-side reference
**Confidence:** HIGH for API behavior and reference-infrastructure facts (all verified by direct execution against this repo's installed `venv`, `perceval-quandela==1.2.4`); MEDIUM for the general operator identity's algebra (verified as a 4×4 matrix identity, not yet verified end-to-end through the actual wired circuit); LOW/flagged-open for the exact circuit wiring needed to pass TVD, and for one apparent contradiction in `15-CONTEXT.md`'s stated boundary value.

## Summary

`PostProcessedControlledRotationsItem` (catalog key `"postprocessed controlled gate"`, from `perceval.components.core_catalog.controlled_rotation_gates`, referencing arXiv:2405.01395) is confirmed by direct execution to implement exactly `CP(α) = diag(1,1,1,e^{iα})` on two dual-rail qubits, as a post-selected (not heralded) gate: `alpha` is a literal Python `float` kwarg passed to `build_circuit(n=2, alpha=...)`/`build_experiment(n=2, alpha=...)`, `n` is "number of qubits of the gate" (n=2 for a 2-qubit gate — confirmed, not "number of control qubits"), and the circuit uses `4n=8` total modes for n=2: 4 data modes (2 dual-rail qubits) + 4 ancilla modes, all held at vacuum (`add_herald(i, 0)` for i in 4..7) — a structurally different resource cost and success mechanism than `heralded_cz`'s 6 modes (4 data + 2 heralded-photon ancilla). This was confirmed via `Simulator.prob_amplitude` directly on the bare 8-mode circuit across 8 different α values spanning `(0, π]`, including the CONTEXT.md-mandated non-trivial set.

The single most important finding for planning: **the exact qubit-side reference (`exact_qubit_iqp_distribution`) is already parameterized by angle** via its existing `pair_thetas={(i,j): theta}` argument (added in Phase 12, confirmed by reading the source directly — `total_phase += th * za * zb` for arbitrary `th`, no hardcoding to π/4 anywhere in that function). **No "generalize the reference" task is needed in Phase 15's plan** — this closes the key research question the roadmap posed. The photonic-*side* weight-2 builder (`photonic_weight2_iqp_distribution`/`build_weight2_processor`), by contrast, *is* hardcoded to the `+π/4` fold and cannot be reused as-is; Phase 15 needs a new, CP-specific photonic-side builder analogous to it, not a generalization of the existing one.

Second critical finding, an open contradiction that must be resolved before locking task-level plan details: this research's own algebraic derivation (confirmed both symbolically and against the "boundary reduces to heralded_cz" claim) shows the value of CP's raw `alpha` dial that reproduces `heralded_cz`'s `CZ = diag(1,1,1,-1)` exactly is **`alpha=π`**, not `alpha=π/4` as `15-CONTEXT.md` states. `alpha=π/4` on CP's own dial does **not** match `heralded_cz` (confirmed by direct computation: phase pattern is `diag(1,1,1, e^{iπ/4})`, not `diag(1,1,1,-1)`). The general identity is `exp(iφ·Z_iZ_j) = CP(4φ)·WP(φ,0)_i·WP(φ,0)_j` (up to global phase `e^{iφ}`) — at the existing document's `φ=θ=π/4` (the `Z_iZ_j` generator's own angle, matching `exact_qubit_iqp_distribution`'s `pair_thetas` convention and the existing test suite's own `pair_thetas={(0,1): np.pi/4}` usage), this correctly gives `CP(4·π/4)=CP(π)=CZ`. `15-CONTEXT.md`'s phrase "α=π/4" appears to conflate CP's own dial parameter (called `α` by the roadmap/ARB-02) with the `Z_iZ_j` generator's own angle (called `θ` by the same roadmap text) — these are different variables related by `α=4θ`. This is flagged as the top open question for planning (see Open Questions).

Third finding, a real unresolved risk: an end-to-end circuit-level integration attempt in this research spike (PBS-wrap → CP-insertion → PBS-unwrap, wired into the existing `build_state_prep_circuit`/`build_diagonal_layer_circuit`/`build_conjugation_circuit`/`build_readout_circuit` pipeline, mirroring `build_weight2_processor`'s exact structure) did **not** reproduce the exact reference — TVD ~0.3-0.4 against target ≤1e-6, even after trying the same ctrl/data `PERM([1,0])` adapter fix that `_build_cz_insertion_core` needed for `heralded_cz`. The bare-circuit phase/amplitude behavior (Finding 1) is solid; the mode-wiring needed to compose it correctly with PBS-wrap/state-prep/conjugation/readout is not yet found. Phase 15's plan should budget a dedicated wiring/debugging task for this — treat it with the same seriousness Phase 11 gave `heralded_cz`'s ctrl/data convention bug, not as a trivial copy-paste of `build_cz_insertion`.

**Primary recommendation:** Scope Phase 15's plan around three facts now confirmed HIGH-confidence (gate identity, reference parameterization, success-probability-varies-with-α), one open disambiguation the owner must resolve before finalizing which literal value goes in the "boundary sanity check" test (α=π vs α=π/4 — see Open Questions), and one real implementation-risk task (circuit wiring to hit TVD≤1e-6) that needs explicit budget, not an assumption of easy reuse.

## Standard Stack

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `perceval-quandela` | 1.2.4 (already installed in repo's `venv`) | `PostProcessedControlledRotationsItem` catalog gate, `Simulator`, `SLOSBackend`, `Processor`, `Analyzer` | Same library/version this project's entire IQP-photonic encoding stack already depends on; no new dependency needed |
| `numpy` | already installed | `exact_qubit_iqp_distribution`'s exact state-vector reference (already parameterized, reused as-is) | Existing infrastructure |

### Supporting
No new libraries needed. This phase is validation/derivation work on top of already-installed `perceval-quandela==1.2.4` and this repo's own `iqp_photonic_encoding.py`.

### Alternatives Considered
Not applicable — the gate to validate is fixed by the roadmap (`PostProcessedControlledRotationsItem`), not chosen from alternatives.

## Architecture Patterns

### `PostProcessedControlledRotationsItem` API (verified against installed source, `venv/Lib/site-packages/perceval/components/core_catalog/controlled_rotation_gates.py`)

```python
from perceval.components.core_catalog.controlled_rotation_gates import PostProcessedControlledRotationsItem

item = PostProcessedControlledRotationsItem()
circuit = item.build_circuit(n=2, alpha=some_float)   # bare Circuit(8) for n=2 -- 4 data + 4 ancilla modes
exp = item.build_experiment(n=2, alpha=some_float)     # Experiment wrapping build_circuit + ports + heralds + postselect
```

Key facts, all confirmed by direct execution:
- `n` = "number of qubits of the gate" (not "number of controls") — for a 2-qubit `CP(α)` gate, pass `n=2`. `n < 2` raises `ValueError`.
- `alpha` must be a plain Python `float` (`isinstance(n, int)`/`isinstance(alpha, float)` are enforced — passing a bare `int` or `numpy.float64` raises `TypeError`; this repo already has a documented `numpy.float64`-breaks-Perceval gotcha (STATE.md) — cast explicitly).
- Circuit size is `4n` modes. For `n=2`: modes 0-1 = qubit-0 dual rail ("ctrl0" port), modes 2-3 = qubit-1 dual rail ("data" port — the class names the last qubit "data", the rest "ctrl{i}"), modes 4-7 = ancilla, all held at vacuum.
- `build_experiment()` (NOT `build_circuit()`, same pattern as `heralded_cz` — `build_circuit()` alone drops all herald/port/postselect metadata) attaches:
  - `e.add_herald(i, 0)` for `i` in 4..7 (**vacuum** ancilla, both ends — unlike `heralded_cz`'s `add_herald(4,1)`/`add_herald(5,1)`, which requires a **real photon** input/output on each herald mode).
  - `e.set_postselection(PostSelect('[0,1]==1 & [2,3]==1'))` — an *additional*, separate condition requiring each qubit's own dual-rail pair to carry exactly 1 photon (data validity). This is the "post-selection" half of "post-selection + ancilla vacuum" that `15-CONTEXT.md` already correctly names as the distinguishing mechanism vs. `heralded_cz`'s pure ancilla-heralding.
  - Ports registered via `Port(Encoding.DUAL_RAIL, ...)` — **the same `Encoding.DUAL_RAIL` standard `heralded_cz` uses**, which this repo's own `docs`/code already documents as the *mirror image* of this module's PBS-derived H/V convention (Plan 09-02/11-01's `_build_cz_insertion_core` `PERM([1,0])` adapter fix). Expect the same class of convention mismatch to need resolving for CP — confirmed necessary in principle (see Common Pitfalls), though this research's spike did not find the exact fix (see below).

### Confirmed gate identity (HIGH confidence — Simulator.prob_amplitude on the bare circuit, ancilla vacuum in and out)

```python
import perceval as pcvl, math
from perceval.components.core_catalog.controlled_rotation_gates import PostProcessedControlledRotationsItem
from perceval.simulators import Simulator
from perceval.backends import SLOSBackend

item = PostProcessedControlledRotationsItem()
alpha = math.pi / 3
circuit = item.build_circuit(n=2, alpha=alpha)   # 8 modes
sim = Simulator(SLOSBackend()); sim.set_circuit(circuit)

DUAL_RAIL = {'0': (1, 0), '1': (0, 1)}   # Perceval's own Encoding.DUAL_RAIL convention (mirror of this repo's own PBS convention)
ancilla = [0, 0, 0, 0]                    # vacuum, both ends

for c in '01':
    for d in '01':
        cm, dm = DUAL_RAIL[c], DUAL_RAIL[d]
        state = pcvl.BasicState(list(cm) + list(dm) + ancilla)
        amp = sim.prob_amplitude(state, state)
        # amp == (raw scale) for (c,d) != ('1','1'); amp == (raw scale)*exp(1j*alpha) for ('1','1')
```

Measured raw (unnormalized/pre-postselection) amplitude table, `n=2`, all four computational-basis inputs (uniform magnitude for a given α — the gate is a genuine phase gate, no population distortion):

| α | \|amp\|² (= raw post-selection success prob per basis state) | phase(amp₁₁)/phase(amp₀₀) |
|---|---|---|
| π/6 | 0.174539 | matches `e^{iα}` |
| π/4 | 0.133447 | matches `e^{iα}` |
| 0.9 | 0.122133 | matches `e^{iα}` |
| π/3 | 0.111111 (= 1/9) | matches `e^{iα}` |
| 2π/5 | 0.100142 | matches `e^{iα}` |
| π/2 | 0.090485 | matches `e^{iα}` |
| 3.0 | 0.104397 | matches `e^{iα}` |
| **π** | **0.111111 (= 1/9 exactly)** | **exactly -1 (matches CZ)** |

All phase ratios matched `e^{iα}` to floating-point precision (`~1e-16` residual) at every α tested — this is the strongest, most directly reusable confirmation for ARB-01 (criterion 1: "gate phase/structure confirmed at ≥3 non-trivial α values"). **α=π gives exactly the literature's cited "1/9 for a post-selected construction" figure** (already cited, unverified-for-this-exact-gate, in `docs/iqp-photonic-encoding.md`'s ENC-01 section) — this is a second, independent confirmation of that figure, now tied to a specific, executable gate.

**Success probability is not constant in α** (unlike `heralded_cz`'s fixed 2/27) — it must be reported as an explicit table/curve, exactly as ARB-04 already requires. No closed form was derived in this research pass (deliberately — the owner's derivation task, per `15-CONTEXT.md`'s attempt-first gating on the general identity; the raw ingredients for the derivation are in `build_control_gate_unitary`'s source: `a = (e^{iα}-1)^{1/n}`, `A0 = I + a·J` for a cyclic-shift `J`, embedded into a full unitary via `Matrix.get_unitary_extension`).

### General operator identity (algebra verified independently of the circuit — MEDIUM confidence, not yet confirmed through the actual wired circuit)

Writing `CP(α) = diag(1,1,1,e^{iα})` and `WP(θ,0) = exp(iθZ)` (already established, `docs/iqp-photonic-encoding.md` Ingredient 2), direct 4×4 matrix multiplication (basis order `00,01,10,11`) confirms:

```
CP(4φ) · WP(φ,0)_i · WP(φ,0)_j = e^{iφ} · exp(iφ·Z_i·Z_j)
```

This exactly generalizes the existing document's fixed-case identity (`exp(iπ/4·Z_iZ_j) = CZ · exp(iπ/4·Z_i) · exp(iπ/4·Z_j)`, up to global phase) — substituting `φ=π/4` gives `CP(π) = CZ`, matching the existing derivation exactly. **This is the natural candidate for ARB-02's general-α identity** — but per `15-CONTEXT.md`'s attempt-first gating, the owner should attempt this derivation themselves before it's written into `docs/iqp-photonic-encoding.md`; this research only confirms the algebra checks out as a sanity backstop, not as the delivered derivation.

### `exact_qubit_iqp_distribution` — already parameterized (HIGH confidence, resolves the roadmap's key research question)

```python
def exact_qubit_iqp_distribution(n, thetas, pair_thetas=None):
    ...
    for (a, b), th in pair_thetas.items():          # pair_thetas: {(i,j): theta_ij}, NOT hardcoded to pi/4
        za = 1 if bit_a == 0 else -1
        zb = 1 if bit_b == 0 else -1
        total_phase += th * za * zb
    ...
```

Confirmed by reading `iqp_photonic_encoding.py` directly (lines 544-599): `pair_thetas` accepts **any** `θ_ij` float, added Phase 12 (WT2-02) specifically so the reference generalizes beyond the fixed π/4 case, and the existing test suite already exercises it at non-default values (`test_exact_qubit_distribution_weight2_extension_sums_to_one`). **Reuse directly, unmodified, for Phase 15** — pass `pair_thetas={(i,j): θ}` for whatever `θ` the plan's 3 non-trivial α values correspond to (via `θ = α/4`, per the identity above, pending the disambiguation below). No generalization task needed.

What is *not* reusable as-is: `photonic_weight2_iqp_distribution`/`build_weight2_processor`/`_build_weight2_processor_no_herald` are all hardcoded to the `+π/4` fold (confirmed: `thetas_folded[i] += np.pi / 4` is a literal constant, not a parameter, in all three functions) and structurally wired to `heralded_cz`'s 6-mode/2-ancilla layout. Phase 15 needs new, CP-specific analogues of these three functions (a `_build_cp_insertion`-style circuit builder generalizing `build_cz_insertion`, and a `photonic_cp_iqp_distribution`-style measurement function generalizing `photonic_weight2_iqp_distribution`, parameterized by `α` or `φ` instead of hardcoded to `π/4`), not a straight reuse or a one-line generalization of the existing weight-2 functions.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|--------------|-----|
| Exact qubit-side reference distribution at arbitrary weight-2 angle | A new reference implementation | `exact_qubit_iqp_distribution(n, thetas, pair_thetas={(i,j): θ})` | Already generalized (Phase 12), already tested, already the project's canonical reference — confirmed not hardcoded to π/4 |
| TVD metric | A new distance function | `total_variation_distance` (already in `iqp_photonic_encoding.py`) | Same metric, same threshold convention (`<1e-6`) the weight-2 work already established |
| Bitstring decode / out-of-subspace handling | New decode logic for the CP-based circuit's output | `fock_to_bitstring(state, n)` (existing, ENC-03) | Works on any 2n-mode readout `BasicState` regardless of which gate produced it upstream — pure decode logic, gate-agnostic |
| Manual herald/postselect filtering | Reliance on `Processor.add_herald()`/`set_postselection()` for the ancilla/data-validity conditions | The same manual-filtering pattern `_build_weight2_processor_no_herald`/`photonic_weight2_iqp_distribution` already established (herald-free processor variant, filter ancilla and data validity by hand in Python after `.probs()`/`Analyzer.compute()`) | This research confirmed the same class of Perceval limitation applies to CP's postselection (see Common Pitfalls) — the existing workaround pattern is directly reusable |

**Key insight:** almost everything on the *reference* and *measurement-metric* side of this phase already exists and generalizes cleanly; the actual new work is narrowly scoped to (a) a new CP-specific circuit-wiring function (data-mode PBS-wrap/unwrap around `PostProcessedControlledRotationsItem`, ctrl/data convention-adapted) and (b) a new CP-specific manual-filtering measurement function mirroring `photonic_weight2_iqp_distribution`'s structure. Do not let the plan re-derive the reference or the metric.

## Common Pitfalls

### Pitfall 1: `alpha` must be a plain Python `float`, not `numpy.float64` or `int`
**What goes wrong:** `PostProcessedControlledRotationsItem.build_circuit(n=2, alpha=...)` raises `TypeError` if `alpha` is anything but `float` (explicit `isinstance` check in the source), and `n` must be a plain `int`.
**Why it happens:** Same class of issue as this repo's already-documented `numpy.float64`-breaks-`StateVector`-arithmetic gotcha (STATE.md) — this is a second, independent place the same discipline (cast explicitly before calling into Perceval) is needed.
**How to avoid:** `alpha=float(alpha_value)` at every call site, especially inside any sweep/parametrize loop using `np.linspace` or similar (which yields `numpy.float64`).
**Warning signs:** `TypeError: alpha must be of type float.`

### Pitfall 2: `Encoding.DUAL_RAIL` ctrl/data convention likely needs the same `PERM([1,0])` adapter `heralded_cz` needed — but the exact fix wasn't found in this research pass
**What goes wrong:** `PostProcessedControlledRotationsItem.build_experiment()` registers ports via Perceval's own `Encoding.DUAL_RAIL` standard, same as `heralded_cz` — the same standard this repo's `_build_cz_insertion_core` already documented as the *mirror image* of this module's own PBS-derived H/V convention (`Port(Encoding.DUAL_RAIL,...)`: logical `1` → Fock pattern `(0,1)`, vs. this module's own convention, logical `H`/'0' → `(0,1)`).
**Why it happens:** Two independently-motivated conventions (a physics-driven polarization convention vs. an abstract dual-rail-qubit standard) that were never chosen to agree.
**How to avoid:** Expect to need a `PERM([1,0])` adapter analogous to `_build_cz_insertion_core`'s, immediately before/after the CP gate on one or both qubit's dual-rail pair. **This research tried all four combinations (no swap, swap ctrl only, swap data only, swap both) in a full end-to-end pipeline test and none reproduced the exact reference (best TVD ~0.30, target ≤1e-6)** — the fix is not simply "copy `_build_cz_insertion_core`'s adapter." Budget real debugging time here; do not assume this is a trivial adaptation. Candidate next debugging steps for the plan (not resolved here): verify the physical mode-index-to-(qubit,rail) mapping `build_control_gate_unitary`'s internal permutation (`final_modes = [2*i for i in range(n)] + [2*i+1 for i in range(n)] + [i for i in range(2*n,4*n)]`) actually produces before assuming it groups as `(qubit0-rail0, qubit0-rail1, qubit1-rail0, qubit1-rail1, ancilla...)`; isolate the bare-circuit (no PBS, no state-prep) dual-rail-in/dual-rail-out truth table directly against `Encoding.DUAL_RAIL`'s own logical convention, the same way `heralded_cz_derisking.py` did, before wiring in the rest of the pipeline.
**Warning signs:** TVD several orders of magnitude above threshold with the joint distribution's *shape* visibly wrong (probability mass on the wrong bitstrings, not just off by a small numerical error) — this is a wiring/convention bug, not a precision issue.

### Pitfall 3: `Processor.set_postselection()` cannot be registered before later components touch the same modes
**What goes wrong:** Calling `proc.set_postselection(...)` (or wiring an `Experiment`'s existing `post_select_fn`) on the CP gate's data-validity condition, then adding further components (e.g. conjugation, readout) that touch the same mode indices, raises: `AssertionError: Post-selection conditions cannot compose with modes [...]` from `Experiment._validate_postselect_composition`. Confirmed by direct execution in this research pass — this is a **new** pitfall, distinct from and in addition to the already-documented `add_herald()`+`PBS` crash (STATE.md/12-RESEARCH.md Pitfall 3).
**Why it happens:** Perceval's `Experiment` validates that postselection conditions describe the *final* measured state; components added afterward that could still change photon distribution on those modes invalidate that assumption from Perceval's point of view, even when (as here) the later components are photon-number-preserving per mode-pair.
**How to avoid:** Do not call `Processor.set_postselection()`/`Processor.add_herald()` mid-pipeline for CP's own conditions. Use the same manual/deferred approach already established for `heralded_cz`+PBS (`_build_weight2_processor_no_herald`'s pattern): build the full pipeline with no herald/postselect registered at all, run `Analyzer`/`.probs()` unconditionally, then filter by hand in Python — checking ancilla vacuum (`state[ancilla_idx] == 0` for all 4 ancilla modes) and data validity (via the existing `fock_to_bitstring`, which already returns `None` for invalid/bunched patterns) as two separate conditions, exactly mirroring `photonic_weight2_iqp_distribution`'s existing accounting (`dist`, `residual`, and a `*_failure_prob`-style third number, kept separate per this project's established reporting convention).
**Warning signs:** `AssertionError: Post-selection conditions cannot compose with modes [...]` at circuit-assembly time, not at `.probs()` time — this fails fast and unambiguously, easy to detect early in a plan verification step.

### Pitfall 4: `Processor.add_herald()` + `PBS`-containing circuit does NOT reliably crash for CP's *vacuum* heralds (tentative, narrower-scope favorable finding vs. the existing `heralded_cz` gotcha)
**What goes wrong (or rather, doesn't):** The already-documented gotcha ("`Processor.add_herald()` combined with any `PBS`-containing circuit crashes `Processor.probs()` unconditionally," STATE.md, filed upstream as Quandela/Perceval#783) was diagnosed specifically for `heralded_cz`'s **photon-count** heralds (`add_herald(4,1)`/`add_herald(5,1)`, requiring `{P:V}`-annotated ancilla input). A standalone test in this research pass — `Processor.add_herald(i, 0)` for CP's **vacuum** heralds, on a PBS-wrapped circuit, single computational-basis `BasicState` input, `Processor.probs()` — did **not** crash.
**Why this matters, and why it's still flagged as a pitfall rather than a green light:** This was only tested in isolation (standalone 8-mode circuit, no state-prep/conjugation/readout composed around it), and Pitfall 3 above shows the *postselection* half of CP's condition set (not the herald half) crashes once more components are composed. Given Pitfall 3 already forces the manual-filtering workaround regardless, this finding doesn't change the recommended approach (still: don't use built-in `add_herald`/`set_postselection` for CP's own conditions, filter manually) — it's noted so the plan doesn't waste time assuming Pitfall 3's crash mode extends to the herald half too, if a future debugging step needs to isolate which half of CP's condition set is responsible for a given failure.
**How to avoid:** N/A — informational; the manual-filtering path (Pitfall 3's resolution) sidesteps this either way.

### Pitfall 5 (already known, restated for this gate family): StateVector-based superposition inputs need care
**What goes wrong:** A hand-built `pcvl.StateVector` combining polarization-annotated (`{P:H}`/`{P:V}`) and bare-integer (`0`) mode entries raises `NotImplementedError: Polarization simulator can only process AnnotatedFockState inputs` once the circuit contains a `PBS` (forcing `PolarizationSimulator` dispatch).
**Why it happens:** Same root cause as this repo's existing "always explicitly annotate ancilla polarization" STATE.md gotcha — inconsistent annotation across mode indices in a single `BasicState`/`StateVector` breaks `PolarizationSimulator`'s input dispatch.
**How to avoid:** This is moot for the actual weight-2 validation pipeline: like the existing `heralded_cz`-based pipeline, superposition should be created *inside* the circuit (via `build_state_prep_circuit`'s `HWP` gates) starting from a definite computational-basis input (`all_h_input(n)`-style), never via a hand-built `StateVector`. If a plan step does need a raw `StateVector` input for a standalone spot-check (mirroring `heralded_cz_derisking.py`'s superposition spot-checks), build the *entire* `BasicState` string in one annotated pass (e.g. `"|" + ",".join(["{P:H},0"]*n) + "," + ",".join(["0"]*4) + ">"`), not via `list(existing_basic_state) + [0,0,0,0]` (which silently strips annotations — confirmed to cause exactly this crash in this research pass).
**Warning signs:** `NotImplementedError: Polarization simulator can only process AnnotatedFockState inputs`.

## Code Examples

### Confirming the gate identity at a candidate α value (ARB-01, criterion 1 — directly reusable as a test skeleton)
```python
# Source: this research pass, verified against perceval-quandela==1.2.4
import perceval as pcvl, math
from perceval.components.core_catalog.controlled_rotation_gates import PostProcessedControlledRotationsItem
from perceval.simulators import Simulator
from perceval.backends import SLOSBackend

item = PostProcessedControlledRotationsItem()
DUAL_RAIL = {'0': (1, 0), '1': (0, 1)}  # Perceval's own Encoding.DUAL_RAIL convention

def measure_cp_amplitudes(alpha: float, n: int = 2):
    circuit = item.build_circuit(n=n, alpha=float(alpha))
    sim = Simulator(SLOSBackend()); sim.set_circuit(circuit)
    ancilla = [0] * (2 * n)
    amps = {}
    for c in '01':
        for d in '01':
            cm, dm = DUAL_RAIL[c], DUAL_RAIL[d]
            state = pcvl.BasicState(list(cm) + list(dm) + ancilla)
            amps[(c, d)] = sim.prob_amplitude(state, state)
    return amps
```

### Reusing the exact reference at arbitrary angle (ARB-03 — no changes needed to `exact_qubit_iqp_distribution`)
```python
# Source: iqp_photonic_encoding.py, already-shipped code (Phase 12)
from iqp_photonic_encoding import exact_qubit_iqp_distribution

theta = alpha / 4  # per the general identity: CP(alpha) <-> exp(i*(alpha/4)*Z_i*Z_j)
exact = exact_qubit_iqp_distribution(n=2, thetas=[0.3, 1.1], pair_thetas={(0, 1): theta})
```

## State of the Art

| Old Approach (v2.1, Phases 10-13) | New Approach (Phase 15, ARB-01) | When Changed | Impact |
|---|---|---|---|
| `heralded_cz`: fixed `CZ = diag(1,1,1,-1)`, heralded (ancilla photon in/out), success 2/27, 6 modes | `PostProcessedControlledRotationsItem`: tunable `CP(α) = diag(1,1,1,e^{iα})`, post-selected (ancilla vacuum in/out + data postselect), success varies with α (=1/9 at α=π), 8 modes (n=2) | Phase 15 | Unlocks continuously-tunable weight-2 IQP generators, not just the fixed π/4 angle — this is ARB-01's whole point, already framed correctly by the roadmap |

**Not deprecated:** `heralded_cz`/`build_cz_insertion`/`build_weight2_processor` remain the validated, shipped fixed-angle construction — Phase 15 adds a second, parallel gate family (per `15-CONTEXT.md`'s locked decision: comparison table only, no "which to prefer" recommendation, no replacement).

## Open Questions

1. **α vs θ: which variable does `15-CONTEXT.md`'s "α=π/4 boundary" refer to? (Highest priority — blocks locking the boundary-agreement test's literal parameter value)**
   - What we know: `CP`'s own raw `alpha` dial (the literal kwarg to `PostProcessedControlledRotationsItem.build_circuit`) at `alpha=π` reproduces `heralded_cz`'s `CZ` phase pattern exactly (confirmed, HIGH confidence). At `alpha=π/4`, it does not (confirmed — phase is `e^{iπ/4}` on `|11⟩`, not `-1`). The existing codebase's own established convention (`exact_qubit_iqp_distribution`'s `pair_thetas`, the existing test suite's `pair_thetas={(0,1): np.pi/4}`) already uses `θ=π/4` to mean the `Z_iZ_j` generator's own angle — and `θ=π/4` maps to `CP`'s dial via `α=4θ=π`, matching the alpha=π finding.
   - What's unclear: whether `15-CONTEXT.md`'s "α=π/4" was written using the roadmap's `α`-for-CP's-dial convention (in which case the stated boundary check plan needs correcting to `α=π`) or was using `α` loosely to mean the `θ` the existing docs/tests already call the `Z_iZ_j` angle (in which case the literal test should pass `alpha=π` to `PostProcessedControlledRotationsItem` while still describing it in prose as "the π/4 angle," matching the existing document's own framing).
   - Recommendation: resolve explicitly during planning (or via a quick owner check-in before locking task details) — this determines the literal `alpha=` value passed into the CP-vs-heralded_cz boundary-agreement test (ARB-05's "direct boundary-agreement test") and needs a one-line clarifying note in the plan so the distinction between `α` (CP dial) and `θ` (Z_iZ_j generator angle) is stated unambiguously in both the plan and the eventual `docs/iqp-photonic-encoding.md` writeup.

2. **Exact circuit wiring to pass TVD ≤1e-6 for the CP-insertion**
   - What we know: the bare-gate phase/amplitude behavior is exactly right (Finding 1, HIGH confidence). The general operator identity is algebraically correct as a 4×4 matrix identity (MEDIUM confidence). A full end-to-end wiring attempt (PBS-wrap + CP + PBS-unwrap, composed with state-prep/diagonal-fold/conjugation/readout, mirroring `build_weight2_processor`'s structure) did not match the exact reference in this research pass, across 4 ctrl/data `PERM` adapter variants.
   - What's unclear: which specific mode-convention fix (if any single one) resolves it — could be the ctrl/data convention (tried, didn't work naively), could be something in how `build_control_gate_unitary`'s internal permutation groups modes for `n≥2` in a way that doesn't map onto "qubit-by-qubit dual rail pairs" as cleanly as assumed, or could be an issue with how `Processor.add()`'s automatic `ModeConnector` PERM-insertion interacts with an 8-mode (vs. `heralded_cz`'s 6-mode) inserted component.
   - Recommendation: budget a dedicated, standalone de-risking task (bare CP circuit, dual-rail in/out, no PBS/state-prep/conjugation involved yet — directly analogous to how `heralded_cz_derisking.py`/Phase 10 first validated `heralded_cz` in complete isolation before Phase 11 wired it into the full pipeline) before attempting the full TVD pipeline integration. Do not assume this is a drop-in adaptation of `build_cz_insertion`.

3. **Whether the general identity's global phase (`e^{iφ}`) needs explicit correction in the photonic circuit, or is already unobservable**
   - What we know: global phase is unobservable in any single measurement (standard QM fact, and this project's own established convention per ENC-01's treatment of `HWP`'s `i` global phase).
   - What's unclear: whether the mismatch found in Open Question 2 has anything to do with this (unlikely, since global phase doesn't affect probabilities) or is purely a mode-index/convention bug — noted only to rule it out explicitly during the Open Question 2 debugging task rather than let it become a distraction.

## Sources

### Primary (HIGH confidence — direct execution against this repo's installed venv)
- `venv/Lib/site-packages/perceval/components/core_catalog/controlled_rotation_gates.py` — `PostProcessedControlledRotationsItem` full source, read directly
- `venv/Lib/site-packages/perceval/components/core_catalog/heralded_cz.py` — `HeraldedCzItem` full source, read directly, for comparison
- Direct Python execution against `perceval-quandela==1.2.4` (this repo's `venv`): gate identity confirmation across 8 α values, `add_herald`+PBS crash/non-crash isolation, `set_postselection` composition-validation crash, `exact_qubit_iqp_distribution`'s `pair_thetas` parameterization read from source
- `C:\Users\cuqui\merlin-quantum-case-study\iqp_photonic_encoding.py` — full read of the existing weight-1/weight-2 pipeline (`build_cz_insertion`, `build_weight2_processor`, `_build_weight2_processor_no_herald`, `photonic_weight2_iqp_distribution`, `exact_qubit_iqp_distribution`)
- `C:\Users\cuqui\merlin-quantum-case-study\tests\test_iqp_photonic_encoding.py` — full read of existing test conventions (tolerances, parametrization style)
- `C:\Users\cuqui\merlin-quantum-case-study\docs\iqp-photonic-encoding.md` — full read of the existing fixed-π/4 derivation and `heralded_cz` construction

### Secondary (MEDIUM confidence)
- arXiv:2405.01395 (via WebFetch of the abstract) — confirms `PostProcessedControlledRotationsItem` corresponds to a paper on "generalized post-selected n-qubit control-rotation gates" via linear optics; full-text success-probability formula not retrieved (abstract only) — not needed for this phase's empirical validation approach, but available if the owner wants a literature citation for the derivation writeup

### Tertiary (LOW confidence / not used)
None — no unverified WebSearch-only claims are relied on in this document.

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH — no new dependencies, existing installed venv used directly
- Gate identity / API behavior (`CP(α)=diag(1,1,1,e^{iα})`, success-probability-varies-with-α, `n`/`alpha` type requirements): HIGH — verified by direct execution at 8 different α values
- Reference-infrastructure parameterization (`exact_qubit_iqp_distribution` already generalized): HIGH — read directly from source, confirmed by existing test usage
- General operator identity algebra: MEDIUM — verified as an abstract 4×4 matrix identity, not yet confirmed through the actual wired photonic circuit
- Circuit wiring / TVD pass: LOW / open risk — explicitly unresolved in this research pass, flagged as a real implementation task, not a research gap that blocks planning (the plan should include a wiring de-risking task, not assume the wiring is solved)
- α vs θ boundary-value disambiguation: flagged as an open question requiring explicit resolution, not asserted either way

**Research date:** 2026-08-07
**Valid until:** No expiry driver (no external library version changes expected to affect this — `perceval-quandela==1.2.4` is already pinned/installed; re-verify only if the venv's Perceval version changes)
