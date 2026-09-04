---
phase: 24-v3-1-correction
verified: 2026-09-03T00:00:00Z
status: gaps_found
score: 5/10 must-haves verified
overrides_applied: 0
note: >
  No PLAN.md/SUMMARY.md exist for this phase (executed interactively, not via
  gsd-executor). Must-haves below are derived from ROADMAP.md's 6 numbered
  success criteria plus REQUIREMENTS.md's Must-have requirements (NULL-01/02,
  CORR-01..07, REFRAME-01/02, GATE-01, REVIEW-01, COMM-01), per this
  verifier's Option-C fallback procedure.
gaps:
  - truth: "REVIEW-01: independent Codex review of corrected docs run, findings dispositioned in 24-REVIEW.md"
    status: failed
    reason: "No 24-REVIEW.md exists anywhere in the repo (only the unrelated 22-REVIEW.md from Phase 22). No evidence in git log, STATE.md, or PROJECT.md that a Codex review was run against the corrected text with the null-result prompt."
    artifacts:
      - path: ".planning/phases/24-v3-1-correction/24-REVIEW.md"
        issue: "File does not exist"
    missing:
      - "Run the Codex (gpt-5.5) review with the prompt 'for each stated finding, write the null result and check whether the finding differs from it' against the corrected docs, and write 24-REVIEW.md with each finding's disposition."
  - truth: "COMM-01: correction note to Vincent Espitalier drafted; send/hold decision recorded"
    status: failed
    reason: "No draft note found anywhere in the repo (searched all .md files for 'Vincent'; only the pre-existing, unrelated v1.0 technical-note reference in STATE.md/PROJECT.md turns up). 24-CONTEXT.md's decision log explicitly still reads 'COMM-01 send/hold: pending' — the decision was never made and the draft was never written."
    artifacts:
      - path: ".planning/phases/24-v3-1-correction/24-CONTEXT.md"
        issue: "Decision log line 36: 'COMM-01 send/hold: *pending*' — unresolved"
    missing:
      - "Owner drafts the 3-5 sentence correction note (what was wrong, what each result actually shows, link to corrected repo)."
      - "Send/hold decision recorded in 24-CONTEXT.md's decision log."
  - truth: "REFRAME-01: a short table or plot of throughput vs n and k, computed from the closed form, replaces the TVD plots as the figure the hardness section leads with"
    status: failed
    reason: "The throughput closed form eta^(n+2k)*(2/27)^k is stated correctly in prose inside the 2026-09-03 correction section (docs/hardness-under-loss-study.md line 36), which does satisfy the looser wording of ROADMAP success criterion #3 ('leads with the throughput closed form'). But no table or plot of throughput vs n/k exists anywhere in the document, and the TVD-vs-eta plots were only retitled ('pipeline check') — they were not replaced as the section's leading figure, as REFRAME-01's fuller requirement text specifies. Grepped the full document structure and found no throughput table/figure."
    artifacts:
      - path: "docs/hardness-under-loss-study.md"
        issue: "No throughput-vs-n,k table or plot; TVD plots remain the section's only figures, retitled but not replaced"
    missing:
      - "A table or plot of throughput = eta^(n+2k)*(2/27)^k vs n and k, placed as the section's leading figure."
  - truth: "REFRAME-02 (Should): photonic_iqp_distribution_lossy / photonic_weight2_iqp_distribution_lossy additionally return the non-post-selected outcome distribution as separate keys, with a mass-consistency test"
    status: failed
    reason: "Read src/merlin_iqp/hardness/loss_model.py and loss_model_weight2.py directly. Both functions are unchanged from their pre-Phase-24 form: out-of-subspace/partial-loss outcomes are still collapsed into a single 'residual' scalar (fock_to_bitstring returning None -> residual += p), never split into per-pattern keys. Neither file appears in the Phase 24 commit's changed-file list (git show --stat 0658ab6). This is marked '(Should)' in REQUIREMENTS.md, not a Must, but it is unaddressed, not partially addressed."
    artifacts:
      - path: "src/merlin_iqp/hardness/loss_model.py"
        issue: "residual is still a single float, not per-pattern keys (lines 64-74)"
      - path: "src/merlin_iqp/hardness/loss_model_weight2.py"
        issue: "residual is still a single float, not per-pattern keys (lines 164-183)"
    missing:
      - "Return non-post-selected outcomes as their own keys instead of collapsing into residual."
      - "A test asserting total mass (in-subspace + non-post-selected) is global_perf-consistent."
  - truth: "NULL-01: owner fills both null-result formulas and can state in one sentence why each has that form (the phase's self-explanation checkpoint)"
    status: partial
    reason: "The weight-1 formula (TVD = 0.5*(1-eta^n), and the TRAIN ratio model) is confirmed owner-derived and self-explained per 24-CONTEXT.md's decision log ('derived by the owner unaided through a guided Socratic process and is fully self-explained'). The mixed-scope formula's h(eta) polynomial, however, was produced by a parallel Fable 5.1 session, not the owner and not Claude in this session -- disclosed honestly in both the test docstring and 24-CONTEXT.md's decision log, and the docstring itself still contains a bracketed placeholder: '[owner: replace this line with your own sentence once you've walked through _herald_success_rate above -- deferred per the 2026-09-03 ship-first decision.]' The same placeholder appears in owner_train_null_ratio's docstring. This is an explicitly disclosed, tracked deviation (not a hidden one) -- the project's own decision log names it a 'Follow-up owed' -- but it means NULL-01's literal completion bar ('the owner can say in one sentence why it has that form') is not yet met for the mixed-scope formula in either function."
    artifacts:
      - path: "tests/v3_correction/test_null_results.py"
        issue: "owner_hard_null_tvd and owner_train_null_ratio docstrings both contain an unfilled '[owner: replace this line...]' placeholder for the mixed-scope reasoning"
    missing:
      - "Owner walks through why h(eta) = (2/27)eta^4 + (8/27)eta^3(1-eta) + (10/27)eta^2(1-eta)^2 has that form, and replaces the placeholder sentence in both docstrings."
