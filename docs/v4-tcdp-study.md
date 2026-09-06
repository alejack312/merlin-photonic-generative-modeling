# v4.0 TCDP implementation report

Status: reviewable implementation branch, with scientific interpretation provisional.

Owner decisions are now recorded: D1 selects fixed-photon `g2=0` with explicit uniform loss; D2 selects discrete alpha-key NAT with continuous singles; D3 selects sibling-style parity initialization from exact train-target moments at scale `0.1`. These choices unlock dependent implementation, but do not close the separate evidence gates for multi-gate full-Fock validity, main-run coverage, or owner interpretation.

The branch adds three additive boundaries: a NumPy classical IQP trainer, a read-only sibling inventory/export boundary, and a logical compiler plus qualified ideal CP-map deployment boundary. Existing generator, trainability, hardness, photonic, checkpoints, and historical result paths remain unchanged.

## Delivered evidence

- The classical core has typed finite/binary/provenance contracts, exact IQP probabilities and Jacobians, spatial and Hamming Gaussian objectives, deterministic Adam/SGD updates, initialization, checkpoints and resume checks.
- The ring pipeline reproduces the 400-point `make_circles` recipe and 320/80 split, persists train-derived normalization and the explicit `2**n` row-major MSB-first codec, and uses the selected data-dependent parity initialization at scale `0.1` by default. Small-angle and uniform remain explicit ablations.
- The registered primary ring budget is complete for both kernels at n=6 and n=8: 20 main artifacts (five seed IDs per profile and n, 300 updates each) are present. The artifacts explicitly record that deterministic parity initialization yields one unique parameterization per profile/n group.
- The sibling checkout was observed read-only at `f6d6ebe87e4ee1de10893c6ea2f0ffa367493336`; its source/config/result families were hashed and dispositioned. Inventory is not source scientific certification and no unsafe serialized artifact was loaded.
- The available `training_smoke` step-4 checkpoint was safely replayed through the ideal construction as an adapted reproduction. Its product-Bernoulli input was regenerated from the recorded source recipe/seed, and an isolated source-trainer rerun matched all five recorded theta/loss rows exactly with verified source identity; checkpoint replay and retraining remain separately labelled.
- Deployment tests cover negative PS signs, alpha keys, winding, topology rejection, ideal compiled equality, CP/trace-nonincreasing checks, unnormalized composition, explicit fixed-photon `eta**n` loss scaling, erasure mass, throughput controls and full-Fock capability boundaries.
- NAT implements bounded discrete alpha-key neighbor search with continuous single-angle updates, Adam-state warm-start/resume, two matched continuation arms from one frozen warm start, and an equal-budget fixed-pair ablation; focused tests prove key movement, winding preservation, reproducibility and serialization.
- The matched comparison preserves raw/compiled/deployed vectors and reports Hamming MMD², spatial MMD², TVD, true KL, labelled floored scores, expected coverage, support diagnostics and acceptance cost.

## Deliberately open

The repository does not claim a validated multiphoton noisy source model, multi-gate full-Fock equivalence, final-only projection theorem, complete sibling reproduction across all registered rows, NAT efficacy, or an ideal photonic ring advantage. Owner null predictions, owner explanation, external review, and publication remain incomplete in the evidence ledger until their required inputs and human review exist. No merge, publish, or external communication was performed.

See the [requirement evidence ledger](../.planning/v4-requirement-evidence.md) for per-ID status and commands.
