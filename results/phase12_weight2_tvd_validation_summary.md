# Phase 12: Weight-2 Exact Reference Extension & TVD Validation Summary

Validates `build_weight2_processor`'s actual composed photonic pipeline against
an exact qubit-side reference extended with `Z_i*Z_j` pair-generator terms, at
the CZ/ZZ operator identity's exact fold point (`theta=pi/4`).

## Method

Measurement uses a herald-unregistered sibling processor
(`_build_weight2_processor_no_herald`), which mirrors `build_weight2_processor`'s
exact wiring and mode-mapping minus the two `add_herald()` calls, plus manual
post-selection on the ancilla output modes -- the confirmed workaround for two
separate Perceval `PolarizationSimulator` issues: (1) `Processor.add_herald()`
combined with any `PBS`-containing circuit crashes `Processor.probs()`
unconditionally, and (2) unannotated ancilla photons are silently
mis-distinguished from qubit photons during multi-photon interference, giving
wrong (non-crashing) numbers unless the ancilla input photons are explicitly
annotated `{P:V}` (see 12-RESEARCH.md). Upstream bug report for issue (1):
pending (filed separately -- see Plan 12-02 Task 2).

Both configurations below were re-run live against the committed
`iqp_photonic_encoding.py` (perceval-quandela 1.2.4) immediately before writing
this file.

## Primary result (locked gate, ROADMAP Success Criterion 3 / WT2-05)

| n | (i,j) | theta | TVD | herald_success_prob | herald_failure_prob | residual | passed (TVD<1e-6) |
|---|---|---|---|---|---|---|---|
| 2 | (0,1) | pi/4 | 2.581268532253489e-15 | 0.0740740740740744 | 0.9259259259259256 | 0.0 | True |

`qubit_dist` sums to 0.9999999999999996; `photonic_dist + residual` sums to
0.9999999999999944 -- both consistent with 1.0 to floating-point precision.

## Supplementary: n=3 opportunistic robustness check

| n | (i,j) | theta | TVD | herald_success_prob | herald_failure_prob | residual | passed (TVD<1e-6) |
|---|---|---|---|---|---|---|---|
| 3 | (1,2) | pi/4 (bystander qubit 0 at theta=0.6) | 1.3600232051658168e-15 | 0.07407407407407429 | 0.9259259259259257 | 0.0 | True |

`qubit_dist` sums to 0.9999999999999992; `photonic_dist + residual` sums to
0.9999999999999964.

## Interpretation

(Owner's interpretation — not yet written.)
