---
phase: 20-technical-write-up
slug: technical-write-up
status: partial
nyquist_compliant: false
wave_0_complete: true
created: 2026-08-23
---

# Phase 20 — Validation Strategy

> Retrospective validation map for the completed documentation-synthesis phase.

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | PowerShell artifact/traceability checks; project pytest remains available for upstream numerical evidence |
| **Config file** | `pytest.ini` for the project suite; no phase-specific test config |
| **Quick run command** | `powershell -Command "$checks = @('docs/trainability-study.md','docs/hardness-under-loss-study.md','docs/iqp-photonic-encoding.md','docs/technical-findings.md','docs/julia-cross-check-study.md','docs/papers','results/phase17_curve_fit_summary.csv','results/phase171_train09_curve_fit_summary.csv','results/phase171_train10_curve_fit_summary.csv','results/phase18_weight1_loss_sweep.csv','results/phase16_alpha_sweep.csv'); $missing = $checks | Where-Object { -not (Test-Path $_) }; if ($missing) { throw ('Missing artifacts: ' + ($missing -join ', ')) }; $tf = Get-Content -Raw docs\\technical-findings.md; $required = @('trainability-study.md','hardness-under-loss-study.md','iqp-photonic-encoding.md','julia-cross-check-study.md','Traceability and consistency'); $absent = $required | Where-Object { $tf -notmatch [regex]::Escape($_) }; if ($absent) { throw ('Missing traceability markers: ' + ($absent -join ', ')) }; 'PASS'"` |
| **Full suite command** | `venv/Scripts/python.exe -m pytest -q` (upstream evidence regression; not phase-specific) |
| **Estimated runtime** | <1 second for the phase artifact check; ~seconds/minutes for full pytest |

## Sampling Rate

- **After every task commit:** Run the phase artifact/traceability check above.
- **After every plan wave:** Run the phase artifact/traceability check plus the full pytest suite when upstream numerical evidence is changed.
- **Before `$gsd-verify-work`:** Confirm all linked source documents, cited CSVs, and paper directory entries exist.
- **Max feedback latency:** <1 second for phase-specific checks.

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 20-01 | 01 | 1 | WRITE-02, WRITE-05 | T-20-01 | TRAIN write-up contains the owner transcript and all 11 baseline dispositions. | documentation/traceability | phase artifact check; inspect `docs/trainability-study.md` | ✅ | ✅ green |
| 20-02 | 02 | 1 | WRITE-02 | T-20-02 | HARD write-up contains all 11 baseline dispositions and the Herbst cross-reference. | documentation/traceability | phase artifact check; inspect `docs/hardness-under-loss-study.md` | ✅ | ✅ green |
| 20-03 | 03 | 1 | WRITE-02, WRITE-04 | T-20-03 | ARB section has scoped claims and explicitly addresses the named baselines. | documentation/traceability | phase artifact check; inspect `docs/iqp-photonic-encoding.md` | ✅ | ✅ green |
| 20-04 | 04 | 2 | WRITE-01, WRITE-03, WRITE-06 | T-20-04 | Synthesis links source docs, preserves cautious framing, and points numeric claims to traceability artifacts. | documentation/traceability | phase artifact check; inspect `docs/technical-findings.md` | ✅ | ✅ green |

## Wave 0 Requirements

Existing documentation and numerical-test infrastructure covers the phase requirements. No new application test fixture is appropriate for this documentation-only phase.

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Owner-authored TRAIN-07 interpretation is substantively correct and unaided. | WRITE-05 | Correctness of scientific interpretation cannot be established by link or presence checks. | Owner rereads the transcript in `docs/trainability-study.md` and confirms it reflects their own reasoning and the stated evidence. |
| Negative/inconclusive framing and Herbst cross-thread conclusions are scientifically justified. | WRITE-03 | The checks prove presence/traceability, not the truth of the interpretation. | Owner reviews the TRAIN/HARD source notes alongside cited results and confirms no claim is softened or overstated. |
| Markdown anchors render correctly in the target viewer. | WRITE-01, WRITE-02, WRITE-04 | Renderer behavior is environment-specific. | Open `docs/technical-findings.md` and follow each source/scope link in the repository viewer. |

## Validation Sign-Off

- [x] All tasks have an automated artifact/traceability check.
- [x] Existing numerical test infrastructure is identified; no phase-specific fixture is needed.
- [x] No watch-mode flags.
- [x] Phase-specific feedback latency is below one second.
- [ ] All phase behaviors have automated verification — owner interpretation and rendered-link checks remain manual.
- [ ] `nyquist_compliant: true` — not set because manual-only scientific interpretation remains.

**Approval:** partial — automated artifact check passed on 2026-08-23; owner review remains open.

## Validation Audit 2026-08-23

| Metric | Count |
|--------|-------|
| Gaps found | 3 manual-only boundaries |
| Resolved | 4 task-level artifact/traceability checks |
| Escalated | 0 |

