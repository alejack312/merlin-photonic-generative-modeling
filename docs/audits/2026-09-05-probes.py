"""Read-only reproductions for the September 5 audit; run from repo root."""
import json
import math
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import numpy as np
from merlin_iqp.encoding.dual_rail import dual_rail_photonic_iqp_distribution
from merlin_iqp.encoding.iqp_photonic import photonic_iqp_distribution, exact_qubit_iqp_distribution
from merlin_iqp.trainability.curve_fit import fit_and_compare
from scripts.v3_trainability.trainability_analysis import fit_verdict_to_plateau_label


def main():
    result = {}
    cases = []
    for theta in [0.0, 0.3, math.pi / 2]:
        p, _ = photonic_iqp_distribution(1, [theta])
        q, _ = dual_rail_photonic_iqp_distribution(1, [theta])
        cases.append(dict(theta=theta, polarization=p, dual_rail=q,
                          tvd=0.5 * sum(abs(p.get(k, 0)-q.get(k, 0)) for k in set(p)|set(q))))
    result['encoding'] = cases
    ns = np.arange(2, 9)
    ys = 1 - np.exp(-0.8 * ns)
    fit = fit_and_compare(ns, ys)
    result['increasing_variance'] = dict(values=ys.tolist(), exp_params=list(fit['exp']['params']),
        verdict=fit['verdict'], plateau_label=fit_verdict_to_plateau_label(fit))
    factorization = []
    for n in [2, 3, 5, 8]:
        theta = np.linspace(0.13, 0.91, n)
        p = exact_qubit_iqp_distribution(n, list(theta), pair_thetas={(0, 1): math.pi/4})
        pair = exact_qubit_iqp_distribution(2, list(theta[:2]), pair_thetas={(0, 1): math.pi/4})
        errors = []
        for bits, probability in p.items():
            q = pair[bits[:2]]
            for k in range(2, n):
                q *= math.sin(theta[k])**2 if bits[k] == '1' else math.cos(theta[k])**2
            errors.append(abs(probability-q))
        factorization.append(dict(n=n, max_error=max(errors)))
    result['mixed_pair_times_singles'] = factorization
    result['throughput_formula'] = {str(eta): [[n]+[1/(eta**(n+2*k)*(2/27)**k) for k in range(4)]
        for n in [2,4,6,8]] for eta in [0.9,0.6]}
    print(json.dumps(result, indent=2))


if __name__ == '__main__':
    main()
