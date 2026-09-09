# v4 post-repair independent audit

Date: 2026-09-09. Reviewed head: `6d3af6f`; previous audited head: `40df0dc`.

## Verdict and scope

The A01–A04 fixes are present. The saved corrected shared-gate TVD is approximately 1.94e-16, and the three regenerated physical controls agree with independently calculated ideal acceptance to at most 4.17e-17. No new numerical disagreement was found in those controls.

Three remaining reproducible robustness defects follow. They concern qualification and continuation, not evidence that the regenerated nominal distributions are wrong. Resolve them with a focused repair pass; they do not require reopening deferred multiphoton or larger-n research.

Reviewed the repair diff, physical and ring qualification paths, sibling comparison changes and hashes, trainer/checkpoint continuation, resource aggregation, and nearby NAT contracts. This was not a line-by-line recertification of every historical artifact or the entire legacy implementation. Implementation, canonical results, and sibling files were not modified.

## B01 — P1: Physical acceptance correctness is still not enforced

Locations: `src/merlin_iqp/deploy/ring.py:261–291`; `scripts/v4_tcdp/validate_physical_controls.py:68–115`.

The repaired Fock adapter validates total backend probability mass, which correctly addresses A02. However, downstream qualification still tests only conditional shape and self-reported acceptance bookkeeping. Conservation of total probability does not establish that the correct subset of outcomes was accepted.

The ring evaluator allows acceptance in the closed interval [0,1], then selects PASS solely from conditional TVD. It does not compare absolute acceptance to an independent instrument prediction or check its consistency with the reported raw acceptance and eta. A normalized conditional output paired with zero acceptance is accepted.

Probe: load the regenerated spatial ring JSON, supply its unchanged conditional distribution and diagnostics through a process-local replacement of `direct_fock_compiled_distribution`, but return accepted mass 0 and rejected mass 1. `evaluate_ring_artifact` returns **PASS**. The saved original acceptance is **0.0013629669360371189**.

The physical-control producer has the same independent-check gap: replace both direct control results with half their original raw and accepted mass, preserving eta scaling, conditional distributions, and complementary rejected mass. `_control` still returns **PASS** and `absolute_mass_valid=True`. This also passes the final/intermediate acceptance-delta check because both arms share the same error.

The current saved controls are not demonstrated wrong: their actual acceptance agrees with `eta**n * product(ideal_cp_map(4*theta).success)` for the registered fixtures. The missing assertion means an acceptance-selection regression could still be certified.

Repair: for the registered ideal fixed-photon fixtures, enforce and record absolute acceptance against the independent expected instrument, separately from conditional TVD and total mass. Reject undefined conditional distributions at zero accepted mass; check consistency of accepted/rejected/raw/eta fields. Add shape-preserving acceptance mutations. For future topologies where the analytic composition is not independently qualified, explicitly report that limitation rather than assuming the product formula generally.

## B02 — P2: Accepted empty-history checkpoints become unresumable

Location: `src/merlin_iqp/classical/trainer.py:116` and `:59–80`.

`resume` accepts an empty loss history even when `checkpoint.step` is positive. The next `run` initializes a new history at the current parameter state but keeps the old global step. Saving succeeds; loading that newly saved checkpoint then fails the history-length check.

Probe: train a two-qubit model for two steps, save an otherwise unchanged checkpoint with `loss_history=()`, resume it, run one step, and save again. The first resume succeeds. The new checkpoint has step 3 and two loss entries. A second resume raises `ValueError: checkpoint loss history length is inconsistent with checkpoint step`.

This input is accepted by both the checkpoint contract and the resume validator. Normal complete-history checkpoints were not shown to fail.

Repair: either reject missing history for positive-step strict resumes before state mutation, or explicitly represent a history offset and consistently support it during save and resume. Do not reconstruct or invent the missing losses. Add an accepted-resume → run → save → resume round-trip test.

## B03 — P2: Resource aggregation promotes incomplete measurements to PASS

Location: `scripts/v4_tcdp/resource_pilot.py:367–376`.

`aggregate_status` rejects explicit FAIL cases, then checks only n=10 RSS. An INCONCLUSIVE measurement at n=4, n=6, or n=8 does not prevent the overall report from passing. Missing required sizes are also not checked. Thus unavailable memory evidence can be hidden by one successful n=10 case.

Minimal probe:

```python
aggregate_status([
    {"n": 4, "measurement_status": "INCONCLUSIVE", "peak_rss_bytes": None},
    {"n": 10, "measurement_status": "PASS", "rss_growth_bytes": 1,
     "peak_rss_bytes": 100},
])
# 'PASS'
```

The same status issue applies to a complete list where one smaller-n measurement is INCONCLUSIVE. The stored pilot's measurements are labeled PASS; this probe demonstrates an aggregation defect rather than invalidating its recorded measurements.

Repair: require exactly the registered sizes, reject duplicates/unknown statuses, propagate missing or inconclusive measurements, and only return PASS when every required measurement passes and the n=10 threshold passes. Preserve the plan's distinction between peak RSS growth and absolute RSS.

## Verification record

- Reviewed current clean head `6d3af6f` before adding this report.
- Independently read and checked the corrected physical controls. Maximum ideal acceptance error: 4.163336342344337e-17; shared-gate conditional TVD: 1.942890293094024e-16.
- Verified 64 array/file hashes across all eight regenerated sibling-comparison cells.
- Executed all three counterexamples above, using temporary files or process-local replacements only.
- Sibling repository independently verified clean at `f6d6ebe87e4ee1de10893c6ea2f0ffa367493336`.
- Full suite: `venv/Scripts/python.exe -m pytest -q`, with a temporary writable Perceval persistence path: **693 passed, 1 skipped in 356.04 seconds**. Explicit optional sibling integration tests were not rerun in this review.
- Confirmed B03 also reproduces with all four registered sizes present and n=4 marked INCONCLUSIVE.
- `git diff --check` passed; the review adds this report and a learning-note addendum only.

The probes are defect reproductions, not production fixes. Tests passing does not close these untested acceptance and continuation cases.
