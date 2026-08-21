---
phase: 22-multi-pair-ancilla-allocation-formal-verification
reviewed: 2026-08-21T00:00:00Z
depth: standard
files_reviewed: 7
files_reviewed_list:
  - mpair07_reuse_check.py
  - results/phase22_reuse_gate.md
  - forge/pooled_ancilla_allocation.frg
  - results/phase22_forge_run_log.md
  - pooled_allocation_baseline.py
  - results/phase22_forge_summary.md
  - docs/iqp-photonic-encoding.md
findings:
  critical: 0
  warning: 2
  info: 4
  total: 6
status: issues_found
---

# Phase 22: Code Review Report

**Reviewed:** 2026-08-21
**Depth:** standard
**Files Reviewed:** 7
**Status:** issues_found

## Summary

Reviewed the Phase 22 (multi-pair pooled ancilla allocation) deliverables: two standalone research scripts (`mpair07_reuse_check.py`, `pooled_allocation_baseline.py`), a Forge model (`forge/pooled_ancilla_allocation.frg`), three results/documentation artifacts, and the new `docs/iqp-photonic-encoding.md` section. No critical bugs, security issues, or logic errors were found — the arithmetic in the docs is internally consistent (bitwidth justification, ratio/timing claims, formula cross-checks all check out), the Forge model's predicates are semantically sound (`pairsAreKn` + exact-count bound correctly forces full K_n coverage by pigeonhole; `ancillaDisjointFromDataPorts` is a tautology-by-construction check, matching the stated Phase 16 precedent), and the two Python scripts' numeric logic (colour search, TVD/postselection filter, harness anchor) traces correctly against their own decision rules.

The two Warning-level findings concern real gaps: (1) a structural blind spot in `mpair07_reuse_check.py`'s test design — the residual/bystander-qubit code path is never exercised by either probe actually run, weakening what the "harness anchor" checks; and (2) a CLI argument (`--alpha`) that is accepted but silently discarded, which risks misleading a future user of the script. The Info-level findings are minor dead-code/unused-variable items typical of research scripts, not correctness risks.

## Warnings

### WR-01: `postselected_distribution`'s bystander/residual branch is never exercised by either probe

**File:** `mpair07_reuse_check.py:167-232` (residual logic at 209-225), exercised via `run_probe_n2` (`mpair07_reuse_check.py:298-333`) and `run_probe_n4` (`mpair07_reuse_check.py:336-375`)

**Issue:** `postselected_distribution` generalizes `photonic_cp_iqp_distribution`'s three-way filter (ancilla check → gate-qubit check → bystander check) to an arbitrary set of ancilla modes and gate-touched qubits. The bystander/`residual` branch (lines 209-225) only fires when a qubit exists that is *not* touched by any gate insertion (`gate_qubits`). But in `run_probe_n2`, `pair_a = pair_b = (0, 1)` at `n=2` — every qubit is gate-touched. In `run_probe_n4`, `pair_a=(0,1)`, `pair_b=(2,3)` at `n=4` — again every qubit is gate-touched (`gate_qubits = {0,1,2,3} = range(n)`). So across every draw in both probes, `residual` is structurally always `0.0` — the bystander-decode path is dead code for the purposes of this evidence run.

This matters because the pre-committed HARNESS ANCHOR explicitly includes `residual_dedicated <= 1e-9` as a validity gate (module docstring lines 24-26, `results/phase22_reuse_gate.md` lines 36-38). Since `residual` can never be anything but exactly `0.0` in the configurations actually tested, that half of the harness anchor is trivially satisfied regardless of whether the generalized bystander-handling code is correct — it provides no actual signal here. This is a real coverage gap for any future k-pair (k≥3) or larger-`n` extension of this evidence, where bystander qubits would exist and this exact code path would need to be trusted for the first time untested.

`results/phase22_reuse_gate.md`'s "What this does not establish" section (lines 151-170) lists several honest scope limits (bounded n, no ≥3-pair pooling, no Kraus-level root cause) but does not call out this specific blind spot — that the residual-handling branch itself was never exercised.

**Fix:** Either (a) add a third draw/probe configuration with `n > len(gate_qubits)` so at least one bystander qubit exists and the residual path is genuinely exercised, or (b) explicitly note in `results/phase22_reuse_gate.md`'s "What this does not establish" section that the residual/bystander code path was not exercised by either probe and remains unvalidated for the generalized two-insertion case.

## Info

### IN-01: `--alpha` CLI argument is accepted but silently ignored

**File:** `mpair07_reuse_check.py:383, 387-389`

**Issue:** `main()` defines `parser.add_argument("--alpha", type=float, default=None, help="unused override placeholder; draws are fixed per-plan")` and passes `args.alpha` through to `run_probe_n2(args.alpha)` / `run_probe_n4(args.alpha)`. Both functions accept an `alpha=None` parameter but never reference it in their bodies — draws are hardcoded tuples. A user passing `--alpha 2.0` expecting it to override the draw values gets no error and no effect; the help text is the only signal, easy to miss.

**Fix:** Either remove the `--alpha` argument entirely (draws are fixed per-plan, per the docstring), or make its unused status loud — e.g. `if args.alpha is not None: parser.error("--alpha is not implemented; draws are fixed per-plan")`.

### IN-02: Unused `total_modes` local variable

**File:** `mpair07_reuse_check.py:180`

**Issue:** `total_modes = 2 * n + len(ancilla_modes)` is computed at the top of `postselected_distribution` but never referenced again in the function body.

**Fix:** Remove the dead assignment.

### IN-03: Unused `ancilla_spec_a` / `ancilla_spec_b` and `conflict_pairs` variables

**File:** `mpair07_reuse_check.py:132, 141`; `pooled_allocation_baseline.py:125, 147 (`_try_colour`'s `conflict_pairs` parameter, never used inside the function body)`

**Issue:** `build_cp_insertion(...)`'s second return value is captured as `ancilla_spec_a`/`ancilla_spec_b` but discarded. Similarly, `backtracking_min_colouring` builds `conflict_pairs = None  # unused, kept for signature clarity` and threads it through to `_try_colour(pair_list, k, conflict_pairs)`, whose `conflict_pairs` parameter is likewise never read inside `_try_colour`.

**Fix:** Use `_` for intentionally-discarded values, and drop the unused `conflict_pairs` parameter/argument from `_try_colour`'s signature and call site (or wire it in if it was meant to speed up `neighbours()`/`adj` construction).

### IN-04: `check_round_robin` computes `uses_exactly_claimed` but never uses it

**File:** `pooled_allocation_baseline.py:190-210`

**Issue:** `uses_exactly_claimed = k_used <= k_claimed` is computed at line 207 but the function's return value only uses `all_in_range` (line 210: `return is_proper and all_in_range, ...`). The variable is dead.

**Fix:** Either fold `uses_exactly_claimed` into the returned correctness check (it appears to be a stricter/redundant variant of `all_in_range`) or remove it.

---

_Reviewed: 2026-08-21_
_Reviewer: Claude (gsd-code-reviewer)_
_Depth: standard_
