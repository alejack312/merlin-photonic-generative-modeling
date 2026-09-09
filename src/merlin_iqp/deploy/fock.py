"""Small-n direct full-Fock controls and explicit capability diagnostics.

The analytic CP-map path is deliberately kept separate from this module's
direct Perceval path.  The latter prepares one fixed-photon source state for
the complete circuit, simulates the full Fock output, and applies the
declared projection only while classifying the output.  It therefore gives a
real backend comparison for the bounded ``g2=0`` scope rather than relabeling
an analytic map evaluation as physical evidence.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Sequence
import hashlib
import json
import math

import numpy as np


@dataclass(frozen=True)
class FullFockResult:
    status: str
    distribution: dict[str, float] = field(default_factory=dict)
    accepted_mass: float | None = None
    rejected_mass: float | None = None
    diagnostics: dict[str, Any] = field(default_factory=dict)


PairSpec = tuple[int, int, float, float]
Projection = Literal["final_only", "intermediate"]
FULL_FOCK_MASS_TOLERANCE = 1.0e-12


class _MassReconciliationError(ValueError):
    def __init__(self, context: str, measured_mass: float) -> None:
        self.context = context
        self.measured_mass = float(measured_mass)
        self.reconciliation_error = abs(self.measured_mass - 1.0)
        super().__init__(
            f"{context} total mass {self.measured_mass} differs from 1.0 by "
            f"{self.reconciliation_error} > {FULL_FOCK_MASS_TOLERANCE}"
        )


def _validate_total_mass(total_mass: float, context: str) -> float:
    if not math.isfinite(total_mass):
        raise ValueError(f"{context} returned non-finite total mass {total_mass!r}")
    reconciliation_error = abs(float(total_mass) - 1.0)
    if reconciliation_error > FULL_FOCK_MASS_TOLERANCE:
        raise _MassReconciliationError(context, float(total_mass))
    return reconciliation_error


def _failure_diagnostics(prefix: str, exc: Exception) -> dict[str, Any]:
    diagnostics: dict[str, Any] = {"reason": f"{prefix}: {type(exc).__name__}: {exc}"}
    if isinstance(exc, _MassReconciliationError):
        diagnostics.update(
            {
                "full_fock_total_mass": exc.measured_mass,
                "mass_reconciliation_error": exc.reconciliation_error,
                "mass_reconciliation_tolerance": FULL_FOCK_MASS_TOLERANCE,
            }
        )
    return diagnostics


def _tvd(left: dict[str, float], right: dict[str, float]) -> float:
    keys = set(left) | set(right)
    return float(0.5 * sum(abs(left.get(key, 0.0) - right.get(key, 0.0)) for key in keys))


def _json_hash(value: object) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _perceval_modules() -> tuple[Any, Any, Any, Any]:
    """Import optional physical dependencies only when direct simulation runs."""

    import perceval as pcvl  # type: ignore
    from perceval.backends import SLOSBackend  # type: ignore
    from perceval.simulators import Simulator  # type: ignore
    from perceval.utils import allstate_iterator  # type: ignore

    return pcvl, SLOSBackend, Simulator, allstate_iterator


def _validate_pair_specs(n: int, singles: Sequence[float], pair_specs: Sequence[PairSpec]) -> tuple[float, ...]:
    if int(n) != n or n < 1:
        raise ValueError("n must be a positive integer")
    if len(singles) != n:
        raise ValueError("single-angle count does not match n")
    if any(not math.isfinite(float(value)) for value in singles):
        raise ValueError("single angles must be finite")
    seen: set[tuple[int, int]] = set()
    for i, j, theta, alpha in pair_specs:
        if int(i) != i or int(j) != j or i == j or not (0 <= i < n and 0 <= j < n):
            raise ValueError(f"invalid pair {(i, j)} for n={n}")
        pair = (min(int(i), int(j)), max(int(i), int(j)))
        if pair in seen:
            raise ValueError(f"duplicate pair {pair}")
        seen.add(pair)
        if not math.isfinite(float(theta)) or not math.isfinite(float(alpha)):
            raise ValueError("pair angles must be finite")
    folded = [float(value) for value in singles]
    for i, j, theta, _ in pair_specs:
        folded[int(i)] += float(theta)
        folded[int(j)] += float(theta)
    return tuple(folded)


def _build_direct_processor(n: int, singles: Sequence[float], pair_specs: Sequence[PairSpec], count: int | None = None) -> tuple[Any, Any, list[tuple[int, ...]]]:
    """Build a plain Perceval Processor with no native post-selection."""

    pcvl, _, _, _ = _perceval_modules()
    pair_specs = tuple(pair_specs)
    folded = _validate_pair_specs(n, singles, pair_specs)
    gate_count = len(pair_specs) if count is None else int(count)
    if not 0 <= gate_count <= len(pair_specs):
        raise ValueError("invalid direct-processor gate count")
    total_modes = 2 * n + 4 * len(pair_specs)
    processor = pcvl.Processor("SLOS", total_modes)

    prep = pcvl.Circuit(total_modes)
    for qubit in range(n):
        prep.add(2 * qubit, pcvl.BS())
    processor.add(0, prep)

    diagonal = pcvl.Circuit(total_modes)
    # A single-sided PS(phi) is exp(i*phi/2*Z) up to a scalar, so the
    # abstract exp(i*theta*Z) angle is represented by phi=2*theta.
    for qubit, theta in enumerate(folded):
        diagonal.add(2 * qubit, pcvl.PS(-2.0 * theta))
    processor.add(0, diagonal)

    from merlin_iqp.encoding.iqp_photonic import _build_cp_insertion_core

    for gate_index, (i, j, _, alpha) in enumerate(pair_specs[:gate_count]):
        ancilla_start = 2 * n + 4 * gate_index
        mapping = {
            2 * int(i): 0,
            2 * int(i) + 1: 1,
            2 * int(j): 2,
            2 * int(j) + 1: 3,
            ancilla_start: 4,
            ancilla_start + 1: 5,
            ancilla_start + 2: 6,
            ancilla_start + 3: 7,
        }
        processor.add(mapping, _build_cp_insertion_core(float(alpha)))

    if count is None or gate_count == len(pair_specs):
        conjugation = pcvl.Circuit(total_modes)
        for qubit in range(n):
            conjugation.add(2 * qubit, pcvl.BS())
        processor.add(0, conjugation)
    # The Perceval BS convention maps the module's declared logical-zero
    # rail (0,1) to the opposite rail after the prepare/conjugate sandwich at
    # zero angle.  Starting in (1,0) makes the independent no-gate identity
    # fixture land on (0,1) at readout, while _valid_bitstring retains the
    # declared (0,1)->0, (1,0)->1 output convention.
    return processor, pcvl.BasicState([1, 0] * n + [0] * (4 * len(pair_specs))), [
        tuple(range(2 * n + 4 * gate, 2 * n + 4 * gate + 4)) for gate in range(len(pair_specs))
    ]


def _valid_bitstring(state: Any, n: int) -> str | None:
    bits: list[str] = []
    for qubit in range(n):
        pair = (int(state[2 * qubit]), int(state[2 * qubit + 1]))
        if pair == (0, 1):
            bits.append("0")
        elif pair == (1, 0):
            bits.append("1")
        else:
            return None
    return "".join(bits)


def _accepted_state(state: Any, n: int, ancilla_groups: Sequence[tuple[int, ...]], through_gate: int | None = None) -> str | None:
    groups = ancilla_groups if through_gate is None else ancilla_groups[: through_gate + 1]
    if any(int(state[mode]) != 0 for group in groups for mode in group):
        return None
    return _valid_bitstring(state, n)


def _all_states(input_state: Any, allstate_iterator: Any) -> list[Any]:
    return list(allstate_iterator(input_state))


def _final_distribution(
    processor: Any,
    input_state: Any,
    n: int,
    ancilla_groups: Sequence[tuple[int, ...]],
) -> tuple[dict[str, float], float, int, int, float, float]:
    _, _, Simulator, allstate_iterator = _perceval_modules()
    simulator = Simulator(_perceval_modules()[1]())
    simulator.set_circuit(processor.linear_circuit())
    full = simulator.probs(input_state)
    full_mass = 0.0
    accepted: dict[str, float] = {}
    accepted_count = 0
    state_count = 0
    for state, probability in full.items():
        state_count += 1
        complex_probability = complex(probability)
        if abs(complex_probability.imag) > FULL_FOCK_MASS_TOLERANCE:
            raise ValueError("direct full-Fock simulator returned a complex probability")
        mass = float(complex_probability.real)
        if not math.isfinite(mass) or mass < 0.0:
            raise ValueError("direct full-Fock simulator returned negative or non-finite probability mass")
        full_mass += mass
        bits = _accepted_state(state, n, ancilla_groups)
        if bits is not None:
            accepted[bits] = accepted.get(bits, 0.0) + mass
            accepted_count += 1
    reconciliation_error = _validate_total_mass(full_mass, "direct full-Fock simulator")
    accepted_total = float(sum(accepted.values()))
    if accepted_total < 0.0 or accepted_total > 1.0 + FULL_FOCK_MASS_TOLERANCE:
        raise ValueError(f"accepted full-Fock mass {accepted_total} is outside [0, 1]")
    raw_acceptance = accepted_total
    if raw_acceptance <= 0.0:
        return {}, raw_acceptance, state_count, accepted_count, full_mass, reconciliation_error
    return (
        {key: value / accepted_total for key, value in accepted.items()},
        raw_acceptance,
        state_count,
        accepted_count,
        full_mass,
        reconciliation_error,
    )


def _intermediate_distribution(
    n: int,
    singles: Sequence[float],
    pair_specs: Sequence[PairSpec],
    input_state: Any,
    ancilla_groups: Sequence[tuple[int, ...]],
) -> tuple[dict[str, float], float, int, int, float, float]:
    """Propagate amplitudes while projecting after each CP insertion.

    This is intentionally a small-n diagnostic.  It retains complex
    amplitudes between projections so it does not confuse sequential
    conditioning with a product of independently normalized probabilities.
    """

    _, SLOSBackend, Simulator, allstate_iterator = _perceval_modules()
    states = _all_states(input_state, allstate_iterator)
    if not pair_specs:
        processor, _, _ = _build_direct_processor(n, singles, pair_specs)
        return _final_distribution(processor, input_state, n, ancilla_groups)

    prep_processor, _, _ = _build_direct_processor(n, singles, pair_specs, count=0)
    prep_sim = Simulator(SLOSBackend())
    prep_sim.set_circuit(prep_processor.linear_circuit())
    amplitudes: dict[Any, complex] = {
        state: prep_sim.prob_amplitude(input_state, state) for state in states
    }
    amplitudes = {
        state: amplitude
        for state, amplitude in amplitudes.items()
        if abs(amplitude) > 1e-14
    }
    initial_mass = float(sum(abs(amplitude) ** 2 for amplitude in amplitudes.values()))
    initial_reconciliation_error = _validate_total_mass(initial_mass, "intermediate source propagation")
    for gate_index in range(len(pair_specs)):
        # Remove preparation/diagonal components by constructing the gate-only
        # circuit from the same CP core.  Rebuilding it avoids relying on
        # private Processor component internals.
        gate_only = _build_gate_only_processor(n, pair_specs, gate_index)
        transition_sim = Simulator(SLOSBackend())
        transition_sim.set_circuit(gate_only.linear_circuit())
        next_amplitudes: dict[Any, complex] = {}
        for input_value, input_amplitude in amplitudes.items():
            if abs(input_amplitude) <= 1e-14:
                continue
            for output_state in states:
                transition = transition_sim.prob_amplitude(input_value, output_state)
                if abs(transition) > 1e-14:
                    next_amplitudes[output_state] = next_amplitudes.get(output_state, 0.0j) + input_amplitude * transition
        amplitudes = {
            state: amplitude
            for state, amplitude in next_amplitudes.items()
            if _accepted_state(state, n, ancilla_groups, through_gate=gate_index) is not None
            and abs(amplitude) > 1e-14
        }

    final_processor = _build_final_readout_processor(n, pair_specs)
    final_sim = Simulator(SLOSBackend())
    final_sim.set_circuit(final_processor.linear_circuit())
    accepted_amplitudes: dict[str, complex] = {}
    accepted_states: set[str] = set()
    for input_value, input_amplitude in amplitudes.items():
        for output_state in states:
            transition = final_sim.prob_amplitude(input_value, output_state)
            amplitude = input_amplitude * transition
            bits = _accepted_state(output_state, n, ancilla_groups)
            if bits is not None:
                accepted_amplitudes[bits] = accepted_amplitudes.get(bits, 0.0j) + amplitude
                accepted_states.add(bits)
    accepted = {key: float(abs(amplitude) ** 2) for key, amplitude in accepted_amplitudes.items()}
    accepted_total = float(sum(accepted.values()))
    if accepted_total < 0.0 or accepted_total > initial_mass + FULL_FOCK_MASS_TOLERANCE:
        raise ValueError(f"intermediate accepted mass {accepted_total} exceeds source mass {initial_mass}")
    accepted_count = len(accepted_states)
    if initial_mass <= 0.0 or accepted_total <= 0.0:
        return {}, 0.0, len(states), accepted_count, initial_mass, initial_reconciliation_error
    raw_acceptance = accepted_total
    return (
        {key: value / accepted_total for key, value in accepted.items()},
        raw_acceptance,
        len(states),
        accepted_count,
        initial_mass,
        initial_reconciliation_error,
    )


def _build_gate_only_processor(n: int, pair_specs: Sequence[PairSpec], gate_index: int) -> Any:
    pcvl, _, _, _ = _perceval_modules()
    from merlin_iqp.encoding.iqp_photonic import _build_cp_insertion_core

    total_modes = 2 * n + 4 * len(pair_specs)
    processor = pcvl.Processor("SLOS", total_modes)
    i, j, _, alpha = pair_specs[gate_index]
    ancilla_start = 2 * n + 4 * gate_index
    processor.add(
        {
            2 * int(i): 0,
            2 * int(i) + 1: 1,
            2 * int(j): 2,
            2 * int(j) + 1: 3,
            ancilla_start: 4,
            ancilla_start + 1: 5,
            ancilla_start + 2: 6,
            ancilla_start + 3: 7,
        },
        _build_cp_insertion_core(float(alpha)),
    )
    return processor


def _build_final_readout_processor(n: int, pair_specs: Sequence[PairSpec]) -> Any:
    pcvl, _, _, _ = _perceval_modules()
    processor = pcvl.Processor("SLOS", 2 * n + 4 * len(pair_specs))
    conjugation = pcvl.Circuit(2 * n + 4 * len(pair_specs))
    for qubit in range(n):
        conjugation.add(2 * qubit, pcvl.BS())
    processor.add(0, conjugation)
    return processor


def direct_fock_cp_reference(
    n: int,
    singles: Sequence[float],
    pairs: Sequence[tuple[int, int, float]],
    *,
    eta: float = 1.0,
    projection: Projection = "final_only",
) -> FullFockResult:
    """Evaluate an ideal fixed-photon CP circuit through direct Perceval SLOS.

    ``pairs`` contains abstract ZZ angles; each is implemented by a CP gate
    with ``alpha=4*theta`` and its local compensation.  The source is one
    input state with exactly n data photons and vacuum gate ancillas.  Loss is
    the selected D1 uniform per-photon model, applied once to the source
    acceptance mass as ``eta**n``; no multiphoton source or gate-local noise is
    inferred.
    """

    if projection not in {"final_only", "intermediate"}:
        raise ValueError("projection must be final_only or intermediate")
    eta = float(eta)
    if not math.isfinite(eta) or not 0.0 < eta <= 1.0:
        raise ValueError("eta must be finite and in (0,1]")
    pair_specs: tuple[PairSpec, ...] = tuple((int(i), int(j), float(theta), 4.0 * float(theta)) for i, j, theta in pairs)
    folded = _validate_pair_specs(n, singles, pair_specs)
    try:
        processor, input_state, ancilla_groups = _build_direct_processor(n, singles, pair_specs)
        if projection == "final_only" or len(pair_specs) <= 1:
            distribution, raw_acceptance, state_count, accepted_count, full_mass, reconciliation_error = _final_distribution(
                processor, input_state, n, ancilla_groups
            )
        else:
            distribution, raw_acceptance, state_count, accepted_count, full_mass, reconciliation_error = _intermediate_distribution(
                n, singles, pair_specs, input_state, ancilla_groups
            )
    except Exception as exc:
        return FullFockResult(
            "INCONCLUSIVE",
            diagnostics={
                **_failure_diagnostics("direct Perceval full-Fock reference failed", exc),
                "backend": "Perceval SLOS",
                "projection": projection,
            },
        )
    accepted_mass = float(raw_acceptance * eta**int(n))
    return FullFockResult(
        "PASS",
        distribution=distribution,
        accepted_mass=accepted_mass,
        rejected_mass=float(1.0 - accepted_mass),
        diagnostics={
            "backend": "Perceval SLOS direct full-Fock",
            "perceval_version": _perceval_modules()[0].__version__ if hasattr(_perceval_modules()[0], "__version__") else "unknown",
            "source_once": True,
            "source_model": "fixed_photon_g2_0",
            "source_input_photons": int(n),
            "gate_ancilla_input": "vacuum",
            "gate_count": len(pair_specs),
            "projection": projection,
            "loss": "uniform_all_data_photons_once",
            "g2": 0.0,
            "eta": eta,
            "raw_source_acceptance": raw_acceptance,
            "full_fock_state_count": state_count,
            "accepted_state_count": accepted_count,
            "full_fock_total_mass": full_mass,
            "mass_reconciliation_error": reconciliation_error,
            "mass_reconciliation_tolerance": FULL_FOCK_MASS_TOLERANCE,
            "conditional_distribution": True,
            "distribution_hash": _json_hash(distribution),
            "folded_single_angles": list(folded),
        },
    )


def direct_fock_compiled_distribution(compiled: Any, *, eta: float = 1.0, projection: Projection = "final_only") -> FullFockResult:
    """Directly evaluate a compiled weight-1/2 circuit with full-Fock output."""

    pairs = [
        (pair[0], pair[1], angle.lifted_theta)
        for pair, angle in compiled.pair_angles
    ]
    pair_specs: tuple[PairSpec, ...] = tuple(
        (int(pair[0]), int(pair[1]), float(angle.lifted_theta), float(angle.wrapped_alpha))
        for pair, angle in compiled.pair_angles
    )
    if projection == "final_only" or len(pair_specs) <= 1:
        try:
            processor, input_state, ancilla_groups = _build_direct_processor(compiled.n, compiled.singles, pair_specs)
            distribution, raw_acceptance, state_count, accepted_count, full_mass, reconciliation_error = _final_distribution(
                processor, input_state, compiled.n, ancilla_groups
            )
        except Exception as exc:
            return FullFockResult("INCONCLUSIVE", diagnostics=_failure_diagnostics("direct Perceval compiled adapter failed", exc))
        eta_value = float(eta)
        if not math.isfinite(eta_value) or not 0.0 < eta_value <= 1.0:
            raise ValueError("eta must be finite and in (0,1]")
        accepted_mass = raw_acceptance * eta_value ** int(compiled.n)
        return FullFockResult(
            "PASS",
            distribution=distribution,
            accepted_mass=float(accepted_mass),
            rejected_mass=float(1.0 - accepted_mass),
            diagnostics={
                "backend": "Perceval SLOS direct full-Fock",
                "perceval_version": _perceval_modules()[0].__version__ if hasattr(_perceval_modules()[0], "__version__") else "unknown",
                "source_once": True,
                "source_model": "fixed_photon_g2_0",
                "projection": projection,
                "raw_source_acceptance": float(raw_acceptance),
                "full_fock_state_count": state_count,
                "accepted_state_count": accepted_count,
                "full_fock_total_mass": full_mass,
                "mass_reconciliation_error": reconciliation_error,
                "mass_reconciliation_tolerance": FULL_FOCK_MASS_TOLERANCE,
                "distribution_hash": _json_hash(distribution),
                "compiled_metadata": compiled.as_metadata(),
            },
        )
    return _direct_compiled_intermediate(compiled, eta=eta)


def _direct_compiled_intermediate(compiled: Any, *, eta: float) -> FullFockResult:
    pair_specs: tuple[PairSpec, ...] = tuple(
        (int(pair[0]), int(pair[1]), float(angle.lifted_theta), float(angle.wrapped_alpha))
        for pair, angle in compiled.pair_angles
    )
    try:
        _, input_state, ancilla_groups = _build_direct_processor(compiled.n, compiled.singles, pair_specs)
        distribution, raw_acceptance, state_count, accepted_count, full_mass, reconciliation_error = _intermediate_distribution(
            compiled.n, compiled.singles, pair_specs, input_state, ancilla_groups
        )
    except Exception as exc:
        return FullFockResult("INCONCLUSIVE", diagnostics=_failure_diagnostics("direct Perceval compiled intermediate adapter failed", exc))
    eta_value = float(eta)
    if not math.isfinite(eta_value) or not 0.0 < eta_value <= 1.0:
        raise ValueError("eta must be finite and in (0,1]")
    accepted_mass = raw_acceptance * eta_value ** int(compiled.n)
    return FullFockResult(
        "PASS",
        distribution=distribution,
        accepted_mass=float(accepted_mass),
        rejected_mass=float(1.0 - accepted_mass),
        diagnostics={
            "backend": "Perceval SLOS direct full-Fock",
            "perceval_version": _perceval_modules()[0].__version__ if hasattr(_perceval_modules()[0], "__version__") else "unknown",
            "source_once": True,
            "source_model": "fixed_photon_g2_0",
            "projection": "intermediate",
            "raw_source_acceptance": float(raw_acceptance),
            "full_fock_state_count": state_count,
            "accepted_state_count": accepted_count,
            "full_fock_total_mass": full_mass,
            "mass_reconciliation_error": reconciliation_error,
            "mass_reconciliation_tolerance": FULL_FOCK_MASS_TOLERANCE,
            "distribution_hash": _json_hash(distribution),
            "compiled_metadata": compiled.as_metadata(),
        },
    )


def full_fock_cp_reference(
    n: int,
    i: int,
    j: int,
    singles: list[float] | tuple[float, ...],
    alpha: float,
    *,
    g2: float = 0.0,
    eta: float = 1.0,
) -> FullFockResult:
    """Run the existing small CP dual-rail reference when its scope applies.

    This deliberately supports only one CP insertion. The fixed-photon
    ``g2=0`` branch accepts uniform loss through explicit ``eta**n`` success
    scaling; multiphoton source requests remain INCONCLUSIVE rather than being
    silently approximated by a gate-local map.
    """

    if n not in (2, 3):
        return FullFockResult("INCONCLUSIVE", diagnostics={"reason": "full-Fock reference is scoped to n=2,3"})
    if not 0 <= i < n or not 0 <= j < n or i == j:
        raise ValueError("invalid CP pair")
    if len(singles) != n:
        raise ValueError("single-angle count does not match n")
    if not np.isfinite(eta) or not 0.0 < eta <= 1.0:
        raise ValueError("eta must be finite and in (0, 1]")
    if not np.isclose(g2, 0.0):
        return FullFockResult(
            "INCONCLUSIVE",
            diagnostics={
                "reason": "multiphoton g2 source model is not implemented; D1 fixed-photon scope excludes it",
                "g2": float(g2),
                "eta": float(eta),
                "source_once": True,
            },
        )
    try:
        from merlin_iqp.encoding.dual_rail import dual_rail_photonic_cp_iqp_distribution
    except Exception as exc:
        return FullFockResult("INCONCLUSIVE", diagnostics={"reason": f"Perceval unavailable: {type(exc).__name__}: {exc}"})
    try:
        distribution, residual, failure = dual_rail_photonic_cp_iqp_distribution(
            n, i, j, list(singles), float(alpha)
        )
    except Exception as exc:
        return FullFockResult("INCONCLUSIVE", diagnostics={"reason": f"Perceval reference failed: {type(exc).__name__}: {exc}"})
    accepted_mass = float((1.0 - failure) * eta**n)
    return FullFockResult(
        "PASS",
        distribution={str(key): float(value) for key, value in distribution.items()},
        accepted_mass=accepted_mass,
        rejected_mass=float(1.0 - accepted_mass),
        diagnostics={
            "source_once": True,
            "source_model": "fixed_photon_g2_0",
            "loss": "uniform_all_photons",
            "projection": "four CP ancilla modes vacuum",
            "residual_out_of_logical_subspace": float(residual),
            "conditional_distribution": True,
            "general_agreement_claim": False,
            "g2": 0.0,
            "eta": float(eta),
            "loss_scaling": "eta**n",
        },
    )
