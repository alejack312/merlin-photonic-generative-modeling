# Independent audit after the v4 repair pass

Date: 2026-09-06. Reviewed HEAD: `b7ed7e8c612b2e3bb96136b3b5e74ee6fd5053d5`.
Full implementation base: `de80e9313beed614528fd6332b2f78aab83c0b50`.
Repair comparison: `4e7cbd7ccd5842a41ec195050469fb1ee1d0c3a7..b7ed7e8`.

**Verdict: changes required. Nine actionable findings remain.** This audit separates working repairs from new defects and incomplete repair integration. It does not treat the already acknowledged missing physical studies or owner explanations as newly discovered bugs.

## Independent verification

- Expanded v4 suite: **129 passed in 106.41 seconds**.
- Full suite: **636 passed in 344.17 seconds**.
- Previously committed repair probes: all seven reported `fixed: true`.
- New counterexamples: reproduced zero-loss spatial training, stale hash acceptance, ablation overwrite, ignored configuration, NaN false PASS, missing source verification and incomplete physical-status aggregation.
- Existing NAT artifacts inspected: primary and warm-start files are byte-identical; only the continuation starts at their final parameters.
- Sibling verified clean at `f6d6ebe87e4ee1de10893c6ea2f0ffa367493336`.
- No changes from the implementation base in legacy `src/merlin_iqp/{generator,encoding,hardness,trainability}`.

Commands used from the repository root:

```powershell
$env:PCVL_PERSISTENT_PATH = Join-Path (Get-Location) '.pytest_cache/review2-perceval'
venv/Scripts/python.exe -m pytest -q tests/v4_tcdp --basetemp .pytest_cache/review2-temp
$env:PCVL_PERSISTENT_PATH = Join-Path (Get-Location) '.pytest_cache/review2-perceval-full'
venv/Scripts/python.exe -m pytest -q --basetemp .pytest_cache/review2-full
venv/Scripts/python.exe docs/audits/2026-09-06-v4-implementation-probes.py
venv/Scripts/python.exe docs/audits/2026-09-06-v4-repair-review-probes.py
```

The new probes use temporary copies and injected failure results. In particular, the NaN probe demonstrates an invalid acceptance guard; it does **not** assert that the currently committed source trajectory contains NaNs. No implementation, original experiment artifacts or sibling files were modified.

## Findings

### R01 — P1: Retraining validation can certify a NaN or empty trajectory

Location: `scripts/v4_tcdp/retrain_sibling.py:59-73`.

The error accumulators start at zero and are updated with Python `max(previous, error)`. For a NaN numerical error, `max(0.0, nan)` remains zero. Injecting a retrained row with NaN theta and loss against a finite source row produced `status=PASS`, `max_theta_abs_error=0.0`, and `max_loss_abs_error=0.0`. Two empty trajectory files would also pass the length check and retain zero errors. Shape equality and complete expected step coverage are not checked; array broadcasting can conceal a shape mismatch.

This is a failure of the evidence gate, despite the real finite fixture passing. Require nonempty trajectories, exact expected step IDs and theta shapes, finite values on both sides, and matching model/data contracts before numerical comparison. An attempted finite mismatch should be FAIL rather than INCONCLUSIVE; the current interpretation string also unconditionally says the trajectory matched even when the tolerance is exceeded. Add NaN, infinity, empty, missing-step, shape-mismatch and finite-mismatch negative tests.

### R02 — P2: The requested retraining configuration is hashed but never executed

Location: `scripts/v4_tcdp/retrain_sibling.py:34,46-49,75-76`.

`--config` is resolved and its bytes are hashed for the report, but execution always loads the fixed committed `training_smoke/.../manifest.json`. A probe supplied a config naming `intentionally_different` with 999 updates. The adapter executed `training_smoke` with four updates while reporting the supplied file as `source_config`. Changing or correcting the source config can therefore leave execution unchanged while appearing in provenance as the input used.

