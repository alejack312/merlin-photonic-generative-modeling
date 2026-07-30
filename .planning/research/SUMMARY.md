# Project Research Summary

**Project:** merlin-quantum-case-study — v2.0 milestone: IQP → photonic circuit encoding
**Domain:** Quantum complexity theory / photonic quantum computing (literature scoping + on-paper encoding design; no implementation in scope)
**Researched:** 2026-07-30
**Confidence:** MEDIUM-HIGH

## Executive Summary

This milestone asks a narrow, genuinely open research question: does a discrete-variable (Fock-space, phase-shifter + beamsplitter + photon-counting) linear-optical construction of qubit IQP circuits exist, and can one be designed on paper against MerLin/Perceval's actual primitives? All four research passes converge on the same answer: no published construction exists for this specific DV/Fock-space mapping, so Phase 1 (on-paper encoding design) is not pre-empted by prior work and is well-supported as a "go." But the search also surfaced a piece of directly adjacent prior art the design cannot ignore: Douce, Markham, Kashefi et al., "Continuous-Variable Instantaneous Quantum Computing is hard to sample" (PRL 118, 070503, 2017, arXiv:1607.07605), which already built an IQP-to-photonics reduction — but for continuous-variable optics (squeezed states plus homodyne detection), a different physical resource model from the discrete-variable (phase shifters, beamsplitters, photon-number counting) primitives Perceval/MerLin natively support and this milestone's source plan (Post_Sept1_IQP_Photonic_Plan.md) targets. This is the single most load-bearing finding in the research: the go/no-go verdict is "go, but position explicitly against Douce et al." rather than "go, blank slate."

The recommended approach is to treat Douce et al. as a structural template (how they built CV analogues of "commuting diagonal gates" and "Hadamard-basis conjugation") to translate into DV/Fock terms, not as a construction to reproduce — and to write Phase 1's design vocabulary directly in Perceval's low-level API (Circuit, PS, BS, BasicState) rather than any qubit-conversion bridge, since no Perceval object does the bespoke structural mapping this milestone needs. A second, closely related item the design must resolve is whether the target really is DV/Fock (native to MerLin/Perceval) or whether the CV-IQP precedent pulls the project toward a CV framework (Strawberry Fields) instead — the Stack research flags this explicitly as a fork that should be resolved with the owner during requirements-gathering, not silently assumed.

The key risks are conceptual rather than technical, since no code ships this milestone: (1) mistaking a structural analogy between IQP/boson-sampling/CV-IQP hardness stories for a formal reduction, (2) over-extending boson-sampling's Haar-random-ensemble hardness intuitions to a deliberately structured, non-random IQP-encoding circuit, and (3) letting genuine excitement about this being "the more novel/interesting stretch" push the search into confirmation bias (finding supporting papers and declaring victory) rather than also actively searching for disconfirming evidence (known classically-simulable photonic subclasses, prior failed attempts). All three are mitigated by writing conditional, conjecture-named claims and requiring an explicit falsifiable check as part of Phase 1's deliverable, not by additional tooling.

## Key Findings

### Recommended Stack

No new dependencies are needed for this milestone — both Phase 0 (literature scoping) and Phase 1 (on-paper design) are non-code deliverables. perceval-quandela==1.2.4 and merlinquantum==0.4.0 are already installed and are the correct reference vocabulary for writing Phase 1's design in directly-transcribable terms, even though no circuit code runs yet. For the literature-scoping task specifically, Semantic Scholar's citation-graph API/UI is the single most valuable tool — citation-chasing Douce et al. (2017) and the original Bremner-Montanaro-Shepherd IQP hardness paper is better suited to this milestone's actual open question than keyword search alone.

