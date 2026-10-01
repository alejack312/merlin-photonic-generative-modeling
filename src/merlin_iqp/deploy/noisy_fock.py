"""Small-n representation A: hidden-label Fock density blocks and loss Kraus maps.

The source is an incoherent mixture of common/private label assignments. Each
assignment is a tensor product of density matrices for orthogonal species,
not a pure-state environment dilation. Labels persist through the whole circuit.
Uniform loss on every mode commutes with a passive unitary, so its Kraus map
is applied at the input. Source truncation precedes loss; omitted branches
are never recovered or renormalized. Only final detector conditioning is used.
"""
from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from itertools import product
import math
from typing import Sequence

import numpy as np

from .fock import _build_direct_processor, _valid_bitstring
from .noisy import NoisyProfile, IGNORED_MASS_FLAG_THRESHOLD, p2_from_g2

Occupation = tuple[int, ...]


@dataclass(frozen=True)
class NoisyFockResult:
    distribution: dict[str, float]
    accepted_mass: float
    observed_outcomes: dict[Occupation, float]
    detected_photon_masses: dict[int, float]
    retained_mass: float
    ignored_mass: float
    cutoff: int
    diagnostics: dict[str, object]

    @property
    def ignored_mass_flagged(self) -> bool:
        return self.ignored_mass >= IGNORED_MASS_FLAG_THRESHOLD

    @property
    def rejected_retained_mass(self) -> float:
        """Observable rejection, excluding the source branches outside cutoff."""
        return self.retained_mass - self.accepted_mass

    def conditional_on_detected_photons(self, photons: int) -> dict[Occupation, float]:
        """True PNR sector conditional; threshold clicks cannot supply this."""
        if self.diagnostics["detector"] != "PNR":
            raise ValueError("true photon-sector outcomes require PNR; threshold reports clicks")
        mass = self.detected_photon_masses.get(photons, 0.0)
        return {state: p/mass for state, p in self.observed_outcomes.items()
                if sum(state) == photons} if mass else {}


@lru_cache(maxsize=32)
def fock_basis(modes: int, cutoff: int) -> tuple[Occupation, ...]:
    """All number sectors 0..cutoff, including vacuum ancilla occupations."""
    def sector(m: int, photons: int):
        if m == 1:
            yield (photons,)
        else:
            for first in range(photons+1):
                for rest in sector(m-1, photons-first):
                    yield (first,)+rest
    return tuple(state for photons in range(cutoff+1) for state in sector(modes, photons))


def loss_kraus_operators(basis: Sequence[Occupation], mode: int, eta: float) -> tuple[np.ndarray, ...]:
    """K_l |r> = sqrt(C(r,l) eta^(r-l) (1-eta)^l) |r-l>."""
    if not math.isfinite(eta) or not 0 <= eta <= 1:
        raise ValueError("eta must be in [0,1]")
    indices = {state: index for index, state in enumerate(basis)}
    operators = []
    for lost in range(max(state[mode] for state in basis)+1):
        operator = np.zeros((len(basis), len(basis)), complex)
        for column, state in enumerate(basis):
            photons = state[mode]
            if photons < lost:
                continue
            output = list(state)
            output[mode] -= lost
            operator[indices[tuple(output)], column] = math.sqrt(
                math.comb(photons, lost)*eta**(photons-lost)*(1-eta)**lost)
        operators.append(operator)
    return tuple(operators)


def circuit_unitary(n: int, singles: Sequence[float], pairs: Sequence[tuple[int,int,float]]) -> np.ndarray:
    specs = tuple((i,j,float(theta),4*float(theta)) for i,j,theta in pairs)
    processor, _, _ = _build_direct_processor(n, singles, specs)
    unitary = np.asarray(processor.linear_circuit().compute_unitary(), dtype=complex)
    if not np.allclose(unitary.conj().T @ unitary, np.eye(len(unitary)), atol=1e-12):
        raise ValueError("passive circuit matrix is not unitary")
    return unitary


def _source_loss_density(input_modes: tuple[int, ...], eta: float) -> tuple[tuple[Occupation, ...], np.ndarray]:
    """Apply K rho K† on occupied input modes; other modes are in vacuum.

    Each species has at most one photon in any input mode in this source model.
    The local input basis (all subsets) is closed under every loss operator.
    """
    basis = tuple(product((0,1), repeat=len(input_modes)))
    rho = np.zeros((len(basis), len(basis)), complex)
    rho[-1,-1] = 1
    for mode in range(len(input_modes)):
        rho = sum(k @ rho @ k.conj().T for k in loss_kraus_operators(basis, mode, eta))
    return basis, rho


def _propagated_species_density(unitary: np.ndarray, input_modes: tuple[int, ...], eta: float) -> tuple[tuple[Occupation, ...], np.ndarray]:
    """U_Fock E_eta(rho) U_Fock†, retaining number-sector coherences.

    Repeated creation operators construct amplitudes independently of the
    Perceval many-photon probability oracle. Source inputs have distinct modes.
    """
    basis = fock_basis(len(unitary), len(input_modes))
    indices = {state: i for i,state in enumerate(basis)}
    source_basis, source_rho = _source_loss_density(input_modes, eta)
    transitions = np.zeros((len(basis), len(source_basis)), complex)
    vacuum = (0,)*len(unitary)
    for column, source in enumerate(source_basis):
        amplitudes = {vacuum: 1+0j}
        for local_mode, occupied in enumerate(source):
            if not occupied:
                continue
            propagated = {}
            for state, amplitude in amplitudes.items():
                for mode in range(len(unitary)):
                    coefficient = unitary[mode,input_modes[local_mode]]
                    if coefficient == 0:
                        continue
                    output = list(state)
                    output[mode] += 1
                    key = tuple(output)
                    propagated[key] = propagated.get(key,0j)+amplitude*coefficient*math.sqrt(output[mode])
            amplitudes = propagated
        for state, amplitude in amplitudes.items():
            transitions[indices[state],column] = amplitude
    rho = transitions @ source_rho @ transitions.conj().T
    trace = float(np.trace(rho).real)
    if abs(trace-1) > 1e-12 or not np.allclose(rho, rho.conj().T, atol=1e-12):
        raise ValueError(f"species density failed trace/Hermiticity: {trace}")
    return basis, rho


