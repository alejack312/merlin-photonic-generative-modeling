"""Phase 18 (Hardness-Under-Loss Assessment) integration layer -- Plan 18-05.

Wires Plan 18-02's `hardness.loss_model.photonic_iqp_distribution_lossy`
(weight1), Plan 18-03's `hardness.loss_model_weight2.photonic_weight2_iqp_distribution_lossy`
(mixed), and Plan 18-04's `hardness.baselines` (uniform_baseline,
product_of_marginals_baseline, anticoncentration_alpha) together into the one
per-cell integration function Plan 18-06 needs to actually run the real
photon-loss sweep: `pooled_cell_for_neta`.

Everything here operates on ONE (n, eta, generator_scope) cell at a time,
pooled/averaged across independent random-theta draws -- mirroring
`trainability/sweep.py::pooled_gradients_for_cell`'s "raw array now,
summarize once (possibly after concatenating draw-chunks) later" shape, but
for this phase's own distinct quantity set (TVD-to-lossless,
TVD-to-uniform-baseline, TVD-to-product-of-marginals-baseline, the BMS
anticoncentration parameter alpha, and -- mixed scope only --
herald_failure_prob/herald_success_rate), not gradients.
"""

import numpy as np

from hardness.baselines import (
    anticoncentration_alpha,
    product_of_marginals_baseline,
    uniform_baseline,
)
from hardness.loss_model import photonic_iqp_distribution_lossy
from hardness.loss_model_weight2 import photonic_weight2_iqp_distribution_lossy
from iqp_photonic_encoding import total_variation_distance
from trainability.rng import get_rng

# 18-CONTEXT.md's locked eta-grid design: a fixed set of ~6-8 representative
# points (mirrors TRAIN-09's fixed-sigma-grid precedent), spacing
# deliberately DENSER near eta=1 (low loss) than near eta=0 (near-total
# loss) -- gaps widen as eta decreases: 0.99->0.95 is 0.04, 0.95->0.90 is
# 0.05, 0.90->0.80 is 0.10, 0.80->0.60 is 0.20, 0.60->0.35 is 0.25,
# 0.35->0.05 is 0.30. The SAME grid is used for both weight-1 and mixed
# scopes (18-CONTEXT.md: "keeps the two scopes directly comparable").
ETA_GRID = [0.99, 0.95, 0.90, 0.80, 0.60, 0.35, 0.05]

# Per-quantity column order for the raw per-draw array this module returns
# for chunking (see _raw_values_for_cell / combine_pooled_cells below).
# Mixed scope adds herald_failure_prob (weight-1 has no herald).
WEIGHT1_QUANTITIES = ["tvd_to_lossless", "tvd_to_uniform", "tvd_to_product_marginals", "alpha"]
MIXED_QUANTITIES = WEIGHT1_QUANTITIES + ["herald_failure_prob"]


def sample_thetas(rng, n):
    """Draw n circuit parameters uniformly over [0, 2*pi).

    This phase's own generic "uniform" init convention (reusing the SHAPE,
    not the code, of trainability.sweep.sample_thetas's "uniform" branch).
    Deliberate, stated scope decision (Claude's Discretion per
    18-CONTEXT.md): HARD-05/HARD-07 want the loss sweep's circuit instances
    to be generic/representative draws (matching Phase 17's own "uniform"
    scope -- the regime that produced its clean measured signal there), not
    a special-cased warm start like "small_angle". Not silently inherited --
    this phase has no init-scheme axis at all, unlike Phase 17/17.1.
    """
    return rng.uniform(0, 2 * np.pi, size=n).tolist()


def _quantities_for_scope(scope):
    if scope == "weight1":
        return WEIGHT1_QUANTITIES
    if scope == "mixed":
        return MIXED_QUANTITIES
    raise ValueError(f"unknown scope: {scope!r}")


