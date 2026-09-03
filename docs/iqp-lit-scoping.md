# Phase 8 Literature Scoping: Douce et al. (2017), Search for a DV/Fock-Space Construction, and the Go/No-Go Verdict

Grounded in a full-text read of Douce et al., "Continuous-Variable Instantaneous Quantum Computing is hard to sample," Phys. Rev. Lett. 118, 070503 (2017), arXiv:1607.07605, read completely (not abstract-level) during this repo's Phase 8 research pass and recorded in `.planning/phases/08-literature-scoping-prerequisites/08-RESEARCH.md`'s LIT-02 section. This document re-derives that summary in different words rather than copy-pasting it, and adds a second, independently-conducted literature search pass (LIT-01) plus the owner's own go/no-go verdict (LIT-04) on top of it.

## Douce et al. (2017) — CV-IQP Hardness Construction

**Full citation:** T. Douce, D. Markham, E. Kashefi, E. Diamanti, T. Coudreau, P. Milman, P. van Loock, G. Ferrini, "Continuous-Variable Instantaneous Quantum Computing is hard to sample," Phys. Rev. Lett. 118, 070503 (2017), arXiv:1607.07605.

### The DV-IQP starting point

The paper opens from the standard discrete-variable IQP recipe: every qubit starts in the `|+⟩` state (the +1 eigenstate of X), a layer of gates that are all diagonal in the Z-basis is applied, and the final measurement is done in the X-basis. Because every gate in that middle layer is Z-diagonal, they all commute with each other: there's no fixed order they need to be applied in, which is where the name "instantaneous" comes from. Classical simulation of the output distribution of this circuit family, under standard complexity assumptions, would collapse the polynomial hierarchy: that's the hardness result this paper is porting into a new physical substrate.

### The CV analogue, ingredient by ingredient

The paper swaps every DV ingredient for a continuous-quadrature counterpart:

- **Input state:** instead of qubits in `|+⟩`, each mode starts in a finitely-squeezed state, squeezed in the momentum quadrature `p̂`.
- **Gate layer:** instead of Z-diagonal qubit gates, the circuit applies gates diagonal in the *position* quadrature `q̂`, built from a small generating set `{Ẑ, ĈZ, T̂}` (all `q̂`-diagonal). These commute with each other for the identical structural reason the DV Z-diagonal gates commute: diagonal operators in the same basis always commute.
- **Measurement:** instead of X-basis measurement, the readout is finite-resolution **homodyne detection of `p̂`**, the quadrature conjugate to `q̂`, playing the same role X plays relative to Z in the DV case.

**What "Hadamard-basis conjugation" means here, stated explicitly:** in DV IQP, Hadamard gates conjugate the Z-diagonal gate layer into the X measurement basis (`H⊗ⁿ D H⊗ⁿ`). In this CV construction, that role is played by the **Fourier transform operator** `F̂ = e^{i(π/4)(p̂²+q̂²)}`, which sandwiches the `q̂`-diagonal gate layer the same way Hadamards sandwich the Z-diagonal layer. Crucially, this Fourier operator is not applied as a literal built-in gate; it's implemented via a **measurement-based gadget**: a `ĈZ`-based teleportation-like circuit, post-selected on a specific homodyne outcome, that effectively applies the Fourier transform to an unknown input state. So "Hadamard-basis conjugation" in this paper is realized through post-selected measurement, not a native unitary.

### The hardness argument, in four steps

1. **Fourier gadget → universality.** Adding post-selection to the realistic (finite-squeezing, finite-resolution) CV-IQP class — the paper calls this class "CVrIQP" — makes the Fourier gadget above enough to reach a universal gate set, giving `CVrMBQC ⊆ PostCVrIQP`.
2. **GKP error correction closes the gap.** Gottesman-Kitaev-Preskill encoding of a logical qubit into an oscillator mode corrects the errors introduced by finite squeezing and finite homodyne resolution (this piece leans on prior GKP results, not new here), yielding `CVrMBQC = BQP` once resolution is high enough.
3. **Post-selection transfers hardness.** The same post-selection that defines the complexity class `PostBQP` maps directly onto the CV hardware described above, so `PostCVrIQP ⊇ PostBQP`, meaning this CV construction inherits the same polynomial-hierarchy-collapsing hardness argument that underlies the original DV IQP result.
4. **A genuinely new requirement versus the idealized DV case:** because real squeezing is always finite, the whole argument only goes through if the squeezing parameter scales at least logarithmically with circuit size, which translates into a polynomial scaling of input energy with circuit size. This scaling requirement — not the "port the DV argument over" part — is the paper's most novel quantitative contribution.

