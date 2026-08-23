---
phase: 19
slug: independent-julia-cross-checks
status: validated-partial
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-23
---

# Phase 19 — Validation Strategy

Phase 19's behavioral checks are executable Julia cross-check programs. The
prior phase verification records live runs and numeric TVD results, but this
validation pass could not reproduce them because Julia is not runnable in the
current Windows environment (`julia.exe` resolves to an inaccessible
WindowsApps shim). The existing scripts and results are therefore recorded as
manual-only evidence, not claimed as fresh automated coverage.

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | Julia 1.10.11; Yao.jl 0.9.1; BosonSampling.jl 1.0.2; Python pytest 7.x for repository tests |
| **Config file** | `julia/Project.toml`; `pytest.ini` |
| **Quick run command** | `julia --project=julia julia/verify_qubit_iqp.jl` (blocked: Julia executable unavailable) |
| **Full suite command** | `julia --project=julia julia/verify_qubit_iqp.jl; julia --project=julia julia/verify_photonic_iqp_weight1.jl; julia --project=julia julia/verify_photonic_iqp_weight2.jl; julia --project=julia julia/verify_loss_model.jl` |
| **Estimated runtime** | ~15 seconds when Julia is installed and dependencies are available |

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Threat Ref | Secure Behavior | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|------------|-----------------|-----------|-------------------|-------------|--------|
| 19-01-01 | 01 | 1 | VERIFY-02/03/04 references | — | Python reference CSVs are generated from the real distribution functions and preserve residual/theta metadata | integration | `venv\\Scripts\\python.exe julia\\generate_reference.py` | ✅ | ❌ blocked by Perceval log permission |
| 19-01-02 | 01 | 1 | VERIFY-04 references | — | Fixed single theta draw and eta rows are recorded in CSV headers | integration | `venv\\Scripts\\python.exe julia\\generate_reference.py` | ✅ | ❌ blocked by Perceval log permission |
| 19-02-01 | 02 | 2 | VERIFY-02 | — | Yao independently reproduces qubit distributions and checks phase/bit ordering | integration | `julia --project=julia julia/verify_qubit_iqp.jl` | ✅ | ⚠️ prior live evidence only |
| 19-03-01 | 03 | 2 | VERIFY-03 | — | BosonSampling.jl independently reproduces weight-1 photonic distributions | integration | `julia --project=julia julia/verify_photonic_iqp_weight1.jl` | ✅ | ⚠️ prior live evidence only |
| 19-04-01 | 04 | 2 | VERIFY-03 | — | Literature-sourced Knill-CZ construction is independently cross-checked with herald accounting | integration | `julia --project=julia julia/verify_photonic_iqp_weight2.jl` | ✅ | ⚠️ prior live evidence only |
| 19-05-01 | 05 | 3 | VERIFY-04 | — | Native BosonSampling loss model is marginalized and compared at three eta values | integration | `julia --project=julia julia/verify_loss_model.jl` | ✅ | ⚠️ prior live evidence only |
| 19-06-01 | 06 | 3 | VERIFY-02/03/04 | — | Canonical write-up reports measured results and scope limits | documentation | inspect `docs/julia-cross-check-study.md` and phase results docs | ✅ | ✅ documented |

## Wave 0 Requirements

- [ ] Install/restore a runnable Julia 1.10.11 executable and project environment.
- [ ] Restore writable Perceval log location if rerunning `julia/generate_reference.py`.

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Yao qubit cross-check at n=2/n=3 | VERIFY-02 | Julia unavailable in this environment; prior verification reports live TVDs 2.26e-17 and 1.12e-16 | Run `julia --project=julia julia/verify_qubit_iqp.jl`; require exit 0, PASS checkpoints, and TVD ≤ 1e-6 |
| BosonSampling weight-1 cross-check | VERIFY-03 | Julia unavailable; prior verification reports live TVDs 2.36e-16 and 3.04e-16 | Run `julia --project=julia julia/verify_photonic_iqp_weight1.jl`; require exit 0 and both TVDs ≤ 1e-6 |
| BosonSampling weight-2 cross-check | VERIFY-03 | Julia unavailable; prior verification reports TVD 3.50e-15 and herald diff 5.55e-16 | Run `julia --project=julia julia/verify_photonic_iqp_weight2.jl`; require exit 0, GO, and both comparisons ≤ 1e-6 |
| BosonSampling native-loss cross-check | VERIFY-04 | Julia unavailable; prior verification reports weight-1 TVD 8e-18–2e-16 and mixed ≈1.75e-14 | Run `julia --project=julia julia/verify_loss_model.jl`; require all eta rows PASS and TVD ≤ 1e-6 |
| Regenerate Python references | VERIFY-02/03/04 | Current run blocked by `perceval.log` permission denied | Run `venv\\Scripts\\python.exe julia\\generate_reference.py` with a writable Perceval log directory; require all 11 CSVs and sane sums |

## Validation Sign-Off

- [ ] All tasks have freshly runnable automated verification
- [ ] Sampling continuity: no 3 consecutive tasks without automated verify
- [ ] Wave 0 covers all blocked runtime dependencies
- [x] No watch-mode flags
- [ ] Feedback latency < 30s in current environment
- [ ] `nyquist_compliant: true` set in frontmatter

**Approval:** pending — restore Julia runtime and rerun the four scripts.

## Validation Audit 2026-08-23

| Metric | Count |
|--------|-------|
| Gaps found | 5 |
| Resolved | 1 documented |
| Escalated/manual-only | 5 |

Observed current-run failures: all four Julia commands failed before script
execution because `C:\Users\cuqui\AppData\Local\Microsoft\WindowsApps\julia.exe`
was inaccessible; Python reference generation failed while Perceval attempted
to create `C:\Users\cuqui\AppData\Local\quandela\perceval-quandela\\logs\\perceval.log`
with permission denied.
