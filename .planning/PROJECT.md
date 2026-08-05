# MerLin Photonic Generative Modeling

## What This Is

A photonic quantum machine learning project built on MerLin (Quandela's PyTorch-based photonic QML framework): an MMD-trained generative model on MerLin's `QuantumLayer`, learning the sklearn `circles` dataset's two-ring shape via a closed-form MMD² loss over spatial bin-centers, with a custom radius/center-of-mass output-correspondence fix (K=462, no `ModGrouping` fold) as the project's key technical contribution. Reuses MMD-loss and generative-eval methodology from a prior IQP (gate-model) generative modeling project, applied here to a photonic circuit instead. Built as a credential and portfolio piece ahead of conversations with Vincent Espitalier and a Spring 2027 Quandela placement search.

## Core Value

A working, end-to-end, honestly-benchmarked MMD-trained photonic generative model, published in a public repo before September 1, 2026 — one the owner can explain unaided to Vincent Espitalier or in an interview. Explainability and a real end-to-end run matter more than polish or an ambitious result.

**Shipped as v1.0 on 2026-07-29**, 10 days after project start, well ahead of the Sept 1 deadline. Core value held throughout: every honest result (including GEN-07 not fully met) was reported plainly, not glossed over, and a full self-audit before shipping caught and fixed real claim-strength issues rather than letting them ship silently.

## Current State

**v2.0 IQP → Photonic Encoding shipped 2026-08-05**, 6 days after starting (2026-07-30 → 2026-08-05). Both phases (8: Literature Scoping & Prerequisites; 9: Encoding Design) complete, 11/11 requirements satisfied, full test suite green (85/85), Phase 9 independently re-verified via a live UAT pass after the milestone audit flagged its missing formal verification as tech debt. Full detail: [`.planning/milestones/v2.0-ROADMAP.md`](milestones/v2.0-ROADMAP.md), [`.planning/milestones/v2.0-REQUIREMENTS.md`](milestones/v2.0-REQUIREMENTS.md), [`.planning/milestones/v2.0-MILESTONE-AUDIT.md`](milestones/v2.0-MILESTONE-AUDIT.md).

## Current Milestone: v2.1 Weight-2 Implementation

**Goal:** Implement and validate the weight-2 IQP generator (`heralded_cz`-based two-qubit diagonal phase gate, fixed at θ=π/4) that v2.0 designed on paper but never built or ran. Extend the classical-comparison validation pattern from weight-1 (TVD-based) to cover weight-2. Empirically measure `heralded_cz`'s actual success probability against Perceval's specific implementation, rather than relying on secondhand literature figures for the general gate family.

**Target features:**
- Implementation of the `PBS`→`heralded_cz`→`PBS` weight-2 construction in Perceval, building on `iqp_photonic_encoding.py`'s existing weight-1 module
- Empirical measurement of `heralded_cz`'s herald-success frequency for this specific implementation
- Classical sanity check: extend the exact-vs-exact TVD comparison pattern (weight-1's ENC-04) to a small-scale weight-2 IQP circuit
- **Explicitly out of scope this milestone:** trainability/barren-plateau study (STUDY-01), hardness-under-loss assessment (STUDY-02), write-up (WRITE-01), and resolving the fixed-angle (π/4-only) limitation for arbitrary-θ weight-2 gates — all deferred to a future milestone once weight-2 is working

**Source:** `docs/iqp-photonic-encoding.md`'s Ingredient 2 (weight-2 derivation) and Conclusion/Open Questions section; `.planning/milestones/v2.0-REQUIREMENTS.md`'s deferred v2 requirements (IMPL-01, IMPL-02)

## Next Milestone Goals (beyond v2.1)

- STUDY-01/STUDY-02/WRITE-01 (trainability/hardness study and write-up), contingent on v2.1's weight-2 implementation actually working
- Arbitrary-θ weight-2 gates (resolving the fixed-π/4 limitation), if the study reveals it's load-bearing
- BMK-03 (exact apples-to-apples QGAN comparison, deferred since v1.0)
- Sending the drafted v1.0 technical note to Vincent Espitalier and flipping the repo public (both still open, independent of any future milestone)

<details>
<summary>Archived: v2.0 IQP → Photonic Encoding milestone scope (shipped 2026-08-05)</summary>

**Goal:** Determine whether IQP's structural properties (trainability, sampling hardness) survive translation into a photonic/linear-optical ansatz — this milestone covers literature scoping and, if viable, a defensible on-paper encoding design. Implementation, the trainability/hardness study, and write-up are deliberately deferred to a follow-on milestone, per the source plan doc's own caveat that it "will get re-planned once Phase 0 lands."

**Target features:**
- Literature scoping: search for existing IQP↔linear-optics or IQP↔continuous-variable constructions; time-boxed go/no-go verdict
- Prerequisite confirmation: Perceval low-level circuit API fluency (beyond `QuantumLayer.simple()`); prior IQP/barren-plateau notes compiled as qubit-side baseline
- On-paper encoding design (contingent on a "go" verdict): map IQP's commuting diagonal gates + Hadamard-basis conjugation onto phase shifters, beamsplitters, and photon-number measurement — written down and defensible before any implementation

**Source doc:** [Post_Sept1_IQP_Photonic_Plan.md](../Post_Sept1_IQP_Photonic_Plan.md) — full 5-phase research plan (this milestone covered Phase 0-1 only)

</details>

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
- ✓ Literature search conducted for existing IQP↔linear-optics or IQP↔CV constructions, time-boxed, go/no-go verdict documented either way — v2.0, 2026-08-04, verdict: **Go** (no DV/Fock construction or impossibility result found; `docs/iqp-lit-scoping.md`)
- ✓ Perceval low-level circuit API fluency confirmed (manual construction with phase shifters/beamsplitters, not just the high-level wrapper) — v2.0, 2026-08-04, `perceval_fluency_demo.py`
- ✓ Prior IQP + barren-plateau notes/results compiled into one reference doc as the qubit-side baseline — v2.0, 2026-08-04, `docs/iqp-baseline.md`
- ✓ On-paper IQP→photonic encoding mapping designed and documented, defensible unaided — v2.0, 2026-08-05, `docs/iqp-photonic-encoding.md`; polarization encoding, weight-1 generators exact/implemented/validated (TVD ~1e-16 at n=2,3), weight-2 derived on paper only and explicitly untested; owner's unaided explanation independently re-verified via UAT 2026-08-05

### Active

- [ ] Weight-2 (`heralded_cz`-based) IQP generator implemented in Perceval
- [ ] `heralded_cz`'s herald-success probability empirically measured for this specific implementation
- [ ] Classical sanity-check validation (TVD-style, per weight-1's ENC-04 pattern) extended to a small-scale weight-2 circuit

### Out of Scope

- **Reproducing the IQP gate-model circuits directly in MerLin (implementation)** — v2.0 completed the *design* side of this (an original, defensible DV/Fock-space encoding mapping, `docs/iqp-photonic-encoding.md`, weight-1 implemented and validated). Actually implementing/testing the full circuit including weight-2, and the trainability/hardness study, remain out of scope until a future milestone (deferred as IMPL-01/02, STUDY-01/02, WRITE-01 — see "Next Milestone Goals").
- **PennyLane independent contributions** — parked, sequenced after the IQP-photonic project.
- **ket.jl / SDP self-study** — informal free-time research only, no artifact expected.
- **Weighted-average → single continuous point output mapping** — rejected: collapses multimodal targets (circles' two rings) into their midpoint, a region with zero real density.
- **Discrete `shots`-based sampling for the generator** — rejected: not differentiable through standard autograd without an additional estimator.
- **Exact replication of MerLin's photonic QGAN paper's full MNIST-patch dataset/architecture (BMK-03)** — not pursued in v1.0 or v2.0; shipped without it. Candidate for a future milestone if the apples-to-apples comparison becomes worth the added scope.
- **v1.0's fold-removal-vs-correspondence-redesign ablation** — the neighbor-locality test and post-fix sigma re-sweep (the other two follow-ups identified by the v1.0 self-audit) were run in Phase 7 (2026-07-30; results measured, owner interpretation still pending). This third ablation remains genuinely not attempted — would reopen a closed phase.

## Context

- **Shipped:** v1.0 complete 2026-07-29 (6 phases, 11 plans, 51 commits, 1,648 LOC Python, 10 days start-to-ship). v2.0 complete 2026-08-05 (2 phases, 8 plans, 33 commits, 1,282 lines added across code+tests, 6 days start-to-ship).
- **Deadline pressure (resolved):** Hard deadline was September 1, 2026, driven by a warm contact (Vincent Espitalier) and the Quandela Spring 2027 placement pipeline. v1.0 shipped ~5 weeks early; v2.0 shipped as a bonus milestone well within the remaining runway.
- **Historical stall pattern (did not recur):** A prior self-directed track (PennyLane) had been stalled since May 2026. The July 25, 2026 v1.0 stall-risk checkpoint (Phase 3, end-to-end training run) was met a day early — the pattern did not repeat in either milestone.
- **Prior relevant expertise:** PyTorch; MMD-loss and generative-modeling experience from an IQP-MMD project; general quantum ML fluency; IQP circuits and barren-plateau research; polarization-optics coursework (Sorbonne) — directly informed v2.0's encoding choice.
- **MerLin specifics (verified empirically, not just from docs):** `ML.QuantumLayer.simple(input_size, output_size)` returns a probability distribution over `output_size` measurement outcomes — non-negative, rows sum to exactly 1. MerLin also ships its own `PhotonicGenerator`/`NormalLatent`/`OutputAdapter` classes (`merlin.models.photonic_generator`) — v1.0 used `NormalLatent` directly but hand-rolled the training loop and output-correspondence logic, since the built-in `VectorAdapter` doesn't solve the correspondence problem the radius/center-of-mass fix addresses (confirmed via the v1.0 self-audit).
- **Perceval specifics (v2.0, verified empirically):** ships a full polarization gate catalog (`HWP`, `QWP`, `PR`, `WP`, `PBS`) — an earlier research pass had incorrectly claimed otherwise, corrected by direct source inspection. `WP(θ,0) = diag(e^{iθ},e^{-iθ})` exactly; `HWP(π/8)` realizes Hadamard up to an unobservable global phase. A bare phase/polarization state is invisible to Fock-basis measurement without an interference partner (a second `BS` for `PS`, a `PBS` for polarization) — confirmed empirically in both Phase 8 and Phase 9.
- **Reproduced-papers catalog (21 papers)** checked directly — none reproduce IQP circuits. Closest neighbors: photonic QGAN (#16, adversarial loss, Sedrakyan & Salavrakos 2024) and QSSL (#14, contrastive loss, Jaderberg et al. 2021).
- **Douce et al. (PRL 118, 070503, 2017)** proved CV-IQP sampling hardness in a continuous-quadrature formalism (squeezed light + homodyne) — a genuinely different formalism from v2.0's Fock-space/photon-number approach; positioned honestly in ENC-02 (favorable contrast on single-qubit conjugation, honest parallel on the multi-qubit measurement-conditioned case).
- **Post-shipment self-audit (v1.0):** A directed Codex (gpt-5.5) deep audit against MerLin's local package source and the sibling IQP-MMD project's Obsidian vault found and the project fixed: a backwards tau/sigma direction claim, a misattributed statistic, stale batch-sweep numbers, a factually wrong claim about the sibling project's exact-MMD path, a silent-mismatch footgun in `NaturallyOrderedGenerator`, and an unsupported "reproducible" claim. Full record: `.planning/milestones/v1.0-MILESTONE-AUDIT.md`.
- **Milestone audit + UAT gap-closure (v2.0):** `/gsd:audit-milestone` found Phase 9 shipped without a standalone `gsd-verifier` report (tech debt, not a functional gap — 11/11 requirements satisfied, integration checks clean). Closed via an independent `/gsd:verify-work 9` UAT pass: 6 of 8 tests verified by directly re-running code against the doc's claimed numbers (all matched exactly), and the self-explanation checkpoint (test 8) was independently re-tested rather than cited from the prior pass, surfacing a real (if minor) gap on the basis-correspondence sub-question that needed two follow-up rounds to resolve correctly. Full record: `.planning/milestones/v2.0-MILESTONE-AUDIT.md`, `.planning/phases/09-encoding-design/09-UAT.md`.
- **Known open items (owner's manual steps):** flip the GitHub repo to public (`gh repo edit alejack312/merlin-photonic-generative-modeling --visibility public`); send the drafted technical note to Vincent Espitalier.

## Constraints

- **Timeline**: Hard deadline Sept 1, 2026 — met with runway to spare on both milestones. Jul 25, 2026 stall-risk checkpoint (v1.0) — met one day early.
- **Tech stack**: Python 3.10–3.12 only (MerLin's `pyproject.toml` caps here). `torch<2.13`, `perceval-quandela>=1.2.1`.
- **Collaboration process** (see [CLAUDE.md](../CLAUDE.md)): core conceptual/design decisions require the owner's own attempt or explanation before full implementation is written; self-explanation checkpoints occur at each SMART-spec milestone; no silent unilateral design decisions. Held throughout both milestones — including a corrected self-explanation attempt at v1.0's Phase 3 checkpoint, and v2.0's Phase 9 attempt-first checkpoints (each of ENC-01/ENC-03/ENC-04 gated on an owner attempt before implementation, with real corrections along the way — e.g. the H/V port-labeling bug caught during ENC-03's checkpoint).
- **Scope discipline**: single project, sized to fit the window — held across both milestones. BMK-03, the full IQP→photonic implementation/study (v2 requirements), and PennyLane all stayed parked rather than scope-creeping into either shipped milestone.

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
| Started v2.0 (IQP→photonic) on 2026-07-30, overriding the plan doc's "not before Sept 2, 2026" gate | v1.0's dev work is fully complete (shipped 2026-07-29, Phase 7 closed 2026-07-30); only two owner-only manual steps remain (flip repo public, send note to Vincent) and ample runway remains before Sept 1 — owner explicitly chose to proceed rather than wait | ✓ Good — shipped 6 days later, no deadline pressure created |
| v2.0 roadmap scoped to Phase 0-1 only (literature scoping + encoding design), not all 5 plan-doc phases | The plan doc itself says it "will get re-planned once Phase 0 lands" — Phase 0 is an explicit go/no-go gate, so committing implementation/study/write-up phases now would plan against an unknown | ✓ Good — Phase 8's Go verdict unblocked Phase 9 as designed; v2 requirements (IMPL/STUDY/WRITE) correctly left unplanned pending a future milestone decision |
| Encoding target is discrete-variable (DV, Fock-space: phase shifters/beamsplitters/photon-counting), not continuous-variable (CV, squeezed states/homodyne) | Research found no published DV construction (genuinely novel, open-source-worthy) vs. CV where Douce et al. (2017) already proved the hardness result (reproduction, not invention); DV also preserves IQP's native discrete bitstring-sampling character, where CV's continuous homodyne outcomes would redefine the sampling problem itself | ✓ Good — DV mapping designed, implemented (weight-1), and validated (TVD ~1e-16); ENC-02 honestly positions it against Douce et al. rather than overclaiming novelty |
| Polarization encoding (H/V) chosen over dual rail or QUDIT | Owner's own choice, from personal Sorbonne coursework — corrected an inaccuracy in `09-RESEARCH.md`'s survey (Perceval does ship a polarization gate catalog: `HWP`/`QWP`/`PR`/`WP`/`PBS`) | ✓ Good — weight-1 generators map exactly (`WP(θ,0) = exp(iθZ)`), validated to floating-point precision |
| Runnable code/tests scoped to weight-1 IQP generators only; weight-2 derived on paper via `heralded_cz` at a fixed angle (π/4) | `heralded_cz` is a fixed catalog gate, not a continuously-tunable one — resolving an arbitrary-θ two-qubit diagonal phase gate from Perceval's catalog alone is a real, unresolved gap, not glossed over | ⚠️ Revisit — a real, stated limitation; weight-2 implementation/testing is the natural first task of any follow-on milestone |
| Validation metric: total variation distance (exact-vs-exact), not MMD | MMD's kernel-bandwidth machinery exists to handle sampling noise, which doesn't apply when both sides of the comparison are exact calculations | ✓ Good — TVD ~1e-16 at n=2,3, ten orders of magnitude under the chosen 1e-6 threshold |
| Phase 9 shipped without a standalone `gsd-verifier` VERIFICATION.md (unlike Phase 8) | Not a deliberate choice — a process gap flagged by the milestone audit as tech debt | ⚠️ Revisit — closed post-audit via an independent `/gsd:verify-work 9` UAT pass (8/8, live-verified), but worth avoiding in future milestones: run `gsd-verifier` per-phase during execution, not just at milestone audit time |

---
*Last updated: 2026-08-05 after v2.0 milestone completion*
