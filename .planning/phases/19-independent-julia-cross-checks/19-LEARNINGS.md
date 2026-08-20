---
phase: 19
phase_name: "Independent Julia Cross-Checks"
project: "MerLin Photonic Generative Modeling"
generated: "2026-08-20"
counts:
  decisions: 6
  lessons: 5
  patterns: 6
  surprises: 4
missing_artifacts: ["UAT.md"]
---

# Phase 19 Learnings: Independent Julia Cross-Checks

## Decisions

### CSV reference bridge with self-documenting headers
Python-generated reference distributions are written as plain 2-column `bitstring,probability` CSVs with `# key=value` header comment lines recording every literal input value (thetas, eta, residual, herald_failure_prob, global_perf) a downstream Julia script needs to reproduce the exact same circuit instance.

**Rationale:** Downstream Julia scripts need the literal circuit parameters, not just the output distribution, to construct an independent circuit that is genuinely comparable rather than accidentally different.
**Source:** .planning/phases/19-independent-julia-cross-checks/19-01-SUMMARY.md

---

### Independent builds from library primitives, never mechanical ports
VERIFY-03's Julia circuits were required to be built independently from BosonSampling.jl's/Yao.jl's own API and idioms, not ported from Perceval's circuit structure — even reusing the same test inputs (Fock states, params) for direct numeric comparability.

**Rationale:** A mechanical port would replay the same bug in two languages instead of providing a real independence check; this was framed as the single most load-bearing decision in the phase.
**Source:** .planning/phases/19-independent-julia-cross-checks/19-CONTEXT.md

---

### Locked tight tolerance (TVD ≤ 1e-6) across all legs, including loss
The owner explicitly chose not to loosen the TVD tolerance for the lossy-distribution comparison (VERIFY-04), keeping the same bar used for the exact-case checks (VERIFY-02/03).

**Rationale:** Both sides of every comparison are exact, non-sampling computations, so a tight bar is achievable and was deliberately kept uniform.
**Source:** .planning/phases/19-independent-julia-cross-checks/19-CONTEXT.md

---

### Used BosonSampling.jl's native loss API, not hand-attenuation
VERIFY-04 used `UniformLossInterferometer`, BosonSampling.jl's own native loss/noise API, confirmed usable against the actually-installed v1.0.2 depot source (not GitHub main), rather than falling back to hand-attenuating the exact distribution.

**Rationale:** A native independently-implemented loss mechanism is a stronger independence guarantee than replaying Perceval's loss math in Julia; CONTEXT.md left the fallback decision to Claude's discretion only if no native API existed, and the investigation succeeded within budget.
**Source:** .planning/phases/19-independent-julia-cross-checks/19-05-SUMMARY.md

---

### Sourced the Knill CZ gate matrix from the primary paper, never from Perceval's own circuit
The heralded-CZ unitary was fetched directly from arXiv:quant-ph/0110144 Eq. 11 (both PDF and LaTeX source, to eliminate OCR/transcription risk), explicitly avoiding the anti-pattern of extracting it from Perceval's own already-built `heralded_cz` circuit.

**Rationale:** Sourcing the gate from Perceval's own implementation would make the "independent" cross-check circular; 19-RESEARCH.md flagged this as an anti-pattern to avoid.
**Source:** .planning/phases/19-independent-julia-cross-checks/19-04-SUMMARY.md

---

### VERIFY-02/03/04 marked Complete, not Partial
Since every leg (VERIFY-02, VERIFY-03 weight-1, VERIFY-03 weight-2, VERIFY-04) reached a full, measured GO verdict with no unresolved disagreement, REQUIREMENTS.md's rows were corrected directly from Pending to Complete rather than Partial.

**Rationale:** CONTEXT.md's own disagreement-handling framing treats a documented, time-boxed disagreement as an acceptable Complete outcome, but none occurred — the one real bug found (weight-2 transpose issue) was resolved inside the time-box, so it counts as a genuine GO.
**Source:** .planning/phases/19-independent-julia-cross-checks/19-06-SUMMARY.md

---

## Lessons

### numpy float64 repr() silently corrupts downstream CSV parsers
Several upstream distribution functions (`exact_qubit_iqp_distribution`, `photonic_iqp_distribution`, `photonic_weight2_iqp_distribution`) return `np.float64` values; writing `repr()` on them directly produced strings like `np.float64(0.123...)` instead of bare floats, which would have silently broken every downstream Julia CSV parse.

**Context:** Caught by inspecting the first generated `qubit_n2.csv` before committing, not assumed correct; fixed by explicitly casting every written value through `float(...)` first.
**Source:** .planning/phases/19-independent-julia-cross-checks/19-01-SUMMARY.md

---

### BosonSampling.jl's eta is a transmission amplitude, not a transmission probability
`UniformLossInterferometer(eta, U)` treats `eta` as a transmission amplitude (transmission probability = eta²), while this repo's Python-side `eta` is a transmission probability directly.

