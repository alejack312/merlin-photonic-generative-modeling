# R1 bucket 2: representation A validation

Date: 2026-10-01. Scope: registered n=2,3 full-Fock fixtures; final-only
projection. No device-profile grid, timing pilot, representation B, or physical
claim. Budget: 75 focused minutes. Start: 15:41:41 UTC (17:41:41 Paris).
Focused-time accounting uses the owner's correction below: wall elapsed time
includes a transit pause and must not be charged as focused work.

## Changed files and model boundary

- `src/merlin_iqp/deploy/noisy_fock.py`: representation A and run accounting.
- `src/merlin_iqp/deploy/__init__.py`: export the new result and evaluator.
- `tests/v4_completion/test_r1_representation_a.py`: independent oracles and
  process-local mutation switches; original null adapters remain unchanged.
- `docs/audits/r1-a-evidence/*.txt`: actual mutation failures and subsequent
  focused green output. This report and the project learning note document scope.

The density is a mixture of tensor products over orthogonal hidden species.
Each factor is an actual complex Fock density matrix, with off-diagonal
coherences retained through the whole passive circuit. Factors are evaluated
one at a time and their measurement diagonals convolved; no pure-state
environment dilation is implemented. Every retained emission branch has total
photon number <= n+c. Full spatial sectors include gate ancilla modes, initially
in vacuum. Reusing a species' computed density does not merge its label with
another species or reset labels at gates.

Explicit modeling convention: a desired photon belongs to the common species
with probability sqrt(V), otherwise to its own pulse-private species. Two
desired photons then share a species with probability V. Every extra photon is
orthogonal to all desired photons and other extras. V alone does not uniquely
specify higher-order distinguishability; this common/private convention is
declared in diagnostics, not attributed to a hardware calibration.

Loss uses K_l |r> = sqrt(C(r,l) eta^(r-l) (1-eta)^l) |r-l> and sums K rho K†.
The same eta acts on every photon and every optical mode. Uniform attenuation
commutes with a passive unitary: mixing the identical vacuum loss environments
by the same unitary leaves their vacuum state invariant. Hence applying this
Kraus channel at the input equals applying it after the whole circuit. This
argument does not cover mode-dependent loss or intermediate postselection.
The Fock unitary is constructed by repeated creation operators, independently
of Perceval's many-photon probability computation. Circuit wiring/unitary is
shared with the existing reference, intentionally preserving its conventions.

p2 uses the contract's inversion assuming p1+p2=1. That normalization is an
explicit model assumption; its hardware applicability is not established here.
Brightness is not applied. The reported acceptance is measured observable
logical acceptance, not the contract's fixed-photon eta^n baseline. Rejected
retained mass + accepted mass + ignored mass = 1. True detected-photon sector
masses and detector-observed outcome masses are both retained. Threshold
conditioning means one click per logical rail pair and vacuum ancillary clicks;
it does not mean exactly n true photons. The true-sector conditional accessor
therefore requires PNR.

## Red and green evidence

The first test-only run failed collection before implementation: missing
`merlin_iqp.deploy.noisy_fock` (exit 1, 11.10 seconds). A provisional 24-test
green run established numeric values. Deliberate mutations then failed the
ordinary oracle assertions, followed by the final unmutated green run. This
is the precise chronology; mutation failures were not expected-failure tests.

Reproduce: set `R1_MUTATION` to the named mutation in a temporary PowerShell
process; run `venv/Scripts/python.exe -m pytest -q -s
tests/v4_completion/test_r1_representation_a.py -k <selector>`; remove the
variable and run the complete file unmutated. Mutations are monkeypatched into
the production helper/evaluator in that test process only.

| Oracle / mutation | Selector | Red evidence (exit 1) | Subsequent green gap |
|---|---|---|---|
| NULL 1 / `ideal_corruption` | `test_null_1` | 3 fail, 1 pass; n3 TVD 0.26149, 0.28959, 0.33559 | Max TVD 2.95e-17; max acceptance gap 8.88e-16 |
| NULL 2 / `wrong_eta_exponent` | `test_null_2` | 4 fail; acceptance gaps 0.0195922, 0.000305752, 0.0000403105, 0.000257076 | Max conditional TVD 8.11e-17; max acceptance gap 5.43e-20 |
| NULL 2 / `dropped_normalization` | `test_null_2` | 4 fail; conditional gaps 0.488448, 0.0511546, 0.00674425, 0.0430108 | Same NULL 2 bounds |
| Pulse oracle / `wrong_p2` | `test_owner_pulse_oracle` | 6 fail; max gaps 0.013985..0.147422; n2 eta=.5 gap 0.0163223 | Max sector gap 1.06e-15 |
| g2>0 / `posthoc_loss` | `g2_loss_changes or no_gate_g2` | 2 fail; both conditional TVDs are 0, below required 1e-3 | Logical bystander TVD 0.0964797198862; true-n no-gate TVD 0.120386144236 |
| Threshold / `detector_mass` | `test_threshold_merges_and_conserves_mass` | 1 fail; outcome gap .0275625; mass gap .1 | Outcome gap 0; mass gap 2.23e-16 |

The ideal mutation intentionally survives the deterministic no-gate fixture;
the three nonuniform n3 fixtures reject it. NULL 2 also checks nonuniformity
and that lossy acceptance differs from 1 by more than 1e-3.

