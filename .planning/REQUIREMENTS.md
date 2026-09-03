# Requirements: MerLin Photonic Generative Modeling — v3.1 Correction

**Defined:** 2026-09-03
**Core Value:** A working, end-to-end, honestly-benchmarked photonic project, published in a public repo — explainable unaided to Vincent Espitalier. v3.1 exists to keep the "honestly-benchmarked" half true after an external audit found two v3.0 headline findings were pipeline artifacts.

## Why this milestone exists

The 2026-09-03 audit (Fable 5.1, artifact `claude.ai/code/artifact/2eb88fd5-d090-4933-82b8-396135c2f348`) established, by recomputation against the shipped CSVs:

1. **TRAIN.** At `sigma` in {0.03, 0.1} the Gaussian kernel over the `2^n` target grid is numerically the identity (bin spacing 1.2 → 0.17 for n=2..6, always larger than sigma), so MMD² is the squared L2 distance between two probability vectors. On a product distribution that gradient variance scales as `2^-n` regardless of the circuit. The shipped `weight1/uniform` curve (0.304, 0.198, 0.118, 0.061, 0.031) is reproduced by a ten-line closed-form product model with no photonics. It is not a barren plateau; a weight-1 circuit cannot have one.
2. **HARD.** Every mixed-scope `tvd_to_lossless` row equals `½·(1 − eta^(n+2))` (n data photons + 2 herald photons) and every weight-1 row equals `½·(1 − eta^n)`. Post-selecting on full photon survival returns the lossless distribution by definition, so shape-preservation and `alpha` invariance are tautologies. The non-post-selected output (partial-loss shots) was never analyzed.

Both were catchable by writing the null result before running the sweep. The milestone's scope is the correction and the gate that prevents recurrence — not the frontier work the audit also identified (that is a v4.0 decision, not made here).

## v1 Requirements

All Must-have unless marked otherwise. Order matters: NULL-01 gates everything else.

### Null-result derivation, owner-owned (NULL)

- [ ] **NULL-01**: The owner fills the two null-result formulas in `tests/v3_correction/test_null_results.py` (`owner_hard_null_tvd` and `owner_train_null_ratio`) and runs the file red/green against the shipped CSVs, before any other task in this phase starts. Derivation is by experiment, not by hand: propose a formula, run it against the data, revise. The formula is "derived" when the test is green for every row and the owner can say in one sentence why it has that form. Claude may ask questions and point at data; Claude does not supply the formula. *(Attempt-first gate; self-explanation checkpoint for the phase.)*
- [ ] **NULL-02**: The filled tests are promoted from `skip` to real assertions, cover every row of `results/v3_hardness/phase18_weight1_loss_sweep.csv`, `phase18_mixed_loss_sweep.csv`, both `phase18_merlin_dual_rail_*` CSVs, and the `sigma in {0.03, 0.1}` rows of `results/v3_trainability/phase171_train09_*_gradient_variance.csv`, and are green in `python -m pytest -q`.

### Corrections to shipped documents (CORR) — additive, dated, never deleted

- [ ] **CORR-01**: `docs/trainability-study.md` gains a dated "Correction (2026-09)" section at the top of Results: the exp verdict rows are a loss-normalization artifact; the TRAIN-09 sigma pattern is the kernel changing character relative to grid spacing; the Rudolph et al. row is upgraded from "directionally consistent" to "this is the mechanism". The original tables stay, labeled as a documented artifact.
- [ ] **CORR-02**: `docs/hardness-under-loss-study.md` gains the same kind of section: the closed form for `tvd_to_lossless`, why `alpha` invariance is a tautology under post-selection, and the statement that the non-post-selected distribution was not analyzed. TVD tables move under an "appendix: pipeline check" heading in spirit (retitled, not removed).
- [ ] **CORR-03**: `docs/technical-findings.md` mirrors both corrections in its Trainability and Hardness sections and in the Herbst cross-thread (now doubly silent).
- [ ] **CORR-04**: `README.md` v3.0 headline paragraphs rewritten to state the corrected findings first; the "how this was built" paragraph mentions the external audit and the null-result gate.
- [ ] **CORR-05**: `docs/iqp-lit-scoping.md` gains an addendum: Hoban et al. (arXiv:1304.2667, IQP = non-adaptive X-Y-plane MBQC on graph states) and KLM answer the Phase 0 question ("yes, trivially"); Oh (arXiv:2406.08086), Oszmaniec–Brod (2018), Xie/Notton/Senellart (arXiv:2605.11879), Salavrakos et al. (arXiv:2405.02277) added as the loss-native and Quandela-authored baselines the earlier searches missed. Abstract-level reads are labeled as such until read in full.
- [ ] **CORR-06**: `Post_Sept1_IQP_Photonic_Plan.md`'s "no established IQP→linear-optics reduction is known" sentence corrected; the open question restated as resource cost under MBQC versus KLM.
- [ ] **CORR-07**: The public case-study page (`C:\Users\cuqui\projects\alejandro-jackson\src\pages\case-studies\merlin-quantum.tsx`, separate repo) carries the same corrections; `npm run lint` and `npm run build` green; push is a separate explicit owner action.

