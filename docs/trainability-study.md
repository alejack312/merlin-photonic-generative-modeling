# Trainability / barren-plateau study (Phase 17)

The phase's canonical reference document, detailing methodology, generator scope, init/normalization convention, curve-fit results, honest max-n statement, and the cross-reference against `docs/iqp-baseline.md`'s qubit-side empirical plateau rule. Phase 20 (Technical Write-Up) draws on this document rather than re-deriving any of it.

## Methodology

Gradients are computed by **exact parameter-shift** (`shift = pi/4`, no division) directly on `photonic_iqp_distribution` / `photonic_weight2_iqp_distribution` (`merlin_iqp/encoding/iqp_photonic.py`), **not** MerLin `QuantumLayer` autograd. `QuantumLayer` categorically rejects this project's polarization-annotated `BasicState`s (`ValueError: BasicState with annotations is not supported`, confirmed live and recorded in `.planning/STATE.md`'s Accumulated Context), so autograd through it is structurally unavailable for this polarization encoding. (This is a restriction on the encoding, not on MerLin or on this abstract circuit family. See **Independent cross-check: dual-rail encoding + MerLin native autograd** below, where a different, polarization-free encoding of the same abstract circuit does support `QuantumLayer` autograd. The CORE sweep in this document still uses the polarization encoding throughout, so parameter-shift is what it uses.) 

Parameter-shift is used here because it is the only mechanism that works for this encoding, not because of a style preference. `trainability/param_shift.py` implements the shift. `trainability/rng.py` provides deterministic, reorder-safe RNG substreams so adding an n-value or init scheme never reshuffles another cell's random draws.

The loss whose gradient is measured is **MMD² between the circuit's output distribution and v1.0's K=2^n-generalized target distribution** (`trainability/target_grid.py`, Plan 17-03): a fresh `2^n`-bin grid built at every sweep point, cross-validated bit-faithfully against v1.0's original `compute_p_real` at its own K=462 shape. MMD² is computed via the **exact closed form** (`trainability/mmd_exact.py`, a numpy port of `generator/mmd.py`'s quadratic form `pᵀKp + qᵀKq − 2pᵀKq`), with no Monte Carlo sampling anywhere in this pipeline. A Monte-Carlo fallback was deliberately **not implemented**. Exact enumeration is tractable across this project's entire reachable n range (the photonic-simulation cost itself, not the `2^n`-sized kernel matrix, is what bounds how far n can go — see the Honest max-n statement below), so a fallback path would have been unused code.

## Parameter-initialization and normalization (TRAIN-03)

Two initialization regimes were swept, matching the split `docs/iqp-baseline.md`'s empirical rule is conditioned on:

- `**small_angle**`: `theta ~ Uniform(-0.1, 0.1)` per parameter.
- `**uniform**`: `theta ~ Uniform(0, 2*pi)` per parameter.

**Normalization convention:** this circuit's gates (phase shifters, `WP`, beamsplitters) are all passive/unitary. Total photon number is conserved by construction, with no separate energy-normalization parameter anywhere in the pipeline. `theta` is a bare phase-gate angle in radians, used directly as the `WP(theta, 0) = exp(i*theta*Z)` generator's argument. There is no rescaling, clipping, or per-circuit energy budget applied to it.

## Generator scope (TRAIN-04)

Two generator scopes were swept:

- `**weight1**`: one weight-1 `WP(theta_k, 0)` phase gate per qubit, `k = 0..n-1`.
- `**mixed**`: the same `n` weight-1 gates, plus **one fixed weight-2 `Z_i * Z_j` pair at `(i, j) = (0, 1)`**, composed via `photonic_weight2_iqp_distribution`: Phase 13's validated weight-1+weight-2 composability path.

**Why this split, and why exactly this mix:** `photonic_weight2_iqp_distribution` is the *only* already-shipped, already-validated multi-generator composition this project has (Phase 13, `test_wt2_composability_mixed_generators_n3` and related tests). Rather than inventing a new circuit topology or mix ratio for this study, Phase 17 reuses that exact composition as-is: one weight-2 pair added to the full weight-1 layer, at the lowest-index pair `(0,1)` so the same circuit shape generalizes unchanged across every swept `n >= 2`.

## Correction (2026-09-03, revised after an independent adversarial review) — the exponential-decay verdict is a pipeline artifact, not a trainability finding

**An external audit found, and this project independently re-verified, that the "exp" verdicts below do not measure the circuit.** At `sigma=0.03` and `sigma=0.1` (the bandwidths where the "exp" verdict appears), the Gaussian kernel is **numerically the identity matrix only for `n<=4`** (`target_grid.bin_spacing`: 1.2, 0.4 at n=2,3,4 — max off-diagonal kernel entry 3.4e-4, genuinely negligible). **This document's first version of this correction overclaimed that the same held "at every swept n" through n=6; it does not.** At `n=5,6` the bin spacing shrinks to 0.171, and the nearest-neighbor off-diagonal kernel entry is `exp(-0.171^2 / (2*0.1^2)) = 0.230` — a real, non-negligible off-diagonal term, independently confirmed by direct computation (`gaussian_kernel_matrix_np`), not the identity. `tests/v3_correction/test_null_results.py::test_kernel_is_identity_below_bin_spacing` only ever checked `n<=4`, correctly; the prose here previously extended that finding further than the test actually established, the exact kind of gap this whole correction exists to close.

