---
phase: 23-ancilla-lifecycle-safety-formal-verification
slug: ancilla-lifecycle-safety-formal-verification
status: validated-partial
nyquist_compliant: false
wave_0_complete: true
created: 2026-08-23
---

# Phase 23 — Validation Strategy

> Retrospective validation reconstructed from the executable Forge model, its
> preserved run log, trace projections, and the phase verification report.

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Forge 5.2 via Racket 8.15; pytest 9.1.1 for the repository suite |
| **Config file** | `pytest.ini` (`testpaths = tests`); no Forge test config |
| **Quick run command** | `racket forge/ancilla_lifecycle_safety.frg` |
| **Full suite command** | `racket forge/ancilla_lifecycle_safety.frg`; `venv/Scripts/python.exe -m pytest -q` for repository regression coverage |
| **Observed runtime** | Forge completed successfully; current pytest collection was blocked by Perceval log-file permission |

## Sampling Rate

- **After every model change:** Run `racket forge/ancilla_lifecycle_safety.frg`.
- **Before phase sign-off:** Run the Forge suite and inspect the preserved run log and trace projections.
- **Regression check:** Run `venv/Scripts/python.exe -m pytest -q` when the Perceval logger is writable.
- **Feedback latency:** Forge run completed in under two minutes in the current environment.

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 23-01 | 01 | 1 | LIFE-01 | — | Explicit State.next trace models blocks, modes, and lifecycle events | bounded formal model | `racket forge/ancilla_lifecycle_safety.frg` | ✅ | ✅ green |
| 23-01 | 01 | 1 | LIFE-02 | — | Safe protocol has no live reallocation; unsafe same-epoch witness is separately exhibited | bounded formal model | `racket forge/ancilla_lifecycle_safety.frg` | ✅ | ✅ green |
| 23-01 | 01 | 1 | LIFE-03 | — | Finish preserves liveness; post-selection and release perform the terminal transitions | bounded formal model | `racket forge/ancilla_lifecycle_safety.frg` | ✅ | ✅ green |
| 23-01 | 01 | 1 | LIFE-04 | — | Two-gate cross-epoch reuse occurs only after release | bounded formal model | `racket forge/ancilla_lifecycle_safety.frg` | ✅ | ✅ green |
| 23-02 | 02 | 2 | LIFE-05 | — | Structural Forge and numerical Phase 22 evidence remain explicitly separated | evidence/report | `rg -n "MPAIR-07|numerical|structural|same-trace|cross-epoch|unresolved" results/phase23_lifecycle_run_log.md` | ✅ | ✅ green |
| 23-03 | 03 | 3 | LIFE-06 | — | Static minimum-K and temporal capacity are stated as separate constraints | evidence/report | `rg -n "LIFE-06|minimum-K|static|temporal|bounded" results/phase23_lifecycle_summary.md` | ✅ | ✅ green |
| 23-03 | 03 | 3 | LIFE-07 | — | Canonical encoding documentation contains the Phase 23 lifecycle section and evidence links | documentation check | `rg -n "Ancilla Lifecycle Safety|phase23_lifecycle|LIFE-0[1-7]" docs/iqp-photonic-encoding.md .planning/REQUIREMENTS.md` | ✅ | ✅ green |

## Wave 0 Requirements

Existing infrastructure covers the executable phase requirements. No new test
file was needed: the model's three named `test expect` blocks are the phase's
behavioral tests.

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Human-readable unsafe and safe lifecycle tables accurately project the bounded witness predicates | LIFE-02, LIFE-04 | Sterling is disabled and Forge stdout contains verdicts/timings, not symbolic atom instances; the trace artifact explicitly labels its tables as projections | Compare `results/phase23_lifecycle_traces.md` with `forge/ancilla_lifecycle_safety.frg` and the verbatim stdout in `results/phase23_lifecycle_run_log.md`. |
| Owner interpretation of the structural/numerical boundary and static-vs-temporal conclusion | LIFE-05, LIFE-06 | Conceptual interpretation cannot be established by the solver alone | Review `results/phase23_lifecycle_summary.md` under `## Owner review`; confirm the four interpretation points remain approved. |
| Full repository regression suite | — | Current environment denied Perceval's external log file during collection | Re-run `venv/Scripts/python.exe -m pytest -q` with `C:\Users\cuqui\AppData\Local\quandela\perceval-quandela\logs\perceval.log` writable; prior phase evidence records 296 passed. |

## Actual Verification Evidence

- `racket forge/ancilla_lifecycle_safety.frg` — exit 0; `unsafeSameEpochWitness`, `noLiveReallocationUnderSafeProtocol`, and `safeCrossEpochReuseWitness` all passed.
- `venv/Scripts/python.exe -m pytest -q` — not green in this run: collection failed with `Permission denied` opening Perceval's user log, before test execution. This is an environment limitation, not evidence that Phase 23 behavior failed.
- `git diff --check` and the Phase 23 verification report provide additional documentation-integrity evidence.
- Scope remains bounded to n=4 and nine states; no unbounded theorem, Perceval amplitude equivalence, physical unitary equivalence, Python k-pair implementation, or new hardness-under-loss result is claimed.

## Validation Sign-Off

- [x] All phase tasks have an executable or evidence-backed verify command
- [x] Sampling continuity is documented across all three plan waves
- [x] No watch-mode flags
- [x] Forge feedback latency is bounded and observed
- [ ] Full repository regression suite green in this environment
- [ ] `nyquist_compliant: true` — retained false because trace projection and conceptual owner interpretation remain explicit manual gates

**Approval:** validated partial 2026-08-23; Forge evidence green, pytest regression rerun required after environment permission repair.

