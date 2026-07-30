# MerLin Photonic Generative Modeling

## What This Is

A photonic quantum machine learning project built on MerLin (Quandela's PyTorch-based photonic QML framework): an MMD-trained generative model on MerLin's `QuantumLayer`, learning the sklearn `circles` dataset's two-ring shape via a closed-form MMD² loss over spatial bin-centers, with a custom radius/center-of-mass output-correspondence fix (K=462, no `ModGrouping` fold) as the project's key technical contribution. Reuses MMD-loss and generative-eval methodology from a prior IQP (gate-model) generative modeling project, applied here to a photonic circuit instead. Built as a credential and portfolio piece ahead of conversations with Vincent Espitalier and a Spring 2027 Quandela placement search.

## Core Value

A working, end-to-end, honestly-benchmarked MMD-trained photonic generative model, published in a public repo before September 1, 2026 — one the owner can explain unaided to Vincent Espitalier or in an interview. Explainability and a real end-to-end run matter more than polish or an ambitious result.

**Shipped as v1.0 on 2026-07-29**, 10 days after project start, well ahead of the Sept 1 deadline. Core value held throughout: every honest result (including GEN-07 not fully met) was reported plainly, not glossed over, and a full self-audit before shipping caught and fixed real claim-strength issues rather than letting them ship silently.

## Current Milestone: v2.0 IQP → Photonic Encoding

**Goal:** Determine whether IQP's structural properties (trainability, sampling hardness) survive translation into a photonic/linear-optical ansatz — this milestone covers literature scoping and, if viable, a defensible on-paper encoding design. Implementation, the trainability/hardness study, and write-up are deliberately deferred to a follow-on milestone, per the source plan doc's own caveat that it "will get re-planned once Phase 0 lands."

**Target features:**
- Literature scoping: search for existing IQP↔linear-optics or IQP↔continuous-variable constructions; time-boxed go/no-go verdict
- Prerequisite confirmation: Perceval low-level circuit API fluency (beyond `QuantumLayer.simple()`); prior IQP/barren-plateau notes compiled as qubit-side baseline
- On-paper encoding design (contingent on a "go" verdict): map IQP's commuting diagonal gates + Hadamard-basis conjugation onto phase shifters, beamsplitters, and photon-number measurement — written down and defensible before any implementation

**Source doc:** [Post_Sept1_IQP_Photonic_Plan.md](../Post_Sept1_IQP_Photonic_Plan.md) — full 5-phase research plan (this milestone covers Phase 0-1 only)

## Requirements

### Validated

- ✓ MerLin installed in a version-compatible environment (Python 3.12 venv; MerLin caps Python at 3.10–3.12, torch <2.13) — 2026-07-19
- ✓ Quickstart classifier (circles dataset) runs end-to-end; confirmed gradients flow through the quantum layer via PyTorch's autograd — 2026-07-19
- ✓ Generator output-representation architecture decided: full-distribution/histogram matching via closed-form MMD², not single-point averaging or discrete sampling — 2026-07-19
- ✓ Latent noise sampling + encoding as `QuantumLayer` input — 2026-07-19 (`generator/noise.py`)
- ✓ Fixed set of K bin-centers spanning the circles data's (x, y) region — 2026-07-19 (`generator/bin_centers.py`, K=400; later K=462 for the natural-order variant)
- ✓ Real-data histogram (`p_real`) precomputed once over the K bin-centers — 2026-07-19 (`generator/data.py`)
- ✓ Closed-form MMD² loss between the model's probability-vector output and `p_real` — 2026-07-19 (`generator/mmd.py`)
- ✓ Training loop runs end-to-end with a real, scripted-verified MMD-decreasing run — 2026-07-24, one day ahead of the July 25 stall-risk checkpoint
- ✓ Held-out benchmark metric reported and qualitative QGAN comparison documented — 2026-07-29 (`results/phase5_summary.md`)
- ✓ README, public-repo prep, technical note, and portfolio case study — 2026-07-29 (v1.0)
- **~ Generator's samples visibly approximate the two-ring circles shape — NOT MET, 2026-07-25.** Best result (natural-order correspondence, ring_mass=0.609→0.691) is a real, mechanistically-motivated improvement, not two recognizable rings. Owner-confirmed verdict, honestly documented rather than reframed as success. See `.planning/milestones/v1.0-ROADMAP.md` Phase 4 detail.

### Active

- [ ] Literature search conducted for existing IQP↔linear-optics or IQP↔CV constructions, time-boxed, go/no-go verdict documented either way
- [ ] Perceval low-level circuit API fluency confirmed (manual construction with phase shifters/beamsplitters, not just the high-level wrapper)
- [ ] Prior IQP + barren-plateau notes/results compiled into one reference doc as the qubit-side baseline
- [ ] On-paper IQP→photonic encoding mapping designed and documented, defensible unaided, contingent on a "go" verdict from the literature search

### Out of Scope

- **Reproducing the IQP gate-model circuits directly in MerLin** — no established IQP→linear-optics reduction exists; doing this honestly would be original theoretical research, not an extension. Parked as its own post-Sept-1 project — see [Post_Sept1_IQP_Photonic_Plan.md](../Post_Sept1_IQP_Photonic_Plan.md).
- **PennyLane independent contributions** — parked, sequenced after the IQP-photonic project.
- **ket.jl / SDP self-study** — informal free-time research only, no artifact expected.
- **Weighted-average → single continuous point output mapping** — rejected: collapses multimodal targets (circles' two rings) into their midpoint, a region with zero real density.
- **Discrete `shots`-based sampling for the generator** — rejected: not differentiable through standard autograd without an additional estimator.
- **Exact replication of MerLin's photonic QGAN paper's full MNIST-patch dataset/architecture (BMK-03)** — not pursued this milestone; shipped without it. Candidate for a future milestone if the apples-to-apples comparison becomes worth the added scope.
- **Ablation isolating fold-removal from correspondence-redesign, a direct neighbor-locality test on the circuit's raw outputs, and a post-fix sigma re-sweep** — all identified during the v1.0 self-audit as the concrete follow-ups that would either confirm or overturn the natural-order-correspondence mechanism story; documented as backlog (case study's "What I'd Do Next"), not attempted — would reopen a closed phase.

## Context

- **Shipped:** v1.0 complete 2026-07-29. 6 phases, 11 plans, 51 commits, 1,648 LOC Python, 10 days start-to-ship.
- **Deadline pressure (resolved):** Hard deadline was September 1, 2026, driven by a warm contact (Vincent Espitalier) and the Quandela Spring 2027 placement pipeline. Shipped ~5 weeks early.
- **Historical stall pattern (did not recur):** A prior self-directed track (PennyLane) had been stalled since May 2026. The July 25, 2026 stall-risk checkpoint (Phase 3, end-to-end training run) was met a day early — the pattern did not repeat here.
- **Prior relevant expertise:** PyTorch; MMD-loss and generative-modeling experience from an IQP-MMD project; general quantum ML fluency; IQP circuits and barren-plateau research.
- **MerLin specifics (verified empirically, not just from docs):** `ML.QuantumLayer.simple(input_size, output_size)` returns a probability distribution over `output_size` measurement outcomes — non-negative, rows sum to exactly 1. MerLin also ships its own `PhotonicGenerator`/`NormalLatent`/`OutputAdapter` classes (`merlin.models.photonic_generator`) — this project used `NormalLatent` directly but hand-rolled the training loop and output-correspondence logic, since the built-in `VectorAdapter` doesn't solve the correspondence problem this project's radius/center-of-mass fix addresses (confirmed via the v1.0 self-audit).
- **Reproduced-papers catalog (21 papers)** checked directly — none reproduce IQP circuits. Closest neighbors: photonic QGAN (#16, adversarial loss, Sedrakyan & Salavrakos 2024) and QSSL (#14, contrastive loss, Jaderberg et al. 2021).
- **Post-shipment self-audit:** A directed Codex (gpt-5.5) deep audit against MerLin's local package source and the sibling IQP-MMD project's Obsidian vault found and the project fixed: a backwards tau/sigma direction claim, a misattributed statistic, stale batch-sweep numbers, a factually wrong claim about the sibling project's exact-MMD path, a silent-mismatch footgun in `NaturallyOrderedGenerator`, and an unsupported "reproducible" claim. Full record: `.planning/milestones/v1.0-MILESTONE-AUDIT.md`.
- **Known open items (owner's manual steps):** flip the GitHub repo to public (`gh repo edit alejack312/merlin-photonic-generative-modeling --visibility public`); send the drafted technical note to Vincent Espitalier.

## Constraints

- **Timeline**: Hard deadline Sept 1, 2026 — met with runway to spare. Jul 25, 2026 stall-risk checkpoint — met one day early.
- **Tech stack**: Python 3.10–3.12 only (MerLin's `pyproject.toml` caps here). `torch<2.13`, `perceval-quandela>=1.2.1`.
- **Collaboration process** (see [CLAUDE.md](../CLAUDE.md)): core conceptual/design decisions require the owner's own attempt or explanation before full implementation is written; self-explanation checkpoints occur at each SMART-spec milestone; no silent unilateral design decisions. Held throughout — including a corrected self-explanation attempt at the Phase 3 checkpoint (owner's first attempt conflated this project's continuous-distribution MMD with the prior project's bitstring MMD, caught and corrected before proceeding).
- **Scope discipline**: single project, sized to fit the window — held. BMK-03 and the IQP→photonic mapping project both stayed parked rather than scope-creeping into v1.0.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Extend quickstart classifier into an MMD generator (SMART spec option b), rather than reproduce a catalog paper directly | Best reuses the owner's actual specialized background (MMD/generative modeling); gives a natural comparison point against MerLin's own photonic QGAN reproduction | ✓ Good — shipped, gave a genuine second demonstration of the "low loss ≠ learned structure" lesson from the prior IQP-MMD project |
| Generator output = full-distribution/histogram matching via closed-form MMD² (not single-point averaging, not discrete sampling) | Avoids collapsing circles' two-ring (multimodal) target into its empty middle; avoids the non-differentiability of discrete sampling | ✓ Good — verified working end-to-end, no regressions found in the self-audit |
| IQP→photonic circuit mapping parked to a dedicated post-Sept-1 project | No established IQP→linear-optics reduction exists — doing it honestly is original research, too heavy/risky for this deadline | ✓ Good — stayed parked, did not scope-creep into v1.0 |
| Python 3.12 venv instead of system default Python 3.13 | MerLin's `torch<2.13` + `python>=3.10,<=3.12` constraints would break dependency resolution on 3.13 | ✓ Good — verified working |
| Batch-averaged per-sample MMD² training step, not batch=1 | MMD-based generative training is noise-sensitive at small batch sizes; a noisy batch=1 curve threatened the July 25 checkpoint being defensibly true | ✓ Good in practice, ⚠️ revisit framing — empirically validated (clean decreasing trend, p≈1e-128), but the self-audit found this objective is provably an upper bound on the marginal-distribution MMD² (Jensen's inequality on the convex kernel term), not identical to it — documented as a caveat in DESIGN_DECISIONS.md, not reversed |
| Natural-order correspondence fix (K=462, radius-sorted bins, no `ModGrouping` fold) over increasing `input_size` (diagnosed counterproductive) or a point-averaging fallback (rejected in Phase 1) | The circuit's raw output index has no designed relationship to the (x,y) grid by default; radius-sorting turns 44 disjoint target fragments into ~6 contiguous bands | ⚠️ Revisit — real, measured improvement (ring_mass 0.609→0.691), but the self-audit found the causal mechanism (why reordering helps) is asserted, not demonstrated; concrete follow-up tests documented as backlog, not yet run |
| GEN-07 concluded "not met" rather than reframed or re-scoped | Owner's explicit instruction: "GEN-07 not met, move to Phase 5" — per PROJECT.md's founding "don't gloss over it" rule | ✓ Good — held the line through Phase 5/6 and the case study, no softening under publication pressure |
| Portfolio case study built as a full interactive TSX page in a separate repo (alejandro-jackson), not a markdown file here | Matched the actual reference format (`iqp-mmd.tsx`) the owner intended, not the initially-assumed markdown convention | ✓ Good — shipped, owner-approved live, cross-linked from all other case studies |
| Self-directed post-ship audit (Codex/gpt-5.5) against MerLin's source and the sibling project's vault | Owner requested an independent check before calling the project truly done | ✓ Good — found real issues (not manufactured ones); every finding was either fixed or honestly caveated before archiving |
| Started v2.0 (IQP→photonic) on 2026-07-30, overriding the plan doc's "not before Sept 2, 2026" gate | v1.0's dev work is fully complete (shipped 2026-07-29, Phase 7 closed 2026-07-30); only two owner-only manual steps remain (flip repo public, send note to Vincent) and ample runway remains before Sept 1 — owner explicitly chose to proceed rather than wait | — Pending |
| v2.0 roadmap scoped to Phase 0-1 only (literature scoping + encoding design), not all 5 plan-doc phases | The plan doc itself says it "will get re-planned once Phase 0 lands" — Phase 0 is an explicit go/no-go gate, so committing implementation/study/write-up phases now would plan against an unknown | — Pending |

---
*Last updated: 2026-07-29 after v1.0 milestone completion*