### Why this does NOT hand us a Fock-space/photon-number construction

This is the paragraph that matters most for positioning Phase 9, so it's stated plainly: everything above is built in the **continuous-quadrature** formalism: squeezed light, homodyne detection of `p̂`/`q̂`, GKP bosonic-qubit encoding. That is a different physical encoding from a **Fock-space/photon-number** linear-optical circuit: phase shifters, beamsplitters, and photon-counting detectors, which is what Perceval and MerLin actually simulate. The paper contains no mention anywhere of photon-number states, Fock-basis measurement, or discrete linear-optical networks; its notion of "continuous variable" is squarely the quadrature tradition (Menicucci, van Loock, GKP-style bosonic codes), not the (much less common, and unrelated) sense in which someone might loosely call "many photon-number levels" continuous. Concretely: this paper's `q̂`/`p̂` are continuous real-valued operators with no discrete eigenspectrum, whereas Fock-space encodings work entirely with discrete photon-count eigenstates `|0⟩, |1⟩, |2⟩, ...`. **These are two different formalisms that happen to share the word "continuous-variable photonics" as an umbrella term, and they must not be conflated in either direction**: a DV/Fock-space IQP analogue is not something this paper already proves, disproves, or even gestures at; it would have to be built from scratch, which is exactly Phase 9's job.

## Literature Search (LIT-01)

### Starting point: 08-RESEARCH.md's existing WebSearch pass

`.planning/phases/08-literature-scoping-prerequisites/08-RESEARCH.md` already ran a WebSearch-based scan before this document was written. For reference, its query list and findings:

**Direct keyword queries tried:**
- `IQP linear optics boson sampling discrete variable photonic`
- `"instantaneous quantum polynomial" linear optical circuit photon counting hardness`
- `linear optical circuit commuting phase gates sampling hardness photon number basis "IQP"`

**Structural-analogue queries tried:**
- Commuting-diagonal-gates and Hadamard-conjugation framing (via the Douce et al. read itself, which cites the DV IQP definition it builds from; no separate DV-linear-optics paper cited there)
- Boson sampling / Gaussian boson sampling adjacency

**What it surfaced:** boson sampling and Gaussian boson sampling papers (permanent-based hardness, structurally different from IQP's commuting-diagonal-gate argument); Jabbour & Novo (arXiv:2310.06034, CV/Gaussian non-linearity-layering complexity, not DV/Fock); "Unified boson sampling" (PRR 7, L042068, merges DV scattershot + CV Gaussian boson sampling, no IQP connection); and standard qubit-native DV-IQP theory papers (Bremner-Jozsa-Shepherd lineage). None matched. That pass's own stated caveat: a single WebSearch scan is not exhaustive and doesn't by itself satisfy LIT-04's "cite both a constructive and a disconfirming search pass" bar: it explicitly recommended a follow-up pass with different phrasing and, ideally, citation-chasing.

### Independent second pass (this document, run 2026-08-03)

This repo's execution environment does not expose a WebSearch/WebFetch tool, so this second pass used a different, arguably stronger method than WebSearch: direct live queries against the **arXiv API** (`export.arxiv.org/api/query`) for keyword search, plus the **Semantic Scholar Graph API** for citation-chasing (pulling arXiv:1607.07605's actual citing-paper and cited-reference lists, the exact "what cites Douce et al." check `08-RESEARCH.md`'s Open Questions section flagged as worth doing but hadn't done). This is a genuinely different tool and a genuinely different query set from the first pass, not a restatement of it.

**1. Citation-chase: who cites Douce et al. (arXiv:1607.07605), and what does it itself cite?**

Queried Semantic Scholar for all citing papers (51 returned, spanning 2017-2026) and all references Douce et al. cites. The citing-paper list spans continuous-variable quantum computing, Gaussian boson sampling, GKP-code, and photonic-QML topics (e.g. "Continuous-Variable Quantum Encoding Techniques," "Resources for Bosonic Quantum Computational Advantage," "Strawberry Fields: A Software Platform for Photonic Quantum Computing," "A Convolutional Approach for Discrete-Variable Quantum Systems"). None of the 51 citing papers, and none of Douce et al.'s own references (standard DV-IQP theory citations, Bremner-Jozsa-Shepherd lineage, `PostBQP` complexity-class papers), constructs or proposes a Fock-space/photon-number linear-optical IQP analogue. **Result: no match, no impossibility result, in either direction of the citation graph.**

