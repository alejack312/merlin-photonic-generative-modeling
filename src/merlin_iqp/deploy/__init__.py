"""Additive v4 deployment and compiler contracts.

The deploy package deliberately keeps the logical compiler and density-matrix
composition independent of Perceval.  Perceval is an optional validation
backend for the small CP-map/full-Fock checks; an unavailable backend is a
reported capability state, never a silently substituted physical result.
"""

from .compile import (
    ALPHA_KEYS,
    CompiledCircuit,
    CompiledGate,
    QuantizedAngle,
    compile_iqp,
    compile_generators,
    nearest_alpha_key,
    quantize_theta,
    validate_topology,
)
from .density import (
    apply_compiled_density,
    compose_instruments,
    ideal_iqp_distribution,
    ideal_cp_map,
    ideal_single_map,
)
from .maps import (
    GateMap,
    MapCache,
    MapPhysicality,
    reconstruct_cp_map,
    success_weighted_haar_fidelity,
    validate_gate_map,
)
from .throughput import (
    fixed_photon_attempts_per_sample,
    general_attempts_per_sample,
    heralded_cz_attempts_per_sample,
)
from .erasure import conditional_erasure_distribution
from .fock import FullFockResult, full_fock_cp_reference

__all__ = [
    "ALPHA_KEYS",
    "CompiledCircuit",
    "CompiledGate",
    "QuantizedAngle",
    "compile_iqp",
    "compile_generators",
    "nearest_alpha_key",
    "quantize_theta",
    "validate_topology",
    "GateMap",
    "MapCache",
    "MapPhysicality",
    "reconstruct_cp_map",
    "success_weighted_haar_fidelity",
    "validate_gate_map",
    "apply_compiled_density",
    "compose_instruments",
    "ideal_iqp_distribution",
    "ideal_cp_map",
    "ideal_single_map",
    "fixed_photon_attempts_per_sample",
    "general_attempts_per_sample",
    "heralded_cz_attempts_per_sample",
    "conditional_erasure_distribution",
    "FullFockResult",
    "full_fock_cp_reference",
]