What survives, precisely: the regression test that reproduces the shipped curve (`closed_form_gradient_variance`) uses the **real** kernel throughout — it never assumed identity — and still reproduces the shipped `n=2..6` curve within a documented tolerance (widened to `rel=0.5` specifically because the `n=5,6` fit is looser than `n<=4`'s, a direct consequence of the kernel genuinely doing more at those sizes, not a modeling error). So the "no photonics needed" claim survives at every `n`, but the *mechanism* is more precisely: exact L2-on-a-product-distribution for `n<=4`, and a partially-kernel-smoothed version of the same no-circuit-content computation for `n=5,6` — not literally identical to L2 there. Both are reproduced with **no photonics at all**, using this project's own `target_grid`/`mmd_exact` code and a product-distribution model (`weight1`) or that same product plus one fixed-`pi/4`-coupled pair (`mixed`) — this is now a standing regression test (`tests/v3_correction/test_null_results.py`), not a one-off check.

**This is not evidence of a barren plateau, for a structural reason as well as an empirical one — stated at the strength this actually supports.** `weight1` has no entangling gate; its output is a pure product distribution (already established in `docs/hardness-under-loss-study.md`'s HARD scope precondition). The measured decay is fully reproduced by a model with no circuit content, so it cannot be attributed to this circuit's loss landscape. That is not the same as a general proof that no product-distribution-based metric could ever exhibit barren-plateau-style behavior in some other setup — the claim here is narrower and specific to this measurement: this exponential shape is the null model's own `~2^-n`-type scaling, not a landscape property of this circuit.

**TRAIN-09's bandwidth-sensitivity pattern is consistent with, not proven by, this mechanism.** The sweep below found the "exp" signature present at `sigma in {0.03, 0.1}`, gone at `sigma in {0.3, 1.0}`, and back (non-monotonically) at `sigma in {3.0, 9.0}`. The low-`sigma` half of that pattern is directly explained by the mechanism above. The high-`sigma` re-emergence has **not** been checked against the same no-photonics null (the regression tests only cover `sigma<=0.1`) — it is plausible this is a second, different kernel-degeneracy artifact, but that is not yet a verified claim, and is stated here as a hypothesis, not a finding.

**The Rudolph et al. literature-comparison row (below) is corrected accordingly, at `n<=4` where the identity-kernel mechanism is exact**: this project's original fixed `SIGMA=0.1` is not merely "in the risk regime" their Theorem 2 flags — the identity-kernel mechanism confirmed here *is* the mechanism their theorem describes at those sizes. At `n=5,6`, the correction is weaker but still real: the shipped curve is fully reproduced by a no-circuit-content model regardless of the exact kernel character there.

**What survives this correction:** `docs/iqp-baseline.md`'s Mhiri et al. and Recio-Armengol et al. rows, and TRAIN-10's negative result (data-dependent init did not resolve `small_angle`), are untouched — they don't depend on this artifact. The tables and fitted curves below are kept as a documented pipeline artifact, not deleted, per this project's standing correction convention; read them as "what a no-circuit-content model of this loss reproduces," not as a trainability result.

## Results

**The table and curves immediately below are the ORIGINAL, uncorrected verdicts — read the correction above first.** They are retained as a documented artifact of the mechanism described above, not as an active trainability finding.

weight-1 curve fitmixed curve fit


| generator_scope | init_scheme | n range     | winning model | exp R² | exp AIC | poly R² | poly AIC |
| --------------- | ----------- | ----------- | ------------- | ------ | ------- | ------- | -------- |
| weight1         | small_angle | 2–6 (5 pts) | inconclusive  | 0.543  | -47.11  | 0.405   | -45.79   |
| weight1         | uniform     | 2–6 (5 pts) | exp           | 0.999  | -53.43  | 0.998   | -48.53   |
| mixed           | small_angle | 2–5 (4 pts) | inconclusive  | 0.000  | -41.76  | -0.000  | -41.76   |
| mixed           | uniform     | 2–5 (4 pts) | exp           | 0.910  | -37.56  | 0.823   | -34.85   |


Full per-cell numbers (including fitted parameters) are in `results/v3_trainability/phase17_curve_fit_summary.csv`.

**A fit-quality caveat, reported honestly:** two of the "exp"-winning fits (`weight1/uniform`'s R²=0.999 fit and, more severely, `mixed/uniform`'s R²=0.910 fit) show a large-magnitude, near-cancelling `a`/`c` pair (e.g. `mixed/uniform`: `a=153.6, c=-153.5`). `scipy.optimize.curve_fit` reported `Covariance of the parameters could not be estimated` for at least one cell during this run, a symptom of a poorly-identified (not just poorly-fit) parameterization at only 4-5 data points. The AIC-based verdict still holds (delta-AIC exceeds the 2.0 threshold in both "exp"-winning cells), but the specific fitted decay rate `b` in these near-degenerate cases should be read as "an exponential shape fits the data better than a power law," not as a precisely determined decay constant.

## Honest max-n statement (TRAIN-05, TRAIN-08)

**Correction (2026-09-03, revised) — the ceiling below is a simulator-architecture choice, not a physical limit, though the exact reachable n for a redesigned simulator is not established here.** The `C(3n-1,n) ~ 6.75^n` growth described below is real for *this pipeline's specific method* (enumerating every photon-number-conserving Fock state across the full `2n`/`2n+2`-mode register at once), but that method is not forced by the physics. `weight1` is `n` independent two-mode blocks with no cross-qubit interaction, and `mixed` adds exactly one fixed eight-mode gate block; a structured simulator that computes the gate's own small Fock space once and tensors the (trivial) per-qubit marginals for the rest would not run into a `MemoryError` at `n=7` the way the current full-register enumeration does — the exponential factor driving that error would no longer scale with total register size. This project's own `dual_rail_autograd_sweep.py` cross-check already reached `n=7-8` without hitting this wall, which corroborates that the ceiling is architecture-dependent, not that it demonstrates the specific `n` a structured Fock-space simulator would reach — that uses a different encoding (dual-rail via MerLin's native autograd) and method, not a direct benchmark of the redesign proposed here. **No structured Fock-space simulator has been built or timed; any specific reachable-`n` figure would be an unverified extrapolation and is deliberately not stated.** Building and benchmarking that simulator, and re-running toward the `N=20-24` threshold below, is out of this milestone's scope (see `.planning/REQUIREMENTS.md`'s v3.1 Out-of-Scope list) — the correction here is only to the *stated reason* for the ceiling, not a re-run or a performance claim.

**Actual n range reached, CORE data (complete and final):**

- `weight1`: n = 2..6, both init schemes, 100 draws/cell.
- `mixed`: n = 2..5, both init schemes, 100 draws/cell.

**Relative to `docs/iqp-baseline.md`'s n≥6 qubit-baseline threshold:** reached for `weight1` (n_max=6 satisfies n≥6 exactly at the boundary), **not reached** for `mixed` (n_max=5, one short of the threshold — mixed's per-call cost, driven by the weight-2 heralded-CZ/CP(alpha) postselection overhead, made n=6 substantially more expensive than n=6 weight-1. See `17-RESEARCH.md`'s measured per-n costs).

