---
status: complete
phase: 09-encoding-design
source: [09-01-SUMMARY.md, 09-02-SUMMARY.md, 09-03-SUMMARY.md, 09-04-SUMMARY.md]
started: 2026-08-05T00:00:00Z
updated: 2026-08-05T00:30:00Z
---

## Current Test

[testing complete]

## Tests

### 1. ENC-01 ingredient-level mapping reads coherently
expected: |
  Opening docs/iqp-photonic-encoding.md and reading the ENC-01 section, you should
  find: the owner's original attempt (with its two corrections: HWP not a beamsplitter,
  CZ not CNOT/SWAP), then an equation-level derivation of WP(theta,0)=diag(e^{i theta},
  e^{-i theta}) and HWP(pi/8) realizing Hadamard up to a global phase, then worked n=2
  and n=3 examples whose numbers match the predicted product distribution.
result: pass
verified_by: claude
evidence: |
  All expected subsections present (Owner's Attempt, Chosen scheme, Ingredients 1-3,
  Commutativity/conjugation-symmetry derivation, n=2 worked example, Relation to
  owner's attempt, Status, Self-Explanation Checkpoint). Live-ran
  run_full_circuit(n=2, thetas=[0.3,1.1]) and expected_joint_distribution: output
  matches the doc's quoted numbers exactly (e.g. HV=0.7248869159124994).

### 2. ENC-03 basis correspondence is bidirectional and falsifiable
expected: |
  The ENC-03 section states the forward map ('0'->H, '1'->V) and reverse map
  ((0,1)->H, (1,0)->V), and explicitly lists all four out-of-subspace patterns
  ((0,0) lost, (1,1) extra photon, (2,0)/(0,2) bunched) with a stated residual-
  reporting policy (report the leftover probability, never silently discard or
  renormalize it away).
result: pass
verified_by: claude
evidence: |
  Live-ran bitstring_to_fock('0'/'1', 1) -> H/V as documented. Live-ran
  fock_to_bitstring on all 4 invalid patterns (0,0)/(1,1)/(2,0)/(0,2): all
  return None as claimed. Valid patterns (0,1)->'0', (1,0)->'1' match the
  doc's stated reverse map exactly. Residual-reporting policy explicitly
  stated in "Reverse Map and Out-of-Subspace Handling" section.

### 3. Weight-1 generator code runs and its tests pass
expected: |
  Running `./venv/Scripts/python.exe -m pytest tests/test_iqp_photonic_encoding.py -v`
  shows all tests passing (26 as of Plan 03; may be more after Plan 04's final pass),
  covering circuit construction, the bitstring<->Fock round trip, and the out-of-
  subspace cases.
result: pass
verified_by: claude
evidence: "Live-ran pytest tests/test_iqp_photonic_encoding.py -v: 26 passed in 10.30s, 0 failed."

### 4. ENC-04 toy-scale validation numbers are real and reproducible
expected: |
  The ENC-04 section in docs/iqp-photonic-encoding.md reports actual computed TVD
  values for n=2 (thetas=[0.3,1.1]) and n=3 (thetas=[0.3,1.1,0.75]) around 1e-16,
  ten orders of magnitude under the stated 1e-6 threshold, with zero residual
  probability in both cases — not a hypothetical or placeholder number.
result: pass
verified_by: claude
evidence: "Live-ran exact_qubit_iqp_distribution/photonic_iqp_distribution/total_variation_distance for both n values: n=2 TVD=3.851e-16, n=3 TVD=5.681e-16, residual=0.0 both — matches doc exactly."

### 5. ENC-02 honestly positions the mapping against Douce et al.
expected: |
  The ENC-02 section states both a favorable contrast (native single-qubit HWP
  conjugation, deterministic, any angle) and an honest parallel (the weight-2
  heralded_cz construction is measurement-conditioned, same character as Douce
  et al.'s post-selected gadget) — not just the flattering half.
result: pass
verified_by: claude
evidence: |
  Read the full ENC-02 section. "How this DV/Fock-space mapping differs" states
  the favorable contrast (HWP(pi/8) native/deterministic vs Douce's post-selected
  gadget). "Where the honest parallel exists" states the parallel explicitly and
  up front ("stating that plainly matters more than the flattering half") — the
  weight-2 heralded_cz construction is probabilistic/measurement-conditioned,
  same character as Douce's Fourier gadget. Both halves genuinely present.

### 6. The document reads as one coherent whole, not four stitched fragments
expected: |
  docs/iqp-photonic-encoding.md has a working intro (scope statement, prerequisite
  reading pointers to docs/iqp-baseline.md and docs/iqp-lit-scoping.md), a table of
  contents, sections in ENC-01 -> ENC-02 -> ENC-03 -> ENC-04 order, and a
  "Conclusion and Open Questions" section that collects every stated limitation
  (weight-2 untested, heralded_cz success probability unverified, toy-check scope,
  general-n scaling not demonstrated) in one place.
result: pass
verified_by: claude
evidence: |
  Intro has What this is/is not, prerequisite reading links to both docs (both
  files confirmed to exist), how-to-read guidance, and a working TOC linking all
  6 sections. Conclusion and Open Questions section collects all four limitations
  named in the expected behavior, verbatim.

### 7. Full test suite is green with no regressions
expected: |
  Running `./venv/Scripts/python.exe -m pytest tests/ -v` from the project root
  shows 85 passed, 0 failed — including both Phase 8's and Phase 9's test files,
  with no regressions in earlier-phase tests (generator/, quickstart, etc.).
result: pass
verified_by: claude
evidence: "Live-ran pytest tests/ -v: 85 passed in 41.15s, 0 failed."

### 8. You can explain the mapping unaided, the same bar as ENC-05
expected: |
  Without looking at the document, you can explain: why the scheme (polarization
  encoding) was chosen, why the diagonal-layer gates commute, the basis
  correspondence rule, what the n=2/3 TVD result does and does not prove, and how
  this differs from Douce et al.'s CV construction — matching the self-explanation
  checkpoint you already passed during Plan 09-04 (documented in 09-04-SUMMARY.md).
result: pass (with correction rounds)
reported: |
  First-pass answers on scheme choice, commutativity, weight-1/weight-2 scope, and
  Douce et al. contrast were all correct and independent (not quoted from the doc).
  Basis-correspondence piece: first response was "Idk what you mean" — taught the
  forward/reverse rule and the four invalid patterns directly, then re-asked.
  Second attempt correctly restated the invalid-pattern enumeration but skipped
  the falsifiability half of the question (why the round trip makes the claim
  checkable, not just plausible). Third attempt ("because we can check we got the
  same input") captured the core idea in minimal form; completed with the explicit
  "what would prove it wrong" framing (the actual H/V-swap bug from Wave 1).
severity: minor
notes: |
  This is this UAT's own independent re-test of the ENC-05 bar, not a citation of
  the prior pass. Owner needed two follow-up rounds specifically on the basis-
  correspondence/falsifiability piece before reaching a correct, own-words answer
  — consistent with 09-04-SUMMARY.md's own record that this was the piece
  requiring the most correction rounds during the original Plan 09-04 checkpoint
  too. Not logged as a Gap (no code/doc defect, no fix plan needed) — recorded
  here per this repo's standing practice of keeping the actual back-and-forth
  visible rather than smoothed into "passed."

## Summary

total: 8
passed: 8
issues: 0
pending: 0
skipped: 0

## Gaps

[none — all 8 tests passed; test 8 required two correction rounds on the
basis-correspondence/falsifiability sub-question but was resolved to a correct,
owner-articulated answer, see test 8's notes]
