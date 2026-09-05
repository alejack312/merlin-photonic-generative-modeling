# Project Milestones: MerLin Photonic Generative Modeling

## v3.1 Correction (Shipped: 2026-09-04)

**Delivered:** Corrected the public record after a 2026-09-03 external audit (Fable 5.1) found both v3.0 co-lead findings were pipeline artifacts — trainability's exponential decay was the MMD kernel going numerically identity below the target grid's bin spacing (no circuit content), and hardness-under-loss's `tvd_to_lossless` was a closed form in `eta`/`n` alone from post-selecting on full photon survival. Shipped owner-derived null-result regression tests, dated additive corrections across every affected document and the public case-study page, a throughput reframing of the hardness result, a standing `CLAUDE.md` null-result gate, and an independent Codex adversarial review of the correction itself.

**Phases completed:** 1 (Phase 24 — executed interactively, no `gsd-executor`/PLAN.md; substance delivered via direct commits plus 2 `/gsd-quick` tasks: `260903-t9j` TCDQ framing gap, `260903-ukn` REFRAME-02)

**Key accomplishments:**

- Diagnosed and closed-form-proved both v3.0 artifacts: TRAIN's `weight1/uniform` exponential decay reproduced by a no-circuit-content product-distribution model; HARD's `tvd_to_lossless` = `½(1−eta^n)` (weight1) / a herald-conditioned analogue (mixed) — both verified to floating-point precision against the shipped CSVs
- Built the owner-derived null-result test suite (`tests/v3_correction/test_null_results.py`), gating every other correction task per this phase's own attempt-first rule
- Shipped dated, additive corrections in all 7 required documents (trainability-study, hardness-under-loss-study, technical-findings, README, iqp-lit-scoping, Post_Sept1 plan) plus the separate public case-study repo — originals kept, never deleted
- Reframed the hardness section around what it actually shows: a throughput-vs-`n,k` table (verified `k=0,1`, flagged-extrapolated `k≥2`) now leads the section, replacing the old TVD-as-hardness framing
- REFRAME-02: stopped silently discarding partial-loss photon data — both loss-model functions now return a `partial_loss` breakdown, all 5 real call sites updated, mass-conservation regression tests added
- Added a standing `CLAUDE.md` null-result gate + learning note so a future sweep can't repeat this failure mode
- Ran an independent Codex adversarial review of the correction itself (not just the original findings) — confirmed 9 of 13 flagged issues as real overclaims (e.g. the trainability correction's own "identity kernel at every n" claim overstated past `n=4`) and fixed them
- Sent the correction note to Vincent Espitalier (COMM-01), closing the milestone's one external-facing commitment

**Stats:**

- 34 files changed, 2,138 insertions / 74 deletions
- 1 phase, 0 formal plans (interactive + 2 quick tasks), 19 commits
- 2 days (2026-09-03 → 2026-09-04)
- 12/13 requirements shipped; 1 tracked as a known gap (see below)

**Git range:** `0658ab6` (first correction commit) → `ab969ed` (COMM-01 closed)

**Known gaps at close (tracked separately, not blocking):**
- **NULL-01 (partial):** the mixed-scope `h(eta)` null formula was sourced from a parallel Fable 5.1 session rather than derived by the owner. The weight-1 formula is fully owner-derived and self-explained; the mixed-scope formula's self-explanation placeholder in `tests/v3_correction/test_null_results.py` remains unfilled. Owner-gated by the requirement's own design — not a task for Claude to close.

**What's next:** v4.0 direction undecided (per `24-CONTEXT.md`'s decision log). A "Train Classically, Deploy Photonically" plan already exists on the `claude/merlin-photonic-iqp-audit-e8144c` branch (`docs/v4-plan-train-classical-deploy-photonic.md`, phases 26-32, not yet executed) as one candidate, alongside the other audit-identified frontier directions explicitly deferred out of v3.1's scope (structured n≈20+ simulator, Hamming-kernel trainability rerun, distinguishability noise, non-post-selected simulability analysis).

---

## v3.0 IQP Circuit Study & Write-Up (Shipped: 2026-08-24)

**Phases completed:** 11 phases, 50 plans, 88 tasks

**Key accomplishments:**

