# Adversarial audit of v4.0 plan revision 2

Date: 2026-09-05. Reviewed starting checkout: `bdbcf88`; revision-2 origin: `3f9cb92`; sibling source inspected: `4e5bfc43e325029d7cc760bc2c355afa2d6461e4`. Existing dirty `docs/trainability-study.md` and `.planning/phases/06-documentation-publication/06-technical-note.md` were not edited by this audit. A concurrent documentation commit moved HEAD to `c280c67` during verification; it does not change the audited v4 plan or code. Scope: the plan, prior review/disposition, queued requirements/roadmap, relevant installed Perceval and sibling APIs, primary-source checks and small executable probes. No v4 production implementation or full noise sweep was performed.

**Verdict: revision 2 was not executable as a defensible scientific study. Six blocking contracts and sixteen additional major findings remain despite its earlier disposition.** Revision 3 corrects the mathematical and execution contracts and explicitly leaves three scientific design choices open. This audit is complete; the proposed production experiment is not approved or validated by it.

Evidence is reproducible with:

`venv/Scripts/python.exe docs/audits/2026-09-05-v4-plan-probes.py`

The script asserts the expected controls/counterexamples and writes [numeric results](2026-09-05-v4-plan-probe-results.json). It uses an independent explicit IQP amplitude sum and installed Perceval circuits, not a new implementation of the planned simulator. Numbers below are rounded for reading; the JSON retains precision. An assertion PASS means the audit reproduced its stated finding, not that the old plan passed.

## Blocking findings

### V4-01 — Loss invariance does not extend to multiphoton sources

Revision 2 §§0, 4.2, 4.6, 5.1 exclude eta from the map key and multiply acceptance by eta^n for the entire g2 grid. That theorem assumes a fixed photon number. With multiphoton emission, losing extra photons can still leave an accepted detection pattern, changing the conditional mixture.

**Verified:** n=2, singles (.3,.7), pair theta=.3, V=1. At g2=0, eta=.5 preserves q and divides success by four. At g2=.025 the conditional distribution differs from ideal by TVD .0081128358 at eta=.5, versus numerical zero at eta=1. Success/eta² changes from .1000536163 to .1045652725. This is not roundoff.

**Disposition:** corrected restricted theorem; joint source/loss model must include eta. Owner D1 chooses physical scope. A g2=0 study is possible in principle; the old full-grid physical claim is not.

### V4-03 — Full-Fock reference has the wrong phase-shifter sign

Revision 2 §4.5 uses PS(+2theta) on the logical-1 rail and calls it exp(+i theta Z). Its diagonal is (1,exp(+2i theta)), which is exp(-i theta Z) up to global phase. The sign applies to both single angles and CP compensation phases.

**Verified:** the specified positive-sign construction has TVD .4426511459 from the intended n=2 model. Negative signs agree to 3.75e-16. A full-Fock “reference” following the old plan would reject a correct qubit simulator or encourage fixing the wrong side.

**Disposition:** corrected compilation identity, negative signs, independent sign-mutation fixture.

### V4-04 — Modulo-CP wrapping discards physically relevant local operations

Revision 2 §§4.2, 5.1 set theta_eff=alpha_key/4 after reducing alpha modulo 2pi. But theta and theta+pi/2 in exp(i theta ZZ) differ by i ZZ, not only global phase. Wrapping CP without preserving the corresponding local compensation changes the model.

**Verified:** theta=.2 versus .2+pi/2, same singles (.3,.7), gives TVD .7601844419 even though the CP key is identical.

**Disposition:** preserve the nearest integer winding/lift when quantizing theta; keep wrapped CP keys and lifted compensation angles separately. Boundary, negative-angle and adapter tests required.

### V4-05 — The noiseless control contradicts the quantized reference

Revision 2 §§5.2, 5.6, 10 demand zero TVD against the trained unrounded model at every noiseless control point while deploying rounded parameters. Adding a rounding column does not fix that contradiction.

**Verified:** pair theta=.311 rounds to .300 under the old grid, producing TVD .0052082208 at ideal noise. A 1e-12 equality assertion must fail.

