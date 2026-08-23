---
phase: 14
slug: julia-toolchain-spike
status: partial
nyquist_compliant: false
wave_0_complete: false
created: 2026-08-23
---

# Phase 14 — Validation Strategy

> Retroactive Nyquist validation reconstructed from the completed phase artifacts.

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | None; standalone Julia scripts with `@assert` checks |
| **Config file** | none |
| **Quick run command** | `julia --version; juliaup status; julia --project=julia julia/hello_yao.jl; julia --project=julia julia/hello_bosonsampling.jl` |
| **Full suite command** | same as quick run; no project-wide Julia test runner exists |
| **Estimated runtime** | seconds after package precompilation; package setup is substantially longer |

## Sampling Rate

- **After every task commit:** run the two hello-world scripts and confirm their analytical `@assert`s.
- **After every plan wave:** run the full command above and confirm the LTS channel and both package banners.
- **Before `$gsd-verify-work`:** rerun both scripts from the project-scoped Julia environment.
- **Max feedback latency:** ~60 seconds after precompilation.

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 14-01-01 | 01 | 1 | Julia 1.10 LTS toolchain is callable and default | smoke | `julia --version; juliaup status` | ❌ W0 | ⚠️ manual-only |
| 14-01-02 | 01 | 1 | Yao Bell-state output matches analytical probabilities | integration | `julia --project=julia julia/hello_yao.jl` | ❌ W0 | ⚠️ manual-only |
| 14-01-03 | 01 | 1 | BosonSampling beamsplitter output matches analytical probabilities | integration | `julia --project=julia julia/hello_bosonsampling.jl` | ❌ W0 | ⚠️ manual-only |
| 14-01-03 | 01 | 1 | Consistent full-go verdict is recorded in results and STATE | documentation review | `rg -n "FULL GO|full go" results/phase14_julia_toolchain_summary.md .planning/STATE.md` | ❌ W0 | ⚠️ manual-only |

## Wave 0 Requirements

- [ ] No new test file was generated. The phase's existing Julia scripts are executable behavioral checks, but they are not integrated into the repository's pytest suite or a dedicated automated command.

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Julia toolchain and `juliaup` default channel | Phase 14 toolchain truth | Julia is an external system toolchain and is unavailable to the repository's pytest runner; current shell could not start the WindowsApps shims. | In a fresh shell run `julia --version` and `juliaup status`; confirm Julia 1.10.11 LTS is marked default. |
| Yao Bell-state circuit | Phase 14 Yao truth | Existing script is an assertion-backed executable, but no test-file/CI integration exists. Prior verification reports a live exit-0 run with `[0.5, 0.0, 0.0, 0.5]`. | Run `julia --project=julia julia/hello_yao.jl`; require Julia/Yao banners, four passing assertions, and the analytical probabilities. |
| BosonSampling beamsplitter circuit | Phase 14 BosonSampling truth | Existing script is an assertion-backed executable, but no test-file/CI integration exists. Prior verification reports a live exit-0 run with transmitted/reflected probabilities of 0.5/0.5. | Run `julia --project=julia julia/hello_bosonsampling.jl`; require Julia/BosonSampling banners, two passing assertions, and 0.5/0.5. |
| Cross-recorded verdict | Phase 14 verdict artifact | Text consistency is a documentation check, not a repository test. | Confirm both `results/phase14_julia_toolchain_summary.md` and `.planning/STATE.md` state FULL GO. |

## Validation Sign-Off

- [x] PLAN, SUMMARY, and VERIFICATION artifacts reviewed.
- [x] Existing behavioral commands and evidence mapped.
- [x] Missing dedicated test integration recorded as manual-only.
- [ ] All phase behaviors have repository-integrated automated verification.
- [ ] `nyquist_compliant: true` set in frontmatter.

**Approval:** pending — prior verification evidence is strong, but a fresh run was blocked in this shell because `julia.exe` and `juliaup.exe` could not be started.

## Validation Audit 2026-08-23

| Metric | Count |
|--------|-------|
| Gaps found | 4 |
| Resolved with new tests | 0 |
| Marked manual-only | 4 |
| Environment blockers | 1 |

