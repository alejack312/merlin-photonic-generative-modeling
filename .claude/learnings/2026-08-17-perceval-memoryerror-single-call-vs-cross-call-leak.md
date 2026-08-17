# Perceval MemoryError: is it a cross-call leak or a single-call ceiling?
Date: 2026-08-17 · Scope: project · Recurs when: sizing a compute-heavy Perceval `Processor.probs()` sweep in this repo (any future phase that adds loss channels, ancilla modes, or otherwise grows mode/photon count beyond Phase 17's original Analyzer-based ceilings) and it hits `MemoryError: bad allocation`.

## Context & constraints
- This machine has documented, materially constrained free memory during heavy background compute (STATE.md: as low as ~1GB free with zero of this project's own processes running).
- Phase 17 already established one `MemoryError` pattern: memory accumulates ACROSS ~hundreds of repeated calls within one long-running process (e.g. mixed n=5's gradient sweep leaking over ~600 calls), even though a single call is cheap. Fixed by draw-range chunking across fresh processes (`--draw-start`/`--draw-count`/`--combine-chunks`).
- Phase 18's weight-2 loss primitive (`hardness/loss_model_weight2.py`) adds `pcvl.LC` loss components on all `2n+2` modes on top of the already-expensive `heralded_cz` circuit — a materially larger Fock space per call than Phase 17's loss-free `Analyzer` enumeration.

## Approach
1. When a `MemoryError` appears during a Perceval sweep, don't assume it's automatically Phase 17's known cross-call-leak pattern just because that's the precedent in this repo. Check WHERE in the run it failed:
   - If it failed after many prior successful calls within the same process -> cross-call leak, chunking will fix it.
   - If it failed on the very FIRST call of a fresh process (confirmed here: `MemoryError` inside `Processor.probs()` -> `Simulator.probs_svd`, before any result printed) -> single-call ceiling, chunking cannot fix it.
2. Rule out transient memory pressure from concurrent processes before treating a single-call failure as a real ceiling: check free physical memory (`Get-CimInstance Win32_OperatingSystem | Select FreePhysicalMemory` on Windows) immediately before a retry, and retry once. If the retry fails identically with comparable/adequate free memory (here: ~5.16GB free both times, well above the ~1GB documented worst case), it's a reproducible ceiling, not noise.
3. Report a single-call ceiling honestly as infeasible-at-this-n, rather than budgeting compute time or chunking machinery at it expecting eventual success.

## Decision rules that generalize
- IF a `MemoryError` traceback shows the failure inside the FIRST call of a fresh process (no prior successful calls in that process), THEN draw/chunk-range chunking (this repo's standard sweep mitigation) will NOT help — the fix space is: reduce n, reduce mode/photon count some other way, or accept the cell as unreachable.
- IF a `MemoryError` only appears after many prior successful calls in one long process, THEN chunking across fresh processes is the correct, already-proven fix.
- IF unsure which pattern applies, run ONE retry with free-memory checked immediately before it. A repeat failure at comparable-or-better free memory than the documented worst case confirms a real ceiling.

## Mistakes avoided / dead ends
- Did not assume the first `MemoryError` (mixed n=5, eta=0.99/0.35 chunk) was a transient concurrent-load spike and immediately retry with a smaller batch size — checked free memory first (5.16GB, well above the ~1GB documented worst case) so a second failure would be interpretable as a real ceiling rather than "maybe just bad luck," and it was.
- Did not attempt to "fix" the mixed n=5 ceiling with the repo's existing draw-chunking CLI flags — that mechanism addresses a different failure shape (cross-call accumulation) and would have wasted a full sweep attempt's worth of compute time discovering it doesn't apply.

## Verification
- 2 independent single-cell attempts (different eta values: `{0.99, 0.35}` then `{0.99}` alone), both fresh processes, both failed with the identical traceback (`Simulator.probs_svd` -> `MemoryError: bad allocation`) before producing any output line.
- Free memory checked immediately before the second attempt: 5,164,564 KB (~5.16GB) free of 16,099,644 KB (~16GB) total.

## Next time (for a weaker model)
- Do: read the full traceback to see whether the failure is inside the FIRST call of a fresh process or after N successful calls; check free memory and retry once before concluding it's a real ceiling; report a real single-call ceiling plainly rather than looping chunking attempts at it.
- Don't: reflexively apply this repo's established draw-chunking fix to every `MemoryError` — it only fixes the cross-call-leak shape, not a single-call ceiling.

## Changed files
- results/phase18_timing_probe.md — documents both measured mixed n=5 `MemoryError` attempts and the resulting "not a CORE requirement" decision.
