# IQP → Photonic (DV/Fock-Space) Encoding

This document is a design/mapping deliverable, checkable in principle at small scale (n=2-3) — it is not a peer-review-grade hardness proof. The goal is a defensible, on-paper correspondence between IQP's structure and Perceval's discrete-variable (Fock-space) primitives, rigorous enough to state and check, not a claim of a new complexity-theoretic result.

**Contents:** ENC-01 (ingredient-level mapping) · ENC-02 (positioning against Douce et al.) · ENC-03 (basis correspondence) · ENC-04 (validation plan + toy check)

<!-- ENC-02 inserted here by 09-04 -->

## ENC-01: Ingredient-Level Mapping

### Owner's Attempt

Scheme chosen: **polarization encoding** (H/V), per the owner's coursework at Sorbonne — one photon per qubit, one spatial mode, polarization degree of freedom carries the qubit basis states (`|0⟩ = |H⟩`, `|1⟩ = |V⟩`).

This is a correction to `09-RESEARCH.md`'s and `09-01-PLAN.md`'s characterization of polarization encoding as having "no polarization-specific gate catalog — derive gates from scratch by analogy." That's inaccurate: `perceval-quandela==1.2.4` ships real polarization primitives, confirmed by reading the installed source directly (not assumed from the survey doc):

- `HWP(xsi)`, `QWP(xsi)` — half/quarter wave plates
- `PR(delta)` — polarization rotator
- `WP(delta, xsi)` — general two-parameter wave plate; `HWP(xsi)` is literally `WP(delta=π/2, xsi)` (confirmed from `WP.__init__` source)
- `PBS()` — polarizing beam splitter, converts a polarization superposition in one spatial mode into the same superposition spread across two spatial modes, and back (the bridge to dual rail)

Q&A walkthrough, piece by piece:

**1. `|+⟩` state prep.** Owner's initial guess was a beamsplitter at 45°. Corrected via `WP`'s actual unitary (read from `WP._compute_unitary` source):

```
U(delta, xsi) = [[cos(delta) + i·sin(delta)·cos(2·xsi),   i·sin(delta)·sin(2·xsi)],
                 [i·sin(delta)·sin(2·xsi),                 cos(delta) - i·sin(delta)·cos(2·xsi)]]
```

At `delta = π/2` (the `HWP` case), this reduces to `i·[[cos(2·xsi), sin(2·xsi)], [sin(2·xsi), -cos(2·xsi)]]` — up to the irrelevant global phase `i`, the standard reflection-about-axis-`xsi` Jones matrix. A half-wave plate rotates linear polarization by **twice** its physical axis angle. Starting from `|H⟩` (0°), landing on diagonal `(|H⟩+|V⟩)/√2` (45°) requires the plate's optical axis at **22.5°**, i.e. `HWP(xsi=π/8)` — not 45°, which was the owner's first guess and a classic wave-plate half-angle gotcha.

**2. Weight-1 diagonal generator.** `PR(delta)` or `WP(delta, xsi)` applies a phase between `H` and `V` on a single photon — the polarization analogue of `PS` on one rail of dual rail. (Exact parameter correspondence to `θ` in the qubit-side `MultiRZ(2θ, ...)` — Task 2.)

