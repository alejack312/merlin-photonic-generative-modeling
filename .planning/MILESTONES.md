# Project Milestones: MerLin Photonic Generative Modeling

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
