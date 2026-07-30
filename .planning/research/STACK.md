# Stack Research

**Domain:** Quantum computing research (photonic QML) — literature scoping + on-paper encoding design for an IQP-to-photonics mapping. No implementation phase in this milestone.
**Researched:** 2026-07-30
**Confidence:** MEDIUM-HIGH (Perceval API verified against installed version + current docs; literature findings verified across multiple independent papers, but literature scoping is never exhaustive by nature — treat the "no DV mapping found" conclusion as this milestone's own Phase 0 starting point, not a closed case)

## Headline finding (answers the downstream consumer's key question)

**No existing published construction maps IQP circuits onto discrete-variable (Fock-basis) linear optics** — the physical model MerLin/Perceval actually uses (phase shifters, beamsplitters, photon-number-resolving detection). This milestone's "invent, don't just reproduce" framing in `Post_Sept1_IQP_Photonic_Plan.md` still holds.

However, **partial, directly relevant prior art exists one layer over, in continuous-variable (CV) optics**:

- **Douce, Markham, Kashefi, Diamanti, Coudreau, Milman, van Loock, Ferrini, "Continuous-Variable Instantaneous Quantum Computing is hard to sample,"** *PRL* 118, 070503 (2017), [arXiv:1607.07605](https://arxiv.org/abs/1607.07605). This is a real IQP→photonics reduction — it defines **CV-IQP**, an IQP analogue built from squeezed states and finitely-resolved homodyne detection, and proves a hardness-of-sampling result that survives the CV translation (with squeezing scaling logarithmically in circuit size, i.e. polynomial energy cost — the CV analogue of the boson-sampling noise/loss degradation problem this milestone's Phase 3 asks about).
- This is **not directly portable** to Perceval/MerLin: it's Gaussian-state/homodyne CV optics, not Fock-state/photon-counting DV optics. Perceval and MerLin are DV. Treat Douce et al. as the closest known analogue and a template for *how to structure a hardness argument under photonic translation*, not as a construction to reproduce as-is.
- **Adjacent but non-equivalent:** Park & Oh, "Matrix product state approach to lossy boson sampling and noisy IQP sampling" ([arXiv:2510.24137](https://arxiv.org/abs/2510.24137), Oct 2025, rev. Jul 2026) analyzes IQP sampling and boson sampling **as parallel case studies under one MPS simulation toolkit**, not as physically equivalent systems. Useful for understanding how the two hardness stories are compared in current literature, not a mapping.
- **Adjacent, worth reading for methodology (not mapping):** Gottlieb, Faraji, Mezher, Ventura, Mansfield, Salavrakos, "Efficient training of photonic quantum generative models" ([arXiv:2603.08793](https://arxiv.org/abs/2603.08793), Mar 2026, rev. Jul 2026) — appears to be Quandela-affiliated (author list matches Quandela researchers), studies MMD-trained photon-native generative models where deployment = boson sampling. This is the closest thing to a "sibling" of the owner's own v1.0 MerLin project and may cite/be cited by whatever the owner finds on trainability of photonic ansätze — worth a citation-chase step in Phase 0, separate from the IQP question specifically.

**Practical consequence for the plan:** Phase 0 (literature scoping) is not a quick confirm-and-move-on — it should explicitly (a) read Douce et al. in full to extract which structural ideas transfer to DV Fock-basis (e.g., how they define the analogue of "diagonal commuting gates" and "Hadamard-basis conjugation" for continuous quadratures — the owner's Phase 1 will need a DV-native version of the same two ingredients), and (b) forward/backward citation-chase Douce et al. (2017, well-cited) for any follow-up work that specifically targets DV/Fock optics, since a 2017 paper is old enough that someone may have since asked exactly this milestone's question. Do this chase via Semantic Scholar's citation graph (see Development Tools below) before concluding the DV gap is genuinely open.

## Recommended Stack

### Core Technologies

| Technology | Version | Purpose | Why Recommended |
|------------|---------|---------|-----------------|
| perceval-quandela | 1.2.4 (installed; current as of 2026-07-02 release) | Low-level photonic circuit construction (`Circuit`, `comp.PS`, `comp.BS`, `BasicState`, `Processor`, `Analyzer`, `Sampler`) | Already installed and pinned in `requirements.txt`; this is the actual substrate MerLin sits on, and Phase 1's encoding design must be expressible in Perceval's primitives to be implementable in a later milestone. No version bump needed. |
| merlinquantum | 0.4.0 (installed) | Photonic QML layer wrapper (already used in v1.0 via `QuantumLayer.simple()`) | Not directly needed for this milestone's two tasks (scoping + on-paper design don't require running code), but keep installed/pinned since Phase 2 (deferred) will need it and version drift between now and then should be tracked. |
| Python | 3.10–3.12 (repo venv) | Runtime | Matches existing repo constraint; Perceval 1.2.4 supports up to 3.14 so no compatibility pressure to upgrade. |

### Supporting Libraries (for the literature-scoping task specifically)

| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| `arxiv` (PyPI: `arxiv`, by lukasschwab) | latest (2.x) | Programmatic arXiv search/metadata pull | If the owner wants a reusable, scriptable search across many query variants (e.g. sweeping "IQP linear optics," "IQP boson sampling," "commuting diagonal gates photonic") rather than one-off web searches. Optional — see "What NOT to Use" below. |
| Semantic Scholar API (no library needed — plain `requests` against `api.semanticscholar.org/graph/v1`) | current, free tier (no key required; key optional for higher rate limit) | Citation-graph traversal: find what cites/is-cited-by Douce et al. 2017 and Bremner-Montanaro-Shepherd's original IQP hardness paper | This is the single most valuable literature tool for this milestone's actual open question ("has anyone extended Douce et al. to DV/Fock optics since 2017?") — citation-chasing beats keyword search for finding follow-on work to a specific known paper. |

### Development Tools

| Tool | Purpose | Notes |
|------|---------|-------|
| Web search (Claude/browser) + arXiv abstract pages | Ad hoc literature scoping | Sufficient for the breadth-first part of Phase 0 (this research already did a first pass — see findings above). Don't build tooling around this; a milestone this narrowly scoped (2 tasks, no code) doesn't justify a search pipeline. |
| Semantic Scholar web UI (semanticscholar.org) citation graph view | Manual citation-chase on Douce et al. 2017 and Bremner-Montanaro-Shepherd | Faster than the API for a one-time, small citation walk (dozens of papers, not hundreds) — use the API only if the citation list turns out large enough to need filtering/scripting. |
| Perceval `Circuit`, `comp.PS`/`comp.BS`, `BasicState`, `Processor`, `Analyzer`, `Sampler` classes (already installed) | Reference for Phase 1's on-paper design — even though Phase 1 doesn't write code, the encoding must be describable in terms these classes actually support | Confirmed current: `perceval.Circuit(m)` for an m-mode circuit, `c.add((i,j), comp.BS())` / `c.add(i, comp.PS(Parameter(...)))` for manual placement, `pcvl.BasicState('|0,2,0,1>')` or `BasicState([0,2,0,1])` for Fock-state inputs, `Processor("SLOS", circuit).with_input(...)` to bind input+circuit, `Analyzer` for full output-distribution tables, `Sampler` for finite-shot sampling. Source: [Perceval v0.13 circuits docs](https://perceval.quandela.net/docs/v0.13/circuits.html), [Perceval v0.13 tutorial](https://perceval.quandela.net/docs/v0.13/notebooks/Tutorial.html). |

## Installation

No new installs required for this milestone's two tasks (literature scoping, on-paper design) — both are non-code deliverables.

```bash
# Already present in requirements.txt — nothing to add for Phase 0/1 of this milestone.
# Optional, only if the owner wants scriptable arXiv search instead of ad hoc web search:
pip install arxiv
```

Do not add anything to `requirements.txt` for this milestone unless Phase 2 (deferred, minimal implementation) actually starts — adding deps now for work that may not happen creates version-drift risk for no benefit.

## Alternatives Considered

| Recommended | Alternative | When to Use Alternative |
|-------------|-------------|--------------------------|
| Ad hoc web search + direct arXiv abstract fetch for Phase 0 | `arxiv` Python library scripted search | If the owner wants a persistent, rerunnable search log (e.g. to show search queries/results as part of the milestone's paper trail for defensibility to Vincent) — a script is more auditable than ad hoc browsing. Not necessary for correctness, only for documentation rigor. |
| Semantic Scholar for citation-chasing | Google Scholar (manual, no API) | Google Scholar has broader coverage and is fine for a single manual check, but has no stable free API and aggressively rate-limits scraping — use it as a spot-check, not a primary tool. |
| Perceval low-level API (`Circuit`/`comp.PS`/`comp.BS`) for Phase 1's design vocabulary | Strawberry Fields / Xanadu's photonic SDK | Strawberry Fields is CV-native (squeezed states, homodyne) and would actually be the *better* match if the owner decides to pursue the CV-IQP (Douce et al.) direction instead of a DV/Fock mapping — flag this as a live fork-in-the-road for Phase 1, not a settled choice. See "Stack Patterns by Variant" below. |
| Qiskit's `qiskit.circuit.library.IQP` class as the qubit-side reference implementation | PennyLane's IQP embedding utilities, or IQPopt (JAX-based, arXiv:2501.04776) | The owner already has Qiskit/PennyLane-adjacent fluency per project context. Qiskit ships a canonical `IQP` circuit class (see [IBM Quantum docs](https://docs.quantum.ibm.com/api/qiskit/qiskit.circuit.library.IQP)) that's a good, minimal, well-documented reference for "what does textbook IQP actually look like as a circuit" when writing the Phase 1 mapping spec. IQPopt is a JAX package purpose-built for *training/optimizing* large IQP circuits at scale (barren-plateau-style studies) — more relevant to the deferred Phase 3 (trainability study) than to this milestone's scoping/design tasks. Don't install either now; both are reference reading, not runtime dependencies for Phase 0/1. |

## What NOT to Use

| Avoid | Why | Use Instead |
|-------|-----|--------------|
| Strawberry Fields as a *runtime* dependency for this milestone | This milestone has no code deliverable — adding a second photonic framework (on top of Perceval/MerLin) before even knowing whether the target is DV or CV is premature. It also duplicates Perceval's role and would fragment the eventual Phase 2 implementation across two SDKs. | Keep Strawberry Fields as *reading material only* (its docs are a clean reference for CV gate vocabulary) until Phase 1 concludes whether the mapping is DV or CV. |
| A dedicated literature-review tool/framework (e.g. LitLLM, reference managers, systematic-review software) | This is a scoped, time-boxed literature check per the plan doc ("Time-box this — if nothing viable turns up in a defined window, this track isn't ready"), not a systematic review. Standing up review tooling is scope creep for a milestone whose own finish criteria are modest. | Web search + a handful of targeted arXiv/Semantic Scholar lookups, written up directly in the milestone's Phase 0 findings doc. |
| Treating Douce et al. (2017) as "the answer" and skipping straight to reproduce-and-extend | It's CV, not DV — MerLin/Perceval are DV/Fock-basis. Conflating the two physical models would produce a Phase 1 design that can't actually be built in Perceval later, which is exactly the "invent nothing, then discover it doesn't fit the toolchain" failure mode this research is meant to prevent. | Use Douce et al. as a structural template (how they defined CV analogues of "commuting diagonal gates" and "basis-conjugation") and translate that structure into DV/Fock primitives explicitly, as its own Phase 1 step — don't assume translation is free. |
| Bumping `perceval-quandela`/`merlinquantum`/`torch` versions as part of this milestone | No code runs in Phase 0/1; version bumps belong with the actual implementation milestone (Phase 2, deferred) so they can be tested against real usage, not speculatively bumped now. | Leave `requirements.txt` untouched until Phase 2 begins; re-check current versions at that point since more releases will have shipped by then. |

## Stack Patterns by Variant

**If Phase 1 concludes the encoding should be DV/Fock-basis (the "native MerLin" path):**
- Design vocabulary: Perceval's `Circuit`, `comp.PS` (phase shifter), `comp.BS` (beamsplitter), `BasicState` (Fock input), `Analyzer`/`Sampler` (photon-number measurement).
- Because no published DV mapping exists (per the headline finding), this is genuinely the milestone's "actual novel contribution," as the plan doc already anticipates — budget Phase 1 accordingly, don't expect to find shortcuts mid-design.

**If Phase 1 concludes the encoding should follow the CV-IQP precedent (Douce et al.) instead:**
- This would be a *scope change* from the plan doc's implicit assumption (MerLin/Perceval, which is DV) — flag it explicitly rather than silently pivoting, since it would mean either (a) reproduce-and-extend Douce et al. directly in a CV framework (Strawberry Fields, not Perceval), or (b) attempt a DV/Fock discretization of the CV-IQP construction, which is itself a novel step needing its own justification.
- Either sub-path is a bigger scope decision than this STACK.md should make — surface it as an explicit fork for the roadmap/requirements step, not something to resolve here.

## Version Compatibility

| Package A | Compatible With | Notes |
|-----------|------------------|-------|
| perceval-quandela==1.2.4 | Python 3.10–3.14 | Repo venv (3.10–3.12) is well within range; no compatibility risk for this milestone's scoping/design work (which doesn't even require running Perceval, only knowing its primitives). |
| merlinquantum==0.4.0 | torch<2.13 (repo constraint), perceval-quandela>=1.2.1 | Installed torch is 2.12.1 — inside the `<2.13` ceiling. Not exercised in this milestone but noted for continuity into the deferred Phase 2. |

## Sources

- [arXiv:1607.07605](https://arxiv.org/abs/1607.07605) — Douce, Markham, Kashefi et al., "Continuous-Variable Instantaneous Quantum Computing is hard to sample," PRL 118, 070503 (2017). HIGH confidence (peer-reviewed, WebFetch-verified abstract).
- [arXiv:2510.24137](https://arxiv.org/abs/2510.24137) — Park & Oh, "Matrix product state approach to lossy boson sampling and noisy IQP sampling" (Oct 2025, rev. Jul 2026). MEDIUM confidence (WebFetch-verified abstract; preprint, not yet confirmed peer-reviewed venue).
- [arXiv:2603.08793](https://arxiv.org/abs/2603.08793) — Gottlieb, Faraji, Mezher, Ventura, Mansfield, Salavrakos, "Efficient training of photonic quantum generative models" (Mar 2026, rev. Jul 2026). MEDIUM confidence (metadata verified; full text not fetched — page limit hit).
- [Perceval v0.13 circuits documentation](https://perceval.quandela.net/docs/v0.13/circuits.html) and [tutorial](https://perceval.quandela.net/docs/v0.13/notebooks/Tutorial.html) — HIGH confidence, cross-checked against locally installed `perceval-quandela==1.2.4` in the repo venv.
- [PyPI: perceval-quandela](https://pypi.org/project/perceval-quandela/) — HIGH confidence, confirms 1.2.4 released 2026-07-02, i.e. currently the latest release (repo is not on a stale version).
- [IBM Quantum docs: qiskit.circuit.library.IQP](https://docs.quantum.ibm.com/api/qiskit/qiskit.circuit.library.IQP) — HIGH confidence, official docs, useful as the owner's qubit-side reference implementation.
- [arXiv:2501.04776](https://arxiv.org/abs/2501.04776) — "IQPopt: Fast optimization of instantaneous quantum polynomial circuits in JAX." MEDIUM confidence (abstract-level only); relevant to deferred Phase 3, not Phase 0/1.
- Local repo files verified directly: `requirements.txt`, installed `venv/Lib/site-packages` (perceval-quandela 1.2.4, merlinquantum 0.4.0, torch 2.12.1) — HIGH confidence, ground truth.

---
*Stack research for: IQP → photonic circuit encoding (literature scoping + on-paper design milestone)*
*Researched: 2026-07-30*