The owner's rounded n2 example at p2=.1, eta=.5 is reproduced as the exact
values {0: .225625, 1: .475, 2: .27375, 3: .025, 4: .000625}. At eta=1,
vacuum probability is exactly zero. The pulse oracle uses c=n to retain all
2n emissions; c=1 cannot reproduce this untruncated oracle, because the two
extra-photon branch is intentionally omitted. A separate c=1 test subtracts
that branch's independently derived binomial loss distribution, verifies .99
retained mass at n2/p2=.1, and checks the ignored-mass flag including its exact
>=1e-3 boundary.

Threshold merges (no-gate n2, p2=.1, eta=.5, c=2), occupations ordered by mode:

| Click outcome | PNR outcomes merged |
|---|---|
| (0,0,0,1) | (0,0,0,1), (0,0,0,2) |
| (0,1,0,0) | (0,1,0,0), (0,2,0,0) |
| (0,1,0,1) | (0,1,0,1), (0,1,0,2), (0,2,0,1), (0,2,0,2) |

Vacuum remains vacuum. All masses are absolute; no interpretation is assigned.

## Ignored mass at c=1

Calculated source-tail probability: P(Binomial(n,p2)>=2). It is independent of
eta, V, detector, and circuit because the emission cutoff precedes loss. Values
below apply separately to both PNR and threshold profiles; these are accounting
checks, not the bucket-3 noisy profile grid.

| Source profile | Detector profiles | n=2 | n=3 | Flag >=1e-3 |
|---|---|---:|---:|---|
| Ideal (g2=0) | PNR, threshold | 0 | 0 | false for both n |
| Ascella anchor (g2=.00732) | PNR, threshold | 1.359425569954e-5 | 4.068252200001e-5 | false for both n |
| Belenos anchor (g2=.019) | PNR, threshold | 9.379737044554e-5 | 2.795752742322e-4 | false for both n |

## Analytic limits and explicit gaps

- V=1, g2=0: all four registered full-Fock fixtures recover ideal probabilities
  and acceptance; eta=.152 obeys the source-photon eta^n null.
- V=0, g2=0: each primary is an independent categorical draw with probabilities
  |U(mode,input)|². Independently convolving these draws checks all registered
  fixtures (including shared gates); numeric gaps are in the green log.
- Balanced two-input splitter toy unitary: P(coincidence)=(1-V)/2;
  P(two photons in either output)=(1+V)/4. Density construction is checked at
  V=0,.4,1, with max gap 2.23e-16. This is an analytic unit test, not a profile run.
- Kraus completeness, trace preservation, off-diagonal damping, and propagated
  density coherence/positivity are checked separately.
- No independent analytic distribution oracle is supplied for generic 0<V<1
  n3 CP circuits, or their joint g2>0/loss variants. The pulse-total oracle and
  special limits do not close that distribution-level gap. No self-comparison
  is substituted. Higher-order distinguishability is model-dependent.
- Final/intermediate projection comparison, representation B, cutoff convergence
  sweeps, device calibration, profile-grid runs, and timing pilots remain deferred.
- Referenced global `review-gates.md`, `learning-law.md`, `brown-engineering.md`,
  and `agentic-collaboration.md` were absent at their supplied paths. Local
  CLAUDE GATE-02/03, project learning notes, and extract-approach were read.
- Python-only repository: no tsconfig/package.json, configured lint command,
  or Python type checker; tsc and npm lint/test are inapplicable. Python suite,
  compilation, and diff whitespace checks are the executable gates.

## Verification and focused-time accounting

- Unmutated focused run after all changes: **35 passed in 16.38 seconds**.
- Full repository run: **870 passed, 1 skipped in 3269.44 seconds (54:29)**.
  This run collected the first 30 new tests. Five additional analytic/flag tests
  were added while it ran; all five pass in the final 35-test focused run.
  No production code changed after that full-suite run began. A second full-suite
  invocation collecting all final tests was started after the owner's focused-
  time correction: **875 passed, 1 skipped in 426.22 seconds (7:06)**, exit 0.
  Actual output: `r1-a-evidence/full-suite.txt`. The collection gap is closed.
- `venv/Scripts/python.exe -m compileall -q` on the new evaluator and tests:
  exit 0. `git diff --check`: exit 0.
- The skip belongs to the existing suite; the focused representation-A suite
  has zero skips. No profile runs or timing pilot were executed.
- Local commit only; no push. Suite wall duration is verification evidence,
  not a device/circuit timing pilot or a measurement of focused work.

Budget correction (owner, during local-commit preparation): "I was in transit
home, so you haven't actually been running for 65 minutes, more like 30."
The earlier 66m34s clock difference was wall elapsed time, not focused time.
Use approximately 30 focused minutes at that correction, plus subsequent active
work. No cap extension was requested or assumed. Final estimate is recorded
after the final full-suite invocation and local commit.

Final verification checkpoint: 16:57:49 UTC (18:57:49 Paris). Estimated focused
time through commit: **about 40 minutes / 75-minute cap**, using the owner's
approximately 30-minute correction plus subsequent active verification and
commit work. This is an estimate, not a stopwatch measurement. The 7:06 fresh
suite confirms that the earlier 54:29 wall duration must not be charged as
54:29 of focused work. No budget overrun or analytic-oracle substitution.