**Disposition:** three references: raw trained, ideal compiled, noisy compiled. Ideal-map controls compare the last two. Noise-only and total TVD are different columns/curves. Triangle bounds replace any additive decomposition claim.

### V4-06 — NAT's proposed gradient cannot optimize the pair angles

Revision 2 §6 rounds pair angles before evaluating an h=1e-4 central difference. Away from bin boundaries both evaluations use exactly the same map and compensation angle. At a boundary it estimates a jump divided by 2h, not a useful smooth derivative.

**Verified:** 99.19% of 10,000 seeded angle probes select identical keys for theta±h. The typical theta bin width is .025. This cannot substantiate adaptation of every n+k parameter.

**Disposition:** owner D2 chooses a discrete-key optimizer with continuous singles or a validated continuous model. No silent interpolation, straight-through gradients, or switch to singles-only optimization. The universal statement that parameter-shift cannot apply to a channel was also removed: applicability depends on the parameterized map and conditioning.

### V4-08 — “Verbatim” vendoring cannot supply the promised exact target training

Revision 2 §§2–3 omit Trainer dependencies (`IQPModel`, checkpoint helper, RNG constants/derive_seed). Prefix replacement does not resolve the proposed flattened package. More fundamentally, the sibling Trainer casts `data` to uint8 and its exact-small-n loss takes samples, not an exact probability vector. The plan prohibits samples at n<=10 yet demands verbatim functions needing them.

**Verified by source:** `training/trainer.py` imports at lines 12–17, data conversion at construction; `mmd/loss.py::mmd2_exact_small_n` calls empirical dataset expectations; `experiments/initialization.py` likewise requires sample-derived moments. “Exact” refers to circuit/observable enumeration, not an exact supplied target vector.

**Disposition:** explicit import closure and target-moment adaptation shared across objective, gradient and initialization; independent weighted-vector tests and import isolation. Phase 26 becomes an accurately specified adaptation rather than an impossible copy instruction.

## Additional major findings

