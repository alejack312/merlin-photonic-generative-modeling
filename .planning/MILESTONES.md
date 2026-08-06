# Project Milestones: MerLin Photonic Generative Modeling

## v2.1 Weight-2 Implementation (Shipped: 2026-08-06)

**Delivered:** The weight-2 IQP generator (`heralded_cz`-based two-qubit diagonal phase gate, fixed at θ=π/4) that v2.0 designed on paper but never built or ran — now implemented, empirically de-risked, and validated to the same rigor bar weight-1 already cleared: exact-reference TVD comparison, honest herald-failure/residual accounting, and confirmed composability alongside weight-1 in a shared circuit.

**Phases completed:** 10-13 (6 plans total)

**Key accomplishments:**

- `heralded_cz`'s herald-success probability empirically confirmed at exactly 2/27 (~0.074074), uniform across all computational-basis and superposition inputs — replacing secondhand literature figures with a measured value for this specific Perceval implementation
- Full weight-2 generator circuit implemented (`build_cz_insertion`, `build_weight2_processor`) via `Processor`-level composition, reusing all four existing weight-1 builders completely unmodified
- Discovered and worked around a genuine Perceval library limitation (`add_herald`+`PBS` crash in `Processor.probs()`) via a herald-free measurement variant with manual post-selection — filed upstream as [Quandela/Perceval#783](https://github.com/Quandela/Perceval/issues/783)
- Weight-2 validated to the same rigor bar as weight-1: exact reference extended with `Z_i·Z_j` pair terms, TVD=2.58e-15 at the locked n=2, θ=π/4 gate, herald-failure probability and residual reported as two separate never-merged numbers
- Weight-1 and weight-2 layers confirmed to compose correctly in a shared n=3 circuit, including the stronger case of a weight-1 term stacked directly on a weight-2 pair member
- Full test suite grew from 26 (weight-1 baseline) to 118 tests, zero regressions across all 4 phases — each independently re-verified live by `gsd-verifier`, not trusted from summaries

**Stats:**

- 33 files modified (4,167 insertions, 45 deletions); 1,144 lines of Python across 4 files
- 4 phases, 6 plans, 38 commits
- 1 day (2026-08-06, same-day sprint, 09:04 → 21:42)
- 8/8 requirements shipped, 0 dropped, 0 scope-adjusted
- One tech-debt item found and closed within the milestone audit itself: `docs/iqp-photonic-encoding.md` had gone stale after Phase 11's own last edit, still describing weight-2 as unimplemented — fixed before archiving, not deferred

**Git range:** `58f007b` (Phase 10 context) → `e817844` (audit commit)

**What's next:** STUDY-01/STUDY-02 (trainability/barren-plateau and hardness-under-loss study) and WRITE-01 (write-up), now unblocked since weight-2 actually works. ARB-01 (arbitrary-θ weight-2) remains a genuinely open research question, not a resolvable implementation task. Two owner-only manual steps still open since v1.0: send the technical note to Vincent Espitalier, flip the repo public.

---

## v2.0 IQP → Photonic Encoding (Shipped: 2026-08-05)

**Delivered:** A defensible, on-paper, empirically-checked mapping from IQP's structure (commuting Z-diagonal gates, Hadamard-basis conjugation) onto Perceval's discrete-variable/Fock-space primitives — polarization encoding, weight-1 generators fully derived/implemented/validated (TVD ~1e-16 at n=2,3 against the exact qubit-side distribution), weight-2 derived on paper only and explicitly flagged as untested. Positioned honestly against Douce et al.'s (2017) CV precedent, including the multi-qubit case's honest parallel to their measurement-based gadget.

**Phases completed:** 8-9 (8 plans total)

**Key accomplishments:**

- Literature scoping (two independent search passes) found no existing DV/Fock-space linear-optical IQP construction and no impossibility result, yielding a **Go** verdict for original design work
- Demonstrated low-level Perceval API fluency (`Circuit`/`PS`/`BS`/`BasicState`/`Analyzer`) beyond the high-level wrapper, closed-form verified against single-photon split, HOM dip, and PS-driven MZI interference
- Compiled the qubit-side IQP structure/hardness and barren-plateau trainability baseline as the comparison reference
- Designed and implemented a polarization-encoded DV/Fock-space mapping — weight-1 generators exact and tested, falsifiable bidirectional bitstring↔Fock basis correspondence with explicit out-of-subspace handling
- Empirically validated the mapping: TVD ~1e-16 at n=2,3, ten orders of magnitude under the chosen 1e-6 threshold
- Honestly positioned against Douce et al. (2017), stating both the favorable contrast and the honest parallel; a real H/V port-labeling bug was caught and fixed mid-milestone via a direct calibration check

**Stats:**

- 1,282 lines added across code and tests (`iqp_photonic_encoding.py`, `perceval_fluency_demo.py`, plus test files); 3 new docs (`docs/iqp-lit-scoping.md`, `docs/iqp-baseline.md`, `docs/iqp-photonic-encoding.md`)
- 2 phases, 8 plans, 33 commits
- 6 days (2026-07-30 → 2026-08-05)
- 11/11 requirements shipped, 0 dropped, 0 scope-adjusted
- Phase 9 shipped without a standalone `gsd-verifier` VERIFICATION.md (tech debt flagged by the milestone audit); closed post-audit via an independent `/gsd:verify-work 9` UAT pass (8/8, live-verified)

**Git range:** `1200e75` (start) → `20da49a` (Phase 9 UAT)

**What's next:** No follow-on milestone scoped yet. The v2 requirements deferred this milestone (IMPL-01/02: minimal Perceval implementation + classical sanity check; STUDY-01/02: trainability/barren-plateau and hardness-under-loss study; WRITE-01: write-up) are the natural next candidates, contingent on the owner wanting to continue into implementation. Weight-2 (`heralded_cz`) implementation/testing is the most concrete first piece.

---

## v1.0 Photonic Generator (Shipped: 2026-07-29)

**Delivered:** A working, end-to-end, honestly-benchmarked MMD-trained photonic generative model on MerLin's `QuantumLayer`, published in a public-ready repo with a portfolio case study and a technical note ready for Vincent Espitalier — GEN-07 (clean two-ring generative output) not fully met, and reported that way rather than glossed over.

**Phases completed:** 1-6 (11 plans total)

**Key accomplishments:**

- Verified MerLin environment and decided the generator's core architecture (full-distribution MMD matching, not point-averaging or discrete sampling)
- Built and independently verified the generator's data/loss infrastructure — latent sampling, K bin-centers, real-data histogram, closed-form MMD² loss
- Trained the photonic generator end-to-end with a scripted (non-eyeballed) decreasing-MMD check — met the July 25 stall-risk checkpoint a day early, avoiding the prior project's stall pattern
- Tuned generative quality across three axes (sigma sweep, batch sweep, natural-order output correspondence); honestly concluded GEN-07 not fully met, with a real ring_mass 0.609→0.691 improvement from the natural-order fix — the project's key technical contribution
- Benchmarked the trained generator against untrained and real-vs-real-floor baselines, plus a qualitative comparison against MerLin's own photonic QGAN reproduction
- Published README, LICENSE, technical note, and an interactive portfolio case study — then ran a full self-audit (Codex/gpt-5.5 deep review) that caught and fixed a real documentation error and added honest caveats on unproven claims

**Stats:**

- 103 files created/modified
- 1,648 lines of Python
- 6 phases, 11 plans, 51 commits
- 10 days from project start to ship (2026-07-19 → 2026-07-29), well inside the ~6.5-week window

**Git range:** `57e2aee` → `9f713e6`

**What's next:** No follow-on milestone scoped yet. Candidates noted in PROJECT.md's "Next Milestone Goals": BMK-03 (exact apples-to-apples QGAN comparison), the untested natural-order-mechanism follow-ups (neighbor-locality test, post-fix sigma re-sweep), and the deferred IQP→photonic circuit mapping project.

---
