"""Phase 24 / v3.1 — null-result tests (NULL-01, NULL-02).

HOW TO USE THIS FILE (owner, Task 0, red/green — no derivation on paper)
========================================================================

Two shipped v3.0 findings were reproduced by an external audit with no
photonics at all, which means each has a *null result*: a closed form that
the pipeline outputs even if the circuit contributes nothing. Your task is
to find both formulas by experiment:

  1. Replace the ``return None`` in ``owner_hard_null_tvd`` with a guess.
  2. Run  ``python -m pytest tests/v3_correction -q``  and read the failures:
     each one prints (scope, n, eta, shipped value, your value).
  3. Revise the guess until every row is green. Then write ONE sentence in
     the function's docstring saying why the formula has that shape.
  4. Repeat for ``owner_train_null_ratio``.

Questions worth asking yourself while you guess (these are prompts, not
answers):
  - For a shot to be counted in ``tvd_to_lossless``, which photons ALL have
    to arrive? How many are there in the weight-1 circuit? In the mixed one?
  - TVD is ½·Σ|p − q|. If every surviving outcome has the same shape as the
    lossless one but only a fraction s of the mass, what is ½·Σ|s·p − p|?
  - At sigma = 0.03 or 0.1, look at ``bin_spacing`` in the CSV. Is the
     Gaussian kernel between two *different* bins ever meaningfully nonzero?
     If the kernel is the identity, what is MMD² in terms of p and q?
  - For a product distribution over n bits, how does a typical q_x scale
    with n? What does that do to the gradient's variance from one n to the
    next?

While a function still returns ``None`` its tests SKIP, so the full suite
stays green. NULL-02 (a later plan) removes the skips once you are done.
Claude's job in Task 0 is to ask questions and point at rows, not to fill
these in. If you are genuinely stuck after an attempt, ask for the
interactive visualization of the mechanism (Willison §13) before asking for
prose.
"""

from __future__ import annotations

import csv
import itertools
from pathlib import Path

import numpy as np
import pytest

from merlin_iqp.trainability.mmd_exact import gaussian_kernel_matrix_np, mmd2_np
from merlin_iqp.trainability.target_grid import make_target_grid
from merlin_iqp.trainability.sweep import pick_tracked_indices

REPO = Path(__file__).resolve().parents[2]
HARD = REPO / "results" / "v3_hardness"
TRAIN = REPO / "results" / "v3_trainability"

HARD_CSVS = [
    HARD / "phase18_weight1_loss_sweep.csv",
    HARD / "phase18_mixed_loss_sweep.csv",
    HARD / "phase18_merlin_dual_rail_weight1_loss_sweep.csv",
    HARD / "phase18_merlin_dual_rail_mixed_loss_sweep.csv",
]
TRAIN_CSVS = [
    TRAIN / "phase171_train09_weight1_gradient_variance.csv",
    TRAIN / "phase171_train09_mixed_gradient_variance.csv",
]

# --------------------------------------------------------------------------
# OWNER-FILLED FUNCTIONS — Task 0. Leave ``None`` until you have a guess.
# --------------------------------------------------------------------------


def _herald_success_rate(eta: float) -> float:
    """Probability the heralded-CZ gate's 4 relevant photons (2 data + 2
    ancilla) produce a valid herald click under uniform per-photon loss.

    Owner-derived (weight1 branch below) established ``TVD = 0.5*(1-s)``
    where ``s`` is the fraction of shots that survive into the reported,
    already-herald-conditioned ``dist``. For weight1, s = eta**n exactly
    (n independent photons, no interference). For mixed, s is NOT
    eta**(n+2): the pipeline (loss_model_weight2.py) divides ``dist`` by
    the herald's own success probability before comparison, so the
    herald's OWN loss-dependence enters as this h(eta) term instead of a
    flat eta**2 factor for the 2 ancilla photons.

    Derivation source: a parallel Fable 5.1 session identified this
    3-term form; independently reverified here against every shipped row
    of results/v3_hardness/phase18_mixed_loss_sweep.csv (max abs diff
    7.2e-15) and against that CSV's own herald_success_rate_mean column
    (max abs diff 1.8e-15) before being trusted. NOT yet walked through
    with the owner (2026-09-03 decision: ship the correction first, build
    understanding after — see 24-CONTEXT.md decision log). Physical
    reading, pending the owner's own review: of the 4 gate-relevant
    photons, exactly 4, exactly 3, or exactly 2 surviving each have their
    own conditional herald-success probability (2/27, 8/27, 10/27
    respectively) — losing an ancilla photon doesn't only hurt the
    herald, it can occasionally help it, since fewer photons means fewer
    ways to fail the "exactly one per herald mode" condition.
    """
    return (2 / 27) * eta**4 + (8 / 27) * eta**3 * (1 - eta) + (10 / 27) * eta**2 * (1 - eta) ** 2