**Context:** Resolved by passing `sqrt(eta)`, verified (not assumed) via an n=1 closed-form sanity check (`p(survive)=eta`, `p(lost)=1-eta`) at all 3 tested eta values before trusting the n=2 comparison.
**Source:** .planning/phases/19-independent-julia-cross-checks/19-05-SUMMARY.md

---

### Installed BosonSampling.jl v1.0.2 has a real dispatch gap for its own native loss type
Constructing an `Event` directly against a `UniformLossInterferometer` raises `MethodError: no method matching LossParameters(::Type{UniformLossInterferometer})` — the installed package never registered this method for its own type (unlike `RandomPhaseShifter`, `LosslessLoop`, `LossyBeamSplitter`).

**Context:** Confirmed live via a standalone repro before writing any workaround, not inferred from source reading alone; worked around by wrapping the interferometer's own computed `.U` field in `UserDefinedInterferometer(li.U)`, which changes nothing about the loss physics since `compute_probability!` only ever reads `.U`.
**Source:** .planning/phases/19-independent-julia-cross-checks/19-05-SUMMARY.md

---

### A degenerate/symmetric test case cannot rule out certain convention-mismatch bug classes
The original locked weight-2 test case used `thetas=[0,0]`, producing a distribution (`P(01)=P(10)=0`, `P(00)=P(11)≈0.5`) symmetric enough that a hidden Julia/Python bit-to-rail convention error could in principle produce the same-looking passing result — the test could not distinguish a correct implementation from a specific class of bug.

**Context:** Surfaced by an independent Codex (gpt-5.5) review the owner requested of the earlier transpose-bug fix, applied as a gap-closure follow-up after Plan 19-04 originally shipped. Fixed by adding an asymmetric-theta case (`thetas=[0.3, 1.1]`), which does catch a single-qubit rail-convention error the locked case could not.
**Source:** results/phase19_verify03_weight2_results.md

---

### Even a proven-closed residual ambiguity should be verified against a primary source, not left as a hedge
After adding the asymmetric-theta case, a hand derivation suggested `P(00)=P(11)` and `P(01)=P(10)` hold for *every* `theta_i`/`theta_j` in this circuit — meaning a simultaneous both-qubit bit-flip or qubit-order swap remains undetectable by symmetry alone, regardless of theta choice.

**Context:** This was converted from a hand-wavy observation into an actual proof by checking it against Hein, Eisert & Briegel's graph-state paper (Phys. Rev. A 69, 062311 (2004), arXiv:quant-ph/0307130) — verified directly against the primary source, not accepted from an AI-provided citation. Their Eq. (41) reduced-state formula confirms each qubit's marginal is exactly maximally mixed (I/2) for any theta, explaining and bounding exactly which residual ambiguity is structurally unresolvable versus which was closed by the new test case.
**Source:** results/phase19_verify03_weight2_results.md

---

## Patterns

### Two-candidate empirical bit-ordering test
When a target library's basis-index convention is uncertain, build an asymmetric-parameter circuit with an independently-known closed-form per-qubit marginal, test both plausible orderings (e.g. "qubit = LSB" vs "qubit = MSB") against it, and hard-assert exactly one candidate matches — never assume the convention from prior documentation or a comment alone.

**When to use:** Any time a second language/library's basis-index or bit-ordering convention needs confirming before it can be trusted in a larger circuit comparison.
**Source:** .planning/phases/19-independent-julia-cross-checks/19-02-SUMMARY.md

---