**Relative to the N=20-24 literature fit-flip threshold** (arXiv:2605.11879, the N=2-10-vs-N=24 poly-vs-exp fit flip this project's own pitfalls research flagged): **not reached, for either generator scope.**

This is a compute-cost fact, not a scheduling shortfall. This repo's photonic Fock-space output enumerates every photon-number-conserving Fock state across `2n` (or `2n+2`) modes — a space of size `C(3n-1,n)` for weight-1 or `C(3n+3,n+2)` for weight-2, not `2^n`. Stirling's approximation puts `C(3n-1,n) ~ (27/4)^n/sqrt(n) ~ 6.75^n`, a materially faster-growing function of `n` than the qubit-side literature's `2^n`.

`17-RESEARCH.md`'s directly-measured single-call costs in this repo's own venv confirm the growth is real, not a theoretical worst case:


| circuit  | n   | single distribution-call cost (measured) |
| -------- | --- | ---------------------------------------- |
| weight-1 | 2   | 0.033 s                                  |
| weight-1 | 8   | 247 s                                    |
| weight-2 | 2   | 0.041 s                                  |
| weight-2 | 6   | 71 s                                     |


At this sweep's actual cost structure (≥100 draws × ~3 tracked params × 2 shifts/param), the full sweep was estimated at:

- n=7 weight-1: ~5 hours (single init scheme)
- n=8 weight-1: ~3 days (single init scheme)

That's well past what fits inside this phase's timeline without becoming the open-ended compute struggle this project's `CLAUDE.md` explicitly warns against (the PennyLane-stall pattern).

**Stretch attempt status, final outcome:** a background job targeting n=7 (weight-1) and n=6 (mixed) was launched during Plan 17-06 with no time-box, per this phase's locked no-time-box decision.

Weight-1 n=7 failed 4/4 consecutive chunked attempts with an identical `MemoryError` on the very first circuit evaluation of each attempt — including when isolated in a completely fresh process with ~14GB free RAM immediately beforehand. That points to a genuine single-call memory ceiling on this hardware at n=7 weight-1, not a fixable cross-call leak (contrast the mixed n=5 CORE cell earlier in this phase, where chunking *did* resolve a real cross-call leak). The owner manually stopped the job rather than let it continue failing.

No stretch CSVs were produced; the n=2..6 (weight1) / n=2..5 (mixed) CORE range above is the actual measured range this document's verdict is based on. This gap between the reached range (n<=6) and the literature's N=20-24 fit-flip threshold is real, and this document reports it as a limitation of the measured range rather than a future-work item.

(A subsequent, independent dual-rail/MerLin cross-check *did* reach n=7-8 without hitting this same ceiling — see the new section below — but that used a different physical circuit and computational method, not a fix to this pipeline.)

## Cross-reference verdict (TRAIN-07)

**Read against the 2026-09-03 correction above:** the "measured shows exponential decay" / "measured data shows exponential decay anyway" language below refers to this document's own now-corrected artifact, not a genuine trainability measurement — so this section compares the qubit-side empirical rule (itself a separate fit, not re-examined here) against a photonic-side result that turned out not to measure the circuit. The comparison is kept as a documented record of the owner's original reasoning process, not as an active cross-validation between two independent findings.

`docs/iqp-baseline.md`'s empirical rule, applied directly to this project's own measured n range (its `not complete_graph_like` escape-hatch clause is a qubit-side structural notion this project's weight-1/mixed photonic circuits have no established mapping onto: treated as inapplicable here, not silently assumed to hold, since this project's circuits were never constructed with "complete-graph-like" as a design axis one way or the other):

```
plateau if init_scheme == small_angle
or plateau if init_scheme == uniform and max(n) >= 6
```


| generator_scope | init_scheme | baseline rule predicts   | measured fit verdict                           | agreement    |
| --------------- | ----------- | ------------------------ | ---------------------------------------------- | ------------ |
| weight1         | small_angle | plateau                  | inconclusive (weak fit both ways, R²≈0.4-0.5)  | inconclusive |
| weight1         | uniform     | plateau (n_max=6 >= 6)   | plateau (exp wins, R²=0.999, decaying)         | **agree**    |
| mixed           | small_angle | plateau                  | inconclusive (both R²≈0, no discernible trend) | inconclusive |
| mixed           | uniform     | no_plateau (n_max=5 < 6) | plateau (exp wins, R²=0.910, decaying)         | **disagree** |


> **Owner interpretation:** I went in without knowing the empirical rule, so I asked for it directly, along with whether TRAIN-10's data-dependent init resolved anything and whether this project ever varied circuit/graph structure the way the sibling project did. (For the record: the rule is `plateau if small_angle OR (uniform AND n>=6 AND not complete_graph_like)`; data-dependent init did not resolve `small_angle`'s inconclusive verdict in either scope; this project never varied circuit connectivity as a design axis.)
>
> First hypothesis, which didn't hold up: "Since the mixed/uniform produced a plateau at n=5, it may be complete_graph_like." This doesn't work, for two reasons. First, `not complete_graph_like` only modifies the `uniform AND n>=6` branch of the rule — at n=5 the rule already predicts no-plateau on n alone, so complete_graph_like status can't be what's driving a different outcome there. Second, this document itself states that removing `not complete_graph_like` "reintroduces false positives on complete-graph structures" — i.e., in the sibling project's data, complete-graph-like circuits tended toward *no* plateau, not toward one. So even if this circuit were complete-graph-like, that would point the wrong direction to explain an observed plateau. At this point, I acknowledged: "I'm not sure why we got this result then."
>
> Before concluding anything, I was asked to look at more data. I reviewed the raw fitted exponential parameters. `weight1/uniform` has a real, well-identified decay (`a=0.749, b=0.365, c=-0.055`), while `mixed/uniform`'s fit is the numerically degenerate one already flagged elsewhere in this document (`a=153.6, b=0.00008, c=-153.5`, near-zero decay rate with `a`/`c` nearly cancelling). I also looked at the raw per-n gradient-variance values directly. `weight1/uniform` decays smoothly and monotonically at every step across all 5 points. `mixed/uniform` is nearly flat from n=2→3 then drops from n=3→5, across only 4 points.
>
> I asked, mechanically, why the `c` parameters differ so much between the two fits. The answer: when the fitted decay rate `b` is near zero, `a` and `c` become unidentifiable/interchangeable, and the optimizer picks an arbitrary large cancelling pair rather than a data-pinned value — exactly the degeneracy `curve_fit`'s "covariance could not be estimated" warning already flags elsewhere in this document.
>
> I asked what the literature actually says about this. Recio-Armengol et al. (arXiv:2503.02934, Sec. 9.3) analytically derive that uniform/random init causes exponential concentration generically (`⟨Z_1⟩ = ∏cos(2θ_k)` over n terms) — an asymptotic-in-n claim with no specific n threshold attached, applying equally to weight1 and mixed circuits. Since the literature doesn't stake out a position on any particular n cutoff, `mixed/uniform` plateauing isn't anomalous relative to the general literature at all under that framing. What's actually unmatched is the sibling project's own fitted `n>=6` numeric threshold, which comes from a different, qubit-side circuit family, not the general literature claim.
>
> First proposed framing: "The empirical rule derived from the sibling project disagrees with the general rule established in literature. As a result, this finding agrees with the general literature." Since nothing actually shows the literature and the sibling's empirical n>=6 cutoff are in conflict with each other, and the literature just doesn't commit to a threshold at all, this framing was pushed back on as stated. The real, narrower finding is that `mixed/uniform`'s plateau at n=5 didn't match the sibling's specific fitted cutoff, which is a mismatch with a threshold, not evidence the two sources disagree in general.
>
> Final interpretation, accepted after that correction: the sibling project's specific `n>=6` numeric threshold didn't hold for `mixed/uniform` (which plateaued at n=5, below that cutoff) — but this is still consistent with the general literature's asymptotic (not threshold-specific) prediction that uniform init drives exponential concentration as n grows (Recio-Armengol et al., arXiv:2503.02934, Sec. 9.3). The literature doesn't stake out a position on any specific n cutoff, so `mixed/uniform` plateauing at n=5 isn't in tension with it — only with the sibling project's own fitted, qubit-side-specific `n>=6` heuristic. `weight1/uniform`'s agreement with that same `n>=6` cutoff may simply be coincidental alignment between a fitted threshold from a different circuit family and this project's own `n_max=6` reach, rather than evidence the threshold itself transfers mechanistically to this photonic circuit family.

