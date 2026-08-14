# Phase 18: Hardness-Under-Loss Assessment - Context

**Gathered:** 2026-08-13
**Status:** Ready for planning

<domain>
## Phase Boundary

Measure whether the IQP sampling-hardness argument survives realistic photon loss, using `Processor.probs()` + `pcvl.LC(loss)` component insertion (with explicit `min_detected_photons_filter(0)`) over a defined η grid (never `Analyzer`, which silently ignores loss; never the `NoiseModel(transmittance=η)` constructor path, confirmed to silently no-op for this project's polarization-annotated circuits — see "Literature correction" and mechanism-correction notes below). Grounded in two named literature thresholds — arXiv:2510.24137 (Park & Oh, not Aaronson-Brod — see correction below; read in full first, per HARD-03) and Bremner-Montanaro-Shepherd's depolarizing-noise theorem (arXiv:1610.01808) — with an explicit, stated translation model between photon loss and depolarizing rate rather than an assumed equivalence. Covers weight-1 and weight-2 (mixed) generator scopes. Reported honestly either direction, matching this project's Phase 7/17/17.1 precedent.

</domain>

<decisions>
## Implementation Decisions

### Classically-easy baseline (HARD-05)
- Track TVD-vs-η against **both** a uniform-over-output-states baseline and a product-of-marginals (mean-field) baseline, reported separately rather than picking one.
- Product-of-marginals' per-qubit marginals are computed **once**, from the lossless (η=1) target distribution — not recomputed per η. Isolates "how far does loss alone move the true output toward independence" as a single fixed comparison point across the whole grid.
- No hard numeric crossover threshold (e.g. "TVD-to-baseline < TVD-to-target ⇒ classically easy") is defined in this phase. Report both TVD curves as measured; interpretation is Phase 20's/the owner's job, per this project's honesty-over-narrative convention (Phase 7, Phase 17).
- Both baselines run across the **same n range and both generator scopes** (weight-1, mixed) as the main η-sweep — full coverage, not a narrower representative subset.

### η grid design
- Range: full range down to near-total loss, e.g. η ∈ [0.05, 1.0] — not restricted to a "realistic hardware" subrange. Mirrors TRAIN-09's precedent of measuring the full grid rather than presupposing where the interesting behavior sits; a realistic-loss reading is still extractable as a subset of the same data.
- Spacing: a fixed grid of ~6-8 points, log- or geometrically-spaced denser near η=1 (low loss) — mirrors TRAIN-09's 6-point sigma-grid convention.
- The **same η grid** is used for both weight-1 and mixed scopes (not scope-specific grids) — keeps the two scopes directly comparable.
- Compute approach: best-effort, chunked/resumable execution (Phase 17/17.1's established pattern) — no fixed time-box for this phase, despite the ~2026-08-20 mid-milestone checkpoint being ~1 week out. Report whatever max-n is honestly reached by the checkpoint.

### Weight-2 loss ↔ herald-failure compounding (HARD-07)
- Photon transmittance loss is applied **uniformly across all modes**, including the `heralded_cz` ancilla modes — not just the data-carrying dual-rail modes. This is the only way to see whether loss degrades the herald mechanism itself, not just the post-herald data readout.
- Compounding method: run the **full `Processor.probs()`+`NoiseModel` pipeline through the real `heralded_cz` circuit** so herald failure and transmission loss interact as they physically would. Do NOT analytically multiply the known lossless 2/27 herald-success rate by a separately-computed η-effect — that would assume independence between the two failure modes, which isn't established.
- The weight-2 TVD-vs-η metric is computed **conditioned on herald success** (postselected) — matches this project's existing `heralded_cz` convention and answers the operationally meaningful question ("given the gate reports success, how does output quality degrade with loss").
- The herald-success **rate itself** is also tracked and reported as an explicit function of η (does loss measurably shift the lossless 2/27 baseline) — cheap to extract from the same full-pipeline simulation, directly supports HARD-07's compounding requirement.

### Depolarizing-translation rigor & anticoncentration tracking (HARD-04, HARD-05)
- The η→effective-depolarizing-rate translation is **derived from this project's own circuit failure mechanics** (heralded-CZ/CP(α) failure probabilities and transmittance model) as a project-specific derivation with its own stated assumptions — not a borrowed generic formula, and not left as qualitative-only positioning. Mirrors Phase 15's ARB-02 general-α operator-identity precedent.
- This derivation is a genuinely conceptual/design decision and goes through this project's **attempt-first checkpoint**: the owner sketches/attempts the η→ε mapping before Claude derives it, matching the ARB-02 checkpoint pattern. Planner should schedule this explicitly, not skip it as boilerplate.
- Anticoncentration parameter α(η) (BMS Theorem 4: Σp_x² ≤ α·2⁻ⁿ) is computed **directly/exactly** from the full simulated distribution at each (n, η) — not sampled/estimated. Feasible given this project's demonstrated n range (n≤6-8).
- α(η) is tracked for **both** weight-1 and mixed (weight-2) scopes, not weight-1 only — it's exactly the quantity both the translation model and the write-up's compounded-loss discussion key on.

### Literature correction: arXiv:2510.24137 is not Aaronson-Brod (2026-08-14, discovered during /gsd:plan-phase research)
- `18-RESEARCH.md` found that arXiv:2510.24137 is Park & Oh (KAIST, 2026), "Matrix product state approach to lossy boson sampling and noisy IQP sampling" — not an Aaronson-Brod paper. The real Aaronson-Brod paper ("BosonSampling with Lost Photons," Phys. Rev. A 93, 012335 (2016)) is arXiv:1510.05245, a different paper never read in this project. This is a factual correction to this file's original `<decisions>` framing above, not a scope reduction.
- **Owner decision:** read both papers, keep them clearly separated. HARD-03 remains satisfied by the already-completed full read of Park & Oh (arXiv:2510.24137) — cite its Theorem 1 (the lossy-boson-sampling/passive-linear-optics result, which matches this project's photon-transmittance channel), not its Section V "Noisy IQP Sampling" result (qubit-level Pauli noise, a different channel — see 18-RESEARCH.md Finding 2). HARD-04 additionally requires a real, focused read of the genuine Aaronson-Brod paper (arXiv:1510.05245) so its fixed-loss-count regime is cited from primary-source reading, not inherited from the misattribution. Both papers must be cited explicitly by name/arXiv ID in the write-up so neither is silently substituted for the other.
- Planner: add an explicit task for reading arXiv:1510.05245 (mirrors HARD-03's existing "read before finalizing methodology" pattern) before HARD-04's positioning work is finalized.

### Claude's Discretion
- Exact number of η grid points within the ~6-8 range, and the precise log/geometric spacing formula.
- Chunking/resumability implementation details for the sweep (mirroring Phase 17/17.1's `--draw-start`/`--combine-chunks` pattern).
- Exact max-n target per scope, subject to the same memory constraints documented in `STATE.md` (chunked execution, no concurrent heavy jobs, never kill untracked processes).
- Internal code structure/module layout for the new sweep infrastructure.

</decisions>

<specifics>
## Specific Ideas

- Follow the TRAIN-09 sigma-grid precedent directly: a fixed grid of discrete values (not a continuous schedule), modeled on the same "pick a small set of representative points, run the full n-range at each" pattern that worked for Phase 17.1.
- Follow the ARB-02 attempt-first-checkpoint precedent for the η→depolarizing-rate translation: this is the kind of thing the owner needs to be able to explain unaided to Vincent, per this project's CLAUDE.md.
- The anticoncentration-parameter tracking is explicitly meant to set up Phase 20's WRITE-06 cross-reference against Herbst et al.'s framework (hardness and trainability predicted to co-occur via anticoncentration) — keep α(η) numbers clean and traceable for that later use.

</specifics>

<deferred>
## Deferred Ideas

None — discussion stayed within Phase 18's scope. (HARD-03's literature read, HARD-01/02's core NoiseModel/LossSimulator cross-check, and HARD-06's scope statement weren't discussed here as they're either already-scoped mechanical steps or don't have open gray areas requiring the owner's input.)

</deferred>

---

*Phase: 18-hardness-under-loss-assessment*
*Context gathered: 2026-08-13*
