---
phase: 20-technical-write-up
verified: 2026-08-18T11:39:12Z
status: passed
score: 6/6 must-haves verified
---

# Phase 20: Technical Write-Up Verification Report

**Phase Goal:** Write up STUDY-01 (Phase 17), STUDY-02 (Phase 18), and ARB-01
(Phases 15-16) findings as the projects technical findings document -
methodology-stated-before-results, honest negative/inconclusive framing
wherever the data warrants it, matching this projects existing
GEN-07/LIT-04/Phase-7 rigor bar.

**Verified:** 2026-08-18T11:39:12Z
**Status:** passed
**Re-verification:** No - initial verification

## Goal Achievement

### Observable Truths / Success Criteria

| # | Criterion | Status | Evidence |
|---|-----------|--------|----------|
| 1 | Methodology-before-results structure for TRAIN/HARD/ARB | VERIFIED | docs/trainability-study.md: Methodology (L9) precedes Results (L72). docs/hardness-under-loss-study.md: Methodology (L24) precedes HARD-05 results (L150). docs/iqp-photonic-encoding.md ARB-01/ARB-02 section: Owners Attempt derivation (L379) precedes General-alpha Operator Identity / Closed-Form Success Probability / Full-Pipeline Validation results (L391-467). |
| 2 | Comparison table vs all 11 named baselines, per-baseline verdict | VERIFIED | TRAIN table (trainability-study.md L623-711): 6 substantive plus 5 silent rows, all 11 named. HARD table (hardness-under-loss-study.md L544-591): 5 substantive plus 6 silent rows, all 11 named, with reasoning paragraph per substantive row. ARB table (iqp-photonic-encoding.md L488-503): 1 substantive row (arXiv:2405.01395) plus explicit prose naming and dispositioning the other 10 as not-applicable (not silently omitted). All cited papers present as PDFs in docs/papers/. |
| 3 | Honest negative/inconclusive framing where data warrants it | VERIFIED | TRAIN-09 (bandwidth follow-up) reported as NOT robust and TRAIN-10 (data-dependent init) reported as did NOT resolve - genuine negative results stated plainly, not softened. HARD-04 explicitly declines to fabricate an eta-to-epsilon translation, on the record. mixed/uniforms disagreement with the qubit-side empirical rule is reported as disagree, not smoothed over. |
| 4 | What this does/doesnt establish scope paragraph per section | VERIFIED | trainability-study.md What this does/doesnt establish (L595+). hardness-under-loss-study.md HARD-06 section (L643+). iqp-photonic-encoding.md What ARB-01/ARB-02 does/doesnt establish (L488+). All three explicitly state non-claims (no complexity proof, no asymptotic-scale demonstration, toy-check scope). |
| 5 | Self-explanation checkpoint transcripts (owners own words, not Claude-authored), plus numeric traceability, plus fixed seeds | VERIFIED | docs/trainability-study.md Cross-reference verdict TRAIN-07 section (starting ~L174) is a genuine multi-step transcribed dialogue: states the ruled-out complete_graph_like first hypothesis and why it failed, a pushed-back-on overreaching framing, and the final revised literature-framing conclusion. technical-findings.md Traceability and consistency note (L304-321) maps every headline number to a specific CSV or test file, confirmed present in results/. HARDs seed_base=180814 is a fixed literal (hardness-under-loss-study.md L91-92); TRAINs trainability/rng.py derive_seed per-coordinate hashed-seed scheme is described honestly as architecturally different rather than forced into false parity. |
| 6 | TRAIN and HARD explicitly engage with Herbst et al anticoncentration-tradeoff prediction, stated plainly consistent/inconsistent | VERIFIED | trainability-study.md Cross-reference: Herbst et al section (L717+) and hardness-under-loss-study.md equivalent section (L680+) both state the framework, TRAINs own necessary-precondition finding, and HARDs own measured direction (alpha(eta) decreasing, i.e. MORE anticoncentrated under loss - the reverse of the projects own earlier speculative guess). HARDs literature table explicitly marks Herbst as inconsistent with the original speculative framing; TRAINs table points to the cross-reference note rather than forcing a premature single-word verdict. Both sections state the honest hedge that TRAIN and HARD dont share a common independent variable. |

**Score:** 6/6 criteria verified.

### Required Artifacts

