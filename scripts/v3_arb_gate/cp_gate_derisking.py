import math

import perceval as pcvl  # Circuit, BasicState live at top-level.
from perceval.components.core_catalog.controlled_rotation_gates import (
    PostProcessedControlledRotationsItem,
)
from perceval.simulators import Simulator
from perceval.backends import SLOSBackend

import numpy as np

# Phase 15: PostProcessedControlledRotationsItem (CP(alpha)) de-risking.
#
# This module reproduces 15-RESEARCH.md's live-measured numbers as
# executable, asserted checks -- not just re-printing cached results. It
# measures CP(alpha)'s bare-gate phase/structure behavior directly against
# this repo's installed Perceval venv (perceval-quandela==1.2.4), following
# the same standalone-gate-first pattern heralded_cz_derisking.py
# established in Phase 10.
#
# What this confirms (ARB-01, criterion 1): PostProcessedControlledRotationsItem
# implements CP(alpha) = diag(1,1,1,e^{i*alpha}) on two dual-rail qubits --
# a POST-SELECTED (not heralded) gate: n=2 gives a bare Circuit(8) (4 data
# modes + 4 ancilla modes, all held at vacuum), structurally different from
# heralded_cz's 6-mode/2-heralded-photon-ancilla construction.
#
# alpha (CP's own raw dial) vs theta (this codebase's Z_iZ_j generator-angle
# convention, matching pair_thetas={(i,j): theta} in
# exact_qubit_iqp_distribution) are DIFFERENT variables, related by
# alpha = 4*theta. This module tests CP's own dial directly. The boundary
# check below uses alpha=pi (NOT alpha=pi/4) -- per 15-CONTEXT.md's
# owner-confirmed correction: alpha=pi is the CP-dial value that reproduces
# heralded_cz's CZ=diag(1,1,1,-1) exactly (alpha=pi/4 does NOT -- it gives
# phase e^{i*pi/4} on |1,1>, confirmed by direct computation in
# 15-RESEARCH.md). alpha=pi corresponds to theta=pi/4, the existing
# Z_iZ_j-generator boundary this codebase's pair_thetas already uses.
#
# API reference (verified against installed perceval-quandela==1.2.4):
#   - PostProcessedControlledRotationsItem().build_circuit(n=2, alpha=...)
#     -- NOT build_experiment() -- returns a bare 8-mode Circuit with no
#     herald/postselect metadata attached. This matches
#     heralded_cz_derisking.py's measure_cz_phase pattern: the phase-only
#     Simulator.prob_amplitude path doesn't need herald/postselect
#     metadata, only the bare unitary.
#   - alpha must be a plain Python float (isinstance check enforced by the
#     source) -- numpy.float64 or int raises TypeError. This matters more
#     here than for heralded_cz since this function is called in a loop
#     over multiple alpha values, any of which could originate as
#     numpy.float64 from a generator/np.array -- cast explicitly at every
#     call site.

PHASE_TOLERANCE = 1e-6
MAGNITUDE_TOLERANCE = 1e-9

# alpha=pi boundary literature figure (post-selected construction),
# already cited (unverified-for-this-exact-gate, until now) in
# docs/iqp-photonic-encoding.md's ENC-01 section. This is a DIFFERENT
# number from heralded_cz's 2/27 herald-success figure -- different gate
# mechanisms (post-selection vs. heralding) have different raw success
# probabilities, and should never be conflated.
EXPECTED_BOUNDARY_MAGNITUDE_SQ = 1 / 9

# Perceval's own Encoding.DUAL_RAIL convention (verified in 15-RESEARCH.md):
# logical '0' -> Fock pattern (1,0), logical '1' -> Fock pattern (0,1).
# NOTE: this is DIFFERENT from this module's own PBS-derived H/V
# convention used elsewhere in this repo (MODULE_DUAL_RAIL) -- reconciling
# the two conventions for full pipeline wiring is Plan 15-02's job, not
# this standalone bare-gate de-risking script's.
DUAL_RAIL = {"0": (1, 0), "1": (0, 1)}

NON_TRIVIAL_ALPHAS = [math.pi / 6, math.pi / 3, 2 * math.pi / 5]
BOUNDARY_ALPHA = math.pi  # NOT math.pi / 4 -- see module docstring above.

ALL_TESTED_ALPHAS = NON_TRIVIAL_ALPHAS + [BOUNDARY_ALPHA]

_ITEM = PostProcessedControlledRotationsItem()


def measure_cp_amplitudes(alpha: float, n: int = 2) -> dict:
    """Build a Simulator directly on CP(alpha)'s bare 4n-mode circuit (no
    build_experiment() wrapper -- that would attach herald/postselect
    metadata the phase-only Simulator path doesn't need) and read the
    complex amplitude for each of the 4 computational-basis combos via
    prob_amplitude. Ancilla modes (indices 2n..4n-1, i.e. modes 4-7 for
    n=2) are held at vacuum on both input and output."""
    circuit = _ITEM.build_circuit(n=n, alpha=float(alpha))
    sim = Simulator(SLOSBackend())
    sim.set_circuit(circuit)

    ancilla = [0] * (2 * n)
    amplitudes = {}
    for ctrl in "01":
        for data in "01":
            cm, dm = DUAL_RAIL[ctrl], DUAL_RAIL[data]
            state = pcvl.BasicState(list(cm) + list(dm) + ancilla)
            amp = sim.prob_amplitude(state, state)
            amplitudes[(ctrl, data)] = amp
    return amplitudes