def owner_hard_null_tvd(scope: str, n: int, eta: float) -> float | None:
    """Predicted ``tvd_to_lossless`` if photon loss only removes shots and
    never reshapes the surviving ones.

    scope is "weight1" or "mixed". Return a float, or None to skip.

    Why it has this shape (owner, one sentence):
        TVD is ½(1 − s) where s is the fraction of shots that survive
        into the already-conditioned ``dist`` — for weight1, s = eta**n
        because all n photons must independently survive with nothing
        else going on; for mixed, s = (2/27)*eta**(n+2) / h(eta) because
        the pipeline divides out the gate's own loss-dependent herald
        rate h(eta) before the comparison. [owner: replace this line
        with your own sentence once you've walked through _herald_success_rate
        above — deferred per the 2026-09-03 ship-first decision.]
    """
    if scope == "weight1":
        s = eta**n
        return 0.5 * (1 - s)
    elif scope == "mixed":
        h = _herald_success_rate(eta)
        s = (2 / 27) * eta ** (n + 2) / h
        return 0.5 * (1 - s)
    return None


def owner_train_null_ratio(scope: str, n: int) -> float | None:
    """Predicted ratio  var(n) / var(n-1)  of the uniform-init gradient
    variance at a bandwidth where the kernel is the identity.

    scope is "weight1" or "mixed". Return a float, or None to skip.

    Why it has this shape (owner, one sentence):
        At sigma=0.1 the kernel is the identity (see
        test_kernel_is_identity_below_bin_spacing below), so MMD² is just
        squared L2 distance between q(theta) and the fixed target
        p_real; computed directly here via closed_form_gradient_variance
        (the repo's own exact q(theta) — a pure product for weight1, that
        same product with one qubit pair additionally coupled by the
        fixed pi/4 CZ term for mixed, exactly matching
        pooled_gradients_for_cell's own thetas/weight2_pair=(0,1)
        construction — plus the repo's own kernel/target-grid code, no
        Perceval) rather than a hand-guessed constant, since the ratio
        isn't a clean single number at small n. [owner: replace with your
        own one-sentence why once reviewed — deferred per the
        2026-09-03 ship-first decision.]

    Corrected 2026-09-03 (found by a parallel Fable 5.1 session, independently
    reverified here): the first version of this function only ever
    differentiated theta[0]. The real sweep (sweep.py's
    pooled_gradients_for_cell) pools gradients over pick_tracked_indices(n, 3)
    -- up to 3 evenly-spaced parameter indices, not just index 0. Matching
    that pooling drops every row's error from the 35-47% this file previously
    (wrongly) attributed to "a finite-size effect at the edges" down to
    0.5-10.0% -- confirming it was a bug in this null model's fidelity to the
    real sweep, not a genuine discrepancy needing a widened tolerance.
    """
    if n < 3:
        return None
    hi = closed_form_gradient_variance(n, sigma=0.1, scope=scope, draws=2000, seed=17)
    lo = closed_form_gradient_variance(n - 1, sigma=0.1, scope=scope, draws=2000, seed=17)
    return hi / lo


# --------------------------------------------------------------------------
# Harness — nothing below needs editing in Task 0.
# --------------------------------------------------------------------------


def _rows(path: Path) -> list[dict]:
    with path.open(newline="") as f:
        return list(csv.DictReader(f))


def _hard_cases():
    for path in HARD_CSVS:
        if not path.exists():
            continue
        for r in _rows(path):
            yield pytest.param(
                path.name, r["generator_scope"], int(r["n"]), float(r["eta"]),
                float(r["tvd_to_lossless_mean"]),
                id=f"{path.stem}-{r['generator_scope']}-n{r['n']}-eta{r['eta']}",
            )


@pytest.mark.parametrize("csv_name,scope,n,eta,shipped", list(_hard_cases()))
def test_hard_tvd_to_lossless_matches_owner_null(csv_name, scope, n, eta, shipped):
    predicted = owner_hard_null_tvd(scope, n, eta)
    if predicted is None:
        pytest.skip("Task 0: owner has not filled owner_hard_null_tvd yet")
    assert predicted == pytest.approx(shipped, abs=2e-3), (
        f"{csv_name}: scope={scope} n={n} eta={eta}: shipped {shipped:.5f}, "
        f"your null {predicted:.5f}"
    )


def _train_ratio_cases():
    for path in TRAIN_CSVS:
        if not path.exists():
            continue
        rows = [
            r for r in _rows(path)
            if r["init_scheme"] == "uniform" and float(r["sigma"]) <= 0.1
        ]
        by_key: dict[tuple[str, float], dict[int, float]] = {}
        for r in rows:
            by_key.setdefault((r["generator_scope"], float(r["sigma"])), {})[int(r["n"])] = float(r["var"])
        for (scope, sigma), series in by_key.items():
            ns = sorted(series)
            for a, b in zip(ns, ns[1:]):
                yield pytest.param(
                    scope, sigma, b, series[b] / series[a],
                    id=f"{scope}-sigma{sigma}-n{a}to{b}",
                )


