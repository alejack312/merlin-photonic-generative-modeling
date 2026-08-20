---
phase: 18
phase_name: "Hardness-Under-Loss Assessment"
project: "MerLin Photonic Generative Modeling"
generated: "2026-08-20"
counts:
  decisions: 7
  lessons: 6
  patterns: 5
  surprises: 5
missing_artifacts: []
---

# Phase 18 Learnings: Hardness-Under-Loss Assessment

## Decisions

### Cite Park & Oh's Theorem 1, not its Section V
Cited Park & Oh (arXiv:2510.24137) Theorem 1 (lossy-boson-sampling/passive-linear-optics, eta=Theta(1/sqrt(N))) as the physically-matching hardness result, explicitly excluding the same paper's Section V ("Noisy IQP Sampling," qubit-level Pauli noise) despite its more tempting "IQP" label.

**Rationale:** The two results live under different noise channels in the same paper; only Theorem 1 physically matches this project's photon-loss mechanism. Stating the exclusion explicitly in the doc prevents a future reader (or a later phase's write-up) from citing the wrong half of the paper.
**Source:** 18-01-SUMMARY.md

---

### State the Aaronson-Brod fixed-k-vs-fractional-eta mismatch plainly, using the paper's own words
Rather than asserting or implying a translation, quoted Aaronson-Brod's own discussion (pp.4, 9) of how their fixed-loss-count guarantee weakens as k scales with n, and flagged that this project's fixed-eta-as-n-grows regime falls into the paper's own "weak, no strong complexity claims" case.

**Rationale:** The mismatch is a fact from the source text, not an inference Claude introduced — recording it verbatim avoids silently overstating what the citation supports.
**Source:** 18-01-SUMMARY.md

---

### Use pcvl.LC(loss) + explicit min_detected_photons_filter(0) as the only loss mechanism, never NoiseModel(...) for polarization circuits
Adopted 18-RESEARCH.md's verified code skeleton exactly for both weight-1 and weight-2 loss primitives: LC front-loaded on every mode (including ancilla modes for weight-2) before circuit construction, with min_detected_photons_filter(0) called explicitly every time.

**Rationale:** NoiseModel(transmittance=eta) silently no-ops on polarization-annotated circuits, and omitting the filter silently discards all lossy branches — both produce plausible-looking but loss-invariant output. LC+filter was proven (regression-tested), not assumed, to actually respond to eta.
**Source:** 18-02-SUMMARY.md, 18-03-SUMMARY.md

---

### Measure herald-failure/loss compounding via one real Processor.probs() call, never an analytical product
For the weight-2 primitive, herald_failure_prob and transmission loss are read off a single real simulator call rather than computed as (lossless herald rate) x (per-mode survival probability).

**Rationale:** The naive analytical decomposition was directly measured to diverge from the real compounded value by several orders of magnitude past the 1e-6 tolerance at every non-lossless eta tested — the shortcut CONTEXT.md forbids is demonstrably wrong, not just theoretically suspect.
**Source:** 18-03-SUMMARY.md

---

### Decline to fabricate an eta-to-epsilon (depolarizing) translation; position against loss-native regimes instead
At the HARD-04 attempt-first checkpoint, the owner rejected all three candidate translation directions (erasure-as-depolarizing, compounded-gate-failure-rate, fitted-effective-channel) because deriving one rigorously (e.g. diamond-norm-closest-depolarizing-channel) would be unowned original numerics research outside project scope. Positioned the tested ETA_GRID instead against two loss-native regimes: Aaronson-Brod's fixed-photon-count regime (via a simple explicit N*(1-eta) expected-lost-photon-count translation) and arXiv:2511.07853's logarithmic-loss-fraction regime. BMS was kept qualitative-only as a consequence.

**Rationale:** Stating "no translation exists / declined to fabricate one" honestly is more defensible than inventing a numeric bridge the project can't own or explain. This is the phase's central owner-level judgment call, recorded verbatim in the doc.
**Source:** 18-08-SUMMARY.md

