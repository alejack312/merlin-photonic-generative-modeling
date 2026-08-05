# Phase 9: Encoding Design - Research

**Researched:** 2026-08-05
**Domain:** Linear-optical (Fock-space, DV) qubit encoding schemes, mapped onto Perceval's native primitives, for translating IQP's structure
**Confidence:** MEDIUM-HIGH (Perceval API facts are HIGH — read directly from the installed `perceval-quandela==1.2.4` source; the encoding-scheme survey and IQP-correspondence material is MEDIUM, since it synthesizes textbook LOQC theory that the owner still has to adapt and verify; the toy-validation options are MEDIUM-HIGH, grounded in this repo's own verified code)

## Summary

This phase has no finished answer to hand over — CONTEXT.md is explicit that the encoding scheme is the owner's choice and Claude must not recommend one. What follows is raw material: (1) an inventory of what Perceval actually has built in for qubit-on-photon encoding (more than expected — Perceval ships a first-class `Encoding` enum with `DUAL_RAIL`, `POLARIZATION`, `RAW`, and `QUDIT2`-`QUDIT7`, plus a catalog of ready-made single- and two-qubit gates for dual rail), (2) the structural tension each candidate scheme has with IQP's three ingredients (fixed `|+⟩` start, commuting Z-diagonal middle layer, Hadamard-conjugated measurement), (3) exactly what basis-correspondence and validation options are concretely available given what's installed in this repo's venv, and (4) the known theoretical pitfalls (KLM non-determinism, a single-rail no-go theorem, and how Douce et al. realized their own Hadamard-analogue) that any owner-authored mapping will have to confront honestly rather than paper over.

The central finding worth flagging up front: Perceval's own dual-rail single-qubit gate catalog (`gates_1qubit.py`) implements Hadamard as exactly `BS.H()` — the same Hadamard-convention beamsplitter already verified end-to-end in `perceval_fluency_demo.py`'s MZI example — and implements Z-axis phase gates (S, T, Rz, Pauli-Z) as bare `PS()` on one rail. That is a strong, ready-made structural echo of IQP's own `H`-diagonal-gates-`H` sandwich, and it is the most natural place to start an ENC-01 attempt for dual rail. The second finding worth flagging is that Perceval's `QUDITn` encoding (one photon among `2^n` modes, i.e. a one-hot/path encoding of an entire n-qubit register) sidesteps the hardest part of dual rail — probabilistic multi-qubit entangling gates — entirely, at the cost of `2^n` modes. Both of these are structural facts about the *toolkit*, not endorsements of either scheme; the owner should weigh them alongside the tradeoffs below.

**Primary recommendation (process, not scheme choice):** structure ENC-01's attempt around whichever scheme the owner instinctively reaches for after reading the survey below, but budget explicit time to hit and resolve the "how does the *entangling* part of the gate layer work" question for that scheme before calling ENC-01 done — every scheme surveyed here has a real, non-hand-wavy difficulty at exactly that point, and it's the part most likely to get glossed over in an on-paper mapping if not deliberately confronted.

## Standard Stack

### What Perceval (v1.2.4, installed in this repo's venv) natively ships for DV qubit encoding

Verified by direct introspection of the installed package (`venv/Lib/site-packages/perceval`), not from general/possibly-stale training knowledge:

| Component | What it is | Verified location |
|---|---|---|
| `pcvl.Encoding` (enum) | `DUAL_RAIL`, `POLARIZATION`, `RAW`, `QUDIT2`...`QUDIT7` | `perceval/utils/_enums.py` |
| `pcvl.LogicalState` | Represents a bitstring (`"011"` or `[0,1,1]`) as a logical qubit-register state, independent of the Fock encoding | `perceval/utils/...` (used by `Processor.with_input`) |
| `pcvl.Port(encoding, name)` / `get_basic_state_from_ports` | Attaches an `Encoding` to a block of modes on a `Processor`, and converts a `LogicalState` → `BasicState` automatically per that encoding's rule | `perceval/components/port.py` |
| `pcvl.components.core_catalog.*` | Ready-made circuits: `h`, `s`, `sdag`, `t`, `tdag`, `x`, `y`, `z`, `rx`, `ry`, `rz`, `ph` (all dual-rail, 2 modes each); `heralded cnot`, `heralded cz`, `postprocessed cnot`, `postprocessed cz`, `klm cnot`, `toffoli` | `perceval/components/core_catalog/*.py` |
| `pcvl.GenericInterferometer` / `pcvl.Unitary` | Build an arbitrary `m×m` unitary as a Reck/Clements-decomposed mesh of beamsplitters+phase shifters, or drop in a raw unitary matrix directly | `perceval/components/generic_interferometer.py` |
| `pcvl.PERM([...])` | A fixed mode-permutation component (used for Pauli-X in dual rail: `PERM([1,0])`) | used throughout `core_catalog` |
| `pcvl.DetectionType` | `PNR` (photon-number-resolving), `Threshold`, `PPNR`, `Mixed` — which kind of photon-counting the measurement models | `perceval/utils/_enums.py` |
| `pcvl.StateGenerator(encoding)` | Convenience class turning a bit-list into a `StateVector`, for `RAW`, `DUAL_RAIL`, `POLARIZATION` only (not `QUDIT*`) | `perceval/utils/stategenerator.py` |

**What Perceval does NOT have** (checked directly — `dir(pcvl)` contains no matches for `squeez`, `homodyne`, `displac`, `quadrature`, `gkp`, `continuous`): no continuous-quadrature/CV primitives at all. This is hard confirmation — not just CONTEXT.md's stated scope decision — that a GKP-style or any other quadrature-based scheme is not buildable with Perceval's actual installed API; it would require Strawberry Fields or similar, which `REQUIREMENTS.md`'s Out-of-Scope table already excludes.

### Already-verified Perceval usage patterns in this repo (from `perceval_fluency_demo.py`, PREQ-01 checkpoint, owner-run)

- `pcvl.Circuit(m)` then `circuit.add(start_port_index, component)` — `add`'s first argument is a **starting port index (int)**, not a range or tuple, even for multi-mode components (gotcha already caught in Phase 8).
- `pcvl.BS.H()` — the Hadamard-convention 50/50 beamsplitter, real-valued `[[1,1],[1,-1]]/√2`. This is what dual-rail's catalog `h` gate also literally is (`gates_1qubit.py`: `HadamardItem.circuit = BS.H()`).
- `pcvl.PS(theta)` applies phase `e^{iθ}` to one mode; **invisible under Fock-basis (photon-number) measurement unless there's a second beamsplitter to interfere against** — already derived and verified via the MZI (`BS.H() → PS(θ) → BS.H()`) construction, closed form `P(|1,0⟩) = cos²(θ/2)`, `P(|0,1⟩) = sin²(θ/2)`.
- `Analyzer(processor, input_states, "*")` needs a `Processor("SLOS", circuit)`, not a bare `Circuit`; `.compute()` then `.distribution` (rows = inputs, columns = `.output_states_list`).
- `PYTHONIOENCODING=utf-8` needed on Windows before `pcvl.pdisplay()` or it raises `UnicodeEncodeError` on box-drawing characters.

**Installed versions (confirmed via venv):** `perceval-quandela==1.2.4`, `merlinquantum==0.4.0`, `numpy==2.5.1`, `torch==2.12.1`. No `pytest`/CV toolkits relevant here beyond what's listed.

## Survey of Candidate Encoding Schemes

Presented as options with honest tradeoffs — not a recommendation. All four are natively representable in Perceval's `Encoding` enum or its documented conventions; GKP/time-frequency/continuous schemes are addressed separately below and ruled out on toolkit grounds, not preference.

### 1. Dual-rail (path) encoding — `Encoding.DUAL_RAIL`

**What it is:** each qubit = 2 modes, exactly one photon shared between them. `|0⟩ → BasicState([1,0])`, `|1⟩ → BasicState([0,1])` (Perceval's own convention, `port.py:_to_fock`). n qubits → 2n modes, n photons total.

**Why it's the textbook-standard LOQC scheme:** this is the encoding Kok, Munro, Nemoto, Ralph, Dowling, Milburn's review ("Linear optical quantum computing with photonic qubits," Rev. Mod. Phys. 79, 135, 2007) and the original KLM protocol (Knill, Laflamme, Milburn 2001) are built around. It's also exactly the scheme Perceval's own gate catalog implements.

**Single-qubit gates:** trivial and deterministic — `H = BS.H()`, `Z = PS(π)` on rail 1, `S/T = PS(±π/2)/PS(±π/4)` on rail 1, `X = PERM([1,0])`, `Rz(θ) = PS(-θ/2)` on rail 0 `+ PS(θ/2)` on rail 1, `Rx/Ry` via `BS.Rx`/`BS.Ry`. All read directly from `perceval/components/core_catalog/gates_1qubit.py` — no derivation needed, they're shipped.

**Multi-qubit (entangling) gates — the hard part:** deterministic linear optics **cannot** implement a deterministic two-photon entangling gate on dual-rail qubits (this is the KLM starting problem). Perceval's own catalog only offers CZ/CNOT as **heralded** (`heralded cz`/`heralded cnot`, ancilla photons + herald detection, still probabilistic but flagged by a successful herald) or **post-selected** (`postprocessed cz`/`postprocessed cnot`, success conditioned on a specific measurement outcome, `PostSelect("[0,1]==1 & [2,3]==1")` in the installed source, using a beamsplitter of reflectivity 1/3 — `BS.r_to_theta(1/3)`). Known success-probability figures from the literature: KLM's original post-selected CZ succeeds with probability 1/9; various heralded variants reported around 2/27 (Knill 2002) — exact numbers vary by construction and the owner should verify against whichever specific gate they cite, not treat these as settled. **This directly matters for ENC-01**: IQP's middle layer is `MultiRZ(2θⱼ, wires=gⱼ)` for generators `gⱼ` that can touch 2+ qubits (weight-≥2 Z-words), not just single-qubit phase gates. Realizing those in dual rail means chaining probabilistic/heralded CZ-like gates — a real cost that scales with how many multi-qubit generators the worked example uses, and something the mapping needs to state plainly rather than gloss over.

**Interesting structural echo:** Perceval's own `heralded cnot` catalog item is built as `H(data) → Heralded-CZ → H(data)` (`heralded_cnot.py`) — literally the same "sandwich a diagonal operation between Hadamards" structure IQP itself uses. Worth noting as a resonance, not proof of anything.

### 2. Single-rail (Fock/occupation) encoding — `Encoding.RAW`

**What it is:** each qubit = 1 mode; `|0⟩` = vacuum, `|1⟩` = one photon in that mode (`port.py`: `RAW` → `[int(qubit_state[0])]`). n qubits → n modes.

**Appeal:** minimal mode count (no doubling), and single-rail's entangled states *can* be generated deterministically, unlike dual rail's probabilistic two-qubit gates (this is the tradeoff single-rail is usually pitched on).

**The catch, with a citable no-go result:** Wu, Walther, Lidar, "No-go theorem for passive single-rail linear optical quantum computing," Sci. Rep. 3, 1394 (2013), arXiv:1107.4646, proves that **passive linear optics alone (beamsplitters + phase shifters, no nonlinearity) cannot simultaneously (a) implement a deterministic two-qubit entangling gate and (b) suppress two-photon bunching** — bunched states (two photons landing in the same single-rail mode) leak outside the computational subspace and passive optics can't be built to prevent it while keeping entangling determinism. Universal single-rail LOQC needs nonlinear elements, active measurement/post-selection, or dissipative operations — i.e., it inherits its own version of the same "can't stay deterministic and stay in the computational subspace with linear optics alone" problem dual rail has, just packaged differently.

**A more basic problem for IQP specifically:** a bare single mode gives no interference partner. `perceval_fluency_demo.py` already demonstrated that `PS(θ)` alone is invisible to Fock-basis measurement without a second beamsplitter to interfere against — so any single-rail "gate" that needs to do anything beyond a global (unobservable) phase requires borrowing a second mode anyway (a reference/vacuum arm), at which point the construction is operationally close to a 2-mode (dual-rail-like) circuit for that gate, even though the encoding is nominally 1 mode per qubit. This tension — single-rail's minimal mode count vs. its need for borrowed interference partners to do anything Hadamard-conjugation-like — is worth the owner working through explicitly if this scheme is chosen.

### 3. Polarization encoding — `Encoding.POLARIZATION`

**What it is:** each qubit = 1 spatial mode carrying a single photon in a superposition of horizontal/vertical polarization; `|0⟩`/`|1⟩` map to `BasicState("|{P:H}>")` / `BasicState("|{P:V}>")` by default (`StateGenerator`, `perceval/utils/stategenerator.py`). Structurally isomorphic to dual rail (2 orthogonal degrees of freedom carrying 1 photon) — a polarizing beamsplitter or waveplate plays the role a spatial beamsplitter/phase shifter plays in dual rail.

**Native support level:** thinner than dual rail in Perceval's own catalog — `Encoding.POLARIZATION` is listed and `StateGenerator` supports it, and `pcvl.HWP` (half-wave plate) exists as a component, but there is **no polarization-encoded gate catalog** analogous to `gates_1qubit.py`'s dual-rail set, and the two-qubit gate catalog (`heralded/postprocessed cnot/cz`) is dual-rail-only. Using polarization would mean deriving the gate set from scratch by analogy to dual rail (polarization rotation ↔ `BS`-like mixing, phase plate ↔ `PS`-like phase) rather than reusing shipped building blocks — more owner-derivation work for a scheme that's mathematically the twin of dual rail, not the same amount of glue-code savings.

**Bottom line for the survey:** polarization is a legitimate standard scheme in the LOQC literature (Kok et al. cover it), but for *this* project's "use MerLin/Perceval's existing native primitives, no custom infrastructure" constraint, it offers strictly less ready-made scaffolding than dual rail for essentially the same physics — worth including for completeness, but the owner should weigh that gap honestly if considering it.

### 4. QUDIT/one-hot path encoding of the whole register — `Encoding.QUDIT2`...`QUDIT7`

**What it is:** not "one qubit at a time" — `QUDITn` encodes **n qubits at once** as a single photon in one of `2^n` modes (`_enums.py`: `QUDIT3` = "Encodes 3 qubits on 1 photon in 8 modes"). Bit-string `b` maps to a photon in mode `int(b, 2)` (`port.py:_to_fock`, `QUDIT*` branch: `photon_pos = sum(val*(2**idx) for idx, val in enumerate(reversed(qubit_state)))`).

**Why this is structurally interesting for IQP specifically:** because the full computational-basis bitstring is literally the mode index, any operator diagonal in the computational basis (which is exactly what IQP's whole middle layer is, by construction — every generator `gⱼ` contributes a Z-diagonal phase) becomes diagonal in the Fock/mode basis too. A diagonal-in-mode-basis unitary on a single photon is realized by **independent phase shifters, one per mode** — no interferometry, no ancillas, no entangling gates needed at all, regardless of how many qubits a given generator `gⱼ` touches. This sidesteps dual rail's hardest problem (probabilistic multi-qubit entangling gates) completely, because in this encoding there's no multi-photon entangling operation to build in the first place — the "entanglement" of the original qubit register is entirely absorbed into which single mode the lone photon occupies.

**The cost:** Hadamard-basis conjugation (`H^⊗n`, an honest `2^n × 2^n` dense unitary in this basis) is no longer a small fixed 2-mode gate you tensor n times — it needs a genuine `2^n`-mode interferometer. `pcvl.GenericInterferometer`/`pcvl.Unitary` can realize *any* `2^n×2^n` unitary deterministically (Reck/Clements decomposition, no post-selection, no ancillas — single-particle QM guarantees this), but mode count and component count both scale exponentially in n. For the n=2-3 worked example this is trivial (4-8 modes); it does not scale as a general-n construction, and the mapping document should say so plainly rather than imply it does.

**Framing worth surfacing to the owner:** this scheme effectively re-derives the standard "qubit register as a first-quantized single-particle state in an exponentially large mode space" trick sometimes used in photonic/LOQC pedagogy — it is a real, correct correspondence, not a hack, but its exponential mode cost is exactly why it isn't how anyone builds a *scalable* photonic quantum computer (dual rail's linear-in-n mode count is why that's the field's actual workhorse). Whether that tradeoff is acceptable depends entirely on what ENC-01/ENC-04 need to demonstrate at n=2-3 versus what the "general n" statement is allowed to claim.

### Ruled out on toolkit grounds (not preference): GKP, time-bin, frequency-bin

- **GKP (Gottesman-Kitaev-Preskill) encoding:** the scheme Douce et al. (2017) themselves rely on to correct finite-squeezing errors. It requires squeezed states and homodyne detection — continuous-quadrature CV primitives. Confirmed by direct introspection: Perceval has **zero** CV/quadrature components (`squeez`, `homodyne`, `displac`, `quadrature`, `gkp` all return no matches in `dir(pcvl)`). Not buildable without Strawberry Fields or equivalent, which is explicitly out of scope per `REQUIREMENTS.md`.
- **Time-bin encoding:** a real, standard hardware scheme (qubit = a single photon's arrival time in one of two temporal bins, via an unbalanced fiber-loop interferometer). Perceval's `Circuit`/`Processor` model is a **static spatial-mode** linear-optical network — there's no native time-bin component. Once a time-bin scheme is unfolded into Perceval's simulation formalism, it is mathematically indistinguishable from dual rail (2 "which-path" degrees of freedom carrying 1 photon) — so for *this project's simulation purposes* it adds a physical-realizability story but no new mapping content over dual rail. Worth a one-line mention in the doc, not separate treatment.
- **Frequency-bin / other continuous DOF schemes:** same story as time-bin — not natively modeled by Perceval's discrete spatial-mode `Circuit` abstraction.

## IQP Ingredient-by-Ingredient Correspondence — Raw Material (not a finished mapping)

IQP's three ingredients, restated from `docs/iqp-baseline.md`: (1) every qubit starts in `|+⟩` (Hadamard on `|0⟩`), (2) a middle layer of gates diagonal in the Z-basis (commuting, hence "instantaneous"), (3) Hadamard again, then computational-basis measurement (equivalently: measurement in the X-basis relative to the diagonal layer).

For each candidate scheme, here is the raw material an ENC-01 attempt would need to reason through — presented as open questions/starting points, not resolved claims:

**Dual rail:**
- *Ingredient 1 (`|+⟩` start):* `BS.H()` applied to each qubit's rail-0-occupied input state (`BasicState([1,0])`) — direct reuse of the exact component already verified in `perceval_fluency_demo.py`.
- *Ingredient 2 (Z-diagonal layer):* single-qubit-generator terms → `PS` on rail 1, straightforward (see gate catalog above). Multi-qubit-generator terms (weight-≥2 `gⱼ`) → open problem, needs either chained heralded/post-selected CZ-style gates (probabilistic, success-probability cost compounds with generator count) or an explicit scope decision to only demonstrate weight-1 generators in the worked example (a real, statable limitation, not a thing to hide).
- *Ingredient 3 (Hadamard-conjugated measurement):* `BS.H()` again per qubit, then photon-counting (`Analyzer` / `Processor` with a `Detector`) reading out which rail the photon is in.
- *Commutativity check owner will need to do:* do the chosen realization(s) of the multi-qubit diagonal terms actually commute with each other in the same way the qubit-side `MultiRZ` terms do? This is exactly the "preserves IQP's structural properties" claim CONTEXT.md asks ENC-01 to argue at equation level, not assert.

**QUDIT/one-hot:**
- *Ingredient 1:* the qubit-side `|+⟩^⊗n` state is, in this basis, an **equal superposition of a single photon across all `2^n` modes** — realizable via a single `2^n`-mode balanced multiport (a generalized Hadamard/DFT-like mesh) fed a photon in mode 0, or equivalently by construction directly as the input `StateVector`.
- *Ingredient 2:* trivial by construction (see survey above) — one `PS` per mode, values set by the diagonal phase the generator layer assigns to each bitstring. Owner still needs to write out, per generator `gⱼ`, exactly which per-mode phase results — an explicit, checkable calculation, not hand-waved.
- *Ingredient 3:* the `H^⊗n` conjugation is a full `2^n×2^n` unitary — realizable via `pcvl.Unitary` (drop in the matrix directly) or `pcvl.GenericInterferometer` (decompose into beamsplitters/phase shifters). For n=2-3 this is a concrete, buildable circuit; whether/how the doc states a general-n claim about this is exactly where the "closer to Douce et al.'s equation-level rigor" bar matters — an exponential-resource claim dressed as if it were efficient would be the kind of overclaim CONTEXT.md's tone constraint explicitly warns against.

**Single-rail / polarization:** raw material is a hybrid of dual rail's (borrow a reference mode for anything Hadamard-like) and the no-go theorem's warning (deterministic entangling + bunching suppression can't both hold under passive optics) — an owner attempt here would need to decide up front whether "passive-only" is even the constraint being kept, since relaxing it (allowing post-selection/ancillas) reopens design space at the cost of the same non-determinism dual rail has.

## Basis Correspondence — What ENC-03 Could Concretely Say, Per Scheme

CONTEXT.md requires ENC-03 to be falsifiable, not a hand-wavy analogy — i.e., given a bitstring like `"011"`, the mapping must name a specific `BasicState`/Fock outcome, not just gesture at "the photon encodes the bit somehow."

| Scheme | `"011"` (n=3) maps to | General rule |
|---|---|---|
| Dual rail | `BasicState([1,0, 0,1, 0,1])` (rail pairs, one photon per pair, `[1,0]`=0, `[0,1]`=1) | Already Perceval's own documented convention (`port.py:_to_fock`, `DUAL_RAIL` branch) — not something to derive, just cite and demonstrate |
| Single-rail (RAW) | `BasicState([0,1,1])` (each mode's occupation number IS the bit) | Also Perceval's documented convention (`RAW` branch) |
| QUDIT (one-hot) | `BasicState([0,0,0,1,0,0,0,0])` — single photon in mode `int("011",2) = 3` of 8 modes | Perceval's documented convention (`QUDIT*` branch: `photon_pos = Σ bit·2^idx`) |
| Polarization | `|H,V,V⟩` in Perceval's `{P:H}`/`{P:V}` per-mode annotation syntax, one polarized photon per qubit-mode | Documented via `StateGenerator`'s default `polarization_base` |

**What still needs owner work for ENC-03**, regardless of scheme: stating this correspondence is necessary but not sufficient — ENC-03 also needs the *reverse* direction stated (given a measured photon-count outcome, which classical bitstring, if any, does it correspond to, and what happens to outcomes that fall outside the computational subspace — e.g. two photons bunched in one dual-rail pair, or zero photons in a rail pair due to loss/error in a real device model). That failure-mode question is exactly what makes a correspondence falsifiable rather than a slogan, and it's untouched by any of the rows above.

## Validation / Toy-Check Options (ENC-04) — n=2-3, Actually Runnable

CONTEXT.md requires Phase 9 to **actually run** a small comparison (not just describe a plan), comparing the Fock-outcome distribution from a hand-built Perceval circuit against the exact qubit-side IQP distribution, for n=2-3.

**Reference (qubit-side, ground truth) options:**
1. **Hand-derive directly** (simplest, most self-contained, no new dependency): for n=2-3, `|+⟩^⊗n → diagonal phase layer → H^⊗n → measure` is an 4×4 or 8×8 state-vector computation, doable by hand or in ~15 lines of plain `numpy` (no PennyLane/jax needed) — build the `2^n`-dim state vector directly, apply the diagonal phases from the chosen generator set, apply the `H^⊗n` matrix, take `|amplitude|²`. This avoids pulling in the sibling `iqp-mmd-barren-plateau` repo's heavier `iqpopt`/`jax`/PennyLane dependency chain (confirmed not installed in this repo's venv) purely to reproduce a computation that's trivial at n=2-3.
2. **Reuse `docs/iqp-baseline.md`'s Van den Nest cosine-formula trick**, available but not required by CONTEXT.md — it produces Z-word *expectation values* (`⟨Zₐ⟩ = E_z[cos(Φ(θ,z,a))]`), not a full output distribution, so it would need to be combined with something else (e.g. inverse-Fourier-transforming a full set of Z-word expectations back into a probability distribution) to serve as a full-distribution comparison target — more machinery than option 1 for the same n=2-3 scale. Better suited as a spot-check on individual expectation values than as the primary comparison method.
3. **Sibling repo's `IqpSimulator`** (`C:\Users\cuqui\iqp-mmd-barren-plateau\src\iqp_mmd\models\iqp_simulator.py`, built on `iqpopt`/PennyLane/jax): exists and is a working, tested exact-and-approximate IQP simulator, but pulling a cross-repo dependency chain into this repo purely for an n=2-3 sanity check is disproportionate — noted here for completeness/awareness, not as the recommended path.

**Photonic-side (Perceval) options, both already-verified patterns:**
- Build the chosen encoding's circuit for the n=2-3 worked example using `Circuit`/`BS`/`PS`/`PERM` per the mapping, wrap in `Processor("SLOS", circuit)`, and run `Analyzer(proc, [input_state], "*")` exactly as `perceval_fluency_demo.py` already does — `.distribution` gives the full output-state probability table directly, which is exactly the object to compare against the qubit-side reference distribution (after applying the ENC-03 basis correspondence to translate Fock outcomes back to bitstrings).
- **Comparison metric:** total variation distance or per-outcome absolute difference between the two probability tables is simplest and most defensible at this scale (n=2-3 has only 4-8 outcomes) — no need for anything fancier (MMD, KL) at toy scale; save that machinery for a future implementation-phase, larger-n validation.

**If the scheme chosen has probabilistic/heralded components (dual rail's multi-qubit gates):** the comparison needs to decide up front whether it's comparing (a) the *conditional* output distribution given successful heralding, or (b) something that accounts for the non-unit success probability — these are different claims, and CONTEXT.md's honesty requirement ("if the toy check reveals a mismatch... report it honestly") applies just as much to picking the wrong one of these two silently as to a numerical mismatch.

## Course Material Cross-Reference

The owner's course notes at `C:\Users\cuqui\quantum-information-material\quantum-physics-for-computer-scientists\lectures\` were checked directly (PDF page extraction — legible, mostly handwritten lecture notes with typed slide decks). Confirmed directly relevant content, by file:

- **`Note6QPh4CS-f.pdf`** ("Quantum Optical Field") — derives the quantized single-mode field, quadrature operators `x̂ = â†+â`, `p̂ = i(â†-â)`, `[x̂,p̂]=2i`, and explicitly notes convention choices differ across the course's own materials ("this definition is different by purpose of the one of TD8... we can use different conventions for quadrature operators") — a useful reminder to state whichever convention Phase 9's own document adopts explicitly, since even the owner's own course isn't uniform on this.
- **`Notes8QPh4CS.pdf`** (Jaynes-Cummings model) — derives the free-field Hamiltonian `H₀^field = ℏω(â†â + 1/2)`, i.e. the number operator `â†â` and its eigenstates (Fock states `|n⟩`) as the natural energy eigenbasis of a quantized field mode — directly the formalism Phase 9's photon-number measurement claims are built on.
- **`supplement-harmonic-oscillator.pdf`** — likely covers ladder-operator/Fock-state derivation for the quantum harmonic oscillator in more depth (file present but not machine-readable via this session's available PDF tooling — `pdftoppm`/poppler not installed, so only the two files above were actually opened; this one and the remaining files (`Note3QPh4CS.pdf`, `Note7QPh4CS.pdf`, `Notes4QPh4CS.pdf`, `Notes5QPh4CS.pdf`, `Notes-first-class1.pdf`, `Notes-second-class.pdf`, `Time-evolution-and-pictures*.pdf`) could not be opened this pass and should be checked directly by the owner at the point in ENC-01/writing where Fock-state notation is first introduced in the mapping document).

**Recommendation for the plan (not for this research doc to resolve):** point the owner to `Note6QPh4CS-f.pdf` and `Notes8QPh4CS.pdf` specifically at the point in `docs/iqp-photonic-encoding.md`'s drafting where Fock states / the number operator are first introduced, so the document's formalism is anchored in the owner's own already-internalized notation rather than a fresh derivation from scratch.

## Common Pitfalls

### Pitfall 1: Treating "Hadamard-basis conjugation" as if it were a native gate in every encoding
**What goes wrong:** assuming there's always a small fixed unitary that plays H's role, the way there is in dual rail (`BS.H()`) or in the qubit picture.
**Why it happens:** dual rail's convenient `BS.H()` echo (and its own catalog's H-sandwich CNOT construction) makes it easy to assume every DV encoding has an equally cheap conjugation gate.
**How to avoid:** explicitly check, per scheme, whether the conjugation operator is a small fixed local gate (dual rail: yes) or an exponentially-large global mesh (QUDIT one-hot: yes, but it's `2^n`-dimensional, not free) — and say which, out loud, in the doc.
**Warning sign:** a mapping section that states "apply Hadamard" without naming the actual Perceval component(s) and their mode-count/parameter-count scaling in n.

### Pitfall 2: Confusing "the mapping is checkable in principle" with "the toy check ran and passed"
**What goes wrong:** ENC-04 gets satisfied by a description of how a check *could* be done, rather than an actual executed comparison with a pass/fail (or an honestly-reported mismatch).
**Why it happens:** the other three requirements (ENC-01/02/03) are on-paper deliverables, and it's easy for ENC-04 to drift into the same register.
**How to avoid:** CONTEXT.md is explicit — code must actually run for n=2-3 and the comparison must actually execute, mirroring `perceval_fluency_demo.py`'s own PASS/FAIL assertion pattern.
**Warning sign:** the mapping doc's validation section has no numbers in it.

### Pitfall 3: Douce et al.'s own resolution to this exact problem is a warning, not a template to copy blindly
**What it shows:** in the CV case, Fourier-transform-as-Hadamard-analogue was realized not as a native gate but via a **measurement-based teleportation gadget**, post-selected on a specific homodyne outcome (`docs/iqp-lit-scoping.md`). The DV/Fock-space analogue of "conjugation via measurement-based gadget rather than a native unitary" is exactly what dual rail's heralded/post-selected CZ gates already are — non-deterministic, success conditioned on an ancilla measurement outcome. **The pitfall is assuming DV automatically avoids this because it has a convenient `BS.H()` for the *single-qubit* conjugation** — that convenience only covers the Hadamard *gate*, not necessarily the multi-qubit entangling structure the middle layer needs, which (in dual rail) inherits the same "conjugation/entangling realized via measurement, not a native operation" character Douce et al.'s CV construction has. Whether this parallel is worth stating explicitly in ENC-02's positioning (as a point of *similarity* rather than pure contrast) is a judgment call for the owner, but the raw material for making that argument, if wanted, is here.
**How to avoid overclaiming either way:** state plainly which parts of the chosen DV scheme are deterministic/native (typically: single-qubit gates, in both dual rail and QUDIT) and which are not (typically: multi-qubit entangling structure, in dual rail; nothing, in QUDIT one-hot, at the cost of exponential modes) — this symmetric honesty is exactly what CONTEXT.md's tone constraint is asking for.

### Pitfall 4: Assuming a scheme's minimal per-qubit mode count implies it's cheaper overall
**What goes wrong:** single-rail's "1 mode per qubit" or QUDIT's "1 photon total" can look strictly cheaper than dual rail's "2 modes per qubit, n photons," until the hidden costs (single-rail's no-go-theorem-driven need for nonlinearity/post-selection; QUDIT's exponential mode count for entangling structure) are accounted for.
**How to avoid:** compare schemes on total resource cost for the *specific* n=2-3 worked example the mapping will actually build, not on asymptotic per-qubit mode count alone.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| Dual-rail single-qubit gates (H, S, T, Z, X, Rx, Ry, Rz) | Custom circuit derivations from scratch | `perceval.components.core_catalog.gates_1qubit` (`h`, `s`, `t`, `z`, `x`, `rx`, `ry`, `rz`, `ph` catalog items), or just cite/reuse their `BS`/`PS`/`PERM` definitions directly | Already implemented, tested, and shipped in the installed package — re-deriving from scratch risks a sign/convention mismatch with what Perceval actually simulates |
| Dual-rail 2-qubit entangling gates | A from-scratch heralded/post-selected CZ derivation | `heralded cz`/`postprocessed cz`/`heralded cnot`/`klm cnot` catalog items (`perceval/components/core_catalog/`) | These already encode the correct beamsplitter reflectivities (e.g. `BS.r_to_theta(1/3)`) and post-selection conditions from the KLM literature — a fresh derivation is exactly the kind of "custom simulation infrastructure" CONTEXT.md's constraint says to avoid |
| A `2^n×2^n` Hadamard-tensor-power unitary (QUDIT scheme) | Manual Reck/Clements decomposition by hand | `pcvl.Unitary(H_tensor_n)` (drop the matrix straight in) or `pcvl.GenericInterferometer` if an explicit beamsplitter-mesh decomposition is wanted for the write-up | Perceval already implements unitary decomposition; hand-deriving the mesh is unnecessary work for what the doc needs |
| Exact small-n IQP reference distribution | Pulling in the sibling repo's `iqpopt`/jax/PennyLane stack | ~15 lines of direct `numpy` state-vector simulation (see Validation section) | Simpler, self-contained, no new dependency in this repo's venv, and n=2-3 needs none of that stack's scale/training machinery |

**Key insight:** everything genuinely hard about this phase (multi-qubit entangling structure in a probabilistic-gate encoding, or exponential mode scaling in a deterministic one) is a *known, literature-documented* tradeoff, not a gap Phase 9 needs to invent a fix for. The honest move is naming which known tradeoff the chosen scheme inherits, not solving it.

## Open Questions

1. **Which scheme will the owner pick, and does the n=2-3 worked example need to exercise a weight-≥2 IQP generator?**
   - What we know: dual rail's difficulty is concentrated exactly in weight-≥2 generators; QUDIT one-hot has no difficulty there but an exponential-mode caveat instead.
   - What's unclear: whether ENC-01's "general n" statement needs to handle arbitrary generator weight, or whether the worked example can legitimately scope itself to weight-1 generators and state that scoping explicitly.
   - Recommendation: this is precisely an attempt-first question — let the owner's ENC-01 attempt surface which generator weights it needs to handle, then confront the gate-realization cost for that scheme honestly.

2. **How should ENC-03's basis correspondence handle Fock outcomes outside the computational subspace** (bunched photons in dual rail, non-single-photon outcomes elsewhere)?
   - What we know: Perceval's documented `Encoding` conventions define the *forward* map (bitstring → Fock state) cleanly; they say nothing about what to do with an observed Fock outcome that doesn't correspond to any valid logical bitstring.
   - What's unclear: whether the n=2-3 toy check will actually produce such outcomes with nonzero probability under the chosen circuit (idealized/lossless SLOS simulation may or may not populate them, depending on the circuit).
   - Recommendation: check empirically during the ENC-04 toy run rather than assume either way.

3. **Poppler/`pdftoppm` is not installed in this environment**, so only 2 of the owner's 12 course-material files were actually opened this pass (see Course Material Cross-Reference above). If deeper Fock-state/number-operator derivations turn out to matter for the equation-level rigor CONTEXT.md asks for, the owner should open the remaining files directly (their own PDF viewer, not this tooling) rather than relying on file-name inference of their contents.

## Sources

### Primary (HIGH confidence — read directly from installed source / repo files)
- `venv/Lib/site-packages/perceval/utils/_enums.py` — `Encoding` enum definition, `fock_length`/`logical_length`
- `venv/Lib/site-packages/perceval/components/port.py` — `_to_fock`, `get_basic_state_from_encoding` (the actual basis-correspondence conventions Perceval itself uses)
- `venv/Lib/site-packages/perceval/components/core_catalog/gates_1qubit.py` — dual-rail single-qubit gate circuits (H, S, T, Z, X, Y, Rx, Ry, Rz, phase)
- `venv/Lib/site-packages/perceval/components/core_catalog/{heralded_cnot,heralded_cz,postprocessed_cz,postprocessed_cnot,klm_cnot}.py` — dual-rail entangling gate circuits, herald/post-select conditions
- `venv/Lib/site-packages/perceval/utils/stategenerator.py` — `StateGenerator` per-encoding zero/one state conventions
- `venv/Lib/site-packages/perceval/components/generic_interferometer.py` — `GenericInterferometer` signature and cited decomposition literature (Reck 1994, Clements 2016, Fldzhyan 2020, per its own docstring)
- `C:\Users\cuqui\merlin-quantum-case-study\perceval_fluency_demo.py` — verified `Circuit`/`BS.H`/`PS`/`Processor`/`Analyzer` usage patterns, MZI closed-form derivation
- `C:\Users\cuqui\merlin-quantum-case-study\docs\iqp-lit-scoping.md` — Douce et al. (2017) full summary, CV Fourier-gadget realization of Hadamard-conjugation
- `C:\Users\cuqui\merlin-quantum-case-study\docs\iqp-baseline.md` — qubit-side IQP recipe, `MultiRZ` generator structure, Van den Nest cosine formula
- `C:\Users\cuqui\quantum-information-material\quantum-physics-for-computer-scientists\lectures\Note6QPh4CS-f.pdf`, `Notes8QPh4CS.pdf` — opened directly this pass, quadrature operators and field-quantization Hamiltonian confirmed
- `C:\Users\cuqui\iqp-mmd-barren-plateau\src\iqp_mmd\models\iqp_simulator.py` — sibling repo's exact IQP simulator (noted as available but not recommended for the n=2-3 toy check, per Validation section)

### Secondary (MEDIUM confidence — WebSearch, cross-checked against well-known literature)
- Kok, Munro, Nemoto, Ralph, Dowling, Milburn, "Linear optical quantum computing with photonic qubits," Rev. Mod. Phys. 79, 135 (2007) — standard LOQC review, dual-rail/single-rail/polarization terminology (existence and venue confirmed via search; specific content claims in this doc are drawn from the Perceval source code and general knowledge of KLM, not re-verified page-by-page against the paper itself this pass — owner should skim the actual paper before citing it directly in `docs/iqp-photonic-encoding.md`)
- Knill, Laflamme, Milburn (2001) KLM protocol — success-probability figures (1/9 post-selected, ~2/27 heralded variants) reported via WebSearch cross-referencing multiple secondary sources; exact numbers vary by construction in the literature and should be verified against whichever specific gate the owner ends up citing

### Tertiary (verified via one WebSearch + one WebFetch, single-source for the specific claim)
- Wu, Walther, Lidar, "No-go theorem for passive single-rail linear optical quantum computing," Sci. Rep. 3, 1394 (2013), arXiv:1107.4646 — no-go result summarized via WebFetch of the PMC-hosted version; the specific claim (passive linear optics can't simultaneously give deterministic entangling gates and bunching suppression for single-rail) is drawn from that one fetch and should be treated as a strong lead to verify against the abstract/paper directly if the owner picks single-rail and needs to cite this precisely.

## Metadata

**Confidence breakdown:**
- Perceval API inventory (Standard Stack section): HIGH — read directly from installed `perceval-quandela==1.2.4` source, not from training-data assumptions about Perceval's API (which the project's own CLAUDE.md/Phase 8 gotchas already flagged as unreliable without verification).
- Encoding-scheme survey and tradeoffs: MEDIUM — synthesizes standard LOQC theory (Kok et al., KLM, single-rail no-go) that is well-established in the field but was verified this pass via WebSearch/WebFetch rather than a full paper read; good enough to hand to the owner as real options, not yet at the rigor bar the final `docs/iqp-photonic-encoding.md` itself needs to hit.
- IQP-correspondence raw material: MEDIUM — grounded in verified facts about both IQP's structure (`docs/iqp-baseline.md`) and Perceval's primitives, but the correspondences themselves are framed as open questions for the owner's attempt, deliberately not resolved claims.
- Validation/toy-check options: MEDIUM-HIGH — grounded in this repo's own verified, working code patterns (`perceval_fluency_demo.py`) and a straightforward, low-risk numpy alternative to the sibling repo's heavier dependency stack.

**Research date:** 2026-08-05
**Valid until:** ~30 days (Perceval/MerLin versions are pinned in this repo's venv and unlikely to drift; the LOQC-theory survey is stable, textbook-level material unlikely to become stale on this timescale)
