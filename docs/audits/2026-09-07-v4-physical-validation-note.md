# v4 physical validation note

Date: 2026-09-07. Scope: direct fixed-photon `g2=0` full-Fock/source-once controls and deployment boundary.

The analytic deployment smoke passed. Perceval 1.2.4 and SLOS were available, and a direct bare-CP accepted-mass probe matched the analytic success at floating-point precision. The new direct full-Fock adapter was exercised for n=2 no-gate, n=3 single-gate+bystander, and n=3 shared-gate fixtures. The documented dual-rail readout convention `(0,1) = 0` was retained. Inspection showed a concrete local source-preparation error: Perceval's beam-splitter preparation/conjugation maps the existing `(0,1)` input to physical `(1,0)`, so the direct source must start in `(1,0)` for the required decoded convention. After that correction, the no-gate zero-angle identity passes; the CP-gate controls still disagree with the independent analytic IQP reference. The shared-gate intermediate-projection path was therefore not promoted to a physical equivalence claim.

Disposition: physical/source validation is `FAIL` for the current adapter contract, despite backend availability. The fixed-photon `g2=0` boundary remains explicit; `g2>0` remains `INCONCLUSIVE`. No photonic ring deployment was run or claimed because the declared validation gate did not pass. Existing analytic ring artifacts and concurrent shared edits were preserved.

Evidence exercised:

- `venv/Scripts/python.exe scripts/v4_tcdp/validate_deploy.py` — analytic status `PASS`; model success `0.013726388348954028`; probability sum `1.0`.
- `venv/Scripts/python.exe scripts/v4_tcdp/validate_deploy.py --with-perceval` — Perceval bare-CP probe `PASS`; accepted probe error `1.39e-16`; existing single-gate full-Fock diagnostic `PASS`.
   - Direct controls in `results/v4_tcdp/deploy/physical_control_manifest.json`: n=2 no-gate raw acceptance `1.0`, TVD `6.418476861114186e-17` (`PASS`); n=3 single-gate+bystander raw acceptance `0.10266972533167883`, TVD `0.60070872508387` (`FAIL`); n=3 shared-gate raw acceptance `0.012513228886432583`, TVD `0.5541109141490421` (`FAIL`). The manifest file SHA-256 is `09e97da17b9599511dd8d48f6c60afdba50ec174634a9cbb3660c049cab9d5df`; its recorded payload identity is `df4fd964ea22a6fd6790843276e4d0169dcdf104555888c8c848c2892ebbbc78`; the aggregate physical-control status remains `FAIL`.

   Open evidence: resolve the remaining CP insertion/wiring/phase convention, then rerun the three controls and final-only/intermediate projection comparison before any frozen ring checkpoint deployment. This is a construction mismatch, not a justification to relabel outputs or change D1/D2/D3. No central ledger or shared synthesis document was edited by this workstream.
