# Literature Landscape: IQP → Photonic Circuit Encoding

**Adaptation note:** This document repurposes the standard FEATURES.md template. "Table stakes / differentiators / anti-features" doesn't map cleanly onto a literature-scoping question, so the structure below is reorganized around the downstream consumer's actual need: a go/no-go call on whether Phase 1 (on-paper encoding design) is worth attempting. Sections are: **Directly relevant prior work**, **Adjacent/analogous work**, **Confirmed gaps**, and a **Phase 1 direction recommendation** in place of "MVP Definition."

**Domain:** Quantum complexity theory / photonic quantum computing — IQP circuits, boson sampling, continuous-variable (CV) sampling hardness, barren plateaus in photonic variational circuits.
**Researched:** 2026-07-30
**Confidence:** MEDIUM-HIGH for "does a direct construction exist" (converging evidence across independent searches and a dedicated survey paper); MEDIUM for "is this specific milestone question already answered" (absence-of-evidence claims, time-boxed search, not an exhaustive literature review)

---

## Bottom line (for the go/no-go call)

**The milestone's core question is open.** No paper found constructs a discrete-variable (Fock-space, phase-shifter + beamsplitter + photon-counting) linear-optical realization of qubit IQP circuits, and no paper found studies barren-plateau/trainability behavior for such a construction. The two closest bodies of work — CV-IQP (Douce et al. 2017) and the Boson Sampling Born Machine (Kurkin et al. 2026) — each answer an adjacent but different question. Phase 1 (on-paper encoding design) is worth attempting; it is not pre-empted by existing work, but it should explicitly position itself relative to both of these adjacent papers rather than starting from a blank page.

---

## Directly relevant prior work

### 1. CV-IQP hardness construction — Douce, Markham, Kashefi, Diamanti, Coudreau, Milman, van Loock, Ferrini, *"Continuous-Variable Instantaneous Quantum Computing is hard to sample,"* Phys. Rev. Lett. 118, 070503 (2017). [arXiv:1607.07605](https://arxiv.org/abs/1607.07605)

**This is the closest thing to an existing "IQP → photonic" mapping, and the milestone should read it before Phase 1.**

- Extends the discrete-variable (qubit) IQP hardness proof to the **continuous-variable domain**, using **squeezed states** and **homodyne (quadrature) detection**, plus post-selection.
- To make post-selection well-defined in CV, they use finitely-resolved homodyne detectors (discrete probability distributions over continuous outcomes).
- Residual errors from finite squeezing are suppressed via a **GKP (Gottesman-Kitaev-Preskill) qubit-into-oscillator encoding**.
- Key quantitative result: squeezing must scale **logarithmically with circuit size** (→ polynomial input energy) for the post-selected computational class to remain meaningful.
- **Why it's not a full answer to this milestone's question:** it's CV-IQP, not DV/Fock-space IQP. The physical primitives are squeezed-state preparation + homodyne detection, not the phase-shifter + beamsplitter + **photon-number counting** toolchain the milestone specifies (and that MerLin/Perceval natively support). Homodyne measurement and photon-counting measurement are genuinely different physical/computational resources — a CV-IQP result does not automatically transfer to a Fock-space photon-counting ansatz. Confidence: HIGH that this paper exists and says what's summarized above (read via WebFetch of the arXiv abstract; abstract text quoted directly). MEDIUM on completeness of extracting the full paper's technical content, since only the abstract/PRL summary was reviewed, not the full body.

### 2. Boson Sampling Born Machine (BSBM) — Kurkin, Chabaud, Kolarovszki, Bakó, Zimborás, Dunjko, *"Universality of Classically Trainable, Quantum-Deployed Boson-Sampling Generative Models,"* 2026. [arXiv:2603.11014](https://arxiv.org/abs/2603.11014)

**The closest existing work in spirit — same "train classically, deploy quantumly" paradigm the project's v1.0 IQP-MMD work already uses, now explicitly ported to boson sampling — but it is an analogy at the algorithmic-training level, not a circuit-level IQP→photonics reduction.**

