# Project Milestones: MerLin Photonic Generative Modeling

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
