# Phase 8: Literature Scoping & Prerequisites - Research

**Researched:** 2026-07-31
**Domain:** Quantum complexity literature (IQP hardness, CV vs. DV constructions), Perceval low-level linear-optical circuit API, reference-doc compilation
**Confidence:** HIGH for Perceval API and Douce et al. paper content (both verified directly — live code execution and full-text PDF read); MEDIUM for the literature-scoping conclusion (WebSearch-based, not an exhaustive arXiv/Scholar crawl — this research pass itself is evidence toward, but not a substitute for, the owner's own LIT-01/LIT-04 pass)

## Summary

This phase has three independent deliverables, and research turned up concrete, verified material for all three. First, the **Douce et al. (2017) paper was read in full text** (not just abstract) via a freely available PDF mirror — its CV construction is now well understood and clearly does *not* transfer to a Fock-space/discrete-variable encoding, which matters for how Phase 9's design should be positioned against it. Second, a **literature scan for an existing DV/Fock-space linear-optical IQP construction found nothing** — multiple targeted searches (direct IQP-photonics terms and structural-analogue terms) surfaced boson sampling, Gaussian boson sampling, and CV-non-Gaussian-complexity papers, but no construction matching IQP's defining structure (input in a fixed basis, commuting diagonal gates, Hadamard-conjugated measurement) built from photon-counting/Fock-basis linear optics. This is consistent with the CONTEXT.md's "go" bar (absence of a proven obstruction is sufficient) — nothing found, and no impossibility result found either. Third, the **Perceval low-level API was fully verified by running actual code** against this repo's installed `perceval-quandela` 1.2.4: a minimal beamsplitter circuit was built with `Circuit`/`BS`/`BasicState`/`Analyzer` (no `QuantumLayer.simple()`), executed, and its output checked against the textbook closed-form prediction (including the Hong-Ou-Mandel dip), with the print-out captured in this document.

**Primary recommendation:** Frame LIT-04's verdict as "go" (no blocking impossibility found, DV construction remains open territory) rather than "not ready" — per CONTEXT.md's bar, a time-box expiring with nothing found is not itself "not ready." For PREQ-01, use the two-circuit demo below (single photon through `BS.H()`, then two photons through the same circuit for the HOM dip) — both are closed-form-verifiable and were actually run in this environment, not just described. For PREQ-02, the sibling project's `docs/technical/iqp-classical-sampling.md` and the vault's `Theory/Barren Plateaus.md` + `Report/Final Findings.md` are the strongest source material and are summarized below.

## Standard Stack

No new libraries needed for this phase — everything required is already installed in this repo's `venv` (`perceval-quandela==1.2.4`, confirmed via `importlib.metadata.version`).

### Core
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| `perceval-quandela` | 1.2.4 (installed) | Low-level linear-optical circuit construction and simulation | Already the project's photonic backend (via MerLin); this phase demonstrates the layer beneath MerLin's `QuantumLayer.simple()` wrapper |

No supporting libraries, no alternatives to weigh — this phase is scoping/reading/one small script, not new engineering.

## Architecture Patterns

### Pattern: Perceval low-level circuit build (Circuit / PS / BS / BasicState / Analyzer)

**What:** Build a circuit directly from linear-optical components, wrap it in a `Processor`, and use `Analyzer` to get exact output probabilities — bypassing MerLin's `QuantumLayer` entirely.

**Verified import paths** (checked against the installed package — `Analyzer` is NOT exported at the top-level `pcvl` namespace, unlike `Circuit`/`BS`/`PS`/`BasicState`):
```python
import perceval as pcvl                       # Circuit, BS, PS, BasicState, Processor all live here
from perceval.algorithm import Analyzer        # Analyzer must be imported from perceval.algorithm explicitly
```

**Minimal example — actually executed in this repo's venv, output captured verbatim:**
```python
import perceval as pcvl
from perceval.algorithm import Analyzer

# Single photon through a 50/50 beamsplitter (Hadamard convention: real, symmetric)
circuit = pcvl.BS.H()                          # BS.H(theta=pi/2) — the balanced/Hadamard-like convention
proc = pcvl.Processor("SLOS", circuit)         # "SLOS" = strong linear optical simulation backend
input_state = pcvl.BasicState([1, 0])          # one photon in mode 0, vacuum in mode 1
analyzer = Analyzer(proc, [input_state], "*")  # "*" = compute all reachable output states
analyzer.compute()
print(analyzer.distribution)                  # [[0.5+0.j 0.5+0.j]]
print(analyzer.output_states_list)             # [|0,1>, |1,0>]
```
**Verified output:** `[[0.5+0.j 0.5+0.j]]` over `[|0,1>, |1,0>]` — matches the textbook closed-form prediction exactly (a single photon on a 50/50 beamsplitter has a 50% chance of exiting either port, no interference term possible with one photon).

**Second example — Hong-Ou-Mandel dip, also verified live:**
```python
circuit2 = pcvl.BS.H()
proc2 = pcvl.Processor("SLOS", circuit2)
input_state2 = pcvl.BasicState([1, 1])         # one indistinguishable photon in EACH port
analyzer2 = Analyzer(proc2, [input_state2], "*")
analyzer2.compute()
print(analyzer2.distribution)                  # [[0. +0.j 0.5+0.j 0.5+0.j]]
print(analyzer2.output_states_list)             # [|1,1>, |0,2>, |2,0>]
```
**Verified output:** `P(|1,1>) = 0`, `P(|0,2>) = P(|2,0>) = 0.5` — this is the textbook Hong-Ou-Mandel effect: two indistinguishable photons entering a balanced beamsplitter, one per port, always bunch into the same output port (never split 1-1), a well-known closed-form result any quantum optics reference will confirm.

Either example (or both, showing the progression from a trivial 50/50 split to the two-photon interference effect) satisfies PREQ-01's "compare against a known closed-form result" requirement, since both were computed and match hand-derivable predictions exactly — not just "eyeballed."

### Pitfall: `Analyzer` requires a `Processor`, not a bare `Circuit`
`Analyzer.__init__` type-hints its first argument as `AProcessor` (see `perceval/algorithm/analyzer.py`), and asserts every input `BasicState` has `.m == self._processor.m`. Passing a bare `Circuit`/`BS`/`PS` object directly to `Analyzer` will fail — it must first be wrapped: `pcvl.Processor("SLOS", circuit)`. `"SLOS"` is the standard exact simulation backend name used throughout Perceval's own docs and this project's dependency tree.

### Pitfall: default `BS()` uses the Rx convention, not the Hadamard convention
`BS()`'s default constructor (`perceval/components/unitary_components.py`) is `BS(theta=pi/2, ..., convention=BSConvention.Rx)`, giving the unitary `[[1, i], [i, 1]]/√2` (complex, with `i` on the cross terms). `BS.H(...)` gives `[[1, 1], [1, -1]]/√2` (real, Hadamard-like). Both are 50/50 splitters for single-photon *probability* (verified — single-photon output was identical 50/50 under both conventions when tested), but they differ in the *phase* imprinted on superpositions, which matters for anything beyond single-photon inputs (e.g. the HOM dip's exact interference pattern depends on which convention and which relative phases are used). For a demo whose entire point is "convention-robust closed-form check," `BS.H()` is the safer choice since its real-valued matrix has no phase-convention subtlety to get wrong when hand-deriving the expected result.

