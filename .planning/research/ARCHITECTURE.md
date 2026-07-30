# Architecture Research

**Domain:** Photonic quantum computing (Perceval/MerLin) — module/code-boundary planning for an IQP-to-photonics encoding-design milestone. No implementation in this milestone; this documents where the *eventual* code will live and which API layer it will use, so Phase 1's on-paper design is written in directly-transcribable terms.
**Researched:** 2026-07-30
**Confidence:** HIGH (all claims below verified against the actually-installed packages in this repo's venv — `perceval-quandela==1.2.4`, `merlinquantum==0.4.0` — by reading source and running a live Perceval circuit/Processor/Analyzer round-trip, not from training-data recall or docs alone)

## Answering the four research questions directly

1. **New work should live in a new top-level module, sibling to `generator/`, not nested inside it.** Recommend `iqp_photonic/` at repo root. Reasoning in "Recommended Project Structure" below.
2. **Confirmed: MerLin wraps Perceval, at a specific and narrow point.** MerLin ships its own circuit-description DSL (`CircuitBuilder` + a `merlin.core.circuit.Circuit` metadata container of `Rotation`/`BeamSplitter`/`GenericInterferometer` objects) that *compiles down to* a real `perceval.Circuit` via `CircuitBuilder.to_pcvl_circuit()`. Separately, `merlin.QuantumLayer.__init__` accepts a raw `pcvl.Circuit` directly (`circuit=` kwarg) as a first-class, fully-supported alternative to the builder — this is the manual-construction code path, not an unofficial escape hatch. See "Perceval vs. MerLin API Boundary" below for the concrete mechanics.
3. **No built-in Perceval object represents a qubit-gate-model circuit for direct structural comparison.** Perceval's only qubit-circuit bridge (`QiskitConverter`, in the separate `perceval-interop` package, not installed) converts a qubit circuit into a *generic* dual-rail-encoded photonic `Processor` with ancilla photons for CNOTs — a different, heavier embedding than the bespoke IQP-specific structural mapping this milestone is designing, and not what Phase 2 needs. The idiomatic approach for Phase 2's "reduces to known/classically-checkable behavior" check is **two independent classical computations diffed against each other**, not a circuit conversion. Detailed in "Anti-Patterns" and "Integration Points" below.
4. **No new dependencies needed for this milestone (Phase 0/1, docs only).** For the deferred Phase 2 implementation, raw Perceval circuit construction (`Circuit`, `PS`, `BS`, `BasicState`, `Processor`, `Analyzer`) needs nothing beyond what's already installed — verified by running a live example (below). The qubit-IQP reference side needs no new dependency either; IQP's own algebraic structure (`H^⊗n · D · H^⊗n`) is directly computable with plain NumPy at the small system sizes a brute-force sanity check requires. Do not add Qiskit or `perceval-interop` speculatively — see "Anti-Patterns."

## Standard Architecture

### System Overview (current repo, both milestones)

```
┌──────────────────────────────────────────────────────────────────────┐
│                         Repo root (Python)                            │
├─────────────────────────────┬──────────────────────────────────────┤
│   generator/  (v1.0, shipped)│   iqp_photonic/  (v2.0, this milestone)│
│   MMD-trained photonic       │   IQP→photonic encoding research —    │
│   generative model on        │   literature scoping (Phase 0/8) +    │
│   QuantumLayer.simple()      │   on-paper design (Phase 1/9) now;    │
│                               │   minimal implementation (Phase 2)    │
│                               │   and trainability study (Phase 3)    │
│                               │   deferred to a future milestone      │
├─────────────────────────────┴──────────────────────────────────────┤
│                    merlin (merlinquantum==0.4.0)                     │
│  ┌────────────────────┐   ┌──────────────────────────────────────┐  │
│  │ CircuitBuilder DSL   │   │ QuantumLayer(circuit=<pcvl.Circuit>) │  │
│  │ (.simple(), declar-  │──▶│ raw-circuit path — v2.0's future      │  │
│  │ ative add_rotations/ │   │ code path once Phase 2 starts         │  │
│  │ add_superpositions)  │   │                                        │  │
│  └──────────┬───────────┘   └───────────────┬──────────────────────┘  │
│             │ .to_pcvl_circuit()             │ both converge here      │
│             ▼                                ▼                        │
│  ┌────────────────────────────────────────────────────────────────┐  │
│  │           merlin/pcvl_pytorch/ — SLOS/TorchScript bridge        │  │
│  │  Converts a pcvl.Circuit's unitary + Fock input/output basis    │  │
│  │  into differentiable permanent-based probability tensors.       │  │
│  │  This is the actual simulation engine; both circuit sources     │  │
│  │  (builder-compiled or hand-built) go through it identically.    │  │
│  └────────────────────────────────────────────────────────────────┘  │
├───────────────────────────────────────────────────────────────────┤
│                  perceval (perceval-quandela==1.2.4)                 │
│  Circuit, PS, BS, BasicState, Processor, Simulator, Analyzer,        │
│  Sampler — the actual linear-optical primitives and exact/           │
│  finite-shot simulators. Independent of MerLin; usable standalone    │
│  for Phase 2's non-differentiable brute-force sanity check.          │
└───────────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

| Component | Responsibility | Typical Implementation |
|-----------|----------------|------------------------|
| `perceval.Circuit` / `PS` / `BS` | Ground-truth linear-optical circuit description: modes, phase shifters, beamsplitters, placed manually by mode index | `c = pcvl.Circuit(n_modes); c.add(i, pcvl.PS(phi)); c.add((i,j), pcvl.BS())` |
| `perceval.BasicState` | Fock-space input/output state (photon occupation per mode) | `pcvl.BasicState([1,0,1,0])` |
| `perceval.Processor` + `Simulator`/`Analyzer`/`Sampler` | Exact or finite-shot simulation of a circuit against a bound input state; `Analyzer` produces a full output probability table over specified `BasicState`s — the tool for Phase 2's brute-force check | `p = pcvl.Processor("SLOS", circuit); p.with_input(input_state); pcvl.algorithm.Analyzer(p, output_states).compute()` |
| `merlin.builder.CircuitBuilder` | Declarative, auto-parameter-tracking circuit assembly (what v1.0's `.simple()` uses internally) | `.add_rotations(...)`, `.add_superpositions(...)`, `.to_pcvl_circuit()` |
| `merlin.algorithms.QuantumLayer` | Differentiable PyTorch module wrapping a circuit (from a builder, a raw `pcvl.Circuit`, or a `pcvl.Experiment`) plus an input state and measurement strategy | `ML.QuantumLayer(circuit=my_pcvl_circuit, input_state=..., trainable_parameters=[...], input_parameters=[...])` |
| `merlin.pcvl_pytorch` | Low-level permanent-computation bridge (SLOS, TorchScript-compiled) converting a circuit's unitary + Fock basis into a differentiable probability tensor | Internal; not called directly by user code — `QuantumLayer` invokes it |

## Recommended Project Structure

This milestone (literature scoping + on-paper design) produces **no code under this structure yet** — it is a documentation deliverable. The structure below is the target layout Phase 1's design doc should be written *against*, so a future implementation milestone can transcribe it directly without a redesign pass.

```
merlin-quantum-case-study/
├── generator/                    # v1.0, shipped — untouched by v2.0
│   └── ...                       # (existing MMD generator modules)
├── iqp_photonic/                 # v2.0 — NEW top-level module, sibling to generator/
│   ├── __init__.py
│   ├── qubit_iqp.py              # (future) qubit-side reference: build & exactly
│   │                              #   evaluate small IQP circuits via H^⊗n D H^⊗n
│   │                              #   in plain NumPy — the "known/classically-
│   │                              #   checkable" baseline for Phase 2
│   ├── encoding.py                # (future) Phase 1's design turned into code:
│   │                              #   functions mapping IQP structural parameters
│   │                              #   (num modes, diagonal-gate angles) onto a
│   │                              #   pcvl.Circuit built from PS/BS primitives
│   ├── compare.py                 # (future) Phase 2's sanity-check harness: run
│   │                              #   both sides at small n, diff distributions
│   │                              #   (this is where the qubit-bitstring ↔
│   │                              #   photonic-Fock-state label correspondence
│   │                              #   defined in Phase 1's design gets used)
│   └── trainability.py            # (future, Phase 3 — do not build this milestone)
├── docs/
│   ├── iqp-baseline.md            # THIS milestone: compiled prior IQP +
│   │                              #   barren-plateau notes (Active requirement #3)
│   └── iqp-photonic-encoding.md   # THIS milestone: the on-paper mapping design
│                                  #   itself (Active requirement #4) — the actual
│                                  #   novel-contribution deliverable
├── .planning/research/            # literature-scoping findings (this research pass)
└── tests/
    └── test_iqp_photonic_*.py     # (future) mirrors generator/'s one-file-per-
                                   #   module test convention once Phase 2 starts
```

### Structure Rationale

- **`iqp_photonic/` as a new top-level sibling module, not `generator/iqp_photonic/`:** the two milestones have genuinely different core values — v1.0 is "a working, benchmarked MMD generative model"; v2.0 is "does IQP's structure survive photonic translation," a trainability/hardness research question. They share no runtime code path: `generator/`'s bin-centers, MMD-loss, and natural-order correspondence machinery are all specific to the histogram-matching generative task and have no role in a gradient-variance-vs-system-size study or a classical-vs-photonic distribution diff. Nesting under `generator/` would imply a dependency or extension relationship that doesn't exist and would force future readers to untangle unrelated concerns inside one package. The existing repo already uses flat top-level modules (`generator/`, `docs/`, `tests/`) rather than a nested `src/` tree, so a new sibling module matches convention.
- **`docs/iqp-baseline.md` and `docs/iqp-photonic-encoding.md` under the existing `docs/`:** the repo already uses `docs/` for durable reference material (`raster-order.md`, `mmd-loss.md` from v1.0) rather than `.planning/`, which is scoped to phase/milestone process artifacts. The two Active requirements that are genuinely durable knowledge (compiled IQP/barren-plateau baseline; the encoding design itself) belong there for the same reason v1.0's mechanism docs do — they're referenced by future code and by the eventual write-up, not just by this milestone's planning process.
- **`compare.py` living inside `iqp_photonic/`, not a top-level script:** unlike v1.0's `benchmark.py`/`sweep.py` pattern (top-level scripts for one-off analysis runs), the classical-vs-photonic comparison is core validation logic Phase 2 depends on directly (it's the "verify it reduces to known IQP behavior" gate) — it belongs in the importable package, with a thin top-level script (if wanted) calling into it, matching how `generator/train.py` is importable and `train.py` at repo root is a thin caller.

## Perceval vs. MerLin API Boundary

### The actual relationship (verified against installed source, not assumed)

MerLin (`merlinquantum==0.4.0`) is built **on top of** Perceval (`perceval-quandela==1.2.4`) — it does not reimplement linear optics. Concretely:

- `merlin.core.circuit.Circuit` is **MerLin's own metadata container** (a dataclass holding a list of `Rotation`/`BeamSplitter`/`GenericInterferometer`/`EntanglingBlock` objects) — it is **not** a `perceval.Circuit` and has no simulation capability of its own. Do not confuse the two; they share the class name `Circuit` but live in different modules (`merlin.core.circuit.Circuit` vs. `perceval.components.linear_circuit.Circuit`, exposed as `pcvl.Circuit`). This is a real naming collision worth flagging for whoever writes Phase 2's code — always import Perceval as `pcvl` and never do `from merlin.core.circuit import Circuit` in the same file as `from perceval import Circuit`.
- `merlin.builder.CircuitBuilder` is MerLin's **declarative DSL layer**: `.add_rotations(...)`, `.add_superpositions(...)`, `.add_entangling_layer(...)` build up the MerLin-native `Circuit` metadata object, tracking which parameters are trainable vs. input-driven automatically. `QuantumLayer.simple()` — what v1.0 used exclusively — calls this builder internally and never exposes a raw `pcvl.Circuit` to user code.
- `CircuitBuilder.to_pcvl_circuit()` is the actual compilation step: it walks the MerLin `Circuit`'s component list and emits a real `perceval.Circuit`, translating each MerLin component 1:1 (`Rotation` → `pcvl.PS`, `BeamSplitter` → `pcvl.BS`, `GenericInterferometer` → a Perceval `GenericInterferometer` built from an MZI or "bell" factory). This confirms MerLin's abstractions sit **strictly above** Perceval's circuit primitives — one level of indirection, not a parallel implementation.
- `merlin.algorithms.QuantumLayer.__init__` accepts **exactly one** of three mutually exclusive circuit sources (source-verified, `layer.py:109-135`): `builder: CircuitBuilder`, `circuit: pcvl.Circuit`, or `experiment: pcvl.Experiment`. The `circuit=` path is what "manual circuit construction with phase shifters/beamsplitters" concretely means in code — it is a fully documented, first-class constructor argument, not an internal/private workaround.
- Underneath both paths, `merlin/pcvl_pytorch/` (`slos_torchscript.py`, `noisy_slos.py`, `locirc_to_tensor.py`) is the actual simulation engine: it takes the resolved Perceval circuit's unitary and the bound Fock input/output state space and computes permanents (SLOS algorithm, TorchScript-compiled) to produce a differentiable probability tensor. This is identical regardless of whether the circuit came from a builder or was hand-built — the builder/raw-circuit distinction only affects *how the circuit's structure was described*, not how it's simulated.

### What "manual circuit construction" concretely looks like as code

Two distinct code paths exist depending on whether differentiability/training is needed — both use the same Perceval object vocabulary:

**Path A — raw Perceval only (no MerLin), for Phase 2's non-differentiable classical-behavior check:**
```python
import perceval as pcvl

n_modes = 4
circuit = pcvl.Circuit(n_modes)
circuit.add(0, pcvl.PS(phi=some_angle))          # phase shifter, single mode
circuit.add((1, 2), pcvl.BS())                   # beamsplitter, mode pair
# ... place remaining PS/BS per the Phase 1 design spec, by explicit mode index

input_state = pcvl.BasicState([1, 0, 1, 0])       # Fock-space input
processor = pcvl.Processor("SLOS", circuit)
processor.with_input(input_state)

output_states = [pcvl.BasicState([...]), ...]     # the states to compare against
analyzer = pcvl.algorithm.Analyzer(processor, output_states)
analyzer.compute()                                 # exact output distribution
```
Verified working end-to-end against the installed `perceval-quandela==1.2.4` (a live 2-mode PS+BS circuit through `Processor` + `Analyzer` was run during this research pass and produced the expected symmetric two-photon interference distribution).

**Path B — wrapped in MerLin, once/if the design needs to be trainable (a later milestone, not this one):**
```python
import perceval as pcvl
import merlin as ML

circuit = pcvl.Circuit(n_modes)
# ... same manual PS/BS placement as Path A ...

layer = ML.QuantumLayer(
    circuit=circuit,
    input_state=pcvl.BasicState([1, 0, 1, 0]),
    trainable_parameters=["theta"],   # Perceval parameter-name prefixes to expose to autograd
    input_parameters=["px"],          # prefixes used for classical (angle) encoding, if any
)
```
This is the path v1.0's code never used (it only called `.simple()`), so it is genuinely new ground for this repo — but it is a documented, supported constructor path, not experimental API surface.

**Recommendation for Phase 1's design doc:** write the mapping in terms of Path A's vocabulary (`pcvl.Circuit`/`PS`/`BS`/`BasicState`) since that's the minimal, framework-agnostic description of the actual linear-optical circuit. Whether it later gets wrapped in `ML.QuantumLayer` (Path B) is an implementation-time decision for a deferred trainability-study milestone, not something Phase 1's design needs to settle now.

## Architectural Patterns

### Pattern 1: Two-sided independent classical evaluation (for Phase 2's sanity check)

**What:** Instead of converting one circuit representation into the other, compute each side's output probability distribution independently at a small system size, then numerically diff the two distributions against an explicitly-defined label correspondence.
**When to use:** Any time a novel encoding claims to "reduce to" or "preserve the structure of" a known circuit family — the honest verification is agreement between two independently-derived ground truths, not a single converted artifact that could itself be buggy.
**Trade-offs:** Requires defining the qubit-bitstring ↔ photonic-Fock-state correspondence explicitly as part of the design (this is real design work, not a formality) — but that correspondence is something Phase 1's spec needs to state anyway to be implementable, so this isn't extra scope, just making an implicit step explicit and load-bearing.

**Example (conceptual, not yet code — this is what Phase 2, deferred, will build):**
```python
# Qubit side: IQP circuit is H^⊗n · D · H^⊗n where D is diagonal in the
# computational basis. At small n this is directly computable with NumPy —
# no qiskit/qutip dependency needed.
qubit_probs = evaluate_iqp_classically(diagonal_angles, n_qubits=3)

# Photonic side: the Phase 1 encoding, simulated exactly via Perceval.
photonic_probs = analyzer_output_from(encoding_circuit, input_state)

# The correspondence (defined by Phase 1's design) maps qubit bitstrings
# to the photonic circuit's relevant BasicState outputs.
compare_distributions(qubit_probs, photonic_probs, correspondence_map)
```

### Pattern 2: Builder DSL for structured/repeating layers vs. raw Circuit for bespoke placement

**What:** MerLin's `CircuitBuilder` is optimized for regular, repeating layer structures (trainable entangling layers, uniform angle encodings) — it auto-generates parameter names and tracks trainable/input prefixes for you. Raw `pcvl.Circuit` construction is for bespoke, irregular placement where each phase shifter/beamsplitter's position is dictated by a specific structural mapping (exactly this milestone's situation: IQP's diagonal-gate-per-qubit + paired Hadamard-basis-conjugation structure doesn't match any of the builder's generic layer templates).
**When to use:** Builder DSL when the circuit is "N repeated units of a standard block" (what v1.0 needed); raw Perceval when the circuit's structure *is* the research question (what v2.0 needs).
**Trade-offs:** Raw construction means no automatic parameter-prefix bookkeeping — `trainable_parameters`/`input_parameters` prefixes must be tracked and passed to `QuantumLayer` explicitly if/when Path B is used later.

## Anti-Patterns

### Anti-Pattern 1: Reaching for `perceval-interop`'s `QiskitConverter` as the Phase 2 comparison tool

**What people do:** See "convert a qubit circuit to a photonic one" and assume that's the tool for "compare against qubit IQP."
**Why it's wrong:** `QiskitConverter` (in the separate, not-installed `perceval-interop` package) performs a *generic* dual-rail encoding of an arbitrary qubit circuit — 2 modes per qubit plus ancilla photons implementing CNOTs via heralding/post-selection. That is a completely different, much heavier embedding than the bespoke structural mapping (diagonal gates → phase shifters, Hadamard conjugation → beamsplitters) this milestone is designing. Using it would validate a different circuit than the one Phase 1 actually designs, and would silently add an unrelated dependency and a resource-hungry heralded-gate construction to what should be a small brute-force sanity check.
**Do this instead:** Independent evaluation on both sides (Pattern 1 above) with an explicit, small system size. No circuit-conversion library is needed for this milestone's goals at all.

### Anti-Pattern 2: Treating `merlin.core.circuit.Circuit` and `perceval.Circuit` as the same type

**What people do:** Assume "Circuit" means the same thing across an import boundary, especially since MerLin's builder API is the only thing v1.0's code ever touched.
**Why it's wrong:** They are unrelated classes with the same name in different packages; MerLin's is a plain metadata container with no simulation behavior, Perceval's is the real linear-optical circuit object with a unitary and simulation support. Passing one where the other is expected fails loudly (attribute errors), but silent confusion during design-doc writing (e.g., describing "add a PS to the Circuit" without specifying which) can lead to an ambiguous spec that reads correctly but isn't directly transcribable to code.
**Do this instead:** In Phase 1's design doc and any future code, always write `pcvl.Circuit`/`import perceval as pcvl` explicitly when referring to the actual photonic circuit; never write bare "Circuit" in the spec.

### Anti-Pattern 3: Installing Qiskit or `perceval-interop` speculatively during this milestone

**What people do:** Reach for a qubit-circuit-framework dependency "just in case" the design or comparison needs it later.
**Why it's wrong:** This milestone (Phase 0/1, per PROJECT.md) is docs-only — no code runs. Adding dependencies now, before Phase 2 (deferred, not yet planned) confirms what's actually needed, creates version-drift risk for a benefit that may never materialize, matching the same discipline `STACK.md` already states for `requirements.txt`.
**Do this instead:** Leave `requirements.txt` untouched. When a future milestone actually starts Phase 2, re-derive the dependency need from what the finalized design doc requires (very likely: nothing beyond NumPy for the qubit-side reference, already a transitive dependency via SciPy/scikit-learn).

## Integration Points

### Internal Boundaries

| Boundary | Communication | Notes |
|----------|---------------|-------|
| `generator/` ↔ `iqp_photonic/` | None — no shared imports, no shared runtime state | Deliberate: different research questions, different core values (per PROJECT.md's Current Milestone framing). If a genuine shared utility emerges later (e.g., a common Perceval-circuit-rendering helper), promote it to a small top-level `photonic_utils/` module rather than importing across the two research modules directly — but don't build this preemptively; no such need exists yet. |
| `iqp_photonic/encoding.py` ↔ `perceval` | Direct — builds a `pcvl.Circuit` from Perceval primitives per the Phase 1 design spec | This is the primary, unavoidable dependency; Phase 1's design doc should be written precisely enough that this file is close to a direct transcription. |
| `iqp_photonic/qubit_iqp.py` ↔ `numpy` | Direct — computes `H^⊗n · D · H^⊗n` and resulting output probabilities via plain linear algebra | No qubit-framework dependency (Qiskit/PennyLane/QuTiP) needed at the small system sizes ("small enough to brute-force compare" per the plan doc) this check requires. |
| `iqp_photonic/compare.py` ↔ both of the above | Imports both, applies the Phase 1-defined bitstring↔Fock-state correspondence, diffs distributions | The correspondence-definition step is itself part of Phase 1's design deliverable, not something to improvise during Phase 2 implementation. |
| `iqp_photonic/` ↔ `merlin.QuantumLayer` | Deferred — only relevant once/if a future trainability-study milestone needs differentiability | Not exercised by Phase 0/1 or even Phase 2's sanity check (which only needs exact, non-differentiable simulation via `pcvl.Processor`/`Analyzer`). |

### External Services

None. All work is local simulation (Perceval's `SLOS`/permanent-based exact simulator for small photon numbers) — no cloud QPU access (`cloud.quandela.com`) is in scope for this milestone or the deferred phases described in the plan doc.

## System-Size Scaling Considerations (domain-specific — not user-count scaling)

The relevant "scale" axis for this domain is number of modes/photons (photonic side) and number of qubits (gate-model side), not users/traffic. Included because it directly affects what "small enough to brute-force compare" (Phase 2, deferred) can mean, and should inform Phase 1's design about what system sizes are even checkable later.

| Scale | Photonic-side cost | Qubit-side cost | Implication |
|-------|--------------------|--------------------|-------------|
| n ≤ ~4–6 modes/qubits | Exact permanent computation (`Analyzer`) is fast, full output table enumerable | Exact `2^n`-dimensional statevector via NumPy is trivial | This is the regime Phase 2's brute-force sanity check should target — both sides fully exact and cheap. |
| n ~ 8–14 | Permanent computation cost grows combinatorially (photon-number/mode-count dependent); still tractable for a handful of runs, not a sweep | `2^n` statevector still fine up to ~20-25 qubits in plain NumPy | Plausible upper bound for a deferred Phase 3 (trainability/gradient-variance) sweep across "system size," if that phase is ever planned. |
| Large n (barren-plateau asymptotic regime) | Out of scope — exact simulation infeasible; would need the same finite-shot/`Sampler`-based statistical approach real barren-plateau studies use | Out of scope for brute-force; would need qubit-side gradient-variance estimation matching the owner's prior IQP work | Not this milestone's concern (Phase 0/1 only) — flagged here only so Phase 1's design doc doesn't accidentally assume asymptotic claims are checkable via the same brute-force method as the small-n sanity check. |

## Sources

- `venv/Lib/site-packages/merlin/algorithms/layer.py` (installed `merlinquantum==0.4.0`, lines 93–300, 2010–2100) — `QuantumLayer.__init__` signature and `.simple()` implementation, read directly. HIGH confidence (primary source, matches installed version).
- `venv/Lib/site-packages/merlin/builder/circuit_builder.py` — `CircuitBuilder` and `to_pcvl_circuit()` compilation logic, read directly. HIGH confidence.
- `venv/Lib/site-packages/merlin/core/circuit.py` — MerLin's own `Circuit` metadata container, read directly (confirms it is distinct from `perceval.Circuit`). HIGH confidence.
- `venv/Lib/site-packages/merlin/algorithms/layer_utils.py` (lines 467–780) — `validate_and_resolve_circuit_source`, `resolve_circuit`, `prepare_input_state`, read directly; confirms the three mutually-exclusive circuit sources (`builder`/`circuit`/`experiment`). HIGH confidence.
- Live verification run in this repo's venv: constructed a 2-mode `pcvl.Circuit` with `PS`+`BS`, bound via `pcvl.Processor("SLOS", circuit)`, computed exact output distribution via `pcvl.algorithm.Analyzer` — produced the expected symmetric Hong-Ou-Mandel-style two-photon distribution. HIGH confidence (executed against installed `perceval-quandela==1.2.4`, not assumed from docs).
- [Perceval-Interop Qiskit converter docs](https://perceval.quandela.net/interopdocs/v1.1/notebooks/Qiskit_converter.html) — confirms the Qiskit bridge lives in a separate `perceval-interop` package (not installed in this repo) and performs dual-rail + ancilla-photon encoding, distinct from a bespoke structural mapping. MEDIUM-HIGH confidence (official docs, WebSearch-surfaced, not independently WebFetched in full).
- `.planning/research/STACK.md` (this milestone's companion research file, already written) — cross-checked for consistency on Perceval API surface (`Circuit`, `PS`, `BS`, `BasicState`, `Processor`, `Analyzer`, `Sampler`) and the "no new dependencies this milestone" conclusion; both files independently arrived at the same recommendation. HIGH confidence (agreement between two independent research passes against the same installed environment).
- `.planning/PROJECT.md` (Current Milestone, Requirements, Context sections) and `Post_Sept1_IQP_Photonic_Plan.md` — milestone scope, phase boundaries, and the explicit "Phase 0/1 only, re-plan after Phase 0" constraint that shapes why this doc treats Phase 2+ as deferred/future rather than in-scope. HIGH confidence (primary repo sources).

---
*Architecture research for: IQP → photonic circuit encoding (literature scoping + on-paper design milestone)*
*Researched: 2026-07-30*
