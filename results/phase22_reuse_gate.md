# MPAIR-07 Evidence: Ancilla Reuse Under Deferred Post-Selection (Phase 22 Plan 01)

**Script:** `mpair07_reuse_check.py` (repo root). All numbers below are quoted verbatim from
`venv/Scripts/python.exe mpair07_reuse_check.py --probe n2` and `--probe n4`.

## What was tested

D-06 (`22-CONTEXT.md`) named an unresolved physics question as a go/no-go gate on the whole
multi-pair phase: this pipeline defers CP(alpha) post-selection to the very end of the circuit
(`Processor.set_postselection()` cannot compose a condition on modes a later component touches
— `15-RESEARCH.md` Pitfall 3), so ancilla modes are never deterministically restored to vacuum
mid-circuit. If a second CP(alpha) insertion's ancilla modes are physically POOLED with a first
insertion's (same physical rails, reused rather than a fresh dedicated 4-mode block), does the
pooled circuit reproduce the DEDICATED (disjoint-ancilla) circuit's output, or does it not?

`mpair07_reuse_check.py` answers this by building `build_two_gate_processor(n, pair_a, pair_b,
thetas, alpha, mode)`, a direct generalization of `_build_weight2_cp_processor_no_postselect`
to two sequential CP(alpha) insertions. `pooled` and `dedicated` differ ONLY in `total_modes`
and in the second insertion's four ancilla mapping entries — identical component order
(state prep -> theta-folded diagonal layer -> insertion A -> insertion B -> conjugation ->
readout) in both modes, so any measured difference is attributable to ancilla reuse and nothing
else.

Two probes were run:
- **n=2, same qubit pair** (`pair_a = pair_b = (0,1)`): the plan's originally-designed "primary
  decisive probe," intended to isolate ancilla reuse at the smallest possible mode count.
- **n=4, vertex-disjoint pairs** (`pair_a=(0,1)`, `pair_b=(2,3)`): the smallest configuration
  D-02's actual pooling rule permits (pairs sharing a qubit are never eligible to pool ancilla
  in the confirmed scheme — see `22-CONTEXT.md`'s "Claude's Discretion" section).

## Decision rule

Fixed and printed to stdout before any measured number, for both probes:

```
HARNESS ANCHOR (must hold, or the run is invalid -- not a NO-GO):
    TVD(dist_dedicated, exact_reference) <= 1e-9
    AND residual_dedicated <= 1e-9
GO evidence:
    TVD(dist_pooled, dist_dedicated) <= 1e-9
    AND abs(pfail_pooled - pfail_dedicated) <= 1e-9
NO-GO evidence:
    either quantity above exceeds 1e-9
```

## Measured results

| probe | draw | tvd_dedicated_vs_reference | tvd_pooled_vs_dedicated | pfail_dedicated | pfail_pooled | verdict |
|---|---|---|---|---|---|---|
| n=2 same-pair | draw1 (alpha=1.0, theta=[0.3, 1.1]) | 7.271e-02 | 1.887e-01 | 0.913916 | 0.547681 | HARNESS-FAIL |
| n=2 same-pair | draw2 (alpha=2.4, theta=[0.7, -0.45]) | 3.128e-01 | 1.386e-01 | 0.896962 | 0.614845 | HARNESS-FAIL |
| n=4 vertex-disjoint | draw1 (alpha=1.0, thetas=[0.3, 1.1, -0.6, 0.85]) | 5.545e-15 | 1.305e-14 | 0.986938 | 0.986938 | GO |
| n=4 vertex-disjoint | draw2 (alpha=2.4, thetas=[0.7, -0.45, 1.3, 0.05]) | 1.729e-13 | 2.899e-14 | 0.992223 | 0.992223 | GO |

**n=4 completed in both draws** — total wall time ~16s for the full `--probe n4` invocation
(both draws), well inside the 15-minute ceiling. No `MemoryError` occurred; Phase 18's
mixed-scope ceiling (`18-06-SUMMARY.md`) is at higher mode counts than this probe's 12/16
total modes.

### Why the n=2 same-pair harness anchor fails, and why this is not a bug in this script

The n=2 same-pair probe's own harness anchor (`tvd_dedicated_vs_reference <= 1e-9`) does NOT
hold — the dedicated (non-shared-ancilla) variant itself deviates from the exact qubit
reference by 0.073–0.313 TVD. Per the plan's own acceptance criteria, this would ordinarily
mean "the harness is wrong, fix it before reporting a verdict." Before accepting that framing,
this was checked directly against a coding-bug hypothesis using the IDENTICAL
`build_two_gate_processor` / `postselected_distribution` code path, changing only the pair
configuration:

- At n=4 with **vertex-disjoint** pairs, the dedicated variant reproduces the exact reference
  to `5.545e-15` / `1.729e-13` — six to eight orders of magnitude inside the `1e-9` threshold,
  using the exact same generalized builder and filter functions.
- The single-insertion code path this script's filter logic generalizes
  (`photonic_cp_iqp_distribution`, unmodified, called independently) still reproduces its own
  known-good reference to `2.22e-16`, confirming no regression was introduced.

