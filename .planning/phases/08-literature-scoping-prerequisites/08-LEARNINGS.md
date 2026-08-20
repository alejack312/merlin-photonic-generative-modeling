---
phase: 8
phase_name: "Literature Scoping & Prerequisites"
project: "MerLin Photonic Generative Modeling"
generated: "2026-08-20"
counts:
  decisions: 5
  lessons: 4
  patterns: 4
  surprises: 3
missing_artifacts: []
---

# Phase 8 Learnings: Literature Scoping & Prerequisites

## Decisions

### Go verdict on LIT-04: proceed to Phase 9
No blocking impossibility result against a DV/Fock-space IQP construction was found across two independent search passes (WebSearch-based in `08-RESEARCH.md`, arXiv-API + Semantic Scholar citation-graph-based in `docs/iqp-lit-scoping.md`) plus a full read of the closest tangential paper (Kurkin et al.'s Boson Sampling Born Machine, arXiv:2603.11014). Per `08-CONTEXT.md`'s locked bar, a full constructive mapping is not required at this gate — absence of a blocker is sufficient, since building the construction is Phase 9's own job.

**Rationale:** `08-CONTEXT.md` set a deliberately low "go" bar (no blocking impossibility result found) versus a high "not-ready" bar (an explicit impossibility/no-go argument required). Two search passes plus one full paper read cleared the low bar with no hits on the high bar.
**Source:** 08-01-SUMMARY.md, docs/iqp-lit-scoping.md (verdict section)

---

### Kurkin et al.'s BSBM explicitly rejected as grounds for "promising but needs more time"
The owner considered and rejected using this closely-adjacent paper as the trigger for a "needs more time" verdict.

**Rationale:** BSBM transplants IQP-QCBM's classically-trainable/quantum-deployed training recipe onto boson sampling's own separate, pre-existing hardness lineage (Aaronson-Arkhipov permanent-hardness) rather than building IQP's own commuting-diagonal-gate + Hadamard-conjugated-measurement structure inside Fock space. It doesn't satisfy LIT-01's specific ask, though it's flagged as relevant context for Phase 9 to cite.
**Source:** 08-01-SUMMARY.md (Decisions Made section)

---

### Doc house style: grounding statement + reference-glossary scope, not persuasive essay
Both `docs/iqp-lit-scoping.md` and `docs/iqp-baseline.md` open with a grounding statement naming exact source files read (not memory-derived), and are scoped to 1-2 pages as scannable reference docs rather than deep-dives.

**Rationale:** Follows the existing `docs/mmd-loss.md` convention; keeps future-reader (including the owner, unaided) able to scan quickly without re-reading a full paper stash. `docs/iqp-baseline.md` cross-references `docs/iqp-lit-scoping.md` by name instead of duplicating its content, deliberately keeping scope tight.
**Source:** 08-03-PLAN.md, 08-03-SUMMARY.md

---

### PS gap closed via a Mach-Zehnder (BS-PS-BS) construction, not a bare PS example
When `08-VERIFICATION.md` flagged that `perceval_fluency_demo.py` never exercised `pcvl.PS`, the remediation (plan 08-04) added a BS.H()->PS(theta)->BS.H() construction rather than a standalone phase-shifter call.

**Rationale:** A bare phase shifter's angle has no effect on Fock-basis photon-number measurement without a second beamsplitter to convert phase into an observable amplitude/probability change. The MZI form is the version that actually demonstrates why PS matters, and doubles as directly relevant groundwork for Phase 9's phase-driven interference reasoning.
**Source:** 08-04-PLAN.md, 08-04-SUMMARY.md

---

### Gap closure treated as boilerplate, not a design decision requiring attempt-first gating
Plan 08-04 (adding the missing PS example) proceeded without an owner attempt-first checkpoint, unlike plans 08-01 (owner verdict) and 08-02 (owner circuit sketch).

**Rationale:** Per this repo's CLAUDE.md, MerLin/Perceval API syntax lookups are offloadable; this was API-lookup work on an already-attempted, already-implemented demo, not a new conceptual decision.
**Source:** 08-04-PLAN.md (objective section)

---

## Lessons

### Line count understates content for this repo's dense-prose doc style
`docs/iqp-baseline.md` and `docs/iqp-lit-scoping.md` run 32-45 lines by `wc -l` while still being genuinely 1-2 pages of content, because the house style uses unwrapped long-line paragraphs.

**Context:** The plan's `min_lines: 40` artifact check was cross-verified against word count (~885-900 words) as a better "1-2 pages" proxy than raw line count, when confirming `docs/iqp-baseline.md` met its scope target.
**Source:** 08-03-SUMMARY.md (Decisions Made, patterns-established)

---

### `pcvl.pdisplay()` requires `PYTHONIOENCODING=utf-8` on Windows
`pcvl.pdisplay()`'s box-drawing table characters raise a `UnicodeEncodeError` in a default Windows terminal/venv without this env var set.

**Context:** Discovered during the owner's live attempt at the Perceval fluency demo (plan 08-02, Task 1 checkpoint). Documented in the script's own header comment as a standing requirement for this machine, and confirmed still needed when running plan 08-04's extended demo.
**Source:** 08-02-SUMMARY.md (Issues Encountered), 08-04-SUMMARY.md (Issues Encountered)

---

### `circuit.add(port, component)` takes a starting port index (int), not a range/tuple
The owner's first attempt at building a manual Perceval circuit needed to work out this call signature — `pcvl.BS.H()` is a 2-mode component, so `circuit.add(0, pcvl.BS.H())` wires it across modes 0 and 1 of a 2-mode circuit.

**Context:** Surfaced during the owner's live, unaided circuit-build attempt in plan 08-02's attempt-first checkpoint; the correct call is now the working pattern reused across all of `perceval_fluency_demo.py`'s three examples.
**Source:** 08-02-SUMMARY.md (Issues Encountered)

---

### `Analyzer` requires a `Processor`, not a bare `Circuit`, and lives outside the top-level namespace
`from perceval.algorithm import Analyzer` is required (not exported at `pcvl.` top level); it must be constructed as `Analyzer(pcvl.Processor("SLOS", circuit), [input_states], "*")`.

**Context:** Verified directly against the installed `perceval-quandela==1.2.4` during `08-RESEARCH.md`'s prep for plan 08-02, and carried into the checkpoint's pre-implementation API brief so the owner could attempt the circuit unaided.
**Source:** 08-02-PLAN.md (checkpoint context)

---

## Patterns

### Reading `Analyzer.distribution` via BasicState-keyed dict, not positional indexing
Zip `ca.output_states_list` against each row of `analyzer.distribution` into a `{BasicState: probability}` dict rather than indexing by column position.

**When to use:** Any future Perceval `Analyzer` usage — stays robust to Perceval's internal output-state enumeration order changing, and makes assertion code self-documenting (e.g. `dist.get(pcvl.BasicState([1, 1]))` reads directly as the physics being checked). Directly reusable in Phase 9's less-trivial encoding circuits.
**Source:** 08-02-SUMMARY.md (tech-stack patterns, Decisions Made)

---

### Layer assertions on top of an owner's working circuit sketch rather than rewriting wholesale
When the owner's attempt-first checkpoint produces a genuinely correct, working implementation, Claude's follow-up task builds on top of it (adds tests/PASS-FAIL reporting) instead of replacing the owner's structure with a "cleaner" rewrite.

**When to use:** Any attempt-first-gated task where the owner's sketch already works — preserves ownership and avoids silently discarding the owner's verified reasoning. Applied even down to preserving a single-`Analyzer`-call structure that diverged cosmetically from the plan's literal wording.
**Source:** 08-02-SUMMARY.md (Decisions Made, Deviations from Plan)

---

### Closed-form interference check via algebraic amplitude derivation + small theta sweep
Derive output amplitudes algebraically from real Hadamard-BS matrices sandwiching a bare `e^{i*theta}` phase term, then assert `np.isclose` per output state across a small theta sweep covering fully-constructive (0), 50/50 (pi/2), and fully-flipped (pi) cases.

**When to use:** Any future Perceval demo or test needing to verify phase-driven interference programmatically rather than eyeballing a printed distribution table. Reusable directly for Phase 9's less-trivial encoding circuits, which will need similar phase-driven interference reasoning.
**Source:** 08-04-SUMMARY.md (patterns-established)

---

### Second literature-search pass must use a genuinely different method, not re-run the same query style
When a prior pass (WebSearch keyword search) found nothing, the confirming second pass used a different method entirely (arXiv API keyword search + Semantic Scholar citation-graph chasing in both directions from the seed paper), not just differently-phrased WebSearch queries.

**When to use:** Any go/no-go literature-scoping gate requiring both a constructive and disconfirming search pass — using a structurally different search method (not just different keywords) is stronger evidence of a genuine absence than repeating the same tool with new phrasing.
**Source:** 08-01-SUMMARY.md (Accomplishments), 08-01-PLAN.md (Task 2 action)

---

## Surprises

### Verification found a real functional gap (PS never exercised) despite an otherwise-complete-looking demo
`08-VERIFICATION.md`'s first pass scored Phase 8 at 9/10: `perceval_fluency_demo.py` had a dead `phase_shift(circuit, angle)` stub referencing `pcvl.PS(angle)` but it was never actually wired into a circuit or called — despite `PS` being explicitly named in both `08-CONTEXT.md`'s locked scope and ROADMAP.md's Phase 8 success criterion 4.

**Impact:** Required a full extra plan (08-04) to close, adding a third worked example (Mach-Zehnder interferometer) and its test coverage. Confirms that mechanical `grep`-style verification checks (e.g. "does `pcvl.PS(` appear") catch gaps that plan-writing and even a passing test suite can miss when a helper is defined but never called.
**Source:** 08-VERIFICATION.md (score 9/10 -> 10/10, gap closed), 08-04-PLAN.md (objective)

---

### Owner's live attempt-first checkpoint exceeded the plan's minimum bar
Plan 08-02's Task 1 checkpoint only required "even a rough attempt, partial code, or a written description" — the owner instead built a fully working, physically-correct circuit end-to-end in their own live terminal session, confirmed by eye against both closed-form predictions before Claude wrote anything.

**Impact:** Task 2 built directly on top of the owner's working structure rather than needing to construct anything from scratch, and preserved several of the owner's specific implementation choices (single combined `Analyzer` call, particular import path) as deliberate rather than default choices.
**Source:** 08-02-SUMMARY.md (Checkpoint Resolution section)

---

### Documentation-bookkeeping gaps (stale REQUIREMENTS.md checkboxes) persisted across two verification passes
Both the initial verification and the post-gap-closure re-verification flagged the same issue: `.planning/REQUIREMENTS.md`'s checkboxes for LIT-01/02/04/PREQ-01/02 remained unchecked and `ROADMAP.md`'s Phase 8 progress row remained stale, even after all functional/artifact gaps were closed.

**Impact:** Confirms these are explicitly out-of-scope for the plans that closed the functional gap (08-04 was "scoped narrowly to the PS gap, correctly so") — the bookkeeping update is a separate, still-open task for whoever next touches those files, not a signal that Phase 8's actual deliverables are incomplete.
**Source:** 08-VERIFICATION.md (Requirements Coverage note, Anti-Patterns Found), 08-04-SUMMARY.md (Next Phase Readiness)
