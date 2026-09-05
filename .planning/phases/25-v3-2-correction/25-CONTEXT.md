# Phase 25: v3.2 Correction (Audit Response) — Context

**Status:** Mechanical track substantially done 2026-09-05 (CORR-08, 09, 11, 12, 16, 17, GATE-02, GATE-03 shipped; CORR-10, 13, 14, 15 deferred — see `.planning/REQUIREMENTS.md` for per-item disposition and evidence). Conceptual track (CONCEPT-01..03) is owner-only and not started.

## Why this phase exists

An independent audit (GPT-6 Astra, `docs/audits/2026-09-05-codebase-audit.md`, two runnable probes in the same directory) reviewed the post-v3.1 codebase and found:

- Two P1 findings that the v3.1 correction itself, or a claim that survived it, overreached (CONCEPT-01, CONCEPT-02).
- One P1 finding that a retained "negative result" (TRAIN-10) compares mismatched statistics (CONCEPT-03).
- One more P1: a real classifier logic bug (`fit_verdict_to_plateau_label` only checks `b > 0`, not whether the fitted curve actually decays) — confirmed by direct code read against the function's own docstring, independent of the audit's probe output.
- Several P2 code-level defects (chunked-sweep double-counting, Julia scripts exiting 0 on disagreement, the null-result gate silently skipping missing data, `fit_and_compare` contradicting its own documented contract on partial convergence, incorrect dual-rail equivalence math, an inaccurate MBQC literature summary, an unenforced search timeout).

I (Claude) independently re-verified CONCEPT-01, CONCEPT-02, and the classifier/fit_and_compare bugs by reading the actual source directly (not just trusting the audit's prose) before treating any of this as real. Detail in the session transcript and `docs/audits/2026-09-05-codebase-audit.md`.

## Decision log

- **D-01:** Per `CLAUDE.md`'s "do not shortcut — interpreting benchmark/metric results" rule, Claude does not draft the corrected scientific claims for CONCEPT-01/02/03. Claude may point at the exact code, the exact q(theta) definitions, and the exact factorization math, and answer questions — the owner writes the sentence.
- **D-02:** The mechanical track (CORR-08..17, GATE-02/03) does not depend on how CONCEPT-01..03 resolve — a wrong classifier is wrong regardless of what the mixed-scope framing ends up being — so it proceeds independently rather than being gated behind the owner's review, unlike v3.1's NULL-01 (which structurally had to come first there).
- **D-03:** This phase is numbered 25 on `master`. The open, unmerged v4.0 plan (PR #3, `claude/merlin-photonic-iqp-audit-e8144c`) also claims phases 25-31. Whichever merges second will need its phase numbers shifted — noted here rather than silently resolved, since it affects both branches' `ROADMAP.md`.
- **D-04:** No full sweep, training run, Julia verifier, or Forge solver was rerun as part of this phase (matches the audit's own stated coverage limit). CORR-08..12 are fixed and regression-tested against synthetic/adversarial cases, not by re-deriving every historical CSV.

## What's owner-only vs. Claude-executable, restated plainly

Owner-only (Claude does not write these):
- CONCEPT-01: the corrected sentence(s) in `docs/trainability-study.md` distinguishing "classically reproducible" from "no landscape effect."
- CONCEPT-02: the reclassification (or justified retention) of `mixed` scope's hardness-candidate status in `docs/hardness-under-loss-study.md`.
- CONCEPT-03: TRAIN-10's disposition (retract / narrow / defend-with-correction).

Claude-executable now:
- CORR-08 through CORR-17, GATE-02, GATE-03 — all code-level bug fixes, test additions, and CLAUDE.md rule additions that don't require deciding what the mixed-scope or trainability-landscape claims should say.

## Suggested plan outline

- **25-00 (owner):** Resolve CONCEPT-01..03. No fixed order requirement; independent of the mechanical track below.
- **25-01 (Claude):** CORR-08, CORR-09 (classifier + fit_and_compare bugs) with adversarial regression tests.
- **25-02 (Claude):** CORR-12 (null-result gate hardening).
- **25-03 (Claude):** CORR-10 (chunk-overlap validation), CORR-11 (Julia exit codes).
- **25-04 (Claude):** CORR-13..17 (Should items) + GATE-02/03.
- **25-05:** Once CONCEPT-01..03 land, mirror them into `docs/technical-findings.md`/`README.md`/the case-study page per this project's standing correction convention (additive, dated, original tables kept).
