"""Independent R1 oracles; R1_MUTATION activates deliberate failing pipelines."""
from __future__ import annotations

from dataclasses import replace
import math
import os

import numpy as np
import pytest

from merlin_iqp.deploy.noisy import NoisyProfile
from merlin_iqp.deploy import noisy_fock as model
from test_r1_noisy_profile_nulls import FIXTURES, _run_existing_ideal_full_fock, _tvd


@pytest.fixture(autouse=True)
def deliberate_mutation(monkeypatch):
    mutation = os.environ.get("R1_MUTATION", "")
    if mutation == "wrong_p2":
        monkeypatch.setattr(model, "p2_from_g2", lambda g2, **kw: g2)
    elif mutation == "wrong_eta_exponent":
        original = model.run_noisy_fock_density
        def wrong(*args, **kwargs):
            result = original(*args, **kwargs)
            profile = args[3]
            return replace(result, accepted_mass=result.accepted_mass * profile.eta)
        monkeypatch.setattr(model, "run_noisy_fock_density", wrong)
    elif mutation == "posthoc_loss":
        original = model.run_noisy_fock_density
        def wrong(*args, **kwargs):
            profile = args[3]
            result = original(*args[:3], replace(profile, eta=1.0), **kwargs)
            return replace(result, accepted_mass=result.accepted_mass * profile.eta**args[0])
        monkeypatch.setattr(model, "run_noisy_fock_density", wrong)
    elif mutation in {"dropped_normalization", "ideal_corruption", "detector_mass"}:
        original = model.run_noisy_fock_density
        def wrong(*args, **kwargs):
            result = original(*args, **kwargs)
            if mutation == "dropped_normalization":
                return replace(result, distribution={k: v * result.accepted_mass for k, v in result.distribution.items()})
            if mutation == "ideal_corruption":
                return replace(result, distribution={"0" * args[0]: 1.0})
            if args[3].detector == "threshold":
                return replace(result, observed_outcomes={k: 0.9*v for k, v in result.observed_outcomes.items()})
            return result
        monkeypatch.setattr(model, "run_noisy_fock_density", wrong)


def profile(*, eta=1.0, p2=0.0, detector="PNR", c=1, visibility=1.0):
    return NoisyProfile("oracle", visibility, 2*p2/(1+p2)**2, eta, detector, c)


def run(fixture, p):
    return model.run_noisy_fock_density(fixture.n, fixture.singles, fixture.pairs, p)


@pytest.mark.parametrize("fixture", FIXTURES, ids=lambda f: f.name)
def test_null_1(fixture):
    ideal = _run_existing_ideal_full_fock(fixture)
    actual = run(fixture, profile())
    gap = _tvd(actual.distribution, ideal.distribution)
    mass_gap = abs(actual.accepted_mass - ideal.acceptance)
    print(f"NULL1 {fixture.name}: TVD={gap:.17g}; acceptance gap={mass_gap:.17g}")
    assert gap < 1e-9
    assert mass_gap < 1e-9


@pytest.mark.parametrize("fixture", FIXTURES, ids=lambda f: f.name)
def test_null_2(fixture):
    ideal = run(fixture, profile())
    actual = run(fixture, profile(eta=0.152))
    gap = _tvd(actual.distribution, ideal.distribution)
    mass_gap = abs(actual.accepted_mass - ideal.accepted_mass * 0.152**fixture.n)
    print(f"NULL2 {fixture.name}: TVD={gap:.17g}; acceptance gap={mass_gap:.17g}")
    assert gap < 1e-9
    assert mass_gap < 1e-9
    assert abs(actual.accepted_mass - 1) > 1e-3
    assert _tvd(ideal.distribution, {format(i, f"0{fixture.n}b"): 2**-fixture.n for i in range(2**fixture.n)}) > 1e-3


def pulse_oracle(n, p2, eta):
    # Owner's one-pulse function, independently convolved (no model helpers).
    pulse = [(1-p2)*(1-eta)+p2*(1-eta)**2,
             (1-p2)*eta+2*p2*eta*(1-eta), p2*eta**2]
    result = np.array([1.0])
    for _ in range(n):
        result = np.convolve(result, pulse)
    return dict(enumerate(result))