- Directly motivated by the IQP-QCBM (IQP quantum-circuit Born machine) paradigm: train the generative model classically (loss efficiently computable), deploy/sample quantumly (sampling remains classically hard).
- Introduces the BSBM using **passive linear-optical interferometers** — phase shifters and beamsplitters implicit in the interferometer unitary U(m) — with **Fock-basis (photon-number) measurement** in a collision-free regime. This is exactly the DV linear-optics primitive set the milestone cares about.
- Explicitly states: *"Our analysis retraces analogous steps as were found for IQP-QCBMs with twists"* — i.e., the authors themselves frame this as a structural parallel, not a formal reduction. **No explicit circuit-level mapping from an IQP circuit to a boson-sampling circuit is given.**
- Shows BSBMs are classically trainable for wide loss-function families (via recent results on classically approximating linear-optics expectation values), that "basic" BSBMs are not universal, and that universality can be recovered (as in IQP-QCBM) via constant-function postprocessing / model extension, while preserving sampling hardness.
- Discusses gradient-estimation modalities for efficient classical training but does not run a barren-plateau/gradient-variance-vs-system-size study comparable to what Phase 3 of this milestone would need.
- Confidence: HIGH on existence and abstract content (full abstract fetched and quoted). MEDIUM on the "no explicit circuit mapping" claim — this is drawn from a single WebFetch summarization pass over the HTML version, not a full read of the paper's construction section; worth a direct read before finalizing Phase 1's positioning.

### 3. Photonic barren-plateau baseline (DV linear optics) — Xie, Notton, Senellart, *"Pre-Asymptotic Trainability in Photonic Variational Circuits under Postselection,"* 2026. [arXiv:2605.11879](https://arxiv.org/abs/2605.11879)

**Not an IQP paper, but this is the right kind of primitive (MZI meshes, phase shifters + beamsplitters, Fock space) and the right kind of question (trainability/barren plateaus) — the most useful baseline for what "barren-plateau behavior in the photonic setting" concretely means.**

- Studies rectangular MZI-mesh interferometers (the standard Clements-style universal linear-optics decomposition) acting on Fock-space photon states.
- Finds **regime-dependent trainability**: under allow-bunching / collision-free postselection, gradient variance decays only **polynomially** with mode count (no barren plateau). Under **dual-rail-code postselection**, gradient variance decays **exponentially** — a genuine barren plateau (empirically ~exp(−0.19 to −0.20·N) for N logical dual-rail units, m=2N modes).
- Mechanism identified: postselection reshapes the pulled-back observable across the irreducible decomposition of U(m)'s operator space; whether high-dimensional (exponentially-growing) irreps dominate the gradient-variance sum determines trainability.
- No IQP connection made in this paper. Note for the owner: one author (Notton) also co-authors the MerLin framework paper (arXiv:2602.11092) — likely the same lab/group, meaning this specific trainability framework may be directly reachable via existing project contacts (relevant if this comes up with Vincent).
- Confidence: MEDIUM — content extracted via WebFetch of the HTML rendering; core scaling claims (polynomial vs. exponential regimes, the ~exp(−0.19N) figure) should be re-verified against the primary source before being cited as a numeric baseline in Phase 3.

### 4. General photonic/bosonic barren-plateau results (baseline, not IQP-specific)

- Horner, *"Mitigating the barren plateau problem in linear optics,"* arXiv:2510.02430 (2024/2025). Proves barren plateaus exist for **both bosonic and fermionic** linear-optics variational circuits, shows fermionic linear optics is less susceptible, and proposes a "dual-valued phase shifter" (via non-linear optics, measurement-induced nonlinearity, or entangled resource states) as a mitigation that reduces local minima regardless of ansatz. No IQP connection. Confidence MEDIUM (abstract-level extraction only).
- Zhang & Zhuang, *"Energy-dependent barren plateau in bosonic variational quantum circuits,"* arXiv:2305.01799, Quantum Sci. Technol. (2023, published 2025). Studies abstract CV bosonic circuits (not necessarily tied to phase-shifter/beamsplitter primitives specifically). Gradient variance scales as **1/E^(Mν)** — exponential in mode count M, polynomial in per-mode circuit energy E, with ν=1 (shallow) or ν=2 (deep circuits). Energy is a controllable knob for mitigation. No IQP connection. Confidence MEDIUM (abstract-level only; full-text PDF fetch failed due to binary/encoding issues, so this is WebSearch-summary-corroborated rather than independently re-verified from the primary text).