---

### Do not create hardness/depolarizing_translation.py as a placeholder
The plan anticipated two outcomes (closed-form function, or documented "no closed form"); the actual outcome was a third case — no translation attempted at all — so no code artifact was created.

**Rationale:** A placeholder or trivial stub function would misrepresent the decision as more resolved than it actually is.
**Source:** 18-08-SUMMARY.md, 18-VERIFICATION.md (Anti-Patterns Found)

---

### Delete a zero-row stretch CSV rather than leave it on disk
The mixed n=5 stretch attempt crashed before writing any row; the resulting header-only CSV was deleted, and the outcome documented in prose instead.

**Rationale:** An empty CSV could be mistaken by a future glob/analysis script for a real (if empty) dataset. Matches Phase 17's own precedent of not producing a stretch CSV when a stretch attempt fails before any data is written.
**Source:** 18-06-SUMMARY.md

---

## Lessons

### NoiseModel silently no-ops on polarization-annotated circuits
Passing noise=NoiseModel(transmittance=eta) to a Processor built from this project's polarization-annotated circuits produces output that does not change with eta — a plausible-looking but entirely loss-invariant result, with no error raised.

**Context:** Discovered/confirmed while building the weight-1 loss primitive (18-02) and reconfirmed for weight-2 (18-03); this is the first of three separate silent-no-op failure modes found in this phase (see Surprises).
**Source:** 18-02-SUMMARY.md, 18-RESEARCH.md (referenced in 18-02/18-03 tech-stack sections)

---

### Omitting min_detected_photons_filter(0) silently discards every lossy branch
Even when using the correct pcvl.LC(loss) mechanism, forgetting the explicit min_detected_photons_filter(0) call causes the resulting distribution to stay pinned at its lossless value across every eta — the "herald-success-rate never moves off 2/27" symptom research had flagged as a warning sign.

**Context:** Proven via a deliberately-broken test helper in both 18-02 (weight-1) and 18-03 (weight-2): the broken helper is loss-invariant (identical dist at eta=1.0 and eta=0.3), while the correct function's dist genuinely differs (TVD > 0.05).
**Source:** 18-02-SUMMARY.md, 18-03-SUMMARY.md

---

### Real per-cell compute cost can diverge wildly from research-note extrapolation
18-RESEARCH.md's n=4 timing (0.07s/cell, "trivial") predicted tractability "likely beyond" n=6 based on 3^n output-state growth. The real machine-measured n=6 cost was ~133s/cell — about 1900x the n=4 figure over only 2 n-steps (~43x per n-step), i.e. wall-time growth was not flat relative to the 3^n state-count argument.

**Context:** Discovered during Plan 18-05's pre-commit timing probe, run specifically to avoid committing compute budget on an extrapolated (not measured) estimate; reported honestly rather than smoothed over, per the project's established honesty-over-narrative convention.
**Source:** 18-05-SUMMARY.md

---

### A single-call MemoryError is a different failure mode from a cross-call memory leak, and draw-chunking cannot fix it
Mixed-scope n=5 reproducibly raised MemoryError inside Processor.probs()'s first call in a fresh process with ~5.16GB free memory, confirmed on 3 independent attempts across different eta values and different free-memory conditions. This is mechanically distinct from Phase 17's own mixed-n=5 MemoryError, which was a cross-call leak across ~600 repeated calls within one process and was fixed there by draw-chunking.

**Context:** Discovered in Plan 18-05's timing probe and reconfirmed twice more in Plan 18-06; because the failure occurs before any result is produced on the very first call, chunking (which amortizes across many calls) provides no mitigation.
**Source:** 18-05-SUMMARY.md, 18-06-SUMMARY.md

---