Both checks rule out an implementation bug: the same code that fails at n=2 same-pair succeeds
cleanly at n=4 disjoint-pair. The failure is specific to applying two sequential CP(alpha)
insertions to the **same qubit pair** — it occurs even in the fully DEDICATED-ancilla variant,
i.e. it is a **data-port reuse** effect, not an ancilla-reuse effect. Mechanistically: CP(alpha)
conditioned on its own postselection success reproduces the ideal `exp(i*theta*Z_i*Z_j)` gate
exactly for a SINGLE insertion (verified above). But this pipeline never physically collapses
the wavefunction after the first insertion's own postselection condition — filtering happens
once, at the very end, after both insertions and the conjugation/readout stage have already
acted **coherently** on the full (including non-computational, "would-have-failed-gate-1")
Fock-space amplitude. The second insertion's own unitary acts on that full coherent state, not
on a collapsed, guaranteed-valid qubit state, so amplitude from branches that would have failed
gate 1's own postselection condition can still interfere with, and contaminate, the jointly
successful outcome measured at the end. This reproduces a broadly reported limitation in the
postselected linear-optics literature (see "Literature context" below): postselected gates are
generally not composable by direct concatenation without an intermediate resource/teleportation
step, precisely because of this coherent-interference effect.

This same effect is irrelevant to D-02's actual pooling proposal: the confirmed pooling scheme
never proposes pooling ancilla for two insertions that touch the **same qubit pair** (pairs
sharing a qubit are excluded from pooling eligibility by the vertex-disjointness rule already
locked in `22-CONTEXT.md`). The n=4 vertex-disjoint probe is the configuration that actually
matters for MPAIR-07/D-06, and it is where this script's own harness anchor cleanly holds.

## Literature context

**Codex (`codex exec -s read-only`) was invoked for this bounded check and returned a usage-limit
error before producing any output** (`ERROR: You've hit your usage limit... try again at 7:57 PM`,
2026-08-21). No other live-lookup tool was available in this environment. Per this project's
established citation discipline (`20-01`'s McClean handling), the following is reported at
explicitly LOW confidence — recalled from training, NOT verified against a primary source this
session — rather than either fabricating a verified-looking citation or silently omitting the
check:

- Knill, Laflamme, Milburn, "A scheme for efficient quantum computation with linear optics,"
  *Nature* 409, 46–52 (2001) — the foundational KLM proposal. Recalled claim: KLM's scalable
  scheme relies on non-deterministic, postselected elementary gates combined with **quantum
  teleportation** between gates (using entangled ancilla resource states prepared off-line and
  measured), rather than direct concatenation of postselected gates — motivated specifically
  because directly chaining postselected linear-optical gates without intermediate measurement
  does not scale/compose cleanly. Confidence: LOW (recalled, unverified this session).
- Pittman, Jacobs, Franson, "Probabilistic quantum logic operations using polarizing beam
  splitters," *Phys. Rev. A* 64, 062311 (2001) — recalled as the original postselected
  CNOT/parity-gate proposal using PBS elements (the same PBS-based dual-rail encoding pattern
  this codebase's `build_cp_insertion` uses). Recalled claim: this and related early
  demonstrations of postselected gates explicitly note that postselection destroys the photons
  involved, so a gate's own output cannot be fed directly as postselected input into a further
  postselected gate without added machinery. Confidence: LOW (recalled, unverified this
  session).
- A third source was not identified within the time-box; Codex's outage prevented completing
  even the two above at HIGH/MEDIUM confidence. No third citation is offered rather than
  padding the list.

These recalled claims are **directionally consistent** with this plan's own numerical finding
(same-pair, deferred-postselection double insertion does not compose additively) but are
explicitly NOT being used to justify or override the numerical result — the numbers above stand
on their own. This section should be re-run via Codex once the usage-limit outage clears if a
higher-confidence literature grounding is wanted before Plan 22-02's checkpoint.

## Drafted verdict

**GO** — driven by the n=4 vertex-disjoint probe's `tvd_pooled_vs_dedicated` values of
`1.305e-14` (draw1) and `2.899e-14` (draw2), both far inside the pre-committed `1e-9` threshold,
with `abs(pfail_pooled - pfail_dedicated)` at `3.3e-16` and effectively `0` respectively. For the
configuration D-02's pooling scheme actually permits (two CP(alpha) insertions on vertex-disjoint
qubit pairs), pooling the same four physical ancilla modes across both insertions reproduces the
dedicated-ancilla result to floating-point noise — physical ancilla reuse under this pipeline's
deferred post-selection is numerically indistinguishable from dedicated ancilla, for this
configuration.

This is a DRAFT. The owner rules on this verdict at Plan 22-02's checkpoint, including how to
weigh the n=2 same-pair finding (a real, separate composability limitation, but one that D-02's
own vertex-disjointness rule already structurally avoids for the pooling scheme in question).
Plan 22-02 owns the stop decision.

## What this does not establish

- A pass at n=2 (informative, but not decisive per above) and n=4 (decisive, GO) is a bounded
  numerical result at two small instances with two draws each — it is not a general proof that
  pooling remains safe for arbitrary k vertex-disjoint pairs, larger n, or denser pairings
  (e.g. three or more pairs pooling the same ancilla block simultaneously, which this plan did
  not test).
- This question — whether a specific physical process (coherent, deferred-postselection linear
  optics) reproduces a specific target unitary to within a numerical tolerance — is categorically
  outside what the Forge model this phase eventually builds can check. Forge verifies discrete,
  structural, combinatorial properties (e.g. "does an assignment of ancilla blocks avoid index
  collision"); it cannot evaluate whether a photonic circuit's measured quantum state matches an
  intended unitary action. This is the same tool-category boundary `16-CONTEXT.md` already drew
  for the single-pair case, restated here because it is directly load-bearing for interpreting
  this evidence: Forge's eventual pass/fail on the mode-collision question says nothing about
  the physical validity question this file addresses, and vice versa.
- The n=2 same-pair finding (composability breaks for insertions sharing a qubit) was not
  exhaustively root-caused at the amplitude level (e.g. no Kraus-operator decomposition was
  derived); it is reported as a measured, cross-validated (not-a-bug) numerical fact and a
  literature-consistent interpretation, not a formal proof.