### Reframing the hardness result (REFRAME)

- [ ] **REFRAME-01**: `docs/hardness-under-loss-study.md` states the actual hardness-under-loss result for this encoding as its headline: the post-selected distribution is exactly the lossless one, and the cost is throughput `eta^(n+2k) · (2/27)^k` for k heralded CZs (or the CP(alpha) analogue). A short table or plot of throughput vs n and k, computed from the closed form, replaces the TVD plots as the figure the section leads with.
- [ ] **REFRAME-02** *(Should)*: `photonic_iqp_distribution_lossy` and `photonic_weight2_iqp_distribution_lossy` additionally return the non-post-selected outcome distribution (partial-loss patterns kept as their own keys, not collapsed into `residual`), with a test that its total mass plus the in-subspace mass equals `global_perf`-consistent totals. No analysis of it in this milestone — this only stops discarding the data.

### Process gate (GATE)

- [ ] **GATE-01**: `CLAUDE.md` gains a "Null-result gate" rule: before any sweep or measurement phase, the owner writes the closed-form prediction for what the pipeline outputs if the circuit contributes nothing, as a test; a measurement matching the null is a pipeline check, not a finding. Recorded in `.claude/learnings/`.
- [ ] **REVIEW-01**: Before CORR-04/CORR-07 ship, an independent Codex (`gpt-5.5`) review of the corrected docs is run with the explicit prompt "for each stated finding, write the null result and check whether the finding differs from it". Findings addressed or explicitly declined in the phase summary.

### Communication (COMM)

- [ ] **COMM-01**: A correction note to Vincent Espitalier is drafted by the owner (three to five sentences: what was wrong, what each result actually shows, link to the corrected repo). Whether and when to send is the owner's call and is recorded as a decision either way; the draft exists regardless, because the public case study and repo already carry the claims.

## Out of Scope (explicit — v4.0 candidates, not decided here)

- Structured tensor-product simulator to reach n ≈ 20+ (audit item D).
- Re-running trainability with a Hamming kernel, bandwidth ∝ n, observable-based loss, full ZZ layer.
- Partial-distinguishability / g2 noise model (audit item C).
- Non-post-selected lossy IQP simulability analysis (audit direction 1).
- Herald-cost gradient variance (audit direction 2), train-classical/deploy-photonic gap (direction 3), KLM-vs-graph-state comparison (direction 4).
- Any new headline claim. v3.1 ships when the record is correct, not when it is interesting.

## Finish criteria

1. `python -m pytest -q` green, including the promoted `tests/v3_correction/test_null_results.py`.
2. Every document that stated the two findings carries a dated, additive correction (CORR-01..07 checked off with commit SHAs in the phase summary).
3. `CLAUDE.md` null-result gate present; learning note written.
4. Codex review run and its findings dispositioned in `24-REVIEW.md`.
5. Vincent note drafted; send/hold decision recorded in `24-CONTEXT.md`'s decision log.


---

# Requirements: v4.0 Train Classically, Deploy Photonically (TCDP)