**Core technologies:**
- perceval-quandela 1.2.4 (installed) — low-level photonic circuit primitives (Circuit, PS, BS, BasicState, Processor, Analyzer, Sampler) — the actual substrate Phase 1's encoding must be expressible in to be buildable later; no version bump needed.
- merlinquantum 0.4.0 (installed) — photonic QML wrapper used by v1.0; not needed for this milestone's two tasks but kept pinned for continuity into a deferred Phase 2.
- Semantic Scholar API/UI (no install needed) — citation-graph traversal on Douce et al. 2017, the single most valuable literature tool for this milestone's actual open question.
- Strawberry Fields (Xanadu) — explicitly not installed; reading-material-only reference for CV gate vocabulary, relevant only if the DV-vs-CV fork (see below) resolves toward CV.

### Literature Landscape (in place of "Expected Features")

**Confirmed gap (the milestone's actual target):** No paper maps qubit IQP (Hadamard-conjugated diagonal unitaries, X-basis measurement) onto phase-shifter + beamsplitter + photon-counting primitives in the DV/Fock-space regime. This is genuinely open, not just unindexed — three independent, differently-phrased search passes across STACK, FEATURES, and PITFALLS research confirmed this.

**Directly relevant prior art to position against:**
- Douce, Markham, Kashefi et al. (PRL 2017, arXiv:1607.07605) — CV-IQP: squeezed states + homodyne detection, squeezing scales logarithmically with circuit size for the hardness result to survive. Different physical resource (continuous quadrature measurement) from photon counting.
- Kurkin et al., "Boson Sampling Born Machine" (2026, arXiv:2603.11014) — same "train classically, deploy quantumly" paradigm as this project's v1.0, explicitly ported to boson sampling, using DV linear optics with photon-number measurement — the right physical model, but an algorithmic-paradigm analogy, not a circuit-level IQP-to-photonics reduction. Authors themselves call it "analogous steps... with twists," not a formal mapping.
- Xie, Notton, Senellart, "Pre-Asymptotic Trainability in Photonic Variational Circuits under Postselection" (2026, arXiv:2605.11879) — not IQP-related, but the closest existing trainability/barren-plateau machinery for DV linear optics (MZI meshes, Fock space); one author overlaps with the MerLin framework paper, making this a plausible direct reference point in the Quandela context.

**Defer/out of scope for this milestone:** hardness-argument derivation, trainability sweeps, and any implementation — all explicitly Phase 2/3, not Phase 0/1.

### Architecture Approach

New work belongs in a new top-level module (iqp_photonic/), sibling to the existing generator/, not nested inside it — the two milestones share no runtime code path and have genuinely different core research questions. MerLin wraps Perceval at a specific, narrow point: MerLin's CircuitBuilder DSL compiles down to a real perceval.Circuit via .to_pcvl_circuit(), and QuantumLayer also accepts a raw pcvl.Circuit directly as a documented, first-class alternative — this raw-circuit path is what Phase 1's design should target since IQP's structure is bespoke/irregular, not a repeating layer template the builder DSL is optimized for. No built-in Perceval object performs the bespoke qubit-to-photonic structural mapping this milestone needs (the existing QiskitConverter does a generic, much heavier dual-rail+ancilla embedding) — the idiomatic verification pattern for a later Phase 2 is two independently-computed classical distributions diffed against each other, not a circuit conversion.

**Major components (target structure, not built this milestone):**
1. iqp_photonic/qubit_iqp.py — qubit-side reference (H^n * D * H^n via NumPy), the "known/classically-checkable" baseline.
2. iqp_photonic/encoding.py — Phase 1's design turned into code: functions mapping IQP structural parameters onto a pcvl.Circuit.
3. docs/iqp-photonic-encoding.md — the actual novel-contribution deliverable of this milestone: the on-paper mapping design itself.
4. docs/iqp-baseline.md — compiled prior IQP + barren-plateau literature notes.

### Critical Pitfalls

1. **Acronym collision poisons the search** — "IQP" means both Instantaneous Quantum Polynomial-time and Integrated Quantum Photonics in exactly this literature; always search with the term spelled out for at least one full pass, and disambiguate on first use in any doc (especially since the audience, Vincent Espitalier, is a photonics expert for whom the second sense is more familiar).
2. **Mistaking a structural analogy for a formal reduction** — IQP, boson sampling, and CV-IQP hardness are each separately-proven, conjecture-conditional theorems for specific circuit ensembles; "this also looks hard" is not evidence of hardness. Phase 1's design doc should state any hardness-adjacent claims conditionally, named by conjecture, with an explicit reduction direction — or explicitly defer the hardness question as out of scope.
3. **Over-extending boson-sampling intuitions to a structured, non-Haar-random circuit** — boson sampling's hardness is a property of a Haar-random unitary ensemble, not of "linear optics" generally; an IQP-inspired mapping is deliberately structured, the opposite of Haar-random, so the proof technique does not automatically transfer.
4. **Confirmation-biased literature search under time-box pressure** — the plan doc's own time-box creates pressure to search until finding supporting evidence and stop. Phase 0's go/no-go verdict should explicitly cite at least one disconfirming-pass query result (e.g., searching for known classically-simulable photonic subclasses), not just constructive-pass findings.
5. **Declaring the mapping "designed" without a falsifiable check** — a design narrative ("diagonal gates become phase shifters...") without a stated, concrete small-instance check and an explicit statement of what a mismatch would mean is not actually falsifiable; Phase 1's deliverable needs this stated up front, before any Phase 2 implementation.

## Implications for Roadmap

This milestone is explicitly scoped to two phases only (per the plan doc and PROJECT.md): Phase 0 (literature scoping) and Phase 1 (on-paper encoding design). Phases 2-4 (implementation, trainability study, write-up) are deferred pending Phase 0's go/no-go verdict and are out of scope for this roadmap.

### Phase 1: Literature Scoping (plan doc's "Phase 0")
**Rationale:** Must run first — it produces the go/no-go verdict that determines whether Phase 2 (design) is worth attempting, and this research pass already surfaces the Douce et al. precedent that the design phase must position against.
**Delivers:** docs/iqp-baseline.md (compiled IQP + barren-plateau literature notes) and an explicit go/no-go verdict with cited constructive AND disconfirming search passes.
**Addresses:** Confirms the DV/Fock-space IQP-photonics gap is genuinely open (per Literature Landscape above); surfaces Douce et al. (CV-IQP), Kurkin et al. (BSBM), and Xie/Notton/Senellart (photonic trainability) as required reading before Phase 2 starts.
**Avoids:** Pitfall 1 (acronym collision — require a spelled-out-term search pass), Pitfall 7 (confirmation bias — require a disconfirming-pass search explicitly).
**Requirements-gathering decision to surface with the owner in this phase:** the DV-vs-CV fork flagged by Stack research — does the milestone stay DV/Fock-native (Perceval, matching the plan doc's implicit assumption) or does the Douce et al. precedent make a CV-IQP-adjacent direction (Strawberry Fields) more attractive? This is a scope decision, not something Phase 0 should resolve silently.

### Phase 2: On-Paper Encoding Design (plan doc's "Phase 1")
**Rationale:** Only proceeds if Phase 1 (literature scoping) returns "go." Depends entirely on Phase 1's findings — specifically must explicitly position the design against Douce et al. and Kurkin et al. rather than starting from a blank page.
**Delivers:** docs/iqp-photonic-encoding.md — the milestone's actual novel-contribution deliverable: an explicit basis correspondence (qubit computational-basis strings <-> photonic Fock states), a checked (not assumed) gate-algebra mapping (diagonal gates -> phase shifters, Hadamard conjugation -> beamsplitters), and a stated falsifiable check for a later Phase 2-implementation to run.
**Uses:** Perceval's raw Circuit/PS/BS/BasicState vocabulary (per Architecture research) as the design's implementable target — not the MerLin builder DSL, and not a Qiskit-conversion bridge.
**Implements:** The "Two-sided independent classical evaluation" pattern from Architecture research (define correspondence explicitly, so a future Phase 2/3 implementation can diff two independently-computed distributions rather than converting one representation into the other).
**Avoids:** Pitfall 2 (analogy-as-reduction — state hardness claims conditionally), Pitfall 3 (boson-sampling over-extension — check the mapping's ensemble against Haar-randomness assumptions explicitly), Pitfall 5 (unfalsifiable design — require a stated falsification condition), Pitfall 6 (basis/algebra glossing — write the correspondence out explicitly, don't rely on qualitative resemblance), Pitfall 8 (sliding into implementation — no perceval/MerLin circuit-building code should appear in this milestone's commits; scratch NumPy checks only, if needed).

### Phase Ordering Rationale

- Literature scoping must precede design because the go/no-go verdict gates whether design work is worth doing at all, and because the Douce et al. finding materially changes what "novel" means for the design (it's novel relative to DV/Fock-space specifically, not to IQP-photonics generally) — the design phase cannot responsibly start without this framing.
- The DV-vs-CV fork is deliberately placed as a decision point inside Phase 1 (literature scoping), not Phase 2, because getting it wrong reroutes the entire design phase's target framework (Perceval vs. Strawberry Fields) — resolving it early avoids a design rewrite.
- Both phases are pre-implementation by design (per the plan doc and Architecture research's "no code runs" framing) — this ordering exists specifically to avoid Pitfall 8 (design sliding into implementation), by keeping the two phases doc-only and code-free until a future, separately-planned Phase 2/3 milestone.

### Research Flags

Needs deeper research during phase planning:
- **Phase 1 (Literature Scoping):** MerLin's own 18 reproduced SOTA papers have not been checked for IQP-adjacency (Gap 4 in FEATURES.md) — a five-minute, high-value check the owner should do directly against MerLin's GitHub/docs before finalizing the go/no-go verdict. Also flagged: a full (not abstract-only) read of Douce et al. 2017 is needed before Phase 2 can responsibly position against it — most of this research's extraction was abstract-level.
- **Phase 2 (Encoding Design):** No further external research needed to start — the open question is genuinely a design problem (translate CV structural ideas to DV/Fock terms), not a literature gap. However, if the design surfaces a need to check a specific unitary's action algebraically, that's scratch-calculation work (NumPy), not literature research.

Phases with standard patterns (skip research-phase for these sub-questions):
- **Perceval API vocabulary** for Phase 2's design: well-documented, verified against the installed package and live-tested in this research pass (Architecture research). No further API research needed.

## Confidence Assessment

| Area | Confidence | Notes |
|------|------------|-------|
| Stack | MEDIUM-HIGH | Perceval/MerLin API verified against installed versions and live code execution; literature findings (the "no DV mapping exists" claim) verified across multiple independent searches but literature scoping is never exhaustive by nature — treated as this milestone's own Phase 0 starting point, not a closed case. |
| Features (Literature Landscape) | MEDIUM-HIGH for "does a direct construction exist" (converging evidence across independent searches plus a dedicated survey paper explicitly presenting IQP and boson sampling as parallel, unconnected results); MEDIUM for "is this exact question already answered anywhere" (absence-of-evidence claims from a time-boxed, not exhaustive, search). |
| Architecture | HIGH | All claims verified against actually-installed packages (perceval-quandela==1.2.4, merlinquantum==0.4.0) by reading source directly and running a live circuit/Processor/Analyzer round-trip, not from recall or docs alone. |
| Pitfalls | HIGH for complexity-theory/photonics-specific claims (grounded in cited peer-reviewed/arXiv sources); MEDIUM for general research-process pitfalls (confirmation bias, scope creep) — informed judgment applied to this project's documented history, not citation-backed facts. |

**Overall confidence:** MEDIUM-HIGH

### Gaps to Address

- **MerLin's own 18 reproduced SOTA papers not checked for IQP-adjacency** (FEATURES.md Gap 4) — flagged as a required five-minute follow-up before Phase 1's go/no-go verdict is finalized, not a confirmed gap yet.
- **Douce et al. (2017) reviewed at abstract-level only, not full-text** — before Phase 2 (design) positions against it, a full read is needed to correctly extract how they define CV analogues of "commuting diagonal gates" and "Hadamard-basis conjugation," per Stack research's explicit recommendation.
- **The DV-vs-CV fork is unresolved** — Stack research explicitly surfaces this as a live decision (native Perceval/Fock-space design vs. pulling in Strawberry Fields for a CV-IQP-adjacent direction) that this milestone's requirements-gathering needs to resolve explicitly with the owner, not something any of the four research passes can settle unilaterally.
- **Kurkin et al. (BSBM) "no explicit circuit mapping" claim** is based on a single abstract-level pass, not a full read of the paper's construction section — worth verifying directly before Phase 2 relies on it as established.
- **Lund-Bremner-Ralph survey's "no reduction claimed between IQP and boson sampling"** reading is based on abstract framing, not full-text confirmation — worth a targeted full-text check if this claim becomes load-bearing for Phase 1's final go/no-go writeup.

## Sources

### Primary (HIGH confidence)
- venv/Lib/site-packages/merlin/algorithms/layer.py, merlin/builder/circuit_builder.py, merlin/core/circuit.py, merlin/algorithms/layer_utils.py — read directly against installed merlinquantum==0.4.0.
- Live verification run: pcvl.Circuit + PS/BS + Processor("SLOS", ...) + Analyzer round-trip against installed perceval-quandela==1.2.4.
- Perceval v0.13 circuits docs (https://perceval.quandela.net/docs/v0.13/circuits.html) / tutorial (https://perceval.quandela.net/docs/v0.13/notebooks/Tutorial.html) — cross-checked against installed version.
- PyPI: perceval-quandela (https://pypi.org/project/perceval-quandela/) — confirms 1.2.4 is current as of 2026-07-02.
- Douce, Markham, Kashefi et al., "Continuous-Variable Instantaneous Quantum Computing is hard to sample," PRL 118, 070503 (2017). https://arxiv.org/abs/1607.07605

### Secondary (MEDIUM confidence)
- Kurkin, Chabaud, Kolarovszki, Bakó, Zimborás, Dunjko, "Universality of Classically Trainable, Quantum-Deployed Boson-Sampling Generative Models" (2026). https://arxiv.org/abs/2603.11014
- Xie, Notton, Senellart, "Pre-Asymptotic Trainability in Photonic Variational Circuits under Postselection" (2026). https://arxiv.org/abs/2605.11879
- Lund, Bremner, Ralph, "Quantum sampling problems, BosonSampling and quantum supremacy," npj Quantum Information (2017). https://arxiv.org/abs/1702.03061
- Notton, Stott, Schoeb, et al., "MerLin: A Discovery Engine for Photonic and Hybrid Quantum Machine Learning" (2026). https://arxiv.org/abs/2602.11092
- Bremner, Montanaro, Shepherd, "Average-case complexity versus approximate simulation of commuting quantum computations." https://arxiv.org/abs/1504.07999

### Tertiary (LOW confidence)
- Park & Oh, "Matrix product state approach to lossy boson sampling and noisy IQP sampling" (Oct 2025, rev. Jul 2026). https://arxiv.org/abs/2510.24137 — abstract-level only, preprint status unconfirmed.
- Gottlieb et al., "Efficient training of photonic quantum generative models" (Mar 2026, rev. Jul 2026). https://arxiv.org/abs/2603.08793 — metadata-level only.
- Zhang & Zhuang, "Energy-dependent barren plateau in bosonic variational quantum circuits" (2023/2025). https://arxiv.org/abs/2305.01799 — abstract-level, full-text fetch failed.

Full source lists with per-claim confidence annotations are in each individual research file: STACK.md, FEATURES.md, ARCHITECTURE.md, PITFALLS.md.

---
*Research completed: 2026-07-30*
*Ready for roadmap: yes*
