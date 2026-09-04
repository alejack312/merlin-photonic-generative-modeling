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
- [x] **REFRAME-02** *(Should)*: `photonic_iqp_distribution_lossy` and `photonic_weight2_iqp_distribution_lossy` additionally return the non-post-selected outcome distribution (partial-loss patterns kept as their own keys, not collapsed into `residual`), with a test that its total mass plus the in-subspace mass equals `global_perf`-consistent totals. No analysis of it in this milestone — this only stops discarding the data. **Done 2026-09-03** (quick task 260903-ukn): `partial_loss` dict appended to both functions' return tuples, herald-renormalized identically to `residual` for weight-2; `sum(partial_loss.values()) == residual` and mass-total tests added in `tests/hardness/test_loss_model.py`/`test_loss_model_weight2.py`; all callers (including two found only during planning: `julia/generate_reference.py`, a monkeypatch stub in `tests/scripts/v3_hardness/test_merlin_loss_model.py`) updated; 451/451 tests pass.

### Process gate (GATE)

- [ ] **GATE-01**: `CLAUDE.md` gains a "Null-result gate" rule: before any sweep or measurement phase, the owner writes the closed-form prediction for what the pipeline outputs if the circuit contributes nothing, as a test; a measurement matching the null is a pipeline check, not a finding. Recorded in `.claude/learnings/`.
- [ ] **REVIEW-01**: Before CORR-04/CORR-07 ship, an independent Codex (`gpt-5.5`) review of the corrected docs is run with the explicit prompt "for each stated finding, write the null result and check whether the finding differs from it". Findings addressed or explicitly declined in the phase summary.

### Communication (COMM)

- [x] **COMM-01**: A correction note to Vincent Espitalier is drafted by the owner (three to five sentences: what was wrong, what each result actually shows, link to the corrected repo). Whether and when to send is the owner's call and is recorded as a decision either way; the draft exists regardless, because the public case study and repo already carry the claims. **Done 2026-09-04:** owner drafted and sent the note directly (outside this repo/session). Send/hold decision recorded in `24-CONTEXT.md`'s decision log as "sent." The accuracy check D-03 assigns to Claude (checking the draft against the corrected docs before sending) did not happen, since the draft wasn't routed through this session.

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
