# Phase 18 Timing Probe (Plan 18-05)

Per `18-RESEARCH.md`'s "Open Question 2" and this project's established
Phase-17 practice of checking before committing: a handful of real,
machine-measured single-cell (n, eta) timing calls, run via
`loss_sweep.py`'s chunk mode (`--draw-start 0 --draw-count 1`) so each
number is a genuine single-draw invocation of the actual sweep code path
(`hardness.sweep.pooled_cell_for_neta`), not an extrapolation. Machine: this
project's own dev machine (the same one documented in `STATE.md`'s memory-
constraint note), venv `perceval-quandela==1.2.4`.

Each `pooled_cell_for_neta` call for a given (n, eta, scope) performs TWO
full `Processor.probs()` calls per draw (the eta=1.0 lossless reference,
computed via the same loss-model function per 18-CONTEXT.md's lock, plus
the requested eta) -- roughly double the cost of a single bare loss-model
call, which is why the numbers below run higher than
`18-RESEARCH.md`'s single-call figures.

## Weight-1 scope, n=6

All 7 `ETA_GRID` points measured in one chunked invocation
(`loss_sweep.py --scope weight1 --n-values 6 --draw-start 0 --draw-count 1`):

| eta  | wall time |
|------|-----------|
| 0.99 | 141.2s |
| 0.95 | 129.5s |
| 0.90 | 136.6s |
| 0.80 | 142.9s |
| 0.60 | 145.3s |
| 0.35 | 144.7s |
| 0.05 | 153.5s |

Mean: ~133s/cell (range 129.5s-153.5s -- flat across eta, as expected: the
circuit topology/mode count is identical across eta, only the `LC`
transmittance parameter changes). Total wall time for all 7 cells:
16m43s.

**This is a genuine surprise relative to `18-RESEARCH.md`'s sizing note**,
which measured weight-1 as "trivial" (0.07s/cell) at n=4 and predicted
weight-1 loss sweeps would "stay tractable... likely beyond" n=6 on that
basis. The real n=6 number is ~1900x the n=4 number over 2 n-steps (~43x
per n-step) -- i.e. weight-1's `LC`-loss wall-time growth is NOT flat
relative to its own `3^n` output-state-count growth, contrary to the
research note's optimistic reading of n<=4 data. Weight-1 n=7 was NOT
attempted: the plan's stretch condition ("if [n=6] is fast, also try n=7")
does not hold -- 133s/cell already far exceeds "fast" -- so the stretch
probe was explicitly skipped rather than run and left to fail slowly.

## Mixed scope, n=4

All 7 `ETA_GRID` points measured in one chunked invocation
(`loss_sweep.py --scope mixed --n-values 4 --draw-start 0 --draw-count 1`):

| eta  | wall time |
|------|-----------|
| 0.99 | 42.8s |
| 0.95 | 44.3s |
| 0.90 | 42.0s |
| 0.80 | 43.2s |
| 0.60 | 44.0s |
| 0.35 | 44.0s |
| 0.05 | 43.6s |