**2. Alternate-phrasing keyword queries (arXiv API, different wording than 08-RESEARCH.md's list):**

| Query | Results | What surfaced |
|---|---|---|
| `"sampling complexity" AND "linear optical" AND "commuting"` | 0 | Nothing |
| `"photon number" AND IQP AND hardness` | 1 | "Gaussian Boson Sampling to Accelerate NP-Complete Vertex-Minor Graph Classification" (2024), a GBS application paper, not an IQP construction |
| `"discrete variable" AND "instantaneous quantum computing"` | 1 | Douce et al. itself only; no other paper uses this exact phrase pairing |
| `IQP AND "linear optic"` | 3 | Two unrelated qubit-supremacy/complexity papers (2018, 2014) + the Boson Sampling Born Machine paper (2026, flagged below) |
| `IQP AND "boson sampling"` | 11 | Mostly standard quantum-supremacy/complexity theory papers; two directly relevant recent hits (flagged below) |
| `IQP AND Perceval` | 0 | Nothing |
| `"photon counting" AND "commuting" AND "diagonal gates"` | 0 | Nothing |
| `"Fock" AND "Hadamard" AND "sampling hardness"` | 0 | Nothing |

**3. Targeted recent-preprint check (2024-2026), per the plan's explicit ask:**

Two papers surfaced that are worth flagging explicitly as the closest hits either search pass has found; neither is a match for LIT-01's specific ask, but both are directly relevant context:

- **Kurkin, Chabaud, Kolarovszki, Bakó, Zimborás, Dunjko, "Universality of Classically Trainable, Quantum-Deployed Boson-Sampling Generative Models," arXiv:2603.11014 (Mar 2026).** Introduces the "Boson Sampling Born Machine" (BSBM), explicitly built as a linear-optical analogue of the IQP-QCBM (IQP quantum-circuit Born machine) train-classically/deploy-quantumly paradigm. Checked its reference list via Semantic Scholar (20 references): it does **not** cite Douce et al., and its hardness argument comes from **standard boson sampling's permanent-based hardness** (Aaronson-Arkhipov lineage), not from constructing an IQP-equivalent circuit class (commuting diagonal gates + Hadamard-conjugated measurement) in Fock space. So: not a match for LIT-01 (it doesn't build IQP's defining structure in Fock space), but it is the single closest piece of literature found connecting IQP-style generative-modeling structure to a photon-counting/linear-optical substrate: worth Phase 9 being aware of and citing, even though it answers a different question (Born-machine trainability/universality via boson-sampling hardness, not a DV-IQP hardness construction via IQP's own commuting-gate argument).
- **"Matrix product state approach to lossy boson sampling and noisy IQP sampling," arXiv:2510.24137 (Oct 2025).** Studies classical simulability of noisy/lossy boson sampling and noisy IQP sampling side-by-side using a shared MPS-based simulation technique, but treats them as two separate sampling models under a shared method — it does not construct or claim any structural correspondence between IQP and boson sampling. Not a match, not an impossibility result, not a partial lead — a coincidental methodological pairing.

