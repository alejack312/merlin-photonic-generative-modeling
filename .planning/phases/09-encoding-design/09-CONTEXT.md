# Phase 9: Encoding Design - Context

**Gathered:** 2026-08-05
**Status:** Ready for planning

<domain>
## Phase Boundary

Produce a defensible, on-paper mapping from IQP's structure (input in a fixed basis, commuting diagonal gates, Hadamard-basis conjugation) onto Perceval's DV/Fock-space primitives (phase shifters, beamsplitters, photon-number measurement) — the milestone's actual novel-contribution deliverable. Output is `docs/iqp-photonic-encoding.md`, satisfying ENC-01 through ENC-05. No implementation/training work happens here — that's a future, currently-deferred milestone, contingent on this mapping.

</domain>

<decisions>
## Implementation Decisions

### Encoding scheme selection
- Fully open — no starting intuition on dual-rail vs. single-rail/multi-mode vs. any other scheme. Research should survey standard linear-optical qubit-encoding schemes (dual-rail, single-rail, GKP-style, etc.) and present options with tradeoffs.
- Constrained to schemes MerLin/Perceval already has good native support for (Circuit/BS/PS/BasicState/Analyzer primitives) — not open to schemes requiring custom simulation infrastructure. Keeps the mapping defensible and avoids a future implementation-phase rabbit hole.
- Owner picks the scheme themselves after research presents options — Claude does not propose a recommendation that could bias the choice.
- Worked concrete example scale: both — state the mapping for general n, then instantiate it concretely for a small n=2-3 worked example (matching `iqp-baseline.md`'s own small-scale framing), so it's checkable, not just abstract notation.

### Reference sources for research
- Build directly on Phase 8's outputs: `docs/iqp-lit-scoping.md`, `docs/iqp-baseline.md`, `perceval_fluency_demo.py` (MZI/PS pattern reusable for phase-driven interference reasoning).
- Also pull in standard textbook-level linear-optical qubit-encoding references (e.g. Kok et al.-style review) as background for whichever scheme gets chosen.
- Owner-provided course material: `C:\Users\cuqui\quantum-information-material\quantum-physics-for-computer-scientists` (verified present — lecture PDFs + slides covering Fock states, the Jaynes-Cummings model, harmonic-oscillator quantization, time evolution/pictures). Research should check this for material relevant to Fock-state/photon-number formalism grounding before falling back to external sources.

### Mapping document depth & format (`docs/iqp-photonic-encoding.md`)
- **Rigor:** full proof-sketch derivation for ENC-01 — equation-level reasoning for why the mapping preserves IQP's structural properties (commutativity of the gate layer, conjugation symmetry), not just a summary/structural table. Closer in rigor to how Douce et al. (2017) is written than to `iqp-baseline.md`'s scannable-reference style.
- **Code:** interleave runnable Perceval code snippets alongside the math (in the style of `perceval_fluency_demo.py`) — small blocks that demonstrate pieces of the mapping concretely and are actually checkable, not just described.
- **Length:** longer treatment than Phase 8's 1-2 page docs — expected to run longer given this is the milestone's core deliverable and needs enough rigor to be defensible unaided (ENC-05's bar).
- **ENC-02 (positioning against Douce et al.):** depth left to Claude's discretion, but under an explicit hard constraint — see Tone & Framing below.

### Tone & framing (applies across the whole document, especially ENC-02)
- The owner is a master's student (not yet graduated) using an LLM as a collaborator — the document must not stake out claims or defend positions that risk making the owner look like they don't know what they're doing.
- This means: appropriately hedge claims of novelty/contribution, explicitly own open questions and limitations rather than asserting a fully resolved result, and avoid overclaiming rigor the mapping doesn't actually have. When comparing to Douce et al., be precise about what is and isn't established rather than reaching for a stronger claim than the mapping supports.

### Validation plan concreteness (ENC-04)
- Actually run a small toy-scale check during Phase 9 (n=2-3), not just describe one — compare the Fock-outcome distribution from a hand-built Perceval circuit against the exact qubit-side IQP distribution. Given the code-snippets decision above, this is a natural extension of the worked example.
- Comparison method: open to whatever is most natural for the chosen encoding scheme — not forced to reuse `iqp-baseline.md`'s Van den Nest cosine-formula trick, though it remains available if it fits.
- If the toy check reveals a mismatch or the mapping needs a caveat/exception: report it honestly and revise the mapping (ENC-01/ENC-03) as needed — matches this repo's established pattern (v1.0's GEN-07, Phase 7's neighbor-locality result) of documenting negative/partial results rather than smoothing them over.

### Attempt-first cadence for the design work
- Piece-by-piece pacing: owner attempts/sketches ENC-01 (ingredient mapping) first, checkpoint, then ENC-03 (basis correspondence), checkpoint, then ENC-04 (validation plan + toy check), checkpoint. Matches CLAUDE.md's attempt-first gating applied at finer grain given this is the hardest conceptual phase in the project.
- Self-explanation checkpoints happen at each of these intermediate points, not just once at phase end — in addition to (not instead of) the end-of-phase checkpoint already implied by CLAUDE.md's milestone-checkpoint pattern.
- No specific past failure mode flagged to watch for — standard attempt-first process applies.

### Claude's Discretion
- Exact ENC-02 comparison depth (short paragraph vs. structural table), constrained by the Tone & Framing rule above — err toward precise and hedged over comprehensive and confident.
- Exact section breakdown and ordering of `docs/iqp-photonic-encoding.md`.
- Exact phrasing/scope of the research survey of candidate encoding schemes.

</decisions>

<specifics>
## Specific Ideas

- The mapping should read with the same proof-sketch rigor as Douce et al. (2017), not the scannable-reference style of `iqp-baseline.md` — those are two different registers this project has already demonstrated, and Phase 9 should aim for the former.
- Owner-provided course material at `C:\Users\cuqui\quantum-information-material\quantum-physics-for-computer-scientists\lectures` includes notes on Fock states, the Jaynes-Cummings model, harmonic-oscillator quantization, and time-evolution pictures — directly relevant background for the Fock-space formalism this mapping is built in.

</specifics>

<deferred>
## Deferred Ideas

- Actual implementation/training of a generator using this encoding — that's a future, currently out-of-scope milestone (already noted as deferred in the v2.0 roadmap: IMPL-01/02, STUDY-01/02, WRITE-01).
- Any specific worry/failure-mode watchlist for attempt-first pacing — owner had none to flag; if one surfaces during Phase 9 execution, capture it then.

</deferred>

---

*Phase: 09-encoding-design*
*Context gathered: 2026-08-05*