| Artifact | Expected | Status | Details |
|----------|----------|--------|---------|
| docs/technical-findings.md | Synthesis doc, mirrors 3 source docs tables, no re-derivation | VERIFIED | 322 lines, substantive. Every table mirrored with pointer-back to source. Traceability note confirms no new/uncited numbers. Links (not restates) each source docs scope section and Herbst cross-reference. |
| docs/trainability-study.md | TRAIN-07 checkpoint, literature table, Herbst note | VERIFIED | All three present and substantive. |
| docs/hardness-under-loss-study.md | Literature table, Herbst note, stale-header fix | VERIFIED | All three present; HARD-04 heading confirmed a resolvable single heading anchor. |
| docs/iqp-photonic-encoding.md | ARB-01/ARB-02 scope subsection plus literature table | VERIFIED | Section present with both scope statement and table. |
| docs/papers PDFs | Primary sources for all 11 cited baselines | VERIFIED | All 11 baseline papers present as downloaded PDFs (McClean confirmed via arXiv API per stated lower-confidence-tier caveat, all others full PDF). |
| results CSVs | Numeric traceability targets cited in technical-findings.md | VERIFIED | phase17_curve_fit_summary.csv, phase171_train09/10_curve_fit_summary.csv, phase18_weight1/mixed_loss_sweep.csv, phase16_alpha_sweep.csv all present in results/. |

### Key Link Verification

| From | To | Via | Status |
|------|-----|-----|--------|
| technical-findings.md TRAIN section | trainability-study.md | markdown link to methodology, cross-reference-verdict, scope, literature-table anchors | WIRED |
| technical-findings.md HARD section | hardness-under-loss-study.md | markdown link to HARD-06 and HARD-04/HARD-06 anchors | WIRED |
| technical-findings.md ARB section | iqp-photonic-encoding.md | markdown link to ARB-01/ARB-02 scope anchor | WIRED |
| technical-findings.md Herbst cross-thread | both source docs cross-reference notes | markdown links | WIRED |
| technical-findings.md Independent verification | docs/julia-cross-check-study.md | markdown link | WIRED (file exists) |

### Requirements Coverage

| Requirement | Status | Note |
|-------------|--------|------|
| WRITE-01 (methodology-before-results) | SATISFIED | See criterion 1 |
| WRITE-02 (11-baseline comparison table) | SATISFIED | See criterion 2 |
| WRITE-03 (honest negative framing) | SATISFIED | See criterion 3 |
| WRITE-04 (scope paragraphs) | SATISFIED | See criterion 4 |
| WRITE-05 (self-explanation transcripts) | SATISFIED | See criterion 5 |
| WRITE-06 (numeric traceability plus fixed seeds) | SATISFIED | See criterion 5 |

Bookkeeping note (not a goal-achievement gap): .planning/REQUIREMENTS.md
still shows WRITE-01 through WRITE-06 as unchecked and Pending (lines
54-59, 127-132), even though the underlying work is substantively complete
and verified above (contrast with TRAIN-07, which is marked Complete at
lines 18/113). This is a checklist-maintenance gap in REQUIREMENTS.md
itself, not evidence the phase goal was not achieved - recommend updating
those checkboxes as a trivial follow-up, but it does not block phase 20
status.

### Anti-Patterns Found

None. No TODO/FIXME/placeholder patterns found in the phases deliverables.
No stub sections, empty scope statements, or unsupported claims - this is a
documentation phase, and all four SUMMARY-claimed artifacts are present,
substantive, and cross-linked correctly.

### Human Verification Required

None required for structural/goal verification. The one item that is
inherently a human judgment call - whether the TRAIN-07 owner interpretation
and the Herbst cross-reference framing are correct physics/statistics
reasoning, not just present as a transcript - was already the owner own
stated conclusion (transcribed, not Claude-authored), consistent with this
project CLAUDE.md convention that interpretive conclusions are the owner
to make, not Claude own.

### Gaps Summary

No gaps found. All 6 ROADMAP success criteria and all 6 mapped requirements
(WRITE-01..06) are verified against actual file content, not SUMMARY claims.
The one discrepancy found - REQUIREMENTS.md stale unchecked checkboxes -
is a documentation-bookkeeping issue, not a goal-achievement gap, and is
flagged above for a trivial follow-up fix rather than blocking phase status.

---

Verified: 2026-08-18T11:39:12Z
Verifier: Claude (gsd-verifier)
