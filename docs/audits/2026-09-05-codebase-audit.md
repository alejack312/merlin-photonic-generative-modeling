# Current-codebase audit — 2026-09-05

Audited checkout: `2ab4b90` (merged v3.1 correction). Scope: Python library, experiment runners, regression tests, active scientific claims, and static inspection of Julia/Forge verification paths. Historical retractions are distinguished from active assertions. This audit changes no implementation, experiment data, or owner-authored interpretation.

**Overall: FAIL for current scientific-claim reliability.** The existing Python suite passes, but additional probes expose defects and unsupported surviving conclusions. This is not a claim that every implementation or prior result is invalid.

## Verification evidence

- `venv/Scripts/python.exe -m pytest -q`: **451 passed in 323.27 s**. Initial sandbox attempt stopped during collection because Perceval could not write its AppData log; the authorized retry completed.
- `venv/Scripts/python.exe -m pip check`: **No broken requirements found.**
- `venv/Scripts/python.exe -m compileall -q src scripts tests`: completed successfully.
- `venv/Scripts/python.exe docs/audits/2026-09-05-probes.py`: completed; outputs in `2026-09-05-probe-results.json`.
- `venv/Scripts/python.exe docs/audits/2026-09-05-additional-probes.py`: completed; outputs in `2026-09-05-additional-results.txt`. Temporary synthetic chunk files are isolated from real results.
- No TypeScript project or configured Python lint/type-check gate is present in `pyproject.toml`; `tsc` is not a meaningful check of this Python library.
- No full sweep, training run, Julia numerical verifier, or Forge solver suite was rerun. No new assertion that their historical results all remain reproducible is made.

Priority: P1 = resolve before reusing a scientific conclusion or affected analysis; P2 = actionable correctness/verification defect. Proposed corrections below are recommendations, not implemented fixes.

## 1. P1 — The correction mistakes exact classical evaluation for a circuit-independent null

Locations: `docs/trainability-study.md:35-43`, especially line 37; `README.md:29`; `tests/v3_correction/test_null_results.py:242-299`.

The active correction says that reproducing the gradient decay without photonics means it cannot be a property of the circuit's loss landscape. But `_product_q` implements exactly the weight-1 circuit's parameterized probabilities, and `_mixed_q` explicitly calls `exact_qubit_iqp_distribution` with the original fixed ZZ pair. Both retain the parameter dependence of the original model. Finite-differencing the same `MMD2(p,q(theta))` necessarily computes its same landscape, regardless of the simulation substrate.

The valid conclusion is narrower: this measurement is classically reproducible and provides no evidence of a specifically photonic, entanglement-driven effect. Loss-induced concentration can still be a property of the chosen circuit-plus-objective. An exact alternative simulator is not a control in which the model contributes nothing. Nor does the current small-n evidence establish an asymptotic barren plateau.

