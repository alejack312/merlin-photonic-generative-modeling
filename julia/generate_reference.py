"""Reference-distribution generator for Phase 19's Julia cross-checks
(VERIFY-02/VERIFY-03/VERIFY-04, Plans 19-02..19-05).

Calls this repo's already-tested exact/lossy distribution functions
directly -- no new physics, no new Python logic beyond wiring and file I/O
-- and writes plain `bitstring,probability` CSVs under
`results/julia_reference/` for the independently-built Julia scripts in
Plans 19-02..19-05 to diff against.

Run: `python julia/generate_reference.py` (idempotent -- overwrites the same
files every run with the same deterministic inputs).
"""

import csv
import os
import sys

# Allow running as `python julia/generate_reference.py` directly (repo root
# is not automatically on sys.path in that invocation form, unlike
# `python -m julia.generate_reference`).
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from iqp_photonic_encoding import (
    exact_qubit_iqp_distribution,
    photonic_iqp_distribution,
    photonic_weight2_iqp_distribution,
)

OUT_DIR = os.path.join(os.path.dirname(__file__), "..", "results", "julia_reference")


def _write_csv(dist, path, header_comments=None):
    """Write a {bitstring: probability} dict as a sorted 2-column CSV, with
    optional `# key=value` comment lines at the top (for recording residual
    /herald_failure_prob/thetas/eta -- literal values Julia needs to
    reproduce the same reference, not just a seed)."""
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", newline="") as f:
        if header_comments:
            for line in header_comments:
                f.write(f"# {line}\n")
        writer = csv.writer(f)
        writer.writerow(["bitstring", "probability"])
        for bitstring in sorted(dist.keys()):
            # float(...) first: some upstream functions (e.g.
            # exact_qubit_iqp_distribution) return np.float64 values, whose
            # repr() is "np.float64(...)" -- not a bare number a Julia CSV
            # parser could read. repr() of a plain Python float preserves
            # full round-trip precision without that wrapper.
            writer.writerow([bitstring, repr(float(dist[bitstring]))])


def _assert_sums_to(dist, target, tol, label):
    total = sum(dist.values())
    if abs(total - target) > tol:
        raise AssertionError(
            f"{label}: probabilities sum to {total!r}, expected {target!r} (tol={tol!r})"
        )


# ---------------------------------------------------------------------------
# Task 1: exact-distribution references (VERIFY-02 / VERIFY-03 targets)
# ---------------------------------------------------------------------------

def generate_exact_references():
    # --- VERIFY-02: qubit-side exact references ---
    qubit_n2 = exact_qubit_iqp_distribution(n=2, thetas=[0.3, 1.1])
    _assert_sums_to(qubit_n2, 1.0, 1e-9, "qubit_n2")
    _write_csv(qubit_n2, os.path.join(OUT_DIR, "qubit_n2.csv"))

    qubit_n3 = exact_qubit_iqp_distribution(n=3, thetas=[0.3, 1.1, 0.75])
    _assert_sums_to(qubit_n3, 1.0, 1e-9, "qubit_n3")
    _write_csv(qubit_n3, os.path.join(OUT_DIR, "qubit_n3.csv"))

    # --- VERIFY-03: weight-1 photonic references ---
    weight1_n2, residual_w1_n2 = photonic_iqp_distribution(n=2, thetas=[0.3, 1.1])
    assert residual_w1_n2 < 1e-9, f"weight1_n2 residual too large: {residual_w1_n2!r}"
    _assert_sums_to(weight1_n2, 1.0 - residual_w1_n2, 1e-9, "weight1_n2")
    _write_csv(
        weight1_n2,
        os.path.join(OUT_DIR, "weight1_n2.csv"),
        header_comments=[f"residual={float(residual_w1_n2)!r}"],
    )

    weight1_n3, residual_w1_n3 = photonic_iqp_distribution(n=3, thetas=[0.3, 1.1, 0.75])
    assert residual_w1_n3 < 1e-9, f"weight1_n3 residual too large: {residual_w1_n3!r}"
    _assert_sums_to(weight1_n3, 1.0 - residual_w1_n3, 1e-9, "weight1_n3")
    _write_csv(
        weight1_n3,
        os.path.join(OUT_DIR, "weight1_n3.csv"),
        header_comments=[f"residual={float(residual_w1_n3)!r}"],
    )

    # --- VERIFY-03: weight-2 locked-gate reference ---
    # Same case as tests/test_iqp_photonic_encoding.py::test_wt2_tvd_gate_n2_theta_pi_4
    # (n=2, i=0, j=1, thetas=[0.0, 0.0] -- photonic_weight2_iqp_distribution folds
    # +pi/4 onto thetas[i]/thetas[j] internally, realizing a pure weight-2 pair
    # term at pair angle pi/4). NOTE: dist/residual are already renormalized by
    # (1 - herald_failure_prob) inside photonic_weight2_iqp_distribution, so
    # sum(dist) + residual == 1.0 -- herald_failure_prob is a separate,
    # never-merged number, recorded here only as a header comment.
    n, i, j = 2, 0, 1
    thetas = [0.0, 0.0]
    weight2_locked_n2, residual_w2, herald_failure_prob = photonic_weight2_iqp_distribution(n, i, j, thetas)
    _assert_sums_to(weight2_locked_n2, 1.0 - residual_w2, 1e-9, "weight2_locked_n2")
    print(f"weight2_locked_n2: herald_failure_prob={float(herald_failure_prob)!r}, residual={float(residual_w2)!r}")
    _write_csv(
        weight2_locked_n2,
        os.path.join(OUT_DIR, "weight2_locked_n2.csv"),
        header_comments=[
            f"herald_failure_prob={float(herald_failure_prob)!r}",
            f"residual={float(residual_w2)!r}",
            f"n={n} i={i} j={j} thetas={thetas!r}",
        ],
    )

    print("qubit_n2 sum:", sum(qubit_n2.values()))
    print("weight2_locked_n2 sample probs:", dict(list(sorted(weight2_locked_n2.items()))[:2]))


if __name__ == "__main__":
    generate_exact_references()
    print("Done. Exact-case reference CSVs written to", os.path.abspath(OUT_DIR))