For a deliberately smoke-only adapter, reject unsupported config identities and verify the requested YAML hash against the exported manifest before execution. Otherwise resolve and execute the supplied configuration. Record the exact resolved config and adaptations, including the inserted `n_generators='n'`, rather than hashing an unused file.

### R03 — P2: The new retraining path bypasses the repaired source-identity boundary

Location: `scripts/v4_tcdp/retrain_sibling.py:32-44,71-87`.

Unlike the inventory/replay paths, retraining does not verify Git HEAD, dirty source hashes, the exported source identity, or the imported module's origin. Its report contains no observed source commit/tree, environment versions or reference trajectory hash. `sibling_unchanged_by_adapter` is a literal True, not an observation. A controlled fixture with no Git checkout was accepted by the report generator when an injected trainer supplied matching-shaped output; the same missing guards apply to changed real checkouts. Merely prepending a path also does not displace an already imported `iqp_bp` package from another checkout.

Reuse source-identity checks before importing/executing; record actual code/config/data/trajectory hashes and numerical-library versions. Verify imported source paths or isolate the source trainer in a subprocess. Check that generated output cannot resolve inside the sibling. Record before/after source state instead of an unconditional unchanged claim. Current clean-local agreement remains useful evidence, but the adapter does not enforce its provenance claim for subsequent runs.

The global `yaml` stub is an additional isolation hazard in this function: it remains in `sys.modules` and returns `{}` for every `safe_load` call when PyYAML was absent. Keep any narrowly required compatibility shim scoped to the source subprocess; do not silently replace a YAML parser for subsequent work in the parent interpreter.

### R04 — P1: Supported ring ablations overwrite primary evidence

Location: `src/merlin_iqp/experiments/rings.py:64-65,393-423`; CLI flags in `scripts/v4_tcdp/train_rings.py:30-34`.

Artifact paths contain profile, n, seed and smoke/main only. Initialization scheme/scale, optimizer, learning rate and update count do not distinguish destinations, and the writer unconditionally overwrites NPZ/JSON files. Writing parity and uniform runs with the same n/seed/profile into a temporary output root produced the same path and replaced its data. Running the documented initialization ablation with `--main` and the normal output root can overwrite the canonical parity main run. Existing `backend_comparison.json` files in that directory are left behind and can then refer to the previous checkpoint.

Include a stable experiment/config identity in the namespace or reject incompatible existing manifests before writing anything. Make a run-directory write atomic and handle dependent comparison artifacts explicitly. Add sequential primary/ablation and different-step-count tests. This is the same class of problem repaired for sibling replay, now confirmed in the ring pipeline.

### R05 — P2: Comparison consumes modified artifacts under unchanged provenance hashes

Location: `scripts/v4_tcdp/compare_backends.py:24-31,70-81`.

The runner loads numerical arrays and copies the manifest's generator/theta/dataset hashes into its output without verifying them. A temporary copy of the committed n=4 smoke run was modified by adding 0.02 to its first theta. `build_comparison` succeeded and retained theta hash `bd025841...` even though the actual loaded theta hashed to `a46a9a39...`. This can silently combine stale manifests with replaced runs, including the overwrite scenario in R04.

Validate generator, theta, dataset/codec and relevant numerical-array hashes before evaluation, and record hashes of the arrays actually evaluated. Validate binary values before casting generators to uint8; the current eager cast can also coerce invalid source values. Add mutation tests that keep valid shapes but alter data, theta, generator and centers. Hash presence alone does not implement a stale-artifact rejection gate.

### R06 — P2: Spatial Trainer shorthand constructs a meaningless zero loss

Location: `src/merlin_iqp/classical/trainer.py:24`.

`Trainer(..., kernel='spatial_gaussian')` silently supplies an all-zero coordinate matrix. All kernel entries are then one, so normalized distributions have MMD squared zero regardless of fit. A two-qubit target concentrated on `11` returned loss history `(0,0)` with TVD `0.9965530418`, leaving parameters unchanged. This is a public supported constructor path, although the registered ring pipeline correctly supplies an explicit KernelSpec and is not affected by this particular defect.

