# Verifying photonic hardware specifications
Date: 2026-10-01 · Scope: project · Recurs when: hardware parameters are proposed for a simulator.

## Context & constraints
- D1 fact-finding requires sources without choosing a physical model.
- A detector technology name does not establish photon-number resolution.
- Published examples, measured configurations, and current cloud metadata have distinct provenance.

## Approach
1. Read the experimental paper's supplement before treating rounded headline values as calibration.
2. Record the machine, measurement boundary, correction convention, page, and short quote per claim.
3. Inspect versioned remote-client metadata handling separately from detector-model constructors.
4. Preserve conflicting configurations and mark missing live metadata explicitly.

## Decision rules that generalize
- If HOM is corrected for multiphoton emission, retain raw visibility and corrected overlap as separate quantities.
- If brightness is measured at the first lens or fibre, do not relabel it end-to-end transmission.
- If a catalogue says a feature will be integrated, record a proposed feature rather than verified deployment.
- If source code accepts detector metadata, it proves client handling, not a named server's present setting.
- If an appendix omits the platform name, do not assign its detector count to another paper's named QPU.

## Mistakes avoided / dead ends
- Guessed supplement paths returned 404; the exact article hyperlink succeeded.
- General SNSPD literature was not used to classify Altair.

## Verification
- Publisher supplement, public papers, vendor PDFs, and Perceval 1.2.4 sources inspected.
- Research table checked for five columns and quotes shorter than 15 words.
- Current authenticated cloud settings were not obtained.

## Next time (for a weaker model)
- Do: locate the exact supplement; distinguish raw and corrected metrics; date each configuration.
- Don't: turn a simulation example, proposed catalogue feature, or unnamed setup into live hardware evidence.

## Addendum: multiphoton overlap (2026-10-01)
- If a paper reports desired-photon overlap M_s, do not relabel it signal-noise overlap M_sn.
- If a simulation cites another source model, trace that model's appendix and label the resulting hardware-model attribution as a citation-chain inference.
- If a notebook omits a flag, verify the versioned descriptor default and conversion code before identifying its effective model.
- If g2 appears, retain the paper's relation to p2; do not treat autocorrelation as a two-photon emission probability.
- If re-excitation emissions are time-correlated, preserve the paper's approximation boundary for separable noise.
- Verified: source-model papers, Ascella citation chain, Perceval v1.2.1/v1.2.4 source and v1.2 tomography defaults; no named-QPU unwanted-pair overlap calibration found.
