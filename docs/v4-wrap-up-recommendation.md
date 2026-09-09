# v4.0 wrap-up recommendation and broader-scope feasibility

Date: 2026-09-09  
Repository snapshot assessed: `40df0dc`  
Status: recommendation for owner review; this document does not change acceptance criteria or close the milestone.

## Recommendation

Wrap up the selected, bounded v4.0 release. Do not describe it as completing the original, broader scientific scope.

The reported implementation now includes matched sibling-to-photonic-map comparisons for all eight selected sibling training cells. This closes the central missing comparison identified in earlier discussions. These are analytic photonic-model comparisons, not direct full-Fock simulations or hardware experiments at those sizes. The owner-authored technical explanation is also recorded.

These additions justify closing a clearly scoped release while preserving incomplete scientific requirements. Further work should be a separately bounded research extension with its own question, budget, and stopping criteria.

## Evidence and verification boundary

This recommendation uses the orchestrator's status report and a read-only check of the current repository head, resource pilot, machine memory, and optical simulation structure. The test suite was not rerun for this recommendation, and every reported result was not independently recertified.

Relevant records:

- [Requirement evidence ledger](../.planning/v4-requirement-evidence.md)
- [Independent reviewer handoff](../.planning/v4-independent-reviewer-handoff.md)
- [Owner explanation](v4-owner-explanation-2026-09-09.md)
- [Repaired eight-cell sibling comparison summary](../results/v4_tcdp/sibling_comparisons/closure_20260909_final/summary.json)
- [Recorded resource pilot](../results/v4_tcdp/deploy/resource_budget_final_v6.json)
- [Optical simulation implementation](../src/merlin_iqp/deploy/fock.py)

The bounded results do not establish broader multiphoton validation, direct larger-n optical deployment, all sibling experiments, sampled uncertainty, or the source-mutation hypothesis. The ledger remains the authority for individual acceptance statuses.

## Current hardware and feasibility

The machine check found approximately **15.4 GiB total RAM** and **16 logical processors**. Approximately **2.7 GiB RAM was available** at the time of inspection; available memory varies with other applications.

The recorded resource pilot evaluated the n=10 **map model** in approximately **4.3 seconds**. This is evidence that the bounded map calculation is practical. It is not a benchmark for n=10 full-Fock simulation.

The optical implementation allocates two data modes per photon plus four additional modes per two-qubit gate. It also contains an evaluation path that materializes the fixed-photon output states. For an illustrative circuit with n photons and n−1 two-qubit gates, the mode count is m = 2n + 4(n−1), and the number of possible n-photon occupation states is binomial(m+n−1, n).

| Photons | Optical modes | Possible fixed-photon output states |
| --- | --- | --- |
| 4 | 20 | 8,855 |
| 6 | 32 | 2,324,784 |
| 8 | 44 | 636,763,050 |

These are calculated state-space sizes for the illustrative gate count, not measured runtimes or counts of nonzero amplitudes. Actual costs depend on circuit structure, gate count, and simulation method.

At n=8, storing one 16-byte complex amplitude per possible state alone would require approximately **9.5 GiB**. State objects, simulator intermediates, and other applications require additional memory. This calculation is not a claim that every algorithm must allocate such an array; it explains why the current enumeration approach is a concern on this machine.

**n=6 merits a controlled feasibility probe. Direct n=8 simulation should not be promised with the current approach and hardware.** More RAM or a different simulation method may help, but neither automatically establishes physical correctness. Simulated deployment also does not constitute an experiment on a physical photonic device.

## Effort estimates

The following are planning estimates for focused engineering and research work, not benchmark-derived completion promises. They assume access to the existing environment and timely resolution of necessary design choices. They exclude unknown external-input delays.

| Work | Estimated effort | Main qualification |
| --- | --- | --- |
| Package the bounded release, reconcile claims, and perform final review | ½–2 focused days | Assumes existing verification remains valid and no material defect appears |
| Add sampling uncertainty to existing model-based comparisons | 2–5 days | Requires an explicit sampling protocol; does not validate physical source noise |
| Investigate and validate direct n=6/n=8 optical deployment | Several days to several weeks | Resource feasibility and algorithm changes remain uncertain |
| Specify, implement, and validate a richer source model and source-mutation experiment | Several weeks | Requires a precise experimental question and a validated model |
| Reproduce every unavailable sibling experiment | Not yet estimable | Missing inputs and environment requirements must first be resolved |

These activities overlap and the estimates should not simply be added. Matching the broader original scope is a **weeks-scale research extension, potentially longer**, rather than one more cleanup pass. There is no defensible fixed completion date for the entire broader scope from the available evidence.

Some questions may yield negative results. A universal equivalence claim cannot be completed by producing a proof if the claim is false. A scoped counterexample or negative experimental result can be a valid research outcome when evaluated against the registered question. Likewise, NAT need not outperform its control for an honestly conducted comparison to be informative.

## Proposed closure steps

1. Freeze the bounded implementation and identify the exact release commit.
2. Have the owner explicitly accept the release scope. Preserve original broader requirements and their current evidence statuses; do not silently relabel them as passed.
3. Reconcile the release summary, ledger, and study documents so analytic map results, direct optical simulation, and hardware evidence are clearly distinguished.
4. Confirm that required verification applies to the release commit and that reported artifacts retain valid provenance.
5. Record remaining work as a separate research extension. Any merge or publication follows its own authorization and review process.

This document recommends those steps; it does not execute them or record owner approval.

## Suggested next investigation, if work continues

Start with a bounded n=6 direct optical feasibility probe before committing to n=8 or a larger sweep. Specify the circuit, gate count, source assumptions, expected reference, resource ceiling, and stopping rule before running it. Measure elapsed time and peak memory, and compare both absolute acceptance probability and the conditional output distribution against the qualified reference.

A successful timing probe establishes affordability only. Correctness requires agreement under the declared source and projection assumptions. If the probe exceeds its budget, record that boundary and assess a different method or additional resources before expanding the run.

The recommended immediate action is scoped release closure. Further compute should answer a specific remaining question rather than pursue an unrestricted promise to make every original criterion pass.