### Verify a literature-sourced gate matrix against the paper's own stated exact constraints before embedding it
Before trusting a gate matrix pulled from a paper in a larger circuit, build a standalone diagnostic that checks it against constraints the paper itself proves must hold exactly (here: Knill's Eq. 6 zero-leak identities) — this isolates convention bugs (transpose, sign, mode ordering) from downstream composition bugs immediately, rather than debugging a full multi-mode circuit's TVD mismatch as one large search space.

**When to use:** Any time a gate/operator matrix is sourced from external literature for use in a larger independently-built pipeline.
**Source:** .planning/phases/19-independent-julia-cross-checks/19-04-SUMMARY.md

---

### Eliminate transcription risk by fetching both PDF and LaTeX source for a cited paper
When sourcing a matrix or formula from a paper, fetch both the PDF and the LaTeX e-print source and confirm the transcribed value byte-for-byte before debugging begins — this rules out OCR/transcription error as a possible cause and lets debugging focus on genuine convention mismatches.

**When to use:** Any time a numerical result (gate matrix, formula) is transcribed from an external paper into code.
**Source:** .planning/phases/19-independent-julia-cross-checks/19-04-SUMMARY.md

---

### Exact doubled-mode marginalization via conserved-quantity enumeration
When a native library API produces virtual/doubled-mode output states that need marginalizing to physical modes, and the underlying transform is unitary (so a quantity like total photon count is exactly conserved), enumerate every composition of that conserved quantity across the virtual mode space and bucket results by the physical-mode sub-pattern — giving an exact marginal without sampling or relying on unverified library abstractions.

**When to use:** When a library's loss/noise or ancilla-expansion feature returns state in an expanded mode space and the exact physical-mode marginal is needed, and unfamiliar library helper functions for marginalization exist but have unverified semantics.
**Source:** .planning/phases/19-independent-julia-cross-checks/19-05-SUMMARY.md

---

### Route around a missing type-dispatch method by wrapping the computed output in a sibling type
When an installed package's own `MethodError` reveals a missing type-specific method registration, verify the failure live with a minimal standalone repro first, then work around it by wrapping the struct's own already-computed output field in a sibling type that does have the needed dispatch — preserving the original computation while avoiding the unrelated API gap.

**When to use:** When a third-party library has an internal dispatch/registration gap for one of its own types, confirmed live (not assumed from reading source), and the actual computed data is otherwise correct and reusable.
**Source:** .planning/phases/19-independent-julia-cross-checks/19-05-SUMMARY.md

---

### When a symmetric/degenerate test case can't rule out a bug class, add an asymmetric case and prove the residual against a primary source
If a test case's output happens to be invariant under the specific transformation a suspected bug class would apply (e.g. bit-relabeling, rail-swap), that test cannot distinguish correct from incorrectly-labeled results. Add a case with distinct, nonzero parameters that breaks the invariance, and if any residual ambiguity remains even then, prove — via a primary literature source, not just hand-waving — exactly which symmetry is structural (and thus permanently untestable by this method) versus which was actually closed by the new case.

**When to use:** Any cross-check or verification test whose initial parameter choice (zeros, defaults, symmetric angles) may accidentally produce a distribution invariant under the exact error mode being guarded against.
**Source:** results/phase19_verify03_weight2_results.md

---

## Surprises

### A real Knill-CZ matrix transpose-convention bug was found and fixed, not just a benign near-miss
The paper's own Eq. 11 matrix, used exactly as printed, produced ~0.033 probability leakage into bunched outputs that Knill's own Eq. 6 proves should be exactly zero. Root cause: the paper defines its matrix via `V_rs = u_sr` (a transpose convention) differing from BosonSampling.jl's `UserDefinedInterferometer` expected orientation.

**Impact:** This was the phase's flagged highest-stall-risk piece, and it did not stall — the bug was diagnosed via a standalone zero-leak check and fixed (transposing the matrix) within the same session, dropping leak terms from ~0.033 to ~1e-32 and yielding a full GO (TVD=3.5e-15), confirmed via external review as a legitimate fix.
**Source:** .planning/phases/19-independent-julia-cross-checks/19-04-SUMMARY.md; results/phase19_verify03_weight2_results.md

---

### BosonSampling.jl v1.0.2's own native loss type has a missing dispatch registration
`Event()` cannot be constructed directly against a `UniformLossInterferometer` because the installed package never registered a `LossParameters` method for its own type — a genuine package gap, not caller error.

**Impact:** Required a documented workaround (wrapping `.U` in `UserDefinedInterferometer`) but did not block VERIFY-04 from reaching a full GO using the native loss API rather than falling back to hand-attenuation.
**Source:** .planning/phases/19-independent-julia-cross-checks/19-05-SUMMARY.md

---

### The weight-2 leg's own original test case was too symmetric to catch the bug class it existed to catch
`thetas=[0,0]` produced a distribution symmetric enough that a hidden bit-to-rail convention error could have produced the same passing result — meaning the cross-check, as originally shipped, could not fully rule out the class of bug it was designed to guard against.

**Impact:** Surfaced only via an independent Codex (gpt-5.5) review requested after the plan originally shipped, not caught during the phase's own execution or verification pass; required a gap-closure follow-up (an asymmetric-theta case plus a primary-source proof) added after Plan 19-04 and the phase's initial VERIFICATION.md.
**Source:** results/phase19_verify03_weight2_results.md

---

### A hand-derived symmetry observation converted into a rigorous proof via a primary source, not just accepted as intuition
The suspicion that `P(00)=P(11)` and `P(01)=P(10)` hold for *any* theta (making a specific residual ambiguity permanently untestable by this method) was independently checked against Hein, Eisert & Briegel's graph-state paper (Phys. Rev. A 69, 062311 (2004)) rather than left as an unverified hand-wave or an AI-asserted citation.

**Impact:** Converts a "we think this residual gap is unavoidable" hedge into a documented, source-verified structural limit, giving the phase's final write-up an honest and precisely-bounded scope statement rather than an overclaimed or underclaimed one.
**Source:** results/phase19_verify03_weight2_results.md

---