@pytest.mark.parametrize("n", [2, 3])
@pytest.mark.parametrize("eta", [0.5, 1.0, 0.152])
def test_owner_pulse_oracle(n, eta):
    actual = model.run_noisy_fock_density(n, (0.0,)*n, (), profile(p2=0.1, eta=eta, c=n))
    expected = pulse_oracle(n, 0.1, eta)
    gap = max(abs(actual.detected_photon_masses.get(k, 0)-v) for k, v in expected.items())
    print(f"PULSE n={n} eta={eta}: max gap={gap:.17g}; masses={actual.detected_photon_masses}")
    assert gap < 1e-12
    if eta == 1:
        assert actual.detected_photon_masses.get(0, 0) == 0
    if n == 2 and eta == 0.5:
        assert np.allclose(list(expected.values()), [.225625, .475, .27375, .025, .000625], atol=1e-12)


def test_g2_loss_changes_conditional_distribution():
    fixture = FIXTURES[1]
    left = run(fixture, profile(p2=0.1, c=1))
    right = run(fixture, profile(p2=0.1, eta=0.152, c=1))
    gap = _tvd(left.distribution, right.distribution)
    print(f"G2 LOSS {fixture.name}: conditional TVD={gap:.17g}")
    assert gap > 1e-3


def test_no_gate_g2_changes_true_n_detected_conditional():
    fixture = FIXTURES[0]
    lossless = run(fixture, profile(p2=.1))
    lossy = run(fixture, profile(p2=.1, eta=.152))
    gap = _tvd(lossless.conditional_on_detected_photons(fixture.n),
               lossy.conditional_on_detected_photons(fixture.n))
    print(f"G2 LOSS no_gate_n2: true-n-detected conditional TVD={gap:.17g}")
    assert gap > 1e-3


def test_threshold_merges_and_conserves_mass():
    fixture = FIXTURES[0]
    pnr = run(fixture, profile(p2=0.1, eta=0.5, c=2))
    threshold = run(fixture, profile(p2=0.1, eta=0.5, c=2, detector="threshold"))
    expected = {}
    merged = {}
    for state, mass in pnr.observed_outcomes.items():
        clicks = tuple(min(1, x) for x in state)
        expected[clicks] = expected.get(clicks, 0) + mass
        merged.setdefault(clicks, []).append(state)
    gap = max(abs(threshold.observed_outcomes.get(k, 0)-v) for k, v in expected.items())
    print(f"THRESHOLD max gap={gap:.17g}; mass gap={abs(sum(threshold.observed_outcomes.values())-sum(pnr.observed_outcomes.values())):.17g}; merges={ {k:v for k,v in merged.items() if len(v)>1} }")
    assert gap < 1e-12
    assert abs(sum(threshold.observed_outcomes.values())-pnr.retained_mass) < 1e-12
    assert any(len(states)>1 for states in merged.values())


@pytest.mark.parametrize("n", [2, 3])
@pytest.mark.parametrize("g2", [0, .00732, .019])
def test_ignored_mass_accounting(n, g2):
    p = NoisyProfile("accounting", 1, g2, 1, "PNR", 1)
    p2 = model.p2_from_g2(g2, assume_p1_plus_p2_normalized=True)
    expected = sum(math.comb(n,k)*p2**k*(1-p2)**(n-k) for k in range(2,n+1))
    actual = model.run_noisy_fock_density(n, (0.0,)*n, (), p)
    print(f"IGNORED n={n} g2={g2}: mass={actual.ignored_mass:.17g}; flagged={actual.ignored_mass_flagged}")
    assert abs(actual.ignored_mass-expected) < 1e-12
    assert abs(sum(actual.observed_outcomes.values())+actual.ignored_mass-1) < 1e-12
    assert actual.ignored_mass_flagged == (expected >= 1e-3)