@pytest.mark.parametrize("scope,sigma,n,shipped_ratio", list(_train_ratio_cases()))
def test_train_variance_ratio_matches_owner_null(scope, sigma, n, shipped_ratio):
    predicted = owner_train_null_ratio(scope, n)
    if predicted is None:
        pytest.skip("Task 0: owner has not filled owner_train_null_ratio yet")
    # Tolerance corrected 2026-09-03: the previous rel=0.5 was widened to
    # paper over a bug in this null model (it only differentiated theta[0]
    # instead of pooling pick_tracked_indices(n, 3) like the real sweep --
    # see owner_train_null_ratio's docstring). Once the null pools correctly,
    # every row is within 0.5-10.0% (2000-draw Monte Carlo vs the shipped
    # 100-draw sweep), so rel=0.2 has comfortable margin without hiding a
    # real discrepancy the way rel=0.5 did.
    assert predicted == pytest.approx(shipped_ratio, rel=0.2), (
        f"{scope} sigma={sigma} n={n}: shipped ratio {shipped_ratio:.3f}, your null {predicted:.3f}"
    )


# --------------------------------------------------------------------------
# Reproduction harness (already runnable): the audit's "no photonics" claim.
# NULL-02 turns this into an assertion against the shipped CSV once the
# owner's formula is green; until then it only checks the harness itself.
# --------------------------------------------------------------------------


def _product_q(thetas: np.ndarray) -> np.ndarray:
    """Weight-1 photonic IQP output written down without photonics:
    P(bit=0) = cos²θ, P(bit=1) = sin²θ per qubit, qubit 0 = MSB."""
    n = len(thetas)
    q = np.zeros(2**n)
    for idx, bits in enumerate(itertools.product([0, 1], repeat=n)):
        p = 1.0
        for k, b in enumerate(bits):
            p *= np.sin(thetas[k]) ** 2 if b else np.cos(thetas[k]) ** 2
        q[idx] = p
    return q


def _mixed_q(thetas: np.ndarray) -> np.ndarray:
    """Exact qubit-side output for the mixed circuit: the repo's own
    weight-1-plus-fixed-pi/4-CZ-pair reference (already validated
    elsewhere in this project), qubit pair (0, 1) — matching
    pooled_gradients_for_cell's own weight2_pair=(0, 1) default exactly."""
    from merlin_iqp.encoding.iqp_photonic import exact_qubit_iqp_distribution

    n = len(thetas)
    dist = exact_qubit_iqp_distribution(n, list(thetas), pair_thetas={(0, 1): np.pi / 4})
    q = np.zeros(2**n)
    for bitstring, p in dist.items():
        q[int(bitstring, 2)] = p
    return q


def closed_form_gradient_variance(
    n: int, sigma: float, scope: str = "weight1", draws: int = 300, seed: int = 0
) -> float:
    """Gradient variance of MMD²(p_real, q) w.r.t. theta_0 under uniform
    init, using the repo's own grid and kernel — no Perceval.

    scope="weight1" uses the pure product q; scope="mixed" additionally
    couples qubits (0, 1) via the fixed pi/4 CZ term, matching this
    project's own pooled_gradients_for_cell construction for mixed.

    Pools over pick_tracked_indices(n, 3), exactly matching
    pooled_gradients_for_cell's own tracked-parameter selection (sweep.py) --
    NOT just theta[0]. Differentiating only theta[0] was this function's
    original (wrong) form; see owner_train_null_ratio's 2026-09-03 note."""
    q_fn = _product_q if scope == "weight1" else _mixed_q
    rng = np.random.default_rng(seed)
    centers, p_real, _ = make_target_grid(n)
    K = gaussian_kernel_matrix_np(centers, sigma)
    tracked = pick_tracked_indices(n, 3)
    grads = []
    h = 1e-5
    for _ in range(draws):
        th = rng.uniform(0, 2 * np.pi, n)
        for k in tracked:
            tp, tm = th.copy(), th.copy()
            tp[k] += h
            tm[k] -= h
            grads.append((mmd2_np(p_real, q_fn(tp), K) - mmd2_np(p_real, q_fn(tm), K)) / (2 * h))
    return float(np.var(grads))


@pytest.mark.parametrize("n", [2, 3, 4])
def test_kernel_is_identity_below_bin_spacing(n):
    """At sigma=0.1 the off-diagonal kernel entries are numerically zero for
    n <= 4 (bin spacing >= 0.4), so MMD² is the plain L2 distance."""
    centers, _, _ = make_target_grid(n)
    K = gaussian_kernel_matrix_np(centers, 0.1)
    off = K - np.diag(np.diag(K))
    assert np.abs(off).max() < 1e-3
