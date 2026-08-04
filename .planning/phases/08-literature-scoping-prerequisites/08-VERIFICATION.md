---
phase: 08-literature-scoping-prerequisites
verified: 2026-08-04T17:00:00Z
status: passed
score: 10/10 must-haves verified
re_verification:
  previous_status: gaps_found
  previous_score: 9/10
  gaps_closed:
    - "A working manual Perceval circuit is built and run using Circuit/PS/BS/BasicState/Analyzer directly, without QuantumLayer.simple()"
  gaps_remaining: []
  regressions: []
---

# Phase 8: Literature Scoping and Prerequisites Verification Report

**Phase Goal:** Determine whether a discrete-variable (DV, Fock-space) linear-optical construction of IQP is worth designing at all, and confirm the technical/reference prerequisites that any subsequent design work depends on.
**Verified:** 2026-08-04
**Status:** passed
**Re-verification:** Yes, after gap closure (plan 08-04)

## Goal Achievement

### Observable Truths

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | Go/no-go verdict on Phase 9 written explicitly, citing both a constructive and a disconfirming search pass, owner reasoning recorded | VERIFIED (regression check, unchanged since prior verification) | docs/iqp-lit-scoping.md, Go/No-Go Verdict section, 104 lines total, file unchanged since prior pass |
| 2 | Douce et al. CV construction summarized from a full-text read, positions DV/Fock design against it | VERIFIED (regression check) | docs/iqp-lit-scoping.md lines 5-32, unchanged |
| 3 | Verdict and summary explicitly distinguish CV-quadrature from Fock-space/photon-number encoding, never conflated | VERIFIED (regression check) | docs/iqp-lit-scoping.md lines 30-32, unchanged |
| 4 | LIT-03 (MerLin reproduced-papers catalog check) cited in the writeup for coverage | VERIFIED (regression check) | docs/iqp-lit-scoping.md lines 81-83, unchanged |
| 5 | Owner attempted or sketched a manual Perceval circuit before Claude wrote the final implementation | VERIFIED (attested, regression check) | 08-02-SUMMARY.md Checkpoint Resolution section, unchanged; process claim, not independently re-confirmable from file artifacts |
| 6 | Working manual Perceval circuit built and run using Circuit, PS, BS, BasicState, Analyzer directly, without QuantumLayer.simple() | VERIFIED, gap closed | perceval_fluency_demo.py now contains build_mzi_circuit(theta) which calls circuit.add(0, pcvl.PS(theta)) between two pcvl.BS.H() components (line 78), forming a real BS-PS-BS Mach-Zehnder interferometer. grep for pcvl.PS( in perceval_fluency_demo.py returns exactly this line, an actual instantiation wired into the circuit, not a comment. grep for QuantumLayer.simple across the repo shows zero matches in perceval_fluency_demo.py or tests/test_perceval_fluency_demo.py (matches found elsewhere belong to unrelated files: quickstart.py, generator/, tests/test_mmd.py, not this deliverable). Live-ran PYTHONIOENCODING=utf-8 ./venv/Scripts/python.exe perceval_fluency_demo.py: prints PASS for single-photon split, HOM dip, and all three MZI theta values (0, pi/2, pi), with output distributions exactly matching cos^2(theta/2)/sin^2(theta/2): theta=0 gives P(1,0)=1.0; theta=pi/2 gives P(1,0)=P(0,1)=0.5; theta=pi gives P(0,1)=1.0. |
| 7 | Circuit output checked against a known closed-form result programmatically, not just eyeballed | VERIFIED, extended | check_single_photon, check_hom_dip, check_mzi all use np.isclose; script asserts all five checks and prints PASS/FAIL. Live-ran PYTHONIOENCODING=utf-8 ./venv/Scripts/python.exe -m pytest tests/test_perceval_fluency_demo.py -v: 6 of 6 passed (3 original tests plus 3 parametrized MZI theta tests), 12.61s. |
| 8 | A single reference doc compiles prior IQP structure/hardness and barren-plateau trainability notes as qubit-side baseline | VERIFIED (regression check) | docs/iqp-baseline.md, 42 lines, unchanged |
| 9 | Both IQP structure/hardness and barren-plateau trainability covered with roughly equal weight | VERIFIED (regression check) | unchanged, balanced sections |
| 10 | Doc states which specific source files it draws from, matching grounding-statement convention | VERIFIED (regression check) | docs/iqp-baseline.md lines 3-6, unchanged, all three paths confirmed to exist |

Score: 10/10 truths verified. The one gap from the prior verification (truth 6, PS usage) is now closed.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| docs/iqp-lit-scoping.md | LIT-01/LIT-02/LIT-04 deliverable, min 60 lines, contains Go/No-Go Verdict heading | VERIFIED (unchanged) | 104 lines, no stub patterns |
| perceval_fluency_demo.py | Manual low-level Perceval demo exercising Circuit/PS/BS/BasicState/Analyzer | VERIFIED, gap closed | 200 lines (was 130), now instantiates and wires pcvl.PS(theta) in build_mzi_circuit, adds run_mzi_analyzer, check_mzi, and a main() sweep over theta in [0, pi/2, pi]. Live-run confirms all checks PASS. No QuantumLayer.simple(). |
| tests/test_perceval_fluency_demo.py | Automated test asserting closed-form predictions, including the new PS/MZI construction | VERIFIED, extended | 48 lines (was shorter), 6 tests total, all pass live (pytest run: 6 passed in 12.61s), including parametrized test_mzi_interference over theta in [0, pi/2, pi] |
| docs/iqp-baseline.md | 1-2 page qubit-side reference, min 40 lines, contains a heading | VERIFIED (unchanged) | 42 lines |

### Key Link Verification

| From | To | Via | Status | Details |
|------|-----|-----|--------|---------|
| docs/iqp-lit-scoping.md verdict section | search findings and Douce summary sections, same doc | explicit above citation | VERIFIED (unchanged) | unchanged from prior pass |
| perceval_fluency_demo.py | perceval.algorithm.Analyzer | Processor wraps Circuit, passed into Analyzer | VERIFIED (unchanged) | unchanged pattern, still correct |
| perceval_fluency_demo.py | perceval.PS | circuit.add(0, pcvl.PS(theta)) placed between two BS.H() components, forming a BS-PS-BS Mach-Zehnder interferometer | WIRED, gap closed | build_mzi_circuit(theta) (lines 70-80) builds exactly this construction; run_mzi_analyzer(theta) (lines 83-98) wraps it in a Processor and runs it through Analyzer; check_mzi(dist, theta) (lines 101-110) asserts the closed-form prediction with np.isclose; main() (lines 183-193) sweeps theta over [0, pi/2, pi] and asserts all pass. Live-run confirms correct physics: theta=0 gives P(1,0)=1.0 (fully constructive), theta=pi/2 gives 50/50, theta=pi gives P(0,1)=1.0 (fully flipped), exactly matching the derived closed form. |
| docs/iqp-baseline.md | sibling project iqp-classical-sampling.md, Barren Plateaus.md, Final Findings doc | explicit source citation in grounding statement | VERIFIED (unchanged) | unchanged |

### Requirements Coverage

| Requirement | Status | Blocking Issue |
|-------------|--------|-----------------|
| LIT-01 (literature search for DV/Fock IQP construction) | SATISFIED | unchanged |
| LIT-02 (Douce et al. full-text read and summary) | SATISFIED | unchanged |
| LIT-03 (MerLin catalog check) | SATISFIED, carried forward, already complete 2026-07-30 | unchanged |
| LIT-04 (go/no-go verdict) | SATISFIED | unchanged |
| PREQ-01 (Perceval low-level API fluency) | FULLY SATISFIED (was PARTIAL) | Demo now exercises all five named primitives (Circuit, PS, BS, BasicState, Analyzer) directly, no QuantumLayer.simple(), every output checked against closed-form predictions programmatically |
| PREQ-02 (qubit-side baseline doc) | SATISFIED | unchanged |

Note: .planning/REQUIREMENTS.md checkboxes for LIT-01, LIT-02, LIT-04, PREQ-01, PREQ-02 are still shown as unchecked, and its requirements-coverage table still lists them as Pending, as of this re-verification. This is the same documentation-bookkeeping gap flagged in the prior verification, unresolved by plan 08-04 (which was scoped narrowly to the PS gap, correctly so, it did not claim to touch REQUIREMENTS.md or ROADMAP.md). Not a code or artifact gap; flagged again for the orchestrator to update these checkboxes now that Phase 8 has a passed verification on record.

### Anti-Patterns Found

| File | Line | Pattern | Severity | Impact |
|------|------|---------|----------|--------|
| .planning/REQUIREMENTS.md | 14-22 | Stale unchecked checkboxes for completed requirements (LIT-01, LIT-02, LIT-04, PREQ-01, PREQ-02) | Info | Documentation currency only, no functional impact |

No blocker or warning-level anti-patterns (TODO, FIXME, placeholder, stub returns) found in any of the phase-produced files (docs/iqp-lit-scoping.md, docs/iqp-baseline.md, perceval_fluency_demo.py, tests/test_perceval_fluency_demo.py).

### Human Verification Required

None outstanding. The prior human-verification item (confirm the PS omission gap resolution path) has been resolved: plan 08-04 added the PS-based Mach-Zehnder example rather than seeking a waiver, and this re-verification independently confirms the addition is real, wired, and passing live.

### Gaps Summary

No gaps remain. Plan 08-04 closed the single gap identified in the prior verification: perceval_fluency_demo.py now instantiates and uses pcvl.PS inside a genuine BS.H to PS(theta) to BS.H Mach-Zehnder construction, with its output distribution checked against the closed-form prediction P(1,0) = cos^2(theta/2), P(0,1) = sin^2(theta/2) across theta in [0, pi/2, pi], verified both by direct script execution (all PASS) and by an automated, parametrized pytest suite (6 of 6 passed). All five named Perceval primitives (Circuit, PS, BS, BasicState, Analyzer) are now genuinely exercised without QuantumLayer.simple(). Combined with the already-verified go/no-go literature verdict (LIT-01/02/03/04) and the qubit-side baseline doc (PREQ-02), all five of ROADMAP.md Phase 8 success criteria are met. Phase 8 is fully verified with no code or artifact gaps; the only outstanding item is a documentation-bookkeeping one (stale checkboxes in REQUIREMENTS.md), not a functional gap, and does not block Phase 9.

---

Verified: 2026-08-04
Verifier: Claude (gsd-verifier)
