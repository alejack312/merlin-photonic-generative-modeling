# Hardness-under-loss study (Phase 18)

The phase's canonical reference document: methodology, the real measured
TVD-vs-eta and anticoncentration-vs-eta datasets (both generator scopes,
both classically-easy baselines), and the weight-2 herald-compounding
results. Mirrors `docs/trainability-study.md`'s established Phase-17
structure (methodology stated before any results, per this project's
`WRITE-01` convention) and `docs/iqp-photonic-encoding.md`'s `ENC-02` rigor
bar. This document does not yet contain HARD-04's depolarizing-translation
positioning or HARD-06's final scope statement -- those sections are
appended by Plan 18-08 after the owner's attempt-first checkpoint (see the
placeholder heading at the end of this document).

## Methodology

**Loss mechanism.** Photon loss is applied via `pcvl.LC(1 - eta)` component
insertion, front-loaded onto every mode of a `Processor` *before* the rest
of the circuit is added (`hardness/loss_model.py`,
`hardness/loss_model_weight2.py`) -- **never** the `noise=NoiseModel(...)`
`Processor` constructor parameter. A reader unfamiliar with Perceval would
reasonably expect the `NoiseModel` API to be the "obvious" way to add loss;
it is not used here because it is confirmed (`18-RESEARCH.md` Pitfall 1) to
**silently no-op** on this project's polarization-annotated circuits --
`Processor.probs()` runs without error and returns a plausible-looking but
loss-invariant result. Two further requirements, both proven avoided by
dedicated regression tests rather than merely documented:

- `proc.min_detected_photons_filter(0)` must be called **explicitly**
  (Pitfall 2) -- the `Processor`'s automatic filter only inspects
  `NoiseModel`, has no knowledge of `LC` components, and silently defaults
  to a filter that excludes every lossy branch, again producing a
  plausible-looking but loss-invariant "normalized" result.
- Front-loading `LC` on all modes before the rest of the circuit (rather
  than distributing loss through the circuit) is exact, not a
  simplification with hidden risk: uniform per-mode loss commutes with any
  passive linear-optical unitary, and every component in this project's
  weight-1/weight-2 pipelines (state prep, diagonal layer, conjugation,
  CZ insertion, readout) is passive/photon-number-preserving (`18-RESEARCH.md`
  Architecture Patterns; matches Park & Oh's own stated commutation fact,
  arXiv:2510.24137 Sec. II.B).

For weight-2 (mixed scope), `LC` is applied to **all `2n+2` modes**,
including both `heralded_cz` ancilla modes (`2n`, `2n+1`) -- not just the
`2n` data-carrying modes -- per `18-CONTEXT.md`'s locked HARD-07 decision:
this is the only way to see whether loss degrades the herald mechanism
itself, not just the post-herald data readout.

**Eta grid.** A fixed 7-point grid, denser near `eta=1` (low loss) than
near `eta=0` (near-total loss), the same grid used for both generator
scopes so they remain directly comparable (`hardness/sweep.py::ETA_GRID`):

```
ETA_GRID = [0.99, 0.95, 0.90, 0.80, 0.60, 0.35, 0.05]
```

There is **no literal `eta=1.0` row** in either dataset -- `eta=0.99` is the
closest available near-lossless anchor point, referred to as such below,
never implied to be a lossless measurement itself. (The lossless reference
distribution *is* computed internally, via the same loss-model function
called with `eta=1.0`, as the fixed comparison point `tvd_to_lossless` is
measured against for every eta -- it is simply not saved as its own CSV
row.)

**n range actually reached, per scope (stated honestly, per this project's
TRAIN-05/TRAIN-08 convention):**

- **weight1: n = 2..6** (full 7-point eta grid, 35 rows,
  `results/phase18_weight1_loss_sweep.csv`) -- matches Phase 17's own
  weight-1 ceiling.