## Bandwidth sensitivity follow-up (TRAIN-09)

**Scope note, stated up front:** this section and the one below it are Phase 17.1's follow-up checks, run *after* Phase 17 was already complete and verified. They do not alter any number or verdict in the sections above: they test whether those results hold up under a wider bandwidth/init sweep, and report the answer plainly in whichever direction it came out.

### Methodology / what changed

Phase 17's CORE sweep (`weight1` n=2–6, `mixed` n=2–5, both init schemes, 100 draws/cell) was re-run at a fixed sigma grid `{0.03, 0.1, 0.3, 1.0, 3.0, 9.0}` (owner-decided, ~3x log-spacing per step, centered on Phase 17's original `SIGMA=0.1` and chosen to bracket the CORE bin-spacing range of 0.17–1.2 on both sides), each sigma value held **constant across the whole n-range**: six independent fixed-sigma sweeps, not one sigma-schedule sweep.

An earlier candidate design — a per-n sigma *schedule*, scaling sigma with `n` to hold `sigma/bin-spacing` constant — was explicitly dropped. It requires picking one arbitrary anchor n to normalize against (anchoring at n=2 vs. n=5/6 tests different things, and neither is more "correct" than the other), and this project's own established convention is to sweep one fixed hyperparameter across the full n-range per run (exactly how `init_scheme` and Phase 17's original `SIGMA` were themselves swept). The fixed-grid design avoids the anchor-choice ambiguity entirely rather than resolving it with a guess, and directly follows the sibling project's own `AC12` bandwidth-sweep precedent, per `17.1-RESEARCH.md`'s Owner Decisions section.

### Results

