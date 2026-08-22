# Phase 23 Lifecycle Run Log

## Run metadata

- **Run date:** 2026-08-22T20:58:57.4818548+02:00
- **Command:** `racket forge/ancilla_lifecycle_safety.frg`
- **Forge:** 5.2
- **Racket:** Welcome to Racket v8.15 [cs]
- **Forge package source:** `C:\Users\cuqui\cs1710\forge\forge`
- **Declared domain:** n=4 (`Pair` atoms are the six edges of K4), one four-mode block, two gates, nine ordered `State` atoms
- **Bound clause:** `for 7 Int, exactly 6 Pair, exactly 4 Mode, exactly 1 Block, exactly 2 Gate, exactly 9 State`
- **Solver configuration:** `option run_sterling off`

The model is intentionally bounded. The n=4 domain is the smallest domain with
two vertex-disjoint pairs that can be assigned the same four-mode block. No
depth sweep or n>4 run was attempted in this plan; the declared nine-state
scope is the explicit two-gate witness bound.

## Verbatim Forge stdout

```text
Forge version: 5.2
To report issues with Forge, please visit https://report.forge-fm.org
#vars: (size-variables 69078); #primary: (size-primary 1963); #clauses: (size-clauses 209519)
Transl (ms): (time-translation 1839); Solving (ms): (time-solving 3455)
    Test passed: unsafeSameEpochWitness
#vars: (size-variables 67707); #primary: (size-primary 1963); #clauses: (size-clauses 205484)
Transl (ms): (time-translation 668); Solving (ms): (time-solving 944) Core min (ms): (time-core 0)
    Test passed: noLiveReallocationUnderSafeProtocol
#vars: (size-variables 69266); #primary: (size-primary 1965); #clauses: (size-clauses 210004)
Transl (ms): (time-translation 423); Solving (ms): (time-solving 11624)
    Test passed: safeCrossEpochReuseWitness
```

## Verdict map

| Test | Expected | Actual | Solver timing |
|---|---:|---:|---:|
| `unsafeSameEpochWitness` | sat | passed | translation 1839 ms; solving 3455 ms |
| `noLiveReallocationUnderSafeProtocol` | unsat | passed | translation 668 ms; solving 944 ms |
| `safeCrossEpochReuseWitness` | sat | passed | translation 423 ms; solving 11624 ms |

The SAT unsafe test means an unsafe trace exists under the deliberately
permissive counterexample transition. It is not a safety approval. The UNSAT
test means the valid lifecycle transitions cannot contain that live
reallocation shape. The second SAT test is the separate safe witness after
terminal post-selection and release.

## LIFE-05: Phase 22 cross-check boundary

Phase 22's MPAIR-07 numerical probe measured a specific Perceval output
distribution comparison for n=4 vertex-disjoint pairs: pooled versus dedicated
ancilla modes. Its recorded `tvd_pooled_vs_dedicated` values were approximately
`1.305e-14` and `2.899e-14`, both inside the pre-committed `1e-9` tolerance
(`results/phase22_reuse_gate.md`). That is a numerical physical result for the
tested circuit and draw instances.

Phase 23 measures a different object: whether an explicit bounded lifecycle
trace permits a block to be allocated again while strict deferred
post-selection still marks it live. The primary comparison is therefore the
same-trace case: Phase 22 reports numerical indistinguishability for the
tested vertex-disjoint configuration, while Phase 23 reports structural
unsafety under the locked liveness discipline. This is an unresolved
abstraction-level disagreement, not evidence that either tool proves the
other wrong. The cross-epoch safe-reuse witness is a separate sanity check,
not a replacement for the primary same-trace comparison.

Forge does not prove Perceval amplitudes, output-distribution equivalence, or
physical unitary validity. Perceval's numerical GO does not prove the
structural lifecycle predicate. The two results are retained side by side.
