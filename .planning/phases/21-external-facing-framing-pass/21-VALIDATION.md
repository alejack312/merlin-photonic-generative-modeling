---
phase: 21
slug: external-facing-framing-pass
status: partial
nyquist_compliant: false
wave_0_complete: true
created: 2026-08-23
---

# Phase 21 — Validation Strategy

> Retroactive Nyquist validation reconstructed from the completed phase plans,
> summaries, and `21-VERIFICATION.md`. This phase is primarily an external
> content/framing change; deployment/render checks remain outside this repo's
> automated test infrastructure.

## Test Infrastructure

| Property | Value |
|----------|-------|
| **Framework** | PowerShell content/link checks; no phase-specific test framework |
| **Config file** | none |
| **Quick run command** | `powershell -Command "$r=Get-Content -Raw README.md; if($r.IndexOf('## v3.0: IQP Circuit Study') -le $r.IndexOf('## Process & AI Use') -or $r.IndexOf('## License') -le $r.IndexOf('## v3.0: IQP Circuit Study')){exit 1}; @('docs/technical-findings.md','docs/trainability-study.md','docs/hardness-under-loss-study.md','docs/iqp-photonic-encoding.md','docs/julia-cross-check-study.md') | %% { if(-not (Test-Path $_)){exit 1} }"` |
| **Full suite command** | `cd C:\Users\cuqui\projects\alejandro-jackson; npm run lint; npm run build` plus the README check above |
| **Observed runtime** | README/link checks completed in seconds; sibling-repo lint/build not rerun in this reconstruction |

## Sampling Rate

- After each documentation task: run the README section-order/link check.
- After the phase wave: run the sibling portfolio repo's lint and build, then perform a rendered/manual review of the case-study route.
- Before `$gsd-audit-milestone`: confirm the external page is reachable and the content numbers/verdicts still agree with the canonical docs.
- Max feedback latency: seconds for local checks; external build/render is environment-dependent.

## Per-Task Verification Map

| Task ID | Plan | Wave | Requirement | Test Type | Automated Command | File Exists | Status |
|---------|------|------|-------------|-----------|-------------------|-------------|--------|
| 21-01 | 01 | 1 | WRITE-07 case-study v3.0 framing, honest negative/inconclusive findings, and self-explanation evidence | content inspection | `Select-String`/PowerShell checks against `C:\Users\cuqui\projects\alejandro-jackson\src\pages\case-studies\merlin-quantum.tsx` | ✅ external file present | ⚠️ warning: static content checks pass, but sibling lint/build and rendered route were not rerun here |
| 21-02 | 02 | 1 | WRITE-07 README pitch and links | content/link smoke | README section-order/link check above | ✅ `README.md` and all five linked docs | ✅ green |

## Wave 0 Requirements

Existing documentation and repository files cover the phase. No new test file
was generated because the phase's local behavioral surface is markdown/content
presence and the portfolio page lives in a separate repository.

## Manual-Only Verifications

| Behavior | Requirement | Why Manual | Test Instructions |
|----------|-------------|------------|-------------------|
| Portfolio case-study renders at the production route and preserves existing v1.0 content | WRITE-07 | The page is in `alejandro-jackson`, outside this repo's test paths; route/render behavior requires that repo's dependencies and a browser or deployed site | In the sibling repo run `npm run lint` and `npm run build`; start/visit `/case-studies/merlin-quantum`; confirm the v3.0 sections, existing v1.0 sections, and responsive rendering. |
| External deployment is reachable and current | WRITE-07 | Deployment state is external and can drift independently of source files | Visit `https://alejandrojackson.dev/case-studies/merlin-quantum` and record HTTP/render evidence. |
| HARD anticoncentration wording is reconciled across README, canonical docs, and verification | WRITE-07 | This is a research-result interpretation/consistency gate, not a structural test | Compare the current README wording with `docs/technical-findings.md`, `docs/hardness-under-loss-study.md`, and `21-VERIFICATION.md`; resolve whether the measured result is decreasing or invariant before declaring the framing fully green. |

## Validation Sign-Off

- [x] PLAN and SUMMARY artifacts reviewed for both phase plans.
- [x] Existing `21-VERIFICATION.md` reviewed.
- [x] README section order and all five local documentation links checked live.
- [x] External case-study file inspected read-only; expected v3.0 sections and honest sigma/no-translation language are present.
- [ ] Sibling portfolio lint/build rerun in this pass.
- [ ] Production/rendered review completed.
- [ ] HARD anticoncentration wording reconciled across source artifacts.
- [ ] `nyquist_compliant: true` — not set because external build/render and a result-wording consistency gate remain open.

**Approval:** pending external build/render review and HARD wording reconciliation

## Validation Audit 2026-08-23

| Metric | Count |
|--------|-------|
| Tasks mapped | 2 |
| Automated/content checks green | 1 |
| Static external-file checks passed with caveat | 1 |
| Manual-only boundaries | 3 |
| New test files | 0 |
| Implementation files modified | 0 |