deferred: []
human_verification: []
---

# Phase 24: v3.1 Correction Verification Report

**Phase Goal:** Correct the public record after the 2026-09-03 external audit established that v3.0's trainability "exponential decay" and hardness-under-loss TVD/alpha-invariance findings are pipeline artifacts, not circuit properties — via owner-derived null-result regression tests, dated additive corrections in every affected document, a throughput reframing of the hardness result, a standing CLAUDE.md null-result gate, an independent Codex review, and a drafted (not necessarily sent) correction note to Vincent Espitalier.

**Verified:** 2026-09-03
**Status:** gaps_found
**Re-verification:** No — initial verification (no prior VERIFICATION.md existed)
**Execution mode:** Interactive session, no PLAN.md/SUMMARY.md/gsd-executor. Must-haves derived from ROADMAP.md's 6 success criteria + REQUIREMENTS.md's Must-have list (Step 2 Option C fallback).

## Goal Achievement

### Observable Truths (ROADMAP Success Criteria + REQUIREMENTS Musts)

| # | Truth | Status | Evidence |
|---|-------|--------|----------|
| 1 | `python -m pytest -q` green, including promoted null-result tests over every shipped HARD row and sigma<=0.1 TRAIN row | ✓ VERIFIED | `python -m pytest -q` (via `venv/Scripts/python.exe`): **425 passed**, 0 failed, 0 skipped, 102.78s. `pytest tests/v3_correction -q`: 129 passed, 0 skipped (`-rs` confirms zero skip lines) — matches NULL-02's coverage requirement (4 HARD CSVs = 112 rows-minus-headers worth of parametrized cases + 2 TRAIN CSVs' sigma<=0.1 uniform-init ratio cases + 3 kernel-identity sanity tests). |
| 2 | Every affected document (trainability-study, hardness-under-loss-study, technical-findings, README, iqp-baseline Rudolph row, lit-scoping, Post_Sept1 plan, case-study page) carries a dated, additive, section-leading correction | ✓ VERIFIED | All 8 confirmed by direct read/grep for "2026-09-03"/"Correction": `docs/trainability-study.md` (2 corrections, lines 31, 66, 107, 329, 346 — leads Results and the Honest-max-n and cross-reference sections), `docs/hardness-under-loss-study.md` (leads at line 22, additional corrections at 136, 334), `docs/technical-findings.md` (line 5, leads), `README.md` (line 27, leads the v3.0 section), `docs/iqp-lit-scoping.md` (addendum, line 106), `Post_Sept1_IQP_Photonic_Plan.md` (line 21), and the separate case-study repo's `merlin-quantum.tsx` (4 dated correction call-outs, lines 737-909, committed as `67d73dc`). The "iqp-baseline Rudolph row" item resolves via `docs/trainability-study.md`'s literature table (line 329), not a direct edit to `docs/iqp-baseline.md` itself — `docs/iqp-baseline.md` has no 2026-09-03 edit, but CORR-01..07 never names it as a required edit target, so this is not scored as a gap. Original tables/verdicts are confirmed still present (not deleted) in every file checked — additive convention held. |
| 3 | Hardness section leads with the throughput closed form `eta^(n+2k)*(2/27)^k`; TVD plots retitled as a pipeline check | ⚠️ PARTIAL | The closed form is stated correctly in prose inside the leading Correction section (`docs/hardness-under-loss-study.md` line 36), and the TVD results header is retitled "pipeline check, see the 2026-09-03 correction above" (line 79) — the roadmap SC's literal wording is met. REFRAME-01's fuller spec (a table/plot of throughput vs n,k as the section's leading figure, replacing the TVD plots) is NOT met — grepped the full document structure; no such table/figure exists anywhere. See gap in frontmatter. |
| 4 | `CLAUDE.md` null-result gate present; `.claude/learnings/2026-09-03-null-result-gate-before-sweeps.md` exists | ✓ VERIFIED | `CLAUDE.md` lines 21, 63-65: "## Null-result gate (added 2026-09-03)" with the full rule text and a pointer to the learning note. `.claude/learnings/2026-09-03-null-result-gate-before-sweeps.md` exists, read in full — states the problem type, both TRAIN/HARD instances, the rule, decision rules, tells, verification pointer, and scope. Well-formed. |
| 5 | `24-REVIEW.md` records the Codex null-result review and disposition of each finding | ✗ FAILED | No `24-REVIEW.md` exists in `.planning/phases/24-v3-1-correction/` (only `24-CONTEXT.md` is present). No evidence anywhere (git log, STATE.md, PROJECT.md) that an independent Codex review was run against the corrected text. REVIEW-01 is unaddressed. |
| 6 | Vincent note drafted by the owner; send/hold decision logged in `24-CONTEXT.md` | ✗ FAILED | Searched every `.md` file in the repo for "Vincent" — no draft correction note found (only the pre-existing, unrelated v1.0 technical-note reference). `24-CONTEXT.md`'s own decision log (line 36) reads "COMM-01 send/hold: *pending*" — both the draft and the decision are outstanding. |

**Score:** 3.5/6 roadmap success criteria fully verified (SC1, SC2, SC4 clean; SC3 partial; SC5, SC6 failed). Counting REQUIREMENTS.md-level Must-haves separately below for the frontmatter score.

### Additional Must-Have Requirements (REQUIREMENTS.md, not folded into the 6 numbered SCs)

| # | Requirement | Status | Evidence |
|---|-------------|--------|----------|
| 7 | NULL-01: owner derives both formulas by red/green experiment and can self-explain each in one sentence | ⚠️ PARTIAL | Weight-1 formulas (both HARD and TRAIN) fully owner-derived and self-explained per `24-CONTEXT.md`'s decision log. The mixed-scope `h(eta)` formula was sourced from a parallel Fable 5.1 session, not the owner — disclosed honestly in both the test docstring and the decision log ("NOT yet walked through with the owner... Follow-up owed"), but both `owner_hard_null_tvd` and `owner_train_null_ratio` docstrings still carry an unfilled `[owner: replace this line...]` placeholder. NULL-01's literal completion bar is not fully met. |
| 8 | REFRAME-02 (Should): lossy distribution functions return non-post-selected outcomes as separate keys, with a mass-consistency test | ✗ FAILED (Should-have) | Read `src/merlin_iqp/hardness/loss_model.py` and `loss_model_weight2.py` directly — both unchanged; `residual` is still a single collapsed float, no per-pattern keys, no mass-consistency test. Neither file is in Phase 24's commit diff. Lower severity since REQUIREMENTS.md marks this "(Should)", but it is fully unaddressed, not partially done. |
| 9 | CORR-07: case-study page corrected; `npm run lint` and `npm run build` green | ✓ VERIFIED | `C:\Users\cuqui\projects\alejandro-jackson`: 4 dated 2026-09-03 correction call-outs present in `merlin-quantum.tsx` (read in full, lines 700-909), additive (pre-correction text retained and explicitly labeled as such). Committed as `67d73dc "fix(case-studies): correct MerLin v3.0 trainability/hardness findings"`. `npm run lint`: 0 errors (pre-existing warnings only, in files this phase didn't touch). `npm run build`: exit code 0, all 42 pages generated including `/case-studies/merlin-quantum`. Local branch is 1 commit ahead of `origin/main` — not pushed, matching the requirement that push is a separate explicit owner action. |
| 10 | Uncommitted work check | ⚠️ WARNING | `git status` at HEAD `0658ab6` shows 3 files with **uncommitted** working-tree changes: `README.md`, `docs/iqp-lit-scoping.md`, `docs/trainability-study.md`. These specifically contain: the KLM/Hoban/Oh/Oszmaniec-Brod/Xie/Salavrakos literature addendum in `iqp-lit-scoping.md`; the trainability-study.md "Honest max-n statement" correction (see Independent Assessment below); and a README four-milestone rewrite. None of this is reflected in the phase's single commit (`0658ab6`), and Finish Criteria #2 requires "CORR-01..07 checked off with commit SHAs" — that bookkeeping cannot exist yet for uncommitted work. Risk: this work could be lost or left permanently uncommitted if not explicitly finished. |

### Requirements Coverage

| Requirement | Status | Evidence |
|---|---|---|
| NULL-01 | ⚠️ Partial | Weight-1 done and self-explained; mixed-scope formula sourced externally, self-explanation deferred (disclosed) |
| NULL-02 | ✓ Satisfied | 129/129 tests green, 0 skips, full CSV coverage confirmed |
| CORR-01 | ✓ Satisfied | trainability-study.md correction, additive, dated, leads Results |
| CORR-02 | ✓ Satisfied | hardness-under-loss-study.md correction, additive, dated, leads |
| CORR-03 | ✓ Satisfied | technical-findings.md mirrors both, dated |
| CORR-04 | ✓ Satisfied | README v3.0 section rewritten; audit/gate mentioned in the linked "Process & AI Use" section (not the literal top "How this was built" one-liner, which is unchanged — minor, not scored as a gap given the explicit link) |
| CORR-05 | ✓ Satisfied | iqp-lit-scoping.md addendum present (uncommitted — see #10 above) |
| CORR-06 | ✓ Satisfied | Post_Sept1_IQP_Photonic_Plan.md corrected |
| CORR-07 | ✓ Satisfied | case-study page corrected, lint/build green, committed (not pushed) |
| REFRAME-01 | ✗ Blocked | Closed form stated in prose; required table/plot missing |
| REFRAME-02 | ✗ Blocked (Should) | No code change found; residual still collapsed |
| GATE-01 | ✓ Satisfied | CLAUDE.md gate + learning note present |
| REVIEW-01 | ✗ Blocked | No 24-REVIEW.md, no evidence a Codex review ran |
| COMM-01 | ✗ Blocked | No draft found; decision log still "pending" |

### Anti-Patterns Found

None in the reviewed correction prose or test file (no TBD/FIXME/XXX debt markers in the phase-touched files). One readability defect, informational only: `README.md` lines 33 and 35 contain near-duplicate "Supporting this pair of..." paragraphs back-to-back — looks like a leftover from the correction edit that wasn't cleaned up (not a factual error, just a duplicated sentence).

### Independent Assessment (requested beyond standard phase verification)

**1. Does `docs/iqp-photonic-encoding.md` still claim/imply the polarization encoding is a novel contribution rather than a specific instance of KLM (2001)?**

**Yes — confirmed still standing, uncorrected.** Line 3 states: "This is Phase 9's deliverable in the `v2.0 IQP → Photonic Encoding` milestone, and **the milestone's actual novel-contribution piece**." No 2026-09-03 dated correction exists anywhere in this file (grepped for "novel", "KLM", "Knill", "contribution", "2026-09"). The document does have a pre-existing, more careful "What is, and isn't, a contribution here" section (line 214) that scopes the claim to "a design/mapping exercise... not a peer-review-grade complexity-theoretic reduction proof" and elsewhere (line 212) references "KLM-type no-go for deterministic linear-optical entangling gates" for the multi-qubit case specifically — but this predates the audit and does not state the broader point the (uncommitted) `iqp-lit-scoping.md` addendum makes explicitly: that KLM (dual-rail photons + heralded gates, 2001) already lets *any* qubit circuit be realized in linear optics, so this project's mapping is "a genuine, carefully-checked instance of that general fact, not a case the literature left open." That addendum text explicitly says this framing is "worth citing in `docs/iqp-photonic-encoding.md`'s positioning" — i.e., it names the fix as not-yet-done. This matches the user's premise exactly: not corrected in this session.

**2. Does `docs/trainability-study.md`'s "Honest max-n statement" (TRAIN-05/TRAIN-08) still attribute the n<=6 ceiling purely to Fock-space combinatorial growth, without noting it's a simulator-architecture choice?**

**No — this one WAS corrected, contrary to the premise, but the fix is uncommitted.** A new paragraph now leads the "Honest max-n statement" section (line 66): "**Correction (2026-09-03) — the ceiling below is a simulator-architecture choice, not a physical limit.**" It explicitly states the `C(3n-1,n) ~ 6.75^n` growth is real for "this pipeline's specific method" but "not forced by the physics," names the structured-simulator alternative that would reach n in the 20s, and cites `dual_rail_autograd_sweep.py`'s own n=7-8 result as corroboration. This is a substantive, accurate correction. **However**, this text exists only in the working tree, not in the last commit (`0658ab6`) — `git diff` confirms `docs/trainability-study.md` is currently modified-but-uncommitted. Report this to the owner as needing a commit, not as a missing fix.

### Gaps Summary

Two Must-have deliverables are entirely missing (REVIEW-01's Codex review + `24-REVIEW.md`; COMM-01's Vincent draft + send/hold decision) — both were explicitly required by ROADMAP.md's numbered success criteria #5 and #6 and by REQUIREMENTS.md's Finish Criteria #4/#5. One Must-have (REFRAME-01) is half-done: the throughput closed form is stated correctly in prose, but the required table/plot never shipped. One Should-have (REFRAME-02) was not started at all — the lossy distribution functions are byte-for-byte unchanged from before Phase 24. NULL-01, the phase's own explicit self-explanation gate, is honestly disclosed as incomplete for the mixed-scope formula (weight-1 is solid). Finally, three files carrying real correction content (`README.md`, `docs/iqp-lit-scoping.md`, `docs/trainability-study.md`) are currently uncommitted at HEAD — none of this uncommitted work is reflected in the single Phase 24 commit, so the "shipped" record as of `0658ab6` is narrower than what's sitting in the working tree.

What is genuinely solid: the null-result test suite (129/129 green, full suite 425/425 green, no skips, real CSV coverage), five of seven document corrections fully committed and well-written (trainability-study, hardness-under-loss-study, technical-findings, README, Post_Sept1), the CLAUDE.md gate + learning note, and the separate case-study repo's correction (committed, lint/build green). The corrections that do exist are unusually careful and honest in tone — they read as genuine corrections, not narrative repair.

---

*Verified: 2026-09-03*
*Verifier: Claude (gsd-verifier)*
