# Phase 16: ARB-01 Extended Validation & Postselection Bookkeeping - Research

**Researched:** 2026-08-08
**Domain:** (1) Perceval/photonic gate composability testing (Python, existing codebase), (2) Forge (Racket-hosted relational modeling, v5.2) for a bounded discrete-correctness check, (3) matplotlib/csv output conventions already established in this repo.
**Confidence:** HIGH — every claim below is either read directly from the shipped source (line-cited) or confirmed by actually executing a `racket`/Forge model in this environment during this research pass (not inferred from docs).

## Summary

This phase requires no new library research — it extends code and conventions that already exist and are already validated in this repo. All three deliverables are mechanical extensions of Phase 13/15 patterns:

1. The composability test (ARB-07) is a direct copy of `test_wt2_composability_mixed_generators_n3` (tests/test_iqp_photonic_encoding.py:579-628) with two changes: call `photonic_cp_iqp_distribution` instead of `photonic_weight2_iqp_distribution`, and use a per-config α from `NON_TRIVIAL_ALPHAS` instead of the hardcoded π/4. **Confirmed: `photonic_cp_iqp_distribution(n, i, j, thetas, alpha)`'s signature already matches Phase 13's test parametrization exactly** (`n, i, j, thetas` unchanged, `alpha` appended) — no adaptation needed, contrary to a risk flagged in the task prompt.
2. The α sweep (ARB-08) extends `test_cp_pipeline_success_probability_vs_alpha_table` (tests/test_iqp_photonic_encoding.py:819-847), which already has the exact `sigma_max(alpha)` closed-form helper inline and already asserts against it — the 16-point version is the same loop body over a longer, uniformly-spaced alpha list with the `dist.values()` written to CSV and plotted, matching `batch_sweep.py`'s established save pattern.
3. The Forge model (ARB-09) was **built and actually run during this research pass** (not just designed) against the real Forge v5.2 install — both required checks (sat non-vacuity, unsat non-collision) passed in ~1.2s wall time at n≤8. The working `.frg` source, exact CLI invocation, and gotchas are recorded below verbatim from that run.

**Primary recommendation:** Plan all three deliverables as thin extensions of named, existing functions/tests — cite the line numbers below directly in task descriptions so the executor is not searching for these patterns.

## Standard Stack

No new dependencies. Everything needed is already installed and used elsewhere in this repo.

### Core
| Tool | Version (confirmed) | Purpose | Why Standard (here) |
|---|---|---|---|
| `iqp_photonic_encoding.py` functions | n/a (this repo) | CP(alpha) pipeline, exact reference, TVD | Already shipped, Phase 15 |
| pytest + numpy | already in `requirements.txt`/venv | composability test, alpha-sweep assertions | matches every prior phase's test file |
| matplotlib (`Agg` backend) | already in venv (used by `batch_sweep.py`) | sweep plot | established repo convention |
| Racket 8.15 / Forge v5.2 | confirmed live: `racket --version` → `Welcome to Racket v8.15 [cs]`; `raco pkg show forge` → linked package at `C:\Users\cuqui\cs1710\forge\forge` | relational model + sat/unsat check | owner's own CS1710 checkout, already the newest tagged release |

### Alternatives Considered
None — this phase is explicitly scoped (CONTEXT.md) to extend existing infrastructure, not introduce new libraries.

**Installation:** None required. `pip install` needs nothing new. Forge/Racket is already installed and linked; no `raco pkg install` needed.

## Architecture / Current Code State (exact, line-cited)

### `iqp_photonic_encoding.py` (1025 lines total)

| Symbol | Lines | Signature / shape |
|---|---|---|
| `photonic_cp_iqp_distribution` | 682-800 | `(n, i, j, thetas, alpha)` → `(dist, residual, postselect_failure_prob)` |
| `_build_weight2_cp_processor_no_postselect` | 566-636 | `(n, i, j, thetas, alpha)` → `(proc, ancilla_spec)` |
| `mapping` dict (the Forge target) | 622-627 | `{2*i: 0, 2*i+1: 1, 2*j: 2, 2*j+1: 3, 2*n: 4, 2*n+1: 5, 2*n+2: 6, 2*n+3: 7}` |
| `build_cp_insertion` | 281-353 | `(n, i, j, alpha)` → `(Circuit(8), ancilla_spec)`; asserts `ancilla_spec == {4:0,5:0,6:0,7:0}` (line 349) |
| `exact_qubit_iqp_distribution` | 927-982 | `(n, thetas, pair_thetas=None)` — used as the reference in both composability and alpha-sweep tests |
| `total_variation_distance` | 1006-1010 | unchanged, reused as-is |

