# Phase 16 Forge Verification Summary (ARB-09)

**What was modeled:** the ancilla mode-mapping dict inside `_build_weight2_cp_processor_no_postselect`
(`iqp_photonic_encoding.py:622-627`) — `{2i:0, 2i+1:1, 2j:2, 2j+1:3, 2n:4, 2n+1:5, 2n+2:6, 2n+3:7}`,
the local-circuit-index target of qubit `i`/`j`'s dual-rail data ports plus the 4 tail ancilla
modes. The property checked is that the 8 dict **keys** — `{2i, 2i+1, 2j, 2j+1, 2n, 2n+1, 2n+2, 2n+3}` —
are pairwise distinct (injective) for every valid `(n, i, j)`, checked against **all** `n` qubits'
own data ports (`0..2n-1`), not just qubit `i`/`j`'s — the fully general non-aliasing property, per
`16-CONTEXT.md`. Model: `forge/ancilla_mapping.frg`.

**Bound checked:** `n` from 2 to 8 inclusive (`0 <= i,j < n`, `i != j`), at Forge bitwidth `for 6 Int`
(signed range `[-32, 31]`) — chosen because the model's largest computed value, `2n+3` at `n=8`, is
`19`, comfortably inside `[-32, 31]` with headroom, avoiding any silent integer wraparound at
Forge's default 4-bit bitwidth (`[-8, 7]`).

**Result — `racket forge/ancilla_mapping.frg` (exit code 0):**

```
Forge version: 5.2
 branch: HEAD
 commit: 2f80c9e6
 timestamp: Fri Mar 6 18:09:13 2026 +0000
Skipping version check vs. main branch.
To report issues with Forge, please visit https://report.forge-fm.org
#vars: (size-variables 3306); #primary: (size-primary 192); #clauses: (size-clauses 10443)
Transl (ms): (time-translation 249); Solving (ms): (time-solving 167)
    Test passed: nonVacuous
#vars: (size-variables 3778); #primary: (size-primary 192); #clauses: (size-clauses 12125)
Transl (ms): (time-translation 227); Solving (ms): (time-solving 506) Core min (ms): (time-core 0)
    Test passed: noCounterexample
```

Both required checks passed: `nonVacuous` (sat — at least one valid `(n,i,j)` instance exists,
guarding against a vacuously-true, over-constrained model) and `noCounterexample` (unsat — no
`(n,i,j)` within the checked bound violates injectivity/non-collision).

**Verdict:** the ancilla mode-mapping dict is confirmed injective and non-aliasing for all valid
`(n,i,j)` with `2 <= n <= 8` — no bug found. This matches `16-CONTEXT.md`'s expectation that the
property is provably true by construction (ancilla ports start at `2n`, which is always `>=` the
largest qubit data port `2n-1`), and formally confirms it rather than leaving it as an informal
observation.