### Pitfall: `BasicState` accepts multiple constructor forms — pick one and be consistent
Verified via `perceval/utils/states.py`: `BasicState([1, 0])` (list), `BasicState("|1,0>")` (string), and `BasicState(m)` (bare mode count, for a vacuum state) are all valid, dispatched via `multipledispatch`. Mixing string and list forms in the same script is fine functionally but reads inconsistently — the plan should pick one form (list form used above) for the demo script.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Computing output probabilities for a small fixed circuit | A manual amplitude/permanent calculation | `perceval.algorithm.Analyzer` | It already does exactly this (iterates input states, calls the `Sampler`, builds a distribution matrix) — reimplementing it defeats the point of "API fluency," which is to use the library's own analysis tool correctly |
| Checking that a result "looks close" to the closed form | Visual/eyeball comparison of printed probabilities | Compare `analyzer.distribution` values against the exact expected fractions (0.5, 0, 0.5, etc.) programmatically or by direct arithmetic in the writeup | CONTEXT.md explicitly requires more than eyeballing; both examples above have exact rational closed forms (0.5, 0), making an exact-match assertion trivial to write |

## Literature Findings (LIT-01, LIT-02)

### LIT-02: Douce et al. (PRL 118, 070503, 2017; arXiv:1607.07605) — read in full text