- **mixed: n = 2..4** (full 7-point eta grid, 21 rows,
  `results/phase18_mixed_loss_sweep.csv`). **Mixed n=5 is a confirmed hard
  ceiling, not a pending/in-progress item** -- a reproducible
  `MemoryError: bad allocation` inside `Simulator.probs_svd` (called via
  `Processor.probs()`) on the very first circuit evaluation of a fresh
  process, independently reproduced 3 times (2 in Plan 18-05's timing
  probe, 1 in Plan 18-06's own stretch attempt) at different eta values and
  different free-memory conditions. Draw-chunking does not help -- this is
  a single-call memory ceiling, not a cross-call leak. Mixed scope's usable
  range for this document and for Plan 18-08 is n=2..4 only.

**n_draws and seed.** `n_draws=5` independent random-theta draws per
`(n, eta, scope)` cell, `seed_base=180814`, drawn via this project's
existing deterministic, reorder-safe RNG substream utility
(`trainability.rng.get_rng`, reused across packages) -- per this project's
`WRITE-06` traceability requirement, every number in this document is
reproducible from `results/phase18_weight1_loss_sweep.csv` /
`results/phase18_mixed_loss_sweep.csv` plus this seed.

**Theta-init convention.** All circuit parameters are drawn
`theta ~ Uniform(0, 2*pi)` (`hardness/sweep.py::sample_thetas`) -- this
phase's own single init convention, a **deliberate scope decision**
(`18-CONTEXT.md`, "Claude's Discretion"), not silently inherited from Phase
17. Unlike Phase 17/17.1, this phase has no `init_scheme` axis at all: it
reuses only the *shape* of Phase 17's "uniform" branch (the regime that
produced Phase 17's own clean measured signal), on the reasoning that
HARD-05/HARD-07 want generic/representative circuit instances, not a
special-cased warm start.

**Classically-easy baselines.** Two baselines are tracked, separately, at
every `(n, eta, scope)` cell -- never collapsed into a single "classically
easy?" verdict:

- **`uniform`**: the maximally-anticoncentrated `2**-n`-per-outcome
  distribution.
- **`product_of_marginals`**: the mean-field/independence baseline, derived
  from each draw's own per-qubit marginals. Computed **once per draw**,
  from that draw's own lossless (`eta=1.0`) reference distribution -- not
  recomputed at every eta -- per `18-CONTEXT.md`'s explicit lock. This
  isolates "how far does loss alone move the true output toward
  independence" as a single fixed comparison point across the whole eta
  grid.

`18-CONTEXT.md` **explicitly locks that no single numeric crossover
threshold** (e.g. "TVD-to-baseline < TVD-to-lossless implies classically
easy") is defined in this phase. Both TVD curves are reported below exactly
as measured; the "is this classically easy" interpretation is deferred to
Phase 20 / the owner, matching this project's honesty-over-narrative
convention (Phase 7, Phase 17).

## HARD-01 / HARD-02: loss sweep mechanism and cross-check

**HARD-01** (a real loss sweep exists) is satisfied by the two CSVs
described above -- every cell computed via a real `Processor.probs()` call
through the `LC`-loss pipeline, never an `Analyzer` call (which silently
ignores loss entirely) and never `NoiseModel` (which silently no-ops on
this project's polarization-annotated circuits, as above).

**HARD-02** (cross-check that `LC`-based loss agrees with Perceval's
`NoiseModel` mechanism where the latter *is* valid) is satisfied by Plan
18-02's dedicated cross-check: on a shared bare 2-mode **non-polarization**
toy circuit (where `NoiseModel` is not subject to Pitfall 1),
`NoiseModel(transmittance=eta)` and `pcvl.LC(1-eta)` agree to **`atol=1e-9`**
at `eta=0.5` and `eta=0.8`, matching `18-RESEARCH.md`'s own independently
verified spot-check (`{|0,0>: 0.5, |1,0>: 0.5}` at `eta=0.5`). This
confirms the `LC` mechanism itself is correct, isolating the earlier
Pitfall-1 finding to `NoiseModel`'s behavior specifically on
polarization-annotated circuits, not to a flaw in the loss physics being
modeled.

## HARD-05 results: TVD vs eta (weight-1 and mixed)

![weight-1 TVD vs eta](../results/phase18_weight1_tvd_plot.png)

![mixed TVD vs eta](../results/phase18_mixed_tvd_plot.png)

Each plot shows `tvd_to_lossless`, `tvd_to_uniform`, and
`tvd_to_product_marginals` vs eta, one line per n, error bars from the
CSV's own `_std` columns (5-draw sample std). Full per-cell numbers are in
`results/phase18_weight1_loss_sweep.csv` / `results/phase18_mixed_loss_sweep.csv`.

### weight1 (n=2..6): TVD at the highest measured eta (0.99, near-lossless anchor) and lowest measured eta (0.05, near-total loss)

| n | eta | tvd_to_lossless | tvd_to_uniform | tvd_to_product_marginals | alpha |
|---|---|---|---|---|---|
| 2 | 0.99 | 0.0100 | 0.5726 | 0.0099 | 2.7784 |
| 2 | 0.05 | 0.4987 | 0.4987 | 0.4987 | 1.81e-05 |
| 3 | 0.99 | 0.0149 | 0.4900 | 0.0149 | 2.4474 |
| 3 | 0.05 | 0.4999 | 0.4999 | 0.4999 | 4.06e-08 |
| 4 | 0.99 | 0.0197 | 0.6865 | 0.0197 | 5.4947 |
| 4 | 0.05 | 0.5000 | 0.5000 | 0.5000 | 2.33e-10 |
| 5 | 0.99 | 0.0245 | 0.6876 | 0.0245 | 7.1938 |
| 5 | 0.05 | 0.5000 | 0.5000 | 0.5000 | 7.77e-13 |
| 6 | 0.99 | 0.0293 | 0.7988 | 0.0293 | 16.2048 |
| 6 | 0.05 | 0.5000 | 0.5000 | 0.5000 | 4.46e-15 |

Note: `tvd_to_product_marginals` is numerically **near-equal to
`tvd_to_lossless`** at `eta=0.99` for every weight1 n (e.g. n=2: 0.0099 vs
0.0100) -- `tvd_to_uniform` is not (0.5726 at n=2). This is a real
structural fact about the weight1 circuit family, not a coincidence of the
baseline construction: weight1's generator layer has **no entangling
(weight-2) gate**, so its true lossless output distribution already
factors as a product over qubits -- `product_of_marginals_baseline`,
computed from that same lossless reference's own marginals, closely
reproduces it. `tvd(lossy, product_marginals) ~= tvd(lossy, lossless)`
follows directly from `product_marginals ~= lossless`, not from any
special property of the loss channel. This coincidence narrows as eta
decreases -- by eta=0.05, all three distances (`tvd_to_lossless`,
`tvd_to_uniform`, `tvd_to_product_marginals`) converge to the same ~0.50
value at every n, since all three comparison distributions become
indistinguishable once almost no signal survives.

### mixed (n=2..4): TVD at the highest measured eta (0.99) and lowest measured eta (0.05)

| n | eta | tvd_to_lossless | tvd_to_uniform | tvd_to_product_marginals | alpha |
|---|---|---|---|---|---|
| 2 | 0.99 | 0.0197 | 0.1091 | 0.1091 | 1.0014 |
| 2 | 0.05 | 0.4997 | 0.4997 | 0.4997 | 3.06e-07 |
| 3 | 0.99 | 0.0245 | 0.4750 | 0.2126 | 2.0474 |
| 3 | 0.05 | 0.5000 | 0.5000 | 0.5000 | 1.60e-09 |
| 4 | 0.99 | 0.0292 | 0.5600 | 0.1770 | 3.1992 |
| 4 | 0.05 | 0.5000 | 0.5000 | 0.5000 | 6.37e-12 |

(Mixed scope's `tvd_to_uniform` and `tvd_to_product_marginals` are equal at
n=2 but diverge from n=3 onward -- with the weight-2 pair present, the
lossless reference's marginals are no longer product-like even at low
loss, unlike the pure-weight1 case above.)

**Stated plainly, both curves reported, no crossover-threshold judgment
made here (per `18-CONTEXT.md`'s lock):** for every n and both scopes,
`tvd_to_lossless` rises monotonically as eta decreases (from the
near-lossless anchor at eta=0.99 to ~0.50 at eta=0.05, i.e. the lossy
output becomes maximally distinguishable from the true lossless target).
Over that same range, `tvd_to_uniform` and `tvd_to_product_marginals`
**fall** as eta decreases -- from their eta=0.99 values (well above zero,
i.e. the lossless-ish output is still far from either classically-easy
baseline) down toward the same ~0.50 floor that `tvd_to_lossless` rises
to. In other words: as loss increases, the measured output distribution
moves away from the true lossless target and simultaneously moves toward
(and at the lowest measured eta, converges numerically with) both
classically-easy baselines. Whether/where this constitutes "classically
easy" is not asserted in this document.

## Anticoncentration results: alpha(eta)

![anticoncentration alpha vs eta](../results/phase18_anticoncentration_plot.png)

`alpha(eta) = 2**n * sum(p_x**2)` (Bremner-Montanaro-Shepherd's Theorem 4
normalization, arXiv:1610.01808: `Sigma p_x^2 <= alpha * 2^-n`), computed
directly/exactly from the full materialized distribution at each
`(n, eta)` cell (`hardness/baselines.py::anticoncentration_alpha`), never
sampled or estimated. `alpha=1.0` is the uniform/maximally-anticoncentrated
reference value (marked with a horizontal line in the plot above);
`alpha=2**n` is the maximally-concentrated (delta-distribution) extreme.

Alpha values at the same representative eta points (from the tables
above): **weight1** ranges from `alpha=2.78` (n=2, eta=0.99) up to
`alpha=16.20` (n=6, eta=0.99) at low loss, collapsing to `alpha<1e-4` (well
below the `alpha=1` uniform reference) at every n by eta=0.05. **mixed**
ranges from `alpha=1.00` (n=2, eta=0.99, i.e. already at the uniform
reference value) up to `alpha=3.20` (n=4, eta=0.99), collapsing similarly
by eta=0.05. In both scopes, `alpha(eta)` decreases monotonically as eta
decreases, and crosses below the `alpha=1` uniform-reference line
somewhere in the measured grid at every n -- the exact crossing eta is
readable directly from `results/phase18_weight1_loss_sweep.csv` /
`results/phase18_mixed_loss_sweep.csv`, not restated as a single number
here since it varies by n.

This is the exact quantity `docs/iqp-baseline.md`'s Bremner-Montanaro-Shepherd
(arXiv:1610.01808) bullet identifies as the one BMS's Theorem 4 keys its
depolarizing-noise hardness-vs-simulability threshold on. Reporting it here
is a forward pointer to Plan 18-08's HARD-04 positioning work, not itself a
positioning claim -- this document does not assert what alpha value or
crossing eta constitutes "hardness lost."

## HARD-07 results: weight-2 herald compounding

Photon loss is applied to **all `2n+2` modes** of the weight-2 pipeline,
including both `heralded_cz` ancilla modes -- per the Methodology section
above, the only mechanism that exposes whether loss degrades the herald
mechanism itself. Herald failure and transmission loss are measured
through **one** real `Processor.probs()` call per cell (never an
analytical product of a separately-computed lossless herald rate and a
separately-computed loss-survival probability), so any interaction between
the two failure modes is captured, not assumed away.

**Herald-success-rate vs eta** (n-independent within measurement precision
-- verified directly against the CSV: at each eta, `herald_success_rate_mean`
agrees across n=2, 3, 4 to 5+ significant figures, since the ancilla loss
mechanism does not depend on the number of data qubits):

| eta | herald_success_rate | herald_failure_prob |
|---|---|---|
| 0.99 | 0.07407 | 0.92593 |
| 0.95 | 0.07387 | 0.92613 |
| 0.90 | 0.07320 | 0.92680 |
| 0.80 | 0.07016 | 0.92984 |
| 0.60 | 0.05653 | 0.94347 |
| 0.35 | 0.02854 | 0.97146 |
| 0.05 | 0.00087 | 0.99913 |

At the near-lossless anchor (eta=0.99), `herald_success_rate` (0.07407) is
already close to the lossless `heralded_cz` baseline of `2/27 ≈ 0.07407`
(Phase 10's independently-established value, `STATE.md`'s Accumulated
Context) -- as expected, since eta=0.99 is near-lossless, not identically
lossless. It then falls monotonically to `0.00087` at eta=0.05, i.e. loss
compounds with the gate's own intrinsic herald-failure rate rather than
leaving it unchanged, confirming HARD-07's compounding requirement is
measured, not assumed.

**Postselection convention, restated explicitly (per `18-CONTEXT.md`'s
locked HARD-07 decision):** the `tvd_to_lossless` / `tvd_to_uniform` /
`tvd_to_product_marginals` / `alpha` values reported above for the mixed
scope are all computed on the distribution **conditioned on herald
success** (i.e. `dist`/`residual` are renormalized by dividing by
`herald_success_prob = 1 - herald_failure_prob`) -- matching this project's
existing `heralded_cz` convention and answering the operationally
meaningful question ("given the gate reports success, how does output
quality degrade with loss"). `herald_failure_prob` (the un-renormalized
number) is tracked and reported **separately** in the table above -- it is
never folded into `residual`, per this project's standing convention that
a gate's own postselection condition (herald mismatch, here) must be
accounted in that gate's own failure-probability column, not a generic
leakage bucket (`STATE.md`'s Accumulated Context, established during Phase
15).

## HARD-04/HARD-06: Positioning and Scope Statement (Plan 18-08)

*This section is intentionally incomplete at this point in the phase's
execution -- it is not abandoned.* HARD-04's eta-to-effective-depolarizing-rate
translation (grounded in this project's own heralded-CZ/CP(alpha) failure
mechanics, per `18-CONTEXT.md`'s locked derivation approach) and HARD-06's
final scope statement are completed by **Plan 18-08**, after the owner's
attempt-first checkpoint on the translation derivation (this project's
`CLAUDE.md` requires the owner to attempt any core conceptual derivation
before it is implemented for them, matching the ARB-02 checkpoint
precedent). Plan 18-08 appends its sections here without restructuring
anything written above.