`photonic_cp_iqp_distribution`'s docstring (line 745-748) explicitly states: *"Success probability (1 - postselect_failure_prob) VARIES with alpha ... callers needing the success-probability-vs-alpha table (ARB-04) should compute this across multiple alpha values"* — i.e. the function was written anticipating exactly this phase's sweep.

**No `set_postselection` call exists anywhere in the shipped pipeline** — confirmed by reading the full file; `_build_weight2_cp_processor_no_postselect`'s docstring (lines 572-580) states explicitly that `Processor.set_postselection()` raises `AssertionError: Post-selection conditions cannot compose with modes [...]` the moment a later component touches the same modes, and that filtering is done by hand in `photonic_cp_iqp_distribution` (lines 761-793) instead. This matches CONTEXT.md's roadmap-wording correction: the Forge target is the `mapping` dict, not a literal `set_postselection` call.

### `tests/test_iqp_photonic_encoding.py` (847 lines total)

**Phase 13's composability test — the template to clone (lines 579-628):**
```python
@pytest.mark.parametrize(
    "n, i, j, thetas",
    [
        (3, 0, 1, [0.5, 0.0, 1.3]),
        (3, 1, 2, [0.9, 0.4, 0.0]),
        (3, 0, 2, [0.2, 1.7, 0.65]),
    ],
)
def test_wt2_composability_mixed_generators_n3(n, i, j, thetas):
    qubit_dist = exact_qubit_iqp_distribution(n, thetas, pair_thetas={(i, j): np.pi / 4})
    photonic_dist, residual, herald_failure_prob = photonic_weight2_iqp_distribution(n, i, j, thetas)
    assert np.isclose(residual, 0.0, atol=1e-9)
    assert np.isclose(herald_failure_prob, EXPECTED_HERALD_FAILURE_PROB, atol=1e-6)
    assert np.isclose(sum(qubit_dist.values()), 1.0, atol=1e-9)
    assert np.isclose(sum(photonic_dist.values()) + residual, 1.0, atol=1e-9)
    tvd = total_variation_distance(qubit_dist, photonic_dist)
    assert 0.0 <= tvd <= 1.0
    assert tvd < 1e-6, f"..."
    # non-vacuity sanity check against weight-1-only reference
    qubit_dist_w1only = exact_qubit_iqp_distribution(n, thetas, pair_thetas=None)
    tvd_sanity = total_variation_distance(qubit_dist_w1only, photonic_dist)
    assert tvd_sanity > 0.1, f"..."
```
The exact same 3 `(n, i, j, thetas)` tuples are what CONTEXT.md says to reuse for ARB-07, pairing each with a different `NON_TRIVIAL_ALPHAS` value instead of the fixed π/4. The equivalent CP call for this phase's version is:
```python
qubit_dist = exact_qubit_iqp_distribution(n, thetas, pair_thetas={(i, j): alpha / 4})
photonic_dist, residual, postselect_failure_prob = photonic_cp_iqp_distribution(n, i, j, thetas, alpha)
```
(no `herald_failure_prob`/`EXPECTED_HERALD_FAILURE_PROB` — CP's mechanism uses `postselect_failure_prob`, per `test_cp_pipeline_tvd_gate_n2`'s existing pattern at lines 739-761, which asserts `0.0 < postselect_failure_prob < 1.0` rather than an exact fixed value, since it varies with α).

**Phase 15's alpha-table test — the template for the 16-point sweep (lines 819-847):**
```python
NON_TRIVIAL_ALPHAS = [np.pi / 6, np.pi / 3, 2 * np.pi / 5]  # line 733

def test_cp_pipeline_success_probability_vs_alpha_table():
    n, i, j = 2, 0, 1
    thetas = [0.0, 0.0]
    def sigma_max(alpha):
        a = np.sqrt(complex(np.exp(1j * alpha) - 1))
        return max(abs(1 + a), abs(1 - a))
    table = {}
    for alpha in NON_TRIVIAL_ALPHAS + [np.pi]:
        _, _, postselect_failure_prob = photonic_cp_iqp_distribution(n, i, j, thetas, alpha)
        success_prob = 1.0 - postselect_failure_prob
        table[alpha] = success_prob
        expected_success = 1.0 / sigma_max(alpha) ** 4
        assert np.isclose(success_prob, expected_success, atol=1e-6), f"..."
```
This `sigma_max` closed-form helper is exactly the one documented in `docs/iqp-photonic-encoding.md` lines 404-419 (`p_success(α) = 1/σ_max⁴` at n=2) — reuse it verbatim for the 16-point version (locked at n=2, (i,j)=(0,1), matching CONTEXT.md).