**Defined:** 2026-09-03 (queued behind v3.1; becomes the current milestone when v3.1 is closed)
**Core Value:** A working, end-to-end, honestly-benchmarked photonic project the owner can explain unaided. v4.0 asks the first question this repo's tooling can answer that nobody has published: how far does a classically trained IQP Born machine's photonic output drift from what the trainer deployed, and can the classical trainer absorb the device's gate noise without touching the device.
**Source plan:** [`docs/v4-plan-train-classical-deploy-photonic.md`](../docs/v4-plan-train-classical-deploy-photonic.md) — design table 5.1 and forbidden moves section 9 are binding on every phase below.

## Why this milestone exists

v3.1 established that loss alone does not change the post-selected output of this encoding (closed form, throughput pays). The open axes are partial distinguishability and multi-photon emission, which act inside the two-photon gates: a tomographed `CP(alpha)` gate has average fidelity 1.0 ideal and 0.9707 at indistinguishability 0.9 (probe 2026-09-03). The owner's spring-semester project (`iqp-mmd-barren-plateau`) trains IQP Born machines entirely classically; its theta convention equals this repo's exactly (verified 2026-09-03). Combining the two turns the photonic side into a deployment-fidelity study and, if noise-aware training closes the gap, a method result.

## v1 Requirements

All Must-have unless marked otherwise.

### Classical trainer, vendored (TRAIN)

- [ ] **TRAIN-01**: `merlin_iqp.classical` contains the sibling repo's numpy core (expectation, gaussian kernel, mixture cache, loss, analytic gradients, rng, initialization, trainer) with `PROVENANCE.md` recording the sibling commit hash and every removed jax/laplacian/polynomial path; `import merlin_iqp.classical` succeeds with jax absent.
- [ ] **TRAIN-02**: `families.chain_1d(n, k)` builds n weight-1 rows then the first k nearest-neighbour ZZ rows in that fixed order.
- [ ] **TRAIN-03**: `adapter.theta_to_repo` / `repo_to_theta` convert between generator-matrix theta and `(thetas, pair_thetas)` with no scaling or sign change, raising on weight-0/weight-3+ rows, duplicates, or a missing weight-1 row.
- [ ] **TRAIN-04**: `tests/v4_tcdp/test_convention.py` proves the Walsh-inverse of the sibling's exact `<Z_a>` equals `exact_qubit_iqp_distribution` to 1e-12 (n=2..4, k=0,1,n-1, 5 draws), that theta×0.5 and theta×2 fail, and that exact MMD² at n=10 runs in under 60 s.

### Noisy gate map (CHAN) — revised 2026-09-03 after the Codex plan review (method changed; plan § 4.1-4.3)

- [ ] **CHAN-01**: `deploy.gate_map.reconstruct_gate_map(alpha, V, g2)` reconstructs the **bare** catalog `PostProcessedControlledRotationsItem` gate (never the PERM-adapted core) as a **trace-decreasing completely positive map** by linear inversion from absolute post-selected Perceval probabilities (`results × global_perf`) over 16 product inputs × 9 readout-basis pairs, with prep states and readout POVMs derived from the circuits' own `compute_unitary()`, never hand-written; rank 256 and fit residual < 1e-12 asserted.
- [ ] **CHAN-02**: Ideal maps (V=1, g2=0) equal `(1/sigma_max(alpha)^4) · U ρ U†` to 1e-9 at alpha ∈ {π/6, π/3, π, 2.0} for random pure ρ, phase on |11⟩; every cached map is CP (Choi min eigenvalue > −1e-9), Hermiticity-preserving, and trace-non-increasing on all 16 matrix units; no map is ever renormalised per gate.
- [ ] **CHAN-03**: Input-dependence of success is recorded (at V=0.9, alpha=π/3 the basis successes differ by > 1e-4); two reconstructions of one key agree to 1e-13; Perceval `ProcessTomography` average fidelity agrees with the map's exact conditional average fidelity within 5e-3 at (1,0), (0.9,0), (0.93,0.007), discrepancy recorded.
- [ ] **CHAN-04**: Maps are cached under `results/v4_tcdp/channels/` keyed by `alpha_key(alpha)` (reduce mod 2π, round to 0.1 rad, wrap: exactly 63 keys, tested), V, g2; eta is not a key; `test_reconstruction_wall_clock` records seconds per map at the slowest condition (V=0.84, g2=0.025) into `results/v4_tcdp/map_timing.json` (measured 2026-09-03: 2.3 s, so 1134 maps ≈ 45 min); if 1134 × that exceeds 3 hours the executor stops.

