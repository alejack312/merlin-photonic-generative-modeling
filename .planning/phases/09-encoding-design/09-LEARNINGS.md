---
phase: 9
phase_name: "Encoding Design"
project: "MerLin Photonic Generative Modeling"
generated: "2026-08-20"
counts:
  decisions: 8
  lessons: 6
  patterns: 6
  surprises: 5
missing_artifacts:
  - "VERIFICATION.md"
---

# Phase 9 Learnings: Encoding Design

## Decisions

### Polarization (H/V) encoding chosen over dual-rail/QUDIT
Owner chose polarization encoding from personal Sorbonne coursework, not dual rail or QUDIT.

**Rationale:** Personal familiarity, and it corrected a real inaccuracy in 09-RESEARCH.md, which had characterized polarization as lacking a native gate catalog — direct inspection of the installed `perceval-quandela==1.2.4` source showed it ships HWP, QWP, PR, WP, and PBS.
**Source:** 09-01-SUMMARY.md

---

### Scope limited to weight-1 IQP generators for runnable code; weight-2 derived on paper only
Runnable code and tests cover only weight-1 (`exp(iθZ)`) generators. Weight-2 (`exp(iθZ_iZ_j)`) is derived on paper via a PBS-mediated conversion to dual rail's `core_catalog.heralded_cz`, using the operator identity `CZ = exp(iπ/4·(I−Z_i−Z_j+Z_iZ_j))`.

**Rationale:** `heralded_cz` is a fixed-angle (π/4) instance of the ZZ-interaction family, not continuously tunable — a real limitation of the catalog gate, not a design flaw in the mapping. Extending it to a runnable, continuously-tunable weight-2 gate was out of scope for this phase.
**Source:** 09-01-SUMMARY.md

---

### heralded_cz's mechanism verified by source read; its success probability explicitly left unverified
The source of `core_catalog.heralded_cz` was read directly (Knill CZ, arXiv:quant-ph/0110144, 2 herald modes each requiring exactly 1 photon) to confirm the mechanism is real.

**Rationale:** The 1/9 (post-selected KLM) / 2/27 (heralded variant) success-probability figures are secondhand literature citations for the same gate family — flagged as assumed, not verified, rather than stated as established fact.
**Source:** 09-01-SUMMARY.md

---

### Out-of-subspace policy: report residual probability, never silently discard/renormalize
`fock_to_bitstring` returns `None` for any of the four out-of-subspace photon patterns; the readout pipeline reports the leftover probability mass explicitly rather than discarding and rescaling.

**Rationale:** Owner's choice, confirmed at a Task 3 checkpoint by reasoning through what silent renormalization would hide from ENC-04's later distribution comparison — the qubit-side reference distribution has no invalid outcomes, so silently rescaling the photonic side would produce an unfair comparison.
**Source:** 09-02-SUMMARY.md

---

### Corrected H/V port convention applied retroactively across the whole codebase
The verified port convention (H=(0,1), V=(1,0), confirmed via bare-PBS calibration) was applied retroactively to Wave 1's `basic_state_to_bitstring`, `expected_single_qubit_probs`, and ENC-01's derivation text — not scoped narrowly to just the new ENC-03 functions.

