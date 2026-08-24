"""IQP -> photonic encodings (v2.0/v2.1/v3.0 milestones): maps an IQP-style
qubit circuit onto a photonic Fock-space ansatz.

Two parallel encodings live here:

- :mod:`merlin_iqp.encoding.iqp_photonic` -- the original polarization
  encoding (one photon per qubit, H/V carries the qubit basis). Not wrappable
  by MerLin's ``QuantumLayer``, which rejects polarization-annotated
  ``BasicState`` inputs outright; used with direct Perceval
  ``Processor``/``Simulator`` calls instead.
- :mod:`merlin_iqp.encoding.dual_rail` -- an additive, polarization-free
  spatial dual-rail re-encoding of the same abstract circuit family, wrapped
  by MerLin's ``QuantumLayer`` for native torch autograd. Reuses shared
  Fock-space/mode-occupation logic directly from ``iqp_photonic`` rather than
  re-deriving it.
"""
