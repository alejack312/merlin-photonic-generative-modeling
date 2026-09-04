# Phase 24: REVIEW-01 — Independent Codex Null-Result Review

**Run:** 2026-09-03, `codex exec -s read-only`, prompted adversarially to write the null result for each corrected claim and check whether the claim survives it — the same discipline this whole milestone exists to enforce, aimed at the corrections themselves.
**Raw output:** `24-REVIEW-codex-raw.md` (verbatim, unedited).
**Codex's own learning note:** `.claude/learnings/2026-09-03-adversarial-null-result-review.md` (Codex wrote this unprompted; relocated from a stray `.Codex/learnings/` it created to match this repo's actual convention).

## Disposition

| Finding | Verdict | Action taken |
|---|---|---|
| Trainability correction's "identity kernel at every swept n" | **Confirmed real error.** Independently reverified: off-diagonal kernel at n=5,6 is 0.230, not negligible. My own test only ever checked n<=4; the prose overclaimed beyond it. | Fixed in `docs/trainability-study.md`, `README.md`, `docs/technical-findings.md` — now precisely scoped to n<=4 exact, n=5,6 "reproduced by the same no-circuit-content model using the real kernel," not identity. |
| "Reproduces the shipped curve" overstates a Monte Carlo, 0.5-relative-tolerance regression | Confirmed — regression covers the trend, not floating-point reproduction. | Language softened to "reproduced ... within a documented tolerance," tolerance rationale already stated in test comments. |
| "Not a barren plateau by construction" reads as a categorical proof | Confirmed overreach — the check establishes this circuit's exponential shape isn't attributable to the circuit, not a general theorem about product-distribution metrics. | Reworded to the narrower, defensible claim in `docs/trainability-study.md`. |
| High-sigma re-emergence called "exactly what this mechanism predicts" with no sigma=3,9 null check | Confirmed unverified. | Reworded to "consistent with, not proven by" / "a hypothesis, not a finding." |
| "n in the 20s in milliseconds" is an unrun performance claim | Confirmed. | Removed the specific figure; states no structured simulator was built or timed, and that any specific n would be an unverified extrapolation. |
| "Exactly as hard as the lossless case" smuggles a hardness claim the null doesn't establish | Confirmed — the null proves conditional shape identity, not hardness equivalence; this project never proved the lossless case is hard, only inherited IQP's conjecture. | Reworded across `docs/hardness-under-loss-study.md`, `README.md`, `docs/technical-findings.md` to "provably identical ... a shape statement, not a new hardness proof." |
| Throughput paragraph calls a probability "samples per useful shot" (should be `1/p`) | Confirmed real bug — the table caption already had it right, the prose above it didn't. | Fixed the prose to match the table. |
| k>=2 throughput rows presented without flagging they're an unverified extrapolation of the single-gate mechanism | Confirmed. | Table and caption now explicitly label k=0,1 as verified-range, k>=2 as "extrapolated, not measured." |
| "Why every curve converges to ~0.50" section says the lossy distribution is "raw, un-renormalized" for both scopes, but `mixed`'s pipeline already divides by `herald_success_prob` before returning it | Confirmed real imprecision (pre-existing v3.0 text, not something this correction introduced, but the correction should have caught it). | Added a precision note distinguishing weight1 (genuinely raw) from mixed (already herald-conditioned), tying it to the closed form above. |
| `iqp-photonic-encoding.md`'s "genuine, careful, original work" is a novelty claim the literature search didn't actually check | Confirmed — the search checked for a DV/Fock-space IQP-specific construction, not for prior art on this specific polarization encoding. | Reworded to distinguish "checked correctness" from "originality," explicitly noting no priority search was done. |
| Literature addendum claims are abstract-level, not full reads | **Not a new finding** — already disclosed as such in the addendum's own text (per D-07's confidence-tiering convention). No action needed; Codex's flag confirms the existing hedge is doing its job, not that it's missing. |
| Anticoncentration invariance "PASS only as a shape-statistic null," not independently tested by `test_null_results.py` | Accurate as stated — `alpha` invariance is a corollary of the same shape-preservation fact TVD's null already covers, not a separate untested claim. No code action; already correctly scoped in prose as "a direct, provable consequence," not a standalone finding. |
| technical-findings.md / README "inherit" corrections without independently re-checking them | Expected — they're synthesis/pitch documents that mirror the two source docs by design, not separate primary sources. No action; this is the documented convention (`docs/technical-findings.md`'s own opening states it mirrors, doesn't re-derive). |

## What this review did not check (out of scope for REVIEW-01)

Whether the KLM-universality citation itself (Knill, Laflamme & Milburn 2001) is accurately characterized — Codex flagged this as worth double-checking but it's a citation-accuracy question, not a null-result question; not re-verified here.

## Bottom line

Nine of thirteen findings were real, independently reverified before acting, and fixed. The most serious one (the kernel-identity overclaim at n=5,6) was the same class of error — an unchecked boundary case — that caused the original v3.0 mistakes this milestone exists to correct, now caught by aiming the same discipline at the correction itself. Four findings were confirmed-as-already-correctly-scoped, not gaps.
