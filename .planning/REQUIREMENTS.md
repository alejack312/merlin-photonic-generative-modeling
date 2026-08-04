# Requirements: MerLin Photonic Generative Modeling — v2.0 IQP → Photonic Encoding

**Defined:** 2026-07-30
**Core Value (this milestone):** Determine whether IQP's structural properties survive translation into a discrete-variable (DV, Fock-space) photonic ansatz — literature scoping and, if viable, a defensible on-paper encoding design. No implementation this milestone.

## v1 Requirements

Requirements for this milestone (v2.0). Each maps to roadmap phases (continuing numbering from v1.0's Phase 7).

### Literature Scoping

*A quick verification pass during requirements-gathering (2026-07-30) already corroborates the "no DV construction exists, only Douce et al.'s CV extension" finding via three independent checks — see PROJECT.md Context. This does not replace the formal Phase 0 work below (full-text Douce et al. read, systematic time-boxed search), which should still run to the rigor the plan doc and PITFALLS.md's anti-premature-closure guidance calls for.*

- [x] **LIT-01**: Literature search conducted (beyond the CV precedent already found) for any existing discrete-variable/Fock-space linear-optical construction of IQP — complete 2026-08-04, two independent passes (`08-RESEARCH.md` WebSearch + `docs/iqp-lit-scoping.md` arXiv-API/Semantic-Scholar citation-graph), no construction and no impossibility result found either way
- [x] **LIT-02**: Douce et al. (PRL 118, 070503, 2017, arXiv:1607.07605) reviewed in full text (not abstract-level only) so the DV design can be correctly positioned against the existing CV precedent — complete 2026-08-04, `docs/iqp-lit-scoping.md`
- [x] **LIT-03**: MerLin's own reproduced-papers catalog checked for IQP-adjacency — verified 2026-07-30, all 21 titles enumerated directly from `merlinquantum.ai/0.4/reproduced_papers/`, none relate to IQP
- [x] **LIT-04**: Go/no-go verdict on Phase 1 (encoding design) written down explicitly, time-boxed — "not ready" is a valid, reportable outcome if nothing viable is found — complete 2026-08-04, verdict: **Go**, `docs/iqp-lit-scoping.md`

### Prerequisites

- [x] **PREQ-01**: Perceval low-level circuit API fluency confirmed via a working manual circuit build (`Circuit`, `PS`, `BS`, `BasicState`, `Analyzer`) — demonstrated, not just read about — complete 2026-08-04, `perceval_fluency_demo.py` (single-photon split, Hong-Ou-Mandel dip, and PS-driven Mach-Zehnder interference, all closed-form verified)
- [x] **PREQ-02**: Prior IQP + barren-plateau notes/results compiled into one reference doc as the qubit-side baseline for later comparison — complete 2026-08-04, `docs/iqp-baseline.md`

### Encoding Design

*Contingent on LIT-04 = "go."*

- [ ] **ENC-01**: On-paper mapping defined: IQP's commuting diagonal gates + Hadamard-basis conjugation → phase shifters, beamsplitters, photon-number measurement, written in raw Perceval vocabulary (not MerLin's high-level builder DSL)
- [ ] **ENC-02**: Mapping explicitly positioned against the Douce et al. CV precedent — how the DV approach differs and why it's a distinct contribution, not a restatement
- [ ] **ENC-03**: Basis correspondence stated concretely between qubit computational-basis bitstrings and photonic Fock-state/photon-count outcomes — a falsifiable mapping, not hand-wavy analogy
- [ ] **ENC-04**: A stated falsifiable check for the mapping (e.g., a small-scale classical comparison plan) — even though it isn't run until a future implementation phase, the design must be checkable in principle
- [ ] **ENC-05**: Mapping documented in `docs/iqp-photonic-encoding.md`, defensible unaided by the owner — same bar as the v1.0 self-explanation checkpoints

## v2 Requirements

Deferred to a future milestone, contingent on this milestone's findings (per the source plan doc, Phases 2-4).

### Implementation & Study

- **IMPL-01**: Minimal Perceval implementation of the mapped circuit
- **IMPL-02**: Classical sanity check against small-scale qubit-IQP simulation
- **STUDY-01**: Trainability study — gradient variance vs. system size (barren-plateau check) against the qubit-IQP baseline
- **STUDY-02**: Hardness assessment — whether realistic photonic noise/loss breaks the mapped circuit's hardness claim
- **WRITE-01**: Write-up in a format decided by what the study finds (case study, note to Vincent, or workshop/preprint)

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Continuous-variable (CV) encoding, following Douce et al. | Owner explicitly chose DV: no published DV construction exists (genuinely novel), and DV preserves IQP's native discrete bitstring-sampling character where CV's continuous homodyne outcomes would redefine the sampling problem |
| Any implementation code this milestone | Deferred pending this milestone's design output — the source plan doc says the full plan "will get re-planned once Phase 0 lands" |
| A formal complexity-theoretic reduction proof | This milestone produces a defensible design + a stated falsifiable check plan, not a peer-review-grade proof; a formal proof (if pursued) belongs to a later phase |
| Strawberry Fields or other CV toolkits | Not needed — DV route uses Perceval/MerLin's existing native primitives, no new dependencies |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| LIT-01 | Phase 8: Literature Scoping & Prerequisites | Complete (2026-08-04) |
| LIT-02 | Phase 8: Literature Scoping & Prerequisites | Complete (2026-08-04) |
| LIT-03 | Phase 8: Literature Scoping & Prerequisites | Complete (2026-07-30) |
| LIT-04 | Phase 8: Literature Scoping & Prerequisites | Complete (2026-08-04) — Go |
| PREQ-01 | Phase 8: Literature Scoping & Prerequisites | Complete (2026-08-04) |
| PREQ-02 | Phase 8: Literature Scoping & Prerequisites | Complete (2026-08-04) |
| ENC-01 | Phase 9: Encoding Design | Pending |
| ENC-02 | Phase 9: Encoding Design | Pending |
| ENC-03 | Phase 9: Encoding Design | Pending |
| ENC-04 | Phase 9: Encoding Design | Pending |
| ENC-05 | Phase 9: Encoding Design | Pending |

**Coverage:**
- v1 requirements: 11 total
- Mapped to phases: 11/11 ✓
- Unmapped: 0 ✓ no orphans

---
*Requirements defined: 2026-07-30*
*Last updated: 2026-07-30 after roadmap creation (Phases 8-9)*
