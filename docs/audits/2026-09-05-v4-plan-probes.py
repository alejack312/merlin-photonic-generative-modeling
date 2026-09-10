"""Small independent probes of v4 plan revision 2; no study implementation.

Run from repository root with venv/Scripts/python.exe. Results go to stdout.
"""
import itertools
import json
import math
import importlib.metadata
import numpy as np
import perceval as pcvl
from perceval.components.core_catalog import PostProcessedControlledRotationsItem


def tvd(a, b):
    return float(np.abs(a - b).sum() / 2)


def ideal(n, singles, pairs):
    bits = np.array(list(itertools.product([0, 1], repeat=n)))
    spins = 1 - 2 * bits
    phase = spins @ np.array(singles)
    for (i, j), th in pairs.items():
        phase += th * spins[:, i] * spins[:, j]
    walsh = (-1.) ** (bits @ bits.T)
    return np.abs(walsh @ np.exp(1j * phase) / 2**n)**2


def fock(n, singles, pairs, V=1., g2=0., eta=1., sign=-1):
    p = pcvl.Processor('SLOS', 2*n + 4*len(pairs), noise=pcvl.NoiseModel(
        indistinguishability=V, g2=g2, transmittance=eta))
    for q, th in enumerate(singles):
        p.add(2*q, pcvl.BS.H())
        p.add(2*q+1, pcvl.PS(sign * 2 * th))
    for g, ((i, j), th) in enumerate(pairs.items()):
        for q in (i, j):
            p.add(2*q+1, pcvl.PS(sign*2*th))
        a = 2*n + 4*g
        mapping = dict(zip([2*i, 2*i+1, 2*j, 2*j+1, a, a+1, a+2, a+3], range(8)))
        p.add(mapping, PostProcessedControlledRotationsItem().build_circuit(n=2, alpha=float(4*th)))
    for q in range(n):
        p.add(2*q, pcvl.BS.H())
    for a in range(2*n, p.circuit_size):
        p.add_herald(a, 0)
    p.set_postselection(pcvl.PostSelect(' & '.join(f'[{2*q},{2*q+1}]==1' for q in range(n))))
    p.min_detected_photons_filter(n)
    p.with_input(pcvl.BasicState([1, 0]*n))
    result = p.probs()
    probs = np.zeros(2**n)
    for state, prob in result['results'].items():
        idx = sum(int(state[2*q+1]) << (n-1-q) for q in range(n))
        probs[idx] += float(prob)
    return probs, float(result['global_perf'])


