---
phase: 22
slug: multi-pair-ancilla-allocation-formal-verification
status: draft
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-20
---

# Phase 22 — Validation Strategy

> Per-phase validation contract for feedback sampling during execution.

**Phase-specific note:** this phase produces no application code and deliberately stays outside `pytest`, matching Phase 16's precedent for `forge/ancilla_mapping.frg` (Forge is a Racket toolchain, not a Python dependency; `pytest.ini`'s `testpaths = tests` must remain unaffected). "Tests" here means the Forge model's own `test expect` blocks plus a standalone brute-force baseline script.

---

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | None (Forge model runs standalone via `racket`, not wired into `pytest` — established convention per `16-CONTEXT.md`) |
| **Config file** | none |
| **Quick run command** | `racket forge/pooled_ancilla_allocation.frg` (exact filename at executor discretion) |
| **Full suite command** | `racket forge/pooled_ancilla_allocation.frg` + `venv/Scripts/python.exe pooled_allocation_baseline.py` |
| **Estimated runtime** | Forge: unknown — expected seconds under D-05's search framing, but hard-capped at the 5–10 min ceiling per D-04. Baseline: expected < 1 s. |
| **Regression guard** | `venv/Scripts/python.exe -m pytest -q` must stay green (currently 296 passing) — this phase must not touch it |

---

## Sampling Rate

- **After every task commit:** Re-run `racket forge/pooled_ancilla_allocation.frg` after any predicate, bound, or bitwidth change. Do **not** trust a prior SUMMARY's claim that it passed — ARB-09's own 2026-08-20 audit re-ran the model directly and found a stale source reference precisely because re-running is cheap and trusting is not.
- **After every plan wave:** Run the Forge model and the brute-force baseline together, recording both timings side by side in the `results/phase16_forge_summary.md` comparison-table format.
- **Before `/gsd:verify-work`:** Both `test expect` blocks passing with the specified verdicts, a timed brute-force comparison recorded, and the Python suite still green.
- **Max feedback latency:** 10 minutes (the D-04 ceiling); anything longer is itself the reportable finding, not a reason to wait.

---

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 22-01-xx | 01 | 0 | MPAIR-07 | manual (physics go/no-go) | — see Manual-Only below | ❌ W0 | ⬜ pending |
| 22-02-xx | 02 | 1 | MPAIR-02 | manual (prose invariant review) | — see Manual-Only below | ❌ W0 | ⬜ pending |
| 22-03-xx | 03 | 2 | MPAIR-03 | Forge `is unsat` | `racket forge/pooled_ancilla_allocation.frg` | ❌ W0 | ⬜ pending |
| 22-03-xx | 03 | 2 | MPAIR-04 | Forge `is sat` (non-vacuity) | `racket forge/pooled_ancilla_allocation.frg` | ❌ W0 | ⬜ pending |
| 22-04-xx | 04 | 3 | MPAIR-05 | timed comparison | `venv/Scripts/python.exe pooled_allocation_baseline.py` | ❌ W0 | ⬜ pending |
| 22-05-xx | 05 | 4 | MPAIR-06 | doc review + link check | `grep -n "Pooled" docs/iqp-photonic-encoding.md` | ❌ W0 | ⬜ pending |

*Status: ⬜ pending · ✅ green · ❌ red · ⚠️ flaky*

**MPAIR-01 has no row** — it was satisfied during `/gsd-discuss-phase 22` (owner selected pooled/recycled from three unranked candidates; selection and rejected alternatives recorded in `22-CONTEXT.md` D-02 and `22-DISCUSSION-LOG.md`). Nothing to execute.

---

## Wave 0 Requirements

- [ ] `forge/pooled_ancilla_allocation.frg` — does not exist; this phase creates it (analogous to Phase 16 creating `forge/ancilla_mapping.frg` from nothing).
- [ ] Brute-force baseline script (Python, standalone, **not** under `tests/`) — new for this phase per MPAIR-05. Must be a colouring **search** (greedy/backtracking), not a 406-case verification loop, or the comparison is a strawman (D-05).
- [ ] No pytest infrastructure gap — this phase deliberately stays outside `pytest`.

---

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Deferred post-selection permits (or forbids) physical ancilla reuse across sequential CP(α) gates | MPAIR-07 | A unitarity/physics claim, categorically outside what a bounded model finder can check — the same tool-category boundary `16-CONTEXT.md` already drew around Forge | Amplitude calculation and/or literature check on ancilla reuse in post-selected linear-optical gates. **Stop condition: a "reuse is invalid" verdict halts the phase** — report the finding, do not proceed to model an unbuildable scheme. |
| The stated invariant means what it claims | MPAIR-02 | Prose precision cannot be machine-checked; the pairwise-reduction argument is the load-bearing step and must be reviewed by a human before the model encodes it | Read the invariant statement against D-05's reduction argument. Confirm it names: the compatibility rule, the fixed-allocation condition the reduction depends on, and the explicit scope boundary that index-level non-collision ≠ physical reuse validity. |
| Bitwidth is sufficient for the final formula | MPAIR-03 | Silent integer overflow produces a passing model that verified the wrong arithmetic — the exact failure class this project's bitwidth-note discipline exists to prevent | Compute the largest mode index the final formula produces at n=8; confirm it fits the chosen `for N Int` range. **`for 6 Int` (`[-32,31]`) is known insufficient** — max index ≈ 43. Minimum `for 7 Int`. |
| Forge's search actually engaged | MPAIR-05 | Requires judgment comparing two runtimes and stating an honest verdict; a green test proves nothing about whether the tool earned its place | Compare Forge and baseline timings. State plainly whether Forge added anything over brute force. **A "no it didn't" verdict satisfies the requirement** — only an unchecked assertion fails it. |

---

## Validation Sign-Off

- [ ] MPAIR-07 gate resolved with an explicit verdict **before** any `.frg` file exists
- [ ] Both `test expect` blocks present and returning their specified verdicts (`sat` for non-vacuity, `unsat` for no-counterexample)
- [ ] Non-vacuity check requires ≥ 2 simultaneously-active, mutually-compatible pairs that actually share a block — not merely `some active` (which would pass on a single-pair instance and be vacuous in a new way the scalar model never faced)
- [ ] Bitwidth recomputed against the final formula, not copied from `ancilla_mapping.frg`
- [ ] Brute-force baseline is a search, not a verification loop
- [ ] `venv/Scripts/python.exe -m pytest -q` still green (296 passing) — no regression
- [ ] Feedback latency < 600s, or the timeout itself recorded as the finding
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending
