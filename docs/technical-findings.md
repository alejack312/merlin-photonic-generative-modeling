# Technical Findings — Synthesis (Phase 20)

This is the project's synthesis document for the v3.0 milestone's three
research questions: trainability (STUDY-01, Phase 17/17.1), hardness under
photon loss (STUDY-02, Phase 18), and the tunable weight-2 gate's
correctness (ARB-01/ARB-02, Phases 15-16). It organizes and
cross-references findings that are already published and already verified
in [`docs/trainability-study.md`](trainability-study.md),
[`docs/hardness-under-loss-study.md`](hardness-under-loss-study.md), and
[`docs/iqp-photonic-encoding.md`](iqp-photonic-encoding.md) — it does not
introduce new numbers, re-run any analysis, or re-derive any of the
reasoning those three documents already contain. Every table below is
mirrored from its source document; every claim is traceable to the same
script/CSV/test its source document already cites. Per `20-CONTEXT.md`'s
locked scope, this is an internal/candid technical document — external-facing
reframing is Phase 21's separate job, not pulled forward here.

## Trainability (STUDY-01, TRAIN-01..10)

**Methodology summary.** Gradients are computed by exact parameter-shift
(`shift = pi/4`, undivided) directly on the photonic circuit functions, not
MerLin `QuantumLayer` autograd (structurally unavailable for this project's
polarization-annotated circuits). Two generator scopes were swept
(`weight1`: n=2-6; `mixed`: weight1 + one fixed weight-2 pair, n=2-5), each
under two initialization schemes (`small_angle`: `theta ~ Uniform(-0.1,0.1)`;
`uniform`: `theta ~ Uniform(0,2*pi)`). The loss whose gradient is measured
is exact MMD² against a fresh `2^n`-bin target grid, computed via closed
form (no Monte Carlo). Full methodology:
[`docs/trainability-study.md#methodology`](trainability-study.md#methodology).

**Headline results.**

| generator_scope | init_scheme | n range | winning model | exp R² |
|---|---|---|---|---|
| weight1 | uniform | 2–6 | exp | 0.999 |
| mixed | uniform | 2–5 | exp | 0.910 |
| weight1 | small_angle | 2–6 | inconclusive | 0.543 |
| mixed | small_angle | 2–5 | inconclusive | 0.000 |

At Phase 17's original fixed bandwidth (`SIGMA=0.1`), both `uniform`-init
cells show a statistically clear exponential-decay signature in
gradient-variance-vs-n (an exponential model beats a polynomial one on
AIC). **TRAIN-09's bandwidth-sensitivity follow-up found this signature is
NOT robust**: re-run across a six-point sigma grid `{0.03, 0.1, 0.3, 1.0,
3.0, 9.0}`, both `uniform` cells survive only near the original bandwidth
(sigma in {0.03, 0.1}) and flip to "inconclusive" at intermediate sigma
(0.3, 1.0); `weight1/uniform` then non-monotonically re-emerges as "exp" at
high sigma (3.0, 9.0) while `mixed/uniform` stays inconclusive through
sigma=9.0. **TRAIN-10's data-dependent-init follow-up found that
Recio-Armengol et al.'s literature-sourced alternative initialization did
NOT resolve `small_angle`'s inconclusive verdict** in either generator
scope — a genuine negative result, reported here exactly as measured.

**TRAIN-07 cross-reference verdict — owner's interpretation (transcribed,
not re-authored).** `docs/iqp-baseline.md`'s empirical plateau rule
(`plateau if small_angle OR (uniform AND n>=6 AND not complete_graph_like)`)
agrees with the measured data for `weight1/uniform` (rule predicts plateau
at n_max=6>=6; measured shows exponential decay) but disagrees for
`mixed/uniform` (rule predicts no-plateau since n_max=5<6; measured data
shows exponential decay anyway). The owner's own unaided reasoning, in
full, is recorded in
[`docs/trainability-study.md`'s Cross-reference verdict (TRAIN-07)
section](trainability-study.md#cross-reference-verdict-train-07): the
owner first hypothesized a `complete_graph_like` explanation, ruled it out
by re-reading the rule's own structure, reviewed the raw fitted parameters
and per-n gradient-variance values, asked what the literature (as opposed
to the sibling project's own fitted threshold) actually claims, and — after
an initial overreaching framing was pushed back on — landed on the final
interpretation: the sibling project's specific `n>=6` numeric threshold
didn't hold for `mixed/uniform`, but this is not in tension with the general
literature's asymptotic (non-threshold-specific) prediction that uniform
init drives exponential concentration as n grows (Recio-Armengol et al.,
arXiv:2503.02934, Sec. 9.3) — only with the sibling project's own
qubit-side-specific fitted cutoff. `weight1/uniform`'s agreement with that
cutoff may be coincidental rather than evidence the threshold transfers
mechanistically to this photonic circuit family.

**Randomness / seed mechanism (WRITE-06).** TRAIN's randomness uses a
deterministic, reorder-safe hashed-seed scheme
(`trainability/rng.py::derive_seed`), not a single global seed constant —
each `(n, generator_scope, init_scheme, draw_index)` coordinate gets its
own reproducible seed, so results are exactly reproducible without needing
one literal number quoted here. This is architecturally different from
HARD's single literal `seed_base` (below), and is stated as-is rather than
forced into parity with HARD's style — see Part C of this synthesis
document's own drafting process for why (a single fabricated seed number
would misrepresent TRAIN's actual, more robust per-coordinate design).

**Scope statement.** Full scope — what this measurement does and does not
establish, including the honest caveat that a measured exponential-decay
signature at n<=6 does not, by itself, establish this photonic realization
inherits the qubit-side rule's behavior at hardware-relevant scale — is in
[`docs/trainability-study.md#what-this-doesdoesnt-establish`](trainability-study.md#what-this-doesdoesnt-establish).

### Trainability literature comparison table (mirrored from `docs/trainability-study.md`)

Full reasoning and citations: see
[`docs/trainability-study.md`'s "Literature comparison table
(WRITE-02)"](trainability-study.md#literature-comparison-table-write-02).
Six baselines get a substantive verdict; five are HARD-/ARB-specific and
are silent here, per that document's own scoping decision.

| Baseline | Verdict |
|---|---|
| McClean et al. (arXiv:1803.11173) | Consistent with the well-known protocol shape (confirmed live via arXiv API, lower confidence tier than fully-PDF-read baselines) |
| `docs/iqp-baseline.md`'s own empirical rule | Split — agrees for `weight1/uniform`, disagrees for `mixed/uniform` (see TRAIN-07 above) |
| Rudolph et al. (arXiv:2305.02881, Thm. 2) | Directionally consistent with TRAIN-09's bandwidth-sensitivity finding; mechanism (Hamming-distance kernel) does not directly transfer to this project's Euclidean-distance kernel |
| Mhiri et al. (arXiv:2502.07889) | Consistent — commuting/structured-circuit risk case matches both inconclusive `small_angle` rows |
| Recio-Armengol et al. (arXiv:2503.02934) | Consistent for the uniform-init exponential-concentration finding (Sec. 9.3); their proposed data-dependent-init fix (Sec. 8.1.2) tested as TRAIN-10 and found NOT to resolve `small_angle`'s inconclusive verdict — genuine negative result |
| Herbst et al. (arXiv:2512.24801) | See Herbst cross-thread section below |
| Aaronson-Brod, Park & Oh, arXiv:2405.01395, BMS 2015, BMS 2017 | Silent — HARD-/ARB-specific, no trainability claim |

## Hardness under loss (STUDY-02, HARD-01..07)

**Methodology summary.** Photon loss is applied via `pcvl.LC(1-eta)`
component insertion, front-loaded before the rest of the circuit, with an
explicit `proc.min_detected_photons_filter(0)` call — never
`noise=NoiseModel(...)`, which silently no-ops on this project's
polarization-annotated circuits. A fixed 7-point eta grid
(`[0.99, 0.95, 0.90, 0.80, 0.60, 0.35, 0.05]`) is swept for both generator
scopes (weight1: n=2-6; mixed weight-1+weight-2: n=2-4), 5 draws/cell,
`theta ~ Uniform(0,2*pi)`. Two classically-easy baselines
(`uniform`, `product_of_marginals`) are tracked separately, never collapsed
into a single crossover threshold, per `18-CONTEXT.md`'s explicit lock.
Full methodology:
[`docs/hardness-under-loss-study.md#methodology`](hardness-under-loss-study.md#methodology).

**Headline results.** For every n and both scopes, `tvd_to_lossless` rises
monotonically as eta decreases (from ~0.01-0.03 at the near-lossless anchor
eta=0.99 to ~0.50 at eta=0.05), while `tvd_to_uniform` and
`tvd_to_product_marginals` fall over the same range, converging with
`tvd_to_lossless` near ~0.50 by eta=0.05. Anticoncentration
`alpha(eta) = 2^n * sum(p_x^2)` decreases monotonically as eta decreases for
both scopes, crossing below the `alpha=1` uniform-reference line somewhere
in the measured grid at every n — i.e., **photon loss makes this project's
own circuits MORE anticoncentrated, not less.** For the weight-2 (mixed)
scope, loss is applied to all `2n+2` modes including both `heralded_cz`
ancilla modes, and herald-success rate is measured through one real
`Processor.probs()` call per cell: `herald_failure_prob` rises
monotonically from the near-lossless anchor value (~0.926, matching the
lossless `2/27` baseline) to 0.999 at eta=0.05 — loss compounds with the
gate's own intrinsic herald-failure rate rather than leaving it unchanged.

**HARD-04's positioning.** By the owner's explicit decision, no eta-to-epsilon
(photon-loss-to-depolarizing-rate) translation was attempted — this was a
deliberate scope call (computing one, e.g. via a diamond-norm-closest-
depolarizing-channel calculation, would be original numerics work outside
this project's stated scope), not a fallback after a failed attempt. The
full owner's attempt-first response, including the three candidate
translation directions considered and why none was picked, is recorded in
[`docs/hardness-under-loss-study.md`'s "HARD-04/HARD-06: Positioning and
Scope Statement" section](hardness-under-loss-study.md#hard-04hard-06-positioning-and-scope-statement-plan-18-08)
(the "Owner's attempt-first response" subsection at its start) and is not
restated here. Instead, this project's tested eta range is
positioned against two loss-native regimes that avoid the translation
question entirely: Aaronson-Brod's fixed-loss-count regime (structural
regime mismatch — this project's fixed-eta/growing-n sweep sits in AB's own
"insufficient for strong complexity claims" fractional-loss regime) and
arXiv:2511.07853's logarithmic-loss-fraction threshold (a computed,
illustrative crossover: this project's four highest-eta points sit inside
the "at most log(N) lost" regime at each scope's largest reached n; the
three lowest do not — reported as a small-n-limited structural observation,
not an asymptotic or hardness claim).

**Scope statement.** Full scope — what HARD-01 through HARD-07 do and do
not establish, including the explicit statement that this is not a
complexity-theoretic proof and does not demonstrate an asymptotic
transition — is in
[`docs/hardness-under-loss-study.md#hard-06-what-this-phase-does-and-does-not-establish`](hardness-under-loss-study.md#hard-06-what-this-phase-does-and-does-not-establish).

### Hardness literature comparison table (mirrored from `docs/hardness-under-loss-study.md`)

Full reasoning and citations: see
[`docs/hardness-under-loss-study.md`'s "Literature comparison table
(WRITE-02)"](hardness-under-loss-study.md#literature-comparison-table-write-02).
Five baselines get a substantive verdict; six are TRAIN-/ARB-specific and
are silent here.

| # | Baseline | Verdict |
|---|---|---|
| 1 | Aaronson-Brod (arXiv:1510.05245, Thm. 1) | Silent — regime mismatch (this project's fractional-rate sweep sits in AB's own "insufficient for strong complexity claims" regime) |
| 2 | arXiv:2510.24137 (Park & Oh), Thm. 1 | Silent — structural match (closest physical model to `pcvl.LC(1-eta)`) but no testable hardness claim (Thm. 1 bounds one classical algorithm's efficiency, not a lower bound) |
| 3 | BMS 2017 (arXiv:1610.01808, Thm. 4) | Silent by owner decision — no eta-to-epsilon translation exists or was derived |
| 4 | BMS 2015 (arXiv:1504.07999, Thm. 1) | Silent — background/lineage only, makes no noise/loss claim of its own |
| 5 | Herbst et al. (arXiv:2512.24801) | **Inconsistent** — see Herbst cross-thread section below |
| 6-11 | McClean et al., arXiv:2405.01395, `iqp-baseline.md`'s empirical rule, Rudolph et al., Mhiri et al., Recio-Armengol et al. | Silent — TRAIN-specific, no loss/hardness claim |

## ARB-01/ARB-02 (tunable weight-2 gate, ARB-01..09)

**Methodology summary.** `PostProcessedControlledRotationsItem`
implements a continuously-tunable `CP(alpha) = diag(1,1,1,e^{i*alpha})`, a
genuinely different gate family from the fixed-angle `heralded_cz`
(post-selection on ancilla vacuum + per-qubit data validity, not ancilla
heralding). The general operator identity `exp(i*theta*Z_i*Z_j) =
e^{-i*theta} * CP(4*theta) * exp(i*theta*Z_i) * exp(i*theta*Z_j)` connects
`CP(alpha)` to IQP's generic weight-2 generator for arbitrary theta
(`alpha = 4*theta`); the closed-form success probability
`p_success(alpha) = 1/sigma_max(alpha)^(2n)` (n=2: `1/sigma_max^4`) was
derived from the gate's own primary source (arXiv:2405.01395, Sec. V-B)
and confirmed against measurement to ~1e-7.

**Headline results.** A 16-point `alpha` sweep spanning `[0, 2*pi)`
matches the closed-form success probability to within 1e-6 at every point
(Phase 16, ARB-08). Full-pipeline TVD validation is at floating-point-noise
level (~1e-16 to 1e-15) against the exact reference for `n=2,3` across
multiple non-trivial `alpha` values, plus a direct boundary-agreement
confirmation against `heralded_cz`'s own full pipeline at `alpha=pi`
(Phase 15). `n=3` mixed weight-1 + arbitrary-theta weight-2 composability
passed with TVD < 1e-6 (Phase 16, ARB-07). A Forge-based formal check
confirmed the gate's ancilla mode-mapping dict is injective/non-aliasing
for all valid `(n,i,j)`, `n<=8`, with no bug found (Phase 16, ARB-09).

**Scope statement.** Full scope — what ARB-01/ARB-02 do and do not
establish, including the explicit statement that this is not a hardness or
trainability claim, and that ARB-01/ARB-02's `CP(alpha)` and HARD-01..07's
`heralded_cz` are two different weight-2 gate families never cross-tested
under loss together — is in
[`docs/iqp-photonic-encoding.md`'s "What ARB-01/ARB-02 does/doesn't
establish" subsection](iqp-photonic-encoding.md#what-arb-01arb-02-doesdoesnt-establish).

### ARB-01/ARB-02 literature comparison table (mirrored from `docs/iqp-photonic-encoding.md`)

Full reasoning and citations: see
[`docs/iqp-photonic-encoding.md`'s "Literature comparison table
(WRITE-02)"](iqp-photonic-encoding.md#what-arb-01arb-02-doesdoesnt-establish).
Only one of the 11 named WRITE-02 baselines bears directly on ARB-01/ARB-02's
actual subject (gate construction, success probability, postselection
mechanics); the other 10 are trainability and/or hardness-under-noise
papers that make no claim about this section's subject, and are addressed
in prose rather than padded into table rows — see the source document for
the full list.

| Baseline | Verdict |
|---|---|
| arXiv:2405.01395 ("Simple rules for two-photon state preparation with linear optics"), Sec. V-B | **Consistent** — primary source of `PostProcessedControlledRotationsItem`'s own construction; its closed-form success-probability formula independently verified against this project's measured amplitudes to ~1e-7 |

## Trainability and hardness: are they connected?

Herbst, Brandic & Perez-Salinas (arXiv:2512.24801) predict that circuits
whose output distributions anticoncentrate should show BOTH increased
classical-simulability-under-noise (the hardness side) AND increased
MMD-type-loss concentration (the trainability side) — the two effects
predicted to co-occur, not trade off. This project's own headline: **TRAIN's
zero-loss data shows a genuine (if bandwidth-fragile) untrainability
signature for `uniform` init; HARD's data shows anticoncentration
INCREASING (not decreasing) as loss increases** — the reverse of
`docs/iqp-baseline.md`'s original 2026-08-12 speculative guess about which
direction Phase 18 would find. Under Herbst et al.'s framework, this means
training should, if anything, get worse (not better) as loss increases —
opposite the original speculative conclusion.

TRAIN and HARD do not share a common independent variable — TRAIN sweeps
`n` at fixed `eta=1`; HARD sweeps `eta` at small fixed `n` — so this project
cannot directly test the co-occurrence prediction with one combined
experiment. The full reasoning for each half, including this hedge, is
recorded in the two source docs' own cross-reference notes, not re-derived
here:
[`docs/trainability-study.md`'s Herbst cross-reference note](trainability-study.md#cross-reference-herbst-et-als-anticoncentration-tradeoff-prediction)
and
[`docs/hardness-under-loss-study.md`'s Herbst cross-reference note](hardness-under-loss-study.md#cross-reference-herbst-et-als-anticoncentration-tradeoff-prediction).

## Independent verification

[`docs/julia-cross-check-study.md`](julia-cross-check-study.md)
independently cross-checked the underlying exact and lossy distributions
this project's TRAIN/HARD/ARB findings are built on, via a separate
toolchain (Yao.jl for the qubit-side circuit; BosonSampling.jl for the
weight-1 and weight-2 photonic-level circuits; BosonSampling.jl's native
loss API for the loss model) — never a mechanical port of this project's
Python/Perceval code, but circuits built from each library's own native
primitives and idioms. All four legs (VERIFY-02 qubit-side, VERIFY-03
weight-1, VERIFY-03 weight-2, VERIFY-04 loss model) reached a genuine GO
verdict. This is supplementary evidence only, per `20-CONTEXT.md`'s
explicit lock — its own numbers are not restated here and it is not forced
into the TRAIN/HARD/ARB structure above; see the document itself for the
full per-leg results.

## What this project does not establish, at the milestone level

- **No complexity-theoretic proof.** Neither the hardness-under-loss study
  nor the IQP-photonic mapping constitutes a formal reduction or
  complexity-theoretic hardness proof — this is explicitly excluded from
  this milestone's scope (`.planning/REQUIREMENTS.md`'s Out-of-Scope
  table), and both source documents state this limitation directly at the
  point where overclaiming risk is highest.
- **No asymptotic-scale demonstration.** All three studies operate at
  small, compute-bound n (TRAIN: n<=6 CORE, n<=8 via the supplementary
  dual-rail/autograd cross-check; HARD: weight1 n<=6, mixed n<=4; ARB:
  n=2-3). None of this demonstrates scaling behavior at hardware-relevant n
  — see each source document's own honest max-n statement for the specific
  compute-cost reasoning.
- **Two different weight-2 gate families, never cross-tested under loss
  together.** ARB-01/ARB-02 (Phases 15-16) and HARD-01..07 (Phase 18) use
  genuinely different weight-2 gate constructions: `heralded_cz`
  (ancilla-heralding, fixed angle `theta=pi/4`) is what HARD-01..07's
  photon-loss sweep was built and tested against; `CP(alpha)`
  (post-selection-based, continuously tunable) is what ARB-01/ARB-02
  validated for correctness. Neither study's result transfers to the
  other's gate family without separate validation — this is stated
  explicitly here because it is easy to conflate the two constructions
  when reading this synthesis document in isolation from its three source
  documents.