**Second-pass conclusion:** this pass corroborates 08-RESEARCH.md's original finding rather than changing it: no DV/Fock-space linear-optical construction of IQP's specific structure (input in a fixed basis, commuting diagonal gates, Hadamard-conjugated measurement) exists in the literature, and no impossibility/no-go result against such a construction exists either, across both a keyword scan with different phrasing and a full citation-graph chase in both directions from Douce et al. The one addition this pass makes to the evidence base is the BSBM paper above: a very recent, closely-adjacent-but-structurally-distinct piece of work the owner should weigh before finalizing the verdict, since it shows IQP-style generative-modeling ideas are already being actively extended into linear optics (via boson sampling's own hardness, not a DV-IQP construction), relevant context for how Phase 9's contribution would be positioned, even though it doesn't change the underlying "nothing found, no impossibility" conclusion.

### LIT-03 coverage note

MerLin's own reproduced-papers catalog check (LIT-03) was already completed and verified 2026-07-30 per `.planning/REQUIREMENTS.md`: all 21 titles in `merlinquantum.ai/0.4/reproduced_papers/` were enumerated directly, and none are IQP-adjacent. That check stands as-is and required no re-verification in this pass; it's cited here only for completeness of the phase's overall literature coverage.

## Go/No-Go Verdict

**Verdict: Go, proceed to Phase 9 (Encoding Design).**

This is stated in the owner's own words: after reading Kurkin et al.'s Boson Sampling Born Machine paper (arXiv:2603.11014) in full (not just the abstract, fetched and read in full via PDF extraction, prompted by it being the closest tangential hit surfaced above), the owner's conclusion was **"No blocking impossibility, let's proceed."**

**Reasoning, per the owner:**

Per the locked bar in `08-CONTEXT.md`, "Go" requires only the absence of a blocking impossibility result: a full constructive mapping is explicitly not required at this stage, since building one is Phase 9's own job. Across both search passes on record above:

- The first pass (`08-RESEARCH.md`'s original WebSearch-based scan, cited in the "Starting point" subsection above) found boson sampling, Gaussian boson sampling, and standard DV-IQP theory papers, but no DV/Fock-space IQP construction and no impossibility result.
- The second, independently-conducted pass (this document's arXiv-API + Semantic-Scholar-citation-graph search, cited above) corroborated that finding rather than changing it, including a full citation-graph chase in both directions from Douce et al. (2017), and surfaced no construction and no impossibility result either.

Combined with the Douce et al. summary above, which establishes that the one existing IQP-hardness-in-photonics result (the CV-quadrature construction) is built in a formalism (continuous-quadrature squeezed-light/homodyne) that is fundamentally distinct from Fock-space/photon-number linear optics and neither proves nor disproves anything about the DV/Fock-space case, there is no evidence anywhere in the literature searched that a DV/Fock-space IQP construction is impossible.

The owner explicitly considered and set aside the Kurkin et al. BSBM paper as grounds for a "promising but needs more time" verdict instead of "Go." Having read the full paper, the owner confirmed it borrows IQP-QCBM's classically-trainable/quantum-deployed *training and deployment recipe*, but transplants that recipe onto boson-sampling's own separate, pre-existing hardness lineage (Aaronson-Arkhipov permanent-hardness): it does not build IQP's own defining structure (input in a fixed basis, commuting diagonal gates, Hadamard-conjugated measurement) inside Fock space. It therefore doesn't constitute a partial or ambiguous lead worth deeper follow-up before proceeding; it's directly relevant context for how Phase 9's contribution should be positioned (worth citing there), but it doesn't change the underlying "nothing found, no impossibility" conclusion that is the actual gating question here.

**What this verdict does not claim:** neither search pass was an exhaustive manual literature crawl, so there remains some residual risk that a deeper pass would surface something. That risk is accepted as a stated caveat, per `08-CONTEXT.md`'s own framing that a full constructive mapping (and, implicitly, a fully exhaustive literature sweep) is not the bar for this gate.

**Outcome:** LIT-04 is satisfied. Phase 8 is complete. Phase 9 (Encoding Design) is unblocked and can be planned via `/gsd:plan-phase 9`.

## Addendum (2026-09-03) — two citations an external audit found missing from this search

Neither changes the Go/No-Go verdict above (both are about how to *position* the resulting mapping's novelty, not about whether the specific DV/Fock-space construction this project builds already exists elsewhere — that finding stands). Added for completeness, both at abstract-level confidence pending a full read, per this document's own confidence-tiering convention:

- **Hoban, Wallman, Anwar, Usher, Raussendorf & Browne, "Measurement-based classical computation," PRL 112, 140505 (2014), arXiv:1304.2667.** Establishes IQP as exactly non-adaptive single-qubit measurement in the X-Y plane on a graph/cluster state — a second, MBQC-native formulation of IQP itself (distinct from the gate-model commuting-diagonal-layer formulation this document already covers). Worth citing in `docs/iqp-photonic-encoding.md`'s positioning, since a graph-state/measurement-based photonic realization is closer to Quandela's own hardware direction than the heralded-gate construction this project actually built, and the "is a photonic IQP realization novel" framing should be read against both formulations, not just the gate-model one.
- **KLM's own universality result should be named explicitly as a limit on the novelty claim.** Dual-rail photons plus heralded linear-optical gates (Knill, Laflamme & Milburn 2001, and this project's own `heralded_cz`/Knill-CZ construction, arXiv:quant-ph/0110144) already let *any* qubit circuit — IQP included — be realized in linear optics. This project's `iqp-photonic-encoding.md` mapping is a genuine, carefully-checked instance of that general fact, not a case the literature left open; the polarization-encoding *specifics* (which wave-plate angle realizes which gate, the exact herald-success bookkeeping) are this project's own real, checked work, and that distinction should be stated plainly rather than implied to be more novel than it is.
