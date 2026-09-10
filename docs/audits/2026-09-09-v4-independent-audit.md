# Independent v4 audit — 2026-09-09

Reviewed head: `40df0dc`. Base: `de80e9313beed614528fd6332b2f78aab83c0b50`.

Verdict: **changes required before release**. Four independently reproduced findings follow. The projection finding invalidates an existing numerical conclusion. The other findings expose acceptance or input-validation failures; they do not by themselves establish that the saved nominal distributions are wrong.

## Scope and method

Read the reviewer handoff and relevant ledger/study claims, inspected the classical objectives, compiler and density path, CP reconstruction, direct optical simulation, ring deployment gate, comparison metrics, NAT contracts, and sibling comparison path. Used independent numerical and fault-injection probes rather than treating existing tests or saved PASS labels as proof. This is not a claim to have exhaustively inspected every line of the approximately 805-file base-to-head diff, which includes generated evidence.

Implementation, canonical results, sibling files, and owner-authored material were left unchanged. Runtime probes temporarily replaced functions in isolated Python processes. The existing untracked wrap-up recommendation was preserved. No sweep, retraining, merge, or publication was performed.

## A01 — P1: Intermediate projection loses coherence at final readout

Location: `src/merlin_iqp/deploy/fock.py:237–245`.

The intermediate path correctly retains amplitudes through its CP stages, but the final readout squares each input-to-output contribution separately and adds the resulting probabilities. Distinct retained basis components are coherent. For each output state, their amplitudes must be summed before taking the squared magnitude. The current calculation introduces an unrequested dephasing operation immediately before readout.

Independent probe: run the registered shared-gate fixture with n=3, singles `[0.17, -0.24, 0.36]`, pairs `[(0,1,0.20), (1,2,0.30)]`, and eta=1. In an isolated process, change only final-readout accumulation from `sum(abs(amplitude)**2)` to `abs(sum(amplitude))**2` for each accepted output. Accepted logical bitstrings uniquely identify accepted output Fock states under the vacuum-ancilla, one-photon-per-qubit predicate used here.

| Quantity | Current implementation | Coherent readout probe |
| --- | --- | --- |
| TVD against final-only | 0.585411845271861 | 1.942890293094024e-16 |
| Intermediate accepted mass | 0.013536031512283192 | 0.013536031512283192 |
| Final-only accepted mass | 0.013536031512283199 | 0.013536031512283199 |

All calls returned PASS. The large recorded discrepancy is a simulation error, not evidence of a projection-placement effect in this fixture. This finding does not prove general equivalence for arbitrary circuits or sources.

The error has been incorporated into the acceptance contract: `src/merlin_iqp/deploy/ring.py:100–101` requires a discrepancy above 0.001. Thus fixing the physics alone makes corrected evidence fail the ring gate. `DEPLOY-04` in the ledger and several study documents repeat the erroneous number and conclusion, including the factual premise supplied to the owner explanation.

Required repair: preserve coherent amplitudes at readout; add an independent reference test; replace the discrepancy-required gate with a physically justified fixture expectation; regenerate affected manifests and dependent ring evidence; correct the ledger and study claims. Present the correction to the owner rather than silently rewriting their explanation. Do not infer a universal projection theorem from either result.

## A02 — P1: Full-Fock normalization hides missing probability mass

Locations: `src/merlin_iqp/deploy/fock.py:176–178` and `:352`.

`_final_distribution` only requires positive finite total mass, then divides accepted mass by that total. Consequently, incomplete or misnormalized backend output is silently promoted to a normalized instrument. The reported reconciliation error is `1 - (p + (1-p))`, a tautology rather than a measurement of backend mass conservation.

Independent fault injection: wrap `Simulator.probs` so every returned probability is multiplied by 0.5, then run the n=2 no-gate control at eta=1. The adapter returns **PASS, accepted mass 1.0, reconciliation error 0.0**, despite the backend returning only half the expected mass. This demonstrates the gate failure; it does not assert that the normal backend currently loses half its mass.

