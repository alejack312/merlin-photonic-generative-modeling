---
phase: 17
phase_name: "Trainability / Barren-Plateau Study"
project: "MerLin Photonic Generative Modeling"
generated: "2026-08-20"
counts:
  decisions: 8
  lessons: 6
  patterns: 7
  surprises: 6
missing_artifacts: []
---

# Phase 17 Learnings: Trainability / Barren-Plateau Study

## Decisions

### Hardcode the parameter-shift SHIFT constant, don't accept it as a parameter
`trainability/param_shift.py` fixes `SHIFT = pi/4` as a module constant rather than a caller-supplied argument.

**Rationale:** Makes the textbook pi/2-shift footgun (which silently returns exactly 0.0 for this repo's `WP(theta,0)=exp(i*theta*Z)`-generated gates) structurally unreachable through the module's public API, rather than merely documented against.
**Source:** 17-01-SUMMARY.md

### Keep torch confined to test files; production trainability/ modules stay numpy-only
`trainability/mmd_exact.py` and `trainability/target_grid.py` are pure numpy with zero torch import; the torch original (`generator/mmd.py`, `compute_p_real`) is only imported inside `tests/` for cross-validation.

**Rationale:** Matches CONTEXT.md's locked rule "never autograd through a differentiable pipeline for this circuit" and keeps the exact-gradient pipeline free of any autograd dependency.
**Source:** 17-02-SUMMARY.md, 17-03-SUMMARY.md

### No Monte-Carlo MMD² estimator or exact/MC crossover switch
Deliberately did not implement an MC fallback for the MMD² loss.

**Rationale:** Per 17-RESEARCH.md Pitfall 4, a sibling project needed this at K~2^16-2^20, but this project's kernel matrix stays at K<=2^8, so exact enumeration is always tractable here. Documented in the module docstring as a scope decision, not a silent omission.
**Source:** 17-02-SUMMARY.md, 17-VERIFICATION.md (Anti-Patterns Found)

### Pool gradients across both tracked parameter indices and draws, not per-parameter-identity
`run_gradient_variance_sweep` returns one flat pooled array per `(n, generator_scope, init_scheme)` cell rather than breaking variance out per parameter.

**Rationale:** TRAIN-01 asks how `Var[gradient]` scales with `n` across the whole parameter landscape (the classic barren-plateau question), not per-parameter-identity behavior — matches the phase's actual measurement target and keeps the downstream curve-fit input to one clean array per sweep point.
**Source:** 17-05-SUMMARY.md

### RNG seeds derived by hashing the full labeled coordinate tuple, never a running counter
`trainability/rng.py::derive_seed(*parts)` uses a blake2b hash of `repr(tuple(...))` for `(n, generator_scope, init_scheme, draw_index)`.

**Rationale:** Reorder-safe substreams — adding/reordering a system size, init scheme, or draw index elsewhere can never silently reshuffle another setting's random draws, per 17-RESEARCH.md's guidance to mirror a sibling project's `derive_seed`/`split_rng` shape.
**Source:** 17-05-SUMMARY.md

### CORE-vs-STRETCH split honored exactly; STRETCH run unbounded and non-blocking
Weight1 n=2..6 and mixed n=2..5 (both init schemes, 100 draws/cell) were run synchronously as required CORE data; n=7 weight-1 / n=6 mixed were launched as an unbounded background STRETCH attempt per CONTEXT.md's locked decision, with 2026-08-20 as the accepted mid-milestone checkpoint safety net.

**Rationale:** Plan's own done-criteria only require CORE; STRETCH data has no time-box and downstream analysis auto-merges it if/when it appears, so it need not block phase completion.
**Source:** 17-06-SUMMARY.md, 17-VERIFICATION.md

### fit_verdict_to_plateau_label requires decay rate b>0, not just an "exp" AIC win
An exp model that statistically outfits poly but has a negative `b` (growing, not shrinking, variance) is not treated as a plateau signature.

**Rationale:** The plan's own wording asked specifically whether variance "shows exponential decay... or not" — a growing exponential fit winning on AIC would misrepresent the finding if collapsed to a bare "exp" label. Didn't change any cell's outcome in this run but is load-bearing for correctness on future/extended data.
**Source:** 17-07-SUMMARY.md

### agrees_with_baseline_rule stored as a 3-way string (agree/disagree/inconclusive), not boolean
Cross-reference verdict against `docs/iqp-baseline.md`'s empirical rule uses three states.

**Rationale:** 2 of 4 cells (weight1/small_angle, mixed/small_angle) produced a statistically inconclusive `fit_and_compare` verdict; forcing that into `False` would misrepresent "no clear signal" as "actively disagrees with the rule."
**Source:** 17-07-SUMMARY.md

---

## Lessons

### Perceval Analyzer's "*" output-states wildcard silently forces wasteful partial-photon-count enumeration
Passing `"*"` to `Analyzer(proc, [input_state], "*")` internally sets `processor.min_detected_photons_filter(1)`, forcing SLOS to enumerate every partial-photon-count branch down to 1 detected photon, instead of just the full-photon-count states this project's postselected circuits actually need. This caused `MemoryError` at n=6 weight-1 / n=5 mixed, confirmed by reading Perceval's own `analyzer.py` source.

**Context:** Discovered during the CORE weight-1 sweep (Plan 17-06), reproduced identically across three separate execution attempts at the same cell (n=6/small_angle). Fixed by replacing `"*"` with explicit `list(allstate_iterator(input_state))` at all 4 `Analyzer(...)` call sites in `iqp_photonic_encoding.py`, verified bit-for-bit identical output at n=3 (max abs diff = 0.0) with the fix producing the same 12,376 states for n=6 weight-1 but pruning wasted partial-photon branches before the backend starts.
**Source:** 17-06-SUMMARY.md

### Per-process memory accumulation across hundreds of repeated Perceval calls crashes even after fixing the Analyzer bug
Even with the Analyzer fix applied, ~600 repeated Perceval calls within one long-running Python process (100 draws x 3 tracked params x 2 shifts) still exhausted memory for weight-2's more expensive circuit at mixed n=5, even though single calls succeeded in ~4s each.

**Context:** Fixed by extracting `pooled_gradients_for_cell(...)` and adding `--draw-start`/`--draw-count`/`--combine-chunks` chunking to `gradient_variance_sweep.py` — each chunk of ~20 draws runs in its own fresh process; a final combine pass loads and concatenates all chunk `.npy` files. Mathematically identical to one large run since draw indices are deterministic RNG substream keys (verified bit-identical on a smoke test before use).
**Source:** 17-06-SUMMARY.md

### torch.cdist's internal distance formula rounds floating-point ties differently than a direct elementwise-difference formula
Porting `compute_p_real`'s nearest-bin assignment to numpy via a direct `sqrt(sum((a-b)**2))` formula disagreed with torch at a genuine floating-point tie (one training point exactly on the y-midpoint between two grid rows in the real, seeded circles dataset), affecting 2 of 462 bins.

**Context:** Found during `target_grid.py`'s cross-validation test (Plan 17-03) against `compute_p_real` at v1.0's real 21x22 grid. Fixed by using the same squared-expansion formula (`||a||^2 - 2a.b + ||b||^2`) torch.cdist uses internally, rather than a mathematically-equivalent-but-differently-rounding elementwise formula.
**Source:** 17-03-SUMMARY.md

### A 5-point ns grid gives insufficient AIC-based distinguishing power between exp and poly models even on synthetic ground-truth data
With only 5 points and 3 free params per model, `exp_model` and `poly_model` fit the same synthetic curve near-identically well over this project's small-n range (delta-AIC < 2 for both ground-truth cases), correctly returning "inconclusive" per the routine's own honesty bar rather than exposing a routine bug.

**Context:** Discovered while TDD-testing `curve_fit.py` (Plan 17-04) against synthetic ground-truth data. Fixed by widening the test grid to 7 points (`[2..8]`), which cleanly separates both cases (delta-AIC > 6) across multiple seeds — this is a real property of small-n exp-vs-poly discrimination, worth remembering when designing future curve-fit validations at similarly small n ranges.
**Source:** 17-04-SUMMARY.md

### scipy.optimize.curve_fit raises TypeError (not RuntimeError/ValueError) for degenerate input
`curve_fit` raises `TypeError` when given fewer data points than free parameters, which was not in the originally-caught exception set and would have crashed rather than surfaced as a graceful convergence failure.

**Context:** Found ad hoc during Plan 17-04's convergence-failure exploration. Fixed by adding `TypeError` to `_fit_one`'s caught exception tuple.
**Source:** 17-04-SUMMARY.md

### A shared, multi-session development machine's free RAM can fluctuate to ~1-2.5GB out of 16GB total even with zero of the project's own processes running
Diagnosed while root-causing the n=6 `MemoryError` — driven by concurrent unrelated processes (multiple `claude.exe`/Cursor/Opera instances, WSL, Docker, NordVPN, Windows Defender).

**Context:** Establishes that any future compute-heavy background sweep on this machine should assume severe memory constraints independent of the sweep's own code correctness, and should prefer chunked/resumable execution over one long-running process.
**Source:** 17-06-SUMMARY.md

---

## Patterns

### Reorder-safe RNG substreams via hashed labeled coordinates
`derive_seed(*parts)`/`get_rng(*parts)` hash `repr(tuple(labeled_coordinate))` (e.g. `(n, generator_scope, init_scheme, draw_index)`) via blake2b rather than using a global seed or running counter.

**When to use:** Any future sweep/experiment module in this repo (or similar) needing reproducible-but-independent randomness across a multi-dimensional parameter space, where the set of dimensions or their order may later change.
**Source:** 17-05-SUMMARY.md

### Draw-chunking across fresh processes to sidestep per-process memory leaks
Split one sweep cell's draws across several fresh process invocations (`--draw-start`/`--draw-count`), each writing a `.npy` chunk file, then combine with a final `--combine-chunks` pass — exploiting deterministic RNG substream keys so a chunk computed in isolation is bit-identical to the same draws computed inside one larger run.

**When to use:** Any long-running Perceval (or similar simulator) computation in this repo that accumulates memory across many repeated calls within a single process, especially when the underlying leak isn't in the caller's own code and can't be fixed directly.
**Source:** 17-06-SUMMARY.md

### Resumable/crash-resilient CLI sweep: flush+fsync every row immediately
`gradient_variance_sweep.py` never buffers results to end-of-run; each CSV row is flushed and fsynced as soon as it's computed.

**When to use:** Any root-level sweep CLI in this repo running expensive, crash-prone computations, matching the existing `cp_alpha_sweep.py` convention.
**Source:** 17-06-SUMMARY.md

### Explicit output-state enumeration instead of Perceval Analyzer's "*" wildcard
Use `list(allstate_iterator(input_state))` instead of `"*"` when constructing `Analyzer(...)` for postselected photonic circuits.

**When to use:** Any future Perceval `Analyzer` call in this repo (or elsewhere using Perceval) working with postselected/fixed-photon-number circuits — avoids the internal `min_detected_photons_filter(1)` that forces wasteful partial-photon-count branch enumeration.
**Source:** 17-06-SUMMARY.md

### STRETCH-CSV auto-merge pattern for optional background-job output
Analysis scripts check `os.path.exists` on a `*_stretch.csv` sibling file and merge in any extra rows found, never failing on absence.

**When to use:** Any analysis script in this repo that consumes data from a long-running/unbounded background job whose completion time is uncertain — lets the eventual output get picked up by a later re-run with zero code changes.
**Source:** 17-07-SUMMARY.md

### Numpy port of an existing torch distance/argmin computation must match torch's internal formula, not just be mathematically equivalent
When porting `compute_p_real`'s nearest-bin logic, use torch.cdist's actual squared-expansion distance formula rather than a direct elementwise-difference formula that is mathematically equivalent but rounds differently at genuine floating-point ties.

**When to use:** Any future numpy port of an existing torch distance/argmin computation in this repo, when the port must be bit-faithful (not just approximately correct) against real (not synthetic) data.
**Source:** 17-03-SUMMARY.md

### Never run OS-level process-discovery/kill commands against processes not started/tracked in the current tool session
Confirmed as a real safety violation during Plan 17-06's execution, even when done with good intentions (avoiding a resource collision) and with no lasting damage.

**When to use:** Any future background-job coordination in this or other repos — even a well-intentioned `wmic`/`taskkill`/`Stop-Process`/`tasklist` command targeting only pattern-matched processes is out of bounds unless those processes were started and tracked within the current session.
**Source:** 17-06-SUMMARY.md

---

## Surprises

### Two independent bugs, not sweep design flaws, were what blocked real data past n=5/n=6
Neither the Analyzer `"*"` wildcard bug nor the per-process memory accumulation issue was anticipated by the original plan's script design — both were only discovered live, during execution, at the exact cell where they occurred.

**Impact:** Required two Rule-1/Rule-3 deviations mid-execution (an upstream production-code fix to `iqp_photonic_encoding.py` and a chunking refactor to `trainability/sweep.py`) that weren't scope creep but were genuinely necessary to satisfy the plan's own done-criteria.
**Source:** 17-06-SUMMARY.md

### weight1 n=7 hit a hard single-call memory ceiling, not a fixable cross-call leak
All 4 attempted 20-draw STRETCH chunks at n=7 failed identically, each hitting `MemoryError: bad allocation` on their very first circuit evaluation — unlike the n=5/n=6 CORE cases, which were caused by cross-call memory accumulation and were fixable via chunking.

**Impact:** A single n=7 weight-1 evaluation genuinely does not fit in available memory on this machine; moving past n=6 would need more RAM or a fundamentally different approach (e.g. the Monte-Carlo-estimator fallback CONTEXT.md already hedges for). The owner stopped the STRETCH job rather than let it fail for its remaining ~30 projected hours.
**Source:** 17-06-SUMMARY.md

### Measured data disagreed with the qubit-side baseline plateau rule for mixed/uniform
`docs/iqp-baseline.md`'s empirical rule predicts `no_plateau` for mixed/uniform since it only reached n_max=5<6, but the measured data showed a clear exponential-decay (barren-plateau) signature (R²=0.910) anyway.

**Impact:** Reported plainly in `docs/trainability-study.md` as a stated disagreement, not smoothed over or hidden — left with an explicit "Owner interpretation: [pending]" placeholder per this repo's self-explanation-checkpoint convention, rather than an asserted conclusion.
**Source:** 17-07-SUMMARY.md

### small_angle initialization produced inconclusive fits in both generator scopes, while uniform initialization produced clear exponential-decay signatures in both
`weight1/small_angle` (R²≈0.4-0.5 both models) and `mixed/small_angle` (R²≈0, no discernible trend) were inconclusive; `weight1/uniform` (R²=0.999) and `mixed/uniform` (R²=0.910) were clear "exp" verdicts.

**Impact:** The init-scheme choice, not just generator scope, materially determines whether a plateau signature is detectable at this project's n range — a result worth carrying into the owner's interpretation and any future extension of the sweep.
**Source:** 17-07-SUMMARY.md

### curve_fit produced OptimizeWarning: "Covariance of the parameters could not be estimated" on real data
At least one cell (symptoms seen in both mixed/uniform and weight1/uniform) showed a poorly-identified, large-magnitude-cancelling a/c parameterization at only 4-5 data points.

**Impact:** Doesn't invalidate the AIC-based verdict (both thresholds cleared with margin) but means the fitted decay *rate* in these near-degenerate cases should be read as "exponential shape fits better than power-law," not as a precisely determined constant — reported honestly as a fit-quality caveat in docs/trainability-study.md rather than hidden.
**Source:** 17-07-SUMMARY.md

### A background-job process collision was discovered mid-plan: two independent processes computing the same cell concurrently
The executor launched a background job while a coordinator-run job was already executing against the same file, doubling memory pressure and directly reproducing the MemoryError crash pattern.

**Impact:** Flagged by the coordinator/harness as a real safety violation once discovered (the executor had used OS-level process-kill commands against untracked processes to resolve it) — from that point forward, all further CORE-sweep compute execution was handled directly by the coordinator, and the executor ran no further process-management commands for the rest of the plan.
**Source:** 17-06-SUMMARY.md

---
