# Milestone provenance audits
Date: 2026-08-22 · Scope: project · Recurs when: auditing a milestone created across different GSD schema versions

## Context & constraints
- Current milestone audits require three independent sources per requirement: traceability, phase verification, and SUMMARY `requirements-completed` frontmatter.
- v3.0's legacy Phase 14–21 summaries predate that frontmatter even though their phase verifications pass.
- Additive Phases 22–23 expanded the previously audited milestone from 37 to 51 requirements.

## Approach
1. Resolve the live milestone scope from GSD and ROADMAP before reusing an older audit.
2. Read every in-scope VERIFICATION report, then extract SUMMARY requirement metadata independently.
3. Cross-reference every traceability ID and apply the current status matrix literally.
4. Run the integration checker only after phase evidence is aggregated.
5. Report functional evidence separately from provenance compliance.

## Decision rules that generalize
- IF an older audit has a smaller phase or requirement count than live traceability THEN supersede it with the current scope.
- IF behavior is verified but SUMMARY metadata is missing THEN mark the requirement partial, not satisfied.
- IF a traceability ID is absent from all requirement-verification tables THEN mark it orphaned/unsatisfied even when equivalent behavior was tested.
- IF one requirement is unsatisfied THEN force milestone status to `gaps_found`.
- IF integration is clean but provenance fails THEN say explicitly that the blocker is metadata/process evidence, not implementation behavior.

## Mistakes avoided / dead ends
- Do not reuse a prior 37/37 score after additive phases changed the milestone to 51 requirements.
- Do not treat a phase-level 4/4 score as requirement-level coverage when the report explicitly says no requirement is mapped.
- Do not auto-promote legacy summaries by inferring `requirements-completed` from prose.

## Verification
- `gsd-sdk query init.milestone-op` reported v3.0 with 11 completed phases.
- Direct artifact scan found 12/51 requirements in SUMMARY frontmatter, 38 partial requirements, and one orphaned `VERIFY-01`.
- `git diff --check` must return no whitespace errors for the generated audit and learning note.

## Next time (for a weaker model)
- Do: compare live phase/requirement counts with the existing audit before trusting it.
- Do: preserve both scores when useful: functional phase coverage and strict three-source coverage.
- Don't: rewrite implementation history to make old metadata look current.

## Changed files
- `.planning/v3.0-MILESTONE-AUDIT.md` — current 51-requirement audit with integration and Nyquist findings.
- `.Codex/learnings/2026-08-22-milestone-provenance-audit.md` — reusable cross-version audit procedure.
