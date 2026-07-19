# SMART Specification: MerLin Project
**Owner:** Alejandro Jackson
**Deadline:** September 1, 2026
**Status as of:** July 6, 2026 (traveling until ~July 11)

---

## Scope decision (read this first)

This document covers **one committed deliverable: the MerLin project.**

PennyLane contributions and ket.jl/SDP self-study are **parked for this cycle** — not cancelled, just not competing for the same hours. Reasoning: three unstarted tracks with a demonstrated stalling pattern (PennyLane since May) is not a realistic plan. MerLin has an active warm contact (Vincent Espitalier) expecting follow-through and a live pipeline target (Quandela). That earns priority.

If MerLin finishes with real buffer time before Sept 1, you may pick up **one** stretch track — not both. Decide that in Week 5, not now.

---

## S — Specific
Build and publish one complete, working project using **MerLin** (Quandela's photonic QML framework), either:
- (a) reproducing a paper from MerLin's reproduced-papers catalog, or
- (b) meaningfully extending the quickstart classifier with a novel experiment (e.g., a photonic analogue of your MMD-based generative modeling work)

Decision on (a) vs (b) is due by **July 18** (see milestones).

## M — Measurable
Deliverable is complete when ALL of the following exist:
- [ ] Public GitHub repo (github.com/alejack312) with working, runnable code
- [ ] README documenting the problem, approach, and results (numbers/plots, not just prose)
- [ ] At least one benchmark or comparison metric reported (accuracy, loss curve, fidelity — whatever fits the chosen project)
- [ ] Short technical note (3–5 sentences) summarizing the project, ready to send to Vincent Espitalier
- [ ] Portfolio case study drafted (can follow IQP-MMD case study format)

## A — Achievable
- Effective working window: **July 14 – Aug 31** (~6.5 weeks, post-travel)
- Directly transferable skills: PyTorch (MerLin is PyTorch-based), MMD-loss/generative modeling experience from IQP-MMD, general quantum ML fluency
- Scope is intentionally single-project, not multi-paper — sized to fit the window, not to impress

## R — Relevant
- Directly serves the Quandela pipeline (warm Vincent thread) and Spring 2027 placement search
- MerLin experience is a stated gap for Quandela positioning ("existing gate-based IQP code does not translate")
- This is the only one of the three tracks tied to an active, expectant human contact

## T — Time-bound: Milestones

| Date | Milestone |
|---|---|
| **Jul 11** | Back from travel |
| **Jul 18** | Project chosen (a or b), MerLin installed, quickstart run locally, repo scaffolded |
| **Jul 25** | Core implementation started; first end-to-end (even if broken) run completed |
| **Aug 8** | Working version producing real output/metrics |
| **Aug 15** | Debugging + benchmark/comparison complete |
| **Aug 22** | README + results write-up drafted |
| **Aug 29** | Portfolio case study + technical note for Vincent drafted |
| **Sep 1** | Repo public, README finalized, note sent to Vincent |

---

## Risk check-in (be honest with yourself here)

- **If by Jul 25 nothing has run end-to-end yet:** this is the same stall pattern as PennyLane. Flag it explicitly rather than letting the date quietly slip.
- **Weekly gut-check question:** "Did I touch this project this week, or did I just think about it?" Thinking about it doesn't count.
- **If you're tempted to fold PennyLane or ket.jl work back in before Sep 1:** that's the three-track pattern reasserting itself. Don't.

---

## Explicitly parked (not part of this deadline)
- **IQP → photonic encoding research project** — next up after Sept 1, immediately following MerLin. See [Post_Sept1_IQP_Photonic_Plan.md](Post_Sept1_IQP_Photonic_Plan.md).
- **PennyLane independent contributions** — sequenced after the IQP-photonic project wraps, not competing with it. (Decided 2026-07-19.)
- **ket.jl / SDP self-study** — informal free-time research only, no artifact or deliverable expected. Not scheduled, doesn't compete with the sequence above.

Order decided 2026-07-19: MerLin (current) → IQP-photonic → PennyLane. ket.jl/SDP runs ambiently in parallel with no deadline pressure.
