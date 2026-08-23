---
phase: 15
slug: arb-01-core-gate-de-risking-validation
status: partial
nyquist_compliant: false
wave_0_complete: true
created: 2026-08-23
---

# Phase 15 — Validation Strategy

> Retroactive Nyquist validation reconstructed from the four phase plans, summaries, and `15-VERIFICATION.md`.

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest (repository `pytest.ini`) |
| **Config file** | `pytest.ini` |
| **Quick run command** | `venv\Scripts\python.exe -m pytest tests/test_cp_gate_derisking.py tests/test_iqp_photonic_encoding.py -q` |
| **Full suite command** | `venv\Scripts\python.exe -m pytest -q` |
| **Estimated runtime** | ~2 minutes (Perceval simulations; verify live in the current environment) |

## Sampling Rate

- **After every task commit:** Run the focused pytest command above.
- **After every plan wave:** Run the full repository pytest command.
- **Before `$gsd-verify-work`:** Full suite must be green.
- **Max feedback latency:** 120 seconds.

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 15-01 | 01 | 1 | ARB-01 | — | CP(alpha) has the expected phase-only truth table at three non-special alpha values and the alpha=pi boundary; success probability is tabulated. | unit/smoke | `venv\Scripts\python.exe cp_gate_derisking.py`; `venv\Scripts\python.exe -m pytest tests/test_cp_gate_derisking.py -q` | ✅ | ✅ green (reported in `15-VERIFICATION.md`; not re-confirmed in this pass) |
| 15-02 | 02 | 2 | ARB-01, ARB-06 | convention adapter | The module's dual-rail convention produces `diag(1,1,1,e^(i*alpha))`, including sign-for-sign alpha=pi agreement with the CZ core. | unit | `venv\Scripts\python.exe -m pytest tests/test_iqp_photonic_encoding.py -q` | ✅ | ✅ green (reported in `15-VERIFICATION.md`; not re-confirmed in this pass) |
| 15-03 | 03 | 2 | ARB-02, ARB-04 | derivation/data consistency | The general-alpha identity (`alpha=4*theta`) and success-probability expression are written and compared with measured values. | document/manual | — | ✅ | ⚠️ manual-only: prose/algebra and the owner-attempt transcript require review |
| 15-04 | 04 | 3 | ARB-03, ARB-04, ARB-05, ARB-06 | pipeline wiring/post-selection | The full CP pipeline agrees with the exact reference below `1e-6`, agrees with heralded_cz at alpha=pi, and reports success probability as a function of alpha. | integration | `venv\Scripts\python.exe -m pytest tests/test_iqp_photonic_encoding.py -q` | ✅ | ✅ green (reported in `15-VERIFICATION.md`; not re-confirmed in this pass) |

## Wave 0 Requirements

Existing infrastructure covers all phase requirements. The phase already contains regression tests in `tests/test_cp_gate_derisking.py` and `tests/test_iqp_photonic_encoding.py`; no new fixtures or test stubs were added.

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| General-alpha operator identity and recorded owner-attempt transcript | ARB-02 | The requirement includes explanatory derivation and provenance of the attempt-first checkpoint, which is not meaningfully established by a structural string test. | Read `docs/iqp-photonic-encoding.md` ARB-01/ARB-02 section; check the step-by-step algebra, explicit `alpha=4*theta` relationship, boundary reduction, measured comparison, and transcript against `15-VERIFICATION.md`. |
| Descriptive CP-vs-heralded_cz comparison | ARB-05 | The requirement is documentation framing (mechanism distinction and no recommendation), not only executable behavior. | Read the comparison table in `docs/iqp-photonic-encoding.md`; confirm mechanism, resource cost, depth, and success probability are stated without recommendation language. |
| Current-environment rerun of focused simulations | ARB-01, ARB-03, ARB-04, ARB-06 | A focused pytest invocation was started during this reconstruction but did not produce output within the bounded run window and was stopped; the existing verification report records prior live passes. | Run the focused command from Test Infrastructure in an environment with Perceval simulation runtime available; require exit code 0 and inspect TVD/success-probability assertions. |

## Validation Sign-Off

- [x] All executable phase behaviors have existing automated tests and prior live verification evidence.
- [x] Sampling continuity: no three consecutive tasks without automated verification.
- [x] Wave 0 covers all missing references.
- [x] No watch-mode flags.
- [ ] Feedback latency < 120s in the current environment (focused command timed out without output).
- [ ] `nyquist_compliant: true` — not set because documentation behaviors and current rerun remain manual-only.

**Approval:** pending — reconstructed in text/manual-only mode on 2026-08-23.

## Validation Audit 2026-08-23

| Metric | Count |
|--------|-------|
| Gaps found | 3 |
| Resolved by existing automated evidence | 2 |
| Manual-only / current-environment caveats | 3 |
| New test files | 0 |

