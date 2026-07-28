# Roadmap: MerLin Photonic Generative Modeling

## Overview

Extend MerLin's quickstart circles-dataset classifier into an MMD-trained photonic generative model, benchmark it honestly, and publish it as a credential/portfolio piece before September 1, 2026. The path runs from a verified environment and architecture decision (done), through building the generator's data/loss infrastructure, to a critical end-to-end training checkpoint on July 25, then quality tuning, benchmarking, and finally packaging the result for Vincent Espitalier, a public repo, and a portfolio case study.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Environment & Architecture Foundation** - MerLin environment verified working; generator's output-representation approach decided
- [x] **Phase 2: Generator Data & Loss Infrastructure** - Noise encoding, bin-centers, real histogram, and MMD² loss built and independently verified
- [x] **Phase 3: End-to-End Training Run** - Training loop runs and MMD measurably decreases (the July 25 stall-risk checkpoint)
- [~] **Phase 4: Generative Quality** - CONCLUDED, GEN-07 NOT MET (owner-confirmed 2026-07-25) — best result is a real, documented improvement, not two recognizable rings
- [x] **Phase 5: Benchmarking** - Model performance quantified and compared against MerLin's photonic QGAN reproduction
- [ ] **Phase 6: Documentation & Publication** - README, public repo, technical note, and portfolio case study ready to share

## Phase Details

### Phase 1: Environment & Architecture Foundation
**Goal**: A working, verified MerLin environment exists, and the generator's core architectural approach is decided before any generator code is written.
**Depends on**: Nothing (first phase)
**Requirements**: ENV-01, ENV-02, GEN-01
**Success Criteria** (what must be TRUE):
  1. MerLin's quickstart classifier runs end-to-end locally, with gradients confirmed flowing through the quantum layer via PyTorch autograd.
  2. The Python 3.12 venv resolves all required package versions (`torch<2.13`, `perceval-quandela>=1.2.1`) without conflict.
  3. The generator's output representation (full-distribution/histogram MMD matching, not single-point averaging or discrete sampling) is decided and recorded in DESIGN_DECISIONS.md.
**Status**: Complete (2026-07-19)

Plans:
- [x] Pre-roadmap work (environment setup, quickstart verification, architecture decision — completed before this roadmap existed)

### Phase 2: Generator Data & Loss Infrastructure
**Goal**: Every component the training loop will need — noise encoding, bin-centers, real-data histogram, and the MMD² loss function — exists and is independently verified correct, before being wired together.
**Depends on**: Phase 1
**Requirements**: GEN-02, GEN-03, GEN-04, GEN-05
**Success Criteria** (what must be TRUE):
  1. Latent noise vectors can be sampled and encoded as valid input to `QuantumLayer` on each call.
  2. A fixed set of K bin-centers spanning the circles dataset's (x, y) region is defined and reproducible across runs.
  3. The real-data histogram (`p_real`) over the K bin-centers is precomputed once and its probabilities sum to 1.
  4. The closed-form MMD² between two probability vectors over the bin-centers computes a finite, non-negative value, using a kernel over bin-center coordinates.
**Plans**: 4 plans
**Status**: Complete (2026-07-19)

Plans:
- [x] 02-01-PLAN.md — Setup (pytest + package scaffolding) + deterministic K=400 bin-centers (GEN-03)
- [x] 02-02-PLAN.md — Latent noise sampling/encoding (GEN-02)
- [x] 02-03-PLAN.md — Real-data histogram p_real (GEN-04)
- [x] 02-04-PLAN.md — Closed-form MMD² loss (GEN-05)

### Phase 3: End-to-End Training Run
**Goal**: The generator trains end-to-end on real data with a loop that measurably decreases MMD — the explicit July 25, 2026 stall-risk checkpoint named in PROJECT.md.
**Depends on**: Phase 2
**Requirements**: GEN-06
**Success Criteria** (what must be TRUE):
  1. The training loop runs to completion without errors, using the `QuantumLayer` generator, precomputed `p_real`, and the MMD² loss from Phase 2.
  2. The loss curve shows a real, observable decreasing trend across epochs (not flat, not diverging).
  3. This phase's success criteria are met on or before July 25, 2026 — if not, the historical PennyLane stall pattern is recurring and must be named plainly per PROJECT.md.
**Plans**: 1 plan
**Status**: Complete (2026-07-24)

Plans:
- [x] 03-01-PLAN.md — Wire Phase 2 modules into train.py, run 300-epoch training, verify decreasing MMD trend via scripted check