`TOLERANCE = 1e-9`, `PHASE_TOLERANCE = 1e-6` (lines 40-41) are the two module-level tolerance constants already in use; the composability test's TVD bar is a separate literal `1e-6` inline (not a named constant) — match that existing style rather than introducing a new named constant.

### Composability signature confirmation (task risk item, resolved)

The task prompt flagged a risk that `photonic_cp_iqp_distribution` might not accept a full `thetas` array plus `(i,j,alpha)` matching Phase 13's mixed-generator signature. **Confirmed false** — direct read of lines 682-800 shows `photonic_cp_iqp_distribution(n, i, j, thetas, alpha)` accepts exactly the same `(n, i, j, thetas)` shape Phase 13's test already parametrizes over, with `alpha` as the one new trailing argument. No wrapper or adaptation function is needed.

## Don't Hand-Roll

| Problem | Don't Build | Use Instead | Why |
|---|---|---|---|
| CP(alpha) closed-form success probability | A new derivation | `sigma_max(alpha)` helper already inline in `test_cp_pipeline_success_probability_vs_alpha_table` (line 829) and documented in `docs/iqp-photonic-encoding.md` lines 404-419 | Already verified to ~1e-15 (Phase 15); re-deriving risks introducing a transcription error |
| Exact qubit-side reference for the composability test | A hand-rolled state-vector calc | `exact_qubit_iqp_distribution(n, thetas, pair_thetas={(i,j): alpha/4})` | Already the project's single source of truth for the exact reference, reused unmodified since Phase 9 |
| CSV/plot save pattern | A new plotting scheme | `batch_sweep.py`'s `update_metrics_csv`/`build_comparison_figure` pattern (matplotlib `Agg` backend, `csv.DictWriter`, resumable-merge-not-overwrite) | Matches this repo's established `results/` convention exactly |
| Sat/unsat harness scripting for Forge | Any Python wrapper around `racket` | `test expect { name: {...} for N Int is sat/unsat }` blocks + `option run_sterling off`, run directly via `racket file.frg` | Forge's own idiom; a Python wrapper adds a moving part with no benefit — confirmed the direct invocation already gives clean stdout + exit code |

## Common Pitfalls

### Pitfall 1: `racket file.frg` hangs on Windows if the file contains a bare `run { ... }` or omits `option run_sterling off`
**What goes wrong:** Running any `.frg` file that reaches Forge's default end-of-run behavior (opening the Sterling visualizer as a local web server) fails on this Windows/Git-Bash environment with `error reading from stream port ... win_err=1` inside `serve-sterling-static.rkt`, and the process does not exit cleanly.
**Confirmed live:** reproduced with `racket grandpa.frg` and `racket stacks.tests.frg` (both real files from the owner's own CS1710 checkout, no `option run_sterling off`) — both printed correct results first, then hit this error at the very end.
**How to avoid:** Put `option run_sterling off` as the second line of any `.frg` file meant to run headlessly/in CI. Confirmed this fully resolves it — a file with `option run_sterling off` plus only `test expect { ... }` blocks (no bare `run`) exits cleanly with exit code 0 on all-pass, exit code 1 on any failure, and prints `Test passed: <name>` / `*** TEST FAILED ***` per block to stdout.
**Warning signs:** the process appears to hang or exits with an unrelated-looking Racket internal error after your test output already printed — the test results already ran and printed; the error is purely post-hoc UI-launch noise, but it will pollute exit-code checks if not suppressed.

### Pitfall 2: `raco forge` is not a valid command
**What goes wrong:** The phase's own CONTEXT.md says the Forge model "runs via Racket/raco forge directly" — but `raco forge --help` returns `raco.exe: Unrecognized command: forge` (confirmed live). There is no `raco forge` subcommand in Forge v5.2.
**How to avoid:** The correct invocation is simply `racket path/to/model.frg` (Forge is a `#lang forge` Racket language, loaded like any other Racket module — not a `raco` package command). Document this exact form in the plan/task, not `raco forge`.
**Warning signs:** any task description that says "run via raco forge" will fail at the first command.

### Pitfall 3: comparison operator is `<=`, not `=<`
**What goes wrong:** Writing `n =< 8` (a plausible typo direction from math notation) is a parse error: `NT-Expr: expected one of these literals: "in", "=", "<", ">", "<=", ">=", "is", or "ni"`.
**How to avoid:** Forge's operators are `<`, `>`, `<=`, `>=`, `=`, `!=`, `in`, `ni` — same left-to-right order as most languages, not Alloy's occasional `=<`.

### Pitfall 4: default Forge bitwidth (4 bits, range [-8,7]) is too small for this model
**What goes wrong:** With `n` up to 8, the largest global index the mapping touches is `2*n+3 = 19`. Forge's default bitwidth (per `binarysearch.frg`'s own comment, confirmed) is 4 bits, giving representable range `[-8, 7]` — 19 silently wraps/overflows.
**How to avoid:** Explicitly set bitwidth via `for N Int` on every `test expect` entry (or block). **Confirmed sufficient and tested live: `for 6 Int`** (range `[-32, 31]`) comfortably covers all values up to 19 with headroom, and the model still solves in ~1.2s combined at n≤8.
**Warning signs:** a model that should be trivially sat/unsat instead reports a surprising counterexample or unexpected result — check bitwidth first before assuming a logic bug.