- Full go: juliaup + Julia 1.10.11 LTS + Yao.jl 0.9.1 + BosonSampling.jl 1.0.2 all installed and verified via hand-derived-analytical-assertion hello-world scripts, with zero alternate-path attempts needed.
- Confirmed `PostProcessedControlledRotationsItem` implements `CP(α) = diag(1,1,1,e^{iα})` via `Simulator.prob_amplitude` on the bare 8-mode circuit at 3 non-trivial α (π/6, π/3, 2π/5) plus the α=π boundary, independently reproducing the 1/9 literature figure and `heralded_cz`'s exact sign pattern.
- Wired `build_cp_insertion` into the complete weight-2 IQP pipeline as `photonic_cp_iqp_distribution`, found and fixed a postselection-accounting bug that was the root cause of `15-RESEARCH.md`'s previously-unresolved TVD~0.3-0.4 finding, and validated the corrected pipeline to floating-point-noise-level TVD against the exact reference at n=2,3 across 3 non-trivial α values plus the α=π boundary against `heralded_cz`.
- Added a parametrized pytest test confirming CP(alpha)'s arbitrary-theta weight-2 gate composes correctly with weight-1 terms at n=3, across 3 distinct non-trivial alpha values, closing ARB-07.
- 16-point α sweep of `photonic_cp_iqp_distribution`'s measured success probability across `[0, 2π)`, every point asserted against the closed-form `1/σ_max(α)⁴` to within 1e-6, saved as CSV+PNG and documented as a direct extension of Phase 15's 4-point table.
- Relational Forge model (`forge/ancilla_mapping.frg`) formally confirms the CP(alpha) insertion's 8-key local->global ancilla mode-mapping dict is injective/non-aliasing for every valid (n,i,j) up to n=8, checked against all n qubits' own data ports, not just i/j's — both required sat (non-vacuity) and unsat (non-collision) checks passed, no bug found.
- Concurrent wave-1 execution:
- Pure-numpy port of `generator/mmd.py`'s Gaussian-kernel MMD^2 quadratic form plus a new exact chain-rule gradient (`mmd2_grad`), torch-parity verified to 1e-6 and gradient-exactness verified to 1e-9 against an algebraically-known synthetic quadratic.
- Numpy `make_target_grid(n)` generalizes v1.0's fixed K=462 MMD target grid to any K=2^n, cross-validated bit-faithfully against the existing `compute_p_real` by matching torch.cdist's internal distance formula, not just its output.
- `trainability/curve_fit.py` implements `scipy.optimize.curve_fit`-based exp-vs-poly model comparison with R^2 and AIC, TDD-proven to recover the correct verdict on synthetic ground-truth data before ever touching real sweep data.
- `run_gradient_variance_sweep` wires the exact parameter-shift gradient, exact MMD^2 gradient, and per-n target grid into one pooled gradient-variance measurement per (n, generator_scope, init_scheme), backed by a reorder-safe hashed-seed RNG utility.
- Produced the phase's real measured dataset -- gradient-variance-vs-n for weight-1 (n=2..6) and mixed weight-1+weight-2 (n=2..5) generators, both init regimes, via `gradient_variance_sweep.py` -- after diagnosing and fixing two genuine Perceval/memory blockers that the original plan's script design didn't anticipate.
- Ran Plan 17-04's poly-vs-exponential model comparison against Plan 17-06's real gradient-variance data for all 4 (generator_scope, init_scheme) cells, finding 2 statistically clear "exp" verdicts (weight1/uniform, mixed/uniform), 2 inconclusive fits, and one direct disagreement with `docs/iqp-baseline.md`'s qubit-side plateau rule (mixed/uniform: rule predicts no_plateau at n_max=5, measured data shows exponential decay) — written up honestly in `docs/trainability-study.md` with an owner-interpretation placeholder rather than an asserted conclusion.
- `trainability/data_dependent_init.py` implementing Recio-Armengol et al.'s (arXiv:2503.02934 Sec 8.1.2) data-dependent init recipe on this project's grid-bin `p_real`, with the bitstring-index-to-qubit bit-ordering convention proven correct by a dedicated test rather than assumed.
- Threaded an explicit, backward-compatible `sigma` kernel-bandwidth parameter through `trainability/sweep.py` and `gradient_variance_sweep.py`'s CLI, plus a `target_grid.bin_spacing(n)` reporting helper, with a structural fix (sigma embedded in chunk filenames) so chunk/combine sigma mismatches fail loudly instead of silently corrupting results.
- `init_scheme="data_dependent"` is now a fully working, deterministic, CLI-selectable option end to end (trainability/sweep.py through gradient_variance_sweep.py), with the mixed-scope weight-2-pair override provably implemented, not silently assumed.
- Real gradient-variance-vs-n dataset across a 6-point sigma grid {0.03, 0.1, 0.3, 1.0, 3.0, 9.0} for both generator scopes (weight1 n=2..6, mixed n=2..5), both init schemes, produced via `gradient_variance_sweep.py`'s existing `--sigma`/draw-chunking CLI -- 108 total data rows, all `var` finite, with an executed (not assumed) sigma=0.1 consistency check against Phase 17's original CSVs.
- Ran TRAIN-10's data-dependent-init sweep (~40s total) and built `trainability_analysis_1701.py`, which applies Phase 17's unmodified `fit_and_compare` to both follow-up datasets — finding weight1/uniform and mixed/uniform's original "exp" verdict survives near Phase 17's original sigma=0.1 but disappears at sigma in {0.3, 1.0} (non-monotonically re-emerging for weight1 at higher sigma), and that data-dependent init did not resolve small_angle's "inconclusive" verdict in either generator scope.
- Wrote docs/trainability-study.md's TRAIN-09 (bandwidth sensitivity) and TRAIN-10 (data-dependent init) follow-up sections, reporting both as honest either-direction findings: the original "exp" verdict is NOT robust across the sigma grid (non-monotonic for weight1/uniform), and data-dependent init did NOT resolve small_angle's inconclusive verdict.
- Downloaded and fully read the genuine Aaronson-Brod paper (arXiv:1510.05245) for the first time in this project, and added two verbatim-quoted, explicitly-distinguished citation bullets to `docs/iqp-baseline.md` — correcting `18-CONTEXT.md`'s original misattribution of arXiv:2510.24137 as "Aaronson-Brod" before it could propagate further.
- `photonic_iqp_distribution_lossy(n, thetas, eta)` — weight-1 photon loss via `pcvl.LC` component insertion (never `NoiseModel`), with both of 18-RESEARCH.md's load-bearing Perceval pitfalls proven avoided by dedicated regression tests, not just documented.
- `photonic_weight2_iqp_distribution_lossy(n, i, j, thetas, eta)` — heralded_cz photon loss via `pcvl.LC` on all `2n+2` modes (including both herald ancilla modes), with herald-failure/transmission-loss compounding measured through one real `Processor.probs()` call and proven to differ from a naive analytical decomposition.
- `hardness/baselines.py` implementing HARD-05's two classically-easy comparison distributions (uniform, product-of-marginals) plus BMS Theorem 4's anticoncentration parameter `alpha(dist, n)`, all pure/Perceval-free and verified against known closed-form values.
- `hardness/sweep.py` (per-cell TVD/anticoncentration/herald-failure integration) and `loss_sweep.py` (chunked/resumable CLI) wired together and verified end-to-end; a real machine-measured timing probe found weight-1 n=6 costs ~1900x more than n=4's extrapolated figure and mixed n=5 hits a reproducible, unfixable single-call `MemoryError` -- both facts now locked into `results/phase18_timing_probe.md`'s Final n-range decision for Plan 18-06.
- Ran the phase's central compute-heavy measurement: real TVD-vs-eta and anticoncentration-alpha-vs-eta data for weight-1 (n=2..6, 35 rows) and mixed weight-1+weight-2 (n=2..4, 21 rows) generators across the full 7-point eta grid, with herald-failure-vs-eta tracked explicitly for mixed scope; confirmed mixed n=5 is a genuine, three-times-reproduced single-call memory ceiling that draw-chunking cannot fix.
- Turned Plan 18-06's real measured weight-1/mixed loss-sweep CSVs into `docs/hardness-under-loss-study.md` -- Phase 18's canonical results document, with `hardness_analysis.py` producing the 3 plots it embeds.
- Closed HARD-04 by declining to fabricate an eta->epsilon depolarizing translation (owner's explicit attempt-first decision) and instead positioning this phase's tested loss range against two loss-native hardness regimes -- Aaronson-Brod's fixed-photon-count result and a newly-verified 2025 lossy-Gaussian-boson-sampling logarithmic-fraction result -- closing out Phase 18 entirely.
- `julia/generate_reference.py` calls this repo's already-tested exact and lossy IQP distribution functions directly and writes 11 self-documenting CSV files (5 exact-case, 6 fixed-single-draw loss-case) that Plans 19-02 through 19-05's independently-built Julia scripts diff against.
- Independent Yao.jl circuit (H/Rz/put/chain primitives) reproduces `iqp_photonic_encoding.py`'s exact qubit-side IQP distribution at n=2 and n=3 with measured TVD of 2.3e-17 and 1.1e-16 respectively -- roughly 10 orders of magnitude inside the locked 1e-6 tolerance.
- Independently-built BosonSampling.jl dual-rail weight-1 photonic IQP circuit reproduces the Python/Perceval reference distribution to TVD ~1e-16 at n=2 and n=3 (well under the 1e-6 tolerance), with the phase-shift-to-theta convention algebraically derived rather than assumed.
- Sourced the Knill CZ gate's unitary directly from the original 2001 paper (arXiv:quant-ph/0110144, Eq. 11), built it independently in BosonSampling.jl, found and fixed a real transpose-convention bug via a standalone zero-leak diagnostic, and reproduced Python's locked weight-2 gate distribution to floating-point precision (TVD=3.5e-15) -- a full GO, not a partial-go.
- BosonSampling.jl's native `UniformLossInterferometer` loss model (not a hand-attenuation fallback), with one narrow documented workaround for a real dispatch bug in the installed v1.0.2 package, reproduces Phase 18's LC-based photon-loss distributions for both weight-1 and mixed (weight-1+weight-2) scope at n=2, all 3 tested eta values, with TVD between 1e-14 and 1e-18 -- a full GO, not a partial-go.
- Wrote `docs/julia-cross-check-study.md`, folding Plans 19-02..19-05's four independent Julia cross-checks into one canonical results document, and corrected REQUIREMENTS.md's VERIFY-02/03/04 rows from Pending to Complete to match the real, all-GO outcome.
- Owner's own multi-step reasoning (including a ruled-out hypothesis) closed TRAIN-07's genuinely open interpretation gap; added an 11-baseline WRITE-02 literature table and a hedged Herbst et al. cross-reference note to docs/trainability-study.md.
- Added HARD's WRITE-02 literature comparison table (11 baselines, 5 substantive + 6 silent) and a Herbst et al. cross-reference note to `docs/hardness-under-loss-study.md`, correcting an earlier speculative anticoncentration-direction guess in `docs/iqp-baseline.md` and fixing a stale header note left over from before Plan 18-08 completed the document.
- Added a section-scoped "what this does/doesn't establish" subsection plus a 1-row-plus-prose literature comparison table to `docs/iqp-photonic-encoding.md`'s ARB-01/ARB-02 section, closing the one structural gap Phase 20's research identified relative to TRAIN's and HARD's existing per-section scope subsections.
- Wrote `docs/technical-findings.md`, the project's single project-level synthesis document, mirroring all three source docs' literature tables and pointing at (not re-deriving) their scope statements, the Herbst et al. cross-thread, and the julia-cross-check independent verification.
- Two new Section blocks (v3.0 headline findings; supporting gate-validation/Julia evidence) inserted into the live `merlin-quantum.tsx` portfolio page between Technical Depth and Role, plus an extended Role QuoteBlock naming the TRAIN-07 transcribed-reasoning mechanism — committed locally in a separate repo (`alejandro-jackson`), not pushed.
- Added a short "v3.0: IQP Circuit Study" section to README.md — honest co-lead-findings pitch (including the sigma-grid negative result and the no-eta-translation scope call) that links out to the case-study page and `docs/technical-findings.md` instead of restating them.
- Numerically confirmed pooled-vs-dedicated ancilla reuse is physically safe (TVD ~1e-14) for the vertex-disjoint two-pair configuration D-02's pooling scheme actually uses, while separately discovering and documenting a real, unrelated composability limit when two CP(alpha) insertions share a data qubit pair.
- Owner ruled GO on ancilla reuse (MPAIR-07); MPAIR-02's prose invariant for pooled/recycled ancilla allocation (vertex-disjointness compatibility rule, round-robin K_n edge-colouring formula, mode-index generalization, `for 7 Int` bitwidth, 406-case pairwise-reduction argument, and scope boundary against the physics claim) is written before any Forge code exists.
- Owner confirmed both mechanism premises (vertex-disjoint compatibility rule and fixed round-robin allocation formula) via the `confirm-both` option, discharging 22-CONTEXT.md's flag-back obligation with no revisions needed to the invariant file.
- Built `forge/pooled_ancilla_allocation.frg`, a Forge model that SEARCHES for a minimum ancilla-block edge-colouring of `K_n` (not verifying a fixed formula), confirming Forge's independent minimum matches the round-robin formula's `K` at n=4/5/6 (both parities) before the search hit D-04's 10-minute ceiling at n=7 -- honestly reported rather than shrunk to fit.
- Backtracking-DFS colouring search matches Forge's minimum K exactly at every n Forge reached (4, 5, 6) and additionally solves n=7 (2.28s) and n=8 (0.006s) where Forge's own exhaustive SAT-backed search timed out at n=7 (~610s, zero blocks resolved) — Forge did not earn its place here either, verdict recorded as passing per the corrected MPAIR-05 criterion.
- The pooled multi-pair ancilla allocation scheme is recorded in `docs/iqp-photonic-encoding.md` as a specification for future implementation (Task 1, already committed at `366a5bf`), and the owner's live self-explanation checkpoint — which surfaced and corrected a real conflation between MPAIR-07's physics comparison and MPAIR-02's combinatorial argument before closing — is transcribed verbatim into the document (Task 2, this commit), closing Phase 22.
- Bounded Forge model of CP(alpha) ancilla allocation, deferred liveness, and trace-shaped reuse witnesses
- Reproducible Forge output and human-readable lifecycle traces preserving the Phase 22 comparison boundary
- Owner-reviewed lifecycle conclusion distinguishing static minimum-K coloring from temporal deferred-postselection capacity

---

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
