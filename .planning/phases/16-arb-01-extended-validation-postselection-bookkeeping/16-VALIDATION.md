---
phase: 16
slug: arb-01-extended-validation-postselection-bookkeeping
status: partial
nyquist_compliant: false
wave_0_complete: true
created: 2026-08-23
---

# Phase 16 — Validation Strategy

> Reconstructed validation record from the completed phase artifacts and live
> execution on 2026-08-23.

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest 9.1.1, Python 3.12.1; Forge 5.2 via Racket |
| **Config file** | `pytest.ini` |
| **Quick run command** | `$env:PCVL_PERSISTENT_PATH='.pcvl-test-data'; .\\venv\\Scripts\\python.exe -m pytest tests/test_iqp_photonic_encoding.py -v -k test_cp_composability_mixed_generators_n3` |
| **Full suite command** | `$env:PCVL_PERSISTENT_PATH='.pcvl-test-data'; .\\venv\\Scripts\\python.exe -m pytest tests/ -q` |
| **Additional commands** | `$env:PCVL_PERSISTENT_PATH='.pcvl-test-data'; .\\venv\\Scripts\\python.exe cp_alpha_sweep.py`; `racket forge/ancilla_mapping.frg` |
| **Observed runtime** | Focused pytest 20.41s; sweep 30.0s; Forge 5.9s; full suite 88.83s |

## Sampling Rate

- After each implementation task: run the focused pytest, sweep, or Forge command above.
- After the phase wave: run the full suite command.
- Before `$gsd-verify-work`: all listed commands must be green.
- Max observed feedback latency: 88.83s for the full suite.

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 16-01-01 | 01 | 1 | ARB-07 | mixed-generator composition | CP(alpha) composes with weight-1 generators and matches the exact reference at n=3 for three non-trivial alphas | integration | `... pytest tests/test_iqp_photonic_encoding.py -v -k test_cp_composability_mixed_generators_n3` | ✅ `tests/test_iqp_photonic_encoding.py` | ✅ green (3 passed, 61 deselected) |
| 16-01-02 | 01 | 1 | ARB-07 | regression | Existing behavior remains green after the new parametrized cases | integration | `... pytest tests/ -q` | ✅ existing suite | ✅ green (296 passed) |
| 16-02-01 | 02 | 1 | ARB-08 | alpha coverage / closed form | All 16 alpha points in [0, 2pi) match `1/sigma_max(alpha)^4` within 1e-6 and artifacts are written | integration | `... .\\venv\\Scripts\\python.exe cp_alpha_sweep.py` | ✅ `cp_alpha_sweep.py`, CSV, PNG | ✅ green (16/16 matched; CSV and PNG saved) |
| 16-02-02 | 02 | 1 | ARB-08 | documentation traceability | Sweep subsection identifies the 16-point assertion and links both output artifacts | inspection | Read `docs/iqp-photonic-encoding.md` and verify links/content | ✅ docs present | ✅ green (documented in 16-02-SUMMARY/VERIFICATION) |
| 16-03-01 | 03 | 2 | ARB-09 | attempt-first design gate | Owner explains the Forge injectivity predicate and sat/unsat purpose before model finalization | human gate | Owner explanation checkpoint | N/A | ⚠️ manual-only |
| 16-03-02 | 03 | 2 | ARB-09 | mapping alias/collision | Mapping model is non-vacuous and has no counterexample through the bounded n range | integration | `racket forge/ancilla_mapping.frg` | ✅ `forge/ancilla_mapping.frg` | ✅ green (`nonVacuous` and `noCounterexample` passed) |
| 16-03-03 | 03 | 2 | ARB-09 | evidence/document consistency | Forge result and completed Phase 16 scope are recorded in the summary and canonical docs | inspection | Read `results/phase16_forge_summary.md` and the Forge subsection in `docs/iqp-photonic-encoding.md` | ✅ docs/results present | ✅ green (documented in 16-03-VERIFICATION) |

## Wave 0 Requirements

Existing pytest and Forge infrastructure covers all executable phase requirements. No stubs or dependency installation were needed.

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Owner's attempt-first Forge predicate design and explanation | ARB-09 | This is an owner-understanding checkpoint, not an observable runtime behavior | Ask the owner to explain valid `(n,i,j)`, pairwise/non-aliasing mapping constraints, and why both a satisfiable non-vacuity check and unsatisfiable counterexample check are required. Record approval in the phase verification notes. |

## Validation Sign-Off

- [x] All executable tasks have automated verification.
- [x] Sampling continuity is maintained across both waves.
- [x] Wave 0 dependencies are already present.
- [x] No watch-mode flags are used.
- [x] Focused pytest, alpha sweep, Forge model, and full suite were run live on 2026-08-23.
- [ ] `nyquist_compliant: true` — not set because the owner-understanding gate remains manual-only.

**Approval:** pending owner checkpoint

## Validation Audit 2026-08-23

| Metric | Count |
|--------|-------|
| Requirements/tasks checked | 7 |
| Automated green | 6 |
| Manual-only | 1 |
| Blockers | 0 |