### Pitfall 5: `+` between Int expressions is set union, not arithmetic addition
**What goes wrong** (not hit directly in this research pass, but confirmed from every real `.frg` example inspected — `binarysearch.frg`, `gameOfLife.frg`, `intOperators.frg` — none of which ever write `i + 1` for arithmetic): Forge's `Int` sig values are still relational atoms; `+` is the general set/relation union operator, not addition. Arithmetic must go through the explicit integer functions.
**How to avoid:** Use `add[x, y]`, `subtract[x, y]`, `multiply[x, y]`, `divide[x, y]` for arithmetic (confirmed this exact style works in the model built and run below — `multiply[2, i]`, `add[multiply[2, i], 1]`, etc.). Comparison operators (`<`, `<=`, `>`, `>=`, `=`, `!=`) work directly on `Int` expressions without a wrapper function (confirmed live).

### Pitfall 6: `expect NAME { ... }` alone is a no-op — must be `test expect NAME { ... }`
**What goes wrong:** `gameOfLife.frg`'s own comment (line 49-50, read directly) warns: *"Add 'test' keyword before 'expect' to run these validation tests"* — a bare `expect nhood_tests { ... }` block (no leading `test`) is parsed but never executed.
**How to avoid:** Always write `test expect { name: { ... } for N Int is sat }` (as used throughout this research's own verified model) — the `test` keyword is required, not optional decoration.

### Pitfall 7 (not a pitfall, a confirmed non-issue): CP's postselect_failure_prob is not a fixed constant like heralded_cz's
Unlike `photonic_weight2_iqp_distribution`'s `EXPECTED_HERALD_FAILURE_PROB` (a single constant, `1 - 2/27`), `photonic_cp_iqp_distribution`'s `postselect_failure_prob` genuinely varies with `alpha` (docs/iqp-photonic-encoding.md lines 406-434, non-monotonic). The composability test's α-varying analogue must **not** assert a fixed expected failure probability the way `test_wt2_composability_mixed_generators_n3` does for `herald_failure_prob` — only bound it `0.0 < postselect_failure_prob < 1.0`, matching `test_cp_pipeline_tvd_gate_n2`'s existing pattern (line 757).

## Code Examples

### Verified Forge model (built and executed live in this research pass — real result, not a design sketch)

Ran via: `racket ancilla_mapping.frg` (no `raco forge` — see Pitfall 2). Both required checks passed on the first attempt with **no counterexample found** — i.e. the mapping dict genuinely is injective and non-colliding at every valid `(n,i,j)` with `2 <= n <= 8`, confirming CONTEXT.md's expectation that this is "provably structurally impossible by construction" rather than a real bug.

```racket
#lang forge
option run_sterling off

-- Structural correctness check of the CP(alpha) insertion's local->global
-- ancilla mode-index mapping dict (iqp_photonic_encoding.py,
-- _build_weight2_cp_processor_no_postselect, lines 622-627):
--   mapping = {2i:0, 2i+1:1, 2j:2, 2j+1:3, 2n:4, 2n+1:5, 2n+2:6, 2n+3:7}

pred validTriple[n, i, j: Int] {
    n >= 2
    n <= 8
    i >= 0
    i < n
    j >= 0
    j < n
    i != j
}

pred distinctPorts[n, i, j: Int] {
    let pi0 = multiply[2, i], pi1 = add[multiply[2, i], 1],
        pj0 = multiply[2, j], pj1 = add[multiply[2, j], 1],
        a0 = multiply[2, n], a1 = add[multiply[2, n], 1],
        a2 = add[multiply[2, n], 2], a3 = add[multiply[2, n], 3] | {
        pi0 != pi1  pi0 != pj0  pi0 != pj1  pi0 != a0  pi0 != a1  pi0 != a2  pi0 != a3
        pi1 != pj0  pi1 != pj1  pi1 != a0  pi1 != a1  pi1 != a2  pi1 != a3
        pj0 != pj1  pj0 != a0  pj0 != a1  pj0 != a2  pj0 != a3
        pj1 != a0  pj1 != a1  pj1 != a2  pj1 != a3
        a0 != a1  a0 != a2  a0 != a3  a1 != a2  a1 != a3  a2 != a3
        -- ancilla ports must not collide with ANY qubit's own data port
        -- (0..2n-1), not just qubit i/j's -- the fully general property
        -- (CONTEXT.md's explicit instruction, not just the narrower check).
        all k: Int | (k >= 0 and k < multiply[2, n]) implies {
            k != a0
            k != a1
            k != a2
            k != a3
        }
    }
}

test expect {
    -- Part 1: non-vacuity -- guards against a vacuously-true,
    -- over-constrained model (the classic Forge pitfall).
    nonVacuous: {
        some n, i, j: Int | validTriple[n, i, j]
    } for 6 Int is sat

    -- Part 2: no counterexample to injectivity/non-collision within bound.
    noCounterexample: {
        some n, i, j: Int | validTriple[n, i, j] and not distinctPorts[n, i, j]
    } for 6 Int is unsat
}
```

**Actual output from `racket ancilla_mapping.frg` (this research pass, exit code 0):**
```
Forge version: 5.2
...
#vars: (size-variables 3306); #primary: (size-primary 192); #clauses: (size-clauses 10443)
Transl (ms): (time-translation 348); Solving (ms): (time-solving 231)
    Test passed: nonVacuous
#vars: (size-variables 3778); #primary: (size-primary 192); #clauses: (size-clauses 12125)
Transl (ms): (time-translation 316); Solving (ms): (time-solving 889) Core min (ms): (time-core 0)
    Test passed: noCounterexample
```
Total solve time ~1.2s at `n<=8`, `for 6 Int` — well inside "effectively instant," matching CONTEXT.md's expectation. This confirms the property genuinely holds (a real finding, per CONTEXT.md's "or surfacing and documenting a real bug if one is found" — no bug found).

