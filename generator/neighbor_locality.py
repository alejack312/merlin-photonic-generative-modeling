import torch
import torch.nn.functional as Fnn
from torch.func import jacrev
from scipy.stats import mannwhitneyu


def compute_jacobian(gen, z: torch.Tensor) -> torch.Tensor:
    """Full Jacobian d(output)/d(parameters) at a fixed latent input z.

    Row i of the returned (K, P) matrix already corresponds to output index i
    post-permutation: NaturallyOrderedGenerator.forward applies self.perm
    before returning (self.base(z)[:, self.perm]), so this differentiates
    that same forward and the permutation is baked into row order. Callers
    must NOT reapply any permutation to J's rows.

    z must be shape (1, LATENT_DIM) -- one latent draw. gen must already be
    .eval()'d by the caller (this function does not call .eval() itself).

    Deviation from the naive functional_call-only recipe (07-RESEARCH.md /
    07-01-PLAN.md's original sketch): verified live that plain
    `functional_call(gen, params, (z,))` under `jacrev` silently returns an
    ALL-ZERO Jacobian for MerLin's QuantumLayer, with no error. Root cause:
    QuantumLayer._setup_parameters_from_custom populates a plain Python list
    (`quantum_layer.thetas`) once at construction, and forward() reads
    trainable parameters from that list directly on every call -- not from
    the module's named-parameter attributes. functional_call only swaps the
    named-parameter attributes (self.LI_simple / self.RI_simple), so it
    never reaches `.thetas`, and the substituted parameters never enter the
    circuit computation at all. Fix: also monkey-patch `quantum_layer.thetas`
    to point at the traced parameter tensors for the duration of each call,
    restoring the original list afterward. Verified: with this patch, J is
    correctly nonzero and `gen(z)` output under the patch matches the plain
    unpatched forward exactly (same values, real gradient dependency).
    """
    qlayer = gen.base.quantum_layer
    param_names = [n for n, _ in qlayer.named_parameters()]
    params = {n: p.detach().clone() for n, p in qlayer.named_parameters()}

    def f(p):
        original_thetas = qlayer.thetas
        qlayer.thetas = [p[n] for n in param_names]
        try:
            q = gen(z)
        finally:
            qlayer.thetas = original_thetas
        return q[0]

    J_dict = jacrev(f)(params)
    K = next(iter(J_dict.values())).shape[0]
    J = torch.cat([J_dict[k].reshape(K, -1) for k in param_names], dim=1)
    return J


def adjacent_and_random_cosines(J: torch.Tensor, seed: int | None = None) -> tuple[torch.Tensor, torch.Tensor]:
    """Signed cosine similarity between adjacent Jacobian rows (list-neighbors
    under the natural/radius-sort ordering) vs. an equal-sized sample of
    random non-adjacent row pairs.

    Signed, not absolute: "list-neighbors move together" means the same
    direction of parameter-sensitivity, not merely coupled magnitude -- an
    anti-correlated neighbor pair scores negative cosine and counts as
    evidence AGAINST the mechanism claim, not for it. Do not use .abs().
    """
    K = J.shape[0]
    if K < 4:
        raise ValueError(
            f"K={K} is too small: no non-adjacent row pairs exist (abs(i-j) > 1 "
            "is unsatisfiable for K < 4), so the random-pair rejection sampling "
            "below would loop forever."
        )
    adj_i = torch.arange(K - 1)
    adj_cos = Fnn.cosine_similarity(J[adj_i], J[adj_i + 1], dim=1)

    n_random = K - 1
    g = torch.Generator().manual_seed(seed) if seed is not None else None
    rand_pairs = set()
    while len(rand_pairs) < n_random:
        i, j = torch.randint(0, K, (2,), generator=g).tolist()
        if abs(i - j) > 1:
            rand_pairs.add((min(i, j), max(i, j)))
    ri = torch.tensor([p[0] for p in rand_pairs])
    rj = torch.tensor([p[1] for p in rand_pairs])
    rand_cos = Fnn.cosine_similarity(J[ri], J[rj], dim=1)
    return adj_cos, rand_cos


def neighbor_locality_check(adj_cos: torch.Tensor, rand_cos: torch.Tensor, min_effect: float = 0.10) -> dict:
    """Two-condition pass/fail: adjacent-vs-random cosine similarity must be
    both statistically significant (Mann-Whitney U, one-sided) AND clear a
    stated practically-meaningful effect-size bar -- mirrors
    generator/train.py's decreasing_trend_check, this project's only other
    precedent for "scripted, not eyeballed" statistical evidence, which uses
    the same two-condition (direction + effect-size threshold) shape rather
    than a bare p-value.

    min_effect=0.10 mirrors decreasing_trend_check's own 10%-relative-drop
    effect-size bar (see 07-01-PLAN.md's objective section for the full
    rationale): pooling 20 draws x 461 pairs/group = 9,220 samples/group
    gives very high statistical power, so p < 0.05 alone would be a weak
    bar -- reusing this codebase's existing 10% threshold keeps both
    "is this a real effect" checks in the project consistent with each other.
    """
    stat, p_value = mannwhitneyu(adj_cos.numpy(), rand_cos.numpy(), alternative="greater")
    mean_diff = adj_cos.mean().item() - rand_cos.mean().item()
    passed = bool(mean_diff >= min_effect and p_value < 0.05)
    return {
        "adj_mean": adj_cos.mean().item(),
        "rand_mean": rand_cos.mean().item(),
        "mean_diff": mean_diff,
        "p_value": float(p_value),
        "min_effect": min_effect,
        "passed": passed,
    }