Required repair: validate finite, nonnegative outcome probabilities and total mass against the normalized input with an explicit numerical tolerance. Preserve and report the measured total and actual residual. Reject or qualify material missing mass instead of renormalizing it away. Compare acceptance with an independent expected instrument where the control provides one.

## A03 — P2: The sibling unquantized compilation control cannot fail

Location: `scripts/v4_tcdp/compare_sibling_backends.py:386–418`.

The script computes and labels an `ideal-unquantized-control` arm but never asserts equality between that arm and the source/local IQP reference. Source/local equality checks compare the two raw IQP implementations; compiled/deployed checks compare the map with itself under uniform scalar loss. Neither tests lossless, unquantized compilation equivalence.

Independent fault injection: load the existing training-smoke record and replace only the first `apply_compiled_density` result, the unquantized arm, with a valid point-mass distribution. Leave the other arms untouched. `_build_cell` completes with source and output checks marked **PASS**, while the corrupted unquantized arm has **TVD 0.9999999999379847** against the local IQP vector.

Required repair: record and enforce source/local-versus-unquantized equality per cell, with a declared tolerance and an injected-distribution mutation test. Keep the expected quantization gap separate. This is a missing verification gate, not evidence that the stored unquantized arm is currently corrupted.

## A04 — P2: Public spatial MMD accepts an invalid kernel mixture

Location: `src/merlin_iqp/classical/objectives.py:39–45`.

`spatial_mmd2` normalizes mixture weights without requiring finite nonnegative weights, positive finite bandwidths, or finite valid centers. Unlike the typed training path and Hamming helpers, this public calculation can return an invalid value labeled MMD².

Independent probe:

```python
spatial_mmd2(
    np.array([1., 0.]), np.array([0., 1.]),
    np.array([[0.], [1.]]),
    sigmas=[0.1, 10.], weights=[-1., 2.],
)
# -1.9800499167707293
```

A squared MMD for the intended positive-semidefinite Gaussian mixture cannot have this large negative value. The typed `KernelSpec` path rejects these weights, so this probe does not invalidate the nominal trained-ring results.

Required repair: reuse the shared kernel-mixture validation, validate centers and matching vector dimensions, and avoid mutating a caller-provided NumPy weights array during normalization. Test negative/zero-total/nonfinite weights and invalid bandwidths.

## Release consequence

The earlier wrap-up recommendation preceded these probes. Scoped closure remains a reasonable destination, but A01 and its dependent scientific claims must be repaired before treating the current release evidence as sound. More expensive experiments are not needed to resolve the demonstrated defects. These findings call for a focused repair and evidence regeneration pass, not reopening every deferred research question.

## Verification

The four fault-injection/numerical probes above were executed against the reviewed code.

- Full suite: `venv/Scripts/python.exe -m pytest -q`, with `PCVL_PERSISTENT_PATH` set to a temporary writable directory: **687 passed, 1 skipped in 601.71 seconds**. Explicit optional sibling integration was not rerun; the A03 probe did load the existing sibling training-smoke input and source model.
- Independent finite-difference checks: 18 Hamming/spatial objective cases across n=2,3,4, using seed 20260909 and step 1e-5; maximum gradient error **3.1135916067626113e-10**.
- Independent unquantized compiler comparison: nine n=2,3,4 cases with random angles in [-8,8]; maximum probability error against the classical IQP model **4.440892098500626e-16**.
- Canonical physical manifest independently read back: PASS with the erroneous shared-gate TVD **0.585411845271861**.
- `git diff --check` passed. Only the audit report and a reusable learning note were added; the pre-existing untracked wrap-up document was preserved.

The passing suite does not cover the four counterexamples. Random numerical agreement supports the exercised gradient/compiler cases, not arbitrary inputs or every deferred scientific requirement.