def _raw_values_for_cell(n, eta, scope, draw_start, draw_count, weight2_pair=(0, 1), seed_base=180814):
    """Raw (not summarized) per-draw quantity values for ONE (n, eta, scope)
    cell, over draw indices [draw_start, draw_start + draw_count).

    Returns a 2D np.ndarray of shape (draw_count, n_quantities), columns
    ordered per _quantities_for_scope(scope) -- the same "raw array now,
    summarize later" contract trainability/sweep.py::pooled_gradients_for_cell
    uses (reusing that SHAPE, not that code, since the quantities differ),
    so draw-chunks computed in separate processes can be concatenated and
    re-summarized exactly once by combine_pooled_cells below.

    For each draw:
      1. draw_rng = trainability.rng.get_rng(seed_base, scope, n, draw) --
         this repo's existing deterministic RNG substream utility, reused
         verbatim rather than hand-rolled a second time. `hardness`
         importing from `trainability` here is a deliberate cross-package
         reuse of a generic utility (not trainability-specific logic).
      2. thetas = sample_thetas(draw_rng, n).
      3. The LOSSLESS reference distribution for this draw is computed via
         the SAME loss-model function used for every other eta, called with
         eta=1.0 -- not a separate "lossless" code path, so the eta=1.0 row
         in the final CSV is provably consistent with every other row.
      4. product_of_marginals_baseline is derived from that SAME draw's
         lossless reference ONCE (18-CONTEXT.md's explicit lock:
         "computed once, from the lossless target distribution, not
         recomputed per eta") -- computed here, inside the per-draw loop,
         before the (single) requested-eta computation below, never inside
         a per-eta loop.
      5. For the REQUESTED eta (this cell's actual eta, which may or may not
         be 1.0): the lossy distribution is computed via the same loss-model
         function, then TVD-to-lossless, TVD-to-uniform,
         TVD-to-product-marginals, alpha, and (mixed only)
         herald_failure_prob are derived from it.
    """
    if scope not in ("weight1", "mixed"):
        raise ValueError(f"unknown scope: {scope!r}")
    if not (0.0 <= eta <= 1.0):
        raise ValueError(f"eta must be in [0.0, 1.0], got {eta!r}")

    quantities = _quantities_for_scope(scope)
    rows = []
    for draw in range(draw_start, draw_start + draw_count):
        draw_rng = get_rng(seed_base, scope, n, draw)
        thetas = sample_thetas(draw_rng, n)

        if scope == "weight1":
            lossless_dist, _residual, _perf = photonic_iqp_distribution_lossy(n, thetas, eta=1.0)
        else:
            i, j = weight2_pair
            lossless_dist, _residual, _herald_fail, _perf = photonic_weight2_iqp_distribution_lossy(
                n, i, j, thetas, eta=1.0
            )

        # Product-of-marginals computed ONCE per draw, from this draw's own
        # lossless (eta=1.0) reference -- 18-CONTEXT.md's explicit lock.
        product_marginals = product_of_marginals_baseline(lossless_dist, n)
        uniform = uniform_baseline(n)

        if scope == "weight1":
            lossy_dist, _residual, _perf = photonic_iqp_distribution_lossy(n, thetas, eta=eta)
            herald_failure_prob = None
        else:
            i, j = weight2_pair
            lossy_dist, _residual, herald_failure_prob, _perf = photonic_weight2_iqp_distribution_lossy(
                n, i, j, thetas, eta=eta
            )

        values = {
            "tvd_to_lossless": total_variation_distance(lossy_dist, lossless_dist),
            "tvd_to_uniform": total_variation_distance(lossy_dist, uniform),
            "tvd_to_product_marginals": total_variation_distance(lossy_dist, product_marginals),
            "alpha": anticoncentration_alpha(lossy_dist, n),
        }
        if scope == "mixed":
            values["herald_failure_prob"] = herald_failure_prob

        rows.append([values[q] for q in quantities])

    return np.array(rows, dtype=np.float64)


def _summarize_raw(raw_array, scope):
    """(mean, std) per quantity over a raw per-draw array's rows -- mirrors
    trainability/stats.py::summarize_gradient_samples's shape (a dict of
    named summary stats), for this phase's own quantity set."""
    quantities = _quantities_for_scope(scope)
    n_draws = raw_array.shape[0]
    summary = {"n_draws": n_draws}
    for idx, name in enumerate(quantities):
        col = raw_array[:, idx]
        summary[f"{name}_mean"] = float(np.mean(col))
        summary[f"{name}_std"] = float(np.std(col))
    if scope == "mixed":
        # herald_success_rate is reported as a mean only (CSV contract,
        # loss_sweep.py) -- it's exactly 1 - herald_failure_prob per draw,
        # so its std is redundant with herald_failure_prob_std.
        summary["herald_success_rate_mean"] = 1.0 - summary["herald_failure_prob_mean"]
    return summary


def pooled_cell_for_neta(n, eta, scope, draw_start, draw_count, weight2_pair=(0, 1), seed_base=180814):
    """Compute, for ONE (n, eta, generator_scope) cell, all of HARD-05's/
    HARD-07's required per-cell quantities in one place: TVD-to-lossless-
    reference, TVD-to-uniform-baseline, TVD-to-product-of-marginals-baseline,
    the anticoncentration parameter alpha, and (mixed scope only)
    herald_failure_prob/herald_success_rate -- pooled/averaged across
    draw_count independent random-theta draws starting at draw_start.

    Returns (summary, raw):
      - summary: dict of {"n_draws": int, "<quantity>_mean": float,
        "<quantity>_std": float, ...} (mixed scope also gets
        "herald_success_rate_mean").
      - raw: the 2D np.ndarray this draw sub-range produced (see
        _raw_values_for_cell) -- callers doing chunked/resumable execution
        (loss_sweep.py) save this directly to a .npy file so multiple
        draw-chunks from separate processes can later be concatenated and
        re-summarized exactly once via combine_pooled_cells, without losing
        or double-counting any already-completed draws.
    """
    raw = _raw_values_for_cell(
        n, eta, scope, draw_start, draw_count, weight2_pair=weight2_pair, seed_base=seed_base
    )
    summary = _summarize_raw(raw, scope)
    return summary, raw


def combine_pooled_cells(raw_arrays, scope):
    """Concatenate raw per-draw arrays from separate draw-chunks (each one
    the `raw` half of a pooled_cell_for_neta(...) call over a draw
    sub-range) and summarize ONCE over the full concatenated draw range --
    identical math to calling pooled_cell_for_neta once over the whole draw
    range in a single process. Mirrors gradient_variance_sweep.py's
    combine_chunks concatenation logic."""
    combined = np.concatenate(raw_arrays, axis=0)
    return _summarize_raw(combined, scope)