**Rationale:** Owner explicitly requested consistency across the document/codebase even though the bug was self-consistent (no Wave 1 test's pass/fail result ever changed) — a correctness fix, not a new feature, and treated as in-scope per this repo's deviation rules.
**Source:** 09-02-SUMMARY.md

---

### Validation metric: total variation distance (TVD), not MMD, with threshold 1e-6
ENC-04 uses TVD between a direct numpy state-vector reference distribution and the decoded photonic circuit's output distribution, with a pass threshold of TVD < 1e-6.

**Rationale:** MMD's kernel/bandwidth-selection machinery exists to handle sampling noise; both distributions here are exact calculations, so there is no noise to smooth over and no principled way to pick a bandwidth. The 1e-6 threshold was deliberately distinguished from the sibling `iqp-mmd-barren-plateau` project's thresholds (0.05/0.4), which apply to a sampled-vs-learned comparison with real statistical noise — not this exact-vs-exact situation.
**Source:** 09-03-SUMMARY.md

---

### Reference distribution: direct numpy state-vector simulation, not Van den Nest's cosine formula or the sibling repo's IqpSimulator
ENC-04's ground-truth distribution is computed via plain numpy (`|+⟩^n → diagonal phase → H^n → |amplitude|²`).

**Rationale:** Van den Nest's cosine-formula trick yields expectation values, not a full distribution, requiring an extra transform step; reusing the sibling repo's `IqpSimulator` was judged a disproportionate cross-repo dependency for an n=2-3 toy check.
**Source:** 09-03-SUMMARY.md

---

### ENC-02 states the honest parallel to Douce et al. as prominently as the favorable contrast
ENC-02 positions the mapping against Douce et al. (2017) with an explicit favorable contrast (native, deterministic `HWP(π/8)` single-qubit conjugation vs. Douce's gadget-only realization) placed alongside an equally explicit honest parallel: the weight-2 `heralded_cz` construction is itself measurement-conditioned, the same character as Douce's post-selected Fourier gadget.

**Rationale:** Required by 09-CONTEXT.md's explicit hedged-tone constraint (owner is a not-yet-graduated master's student; document must not overclaim) and 09-RESEARCH.md's Pitfall 3 warning against claiming DV avoids the measurement-based-realization problem entirely.
**Source:** 09-04-SUMMARY.md

---

## Lessons

### A self-consistent bug can still be physically backwards
Wave 1's `basic_state_to_bitstring` and `expected_single_qubit_probs` had the H/V port convention backwards `((1,0)→H, (0,1)→V` instead of the correct `(0,1)→H, (1,0)→V)`. Because the error was applied consistently throughout the pipeline, no Wave 1 test's pass/fail result was ever wrong — but the human-readable labels didn't match true physical polarization.

**Context:** Caught in Plan 09-02 via a bare-`PBS`, pure-H/V-input calibration check that isolated the port↔polarization fact from the rest of the pipeline. Self-consistency is not the same as correctness; a convention bug can hide indefinitely behind passing tests until an independent calibration check is run.
**Source:** 09-02-SUMMARY.md

---

### A clean match at one generator weight provides no evidence about a structurally different weight
The owner's initial claim that the weight-1 TVD match "will extend to generators of higher weight" was corrected during the Plan 09-03 checkpoint: weight-1 (`WP`, exact/deterministic/any angle) and weight-2 (`heralded_cz`, probabilistic/fixed-angle) are structurally different mechanisms.

**Context:** A clean weight-1 result is silent on weight-2's behavior; this was documented as a standing scope limit in the mapping document rather than smoothed over or left implicit.
**Source:** 09-03-SUMMARY.md

---

### Scientific notation is easy to misread under threshold comparison
The owner's first interpretation of the TVD result read `3.85×10⁻¹⁶` as failing the `1×10⁻⁶` threshold, rather than passing it by ten orders of magnitude.

**Context:** Caught during the Plan 09-03 self-explanation checkpoint; corrected with a concrete magnitude comparison rather than restating the numbers abstractly. A draft of the doc itself also contained a related arithmetic slip ("four orders of magnitude" instead of the correct ten), caught before finalizing.
**Source:** 09-03-SUMMARY.md

---

### The hardest checkpoint question across multiple passes was the same one: basis correspondence / falsifiability
In both the Plan 09-04 final self-explanation checkpoint and the independent 09-UAT re-test, the basis-correspondence/falsifiability question required the most correction rounds of any topic — including a repeat of the exact reversed H/V port-labeling mistake that Plan 09-02's calibration check had originally caught and fixed.

**Context:** Suggests this particular piece (why the forward/reverse round-trip constitutes a checkable, falsifiable claim rather than a plausible-sounding analogy) is genuinely harder to internalize than the other four checkpoint topics, and that a corrected bug can resurface in verbal explanation even after the code fix is verified and tested.
**Source:** 09-04-SUMMARY.md, 09-UAT.md

---

### Phase 9 shipped without a standalone VERIFICATION.md; closed later via an independent UAT pass
Unlike most phases in this project, Phase 9 has no `09-VERIFICATION.md`. This was later identified as process tech debt and closed out via a separate `09-UAT.md` pass that independently re-verified all `must_haves` (including re-running the self-explanation checkpoint bar).

**Context:** The UAT pass re-ran ENC-01 through ENC-05's checks live (code execution, doc-section presence, full test suite) rather than trusting the SUMMARY.md files' claims, and treated the checkpoint-repeat of the H/V mixup as a recorded (not hidden) minor finding rather than a blocking gap.
**Source:** 09-UAT.md

---

### Owner's initial attempt-first sketches consistently needed correction before being workable
Across all four plans' Task 1 checkpoints, the owner's first-round answer required at least one correction: beamsplitter vs. waveplate and CNOT/SWAP-not-Z-diagonal (Plan 01); all three sub-questions needed to be broken into smaller guided questions (Plan 02); mistaking the photonic circuit for its own validation reference, then proposing MMD before settling on TVD (Plan 03); five correction rounds across all five required points in the whole-document checkpoint (Plan 04).

**Context:** This is the expected shape of attempt-first gating on a genuinely hard conceptual phase, not a process failure — the plan's "a rough attempt is enough" allowance was explicitly invoked rather than treating multi-round correction as a blocker.
**Source:** 09-01-SUMMARY.md, 09-02-SUMMARY.md, 09-03-SUMMARY.md, 09-04-SUMMARY.md

---

## Patterns

### Isolate one fact with a minimal calibration circuit before trusting it inside a larger pipeline
The port↔polarization convention was verified using a bare `PBS` with no other gates and pure H/V input, rather than inferring it from a sandwiched multi-gate circuit.

**When to use:** Whenever a convention or mapping fact needs verifying and could be entangled with other pipeline behavior — build the smallest possible circuit/test that isolates exactly the one fact being checked.
**Source:** 09-02-SUMMARY.md

---

### Round-trip tests double as both a falsifiability statement and a bug-catching mechanism
Forward map → physical circuit → reverse map → compare to original was documented as ENC-03's falsifiability claim, and it's also the mechanism that actually caught the H/V labeling bug.

**When to use:** When a design document needs to state a "checkable claim" (vs. a plausible-sounding analogy) about a bidirectional mapping — implement the round trip as an actual test, not just prose, so the claim and its verification are the same artifact.
**Source:** 09-02-SUMMARY.md

---

### Document negative/partial results and Q&A corrections in place, not just polished final answers
Self-explanation checkpoint transcripts — including initial incorrect/incomplete answers and their corrections — are recorded directly in the mapping document's own sections, not smoothed into a single clean final answer.

**When to use:** Any phase involving attempt-first checkpoints or self-explanation gates where the document itself is meant to be a defensible, honest record (matches this repo's established v1.0 GEN-07 / Phase 7 precedent).
**Source:** 09-01-SUMMARY.md, 09-02-SUMMARY.md, 09-03-SUMMARY.md, 09-04-SUMMARY.md

---

### When a later plan corrects an earlier convention, add an editorial note rather than rewriting historical transcripts
ENC-01's Self-Explanation Checkpoint section (which referenced the pre-correction H/V convention) was left unedited when Plan 09-02 fixed the underlying bug; an editorial note pointing to the correction was added instead.

**When to use:** Any time a later phase/plan invalidates an assumption baked into an earlier, already-recorded checkpoint transcript — preserves an accurate historical record of what was actually said/known at the time, rather than silently rewriting history.
**Source:** 09-02-SUMMARY.md

---

### A document-level "Conclusion and Open Questions" section collects every limitation stated piecemeal
Rather than requiring a reader to hunt through each section for its individually-stated caveat, a final Conclusion section aggregates every limitation (generator-weight scope, unverified `heralded_cz` success probability, toy-check scope, general-n scaling not demonstrated) into one place.

**When to use:** Any multi-section technical document that accumulates scope limitations section-by-section and needs a single honesty ledger for a reader (e.g., an advisor or interviewer) to check quickly.
**Source:** 09-04-SUMMARY.md

---

### Hedged-tone positioning states both the favorable contrast and the honest parallel, not just the flattering half
When comparing this work against prior literature (Douce et al.), the document states the favorable difference and the place where the same limitation the literature has also applies here — deliberately, not by omission.

**When to use:** Any positioning/related-work section written under an explicit tone constraint against overclaiming (e.g., pre-publication, student-authored, or credential-building documents) — state the parallel as prominently as the contrast.
**Source:** 09-04-SUMMARY.md

---

## Surprises

### A research document's factual claim about API capability was wrong and caught only by direct source inspection
09-RESEARCH.md claimed Perceval lacks a polarization gate catalog. Direct inspection of the installed `perceval-quandela==1.2.4` source showed it ships HWP, QWP, PR, WP, and PBS.

**Impact:** Corrected the scheme-selection decision's factual basis after the fact; a reminder that research-phase API surveys should be checked against installed source rather than trusted at face value when a downstream decision depends on them.
**Source:** 09-01-SUMMARY.md

---

### The H/V port-labeling bug was invisible to the entire Wave 1 test suite
Despite being physically backwards, the bug produced zero test failures because the mislabeling was applied consistently everywhere it was used.

**Impact:** A full green test suite (12/12 in Wave 1) gave false confidence about physical correctness; it took an independent calibration check unrelated to the existing tests to surface the bug.
**Source:** 09-02-SUMMARY.md

---

### The toy-scale validation matched to 10 orders of magnitude below threshold, not just barely passing
TVD came out at ~3.85e-16 (n=2) and ~5.68e-16 (n=3) against a chosen threshold of 1e-6 — ten orders of magnitude of margin, with zero residual probability in both cases.

**Impact:** Strong quantitative confirmation of the weight-1 mapping's correctness for the tested cases; also created a scientific-notation misreading risk during the checkpoint (see Lessons) precisely because the margin was so large it was easy to misjudge which side of the threshold it landed on.
**Source:** 09-03-SUMMARY.md

---

### The final whole-document checkpoint required five correction rounds across all five required topics
Every one of the five required points in Plan 09-04's final self-explanation checkpoint (scheme choice, commutativity, basis correspondence, n=2-3 result, Douce et al. positioning) needed at least one correction, with basis correspondence needing the most (a repeated reversed port convention, an incomplete invalid-pattern list, and confusion between two different real mechanisms).

**Impact:** Took roughly 45 minutes versus the ~1 hour of implementation work that preceded it — a whole-document checkpoint re-testing everything at once surfaces more/different gaps than the per-section checkpoints that already individually passed.
**Source:** 09-04-SUMMARY.md

---

### The same basis-correspondence weak point resurfaced in an independent re-test weeks/passes later
09-UAT.md's fully independent re-run of the ENC-05 bar found the identical weak spot (basis-correspondence/falsifiability) needed the most correction rounds — consistent with, not just coincidentally similar to, Plan 09-04's own finding.

**Impact:** Indicates a durable comprehension gap on this specific topic rather than a one-off slip, useful signal for where explanation practice would pay off most before an external conversation (e.g., with Vincent Espitalier).
**Source:** 09-UAT.md
