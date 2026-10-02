# Hidden-label Fock density and cutoff accounting
Date: 2026-10-01 · Scope: project · Recurs when: noisy source sectors and hidden labels enter passive full-Fock controls.

## Context & constraints
- Representation A only, registered n=2,3, source once, vacuum gate ancillas.
- Source cutoff is n+c emitted photons; omitted branches stay omitted after loss.
- Desired common/private labels and fully distinguishable extras persist across gates.

## Approach
1. Test ideal and uniform-loss nulls against the existing full-Fock probability oracle.
2. Build source density, apply per-mode loss Kraus maps, then propagate density via creation-operator Fock transitions.
3. Preserve tensor-product species factors until the final diagonal detector measurement.
4. Check the owner's pulse polynomial by independent convolution, with a cutoff that retains every branch.
5. Run process-local wrong-p2, wrong-exponent, posthoc-loss, normalization, and detector-mass mutations; rerun unmutated oracles.

## Decision rules that generalize
- IF attenuation is uniform on all modes and the circuit is passive with final-only projection, THEN loss may commute to the source; otherwise prove the move separately.
- IF the cutoff omits emission branches, THEN keep absolute subnormalized detector masses and report the source tail, independent of loss.
- IF a two-pulse oracle includes four emitted photons, THEN use c=2 for its exact check; c=1 requires subtracting the omitted branch explicitly.
- IF detectors are threshold, THEN distinguish click acceptance from conditioning on true total photon number.
- IF V fixes only pair overlap, THEN document the higher-order hidden-label convention and the missing independent oracle.

## Mistakes avoided / dead ends
- Applying eta^n after g2>0 loses the n+1-emitted/one-lost contribution.
- Normalizing retained emission mass hides the cutoff tail.
- Convolving species diagonals is valid at final number measurement; doing it between gates destroys interference.

## Verification
- Focused green and actual mutant failures: docs/audits/r1-a-evidence/.
- Analytic two-photon splitter, V=0 categorical convolution, pulse totals, density coherence, and Kraus completeness pass.
- Full-suite and final elapsed-time evidence: docs/audits/2026-10-01-r1-representation-a.md.

## Next time (for a weaker model)
- Do: inspect noisy.py, owner addenda, Fock source rail conventions, and the exact conditional event first.
- Don't: call a retained-tail normalization or a self-comparison an independent noisy-distribution oracle.

## Changed files
- src/merlin_iqp/deploy/noisy_fock.py — additive small-n density evaluator and accounting.
- tests/v4_completion/test_r1_representation_a.py — independent oracles and deliberate mutations.

## Profile preflight addendum (2026-10-02)
- IF a profile grid requests every circuit/size combination, THEN enumerate the existing fixture registry first; four registered combinations yield 32 cells here, with 32 other grid cells explicitly undefined.
- IF a required owner null is absent, THEN mark it NOT_REGISTERED, ask for its definition, and preserve pilot/null-check evidence without accepting profile results.
- Keep preflight manifests immutable and separate from later accepted-run directories; hash the source files and freeze the exact profile table and tolerances.
- Verification: results/v4_completion/20261002_first_r1_preflight/ records four timing measurements, 14 passing NULL 1/2/4 checks, and no accepted profile rows. NULL 3 remains unregistered.

## Profile execution addendum (2026-10-02)
- Owner NULL 3 was subsequently registered at 45a2ab9: balanced beam splitter, V=.4, coincidence .3, tolerance 1e-9; generic partial-V n3 CP distribution validation remains unavailable.
- Reuse a committed pilot only after matching simulation/test code hashes. Preserve its preflight snapshot and write accepted runs to a separate immutable directory.
- Verification: all four nulls passed before 32 defined profile cells; saved distributions normalize, threshold true-n conditionals coarse-grain their PNR companions, and every Belenos/g2 row carries the required measurement/assumption qualifiers. See results/v4_completion/20261002_first_r1_runs/.

## Brightness accounting addendum (2026-10-02)
- IF published first-lens brightness is used as independent pulse emission probability, THEN label that mapping as an assistant definition that the owner may revise.
- IF only one results column may change, THEN compare every other CSV cell as strings, preserve historical notes, and put the revised definition in the new manifest and table caption.
- Verification: wrong n+1 exponent fails all eight Ascella rows; correct n exponent passes 33 checks with zero product gap. Original results remain immutable; null evidence is inherited, not rerun.