Mean: ~43.4s/cell (flat across eta, same reasoning as weight-1 above).
Total wall time for all 7 cells: 5m16s. Roughly `2 x 16.8s` (Phase 18-03's/
`18-RESEARCH.md`'s single-call n=4 measurement of 16.8s) plus baseline/TVD
overhead -- consistent with the "two `Processor.probs()` calls per draw"
explanation above, not a new surprise.

## Mixed scope, n=5

Measured directly (not extrapolated) via two independent single-cell
attempts, each its own fresh process:

| attempt | eta  | outcome | wall time before failure |
|---------|------|---------|---------------------------|
| 1 | 0.99, 0.35 (first of the two attempted) | `MemoryError: bad allocation` inside `perceval.simulators.simulator.Simulator.probs_svd` (called from `Processor.probs()`) | 2m52.6s |
| 2 (retry) | 0.99 only | Same `MemoryError: bad allocation`, same call site | 4m18.6s |

Free physical memory was checked before the retry (`Get-CimInstance
Win32_OperatingSystem`): 5,164,564 KB (~5.16 GB) free out of 16,099,644 KB
(~16 GB) total -- a materially better condition than `STATE.md`'s
documented worst case (~1 GB free), yet the retry failed identically. This
rules out a one-off transient memory-pressure spike from a concurrent
process (this project's established false-positive pattern from Phase 17)
as the explanation -- **this is a reproducible, real ceiling for mixed n=5
under the current `LC`-loss pipeline, not noise.**

**Important distinction from Phase 17's mixed n=5 `MemoryError` pattern:**
Phase 17's mixed n=5 `MemoryError` was a *cross-call* leak -- it took
~600 repeated (loss-free) `Analyzer` calls within one long-running process
before memory was exhausted, and chunking draws across fresh processes
fixed it completely (a single call succeeded in ~4s). Here, the failure
occurs *inside the very first* `Processor.probs()` call of a fresh process
that has run nothing else -- the `2n+2=12`-mode, `LC`-loss-doubled Fock
space for weight-2 at n=5 apparently exceeds available contiguous memory
for a SINGLE strong-simulation call. **Draw-range chunking (this phase's
own resumability mechanism, `--draw-start`/`--draw-count`) cannot fix
this** -- it splits which draws run in which process, not how much memory
one draw's own single call needs.

## Final n-range decision

**Weight-1 scope:** CORE range is `n = 2..6`, matching Phase 17's own
established weight-1 ceiling -- n=6 is confirmed reachable (measured
~133s/cell), just far more expensive than `18-RESEARCH.md`'s optimistic
reading anticipated. At Plan 18-06's planned `n_draws=5` (this phase's own
default) and the full 7-point `ETA_GRID`, n=6 alone costs an estimated
`133s x 7 x 5 ≈ 4655s ≈ 77.6 minutes`; n=5's per-cell cost was not
separately measured for weight-1 (only n=4's near-trivial and n=6's ~133s
were), so the full n=2..6 CORE sweep's total wall time is estimated in the
range of roughly 1.5-2.5 hours, not a small number -- **Plan 18-06 should
run this via `loss_sweep.py`'s chunked/resumable mode (`--draw-start`/
`--draw-count`/`--combine-chunks`), one n at a time, not as a single
long-running synchronous invocation**, both to bound per-process memory
growth (this machine's documented constraint) and to make partial progress
resumable if a session boundary or crash interrupts it. Weight-1 n=7 is
explicitly NOT attempted (see above) -- not silently dropped, but ruled
out by this plan's own measured n=6 result, per the plan's own stated
stretch condition.

**Mixed scope:** CORE range is `n = 2..4` -- n=4 is confirmed reachable
(measured ~43.4s/cell; full 7-point `ETA_GRID` at `n_draws=5` costs an
estimated `43.4s x 7 x 5 ≈ 1519s ≈ 25.3 minutes`, comfortably within a
single session). **Mixed n=5 is explicitly NOT a CORE requirement** --
this is not a "slow but eventually finishes" judgment call, it's a
reproducible hard `MemoryError` on the very first call, confirmed twice at
different eta values with ~5.16 GB free memory both times (see above).
Per this task's own instruction not to silently drop it either: Plan 18-06
MAY attempt mixed n=5 once, as a best-effort, likely-to-fail STRETCH probe
(mirroring Phase 17's own n=7 weight-1/n=6 mixed STRETCH precedent of
attempting and honestly reporting the outcome, "no fixed time-box" per
18-CONTEXT.md) -- but should NOT budget compute time expecting success,
should NOT attempt chunking as a fix (chunking does not address a
single-call memory ceiling, per the distinction above), and a repeat
`MemoryError` should be reported as confirmation of this same measured
ceiling, not treated as a new bug requiring debugging.
