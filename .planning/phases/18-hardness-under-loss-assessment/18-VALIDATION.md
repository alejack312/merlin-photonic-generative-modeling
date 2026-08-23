---
phase: 18-hardness-under-loss-assessment
slug: hardness-under-loss-assessment
status: validated-partial
nyquist_compliant: false
wave_0_complete: true
created: 2026-08-23
---

# Phase 18 — Validation Strategy

> Retrospective Nyquist validation reconstructed from the shipped plans, summaries, verification report, real datasets, and executable regression tests.

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | pytest |
| **Config file** | `pytest.ini` |
| **Quick run command** | `PCVL_PERSISTENT_PATH=.tmp-perceval venv/Scripts/python.exe -m pytest tests/test_loss_model.py tests/test_loss_model_weight2.py tests/test_baselines.py -q` |
| **Full suite command** | `PCVL_PERSISTENT_PATH=.tmp-perceval venv/Scripts/python.exe -m pytest -q` |
| **Executed focused result** | 56 passed in 23.73s; integration/CLI checks 25 passed in 52.87s |
| **Environment note** | `PCVL_PERSISTENT_PATH` is required here because the default Perceval log directory is not writable. |

## Sampling Rate

- After every task commit: run the focused Phase 18 tests above.
- After the phase: run the full pytest suite and the dataset/document checks recorded in `18-VERIFICATION.md`.
- Max observed focused feedback latency: 52.87 seconds for the integration/CLI subset.

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 18-01-01 | 01 | 1 | HARD-03 | manual/document | `18-VERIFICATION.md` source-read evidence | ✅ | ⚠️ manual-only |
| 18-01-02 | 01 | 1 | HARD-03/HARD-04 | manual/document | `18-VERIFICATION.md` citation review | ✅ | ⚠️ manual-only |
| 18-02-01 | 02 | 1 | HARD-01 | unit | `PCVL_PERSISTENT_PATH=.tmp-perceval venv/Scripts/python.exe -m pytest tests/test_loss_model.py -q` | ✅ | ✅ green |
| 18-02-02 | 02 | 1 | HARD-02 | integration | same focused command | ✅ | ✅ green |
| 18-03-01 | 03 | 1 | HARD-07 | unit/integration | `PCVL_PERSISTENT_PATH=.tmp-perceval venv/Scripts/python.exe -m pytest tests/test_loss_model_weight2.py -q` | ✅ | ✅ green |
| 18-03-02 | 03 | 1 | HARD-07 | integration | same focused command | ✅ | ✅ green |
| 18-04-01 | 04 | 1 | HARD-05 | unit | `PCVL_PERSISTENT_PATH=.tmp-perceval venv/Scripts/python.exe -m pytest tests/test_baselines.py -q` | ✅ | ✅ green |
| 18-04-02 | 04 | 1 | HARD-05 | unit | same focused command | ✅ | ✅ green |
| 18-05-01 | 05 | 2 | HARD-05/HARD-07 | integration | `PCVL_PERSISTENT_PATH=.tmp-perceval venv/Scripts/python.exe -m pytest tests/test_sweep.py -q` | ✅ | ✅ green |
| 18-05-02 | 05 | 2 | HARD-01/HARD-05/HARD-07 | integration | `PCVL_PERSISTENT_PATH=.tmp-perceval venv/Scripts/python.exe -m pytest tests/test_merlin_loss_model.py -q` | ✅ | ✅ green |
| 18-06-01 | 06 | 3 | HARD-01/HARD-05/HARD-07 | integration/data | `PCVL_PERSISTENT_PATH=.tmp-perceval venv/Scripts/python.exe -m pytest tests/test_merlin_loss_model.py -q` plus CSV checks in `18-VERIFICATION.md` | ✅ | ✅ green |
| 18-06-02 | 06 | 3 | HARD-01/HARD-05/HARD-07 | integration/data | same command plus real CSV row/value checks | ✅ | ✅ green |
| 18-07-01 | 07 | 4 | HARD-01/HARD-02/HARD-05/HARD-07 | manual/document | `hardness_analysis.py` and rendered plot/doc evidence | ✅ | ✅ green |
| 18-07-02 | 07 | 4 | HARD-05/HARD-07 | manual/document | canonical document review | ✅ | ✅ green |
| 18-08-01 | 08 | 5 | HARD-04 | manual/owner checkpoint | attempt-first transcript and loss-native positioning in `docs/hardness-under-loss-study.md` | ✅ | ⚠️ manual-only |
| 18-08-02 | 08 | 5 | HARD-06 | manual/document | closing scope statement review | ✅ | ⚠️ manual-only |

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Primary-source literature was read in full and formulas were extracted | HARD-03 | Reading/provenance is not established by a unit test | Confirm the two PDFs and cited formulas against `18-RESEARCH.md`, `18-01-SUMMARY.md`, and `18-VERIFICATION.md`. |
| Owner decides not to fabricate an η→ε depolarizing translation and accepts loss-native positioning | HARD-04 | Human conceptual/attempt-first checkpoint | Review the recorded checkpoint transcript and verify Aaronson–Brod/BMS positioning and explicit non-translation boundary in the canonical doc. |
| “What this does/doesn’t establish” scope boundary is honestly stated | HARD-06 | Documentation interpretation boundary | Read the final HARD-06 section and confirm tested scope, model differences, and excluded claims are explicit. |

## Validation Sign-Off

- [x] Plan/SUMMARY artifacts and existing verification evidence were audited.
- [x] Focused behavioral tests were executed; no implementation files were modified.
- [x] Integration/CLI subset was executed: 25 passed in 52.87s.
- [ ] All phase behaviors have automated verification (HARD-03/HARD-04/HARD-06 remain manual-only by nature).
- [x] No watch-mode flags.
- [ ] `nyquist_compliant: true` — not set because three human/documentary boundaries remain explicitly manual-only.

**Approval:** validated-partial 2026-08-23

## Validation Audit 2026-08-23

| Metric | Count |
|--------|-------|
| Requirements covered by executed automated tests/data checks | 4 (HARD-01, HARD-02, HARD-05, HARD-07) |
| Requirements manual-only | 3 (HARD-03, HARD-04, HARD-06) |
| Focused tests | 56 passed |
| Integration/CLI tests | 25 passed |
| Implementation bugs found | 0 |
