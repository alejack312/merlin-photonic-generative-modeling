# Pitfalls Research

**Domain:** Complexity-theory literature scoping + novel qubit-gate-model→linear-optics encoding design (IQP → photonic ansatz), pre-implementation
**Researched:** 2026-07-30
**Confidence:** HIGH for complexity-theory/photonics-specific claims (grounded in cited peer-reviewed/arXiv sources below); MEDIUM for general research-process pitfalls (confirmation bias, scope creep) — these are informed judgment applied to this project's documented history, not citation-backed facts.

**Scope note:** This milestone (per `Post_Sept1_IQP_Photonic_Plan.md` and `.planning/STATE.md`) covers only the literature-scoping phase (plan doc's "Phase 0," expected roadmap **Phase 8**) and the on-paper encoding-design phase ("Phase 1," expected roadmap **Phase 9**). Implementation (Phase 2), the trainability/hardness study (Phase 3), and write-up (Phase 4) are explicitly out of scope for v2.0 and are covered here only where a scoping/design-phase decision would set up a downstream failure in them.

---

## Critical Pitfalls

### Pitfall 1: The acronym collision poisons the literature search

**What goes wrong:** "IQP" is a heavily overloaded acronym. In quantum computing and photonics literature specifically, it means both **Instantaneous Quantum Polynomial-time** (the complexity class/circuit family this project cares about) and **Integrated Quantum Photonics** (a hardware/engineering term for on-chip photonic circuits — exactly the kind of paper that *sounds* directly relevant to an "IQP photonic" search but is about something else entirely). A search for "IQP linear optics" or "IQP photonic encoding" returns a mix of both senses, and it is easy to either (a) miscount "Integrated Quantum Photonics" hits as evidence the topic is well-covered (false sense of a crowded/solved space), or (b) bury the few genuinely relevant "Instantaneous Quantum Polynomial-time" hits under noise and miss them.

**Why it happens:** Both usages are common in exactly the corner of the literature this project needs to search, and neither community consistently disambiguates on first use in titles/abstracts.

**How to avoid:** Always search with the term spelled out ("instantaneous quantum polynomial-time" or "instantaneous quantum polynomial time circuits"), never bare "IQP," for at least one full pass. Cross-check hits against known IQP authors/venues (Bremner, Montanaro, Shepherd; the commuting-quantum-computation / PH-collapse literature) rather than trusting keyword relevance alone. When writing this project's own docs, spell out the acronym on first use per document — this also matters for Pitfall 7 below (communicating with Vincent Espitalier, whose own field is integrated photonics).

**Warning signs:** This collision was directly observed live during this research session — an initial search for `"IQP" linear optics photonic encoding construction` returned "Integrated Quantum Photonics" as the dominant hit, not Instantaneous-Quantum-Polynomial-time constructions, until the query was reformulated.

**Phase to address:** Literature Scoping (Phase 8)

---

### Pitfall 2: Mistaking a structural analogy for a reduction

**What goes wrong:** IQP's classical-hardness argument is a specific, conditional theorem: sampling from IQP circuits within constant additive error is classically hard unless the polynomial hierarchy collapses, *conditional on* two technical conjectures (an IQP-analogue of the permanent-anticoncentration conjecture, and an IQP-analogue of the "permanent of Gaussians is hard to estimate" conjecture). Boson sampling's hardness argument is a structurally similar but *separately proven* theorem, conditional on its own analogous pair of conjectures (anticoncentration + average-case permanent-estimation hardness), and it holds only for a specific circuit ensemble (Haar-random linear-optical unitaries acting on Fock states, roughly Haar-uniform, with modes scaling appropriately relative to photon number). Mapping IQP's gates onto phase shifters/beamsplitters and observing "this also looks like it should be hard to sample from" is not a proof that hardness transfers — it requires either (a) an explicit reduction showing the photonic circuit's output distribution reduces to (or from) IQP's/boson-sampling's known-hard distribution in the formal reduction sense, or (b) an independent re-derivation of both technical conjectures for the new, structured (non-Haar-random) circuit ensemble the mapping actually produces.

**Why it happens:** All three hardness stories (IQP, boson sampling, GBS) share surface features — commuting/passive/Gaussian-flavored operations, PH-collapse-style average-case arguments, anticoncentration lemmas — which makes them look like instances of one general principle. They are not; each was proven separately, for a specific circuit ensemble, and the conjectures involved are ensemble-specific (a permanent-of-Gaussians conjecture for boson sampling is not automatically true for a structured circuit built to encode IQP's diagonal-gate structure, which is emphatically *not* Haar-random).

**Specific failure patterns to watch for while writing the design doc:**
- Treating "the circuit family is expressive enough to represent IQP's polynomials" as equivalent to "sampling from it is hard" — expressiveness and hardness are different claims; the latter needs anticoncentration + average-case hardness separately.
- Getting the **direction of reduction** backwards — showing a photonic circuit *can simulate* IQP (one direction) says nothing about whether *classically simulating the photonic sampler* is hard (the actually-wanted direction). A hardness claim needs the reduction to run from the known-hard problem *into* an efficient description of the new sampler, not the other way around.
- Silently switching **error models** — IQP's additive-constant-error hardness and boson sampling's related results are not interchangeable with multiplicative-error or exact-sampling claims; a mapping that "seems to preserve hardness" under one error notion may say nothing under another, and downstream papers/talks often drop this qualifier without noticing.

**How to avoid:** For Phase 9 (Encoding Design), write the mapping's claims in the same conditional, conjecture-named form the source papers use ("this construction would inherit X's hardness *if* conjecture Y also holds for the derived ensemble — Y has not been checked here"), rather than an unqualified "this is hard" or "this inherits IQP's hardness." Explicitly state which direction of reduction (if any) has been sketched, and flag it as informal/on-paper, not a proof, per the milestone's own scope (implementation and any real complexity-theoretic derivation are out of scope for this milestone — the design doc should say so rather than imply otherwise).

**Warning signs:** The design doc uses "hard" or "hardness" without naming a specific conjecture or paper it's conditional on; the doc never states which direction the reduction runs; the phrase "should inherit" or "likely preserves" appears without a stated falsifiable check (see Pitfall 5).

**Phase to address:** Encoding Design (Phase 9)

---

### Pitfall 3: Over-extending boson-sampling intuitions to a structurally different photonic circuit class

**What goes wrong:** Boson sampling's hardness proof applies to a specific ensemble: Haar-random (or Haar-like) passive linear-optical unitaries, acting on single-photon Fock states (or specific Gaussian/squeezed input states for GBS), measured via photon-number counting, with mode count scaling appropriately relative to photon number for anticoncentration to hold (the literature's own caveat: submatrices need to "look Gaussian," which needs the mode count to scale polynomially/quintically faster than photon number in some regimes). An IQP-inspired mapping is the opposite of Haar-random by construction — it's built from a *specific, structured* sequence of phase shifters and beamsplitters chosen to encode IQP's commuting diagonal gates and Hadamard-basis conjugation, not a random unitary. "This is also linear optics, and linear optics can be hard (boson sampling proves it), so this should be hard too" is exactly the over-extension to guard against — the proof techniques (permanent-based hardness, anticoncentration over a Haar-random ensemble) do not automatically apply to a structured, non-random circuit family.

**Why it happens:** Boson sampling is the most famous photonic hardness result, making it the default mental anchor for "photonic circuits can be hard to simulate" — but its hardness is a property of the *ensemble*, not of "linear optics" as a general resource.

**A second-order version of this pitfall:** even granting that a boson-sampling-flavored hardness argument could somehow be constructed for the IQP-photonic mapping, boson sampling's own hardness is fragile under realistic noise — photon loss provably destroys the intractability (there exist efficient classical algorithms simulating lossy boson sampling within constant total-variation distance in general), with hardness surviving only under specific, narrow conditions (loss scaling logarithmically with photon number, in some recent GBS-specific results). An "ideal circuit is hard" claim inherited loosely from boson sampling says nothing about a realizable one, and this fragility is *itself* one of the two questions the parent research question explicitly asks about (whether the photonic translation "degrades the way boson sampling's hardness argument degrades under photon loss/noise").

**How to avoid:** In the literature-scoping phase, explicitly search for and read the boson-sampling hardness proof's stated assumptions (Haar-randomness, mode-scaling regime, collision-free/anticoncentration conditions), not just its headline result, so the design phase can check each assumption against what the IQP mapping actually produces. Do not cite boson-sampling hardness or its noise-resilience results (e.g., logarithmic-loss thresholds) as applying to the derived circuit without re-deriving or explicitly flagging the gap.

**Warning signs:** The design doc or any note cites "boson sampling is hard, and this circuit is also linear optics" as a complete argument; noise/loss resilience is asserted by analogy to GBS's log-loss-threshold result without checking whether that result's derivation conditions (specific input-state ensemble, specific loss model) match the IQP-photonic construction.

**Phase to address:** Literature Scoping (Phase 8) for gathering the actual assumption list; Encoding Design (Phase 9) for checking the mapping against it.

---

### Pitfall 4: Naive gradient-variance-vs-system-size sweep is a known-misleading test in this exact photonic setting

**What goes wrong:** "Barren plateau" is not a single, cleanly-transplantable concept from qubit variational circuits to continuous-variable/photonic ones, and a straightforward "plot gradient variance vs. number of modes" sweep — the check this milestone's Phase 3 (out of scope for v2.0, but the design phase should anticipate it) explicitly proposes — has documented, specific failure modes in the CV/photonic setting that don't have a clean qubit analog:

- **Circuit energy is a hidden, load-bearing variable with no qubit equivalent.** In bosonic continuous-variable VQCs, gradient variance decays as roughly `1/E^(Mν)` — exponential in mode count `M` but *polynomial* in per-mode circuit energy `E` (a tunable parameter that doesn't exist in the qubit picture). A sweep that varies system size without fixing or reporting circuit energy is measuring a different, entangled quantity, and could show or hide a plateau purely as an energy-scaling artifact.
- **Gaussian vs. non-Gaussian operations change which analytic tools even apply.** The rigorous barren-plateau results for bosonic VQCs are proven for Gaussian states/operations (where CV analogs of qubit tools exist); extending them numerically to a non-Gaussian ansatz (which an IQP-inspired encoding, with its Hadamard-basis-conjugated diagonal structure, plausibly requires) is not automatically justified — the infinite-dimensional Hilbert space of CV systems lacks the finite-dimensional t-design machinery qubit barren-plateau proofs rely on.
- **Postselection/measurement scheme changes the qualitative answer, not just the number.** For *passive* photonic circuits specifically (closer to what an IQP-photonic mapping likely uses — phase shifters + beamsplitters, no squeezing), recent work shows gradient-variance scaling is governed by how the chosen postselection scheme (allow-bunching/collision-free filtering vs. dual-rail encoding vs. others) redistributes weight across the circuit's representation-theoretic structure — different schemes give *polynomial* decay in some cases and *exponential* (but at a slower rate than standard qubit 2-design plateaus) in others, for the *same underlying circuit*, depending only on the readout convention.
- **Finite-size deception is a named, measured effect in this exact setting.** For dual-rail postselection specifically, the same source found the gradient-variance-vs-N curve is genuinely ambiguous between a polynomial and an exponential fit across N=2–10 modes — the polynomial model is *nominally favored* on that range — but the fit "flips decisively to exponential" once measured out to N=24. A sweep that stops at small N (as is very likely for this project, given simulation cost and no-implementation-yet scope) risks a false "no barren plateau" read that a slightly larger sweep would reverse.

**Why it happens:** The phrase "barren plateau" is imported wholesale from the qubit variational-circuit literature, where it has one well-defined meaning (exponentially-vanishing gradient variance with qubit count, tied to unitary 2-designs). Applying the same sweep methodology to a CV/photonic system without checking whether the underlying theory transfers is a natural but unjustified shortcut.

**How to avoid:** The design-phase doc should not promise a bare "measure gradient variance vs. system size" check as sufficient for a trainability verdict later. Instead, it should specify (a) that circuit energy per mode will be fixed or explicitly swept as its own axis, (b) whether the ansatz is Gaussian-only or includes non-Gaussian elements, and what that implies for which prior results even apply, (c) which postselection/measurement convention is used and that this choice is expected to materially change the trainability answer, and (d) that any conclusion needs an explicit model-comparison (polynomial vs. exponential decay fit) run out to a system size large enough to distinguish them — not eyeballed off a handful of small points. This is a design-phase responsibility even though the actual sweep is a later phase's work, because the encoding choice (Gaussian-only vs. not, which postselection scheme) determines which of these caveats even apply.

**Warning signs:** Any future claim of "no barren plateau observed" based on fewer than roughly 10-20 modes, with no stated circuit-energy control, and no explicit polynomial-vs-exponential model comparison.

**Phase to address:** Encoding Design (Phase 9) — must specify these parameters up front so the later trainability study (out of scope for v2.0) isn't designed into this trap; flag it explicitly for whichever future phase does run the sweep.

---

### Pitfall 5: Declaring the mapping "designed" without a concrete, falsifiable check

**What goes wrong:** The plan doc's own Phase 1 description says the design must be something the owner "can defend," and its finish criteria elsewhere state a negative result ("it doesn't preserve X") is a valid, reportable outcome. But a design write-up that describes an isomorphism-flavored narrative — "diagonal gates become phase shifters, Hadamard conjugation becomes beamsplitters, measurement becomes photon counting" — without stating in advance *what a small-scale check would need to show to count as the mapping failing* is not actually falsifiable. If no failure condition was ever specified, then Phase 2's later brute-force sanity check (comparing against classically-simulable small IQP instances) either trivially "passes" (because nothing precise enough to fail was pinned down) or any mismatch gets quietly rationalized as an implementation detail rather than treated as evidence the design itself is wrong.

**Why it happens:** "Design the encoding" is naturally read as a positive, constructive task (build the mapping), which pulls attention away from also specifying the negative case (what would this mapping predict, concretely enough to be wrong).

**How to avoid:** The design-phase deliverable should include an explicit statement, before any implementation, of: (1) the exact basis correspondence between qubit computational-basis states and the chosen photonic encoding (dual-rail per qubit? genuine Fock/photon-number encoding? something else) — this determines the available gate set, per Pitfall 6 below; (2) at least one concrete small instance (e.g., n=2-3 "qubits") where the mapped circuit's predicted output distribution can be computed by hand or by brute force and compared against a real qubit-IQP simulation; (3) what a mismatch would mean (which step of the mapping it would implicate) rather than treating a generic "small case matches" as sufficient (see the Verification Traps table below — small-case matches are weak evidence on their own).

**Warning signs:** The design doc has no section stating what would falsify the mapping; "verify it reduces to known IQP behavior in a limiting case" (Phase 2's stated job in the plan doc) has no corresponding "and here specifically is what that comparison will check" in the Phase 1 write-up.

**Phase to address:** Encoding Design (Phase 9)

---

### Pitfall 6: Basis-correspondence and gate-algebra mismatches get glossed over as "close enough"

**What goes wrong:** IQP's structure (`H^⊗n D H^⊗n` — Hadamard-conjugated commuting diagonal gates) is defined in the qubit computational basis, a specific finite-dimensional Hilbert space with a specific group structure (Hadamard is a Clifford operation on `(Z/2)^n`). Linear optics operates on a different mathematical object: mode operators and Fock states, with beamsplitters implementing passive (Bogoliubov-type) transformations on those operators. "Beamsplitters create superposition, and so does Hadamard, so beamsplitters are the photonic Hadamard" is the kind of gloss that sounds right but skips the actual required step: verifying the transformation a beamsplitter (or beamsplitter network) induces on the *specific encoding basis chosen* algebraically matches what Hadamard-basis conjugation requires — not just that both operations produce "superposition" in some informal sense. The same risk applies to mapping IQP's diagonal gates onto phase shifters (dimension/basis mismatch between qubit computational-basis diagonal entries and per-mode phase accumulation) and to mapping computational-basis (Z) measurement onto photon-number measurement (which requires first fixing whether the encoding is dual-rail-per-qubit, single-photon-per-mode, or a genuinely different photon-number/Fock encoding with no per-qubit substrate at all — these have different available native gate sets and different pre-existing hardness/simulability literature to check against).

**Why it happens:** Both models offer intuitively similar-sounding primitives (both have a way to "create superposition," both have a "phase" operation, both have a "measurement"), which invites pattern-matching by vibe rather than by verifying the actual induced transformation on the chosen basis.

**How to avoid:** Before finalizing the mapping, write out explicitly which physical states of the photonic system represent which qubit computational-basis strings, and then check the group/algebra correspondence directly (what unitary does this specific beamsplitter network induce on that encoding, and does it match Hadamard-basis conjugation's required action) rather than relying on qualitative similarity.

**Warning signs:** The design doc describes gate correspondences in prose ("beamsplitters play the role of Hadamard") without ever writing the encoding basis down explicitly or checking the induced transformation against it.

**Phase to address:** Encoding Design (Phase 9)

---

### Pitfall 7: Confirmation-biased literature search and premature "search is done" declaration under time-box pressure

**What goes wrong:** The plan doc explicitly time-boxes Phase 8: "if nothing viable turns up in a defined window, this track isn't ready and shouldn't be forced." That framing, combined with genuine interest in this being the more novel/interesting stretch project (the plan doc calls it "the harder, more interesting thing"), creates real pressure to search until finding evidence the mapping *should* work, then stop — rather than searching until confident the negative case (an existing construction, or a known impossibility/simulability result) has also been actively ruled out. Concretely, this shows up as: search queries phrased to confirm ("IQP linear optics construction," "photonic IQP encoding") rather than to disconfirm ("IQP linear optics no known construction," "classically simulable Gaussian continuous-variable circuit classes," "Gottesman-Knill analog continuous variable"); treating "found papers on boson sampling hardness" and "found papers on IQP hardness" as if their mere co-existence supports the mapping, when neither paper says anything about whether the *specific mapping* works (see Pitfall 2); and never searching for the class of result that would actually kill the project — known classically-simulable photonic circuit subclasses. (For context: passive linear optics acting on Gaussian states without a photon-counting/non-Gaussian nonlinearity is a known efficiently-classically-simulable regime in the CV literature — precisely the kind of finding that would matter enormously here and needs to be actively searched for, not stumbled into. Whether the eventual IQP-photonic mapping lands inside or outside that easy class is exactly the kind of question a confirmation-biased search would miss.)

**Why it happens:** Time-boxing under deadline pressure naturally optimizes for "did I find enough to proceed," which is a different (and easier to satisfy) question than "did I find the strongest available case against proceeding."

**How to avoid:** Structure the Phase 8 search explicitly around two separate passes with different goals: (1) a constructive pass — does an IQP↔linear-optics/CV construction already exist (reuse if so); (2) a *disconfirming* pass — search specifically for reasons this shouldn't work (known simulability results for the relevant circuit class, prior attempts noted as failed or abandoned, structural obstructions). Require the go/no-go decision at the end of Phase 8 to cite at least one disconfirming-pass query and its result, not just the constructive pass. This turns the time-box into a forcing function for both directions, not just a countdown to "proceed."

**Warning signs:** A Phase 8 summary that lists only papers supporting feasibility; no search query in the record was phrased to find a reason the project shouldn't proceed; the go/no-go verdict is reached without an explicit list of "searched for and did not find X" negative claims (which, per this project's own established practice — see Phase 7's honest "not confirmed" mechanism verdict — should be reported as informative, not treated as failure to find something).

**Phase to address:** Literature Scoping (Phase 8)

---

### Pitfall 8: Encoding-design work quietly slides into implementation before the design is locked

**What goes wrong:** Since the encoding is explicitly "the actual novel contribution" (plan doc), and MerLin/Perceval low-level circuit fluency already exists from the v1.0 milestone, there's a strong pull to "just check it works" by writing Perceval code as soon as an idea for the mapping forms — especially since the owner's context (per `STATE.md`) shows genuine appetite to move fast on this track (the milestone was explicitly started ahead of the plan doc's own "not before Sept 2" gate). If implementation starts before the on-paper design (basis correspondence, gate algebra, falsifiable check — Pitfalls 5 and 6) is actually written down and defensible, three things go wrong: (a) debugging code becomes a substitute for resolving real design ambiguities (a circuit that "runs" isn't the same as a circuit whose correspondence to IQP is understood); (b) a working small circuit can get *post-hoc rationalized* into looking like it matches a principled mapping, when really the mapping was discovered by trial and error in code, inverting the plan's stated order (design, then verify); (c) it exceeds this milestone's explicit scope, which `STATE.md` records as "Phase 0-1 of the 5-phase plan doc only... implementation/trainability-study/write-up deliberately deferred pending Phase 0's go/no-go verdict."

**Why it happens:** Design work (writing precise basis correspondences and checking gate algebra by hand) is slower and less immediately gratifying than writing runnable code, and existing tooling fluency lowers the activation energy to reach for implementation as a way to "test an idea" that should instead be tested on paper first.

**How to avoid:** Treat any Perceval/MerLin code written during this milestone as a red flag requiring an explicit scope-check, not a natural continuation. If a design idea genuinely needs code to check (e.g., a matrix multiplication too tedious by hand), do the narrowest possible calculation outside the project's actual circuit-building tooling (e.g., a scratch NumPy check of a specific unitary's action) rather than standing up Perceval circuit objects — the latter is a slope toward Phase 2 (implementation) work this milestone explicitly defers.

**Warning signs:** Any commit or file in this milestone that imports `perceval` or builds a `pcvl.Circuit`; the encoding-design phase's deliverable file describes results from "running" something rather than results from writing something down and checking it by hand.

**Phase to address:** Encoding Design (Phase 9)

---

## Technical Debt Patterns

Shortcuts that seem reasonable but create long-term problems for this research project.

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|-----------------|------------------|
| Accepting a structural analogy as sufficient without a formal reduction sketch | Faster path to a written design doc | Downstream trainability/hardness claims rest on an unestablished premise — risks exactly the "positive result you can't explain" outcome the plan doc rules out as a non-finish | Only as an explicitly-labeled "conjecture, not proof" scaffolding step in the design doc — never presented as the final claim |
| Reusing boson-sampling's Haar-random-unitary hardness template without checking IQP's diagonal-gate structure satisfies the same assumptions | Saves deriving a new hardness argument from scratch | Silently smuggles in an assumption (Haar-randomness) a structured IQP-encoding circuit doesn't satisfy | Never acceptable as a stated claim; fine as an initial intuition to interrogate and then either confirm or discard |
| Measuring gradient variance only at small system size (N < 10 modes) because larger sims are expensive and no implementation exists yet | Cheap, fast preliminary read | Finite-size deception (Pitfall 4) — small-N trends have been shown to reverse by N=24 in this exact circuit class | Acceptable only as an explicitly-labeled preliminary probe, with a stated plan to extend before drawing any conclusion |
| Treating "found supporting papers" as "confirmed no existing IQP-photonic construction/no known obstruction exists" | Lets Phase 8 close on schedule | A missed prior construction means Phase 9 "designs" something already published (undercuts novelty) or already shown not to work | Only if the search explicitly included both a constructive pass and a disconfirming pass (Pitfall 7), and the acronym-collision-safe query variants (Pitfall 1) |

## Model-Translation Gotchas

Common mistakes when mapping primitives between the qubit gate model and linear optics.

| Mapping | Common Mistake | Correct Approach |
|---------|-----------------|-------------------|
| IQP diagonal gates → phase shifters | Assuming a per-qubit diagonal unitary maps directly onto a per-mode phase shifter without first fixing the encoding basis (qubit computational-basis strings vs. Fock/photon-number states are different combinatorial objects) | Write the explicit basis correspondence first (which photonic state represents which qubit basis string), then check the phase-shifter action against it |
| IQP Hadamard-basis conjugation (`H^⊗n D H^⊗n`) → beamsplitters | Treating beamsplitters as a drop-in Hadamard analog because "both create superposition" | Verify the actual unitary a given beamsplitter network induces on the chosen encoding basis algebraically matches Hadamard conjugation's required action — not just a qualitative resemblance |
| Computational-basis (Z) measurement → photon-number measurement | Assuming these are equivalent without first deciding the encoding scheme (dual-rail-per-qubit vs. genuine Fock/photon-number encoding vs. other) — each implies a different available gate set and different pre-existing literature | Pin down the encoding scheme explicitly before mapping the measurement step, and note which encoding's literature (if any) the design should be checked against |

## Verification Traps

Checks that look convincing at small/toy scale but are misleading as evidence at the scale the actual claim needs.

| Trap | Symptoms | Prevention | When It Breaks |
|------|----------|------------|-----------------|
| A 2-3 "qubit" brute-force match (Phase 2's planned sanity check) treated as strong confirmation | The mapping "passes" its only stated check | Combine with at least one structurally distinct check designed to fail if a specific mapping step (e.g., the measurement-basis correspondence) was wrong, not just one generic small case | Small Hilbert spaces have limited discriminating power — many wrong mappings can accidentally agree on a 2-3 qubit instance |
| Gradient-variance sweep stopped at small N read as "no barren plateau" | A polynomial-looking fit at N=2-10 | Require an explicit exponential-vs-polynomial model comparison extended to N≈20+ before drawing a conclusion (Pitfall 4) | Documented to flip from polynomial-favored to decisively-exponential between N=10 and N=24 in the closest analogous photonic postselection setting found in the literature |
| "This looked hard to simulate/reason about by hand" treated as evidence of hardness | An intuitive gut-check feels like partial validation | Never cite manual difficulty as complexity evidence — only a stated, conditional hardness argument (Pitfall 2) counts | Always misleading as evidence; acceptable only as a motivating anecdote, never as a claim in the write-up |

## Claim-Integrity Mistakes

Domain-specific rigor risks for a complexity-theory-adjacent research write-up (not security in the software sense).

| Mistake | Risk | Prevention |
|---------|------|------------|
| Citing IQP/boson-sampling hardness results without naming the specific conjecture(s) they're conditional on | Reads as an unconditional hardness claim when the source material is not | Always state hardness claims as conditional and name the conjecture(s), on both the qubit and photonic sides |
| Quoting boson-sampling/GBS noise-resilience results (e.g., logarithmic-loss thresholds) as applying automatically to the derived circuit | The circuit class differs (structured, non-Haar) from the ensemble those resilience results were derived for | Explicitly flag as untested for the new circuit family, or re-derive; never inherit by citation alone |
| Softening or implying away a negative Phase 3-equivalent result to make the project read as more successful | Contradicts this project's own established finish criteria ("a negative result you can explain is a real finish") and its own self-audit culture (see `results/phase7_neighbor_locality_summary.md`'s honest "does not support the mechanism" verdict as this repo's own precedent) | Report negative/null results in the same direct language this repo already uses for Phase 7's findings — never acceptable to soften |

## Explanation/Communication Pitfalls

This project's stated bar is "explainable unaided to Vincent Espitalier" (a photonics expert) — the audience is domain-literate, which raises rather than lowers the precision bar.

| Pitfall | Impact | Better Approach |
|---------|--------|------------------|
| Presenting the mapping via diagram/isomorphism claim without a plain-language statement of exactly which properties are claimed preserved and which aren't | Reader can't locate the claim's actual confidence boundary | State explicitly: "this mapping preserves ___, does not establish ___, and is silent on ___" |
| Using "hard"/"hardness" loosely (colloquial vs. the technical PH-collapse-conditional sense) | A domain expert reader could reasonably read "hard" as an established worst-case result | Use precise complexity language throughout: average-case vs. worst-case, conditional on named conjecture, additive vs. multiplicative error, sampling vs. computing marginals |
| Using the bare "IQP" acronym in conversation/writing without disambiguation | Real confusion risk specifically with a photonics-expert audience, where "Integrated Quantum Photonics" is the more familiar sense | Spell out "Instantaneous Quantum Polynomial-time (IQP)" on first use per document/conversation |

## "Looks Done But Isn't" Checklist

- [ ] **Literature search (Phase 8):** Often missing a check for the acronym-collision problem — verify at least one full search pass used "instantaneous quantum polynomial" spelled out, not bare "IQP."
- [ ] **Literature search (Phase 8):** Often missing a disconfirming pass — verify at least one query was framed to find a reason the project shouldn't proceed (known simulability results, prior failed attempts), not just supporting evidence.
- [ ] **Go/no-go verdict (end of Phase 8):** Often stated as "found supporting papers" — verify it also states what was searched for and *not* found (Pitfall 7).
- [ ] **Encoding design doc (Phase 9):** Often missing an explicit falsifiable-check statement — verify it states what a small-scale comparison would need to show to count as the mapping failing, not just passing.
- [ ] **Encoding design doc (Phase 9):** Often missing an explicit basis-correspondence statement (which photonic state = which qubit basis string) — verify this is written down, not left implicit in a diagram.
- [ ] **Any hardness claim in the design doc:** Often missing the specific conjecture(s) it's conditional on — verify named explicitly, not just "hardness."
- [ ] **Any barren-plateau framing in the design doc:** Often missing a stated circuit-energy control and Gaussian-vs-non-Gaussian scope note — verify both are addressed even though the actual sweep is a later, out-of-scope phase.

## Recovery Strategies

| Pitfall | Recovery Cost | Recovery Steps |
|---------|-----------------|------------------|
| Phase 8 declared done, but a directly-relevant paper surfaces later | LOW-MEDIUM | Re-open Phase 8 briefly; document the new source explicitly rather than silently folding it into Phase 9 as if it had always been known; note in the decision log if it changes the design's novelty framing |
| Phase 9's mapping later found (in a future implementation phase) to violate a basis/algebra requirement | MEDIUM | This is an expected, healthy outcome per the plan doc's own honesty framing — document exactly what broke and which mapping step it implicates, then either revise the mapping or downgrade the claim to "attempted, doesn't preserve X"; don't force-fit |
| A small-N gradient-variance read gave a false "no plateau" impression, caught only after further work | MEDIUM-HIGH | Extend the sweep to larger N before finalizing any conclusion; treat the earlier small-N read as explicitly preliminary rather than a retraction — this is a documented, expected trap in this exact photonic setting, not a unique failure |
| Confirmation-biased search missed a known classically-simulable subclass that undercuts the whole track | HIGH (could invalidate downstream design work) | Run the disconfirming-pass search retroactively before investing further in Phase 9; if found, this is exactly the kind of outcome the plan doc's time-box exists to catch early — report it and stop, don't route around it |

## Pitfall-to-Phase Mapping

| Pitfall | Prevention Phase | Verification |
|---------|-------------------|----------------|
| 1. Acronym collision poisons search | Literature Scoping (Phase 8) | Search log shows at least one full pass using the spelled-out term, not bare "IQP" |
| 2. Analogy mistaken for reduction | Encoding Design (Phase 9) | Design doc states hardness claims conditionally, names conjectures, states reduction direction |
| 3. Boson-sampling over-extension | Literature Scoping (Phase 8) / Encoding Design (Phase 9) | Design doc cross-checks the mapping's circuit ensemble against boson sampling's stated assumptions (Haar-randomness, mode-scaling regime) rather than citing the headline result alone |
| 4. Misleading gradient-variance sweep | Encoding Design (Phase 9) | Design doc specifies circuit-energy control, Gaussian/non-Gaussian scope, postselection scheme, and a stated minimum system-size range for any future sweep |
| 5. Unfalsifiable "designed" declaration | Encoding Design (Phase 9) | Design doc includes an explicit falsification statement and at least one concrete small-instance check plan |
| 6. Basis/algebra mismatch glossed over | Encoding Design (Phase 9) | Design doc contains an explicit written basis correspondence and a checked (not assumed) gate-algebra match |
| 7. Confirmation-biased literature search | Literature Scoping (Phase 8) | Go/no-go verdict cites both a constructive-pass and a disconfirming-pass search result |
| 8. Design work sliding into implementation | Encoding Design (Phase 9) | No `perceval`/MerLin circuit-building code exists in this milestone's commits; any calculation-by-code is scratch-only, outside the project's circuit tooling |

## Sources

- Bremner, Montanaro, Shepherd — "Average-case complexity versus approximate simulation of commuting quantum computations" (IQP hardness, conditional on IQP-analogue conjectures) — https://arxiv.org/abs/1504.07999
- "Achieving quantum supremacy with sparse and noisy commuting quantum computations" — https://arxiv.org/abs/1610.01808
- "Quantum Sampling Problems, BosonSampling and Quantum Supremacy" (survey covering assumptions/regimes for boson sampling hardness) — https://arxiv.org/pdf/1702.03061
- "On computational complexity and average-case hardness of shallow-depth boson sampling" — https://arxiv.org/pdf/2405.01786 / https://quantum-journal.org/papers/q-2026-03-13-2026/
- "Sufficient conditions for hardness of lossy Gaussian boson sampling" (logarithmic-loss-threshold hardness-preservation result) — https://arxiv.org/abs/2511.07853
- "Quantum Computational Advantage of Noisy Boson Sampling with Partially Distinguishable Photons" (PRX Quantum) — https://journals.aps.org/prxquantum/abstract/10.1103/rflv-gc66
- "Transition of Anticoncentration in Gaussian Boson Sampling" (Phys. Rev. Lett.) — https://journals.aps.org/prl/abstract/10.1103/PhysRevLett.134.140601
- "Energy-dependent barren plateau in bosonic variational quantum circuits" — https://arxiv.org/abs/2305.01799 (also IOPscience: https://iopscience.iop.org/article/10.1088/2058-9565/ad80bf)
- "Pre-Asymptotic Trainability in Photonic Variational Circuits under Postselection" (postselection-scheme-dependent trainability, finite-size deception at N=2-10 vs. N=24) — https://arxiv.org/html/2605.11879
- "Investigating and mitigating barren plateaus in variational quantum circuits: a survey" — https://link.springer.com/article/10.1007/s11128-025-04665-1
- Live search finding (this session, 2026-07-30): querying `"IQP" linear optics photonic encoding construction arxiv` returns "Integrated Quantum Photonics" as the dominant sense, confirming Pitfall 1's acronym-collision risk directly rather than by inference.
- Project-internal precedent for this repo's own rigor/honesty culture (informs Pitfalls 5, 7, and the Claim-Integrity table, not photonics-specific facts): `.planning/milestones/v1.0-MILESTONE-AUDIT.md`, `results/phase7_neighbor_locality_summary.md`, `DESIGN_DECISIONS.md`, `Post_Sept1_IQP_Photonic_Plan.md`, `.planning/STATE.md`

---
*Pitfalls research for: IQP → photonic circuit encoding (literature scoping + on-paper design)*
*Researched: 2026-07-30*

---

# Pitfalls Research — v2.1 Addendum: Weight-2 Heralded CZ Implementation

**Domain:** Heralded/probabilistic linear-optical two-qubit gates (Knill CZ / KLM family) in Perceval, integrated into the existing weight-1 photonic IQP encoding module (`iqp_photonic_encoding.py`)
**Researched:** 2026-08-05
**Confidence:** HIGH — the load-bearing claims below were verified by direct inspection of the installed `perceval-quandela` package source (`venv/Lib/site-packages/perceval/components/core_catalog/heralded_cz.py`, `experiment.py`) and by running small scripts against `catalog['heralded cz']` in this repo's own venv, not by citing secondhand literature. Literature figures (1/9, 2/27) are cited only where independently reproduced numerically in this venv.

**Scope note:** This addendum covers the v2.1 milestone (implementing and measuring `heralded_cz`-based weight-2 generators, building on v2.0's shipped weight-1 module) and supersedes nothing above — the v2.0 pitfalls (literature scoping, encoding design) remain valid background. This section is scoped narrowly to the heralded-gate implementation/measurement task itself.

## Critical Pitfalls

### Pitfall 9: Conflating `.performance`/`global_perf` (herald success) with `.distribution`/`results` (conditional output)

**What goes wrong:**
Both `pcvl.algorithm.Analyzer` and `Processor.probs()` silently return an **already-renormalized, conditional-on-success distribution** as the main result. `Analyzer.distribution` sums to 1 by construction — it does NOT tell you how often the herald actually fires. The herald/success probability lives in a *separate* attribute (`Analyzer.performance`, or `Processor.probs()['global_perf']`) that is easy to never look at, especially since the project's existing weight-1 code (`iqp_photonic_encoding.py::run_full_circuit`) only ever reads `analyzer.distribution` — that pattern has no herald, so `.performance` was never relevant there.

**Why it happens:**
Weight-1 code was written and validated (ENC-04, TVD ~1e-16) against a deterministic, herald-free circuit where `performance == 1.0` always, so nothing forced acknowledging the attribute. Copy-pasting the same `run_full_circuit`-style helper for weight-2 will compute a distribution that looks perfectly normal (sums to 1, no errors) while quietly discarding the actual success-probability measurement the milestone exists to produce.

**Verified in this repo's venv (2026-08-05):**
```python
exp = catalog['heralded cz'].build_experiment()
proc = pcvl.Processor('SLOS', exp)
analyzer = pcvl.algorithm.Analyzer(proc, [pcvl.BasicState([1,0,1,0])], '*')
analyzer.compute()
# analyzer.distribution -> conditional dist, sums to 1 (looks fine, tells you nothing about success rate)
# analyzer.performance   -> 0.0740740740740741  (the actual herald success probability, 2/27)
```
`Processor.probs()` mirrors this exactly: `res['results']` is the conditional distribution, `res['global_perf']` is the physical success probability. With `proc.compute_physical_logical_perf(True)` set, it further splits into `physical_perf` (photon-loss/leakage in the whole unitary evolution — 1.0 here, since nothing is lost, just filtered) and `logical_perf` (herald-click-pattern + valid-dual-rail-output condition combined) — `global_perf = physical_perf * logical_perf` in this gate.

**How to avoid:**
Any weight-2 measurement helper must explicitly capture and return `analyzer.performance` (or `probs()['global_perf']`) as a first-class output, not an afterthought — treat "what's the success probability" as a separate return value from "what's the output distribution," never inferred from the distribution alone.

**Warning signs:**
A weight-2 result report that only shows a normalized output distribution with no separate success-probability number is the tell — if the milestone's actual deliverable ("measure `heralded_cz`'s success probability") can't be read directly off one specific field in the code's output, the measurement wasn't actually taken.

**Phase to address:** The implementation/measurement phase itself (first thing built), not a later validation pass — the whole point of this milestone is this number.

---

### Pitfall 10: Manually constructing a `StateVector`/superposition input skips the automatic herald-ancilla injection that `BasicState` input gets for free

**What goes wrong:**
`Experiment.with_input` is multiply-dispatched by input type, and the two paths behave very differently:
- `with_input(BasicState/FockState/list/tuple)` — you supply only the **logical** (non-herald) modes (`exp.m == 4` for `heralded cz`, not the internal `circuit_size == 6`); Perceval auto-inserts the ancilla herald photons at the internal herald mode positions (mode 4, 5) for you, and auto-sets `min_detected_photons_filter = input_state.n`.
- `with_input(StateVector/SVDistribution/NoisyFockState)` — bypasses that convenience entirely. It asserts `svd.m == self.circuit_size` (the FULL internal size, 6, including herald modes) and raises `AssertionError` if you pass a 4-mode superposition. If you correctly pad it to 6 modes (manually adding the `,1,1` ancilla photons yourself), `probs()` will then raise a *different* error (`min_detected_photons_filter is not set`) because that auto-set only happens on the `LogicalState`/`BasicState` path.

**Verified in this repo's venv:** both failure modes reproduced directly — a 4-mode `StateVector` raises `AssertionError: ... bad size (4), expected 6`; correctly padding to 6 modes and calling `probs()` without first calling `proc.min_detected_photons_filter(n)` raises `ValueError: The value of min_detected_photons is not set.`

**Why it happens:**
For a weight-2 IQP diagonal-phase generator, the interesting inputs are superpositions (the whole point of the `|+>`-conjugated middle layer), so this project *will* need `StateVector`/`SVDistribution` input at some point (e.g. to check the gate's action on a superposition directly, independent of the `Analyzer`'s automatic basis sweep) — unlike weight-1, where `all_h_input` only ever built pure computational-basis `BasicState`s and never hit this path.

**How to avoid:** Prefer driving weight-2 experiments through `Analyzer(processor, [BasicState(...)], '*')` over the full logical basis (as weight-1 already does) rather than hand-building `StateVector` inputs — it's the same convenience path already proven in this codebase. If a direct `StateVector` input is genuinely needed, explicitly pad to `circuit_size` (not `exp.m`) with the herald ancilla counts, and explicitly call `min_detected_photons_filter(...)` first.

**Warning signs:** An `AssertionError` about mode-size mismatch, or a `ValueError` about `min_detected_photons`, when testing a hand-built superposition input — both indicate the wrong `with_input` overload was hit, not a physics bug.

**Phase to address:** Implementation phase, specifically whenever any test goes beyond the `Analyzer`-over-computational-basis pattern already established for weight-1.

---

### Pitfall 11: Assuming heralding == post-selection (or writing code that accidentally implements post-selection instead)

**What goes wrong:**
The project's own design doc (`docs/iqp-photonic-encoding.md`) already correctly distinguishes heralding (accept/reject based on ancilla-mode detector clicks, independent of the data-qubit measurement) from post-selection (accept/reject based on the data-mode measurement outcome itself) at the conceptual level — but that distinction has to survive into the actual measurement code, and it is easy to lose. `core_catalog.heralded_cz`'s `build_experiment()` adds heralds via `add_herald(4, 1)` / `add_herald(5, 1)` — these are genuinely separate ancilla modes (4, 5), disjoint from the 4 logical data modes (0-3: ctrl dual rail + data dual rail). But Perceval's `logical_perf`/`global_perf` in `Processor.probs()` actually bundles the herald condition together with a **second, distinct** filter: rejecting output patterns on the *data* modes that fall outside the valid dual-rail (exactly-one-photon-per-rail) subspace. That second filter is cheap to conflate with "post-selection" language but is not what this project means by post-selection avoidance.

**Why it happens:**
`logical_perf` sounds like it should be "the herald probability," but per the source it's actually P(herald clicks correctly AND output data state is a valid logical dual-rail state) — i.e., it already includes a portion that *is* a post-selection-like filter (on the data output), stacked with the true heralding filter (on the ancilla output). For an ideal, lossless gate acting on valid dual-rail inputs, the "bunched/leaked data output" component is typically zero or negligible so `logical_perf ≈` pure herald probability in practice — but that's a property of this specific gate/input regime, not a guarantee, and should be checked rather than assumed silently.

**How to avoid:** When reporting "the herald success probability," explicitly decompose and state which Perceval-reported number is being cited (`physical_perf`, `logical_perf`, `global_perf`), and verify that no probability mass in the *rejected* set actually comes from the "data output outside valid dual-rail subspace" case rather than "herald ancilla modes didn't click." A cheap check: sum `analyzer.distribution` (or `probs()['results']`) restricted to malformed/bunched data-mode outcomes with the herald condition dropped, and confirm it's ~0 for the inputs actually used, before treating `logical_perf` as a pure heralding number.

**Warning signs:** A reported success probability that doesn't match a hand re-derivation of "P(herald clicks)" from the raw (pre-filter) output distribution is the tell that some other filter (data-mode post-selection) snuck into the number.

**Phase to address:** Measurement/validation phase — this is exactly the kind of subtle semantic gap the project has a track record of catching (the H/V port-labeling bug in weight-1 was caught the same way: a direct empirical check rather than trusting the API's naming).

---

### Pitfall 12: Assuming a single, input-independent success probability without checking it across the actual generator's input regime

**What goes wrong:**
Literature figures for the general Knill-CZ family (1/9 post-selected, ~2/27 heralded) are quoted for the gate acting generically — this project's actual use case is narrower: the gate is always preceded by `PBS` (polarization → dual rail) and followed by `PBS` (dual rail → polarization) at a fixed θ=π/4, inserted into a specific IQP diagonal layer where the "data" input arriving at the gate is always a **product of two independent `|+>`-derived single-qubit states** (from the state-prep + weight-1 diagonal layer), never an arbitrary two-qubit state. It would be a mistake to assume without checking that the measured success probability is the same across (a) computational basis inputs, (b) the actual `|+>`-family inputs this circuit produces, and (c) inputs after other weight-1 phases have already been applied.

**Verified in this repo's venv (2026-08-05):** for all four computational-basis inputs (`|00>`,`|01>`,`|10>`,`|11>` in dual-rail), `global_perf` was identical to 10+ significant figures (≈0.074074074074074, i.e. 2/27 exactly) — consistent with this being an input-independent property of the *unitary* part of the gate (the herald condition is on ancilla modes only, decoupled from the data state, so this is expected for any gate design that's supposed to work as a general-purpose CZ). One superposition case (`ctrl=|+>, data=|0>`) also reproduced `global_perf ≈ 2/27`, consistent with input-independence — but this was only spot-checked, not exhaustively verified across entangling cases (e.g. `ctrl=|+>, data=|+>`).

**How to avoid:** Explicitly measure (don't assume) the success probability using the actual inputs the weight-2 generator will see in the full pipeline (post-`PBS`, post-weight-1-layer states), not only bare computational-basis states — and state in the milestone's writeup whether it was found to be input-independent (expected, given the herald is decoupled from the data modes) or not, rather than silently generalizing from one spot-check.

**Warning signs:** A single number reported for "the success probability" with no statement of which input(s) it was measured against.

**Phase to address:** Validation phase, alongside the classical TVD sanity check (ENC-04-style extension).

---

### Pitfall 13: `heralded_cz`'s `build_circuit()` alone has no herald — only `build_experiment()`/`build_processor()` do

**What goes wrong:**
`catalog['heralded cz'].build_circuit()` returns a plain 6-mode `pcvl.Circuit` with **no heralds attached at all** — it's just the linear-optical unitary. The existing weight-1 module (`iqp_photonic_encoding.py`) is built entirely around composing raw `pcvl.Circuit` objects with `circuit.add(pos, component)` and wrapping the whole thing in a single `Processor("SLOS", circuit)` at the end. If weight-2 code follows that exact pattern — grabbing `build_circuit()` and splicing it into a bigger `Circuit(2n)` the same way `HWP`/`WP`/`PBS` are added today — the herald condition is silently dropped: the simulation will still run and produce *some* distribution, but it will be the **full, unheralded 6-mode unitary's raw output**, not the heralded, success-probability-weighted CZ. This would produce numbers that look plausible (no crash, a valid distribution) but are physically wrong for what the milestone needs.

**Why it happens:** The catalog's `build_circuit()`/`build_experiment()`/`build_processor()` three-tier API (confirmed by direct inspection of `CatalogItem`) makes it easy to reach for the `Circuit`-returning method out of habit, since that's the type every other component in this project's existing code uses (`pcvl.HWP`, `pcvl.WP`, `pcvl.PBS` are all added directly as circuit components).

**How to avoid:** Weight-2 code must use `build_experiment()` or `build_processor()` (which attach the `add_herald(4,1)`/`add_herald(5,1)` calls, per direct source read of `heralded_cz.py`), and compose it into the larger pipeline via `Processor.add(mode_mapping, component)` (which accepts a mode offset) rather than `Circuit.add`. This is a structural break from the pure-`Circuit`-composition style weight-1 uses — expect (and budget time for) an actual API-shape change, not a drop-in extension of `build_full_circuit`.

**Warning signs:** A weight-2 run whose output distribution has support on more than the expected valid dual-rail computational states (e.g. bunched/leaked states appearing in the *conditional* result, or the "success probability" always coming out as 1.0) is the signature of an unheralded raw unitary being run instead of the actual heralded gate.

**Phase to address:** Implementation phase — verify by construction, before running anything else on it, that the assembled processor's `heralds` property is non-empty (`{4: 1, 5: 1}` in the bare-gate case; renumbered once embedded).

---

### Pitfall 14: Mode-index renumbering when embedding a heralded sub-block breaks the existing `2*k`/`2*k+1` qubit-layout convention

**What goes wrong:**
`Experiment.m` (the mode count "of interest," i.e. what input/output BasicStates are indexed against) is defined as `self._m - len(self.heralds)` — heralded modes are silently excluded from the external numbering once a herald is added. `heralded_cz`'s bare `build_experiment()` has `circuit_size == 6` internally but `exp.m == 4` externally. The existing weight-1 layout convention (`iqp_photonic_encoding.py`'s docstring: "qubit k occupies 2 adjacent spatial modes, port 2*k and 2*k+1") is written entirely in terms of a flat `Circuit(2n)` with no heralds anywhere — there is no established convention yet in this codebase for how ancilla/herald modes interleave with that `2*k`/`2*k+1` numbering once weight-2 introduces 2 extra internal (herald) modes per CZ application, on top of the 4 dual-rail modes (2 qubits × 2 rails, from `PBS`-converting each qubit's existing 2-mode polarization block).

**Why it happens:** Weight-1's mode-numbering convention was designed and validated before any herald/ancilla modes existed in the picture; nothing in the existing code or its tests exercises non-contiguous or herald-excluded mode numbering, so there's no established, tested pattern to reuse — it has to be designed fresh, and a naive port of the `2*k`/`2*k+1` convention will not automatically map input BasicStates and output readouts correctly around the herald-mode gap unless the offset arithmetic is worked out explicitly and tested.

**How to avoid:** Before writing the full weight-2 circuit, write a small, throwaway script (mirroring the direct-inspection style already used for weight-1's H/V port-labeling check) that builds a 2-qubit `Processor` embedding `heralded_cz` via `Processor.add(mode_mapping, ...)`, confirms `processor.m` and `processor.heralds` match expectations, and round-trips a known computational-basis dual-rail input through it before extending `fock_to_bitstring`/`basic_state_to_bitstring`-equivalent helpers to the weight-2 case.

**Warning signs:** Any weight-2 output-parsing helper that assumes a flat, contiguous `2n`-mode layout (like weight-1's `2*k`/`2*k+1` helpers) will either crash on an unexpected mode count or, worse, silently misparse herald-adjacent modes as if they were qubit modes — the latter is the dangerous case, since it fails quietly the same way the H/V labeling bug did.

**Phase to address:** Implementation phase, as an explicit calibration/round-trip check before building the full weight-2 pipeline — same pattern that caught the weight-1 H/V bug (empirical check prompted by the owner's own attempt, not an assumption from the API docs).

---

## Technical Debt Patterns (v2.1 addendum)

| Shortcut | Immediate Benefit | Long-term Cost | When Acceptable |
|----------|-------------------|----------------|-----------------|
| Reusing weight-1's `run_full_circuit`/`Analyzer`-only pattern verbatim for weight-2 without also capturing `.performance` | Fast to write, matches existing code style | Silently ships a measurement that never actually reports the herald probability — defeats the milestone's stated purpose | Never — this milestone's core deliverable IS the success-probability number |
| Citing literature's 1/9 or 2/27 figures instead of measuring `global_perf`/`.performance` directly | Saves a few lines of code | Directly contradicts the milestone's explicit goal ("measure `heralded_cz`'s actual success probability... rather than relying on secondhand literature figures") and the project's own recorded open item that this figure is unverified for this exact gate | Never for the final reported number; fine only as a sanity-check upper/lower bound while debugging |
| Treating `logical_perf` as if it were purely the herald probability without checking the data-output-validity component is negligible | One fewer verification step | Risk of quietly re-introducing post-selection semantics into a number meant to represent pure heralding | Acceptable only after the negligibility check (Pitfall 11) has actually been run once and recorded |
| Testing only computational-basis inputs, generalizing to "the success probability is 0.074, period" | Simpler test matrix | Overclaims input-independence without exhaustively checking the entangling-input case this circuit will actually see | Acceptable as an interim finding IF explicitly flagged as not-yet-exhaustive, per this project's honest-reporting norm |

## Integration Gotchas (v2.1 addendum)

| Integration | Common Mistake | Correct Approach |
|-------------|----------------|-------------------|
| `catalog['heralded cz']` → existing `Circuit(2n)`-based pipeline | Grabbing `build_circuit()` (no heralds) and `circuit.add()`-splicing it in, matching the `HWP`/`WP`/`PBS` pattern already in `iqp_photonic_encoding.py` | Use `build_experiment()`/`build_processor()` and `Processor.add(mode_mapping, component)`; verify `processor.heralds` is non-empty post-assembly |
| `Analyzer`/`Processor.probs()` output → weight-1-style `dist = {state: prob}` extraction | Reusing `run_full_circuit`'s dict-comprehension verbatim, which only reads `analyzer.distribution`/`res['results']` | Also capture `analyzer.performance` / `res['global_perf']` (and, if `compute_physical_logical_perf(True)` is set, `physical_perf`/`logical_perf` separately) as an explicit, separate return value |
| Superposition test inputs for the weight-2 gate | Hand-building a `StateVector` at the gate's *logical* mode count (4) | Either stay on the `Analyzer`-over-`BasicState`-list pattern (matches `exp.m`, gets auto ancilla-fill), or if using `StateVector`/`SVDistribution` directly, pad to `circuit_size` (includes herald modes) and call `min_detected_photons_filter(...)` first |
| Extending `exact_qubit_iqp_distribution` (weight-1, `iqp_photonic_encoding.py`) to include a ZZ term for weight-2 validation | Ad-hoc bolting a `Z_i*Z_j` phase term onto the existing per-qubit-loop implementation without re-deriving the bit-index/Z-eigenvalue convention already documented for weight-1 | Reuse the exact same `(1 if bit_k==0 else -1)` Z-eigenvalue convention per qubit already established for weight-1, and add `thetas_zz[(i,j)] * (1 if bit_i==bit_j else -1)` (`Z_i⊗Z_j` eigenvalue is `+1` when bits agree, `-1` when they differ) as an additional phase term — keep it in the same closed-form numpy reference function so it stays independently checkable against Perceval's output the same way ENC-04 already validates weight-1 |
| Reference-distribution semantics: qubit-side ZZ term vs. photonic-side conditional-on-herald output | Comparing the qubit-side *exact unitary* CZ/ZZ prediction directly against the photonic side's *unconditional* (raw, includes-failure) distribution | The qubit-side exact reference must be compared against the photonic side's **conditional-on-herald-success** distribution (`analyzer.distribution` / `probs()['results']`), since that's the distribution the herald's acceptance already selects for being the "ideal CZ" output; the success probability itself is a separate, additional number to report alongside the TVD, not folded into it |

## "Looks Done But Isn't" Checklist (v2.1 addendum)

- [ ] **Weight-2 measurement code**: often reports only a normalized output distribution — verify a distinct, explicitly-labeled success-probability number (`.performance` or `global_perf`) is also captured and printed/logged.
- [ ] **Weight-2 circuit assembly**: often "runs without error" even when heralds were never attached — verify `processor.heralds` (or equivalent) is non-empty immediately after assembly, before running anything downstream.
- [ ] **Weight-2 validation (TVD-style)**: often compares against the wrong side of the herald conditioning — verify the qubit-side exact reference is being compared against the *conditional* photonic distribution, and that the success probability is reported as a separate number, not baked into or confused with the TVD result.
- [ ] **Success-probability claim**: often generalizes from one input case — verify it was checked (or explicitly flagged as un-checked) against the actual `|+>`-derived, potentially-entangling inputs this circuit produces, not only bare computational-basis states.
- [ ] **Mode-index bookkeeping post-herald-embedding**: often silently assumes the old flat `2*k`/`2*k+1` convention still holds — verify with an explicit round-trip check (build → run known input → confirm output parses back to the expected bitstring) before trusting any output-parsing helper extended from weight-1.

## Pitfall-to-Phase Mapping (v2.1 addendum)

| Pitfall | Prevention Phase | Verification |
|---------|------------------|---------------|
| 9. Conflating success probability with conditional distribution | Implementation | Code explicitly returns/prints `.performance` (or `global_perf`) as its own labeled output, distinct from the distribution dict |
| 10. `StateVector` input skipping ancilla auto-injection | Implementation (only if `StateVector`/`SVDistribution` input is used at all) | A superposition test input round-trips without `AssertionError`/`ValueError`; if hit once during dev, documented as the reason `Analyzer`-over-`BasicState` was preferred |
| 11. Heralding vs. post-selection semantic drift (`logical_perf` bundling) | Validation | A recorded check that malformed/bunched-data-output probability mass is negligible for the inputs actually used, before citing `logical_perf`/`global_perf` as "the herald probability" |
| 12. Input-dependence of the measured success probability | Validation | Success probability measured (not assumed) across at least: computational basis, and the actual `|+>`-derived inputs the full pipeline produces; result explicitly labeled with which inputs were tested |
| 13. `build_circuit()` (no herald) used by mistake instead of `build_experiment()`/`build_processor()` | Implementation | `processor.heralds` non-empty check run and recorded before any downstream measurement |
| 14. Mode-index renumbering breaking the weight-1 layout convention | Implementation | A throwaway calibration script (mirroring the weight-1 H/V check) round-trips a known input through the embedded weight-2 block before the full pipeline is built |

## Sources (v2.1 addendum)

- `venv/Lib/site-packages/perceval/components/core_catalog/heralded_cz.py` (installed `perceval-quandela` package, this repo's venv) — direct source read: confirms `build_circuit()` has no herald, `build_experiment()` adds `add_herald(4,1)`/`add_herald(5,1)`, article ref arXiv:quant-ph/0110144 (Knill 2002).
- `venv/Lib/site-packages/perceval/components/experiment.py` — direct source read: `add_herald` sets both input AND output expected photon count by default (`location=IN_OUT`); `Experiment.m = self._m - len(self.heralds)`; the `with_input` multiple-dispatch table for `FockState`/`BasicState` (auto-fills herald ancillas + auto-sets `min_detected_photons_filter`) vs. `StateVector`/`SVDistribution` (requires full `circuit_size`, no auto-filter).
- Direct empirical runs against `perceval.components.catalog['heralded cz']` in this repo's venv (2026-08-05): `global_perf`/`analyzer.performance` measured as ≈0.0740740740740741 (= 2/27, matching the literature figure for the *heralded* Knill CZ variant, independently reproduced rather than cited secondhand) across all 4 computational-basis dual-rail inputs and one spot-checked superposition input; `physical_perf == 1.0` in all cases (no photon loss in the unitary evolution itself — the entire cost is the herald/logical filter).
- `docs/iqp-photonic-encoding.md` (this repo) — existing project derivation of the `PBS → heralded_cz → PBS` weight-2 construction and the CZ/ZZ operator identity (`exp(iθZ_iZ_j) = CZ · exp(iθZ_i) · exp(iθZ_j)` up to global phase at θ=π/4); already correctly distinguishes heralding from post-selection conceptually, cross-checked here at the code/API level.
- `iqp_photonic_encoding.py` (this repo) — existing weight-1 implementation and its documented mode-layout/bit-ordering conventions, used as the baseline for identifying where weight-2 diverges structurally.

---
*Pitfalls research addendum for: heralded two-qubit photonic gate (Perceval `core_catalog.heralded_cz`), v2.1 weight-2 milestone*
*Researched: 2026-08-05*