**3. Weight-≥2 diagonal generator.** Owner initially proposed CNOT/CZ/SWAP as "how multi-qubit circuits are built" generically. Corrected: IQP's middle layer is *defined* to be diagonal in the Z basis — that's the acronym's premise, and what makes the circuit commute pairwise despite being classically hard to sample (Bremner-Jozsa-Shepherd; Douce et al.'s CV analogue). Of the three gates named:
   - **CNOT** — not Z-diagonal. Never appears in an IQP middle layer.
   - **SWAP** — not Z-diagonal either. Same conclusion.
   - **CZ** — `diag(1, 1, 1, −1)`. **Is** Z-diagonal, and a legitimate stand-in for IQP's generic weight-2 generator `exp(iθ·Z_i·Z_j) = diag(e^{iθ}, e^{-iθ}, e^{-iθ}, e^{iθ})` (CZ is a specific instance of that family up to single-qubit Z corrections).

   Owner picked the **heralded** construction (over post-selected) for the two-qubit gate.

   Mechanism, as sketched: each of the two polarization photons (qubits `i`, `j`) passes through its own `PBS`, converting polarization → two spatial modes per photon (4 modes total) — this is what "H/V splits onto a spatial mode" means: the photon's former polarization state now determines which of two paths it's found in. `core_catalog.heralded_cz` (built for dual rail) acts on those 4 modes plus ancilla herald mode(s); the gate is accepted only when a specific detector click pattern fires on the heralds (heralding — confirming success without measuring the data photons themselves, as opposed to post-selection, which checks an acceptance condition on the data-mode measurement after the fact). Each qubit's 2 modes then pass back through a `PBS` to return to polarization encoding. Same probabilistic success-probability cost as dual rail's native heralded CZ — polarization → `PBS` → dual rail → `PBS` → polarization doesn't dodge KLM, it inherits it via a lossless conversion.

**4. Hadamard-conjugated measurement.** Same component family as (1) — `HWP` at the angle realizing Hadamard on the polarization basis (Task 2: confirm exact angle from the same matrix above).

### Chosen scheme and why it fits Perceval's native primitives