def test_loss_kraus_coherence_and_completeness():
    basis = ((0,), (1,), (2,))
    operators = model.loss_kraus_operators(basis, 0, .37)
    assert np.allclose(sum(k.conj().T @ k for k in operators), np.eye(3), atol=1e-12)
    ket = np.array([0, 1, 1j])/np.sqrt(2)
    rho = np.outer(ket, ket.conj())
    result = sum(k @ rho @ k.conj().T for k in operators)
    assert np.isclose(np.trace(result), 1)
    assert np.isclose(result[1,2], rho[1,2]*.37**1.5)


def test_species_density_retains_coherence_and_is_positive():
    unitary = np.array([[1, 1], [1, -1]])/np.sqrt(2)
    basis, rho = model._propagated_species_density(unitary, (0,), .37)
    assert np.isclose(rho[basis.index((1,0)), basis.index((0,1))], .37/2)
    assert np.linalg.eigvalsh(rho).min() > -1e-12
    assert np.isclose(np.trace(rho), 1)


@pytest.mark.parametrize("visibility", [0, .4, 1])
def test_balanced_hom_analytic_limit(monkeypatch, visibility):
    # Same density construction on a solvable two-input balanced splitter.
    unitary = np.eye(4, dtype=complex)
    unitary[np.ix_([0,2],[0,2])] = np.array([[1,1],[1,-1]])/np.sqrt(2)
    monkeypatch.setattr(model, "circuit_unitary", lambda *args: unitary)
    actual = model.run_noisy_fock_density(2, (0,0), (), profile(visibility=visibility))
    coincidence = actual.observed_outcomes.get((1,0,1,0),0)
    bunch0 = actual.observed_outcomes.get((2,0,0,0),0)
    bunch1 = actual.observed_outcomes.get((0,0,2,0),0)
    gap = max(abs(coincidence-(1-visibility)/2),
              abs(bunch0-(1+visibility)/4), abs(bunch1-(1+visibility)/4))
    print(f"HOM V={visibility}: analytic max gap={gap:.17g}")
    assert gap < 1e-12


def test_cutoff_flag_and_truncated_mass_not_normalized():
    result = run(FIXTURES[0], profile(p2=.1, eta=.5, c=1))
    assert result.ignored_mass_flagged
    assert np.isclose(result.ignored_mass, .01)
    assert np.isclose(sum(result.observed_outcomes.values()), .99)
    assert np.isclose(result.accepted_mass+result.rejected_retained_mass+result.ignored_mass,1)
    # Omitted two-doubling branch contributes at every detected sector under loss.
    expected = pulse_oracle(2,.1,.5)
    omitted = .01*np.array([1,4,6,4,1])/16
    assert np.allclose([result.detected_photon_masses.get(k,0) for k in expected],
                       np.array(list(expected.values()))-omitted, atol=1e-12)


@pytest.mark.parametrize("fixture", FIXTURES, ids=lambda f: f.name)
def test_fully_distinguishable_analytic_limit(fixture):
    # With V=0 each primary photon has its own label. No multiphotons here.
    actual = run(fixture, profile(visibility=0))
    unitary = model.circuit_unitary(fixture.n, fixture.singles, fixture.pairs)
    expected = {(0,)*len(unitary): 1.0}
    for q in range(fixture.n):
        next_values = {}
        for state, mass in expected.items():
            for mode in range(len(unitary)):
                output = list(state)
                output[mode] += 1
                key = tuple(output)
                next_values[key] = next_values.get(key,0)+mass*abs(unitary[mode,2*q])**2
        expected = next_values
    gap = max(abs(actual.observed_outcomes.get(k,0)-v) for k,v in expected.items())
    print(f"V=0 {fixture.name}: independent categorical convolution max gap={gap:.17g}")
    assert gap < 1e-12


@pytest.mark.parametrize("mass,flagged", [(1e-3, True), (.999e-3, False)])
def test_ignored_mass_flag_boundary(mass, flagged):
    result = model.NoisyFockResult({}, 0, {}, {}, 1-mass, mass, 3, {})
    assert result.ignored_mass_flagged is flagged