### Deployment simulator (DEPLOY)

- [ ] **DEPLOY-01**: `deploy.density_matrix.deploy_density_matrix(n, thetas, pair_thetas, gate_maps)` evolves `|+⟩^n` as a `(2,)*2n` tensor: exact weight-1 phases, exact single-qubit corrections, one unnormalised gate map per ZZ pair in ascending pair order (raises unless `gate_maps[(i,j)].alpha == alpha_key(4·theta_pair)`), H^n, then **one** final normalisation; returns `(probs, p_success)` with `p_success` the composed trace; bit order equals `exact_qubit_iqp_distribution`; two-qubit maps applied by einsum, no `4^n × 4^n` matrix ever formed (tested by monkeypatch); peak RSS growth at n=10 under 400 MB.
- [ ] **DEPLOY-02**: With ideal maps the output equals `exact_qubit_iqp_distribution` to 1e-12 and `p_success` equals the product of `1/sigma_max^4` to 1e-9 (n=2..4, k=0,1,n-1); with k=0 noisy maps leave the output unchanged and `p_success = 1`; the hand-computed asymmetric n=3 fixture (thetas (0.3, 0, 0.9), pair (0,2) θ=0.4) matches by named bitstring. (Phase-level null result.)
- [ ] **DEPLOY-03**: `deploy.fock_reference.noisy_full_fock_distribution` runs the full dual-rail Perceval circuit under `NoiseModel` at n ≤ 3 with the exact mode map in plan § 4.5, returning normalised probs and the full-Fock success probability; `test_fock_crosscheck.py` shows TVD < 1e-9 **and** success-probability agreement to 1e-9 against `deploy_density_matrix` for one gate at n=2 (V ∈ {1, 0.9, 0.7} × g2 ∈ {0, 0.02}) and n=3 bystander, the latter run separately for V-only and g2-only noise; if g2-only fails while V-only passes, g2 is demoted to a flagged gate-local approximation and the executor stops to report both numbers.
- [ ] **DEPLOY-04**: The two-gate shared-qubit case (n=3, pairs (0,1),(1,2)) at (V,g2) ∈ {(0.9,0), (1,0.02), (0.93,0.007)} × theta_pair ∈ {π/12, 0.5} records every TVD and success discrepancy to `results/v4_tcdp/crosscheck_shared_qubit.json`; pre-registered bands: max TVD < 0.01 → error bar on every figure; 0.01–0.05 → full-Fock n=3 overlay on every figure and the discrepancy leads the write-up; > 0.05 → method fails, executor stops.
- [ ] **DEPLOY-05**: CP throughput is `1/(eta^n · p_success)` with `p_success` the composed trace; `deploy.throughput.heralded_cz_throughput(n, k, eta) = 1/(eta^(n+2k) · (2/27)^k)` exists for the Fig 4 overlay only; no function multiplies per-gate mean successes.
- [ ] **REFRAME-03**: `deploy.erasure.erasure_marked_distribution(q, n, eta, gates)` returns the non-post-selected output over `{0,1,E}^n` by the exact per-pattern formula in plan § 4.7 plus `dropped = 1 − eta^(n_gate)`; tested against hand-enumerated patterns for k=0 (n=2), one gate (n=3), and the shared-qubit case; mass + dropped = 1 to 1e-12; eta=1 reproduces `q`.

### Owner null results (NULL) — owner-only, written red before any sweep runs