### 5. Qubit-side IQP-QCBM trainability line (the baseline this project's v1.0 already sits on top of)

A concentrated 2026 line of work on trainability of IQP-based quantum circuit Born machines, entirely in the qubit/gate model (no photonics):
- *"Trainability of IQP Quantum Circuit Born Machines Under Gaussian Initialization,"* [arXiv:2606.10179](https://arxiv.org/abs/2606.10179) (2026)
- *"Characterizing Trainability of Instantaneous Quantum Polynomial Circuit Born Machines,"* [arXiv:2602.11042](https://arxiv.org/abs/2602.11042) (2026)
- *"Discovery of connectivity-trainability trade-off of IQP Circuits for Hamiltonian Optimization,"* [arXiv:2606.24264](https://arxiv.org/abs/2606.24264) (2026)

Consistent theme across this line: barren plateaus/exponential concentration in IQP-QCBMs depend on the **generator set and kernel spectrum** under uniform initialization; it remains an **explicitly open question** (stated as such in this literature) under what conditions IQP-QCBM avoids barren plateaus entirely. **This is directly useful as the qubit-side baseline the milestone's Phase 3 plan calls for** ("your own IQP + barren-plateau notes/results compiled into one reference doc" — this line of work is what the owner's own prior results should be checked against/cited alongside). Confidence: MEDIUM — found via WebSearch summarization, not independently read in full; recommend the owner pull these directly given they're load-bearing for Phase 3's comparison baseline.

---

## Adjacent/analogous work

Useful as background or building blocks, not answers to the milestone's core question.

- **Lund, Bremner, Ralph, *"Quantum sampling problems, BosonSampling and quantum supremacy,"* npj Quantum Information (2017).** [arXiv:1702.03061](https://arxiv.org/abs/1702.03061) — A survey explicitly covering both BosonSampling and IQP Sampling as "two classes of quantum sampling problems that demonstrate the supremacy of quantum algorithms." Read via full abstract fetch: it presents them **side by side as parallel, independently-derived hardness results, not as reduced/connected to one another.** This is good evidence (from a dedicated survey, which is exactly where a reduction would be flagged if one existed) that no established reduction connects the two hardness arguments. Confidence MEDIUM-HIGH for the "no reduction claimed" reading, since it's based on the abstract's framing rather than a full-text confirmation that the body doesn't contain one — worth a targeted full-text check if this claim becomes load-bearing for Phase 0's final go/no-go writeup.

- **Bremner, Montanaro, Shepherd, *"Achieving quantum supremacy with sparse and noisy commuting quantum computations,"* Quantum 1, 8 (2017)**, and **Paletta, Leverrier, Sarlette, Mirrahimi, Vuillot, *"Robust sparse IQP sampling in constant depth,"* Quantum 8, 1337 (2024).** [arXiv link via Quantum journal] — Both qubit-based, no photonic implementation. Notable point for the hardness/noise sub-question: IQP's hardness argument is **native to the standard quantum circuit model**, meaning (per these papers) any gate-model architecture can implement it and standard **error correction** can be used to protect it from noise — a structurally different noise story than boson sampling, where hardness is tied to specific optical loss/distinguishability physics that can't simply be "error corrected" away in the same sense. This is the closest thing found to an **implicit contrast** between the two noise-robustness stories, though no paper makes the comparison explicitly (see Confirmed Gaps below).

- **Boson sampling noise/loss hardness literature** (for the photonic side of the noise contrast): multiple 2024-2025 papers establish that boson sampling/Gaussian boson sampling hardness survives *some* loss regimes and collapses in others — e.g. *"Sufficient conditions for hardness of lossy Gaussian boson sampling"* [arXiv:2511.07853] finds lossy GBS retains full hardness when at most a **logarithmic fraction of photons is lost**; hardness is known to break down when per-photon survival probability vanishes with system size (constant per-photon loss is fine, loss that scales adversarially with photon number is not). *"Transition of Anticoncentration in Gaussian Boson Sampling"* [arXiv:2312.08433] characterizes when anticoncentration (needed for the standard hardness argument) breaks down as squeezed-mode count vs. photon count scales change. These are the right reference points for Phase 3's "does hardness degrade like boson sampling" comparison, once/if the project gets that far — but none of them reference IQP.

- **IQP-QCBM classical-surrogation framework** — Herrero-Gonzalez, Coyle, McDowall, Grassie, Beentjes, Khamseh, Kashefi, *"The Born Ultimatum: Conditions for Classical Surrogation of Quantum Generative Models with Correlators,"* [arXiv:2511.01845] (2025). Derives closed-form Pauli-propagation expressions for IQP circuits (plus matchcircuits, Heisenberg/Haldane-chain circuits) to determine when a classical surrogate can match a trained QCBM. Confirmed via direct fetch: **does not include boson sampling/linear-optical models** in its comparison set. Useful as a template for the *kind* of classical-surrogation analysis Phase 3 might eventually want to run on a photonic IQP analogue, but not evidence toward the cross-paradigm comparison itself.

- **MerLin framework paper** — Notton, Stott, Schoeb, et al., *"MerLin: A Discovery Engine for Photonic and Hybrid Quantum Machine Learning,"* [arXiv:2602.11092] (2026). The framework this project's v1.0 is built on. Supports photon-number-resolving and threshold detectors and reproduces 18 SOTA photonic QML papers — worth checking directly (not done in this pass) whether IQP-inspired ansätze are among the 18 reproductions, since that would be the single most relevant thing to check before Phase 1 starts. **This is a gap in this research pass, not a confirmed absence** — flagged explicitly below.

- **Related "train classical / deploy quantum" generative-model families** for pattern-matching Phase 1's design choices: Fermionic Born Machines (arXiv:2511.13844) and Spectral Born Machines (arXiv:2607.06675) apply the same paradigm to fermion-sampling and discrete-data settings respectively — useful as design-pattern references for how a sampling-hardness class gets turned into a trainable generative model, independent of the IQP question specifically.

---

## Confirmed gaps

Each gap below states what was searched, so the negative result can be trusted rather than assumed to be an omission.

### Gap 1: No discrete-variable (Fock-space) linear-optical IQP construction found

**Searched:** "IQP circuits linear optics photonic mapping instantaneous quantum polynomial", "dual-rail linear optical IQP construction phase shifter beamsplitter photon counting Hadamard", "linear optical IQP OR photonic IQP OR boson sampling IQP dual-rail qubit encoding construction paper", plus general Google/WebSearch scans of Perceval/MerLin/Quandela publication lists.

**Result:** No paper found that takes qubit IQP (Hadamard-conjugated diagonal unitaries, X-basis measurement) and maps it onto phase-shifter + beamsplitter + photon-number-counting primitives in the discrete-variable/Fock-space regime — the regime MerLin and Perceval natively operate in. The only existing "photonic IQP" is CV-IQP (Douce et al., squeezed states + homodyne, see above), which uses different physical resources (continuous quadrature measurement, not photon counting). Dual-rail linear-optical qubit encodings (KLM-style) are well established generically, and single-qubit gates (including Hadamard) are known to be directly realizable via beamsplitter+phase-shifter circuits on a dual-rail qubit — but no paper was found that assembles this into an explicit IQP circuit construction. **This gap is genuinely open, not just unindexed** — it is the literal target of this milestone's Phase 1.

### Gap 2: No formal reduction or explicit analogy between IQP's hardness argument and boson sampling's hardness argument

**Searched:** "IQP sampling hardness boson sampling relationship reduction complexity", "boson sampling hardness fragile noise loss compared IQP hardness argument analogy", "'IQP' 'boson sampling' reduction equivalence complexity class 2024 2025", "Gaussian boson sampling IQP relationship complexity comparison photon loss anticoncentration".

**Result:** IQP's hardness rests on average-case #P-hardness of complex-temperature Ising partition functions / counting zeros of random low-degree polynomials, with anticoncentration **provable** for IQP. Boson sampling's hardness rests on average-case hardness of estimating matrix permanents, with anticoncentration only conjectured (and separately studied — see Transition of Anticoncentration paper above). These are structurally similar in *form* (both are worst-to-average-case reductions feeding a Stockmeyer-approximate-counting argument against polynomial-hierarchy collapse) but **no paper found treats one as a special case, generalization, or formal reduction of the other**. The dedicated survey (Lund-Bremner-Ralph) that would be the natural place for such a connection to be stated presents them as parallel, separately-derived results. This is a **structural-analogy relationship at best, not a proven or even conjectured formal reduction** — the milestone plan's framing of "does hardness survive the photonic translation the way boson sampling's degrades under loss" is therefore an open research question, not a known result being looked up.

### Gap 3: No barren-plateau/trainability study for a photonic IQP-inspired ansatz specifically

**Searched:** "barren plateaus continuous variable quantum neural network photonic variational circuits", "IQP continuous variable quantum computing hardness sampling" (for trainability side-content), plus the searches in Gap 1.

**Result:** Two disjoint literatures exist — (a) barren-plateau studies for generic photonic/bosonic variational circuits (Xie/Notton/Senellart, Horner, Zhang/Zhuang — none IQP-specific), and (b) barren-plateau studies for qubit IQP-QCBMs (the 2026 trainability line under Gap-adjacent "Directly relevant" section — none photonic). **No paper found sits at the intersection.** This directly confirms the milestone's premise that Phase 3's trainability study, once an encoding exists, would be addressing a genuinely unstudied combination — not re-deriving a known result.

### Gap 4: Not checked — MerLin's own 18 reproduced SOTA papers

**Not searched directly in this pass; flagged as a recommended immediate follow-up, not a confirmed gap.** The MerLin paper (arXiv:2602.11092) reproduces 18 state-of-the-art photonic QML papers spanning kernels, reservoir computing, convolutional/recurrent architectures, and generative models. This research pass did not enumerate that list to check whether any of the 18 is IQP-adjacent. Given the project's direct access to MerLin's own documentation/GitHub, this is a five-minute check the owner should do before finalizing Phase 0's go/no-go (higher-confidence and lower-cost than further arXiv searching, and closest to "ground truth" for what Quandela's own team already considers IQP-relevant).

---

## Phase 1 direction recommendation (in place of MVP Definition)

Based on the above, if the go/no-go call is "go," Phase 1's on-paper encoding design should:

1. **Explicitly position against Douce et al. (CV-IQP) and Kurkin et al. (BSBM)** in its opening framing — both are the "nearest neighbors" a reviewer (or Vincent) will immediately think of, and the design should state up front why it targets Fock-space/photon-counting DV linear optics instead of CV/homodyne (Douce et al.) and why it's a circuit-level structural mapping rather than an algorithmic-paradigm analogy (Kurkin et al.).
2. **Reuse the Xie/Notton/Senellart trainability framework** (irreducible-representation decomposition of the pulled-back observable under postselection) as the analytical toolkit for Phase 3's eventual barren-plateau question — it's the closest existing machinery for "what does barren-plateau behavior mean in DV linear optics," and one author's overlap with the MerLin paper makes it a plausible direct reference point given the Quandela context.
3. **Use dual-rail KLM-style qubit encoding** as the starting substrate for translating IQP's Hadamard-conjugated diagonal-unitary structure: Hadamard → symmetric beamsplitter on a dual-rail pair (well-established primitive, confirmed above); diagonal IQP gates → phase shifters (natural fit, phase shifters are literally diagonal unitaries in the Fock/mode basis); the open design question is what "commuting diagonal gates across multiple dual-rail-encoded qubits, all applied instantaneously/in any order" looks like once multiple dual-rail pairs interact — that's the actual novel content Phase 1 needs to produce, not something found in the literature.
4. **Treat the hardness question as explicitly open** rather than something to look up — Gap 2 confirms there is no existing argument to adapt, so Phase 1's hardness discussion (if attempted at all before Phase 3) should be scoped as "what would a hardness argument even need to establish here," not "adapt argument X."

---

## Sources

All sources below were retrieved via WebSearch and WebFetch during this research pass (2026-07-30). Confidence levels noted per-claim above; most extractions are abstract-level (via WebFetch summarization of arXiv HTML/abstract pages), not full-text reads — flagged explicitly where this matters for downstream reliance.

- Douce et al., "Continuous-Variable Instantaneous Quantum Computing is hard to sample," PRL 118, 070503 (2017). https://arxiv.org/abs/1607.07605
- Kurkin, Chabaud, Kolarovszki, Bakó, Zimborás, Dunjko, "Universality of Classically Trainable, Quantum-Deployed Boson-Sampling Generative Models" (2026). https://arxiv.org/abs/2603.11014
- Xie, Notton, Senellart, "Pre-Asymptotic Trainability in Photonic Variational Circuits under Postselection" (2026). https://arxiv.org/abs/2605.11879
- Horner, "Mitigating the barren plateau problem in linear optics" (2024/2025). https://arxiv.org/abs/2510.02430
- Zhang, Zhuang, "Energy-dependent barren plateau in bosonic variational quantum circuits," Quantum Sci. Technol. (2023/2025). https://arxiv.org/abs/2305.01799
- "Trainability of IQP Quantum Circuit Born Machines Under Gaussian Initialization" (2026). https://arxiv.org/abs/2606.10179
- "Characterizing Trainability of Instantaneous Quantum Polynomial Circuit Born Machines" (2026). https://arxiv.org/abs/2602.11042
- "Discovery of connectivity-trainability trade-off of IQP Circuits for Hamiltonian Optimization" (2026). https://arxiv.org/abs/2606.24264
- Lund, Bremner, Ralph, "Quantum sampling problems, BosonSampling and quantum supremacy," npj Quantum Information (2017). https://arxiv.org/abs/1702.03061
- Bremner, Montanaro, Shepherd, "Achieving quantum supremacy with sparse and noisy commuting quantum computations," Quantum 1, 8 (2017).
- Paletta, Leverrier, Sarlette, Mirrahimi, Vuillot, "Robust sparse IQP sampling in constant depth," Quantum 8, 1337 (2024). https://quantum-journal.org/papers/q-2024-05-06-1337/
- "Sufficient conditions for hardness of lossy Gaussian boson sampling" (2025). https://arxiv.org/abs/2511.07853
- "Transition of Anticoncentration in Gaussian Boson Sampling," PRL 134, 140601. https://arxiv.org/abs/2312.08433
- Herrero-Gonzalez, Coyle, McDowall, Grassie, Beentjes, Khamseh, Kashefi, "The Born Ultimatum: Conditions for Classical Surrogation of Quantum Generative Models with Correlators" (2025). https://arxiv.org/abs/2511.01845
- Notton, Stott, Schoeb, et al., "MerLin: A Discovery Engine for Photonic and Hybrid Quantum Machine Learning" (2026). https://arxiv.org/abs/2602.11092
- Herbst, Brandić, Pérez-Salinas, "Limits of quantum generative models with classical sampling hardness" (2025). https://arxiv.org/abs/2512.24801

---
*Literature landscape research for: IQP → Photonic Circuit Encoding milestone (Post_Sept1_IQP_Photonic_Plan.md, Phase 0)*
*Researched: 2026-07-30*
