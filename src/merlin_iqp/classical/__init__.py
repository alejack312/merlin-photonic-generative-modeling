"""NumPy-only classical IQP training core for the additive v4 pipelines.

The package deliberately has no dependency on Perceval, MerLin, JAX, or the
legacy sibling package.  The sibling experiment is a source of semantics and
provenance, not an import dependency.
"""

from .adapters import (
    chain_1d,
    generators_from_pairs,
    generators_to_pairs,
    pairs_from_generators,
    round_trip_generators,
)
from .contracts import (
    BackendResult,
    Checkpoint,
    CompatibilityRecord,
    DatasetBundle,
    IQPSpec,
    KernelSpec,
)
from .expectation import (
    all_bitstrings,
    all_observables,
    expectation_exact,
    expectation_gradient_exact,
    grad_expectation_exact,
    iqp_expectation_exact,
    iqp_phase,
    expectations_and_jacobian_exact,
)
from .initialization import initialize_theta
from .ising import ising_probabilities, ising_target
from .kernel import (
    gaussian_hamming_kernel,
    gaussian_hamming_spectrum,
    gaussian_spectral_weights,
    gaussian_tau,
    hamming_walsh_matrix,
    spatial_walsh_matrix,
)
from .model import IQPModel
from .objectives import (
    hamming_mmd2,
    hamming_mmd2_walsh,
    spatial_mmd2,
)
from .rng import derive_seed, make_rng, split_rng
from .targets import (
    BinarySamples,
    ExactProbabilities,
    TargetMoments,
    WeightedSupport,
    target_moments,
)
from .trainer import Trainer

__all__ = [
    "BackendResult",
    "BinarySamples",
    "Checkpoint",
    "CompatibilityRecord",
    "DatasetBundle",
    "ExactProbabilities",
    "IQPModel",
    "IQPSpec",
    "KernelSpec",
    "TargetMoments",
    "Trainer",
    "WeightedSupport",
    "all_bitstrings",
    "all_observables",
    "chain_1d",
    "derive_seed",
    "expectation_exact",
    "expectation_gradient_exact",
    "expectations_and_jacobian_exact",
    "grad_expectation_exact",
    "iqp_expectation_exact",
    "iqp_phase",
    "gaussian_hamming_kernel",
    "gaussian_hamming_spectrum",
    "gaussian_spectral_weights",
    "gaussian_tau",
    "generators_from_pairs",
    "generators_to_pairs",
    "hamming_mmd2",
    "hamming_mmd2_walsh",
    "hamming_walsh_matrix",
    "initialize_theta",
    "ising_probabilities",
    "ising_target",
    "make_rng",
    "pairs_from_generators",
    "round_trip_generators",
    "spatial_mmd2",
    "spatial_walsh_matrix",
    "split_rng",
    "target_moments",
]