**Full citation:** T. Douce, D. Markham, E. Kashefi, E. Diamanti, T. Coudreau, P. Milman, P. van Loock, G. Ferrini, "Continuous-Variable Instantaneous Quantum Computing is hard to sample," Phys. Rev. Lett. 118, 070503 (2017).

**Access:** The arXiv PDF (`arxiv.org/pdf/1607.07605`) is fetchable, but WebFetch cannot parse PDF binary content directly — the fix was to fetch the PDF as binary (it gets saved to a local temp path by the WebFetch tool) and then re-read that saved file with the `Read` tool, which does handle PDF text extraction. This is the correct approach for the owner (or a future Claude session) if a fresh full-text read is ever needed again — a direct `WebFetch` prompt-and-extract on a PDF URL silently fails without this two-step workaround.

**What the construction actually is** (verified by reading the full paper, not the abstract):

The paper's DV-IQP recap (Fig. 1, left, in the paper) is the standard construction: all qubits start in `|+⟩` (X-eigenstate +1), a layer of gates diagonal in the Z-basis is applied (these commute — hence "instantaneous," no fixed gate ordering required), and measurement is in the X-basis (`{|±⟩}`).

The **CV analogue** (Fig. 1, right) swaps every DV ingredient for its continuous-quadrature counterpart:
- **Input:** finitely-squeezed states `|σ⟩_p` (squeezed in the momentum/p̂ quadrature) instead of qubit `|+⟩` states.
- **Gates:** a gate `D̂_q(n)`, a uniform combination of elementary gates `{Ẑ = e^{iq̂√π}, ĈZ = e^{iq̂₁q̂₂}, T̂}`, all diagonal in the **position quadrature q̂** — the direct analogue of "diagonal in the Z-basis." These commute for the same structural reason DV IQP's diagonal gates commute.
- **Measurement:** finite-resolution **homodyne detection of p̂** (the conjugate quadrature) — the analogue of the X-basis measurement, since p̂ and q̂ are Fourier-conjugate the same way X and Z are Hadamard-conjugate.

**"Hadamard-basis conjugation" in this paper specifically means:** the DV Hadamard gate (which maps Z-diagonal structure into the X-measurement basis) is realized in CV via the **Fourier transform operator** `F̂ = e^{i(π/4)(p̂²+q̂²)}`, sandwiching the q̂-diagonal gates the same way Hadamards sandwich Z-diagonal gates in DV IQP (`H⊗ⁿ D H⊗ⁿ`). This Fourier gadget is realized via a measurement-based "Hadamard gadget" analogue (their Fig. 2/3, Supplemental Material "Ingredient 1") — a CV `ĈZ`-based teleportation-like circuit, post-selected on a specific homodyne outcome, that implements the Fourier transform on an unknown input state.