def _convolve_occupations(left: dict[Occupation,float], right: dict[Occupation,float]) -> dict[Occupation,float]:
    result = {}
    for a,pa in left.items():
        for b,pb in right.items():
            state = tuple(x+y for x,y in zip(a,b))
            result[state] = result.get(state,0)+pa*pb
    return result


def run_noisy_fock_density(
    n: int,
    singles: Sequence[float],
    pairs: Sequence[tuple[int,int,float]],
    profile: NoisyProfile,
) -> NoisyFockResult:
    """Source-once n=2,3 final-only density model, with absolute output mass.

    Desired photons independently choose a common species with probability
    sqrt(V), otherwise a pulse-private species. Thus two desired photons share
    a species with probability V (pair HOM limit). This is an explicit mixture
    convention, not a uniquely determined higher-order model from measured V.
    Every extra photon has a separate orthogonal label, including from its own
    desired photon. Brightness is not applied; the contract's N/A stays N/A.

    Factor blocks are supported on the full spatial Fock space. Their tensor
    products lie in total sectors <= n+c. This exact density factorization
    avoids allocating a redundant square over all species combinations.
    """
    if n not in (2,3):
        raise ValueError("representation A is scoped to n=2,3")
    unitary = circuit_unitary(n,singles,pairs)
    cutoff = profile.cutoff(n)
    p2 = p2_from_g2(profile.g2, assume_p1_plus_p2_normalized=True)
    common_probability = math.sqrt(profile.visibility)
    vacuum = (0,)*len(unitary)
    species_cache = {}
    max_density_bytes = 0

    def species_probabilities(modes):
        nonlocal max_density_bytes
        if modes not in species_cache:
            basis,rho = _propagated_species_density(unitary,modes,profile.eta)
            max_density_bytes = max(max_density_bytes,rho.nbytes)
            probabilities = np.real(np.diag(rho))
            if np.min(probabilities) < -1e-12:
                raise ValueError("negative species probability")
            species_cache[modes] = {state: float(p) for state,p in zip(basis,probabilities) if p > 0}
        return species_cache[modes]

    outcomes = {}
    retained_mass = 0.0
    ignored_mass = 0.0
    for doubled in product((False,True),repeat=n):
        extras = sum(doubled)
        emission_weight = p2**extras*(1-p2)**(n-extras)
        if n+extras > cutoff:
            ignored_mass += emission_weight
            continue
        retained_mass += emission_weight
        if emission_weight == 0:
            continue
        for shared in product((False,True),repeat=n):
            weight = emission_weight*common_probability**sum(shared)*(1-common_probability)**(n-sum(shared))
            if weight == 0:
                continue
            species = [tuple(2*q for q in range(n) if shared[q])]
            species += [(2*q,) for q in range(n) if not shared[q]]
            species += [(2*q,) for q in range(n) if doubled[q]]
            combined = {vacuum: 1.0}
            for modes in species:
                if modes:
                    combined = _convolve_occupations(combined,species_probabilities(modes))
            for state,probability in combined.items():
                outcomes[state] = outcomes.get(state,0)+weight*probability
    measured_mass = sum(outcomes.values())
    if abs(measured_mass-retained_mass) > 1e-10:
        raise ValueError(f"retained density mass mismatch: {measured_mass} vs {retained_mass}")
    photon_masses = {}
    observed = {}
    accepted = {}
    for state,mass in outcomes.items():
        photons = sum(state)
        photon_masses[photons] = photon_masses.get(photons,0)+mass
        detected = state if profile.detector == "PNR" else tuple(min(1,x) for x in state)
        observed[detected] = observed.get(detected,0)+mass
        bits = _valid_bitstring(detected,n)
        if bits is not None and not any(detected[2*n:]):
            accepted[bits] = accepted.get(bits,0)+mass
    acceptance = sum(accepted.values())
    conditional = {bits: mass/acceptance for bits,mass in accepted.items()} if acceptance else {}
    return NoisyFockResult(conditional,acceptance,observed,photon_masses,retained_mass,ignored_mass,cutoff,{
        "representation": "A: mixture of tensor-product Fock density blocks",
        "loss": "uniform per-photon input Kraus map; commutes with passive circuit",
        "source_once": True, "p2": p2, "p1_plus_p2_normalized_assumption": True,
        "desired_label_model": "independent common/private mixture; P(common)=sqrt(V)",
        "extra_photon_model": profile.extra_photon_model,
        "projection": "final_only", "detector": profile.detector,
        "true_detected_photon_masses": "before detector coarse-graining",
        "ignored_mass": ignored_mass,
        "ignored_mass_flagged": ignored_mass >= IGNORED_MASS_FLAG_THRESHOLD,
        "max_density_block_bytes": max_density_bytes,
        "brightness_applied": False,
    })
