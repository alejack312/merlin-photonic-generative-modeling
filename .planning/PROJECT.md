# MerLin Photonic Generative Modeling

## What This Is

A photonic quantum machine learning project built on MerLin (Quandela's PyTorch-based photonic QML framework): extending MerLin's quickstart circles-dataset classifier into an MMD-trained generative model. It reuses MMD-loss and generative-eval methodology from a prior IQP (gate-model) generative modeling project, applied here to a photonic circuit instead. Built as a credential and portfolio piece ahead of conversations with Vincent Espitalier and a Spring 2027 Quandela placement search.

## Core Value

A working, end-to-end, honestly-benchmarked MMD-trained photonic generative model, published in a public repo before September 1, 2026 — one the owner can explain unaided to Vincent Espitalier or in an interview. Explainability and a real end-to-end run matter more than polish or an ambitious result.

## Requirements

### Validated

- ✓ MerLin installed in a version-compatible environment (Python 3.12 venv; MerLin caps Python at 3.10–3.12, torch <2.13) — 2026-07-19
- ✓ Quickstart classifier (circles dataset) runs end-to-end; confirmed gradients flow through the quantum layer via PyTorch's autograd — 2026-07-19
- ✓ Generator output-representation architecture decided: full-distribution/histogram matching via closed-form MMD², not single-point averaging or discrete sampling — see [DESIGN_DECISIONS.md](../DESIGN_DECISIONS.md) — 2026-07-19

### Active

- [ ] Latent noise sampling + encoding as `QuantumLayer` input (generator's forward pass)
- [ ] Fixed set of K bin-centers defined, spanning the circles data's (x, y) region
- [ ] Real-data histogram (`p_real`) precomputed once over the K bin-centers
- [ ] Closed-form MMD² loss implemented between the model's probability-vector output (`q`) and `p_real`, using a kernel over bin-center coordinates
- [ ] Training loop runs end-to-end with a real (even if rough) MMD-decreasing run
- [ ] Generator's samples visibly approximate the two-ring circles shape
- [ ] At least one benchmark/comparison metric reported (held-out MMD statistic, and/or qualitative comparison against MerLin's own photonic QGAN reproduction — paper #16 in its catalog, which uses adversarial loss instead of MMD)
- [ ] README documenting problem, approach, and results (numbers/plots, not just prose)
- [ ] Public GitHub repo (github.com/alejack312) with working, runnable code
- [ ] Short technical note (3–5 sentences) ready to send to Vincent Espitalier
- [ ] Portfolio case study drafted (IQP-MMD case-study format)

### Out of Scope

- **Reproducing the IQP gate-model circuits directly in MerLin** — no established IQP→linear-optics reduction exists; doing this honestly would be original theoretical research, not an extension. Parked as its own post-Sept-1 project, sequenced right after this one — see [Post_Sept1_IQP_Photonic_Plan.md](../Post_Sept1_IQP_Photonic_Plan.md).
- **PennyLane independent contributions** — parked, sequenced after the IQP-photonic project (decided 2026-07-19, per SMART spec).
- **ket.jl / SDP self-study** — informal free-time research only, no artifact expected, doesn't compete with the sequence above.
- **Weighted-average → single continuous point output mapping** — rejected: collapses multimodal targets (circles' two rings) into their midpoint, a region with zero real density. See [DESIGN_DECISIONS.md](../DESIGN_DECISIONS.md).
- **Discrete `shots`-based sampling for the generator** — rejected: not differentiable through standard autograd without an additional estimator (e.g. REINFORCE, Gumbel-softmax), not worth the added complexity for this timeline.
- **Exact replication of MerLin's photonic QGAN paper's full MNIST-patch dataset/architecture** — treated as a stretch goal if time allows (targeted for the Aug 8 milestone), not a hard requirement; the core deliverable uses the simpler circles dataset already in the quickstart.

## Context

- **Deadline pressure:** Hard deadline September 1, 2026, driven by a warm contact (Vincent Espitalier) and the Quandela Spring 2027 placement pipeline. MerLin experience is a stated gap in current Quandela positioning.
- **Historical stall pattern:** A prior self-directed track (PennyLane) has been stalled since May 2026. July 25, 2026 is explicitly flagged in the SMART spec as "not a formality" — if there's no end-to-end run by then, that's the same stall pattern recurring and must be named plainly, not glossed over.
- **Prior relevant expertise:** PyTorch; MMD-loss and generative-modeling experience from an IQP-MMD project; general quantum ML fluency; IQP circuits and barren-plateau research.
- **MerLin specifics (verified empirically, not just from docs):** `ML.QuantumLayer.simple(input_size, output_size)` returns a probability distribution over `output_size` measurement outcomes — non-negative, rows sum to exactly 1. `forward()` also accepts `shots`/`sampling_method` for literal discrete sampling instead of the exact expectation (rejected for this project — see Out of Scope).
- **Reproduced-papers catalog (21 papers)** was checked directly — none reproduce IQP circuits. Closest neighbors: photonic QGAN (#16, adversarial loss, Sedrakyan & Salavrakos 2024) and QSSL (#14, contrastive loss, Jaderberg et al. 2021).
- **Repo state:** `quickstart.py` (verified working), `requirements.txt`, `.gitignore`, `CLAUDE.md` (collaboration rules for this project), `MerLin_SMART_Spec_Sept1.md`, `DESIGN_DECISIONS.md`, `Post_Sept1_IQP_Photonic_Plan.md`. Local git repo initialized, no commits yet. Python 3.12 venv with `merlin 0.4.0`, `torch 2.12.1+cpu`.

## Constraints

- **Timeline**: Hard deadline Sept 1, 2026; Jul 25, 2026 is a critical early checkpoint (historical stall point) — a milestone, not a suggestion.
- **Tech stack**: Python 3.10–3.12 only (MerLin's `pyproject.toml` caps here; the machine's default `python` is 3.13, which is unsupported — the project venv pins 3.12). `torch<2.13`, `perceval-quandela>=1.2.1`.
- **Collaboration process** (see [CLAUDE.md](../CLAUDE.md)): core conceptual/design decisions require the owner's own attempt or explanation before full implementation is written; self-explanation checkpoints occur at each SMART-spec milestone; no silent unilateral design decisions.
- **Scope discipline**: single project only, sized to fit the window — not a multi-paper reproduction, not a stretch for impressiveness.

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Extend quickstart classifier into an MMD generator (SMART spec option b), rather than reproduce a catalog paper directly (option a) | Best reuses the owner's actual specialized background (MMD/generative modeling); gives a natural comparison point against MerLin's own photonic QGAN reproduction (adversarial loss) | — Pending |
| Generator output = full-distribution/histogram matching via closed-form MMD² (not single-point averaging, not discrete sampling) | Avoids collapsing circles' two-ring (multimodal) target into its empty middle; avoids the non-differentiability of discrete sampling; reuses the exact closed-form MMD² formula from the owner's prior IQP-MMD work | — Pending |
| IQP→photonic circuit mapping parked to a dedicated post-Sept-1 project, sequenced before PennyLane | Genuinely interesting, but no established IQP→linear-optics reduction exists — doing it honestly is original research, too heavy/risky for this deadline. Explicit three-track relapse risk flagged for when Sept 1 arrives. | — Pending |
| Python 3.12 venv instead of system default Python 3.13 | MerLin's `torch<2.13` + `python>=3.10,<=3.12` constraints would break dependency resolution on 3.13 | ✓ Good — verified working |

---
*Last updated: 2026-07-19 after synthesis from MerLin_SMART_Spec_Sept1.md, DESIGN_DECISIONS.md, and prior conversation (no fresh interview run — see project's own AskUserQuestion decision to synthesize existing docs instead)*