- [ ] **NULL-03**: `owner_null_gap_k0(V, g2)` — predicted TVD(ideal, deployed) at k=0 for any V, g2 — filled by the owner and green.
- [ ] **NULL-04**: `owner_null_gap_noiseless(k)` — predicted gap at V=1, g2=0 for any k — filled and green.
- [ ] **NULL-05**: `owner_null_eta_effect(n, k, eta)` — predicted change in the conditional distribution from eta alone — filled and green.
- [ ] **NULL-06**: `owner_null_throughput_cp(n, alphas, eta)` and `owner_null_throughput_hcz(n, k, eta)` — both closed forms — filled and green.
- [ ] **NULL-07**: `owner_hypothesis_gap_scaling(k, F)` — the owner's first-order hypothesis for gap vs gate count, marked `xfail(strict=False)`; whether it held is a sentence in the write-up either way.
- [ ] **NULL-08**: `owner_null_nat_ideal()` — what noise-aware training does when every gate map is ideal (predicted before/after gap and the relation of the NAT-trained theta to the ideal-trained theta) — filled and green before Phase 30.
- [ ] **NULL-09** (pipeline null, may be written by Codex): `test_control_point_every_cell` asserts at (V,g2)=(1,0), for every trained cell, that every deployed metric equals its ideal counterpart (TVD = 0 to 1e-12; MMD², KL at both floors, coverage, fidelity, marginal errors equal; `mean_gate_fidelity = 1`; `p_success` equals the closed-form product), run inside `deploy_sweep.py` on the control rows and standalone on three cells; `test_control_point_can_fail` perturbs one entry by 1e-3 and every equality must fail.

### Deployment gap sweep (SWEEP)

- [ ] **SWEEP-01**: `scripts/v4_tcdp/train_classical.py` trains every cell of design table 5.1 (chain_1d; n ∈ {4,6,8,10} deployable, {16,20} training-only; k = 0..n-1; 1D Ising target seed 4001; sigma = 0.5√n primary and 1.0 control; three inits; Adam lr 0.05, 300 steps; 5 seeds) and writes deterministic `results/v4_tcdp/trained/{cell}.npz` with G, theta, trajectory, metadata, and q_ideal for n ≤ 10.
- [ ] **SWEEP-02**: `scripts/v4_tcdp/deploy_sweep.py --build-maps` precomputes all 1134 maps, then writes `results/v4_tcdp/deploy_sweep.csv` with exactly the column list in plan § 5.5, one row per (trained cell, V, g2): 840 cells × 18 = 15 120 rows, or a `missing_cells.md` naming each missing row; eta enters only as the four `throughput_eta*` columns; `alpha_trained_list`, `alpha_rounded_list`, `theta_eff_list`, `tvd_rounding_only`, and `rounding_flag` (10% of the noise gap) are mandatory columns; `--erasure` writes the erasure npz files for n ≤ 6; no tolerance, grid value, seed count, or formula is adjustable by the executor.
- [ ] **SWEEP-03**: Metrics are exactly the formulas in plan § 5.4 (`deploy/metrics.py`, each checked on a hand case in `test_metrics.py`): TVD; MMD² from the vectors with the training kernel's spectral weights; forward KL at floors 1e-12 and 1e-9; population coverage `(1/|S|) Σ_{x∈S} (1−(1−q(x))^Q)` and population fidelity `Σ_{x∈S} q(x)` with `S = {x: p(x) > 1e-6}`, `Q = 20000`, and the stated deviation from Raj et al.'s sample protocol; order-1 and order-2 marginal TVD; nothing else.
- [ ] **SWEEP-04**: `scripts/v4_tcdp/tcdp_analysis.py` regenerates Figures 1–4 and the summary table from the CSV with no manual edits, using the fixed aggregation (primary kernel, `data_dependent` init, mean ± std over 5 seeds; other combinations in an appendix table); the control line in Fig 1 is drawn and is zero; the headline is pre-registered on one cell (n=10, k=9, Ascella, median over seeds) with the two descriptive outcome bands of plan § 5.6; every number in the write-up traces to the CSV or a test.
- [ ] **SWEEP-05**: The write-up states, for each null in NULL-03..07, whether the sweep matched it, and identifies which of the two headline outcomes in plan section 5.6 occurred.

### Noise-aware classical training (NAT) — promoted from Should to Must on 2026-09-03 (owner decision after Fable's recommendation)