The source literature itself analyzes MMD concentration for product ansatzes: [Rudolph et al., Theorem 2 and Fig. 6](https://arxiv.org/html/2305.02881v2). Its assumptions differ from this spatial-grid experiment, so it should neither be used to prove this experiment has a plateau nor dismissed because the model is a product.

Recommendation: replace the categorical denial of a landscape effect with the limited conclusion above; distinguish exact reference implementations from mechanism-removing controls. Preserve the retraction of the original photonic claim.

## 2. P1 — The tested mixed family is also efficiently classically sampleable

Locations: `docs/hardness-under-loss-study.md:15-19,33,57`; `README.md:31`; `src/merlin_iqp/trainability/sweep.py:169-175`.

The live scope precondition calls only the mixed rows hardness candidates and links their conditional hardness to general IQP conjectures. The actual construction has just one interacting pair `(0,1)` plus independent single-qubit gates. Its distribution factorizes:

`P(x) = P_01(x0,x1) * product_{k>=2} P_k(xk)`.

The audit evaluates the two-qubit factor and single-bit factors separately and compares them to the full exact reference at n=2,3,5,8. Maximum absolute discrepancy is **1.11e-16**. Sample one four-outcome variable and n-2 biased coins: O(n) work per sample. The fixed-size photonic gate block likewise does not acquire a growing interaction component just because more disconnected photons are added.

Thus neither tested family inherits generic IQP sampling-hardness conjectures. Entanglement in one constant-size block is insufficient. The September 4 literature note already notices that the mixed connectivity is disconnected, but this has not propagated into the headline scope statement.

Recommendation: classify both families as easy controls; retain the conditional shape and throughput statements within their assumptions. Any future hardness study needs a separately justified scalable circuit family, not merely the presence of one ZZ gate.

## 3. P1 — TRAIN-10 does not establish the retained negative initialization result

Locations: `src/merlin_iqp/trainability/sweep.py:109-157`; `docs/trainability-study.md:43,215,239`.

TRAIN-10 uses one deterministic parameter vector per n, then takes variance across different parameter coordinates. The random-init comparison pools coordinates AND random parameter draws. These are different quantities. At n=3, the deterministic weight-1 gradient vector is:

`[0.00747760974951, -0.00890393489046, 0.000119744043962]`.

Its pooled variance is **4.4879997116e-05**. Repeating the deterministic initialization twice gives exactly the same vector; each coordinate's variance across draws is **zero**. A curve fit to the spread across coordinates at one point cannot establish that a warm-start method failed to improve trainability. An inconclusive fit is also not affirmative evidence that an intervention failed.

For mixed scope, the covariance initializer overwrites two single-qubit Z angles while the ZZ angle stays fixed at pi/4. The document discloses this adaptation, so it is not an undisclosed implementation change. But it is not a direct test of initializing the pair angle using the literature recipe. [Recio-Armengol et al., Sec. 8.1.2](https://arxiv.org/html/2503.02934v2) distinguishes those gate parameters.

Recommendation: retract the surviving claim of a genuine negative literature-init result. Describe the experiment as a deterministic initialization diagnostic; choose a matched ensemble or an actual optimization comparison before assessing the remedy.

## 4. P1 — The plateau classifier accepts increasing curves and nonzero asymptotes

Locations: `scripts/v3_trainability/trainability_analysis.py:123-140`; corresponding classifier in `trainability_analysis_1701.py:170-187`; `src/merlin_iqp/trainability/curve_fit.py:8-11`.

The classifier checks only `b > 0` for `a*exp(-b*n)+c`. The sign of the derivative depends on `-a*b`, not b alone. The independent probe supplies the strictly increasing sequence `1-exp(-0.8*n)`, n=2..8. The real fitter returns approximately `a=-1,b=0.8,c=1`, verdict `exp`, and the classifier returns **plateau**.

Even when a and b are positive, unrestricted positive c means variance approaches a nonzero floor. Winning an exponential-with-offset fit is not evidence of exponentially vanishing variance.

Recommendation: separate finite-range fit shape from a plateau claim; check the derivative and asymptotic assumptions explicitly. Add increasing-curve and positive-floor adversarial cases. The concrete increasing-curve bug is confirmed; this audit does not claim it changed a particular archived CSV verdict.

## 5. P2 — The dual-rail API still contains incorrect equivalence mathematics

Locations: `src/merlin_iqp/encoding/dual_rail.py:21-38,84-110,132-143`; `docs/trainability-study.md:7,245`; contrast `docs/hardness-under-loss-study.md:229-246`.

The library factors `diag(exp(i*theta),1)` into a global phase times `diag(exp(i*theta/2),exp(-i*theta/2))`, then incorrectly calls the latter `exp(i*theta*Z)`. It also calls the default `BS()` its own inverse. These are false as written. The dual-rail function has a different phase and mixing convention from the polarization function.

Direct n=1 probes at identical theta:

| theta | polarization P(0) | dual-rail P(0) |
|---|---:|---:|
| 0 | 1 | 0 |
| 0.3 | 0.9126678075 | 0.0223317556 |
| pi/2 | 0 | 0.4999999702 |

**Important historical distinction:** the hardness document already explains this half-angle/complement mismatch and warns against comparison at identical numeric angles. The discovery is not that this discrepancy was wholly unknown. The remaining defect is the active contradictory API derivation and use of the parallel sweep as an encoding comparison without matching physical initialization and derivative coordinates.

The tests explicitly compare MerLin to bare Perceval on the SAME dual-rail circuit and explicitly disclaim polarization equality. They verify that backend evaluation, not the equivalence claimed by the library prose. For example, theta near zero is near a different physical state in the two parameterizations, and a half-angle reparameterization changes gradient scale by the chain rule.

Recommendation: document and test an explicit mapping for each gate family, initialization distribution, output label, and gradient coordinate, or narrow the cross-check claim. Do not silently alter saved experiments to a new convention.

## 6. P2 — Resumed sweeps silently double-count overlapping chunks

Locations: `scripts/v3_hardness/loss_sweep.py:255-275`; `scripts/v3_trainability/gradient_variance_sweep.py:236-268`.

Both combiners glob every matching file and concatenate arrays without validating draw intervals. A rerun with different chunk sizes can leave overlapping intervals in the same folder.

The probe writes chunks `[0,2)` and `[1,3)` containing per-draw values `[0.1,0.9]` and `[0.9,0.2]`. The loss combiner reports **4 draws and mean 0.525**, while there are **3 unique draws with mean 0.4**. The trainability combiner similarly reports **8 pooled gradients** instead of six and the wrong mean/variance. Neither rejects the overlap.

The trainability filename also omits `scale_factor` and tracked-parameter count, while combination derives the latter from current CLI arguments. Incompatible runs can therefore collide or be mislabeled. This is an operational bug; no claim is made that archived runs actually contain overlaps.

Recommendation: persist a complete cell configuration and interval manifest; reject duplicate/overlapping ranges, gaps when a complete run is requested, and incompatible configurations before combining.

## 7. P2 — A failed competing fit is promoted into a positive model verdict

Location: `src/merlin_iqp/trainability/curve_fit.py:116-119`.

If only one optimizer converges, `fit_and_compare` declares that model the winner without an AIC comparison. The module's documented contract says one or both fit failures yield inconclusive. Numerical failure of an optimizer is not evidence against the competing model.

Recommendation: return inconclusive with convergence diagnostics unless both valid fits support comparison. Static branch defect confirmed. The independent subreview recomputed the 24 TRAIN-09 fits and reported both models converged there; no historical table change is asserted from this branch.

## 8. P2 — Julia verification disagreement does not fail the process

Locations: `julia/verify_photonic_iqp_weight1.jl:223-232` and end of script; `julia/verify_photonic_iqp_weight2.jl:428-433`; `julia/verify_loss_model.jl:480-488` and end of script.

These paths print DISAGREEMENT/PARTIAL-GO/NO-GO and reach normal program termination. Weight-1's TVD assertion is placed only inside the already-all-pass branch. A command runner can therefore observe exit status zero despite a failed final comparison. Some earlier structural assertions do fail correctly; that does not protect final numeric comparisons.

Recommendation: retain the diagnostic report and then exit nonzero if any required comparison fails. This is a static control-flow finding; no original reference CSV was corrupted to force a failure, and no fresh Julia numeric run is claimed.

## 9. P2 — The null-result regression gate can silently stop checking its evidence

Locations: `tests/v3_correction/test_null_results.py:176-179,190-193,199-202,220-231`.

Missing CSVs are silently skipped during parametrization; returning None still calls `pytest.skip`. These are unfinished scaffold behaviors in a supposedly mandatory shipped gate. In addition, TRAIN checks ratios only, so multiplying every variance in a series by the same wrong factor leaves the tested ratios unchanged. The ratio function hardcodes sigma=0.1 while cases also contain sigma=0.03. The original Phase 17 CSV is absent from `TRAIN_CSVS`.

Recommendation: require the expected files, row counts, scope/bandwidth coverage, and completed formulas. Test same-seed absolute gradients or variances at the row's actual sigma in addition to ratios. The current 451-pass result is real, but does not establish the stronger complete-reproduction claim.

## 10. P2 — The new MBQC literature summary misstates the construction

Location: `docs/iqp-lit-scoping.md:110`; related broad wording in `Post_Sept1_IQP_Photonic_Plan.md:24`.

The full-read addendum describes fixed X-Z-plane measurements chosen from each qubit's own angle as the general IQP implementation. [Hoban et al., Fig. 1 and Lemma 3](https://arxiv.org/pdf/1304.2667) instead explicitly constructs gate/resource qubits and accounts for commuting Z byproducts. Its Fig. 1 angle-dependent observable is `U_X(-theta) Z U_X(theta)`, which lies in the Y-Z plane; the appendix uses another graph-state presentation involving equatorial measurements. These presentations cannot be collapsed into the stated universal X-Z recipe. General multi-qubit diagonal gates cannot simply be absorbed into one local measurement angle per original qubit.

Recommendation: summarize nonadaptivity accurately, including auxiliary resource qubits and classical byproduct handling where applicable. Specify a convention and its source figure before deriving a photonic resource budget.

## Additional correction drift and lower-priority observations

- `docs/trainability-study.md:35` still attributes `rel=0.5` to the kernel at large n. The code and decision log say this was a wrong diagnosis of a parameter-pooling bug; the current threshold is 0.2. This is active correction prose, not struck-through history.
- `julia/generate_reference.py:124-128` says asymmetric local angles make all four fixed-CZ probabilities distinct. The weight-2 Julia verifier correctly explains the unavoidable equalities P00=P11 and P01=P10. The comment overstates the regression's label-error coverage.
- README's 'same circuit family' description of v1 and v3 is misleading: v1 constructs MerLin's generic `QuantumLayer.simple`; v3 builds the explicit commuting IQP encoding. Shared framework and MMD methodology do not establish the same ansatz.
- The throughput table is broadly consistent with its stated formula but contains small arithmetic/rounding drift: eta=.6,n=6,k=1 is 803.755 (table 806); eta=.9,n=6,k=2 is 522.688 (table 524). Generate the table from code rather than transcribing approximate values. Its n=8 and mixed n=6 rows are outside the documented measured range even in k=0/1 columns, as the later caption partly acknowledges.
- `backtracking_min_colouring` checks its timeout only between calls to recursive `_try_colour`; the recursive search has no deadline. A hard timeout is not enforced inside the expensive operation. Static limitation confirmed, long-running timeout reproduction not performed.
- Planning headers still describe pending work already merged; current requirement/owner-understanding completion cannot be inferred from those headers alone.

## Coverage and remaining uncertainty

The audit reviewed active source contracts and analysis logic and traced claims to tests, saved data, and selected primary papers. Independent subreviews covered encoding/loss, generator/trainability, and verifier paths; those workers hit an account usage limit before producing final reports. The main audit independently reproduced the numerical findings reported above; their unverified candidates are not presented as numerically established.

No new generator-training arithmetic bug was established. No new error in the polarization parameter-shift formula or single-gate survival formula was established. These limited negative findings are not blanket certifications. Fresh Julia/Forge execution, every paper/theorem, every stored result row, and every operating-system/install combination remain outside completed coverage.

## Suggested order of repair

1. Correct the unsupported surviving scientific claims (items 1–3) and mark affected evidence accurately.
2. Repair analysis/verification contracts (items 4,6–9) with adversarial tests before any new sweep.
3. Resolve/document the physical parameter mapping (item 5), then decide which comparisons need rerunning.
4. Correct literature framing and stale explanations before choosing a v4 experiment.

The owner's existing technical-note edits were preserved. No source fixes, experiment reruns, commits, external messages, or public updates were made.