### Verify every cross-baseline numeric coincidence claim against the source CSV before writing it into a doc
Two claims in the write-up's first draft were wrong until re-checked: (1) a claim that tvd_to_uniform (not just tvd_to_product_marginals) matched tvd_to_lossless at eta=0.99 for weight-1 — false (0.5726 vs 0.0100 at n=2, only the product-marginals match holds, because weight-1 has no entangling gate so its lossless output already factors as a product distribution); (2) 2/27 (heralded_cz's lossless success rate) was mistyped as 0.09259 instead of 0.07407 in an early draft, confusing it with the herald failure rate (25/27 ≈ 0.9259).

**Context:** Both errors were caught and fixed before commit during Plan 18-07's write-up drafting, not left as errors in shipped docs.
**Source:** 18-07-SUMMARY.md

---

### A bare `git commit -m` trusts whatever is currently staged, not just the paths you most recently added
Because concurrent sessions were staging files into a shared git index, `git commit -m` (without an explicit pathspec) swept in other sessions' already-staged files even when only specific files were intentionally `git add`-ed beforehand.

**Context:** Observed in Plan 18-04 when another concurrent session's `tests/test_loss_model.py` (Plan 18-02's RED-phase file) landed inside Plan 18-04's own GREEN commit. No content was lost, but commit attribution was mixed. The plan's own recorded lesson: always re-run `git status --short` immediately before `git commit`, or commit with an explicit pathspec, never a bare `git commit -m` that trusts the index's current contents.
**Source:** 18-04-SUMMARY.md

---

## Patterns

### LC-component insertion + explicit filter for photon loss on polarization circuits
Insert pcvl.LC(1-eta) on every mode a Processor exposes (front-loaded, before any other component) and always call proc.min_detected_photons_filter(0) explicitly afterward. Never use the noise=NoiseModel(...) constructor parameter on a polarization-annotated circuit.

**When to use:** Any future Processor built on this project's polarization circuits that needs to simulate photon loss.
**Source:** 18-02-SUMMARY.md (tech-stack patterns), 18-VERIFICATION.md

---

### Ancilla-inclusive loss coverage, structurally proven via component introspection
For any weight-2/ancilla-bearing loss primitive, front-load LC on every mode the outer Processor exposes — data modes and ancilla modes alike — and prove ancilla coverage by inspecting the constructed Processor's `.components` list directly (a dedicated structural test), not just by observing a numeric side effect.

**When to use:** Any future herald/ancilla-based photonic circuit that needs a loss model; use a private `_build_*_processor_lossy` helper returning `(proc, herald_spec)` to give the structural test a clean introspection point, mirroring the existing build_*/no_herald split pattern in iqp_photonic_encoding.py.
**Source:** 18-03-SUMMARY.md

---

### Real, machine-measured timing probes before locking a compute-heavy sweep's n-range
Before committing to an n-range for a compute-heavy sweep, run the CLI's own chunk mode to measure real single-cell wall time at the target sizes, then record an explicit, unambiguous "Final n-range decision" in a results doc that the next plan follows without re-deriving.

**When to use:** Any future phase with a parameter sweep whose per-cell cost is uncertain or extrapolated from smaller sizes — especially when a research note's extrapolation might not hold (see the n=6 timing surprise below).
**Source:** 18-05-SUMMARY.md

---

### Raw-array-now-summarize-later chunking, with per-n (not just per-draw) granularity for memory-constrained runs
Mirrors trainability/sweep.py::pooled_gradients_for_cell: a per-cell function returns (summary, raw), raw is saved to .npy per chunk, and a separate combine function re-summarizes once all chunks exist. Extended in this phase with a coarser per-n chunking granularity (running each n as a separate CLI invocation) on top of the existing draw-range chunking, to bound per-process memory growth.

**When to use:** Any future compute-heavy sweep on this machine's memory-constrained hardware, especially when per-cell cost grows steeply with n.
**Source:** 18-05-SUMMARY.md, 18-06-SUMMARY.md

---

### When a cross-noise-model translation would itself be unowned original research, reposition against noise-native regimes instead of fabricating a bridge
Rather than deriving a numeric translation between this project's photon-loss model and a differently-modeled hardness result (e.g. depolarizing-rate thresholds), state the absence of an established translation explicitly and compare the tested parameter range directly against literature results that use the same native noise type (fixed-photon-count, loss-fraction), flagging structurally different photonic models (e.g. Gaussian boson sampling vs. discrete Fock-state) as such rather than assuming transferability.