| ID | Revision-2 location | Finding and evidence | Revision-3 action/status |
|---|---|---|---|
| V4-02 | §§4.1–4.5 | Source emission is applied again in each gate map; spectators have none. One noisy gate's acceptance ratio is .974519 at n=2 but .962023 with a bystander at n=3. The latter is source acceptance, not leakage into disconnected rails. | Source once per input event; record number-sector and spectator effects; D1 pending. |
| V4-07 | §§5.2,6 | Ideal NAT need not preserve the original trained parameters or metrics: another 150 optimization steps can improve an unfinished 300-step fit. MMD-to-target optimization also need not reduce distance to the original ideal-trained distribution. | Same-parameter ideal-map equality plus equal-budget continued-training control; separately report objective and reference distances. |
| V4-09 | §§3.1,5.1 | Data-dependent method/scale are missing. The actual sibling defaults to parity, scale .1; covariance is a different branch. For the zero-field target this makes singles zero and leaves training in a parity-conserving stationary subspace. At n=4 the initialized odd-parity mass is 3.47e-33, target odd mass .681240, and single-angle central derivatives are <=1.12e-11. | D3 requires explicit recipe and short training diagnostic before primary runs. No silent jitter or method change. |
| V4-10 | §§5.1,5.6 | Five seed IDs with exact deterministic initialization/updates need not provide five distinct runs; reported seed variability may be identically zero. | Persist parameter hashes, n_unique and actual randomness source; no pseudoreplication. D3 defines replication unit. |
| V4-11 | §5.4 | Every deployable Ising probability exceeds 1e-6: S has 16/64/256/1024 states at n=4/6/8/10. Thus fidelity_pop=sum_S q=1 for every normalized q. It cannot measure deployment quality. | Keep support-validity as annotated constant; use informative target-distance metrics already available. Do not change target merely to get a nonconstant score. |
| V4-12 | §5.2 | Changing one q entry violates normalization; requiring every metric to change is impossible. Gate success/fidelity do not depend on the mutated q, support validity is constant, and some marginal changes cancel. | Mass-preserving metric-specific fixtures; independent mutations of acceptance/map fields; constants tested as constants. |
| V4-13 | §§4.1,7 | CP-map composition is exact for a sequence of success instruments, not automatically final-only post-selection. The repeated-rail, fresh-ancilla probe gives a .463774 maximum amplitude difference between final-only and intermediate projection. This counterexample is outside the proposed one-pass chain and must not be misreported as a failure of that chain. | Require a no-return/projection proof for the restricted topology/order and reject unsupported circuits. Separately handle hidden-label memory and source sectors. Per-step normalization with tracked success products is algebraically valid; only treating it as linear TP or discarding factors is wrong. |
| V4-14 | §4.3 | Product-input trace tests do not prove trace nonincrease. A CP map E(rho)=1.1 <Bell|rho|Bell> |00><00| has success <=.55 on every product state but 1.1 on Bell. Off-diagonal matrix units are not Hermitian states either. | Eigenvalue test of E_dagger(I)<=I; Choi CP; E(Eij)^dag=E(Eji); independent vectorization/Kraus fixtures. |
| V4-15 | §§4.2–4.3 | “Exact average fidelity of the normalized map from Choi” is undefined when success depends on input. Haar average of a ratio differs from ratio of averages. Arbitrary .005 agreement with differently normalized tomography is not a validation contract. | Define success-weighted Haar fidelity explicitly and test it against Kraus/Haar calculations; tomography remains a labeled secondary diagnostic. |
| V4-16 | §4.5 | A maximum error on a few n=3 points is not an error bound for n=10, other angles/noise points, KL or coverage. The success discrepancy has no decision rule. Reusing the same pair angle narrows coverage. | Keep .01/.05 only as small-n triage; record absolute/relative acceptance error; asymmetric and differing-angle fixtures; no extrapolated figure error bars. |
| V4-17 | §4.7 | Erasure helper starts from conditional q and omits gate failure even at eta=1; it also forbids erasures on gate participants without specifying a physical measurement that permits/forbids them. It cannot be full non-post-selected output. Multiphoton/collision patterns cannot fit only {0,1,E}. | Distinguish explicitly conditional synthetic output erasure from physical full-Fock outcomes; preserve all failure categories; D1 resolves M5 scope. |
| V4-18 | §§5.1,6; requirements | NAT has m=n+k, giving 15/23/31 evaluations per step and 51,750 total, not 29,250. All stated k at n=16,20 require 1,080 training-only files: 1,920 total, not 900. Queued requirements contain 34 checkboxes, not 32. | Correct counts, preserve all-k axis unless owner changes it, generate manifests; include control overhead and all resource stages. |
| V4-19 | §§3.2,4.3–4.5 | General forward adapter and chain-only inverse conflict; pi/12 test is not alpha=.1*j grid aligned. Random-key-count testing misses deterministic boundary behavior; rank/fit claims do not verify held-out preparations or omitted zero outcomes. | General sorted-pair inverse, independent exact-alpha tests, fixed circular-boundary fixtures, full outcome design and holdouts. |
| V4-20 | §§0,4.2–4.3 | Hardware raw HOM visibility is not automatically the overlap parameter used with g2. Official Perceval tomography uses .9438/.00732. Source defaults and unavailable earlier probe artifacts are load-bearing; SLOS is floating-point, not exact arithmetic. A single key is not demonstrated slowest. | Calibrate parameter meanings, version/hash evidence, source/default/cutoff manifests; regenerate old probes; benchmark representative maximum cost. |
| V4-21 | §§0,5.6–5.7 | Nonzero noise gap is not itself a novel finding or useful model. Re-training as k changes confounds expressivity/angles with gate count; “distinguishability ceiling” at nonzero g2 is causal overreach; ideal chain tractability matters to positioning. | Descriptive curves, same-cell noise ablations, target-fit diagnostics, qualified hardware-inspired labels and scoped literature comparison. |
| V4-22 | §§5.4–5.5,10 | Unnormalized q-floor score is not KL and can be negative; support coverage may saturate. Cache/files lack sufficient configuration hashes and schema checks; missing_cells does not make an incomplete experiment complete. | True KL plus labeled floor diagnostics, stable occupancy computation, vector validation, versioned atomic artifacts, manifest completeness and explicit partial outcomes. |

