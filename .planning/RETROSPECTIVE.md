# Project Retrospective

*A living document updated after each milestone. Lessons feed forward into future planning.*

*Started at v3.1's close (2026-09-04) — v1.0 through v3.0 shipped before this document existed and are not reconstructed here retroactively; each has its own `.planning/milestones/v{X}-MILESTONE-AUDIT.md`.*

## Milestone: v3.1 — Correction

**Shipped:** 2026-09-04
**Phases:** 1 (Phase 24) | **Plans:** 0 formal (executed interactively) + 2 `/gsd-quick` tasks | **Sessions:** multiple, spanning 2026-09-03 to 2026-09-04

### What Was Built
- Owner-derived null-result regression test suite (`tests/v3_correction/test_null_results.py`) proving both v3.0 co-lead findings were pipeline artifacts, verified to floating-point precision against the shipped CSVs
- Dated, additive corrections in all 7 required documents plus the public case-study page — originals kept, never deleted
- A throughput-vs-`n,k` table replacing TVD-as-hardness as the hardness section's leading figure
- REFRAME-02: `partial_loss` breakdown returned by both loss-model functions instead of silently discarded, all callers updated
- A standing `CLAUDE.md` null-result gate + learning note
- An independent Codex adversarial review of the correction itself (`24-REVIEW.md`), not just the original findings

### What Worked
- Running the correction interactively (direct commits + `/gsd-quick`) instead of forcing it through full plan/execute ceremony matched the actual shape of the work (diagnosis-and-write, not new feature construction) and shipped in 2 days
- Aiming a second adversarial review at the correction's own prose (not just the original v3.0 claims) caught 9 more real overclaims, including one in the correction's own headline sentence — the same failure class the milestone existed to fix, now caught before it shipped a second time
- The milestone audit's Option-C fallback (deriving must-haves from ROADMAP.md + REQUIREMENTS.md directly, since no PLAN.md/SUMMARY.md existed for this phase) worked cleanly — verification rigor didn't depend on the formal artifact trail existing

### What Was Inefficient
- `24-VERIFICATION.md` was written mid-correction (2026-09-03) and never re-run after REFRAME-01/REFRAME-02/REVIEW-01 actually landed — it sat stale, reporting `gaps_found` on three items that were later completed, until `/gsd-audit-milestone` re-checked it a day later. A verification snapshot that isn't re-run after further work lands is worse than no snapshot, since it looks authoritative while being wrong.
- Two real doc-drift items (a superseded tolerance number, three broken cross-doc anchors) slipped through the correction's own review passes and were only caught by the milestone audit's integration check — a reminder that "the correction is done" and "the correction is internally consistent" are different claims.

### Patterns Established
- **Aim adversarial review at your own correction, not just the original claim.** A correction is new prose with new claims; it needs the same scrutiny the thing it's correcting got.
- **A milestone audit should re-verify stale VERIFICATION.md gaps against current files before reporting them**, not repeat them — a `*-VERIFICATION.md` written mid-phase is a snapshot, not a live status.
- **Owner-gated requirements (self-explanation, external communication) stay open rather than being marked complete on Claude's behalf** — NULL-01 and COMM-01 were both tracked honestly as partial/pending until the owner actually did the gated step, and closing the milestone with one still open (NULL-01) was an explicit, recorded owner choice, not a quiet drop.

### Key Lessons
1. A null-result gate (write the closed-form prediction for "circuit contributes nothing" before running a sweep) is cheap insurance against exactly the failure mode that cost this milestone's existence — now standing policy in `CLAUDE.md`.
2. Verification/audit documents need a re-run trigger, not just a creation trigger — otherwise they decay into misleading artifacts the moment more work lands after they're written.
3. Interactive execution (skipping gsd-executor's plan/summary ceremony) is a legitimate choice for time-sensitive, diagnosis-shaped work, but it means milestone audits must fall back to ROADMAP/REQUIREMENTS-derived must-haves rather than SUMMARY frontmatter — worth choosing deliberately, not defaulting into by accident.

### Cost Observations
- Model mix: primarily sonnet-5 for the correction work and audit; one gsd-integration-checker subagent run (sonnet-5)
- Sessions: work spanned at least 3 distinct sessions/worktrees (`serene-sanderson-728202` for the correction, `amazing-kalam-773394` for the audit and close)
- Notable: the milestone audit + integration check (a few hours of agent time) found and fixed 2 real cross-document drift issues that had already shipped past the correction's own review — cheap relative to a resume/interview conversation surfacing a citation that points at the wrong section or a stale number

---

## Cross-Milestone Trends

*Only one milestone (v3.1) is recorded here so far — this section will start showing real trends once v4.0 or a later milestone closes.*

### Process Evolution

| Milestone | Sessions | Phases | Key Change |
|-----------|----------|--------|------------|
| v3.1 | 3+ | 1 | First milestone executed interactively (no `gsd-executor`/PLAN.md); first milestone audit to need a stale-VERIFICATION.md re-check; first `RETROSPECTIVE.md` entry |

### Cumulative Quality

| Milestone | Tests | Coverage | Zero-Dep Additions |
|-----------|-------|----------|---------------------|
| v3.1 | 451 (per quick-task-ukn's reported count) | not tracked | 0 |

### Top Lessons (Verified Across Milestones)

1. *(Pending — needs a second milestone's retrospective to confirm any lesson generalizes rather than being v3.1-specific.)*