def main():
    out = {'versions': {'numpy': np.__version__, 'perceval': importlib.metadata.version('perceval-quandela')}}
    th = .311
    rounded = round((4*th % (2*np.pi))/.1) % 63 * .1/4
    out['rounding_control_tvd'] = tvd(ideal(2,[.3,.7],{(0,1):th}), ideal(2,[.3,.7],{(0,1):rounded}))
    out['wrapped_theta_tvd'] = tvd(ideal(2,[.3,.7],{(0,1):.2}), ideal(2,[.3,.7],{(0,1):.2+np.pi/2}))
    rng = np.random.default_rng(17)
    angles = rng.uniform(-np.pi,np.pi,10000)
    key = lambda t: np.round((4*t % (2*np.pi))/.1) % 63
    out['nat_pair_zero_difference_fraction'] = float(np.mean(key(angles+1e-4)==key(angles-1e-4)))
    out['nat_evaluations_actual'] = sum((2*(2*n-1)+1)*150*5 for n in [4,6,8])
    # A CP map passing every product-state trace check may still increase trace.
    bell = np.array([1,0,0,1],dtype=complex)/np.sqrt(2)
    prep = [np.array([1,0]),np.array([0,1]),np.array([1,1])/np.sqrt(2),np.array([1,1j])/np.sqrt(2)]
    out['cp_counterexample_max_product_success'] = max(float(1.1*abs(np.vdot(bell,np.kron(a,b)))**2) for a in prep for b in prep)
    out['cp_counterexample_bell_success'] = 1.1
    out['trained_files_if_all_k'] = sum([4,6,8,10,16,20])*2*3*5
    out['ising_support'] = {}
    J = np.random.default_rng(4001).normal(size=19)
    for n in [4,6,8,10]:
        bits = np.array(list(itertools.product([0,1], repeat=n)))
        spins = 1 - 2*bits
        p = np.exp((spins[:,:-1]*spins[:,1:]) @ J[:n-1]); p /= p.sum()
        out['ising_support'][n] = {'size':int((p>1e-6).sum()), 'total':len(p), 'minimum':float(p.min())}
        if n == 4:
            # Sibling default parity initialization, adapted to exact target moments.
            singles = np.zeros(n)
            pair_theta = .1 * (p @ (spins[:,:-1]*spins[:,1:]))
            pp = {(i,i+1):float(t) for i,t in enumerate(pair_theta)}
            kernel = np.exp(-np.count_nonzero(bits[:,None,:] != bits[None,:,:],axis=2)/(2*(.5*np.sqrt(n))**2))
            def loss(s):
                delta = ideal(n,s,pp)-p
                return float(delta @ kernel @ delta)
            grad = []
            for i in range(n):
                s1=singles.copy(); s1[i]+=1e-5
                s2=singles.copy(); s2[i]-=1e-5
                grad.append((loss(s1)-loss(s2))/2e-5)
            out['parity_init_single_gradients'] = grad
            out['parity_init_odd_mass'] = float(ideal(n,singles,pp)[bits.sum(axis=1)%2==1].sum())
            out['target_odd_mass'] = float(p[bits.sum(axis=1)%2==1].sum())
    # Two post-selected gates reusing the same data rails, with fresh vacuum ancillas.
    u = np.array(PostProcessedControlledRotationsItem().build_circuit(n=2,alpha=1.2).compute_unitary(),dtype=complex)
    u1=np.eye(12,dtype=complex); u1[:8,:8]=u
    u2=np.eye(12,dtype=complex); ids=[0,1,2,3,8,9,10,11]; u2[np.ix_(ids,ids)]=u
    def logical_block(unitary):
        inputs=[(a,b) for a in (0,1) for b in (2,3)]
        return np.array([[unitary[r,a]*unitary[s,b]+unitary[r,b]*unitary[s,a] for a,b in inputs] for r,s in inputs])
    k=logical_block(u)
    out['end_only_vs_intermediate_projection_max_amplitude'] = float(np.max(np.abs(logical_block(u2@u1)-k@k)))
    singles=[.3,.7]; pairs={(0,1):.3}
    q, success = fock(2,singles,pairs)
    out['fock_correct_sign_tvd'] = tvd(q,ideal(2,singles,pairs))
    wrong, _ = fock(2,singles,pairs,sign=1)
    out['fock_plan_phase_sign_tvd'] = tvd(wrong,ideal(2,singles,pairs))
    for g2 in [0.,.025]:
        for eta in [1.,.5]:
            qn, sn = fock(2,singles,pairs,g2=g2,eta=eta)
            out[f'noise_g2={g2}_eta={eta}'] = {'success':sn,'tvd_from_ideal':tvd(qn,q), 'success_over_eta_n':sn/eta**2}
    for n in [2,3]:
        _, s0 = fock(n,[.3]*n,{(0,1):.3},g2=0.)
        _, s1 = fock(n,[.3]*n,{(0,1):.3},g2=.025)
        out[f'g2_source_success_ratio_n{n}'] = s1/s0
    assert out['fock_correct_sign_tvd'] < 1e-12
    assert out['fock_plan_phase_sign_tvd'] > .4
    assert out['rounding_control_tvd'] > .005
    assert out['wrapped_theta_tvd'] > .7
    assert out['nat_pair_zero_difference_fraction'] > .98
    assert out['nat_evaluations_actual'] == 51750
    assert out['trained_files_if_all_k'] == 1920
    assert all(row['size'] == row['total'] for row in out['ising_support'].values())
    assert out['noise_g2=0.0_eta=0.5']['tvd_from_ideal'] < 1e-12
    assert out['noise_g2=0.025_eta=0.5']['tvd_from_ideal'] > .008
    assert out['end_only_vs_intermediate_projection_max_amplitude'] > .4
    assert max(abs(g) for g in out['parity_init_single_gradients']) < 1e-8
    assert out['cp_counterexample_max_product_success'] < 1
    out['probe_assertions'] = 'PASS'
    from pathlib import Path
    encoded = json.dumps(out, indent=2)
    Path(__file__).with_name('2026-09-05-v4-plan-probe-results.json').write_text(encoded+'\n', encoding='utf-8')
    print(encoded)


if __name__ == '__main__':
    main()
