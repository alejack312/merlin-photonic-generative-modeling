# Phase 8 Literature Scoping: Douce et al. (2017), Search for a DV/Fock-Space Construction, and the Go/No-Go Verdict

Grounded in a full-text read of Douce et al., "Continuous-Variable Instantaneous Quantum Computing is hard to sample," Phys. Rev. Lett. 118, 070503 (2017), arXiv:1607.07605 — read completely (not abstract-level) during this repo's Phase 8 research pass and recorded in `.planning/phases/08-literature-scoping-prerequisites/08-RESEARCH.md`'s LIT-02 section. This document re-derives that summary in different words rather than copy-pasting it, and adds a second, independently-conducted literature search pass (LIT-01) plus the owner's own go/no-go verdict (LIT-04) on top of it.

## Douce et al. (2017) — CV-IQP Hardness Construction

**Full citation:** T. Douce, D. Markham, E. Kashefi, E. Diamanti, T. Coudreau, P. Milman, P. van Loock, G. Ferrini, "Continuous-Variable Instantaneous Quantum Computing is hard to sample," Phys. Rev. Lett. 118, 070503 (2017), arXiv:1607.07605.

### The DV-IQP starting point

The paper opens from the standard discrete-variable IQP recipe: every qubit starts in the `|+⟩` state (the +1 eigenstate of X), a layer of gates that are all diagonal in the Z-basis is applied, and the final measurement is done in the X-basis. Because every gate in that middle layer is Z-diagonal, they all commute with each other — there's no fixed order they need to be applied in, which is where the name "instantaneous" comes from. Classical simulation of the output distribution of this circuit family, under standard complexity assumptions, would collapse the polynomial hierarchy — that's the hardness result this paper is porting into a new physical substrate.

### The CV analogue, ingredient by ingredient

The paper swaps every DV ingredient for a continuous-quadrature counterpart:

- **Input state:** instead of qubits in `|+⟩`, each mode starts in a finitely-squeezed state, squeezed in the momentum quadrature `p̂`.
- **Gate layer:** instead of Z-diagonal qubit gates, the circuit applies gates diagonal in the *position* quadrature `q̂` — built from a small generating set `{Ẑ, ĈZ, T̂}` (all `q̂`-diagonal). These commute with each other for the identical structural reason the DV Z-diagonal gates commute — diagonal operators in the same basis always commute.
- **Measurement:** instead of X-basis measurement, the readout is finite-resolution **homodyne detection of `p̂`** — the quadrature conjugate to `q̂`, playing the same role X plays relative to Z in the DV case.

**What "Hadamard-basis conjugation" means here, stated explicitly:** in DV IQP, Hadamard gates conjugate the Z-diagonal gate layer into the X measurement basis (`H⊗ⁿ D H⊗ⁿ`). In this CV construction, that role is played by the **Fourier transform operator** `F̂ = e^{i(π/4)(p̂²+q̂²)}`, which sandwiches the `q̂`-diagonal gate layer the same way Hadamards sandwich the Z-diagonal layer. Crucially, this Fourier operator is not applied as a literal built-in gate — it's implemented via a **measurement-based gadget**: a `ĈZ`-based teleportation-like circuit, post-selected on a specific homodyne outcome, that effectively applies the Fourier transform to an unknown input state. So "Hadamard-basis conjugation" in this paper is realized through post-selected measurement, not a native unitary.

### The hardness argument, in four steps

1. **Fourier gadget → universality.** Adding post-selection to the realistic (finite-squeezing, finite-resolution) CV-IQP class — the paper calls this class "CVrIQP" — makes the Fourier gadget above enough to reach a universal gate set, giving `CVrMBQC ⊆ PostCVrIQP`.
2. **GKP error correction closes the gap.** Gottesman-Kitaev-Preskill encoding of a logical qubit into an oscillator mode corrects the errors introduced by finite squeezing and finite homodyne resolution (this piece leans on prior GKP results, not new here), yielding `CVrMBQC = BQP` once resolution is high enough.
3. **Post-selection transfers hardness.** The same post-selection that defines the complexity class `PostBQP` maps directly onto the CV hardware described above, so `PostCVrIQP ⊇ PostBQP` — meaning this CV construction inherits the same polynomial-hierarchy-collapsing hardness argument that underlies the original DV IQP result.
4. **A genuinely new requirement versus the idealized DV case:** because real squeezing is always finite, the whole argument only goes through if the squeezing parameter scales at least logarithmically with circuit size, which translates into a polynomial scaling of input energy with circuit size. This scaling requirement — not the "port the DV argument over" part — is the paper's most novel quantitative contribution.

### Why this does NOT hand us a Fock-space/photon-number construction

This is the paragraph that matters most for positioning Phase 9, so it's stated plainly: everything above is built in the **continuous-quadrature** formalism — squeezed light, homodyne detection of `p̂`/`q̂`, GKP bosonic-qubit encoding. That is a different physical encoding from a **Fock-space/photon-number** linear-optical circuit — phase shifters, beamsplitters, and photon-counting detectors, which is what Perceval and MerLin actually simulate. The paper contains no mention anywhere of photon-number states, Fock-basis measurement, or discrete linear-optical networks; its notion of "continuous variable" is squarely the quadrature tradition (Menicucci, van Loock, GKP-style bosonic codes), not the (much less common, and unrelated) sense in which someone might loosely call "many photon-number levels" continuous. Concretely: this paper's `q̂`/`p̂` are continuous real-valued operators with no discrete eigenspectrum, whereas Fock-space encodings work entirely with discrete photon-count eigenstates `|0⟩, |1⟩, |2⟩, ...`. **These are two different formalisms that happen to share the word "continuous-variable photonics" as an umbrella term, and they must not be conflated in either direction** — a DV/Fock-space IQP analogue is not something this paper already proves, disproves, or even gestures at; it would have to be built from scratch, which is exactly Phase 9's job.
