# v4 physical validation note (superseded pre-fix record)

Date: 2026-09-07. Scope: direct fixed-photon `g2=0` full-Fock/source-once controls and deployment boundary. The first result below is preserved as a failed pre-fix record; the final disposition is recorded afterward.

Supersession note (2026-09-09): the later independent audit found that the shared-gate projection comparison squared path contributions before summing coherent amplitudes. The historical material-discrepancy value in this note is therefore superseded; see [the independent audit](2026-09-09-v4-independent-audit.md) and [the repaired manifest](../../results/v4_tcdp/deploy/physical_control_manifest_20260909_final.json). The historical values below are retained for provenance.

The analytic deployment smoke passed. Perceval 1.2.4 and SLOS were available, and a direct bare-CP accepted-mass probe matched the analytic success at floating-point precision. The direct full-Fock adapter was exercised for n=2 no-gate, n=3 single-gate+bystander, and n=3 shared-gate fixtures. The documented dual-rail readout convention `(0,1) = 0` was retained. Inspection showed a concrete local source-preparation error: Perceval's beam-splitter preparation/conjugation maps the existing `(0,1)` input to physical `(1,0)`, so the direct source must start in `(1,0)` for the required decoded convention. After that correction, the no-gate zero-angle identity passes; the CP-gate controls still disagree with the independent analytic IQP reference. The intermediate path now tracks squared norm through each projection relative to the source norm, so its absolute accepted mass is comparable to final-only. Its conditional distribution is still a distinct projection result and is reported separately.

Historical disposition: physical/source validation was `FAIL` for the pre-fix adapter contract. That result is preserved and is not the final milestone disposition.

## Final post-fix disposition

The source rail/sign contract was corrected to use the required `(1,0)` source rail and `PS(-2theta)`. The regenerated canonical manifest at [physical_control_manifest.json](../../results/v4_tcdp/deploy/physical_control_manifest.json) is `PASS` for the declared fixed-photon final-only controls: n=2 no-gate, n=3 single-gate with bystander, and n=3 shared-gate. Direct-vs-analytic conditional TVDs are at floating-point scale, and final/intermediate absolute accepted mass agrees. The shared conditional final-only/intermediate TVD is `0.585411845271861`, so final-only is the supported boundary and intermediate projection is explicitly unsupported.

The fixed-photon `g2=0` boundary remains explicit; `g2>0`, joint source/loss, non-postselected multiphoton output, and a general intermediate-projection theorem remain outside scope. The registered n=4 spatial and Hamming ring outputs are now evaluated through this validated final-only boundary; no n=6/n=8 photonic extrapolation is made.

## Historical pre-fix evidence (preserved)

The following command outputs belong to the pre-fix run and remain as audit evidence; they must not be read as the final status:

Evidence exercised:

- `venv/Scripts/python.exe scripts/v4_tcdp/validate_deploy.py` — analytic status `PASS`; model success `0.013726388348954028`; probability sum `1.0`.
   - `venv/Scripts/python.exe scripts/v4_tcdp/validate_deploy.py --with-perceval` — Perceval bare-CP probe `PASS`; accepted probe error `1.39e-16`; existing single-gate full-Fock diagnostic `PASS`.
   - `venv/Scripts/python.exe scripts/v4_tcdp/validate_physical_controls.py --pcvl-path "$env:TEMP\\merlin-v4-physical" --output results/v4_tcdp/deploy/physical_control_manifest.json` — deterministic CLI exit `1` because the physical aggregate is `FAIL`.
   - Direct controls in `results/v4_tcdp/deploy/physical_control_manifest.json`: n=2 no-gate raw acceptance `1.0`, TVD `1.196959198423997e-16` (`PASS`); n=3 single-gate+bystander raw acceptance `0.10266972533167879`, TVD `0.6007087250838697` (`FAIL`); n=3 shared-gate raw acceptance `0.013536031512283192`, TVD `0.5586365277873628` (`FAIL`). Final/intermediate accepted-mass delta is `0.0` for all three controls at `eta=0.9`; shared conditional final-vs-intermediate TVD is `0.19315524169043255`, so the comparison is valid and materially different. The manifest file SHA-256 is `de7747b0dec38f0f400c88b6a064da434b953d4ade677d3908d46b8919b39b26`; the aggregate physical-control status remains `FAIL`.

   Open evidence: resolve the remaining CP insertion/wiring/phase convention, then rerun the three controls and final-only/intermediate projection comparison before any frozen ring checkpoint deployment. The intermediate projection comparison is executable and mass-consistent, but its shared conditional distribution differs materially from final-only. This is a construction mismatch, not a justification to relabel outputs or change D1/D2/D3. No central ledger or shared synthesis document was edited by this workstream.