**The hardness argument's structure** (three steps, explicitly laid out in the paper):
1. **Fourier gadget:** adding post-selection to the CV-realistic IQP class (called "CVrIQP" — realistic = finite squeezing + finite-resolution homodyne) yields a universal gate set, so `CVrMBQC ⊆ PostCVrIQP`.
2. **Error correction:** GKP (Gottesman-Kitaev-Preskill) encoding of a qubit into an oscillator corrects the errors from finite squeezing/finite resolution, giving `CVrMBQC = BQP` for sufficiently high resolution (this leans on prior work, not new in this paper).
3. **Post-selection:** the logical-qubit post-selection defining `PostBQP` maps onto the CV hardware, completing `PostCVrIQP ⊇ PostBQP` — i.e., CVrIQP inherits DV IQP's known hardness (any classical algorithm efficiently sampling it would collapse the polynomial hierarchy, per the same complexity-theoretic argument original DV IQP hardness proofs use).
4. A key added requirement, not present in the idealized DV case: because real squeezing is always finite, the proof only goes through if the **squeezing parameter scales logarithmically with circuit size** (`Δ²_dB > O(log n)`), which translates into a **polynomial scaling of input energy** with circuit size — this is the paper's most novel quantitative contribution beyond "the DV argument transfers."

**Why this does NOT transfer to a Fock-space/DV linear-optical construction (important for positioning Phase 9):** this paper's "CV" means continuous-quadrature encoding — squeezed light, homodyne detection, GKP bosonic-qubit encoding — entirely in the position/momentum quadrature formalism. It is a fundamentally different physical encoding from a **Fock-space/photon-number** linear-optical circuit (phase shifters + beamsplitters + photon-counting detectors, i.e. what Perceval/MerLin actually simulate). The paper contains **no mention whatsoever** of photon-number/Fock-basis measurement, boson sampling, or discrete linear-optical networks — it is squarely in the "CV = quadrature" tradition (Menicucci, van Loock, GKP), not the "CV = many photon-number levels" sense sometimes used loosely. This confirms the project's own prior framing (in STATE.md's Accumulated Context) that Douce et al. is a reproduction of DV-IQP hardness in a different (quadrature) encoding, not a template that hands you a DV/Fock-space construction — a genuinely new DV/Fock-space IQP analogue would need to be built from scratch, motivating Phase 9.

### LIT-01: Search for an existing DV/Fock-space linear-optical IQP construction — none found

**Search methodology used (within the CONTEXT.md time-box and source scope — arXiv + Google Scholar via WebSearch, no forums, no direct outreach):**

Direct keyword queries tried:
- `IQP linear optics boson sampling discrete variable photonic`
- `"instantaneous quantum polynomial" linear optical circuit photon counting hardness`
- `linear optical circuit commuting phase gates sampling hardness photon number basis "IQP"`

Structural-analogue queries tried:
- Commuting-diagonal-gates and Hadamard-conjugation framing (via the Douce et al. read itself, which explicitly cites the DV IQP definition it builds from — no separate DV-linear-optics paper cited)
- Boson sampling / Gaussian boson sampling adjacency

**What surfaced (none is a match):**
- Boson sampling and Gaussian boson sampling papers (permanent-based hardness — a structurally different argument from IQP's commuting-diagonal-gate / Ising-partition-function argument; these were already known-adjacent, not new leads)
- Jabbour & Novo, "Complexity of Gaussian quantum optics with a limited number of non-linearities" (arXiv:2310.06034, Quantum Sci. Technol. 2025) — CV Gaussian-optics complexity with layered non-linearities and a CV Hadamard-test construction; adjacent in spirit (complexity of optical circuits with a specific gate-layer structure) but still explicitly CV/Gaussian, not DV/Fock-space, and does not construct or cite an IQP analogue
- "Unified boson sampling" (Phys. Rev. Research 7, L042068, 2025) — merges DV scattershot boson sampling with CV Gaussian boson sampling; no IQP connection
- Standard DV-IQP theory papers (Bremner-Jozsa-Shepherd lineage, IQPopt, fault-tolerant IQP compiling) — these are qubit-native, no linear-optical variant proposed

**Verdict basis:** no explicit impossibility/no-go result was found either (nothing in the literature says a DV/Fock-space IQP construction *cannot* exist) — the searches simply didn't surface a construction, positive or negative. Per CONTEXT.md's stated bar, this is a "go": the absence of a proven obstruction is sufficient, and a time-box expiring with nothing found does not by itself count as "not ready." This also is not a "promising lead" case — nothing partial or ambiguous surfaced that would justify a deeper follow-up pass; it's a clean absence in both directions.

**Confidence caveat:** this is a WebSearch-based scan (MEDIUM confidence, not an exhaustive manual arXiv/Google Scholar crawl with citation-chasing). The CONTEXT.md's own search-methodology section calls for the owner to do the actual arXiv + Google Scholar pass; this research provides a head start and a set of query strings already tried (so the owner's own pass shouldn't need to repeat these verbatim) but is not a substitute for LIT-04's required "citing both constructive and disconfirming search passes" — the owner should still run their own pass, ideally with different phrasing, to have independently-conducted evidence to cite.

### LIT-03: Already complete (carried forward, not re-researched)
REQUIREMENTS.md confirms this was verified 2026-07-30 — all 21 titles in MerLin's reproduced-papers catalog (`merlinquantum.ai/0.4/reproduced_papers/`) enumerated, none IQP-adjacent. No further action needed in Phase 8 beyond citing this in the go/no-go writeup for coverage.

## PREQ-02: Source material for `docs/iqp-baseline.md`

**Primary source directory confirmed:** `C:\Users\cuqui\iqp-mmd-barren-plateau\docs\papers` — 9 PDFs present and verified by filename:
`1504.07999v2.pdf`, `1610.01808v4.pdf`, `2012.09265v2.pdf`, `2305.02881v2.pdf` (+ a duplicate `2305.02881-implicit-explicit-losses.pdf`), `2405.00781-barren-plateau-review.pdf`, `2502.07889-warm-start-guarantees.pdf`, `2503.02934v2 (3).pdf`, `2512.24801v1.pdf`.

**Best existing secondary material to pull from (already-written, already-verified summaries — don't re-derive from the raw PDFs if these cover it):**

1. **`iqp-mmd-barren-plateau/docs/technical/iqp-classical-sampling.md`** — an excellent, already-written explainer of IQP circuit structure (Hadamard-sandwiched commuting diagonal gates, exactly matching the Douce et al. DV recap above), the classical-training trick (Van den Nest's cosine formula for `⟨Z_a⟩`), and *why* IQP's commuting structure is what makes this tractable ("All IQP gates commute with each other... so the circuit has no gate ordering to track... For random deep circuits, none of these hold"). This single doc alone likely covers most of the "IQP circuit structure/hardness" half of the 1-2 page baseline doc.

2. **`iqp-mmd-barren-plateau-vault/Theory/Barren Plateaus.md`** — a concise definition (`Var[∂L/∂θᵢ] = O(2^{-αn})`), the "Why This Paper Exists" framing (does IQP's commuting/structured gate set protect trainability the way random unitary-2-design circuits don't?), the average-case-vs-pointwise framing from Larocca et al. 2024, and the project's "Five Possible Conclusions" (A–E) taxonomy.

3. **`iqp-mmd-barren-plateau-vault/Report/Final Findings - IQP MMD Barren Plateaus.md`** — the closing empirical answer: structure alone doesn't predict plateaus; the best empirical rule found is `plateau if small_angle OR (uniform AND n>=6 AND NOT complete_graph_like)` (97.9% accuracy, 100% precision, 97.5% recall across 283 rows); anti-concentration alone is an insufficient success criterion for a learned distribution (target-vs-learned marginal agreement is the better diagnostic).

**Suggested weighting:** CONTEXT.md calls for "roughly equal weight" between IQP structure/hardness and barren-plateau trainability — doc #1 above covers structure/hardness, docs #2+#3 cover barren-plateau trainability and its empirical resolution in the prior project, which naturally balances the two halves.

**Owner's own prior notes:** the vault (`iqp-mmd-barren-plateau-vault/`) is an Obsidian-style note vault with cross-linked pages (`[[Gradient Variance]]`, `[[Research Questions]]`, etc.) — treat the two files above as entry points; other linked pages exist but weren't required reading for a 1-2 page summary doc.

## Repo Conventions for `docs/iqp-baseline.md`

This repo (`merlin-quantum-case-study`) already has a `docs/` directory with two precedent files: `docs/mmd-loss.md` and `docs/raster-order.md`. Both establish the house style for a new reference doc:

- **Grounding statement up top:** `docs/mmd-loss.md` opens with an explicit statement of what was directly read/verified ("Grounded by directly reading the prior project's source... not from memory of either project") — `docs/iqp-baseline.md` should open the same way, citing the specific source files/vault pages it draws from.
- **Section-per-difference / section-per-topic structure**, not one long prose block — headers like "## Difference 1: ...", "## Difference 2: ..." keep it scannable.
- **Code blocks with source attribution** when quoting formulas or implementation (e.g., `kernel.py`'s `gaussian_kernel` shown verbatim with a comment on where it's from).
- **Honesty about corrections** — `docs/mmd-loss.md` includes a dated "Correction" block where an earlier claim in the same doc was found wrong and is left visible with the fix, rather than silently edited. If anything in the iqp-baseline doc later turns out wrong, the same pattern (dated correction, not silent edit) should be followed.
- **Length discipline:** both precedent docs run long (~200-400 lines) covering deep technical comparisons; the CONTEXT.md's 1-2 page cap for `docs/iqp-baseline.md` is intentionally much shorter — a reference/glossary style doc, not a deep-dive like the precedents. Structure suggestion: one short section on IQP circuit structure/hardness (pulling from source #1 above), one short section on barren-plateau trainability + the prior project's empirical answer (pulling from sources #2/#3), and a short "why this matters for Phase 9" bridging paragraph.

`DESIGN_DECISIONS.md` is a different genre (a running decision log with dated entries, options-considered/why-chosen structure) — not the right template for `docs/iqp-baseline.md`, which is a reference doc, not a decision record.

## Common Pitfalls

### Pitfall: conflating "CV" in Douce et al. with "the photon-number/Fock space this project's circuits use"
**What goes wrong:** Someone skimming Douce et al.'s title ("Continuous-Variable...") might assume it already covers what a Fock-space/photon-counting linear-optical IQP analogue would look like, since Perceval/MerLin circuits are also "photonic."
**Why it happens:** "Continuous-variable quantum optics" and "photonic/linear-optical quantum computing with Fock states" are both photonic but are different formalisms (quadrature-continuous vs. photon-number-discrete).
**How to avoid:** Explicitly state, when summarizing Douce et al. for the go/no-go verdict, that its CV construction is quadrature-based (squeezed light + homodyne), not photon-number-based — already done in the LIT-02 section above, worth repeating explicitly in the phase's own writeup so it's unambiguous to a future reader (or interviewer).
**Warning signs:** if the go/no-go verdict or the Douce summary uses "CV" and "DV" without ever spelling out which specific physical quantity is continuous/discrete (quadrature vs. photon number), that's a sign the distinction may have blurred.

### Pitfall: treating a WebSearch-only literature scan as satisfying LIT-04's evidentiary bar on its own
**What goes wrong:** This research pass's LIT-01 findings (nothing found) could be mistaken for a complete literature pass.
**Why it happens:** The search queries used here are a reasonable start but were run through WebSearch, not a systematic arXiv/Google Scholar session with citation-chasing (checking what cites Douce et al., what Douce et al. itself cites for DV IQP, etc.).
**How to avoid:** The phase's actual go/no-go writeup (LIT-04) should have the owner run their own arXiv/Google Scholar pass (per CONTEXT.md's search-methodology section) and cite that pass explicitly, using this research as a starting point/query list, not a replacement.

## Code Examples

See "Architecture Patterns" above for the two verified Perceval examples (single-photon 50/50 split, HOM dip) — both are complete, runnable, and their outputs are quoted verbatim from an actual run in this repo's `venv`.

## State of the Art

Not applicable in the usual "library version churn" sense — this phase's core question (does a DV/Fock IQP construction exist) is a research-literature question, not a tooling-currency question. No relevant deprecations or version changes affect this phase.

## Open Questions

1. **Whether a more exhaustive literature pass (citation-chasing, not just keyword search) would surface a partial/adjacent lead this pass missed.**
   - What we know: keyword + structural-analogue WebSearch queries found nothing matching.
   - What's unclear: whether following citation chains from Douce et al. or from recent IQP-hardness papers (e.g. the 2025 fault-tolerant IQP compiling paper) would surface something.
   - Recommendation: if the owner's own arXiv/Google Scholar pass also comes up empty, treat that as sufficient per the CONTEXT.md bar — this is a "go," and Phase 9 is the place to actually attempt the construction, not further literature archaeology.

2. **Whether Jabbour & Novo (arXiv:2310.06034) is worth a closer read before Phase 9, given it's the closest tangential hit.**
   - What we know: it studies complexity of Gaussian quantum optics with a layered non-linearity structure — some structural resemblance to "circuit with a special gate-layer structure that's easier to analyze."
   - What's unclear: whether its non-linearity layering has any exploitable structural parallel to IQP's diagonal-gate layering, or whether this is a false-positive resemblance.
   - Recommendation: not required reading for LIT-04 (it's CV/Gaussian, not DV/Fock), but flag it as a low-priority skim if Phase 9's design work stalls for ideas.

## Sources

### Primary (HIGH confidence)
- `arxiv.org/pdf/1607.07605` (Douce et al., full text) — read completely via WebFetch (binary save) + Read tool PDF extraction; all LIT-02 claims above trace directly to this read.
- This repo's installed `perceval-quandela` 1.2.4 source (`venv/Lib/site-packages/perceval/`) — `components/unitary_components.py` (BS, PS classes), `utils/states.py` (BasicState), `algorithm/analyzer.py` (Analyzer), `runtime/processor.py` (Processor) all read directly.
- Live execution of the two Perceval code examples above, in this repo's actual `venv` — outputs quoted verbatim, not inferred.
- `C:\Users\cuqui\iqp-mmd-barren-plateau\docs\technical\iqp-classical-sampling.md` — read in full.
- `C:\Users\cuqui\iqp-mmd-barren-plateau\iqp-mmd-barren-plateau-vault\Theory\Barren Plateaus.md` and `Report\Final Findings - IQP MMD Barren Plateaus.md` — read in full.
- This repo's `docs/mmd-loss.md`, `README.md`, `DESIGN_DECISIONS.md` — read for style/convention precedent.
- `.planning/REQUIREMENTS.md` — confirmed LIT-03 completion status verbatim.

### Secondary (MEDIUM confidence)
- WebSearch results on Douce et al.'s abstract (used only to cross-check the full-text read, not as a standalone source) — matched the full-text read exactly.
- WebSearch results identifying Jabbour & Novo (arXiv:2310.06034) and "Unified boson sampling" (PRR 7, L042068) as the closest tangential hits — titles/abstracts corroborated via multiple independent search result snippets, not independently full-text read.

### Tertiary (LOW confidence)
- None of the "nothing found" conclusion is asserted as exhaustive — flagged explicitly above (LIT-01 confidence caveat) as a WebSearch-based scan, not a citation-chasing literature review.

## Metadata

**Confidence breakdown:**
- Perceval API / PREQ-01 code examples: HIGH — actually executed in this repo's environment, outputs verified against closed-form predictions
- Douce et al. summary (LIT-02): HIGH — full text read via PDF, not abstract-level
- Literature absence finding (LIT-01): MEDIUM — WebSearch-based scan, honestly flagged as not exhaustive; the go/no-go verdict itself should still be the owner's, informed by their own pass per CONTEXT.md
- PREQ-02 source material identification: HIGH — files directly located, listed by name, and read in full where used as primary summary sources

**Research date:** 2026-07-31
**Valid until:** Indefinite for the Perceval API findings (stable, version-pinned, verified live) and the Douce et al. summary (published paper, won't change). The LIT-01 absence finding should be treated as time-of-search — re-run if Phase 9 is delayed by more than ~30 days, since new arXiv preprints appear continuously.