**When to use:** Any future phase where positioning this project's results against a literature hardness threshold would require inventing a cross-model noise translation not established in the literature.
**Source:** 18-08-SUMMARY.md

---

## Surprises

### The same silent no-op failure mode appeared three separate times in one phase
(1) An unspecified Analyzer-based approach was known ahead of time to silently ignore loss (per the phase goal statement itself); (2) Processor(noise=NoiseModel(transmittance)) was found to silently no-op for polarization-annotated circuits; (3) omitting an explicit min_detected_photons_filter(0) was found to silently discard every lossy branch, producing loss-invariant but plausible-looking results.

**Impact:** Each of the three had to be independently proven-not-assumed avoided via dedicated regression tests before the phase's core measurement could be trusted; this shaped the phase's central methodology (LC + explicit filter, verified by tests, not just described in prose).
**Source:** 18-VERIFICATION.md, 18-02-SUMMARY.md, 18-03-SUMMARY.md

---

### arXiv:2510.24137 was misattributed as "Aaronson-Brod" before this phase corrected it
18-CONTEXT.md's original framing had misattributed arXiv:2510.24137 (Park & Oh) as the Aaronson-Brod paper. The genuine Aaronson-Brod paper (arXiv:1510.05245) had never actually been read in this project before Plan 18-01.

**Impact:** Corrected before the misattribution could propagate into the phase's central hardness-positioning argument (HARD-04) or the final technical write-up; both papers are now cited separately with an explicit "must never be merged" sentence.
**Source:** 18-01-SUMMARY.md

---

### Weight-1 wall-time growth from n=4 to n=6 was ~1900x, not flat relative to 3^n state growth
18-RESEARCH.md's n=4 measurement (0.07s/cell) and its 3^n-output-state-growth argument predicted tractability "likely beyond" n=6. The real measured n=6 cost (~133s/cell) was roughly 43x per n-step, far outside what the research note's model suggested.

**Impact:** Forced Plan 18-05 to run a dedicated timing probe rather than trust the extrapolation, and to explicitly skip a planned n=7 stretch attempt since the plan's own stated stretch condition ("if n=6 is fast, also try n=7") no longer held.
**Source:** 18-05-SUMMARY.md

---

### Mixed-scope n=5 is a hard, reproducible single-call memory ceiling, not a fixable leak
Confirmed three independent times (2 in the timing probe at different eta values, 1 more in the real sweep at different free-memory conditions) that Processor.probs() raises MemoryError on its very first call for mixed-scope n=5, regardless of available free memory (~5.16GB in one case, ~2.5GB in another) — ruling out both "just needs more memory headroom" and "chunking will fix it" as hypotheses.

**Impact:** Mixed scope's usable range was locked at n=2..4 for the rest of the phase and flagged for later phases (Phase 19's VERIFY-04) not to expect n=5 data to ever arrive under the current pipeline.
**Source:** 18-05-SUMMARY.md, 18-06-SUMMARY.md

---

### Multiple phase-runner sessions operated on the same working directory concurrently, causing repeated commit-attribution mixing
Across Plans 18-01 through 18-04, files from one plan's work (RED-phase test files, SUMMARY.md files, STATE.md updates) repeatedly landed inside another plan's commits due to a git-index race between concurrent sessions' `git add`/`git commit` calls — observed and independently reconfirmed in essentially every commit made during the wave-1 concurrent window.

**Impact:** No data was lost or corrupted in any instance (each SUMMARY cross-checked content integrity), but attribution was mixed repeatedly; flagged three separate times (18-02, 18-03, 18-04 SUMMARYs) as an owner-visible operational concern worth confirming was intentional.
**Source:** 18-02-SUMMARY.md, 18-03-SUMMARY.md, 18-04-SUMMARY.md

---
