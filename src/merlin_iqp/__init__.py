"""merlin_iqp: an IQP-style photonic-circuit toolkit built on Quandela's
MerLin framework.

Four subpackages, each an independent study built on a shared photonic IQP
encoding:

- :mod:`merlin_iqp.encoding` -- the IQP -> photonic circuit encodings
  (polarization and dual-rail) shared by every other subpackage.
- :mod:`merlin_iqp.generator` -- an MMD-trained photonic generative model
  (v1.0 milestone).
- :mod:`merlin_iqp.trainability` -- gradient-variance / barren-plateau study
  for the encoded circuit family (v3.0 milestone).
- :mod:`merlin_iqp.hardness` -- sampling-hardness-under-photon-loss study for
  the same circuit family (v3.0 milestone).

The phase-tagged sweep runners, analysis scripts, and de-risking probes that
use this package to produce the project's actual results live under
``scripts/`` at the repository root, not inside this package -- they are
one-off study CLIs, not reusable library code.
"""

__version__ = "3.0.0"
