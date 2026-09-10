# Registered comparison derivation evidence

Date: 2026-09-07. This scoped note records only derived metrics artifacts from already-existing registered ring runs. It does not change the central ledger or synthesis reports.

## Completed bounded derivation

- Hamming comparisons: n=6 seeds 0–4 and n=8 seeds 0–4, 10 cells total.
- Spatial comparisons: n=6 seeds 0–1, 2 cells completed before the bounded pass was stopped.
- Existing n=4 Hamming and spatial smoke comparisons remain unchanged.
- Each emitted manifest retains raw, unquantized compiled control, quantized compiled, and fixed-photon deployed arms, common hashes, acceptance, KL, coverage, occupancy, marginals, and direct/Walsh/trainer Hamming-MMD cross-checks.
- No new training, NAT, sibling, or physical sweep was launched. Remaining n=6 spatial seeds 2–4 and n=8 spatial seeds 0–4 are unrun in this pass.

## Verification

- Every completed comparison process exited 0 except the first n=6 Hamming probe, which encountered the intended immutable-artifact equality guard after its artifact had already been written; the retained artifact is valid and was not overwritten.
- Focused comparison/NAT/resource tests are the acceptance checks for this bounded derivation.