**weight1** (n=2–6; sigma column is the fixed kernel bandwidth used for that row's whole sweep):


| sigma | init_scheme | winning model | exp R² | exp AIC | poly R² | poly AIC | vs. original                               |
| ----- | ----------- | ------------- | ------ | ------- | ------- | -------- | ------------------------------------------ |
| 0.03  | small_angle | inconclusive  | 0.139  | -49.85  | 0.021   | -49.21   | n/a (no exp verdict in original)           |
| 0.1   | small_angle | inconclusive  | 0.543  | -47.11  | 0.405   | -45.79   | n/a, matches original row exactly          |
| 0.3   | small_angle | exp           | 0.904  | -50.15  | 0.823   | -47.12   | n/a (no exp verdict in original)           |
| 1.0   | small_angle | inconclusive  | 0.993  | -73.46  | 0.992   | -73.33   | n/a (no exp verdict in original)           |
| 3.0   | small_angle | inconclusive  | 0.997  | -115.13 | 0.995   | -113.68  | n/a (no exp verdict in original)           |
| 9.0   | small_angle | inconclusive  | 0.997  | -158.78 | 0.996   | -157.05  | n/a (no exp verdict in original)           |
| 0.03  | uniform     | **exp**       | 0.999  | -52.40  | 0.998   | -47.73   | **survives**                               |
| 0.1   | uniform     | **exp**       | 0.999  | -53.43  | 0.998   | -48.53   | **survives**, matches original row exactly |
| 0.3   | uniform     | inconclusive  | 0.988  | -39.86  | 0.989   | -40.29   | **disappears**                             |
| 1.0   | uniform     | inconclusive  | 0.996  | -55.11  | 0.995   | -54.28   | **disappears**                             |
| 3.0   | uniform     | **exp**       | 0.999  | -95.78  | 0.997   | -92.31   | **survives** (re-emerges)                  |
| 9.0   | uniform     | **exp**       | 0.999  | -139.28 | 0.997   | -135.38  | **survives** (re-emerges)                  |


**mixed** (n=2–5):


| sigma | init_scheme | winning model | exp R² | exp AIC | poly R² | poly AIC | vs. original                               |
| ----- | ----------- | ------------- | ------ | ------- | ------- | -------- | ------------------------------------------ |
| 0.03  | small_angle | inconclusive  | 0.213  | -43.14  | 0.213   | -43.14   | n/a (no exp verdict in original)           |
| 0.1   | small_angle | inconclusive  | 0.000  | -41.76  | -0.000  | -41.76   | n/a, matches original row exactly          |
| 0.3   | small_angle | exp           | 0.920  | -50.68  | 0.837   | -47.84   | n/a (no exp verdict in original)           |
| 1.0   | small_angle | inconclusive  | 0.072  | -50.69  | 0.020   | -50.47   | n/a (no exp verdict in original)           |
| 3.0   | small_angle | inconclusive  | 0.337  | -76.62  | 0.337   | -76.62   | n/a (no exp verdict in original)           |
| 9.0   | small_angle | inconclusive  | 0.328  | -110.56 | 0.328   | -110.56  | n/a (no exp verdict in original)           |
| 0.03  | uniform     | **exp**       | 0.911  | -37.73  | 0.825   | -35.01   | **survives**                               |
| 0.1   | uniform     | **exp**       | 0.910  | -37.56  | 0.823   | -34.85   | **survives**, matches original row exactly |
| 0.3   | uniform     | inconclusive  | 0.598  | -32.21  | 0.470   | -31.10   | **disappears**                             |
| 1.0   | uniform     | inconclusive  | 0.000  | -29.51  | 0.302   | -30.95   | **disappears**                             |
| 3.0   | uniform     | inconclusive  | 0.330  | -58.71  | 0.330   | -58.71   | **disappears**                             |
| 9.0   | uniform     | inconclusive  | 0.325  | -92.96  | 0.325   | -92.96   | **disappears**                             |


Full per-cell numbers (all 24 rows, both scopes): `results/v3_trainability/phase171_train09_curve_fit_summary.csv`.

**Sigma=0.1 consistency-check footnote:** the `sigma=0.1` row of this grid is a built-in sanity check: it should reproduce Phase 17's original CORE result exactly, since it re-runs the identical sweep at the identical bandwidth through the new sigma-threaded code path. `weight1` matched bit-for-bit on every compared row. `mixed` matched exactly on 2 of 8 rows and showed a ~1e-13 to 1e-16 relative-magnitude difference on the other 6 (`small_angle` at n=2,3,4), diagnosed (Plan 17.1-04) as a deterministic environment/floating-point-ordering difference rather than a logic bug (re-running the affected cell reproduced this pipeline's own value bit-for-bit, and `weight1`'s identical sigma-threading code shows zero drift), and noted here as an open, non-blocking item.

### Does the exp-decay verdict survive the sigma grid?

**No, not for either `uniform` cell, and the way it fails is itself the finding.** `weight1/uniform` and `mixed/uniform` were the two cells with a definite original "exp" verdict. Both survive at sigma in {0.03, 0.1} (near Phase 17's original fixed bandwidth) and both flip to "inconclusive" at sigma in {0.3, 1.0}. Past that, the two scopes diverge. `weight1/uniform` **non-monotonically re-emerges** as "exp" at sigma in {3.0, 9.0}, while `mixed/uniform` stays "inconclusive" through sigma=9.0. A simple "it was only ever a fixed-bandwidth artifact and fades away as sigma grows" story does not fit `weight1`'s re-emergence at large sigma either: the true picture is that the verdict is **sigma-dependent in a non-trivial, non-monotonic way**, not a stable property of the circuit/init pair across bandwidths.

**Plain statement, no hedging:** Phase 17's original "exp" verdict for `weight1/uniform` and `mixed/uniform` is **not robust** across this sigma grid. It survives only near the original bandwidth and, in `weight1`'s case, again at bandwidths far from it. This reveals the original fixed-`SIGMA=0.1` result was at least partly a bandwidth-dependent artifact of that specific kernel choice, not solely a genuine, bandwidth-independent circuit/init property. A genuine effect may still exist — the sigma=0.1 and sigma=0.03 agreement, and `weight1`'s large-sigma re-emergence, are both real measured signals rather than noise — but the single-bandwidth Phase 17 result cannot be read as bandwidth-independent evidence on its own.

## Data-dependent initialization follow-up (TRAIN-10)

### Methodology

Recio-Armengol et al.'s (arXiv:2503.02934, Sec. 8.1.2) data-dependent initialization recipe was translated onto this project's grid-bin target representation (the paper's own recipe assumes a raw bitstring dataset, which this project does not have: its target is `p_real`, a probability distribution over `2^n` grid bins built by `trainability/target_grid.py`). Weight-1 angles are set to `arcsin(sqrt(<x_k>))`, where `<x_k>` is the marginal probability that bit `k` of the sampled bin index equals 1 under `p_real` (the project's stand-in for "the mean of the k-th dimension of the training data"). For the `mixed` scope, this project's circuit has no independent weight-2-only parameter: the weight-2 pair's two qubits `(0,1)` receive the covariance-based `weight2_data_dependent_theta` value **in place of** their own per-qubit weight-1 rule value, while every other qubit keeps the standard weight-1 rule. This design decision was made explicitly in Plan 17.1-03 (not silently), since a reader of this document would not otherwise have seen it, and is independently verified there by a test that reproduces the gradient computation with and without the override and confirms the actual sweep output matches only the "with override" version. `scale_factor=1.0` (owner-decided, matches the paper's own upper grid-search bound, making weight-2 angles directly equal to the raw ±1-convention covariance) and `n_draws=1` (owner-decided) were used: the recipe is fully deterministic given `(n, p_real, scale_factor)`, so additional draws would produce bit-identical theta vectors and add no rigor, only redundant compute.

### Results


| generator_scope | init_scheme    | n range     | winning model | exp R² | exp AIC | poly R² | poly AIC |
| --------------- | -------------- | ----------- | ------------- | ------ | ------- | ------- | -------- |
| weight1         | data_dependent | 2–6 (5 pts) | inconclusive  | 0.000  | -103.85 | -0.000  | -103.85  |
| mixed           | data_dependent | 2–5 (4 pts) | inconclusive  | 0.253  | -46.63  | 0.253   | -46.63   |


Full numbers: `results/v3_trainability/phase171_train10_curve_fit_summary.csv`.

**Comparison against the original `small_angle` verdict, stated plainly:**


| generator_scope | original (`small_angle`) verdict | new (`data_dependent`) verdict | clearer result?            |
| --------------- | -------------------------------- | ------------------------------ | -------------------------- |
| weight1         | inconclusive (R²≈0.4–0.5)        | inconclusive (R²≈0.000)        | **no, still inconclusive** |
| mixed           | inconclusive (R²≈0)              | inconclusive (R²≈0.253)        | **no, still inconclusive** |


### Does a literature-sourced init resolve the inconclusive verdict?

**No, plainly.** Recio-Armengol et al.'s data-dependent initialization did **not** produce a clearer (non-inconclusive) verdict than `small_angle` in either generator scope: both `weight1/data_dependent` and `mixed/data_dependent` remain "inconclusive," in `weight1`'s case with an even weaker exp-model fit (R²≈0.000) than the original `small_angle` row (R²=0.543) it was meant to potentially clarify. This is a genuine negative result for the literature-sourced alternative-init hypothesis, reported here exactly as measured: the `small_angle` scheme's inconclusiveness is not an artifact of that specific init recipe: it persists under a different, principled init strategy too.

## Independent cross-check: dual-rail encoding + MerLin native autograd

**Scope note, stated up front:** everything in this section is supplementary work done *after* Phase 17 was already complete and verified (8/8 must-haves, `.planning/phases/17-trainability-barren-plateau-study/17-VERIFICATION.md`). It is not tracked as a phase requirement in `ROADMAP.md`/`REQUIREMENTS.md` and does not change Phase 17's own verdict above: it is an independent second measurement of the same underlying question, using a different circuit and a different computational method, kept here because it bears directly on TRAIN-05/TRAIN-08's max-n question.

### Why this is possible at all

The Methodology section above states plainly that MerLin `QuantumLayer` autograd is unavailable for this project's polarization-annotated circuits. That remains true. What changed: `merlin_iqp/encoding/dual_rail.py` (added after Phase 17 closed) re-implements the same abstract weight-1/weight-2 IQP generator family in a **polarization-free spatial dual-rail basis**: `BS()` in place of `HWP(pi/8)`, `PS(theta)` in place of `WP(theta,0)`, no `PBS()` needed since the circuit is already dual rail throughout. MerLin's restriction is specifically on polarization annotations, not on dual rail itself, so `QuantumLayer` accepts this circuit with no issue. This is a **different physical encoding of the same abstract circuit**, not a fix or optimization of the polarization pipeline above. The two are independent measurements, not before/after versions of one pipeline.

`trainability/dual_rail_autograd_sweep.py` computes the same MMD² loss against the same per-n target grid (`trainability/target_grid.py`, reused unmodified), but keeps the entire computation (MerLin's raw output, the bin-mapping to the target grid, the MMD² quadratic form) in torch tensors throughout, so `.backward()` yields exact gradients for **all** n circuit parameters from one forward+backward pass. Since autograd's cost doesn't scale with how many parameters are tracked, this sweep tracks all n parameters (no `max_tracked_params` cap) — structurally different from parameter-shift's 2-evaluations-per-tracked-parameter cost.

### Reached n range and why it's larger


| generator_scope | this phase's CORE range (parameter-shift) | dual-rail/autograd range |
| --------------- | ----------------------------------------- | ------------------------ |
| weight1         | n = 2..6                                  | n = 2..8                 |
| mixed           | n = 2..5                                  | n = 2..7                 |


Two sizes further in each case, reached without hitting the `MemoryError` ceiling described above. Two compounding, distinct reasons, not one:

1. **Fewer circuit evaluations per draw** (inherent to the method, not an implementation detail): parameter-shift needs 2 Perceval evaluations *per tracked parameter*: at n=8 tracking all 8 params, 16 evaluations per draw. Reverse-mode autograd gets every parameter's gradient from one forward + one backward pass, regardless of parameter count.
2. **Cheaper per-evaluation cost, via reuse** (partly a fixable gap in how the polarization pipeline above is written, partly inherent to supporting autograd at all): `run_full_circuit`/`photonic_iqp_distribution` bake theta in as a concrete float and rebuild a fresh `pcvl.Processor` + `Analyzer` from scratch on every single call. MerLin's `QuantumLayer` builds its differentiable computation graph once per circuit topology and reuses it across draws. Only parameter *values* change between calls. This was measured directly. At n=8, `QuantumLayer` construction takes ~~40s (one-time), then each subsequent forward+backward pass on that same layer takes ~0.2s, cheaper than a *single* `Analyzer` call was at the smaller n=6 in this phase's own CORE sweep (~~1.57s, backed out from that sweep's logged per-cell timings: ~950s / 600 calls).

Net effect on wall-clock time: the full dual-rail sweep (weight1 n=2..8 + mixed n=2..7, both init schemes, 100 draws/cell, all n parameters tracked) completed in **~10.5 minutes** of actual compute, run overnight locally to avoid competing with the owner's other active work for RAM.

### Results


| generator_scope | init_scheme | n range     | winning model | exp R² | exp AIC | poly R² | poly AIC |
| --------------- | ----------- | ----------- | ------------- | ------ | ------- | ------- | -------- |
| weight1         | small_angle | 2–8 (7 pts) | **exp**       | 0.838  | -110.17 | 0.714   | -106.20  |
| weight1         | uniform     | 2–8 (7 pts) | **exp**       | 0.983  | -74.59  | 0.973   | -71.33   |
| mixed           | small_angle | 2–7 (6 pts) | inconclusive  | 0.570  | -70.64  | 0.570   | -70.64   |
| mixed           | uniform     | 2–7 (6 pts) | inconclusive  | 0.840  | -69.16  | 0.814   | -68.26   |


Full numbers: `results/v3_trainability/phase17_dual_rail_curve_fit_summary.csv`.

**Comparison against this phase's own CORE verdict, stated plainly (agreements and disagreements both):**


| generator_scope | init_scheme | CORE verdict (n<=6, polarization) | dual-rail verdict (n<=7/8)                  | agreement                                                                                                                                                                 |
| --------------- | ----------- | --------------------------------- | ------------------------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| weight1         | small_angle | inconclusive                      | **exp** (R²=0.838)                          | verdict label changed, but see Follow-up Experiments below. The exp fit's own `b` parameter is still degenerate (6.48e-05 dual-rail vs 6.97e-05 original, near-unchanged) |
| weight1         | uniform     | exp (R²=0.999)                    | exp (R²=0.983)                              | **agree**                                                                                                                                                                 |
| mixed           | small_angle | inconclusive                      | inconclusive                                | **agree**                                                                                                                                                                 |
| mixed           | uniform     | exp (R²=0.910)                    | **inconclusive** (R²=0.840, AIC margin < 2) | **disagree**                                                                                                                                                              |


The `mixed/uniform` disagreement is reported exactly as found, not resolved or explained away here: it could reflect the extra 2 data points changing the fit, a real difference between the two physical encodings, or both. Distinguishing between those requires the owner's own analysis, not an assertion in this document.

> **Owner interpretation:** Three candidate interpretations for the `mixed/uniform` disagreement, none currently ruled in or out:
>
> 1. **No real effect.** The original 4-point "exp" verdict was decided between two near-identical degenerate fits (both `b≈0`, both with large near-cancelling `a`/`c`) — essentially a noise-level AIC difference, not a real signal. The dual-rail fit's `exp` model became well-conditioned (`b=0.103`), but still did not clear the delta-AIC>2 threshold against `poly`, and the bootstrap CI's lower bound (0.0002) sits arbitrarily close to zero. Under this reading, six data points still isn't enough to distinguish real weak decay from no decay.
> 2. **A real, weak effect.** If the true decay rate were exactly zero, roughly half of 500 independent bootstrap resamples should land on a negative `b` from noise alone. 0/500 did. Under this reading, both datasets are picking up the same real, if weak, decay — something specific to the weight-2/mixed circuit, since `weight1/small_angle` did *not* resolve into a non-degenerate fit with more data while `mixed/uniform` did.
> 3. **The comparison may be under-specified.** The two datasets don't fully overlap in n range (2-5 vs 2-7), use different computational methods (parameter-shift vs. autograd) and different gate mechanics for the surrounding weight-1 layer (symmetric `WP` vs. single-sided `PS` — argued equivalent up to global phase, never independently verified at the gradient-variance statistical level across the actual swept draws), and different floating-point precision paths (MerLin defaults to float32). Treating the two datasets as replications of one experiment may itself be premature.
>
> **Further experimentation is required to conclude whether the true explanation is one of these three, some combination, or something else not yet identified.** None of the three is asserted as the answer here.

**What this cross-check does/doesn't establish, beyond the section below's general caveats:** agreement between two *different physical circuits* answering the same abstract question is stronger evidence than either alone, but the two encodings are not guaranteed to have identical trainability behavior even if they realize "the same" IQP generator family: dual rail and polarization differ in gate composition, ancilla structure (weight-2), and every other implementation detail below the abstract operator level. A disagreement (as seen in `mixed/uniform`) is therefore genuinely ambiguous between "thin-data artifact" and "encoding matters," and this document does not resolve which.

### Follow-up experiments (post-cross-check)

Three follow-up experiments were run after the cross-check above, in response to the `mixed/uniform` disagreement.

**1. Fitted parameters for `weight1/small_angle`.** This cell's verdict changed from "inconclusive" (original, n=2..6) to "exp" (dual-rail, n=2..8) in the tables above. The fitted `exp_model(n) = a*exp(-b*n) + c` parameters for both:


|                    | a      | b         | c       |
| ------------------ | ------ | --------- | ------- |
| Original (n=2..6)  | 54.556 | 6.972e-05 | -54.490 |
| Dual-rail (n=2..8) | 4.372  | 6.477e-05 | -4.368  |


For comparison, `mixed/uniform`'s fitted parameters (already given above): original `a=153.555, b=7.998e-05, c=-153.478`; dual-rail `a=0.0390, b=0.1026, c=-0.0180`.

**2. Attempted extension of the dual-rail mixed sweep to n=8/9.** `pooled_native_gradients_for_cell(8, "mixed", "uniform", draw_start=0, draw_count=100)` was run. It took 2929.4s (~48.8 min) and raised `MemoryError` inside MerLin's `SLOSComputeGraph._build_graph_structure` (`merlin/pcvl_pytorch/slos_torchscript.py`), during `QuantumLayer` construction, before any forward/backward pass executed. n=9 was not attempted. The process exited on the n=8 failure. For reference: mixed n=8 has `2n+2=18` modes and `n+2=10` total photons (`C(27,10) ≈ 8.4 million` Fock states). Mixed n=7 (the largest completed cell) has 16 modes and 9 photons (`C(24,9) ≈ 1.3 million` Fock states).

**3. Bootstrap confidence interval on `mixed/uniform`'s dual-rail decay rate `b`.** Method: for each of 500 iterations, the pooled gradient samples at each n=2..7 were independently resampled with replacement (same sample count per n), `var` was recomputed per n from the resampled values, and `exp_model` was refit via `scipy.optimize.curve_fit`. Results:

- 500/500 bootstrap iterations produced a converged fit.
- `b` across the 500 fits: mean = 0.1022, median = 0.1009, std = 0.0604.
- 95% CI (2.5th–97.5th percentile of the 500 `b` values): [0.0002, 0.2285].
- Fraction of the 500 resampled `b` values that were <= 0: 0.000.

## What this does/doesn't establish

This is an empirical measurement at this project's own small, compute-bound n range (n<=6), not a proof of any asymptotic trainability property. A measured exponential-decay signature at n=2..6 does not, by itself, establish that this photonic realization inherits the qubit-side rule's behavior at hardware-relevant scale (n in the tens to hundreds). The same caution `docs/iqp-baseline.md` itself raises about average-case barren-plateau statements applies here too. Nor does the one measured disagreement (`mixed/uniform`) establish that the qubit-side rule fails to transfer to photonic encodings in general: it establishes that, at this specific small n range, with this specific mixed weight-1+weight-2 circuit and this specific target distribution, the rule's prediction and the measured gradient-variance trend disagreed. Extending this measurement toward the literature's N=20-24 range, or testing other circuit topologies/target distributions, would be required before drawing any stronger conclusion.

**Phase 17.1 addendum:** two further follow-up checks exist beyond the cross-check above and are documented in their own sections earlier in this document: **Bandwidth sensitivity follow-up (TRAIN-09)**, which found Phase 17's original "exp" verdict for `weight1/uniform` and `mixed/uniform` is not robust across a six-point sigma grid, and **Data-dependent initialization follow-up (TRAIN-10)**, which found a literature-sourced alternative init did not resolve `small_angle`'s inconclusive verdict in either scope. Neither follow-up alters Phase 17's own reported numbers or verdicts above. Both narrow what those original numbers can be read to establish.

### Literature comparison table (WRITE-02)

All 11 baselines from this project's fresh primary-source literature read (`docs/iqp-baseline.md`'s "Fresh Primary-Source Verification" section), checked against TRAIN's own results above. Six bear directly on trainability and get a substantive consistent/inconsistent/silent verdict with reasoning; five are HARD- or ARB-specific and are marked silent with a one-line reason, per this plan's own scoping decision (keeping this table TRAIN-focused rather than padded with baselines that make no trainability claim).

**Substantive rows:**

- **McClean, Boixo, Smelyanskiy, Babbush & Neven, "Barren plateaus in quantum neural network training landscapes"**: before drafting this row, the paper's actual arXiv ID and core claim were confirmed live against the arXiv API (not trusted from this repo's own prior WebSearch-sourced summaries, per `20-RESEARCH.md`'s flagged gap): **arXiv:1803.11173**, *Nature Communications* 9, 4812 (2018). The fetched abstract confirms the paper's core claim: for a wide class of parameterized quantum circuits, gradient magnitude along any fixed direction becomes exponentially small as a function of qubit count, which is the same diagnostic shape (gradient-variance-vs-system-size) Phase 17's own methodology uses. **Verdict: consistent with the well-known protocol shape.** Confidence caveat, stated honestly rather than silently upgraded: this confirmation is a direct primary-source fetch of the paper's own abstract/metadata via the arXiv API, not a full PDF read, unlike the other 10 baselines in this list, all of which have a downloaded PDF in `docs/papers/`. It should be read as more reliable than a WebSearch-level summary, but at a lower confidence tier than this project's fully-read papers.
- `**docs/iqp-baseline.md`'s own empirical rule**: see the Cross-reference verdict (TRAIN-07) table above rather than re-deriving it here. **Verdict: split.** `weight1/uniform` **agrees** with the rule (predicts plateau at n_max=6>=6, measured shows decay); `mixed/uniform` **disagrees** (rule predicts no-plateau since n_max=5<6, but measured data shows exponential decay anyway); see the owner's interpretation of this split immediately above. Both `small_angle` rows are inconclusive on both sides, with no verdict to compare.
- **Rudolph et al. (arXiv:2305.02881, Theorem 2)**: **Correction (2026-09-03): upgraded from "directionally consistent" to this is the mechanism.** The row below is the pre-correction text, kept for the record; see the dated correction at the top of Results. This project's fixed `SIGMA=0.1` is not merely in the risk regime Theorem 2 flags — the identity-kernel-on-a-product-distribution mechanism verified in `tests/v3_correction/test_null_results.py` is a direct instance of the paper's own constant-bandwidth exponential-concentration argument, confirmed by reproducing the shipped curve with no photonics at all. The paper's bodyness decomposition assumes a bitstring-Hamming-distance kernel rather than this project's Euclidean-distance kernel, so the *specific formula* doesn't transfer, but the *phenomenon* — a fixed, n-independent bandwidth forcing exponential concentration regardless of circuit structure — is exactly what happened here, not a merely-analogous risk.

  *Original (2026-08-12) text, superseded by the correction above:* "verdict: directionally consistent with TRAIN-09's bandwidth-sensitivity finding, mechanistically non-transferable. The original fixed-`SIGMA=0.1` 'exp' verdict for both `uniform` rows is exactly the regime Theorem 2 identifies as independently sufficient to cause exponential MMD concentration (a constant, n-independent bandwidth), and TRAIN-09 found that verdict is indeed not robust once bandwidth is varied: directional agreement on the *risk*. The paper's own bodyness decomposition assumes a bitstring-Hamming-distance kernel, which does not mechanically transfer to this project's Euclidean-distance kernel over grid bin centers (already stated in the TRAIN-09 section and in `docs/iqp-baseline.md`), so the *mechanism* the paper proves does not directly apply here, even though the qualitative risk it flags does. Both halves are reported here in full."
- **Mhiri et al. (arXiv:2502.07889, p.5-6, Appendix H)**: **verdict: consistent.** Their proof that small-angle/warm-start guarantees are not general (with structured/commuting circuits flagged as the specific risk case, "an extreme example... is one that completely commutes with the observable or state... its variance trivially becomes zero," p.5-6) is a citable theoretical reason both `small_angle` rows (weight1 and mixed) came out inconclusive rather than a clean plateau either way, matching this project's IQP-style commuting-diagonal-gate structure.
- **Recio-Armengol et al. (arXiv:2503.02934, Sec. 9.3 and Sec. 8.1.2)**: **verdict: consistent for the uniform-init exponential-concentration finding.** Their Sec. 9.3 analytical derivation (`⟨Z_1⟩ = ∏cos(2θ_k)` over n terms causing generic exponential concentration under uniform init) matches this project's own empirical `uniform`-init signature. Their Sec. 8.1.2 proposed fix (data-dependent init) was directly implemented and tested as TRAIN-10 and found **not** to resolve `small_angle`'s inconclusive verdict in either generator scope: a genuine negative result for the literature-sourced alternative-init hypothesis, reported here exactly as measured.
- **Herbst et al. (arXiv:2512.24801)**: this baseline's substantive content is the cross-reference note below. **Verdict: see Cross-reference note below.** TRAIN's own zero-loss data shows a genuine (if bandwidth-fragile) untrainability signature for `uniform` init, which is not in tension with Herbst et al.'s framework, but TRAIN never varies loss and so cannot itself confirm or refute the paper's eta-dependent co-occurrence prediction.

**Silent rows** (one line each: these baselines don't bear on TRAIN specifically):

- **Aaronson-Brod (arXiv:1510.05245)**: lost-photon hardness result; HARD-specific, not a trainability claim.
- **arXiv:2510.24137 (Park & Oh)**: MPS-simulability/noisy-IQP hardness result; HARD-specific.
- **arXiv:2405.01395**: two-photon gate construction paper; ARB-specific, makes no trainability or hardness claim of its own.
- **Bremner-Montanaro-Shepherd 2015 (arXiv:1504.07999)**: foundational noiseless-IQP hardness threshold; no trainability claim.
- **Bremner-Montanaro-Shepherd 2017 (arXiv:1610.01808)**: depolarizing-noise hardness threshold; HARD-specific, no direct trainability claim of its own.

### Cross-reference: Herbst et al.'s anticoncentration-tradeoff prediction

**Correction (2026-09-03):** TRAIN's own "concentrated-loss-landscape signature" this section cites is the identity-kernel/product-distribution artifact described at the top of this document's Results section — not a genuine concentration signature. This cross-reference's conclusion (this project's data is silent on Herbst et al.'s prediction) is unaffected, but for a stronger reason than originally stated: TRAIN never measured a real trainability signature at all, so it could not have tested the prediction's trainability side regardless of what HARD's `eta`-axis did.

`docs/iqp-baseline.md`'s "Fresh Primary-Source Verification" section cites Herbst, Brandic & Perez-Salinas (arXiv:2512.24801) for a formal result: circuits whose output distributions anticoncentrate are predicted to have *both* increased classical-simulability-under-noise (the hardness side) and increased MMD-type-loss concentration (the trainability side). The two effects are predicted to co-occur, not trade off against each other.

**TRAIN's own measured facts, stated plainly:** at Phase 17's original fixed bandwidth (`SIGMA=0.1`), both `uniform`-init cells (`weight1` and `mixed`) show an exponential gradient-decay signature (R²=0.999 and R²=0.910 respectively): exactly the concentrated-loss-landscape signature Herbst et al.'s framework predicts should accompany anticoncentration. TRAIN-09's bandwidth-sensitivity follow-up found this signature is **not** robust across a wider sigma grid: both cells' "exp" verdict survives only near the original bandwidth (sigma in {0.03, 0.1}) and flips to "inconclusive" at intermediate sigma (0.3, 1.0), with `weight1/uniform` non-monotonically re-emerging as "exp" at high sigma while `mixed/uniform` does not. This caveat must be stated alongside the headline exponential-decay result, not in its place.

**What TRAIN's own dataset cannot do:** TRAIN never varies loss (`eta`) at all: Phase 17/17.1's entire sweep is run at `eta=1` (no photon loss), varying only `n` and the bandwidth/init hyperparameters. Herbst et al.'s prediction is specifically about how anticoncentration (and its knock-on effects on both hardness and MMD-loss concentration) changes as loss increases: a claim about the `eta` axis. TRAIN's data alone cannot confirm or refute that axis. It can only establish that a genuine (if bandwidth-fragile) concentration signature exists for `uniform` init at zero loss, which is a necessary precondition for the co-occurrence prediction to be interesting here, not a test of the prediction itself.

**Pointer to the HARD-side half:** `docs/hardness-under-loss-study.md`'s own equivalent cross-reference note reports the measured `eta`-side result directly. Because uniform per-mode photon loss preserves the surviving distribution's shape exactly, `alpha(eta)` is **exactly invariant** under loss, for both weight-1 and mixed scope. Since Herbst et al.'s prediction is keyed on anticoncentration varying, and the `eta` axis does not move it, the HARD-side data is **silent** on that prediction rather than supporting or contradicting it. *Corrected 2026-08-20:* this pointer previously reported `alpha(eta)` decreasing with loss (and, via Herbst et al., implied trainability should worsen with loss) — that was an un-renormalized-alpha artifact, now fixed in code and regenerated across every affected dataset. See that document for the corrected result; it is not restated here.

**Combined statement, hedged appropriately:** TRAIN and HARD do not share a common independent variable: TRAIN sweeps `n` at fixed `eta=1`; HARD sweeps `eta` at small fixed `n`. Neither phase varies both together on one dataset, so this project cannot directly test Herbst et al.'s co-occurrence prediction with a single combined experiment. What can be said, qualitatively: TRAIN's zero-loss data shows a genuine (if bandwidth-sensitive) untrainability signature for `uniform` init, while HARD's data shows anticoncentration is exactly invariant along the `eta` axis (corrected 2026-08-20; the previously-reported increase was an artifact). Taken together under Herbst et al.'s framework, these two facts are not in tension — but neither do they combine into support for the prediction. One axis shows a concentration signature at fixed zero loss, the other shows the keyed quantity not moving at all. This is a statement about what the two datasets do and don't jointly cover, not a joint confirmation of the prediction. Per this project's `CLAUDE.md` convention (Claude organizes and computes; the owner reviews and owns interpretive conclusions), this combined reading is offered as an organized statement of the measured facts, not asserted as a settled conclusion: distinguishing what's actually consistent (no contradiction found) from what remains untested (the actual eta-dependence of TRAIN's own gradient variance, never measured in this project).