**What the plan should do differently from this scratch version:** this exact model is ready to use as the `forge/` directory's `.frg` file content (adjust file header/comments to reference the final n-bound chosen within 6-8, add a header comment block matching this repo's documentation style, e.g. `julia/README.md`'s pattern). The owner should still review/re-derive the predicate logic themselves per this project's attempt-first convention (`CLAUDE.md`) — this is a confirmed-working scaffold, not a substitute for that.

### batch_sweep.py's plot+CSV save pattern (the template for `results/phase16_alpha_sweep.png`/`.csv`)

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import csv

# CSV: resumable merge-not-overwrite pattern (update_metrics_csv, batch_sweep.py:63-83)
csv_path = f"{RESULTS_DIR}/phase16_alpha_sweep.csv"
with open(csv_path, "w", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=["alpha", "measured_success_prob", "closed_form_success_prob"])
    writer.writeheader()
    for row in rows:
        writer.writerow(row)

# Plot: matplotlib.use("Agg") set BEFORE importing pyplot (batch_sweep.py:5-7),
# plt.savefig(...) then plt.close() (batch_sweep.py:109-110)
plt.savefig(f"{RESULTS_DIR}/phase16_alpha_sweep.png")
plt.close()
```
Note: `batch_sweep.py`'s CSV pattern merges into existing rows keyed by a parameter (there, `batch_size`); for a fixed 16-point sweep run in one pass, a simpler full-overwrite write (as sketched above) is sufficient and matches `phase4_sweep_metrics.csv`'s simpler sibling scripts — no need to replicate the resumability logic since this sweep is not expected to run in unresumable chunks like the multi-minute training runs `batch_sweep.py` guards against.

## State of the Art

Not applicable in the usual sense (no external ecosystem drift to track) — this phase extends internal, already-validated code. The one relevant "current vs. deprecated" fact:

| Old approach (what CONTEXT.md's roadmap wording implied) | Current approach (what actually ships) | Why |
|---|---|---|
| Verify a literal `Processor.set_postselection()` call | Verify the `mapping` dict in `_build_weight2_cp_processor_no_postselect` (lines 622-627) | `set_postselection` was tried and found to raise `AssertionError` when composed with later components (15-RESEARCH.md Pitfall 3) — the shipped pipeline never calls it; filtering is manual (lines 761-793) |

## Open Questions

1. **Exact n-bound for the Forge model (6, 7, or 8)** — CONTEXT.md leaves this to Claude's discretion within [6,8]. Verified live: n=8 already solves in ~1.2s total, so there is no performance reason to pick a smaller bound within this range; recommend n=8 (the top of the allowed range) since it costs nothing extra and gives the largest verified envelope. No further research needed — this is a planning choice, not an unresolved technical question.
2. **Exact sanity-check TVD threshold for the composability test's non-vacuity check** — CONTEXT.md defers this to measurement ("measure first, then set a safe lower bound with headroom"). This requires actually running the new CP-based composability test once at each of the 3 chosen α values to observe the real TVD-vs-weight-1-only numbers (analogous to Phase 13's 0.46-0.50 observation that produced its 0.1 threshold) — cannot be determined from static code reading alone; this is properly a task for the execution phase (or a short measurement task within planning), not something this research pass can responsibly assert without running the actual non-trivial-α CP pipeline.

## Sources

### Primary (HIGH confidence — direct source read + live execution in this repo/environment)
- `C:\Users\cuqui\merlin-quantum-case-study\iqp_photonic_encoding.py` (full file read, 1025 lines) — exact function bodies, docstrings, line numbers cited above.
- `C:\Users\cuqui\merlin-quantum-case-study\tests\test_iqp_photonic_encoding.py` (full file read, 847 lines) — exact existing test patterns, constants (`NON_TRIVIAL_ALPHAS`, `TOLERANCE`, `PHASE_TOLERANCE`), Phase 13/15 test bodies.
- `C:\Users\cuqui\merlin-quantum-case-study\docs\iqp-photonic-encoding.md` (targeted reads, lines 404-474) — closed-form success probability, existing comparison/results tables to extend.
- `C:\Users\cuqui\merlin-quantum-case-study\batch_sweep.py` (full file read) — CSV/plot save convention.
- `C:\Users\cuqui\merlin-quantum-case-study\.planning\STATE.md` (tail read) — decision-log format and confirmed Forge-install fact already recorded.
- Live shell execution: `racket --version`, `raco pkg show forge`, `raco forge --help` (confirms no such subcommand), `racket grandpa.frg`/`racket stacks.tests.frg` (reproduces the Sterling-hang pitfall), `racket sterling_test2.frg` (confirms `option run_sterling off` fix + exit codes), `racket ancilla_mapping.frg` (the full mapping-dict model, both sat/unsat checks passed).
- `C:\Users\cuqui\cs1710\forge\forge\examples\bsearch_array\binarysearch.frg`, `examples\basic\gameOfLife.frg`, `tests\forge\ints\intOperators.frg`, `tests\forge\other\sterling-off.frg`, `tests\error\failed_sat.frg`, `hw\cs1710-modeling-intro-alejack312\grandpa.frg`/`stacks.tests.frg` — the owner's own installed Forge checkout and CS1710 homework, used to derive and cross-check the exact syntax (arithmetic functions, `for N Int` bitwidth spec, `test expect ... is sat/unsat`, `option run_sterling off`).

### Secondary / Tertiary
None used — every claim in this document is grounded in a primary source (direct file read or live command execution), not web search or training-data recall, since the entire research surface is this repo's own code plus a locally-installed, version-pinned tool the owner already confirmed working.

## Metadata

**Confidence breakdown:**
- Composability test design: HIGH — signature compatibility confirmed by direct source read, not assumption.
- Alpha sweep: HIGH — closed-form and existing 4-point test already validated in Phase 15; 16-point extension is mechanical.
- Forge model: HIGH — the exact model was written and executed successfully against the real installed toolchain during this research pass; syntax, invocation, and bitwidth were all empirically confirmed, including two real gotchas (Sterling hang, `raco forge` not existing) that would otherwise have cost an execution-time iteration.

**Research date:** 2026-08-08
**Valid until:** Stable — this research is grounded in code and a locally-pinned tool version that don't change without explicit repo/toolchain action. No expiry pressure; re-verify only if `iqp_photonic_encoding.py`, the test file, or the Forge install change before planning executes.