Require an explicit spatial KernelSpec with real centers, or accept and validate centers as a constructor argument. Reject missing geometry rather than fabricating it. Add a nontrivial target-fit test through the public shorthand boundary and retain the explicit ring path regression.

### R07 — P2: The NAT CLI still does not emit two matched arms from a common warm start

Location: `scripts/v4_tcdp/run_nat.py:34-41`; `.planning/v4-requirement-evidence.md` repair F02 and NAT-02 rows.

The new continuation helper preserves pair updates and Adam state, which repairs the library-level omission. The CLI first runs NAT for 150 steps, writes that result as `primary`, copies it verbatim to `warm-start`, and then runs another 150 steps only for `matched-continuation`. Inspection of the committed files confirms primary==warm-start byte-for-byte, Adam step 150 in both, and Adam step 300 in the continuation. Their initial parameter hashes differ. There is no second treatment continuation branching from the same warm state.

These artifacts support sequential continuation, not the planned equal-budget treatment/control comparison. Create/load one frozen trained warm start, then execute both matched arms from it with identical initial parameters and optimizer state. Record common start hashes, per-arm evaluation budgets and trajectory null results. At the current ideal objective the arms should coincide. Retain the fixed-pair routine as an ablation. Keep the F02 repair disposition partial until the caller and paired artifacts satisfy that contract; the open issue is more than a missing metric panel.

### R08 — P2: Aggregate physical validation still ignores the full-Fock result

Location: `scripts/v4_tcdp/validate_deploy.py:41-49,64-71`.

The aggregate status is calculated before `full_fock_cp_reference` runs. It incorporates the bare-CP probe but never incorporates the subsequently attached full-Fock status. A probe injected a successful bare-CP diagnostic and an INCONCLUSIVE full-Fock result: the report returned overall PASS, physical PASS and nested full-Fock INCONCLUSIVE. The CLI would exit successfully. The previous repair improved the bare-probe handling but left this requested check outside aggregation.

Aggregate after every requested check completes; propagate FAIL and INCONCLUSIVE according to the declared validation scope. Keep individual statuses and distinguish an executed simulator call from an actual distribution/success comparison. Add a failure-injection test for the full-Fock call itself, not only the initial probe.

### R09 — P2: The default suite now depends unconditionally on one developer's sibling checkout

Location: `tests/v4_tcdp/test_sibling_retrain.py:6-11`.

The test hard-codes `C:\Users\cuqui\iqp-mmd-barren-plateau` and requires its ignored historical result files. A fresh clone, CI runner, or another machine cannot run the default suite even if the photonic package and its declared dependencies are installed. The local 636-pass result therefore does not establish portable regression coverage. This newly added test makes optional source integration a mandatory machine-specific fixture.

Keep a self-contained unit fixture for the adapter's acceptance/provenance checks. Put real sibling trajectory comparison behind an explicit integration marker and configured root, or provide the required portable frozen fixture and provenance. When source inputs are unavailable, report that integration evidence as unavailable; do not treat a skip as a faithful-reproduction PASS.

## Repair disposition and practical limits

Independently confirmed repairs include the compiled/deployed parameter alignment, typed ring bundle, asymmetric ordered-map application, direct-resume lr rejection, initialization-std forwarding, honest analytic tomography label, operative/supplied Choi consistency, infinite-KL serialization, zero-shot coverage, and replay namespace collision guard. The source smoke retraining integration test also passed on this machine, as part of both suites. Findings R01–R03 concern its invalid-input and provenance guarantees, not a claim that the finite committed trajectory failed to match.

The primary scientific milestone remains incomplete for the physical/full-Fock/photonic-ring and other already listed requirements. Passing 636 tests does not settle those questions. Repair the false PASS and overwrite paths first, then the matched NAT caller, provenance checks and remaining API contracts. Regenerate only affected artifacts with truthful source identities and rerun the independent probes.

This review added only its report, probe script and a learning-note addendum. It did not fix production code, change the sibling, merge, publish or execute large sweeps.