- [ ] **NAT-01**: `scripts/v4_tcdp/nat_train.py` optimizes theta against `mmd2_train(q_dep(theta))` with `q_dep` from `deploy_density_matrix` (theta_eff inside), warm-started from the Phase-29 ideal-trained theta, Adam lr 0.02, 150 steps, central finite differences h = 1e-4 on the exact deployed vector (parameter-shift is not valid for a channel; the piecewise objective from alpha rounding is accepted and stated); all 63 Ascella-point maps are precomputed before the first step.
- [ ] **NAT-02**: At n ∈ {4, 6, 8}, k = n−1, primary kernel, `data_dependent` init, the 5 Phase-29 seeds, Ascella noise (V=0.93, g2=0.007): all six metrics of `q_dep(theta_NAT)` reported next to `q_dep(theta_ideal-trained)` and `q_ideal(theta_ideal-trained)`; NULL-08 run first with ideal maps and its prediction confirmed; the cost budget (29 250 evaluations × the per-call time measured in Phase 27) recorded before the run.
- [ ] **NAT-03**: Stop rule enforced and recorded: if one n=8 run exceeds 20 minutes, or two calendar days pass without a green end-to-end n=4 run, timing is written to `PROJECT.md` and NAT ships as "attempted, stopped" with the numbers obtained; the milestone still closes.

### Write-up, gates, communication (WRITE / REVIEW / COMM)

- [ ] **WRITE-07**: Owner self-explanation checkpoint recorded before any prose: theta needs no conversion; why the channel model is exact for one gate and approximate for two gates on a shared qubit, with the measured number; why k=0 is a null for distinguishability but not loss; what changes in throughput between CP and heralded CZ. Hedging stops the phase.
- [ ] **WRITE-08**: `docs/tcdp-study.md` with question, design table, null outcomes, figures, shared-qubit approximation number, hardware anchors (Ascella V 0.930 / g2 7.3e-3 / ~8% transmission; Altair V 0.84 / purity 0.025; roadmap 70% → 99%), "what this does/doesn't establish", literature table with read-depth labels (full reads: arXiv:2503.02934, 2608.31117, 2405.02277, 2605.11879).
- [ ] **WRITE-09**: `docs/technical-findings.md` gains a v4.0 section, README gains a v4.0 paragraph, `CLAUDE.md` Repo state updated; no sentence states "barren plateau" as a finding.
- [ ] **REVIEW-02**: A Fable/Opus review then a Codex adversarial review with the verbatim prompt "For each stated finding, write the null result and check whether the finding differs from it. Then check every number against deploy_sweep.csv"; findings dispositioned in the phase's REVIEW.md.
- [ ] **COMM-02**: Gibbs pass offered (questions only), journal entry in the owner's words, Vincent note (3–5 sentences, owner's words) drafted with send/hold recorded.

## Out of Scope

| Feature | Reason |
|---|---|
| Structured Fock-space simulator to n≈20 | The channel approach answers this milestone's question without it |
| Any barren-plateau claim or Hamming-kernel gradient-variance rerun | Sibling project already found init and n dominate; not this milestone's question |
| Graph-state / MBQC realization of IQP (audit direction 4) | Separate, larger milestone; does not reuse the spring trainer |
| Heralded CZ under distinguishability | CP(alpha) is the validated tunable gate and the cheaper one under loss |
| Recycling mitigation (Salavrakos et al.) | Threshold-detector, different circuit class; cite only |
| New dependencies (jax, iqpopt, pennylane, torch training) | Numpy core suffices; adding any is a stop-and-ask |
| Analysis of the erasure-marked output (REFRAME-03's consumer) | Audit direction 1, future milestone |

## Traceability

| Requirement | Phase | Status |
|---|---|---|
| TRAIN-01..04 | Phase 25 | Pending |
| CHAN-01..04 | Phase 26 | Pending |
| DEPLOY-01..05, REFRAME-03 | Phase 27 | Pending |
| NULL-03..09 | Phase 28 | Pending (owner; NULL-09 pipeline) |
| SWEEP-01..05 | Phase 29 | Pending |
| NAT-01..03 | Phase 30 | Pending |
| WRITE-07..09, REVIEW-02, COMM-02 | Phase 31 | Pending |

**Coverage:** v1 requirements: 32 total; mapped: 32; unmapped: 0.

---
*v4.0 requirements defined: 2026-09-03, from `docs/v4-plan-train-classical-deploy-photonic.md`; owner promoted NAT to Must the same day; revised the same day after the Codex adversarial plan review (`.planning/research/v4-plan-codex-review-disposition.md`): gate maps are reconstructed trace-decreasing CP maps composed unnormalised, not renormalised tomography channels.*