## Corrected mathematical contracts

- Compilation: `exp(i t ZiZj)=exp(-i t) exp(i t Zi) exp(i t Zj) CP(4t)`, with negative optical phase-shifter signs on logical-1 rails and preserved winding under quantization.
- Three distributions: raw trained, ideal compiled, noisy compiled. The ideal-map control is noisy compiled = ideal compiled. TVD components obey triangle bounds; they do not generally add.
- Physicality: Choi positivity plus `E_dagger(I)<=I`, not sampling trace checks.
- Conditional fidelity: with unnormalized Choi J and `u=sum_i |i> tensor U|i>`, success-weighted Haar fidelity is `(Tr J+<u|J|u>)/((d+1)Tr J)`. The proof uses the Haar second moment; the prospective implementation must still pass Kraus/integration tests.
- Conditioning: sequential `rho_j=E_j(rho_(j-1))/s_j` with `s_j=Tr E_j(rho_(j-1))` gives the same final normalized state as unnormalized composition, and total success is `product s_j`. This does not make the conditional operation linear or equate a changed instrument with end-only post-selection.

## What changed and what remains open

The canonical plan is rewritten as revision 3; the 34 queued requirements and v4 roadmap are synchronized. Old review/disposition files remain unchanged so their incorrect closure claims remain inspectable. The evidence scripts and this report are new. No production library code, source dependencies, v3 results, owner formulas or unrelated dirty files were changed.

D1 (physical/source scope), D2 (NAT representation/optimizer), D3 (initialization and replication) need actual owner choices before dependent production work. This audit supplies the invalidated assumptions and concrete contracts, not fabricated design approval. Restricted source validation and mechanical vendoring preparations can be planned independently, but no full v4 run is authorized by this audit.

## Verification and limits

- Runnable audit probes cover signs, winding/rounding, quantizer gradients, count arithmetic, target support/parity initialization, CP/TNI counterexample, intermediate projection, g2/loss and bystander acceptance. Exact JSON is the numerical record.
- The counterexample circuit uses repeated rails; it is not evidence that the one-pass chain fails at ideal noise. A chain-specific proof remains a gate.
- No complete gate reconstruction, continuous noise model, NAT implementation, hardware execution or n=10 full-Fock validation was done. No extrapolated uncertainty bound is claimed.
- Existing repository suite: **507 passed in 406.70 seconds**, run during this audit with a unique workspace pytest basetemp. A green existing suite does not validate an unimplemented plan. Python lint/type checking is not configured in pyproject.toml; TypeScript checks do not apply.
- Final document checks passed: local links resolve, all 34 requirement IDs are unique, the Phase 25 roadmap tail is unchanged from the starting commit, probe syntax parses, recorded probe assertions are PASS, and the changed plan/requirements/roadmap pass `git diff --check`.

## Sources checked

Primary sources supplement direct local code/probe evidence:

- [Perceval source model](https://perceval.quandela.net/docs/v1.1/reference/exqalibur/source.html): noisy-source Fock-mixture semantics; installed NoiseModel and Processor code were also inspected.
- [Perceval v1.2 tomography](https://perceval.quandela.net/docs/v1.2/notebooks/Tomography_walkthrough.html): source settings, normalization and reported fidelity. Its use of a normalized tomography matrix is not proof that arbitrary input-dependent success becomes TP.
- [Salavrakos et al.](https://arxiv.org/html/2405.02277v3): architecture, detector and setup passages inspected. Its universal-interferometer/threshold-detector experiment differs from this proposal's dual-rail PNR calculation.
- [Recio-Armengol et al.](https://arxiv.org/html/2503.02934v2): retrieved for training context; no new broad conclusion about every deployment variant is asserted.
- [Maring et al.](https://arxiv.org/abs/2306.00874), [Raj et al.](https://arxiv.org/abs/2608.31117), [Xie et al.](https://arxiv.org/abs/2605.11879), [catalog gate reference](https://arxiv.org/abs/2405.01395): identity/abstract-level checks; this audit does not relabel these as new full reads. The failed Maring PDF retrieval was not used as evidence for numerical calibration.