def check_uniform_magnitude(amplitudes: dict) -> bool:
    """Assert |amplitude|^2 is uniform across all 4 computational-basis
    combos for a given alpha -- CP is a genuine phase-only gate with no
    population distortion."""
    magnitudes_sq = [abs(amp) ** 2 for amp in amplitudes.values()]
    reference = magnitudes_sq[0]
    return all(np.isclose(m, reference, atol=MAGNITUDE_TOLERANCE) for m in magnitudes_sq)


def check_phase_matches_alpha(amplitudes: dict, alpha: float) -> bool:
    """Assert amp(1,1)/amp(0,0) matches e^{i*alpha} to floating-point
    precision -- CP(alpha) = diag(1,1,1,e^{i*alpha})."""
    amp_00 = amplitudes[("0", "0")]
    amp_11 = amplitudes[("1", "1")]
    ratio = amp_11 / amp_00
    expected = complex(math.cos(alpha), math.sin(alpha))
    return np.isclose(ratio.real, expected.real, atol=PHASE_TOLERANCE) and np.isclose(
        ratio.imag, expected.imag, atol=PHASE_TOLERANCE
    )


def check_boundary_magnitude(amplitudes: dict) -> bool:
    """At alpha=pi: assert |amplitude|^2 == 1/9 for every combo -- the
    post-selected-construction literature figure, now independently
    confirmed for this exact gate (PostProcessedControlledRotationsItem),
    distinct from heralded_cz's 2/27 herald-success figure."""
    return all(
        np.isclose(abs(amp) ** 2, EXPECTED_BOUNDARY_MAGNITUDE_SQ, atol=MAGNITUDE_TOLERANCE)
        for amp in amplitudes.values()
    )


def check_boundary_sign(amplitudes: dict) -> bool:
    """At alpha=pi: assert the sign pattern exactly matches heralded_cz's
    diag(1,1,1,-1) -- negative real amplitude on (1,1), positive on the
    other three."""
    all_pass = True
    for (ctrl, data), amp in amplitudes.items():
        if ctrl == "1" and data == "1":
            if not amp.real < 0:
                all_pass = False
        else:
            if not amp.real > 0:
                all_pass = False
    return all_pass


def main():
    print("=" * 70)
    print("CP(alpha) de-risking: phase/structure confirmation")
    print("=" * 70)
    print()
    print("alpha (CP's own dial) vs theta (Z_iZ_j generator angle, this")
    print("codebase's pair_thetas convention): related by alpha = 4*theta.")
    print("Boundary check below uses alpha=pi (== theta=pi/4), NOT")
    print("alpha=pi/4 -- see 15-CONTEXT.md's owner-confirmed correction.")
    print()

    results = {}
    for alpha in ALL_TESTED_ALPHAS:
        amplitudes = measure_cp_amplitudes(alpha)
        results[alpha] = amplitudes

    print("Success-probability-vs-alpha table:")
    print(f"{'alpha':>12} {'|amplitude|^2':>16} {'phase(amp)':>14} {'matches e^{i*alpha}':>20}")
    phase_checks = {}
    uniform_checks = {}
    for alpha in ALL_TESTED_ALPHAS:
        amplitudes = results[alpha]
        amp_00 = amplitudes[("0", "0")]
        magnitude_sq = abs(amp_00) ** 2
        phase = math.atan2(amp_00.imag, amp_00.real)  # phase of |0,0> itself (reference amp)
        amp_11 = amplitudes[("1", "1")]
        measured_phase_diff = math.atan2(amp_11.imag, amp_11.real) - phase
        phase_ok = check_phase_matches_alpha(amplitudes, alpha)
        phase_checks[alpha] = phase_ok
        uniform_checks[alpha] = check_uniform_magnitude(amplitudes)
        print(
            f"{alpha:12.6f} {magnitude_sq:16.6f} {measured_phase_diff:14.6f} "
            f"{'PASS' if phase_ok else 'FAIL':>20}"
        )

    uniform_pass = all(uniform_checks.values())
    phase_pass = all(phase_checks.values())
    print()
    print(f"Uniformity check (all alpha): {'PASS' if uniform_pass else 'FAIL'}")
    print(f"Phase-matches-e^i*alpha check (all alpha): {'PASS' if phase_pass else 'FAIL'}")

    print()
    print("=" * 70)
    print(f"alpha=pi boundary check (theta=pi/4 equivalent, matches heralded_cz's CZ)")
    print("=" * 70)
    boundary_amplitudes = results[BOUNDARY_ALPHA]
    for (ctrl, data), amp in boundary_amplitudes.items():
        print(
            f"ctrl={ctrl}, data={data}: amplitude={amp}, "
            f"|amplitude|^2={abs(amp) ** 2:.10f}"
        )
    boundary_magnitude_pass = check_boundary_magnitude(boundary_amplitudes)
    boundary_sign_pass = check_boundary_sign(boundary_amplitudes)
    print(f"Boundary magnitude check (|amp|^2 == 1/9): {'PASS' if boundary_magnitude_pass else 'FAIL'}")
    print(f"Boundary sign check (matches diag(1,1,1,-1)): {'PASS' if boundary_sign_pass else 'FAIL'}")

    assert uniform_pass, "|amplitude|^2 not uniform across computational-basis combos for some alpha"
    assert phase_pass, "amp(1,1)/amp(0,0) did not match e^{i*alpha} for some alpha"
    assert boundary_magnitude_pass, "alpha=pi boundary |amplitude|^2 did not match 1/9"
    assert boundary_sign_pass, "alpha=pi boundary sign pattern did not match heralded_cz's diag(1,1,1,-1)"

    print()
    print("All checks PASS.")


if __name__ == "__main__":
    main()
