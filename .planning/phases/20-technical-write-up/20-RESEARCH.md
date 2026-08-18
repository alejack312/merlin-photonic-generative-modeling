# Phase 20: Technical Write-Up - Research

**Researched:** 2026-08-18
**Domain:** Documentation synthesis / technical-writing structure (no new code, no new experiments) — organizing already-shipped results from Phases 15-19 into a literature-grounded findings document
**Confidence:** HIGH (this is reconnaissance of the repo's own existing content, not external-library research; every claim below is a direct read of a file already in this repo)

## Summary

Phase 20 is pure documentation synthesis: the three source docs (`docs/trainability-study.md`, `docs/hardness-under-loss-study.md`, `docs/iqp-photonic-encoding.md`'s ARB-01/ARB-02 section) already exist, are already extremely disciplined about methodology-before-results structure, already cite specific scripts/CSVs for every number, and two of the three already have recorded self-explanation checkpoints. The actual net-new work is narrower than the phase's requirement list makes it look:

1. **One genuinely open task**: TRAIN-07's owner interpretation is a literal `[pending]` placeholder at `docs/trainability-study.md:174` — this must be filled via a real, unaided self-explanation checkpoint (not written by Claude).
2. **Three new literature-comparison tables** (TRAIN, HARD, ARB) — the raw material for most rows already exists in the repo's own prior citations (`docs/iqp-baseline.md`, `docs/hardness-under-loss-study.md`'s HARD-04 section, `docs/iqp-photonic-encoding.md`'s ARB-01 section), but the verdict cells (consistent/inconsistent/silent) are the owner's/planner's interpretive call, not something to derive here. Two baselines (McClean et al., and to a lesser degree arXiv:2405.01395/arXiv:2510.24137) have never been read as a primary source in this repo — flagged as a real gap requiring either a primary-source fetch during Phase 20 execution or an explicit "silent, not independently verified" framing.
3. **Two short Herbst-et-al. cross-reference notes**, one in each of `trainability-study.md`'s and `hardness-under-loss-study.md`'s existing "what this does/doesn't establish" sections — the underlying prediction and its Phase 17/18 relevance is already spelled out in `docs/iqp-baseline.md`'s Fresh Primary-Source Verification section (2026-08-12), so this is a linking/synthesis task, not new research.
4. **A new synthesis doc** (`docs/technical-findings.md`) that mirrors the three tables and points at the two source docs' scope sections — largely a structuring/summarizing task once the above exist.

**Primary recommendation:** Sequence the plan so the TRAIN-07 self-explanation checkpoint happens *before* the TRAIN literature table is drafted (the table's own weight1/uniform-vs-mixed/uniform row depends on that interpretation being on record), then treat the three source-doc edits (tables + Herbst notes) as three independent, file-scoped waves that can run in parallel since they touch three different files, and make `docs/technical-findings.md` the final wave since it depends on all three source docs being updated first.

## Source Document Current State

### `docs/trainability-study.md` (548 lines)

Existing top-level structure (exact headings, with line numbers):

| Line | Heading |
|---|---|
| 1 | `# Trainability / barren-plateau study (Phase 17)` |
| 9 | `## Methodology` |
| 38 | `## Parameter-initialization and normalization (TRAIN-03)` |
| 53 | `## Generator scope (TRAIN-04)` |
| 72 | `## Results` |
| 101 | `## Honest max-n statement (TRAIN-05, TRAIN-08)` |
| 152 | `## Cross-reference verdict (TRAIN-07)` |
| 176 | `## Bandwidth sensitivity follow-up (TRAIN-09)` |
| 283 | `## Data-dependent initialization follow-up (TRAIN-10)` |
| 340 | `## Independent cross-check: dual-rail encoding + MerLin native autograd` |
| 480 | `### Follow-up experiments (post-cross-check)` |
| 522 | `## What this does/doesn't establish` |

**Insertion points:**
- **(a) Literature comparison table** → the `## What this does/doesn't establish` section (line 522-548) is the natural home, matching the locked decision ("next to that doc's existing 'what this does/doesn't establish' section"). This section currently ends at line 548 with the "Phase 17.1 addendum" paragraph — a new `### Literature comparison` (or similar) subsection can be appended after line 548, or inserted as its own `##` section immediately before "What this does/doesn't establish" if the planner prefers the table to precede the scope paragraph rather than follow it.
- **(b) Herbst et al. cross-reference note** → same section (`## What this does/doesn't establish`, line 522). This section already discusses "what a measured exponential-decay signature does/doesn't establish" — a short paragraph pointing at `docs/hardness-under-loss-study.md`'s equivalent section fits naturally as an additional paragraph here, or as its own short subsection.
- **(c) "What this does/doesn't establish" scope paragraph** → **already exists in full** at line 522-548 (`## What this does/doesn't establish` + the "Phase 17.1 addendum" paragraph). WRITE-04 is already satisfied for TRAIN structurally; Phase 20's job here is only to append the Herbst cross-reference, not create the section from scratch.

### `docs/hardness-under-loss-study.md` (569 lines)

Existing top-level structure:

| Line | Heading |
|---|---|
| 1 | `# Hardness-under-loss study (Phase 18)` |
| 14 | `## Methodology` |
| 120 | `## HARD-01 / HARD-02: loss sweep mechanism and cross-check` |
| 140 | `## HARD-05 results: TVD vs eta (weight-1 and mixed)` |
| 213 | `## Anticoncentration results: alpha(eta)` |
| 245 | `## HARD-07 results: weight-2 herald compounding` |
| 296 | `## MerLin dual-rail parallel` |
| 340 | `### What agrees, and what does not` |
| 362 | `## HARD-04/HARD-06: Positioning and Scope Statement (Plan 18-08)` |
| 364 | `### Owner's attempt-first response (recorded as-given...)` |
| 425 | `### Verifying arXiv:2511.07853 ... directly` |
| 463 | `### Dual/triple positioning: where this project's tested eta range actually sits` |
| 534 | `### HARD-06: What this phase does and does not establish` |

**Insertion points:**
- **(a) Literature comparison table** → `### HARD-06: What this phase does and does not establish` (line 534-569) is the natural anchor. This subsection already discusses scope relative to Aaronson-Brod, BMS, and arXiv:2511.07853 in prose; a formal table (with the locked consistent/inconsistent/silent columns) can be added either immediately before or after this subsection, inside the parent `## HARD-04/HARD-06` section.
- **(b) Herbst et al. cross-reference note** → same subsection (line 534). Points at `docs/trainability-study.md`'s equivalent note. The doc's Anticoncentration section (line 213-243) is also a plausible secondary anchor since it's where `alpha(eta)` — the exact quantity Herbst et al.'s prediction keys on — is reported, but the locked decision specifies "existing scope sections," so `### HARD-06` is the primary target.
- **(c) "What this does/doesn't establish" scope paragraph** → **already exists in full** at line 534-569 (`### HARD-06: What this phase does and does not establish`), with an explicit bulleted "It does **not**:" list. WRITE-04 is already satisfied structurally for HARD.

Note: `docs/hardness-under-loss-study.md`'s own header (line 9-12) states this doc "does not yet contain HARD-04's depolarizing-translation positioning or HARD-06's final scope statement" — that note is **stale**; both sections were in fact added by Plan 18-08 (visible at lines 362-569). Worth a one-line cleanup during Phase 20 if the planner wants the doc internally consistent, though not itself a WRITE-01..06 requirement.

### `docs/iqp-photonic-encoding.md` — ARB-01/ARB-02 section (full doc 500 lines)

Existing top-level structure (relevant portion only):

| Line | Heading |
|---|---|
| 375 | `## ARB-01/ARB-02: General-α Operator Identity and Success Probability` |
| 379 | `### Owner's Attempt` |
| 391 | `### General-α Operator Identity` |
| 404 | `### Closed-Form Success Probability` |
| 436 | `### Comparison Against \`heralded_cz\`` |
| 451 | `### Full-Pipeline Validation (Plan 15-04)` |
| 467 | `### Denser α Sweep (Phase 16)` |
| 482 | `### Forge Verification of the Ancilla Mode-Mapping (Phase 16)` |
| 488 | `## Conclusion and Open Questions` (document-level, not ARB-specific) |
| 492 | `**What it does not establish**` (bulleted list, inside Conclusion, document-level) |

**Insertion points:**
- **(a) Literature comparison table** → No ARB-specific "what this does/doesn't establish" subsection exists today — unlike TRAIN and HARD, this section's scope framing is folded into the document-level `## Conclusion and Open Questions` (line 488-499), which covers the *entire* `iqp-photonic-encoding.md` doc (ENC-01 through ARB-09), not ARB-01/ARB-02 specifically. Two reasonable placements: (i) append a new `### What ARB-01/ARB-02 does/doesn't establish` subsection directly after `### Forge Verification...` (line 482-486) and before `## Conclusion and Open Questions` (line 488), scoped narrowly to ARB-01/ARB-02 only; or (ii) fold the table into the existing document-level Conclusion's "Generator-weight scope" bullet (line 494), which already discusses ARB-01/ARB-02's coverage. **Recommendation for the planner to weigh (Claude's discretion per CONTEXT.md):** option (i) is more consistent with TRAIN's and HARD's per-section pattern (both have a dedicated, section-scoped scope subsection, not a document-level one) and is architecturally cleaner since ARB-01/ARB-02 is one of three sections Phase 20 covers, while the rest of `iqp-photonic-encoding.md` (ENC-01..09, ARB-03..09) is out of Phase 20's scope.
- **(b) Herbst et al. cross-reference note** → Herbst et al.'s prediction (anticoncentration ↔ trainability tradeoff) is about trainability/hardness, not about the ARB-01/ARB-02 gate-mechanics question (general-α operator identity, success probability) — **the CONTEXT.md's locked decision only requires the Herbst cross-thread in `trainability-study.md` and `hardness-under-loss-study.md`**, not in `iqp-photonic-encoding.md`. No insertion needed here; confirmed no such requirement in WRITE-02/success-criterion-6 text.
- **(c) "What this does/doesn't establish" scope paragraph** → **does not yet exist as an ARB-01/ARB-02-scoped section** (only the whole-document Conclusion exists). This is the one real structural gap among the three source docs — WRITE-04 requires this scope paragraph "for each of the three sections," and ARB-01/ARB-02 currently only has the document-wide version. A new subsection is needed (see option (i) above), even though its content can draw heavily on the existing Conclusion bullets (lines 494 "Generator-weight scope," 497 "General-n scaling," 498 "design/mapping exercise, not a hardness proof").

## TRAIN-07 Pending Interpretation

Exact current text, `docs/trainability-study.md` lines 152-175:

```
## Cross-reference verdict (TRAIN-07)

`docs/iqp-baseline.md`'s empirical rule, applied directly to this project's
own measured n range (its `not complete_graph_like` escape-hatch clause is
a qubit-side structural notion this project's weight-1/mixed photonic
circuits have no established mapping onto — treated as inapplicable here,
not silently assumed to hold, since this project's circuits were never
constructed with "complete-graph-like" as a design axis one way or the
other):

​```
plateau if init_scheme == small_angle
or plateau if init_scheme == uniform and max(n) >= 6
​```

| generator_scope | init_scheme | baseline rule predicts | measured fit verdict | agreement |
|---|---|---|---|---|
| weight1 | small_angle | plateau | inconclusive (weak fit both ways, R²≈0.4-0.5) | inconclusive |
| weight1 | uniform | plateau (n_max=6 >= 6) | plateau (exp wins, R²=0.999, decaying) | **agree** |
| mixed | small_angle | plateau | inconclusive (both R²≈0, no discernible trend) | inconclusive |
| mixed | uniform | no_plateau (n_max=5 < 6) | plateau (exp wins, R²=0.910, decaying) | **disagree** |

> Owner interpretation: [pending]
```

**The specific question the owner needs to answer, unaided:** why does `weight1/uniform` **agree** with `docs/iqp-baseline.md`'s qubit-side empirical rule (rule predicts plateau at n_max=6≥6; measured fit is a decaying exponential — "plateau") while `mixed/uniform` **disagrees** (rule predicts no_plateau since n_max=5<6; measured fit is still a decaying exponential — "plateau" instead of the rule's predicted "no_plateau")? Both `small_angle` rows are already flagged "inconclusive" on both sides (no verdict to explain there) — the interpretive question is specifically about the two `uniform` rows' split outcome.

Relevant context the owner would need to draw on when answering (already on record elsewhere in the same document, not something Claude should supply as the answer):
- The `mixed` scope's exponential fits (`weight1/uniform` R²=0.999 vs `mixed/uniform` R²=0.910) both carry the "near-cancelling a/c pair, poorly-identified parameterization at only 4-5 points" caveat from the Results section (lines 88-99).
- TRAIN-09's bandwidth-sensitivity follow-up (lines 176-282) found neither `uniform` row's "exp" verdict is robust across a sigma grid — both flip to "inconclusive" at intermediate sigma, `weight1/uniform` re-emerges non-monotonically at high sigma, `mixed/uniform` does not.
- The `not complete_graph_like` escape hatch is explicitly "treated as inapplicable" for this photonic circuit family (stated directly above the table) — the owner may need to reason about whether that structural gap in the baseline rule's applicability, rather than a genuine trainability discrepancy, explains the `mixed/uniform` disagreement.

This is a real, currently-open gap (confirmed live at line 174 — the literal placeholder text is `> Owner interpretation: [pending]`), not a formality. Per CONTEXT.md, the Phase 20 plan must include an explicit task where the owner attempts this unaided, following the same Socratic/attempt-first ritual already used for ENC-05 and HARD-04 (see next section for those two examples' recorded style).

## Already-Recorded Self-Explanation Checkpoints

### ARB-01/ARB-02 (`docs/iqp-photonic-encoding.md` lines 379-389)

Confirmed genuinely recorded, not a placeholder — full text under `### Owner's Attempt` (line 379) documents a multi-round Socratic dialogue with real wrong turns and corrections:

> "The owner was walked through both derivations via the Socratic method, per this repo's attempt-first gating, rather than being handed the results directly."

Part (a) records a specific error caught (`exp(iθZ_iZ_j)` written as the eigenvalue matrix instead of its exponential) and a specific correct independent derivation, ending with the owner's own final words:

> *"α is equal to 4θ as we computed this using eigenvalues and matrix multiplication. We also found that theta and phi need to be opposite sign, but equal in magnitude."*

Part (b) records the owner's own dilation-theory explanation:

> *"This has to do with dilations and basically representing quantum operations as part of a larger system entangled system. This means that the 'missing' probability comes from correlations with the environment."*

This is directly citable/reusable per the locked decision — no re-run needed.

### HARD-04 (`docs/hardness-under-loss-study.md` line 362 area, actual heading at line 364)

Confirmed genuinely recorded under `### Owner's attempt-first response (recorded as-given, per this project's CLAUDE.md attempt-first gating and the ENC-01/ARB-02 transcript style)` (line 364-423). Contains the owner's actual decision, quoted directly:

> "**The owner's actual answer:** there is no established, principled eta->epsilon translation in the literature for this project's loss channel. Computing one from scratch ... is mathematically possible but would be original numerics work outside this project's stated scope (the owner's explicit call, not a fallback after attempting and failing...)."

This is likewise directly citable/reusable — genuinely an owner-authored decision, not a Claude-authored placeholder, and explicitly labeled with the ENC-01/ARB-02 transcript-style callout confirming it followed the same convention.

**Note on the CONTEXT.md's stated line number:** CONTEXT.md says "~line 364" for HARD-04 — confirmed accurate; the heading itself starts at line 364, with the parent `## HARD-04/HARD-06:...` section header at line 362.

## Literature Baselines — What Already Exists in the Repo

All 11 named baselines, what's already cited/engaged, and where. Verdict calls (consistent/inconsistent/silent) are explicitly NOT made here — this is inventory only.

| # | Baseline | Where already cited in repo | What's already known (from prior phase work) | Primary-source status |
|---|---|---|---|---|
| 1 | **McClean et al.** (barren plateaus in QNN training, 2018) | `.planning/research/FEATURES.md`, `SUMMARY.md`, `PITFALLS.md` (protocol citation only — "McClean-et-al.-style" gradient-variance-vs-system-size diagnostic). **Not cited anywhere in `docs/`.** | Standard protocol: variance of `∂L/∂θᵢ` over many random draws at each of several system sizes, checked for exponential-vs-polynomial decay — this is exactly Phase 17's own methodology shape. | **GAP — MEDIUM at best.** `SUMMARY.md` line 138 explicitly states "WebSearch-sourced summary of a well-known, frequently-cited result; not independently re-read from the primary paper in this session." No PDF in `docs/papers/`. This is the weakest-grounded of the 11 baselines — flag for either a primary-source fetch during Phase 20 execution, or an explicit "consistent with the well-known protocol shape, not independently re-verified against McClean et al.'s primary text" framing. |
| 2 | **Aaronson-Brod** (arXiv:1510.05245, lost-photon BosonSampling hardness) | `docs/iqp-baseline.md` (extensive, lines 59), `docs/hardness-under-loss-study.md` (lines 479-489, "Against Aaronson-Brod's fixed-count regime"). | Fixed-count-`k`-loss hardness holds for constant `k`; degrades sharply once `k` scales with `n` (a *fractional* rate, as this project uses, "does not allow strong complexity claims" per the paper's own text, p.9). Phase 18's own analysis already concludes this project's fixed-`eta` sweep structurally sits in the weak/constant-fraction regime the paper itself flags as insufficient. | **HIGH.** PDF read in full (`docs/papers/1510.05245.pdf`, Plan 18-01), verbatim quotes on record. |
| 3 | **arXiv:2510.24137** (Park & Oh, MPS approach to lossy boson sampling + noisy IQP) | `docs/iqp-baseline.md` (lines 57, extensive), `.planning/research/FEATURES.md`/`STACK.md`/`SUMMARY.md`. | Theorem 1 (Sec. IV): MPS-simulability upper bound at `η = O((log N/N)^(1/2α))` ≈ `η=Θ(1/√N)` — an upper bound on *one classical algorithm's* efficiency, explicitly NOT a hardness lower bound (paper states this itself). Section V's noisy-IQP result is a *different* result (qubit-level dephasing/depolarizing, not photon transmittance) — already flagged in-repo as "not the result being cited... for this project's photon-transmittance-loss claim." | **MEDIUM-HIGH for Theorem 1** (full text read per `18-RESEARCH.md` Finding 2, no PDF in `docs/papers/` but content directly quoted/paraphrased with equation numbers). Section V (the literally "IQP"-labeled result) is explicitly NOT the one used — worth being careful in the table not to conflate which sub-result is being compared against. |
| 4 | **arXiv:2405.01395** ("Simple rules for two-photon state preparation with linear optics") | `docs/iqp-photonic-encoding.md` (lines 389, 406 — extensively engaged, this is the literature source for ARB-01's own closed-form success-probability formula), `.planning/research/FEATURES.md`/`STACK.md`. | This is NOT a trainability or hardness paper — it's the construction paper `PostProcessedControlledRotationsItem`'s Section V-B formula (`p_success(α) = 1/σ_max^(2n)`) is sourced from. Its "baseline" role for ARB-01 is structural: this project's implementation already verifies its formula to ~1e-7 against measured amplitudes (table at `iqp-photonic-encoding.md` lines 420-432). This makes the ARB-01 "comparison" fundamentally different in character from the TRAIN/HARD baselines — it's a construction the project directly implements and validates against, not an independent theoretical prediction to check measured results against. | **MEDIUM.** `FEATURES.md`/`STACK.md` note this was WebFetch/WebSearch-confirmed (title/abstract + Section V-B formula), not a full independent primary-source PDF read — no PDF in `docs/papers/`. The formula itself IS independently verified empirically (measured vs. closed-form table already in `iqp-photonic-encoding.md`), which is a stronger form of verification than a citation check, even without a full paper read. |
| 5 | **`docs/iqp-baseline.md`'s own empirical rule** | `docs/iqp-baseline.md` (lines 37-44, the rule itself), `docs/trainability-study.md` (lines 152-175, TRAIN-07's cross-reference table — already directly compares against this rule). | This is this project's own compiled rule (not third-party literature): `plateau if small_angle OR (uniform AND n≥6 AND not complete_graph_like)`, 97.9% accuracy on 283 rows in the sibling project. TRAIN-07's table already does the exact per-cell comparison WRITE-02 wants for TRAIN — the "baseline" column of that table IS this row's raw material. | **HIGH** (originates from this project's own prior work, already directly exercised). |
| 6 | **Bremner-Montanaro-Shepherd 2015** (arXiv:1504.07999, hardness threshold, 1/192 ℓ1-error PH-collapse argument) | `docs/iqp-baseline.md` (lines 25-27, "Precise hardness statement," verified against Theorem 1 p.1). | Conditional hardness (PH collapse) for classical sampling within 1/192 ℓ1-error, conditional on average-case hardness conjectures whose worst-case analogues are proven. This is a structural/foundational hardness statement, not conditioned on loss or noise — most directly relevant as ARB-01's or a general framing citation rather than a loss-specific comparison. | **HIGH.** Verified directly against Theorem 1, p.1 — PDF present (`docs/papers/1504.07999v2.pdf`). |
| 7 | **Bremner-Montanaro-Shepherd 2017** (arXiv:1610.01808, noise+hardness, depolarizing threshold) | `docs/iqp-baseline.md` (lines 55, extensive), `docs/hardness-under-loss-study.md` (lines 213-243 "Anticoncentration results," 522-532 "Against BMS's depolarizing regime"). | Theorem 4: constant-rate depolarizing noise + sufficient anticoncentration (`α` = `Σp_x² ≤ α·2⁻ⁿ`) → poly-time classical simulability. This project's own measured `alpha(eta)` quantity (Phase 18's Anticoncentration section) is the exact quantity BMS's Theorem 4 keys on — but the owner's HARD-04 decision explicitly declined to compute an eta→epsilon depolarizing-rate translation, so BMS is stated in the doc as "structurally different, not-directly-comparable" by explicit owner decision, not silently omitted. | **HIGH.** PDF read in full (`docs/papers/1610.01808.pdf`/`.txt`/`v4.pdf`), Theorem 4/5 directly cited with page numbers. |
| 8 | **Rudolph et al.** (arXiv:2305.02881, MMD bodyness/bandwidth trainability) | `docs/iqp-baseline.md` (lines 51, "MMD's trainability depends on kernel bandwidth"), `docs/trainability-study.md` (TRAIN-09 section, lines 176-282, directly motivated by this paper's Theorem 2 — though the doc notes the paper's bitstring-Hamming-kernel bodyness decomposition doesn't mechanically transfer to this project's Euclidean-grid kernel). | Theorem 2: fixed (n-independent) bandwidth → exponential MMD-variance decay regardless of ansatz/init; `σ∈Θ(n)` bandwidth → polynomial. Phase 17's original fixed `SIGMA=0.1` sweep sits exactly in the "risky" regime this paper flags — TRAIN-09's entire follow-up study exists because of this finding. Very rich existing engagement — arguably the single most load-bearing external baseline already in the codebase for TRAIN. | **HIGH.** Two PDFs present (`docs/papers/2305.02881-implicit-explicit-losses.pdf`, `2305.02881v2.pdf`), Theorem 2 directly cited, mechanism-transfer caveat explicitly already worked through. |
| 9 | **Mhiri et al.** (arXiv:2502.07889, warm-start/small-angle guarantees) | `docs/iqp-baseline.md` (lines 52, "Small-angle/identity initialization is not a general trainability guarantee"). | Proves warm-start (near-zero-curvature) guarantees are NOT general — Appendix H gives a concrete commuting-circuit counterexample where curvature at θ=0 is exactly zero. Explicitly names "structured/commuting circuits" (i.e., IQP-like) as the risk case. Directly relevant to explaining why Phase 17's `small_angle` rows came out "inconclusive" rather than confirming a plateau. | **HIGH** for the specific claims quoted (page/section cited: p.5-6, Appendix H) — PDF present (`docs/papers/2502.07889-warm-start-guarantees.pdf`). |
| 10 | **Recio-Armengol et al.** (arXiv:2503.02934, n=1000 IQP-generative-ML) | `docs/iqp-baseline.md` (lines 27, 53 — two separate engagements: den Nest cosine-formula attribution confirmation, AND data-dependent-init finding), `docs/trainability-study.md` (TRAIN-10 section, lines 283-338 — the paper's data-dependent init recipe is directly implemented and tested). | Sec. 9.3 analytically derives exponential concentration under random/uniform init (same signature Phase 17 measured empirically) — their proposed fix (data-dependent init) was directly implemented as TRAIN-10 and found NOT to resolve the inconclusive verdict in either scope. This is the most deeply engaged baseline of all 11 — implemented and empirically tested, not just cited. | **HIGH.** PDF present (`docs/papers/2503.02934v2 (3).pdf`), Proposition 1 (den Nest formula) and Sec. 9.3/8.1.2 (data-dependent init) both directly cited and implemented. |
| 11 | **Herbst et al.** (arXiv:2512.24801, anticoncentration-trainability tradeoff) | `docs/iqp-baseline.md` (lines 54, "Trainability and sampling-hardness may be two faces of the same anticoncentration property"). Not yet cited in `trainability-study.md` or `hardness-under-loss-study.md` — this is the cross-thread Phase 20 is explicitly tasked with adding. | Formal result: anticoncentrating output distributions cause MMD-type losses to concentrate exponentially — trainability and hardness predicted to co-occur, not trade off. Their own numerics include IQP directly (PennyLane/IQPopt) and show it concentrating fast. Explicit consequence already drafted in `iqp-baseline.md`: "if Phase 18 finds photon loss erodes anticoncentration (and thus hardness), this framework predicts trainability should correspondingly improve at higher loss" — this is the literal prediction success criterion 6 asks the two source docs to check their own measured results against. | **HIGH** for the paper's claim (PDF present, `docs/papers/2512.24801v1.pdf`) — but the actual cross-check against Phase 17's TRAIN result and Phase 18's HARD result is explicitly unwritten (the task this phase must do), not a pre-existing gap in citation quality. |

**Summary of gaps requiring attention during Phase 20 execution:**
- **McClean et al.** — no primary-source PDF, no `docs/` citation at all yet, MEDIUM confidence per prior research docs. The planner should decide whether to (a) fetch and read the primary source before drafting TRAIN's table, or (b) explicitly frame the McClean row as "consistent with the well-known protocol shape (WebSearch/secondary-source confirmed, not independently primary-source-verified)" rather than presenting it with the same confidence as the other 10.
- **arXiv:2405.01395** and **arXiv:2510.24137** — no PDF downloaded (unlike the other 8, which all have PDFs in `docs/papers/`), though both have been meaningfully engaged (formula-level for 2405.01395, Theorem-level for 2510.24137) via WebFetch/direct quoting. Lower priority gap than McClean since substantive content already exists in-repo, but worth flagging if the planner wants full primary-source parity across all 11.

## Numbers/Scripts to Trace (WRITE-06)

Confirmed near-trivial to satisfy — every source doc already names its exact CSV/script for every results table:

**TRAIN:**
- Core sweep: `results/phase17_curve_fit_summary.csv` (Results section, line 85-86); gradient-variance CSVs `results/phase17_{weight1,mixed}_gradient_variance.csv` (implied by curve-fit summary's dependency).
- TRAIN-09 (bandwidth): `results/phase171_train09_curve_fit_summary.csv` (line 241).
- TRAIN-10 (data-dependent init): `results/phase171_train10_curve_fit_summary.csv` (line 318).
- Dual-rail cross-check: `results/phase17_dual_rail_curve_fit_summary.csv` (line 418).
- Seeds: RNG substreams via `trainability/rng.py`, deterministic and reorder-safe (line 21) — no single global seed constant named in the doc text itself, but the mechanism is code-referenced (`trainability/rng.py`), which satisfies "fixed seed where randomness is involved" via a pointed reference rather than a literal number. If the planner wants a literal seed value quoted in the write-up, it would need a quick source check (not yet inventoried here — flagged as a possible small task, not a blocker).

**HARD:**
- Weight-1 sweep: `results/phase18_weight1_loss_sweep.csv` (line 149, 234).
- Mixed sweep: `results/phase18_mixed_loss_sweep.csv` (line 149, 234).
- Seed: **explicitly literal and quoted** — `seed_base=180814` (line 82), reused for the MerLin dual-rail parallel too (line 326).
- MerLin dual-rail: `results/phase18_merlin_dual_rail_{weight1,mixed}_loss_sweep.csv`, `results/phase18_backend_comparison.csv` (lines 329-331).
- Draw count: `n_draws=5` (line 81), explicit.

**ARB:**
- Alpha sweep: `results/phase16_alpha_sweep.csv` (line 475).
- Forge verification: `results/phase16_forge_summary.md`, `forge/ancilla_mapping.frg` (line 486).
- Full-pipeline validation: `tests/test_iqp_photonic_encoding.py` (line 457) — test-referenced rather than CSV-referenced, since these are TVD checks not sweeps.
- No explicit "seed" concept for ARB-01/ARB-02's own results (the α sweep is a fixed deterministic grid of α values at a fixed `thetas=[0.0,0.0]`, not a random draw — confirmed at line 469, "the exact same locked configuration"), so "fixed seed where randomness is involved" is vacuously satisfied here (no randomness in this section's results).

**Conclusion:** WRITE-06 is essentially already satisfied by the existing docs' own citation discipline. Phase 20's synthesis doc (`docs/technical-findings.md`) needs to preserve/mirror these citations rather than re-derive them — the only real "work" here is making sure `technical-findings.md` doesn't accidentally state a number without repeating its source doc's own citation.

## File/Module Conventions

- **`docs/*.md` naming**: kebab-case, descriptive of study/topic (`trainability-study.md`, `hardness-under-loss-study.md`, `iqp-baseline.md`, `iqp-photonic-encoding.md`, `iqp-lit-scoping.md`, `julia-cross-check-study.md`, `mmd-loss.md`, `raster-order.md`). No front-matter (no YAML headers) in any existing doc — plain `# Title` as line 1. `docs/technical-findings.md` should follow this pattern: `# Technical Findings — [subtitle]`, no front-matter.
- **Heading hierarchy convention**: `#` for doc title (once), `##` for major sections (often tagged with a requirement ID in parens, e.g. `## Parameter-initialization and normalization (TRAIN-03)`), `###` for subsections. Results tables are always preceded by a `##`/`###` heading naming what they show, and PNG figures are embedded via `![alt text](../results/xxx.png)` immediately before or after their data table.
- **`docs/iqp-baseline.md`'s "Fresh Primary-Source Verification" section (lines 47-61) is a strong format precedent worth mirroring** for the new literature-comparison tables — it's already exactly this project's established style for "per-baseline paper: what it claims, what it means for this project's own result, stated in bulleted paragraph form with the source's page/theorem cited inline." The new tables should likely retain that same "cite the specific theorem/page, then state the relevance" texture inside each table cell or in prose immediately following the table, rather than inventing a terser format that loses the citation precision.
- **Self-explanation checkpoint format**: two established sub-styles exist:
  - `docs/trainability-study.md`'s existing `> Owner interpretation:` single-line blockquote (line 174, currently `[pending]`) — used for a compact, single-paragraph interpretation.
  - `docs/iqp-photonic-encoding.md`'s `### Self-Explanation Checkpoint (Task 3) — Owner's Interpretation` / `### Owner's Attempt` heading style (lines 336, 379) and `docs/hardness-under-loss-study.md`'s `### Owner's attempt-first response (recorded as-given...)` (line 364) — used for multi-round Socratic dialogues with recorded wrong turns.
  - TRAIN-07's checkpoint, given it's a focused single interpretive question (not a whole-document explanation), likely fits the shorter blockquote style already scaffolded at line 174 — filling in `[pending]` in place, possibly extended to a short paragraph if the dialogue takes more than one exchange, matching the existing precedent at `trainability-study.md` lines 436-467 (the `> **Owner interpretation:**` block for the dual-rail `mixed/uniform` disagreement, which is a longer multi-paragraph blockquote in the same file).
- **Scripts that already produce numbers vs. reference-only**: `trainability_analysis.py` (curve-fit analysis, referenced in STATE.md's Phase 17 close-out), `hardness_analysis.py`-equivalent is actually `hardness/sweep.py` + `loss_sweep.py` (CLI orchestration) — no single monolithic "analysis.py" file confirmed for HARD by this research pass; the CSVs already contain the final computed numbers (TVD, alpha, herald rates), so Phase 20 does not need to re-run any script, only cite the existing CSVs/scripts already named in each source doc.

## Sizing/Waves — Suggested Breakdown

This is explicitly Claude's discretion per CONTEXT.md; the following is a suggestion with the hard sequencing constraints called out.

**Hard sequencing constraint #1:** The TRAIN literature table's `iqp-baseline.md`-empirical-rule row (baseline #5 above) overlaps directly with TRAIN-07's cross-reference table and its pending owner interpretation. The self-explanation checkpoint should run **before** finalizing the TRAIN literature table's row for baseline #5, since the interpretation may inform how that row's consistent/inconsistent/silent verdict gets framed (though the raw agree/disagree data already exists in the table at lines 167-172 regardless of the interpretation's content).

**Hard sequencing constraint #2:** `docs/technical-findings.md` (the synthesis doc) depends on all three source docs' tables + scope paragraphs + Herbst notes being in their final form, since it mirrors them. It must be the last wave.

**No sequencing constraint between the three source-doc edits themselves** — `trainability-study.md`, `hardness-under-loss-study.md`, and `iqp-photonic-encoding.md` are three different files with no dependency between their respective table/scope-paragraph/Herbst-note edits (the Herbst notes in TRAIN and HARD do reference each other by content, but each doc's own note only needs to state its own section's verdict plus a pointer — it doesn't need the other doc's edit to already exist on disk to be written correctly, since the underlying Phase 17/18 results are already fixed and known).

**Suggested wave structure:**
1. **Wave 0 (sequential, first):** TRAIN-07 self-explanation checkpoint task — owner explains the weight1/uniform-agrees vs. mixed/uniform-disagrees pattern unaided; text recorded in place of `[pending]` at `trainability-study.md:174`.
2. **Wave 1 (parallel, 3 independent tracks, one per source doc):**
   - Track A: `trainability-study.md` — draft TRAIN literature table (11-baseline subset relevant to TRAIN, likely baselines #1, #5, #6/7 lightly, #8, #9, #10, #11 primarily — exact subset is the planner's call) + Herbst cross-reference note in `## What this does/doesn't establish`.
   - Track B: `hardness-under-loss-study.md` — draft HARD literature table (likely baselines #2, #3, #6, #7, #11 primarily) + Herbst cross-reference note in `### HARD-06`.
   - Track C: `iqp-photonic-encoding.md` — draft ARB literature table (likely baselines #4, #5/#6 lightly relevant since ARB is a gate-construction/validation exercise not a hardness/trainability study) + create the new ARB-01/ARB-02-scoped "what this does/doesn't establish" subsection (this doc's one real structural gap, per Source Document Current State above).
3. **Wave 2 (sequential, last):** `docs/technical-findings.md` — new synthesis doc, mirrors all three tables, links to all three source docs' scope sections, adds executive framing (Claude's discretion on structure per CONTEXT.md).

This groups naturally into 3 file-scoped waves (0, 1, 2) rather than one task per WRITE-0x requirement, since most WRITE-0x requirements (01, 03, 04, 05, 06) are properties that fall out of doing Wave 0/1/2 correctly rather than standalone deliverables — WRITE-02 (the 11-baseline tables) and WRITE-05 (the TRAIN-07 checkpoint) are the only two requirements that need a dedicated, explicitly-named task each.

## Open Questions

1. **How many of the 11 baselines apply per section, and which are "silent" by design?**
   - What we know: CONTEXT.md locks "each table lists only the baselines actually relevant to that section (avoids rows full of silent)" — implying not all 11 appear in all 3 tables.
   - What's unclear: the exact per-table subset is not specified anywhere in ROADMAP.md/REQUIREMENTS.md/CONTEXT.md — it's left to the planner/owner's judgment about relevance.
   - Recommendation: the planner should make an explicit relevance call per baseline per section as part of drafting each table (e.g., baseline #4, arXiv:2405.01395, is almost certainly ARB-only and silent for TRAIN/HARD given its subject matter; baseline #9, Mhiri et al., is TRAIN-only given its subject is warm-start guarantees).

2. **Does the McClean et al. gap block Phase 20, or get worked around with a caveat?**
   - What we know: no primary-source PDF exists in this repo for McClean et al.; existing citations are WebSearch-sourced summaries at MEDIUM confidence.
   - What's unclear: whether the phase's rigor bar (matching GEN-07/LIT-04/Phase-7 honesty) requires a fresh primary-source read before citing it in a formal comparison table, or whether an explicitly-caveated secondary-source citation is acceptable given this project's history of flagging exactly this kind of gap rather than silently upgrading confidence.
   - Recommendation: given this project's demonstrated pattern (e.g., the Aaronson-Brod/Park-Oh misattribution correction, the "Van den Nest" attribution gap independently confirmed on 2026-08-17), the planner should likely schedule a primary-source fetch (arXiv:1802.06002, McClean et al. 2018 — not yet verified as the correct arXiv ID by this research pass, would need confirming) for McClean before finalizing TRAIN's table, or explicitly write the McClean row as secondary-source-confirmed only.

3. **Is a literal RNG seed value needed for TRAIN's WRITE-06 traceability, or does the `trainability/rng.py` code-reference suffice?**
   - What we know: HARD's `seed_base=180814` is explicitly quoted as a literal number in the doc; TRAIN's doc only names the mechanism (`trainability/rng.py`, "deterministic, reorder-safe RNG substreams") without quoting a literal seed constant.
   - What's unclear: whether WRITE-06's "fixed seed where randomness is involved" requirement is satisfied by a code-reference alone, or needs a literal number quoted in `technical-findings.md` for full parity with HARD's style.
   - Recommendation: low-priority, easily resolved with a two-minute source check of `trainability/rng.py` during Phase 20 execution if the planner wants full parity; not a structural gap.

## Sources

### Primary (HIGH confidence — direct reads of this repo's own files during this research pass)
- `docs/trainability-study.md` (full, 548 lines)
- `docs/hardness-under-loss-study.md` (full, 569 lines)
- `docs/iqp-photonic-encoding.md` (lines 300-500, covering ENC-04/05 and ARB-01/ARB-02 through Conclusion)
- `docs/iqp-baseline.md` (full, 65 lines)
- `docs/julia-cross-check-study.md` (heading structure only)
- `.planning/phases/20-technical-write-up/20-CONTEXT.md` (full)
- `.planning/REQUIREMENTS.md`, `.planning/ROADMAP.md` (WRITE-0x sections)
- `.planning/research/FEATURES.md`, `STACK.md`, `SUMMARY.md`, `PITFALLS.md` (McClean/2405.01395/2510.24137 citation-confidence provenance)
- `.planning/STATE.md` (tail, session-continuity and pending-todos sections)
- `results/phase7_neighbor_locality_summary.md` (GEN-07/Phase-7 honest-negative-framing tone example)
- `.planning/milestones/v1.0-REQUIREMENTS.md`, `v2.0-REQUIREMENTS.md`/`MILESTONE-AUDIT.md` (GEN-07/LIT-04 provenance)
- `docs/papers/` directory listing (PDF inventory, confirms which of the 11 baselines have a downloaded primary source vs. not)
- `results/` directory listing (CSV inventory, confirms WRITE-06 traceability claims)

### Secondary / Tertiary
None used — this research task is entirely internal repo reconnaissance, no external Context7/WebSearch/WebFetch calls were needed or made.

## Metadata

**Confidence breakdown:**
- Source-document current state (insertion points, existing structure): HIGH — direct file reads with exact line numbers.
- TRAIN-07 pending interpretation: HIGH — exact placeholder text quoted directly.
- Already-recorded self-explanation checkpoints: HIGH — exact quotes confirm genuine, non-placeholder content.
- Literature baseline inventory: HIGH for what's already in the repo (direct greps/reads); MEDIUM for characterizing McClean/2405.01395/2510.24137's primary-source verification status, since that assessment relies on this project's own prior research docs' self-reported confidence levels rather than an independent re-verification during this research pass.
- WRITE-06 traceability: HIGH — direct citation checks against each source doc's own text.
- Sizing/waves: this is a recommendation, not a finding — stated as such, not a confidence-rated claim.

**Research date:** 2026-08-18
**Valid until:** No external decay risk (all findings are about this repo's own static file contents, not a fast-moving library) — valid until the source docs themselves are next edited.
