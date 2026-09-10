# Documentation reconciliation — 2026-09-10

The public reading order is [bounded results](v4-bounded-release.md), [corrected synthesis](technical-findings.md), [IQP conventions](iqp-baseline.md), [MMD conventions](mmd-loss.md), then the detailed study of interest. Full original v4 scientific acceptance remains incomplete.

This pass assessed README and all 26 top-level study documents. It corrected current scientific explanations and identified historical plans, earlier verification checkpoints and owner-authored records as such. Historical audits, planning logs, source papers and raw result records are preserved; their presence is not an endorsement of every superseded conclusion. This was a documentation reconciliation, not a fresh audit of every historical source file or every theorem cited in the repository.

## Changes that affect scientific interpretation

- Classical parity estimation, exact enumeration, optimization success and sampling complexity are separate claims.
- Hamming distance, Euclidean distance, bandwidth notation and normalized Walsh weights are explicit. Every finite kernel has a Walsh representation; a spatial kernel generally has a dense representation.
- The v3 half-L1 loss diagnostic uses subnormalized mass. It cannot be interpreted as conditional TVD or sampling-hardness evidence.
- Commuting generators do not imply commuting observables. Equivalent ideal logical encodings do not acquire different gradients solely from their substrate.
- Loss simulation theorems retain their source-model and scaling assumptions. The literature review does not claim novelty from an unsuccessful search.
- Final comparisons report fit, target support and expected source attempts. Analytic references, synthetic tomography and direct optical simulations are distinguished. Nominal budgets do not imply sampled uncertainty.
- WRITE-07 is recorded; NULL-07 experimental adjudication remains incomplete. Historical owner statements are preserved without attributing new interpretations to the owner.

## Per-file assessment

| Document | Action | Reason |
|---|---|---|
| [hardness-under-loss-study.md](hardness-under-loss-study.md) | Updated | Corrected claims, status or current/historical evidence boundary. |
| [iqp-baseline.md](iqp-baseline.md) | Updated | Corrected claims, status or current/historical evidence boundary. |
| [iqp-lit-scoping.md](iqp-lit-scoping.md) | Updated | Corrected claims, status or current/historical evidence boundary. |
| [iqp-photonic-encoding.md](iqp-photonic-encoding.md) | Updated | Corrected claims, status or current/historical evidence boundary. |
| [julia-cross-check-study.md](julia-cross-check-study.md) | Updated | Corrected claims, status or current/historical evidence boundary. |
| [mmd-loss.md](mmd-loss.md) | Updated | Corrected claims, status or current/historical evidence boundary. |
| [raster-order.md](raster-order.md) | Updated | Corrected claims, status or current/historical evidence boundary. |
| [technical-findings.md](technical-findings.md) | Updated | Corrected claims, status or current/historical evidence boundary. |
| [trainability-study.md](trainability-study.md) | Updated | Corrected claims, status or current/historical evidence boundary. |
| [v4-additive-pipelines-design.md](v4-additive-pipelines-design.md) | Updated | Corrected claims, status or current/historical evidence boundary. |
| [v4-backend-comparison.md](v4-backend-comparison.md) | Updated | Corrected claims, status or current/historical evidence boundary. |
| [v4-bounded-release.md](v4-bounded-release.md) | Retained | Retains its stated bounded evidence or dated owner-authored record; no numerical result or owner words changed. |
| [v4-closure-validation-2026-09-08.md](v4-closure-validation-2026-09-08.md) | Updated | Corrected claims, status or current/historical evidence boundary. |
| [v4-communication-disposition-2026-09-08.md](v4-communication-disposition-2026-09-08.md) | Retained | Retains its stated bounded evidence or dated owner-authored record; no numerical result or owner words changed. |
| [v4-correction-pass-2026-09-10.md](v4-correction-pass-2026-09-10.md) | Updated | Corrected claims, status or current/historical evidence boundary. |
| [v4-deployment-study.md](v4-deployment-study.md) | Updated | Corrected claims, status or current/historical evidence boundary. |
| [v4-milestone-completion-report.md](v4-milestone-completion-report.md) | Updated | Corrected claims, status or current/historical evidence boundary. |
| [v4-null-behavior-literature-review.md](v4-null-behavior-literature-review.md) | Retained | Retains its stated bounded evidence or dated owner-authored record; no numerical result or owner words changed. |
| [v4-owner-explanation-2026-09-09.md](v4-owner-explanation-2026-09-09.md) | Annotated | Corrected input/output rail distinction separately from preserved owner wording. |
| [v4-owner-learning-position.md](v4-owner-learning-position.md) | Updated | Corrected claims, status or current/historical evidence boundary. |
| [v4-owner-predictions-2026-09-08.md](v4-owner-predictions-2026-09-08.md) | Retained | Retains its stated bounded evidence or dated owner-authored record; no numerical result or owner words changed. |
| [v4-plan-train-classical-deploy-photonic.md](v4-plan-train-classical-deploy-photonic.md) | Updated | Corrected claims, status or current/historical evidence boundary. |
| [v4-rings-study.md](v4-rings-study.md) | Updated | Corrected claims, status or current/historical evidence boundary. |
| [v4-sibling-reproduction.md](v4-sibling-reproduction.md) | Updated | Corrected claims, status or current/historical evidence boundary. |
| [v4-tcdp-study.md](v4-tcdp-study.md) | Updated | Corrected claims, status or current/historical evidence boundary. |
| [v4-wrap-up-recommendation.md](v4-wrap-up-recommendation.md) | Updated | Corrected claims, status or current/historical evidence boundary. |

README was updated to lead readers to the current bounded results and this guide. The earlier baseline, MMD, raster-order and synthesis text is retained through immutable Git links in their replacements. The literature scope likewise links its original search and owner decision.

## Verification scope

Primary-source checks covered the claims in the revised literature scope and the load-bearing IQP/MMD explanations. Algebra was checked independently on small finite examples. Local document targets and affected section links were checked. No new scientific experiment, hardware timing prediction or source-model validation was performed.

The existing final implementation gate remains 726 passed, 1 skipped, with 37 explicit sibling integration tests, at implementation commit `a8db410`. This documentation-only pass does not relabel those tests as newly run or close deferred scientific requirements.

Root documentation: DESIGN_DECISIONS, NOTES and the post-September plan received historical-context notices. The SMART specification remains an original dated contract. CONTRIBUTING now includes the additive v4 package and test layout. Agent guidance is operational instruction, not scientific evidence.

Verification result: independent n=1..5 Hamming and dense-Walsh identities, simultaneous-permutation invariance, and accepted/failure-mass formulas passed. The README section-link defect found by the local link check was repaired.

The independent IQP cosine/state-vector comparison also passed for n=1..5. The release probe rechecked 99 committed evidence files and 64 sibling payload hashes. All local link targets in the 28 changed public documents passed after repairing the historical quickstart link.