### Phase 4: Generative Quality
**Goal**: The trained generator's samples are recognizable to a human as approximating the circles dataset's two-ring shape — not just a loss number going down.
**Depends on**: Phase 3
**Requirements**: GEN-07
**Success Criteria** (what must be TRUE):
  1. Generated samples, plotted, visibly form two rings resembling the circles dataset's shape (not a blob, not concentrated in the empty middle). **NOT MET** — best result (natural-order correspondence, ring_mass=0.691) is a real, mechanistically-understood improvement over the documented baseline (ring_mass=0.609), owner-confirmed as "quite an improvement... still not two distinct rings."
  2. Any hyperparameter or architecture tuning needed to reach recognizable output is documented. **MET** — see `results/phase4_summary.md`, `DESIGN_DECISIONS.md`, `.planning/STATE.md`.
**Plans**: 3 plans, plus 2 ad hoc (non-GSD) tuning axes (batch-size sweep, natural-order spatial correspondence)
**Status**: CONCLUDED 2026-07-25 — GEN-07 not met, owner's explicit instruction: "GEN-07 not met, move to Phase 5."

Plans:
- [x] 04-01-PLAN.md — Visualize sigma=0.1 checkpoint (scatter + heatmap + ring/gap metric), decide if sweep needed
- [x] 04-02-PLAN.md — Conditional: full SIGMA_GRID sweep (5 values) if 04-01 decision says sweep-needed
- [x] 04-03-PLAN.md — Document tuning path, human-verify checkpoint confirming GEN-07 (result: not met)

### Phase 5: Benchmarking
**Goal**: The model's performance is honestly quantified and situated against a reference point, not presented as a bare "it trained."
**Depends on**: Phase 4
**Requirements**: BMK-01, BMK-02
**Success Criteria** (what must be TRUE):
  1. At least one benchmark/comparison metric (e.g. a held-out MMD statistic) is computed and reported for the trained generator.
  2. A qualitative or quantitative comparison against MerLin's photonic QGAN reproduction (paper #16, adversarial loss) is documented.
**Plans**: 1 plan
**Status**: Complete (2026-07-29) — BMK-01 met (held-out MMD² trained=0.0125±0.0003 vs untrained=0.0360±0.0048 vs floor=0.0114); BMK-02 met via explicitly-flagged qualitative fallback (QGAN reproduction trains on a different data domain, no matched metric possible without out-of-scope work)

Plans:
- [x] 05-01-PLAN.md — Held-out MMD² statistic (trained/untrained/floor baselines) + timed wall-clock/param-count instrumentation + citation-ready phase5_summary.md with BMK-02 qualitative fallback comparison against MerLin's photonic QGAN reproduction

### Phase 6: Documentation & Publication
**Goal**: The project is packaged into artifacts the owner can explain unaided — to Vincent Espitalier, in the Quandela pipeline, and in a portfolio — before September 1, 2026.
**Depends on**: Phase 5
**Requirements**: DOC-01, DOC-02, DOC-03, DOC-04
**Success Criteria** (what must be TRUE):
  1. README documents the problem, approach, and results with real numbers/plots, not just prose.
  2. A public GitHub repo (github.com/alejack312) contains working, runnable code and is publicly accessible.
  3. A 3-5 sentence technical note is drafted and ready to send to Vincent Espitalier.
  4. A portfolio case study is drafted in the IQP-MMD case-study format.
**Plans**: TBD

Plans:
- [ ] 06-01: TBD (assigned during plan-phase)

## Progress

**Execution Order:**
Phases execute in numeric order: 1 → 2 → 3 → 4 → 5 → 6

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Environment & Architecture Foundation | - | Complete | 2026-07-19 |
| 2. Generator Data & Loss Infrastructure | 4/4 | Complete | 2026-07-19 |
| 3. End-to-End Training Run | 1/1 | Complete | 2026-07-24 |
| 4. Generative Quality | 3/3 | Concluded (GEN-07 not met) | 2026-07-25 |
| 5. Benchmarking | 1/1 | Complete | 2026-07-29 |
| 6. Documentation & Publication | 0/TBD | Not started | - |

## Notes on Depth

Config requested "comprehensive" depth (8-12 phases). This roadmap uses 6 phases (1 complete + 5 active). Deviation is deliberate: this is a ~6.5-week solo research project explicitly scoped "not to impress" (PROJECT.md constraints), and the 15 v1 requirements cluster naturally into 6 delivery boundaries. Splitting further (e.g. separating bin-centers from the histogram, or the loss from training) would create phases with no independent verification value — a violation of the "coherent, verifiable capability" boundary rule. Padding to 8-12 would mean re-slicing a single build-and-verify sequence (GEN-02 through GEN-07) into artificially small pieces, which contradicts the requirements' own natural grouping and the project's stated scope discipline.