**Polarization encoding**: one photon per qubit, one spatial mode, the qubit basis carried by the photon's polarization (`|0⟩ = |H⟩`, `|1⟩ = |V⟩`). Contrary to `09-RESEARCH.md`'s survey (corrected above, in the Owner's Attempt section, after direct inspection of the installed `perceval-quandela==1.2.4` source), Perceval ships a complete polarization gate set, not just the `Encoding.POLARIZATION` enum value:

- `pcvl.WP(delta, xsi)` — a general two-parameter wave plate acting on one spatial mode's polarization DOF
- `pcvl.HWP(xsi)` — `WP(delta=π/2, xsi)` (confirmed from `HWP.__init__`'s source: `super().__init__(sp.pi/2, xsi)`)
- `pcvl.PBS()` — converts a polarization superposition on one spatial mode into the same superposition spread across two spatial modes, and back

That's sufficient to realize all three IQP ingredients with exact (not approximate) native components, with no custom gate derivation needed — matching this project's "use MerLin/Perceval's existing native primitives" constraint as well as dual rail does, just via a different component family.

### Ingredient 1: `|+⟩^⊗n` state preparation

`WP`'s unitary, read directly from `perceval/components/unitary_components.py`'s `WP._compute_unitary`:

```
U(δ, ξ) = [[cos(δ) + i·sin(δ)·cos(2ξ),   i·sin(δ)·sin(2ξ)          ],
           [i·sin(δ)·sin(2ξ),             cos(δ) − i·sin(δ)·cos(2ξ)]]
```

At `δ = π/2` (`HWP`'s fixed value), this reduces to:

```
U(π/2, ξ) = i · [[cos(2ξ), sin(2ξ)], [sin(2ξ), −cos(2ξ)]]
```

Up to the global phase `i` (unobservable — global phase never affects measurement probabilities), this is the standard Jones reflection-about-axis-`ξ` matrix. A half-wave plate rotates linear polarization by **twice** its physical axis angle. Starting from `|H⟩` (polarization angle 0°), landing on `|+⟩ = (|H⟩+|V⟩)/√2` (45°) requires `2ξ = 45°`, i.e. `ξ = π/8` (22.5°) — confirmed both symbolically above and numerically (`HWP(π/8).compute_unitary()` gives `i·(1/√2)[[1,1],[1,-1]]`, matching `i·Hadamard` to floating-point precision).

For `n` qubits, each qubit's photon occupies its own spatial mode (with an adjacent vacuum "partner" mode reserved for the readout step — see Ingredient 3), and `HWP(π/8)` is applied independently to each qubit's polarization mode. Since `WP`/`HWP` are single-spatial-mode components (`hwp.m == 1`, confirmed empirically — no cross-mode coupling), applying `HWP(π/8)` to `n` independent modes realizes exactly the tensor product `H^⊗n`, matching the qubit-side `|+⟩^⊗n = H^⊗n|0⟩^⊗n` construction mode-by-mode, not just in aggregate effect.

`build_state_prep_circuit(n)` in `iqp_photonic_encoding.py` implements this: `HWP(π/8)` at port `2k` for each qubit `k` (even ports carry polarization, odd ports are vacuum-partner modes, untouched here).

### Ingredient 2: Z-diagonal middle layer

At `ξ = 0`, `WP`'s unitary reduces to:

```
U(δ, 0) = [[cos(δ) + i·sin(δ), 0], [0, cos(δ) − i·sin(δ)]] = diag(e^{iδ}, e^{-iδ})
```

— confirmed numerically (`WP(π/3, 0).compute_unitary()` gives `diag(e^{iπ/3}, e^{-iπ/3})` to floating-point precision). This is **exact**, not an approximation: `WP(θ, 0)` realizes `exp(iθZ)` on the polarization qubit, the same role `PS` plays for a single-qubit generator in dual rail, with no additional interference partner needed for the *phase itself* to be well-defined (though, as in dual rail, that phase is only *observable* after a subsequent basis change — see Ingredient 3).

For a weight-1 IQP generator `g_j` touching only qubit `k` with angle `θ_j`, the photonic realization is `WP(θ_j, 0)` on qubit `k`'s polarization mode. `build_diagonal_layer_circuit(n, thetas)` implements this directly: `WP(thetas[k], 0)` at port `2k` for each qubit `k` (`thetas[k] = 0` realizes the identity, for qubits untouched by any weight-1 generator).

**Weight-≥2 generators — stated scope limitation.** IQP's middle layer can include generators touching two or more qubits, e.g. `exp(iθ·Z_i·Z_j)`. This module implements and tests **weight-1 generators only**; the weight-2 case is derived on paper here but not built/tested as runnable code in this plan. The mechanism, following the owner's Task 1 attempt:

1. Each of the two qubits' polarization photons passes through its own `PBS`, converting polarization → two plain spatial modes per photon (4 modes total) — dual rail's representation.
2. `perceval.components.core_catalog.heralded_cz` acts on those 4 modes plus ancilla herald mode(s), succeeding (confirmed by a specific detector click pattern on the heralds) only some fraction of the time — a real, literature-known probabilistic cost (`09-RESEARCH.md` cites commonly-quoted figures like 1/9 for a post-selected construction and ~2/27 for a heralded variant, flagged there as needing verification against the specific gate cited, not treated as settled here either).
3. Each qubit's 2 modes convert back to polarization via `PBS`.

The operator-identity connecting this to IQP's generic weight-2 generator: writing `Z_i`, `Z_j`, `Z_iZ_j` eigenvalues on the four computational basis states `{|00⟩,|01⟩,|10⟩,|11⟩}` as `(1,1,-1,-1)`, `(1,-1,1,-1)`, `(1,-1,-1,1)` respectively, direct calculation gives:

```
I − Z_i − Z_j + Z_iZ_j = diag(0, 0, 0, 4)
⟹ exp(i·(π/4)·(I − Z_i − Z_j + Z_iZ_j)) = diag(1, 1, 1, e^{iπ}) = diag(1,1,1,−1) = CZ
```

Since `I, Z_i, Z_j, Z_iZ_j` all commute (all diagonal in the same basis), the exponential of their sum factors:

```
CZ = e^{iπ/4}·exp(−iπ/4·Z_i)·exp(−iπ/4·Z_j)·exp(iπ/4·Z_iZ_j)
⟹ exp(iπ/4·Z_iZ_j) = CZ · exp(iπ/4·Z_i) · exp(iπ/4·Z_j)   (up to the global phase e^{-iπ/4})
```

So `heralded_cz`, corrected by two single-qubit `WP(π/4, 0)` gates (already available from Ingredient 2), realizes `exp(iθZ_iZ_j)` **at the fixed angle `θ = π/4`** — not a continuously-tunable angle, since the catalog's `heralded_cz` is a fixed gate, not a parameterized family. Realizing an arbitrary-`θ` two-qubit diagonal phase gate from this catalog alone is not resolved here; that gap is named explicitly rather than glossed over, per this document's tone constraint.

### Ingredient 3: Hadamard-conjugated measurement

`build_conjugation_circuit(n)` applies the same `HWP(π/8)` as state prep (Hadamard is self-inverse, so the same gate realizes both ends of the `H`-diagonal-`H` sandwich). `build_readout_circuit(n)` then applies `PBS` per qubit, converting the polarization state into a which-path spatial state so `Analyzer`/`Processor.probs()` can resolve it — a bare polarized state is invisible to Fock-basis (photon-number) measurement without this conversion, confirmed empirically (an `Analyzer` run on a polarized `BasicState` with no `PBS` collapses to a single "photon present" outcome, never resolving `H` vs `V`), the polarization analogue of `perceval_fluency_demo.py`'s finding that a bare `PS` needs a second beamsplitter to become visible.

### Commutativity and conjugation-symmetry, argued at equation level

**Commutativity.** IQP's structural property is that every middle-layer generator commutes with every other, because all are diagonal in the same (Z) basis. In this photonic realization: each weight-1 generator `WP(θ_k, 0)` acts on a *distinct* qubit's own single mode; operators on disjoint tensor factors commute trivially (`[A⊗I, I⊗B] = 0` for any `A, B`). Two generators on the *same* qubit (different `θ` values) are both exactly diagonal in that qubit's `{H,V}` basis (`WP(θ,0) = diag(e^{iθ}, e^{-iθ})`), and diagonal matrices always commute with each other regardless of angle. This is the same structural argument as the qubit-side proof (`Z_i` and `Z_j` commute trivially for `i≠j`; two Z-diagonal operators on the same qubit commute because diagonal matrices commute) — preserved exactly, not just informally echoed, because `WP(θ,0)`'s unitary *is* diagonal in the `{H,V}` computational basis, not merely "phase-like" in some looser sense. The weight-2 case (Ingredient 2's derivation) inherits the same property *conditional on successful heralding*: `heralded_cz` realizes `CZ`, an exactly-diagonal 4×4 matrix, so on the subspace where the herald succeeds, the resulting operation is diagonal in the joint computational basis and therefore commutes with all other diagonal-layer operations by the identical argument. This conditional caveat is real, not a technicality to bury: heralding failure leaks probability outside the two-qubit computational subspace entirely, so the *unconditional* physical process (including failure outcomes) is not a diagonal unitary on the qubit subspace alone.

**Conjugation symmetry.** IQP's measurement is in the Hadamard-conjugate (X) basis relative to the diagonal layer — equivalently, `H^⊗n` applied before computational-basis measurement. `HWP(π/8)` realizes Hadamard exactly (up to the unobservable global phase `i`) on each qubit's own two-level polarization space independently, with zero cross-mode coupling (confirmed: `hwp.m == 1`). Applying `HWP(π/8)` to all `n` qubit modes therefore realizes `H^⊗n` exactly, up to the global phase `i^n` — again mode-by-mode, matching the qubit-side tensor-product structure directly rather than merely reproducing its aggregate effect.

### n=2 worked example

Two qubits, weight-1 generators only: `θ₀ = 0.3`, `θ₁ = 1.1`, both qubits starting in `|H⟩ = |0⟩`. `iqp_photonic_encoding.py`'s `build_full_circuit(2, [0.3, 1.1])` builds the 4-mode circuit (`HWP(π/8)` ×2 → `WP(θ_k,0)` ×2 → `HWP(π/8)` ×2 → `PBS` ×2); running it through `Processor("SLOS", ...)` + `Analyzer` gives:

```python
from iqp_photonic_encoding import run_full_circuit, expected_joint_distribution

_, dist = run_full_circuit(n=2, thetas=[0.3, 1.1])
# {'|1,0,1,0>': 0.069364, '|1,0,0,1>': 0.017969,
#  '|0,1,1,0>': 0.724887, '|0,1,0,1>': 0.187781}

expected = expected_joint_distribution(n=2, thetas=[0.3, 1.1])
# {'HH': 0.187781, 'HV': 0.724887, 'VH': 0.017969, 'VV': 0.069364}
```

(Bitstring labels use the verified convention `H=(0,1)`, `V=(1,0)` — see the port↔polarization correction below. The raw Perceval output above is unchanged by that correction; only which label attaches to which outcome changed.)

These match to floating-point precision (`tests/test_iqp_photonic_encoding.py`'s parametrized product-distribution test, which also checks `n=3` with three independent generators). Two things this concretely confirms, not just for the marginal per-qubit phase-to-probability relationship but for the *joint* two- and three-qubit state:

1. **No spurious correlations.** The joint distribution factors exactly into the product of independent per-qubit marginals — direct empirical evidence that weight-1 generators don't entangle the photonic realization, consistent with the commutativity argument above (weight-1 generators are local operators; no shared mode, no interaction).
2. **No leakage outside the computational subspace.** Every one of the 9 (`n=2`) and 27 (`n=3`) enumerable bunched/lost-photon outcomes (e.g. `|2,0,0,0⟩`, `|0,0,0,0⟩`, ...) has exactly zero probability in this ideal, lossless `SLOS` simulation — answering one of `09-RESEARCH.md`'s open questions (whether the toy circuit would empirically populate out-of-subspace Fock outcomes) for this specific weight-1-only construction: it does not, under ideal simulation.

The per-qubit closed form underlying both: starting from `|H⟩`, `HWP(π/8)·WP(θ,0)·HWP(π/8)` gives (using the real Hadamard `Had = (1/√2)[[1,1],[1,-1]]`, with `HWP(π/8) = i·Had`, so the two `i` factors cancel to an overall `-1`, itself unobservable):

```
Had · diag(e^{iθ},e^{-iθ}) · Had = [[cos θ, i sin θ], [i sin θ, cos θ]]
```

giving `P(stay) = cos²θ`, `P(flip) = sin²θ` in the abstract `{index0, index1}` ordering. Which physical port is which required a direct check, not an assumption: a bare `PBS()` with no other gates, fed pure `|H⟩` or pure `|V⟩`, gives `H → (0,1)`, `V → (1,0)` (deterministically, to floating-point precision). Combining that with the abstract result above: **`P(H) = cos²θ`, `P(V) = sin²θ`.**

*Correction (Plan 09-02):* an earlier version of this document and `iqp_photonic_encoding.py` had this port↔polarization assignment backwards — self-consistent within its own labels (so no numerical test result was ever wrong), but the "H"/"V" tags didn't match true physical polarization. Caught during the ENC-03 attempt-first checkpoint when the owner asked which output pair was really H, prompting the direct bare-`PBS` check above. Fixed in both the module and its tests (`tests/test_iqp_photonic_encoding.py`'s parametrized closed-form test now reads `H` from `BasicState([0,1])` and `V` from `BasicState([1,0])`); all 12 tests still pass, since the fix is a consistent relabeling, not a change to the underlying physics.

### Relation to the owner's Task 1 attempt

The final mapping follows the owner's attempt closely: polarization encoding was the owner's own choice (from personal coursework), the state-prep mechanism (a "diagonal beamsplitter"-type operation) correctly identified `WP`/`HWP` as the right primitive (the derivation above corrects only the specific angle — 22.5°, not the owner's initial 45° guess, or the beamsplitter framing — a wave plate, not a beamsplitter, is the correct component for polarization rotation), and the weight-2 mechanism (heralded `PBS`-mediated conversion to dual rail's `heralded_cz`) is exactly what Ingredient 2's weight-2 derivation formalizes, including the owner's choice of the heralded (not post-selected) construction.

### Status

ENC-01 is implemented and tested: `iqp_photonic_encoding.py` (state-prep/diagonal-layer/conjugation/readout circuit builders, weight-1 generators) and `tests/test_iqp_photonic_encoding.py` (12 tests, all passing) — `python -c "import iqp_photonic_encoding"` and `pytest tests/test_iqp_photonic_encoding.py -v` both verified clean.

### Self-Explanation Checkpoint (Task 3)

Per this repo's CLAUDE.md self-explanation checkpoints, the owner was asked to explain, unaided: (1) why the photonic realization of the diagonal layer actually commutes, and (2) what Hadamard-conjugation is physically doing and what the weight-2 case costs. Full Q&A recorded below, following this project's established pattern of documenting the actual back-and-forth rather than only the polished result.

*Note (added in Plan 09-02):* the `P(H)`/`P(V)` labels quoted in this transcript use the port↔polarization convention believed correct at the time (`H=(1,0)`, `V=(0,1)`) — since corrected to `H=(0,1)`, `V=(1,0)` after direct verification (see Ingredient 1's "Correction" note above). The transcript is left as an accurate record of what was actually said; only the physics discussed (phase → population imbalance) is what matters here, and that reasoning is unaffected by which physical port carries which label.

**Round 1 — initial answers restated the qubit-side abstraction rather than the photonic mechanism**, and contained one physical misconception:
- Commutativity: initially restated "diagonal in the Z-basis, all pairwise commuting" without connecting it to the actual `WP` construction — flagged as not yet meeting the bar, since it doesn't distinguish *why this specific realization* inherits the property.
- Hadamard-conjugation: initially described as "taking the states out of superposition and back into one polarization" — corrected: the second `HWP` does not collapse the state; it converts an invisible relative phase into an observable population difference (`P(H)=sin²θ`, `P(V)=cos²θ`) via interference. The state remains a superposition for general `θ`.
- Cost clarification: the single-qubit conjugation step itself is free (deterministic, native `HWP`, no ancillas); "cost" refers to the weight-2 case sitting *inside* the diagonal layer between the two conjugation layers.

**CZ-vs-ZZ question, verified against Perceval's actual source (not repeated from the secondhand literature figure):** `perceval.components.core_catalog.heralded_cz` implements the **Knill CZ gate** (arXiv:quant-ph/0110144, Knill 2002) — 4 data modes (2 dual-rail qubits) + 2 herald modes, success conditioned on exactly 1 photon in *each* herald mode (`add_herald(4,1)`, `add_herald(5,1)`). The mechanism is confirmed real and exactly as sketched in the owner's original attempt. The specific success probability was **not** independently recomputed from this circuit — the 1/9 (post-selected KLM) and ~2/27 (heralded variant) figures cited earlier in this document and in `09-RESEARCH.md` are secondhand literature citations for the same general gate family, not a verified property of this exact implementation. Flagged explicitly as assumed, not verified, per this repo's standing distinction between the two.

**Round 2 — final answers, correct:**
- *"The CZ is a special instance of the ZZ gate when the ZZ-dial is set to pi/4 and there is a small correction applied to every qubit."* — correct, matches the operator identity derived above (`exp(iπ/4·Z_iZ_j) = CZ · exp(iπ/4·Z_i) · exp(iπ/4·Z_j)` up to global phase).
- *"The operators on different qubits' modes automatically commute because the gates are 1-mode components that have no way to touch the other qubit's mode. If it is the same qubit, they commute because they are diagonal matrices in the same fixed basis."* — correct, and correctly distinguishes the two different reasons (disjoint tensor factors vs. diagonal-matrix multiplication) rather than conflating them.
- *"The hadamard-conjugation makes the invisible phase convert into a visible difference, like `|+⟩` converting into `|0⟩` or `|1⟩`."* — the core mechanism (phase → visible population difference) is correct; the closing analogy overstates it into a deterministic collapse. The corrected version: the post-conjugation state is `α|H⟩+β|V⟩` with `|α|²=sin²θ`, `|β|²=cos²θ` — a superposition with unequal weights, not a collapse to a single definite state, except at the special angles `θ=0` or `θ=π`.
